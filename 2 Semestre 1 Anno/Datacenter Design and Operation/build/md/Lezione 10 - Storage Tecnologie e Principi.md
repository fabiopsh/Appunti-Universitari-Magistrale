
# Storage — Tecnologie e Principi Fondamentali

Questa lezione apre il secondo grande pilastro di un datacenter: lo **storage**. Dopo aver studiato il fabric (il networking interno), e prima di affrontare il compute, il professore dedica questa sessione a capire come sono costruiti i drive, come si è evoluta la tecnologia, e quali sono i principi fondamentali che guidano la progettazione di sistemi di storage affidabili.

---

## I Tre Pilastri di un Datacenter

Un datacenter è definito dall'aggregazione flessibile di tre risorse fondamentali:

1. **Networking** (il fabric) — già trattato
2. **Storage** — argomento di questa lezione
3. **Compute** — lezione futura

Il fabric è la colla che tiene insieme tutto: se si interrompe, il sistema è giù. Lo storage è invece il luogo dove i dati sopravvivono alla perdita di corrente. Questa caratteristica — la **persistenza** — è al centro di ogni scelta architetturale nel dominio dello storage.

---

## HDD vs SSD: La Rivoluzione Silenziosa

### Il disco meccanico e i suoi limiti fisici

Per decenni, il termine generico "disco" ha designato gli **HDD** (*Hard Disk Drive*): dispositivi con piatti magnetici rotanti, testine di lettura/scrittura, settori e cilindri. La fisica impone un limite invalicabile: il tempo di accesso dipende dal movimento meccanico, sia rotazionale (il piatto deve portare il settore corretto sotto la testina) sia lineare (la testina deve spostarsi sul traccia giusta). Questo tempo, detto *seek time* e *rotational latency*, porta la latenza totale nell'ordine dei **3–5 millisecondi**.

> [!tip] Perché la latenza HDD è un muro fisico
>
> Non importa quanto sofisticata sia l'elettronica: finché il sistema dipende da un motore che fa ruotare un piatto a 7.200 o 15.000 giri al minuto, la latenza minima è imposta dalla meccanica. Non c'è algoritmo che elimini il tempo di rotazione.

L'interfaccia dominante per gli HDD è stata per anni **SATA** (*Serial ATA*), nata per i PC desktop e poi adottata anche nei server per il minor costo. In ambito server esisteva anche **SAS** (*Serial Attached SCSI*): un protocollo più performante, tipicamente usato con drive a 15.000 RPM, con latenza leggermente inferiore e supporto multipath. Oggi, con gli HDD relegati prevalentemente allo storage freddo (backup e archivi), SAS ha perso gran parte della sua rilevanza pratica: si preferisce SATA per ragioni di costo, visto che la performance non è più l'obiettivo primario di un HDD moderno.

> [!note] Capacità degli HDD oggi
>
> I drive meccanici moderni raggiungono capacità di **30–36 TB** (Samsung, Seagate, Western Digital, 2024). Questo progresso riflette esclusivamente l'uso come *cold storage*: la densità è massimizzata perché il throughput non è critico.

![Interno di un Hard Disk Drive: piatti magnetici e testine di lettura/scrittura](images/Seagate-ST33232A-hard-disk-inner-view-3421b8.jpg)
*Fig. — Anatomia interna di un HDD Seagate: i piatti magnetici rotanti e il braccio con le testine rendono visibile il vincolo meccanico che limita la latenza a 3–5 ms.*

---

### La transizione all'SSD: 30x in un solo salto

Gli SSD entrarono nel mercato consumer intorno al **2010**, inizialmente come dispositivi costosi e di piccola capacità, nella forma fattore di un disco da 2,5" per poter usare la stessa infrastruttura meccanica degli HDD. Il cambio non fu graduale: le prime generazioni di SSD su interfaccia SATA offrirono una riduzione della latency di circa **30x** rispetto agli HDD — da millisecondi a centinaia di microsecondi. Il risultato fu una "rivoluzione silenziosa" che pochi compresero appieno all'epoca.

> [!warning] Impatto a catena sull'intero stack
>
> L'accelerazione dello storage non rimase confinata all'hardware. Il sistema operativo Linux (e altri) nascondeva bug di concorrenza latenti da oltre vent'anni nel sottosistema di I/O, mai scatenati perché il disco era troppo lento. Con l'arrivo degli SSD, alcune race condition diventarono manifeste. Bisognò riscrivere parti del kernel e rivedere decenni di assunzioni sulla lentezza del disco.

---

### NVMe: un protocollo, non un dispositivo

La seconda grande svolta fu lo spostamento degli SSD dal controller SATA alla connessione diretta al bus **PCIe** (*PCI Express*) tramite il protocollo **NVMe** (*Non-Volatile Memory Express*).

È fondamentale capire che **NVMe non è un componente hardware**: è uno **standard di protocollo** che definisce come un dispositivo di storage a blocchi deve comportarsi sul bus PCIe. In pratica, un drive NVMe si presenta al sistema esattamente come qualsiasi altra scheda PCIe — una scheda di rete, una GPU — e il sistema operativo lo riconosce automaticamente senza driver proprietari.

L'effetto sul collo di bottiglia fu immediato:

| Interfaccia | Latenza tipica | Bandwidth tipico |
|---|---|---|
| HDD SATA/SAS | 3–5 ms | 100–250 MB/s |
| SSD SATA (2015) | 50–200 µs | 500–550 MB/s |
| SSD NVMe Gen 3 (2016+) | 20–100 µs | ~3,5 GB/s |
| SSD NVMe Gen 4 (2019+) | 10–50 µs | ~7 GB/s |
| SSD NVMe Gen 5 (2022+) | 5–20 µs | 10–14 GB/s |

![SSD NVMe M.2 2280 da 1 TB](images/1TB-2280-NVME-SSD-3504e0.jpg)
*Fig. — Un SSD NVMe in formato M.2 2280: la connessione diretta al bus PCIe elimina il controller SATA e porta la bandwidth a oltre 7 GB/s.*

> [!tip] Il controller come collo di bottiglia
>
> Il controller SATA/SAS era un chip hardware interposto tra il drive e la CPU, utile quando il drive era lento e aveva bisogno di buffering e command queuing. Con l'SSD, il controller divenne il **bottleneck**: rimuovendolo e collegando il drive direttamente al bus PCIe, si ottenne un guadagno di **4–5x in bandwidth** e **3–4x in latenza** a parità di tecnologia flash.

Ogni drive NVMe usa tipicamente **4 corsie PCIe** (*lanes*). La latenza attuale dei drive NVMe enterprise più veloci — circa 5 µs — è a un passo dai 2 µs di InfiniBand, la migliore fabric HPC. Lo storage, da componente lento, sta diventando "memoria persistente lenta".

---

## La Conseguenza Sistemica: PCIe come Collo di Bottiglia

Con la rimozione del controller e la connessione diretta al bus PCIe, l'intero ecosistema dovette adeguarsi. PCIe Gen 3 aveva retto per circa 10 anni, ma improvvisamente divenne il nuovo collo di bottiglia.

La risposta fu una rapida evoluzione degli standard:

- **PCIe Gen 4** (2019): raddoppia la bandwidth rispetto a Gen 3
- **PCIe Gen 5** (2021): raddoppia ancora — ~14 GB/s per drive
- **PCIe Gen 6 e 7**: in sviluppo

> [!example] AMD EPYC "Naples" (2017) e le corsie PCIe
>
> Quando AMD tornò competitiva nel segmento server con la serie EPYC, una delle sue proposte di valore chiave fu l'offerta di **128 corsie PCIe** per socket. La scelta non era casuale: il settore aveva già compreso che la CPU doveva poter alimentare direttamente i drive NVMe senza intermediari, e più corsie significava più drive operativi in parallelo.

Un server tipico con 24 drive NVMe (24 × 4 corsie = 96 corsie) richiede un numero di corsie PCIe che solo le CPU moderne riescono a fornire. Ciò ha spinto i produttori a integrare direttamente il controller PCIe nel die della CPU, eliminando il chip bridge che aggiungeva latenza.

---

## Gerarchia della Memoria e la Nuova Posizione dello SSD

La tradizionale gerarchia della memoria è sempre stata:

```
Cache L1/L2/L3 (ns) → DRAM (50–100 ns) → Disco (ms)
```

Con gli SSD NVMe moderni, la gerarchia si è trasformata:

```
Cache L1/L2/L3 (ns) → DRAM (50–100 ns) → SSD NVMe (5–20 µs) → HDD (3–5 ms)
```

Il salto tra DRAM e SSD non è più di 6 ordini di grandezza (come tra ns e ms), ma di **2 ordini di grandezza**. Questo ha conseguenze algoritmiche profonde: strutture dati che prima dovevano risiedere interamente in memoria — perché la serializzazione su disco era proibitiva — ora possono essere mantenute direttamente sull'SSD.

> [!example] RocksDB come caso paradigmatico
>
> RocksDB (Facebook/Meta) è una libreria che implementa una *persistent hash table* ottimizzata per SSD. Prima degli SSD veloci, qualsiasi dato che doveva sopravvivere al riavvio richiedeva serializzazione su disco con buffer intermedi in memoria. Con RocksDB su NVMe, si scrivono coppie chiave-valore direttamente su storage persistente senza gestire esplicitamente buffer o strutture doppie. Le performance sono abbastanza buone da rendere il pattern accettabile.

---

### Intel Optane (3D XPoint): La Memoria Persistente che Non Fu

Intel Optane è una tecnologia **non NAND** che merita menzione, nonostante Intel l'abbia cancellata nel 2022. Utilizzava una struttura tridimensionale a giunzioni (*3D Cross-Point*) che permetteva di memorizzare un bit a ogni incrocio di un reticolo 3D. Le proprietà che la distinguevano dalle NAND flash:

- **Latenza quasi simmetrica**: lettura e scrittura avevano tempi paragonabili (fattore 3–10x, contro i 6–100x delle NAND)
- **Endurance molto superiore**: milioni di cicli PE contro i migliaia delle NAND TLC
- **Connessione alla memoria bus**: installabile su slot DIMM (*NVDIMM*), non solo su PCIe

> [!definition] NVDIMM — Non-Volatile DIMM
>
> Standard elettrico introdotto da Intel intorno al 2015 per permettere l'installazione di moduli di memoria persistente sullo stesso bus dei moduli DRAM standard. Optane era disponibile in moduli da 512 GB per slot, consentendo server con **terabyte di RAM persistente**.

La tecnologia permetteva al processore di fare *tiering* automatico: i dati caldi residevano in DRAM, quelli tiepidi migrando su Optane. In termini di latenza, Optane NVMe era intorno ai **10 µs** con variazione minima tra lettura e scrittura — il miglior avvicinamento alla DRAM come storage persistente mai commercializzato.

I motivi del fallimento furono due:
1. **Intel attraversava una crisi interna** e dovette tagliare progetti costosi
2. **Il software non era pronto**: i sistemi operativi non sapevano sfruttare il memory tiering con sufficiente efficienza, e l'NVMe SSD nel frattempo stava migliorando rapidamente

> [!note] Il problema di sicurezza della memoria persistente
>
> La persistenza nei DIMM introduce un vettore di attacco imprevisto: un attaccante fisico che rimuove i moduli può leggerne il contenuto offline. Intel risolse generando una chiave crittografica casuale all'avvio, memorizzata in un registro volatile. Tutti i dati scritti sull'Optane erano cifrati con quella chiave. Se il modulo veniva rimosso, il registro veniva perso, rendendo inutilizzabile il contenuto — simulando il comportamento della DRAM tradizionale.

---

## Asimmetria Lettura/Scrittura negli SSD

Tutti i dispositivi basati su tecnologia NAND (a differenza di Optane) presentano una **asimmetria fondamentale** tra latenza di lettura e latenza di scrittura.

> [!definition] Ciclo PE — Program/Erase
>
> Una cella NAND non può essere riscritta direttamente: prima deve essere **cancellata** (*erase*) e poi **programmata** (*program*). La cancellazione avviene a livello di blocco (migliaia di celle), mentre la scrittura avviene a livello di pagina. Questo genera amplificazione di scrittura e latenza asimmetrica.

| Tecnologia | Latenza lettura | Latenza scrittura | Rapporto |
|---|---|---|---|
| DRAM | ~50–100 ns | ~50–100 ns | ~1x (simmetrica) |
| Intel Optane | ~6–10 µs | ~6–10 µs | ~1–3x |
| SSD NVMe Gen 5 | ~20–50 µs | ~50–200 µs | ~2–7x |
| SSD SATA (2015) | ~50–100 µs | ~500 µs–5 ms | ~10–100x |
| HDD | ~3–5 ms | ~3–5 ms | ~1x (simmetrica, ma lenta) |

Questa asimmetria è rilevante nelle scelte architetturali: workload write-intensive richiedono drive con migliore endurance (SLC o MLC), e i sistemi di storage devono prevedere buffer di scrittura appropriati.

---

## Tipologie di Celle NAND e Endurance

Non tutti gli SSD sono uguali: la densità delle celle NAND — misurata in bit per cella — determina un trade-off tra capacità, costo, prestazioni e vita utile.

> [!definition] Cicli PE (Program/Erase)
>
> Ogni cella NAND può essere cancellata e riscritta un numero finito di volte. Questo numero, detto *PE cycles* o *endurance*, diminuisce all'aumentare dei bit per cella: più stati da distinguere significano margini elettrici più stretti e usura più rapida.

| Tipo | Bit/cella | PE Cycles tipici | Latenza scrittura | Costo/GB | Caso d'uso |
|---|---|---|---|---|---|
| **SLC** | 1 | ~50.000–100.000 | ~200 µs | Molto alto | Cache, storage ad alta frequenza di scrittura |
| **MLC (eMLC)** | 2 | ~10.000–30.000 | ~600 µs | Alto | Enterprise, workload misto lettura/scrittura |
| **TLC** | 3 | ~1.000–3.000 | ~1–3 ms | Medio | Standard consumer e enterprise oggi |
| **QLC** | 4 | ~100–1.000 | ~5–10 ms | Basso | Storage freddo, archivio |
| **PLC** | 5 | <100 | ~10–20 ms | Molto basso | Archiviazione pura (*write once*) |

> [!warning] SLC come cache interna
>
> Molti drive TLC e QLC includono una porzione di celle configurate in modalità SLC come **buffer di scrittura** interno. Le scritture iniziali vanno nella cache SLC (molto veloce), poi vengono migrata nel TLC/QLC in background. Quando il buffer SLC si esaurisce (drive quasi pieno), le prestazioni di scrittura crollano bruscamente.

---

### Over-provisioning e precondizionamento

Un SSD da 4 TB potrebbe internamente contenere 6–8 TB di celle NAND. La capacità "nascosta" oltre quella esposta serve a due scopi:

1. **Wear leveling**: il controller distribuisce le scritture uniformemente su tutte le celle per evitare che alcune si esauriscano prima di altre. Avere celle di riserva moltiplica la vita effettiva del drive.
2. **Performance**: il controller usa lo spazio libero per ottimizzare le operazioni di garbage collection e riorganizzazione interna.

> [!warning] Il "precondizionamento" e la barra rossa
>
> Quando un drive supera circa il **90% di riempimento**, le prestazioni degradano significativamente. Il controller ha meno spazio libero per fare wear leveling e ottimizzazione. macOS e Windows mostrano la barra di utilizzo in rosso proprio a questo punto — non per indicare che il disco è quasi pieno in senso assoluto, ma per segnalare che le **prestazioni stanno per peggiorare**. Regola pratica: mantenere un drive SSD sotto il 75–80% per preservare le prestazioni.

---

## Il Peccato Imperdonabile: Perdere i Dati

Prima di affrontare le soluzioni tecniche, il professore pone il principio cardine di tutto il dominio storage:

> [!warning] La regola fondamentale dello storage
>
> In IT esistono eventi gravi ma recuperabili — un server che si rompe, una rete che cade. Esiste però **un solo peccato imperdonabile**: **perdere i dati**. Tutto il resto si ripristina; i dati persi non tornano.

Questo non è un fatto tecnologico, è un fatto organizzativo e culturale. Qualsiasi sistema di storage deve essere progettato partendo da questo assioma: il disco *può* e *prima o poi* **fallirà**. La domanda non è "se" un drive si romperà, ma "quando".

> [!example] Il datacenter di Bruxelles
>
> Un cloud provider installò due datacenter nello stesso isolato di Bruxelles, in edifici separati con linee elettriche indipendenti. I due datacenter erano configurati come backup l'uno dell'altro. Un incendio di proporzioni eccezionali distrusse entrambi gli edifici. Risultato: perdita totale dei dati. La normativa europea richiede oggi una distanza minima di **11–12 km** tra datacenter usati per la replica dei dati, proprio per mitigare rischi di questo tipo (inondazioni, incendi, guasti di rete elettrica locali).

---

## RAID: Ridondanza attraverso l'Aggregazione

**RAID** (*Redundant Array of Inexpensive Disks*) nacque negli anni '80 non come soluzione di backup, ma come risposta a un problema economico: un drive di grande capacità costava molto più di due drive più piccoli. L'idea era aggregare drive economici in un unico volume logico, compensando la loro minore affidabilità con la ridondanza.

Il meccanismo comune a tutti i livelli RAID è il **parallelismo**: se ho due drive e devo scrivere due blocchi, posso inviarli contemporaneamente ai due drive, eseguendo due scritture al costo temporale di una.

---

### RAID 0 — Striping (nessuna ridondanza)

Il **RAID 0** non è propriamente un RAID nel senso di ridondanza: si tratta di **striping**, cioè della distribuzione dei dati su più drive per presentare al sistema un singolo volume logico più grande. I blocchi vengono alternati tra i drive: blocco 0 → drive A, blocco 1 → drive B, blocco 2 → drive A, ecc.

Il vantaggio è doppio: capacità aggregata e potenziale di leggere/scrivere in parallelo dai due drive. Lo svantaggio è totale assenza di protezione: la perdita di un qualsiasi drive causa la perdita dell'intero volume.

---

### RAID 1 — Mirror (specchio)

Il **RAID 1** è la forma più intuitiva di ridondanza: ogni blocco è scritto identicamente su due drive. In caso di guasto di un drive, si opera sul secondo senza interruzioni. Il prezzo da pagare è la **capacità effettiva dimezzata**: due drive da 4 TB danno 4 TB utilizzabili.

In compenso, le letture possono essere distribuite sui due drive, migliorando il throughput in lettura. La fase di *rebuild* (copia del drive funzionante sul nuovo drive) non richiede di portare il volume offline.

---

### RAID 5 — Parità distribuita con XOR

Il **RAID 5** usa un meccanismo matematico elegante per ottenere ridondanza con un overhead di **1/N** anziché del 50% del RAID 1.

> [!theorem] La proprietà XOR che rende possibile RAID 5
>
> L'operazione **XOR** (*OR esclusivo*) ha una proprietà fondamentale: se $A \oplus B = C$, allora conoscendo due qualsiasi dei tre valori si può ricostruire il terzo: $A = B \oplus C$, $B = A \oplus C$.
>
> In RAID 5 con 3 drive, si memorizzano i dati sui drive A e B, e il loro XOR sul drive C (chiamato blocco di parità). Se uno dei tre drive fallisce, si ricostruisce il suo contenuto calcolando lo XOR degli altri due.

Con $N$ drive in RAID 5:
- **Capacità utile**: $(N-1)/N$ del totale (con 3 drive: 66%, con 6 drive: 83%)
- **Tolleranza**: perdita di **1 drive**
- **Rebuild**: richiede di portare il volume offline, ricalcolare tutti i blocchi di parità

Il costo nascosto del RAID 5 è il **degraded mode**: quando un drive fallisce e si aspetta la sostituzione, il sistema deve eseguire la ricostruzione di ogni blocco mancante on-the-fly, aumentando la latenza di lettura. Se un secondo drive fallisce durante il rebuild, si perde tutto.

---

### RAID 6 — Doppia parità

Il **RAID 6** estende il RAID 5 con **doppia parità** (usando algoritmi matematici più sofisticati dell'XOR semplice, basati sui campi di Galois). Questo permette di:

- Tollerare la perdita di **2 drive** simultaneamente
- Rimanere **online** in modalità degradata con 1 drive guasto durante il rebuild

Il costo in capacità è leggermente superiore al RAID 5 (overhead di 2/N anziché 1/N), ma il guadagno in affidabilità è significativo.

**RAID 6 è oggi lo standard de facto** nei sistemi di storage, preferito al RAID 5 perché il rischio di guasto di un secondo drive durante il lungo processo di rebuild di un array moderno (ore su drive da decine di TB) è concreto.

---

### Confronto riepilogativo RAID

| Livello | Drive minimi | Capacità utile | Drive tollerati | Online con 1 guasto | Meccanismo |
|---|---|---|---|---|---|
| RAID 0 | 2 | 100% | 0 | No | Striping |
| RAID 1 | 2 | 50% | 1 | Sì | Mirroring |
| RAID 5 | 3 | $(N-1)/N$ | 1 | Degraded | Parità XOR |
| RAID 6 | 4 | $(N-2)/N$ | 2 | Sì (con 1) | Doppia parità |

> [!note] Chi implementa il RAID?
>
> Storicamente, il RAID era implementato dal **controller hardware** del disco: il chip interposto tra i drive e la CPU esponeva un singolo volume logico al sistema operativo. Con la transizione a NVMe (che elimina il controller), il RAID deve essere implementato dal **sistema operativo** (Linux `mdadm`, Windows Storage Spaces) o da software dedicato. L'OS è perfettamente in grado di farlo, ma la transizione ha richiesto adattamento nei workflow di amministrazione.

---

## Verso le Architetture di Storage Distribuite

La lezione si chiude con un'anticipazione: il singolo server con RAID non è sufficiente per le esigenze dei datacenter moderni. L'evoluzione naturale porta alle **architetture di storage centralizzato e distribuito**, che saranno trattate nelle lezioni successive:

- **SAN** (*Storage Area Network*): storage condiviso accessibile via rete dedicata
- **NAS** (*Network Attached Storage*): file system condiviso via rete standard
- **HCI** (*Hyper-Converged Infrastructure*): storage distribuito che usa i drive locali dei server, con replicazione software a **3 copie** (overhead 3x, ma proprietà di disponibilità superiori)

> [!abstract] Sintesi della lezione
>
> La transizione da HDD a SSD NVMe è una delle rivoluzioni più sottovalutate dell'informatica degli ultimi 15 anni. Ha ridotto la latenza di storage da millisecondi a microsecondi, trasformando il disco da componente lento a quasi-memoria persistente. Questa trasformazione ha costretto a riprogettare controller, bus PCIe, CPU, sistemi operativi e architetture software. Il principio guida di tutto lo storage rimane invariato: **perdere i dati è imperdonabile**, e ogni scelta tecnologica — dal tipo di cella NAND al livello RAID — ruota attorno alla massimizzazione dell'affidabilità al minor costo possibile.

