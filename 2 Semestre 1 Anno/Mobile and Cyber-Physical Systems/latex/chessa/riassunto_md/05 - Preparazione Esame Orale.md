# 05 - Preparazione Esame Orale

Documento di preparazione all'esame orale del corso **Mobile and Cyber-Physical Systems**, modulo del Prof. Stefano Chessa. Per ogni schema del documento originale viene fornita una risposta dettagliata, corredata dell'immagine di riferimento e dei link alle lezioni pertinenti.

---

## Interoperabilità

![[exam_chessa_interoperability.jpg]]
*Fig. — Rete IoT eterogenea: dispositivi di produttori diversi (colori diversi) comunicano attraverso gateway di integrazione.*

Lo schema mostra una rete in cui dispositivi appartenenti a ecosistemi diversi (rappresentati con colori diversi) devono comunicare tra loro. Il problema fondamentale è l'**interoperabilità**.

Il percorso storico delle soluzioni IoT "dal basso" porta spesso alla creazione di **vertical silos**: sistemi proprietari in cui i dispositivi di un fornitore comunicano solo con l'infrastruttura dello stesso produttore. Questa strategia risponde a un preciso modello di business chiamato **vendor lock-in**, che costringe il cliente a restare nell'ecosistema del fornitore pena una costosa migrazione.

La soluzione naturale è l'adozione di **standard condivisi** (Wi-Fi, ZigBee, Bluetooth, ecc.), ma la proliferazione degli standard sposta il problema al livello middleware e applicativo: oggi coesistono MQTT, CoAP, LWM2M e molti altri protocolli applicativi, incompatibili tra loro.

Per gestire questa eterogeneità si ricorre agli **application-level gateway**, che non si limitano a tradurre protocolli di basso livello ma mappano comportamenti applicativi differenti, operando come interpreti semantici tra ecosistemi.

Le architetture IoT si classificano in quattro tipi:

| Tipo | Fornitore | Protocollo | Gateway? |
|------|-----------|------------|----------|
| A | Unico | Unico | No |
| B | Multiplo | Unico condiviso | No / minimale |
| C | Multiplo | Diversi | Sì — traduzione |
| D | Multiplo | Eterogenei distribuiti | Sì — gateway multipli |

All'aumentare della complessità da A a D, il gateway deve gestire un numero esponenziale di mappature tra protocolli.

> [!note] Riferimento
> [[Lezione 3 - Interoperabilità e Standard]]

---

## IoT & Security

![[exam_chessa_iot_security.jpg]]
*Fig. — Architettura di sicurezza IoT: dispositivi vincolati (C), gateway (G), applicazioni (A) e relative misure di sicurezza per ogni livello.*

Lo schema mostra un'architettura IoT a strati in cui la sicurezza deve essere garantita a ogni livello: tra dispositivi periferici e gateway (autenticazione + trasferimento sicuro), e tra gateway e cloud/applicazione (sicurezza dei dati a riposo + autenticazione).

I dispositivi IoT sono spesso sistemi embedded economici, prodotti con forti incentivi a ridurre costi e tempi di immissione sul mercato, a discapito della sicurezza. La conseguenza sono centinaia di milioni di dispositivi vulnerabili, privi di meccanismi di patching efficaci.

La raccomandazione **ITU-T Y.2066** definisce tre aree fondamentali di sicurezza:

1. **Sicurezza della comunicazione** — riservatezza e integrità dei dati in transito tra dispositivi e piattaforme.
2. **Sicurezza della gestione dei dati** — protezione di riservatezza e integrità quando i dati sono archiviati o elaborati (*data at rest*).
3. **Sicurezza della fornitura del servizio** — prevenzione di accessi non autorizzati e protezione della privacy degli utenti.

A questi si aggiungono l'**autenticazione mutua** (entrambe le parti si verificano reciprocamente, più robusta dell'autenticazione a una via) e la capacità di audit di sicurezza.

Il **gateway** gioca un ruolo centrale:
- Gestisce identificazione e autenticazione di ogni dispositivo connesso.
- Protegge la privacy dei dispositivi periferici.
- Supporta manutenzione, aggiornamento firmware e autodiagnosi remota.
- Applica policy di configurazione dinamiche.

> [!warning] Dispositivi vincolati e limiti
>
> I *constrained devices* spesso non dispongono di hardware crittografico dedicato, rendendo impraticabile la cifratura dei dati archiviati. Con il *Massive IoT*, la privacy diventa critica per la grande mole di dati sensibili (medici, posizione, abitudini) raccolti.

> [!note] Riferimento
> [[Lezione 3 - Interoperabilità e Standard]] (sezione sicurezza)

---

## Publish/Subscribe & MQTT

![[exam_chessa_mqtt_pubsub.jpg]]
*Fig. — Il paradigma publish/subscribe: i publisher inviano messaggi al broker tramite PUBLISH; i subscriber si registrano (SUBSCRIBE) e ricevono notifiche (PUBLISH dal broker); possono anche disdire (UNSUBSCRIBE).*

Il paradigma **publish/subscribe** è il cuore di MQTT. A differenza del modello client/server, il pub/sub è *loosely coupled* grazie a tre forme di disaccoppiamento:

- **Space decoupling**: publisher e subscriber non si conoscono, non condividono IP né porta.
- **Time decoupling**: non devono essere attivi contemporaneamente.
- **Synchronization decoupling**: le operazioni non sono bloccanti.

Il **broker** è il server dell'infrastruttura: riceve tutti i messaggi, li filtra per topic, li distribuisce ai subscriber interessati. Le operazioni fondamentali sono quattro: *Publish*, *Subscribe*, *Notify*, *Unsubscribe*.

**MQTT** (*Message Queuing Telemetry Transport*) implementa pub/sub con filtraggio basato su **topic** — stringhe gerarchiche separate da `/` (es. `home/firstfloor/bedroom/temperature`). I subscriber possono usare wildcard:
- `+` sostituisce un singolo livello: `home/+/temperature`
- `#` sostituisce tutti i livelli successivi: `home/#`

MQTT opera su TCP (porta 1883, o 8883 con TLS) e concentra la complessità sul broker, mantenendo i client semplici. È *data agnostic*: il payload può essere binario, testo, JSON o XML.

> [!note] Riferimento
> [[Lezione 4 - MQTT Part 1]]

---

## MQTT – II (QoS 2)

![[exam_chessa_mqtt_qos2.jpg]]
*Fig. — Handshake a quattro fasi del QoS 2 tra MQTT client e broker: PUBLISH → PUBREC → PUBREL → PUBCOMP.*

MQTT definisce tre livelli di **Quality of Service**:

| Livello | Nome | Garanzia | Meccanismo |
|---------|------|----------|------------|
| QoS 0 | At most once | Nessuna | Nessun ACK |
| QoS 1 | At least once | Almeno una consegna | PUBACK (possibili duplicati) |
| QoS 2 | Exactly once | Esattamente una consegna | 4-way handshake |

**QoS 2** è il livello più affidabile. Il handshake a quattro fasi serve a evitare sia la perdita che la duplicazione:

1. **PUBLISH**: il client invia il messaggio al broker (con packetId).
2. **PUBREC** (*Publish Received*): il broker conferma la ricezione e memorizza il messaggio.
3. **PUBREL** (*Publish Release*): il client autorizza il broker a procedere con la consegna effettiva.
4. **PUBCOMP** (*Publish Complete*): il broker conferma che la consegna ai subscriber è avvenuta e il messaggio può essere eliminato.

Il PUBREC garantisce che il messaggio non vada perso; PUBREL + PUBCOMP garantiscono che non venga consegnato due volte. Due fasi non sarebbero sufficienti perché, se il broker consegnasse immediatamente al PUBLISH senza aspettare PUBREL, e il client ritrasmettesse credendo di non aver ricevuto PUBREC, si avrebbero duplicati.

> [!note] Riferimento
> [[Lezione 4 - MQTT Part 1]]

---

## MQTT-III — Topic, Sessioni, Retained Messages, Last Will & Keep Alive

### Come il broker filtra i messaggi e cosa sono i topic

Il broker usa il **filtraggio basato su topic** (topic-based filtering): ogni messaggio PUBLISH porta un topic; il broker lo confronta con le sottoscrizioni attive e lo consegna ai subscriber che corrispondono. I topic sono stringhe gerarchiche; le wildcard `+` e `#` permettono iscrizioni a insiemi di topic. Il broker non ispeziona il payload (a differenza del content-based filtering), il che consente la cifratura end-to-end.

### Sessioni Persistenti

Quando un dispositivo IoT si disconnette (per sleep, copertura persa, reset), rischia di perdere le sottoscrizioni attive e i messaggi pubblicati durante l'assenza. Le **persistent session** risolvono questo: impostando `cleanSession = false` nel CONNECT, il broker conserva per quel `clientId`:
- Tutte le sottoscrizioni attive
- I messaggi non consegnati con QoS 1 o 2
- I messaggi in attesa di completamento del flusso QoS 2

Alla riconnessione con lo stesso `clientId`, la sessione viene ripristinata automaticamente. Il broker segnala la presenza di una sessione precedente tramite il flag *Session Present* nel CONNACK.

### Retained Messages

Nel pub/sub classico, un nuovo subscriber non sa quando arriverà il primo messaggio. I **retained message** risolvono questo: un messaggio pubblicato con `retainFlag = true` viene conservato dal broker (uno per topic). Ogni nuovo subscriber riceve immediatamente l'ultimo messaggio trattenuto al momento dell'iscrizione, senza aspettare la prossima pubblicazione.

> [!tip] Pattern potente
>
> Un dispositivo pubblica il proprio stato (`"ON"`) come retained message. Configura anche un testamento con payload `"OFF"` e retain flag attivo sullo stesso topic. Se va in crash, il broker pubblica automaticamente `"OFF"` come retained message — tutti i client (connessi e futuri) vedono lo stato corretto.

### Last Will & Testament

Quando un dispositivo si disconnette *normalmente* (DISCONNECT), può notificare gli altri esplicitamente. Per le **disconnessioni anomale** (crash, timeout, interruzione di rete) non esiste tale possibilità. Il **Last Will & Testament** consiste in un messaggio pre-configurato consegnato al broker al momento del CONNECT: se il broker rileva una disconnessione anomala, pubblica quel messaggio automaticamente. Il testamento ha topic, payload, QoS e retained flag propri.

Il broker invia il testamento quando: errore di I/O sulla connessione, mancato invio di PINGREQ entro il keep alive, chiusura brusca TCP senza DISCONNECT, o chiusura forzata per errore di protocollo. Se il client si disconnette con DISCONNECT regolare, il testamento viene scartato.

### Keep Alive

TCP può mantenere una connessione apparentemente attiva anche quando il peer è irraggiungibile. Il **Keep Alive** risolve: il client dichiara un intervallo (campo a 16 bit nel CONNECT) entro cui si impegna a inviare almeno un pacchetto. Se non lo fa, il broker chiude la connessione e invia il testamento. Il client invia **PINGREQ** se non ha altro traffico; il broker risponde con **PINGRESP**. Il valore `0` disabilita il meccanismo.

> [!note] Riferimento
> [[Lezione 4 - MQTT Part 1]], [[Lezione 8 - MQTT Part 2]]

---

## ZigBee - I (Join through Association)

![[exam_chessa_zigbee_join.jpg]]
*Fig. — Sequenza di primitives tra Application Layer, Network Layer e MAC Layer durante il processo di join di un dispositivo ZigBee.*

Lo schema mostra il processo con cui un dispositivo si unisce a una rete ZigBee esistente attraverso il meccanismo di **associazione**. Si tratta di un'interazione a tre livelli (Application, Network, MAC) tramite service primitives.

La sequenza è:

1. **Application layer** emette `NETWORK-DISCOVERY.request` al Network Layer.
2. **Network Layer** emette `SCAN.request` al MAC: viene eseguito un active scan per trovare le PAN disponibili.
3. **MAC** esegue lo scan e risponde con `SCAN.confirm`.
4. **Network Layer** risponde all'applicazione con `NETWORK-DISCOVERY.confirm`, che elenca le PAN trovate.
5. **Application layer** sceglie una PAN e invia `JOIN.request` al Network Layer.
6. **Network Layer** seleziona un nodo genitore P e avvia il protocollo di associazione MAC tramite `ASSOCIATE.request`.
7. **MAC** esegue il protocollo di associazione: il coordinatore/router assegna un **indirizzo breve a 16 bit** al nuovo dispositivo.
8. **MAC** risponde con `ASSOCIATE.confirm` → **Network Layer** risponde con `JOIN.confirm` all'applicazione.

Nelle reti a stella, P è necessariamente il coordinatore. Nelle reti ad albero o mesh, P può essere qualsiasi router raggiungibile.

> [!note] Riferimento
> [[Lezione 9 - The ZigBee Standard Part 1]]

---

## ZigBee – II (Application Layer Stack)

![[exam_chessa_zigbee_applayer.jpg]]
*Fig. — Stack protocollare ZigBee: dall'IEEE 802.15.4 (MAC) fino all'Application Layer, con Application Framework, ZDO e APS.*

ZigBee aggiunge sopra IEEE 802.15.4 (PHY + MAC) due livelli: **Network Layer** e **Application Layer**. Il livello applicativo si compone di tre elementi:

**Application Framework**: ospita fino a 240 **Application Objects (APO)**, ciascuno associato a un endpoint (numerato da 1 a 240). Ogni APO è identificato univocamente dalla coppia `<indirizzo di rete, endpoint>`. Più APO sullo stesso dispositivo possono corrispondere ad applicazioni diverse che operano simultaneamente.

**ZigBee Device Object (ZDO)**: occupa l'endpoint 0 ed è la componente gestionale del nodo. Fornisce:
- Device & Service Discovery (trova altri nodi e i loro servizi)
- Binding Management (crea/modifica le binding table dell'APS)
- Network Management (gestisce join/leave e routing table)

**Application Support Sublayer (APS)**: fa da intermediario tra APO/ZDO e il Network Layer. Fornisce:
- *Data Service*: trasmissione messaggi con acknowledgment end-to-end
- *Binding Service*: creazione di connessioni logiche tra endpoint
- *Group Management*: indirizzamento multicast tramite Group Table

L'APS filtra i pacchetti per endpoint e profile ID, scartando quelli non destinati ad applicazioni registrate.

> [!note] Riferimento
> [[Lezione 9 - The ZigBee Standard Part 1]], [[Lezione 12 - Application Layer of ZigBee]]

---

## ZigBee - III (Topologie di Rete)

![[exam_chessa_zigbee_topologies.jpg]]
*Fig. — Le tre topologie ZigBee: Star (sinistra), Tree (centro), Mesh (destra). Nodo giallo = coordinatore, nodi blu = router, nodi rossi = end-device.*

ZigBee supporta tre topologie di rete gestite dal Network Layer:

**Star (Stella)**: tutti i dispositivi comunicano direttamente con il coordinatore. Si mappa direttamente sulla struttura IEEE 802.15.4 e supporta il meccanismo del superframe/beacon. Semplice ma non scalabile: ogni dispositivo deve essere nel raggio radio del coordinatore.

**Tree (Albero)**: il coordinatore è la radice, i router sono nodi interni, gli end-device sono foglie. Può usare il superframe. Il routing segue la struttura gerarchica (tree routing): i pacchetti salgono verso la radice e poi scendono verso la destinazione. Il vantaggio è la semplicità; lo svantaggio è la rigidità e i percorsi spesso subottimali.

**Mesh**: topologia più flessibile in cui i router possono comunicare direttamente tra loro indipendentemente dalla struttura ad albero. Usa mesh routing (ispirato ad AODV): se non esiste un'entry nella routing table, viene avviato il Route Discovery Protocol (broadcast RREQ, unicast RREP). Non supporta il beaconing. È più robusto: percorsi alternativi sono disponibili se un link cade.

> [!tip] Coesistenza
>
> Tree routing e Mesh routing possono coesistere nella stessa rete: ogni router mantiene sia la logica ad albero che la routing table mesh, passando dinamicamente dall'uno all'altro.

> [!note] Riferimento
> [[Lezione 9 - The ZigBee Standard Part 1]]

---

## ZigBee - IV (Indirizzamento ad Albero)

![[exam_chessa_zigbee_addrtree.jpg]]
*Fig. — Albero di indirizzi ZigBee con $R_m=2$, $D_m=2$, $L_m=3$: ogni nodo gestisce un intervallo di indirizzi calcolato con la formula $C_{skip}$.*

ZigBee assegna gli indirizzi di rete in modo completamente decentralizzato usando la struttura ad albero. Il coordinatore viene configurato con tre parametri:
- $R_m$: massimo numero di router figli per nodo
- $D_m$: massimo numero di end-device figli per nodo
- $L_m$: profondità massima dell'albero

La dimensione del blocco di indirizzi assegnato a un router a profondità $d$ è:

$$C_{skip}(d) = \begin{cases} 1 & \text{se } d = L_m \\ 1 + R_m \cdot C_{skip}(d+1) + D_m & \text{altrimenti} \end{cases}$$

Se un router ha indirizzo $A$ e si trova a profondità $d$, i suoi figli router ricevono: $A+1$, $A+1+C_{skip}(d+1)$, $A+1+2 \cdot C_{skip}(d+1)$, … Gli end-device ricevono gli indirizzi successivi a tutti i blocchi router.

> [!example] Nell'immagine: $R_m=2$, $D_m=2$, $L_m=3$
>
> - $C_{skip}(3)=1$, $C_{skip}(2)=5$, $C_{skip}(1)=13$, $C_{skip}(0)=29$
> - Coordinator (addr=0) gestisce [0–28]; primo figlio router addr=1 gestisce [1–13]; secondo figlio router addr=14 gestisce [14–26]; end-device 27 e 28.

**Vantaggio**: completamente decentralizzato, nessun rischio di collisione, nessun coordinamento distribuito necessario.

**Svantaggio**: rigido — se un sottoalbero è saturo, nuovi dispositivi non possono aggiungersi tramite quel nodo anche se ce ne fosse necessità.

> [!note] Riferimento
> [[Lezione 9 - The ZigBee Standard Part 1]]

---

## ZigBee - V (Tabella APS / Binding Table)

![[exam_chessa_zigbee_aps.jpg]]
*Fig. — Esempio di APS Binding Table: ogni entry mappa un endpoint sorgente con cluster e destination address/endpoint.*

La tabella mostra la **APS Binding Table**, il meccanismo con cui ZigBee implementa l'**indirizzamento indiretto**. Un dispositivo sorgente (che conosce solo il proprio endpoint e il cluster di interesse) non ha bisogno di conoscere l'indirizzo di rete del destinatario: consulta la binding table.

Le colonne della tabella sono:
- **Src Addr (64 bit)**: indirizzo MAC a 64 bit del dispositivo sorgente.
- **Src EP**: endpoint sorgente (1–240).
- **Cluster ID**: il cluster di riferimento (es. `0x0006` = OnOff Cluster).
- **Dest Addr (16/64 bit)**: indirizzo di destinazione (short 16 bit o MAC 64 bit).
- **Addr/Grp**: `A` = indirizzo unicast, `G` = indirizzo di gruppo (multicast).
- **Dest EP**: endpoint destinazione (vuoto per i gruppi).

Nell'esempio, il dispositivo `0x3232...` endpoint 5 può inviare messaggi:
- All'indirizzo `0x1234...` endpoint 12 (unicast)
- All'indirizzo `0x796F...` endpoint 240 (unicast)
- Al gruppo `0x9999` (multicast, nessun endpoint specifico)
- All'indirizzo `0x5678...` endpoint 44 (unicast)

Questo meccanismo è fondamentale: se un dispositivo cambia indirizzo di rete (dopo un reset), l'APS usa la **Address Map Table** (che associa indirizzi 16-bit agli immutabili MAC 64-bit) per ripristinare i binding automaticamente.

> [!note] Riferimento
> [[Lezione 12 - Application Layer of ZigBee]]

---

## ZigBee - VI (Cluster e Binding tra Dispositivi)

![[exam_chessa_zigbee_binding.jpg]]
*Fig. — Esempio di binding ZigBee: Configuration tool configura un on/off switch, che controlla una Simple lamp e un Dimmer switch, il quale controlla una Dimmable lamp.*

Lo schema illustra come il **binding** ZigBee colleghi dispositivi tramite cluster. Ogni rettangolo contiene le lettere C (Client) o S (Server) per ciascun cluster supportato.

Un **Cluster** è una collezione di comandi e attributi che definisce l'interfaccia per una funzionalità specifica. Ogni cluster ha un ID a 16 bit (es. `0x0006` = OnOff, `0x0008` = Level Control). Il cluster lato **server** ospita lo stato (attributi); il lato **client** invia comandi.

Nell'esempio:
- La **Configuration tool** (solo C) si lega all'**On/off switch** (S+C) per configurarlo.
- L'**On/off switch** (come client) controla la **Simple lamp** (S = solo server OnOff).
- Il **Dimmer switch** (S+C) riceve configurazioni (S) e controla la **Dimmable lamp** che implementa sia OnOff (S) che Level Control (S).

Il binding è unidirezionale: si va da client a server. Viene creato tramite `BIND.request` allo ZDO e memorizzato nella binding table dell'APS. Un singolo client può essere legato a più server (fan-out).

> [!note] Riferimento
> [[Lezione 12 - Application Layer of ZigBee]]

---

## Duty Cycle - I (Calcolo del Duty Cycle)

![[exam_chessa_dutycycle_code.jpg]]
*Fig. — Codice Arduino che implementa il duty cycling selettivo dei componenti (sensore, radio) e tabella dei consumi in mA per componente e stato.*

Il **duty cycle** di un componente è la frazione di tempo in cui è attivo rispetto al periodo totale. La strategia fondamentale di risparmio energetico nei dispositivi IoT è attivare ogni componente **solo quando strettamente necessario**.

Il codice mostra il pattern classico:
```
turnOn(analogSensor)   → sensore acceso solo durante lettura
analogRead(A0)         → lettura
turnOff(analogSensor)  → sensore spento

turnOn(radioInterface) → radio accesa solo durante trasmissione
Serial.println(voltage)
turnOff(radioInterface)

idle(380)              → MCU in sleep 380ms
```

Usando i valori della tabella (es. Tmote Sky):
- Processore attivo: 8 mA, sleep: 15 μA
- Radio TX: 17.4 mA, RX: 19.7 mA, sleep: 20 μA
- Sensore: 5 mA, sleep: 5 μA

Se le operazioni di sensing + TX durano ~20 ms e il ciclo totale è 400 ms, il duty cycle della radio è 20/400 = 5%. La corrente media risultante è molto inferiore alla corrente di picco, estendendo la vita della batteria di ordini di grandezza.

La perdita di capacità della batteria del 3%/anno indica che anche con battery standby c'è un degrado nel tempo.

> [!note] Riferimento
> [[Lezione 23 - Embedded Programming e Arduino]]

---

## Duty Cycle - II (Impatto sulla Vita della Batteria)

![[exam_chessa_dutycycle_graph.jpg]]
*Fig. — Grafico log-log: vita della batteria (mesi) vs capacità della batteria (mAh) per duty cycle 100% (model1) e 5% (model2).*

Il grafico mostra l'impatto del duty cycle sulla vita della batteria in scala logaritmica. Due modelli a confronto:

- **Model 1 (100% DC)**: il dispositivo è sempre attivo. La vita della batteria scala linearmente con la capacità ma rimane nell'ordine dei mesi (0.01–0.3 mesi per capacità 500–3000 mAh).
- **Model 2 (5% DC)**: il dispositivo è attivo solo il 5% del tempo. La vita si estende di un fattore ~20: con la stessa batteria, si passa da 0.1 a circa 2–8 mesi.

La scala logaritmica rivela che la relazione vita-capacità non è lineare: il duty cycle agisce moltiplicativamente. Ridurre il duty cycle da 100% a 5% equivale a moltiplicare la capacità effettiva della batteria per 20.

**Conclusione progettuale**: per applicazioni IoT con autonomia di anni, ridurre il duty cycle è molto più efficace che aumentare la capacità della batteria. Una batteria da 3000 mAh a 5% DC dura circa 8 mesi; per durare anni si deve abbassare ulteriormente il duty cycle o usare energy harvesting.

> [!note] Riferimento
> [[Lezione 23 - Embedded Programming e Arduino]]

---

## Embedded Programming - I (Modello Arduino)

![[exam_chessa_embedded_arduino.jpg]]
*Fig. — Modello di esecuzione Arduino: init → loop() ripetuto. I comandi attivano l'hardware; delay() aspetta; il timer fires avvia la ripetizione.*

Lo schema mostra il **modello di programmazione Arduino**, basato su un singolo thread di esecuzione:

1. **init**: la funzione `setup()` viene eseguita una sola volta all'avvio. Inizializza l'hardware, configura i pin, prepara le comunicazioni seriali.
2. **Main loop**: la funzione `loop()` viene invocata ripetutamente all'infinito dal runtime Arduino.
3. **Command**: dentro `loop()`, il codice interagisce con l'hardware tramite comandi sincroni (es. `analogRead()`, `Serial.println()`).
4. **Delay**: `delay(ms)` blocca l'esecuzione per il tempo specificato (busy waiting o sleep), poi il timer fires riavvia il loop.

Il modello è semplice ma **bloccante**: durante `delay()` il processore non può fare altro. Gli interrupt possono intervenire anche durante il delay (come mostrato nel codice Arduino interrupt), ma il thread principale rimane sospeso.

**Differenza con TinyOS**: nel modello Arduino tutto avviene sequenzialmente in un unico thread. In TinyOS (modello event-driven) il sistema reagisce ad eventi: non c'è un loop esplicito, ma handler che si concatenano tramite eventi hardware.

> [!note] Riferimento
> [[Lezione 23 - Embedded Programming e Arduino]]

---

## Embedded Programming - II (Modello TinyOS/Event-Driven)

![[exam_chessa_embedded_tinyos.jpg]]
*Fig. — Modello di esecuzione TinyOS: catena di eventi (Timer → Read → task → Send) senza loop bloccante. Il data processing avviene nel task asincrono.*

TinyOS usa un modello **event-driven** con componenti e interfacce. Non esiste un loop bloccante: il sistema è guidato dagli eventi hardware. Lo schema mostra una catena tipica:

1. **init**: configura timer e hardware.
2. **Timer handler** (evento): scatta quando il timer fires → avvia una lettura dal sensore (`Start read`).
3. **Read handler** (evento): scatta quando la lettura è completata (`Read done`) → posta un task per il processing.
4. **task**: elabora i dati (*Data processing happens here*) → avvia la trasmissione radio.
5. **Send handler** (evento): scatta quando la trasmissione è completa → riconfigura il timer per il prossimo ciclo.

**Vantaggi del modello event-driven**:
- Nessun busy waiting: il processore dorme tra un evento e l'altro.
- Nessuno stack multiplo: un unico stack (run-to-completion semantics).
- Efficienza energetica: il MCU è attivo solo durante gli handler.

**Confronto con Arduino**: Arduino è più semplice da programmare (loop sequenziale), ma meno efficiente in termini energetici. TinyOS è ottimale per nodi a basso consumo (mica motes, TMote Sky) dove ogni microsecondo di sleep conta.

> [!note] Riferimento
> [[Lezione 23 - Embedded Programming e Arduino]]

---

## Arduino - Interrupt

![[exam_chessa_arduino_interrupt.jpg]]
*Fig. — Esempio di programmazione con interrupt su Arduino: attachInterrupt() collega il pin 2 a interruptSwitchGreen(); count viene resettato e il LED acceso all'interrupt.*

Il codice mostra il meccanismo degli **interrupt hardware** su Arduino:

```cpp
volatile int count = 0;
attachInterrupt(0, interruptSwitchGreen, RISING);
```

`attachInterrupt(0, handler, RISING)` collega il pin 2 (interrupt 0 su Arduino Uno) alla funzione `interruptSwitchGreen`, eseguita automaticamente sul fronte di salita del segnale.

**Punti chiave**:
- La variabile `count` è dichiarata `volatile`: indica al compilatore di non ottimizzarla in registro, perché può essere modificata da handler fuori dal flusso normale.
- Gli interrupt sono ricevuti **anche durante `delay()`** (come nota il commento): il delay non disabilita gli interrupt, quindi l'handler può intervenire in qualsiasi momento.
- L'interrupt resetta `count=0` e accende il LED verde; il loop principale incrementa `count`, aspetta 1 secondo, e gestisce il timeout a 10.

**Utilizzo tipico negli embedded IoT**: gli interrupt sono usati per ricevere dati dal sensore (read done), notificare la fine di una trasmissione radio, o rispondere a eventi fisici (pressione di un pulsante) senza polling continuo, risparmiando energia.

> [!note] Riferimento
> [[Lezione 23 - Embedded Programming e Arduino]]

---

## SMAC (Sensor-MAC)

![[exam_chessa_smac.jpg]]
*Fig. — S-MAC: i nodi A–F hanno schedule sincronizzati (verde = listen, rosso = active/TX). La latenza multi-hop si accumula: il pacchetto da A deve aspettare i periodi di ascolto di ogni hop successivo.*

**S-MAC** (*Sensor MAC*) è un protocollo MAC per WSN che riduce il consumo energetico tramite **sincronizzazione locale**: nodi vicini si accordano su un periodo di ascolto comune (listen period) e dormono nel resto del tempo.

**Meccanismo**:
1. Ogni nodo trasmette periodicamente un pacchetto **SYNC** che annuncia il proprio schedule (quando si sveglierà).
2. I vicini che ricevono il SYNC adottano lo stesso schedule o mantengono il proprio e memorizzano quello del vicino.
3. Nel **listen period**: esecuzione di CSMA/CA con RTS/CTS prima di trasmettere.
4. Nel **sleep period**: la radio è spenta.

**Duty cycle**: definito come $DC = t_{listen} / (t_{listen} + t_{sleep})$, tipicamente 10% in S-MAC.

**Problema della latenza multi-hop**: come visibile nello schema, ogni nodo deve aspettare il periodo di ascolto del nodo successivo. La latenza totale si accumula: se ogni hop aggiunge un'attesa $\approx t_{sleep}$, un percorso di $n$ hop ha latenza $\approx n \cdot (t_{sleep}/2)$ in media.

**Adaptive duty cycle**: se un nodo riceve un RTS o CTS (anche non destinato a lui), capisce che c'è traffico nelle vicinanze e mantiene la radio accesa — potrebbe essere il prossimo hop e il messaggio arriverà presto.

> [!note] Riferimento
> [[Lezione 17 - MAC Protocols]]

---

## BMAC - I (Struttura del Protocollo)

![[exam_chessa_bmac.jpg]]
*Fig. — B-MAC: il mittente (in alto) invia un lungo preamble seguito dai data; il ricevitore (in basso) si sveglia, ascolta, individua il preamble, rimane sveglio e riceve i data.*

**B-MAC** (*Berkeley MAC*) usa un approccio completamente diverso da S-MAC: **nessuna sincronizzazione** tra i nodi. Il principio è il **preamble sampling** (o Low Power Listening, LPL):

**Lato ricevitore**:
- Si sveglia periodicamente ogni $t_{check}$ millisecondi.
- Campiona il canale per un breve istante.
- Se rileva attività (preamble), rimane sveglio e riceve il pacchetto dati.
- Altrimenti, si riaddormenta immediatamente.

**Lato mittente**:
- Quando vuole trasmettere, invia un **preamble lungo** per una durata > $t_{check}$.
- Questo garantisce che, qualunque sia il momento in cui il ricevitore si sveglia per campionare, troverà il preamble ancora in corso.
- Dopo il preamble, invia i dati effettivi.

**Confronto con S-MAC**:
- B-MAC non richiede sincronizzazione → deployment più semplice.
- Il preamble lungo consuma energia extra dal mittente.
- Il ricevitore non spreca energia in lunghi listen period, ma solo in brevi campionamenti.

> [!note] Riferimento
> [[Lezione 17 - MAC Protocols]]

---

## BMAC - II (Trade-off t_check e Vita del Trasmettitore)

![[exam_chessa_bmac_graph.jpg]]
*Fig. — Grafico B-MAC: vita del trasmettitore (anni) vs intervallo di check t_check (ms), per diverse frequenze di campionamento (1 sample/min, 1/5 min, 1/10 min, 1/20 min).*

Il grafico mostra il trade-off fondamentale di B-MAC: come la frequenza di trasmissione e l'intervallo $t_{check}$ influenzano la vita della batteria del **trasmettitore**.

**Interpretazione**:
- Ogni curva rappresenta una diversa frequenza di campionamento dati (1 campione/minuto → consumo più alto, 1 campione/20 minuti → consumo più basso).
- Al crescere di $t_{check}$ (asse x), il preamble deve essere più lungo (per garantire che il ricevitore lo trovi), quindi il trasmettitore consuma di più per ogni trasmissione.
- Tuttavia, la vita del trasmettitore ha un **massimo** per un valore ottimale di $t_{check}$: troppo breve → il ricevitore si sveglia spesso ma il preamble è corto (basso overhead); troppo lungo → preamble lunghissimo, overhead alto.
- Per frequenze di trasmissione più basse (1/20 min), il trasmettitore vive molto più a lungo (fino a 7+ anni).

**Conclusione**: il parametro $t_{check}$ va ottimizzato in base al profilo di trasmissione dell'applicazione. Non esiste un valore universalmente ottimale.

> [!note] Riferimento
> [[Lezione 17 - MAC Protocols]]

---

## X-MAC / B-MAC (Confronto LPL vs X-MAC)

![[exam_chessa_xmac.jpg]]
*Fig. — Confronto LPL (B-MAC, righe superiori) e X-MAC (righe inferiori): X-MAC usa preamble corti con indirizzo target; il ricevitore invia early ACK; mittente e ricevitore risparmiano tempo ed energia.*

**X-MAC** migliora B-MAC risolvendo lo spreco energetico del long preamble con i **short preamble strobes** con target address:

**LPL (B-MAC)**:
- Mittente: invia un unico preamble lungo > $t_{check}$, poi i dati.
- Ricevitore: si sveglia, trova il preamble, rimane sveglio per tutta la durata del preamble + dati.
- **Problema**: anche i nodi non destinatari che si svegliano durante il preamble restano svegli inutilmente (overhearing).

**X-MAC**:
- Mittente: invia una sequenza di **short preambles** contenenti ciascuno l'indirizzo del destinatario target.
- Ricevitore target: si sveglia, legge il proprio indirizzo nel preamble, invia immediatamente un **early ACK**.
- Mittente: riceve l'ACK → interrompe la sequenza di preamble → trasmette i dati direttamente.
- **Risparmio**: il mittente non deve completare tutta la sequenza di preamble; il ricevitore non aspetta un preamble lungo.
- **Risparmio per i non-destinatari**: vedono il proprio indirizzo assente nel preamble → si riaddormentano subito.

Il risultato è un risparmio sia per il mittente (preamble più corto in media) sia per il ricevitore (less idle listening), indicato nello schema come "Time & energy saved at S & R".

> [!note] Riferimento
> [[Lezione 17 - MAC Protocols]]

---

## IEEE 802.15.4 - I (Struttura del Superframe)

![[exam_chessa_ieee802154_superframe.jpg]]
*Fig. — Struttura del superframe IEEE 802.15.4: Beacon frame → CAP (Contention Access Period, slot 0–6) → CFP (Contention Free Period, GTS1 e GTS2, slot 7–11) → Inactive period (slot 12–14) → prossimo Beacon.*

IEEE 802.15.4 definisce una struttura temporale chiamata **superframe** per organizzare l'accesso al canale in reti beacon-enabled:

**Beacon frame**: il coordinatore trasmette periodicamente un beacon che annuncia l'inizio del superframe, contiene i parametri della rete e la lista dei dispositivi con dati pendenti.

**CAP (Contention Access Period)**: periodo di accesso conteso tramite **CSMA/CA slottato**. Tutti i dispositivi competono per l'accesso al canale. Usato per traffico non deterministico (dati aperiodici).

**CFP (Contention Free Period)**: suddiviso in **GTS (Guaranteed Time Slots)**, assegnati dal coordinatore a specifici dispositivi per comunicazioni deterministiche a bassa latenza. Fino a 7 GTS per superframe. Usato per applicazioni real-time che richiedono garanzie temporali.

**Inactive period**: tutti i dispositivi (incluso il coordinatore) possono dormire per risparmiare energia. La durata del periodo inattivo determina il duty cycle della rete.

La durata del superframe è configurabile e determina il duty cycle: un inactive period lungo → basso duty cycle → lunga vita della batteria → latenza più alta.

> [!note] Riferimento
> [[Lezione 18 - The IEEE 802.15.4 Standard]]

---

## IEEE 802.15.4 - II (Indirect Data Transfer)

![[exam_chessa_ieee802154_indirect.jpg]]
*Fig. — Trasferimento dati indiretto in IEEE 802.15.4: il dispositivo si sveglia al beacon, invia una Data request al coordinatore, riceve ACK e poi i dati.*

Il trasferimento **indiretto** è usato quando il destinatario è un dispositivo che dorme la maggior parte del tempo (RFD, end-device). Il coordinatore non può trasmettere dati in modo asincrono perché il dispositivo potrebbe essere in sleep.

**Sequenza**:
1. Il **coordinatore** trasmette un **Beacon** che include (nella lista *pending addresses*) l'indirizzo dei dispositivi per cui ha dati in coda.
2. Il **dispositivo** si sveglia al beacon, legge la lista, se vede il proprio indirizzo invia una **Data request** al coordinatore.
3. Il **coordinatore** risponde con un **Acknowledgement** immediato.
4. Il **coordinatore** trasmette i **dati** accodati.
5. Il **dispositivo** risponde con un **Acknowledgement**.

Il device può poi tornare in sleep. Il vantaggio è che il dispositivo non deve rimanere sveglio ad aspettare dati: si sveglia solo al beacon (duty cycle controllato), controlla se ci sono dati per lui, li recupera e dorme di nuovo.

> [!note] Riferimento
> [[Lezione 18 - The IEEE 802.15.4 Standard]]

---

## IEEE 802.15.4 - III (Protocollo di Associazione)

![[exam_chessa_ieee802154_association.jpg]]
*Fig. — Protocollo di associazione IEEE 802.15.4: sequenza di messaggi tra NWK e MAC layer del dispositivo (sinistra) e del coordinatore/router (destra).*

Lo schema mostra il protocollo di **associazione** visto a livello di primitives NWK-MAC. È il meccanismo con cui un dispositivo entra nella rete:

1. Il NWK del dispositivo emette `ASSOCIATE.request` al proprio MAC layer.
2. Il MAC invia un **Association request** frame al coordinatore.
3. Il coordinatore MAC risponde con **Acknowledgement** immediato.
4. Il coordinatore NWK riceve `ASSOCIATE.indication` e prepara la risposta con `ASSOCIATE.response`.
5. Il dispositivo aspetta un **pre-defined waiting time** (il coordinatore deve elaborare la richiesta e decidere se accettarla).
6. Il dispositivo MAC invia una **Data request** per recuperare la risposta del coordinatore.
7. Il coordinatore MAC risponde con **Acknowledgement** + **Association response** (contenente l'indirizzo a 16 bit assegnato).
8. Il dispositivo MAC invia **Acknowledgement** finale.
9. Il dispositivo NWK riceve `ASSOCIATE confirm` con l'indirizzo assegnato.
10. Il coordinatore NWK riceve `COMM.STATUS.indication`.

Questo è il meccanismo di basso livello che corrisponde a `ASSOCIATE.request`/`ASSOCIATE.confirm` nelle primitive ZigBee viste nello schema ZigBee-I.

> [!note] Riferimento
> [[Lezione 18 - The IEEE 802.15.4 Standard]]

---

## Energy Harvesting — Domande Generali

> [!question] Domande del PDF
>
> - Explain the difference between an harvest-use and an harvest-store-use architecture
> - Explain the classification of sources in terms of controllability and predictability
> - Explain the concept of energy neutrality

### Harvest-Use vs Harvest-Store-Use

**Harvest-Use**: l'energia è raccolta e consumata istantaneamente. Non esiste un buffer. Il dispositivo funziona solo se $P_s(t) \geq P_c(t)$ (potenza sorgente ≥ potenza consumata). Se la sorgente produce meno del necessario il dispositivo si spegne; se produce di più l'eccesso va perduto. Esempi: mulini ad acqua, tag RFID passivi.

**Harvest-Store-Use**: un buffer energetico (batteria ricaricabile o supercapacitore) disaccoppia temporalmente produzione e consumo. L'energia in eccesso ($P_s > P_c$) viene accumulata nel buffer; l'energia in difetto ($P_c > P_s$) viene prelevata dal buffer. Un buffer ideale ha capacità infinita ed efficienza $\eta = 1$. Un buffer reale ha capacità massima $B_{max}$, efficienza $\eta < 1$, e una potenza di leakage $P_{leak}$.

### Classificazione delle Sorgenti

Le sorgenti si classificano su due assi:

**Controllabilità**:
- *Completamente controllabile*: energia disponibile su richiesta (torcia shake-to-power, sorgenti RF dedicate).
- *Parzialmente controllabile*: influenzabile ma non deterministica (RFID in ambiente RF non uniforme).
- *Non controllabile*: raccolta solo quando disponibile (sole, vento, calore ambientale).

**Prevedibilità** (per le sorgenti non controllabili):
- *Prevedibile*: esistono modelli affidabili (sole: ciclo giorno/notte + stagioni + meteo).
- *Non prevedibile*: nessun modello affidabile (vibrazioni da terremoti).

### Concetto di Energy Neutrality

Un dispositivo è **energy neutral** se, in qualsiasi intervallo di tempo, l'energia consumata non supera l'energia raccolta (più la carica iniziale del buffer):

$$\int_0^T P_c(t)\,dt \leq \int_0^T P_s(t)\,dt + B_0 \qquad \forall T$$

Il raggiungimento dell'energy neutrality richiede di adattare il carico in base alla disponibilità energetica prevista — obiettivo del problema di Kansal.

> [!note] Riferimento
> [[Lezione 24 - Energy Harvesting IoT]]

---

## Energy Harvesting - I (Grafico Ps vs Pc)

![[exam_chessa_energy_neutrality_graph.jpg]]
*Fig. — Grafico potenza/tempo: l'area tratteggiata in blu (Ps > Pc) è l'energia raccolta e accumulata nel buffer; l'area punteggiata (Pc > Ps) è l'energia prelevata dal buffer. La retta arancione mostra l'energia immediatamente consumata (Pc=Ps).*

Il grafico mostra due curve di potenza in funzione del tempo:
- $P_s(t)$: potenza prodotta dall'energy harvester (curva decrescente).
- $P_c(t)$: potenza consumata dal dispositivo (curva a forma di U).

Le due aree rappresentano:

$$\int_0^T [P_s(t) - P_c(t)]^+ dt$$

Area in blu (Ps > Pc, da t≈0 a t≈4): energia prodotta in eccesso → accumulata nel buffer. Il buffer si carica.

$$\int_0^T [P_c(t) - P_s(t)]^+ dt$$

Area punteggiata (Pc > Ps, da t≈4 a t≈8): il consumo supera la produzione → energia prelevata dal buffer. Il buffer si scarica.

La retta arancione indica la zona in cui $P_s = P_c$: energia prodotta e immediatamente consumata, senza passare dal buffer.

Il sistema è energy neutral se la prima integrale ≥ seconda integrale su tutto l'orizzonte temporale considerato.

> [!note] Riferimento
> [[Lezione 24 - Energy Harvesting IoT]]

---

## Energy Harvesting – II (Stima Stato di Carica)

![[exam_chessa_energy_harvesting_table.jpg]]
*Fig. — Tabella con parametri di batteria per tre piattaforme (RPI, Arduino, Tmote): tensioni min/max/ref, livelli di quantizzazione, xmin/xmax e stima Battery charge.*

La tabella mostra come misurare lo **stato di carica** (SoC) di una batteria attraverso la sua tensione terminale, per tre piattaforme hardware.

Le colonne chiave:
- $v_{min}$, $v_{max}$: range operativo della batteria (es. Arduino: 7–9 V).
- $v_{ref}$: risoluzione della quantizzazione ADC (es. Arduino: 0.008789 V per LSB).
- **quantization levels (bit)**: risoluzione dell'ADC (10 o 12 bit).
- $x_{min}$, $x_{max}$: valori ADC corrispondenti a $v_{min}$ e $v_{max}$.
- **Battery charge (mAh)**: capacità totale della batteria stimata.

L'idea è che la tensione ai terminali di una batteria è approssimabile come monotona rispetto alla carica residua. Campionando la tensione tramite ADC e mappando il valore digitale $x$ nell'intervallo $[x_{min}, x_{max}]$, si ottiene una stima lineare della carica rimanente:

$$\text{SoC} \approx \frac{x - x_{min}}{x_{max} - x_{min}} \times B_{cap}$$

Questa stima è utile per il task scheduler: sa quanta energia ha disponibile e può pianificare i task di conseguenza (approccio Kansal).

> [!note] Riferimento
> [[Lezione 24 - Energy Harvesting IoT]]

---

## Energy Harvesting – III (Approccio Kansal all'Energy Neutrality)

![[exam_chessa_kansal_system.jpg]]
*Fig. — Sistema Kansal: il Device (con Scheduler e Tasks energy model) è alimentato dall'Energy buffer (Battery + DC/DC converter), rifornito dall'Energy harvester. L'Energy predictor stima la disponibilità futura e informa lo Scheduler.*

L'approccio di **Kansal** all'energy neutrality mira a massimizzare le prestazioni del dispositivo garantendo al contempo che la batteria non si scarichi mai completamente (energy neutral operation).

Il sistema è composto da:

- **Energy harvester**: raccoglie energia dalla sorgente (es. pannello solare).
- **Energy buffer (Battery + DC/DC converter)**: accumula l'energia raccolta e la cede al dispositivo quando necessario.
- **Energy predictor** (con Energy source model): stima la quantità di energia che sarà disponibile nel futuro (ad es. usando previsioni meteo per un pannello solare).
- **Device** con **Scheduler** (e Tasks energy model): pianifica quali task eseguire e a quale frequenza, basandosi sia sullo stato attuale della batteria sia sulla predizione energetica futura.

**Idea centrale**: adattare il carico ($P_c$) alla disponibilità energetica prevista. Se le previsioni indicano un giorno soleggiato → il dispositivo può aumentare la frequenza di campionamento. Se le previsioni indicano bassa produzione → il dispositivo riduce l'attività.

**Condizione di energy neutrality di Kansal**:

$$B_T = B_0 + \eta \int_0^T [P_s - P_c]^+ dt - \int_0^T [P_c - P_s]^+ dt \geq B_{min} \quad \forall T$$

Il Kansal problem è quindi un problema di ottimizzazione: massimizzare le prestazioni (es. frequenza di campionamento) soggetto al vincolo di energy neutrality.

> [!note] Riferimento
> [[Lezione 28 - Kansal Problem e Energy Neutrality]]

---

## Energy Harvesting – IV (Task Model per l'Energy Neutrality)

![[exam_chessa_kansal_taskmodel.jpg]]
*Fig. — Task model: lo Scheduler pianifica i task in base al Tasks model (energia per task) e alle previsioni energetiche dell'Energy predictor (alimentato da weather forecast e da un Solar panel harvester collegato alla Battery).*

Lo schema espande il sistema Kansal con il dettaglio del **task model**. Rispetto allo schema III, qui è esplicitato il ruolo delle previsioni meteorologiche esterne.

**Componenti**:

- **Tasks model**: specifica il costo energetico di ogni task (es. campionamento = X mJ, trasmissione = Y mJ). Il Scheduler usa questo modello per stimare quanta energia consumerà ogni operazione.
- **Scheduler**: dato il livello attuale della batteria e la previsione di energia futura, decide:
  - Quali task eseguire nel prossimo periodo.
  - A quale frequenza/duty cycle eseguirli.
  - Obiettivo: massimizzare la qualità del servizio senza violare l'energy neutrality.
- **Energy predictor + Energy source model**: riceve dati dal weather forecast (Internet) e dalle misurazioni del pannello solare per costruire un modello predittivo della produzione energetica futura.
- **Solar panel energy harvester → Battery**: flusso di potenza fisico (linea arancione); informazioni di stato (linea tratteggiata) comunicano il livello di carica allo Scheduler.

**Flusso informativo** (linee tratteggiate):
- Weather forecast → Energy source model → Energy predictor → Scheduler
- Battery state → Scheduler (per decisioni in tempo reale)
- Tasks model → Scheduler (per la stima del costo)

> [!note] Riferimento
> [[Lezione 28 - Kansal Problem e Energy Neutrality]]

---

## Directed Diffusion

![[exam_chessa_directed_diffusion.jpg]]
*Fig. — Macchina a stati della Directed Diffusion: il nodo è Idle finché non riceve un interest; passa a Sampling e forward gli eventi corrispondenti verso il sink; torna Idle all'expire dell'interest.*

**Directed Diffusion** è un protocollo di routing **data-centric** per WSN, in cui i dati vengono nominati con coppie attributo-valore (non con indirizzi di rete).

**Fasi principali**:

1. **Interest propagation**: il sink diffonde in broadcast un **interest** (query) che descrive il tipo di dati desiderati (es. `type=temperature, area=sector-A, interval=30s`). Ogni nodo intermedio memorizza l'interest nella propria **interest cache** e imposta un **gradiente** verso il nodo da cui ha ricevuto l'interest (direzione verso il sink).

2. **Sampling** (stato attivo): un nodo che ha interest in cache e rileva dati corrispondenti (o riceve eventi corrispondenti da nodi vicini) li **forwarda verso il sink attraverso il gradiente** impostato.

3. **Expire e ritorno a Idle**: quando l'interest scade (`interest expires`), il nodo lo elimina dalla cache e torna allo stato Idle in attesa di nuovi interest.

**La macchina a stati del nodo**:
- **Idle** (waiting for interests): radio in ascolto, nessun sampling attivo.
- **Sampling**: il nodo è in fase di rilevamento e forwarding.
- Transizione Idle → Sampling: all'arrivo di un `interest received` → cache interest, set gradient.
- Transizione Sampling → Idle: `interest expires` → delete from cache.
- Permanenza in Sampling: se arriva un nuovo interest → aggiorna cache e gradiente.
- Evento in Sampling: se `event matching interest in cache` → forward al sink tramite gradiente.

**Reinforcement**: il sink può rinforzare il percorso migliore inviando un interest più frequente lungo il path ottimale, aumentando la frequenza di ricezione dati da quel percorso.

---

## GPSR - I (Greedy Forwarding e Void)

![[exam_chessa_gpsr_greedy.jpg]]
*Fig. — GPSR greedy: S forwarda verso x (più vicino a D); x incontra un void (nessun vicino è più vicino a D di x stesso) → attiva il perimeter routing attorno al void per raggiungere D.*

**GPSR** (*Greedy Perimeter Stateless Routing*) è un protocollo di routing geografico per WSN che usa le posizioni fisiche dei nodi. Ogni nodo conosce la propria posizione GPS e quella dei propri vicini immediati.

**Greedy Forwarding**:
- Ogni nodo forward il pacchetto al vicino **più vicino geograficamente alla destinazione D**.
- Esempio: S → a → e → x, perché in ogni hop si seleziona il vicino con distanza minima da D.
- Efficiente quando esiste sempre un vicino più vicino alla destinazione.

**Il problema del Void**:
- Un nodo $x$ si trova in un **void** quando nessuno dei suoi vicini è geograficamente più vicino a D di $x$ stesso.
- Il greedy routing si blocca in un void.
- Nell'immagine: $x$ è circondato da un void (area verde chiaro) → nessun vicino è più vicino a D.

**Soluzione — Perimeter Routing**:
- Quando si incontra un void, GPSR passa al **perimeter routing** (face routing).
- Il nodo $x$ inizia a navigare il confine del void usando la **right-hand rule** sul grafo planare.
- Il perimeter routing termina quando si raggiunge un nodo più vicino a D rispetto al punto in cui si è entrati nel void.
- Poi si torna al greedy forwarding.

---

## GPSR - II (Perimeter Routing / Face Traversal)

![[exam_chessa_gpsr_perimeter.jpg]]
*Fig. — Perimeter routing: il pacchetto naviga il confine del void (obstacle rettangolare) passando per w→x→y→z→destination, con alcuni nodi che rimandano indietro il pacchetto durante la face traversal.*

Il **perimeter routing** di GPSR è basato sulla **right-hand rule** applicata a un grafo planare:

**Right-hand rule**: muovendo verso il prossimo hop, gira sempre verso l'arco più a destra disponibile rispetto alla direzione di provenienza. Questo garantisce di attraversare ogni faccia del grafo esattamente una volta.

**Nell'esempio**:
- Il pacchetto entra in modalità perimeter a x (che è nel void).
- Naviga seguendo la right-hand rule: x → y → z → destination, con possibili rimbalzi tra nodi adiacenti.
- L'obstacle rettangolare (area rossa) rappresenta la zona senza nodi.
- Le frecce mostrano il percorso che circumnaviga l'obstacle.
- Quando si raggiunge un nodo (y, z) con distanza da D minore di quella del nodo di ingresso nel perimeter (x), si torna al greedy forwarding.

**Importante**: il perimeter routing funziona solo su un **grafo planare** (senza archi che si incrociano). Per questo GPSR richiede una fase di planarizzazione del grafo.

---

## GPSR - III (Planarizzazione: Gabriel Graph e RNG)

![[exam_chessa_gpsr_planarization.jpg]]
*Fig. — Planarizzazione del grafo: GG (sopra) e RNG (sotto). Un arco (u,v) è incluso solo se nessun nodo w cade nell'area tratteggiata (cerchio per GG, lente per RNG).*

Per applicare il face routing, GPSR ha bisogno di un **grafo planare** (senza archi incrociati). Due algoritmi di planarizzazione distribuita sono usati:

**Gabriel Graph (GG)**:
- Un arco $(u, v)$ è incluso nel GG se e solo se il **cerchio** con diametro $\overline{uv}$ non contiene nessun altro nodo $w$.
- Formalmente: $|uw|^2 + |vw|^2 > |uv|^2$ per ogni $w$ vicino di entrambi $u$ e $v$.
- Nel diagramma superiore: il cerchio (area tratteggiata) deve essere vuoto per includere l'arco.

**Relative Neighborhood Graph (RNG)**:
- Un arco $(u, v)$ è incluso se la **regione a lente** (intersezione dei cerchi di raggio $|uv|$ centrati in $u$ e $v$) non contiene nessun altro nodo $w$.
- Formalmente: $|uw| < |uv|$ e $|vw| < |uv|$ → $w$ è nella lente → l'arco viene eliminato.
- Nel diagramma inferiore: la lente tratteggiata deve essere vuota.

**RNG ⊆ GG**: l'RNG è più sparso (meno archi) del GG, perché la lente è più piccola del cerchio. Entrambi producono grafi planari su cui il face routing funziona correttamente.

**Distribuzione**: ogni nodo può calcolare localmente quali archi includere o escludere, consultando solo i propri vicini diretti. Non è richiesto stato globale.

---

> [!abstract] Riepilogo degli argomenti
>
> | Argomento | Lezione di riferimento |
> |-----------|----------------------|
> | Interoperabilità, vertical silos, vendor lock-in | [[Lezione 3 - Interoperabilità e Standard]] |
> | IoT Security, ITU-T Y.2066 | [[Lezione 3 - Interoperabilità e Standard]] |
> | MQTT pub/sub, topic, QoS 0/1/2 | [[Lezione 4 - MQTT Part 1]] |
> | MQTT sessioni, retained, last will, keepalive | [[Lezione 8 - MQTT Part 2]] |
> | ZigBee join, stack, topologie, indirizzamento | [[Lezione 9 - The ZigBee Standard Part 1]] |
> | ZigBee application layer, cluster, binding | [[Lezione 12 - Application Layer of ZigBee]] |
> | Duty cycle, embedded programming Arduino/TinyOS | [[Lezione 23 - Embedded Programming e Arduino]] |
> | SMAC, BMAC, X-MAC | [[Lezione 17 - MAC Protocols]] |
> | IEEE 802.15.4 superframe, indirect transfer | [[Lezione 18 - The IEEE 802.15.4 Standard]] |
> | Energy harvesting, architetture, fonti | [[Lezione 24 - Energy Harvesting IoT]] |
> | Kansal, task model, energy neutrality | [[Lezione 28 - Kansal Problem e Energy Neutrality]] |
