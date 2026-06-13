# Interoperabilità e Standard nell'IoT

Il concetto di **interoperabilità** rappresenta una delle sfide cruciali nello sviluppo dell'Internet of Things. Implementare una soluzione IoT "dal basso", ovvero dal livello fisico fino all'applicazione, non costituisce di per sé un problema tecnico insormontabile; tuttavia, questo approccio porta spesso alla creazione di quelli che vengono definiti *vertical silos*.

> [!definition] Vertical Silos
>
> In questo modello, una soluzione funziona esclusivamente all'interno del proprio ecosistema: i dispositivi proprietari comunicano solo con l'infrastruttura dello stesso fornitore, rendendo incompatibili i prodotti di terze parti.

Questa strategia di design è spesso intenzionale e risponde a un modello di business basato sul *vendor lock-in*.

> [!definition] Vendor Lock-in
>
> La pratica di "ingabbiare" il cliente con l'obiettivo di prevenire l'utilizzo di componenti di altri produttori e imporre costi elevati per l'eventuale migrazione verso soluzioni alternative. Tale migrazione comporta spesso la completa riprogettazione e il dispiegamento di un nuovo sistema, con il rischio di entrare semplicemente in un altro silos.

Storicamente, il problema dell'interoperabilità risiedeva principalmente a livello hardware (come nel caso delle prese elettriche), ma nell'IoT moderno la questione si è spostata prevalentemente a livello software. La soluzione universalmente riconosciuta per mitigare queste barriere è l'introduzione e l'adozione di **standard** condivisi.

## Tecnologie Wireless e Standard di Riferimento

Il panorama delle tecnologie wireless è vasto e differenziato in base al rapporto tra raggio di copertura (range) e velocità di trasmissione dati (data rate).

**IEEE 802.11 (Wi-Fi)** è una famiglia di standard originariamente definita per operare a 2.4 GHz con velocità di 1–2 Mbps, che si è evoluta nel tempo attraverso varie iterazioni (802.11a, b, g, n, ac, ecc.). Le evoluzioni successive hanno introdotto nuove bande di frequenza (come i 5 GHz), aumentato drasticamente il bit rate (fino a oltre 400 Mbps), esteso il raggio di trasmissione e migliorato la gestione della **Quality of Service (QoS)** e il roaming tra access point.

**IEEE 802.15.4** definisce i livelli fisico e MAC per reti a basso consumo. Su queste basi costruisce **ZigBee**, un consorzio industriale che aggiunge i livelli di rete superiori e le interfacce applicative. ZigBee è progettato specificamente per reti di sensori a bassa potenza, caratterizzate da un throughput limitato (fino a 115 Kbps) e un duty cycle molto basso (circa l'1%). Supporta configurazioni multi-hop, essenziali per coprire aree estese attraverso una rete capillare di dispositivi.

**Bluetooth** offre rispetto a ZigBee un data rate superiore ed è orientato alla comunicazione personale e multimediale (audio e video a bassa qualità). Si basa su una topologia master-slave per piccoli gruppi di dispositivi, detta *piconet*. Con l'avvento del Bluetooth 2 il throughput è stato incrementato fino a 10 Mbps.

Le **reti cellulari** hanno attraversato diverse generazioni: dall'analogico (1G) al digitale con supporto SMS (2G-GSM), fino all'introduzione della commutazione di pacchetto e dell'accesso a Internet (2.5G GPRS, 3G EDGE). Il **4G LTE** ha segnato un punto di svolta per la larghezza di banda e la riduzione della latenza sotto i 20 ms.

## Il Paradigma 5G

> [!tip] Il 5G come cambio di paradigma
>
> Il 5G non rappresenta solo un incremento di velocità, ma un cambiamento profondo che abilita categorie di scenari d'uso radicalmente diverse, ciascuna con requisiti tecnici incompatibili tra loro. Questa molteplicità di casi d'uso è spesso rappresentata in un diagramma triangolare.

Le tre macro-categorie del 5G esprimono esigenze distinte. L'**Enhanced Mobile Broadband (eMBB)** copre applicazioni che richiedono altissima velocità dati, come video 3D o streaming in qualità 8K: il requisito dominante è la larghezza di banda. Il **Massive Machine Type Communication (mMTC)** affronta invece lo scenario dell'IoT su scala urbana — smart cities, smart homes — dove l'obiettivo non è la velocità ma la capacità di connettere simultaneamente miliardi di dispositivi a basso consumo energetico. L'**Ultra-Reliable Low Latency Communications (URLLC)**, infine, si rivolge ad applicazioni mission-critical come la guida autonoma o la chirurgia remota: qui affidabilità e latenza diventano parametri vitali, mentre la velocità di picco è secondaria.

Confrontando il 5G con il 4G tramite grafici radar (*spider chart*), si nota un miglioramento sostanziale in tutte le metriche chiave: efficienza spettrale, densità di connessione, efficienza energetica della rete e latenza.

## La Necessità e la Complessità degli Standard

Gli standard nascono dalla necessità di ridurre i costi di sviluppo tecnologico attraverso accordi tra diversi produttori, in un regime di **coopetition** (cooperazione tra competitor). Solitamente, la standardizzazione avviene quando una tecnologia diventa matura e i grandi margini di profitto non risiedono più nello sviluppo della tecnologia di base, ma altrove. Senza queste condizioni economiche, gli standard tendono a fallire.

Tuttavia, la proliferazione degli standard — come nel caso delle comunicazioni wireless — ha spostato il problema dell'interoperabilità ai livelli middleware e applicativo. Oggi esistono numerosi protocolli di livello applicativo (MQTT, CoAP, LWM2M, ecc.), creando una situazione in cui l'incompatibilità non è solo tra silos verticali, ma anche tra standard differenti.

Per gestire questa eterogeneità si ricorre agli **Application-level gateway**. Questi dispositivi non si limitano a tradurre protocolli di basso livello: mappano comportamenti applicativi differenti l'uno nell'altro, operando come interpreti semantici tra ecosistemi incompatibili.

## Configurazioni di Integrazione

Le architetture IoT possono assumere configurazioni molto diverse in base all'omogeneità dei dispositivi e dei protocolli coinvolti. La tabella seguente riassume i quattro tipi principali:

| Tipo | Fornitore | Protocollo | Necessità di gateway |
|------|-----------|------------|----------------------|
| A | Unico | Unico | No |
| B | Multiplo | Unico (condiviso) | No o minimale |
| C | Multiplo | Diversi | Sì — Integration Gateway per la traduzione |
| C/II | Multiplo (consumer) | Diversi | Sì — ecosistemi come Google Home o Alexa |
| D | Multiplo | Eterogenei e distribuiti | Sì — gateway multipli con mappature complesse |

Al crescere della complessità, dal Tipo A al Tipo D, il gateway di integrazione deve gestire un numero esponenziale di mappature tra protocolli allo stesso livello. La sfida non è solo tecnica ma organizzativa: ogni nuovo fornitore o protocollo aggiunto alla rete moltiplica le combinazioni da gestire.

---

## Sicurezza nell'IoT

La sicurezza nei sistemi cyber-fisici e nell'IoT ha raggiunto un punto di crisi. A differenza dei sistemi IT tradizionali, i dispositivi IoT sono spesso sistemi embedded economici, prodotti con forti incentivi a ridurre costi e tempi di immissione sul mercato (*Time-to-Market*), a discapito della sicurezza.

Questi dispositivi sono frequentemente affetti da vulnerabilità per le quali non esiste un meccanismo efficace di patching, lasciando centinaia di milioni di dispositivi connessi esposti ad attacchi. Le conseguenze variano dall'inserimento di dati falsi nella rete (attacchi ai sensori) alla compromissione delle operazioni fisiche (attacchi agli attuatori). Esempi reali includono università attaccate dalle proprie vending machine connesse o sistemi ransomware che bloccano l'accesso fisico alle stanze d'albergo.

## Requisiti di Sicurezza secondo ITU-T Y.2066

La raccomandazione **Y.2066** dell'ITU-T identifica i requisiti fondamentali per la sicurezza IoT organizzandoli in tre aree concettuali distinte. La prima riguarda la **sicurezza della comunicazione**: si tratta di garantire la riservatezza e l'integrità dei dati durante la trasmissione o il trasferimento tra dispositivi e piattaforme. La seconda area è la **sicurezza della gestione dei dati**, che si occupa di proteggere riservatezza e integrità quando i dati sono archiviati o elaborati, ovvero a riposo piuttosto che in transito. La terza area affronta la **sicurezza della fornitura del servizio**: l'obiettivo è prevenire accessi non autorizzati ai servizi e proteggere le informazioni private degli utenti.

A questi tre pilastri si aggiungono la necessità di integrare diverse politiche di sicurezza, l'implementazione dell'**autenticazione mutua** tra dispositivi o tra dispositivo e utente — più robusta dell'autenticazione a una via — e la capacità di effettuare audit di sicurezza trasparenti e tracciabili.

## Il Ruolo del Gateway nella Sicurezza

In un'architettura IoT, il gateway agisce spesso come punto centrale di applicazione delle policy di sicurezza. Sul fronte dell'**identificazione e autenticazione**, gestisce l'accesso di ogni dispositivo connesso: l'autenticazione mutua è preferibile perché entrambe le parti si verificano reciprocamente, mentre quella a una via lascia uno dei due lati esposto. Il gateway si occupa anche della **protezione della privacy**, tutelando sia i dispositivi periferici che se stesso. Supporta inoltre le attività di **manutenzione e aggiornamento**, inclusi l'autodiagnosi, la riparazione remota e — punto cruciale — l'aggiornamento di firmware e software, spesso assente nei dispositivi IoT economici. Infine, gestisce la **configurazione** dei dispositivi, sia in modalità automatica che manuale, locale o remota, basandosi su policy dinamiche.

> [!warning] Dispositivi vincolati e limiti di sicurezza
>
> I **dispositivi vincolati** (*constrained devices*) pongono ostacoli concreti all'implementazione di questi requisiti. Ad esempio, garantire la sicurezza dei dati archiviati su un dispositivo privo di capacità hardware di crittografia può risultare impraticabile. Con la diffusione del *Massive IoT*, la **privacy** diventa un'area di crescente preoccupazione: l'enorme mole di dati sensibili — medici, di posizione, sulle abitudini — raccolti da governi e aziende amplifica i rischi in modo proporzionale alla scala del deployment.

> [!question] Possibili domande d'esame
>
> - Cosa si intende per vertical silo e vendor lock-in nell'IoT? Qual è la relazione tra i due concetti?
> - Quali sono le tre macro-categorie di scenari d'uso del 5G e quali requisiti tecnici le caratterizzano?
> - Descrivere le configurazioni di integrazione Tipo A, B, C e D: quando è necessario un gateway applicativo?
> - Quali sono i requisiti di sicurezza identificati dalla raccomandazione ITU-T Y.2066?
> - Qual è il ruolo del gateway nella sicurezza IoT e quali limitazioni incontrano i dispositivi vincolati?
