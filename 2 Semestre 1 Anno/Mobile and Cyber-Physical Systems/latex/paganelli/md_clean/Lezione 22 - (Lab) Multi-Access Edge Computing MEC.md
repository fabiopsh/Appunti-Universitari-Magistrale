---
tags:
  - università/mobile-cyber-physical-systems
  - edge-computing
  - MEC
  - reti-mobili
  - 5G
data: 2026-04-15
lezione: "22 – Multi-Access Edge Computing (MEC)"
professore: "Paganelli"
---

# Multi-Access Edge Computing (MEC)

## Dal Cloud all'Edge

Il paradigma del **cloud computing** si basa sull'idea che le risorse computazionali possano essere fisicamente delocalizzate e connesse remotamente all'utente finale. L'**edge computing** estende questo paradigma portando le risorse elaborative ai margini della rete, fisicamente più vicine all'utente. Con l'edge computing, il traffico utente viene terminato in prossimità dell'utente stesso, creando un ambiente caratterizzato da latenza ridotta e throughput più elevato.

### Perché la latenza conta: la formula di Mathis

Per capire perché la vicinanza fisica all'utente sia importante, occorre capire come la latenza influenzi le prestazioni TCP. La **formula di Mathis** (1997) stabilisce che, per un tasso di perdita inferiore all'1%, il throughput massimo raggiungibile da una connessione TCP è limitato da:

![Formula di Mathis per il throughput TCP](images/lezione-22-lab-multi-access-edge-computing-mec-img-01.jpg)
*Fig. — La formula di Mathis: il throughput TCP è inversamente proporzionale all'RTT e alla radice quadrata della probabilità di perdita.*

dove $MSS$ è la *Maximum Segment Size*, $RTT$ è il *Round-Trip Time* e $P_{loss}$ è la probabilità di perdita dei pacchetti. La formula mostra come il throughput TCP sia limitato da due fattori strettamente legati alla rete: non basta ridurre il ritardo, ma serve anche migliorare il tasso di errore del canale. Questo motiva l'adozione di meccanismi di **QoS** implementati come elaborazione del traffico all'edge, finalizzati a ridurre la perdita di pacchetti.

> [!tip] Intuizione chiave
>
> Portare il server vicino all'utente riduce l'RTT; terminare il traffico radio all'edge riduce anche $P_{loss}$. Entrambi i fattori si combinano per migliorare il throughput TCP in modo significativo.

### La latenza nella pratica: misurazioni reali

Un aspetto spesso controintuitivo è che la latenza end-to-end non è necessariamente proporzionale alla distanza geografica. Misurazioni effettuate in abitazioni distanti meno di 1 miglio quadrato mostrano differenze enormi di latenza, specialmente quando sono coinvolti ISP diversi.

I grafici CDF (Cumulative Distribution Function) illustrano il confronto tra *nearby cloudlet* (bordo della rete, scenario MEC) e *distant cloudlet* (cloud tradizionale) per tre diverse applicazioni:

![Confronto CDF di latenza: cloudlet vicino vs. lontano per tre applicazioni](images/lezione-22-lab-multi-access-edge-computing-mec-img-02.jpg)
*Fig. — CDF del tempo di risposta per Fluid Graphics, Face Recognition e Augmented Reality: il cloudlet vicino (linea rossa tratteggiata) mostra latenze significativamente inferiori.*

> [!note] Evidenza empirica
>
> Il risultato chiave è che la latenza end-to-end dipende dall'infrastruttura di rete (numero di hop, ISP attraversati) molto più che dalla distanza fisica. Questo rende l'edge computing essenziale per applicazioni sensibili alla latenza.

---

## MEC: definizione e standard

**ETSI MEC** (*Multi-Access Edge Computing*) è il principale standard internazionale nell'area dell'edge computing. La definizione ufficiale ETSI recita:

> [!definition] Multi-Access Edge Computing (MEC)
>
> MEC offre a sviluppatori di applicazioni e provider di contenuti capacità di cloud computing e un ambiente di servizi IT al margine della rete.

Il termine **"multi-access"** indica che lo standard è agnostico rispetto alla tecnologia di accesso: è applicabile in linea di principio a reti 4G/5G, Wi-Fi o accesso fisso. Il "core business" dello standard ETSI MEC è la pubblicazione di **API standardizzate** che le applicazioni virtualizzate all'edge possono utilizzare per accedere a informazioni di rete.

### Standard di riferimento

Esistono due principali corpi di standardizzazione nel dominio dell'edge computing:

| Standard | Focus | Note |
|----------|-------|-------|
| **ETSI MEC** | Edge computing da prospettiva IT, access-agnostic | Definisce le API e le specifiche per piattaforme MEC |
| **3GPP** | Tecnologie radio e core network | Integra edge computing dal Release 15 (5G) in poi |

---

## Il concetto di "edge": dove si trova?

Il concetto di *edge* non è definito in modo rigido dallo standard ETSI, proprio per poter includere molte opzioni di deployment basate su requisiti diversi (costi, traffico, presenza di utenti, tariffe). L'edge può essere:

- **Base Station** (stazione radio base)
- **WiFi Access Point**
- **Data center** o micro-data center a uffici centrali, siti di aggregazione
- **Locali del cliente** (*customer premises*)

![Schema delle posizioni possibili dell'edge nella rete mobile](images/lezione-22-lab-multi-access-edge-computing-mec-img-03.jpg)
*Fig. — Confronto tra il percorso dati UE→Cloud (verde, attraverso core network, internet e data center) e UE→MEC Service (arancione, terminato al Mobile Edge Cloud). Fonte: GIGABYTE, 2021.*

---

## Benefici di MEC

I due abilitatori chiave forniti da MEC sono:

1. **Prossimità agli utenti finali**: riduzione della latenza end-to-end a livello del piano utente (UP – *User Plane*).
2. **Accesso alle informazioni radio locali** (piano di controllo, CP – *Control Plane*): permette di implementare meccanismi per migliorare il tasso di errore del canale.

A questi si aggiungono benefici supplementari:

- possibilità di eseguire elaborazioni locali sfruttando grandi quantità di dati locali (sensori, dispositivi);
- supporto al **task offloading** da dispositivi finali con capacità di elaborazione limitata;
- facilitazione delle garanzie di **sicurezza e privacy**, ad esempio anonimizzando informazioni personali all'edge e trasmettendo solo dati aggregati al cloud centrale.

---

## Scenari di servizio MEC

### Analisi di flussi video

Un caso d'uso emblematico è il sistema di monitoraggio video con algoritmi di riconoscimento immagini, ad esempio per il riconoscimento di targhe o il controllo degli accessi in aree urbane.

![Scenario MEC per l'analisi di flussi video](images/lezione-22-lab-multi-access-edge-computing-mec-img-04.jpg)
*Fig. — Il MEC Server, co-locato con la base LTE, esegue video management e analytics localmente. Verso la core network vengono trasmessi solo eventi, metadati e clip rilevanti (bassa banda), anziché stream video ad alta banda.*

Eseguire il video analytics sul **MEC host** consente di:
- evitare la trasmissione di stream video ad alta banda attraverso la core network verso servizi cloud remoti;
- inviare alla rete solo i dati estratti dall'elaborazione (risultati, metadati, clip rilevanti);
- ottenere prestazioni migliori rispetto sia a processare il video sulle telecamere stesse sia a processarlo su un server remoto.

### IoT Gateway

MEC può fungere da **gateway IoT** intelligente, aggregando il traffico proveniente da dispositivi eterogenei (veicoli, sensori, attuatori industriali, dispositivi consumer) e applicando analytics verticali prima di trasmettere dati verso la core network e Internet.

![Scenario MEC come IoT gateway](images/lezione-22-lab-multi-access-edge-computing-mec-img-05.jpg)
*Fig. — Un'applicazione IoT GW App gira sul MEC Server, raccogliendo traffico da dispositivi IoT eterogenei via radio. Verso la core network vengono propagate solo analisi aggregate e eventi rilevanti.*

---

## Architettura MEC

### Il sistema MEC

Un **sistema MEC** include i MEC host e la gestione MEC necessaria per eseguire applicazioni MEC all'interno di una rete operatore.

### Il MEC Framework

![Architettura del MEC Framework con livelli di gestione](images/lezione-22-lab-multi-access-edge-computing-mec-img-06.jpg)
*Fig. — Il MEC Framework: i MEC host ospitano la virtualization infrastructure (NFV) con le MEC app e la MEC platform. La gestione è strutturata su due livelli: system-level e host-level.*

I componenti principali dell'architettura sono:

> [!definition] MEC Host
>
> Include una **MEC platform** e una **virtualization infrastructure** che fornisce risorse di calcolo, storage e rete per le MEC application. È il server fisico che ospita la piattaforma e le applicazioni.

> [!definition] MEC Platform
>
> Raccolta delle funzionalità essenziali per eseguire le MEC application su una particolare infrastruttura di virtualizzazione, abilitandole a consumare e offrire **MEC services**. La piattaforma può essa stessa offrire servizi.

> [!definition] MEC Application
>
> Applicazione che gira sopra la virtualization infrastructure fornita dal MEC host. Può interagire con la MEC platform per consumare e fornire MEC services.

> [!definition] MEC Management
>
> Divisa in *system-level* e *host-level*, gestisce l'orchestrazione dell'intero sistema MEC.

L'architettura è volutamente **astratta dalla tecnologia di accesso specifica**: le reti sottostanti possono essere 3GPP (4G/5G), Wi-Fi, rete fissa o qualsiasi combinazione. I dispositivi terminali non sono necessariamente UE cellulari, ma qualsiasi terminale connesso all'infrastruttura d'accesso.

---

## Categorie di casi d'uso

I casi d'uso MEC si raggruppano in tre categorie principali:

| Categoria | Esempi |
|-----------|--------|
| **Consumer-oriented services** | Gaming, remote desktop, assistenza cognitiva, servizi in tempo reale per stadi/retail, offloading computazionale |
| **Operator and third-party services** | Tracciamento posizione dispositivi, big data, video analytics, veicoli connessi, sicurezza |
| **Network performance & QoE improvements** | Content/DNS caching, ottimizzazione prestazioni, ottimizzazione e accelerazione video |

---

## MEC Service APIs

MEC standardizza un insieme di **API di servizio** che consentono alle applicazioni virtualizzate all'edge di accedere a informazioni di rete e utente dal nodo locale. Le API principali sono:

| API | Funzionalità |
|-----|-------------|
| **Radio Network Info API (RNIS)** | Condizioni radio attuali, Cell ID, intensità segnale, bearer UE |
| **Location API** | Posizione geografica/logica degli UE, lista UE in un'area, movimenti in/out |
| **UE Identity API** | Identificazione dei terminali |
| **Bandwidth Management API** | Gestione della banda |
| **App Lifecycle Management API** | Ciclo di vita delle applicazioni |
| **WLAN Info API** | Informazioni sulle reti Wi-Fi |
| **V2X Info Service API** | Comunicazioni vehicle-to-everything |
| **Service Discovery API** | Scoperta dei servizi disponibili |
| **Mobility API** | Gestione della continuità di servizio durante la mobilità |
| **MultiAccess Traffic Steering API** | Steering, splitting e duplicazione del traffico su accessi multipli |

### Radio Network Information API (RNIS)

La RNIS fornisce informazioni aggiornate sulle condizioni radio: Cell ID, intensità del segnale, misurazioni relative al piano utente, contesto degli UE connessi ai nodi radio associati al MEC host. È utile sia per le MEC app che vogliono ottimizzare i propri servizi (ad esempio guidare il throughput video adattativamente) sia per la MEC platform per ottimizzare le procedure di mobilità.

### Location API

La Location API espone informazioni di localizzazione con due tipi di rappresentazione:
- **Geolocalizzazione**: coordinate geografiche GPS.
- **Localizzazione logica**: Cell ID, identificativi di settore radio.

Le informazioni includono: posizione di UE specifici, lista degli UE in un'area geografica, notifiche di ingresso/uscita da un'area, posizione dei nodi radio associati all'host.

---

## MultiAccess Traffic Steering (MTS) API

Nessuna singola tecnologia di accesso wireless è in grado di soddisfare simultaneamente tutti i requisiti di comunicazione umana e machine-type: massima velocità di trasmissione da un lato, massima affidabilità dall'altro. La **MTS API** nasce per sfruttare la presenza di connessioni multiple combinandole intelligentemente.

### Il trade-off fondamentale

L'idea di base è semplice: se si dispone di $N$ link wireless, ciascuno con data rate $R$ Mbps e affidabilità $p$, combinando i link si può ottenere:

- **Split traffic** (traffico suddiviso): data rate aggregato $N 	imes R$ Mbps, stessa affidabilità $p$ — si guadagna in throughput ma non in affidabilità.
- **Duplicate traffic** (traffico duplicato): stesso data rate $R$, affidabilità $p^N$ — si guadagna in affidabilità ma non in throughput.

> [!warning] Trade-off esclusivo
>
> Il miglioramento del data rate e il miglioramento dell'affidabilità non si ottengono contemporaneamente. Le due strategie (split e duplicate) sono mutuamente esclusive in termini di beneficio primario.

La tabella seguente mostra un esempio numerico con $N$ link da 100 Mbps e affidabilità $10^{-3}$:

![Tabella MTS: data rate e affidabilità al variare del numero di link N](images/lezione-22-lab-multi-access-edge-computing-mec-img-07.jpg)
*Fig. — Con N=4 link: data rate aggregato 400 Mbps (split) oppure affidabilità $10^{-12}$ (duplicate). Le due colonne "Split traffic" e "Duplicate traffic" evidenziano il trade-off.*

### Operazioni MTS supportate

| Operazione | Logica | Caso d'uso tipico |
|------------|--------|-------------------|
| **Low Cost** | Usa la rete non misurata (Wi-Fi) quando disponibile | Email, backup in background |
| **Low Latency** | Usa la connessione con latenza minore | Controllo remoto, gaming |
| **High Throughput** | Usa la rete con throughput maggiore, o più reti simultaneamente | Video streaming HD |
| **Redundancy** | Duplica i pacchetti su più connessioni | Controllo robotico (URLLC) |

> [!example] Esempi pratici di MTS
>
> - **Email/Dropbox**: applicazione data-centric in background, non sensibile a latenza né throughput → preferisce Wi-Fi (Low Cost).
> - **Controllo robot** (URLLC): richiede altissima affidabilità e bassa latenza → Redundancy, pacchetti duplicati su più connessioni simultaneamente.
> - **Video HD real-time**: richiede alto throughput → High Throughput con bandwidth aggregation (traffic split su più link).

### Esercizio: applicabilità MTS

> [!question] Possibili domande d'esame
>
> - Dato un insieme di link wireless con parametri di QoS, determinare quale operazione MTS è necessaria per soddisfare i requisiti di ciascuna applicazione.
> - Spiegare il trade-off tra split traffic e duplicate traffic con esempio numerico.
> - Perché nessuna singola tecnologia di accesso può soddisfare tutti i requisiti? Come risponde MEC?
> - Qual è la differenza tra MEC host, MEC platform e MEC application?
> - Quali informazioni espone la RNIS API e per quali ottimizzazioni viene usata?

---

## Implementazione e strumenti

MEC è supportato da tutti i principali cloud provider con soluzioni proprietarie: **Azure private multi-access edge compute** (con partner Nokia ed Ericsson), **AWS Wavelength** (che porta l'infrastruttura AWS nei data center dei partner telco per soddisfare requisiti di bassa latenza e residenza dei dati).

Per la sperimentazione, ETSI fornisce **MEC Sandbox** (`try-mec.etsi.org`), un ambiente interattivo per imparare e sperimentare con le MEC Service API senza necessità di infrastruttura fisica.
