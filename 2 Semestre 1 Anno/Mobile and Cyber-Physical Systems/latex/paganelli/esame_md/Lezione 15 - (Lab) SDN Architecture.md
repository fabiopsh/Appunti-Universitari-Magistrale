# Software Defined Networking (SDN) — Architettura

Il Software Defined Networking è un paradigma architetturale che separa nettamente il **piano di controllo** (*control plane*) dal **piano dati** (*data plane*). Questa separazione permette di programmare il comportamento della rete in modo centralizzato, eliminando la rigidità dei dispositivi di rete tradizionali che incorporano sia la logica di instradamento che la funzione di forwarding. 

## Il Paradigma SDN e la Separazione dei Piani

Le funzioni di rete a livello network si dividono in due categorie temporalmente molto diverse: il **forwarding** (spostare pacchetti dall'input all'output appropriato) avviene su scala temporale dei pacchetti (*fast timescales*), mentre il **routing** (determinare il percorso dei pacchetti da sorgente a destinazione) avviene su scala degli eventi di controllo (*slow timescales*). In una rete tradizionale, queste due funzioni sono tightly coupled nello stesso dispositivo.

### Esempio di rete gestita con SDN

![[exam_mod2_sdn_example.jpg]]

Questo schema è un esempio concreto di rete gestita con SDN per mostrare come il **control plane centralizzato** possa implementare politiche impossibili con il routing tradizionale.

Nell'architettura mostrata, il **controller OpenFlow** mantiene una visione globale della topologia: conosce tutti gli switch, tutte le loro porte, e dove si trovano i vari host. Le flow table degli switch s1, s2, s3 vengono popolate **dal controller**, non calcolate localmente dagli switch.

**Traffic Engineering con SDN:** supponiamo che il controller voglia bilanciare il traffico da h1 (10.1.0.1) verso h4 (10.2.0.4) su due percorsi:
- Percorso A: h1 → s1 → s2 → h4
- Percorso B: h1 → s1 → s3 → s2 → h4

Con il routing IP tradizionale questo è impossibile: l'algoritmo SPF converge su un solo percorso minimo. Con SDN, il controller installa regole diverse in s1 per flussi diversi (es. dividendo per porta sorgente TCP), realizzando il load balancing.

**Forwarding basato su flusso:** il controller può distinguere il traffico h1→h4 dal traffico h2→h4 e applicare politiche diverse. Ad esempio:
- Traffico h1→h4: percorso s1→s2, priorità alta
- Traffico h2→h4: percorso s1→s3→s2, priorità normale

Questo è il **routing per-flusso**, impossibile nel routing tradizionale destination-based.

**Topology discovery:** il controller scopre la topologia inviando pacchetti LLDP (*Link Layer Discovery Protocol*) tramite gli switch. Ogni switch incapsula un pacchetto LLDP e lo invia su tutte le porte; quando un altro switch lo riceve, lo invia al controller, che così ricostruisce le connessioni tra switch.

---

## Architettura SDN a Tre Livelli

![[exam_mod2_sdn_architecture.jpg]]

L'architettura SDN è organizzata in tre livelli che realizza la separazione netta tra data plane, control plane e application plane.

**Data Plane (Livello inferiore):** contiene gli switch del data plane, che possono essere sia fisici (hardware commodity a basso costo) sia virtuali (Open vSwitch su hypervisor). Sono dispositivi semplici: il loro unico compito è applicare meccanicamente le regole di forwarding (match-action) ai pacchetti in transito secondo le flow table installate dal controller. Non calcolano nulla autonomamente. L'API per il controllo (es. OpenFlow) definisce cosa è controllabile e cosa non lo è.

**Control Plane (Livello centrale):** contiene il controller SDN, o meglio una **rete di controller SDN** distribuiti (*network operating system*). Sebbene appaia come un'entità logicamente centralizzata (ha una visione globale della rete), è implementato fisicamente come sistema distribuito per garantire tolleranza ai guasti e scalabilità. Il controller mantiene: la topologia della rete, le statistiche dei flussi, i link attivi, le tabelle di forwarding. Comunica verso il basso con il Data Plane tramite la **Southbound API** (tipicamente OpenFlow), e verso l'alto con le applicazioni tramite la **Northbound API**. I controller comunicano tra loro tramite **Westbound/Eastbound API** per sincronizzare lo stato globale.

**Application Plane (Livello superiore):** contiene le applicazioni di controllo della rete (*network-control applications*), il vero "cervello" del sistema. Sono **unbundled**: possono essere sviluppate da terze parti indipendentemente dai produttori hardware e software del controller. Esempi: load balancer, firewall, traffic engineering, monitoraggio, rilevamento anomalie. Le applicazioni esprimono policy di alto livello al controller tramite la Northbound API.

---

## SDN Data Plane

Il data plane è composto da dispositivi di forwarding — switch fisici e virtuali — che trasportano e processano i dati secondo le decisioni del control plane. 

### Forwarding Generalizzato e Match-Action

![[exam_mod2_sdn_generalized_forwarding.jpg]]

Questo schema illustra il concetto di **forwarding generalizzato** (*generalized forwarding*) in SDN, che è l'astrazione fondamentale che rende il data plane programmabile.

Nell'approccio tradizionale, i router inoltrano i pacchetti basandosi **solo sull'indirizzo IP di destinazione** (*destination-based forwarding*). OpenFlow generalizza questo concetto con l'astrazione **match-action**: ogni pacchetto viene confrontato con le regole nella flow table, e quando c'è un match, viene eseguita l'azione corrispondente.

**I campi di match** possono essere qualsiasi combinazione dei seguenti:
- Livello 1: **Ingress Port** (la porta fisica da cui è arrivato il pacchetto)
- Livello 2 (Datalink): Src MAC, Dst MAC, Eth Type, VLAN ID, VLAN Priority
- Livello 3 (Rete): IP Src, IP Dst, IP Protocol, IP ToS
- Livello 4 (Trasporto): TCP/UDP Src Port, TCP/UDP Dst Port

Questo consente di distinguere flussi in base a qualsiasi combinazione di questi campi: non solo la destinazione IP, ma anche il protocollo, le porte, le VLAN, ecc. Si parla di **flow-based forwarding**.

**Le azioni possibili** sono:
1. **Forward to port(s)**: invia il pacchetto su una o più porte (forwarding normale, broadcast, multicast).
2. **Drop**: scarta il pacchetto (firewall, access control).
3. **Modify fields in header**: modifica campi dell'intestazione prima di forwardare (NAT, QoS marking, VLAN tagging).
4. **Encapsulate and forward to controller**: invia il pacchetto al controller SDN per una decisione centralizzata (usato per pacchetti non matchati da nessuna regola — *table-miss*).

**Stats**: ogni entry mantiene contatori di pacchetti e byte, utili per monitoring e traffic engineering.

> [!tip] Generalità del match-action
>
> L'astrazione match-action è sufficientemente generale da esprimere: routing IP (match su IP dst), load balancing (match su src/dst + hash), firewall (match su src/dst/protocol + drop), NAT (match + modify). Un singolo modello unifica dispositivi che nelle reti tradizionali richiederebbero apparati separati.

---

### OpenFlow Switch e Flow Table Pipeline

![[exam_mod2_openflow_switch.jpg]]

Lo schema illustra l'architettura interna di uno switch OpenFlow, distinguendo il **piano dati interno** (*Datapath*) dal **canale di controllo** (*Control Channel*).

**Ports:** lo switch ha porte fisiche su cui arrivano e partono i data packet flow (TCP/IP, UDP/IP, altri). Sono le interfacce verso la rete esterna.

**Pipeline di Flow Table:** quando un pacchetto entra in una porta, viene processato attraverso una catena (*pipeline*) di Flow Table in sequenza, dalla tabella 0 in poi. In ogni tabella si cerca un match con le regole installate dal controller:
- Se c'è un match → si esegue l'azione (forward, drop, modify, ecc.) e si passa alla tabella successiva o si finalizza.
- Se non c'è match → si applica la regola di *table-miss* (tipicamente: invia al controller per una decisione).

**Group Tables:** le Group Tables consentono azioni più complesse che non si possono esprimere con le semplici Flow Table: ad esempio la replica di un pacchetto su più porte (multicast/broadcast), il fast-failover (selezionare automaticamente una porta alternativa se quella principale è down), o il load balancing su un gruppo di porte.

**Control Channel:** è il canale sicuro (tipicamente TLS su TCP) attraverso cui lo switch OpenFlow comunica con il controller. Il canale usa il **protocollo OpenFlow** per scambiarsi tre tipi di messaggi:
- **Controller → Switch**: *Flow-Mod* (installa/modifica/cancella una flow entry), *Packet-Out* (invia un pacchetto da una porta specifica), *Stats-Request*.
- **Switch → Controller**: *Packet-In* (invia un pacchetto al controller quando non c'è match), *Flow-Removed* (notifica la scadenza di una entry), *Port-Status*, *Stats-Reply*.
- **Bidirezionali**: *Hello* (handshake iniziale), *Echo Request/Reply* (keepalive).

> [!note] Multi-controller
>
> Uno switch OpenFlow può connettersi a più controller per ridondanza: uno è il controller primario, gli altri sono di backup. Se il controller primario va offline, il backup prende il controllo senza interruzione del servizio.

---

## SDN Control Plane e Interazione con il Data Plane

![[exam_mod2_sdn_control_data_interaction.jpg]]

Questo schema mostra come il controller SDN interagisce concretamente con il data plane, evidenziando le due direzioni di comunicazione: **southbound** (controller → switch) e **northbound** (switch → controller).

**Il controller SDN mantiene internamente:**
- **Network graph**: un grafo della topologia completo, aggiornato in tempo reale. Ogni nodo è uno switch o un host, ogni arco è un link con la sua capacità.
- **Link-state info**: lo stato di ogni link (attivo/down, latenza, utilizzo) raccolto tramite LLDP o SNMP.
- **Host info**: la posizione di ogni host nella rete (a quale porta di quale switch è connesso).
- **Switch info**: le caratteristiche di ogni switch (numero di porte, OpenFlow version, capabilities).
- **Statistics**: contatori di pacchetti e byte per ogni flow entry, per traffic engineering e monitoring.
- **Flow tables**: le regole di forwarding da installare negli switch.

**Interfaccia verso le applicazioni (Northbound):**
- **RESTful API**: le applicazioni di rete (routing, load balancing, ACL) interrogano e modificano lo stato del controller tramite API REST.
- **Intent**: alcune implementazioni supportano un livello di astrazione più alto, dove le applicazioni esprimono "intenzioni" (es. "garantisci 10 Mbps di banda tra h1 e h2") che il controller traduce in flow rules.

**Interfaccia verso gli switch (Southbound):**
- **OpenFlow**: protocollo principale per installare le flow rule e ricevere packet-in dagli switch.
- **SNMP** (*Simple Network Management Protocol*): usato per raccogliere statistiche di gestione dagli switch (link status, error counters, ecc.) anche da switch non necessariamente OpenFlow.

### Topology Discovery con LLDP

La topology discovery in reti OpenFlow si basa sul **Link Layer Discovery Protocol (LLDP)**, standardizzato da IEEE nel 2005 e 2009. 

Il processo si svolge in quattro passi:
1. Il controller genera un **Packet-Out** per ogni porta attiva su ogni switch scoperto, incapsulando al suo interno un frame LLDP con il Chassis ID e il Port ID dello switch sorgente.
2. Quando uno switch OF riceve un messaggio Packet-Out con un frame LLDP, lo **forwarda** sulla porta specificata nel Port ID verso lo switch adiacente.
3. Lo switch adiacente, ricevendo il frame LLDP su una porta non di controllo, lo **incapsula in un Packet-In** indirizzato al controller, includendo i propri Switch ID e Port ID come metadata.
4. Il controller riceve il Packet-In ed **estrae le informazioni**: conosce ora lo Switch ID e Port ID del frame LLDP (mittente originale) e lo Switch ID e Port ID del Packet-In (ricevente). Da questi dati deduce che esiste un link tra quei due switch su quelle specifiche porte.
