# Capitolo 5 - Bitcoin: Scripting e Layer 2

Tre costrutti avanzati di Bitcoin — **multisignature**, **hash lock** e **time lock** — sono alla base della Lightning Network, la principale soluzione di scalabilità per Bitcoin. Oltre a questi, esamineremo il trilemma della blockchain, la gestione dei dati e i client leggeri (SPV).

## Multisignature (Multisig)

In un protocollo multi-firma, un gruppo di firmatari autorizza collettivamente una transazione; la verifica avviene tramite le chiavi pubbliche di tutti i partecipanti. L'approccio ingenuo concatena le firme individuali, ma la dimensione cresce linearmente con il numero di firmatari. L'ideale sarebbe una dimensione fissa indipendente dal numero di partecipanti.

![Confronto tra firme multiple separate e aggregate.](images/Pasted-image-20260407113044.png)

Bitcoin ha adottato inizialmente la soluzione più semplice con **ECDSA**: firme multiple separate, non aggregate. Le **firme Schnorr**, che permettono l'aggregazione, sono state introdotte solo in seguito con il protocollo **Taproot**.

Un indirizzo multisig accoppia un indirizzo Bitcoin a un locking script che richiede **M** firme valide su **N** chiavi pubbliche associate.

### Script Multisig

**Locking script** M-of-N:
```
M <PubKey1> … <PubKeyN> N OP_CHECKMULTISIG
```

**Unlocking script** (qualsiasi combinazione valida di M firme):
```
<Signature 1> … <Signature M>
```

Esempio 2-of-3 con Alice, Bob e Judy:
- Locking: `2 <PkA> <PkB> <PkC> 3 OP_CHECKMULTISIG`
- Unlocking valido: `<Sig A> <Sig C>` — qualsiasi due delle tre

### Casi d'uso

| Schema | Caso d'uso |
|---|---|
| **1-of-2** | Conto corrente coniugale per piccole spese — basta la firma di uno |
| **2-of-2** | Conto risparmio — entrambi devono approvare |
| **2-of-2** | Wallet con autenticazione a due fattori (laptop + smartphone) — un trojan sul telefono non basta per rubare i fondi |
| **2-of-2** | Blocco fondante della Lightning Network |
| **2-of-3** | Conto risparmio genitore-figlio — il figlio non può prelevare senza il consenso di un genitore |
| **2-of-3** | Escrow trustless tra compratore e venditore con arbitro |

## Transazioni Escrow

Alice vuole acquistare un libro raro da Bob, ma vivono in città diverse e non si fidano l'uno dell'altro: Alice non vuole pagare prima di ricevere il libro, Bob non vuole spedire prima di essere pagato.

La soluzione è una **transazione escrow 2-of-3** con Judy come arbitro neutrale. Alice crea la transazione multisig con una chiave pubblica ciascuno per Alice, Bob e Judy, e la pubblica sulla blockchain. I fondi entrano in una sorta di "limbo": nessuno può muoverli da solo, servono sempre due firme. L'escrow fallisce solo se Judy collude esplicitamente con una delle parti.

> [!example] I tre scenari possibili
>
> **2a — Tutto ok**: Alice riceve il libro. Alice e Bob firmano insieme per rilasciare i fondi a Bob. Judy non viene coinvolta. Servono due transazioni: una per depositare nell'escrow, una per pagare Bob.
>
> **2b — Alice riceve ma rifiuta di pagare**: Bob fornisce a Judy la prova di spedizione. Bob e Judy firmano insieme per inviare i fondi a Bob.
>
> **2c — Bob non spedisce**: Alice dimostra a Judy di non aver ricevuto nulla. Alice e Judy firmano insieme per restituire i fondi ad Alice.

## Pay-To-Script-Hash (P2SH)

Gli script multisig sono scomodi in pratica. Se un cliente deve pagare un'azienda con un multisig 2-of-5, l'azienda deve trasmettere l'intero script al cliente, che ha bisogno di un wallet speciale per costruirlo. La transazione risultante è cinque volte più grande del normale: fee più alte (a carico del mittente), script troppo lungo per un QR code, e l'intero script resta in RAM nel set UTXO di ogni full node finché non viene speso.

![Schema di funzionamento del Pay-To-Script-Hash (P2SH).](images/Pasted-image-20260407113120.png)

**P2SH** (BIP-16, gennaio 2012) risolve il problema: il destinatario del pagamento è identificato dall'**hash dello script**, non dallo script stesso.

| | Locking script | Unlocking script |
|---|---|---|
| **Multisig classico** | `OP_1 <PK1> <PK2> OP_2 OP_CHECKMULTISIG` | `OP_0 <Sig1>` |
| **P2SH** | `OP_HASH160 <RedeemScriptHash> OP_EQUAL` | `OP_0 <Sig1> <Sig2> \| <OP_2 <PK1> <PK2> <PK3> OP_3 OP_CHECKMULTISIG>` |

Per riscattare un P2SH l'utente presenta: la firma richiesta + il *Redeem Script* originale in chiaro, che hashato deve coincidere con l'hash nel locking script.

> [!tip] Il vantaggio chiave del P2SH
>
> Il P2SH sposta tutti gli oneri **dal mittente al destinatario**:
> - La complessità di costruire lo script passa al destinatario
> - Le fee aggiuntive per lo script lungo le paga il destinatario (al momento della spesa), non il mittente
> - Lo script lungo non occupa RAM nell'UTXO set ora, ma viene registrato sulla blockchain solo quando viene speso (nell'input)
> - Gli script vengono codificati come normali indirizzi: qualsiasi wallet semplice può pagare

## Hash-Time Locked Contracts (HTLC)

Un HTLC combina due meccanismi:

> [!definition] HTLC
>
> - **Hash Lock**: l'hash di un segreto è pubblicato nello script. I fondi si sbloccano solo se il destinatario rivela pubblicamente il segreto originale.
> - **Time Lock**: condizione di fallback — se entro un timeout prestabilito il segreto non viene rivelato, i fondi tornano al mittente.

Gli HTLC sono usati nei **payment channel** (Lightning Network) e negli **Atomic Swap**.

### Atomic Swap

Un Atomic Swap permette di scambiare criptovalute su blockchain diverse in modo *trustless*, senza exchange centralizzati. Il problema classico: chi invia i fondi per primo rischia che la controparte non adempia. L'HTLC risolve sincronizzando i due lati dello scambio.

**Esempio**: Alice ha BTC e vuole ZEN di Bob.

1. Alice genera un segreto `s`, ne calcola `H(s)` e crea un HTLC sulla blockchain Bitcoin bloccando 1 BTC: Bob può riscattarli rivelando `s`, oppure dopo 24 ore i fondi tornano ad Alice. Alice invia `H(s)` a Bob.
2. Bob crea un HTLC identico sulla blockchain ZEN bloccando 200 ZEN con lo stesso `H(s)` e un timelock di 24 ore.
3. Alice usa `s` per sbloccare l'HTLC di Bob sulla rete ZEN e incassare i 200 ZEN — operazione pubblica e registrata sulla blockchain.
4. Bob legge `s` dalla blockchain ZEN e lo usa per sbloccare l'HTLC di Alice su Bitcoin, incassando 1 BTC.

L'hashlock sincronizza lo scambio; il timelock garantisce che nessuno perda i fondi se la controparte sparisce.

## Data Registering e Proof of Burn

La blockchain può fungere da **registro notarile**: si calcola l'hash di un documento e lo si registra on-chain per provare l'esistenza di quel file in una data specifica.

Il metodo originale era simulare un pagamento verso un indirizzo falso (nessuno ha la chiave privata corrispondente) usando 20 byte liberi come campo dati. Il problema: quell'UTXO non può mai essere rimosso dalla RAM dei full node — **data pollution**.

**OP_RETURN** (introdotto dopo il 2013 come compromesso) standardizza la registrazione:

```
OP_RETURN <Data>
```

L'output è esplicitamente non spendibile: i coin associati vengono distrutti, ma l'entry non entra nell'UTXO set e non inquina la RAM. Si usa in due modi:
- Solo per registrare dati (senza bruciare coin significativi)
- **Proof of Burn**: distruggere deliberatamente coin in modo verificabile

> [!note] Usi della Proof of Burn
>
> - **Bootstrap di nuove criptovalute**: gli utenti bruciano BTC per ottenere token della nuova chain, distribuendo la supply in modo decentralizzato
> - **Consenso alternativo**: si vince la "lotteria dei blocchi" bruciando coin invece di consumare energia (come nella PoW). Il bilanciamento matematico tra coin bruciati e ricompense è però difficile da implementare correttamente.

## Simplified Payment Verification (SPV)

Scaricare l'intera blockchain (>649 GB ad aprile 2025) non è pratico su smartphone. I **client SPV** (o *lightweight client*) scaricano solo gli **header dei blocchi** — circa 80 byte ciascuno, mille volte più leggeri del blocco completo — e sono interessati solo alle transazioni che riguardano gli indirizzi nel proprio wallet.

La sicurezza è mantenuta su due livelli:
- L'header contiene il **nonce**: si può verificare che la Proof of Work sia stata completata
- La validità di una transazione si verifica tramite **Merkle proof**: il full node invia il ramo del Merkle Tree che collega la transazione alla Merkle Root nell'header. L'SPV ricalcola ricorsivamente gli hash dal basso verso l'alto e confronta il risultato con la radice — se coincide, la transazione è autentica.

### Bloom Filter e Privacy

Richiedere transazioni specifiche per indirizzo rivelerebbe al full node quali indirizzi appartengono all'utente. Per proteggere la privacy, l'SPV invia al full node un **Bloom filter** costruito sugli indirizzi del wallet (OR bit a bit degli hash di ogni indirizzo).

Il full node testa ogni output di ogni transazione contro il filtro:
- Se tutti gli hash restituiscono un bit a 1 → la transazione è *probabilmente* rilevante → viene inviata all'SPV
- Se anche un solo hash restituisce uno 0 → la transazione è *certamente* irrilevante → viene ignorata

I falsi positivi sono accettati deliberatamente: nascondono quali indirizzi interessano davvero all'SPV (privacy) e rimangono comunque pochi (efficienza di banda).

## Bitcoin Protocol Stack e Rete P2P

| Livello | Descrizione |
|---|---|
| **Application layer** | Applicazioni user-facing che usano la blockchain |
| **Transaction layer** | Script e logica di validità delle transazioni |
| **Consensus layer** | Algoritmi per l'accordo sull'incorporazione delle transazioni (es. PoW) |
| **Network (P2P) layer** | Broadcasting dei dati tra i nodi |

La rete P2P è **non strutturata**: chiunque può connettersi. Di default ogni nodo mantiene 117 connessioni TCP in uscita e accetta fino a 8 in entrata sulla porta 8333, senza autenticazione né cifratura.

![Schema della rete P2P di Bitcoin non strutturata.](images/Pasted-image-20260407113308.png)

### Bootstrap e Peer Discovery

Un nodo nuovo deve prima trovare qualcuno con cui parlare. I metodi in ordine di preferenza:
1. **Seed address hard-coded** nel client — nodi stabili con IP statici
2. **DNS bootstrap** — server DNS dedicati che restituiscono liste di IP
3. **Forum e chat** — fallback manuale se tutto il resto fallisce

Una volta connesso, il nodo ricorda gli indirizzi dei peer con cui ha comunicato con successo: al riavvio può riconnettersi rapidamente senza ripartire da zero.

Per scoprire ulteriori peer, il nodo invia messaggi `GETADDR` ai vicini, che rispondono con messaggi `ADDR` contenenti liste di IP. Il nuovo nodo annuncia anche se stesso inviando un `ADDR` con il proprio IP, che i vicini propagano ai loro vicini.

### Handshake

All'apertura di una connessione, i nodi si scambiano un messaggio `VERSION` che contiene tra l'altro il campo **bestHeight** — l'altezza corrente della blockchain del nodo. Se un nodo ha una catena più corta di quella del vicino, richiede i blocchi mancanti.

![Scambio di messaggi VERSION e processo di Handshake tra nodi Bitcoin.](images/Pasted-image-20260407113353.png)

### Gossip Protocol e Propagazione

La propagazione di transazioni e blocchi avviene tramite **gossip** (*any-to-all*): ogni nodo propaga ai propri vicini ciò che riceve.

Il flusso standard per una transazione o un blocco:

1. **`INV`** — messaggio di annuncio: il nodo invia ai vicini l'hash della transazione/blocco (non il contenuto). È una notifica, non un invio.
2. **`GETDATA`** — i vicini che non hanno già quel dato richiedono il contenuto completo.
3. **`BLOCK` / `TRANSACTION`** — il nodo invia il dato effettivo.

> [!tip] Minimizzare il consumo di banda
>
> Se lo stesso hash arriva da più peer contemporaneamente, il nodo invia `GETDATA` a **uno solo** di essi. Questo evita di scaricare lo stesso dato più volte.

**Unsolicited Block Push**: quando un miner trova un blocco, sa con certezza di essere l'unico ad averlo. Salta il passaggio `INV` e invia direttamente il blocco ai vicini — ogni secondo conta per non perdere il vantaggio competitivo.

**GETBLOCK**: un nodo che si è disconnesso o si avvia per la prima volta deve sincronizzarsi. Chiede al vicino la sua visione locale della blockchain; il vicino risponde con gli hash dei blocchi a varie altezze. Il nodo trova il primo hash in comune con la propria catena e richiede i blocchi successivi tramite `GETDATA`. Il processo è iterativo: dopo aver scaricato un batch, invia un nuovo `GETBLOCK` fino a essere aggiornato.

### Protezione contro il DoS

Nodi malevoli potrebbero inondare la rete con oggetti invalidi, saturando la banda. La protezione è integrata nel protocollo per design:

- Un nodo invia un messaggio `INV` ai vicini **solo dopo aver validato** il blocco o la transazione (firma valida, UTXO valido)
- Ogni nodo mantiene uno **score di reputazione** per ciascun peer
- Se un peer si comporta male (es. invia transazioni con firme invalide), il suo score viene degradato
- Sotto una certa soglia, il peer viene disconnesso

## Il Trilemma della Blockchain

Come visto in precedenza, le soluzioni basate interamente on-chain pongono un limite scalabile, spingendo verso l'utilizzo dei livelli secondari come la Lightning Network. Vitalik Buterin ha formalizzato l'osservazione che i sistemi blockchain tendono a soddisfare al massimo due delle tre proprietà desiderabili simultaneamente.

> [!definition] Trilemma della Blockchain (Buterin)
>
> Un sistema blockchain può soddisfare al massimo due delle seguenti tre proprietà: **decentralizzazione** (nessun punto di controllo centrale, resistenza alla censura), **scalabilità** (capacità di gestire un numero crescente di transazioni per unità di tempo), **sicurezza** (capacità di operare correttamente e difendersi dagli attacchi).

Concretamente, i sistemi esistenti si posizionano in modo diverso su questo triangolo. Bitcoin ed Ethereum privilegiano sicurezza e decentralizzazione, ma non scalano — Bitcoin elabora circa 7 transazioni al secondo a livello globale, contro le 65.000 di Visa. Hyperledger e Ripple sono sicuri e scalabili, ma centralizzati: un numero ristretto di nodi controlla la rete, con minima resistenza alla censura. IOTA era scalabile e decentralizzato, ma usava un Proof-of-Work leggero che ne comprometteva la sicurezza.

Il problema è quantitativamente serio. Con blocchi da 1 MB (4 MB dal 2017 con SegWit) e transazioni medie da 250 byte, Bitcoin può contenere circa 400 transazioni per blocco, che a un blocco ogni 10 minuti danno 7 TPS. La conferma richiede 6 blocchi per considerarsi definitiva, quindi circa un'ora di attesa. Non c'è confronto con i sistemi di pagamento tradizionali.

### Perché le soluzioni on-chain non bastano

La prima risposta intuitiva è: aumentiamo la dimensione del blocco. Bitcoin Cash ha fatto esattamente questo, portando prima a 8 MB e poi a 32 MB in un hard fork. Il problema è che per raggiungere la stessa capacità di Visa servirebbero blocchi da 8 GB — non è un errore di battitura. I nodi dovrebbero archiviare circa 400 TB di dati generati ogni anno e disporre di 120 megabit/sec di banda. Il risultato inevitabile è che solo un piccolo numero di nodi con risorse molto elevate potrebbe partecipare, aumentando la centralizzazione e riducendo la sicurezza.

Aumentare il tasso di produzione dei blocchi introduce un altro problema: più fork concorrenti, con conseguente riduzione della sicurezza complessiva. Il Proof-of-Stake e i protocolli di consenso leggeri risolvono il problema energetico e scalano meglio, ma spesso non sono davvero decentralizzati in pratica, e tendono a favorire chi è già ricco.

## L'Idea dei Canali di Pagamento Off-Chain

L'intuizione chiave che sblocca il problema è questa: non è necessario che ogni transazione finisca sulla blockchain. La blockchain è lenta e cara da usare perché richiede consenso globale tra tutti i nodi — ma il consenso globale è necessario solo per il regolamento finale dei fondi, non per ogni singolo pagamento intermedio.

> [!tip] Intuizione chiave
>
> Spostare la maggior parte delle transazioni _fuori_ dalla blockchain, usando la catena solo per aprire e chiudere i canali di pagamento. In mezzo, le parti si scambiano "cambiali" (promissory notes) off-chain, a velocità di rete.

L'analogia della slide è illuminante: immaginate un cliente al bar che dà la carta di credito al barista all'inizio della serata. Il barista segna ogni drink su un conto ma non addebita la carta ad ogni giro, evitando le commissioni. Alla fine della serata regola tutto con un'unica transazione. Il barista non rischia niente perché ha la carta in mano come garanzia; se il cliente sparisce, può addebitarla. Nella Lightning Network, la "carta di credito" è il deposito in un indirizzo multifirma sulla blockchain, e le "cambiali" sono transazioni Bitcoin firmate ma non ancora trasmesse in rete.

I canali di pagamento off-chain sono quindi:

- **trustless**: non richiedono fiducia reciproca tra le parti, perché la blockchain funge da arbitro
- **decentralizzati**: costruiti sopra l'infrastruttura di Bitcoin, senza hard fork
- **istantanei**: le transazioni avvengono alla velocità della rete peer-to-peer, non ai ritmi della blockchain
- **ad alto volume**: potenzialmente illimitati in numero di transazioni per canale

La tipologia base è **unidirezionale** (una parte paga sempre l'altra), ma le estensioni più importanti sono i **canali bidirezionali** e la **composizione di canali** — che insieme costituiscono la Lightning Network vera e propria.

## Il Protocollo Lightning Network

La Lightning Network è un protocollo di livello 2 proposto da Joseph Poon e Thaddeus Dryja nel 2015. Tecnicamente si basa su tre operazioni fondamentali per ogni canale: apertura, impegni off-chain e chiusura.

### Apertura del Canale: la Funding Transaction

A livello tecnico, un canale di pagamento è un **indirizzo multifirma 2-di-2** — per spendere i fondi in quell'indirizzo servono le firme di entrambe le parti (Alice e Bob), esattamente come un conto bancario cointestato che richiede due firme per i prelievi.

Per aprire il canale, Alice crea una **funding transaction** che invia i suoi bitcoin all'indirizzo multifirma. Questa è l'unica transazione che deve comparire sulla blockchain durante l'intera vita del canale. La struttura è:

```
Funding Transaction:
  Input:  Indirizzo di Alice
  Output: Indirizzo multifirma Alice+Bob
  Importo: 100K satoshi
```

I fondi restano "in escrow" nell'indirizzo condiviso finché il canale non viene chiuso.

### Impegni Off-Chain: le Commitment Transactions

Una volta aperto il canale, Alice e Bob si scambiano **commitment transactions** — transazioni Bitcoin valide che ridistribuiscono i fondi del multifirma tra i due, ma che _non vengono trasmesse_ sulla blockchain. Rimangono conservate localmente da ciascuna delle parti.

Ogni commitment transaction ha questa struttura:

```
Commitment Transaction N:
  Input:  Indirizzo multifirma Alice+Bob
  Output: Alice → importo_A satoshi
  Output: Bob  → importo_B satoshi
```

La transazione deve essere firmata da entrambi. La sequenza tipica è: Alice firma la transazione e la invia a Bob, che la controfirma e la conserva (e viceversa). Così entrambi hanno in mano un documento valido che, se trasmesso, si traduce in un regolamento on-chain corrispondente al loro saldo attuale.

La cosa cruciale è che ogni nuova transazione _sostituisce_ la precedente — non la annulla tecnicamente, ma la rende obsoleta. Se Alice invia 80 BTC a Bob, entrambi conservano una commitment transaction che dice "Alice: 20, Bob: 80". Se poi Bob ne rimanda 10 ad Alice, entrambi creano e conservano una nuova transazione che dice "Alice: 30, Bob: 70". L'ultima transazione valida rappresenta il saldo corrente del canale.

### Chiusura del Canale: il Settlement On-Chain

Quando le parti vogliono chiudere il canale, una delle due trasmette l'ultima commitment transaction alla rete Bitcoin. La blockchain la registra, i fondi vengono distribuiti secondo i saldi finali, e il canale è chiuso. Solo questa seconda transazione, sommata alla funding transaction d'apertura, finisce sulla blockchain — indipendentemente da quante migliaia di transazioni siano state scambiate nel mezzo.

> [!abstract] Sintesi del ciclo di vita di un canale
>
> 1. **Apertura** (on-chain): Alice deposita fondi nel multifirma — 1 transazione blockchain
> 2. **Operatività** (off-chain): N transazioni scambiate direttamente tra le parti, nessuna sulla chain
> 3. **Chiusura** (on-chain): l'ultima commitment viene trasmessa, i saldi finali vengono regolati — 1 transazione blockchain

Questo schema aumenta anche la **privacy**: la blockchain registra solo apertura e chiusura, senza alcun dettaglio sui singoli pagamenti intermedi.

## Meccanismi di Sicurezza Anti-Frode

Il protocollo introduce un problema serio: le commitment transaction precedenti sono ancora firme valide, perché sono state controfirmate in passato da entrambe le parti. Alice potrebbe voler trasmettere una vecchia transazione in cui aveva un saldo più favorevole. Come si impedisce?

### Double Spending Protection

Il primo livello di protezione è semplice: Bitcoin già previene il double spending. Quando viene trasmessa la commitment transaction finale, l'UTXO del multifirma viene "consumato". Se Alice prova a trasmettere anche una vecchia transazione che spende lo stesso multifirma, la rete la rifiuterà come tentativo di doppia spesa.

Questo funziona bene nel caso normale di chiusura cooperativa, ma non nel caso in cui sia Alice a trasmettere _per prima_ una vecchia transazione prima che Bob trasmetta quella corretta.

### Il Problema della "Cambiale Stracciata"

L'analogia delle cambiali chiarisce il nodo: ogni volta che Alice e Bob si accordano su un nuovo saldo, idealmente "straccerebbero" la cambiale precedente. Ma in Bitcoin non esiste un meccanismo per "stracciare" una transazione off-chain — non c'è garanzia che Alice non ne abbia conservato una copia e la trasmetta quando gli fa comodo.

### La Soluzione: Revocation Secrets e Punishment Mechanism

La Lightning Network risolve il problema con un meccanismo di **punizione basato su segreti di revoca** (_revocation secrets_). L'idea è: ogni commitment transaction è "pericolosa" da usare se sei disonesto, perché l'altra parte ha gli strumenti per punirti.

> [!definition] Meccanismo di Revoca
>
> Ogni commitment transaction contiene un output condizionale sulla sua share: Alice può riscuotere i suoi fondi solo dopo un ritardo (es. 24 ore), oppure immediatamente se viene fornito il **revocation secret** della transazione. Prima di emettere una nuova commitment transaction, Alice deve rivelare a Bob il segreto di revoca della transazione _precedente_. Se Alice pubblica una vecchia transazione, Bob ha il segreto per "punirla" e prendere tutti i fondi del canale.

Il flusso concreto è:

1. Stato 1: Alice ha 700 sat, Bob 300 sat. Entrambi conservano la commitment T1.
2. Si aggiorna a Stato 2: Alice 400 sat, Bob 600 sat. Alice rivela a Bob il **segreto di revoca di T1** e riceve la nuova T2.
3. Se Alice ora trasmette T1 (il vecchio stato più favorevole), Bob ha il segreto per "punirla": presenta il segreto, e un apposito script (hash lock script) gli permette di riscuotere _tutti_ i fondi del canale.

Il ritardo nell'output di Alice (es. 24 ore) è fondamentale: dà a Bob il tempo di rilevare il tentativo di frode e reagire prima che Alice possa incassare i suoi fondi dall'old commitment.

```
Commitment Transaction con revoca:
  Input:  Indirizzo multifirma
  Output1: 90K sat
      → IF revocation_secret THEN paga a Bob
      → ELSE after 24 hours paga ad Alice
  Output2: 10K sat → paga a Bob
```

### Watchtower: Delega del Monitoraggio

Un nodo che partecipa a canali Lightning deve monitorare la blockchain almeno una volta a settimana, per poter reagire a eventuali commit disonesti entro la finestra di 1000 blocchi (~7 giorni). Se un nodo è spesso offline, può delegare questo compito a una **watchtower** — un servizio terzo che monitora la blockchain per conto dell'utente. La watchtower è progettata in modo che non possa tradire l'utente: conosce solo le informazioni necessarie per rilevare e punire la frode, non per rubare i fondi.

## Protezione dai Fondi Bloccati: Time Lock

C'è un'altra trappola potenziale: cosa succede se Bob sparisce subito dopo che Alice ha depositato nel multifirma? I fondi di Alice sarebbero bloccati a tempo indeterminato, perché per liberarli serve la firma di entrambi.

La soluzione prevede che **prima** di trasmettere la funding transaction, Alice si faccia firmare da Bob una transazione di rimborso con time lock:

> "Paga 100 BTC ad Alice dall'indirizzo multifirma dopo 30 giorni"

Alice conserva questa transazione off-chain. Solo dopo aver ricevuto questa garanzia, trasmette la funding transaction. Se Bob sparisce, Alice aspetta 30 giorni e poi trasmette la transazione di rimborso firmata da Bob — e recupera i suoi fondi.

## La Rete Lightning: Routing Multi-Hop

Finora abbiamo parlato di canali bilaterali. Il salto concettuale che trasforma i canali in una _rete_ è la **composizione di canali**: Alice può pagare Dave anche se non ha un canale diretto con lui, purché esista un percorso di canali intermedi.

![Esempio di Routing Multi-Hop nella Lightning Network.](images/Pasted-image-20260407113700.png)

Se Alice ha un canale con Bob, e Bob ha un canale con Carol, e Carol ha un canale con Dave, Alice può instradare il pagamento attraverso Bob e Carol. I nodi intermedi **non si fidano l'uno dell'altro** — ognuno impegna i propri fondi solo a condizione che il nodo successivo faccia altrettanto. Questo si ottiene tramite gli **HTLC**.

### HTLC: Hashed Timelock Contract

L'HTLC è il cuore tecnico del routing sicuro. Combina due meccanismi già visti — hash lock e time lock — in un unico contratto che rende i pagamenti multi-hop **atomici**: o tutti i nodi vengono pagati, o nessuno.

> [!definition] HTLC (Hashed Timelock Contract)
>
> Un contratto che condiziona il pagamento alla rivelazione di un **segreto preimage** $R$ tale che $H(R) = H$ (hash lock), con un limite di tempo entro il quale il segreto deve essere rivelato (time lock). Se il segreto non viene rivelato in tempo, i fondi tornano al mittente.

Il protocollo di pagamento multi-hop funziona così:

1. **Dave** (destinatario) genera un numero casuale segreto $R$ e calcola il suo hash $H = H(R)$. Invia $H$ ad Alice fuori banda (es. nell'invoice di pagamento).
2. **Alice** crea un HTLC verso Bob: "ti pago 1 BTC se riesci a darmi l'$R$ tale che $H(R) = H$, entro 20 giorni."
3. **Bob**, sapendo che deve ottenere $R$ da Dave tramite Carol, crea un HTLC verso Carol: "ti pago 1 BTC se mi dai $R$, entro 15 giorni."
4. **Carol** crea un HTLC verso Dave: "ti pago 1 BTC se mi dai $R$, entro 10 giorni."
5. **Dave** rivela $R$ a Carol e incassa il suo BTC.
6. Il segreto $R$ si propaga all'indietro: Carol lo presenta a Bob, Bob lo presenta ad Alice, tutti vengono pagati in cascata.

I timelock sono **decrescenti** lungo il percorso (20→15→10 giorni): questo garantisce che ogni nodo abbia abbastanza tempo per riscuotere il proprio pagamento prima del timeout del nodo precedente. Se Dave non rivela $R$ entro il termine, tutti i pagamenti vengono automaticamente rimborsati.

> [!tip] Atomicità degli HTLC
>
> Poiché ogni nodo può riscuotere solo presentando $R$, e $R$ diventa noto solo quando Dave lo rivela, l'intera catena di pagamenti è atomica: o Dave rivela il segreto e tutti vengono pagati, oppure nessuno lo rivela e i fondi tornano indietro. Un nodo intermedio non può rubare i fondi.

### Capacità del Canale e Liquidità

Il routing introduce due concetti fondamentali che spesso vengono confusi:

> [!definition] Channel Capacity vs Channel Balance
>
> La **channel capacity** è la somma totale dei fondi depositati nel canale alla sua apertura. È fissa per tutta la vita del canale. Il **channel balance** è come quei fondi sono distribuiti tra i due nodi in un dato momento. Varia dinamicamente ad ogni transazione.

Un nodo che vuole fare routing deve avere **liquidità in uscita** (outbound liquidity) verso il nodo successivo. Il routing calcola percorsi basandosi sulla channel capacity (pubblica), ma non conosce il channel balance (privato). Questo genera fallimenti di routing: un canale con capacity 3 BTC potrebbe avere tutto il balance dalla parte sbagliata, rendendo impossibile instradare 2 BTC in quella direzione. La conseguenza pratica è che l'algoritmo attuale usa **brute force path probing**: prova un percorso, se fallisce ne prova un altro, e così via — il che porta a latenze elevate per circa il 5% dei pagamenti (oltre 3 minuti).

### Onion Routing per la Privacy

Per garantire la privacy, il routing usa una tecnica ispirata a [[Tor]] denominata **onion routing**: il mittente costruisce un "cipolla" a strati crittografati. Ogni nodo intermedio può decriptare solo il proprio strato, scoprendo esclusivamente l'identità del nodo precedente e del successivo — mai l'intera traiettoria del pagamento. Questo impedisce ai nodi intermedi di sapere chi sta pagando chi.

### Rebalancing dei Canali

Con l'uso, un canale tende a sbilanciarsi: se Alice paga sempre Bob, il balance si sposta tutto dal lato di Bob, esaurendo la liquidità in uscita di Alice. Per ribilanciare, un nodo può eseguire un **circular payment** — instrada un pagamento a se stesso attraverso un percorso che ripristina i balance desiderati senza costi di apertura/chiusura di nuovi canali.

## Stato Attuale e Problemi Aperti

La Lightning Network ha rilasciato la versione alpha a gennaio 2017. Il primo acquisto noto tramite Lightning è avvenuto a gennaio 2018. Il 20 marzo 2018 è stato sferrato il primo attacco DDoS, portando offline 200 nodi. Da allora la rete è cresciuta significativamente, con migliaia di nodi e canali attivi.

Esistono diverse implementazioni open source indipendenti e interoperabili: C-Lightning, Eclair (Scala), LND (Go), Ptarmigan (C++), Rust-Lightning, LIT (Python), Electrum. Le specifiche sono pubblicate come **BOLT** (Basis Of Lightning Technology), da BOLT #1 (protocollo base) a BOLT #11 (protocollo invoice per pagamenti Lightning).

Per Ethereum esiste la **Raiden Network/uRaiden**, lanciata sulla mainnet a novembre 2017, ma non ha avuto lo stesso successo, soppiantata da altre soluzioni Layer-2 come i rollup.

### Limiti della Lightning Network

La Lightning Network risolve brillantemente il problema della scalabilità, ma introduce nuovi trade-off:

**Fund locking**: i fondi depositati nei canali sono immobilizzati per tutta la durata del canale. Un nodo che vuole fare routing deve impegnare capitali significativi. Comportamenti disonesti della controparte possono bloccare i fondi per settimane.

**Always-on requirement**: senza watchtower, un nodo deve monitorare la blockchain regolarmente per proteggersi da chiusure fraudolente. Questo è problematico per i wallet mobile.

**Centralizzazione strisciante**: ci sono indizi che la rete stia sviluppando una topologia hub-and-spoke, con pochi nodi hub molto connessi che gestiscono la maggior parte del routing. Se confermato, ridurrebbe la decentralizzazione effettiva.

**Routing inefficiente**: il brute force probing è lento e produce molti fallimenti. I nuovi algoritmi proposti (gossip-based, ant algorithms) non sono ancora maturi.

**Apertura del canale costosa**: si ha bisogno di almeno una transazione on-chain per aprire ogni canale, il che non è economico durante periodi di fee elevate.

Resta aperta la domanda centrale posta alla fine della lezione: i canali off-chain sono una soluzione al trilemma? La risposta è: _non è ancora dimostrato formalmente_. Migliorano enormemente la scalabilità senza sacrificare la sicurezza, ma la questione della decentralizzazione — specialmente nella topologia del grafo che si sta formando — rimane un punto di ricerca attivo.
