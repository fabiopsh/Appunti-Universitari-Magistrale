# SDN Applications e P4 Language

Questa lezione affronta tre casi d'uso concreti dell'[[Lezione 15 - (Lab) SDN Architecture]]: il caso reale di **B4**, la rete WAN globale di Google; il linguaggio **P4** per la programmazione del data plane; e il paradigma del **Service Function Chaining**. Il filo conduttore è la progressione da una rete tradizionale — rigida, sovradimensionata, costosa — verso un'infrastruttura completamente programmabile, dove sia il piano di controllo che il piano dati sono definiti via software.

---

## B4 — La WAN Software-Defined di Google

### Il problema: WAN tradizionali e loro limiti

Le reti WAN tradizionali nascono attorno a un principio di conservatività: i link intercontinentali sono costosi, la perdita di pacchetti è inaccettabile, e dunque si impiegano router di fascia altissima con un significativo sovrapprovisionamento della capacità. Il risultato è che i link WAN vengono utilizzati mediamente al **30–40%** della loro capacità, richiedendo un overprovisioning di 2–3x. Questo approccio tende inoltre a trattare tutto il traffico allo stesso modo: tutte le applicazioni sono considerate ugualmente importanti, senza distinzione di priorità o sensibilità alla latenza.

Google si è trovata davanti a una proiezione di costo insostenibile: crescere seguendo il modello tradizionale significava pagare 2–3 volte il costo di una WAN pienamente utilizzata. La soluzione è stata ridisegnare completamente la rete inter-datacenter.

### Cos'è B4

**B4** è la rete WAN globale proprietaria di Google, che connette i suoi datacenter tra loro — non è la rete Internet-facing per il traffico degli utenti. Google gestisce in realtà due backbone separati: **B2**, che porta il traffico Internet verso gli utenti (e cresce alla velocità di Internet), e **B4**, che gestisce il traffico inter-datacenter (cresciuto di 10x in 3,5 anni al momento della pubblicazione del paper originale).

![Mappa della rete B4 — connessioni WAN tra i datacenter Google nel mondo](images/lezione-16-lab-sdn-applications-e-p4-language-img-01.jpg)
*Fig. — La rete B4 connette una dozzina di siti (datacenter) in tutto il mondo tramite link privati intercontinentali.*

![Crescita del traffico B4 nel tempo](images/lezione-16-lab-sdn-applications-e-p4-language-img-02.jpg)
*Fig. — Traffico B4 dal 2012 al 2015: crescita di 10x in 3.5 anni, con B4 che supera B2 per volume.*

### Caratteristiche del traffico B4

Il traffico che percorre B4 non è omogeneo. Le slide distinguono tre categorie principali, ordinate per sensibilità alla latenza e volume:

| Tipo di traffico | Volume | Sensibilità latenza | Priorità |
|---|---|---|---|
| Replicazione dati utente verso datacenter remoti | Basso | Alta | Alta |
| Accesso remoto a storage per computazione distribuita | Medio | Media | Media |
| Sincronizzazione di stato tra datacenter (bulk transfer) | Alto | Bassa | Bassa |

Questa eterogeneità è cruciale: il traffico di tipo 3 è elastico — tollera riduzioni temporanee di banda e persino fallimenti — e costituisce la maggior parte del volume. Questo rende B4 **adatto al traffic engineering aggressivo**: si può rimandare o rallentare il traffico a bassa priorità per fare spazio a quello critico.

> [!tip] L'insight chiave di B4
>
> Il traffico inter-datacenter è prevalentemente *bulk* ed *elastico*. A differenza del traffico utente, non ha bisogno di garanzie di bassa latenza costante. Questo apre la strada a ottimizzazioni aggressive della banda che sarebbero impossibili su una WAN tradizionale.

### Caratteristiche di progetto di B4

B4 si distingue dalla WAN tradizionale per quattro proprietà fondamentali.

La prima è la **domanda di banda elastica**: le applicazioni tollerano failure temporanei e riduzioni di banda, il che permette di ottimizzare l'utilizzo senza sacrificare l'esperienza utente.

La seconda è il **numero moderato di siti**: poche decine di siti significa che le tabelle di routing restano piccole e gestibili — non serve la scalabilità da centinaia di migliaia di rotte tipica di un router ISP.

La terza è il **controllo fine-grained delle applicazioni**: le applicazioni stesse comunicano le loro priorità e possono controllare i burst, eliminando la necessità di overprovisioning dei link.

La quarta è la **sensibilità al costo**: i link intercontinentali privati sono estremamente costosi e devono essere utilizzati al 100% della capacità disponibile. Non ci si può permettere il lusso del 30–40% di utilizzo tipico delle WAN tradizionali.

---

### Architettura SDN di B4

La transizione di Google verso SDN è avvenuta in tre stadi progressivi, che illustrano perfettamente la metodologia di migrazione graduale.

#### Stadio 1 — Rete di partenza

Nella configurazione iniziale, i *site* (nodi WAN) comunicano tra loro tramite protocolli distribuiti tradizionali: iBGP e ISIS per il routing interno ai siti, eBGP tra i siti. I *cluster* (reti datacenter) sono collegati ai siti tramite router BGP. Il controllo è interamente distribuito — nessun controller centralizzato.

![SDN Architecture Stage 1 — rete tradizionale distribuita](images/lezione-16-lab-sdn-applications-e-p4-language-img-03.jpg)
*Fig. — Stage 1: la rete di partenza, con controllo distribuito basato su BGP/ISIS. Un sito è un nodo WAN; un cluster è il dominio server collegato a quel nodo.*

#### Stadio 2 — Deployment parziale di OpenFlow

Nella fase intermedia, viene introdotto per alcuni switch il controller OpenFlow, affiancato da Quagga (il software di routing BGP/ISIS) e da un modulo "Glue" che coordina i due sistemi. Il consenso tra istanze ridondanti del controller è gestito tramite **Paxos**, garantendo fault tolerance. La rete è in uno stato ibrido: alcuni switch sono già controllati da OpenFlow, altri ancora dal piano di controllo distribuito tradizionale.

![SDN Architecture Stage 2 — deployment parziale di OpenFlow](images/lezione-16-lab-sdn-applications-e-p4-language-img-04.jpg)
*Fig. — Stage 2: deployment graduale. I Site Controllers con OpenFlow coesistono con i nodi di controllo tradizionale. Paxos garantisce la fault tolerance del controller.*

#### Stadio 3 — Architettura target

Nella configurazione finale, tutti gli switch sono controllati da OpenFlow. Viene aggiunto il **Central TE Server** (Traffic Engineering Server) come applicazione globale che ottimizza l'intera rete. Il layer di controllo è fisicamente distribuito ma logicamente centralizzato.

![SDN Architecture Stage 3 — architettura target con Central TE Server](images/lezione-16-lab-sdn-applications-e-p4-language-img-05.jpg)
*Fig. — Stage 3: rete target. Tutti i dispositivi sono controllati via OpenFlow. Il Central TE Server fornisce ottimizzazione globale del traffico.*

#### Integrazione con BGP e piano di controllo tradizionale

Anche nell'architettura finale, BGP non scompare completamente. Ogni cluster mantiene router BGP che si appoggiano agli switch B4 tramite eBGP. BGP viene mantenuto per due ragioni pratiche: la familiarità degli operatori con il protocollo (già in uso prima di SDN) e la necessità di un deployment graduale e reversibile. BGP gestisce la *raggiungibilità* (reachability), mentre il **traffic engineering** — ovvero la selezione dei percorsi e l'allocazione della banda — è delegato interamente al sistema centralizzato SDN.

![Architettura B4 completa con integrazione BGP e SDN](images/lezione-16-lab-sdn-applications-e-p4-language-img-06.jpg)
*Fig. — L'architettura completa: BGP per la raggiungibilità, TE Server centralizzato per l'ottimizzazione del traffico. Gateway, Site Controllers e Switch Hardware interagiscono tramite OpenFlow.*

> [!note] Perché mantenere BGP?
>
> BGP non è la scelta tecnicamente "più pulita" in un sistema SDN puro, ma è mantenuto per due motivi pragmatici: (1) gli operatori lo conoscono bene e lo usavano già prima di SDN, facilitando una transizione graduale; (2) permette un rollout incrementale — si può migrare un sito alla volta senza interrompere il servizio.

### Panoramica dell'architettura B4

L'architettura B4 si articola su tre layer sovrapposti.

Lo **Switch Hardware** è hardware custom di Google, progettato con silicio commodity ma senza software di controllo complesso. La riduzione del numero di siti elimina la necessità di grandi tabelle di forwarding; il controllo applicativo fine-grained riduce la necessità di grandi buffer.

Il **Control Layer** è composto da *Network Control Servers* (NCS) che ospitano sia gli **OpenFlow Controllers** (OFC) sia le **Network Control Applications** (NCA). Gli OFC mantengono lo stato della rete in base alle direttive delle NCA e agli eventi degli switch, e istruiscono gli switch ad aggiornare le tabelle di forwarding. Per la fault tolerance, un'istanza Paxos per sito elegge il controller primario tra più repliche fisiche su server differenti.

Il **Global Layer** contiene le applicazioni logicamente centralizzate: l'**SDN Gateway** e il **TE Server**. L'SDN Gateway astrae i dettagli di OpenFlow e dell'hardware degli switch per il TE Server — ogni sito B4 può avere centinaia di porte fisiche, ma il Gateway le aggrega in un'astrazione a livello di sito. Il TE Server opera su questa visione globale per calcolare path e allocazioni di banda.

---

### Traffic Engineering in B4

Il Traffic Engineering (TE) è il meccanismo attraverso cui B4 realizza l'utilizzo vicino al 100% dei link. L'obiettivo del TE Server è **condividere la banda tra applicazioni concorrenti**, possibilmente usando percorsi multipli.

![Architettura del Traffic Engineering in B4](images/lezione-16-lab-sdn-applications-e-p4-language-img-07.jpg)
*Fig. — Il TE Server riceve Flow Groups e funzioni di banda dal Bandwidth Enforcer, ottimizza e produce Tunnels/Tunnel Groups che vengono poi installati nella rete via SDN Gateway e OFC.*

Il TE Server lavora su due astrazioni principali.

In **input** riceve: (1) la *topologia di rete* come grafo di siti e connessioni sito-a-sito, che riduce enormemente la dimensione del problema rispetto a una topologia a livello di porta; (2) i *flow group* (FG), ciascuno definito come una tupla composta da sito sorgente, sito destinazione e classe QoS. Il TE non lavora a livello di singola applicazione — aggrega il traffico per sito e classe di servizio. Il **Bandwidth Enforcer** è un componente esterno che specifica le funzioni di banda per ogni applicazione, derivate da pesi statici configurati dall'amministratore.

In **output** produce: *Tunnel* — percorsi a livello di sito come sequenze di siti (es. A→B→C), implementati tramite IP-in-IP encapsulation — e *Tunnel Group* (TG), che mappano i flow group sui tunnel disponibili.

> [!definition] Tunnel in B4
>
> Un Tunnel rappresenta un percorso a livello di sito nella rete. È una sequenza di siti (es. Amsterdam → Frankfurt → Warsaw) implementata con incapsulamento IP-in-IP. Non coincide con un link fisico: può attraversare più switch e link interni a ogni sito.

I Tunnel Group e i relativi Tunnel e Flow Group vengono inviati dall'SDN Gateway agli OFC, che li installano negli switch via OpenFlow.

#### Forwarding Multipath

Per sfruttare pienamente la banda disponibile, B4 utilizza il **forwarding multipath**: un flusso destinato a una subnet può essere distribuito su più tunnel in parallelo. Lo switch usa una funzione di hash sugli header del pacchetto (modulo il numero di entry ACL) per distribuire equamente i flussi tra i tunnel disponibili, garantendo che pacchetti dello stesso flusso seguano lo stesso percorso (evitando riordinamento).

![Esempio di forwarding multipath in B4](images/lezione-16-lab-sdn-applications-e-p4-language-img-08.jpg)
*Fig. — Esempio di forwarding multipath: i flussi verso 9.0.0.0/24 vengono distribuiti equamente tra due tunnel tramite hash degli header del pacchetto.*

> [!abstract] Risultati di B4
>
> Grazie all'architettura SDN, Google ha raggiunto un utilizzo dei link vicino al **100%** per i carichi elastici — contro il 30–40% delle WAN tradizionali. Questo ha permesso di ridurre costi e complessità dell'infrastruttura, eliminando il sovrapprovisionamento da 2–3x. Ulteriori miglioramenti successivi hanno introdotto topologie gerarchiche e algoritmi TE decentralizzati per migliorare scalabilità e disponibilità.

---

## Verso un Data Plane Programmabile

### Limiti di OpenFlow

OpenFlow ha dimostrato il valore della separazione tra control plane e data plane, ma presenta limiti intrinseci al crescere delle esigenze. Il protocollo è nato semplice — circa 12 header field — ma la specifica è cresciuta fino a ~40 campi, aumentando la complessità. Soprattutto, i datacenter moderni richiedono nuove forme di encapsulamento dei pacchetti (VXLAN, NVGRE, ecc.) che OpenFlow non supporta in modo flessibile.

Il problema più profondo è concettuale: la vera programmabilità di rete richiederebbe la capacità di definire e modificare sia gli algoritmi del control plane sia quelli del **data plane**. Gli operatori di rete dovrebbero poter definire entrambi autonomamente, senza coinvolgere i progettisti originali dell'hardware. OpenFlow permette di *installare regole* nel data plane, ma non di *riprogrammare* il data plane stesso.

> [!tip] La distinzione cruciale
>
> OpenFlow controlla *cosa fanno* le tabelle di un data plane fisso. P4 permette di definire *come è fatto* il data plane stesso — quali header riconoscere, come processarli, quali azioni eseguire.

---

## P4 Language

### Cos'è P4

**P4** (*Programming Protocol-Independent Packet Processors*) è un linguaggio di programmazione *domain-specific* progettato per dispositivi di rete. Il suo nome cattura l'essenza del progetto: permette di programmare il processamento dei pacchetti in modo indipendente dal protocollo sottostante.

P4 estende il paradigma match-action introdotto da OpenFlow, ma lo porta a un livello superiore: invece di installare regole in tabelle predefinite dall'hardware, con P4 il programmatore **definisce le tabelle stesse**, i campi degli header da estrarre, le azioni possibili e il flusso di controllo tra le tabelle.

> [!definition] P4 — Proprietà fondamentali
>
> Un programma P4 descrive integralmente il comportamento atteso nel data plane:
> - **Headers**: tutti gli header dei pacchetti e i campi rilevanti per il matching
> - **Actions**: l'insieme di tutte le azioni possibili supportate dalle tabelle
> - **Tables**: l'insieme delle tabelle di matching e il flusso di controllo tra esse
>
> In aggiunta agli header standard, i progettisti di rete possono definire header per protocolli personalizzati.

P4 è stato concepito nel 2013 da un team accademico-industriale e presentato all'ACM SIGCOMM 2014. La standardizzazione è coordinata dal **P4 Language Consortium** (specifiche su `p4.org/specs`).

### Vantaggi e applicazioni di P4

P4 permette di **personalizzare il processamento dei pacchetti senza modifiche hardware**, accelerando drasticamente il ciclo di innovazione dei protocolli di rete. Le applicazioni principali includono: SDN avanzato, monitoring e telemetria di rete, implementazioni custom di sicurezza e firewall.

Il vantaggio competitivo rispetto all'approccio tradizionale è la separazione tra il *cosa* (il programma P4, scritto dall'utente) e il *come* (l'hardware o il compilatore, forniti dal vendor): lo stesso programma può essere compilato per switch P4, SmartNIC, o software su host.

### Compilazione e target P4

![Flusso di compilazione di un programma P4 verso il target](images/lezione-16-lab-sdn-applications-e-p4-language-img-09.jpg)
*Fig. — Il programmatore scrive un P4 Program; il compilatore vendor-specifico genera una configurazione del data plane e un'API per il control plane (P4Runtime).*

Un programma P4 viene scritto dal programmatore in termini dell'**Architecture Model** — una specifica astratta del target, fornita dal vendor. Il **compilatore P4**, anch'esso vendor-specifico, prende in input il programma e il modello architetturale e produce:

- Una **configurazione del data plane** che implementa la logica di forwarding descritta nel programma.
- Un'**API** per gestire lo stato degli oggetti del data plane dal control plane.

L'interazione a runtime tra control plane e data plane avviene tramite **P4Runtime**, una specifica standard per controllare gli elementi del data plane definiti da un programma P4. Il control plane popola le tabelle con le regole; quando arriva un match, l'azione selezionata viene eseguita con i parametri specificati dalla regola corrispondente.

I target supportati includono switch P4, SmartNIC e host software — la stessa logica di forwarding può essere eseguita su hardware diversissimi semplicemente ricompilando.

### Struttura di un programma P4

Un programma P4 è composto da tre componenti principali, che corrispondono alle tre fasi del ciclo di vita di un pacchetto nel data plane.

![Le tre componenti principali di un programma P4: Parser, Match-Action Pipeline, Deparser](images/lezione-16-lab-sdn-applications-e-p4-language-img-10.jpg)
*Fig. — Pipeline P4: il Parser estrae gli header (state machine), la Match-Action Pipeline applica le regole, il Deparser ricostruisce il pacchetto per il wire.*

#### Parser

Il **Parser** specifica come estrarre gli header dai pacchetti in ingresso. Usa una **macchina a stati** per mappare il flusso di byte in strutture header e metadata. Per esempio, si parte dallo stato `start`, si estrae l'header Ethernet, e in base al campo `eth_type` si transita allo stato `parse_ipv4` (per pacchetti IP) oppure si accetta direttamente il pacchetto.

```p4
header ethernet_t {
    bit<48> dst_addr;
    bit<48> src_addr;
    bit<16> eth_type;
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

parser MyParser(packet_in packet,
                out headers_t hdr,
                inout metadata_t meta) {

    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.eth_type) {
            0x0800: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition accept;
    }
}
```

Gli header vengono dichiarati con campi a larghezza fissa (es. `bit<48>` per un MAC address). La struttura `headers_t` li raggruppa in un unico oggetto che attraversa tutta la pipeline.

#### Match-Action Pipeline

Il programmatore definisce le **tabelle di matching** e la logica di processamento. Ogni tabella specifica i campi su cui fare match, le azioni possibili, e la dimensione massima. Quando un pacchetto arriva, viene confrontato con le regole della tabella (installate dal control plane); se trova un match, l'azione associata viene eseguita con i parametri specificati dalla regola.

> [!note] Differenza rispetto a OpenFlow
>
> In OpenFlow, le tabelle sono fisse nell'hardware: l'operatore può solo popolarle con regole. In P4, le tabelle stesse sono definite nel programma: il programmatore decide quante tabelle ci sono, su quali campi fare match, e quali azioni sono disponibili. Questo abilita protocolli completamente nuovi senza modificare l'hardware.

#### Deparser

Il **Deparser** specifica come ricostruire il pacchetto per l'output sul wire. Definisce l'ordine in cui gli header modificati vengono serializzati nel flusso di byte in uscita, permettendo anche di aggiungere o rimuovere header (es. per encapsulamento/decapsulamento).

> [!abstract] Sintesi del modello P4
>
> P4 porta la programmabilità al data plane con un modello coerente: Parser (deserializzazione) → Match-Action Pipeline (processamento) → Deparser (serializzazione). Il control plane (via P4Runtime) si occupa solo di popolare le tabelle; tutta la logica di parsing e azione è definita staticamente nel programma P4 e compilata nell'hardware.

---

## Service Function Chaining

### Il problema: comporre funzioni di rete

Le reti moderne non applicano ai pacchetti una singola trasformazione, ma una sequenza di elaborazioni: un pacchetto che entra da Internet può dover attraversare un firewall, un sistema di intrusion detection (IDS), e un load balancer prima di raggiungere il server applicativo. Ciascuna di queste elaborazioni è una **Network Function** — una capacità di processamento dei pacchetti fornita da un dispositivo di rete.

> [!definition] Service Function Chaining (SFC)
>
> Il **Service Function Chaining** è il paradigma per definire e gestire servizi di rete come catene ordinate di funzioni di rete. Una catena definisce come un flusso di traffico deve essere processato per raggiungere obiettivi di sicurezza, performance o QoS.
>
> Esempi di funzioni di rete: NAT, firewall, IDS, DNS, caching, DDoS protection, load balancer.

Nelle reti tradizionali, le service chain sono implementate topologicamente: i dispositivi fisici sono cablati in sequenza, e il traffico li attraversa nell'ordine fisico. Questo rende l'aggiornamento o il cambiamento delle chain estremamente rigido e costoso.

### SFC con SDN

![Service Function Chaining con SDN — flusso del traffico attraverso la catena](images/lezione-16-lab-sdn-applications-e-p4-language-img-11.jpg)
*Fig. — SDN permette la definizione dinamica di service chain: il traffico viene instradato dal Service Classifier attraverso le funzioni desiderate (Firewall, Antivirus, Video Optimizer, Parental Control) su una piattaforma NFV, senza richiedere ricablaggio fisico.*

SDN risolve il problema della rigidità. Con SDN, le service chain sono **definite programmaticamente**: il controller SDN configura le regole di forwarding affinché i pacchetti attraversino le funzioni desiderate nell'ordine corretto, indipendentemente dalla topologia fisica. Un **Service Classifier** identifica i flussi e li instrada sulla chain appropriata; alla fine della chain, un secondo classificatore rilascia il traffico verso la destinazione finale.

Questo approccio si integra naturalmente con la **Network Function Virtualization** (NFV): le funzioni di rete non devono essere implementate su hardware dedicato, ma possono girare come istanze software su una piattaforma NFV. SDN + NFV insieme abilitano chain completamente virtuali, modificabili in tempo reale senza intervento fisico.

> [!tip] SDN + NFV: perché si completano
>
> NFV virtualizza le funzioni di rete (le rende software). SDN controlla il forwarding e permette di comporre queste funzioni in catene dinamiche. Insieme, eliminano sia la dipendenza dall'hardware dedicato sia la rigidità topologica delle reti tradizionali.

---

## Sintesi

> [!abstract] Punti chiave della lezione
>
> Il routing tradizionale offre un controllo troppo grossolano: i pesi dei link e il forwarding destination-based non bastano per traffic engineering fine-grained e controllo delle policy.
>
> **B4** dimostra che SDN consente utilizzo vicino al 100% dei link WAN inter-datacenter, contro il 30–40% delle WAN tradizionali — abbattendo costi e complessità. L'architettura è fisicamente distribuita ma logicamente centralizzata, con un TE Server globale che ottimizza l'intera rete.
>
> **OpenFlow** è uno dei possibili meccanismi southbound di SDN — non è SDN stesso. I suoi limiti (data plane fisso, header predefiniti) hanno portato allo sviluppo di P4.
>
> **P4** estende la programmabilità al data plane: non solo installa regole, ma permette di definire il parser, le tabelle, le azioni e il deparser. Il risultato è un data plane completamente personalizzabile, compilato per hardware diversi tramite un compilatore vendor-specifico.
>
> **Service Function Chaining** con SDN permette di comporre funzioni di rete (firewall, IDS, load balancer...) in catene dinamiche, senza ricablaggio fisico — specialmente potente in combinazione con NFV.

> [!question] Possibili domande d'esame
>
> - Perché Google ha sviluppato B4? Quali sono i limiti delle WAN tradizionali che B4 risolve?
> - Descrivere le tre categorie di traffico in B4 e come influenzano le scelte di traffic engineering.
> - Descrivere i tre stadi di migrazione verso SDN in B4. Perché BGP è stato mantenuto?
> - Come funziona il TE Server di B4? Cosa sono i Flow Group, i Tunnel e i Tunnel Group?
> - Quali sono i limiti di OpenFlow che hanno motivato lo sviluppo di P4?
> - Cosa descrive un programma P4? Quali sono le sue tre componenti principali?
> - Come interagiscono control plane e data plane in un sistema P4?
> - Cos'è il Service Function Chaining? Come SDN abilita SFC dinamico?
