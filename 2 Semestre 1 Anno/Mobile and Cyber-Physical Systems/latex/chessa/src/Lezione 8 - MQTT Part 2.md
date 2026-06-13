
# MQTT: Affidabilità, Struttura dei Pacchetti e CoAP

La prima parte della lezione aveva introdotto MQTT come protocollo publish/subscribe progettato per l'IoT. Qui si approfondiscono i meccanismi che rendono il protocollo robusto: sessioni persistenti, messaggi trattenuti, testamento e keep alive. Poi si scende al livello dei singoli byte che compongono i pacchetti di controllo, si vede un'implementazione reale su Arduino, e infine si confronta MQTT con HTTP e con **CoAP** (*Constrained Application Protocol*), l'alternativa principale per reti fortemente vincolate.

---

## Meccanismi di Affidabilità

### Sessioni Persistenti

Il problema che le sessioni persistenti risolvono è semplice: un dispositivo IoT si disconnette spesso — per risparmio energetico, per copertura di rete instabile, per reset. Se il broker e il client non ricordano nulla di ciò che è avvenuto, ogni riconnessione equivale a ricominciare da zero, perdendo iscrizioni ai topic e messaggi accumulati durante l'assenza.

> [!definition] Sessione Persistente (*Persistent Session*)
>
> Meccanismo che richiede al broker — e al client — di conservare lo stato operativo attraverso disconnessioni e successive riconnessioni. Viene attivata dal client al momento della connessione impostando il flag **`cleanSession = false`** nel pacchetto CONNECT. Il broker ne conferma la creazione o la ripresa tramite il messaggio **CONNACK**.

Quando una sessione persistente è attiva, il broker memorizza le iscrizioni ai topic del client, i messaggi con QoS 1 e 2 che non è stato possibile consegnare durante l'assenza, e i messaggi in attesa di completamento del flusso di acknowledgment QoS 2. Simmetricamente, anche il **client** deve salvare stato localmente: tutti i messaggi inviati ma non ancora confermati dal broker (non-acked), e tutti i messaggi ricevuti con QoS 2 per i quali non è ancora stata inviata la conferma. Lo stato viene conservato finché le risorse di sistema lo consentono.

> [!warning] Quando NON usare le sessioni persistenti
>
> Non servono per client che pubblicano soltanto con QoS 0, perché in quel caso non c'è nulla da conservare. Vanno evitate anche quando la ricezione di messaggi vecchi è indesiderata, o quando il sistema è progettato per tollerare la perdita di dati senza conseguenze sulla logica applicativa.

### Messaggi Trattenuti (*Retained Messages*)

Nel paradigma publish/subscribe, un publisher non ha garanzia che i suoi messaggi raggiungano i subscriber — l'unica certezza che può ottenere, con QoS 1 o 2, è che il broker li abbia ricevuti. Di conseguenza, un client che si iscrive a un topic non sa quando arriverà il primo messaggio: potrebbe aspettare ore se il publisher aggiorna raramente. Questo è un problema reale per qualsiasi dato di stato che cambia di rado.

La soluzione è il **retained message**: un normale messaggio con il flag `retainFlag = true`. Quando il broker lo riceve, lo conserva. Se arriva un nuovo messaggio trattenuto sullo stesso topic, il broker sostituisce il precedente con l'ultimo — ne esiste sempre al massimo uno per topic. Il vantaggio si manifesta alla sottoscrizione: non appena un client si iscrive a un topic che possiede un messaggio trattenuto, il broker lo recapita immediatamente, senza attendere la prossima pubblicazione fisiologica. Questo funziona anche con le wildcard.

> [!example] Esempio: stato di un dispositivo domestico
>
> Un dispositivo pubblica il proprio stato su `home/devices/device1/status` con il payload `"ON"` e `retainFlag = true`. Quando un nuovo client si iscrive a quel topic — anche ore dopo — riceve immediatamente `"ON"`, senza aspettare il prossimo aggiornamento. Per cancellare il messaggio trattenuto, il publisher invia un messaggio vuoto con `retainFlag = true` sullo stesso topic.

È importante non confondere i retained messages con le sessioni persistenti: sono meccanismi ortogonali. I messaggi trattenuti vivono sul broker indipendentemente dalle sessioni dei client, e persistono anche dopo la consegna.

### Last Will & Testament

Quando un dispositivo si disconnette *normalmente* — inviando un pacchetto DISCONNECT — gli altri partecipanti possono essere notificati esplicitamente. Ma quando la disconnessione è anomala (crash hardware, interruzione di rete, timeout di keep alive), il dispositivo non ha modo di comunicare il proprio stato. Il meccanismo del **Last Will & Testament** (*testamento*) risolve esattamente questo scenario.

> [!definition] Last Will & Testament
>
> Messaggio pre-configurato che il client consegna al broker al momento della connessione (CONNECT time). Se il broker rileva una disconnessione anomala del client, pubblica automaticamente quel messaggio sul topic specificato, notificando tutti gli iscritti.

Il testamento è a tutti gli effetti un messaggio MQTT completo: ha un topic, un payload, un livello di QoS e un retained flag. Il broker lo memorizza dal momento della connessione e lo invia in quattro circostanze: errore di I/O sulla connessione di rete, mancato invio del PINGREQ entro l'intervallo di keep alive, chiusura brusca della connessione TCP senza DISCONNECT, oppure chiusura forzata da parte del broker per errore di protocollo. Se invece il client termina la sessione correttamente con DISCONNECT, il testamento viene scartato.

I quattro parametri del testamento si dichiarano nel messaggio CONNECT: **`lastWillTopic`** (stringa del topic), **`lastWillQoS`** (livello 0, 1 o 2), **`lastWillMessage`** (payload testuale) e **`lastWillRetain`** (booleano).

> [!tip] Sinergia tra Last Will e Retained Messages
>
> Il pattern più potente combina i due meccanismi. Riprendendo l'esempio precedente: il dispositivo pubblica `"ON"` come retained message su `home/devices/device1/status`. Configura anche un testamento con payload `"OFF"`, retained flag attivo, sullo stesso topic. Se va in crash, il broker pubblica automaticamente `"OFF"` come retained message — sia i client connessi che quelli futuri vedranno lo stato corretto del dispositivo.

### Keep Alive

Il **Keep Alive** affronta un problema specifico del TCP: una connessione può sembrare attiva anche quando il peer è irraggiungibile, finché non si tenta di trasmettere. In un sistema IoT con dispositivi che si connettono e scompaiono, il broker ha bisogno di un modo per accorgersi tempestivamente delle disconnessioni silenti.

Il client dichiara un intervallo di keep alive nel pacchetto CONNECT. È suo obbligo inviare un pacchetto **PINGREQ** al broker prima che quell'intervallo scada — qualunque messaggio trasmesso vale come segnale di vita, non solo il PINGREQ. Il broker risponde con **PINGRESP**. Se il client non invia nulla entro il timeout, il broker chiude la connessione e, se configurato, invia il messaggio di last will.

---

## Struttura dei Pacchetti MQTT

Comprendere la struttura dei pacchetti è utile sia per il debug a basso livello che per capire perché MQTT è così leggero. Ogni **MQTT Control Packet** si compone di tre parti: un **Fixed Header** (sempre presente), un **Variable Header** (presente solo in alcuni tipi di pacchetto) e un **Payload** (dipendente dal tipo).

### Fixed Header

Il Fixed Header occupa almeno 2 byte. Il **primo byte** codifica due informazioni: i bit 7–4 contengono il tipo di pacchetto (4 bit → 16 valori possibili, di cui 0 e 15 sono riservati); i bit 3–0 contengono flag specifici per tipo. Il **secondo byte** — eventualmente seguito da altri — rappresenta la *Remaining Length*, cioè la dimensione combinata di variable header e payload. Il campo usa una codifica a lunghezza variabile: un singolo byte copre fino a 127 byte, e il bit più significativo segnala la presenza di un byte aggiuntivo di lunghezza.

> [!note] Flag del primo byte
>
> Per la maggior parte dei pacchetti i 4 bit di flag sono riservati e devono valere `0,0,0,0`. Il pacchetto PUBLISH è l'eccezione: codifica nei flag i parametri **DUP** (primo bit), **QoS** (due bit centrali) e **Retain** (ultimo bit). I pacchetti PUBREL, SUBSCRIBE e UNSUBSCRIBE richiedono invece il valore fisso `0,0,1,0`.

I tipi di pacchetto e la direzione del flusso sono:

| Valore | Tipo | Direzione |
|--------|------|-----------|
| 1 | CONNECT | Client → Server |
| 2 | CONNACK | Server → Client |
| 3 | PUBLISH | Bidirezionale |
| 4–7 | PUBACK, PUBREC, PUBREL, PUBCOMP | Bidirezionale (gestione QoS) |
| 8 | SUBSCRIBE | Client → Server |
| 9 | SUBACK | Server → Client |
| 10 | UNSUBSCRIBE | Client → Server |
| 11 | UNSUBACK | Server → Client |
| 12 | PINGREQ | Client → Server |
| 13 | PINGRESP | Server → Client |
| 14 | DISCONNECT | Client → Server |

### Variable Header e Payload

Il **Variable Header** contiene principalmente il **packet identifier** (2 byte), un identificativo numerico univoco usato per correlare i pacchetti di acknowledgment. CONNECT e CONNACK non includono questo campo. Per PUBLISH, è presente solo se QoS > 0. L'header variabile trasporta anche informazioni aggiuntive dipendenti dal tipo: in CONNECT, ad esempio, include nome e versione del protocollo più vari flag operativi.

Il **Payload** è il corpo del messaggio. Nel CONNECT è obbligatorio e deve contenere il **client identifier**; può inoltre includere will topic, will message, username e password. In CONNACK e PUBLISH è opzionale. Nei pacchetti di puro controllo come PINGREQ, PINGRESP, DISCONNECT e tutti i pacchetti di acknowledgment QoS il payload è assente.

---

## Implementazione Pratica: MQTT su Arduino

La libreria più diffusa per MQTT su Arduino è **PubSubClient**. È progettata deliberatamente per essere leggera: implementa solo le funzionalità core di MQTT, senza SSL/TLS, senza supporto a QoS 2, e con un limite rigido di 128 byte per il payload. Questi vincoli la rendono adatta ai microcontrollori a basse risorse tipici dell'ecosistema Arduino.

### Costruzione del client

La libreria si istanzia con il costruttore completo `PubSubClient(server, port, callback, client, stream)`, dove `server` è l'`IPAddress` del broker, `port` è un intero, `callback` è un puntatore a funzione che viene invocata all'arrivo di un messaggio, `client` è un'istanza di rete (tipicamente `EthernetClient`), e `stream` è opzionale per lo storage dei messaggi ricevuti. È anche possibile usare il costruttore vuoto e configurare i parametri successivamente via setter (`setServer`, `setCallback`, `setClient`, `setStream`).

> [!note] Callback
>
> Il meccanismo di callback funziona come nelle interfacce grafiche con gli event listener: la funzione viene eseguita solo quando arriva un messaggio su un topic sottoscritto. Non c'è polling attivo.

### API principale

`connect(clientID, username, password, willTopic, willQoS, willRetain, willMessage)` avvia la connessione specificando credenziali e parametri del testamento; restituisce `true` in caso di successo. `disconnect()` chiude la sessione in modo pulito.

`publish(topic, payload, length, retained)` pubblica un messaggio; restituisce `false` se la connessione è caduta o il payload supera il limite. `subscribe(topic, qos)` e `unsubscribe(topic)` gestiscono le iscrizioni, entrambe con valore di ritorno booleano.

Fondamentale è la chiamata ripetuta a **`loop()`** nel ciclo principale: è questa funzione che genera i PINGREQ e mantiene viva la connessione. Senza di essa il broker considererà il client disconnesso entro l'intervallo di keep alive. I metodi `connected()` e `state()` supportano il debugging.

---

## MQTT vs HTTP e il Problema della Scalabilità

MQTT e HTTP sono i principali competitor nell'IoT, ma operano su paradigmi radicalmente diversi. HTTP impone un'architettura **client/server** rigida e simmetrica: ogni entità deve essere o client o server. Organizzare una rete IoT con HTTP significa che ogni sensore deve agire da server (o da client che interroga un server centrale), e che ogni comunicazione è strettamente 1-a-1. Con centinaia o migliaia di dispositivi, il numero di connessioni simultanee al server centrale cresce proporzionalmente — e con esso il carico di risorse. **HTTP non scala bene**.

MQTT invece, grazie al publish/subscribe, fa crescere il numero di connessioni solo sul broker, non sui client. Un nuovo subscriber si aggiunge alla rete senza che nessun publisher debba sapere della sua esistenza. Il broker gestisce il *fan-out* internamente.

Dal punto di vista tecnico, MQTT invia dati come array di byte con header compatti (pochi byte), mentre HTTP trasmette documenti con header testuali voluminosi. MQTT supporta tre livelli di QoS e topologie 1-a-0, 1-a-1 e 1-a-N; HTTP ha un solo livello di servizio e comunicazione esclusivamente 1-a-1.

> [!warning] Limiti strutturali di MQTT
>
> Nonostante i vantaggi, MQTT presenta tre criticità architetturali importanti. Prima: il broker è un **single point of failure** — se cade, l'intera rete smette di comunicare. Seconda: al crescere della rete, l'overhead computazionale del broker può diventare incompatibile con le risorse dei dispositivi finali più vincolati. Terza: MQTT si appoggia a **TCP**, che richiede risorse considerevolmente superiori a UDP, causa tempi di risveglio (*wake-up time*) elevati per la procedura di handshake, e accorcia la vita della batteria dei dispositivi che devono mantenere connessioni persistenti.

---

## CoAP: L'Alternativa per Reti Vincolate

È proprio il problema del TCP che apre la strada al **CoAP** (*Constrained Application Protocol*), standardizzato in RFC 7252. CoAP è progettato specificamente per operare su nodi computazionalmente deboli e reti con alta perdita di pacchetti, bandwidth nell'ordine dei 10 kbit/s e dispositivi con poche decine di byte di RAM e ROM. Trova applicazione naturale in sistemi M2M (*Machine-to-Machine*), building automation e smart energy.

A differenza di MQTT, CoAP abbraccia un classico paradigma **client/server** con un twist: sono i sensori e gli attuatori periferici ad agire da *server*, mentre i software applicativi centrali fanno da *client* che li interrogano. L'interfaccia è un modello **REST** completo: i sensori espongono risorse tramite URI, e i client le manipolano con i verbi **GET, PUT, POST, DELETE** — esattamente come nell'HTTP convenzionale, ma con profonde ottimizzazioni sotto.

> [!abstract] Caratteristiche tecniche di CoAP
>
> CoAP utilizza **UDP/IP** come trasporto invece di TCP, eliminando l'overhead di connessione. Adotta formati di codifica compatti con header di dimensioni ridottissime. Include nativamente una *resource directory* per la scoperta (*discovery*) delle risorse nella rete. Sul fronte sicurezza, integra meccanismi crittografici robusti — la protezione è paragonabile a chiavi RSA da 3072 bit. Prospera nelle **6LoWPAN** (reti IPv6 over Low-Power Wireless PAN), ambienti con packet error rate elevato e throughput limitato.

CoAP supporta anche un modello di comunicazione asincrona che ne avvicina il comportamento a MQTT, e ha un supporto nativo (seppur minoritario) per trasmissioni multicast. Il supporto formale di Eclipse ne accelera la diffusione.

> [!tip] Quando scegliere CoAP vs MQTT
>
> Scegli **MQTT** quando l'obiettivo è massimizzare il disaccoppiamento tra produttori e consumatori di dati — nel tempo e nello spazio — e quando il broker centralizzato non è un vincolo architetturale. Scegli **CoAP** quando lo scenario richiede sicurezza crittografica forte *by default*, quando si lavora su reti UDP con dispositivi ultra-vincolati, o quando si vuole evitare la dipendenza da un broker centrale.

Entrambi i protocolli hanno oggi lo status di standard riconosciuti per l'IoT. CoAP è più giovane e i suoi meccanismi di affidabilità della consegna sono meno sofisticati della gerarchia QoS di MQTT, ma la sua leggerezza e la base UDP lo rendono insostituibile negli scenari più vincolati.

---

> [!question] Possibili domande d'esame
>
> - Cosa memorizza il broker e cosa memorizza il client in una sessione persistente con QoS 2?
> - Qual è la differenza tra sessione persistente e retained message? Sono meccanismi indipendenti?
> - In quali quattro circostanze il broker invia il messaggio di last will?
> - Come è strutturato il Fixed Header di un pacchetto MQTT? Cosa codifica il primo byte?
> - Perché PubSubClient non supporta QoS 2 e SSL/TLS? Qual è il vincolo architetturale?
> - Perché HTTP scala male per reti IoT con molti dispositivi rispetto a MQTT?
> - Quali sono i tre limiti strutturali di MQTT (broker, risorse, TCP)?
> - Cosa cambia nell'architettura client/server di CoAP rispetto al web tradizionale?
> - Perché CoAP usa UDP invece di TCP? Quali vantaggi porta e quali svantaggi introduce?
> - In quale scenario sceglieresti CoAP su MQTT e viceversa?
