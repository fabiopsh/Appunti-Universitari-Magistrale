---
tags:
  - università/datacenter-design-and-operation
  - cloud
  - control-layer
  - orchestrazione
  - sla
  - virtualizzazione
data: 2026-05-15
lezione: "18 - Control Layer, Service Layer, Orchestrazione e SLA"
professore: "Antonio Cisternino"
---

# Control Layer, Orchestrazione e SLA

La lezione riprende dal punto in cui si era interrotto il ciclo precedente, cioè dal **Control Layer**, l'ultimo strato funzionale dell'architettura di riferimento del cloud che non era ancora stato discusso in dettaglio. Il professore chiarisce subito la prospettiva corretta: dal punto di vista informatico, nessuno degli strati funzionali del cloud è particolarmente complesso concettualmente. Le difficoltà reali risiedono nell'hardware, nella topologia e nelle scelte implementative dei singoli layer. L'obiettivo della lezione è passare rapidamente sui layer funzionali per poi spostarsi sugli aspetti trasversali più interessanti: sicurezza, business continuity, service management e, soprattutto, framework legali e compliance.

---

## Il Control Layer

### Posizione nell'architettura

Il control layer si inserisce sopra il virtual layer (o direttamente sopra il physical layer, in assenza di virtualizzazione). Riceve richieste dagli strati superiori — service e orchestration layer — e si occupa di provisioning delle risorse fisiche e virtuali necessarie per soddisfarle.

![Cloud Infrastructure Reference Model con Control Layer evidenziato](../../../General/Images%20and%20Documents/dcdo_cloud_reference_model_control_layer.png)
*Fig. — Il Cloud Reference Model con il Control Layer evidenziato (in giallo). Sopra ci sono Service Layer e Orchestration Layer; sotto il Virtual Layer e il Physical Layer.*

> [!definition] Control Layer
>
> Include gli strumenti software responsabili di gestire e controllare l'infrastruttura cloud sottostante, abilitando il provisioning delle risorse IT per la creazione di servizi cloud.

### Il Control Software

Il control software lega insieme le risorse sottostanti. Le sue funzioni principali sono: **resource pooling**, **allocazione dinamica** delle risorse, **ottimizzazione dell'utilizzo** e gestione centralizzata di tutti gli asset. Quest'ultima caratteristica spiega perché questo software è stato adottato da moltissime organizzazioni enterprise anche al di fuori di contesti cloud puri: offre un punto unico da cui gestire in blocco tutti i sistemi, eseguire operazioni di manutenzione coordinate, applicare patch di sicurezza svuotando il nodo interessato prima di portarlo offline, riavviarlo e poi ribilanciare le risorse — il tutto senza che nessun utente se ne accorga.

Il control software funziona bene solo se l'ambiente è **omogeneo**: se le procedure sono standardizzate e replicabili, l'automazione ha senso. Altrimenti, ogni sistema richiederebbe attenzione individuale, negando i vantaggi del layer.

Un ruolo cruciale del control software è quello di **adapter**: astrae il brand e la tecnologia dei componenti fisici dagli strati superiori. Il cloud non sa se lo storage è Dell, HP o VAS Data — non importa. Il control layer si preoccupa dei dettagli hardware e presenta agli strati superiori un'interfaccia uniforme. Analogamente, tutta l'infrastruttura espone **API** che permettono di automatizzare e orchestrare le operazioni programmaticamente.

### Element Manager vs Unified Manager

Il control software può essere organizzato in due modi:

**Element Manager**: ogni componente infrastrutturale (compute, network, storage) viene gestito da un software dedicato fornito dal vendor. Ogni element manager espone le proprie API verso le risorse che gestisce.

![Schema degli Element Managers: uno per compute, uno per network, uno per storage](../../../General/Images%20and%20Documents/dcdo_cloud_element_managers.png)
*Fig. — Gli Element Managers gestiscono indipendentemente i tre pilastri: compute, network e storage.*

**Unified Manager**: un singolo software fornisce un'interfaccia unificata per configurare e provisioning tutte le risorse. Internamente si interfaccia con gli element manager tramite API, ma presenta all'amministratore e agli strati superiori una visione olistica e coerente dell'intera infrastruttura.

![Schema dell'Unified Manager sopra gli Element Managers](../../../General/Images%20and%20Documents/dcdo_cloud_unified_manager.png)
*Fig. — L'Unified Manager fornisce un singolo punto di controllo, coordinando internamente gli element manager di compute, network e storage.*

In pratica, le implementazioni reali combinano entrambi gli approcci: l'unified manager gestisce le operazioni di alto livello, mentre gli element manager si occupano dei dettagli specifici di ciascun componente.

---

## Fasi del Provisioning delle Risorse

### Resource Discovery

Prima di poter allocare qualcosa, il sistema deve **conoscere le risorse disponibili**. La resource discovery è il processo con cui nuove risorse vengono aggiunte al resource pool. Questo è il riflesso dell'industrializzazione del datacenter: non si interviene sul singolo disco rotto, si aspetta che l'intero pod scenda sotto una soglia (es. 20% di risorse disponibili), si decommissiona tutto il pod, lo si sostituisce fisicamente, e poi le nuove risorse vengono scoperte automaticamente e aggiunte al pool. Tutto ciò vale per compute, storage e network.

### Resource Pool Management e Grading

Una volta note le risorse, queste vengono **astratte e classificate**. Non ha senso tracciare ogni dettaglio tecnico — se un link è da 25 Gbps con fibra ottica OM4 o meno — per scopi di billing, monitoraggio e provisioning. Si definiscono invece **categorie equivalenti**, all'interno delle quali le risorse sono considerate intercambiabili anche se tecnicamente diverse.

Il meccanismo tipico è il **grading**: si definiscono livelli qualitativi come *Gold*, *Silver*, *Bronze* per ogni tipo di risorsa (compute, storage, network). Ogni livello ha un costo diverso e garantisce caratteristiche diverse. Per esempio:

- **Gold Storage**: include drive Flash, FC e SATA, supporta automated storage tiering, capacità 3 TB, RAID 5.
- **Silver Storage**: mix bilanciato tra Flash, FC e SATA, RAID 1+0.
- **Bronze Storage**: solo drive FC, nessun tiering automatico.

Il grading permette di offrire ai consumatori scelte differenziate e consente alla piattaforma di prendere decisioni di allocazione senza conoscere i dettagli fisici sottostanti.

### Resource Provisioning

Quando un consumatore seleziona un servizio dal catalogo, il sistema alloca risorse dal pool corrispondente alla grade richiesta. Se non ci sono risorse sufficienti, la risposta è semplice: il servizio non può essere creato. Un esempio classico è quello di una virtual machine più grande di qualunque singolo server disponibile: anche se il server è libero al 100%, la VM semplicemente non può essere creata perché è fisicamente impossibile.

---

## L'Approccio Software-Defined

Il naturale corollario della gestione centralizzata a scala è la **software-defined infrastructure**: separare le funzioni di management dai componenti fisici e delegarle a controller software. Questo approccio si è affermato a partire dal 2008 circa con standard come **OpenFlow** per il networking e poi VXLAN per gli overlay di rete.

![Schema del Software-Defined Controller con i tre domini](../../../General/Images%20and%20Documents/dcdo_cloud_software_defined_controller.png)
*Fig. — Il software-defined controller astrae compute, storage e network, esponendo API verso le applicazioni esterne e comunicando con i componenti fisici tramite API standardizzate.*

Il vantaggio originale era economico: il software-defined permetteva di evitare hardware proprietario costoso (specialmente storage dedicato) usando hardware commodity. Oggi la situazione si è in parte invertita: i vendor software hanno alzato i prezzi delle licenze al punto che in alcuni casi conviene tornare all'hardware dedicato. Le dinamiche cambiano nel tempo.

Il software-defined si applica a tutti e tre i pilastri:
- **Compute**: il server può essere provisioned completamente via software (es. Redfish sul BMC).
- **Storage**: storage pools gestiti via API, indipendentemente dal vendor.
- **Network**: switch programmabili via OpenFlow, VXLAN per creare VLAN overlay senza configurare fisicamente ogni switch.

---

## Tecniche di Resource Management

### Modelli di Allocazione

Esistono due approcci fondamentali:

> [!definition] Relative Resource Allocation
>
> Le risorse vengono allocate proporzionalmente rispetto agli altri servizi. Non molto diffuso in pratica.

> [!definition] Absolute Resource Allocation
>
> Si definisce un range quantitativo: un **lower bound** (garanzia minima) e un **upper bound** (limite massimo di consumo). Il cloud provider firma contratti SLA in base a questi range, quindi deve rispettarli e gestire la contesa tra tenant.

Il problema dell'allocazione assoluta è la **contesa tra tenant**: se tutti i tenant chiedono il massimo simultaneamente, le risorse si esauriscono. Il cloud provider deve bilanciare le allocazioni in modo da poter onorare i contratti di tutti, altrimenti si espone a responsabilità legale.

### Hyper-Threading

> [!definition] Hyper-Threading
>
> Tecnica Intel che consente a un singolo core fisico di apparire come due core logici, eseguendo due stream di istruzioni in modo parzialmente parallelo condividendo le unità computazionali fisiche.

Il professore spiega l'evoluzione in dettaglio. Negli anni '90, i thread emersero come forma leggera di concorrenza: più flussi di esecuzione all'interno dello stesso processo, con cambio di contesto più economico rispetto ai processi (non si aggiornano le strutture dati della memoria paginata, perché i thread dello stesso processo condividono lo spazio di indirizzamento). I vendor hardware iniziarono a ottimizzare questo pattern.

L'idea chiave dell'hyper-threading è che **non tutti i thread usano tutte le unità computazionali contemporaneamente**: se un thread fa aritmetica intera e l'altro fa operazioni floating point, possono andare in parallelo sullo stesso core. Il core viene progettato con due pipeline fetch/execute che si contendono le unità computazionali fisiche solo quando necessario.

![Diagramma dell'hyper-threading: tre VM, processori virtuali, core logici su un dual-core fisico](../../../General/Images%20and%20Documents/dcdo_cloud_hyperthreading.png)
*Fig. — L'hyper-threading: ogni core fisico espone due core logici. Le VM vedono processori virtuali che si mappano sui core logici, non fisici.*

> [!warning] HPC e Hyper-Threading
>
> In ambienti HPC (High Performance Computing), l'hyper-threading va spesso **disabilitato**: i calcoli sono prevalentemente floating point, quindi entrambi i thread si contendono la stessa FPU, creando più contesa che parallelismo. Il risultato può essere più lento che con un solo thread per core.

Per il cloud generale (IO-bound, network-oriented), l'hyper-threading equivale quasi a raddoppiare i core. Con un server da 56 core logici, si possono allocare tranquillamente 112 core virtuali alle VM senza un vero degrado delle prestazioni, perché la maggior parte del tempo la CPU è idle in attesa di IO. Questo **overbooking dei core** è la norma nel cloud.

### Memory Ballooning (Dynamic Memory Allocation)

L'overbooking della memoria si fa con una tecnica chiamata **ballooning**. Un driver installato nella VM comunica con l'hypervisor. L'hypervisor dichiara alla VM che una parte della memoria è occupata (il "balloon"), riducendo la memoria disponibile percepita dalla VM. L'hypervisor monitora continuamente la pressione di memoria: se vede che una VM sta facendo heavy paging (cioè soffre di mancanza di memoria), può **deflate** il balloon — ridurre la quantità di memoria dichiarata occupata — così la VM percepisce di avere più memoria disponibile.

Questo permette di avere più VM attive contemporaneamente di quante la memoria fisica supporterebbe se tutte fossero pienamente allocate. Se la contesa diventa reale (tutte le VM vogliono tutta la memoria), si definiscono **priorità** per decidere chi aspetta.

Un'ottimizzazione ulteriore è il **memory page sharing**: se due VM eseguono lo stesso sistema operativo, quasi certamente hanno pagine di memoria identiche. L'hypervisor può identificarle e far puntare entrambe le VM alla stessa pagina fisica, risparmiando memoria.

### Virtual Storage Provisioning e Storage Management

Il **thin provisioning** applicato allo storage funziona allo stesso modo: si presenta alla VM più spazio di quello fisicamente allocato. Lo spazio reale viene allocato solo quando i dati vengono effettivamente scritti.

Il **storage pool rebalancing** previene la situazione in cui un server accumula troppe VM mentre altri rimangono quasi vuoti: il sistema migra automaticamente VM da nodi sovraccarichi a nodi meno utilizzati.

L'**automated storage tiering** gestisce automaticamente dove i dati vengono fisicamente conservati: i dati più acceduti di recente vengono tenuti su SSD (o addirittura in cache DRAM), mentre i dati freddi vengono migrati su dischi meccanici più lenti ma più economici. Il movimento avviene in modo trasparente alle applicazioni.

---

## Demo: SCVMM al Polo Universitario di San Piero a Grado

Il professore mostra dal vivo il **System Center Virtual Machine Manager (SCVMM)**, il control layer del private cloud dell'Università di Pisa. Le API sono basate su PowerShell (eredità di un'epoca in cui le REST API HTTP erano meno diffuse), ma il concetto è identico a quello di qualsiasi control layer moderno.

L'interfaccia mostra:
- Il **fabric**: il pool di risorse totale, con classificazione dei port profile (alta banda, media banda, etc.) per taggare la rete.
- Lo **storage**: livelli *bronze*, *flash*, *hyper-class*. L'università usa un'infrastruttura iper-convergente, quindi lo storage è nel medesimo pool dei server.
- La **logical network**: astrazione software-defined che mappa VLAN fisiche diverse (es. VLAN 1800 in datacenter 1 e VLAN 1801 in datacenter 2) a un'unica rete logica "pubblica". Il cloud non sa quale VLAN fisica viene usata; sa solo che si tratta di traffico pubblico.
- La **library delle immagini**: repository da cui clonare le VM.

Degno di nota è il **service template** per il sistema di registrazione degli esami dell'università: due macchine virtuali (frontend + backend database), collegate a specifiche reti, con il frontend scalabile (da 1 a 5 istanze) e il database non scalabile orizzontalmente (si scala verticalmente). Quando si crea una nuova istanza del servizio, SCVMM alloca entrambe le VM, le configura e le connette automaticamente.

La creazione di una singola VM tramite wizard mostra come il sistema suggerisca automaticamente il nodo ottimale per il bilanciamento del carico. Tutto ciò che viene fatto graficamente si traduce in uno **script PowerShell** generato automaticamente — conferma che anche le interfacce grafiche non "controllano" direttamente: generano chiamate API.

> [!tip] Intuizione chiave sul bookkeeping
>
> Il bookkeeping è un'attività critica nel cloud: tenere traccia di ogni VM, ogni servizio, ogni tenant è essenziale perché nel cloud pubblico si arriva facilmente a milioni di istanze. Chi rimuove le risorse abbandonate se non c'è traccia di chi le ha create? Un errore di bookkeeping porta a "VM fantasma" che consumano risorse senza che nessuno ne sia responsabile.

---

## Il Service e Orchestration Layer

![Cloud Reference Model con Service e Orchestration Layer evidenziati](../../../General/Images%20and%20Documents/dcdo_cloud_reference_model_service_layer.png)
*Fig. — Nel Reference Model del modulo 6, Service Layer (blu) e Orchestration Layer (arancione) sono in cima all'architettura.*

### Service Layer

Il service layer è il livello più alto dell'architettura cloud. Le sue funzioni principali sono:

- **Definire il service catalog**: la lista dei servizi disponibili, con tutte le informazioni per il consumatore.
- **On-demand self-provisioning**: il consumatore può richiedere un servizio senza intervento umano da parte del provider.
- **Presentare le cloud interface**: interfaccia funzionale (usare il servizio) e interfaccia di gestione (gestire l'istanza del servizio).

> [!definition] Service Catalog
>
> Elenco strutturato di tutti i servizi offerti dal provider. Ogni voce include: categoria, nome, descrizione, feature e opzioni, aspettative di qualità del servizio, prezzo, tempi di provisioning, riferimento a SLA e documentazione.

Il professore mostra il portale Azure come esempio concreto: una quantità enorme di servizi categorizzati (VM, database, firewall, etc.), ognuno con varianti e opzioni. Quello è il service catalog in produzione.

### Cloud Portal

Il cloud portal è la UI del service layer. Ha due funzioni:

1. **Presentazione**: mostra il service catalog, le istanze attive e le interfacce di gestione.
2. **Interazione con l'orchestration layer**: invia le richieste di servizio all'orchestratore e mostra gli aggiornamenti di stato.

Tutto nel cloud portal è **asincrono**: quando si richiede una VM, si emette una richiesta che entra in una coda. Il portal mostra lo stato dell'ordine in tempo reale (in attesa → in progress → pronto).

### Standard di Portabilità

Il professore racconta la storia degli standard di portabilità cloud con un tono sarcastico:

**TOSCA** (*Topology and Orchestration Specification for Cloud Applications*): tentativo di standardizzare un linguaggio per definire servizi in modo portabile tra cloud diversi. Sostanzialmente fallito. La realtà è che il cloud si è biforcato in due categorie:

1. **Servizi portabili** (tipicamente IaaS): si esporta la VM, si importa nell'altro cloud. Nessun standard sofisticato serve davvero.
2. **Servizi locked-in** (tipicamente PaaS/SaaS): Google Bigtable, Alexa, modelli AI. Questi servizi non sono portabili per natura — si comportano diversamente anche con lo stesso prompt. Nessuno standard può risolvere questa differenza semantica.

**OVF** (*Open Virtualization Format*): standard aperto per il packaging di virtual appliance. Ancora in uso, soprattutto nell'ecosistema VMware. Funziona perché il problema da risolvere è più semplice: impacchettare VM con i loro metadati (numero di CPU, memoria, configurazione di rete) in un formato che un altro hypervisor possa capire.

> [!note] REST e SOAP
>
> I protocolli per accedere ai servizi cloud sono già noti: **REST** (architettura stateless basata su HTTP, risorse identificate da URI, metodi standard GET/POST/PUT/DELETE) e **SOAP** (protocollo basato su XML per lo scambio di messaggi strutturati). REST è oggi predominante.

---

## Service Orchestration

L'orchestrazione è il cuore operativo del cloud: il meccanismo che, a partire da una richiesta nel service catalog, coordina automaticamente tutte le operazioni necessarie per creare, gestire e terminare un servizio.

> [!definition] Service Orchestration
>
> Arrangiamento, coordinamento e gestione automatizzati di vari componenti di un'infrastruttura cloud per fornire e gestire servizi cloud. Converte le richieste del service catalog in operazioni concrete sul control layer.

L'orchestratore lavora con sistemi asincroni e code. La **resilienza** dell'orchestratore è critica: perdere lo stato dell'orchestrazione significa trovarsi con migliaia di VM senza sapere a quale servizio appartengono. Per questo motivo, tutte le operazioni vengono persistite in database, non mantenute solo in memoria.

![Schema dell'integrazione dell'orchestratore con i sistemi aziendali](../../../General/Images%20and%20Documents/dcdo_cloud_orchestrator_integration.png)
*Fig. — L'orchestratore è il punto centrale di integrazione: riceve richieste dal Cloud Portal e coordina Unified Manager, Billing System, Directory Service, CMS e Service Management Tools.*

![Schema API dell'orchestratore verso i sistemi esterni](../../../General/Images%20and%20Documents/dcdo_cloud_orchestrator_api.png)
*Fig. — L'orchestratore esegue un workflow composto da chiamate API verso sistemi diversi (approvazione, billing, unified manager) in sequenza o in parallelo.*

### Use Case: Provisioning di un database DB2

Il workflow illustrato dal professore passo per passo:

1. Risorse disponibili nel pool?
   - **No** → aggiorna il portal (order in attesa) → provisioning di più risorse → se ora disponibili, riprendi; altrimenti → order failed.
   - **Sì** → continua.
2. Aggiorna cloud portal: "Order in Progress".
3. Crea la VM.
4. Installa il Guest OS.
5. Connetti la VM alla VLAN corretta.
6. Assegna l'indirizzo IP.
7. Installa DB2.
8. Configura il database.
9. Aggiorna il Configuration Management System (CMS).
10. Genera il bill per il nuovo servizio.
11. Aggiorna il cloud portal: "Service Ready".

![Workflow di orchestrazione per il provisioning di un database DB2](../../../General/Images%20and%20Documents/dcdo_cloud_orchestration_db2_workflow.png)
*Fig. — Il workflow completo di provisioning di un database DB2: dal controllo delle risorse alla notifica del servizio pronto.*

### Use Case: Rimozione di un Tenant

Quando un'organizzazione decide di non usare più il cloud, tutto va ripulito:

1. Ottieni i dettagli dell'organizzazione consumer (lista utenti e servizi).
2. La lista dei servizi è vuota?
   - **No** → elimina le istanze del servizio e rilascia le risorse → rimuovi dal CMS → ricontrolla.
   - **Sì** → continua.
3. La lista degli utenti è vuota?
   - **No** → elimina gli utenti dal CMS → ricontrolla.
   - **Sì** → elimina l'organizzazione consumer dal CMS. Fine.

![Workflow di orchestrazione per la rimozione di un tenant](../../../General/Images%20and%20Documents/dcdo_cloud_orchestration_tenant_removal.png)
*Fig. — Il workflow di rimozione di un tenant: deprovisioning completo di servizi, utenti e organizzazione dal CMS.*

---

## Cloud Service Lifecycle

Un servizio non inizia quando viene deployato per la prima volta: il suo ciclo di vita inizia molto prima.

![Diagramma Mermaid](images/mermaid-lezione-18-control-layer-orchestrazione-e-sla-01.png)
*Fig. — Le quattro fasi del Cloud Service Lifecycle.*

### Phase 1: Service Planning

La fase di planning è **strategica**: si decide se vale la pena creare un servizio. Il professore fa l'esempio dell'università: a un certo punto si è valutata la domanda di web server per i professori (siti di ricerca, didattica, etc.) e si è deciso di supportare solo WordPress, semplificando il portfolio ma soddisfacendo la maggior parte della domanda.

Le domande chiave del planning:
- Quali servizi verranno creati o aggiornati? Qual è il service model appropriato (IaaS, PaaS, SaaS)?
- Quali risorse hardware e software sono necessarie?
- Chi sono i target consumer? Qual è la domanda prevista?
- Qual è il modello di deployment (private, public, hybrid)?
- Quali requisiti di compliance normativa esistono?

### Billing Policy

Il billing non riguarda solo fare profitto. Il professore insiste su questo punto: il cloud **nasconde i costi**. Quando si accede a un servizio cloud dallo smartphone, non si pensa all'energia consumata dai server, dagli switch, dai dischi. Se si archivia un documento inutile nel cloud, si sta sprecando energia e denaro.

> [!example] Esempio: Google Drive e i 100 TB
>
> Un collega del professore aveva accumulato 100 TB su Google Drive perché un backup era partito con le impostazioni sbagliate e nessuno l'aveva notato. Il problema era che quando il cloud era "infinito" e "gratuito", le persone non si rendevano conto dei costi. Google ha poi reso lo storage limitato per lo stesso motivo: indurre le persone a percepire il valore di ciò che consumano.

Il billing è anche uno **strumento di policy**: si può aumentare il prezzo di un servizio per scoraggiarne l'uso (es. un servizio energivoro o meno verde) e abbassare quello di un alternativa preferita. L'università di Pisa sta valutando di assegnare un "budget IT virtuale" a ricercatori e staff, con la possibilità di scalare usando fondi di ricerca se si supera la soglia — proprio per creare consapevolezza.

Tipi di billing nel private cloud:
- **Chargeback**: il costo viene effettivamente addebitato all'unità organizzativa.
- **Showback**: si mostra il costo senza addebitarlo, solo per trasparenza e consapevolezza.

### Phase 2: Service Creation

Si definisce il **service template** (struttura del servizio, attributi default, operazioni di gestione), si crea il **workflow di orchestrazione** corrispondente e si definisce la **service offering** nel catalogo. La service offering è la combinazione di:

- Template + struttura.
- Constraints (chi può accedere).
- Policy (QoS, firewall, bandwidth quota).
- Rules (limiti di scaling, periodo di subscription).
- Price.
- **SLA** (Service Level Agreement).

### Phase 3: Service Operation

Gestione operativa continua: monitoring, reporting, provisioning di nuove istanze, troubleshooting. L'obiettivo è automatizzare tutto il possibile.

### Phase 4: Service Termination

Quando un servizio viene terminato (per scelta del provider, del consumer, o per fine contratto), tutte le risorse vengono rilasciate e restituite al pool. La terminazione non deve impattare altri servizi né i dati dei consumer.

---

## Service Level Agreement (SLA)

Il professore dedica la parte finale della lezione all'SLA, considerandolo uno dei documenti più importanti — e più trascurati dai tecnici — nel cloud.

> [!definition] Service Level Agreement (SLA)
>
> Contratto che definisce la **qualità di servizio** che il provider garantisce al consumer. Non si acquista hardware specifico: si acquista un livello di qualità indipendentemente da come il provider lo realizzi.

Il cloud è "somewhere": non si sa su quale disco, in quale datacenter, in quale paese siano i propri dati. L'SLA è l'unico strumento contrattuale che garantisce che il servizio ricevuto corrisponda a quello pagato.

### Domande chiave dell'SLA

> [!question] Domande chiave dell'SLA
>
> 1. Quali sono i livelli minimi accettabili di performance e disponibilità?
> 2. C'è un limite alla quantità di risorse consumabili?
> 3. Come viene definita un'interruzione di servizio? Come vengono compensati i consumer?
> 4. Qual è il livello di servizio durante i periodi di manutenzione?
> 5. I consumer devono pagare licenze aggiuntive oltre ai costi del servizio?
> 6. Dove verrà archiviata la copia primaria dei dati? Come sarà protetta?
> 7. Vengono offerti compliance e data security come servizi supplementari?
> 8. I consumer verranno notificati se un'agenzia governativa richiede i loro dati?
> 9. Quali garanzie di customer service e tempi di risposta sono previste?

**Sul punto 1**: il costo aumenta in modo non lineare con il livello di disponibilità. Garantire il 95% di uptime costa relativamente poco; garantire il 99.99% richiede ridondanze massicce che si riflettono sul prezzo.

**Sul punto 3**: la definizione di "service outage" è il punto più critico e insidioso dell'SLA. È qui che i provider hanno margine di manovra legale.

**Sul punto 6**: per le pubbliche amministrazioni europee, i dati devono risiedere in datacenter europei (GDPR). L'SLA deve specificare esplicitamente la geolocalizzazione dei dati.

**Sul punto 8**: dopo gli attentati dell'11 settembre 2001, il governo USA si è riservato il diritto di accedere a email e comunicazioni di sospetti terroristici senza notificare gli interessati. Un SLA con un provider americano potrebbe non garantire notifica in caso di richieste di accesso governativo.

### La Definizione di Downtime: il Punto Critico

Il professore sottolinea che la prima cosa da leggere in un SLA non è la tabella delle compensazioni, ma la **sezione delle definizioni** — in particolare la definizione di downtime.

> [!warning] Trucchi nella definizione di downtime
>
> - **Misura in user-minutes**: il downtime non si misura in minuti di clock, ma in (minuti × utenti impattati). Se il problema riguarda solo un account su 50.000, l'impatto in user-minutes è quasi zero — quindi non viene contato come downtime.
> - **Slot minimi**: Amazon nel suo primo SLA dichiarava che un'interruzione veniva contata solo se la VM non era accessibile per almeno 5 minuti. Interruzioni da 4 minuti non esistevano. Molte interruzioni brevi potevano accumularsi senza essere conteggiate.
> - **Colpa di terze parti**: se il problema è nella rete del provider internet del consumer, o nel laptop del consumer, non è colpa del cloud provider.
> - **Scheduled downtime**: la manutenzione pianificata e notificata con almeno 5 giorni di anticipo non conta come downtime.

### Caso Pratico: Microsoft 365 SLA

Il professore apre live il documento SLA di Microsoft 365 e analizza le sezioni chiave.

**Definizione di Uptime Percentage**:

$$
\text{Uptime \%} = \frac{\text{User Minutes} - \text{Downtime}}{\text{User Minutes}} \times 100
$$

Dove:
- **User Minutes** = (minuti totali nel periodo − scheduled downtime) × numero di utenti.
- **Downtime** = Σ (durata incidente in minuti × utenti impattati dall'incidente).

**Scheduled Downtime**: "We will publish notice at least five days prior to the downtime." Se la notifica arriva tardi, quella manutenzione non è più "scheduled downtime" — è vera interruzione.

**Service Credits** (compensazioni):

| Uptime % | Credito |
|---|---|
| < 99.9% | 25% |
| < 99% | 10% |
| < 95% | 50% |
| Sotto ogni soglia garantita | 100% |

> [!note] I crediti sono crediti, non rimborsi
>
> Microsoft (e la quasi totalità dei provider) restituisce il valore sotto forma di **crediti di servizio**, non di denaro. Il consumer deve fare un claim, Microsoft deve approvarlo, e solo allora riceve crediti da spendere su servizi Microsoft.

> [!example] Impatto pratico della misura in user-minutes
>
> Se un'interruzione dura 1 ora e impatta solo il tuo account su 50.000 utenti dell'Università di Pisa, il downtime in user-minutes è 60 × 1 = 60 user-minutes. I total user-minutes del mese sono ≈ 50.000 × 43.200 = 2.160.000.000. L'impatto percentuale è trascurabile — praticamente zero ai fini del calcolo dell'SLA.

### Il Messaggio Finale

Il professore chiude con una riflessione: i tecnici tendono a guardare solo se il servizio è su o giù, senza preoccuparsi delle implicazioni legali. Ma stiamo entrando in un mondo in cui i sistemi digitali sono il corrispettivo del mondo reale: se i sistemi informatici universitari sono down il giorno della laurea per colpa del CIO, i danni sono reali e le responsabilità legali pure.

> [!abstract] Sintesi
>
> Il cloud non è solo tecnologia: è un sistema sociotecnico con implicazioni legali, economiche e organizzative. Il Control Layer gestisce l'infrastruttura in modo automatizzato e scalabile. Il Service e Orchestration Layer espongono questa infrastruttura come servizi consumabili. L'SLA è il contratto che definisce le garanzie — e la sua comprensione richiede attenzione legale, non solo tecnica.
