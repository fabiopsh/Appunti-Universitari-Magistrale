# Software Defined Networking (SDN)

Questo paradigma architetturale segna il definitivo passaggio da un sistema di protocolli puramente distribuiti a un framework di controllo di rete completamente programmabile.

> [!definition] Software Defined Networking
>
> Il **Software Defined Networking** è un approccio alla gestione delle reti che sfrutta potenti meccanismi di astrazione per abilitare configurazioni e operazioni dinamiche ed efficienti a livello programmatico. La caratteristica distintiva è la separazione netta tra **control plane** e **data plane**.

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

![[exam_mod2_sdn_architecture.jpg]]

Questo schema illustra l'**architettura a tre livelli di SDN**, che realizza la separazione netta tra data plane, control plane e application plane. L'architettura si articola in tre livelli distinti con ruoli ben separati:

### Data-Plane Switches (Livello inferiore)

Contiene gli switch del data plane, che possono essere sia fisici (hardware commodity a basso costo) sia virtuali (Open vSwitch su hypervisor). Sono dispositivi semplici e veloci: il loro unico compito è applicare meccanicamente le regole di forwarding (match-action) ai pacchetti in transito secondo le flow table installate dal controller. Non calcolano nulla autonomamente. Le flow table vengono calcolate e installate da remoto dal controller, non localmente. Lo switch espone un'API standardizzata (tipicamente OpenFlow) che definisce cosa è controllabile dall'esterno e cosa no, e un protocollo per comunicare con il controller.

### SDN Controller / Control Plane (Livello centrale)

Il controller SDN svolge il ruolo di **sistema operativo di rete**: mantiene una visione aggiornata dello stato globale della rete (topologia, link attivi, tabelle di forwarding). È il punto di mediazione tra le applicazioni che esprimono policy di alto livello e gli switch che le devono applicare. Contiene il controller SDN, o meglio una **rete di controller SDN** distribuiti. Sebbene appaia come un'entità logicamente centralizzata (ha una visione globale della rete), è implementato fisicamente come sistema distribuito per garantire performance, scalabilità, tolleranza ai guasti e robustezza. Il controller mantiene: la topologia della rete, le statistiche dei flussi, i link attivi, le tabelle di forwarding. Comunica verso il basso con il Data Plane tramite la **Southbound API** (tipicamente OpenFlow), e verso l'alto con le applicazioni tramite la **Northbound API**. I controller comunicano tra loro tramite **Westbound/Eastbound API** per sincronizzare lo stato globale.

### Network-Control Applications / Application Plane (Livello superiore)

Le applicazioni di controllo (*network-control applications*) sono il vero "cervello" della rete: implementano le funzioni di controllo (routing, access control, load balancing, monitoraggio, rilevamento anomalie, …) sfruttando i servizi e le API esposte dal controller. Il punto chiave è che sono **unbundled**: possono essere sviluppate e fornite da terze parti indipendentemente dai produttori hardware e software del controller. Questo disaccoppiamento abilita un ecosistema aperto in cui l'innovazione a livello applicativo è indipendente dall'hardware sottostante. Le applicazioni esprimono policy di alto livello al controller tramite la Northbound API.

> [!note] Il valore dell'architettura a livelli
>
> La separazione in tre piani replica il principio dei livelli di astrazione di Internet. Ogni livello si può evolvere indipendentemente: nuovi algoritmi di routing nel Control Plane, nuove applicazioni nell'Application Plane, nuovo hardware nel Data Plane — senza impatto sugli altri livelli. Questo è il vantaggio principale rispetto alle reti tradizionali con logica chiusa nell'hardware proprietario.
