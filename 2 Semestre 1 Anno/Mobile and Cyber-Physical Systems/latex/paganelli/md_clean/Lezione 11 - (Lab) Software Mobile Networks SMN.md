
# Software Defined Networking (SDN)

Questo paradigma architetturale segna il definitivo passaggio da un sistema di protocolli puramente distribuiti a un framework di controllo di rete completamente programmabile.

> [!definition] Software Defined Networking
>
> Il **Software Defined Networking** è un approccio alla gestione delle reti che sfrutta potenti meccanismi di astrazione per abilitare configurazioni e operazioni dinamiche ed efficienti a livello programmatico. La caratteristica distintiva è la separazione netta tra **control plane** e **data plane**.

---

## L'Evoluzione dei Requisiti e la Complessità del Traffico

Sebbene il SDN sia spesso definito come un'idea radicalmente nuova, esso nasce per risolvere problemi concreti dettati dai moderni trend tecnologici: l'esplosione del **Cloud computing**, la gestione dei **Big data**, il massiccio aumento del traffico mobile e la diffusione pervasiva dell'**IoT** (Internet of Things). I dispositivi moderni possiedono CPU più potenti, buffer più capienti e link più veloci, ma il vero ostacolo non risiede nei puri volumi di traffico, bensì nella sua **variabilità spaziale e temporale**: i pattern di traffico sono diventati altamente dinamici, complessi e strettamente sensibili alle applicazioni che li generano, rendendo insufficiente la gestione statica.

La complessità e dinamicità del traffico sono alimentate da tre fenomeni strutturali. Le architetture applicative moderne sono fortemente distribuite: interrogano database multipli e server di backend, generando enormi volumi di traffico orizzontale tra server che si sommano al tradizionale traffico verticale client-server. La proliferazione di piattaforme di **Unified Communications (UC)** integra su un'unica infrastruttura servizi come chat, voce, video e gestione della presenza, obbligando la rete a sostenere flussi paralleli con requisiti di **QoS** radicalmente diversi. Infine, l'ascesa del cloud computing ha alterato la località geografica del traffico: dati un tempo confinati nel perimetro aziendale oggi attraversano ampie **WAN** verso cloud remoti, sottoponendo i router enterprise a carichi severi e imprevedibili.

La virtualizzazione aggrava ulteriormente il quadro: migrazioni, replicazioni e failover di **Virtual Machines** causano forti sbalzi di traffico orizzontale la cui posizione e intensità variano costantemente. I dispositivi mobili aggiungono frequenti cambi di access point e ritmi di utilizzo irregolari. Il risultato è che applicazioni real-time necessitano bassa latenza, backup di massa privilegiano la banda, e transazioni finanziarie richiedono garanzie di consegna — esigenze incompatibili con l'instradamento statico.

> [!note] Il dominio del traffico East-West
>
> Oltre il 70% del traffico di rete odierno è di natura **East-West**, ovvero circoscritto alle comunicazioni interne tra server all'interno di un data center. I tradizionali data center a tre livelli (Access, Aggregation, Core) sono però ottimizzati per il traffico **North-South** (richieste client-server). Gestire efficientemente il traffico East-West richiede selezione ultra-flessibile dei path, load balancing efficace e riconfigurazioni immediate.

---

## Limiti Strutturali delle Architetture Tradizionali

Le reti convenzionali falliscono di fronte ai moderni scenari per tre ragioni fondamentali. L'**architettura statica e frammentata** è il primo problema: ogni protocollo risolve un problema isolato (routing, spanning tree, ACL) moltiplicando la complessità operativa senza una visione globale. L'**incoerenza delle policy** è il secondo: i parametri vengono elaborati localmente, obbligando gli operatori ad aggiornare manualmente ogni dispositivo con alto rischio di errata configurazione. Il **vendor lock-in** è il terzo: la logica di controllo è incapsulata in hardware proprietario privo di interfacce aperte, che impedisce la programmabilità dell'infrastruttura.

La forza storica di Internet è stata l'architettura a livelli gerarchici (Fisico, Link, Rete, Trasporto, Applicazione): la suddivisione in strati fornisce astrazioni precise dei servizi e consente a ciascun livello di evolversi indipendentemente. Tuttavia, queste astrazioni non sono state applicate in egual misura a tutti i piani. Mentre il data plane gode di logiche definite, il **control plane** tradizionale si è evoluto caoticamente aggiungendo protocolli su protocolli a ogni nuovo requisito tecnico. Costruito attorno a hardware chiusi con interfacce proprietarie, il network management non segue i principi solidi adottati, ad esempio, nei sistemi di database distribuiti: il risultato è un groviglio ingestibile di regole che sopprime l'innovazione.

---

## La Separazione tra Data Plane e Control Plane

> [!definition] Data Plane e Control Plane
>
> Il **Data Plane (Forwarding)** è l'atto meccanico e istantaneo di smistare ogni singolo pacchetto in transito su una porta d'uscita del router. Il **Control Plane (Routing)** è il processo decisionale, su scale temporali molto più dilatate, attraverso cui si mappa il tragitto completo sorgente-destinazione.

Nel tradizionale instradamento IP entrambi coesistono in un modello **per-router control plane** fortemente accoppiato: gli algoritmi risiedono in ogni nodo e calcolano localmente le tabelle di forwarding in modo decentralizzato. Tale struttura fu ideata per garantire resilienza, ma rende le moderne operazioni di _Traffic Engineering_ estremamente difficili. I link weight sono l'unico "manopola di controllo" disponibile. Si considerino tre scenari concreti su una rete con nodi u, v, w, x, y, z:

> [!example] Tre scenari impossibili con il routing tradizionale
>
> **Scenario 1 — Percorso specifico**: l'operatore vuole che il traffico da u a z segua il percorso u→v→w→z anziché il percorso più breve u→x→y→z. L'unica leva è ridefinire i link weight affinché l'algoritmo calcoli quella rotta — ma non esiste garanzia che il risultato sia quello voluto senza effetti collaterali sugli altri flussi.
>
> **Scenario 2 — Load balancing**: l'operatore vuole dividere il traffico da u a z equamente tra i due percorsi u→v→w→z e u→x→y→z. Non è possibile con il routing basato su destinazione: l'algoritmo converge su un unico percorso minimo.
>
> **Scenario 3 — Routing per-flusso**: il nodo w vuole instradare verso z in modo diverso il traffico blu (proveniente da u) rispetto al traffico rosso (proveniente da x). Non è possibile con il forwarding basato sulla sola destinazione (LS, DV): la decisione dipende unicamente dall'indirizzo di destinazione, non dal flusso.

---

## Il Paradigma SDN: Centralizzazione Logica e Programmabilità

La grande innovazione del SDN è il **Logically Centralized Control Plane**: un controller interroga e supervisiona remotamente la topologia globale calcolando le tabelle di forwarding per tutti i nodi. Mentre nel modello classico ogni tabella è rigidamente calcolata come $T_{i} = SPF(Topology, link\_weights)$ ignorando metriche esterne, nel modello SDN il controller calcola la funzione globale:

$$
\mathcal{F}: S(t) \rightarrow \{T_1, T_2, \ldots, T_n\}
$$

dove le tabelle di uscita derivano dallo stato $S(t)$ che ingloba in tempo reale topologia, traffico totale e vincoli di policy.

> [!important] Architettura SDN e astrazione Match-Action
>
> Il SDN poggia su pilastri imprescindibili: una demarcazione netta tra data plane e control plane; il control plane definisce il comportamento strategico della rete mentre il data plane applica le direttive ai pacchetti fisici; l'uso di switch elementari ad alte prestazioni governati tramite l'astrazione **match-action** orientata ai flussi (es. OpenFlow); il ricorso totale a protocolli aperti e programmabili.

Il controller SDN comunica su due assi. La **Southbound API** (tipicamente OpenFlow) è l'interfaccia verso il basso tra il controller e gli switch del data plane, tramite cui vengono installate le regole di forwarding nell'hardware. La **Northbound API** è l'interfaccia verso l'alto che dialoga con le applicazioni di gestione (bilanciamento, routing avanzato, access control), sviluppabili autonomamente da terze parti indipendentemente dai produttori hardware.

> [!warning] L'illusione del server singolo
>
> Sebbene logicamente centralizzato, il _SDN Controller_ è fisicamente implementato come un sistema fortemente distribuito. Ciò assicura tolleranza agli errori, elevata scalabilità e robustezza contro guasti singoli critici.

---

## Architettura SDN: I Tre Componenti

L'architettura SDN si articola in tre livelli distinti con ruoli ben separati.

### Data-Plane Switches

Gli switch del data plane sono dispositivi semplici e veloci, spesso basati su hardware commodity a basso costo. Il loro unico compito è applicare meccanicamente le regole di forwarding ai pacchetti in transito secondo l'astrazione **match-action**: confrontano i campi dell'intestazione del pacchetto con le regole nella flow table e applicano l'azione corrispondente. Le flow table vengono calcolate e installate da remoto dal controller, non localmente. Lo switch espone un'API standardizzata (tipicamente OpenFlow) che definisce cosa è controllabile dall'esterno e cosa no, e un protocollo per comunicare con il controller.

### SDN Controller (Network Operating System)

Il controller SDN svolge il ruolo di **sistema operativo di rete**: mantiene una visione aggiornata dello stato globale della rete (topologia, link attivi, tabelle di forwarding). È il punto di mediazione tra le applicazioni che esprimono policy di alto livello e gli switch che le devono applicare. Interagisce verso il basso tramite la **Southbound API** con gli switch del data plane, e verso l'alto tramite la **Northbound API** con le applicazioni di controllo. Sebbene appaia come un'entità singola, è implementato come sistema distribuito per garantire performance, scalabilità, tolleranza ai guasti e robustezza.

### Network-Control Applications

Le applicazioni di controllo sono il vero "cervello" della rete: implementano le funzioni di controllo (routing, access control, load balancing, …) sfruttando i servizi e le API esposte dal controller. Il punto chiave è che sono **unbundled**: possono essere sviluppate e fornite da soggetti terzi — distinti sia dal produttore degli switch hardware sia dal produttore del controller SDN. Questo disaccoppiamento abilita un ecosistema aperto in cui l'innovazione a livello applicativo è indipendente dall'hardware sottostante.

> [!abstract] Sintesi dell'architettura
>
> | Livello | Componente | Ruolo |
> |---------|-----------|-------|
> | Alto | Network-control apps | "Brains": routing, load balancing, ACL — unbundled, terze parti |
> | Medio | SDN Controller (Network OS) | Stato globale della rete; northbound ↔ southbound |
> | Basso | Data-plane switches | Match-action su flow table installate dal controller |

---

## Cronologia e Sviluppi Storici

| **Periodo** | **Pietra Miliare** | **Dettagli** |
|---|---|---|
| ~2004 | Genesi ricercativa | Princeton, Stanford, Berkeley avviano la ricerca su nuovi paradigmi di gestione del networking. |
| 2008 | Nascita ufficiale SDN | NICIRA presenta NOX; OpenFlow nasce in collaborazione con Stanford. |
| 2011 | Standardizzazione | Fondazione dell'**Open Networking Foundation (ONF)** con Google, Yahoo, Verizon, Cisco, HP, Dell. |
| 2013 | Consacrazione scalabile | Picco di interesse all'Open Networking Summit (1600 partecipanti). Google rende pubblica la propria implementazione SDN sulla WAN globale. |
| 2014 | Data center | VMware NSX e Cisco ACI portano SDN nei data center globali. |
| 2021+ | ML, 5G, P4 | Intent-Based Networking con AI/ML (Cisco DNA, Mist AI). SDN come base del 5G. Linguaggio **P4** (Programming Protocol-independent Packet Processors) per switch programmabili a line speed. |

---

> [!question] Possibili domande d'esame
>
> - Cos'è il SDN e quale problema risolve rispetto alle architetture tradizionali?
> - Qual è la differenza tra Data Plane (Forwarding) e Control Plane (Routing)?
> - Cos'è il traffico East-West e perché le architetture tradizionali faticano a gestirlo?
> - Descrivere i tre scenari di Traffic Engineering che risultano impossibili con il routing tradizionale.
> - Quali sono i tre limiti strutturali delle reti tradizionali (architettura statica, incoerenza delle policy, vendor lock-in)?
> - Descrivere i tre componenti dell'architettura SDN (data-plane switches, controller, network-control apps) e il ruolo di ciascuno.
> - Cosa significa che le network-control apps sono "unbundled"? Qual è il vantaggio?
> - Cosa sono le Southbound e Northbound API in un'architettura SDN?
> - Cos'è l'astrazione match-action e perché è fondamentale per il data plane programmabile?
> - Perché il controller SDN è "logicamente centralizzato" ma fisicamente distribuito?
> - Qual è la differenza tra $T_i = SPF(Topology, link\_weights)$ e $\mathcal{F}: S(t) \rightarrow \{T_1, \ldots, T_n\}$?
