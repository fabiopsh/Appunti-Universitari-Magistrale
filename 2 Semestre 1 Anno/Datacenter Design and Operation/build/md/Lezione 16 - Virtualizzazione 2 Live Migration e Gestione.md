---
tags:
  - università/datacenter-design-and-operation
  - virtualizzazione
  - hypervisor
  - live-migration
  - cluster
  - vxlan
  - overlay-network
  - hyper-converged
data: 2026-05-08
lezione: "Virtualizzazione 2 — Live Migration e Gestione del Datacenter Virtuale"
professore: "Antonio Cisternino"
---
# Virtualizzazione 2 — Live Migration e Gestione del Datacenter Virtuale

La lezione riprende il filo della virtualizzazione affrontando i meccanismi interni dell'hypervisor, le operazioni che questo rende possibili — in particolare la **live migration** — e le conseguenze architetturali che queste capacità hanno avuto sull'intera industria del cloud. Il professore dimostra tutto in diretta su un cluster reale dell'Università di Pisa.

---

## Contesto storico: da IBM agli anni 2000

La virtualizzazione non è un'invenzione recente. Il sistema operativo **VM/CMS** di IBM, apparso negli anni '70, era già un sistema di virtualizzazione completo: permetteva di far girare multiple istanze indipendenti di un sistema monoprogrammato sullo stesso mainframe fisico. L'idea precede persino il concetto moderno di processo.

### Emulazione: il predecessore pratico

Prima che la virtualizzazione si affermasse, la soluzione dominante per eseguire software scritto per un'architettura diversa era l'**emulazione**. I Macintosh con CPU PowerPC, ad esempio, usavano un emulatore x86 per girare software Windows — più lento, ma funzionante. La logica dell'emulazione è concettualmente semplice:

> [!definition] Emulatore
>
> Un programma che implementa il ciclo *fetch-decode-execute* di una CPU bersaglio, interpreta ogni istruzione e emula l'effetto di ogni operazione I/O. Può eseguire codice di qualsiasi architettura su qualsiasi altra architettura, a patto di accettare un rallentamento significativo.

Il rallentamento deriva dal fatto che ogni ciclo della CPU emulata richiede molti cicli della CPU fisica per essere simulato. Storicamente era accettabile solo per emulare sistemi molto vecchi — la Legge di Moore forniva il margine di velocità necessario a compensare l'inefficienza. Oggi strumenti come **JSLinux** di Fabrice Bellard dimostrano che persino sistemi complessi (Linux, Windows 2000) possono essere emulati all'interno di un browser, incluse CPU di architetture diverse da quella del dispositivo host.

> [!note] Bug fedeli
>
> Un emulatore non deve implementare solo la specifica ufficiale di una CPU, ma anche i suoi bug. Il software reale spesso si affida a comportamenti non documentati o a quirk storici dell'hardware: un emulatore che non li riproduce non riesce a far girare quel software correttamente.

### La nascita di VMware (1997) e la virtualizzazione x86

Nel 1997, quando VMware fu fondata, le CPU multi-core non esistevano ancora. Il problema che spinse a creare il primo hypervisor era pragmatico: un commesso viaggiatore doveva dimostrare architetture client-server senza connessione internet affidabile. La soluzione fu eseguire sia il client che il server sulla stessa macchina laptop — ma in modo isolato.

Emulare una CPU x86 sopra un'altra CPU x86 è tecnicamente possibile ma lento. L'insight chiave di VMware fu diverso: se il codice gira già sulla stessa architettura, non serve emulare le istruzioni — basta trovare un meccanismo per *preemptare* il codice della macchina virtualizzata e lasciarlo girare direttamente sulla CPU fisica, intervenendo solo quando necessario (accessi privilegiati, I/O, cambio di contesto).

![Diagramma Mermaid](images/mermaid-lezione-16-virtualizzazione-2-live-migration-e-gestione-01.png)
*Fig. — Emulazione vs virtualizzazione: il discriminante è la compatibilità di architettura.*

---

## Perché la virtualizzazione si è affermata

L'esplosione della virtualizzazione nei datacenter avviene attorno al **2003-2004**, per una ragione strutturale: l'hardware cresceva più velocemente del software. I server dell'epoca erano già troppo potenti per le applicazioni disponibili. Un web server o un mail server, essendo workload **IO-bound**, teneva la CPU occupata una piccola percentuale del tempo: il processore aspettava il disco o la rete, non elaborava.

In questo contesto, far girare una singola applicazione per server era uno spreco enorme. La virtualizzazione offriva la risposta: eseguire decine di servizi isolati sulla stessa macchina fisica, sfruttando i core altrimenti inattivi.

> [!tip] Perché non semplici processi?
>
> I processi condividono sistema operativo, librerie e kernel. Due applicazioni che richiedono versioni diverse della stessa libreria non possono coesistere facilmente. Una patch di sicurezza a un componente richiede il riavvio dell'intera macchina. Una compromissione del web server può propagarsi al database. La VM risolve tutti e tre i problemi grazie all'**isolamento completo**.

Il secondo catalizzatore fu l'arrivo delle **CPU multi-core** attorno al 2006. Il software dell'epoca era quasi tutto single-threaded — il multithreading era considerato programmazione avanzata. La virtualizzazione diventò il modo principale per sfruttare i core aggiuntivi senza riscrivere le applicazioni: ogni VM occupava uno o più core separati.

L'overhead introdotto dall'hypervisor moderno è stimato attorno al **10-15%** — ben speso dato il ritorno in termini di isolamento, flessibilità e gestibilità.

---

## L'hypervisor per ambienti server

Il software di virtualizzazione desktop (VirtualPC, VMware Workstation) era pensato per eseguire sistemi operativi con interfaccia grafica, audio, USB. L'**hypervisor** per server è un sistema completamente diverso: nessuna console grafica, gestione solo via rete, ottimizzato per eseguire decine o centinaia di VM headless.

### La vCPU e la gestione dell'instruction set

Ogni VM riceve una o più **vCPU** — CPU virtuali che mappano sui core fisici del server. La vCPU non è semplicemente un core fisico dedicato: è un'astrazione configurabile. In particolare, l'hypervisor può dichiarare alla VM un sottoinsieme delle istruzioni disponibili sulla CPU fisica.

Questo è cruciale per la **live migration**. Se una VM utilizza istruzioni AVX-512 disponibili solo su alcuni modelli Intel, non può essere spostata su un server con una CPU più vecchia che non supporta quelle istruzioni. Configurando la vCPU per esporre solo le istruzioni comuni al set minimo tra sorgente e destinazione, si garantisce la portabilità.

Analogamente, l'hypervisor può configurare la topologia **NUMA** percepita dalla VM: quanti socket, quanti nodi NUMA, quanta memoria per nodo. La VM non vede la topologia reale del server fisico — vede solo ciò che l'hypervisor le mostra.

### Due sistemi operativi all'avvio di Windows

Un fatto poco noto: Windows, all'avvio, lancia **due sistemi operativi**, non uno. Il primo è un micro-OS molto piccolo, senza console, che prende il controllo dell'hardware dedicato alla protezione delle chiavi crittografiche — quelle usate per BitLocker, TPM, transazioni finanziarie. Questo micro-OS è chiamato internamente **Secure World** (o Virtual Secure Mode). Solo dopo averlo avviato, lancia Windows normale, che gira accanto a lui in modalità virtualizzata.

> [!example] Perché due OS?
>
> Il software non è perfetto. Se un attaccante ottiene privilegi kernel su Windows, normalmente può leggere qualsiasi area di memoria, incluse le chiavi crittografiche. Con il modello a due OS, le chiavi risiedono nel Secure World, inaccessibile anche al kernel Windows. Il Secure World è esposto solo attraverso API ben definite, rendendo molto più difficile l'esfiltrazione.

Lo stesso principio vale per **Windows Subsystem for Linux (WSL2)**: anche qui gira un kernel Linux completo all'interno di Windows, sfruttando le stesse tecniche di virtualizzazione. Sul laptop del professore (ARM con processore Apple) gira anche un layer di emulazione x86 integrato in Windows, dimostrando la coesistenza di tre livelli: ARM nativo, x86 emulato, Linux virtualizzato.

---

## Operazioni fondamentali sulle VM

### Pause e Resume

Un hypervisor può fermare completamente l'esecuzione di una VM in qualsiasi momento. Questo è possibile perché un sistema operativo è, in ultima analisi, codice che viene eseguito dal ciclo fetch-execute. Se si interrompe quel ciclo e si conserva lo stato — i registri della CPU — il sistema operativo non ha alcun modo di accorgersi che il tempo si è fermato. Alla ripresa, riprende esattamente da dove si era fermato.

> [!definition] Stato completo di una VM
>
> Lo stato completo di una VM è composto da tre elementi: (1) i **registri della CPU** inclusi quelli di sistema, (2) il contenuto della **memoria RAM** allocata alla VM, (3) lo stato del **disco virtuale**. Conservare tutti e tre equivale a poter ricreare fedelmente la VM in qualsiasi momento futuro.

### Snapshot

Uno **snapshot** è una fotografia del stato completo della VM in un istante dato. Tecnicamente si realizza con una combinazione di:
- Copia dei registri CPU
- Copia della memoria (o riferimento CoW — Copy-on-Write)
- Disco differenziale: da quel momento in poi, le scritture sul disco vanno in un file differenziale separato; il disco originale resta intatto come "base"

L'insieme di snapshot forma una catena che permette di tornare a qualsiasi punto precedente nel tempo, esattamente come i commit di un sistema di versionamento.

### Integration Services

L'hypervisor espone alla VM un insieme di servizi di integrazione che vanno oltre la semplice emulazione hardware:

- **Sincronizzazione del clock**: la VM usa il clock dell'host. Cruciale perché Kerberos (il protocollo di autenticazione usato in Active Directory e nei datacenter) richiede che tutti i sistemi abbiano lo stesso orario con margine inferiore a 5 minuti. Un clock desincronizzato impedisce l'autenticazione.
- **Heartbeat**: la VM invia periodicamente un segnale all'hypervisor. Se il heartbeat cessa, l'hypervisor sa che il kernel della VM è bloccato e può intervenire con un riavvio forzato — fondamentale per la business continuity.
- **Shutdown graceful**: l'hypervisor può inviare alla VM il segnale equivalente alla pressione del tasto power, permettendo uno spegnimento pulito anziché un kill brutale.
- **Backup senza contention**: sospendendo brevemente la VM, l'hypervisor può eseguire un backup coerente del disco senza race condition, anche con il sistema in esecuzione.

---

## Live Migration

La **live migration** è probabilmente la funzionalità più importante introdotta dalla virtualizzazione nell'industria del datacenter. Permette di spostare una VM da un server fisico a un altro **mentre è in esecuzione**, con un'interruzione percepibile dell'ordine di qualche millisecondo — del tutto compatibile con i normali glitch di rete.

### Cold migration vs live migration

La *cold migration* è concettualmente semplice: si spegne la VM, si copiano i file del disco e della memoria sul server destinazione, si riavvia. La VM è offline per tutta la durata della copia.

La *live migration* mantiene la VM operativa durante quasi tutta la fase di trasferimento. Il problema tecnico è che la VM continua a modificare memoria e disco durante la copia, rendendo impossibile ottenere uno snapshot coerente senza un intervento coordinato.

![Diagramma Mermaid](images/mermaid-lezione-16-virtualizzazione-2-live-migration-e-gestione-02.png)
*Fig. — Il processo di live migration in sei fasi: pre-copy con dirty tracking, stop-copy, riavvio e cleanup.*

### Fase 1: Pre-copy con dirty page tracking

La prima fase è la più lunga. L'hypervisor comincia a copiare memoria e disco verso il server destinazione mentre la VM continua a girare. Durante questa copia, ogni pagina di memoria (o blocco di disco) modificata dalla VM viene marcata come **dirty**: deve essere ricopiata perché il valore già trasferito è diventato obsoleto.

Il meccanismo di **page fault** dell'hypervisor è lo strumento chiave: quando la VM prova a scrivere in una pagina già inviata alla destinazione, si genera un fault che permette all'hypervisor di aggiornare il tracking.

Con il passare del tempo, se la VM non è troppo "write-intensive", il set di pagine dirty si riduce: la maggior parte della memoria è già stata copiata e non è stata rimodificata. A questo punto si è pronti per la fase finale.

### Fase 2: Stop, copy del working set, riavvio

Quando il dirty set è sufficientemente piccolo — ogni sistema ha le proprie soglie — l'hypervisor **ferma la VM per un brevissimo momento**. In questo fermo:
1. Copia i registri CPU
2. Copia le restanti pagine dirty (il *working set attivo*)
3. Trasferisce il tutto alla destinazione

Dopodiché, la VM viene **riavviata sulla destinazione**. Il fermo dura tipicamente pochi millisecondi — paragonabile alla latenza di un roundtrip di rete, o alla preemption che qualsiasi sistema operativo subisce normalmente durante lo scheduling.

### Fase 3: Gestione della rete — il problema dell'ARP cache

Quando la VM si sposta su un altro host fisico, il suo indirizzo MAC (e IP) rimangono invariati — vanno con la VM. Ma i switch fisici mantengono una **ARP cache** che associa ogni MAC address alla porta fisica su cui lo hanno visto l'ultima volta. Dopo lo spostamento, quella cache è obsoleta: i pacchetti verrebbero ancora inviati alla porta del vecchio host.

La soluzione è un meccanismo a due livelli:

1. Il **virtual switch della destinazione** invia un **gratuitous ARP** — un messaggio ARP non richiesto che annuncia "il MAC X è ora raggiungibile da questo switch". Questo forza gli switch della rete a invalidare immediatamente le entry stantie.

2. Nel breve intervallo tra la migrazione e la propagazione del gratuitous ARP, il virtual switch della sorgente — che è un software a conoscenza della migrazione — fa da **proxy**: i pacchetti che arrivano ancora alla sorgente vengono inoltrati alla destinazione anziché andare persi.

Il risultato pratico è **zero packet loss** durante la migrazione.

![Diagramma Mermaid](images/mermaid-lezione-16-virtualizzazione-2-live-migration-e-gestione-03.png)
*Fig. — Gestione della rete durante la live migration: forwarding proxy + gratuitous ARP eliminano la perdita di pacchetti.*

---

## Il Cloud come conseguenza della live migration

La live migration ha cambiato le regole del gioco nell'industria IT. Prima di essa, il software era legato all'hardware su cui girava: aggiornare o sostituire un server significava downtime. Con la live migration, il legame è spezzato.

> [!tip] Perché si chiama "Cloud"?
>
> Il termine "cloud" è metaforico: le nuvole in cielo sono un insieme di vapore acqueo che non si può localizzare con precisione. Analogamente, nel cloud non si sa — e non importa sapere — su quale hardware specifico girano le proprie risorse. Il cloud provider può muoverle liberamente, e finché il servizio funziona, per il cliente è equivalente.

La live migration è la tecnologia abilitante di questa astrazione. Un server con un disco rotto? Le VM vengono migrate su altri host in pochi secondi, il server viene spento, sostituito, riavviato — senza che nessun utente se ne accorga.

Il professore cita l'esempio concreto del cluster dell'Università di Pisa: operativo da 8 anni, il primo cluster di 10 nodi è stato completamente decommissionato e nessuno ha notato, perché le VM sono state spostate gradualmente con live migration.

### Container vs VM per la mobilità

I **container** — a differenza delle VM — non possono essere migrati a caldo con la stessa facilità. Un processo con il suo stato interno (socket aperti, memoria allocata, descrittori di file) non può essere "congelato" e ripristinato su un altro host senza serializzare esplicitamente tutto lo stato. Quella tecnologia (CRIU per Linux) esiste ma è complessa e non universalmente supportata.

Per questo motivo, il pattern dominante nei datacenter è eseguire **container dentro VM**: si ottiene il meglio di entrambi i mondi. I container forniscono leggerezza e avvio rapido per i workload; la VM fornisce l'isolamento hardware e la mobilità tramite live migration.

---

## Software di gestione: il layer orchestrator

Un singolo hypervisor gestisce le VM di un singolo host. Ma un datacenter ha decine o centinaia di host. Serve un software che coordini tutti gli hypervisor da un unico punto di controllo.

Per gli ambienti Microsoft, questo software è **System Center Virtual Machine Manager (SCVMM)**. Per VMware, **vCloud Foundation**. Questi strumenti permettono di vedere il datacenter come un unico pool di risorse, eseguire live migration attraverso un'interfaccia grafica o API, monitorare tutti i cluster, configurare le reti virtuali.

Esistono alternative open source: **OpenStack** (più orientato alle API, meno integrato), **Proxmox** (più simile agli strumenti commerciali per usabilità). Il professore sottolinea che la scelta tra open source e commerciale nel datacenter non è solo tecnica:

> [!warning] Open source nel datacenter: una riflessione critica
>
> Avere il codice sorgente non significa poter risolvere autonomamente ogni problema. Quando 300 macchine virtuali vanno offline per un'inconsistenza nello storage, il tempo a disposizione per il debug è zero. In quel caso, avere un contratto di supporto con ingegneri che conoscono il prodotto dall'interno vale il suo costo. Il professore descrive un incidente reale: la risoluzione ha richiesto 6 ore di escalation su tre continenti (India → Giappone → Messico), dove un esperto ha usato uno strumento open source per analizzare i metadati del filesystem e fornire il comando esatto per ripristinare la coerenza. L'alternativa senza supporto sarebbe stata 4 giorni di restore da backup.

---

## Architettura a cluster

Un **cluster** è un insieme di server che condividono risorse e si coordinano per garantire alta disponibilità. Ogni nodo contribuisce con CPU, memoria, storage e rete al pool condiviso. L'hypervisor di ciascun nodo comunica con gli altri per sapere quante risorse sono disponibili, dove stanno le VM, e cosa fare in caso di guasto.

![Diagramma Mermaid](images/mermaid-lezione-16-virtualizzazione-2-live-migration-e-gestione-04.png)
*Fig. — Il datacenter come insieme di cluster gestiti da un layer di management centralizzato.*

### Limiti dimensionali del cluster

I cluster non crescono indefinitamente. Il limite pratico è attorno a **32 nodi**. La ragione è la complessità della comunicazione intra-cluster: ogni nodo deve tenersi aggiornato sullo stato di tutti gli altri. Il pattern di comunicazione è quasi **quadratico** nel numero di nodi: raddoppiare i nodi quadruplica quasi la quantità di messaggi di heartbeat e sincronizzazione dello stato. Oltre una certa dimensione, il coordinamento introduce latenze non accettabili.

Il **master role** all'interno del cluster è floating: un nodo assume il ruolo di master, ma non è fisso. Se il master diventa irraggiungibile, gli altri nodi usano un protocollo di consenso per eleggerne uno nuovo. Questo evita il single point of failure che esisterebbe con un master fisso.

Per scalare oltre i limiti di un singolo cluster, si usano **multipli cluster** coordinati dallo stesso management layer.

> [!note] Prerequisito per la live migration intra-cluster
>
> Tutti i nodi di un cluster devono essere connessi alle **stesse reti**. Se una VM è connessa a una specifica VLAN, quella VLAN deve essere disponibile su ogni host del cluster — altrimenti la live migration fallisce perché la VM non può mantenere la sua connettività.

---

## Storage: Hyper-converged vs SAN

Il modo in cui lo storage è collegato alle VM ha implicazioni di performance significative.

### Hyper-converged infrastructure (HCI)

Nell'architettura **hyper-converged**, i dischi fisici di ogni server fanno parte di un pool di storage distribuito. I file delle VM girano fisicamente sui dischi del server su cui la VM è in esecuzione — o sui server più vicini nella rete del cluster. Il traffico tra vCPU e vDisk viaggia sul bus **PCIe** interno al server, non sulla rete.

Il software che gestisce il pool distribuito (S2D su Microsoft, vSAN su VMware) mantiene tipicamente **3 copie** di ogni blocco di dati su nodi diversi. Questo garantisce la sopravvivenza al guasto di uno o due nodi.

**Vantaggio**: bandwidth massima, latenza minima.
**Svantaggio**: si usa solo 1/3 dello spazio disco totale (efficienza 33%). Le licenze software (Microsoft S2D, VMware vSAN) sono costose — talvolta più del hardware stesso.

### SAN (Storage Area Network)

Nella configurazione SAN, lo storage è centralizzato in un array dedicato, raggiungibile via FC o iSCSI. I dischi delle VM risiedono sulla SAN, non sui server.

**Vantaggio**: spazio usato più efficiente (RAID tradizionale, meno overhead di replica); licenze software spesso assenti o più economiche.
**Svantaggio**: la SAN è un collo di bottiglia. La rete FC o iSCSI ha larghezza di banda inferiore al PCIe. Con carichi I/O elevati (database), si nota.

> [!warning] L'impatto dell'AI sui costi dello storage
>
> Il costo degli storage media (SSD, NVMe) è aumentato significativamente a causa della domanda AI. Questo ha reso ancora più costosa la replica ×3 dell'HCI, spingendo alcune organizzazioni verso la SAN nonostante le limitazioni tecniche.

---

## Virtual Networking e Overlay Networks

### La complessità a strati

Ogni VM ha una o più **NIC virtuali** (vNIC). Queste vNIC sono connesse a un **virtual switch** software che gira sull'hypervisor host. Il virtual switch a sua volta è connesso alle NIC fisiche del server, che sono connesse agli switch fisici della rete.

Ogni strato aggiunge complessità al troubleshooting: seguire il percorso di un pacchetto richiede di conoscere la configurazione del virtual switch, le VLAN tagate sulle porte fisiche, e la topologia dello switch fisico.

### Il limite delle VLAN e VXLAN

Le VLAN tradizionali (IEEE 802.1Q) hanno un identificatore a 12 bit: al massimo **4096 VLAN** distinte su tutta la rete. In un datacenter con milioni di tenant virtuali, questo è insufficiente.

La soluzione è **VXLAN** (*Virtual eXtensible LAN*): un protocollo di overlay che incapsula frame Ethernet layer 2 all'interno di pacchetti UDP layer 3. L'identificatore VXLAN è a 24 bit: circa **16 milioni** di reti virtuali distinte.

![Diagramma Mermaid](images/mermaid-lezione-16-virtualizzazione-2-live-migration-e-gestione-05.png)
*Fig. — VXLAN: frame Ethernet tra VM incapsulati in UDP/IP, permettendo LAN virtuali indipendenti dall'infrastruttura fisica.*

> [!definition] Overlay Network
>
> Una rete logica costruita sopra una rete fisica esistente, senza richiedere modifiche all'infrastruttura fisica. Il traffico dell'overlay appare come normale traffico IP/UDP per gli switch fisici, ma trasporta frame di reti virtuali separate. Questo permette di creare LAN isolate per tenant diversi su qualsiasi numero di server nel datacenter.

L'overlay network elimina la necessità di configurare VLAN sugli switch fisici per ogni nuovo tenant — operazione manuale, lenta, e limitata a 4096 combinazioni. Con VXLAN, la configurazione avviene interamente a livello software nel virtual switch, da un pannello centralizzato.

### Ridondanza delle NIC

Ogni server in un cluster è tipicamente connesso con **due NIC** alla rete di produzione (più una terza per il management). Le due NIC vanno a due switch fisici diversi — spine-leaf. Se uno switch fisico cade, il traffico fluisce automaticamente attraverso l'altro link. Il virtual switch gestisce questa failover in modo trasparente per le VM.

---

## Aggregazione delle risorse e visione del datacenter

Mettendo insieme tutti i pezzi, un datacenter virtualizzato si presenta come:

- Un insieme di **cluster** di 8-32 host ciascuno
- Ogni host contribuisce CPU, RAM, storage e network al pool del cluster
- I pool di cluster multipli sono gestiti da un unico management layer
- Le VM vengono allocate *draw*ando dalle risorse del pool
- La live migration permette di bilanciare il carico, fare manutenzione hardware, e rispondere ai guasti in modo trasparente

La virtualizzazione ha completamente **decoupled il software dall'hardware**: il software non sa su quale server fisico gira, e non ha bisogno di saperlo. Il cloud è la manifestazione estrema di questo principio — il software non sa nemmeno in quale datacenter fisico gira.

> [!abstract] Sintesi
>
> La virtualizzazione non è solo un modo per far girare più OS sulla stessa macchina. È l'infrastruttura tecnologica che ha reso possibile il cloud computing: la live migration garantisce mobilità del workload; il virtual switch e VXLAN garantiscono portabilità della rete; l'hyper-convergence massimizza le prestazioni I/O. Il costo pagato — 10-15% di overhead CPU, spazio disco triplicato, licenze software — è ampiamente giustificato dai vantaggi operativi: manutenzione hardware senza downtime, disaster recovery automatico, isolamento completo tra tenant.

