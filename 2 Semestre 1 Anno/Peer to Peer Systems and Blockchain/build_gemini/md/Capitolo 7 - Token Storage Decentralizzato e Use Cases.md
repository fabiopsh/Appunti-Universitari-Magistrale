# Capitolo 7 - Token, Storage Decentralizzato e Use Cases

## Fungible e Non Fungible Tokens: Standard ERC

La tokenizzazione rappresenta una delle applicazioni più trasformative della blockchain. Insieme a criptovalute, DeFi (*Decentralized Finance*), supply chain e identità digitale, i token costituiscono le cosiddette **killer application** delle blockchain. Questo capitolo analizza la distinzione fondamentale tra token fungibili e non fungibili, i meccanismi contrattuali che li implementano su Ethereum (standard ERC), lo storage decentralizzato tramite IPFS, e infine esplora alcune delle principali applicazioni reali degli smart contract.

---

### Coins e Token: una distinzione fondamentale

Prima di entrare nel merito degli standard, è necessario chiarire la differenza tra due termini spesso usati come sinonimi ma che indicano concetti distinti.

Un **digital coin** (*moneta digitale*) è un asset nativo della propria blockchain: bitcoin su Bitcoin, ether su Ethereum, ADA su Cardano, BNB su Binance, SOL su Solana. I coin svolgono le tre funzioni della moneta: mezzo di scambio, riserva di valore e unità di conto. Vengono inoltre utilizzati per ricompensare i nodi che garantiscono il funzionamento della rete.

Un **digital token** (*token digitale*), al contrario, è un asset non nativo creato sopra una blockchain esistente tramite smart contract. Questa dipendenza da un contratto spiega perché la stragrande maggioranza dei token sia implementata su Ethereum, che offre il runtime necessario. I token ereditano le proprietà di sicurezza e tracciabilità della blockchain sottostante, e la loro ragione d'esistenza è quasi sempre legata a un'applicazione decentralizzata specifica — una Dapp — all'interno del cui ecosistema assumono significato e valore.

Storicamente, i token hanno preceduto la blockchain: erano oggetti pseudo-monetari privi di framework legale, emessi da entità private per usi specifici. I gettoni dei casinò o le monete create dalle mining companies per i propri negozi aziendali (*company store*) ne sono esempi emblematici: avevano valore all'interno della comunità che ne accettava l'uso, ma nessuno al di fuori.

---

### Token Fungibili

> [!definition] Fungibilità
>
> Un asset è **fungibile** quando le sue unità sono identiche in natura e funzione: non esiste alcuna caratteristica distintiva tra un'unità e l'altra dello stesso tipo.

Le proprietà fondamentali dei token fungibili sono tre. L'**interscambiabilità** implica che ogni token sia sostituibile con qualsiasi altro token della stessa specie: il tuo biglietto da 20€ e il mio hanno lo stesso valore, così come un lingotto d'oro da 1 kg equivale a qualsiasi altro da 1 kg. Per le criptovalute questa proprietà è generalmente vera, ma con una sfumatura importante: ogni bitcoin ha la propria storia di transazioni on-chain, il che apre interrogativi sulla sua fungibilità assoluta. La **fusione** (*merging*) consente di sommare unità per ottenere valori aggregati. La **divisibilità** permette di trasferire frazioni di token, proprietà essenziale per le criptovalute dove si opera spesso con millesimi o microfraction.

#### Applicazioni dei token fungibili

I token fungibili trovano impiego in scenari economici diversi. Nelle **ICO** (*Initial Coin Offering*), le aziende emettono token per raccogliere fondi dagli investitori, garantendo che la standardizzazione li renda negoziabili. Nella **DeFi**, i token fungibili fungono da collaterale su piattaforme di lending e borrowing, da strumento di voto e governance nelle **DAO** (*Decentralized Autonomous Organization*), e da mezzo di scambio generico. Nell'industria **gaming**, sono usati come valuta in-game e per rappresentare attributi dei personaggi, permettendo economie interne alle piattaforme. Sulle piattaforme social, modellano sistemi di reputazione e incentivi.

---

### Token Non Fungibili (NFT)

> [!definition] Non Fungibilità
>
> Un **NFT** (*Non-Fungible Token*) è un asset unico: contiene informazioni o attributi che lo rendono impossibile da sostituire con un altro token della stessa categoria. Ogni NFT rappresenta un'entità intera, non frazionabile.

La distinzione visiva tra fungibile e non fungibile è immediata: due palline da baseball identiche prodotte in serie sono fungibili; una pallina firmata da Babe Ruth è non fungibile, perché quella firma la rende unica e irreplicabile. Analogamente, la Gioconda è non fungibile (un originale), mentre una maglietta con la stampa della Gioconda è fungibile (producibile in mille copie).

![Diagramma Mermaid](images/mermaid-lezione-22-fungible-e-non-fungible-tokens-erc-standards-01.png)
*Fig. — Tassonomia degli asset secondo fungibilità e tangibilità: i token intangibili fungibili includono criptovalute e carbon credit, quelli non fungibili includono arte digitale e copyright.*

Un NFT può rappresentare oggetti digitali unici come opere d'arte, oggetti in-game, domini .eth; asset fisici come immobili o opere d'arte reali (la tokenizzazione rende il trasferimento di proprietà più efficiente riducendo il rischio di frodi); oppure certificati di proprietà e identità. Il fenomeno dei **Beanie Babies** negli anni '90 anticipa molte dinamiche degli NFT: produzione limitata, ritiro deliberato di edizioni per creare scarsità, difetti intenzionali che generano edizioni ultra-rare. La psicologia del collezionismo è la stessa.

---

### Cryptographic Tokens e Standard ERC

I token crittografici implementati come smart contract ereditano le proprietà di tracciabilità, sicurezza e impossibilità di falsificazione della blockchain. Il settore è in piena espansione: i **colored coins** furono i primi cryptotoken sviluppati su Bitcoin; Ethereum rimane la piattaforma dominante per via degli smart contract, ma esistono ora piattaforme alternative specializzate.

#### Perché uno standard?

> [!tip] Il valore di uno standard
>
> Uno standard ERC garantisce ai developer che gli asset si comporteranno in modo prevedibile, e alle aziende che i propri token saranno compatibili con l'infrastruttura Ethereum esistente: wallet, exchange, marketplace.

**ERC** (*Ethereum Request for Comment*, o *Ethereum Request for Improvements*) è il formato con cui si propongono e approvano le specifiche degli smart contract. Uno standard ERC per i token definisce l'interfaccia che un contratto deve implementare: come vengono creati, trasferiti, mutati e distrutti i token. I tre standard principali sono:

| Standard | Tipo | Caso d'uso principale |
|---|---|---|
| **ERC-20** | Token fungibili | Criptovalute, governance, DeFi |
| **ERC-721** | Token non fungibili (NFT) | Arte digitale, oggetti da collezione, immobili |
| **ERC-1155** | Multi-token (FT + NFT) | Gaming, piattaforme con asset eterogenei |

---

### ERC-20: Standard per Token Fungibili

Lo standard ERC-20 fu proposto dal co-fondatore di Ethereum Vitalik Buterin nel novembre 2015. Definisce un insieme comune di funzioni che ogni token fungibile su Ethereum deve implementare, così da garantire l'interoperabilità con wallet, contratti e marketplace.

#### Struttura interna: il balance map

Il contratto ERC-20 mantiene internamente una struttura dati fondamentale: un mapping da indirizzi a saldi.

```
balanceOf: address → uint256
```

Il saldo di un indirizzo non è un numero astratto: dipende dal contratto specifico e può rappresentare unità fisiche, diritti, valori monetari o qualsiasi altra quantità che il contratto decida di modellare.

#### Funzioni obbligatorie

Le sei funzioni obbligatorie dello standard sono:

| Funzione | Descrizione |
|---|---|
| `totalSupply()` | Restituisce il totale di token attualmente esistenti nel contratto. Può essere fisso o variabile. |
| `balanceOf(address)` | Restituisce il saldo di token di un indirizzo specifico. |
| `transfer(address _to, uint256 _value)` | Trasferisce token dall'indirizzo del chiamante a `_to`. |
| `approve(address _spender, uint256 _value)` | Autorizza `_spender` a spendere al massimo `_value` token per conto del chiamante. |
| `allowance(address _owner, address _spender)` | Restituisce la quota corrente approvata da `_owner` per `_spender`. |
| `transferFrom(address _from, address _to, uint256 _value)` | Trasferisce token da `_from` a `_to` per conto di un delegato autorizzato. |

Oltre alle funzioni, lo standard definisce due **eventi** che devono essere emessi:
- `Transfer(address _from, address _to, uint256 _value)` — emesso a ogni trasferimento
- `Approval(address _owner, address _spender, uint256 _value)` — emesso a ogni approvazione

#### Campi opzionali

I tre campi opzionali migliorano l'usabilità del token:

- `name()`: nome human-readable, ad es. `"US Dollars"`
- `symbol()`: simbolo leggibile, ad es. `"USD"`
- `decimals()`: numero di cifre decimali per la rappresentazione visiva. Solidity non supporta i numeri decimali — lavora solo con interi — per cui si rappresenta un valore con moltiplicatori. Con `decimals = 18`, il valore `1000000000000000000` corrisponde a `1.0` token a schermo.

#### Meccanismo di trasferimento diretto

La funzione `transfer` implementa una transazione diretta in un solo passo: il proprietario del wallet invia token a un altro indirizzo, esattamente come una transazione cryptocurrency convenzionale.

> [!example] Transfer: Alice invia 10 token a Bob
>
> 1. Il wallet di Alice invia una transazione al contratto token, chiamando `transfer(BobAddress, 10)`
> 2. Il contratto aggiorna: `balanceOf[Alice] -= 10` e `balanceOf[Bob] += 10`
> 3. Viene emesso l'evento `Transfer(Alice, Bob, 10)` on-chain, utile per il logging

#### Meccanismo di delega (Allowance)

Il meccanismo di **allowance** risolve un problema pratico: in molti scenari (pagamenti ricorrenti, marketplace, DeFi) è necessario che una terza parte esegua transazioni per conto del proprietario, senza che il proprietario debba approvare ogni singola operazione.

![Diagramma Mermaid](images/mermaid-lezione-22-fungible-e-non-fungible-tokens-erc-standards-02.png)
*Fig. — Flusso del meccanismo allowance: il proprietario approva una quota, il delegato la utilizza con transferFrom.*

Il mapping interno che traccia le allowance è una struttura a due livelli:

```solidity
mapping(address => mapping(address => uint256)) public allowance;
```

La prima chiave è il proprietario, la seconda è lo spender autorizzato, il valore è la quota massima. In altri termini: `allowance[owner][spender]` = quanto lo spender può ancora spendere dal conto di owner.

> [!example] Esempio completo di allowance
>
> Alice ha 1000 token e vuole delegare Bob a spenderne al massimo 100.
> 1. Alice chiama `approve(Bob, 100)`
> 2. Bob verifica la quota con `allowance(Alice, Bob)` → restituisce 100
> 3. Bob preleva 50 token: `transferFrom(Alice, Bob, 50)` → la allowance scende a 50
> 4. Bob può continuare a prelevare fino a esaurire la quota di 100 token totali

#### L'interfaccia IERC20 e l'implementazione

L'interfaccia IERC20 formalizza in Solidity il contratto che ogni implementazione ERC-20 deve rispettare:

```solidity
// Funzioni opzionali
function name()     public view returns (string)  // optional
function symbol()   public view returns (string)  // optional
function decimals() public view returns (uint8)   // optional

// Funzioni obbligatorie
function totalSupply() public view returns (uint256)
function balanceOf(address _owner) public view returns (uint256 balance)
function transfer(address _to, uint256 _value) public returns (bool success)
function approve(address _spender, uint256 _value) public returns (bool success)
function allowance(address _owner, address _spender) public view returns (uint256 remaining)
function transferFrom(address _from, address _to, uint256 _value) public returns (bool success)

// Eventi
event Transfer(address indexed _from, address indexed _to, uint256 _value)
event Approval(address indexed _owner, address indexed _spender, uint256 _value)
```

Un'implementazione minimale del contratto ERC-20 è:

```solidity
pragma solidity ^0.8.7;
contract MyToken {
    string public name = "My Token";
    string public symbol = "MTK";
    uint8 public decimals = 18;
    uint public totalSupply = 100_000 * 10**decimals;
    mapping(address => uint) public balanceOf;
    mapping(address => mapping(address => uint)) public allowance;

    event Transfer(address indexed _from, address indexed _to, uint256 _value);
    event Approval(address indexed _owner, address indexed _spender, uint256 _value);

    function transfer(address _to, uint256 _value) public returns (bool success) {
        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        emit Transfer(msg.sender, _to, _value);
        return true;
    }

    function approve(address _spender, uint256 _value) public returns (bool success) {
        allowance[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }

    function transferFrom(address _from, address _to, uint256 _value)
            public returns (bool success) {
        require(allowance[_from][msg.sender] >= _value);
        balanceOf[_from] -= _value;
        balanceOf[_to] += _value;
        emit Transfer(_from, _to, _value);
        allowance[_from][msg.sender] -= _value;
        return true;
    }
}
```

> [!warning] Bug nella slide originale
>
> Il codice presentato a lezione per `transferFrom` contiene un errore: `balanceOf[_from] += _value` invece di `-= _value`. La versione corretta sottrae il valore dal saldo del mittente e lo aggiunge al destinatario.

---

### Implementare i Token in Solidity

#### Contratti come classi, istanze e deployment

In Solidity, un contratto è concettualmente equivalente a una classe in un linguaggio orientato agli oggetti. Il codice del contratto definisce la struttura; l'**istanza** viene creata quando il contratto viene deployato sulla blockchain tramite una transazione, a un determinato indirizzo. Il creator può essere sia un external account che un altro contratto (come mostrato nel pattern *Fabric* che istanzia token dinamicamente).

Una volta che un contratto crea un'istanza di un altro contratto tramite `new`, l'istanza risultante può essere usata per invocare le funzioni pubbliche dell'altro contratto:

```solidity
Token token = new Token(_name);   // deployment + riferimento
token.name();                     // invocazione funzione pubblica
```

#### Ereditarietà

Solidity supporta l'ereditarietà in stile OOP. Un contratto figlio eredita tutte le variabili di stato e le funzioni non dichiarate `private` dal contratto padre. Le variabili e funzioni `internal` sono accessibili nel contratto e nei derivati; quelle `private` restano confinate al contratto in cui sono dichiarate, rafforzando l'incapsulamento.

Le funzioni dichiarate `virtual` nel padre possono essere sovrascritte nel figlio con `override`:

```solidity
contract Foo {
    function calculate(uint x, uint y) public virtual pure returns (uint) {
        return x + y;
    }
}
contract Bar is Foo {
    function calculate(uint x, uint y) public override pure returns (uint) {
        return x - y;
    }
}
```

#### Interfacce

Le **interfacce** in Solidity sono blueprints puri: dichiarano le firme delle funzioni senza implementarle e senza variabili di stato. Sono lo strumento naturale per descrivere standard come ERC-20 ed ERC-721, e possono ereditare da altre interfacce.

#### OpenZeppelin: non reinventare la ruota

> [!tip] OpenZeppelin
>
> OpenZeppelin (https://openzeppelin.com) è un SDK open source per lo sviluppo sicuro di smart contract. Il codice è sottoposto ad auditing continuo dalla community e usato in circa 3000 progetti blockchain. Fornisce template pronti per ERC-20, ERC-721 ed ERC-1155 importabili direttamente.

```solidity
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
contract MyToken is ERC20 {
    constructor() ERC20("MyToken", "MTK") {
        _mint(msg.sender, 1000);
    }
}
```

`MyToken` è un contratto figlio di `ERC20` di OpenZeppelin, ne eredita tutte le funzioni. Il costruttore del padre richiede nome e simbolo del token, che devono essere trasmessi dal figlio. La funzione `_mint` crea token dal nulla e li assegna all'indirizzo specificato, incrementando di conseguenza il `totalSupply`.

---

### ERC-721: Standard per NFT

Lo standard ERC-721 fu proposto nel gennaio 2018. La differenza architetturale rispetto a ERC-20 è fondamentale: mentre ERC-20 mappa **indirizzi → quantità**, ERC-721 mappa **ID unici → proprietari**.

> [!definition] tokenId in ERC-721
>
> Ogni NFT è identificato da un `uint256 tokenId`. La coppia `(contract address, tokenId)` deve essere **globalmente unica**: il tokenId è univoco all'interno di un contratto. Due contratti ERC-721 diversi possono avere token con lo stesso ID numerico, ma non rappresentano lo stesso asset.

L'interfaccia ERC-721 offre funzionalità analoghe a ERC-20 ma adattate alla gestione di token unici:

```solidity
function balanceOf(address _owner) external view returns (uint256);
function ownerOf(uint256 _tokenId) external view returns (address);
function safeTransferFrom(address _from, address _to, uint256 _tokenId, bytes data) external payable;
function safeTransferFrom(address _from, address _to, uint256 _tokenId) external payable;
function transferFrom(address _from, address _to, uint256 _tokenId) external payable;
function approve(address _approved, uint256 _tokenId) external payable;
function setApprovalForAll(address _operator, bool _approved) external;
function getApproved(uint256 _tokenId) external view returns (address);
function isApprovedForAll(address _owner, address _operator) external view returns (bool);
```

#### safeTransferFrom: perché esiste

La funzione `transferFrom` standard presenta un problema critico: trasferisce il token senza verificare se il contratto destinatario sia in grado di gestire NFT. Se l'indirizzo `_to` è uno smart contract che non implementa il supporto ERC-721, il token viene inviato e si blocca permanentemente, irrecuperabile.

Per questo motivo esiste `safeTransferFrom`, che aggiunge un controllo:
1. Se `_to` è un contratto, chiama `onERC721Received(...)` su di esso
2. Se il contratto non implementa correttamente questa funzione (cioè non "riconosce" il token ricevuto), la transazione viene revertita
3. Il trasferimento avviene solo se il destinatario dimostra di saper gestire NFT

> [!warning] Gli NFT sono preziosi
>
> Usare `transferFrom` invece di `safeTransferFrom` verso un contratto sconosciuto è rischioso: se il contratto destinatario non supporta ERC-721, l'NFT va perso per sempre. Preferire sempre `safeTransferFrom` quando il destinatario potrebbe essere un contratto.

---

### Metadata degli NFT

Un NFT non è solo un ID on-chain: il suo valore deriva dai **metadata** associati, ovvero le informazioni che descrivono cosa rappresenta.

#### La struttura dei metadata

I metadati tipici di un NFT includono:

| Campo | Significato |
|---|---|
| `name` | Nome dell'NFT (es. "Cool Ape #123") |
| `description` | Descrizione testuale |
| `image` | Link all'immagine (IPFS o HTTP) |
| `attributes` | Array di trait_type/value per caratteristiche specifiche |
| `unlockable_content` | Contenuto accessibile solo al proprietario |
| `royalty` | Percentuale di royalty per rivendite future |
| `supply` | Quasi sempre 1 per gli NFT |

#### tokenURI: il collegamento tra on-chain e metadata

La funzione `tokenURI(uint256 tokenId)` è il punto di accesso ai metadata: dato un tokenId, restituisce un URI che punta a un file JSON. Questo URI può essere un URL HTTP (`https://my-nft-site.com/metadata/123.json`) oppure un link IPFS (`ipfs://Qm.../123.json`). Il file JSON contiene a sua volta ulteriori link, tra cui il link all'immagine vera e propria.

![Schema del flusso NFT Image → JSON Metadata → Traits & Attributes](images/lezione-22-fungible-e-non-fungible-tokens-erc-standards-img-01.jpg)
*Fig. — Il flusso dei metadata di un NFT: la `tokenURI` punta al JSON, che contiene il link IPFS all'immagine e l'array di attributi usati da marketplace e sistemi per filtrare e calcolare la rarità.*

#### Perché gli attributi se c'è l'immagine?

L'immagine è per gli umani; gli attributi sono per le macchine. I marketplace come OpenSea usano gli attributi per permettere il **filtro** (*"solo NFT con fur dorata"*), il **calcolo della rarità** (*se solo l'1% ha "Laser Eyes", quell'attributo è molto raro e aumenta il valore*) e la **logica di gioco** (*uno Strength di 85 può influenzare il gameplay*). Senza attributi strutturati, un marketplace potrebbe solo mostrare le immagini, non filtrarle.

#### On-chain vs Off-chain: dove archiviare i metadata?

Archiviare i metadata direttamente on-chain è possibile ma costosissimo e raramente raccomandato. Si fa solo quando:
- L'informazione deve persistere indipendentemente dall'esistenza del sito originale (arte digitale destinata a durare secoli)
- La logica del contratto deve accedere ai metadata (es. l'età dei CryptoKitties influenza la velocità di riproduzione)

La soluzione off-chain prevalente è l'**IPFS** (*InterPlanetary File System*), una rete peer-to-peer decentralizzata dove i contenuti sono distribuiti su più nodi e indirizzati per contenuto (non per posizione). L'alternativa cloud (AWS, Google Cloud) esiste ma contraddice lo spirito decentralizzato della blockchain.

#### Royalties

Le royalties permettono all'autore originale di un NFT di ricevere una percentuale automatica su ogni rivendita futura, senza dover fare nulla. Il contratto traccia la percentuale scelta dall'artista e, ogni volta che l'NFT cambia mano, invia automaticamente la quota al wallet del creatore.

![Infografica sulle ongoing royalties con NFT](images/lezione-22-fungible-e-non-fungible-tokens-erc-standards-img-02.jpg)
*Fig. — Il meccanismo delle royalties: Alice crea e vende NFT #123 per 1 ETH con royalty del 5%. Ad ogni rivendita futura (10 ETH, 10 ETH, 20 ETH), Alice riceve automaticamente il 5% — rispettivamente 0.05, 0.5, 0.5, 1 ETH — senza alcuna azione da parte sua.*

#### Unlockable Content

L'*unlockable content* è contenuto visibile o accessibile solo al proprietario corrente dell'NFT: video esclusivi, documenti privati, codici di attivazione, access key per community ristrette. L'accesso si sposta automaticamente con il token quando viene trasferito.

Il flusso di verifica che una piattaforma deve implementare è:

![Diagramma Mermaid](images/mermaid-lezione-22-fungible-e-non-fungible-tokens-erc-standards-03.png)
*Fig. — Flusso di verifica per l'unlockable content: la piattaforma chiama `ownerOf(tokenId)` on-chain e confronta il risultato con il wallet connesso dall'utente.*

---

### ERC-20 vs ERC-721: il confronto strutturale

La differenza architetturale tra i due standard si riassume in come viene organizzato il registro interno:

![Diagramma Mermaid](images/mermaid-lezione-22-fungible-e-non-fungible-tokens-erc-standards-04.png)
*Fig. — ERC-20 mappa indirizzi a quantità (fungibile); ERC-721 mappa ID unici a proprietari (non fungibile).*

---

### ERC-1155: Multi-Token Standard

Lo standard ERC-1155 fu proposto dal CTO di Enjin nel 2018 con un obiettivo preciso: **ridurre il volume di transazioni e i costi** combinando in un unico contratto le funzionalità di ERC-20 e ERC-721.

> [!definition] ERC-1155
>
> Un singolo contratto ERC-1155 può gestire contemporaneamente token fungibili (come ERC-20) e token non fungibili (come ERC-721), supportando il **batch transfer** (trasferimento di più token in una sola transazione) e includendo meccanismi di safe transfer per prevenire perdite.

Il confronto tra ERC-721 ed ERC-1155 evidenzia i vantaggi di quest'ultimo:

| Caratteristica | ERC-721 | ERC-1155 |
|---|---|---|
| Tipi di token supportati | Solo NFT | FT e NFT |
| Smart contract richiesti | Uno per ogni tipo di token | Uno solo per tutti i tipi |
| Batch transfer | Non supportato | Supportato (meno gas, meno transazioni) |
| Safe transfer | No recovery se indirizzo sbagliato | Verifica + possibilità di recovery |

#### Applicazioni di ERC-1155

Il gaming è il caso d'uso principale. **Enjin Platform** usa ERC-1155 per creare asset di gioco — armi, scudi, oggetti — gestibili in un unico contratto condiviso tra più giochi. **The Sandbox** usa ERC-1155 per terreni, edifici e attrezzature nel suo metaverso. **Rarible** lo usa per supportare sia FT che NFT sulla stessa piattaforma, aumentando la flessibilità per artisti e collezionisti.

---

### La "giungla" degli standard ERC

> [!note] Un ecosistema in espansione
>
> ERC-20, ERC-721 ed ERC-1155 sono i principali standard, ma l'ecosistema Ethereum ne conta molti altri: ERC-777 (valuta Ethereum-based), ERC-827 (trasferimento a terze parti), ERC-884 (stock tokenization), ERC-1400/1404 (security token), ERC-725 (identità digitale), ERC-223 (European Research Council standard). La proliferazione di standard riflette la ricchezza e complessità degli use case che la tokenizzazione rende possibili.

## IPFS: Interplanetary File System

### Il Web centralizzato e il problema della localizzazione

Il Web così come lo conosciamo oggi si regge su un modello **location based**: quando scriviamo `http://sito.com/image.jpg` non stiamo chiedendo "voglio quella specifica immagine", bensì "contatta la macchina che risponde a `sito.com` e chiedigli il file `image.jpg`". L'indirizzo HTTP punta cioè a un **luogo** della rete — un dominio risolto in un indirizzo IP, che a sua volta identifica una macchina fisica. La conseguenza è duplice: il contenuto esiste solo fintanto che quel server è raggiungibile, e l'intero modello è fragile rispetto alla censura, ai guasti e alla centralizzazione delle infrastrutture.

> [!warning] Il problema della censura
>
> Se un governo o un provider decide di bloccare un dominio o un indirizzo IP, il contenuto diventa irraggiungibile per intere porzioni di rete, anche se copie dello stesso file sono fisicamente presenti su milioni di macchine sparse nel mondo. Il legame forte fra **contenuto** e **luogo** è ciò che rende possibile la censura su scala.

C'è inoltre un problema più sottile di *discovery*: immagina che Mary voglia una certa immagine e che Bob, sulla stessa rete locale, ce l'abbia già sul disco. Nel modello HTTP, Mary non ha alcun modo di sapere che il file è a due metri da lei: deve per forza contattare il web server d'origine, magari dall'altra parte del mondo. Manca un meccanismo che permetta di **recuperare il contenuto da dove esso si trova**, invece che da dove è stato pubblicato.

#### Dal Web location-based al Web content-based

L'idea di IPFS è ribaltare la prospettiva: invece di indirizzare il *contenitore* (il server), si indirizza direttamente il *contenuto*. Non ci interessa sapere dove un file è ospitato, ci interessa solo **che cosa è** quel file. Se riusciamo a dare a ogni file un nome univoco derivato dal suo contenuto, allora la rete può occuparsi autonomamente di cercarlo dove esso si trova, replicarlo, servirlo dal nodo più vicino.

> [!tip] Intuizione chiave: content addressing
>
> In un sistema **content-addressed**, il nome di un file *è* il file — nel senso che è una funzione univoca dei suoi bit. Due file identici hanno lo stesso nome, ovunque essi siano; un file manomesso anche in un singolo bit ha un nome diverso. La localizzazione diventa un problema di rete, non di design del protocollo.

---

### IPFS: cos'è e da dove viene

IPFS (**InterPlanetary File System**) è un protocollo peer-to-peer per lo storage distribuito dei contenuti del Web, sviluppato da **Protocol Labs**. Lo slogan canonico, tratto dal white paper di Juan Benet del 2013, lo descrive come un "Content Addressed, Versioned, P2P File System". Il contributo di IPFS, secondo lo stesso Benet, non è inventare nuove tecniche, ma *combinare* in un unico sistema coerente idee già collaudate nel mondo peer-to-peer.

> [!info] L'ecosistema di Protocol Labs
>
> - **IPFS** — protocollo P2P content-based, alternativa a HTTP per lo scambio di contenuti.
> - **Filecoin** — rete di storage decentralizzata con un mercato basato su criptovaluta, costruita *sopra* IPFS per risolvere il problema degli incentivi allo storage.
> - **libp2p** — libreria modulare di rete nata come sotto-progetto di IPFS e poi diventata indipendente, usata da molti altri progetti.

Le idee che IPFS riprende e integra sono:

| Componente | Ispirazione |
|---|---|
| Routing | DHT (con miglioramenti da **S/Kademlia** per la sicurezza e **Coral sloppy DHT** per la performance) |
| Strutture dati | **Merkle DAG** (da Git e dai Merkle tree crittografici) |
| Scambio di blocchi | **BitTorrent**, adattato nel protocollo **Bitswap** |
| Versionamento | **Git** (version control system) |
| Namespace auto-certificante | **SFS** (Self-Certified File System) |

Nessuno di questi è un nodo "privilegiato": la rete IPFS è piatta, ogni peer memorizza oggetti nel proprio store locale e si connette ad altri peer per trasferire blocchi. L'identificazione dei contenuti è **content-based tramite hash crittografico sicuro**, lo scambio è peer-to-peer in stile BitTorrent, l'organizzazione dei file segue un **DAG di Merkle** che permette al tempo stesso verifica crittografica, deduplicazione e versionamento.

---

### Lo stack di IPFS a colpo d'occhio

Prima di entrare nei dettagli, è utile avere in mente l'architettura a livelli di IPFS. Il sistema si presenta come uno stack, in cui ogni livello si appoggia a quello sottostante e risolve un problema distinto.

![Diagramma Mermaid](images/mermaid-lezione-24-ipfs-interplanetary-file-system-01.png)
*Fig. — Lo stack IPFS: il livello più basso trasporta i dati (network, routing, exchange), quello intermedio li definisce (Merkle-DAG, naming), quello superiore li usa (applicazioni).*

Tre blocchi logici emergono chiaramente. In basso troviamo **Transporting Data**, il compito di muovere bit tra peer: network (libp2p), routing (DHT), exchange (Bitswap). Al centro **Defining Data**, dove i bit diventano strutture identificabili: Merkle-DAG e naming (IPNS). In cima **Using Data**, dove le applicazioni si appoggiano a tutto il resto.

---

### Content addressing: l'hashing come indirizzo

L'idea fondativa di IPFS è trasformare ogni pezzo di contenuto in un identificatore derivato matematicamente dai suoi bit. Quando carichi una foto su IPFS, accade questo: l'immagine viene convertita in raw data (una sequenza di byte), e su questi byte viene calcolato un **hash crittografico sicuro** — per default **SHA-256**, ma l'architettura supporta esplicitamente l'uso di altri algoritmi (e vedremo fra poco perché questa flessibilità è cruciale). Il digest risultante diventa l'etichetta univoca del contenuto.

> [!definition] Hash crittografico come indirizzo
>
> Un hash crittografico è una funzione che mappa input di qualsiasi lunghezza in output di lunghezza fissa (256 bit per SHA-256), con tre proprietà fondamentali: **tamper-freeness** (cambiare un bit dell'input cambia drasticamente l'output), **verifiability** (chiunque può ricalcolare l'hash e verificare l'integrità del dato) e **security** (non è possibile risalire all'input dall'output).

Queste tre proprietà si traducono direttamente in tre garanzie di IPFS. La prima è **l'auto-certificazione**: se Bob ti invia un file dichiarando che ha un certo CID, basta ricalcolare l'hash per verificare che non sia stato manomesso — non serve fidarsi di Bob. La seconda è **l'integrità end-to-end**: se anche un singolo pixel di una foto viene modificato, il suo hash cambia completamente, quindi il CID corrispondente è diverso. La terza è **la robustezza contro la manipolazione**: non esistendo un modo efficiente per costruire un file diverso con lo stesso hash, IPFS è di fatto un file system a prova di tampering.

#### Dal digest al CID (Content Identifier)

Il digest da solo, però, non basta. Per poter evolvere l'algoritmo di hashing nel tempo, supportare formati di codifica diversi e permettere a software differenti di interpretare correttamente i dati, IPFS non usa *l'hash puro* come indirizzo: lo avvolge in una struttura chiamata **CID (Content Identifier)**.

> [!definition] Content Identifier (CID)
>
> Un CID è un'identificazione **self-describing** del contenuto. Contiene:
>
> - **l'hash del contenuto** — che identifica *cosa* è il dato;
> - **metadata** che descrivono *come* interpretare/decodificare il dato (quale algoritmo di hash, quale codifica, quale formato di serializzazione).
>
> Il CID **non** indica dove il contenuto è memorizzato: non è un puntatore di rete, è un'"impronta digitale" auto-descrittiva.

Nelle versioni legacy, i CID cominciano con il prefisso `Qm…` (es. `QmPK1s3pNYLi9ERiq3BDxKa4XosgWwFRQUydHUtz4YgpqB`). Le versioni moderne (CIDv1) hanno una struttura più flessibile e ricca, che analizzeremo a breve.

---

### Il progetto Multiformat

La scelta di includere i metadata dentro il CID nasce da un'esigenza molto concreta di **evoluzione del software**. Se hard-codifichi SHA-256 ovunque nel tuo codice, il giorno in cui SHA-256 viene rotto (come è successo a MD5, e come potrebbe succedere domani con l'arrivo di computer più potenti o con attacchi crittografici imprevisti) devi riscrivere e ridistribuire tutto lo stack. Tool, applicazioni e script avranno fatto assunzioni *implicite* sulla lunghezza del digest, sul formato dell'identificatore, sul protocollo di rete. È un problema analogo al millennium bug.

> [!tip] L'insight dietro il Multiformat
>
> Invece di assumere un formato fisso, ogni valore trasporta con sé una descrizione di *quale* formato usa. Un'applicazione che riceve un dato lo interpreta leggendo prima i metadata, poi il valore. Così l'evoluzione dei protocolli di hashing, di codifica o di rete non richiede di modificare il codice delle applicazioni: basta che esse leggano correttamente il prefisso auto-descrittivo.

Il Multiformat è una **collezione di standard** nati all'interno di IPFS e poi diventati indipendenti. I protocolli attuali sono:

| Protocollo | Cosa descrive |
|---|---|
| **multihash** | hash auto-descrittivi (quale funzione di hash, quale lunghezza) |
| **multibase** | codifica auto-descrittiva di stringhe (base32, base58, base64...) |
| **multicodec** | formato di serializzazione auto-descrittivo |
| **multiaddr** | indirizzi di rete auto-descrittivi |

#### Multibase: come leggere una stringa

Quando un CID viene presentato come stringa leggibile (per copiarlo in un URL, incollarlo in chat, stamparlo su una slide), i suoi byte binari devono essere codificati in caratteri alfanumerici. Esistono molte basi possibili — Base32, Base58 (la stessa usata da Bitcoin), Base64 — e Multibase risolve il problema di non dover sapere a priori quale è stata usata: **un singolo carattere di prefisso** identifica la codifica, e un'applicazione può decodificare qualsiasi stringa senza ipotesi hard-coded.

#### Multihash: come leggere un digest

Un multihash non memorizza soltanto il valore dell'hash, ma anche **quale funzione di hash è stata usata** e **quale lunghezza ha il digest**. Il formato è compatto:

```
<hash-function-code> <digest-length> <digest-bytes>
```

Anche se oggi il sistema usa di fatto solo SHA-256, il formato multihash segnala alle applicazioni che domani potrebbe essere qualsiasi altra cosa. Tool, applicazioni e script non devono fare assunzioni sulla lunghezza: la leggono direttamente dal valore. Il risultato è che **la stragrande maggioranza del software non richiede alcun upgrade** quando l'algoritmo di hash cambia — un risparmio enorme di ore di engineering su larga scala.

#### CID: tutto il Multiformat messo insieme

Un CIDv1 mette insieme tutti questi elementi: una versione, un multicodec che descrive il formato di serializzazione del contenuto, un multihash (con codice della funzione di hash, lunghezza e valore). La stringa visibile all'utente è poi passata attraverso multibase per essere codificata in caratteri stampabili.

![Diagramma Mermaid](images/mermaid-lezione-24-ipfs-interplanetary-file-system-02.png)
*Fig. — Struttura a byte di un CIDv1 (dag-pb, sha2-256): versione, multicodec, funzione di hash, lunghezza, digest.*

Il CID completo è quindi un flusso di byte che viene poi raggruppato in chunk da 5 bit e codificato — tramite multibase — in caratteri Base32 (o altra base). Il carattere di prefisso della stringa finale identifica la base usata, completando il quadro auto-descrittivo.

> [!note] Perché 5 bit per Base32
>
> Base32 usa 32 simboli distinti, cioè $2^5$. Ogni gruppo di 5 bit del flusso binario diventa un carattere dell'alfabeto Base32. Si noti che i confini dei campi originari (versione, multicodec, ecc.) **non** sono allineati ai 5 bit: nella stringa Base32 finale la struttura a byte non è più visibile, si può recuperare solo dopo aver decodificato.

---

### IPLD e il Merkle DAG

Fin qui abbiamo parlato di file singoli. Ma IPFS deve gestire anche strutture più complesse — directory, collezioni di blocchi, versioni successive di uno stesso documento — e lo fa attraverso un livello chiamato **IPLD (InterPlanetary Linked Data)**, il modello dati di IPFS.

> [!definition] IPLD e Merkle DAG
>
> IPLD trasforma tutti i dati in un **grafo di nodi collegati da CID**. Ogni pezzo di dato è un nodo; i nodi sono connessi da *link*, dove un link è semplicemente il CID del nodo di destinazione. L'insieme forma un **Merkle DAG (Directed Acyclic Graph)**: un grafo orientato aciclico in cui ogni nodo contiene, all'interno dei propri dati, i digest dei nodi figli.

L'aggettivo "Merkle" viene dalle classiche strutture crittografiche di Ralph Merkle: **il contenuto di cui si calcola l'hash contiene i digest di altri contenuti**, quindi ogni nodo autentica ricorsivamente tutti i suoi discendenti. L'hash della radice è sufficiente per verificare l'integrità dell'intera struttura.

#### Come funziona in concreto

Quando aggiungi un file a IPFS, il sistema lo divide in **chunk** (blocchi di dimensione fissa o variabile). Per ogni chunk calcola un digest e crea un CID. Poi costruisce un nodo "indice" che contiene i CID dei chunk in ordine, e ne calcola a sua volta il CID: questo è il **base CID** del file.

![Diagramma Mermaid](images/mermaid-lezione-24-ipfs-interplanetary-file-system-03.png)
*Fig. — Costruzione del Merkle DAG di un file: chunking, hashing, generazione dei CID dei figli e del CID radice.*

#### Deduplicazione automatica

Una conseguenza bellissima di questa struttura è la **deduplicazione**: lo stesso contenuto è memorizzato **una sola volta** nell'intera rete. Se due foto condividono gli stessi chunk — perché sono simili, perché hanno la stessa intestazione, perché qualcuno ha modificato solo una piccola parte dell'immagine — la parte comune ha lo stesso CID in entrambi i file, quindi non viene duplicata.

L'esempio limite è evocativo: immagina che ogni lettera dell'alfabeto abbia il suo CID e sia memorizzata una sola volta nel sistema. Un intero libro potrebbe essere rappresentato *componendo i CID delle lettere* — ovviamente in pratica si lavora a grana più grossa, ma l'idea è quella.

Il diagramma seguente mostra concretamente come IPLD organizza i dati in un Merkle DAG, evidenziando il caso in cui un nodo (qui `CID_D`) è **condiviso** fra più genitori — ed è proprio questo che rende la struttura un DAG e non un semplice albero.

![Merkle DAG in IPFS (IPLD) — nodi che contengono link ai figli tramite CID, con un nodo condiviso fra due genitori](images/lezione-24-ipfs-interplanetary-file-system-img-01.jpg)
*Fig. — Merkle DAG in IPFS (IPLD). `CID_root` contiene i CID dei figli `CID_A` e `CID_B` (entrambe directory). Il file `CID_D` è referenziato sia da `CID_A` sia da `CID_B`: essendo identificato dall'hash del suo contenuto, viene memorizzato una sola volta ma puntato da più genitori. A destra, l'esempio del payload serializzato di `CID_B`, che elenca i suoi figli come coppie `(name, link)`.*

#### Proprietà del Merkle DAG

La struttura ha tre proprietà fondamentali che conviene tenere a mente.

**Il CID di un nodo dipende dai CID di tutti i suoi discendenti.** Se fotoritocchi anche un solo pixel di un'immagine contenuta in una directory, il CID del chunk modificato cambia; di conseguenza cambia il CID del nodo che lo contiene; poi cambia il CID della directory; e così via fino alla radice. La modifica **si propaga verso gli antenati**, mai verso i fratelli.

**La costruzione avviene sempre dal basso verso l'alto.** Non si può creare un nodo padre finché i CID dei figli non sono noti. Questa è anche la ragione strutturale per cui il DAG non può contenere cicli: sarebbe una dipendenza circolare dei CID.

**Una modifica in un ramo non tocca gli altri rami.** Se cambi un file in `dir/foto/gatto.jpg`, i CID di tutti i file dentro `dir/foto/` vengono ricalcolati solo per il ramo interessato; gli altri file della directory mantengono invariato il loro CID. È la stessa proprietà che in Git permette di identificare in modo compatto un commit e di verificare rapidamente l'identità di due sottocartelle.

> [!example] Verifica di due directory
>
> Hai fatto una copia di backup di una directory durante un lavoro di editing, mesi fa. Oggi ritrovi le due copie e vuoi sapere se hanno lo stesso contenuto. Invece di confrontare file per file, calcoli il Merkle DAG di ciascuna: se i CID delle radici coincidono, le due directory sono *identiche* bit per bit — puoi cancellare una delle due in tutta sicurezza e liberare spazio. È lo stesso principio con cui Git confronta due commit.

#### Ogni nodo può essere radice

Il Merkle DAG è **ricorsivo**: ogni sottografo è a sua volta un DAG completo, con una sua radice (il suo nodo di partenza) e un suo CID. Questo apre possibilità espressive molto potenti.

> [!tip] DAG come strutture componibili
>
> - Puoi **condividere un sottografo** semplicemente inviando il CID della sua radice — il destinatario non ha bisogno del contesto del grafo più grande.
> - Puoi **incorporare lo stesso sottografo in DAG diversi**: il CID del sottografo dipende solo dai suoi discendenti, non dai suoi antenati. Lo stesso file, lo stesso chunk, la stessa directory possono apparire in posizioni diverse di DAG diversi senza essere duplicati.

Questa proprietà è la base strutturale su cui IPFS costruisce file system versionati, blockchain e, più in generale, qualunque sistema che abbia bisogno di memorizzare dati autenticati, componibili e condivisibili.

---

### Il livello di rete: libp2p

Passiamo dalla struttura dei dati al modo in cui i nodi si parlano. Il livello di rete di IPFS è implementato da **libp2p**, una libreria modulare nata come sotto-progetto di IPFS e oggi usata da molti altri progetti peer-to-peer (tra cui Ethereum 2.0, Polkadot, Filecoin).

Libp2p si occupa di tutto ciò che serve per mettere in comunicazione due nodi senza fare assunzioni sulla rete sottostante. Le funzionalità principali sono:

| Funzionalità | Cosa fa |
|---|---|
| **Peer discovery** | trovare altri nodi tramite Kademlia DHT, mDNS, bootstrap node |
| **Transport abstraction** | supportare TCP, QUIC, WebSocket, WebRTC in modo trasparente |
| **Connection establishment** | aprire connessioni anche attraverso NAT e firewall (hole punching, relay) |
| **Secure communication** | cifratura e autenticazione (Noise, TLS) — i peer hanno identità crittografiche |
| **Stream multiplexing** | più stream logici sulla stessa connessione (come HTTP/2) |
| **Protocol handling** | supporto a protocolli custom (Request/Response, PubSub) |
| **Peer routing** e **Content routing** | trovare peer e contenuti |
| **PubSub messaging** | canali di publish/subscribe (es. Gossipsub) |
| **NAT traversal & relay** | raggiungere peer dietro NAT |
| **Peer identity** | ogni nodo ha un PeerId crittografico |

#### PeerId e multiaddress

Ogni peer possiede una coppia di chiavi **(pubblica, privata)**. Il **PeerId** è l'hash crittografico della chiave pubblica — cioè un CID, coerentemente con la filosofia content-based di IPFS. La coppia di chiavi permette poi di stabilire canali sicuri e autenticati tra peer.

> [!definition] Multiaddress
>
> Un **multiaddress** è un indirizzo di rete **self-describing** che contiene tutte le informazioni necessarie per raggiungere un peer: protocollo di rete, indirizzo, porta, protocollo applicativo, PeerId.

Un esempio concreto:

```
/ip4/127.0.0.1/tcp/4001/p2p/12D3KooWJ...
```

Letto da sinistra a destra: "usa IPv4, indirizzo 127.0.0.1, protocollo TCP, porta 4001, protocollo p2p, PeerId 12D3KooWJ...". La struttura è componibile: si può sostituire `ip4` con `ip6`, `tcp` con `udp`/`quic`, aggiungere `wss` per WebSocket sicuri, o wrappare tutto in un relay. Ogni componente ha un codice di protocollo (varint) che lo identifica e alcuni hanno una lunghezza/byte value associati.

> [!tip] Perché il multiaddress è così flessibile
>
> - **Self-describing**: contiene tutti i protocolli e gli indirizzi necessari.
> - **Composable**: è fatto di componenti di protocollo concatenabili.
> - **Transport agnostic**: funziona con qualsiasi protocollo di rete.
> - **Extensible**: aggiungere nuovi protocolli è facile.

Esempi tipici: `/ip4/127.0.0.1/tcp/4001/p2p/12D3Koo...` per una connessione TCP locale, `/ip4/203.0.113.10/tcp/4001/p2p/12D3...` per TCP pubblico, `/dns4/example.com/tcp/443/wss/p2p/12D3...` per WebSocket su HTTPS, `/ip6/2001:db8::1/udp/443/quic-v1/p2p/12D3...` per QUIC su IPv6.

---

### Il livello di routing: la DHT

Quando richiedi un contenuto a partire dal suo CID, IPFS deve risolvere una domanda precisa: **quali peer hanno questo contenuto?** È compito del livello di **routing**, implementato tramite una **DHT (Distributed Hash Table)**.

> [!warning] Cosa fa (e cosa non fa) la DHT di IPFS
>
> La DHT di IPFS **non memorizza i dati**. Memorizza soltanto una mappa `CID → lista di PeerId che hanno dichiarato di averlo`. Quando un nodo pubblica un contenuto, annuncia alla DHT "io ho questo CID"; la DHT registra il mapping. Quando qualcuno cerca il CID, la DHT risponde "prova a chiedere a questi peer". Il trasferimento vero e proprio avviene **peer-to-peer direttamente**, bypassando la DHT.

Inoltre la DHT serve anche per la **peer discovery**: se hai un PeerId e vuoi sapere come raggiungerlo, la DHT può restituirti il suo multiaddress.

Il problema che risolve è concreto: tu hai un CID `bafybeigdyrzt...` ma non sai né chi ha il dato né da dove scaricarlo. La DHT fa da "elenco telefonico" decentralizzato: usa l'hash del file come chiave e restituisce le *locations* (i peer) del file.

#### Miglioramenti rispetto a Kademlia

La DHT vanilla di Kademlia non basta per un sistema in produzione: IPFS adotta una serie di miglioramenti presi da due filoni di ricerca.

> [!note] Estensioni adottate
>
> - **S/Kademlia** — migliora la **sicurezza** contro attacchi Sybil ed eclipse: invece di affidarsi a un singolo percorso di routing, cerca i nodi attraverso percorsi disgiunti e verifica l'identità dei peer con primitive crittografiche.
> - **Coral sloppy DHT** — migliora la **performance** con una struttura gerarchica che permette di trovare repliche "vicine" (geograficamente o in termini di latenza), evitando di contattare sempre lo stesso nodo logicamente responsabile di una chiave.

---

### Il livello di scambio: Bitswap

Una volta che la DHT ti ha detto "questi peer dovrebbero avere il contenuto", serve un protocollo per **scambiare effettivamente i blocchi**. È il compito di **Bitswap**, il livello di exchange di IPFS.

#### Perché non basta la DHT

La DHT ti dice "questo peer **ha annunciato** di avere il CID", ma non garantisce che ce l'abbia *in questo momento*. Tra il tempo in cui un peer pubblica l'annuncio e il tempo in cui un client cerca il contenuto possono succedere molte cose: il peer può essere andato offline, il blocco può essere stato rimosso (unpin, garbage collection), il peer può non rispondere per problemi di rete. L'informazione della DHT può essere **obsoleta**.

> [!abstract] Division of labor
>
> - **DHT** risponde alla domanda "*chi potrebbe avere il CID?*" — è un elenco, non una garanzia.
> - **Bitswap** risponde alla domanda "*chi effettivamente me lo dà adesso?*" — è il protocollo real-time che scarica i blocchi.

#### Bitswap vs BitTorrent

Bitswap è ispirato a BitTorrent ma non coincide con esso. La differenza fondamentale è architetturale:

| BitTorrent | Bitswap (IPFS) |
|---|---|
| uno **swarm separato** per ogni file | un **unico swarm globale** per tutti i contenuti condivisi dagli utenti |
| il peer cerca chi ha quel file specifico | il peer partecipa a un unico mercato di blocchi in cui tutti domandano e offrono CID qualsiasi |
| file diviso in pezzi | tutto è diviso in **blocchi**, la più piccola unità di dato trasferibile |

Il white paper originale introduce anche una **strategia di bartering** di base per lo scambio (tu mi dai blocchi, io te ne do in cambio), che nel progetto **Filecoin** viene poi estesa con una criptovaluta vera e propria.

#### Come funziona un trasferimento Bitswap

Il protocollo ruota attorno a quattro tipi di messaggio: **WANT** (voglio questo CID), **HAVE** (ho questo CID), **REQUEST** (mandami il blocco), **BLOCK** (ecco il blocco).

![Diagramma Mermaid](images/mermaid-lezione-24-ipfs-interplanetary-file-system-04.png)
*Fig. — Scambio Bitswap: il nodo A chiede un blocco, il nodo B conferma di averlo, A richiede i dati e B li invia. A verifica l'integrità ricalcolando il CID.*

**A cosa serve HAVE?** Fornisce una **conferma in tempo reale**: la DHT dice "potrebbe avere", HAVE dice "ce l'ho *adesso*". È un messaggio **opzionale**: un peer può rispondere direttamente con il blocco (`WANT → REQUEST → BLOCK`), saltando la conferma intermedia. Bitswap è **best effort**: se un peer non risponde, il richiedente può provare con altri peer — nessuna garanzia di consegna da un singolo fornitore, ma alta probabilità grazie alla molteplicità.

> [!tip] Punti chiave di Bitswap
>
> - I blocchi sono identificati dal loro CID (content ID).
> - Bitswap è **demand-driven** ed efficiente: nulla viene trasferito se nessuno lo richiede.
> - **Più provider** possono rispondere allo stesso WANT in parallelo: il richiedente scarica dal più veloce.
> - La verifica avviene **lato ricevente** ricalcolando l'hash dei blocchi ricevuti.

---

### Disponibilità dei file: il problema della persistenza

Il modello peer-to-peer di IPFS ha un vantaggio enorme — la replicazione naturale dei contenuti popolari — ma porta con sé un problema di disponibilità. Dove sono memorizzati i file in IPFS? Ogni nodo mantiene una **cache** dei file che ha scaricato o condiviso; rimane online fintanto che ha interesse a esserlo e aiuta a distribuire se altri utenti lo richiedono. È un modello simile a uno swarm BitTorrent, con la differenza che **esiste un solo swarm per tutti i contenuti** anziché uno swarm per file.

> [!warning] Cosa succede se tutti i nodi che ospitano un file vanno offline?
>
> Il file diventa **irraggiungibile**. Il CID resta valido in astratto (è una proprietà matematica del contenuto), ma non c'è nessuno sulla rete che possa servire i blocchi corrispondenti. Questo è il problema di **persistenza dei dati** in IPFS.

Tre strategie di mitigazione sono possibili.

1. **Pinning services** — servizi centralizzati che mantengono sempre attivi i contenuti di interesse.
2. **Incentivazione economica** — pagare i nodi per tenere online certi file (la soluzione di Filecoin).
3. **Distribuzione proattiva** — replicare attivamente i file per garantire un numero minimo di copie nella rete.

#### Pinning services: Pinata

**Pinata** è l'esempio più noto di pinning service centralizzato. Gestisce la propria infrastruttura, pinna i dati dei clienti e garantisce uptime.

> [!info] Come funziona Pinata
>
> Pinata esegue i propri nodi IPFS e "pinna" (fissa) i contenuti che i clienti caricano: significa che quei nodi non cancelleranno mai il blocco né lo rimuoveranno dalla cache. Risultato: il CID resta sempre servibile. L'interfaccia è semplice: *upload → ottieni CID → il dato resta disponibile*. È essenzialmente uno "storage cloud per IPFS".

Un aspetto importante: siccome il CID identifica il *contenuto* e non il *server*, lo stesso CID può essere pinnato **contemporaneamente** su Pinata, sul tuo nodo locale, e su altri peer. Non c'è un "vero proprietario" del dato — c'è solo un insieme di nodi che lo servono, e basta che uno sia raggiungibile perché il file sia accessibile.

#### Filecoin: incentivare lo storage con una criptovaluta

Filecoin prende questa idea e la decentralizza: invece di un pinning service centralizzato, costruisce **un mercato decentralizzato per lo storage** sopra IPFS.

> [!definition] Filecoin
>
> Filecoin è un layer costruito sopra IPFS che trasforma lo storage in un bene scambiabile sul mercato. I nodi che hanno spazio libero sul disco possono affittarlo ad altri utenti e guadagnare in cambio un token, **FIL**. I clienti pagano in FIL per memorizzare i loro dati sulla rete.

L'idea economica è potente: c'è una quantità enorme di spazio storage inutilizzato sui computer del mondo, e al tempo stesso una domanda crescente di cloud storage. Filecoin connette domanda e offerta in un mercato competitivo.

Vantaggi rispetto alle alternative centralizzate (Pinata, Google Drive, Dropbox):

- **Prezzi più equi** — il mercato competitivo tende a pressare al ribasso i prezzi rispetto a quelli delle infrastrutture centralizzate.
- **Efficienza di utilizzo** — invece di costruire nuovo storage, si sfrutta quello esistente e sottoutilizzato.
- **Decentralizzazione** — nessun punto di fallimento unico, nessun singolo fornitore che può chiudere l'account.

Il token FIL viene usato dai client per pagare lo storage, e dai *miner* come ricompensa per i task che svolgono: memorizzare i dati, dimostrare crittograficamente di continuare a memorizzarli nel tempo, proteggere la rete, validare le transazioni.

---

### NFT e IPFS

Un uso concreto e molto diffuso di IPFS è lo storage dei metadata e degli asset degli **NFT (Non-Fungible Token)**. Un NFT su Ethereum non contiene di solito l'immagine o il file multimediale vero e proprio (sarebbe proibitivamente costoso in gas): contiene un **puntatore** a dove quel contenuto è memorizzato.

> [!warning] Il rischio dei puntatori HTTP
>
> Se il puntatore è un URL HTTP (`https://mysite.com/nft-image.jpg`), il NFT è tanto permanente quanto il dominio e il server. Se il sito chiude, l'immagine sparisce — e con essa tutto ciò che l'NFT "rappresenta". Storie di NFT che hanno perso il loro contenuto sono frequenti proprio per questa ragione.

La soluzione è usare un **CID IPFS** come puntatore. Il CID è immutabile e content-addressed: anche se un nodo specifico va offline, finché il contenuto esiste da qualche parte nella rete IPFS (tipicamente pinnato su un servizio come Pinata o su Filecoin), il NFT continua a puntare correttamente al contenuto originale. I marketplace NFT (OpenSea, Rarible, ecc.) leggono il CID dal metadata del token e risolvono il contenuto tramite IPFS gateway.

> [!tip] Perché IPFS è naturale per gli NFT
>
> Il CID **è** un'impronta digitale crittografica del contenuto. Se un giorno qualcuno sostituisse l'immagine con un'altra, il CID sarebbe diverso: non può silenziosamente cambiare a cosa punta un NFT. L'immutabilità dell'NFT sulla blockchain si estende, tramite il CID, all'immutabilità del contenuto puntato.

---

### Sintesi su IPFS

> [!abstract] Riepilogo della lezione
>
> IPFS è un protocollo P2P **content-based** che sostituisce l'indirizzamento HTTP basato sulla location con identificatori crittografici (**CID**) derivati dal contenuto stesso. Lo stack si articola su tre blocchi logici: **trasporto** (libp2p per la rete, DHT per il routing, Bitswap per lo scambio), **definizione** (IPLD con Merkle DAG per la strutturazione dei dati, IPNS per il naming), **applicazioni**. Il progetto **Multiformat** (multihash, multibase, multicodec, multiaddr) rende tutti i valori auto-descrittivi, permettendo al protocollo di evolvere senza rompere il software esistente. Il **Merkle DAG** garantisce deduplicazione automatica, verifica crittografica end-to-end e versionamento naturale. La **persistenza** dei dati è un problema aperto, mitigato da servizi di pinning centralizzati (**Pinata**) o dal mercato decentralizzato di **Filecoin**, che incentiva lo storage con una criptovaluta.

## Applicazioni Reali con Smart Contracts

Le criptovalute come Bitcoin, Ethereum e Solana rappresentano le applicazioni più note della blockchain, ma si tratta soltanto del punto di partenza. L'introduzione degli **smart contract**, come abbiamo visto per i token fungibili e non fungibili, ha reso possibile il passaggio da semplici transazioni finanziarie a sistemi digitali completamente programmabili on-chain: supply chain, finanza decentralizzata (DeFi), organizzazioni governate da comunità (DAO) e identità digitale auto-sovrana (SSI). La chiave di questa espansione è la **composabilità**: diversi protocolli possono essere combinati tra loro come moduli software, creando ecosistemi di applicazioni interoperabili.

---

### Caso d'uso: Supply Chain

#### Limiti dell'architettura classica

Il problema di partenza è concreto: un'azienda come Alpha Corporation progetta e fa produrre macchinari complessi, li spedisce in sedi remote, li sottopone a manutenzione periodica tramite terze parti autorizzate, ne trasferisce la proprietà tra aziende diverse, e infine li dismette. In un'architettura centralizzata classica, la sede centrale A1 gestisce un database che traccia componenti, attrezzature, posizioni, storici di manutenzione e ciclo di vita. Questo approccio presenta fragilità strutturali: un attacco di tipo denial of service o una compromissione del database può cancellare o alterare i record; i processi manuali dipendono dalla memoria e dall'intervento umano; la conformità normativa e l'auditing da parte di terzi sono difficili da garantire; le dispute legali successive risultano costose e complesse perché l'auditabilità del sistema non è garantita by design.

#### Blockchain permissioned per la supply chain

La soluzione proposta è una **blockchain permissioned**: una rete P2P privata in cui solo i partecipanti autorizzati possono unirsi e aggiungere blocchi. A differenza di una blockchain pubblica come Ethereum, l'accesso è controllato da un'entità centralizzata — in questo caso Alpha — che gestisce le chiavi pubbliche dei partecipanti tramite un **Membership Service Provider (MSP)**.

![Diagramma Mermaid](images/mermaid-lezione-27-applicazioni-reali-con-smart-contracts-01.png)
*Fig. — Architettura di una blockchain permissioned: ogni organizzazione gestisce un peer node e condivide un ledger immutabile; l'accesso è mediato dal Membership Service Provider (MSP).*

Il processo di bootstrap avviene in questo modo:

1. **Alpha (A1)** avvia la blockchain creando il blocco genesi, che contiene la propria chiave pubblica. Questa chiave servirà ad autenticare tutti i dati registrati da A1 in futuro.
2. **A2** (la fabbrica) e **B** (l'azienda di manutenzione) generano coppie di chiavi pubblica/privata e inviano le chiavi pubbliche ad A1, che le annuncia sulla blockchain. Da questo momento A2 e B sono nodi della rete P2P, gestiscono il proprio nodo blockchain e possono aggiungere blocchi.
3. Nessun partecipante conosce le chiavi private degli altri: l'impersonificazione è impossibile per costruzione crittografica.

##### Identificazione dei componenti e IoT

Ogni componente prodotto da A2 riceve una propria coppia di chiavi: la chiave pubblica viene annunciata sulla blockchain insieme alla posizione iniziale (magazzino della fabbrica), mentre la chiave privata può essere fisicamente incorporata nel componente. A seconda del valore del componente, la comunicazione con la blockchain avviene in modo diverso:

- **Componenti economici**: codice QR con la chiave pubblica; lettori RFID leggono la chiave e inviano report alla blockchain per conto del componente.
- **Componenti costosi**: tag RFID attivo con connettività Bluetooth; il componente può autonomamente contattare dispositivi vicini e inviare report on-chain.
- **Macchinario completo**: dispositivo IoT completamente connesso con GPS integrato, eventualmente un nodo blockchain leggero, e un lettore RFID integrato che scansiona tutti i componenti interni e rileva eventuali sostituzioni.

##### Smart contract e automazione della manutenzione

Quando un componente viene registrato sulla blockchain, all'annuncio della sua chiave pubblica può essere allegato uno smart contract. Questo contratto può innescare automaticamente richieste di manutenzione, ordini di sostituzione o procedure di dismissione senza intervento umano.

![Diagramma Mermaid](images/mermaid-lezione-27-applicazioni-reali-con-smart-contracts-02.png)
*Fig. — Flusso di automazione: dal rilevamento della condizione critica (IoT) all'esecuzione dello smart contract, fino alla registrazione immutabile dell'intervento.*

##### Revoca delle certificazioni

Se un tecnico lascia l'azienda B, il responsabile pubblica un messaggio di revoca della chiave sul blocco, firmato con la propria chiave privata. Tutti i record precedenti al blocco di revoca rimangono validi e immutabili; i record successivi firmati con la chiave revocata non sono più considerati autentici.

##### Trasferimento di proprietà e decommissioning

Quando il macchinario cambia proprietario (dall'azienda X alla Y), l'evento viene registrato sulla blockchain, creando un registro immutabile di provenienza. Al termine del ciclo di vita, la dismissione viene certificata con la firma del produttore originale A, consentendo futuri audit ambientali e di conformità normativa. Al termine dell'intero processo esiste sulla blockchain un registro completo di tutti i partecipanti, componenti, posizioni, interventi e trasferimenti: i record non possono essere alterati né cancellati, e non esiste un single point of failure.

---

### Certificazione e Tracciabilità

Oltre alla supply chain industriale, la blockchain trova applicazione ovunque sia necessaria la **tracciabilità** di prodotti lungo l'intera catena di distribuzione e la **prova di autenticità** a prova di manomissione. I settori principali includono: alimentare e agricoltura, farmaceutica, manifattura industriale, edilizia e BIM (dove si tracciano materiali, certificazioni e dati del ciclo di vita dell'edificio), beni di lusso e diamanti.

> [!note] EU Digital Product Passport
>
> L'Unione Europea sta valutando il Digital Product Passport (DPP) per tracciare sostenibilità e provenienza dei prodotti. I pilot attuali esplorano blockchain, Decentralized Identifiers (DID), Verifiable Credentials e smart contract. Lo scenario più realistico prevede architetture ibride: database centralizzati con prove su blockchain, reti DLT permissioned e standard di interoperabilità come EBSI.

---

### NFT: Arte Digitale e Proprietà

Un'opera d'arte digitale è banalmente copiabile: chiunque può farne screenshot o download. Ma **copiare non significa possedere**. In un sistema tradizionale, la proprietà resta all'artista o a chi detiene il copyright, indipendentemente da quante copie circolino. L'analogia fisica è la prima edizione di un libro: ha lo stesso contenuto di tutte le ristampe, ma vale di più.

Come abbiamo esplorato in precedenza, gli **NFT** estendono questo concetto al digitale. Quando Beeple ha mintato il suo NFT per l'opera *Everydays: The First 5000 Days*, ha creato un token sulla blockchain contenente:
- Un **fingerprint unico** del file dell'opera (`8a5de7b183ecf2ec9f488`)
- Il nome del token: `Everydays: The First 5000 Days`
- Il simbolo: `EF5000D`

La transazione sulla blockchain registra che "il token `8a5de7b183ecf2ec9f488` è creato da Beeple, che ne è il proprietario." L'opera stessa **non è nel blocco**: l'NFT contiene solo un link al file archiviato su un file system distribuito (IPFS o equivalente). Ciò che si acquista è il certificato di proprietà, non il file — esattamente come comprare la chitarra di Elvis Presley: chiunque può comprare una chitarra identica, ma solo una ha quel certificato di autenticità.

---

### DeFi — Finanza Decentralizzata

La **DeFi** (Decentralized Finance) è l'insieme di applicazioni finanziarie costruite su blockchain che eliminano intermediari tradizionali come banche, broker e exchange, sostituendoli con smart contract e protocolli automatizzati.

#### Stable Coin

Le criptovalute tradizionali sono altamente volatili. Una **stable coin** è progettata per mantenere un valore stabile, tipicamente agganciato a una valuta fiat (1 coin = 1 USD). Questo permette di integrare valute reali nelle applicazioni on-chain e offre a persone in paesi con alta inflazione un'alternativa digitale al dollaro senza necessitare di un conto bancario statunitense.

> [!definition] Tipi di Stable Coin
>
> | Tipo | Backing | Custodia | Esempi |
> |------|---------|----------|--------|
> | **Fiat-Collateralized** | Valute fiat 1:1 in riserva presso un ente | Custodial | USDC, USDT, BUSD |
> | **Commodity-Backed** | Materie prime fisiche (oro, argento) | Custodial | PAXG, XAUT |
> | **Crypto-Collateralized** | Crypto bloccate in smart contract (over-collateralized) | Non-custodial | DAI, LUSD |
> | **Algorithmic** | Algoritmi + incentivi di mercato | Non-custodial | FRAX, AMPL |

##### Fiat-Backed: ciclo di vita completo

Il ciclo di vita di una stable coin fiat-backed si articola in tre operazioni governate da uno smart contract **ERC-20**:

**Minting** — Bob deposita 100 USD e Alice 35 USD presso il custodian (la banca). Il custodian chiama `mint(Bob, 100)` e `mint(Alice, 35)` sul contratto ERC-20. Il contratto aggiorna il mapping `_balances` on-chain. La riserva del custodian ammonta a 135 USD.

**Transfer** — Bob paga 15 USDC a Carol chiamando `transfer(Bob → Carol, 15)` sul contratto (pagando la gas fee). Il trasferimento avviene completamente on-chain senza coinvolgere il custodian: i saldi diventano Bob: 85, Alice: 35, Carol: 15.

**Withdrawal** — Bob ritira 60 USD reali. Il custodian chiama `burn(Bob, 60)` sul contratto, distruggendo i token. Il saldo di Bob scende a 25 USDC, la riserva del custodian si riduce a 75 USD, e Bob riceve 60 USD fisici.

![Diagramma Mermaid](images/mermaid-lezione-27-applicazioni-reali-con-smart-contracts-03.png)
*Fig. — Ciclo completo di una stable coin fiat-backed: il minting e il withdrawal coinvolgono il custodian; il trasferimento è puramente on-chain.*

##### Stabilità tramite arbitraggio

Le stable coin fiat-backed mantengono il peg attraverso l'**arbitraggio**: se 1 USDC vale 1,02 USD sul mercato secondario, i trader acquistano USD dalla banca a 1:1 e vendono USDC sul mercato, spingendo il prezzo verso il basso. Il meccanismo inverso vale quando il prezzo scende sotto il peg.

##### Crypto-Collateralized

Le stable coin crypto-collateralized sono decentralizzate e non-custodial: il collaterale è bloccato in smart contract, non presso una banca. Poiché le criptovalute sono volatili, è richiesta la **over-collateralization**: per mintare 100 USD di stable coin occorre depositare 150 USD di ETH. Se il valore del collaterale scende sotto la soglia di sicurezza, la posizione viene liquidata automaticamente.

##### Algorithmic Stable Coin

Le stable coin algoritmiche mantengono il peg senza riserve complete, usando algoritmi, smart contract e meccanismi di arbitraggio. Un oracolo monitora il prezzo di mercato e lo invia on-chain: se il prezzo supera il peg, l'offerta aumenta; se scende al di sotto, l'offerta si riduce.

---

#### Lending e Borrowing

I protocolli DeFi di lending replicano on-chain la funzione delle banche commerciali: chi ha liquidità la presta guadagnando interessi; chi ha asset ma non vuole venderli ottiene liquidità depositando collaterale. Il sistema coinvolge quattro attori: lender, borrower, price oracle e liquidator.

![Diagramma Mermaid](images/mermaid-lezione-27-applicazioni-reali-con-smart-contracts-04.png)
*Fig. — Modello generale del lending DeFi: il vault gestisce collaterale e debito; l'oracle fornisce prezzi; il liquidator interviene quando il Health Factor scende sotto 1.*

##### Il lender

Il lender deposita asset liquidi (es. 50.000 USDC) nel protocollo e riceve in cambio token di interesse. Nel tempo accumula rendimento proporzionale alla liquidità fornita e alla domanda di prestito.

##### Il borrower e l'over-collateralization

Il borrower deposita collaterale (es. 10 ETH a $3.000 = $30.000) e ottiene liquidità (es. 20.000 USDC) senza vendere i propri asset. La motivazione è strategica: Bob vede i suoi BTC o ETH come asset con potenziale di apprezzamento a lungo termine e preferisce ottenerci liquidità piuttosto che venderli. Il protocollo traccia il **Health Factor (HF)**:

$$HF = \frac{\text{Valore collaterale} \times \text{Liquidation threshold}}{\text{Valore debito}}$$

Quando $HF < 1$, la posizione è sottocollateralizzata e diventa liquidabile.

##### Il liquidatore

Se il mercato crolla e il collaterale scende sotto soglia (es. ETH da $3.000 a $2.200, collaterale vale $22.000 ma debito è ancora $20.000), il protocollo consente a qualsiasi liquidatore di intervenire:

1. Alice (liquidator) rimborsa 5.000 USDC del debito di Bob.
2. Il protocollo dà ad Alice ETH per $5.500 (liquidation bonus del 10%).
3. Bob perde parte del collaterale, ma il suo debito si riduce; Alice guadagna il bonus; il protocollo rimane solvente.

> [!warning] Il ruolo critico dell'oracle
>
> Per calcolare il Health Factor in tempo reale, il protocollo deve conoscere il prezzo corrente dell'ETH. Ma una blockchain è un "database isolato" senza connessione a Internet. La soluzione sono i **blockchain oracle**: servizi che portano dati off-chain (prezzi di mercato, risultati sportivi, orari voli) on-chain in modo sicuro.

##### Blockchain Oracle — use case

| Use Case | Dato richiesto |
|----------|---------------|
| Lending/Borrowing | Prezzi in tempo reale per il calcolo del Health Factor e trigger di liquidazione |
| Mercati scommesse | Risultato finale di eventi sportivi |
| Assicurazione voli | Orari e ritardi per contratti di rimborso automatico |
| Stable coin algoritmiche | Prezzo di mercato della stable coin per regolare l'offerta |

---

#### Flash Loan

> [!definition] Flash Loan
>
> Un **flash loan** è un prestito preso e rimborsato all'interno di una singola transazione atomica. Se il rimborso fallisce, l'intera transazione viene revertita automaticamente: zero rischio per il lender, zero collaterale necessario per il borrower — la garanzia è l'atomicità della transazione stessa.

La potenza dei flash loan risiede nel permettere accesso a capitali enormi per pochi secondi al fine di eseguire operazioni complesse come l'arbitraggio. Esempio concreto:

1. Borrow di 1.000.000 USDC dal protocollo di lending.
2. Acquisto di ~625 ETH su DEX A (prezzo più basso).
3. Vendita dei ~625 ETH su DEX B (prezzo più alto), ricevendo ~1.025.000 USDC.
4. Rimborso di 1.000.900 USDC (loan + fee) al protocollo.
5. Profitto netto: ~24.100 USDC.
6. Tutta la sequenza è un'unica transazione atomica: se un passo fallisce, tutto si reverte e il prestito non viene mai erogato.

![Diagramma Mermaid](images/mermaid-lezione-27-applicazioni-reali-con-smart-contracts-05.png)
*Fig. — Flash loan per arbitraggio: borrow → buy on DEX A → sell on DEX B → repay, tutto in un'unica transazione atomica.*

---

### Exchange: Centralizzati vs Decentralizzati

#### CEX — Exchange Centralizzati

Un exchange centralizzato (CEX) funziona come un mercato finanziario tradizionale: gli utenti depositano fondi sulla piattaforma, che gestisce custodia, esecuzione e liquidità. Il meccanismo centrale è l'**order book**: i compratori specificano il prezzo massimo che sono disposti a pagare (*bid*), i venditori il prezzo minimo accettabile (*ask*). Quando bid e ask si incontrano, avviene la transazione e il prezzo dell'incrocio diventa il prezzo di mercato. Esempi: Binance, Coinbase, Kraken.

> [!example] Order Book BTC/USDT
>
> | BUY ORDERS (Bids) | | | SELL ORDERS (Asks) | |
> |---|---|---|---|---|
> | Price (USDT) | Qty (BTC) | | Price (USDT) | Qty (BTC) |
> | 66.350 | 0.4200 | | 66.450 | 0.6000 |
> | 66.300 | 1.2500 | | 66.500 | 1.0000 |
> | 66.250 | 0.7500 | | 66.550 | 0.8500 |
>
> **Best bid**: 66.350 USDT | **Best ask**: 66.450 USDT | **Spread**: 100 USDT | **Mid price**: 66.400 USDT

#### DEX — Exchange Decentralizzati

Un exchange decentralizzato (DEX) consente agli utenti di scambiare token direttamente dal proprio wallet, senza depositare fondi su una piattaforma centralizzata. I token vengono acquistati da una **liquidity pool**: un deposito di coppia di token (es. USDC/WETH) fornito da utenti chiamati **Liquidity Provider (LP)**, che guadagnano le fee sulle transazioni. Il prezzo non emerge da ordini umani ma da una formula matematica eseguita dallo smart contract.

![Diagramma Mermaid](images/mermaid-lezione-27-applicazioni-reali-con-smart-contracts-06.png)
*Fig. — Struttura di un DEX: i liquidity provider alimentano la pool con entrambi i token della coppia; il trader swappa pagando una fee che va agli LP.*

#### Automated Market Maker (AMM)

##### La Constant Product Formula

Il cuore matematico dell'AMM è la **constant product formula**:

> [!definition] Constant Product Formula
>
> $$x \cdot y = k$$
>
> dove $x$ = quantità del token X nella pool, $y$ = quantità del token Y, $k$ = costante. Il prodotto dei due saldi rimane costante dopo ogni swap.

![Constant Product Formula: iperbola xy=k con stato prima e dopo uno swap](images/lezione-27-applicazioni-reali-con-smart-contracts-img-01.jpg)
*Fig. — La curva iperbola $xy = k$: a sinistra lo stato iniziale ($x_0 = 10, y_0 = 30, k = 300$); a destra lo stato dopo uno swap ($x_1 = 15, y_1 = 20, k$ rimane 300). Il punto si muove lungo la curva mantenendo il prodotto costante.*

L'intuizione è immediata: più un asset diventa scarso nella pool (il suo $x$ o $y$ diminuisce), più il suo prezzo aumenta. Non c'è order book, non ci sono trader umani: solo matematica, liquidità e smart contract.

##### Il prezzo istantaneo

Per una curva $\psi(x, y) = \text{costante}$, il prezzo istantaneo di Y in termini di X si ricava come la pendenza della tangente alla curva nel punto corrente:

$$P_{Y/X} = \frac{dY}{dX} = \frac{y}{x}$$

![Prezzo istantaneo nell'AMM: slope della tangente alla curva xy=k](images/lezione-27-applicazioni-reali-con-smart-contracts-img-02.jpg)
*Fig. — Il prezzo istantaneo di Y è il rapporto $y/x$, ovvero la pendenza della tangente alla curva $\psi(x,y) = \text{costante}$ nel punto corrente.*

##### Variazioni di $k$

$k$ non è permanentemente fisso: aumenta quando i liquidity provider aggiungono liquidità o quando le fee di trading si accumulano nella pool; diminuisce quando la liquidità viene rimossa. Gli swap spostano il punto lungo la curva; le operazioni di liquidità spostano l'intera curva. In conclusione, in un CEX i prezzi emergono dalla competizione di ordini umani/automatici nel mercato; in un AMM i prezzi emergono automaticamente dalla formula matematica e dal bilanciamento degli asset nella pool.

---

### Tokenizzazione di Asset Reali (RWA)

I **Tokenized Real-World Assets (RWA)** sono asset fisici o finanziari tradizionali rappresentati digitalmente su blockchain. Un asset reale viene convertito in un token blockchain che può essere scambiato, trasferito o usato in applicazioni DeFi. Esempi: immobili, titoli di stato, azioni, materie prime (oro, petrolio), opere d'arte, crediti privati.

Il processo è concettualmente semplice: l'asset esiste off-chain, una struttura legale collega l'asset al token on-chain, e il token rappresenta proprietà o quote dell'asset. I vantaggi rispetto alla finanza tradizionale: **proprietà frazionata**, **liquidità aumentata**, **trading 24/7 globale**, **settlement più rapido**, **maggiore trasparenza** e **integrazione nativa con smart contract e DeFi**.

> [!example] Esempi reali
>
> - **BlackRock BUIDL**: fondo che investe in T-bill americani a breve termine; la proprietà è rappresentata da token blockchain.
> - **Maple Finance**: tokenizzazione di prestiti e prodotti di credito istituzionali.
> - Esperimenti di tokenizzazione immobiliare a Dubai, Singapore e Svizzera.

---

### Rischi Nascosti nel DeFi

La DeFi rimuove banche e intermediari sostituendoli con smart contract e transazioni blockchain pubbliche. Questa trasparenza apre però la porta a nuove forme di manipolazione del mercato basate sull'**ordinamento delle transazioni**.

Prima di essere confermate on-chain, le transazioni rimangono visibili nel **mempool pubblico**, dove i validatori (miner nel PoW, proposer nel PoS) possono osservarle e decidere l'ordine di inclusione nel blocco. Chi controlla l'ordinamento può influenzare gli outcome di mercato.

#### Sandwich Attack

> [!warning] Sandwich Attack
>
> Un attaccante osserva una transazione profittevole della vittima nel mempool e la circonda con due proprie transazioni:
>
> 1. **Front-run** ($T_{A_1}$, gas price **più alto** di $T_V$): compra lo stesso asset prima della vittima, facendone salire il prezzo.
> 2. **Vittima** ($T_V$): acquista l'asset a prezzo ormai più alto, subendo slippage sfavorevole.
> 3. **Back-run** ($T_{A_2}$, gas price **più basso** di $T_V$): vende l'asset al prezzo gonfiato dalla transazione della vittima, intascando il profitto.

![Sandwich attack: T_A1 inserita prima di T_V, T_A2 inserita dopo nel blocco](images/lezione-27-applicazioni-reali-con-smart-contracts-img-03.jpg)
*Fig. — Il sandwich attack: $T_{A_1}$ (front-run) e $T_{A_2}$ (back-run) circondano $T_V$ (vittima) nel blocco proposto. I miner includono nell'ordine corretto grazie al differenziale di gas price.*

#### MEV — Maximum Extractable Value

> [!definition] MEV
>
> Il **Maximum Extractable Value (MEV)** è il massimo profitto estraibile dal controllo dell'ordinamento e della selezione delle transazioni nella produzione di un blocco. Un miner o validatore può includere, escludere o riordinare arbitrariamente le transazioni.

Oggi la maggior parte dell'estrazione MEV proviene da **Bot Operator** che monitorano continuamente il mempool, identificano opportunità (sandwich attack, arbitraggio tra pool, liquidazioni) e le sfruttano automaticamente. Il MEV non è un bug accidentale: è una conseguenza strutturale della trasparenza del mempool e della discrezionalità sull'ordinamento.

#### Prevenzione degli attacchi

Due meccanismi principali:

- **Limite sul gas price**: impedisce agli utenti di ottenere priorità tramite offerte più alte. Non funziona se i miner stessi sono gli attaccanti.
- **Commit-reveal scheme**: la transazione viene inviata con informazioni nascoste (hash dell'intenzione); solo dopo che la transazione è inclusa nel blocco l'utente rivela i dati in chiaro con una seconda transazione. L'attaccante nel mempool vede solo l'hash, non i dettagli dell'operazione, rendendo impossibile il front-running.

---

### Conclusione: Innovazioni Fondamentali della DeFi

> [!abstract] Core innovations
>
> - **Flash Loan**: accesso a capitale senza collaterale, rimborsato nella stessa transazione atomica; zero rischio per il lender.
> - **Automated Market Maker (AMM)**: pool di liquidità algoritmiche che eliminano l'order book; il prezzo è un output matematico deterministico.
> - **Finanza composabile**: i protocolli si combinano come moduli software, creando ecosistemi di applicazioni interoperabili.
> - **Accesso permissionless**: chiunque può usare i protocolli finanziari senza banche né intermediari.
> - **Logica finanziaria programmabile**: mercati, lending e governance diventano codice eseguibile on-chain.
> - **On-chain governance**: i protocolli sono gestiti collettivamente tramite token voting.
> - **Infrastruttura finanziaria aperta**: i sistemi finanziari diventano API pubbliche accessibili a qualsiasi sviluppatore.
