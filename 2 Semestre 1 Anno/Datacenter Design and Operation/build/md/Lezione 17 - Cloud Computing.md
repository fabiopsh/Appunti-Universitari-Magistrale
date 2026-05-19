---
tags:
  - università/datacenter-design-and-operation
  - cloud-computing
  - service-models
  - deployment-models
data: 2026-05-14
lezione: "17 - Cloud Computing"
professore: "Antonio Cisternino"
---
# Cloud Computing

Il cloud computing è uno degli argomenti centrali del corso, non solo perché interessa direttamente l'architettura dei datacenter moderni, ma perché ha ridefinito il modo in cui le organizzazioni pensano all'IT. Il professore parte da un punto fondamentale: il cloud non è nato come tecnologia, ma come **modello di business**.

---

## Origini e contesto storico

Nei primi anni 2000, Amazon, Microsoft e Google stavano costruendo datacenter sempre più grandi per supportare picchi stagionali di traffico (Natale, estate). Fuori dai picchi, i server rimanevano inutilizzati. Qualcuno — in particolare Amazon — ebbe l'idea di monetizzare quella capacità in eccesso: perché non affittarla a terzi?

Questo segna il momento in cui nasce il cloud: non come invenzione tecnica, ma come risposta a un problema economico. Google aveva già offerto qualcosa di simile con BigTable — la possibilità di pagare per indicizzare dati usando le infrastrutture di ricerca di Google — ma Amazon trovò la ricetta giusta, quella che portò all'AWS che conosciamo oggi.

Il cambiamento più profondo non era tecnologico ma finanziario: si passava dalle **CapEx** (Capital Expenses, spese in conto capitale) alle **OpEx** (Operational Expenses, spese operative). Prima, un'organizzazione comprava server che possedeva; ora paga per un servizio, e se smette di pagare non le rimane nulla. Questo è un cambio di paradigma enorme.

> [!tip] La logica del capex vs opex
>
> Con CapEx si compra qualcosa che si possiede e ammortizza nel tempo. Con OpEx si paga per l'uso: se smetti di usare, smetti di pagare. Il cloud ha spostato la spesa IT verso OpEx, eliminando l'investimento iniziale ma introducendo una dipendenza continua dal fornitore.

Nella prima ondata cloud, molti Chief Information Officer pensarono di potersi liberare completamente dell'IT on-premise. La promessa era allettante: eliminare l'intero reparto IT aziendale delegando tutto al cloud. Poi arrivarono i problemi:

- **Sovranità dei dati**: usare cloud US significa che il governo americano può accedere ai dati. L'NSA stava spiando anche Angela Merkel; la Germania reagì imponendo a Microsoft di creare una società tedesca indipendente per gestire i suoi servizi sul territorio.
- **Banda e latenza**: una risonanza magnetica può produrre 7 TB in mezzora. Come si carica tutto sul cloud? Non si può. Con l'avvento dell'IoT, controllare un semaforo via cloud introduce una latenza inaccettabile.
- **Nuovi carichi di lavoro**: video, contenuti, documenti sono adatti al cloud; sistemi di controllo real-time no.

Questi limiti hanno ridimensionato la promessa del "full cloud", ma il cloud è rimasto fondamentale per molti carichi di lavoro.

---

## La definizione formale NIST

Il **National Institute of Standards and Technology** (NIST) americano ha fornito la definizione più usata e ancora valida di cloud computing:

> [!definition] Cloud Computing (NIST)
>
> Il cloud computing è un modello per abilitare l'accesso di rete conveniente e on-demand a un pool condiviso di risorse computazionali configurabili (reti, server, storage, applicazioni, servizi) che possono essere rapidamente provisionate e rilasciate con minimo sforzo di gestione o interazione con il fornitore.

Il nome "cloud" è evocativo: non si sa dove fisicamente girino le proprie risorse, così come non si sa dove sia fisicamente una nuvola nel cielo. Questa è resa possibile dalla virtualizzazione e dalla live migration: il proprio servizio può essere spostato fisicamente da un continente all'altro senza che l'utente se ne accorga.

---

## Le 5 caratteristiche essenziali del cloud

Il NIST identifica cinque caratteristiche che devono essere presenti perché un servizio possa essere definito cloud.

### On-demand self-service

Il consumatore può approvvigionare risorse computazionali unilateralmente, senza interagire con un operatore umano del fornitore. Si entra in un portale web, si selezionano le risorse, si inserisce la carta di credito e si ottengono le macchine virtuali in pochi minuti. Su AWS, per esempio, non esiste alcun processo di approvazione manuale.

### Broad network access

Le capacità sono disponibili attraverso la rete e accessibili tramite meccanismi standard che supportano client thin e thick: telefoni, tablet, laptop, workstation. Il corollario critico di questa caratteristica è che **senza rete non si ha accesso a nulla**: il cloud è inutile offline. Tant'è che alcune app pubblicitizzano il funzionamento offline come feature premium.

### Resource pooling

Le risorse del fornitore sono aggregate in un pool condiviso per servire più consumatori con un modello **multi-tenant**. Le risorse fisiche e virtuali vengono assegnate e riassegnate dinamicamente secondo la domanda.

Il concetto di **tenant** è fondamentale: un tenant è l'insieme di risorse usate da un'organizzazione all'interno del cloud. Un cloud multi-tenant ospita contemporaneamente l'Università di Pisa, l'Università di Bologna, e così via, ciascuna con proprie policy di sicurezza e identità.

Un aspetto importante è la **location independence**: il cliente in generale non conosce né controlla dove esattamente si trovano le sue risorse, ma può specificare la posizione a livello alto (paese, regione). Per le pubbliche amministrazioni in Italia, è obbligatorio per legge garantire la residenza dei dati in Europa.

### Rapid elasticity

Le risorse possono essere provisionate e rilasciate elasticamente — in alcuni casi automaticamente — per scalare rapidamente verso l'alto e verso il basso in funzione della domanda. Per il consumatore, le risorse sembrano *infinite*: è la dimensione del datacenter ad essere così grande che quasi sempre c'è spazio per un'altra macchina virtuale.

> [!example] Elasticità: l'esempio dei videogiochi
>
> Ubisoft non possiede un proprio datacenter dimensionato per il picco di lancio dei suoi giochi. Nelle settimane del lancio c'è un ramp-up enorme di richieste, poi il traffico cala. Se Ubisoft acquistasse hardware per il picco, lo lascerebbe quasi sempre inutilizzato. Con il cloud invece si aggiungono risorse durante il picco, si pagano, e si rilasciano quando il traffico cala.

> [!example] Elasticità automatica: il sistema delle tasse
>
> Il sistema di dichiarazione dei redditi in Italia ha un picco enorme nel giorno di scadenza (tutti aspettano l'ultimo momento). Con l'elasticità automatica si può configurare: "se la latenza delle risposte del web server supera X, aggiungi un worker; se scende sotto Y, rimuovine uno". Il sistema scala da solo, pagando solo per le risorse effettivamente usate.

È importante distinguere **scala** (dimensione totale dell'infrastruttura) da **elasticità** (capacità di allocare e deallocare rapidamente su scale temporali brevi). Comprare un server e venderlo dopo 5 anni non è elasticità; richiedere 1000 CPU e ottenerle in 5 minuti, per poi rilasciarle in un'ora, lo è.

### Measured service

I sistemi cloud controllano e ottimizzano automaticamente l'uso delle risorse tramite capacità di misurazione. L'uso delle risorse può essere monitorato, controllato e comunicato, garantendo trasparenza sia al fornitore che al consumatore.

La misurazione avviene a un livello di astrazione: il fornitore non ti dice su quale specifico disco SSD stanno i tuoi dati, ma ti propone livelli di servizio — bronze, silver, gold — ognuno con garanzie di throughput diverse (es. bronze: 500 MB/s, silver: 1 GB/s, gold: 5 GB/s). Paghi per il livello, non per il dispositivo specifico.

![](images/dcdo-cloud-nist-definition.png)
*Fig. — Le cinque caratteristiche essenziali del cloud computing secondo il NIST.*

---

## Benefici del cloud

Il cloud porta numerosi vantaggi rispetto al modello on-premise tradizionale.

**Business agility**: la capacità di rispondere rapidamente alle opportunità di mercato senza aspettare mesi per acquistare, installare e configurare hardware.

**Riduzione dei costi IT**: questa è la promessa più pubblicizzata, ma anche la più insidiosa. I costi materiali (hardware) sono facilmente misurabili. I costi del software invece no: il prezzo del software è quello che il mercato accetta di pagare, non quello che costa produrlo. Le licenze HCI (Hyper-Converged Infrastructure) sono diventate così costose che molte organizzazioni stanno tornando allo storage di rete tradizionale. Attenzione: si può facilmente finire per pagare più di prima.

**High availability**: un cloud provider con decine di datacenter globali può offrire ridondanza e resilienza irraggiungibili per una singola organizzazione. Se un datacenter viene colpito (per esempio da un attacco missilistico come nell'esempio citato), il traffico viene reindirizzato altrove.

**Flexible scaling**: possibilità di scalare dinamicamente sia horizontalmente (scale-out) che verticalmente (scale-up).

**Semplificazione dello sviluppo**: le organizzazioni in passato mantenevano il doppio dell'infrastruttura — una per la produzione, una per il test. Con il cloud, si provisiona un ambiente di test, si usa, si rilascia.

---

## Limiti e svantaggi

I drawback del cloud sono reali e rilevanti nella pratica.

Il problema della **sovranità dei dati** è ancora aperto. Il governo americano rivendica il diritto di accedere a tutti i dati conservati su cloud di proprietà americana, indipendentemente dalla posizione geografica. Microsoft, Google e altri hanno fatto azioni legali per opporsi, con successo parziale. La Germania ha risolto il problema imponendo a Microsoft di creare una controllata tedesca indipendente per gestire i dati tedeschi.

Il **vendor lock-in** è strutturale: se si costruisce tutta la propria infrastruttura su API proprietarie di un singolo cloud provider, cambiarlo in seguito è estremamente costoso. La diversificazione degli investimenti e l'uso di API aperte mitigano il problema, ma non lo eliminano.

Il **software licensing** è un territorio complesso: ci sono professionisti pagati esclusivamente per conoscere i dettagli dei contratti di licenza Microsoft. Un cambiamento nelle condizioni di licenza può ribaltare completamente la convenienza economica di una scelta tecnologica.

---

## I modelli di servizio cloud

Il NIST formalizza tre modelli di servizio principali che è indispensabile conoscere. Il professore usa l'analogia della pizza per renderli immediatamente memorizzabili.

> [!tip] L'analogia della pizza
>
> Pensate alla pizza come all'insieme di tutto ciò che serve per mangiare: ingredienti, impasto, cottura, forno, gas/luce, tavolo, bibita.
> - **On-premise**: si fa tutto a casa (si gestisce tutto).
> - **IaaS**: si compra la pizza surgelata al supermercato e la si cuoce a casa (il fornitore gestisce fino all'OS, tu gestisci il resto).
> - **PaaS**: si ordina la consegna a domicilio (il fornitore gestisce tutto tranne la personalizzazione dell'applicazione).
> - **SaaS**: si va al ristorante (il fornitore gestisce tutto, tu usi solo il servizio finale).

### Infrastructure as a Service (IaaS)

Il fornitore offre capacità computazionale grezza: processori, storage, reti. Il consumatore può deployare e far girare qualsiasi software, inclusi sistema operativo e applicazioni. Il consumatore **non gestisce** l'infrastruttura cloud sottostante, ma **ha controllo** su OS, storage, applicazioni deployate e — limitatamente — sui componenti di rete (es. firewall).

In pratica: il fornitore installa l'hardware e porta l'OS "vergine"; tu lo configuri, aggiorni, gestisci tutta la pila software sopra.

![](images/dcdo-cloud-iaas-stack.png)
*Fig. — In IaaS il fornitore gestisce hardware e virtualizzazione; il consumatore gestisce da OS in su.*

### Platform as a Service (PaaS)

Il consumatore deploya applicazioni proprie su un'infrastruttura cloud usando linguaggi, librerie e tool supportati dal fornitore. Non gestisce né conosce l'OS sottostante: quello è responsabilità del fornitore. Si ha controllo solo sull'applicazione.

**Esempi pratici**: WordPress è un tipico PaaS. Vuoi un sito web? Non ti preoccupi del web server, del PHP, del sistema operativo. Acquisti un'istanza WordPress, la personalizzi con plugin e temi tuoi, e il fornitore gestisce tutto il resto. Salesforce è un altro esempio sul lato commerciale.

![](images/dcdo-cloud-paas-stack.png)
*Fig. — In PaaS il fornitore gestisce fino al runtime; il consumatore gestisce solo l'applicazione.*

### Software as a Service (SaaS)

Il consumatore usa direttamente l'applicazione del fornitore girante su infrastruttura cloud. Non gestisce nulla dell'infrastruttura, della piattaforma, o dell'applicazione stessa — solo la configurazione utente.

**Esempi**: Gmail è SaaS via browser. Microsoft 365 è SaaS con applicazioni scaricabili localmente ma intrinsecamente legate al cloud: se si smette di pagare, le app smettono di funzionare dopo 30 giorni.

![](images/dcdo-cloud-saas-stack.png)
*Fig. — In SaaS tutto è gestito dal fornitore; il consumatore usa solo il prodotto finale.*

### Cloud Services Brokerage (CSB)

La **brokerage** è un livello intermedio che cerca di allocare le risorse cloud sul fornitore più conveniente tra quelli disponibili (AWS, Azure, GCP…). In teoria interessante; in pratica, quando Microsoft e altri hanno adottato la strategia di *matching* automatico dei prezzi dei concorrenti, il vantaggio economico del broker è quasi scomparso.

---

## I modelli di deployment cloud

Oltre ai modelli di servizio, esistono modelli di *deployment* che definiscono chi può accedere all'infrastruttura.

### Public cloud

L'infrastruttura è provisioned per uso pubblico aperto. Chiunque può creare un account su AWS, Azure, GCP, Oracle Cloud e allocare risorse, senza restrizioni. "Pubblico" non significa gratuito: significa accessibile a tutti.

### Private cloud

L'infrastruttura è dedicata esclusivamente a una singola organizzazione. Può essere gestita dall'organizzazione stessa o da terzi, e può esistere on-premise o off-premise. L'Università di Pisa, per esempio, gestisce un proprio private cloud.

Il punto chiave: il cloud privato non è privato perché è *owned* dall'organizzazione, ma perché solo quella organizzazione può allocare risorse su di esso.

### Community cloud

Infrastruttura condivisa tra organizzazioni con mission o requisiti comuni (es. università italiane, PA europee). Può essere on-premise o gestita da terzi.

### Hybrid cloud

Combinazione di due o più infrastrutture cloud distinte (private, community, public) che rimangono entità separate ma sono collegate da tecnologie standardizzate che abilitano la portabilità di dati e applicazioni.

> [!example] UniPi come hybrid cloud
>
> Quando accedi a un servizio universitario di Pisa, stai probabilmente usando tre cloud diversi senza saperlo: i servizi di didattica girano nel datacenter di San Piero (cloud privato UniPi), Alunni gira su Cineca a Bologna, i documenti sono su OneDrive (Microsoft Azure). Tutto appare come un'unica esperienza con una singola identità. Questo è hybrid cloud in pratica.

![](images/dcdo-cloud-hybrid-model.png)
*Fig. — Il modello hybrid cloud combina infrastrutture cloud diverse collegate da standard aperti.*

> [!note] Impatto del private cloud sull'organizzazione IT
>
> Il cloud — anche nella sua versione privata — ha rivoluzionato il modello organizzativo dell'IT. Prima ogni progetto acquistava il proprio server; la capacità inutilizzata era spreco puro. Con il private cloud, si gestisce un pool condiviso da cui ogni progetto preleva le risorse di cui ha bisogno, restituendole quando non servono. Tecnologie come VMware vCloud Foundation, Microsoft Azure Local (ex Azure Stack), e Microsoft System Center consentono di implementare questo modello on-premise.

---

## Il Cloud Computing Reference Model

Una volta che le architetture cloud convergono verso pattern comuni, ha senso definire un **reference model** — una mappa condivisa per descrivere come si organizza un'infrastruttura cloud. Il modello OASIS (ripreso dal NIST) è ancora valido dopo oltre 12 anni.

![](images/dcdo-cloud-reference-model.png)
*Fig. — Il reference model OASIS per il cloud computing: layer funzionali e aspetti cross-cutting.*

Il modello è strutturato in layer funzionali verticali e aspetti cross-cutting orizzontali.

### Physical layer

Alla base c'è sempre il silicio: compute, storage, network — tutto ciò che abbiamo studiato nel corso. La maggior parte del cloud è implementata tramite virtualizzazione, ma esiste anche il **bare metal cloud**: invece di una VM, si provisiiona un intero server fisico programmandolo via API (es. Redfish). Meno elasticità di granularità (solo interi server), ma utile per HPC.

### Virtual layer

È il layer cruciale: astrae le risorse fisiche e le presenta come pool omogeneo da cui allocare slice. Macchine virtuali, storage virtuale, reti virtuali (VLAN, vSAN) vivono qui. La virtualizzazione è ciò che rende possibile il resource pooling.

### Control layer

È l'API che consente di dire "allocami una VM con queste caratteristiche" e di ottenere il risultato. Il control layer sa dove ci sono risorse libere, le marca come occupate, tiene il libro contabile. È il "cervello" operativo del cloud: quando si fa una richiesta, il control layer interroga l'inventario, trova capacità disponibile, alloca e conferma.

### Administration / Orchestration layer

Sopra il control layer c'è l'automazione: workflow che definiscono "se succede X, esegui Y, poi Z". Gestisce il provisioning complesso (allocare una VM, poi aspettare che sia pronta, poi configurarla, poi avvisare l'utente), il decommissioning hardware (quando un server va in pensione: wipe dei dischi, rimozione dal configuration database, segnalazione), e tutto ciò che altrimenti richiederebbe intervento umano.

> [!tip] Economia dell'automazione
>
> I grandi cloud provider gestiscono decine di milioni di server con pochissimo personale fisico (poche decine di persone per strutture enormi). Questo è possibile solo perché l'orchestration layer automatizza praticamente tutto: dalla sostituzione di un disco guasto alla sostituzione di un intero rack.

### Service layer

Il layer più alto: il portale web dove l'utente vede il catalogo servizi, si autentica, seleziona le risorse, paga e le riceve. Traduce le richieste utente in task che scendono verso l'orchestration e poi il control layer.

### Aspetti cross-cutting

Sicurezza e business continuity non appartengono a un singolo layer: permeano tutti. La sicurezza deve essere presente a livello fisico (accesso fisico al datacenter), virtuale (isolamento tra tenant), di controllo (autenticazione alle API), di orchestration, e di servizio. La business continuity — RAID, backup, replication, failover tra datacenter — è ugualmente trasversale.

---

## Greenfield vs. Brownfield

Due termini del gergo IT fondamentali:

**Greenfield**: si parte da zero. Hardware nuovo, sistema deployato ex novo, test puliti, consegna. È il caso ideale.

**Brownfield**: si deploya qualcosa in un'infrastruttura già esistente. Le decisioni prese 10, 20, 30 anni fa condizionano le scelte odierne. Il professore gestisce servizi universitari da quasi 10 anni e ancora si confronta con scelte architetturali di decenni fa.

---

## Costruire il cloud: non solo tecnologia

Una lezione chiave: costruire un'infrastruttura cloud non è solo un problema tecnico. Ci sono almeno quattro dimensioni non tecniche altrettanto critiche.

### Governance

La governance è la distribuzione attiva di diritti decisionali e responsabilità tra i vari stakeholder dell'organizzazione. Chi decide quale servizio attivare? Chi approva il budget? Chi è responsabile in caso di incidente?

I modelli principali sono tre: **centralizzato** (un'autorità centrale governa tutte le business unit), **distribuito** (ogni unità ha la propria governance autonoma, tipico di grandi organizzazioni), **federato** (combinazione dei due, con autonomia locale ma coordinamento centrale).

UniPi usa un modello prevalentemente centralizzato: la dimensione dell'organizzazione lo consente.

Il cloud ha introdotto nuovi ruoli organizzativi:
- **Service manager**: responsabile di un singolo servizio
- **Account manager**: gestisce il rapporto con il cliente/utente
- **Cloud architect**: progetta l'architettura complessiva del cloud
- **Service operation manager**: responsabile dell'intera infrastruttura e di tutti i servizi su di essa

### Finance e procurement

In un'organizzazione pubblica italiana, la spesa IT è regolata da norme precise: acquisti diretti fino a ~€139.000, oltre tale soglia si richiede gara europea (€214.000+), con tempi minimi di sei mesi. Se un server si rompe e bisogna lanciare una gara europea, per sei mesi non c'è server.

Questo significa che il procurement deve essere **proattivo**: bisogna prevedere i fabbisogni futuri, pianificare le gare prima che le risorse servano. L'Università di Pisa spende circa 6 milioni/anno in IT: 80.000 switch, 2000 access point, datacenter e cloud privato.

Il **chargeback** è il meccanismo con cui si attribuisce il costo delle risorse cloud ai reparti o progetti che le usano. Non si chiede denaro (in un ente pubblico), ma si tiene traccia di chi usa quanto. Il Dipartimento di Informatica che usa più VM del Dipartimento di Filosofia dovrebbe ricevere un contributo proporzionalmente maggiore.

Modalità di chargeback nel cloud:
- **Pay-as-you-go**: paghi per quello che usi
- **Subscription**: abbonamento per un periodo (come Microsoft 365 annuale)
- **By peak**: si paga per il picco di utilizzo raggiunto
- **User-based**: costo per utente (il modello AI aziendale è spesso così: ogni utente ha una quota di token)

### Service Level Agreement (SLA)

Quando le proprie risorse sono "da qualche parte nel cloud" e non si può andare fisicamente a verificarle, l'unica garanzia possibile è quella **contrattuale**. Uno SLA è la parte del contratto che specifica i parametri del servizio: disponibilità (es. 99.9%), schedule di manutenzione, livelli di performance, tempi di risposta del supporto, e le compensazioni in caso di violazione.

Gli SLA di tutti i servizi Microsoft online, con versioni storiche e in tutte le lingue, sono pubblici e consultabili sul sito Microsoft. Studiarne uno è utile per capire cosa garantisce realmente un cloud provider.

### Vendor lock-in

La dipendenza da un singolo fornitore è un rischio strategico. Se il fornitore cancella un prodotto, cambia le condizioni di licenza, o aumenta i prezzi, l'organizzazione è in difficoltà. Strategie di mitigazione: diversificazione degli investimenti, preferenza per API e standard aperti.

![](images/dcdo-cloud-governance-models.png)
*Fig. — I tre modelli di governance cloud: centralizzato, distribuito, federato.*

---

## Il physical layer e il virtual layer: riepilogo

Il professore dedica gli ultimi minuti a scorrere rapidamente i layer fisici e virtuali già trattati nel corso, confermando che i concetti si incastrano con quanto visto.

Il **physical layer** comprende compute (server, CPU, GPU), storage (a blocchi, a file, a oggetti — unified storage come configurazione ibrida), e network (Fibre Channel per storage, iSCSI sempre meno usato, Ethernet convergente). Le note nelle slide originali fanno riferimento alle tecnologie meccaniche di dischi prima della diffusione degli SSD, ma le categorie logiche (block, file, object) rimangono attuali.

Il **virtual layer** è composto da macchine virtuali (file VMDK, virtual appliance), storage virtuali (LUN thin-provisioned, vSAN), e reti virtuali. La **PVLAN** (*Private VLAN*) merita un dettaglio: è una VLAN che vieta il broadcast orizzontale tra host. Se siete connessi al Wi-Fi universitario, siete su una PVLAN — per questo non potete fare ping tra due device sulla stessa rete wireless: la rete non consente comunicazione diretta tra client, solo north-south (client → gateway).

> [!note] Prossime lezioni
>
> Il professore ha annunciato che la lezione successiva partirà dal **control layer** e dall'**orchestration layer** — le parti veramente nuove rispetto a ciò già coperto nel corso. Poi seguiranno sicurezza e operazioni, e il venerdì successivo la visita al datacenter di San Piero.

---

