# Reti Wireless e Standard IEEE 802.11

L'introduzione alle reti senza fili segna un passaggio fondamentale nello studio delle telecomunicazioni moderne, delineando il confine tra il mondo statico dei cavi e l'ubiquità della connettività mobile. In questo capitolo esploreremo le basi fisiche e architetturali delle reti wireless, le sfide intrinseche alla propagazione dei segnali radio e le prime nozioni sui protocolli necessari per gestire l'accesso a un mezzo condiviso e invisibile. Il testo segue un approccio *top-down*, in linea con la filosofia didattica di Kurose e Ross.

---

## Fondamenti delle Reti Wireless

### Perché le Reti Wireless

Tradizionalmente, i cavi nei computer sono stati impiegati per due scopi primari: comunicare e fornire energia. Tuttavia, l'evoluzione tecnologica ha portato alla nascita dei **Sistemi Cyber-Fisici** (*Cyber-Physical Systems*), i quali integrano capacità di calcolo, sensori, meccanismi di controllo e funzionalità di rete direttamente all'interno di oggetti fisici e infrastrutture, connettendoli a Internet e tra di loro. Poiché è materialmente impossibile cablare ogni singolo oggetto fisico, la tecnologia si è adattata di conseguenza: le reti wireless sostituiscono i cavi per le telecomunicazioni, mentre le batterie rimpiazzano i cavi per l'alimentazione elettrica.

### Elementi di una Rete Wireless

Una rete wireless è costituita da host connessi tramite collegamenti senza fili. Gli **host wireless** sono i dispositivi finali (*end-system*) che eseguono le applicazioni: smartphone, tablet, laptop, sensori, elettrodomestici smart e veicoli. Essi sono solitamente alimentati a batteria e possono essere stazionari oppure mobili.

> [!warning] Wireless ≠ Mobile
>
> È fondamentale sfatare un equivoco comune: **wireless non implica necessariamente mobilità** ($wireless \neq mobile$). Un dispositivo può essere connesso senza fili pur rimanendo fisso in un punto. Mobilità e assenza di cavi sono dimensioni ortogonali.

Un ruolo cardine è giocato dalla **Stazione Base** (*Base Station*) o **Access Point**: essa è responsabile dell'invio e della ricezione dei dati da e verso gli host wireless ad essa associati. Fungere da relè è il suo compito principale, essendo tipicamente connessa a una rete cablata più ampia (si pensi alle torri cellulari o agli Access Point IEEE 802.11). Un host wireless si definisce "associato" a una stazione base quando si trova entro la distanza utile di comunicazione e la utilizza per instradare i dati verso la rete più ampia.

I **collegamenti wireless** (*Wireless Links*) connettono i dispositivi mobili alla stazione base e sono utilizzati anche come collegamenti di backhaul. Poiché il canale è condiviso, un protocollo di accesso multiplo coordina l'accesso al collegamento tramite tecniche come l'accesso casuale, FDMA, TDMA, CDMA o Polling. Un aspetto significativo della complessità moderna è che un singolo dispositivo wireless è dotato di diverse interfacce radio per connettersi a reti differenti: un iPhone 16, ad esempio, è equipaggiato con circa 11 radio differenti e numerose antenne, tra cui 5 diverse radio cellulari, WiFi, Bluetooth, UWB, radio satellitare, NFC e GPS.

### Tassonomia e Prestazioni

Le reti wireless possono essere classificate incrociando due dimensioni: la presenza o assenza di un'infrastruttura centralizzata e il numero di salti (*hop*) necessari per la comunicazione. Le quattro categorie risultanti sono le seguenti.

Nella configurazione **single-hop con infrastruttura** l'host si connette direttamente a una stazione base (WiFi, WiMAX, cellulare 3G/4G/5G), la quale fornisce l'accesso a Internet. Tutte le operazioni di rete tradizionali — autenticazione, fatturazione, assegnazione degli indirizzi IP e routing — sono gestite dall'infrastruttura cablata. È supportato l'**Handoff**, ovvero il processo tramite cui un dispositivo mobile cambia la stazione base di riferimento senza perdere la connessione.

Nella configurazione **multi-hop con infrastruttura** l'host deve passare attraverso diversi nodi wireless prima di raggiungere il nodo connesso a Internet. Questo è il caso delle reti *Mesh* (WiFi Mesh o tecnologie radio per la sicurezza pubblica come TETRA).

Nella configurazione **single-hop senza infrastruttura** non c'è stazione base e non è necessariamente garantita una connessione a Internet. Un esempio classico è il Bluetooth.

Infine, nelle reti **multi-hop senza infrastruttura** i nodi devono fare affidamento sugli altri partecipanti per l'inoltro dei messaggi. Questo è il modello tipico di ZigBee, delle **MANET** (*Mobile Ad-hoc Networks*) e delle **VANET** (*Vehicular Ad-hoc Networks*).

| Modalità | Infrastruttura | Hop | Esempi |
|---|---|---|---|
| Single-hop con infrastruttura | Sì | 1 | WiFi, 4G/5G |
| Multi-hop con infrastruttura | Sì | >1 | WiFi Mesh, TETRA |
| Single-hop senza infrastruttura | No | 1 | Bluetooth |
| Multi-hop senza infrastruttura | No | >1 | ZigBee, MANET, VANET |

Dal punto di vista delle prestazioni esiste un chiaro compromesso tra il tasso di trasferimento dati e l'intervallo di copertura. Per ambienti indoor (10–30 m), lo standard 802.11ax può raggiungere i 14 Gbps, mentre il Bluetooth si attesta sui 2 Mbps. Spostandosi su scenari outdoor a lungo raggio (4–15 km), il 5G può fornire fino a 10 Gbps mentre il 4G LTE garantisce un'ampia copertura.

---

## Fisica dei Segnali Radio

### Onde Elettromagnetiche e Modulazione

La comunicazione wireless è resa possibile dall'elettromagnetismo: una variazione di corrente in un punto (trasmettitore) genera un campo elettromagnetico nello spazio che induce una corrente in una posizione remota (ricevitore).

Le **onde elettromagnetiche** uniscono il campo elettrico e quello magnetico e si propagano alla velocità della luce. Sono caratterizzate dalla **lunghezza d'onda** ($\lambda$), ovvero la distanza spaziale tra due picchi d'onda successivi; dal **tempo di ciclo**, il tempo intercorso tra due picchi successivi; e dalla **frequenza**, l'inverso del tempo di ciclo (misurata in Hz), calcolabile come $c/\lambda$. Si aggiungono la direzionalità di propagazione e l'ampiezza variabile nel tempo.

Un concetto fondamentale per la trasmissione dei bit è la **fase** (*Phase*), che indica la posizione di un segnale periodico all'interno del suo ciclo a un dato istante $t$ (spesso misurata in gradi, da 0° a 360°). È possibile codificare informazioni binarie nel segnale alterando la sua fase pur mantenendo la stessa frequenza: questa tecnica è alla base della **modulazione di fase** (*Phase Shift Keying*).

### Potenza, Banda e Capacità di Shannon

La forza di un segnale radio è definita dalla sua **Potenza**, ovvero l'energia trasmessa o ricevuta dall'antenna per unità di tempo. Può essere misurata in scala lineare usando i Watt (o milliwatt) o in scala logaritmica mediante i decibel (dBm), con la seguente formula di conversione:

$$P_{dBm}=10\cdot \log_{10}\left(\frac{P_{mW}}{1\,\text{mW}}\right)$$

Ad esempio, la potenza trasmissiva massima tipica di un dispositivo mobile è di 250 mW, che equivale a 24 dBm.

L'occupazione dello spettro è descritta dalla **Densità Spettrale di Potenza** (*Power Spectral Density* — PSD), che illustra come la potenza del segnale è distribuita in funzione della frequenza, di solito centrata attorno a una **frequenza portante** (*Carrier Frequency*). La **Larghezza di Banda** (*Bandwidth*) — da non confondersi con la "banda" intesa come capacità massima di trasmissione dati — indica l'estensione in Hz del range di frequenze utilizzato dal segnale. Ad esempio, il canale 6 di una rete WiFi utilizza 22 MHz di larghezza di banda (distribuiti tra 2.427 e 2.449 GHz, centrati a 2.438 GHz).

Nella realtà il segnale deve scontrarsi con il **Rumore** (*Noise*) e l'**Interferenza**, causata da altri trasmettitori che operano nella stessa banda. Il parametro che descrive la qualità del canale è il **Rapporto Segnale-Rumore** (*SNR — Signal-to-Noise Ratio*), spesso misurato in dB:

$$SNR_{dB}=10\cdot \log_{10}\left(\frac{\text{received signal power}}{\text{noise power}}\right)$$

Un SNR pari a 0 dB implica che segnale e rumore hanno uguale potenza. A SNR elevati è facile estrarre il segnale; i limiti operativi inferiori sono circa −10/−6 dB per i cellulari e 20 dB per il WiFi.

> [!note] La banda ISM 2.4 GHz e il problema dell'affollamento
>
> La banda a 2.4 GHz, nota come **banda ISM** (*Industrial, Scientific and Medical*), è non licenziata ed estremamente affollata: ospita contemporaneamente dispositivi WiFi, Bluetooth, ZigBee, forni a microonde, telecomandi per garage, baby monitor e droni. Questo rende il canale particolarmente soggetto a interferenze, e spiega in parte la migrazione verso la banda a 5 GHz introdotta dagli standard più recenti.

> [!definition] Shannon Capacity
>
> Il lavoro di Claude Shannon del 1948 definisce il limite massimo teorico della velocità con cui i dati possono essere trasmessi su un canale in funzione della larghezza di banda e dell'SNR:
>
> $$C = B \cdot \log_{2}\!\left(1 + \frac{\text{received signal power}}{\text{noise power}}\right)$$
>
> Dove $C$ è la capacità in bit/s e $B$ è la larghezza di banda in Hz. Nessun sistema reale può superare questo limite, indipendentemente dalla tecnica di codifica o modulazione adottata.

> [!tip] Il trade-off tra SNR e modulazione
>
> La capacità di Shannon scala **linearmente** con la banda, ma solo **logaritmicamente** con l'SNR. Superato un certo limite, incrementare a dismisura la potenza del segnale — e quindi l'SNR — offre vantaggi sempre minori in termini di bitrate. Di conseguenza, la scelta pratica non è "più potenza sempre", ma adattare lo schema di modulazione all'SNR disponibile: con SNR basso si usano modulazioni robuste come BPSK (1 Mbps), mentre con SNR elevato si può passare a modulazioni ad alto rateo come QAM-256 (8 Mbps).

---

## Le Sfide della Propagazione

### Path Loss, Terminali Nascosti e Multipath

La natura stessa delle onde radio introduce severe sfide per le architetture di rete, che non hanno equivalenti nel mondo cablato.

La prima sfida è il **Path Loss** (o *fading*): il segnale radio si attenua perdendo potenza mentre si propaga. L'attenuazione segue una proporzione generale $1/(f \cdot d)^n$, dove $f$ è la frequenza, $d$ la distanza e l'esponente $n$ dipende dall'ambiente — vale 2 per lo spazio libero, tra 2.7 e 3.5 in aree urbane, e tra 3 e 6 all'interno degli edifici. All'aumentare della distanza, quindi, la ricezione diventa progressivamente più difficile, e frequenze più alte si attenuano più rapidamente.

> [!warning] Hidden Terminal Problem
>
> A causa dell'attenuazione con la distanza (o per la presenza di ostacoli fisici come montagne e palazzi), due nodi potrebbero non essere in grado di percepirsi a vicenda, pur essendo entrambi nel raggio di un terzo nodo intermedio. Se A e C vogliono comunicare con B, ma A e C sono fuori portata l'uno per l'altro, entrambi potrebbero iniziare a trasmettere contemporaneamente — inconsapevoli della reciproca interferenza — causando una collisione disastrosa al ricevitore B. Questo è il **Problema del Terminale Nascosto** (*Hidden Terminal Problem*), e non può essere rilevato dal classico meccanismo CSMA/CD.

![Schema del problema del terminale nascosto: A e C non si vedono ma collidono in B](https://upload.wikimedia.org/wikipedia/commons/2/2b/Wifi_hidden_station_problem.svg)
*Fonte: Wikimedia Commons — I nodi A e C non si trovano nel reciproco raggio di copertura (cerchi tratteggiati non sovrapposti), ma entrambi raggiungono B. Le trasmissioni simultanee causano una collisione invisibile ai due mittenti.*

La terza sfida è il **Multipath**: il segnale trasmesso non viaggia solo in linea d'aria, ma si riflette, viene diffratto e disperso (*scattering*) dal suolo e dagli edifici circostanti. Al ricevitore giungono quindi diverse copie del segnale originale, sfalsate temporalmente. Per evitare che questi echi interferiscano con la trasmissione successiva, i pacchetti di impulsi devono essere distanziati nel tempo. L'intervallo minimo richiesto prima di poter inviare un nuovo segnale senza sovrapposizioni si chiama **Tempo di Coerenza** (*Coherence Time* — $T_c$). Il $T_c$ è inversamente proporzionale alla frequenza utilizzata e alla velocità del ricevitore in caso di mobilità: sistemi ad alta frequenza e ricevitori in movimento richiedono guardie temporali più brevi ma più frequenti.

![Diagramma multipath: trasmettitore, percorso diretto e percorsi riflessi su ostacoli urbani](https://upload.wikimedia.org/wikipedia/commons/f/f2/Multipath_propagation_diagram_en.svg)
*Fonte: Wikimedia Commons — Il trasmettitore (sinistra) invia il segnale verso il ricevitore (destra) attraverso un percorso diretto e più percorsi riflessi dagli edifici circostanti. Al ricevitore giungono "fantasmi" del segnale sfalsati nel tempo, che possono interferire con la trasmissione successiva.*

Questi tre fenomeni influenzano direttamente il **Bit Error Rate** (*BER*), ovvero la probabilità che un bit trasmesso arrivi errato. Per un dato livello fisico, aumentare la potenza riduce il BER incrementando l'SNR. L'adattamento dinamico dello schema di modulazione in base all'SNR rilevato — tecnica nota come *Adaptive Modulation and Coding* — è uno dei meccanismi fondamentali dei sistemi wireless moderni.

---

## Protocolli per Reti Wireless

Le criticità fisiche descritte sopra creano sfide sistemiche che si ripercuotono su tutti i livelli dello stack protocollare: visibilità limitata della rete da parte del singolo nodo (terminali nascosti e terminali esposti), fallimenti e mobilità dei terminali, limiti intrinseci di batteria e memoria, e il problema della privacy causato dall'intercettazione dei segnali (*eavesdropping*).

Per mitigare questi limiti è necessario adottare meccanismi appositi. Il **CSMA/CD**, protocollo standard per reti cablate Ethernet, non può essere utilizzato: un nodo radio non è in grado di trasmettere e ricevere contemporaneamente per "ascoltare" una collisione nel proprio segnale. È quindi necessario un protocollo MAC alternativo. Serve inoltre la gestione dell'**Hand-off** per la transizione tra Access Point, e complessi protocolli di **Routing multi-hop** (per reti ad hoc) capaci di reagire ai cambiamenti arbitrari della topologia di vicinato (*neighborhood*).

Nello stack dei protocolli per reti wireless, mentre i livelli Applicazione e Trasporto (TCP/UDP) restano identici al mondo cablato, le fondamenta si differenziano profondamente. Il livello di Rete per ecosistemi senza infrastruttura si affida a protocolli speciali come AODV, DSR o DYMO. Il livello Datalink implementa l'accesso al mezzo tramite il protocollo **CSMA/CA** (*Carrier Sense Multiple Access with Collision Avoidance*), appositamente studiato per aggirare le trappole dei collegamenti radio.

> [!question] Possibili domande d'esame
>
> - Qual è la differenza tra una rete wireless single-hop e multi-hop con infrastruttura? Fare esempi concreti.
> - Perché il CSMA/CD non può essere applicato nelle reti wireless? Quale protocollo lo sostituisce e con quale logica?
> - Definire la Shannon Capacity e spiegare perché la capacità scala logaritmicamente con l'SNR e non linearmente.
> - Descrivere il problema del terminale nascosto: come si manifesta e perché il meccanismo di rilevamento delle collisioni classico non lo rileva?
> - Cosa si intende per Multipath e Coherence Time? Come la velocità del ricevitore influenza il $T_c$?
> - Spiegare il trade-off tra SNR e scelta dello schema di modulazione (es. BPSK vs QAM-256).
> - Cosa distingue la banda ISM dalla banda licenziata? Perché la banda 2.4 GHz è particolarmente soggetta a interferenze?
