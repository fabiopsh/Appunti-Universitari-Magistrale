---
tags:
  - università/mobile-cyber-physical-systems
  - NFV
  - network-virtualization
  - SDN
data: 2026-04-14
lezione: "Network Function Virtualization"
professore: "Federica Paganelli"
---

# Network Function Virtualization

La **Network Function Virtualization** (NFV) rappresenta uno dei cambiamenti di paradigma più significativi nell'ingegneria delle reti degli ultimi anni. L'idea fondamentale è semplice ma rivoluzionaria: spostare le funzioni di rete — firewall, bilanciatori di carico, gateway — dall'hardware proprietario dedicato a software eseguito su infrastruttura virtualizzata generica. Questa lezione ripercorre il problema che NFV risolve, i suoi benefici, la sua architettura e come i servizi di rete vengono effettivamente composti e distribuiti.

---

## Il problema: middlebox e rigidità hardware

### Un mondo di middlebox

Le reti tradizionali non sono composte solo da router e switch. Accanto a questi elementi "trasparenti" proliferano i **middlebox**: dispositivi che eseguono funzioni di elaborazione avanzata oltre al semplice inoltro dei pacchetti. Firewall, sistemi di rilevamento delle intrusioni (NIDS), media gateway, load balancer, proxy, VPN gateway, WAN optimizer — in una grande impresa con oltre 80.000 utenti su decine di siti, questi apparati possono essere addirittura più numerosi dei router tradizionali.

> [!example] Dati da una grande enterprise (Sekar et al., 2011)
>
> | Tipo di apparato | Numero |
> |---|---|
> | Firewall | 166 |
> | NIDS | 127 |
> | Media gateway | 110 |
> | Load balancer | 67 |
> | Proxy | 66 |
> | VPN gateway | 45 |
> | WAN Optimizer | 44 |
> | **Totale middlebox** | **636** |
> | Totale router | ~900 |
>
> I middlebox sono quasi pari in numero ai router: la rete è molto più di semplice forwarding.

### Il modello tradizionale e i suoi limiti

Nell'industria delle telecomunicazioni tradizionale, ogni funzione di rete corrisponde a un **apparato hardware proprietario** dedicato. Il firewall è un box fisico, il load balancer è un altro box fisico, e così via. Questo modello impone vincoli severi:

- Le funzioni devono essere concatenate in un ordine preciso, riflesso nella topologia fisica della rete (es. il traffico deve passare prima per il firewall e poi per il load balancer — non si può cambiare senza ricablare).
- I fornitori devono garantire alti standard di qualità, performance e conformità ai protocolli, con cicli di sviluppo prodotto molto lunghi.
- Il risultato è una **scarsa agilità**: aggiungere una nuova funzione o scalare una esistente richiede acquisto di nuovo hardware, deployment manuale e formazione del personale.

Contemporaneamente, gli utenti richiedono servizi sempre più diversificati e di breve durata. Ogni nuovo servizio richiede nuovo hardware, deployment manuale e nuove competenze. Le reti diventano complesse, difficili da scalare e costose da operare: i costi **CAPEX** (*Capital Expenditure*, l'investimento in hardware e infrastruttura fisica) e **OPEX** (*Operational Expenditure*, i costi operativi di energia, manutenzione e personale) crescono, ma i ricavi no.

> [!warning] Il nodo del problema
>
> Il modello hardware-based è per natura *lento e rigido*. I provider di servizi Internet (Google, Amazon, Facebook) hanno invece dimostrato che un approccio *software-based* è *veloce e flessibile*. NFV nasce dalla volontà di portare questo modello software dentro le reti di telecomunicazione.

---

## NFV: l'idea fondamentale

Nel 2012, i principali operatori globali (AT&T, Telefónica, Verizon e altri) avviarono un'iniziativa presso **ETSI** (European Telecommunications Standards Institute), dando vita all'Industry Specification Group for NFV. L'obiettivo: trasformare le reti attraverso la virtualizzazione.

### Decoupling tra funzioni e hardware

Il principio cardine di NFV è il **disaccoppiamento** (*decoupling*) tra le funzioni di rete e l'hardware su cui girano. Le funzioni non sono più implementate in appliance fisiche dedicate, ma come **software** eseguito su infrastruttura virtualizzata standard (macchine virtuali o container su server COTS — *Commercial Off-The-Shelf*).

![Confronto tra il modello tradizionale (appliance approach) e il modello virtualizzato (virtual appliance approach)](images/lezione-20-lab-network-function-virtualization-img-01.jpg)
*Fig. — A sinistra, il modello tradizionale: ogni funzione (DPI, Firewall, BRAS, CG-NAT...) richiede HW specifico e un solo ruolo per nodo. A destra, il modello NFV: le stesse funzioni girano come software su server standard ad alto volume, orchestrate in modo automatico e remoto.*

Nel modello tradizionale le funzioni di rete sono basate su HW e SW proprietari, con un nodo fisico per ogni ruolo. Nel modello NFV le funzioni sono implementate in software su hardware commodity, e più ruoli possono coesistere sullo stesso server fisico.

---

## Vantaggi di NFV

NFV introduce tre famiglie di benefici fondamentali:

**Flessibilità**: le funzioni possono essere deployate ovunque nell'infrastruttura e spostate dinamicamente in base alle esigenze, grazie all'allocazione flessibile delle risorse hardware condivise (*hardware pool*).

**Scalabilità ed efficienza**: la capacità dedicata a ciascuna funzione può essere modificata dinamicamente (*scaling up/down*) in base al carico effettivo, migliorando l'utilizzo delle risorse. Non è più necessario acquistare hardware ridondante per gestire i picchi: si alloca più capacità software quando serve e la si riduce quando non serve.

**Innovazione accelerata**: il ciclo di sviluppo di un nuovo servizio di rete si accorcia drasticamente, perché non richiede procurement hardware ma soltanto deployment software.

> [!note] NFV introduce anche nuove sfide
>
> La virtualizzazione porta con sé problemi nuovi: gestione del ciclo di vita delle funzioni, orchestrazione, performance (overhead della virtualizzazione), sicurezza dell'infrastruttura condivisa, e il complesso problema del *placement* delle funzioni virtualizzate.

---

## Da funzioni di rete a servizi di rete

### Composizione di funzioni

Una singola funzione (es. un firewall) non è sufficiente a realizzare un servizio reale. I servizi richiedono la **composizione di più funzioni** applicate in sequenza al traffico. In un servizio tipico, un utente che accede a Internet deve attraversare: firewall → antivirus → video optimizer → parental control. Sequenze diverse possono applicarsi a traffici diversi.

![Schema di un servizio di rete come composizione di funzioni (Firewall, NAT, Load Balancer, Web Service)](images/lezione-20-lab-network-function-virtualization-img-02.jpg)
*Fig. — Un servizio di rete minimo: il traffico dell'utente attraversa in sequenza Firewall, NAT e Load Balancer prima di raggiungere il Web Service.*

In un'infrastruttura reale, non tutto il traffico segue la stessa catena: il servizio non è una pipeline fissa ma una composizione flessibile di funzioni, dipendente dai requisiti del flusso. Questo pone la domanda: come modificare le rotte per applicare trattamenti differenziati a flussi diversi? La risposta è [[Software Defined Networking]] (SDN), che fornisce il piano di controllo per il service chaining.

![Esempio di rete NFV con service chaining su piattaforma SDN](images/lezione-20-lab-network-function-virtualization-img-03.jpg)
*Fig. — Le reti fissa e mobile convergono su una piattaforma NFV. Un service classifier instrada il traffico attraverso funzioni diverse (Firewall, Antivirus, Video optimizer, Parental control) via SDN, prima di raggiungere Internet.*

### Network Function Forwarding Graph (NF-FG)

In NFV, un servizio di rete end-to-end è formalizzato come un **grafo di forwarding** di funzioni di rete e punti terminali. Questo è ciò che un operatore fornisce ai propri clienti.

![Network Service in NFV: il Network Function Forwarding Graph con endpoint e VNF collegate da link logici](images/lezione-20-lab-network-function-virtualization-img-04.jpg)
*Fig. — Un servizio end-to-end è un grafo: l'endpoint A è connesso all'endpoint B attraverso VNF 1, VNF 2 e VNF 3 via link logici.*

> [!definition] VNF — Virtualized Network Function
>
> Una **Virtualized Network Function** (VNF) è l'implementazione software di una funzione di rete tradizionalmente realizzata in hardware dedicato (firewall, load balancer, NAT, ecc.), eseguita su risorse virtualizzate (VM o container).

La separazione fondamentale introdotta da NF-FG è tra:
- la **definizione logica del servizio**: il grafo descrive quali funzioni servono e come sono connesse (link logici)
- il **deployment fisico**: i link logici sono supportati da percorsi fisici attraverso reti di infrastruttura distinte

![VNF-FG mappato su infrastruttura fisica: link logici e link fisici su tre reti di infrastruttura separate](images/lezione-20-lab-network-function-virtualization-img-05.jpg)
*Fig. — Il grafo logico del servizio (VNF 1, VNF 2, VNF 3 con link tratteggiati) è mappato su tre reti di infrastruttura fisiche distinte. La separazione logico/fisico è il principio chiave.*

### VNF-FG nidificati e PoP

Le VNF girano su nodi fisici chiamati **PoP** (*Points of Presence*). I grafi di forwarding possono essere nidificati: un VNF-FG può essere costruito componendo altri VNF-FG (esempio: VNF-FG-2 composto da VNF-2A, VNF-2B e VNF-2C), consentendo la definizione di servizi gerarchici e riutilizzabili.

![VNF Forwarding Graph con VNF-FG annidato (VNF-FG-2) e PoP fisici alla base](images/lezione-20-lab-network-function-virtualization-img-06.jpg)
*Fig. — Il servizio end-to-end (tra End Point A e B) è un VNF-FG composto da VNF-1, dal sotto-grafo VNF-FG-2 (con VNF-2A, VNF-2B, VNF-2C) e VNF-3. Le VNF girano su PoP fisici (NFVI-PoP) tramite un livello di virtualizzazione.*

---

## Il problema del VNF Placement

Dato un servizio di rete composto da più VNF, occorre decidere **dove deployare ciascuna funzione** nell'infrastruttura fisica. Questo è il problema del *VNF chain placement*, uno dei problemi di ottimizzazione centrali in NFV.

Gli obiettivi di ottimizzazione tipici sono:
- minimizzare la latenza end-to-end
- minimizzare i costi di deployment
- massimizzare la banda residua
- risparmiare energia

Soggetti ai vincoli di:
- capacità computazionale dei nodi
- banda disponibile sui link
- requisiti di QoS (latenza massima, banda minima)

> [!tip] VNF placement e 5G Network Slicing
>
> Il VNF placement è particolarmente rilevante nel contesto del [[5G]] e del **network slicing**: ogni slice deve avere una catena di VNF dedicata con garanzie di isolamento e QoS. L'orchestratore deve risolvere il problema di placement per ogni slice contemporaneamente, spesso con obiettivi conflittuali.

Gli approcci risolutivi spaziano dalla **programmazione matematica** (ILP, MILP) alle **euristiche** e **metaeuristiche** (Algoritmi Genetici), fino al **Deep Reinforcement Learning** per scenari dinamici.

### Nuove sfide: hardware programmabile

Le VNF possono essere deployate non solo su server, ma anche su **dispositivi di rete programmabili**, ciascuno con un profilo prestazionale diverso:

| Dispositivo | Latenza per pacchetto | Caratteristiche |
|---|---|---|
| Programmable switch | 1–2 µs | Velocissimo, ma memoria e flessibilità limitate |
| Server (COTS) | 1–10 µs | Flessibile, ma più lento |
| SmartNIC | 10–100+ µs | Soluzione intermedia |

La scelta del dispositivo su cui deployare ciascuna VNF aggiunge una dimensione ulteriore al problema di placement.

---

## L'architettura NFV

L'architettura di riferimento NFV, standardizzata da ETSI, è organizzata in tre blocchi principali: l'**infrastruttura** (NFVI), le **funzioni virtualizzate** (VNF) e il **sistema di gestione e orchestrazione** (NFV-MANO).

![NFV Reference Architectural Framework con NFVI, VNF, EMS, NFVO, VNFM, VIM e interfacce di riferimento](images/lezione-20-lab-network-function-virtualization-img-07.jpg)
*Fig. — Il framework architetturale di riferimento NFV secondo ETSI/Stallings. Le frecce indicano i reference point: Or-Vi, Or-Vnfm, Ve-Vnfm, Vi-Vnfm, Nf-Vi, Se-Ma, Os-Ma.*

### NFV Infrastructure (NFVI)

L'**NFVI** è la totalità delle risorse hardware e software che costituiscono l'ambiente di esecuzione delle VNF. Virtualizza risorse fisiche di computing, storage e networking raggruppandole in *resource pool*.

È composta da tre domini:

- **Compute domain**: fornisce server COTS ad alto volume e storage.
- **Hypervisor domain**: media le risorse del compute domain alle VM (o container) delle VNF, fornendo un'astrazione dell'hardware. Oggi le VNF sono spesso eseguite in container → **Cloud Native Functions (CNF)**.
- **Infrastructure network domain**: switch generici ad alto volume interconnessi in una rete configurabile per erogare servizi di rete.

![Schema dei domini NFVI: compute domain, hypervisor domain e infrastructure network domain](images/lezione-20-lab-network-function-virtualization-img-08.jpg)
*Fig. — L'NFVI si stratifica in tre livelli: hardware fisico (compute, storage, network hardware), virtualizzazione (hypervisor/virtualization layer) e risorse virtuali (virtual computing, storage, network).*

L'NFVI può distribuirsi su più **NFVI-PoP** (*Network Function Virtualization Infrastructure Point of Presence*): posizioni fisiche dove sono deployate le risorse di infrastruttura NFV. Due tipi di rete interconnettono i PoP:
- **NFVI-PoP network**: connette le risorse all'interno di un PoP.
- **Transport network**: interconnette i vari NFVI-PoP tra loro e verso l'esterno.

#### vSwitch

All'interno di un PoP, le VM sono collegate a interfacce virtuali (**VIF**). Un **virtual switch** (vSwitch) è un programma software che emula uno switch di livello 2, fornendo connettività tra le VIF e le interfacce fisiche (PIF), oltre a gestire il traffico tra VIF sullo stesso host fisico. L'esempio più noto è **Open vSwitch** (OVS), che supporta OpenFlow e può integrarsi con switch fisici.

#### Opzioni di virtualizzazione

Le VNF possono essere eseguite in **macchine virtuali** (VM) o in **container**. La differenza fondamentale:

![Confronto architetturale tra container (Docker engine) e macchine virtuali (hypervisor)](images/lezione-20-lab-network-function-virtualization-img-09.jpg)
*Fig. — A sinistra i container: condividono il kernel dell'host, isolati in userspace tramite Docker engine. A destra le VM: includono un guest OS completo sopra l'hypervisor.*

> [!definition] Container vs VM
>
> I **container** includono l'applicazione e le sue dipendenze ma condividono il kernel dell'host OS, girando come processi isolati in userspace. Le **VM** includono invece l'applicazione, le librerie necessarie e un intero guest OS, con un overhead maggiore ma un isolamento più forte.

### NFV Management and Orchestration (NFV-MANO)

Il **MANO** è il framework che gestisce e orchestra tutte le risorse nell'ambiente NFV. Comprende:

#### NFV Orchestrator (NFVO)

Responsabile di installare e configurare nuovi **Network Service (NS)** e pacchetti VNF, gestire il ciclo di vita dei servizi di rete e le risorse globali. Opera su due piani:
- **Network services orchestration**: gestisce/coordina la creazione di servizi end-to-end tra VNF diverse, può istanziare nuovi VNFM.
- Esempi di implementazioni open source: **OSM MANO** (ETSI) e **ONAP** (Linux Foundation).

#### VNF Manager (VNFM)

Gestisce il **ciclo di vita delle istanze VNF**:
- istanziazione (con configurazione iniziale se richiesta dal deployment template)
- scaling out/in e up/down
- raccolta di misure di performance dell'NFVI e correlazione con eventi/fault VNF
- healing automatico o assistito
- terminazione dell'istanza

#### Virtualized Infrastructure Manager (VIM)

Il **VIM** controlla e gestisce l'interazione delle VNF con le risorse fisiche (computing, storage, network) e la loro virtualizzazione, tipicamente all'interno del dominio infrastrutturale di un singolo operatore. Piattaforme IaaS come **OpenStack** fungono da VIM. Un MANO può orchestrare più VIM.

### Repository MANO

Il sistema MANO utilizza quattro repository:

| Repository | Contenuto |
|---|---|
| **Network services catalog** | Template di deployment dei network service in termini di VNF e virtual link |
| **VNF catalog** | VNF Descriptor (VNFD): descrive deployment e behavior di ogni VNF |
| **NFVI resources** | Lista delle risorse NFVI utilizzate per i servizi NFV attivi |
| **NFV instances** | Dettagli sulle istanze di network service e VNF in esecuzione |

---

## Network Service Descriptor: un esempio

Il deployment di un network service è descritto tramite un **Network Service Descriptor (NSD)**, un documento strutturato (tipicamente JSON/YAML) che specifica la composizione del servizio.

> [!example] NSD per un servizio iperf (client-server)
>
> ```json
> {
>   "name": "iperf-NSD",
>   "vendor": "fokus",
>   "version": "0.1-ALPHA",
>   "vnfd": [ ... ],
>   "vld": [ { "name": "private" } ],
>   "vnf_dependency": [
>     {
>       "source": { "name": "iperf-server" },
>       "target": { "name": "iperf-client" },
>       "parameters": ["private"]
>     }
>   ]
> }
> ```
>
> | Campo | Significato |
> |---|---|
> | `name` | Nome del Network Service |
> | `vendor` | Provider del servizio |
> | `vnfd` | Lista delle VNF che compongono il servizio |
> | `vld` | Virtual Link: connettività tra VNF |
> | `vnf_dependency` | Dipendenza tra VNF: l'iperf-server deve fornire il proprio IP all'iperf-client |

Il VNFD per ogni VNF specifica: immagine VM, risorse (flavour), virtual link, lifecycle events (script da eseguire all'istanziazione: `install.sh`, `start-srv.sh`) e configurazione.

---

## Casi d'uso

NFV è applicabile sia alle funzioni del **piano dati** che a quelle del **piano di controllo** nelle reti mobili e fisse:

- **Traffic analysis**: DPI (*Deep Packet Inspection*), misurazione QoE
- **Application-level optimization**: cache server, load balancer, application accelerator
- **Sicurezza**: firewall, virus scanner, IDS, spam protection, gateway IPsec/SSL VPN
- **Nodi di rete mobile**: HLR/HSS, MME, SGSN, PDN-GW, eNodeB (sia il core EPC che la RAN possono essere in larga parte virtualizzati)
- **Infrastruttura di rete**: broadband gateway, CG-NAT, router
- **Edge & Home**: home router, set-top box
- **Controllo & Gestione**: AAA server, policy control, sistemi di charging

---

## Sintesi

> [!abstract] NFV in sintesi
>
> Nelle reti tradizionali, ogni dispositivo è deployato su piattaforme proprietarie/chiuse. Gli elementi di rete sono box chiusi, l'hardware non può essere condiviso, e ogni device richiede hardware aggiuntivo per aumentare la capacità — hardware che rimane inattivo quando il sistema è sotto carico.
>
> Con NFV, gli elementi di rete sono **applicazioni indipendenti** deployate in modo flessibile su una piattaforma unificata di server standard, storage e switch commodity. Software e hardware sono disaccoppiati, e la capacità per ogni applicazione viene aumentata o ridotta aggiungendo o riducendo risorse virtuali.
>
> I benefici principali: **flessibilità**, **innovazione più rapida**, possibilità di **scalare i servizi rapidamente** su/giù secondo le necessità.

> [!question] Possibili domande d'esame
>
> - Che cos'è un middlebox e perché la loro proliferazione ha motivato NFV?
> - Qual è la differenza tra CAPEX e OPEX nel contesto NFV?
> - Descrivere il Network Function Forwarding Graph e la separazione tra definizione logica e deployment fisico.
> - Quali sono i tre componenti principali dell'architettura NFV-MANO? Descrivere le responsabilità di NFVO, VNFM e VIM.
> - In cosa consiste il problema del VNF chain placement e quali approcci risolutivi esistono?
> - Confrontare container e VM come opzioni di virtualizzazione per le VNF.
> - Cosa sono gli NFVI-PoP e come si differenziano NFVI-PoP network e transport network?
