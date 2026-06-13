# Introduzione ai Cyber-Physical Systems e IoT

## Cyber-Physical Systems e Ambienti Intelligenti

I sistemi cyber-fisici (**Cyber-Physical Systems**, CPS) vivono e connettono due mondi distinti: possiedono sensori e attuatori per interagire con il mondo fisico e, contemporaneamente, sono entità cibernetiche dotate di capacità di elaborazione, memoria e comunicazione per agire nel ciberspazio. L'**Internet of Things** (IoT) rappresenta una "incarnazione" concreta di questi sistemi, implementando quelli che vengono definiti **ambienti intelligenti** (*smart environments*).

> [!definition] Cyber-Physical System (CPS)
>
> Sistema che integra capacità computazionali e di comunicazione con il controllo diretto del mondo fisico tramite sensori e attuatori. La componente cibernetica e quella fisica sono inseparabili e si influenzano reciprocamente.

In un ambiente intelligente, gli oggetti (*smart objects*) assumono una duplice natura fisica e cibernetica. Dal punto di vista fisico, qualsiasi oggetto è soggetto a esperienze tangibili: può essere posizionato in luoghi diversi, spostato ed è esposto ai rischi dell'ambiente esterno, come danni, furti o manomissioni. Questi dispositivi sono caratterizzati da posizionamento libero, dimensioni ridotte, diverse forme (*form factor*) e gusci protettivi. La mobilità è garantita da capacità di comunicazione wireless e alimentazione a batteria, rendendoli spesso consapevoli della propria posizione (*position-aware*). L'esposizione all'ambiente esterno impone ridondanza, sicurezza e costi contenuti.

Un ambiente si definisce "smart" principalmente in relazione all'utente finale: è in grado di riconoscere il contesto, le attività e le situazioni, comprendendo i bisogni dell'utente al momento giusto e fornendo servizi — anche fisici — tramite attuatori o robot. Le caratteristiche comuni di questi ambienti includono la pervasività e la natura non intrusiva dei dispositivi cyber-fisici. Il concetto di "smart" si estende però anche alla gestione, al dispiegamento (*deployment*) e alla manutenzione del sistema stesso: un sistema intelligente deve essere sostenibile, flessibile, sicuro e facile da usare.

---

## Le Quattro Generazioni di Internet

L'IoT rappresenta l'ultimo sviluppo di Internet e del computing, interconnettendo dispositivi intelligenti che vanno dagli elettrodomestici ai sensori minuscoli, integrando ricetrasmettitori mobili negli oggetti di uso quotidiano. Internet supporta la loro connettività, solitamente verso sistemi cloud, abilitando nuove forme di comunicazione tra persone e cose, e tra le cose stesse. Gli oggetti forniscono informazioni sensoriali, agiscono sul loro ambiente e, in alcuni casi, modificano se stessi come parte di un sistema più ampio.

È possibile identificare quattro generazioni di Internet in base ai sistemi finali supportati:

| Generazione | Tecnologia | Dispositivi tipici | Caratteristiche |
|---|---|---|---|
| Information Technology (IT) | Cablata | PC, server | Elaborazione e storage centralizzati |
| Operational Technology (OT) | Cablata/industriale | Macchinari, sistemi di controllo | Automazione di processi industriali |
| Personal Technology | Wireless | Smartphone, tablet | Connettività mobile personale |
| Sensor/Actuator Technology (IoT) | Wireless, batteria | Sensori, attuatori monoscopo | Bassa potenza, bassa banda, sistemi embedded |

L'IoT è guidato principalmente da dispositivi embedded a bassa potenza, bassa larghezza di banda ed energia limitata, ma include anche apparecchi come telecamere di sicurezza ad alta risoluzione che richiedono elevate capacità di streaming.

---

## Architettura a Livelli dell'IoT

Ogni dispositivo IoT è composto da sensori e attuatori, un microcontrollore, un'interfaccia wireless e un software che contiene la logica di business. L'architettura IoT è strutturata a livelli sovrapposti che rispecchiano la separazione tra mondo fisico, rete e applicazioni.

Alla base si trova il livello di **Percezione**, costituito dagli oggetti fisici e dai sensori che raccolgono dati dall'ambiente. Sopra di esso si trova il livello di **Comunicazione**, che gestisce le tecnologie di rete e wireless responsabili del trasporto dei dati. Seguono il livello di gestione delle risorse e dei servizi e il livello di gestione dei dati e della conoscenza, che comprende storage e *data analytics*. Al vertice vi sono i servizi specifici del dominio applicativo, come Smart Industry, Smart Energy o Smart Transport. Parallelamente a tutti i livelli opera la sicurezza, che non è un componente isolato ma una proprietà trasversale all'intera architettura.

> [!note] Sensori al livello di percezione
>
> I sensori possono monitorare parametri molto diversi a seconda del contesto. Per il tracciamento degli asset si utilizzano geolocalizzazione GNSS, prossimità NFC o rilevamento dell'orientamento tramite giroscopi. Per la logistica di magazzino si impiegano tecnologie come il Time of Flight (UWB) o l'Angle of Arrival (Bluetooth) per la localizzazione precisa al chiuso.

---

## Piattaforme IoT e Gestione dei Dati

Le **piattaforme IoT** agiscono come strati software tra i dispositivi e le applicazioni, distribuendo le funzionalità tra i dispositivi stessi, i gateway e i server nel cloud. Queste piattaforme offrono un insieme di funzionalità critiche che coprono l'intero ciclo di vita dei dispositivi e dei dati.

L'**identificazione** fornisce un modo univoco per riconoscere gli oggetti nella piattaforma, utilizzando standard come indirizzi IP, URI (*Universal Resource Identifier*) o UUID (*Universally Unique Identifier*). La **discovery** permette di trovare dispositivi, risorse e servizi all'interno di un dispiegamento IoT e di ottenerne le caratteristiche. La **gestione dei dispositivi** (*Device Management*) include l'inizializzazione, la configurazione, l'aggiornamento automatico di software e firmware, il monitoraggio — ad esempio del livello batteria — e il controllo remoto; esistono standard specifici come OMA LWM2M per i dispositivi IoT e BBF TR-069 per gli apparecchi utente. La **composizione dei servizi** costruisce servizi compositi integrando servizi di diversi dispositivi IoT e componenti software. Infine la **semantica** fornisce un modo per rappresentare i dispositivi e il loro contesto, abilitando ragionamento e elaborazione AI sui dati.

Per la gestione dei dati, specialmente in contesti di big data e applicazioni real-time, si utilizzano spesso database **NoSQL** come MongoDB, che offrono un design più semplice rispetto a SQL e scalano bene orizzontalmente. In MongoDB i record sono documenti con sintassi simile a JSON, dove i dati sono memorizzati come coppie nome/valore; questi documenti sono raggruppati in collezioni, che corrispondono alle tabelle dei database relazionali ma senza imporre la stessa struttura a tutti i documenti.

---

## Architetture di Rete: Edge, Fog e Cloud

Le problematiche di latenza, affidabilità e larghezza di banda nell'IoT vengono affrontate distribuendo l'elaborazione su diversi livelli di rete, ciascuno con caratteristiche e responsabilità distinte.

> [!definition] Cloud
>
> Livello centrale dell'architettura, caratterizzato da data center cablati e tempi di risposta transazionali. Adatto per l'archiviazione a lungo termine e l'elaborazione computazionalmente pesante.

> [!definition] Edge
>
> Livello periferico della rete aziendale, costituito dai dispositivi IoT stessi (sensori e attuatori) o dai gateway che li interconnettono. Opera con tempi di risposta nell'ordine dei millisecondi.

> [!definition] Fog Computing
>
> Livello intermedio tra Edge e Cloud. I dispositivi Fog sono fisicamente vicini all'Edge e convertono i flussi di dati di rete in informazioni adatte all'archiviazione o all'elaborazione di alto livello, riducendo il volume di dati inviati al cloud e garantendo tempi di risposta in tempo reale.

Lo scopo del Fog è eseguire l'elaborazione il più vicino possibile ai sensori — valutazione, formattazione, riduzione dei dati — alleggerendo così il traffico verso il cloud e abbattendo la latenza per le applicazioni che richiedono risposte immediate.

> [!tip] Intuizione chiave
>
> La scelta tra Edge, Fog e Cloud non è esclusiva: le architetture IoT moderne sfruttano tutti e tre i livelli in modo complementare, assegnando a ciascuno il tipo di elaborazione più adatto alle sue caratteristiche di latenza, capacità e affidabilità.

---

## Intelligenza Artificiale e Machine Learning

L'**Intelligenza Artificiale** (AI) nell'IoT mira a rendere i sistemi capaci di comportamenti intelligenti, sia attraverso la conoscenza curata sotto forma di regole causa-effetto, sia tramite il **Machine Learning** (ML). Il Machine Learning permette ai sistemi di imparare dai dati (*training set*) per associare input a output, generalizzando poi su dati mai visti prima.

I paradigmi principali del ML sono tre. L'apprendimento **non supervisionato** analizza strutture nei dati senza etichette predefinite. L'apprendimento **supervisionato** impara da esempi in cui sono forniti sia l'input sia l'output desiderato. L'apprendimento per **rinforzo** si basa su un meccanismo di ricompense: il sistema impara a compiere azioni che massimizzano una funzione di utilità interagendo con l'ambiente.

La **Blockchain** introduce un cambio di paradigma per l'IoT, spostando l'archiviazione da centralizzata a decentralizzata su un registro distribuito pubblico e fidato. Questo approccio garantisce che le transazioni non possano essere alterate retroattivamente, fornendo un *single point of truth* utile per la tracciabilità nelle catene di approvvigionamento e per aumentare la fiducia nei dati prodotti dai dispositivi.

---

## Interoperabilità e Sicurezza

### Interoperabilità

L'**interoperabilità** è una delle sfide più critiche dell'IoT. Spesso le soluzioni sono progettate come **silos verticali** (*vertical silos*), dove i dispositivi funzionano solo con componenti dello stesso produttore, generando il fenomeno del *vendor lock-in*. Per gestire standard incompatibili si utilizzano gateway a livello applicativo che mappano protocolli e comportamenti diversi, consentendo l'integrazione tra sistemi eterogenei.

Le configurazioni di interoperabilità variano da sistemi omogenei con stesso produttore e protocollo, fino a sistemi con produttori e protocolli diversi che richiedono gateway di integrazione distribuiti.

Tra gli standard wireless rilevanti per l'IoT, **IEEE 802.11** (WiFi) offre alta velocità nell'ordine dei Mbps con range limitato a circa 100 metri. **IEEE 802.15.4** e **ZigBee** privilegiano la bassa potenza e il basso throughput, supportando reti mesh multi-hop per coprire grandi aree. **Bluetooth** e la sua variante a basso consumo **BLE** (*Bluetooth Low Energy*) sono orientati alla comunicazione personale a corto raggio. Il **5G** offre banda larga mobile potenziata, comunicazioni massive tra macchine (*massive Machine Type Communications*) e comunicazioni ultra-affidabili a bassa latenza (*URLLC*), abilitando scenari come la guida autonoma e l'Industria 4.0.

### Sicurezza

La sicurezza è un punto critico a causa delle vulnerabilità dei sistemi embedded, spesso difficili da aggiornare (*patching*). I requisiti fondamentali, definiti nella raccomandazione **ITU-T Y.2066**, riguardano tre aree principali: la sicurezza della comunicazione (integrità e confidenzialità nel trasferimento dei dati), la sicurezza della gestione dei dati (archiviazione ed elaborazione) e la sicurezza della fornitura dei servizi (controllo degli accessi).

I gateway IoT svolgono funzioni di sicurezza essenziali: l'identificazione di ogni accesso, l'autenticazione — preferibilmente mutua — con dispositivi e applicazioni, e la protezione della privacy. Tuttavia, implementare queste misure su **dispositivi vincolati** (*constrained devices*) privi di capacità crittografiche può risultare impraticabile, rendendo necessario un bilanciamento tra sicurezza e risorse disponibili.

> [!warning] Vincoli dei dispositivi embedded
>
> Molti dispositivi IoT hanno risorse computazionali, memoria e autonomia energetica estremamente limitate. Questo rende difficile applicare protocolli crittografici standard e aggiornare il firmware dopo il dispiegamento, aumentando la superficie di attacco nel tempo.

---

> [!question] Possibili domande d'esame
>
> - Cos'è un Cyber-Physical System e in cosa si distingue da un sistema puramente informatico o puramente fisico?
> - Descrivere le quattro generazioni di Internet e le caratteristiche che differenziano l'IoT dalle generazioni precedenti.
> - Quali sono le differenze tra Edge Computing, Fog Computing e Cloud Computing in un'architettura IoT? In quale scenario conviene usare il Fog?
> - Quali funzionalità offre una piattaforma IoT e perché è necessario uno strato software intermedio tra dispositivi e applicazioni?
> - Quali sono le principali sfide di sicurezza e interoperabilità nell'IoT e come vengono affrontate a livello architetturale?
