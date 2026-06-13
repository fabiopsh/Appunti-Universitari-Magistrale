# Protocolli MAC e Reti Wireless: Da CSMA/CD allo Standard IEEE 802.11

Questo capitolo esplora in modo approfondito l'evoluzione dei protocolli di accesso al mezzo (MAC), partendo dalle fondamenta delle reti cablate fino ad arrivare alle complesse dinamiche delle reti wireless. Analizzeremo le sfide fisiche della trasmissione via radio, introducendo i meccanismi architetturali e i protocolli, come il CSMA/CA e la famiglia IEEE 802.11, che rendono possibile la connettività Wi-Fi moderna.

---

## I Protocolli MAC per le Reti Cablate: Un Riepilogo

Per comprendere le reti wireless, è fondamentale fare un passo indietro e analizzare le assunzioni di base che governano i protocolli MAC (Medium Access Control) nelle tradizionali reti cablate. In questi scenari, si assume generalmente che sia disponibile un **singolo canale condiviso** per tutte le comunicazioni e che tutte le stazioni collegate possano trasmettere e ricevere su di esso. Un principio cardine è che se due o più frame vengono inviati simultaneamente, il segnale risultante sul canale risulterà incomprensibile, generando quella che viene definita una **collisione**. Nelle reti cablate, tutte le stazioni sono fisicamente in grado di rilevare queste collisioni. Nel tempo, sono stati sviluppati diversi protocolli per gestire questo accesso, partendo da ALOHA e slotted ALOHA, fino ad arrivare a CSMA e CSMA/CD.

### Il Protocollo CSMA/CD

Il protocollo **CSMA/CD** (Carrier Sense Multiple Access with Collision Detection) si basa su un'idea fondamentale: "ascoltare prima di parlare". Quando una stazione ha un frame pronto per l'invio, si mette in ascolto sul canale per verificare se qualcun altro sta già trasmettendo. Se il canale risulta occupato, la stazione attende pazientemente che diventi libero (idle). Non appena il mezzo è libero, la stazione inizia a trasmettere il suo frame. Se durante questa fase si verifica una collisione, la stazione interrompe (aborts) immediatamente la trasmissione, attende una quantità di tempo casuale e ripete l'intera procedura.

> [!definition] CSMA/CD — Carrier Sense Multiple Access with Collision Detection
>
> Protocollo di accesso al mezzo che combina l'ascolto preventivo del canale (Carrier Sense) con il rilevamento attivo delle collisioni durante la trasmissione (Collision Detection). Quando viene rilevata una collisione, la trasmissione viene interrotta immediatamente, riducendo lo spreco di banda. È il cuore dello standard IEEE 802.3 Ethernet.

Questo meccanismo di rilevamento precoce fa sì che, se due stazioni percepiscono simultaneamente il canale libero e iniziano a trasmettere, entrambe interrompano l'invio non appena rilevano la sovrapposizione dei segnali, risparmiando così tempo prezioso e larghezza di banda. Per la sua efficienza, il CSMA/CD è stato ampiamente adottato nei sottolivelli MAC delle LAN, diventando il cuore dello standard **IEEE 802.3 Ethernet**.

### Limiti Temporali e Dimensione Minima del Frame

Il comportamento del CSMA/CD impone vincoli fisici ben precisi. Definendo con $T$ il tempo di propagazione necessario per raggiungere la stazione più lontana della rete, nel caso peggiore occorrerà un tempo pari al Round Trip Time ($RTT$), ovvero $2T$, affinché la stazione trasmittente possa rilevare con certezza una collisione.

- Ad esempio, se la stazione A inizia a trasmettere al tempo $t=0$, e la stazione B (la più remota) inizia a trasmettere poco prima che il segnale di A la raggiunga (al tempo $t=T-\delta$), B rileverà la collisione quasi subito, al tempo $t=T$.

- Tuttavia, il fronte d'onda della collisione impiegherà un altro tempo $T$ per viaggiare a ritroso verso A, che si accorgerà del problema solo al tempo $t=2T-\delta$.


Di conseguenza, la stazione A deve obbligatoriamente monitorare il canale per l'intero intervallo di tempo $RTT$ con gli "occhi aperti" per intercettare eventuali interferenze. Una volta che l'intero frame è stato inviato, infatti, la stazione mittente non ne conserva una copia nel buffer MAC e non controlla più il mezzo trasmissivo per eventuali collisioni. Per garantire che la trasmissione duri almeno quanto il tempo $RTT$, è necessario imporre un vincolo sulla **dimensione minima del frame**.

Facciamo un esempio pratico: consideriamo una rete CSMA/CD con una larghezza di banda di 10 Mbps e un tempo massimo di propagazione (inclusi i ritardi hardware) di 25.6 $\mu sec$. Nel caso peggiore, la stazione deve trasmettere per un tempo di trasmissione minimo del frame $T_{fr} = 2 \times T_{p} = 51.2~\mu sec$ per poter intercettare con successo una collisione. Traducendo questo tempo in dati, la dimensione minima del frame risulta essere: 10 Mbps x 51.2 $\mu sec$ = **512 bit**, ovvero **64 byte** (la dimensione minima effettiva adottata nell'Ethernet standard).

### Il Binary Exponential Backoff

Quando avviene una collisione, come si stabilisce il tempo di attesa casuale? Il CSMA/CD utilizza l'algoritmo di **Binary Exponential Backoff**. Il tempo successivo a una collisione viene suddiviso in _contention slots_ (slot di contesa), la cui lunghezza è esattamente pari al tempo di propagazione andata e ritorno nel caso peggiore ($2T$).

- Dopo la prima collisione, ogni stazione coinvolta attende 0 oppure 1 slot in modo casuale prima di riprovare.

- Dopo la collisione iesima ($i$), la stazione sceglie un numero casuale $x$ nell'intervallo $[0, 2^i - 1]$ e salta esattamente $x$ slot prima di un nuovo tentativo.

- Per evitare attese infinite in reti congestionate, dopo 10 collisioni consecutive l'intervallo di randomizzazione viene "congelato" a un massimo di 0..1023.

- Se si raggiungono le 16 collisioni, il livello MAC si arrende e riporta il fallimento della trasmissione ai livelli superiori.


---

## Le Reti Wireless: Sfide e Problemi Strutturali

Nelle reti cablate il rilevamento delle collisioni in fase di trasmissione funziona perfettamente, ma nelle reti wireless questo principio fallisce a causa della natura stessa del mezzo radio. Nelle trasmissioni senza fili, la potenza del segnale decade rapidamente, diminuendo in proporzione al quadrato della distanza.

A causa di questa attenuazione, il segnale emesso dall'antenna del trasmettitore (il _self-signal_) risulta infinitamente più forte rispetto a qualsiasi altro segnale debole in arrivo da una stazione distante. Questo "acceca" il trasmettitore, rendendogli impossibile rilevare una collisione mentre sta inviando dati. Inoltre, le condizioni del canale wireless sono spazialmente diverse tra chi trasmette e chi riceve. Una collisione rilevata dal trasmettitore potrebbe non essere una collisione al ricevitore, e viceversa. Nelle reti wireless, l'unica cosa che conta veramente è l'**interferenza al ricevitore**, non al mittente. Questa limitazione genera due problemi classici della comunicazione radio: il _Terminale Nascosto_ e il _Terminale Esposto_.

### Il Problema del Terminale Nascosto (Hidden Terminal)

> [!definition] Terminale Nascosto (Hidden Terminal)
>
> Si verifica quando due o più stazioni, reciprocamente fuori dal raggio radio l'una dell'altra, trasmettono simultaneamente verso un destinatario comune. Poiché nessuna delle due stazioni riesce a rilevare la trasmissione dell'altra, entrambe credono il canale libero e avviano l'invio, causando una collisione al ricevitore che nessuna delle sorgenti è in grado di percepire.

Immaginiamo quattro stazioni allineate: A, B, C e D. A è in raggio radio con B; B è nel raggio di A e C; C è nel raggio di B e D. Supponiamo che A stia attualmente trasmettendo dei dati a B. C, desiderando trasmettere, si mette in ascolto sul mezzo. Poiché C si trova fisicamente al di fuori del raggio di copertura radio di A, non percepirà alcuna trasmissione in corso. Credendo che il canale sia libero, C avvia una trasmissione (diretta a B o a D). Il risultato è disastroso: i segnali di A e di C si sovrapporranno fisicamente in corrispondenza dell'antenna di B, causando una collisione e distruggendo i dati. In questo scenario, C è incapace di rilevare il potenziale competitore (A) ed è quindi definito come **nascosto** (hidden) rispetto alla comunicazione da A verso B. Il problema del terminale nascosto si verifica quando due o più stazioni, reciprocamente fuori raggio, trasmettono simultaneamente a un destinatario comune. Anche A, per lo stesso motivo legato alla distanza, non si accorgerà della collisione provocata da C.

### Il Problema del Terminale Esposto (Exposed Terminal)

> [!definition] Terminale Esposto (Exposed Terminal)
>
> Si verifica quando una stazione rinuncia inutilmente a trasmettere perché rileva sul canale il segnale di un'altra stazione, pur non essendoci alcun rischio di collisione al ricevitore di destinazione. La stazione "esposta" è in grado di ascoltare una trasmissione vicina ma irrilevante, e ne viene erroneamente bloccata dall'invio di frame del tutto legittimi verso un destinatario distante.

Consideriamo la stessa topologia (A, B, C, D). Questa volta, B sta trasmettendo dati verso A, e parallelamente C desidera inviare un messaggio a D. C, mettendosi in ascolto, rileva forte e chiaro il segnale di B. Applicando ciecamente le regole del CSMA, C conclude erroneamente di non poter trasmettere verso D, per paura di creare una collisione. In realtà, se C iniziasse a trasmettere, il suo segnale raggiungerebbe D senza problemi, e le due trasmissioni (da B verso A, e da C verso D) potrebbero avvenire perfettamente in parallelo senza disturbarsi a vicenda (le loro "zone di interferenza" ai ricevitori non si sovrappongono in modo distruttivo). In questo caso, C è un terminale **esposto** alla comunicazione tra B e A. Il problema del terminale esposto impedisce a una stazione trasmittente di inviare frame del tutto legittimi a causa dell'ascolto di un'interferenza locale generata da un'altra stazione.

Il fatto che non si possa verificare lo stato del canale al ricevitore semplicemente mettendosi in ascolto dal trasmettitore rende palese la necessità di progettare protocolli MAC sensibilmente diversi da quelli delle classiche reti LAN cablate.

---

## I Protocolli MACA e MACAW: Evitare le Collisioni

Per mitigare le problematiche descritte, nel 1990 Phil Karn presentò un protocollo rivoluzionario chiamato **MACA** (Multiple Access with Collision Avoidance), originariamente concepito per il "packet radio". L'idea fondante del MACA non è quella di rilevare le collisioni, ma di prevenirle stimolando il ricevitore a inviare un breve frame di controllo prima che inizi la trasmissione dei dati veri e propri (molto più lunghi). Le stazioni vicine, sentendo questo frame di controllo, si asterranno dal trasmettere durante il successivo invio dei dati.

### Il Meccanismo RTS / CTS

Il funzionamento si basa su uno scambio di messaggi denominato RTS/CTS:

1. **RTS (Request To Send):** Quando la stazione A desidera inviare dati a B, invia prima un breve pacchetto RTS indirizzato a B. Questo pacchetto non è generico, ma contiene l'ID della sorgente, l'ID della destinazione e, fattore cruciale, la lunghezza (durata) del frame dati che seguirà. Tutte le stazioni nel raggio di A (ad esempio C ed E) riceveranno questo RTS.

2. **CTS (Clear To Send):** Se B riceve l'RTS ed è pronto e desideroso di ricevere il messaggio, risponde trasmettendo un pacchetto CTS. Anche il CTS è un frame molto breve che copia e diffonde l'informazione sulla lunghezza dei dati ricevuta nell'RTS. Questo CTS verrà ascoltato da A (che ottiene così il permesso di procedere), ma anche da tutte le stazioni nel raggio di B (ad esempio D ed E).

3. Alla ricezione del frame CTS, la stazione A inizia a trasmettere il frame dati vero e proprio in totale sicurezza.

> [!tip] Insight chiave del meccanismo RTS/CTS
>
> Il meccanismo RTS/CTS risolve entrambi i problemi topologici in modo elegante: il terminale nascosto viene messo a tacere dal CTS del ricevitore (che esso sente, anche se non ha sentito l'RTS del mittente), mentre il terminale esposto viene liberato dall'obbligo di silenzio perché sente l'RTS ma non il CTS (e quindi deduce che la ricezione avviene fuori dalla sua area di influenza). Il canale viene così "prenotato" in modo distribuito, senza coordinamento centralizzato.

Vediamo come il MACA risolve i problemi topologici precedenti:

- **Gestione dell'Esposto (C):** La stazione C ascolta l'RTS inviato da A, ma, essendo troppo lontana da B, non sentirà mai il relativo CTS. Deduce quindi di essere un terminale esposto, comprende che la ricezione avverrà lontano dalla sua area di influenza ed è quindi del tutto libera di iniziare una propria trasmissione.

- **Gestione del Nascosto (D):** La stazione D non ascolta l'RTS di A, ma riceve forte e chiaro il CTS di risposta inviato da B. D capisce immediatamente che B è in procinto di ricevere dati e che una sua trasmissione disturberebbe B. Pertanto, D si silenzia disciplinatamente fino al completamento della trasmissione del frame dati (calcolando il tempo di attesa in base alla durata dichiarata nel CTS).

- Se una stazione centrale come E ascolta sia l'RTS che il CTS, sa ovviamente di dover rimanere in silenzio per non disturbare la delicata operazione in corso.


Nel MACA, le collisioni possono ancora avvenire? Assolutamente sì, ma **solo tra pacchetti RTS** (ad esempio se C e B inviano un RTS simultaneamente verso A). Quando due RTS collidono, il destinatario non genererà alcun CTS. Il grande vantaggio è che in queste collisioni non viene perso alcun dato applicativo (NO DATA information is lost) e, dato che gli RTS sono brevissimi (circa 20 byte), il canale viene tenuto occupato e sprecato solo per una frazione di tempo minuscola. In caso di collisione di RTS, i mittenti rinviano i messaggi utilizzando anch'essi la tecnica del **Binary Exponential Backoff** mutuata dall'Ethernet.

### L'Evoluzione: MACAW e l'Integrazione nel CSMA/CA

Il MACA originario è stato successivamente affinato dando vita al protocollo **MACAW** (MACA for Wireless LANs), documentato da Bharghavan et al. nel 1994. Il MACAW ha introdotto miglioramenti fondamentali:

- L'introduzione di un frame **ACK (Acknowledgement)** inviato dal ricevitore per confermare esplicitamente la ricezione corretta del frame dati.

- Meccanismi di condivisione delle informazioni (come i contatori di backoff) tra le stazioni per garantire un'allocazione equa (fair) del throughput.


La combinazione dei concetti del MACAW con l'aggiunta di una fase preventiva di "Carrier Sensing" (per evitare di inviare pacchetti RTS inutili in un canale già visibilmente saturo) ha dato vita al protocollo **CSMA/CA** (Carrier Sense Multiple Access with Collision Avoidance), che è il cuore pulsante dello standard IEEE 802.11 moderno.

### Esercizio Pratico: Topologia di Rete

Per testare la comprensione del meccanismo RTS/CTS, si consideri la seguente topologia di rete a grafo: il nodo A è connesso a B e C; il nodo D forma uno snodo centrale connesso a B, C, E, F; E è connesso a D e F; F è connesso a D e E. Applicando le regole appena spiegate:

1. In una trasmissione da E verso D, le stazioni B, C e F riceverebbero il CTS da D ma non l'RTS da E (agendo come terminali nascosti da proteggere).

2. Se D ascolta un RTS da E ma non il relativo CTS (ad esempio se E sta contattando F), D deduce di essere un terminale esposto rispetto a E.

3. Similmente, se B ascolta un CTS da D senza aver sentito alcun RTS, deve silenziarsi temporaneamente. Per esplorare appieno questi casi, gli studenti possono avvalersi delle simulazioni interattive per reti 802.11 (con o senza terminali nascosti) fornite durante il corso.


---

## Lo Standard IEEE 802.11 (Wi-Fi) e la sua Architettura

L'**IEEE** (Institute of Electrical and Electronics Engineers) è l'ente principale a livello mondiale per la standardizzazione delle reti locali (LAN). All'interno di questo ecosistema, il progetto IEEE 802 è gestito dall'IEEE 802 Working Group. La filosofia architetturale prevede che il sottolivello LLC (Logical Link Control) e i livelli superiori (es. Rete/IP, Trasporto/TCP o UDP, Applicazione) rimangano comuni tra le diverse tecnologie, mentre i livelli inferiori (il sottolivello MAC e il livello Fisico) vengano specializzati in base al mezzo trasmissivo adottato. Così come lo standard IEEE 802.3 definisce l'Ethernet CSMA/CD su cavo (UTP, STP, fibra), la famiglia **IEEE 802.11** definisce lo standard per le reti Wireless LAN (universalmente note con il marchio commerciale **Wi-Fi**) che utilizzano la trasmissione radio. Altri standard noti includono l'802.15 (Wireless PAN, come il Bluetooth) e l'802.16 (Broadband wireless, WiMAX).

### L'Evoluzione della Famiglia 802.11

Tutte le reti 802.11 operano sfruttando canali radio collocati nelle bande **ISM** (Industrial, Scientific, and Medical) o **U-NII** (Unlicensed National Information Infrastructure), comunemente nelle frequenze dei 900 MHz, 2.4 GHz e 5 GHz, garantendo progressivamente decine fino a migliaia di Mbit/s di capacità. Ripercorriamo l'evoluzione storica del livello fisico (PHY):

- **IEEE 802.11 (Legacy mode):** Rilasciato originariamente nel 1997 e chiarito nel 1999. Operava nella banda dei 2.4 GHz offrendo data rate molto bassi (1-2 Mbps) implementati tramite raggi infrarossi (IR) o frequenze radio. Avendo troppi gradi di libertà implementativi, poneva severi problemi di interoperabilità ed è oggi considerato obsoleto.

- **IEEE 802.11a:** Rilasciato nel 1999, è stato pioniere dell'uso della banda a 5 GHz (U-NII), offrendo un throughput tipico di 23 Mbps e un tetto massimo di 54 Mbps.

- **IEEE 802.11b:** Contemporaneo alla versione 'a' (1999), divenne lo standard di massa iniziale. Operando a 2.4 GHz (massimo 11 Mbps), implementava schemi di modulazione specifici per limitare le forti interferenze in quella banda affollata (telefoni cordless, microonde, ecc.).

- **IEEE 802.11g:** Introdotto nel 2003, mantenne l'uso della banda a 2.4 GHz ma aumentò la velocità fino a 54 Mbps.

- **IEEE 802.11n (WiFi 4):** Rilasciato nel 2009, ha introdotto il rivoluzionario supporto alla tecnologia **MIMO** (multiple-input multiple-output). Usando più antenne in trasmissione e ricezione contemporaneamente sia a 2.4 GHz che a 5 GHz, ha spinto il data rate massimo fino a 248 Mbps (e teoricamente 600 Mbps) estendendo la portata.

- **IEEE 802.11ac (WiFi 5):** Standardizzato nel 2013, si concentra esclusivamente sui 5 GHz, superando la barriera del gigabit (fino a 1.3 Gbps per flussi base, fino a 3.47 Gbps massimi).

- **IEEE 802.11ax (WiFi 6):** Rilasciato intorno al 2019/2020, supporta 2.4 GHz, 5 GHz e introduce i 6 GHz. Progettato per efficienza estrema in ambienti densi, raggiunge fino a 10-14 Gbps, con sensibili miglioramenti nel consumo energetico dei dispositivi e nei protocolli di sicurezza.

- _(Menzioni speciali):_ Versioni come 802.11af (2014, che sfrutta le bande TV inutilizzate) e 802.11ah (2017, per applicazioni a 900 MHz a lunghissimo raggio fino a 1 Km) si rivolgono ad ambiti specialistici o all'IoT.


|**Standard**|**Anno**|**Max Data Rate**|**Copertura (Range)**|**Frequenza**|
|---|---|---|---|---|
|**802.11b**|1999|11 Mbps|30 m|2.4 GHz|
|**802.11g**|2003|54 Mbps|30 m|2.4 GHz|
|**802.11n (WiFi 4)**|2009|600 Mbps|70 m|2.4, 5 GHz|
|**802.11ac (WiFi 5)**|2013|3.47 Gbps|70 m|5 GHz|
|**802.11ax (WiFi 6)**|2020|14 Gbps|70 m|2.4, 5 GHz|
|**802.11af**|2014|35-560 Mbps|1 Km|Bande TV (54-790 MHz)|
|**802.11ah**|2017|347 Mbps|1 Km|900 MHz|
|Tabella riassuntiva delle specifiche IEEE 802.11. Tutti utilizzano CSMA/CA e supportano configurazioni base-station o reti ad-hoc.|||||

### Elementi Architetturali: BSS ed ESS

Dal punto di vista della struttura della rete, il blocco logico fondamentale dell'802.11 è il **BSS (Basic Service Set)**. Un BSS è semplicemente un gruppo di stazioni wireless in grado di comunicare tra loro sotto il controllo di una singola funzione di coordinamento. Esistono due modalità operative principali per un BSS:

1. **Rete Ad-Hoc:** L'infrastruttura di controllo è assente. Le stazioni comunicano direttamente e pariteticamente (peer-to-peer) l'una con l'altra.

2. **Rete Infrastrutturata:** È presente una stazione base specializzata chiamata **AP (Access Point)**. Tutte le comunicazioni, anche tra due host della stessa cella, vengono obbligatoriamente incanalate e gestite attraverso l'AP.


Per formare reti più vaste, più BSS vengono interconnessi tra loro creando un **ESS (Extended Service Set)**. In questo scenario, gli Access Point fungono da ponti e forniscono connettività inter-cella instradando il traffico attraverso un'infrastruttura fissa (solitamente cablata) denominata **DS (Distribution System)**.

### Selezione del Canale e Meccanismi di Associazione

Lo spettro radio assegnato al Wi-Fi è logicamente suddiviso in vari canali operanti a frequenze leggermente diverse. L'amministratore di rete configura manualmente o automaticamente la frequenza in cui opera un determinato AP. Un problema tipico di progettazione si verifica quando AP limitrofi (vicini fisicamente) vengono configurati sullo stesso canale, generando interferenze distruttive tra le celle.

Quando un dispositivo wireless (es. smartphone o laptop) arriva in un'area coperta, deve associarsi a un AP prima di poter navigare. Questo avviene tramite una fase di scansione dei canali (scansione alla ricerca della rete e del suo **SSID** - Service Set Identifier, oltre all'indirizzo MAC dell'AP noto come BSSID). Esistono due modalità di scansione:

1. **Scansione Passiva (Passive Scanning):** L'host si mette in ascolto silente dei _beacon frames_ periodicamente e automaticamente trasmessi dagli AP circostanti. Una volta ricevuti i beacon, l'host sceglie tipicamente l'AP il cui segnale arriva con la massima potenza (highest signal strength). A questo punto, l'host invia all'AP selezionato un frame di _Association Request_, e attende in risposta un frame di _Association Response_.

2. **Scansione Attiva (Active Scanning):** L'host assume l'iniziativa e invia attivamente in broadcast un _Probe Request frame_ su vari canali. Gli AP nel raggio d'azione che ricevono la richiesta rispondono con _Probe Response frames_. L'host valuta le risposte, sceglie l'AP e avvia il classico handshake inviando l' _Association Request_ e ricevendo la _Association Response_.


Completata l'associazione, la stazione segue tipicamente le normali procedure di autenticazione di sicurezza e avvia un client DHCP per ottenere un indirizzo IP valido nella sottorete gestita dall'AP.

---

## Il Sottolivello MAC 802.11: DCF, PCF e Dinamiche CSMA/CA

Il sottolivello MAC dello standard IEEE 802.11 è diviso in due funzioni architetturali ben distinte che determinano le modalità di accesso al mezzo: la DCF e la PCF.

- **PCF (Point Coordination Function):** È un modulo opzionale che si posiziona concettualmente "sopra" il livello DCF e gestisce servizi _contention-free_ (ovvero privi di collisioni) in modo centralizzato, controllando rigorosamente i turni di trasmissione degli host.

- **DCF (Distributed Coordination Function):** È il fondamento universale del MAC 802.11. È sempre disponibile in ogni rete (ad-hoc o infrastrutturata) e gestisce l'accesso _contention-based_ tramite il protocollo **CSMA/CA**. Essendo un sistema decentralizzato e distribuito, le collisioni sono ovviamente una possibilità reale.


### Il Carrier Sensing: Fisico e Virtuale (NAV)

Nel CSMA/CA, prima di trasmettere, una stazione deve necessariamente accertarsi che il canale sia libero eseguendo il **Carrier Sensing**. Questo avviene su due livelli interconnessi:

1. **Sensore Fisico (Physical CS):** L'hardware analizza la frequenza per rilevare energia o intercettare l'arrivo di un segnale elettromagnetico, stabilendo se c'è attività nel canale dovuta ad altre fonti.

2. **Sensore Virtuale (Virtual CS):** È il meccanismo logico software. Il protocollo prevede l'inserimento di precise informazioni sulla durata temporale della comunicazione nell'header dei primissimi byte di frame come RTS, CTS e pacchetti Dati generici. Ascoltando queste durate, ogni stazione aggiorna una variabile locale chiamata **NAV** (Network Allocation Vector). Il NAV funge da timer: indica al sistema per quanto tempo il canale sarà "virtualmente occupato" e quanto bisogna aspettare prima di poter persino pensare di campionare nuovamente lo stato fisico del mezzo.


Basta che uno solo dei due sensori (Fisico o Virtuale/NAV) dia esito "occupato", affinché la stazione consideri l'intero canale indisponibile (busy).

### Gli Interframe Spaces (IFS) e le Priorità

Nel mondo 802.11, il concetto di "canale libero" è strettamente legato ai tempi. L'accesso prioritario al mezzo è regolamentato imponendo l'uso di periodi obbligatori di attesa e inattività chiamati **IFS** (Interframe Space). Lo standard definisce durate precise:

- **DIFS (Distributed IFS):** È un intervallo temporale "lungo". È il tempo minimo di default che una stazione normale deve attendere (misurando canale ininterrottamente libero) prima di poter avviare una trasmissione regolare.

- **SIFS (Short IFS):** È un intervallo temporale "brevissimo". Viene utilizzato esclusivamente come tempo di attesa prima di inviare pacchetti critici e ad altissima priorità, come i CTS o i messaggi di conferma ACK. Poiché rigorosamente **SIFS < DIFS**, la stazione che sta completando un handshake (es. sta per inviare un ACK) riuscirà sempre a prendere possesso del canale prima che le altre stazioni in attesa finiscano di contare il proprio lungo periodo DIFS, garantendo l'assenza di interruzioni durante le transazioni.


### L'Algoritmo CSMA/CA in Azione

Sintetizziamo i passaggi della DCF per trasmettitore e ricevitore:

1. **Attesa Iniziale:** Se la stazione mittente percepisce il canale costantemente libero per un periodo pari almeno al DIFS, trasmette l'intero frame dati (ricordiamo, senza collision detection).

2. **Backoff Randomico:** Se invece il canale risulta occupato (fisicamente o tramite NAV), la stazione fa partire un tempo di backoff casuale. Questo timer scorre alla rovescia (counts down) solamente mentre il canale risulta libero; si congela istantaneamente se un'altra stazione inizia a trasmettere. Quando il timer raggiunge lo zero (ed è trascorso anche il DIFS), la stazione trasmette.

3. **Il ruolo dell'ACK:** Ricevuto correttamente un frame, il destinatario attende il breve tempo SIFS e risponde immediatamente con un pacchetto ACK per confermare l'avvenuto recapito (l'ACK è vitale in wireless a causa delle perdite naturali e dei terminali nascosti).

4. **Gestione delle Collisioni:** Cosa succede se l'ACK non arriva? Il mittente assume che si sia verificata una collisione (o una perdita per attenuazione). Si innesca la penalità: il mittente incrementa l'intervallo casuale di backoff (raddoppiandolo ad ogni tentativo fallito secondo la logica Binary Exponential Backoff), aspetta il DIFS e ritenta la procedura.


_Nota sull'inefficienza delle collisioni semplici:_ Se avviene una collisione e l'RTS/CTS non viene impiegato, poiché nessuna stazione è in grado di interrompere la trasmissione a metà, l'intero frame dati verrà completamente sprecato, "sprecando" una massiccia porzione di larghezza di banda, specialmente se il frame era molto grande.

### RTS e CTS nello Standard IEEE 802.11

Per evitare l'enorme spreco di risorse causato dalle collisioni sui frame dati primari, l'implementazione 802.11 permette di "prenotare" (reserve) il mezzo trasmissivo utilizzando i mini-pacchetti RTS e CTS (descritti nel MACA). L'host invia prima l'RTS in modalità CSMA; l'AP di destinazione diffonde in broadcast un CTS per notificare l'autorizzazione e zittire tutte le altre stazioni (che aggiornano il loro NAV), permettendo poi la trasmissione incontrastata dei dati. Anche qui, se due RTS collidono per il possesso (reservation collision), solo i pacchettini corti vanno persi.

Gli amministratori di rete possono configurare la modalità DCF per gestire l'RTS/CTS in tre modi differenti (RTS Threshold):

1. **Mai (Never):** Non si usano RTS/CTS. Questa impostazione è eccellente per reti con carico di traffico estremamente leggero, in cui il ritardo aggiunto dallo scambio RTS/CTS sarebbe inutile e inefficiente.

2. **Soglia di dimensione:** RTS/CTS viene abilitato unicamente per messaggi "lunghi", ovvero quando la dimensione del pacchetto supera un certo limite (RTS Threshold) calcolato dall'amministratore.

3. **Sempre (Always):** L'uso dell'RTS/CTS è imposto per ogni trasmissione. È l'impostazione raccomandata in condizioni di altissimo carico e densità sul mezzo wireless per minimizzare le disastrose probabilità di sovrapposizione e la gestione dei nodi nascosti.


---

> [!abstract] Riepilogo dei Concetti Chiave
>
> Nelle LAN cablate (802.3) il rilevamento delle collisioni avviene direttamente durante la trasmissione (CSMA/CD), bloccando tempestivamente l'invio. Nelle WLAN (802.11) questo è fisicamente precluso a causa dell'attenuazione del segnale radio, per cui si adottano tecniche di "Avoidance" preventivo basate su ACK obbligatori (CSMA/CA). I problemi strutturali del mezzo radio — terminale nascosto ed esposto — derivano dall'impossibilità di verificare lo stato del canale al ricevitore ascoltando dal trasmettitore; entrambi vengono gestiti tramite il meccanismo di prenotazione del canale MACA/MACAW integrato nello standard 802.11 attraverso lo scambio RTS/CTS. Il Virtual Carrier Sensing e il NAV garantiscono il blocco totale delle trasmissioni indesiderate attraverso timer logici interni che propagano in modo distribuito la durata delle comunicazioni in corso. L'architettura unificata dello standard IEEE 802.11 — basata su BSS e ESS, tempi di attesa differenziati (SIFS vs DIFS) e Backoff Esponenziale — opera sulle bande ISM/U-NII libere da licenze, consentendo la connettività Wi-Fi moderna in una vasta gamma di scenari, dalle reti ad-hoc alle infrastrutture enterprise.
