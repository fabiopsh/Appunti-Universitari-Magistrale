L'**Application Layer** del protocollo ZigBee si basa sullo standard IEEE 802.15.4 e gestisce direttamente i servizi applicativi della rete. Questo livello si compone di tre elementi fondamentali: l'**Application Framework**, lo **ZigBee Device Object (ZDO)** e l'**Application Support Sublayer (APS)**. L'Application Framework è l'ambiente in cui risiedono fino a 240 **Application Objects (APO)**, ovvero le applicazioni ZigBee definite dall'utente. Lo ZDO, invece, fornisce i servizi necessari per organizzare gli APO in un'applicazione distribuita. Infine, l'APS fa da tramite offrendo servizi dati, di scoperta e di gestione (binding) sia agli APO che allo ZDO.

![[Pasted image 20260317144430.png|412]]

## L'Application Framework e gli Endpoints

All'interno dell'Application Framework, ogni **Application Object (APO)** è associato a uno specifico **Endpoint**, identificato da un numero compreso tra 1 e 240. ==L'Endpoint 0 è strettamente riservato allo ZDO==. Grazie a questo sistema, un singolo dispositivo ZigBee può eseguire molteplici applicazioni simultaneamente, in quanto gli endpoint fungono da "cavi virtuali" (simili ai socket in Unix) che collegano le applicazioni e consentono la coesistenza di profili e punti di controllo distinti su un unico nodo. Ogni APO è identificato in modo univoco dalla combinazione tra l'indirizzo di rete del dispositivo ospitante e il suo numero di endpoint. Nelle prime versioni di ZigBee, gli APO più semplici venivano interrogati tramite il servizio **Key Value Pair (KVP)**, ora assorbito dalla Cluster Library , mentre le applicazioni più complesse comunicano tramite il servizio messaggi.

> [!important] Focus: Definizione di Cluster e Profilo 
> Un **Cluster** è una collezione di comandi e attributi che definiscono l'interfaccia per una specifica funzionalità del dispositivo (ad esempio, accendere o spegnere una luce). È identificato da un codice a 16 bit, il cui significato dipende dal profilo di appartenenza. Un **Application Profile** è invece la specifica del comportamento di un'intera classe di applicazioni (es. _Home Automation_) che possono operare su vari dispositivi ZigBee. Anche i profili usano ID a 16 bit: quelli pubblici vanno da $0\times0000$ a $0\times7FFF$, mentre quelli dei produttori da $0\times BF00$ a $0\times FFFF$. Ogni messaggio inviato in rete è infatti contrassegnato (tagged) con un Profile ID.

## I Cluster e i Profili

I cluster permettono di interagire con le funzionalità di un APO tramite protocolli operativi che, nei casi più semplici, prevedono lo scambio di un singolo messaggio. I **comandi** innescano azioni fisiche o logiche sul dispositivo, mentre gli **attributi** ne rivelano lo stato corrente. Esistono svariati cluster definiti dalla ZigBee Alliance per ambiti generali.

|**Cluster Name**|**Cluster ID**|
|---|---|
|Basic Cluster|$0\times0000$|
|Power Configuration Cluster|$0\times0001$|
|Temperature Configuration Cluster|$0\times0002$|
|Identify Cluster|$0\times0003$|
|Group Cluster|$0\times0004$|
|Scenes Cluster|$0\times0005$|
|OnOff Cluster|$0\times0006$|
|Level Control Cluster|$0\times0008$|
|Time Cluster|$0\times000A$|
|Location Cluster|$0\times000B$|

Anche gli Application Profiles sono standardizzati in un "domain space" per garantire l'interoperabilità in settori specifici:

|**Profile ID**|**Profile name**|
|---|---|
|0101|Industrial Plant Monitoring|
|0104|Home Automation|
|0105|Commercial Building Automation|
|0107|Telecom Applications|
|0108|Personal Home & Hospital Care|
|0109|Advanced Metering Initiative|

## Device IDs

I **Device IDs** sono codici a 16 bit (con range da $0\times0000$ a $0\times FFFF$) che identificano la tipologia fisica del dispositivo. Il loro scopo primario è rendere i dispositivi riconoscibili agli esseri umani e agli strumenti di diagnosi, ad esempio per mostrare a display l'icona di un interruttore o di un termostato anziché un codice illeggibile.

> [!warning] Attenzione: Scoperta dei Servizi e Device IDs 
> Un Device ID ti dice solo _cos'è_ l'oggetto (es. un forno o una lampadina intelligente), ma non ti indica affatto come poter comunicare con esso. Per capirlo devi necessariamente scoprire quali ID dei Cluster implementa. Proprio per questo motivo, ==la rete ZigBee non usa i Device ID per la Service Discovery==: la ricerca avviene interrogando direttamente i Profile ID e Cluster ID.

## L'Application Support Sublayer (APS)

L'APS funge da livello di trasporto leggero (Light Transport Layer) che eroga tre tipologie di servizi: **Data Service**, **Binding Service** (gestione delle connessioni logiche tra endpoint allo ZDO) e **Group Management**. Il servizio dati facilita lo scambio di messaggi e l'affidabilità si basa su tre primitive fondamentali: **request** (invio), **confirm** (notifica dell'esito della trasmissione di ritorno) e **indication** (ricezione al livello destinazione). L'APS si occupa attivamente di filtrare i pacchetti per scartare quelli destinati a endpoint non registrati o profili non compatibili, e ha il compito di generare gli acknowledgment end-to-end.

![[Pasted image 20260317150017.png]]

Per gestire gruppi di APO e consentire la trasmissione multicast, l'APS usa le proprie tabelle locali. Ogni gruppo ha uno specifico indirizzo a 16 bit: le primitive `ADD-GROUP` e `REMOVE-GROUP` associano dinamicamente la coppia indirizzo di rete / endpoint al gruppo, occupandosi di crearlo da zero nel caso non esista ancora. Tali informazioni vengono salvate e consultate nelle Group Tables dell'APS.

## APS Binding e Indirizzamento Indiretto

Il **Binding** consente di creare connessioni unidirezionali tra un endpoint su un nodo sorgente e uno o molteplici endpoint su altri nodi. È un meccanismo vitale che può essere configurato solo su esplicita richiesta dello ZDO di un coordinatore o di un router.

Il grande vantaggio del binding è permettere l'**indirizzamento indiretto**. Dispositivi estremamente semplici o sensori poveri non necessitano di conoscere la topologia della rete o l'indirizzo esatto di chi dovrà processare i loro dati. Tramite le primitive `BIND.request` e `UNBIND.request`, la Binding Table prende in carico una richiesta in uscita (incrociando l'indirizzo sorgente e l'ID del cluster in esame) e la mappa automaticamente verso le corrette coordinate `<destination endpoint, destination network addr>`.

> [!note] Contesto: Cambiamento Indirizzi e Address Map 
> Poiché i dispositivi ZigBee acquisiscono gli indirizzi in modo decentralizzato, in caso di reset o mancanza di corrente un sensore e un attuatore prima in comunicazione potrebbero risvegliarsi ottenendo nuovi indirizzi di rete a 16 bit. Non serve però l'intervento di un tecnico: l'APS layer usa internamente la **Address Map Table** che associa stabilmente gli indirizzi 16 bit NWK con gli immutabili indirizzi MAC a 64 bit (IEEE MAC address). In caso di riavvio il nodo esegue un annuncio sulla rete e tutti i nodi riaggiornano le tabelle locali in base ai MAC, ripristinando in modo invisibile i binding indiretti.

## Lo ZigBee Device Object (ZDO)

Lo **ZDO** è la speciale applicazione gestionale del nodo ed è perennemente attaccato all'Endpoint 0. Le sue funzionalità e comportamenti dipendono strettamente dallo **ZigBee Device Profile (ZDP)**, che definisce quali cluster un dispositivo standard deve supportare e regola le policy di sicurezza, la gestione dei nodi e le regole di binding. I principali servizi esposti dallo ZDO includono:

- **Device e Service Discovery:** La Device Discovery recupera per l'utente gli indirizzi fisici MAC o di rete interrogando la rete in unicast oppure sfruttando un broadcast gerarchico in cui i router o i coordinatori rispondono raggruppando i dispositivi a loro associati. La Service Discovery serve a reperire informazioni sui servizi, con richieste filtrate per cluster o ID di profilo, anch'esse risolte gerarchicamente dai router padre o in unicast (con i router che rispondono per conto dei nodi End Device addormentati).
    
- **Binding Management:** Processa e attua fisicamente tutte le richieste di modifica alle tabelle di binding dell'APS da entità remote o locali.
    
- **Node e Network Management:** Implementa il comportamento di base stabilito per il ruolo del nodo alla configurazione, garantendo la gestione ordinata di ingressi (join) e uscite (leave) dalla rete dei dispositivi e lo smistamento di informazioni interne sulle routing table.

## La ZigBee Cluster Library (ZCL)

Per evitare che gli sviluppatori riscrivano codice generico ("reinventare la ruota"), la ZigBee Alliance ha istituito la **ZigBee Cluster Library (ZCL)**, un gigantesco e aggiornato repository di funzionalità standardizzate che supporta e facilita enormemente l'interoperabilità tra dispositivi di terze parti e la manutenibilità software. Per esempio, all'interno del dominio domotico (_Home Automation_), i cluster sono strutturati rigorosamente in categorie semantiche : Closures (chiusure, serrature e tende), HVAC (pompe di calore, deumidificatori e termostati), Lighting (luci), Measurement and Sensing (sensori ambientali) o Protocol Interfaces (interfacce di traduzione).

#### L'Architettura Client-Server della ZCL

Ogni cluster introdotto dalla ZCL poggia saldamente su un modello gerarchico Client-Server per l'accesso e la manipolazione di un Dominio Funzionale:

- **Il Server** è colui che ospita fisicamente il dato e ne conserva lo stato (memorizza e governa gli **attributi**).
    
- **Il Client** è il dispositivo di comando che manipola gli attributi e invia istruzioni al Server. Questa logica supporta l'impilamento e permette la compatibilità verso il basso. In base alla propria complessità, per esempio, una "Lampadina dimmerabile a colori" vestirà simultaneamente i panni del Server nel Cluster On/Off, nel Cluster Level Control (luminosità) e nel Color Control, esponendo attributi diversi alla rete.

#### Comandi e Attributi della ZCL

I comandi ZCL consistono tecnicamente in messaggi formattati con un header e un payload. I flussi logici consentono di leggere, manipolare o interrogare le funzionalità, e partono comunemente dal client. Ma la vera forza è il **Dynamic Attribute Reporting** : si tratta di comandi preposti che viaggiano in senso contrario (dal Server al Client associato) contenenti aggiornamenti sul valore registrato dall'attributo. Grazie a regole parametriche precise (si può impostare una frequenza di aggiornamento, una durata, o notificare le anomalie al superamento di un valore di tolleranza), il reporting automatico previene gli sprechi d'energia in trasmissioni superflue.

Includono inoltre interrogazioni standard ai metadati dell'hardware, basate sul **Basic Device Info Cluster**($0\times0000$) e configurazioni sull'alimentazione tramite il **Power Configuration Cluster** ($0\times0001$), il cui attributo base **PowerSource** può valere "Mains (single phase)" ($0\times01$), "Battery" ($0\times03$) o "DC Source" ($0\times04$), fino agli UPS di emergenza ($0\times05$).

## Esempio Applicativo: Indoor Localization

Oltre alle tipiche automazioni, lo standard include funzionalità ingegnose come l'**Indoor Localization** all'interno di ZigBee. Attraverso lo scambio di segnali radio, un sensore valuta la distanza dai nodi adiacenti estrapolandola dalla qualità del segnale ricevuto misurata dell'hardware (RSSI) e attuando tecniche di triangolazione spaziale. La rete per farlo si appoggia a due architetture primarie:

1. **Remote Positioning:** Il nodo mobile è una scatola nera che invia il suo faro radio (ping). La rete di sensori statici riceventi (le _ancore_) misura e incrocia le RSSI per scoprire la posizione.
    
2. **Self Positioning:** La rete di ancore emette messaggi beacon continui; il dispositivo mobile intelligente fa una stima triangolando internamente i ping ricevuti e scoprendo la propria posizione.

Per esporre i dati agli sviluppatori si utilizza lo speciale **RSSI Location Cluster** che permette scambi opzionali di informazioni sulla potenza o sui canali. Contrariamente a quanto intuitivo, in questo modello ==il Client è il nodo fisso (l'ancora) mentre il Server del cluster è proprio il dispositivo Mobile== in quanto eroga lui i parametri. L'attributo essenziale `Location Method` ($0\times0001$) modella la tecnica: Laterazione RSSI classica ($0\times00$), localizzazione per Prossimità al ricevitore più vicino ($0\times01$), Fingerprinting incrociando i dati con un database precompilato ($0\times02$), Localizzazione da bande estranee a ZigBee ($0\times03$), o elaborazione demandata a Gateway **Centralizzato** ($0\times04$) in cui il nodo centrale raccoglierà tutto lo storico per iniettare l'esito calcolato nel cluster del dispositivo target tramite il comando `Set Absolute Location` ($0\times00$).

## Wrap-Up: Costruire una Soluzione ZigBee

Creare una linea di prodotti supportati da ZigBee non parte mai da zero. L'hardware di base, lo stack con le logiche dei livelli ISO-OSI (e il relativo ZDO) e gran parte delle librerie della ZCL sono già sviluppate dai produttori di SoC radio. Il lavoro dell'azienda si riduce all'assemblaggio dei trasduttori fisici ai chip, unito alla configurazione software mirata della classe del dispositivo: si programma il suo ruolo (Coordinatore, Router o End Device dormiente) e si instanziano gli specifici APO all'interno dei relativi endpoint per dare "cervello logico" (business logic) agli attributi preposti dalla ZCL, garantendo così istantanea compatibilità su vasta scala con gli impianti intelligenti esistenti nel mondo.

> [!summary] Glossario
> 
> - **APO (Application Object):** L'effettiva applicazione firmware scritta per un device ZigBee (es. logica di un termostato). Risiede all'interno dell'Application Framework.
>     
> - **Endpoint:** È l'indirizzamento logico che connette l'APO alla rete come un filo virtuale (da 1 a 240). Il nodo 0 è sempre dedicato per design al gestore di rete ZDO. - **Binding Indiretto:** Un geniale meccanismo dell'APS che crea ponti funzionali logici tra sensori e attuatori senza che essi sappiano nulla della rete, appoggiandosi alla tabella Binding Table aggiornata dinamicamente coi MAC address. 
> - **ZCL (ZigBee Cluster Library):** Standardizzazione mondiale che ordina ogni applicativo in un modello Client/Server rigoroso, associando ID (Cluster ID) a un elenco formale di Comandi e Attributi.
>