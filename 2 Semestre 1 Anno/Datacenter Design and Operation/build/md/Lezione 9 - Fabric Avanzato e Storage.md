
# Fabric Avanzato e Introduzione allo Storage

## Workload e architettura del datacenter

Prima di parlare di fabric ad alte prestazioni, è necessario capire *perché* esistono. La scelta dell'architettura di rete di un datacenter — larghezza di banda, latenza, topologia — non è universale: è guidata dal tipo di workload che il sistema deve eseguire. Il professore distingue quattro categorie fondamentali.

**HPC** (*High Performance Computing*) è la categoria più antica: si tratta di problemi computazionalmente enormi — simulazioni fisiche, fluidodinamica, modellazione sismica — che un singolo computer non può risolvere in tempo utile. La soluzione è decomporre il problema in sotto-problemi assegnati a nodi omogenei (tutti con le stesse risorse), che collaborano comunicando frequentemente. Il classico esempio è ENI che simula la propagazione delle onde sismiche nel sottosuolo tramite elementi finiti per individuare giacimenti petroliferi senza trivellare: il risultato arriva in sei mesi usando migliaia di CPU, mentre con un singolo computer richiederebbe secoli.

**Cloud** è il modello inverso: qui il problema è piccolo — una singola applicazione web, un microservizio — e il server è talmente potente da poter ospitare decine o centinaia di macchine virtuali contemporaneamente. La relazione è uno-a-molti: un computer, molti problemi. Questo modello è stato possibile perché per vent'anni la potenza computazionale è cresciuta molto più velocemente della domanda software.

**Big Data** è orientato all'elaborazione di quantità enormi di dati, tipicamente con dischi meccanici: la latenza d'accesso allo storage (millisecondi) è così dominante che la latenza di rete diventa irrilevante. Non ha senso ottimizzare la rete se il collo di bottiglia è il disco.

**AI/ML** è la categoria che ha recentemente rotto l'equilibrio del cloud: si tratta di workload che, come l'HPC, richiedono uno o più server dedicati per un singolo calcolo. Il professore distingue due sotto-categorie con requisiti molto diversi — **training** e **inference** — e sottolinea che anche i laptop moderni montano oggi un NPU (*Neural Processing Unit*) ottimizzato per l'inferenza locale.

> [!tip] Intuizione chiave
>
> La latenza di rete conta solo quando la computazione è *memory-bound* e *sincronizzata*. In HPC e AI training ogni nodo deve aspettare gli altri a ogni passo: anche 2 ms di latenza di rete moltiplicati per milioni di iterazioni diventano il collo di bottiglia. In Big Data il disco è così lento (ms) che la rete smette di importare.

---

## InfiniBand

### Contesto storico e motivazione

Quando InfiniBand fu introdotto, Ethernet era ancora a 1 Gigabit per secondo. Per aggregare 5 Gbps su un server si usavano 4-5 cavi Ethernet. InfiniBand offriva in un singolo cavo ~80 Gbps — da qui il nome, che richiamava la *larghezza di banda infinita*. Oggi il confronto con Ethernet è molto meno netto dal punto di vista della banda, ma InfiniBand mantiene un vantaggio significativo in **latenza**.

> [!definition] InfiniBand
>
> Fabric di rete ad alte prestazioni progettata per ambienti HPC. Fisicamente simile a Ethernet (connettori SFP/QSFP), radicalmente diversa a livello di protocollo. Originariamente sviluppata da Mellanox, oggi di proprietà NVIDIA.

### Caratteristiche del protocollo

La differenza cruciale rispetto a Ethernet non è nei cavi, ma nel protocollo:

- **Pacchetti fino a 2 GB**: dal punto di vista del software host, si può inviare un pacchetto da 2 gigabyte come unità atomica. Il fabric si occupa internamente della segmentazione e riassemblaggio, ma l'applicazione non deve preoccuparsene.
- **16 classi di priorità** (*QoS* nativo): è possibile classificare il traffico con granularità fine.
- **IP over IB**: esiste un adattatore per far girare TCP/IP sopra InfiniBand, utile per la comunicazione *north-south* verso l'esterno, ma nessuno lo usa per comunicazioni interne al cluster.

La topologia tipica di un cluster InfiniBand è: **east-west su InfiniBand** (comunicazione tra nodi del cluster), **north-south su Ethernet** (comunicazione con l'esterno). Il nodo di testa del cluster (*head node*) è l'unico connesso a entrambe le reti.

Uno switch InfiniBand può arrivare a 128 porte in un singolo chassis: questo permette di implementare in hardware un'interconnessione completamente piatta con latenza garantita sotto i 3 microsecondi tra qualsiasi coppia di porte.

### Top500: lo stato dell'arte

Il *Top500* è la classifica dei 500 supercomputer più potenti al mondo. Tutti i sistemi nelle prime posizioni usano InfiniBand o Slingshot. Il professore cita come esempi:

| Sistema | Potenza | Note |
|---------|---------|------|
| Frontier | ~29 MW, ~11M core | AMD + GPU Instinct, Slingshot (HPE) |
| Eagle | — | Microsoft Azure, NVIDIA H100, InfiniBand — architettura di riferimento per AI |
| Leonardo | — | Italia, top 10 |
| Jupiter | — | Germania, primo sistema europeo exascale |

**Slingshot** (HPE/Cray) è Ethernet "su steroidi": compatibile Ethernet a livello fisico, ma con ottimizzazioni di protocollo per bassa latenza. **InfiniBand** (NVIDIA) è il protocollo nativo per HPC. I due dominano il segmento dei supercomputer.

---

## MPI e RDMA

### MPI: Message Passing Interface

Prima di parlare di RDMA, è fondamentale capire il contesto del software HPC. Quasi tutto il codice HPC distribuito è scritto usando **MPI** (*Message Passing Interface*), una libreria C di ~35 anni che esprime la computazione distribuita come scambio di messaggi tra nodi identificati da un numero progressivo (non da indirizzi di rete).

> [!tip] Intuizione chiave
>
> MPI astrae completamente il fabric sottostante. L'applicazione invia "un messaggio al nodo 4" e MPI si occupa di tradurre questo in chiamate alle primitive di rete specifiche del fabric disponibile — InfiniBand, Slingshot, Ethernet. Questo è il motivo per cui la community HPC ha potuto cambiare fabric multiple volte senza riscrivere il codice applicativo.

### RDMA: Remote Direct Memory Access

**RDMA** estende il concetto di DMA (*Direct Memory Access*) — il meccanismo che permette a una periferica di leggere/scrivere direttamente in RAM senza coinvolgere la CPU — attraverso la rete.

Il meccanismo sfrutta le schede di rete *converged NIC*, collegate al bus PCIe: queste schede possono leggere e scrivere nella RAM del server remoto direttamente, senza passare per il sistema operativo del destinatario.

> [!warning] Implicazioni di sicurezza
>
> RDMA bypassa il sistema operativo: la scheda di rete ha accesso diretto alla memoria. Questo introduce rischi di sicurezza non banali che vanno considerati nel design del sistema.

RDMA è diventato lo standard *de facto* per la comunicazione a bassa latenza in ambienti distribuiti. Dal 2016, anche Windows implementa **RoCE** (*RDMA over Converged Ethernet*), portando RDMA anche su Ethernet standard.

### Confronto di latenza

| Tecnologia | Latenza tipica |
|-----------|---------------|
| InfiniBand nativo (RDMA) | 1–3 μs |
| RoCE (RDMA over Converged Ethernet) | 1.3–5 μs |
| IP over InfiniBand | 5–15 μs |
| TCP/IP su Ethernet | 20–70+ μs |

Il dato più significativo: aggiungere il protocollo IP sopra InfiniBand **moltiplica per 4-5x la latenza** rispetto a RDMA nativo. TCP/IP è ulteriormente peggiore. Questo spiega perché per HPC nessuno usa TCP/IP interno al cluster.

> [!note] L'inventore di TCP/IP e i buffer
>
> Il professore cita un aneddoto: uno degli autori di TCP/IP, analizzando la lentezza della propria rete domestica, scoprì che il problema era il buffering introdotto in ogni switch e router. TCP/IP era stato progettato per essere *adattivo* e senza buffer: l'accumulo di buffer nella rete moderna ne snatura il comportamento. L'autore commentò che, se dovesse progettare il protocollo oggi, lo farebbe diversamente.

---

## Overbooking e topologia Full Fat Tree

### Overbooking

In qualsiasi rete commutata esiste il concetto di **overbooking**: il traffico aggregato generabile dai nodi di accesso supera la capacità del collegamento verso lo strato superiore.

> [!example] Esempio concreto
>
> Uno switch con 48 porte da 25 Gbps e 6 porte uplink da 100 Gbps. Traffico massimo east-west: 48 × 25 = 1.200 Gbps. Uplink totale: 6 × 100 = 600 Gbps. Il rapporto di overbooking è **2:1**: i nodi possono generare il doppio di quanto il fabric possa trasmettere verso lo spine. Questo è normale e atteso — la rete si adatta.

### Full Fat Tree

Per applicazioni HPC dove la latenza e il throughput non-bloccante sono requisiti, esiste una topologia specifica: il **Full Fat Tree**.

> [!definition] Full Fat Tree
>
> Topologia di rete ad albero in cui la banda dell'uplink di ogni nodo è uguale alla *somma* delle bande dei link del sottoalbero che connette. Il risultato è una rete **non-bloccante**: ogni nodo può trasmettere a piena velocità verso qualsiasi altro nodo senza contesa.

![Topologia Full Fat Tree: albero non-bloccante con uplink uguale alla somma dei downlink](images/Fat-tree-92c71e.png)
*Fonte: Wikimedia Commons — Topologia Fat Tree: ogni nodo intermedio ha una banda uplink pari alla somma delle bande dei link verso le foglie. Nessun punto di strozzatura nella rete.*

In pratica, con link aggregation moderna, si implementa sommando più cavi standard in un link logico. La regola è semplice: se voglio che metà delle porte serva i server (east-west) e metà vada verso lo spine (north-south), la banda dei due lati è identica — nessun overbooking.

Il Full Fat Tree ha un costo elevato (gli switch agli strati superiori devono gestire bande crescenti), ma è la topologia usata per supercomputer e cluster HPC dove il throughput non-bloccante è non negoziabile.

> [!note] Fat Tree vs Spine-and-Leaf
>
> L'architettura Spine-and-Leaf vista nelle lezioni precedenti *ricorda* il Fat Tree, ma tipicamente introduce overbooking. Il Fat Tree è la versione non-bloccante dello Spine-and-Leaf, applicata quando il costo è giustificato dalle prestazioni richieste.

---

## Fibre Channel: il fabric per lo storage

Oltre a Ethernet e InfiniBand, nei datacenter esiste un terzo tipo di fabric dedicato allo storage: il **Fibre Channel**.

> [!definition] Fibre Channel
>
> Fabric di rete ottico dedicato alla connessione host-storage. Fisicamente simile a Ethernet e InfiniBand (fibra ottica, connettori analoghi), ma con protocolli completamente diversi orientati all'accesso allo storage.

L'architettura tipica è: server con scheda **HBA** (*Host-Based Adapter*, l'equivalente Fibre Channel della NIC) → fabric Fibre Channel (switch FC) → storage array (un sistema con molti dischi interni). L'HBA emula un disco locale, ma i dati risiedono sullo storage array.

Il protocollo trasportato da Fibre Channel è **SCSI** (o più precisamente FCP — Fibre Channel Protocol che incapsula SCSI), che porta a una curiosità storica importante.

Esiste anche **FCoE** (*Fibre Channel over Ethernet*), pensato come meccanismo di transizione per evitare di mantenere una rete FC separata. Il professore lo definisce "terrible" — non funziona bene ed è stato sostanzialmente abbandonato.

Il Fibre Channel è oggi **legacy**: molte installazioni esistenti lo usano ancora, ma i nuovi progetti preferiscono Ethernet o InfiniBand anche per lo storage.

---

## La storia dei protocolli di storage

Per capire perché Fibre Channel usa ancora SCSI, occorre ripercorrere la storia dei protocolli di accesso ai dischi.

### SCSI: 1979

**SCSI** (*Small Computer System Interface*) nasce nel 1979 come bus parallelo (cavo flat multi-connettore) per collegare più dispositivi di storage a un singolo controller, condividendo il costo del controller tra più dischi. La logica master/slave permetteva di gestire 2 dischi per controller (ATA) o molti di più (SCSI).

Sebbene la tecnologia fisica sia cambiata radicalmente, il **protocollo SCSI è sopravvissuto per 40 anni** grazie al principio di non dover riscrivere il software: ogni nuova tecnologia ha implementato SCSI come adattatore sopra nuovi mezzi fisici.

| Variante | Mezzo fisico | Note |
|---------|-------------|------|
| SCSI parallelo | Cavo flat | Originale 1979 |
| SAS | Seriale | Serial Attached SCSI |
| iSCSI | Ethernet/TCP | SCSI sopra Internet — alto overhead |
| FCP | Fibre Channel | SCSI sopra fibra ottica |
| SRP | InfiniBand | SCSI sopra RDMA |

### ATA → SATA

In parallelo a SCSI, il mondo PC sviluppò **ATA** (più economico) e poi **SATA** (Serial ATA), dominante nei dischi consumer fino a pochi anni fa.

### NVMe: la rivoluzione

**NVMe** (*Non-Volatile Memory Express*) rompe il paradigma: non è un protocollo di bus, è un protocollo direttamente sopra **PCIe** (*PCI Express*). Un SSD NVMe non è "un disco connesso a un controller" — è una scheda PCIe che si comporta come qualsiasi altra periferica del sistema.

> [!tip] Perché NVMe ha cambiato tutto
>
> Per decenni il software — database, filesystem, sistemi operativi, reti — è stato progettato con il presupposto che il disco fosse **lento** (millisecondi). Con NVMe la latenza scende a microsecondi. Il collo di bottiglia si sposta: SCSI, TCP/IP e altri protocolli che introducevano latenza trascurabile rispetto a un disco meccanico diventano improvvisamente il fattore limitante. Questo ha richiesto di ripensare quasi tutto il software di storage.

---

## Gerarchia dello storage

Il datacenter moderno mantiene un'architettura a livelli, in cui ogni livello è un compromesso tra velocità, capacità, costo e durabilità.

| Livello | Tecnologia | Latenza tipica | Uso |
|---------|-----------|---------------|-----|
| Primario | SSD NVMe | Microsecondi | Dati attivi, cache |
| Secondario | HDD meccanici | Millisecondi | Dati caldi, backup primario |
| Terziario | Nastri magnetici | Secondi | Disaster recovery, archivio |
| Futuro | Vetro (Project Silica) | Secondi+ | Long-term storage |

### Nastri magnetici: perché ancora in uso

I nastri sembrano anacronistici, ma hanno proprietà uniche:
- Possono essere fisicamente rimossi e conservati in luoghi sicuri (resistono ad attacchi fisici, EMP, disastri).
- Non richiedono alimentazione per conservare i dati.
- Il costo per GB è molto inferiore ai dischi.

I moderni archivi su nastro usano **robot** che gestiscono automaticamente l'inventario, il recupero e l'inserimento delle cassette nelle unità di lettura. L'aspetto ricorda la fantascienza, ma è tecnologia consolidata.

### Il problema della durabilità dei dati

Tutti i supporti di storage hanno una vita finita. Il professore introduce un problema poco conosciuto anche sugli SSD: ogni blocco di NAND deve essere **riscritto ogni ~2 settimane** da un thread interno del firmware del drive, altrimenti i dati si corrompono per dissipazione della carica.

> [!note] Project Silica (Microsoft)
>
> Microsoft sta sperimentando la scrittura di dati su **vetro** tramite impulsi laser, con lettura tramite microscopia ottica e decodifica AI. I dati stimati durano da mille a un milione di anni, resistono all'EMP e all'acqua. La densità attuale è ~75 GB per pezzetto di vetro (si prevede scala a TB), la latenza è nell'ordine dei secondi. Adatta solo a *cold storage* di lungo termine.

---

## Dove siamo nel corso

> [!abstract] Prossimi argomenti
>
> La prossima lezione (**Lezione 10**) approfondirà lo storage: cosa è successo all'architettura dei server con l'avvento degli SSD NVMe, come è cambiata la gerarchia di memoria, e come il software si è adattato. Seguiranno le architetture server, e poi la parte software del datacenter.

