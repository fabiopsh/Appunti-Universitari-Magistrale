## Ethernet come standard de facto

Il punto di partenza è riconoscere il ruolo attuale dello switch di rete: non è più semplicemente un modo per connettere computer a Internet, ma è il meccanismo con cui si aggregano elementi computazionali in blocchi più grandi. In questo contesto, il traffico dominante nei data center è il cosiddetto **east-west traffic** — cioè il traffico tra server all'interno dello stesso data center — anziché il tradizionale traffico north-south verso l'esterno.

Ethernet è diventato lo standard di connessione locale non perché fosse tecnicamente il migliore, ma perché era il più adottato. La diffusione di massa ha generato economie di scala che hanno abbassato i costi dell'hardware e stimolato lo sviluppo di un ecosistema software enormemente ricco. Originariamente Ethernet era progettato per un singolo cavo coassiale condiviso — un bus fisico — ma questa architettura fisica non esiste più: oggi si emula virtualmente, e tutta l'infrastruttura software costruita su di essa è il vero motivo per cui continuiamo a usarla.

> [!tip] Intuizione chiave
> 
> Ethernet non ha vinto per meriti tecnici assoluti, ma per effetto di rete: più utenti → più volumi → costi più bassi → ancora più utenti. Questa dinamica si ripete in molte tecnologie informatiche.

Quando i requisiti cambiano, lo standard viene esteso anziché rimpiazzato. Le VLAN ne sono l'esempio più importante: aggiungono un tag all'header Ethernet per consentire la segmentazione logica della rete.

---

## MTU e dimensione dei pacchetti

> [!definition] MTU — Maximum Transmission Unit
> 
> La dimensione massima di un frame (pacchetto) che un dispositivo di rete è configurato ad accettare. Il valore di default in Ethernet è **1,5 KB** (più precisamente 1500 byte).

Sapere quanto è grande un pacchetto di rete è fondamentale per capire le prestazioni. Ogni unità di elaborazione di rete implementa un loop del tipo _"per ogni pacchetto, fai qualcosa"_: se i pacchetti sono molti e piccoli, il numero di iterazioni cresce, aumentando il carico sulla CPU. Se i pacchetti sono grandi, diminuisce il numero di iterazioni ma si richiede più memoria per i buffer.

Questo compromesso ha una conseguenza pratica: **i frame Jumbo**. Nei data center è possibile configurare switch per accettare frame da **9 KB** (fattore 6 rispetto al default). Questo è stato introdotto quando si iniziò a usare Ethernet per il traffico di storage, dove trasferire molti dati con un overhead basso è critico.

> [!warning] Attenzione: consistenza dell'MTU nella rete
> 
> In una rete a più switch (es. topologia a tre livelli), tutti i dispositivi lungo un percorso devono avere lo stesso MTU configurato. Se un frame da 9 KB arriva su un link con MTU 1,5 KB, il ricevente deve frammentarlo in 6 pacchetti più piccoli — vanificando il vantaggio del jumbo frame e aggiungendo lavoro inutile. L'MTU è uno dei parametri di configurazione più sottovalutati e fonte di problemi difficili da diagnosticare.

---

## Control plane, CLI e filosofia delle command line

I parametri come l'MTU si configurano attraverso il **control plane** dello switch, tipicamente tramite una **CLI** (Command Line Interface). La CLI degli switch di rete ha una struttura modale: si entra in un contesto (es. `vlan 3`), si emettono comandi specifici, poi si esce. Questa filosofia si è diffusa ben oltre il networking: il comando `ip` di Linux, `netsh` di Windows, e persino `docker` e altri strumenti moderni adottano lo stesso paradigma di _verbo + sottocomando_.

> [!note] Nota filosofica: Unix vs CLI moderna
> 
> La filosofia Unix tradizionale prevedeva comandi piccoli e atomici (`cp`, `ls`, `sort`) composti tramite pipe per costruire comportamenti complessi. La filosofia moderna, nata probabilmente con Docker, preferisce un singolo comando "grasso" con molti sottocomandi (`docker ps`, `docker image`, `docker exec`). Questo riduce la componibilità ma semplifica la gestione e il versionamento quando il numero di risorse da gestire è molto elevato.

---

## VLAN: segmentazione logica del broadcast domain

> [!definition] VLAN — Virtual LAN
> 
> Una VLAN è un tag inserito nell'header Ethernet che identifica il **broadcast domain** di appartenenza di un frame. Permette di dividere logicamente una rete fisica in più reti separate, senza modificare il cablaggio.

Il meccanismo è semplice: quando un frame non taggato arriva su una porta configurata come _untagged_ di una certa VLAN, lo switch lo riscrive aggiungendo il VLAN ID corrispondente. Tutti i frame all'interno dello switch vengono quindi trattati con il loro VLAN ID, garantendo isolamento tra broadcast domain diversi.

### Porte access e trunk

Quando una porta è associata a un unico VLAN ID con traffico non taggato, si parla di porta in **modalità access**: tipicamente usata per connettere un singolo host che non deve preoccuparsi del tagging. Quando invece una porta è associata a più VLAN ID (con traffico taggato), si parla di porta in **modalità trunk**: è usata per i collegamenti tra switch, dove è necessario trasportare il traffico di più broadcast domain sullo stesso cavo fisico.

> [!example] Esempio pratico
> 
> Un data center ha due rack connessi da un singolo cavo tra i rispettivi leaf switch. Quel cavo deve trasportare il traffico di VLAN 2 e VLAN 3 simultaneamente. La porta su entrambi gli switch viene configurata come trunk con VLAN 2 e 3 tagged. In questo modo non è necessario un cavo per ogni VLAN.

### VLAN nella topologia spine-leaf

In un'architettura spine-leaf, le porte sui leaf switch che si collegano verso la spine vengono configurate con tutti i VLAN ID in uso. Ogni frame che arriva su un leaf taggato con un certo VLAN ID viene inoltrato verso la spine solo se la porta di uplink include quel VLAN ID nel trunk. Questo permette di avere una rete logicamente ricca su una topologia fisica molto regolare.

> [!warning] Limite fondamentale delle VLAN
> 
> Lo standard 802.1Q supporta al massimo **4096 VLAN ID** (12 bit). Per una cloud pubblica con milioni di tenant, questo numero è assolutamente insufficiente.

---

## VXLAN e overlay network

Il limite delle 4096 VLAN, combinato con la difficoltà di gestire manualmente la configurazione di ogni switch, ha portato allo sviluppo del **VXLAN** (_Virtual Extensible LAN_).

> [!definition] VXLAN
> 
> VXLAN è un protocollo di **overlay network**: incapsula il traffico di layer 2 (Ethernet) all'interno di pacchetti UDP di layer 3 (IP). Questo permette di simulare reti layer 2 arbitrarie su un'infrastruttura layer 3 esistente.

### Perché conviene lavorare a layer 3

Operare a livello IP (layer 3) offre vantaggi critici rispetto al layer 2 puro:

- **Debug molto più semplice**: a layer 3 ogni pacchetto ha sorgente e destinazione ben definite; è possibile tracciare il percorso e isolare i problemi. A layer 2, un loop di broadcast può abbattere interi domini broadcast senza che sia facile capire dove si trova il problema.
- **Scalabilità**: i VXLAN network identifier sono a 24 bit, ovvero circa **16 milioni** di segmenti virtuali — ordini di grandezza superiori alle 4096 VLAN.
- **Automazione**: i segmenti virtuali vengono creati e gestiti via software, senza intervento manuale su ogni switch fisico.

> [!example] Esempio reale: università di Pisa
> 
> Il core network dell'università usa VXLAN per collegare i diversi dipartimenti. Quando c'è stato un incidente alla facoltà di ingegneria, fu necessario ripristinare rapidamente la connettività creando link layer 2 temporanei. Questo introdusse un loop che causò l'interruzione del servizio. La lezione appresa: reti layer 2 estese sono difficili da debuggare; lavorare a layer 3 con VXLAN riduce drasticamente questo rischio.

### Architettura VXLAN in produzione

In Azure (e provider simili), ogni rack del data center è un dominio layer 2. Tutto il traffico che esce dal rack viene immediatamente incapsulato in layer 3. Questo rende il troubleshooting molto più efficace: ogni flusso ha un identificatore IP univoco e può essere tracciato indipendentemente.

> [!abstract] Sintesi VLAN vs VXLAN
> 
> Le VLAN segmentano un dominio broadcast fisico usando tag nell'header Ethernet (layer 2). VXLAN crea reti layer 2 virtuali incapsulando il traffico in UDP/IP (layer 3). VXLAN richiede un control plane: questo è svolto da **EVPN** (_Ethernet VPN_), il protocollo che gestisce la distribuzione delle informazioni di raggiungibilità tra i nodi VXLAN.

---

## Protocolli implementati da uno switch

Uno switch moderno è molto più di un semplice dispositivo di forwarding. Implementa decine di protocolli, tra cui:

**Switching e VLAN:** IEEE 802.1Q (VLAN tagging), 802.1ad (Q-in-Q, per incapsulare VLAN dentro altre VLAN), Spanning Tree Protocol e varianti (per prevenire loop).

**Quality of Service:** ETS (_Enhanced Transmission Selection_) per il controllo di flusso, PFC (_Priority Flow Control_) per la prioritizzazione del traffico. Questi standard, nati per il traffico storage (dove i dischi non possono aspettare), permettono di suddividere la banda tra fino a 16 classi di traffico con diverse priorità.

> [!note] Il mito di Ethernet senza QoS
> 
> Si sente spesso dire che Ethernet non supporta Quality of Service. Non è vero: il puro standard IEEE 802.3 non ha flow control, ma le estensioni ETS e PFC, presenti in tutti gli switch data center moderni, forniscono proprio questo. Quello che è "lento" non è Ethernet, ma TCP.

**Overlay e virtualizzazione:** VXLAN, EVPN, MAC-in-UDP per il tunneling layer 2 su layer 3.

**Routing:** OSPF, BGP, ARP, protocolli multicast.

**Gestione:** SNMP per il monitoring, syslog, NetFlow per l'analisi del traffico, LLDP/CDP per la discovery della topologia.

---

## OpenFlow e Software Defined Networking

### Il problema della ricerca in rete

Intorno al 2008, ricercatori di Stanford identificarono un problema: i network administrator non permettevano di sperimentare su switch reali perché troppo critici. La ricerca in networking era bloccata.

### La flow table

Per capire OpenFlow occorre capire come funziona internamente uno switch: i dispositivi moderni mantengono una **flow table**, una struttura dati che associa pattern di traffico ad azioni. Anziché rieseguire ogni volta tutta la logica di configurazione per ogni pacchetto, lo switch costruisce regole del tipo:

> Se (source MAC = X) AND (destination IP = Y) AND (VLAN = Z) → output porta 2

Una volta che un flusso è noto, questa regola viene eseguita direttamente in hardware, senza ricalcolare tutto da capo. La flow table include anche contatori, utili per il debugging e il monitoring.

> [!definition] OpenFlow
> 
> OpenFlow è un'**API standard** che permette a un controller esterno di leggere e modificare la flow table di uno switch. Il controller — un processo software su un server normale — può aggiungere, modificare o rimuovere regole in risposta a eventi di rete.

### Applicazioni pratiche

**Firewall sandwich:** si inserisce un firewall L7 tra due switch. Il primo switch reindirizza ogni nuovo flusso attraverso il firewall; quando il firewall approva il flusso, il controller OpenFlow aggiorna la flow table dello switch per far bypassare il firewall ai pacchetti successivi dello stesso flusso. Risultato: si ispeziona solo l'inizio del flusso, il resto transita alla massima velocità.

**Mirroring e honeypot:** OpenFlow permette di copiare selettivamente il traffico su una porta di monitoraggio (per un sistema IDS) o di redirigere traffico sospetto verso un honeypot — un sistema esca che simula un target reale per catturare e studiare gli attaccanti.

> [!note] Stato attuale di OpenFlow
> 
> Nato con grandi ambizioni di "open networking", 15 anni dopo OpenFlow è principalmente uno strumento di ricerca e viene usato in casi specifici. La maggior parte dei professionisti non lo usa mai. È comunque importante conoscerne l'esistenza e il principio.

---

## Latenza in Ethernet

Bandwidth e latenza sono i due parametri fondamentali che governano le prestazioni di rete. La latenza si misura in diversi modi:

- **Serialization latency**: tempo per mettere i bit sul cavo. Con 1 Gigabit era ~12 µs; con le tecnologie moderne siamo nell'ordine di **300 ns**.
- **Propagation latency**: tempo di propagazione del segnale sul cavo. A 10 metri siamo ~50 ns, trascurabile nella maggior parte dei casi.
- **Switch latency** (cut-through): tempo di attraversamento di uno switch. I chipset Broadcom Trident/Tomahawk sono tipicamente tra **400 e 700 ns**.
- **End-to-end con TCP**: il protocollo TCP aggiunge overhead di framing, finestre di congestione, ACK, ecc. La latenza tipica di uno stream TCP è di circa **70 µs** — ordini di grandezza superiore al solo hardware.

> [!tip] Intuizione chiave
> 
> Ethernet in sé è **low latency**. TCP non lo è. Quando si sente dire che "Ethernet non è adatto all'HPC perché ha troppa latenza", il problema è quasi sempre il protocollo TCP sopra, non il mezzo fisico.

---

## InfiniBand e RDMA: introduzione

### Perché InfiniBand

Quando il 1 Gigabit Ethernet aveva latenza di 12 µs, era chiaramente inadeguato per applicazioni HPC (High Performance Computing) dove il pattern computazionale è _calcola → comunica → calcola → comunica_ in cicli molto stretti. InfiniBand è nato per rispondere a questa esigenza.

> [!definition] InfiniBand
> 
> InfiniBand è uno standard di interconnessione progettato per HPC, con latency di **1-2 µs** end-to-end (confrontare con i 70 µs di TCP su Ethernet). La MTU di un pacchetto InfiniBand è di **2 GB** — enormemente più grande rispetto ai 9 KB dei jumbo frame Ethernet. Molte funzioni che in Ethernet sono software sono implementate direttamente in silicio.

InfiniBand è stato a lungo dominato da **Mellanox**, un'azienda israeliana acquisita da **Nvidia** nel 2020. Nvidia ora usa questa tecnologia per la connessione ad alta velocità tra GPU nei cluster di training AI (fabric NVLink/NVSwitch).

### RDMA e RoCE

> [!definition] RDMA — Remote Direct Memory Access
> 
> RDMA permette a un host di rete di scrivere direttamente nella memoria di un altro host **senza coinvolgere la CPU del destinatario**. Analogo alla DMA locale (il meccanismo con cui un disco scrive in RAM senza impegnare la CPU), ma attraverso la rete.

Questo elimina drasticamente la latenza software: non c'è interrupt, non c'è context switch, non c'è copia di dati. La latenza risultante è paragonabile a quella dell'hardware di rete.

Poiché InfiniBand era costoso e richiedeva hardware dedicato, Mellanox ha proposto **RoCE** (_RDMA over Converged Ethernet_):

> [!definition] RoCE — RDMA over Converged Ethernet
> 
> RoCE implementa RDMA su Ethernet, sfruttando le estensioni di QoS (ETS e PFC) per garantire l'affidabilità necessaria. È supportato nativamente su Linux e Windows, ed è oggi lo standard per HPC su Ethernet.

> [!abstract] Dove siamo oggi
> 
> InfiniBand rimane in uso nei cluster HPC tradizionali per la latenza e per la sua topologia ottimizzata (fat tree senza oversubscription). RoCE/RDMA ha eroso parte del suo vantaggio portando latenze simili su Ethernet. Nella prossima lezione si esaminerà più in dettaglio la topologia **fat tree** (_full fat tree_) usata in InfiniBand, che garantisce banda costante indipendentemente dal numero di hop nella rete.

---

## Roadmap delle prossime lezioni

Dopo InfiniBand e le topologie HPC, il corso proseguirà con:

- Storage, drive e ridondanza (RAID e storage distribuito)
- Risalita sullo stack verso virtualizzazione e hypervisor
- Sicurezza di rete e firewall L7

> - Cos'è RoCE e in quale contesto è stato introdotto?