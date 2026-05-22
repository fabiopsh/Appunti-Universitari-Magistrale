---
tags:
  - università/datacenter-design-and-operation
  - operations
  - service-management
  - monitoring
  - incident-management
  - capacity-planning
data: 2026-05-22
lezione: "20 - Operations e Considerazioni Finali"
professore: "Antonio Cisternino"
---

# Operations e Considerazioni Finali

Questa ultima lezione chiude il percorso del corso affrontando la parte più procedurale e operativa del cloud: la **service operations management**, ovvero tutto ciò che avviene *dopo* che l'infrastruttura è in piedi. Se le lezioni precedenti hanno costruito i mattoni dell'infrastruttura — rete, storage, compute, virtualizzazione — questa lezione risponde alla domanda: come si *gestisce* tutto questo nel tempo?

---

## Service Operations Management

Una volta che il cloud è operativo, qualcuno deve essere responsabile di mantenerlo funzionante. Questo non significa solo "fare sì che le macchine girino": significa garantire che gli **SLA siano rispettati**, che i guasti vengano identificati e risolti, che le risorse vengano pianificate con anticipo e che ogni modifica venga tracciata. Se un SLA non è rispettato, il provider paga — letteralmente, sotto forma di compensazioni o servizi gratuiti.

Le attività tipiche di operations management si possono raggruppare in tre categorie principali:

- **Gestione della configurazione dell'infrastruttura**: sapere in ogni momento com'è configurato ogni sistema.
- **Provisioning delle risorse**: allocare risorse quando vengono richieste, e de-provisioning quando non servono più.
- **Problem resolution**: identificare e risolvere guasti, prima che diventino violazioni di SLA.

A queste si aggiunge il **capacity planning**: capire *quante risorse serviranno* nei prossimi mesi, in modo da avere il tempo di approvvigionarle prima che quelle esistenti si esauriscano. Il capacity planning si muove su un equilibrio delicato: avere troppa capacità inutilizzata è un costo capex sprecato che peggiora il TCO; averne troppa poca significa violare gli SLA.

> [!abstract] Processi chiave delle operations
>
> I processi principali che strutturano le operations di un cloud sono:
> - **Monitoring**: osservare continuamente lo stato dell'infrastruttura
> - **Service Asset and Configuration Management**: inventario e tracciamento delle configurazioni
> - **Change Management**: governare ogni modifica al sistema
> - **Capacity Management**: pianificare le risorse nel tempo
> - **Performance Management**: garantire le prestazioni promesse dagli SLA
> - **Incident Management**: rispondere a eventi non pianificati
> - **Problem Management**: prevenire la ricorrenza degli incidenti
> - **Availability Management**: garantire la disponibilità dei servizi
> - **Security Monitoring**: rilevare e tracciare anomalie di sicurezza

---

## Monitoring

Il monitoring è la base di tutto: senza visibilità sullo stato dei sistemi, non si può sapere se si stanno rispettando gli obiettivi. In un'infrastruttura moderna esistono migliaia — a volte milioni — di contatori: a livello di rete, hypervisor, sistema operativo, BMC del server. La quantità di dati è tale che non è possibile leggerli manualmente; servono strumenti software in grado di analizzare questo flusso e segnalare le anomalie.

Un aspetto controintuitivo, ma importante: **ogni sistema "pulito" genera migliaia di errori nei propri log**. I sistemi sono progettati per tollerare molti errori prima di smettere di funzionare, quindi la semplice presenza di warning nei log non significa che il sistema sia compromesso. Il vero lavoro del monitoring consiste nel distinguere tra gli allarmi che indicano un problema reale e quelli che sono semplicemente rumore di fondo. Questo richiede **dati storici** per identificare outlier e variazioni rispetto alla media.

Il monitoring non riguarda solo i contatori di performance. Si distinguono almeno tre tipi:

- **Configuration monitoring**: rilevare errori di configurazione, violazioni di policy, modifiche non autorizzate. Anche solo sapere che *qualcosa è cambiato* — indipendentemente da chi — è già un'informazione preziosa.
- **Availability monitoring**: verificare che tutti i servizi siano raggiungibili. A livello pratico, questo significa monitorare anche i singoli componenti hardware: all'Università di Pisa, ad esempio, una persona controlla quotidianamente lo stato di tutti i dischi dei cluster, usando strumenti automatizzati che segnalano fallimenti o degradi.
- **Security monitoring**: in un cloud pubblico, il target è particolarmente appetibile per gli attaccanti — riuscire a compromettere Google, Amazon o Azure avrebbe un impatto enorme. Per questo il volume di tracking in un datacenter reale è molto elevato; anche accessi fisici alla sala macchine sono controllati con sensori biometrici.

### Predictive Failure

Una delle funzionalità più interessanti del monitoring moderno è la **predictive failure analysis**. I produttori come Dell integrano nei BMC dei modelli statistici costruiti su dati di milioni di dischi: quando un disco inizia a mostrare pattern di comportamento associati a un imminente guasto, il BMC emette un avviso *prima* che il disco si rompa.

Questo consente un flusso operativo molto efficace: si apre un ticket di supporto, si rimuove il disco dal pool di storage (riducendo temporaneamente la ridondanza ma senza perdere dati), si sostituisce il disco e si reinserisce nel pool. Dal punto di vista dell'utente, non è successo nulla.

> [!warning] Attenzione al clock della ridondanza
>
> Quando un componente guasto viene rilevato — che sia per predictive failure o per guasto improvviso — il **clock comincia a ticchettare**. La ridondanza è stata ridotta; se un secondo componente guasta prima che il primo venga sostituito, il sistema può perdere dati o servizi. La sostituzione deve avvenire il più rapidamente possibile.

Il rischio opposto è l'**effetto a cascata**: se un sistema fallisce e il meccanismo di failover sposta il carico su altri nodi, questi possono essere sovraccaricati e fallire a loro volta, scatenando un'ondata di failure che si propaga. Un caso reale citato da Cisternino riguarda Amazon: un sistema fallì, il carico fu automaticamente spostato su un altro sistema che si saturò e collassò, innescando una reazione a catena che impiegò mesi per essere risolta — Amazon arrivò a inviare fisicamente tecnici con dischi aggiuntivi nel datacenter, ma la velocità con cui i sistemi consumavano lo storage era superiore alla velocità con cui i dischi venivano inseriti.

### Frequenza di raccolta e costo del monitoring

Il monitoring non è gratuito: ogni ciclo di calcolo dedicato a raccogliere e analizzare metriche è un ciclo sottratto al carico utile. Bisogna trovare un equilibrio sulla frequenza di raccolta: troppo frequente e si è sommersi da dati; troppo raro e si perdono eventi critici. Lo stesso vale per la granularità: non tutti i contatori hanno la stessa utilità, e raccoglierli tutti ad alta frequenza è economicamente insostenibile.

### Bookkeeping e documentazione

In un datacenter, **la documentazione è obbligatoria**. Il disaccoppiamento tra hardware e software (tipico della virtualizzazione) rende difficile risalire fisicamente a dove si trova un certo componente: non si può semplicemente "seguire il cavo" perché i cavi sono raggruppati in fascette e i sistemi virtuali non hanno un'ubicazione fisica ovvia. Se un cluster si guasta, bisogna sapere *immediatamente* quali sistemi sono coinvolti — e questa risposta deve venire dalla documentazione, non da un'esplorazione manuale.

---

## Capacity Monitoring e Capacity Management

Il **capacity monitoring** è il processo che osserva l'utilizzo delle risorse nel tempo. L'obiettivo è duplice: evitare che le risorse si esauriscano (con conseguente violazione degli SLA) e evitare che siano sovra-dimensionate (con conseguente spreco di capex e peggioramento del TCO/ROI).

> [!tip] L'analogia con le assicurazioni
>
> Il capacity management ragiona come una compagnia assicurativa: si fanno stime statistiche sul comportamento atteso, si aggiunge un margine di sicurezza ragionevole, e si scommette che non tutti useranno le risorse al massimo contemporaneamente. L'**overbooking** — offrire più risorse di quelle fisicamente disponibili, contando sull'utilizzo medio — è una pratica consolidata. Se la scommessa è sbagliata, si paga il prezzo.

Un aspetto pratico del capacity monitoring è il controllo dell'utilizzo **per singola istanza di servizio**. A volte un servizio consuma molto più del previsto a causa di una configurazione mancante o di una falla contrattuale sfruttata dagli utenti. Un esempio reale: Vodafone offriva un router con SIM di backup cellulare per i casi di disservizio. Il contratto non impediva esplicitamente di usare il cellulare come connessione primaria; Cisternino lo usò così, e dopo pochi giorni Vodafone lo chiamò perché il monitoring aveva rilevato un utilizzo anomalo — e risolse il problema installando la linea fissa gratuitamente.

Le tecniche operative di capacity management includono:

- **Over-commitment della CPU**: assegnare più vCPU di quelle fisicamente disponibili, contando sull'utilizzo medio non simultaneo.
- **Dynamic scheduling dei vCPU**: bilanciamento automatico del carico.
- **Tiering dello storage per macchine offline**: quando una VM è spenta, il suo disco viene spostato su un tier più lento (meno costoso). Quando la VM si riavvia, lo storage viene migrato in live verso un tier più veloce, senza che l'utente se ne accorga — e nel frattempo si è risparmiato spazio sul tier premium.

![Diagramma Mermaid](images/mermaid-lezione-20-operations-e-considerazioni-finali-01.png)
*Fig. — Flusso tipico di capacity management per l'espansione di uno storage pool.*

---

## Change Management

Il **change management** è, tra tutti i processi operativi, quello più sottovalutato da chi si avvicina per la prima volta al mondo delle operations. Studenti e programmatori tendono a vederlo come burocrazia inutile; chi gestisce sistemi in produzione sa che la prima domanda quando qualcosa si rompe è sempre: *chi ha toccato qualcosa?*

Il change management ha come obiettivo principale registrare **ogni modifica** alla configurazione di ogni sistema — che sia effettuata da un umano o da un agente automatizzato. Lo strumento centrale è il **CMDB** (*Configuration Management Database*), che traccia lo stato di configurazione di tutta l'infrastruttura nel tempo.

> [!example] Esempio: aggiornamento di una versione di database
>
> Aggiornare la versione di un database in produzione è un'operazione rischiosa: il nuovo schema potrebbe essere incompatibile, l'upgrade potrebbe fallire a metà, il database potrebbe diventare irraggiungibile. La procedura standard è:
> 1. **Snapshot** della VM che ospita il database (costo temporaneo in I/O, ma reversibilità garantita)
> 2. Portare il servizio offline
> 3. Eseguire l'upgrade
> 4. Verificare il corretto funzionamento
> 5. **Se OK**: eliminare lo snapshot (tenerlo ha un costo continuo sulle performance di I/O, perché ogni accesso al disco richiede lookup multipli nella catena degli snapshot)
> 6. **Se KO**: fare rollback dallo snapshot, ripristinare il sistema, analizzare il problema prima del prossimo tentativo

---

## Incident Management e Problem Management

La distinzione tra **incidente** e **problema** è fondamentale nel modello ITIL che struttura le operations:

> [!definition] Incidente
>
> Un incidente è un **evento non pianificato** che interrompe o degrada un servizio. La gestione degli incidenti è *reattiva*: si risponde a qualcosa che è già successo.

> [!definition] Problema
>
> Un problema è un **incidente ricorrente** — o, più precisamente, la causa radice sottostante a più incidenti. La gestione dei problemi è *proattiva*: si interviene per eliminare la causa e prevenire che l'incidente si ripeta.

Il flusso di incident management segue questi passi:

![Diagramma Mermaid](images/mermaid-lezione-20-operations-e-considerazioni-finali-02.png)
*Fig. — Relazione tra incident management e problem management.*

> [!example] Esempio: disco rotto e storage pool esaurito
>
> Un disco si rompe. Lo storage pool esaurisce la capacità residua perché la ridondanza assorbiva spazio, ora non più disponibile. Una VM smette di funzionare.
>
> - **Incident management**: sostituire il disco rotto → la VM torna online.
> - **Root cause**: lo storage pool era già troppo pieno; la perdita di ridondanza ha consumato lo spazio rimanente.
> - **Problem management**: espandere il pool (aggiungere dischi o migrare dati su altri pool) in modo che un guasto futuro non esaurisca la capacità.
>
> Sostituire il disco risolve *il sintomo*, non *la causa*. Senza problem management, il prossimo guasto di un disco produrrà lo stesso effetto.

Un caso speciale di problem management *proattivo* è la predictive failure già descritta nel monitoring: sostituire un disco prima che si rompa è intervenire sulla causa ancora prima che si manifesti l'incidente.

> [!note] Incident vs. Problem: il punto chiave
>
> Incident management = **reattivo** → risolvi l'evento in corso.
> Problem management = **proattivo** → rimuovi la causa radice per evitare che si ripeta.
> I due flussi sono distinti ma si alimentano a vicenda: gli incidenti alimentano il backlog dei problemi, e i problemi risolti riducono la frequenza degli incidenti.

---

## Performance Management e Quality of Service

Negli SLA sono tipicamente incluse garanzie di performance (latenza, throughput, disponibilità). Se il sistema è sovraccarico — per overbooking eccessivo o per un collo di bottiglia non previsto in fase di progettazione — si può violare l'SLA anche senza che nulla sia formalmente "rotto".

Il performance management richiede di monitorare non solo i parametri di availability ma anche la bandwidth allocata per le VM su ogni hypervisor. Internamente ai datacenter moderni la rete è raramente il collo di bottiglia (25-50 Gbps aggregati per host sono la norma), ma la topologia di allocazione delle VM può creare situazioni in cui la bandwidth garantita non è rispettabile.

---

## Alerting e Reporting

Il sistema di **alerting** classifica i segnali su tre livelli: informativo (nessuna azione immediata), warning (monitorare con attenzione), fatale (servizio interrotto o SLA violato). Gli alert fatali richiedono intervento immediato.

Il **reporting** ha invece una valenza anche non tecnica. I report sono la documentazione che permette di:
- Dimostrare al management che un taglio di budget ha causato una violazione di SLA (*"vi avevo chiesto 5 milioni per lo storage, mi avete dato 4 milioni, ora stiamo violando gli SLA"*).
- Giustificare nuove richieste di risorse con dati storici.
- Fare **showback** — anche in contesti non-profit come l'università, dove non si fattura per l'uso delle risorse, si mostra comunque agli utenti quanto stanno consumando, creando consapevolezza e incentivando un uso efficiente.

---

## Considerazioni Finali sul Corso

### Il filo del corso

Il corso ha seguito una traiettoria che parte dal fisico e sale verso l'astratto:

1. **Fondamenta fisiche**: energia, cooling, cablaggio — perché un datacenter è prima di tutto un problema di energia e dissipazione del calore.
2. **Rete**: senza rete non esistono datacenter, esistono solo sistemi isolati. La rete è il *fondamento* del concetto stesso di datacenter.
3. **Fabric e switching**: come i dati si muovono internamente.
4. **Storage**: principi, tecnologie, architetture.
5. **Compute**: server, BMC, GPU, NPU.
6. **Virtualizzazione**: il cambiamento più importante degli ultimi 30 anni nel settore — senza virtualizzazione non esisterebbe il cloud.
7. **Cloud**: architettura di riferimento, orchestrazione, SLA, business continuity, security.
8. **Operations**: come si gestisce tutto questo nel tempo.

> [!tip] Il principio del bilanciamento
>
> Un tema ricorrente è che **il sistema efficiente non è quello con il miglior componente, ma quello bilanciato**. Una CPU potentissima accoppiata a storage lento produce comunque un sistema lento. Il collo di bottiglia limita sempre la prestazione complessiva. Il design di un datacenter — come di qualsiasi sistema informatico — è fondamentalmente un esercizio di bilanciamento tra componenti eterogenei.

### Workload divergence e AI

Intorno al 2008 i workload hanno iniziato a divergere significativamente: i requisiti di un web server sono profondamente diversi da quelli di un cluster per big data analytics o di un'infrastruttura per l'AI. L'idea di acquistare hardware generico e riutilizzarlo per qualsiasi scopo è tramontata. Oggi si progetta hardware specifico per workload specifici.

L'AI in particolare richiede enorme quantità di memoria (per i modelli), latenza ultra-bassa tra i nodi (per il training distribuito) e quindi prossimità fisica dei componenti. Questo spinge verso concentrazioni di potenza sempre maggiori in spazi sempre più ridotti — megawatt, gigawatt in singoli edifici — con sfide di cooling che stanno ridisegnando l'architettura stessa dei datacenter.

### Informazioni sull'esame

L'esame è orale, con prenotazione di slot via calendario. Il prof conduce una conversazione in cui:

- **Verifica la comprensione dei concetti chiave**, non la memorizzazione meccanica dei dettagli.
- **Propone problemi di architettura** da ragionare: dato un workload con certe caratteristiche, come si organizzano storage, compute e rete? Quale tipo di storage è appropriato? Quanti nodi?
- **Valuta la capacità di identificare soluzioni errate**: non esiste la soluzione ottimale, ma esistono soluzioni sbagliate — e il corso ha fornito gli strumenti per riconoscerle.

> [!example] Esempio di domanda d'esame (CERN)
>
> *Al CERN viene prodotto un flusso aggregato di 10 TB/s di dati dal rivelatore. Solo il 10% degli eventi è "interessante" e deve essere conservato; il 90% viene scartato dal livello computazionale. Come organizzereste storage, compute e rete? Usereste SAN o NAS? Quanti nodi servirebbero per il frontend? Come si dimensiona il backend?*
>
> L'obiettivo non è dare la risposta numericamente precisa, ma ragionare correttamente: il frontend deve gestire 10 TB/s, il backend deve ingestire 1 TB/s, il tipo di storage dipende dal pattern di accesso, la scelta tra SAN e NAS dipende dalla granularità degli accessi e dal tipo di parallelismo richiesto.

