# Software Defined Networking (SDN) — Architettura

Il Software Defined Networking è un paradigma architetturale che separa nettamente il **piano di controllo** (*control plane*) dal **piano dati** (*data plane*). Questa separazione permette di programmare il comportamento della rete in modo centralizzato, eliminando la rigidità dei dispositivi di rete tradizionali che incorporano sia la logica di instradamento che la funzione di forwarding. La lezione approfondisce l'architettura interna di questi due piani e i meccanismi con cui interagiscono.

## Motivazioni: Perché SDN?

Il Software Defined Networking non è nato per risolvere un semplice problema di capacità, ma per rispondere a una trasformazione strutturale delle reti moderne. La domanda di rete — alimentata da cloud computing, big data, traffico mobile e IoT — è cresciuta enormemente, ma anche l'offerta ha tenuto il passo: CPU più veloci, buffer più grandi, link ad alta capacità. Il vero problema, dunque, non è quantitativo ma qualitativo: **la complessità si è spostata dal volume alla variabilità**.

I pattern di traffico moderni sono *time-variant* (cambiano nel tempo), *spatially dynamic* (cambiano nei percorsi) e *application-sensitive* (dipendono dal tipo di applicazione). Questa variabilità richiede un controllo programmabile della rete, che le architetture tradizionali non sono in grado di offrire.

### Dinamiche del Traffico Moderno

Le applicazioni distribuite moderne accedono simultaneamente a molteplici database e server backend, generando significativo traffico "orizzontale" (*server-to-server*) in aggiunta al tradizionale traffico "verticale" (*client-server*). I servizi di Unified Communications (UC) — messaggistica, presenza, VoIP, videoconferenza — amplificano ulteriormente questa complessità, richiedendo alla rete di supportare flussi concorrenti con requisiti di QoS eterogenei.

L'adozione massiva del cloud computing ha spostato traffico che un tempo rimaneva all'interno delle reti enterprise verso data center remoti, rendendo i carichi sui router enterprise imprevedibili. La virtualizzazione dei server ha aggiunto un ulteriore strato: una singola macchina fisica ospita multiple VM tra cui avvengono significative comunicazioni (migrazione, replica, failover).

![Diagramma del traffico East-West nei data center: percorsi statici e dinamici tra server, con connettività East-West come problema principale](images/lezione-15-lab-sdn-architecture-img-01.jpg)
*Fig. 0 — Oltre il 70% del traffico nei data center moderni è East-West (tra server). Le architetture tradizionali a tre livelli (Access, Aggregation, Core) erano ottimizzate per il traffico North-South (client-server) e richiedono selezione flessibile dei percorsi, load balancing efficiente e riconfigurazione rapida.*

Il traffico mobile aggiunge un'ulteriore dimensione di imprevedibilità: i dispositivi mobili generano carichi rapidamente mutevoli e cambiano frequentemente il punto di connessione alla rete. Le applicazioni moderne richiedono trattamento differenziato: le applicazioni real-time (VoIP, videoconferenza) richiedono bassa latenza e alta priorità, mentre i trasferimenti bulk (backup) richiedono ampia banda ma tollerano ritardi.

### Limitazioni delle Reti Tradizionali

Le tendenze descritte richiedono una gestione flessibile delle risorse di rete, ma le architetture tradizionali mostrano tre limitazioni strutturali:

**A) Architettura statica e complessa**: le reti tradizionali sono costruite come collezione di protocolli indipendenti, ognuno pensato per una funzione specifica e separata (routing, spanning tree, ACL, ecc.). Il risultato è un control plane frammentato con complessità operativa crescente.

**B) Inconsistenza delle policy e rigidità operativa**: le modifiche di configurazione devono essere applicate manualmente su ogni singolo dispositivo. Le policy vengono enforced localmente, non globalmente, con alto rischio di misconfiguration.

**C) Dipendenza dal vendor e innovazione lenta**: la logica di controllo è embedded in hardware proprietario, con interfacce chiuse. Questo rende lento il deployment di nuovi servizi e limita la programmabilità.

---

## Il Paradigma SDN

### Separazione Control Plane / Data Plane

Le funzioni di rete a livello network si dividono in due categorie temporalmente molto diverse: il **forwarding** (spostare pacchetti dall'input all'output appropriato) avviene su scala temporale dei pacchetti (*fast timescales*), mentre il **routing** (determinare il percorso dei pacchetti da sorgente a destinazione) avviene su scala degli eventi di controllo (*slow timescales*). In una rete tradizionale, queste due funzioni sono tightly coupled nello stesso dispositivo.

> [!definition] Software Defined Networking (SDN)
>
> Approccio alla gestione di rete che usa l'astrazione per abilitare una configurazione e un'operazione della rete dinamica e programmaticamente efficiente. Separa il control plane dal data plane, centralizzando logicamente il primo in un controller remoto.

#### Il Problema del Traffic Engineering Tradizionale

Nelle reti con routing distribuito, i router calcolano i percorsi indipendentemente usando algoritmi come Dijkstra (link-state) o Bellman-Ford (distance-vector). Il problema è che l'unico "knob" disponibile all'operatore sono i pesi dei link: se si vuole forzare il traffico da u a z lungo il percorso uvwz invece di uxyz, bisogna ricalcolare i pesi, e questo può influenzare altri flussi in modo indesiderato.

![Diagramma di traffic engineering con routing tradizionale: topologia con nodi u, v, w, x, y, z e pesi sui link, evidenziando l'impossibilità di controllare percorsi specifici](images/lezione-15-lab-sdn-architecture-img-02.jpg)
*Fig. 0.1 — Con il routing tradizionale, i link weights sono gli unici "knob" di controllo. Non è possibile: (a) forzare percorsi specifici senza alterare il routing globale, (b) fare load balancing su più percorsi, (c) differenziare traffico di colori diversi sullo stesso nodo.*

SDN risolve questo problema spostando la logica di routing in un controller centralizzato che ha visione globale della rete e può installare regole arbitrarie in ogni switch.

#### Control Plane Logicamente Centralizzato

![Architettura SDN con controller remoto: il Remote Controller calcola e installa le forwarding table nei router, con control plane e data plane separati](images/lezione-15-lab-sdn-architecture-img-03.jpg)
*Fig. 0.2 — Nel modello SDN, un Remote Controller logicamente centralizzato calcola le forwarding table e le installa nei router. I dispositivi del data plane (con etichetta CA, Controlled Agent) eseguono le istruzioni ricevute senza logica di routing autonoma.*

In una rete tradizionale, ogni router calcola la propria forwarding table come:
$$T_i = \text{SPF}(\text{Topology}, \text{link weights})$$
Il comportamento globale emerge da computazioni locali non coordinate. Non vengono considerati la traffic demand (traffic matrix) né le policy applicative.

In SDN, un controller centralizzato calcola:
$$\mathcal{F}: S(t) \rightarrow \{T_1, T_2, \ldots, T_n\}$$
dove $S(t)$ include topologia, stato del traffico e policy. Le forwarding table vengono calcolate in modo **consistente** su tutta la rete.

#### I Quattro Pilastri di SDN

SDN si fonda su quattro idee principali:

1. **Generalized flow-based forwarding**: il forwarding non si basa solo sull'indirizzo IP di destinazione, ma può usare qualsiasi campo dell'header (OpenFlow)
2. **Separazione control plane / data plane**: i dispositivi del data plane eseguono il forwarding senza prendere decisioni di routing autonome
3. **Control plane esterno agli switch**: la logica di controllo risiede nel controller, non nei dispositivi di rete
4. **Programmabilità**: le applicazioni di controllo implementano funzioni di rete (routing, access control, load balancing) usando le API del controller

### Architettura SDN a Tre Livelli

![Architettura SDN a tre livelli: network-control applications (in alto), SDN Controller con northbound e southbound API (al centro), SDN-controlled switches (in basso)](images/lezione-15-lab-sdn-architecture-img-04.jpg)
*Fig. 0.3 — L'architettura SDN è organizzata in tre livelli: le applicazioni di controllo in cima, il controller (network OS) al centro, e gli switch programmabili in basso. Le NorthBound API collegano controller e applicazioni; le SouthBound API (es. OpenFlow) collegano controller e switch.*

**Data-plane switches**: switch veloci e semplici (*commodity*) che implementano il generalized forwarding in hardware. Le flow table sono calcolate e installate sotto la supervisione del controller. L'API per il controllo (es. OpenFlow) definisce cosa è controllabile e cosa non lo è.

**SDN Controller** (*network operating system*): mantiene le informazioni di stato della rete, interagisce con le applicazioni via NorthBound API e con gli switch via SouthBound API. È implementato come sistema distribuito per performance, scalabilità, fault-tolerance e robustezza.

**Network-control applications**: il "cervello" del sistema, implementano le funzioni di controllo (routing, access control, load balancing) usando i servizi di basso livello offerti dal controller. Possono essere fornite da terze parti, separate dal vendor del controller o degli switch.

### Breve Storia di SDN

| Anno | Evento |
|------|--------|
| ~2004 | Ricerca su nuovi paradigmi di gestione (Princeton, Stanford/Berkeley) |
| 2008 | NOX Network OS (NICIRA), interfaccia OpenFlow (Stanford/NICIRA) |
| 2011 | Open Networking Foundation — board: Google, Yahoo, Verizon; membri: Cisco, HP, Dell |
| 2013 | 1600 partecipanti all'Open Networking Summit; SDN usato nel WAN di Google (B4) |
| 2014 | SDN nei data center: VMware NSX, Cisco ACI |
| 2021+ | SDN guidato da AI/ML (Cisco DNA Center, Juniper Mist AI), SDN in reti 5G, IoT, edge; P4 per switch hardware programmabili |

> [!note] Da protocolli distribuiti a controllo programmabile
>
> La traiettoria di SDN riflette una tendenza più ampia nell'informatica: la separazione tra *policy* (cosa fare) e *meccanismo* (come farlo). Così come i sistemi operativi hanno astratto l'hardware dai programmi applicativi, SDN astrae l'infrastruttura di rete dalle applicazioni di controllo, abilitando innovazione indipendente a ogni livello.

---

## SDN Data Plane

Il data plane, chiamato anche *resource layer* o *infrastructure layer*, è composto da dispositivi di forwarding — switch fisici e virtuali — che trasportano e processano i dati secondo le decisioni del control plane. L'elemento chiave che distingue un dispositivo SDN da un router tradizionale è l'assenza di software autonomo per prendere decisioni di instradamento: il dispositivo esegue soltanto le istruzioni che riceve dal controller.

![Architettura SDN a tre livelli: Application Plane, Control Plane e Data Plane](images/lezione-15-lab-sdn-architecture-img-05.jpg)
*Fig. 1 — L'architettura SDN stratificata: il Data Plane è il livello inferiore, composto da switch che eseguono il forwarding secondo le regole imposte dal Control Plane via SouthBound API (es. OpenFlow).*

> [!definition] Forwarding Abstraction
>
> Un meccanismo generico e standardizzato con cui il control plane istruisce il data plane su come instradare i pacchetti. Non è legata a un tipo specifico di dispositivo: vale tanto per router quanto per switch o firewall.

### Forwarding Generalizzato e Match+Action

Nel forwarding tradizionale basato sulla destinazione (*destination-based forwarding*), un router confronta l'indirizzo IP di destinazione del pacchetto con la propria tabella di routing e lo instrada di conseguenza. Il forwarding generalizzato di SDN generalizza radicalmente questo concetto: qualsiasi campo dell'header del pacchetto — a livello link, rete o trasporto — può essere usato come chiave di corrispondenza (*match*), e le azioni possibili sono molto più ricche del semplice forwarding.

> [!tip] L'astrazione Match+Action
>
> Un pacchetto arriva allo switch → lo switch confronta i campi dell'header con le voci della **flow table** → se trova corrispondenza, esegue l'**azione** associata. Questa astrazione unifica in un unico modello dispositivi che in passato erano separati: router, switch, firewall, NAT.

Le azioni possibili includono:
- **drop**: scarta il pacchetto (firewall)
- **forward**: invia il pacchetto su una porta specifica (router/switch)
- **modify**: modifica campi dell'header (NAT, VLAN rewriting)
- **send to controller**: invia il pacchetto al controller per decisione centralizzata

### Flow Table e Astrazione di Flusso

Un **flusso** (*flow*) è definito dall'insieme dei valori che i campi header possono assumere. La **flow table** contiene regole della forma:

| Componente | Descrizione |
|------------|-------------|
| **Match** | Pattern da confrontare con i campi header (wildcard `*` per qualsiasi valore) |
| **Action** | Cosa fare con il pacchetto che corrisponde |
| **Priority** | Priorità per risolvere ambiguità tra regole sovrapposte |
| **Counters** | Contatori di byte e pacchetti per statistica |

I campi su cui si può effettuare il match coprono tre livelli OSI contemporaneamente: porta di ingresso, MAC sorgente/destinazione, tipo Ethernet, VLAN ID, IP sorgente/destinazione, protocollo IP, ToS, porte TCP/UDP sorgente e destinazione. Questa flessibilità consente di implementare policy di rete complesse con un singolo meccanismo uniforme.

> [!example] Esempi di regole OpenFlow
>
> - **Forwarding IP classico**: `IP Dst = 51.6.0.8` → `forward(port 6)` — tutti i datagrammi verso quell'IP vengono instradati sulla porta 6.
> - **Firewall (blocca SSH)**: `TCP dst-port = 22` → `drop` — blocca tutti i pacchetti TCP destinati alla porta 22.
> - **Blocco per sorgente**: `IP Src = 128.119.1.1` → `drop` — blocca tutto il traffico da quell'host.
> - **L2 forwarding**: `Eth Dst = 22:A7:23:11:E1:02` → `forward(port 3)` — forwarding basato su MAC address.

---

### OpenFlow

**OpenFlow** è il protocollo standard che implementa la *SouthBound API* di SDN. Definisce come il controller comunica con i dispositivi di forwarding per installare, modificare e rimuovere regole nella flow table. Il primo paper che lo ha introdotto è di Nick McKeown et al. (2008) e ha dato origine a un intero ecosistema gestito oggi dalla *Open Networking Foundation (ONF)*.

> [!definition] OpenFlow
>
> Protocollo di comunicazione nelle architetture SDN che permette ai controller di consegnare *forwarding entries* ai dispositivi di data plane (switch e router, fisici e virtuali). È la principale implementazione della SouthBound API.

Sebbene l'adozione in ambienti di produzione rimanga limitata, OpenFlow ha un valore fondamentale per la ricerca e la didattica, avendo ispirato soluzioni più avanzate come **P4** (p4.org) per la programmazione generalizzata del data plane.

#### Struttura di una Flow Entry OpenFlow

Ogni voce nella flow table OpenFlow ha tre campi fondamentali:

1. **Match**: i campi header da confrontare (tutti i livelli)
2. **Action**: le operazioni da eseguire (forward, drop, modify header, encapsulate e invia al controller)
3. **Stats**: contatori di pacchetti e byte per monitoraggio

#### OpenFlow come Astrazione Unificante

> [!tip] Un solo modello per tutti i dispositivi
>
> | Dispositivo | Match | Action |
> |-------------|-------|--------|
> | Router | Longest prefix IP dst | Forward su link |
> | Switch L2 | MAC address destinazione | Forward o flood |
> | Firewall | IP + TCP/UDP port | Permit o deny |
> | NAT | IP address e port | Rewrite address e port |
>
> Tutti questi dispositivi, storicamente separati, diventano istanze della stessa astrazione match+action con flow table diverse.

---

### OpenFlow Switch e Flow Table Pipeline

Un OpenFlow switch ha tre componenti principali:

1. **Porte I/O**: le interfacce fisiche attraverso cui entrano ed escono i pacchetti
2. **Flow Tables** (*Datapath*): tabelle organizzate in pipeline per il processing dei pacchetti
3. **OpenFlow Channel**: il canale di comunicazione sicuro (TCP, opzionalmente TLS) con il controller

![Architettura interna di un OpenFlow Switch: porte, pipeline di flow table, group table, e canale OpenFlow verso il controller](images/lezione-15-lab-sdn-architecture-img-06.jpg)
*Fig. 2 — L'OpenFlow Switch: il canale OpenFlow collega lo switch al controller, che può aggiungere, aggiornare e rimuovere flow entries sia in modo reattivo (in risposta ai pacchetti) che proattivo.*

#### Flow Table Pipeline

Uno switch può contenere **una o più flow table** organizzate in **pipeline**. Le tabelle sono numerate sequenzialmente a partire da 0. Il pacchetto viene processato prima dalla tabella 0, e in base al risultato del match può essere diretto ad altre tabelle, a una group table, a una meter table, o infine all'uscita.

$$
\text{Packet in} \rightarrow [\text{Table 0}] \rightarrow [\text{Table 1}] \rightarrow \cdots \rightarrow [\text{Table N}] \rightarrow \text{Packet out}
$$

L'uso di più tabelle in pipeline offre al controller notevole flessibilità: permette, ad esempio, di separare le regole di sicurezza da quelle di routing in tabelle distinte, applicandole in sequenza.

#### Processing Pipeline

Quando un pacchetto viene processato da una flow table:
- Se c'è **corrispondenza** con una o più entry, viene eseguita la regola con **priorità più alta**. Le istruzioni possono aggiornare l'action set, aggiornare metadata, eseguire azioni, o redirigere il pacchetto con `Goto` a un'altra tabella.
- Se c'è corrispondenza solo con la **table-miss entry** (entry speciale per pacchetti senza match), si può: (a) inviare al controller, (b) redirigere a un'altra tabella, (c) scartare.
- Se **non c'è alcun match** e non esiste table-miss entry, il pacchetto viene **scartato**.

---

### Group Tables

Oltre alle flow table, OpenFlow definisce le **group table**. Un pacchetto che corrisponde a una flow entry può essere diretto non a una singola porta di uscita, ma a un *group entry*, che specifica come il pacchetto deve essere gestito su più porte.

Ogni group entry ha:
- Un **Group ID** univoco
- Un **Group Type** che definisce la semantica
- Uno o più **action bucket** con le azioni possibili

| Group Type | Comportamento |
|------------|--------------|
| **ALL** | Il pacchetto viene inviato a tutti i bucket (multicast/broadcast) |
| **SELECT** | Il pacchetto viene inviato a un singolo bucket scelto per load balancing o hashing |

> [!example] Group Table in azione
>
> - Group 1 (ALL): Output su Port 2 e Port 3 → flooding su entrambe le porte
> - Group 2 (SELECT): Output su Port 4 o Port 5 → bilanciamento del carico tra due link

---

## SDN Control Plane

Il control plane SDN è il livello di intelligenza della rete. Centralizza la logica di instradamento, il calcolo dei percorsi e la gestione delle policy in un componente software chiamato **controller SDN**, che mantiene una visione globale e consistente dello stato della rete.

### Componenti del Controller SDN

Il controller SDN è organizzato in tre strati funzionali:

**Strato di comunicazione (*Communication Layer*)**: gestisce la comunicazione bidirezionale tra il controller e i dispositivi del data plane. I protocolli utilizzati sono OpenFlow (SouthBound API), SNMP, e altri.

**Strato di gestione dello stato di rete (*Network-Wide State Management*)**: mantiene un database distribuito con le informazioni sullo stato dell'intera rete: topologia dei link, informazioni sugli host, flow table degli switch, statistiche. È il cuore del controller, poiché fornisce la *global network view* necessaria per decisioni di routing ottimali.

**Strato di interfaccia verso le applicazioni (*Interface Layer*)**: espone API (*NorthBound API*) alle applicazioni di controllo (routing, access control, load balancing, orchestrazione). Queste API permettono alle applicazioni di interagire con la rete in modo astratto, senza conoscere i dettagli del protocollo SouthBound.

### Protocollo OpenFlow — Messaggi

OpenFlow opera tra controller e switch tramite **TCP** (opzionalmente cifrato con TLS). I messaggi sono divisi in tre classi:

**Controller → Switch:**

| Messaggio | Funzione |
|-----------|----------|
| **features** | Il controller interroga lo switch sulle sue capacità, lo switch risponde |
| **configure** | Il controller legge o imposta parametri di configurazione dello switch |
| **modify-state (FlowMod)** | Aggiunge, elimina o modifica flow entries nelle tabelle OpenFlow |
| **packet-out** | Il controller invia un pacchetto incapsulato a una porta specifica dello switch |

**Switch → Controller:**

| Messaggio | Funzione |
|-----------|----------|
| **packet-in** | Lo switch trasferisce un pacchetto (e il suo controllo) al controller |
| **flow-removed** | Notifica che una flow entry è stata eliminata dallo switch |
| **port-status** | Informa il controller di un cambiamento di stato su una porta |

> [!warning] I network operator non programmano OpenFlow direttamente
>
> In pratica, gli operatori usano astrazioni di alto livello fornite dal controller (es. intent framework in ONOS). La scrittura diretta di messaggi OpenFlow è riservata allo sviluppo interno del controller.

### Interazione Control Plane / Data Plane — Esempio

Un esempio concreto illustra la collaborazione tra i componenti. Si consideri un guasto su un link della rete:

1. Lo switch **S1** rileva il guasto e invia al controller un messaggio **port-status** per notificare il cambiamento di stato del link.
2. Il **controller SDN** riceve il messaggio e aggiorna il proprio database di stato dei link.
3. L'applicazione di routing **Dijkstra** (che si è registrata per ricevere notifiche sui cambiamenti di link) viene invocata.
4. Dijkstra accede al grafo della rete e alle informazioni di link-state nel controller e calcola i **nuovi percorsi ottimali**.
5. L'applicazione di routing interagisce con il componente di calcolo delle flow table nel controller per determinare le nuove regole da installare.
6. Il controller invia messaggi **FlowMod** via OpenFlow agli switch interessati per installare le nuove flow table.

> [!note] SDN vs routing distribuito tradizionale
>
> In una rete tradizionale, i router eseguono OSPF o BGP e calcolano i percorsi autonomamente scambiandosi informazioni. In SDN, questa logica è centralizzata nel controller: questo semplifica il coordinamento, ma richiede robustezza e alta disponibilità del controller stesso.

---

### Implementazioni di Controller SDN

| Controller | Note |
|------------|------|
| **NOX** | Primo controller SDN, riferimento storico |
| **Ryu** | Framework Python per SDN |
| **OpenDaylight (ODL)** | Controller open source enterprise-grade |
| **ONOS** | Open Network OS, forte enfasi su distribuzione e scalabilità |
| **TeraFlow SDN** | Controller per reti cloud-native, progetto ETSI |

#### OpenDaylight (ODL)

OpenDaylight è uno dei controller SDN più diffusi in ambienti enterprise. La sua architettura è stratificata:

- **Northbound API**: REST/RESTCONF/NETCONF per le applicazioni (Traffic Engineering, Firewalling, Load Balancing, Orchestration)
- **Basic Network Functions**: moduli interni per topology processing, switch management, statistiche, host tracking, gestione regole di forwarding
- **Service Abstraction Layer (SAL)**: il bus interno che interconnette applicazioni, servizi interni e protocolli SouthBound
- **Southbound API**: OpenFlow, NETCONF, SNMP, OVSDB

> [!tip] SAL in ODL
>
> Il Service Abstraction Layer è l'elemento architetturale chiave di ODL: agisce da mediatore tra il mondo delle applicazioni (Northbound) e i protocolli di rete specifici (Southbound), rendendo il controller agnostico rispetto al protocollo SouthBound utilizzato.

#### ONOS

ONOS (*Open Network Operating System*) enfatizza la separazione delle applicazioni di controllo dal core del controller e la robustezza distribuita:

- Le **applicazioni di controllo** (Traffic Engineering, Firewalling, Load Balancing) sono separate dal controller core e comunicano via Northbound API
- L'**intent framework** permette alle applicazioni di specificare *cosa* si vuole ottenere (es. connettività tra due host) piuttosto che *come* (es. quale percorso usare): il controller si occupa di tradurre l'intent in flow rules concrete
- Il **distributed core** garantisce alta disponibilità e scalabilità attraverso replicazione e consensus distribuito

---

## Forwarding e Topology Discovery

Un aspetto cruciale in una rete SDN è come il controller costruisce la conoscenza della topologia e come gestisce il forwarding dei pacchetti prima che le flow table siano popolate.

### Path Computation

![Diagramma di path computation: un pacchetto da A a B genera un Packet-In verso il controller, che risponde con FlowMod per popolare le flow table di S1 e S2](images/lezione-15-lab-sdn-architecture-img-07.jpg)
*Fig. 3 — Path computation: le flow table degli switch sono inizialmente vuote. Il primo pacchetto da A a B genera un Packet-In; il controller calcola il percorso e installa le regole via FlowMod.*

Quando un pacchetto arriva a uno switch e non trova corrispondenza nella flow table (*table-miss*), lo switch lo invia al controller tramite un messaggio **Packet-In**. Il controller, disponendo di una Host Table e di una Topology Table già popolate, calcola il percorso ottimale da sorgente a destinazione e invia messaggi **FlowMod** agli switch lungo il percorso.

> [!warning] Ordine di installazione delle flow entries
>
> I messaggi FlowMod vengono inviati in **ordine inverso**: prima allo switch più vicino alla destinazione, poi risalendo verso la sorgente. Questo garantisce che quando il pacchetto arriva al secondo switch, la regola sia già installata, evitando un secondo Packet-In al controller.

Una volta installate le regole, tutti i pacchetti successivi dello stesso flusso vengono gestiti direttamente dagli switch, senza passare dal controller.

---

### Routing Centralizzato

In una rete tradizionale, la funzione di routing è distribuita tra i router, ognuno dei quali mantiene la propria tabella di routing e partecipa a protocolli come OSPF. In SDN, è naturale centralizzare questa funzione nel controller, che:

- Ha una visione **globale e coerente** dello stato della rete
- Può implementare **policy application-aware** (es. preferire certi link per certi tipi di traffico)
- Libera gli switch dal burden computazionale e di storage del routing, migliorandone le prestazioni

Il routing centralizzato svolge due funzioni distinte:

1. **Link/Topology Discovery**: il controller deve conoscere i link tra gli switch del data plane (non standardizzata in OpenFlow, ogni implementazione ha il proprio approccio)
2. **Topology Manager**: mantiene la topologia aggiornata e calcola i percorsi più brevi tra nodi

---

### Inizializzazione degli Switch

![Switch Initialization: handshake tra switch e controller con Feature Request e Feature Reply](images/lezione-15-lab-sdn-architecture-img-08.jpg)
*Fig. 4 — Switch Initialization: al boot, lo switch stabilisce una connessione TCP con il controller. Lo scambio Feature Request / Feature Reply comunica al controller i parametri dello switch (Switch ID, porte attive).*

Quando uno switch OpenFlow viene acceso, esegue una procedura di handshake con il controller:

1. Lo switch tenta di stabilire una **connessione TCP** con l'indirizzo del controller (pre-configurato)
2. Il controller invia un messaggio **FEATURE REQUEST**
3. Lo switch risponde con un messaggio **FEATURE REPLY** contenente: Switch ID, lista delle porte attive, e altri parametri rilevanti

Al termine dell'handshake, il controller sa esattamente quante porte attive ha ogni switch, ma **non conosce ancora le connessioni fisiche tra switch**. Per questo è necessaria la topology discovery.

---

### Topology Discovery con LLDP

La topology discovery in reti OpenFlow si basa sul **Link Layer Discovery Protocol (LLDP)**, standardizzato da IEEE nel 2005 e 2009. LLDP è un protocollo *vendor-neutral* che opera al Livello 2 del modello OSI e permette a un dispositivo di annunciare la propria identità e le proprie capacità ai dispositivi adiacenti.

Gli switch OpenFlow hanno due configurazioni iniziali che abilitano la topology discovery:
1. **Indirizzo del controller**: ogni switch ha pre-configurato l'IP e la porta TCP del controller, a cui si connette al boot
2. **Flow rule per LLDP**: ogni switch ha una regola pre-installata che invia al controller (via Packet-In) qualsiasi frame LLDP ricevuto

#### Struttura del Frame LLDP

![Struttura del frame LLDP: campi Chassis ID, Port ID, Time to Live, End of LLDPDU](images/lezione-15-lab-sdn-architecture-img-09.jpg)
*Fig. 5 — Struttura del frame LLDP. Il tipo Ethernet è 0x88cc. I TLV (Type-Length-Value) fondamentali sono: Chassis ID (switch mittente), Port ID (porta mittente), TTL, End of LLDPDU.*

Il frame LLDP usa Ethernet come protocollo di trasporto (EtherType `0x88cc`) e contiene i seguenti campi TLV (*Type-Length-Value*):

| TLV | Tipo | Contenuto |
|-----|------|-----------|
| Chassis ID | 1 | Identificatore dello switch che invia il frame LLDP |
| Port ID | 2 | Identificatore della porta attraverso cui il frame viene inviato |
| Time to Live | 3 | Validità in secondi delle informazioni contenute nel frame |
| End of LLDPDU | 4 | Marcatore di fine payload |

#### Processo di Topology Discovery

Il processo si svolge in quattro passi:

1. Il controller genera un **Packet-Out** per ogni porta attiva su ogni switch scoperto, incapsulando al suo interno un frame LLDP con il Chassis ID e il Port ID dello switch sorgente.
2. Quando uno switch OF riceve un messaggio Packet-Out con un frame LLDP, lo **forwarda** sulla porta specificata nel Port ID verso lo switch adiacente.
3. Lo switch adiacente, ricevendo il frame LLDP su una porta non di controllo, lo **incapsula in un Packet-In** indirizzato al controller, includendo i propri Switch ID e Port ID come metadata.
4. Il controller riceve il Packet-In ed **estrae le informazioni**: conosce ora lo Switch ID e Port ID del frame LLDP (mittente originale) e lo Switch ID e Port ID del Packet-In (ricevente). Da questi dati deduce che esiste un link tra quei due switch su quelle specifiche porte.

> [!tip] Scalabilità della topology discovery
>
> In una rete con $S$ switch e un totale di $P$ porte attive, il numero di messaggi Packet-Out inviati dal controller è pari a $P$ (uno per porta attiva su ciascuno switch). L'intero processo viene eseguito periodicamente per rilevare cambiamenti nella topologia.

> [!note] Topology Discovery non standardizzata
>
> Il meccanismo di topology discovery non è standardizzato in OpenFlow: ogni implementazione di controller (ODL, ONOS, Ryu) può adottare varianti proprie. La procedura basata su LLDP descritta qui è quella tipicamente usata.

---

### Host Reachability

La scoperta della raggiungibilità degli host avviene in modo simile alla topology discovery, ma è **event-driven**: viene tipicamente scatenata da traffico sconosciuto che entra nel dominio SDN da un host collegato o da un router vicino.

Quando un host A invia il primo pacchetto verso B e lo switch non ha una regola corrispondente, invia un Packet-In al controller. Il controller:
1. Registra nella **Host Table** l'indirizzo Ethernet di A, lo switch a cui è collegato, e la porta
2. Calcola il percorso verso B (se B è già nella Host Table) oppure avvia una procedura di discovery

La Host Table cresce progressivamente man mano che gli host comunicano, costruendo una mappa completa della rete.

> [!question] Possibili domande d'esame
>
> - Come differisce il forwarding generalizzato dal destination-based forwarding? Quali campi possono essere usati per il match e quali azioni sono disponibili?
> - Descrivere la struttura di una flow entry OpenFlow (match, action, priority, counters) e fare un esempio di regola per implementare un firewall.
> - Descrivere le tre classi di messaggi OpenFlow (controller-to-switch, switch-to-controller, symmetric) e gli esempi principali per ciascuna.
> - Come funziona la flow table pipeline in OpenFlow? Cosa succede in caso di table-miss?
> - Descrivere il processo di topology discovery in una rete SDN: quale protocollo usa, quali messaggi vengono scambiati, e come il controller costruisce la mappa dei link.
> - Qual è la differenza tra Path Computation in SDN e routing distribuito tradizionale? Perché i FlowMod vengono inviati in ordine inverso?
> - Confrontare l'architettura di OpenDaylight (ODL) e ONOS: cosa li distingue in termini di struttura interna e approccio alla programmabilità?
