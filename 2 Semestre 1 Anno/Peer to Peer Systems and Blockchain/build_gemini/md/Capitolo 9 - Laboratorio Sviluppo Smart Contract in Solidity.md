# Capitolo 9 - Laboratorio Sviluppo Smart Contract in Solidity

## Ethereum: ripasso del modello degli account

### Il modello account vs UTXO

Ethereum adotta un **modello basato su account**, non su UTXO come Bitcoin. Questo lo rende concettualmente più simile a un conto bancario: ogni account ha un saldo che può essere incrementato o decrementato direttamente, il "cambio" è implicito, e la verifica della firma è fatta sull'account stesso (non su script).

L'identificatore di un account è gli ultimi 160 bit dell'hash **Keccak-256** della chiave pubblica — non c'è un encoding human-friendly come in Bitcoin (no Base58Check).

### EOA vs Contract account

Esistono due tipi di account:

- **EOA** (*Externally Owned Account*): account controllato da una chiave privata, l'unico che può *iniziare* transazioni autonomamente.
- **Contract**: account senza chiave privata, il cui comportamento è determinato da bytecode EVM. Viene attivato solo quando riceve una transazione.

![Confronto tra EOA e Contract: solo l'EOA possiede una chiave privata e paga il gas. Il Contract riceve il proprio indirizzo come hash di sender+nonce alla creazione.](images/lezione-20-lab-solidity-img-01.jpg)

### Campi di ogni account

Tutti gli account, sia EOA che Contract, condividono quattro campi:

- **nonce** — numero di transazioni inviate dall'account (per EOA) o numero di contratti creati (per Contract, da 1). Previene la *malleability* e garantisce l'ordinamento: campo **dinamico**.
- **balance** — quantità di wei posseduti, espressa come intero: **dinamico**.
- **codeHash** — hash del bytecode EVM del contratto (per gli EOA è l'hash della stringa vuota). Il codice vero e proprio è conservato nel database di stato sotto il suo hash: **statico**.
- **storageRoot** — hash della radice di un *Merkle Patricia Trie* che codifica lo storage dell'account (una mappa da interi a interi), vuoto per default: **dinamico**.

> [!tip] Statico vs Dinamico
>
> `codeHash` è l'unico campo **statico**: il bytecode di un contratto non cambia dopo il deployment. Tutti gli altri campi variano ad ogni transazione che li coinvolge.

---

## Lo stato di Ethereum

Lo stato globale di Ethereum è strutturato come una gerarchia di **Merkle Patricia Trie**. Ogni blocco contiene nel suo header tre radici di trie:

- **stateRoot** — la radice del World State Trie, che mappa ogni indirizzo ai quattro campi dell'account.
- **transactionsRoot** — la radice del Transactions Trie, dove la chiave è l'indice della transazione nel blocco (da 0).
- **receiptsRoot** — la radice del Receipts Trie, che contiene i risultati dell'esecuzione di ogni transazione.

![Il block header punta via hash a tre trie: World State, Receipts e Transactions. L'Account State contiene nonce, balance, storageRoot e codeHash; lo storageRoot punta a sua volta all'Account Storage Trie.](images/lezione-20-lab-solidity-img-02.jpg)

La struttura si replica su blocchi successivi: ogni nuovo blocco N+1 condivide i nodi immutati con il blocco N (persistent data structure) e crea nuovi nodi solo per gli account modificati.

![I blocchi N e N+1 mostrano come i Merkle Patricia Trie si propaghino tra blocchi: le foglie gialle rappresentano gli account modificati, i nodi condivisi rimangono inalterati.](images/lezione-20-lab-solidity-img-03.jpg)

### Receipt e Bloom filter

Per ogni transazione viene generata una **receipt** contenente:

- `medstate` — root del state trie dopo l'elaborazione della transazione.
- `gas_used` — gas consumato cumulativo dopo la transazione.
- `logs` — lista di voci della forma `[address, [topic1, topic2...], data]`, generate dagli opcode `LOG0`…`LOG4` durante l'esecuzione (incluse le sub-call). L'indirizzo è quello del contratto che ha emesso il log, i topic sono fino a 4 valori da 32 byte.
- `logBloom` — **Bloom filter** costruito su indirizzi e topic di tutti i log della transazione.

L'OR bit a bit di tutti i `logBloom` delle receipt viene inserito nell'header del blocco. Questo permette a client leggeri di verificare rapidamente se un blocco contiene log rilevanti senza scaricare l'intero stato.

> [!definition] Bloom filter
>
> Struttura dati probabilistica che permette di verificare l'appartenenza di un elemento a un insieme in tempo costante. Può restituire falsi positivi ma mai falsi negativi. Nel contesto Ethereum, consente di filtrare efficientemente i blocchi rilevanti per una query su eventi.

### Log ed eventi in Solidity

I log risiedono **sopra** lo stato EVM interno e non sono visibili ai contratti durante l'esecuzione. Sono pensati per applicazioni esterne, che possono sottoscriversi a specifici tipi di log senza dover rieseguire tutte le transazioni o mantenere lo stato.

In Solidity i log si usano tramite gli **eventi**:

```solidity
event moneySent(address indexed _from, address _to, uint _amount);

function sendMoney(address _to, uint _amount) public returns (bool) {
    require(Balance[msg.sender] >= _amount, "Not enough value");
    moneyBalance[msg.sender] -= _amount;
    moneyBalance[_to] += _amount;
    emit moneySent(msg.sender, _to, _amount);
    return true;
}
```

Il parametro `indexed` su `_from` significa che il topic corrispondente viene incluso nel Bloom filter, rendendo le query per mittente molto efficienti.

> [!note] Smart contract e source code
>
> Nello stato EVM è conservato solo il **bytecode** compilato, non il sorgente Solidity. I sorgenti visibili su explorer come Etherscan sono caricati volontariamente dagli sviluppatori e verificati dall'explorer tramite compilazione.

---

## Gas

Il **gas** è il meccanismo che risolve due problemi fondamentali dell'EVM, resa Turing-completa dagli smart contract:

1. **Anti-DDoS**: senza un costo per l'esecuzione, un attaccante potrebbe inviare transazioni con loop infiniti bloccando la rete.
2. **Utilizzo equo delle risorse**: ogni operazione ha un costo in gas proporzionale al lavoro computazionale richiesto.

Il gas viene pagato per l'**esecuzione** (opcode EVM) e per lo **storage** (scrittura nello stato). Aspetto importante: il gas viene pagato anche per transazioni che falliscono o che esauriscono il gas — il lavoro già fatto deve essere compensato.

> [!warning] gaslimit a livello di transazione
>
> Il mittente specifica un `gaslimit` nella transazione: se il contratto consuma più gas del limite, l'esecuzione si interrompe con un **revert** (lo stato viene ripristinato) ma il gas già consumato viene comunque pagato. Questo protegge da comportamenti inattesi, incluse sub-call a contratti esterni.

Il `gaslimit` a livello di blocco (analogo alla block size di Bitcoin) limita il tempo di validazione di un blocco e quindi la quantità di computazione per blocco.

I costi in gas per operazione sono **hardcodati** nell'Appendice G del Yellow Paper di Ethereum. Esiste inoltre un insieme speciale di indirizzi (da `0x01` a `0x0a`) che contengono **precompiled contracts**: contratti il cui comportamento non è definito da bytecode EVM ma è implementato direttamente nell'esecuzione environment (Appendice E del Yellow Paper). Si chiamano come contratti normali ma il gas consumption è anch'esso predefinito.

---

## Solidity

**Solidity** è il linguaggio di programmazione ad alto livello per smart contract su Ethereum. Si compila in bytecode EVM.

Caratteristiche principali:
- **Staticamente tipato**: i tipi vengono verificati a tempo di compilazione.
- **Object Oriented**: un contratto si modella come un'istanza di classe, con stato (variabili di stato) e metodi (funzioni).
- **In continuo sviluppo**: la documentazione ufficiale è su `https://docs.soliditylang.org/en/latest/`.

### Remix IDE

Lo strumento standard per sviluppare e testare contratti Solidity è **Remix IDE**, accessibile via browser.

![Remix IDE: pannello di deploy a sinistra, editor con Counter.sol al centro, log delle transazioni in basso. Si vedono le chiamate a `inc`, `dec`, `get` con i rispettivi hash e gas usato.](images/lezione-20-lab-solidity-img-04.jpg)

![Remix IDE (dettaglio): a sinistra il pannello di deploy, al centro l'editor con Counter.sol, in basso i log delle transazioni con hash, gas usato e valori restituiti.](images/lezione-21-lab-solidity-avanzato-img-01.jpg)

### Primo contratto: Counter

Il contratto `Counter` è l'esempio introduttivo classico. Il workflow su Remix:

1. Creare un nuovo file `Counter.sol`
2. Copiare il codice
3. Compilare
4. Deploy su VM (ambiente locale simulato)
5. Chiamare i metodi
6. Ispezionare le receipt delle transazioni

![Il contratto Counter: variabile di stato `uint256 public count`, funzioni `get()` (view), `inc()` e `dec()` (public). La funzione `dec()` fallisce se `count = 0` per underflow aritmetico.](images/lezione-20-lab-solidity-img-05.jpg)

![Counter.sol (dettaglio del codice sorgente nell'editor).](images/lezione-21-lab-solidity-avanzato-img-02.jpg)

### Pragma e versioning

La direttiva `pragma` specifica la versione del compilatore Solidity richiesta. La semantica del versioning segue regole precise:

| Direttiva | Significato |
|---|---|
| `pragma solidity 0.4.16` | Esattamente la versione 0.4.16 |
| `pragma solidity >=0.4.16 <0.7.1` | Dalla 0.4.16 (inclusa) alla 0.7.1 (esclusa) |
| `pragma solidity ^0.4.16` | Dalla 0.4.16 alla 0.5.0 (esclusa) |

La versione `x.y.*` introduce breaking change rispetto a `x-1.*.*` o `x.y-1.*`.

### Import

Solidity supporta diversi meccanismi di import per la modularizzazione del codice:

```solidity
import "lib/util.sol";                        // import diretto
import "../token.sol";                         // import relativo
import * as tokenLibrary from "lib/token.sol"; // rinomina namespace
// uso: tokenLibrary.varName1
```

### Costrutti principali

Un contratto Solidity è composto da quattro categorie di costrutti:

- **State Variables** — variabili persistenti nello storage del contratto.
- **Functions** — le operazioni che il contratto espone o usa internamente.
- **Errors e Modifiers** — meccanismi di validazione e pattern guard.
- **Events** — log emessi durante l'esecuzione, visibili alle applicazioni esterne.

### Visibility Modifiers

La visibilità controlla chi può accedere a variabili e funzioni.

**Variabili di stato:**

| Modificatore | Comportamento |
|---|---|
| `public` | Visibile internamente + getter automatico con visibilità esterna (`view`) |
| `internal` | *Default.* Visibile nel contratto e nei contratti derivati |
| `private` | Solo nel contratto corrente, non nei derivati |

**Funzioni:**

| Modificatore | Comportamento |
|---|---|
| `external` | Chiamabile solo da transazioni/messaggi esterni (internamente via `this.fun()`) |
| `public` | Chiamabile sia da esterno che internamente |
| `internal` | Solo dal contratto corrente o derivati — non fa parte dell'ABI |
| `private` | Solo dal contratto corrente — non fa parte dell'ABI |

> [!warning] `private` non significa segreto
>
> Una variabile `private` non è accessibile via chiamate Solidity, ma il suo valore è comunque leggibile direttamente dallo storage on-chain da chiunque. In Ethereum non esiste vera riservatezza dei dati in-chain.

> [!tip] ABI e visibilità esterna
>
> L'**ABI** (*Application Binary Interface*) è l'interfaccia pubblica del contratto: descrive le funzioni e gli eventi visibili dall'esterno. Solo le funzioni `external` e `public` fanno parte dell'ABI e possono essere chiamate da transazioni o da altri contratti tramite call standard.

---

## Il sistema dei tipi

Solidity distingue due grandi famiglie di tipi: **value types** e **reference types**. La dichiarazione segue la sintassi `tipo [modificatore] nome;`.

I **value types** non specificano un'area di memoria (il compilatore li colloca nello stack se efimeri, nello storage se variabili di stato). Possono avere qualificatori:
- `transient` — come lo storage ma valido solo per la durata di una singola transazione.
- `constant` — valore sostituito a tempo di compilazione.
- `immutable` — valore fissato a tempo di costruzione del contratto.

I **reference types** devono specificare esplicitamente l'area di memoria: `memory` (temporanea, per la durata della chiamata), `storage` (persistente, nel trie dell'account), o `calldata` (read-only, per i parametri di funzioni `external`).

### Value Types

**Booleano e interi:**

```solidity
bool flag;                  // true / false
int8 .. int256              // interi con segno (int == int256)
uint8 .. uint256            // interi senza segno (uint == uint256)
```

Le divisioni intere arrotondano sempre verso zero (troncamento). I numeri in virgola mobile esistono (`fixed`/`ufixed`) ma sono molto limitati nella versione attuale.

**Byte e stringhe:**

```solidity
bytes1, bytes2, ..., bytes32    // array di byte a dimensione fissa
string                          // sequenza di caratteri UTF-8
```

**Enum:** tipo enumerato con al massimo 256 membri. Internamente rappresentato come `uint8`. Quando esposto all'ABI esterna, la firma viene tradotta automaticamente in `uint8`.

```solidity
contract test {
    enum ActionChoices { GoLeft, GoRight, GoStraight, SitStill }
    ActionChoices choice;
    ActionChoices constant defaultChoice = ActionChoices.GoStraight;

    function setGoStraight() public {
        choice = ActionChoices.GoStraight;
    }
    // Per l'ABI esterna getChoice() diventa "getChoice() returns (uint8)"
    function getChoice() public view returns (ActionChoices) {
        return choice;
    }
}
```

### Il tipo `address`

Il tipo `address` è fondamentale in Solidity: rappresenta un indirizzo Ethereum a 20 byte. Esistono due varianti:

- `address` — solo lettura.
- `address payable` — può ricevere Ether (convertibile da `address` con `payable(...)`).

Gli indirizzi hex che superano il checksum EIP-55 sono letterali di tipo `address` (es. `0xdCad3a6d3569DF655070DEd06cb7A1b2Ccd1D3AF`). L'indirizzo zero è `address(0)`.

**Membri dell'address:**

| Membro | Tipo | Descrizione |
|---|---|---|
| `.balance` | `uint256` | Saldo in wei dell'indirizzo |
| `.code` | `bytes memory` | Bytecode all'indirizzo (vuoto per EOA) |
| `.codehash` | `bytes32` | Hash del bytecode |
| `.transfer(amount)` | — | Invia `amount` wei, **revert** on failure, 2300 gas stipend |
| `.send(amount)` | `bool` | Invia `amount` wei, **false** on failure, 2300 gas stipend |
| `.call(payload)` | `(bool, bytes)` | Low-level CALL, tutto il gas disponibile, ritorna bool + data |

> [!warning] `transfer` e `send` sono deprecati
>
> Il limite fisso di 2300 gas era pensato come protezione, ma è una scelta di design fragile: i costi del gas cambiano con gli hard fork e contratti che oggi funzionano potrebbero rompersi in futuro. La pratica corretta è usare `.call{value: amount}("")` con controllo esplicito del valore di ritorno.

**Uso di `call` con selettore di funzione:**

```solidity
(bool success, bytes memory returnData) = address(nameReg).call{
    gas: 1000000,
    value: 1 ether
}(abi.encodeWithSignature("register(string)", "MyName"));
require(success);
```

I primi 4 byte dell'encoding della firma (`abi.encodeWithSignature`) formano il **function selector**: Keccak-256 della firma troncato a 4 byte.

> [!note] `delegatecall` e `staticcall`
>
> - **`delegatecall`**: esegue il codice del contratto chiamato nel contesto del chiamante (stesso storage, stesso `msg.sender`, stesso `msg.value`). Usato nei proxy pattern.
> - **`staticcall`**: come `call` ma esegue un revert se la chiamata modifica lo stato. Corrisponde alle funzioni `view`/`pure`.

**Creazione di contratti e interazione via address type:**

```solidity
contract Created {
    uint public x;
    constructor(uint a) payable { x = a; }
    function increment() public { x += 1; }
    function get() public view returns (uint) { return x; }
}

contract Creator {
    Created innerContract;

    function createCreated(uint arg) public {
        Created newCreated = new Created(arg);   // deploy di un nuovo contratto
        innerContract = newCreated;
    }
    function overrideCreated(address arg) public {
        innerContract = Created(arg);            // cast da address a tipo contratto
    }
    function createAndEndowCreated(uint arg, uint amount) public payable {
        Created newCreated = new Created{value: amount}(arg); // deploy con ETH
        newCreated.x();
    }
}
```

> [!tip] I contratti possono deployare altri contratti
>
> Un account Contract non può *iniziare* transazioni (non ha chiave privata), ma può deployare nuovi contratti tramite `new`. L'indirizzo del contratto creato è il Keccak-256 di `(creator_address, nonce)`.

### La keyword `payable`

Una funzione contrassegnata `payable` può ricevere Ether. Quando un contratto riceve Ether senza specificare una funzione, il runtime EVM cerca nell'ordine:

1. la funzione **`receive()`** (se esiste ed è `payable`),
2. la funzione **`fallback()`** `payable` (se esiste).

```solidity
receive() external payable { ... }   // chiamata senza dati o via transfer/send
fallback() external payable { ... }  // funzione inesistente, o receive assente
```

Entrambe sono funzioni speciali: senza nome (al più una per contratto), senza parametri, senza return. `fallback` viene chiamata anche quando si chiama una funzione inesistente nel contratto.

### Reference Types

**Array:**

```solidity
uint[] storage arr;          // dinamico
uint[10] storage arr;        // statico (dimensione fissa)
// metodi: .length, .push(), .push(elem), .pop()
```

**Struct:**

```solidity
struct Campaign {
    address payable beneficiary;
    uint goal;
    uint amount;
}
```

**Mapping:**

```solidity
mapping(KeyType => ValueType) varName;
```

I mapping funzionano come hash table con tutti i valori inizializzati al default del tipo. La chiave può essere qualsiasi tipo value built-in, `bytes`, `string`, o tipo contratto/enum. Il valore può essere qualsiasi tipo, inclusi mapping annidati.

> [!warning] Limitazioni dei mapping
>
> - I dati della chiave non vengono salvati nello storage: non è possibile enumerare le chiavi.
> - Non hanno `.length`.
> - Possono risiedere solo in `storage` (non in `memory`).
> - **Non sono iterabili**: per iterare occorre mantenere una lista separata delle chiavi.

---

## Unità predefinite

Solidity supporta suffissi per valori monetari e temporali, convertiti a interi a compile time:

```solidity
// Ether
assert(1 wei   == 1);
assert(1 gwei  == 1e9);
assert(1 ether == 1e18);

// Tempo
1 == 1 seconds
1 minutes == 60 seconds
1 hours   == 60 minutes
1 days    == 24 hours
1 weeks   == 7 days
```

---

## Variabili globali

Solidity mette a disposizione variabili e funzioni globali per accedere al contesto di esecuzione:

**Blocco:**

| Variabile | Tipo | Descrizione |
|---|---|---|
| `blockhash(n)` | `bytes32` | Hash del blocco `n` (solo ultimi 256 blocchi) |
| `block.basefee` | `uint` | Base fee del blocco corrente (EIP-1559) |
| `block.chainid` | `uint` | Chain ID corrente |
| `block.coinbase` | `address payable` | Indirizzo del miner/validator del blocco |
| `block.gaslimit` | `uint` | Gas limit del blocco corrente |
| `block.number` | `uint` | Numero del blocco corrente |
| `block.timestamp` | `uint` | Timestamp Unix del blocco corrente (secondi) |
| `gasleft()` | `uint256` | Gas rimanente |

**Messaggio e transazione:**

| Variabile | Tipo | Descrizione |
|---|---|---|
| `msg.data` | `bytes calldata` | Calldata completa |
| `msg.sender` | `address` | Mittente del messaggio (della call corrente — cambia nelle sub-call!) |
| `msg.sig` | `bytes4` | Primi 4 byte della calldata (function selector) |
| `msg.value` | `uint` | Wei inviati con il messaggio |
| `tx.gasprice` | `uint` | Gas price della transazione |
| `tx.origin` | `address` | Mittente originale dell'intera catena di chiamate |

> [!warning] `msg.sender` vs `tx.origin`
>
> `msg.sender` è il mittente della chiamata *corrente* e cambia ad ogni sub-call. `tx.origin` è sempre l'EOA che ha firmato la transazione originale. Non usare `tx.origin` per autenticazione: è vulnerabile ad attacchi di phishing tramite contratti intermedi.

---

## Funzioni

### Constructor

Il `constructor` viene invocato **una sola volta**, durante la creazione del contratto, e non fa parte dell'ABI esterna:

```solidity
constructor() public {
    creator = msg.sender;
}
```

### Valori di ritorno multipli

Solidity supporta return multipli sia con assegnazione esplicita che con `return` inline:

```solidity
// Stile 1: assegnazione nelle named return variables (return implicito)
function arithmetic(uint a, uint b) public pure
    returns (uint sum, uint product)
{
    sum = a + b;
    product = a * b;
}

// Stile 2: return esplicito
function arithmetic(uint a, uint b) public pure
    returns (uint sum, uint product)
{
    return (a + b, a * b);
}
```

Le variabili di ritorno nominate sono inizializzate al valore di default del tipo. Non è possibile restituire mapping (o tipi compositi che li contengono).

### State Mutability

Il modificatore di mutabilità indica cosa può fare la funzione rispetto allo stato della blockchain:

| Modificatore | Può leggere lo stato? | Può modificarlo? |
|---|---|---|
| *(nessuno)* | sì | sì |
| `payable` | sì | sì (+ riceve Ether) |
| `view` | sì | **no** |
| `pure` | **no** | **no** |

**`view`** — vieta di modificare lo stato. Sono considerate modifiche: scrittura a variabili di storage, emissione di eventi, creazione di contratti, `selfdestruct`, invio di Ether, chiamata a funzioni non `view`/`pure`.

**`pure`** — vieta sia lettura che scrittura dello stato. Non può accedere a `block`, `tx`, `msg` (eccetto `msg.sig` e `msg.data`), né a `.balance`. Una funzione `pure` deve essere valutabile a compile-time dati solo i suoi input e `msg.data`.

---

## Errori

Solidity offre tre primitive per segnalare condizioni di errore:

```solidity
assert(bool condition)
// revert con Panic(uint256) se falso — per invarianti che non devono mai fallire

require(bool condition, string memory message)
// revert con Error(string) se falso — per validazione di input o precondizioni

revert(string memory reason)
// revert incondizionato con messaggio personalizzato
```

> [!definition] `Panic` vs `Error`
>
> `Panic` è riservato a errori che **non dovrebbero esistere in codice corretto** (overflow, accesso out-of-bounds, divisione per zero). `Error` è per violazioni di precondizioni o input non validi — condizioni che l'utente può legittimamente causare.

Il **try-catch** è disponibile solo per chiamate esterne — non per chiamate interne. Vedi `FeedConsumer.sol` come esempio.

---

## Function Modifiers

I **modifier** sono guard che si applicano a una funzione prima (e/o dopo) della sua esecuzione. Il simbolo `_` segnaposto indica dove viene inserito il corpo della funzione:

```solidity
contract owned {
    constructor() { owner = payable(msg.sender); }
    address payable owner;

    modifier onlyOwner {
        require(msg.sender == owner, "Only owner can call this function.");
        _;   // <-- qui viene eseguito il corpo della funzione decorata
    }
}

contract myContract is owned {
    function doSomethingRestricted(uint n) public onlyOwner {
        // eseguito solo se msg.sender == owner
    }
}
```

Regole importanti dei modifier:

- Più modifier su una funzione vengono applicati **nell'ordine in cui sono elencati**.
- Non hanno accesso implicito agli argomenti o ai valori di ritorno della funzione decorata — devono essere passati esplicitamente.
- Il simbolo `_` può apparire più volte: ogni occorrenza sostituisce l'intero corpo della funzione.
- Un `return` esplicito in un modifier o nella funzione esce solo dal contesto corrente; il flusso riprende dall'`_` nel modifier precedente.
- I simboli introdotti nel modifier non sono visibili nella funzione e viceversa (eccetto quelli già nel contratto).

---

## Events

Gli eventi sono **log parametrizzati** emessi durante l'esecuzione, scritti nella receipt della transazione e ricercabili off-chain tramite topic, indirizzo del contratto e firma dell'evento. Non sono accessibili on-chain da altri contratti.

```solidity
pragma solidity >=0.4.21 <0.9.0;

contract ClientReceipt {
    event Deposit(
        address indexed from,   // topic 1 (nel Bloom filter)
        bytes32 indexed id,     // topic 2 (nel Bloom filter)
        uint value              // in data (non indicizzato)
    );

    function deposit(bytes32 id) public payable {
        emit Deposit(msg.sender, id, msg.value);
    }
}
```

Un evento può avere fino a **tre parametri `indexed`** (inclusi come topic nel Bloom filter per ricerche efficienti). I parametri non indicizzati vanno nel campo `data` della receipt in formato ABI-encoded.

---

## Selfdestruct

```solidity
selfdestruct(address payable recipient)
```

Nell'EVM pre-Cancun (≤ Shanghai): distrugge il contratto e invia tutti i fondi al `recipient`. Il contratto viene effettivamente rimosso dallo stato **alla fine della transazione** — eventuali revert possono annullare la distruzione. Fino alla fine, tutte le funzioni del contratto rimangono chiamabili.

> [!warning] `selfdestruct` post-Cancun
>
> Dall'hard fork **Cancun** in poi, `selfdestruct` invia i fondi al recipient ma **non distrugge il contratto**. L'unica eccezione è se `selfdestruct` viene chiamato nella stessa transazione che ha creato il contratto (comportamento pre-Cancun preservato).
>
> Per "disattivare" un contratto in modo portabile, è preferibile usare una variabile di stato booleana e far sì che tutte le funzioni facciano revert se il contratto è disattivato. In questo modo il contratto rimanda indietro l'Ether immediatamente.

---

## Advanced Solidity: Vulnerabilities e Contract Upgrading

Affrontiamo ora due temi che separano il codice didattico dal codice production-ready: le **vulnerabilità tipiche** degli smart contract e le **strategie di aggiornamento** per contratti che, per natura, nascono immutabili. I due temi sono strettamente collegati: l'impossibilità di correggere un contratto dopo il deploy rende le vulnerabilità particolarmente dannose, e i pattern di upgrading sono nati proprio per mitigare questa rigidità — al prezzo, però, di introdurre nuove forme di centralizzazione e nuovi vettori di attacco.

> [!tip] Filosofia della sicurezza
>
> In Ethereum il codice è legge, ma la legge può contenere bachi. Scrivere smart contract sicuri significa anticipare i modi in cui un attaccante può manipolare il contesto di esecuzione (chi chiama, quando, con quale gas, con quali effetti collaterali) e progettare il codice perché non dipenda da invarianti che l'attaccante può violare.

---

## Vulnerabilità comuni

Prima di entrare nei singoli pattern di attacco è utile fissare alcune considerazioni generali, valide trasversalmente per qualsiasi contratto che gestisca valore o logica critica.

### Caveat generali

Due insidie ricorrenti, spesso sottovalutate, riguardano la **generazione di casualità** e il **costo delle view function**.

La prima questione nasce dal fatto che, in un sistema deterministico e replicato come l'EVM, non esiste una vera sorgente di casualità interna alla blockchain. Qualsiasi valore apparentemente casuale (hash di un blocco, timestamp, difficulty) è in realtà **manipolabile dai validatori**, che possono scegliere di non produrre il blocco se l'esito non è loro favorevole — o di ritardarne la pubblicazione per estrarre valore. Un contratto che dipenda da "casualità on-chain" per decisioni economicamente rilevanti (lotterie, estrazioni, distribuzione di premi) è vulnerabile per costruzione. Le soluzioni vere richiedono oracoli specializzati con schemi commit-reveal o VRF (Verifiable Random Functions) come Chainlink VRF.

La seconda questione è più sottile. Una funzione marcata `view` non modifica lo stato e, **se chiamata esternamente da fuori la blockchain** (ad esempio via `eth_call` da una DApp), non costa gas. Tuttavia, se la stessa funzione viene chiamata **da un'altra funzione on-chain**, il suo costo viene sommato al gas della transazione che la contiene. Una view function con loop non limitato su una struttura dati che cresce nel tempo può quindi diventare un **denial-of-service economico**: inizialmente gratuita, poi progressivamente più costosa, fino a superare il block gas limit.

> [!warning] Le view function non sono "gratis" in assoluto
>
> `view` garantisce solo che la funzione non scriva sullo stato. Non garantisce che il costo di lettura sia limitato. Se un altro contratto la chiama, paga l'esecuzione. Un attaccante può **far crescere volutamente** strutture dati iterate dalle view per trasformarle in bombe a orologeria.

> [!note] Riferimenti della sicurezza
>
> La guida ufficiale Ethereum sui disaster recovery plans e la sezione sicurezza degli smart contract è disponibile su `ethereum.org/developers/docs/smart-contracts/security`. Per esercitarsi sui pattern di attacco è storicamente utile **Ethernaut** (`ethernaut.openzeppelin.com`), una CTF di OpenZeppelin sui bug classici: leggermente datato, ma ancora ottimo per allenare l'istinto difensivo.

### Overflows

Gli overflow aritmetici sono stati a lungo il bug più classico di Solidity. In una `uint256` l'operazione `type(uint256).max + 1` tornava silenziosamente a `0`, con effetti disastrosi quando il valore rappresentava un saldo o un contatore critico. La libreria **SafeMath** di OpenZeppelin è nata proprio per fornire operazioni aritmetiche con controllo esplicito e revert in caso di overflow.

Dalla versione **0.8.0** del compilatore Solidity, il controllo di overflow/underflow è diventato **automatico** per tutte le operazioni aritmetiche standard. Il compilatore inserisce istruzioni di verifica che fanno revert della transazione se il risultato uscisse dai limiti del tipo. SafeMath rimane storicamente rilevante ma, in pratica, l'uso è diventato marginale: i contratti moderni possono fare affidamento sul controllo automatico, a meno che non sia esplicitamente necessario l'overflow silente (nel qual caso si usa un blocco `unchecked { ... }` per disattivarlo localmente e risparmiare gas).

> [!tip] Quando usare `unchecked`
>
> Il blocco `unchecked` serve quando si è **matematicamente certi** che l'overflow non possa avvenire (es. una variabile di loop limitata, un decremento protetto da un `require` precedente) e si vuole evitare il costo del check automatico. Usarlo per errore è esattamente il tipo di bug che il controllo automatico è stato introdotto per prevenire.

### Phishing tramite `tx.origin`

Solidity espone due variabili globali che a prima vista sembrano intercambiabili: `msg.sender` e `tx.origin`. La differenza è cruciale. `msg.sender` è l'indirizzo dell'**ultimo chiamante** — il contratto o l'EOA (Externally Owned Account) che ha invocato direttamente la funzione corrente. `tx.origin` è invece l'indirizzo dell'**EOA che ha firmato la transazione** all'origine dell'intera catena di chiamate.

Un controllo di autorizzazione basato su `tx.origin` è vulnerabile a un classico attacco **man-in-the-middle**: un contratto malevolo può indurre la vittima (che magari è l'owner di un contratto protetto) a interagire con sé, e poi, durante quella stessa transazione, invocare il contratto protetto. A quel punto `tx.origin` è ancora l'indirizzo della vittima (che ha firmato la transazione), quindi il controllo passa, anche se l'effettivo chiamante immediato (`msg.sender`) è il contratto malevolo.

![Schema dell'attacco di phishing basato su `tx.origin`: l'EOA della vittima resta `tx.origin` lungo tutta la catena di chiamate, quindi il controllo ingannevole passa nonostante il vero chiamante sia un contratto ostile.](images/mermaid-lezione-23-lab-advanced-solidity-vulnerabilities-e-upgrading-01.png)

> [!warning] Regola pratica
>
> **Non usare mai `tx.origin` per controlli di autorizzazione.** Usa sempre `msg.sender`. L'unico uso legittimo di `tx.origin` è il rifiuto deliberato di chiamate da parte di contratti (`require(tx.origin == msg.sender)`), pattern oggi considerato scarsamente utile perché fragile e anti-composizionale.

### Reentrancy

La reentrancy è probabilmente la vulnerabilità più famosa della storia di Ethereum — è il bug che nel 2016 portò al collasso di **The DAO** e alla hard fork che separò Ethereum da Ethereum Classic. L'essenza del problema è semplice: si verifica quando **una funzione (o una combinazione di funzioni) viene richiamata dall'interno della propria esecuzione**, prima che gli effetti della prima chiamata siano stati consolidati nello stato del contratto.

Il vettore tipico è una chiamata esterna a un contratto non fidato: l'EVM, per `.call()`, `send` o `transfer` verso un indirizzo di contratto, esegue il codice del **fallback** o della `receive` di quel contratto. Se il fallback a sua volta richiama la funzione originaria, e questa non ha ancora aggiornato lo stato che regola l'accesso, l'attaccante può ottenere più volte il risultato di un'operazione che avrebbe dovuto essere unica.

#### Esempio classico: withdraw vulnerabile

```solidity
function withdraw() public {
    require(shares[msg.sender] > 0);

    (bool success,) = msg.sender.call{value: shares[msg.sender]}("");

    if (success)
        shares[msg.sender] = 0;
}
```

Il problema è l'**ordine delle operazioni**. La funzione:

1. verifica che il chiamante abbia share positive,
2. invia l'ether corrispondente (che trigger-a eventualmente il fallback del chiamante),
3. **solo dopo** azzera le share.

Se il chiamante è un contratto il cui fallback chiama di nuovo `withdraw()`, al passo 1 della seconda invocazione il controllo `shares[msg.sender] > 0` passa ancora (le share non sono state azzerate), e il contratto invia di nuovo ether. Il processo si ripete fino a svuotare il contratto o esaurire il gas della transazione.

![Il flusso di una reentrancy classica: la chiamata esterna restituisce il controllo al contratto malevolo, che rientra nella funzione prima che lo stato sia aggiornato.](images/mermaid-lezione-23-lab-advanced-solidity-vulnerabilities-e-upgrading-02.png)

#### Mitigazioni

La difesa principale è il pattern **Checks-Effects-Interactions**: prima si fanno tutti i **controlli** (`require`), poi si aggiornano **gli effetti** sullo stato locale, e **solo alla fine** si eseguono le **interazioni** con contratti esterni. Riscritto correttamente, l'esempio diventa:

```solidity
function withdraw() public {
    uint256 amount = shares[msg.sender];
    require(amount > 0);
    shares[msg.sender] = 0;                          // Effect prima
    (bool success,) = msg.sender.call{value: amount}("");
    require(success);
}
```

Ora, anche se il fallback del chiamante richiama `withdraw`, il check fallisce perché `shares[msg.sender]` è già 0.

Esistono mitigazioni complementari, meno robuste ma utili come difesa in profondità:

- **Limitare il gas della chiamata esterna** (usando `send` o `transfer`, che forniscono solo 2300 gas, o fissando un gas cap in `call`). È una mitigazione storica che però non è sempre applicabile: dopo l'EIP-1884 il costo di alcune operazioni è aumentato e i 2300 gas di `transfer` possono non bastare per fallback legittimi, rompendo l'interoperabilità.
- **Lock non-reentrant** (reentrancy guard): un mutex booleano che viene alzato all'ingresso di funzioni sensibili e abbassato all'uscita. Se una chiamata esterna prova a rientrare, il mutex è alto e il require fallisce. OpenZeppelin fornisce `ReentrancyGuardTransient` (versione ottimizzata con storage transient EIP-1153) e `ReentrancyGuard`. **Attenzione a non rimanere bloccati per sempre**: il mutex deve essere abbassato in ogni percorso di uscita, inclusi i revert gestiti.

> [!example] Reentrancy guard con modifier
>
> ```solidity
> bool private locked;
> modifier nonReentrant() {
>     require(!locked, "Reentrant call");
>     locked = true;
>     _;
>     locked = false;
> }
> ```
>
> Applicando `nonReentrant` alla funzione `withdraw`, qualunque rientro trova `locked == true` e viene rifiutato.

> [!note] Approfondimenti
>
> Un'analisi dettagliata del TheDAO exploit si trova su `medium.com/@zhongqiangc/smart-contract-reentrancy-thedao-f2da1d25180c`. Una raccolta sistematica di attacchi reentrancy è mantenuta in `github.com/pcaversaccio/reentrancy-attacks`. Il guard ufficiale OpenZeppelin è su `github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/ReentrancyGuardTransient.sol`.

---

## Contract Upgrading

Gli smart contract su Ethereum sono **immutabili per design**: una volta deployato il bytecode, non esiste un'istruzione EVM per modificarlo. Questa proprietà è sia una forza (garantisce che il codice non possa essere alterato dopo il deploy) sia un limite (non permette di correggere bachi né di aggiungere funzionalità). Il **contract upgrading** è l'insieme dei pattern architetturali che consentono di aggirare questa rigidità quando è necessario.

### Perché (e perché no) aggiornare un contratto

I benefici dell'upgradability sono evidenti: permette di **correggere vulnerabilità o bachi** scoperti dopo il deploy, **aggiungere nuove funzionalità** che rispondano a requisiti emergenti, e predisporre **disaster recovery plans** per intervenire in caso di attacco o malfunzionamento grave.

Il costo è altrettanto concreto: un contratto upgradable è, per definizione, **meno immutabile**, quindi meno credibilmente neutrale. Introduce un potere centralizzato (chi controlla l'upgrade?) che può essere usato maliziosamente o compromesso. L'upgrade stesso è una superficie di attacco: un nuovo contratto logic può introdurre bug o backdoor non presenti nella versione originale.

La mitigazione standard è introdurre **timelock** (ritardi obbligatori tra annuncio e attivazione di un upgrade, per dare agli utenti tempo di uscire) e **multisig** (richiedere più firme per autorizzare l'upgrade, evitando single-point-of-failure sulla chiave del deployer). Il trade-off è evidente: i timelock rallentano le risposte in emergenza, i multisig aumentano il costo operativo. È un compromesso, non una soluzione.

> [!tip] L'upgradability come scelta politica
>
> Rendere un contratto upgradable è anche una dichiarazione di governance: chi può votare l'upgrade? Con quale maggioranza? Dopo quanto tempo? Molti protocolli DeFi hanno migrato nel tempo da multisig a DAO governance proprio per decentralizzare questo potere.

### Esempio guida della lezione

Come filo conduttore la lezione usa l'aggiunta di funzionalità di **"proper deactivation"** al posto di `selfdestruct` come disaster recovery plan: si parte dal contratto `Created.sol` e si trasforma in `CreatedSafe.sol`, ragionando su come far adottare la nuova logica senza rompere lo stato già esistente.

### Le quattro opzioni principali

Esistono due macrofamiglie di soluzioni — quelle **senza proxy** e quelle **con proxy** — per un totale di quattro pattern principali:

![Tassonomia delle strategie di upgrading: si parte dalla scelta se introdurre o meno un proxy, e all'interno di ciascuna famiglia si distinguono approcci monolitici e modulari.](images/mermaid-lezione-23-lab-advanced-solidity-vulnerabilities-e-upgrading-03.png)

#### Opzione 1 — Migration

Si crea una **nuova istanza** del contratto con la logica aggiornata e si **migrano i dati** dal vecchio al nuovo. È l'approccio più semplice concettualmente, ma impone che **tutti gli utenti passino al nuovo contratto**: ogni DApp, ogni wallet, ogni interazione esterna deve essere aggiornata al nuovo indirizzo. Rompe ogni integrazione on-chain che avesse hard-coded il vecchio indirizzo. Funziona bene per contratti di nicchia con pochi utenti coordinabili, male per protocolli con ampia adozione.

#### Opzione 2 — Separazione logic/state

Si divide il contratto in due: un **contratto di stato** (immutabile, contiene i dati) e un **contratto di logica** (mutabile, contiene il codice). Il contratto di stato espone getter/setter accessibili solo dal contratto di logica corrente, e mantiene un puntatore al contratto di logica attivo, aggiornabile dal proprietario.

Il vantaggio è che i dati non si spostano mai: lo stato rimane nello stesso indirizzo. Lo svantaggio è che **il caller interagisce con l'indirizzo della logica**, quindi un cambio di logica cambia l'indirizzo con cui l'utente interagisce — e le DApp devono aggiornarsi. È una mezza soluzione: risolve il problema della migrazione dati ma non quello dello stable address.

#### Opzione 3 — Proxy pattern

È l'approccio più diffuso nei protocolli moderni. Si usa un **proxy contract immutabile** che l'utente chiama sempre allo stesso indirizzo. Il proxy non contiene logica di business: contiene solo una **puntatore al contratto logic** e una funzione `fallback` che **delegate-call**-a al logic contract ogni invocazione ricevuta.

La chiave è `delegatecall`: a differenza di `call`, esegue il codice del callee **nel contesto (storage) del caller**. Quindi lo stato vive nel proxy, ma l'implementazione viene letta dal logic. Aggiornare il contratto significa cambiare il puntatore del proxy verso un nuovo logic contract.

![Pattern proxy: l'utente interagisce sempre con lo stesso indirizzo (il proxy), ma la logica eseguita è quella del contratto puntato, sostituibile dall'owner.](images/mermaid-lezione-23-lab-advanced-solidity-vulnerabilities-e-upgrading-04.png)

> [!definition] `delegatecall`
>
> Opcode EVM che esegue il codice di un altro contratto **nel contesto di storage, `msg.sender` e `msg.value` del caller**. A differenza di `call`, che esegue il callee nel proprio contesto, `delegatecall` tratta il codice del callee come una libreria: lo stato modificato è quello del caller. È il meccanismo fondamentale che rende possibile il pattern proxy.

L'implementazione di riferimento è `Proxy.sol` di OpenZeppelin, disponibile in `github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.8.2/contracts/proxy/Proxy.sol`. Un tutorial pratico è `jamesbachini.com/proxy-contracts-tutorial/`.

> [!warning] Storage collision
>
> Il punto più delicato del pattern proxy è l'**allineamento dello storage**: proxy e logic devono avere layout di storage compatibili, perché entrambi scrivono nello stesso storage (quello del proxy). Se il logic v2 aggiunge una variabile nel mezzo della lista, tutte le variabili successive "scorrono" e vengono sovrascritte/lette da slot sbagliati. Per questo OpenZeppelin impone un layout di storage **append-only** e usa slot deterministici (EIP-1967) per le variabili del proxy stesso (come l'indirizzo dell'implementazione), così da non collidere con quelle della logic.

#### Sintassi Solidity: `virtual`, `override`, `abstract`

Il pattern proxy usa intensivamente l'ereditarietà, quindi richiede familiarità con tre parole chiave:

| Parola chiave | Significato |
|---|---|
| `virtual` | Il metodo **può essere sovrascritto** da un contratto che eredita. |
| `override` | Il metodo **sta sovrascrivendo** un metodo `virtual` del contratto padre. |
| `abstract` | Il contratto **non può essere istanziato** direttamente perché ha funzioni/parametri non implementati; serve solo come base per sottoclassi. |

Il concetto di `abstract` è analogo a Java: un contratto che dichiara firme di funzioni senza implementazione, lasciando ai derivati il compito di completarlo.

#### Opzione 4 — Diamond pattern (EIP-2535)

Il pattern proxy standard ha un limite: **un solo logic contract** alla volta. Ma un logic contract è un singolo contratto Solidity, quindi è soggetto al **limite di dimensione del bytecode** (circa 24 KB per EIP-170). Protocolli grandi (DEX, lending, derivati) rischiano di sbattere contro questo soffitto.

Il **diamond pattern** (EIP-2535) generalizza il proxy: un unico contratto "diamond" (immutabile, con lo stato) delega a **più logic contracts**, detti **facets**. Ogni selector di funzione (i 4 byte che identificano una funzione nell'ABI) è mappato al facet che la implementa. Quando un utente chiama una funzione, il diamond consulta la mappa, individua il facet competente, e delegate-call-a ad esso.

![Pattern diamond: un unico indirizzo esposto all'utente, ma le funzioni sono implementate da più facet. La mappatura funzione → facet è aggiornabile, permettendo di sostituire, aggiungere o rimuovere facet nel tempo.](images/mermaid-lezione-23-lab-advanced-solidity-vulnerabilities-e-upgrading-05.png)

Il cuore del pattern è la **function-to-facet mapping**:

```solidity
mapping(bytes4 => address) facets;

// Esempio di mapping:
// (func1) e2532512 => 0x0b22380B7c423470...  (FacetA)
// (func2) b1e5392a => 0x0b22380B7c423470...  (FacetA)
// (func3) 1857ea99 => 0x501E5D8e2FBbBc8A...  (FacetB)
// (func4) 876e3abc => 0x501E5D8e2FBbBc8A...  (FacetB)
// (func5) 79d9df55 => 0x501E5D8e2FBbBc8A...  (FacetB)
// (func6) 0b7eac44 => 0x39555988230b4c87...  (FacetC)
// (func7) d86e6291 => 0x39555988230b4c87...  (FacetC)
```

Il diamond gestisce anche più **storage struct** dedicate (una per facet o gruppo di facet), tipicamente usando il pattern **Diamond Storage** per isolare gli slot di storage di ciascun facet ed evitare collisioni: ogni facet usa uno slot di storage calcolato come hash di una stringa unica, garantendo che facet diversi non si pestino i piedi.

> [!tip] Perché "diamond"
>
> Il nome richiama la forma dell'ereditarietà multipla: un singolo punto di ingresso (il diamond) si apre su molte facce (i facet). A differenza dell'ereditarietà multipla tradizionale, qui non c'è un unico albero di compilazione: i facet sono contratti separati, deployati indipendentemente, e la "composizione" avviene a runtime tramite la mappa di selector. Il risultato è massima modularità, al prezzo di una maggiore complessità di governance (ora bisogna gestire upgrade, aggiunte e rimozioni di facet).

> [!abstract] Sintesi dei quattro pattern
>
> | Opzione | Indirizzo stabile? | Migrazione dati? | Complessità | Limite dimensione |
> |---|---|---|---|---|
> | Migration | no | sì | bassa | nessuno |
> | Logic/state separation | no (cambia logic) | no | media | ~24 KB |
> | Proxy | **sì** | no | media | ~24 KB |
> | Diamond | **sì** | no | alta | **nessuno** (molti facet) |

---

## Mappa concettuale

![Struttura complessiva dei pattern di upgrading: da un lato i pattern di attacco e le relative difese, dall'altro l'evoluzione dei pattern architetturali per superare l'immutabilità degli smart contract.](images/mermaid-lezione-23-lab-advanced-solidity-vulnerabilities-e-upgrading-06.png)

---

## Risorse

- `https://solidity-by-example.org/` — esempi pratici per tutti i costrutti Solidity
- `https://cryptozombies.io/course/` — corso interattivo gamificato
- `ethereum.org/developers/docs/smart-contracts/security` — guida ufficiale Ethereum ai disaster recovery plans e sicurezza.
- `ethernaut.openzeppelin.com` — CTF di OpenZeppelin per esercitarsi sui bug classici.
