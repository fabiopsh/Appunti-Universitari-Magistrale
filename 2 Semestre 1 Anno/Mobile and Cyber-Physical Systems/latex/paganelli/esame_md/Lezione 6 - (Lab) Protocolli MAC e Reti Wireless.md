# Lezione 6 - (Lab) Protocolli MAC e Reti Wireless

## Le Reti Wireless: Sfide e Problemi Strutturali

Nelle reti cablate il rilevamento delle collisioni in fase di trasmissione funziona perfettamente, ma nelle reti wireless questo principio fallisce a causa della natura stessa del mezzo radio. Nelle trasmissioni senza fili, la potenza del segnale decade rapidamente, diminuendo in proporzione al quadrato della distanza.

A causa di questa attenuazione, il segnale emesso dall'antenna del trasmettitore (il _self-signal_) risulta infinitamente più forte rispetto a qualsiasi altro segnale debole in arrivo da una stazione distante. Questo "acceca" il trasmettitore, rendendogli impossibile rilevare una collisione mentre sta inviando dati. Inoltre, le condizioni del canale wireless sono spazialmente diverse tra chi trasmette e chi riceve. Una collisione rilevata dal trasmettitore potrebbe non essere una collisione al ricevitore, e viceversa. Nelle reti wireless, l'unica cosa che conta veramente è l'**interferenza al ricevitore**, non al mittente. Questa limitazione genera due problemi classici della comunicazione radio: il _Terminale Nascosto_ e il _Terminale Esposto_.

### Il Problema del Terminale Nascosto (Hidden Terminal)

![[Pasted image 20260429160400.png]]

> [!definition] Terminale Nascosto (Hidden Terminal)
>
> Si verifica quando due o più stazioni, reciprocamente fuori dal raggio radio l'una dell'altra, trasmettono simultaneamente verso un destinatario comune. Poiché nessuna delle due stazioni riesce a rilevare la trasmissione dell'altra, entrambe credono il canale libero e avviano l'invio, causando una collisione al ricevitore che nessuna delle sorgenti è in grado di percepire.

Immaginiamo quattro stazioni allineate: A, B, C e D. A è in raggio radio con B; B è nel raggio di A e C; C è nel raggio di B e D. Supponiamo che A stia attualmente trasmettendo dei dati a B. C, desiderando trasmettere, si mette in ascolto sul mezzo. Poiché C si trova fisicamente al di fuori del raggio di copertura radio di A, non percepirà alcuna trasmissione in corso. Credendo che il canale sia libero, C avvia una trasmissione (diretta a B o a D). Il risultato è disastroso: i segnali di A e di C si sovrapporranno fisicamente in corrispondenza dell'antenna di B, causando una collisione e distruggendo i dati. In questo scenario, C è incapace di rilevare il potenziale competitore (A) ed è quindi definito come **nascosto** (hidden) rispetto alla comunicazione da A verso B. Il problema del terminale nascosto si verifica quando due o più stazioni, reciprocamente fuori raggio, trasmettono simultaneamente a un destinatario comune. Anche A, per lo stesso motivo legato alla distanza, non si accorgerà della collisione provocata da C.

Questo è il motivo per cui il protocollo **CSMA/CD**, standard nelle reti Ethernet cablate, non può essere usato nelle reti wireless: il meccanismo di rilevamento delle collisioni richiede che il trasmettitore possa ascoltare il canale mentre trasmette, il che è impossibile in radio (il self-signal del trasmettitore è ordini di grandezza più forte di qualsiasi segnale debole in arrivo).

> [!tip] Il punto chiave
>
> Con CSMA classico, il Carrier Sense viene eseguito dal trasmettitore, ma quello che conta è lo stato del canale **al ricevitore**. Il terminale nascosto è "nascosto" solo rispetto al trasmettitore corrente, non rispetto al ricevitore.

La soluzione a questo problema è il meccanismo **RTS/CTS**.

### Il Problema del Terminale Esposto (Exposed Terminal)

![[exam_mod2_exposed_terminal.jpg]]

> [!definition] Terminale Esposto (Exposed Terminal)
>
> Si verifica quando una stazione rinuncia inutilmente a trasmettere perché rileva sul canale il segnale di un'altra stazione, pur non essendoci alcun rischio di collisione al ricevitore di destinazione. La stazione "esposta" è in grado di ascoltare una trasmissione vicina ma irrilevante, e ne viene erroneamente bloccata dall'invio di frame del tutto legittimi verso un destinatario distante.

Il problema del **terminale esposto** è speculare al precedente: questa volta, una stazione si astiene inutilmente dal trasmettere perché percepisce un segnale sul canale, anche se quel segnale non crea interferenza al suo ricevitore di destinazione.

Consideriamo la stessa topologia (A, B, C, D). Questa volta, B sta trasmettendo dati verso A, e parallelamente C desidera inviare un messaggio a D. C, mettendosi in ascolto, rileva forte e chiaro il segnale di B. Applicando ciecamente le regole del CSMA, C conclude erroneamente di non poter trasmettere verso D, per paura di creare una collisione. In realtà, se C iniziasse a trasmettere, il suo segnale raggiungerebbe D senza problemi, e le due trasmissioni (da B verso A, e da C verso D) potrebbero avvenire perfettamente in parallelo senza disturbarsi a vicenda (le loro "zone di interferenza" ai ricevitori non si sovrappongono in modo distruttivo). In questo caso, C è un terminale **esposto** alla comunicazione tra B e A. Il problema del terminale esposto impedisce a una stazione trasmittente di inviare frame del tutto legittimi a causa dell'ascolto di un'interferenza locale generata da un'altra stazione.

> [!warning] Attenzione
>
> Il terminale esposto non è un problema di collisione, ma di **sotto-utilizzo del canale**. È meno grave del terminale nascosto (che causa corruzioni di dati), ma riduce il throughput complessivo della rete.

Il fatto che non si possa verificare lo stato del canale al ricevitore semplicemente mettendosi in ascolto dal trasmettitore rende palese la necessità di progettare protocolli MAC sensibilmente diversi da quelli delle classiche reti LAN cablate. Il meccanismo RTS/CTS del protocollo MACA risolve anche questo problema.

## I Protocolli MACA e MACAW: Evitare le Collisioni

Per mitigare le problematiche descritte, nel 1990 Phil Karn presentò un protocollo rivoluzionario chiamato **MACA** (Multiple Access with Collision Avoidance), originariamente concepito per il "packet radio". L'idea fondante del MACA non è quella di rilevare le collisioni, ma di prevenirle stimolando il ricevitore a inviare un breve frame di controllo prima che inizi la trasmissione dei dati veri e propri (molto più lunghi). Le stazioni vicine, sentendo questo frame di controllo, si asterranno dal trasmettere durante il successivo invio dei dati.

### Il Meccanismo RTS / CTS

![[exam_mod2_rts_cts.jpg]]

Il meccanismo **RTS/CTS** (*Request To Send / Clear To Send*) è il cuore del protocollo **MACA** e del successivo **MACAW**, ed è integrato nello standard **IEEE 802.11** (Wi-Fi). Risolve entrambi i problemi del terminale nascosto e del terminale esposto prenotando il canale in modo distribuito prima di trasmettere i dati.

Il funzionamento si basa su uno scambio di messaggi denominato RTS/CTS e si articola in tre fasi:

1. **Fase 1 — RTS (Request To Send):** Quando la stazione A desidera inviare dati a B, invia prima un breve pacchetto RTS (≈20 byte) indirizzato a B. Questo pacchetto non è generico, ma contiene l'ID della sorgente (A), l'ID della destinazione (B) e, fattore cruciale, la lunghezza (durata) del frame dati che seguirà. Tutte le stazioni nel raggio di A (ad esempio C ed E) riceveranno questo RTS.

2. **Fase 2 — CTS (Clear To Send):** Se B riceve l'RTS ed è pronto e libero per ricevere il messaggio, risponde trasmettendo un pacchetto CTS. Anche il CTS è un frame molto breve che copia e diffonde l'informazione sulla durata dei dati dichiarata nell'RTS. Questo CTS verrà ascoltato da A (che ottiene così il permesso di procedere), ma anche da tutte le stazioni nel raggio di B (ad esempio D ed E).

3. **Fase 3 — DATA:** Alla ricezione del frame CTS, la stazione A inizia a trasmettere il frame dati vero e proprio in condizioni sicure.

> [!tip] Insight chiave del meccanismo RTS/CTS
>
> Il meccanismo RTS/CTS risolve entrambi i problemi topologici in modo elegante: il terminale nascosto viene messo a tacere dal CTS del ricevitore (che esso sente, anche se non ha sentito l'RTS del mittente), mentre il terminale esposto viene liberato dall'obbligo di silenzio perché sente l'RTS ma non il CTS (e quindi deduce che la ricezione avviene fuori dalla sua area di influenza). Il canale viene così "prenotato" in modo distribuito, senza coordinamento centralizzato.

Vediamo in dettaglio come il MACA risolve i problemi topologici precedenti:

- **Come risolve il terminale esposto (C nel diagramma):** La stazione C ascolta l'RTS inviato da A, ma, essendo troppo lontana da B, non sentirà mai il relativo CTS di B. Da questo C deduce di essere un terminale esposto: comprende che la ricezione avviene lontano dalla sua area di influenza ed è quindi del tutto libera di iniziare una propria trasmissione senza creare interferenze.
- **Come risolve il terminale nascosto (D nel diagramma):** La stazione D non ascolta l'RTS di A (troppo lontano), ma riceve forte e chiaro il CTS di risposta inviato da B. D capisce immediatamente che B è in procinto di ricevere dati e che una sua trasmissione disturberebbe B. Pertanto, D si silenzia disciplinatamente per la durata indicata nel CTS, evitando di interferire con la ricezione di B.
- **Il caso E:** Se una stazione centrale come E si trova nella zona di sovrapposizione e ascolta sia l'RTS che il CTS, sa con certezza di dover rimanere in silenzio per tutta la durata della comunicazione per non disturbare l'operazione in corso.

> [!tip] Collisioni residue
>
> Con RTS/CTS le collisioni non scompaiono del tutto: possono ancora avvenire tra pacchetti RTS (es. se C e D inviano contemporaneamente RTS verso A). Ma in tal caso nessun dato applicativo viene perso (NO DATA information is lost), e lo spreco di canale è minimo dato che gli RTS sono brevissimi (circa 20 byte). I mittenti applicano il **Binary Exponential Backoff** prima di riprovare.

In 802.11, l'impiego di RTS/CTS è configurabile tramite una soglia di dimensione (*RTS Threshold*): sempre, mai, o solo per frame sopra una certa dimensione.
