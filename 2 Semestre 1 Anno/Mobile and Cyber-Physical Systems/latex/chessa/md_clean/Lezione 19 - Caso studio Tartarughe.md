
# Case Study: Biologging e Activity Recognition

Il biologging rappresenta uno dei casi d'uso più concreti e affascinanti dell'IoT applicato al mondo naturale. La lezione sviluppa questo tema attraverso un caso di studio reale: il progetto **Tortoise@**, che automatizza il rilevamento delle attività di nidificazione delle tartarughe con tecniche di machine learning embedded su dispositivi a bassa potenza.

---

## Dal monitoraggio diretto al monitoraggio sensoriale

L'osservazione diretta degli animali (e degli esseri umani) è uno strumento efficace per raccogliere informazioni sulle loro attività, ma è per sua natura limitata: richiede la presenza fisica di un osservatore, non può essere continua e copre solo una frazione ridotta della vita del soggetto. L'impiego di sensori miniaturizzati — accelerometri, GPS, sensori di pressione, luce, temperatura — trasforma questa limitazione: il monitoraggio diventa **continuo**, **automatizzato** e capace di coprire quasi tutti gli aspetti della vita del soggetto.

I dispositivi vengono fisicamente applicati agli animali in libertà (*free-range animals*). A questo punto si apre una distinzione fondamentale tra due approcci:

> [!definition] Biotelemetria vs Bio-logging
>
> **Biotelemetria**: i dati raccolti dai sensori vengono trasmessi in tempo reale a una stazione remota tramite un'interfaccia wireless. Non c'è memorizzazione locale.
>
> **Bio-logging**: i dati vengono memorizzati nella memoria interna del dispositivo. Il ricercatore deve fisicamente recuperare il dispositivo per accedere ai dati. I dispositivi più moderni possono anche trasmettere remotamente quando le condizioni lo permettono.

Il terzo elemento del quadro è l'**activity recognition** (*riconoscimento dell'attività*): un sistema che, a partire dai segnali registrati durante l'attività dell'animale, riconosce automaticamente le azioni compiute. Questo trasforma dati grezzi in informazioni semanticamente ricche.

## Pipeline del Biologging

Il flusso completo del biologging si articola in tre fasi: raccolta dei dati → elaborazione dei dati → classificazione dell'attività.

![Pipeline Biologging: dalla raccolta dati alla classificazione delle attività](images/lezione-19-caso-studio-tartarughe-img-01.jpg)
*Fig. — Il flusso completo: il dispositivo di biologging fornisce serie temporali, che vengono analizzate (da un osservatore umano o da un sistema automatico) e infine classificate in attività specifiche (es. "digging").*

---

## Punti di forza e debolezza

L'approccio sensoriale ha vantaggi importanti rispetto all'osservazione tradizionale, ma introduce anche nuove sfide operative.

| Punti di forza | Debolezze |
|---|---|
| Osservazioni puntuali tramite sensori | È necessario applicare il dispositivo al soggetto |
| Funziona in ambienti domestici e selvatici | Necessità di recuperare fisicamente il dispositivo |
| Enorme quantità di dati (serie temporali) | Quando la memoria si riempie o la batteria si esaurisce, i dati vengono persi |
| — | Vita limitata del dispositivo in monitoraggi intensivi |
| — | Spesso solo analisi off-line |

> [!warning] Il problema della durata della batteria
>
> Nei dispositivi di biologging, il consumo energetico è il vincolo progettuale più critico. Un monitoraggio continuo che raccoglie e trasmette serie temporali grezze porta rapidamente all'esaurimento della batteria, limitando la durata utile del dispositivo a periodi ben inferiori alle stagioni di osservazione necessarie.

---

## Prospettiva del dispositivo: approccio convenzionale vs approccio innovativo

### Approccio convenzionale

Nel paradigma classico, il dispositivo è un semplice *data logger* a bassa potenza: raccoglie enormi quantità di dati di serie temporali e deve poi o trasmetterli a una stazione remota o essere fisicamente recuperato. Entrambe le opzioni hanno costi alti:

- **Comunicare** le serie temporali grezze è estremamente oneroso dal punto di vista energetico
- **Recuperare** fisicamente il dispositivo è altamente invasivo per l'animale e per l'ecosistema

### Approccio innovativo: on-board intelligence

![Approccio innovativo: classificatore automatico on-board con trasmissione dei soli risultati](images/lezione-19-caso-studio-tartarughe-img-02.jpg)
*Fig. — Il nuovo paradigma: un micro-processore a bassa potenza incorpora un classificatore automatico. Invece delle serie temporali grezze, vengono memorizzati e trasmessi solo i risultati della classificazione, riducendo drasticamente il traffico dati e il consumo energetico.*

L'idea chiave è **spostare l'elaborazione sul dispositivo stesso**:

1. Incorporare il classificatore automatico direttamente nel dispositivo (*on-board*)
2. Memorizzare solo i risultati della classificazione (efficienza di memoria)
3. Trasmettere solo i risultati della classificazione (efficienza di comunicazione)

Questo approccio richiede classificatori leggeri, capaci di girare su microcontrollori con risorse molto limitate, ma porta a vantaggi enormi in termini di autonomia e invasività.

---

## Caso di studio: Tortoise@

Il progetto di riferimento è:

> Barbuti R., Chessa S., Micheli A., and Pucci R.; *"Localizing tortoise nests by neural networks"*; PloS One 2016.

### Il problema

I programmi di protezione delle tartarughe mirano a raccogliere le uova e portarle in centri protetti, dove i piccoli vengono custoditi durante il periodo più vulnerabile. Il problema è che **identificare i nidi in natura è estremamente difficile**: le tartarughe sono molto abili nel nasconderli. Il progetto **Tortoise@** automatizza questo processo riconoscendo in tempo reale l'attività di scavo e comunicando la posizione GPS agli erpetologi.

> [!tip] Perché il riconoscimento dell'attività funziona
>
> Le tartarughe scavano i nidi con le zampe posteriori. Questo comportamento produce un pattern caratteristico nel segnale dell'accelerometro, distinguibile dall'attività di camminata o di alimentazione. La chiave è che lo scavo lascia una firma temporale riconoscibile — e questa firma può essere appresa da un modello di ML.

### Idea del sistema

![Flusso operativo di Tortoise@: riconoscimento dello scavo e notifica agli erpetologi](images/lezione-19-caso-studio-tartarughe-img-03.jpg)
*Fig. — Il sistema Tortoise@: un dispositivo con classificatore ML identifica l'attività di scavo, invia un messaggio agli erpetologi che recuperano le uova e le portano in un centro di protezione.*

### Vincoli biologici e scelte progettuali

La biologia delle tartarughe guida direttamente le scelte ingegneristiche:

- Le tartarughe depongono le uova in primavera, in un periodo di circa **4 mesi**
- Una singola tartaruga può deporre più volte (generalmente 3-4 volte)
- La nidificazione avviene di giorno, in luoghi caldi e ben illuminati
- La nidificazione dura **più di un'ora**
- Le tartarughe scavano il nido con le zampe posteriori

Da queste osservazioni derivano direttamente i requisiti tecnici:

- Il dispositivo deve durare **almeno 4 mesi**
- L'attività di scavo è rilevabile con gli accelerometri
- I sensori ambientali (luce e temperatura) possono limitare l'uso degli accelerometri ai soli momenti potenzialmente rilevanti

### Architettura per l'efficienza energetica

![Schema del design Tortoise@ per l'efficienza energetica: stato di macchina a stati finiti](images/lezione-19-caso-studio-tartarughe-img-04.jpg)
*Fig. — Il design di Tortoise@ per l'efficienza energetica: la macchina a stati usa sensori ambientali a bassa frequenza come gate per attivare il campionamento dell'accelerometro, minimizzando il consumo complessivo.*

La logica di controllo del dispositivo è progettata per minimizzare l'uso dell'accelerometro (il sensore più energivoro):

1. **Step 1 — Environment monitoring**: i sensori ambientali (luce e temperatura) vengono campionati a frequenza molto bassa (0,01 Hz). Il campionamento notturno viene evitato completamente.
2. **Step 2 — Movement monitoring**: solo quando le condizioni ambientali sono adatte si attiva il campionamento dell'accelerometro a 1 Hz per 5 minuti.
3. **Step 3 — Extended movement monitoring**: se la risposta è negativa, il dispositivo sospende per almeno mezz'ora (lo scavo dura almeno un'ora, quindi non si perde nessun evento rilevante).
4. **Step 4 — Data communication**: se il classificatore è certo che la tartaruga stia scavando, trasmette la posizione GPS. Per confermare, il ciclo di campionamento viene ripetuto 3 volte, riducendo i falsi positivi. La trasmissione radio avviene solo poche volte nell'arco di diversi mesi.

> [!info] Efficienza di sistema
>
> Questo design a cascata è un esempio di **duty cycling intelligente**: invece di campionare continuamente, si usa un sensore economico (luce/temperatura) come trigger per attivare il sensore costoso (accelerometro). Il risultato è un'autonomia molto più lunga rispetto a un campionamento naïve.

---

## Dataset e classificazione

### Raccolta dati

Il dataset è stato raccolto presso il «Centro di protezione tartarughe Mediterranee» di Massa Marittima, Italia. Gli animali coinvolti sono femmine adulte di *Testudo hermanni*, *Testudo graeca* e *Testudo marginata*. Le attività registrate sono tre: **digging** (scavo), **eating** (alimentazione), **walking** (camminata).

Il sensore utilizzato è un accelerometro a un asse (asse X) con un dispositivo **MicaZ**, campionato a 1 Hz.

![Segnali accelerometrici per le tre attività: scavo, camminata e alimentazione](images/lezione-19-caso-studio-tartarughe-img-05.jpg)
*Fig. — I segnali dell'accelerometro (asse X) per le tre attività: lo scavo (digging) mostra un pattern oscillatorio caratteristico con ampiezza maggiore e periodicità regolare rispetto alla camminata e all'alimentazione.*

### Struttura del dataset

Il dataset è organizzato in due strutture complementari:

**Sequences dataset** (task asincrono):
- Sequenze di 300 secondi, campionamento a 1 Hz
- 126 sequenze totali con classificazione positiva e negativa
- 56 sequenze nel test set, le rimanenti per training e validazione

**Patterns dataset** (task sincrono):
- Sequenze di 90 secondi a 1 Hz
- 67 pattern con classificazione positiva e 67 negativa per la selezione del modello
- 10 pattern positivi e 10 negativi per la validazione

> [!note] Perché due granularità?
>
> La scelta della dimensione della finestra dipende dalla forma del segnale di scavo. La finestra di 300 secondi (5 minuti) cattura un'intera sequenza di scavo, mentre quella di 90 secondi è sufficiente a riconoscere un *pattern* caratteristico. Le finestre più piccole abilitano la classificazione sincrona (in streaming), quelle più grandi quella asincrona (per batch).

### Approcci di classificazione

Vengono valutati **SVM** (*Support Vector Machine*) e diversi modelli di reti neurali:

> [!definition] Modelli considerati
>
> - **IDNN** (Input-Delay Neural Network): rete neurale feedforward con delay di input
> - **CNN** (Convolutional Neural Network): rete convoluzionale
> - **ESN** (Echo State Network): rete neurale ricorrente con reservoir fisso
> - **SVM**: classificatore a vettori di supporto

I due paradigmi di classificazione sono:

**Task asincrono**: classificazione di finestre singole (IDNN, CNN, SVM, ESN). L'output della rete dipende dall'intera finestra.

**Task sincrono**: classificazione step-by-step su uno stream di dati (solo ESN). L'output non richiede l'intera finestra; si basa sugli ultimi 90 secondi di campioni.

---

## Risultati

### Task asincrono

![Risultati task asincrono: accuratezza e overhead di memoria per IDNN, CNN, ESN, SVM](images/lezione-19-caso-studio-tartarughe-img-06.jpg)
*Fig. — Confronto tra modelli per il task asincrono: accuratezza (sinistra) e overhead di memoria per mantenere il modello in RAM (destra). IDNN e CNN raggiungono ~95% di accuratezza, ma con overhead molto diverso.*

| Modello | Accuratezza | Overhead memoria |
|---------|------------|-----------------|
| IDNN LRF PF | ~96% | 0,3 KB |
| CNN | ~95% | 3,5 KB |
| ESN | ~67% | 0,1 KB |
| SVM | ~53% | 25 KB / 10² |

> [!tip] Trade-off chiave
>
> IDNN e CNN raggiungono la stessa accuratezza (~95%), ma IDNN richiede solo **0,3 KB** contro i **3,5 KB** di CNN. Su microcontrollori con pochi KB di RAM, questa differenza è determinante. L'SVM, nonostante la sua semplicità concettuale, ha un overhead di memoria molto alto a causa della necessità di memorizzare i vettori di supporto.

### Task sincrono (ESN)

![Risultati task sincrono con ESN: accuratezza 93% e overhead 0,1 KB](images/lezione-19-caso-studio-tartarughe-img-07.jpg)
*Fig. — L'ESN nel task sincrono raggiunge il 93% di accuratezza con soli 0,1 KB di overhead — risultato notevole per un modello in streaming.*

Il task sincrono con ESN è la **prima applicazione di ESN per il riconoscimento di attività animali**. Il modello raggiunge il 93% di accuratezza con un overhead di soli 0,1 KB, adatto a microcontrollori estremamente vincolati.

---

## Confronto cloud vs elaborazione locale

La tabella seguente mostra il risparmio ottenibile spostando l'elaborazione on-device rispetto all'approccio cloud-based tradizionale (su un periodo di 4 mesi):

| | Elaborazione cloud | Elaborazione locale |
|---|---|---|
| Posizione GPS trasmessa | ogni mezz'ora (46 KB totali) | solo quando rilevato scavo (poche volte) |
| Dati accelerometro | 13 MB (4 mesi a 1 Hz) | max 3 KB (una finestra temporale) |
| Analisi | off-line dopo recupero | in tempo reale sul dispositivo |
| Invasività | alta (recupero fisico) | bassa (trasmissione radio rara) |

> [!abstract] Sintesi del risparmio
>
> L'approccio locale riduce il dato memorizzato da **13 MB a 3 KB** per l'accelerometro, e limita le trasmissioni GPS a **poche eventi** in 4 mesi invece di una ogni 30 minuti. Questo si traduce direttamente in una durata della batteria molto più lunga e in un'invasività drasticamente ridotta.

---

## Strutture dati in memoria

Il dispositivo utilizza due strutture dati:

1. **Struttura per il modello**: memorizza i pesi della rete neurale o i vettori di supporto dell'SVM (0,1–3,5 KB a seconda del modello).
2. **Struttura per i campioni**: memorizza al massimo una finestra di **300 campioni** (nel caso peggiore), ovvero circa 3 KB a 10 bit per campione. Con ESN, la finestra utile è di soli 90 campioni.

> [!question] Possibili domande d'esame
>
> - Qual è la differenza tra biotelemetria e bio-logging? Quando conviene l'uno e quando l'altro?
> - Perché l'approccio con classificatore on-board è superiore a quello con trasmissione delle serie temporali grezze?
> - Come funziona la macchina a stati di Tortoise@ per ottimizzare l'efficienza energetica?
> - Confronta le performance di IDNN, CNN, ESN e SVM nel task asincrono. Quale sceglieresti per un microcontrollore con 1 KB di RAM libera? Perché?
> - Quanto dato deve memorizzare il dispositivo Tortoise@ con elaborazione locale, rispetto all'approccio cloud? Calcola la differenza.
> - Cos'è un task sincrono vs asincrono nel contesto dell'activity recognition? Quale rete neurale supporta il task sincrono e perché?
