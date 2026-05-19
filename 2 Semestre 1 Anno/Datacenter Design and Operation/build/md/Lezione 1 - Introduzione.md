# Lezione 1 — Introduzione ai Data Center

> Corso: *Data Center Design and Operation* — Prof. **Antonio Cisternino**, Università di Pisa
> Visione orizzontale dell'infrastruttura dietro Cloud, VM e sistemi HPC.

---

## Dalle Sale Server alle Gigafactories

Venti anni fa un data center era una stanza con un condizionatore, qualche rack e PC desktop senza monitor. Oggi è infrastruttura critica a livello nazionale.

> [!info] Definizione legislativa
> Il parlamento italiano sta lavorando a una **legge delega** per regolamentare i data center. Un impianto è considerato di **rilevanza nazionale** quando supera **0,5 MW** di assorbimento.

**Riferimenti storici (Università di Pisa):**
- **2013** — Primo data center di Cisternino (vicino al bar d'ingresso): **80 kW**
- **Oggi** — Polo di San Piero: **250–300 kW**

Con l'esplosione delle **AI factories**, si entra nell'era delle **Gigafactories**: esistono progetti per data center da **2,5 GW**, un valore che impone vincoli estremi sulla rete elettrica nazionale (in Italia pochissimi siti possono erogare tale potenza in un unico punto).

---

## Infrastruttura di Rete e Switching

| Contesto | Tecnologia | Velocità |
|---|---|---|
| Campus / Management DC | Ethernet RJ45 | < 1 Gbps |
| Traffico principale DC | Fibra ottica | 10–25 Gbps |

**Switch moderno (< $10.000):**
- 48 porte × 25 Gbps
- Architettura **non-blocking** → nessun overbooking, zero colli di bottiglia
- Capacità di switching: **1,2–2,4 Tbps** (fino a 24 Tbps in TX+RX)

> [!note] Non-Blocking Switch
> Tutti i nodi possono trasmettere e ricevere simultaneamente senza subire rallentamenti. Lo switch diventa esso stesso un sistema di calcolo intensivo.

---

## Il Paradigma Sconvolto dall'IA

### Prima dell'IA: virtualizzazione e Cloud

I laptop e i server moderni rimangono al **10% del potenziale** per il 90% del tempo → a partire dal **2008** l'industria enterprise ha sfruttato la **virtualizzazione** per recuperare questa inattività, dando vita al **Cloud**.

### L'IA rompe l'equilibrio

L'IA è il **primo workload che satura integralmente l'hardware fisico**. Conseguenze:

- La virtualizzazione non ha senso nello stack AI
- Si usano architetture distribuite su **GPU multiple**
- La **latenza di comunicazione** è un vincolo critico → i cavi devono essere i più corti possibile

### Costo computazionale dei token

> [!example] Esempio: LLM da 7B parametri
> - 1 token (≈ 3 caratteri) → **7 miliardi di moltiplicazioni**
> - 1.000 token → **~7 trilioni di operazioni**

Per modelli come **GPT-4** (stimato ~600B parametri), il costo sarebbe improponibile senza la tecnica **Mixture of Experts**: la rete si divide in strati specialistici, limitando le moltiplicazioni attive a **1–3 miliardi per esperto**.

> [!note] Mixture of Experts (MoE)
> Paradigma computazionale che attiva dinamicamente solo una piccola porzione della matrice di parametri per ogni inferenza, abbattendo drasticamente il costo del token.

### Hardware richiesto (2024–2025)

Per eseguire modelli open-source da **120B parametri** (es. GPT-OSS, Deepseek R1):
- 2× **Nvidia RTX 6000** → ~**€50.000 cadauna**

---

## Fisica dei Data Center: Alimentazione e Cooling

### Evoluzione della densità per rack

| Periodo | Potenza per rack |
|---|---|
| Primi anni 2000 | 3 kW |
| 2013–2016 (San Piero) | 15 kW |
| Oggi (AI hardware) | ~200 kW |
| Previsione a breve | 500 kW – 1 MW |

> [!warning] Scala: 200 kW per rack
> Equivale alla potenza massima di **70 appartamenti** collegati simultaneamente a un singolo armadio.

### Implicazioni fisiche

- **Cablaggio:** a 200 kW il rame classico è inutilizzabile → si usa un **power bar rigido** nella parete posteriore del rack
- **Raffreddamento:** il **liquid cooling** è passato da opzione futuristica a **necessità obbligatoria** — un sistema HPC non può essere acceso senza raffreddamento attivo a liquido

> [!tip] Perché i chip generano calore?
> L'algebra booleana è intrinsecamente dissipativa. Nelle porte logiche (es. AND con due input `1`), la tensione in eccesso non può accumularsi e viene disposta come **calore**. Le **Fredkin Gates** (porte trinomiali invertibili, non dissipative) avrebbero risolto il problema, ma non sono mai state realizzate commercialmente per limiti manifatturieri.

---

## Supercomputer e Tensioni Geopolitiche

### Top500 & Green500

- **Top500**: classifica semestrale (dal 1993) basata su benchmark di algebra lineare
- **Green500**: efficienza in **petaflops/Watt**
- La partecipazione non è obbligatoria (es. NSA, Ferrari nel 2003 non hanno certificato i propri sistemi)

### Sistemi di punta

| Sistema | Note |
|---|---|
| Frontier | USA |
| Aurora | USA |
| Jupiter Boost | Europa |
| Fugaku | Giappone (ex campione) |
| **Eagle** (Microsoft Azure) | 2M core, AI-oriented, **distribuito virtualmente** |
| **Leonardo** (CINECA) | 2M core, **10° posto**, Italia |

### Geopolitica europea

- **2019**: post-Brexit, la Commissione Europea (dir. **Roberto Viola**) ha investito **~2 miliardi €** in 7 anni per colmare il vuoto lasciato dal Regno Unito
- L'Italia ha avviato una gara d'appalto (gestita dal CINECA) per un'**AI Factory nazionale**: **500 milioni €**

> [!info] Scala degli investimenti USA
> **Project Stargate** (Oracle/OpenAI/Ellison): **500 miliardi di dollari**
> La capitalizzazione di **Nvidia** supera il PIL di Italia, Francia e Germania.

---

## Localizzazione: Vincoli Geografici e Fiscali

### L'Italia è un paese sfavorevole per i data center

> [!danger] Problemi strutturali italiani
> 1. **Rischio sismico** — Hardware delicato vulnerabile alle scosse. Es: il data center della Regione Lazio è costruito al primo piano su **pilastri ammortizzanti** antisismici.
> 2. **Escursione termica** — Oscillazioni fino a **50°C** tra estate e inverno destabilizzano i sistemi di raffreddamento (stesso fenomeno che crepa l'asfalto italiano).

Stesso problema: sud della Spagna, Barcellona, Grecia.

### Soluzioni adottate nel mondo

| Approccio | Esempio |
|---|---|
| Deserti freddi di notte | Nevada (ghiaccio notturno per raffreddamento diurno) |
| Paesi nordici | Scandinavia, Islanda (ma: rischio eruzioni vulcaniche) |
| Caverne alpine | ENI — supercalcolatore nelle Alpi a temperatura costante |
| Free cooling invernale | **Aruba** (Arezzo) — turbina reversibile: aria fredda d'inverno, estrazione d'estate |
| Fondale marino | **Microsoft Project Natick** — cicli quinquennali; rischi: corrosione salina, servicing difficile |

### Vantaggi fiscali: l'esempio irlandese

Google, Apple, Microsoft e altri hanno scelto l'**Irlanda** principalmente per gli **sconti fiscali** legati all'ingresso nell'UE, non solo per il clima favorevole.

---

## Problematiche Acustiche, Fiscali e Gestionali

### Impatto acustico

I **chiller** (pompe di raffreddamento) sono rumorosi e continui. Il data center del dipartimento di Ingegneria di Pisa fu smantellato per **sentenza di un giudice**: nonostante fosse sotto la soglia legale di decibel, un professore vicino fece causa e vinse, costringendo al trasferimento nel polo extra-cittadino (con ulteriori problemi burocratici legati ad aree boschive vincolate).

### Infrastruttura elettrica

A Pisa, la cabina vicino al bar era predisposta fino a **2 MW**, ma la rete urbana limitava l'impianto a **80 kW**.

### Gestione di larga scala

> [!important] Documentazione e gestione
> In una server farm con **700+ macchine** interconnesse via fibra ottica, non è ammissibile tracciare fisicamente un cavo in caso di guasto.
> Ogni componente, porta logica e armadio deve essere catalogato e rintracciabile via **software di gestione centralizzato**.
> L'efficienza energetica si misura con il **PUE (Power Usage Effectiveness)**.

---

## Glossario

| Termine | Definizione |
|---|---|
| **Legge Delega** | Iter normativo per regolamentare i data center di rilevanza nazionale |
| **Non-Blocking Switch** | Switch senza overbooking: tutti i nodi trasmettono/ricevono senza code |
| **Mixture of Experts (MoE)** | Paradigma AI che attiva dinamicamente solo una frazione dei parametri per ridurre il costo computazionale per token |
| **Top500 / Green500** | Classifiche semestrali di performance HPC (dal 1993) e di efficienza energetica (petaflops/W) |
| **Fredkin Gates** | Porte logiche teoriche trinomiali e invertibili, non dissipative termicamente — mai realizzate commercialmente |
| **PUE** | Power Usage Effectiveness: rapporto tra potenza totale del DC e potenza consumata dall'IT |
| **Liquid Cooling** | Raffreddamento a liquido, oggi obbligatorio per hardware HPC ad alta densità |
