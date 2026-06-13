
# Protocolli MAC per Reti Wireless Multi-hop

## Il problema dell'efficienza energetica

Nei sistemi IoT e nelle reti di sensori wireless, il protocollo MAC non ha come unico obiettivo l'arbitrazione dell'accesso al mezzo: deve anche — e soprattutto — minimizzare il consumo energetico dei nodi. La ragione è semplice: i dispositivi sono tipicamente alimentati a batteria e devono operare per mesi o anni senza manutenzione. Il radio transceiver è di gran lunga il componente più energivoro, e la strategia fondamentale è ridurne il **duty cycle**, ovvero la frazione di tempo in cui rimane attivo.

> [!tip] Intuizione chiave
>
> Un nodo con la radio sempre accesa è connesso ma scarica la batteria rapidamente. Un nodo con la radio sempre spenta risparmia energia ma non può comunicare. Il protocollo MAC deve trovare il giusto compromesso.

Il tradeoff principale è tra **energia** da un lato e **latenza e banda** dall'altro: abbassare il duty cycle risparmia energia ma aumenta il tempo di attesa prima che i pacchetti possano essere trasmessi o ricevuti.

Esistono tre approcci fondamentali per ridurre il consumo:

| Approccio | Descrizione | Esempi |
|---|---|---|
| Sincronizzazione dei nodi | I nodi si svegliano contemporaneamente per comunicare | S-MAC, IEEE 802.15.4 |
| Preamble sampling | Il mittente invia un lungo preambolo; il ricevitore campiona periodicamente il canale | B-MAC, X-MAC, BoX-MAC |
| Polling | Un master coordina i nodi slave tramite beacon periodici | Bluetooth, IEEE 802.15.4 |

---

## Sincronizzazione: S-MAC

S-MAC (*Sensor MAC*) è un protocollo progettato per reti wireless multi-hop, disponibile in TinyOS per piattaforme come le mica motes (Iris, Tmote). La sua idea di base è che se i nodi vicini si svegliano nello stesso istante, possono comunicare durante la finestra di attività e poi tornare in stato di sleep, riducendo drasticamente il consumo complessivo.

> [!definition] Duty cycle in S-MAC
>
> Ogni nodo alterna periodi di **listen** (radio accesa, pronto a ricevere) e periodi di **sleep** (radio spenta). La finestra di ascolto è periodica e relativamente breve rispetto al periodo totale.

### Organizzazione della sincronizzazione

S-MAC non impone una sincronizzazione globale, ma solo **locale**: nodi adiacenti si accordano su un periodo di ascolto condiviso. Il meccanismo è il seguente:

- Ogni nodo trasmette periodicamente dei **frame SYNC** in broadcast, che annunciano la propria schedule (quando si sveglia, quando dorme).
- Un nodo che si avvia ascolta il canale per individuare frame SYNC dei vicini. Se trova vicini con una schedule già definita, la adotta. In caso contrario, sceglie autonomamente la propria schedule e la pubblicizza.
- Un nodo può successivamente cambiare la propria schedule se la maggior parte dei vicini ha adottato un'altra.

Questo approccio consente a sottoreti di adottare schedule diverse, creando delle **isole di sincronizzazione** locali. Il risultato non è una sincronizzazione globale uniforme, ma va bene per la maggior parte delle topologie pratiche.

### Comunicazione durante il periodo di ascolto

Un nodo può inviare un frame a un vicino solo durante il **periodo di ascolto del ricevitore**, non necessariamente durante il proprio. Ciò implica che il mittente deve conoscere le schedule di tutti i suoi vicini e tenere la radio accesa anche al di fuori del proprio periodo di ascolto quando deve trasmettere.

> [!note] Carrier sense e RTS/CTS
>
> Prima della trasmissione S-MAC esegue il **carrier sense**: se il canale è occupato, il frame viene posticipato al periodo di ascolto successivo. Per evitare collisioni usa RTS/CTS (come IEEE 802.11). Una piccola ottimizzazione chiamata *adaptive duty cycle*: se un nodo riceve un RTS o un CTS in sorveglianza, mantiene la radio accesa fino al termine della trasmissione, perché potrebbe essere il prossimo hop.

![Schema S-MAC: trasmissione nei periodi di ascolto](images/lezione-17-mac-protocols-img-01.jpg)
*Fig. — Il frame Sync e il frame Data vengono trasmessi durante il periodo di attività del ricevitore; i periodi di silenzio T separano le finestre di ascolto.*

![Consumo energetico aggregato S-MAC su percorso 10 hop](images/lezione-17-mac-protocols-img-02.jpg)
*Fig. — Consumo energetico totale in funzione del periodo inter-arrivo dei messaggi. La curva "No sleep cycles" è il riferimento; il duty cycle al 10% riduce drasticamente i consumi; l'adaptive duty cycle ottimizza ulteriormente.*

### Latenza nei percorsi multi-hop

La latenza è il tallone d'Achille di S-MAC. In un percorso multi-hop, un frame deve attraversare una sequenza di nodi intermedi: in ogni hop, nel caso peggiore, il frame deve attendere fino al successivo periodo di ascolto del nodo successivo. Se i nodi lungo il percorso hanno schedule diverse, questo attesa si accumula ad ogni salto.

> [!warning] Latenza nel worst case
>
> In una catena di $n$ hop con schedule non allineate, la latenza totale è proporzionale a $n \times T_{listen\_period}$. Con duty cycle bassi (periodo lungo), la latenza può diventare inaccettabile per applicazioni real-time.

Questa latenza è mitigata — ma non eliminata — dalla tendenza dei nodi a convergere verso schedule condivise nel loro vicinato. Se nodi consecutivi lungo un percorso di routing condividono la stessa schedule, il frame non deve attendere tra un hop e l'altro. Tuttavia, questo allineamento non è garantito.

![Latenza media per hop in S-MAC](images/lezione-17-mac-protocols-img-03.jpg)
*Fig. — Latenza media per hop in funzione del numero di hop. Il duty cycle al 10% senza adaptive listen introduce latenze molto più elevate rispetto alla modalità senza sleep e alla variante con adaptive listen.*

### Mantenimento della sincronizzazione

Nel tempo, il **clock drift** (deriva dell'orologio hardware) può desincronizzare i nodi. S-MAC include un meccanismo per il mantenimento della sincronizzazione basato sui frame SYNC periodici. Inoltre, in topologie complesse, potrebbe essere impossibile per un nodo avere un periodo di ascolto compatibile con *tutti* i suoi vicini simultaneamente, e in quel caso S-MAC permette al nodo di cambiare schedule o di mantenerne più di una.

---

## Preamble Sampling: B-MAC

B-MAC (*Berkeley MAC*) rappresenta un approccio radicalmente diverso: invece di sincronizzare i nodi, **elimina del tutto la necessità di coordinazione temporale**. È disponibile in TinyOS per mica motes e si basa sul concetto di *Low-Power Listening* (LPL).

> [!definition] Low-Power Listening (LPL)
>
> Il ricevitore attiva periodicamente la radio per un brevissimo intervallo e controlla se c'è un preambolo sul canale. Se non rileva nulla, torna immediatamente in sleep. Se rileva un preambolo, mantiene la radio accesa per ricevere il frame.

Il mittente, dal canto suo, non deve aspettare il momento giusto: **trasmette quando vuole**, ma antepone al frame un **preambolo molto lungo** — più lungo dell'intervallo di sleep del ricevitore. In questo modo, qualunque sia il momento in cui il ricevitore esegue il campionamento (preamble sampling), il preambolo è ancora "in aria" e può essere rilevato.

![Schema temporale del preamble sampling B-MAC](images/lezione-17-mac-protocols-img-04.jpg)
*Fig. — Il mittente trasmette un lungo preambolo seguito dal frame. Il ricevitore esegue campionamenti brevi e periodici (preamble sampling); quando rileva il preambolo, mantiene la radio accesa per ricevere il frame.*

![Profilo di corrente del radio Mica-Mote durante il ciclo LPL](images/lezione-17-mac-protocols-img-05.jpg)
*Fig. — Profilo di corrente (mA) nel tempo (ms) durante un ciclo di Low-Power Listening: sleep → init → startup → receive mode → ricezione segnale → decoding → sleep. Le fasi (a)-(g) evidenziano i picchi di consumo durante l'attivazione.*

### Bilanciamento energetico

Il principio di B-MAC è spostare il costo energetico dalla ricezione alla trasmissione:

- **Ricevitore**: risparmia molto perché esegue solo brevi campionamenti periodici (molto economici) invece di tenere la radio sempre accesa.
- **Trasmittente**: spende di più perché deve trasmettere un preambolo lunghissimo (dell'ordine di 113 ms per il CC1000) prima di ogni frame dati.

> [!tip] Intuizione chiave
>
> Il preambolo deve essere più lungo del periodo di sleep! Se il ricevitore dorme per $T_{sleep}$, il preambolo deve durare almeno $T_{sleep}$ per garantire che il ricevitore lo intercetti durante il suo campionamento.

### Modello energetico

Definiamo i parametri:
- $f_d$ = frequenza di trasmissione dei dati (Hz)
- $f_c$ = frequenza di campionamento del preambolo (preamble sampling rate)
- $p_t$ = potenza in trasmissione
- $p_r$ = potenza in ricezione
- $p_i$ = potenza in idle (radio accesa ma non trasmette né riceve)

Per il **trasmittente**, il duty cycle è:

$$DC_{data} = f_d \cdot (t_{preamble} + t_{frame})$$
$$DC_{check} = f_d \cdot t_{check}$$

L'energia consumata in $t$ secondi è:

$$E_T(t) = t \left[ p_t \cdot DC_{data} + p_r \cdot DC_{check} + p_i \cdot (1 - DC_{data} - DC_{check}) \right]$$

Per il **ricevitore**:

$$DC_{data} = f_c \cdot (t_{listen} + t_{data})$$
$$DC_{check} = f_c \cdot t_{check}$$

$$E_R(t) = t \left[ p_r \cdot DC_{data} + p_r \cdot DC_{check} + p_i \cdot (1 - DC_{data} - DC_{check}) \right]$$

Da questi, la **lifetime** della batteria è:

$$lifetime_T = \frac{battery}{E_T(1)}, \quad lifetime_R = \frac{battery}{E_R(1)}$$

### Parametri reali (CC1000 radio)

| Parametro | Valore |
|---|---|
| $p_t$ (trasmissione) | 60 mW |
| $p_r$ (ricezione) | 45 mW |
| $p_i$ (idle) | 0,09 mW |
| Lunghezza preambolo | 271 byte (113 ms) |
| Frame dati | 36 byte (15 ms) |
| Durata check | 0,35 ms |

L'analisi numerica mostra che la lifetime sia del trasmittente sia del ricevitore dipende fortemente dall'**intervallo di check** (il periodo di sleep tra un campionamento e l'altro) e dal **traffico nella cella**. Esiste un intervallo di check ottimale che massimizza la lifetime per ciascun tasso di campionamento dei dati: campionamenti radi dei dati permettono check interval più lunghi (e quindi meno campionamenti del preambolo), massimizzando la durata della batteria.

> [!note] Nota sulla scalabilità
>
> Il modello mostra che anche considerando più trasmittenti contemporanei, il trend della lifetime non cambia qualitativamente. La lifetime dipende principalmente dall'intervallo di check e dalla quantità di traffico nella cella radio.

### Punti di forza e limiti di B-MAC

**Punti di forza:**
- Non è un protocollo di organizzazione di rete (non impone strutture topologiche).
- Semplicissimo da configurare: un solo parametro, l'intervallo di check.
- Trasparente ai livelli superiori dello stack.

**Limiti:**
- Preamboli lunghi hanno un costo energetico elevato per il trasmittente.
- All'aumentare dell'intervallo di check (per risparmiare in ricezione), il preambolo deve allungarsi, aumentando il costo in trasmissione.
- In scenari con traffico elevato può risultare meno efficiente della sincronizzazione.

---

## Preamble Sampling: X-MAC

X-MAC è un'evoluzione diretta di B-MAC che risponde alla domanda: *si può ridurre il costo del lungo preambolo?* La risposta è sì, inserendo nel preambolo l'**indirizzo del destinatario**.

Il meccanismo funziona così:

1. Il mittente inizia a trasmettere preamboli brevi ripetuti, ciascuno contenente l'ID del ricevitore target.
2. I nodi che non sono il destinatario ignorano il preambolo.
3. Il destinatario, al primo campionamento, riconosce il proprio ID, **interrompe il preambolo** inviando un acknowledgement, e richiede il frame.
4. Il mittente smette di trasmettere il preambolo e invia direttamente il frame.

> [!tip] Intuizione chiave
>
> In B-MAC il preambolo deve durare almeno $T_{sleep}$ indipendentemente da quando il ricevitore si sveglia. Con X-MAC, la durata effettiva del preambolo è solo il tempo che intercorre tra l'inizio della trasmissione e il momento in cui il ricevitore fa il campionamento: in media $T_{sleep}/2$.

Simulazioni su reti a stella (un ricevitore, più trasmittenti) mostrano che X-MAC riduce significativamente il duty cycle totale rispetto a B-MAC, specialmente con intervalli di check più lunghi.

---

![Confronto temporale X-MAC vs B-MAC](images/lezione-17-mac-protocols-img-06.jpg)
*Fig. — In B-MAC il preambolo dura per tutta la finestra di sleep del ricevitore. In X-MAC il preambolo è una sequenza di frame corti con l'ID del destinatario: il ricevitore interrompe la trasmissione appena si sveglia, riducendo tempo ed energia spesi.*

![Duty cycle totale trasmittenti: X-MAC vs B-MAC al variare del numero di nodi](images/lezione-17-mac-protocols-img-07.jpg)
*Fig. — Simulazione su rete a stella. X-MAC (curve in basso) mantiene un duty cycle significativamente inferiore rispetto a B-MAC (curve in alto) per tutti gli intervalli LPL e al crescere del numero di trasmittenti.*

## Preamble Sampling: BoX-MAC

BoX-MAC (*Backoff X-MAC*) è un ulteriore sviluppo di X-MAC. L'idea chiave è che il preambolo stesso diventa una **sequenza ripetuta del frame dati reale**.

Il funzionamento è il seguente:

1. Il mittente trasmette ripetutamente l'intero frame (header + payload).
2. Il ricevitore, al campionamento, intercetta un'istanza del frame.
3. Se è il destinatario, aspetta il boundary del frame successivo, lo riceve completamente, invia un ACK per fermare il trasmittente.

Questa strategia elimina la distinzione tra preambolo e frame: il "preambolo" è il frame stesso, e il ricevitore non deve aspettare la fine del preambolo per ricevere i dati — basta aspettare il prossimo frame della sequenza. Funziona bene con **frame di piccole dimensioni**, che è il caso tipico nelle reti di sensori.

In scenari multi-hop, BoX-MAC mostra comportamenti interessanti: i nodi intermedi possono eventualmente "sentire" i frame ripetuti e anticipare il routing, riducendo ulteriormente la latenza end-to-end.

---

![Diagramma temporale BoX-MAC](images/lezione-17-mac-protocols-img-08.jpg)
*Fig. — Il mittente ripete il frame più volte. Il ricevitore, al campionamento, aspetta il boundary del frame successivo, lo riceve, e invia un ACK per fermare la trasmissione. La legenda mostra Data TX, Data RX, ACK, y (sync) e channel sampling.*

![Routing multi-hop in BoX-MAC](images/lezione-17-mac-protocols-img-09.jpg)
*Fig. — Tre nodi i1, i2, i3 in cascata. Il nodo i1 trasmette ripetutamente; i2 riceve nel proprio check interval e ritrasmette a i3; i3 riceve nel check interval successivo. Il DUTY_ON_TIME mostra il tempo totale di attività della radio per ciascun nodo.*

## Polling

Il polling è il terzo approccio all'efficienza energetica, usato da **Bluetooth** e **IEEE 802.15.4** (in combinazione con la sincronizzazione). Richiede un'**organizzazione asimmetrica** della rete:

- Un nodo **master** trasmette periodicamente dei **beacon**.
- I nodi **slave** possono tenere la radio spenta quando vogliono, senza coordinazione.

Il meccanismo per la consegna dei messaggi verso uno slave è il seguente:

1. Se il master riceve un messaggio destinato a uno slave, lo memorizza.
2. Il master annuncia nel beacon che c'è un messaggio in attesa per quello slave.
3. Quando lo slave si sveglia, aspetta il beacon, riconosce il pending message, e invia una richiesta esplicita al master.
4. Il master consegna il frame.

> [!note] Nota
>
> Il polling è intrinsecamente compatibile con la sincronizzazione: i beacon del master possono servire anche da segnale di sincronizzazione per i nodi slave. IEEE 802.15.4 usa esattamente questa combinazione nella sua modalità con beacon.

---

## Domande d'esame

> [!question] Possibili domande d'esame
>
> - Qual è il tradeoff fondamentale nei protocolli MAC per IoT e come i tre approcci (sincronizzazione, preamble sampling, polling) lo affrontano diversamente?
> - In S-MAC, perché la latenza in percorsi multi-hop può essere elevata? In quale condizione si riduce?
> - Perché in B-MAC il preambolo deve essere più lungo del periodo di sleep del ricevitore?
> - In B-MAC, calcola il duty cycle del preamble sampling se $t_{check} = 4 \times 10^{-4}$ s e la frequenza di campionamento è 5 Hz: $DC_{check} = f_c \times t_{check} = 5 \times 4 \times 10^{-4} = 2 \times 10^{-3} = 0.2\%$.
> - Come X-MAC riduce il costo energetico del preambolo rispetto a B-MAC?
> - In BoX-MAC il preambolo è un frame dati ripetuto: quali vantaggi porta in termini di latenza e overhead?
> - Descrivi il meccanismo di polling in IEEE 802.15.4: cosa fa il master quando riceve un messaggio per uno slave?
