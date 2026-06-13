# 05 - Preparazione Esame Orale

Questo documento raccoglie le risposte complete a ciascuna delle immagini del documento *Questions for the oral exam 2023 — Module 2*. Per ogni schema viene prima descritta l'immagine, poi illustrato tutto ciò che va spiegato durante l'orale.

---

## Hidden Terminal (Terminale Nascosto)

![[Pasted image 20260429160400.png]]
### Descrizione dell'immagine

Lo schema mostra quattro nodi etichettati A, B, C, D disposti in fila orizzontale. Due cerchi tratteggiati di colore verde indicano i rispettivi raggi di copertura radio: il primo include A e B (con sovrapposizione al centro), il secondo include B e C. Il nodo D è fuori dalla portata di entrambi. Il nodo B è evidenziato (cerchio verde più spesso) perché è il ricevitore comune al centro della situazione.

### Cosa dire all'esame

Il problema del **terminale nascosto** nasce da una limitazione fisica fondamentale delle reti wireless: la potenza del segnale radio cala con il quadrato della distanza, e la comunicazione può avvenire solo tra nodi sufficientemente vicini. In questo scenario, A e C vogliono entrambi trasmettere a B, ma A e C si trovano fuori dal raggio radio l'uno dell'altro.

Supponiamo che A stia già trasmettendo verso B. La stazione C, prima di trasmettere, esegue il **Carrier Sense**: ascolta il canale per verificare se è libero. Poiché C non riesce a sentire il segnale di A (sono fuori portata), C conclude erroneamente che il canale sia libero e inizia a trasmettere verso B (o verso D). Il risultato è che i segnali di A e di C si sovrappongono fisicamente nell'antenna di B, generando una **collisione** che B riceve come segnale incomprensibile. Né A né C rilevano la collisione, perché ciascuna sente solo il proprio segnale (che è enormemente più forte di qualsiasi segnale di ritorno).

Questo è il motivo per cui il protocollo **CSMA/CD**, standard nelle reti Ethernet cablate, non può essere usato nelle reti wireless: il meccanismo di rilevamento delle collisioni richiede che il trasmettitore possa ascoltare il canale mentre trasmette, il che è impossibile in radio (il self-signal del trasmettitore è ordini di grandezza più forte di qualsiasi segnale debole in arrivo).

> [!tip] Il punto chiave
>
> Con CSMA classico, il Carrier Sense viene eseguito dal trasmettitore, ma quello che conta è lo stato del canale **al ricevitore**. Il terminale nascosto è "nascosto" solo rispetto al trasmettitore corrente, non rispetto al ricevitore.

La soluzione a questo problema è il meccanismo **RTS/CTS**, descritto nel terzo schema.

---

## Exposed Terminal (Terminale Esposto)

![[exam_mod2_exposed_terminal.jpg]]

### Descrizione dell'immagine

Lo schema mostra quattro nodi A, B, C, D in fila. A e D sono i nodi periferici (grigi, fuori dal raggio di copertura della coppia centrale). B e C si trovano al centro in sovrapposizione: il cerchio verde tratteggiato principale copre B e C (e parte di A), mentre un cerchio grigio parziale copre C e D. L'ellisse grigia al centro della figura evidenzia la zona di interferenza comune tra B e C.

### Cosa dire all'esame

Il problema del **terminale esposto** è speculare al precedente: questa volta, una stazione si astiene inutilmente dal trasmettere perché percepisce un segnale sul canale, anche se quel segnale non crea interferenza al suo ricevitore di destinazione.

In questo scenario, B sta trasmettendo verso A. Il nodo C vuole inviare un frame a D. Prima di trasmettere, C esegue il Carrier Sense e rileva il segnale di B (che è vicino a C): applica la regola del CSMA e conclude che il canale è occupato, rinviando la trasmissione. Ma questa decisione è sbagliata: se C trasmettesse verso D, il segnale di C raggiungerebbe D (che è fuori dalla portata di B), e le due comunicazioni — B→A e C→D — potrebbero avvenire perfettamente in parallelo senza interferirsi a vicenda.

C è chiamato **terminale esposto** alla trasmissione B→A: "esposto" nel senso che sente la trasmissione di B e ne è bloccato, pur non essendo in conflitto reale con essa. Il risultato è un inutile spreco di capacità: una comunicazione che potrebbe avvenire viene soppressa per un falso allarme.

> [!warning] Attenzione
>
> Il terminale esposto non è un problema di collisione, ma di **sotto-utilizzo del canale**. È meno grave del terminale nascosto (che causa corruzioni di dati), ma riduce il throughput complessivo della rete.

Il meccanismo RTS/CTS del protocollo MACA risolve anche questo problema, come illustrato nel terzo schema.

---

## RTS/CTS

![[exam_mod2_rts_cts.jpg]]

### Descrizione dell'immagine

Lo schema mostra cinque nodi: C, A, B, D in fila orizzontale, e E sotto la fila. Due grandi cerchi tratteggiati arancioni indicano i raggi di copertura: il primo centrato su A copre C, A, B, E; il secondo centrato su B copre A, B, D, E. La freccia arancione etichettata "RTS" va da A verso B. I nodi B e A sono evidenziati con cerchi arancioni doppi (sono gli attori principali). Il nodo E si trova nella sovrapposizione dei due cerchi.

### Cosa dire all'esame

Il meccanismo **RTS/CTS** (*Request To Send / Clear To Send*) è il cuore del protocollo **MACA** (*Multiple Access with Collision Avoidance*, 1990) e del successivo **MACAW**, ed è integrato nello standard **IEEE 802.11** (Wi-Fi). Risolve entrambi i problemi del terminale nascosto e del terminale esposto prenotando il canale in modo distribuito prima di trasmettere i dati.

Il funzionamento si articola in tre fasi:

**Fase 1 — RTS**: quando A vuole inviare dati a B, invia prima un breve pacchetto **RTS** (≈20 byte) che contiene: ID sorgente (A), ID destinazione (B), e la **durata** del frame dati che seguirà. Tutti i nodi nel raggio di A (ovvero C, B, E) ricevono questo RTS.

**Fase 2 — CTS**: se B è libero e pronto, risponde con un pacchetto **CTS** (anch'esso breve) che copia e ritrasmette la durata dichiarata dall'RTS. Tutti i nodi nel raggio di B (ovvero A, D, E) ricevono il CTS.

**Fase 3 — DATA**: ricevuto il CTS, A inizia la trasmissione del frame dati vero e proprio in condizioni sicure.

**Come risolve il terminale nascosto (D nel diagramma):** D non ha sentito l'RTS di A (troppo lontano), ma riceve il CTS di B e capisce che B è in procinto di ricevere dati. Quindi D si mette in silenzio per la durata indicata nel CTS, evitando di interferire con la ricezione di B.

**Come risolve il terminale esposto (C nel diagramma):** C sente l'RTS di A ma, essendo troppo lontano da B, non riceve il CTS di B. Da questo C deduce di essere un terminale esposto: la comunicazione avviene lontano dalla sua area di influenza, e può iniziare una propria trasmissione senza creare interferenze.

**Il caso E:** E si trova nella zona di sovrapposizione, sente sia l'RTS sia il CTS: sa con certezza di dover tacere per tutta la durata della comunicazione.

> [!tip] Collisioni residue
>
> Con RTS/CTS le collisioni non scompaiono del tutto: possono ancora avvenire tra pacchetti RTS (es. se C e D inviano contemporaneamente RTS verso A). Ma in tal caso nessun dato applicativo viene perso, e lo spreco di canale è minimo (RTS sono brevissimi). I mittenti applicano il **Binary Exponential Backoff** prima di riprovare.

In 802.11, l'impiego di RTS/CTS è configurabile tramite una soglia di dimensione (*RTS Threshold*): sempre, mai, o solo per frame sopra una certa dimensione.

---

## Mobile Networks — I

![[exam_mod2_mobile_networks_I.jpg]]

### Descrizione dell'immagine

Lo schema mostra un'architettura a tre attori principali. A sinistra, la **Home Network** (sfondo azzurro) con: un dispositivo mobile (smartphone), il Permanent IP 128.119.40.186, IMSI 78:4f:43:98:d9:27, il Home Subscriber Server, il Mobility Manager, e il Home network gateway. A destra, la **Visited Network** (sfondo azzurro) con: lo smartphone mobile (con NAT IP 10.0.0.99, stesso IMSI), il Mobility Manager, e il Visited network gateway. Al centro in basso c'è il **Correspondent** (laptop) connesso attraverso il public/private Internet. Le frecce mostrano connessioni tra Home gateway, Visited gateway e Correspondent, formando un triangolo di routing.

### Cosa dire all'esame

Questo schema illustra l'architettura del **routing indiretto** (*triangle routing*) nelle reti mobili 4G/5G, che è il meccanismo standard usato nelle reti LTE.

L'idea di base è che ogni utente mobile abbia una **home network**: la rete dell'operatore con cui ha sottoscritto il contratto (es. Verizon, TIM). Questa rete mantiene un database centralizzato, l'**Home Subscriber Server (HSS)**, che registra l'identità dell'utente (IMSI) e i servizi abilitati. Quando il dispositivo lascia la home network ed entra in una **visited network** (roaming), mantiene il suo indirizzo IP permanente (128.119.40.186) ma ottiene temporaneamente un indirizzo locale nella rete visitata (NAT IP: 10.0.0.99).

La **fase di registrazione** avviene così: il dispositivo si associa alla BS della rete visitata e si identifica tramite IMSI → il Mobility Manager della rete visitata contatta l'HSS della home network → l'HSS aggiorna la posizione del dispositivo e restituisce i parametri di autenticazione → da questo momento l'HSS sa dove si trova il dispositivo.

Nel **routing indiretto**, quando il Correspondent vuole inviare dati al dispositivo mobile:
1. Il Correspondent invia il pacchetto all'**indirizzo permanente** del mobile (128.119.40.186), che appartiene alla home network.
2. Il **Home network gateway** riceve il pacchetto, lo **incapsula** in un tunnel (tipicamente usando il protocollo GTP — *GPRS Tunneling Protocol*) e lo forwarda al Visited network gateway.
3. Il **Visited network gateway** decapsula il pacchetto, applica la traduzione **NAT** (perché il dispositivo ha un IP locale 10.0.0.99) e lo consegna al dispositivo.
4. Le risposte del dispositivo possono seguire il percorso inverso oppure essere inviate direttamente al Correspondent.

Il percorso forma un **triangolo**: Correspondent → Home → Visited → Mobile, anche se Correspondent e mobile fossero fisicamente vicini. Questo è il costo dell'approccio, ma il beneficio è che ogni cambio di rete visitata è **trasparente** per il Correspondent: la home network aggiorna silenziosamente l'endpoint del tunnel, senza che il Correspondent debba fare nulla.

---

## Mobile Networks — II

![[exam_mod2_mobile_networks_II.jpg]]

### Descrizione dell'immagine

Lo schema mostra la stessa architettura del precedente (Home Network con HSS, Mobility Manager, Home gateway; Visited Network con Mobility Manager, Visited gateway; Correspondent in basso), ma con un percorso di frecce diverso: il Correspondent sembra comunicare direttamente con il Visited network gateway, senza passare per il Home gateway.

### Cosa dire all'esame

Questo schema illustra il **routing diretto**, l'alternativa al triangle routing per le reti mobili.

Nel routing diretto, il Correspondent non invia i pacchetti all'indirizzo permanente del mobile, ma ottiene prima il suo **care-of address** nella rete visitata. La procedura è la seguente:

1. Il Correspondent interroga l'**HSS** della home network (tramite un protocollo apposito) per ottenere l'indirizzo corrente del dispositivo mobile nella rete visitata (il care-of address, es. 10.0.0.99).
2. Il Correspondent invia i pacchetti **direttamente** al care-of address nella visited network, bypassando la home network.
3. Il Visited network gateway riceve il pacchetto e lo consegna al dispositivo mobile.

**Vantaggi rispetto al routing indiretto:** il percorso è più corto (nessun triangolo), la latenza è ridotta, e non si sovraccarica inutilmente la home network.

**Svantaggi e problemi:** l'approccio **non è trasparente** per il Correspondent, che deve eseguire attivamente la query all'HSS. Inoltre, se il dispositivo cambia rete visitata durante una sessione attiva, il Correspondent ha interrogato l'HSS solo all'inizio della sessione e non conosce il nuovo care-of address: servono meccanismi aggiuntivi (es. forwarding dalla vecchia visited network alla nuova, o re-query dell'HSS). Nel routing indiretto, invece, è sufficiente aggiornare l'endpoint del tunnel lato home network.

> [!tip] Confronto diretto vs indiretto
>
> | Aspetto | Routing Indiretto | Routing Diretto |
> |---|---|---|
> | Percorso pacchetti | Triangolo (via home) | Diretto alla visited |
> | Trasparenza per Correspondent | Sì | No (deve interrogare HSS) |
> | Gestione cambio rete | Automatica (re-tunnel) | Complessa (deve aggiornare il Correspondent) |
> | Latenza | Maggiore (percorso più lungo) | Minore |
> | Adottato in LTE/4G | Sì (per default) | Solo con ottimizzazione esplicita |

---

## Mobile Networks — III

![[exam_mod2_mobile_networks_III.jpg]]

### Descrizione dell'immagine

Lo schema mostra l'architettura di una rete LTE durante un **handover** tra celle. Sono visibili: in alto a destra la **source BS** (Base Station sorgente, la torre radio da cui il dispositivo si sta spostando), in basso a destra la **target BS** (Base Station di destinazione, quella verso cui il dispositivo si sta muovendo). Al centro c'è l'**S-GW** (*Serving Gateway*), a sinistra il **P-GW** (*PDN Gateway*), e in basso al centro il **MME** (*Mobility Management Entity*). Le frecce indicano i percorsi di segnalazione e dati durante l'handover.

### Cosa dire all'esame

Questo schema mostra la procedura di **handover tra Base Station** in una rete 4G LTE, ovvero il meccanismo che consente a un dispositivo in movimento di passare da una cella all'altra senza perdere la connessione.

**Architettura del piano dati:** quando il dispositivo è associato a una BS, il traffico dati fluisce attraverso due tunnel GTP in cascata:
- **Tunnel BS ↔ S-GW**: connette la Base Station corrente al Serving Gateway.
- **Tunnel S-GW ↔ P-GW**: connette il Serving Gateway al PDN Gateway (il gateway verso Internet nella home network), realizzando il routing indiretto.

**Procedura di handover (7 passi):**

1. La **source BS** rileva il degrado del segnale (o il sovraccarico) e decide di avviare l'handover. Sceglie la **target BS** (sulla base delle misure di segnale riportate dal dispositivo) e le invia una **Handover Request**.
2. La **target BS** pre-alloca le risorse radio necessarie e risponde con un **Handover Request ACK** contenente i parametri di configurazione per il dispositivo.
3. La **source BS** notifica al dispositivo il cambio imminente; da questo momento il dispositivo può già trasmettere tramite la nuova BS — dal punto di vista del dispositivo l'handover è già avvenuto.
4. La **source BS** smette di trasmettere al dispositivo e inizia a **forwardare** i datagrammi in arrivo verso la target BS (che li recapita al dispositivo via radio).
5. La **target BS** informa l'**MME** di essere la nuova BS per il dispositivo.
6. L'**MME** istruisce lo **S-GW** di aggiornare l'endpoint del tunnel dati alla nuova target BS. La source BS riceve conferma e libera le risorse radio.
7. Il traffico fluisce ora attraverso il **nuovo tunnel** target BS ↔ S-GW, mentre il tunnel S-GW ↔ P-GW rimane invariato.

> [!tip] Chi decide l'handover?
>
> È un punto classico da esame: la **source BS** decide sia di avviare l'handover sia di scegliere la target BS — non l'MME. L'MME viene coinvolto solo nella fase finale per aggiornare il piano dati. Questo riflette la separazione tra control plane (MME gestisce la mobilità a livello di rete) e data plane (le BS gestiscono la qualità del segnale radio).

> [!note] Continuità delle sessioni TCP
>
> Durante l'handover possono andare persi alcuni datagrammi in transito. Tuttavia le sessioni TCP rimangono attive: dal punto di vista del Correspondent, la posizione del mobile è un dettaglio interno alla home network gestito trasparentemente dal meccanismo di tunneling.

---

## SDN — Generalized Forwarding

![[exam_mod2_sdn_generalized_forwarding.jpg]]

### Descrizione dell'immagine

Lo schema mostra la struttura di una **flow table entry** OpenFlow con tre colonne: **Match** (a sinistra, punteggiata), **Action** (al centro, che elenca 4 azioni possibili), **Stats** (a destra, che mostra "Packet + byte counters"). Nella sezione Action si legge: 1. Forward packet to port(s), 2. Drop packet, 3. Modify fields in header(s), 4. Encapsulate and forward to controller. Nella parte inferiore, una riga mostra i campi dell'header su cui si fa il match: Ingress Port, Src MAC, Dst MAC, Eth Type, VLAN ID, VLAN Pri, IP Src, IP Dst, IP Proto, IP ToS, TCP/UDP Src Port, TCP/UDP Dst Port.

### Cosa dire all'esame

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

## SDN — Example

![[exam_mod2_sdn_example.jpg]]

### Descrizione dell'immagine

Lo schema mostra una topologia di rete con tre switch SDN (s1, s2, s3) e sei host: h1 (10.1.0.1), h2 (10.1.0.2), h3 (10.2.0.3), h4 (10.2.0.4), h5 (10.3.0.5), h6 (10.3.0.6). S1 è connesso a h1, h2, s2 e s3. S2 è connesso a s1, h3, h4. S3 è connesso a s1, h5, h6. Un **OpenFlow controller** è connesso a s3 (e tramite essa all'intera rete). Ogni porta degli switch è numerata.

### Cosa dire all'esame

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

## SDN — Architecture

![[exam_mod2_sdn_architecture.jpg]]

### Descrizione dell'immagine

Lo schema mostra l'architettura SDN a tre livelli sovrapposti. Il livello superiore è l'**Application Plane** con tre categorie di applicazioni: Network Apps, Security Apps, Business Apps. Il livello centrale è il **Control Plane** con tre SDN controller connessi orizzontalmente tramite **Westbound API** e **Eastbound API**. Il livello inferiore è il **Data Plane** con virtual switches (a sinistra, su hypervisor/hardware) e physical switches (a destra). Tra Application Plane e Control Plane c'è una freccia bidirezionale (Northbound API); tra Control Plane e Data Plane c'è un'altra freccia bidirezionale (Southbound API).

### Cosa dire all'esame

Questo schema illustra l'**architettura a tre livelli di SDN**, che realizza la separazione netta tra data plane, control plane e application plane.

**Data Plane (Livello inferiore):** contiene gli switch del data plane, che possono essere sia fisici (hardware commodity a basso costo) sia virtuali (Open vSwitch su hypervisor). Sono dispositivi semplici: il loro unico compito è applicare meccanicamente le regole di forwarding (match-action) ai pacchetti in transito secondo le flow table installate dal controller. Non calcolano nulla autonomamente.

**Control Plane (Livello centrale):** contiene il controller SDN, o meglio una **rete di controller SDN** distribuiti. Sebbene appaia come un'entità logicamente centralizzata (ha una visione globale della rete), è implementato fisicamente come sistema distribuito per garantire tolleranza ai guasti e scalabilità. Il controller mantiene: la topologia della rete, le statistiche dei flussi, i link attivi, le tabelle di forwarding. Comunica verso il basso con il Data Plane tramite la **Southbound API** (tipicamente OpenFlow), e verso l'alto con le applicazioni tramite la **Northbound API**. I controller comunicano tra loro tramite **Westbound/Eastbound API** per sincronizzare lo stato globale.

**Application Plane (Livello superiore):** contiene le applicazioni di controllo della rete (*network-control applications*), il vero "cervello" del sistema. Sono **unbundled**: possono essere sviluppate da terze parti indipendentemente dai produttori hardware e software del controller. Esempi: load balancer, firewall, traffic engineering, monitoraggio, rilevamento anomalie. Le applicazioni esprimono policy di alto livello al controller tramite la Northbound API.

> [!note] Il valore dell'architettura a livelli
>
> La separazione in tre piani replica il principio dei livelli di astrazione di Internet. Ogni livello si può evolvere indipendentemente: nuovi algoritmi di routing nel Control Plane, nuove applicazioni nell'Application Plane, nuovo hardware nel Data Plane — senza impatto sugli altri livelli. Questo è il vantaggio principale rispetto alle reti tradizionali con logica chiusa nell'hardware proprietario.

---

## OpenFlow Switch

![[exam_mod2_openflow_switch.jpg]]

### Descrizione dell'immagine

Lo schema mostra l'architettura interna di un **OpenFlow Switch**. A sinistra e a destra ci sono i **Data packet flows** (TCP/IP o UDP/IP). All'interno dello switch sono evidenziate due aree: il **Datapath** (in alto, che contiene Group Tables) e il **Pipeline** (in basso, che contiene una catena di Flow Tables). Il **Control Channel** (area centrale) ospita due **OpenFlow Channels** connessi ai rispettivi Controller (in alto). Le porte (Port) connettono l'esterno al pipeline interno.

### Cosa dire all'esame

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
> Lo schema mostra due controller connessi tramite due OpenFlow Channel separati. Uno switch OpenFlow può connettersi a più controller per ridondanza: uno è il controller primario, gli altri sono di backup. Se il controller primario va offline, il backup prende il controllo senza interruzione del servizio.

---

## SDN — Control/Data Plane Interaction Example

![[exam_mod2_sdn_control_data_interaction.jpg]]

### Descrizione dell'immagine

Lo schema è diviso in due parti da una linea tratteggiata. In alto, il **Control Plane** (rettangolo bianco) con i componenti: network graph, RESTful API, intent, statistics, flow tables, Link-state info, host info, switch info, e due protocolli di southbound: **OpenFlow** e **SNMP**. In basso, il **Data Plane** (sfondo azzurro) con quattro switch (s1, s2, s3, s4) interconnessi.

### Cosa dire all'esame

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

---

## NFV — Forwarding Graph

![[exam_mod2_nfv_forwarding_graph.jpg]]

### Descrizione dell'immagine

Lo schema mostra un servizio di rete end-to-end tra **End Point A** (a sinistra) e **End Point B** (a destra). Il servizio è composto da: **VNF-1** (in basso a sinistra), il sotto-grafo **VNF-FG-2** (nel riquadro centrale, composto da VNF-2A, VNF-2B e VNF-2C), e **VNF-3** (in alto a destra). I link logici (frecce tratteggiate) indicano la catena di forwarding. In basso, tre **NFVI-PoP** (punti di presenza dell'infrastruttura NFV) sono connessi tramite physical links. Una **Virtualization Layer** separa il livello logico dal livello fisico.

### Cosa dire all'esame

Questo schema rappresenta il concetto di **VNF Forwarding Graph** (VNF-FG), che è il modo in cui NFV formalizza un servizio di rete end-to-end.

**L'idea fondamentale di NFV:** invece di implementare funzioni di rete (firewall, NAT, load balancer, media gateway) in hardware proprietario dedicato, NFV le implementa come software — chiamate **VNF** (*Virtualized Network Functions*) — eseguito su infrastruttura hardware commodity (server COTS). Il decoupling tra funzione e hardware porta flessibilità, scalabilità e riduzione dei costi.

**Il Forwarding Graph:** un servizio di rete non è una singola funzione, ma una **composizione di funzioni** applicate in sequenza al traffico. Il grafo mostra:
- Il traffico entra da **End Point A**, passa attraverso **VNF-1**, poi attraverso il sotto-grafo **VNF-FG-2** (che a sua volta compone internamente VNF-2A → VNF-2B e VNF-2C in parallelo), poi attraverso **VNF-3**, e infine raggiunge **End Point B**.
- I link logici (tratteggiati) rappresentano connettività virtuale: due VNF sono logicamente connesse, ma possono fisicamente trovarsi su macchine diverse.

**I grafi sono nidificati:** VNF-FG-2 è esso stesso un sotto-grafo all'interno del grafo principale. Questo consente la riusabilità: VNF-FG-2 può essere istanziato in altri servizi senza ridefinirlo.

**L'infrastruttura fisica (NFVI):** le VNF girano su nodi fisici chiamati **NFVI-PoP** (*Network Function Virtualization Infrastructure Point of Presence*). Sono server COTS distribuiti geograficamente, interconnessi da una rete di trasporto fisica. La **Virtualization Layer** (hypervisor o container engine) astrae le risorse fisiche e consente a più VNF di condividere lo stesso hardware.

**Il problema del VNF placement:** dato il grafo logico del servizio, occorre decidere dove deployare fisicamente ogni VNF nell'infrastruttura. Questo è un problema di ottimizzazione NP-hard che considera: latenza end-to-end, capacità dei nodi, banda dei link, costi di deployment, requisiti di QoS per ogni slice di rete.

---

## NFV — Management and Orchestration

![[exam_mod2_nfv_mano.jpg]]

### Descrizione dell'immagine

Lo schema mostra il framework **NFV MANO** (*Management and Orchestration*) secondo ETSI. Al livello superiore c'è il blocco **NFV Management and Orchestration (MANO)** che contiene: l'**NFV Orchestrator (NFVO)** in cima (con NS catalog e VNF catalog), connesso tramite l'interfaccia **Or-Vnfm** al **VNF Manager (VNFM)**, che a sua volta è connesso tramite **VI-Vnfm** al **Virtualized Infrastructure Manager (VIM)**. Il VIM è connesso all'**NFVI** (l'infrastruttura virtuale) tramite l'interfaccia **Nf-Vi** e all'**Or-Vi** direttamente dall'NFVO. L'interfaccia **S-Ma** connette un sistema esterno (OSS/BSS) all'NFVO.

### Cosa dire all'esame

Questo schema mostra il framework di **gestione e orchestrazione NFV** standardizzato da ETSI, che è il "piano di controllo" dell'ecosistema NFV.

**NFV Orchestrator (NFVO):** è il componente di più alto livello. Ha due responsabilità principali:
1. **Network services orchestration**: gestisce il ciclo di vita dei **Network Service (NS)** end-to-end, ovvero istanzia, aggiorna e termina l'intero VNF Forwarding Graph. Può istanziare nuovi VNFM se necessario.
2. **Resource orchestration**: gestisce le risorse globali dell'NFVI, allocandole ai servizi in base alle policy e ai requisiti di QoS.
Il NFVO mantiene due repository: il **NS Catalog** (template dei servizi di rete come Network Service Descriptor) e il **VNF Catalog** (descrittori di ogni VNF, i VNFD).

**VNF Manager (VNFM):** gestisce il **ciclo di vita delle istanze VNF** singole:
- **Istanziazione**: crea una nuova istanza VNF su una VM o container nell'NFVI.
- **Scaling**: aumenta o riduce la capacità di una VNF (scaling out/in orizzontale, scaling up/down verticale) in base al carico.
- **Healing**: rileva e gestisce i fault delle VNF (auto-healing o assistito).
- **Terminazione**: distrugge l'istanza quando non serve più.
Il VNFM comunica con il NFVO tramite **Or-Vnfm** e con il VIM tramite **Vi-Vnfm** (o **Ve-Vnfm** verso le VNF stesse).

**Virtualized Infrastructure Manager (VIM):** controlla e gestisce le risorse fisiche e virtuali dell'NFVI (compute, storage, network). Piattaforme IaaS come **OpenStack** fungono da VIM. Il VIM alloca VM o container alle VNF, configura la rete virtuale (vSwitch, VLAN), e monitora l'utilizzo delle risorse. Un MANO può orchestrare più VIM distribuiti geograficamente.

**Le interfacce di riferimento:**
- **Or-Vi** (NFVO → VIM): l'orchestratore può richiedere risorse direttamente al VIM.
- **S-Ma**: collega sistemi OSS/BSS dell'operatore (Operations Support System / Business Support System) al MANO per l'integrazione con i sistemi aziendali.

> [!note] Implementazioni open source
>
> Le principali implementazioni open source del MANO sono **OSM** (*Open Source MANO*, promossa da ETSI) e **ONAP** (*Open Network Automation Platform*, Linux Foundation). Entrambe sono usate nelle reti 5G commerciali.

---

## Network Slicing

![[exam_mod2_network_slicing.jpg]]

### Descrizione dell'immagine

Lo schema è composto da due parti. In alto, la topologia di rete: quattro switch (s1 dpid:1, s2 dpid:2, s3 dpid:3, s4 dpid:4) interconnessi, con quattro host (h1 IP:10.0.0.1, h2 IP:10.0.0.2, h3 IP:10.0.0.3, h4 IP:10.0.0.4). Una linea tratteggiata superiore indica l'**Upper Slice** (che attraversa s1-eth1 → s4-eth1), e una linea tratteggiata inferiore indica la **Lower Slice** (che attraversa s1-eth2 → s4-eth2). S2 ha capacità 10 Mbps, s1 e s4 hanno 1 Mbps. In basso, codice Python che implementa il controller Ryu per lo slicing, con un dizionario `slice_to_port` che mappa (dpid, in_port) → out_port.

### Cosa dire all'esame

Questo schema mostra l'implementazione pratica del **Network Slicing** tramite SDN con il controller **Ryu** (scritto in Python), uno dei casi d'uso più importanti di SDN e NFV nel contesto del 5G.

**Cosa è il Network Slicing:** la possibilità di creare su una stessa infrastruttura fisica **reti logicamente separate** (*slice*), ciascuna con le proprie caratteristiche di QoS, banda, latenza e isolamento. In questo esempio, sulla stessa topologia fisica (s1-s2-s4 e s1-s3-s4) vengono create due slice indipendenti:
- **Upper Slice**: usa il percorso s1(eth1) → s2 → s4(eth1), con capacità 10 Mbps (il link via s2 ha banda più alta).
- **Lower Slice**: usa il percorso s1(eth2) → s3 → s4(eth2), con capacità 1 Mbps.

**Il codice Python — TrafficSlicing:** il dizionario `slice_to_port` è il cuore dell'implementazione. Per ogni switch (dpid) e per ogni porta di ingresso (in_port), specifica la porta di uscita:
```python
self.slice_to_port = {
    1: {1: 3, 3: 1, 2: 4, 4: 2},  # switch s1 (dpid=1)
    4: {1: 3, 3: 1, 2: 4, 4: 2},  # switch s4 (dpid=4)
    2: {1: 2, 2: 1},               # switch s2 (dpid=2)
    3: {1: 2, 2: 1},               # switch s3 (dpid=3)
}
```
Il gestore `_packet_in_handler` è chiamato dal controller Ryu ogni volta che uno switch riceve un pacchetto che non ha una flow entry corrispondente (*packet-in*). Il controller legge il dpid dello switch e la porta di ingresso, cerca nel dizionario la porta di uscita, installa una **flow rule** nello switch (con `self.add_flow(datapath, 1, match, actions)`) e forwarda il pacchetto.

**Il ruolo di SDN nel Network Slicing:** senza SDN, separare il traffico richiederebbe VLAN, configurazione manuale di ogni switch, o hardware dedicato per ogni slice. Con SDN, è sufficiente un controller centralizzato che installa le regole di forwarding appropriate per ogni flusso, realizzando lo slicing in software.

> [!tip] Rilevanza nel 5G
>
> Il Network Slicing è uno dei pilastri del 5G: slice diverse possono essere dedicate a eMBB (enhanced Mobile Broadband, alta banda), URLLC (Ultra-Reliable Low-Latency Communications, bassa latenza per applicazioni critiche) e mMTC (massive Machine Type Communications, IoT a bassa potenza). La separazione logica garantisce che i requisiti di QoS di una slice non vengano degradati dalle altre.

---

## Fourier Series (Serie di Fourier)

![[exam_mod2_fourier_series.jpg]]

### Descrizione dell'immagine

Lo schema mostra: in alto a sinistra, la formula matematica della serie di Fourier $\frac{1}{2}a_0 + \sum_{n=1}^{\infty}(a_n \cos nt + b_n \sin nt)$ con i termini $a_n \cos nt$ e $b_n \sin nt$ evidenziati. A sinistra, cinque segnali sovrapposti: $s_0(t)$ (segnale continuo, linea piatta), $s_1(t)$ (fondamentale, ampiezza 1), $s_2(t)$ (prima armonica, ampiezza 1), $s_3(t)$ (seconda armonica, ampiezza 1), $s_4(t)$ (terza armonica, ampiezza 1), con la legenda "–k –sin a –sin 2a –sin 3a –sin 4a". A destra, il segnale $s(t)$ risultante dalla loro somma, che mostra una forma d'onda composta.

### Cosa dire all'esame

Questo schema illustra il concetto fondamentale della **Serie di Fourier**: qualsiasi segnale periodico può essere decomposto in una somma (infinita) di funzioni sinusoidali a frequenze multiple della frequenza fondamentale.

**La formula:**
$$s(t) = \frac{1}{2}a_0 + \sum_{n=1}^{\infty}\left(a_n \cos(nt) + b_n \sin(nt)\right)$$

dove i coefficienti si calcolano come:
$$a_0 = \frac{1}{\pi}\int_{-\pi}^{\pi} s(t)\,dt \qquad a_n = \frac{1}{\pi}\int_{-\pi}^{\pi} s(t)\cos(nt)\,dt \qquad b_n = \frac{1}{\pi}\int_{-\pi}^{\pi} s(t)\sin(nt)\,dt$$

**Interpretazione fisica:** ogni segnale periodico è la "somma di sinusoidi". Il termine $\frac{1}{2}a_0$ è la **componente continua** (il valor medio del segnale, $s_0$ nel diagramma). I termini successivi sono le **armoniche**: $s_1$ è la **fondamentale** con frequenza $f_0 = 1/T$, $s_2$ è la **prima armonica** con frequenza $f_1 = 2/T = 2f_0$, $s_3$ la seconda armonica a $3f_0$, $s_4$ la terza armonica a $4f_0$, e così via.

**Il significato pratico per le reti:** il canale trasmissivo non tratta tutte le frequenze allo stesso modo: alcune le attenua più di altre. Sapere quali frequenze compongono un segnale — cioè conoscere il suo **spettro** — permette di:
- Predire come il segnale si deformerà attraverso il canale.
- Dimensionare la **banda** necessaria (quante armoniche servono per rappresentare il segnale fedelmente).
- Progettare filtri per rimuovere componenti indesiderate.

**Le condizioni di Dirichlet** garantiscono l'esistenza della serie: è sufficiente che il segnale sia *piecewise continuous* (composto da un numero finito di pezzi continui con limite finito nei punti di discontinuità). In corrispondenza delle discontinuità la serie converge alla media dei limiti sinistro e destro.

> [!warning] Fenomeno di Gibbs
>
> Quando la serie di Fourier approssima un segnale con discontinuità (es. onda quadra), si osserva un *overshoot* del ≈9% dell'ampiezza del salto che non scompare mai, per quanto si aumenti il numero di armoniche. Le oscillazioni nel tratto piatto si riducono, ma il picco al salto rimane costante.

---

## DFT (Discrete Fourier Transform)

### Descrizione dell'immagine

Lo schema mostra la formula della **DFT** (*Discrete Fourier Transform*):
$$S_f = \sum_{n=0}^{N-1} s_n \, e^{-j\frac{2\pi f}{N}n} \quad \text{with } f = 0, 1, \ldots, N-1$$

### Cosa dire all'esame

La **Trasformata di Fourier Discreta** (DFT) è la versione *calcolabile da un computer* dell'analisi di Fourier: opera su un segnale discreto di lunghezza finita $N$ e produce $N$ coefficienti frequenziali.

**La formula:** dato un segnale campionato $s_n$ (con $n = 0, 1, \ldots, N-1$), la DFT calcola il coefficiente $S_f$ per ogni frequenza discreta $f = 0, 1, \ldots, N-1$:
$$S_f = \sum_{n=0}^{N-1} s_n \, e^{-j\frac{2\pi f}{N}n}$$

**Interpretazione:**
- Ogni coefficiente $S_f$ è un numero complesso: il suo **modulo** $|S_f|$ è l'ampiezza del contributo alla frequenza $f$, la sua **fase** $\arg(S_f)$ è lo sfasamento della componente sinusoidale corrispondente.
- Le frequenze reali rappresentate sono $f_k = k \cdot \frac{f_c}{N}$, dove $f_c$ è la frequenza di campionamento.

**Relazione con la Serie di Fourier:** la DFT è il corrispettivo discreto della serie di Fourier: la serie opera su segnali periodici continui e produce coefficienti $S_n$, la DFT opera su sequenze finite discrete e produce $N$ coefficienti $S_f$. La DFT assume implicitamente che il segnale di $N$ campioni sia la ripetizione periodica di un pattern.

**L'algoritmo FFT:** il calcolo diretto della DFT ha complessità $O(N^2)$ (ogni $S_f$ richiede $N$ moltiplicazioni e addizioni complesse). L'algoritmo **FFT** (*Fast Fourier Transform*), sviluppato da Cooley e Tukey nel 1965, riduce la complessità a $O(N \log N)$ sfruttando la simmetria del fattore $e^{-j\frac{2\pi f}{N}n}$. Per $N = 1024$ punti, la FFT è ≈100 volte più veloce della DFT diretta.

**Applicazioni pratiche:**
- **Analisi spettrale** di segnali acquisiti (ECG, audio, sismici).
- **OFDM** (*Orthogonal Frequency Division Multiplexing*): il segnale 4G/5G è creato con una IFFT e demodulato con una FFT, permettendo di trasmettere dati su migliaia di sottoportanti ortogonali simultaneamente.
- Filtraggio digitale e compressione (JPEG usa la DCT, variante della DFT).

---

## Sampling and Aliasing (Campionamento e Aliasing)

![[exam_mod2_sampling_aliasing.jpg]]

### Descrizione dell'immagine

Lo schema mostra un grafico con tre segnali sovrapposti nell'asse tempo (da 0 a 20) e ampiezza (da -1 a 1). Il segnale **rosso** è ad alta frequenza (molti cicli nel grafico). Il segnale **blu** è a bassa frequenza (pochi cicli). Il segnale **verde** è un'involucro che segna lentamente. Due **punti neri** evidenziano due istanti di campionamento: in quei punti, segnale rosso e segnale blu hanno **esattamente lo stesso valore**. I punti neri sono al valore ≈0.5 a t≈0 e a t≈15.

### Cosa dire all'esame

Questo schema illustra il **problema dell'aliasing**, uno dei fenomeni più importanti nella teoria del campionamento digitale.

**Il campionamento:** convertire un segnale analogico continuo in una sequenza discreta $s_n = s(nT_c)$ significa prelevare il valore del segnale a intervalli regolari di periodo $T_c = 1/f_c$ (frequenza di campionamento). Ma campionare introduce un'ambiguità: da un insieme finito di campioni non si può distinguere univocamente quale segnale li ha generati.

**L'aliasing:** il segnale rosso (alta frequenza $f_h$) e il segnale blu (bassa frequenza $f_l$) producono **identici campioni** (i punti neri). Se si guardano solo i campioni, è impossibile capire se il segnale originale era quello rosso o quello blu. Il segnale a bassa frequenza è l'**alias** di quello ad alta frequenza: un'identità fantasma creata dal sottocampionamento.

**Il Teorema di Nyquist-Shannon:** affinché un segnale di banda $B$ (frequenza massima $f_{max}$) sia ricostruito perfettamente dai suoi campioni, la frequenza di campionamento deve soddisfare:
$$f_c \geq 2 \cdot f_{max}$$

La frequenza $f_{Nyquist} = f_c/2$ è la massima frequenza rappresentabile senza aliasing. Se nel segnale originale sono presenti frequenze superiori a $f_{Nyquist}$, queste appaiono come frequenze più basse nello spettro discreto — l'aliasing appunto.

**Come prevenire l'aliasing:** si applica un **filtro anti-aliasing** (filtro passa-basso analogico) prima del campionatore, che elimina tutte le componenti con $f > f_c/2$. Solo dopo si campiona. Questo garantisce che il segnale digitale rappresenti fedelmente l'originale entro la banda di interesse.

**Applicazioni:**
- Audio CD: frequenza di campionamento 44.1 kHz → rappresenta fedelmente frequenze fino a 22.05 kHz (limite dell'udito umano ≈20 kHz).
- Telefonia: 8 kHz (voce fino a 4 kHz).
- WiFi e reti cellulari: i ricevitori devono campionare il segnale RF ad almeno $2 \times B_{canale}$.

---

## Quantization (Quantizzazione)

![[exam_mod2_quantization.jpg]]

### Descrizione dell'immagine

Lo schema mostra tre grafici verticalmente sovrapposti, tutti con asse x da -2 a 2 e asse y da -15 a 15. Il grafico superiore mostra il **segnale analogico $s(t)$** continuo e fluido. Il grafico centrale mostra il **segnale quantizzato** come approssimazione a gradini del segnale originale (ogni campione viene arrotondato al livello discreto più vicino). Il grafico inferiore mostra l'**errore di quantizzazione** $s(t) - y_k$: la differenza tra segnale originale e quantizzato, che appare come un segnale oscillante ad alta frequenza di piccola ampiezza.

### Cosa dire all'esame

Questo schema illustra la **quantizzazione**, il secondo passo nella conversione analogico-digitale (il primo è il campionamento). Dopo aver campionato il segnale nel tempo, ogni campione deve essere rappresentato con un numero finito di bit, cioè deve essere approssimato al livello discreto più vicino tra un insieme finito di valori possibili.

**Il processo:** dato un campione $s(nT_c)$ con valore reale, si sceglie il **livello di quantizzazione** $y_k$ più vicino e si assegna il codice binario corrispondente. Se si usano $M$ bit per campione, si hanno $2^M$ livelli di quantizzazione, spaziati di un passo $\Delta = \frac{s_{max} - s_{min}}{2^M}$.

**L'errore di quantizzazione:** l'approssimazione introduce un errore $e = s(t) - y_k$, che ha valore assoluto al massimo $\Delta/2$. Questo errore è inevitabile: è il prezzo del passaggio dal continuo al discreto. Nel grafico in basso si vede chiaramente: l'errore è un segnale oscillante (dovuto all'arrotondamento al gradino) con ampiezza piccola (≈$\Delta/2$) e frequenza elevata.

**Trade-off:**
- Aumentare $M$ (più bit per campione) riduce $\Delta$ e quindi l'errore di quantizzazione, ma aumenta il **bitrate** richiesto: $\text{Bitrate} = f_c \times M$ bit/s.
- Il **SNR di quantizzazione** cresce approssimativamente di 6 dB per ogni bit aggiunto: $\text{SNR}_{dB} \approx 6.02 \cdot M + 1.76$ dB.

**Applicazioni:**
- **Audio CD**: 16 bit per campione → 96 dB di range dinamico (65536 livelli).
- **Telefonia**: 8 bit (companding μ-law/A-law) → 256 livelli, ma compressione logaritmica per migliorare la qualità percepita a basse ampiezze.
- **Sensori IoT**: 12 bit ADC tipici per temperatura, pressione, accelerometro.

> [!note] Errore di quantizzazione come rumore
>
> Nell'analisi statistica, l'errore di quantizzazione viene modellato come **rumore bianco** uniforme nell'intervallo $[-\Delta/2, +\Delta/2]$ quando il segnale è molto più grande di $\Delta$ (assunzione di piccolo passo di quantizzazione). Questo consente di applicare la teoria del rumore per dimensionare il sistema: il SNR post-quantizzazione deve superare una soglia minima per garantire la qualità del servizio.

> [!abstract] Sintesi — Pipeline di digitalizzazione
>
> Il percorso completo dalla sorgente analogica al digitale è:
> 1. **Filtraggio anti-aliasing** (passa-basso, $f_{taglio} = f_c/2$) → elimina le frequenze che causerebbero aliasing.
> 2. **Campionamento** a $f_c \geq 2 f_{max}$ → sequenza discreta nel tempo.
> 3. **Quantizzazione** con $M$ bit → sequenza digitale.
> 4. **Codifica** binaria → bitstream trasmissibile.
> Il bitrate risultante è $f_c \times M$ bit/s, e deve rientrare nella capacità del canale $C = B \log_2(1 + \text{SNR})$ per garantire la trasmissione senza errori.
