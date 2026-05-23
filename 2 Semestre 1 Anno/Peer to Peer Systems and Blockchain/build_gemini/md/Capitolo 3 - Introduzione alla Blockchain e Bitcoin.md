# Capitolo 3 - Introduzione alla Blockchain e Bitcoin

## Il Ledger Distribuito

> [!definition] Ledger
>
> Un registro cronologico di eventi, **append-only**: si possono solo aggiungere voci, mai modificare o cancellare quelle passate. Funziona come un notaio digitale: tutti i partecipanti devono concordare sul suo contenuto.

Un ledger non serve solo per le transazioni finanziarie: qualunque applicazione che necessita di un log di eventi può beneficiarne. Un ledger distribuito viene replicato tra i nodi di una rete P2P: ogni nodo possiede la stessa copia immutabile.

> [!example] Alice come intermediaria
>
> Alice gestisce un'azienda che fa da intermediaria tra dettaglianti e grossisti. Ha difficoltà a mantenere un ledger consistente perché serve centinaia di clienti. Decide di condividere il ledger con tutti: ciascuno mantiene una copia e la aggiorna. Emerge immediatamente il problema della **consistenza**: chi decide cosa è scritto nel ledger?

Quando il ledger è organizzato come una sequenza di blocchi concatenati prende il nome di **blockchain**. Esistono architetture alternative — **IOTA**, ad esempio, usa un DAG invece di una catena lineare.

Ogni blocco contiene tre elementi:
- **Dati** — le transazioni (es. "Alice invia X a Bob")
- **Hash del blocco** — impronta crittografica del contenuto
- **Hash del blocco precedente** — il collegamento che forma la catena (hash pointer)

La catena parte dal **Genesis Block**. Modificare un blocco cambia il suo hash, invalidando tutti i successivi. In una blockchain **Proof of Work**, ripristinarli non richiede solo ricalcolare gli hash: bisogna trovare un valore che, combinato con il nuovo hash, risolva il PoW per ogni blocco successivo. Questo è computazionalmente impossibile. Altre blockchain possono usare meccanismi diversi (es. PoS).

## Il Problema del Consenso

In un sistema distribuito senza autorità centrale, chi decide quale operazione aggiungere al registro?

> [!definition] Consenso
>
> Accordo tra i nodi di una rete distribuita sull'**ordine e la validità** delle informazioni memorizzate su un ledger condiviso e replicato. Il consenso è il meccanismo che definisce: chi decide quale operazione viene aggiunta alla blockchain, e quale tra le operazioni da confermare viene scelta.

Il consenso è essenziale per prevenire il **double spending**: le informazioni digitali si copiano facilmente — i bit sono più facili da copiare della carta — quindi senza un accordo collettivo nulla impedisce di spendere la stessa moneta due volte. Se la maggioranza è onesta, i nodi dovrebbero votare contro le transazioni di double spending.

Un approccio classico è il **consenso basato sul voto**: ogni operazione viene trasmessa in broadcast sulla rete e si raccolgono i voti; la maggioranza determina la correttezza delle transazioni e l'ordine dei blocchi.

In un mondo ideale funzionerebbe, ma in reti P2P aperte ci sono due ostacoli reali:
- Ritardi e partizioni di rete (*jitter*, nodi che non si vedono temporaneamente)
- Nodi malintenzionati (**byzantine parties**) che possono comportarsi in modo arbitrario

## L'Attacco Sybil

Il punto debole del consenso a voto in reti aperte: cosa significa "maggioranza" se chiunque può creare identità false?

> [!definition] Attacco Sybil
>
> Un attaccante inietta nella rete un numero arbitrario di identità fittizie per ottenere la maggioranza dei voti e manipolare il consenso. Il nome viene dalle Sibille dell'antica Grecia — profetesse attraverso cui parlava una divinità, metafora di più identità per la stessa persona; rappresentate nel pavimento del **Duomo di Siena**. In informatica il libro di riferimento è *Sybil* (Flora Rheta Schreiber, 1973), su una donna con 16 personalità distinte.

Iniettare identità false è banale: basta registrarsi molte volte con la stessa DHT. Il singolo nodo impersona così molteplici identità logiche.

**Obiettivi dell'attacco Sybil:**
- Routing attacks (controllare i percorsi di instradamento)
- Controllare la replica dei dati
- Disturbare la connettività della rete
- Essere la maggioranza nel voto → consenso nelle criptovalute

**Difese:**
- **Proof of Work** (Bitcoin, Ethereum): richiede potere computazionale
- **Proof of Stake**: richiede stake economico
- **Certified Node-IDs**: richiede un'autorità centrale — non è una soluzione P2P

### Double Spending con Sybil

Alice esegue un attacco Sybil assumendo più del 50% delle identità nella rete. Poi tenta di spendere lo stesso bitcoin sia verso Bob che verso Charlie. Usando le sue identità multiple (>50%), approva con il consenso entrambe le transazioni di double spending → l'attacco ha successo.

## La Proof of Work

**La soluzione di Bitcoin**: invece di contare le identità, si conta la **potenza di calcolo**.

> [!definition] Proof of Work
>
> Per partecipare al consenso, un nodo deve risolvere un problema computazionalmente difficile ma facile da verificare. Creare identità multiple è inutile se si ha un solo computer: per manipolare la rete bisogna controllare la maggioranza della potenza di calcolo globale. Gli attacchi Sybil diventano costosi e inutili.

La PoW funziona come una **lotteria** in cui i biglietti sono molto costosi (risolvere il problema). Il vincitore della lotteria decide **unilateralmente** quale sarà il prossimo blocco e riceve una ricompensa economica per comportarsi onestamente — incentivo a seguire le regole.

## Proof of Ownership

Oltre al consenso, serve dimostrare la **proprietà** degli asset.

> [!example] ICO di Alice
>
> Alice vuole aprire un ristorante ma l'affitto è alto e i venture capitalist sono avidi. Usa una **ICO** (*Initial Coin Offering*): propone un progetto su blockchain, raccoglie finanziamenti, crea **token** come compensazione per i finanziatori — nel caso concreto, *cryptocoupon* per pasti scontati all'apertura del ristorante.
>
> Alice usa un ledger per registrare i trasferimenti di token. Il problema: come può un finanziatore dimostrare di possedere un coupon? Come può Alice dimostrare di essere autorizzata a emetterlo? Senza una CA centralizzata.

La soluzione è puramente crittografica: Alice genera una coppia `(chiave pubblica, chiave privata)`. Chiunque conosca la chiave privata corrispondente alla chiave pubblica di Alice possiede i suoi cryptocoupon — Alice stessa, chiunque lei voglia (a cui cede la chiave privata), o chiunque la rubi.

- **Chiave pubblica** → identifica il proprietario del token
- **Chiave privata** → conferisce il possesso effettivo e autorizza i trasferimenti tramite firma digitale

### Esempio di Spesa

Alice (con chiave privata `af876f536...`) vuole trasferire il 50% di un coupon a ciascuno di due finanziatori:
1. Identifica le chiavi pubbliche dei destinatari (es. `1FE1W2EEJE...`, `A5d65ab38...`)
2. Firma il trasferimento con la propria chiave privata → dimostra di essere autorizzata
3. Registra la transazione firmata sul ledger
4. I due destinatari usano le proprie chiavi private per riscuotere il mezzo coupon

> [!warning] La chiave privata è tutto
>
> Chiunque ottenga la chiave privata di un utente ha il pieno controllo dei suoi asset — non esiste recupero, non esiste banca che possa aiutare.

## Permissionless vs Permissioned

| | Permissionless | Permissioned |
|---|---|---|
| **Accesso** | Aperto a chiunque | Limitato a nodi autorizzati |
| **Identità** | Anonima/pseudonima | Certificata (umani con password/chiavi, sensori con chiavi) |
| **Consenso** | PoW, PoS (costoso ma senza fiducia) | PBFT e simili (efficiente, ambiente controllato) |
| **Esempi** | Bitcoin, Ethereum, Steemit, Algorand | Hyperledger, Ethereum Quorum, Corda |
| **Rischi** | Fork, attacchi (es. DAO hack da $54M) | Richiede fiducia negli operatori |

### Permissionless

Chiunque può partecipare e minare. Il sistema funziona senza fidarsi di nessuno, grazie agli incentivi economici. Non richiede autorità centrale.

### Permissioned

Accesso e consenso limitati a partecipanti con identità verificata. Le differenze chiave rispetto alle permissionless sono:
- Le parti hanno **identità**: umani con password/chiavi, sensori con chiavi proprie — tutti **autenticati**
- Si usano meccanismi di consenso diversi, basati sul voto tra nodi noti
- **Accountability**: se un nodo viene scoperto a barare, è identificabile — diverso approccio agli attacchi Sybil

> [!example] Supply chain del frozen yogurt
>
> Alice vende il ristorante e apre un'attività di frozen yogurt. Le spedizioni arrivano sciolte: di chi è la colpa — Bob (il trasportatore) o Carol (la fabbrica)? Con una blockchain permissioned accessibile solo a Bob, Carol e sensori di temperatura certificati, ogni evento è tracciato e firmato digitalmente. La responsabilità è attribuibile con certezza.

Il **PBFT** (*Practical Byzantine Fault Tolerance*, Castro e Liskov, 1999) è il protocollo di consenso tipico delle blockchain permissioned: tolera comportamenti arbitrari di nodi malevoli in reti asincrone, con prestazioni nettamente superiori alla PoW in ambienti con partecipanti noti e controllati.

> [!warning] Bitcoin è difficile da capire
>
> Bitcoin si trova al crocevia di più discipline: non solo informatica, ma economia, diritto, politica e scienze sociali. Non è solo una tecnologia — è un cambio di paradigma culturale con implicazioni legali, politiche e sociali rilevanti.

## Le Origini: dalla Moneta Elettronica a Bitcoin

L'idea di una moneta elettronica (**e-cash**) è nata molto prima di Bitcoin. Già nel 1999 Milton Friedman prevedeva lo sviluppo di un metodo per trasferire fondi su Internet tra due sconosciuti — esattamente come scambiarsi una banconota da 20 dollari.

Il primo tentativo concreto fu quello di David Chaum, professore a Berkeley e "padrino" del movimento cyberpunk, negli anni Ottanta. Il suo sistema si basava sulle **firme cieche** (*blind signatures*):

1. L'utente genera una moneta: un token casuale unico
2. L'utente "acceca" (*blinds*) il token e lo invia alla banca per la firma
3. La banca firma il token accecato senza poterne vedere il contenuto — al momento della firma, sa di aver firmato una moneta, ma non quale
4. L'utente "scopre" (*unblinds*) la moneta, ottenendo un token firmato e valido che può spendere anonimamente

Il sistema garantiva l'**intracciabilità** (*pecunia non olet*), ma non risolveva completamente il double spending: l'utente poteva inviare lo stesso token a due commercianti diversi. La contromisura era che ogni commerciante, al momento della riscossione, sottoponeva la moneta alla banca per verifica: se la moneta era già stata spesa, la transazione veniva rifiutata. Elegante — ma richiedeva ancora la fiducia in una banca centrale.

> [!definition] Requisiti della Moneta Elettronica
>
> L'e-cash deve conservare gli attributi fisici del contante:
> - **Non falsificabile** (*unforgeable*): impossibile il double spending
> - **Non tracciabile** (*untraceable*): la privacy dell'utente deve essere garantita — *pecunia non olet*

La storia dei pagamenti ha attraversato millenni: dai bilanci mesopotamici (2040 a.C.), alle banche centralizzate (BNP Paribas, 1848), ai circuiti VISA (1958), fino all'eCash di Chaum (1983). Il vero salto verso il *decentralized banking* arriva nel 2008, seguito da Ethereum (2015) e Zcash (2016).

## Satoshi Nakamoto e il Whitepaper

Nell'ottobre 2008, sotto lo pseudonimo **Satoshi Nakamoto**, viene pubblicato *"Bitcoin: A Peer-to-Peer Electronic Cash System"* sulla mailing list di crittografia. La proposta: pagamenti online diretti tra due parti, senza istituzioni finanziarie. Le firme digitali da sole non bastano — dipendere da terze parti fiduciarie per evitare il double spending ne annulla i benefici.

> [!example] L'Annuncio Originale
>
> Il messaggio di Nakamoto alla mailing list il 31 ottobre 2008:
>
> *"I've been working on a new electronic cash system that's fully peer-to-peer, with no trusted third party. The main properties: Double-spending is prevented with a peer-to-peer network. No mint or other trusted parties. Participants can be anonymous. New coins are made from Hashcash style proof-of-work. The proof-of-work for new coin generation also powers the network to prevent double-spending."*

La soluzione di Bitcoin è una rete P2P che marca temporalmente le transazioni inserendole in una catena basata su **Proof of Work**. La catena più lunga è sia la prova dell'ordine cronologico degli eventi, sia la garanzia che quella sequenza provenga dalla maggioranza della potenza computazionale.

### Nakamoto Timeline

| Data | Evento |
|---|---|
| 2008-08-18 | Registrazione del dominio bitcoin.org |
| 2008-10-31 | Pubblicazione del Bitcoin paper |
| 2008-11-09 | Progetto Bitcoin registrato su sourceforge.net |
| 2009-01-03 | Genesis Block minato alle 18:15:05 GMT |
| 2009-01-09 | Bitcoin v0.1 rilasciato e annunciato sulla mailing list di crittografia |
| 2009-01-12 | Prima transazione (blocco 170) da Satoshi a Hal Finney |
| 2010 (metà) | Nakamoto interrompe ogni interazione e lascia il progetto alla comunità |

> [!example] La Pizza da 10.000 BTC
>
> Nel maggio 2010, sul forum Bitcointalk, Laszlo Hanyecz offrì 10.000 BTC (circa 25 dollari all'epoca, ricevuti come ricompensa di mining) a chiunque gli consegnasse "un paio di pizze". La richiesta fu esaudita da un ragazzo della costa ovest: primo acquisto documentato di beni reali con Bitcoin.

### Bitcoin: Protocollo e Valuta

È importante distinguere tra due accezioni del termine:

- **Bitcoin** (maiuscolo): il protocollo, il software e la comunità
- **bitcoin** (minuscolo): le unità della valuta, gli *asset* nativi intrinseci al protocollo

I bitcoin vengono trasferiti usando il protocollo Bitcoin. Non esiste bitcoin al di fuori del protocollo che lo definisce.

## Caratteristiche e Resilienza

Bitcoin è pensato come alternativa ai sistemi di pagamento tradizionali. Il confronto con le soluzioni precedenti è diretto:

| Problema dei sistemi precedenti | Soluzione Bitcoin |
|---|---|
| Serve un server fidato o istituzione finanziaria | **Apertura**: basta un client Bitcoin, senza conto bancario né carta di credito; nessun ente centralizzato controlla l'offerta di moneta |
| Nessuna anonimità | **Pseudo-anonimità**: transazioni senza disclosure dell'identità; gli indirizzi come pseudonimi — come "pagare in contanti" |
| Alte commissioni di transazione | Commissioni minime (almeno nei primi anni; PayPal richiede 2–10%) |

Bitcoin è transnazionale e senza confini (*borderless*), **permissionless** (nessun regolatore centrale), **censorship resistant** (i fondi non possono essere congelati), **cross-jurisdictional** (nessuna giurisdizione specifica si applica) e pseudonima. L'infrastruttura opera su sospetto di default: nessun partecipante deve fidarsi degli altri.

### Perché Bitcoin è Sopravvissuto

In 17 anni, Bitcoin ha dimostrato una resilienza notevole. Ha superato:

- Il collasso di **Mt. Gox** nel 2014 (Magic the Gathering Online eXchange): all'epoca era il più grande exchange USD/Bitcoin al mondo; a febbraio 2014 dichiarò bancarotta, con circa 850.000 BTC ($450 milioni all'epoca) scomparsi — probabilmente a causa di un attacco di **malleabilità** del protocollo (trattato nelle lezioni successive)
- L'associazione con il dark web attraverso **Silk Road**: mercato online operante come Tor hidden service, attivo tra febbraio 2011 e ottobre 2013, usato per acquistare beni illeciti (droghe, materiale pornografico) anonimamente; il gestore Ross William Ulbricht è stato condannato all'ergastolo
- Attacchi ransomware come **WannaCry**

Nonostante le enormi fluttuazioni di prezzo e lo scetticismo di economisti come Paul Krugman e Alan Greenspan — che lo hanno paragonato a uno schema Ponzi — il sistema è rimasto vitale.

### Ragioni del Successo

Il successo si spiega con diversi fattori:

- **Ragioni ideologiche**: criptoanarchia (nessuno controlla la moneta), movimento cyberpunk
- **Tempismo**: nato durante la crisi finanziaria del 2008 — impossibile "stampare" nuovi BTC arbitrariamente
- **Bitcoin come oro digitale**: offerta controllata dal protocollo, nessun intervento sull'offerta monetaria, sicuro — alcuni suggeriscono di investire fino al 5% del portafoglio in Bitcoin
- **Presenza di exchange**: piattaforme dove i bitcoin si scambiano con valute fiat tradizionali. Dopo Mt. Gox (chiuso nel 2014), ne sono nati altri più affidabili: CoinDesk, BPI, Bitstamp, Bitfinex, Coinbase, itBit, OKCoin
- **Mercati regolamentati**: stanno emergendo mercati Bitcoin con supervisione legale
- **Ecosistema in espansione**: centinaia di altre criptovalute e token nati negli ultimi anni

## Identità e Indirizzi

In assenza di una Certification Authority, Bitcoin gestisce le identità tramite crittografia asimmetrica con l'algoritmo **ECDSA** (*Elliptic Curve Digital Signature Algorithm*) sulla curva *secp256k1*:

$$y^2 = x^3 + ax + b \pmod{p}$$

La derivazione di un indirizzo parte dalla chiave privata e procede in un'unica direzione:

$$sk \xrightarrow{\text{curva ellittica}} pk \xrightarrow{\text{SHA-256}} \xrightarrow{\text{RIPEMD-160}} \xrightarrow{\text{Base58}} \text{Indirizzo Bitcoin}$$

La **chiave privata** (`sk`) deve rimanere segreta: controlla i fondi associati. La **chiave pubblica** (`pk`) si deriva da `sk` tramite moltiplicazione sulla curva ellittica — operazione irreversibile. La chiave pubblica funziona come il "nome pubblico" dell'utente e "parla per" la sua identità; in pratica, si usa più spesso `Hash(pk)` — l'indirizzo. Se una transazione reca una firma `sig` tale che `verify(pk, data, sig) == true`, si può ragionevolmente concludere che `pk` ha autorizzato quella transazione.

L'**indirizzo** è l'hash della chiave pubblica, codificato in **Base58**: un alfabeto alfanumerico da cui Nakamoto ha rimosso i caratteri ambigui (`0`, `O`, `I`, `l`) per prevenire errori di trascrizione. Base58 usa 58 caratteri (62 dell'alfabeto alfanumerico completo meno i 4 ambigui): permette di rappresentare grandi numeri in formato compatto.

> [!note] Nessuna cifratura
>
> In Bitcoin non esiste nulla di cifrato per nascondere informazioni — tutto è pubblico sulla blockchain. Le chiavi servono solo a dimostrare, tramite firma digitale, la proprietà e l'autorizzazione a spendere.
>
> Per garantire privacy si possono utilizzare tecniche di **Zero Knowledge** — ma non sono native nel protocollo base.

> [!note] Gli Indirizzi Possono Rappresentare Script
>
> Nella maggior parte dei casi un indirizzo Bitcoin corrisponde all'hash di una coppia di chiavi pubblica/privata. Tuttavia, un indirizzo può anche rappresentare uno **script** (P2SH — Pay-to-Script-Hash). Chiunque può generare nuove identità in qualsiasi momento e quante ne vuole. Gli indirizzi funzionano come il nome del beneficiario in un assegno: *"pay to the order of xxx"*. Per quanto riguarda la privacy: gli indirizzi non sono direttamente collegati all'identità reale, ma un osservatore può correlare l'attività di un indirizzo nel tempo e trarre inferenze — quindi si parla di **pseudo-anonimità**.

## Flusso di Pagamento

Il flusso tipico di un pagamento Bitcoin segue quattro passi:

1. Il commerciante Bob comunica il proprio indirizzo **fuori banda** (*out of band*) ad Alice — non attraverso la rete P2P Bitcoin. L'indirizzo può essere condiviso via QR code, email, o verbalmente
2. Alice genera una transazione che paga all'indirizzo di Bob e la trasmette in **broadcast** sulla rete P2P
3. I miner raccolgono le transazioni trasmesse in un blocco candidato; uno dei blocchi candidati contenente la transazione viene minato
4. Bob attende le **conferme** sulla transazione prima di consegnare i beni

## Il Modello UTXO

Bitcoin non ha il concetto di "conto" con un saldo. Esistono solo trasferimenti e il sistema si basa sugli **UTXO** (*Unspent Transaction Output*): le transazioni ricevute e non ancora spese. Spendere un UTXO lo distrugge e ne crea di nuovi per il destinatario (e per il resto).

Il saldo mostrato da un wallet è la somma di tutti gli UTXO associati agli indirizzi dell'utente, calcolata scorrendo la blockchain e aggregando tutti gli output non spesi.

> [!tip] Lo Stato di Bitcoin
>
> "Lo stato di Bitcoin risiede negli output non spesi delle transazioni." — L'insieme degli UTXO rappresenta lo spazio condiviso dell'intera rete Bitcoin. A differenza di Ethereum (che richiede una rappresentazione di stato più complessa), il modello UTXO è semplice e verificabile. L'UTXO set è molto più piccolo dell'intera blockchain e può essere mantenuto in RAM, velocizzando i controlli di validità.

I bitcoin di un utente possono essere distribuiti come UTXO tra centinaia di transazioni e centinaia di blocchi — non esiste una nozione di saldo memorizzato su un indirizzo:

$$\sum \text{inputs} \geq \sum \text{outputs}$$

La differenza è la **transaction fee**, che spetta al minatore che include la transazione nel blocco:

$$fee = \sum \text{inputs} - \sum \text{outputs}$$

Gli input devono essere consumati per intero — non si può frazionare un UTXO alla fonte. Per questo le transazioni comuni hanno due output: uno per il destinatario e uno di "resto" (*change*) verso un indirizzo del mittente.

Le strutture di transazione più comuni:

| Tipo | Input | Output | Uso tipico |
|---|---|---|---|
| **Comune** | 1 | 2 | Pagamento + resto al mittente |
| **Aggregazione** | N | 1 | Unire micro-UTXO in uno solo (equivalente di cambiare un mucchio di monete con una banconota); può essere target di **dusting attack** |
| **Distribuzione** | 1 | N | Pagare più destinatari (es. stipendi) |

L'aggregazione viene anche sfruttata per **transazioni multi-firma** (*multisignature*): più parti contribuiscono input e firmano congiuntamente.

## La Struttura JSON di una Transazione

Una transazione Bitcoin reale è rappresentata in formato JSON con tre sezioni principali:

**Metadati:**
- `hash`: hash dell'intera transazione — identificatore univoco
- `version`: permette interpretazioni diverse di alcuni campi
- `locktime`: definisce il momento più precoce in cui la transazione può essere aggiunta alla blockchain; impostato a zero nella maggior parte delle transazioni per indicare esecuzione immediata; usato in transazioni di escrow e nel Lightning Network (canale di pagamento)

**Input** — array JSON dove ogni elemento contiene:
- Hash pointer alla transazione precedente + indice dell'output da spendere
- Script di sblocco (*unlocking script*)

**Output** — array JSON dove ogni elemento contiene:
- Valore da trasferire in quell'output (in satoshi)
- Script di blocco (*locking script*) contenente l'indirizzo del destinatario

## Il Linguaggio di Scripting

Ogni UTXO è governato da uno **script**: un programma che definisce le condizioni per spenderlo. La validazione concatena uno *scriptSig* (script di sblocco, fornito da chi spende) con uno *scriptPubKey* (script di blocco, imposto da chi ha creato l'UTXO) e li esegue insieme.

Il linguaggio di scripting di Bitcoin è deliberatamente:

- **Non Turing-completo** — nessun loop, per impedire cicli infiniti che bloccherebbero i nodi in fase di validazione; tutti i full node (miner e nodi completi, non mobile) devono validare gli script
- **Stateless** — tutta l'informazione necessaria all'esecuzione è contenuta nello script stesso; nessuno stato persiste tra esecuzioni (a differenza di Ethereum)
- **Deterministico** — l'esecuzione è sempre identica su qualsiasi hardware
- **Semplice e compatto** — opcode da un byte (256 istruzioni possibili); istruzione di base: aritmetica, logica (`IF...THEN...ELSE`), istruzioni speciali per crittografia (hash, verifica firma, verifica multi-firma)

L'esecuzione è **stack-based** (simile al linguaggio FORTH): le istruzioni operano su una pila.

Gli opcode principali:

| Opcode | Hex | Descrizione |
|---|---|---|
| `OP_DUP` | `0x76` | Duplica l'elemento in cima allo stack |
| `OP_HASH160` | `0xa9` | SHA-256 seguito da RIPEMD-160 sull'elemento in cima |
| `OP_EQUALVERIFY` | `0x88` | Verifica che i due elementi in cima siano uguali, altrimenti invalida |
| `OP_CHECKSIG` | `0xac` | Verifica la firma crittografica |
| `OP_VERIFY` | `0x69` | Invalida la transazione se il valore in cima non è vero |
| `OP_EQUAL` | `0x87` | Restituisce 1 se i due elementi in cima sono identici, 0 altrimenti |
| `OP_CHECKMULTISIG` | — | Verifica firme multiple (Multi-Sig) |
| `OP_CHECKLOCKTIMEVERIFY` | — | Locktime assoluto: verifica che la transazione non sia spesa prima di un certo momento |
| `OP_CHECKSEQUENCEVERIFY` | — | Locktime relativo rispetto alla transazione precedente |

### Tipi di Script

I tipi di script principali sono:

- **Verifica di firma semplice** — redimere una transazione precedente firmandola con la chiave privata
- **MultiSig** — richiede più firme per spendere
- **Pay-to-Script-Hash (P2SH)** — l'indirizzo rappresenta l'hash di uno script arbitrario; lo script completo viene rivelato solo al momento della spesa
- **Proof-of-burn** — distrugge irrecuperabilmente dei bitcoin (usato per alcune applicazioni)

Script più complessi codificano condizioni di spesa avanzate: transazioni di **escrow**, **green addresses**, **micro-pagamenti**.

### P2PK — Pay-to-Public-Key

Lo script più semplice. I fondi sono bloccati direttamente sulla chiave pubblica:

- **Locking script**: `<Public Key> OP_CHECKSIG`
- **Unlocking script**: `<Signature>`

L'esecuzione inserisce la firma nello stack, poi la chiave pubblica, e `OP_CHECKSIG` verifica che la firma corrisponda. Se sì, lascia `TRUE` in cima allo stack e la transazione è valida.

### P2PKH — Pay-to-Public-Key-Hash

Lo script standard più usato. Il mittente "blocca" i fondi sull'**hash** della chiave pubblica del destinatario (non sulla chiave stessa). Per sbloccarli, il destinatario deve fornire:

1. La **chiave pubblica** — che hashata con `OP_HASH160` deve coincidere con il valore nel blocco
2. Una **firma** valida sulla transazione, verificata con `OP_CHECKSIG`

La prima istruzione è `OP_DUP` perché la chiave pubblica serve due volte: una copia per il confronto dell'hash, l'originale per la verifica della firma.

> [!example] P2PKH in Pratica: Subway
>
> Subway accetta pagamenti in bitcoin. Bob vuole comprare un panino:
> 1. Subway fornisce il proprio indirizzo P2PKH — che può essere codificato in un **QR code** e scansionato dalla fotocamera dello smartphone di Bob, oppure inviato via email
> 2. Bob crea la transazione con lo script P2PKH che blocca i fondi su quell'indirizzo
> 3. Subway può spenderli presentando la propria chiave pubblica (il cui hash corrisponde all'indirizzo) e la firma valida

### Transazioni Coinbase

Le transazioni Coinbase non hanno input derivanti da UTXO precedenti: creano "denaro fresco" come ricompensa per il minatore che ha risolto la Proof of Work. È l'unico meccanismo con cui nuovi Bitcoin entrano in circolazione.

## Ciclo di Vita di una Transazione

Una transazione firmata viene propagata in broadcast ai nodi vicini, che la ritrasmettono fino a inondare la rete. Ogni nodo la valida contro la propria **UTXO Cache** (una cache in RAM degli output non spesi, molto più piccola dell'intera blockchain):

```
Receive transaction t
for each input (h, i) in t do
    if output (h, i) is not in local UTXO or signature invalid
        then Drop t and stop
    end if
end for
if sum of values of inputs < sum of values of outputs then
    Drop t and stop
end if
for each input (h, i) in t do
    Remove (h, i) from local UTXO
end for
Append t to local memory pool (waiting for confirmation)
Forward t to neighbors in the Bitcoin network
```

I passi di validazione sono:
1. Verifica che tutti gli input esistano nella cache UTXO e non siano già stati spesi
2. Verifica che le firme di tutti gli input siano valide (ogni input è firmato con la chiave privata corrispondente alla chiave pubblica referenziata nello script di output)
3. Verifica che $\sum \text{inputs} \geq \sum \text{outputs}$
4. Rimuove gli UTXO consumati dalla cache locale
5. Inserisce la transazione nel **Memory Pool** locale e la propaga

> [!warning] Accettazione Locale vs Globale
>
> L'algoritmo di ricezione descrive la **politica di accettazione locale**: le transazioni accettate localmente potrebbero non essere accettate globalmente. Le transazioni considerate non confermate vengono aggiunte al memory pool locale. Per essere globalmente confermate e aggiunte alla blockchain, serve il **consenso** — ovvero che un miner le includa in un blocco valido.

La transazione diventa permanente e irreversibile solo quando un minatore la seleziona dal memory pool, la include in un blocco candidato e risolve la Proof of Work — ancorandola alla blockchain con il consenso della rete.
