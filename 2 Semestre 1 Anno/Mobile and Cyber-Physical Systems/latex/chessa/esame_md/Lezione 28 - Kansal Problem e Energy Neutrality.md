# Kansal Problem e Energy Neutrality

## Il Problema di Kansal: Energy Neutrality nei Sistemi IoT

Il problema di **energy management** per dispositivi IoT alimentati da sorgenti rinnovabili è intrinsecamente legato alla natura della sorgente di energia. Kansal considera il caso di sorgenti **prevedibili ma non controllabili**: fonti come l'energia solare sono soggette a variazioni giornaliere e stagionali, ma il loro andamento nel tempo può essere stimato con buona precisione.

L'obiettivo del power management è triplice:
- mantenere il sistema **energy neutral**, cioè fare in modo che la batteria non si esaurisca mai;
- **evitare che il dispositivo si spenga** prima del prossimo ciclo di ricarica;
- **massimizzare le prestazioni** del nodo, ossia la sua utility.

L'approccio consiste nel tener conto del livello attuale e atteso della batteria, modulare dinamicamente le prestazioni del dispositivo (e quindi il carico energetico), garantendo che il dispositivo non scenda sotto le performance minime.

### Approccio Kansal all'Energy Neutrality

![[exam_chessa_kansal_system.jpg]]
*Fig. — Sistema Kansal: il Device (con Scheduler e Tasks energy model) è alimentato dall'Energy buffer (Battery + DC/DC converter), rifornito dall'Energy harvester. L'Energy predictor stima la disponibilità futura e informa lo Scheduler.*

L'approccio di **Kansal** all'energy neutrality mira a massimizzare le prestazioni del dispositivo garantendo al contempo che la batteria non si scarichi mai completamente (energy neutral operation). L'idea è pianificare dinamicamente il duty cycle del dispositivo slot per slot, sfruttando previsioni sulla produzione futura.

Il sistema è composto da:
- **Energy harvester**: raccoglie energia dalla sorgente (es. pannello solare).
- **Energy buffer (Battery + DC/DC converter)**: accumula l'energia raccolta e la cede al dispositivo quando necessario.
- **Energy predictor** (con Energy source model): stima la quantità di energia che sarà disponibile nel futuro (ad es. usando previsioni meteo per un pannello solare).
- **Device** con **Scheduler** (e Tasks energy model): pianifica quali task eseguire e a quale frequenza, basandosi sia sullo stato attuale della batteria sia sulla predizione energetica futura.

**Idea centrale**: adattare il carico ($P_c$) alla disponibilità energetica prevista. Se le previsioni indicano un giorno soleggiato → il dispositivo può aumentare la frequenza di campionamento. Se le previsioni indicano bassa produzione → il dispositivo riduce l'attività.

**Condizione di energy neutrality di Kansal**:
$$B_T = B_0 + \eta \int_0^T [P_s - P_c]^+ dt - \int_0^T [P_c - P_s]^+ dt \geq B_{min} \quad \forall T$$

Il Kansal problem è quindi un problema di ottimizzazione: massimizzare le prestazioni (es. frequenza di campionamento) soggetto al vincolo di energy neutrality.

---

## Modello Task-Based per l'Energy Neutrality

Kansal modella il carico tramite duty cycle, ma le applicazioni IoT reali sono più complesse. Un'applicazione tipica esegue 4 fasi in ciclo: **Sensing → Storing → Processing → Transmitting**. Ciascuna fase può avere implementazioni alternative con diversi trade-off energia/performance.

Si chiama **task** un'implementazione specifica dell'applicazione sul dispositivo IoT. Un dispositivo ha $n$ task alternative, ciascuna con costo energetico $c_j$ e utility $u_j$.

![[exam_chessa_kansal_taskmodel.jpg]]
*Fig. — Task model: lo Scheduler pianifica i task in base al Tasks model (energia per task) e alle previsioni energetiche dell'Energy predictor (alimentato da weather forecast e da un Solar panel harvester collegato alla Battery).*

Lo schema espande il sistema Kansal con il dettaglio del **task model**. Rispetto allo schema base, qui è esplicitato il ruolo delle previsioni meteorologiche esterne.

**Componenti**:
- **Tasks model**: specifica il costo energetico di ogni task (es. campionamento = X mJ, trasmissione = Y mJ). Lo Scheduler usa questo modello per stimare quanta energia consumerà ogni operazione.
- **Scheduler**: dato il livello attuale della batteria e la previsione di energia futura, decide:
  - Quali task eseguire nel prossimo periodo.
  - A quale frequenza/duty cycle eseguirli.
  - Obiettivo: massimizzare la qualità del servizio senza violare l'energy neutrality.
- **Energy predictor + Energy source model**: riceve dati dal weather forecast (Internet) e dalle misurazioni del pannello solare per costruire un modello predittivo della produzione energetica futura.
- **Solar panel energy harvester → Battery**: flusso di potenza fisico; informazioni di stato comunicano il livello di carica allo Scheduler.

Lo scheduler assegna esattamente un task per slot, ottimizzando l'utility complessiva e rispettando i vincoli di batteria e la neutralità energetica di fine giornata.
