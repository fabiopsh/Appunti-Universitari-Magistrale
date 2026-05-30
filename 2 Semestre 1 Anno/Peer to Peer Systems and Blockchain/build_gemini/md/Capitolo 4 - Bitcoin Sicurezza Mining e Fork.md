# Capitolo 4 - Bitcoin: Sicurezza, Mining e Fork

## Consenso Tradizionale vs Consenso di Nakamoto

Gli algoritmi di consenso classici — Paxos, Raft, PBFT — sono progettati per ambienti **chiusi**: i nodi sono noti in anticipo, ciascuno conosce l'identità degli altri e i canali di comunicazione sono autenticati. Funzionano bene per database distribuiti, state machine replication, sincronizzazione di orologi.

Le blockchain permissionless come Bitcoin operano in un contesto radicalmente diverso: nodi anonimi, churn elevato, nessun canale autenticato, nessuna sincronizzazione degli orologi, nessuna lista di partecipanti. I protocolli tradizionali semplicemente non si applicano.

> [!definition] Consenso di Nakamoto
>
> Un approccio "implicito" al consenso: nessuna votazione, nessuno scambio di messaggi collettivo. Garantisce *eventual consistency* — i nodi possono avere visioni temporaneamente divergenti del registro, ma alla fine convergeranno tutti sulla stessa cronologia, a patto che la maggioranza della potenza computazionale sia onesta.

Come osservato in lezione: la decentralizzazione di Bitcoin non è raggiunta con metodi puramente tecnici, ma con una combinazione di crittografia e *clever incentive engineering*.

## Il Problema del Double Spending

Senza consenso, il sistema crollerebbe immediatamente. Immaginiamo che Bob invii bitcoin ad Alice (transazione "verde"), propagata nel network. Subito dopo Bob prova a spendere gli stessi bitcoin con July (transazione "rossa"), propagata da un altro nodo. Nodi diversi riceverebbero le due transazioni in ordine diverso e i loro registri divergerebbero — impossibile capire quale sia quella valida.

La **MemPool** (*Memory Pool*) è la "sala d'attesa" in RAM di ogni nodo: contiene le transazioni ricevute ma non ancora incluse in un blocco. È importante sottolineare che la MemPool **non è l'UTXO set**: quest'ultimo contiene le transazioni già confermate nella blockchain, mentre la MemPool è un buffer temporaneo di transazioni in attesa di conferma. Funziona come una *clearing house*: quando un nodo riceve una transazione in conflitto con una già presente nella sua MemPool, la scarta immediatamente. Ma questo risolve solo il problema locale — il consenso globale richiede qualcosa di più.

## Mining: la Lotteria della Blockchain

I nodi competono per estrarre transazioni dalla propria MemPool e aggiungerle al registro. Questa competizione è il **mining**: una lotteria in cui il vincitore ha il diritto di proporre il blocco successivo e lo trasmette in broadcast alla rete.

Quando un nodo riceve un nuovo blocco valido, elimina dalla propria MemPool tutte le transazioni ora confermate e quelle in conflitto — garantendo che il double spending tentato da Bob venga neutralizzato.

### Anatomia di un Blocco

Il miner riempie un **blocco candidato** con transazioni dalla MemPool, poi costruisce il **Block Header**: un riassunto compatto dei metadati (circa 1000 volte più piccolo della lista delle transazioni).

| Campo | Dimensione | Descrizione |
|---|---|---|
| **Magic Number** | 4 byte | Identificatore costante della rete Bitcoin |
| **Block Size** | 4 byte | Dimensione totale del blocco |
| **Version** | 4 byte | Versione del protocollo; gestisce soft/hard fork |
| **Previous Block Hash** | 32 byte | Hash SHA-256 dell'header del blocco precedente — il "link" crittografico della catena |
| **Merkle Root** | 32 byte | Radice del Merkle Tree delle transazioni; qualsiasi modifica a una transazione altera questo valore |
| **Timestamp** | 4 byte | Secondi Unix dalla mezzanotte del 1 gen 1970; usato per calibrare la difficoltà |
| **Difficulty Target** | 4 byte | Soglia al di sotto della quale deve cadere l'hash del blocco |
| **Nonce** | 4 byte | Il valore che il miner modifica iterativamente per trovare la soluzione |
| **Transaction Counter** | 1–9 byte | Numero di transazioni nel blocco |
| **Transactions List** | Variabile (fino a 1 MB) | L'elenco effettivo delle transazioni |

Perché raggruppare in blocchi e non minare singole transazioni? Una catena di hash su blocchi è molto più corta di una su milioni di transazioni, rendendo la verifica esponenzialmente più rapida. Blocchi più grandi significano anche trasmissioni di rete più efficienti.

## Proof of Work: Meccanica e Complessità

> [!definition] Proof of Work
>
> Funzione $F_d(c, x) \to \{\text{true, false}\}$ dove $d$ è la difficoltà, $c$ è la challenge (l'header del blocco senza il nonce) e $x$ è il **nonce** da trovare. Calcolare $F_d$ con $x$ noto è rapido; trovare $x$ tale che il risultato sia "true" è computazionalmente difficile.

Il procedimento del miner:

1. Imposta il nonce a 0
2. Calcola `SHA256(SHA256(Block-Header + Nonce))`
3. Se l'hash è **inferiore al Target** → blocco valido, trasmetti
4. Altrimenti, incrementa il nonce di 1 e ripeti

Ogni singolo bit dell'hash a 256 bit è indipendente dagli altri — come il lancio di una moneta. Non esistono scorciatoie: l'unico metodo è la forza bruta. La probabilità che un hash casuale cada sotto la soglia $T$ è:

$$p = \frac{T + 1}{2^{256}}$$

Il numero medio di tentativi per trovare un hash valido è $1/p$. Al 1° gennaio 2017, questo valore era circa $2^{70}$.

> [!tip] Gli "zeri iniziali" sono una semplificazione
>
> Spesso si dice che la PoW è risolta quando l'hash inizia con un certo numero di zeri. È una buona approssimazione, ma non precisa: il target può abbassarsi senza cambiare il numero di zeri (es. da `001001` a `001000` — stessi due zeri, target più basso). La soglia effettiva è numerica, non basata sui caratteri.

L'idea di usare puzzle crittografici costosi da risolvere ma facili da verificare non è nuova: sistemi simili erano stati proposti per mitigare DoS e spam email (richiedendo cicli CPU invece di denaro per "affrancare" ogni messaggio). Nakamoto l'ha adattata al consenso distribuito.

> [!tip] La metafora dei dardi
>
> La PoW può essere immaginata come il lancio di freccette verso un bersaglio con gli occhi bendati. Ogni lancio ha uguale probabilità di colpire qualsiasi punto del bersaglio. La difficoltà è inversamente proporzionale alla dimensione del cerchio verde (la zona valida): più il cerchio è piccolo, più è difficile colpirlo. Se i giocatori diventano più bravi (hardware più veloce), si restringe il cerchio — si abbassa il target. Aggiungere uno zero al prefisso richiesto raddoppia in media lo sforzo computazionale; rimuoverne uno lo dimezza.

### PoW: Applicazioni Precedenti a Bitcoin

La Proof of Work come strumento generale ha storia propria, ben prima di Nakamoto. Il suo principio è semplice: un meccanismo che consente a una parte di *dimostrare* a un'altra di aver impiegato una certa quantità di risorse computazionali, dove la verifica richiede molto meno tempo dell'esecuzione.

**Contrasto agli attacchi DoS** — Si può condizionare l'accesso a un servizio alla risoluzione di un puzzle computazionalmente costoso. Questo throttle le richieste: chi vuole inondare il server deve pagare un costo CPU per ogni tentativo, rendendo l'attacco proibitivo su larga scala.

**Contrasto allo spam email** — L'idea è affrancare ogni messaggio non con denaro ma con cicli CPU: chi invia poche email non sente quasi il costo, perché il puzzle viene eseguito poche volte. Per uno spammer che invia centinaia di migliaia di messaggi al giorno, lo stesso puzzle moltiplicato per milioni di invii diventa proibitivamente costoso. Il costo computazionale funge da "francobollo" digitale.

## Resistenza agli Attacchi Sybil

Ad ogni round, il miner che risolve la PoW viene eletto implicitamente come leader. L'elezione è proporzionale alla **potenza computazionale**, una risorsa fisica difficile da monopolizzare — non al numero di identità di rete. Creare migliaia di identità false non dà alcun vantaggio: conta solo quanti hash al secondo si riesce a calcolare. Per sabotare il sistema bisognerebbe controllare almeno il 51% della potenza di hashing globale.

## Incentivi per i Miner

Validare blocchi costa enormi quantità di energia. Perché farlo onestamente?

**Block Reward** — La prima transazione di ogni blocco è la **Coinbase Transaction**: crea bitcoin "dal nulla" e li assegna al miner. È l'unico meccanismo per immettere nuovi BTC nel sistema. La supply totale è fissa a **21.000.000 BTC** (raggiunta circa nel 2140), il che rende Bitcoin strutturalmente resistente all'inflazione — impossibile "stampare" nuova moneta per decisione politica. Questo implica una proprietà che non esiste in alcuna valuta fiat: chi possiede 1 BTC possiede sempre almeno un ventunomilionesimo dell'intera supply globale. Nelle valute tradizionali, i governi e le banche centrali possono aumentare l'offerta per decisioni politiche, diluendo il valore di chi già possiede quella valuta.

La ricompensa si dimezza ogni 210.000 blocchi (~4 anni): è il celebre **Halving**.

| Era | Periodo | Block Reward |
|---|---|---|
| 1 | 2009 | 50 BTC |
| 2 | 2012 | 25 BTC |
| 3 | 2016 | 12,5 BTC |
| 4 | 2020 | 6,25 BTC |
| 5 | 2024 (attuale) | 3,125 BTC |
| … | … fino all'Era 33 | 1 Satoshi ($10^{-8}$ BTC) |

**Transaction Fees** — La differenza tra $\sum \text{inputs}$ e $\sum \text{outputs}$ di ogni transazione va al miner. Gli utenti le impostano volontariamente per ottenere priorità di inclusione. Con il susseguirsi degli halving, le fee costituiranno una percentuale sempre maggiore dei ricavi dei miner.

La Coinbase Transaction contiene anche un input "fittizio" usato per messaggi personalizzati. Nel Genesis Block, Nakamoto vi nascose: *"The Times 03/Jan/2009: Chancellor on brink of second bailout for banks"*.

> [!note] Struttura dell'output della Coinbase
>
> L'output della Coinbase Transaction è inviato a uno o più indirizzi Bitcoin del miner stesso. Il valore corrisponde alla somma della block reward più le fee di tutte le transazioni incluse nel blocco. È il miner a decidere a quali propri indirizzi destinare la ricompensa.

### Dinamiche a Lungo Termine dei Ricavi

Storicamente la componente dominante dei ricavi dei miner è stata il block reward; le transaction fee rappresentano solo una piccola percentuale. Questa situazione è però destinata a cambiare: man mano che gli halving si succedono e la block reward si avvicina a zero, le fee diventeranno la fonte quasi esclusiva di compensazione.

C'è però una tensione strutturale: ogni nuovo miner che entra nella rete abbassa la probabilità di ricompensa degli altri. Per mantenere competitive le proprie probabilità, ogni miner è incentivato ad aumentare continuamente il proprio hash rate, alimentando una corsa agli armamenti computazionale. Questa dinamica ha spinto i miner a organizzarsi in **mining pool** — discusse più avanti in questo capitolo.

## Regolazione Automatica della Difficoltà

Il sistema è calibrato per produrre **un blocco ogni 10 minuti**. Questo intervallo non è casuale: deve essere molto più lungo del tempo di propagazione del blocco sulla rete, affinché tutti i miner lavorino sulla stessa catena senza sprecare energia su rami obsoleti. Nelle parole di Nakamoto stesso: *"We want blocks to usually propagate in much less time than it takes to generate them, otherwise nodes would spend too much time working on obsolete blocks."* Se i blocchi vengono minati troppo frequentemente, i miner costruiscono catene concorrenti: solo una diventerà la più lunga, e tutti gli altri avranno sprecato energia su rami che verranno abbandonati — riducendo la sicurezza effettiva del sistema.

Ethereum ha scelto tempi più rapidi, ottenendo conferme più veloci e minore variabilità nei payout per i miner, ma al costo di più fork e un sistema di ricompensa molto più complesso.

La difficoltà si auto-regola ogni **2016 blocchi** (~2 settimane a 10 min/blocco = 20.160 minuti). Il ricalcolo avviene in modo completamente autonomo su ogni nodo:

$$\text{Nuovo Target} = \text{Vecchio Target} \times \frac{\text{Tempo effettivo}}{20.160 \text{ min}}$$

- Rete troppo veloce (es. 16.128 min) → rapporto $0{,}8$ → target si abbassa → difficoltà aumenta
- Rete troppo lenta (es. 22.176 min) → rapporto $1{,}1$ → target si alza → difficoltà diminuisce

L'aspetto più elegante: nessun coordinatore centrale. Tutti i nodi eseguono lo stesso algoritmo open-source sulle stesse informazioni e convergono autonomamente allo stesso nuovo target.

## Struttura della Blockchain e Fork

La blockchain non è una catena perfettamente lineare, ma un **albero** in cui solo il ramo più lungo è canonico.

I blocchi non hanno un indice interno: vengono identificati dal loro **Block Hash** (calcolato dinamicamente alla ricezione) o dalla **Block Height** (numero di blocchi dal Genesis Block, che ha altezza 0). L'ultimo blocco aggiunto è la *blockchain head*.

La tamper-freeness è garantita strutturalmente: modificare una transazione altera il Merkle Root, cambia l'hash del blocco, invalida il `hashprev` del blocco successivo, e innesca un effetto a cascata che obbliga a ricalcolare tutta la PoW da quel punto in poi.

### Fork Temporanei e Longest Chain Rule

La latenza di rete introduce i **fork temporanei**: due miner possono trovare un blocco valido quasi simultaneamente, puntando allo stesso genitore. La rete si divide — alcuni nodi vedono prima il blocco A, altri il blocco C, in base alla vicinanza fisica al miner che ha trovato il blocco — e due rami crescono in parallelo. Ogni miner continua a lavorare sul ramo che ha ricevuto per primo; il ramo alternativo viene conservato in una cache locale. I due fork possono crescere indipendentemente, con miner diversi che lavorano su rami diversi.

> [!definition] Longest Chain Rule (Regola di Nakamoto)
>
> I nodi considerano valida la catena che rappresenta il maggiore lavoro cumulativo (la più lunga). Non appena un nuovo blocco estende uno dei due rami rendendolo più lungo, tutti i miner abbandonano il ramo più corto e migrano sul ramo vincente. I blocchi del ramo perdente diventano **orphan blocks**; le loro transazioni non confermate tornano nella MemPool per essere eventualmente incluse in un blocco futuro.

Per questo motivo si raccomanda la **regola delle 6 conferme**: una transazione è considerata definitiva solo quando ha almeno altri 5 blocchi costruiti sopra di essa. Il valore 6 è il default, ma può essere configurato dal client in base al livello di sicurezza desiderato — transazioni di alto valore possono richiedere più conferme. Scopo della regola: dare alla rete il tempo di raggiungere un accordo sull'ordinamento dei blocchi.

### Algoritmo di Ricezione di un Blocco

Quando un nodo riceve un nuovo blocco $b$, esegue il seguente algoritmo per aggiornare la propria visione della blockchain:

```
Receive block b
  For this node the current head is block bmax at height hmax
  Connect block b in the tree as child of its parent p at height
    hb = hp + 1
  if hb > hmax then
    hmax = hb
    bmax = b
    compute UTXO for the path leading to bmax
    cleanup memory pool
  end if
```

Se il nuovo blocco è più alto della testa corrente, diventa la nuova testa. Si ricalcola l'UTXO set lungo il percorso fino alla nuova testa e si pulisce la MemPool rimuovendo le transazioni ora confermate e quelle in conflitto. Se invece il blocco appartiene a un fork più corto, viene conservato in cache senza diventare la testa.

### Teorema del Consenso di Nakamoto

> [!theorem] Eventual Consistency
>
> I fork vengono risolti e tutti i nodi concordano alla fine su quale sia la blockchain più lunga. Il sistema garantisce *eventual consistency*.
>
> **Proof sketch**: affinché un fork continui a esistere, devono essere trovati blocchi quasi simultaneamente su entrambi i rami, estendendoli in parallelo. La probabilità che questo accada ripetutamente decresce esponenzialmente con la lunghezza del fork. Quindi esisterà sempre un momento in cui un solo ramo viene esteso, diventando la catena più lunga e imponendosi come quella canonica.

Fork prolungati — due catene che crescono in parallelo a lungo — sono matematicamente possibili ma estremamente improbabili: la componente aleatoria del mining e i ritardi di propagazione introducono sufficiente rumore da impedire una crescita perfettamente sincrona dei due rami.

## Sicurezza: Attacchi e Vulnerabilità

Il sistema Bitcoin si articola su quattro livelli — **Blockchain Design**, **P2P Architecture**, **Consensus** e **Transactions** — ognuno soggetto ad attacchi specifici. La rete P2P affronta l'Eclipse Attack e l'Approx. Bitcoin Mining; il consenso subisce il 51% Attack e il Selfish Mining; le transazioni fronteggiano il Double Spending e il Malleability Attack. La sicurezza è analizzata tramite modelli formali come Random Oracle, Nakamoto's Model e Bitcoin Backbone.

### Double Spending e Attacco del 51%

Il **Double Spending Attack** consiste nel tentare di spendere lo stesso bitcoin due volte verso due destinatari diversi. L'approccio ingenuo — trasmettere entrambe le transazioni alla rete — fallisce: finiscono entrambe nella MemPool, ma un minatore onesto ne includerà solo una nel blocco successivo, scartando la seconda. Se due minatori le validano contemporaneamente generando un fork temporaneo, la Longest Chain Rule ne renderà valida solo una — motivo per cui si attendono solitamente 6 conferme.

L'attacco diventa pericoloso in modalità **stealth**. Il minatore malevolo:
1. Spende bitcoin sulla catena pubblica per acquistare un bene (es. una barca)
2. Mina in segreto una catena privata omettendo quella transazione — mantenendo il controllo dei bitcoin
3. Quando la catena privata supera quella pubblica, la trasmette alla rete
4. Per la Longest Chain Rule, la rete adotta la nuova catena: l'attaccante riottiene i fondi e mantiene il bene

![Schema dell'attacco stealth di Double Spending (51% Attack).](images/Pasted-image-20260319164820.png)

Perché l'attacco riesca con regolarità, il minatore deve detenere oltre il **50% dell'hashing power** — da qui il nome "51% Attack".

> [!note] Il caso GHash.IO (2014)
>
> La mining pool GHash.IO raggiunse quasi il 50% della potenza di calcolo (38,24%), scatenando il panico nella community. Non subì alcun attacco: per chi detiene tanto potere è economicamente più conveniente continuare a minare e incassare i block reward che distruggere il network per annullare una singola transazione.

### Attacco Denial of Service

Se un minatore rifiuta di processare le transazioni di un utente sgradito, quest'ultimo subisce solo un ritardo. La transazione resta nella MemPool finché qualsiasi altro nodo onesto non propone un blocco che la include. Non esiste un meccanismo efficace per censurare permanentemente una transazione in una rete con sufficienti nodi onesti.

## Attori del Network

| Tipo di nodo | Wallet | Mining | Blockchain completa | Routing P2P |
|---|---|---|---|---|
| **Reference Client (Bitcoin Core)** | Sì | Sì | Sì | Sì |
| **Full Node** | No | No | Sì | Sì |
| **Solo Miner** | No | Sì | Sì | Sì |
| **Lightweight / SPV Wallet** | Sì | No | No | Sì |

## L'Evoluzione del Mining

Il mining consiste nell'eseguire SHA-256 in loop variando il nonce fino a ottenere un hash inferiore al target. Il ciclo centrale è concettualmente semplice:

```
while (1)
    HDR[kNoncePos]++;
    if (SHA256(SHA256(HDR)) < (65535 << 208) / DIFFICULTY)
        return;
```

L'hardware su cui gira questo loop si è evoluto in quattro generazioni, con guadagni di efficienza enormi ad ogni salto:

| Generazione | Periodo | Caratteristiche | Tempo medio per un blocco |
|---|---|---|---|
| **CPU** | 2009 | Elaborazione sequenziale su core generici | ~139.461 anni (2015, singolo PC) |
| **GPU** | 2010+ | Alto parallelismo via OpenCL; overclocking diffuso | ~300 anni (100 GPU) |
| **FPGA** | 2011+ | Schede programmabili via Verilog; ottime per operazioni bitwise | ~25 anni |
| **ASIC** | 2013+ | Chip dedicati esclusivamente a SHA-256 (es. TerraMiner 4: 2 TH/s a $3.500) | Secondi/minuti |

### Solo Mining vs Mining Pool

Il **solo mining** segue una distribuzione di Poisson con alta varianza: nel 2014, con 1700 GH/s, l'attesa media per un blocco era oltre 3 anni. Si accumula stress e spese senza entrate garantite.

La deviazione standard è alta per costruzione: se in un mese ci si aspetta di trovare 4 blocchi, la deviazione standard è $\sqrt{4} = 2$. Significa che alcuni mesi se ne trovano 6, altri 2, altri 0. Oltre all'incertezza economica, il solo mining introduce un problema di fiducia: il miner non può verificare in modo indipendente se il proprio hardware funzioni correttamente, né se gli altri miner stiano barando per ottenere una quota sproporzionata dei premi — e in effetti i miner *possono* imbrogliarsi a vicenda. Questo è uno dei motivi principali che ha spinto verso le mining pool.

Le **Mining Pool** aggregano i minatori riducendo la varianza in cambio di entrate più piccole ma costanti. Un *Pool Manager* centrale distribuisce il lavoro, raccoglie le soluzioni e redistribuisce i premi trattenendo una fee. Per verificare che i minatori stiano davvero lavorando, questi inviano **shares**: blocchi "quasi validi" con una difficoltà ridotta rispetto alla rete, che fungono da prova probabilistica del lavoro svolto.

#### Metodi di Pagamento nelle Pool

La scelta del metodo di pagamento è il cuore del rapporto economico tra pool e miner: determina chi si fa carico del rischio della varianza e come viene scoraggiato il comportamento opportunistico. Esistono tre schemi principali, con varianti ibride usate dalle pool moderne.

**Pay Per Share (PPS) e FPPS**

Nel modello **PPS** (*Pay Per Share*), il miner viene pagato per ogni share valida inviata, indipendentemente dal fatto che la pool trovi effettivamente un blocco. Il pagamento è deterministico: se la difficoltà della rete è $D$ e la difficoltà delle share è $d$, ogni share vale esattamente $\frac{d}{D} \cdot \text{block\_reward}$. La pool si assume interamente il rischio della varianza — in settimane sfortuna, pagherà i miner anche senza ricavare premi.

**FPPS** (*Fully Pay Per Share*) è la variante estesa: oltre al block reward, include nella quota per share anche le **transaction fees** del blocco (che in PPS puro vengono spesso trattenute dall'operatore). FPPS è quindi più generoso per il miner ma richiede una fee operativa più alta.

> [!warning] Incentivo perverso del PPS
>
> Poiché il miner viene pagato a prescindere, non ha alcun incentivo a trasmettere immediatamente un blocco valido trovato — potrebbe teoricamente scartarlo per massimizzare le proprie share senza contribuire alla catena. Nella pratica questo comportamento è raro perché degenera nella loss di reputazione e nella rimozione dalla pool.

**Pay Per Last N Shares (PPLNS)**

Nel modello **PPLNS**, la ricompensa viene distribuita solo quando la pool trova un blocco, e viene ripartita in proporzione alle share che ciascun miner ha inviato nell'ultima finestra di $N$ share. Il parametro $N$ è scelto dall'operatore: una finestra piccola premia i miner più recenti; una finestra grande diluisce il contributo nel tempo.

L'effetto principale è che il miner si espone alla stessa varianza della pool: se la pool trova molti blocchi in rapida successione, guadagna molto; se è sfortunata, guadagna poco. In compenso, la fee è bassa perché l'operatore non anticipa pagamenti.

> [!tip] PPLNS scoraggia il pool hopping
>
> Il **pool hopping** è la strategia di un miner opportunista che si unisce a una pool all'inizio di un round (quando le share accumulate sono poche e la sua quota relativa è alta) per poi passare a un'altra pool verso la fine. Con PPLNS la finestra scorrente penalizza chi entra tardi o è intermittente: le sue share recenti hanno peso minore rispetto a chi contribuisce stabilmente. Questo rende PPLNS resistente al pool hopping.

**Pay Proportional**

Nel modello **proporzionale**, la ricompensa di ogni blocco trovato viene divisa tra i miner in proporzione alle share inviate *durante quel round* (cioè dall'ultimo blocco trovato dalla pool al blocco corrente). A differenza di PPLNS non c'è finestra scorrevole: si azzera ad ogni blocco.

Questo schema è vulnerabile al pool hopping in modo ancora più diretto: un miner che entra a inizio round (quando poche share sono state accumulate) ha una quota percentuale molto alta. Man mano che il round si allunga, nuovi miner entrano e la quota si diluisce — conviene quindi abbandonare i round lunghi. Per questo motivo il Pay Proportional puro è stato quasi completamente abbandonato in favore di PPLNS.

**Confronto riassuntivo**

| Metodo | Chi porta il rischio varianza | Vulnerabile al pool hopping | Fee tipica | Transaction fees incluse |
|---|---|---|---|---|
| **PPS** | Operatore della pool | No | Alta | No |
| **FPPS** | Operatore della pool | No | Alta | Sì |
| **PPLNS** | Il miner | Parzialmente (finestra scorrevole lo riduce) | Bassa | Dipende dalla pool |
| **Pay Proportional** | Il miner | Sì (molto vulnerabile) | Bassa | Dipende dalla pool |

> [!warning] Mining Pool Decentralizzate (es. P2Pool, dal 2011)
>
> Non richiedono un operatore fidato. I miner costruiscono in parallelo una **sharechain** — una blockchain privata con difficoltà ridotta (~un blocco ogni 30 secondi) — agganciata all'ultimo blocco Bitcoin. Ogni share è scritta sulla sharechain e registra la quota di ricompensa spettante. Quando si trova un blocco Bitcoin valido, i pagamenti vengono processati sulla rete principale tramite *merge mining*. L'auditability totale impedisce truffe interne.

### Top Mining Pool (2025)

| Pool | Fee | Hashrate | Metodo |
|---|---|---|---|
| Foundry USA | 2% PPLNS / 4% PPS | 231,5 EH/s | FPPS |
| BTC.com | 1,38% | 161,44 EH/s | Advanced FPPS |
| Antpool | 0% PPLNS / 4% PPS+ | 30,5 EH/s | PPLNS, PPS+ |
| F2Pool | 2,5% | 25,81 EH/s | PPS+ |
| Binance | 2,5% | 23,86 EH/s | FPPS, PPS+, PPS |
| Poolin | 2,5% | 23,59 EH/s | FPPS |
| ViaBTC | 2% PPLNS / 4% PPS | 20,32 EH/s | PPLNS, PPS |

Le pool sono nate nel 2010 (era GPU) e già nel 2014 raccoglievano il 90% dell'hashrate globale. I protocolli standardizzati odierni facilitano lo spostamento dei miner tra pool diverse.

## Hard e Soft Fork in Bitcoin

Un **fork** è, in senso generale, una modifica al protocollo e alle strutture dati di una rete blockchain. Nel mondo del software tradizionale si parla semplicemente di aggiornamenti; nel contesto delle criptovalute questi aggiornamenti assumono un nome e una rilevanza speciale, perché non avvengono su un sistema centralizzato ma su una rete distribuita di nodi che devono raggiungere il consenso sulle regole del gioco. I fork possono essere motivati dall'introduzione di nuove funzionalità, dalla correzione di vulnerabilità di sicurezza, dall'affrontare problemi di scalabilità, o dalla necessità di risolvere disaccordi profondi all'interno della comunità di sviluppatori e miner.

### Protocol Fork vs Chain Fork

È fondamentale distinguere due fenomeni che vengono entrambi chiamati "fork" ma hanno natura molto diversa.

Un **protocol fork** (*fork di protocollo*) nasce da un cambiamento deliberato nelle regole di consenso. È un aggiornamento intenzionale e coordinato: alcuni nodi adottano le nuove regole, altri no. Se i nodi seguono regole incompatibili, si crea una divisione permanente della blockchain in due catene separate, ognuna con la propria storia futura e i propri asset. I protocol fork si distinguono in due categorie — **soft fork** (compatibile con le versioni precedenti) e **hard fork** (non compatibile).

Un **chain fork** (*fork di catena*) è invece un fenomeno temporaneo e fisiologico. Accade quando due miner trovano un blocco valido quasi contemporaneamente, oppure a causa della latenza di rete o di un attacco (come discusso precedentemente per i fork temporanei). Si creano così più blocchi validi alla stessa altezza. La rete risolve l'ambiguità applicando la **longest chain rule** (la regola della catena con più lavoro cumulativo): uno dei rami diventa orfano e i suoi blocchi vengono scartati. Non cambia nessuna regola, non nasce nessun nuovo asset. È un evento normale nell'operatività quotidiana di Bitcoin.

![Hard fork vs soft fork a confronto: il primo divide la rete in due catene separate, il secondo mantiene la rete unita con regole più restrittive.](images/lezione-18-hard-and-soft-forks-in-bitcoin-img-01.jpg)

> [!tip] Intuizione chiave
>
> La distinzione chiave è: il protocol fork cambia le regole, il chain fork è una gara temporanea tra blocchi validi che si risolve automaticamente. Solo il primo può generare una divisione permanente della blockchain.

### Soft Fork

> [!definition] Soft Fork
>
> Un soft fork è una modifica all'implementazione di una blockchain che è **backward compatible** (retrocompatibile): i nodi non aggiornati possono continuare a interagire con quelli aggiornati. In generale, un soft fork introduce regole più restrittive rispetto a quelle precedenti.

L'esempio classico è la riduzione della dimensione massima dei blocchi: un nodo non aggiornato, programmato per accettare blocchi fino a 2 MB, accetterà senza problemi blocchi da 1 MB prodotti dai nodi aggiornati. Il vincolo nuovo è un sottoinsieme dei vincoli vecchi.

#### Accettazione del Fork

Il meccanismo con cui un soft fork viene adottato è simile a un **voto distribuito**. Quando gli sviluppatori propongono un aggiornamento, stabiliscono una data futura per la sua attivazione. Nel frattempo, i miner possono segnalare il proprio supporto codificando un numero di versione aggiornato nei blocchi che minano. Gli altri nodi della rete osservano quante versioni aggiornate circolano e possono stimare quanta potenza di hashing ha già adottato il cambiamento.

Il processo funziona così: i miner consapevoli delle nuove regole segnalano supporto tramite i **version bits**, ma non le applicano ancora. Le nuove regole diventano attive solo quando la soglia di approvazione viene raggiunta. Il famoso BIP66 del 2015 — che modificava il formato delle firme digitali — ottenne il 95% della potenza di hashing prima di essere attivato.

> [!note] BIP (Bitcoin Improvement Proposal)
>
> I BIP sono il meccanismo formale attraverso cui vengono proposte modifiche al protocollo Bitcoin. Chiunque può aprire un BIP; la sua adozione dipende dall'accordo della comunità e dei miner.

#### Come Muore la Vecchia Versione

Dopo un soft fork, se la maggioranza della potenza di hashing adotta le nuove regole, la versione legacy sparisce gradualmente. Il motivo è puramente economico: i blocchi prodotti dai nodi non aggiornati vengono rifiutati dalla maggioranza dei nodi aggiornati. I miner non vogliono sprecare potenza computazionale producendo blocchi che la rete scarterà, quindi migrano alla nuova versione per continuare a ricevere ricompense.

![Come la vecchia versione muore: i blocchi dei nodi non aggiornati vengono rifiutati dalla catena dominante. I miner seguono "the chain that pays".](images/lezione-18-hard-and-soft-forks-in-bitcoin-img-02.jpg)

I possibili esiti di un soft fork sono tre: tutti i miner accettano e il fork è semplicemente un aggiornamento software; la maggioranza accetta, la nuova versione si consolida e quella vecchia muore gradualmente; la maggioranza rifiuta e il fork non sopravvive.

#### I Principali Soft Fork di Bitcoin

Prima di analizzare SegWit e Taproot nel dettaglio, è utile avere una visione d'insieme dei soft fork che hanno caratterizzato la storia di Bitcoin.

![Timeline dei soft fork principali di Bitcoin: da P2SH (2012) per il multisig, a SegWit (2017) per la scalabilità, fino a Taproot (2021) per la privacy.](images/lezione-18-hard-and-soft-forks-in-bitcoin-img-03.jpg)

### SegWit — Agosto 2017

**SegWit** (*Segregated Witness*, testimone segregato) è il più importante soft fork della storia di Bitcoin, attivato nell'agosto 2017. Per capire cosa ha cambiato, è necessario partire dal problema che risolveva.

#### Il Problema: Transaction Malleability

Prima di SegWit, una transazione Bitcoin conteneva tre componenti principali: gli **input** (da dove provengono i bitcoin), gli **output** (dove vanno), e le **firme** (la prova che il mittente ha autorizzato la transazione). Le firme erano incluse nei dati della transazione stessa. Questo creava una vulnerabilità nota come **transaction malleability** (*malleabilità delle transazioni*): permetteva di alterare il **TXID** (identificativo) di una transazione senza modificarne gli effetti reali — mittente, destinatario e importo restavano invariati, ma l'ID cambiava. Come se il numero di tracking di un pacco venisse sostituito in transito.

La vulnerabilità era nell'algoritmo **ECDSA**: una firma è una coppia $(r, s)$, ma se $(r, s)$ è valida lo è anche $(r, n-s)$, dove $n$ è una costante della curva. Poiché il TXID è l'hash SHA-256 dell'intera transazione (inclusa la firma nello ScriptSig), cambiare la rappresentazione in $(r, n-s)$ modifica il TXID senza invalidare la firma logica.

Lo schema di attacco funziona così: Alice invia 50 BTC a Bob, generando una transazione con TXID = 1234. Bob intercetta la transazione, ne crea una copia con la firma modificata in $(r, n-s)$ — stessi input, stesso output, stessa firma logicamente valida, ma TXID diverso (es. 4567). Ora c'è una gara: entrambe le transazioni finiscono nella MemPool. Il momento in cui una viene confermata, l'altra viene scartata come duplicato. Se viene confermata quella di Bob (TXID 4567), Alice non trova mai il suo TXID originale (1234) sulla blockchain — e Bob sostiene di non aver ricevuto nulla, costringendola a un secondo pagamento.

> [!note] Il fallimento di Mt. Gox (2013–2014)
>
> Mt. Gox gestiva il 72% delle transazioni Bitcoin mondiali. Ad aprile 2014 dichiarò bancarotta, avendo perso ~744.408 BTC (il 6% dell'offerta totale, ~450 milioni di dollari dell'epoca). Mt. Gox non usava codifiche di firma standard: alcuni utenti le "standardizzavano" applicando la reverse malleability, ispirando gli hacker. Gli attaccanti prelevavano fondi, alteravano il TXID in transito, ricevevano i fondi e — poiché l'exchange non vedeva l'ID originale — rieffettuavano il prelievo.

Il txid cambiato rendeva inoltre impossibile per altri protocolli — come la Lightning Network — fare riferimento in modo affidabile a una transazione non ancora confermata.

#### La Soluzione: Separare la Firma dai Dati

SegWit risolve il problema spostando i dati delle firme fuori dalla struttura principale della transazione, in una sezione separata chiamata **Witness** (*testimone*). Poiché il txid viene ora calcolato senza i dati della firma, non può più essere alterato dopo che la transazione è stata firmata.

![Confronto strutturale: nel blocco Pre-SegWit le firme sono embedded nella transazione; nel blocco SegWit la Witness Data è segregata e non influisce sul calcolo del txid.](images/lezione-18-hard-and-soft-forks-in-bitcoin-img-04.jpg)

I benefici sono: eliminazione della manipolazione del txid, transazioni non confermate più sicure, e l'abilitazione della Lightning Network.

> [!warning] SegWit è davvero un soft fork?
>
> Apparentemente SegWit sembrerebbe incompatibile con i nodi vecchi, ma gli sviluppatori hanno usato un "trucco": le firme vengono spostate fuori dalla parte che i nodi vecchi contano per il calcolo del peso del blocco. I vecchi nodi non analizzano il Witness, vedono blocchi ≤ 1 MB e non violano nessuna regola. Accettano i nuovi blocchi senza sapere che contengono dati Witness.

#### Block Weight e Aumento della Capacità

Anche se non era l'obiettivo primario, SegWit ha aumentato de facto la capacità di transazione. Prima di SegWit i blocchi erano limitati a 1 MB. SegWit introduce il concetto di **block weight** (*peso del blocco*): i byte normali di una transazione contano 4 unità di peso ciascuno, mentre i byte del Witness contano solo 1 unità di peso. Il limite massimo è 4 milioni di unità di peso. Questo significa che blocchi con molte transazioni SegWit possono contenere più dati totali, pur rimanendo entro il limite di peso — effettivamente aumentando il throughput.

![In un blocco SegWit la Witness Area (tratteggiata) contiene le firme a peso ridotto. La base data rimane ≤ 1 MB per i vecchi nodi, ma il blocco reale può superarla.](images/lezione-18-hard-and-soft-forks-in-bitcoin-img-05.jpg)

#### SegWit: Ricapitolazione

Il diagramma seguente riassume in modo completo il funzionamento di SegWit, evidenziando come i vecchi nodi vedano solo la parte base del blocco (≤ 1 MB) e ignorino la witness, mantenendo la retrocompatibilità.

![Ricapitolazione SegWit: il blocco legacy ha firme inline; il blocco SegWit le separa nel Witness. I vecchi nodi vedono solo la base data e rimangono sincronizzati.](images/lezione-18-hard-and-soft-forks-in-bitcoin-img-06.jpg)

### Taproot — Novembre 2021

**Taproot** è il secondo grande soft fork di Bitcoin, attivato il 14 novembre 2021 con il supporto di oltre il 90% dei miner. Si basa su due tecniche crittografiche: le **Schnorr Signatures** e il **MAST** (*Merkelized Abstract Syntax Tree*). L'obiettivo è migliorare sia le capacità di scripting che la privacy della rete Bitcoin.

#### Schnorr Signatures

> [!definition] Schnorr Signatures (Firme di Schnorr)
>
> Schema di firma digitale basato sul problema del logaritmo discreto. Alternativa alle firme ECDSA usate da Bitcoin, con proprietà crittografiche superiori.

Le Schnorr Signatures hanno cinque proprietà fondamentali:

**Privacy**: non è possibile distinguere firme individuali in un gruppo aggregato.

**Linearità**: consentono un metodo semplice ed efficiente per far sì che più parti collaboranti producano una firma valida per la somma delle loro chiavi pubbliche. Questo è il fondamento del **key aggregation** (*aggregazione di chiavi*) — più firmatari possono produrre una singola firma collettiva indistinguibile da quella di un singolo firmatario.

**Batch verification** (*verifica in batch*): con ECDSA, verificare tre firme richiede tre operazioni separate. Con Schnorr è possibile verificare tutte e tre insieme in una sola operazione: $\text{Ver}(\sigma_1 + \sigma_2 + \sigma_3) = 1\ \text{operazione}$, contro $\text{Ver}(\sigma_1) + \text{Ver}(\sigma_2) + \text{Ver}(\sigma_3) = 3\ \text{operazioni}$ con ECDSA.

**Non malleabilità**: le firme non possono essere modificate.

**Sicurezza dimostrabile**: la sicurezza è riducibile formalmente al problema del logaritmo discreto.

![Key aggregation con Schnorr: P1, P2, P3 combinano chiavi e firme in un'unica $P_{agg}$ e $S_{agg}$. La verifica è identica a quella di un firmatario singolo.](images/lezione-18-hard-and-soft-forks-in-bitcoin-img-07.jpg)

Le Schnorr Signatures producono una singola chiave pubblica e una singola firma, anche quando più firmatari cooperano. Il processo richiede cooperazione interattiva tra i firmatari, incluso lo scambio di chiavi pubbliche e la coordinazione del processo di firma.

#### MAST — Merkelized Abstract Syntax Tree

> [!definition] MAST (Merkelized Abstract Syntax Tree)
>
> Struttura dati che combina un **Abstract Syntax Tree** (AST) con un **Merkle Tree** per rappresentare condizioni di spesa multiple in modo efficiente e privato.

Il problema che MAST risolve è il seguente: uno script Bitcoin può prevedere molteplici condizioni di spesa alternative. Senza MAST, tutte le condizioni devono essere incluse nella transazione quando si spende, rivelando tutte le clausole anche quelle non usate. MAST permette di includere nella transazione solo la condizione effettivamente eseguita, insieme alla Merkle proof che dimostra che quella condizione era nel set originale.

**La Parte AST**

L'**Abstract Syntax Tree** specifica come suddividere la logica di spesa in foglie. Le condizioni in relazione OR diventano foglie separate — se basta soddisfarne una, non ha senso includerle tutte. Le condizioni in relazione AND rimangono nella stessa foglia, perché devono essere soddisfatte insieme.

![Da AST a MAST: le condizioni OR (2-of-3 Multisig, Timelock) diventano foglie separate; le condizioni AND (Timelock AND Hash Preimage) rimangono nella stessa foglia.](images/lezione-18-hard-and-soft-forks-in-bitcoin-img-08.jpg)

**La Parte Merkle Tree**

Una volta strutturate le condizioni come foglie, si costruisce un Merkle Tree su di esse. La radice del Merkle Tree impegna crittograficamente tutte le condizioni. Quando si spende, si rivela solo la foglia usata e il percorso di verifica (Merkle proof), non le altre condizioni.

![Il Merkle Tree del MAST: ogni condizione di spesa è una foglia. La MAST ROOT impegna tutte le condizioni. Al momento della spesa si rivela solo la foglia usata + il Merkle path.](images/lezione-18-hard-and-soft-forks-in-bitcoin-img-09.jpg)

> [!example] MAST con 4 condizioni di spesa
>
> Supponiamo di avere:
> - Script 1: multisig 2-di-3 (Alice, Bob, Charlie)
> - Script 2: timelock di 1 anno
> - Script 3: hash preimage
> - Script 4: firma singola di Alice
>
> **Senza MAST**: tutti e 4 gli script sono inclusi nella transazione, rivelando tutte le clausole.
>
> **Con MAST**: solo lo script eseguito + la Merkle proof sono inclusi. Gli altri script rimangono nascosti.

#### La Tweaked Public Key

Il meccanismo con cui Taproot unisce Schnorr Signatures e MAST è la **tweaked public key** (*chiave pubblica modificata*). Si parte da:
- una chiave pubblica $P$ (può essere singola o aggregata da più firmatari)
- la radice del Merkle tree degli script (MAST): $m$

Si calcola il **tweak** come:
$$
t = H(P \,\|\, m)
$$
dove $H$ è una funzione hash e $\|$ indica la concatenazione. Si applica poi il tweak alla chiave pubblica tramite operazione sulla curva ellittica:
$$
P' = P + t \cdot G
$$
Il risultato $P'$ è la **tweaked public key**: una nuova chiave pubblica che impegna crittograficamente sia la chiave interna $P$ che l'intero albero di script $m$.

![La tweaked key: combina la chiave pubblica originale con lo script segreto (MAST root) in un'unica chiave che appare normale on-chain ma impegna crittograficamente le condizioni di spesa.](images/lezione-18-hard-and-soft-forks-in-bitcoin-img-10.jpg)

> [!tip] Cosa viene scritto on-chain
>
> Sull'output della blockchain non viene scritta né la chiave pubblica separatamente né la radice MAST separatamente. Viene scritto solo il singolo valore $P'$ — la tweaked key. Questo valore è indistinguibile da una normale chiave pubblica Schnorr. Gli script sono invisibili, ma sono crittograficamente impegnati all'interno della chiave.

#### Key Path vs Script Path Spending

Taproot prevede due modalità di spesa:

**Key path spending** (*spesa via chiave*): se tutte le parti coinvolte sono d'accordo, producono una firma Schnorr aggregata valida per $P'$. Nessuno script viene rivelato. Dall'esterno sembra una semplice transazione a firma singola, anche se in realtà ci sono molteplici condizioni possibili. Questo è il caso "felice" e più privato.

![Key path spending: tutti i partecipanti cooperano, producono una firma Schnorr aggregata. Il nodo verifica $\text{sig}$ rispetto a $P'$. Indistinguibile da una transazione standard.](images/lezione-18-hard-and-soft-forks-in-bitcoin-img-11.jpg)

**Script path spending** (*spesa via script*): se le parti non possono usare la key path (es. una parte non è disponibile), si rivela la foglia dello script desiderato e la Merkle proof che dimostra che quella foglia era nell'albero. Le condizioni alternative rimangono nascoste.

![Script path spending: si rivela lo script specifico (tapleaf) e il Merkle path verso la root. Si producono le firme/dati richiesti dallo script. Le altre condizioni rimangono private.](images/lezione-18-hard-and-soft-forks-in-bitcoin-img-12.jpg)

> [!abstract] Sintesi: Taproot
>
> Taproot unifica in modo elegante tre tecnologie: Schnorr Signatures (efficienza e aggregazione), MAST (script privati e compatti), e la tweaked key (un unico valore on-chain che impegna tutto). Il risultato è che transazioni Bitcoin complesse — multisig, timelock, contratti — appaiono on-chain identiche a transazioni semplici, migliorando sia la privacy degli utenti che l'efficienza della rete.

### Hard Fork

> [!definition] Hard Fork
>
> Un hard fork è una modifica alle regole di consenso **non retrocompatibile** che crea una divisione permanente della blockchain. I nodi non aggiornati rifiutano i blocchi prodotti dai nodi aggiornati, portando a due catene distinte.

Le caratteristiche chiave sono: i nodi devono aggiornarsi per seguire le nuove regole; i nodi vecchi rifiutano i nuovi blocchi, causando una divisione della catena; le due catene condividono la storia fino al punto di fork; il risultato è l'esistenza di due reti separate con asset separati.

#### Bitcoin Cash — Agosto 2017

Il caso più celebre di hard fork di Bitcoin è **Bitcoin Cash**, nata nell'agosto 2017 dallo stesso giorno in cui veniva attivato SegWit. Il conflitto alla radice era la scalabilità: come rendere Bitcoin capace di gestire più transazioni al secondo?

Due visioni si scontrarono. **Bitcoin Core** sosteneva di mantenere blocchi piccoli (~1 MB) e di costruire soluzioni di secondo livello come SegWit e la Lightning Network. **Bitcoin Cash** optava per aumentare direttamente la dimensione dei blocchi a 8 MB e oltre.

L'hard fork ebbe un effetto immediato e interessante: chiunque avesse 10 BTC al momento del fork si ritrovò con 10 BTC e 10 BCH. La chiave privata Bitcoin funziona anche per Bitcoin Cash, perché le due blockchain condividono la storia fino al punto di scissione. Gli indirizzi dei wallet sono gli stessi. Gli UTXO esistenti al momento del fork sono validi su entrambe le catene, e spendere un UTXO su una catena non lo consuma sull'altra, perché le due catene sono indipendenti.

> [!note] Stato attuale di Bitcoin Cash
>
> Bitcoin Cash è ancora attiva. Fornisce circa 200 transazioni al secondo. Mantiene lo stesso algoritmo di mining di Bitcoin, quindi i miner possono minare entrambe le criptovalute. Il suo prezzo ha raggiunto un picco nella fase iniziale per poi calare significativamente rispetto a Bitcoin.

#### Hard Fork come Strategia di Bootstrap

Gli hard fork sono diventati anche uno strumento strategico per lanciare nuove criptovalute. Anziché costruire una blockchain da zero — con la difficoltà di attirare utenti e sviluppatori — si crea un hard fork di Bitcoin e si annuncia agli utenti Bitcoin esistenti che riceveranno la stessa quantità della nuova criptovaluta. Questo abbassa la barriera all'adozione: chi aveva BTC si ritrova automaticamente con asset nella nuova rete.

Gli **Altcoin** sono nati così: alcune sono fork di Bitcoin fatte da comunità diverse che volevano seguire un percorso alternativo di sviluppo, altre sono fork nate esplicitamente per creare nuovi asset.

![I fork di Bitcoin nel 2017: Bitcoin Cash e Bitcoin Gold sono hard fork che generano nuove catene (BCH, BTG); SegWit è il soft fork che mantiene la catena principale; SegWit2x è un tentativo di hard fork abortito (B2X).](images/lezione-18-hard-and-soft-forks-in-bitcoin-img-13.jpg)

#### Hard Fork per Vulnerabilità Crittografiche

Esistono scenari in cui un hard fork non è una scelta ma una necessità tecnica. Se viene scoperta una vulnerabilità critica nelle primitive crittografiche usate dalla blockchain, la risposta può richiedere un hard fork.

Un esempio concreto: se SHA-256 venisse compromesso, Bitcoin dovrebbe migrare a SHA-3. Aggiungere SHA-3 potrebbe essere un soft fork, ma rimuovere SHA-2 e sostituirlo completamente con SHA-3 richiede un hard fork — è una modifica non retrocompatibile.

Il caso più rilevante a lungo termine è quello dei **computer quantistici**: algoritmi come Shor possono rompere la crittografia a curva ellittica e le firme digitali — incluse le Schnorr Signatures. Se un computer quantistico sufficientemente potente diventasse disponibile, potrebbe derivare chiavi private dalle chiavi pubbliche e accedere ai fondi di chiunque. La risposta richiederebbe un hard fork per adottare algoritmi di firma **post-quantum** resistenti all'attacco quantistico.
