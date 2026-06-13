# Fondamenti dell'IoT e Architettura del Protocollo MQTT

Questa lezione analizza l'evoluzione delle architetture di rete e degli stack di protocolli pensati per l'Internet of Things, culminando con un'analisi strutturale del protocollo MQTT. Vengono esplorati i paradigmi di comunicazione, le logiche di connessione, la strutturazione dei topic e i meccanismi di affidabilità offerti da questa tecnologia.

## I Requisiti dell'IoT e la Conventional Internet Protocol Suite

Perché un oggetto diventi a tutti gli effetti un dispositivo IoT deve essere connesso a Internet. Tradizionalmente, i sistemi si interfacciano alla rete globale tramite la **Internet protocol suite** convenzionale, strutturata sul binomio TCP/IP affiancato da un livello applicativo come HTTP. Questa suite si articola su tre livelli: il **livello di rete**, dominato da **IP** che si occupa di indirizzamento e routing in modalità best-effort; il **livello di trasporto**, che impiega **TCP** per canali con garanzie di consegna o **UDP** per un accesso più diretto al livello IP; il **livello applicativo**, storicamente dominato da **HTTP** con la sua architettura client/server.

Il problema è che questo stack è stato pensato per dispositivi *resource-rich*, privi di vincoli stringenti di alimentazione, memoria o connettività. Per i nodi IoT risulta troppo pesante. I dispositivi periferici operano su reti instabili (*lossy*), con hardware a bassissimo consumo energetico (*low power*) e risorse estremamente limitate (*constrained*), restando però operativi per anni. Questi vincoli impongono una ridefinizione completa dei requisiti di rete e applicativi:

|**Requisiti di Rete**|**Impatto sul Networking**|
|---|---|
|**Scalabilità / Ridondanza**|Necessità di reti multi-hop e architetture mesh.|
|**Sicurezza**|Deve essere configurabile, con livelli differenziati in base alle capacità dei singoli dispositivi.|
|**Indirizzamento**|Richiede uno spazio di indirizzamento scalabile e protocolli a basso overhead.|
|**Requisiti del Dispositivo**|**Impatto sul Livello Applicativo**|
|**Basso consumo / A batteria**|Progettazione di applicazioni con basso duty-cycle.|
|**Capacità limitata (memoria/CPU)**|Necessità di protocolli con footprint minimo e bassa complessità.|
|**Basso costo**|Aumenta la richiesta di affidabilità, introducendo però ulteriori vincoli fisici.|

---

## Introduzione al Protocollo MQTT

> [!definition] MQTT
>
> **MQTT** (*Message Queuing Telemetry Transport*) è un protocollo di messaggistica leggero di tipo publish/subscribe, progettato per ambienti con risorse limitate e connettività instabile. È standardizzato da OASIS e la versione di riferimento è MQTT 3.1.1 (novembre 2014).

MQTT è stato creato nel 1999 da Andy Stanford-Clark (IBM) e Arlen Nipper (Arcom). La sua leggerezza si manifesta in tre modi: code footprint ridotto, basso consumo di banda e overhead di pacchetto minimo, con prestazioni nettamente superiori a HTTP in scenari vincolati.

Dal punto di vista architetturale, MQTT si appoggia su TCP/IP operando tipicamente sulla **porta 1883** per le comunicazioni in chiaro e sulla **porta 8883** quando incapsulato in sessioni **SSL/TLS**. Va tuttavia sottolineato che l'adozione di SSL introduce un overhead computazionale significativo, spesso problematico per le MCU più piccole.

L'infrastruttura MQTT concentra volutamente la complessità sul lato server (il broker), mantenendo l'implementazione client estremamente semplice. Il protocollo è *data agnostic* — non si cura della natura del contenuto trasmesso — e implementa nativamente meccanismi di garanzia della consegna tramite i livelli di **Quality of Service** (QoS). È impiegato in applicazioni M2M e IoT che spaziano dai collegamenti sensore-satellite all'automazione domestica, ed è supportato nativamente da Microsoft Azure, Amazon AWS e Google Cloud IoT.

---

## Il Paradigma Publish / Subscribe

> [!tip] Pub/Sub e i tre disaccoppiamenti
>
> Il paradigma **publish/subscribe** introduce tre forme di *decoupling* che lo rendono ideale per l'IoT:
> - **Space decoupling**: publisher e subscriber non si conoscono, non condividono IP né porta.
> - **Time decoupling**: non devono essere operativi contemporaneamente.
> - **Synchronization decoupling**: le operazioni sui client non vengono bloccate durante publish o receive.

A differenza del rigido paradigma client/server, il pub/sub implementa uno schema di interazione *loosely coupled*. Gli attori sono due: i **publisher** (pubblicatori) e i **subscriber** (sottoscrittori), che agiscono entrambi come client senza essere a conoscenza dell'esistenza reciproca. I publisher producono eventi interagendo unicamente con il broker; i subscriber esprimono il proprio interesse verso specifici topic e ricevono notifiche non appena queste vengono generate.

Il **broker** è il server dell'infrastruttura, noto sia ai publisher che ai subscriber. Si occupa di ricevere tutti i messaggi in ingresso, filtrarli, distribuirli ai subscriber interessati e gestire le richieste di iscrizione e disdetta. Le operazioni cardine si riducono a quattro verbi: *Publish*, *Subscribe*, *Notify* e *Unsubscribe*.

Rispetto all'approccio client/server, la scalabilità di questa architettura è superiore. Poiché le operazioni del broker sono *event-driven*, si prestano bene alla parallelizzazione. Esistono tre modalità di filtraggio dei messaggi: **basato su topic** (il soggetto fa parte del messaggio, ed è la via di MQTT), **basato sul contenuto** (il broker ispeziona il payload, ma questo impedisce la cifratura dei dati), e **basato sul tipo** (filtraggio sulla struttura semantica dell'evento, con forte integrazione richiesta con il linguaggio di programmazione).

Due aspetti importanti del paradigma: publisher e subscriber devono accordarsi *a priori* sui nomi dei topic, e i publisher non possono assumere che qualcuno stia effettivamente ascoltando.

---

## Il Modello MQTT: Connessione e Flusso Operativo

![Diagramma di sequenza MQTT: Client A pubblica dati di temperatura, Client B li riceve tramite broker](https://upload.wikimedia.org/wikipedia/commons/8/82/MQTT_protocol_example_without_QoS.svg)
*Fonte: Wikimedia Commons — Il flusso completo: Client A si connette (CONNECT/CONNACK), Client B si sottoscrive al topic `temperature/roof` (SUBSCRIBE), Client A pubblica tre misurazioni (20°C, 25°C, 38°C) con flag retain, il broker le inoltra a Client B.*

MQTT adotta il paradigma pub/sub con filtraggio basato su topic organizzati gerarchicamente. L'infrastruttura opera ai livelli applicativi (5-6 del modello ISO/OSI), sopra TCP (livello 4) e IP (livello 3). Tutti i dispositivi devono conoscere in anticipo hostname e porta del broker. Le librerie client gestiscono quasi sempre le operazioni asincronamente tramite *callback*, pur non precludendo API sincrone.

### L'Instaurazione della Connessione

L'interazione tra client e broker inizia quando il client invia un messaggio **CONNECT**, che contiene i seguenti parametri:

- **Client ID** (obbligatorio): stringa univoca che identifica il client presso il broker. Se lasciato vuoto, il broker assegna un ID automatico, ma non conserverà alcuno stato persistente; in tal caso il flag *Clean Session* deve essere impostato a `true`.
- **Clean Session** (opzionale): se impostato a `false`, il client richiede una *persistent session* — il broker salva le sottoscrizioni e i messaggi non consegnati (con QoS ≥ 1) e li ripristina alla successiva riconnessione con lo stesso Client ID. Con `true`, la sessione è effimera e il broker rimuove ogni stato precedente.
- **Username/Password** (opzionali): per l'autenticazione. Senza TLS/SSL transitano in chiaro.
- **Will flags** (opzionali): definiscono il "testamento" del nodo — istruiscono il broker a inviare un avviso agli altri client nel caso di disconnessione anomala (*ungraceful disconnect*).
- **KeepAlive** (opzionale): intervallo in secondi (campo a 16 bit) entro cui il client si impegna a inviare almeno un pacchetto di controllo (ping). È il meccanismo primario con cui il broker rileva le disconnessioni fisiche. Il valore `0` disabilita il meccanismo.

Il broker risponde con un pacchetto **CONNACK** (*Connect Acknowledgement*) che include il flag *Connection Accepted* o *Connection Refused* (per violazione del protocollo, ID non valido o credenziali errate) e il flag *Session Present*, che indica se il broker conservava già una sessione persistente per quel client.

### Sottoscrizione e Ricezione

Per abilitare la ricezione dei dati, un client invia al broker un pacchetto **SUBSCRIBE** contenente un `packetId` (per mappare la risposta attesa) e un elenco di topic da sottoscrivere, ciascuno con il proprio livello massimo di QoS desiderato.

Il broker risponde con un pacchetto **SUBACK** che riporta lo stesso `packetId` e un `returnCode` per ogni topic: il valore `128` indica fallimento (permessi assenti o topic malformato); i valori `0`, `1` o `2` indicano successo, comunicando il *maximum QoS granted*, che può essere inferiore a quello richiesto. Per revocare una sottoscrizione si usa il pacchetto **UNSUBSCRIBE** (con `packetId` e lista di topic), a cui il broker risponde con **UNSUBACK**.

### Gestione e Best Practices dei Topic

I **topic** sono stringhe gerarchiche in cui ogni livello è separato dal carattere `/`. Un esempio tipico è `home/firstfloor/bedroom/presence`. I subscriber possono usare due tipi di **wildcard**:

- **`+`**: sostituisce un singolo livello. Ad esempio `home/firstfloor/+/presence` corrisponde a tutti i sensori di presenza al primo piano, indipendentemente dalla stanza.
- **`#`**: sostituisce tutti i livelli successivi. Ad esempio `home/firstfloor/#` cattura qualsiasi dato proveniente dal primo piano.

I topic che iniziano con `$` sono riservati al broker per statistiche interne del sistema (es. `$SYS/broker/uptime`, `$SYS/broker/clients/connected`). I client non possono pubblicare su questi topic.

> [!warning] Best practices per i topic
>
> - Non iniziare il topic con `/` (es. `/home/livingroom` è scorretto).
> - Non usare spazi nelle stringhe.
> - Mantenere le stringhe corte per ridurre l'overhead.
> - Usare solo codifiche ASCII o UTF-8.
> - Includere il `clientId` nella gerarchia (es. `sensor1/temperature`) per delimitare logicamente le autorizzazioni di pubblicazione.
> - Progettare la gerarchia pensando all'espandibilità futura.
> - Preferire topic specifici (`home/livingroom/temperature` e `home/livingroom/humidity`) rispetto ad aggregati generici (`home/livingroom/sensors`).
> - Evitare di abusare del wildcard `#` nella sottoscrizione: si rischia di sommergere il client con troppi messaggi. Ha senso solo per storage centralizzato su database.

### Pubblicazione e Struttura dei Messaggi

Una volta connesso, il publisher può inviare messaggi al broker tramite pacchetti **PUBLISH**, ciascuno composto da:

- **topicName**: stringa che identifica il topic di destinazione, usata dal broker per il routing verso i subscriber.
- **payload**: il contenuto informativo del messaggio. MQTT è *data agnostic*, quindi il payload può essere dati binari grezzi, testo, XML o JSON — la scelta è interamente applicativa.
- **packetId**: identificatore numerico a 16 bit, usato per tracciare lo scambio. Vale `0` per QoS 0 (dove non è necessario).
- **retainFlag**: se attivo, il broker conserva l'ultimo messaggio pubblicato su quel topic e lo consegna immediatamente ai nuovi subscriber che si iscrivono in seguito.
- **dupFlag**: indica che il messaggio è un duplicato di uno precedente non ancora confermato. Rilevante solo per QoS > 0.
- **qos**: livello di Quality of Service (0, 1 o 2).

Una volta inviato il messaggio al broker, il client publisher non ha responsabilità ulteriori: non sa quanti subscriber stiano ascoltando né quando riceveranno il dato.

---

## I Meccanismi della Quality of Service (QoS)

Il QoS in MQTT regola il livello di garanzia di consegna dei messaggi tra client e broker. Un aspetto architetturale importante è che il QoS sul percorso publisher→broker può essere diverso da quello sul percorso broker→subscriber: i due segmenti sono indipendenti. Il `packetId` è un intero a **16 bit**, univoco per sessione, usato per tracciare i messaggi nei livelli con conferme.

> [!abstract] I tre livelli QoS a confronto
>
> | Livello | Nome | Garanzia | Meccanismo | Duplicati |
> |---|---|---|---|---|
> | **QoS 0** | At most once | Nessuna | Nessun ACK, nessuna memorizzazione | No |
> | **QoS 1** | At least once | Almeno una consegna | PUBACK | Possibili |
> | **QoS 2** | Exactly once | Esattamente una consegna | PUBLISH → PUBREC → PUBREL → PUBCOMP | No |

### QoS 0 — At Most Once

QoS 0 è la modalità *best effort*: il messaggio viene inviato una sola volta senza alcuna conferma (**ACK**) e senza che il broker lo memorizzi. Se la connessione cade nel momento sbagliato, il messaggio è perso. È la scelta corretta per dati che invecchiano rapidamente (es. letture periodiche di sensori) e per connessioni stabili dove la perdita occasionale è accettabile.

### QoS 1 — At Least Once

QoS 1 garantisce che il messaggio arrivi almeno una volta a destinazione. Il broker memorizza il messaggio finché non riceve dal publisher il pacchetto di conferma **PUBACK**. Se il PUBACK non arriva entro un certo tempo, il publisher ritrasmette il messaggio con il flag `dupFlag` impostato. Questo può generare **duplicati**: il subscriber potrebbe ricevere lo stesso messaggio più volte. QoS 1 è adatto quando nessun dato deve andare perso e il sistema ricevente è in grado di gestire i duplicati (ad esempio tramite deduplicazione).

### QoS 2 — Exactly Once

QoS 2 è il livello più alto: garantisce che ogni messaggio venga consegnato **esattamente una volta**, senza duplicati. Il costo è un handshake a quattro fasi che aumenta la latenza e l'overhead:

1. **PUBLISH**: il publisher invia il messaggio al broker.
2. **PUBREC** (*Publish Received*): il broker conferma la ricezione e memorizza il messaggio.
3. **PUBREL** (*Publish Release*): il publisher conferma il PUBREC e autorizza il broker a procedere con la consegna.
4. **PUBCOMP** (*Publish Complete*): il broker conferma che la consegna è avvenuta e che il messaggio può essere eliminato.

Il meccanismo a quattro fasi serve a evitare sia la perdita del messaggio (gestita da PUBREC) sia la consegna duplicata (gestita da PUBREL e PUBCOMP). QoS 2 è indicato per applicazioni in cui ogni evento deve essere processato esattamente una volta — ad esempio transazioni finanziarie o comandi critici — accettando il compromesso su latenza e throughput.

---

## Verso le Sessioni Persistenti

Quando un dispositivo IoT si disconnette temporaneamente, il rischio è di perdere le sottoscrizioni attive e i messaggi nel frattempo pubblicati sui topic di interesse. Le **persistent session** risolvono questo problema: se il flag *Clean Session* è impostato a `false` nella fase di CONNECT, il broker mantiene in memoria — associato al `clientId` — tutte le sottoscrizioni attive e tutti i messaggi non ancora consegnati con QoS 1 o 2. Alla riconnessione con lo stesso `clientId`, la sessione viene ripristinata automaticamente senza dover ripetere le sottoscrizioni. Questo meccanismo è fondamentale per dispositivi con connettività intermittente e getta le basi per le logiche avanzate di gestione dello stato nel panorama IoT.

---

> [!question] Possibili domande d'esame
>
> - Quali sono i limiti dello stack TCP/IP tradizionale per l'IoT? Quali requisiti specifici impongono i dispositivi IoT a livello di rete e applicativo?
> - Descrivere il paradigma publish/subscribe e i tre tipi di disaccoppiamento che introduce rispetto al modello client/server.
> - Qual è il ruolo del broker MQTT? Quali operazioni svolge?
> - Quali sono le differenze tra i tre metodi di filtraggio dei messaggi (topic-based, content-based, type-based)?
> - Descrivere la struttura del pacchetto CONNECT e il significato di ciascun campo (Client ID, Clean Session, Will flags, KeepAlive).
> - Cosa contiene un pacchetto SUBSCRIBE e come risponde il broker con SUBACK?
> - Come funzionano le wildcard `+` e `#` nei topic MQTT? Fornire esempi.
> - Perché si evita di usare il wildcard `#` indiscriminatamente nelle sottoscrizioni?
> - Spiegare i tre livelli QoS di MQTT: garanzie offerte, meccanismi usati e casi d'uso ideali.
> - Descrivere il handshake a quattro fasi di QoS 2 (PUBLISH → PUBREC → PUBREL → PUBCOMP). Perché sono necessarie quattro fasi invece di due?
> - Il QoS tra publisher e broker può differire da quello tra broker e subscriber? Perché?
> - Cosa sono le persistent session in MQTT e quando conviene usarle?
