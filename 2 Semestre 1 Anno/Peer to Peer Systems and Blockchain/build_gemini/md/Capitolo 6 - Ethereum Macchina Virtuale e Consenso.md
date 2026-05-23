# Capitolo 6 - Ethereum: Macchina Virtuale e Consenso

## Smart Contracts: l'idea originale

Il concetto di **smart contract** non nasce con Ethereum. Fu Nick Szabo a formularne l'idea nel 1994, descrivendolo come un protocollo di transazione computerizzato che esegue i termini di un contratto, con l'obiettivo di soddisfare condizioni contrattuali comuni, minimizzare eccezioni (sia dolose che accidentali) e ridurre il bisogno di intermediari fiduciari.

> [!definition] Smart Contract
>
> Un programma informatico che automatizza la logica "se questo accade, allora fai quello" tipica dei contratti tradizionali. Il codice informatico si comporta in modo prevedibile ed è privo delle sfumature linguistiche del linguaggio naturale.

La novità fondamentale rispetto a un contratto cartaceo è triplice: il codice è **più funzionale**, può **ridurre i costi**, e soprattutto tende a **eliminare l'intermediario fiducioso** (banca, notaio, assicurazione). La crittografia e i meccanismi di sicurezza garantiscono che le relazioni algoritmicamente specificabili non possano essere violate.

### L'esempio dell'aeroporto

L'esempio didattico classico è quello assicurativo: Bob è in aeroporto e il suo volo subisce un ritardo. L'assicurazione ha caricato su una blockchain (per esempio Ethereum) uno smart contract che monitora i ritardi dei voli collegandosi al database della compagnia. Non appena la condizione "ritardo ≥ X ore" viene verificata, il contratto accredita automaticamente l'importo assicurato nel wallet di Bob.

Il meccanismo si articola in tre fasi distinte. Prima, il contratto viene **creato** con i termini e le condizioni, e registrato in un blocco della blockchain tenendo fermi i fondi della compagnia assicurativa finché la condizione non si avvera. Poi il contratto viene **eseguito** da tutti i nodi della rete P2P, che prelevano i dati dal database dei voli: tutti i nodi devono convergere allo stesso risultato. Infine, se la maggioranza dei nodi onesti valuta la condizione come vera, la compensazione viene trasferita automaticamente a Bob.

---

## Perché Bitcoin non basta: i limiti degli script

Prima di capire cosa fa Ethereum, è utile capire cosa non riesce a fare Bitcoin. Il linguaggio di scripting di Bitcoin presenta tre limitazioni strutturali:

- **Non è Turing-completo**: mancano i cicli, quindi i programmi esprimibili sono solo un sottoinsieme finito di computazioni.
- **Nessuna variabile di stato persistente**: gli script Bitcoin consumano i propri input per produrre un output, ma non lasciano alcuno stato residuo. Un contratto che ha bisogno di "ricordare" informazioni tra un'esecuzione e l'altra è impossibile da implementare.
- **Cecità verso la blockchain**: gli script non possono accedere ai valori degli header dei blocchi (nonce, timestamp, hash del blocco precedente).

> [!tip] Intuizione chiave
>
> Bitcoin è uno storage distribuito di transazioni. Ethereum estende questo modello trasformando la blockchain in un **computer distribuito**: non solo lo storage è replicato, ma anche la computazione. I nodi non si limitano a validare transazioni, eseguono codice.

---

## Ethereum in breve: il world computer

Ethereum è una piattaforma blockchain per la costruzione di **applicazioni decentralizzate** (*DApps*). Fu ideata da **Vitalik Buterin** (nato il 31 gennaio 1994) e lanciata nel 2015.

A differenza di Bitcoin, in Ethereum:
- il **codice** delle applicazioni e il loro **stato** sono memorizzati sulla blockchain,
- le **transazioni** non solo trasferiscono criptovaluta, ma possono innescare l'esecuzione di codice, aggiornare stato, emettere eventi e scrivere log,
- le **interfacce frontend** possono rispondere a eventi e leggere log dalla chain.

Le applicazioni di Ethereum vanno ben oltre il semplice trasferimento di valore: crowdfunding, token (ERC-20), DeFi, NFT, catene di approvvigionamento, IoT, voto, identità digitale sovrana (SSI). Tra gli esempi concreti: *Ethereum Name Service*, *Cryptokitties*, exchange decentralizzati.

> [!note] ICO (Initial Coin Offering)
>
> Un meccanismo basato sul token standard ERC-20 che consente a un'azienda di raccogliere fondi emettendo nuovi token. Negli anni 2017-2018 gli investimenti in ICO raggiunsero rispettivamente 7 e 12 miliardi di dollari.

### Ethereum come macchina a stati distribuita

Il modello formale di Ethereum è quello di una **macchina a stati deterministica distribuita**:

- lo **stato globale** è l'insieme degli stati di tutti gli smart contract,
- le **transazioni** sono gli eventi che cambiano lo stato globale,
- il **consenso** garantisce che tutti i nodi concordino sul risultato dell'esecuzione e aggiornino il proprio ledger in modo coerente.

Una proprietà cruciale è il **determinismo**: lo smart contract deve produrre lo stesso risultato su ogni nodo. Questo implica che la logica sia visibile a tutti (trasparenza), ma può creare problemi di privacy — risolvibili in alcuni casi con prove a conoscenza zero (*zero-knowledge proofs*).

---

## Da Bitcoin a Ethereum: il modello a stati

### Bitcoin come macchina a stati: UTXO

Prima di analizzare Ethereum, vale la pena fissare il modello di Bitcoin come termine di paragone.

![Diagramma della macchina a stati Bitcoin basata su UTXO](images/lezione-19-ethereum-accounts-transactions-gas-img-02.jpg)
*Fig. — In Bitcoin lo stato è l'insieme degli UTXO (Unspent Transaction Output). Una transazione consuma degli UTXO esistenti e ne crea di nuovi, generando la transizione S → S'.*

Il saldo disponibile di un utente Bitcoin è la somma dei suoi UTXO. Ogni UTXO esiste una sola volta e viene consumato dalla transazione che lo spende: questo rende impossibile il doppio utilizzo a livello strutturale.

### Ethereum: account-based

Ethereum usa invece un modello **account-based**, simile a quello bancario. Lo stato globale non è un insieme di output non spesi, ma un insieme di **account**, ognuno con il proprio saldo e, nel caso degli smart contract, con il proprio codice e storage.

> [!definition] Ethereum come macchina a stati
>
> Una macchina virtuale deterministica che applica cambiamenti allo stato globale replicato. A differenza di Bitcoin, chiunque può definire le proprie funzioni di transizione di stato tramite smart contract.

---

## Gli Account di Ethereum

Ogni account Ethereum è identificato da un indirizzo di **20 byte (160 bit)**. Esistono due tipi fondamentalmente diversi.

### Externally Owned Account (EOA)

Gli **EOA** sono gli account "personali", controllati da un'entità esterna (persona o organizzazione) tramite una **chiave privata**. Chi possiede la chiave privata può accedere ai fondi e invocare smart contract.

Un EOA contiene:
- **address**: l'indirizzo pubblico dell'account
- **Ether balance**: il saldo in Ether
- **nonce**: il numero totale di transazioni emesse da quell'account (da non confondere con il nonce PoW!)

Un EOA può inviare transazioni per trasferire Ether o per invocare uno smart contract.

### Contract Account

Gli account contratto sono controllati non da una chiave privata, ma dal **codice** associato. Contengono:
- **contract code**: il bytecode immutabile del contratto
- **persistent storage**: le variabili interne del contratto
- **Ether balance**: come gli EOA, possono ricevere e inviare Ether
- **nonce**: numero di messaggi inviati da questo account

Gli account contratto **non hanno chiave privata**: non possono iniziare autonomamente una transazione, ma solo rispondere a transazioni o messaggi ricevuti.

![Schema strutturale degli account Ethereum: EOA e Contract Account a confronto](images/lezione-19-ethereum-accounts-transactions-gas-img-03.jpg)
*Fig. — Confronto strutturale tra EOA e Contract Account. L'EOA usa una chiave privata per firmare transazioni e ne deriva l'indirizzo con Keccak-256; il Contract Account espone bytecode EVM e storage persistente. Entrambi condividono lo spazio di indirizzamento a 20 byte (160 bit).*

> [!warning] Generazione degli indirizzi
>
> Per un EOA: `EOA = Keccak-256(publicKey)[rightmost 20 bytes]`
> Per un Contract Account: `Contract = Keccak-256(RLP(sender, nonce))[rightmost 20 bytes]`

La tabella seguente riassume le differenze operative:

![Tabella di confronto tra EOA e Contract Account per caratteristiche](images/lezione-19-ethereum-accounts-transactions-gas-img-04.jpg)
*Fig. — Confronto delle capacità: solo gli EOA possono inviare transazioni firmate; solo i Contract Account hanno codice e storage. I contratti possono inviare messaggi (non transazioni firmate) ad altri contratti e crearne di nuovi.*

---

## Transazioni in Ethereum

Qualsiasi azione sulla blockchain Ethereum è sempre **avviata da una transazione proveniente da un EOA**. Gli EOA sono il ponte tra il mondo esterno e lo stato interno di Ethereum.

> [!definition] Transazione
>
> Un pacchetto dati firmato, serializzato e inviato da un EOA a un altro account. Può innescare messaggi successivi tra contratti, genera una modifica allo stato della blockchain se inclusa in un blocco, e può essere usata per creare nuovi contratti.

### Transazione EOA → EOA

La forma più semplice di transazione trasferisce Ether da un EOA a un altro, funzionalmente analoga a una transazione Bitcoin — ma basata su account, non su UTXO.

![Formato della transazione EOA-to-EOA: campi signature, to, amount](images/lezione-19-ethereum-accounts-transactions-gas-img-05.jpg)
*Fig. — Formato della transazione EOA→EOA. I campi principali: `signature` (firma ECDSA del mittente), `to` (indirizzo del destinatario a 20 byte), `amount` (valore in wei).*

### Il nonce della transazione

> [!definition] Transaction Nonce
>
> Un valore scalare uguale al numero di transazioni inviate da quell'indirizzo (per gli EOA) o al numero di contratti creati (per i contract account). È un attributo dell'account mittente, non della singola transazione.

Il nonce serve a due scopi: **registrare l'ordine delle transazioni** e **proteggere dal replay attack**.

#### Il replay attack

Il problema nasce dalla differenza strutturale tra Bitcoin ed Ethereum. In Bitcoin ogni UTXO può essere speso una sola volta: una volta consumato, sparisce. In Ethereum invece esiste un saldo di account, e la stessa transazione firmata potrebbe in principio essere ritrasmessa più volte sulla rete.

Il replay attack funziona così: Alice firma una transazione per inviare 10 ETH a Bob. Bob, dopo che la transazione è stata minata, può prendere la stessa transazione e ritrametterla ripetutamente, svuotando progressivamente il conto di Alice.

La soluzione di Ethereum è il nonce: ogni transazione deve includere il nonce corrente dell'account mittente, e la rete non accetta una seconda transazione con lo stesso nonce. Bob non può modificare il nonce perché questo invaliderebbe la firma di Alice.

> [!warning] Ordinamento obbligatorio
>
> Il nonce impone un ordine rigido. Una transazione con nonce 2 non può essere minata se la rete non ha già confermato quelle con nonce 0 e 1. Le transazioni devono essere in sequenza e non possono essere saltate.

---

## Transizioni di stato in Ethereum

### Transizione semplice EOA→EOA

![Esempio di transizione di stato tra EOA: Alice invia 10 ETH a Bob](images/lezione-19-ethereum-accounts-transactions-gas-img-06.jpg)
*Fig. — Transizione di stato EOA→EOA. Alice (50 ETH, nonce 5) invia 10 ETH a Bob (30 ETH). Lo stato S' vede Alice a 40 ETH (nonce 6) e Bob a 40 ETH. Se il saldo fosse insufficiente (es. Alice=50, Bob=30, send 70) la funzione APPLY restituisce ERROR.*

### Transizione con Smart Contract

![Esempio di transizione di stato con smart contract che aggiorna il proprio storage](images/lezione-19-ethereum-accounts-transactions-gas-img-07.jpg)
*Fig. — Transizione di stato con contract account. Il mittente invia una transazione con value 10 e data "CHARLIE" al contratto. Il contratto aggiorna il proprio storage (la lista diventa [ALICE, BOB, CHARLIE]) e i saldi vengono aggiornati di conseguenza.*

---

## Lifecycle degli Smart Contract

Uno smart contract attraversa tre fasi principali:

![Diagramma del ciclo di vita di uno smart contract: Creation, Interaction, Destruction](images/lezione-19-ethereum-accounts-transactions-gas-img-08.jpg)
*Fig. — Il lifecycle di uno smart contract è una progressione lineare: Creazione → Interazione → Distruzione (opzionale).*

### Creazione

Solo un EOA può creare (fare il *deploy* di) uno smart contract sulla blockchain. La creazione avviene tramite una transazione speciale in cui il campo `to` è **vuoto** (nessun indirizzo di destinazione finché il contratto non è deployato), e il campo `data` contiene il **bytecode compilato** del contratto.

![Formato della transazione di creazione contratto: campo to vuoto, data con bytecode](images/lezione-19-ethereum-accounts-transactions-gas-img-09.jpg)
*Fig. — Transazione di creazione: il campo `to` è vuoto (l'indirizzo del contratto viene generato al deploy), il campo `data` contiene il bytecode EVM del contratto.*

### Interazione

Una volta deployato, il contratto può essere invocato da:
- un **EOA** tramite una transazione che specifica l'indirizzo del contratto e il metodo da chiamare,
- un **altro contratto** tramite un messaggio interno (non una transazione firmata).

![Formato della transazione di interazione con un contratto: to=indirizzo contratto, data=metodo+parametri](images/lezione-19-ethereum-accounts-transactions-gas-img-10.jpg)
*Fig. — Transazione di interazione: `to` contiene l'indirizzo del contratto, `data` codifica il metodo da invocare tramite function selector (primi 4 byte del Keccak-256 del prototipo della funzione) + argomenti ABI-encoded.*

> [!note] Contract-to-Contract
>
> I contratti non possono avviare transazioni autonomamente, ma possono costruire percorsi di esecuzione complessi generando **messaggi** verso altri contratti come risposta a una transazione ricevuta da un EOA o da un altro contratto.

### Caratteristiche di esecuzione

Quando uno smart contract riceve una transazione o un messaggio, viene eseguito dall'**Ethereum Virtual Machine (EVM)**. Le azioni possibili includono:
- calcoli aritmetici/logici,
- scrittura sullo storage interno,
- invio di messaggi ad altri smart contract,
- creazione di nuovi contratti.

### Distruzione

Un contratto può essere eliminato dalla blockchain invocando l'operazione **`selfdestruct`**. La transazione di distruzione contiene nel campo `data` il nome del metodo che chiama `selfdestruct`, e nel campo `to` l'indirizzo del contratto. Dopo la distruzione, il contratto non è più eseguibile.

### Esempio Naive in Solidity

```solidity
pragma solidity ^0.8.0;

contract Crowdsale {
    mapping(address => uint256) public balances;
    uint256 public totalRaised;

    function contribute() public payable {
        require(msg.value > 0, "Contribution amount must be greater than zero");
        balances[msg.sender] += msg.value;
        totalRaised += msg.value;
    }

    function withdraw() public {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No funds available to withdraw");
        balances[msg.sender] = 0;
        payable(msg.sender).transfer(amount);
    }
}
```

Questo semplice contratto di crowdfunding mostra i meccanismi fondamentali di Solidity: un `mapping` per tenere traccia dei contributi, una funzione `payable` per ricevere Ether, e una funzione di prelievo con verifica del saldo e azzeramento prima del trasferimento (per prevenire reentrancy attack).

---

## Il Formato Completo della Transazione

Ogni transazione Ethereum include i seguenti campi, serializzati con lo schema **RLP** (*Recursive Length Prefix*):

![Schema UML del formato completo di una transazione Ethereum](images/lezione-19-ethereum-accounts-transactions-gas-img-11.jpg)
*Fig. — Struttura completa di una transazione Ethereum: nonce, gasLimit, gasPrice, to, value, i tre componenti della firma ECDSA (v, r, s), e data.*

| Campo | Descrizione |
|-------|-------------|
| `nonce` | Numero progressivo di transazioni dell'EOA mittente |
| `gasLimit` | Quantità massima di gas che il mittente è disposto a consumare |
| `gasPrice` | Prezzo in wei per unità di gas (scelto dal mittente) |
| `to` | Indirizzo destinatario (20 byte); vuoto per creazione contratto |
| `value` | Importo in wei da trasferire |
| `v`, `r`, `s` | Componenti della firma ECDSA; permettono di ricavare l'indirizzo del mittente |
| `data` | Payload: bytecode (creazione) o function selector + argomenti (interazione) |

### Il campo `to`

Il campo `to` accetta qualsiasi valore di 20 byte senza validazione: se l'indirizzo è errato o inesistente, l'Ether inviato viene **bruciato** (*burnt*). Rispetto a Bitcoin, Ethereum semplifica radicalmente il formato: un solo indirizzo di output, valore inserito direttamente (nessun riferimento a transazione precedente), nessuno script nel campo destinatario.

### I campi `value` e `data`

I due campi del payload possono essere combinati in modi diversi:

| `value` | `data` | Significato |
|---------|--------|-------------|
| valorizzato | vuoto | Pagamento puro in Ether |
| vuoto | valorizzato | Invocazione di funzione |
| entrambi valorizzati | entrambi valorizzati | Invocazione con trasferimento Ether |

Quando `data` è inviato a un contract account, i primi **4 byte** costituiscono il **function selector** (i primi 4 byte dell'hash Keccak-256 del prototipo della funzione), che identifica univocamente il metodo da invocare. I byte successivi codificano gli argomenti secondo l'ABI Ethereum.

---

## Il Problema dell'Halting e il Gas

Il prezzo della Turing-completezza è l'**halting problem**: non è possibile determinare staticamente se un programma terminerà o girerà all'infinito. Per verificarlo bisogna eseguirlo — ma eseguire codice che non termina su una rete di nodi significa un **denial of service** distribuito. Bitcoin non ha questo problema (il suo linguaggio non è Turing-completo), Ethereum sì.

```javascript
function foo() {
    while (true) { /* Loop forever! */ }
}
```

### La soluzione: il Gas

> [!definition] Gas
>
> Un'unità di misura del costo computazionale associato all'esecuzione di ogni istruzione EVM. Ogni transazione include un budget di gas; l'EVM si ferma (e la transazione fallisce) non appena il gas si esaurisce.

Il gas serve a tre scopi:
1. **Rendere costosi gli attacchi DoS**: chi vuole eseguire codice malevolo deve pagare per ogni ciclo.
2. **Compensare i miner/validatori**: le fee di esecuzione ricompensano chi convalida le transazioni.
3. **Definire il limite computazionale**: l'EVM è una macchina *quasi*-Turing-completa — può eseguire qualsiasi programma purché disponga di gas sufficiente.

### Gas Price e Gas Limit

La **gas price** è il prezzo in Ether per unità di gas, espresso in **gwei** (1 gwei = 10⁹ wei). È il mittente a sceglierla: alta priorità richiede alta gas price, poiché i miner preferiscono le transazioni più remunerative. Il prezzo è variabile e dipende dalla congestione della rete.

Il **gas limit** è la quantità massima di gas che il mittente è disposto a consumare. La fee massima pagabile è:

$$
\text{fee} = \text{gasPrice} \times \text{gasLimit}
$$

Se al termine dell'esecuzione rimane del gas inutilizzato, viene **rimborsato** al mittente. Se il gas si esaurisce prima del completamento, tutte le modifiche di stato vengono **revertite** (ma il gas consumato non viene restituito).

### Ether e le sue denominazioni

![Tabella delle denominazioni dell'Ether: da wei a Megaether](images/lezione-19-ethereum-accounts-transactions-gas-img-12.jpg)
*Fig. — Le denominazioni dell'Ether, ciascuna intitolata a un pioniere dell'informatica: wei (unità base), Babbage (10³), Lovelace (10⁶), Shannon (10⁹), Szabo (10¹²), Finney (10¹⁵), Ether (10¹⁸), Grand (10²¹), Megaether (10²⁴).*

L'unità base è il **wei**: 1 ETH = 10¹⁸ wei. Tutte le operazioni interne di Ethereum lavorano in wei.

### Il meccanismo del Gas: riepilogo

![Diagramma riepilogativo del meccanismo del gas: flusso da TX submission a success/out-of-gas](images/lezione-19-ethereum-accounts-transactions-gas-img-13.jpg)
*Fig. — Riepilogo del meccanismo gas. Il mittente specifica gasLimit e gasPrice (es. 100.000 gas × 20 Gwei = 0.002 ETH upfront). L'EVM esegue consumando gas. Se successo: gas non usato rimborsato. Se out-of-gas: tutte le modifiche revertite, gas consumato NON rimborsato (deterrente contro spam). In basso: tabella dei costi gas per le istruzioni principali.*

### Costi delle operazioni EVM

Il costo in gas di ogni istruzione è fisso e definito nel Yellow Paper di Ethereum. Le operazioni di storage sono di gran lunga le più costose.

![Tabella dei costi gas delle operazioni EVM di base](images/lezione-19-ethereum-accounts-transactions-gas-img-14.jpg)
*Fig. — Costi gas per operazioni di base: ADD/SUB (3 gas), MUL/DIV (5 gas), ADDMOD/MULMOD (8 gas), operazioni bitwise/confronto (3 gas), operazioni stack POP (2), PUSH/DUP/SWAP (3), MLOAD/MSTORE (3).*

![Tabella dei costi gas per operazioni avanzate: JUMP, storage, CREATE, CALL](images/lezione-19-ethereum-accounts-transactions-gas-img-15.jpg)
*Fig. — Costi gas per operazioni avanzate: JUMP (8), JUMPI (10), SLOAD (200), SSTORE (20.000), BALANCE (400), CREATE (32.000), CALL (25.000). Lo storage è deliberatamente costoso per scoraggiare l'uso eccessivo della chain come database.*

### Gas nei messaggi interni

I messaggi interni (da contratto a contratto) **non hanno un proprio gas limit** separato: il gas limit dell'intera catena di esecuzione è quello specificato nella transazione originale dell'EOA, e deve essere sufficiente a coprire tutte le sub-esecuzioni. Se un messaggio interno esaurisce il gas, quella specifica sub-esecuzione viene revertita, ma la transazione padre può continuare se ha gestito il caso d'errore.

---

## L'offerta di ETH e il Mercato delle Fee

### L'offerta di ETH: dalle origini alla supply pre-Merge

Ethereum nacque attraverso un **Initial Coin Offering (ICO)** nel 2014, un evento di crowdfunding pubblico in cui i sostenitori precoci acquistarono ETH usando Bitcoin, prima ancora che la rete fosse operativa. Questa campagna fu cruciale per finanziare lo sviluppo e attirare talenti. Dalla distribuzione iniziale emersero **72 milioni di ETH**, ripartiti tra contribuenti precoci e la Ethereum Foundation.

Prima della transizione al Proof of Stake (il cosiddetto Merge, avvenuto nel settembre 2022), Ethereum era basato sul Proof of Work. I miner ricevevano una **block reward** in ETH come incentivo alla sicurezza della rete, oltre alle gas fee delle transazioni incluse nel blocco. A differenza di Bitcoin — dove i dimezzamenti del reward avvengono automaticamente ogni 210.000 blocchi — in Ethereum la regolazione dell'emissione è **governance-driven**: le modifiche vengono decise dalla comunità attraverso Ethereum Improvement Proposals (EIP) e attivate tramite hard fork.

La progressione storica è la seguente:
- **2015 (genesis):** 5 ETH per blocco
- **2017 (Byzantium):** 3 ETH per blocco
- **2019 (Constantinople):** 2 ETH per blocco

Questa riduzione progressiva abbassò il tasso di inflazione della rete, ma in assenza di un meccanismo sistematico di rimozione dalla circolazione — a meno di perdite accidentali o distruzione volontaria — la supply continuava comunque a crescere.

### Il sistema di fee pre-Merge: il First Price Auction

Prima dell'EIP-1559, le fee di Ethereum seguivano il modello della **first-price auction**: per ogni blocco si apriva un'asta aperta in cui gli utenti dichiaravano il prezzo massimo che erano disposti a pagare per unità di gas (espresso in **gwei**, dove 1 gwei = 0,000000001 ETH). I miner includevano preferibilmente le transazioni con gas price più alto, perché incassavano l'intero importo dichiarato.

> [!definition] First Price Auction
>
> Modello d'asta in cui il vincitore paga esattamente quanto ha offerto, senza rimborso in caso di eccesso. Chi offre di più viene incluso prima.

Questo schema aveva un difetto strutturale: non esisteva un "prezzo giusto" determinato algoritmicamente. Gli utenti dovevano **indovinare** quant'era la domanda corrente, con due scenari negativi simmetrici:
- Se il bid era **troppo basso**, la transazione restava in attesa nel mempool senza essere inclusa.
- Se il bid era **troppo alto**, la transazione veniva inclusa rapidamente ma l'utente **overpagava** senza ricevere alcun rimborso.

> [!example] Bob e l'overpaying
>
> Bob vuole cogliere un'opportunità urgente su Ethereum. Stima competizione elevata e imposta un gas price di 100 gwei. In realtà, la transazione sarebbe stata inclusa con soli 50 gwei. Bob paga il doppio del necessario, poiché non ha strumenti affidabili per stimare il prezzo corretto.

### EIP-1559: la riforma del mercato delle fee

L'EIP-1559, attivato con il London Hard Fork (agosto 2021), ha completamente ridisegnato il meccanismo di fee introducendo quattro innovazioni fondamentali:

1. **Base fee algoritmica** — un prezzo minimo per unità di gas, calcolato dal protocollo e comune a tutte le transazioni del blocco, basato sulla congestione recente.
2. **Burn della base fee** — la base fee viene **bruciata**, cioè rimossa permanentemente dalla circolazione, anziché andare ai miner/validator.
3. **Priority fee (tip)** — un contributo volontario che l'utente aggiunge alla base fee per incentivare i validator a includere la propria transazione.
4. **Blocchi elastici** — la dimensione target di un blocco è fissa, ma i blocchi possono espandersi fino al **doppio del target** durante picchi di domanda.

> [!tip] Perché bruciare la base fee?
>
> Separare la base fee (bruciata) dal tip (ai validator) serve a disaccoppiare l'incentivo economico dei validator dal prezzo di mercato del gas. Se i validator ricevessero l'intera fee, avrebbero interesse a manipolare il mercato gonfiando artificialmente la domanda.

#### baseFeePerGas: il prezzo di mercato algoritmico

La `baseFeePerGas` è un **parametro di protocollo a livello di blocco**, non un campo della transazione: viene calcolata automaticamente e applicata a tutte le transazioni del blocco. L'analogia con Bitcoin è quella dell'aggiustamento della difficoltà: è una forma di **auto-organizzazione del sistema**.

Il meccanismo di aggiustamento segue questa logica:
- Se il blocco precedente era **più che al 50%** della capienza → la base fee **aumenta**
- Se era **esattamente al 50%** → rimane invariata
- Se era **meno del 50%** → **diminuisce**

Il target è che i blocchi siano mediamente al 50% della loro capacità massima. La variazione è **cappata a ±12,5% per blocco**, il che impedisce oscillazioni brusche ma consente adattamento rapido a cambiamenti sostenuti della domanda. Poiché la base fee può cambiare mentre una transazione è ancora in attesa nel mempool, gli utenti specificano valori **massimi** per proteggersi da variazioni impreviste.

#### maxPriorityFeePerGas e maxFeePerGas

In EIP-1559, una transazione include due parametri espliciti:

> [!definition] maxPriorityFeePerGas
>
> Il **tip massimo** che l'utente è disposto a pagare ai validator per prioritizzare l'inclusione. Il validator riceverà `min(maxPriorityFeePerGas, maxFeePerGas - baseFeePerGas)`.

> [!definition] maxFeePerGas
>
> Il **limite massimo assoluto** che l'utente è disposto a pagare per unità di gas. Protegge l'utente da rincari della base fee nel tempo tra submission e inclusione. Deve essere ≥ baseFeePerGas + maxPriorityFeePerGas.

La fee effettivamente pagata sarà: `gas usato × (baseFeePerGas + tip effettivo)`, dove il tip effettivo è `min(maxPriorityFeePerGas, maxFeePerGas - baseFeePerGas)`.

#### Tre casi numerici

> [!example] Caso 1 — fee piena, nessun cap
>
> Transazione EOA→EOA di 1 ETH (21.000 gas). `baseFeePerGas = 100`, `maxPriorityFeePerGas = 20`, `maxFeePerGas = 200`.
>
> `maxFeePerGas > baseFeePerGas + maxPriorityFeePerGas` → nessun cap sul tip.
>
> - Fee totale: 21.000 × (100 + 20) = 2.520.000 gwei = **0,00252 ETH**
> - A paga: 1,00252 ETH; B riceve: 1 ETH
> - Validator ricevono: 0,00042 ETH (21.000 × 20 gwei)
> - Bruciati: 0,0021 ETH (21.000 × 100 gwei)

> [!example] Caso 2 — tip ridotto dal cap
>
> Stessa transazione. `baseFeePerGas = 100`, `maxPriorityFeePerGas = 20`, `maxFeePerGas = 110`.
>
> Tip effettivo = min(20, 110 − 100) = **10 gwei** (il cap abbassa il tip).
>
> - Fee totale: 21.000 × (100 + 10) = 2.310.000 gwei = **0,00231 ETH**
> - Validator ricevono: 0,00021 ETH; Bruciati: 0,0021 ETH
> - La transazione viene inclusa, solo il tip si riduce.

> [!example] Caso 3 — transazione bloccata
>
> `baseFeePerGas = 100`, `maxFeePerGas = 90`. L'utente non copre nemmeno la base fee.
>
> La transazione rimane **pending** nel mempool finché la `baseFeePerGas` non scende sotto 90, oppure viene eliminata.

#### EIP-1559 e la pressione deflazionistica

L'EIP-1559 ha cambiato strutturalmente la politica di emissione di ETH attraverso due meccanismi congiunti:

1. **Riduzione dell'issuance**: i premi al mining sono stati sostituiti da premi allo staking, significativamente più bassi.
2. **Burn della base fee**: una parte del gas viene bruciata ad ogni transazione.

Quando la quantità di ETH bruciata supera quella emessa come ricompensa ai validator, la supply totale di ETH **diminuisce**: ETH diventa **deflazionario**. Questo fenomeno si osserva nei periodi di alta attività on-chain.

---

## L'architettura di Ethereum: i quattro livelli

Ethereum è organizzato in quattro strati funzionali:

![Diagramma Mermaid](images/mermaid-lezione-26-ethereum-2-0-fees-and-tries-01.png)
*Fig. — I quattro livelli dell'architettura Ethereum.*

Il **Data Layer** comprende le strutture dati che rappresentano lo stato del sistema — account, transazioni, ricevute, storage dei contratti — attraverso strutture ad albero basate su Merkle Patricia Trie.

---

## I Trie e il Data Layer

### Il Merkle Patricia Trie (MPT)

Il **Merkle Patricia Trie** è una struttura dati originale introdotta nel Yellow Paper di Ethereum, che combina due strutture classiche:

> [!definition] Merkle Patricia Trie
>
> Albero che unisce il **Patricia Trie** (raggruppamento di prefissi comuni delle chiavi per ricerca efficiente) con il **Merkle Tree** (ogni nodo è l'hash dei propri figli, garantendo integrità e verifica tamper-proof). È la struttura alla base di tutti i trie di Ethereum e della maggior parte delle blockchain EVM-compatibili.

Il Patricia Trie evita di memorizzare ripetutamente sotto-cammini comuni: nodi interni rappresentano prefissi condivisi, riducendo la profondità dell'albero e velocizzando la ricerca. La struttura Merkle garantisce che qualsiasi modifica a un dato foglia si propaghi cambiando gli hash lungo tutto il cammino fino alla radice, rendendo ogni manomissione immediatamente rilevabile.

### I due livelli di Ethereum 2.0

Dopo il Merge, Ethereum è strutturato in due livelli distinti che collaborano:

#### Consensus Layer (Beacon Chain)

Il Consensus Layer gestisce il protocollo di consenso PoS e la validazione. Il suo blocco — il **Beacon Block** — non contiene direttamente transazioni o ricevute, ma include un riferimento al blocco dell'Execution Layer attraverso il campo `execution_payload_header`.

![Beacon Block Header — campi e tipi](images/lezione-26-ethereum-2-0-fees-and-tries-img-01.jpg)
*Fig. — Struttura del Beacon Block Header: gestisce slot, proposer, state root e il collegamento all'Execution Layer.*

#### Execution Layer

L'Execution Layer gestisce le transazioni, i contratti intelligenti e i log. Il suo block header è ricco di radici Merkle che certificano lo stato del sistema:

![Execution Layer Block Header — campi e tipi](images/lezione-26-ethereum-2-0-fees-and-tries-img-02.jpg)
*Fig. — Struttura dell'Execution Layer Block Header: stateRoot, transactionsRoot, receiptsRoot e logsBloom sono le radici dei trie principali.*

I campi chiave per il Data Layer sono:
- `stateRoot` → radice del World State Trie
- `transactionsRoot` → radice del Transaction Trie
- `receiptsRoot` → radice del Receipts Trie
- `logsBloom` → Bloom filter aggregato di tutti i log del blocco

### I Trie dell'Execution Layer

La slide seguente mostra la relazione tra il blocco e i quattro trie principali:

![Diagramma dei trie dell'Execution Layer](images/lezione-26-ethereum-2-0-fees-and-tries-img-03.jpg)
*Fig. — Il blocco punta tramite radici hash al World State Trie, al Receipts Trie e al Transactions Trie. Il World State Trie punta all'Account Storage Trie per ogni contratto.*

![Diagramma Mermaid](images/mermaid-lezione-26-ethereum-2-0-fees-and-tries-02.png)
*Fig. — Relazione tra Block Header e i quattro trie dell'Execution Layer.*

> [!note] Quattro trie distinti
>
> - **World State Trie**: mappa ogni indirizzo → stato dell'account (nonce, balance, codeHash, storageRoot)
> - **Transaction Trie**: albero di tutte le transazioni del blocco; la radice è nel block header
> - **Receipts Trie**: albero delle ricevute di esecuzione (una per transazione)
> - **Account Storage Trie**: uno per ogni contratto, contiene le variabili di storage del contratto

### Il Transaction Trie

Il Transaction Trie è un MPT che indicizza tutte le transazioni di un blocco. Ogni transazione viene hashata, e gli hash vengono combinati fino a produrre un unico **root hash** incluso nel block header. Questo permette di:
- Rilevare qualsiasi modifica a una transazione (il root hash cambia)
- Dimostrare l'appartenenza di una transazione a un blocco senza scaricare il blocco completo (**Merkle proof**)
- Effettuare ricerche efficienti

### Logging e Transaction Receipt

#### Perché i log

Consideriamo un contratto NFT. I dati di proprietà corrente dei token sono salvati nell'**account storage** — lo stato on-chain accessibile dal contratto. Ma altri tipi di informazione non richiedono di essere nello storage del contratto:

- La **storia delle proprietà** interessa analisti e investitori, ma il contratto non ne ha bisogno durante l'esecuzione.
- Le **notifiche al frontend** sono necessarie per confermare all'utente che un mint è avvenuto — ma le transazioni sono asincrone, quindi il contratto non può restituire un valore direttamente all'interfaccia.

La soluzione è che il contratto **emetta un evento** (`emit`), che viene scritto nei **log** della ricevuta di transazione. Il frontend può ascoltare questi log e reagire.

> [!tip] Log vs Storage
>
> Il log storage è **molto più economico** dell'account storage in termini di gas. È la scelta corretta per dati che non devono essere letti dal contratto stesso, ma solo da applicazioni esterne (DApp, analytics, indexer come The Graph).

#### Struttura del Transaction Receipt

> [!definition] Transaction Receipt
>
> Struttura dati che registra l'esito dell'esecuzione di una transazione una volta inclusa in un blocco. Contiene:
> - **status**: 0 (fallita) o 1 (successo)
> - **cumulativeGasUsed**: gas consumato da tutte le transazioni precedenti nel blocco, inclusa quella corrente
> - **logs**: lista di log entries emesse dal contratto durante l'esecuzione
> - **logsBloom**: Bloom filter da 2048 bit costruito sulle log entries, per ricerca rapida

![Smart Contract → Transaction Receipt](images/lezione-26-ethereum-2-0-fees-and-tries-img-04.jpg)
*Fig. — Un contratto Solidity con evento Transfer emette il log quando viene chiamata send(); il log viene registrato nella ricevuta della transazione.*

#### Status

Il campo `status` è 0 o 1. Poiché l'esecuzione è asincrona, il chiamante deve attendere che il blocco venga incluso per leggere lo status dalla ricevuta e determinare se la transazione ha avuto successo.

#### cumulativeGasUsed

Il campo `gasUsed` nella ricevuta **non** è il gas consumato dalla singola transazione: è il **totale cumulativo** di tutto il gas utilizzato dalle transazioni dalla prima alla corrente nel blocco, inclusa quest'ultima.

![Schema gas cumulativo per transazione](images/lezione-26-ethereum-2-0-fees-and-tries-img-05.jpg)
*Fig. — Per la transazione N, gasUsed nella ricevuta e la somma del gas di tutte le transazioni da 1 a N. Nell'esempio, la ricevuta della tx 3 riporta 106.000 gwei = 21.000 + 50.000 + 35.000.*

### I parametri Indexed e la struttura dei Log

#### Parametri indexed in Solidity

Nei contratti Solidity, i parametri di un evento possono essere dichiarati `indexed`. Questo indica che quei valori devono essere salvati nei **topics** del log (campi indicizzati), anziché nel campo `data` generico.

![Codice Solidity con parametri indexed](images/lezione-26-ethereum-2-0-fees-and-tries-img-06.jpg)
*Fig. — Nel contratto SimpleToken, from e to sono marcati indexed — vengono salvati nei topics della ricevuta per abilitare ricerche efficienti.*

I parametri `indexed` abilitano **ricerche e filtraggio efficienti**: per esempio, trovare tutti i trasferimenti di un token effettuati da un dato indirizzo, oppure tutti i token venduti da un utente. Sono salvati nei campi `topics` della ricevuta, mentre i parametri non-indexed finiscono nel campo `data`.

#### La struttura completa di un evento loggato

![Evento Transfer — struttura completa nella ricevuta](images/lezione-26-ethereum-2-0-fees-and-tries-img-07.jpg)
*Fig. — A sinistra il contratto Token con l'evento Transfer; a destra la ricevuta con topics (event signature + from + to) e data (amount non-indexed).*

La struttura di un log entry nella ricevuta è:
- `address`: indirizzo del contratto che ha emesso l'evento
- `topics[0]`: keccak256 della firma dell'evento (es. `Transfer(address,address,uint256)`)
- `topics[1]`, `topics[2]`, ...: parametri `indexed` hashati
- `data`: parametri non-indexed codificati in ABI

### LogsBloom: filtraggio efficiente con Bloom Filter

Cercare tutte le transazioni di un blocco che coinvolgono un certo indirizzo richiederebbe di analizzare tutti i log di tutte le transazioni — un'operazione costosa. La soluzione è il **logsBloom**: un [[Bloom Filter]] da 2048 bit (256 byte) che riassume il contenuto dei log.

#### LogsBloom nella ricevuta (livello transazione)

![LogsBloom nella ricevuta — Bloom Filter da 2048 bit](images/lezione-26-ethereum-2-0-fees-and-tries-img-08.jpg)
*Fig. — Per ogni transazione, logsBloom e un Bloom filter costruito sugli indirizzi e i topics dei log con keccak256 e 3 bit impostati nel vettore da 2048 bit.*

Il processo di costruzione:
1. Per ogni elemento (address o topic) nei log: calcola `keccak256(elemento)`
2. Deriva 3 posizioni nel vettore da 2048 bit usando 3 hash diversi
3. Imposta a 1 i 3 bit corrispondenti

#### LogsBloom nel block header (livello blocco)

![LogsBloom nel Block Header — OR bitwise di tutti i receipt](images/lezione-26-ethereum-2-0-fees-and-tries-img-09.jpg)
*Fig. — Il logsBloom del block header e l'OR bitwise dei logsBloom di tutte le ricevute del blocco.*

Il `logsBloom` del block header è l'**OR bitwise** dei logsBloom di tutte le ricevute nel blocco. Questo permette una ricerca a due livelli:
1. Controlla il `logsBloom` del block header: se il bit cercato è 0, il blocco non contiene quell'evento (nessun falso negativo).
2. Solo se positivo, scendi a esaminare le singole ricevute.

> [!warning] Falsi positivi nel Bloom Filter
>
> Il Bloom Filter garantisce assenza di falsi negativi (se un elemento è nel set, il filtro lo conferma sempre), ma ammette **falsi positivi** (potrebbe indicare la presenza di un elemento che non c'è). Per questo motivo, dopo aver trovato un blocco candidato tramite il Bloom Filter, occorre verificare i dati effettivi.

### Il Transaction Receipt Trie e il Storage Trie

#### Il Transaction Receipt Trie

![Transaction Receipt Trie — sequence diagram](images/lezione-26-ethereum-2-0-fees-and-tries-img-10.jpg)
*Fig. — Il Receipt Trie punta alle ricevute con Gas Used, Logs, Bloom Filter e Status Code. Il sequence diagram mostra l'interazione utente-World State Trie-Receipt Trie durante deploy multipli.*

Le ricevute di tutte le transazioni di un blocco sono indicizzate in un MPT. La radice di questo trie è il campo `receiptsRoot` del block header. Quando un utente vuole sapere se una transazione ha avuto successo o vuole recuperare gli eventi emessi, può richiedere una Merkle proof al nodo, senza dover scaricare l'intero blocco.

#### Il Storage Trie

![Storage Trie — lettura/scrittura variabili contratto](images/lezione-26-ethereum-2-0-fees-and-tries-img-11.jpg)
*Fig. — Il campo storageRoot punta all'Account Storage Trie con uno slot per ogni contratto. Il sequence diagram mostra tre chiamate successive con lookup e aggiornamento del valore.*

Ogni account contratto ha il proprio **Account Storage Trie**, a cui si accede tramite il campo `storageRoot` dello World State Trie. Ogni variabile di stato del contratto occupa uno **slot** nell'albero. Ogni modifica di una variabile di storage aggiorna la radice del trie dell'account, che a sua volta aggiorna la radice dello World State Trie — propagazione tipica della struttura Merkle.

---

## Il Consenso: Proof of Stake

### Il Problema del Consenso Distribuito

Il consenso distribuito nasce da una sfida fondamentale: costruire un sistema affidabile su un'infrastruttura inaffidabile. Nell'ecosistema blockchain, "inaffidabile" significa che i nodi comunicano su Internet — con banda limitata, alta latenza, perdita di pacchetti — e possono comportarsi in modo arbitrariamente difettoso: possono semplicemente andare offline, seguire una versione diversa del protocollo, o tentare attivamente di ingannare altri nodi pubblicando messaggi contraddittori. L'obiettivo del consenso è fare in modo che decine di migliaia di nodi indipendenti, sparsi per il mondo, procedano in modo completamente sincronizzato.

#### Il Problema dei Generali Bizantini

Il modello teorico di riferimento è il **Byzantine Generals Problem** (problema dei generali bizantini). Nell'analogia classica, un esercito circonda una città e i generali devono decidere unanimemente se attaccare o ritirarsi: possono comunicare solo tramite messaggeri, e alcuni generali potrebbero essere traditori.

I "traditori" esibiscono un **comportamento bizantino**: possono ritardare o riordinare messaggi, mentire, inviare messaggi contraddittori a destinatari diversi, o non rispondere affatto. Il requisito del consenso è che tutti i generali leali decidano lo stesso piano d'azione, e che nessun numero di traditori al di sotto di una certa soglia possa portarli ad adottare piani contraddittori.

### Safety e Liveness

Due proprietà fondamentali definiscono la qualità di un protocollo di consenso.

> [!definition] Safety — "Non accade mai nulla di brutto"
>
> Il sistema non raggiunge mai uno stato scorretto o inconsistente. Nel contesto della blockchain: nessun nodo onesto decide valori diversi sullo stesso blocco. La safety corrisponde all'assenza di conflitti e fork permanenti.

> [!definition] Liveness — "Prima o poi accade qualcosa di buono"
>
> Il sistema non si blocca indefinitamente. Nella blockchain: le transazioni vengono eventualmente incluse in un blocco, e nuovi blocchi vengono prodotti continuamente. La violazione della liveness è una situazione di stallo.

Il **Nakamoto Consensus** di Bitcoin sceglie deliberatamente di privilegiare la liveness rispetto alla safety: la catena continua sempre a crescere (always available), ma accetta inconsistenze temporanee sotto forma di fork, che vengono risolti applicando la regola della catena più lunga. La safety in Bitcoin è quindi *probabilistica*: non c'è finality assoluta, ma più conferme accumulate, più è improbabile un'inversione di catena.

> [!warning] CAP Theorem
>
> Il teorema CAP (Consistency, Availability, Partition Tolerance) afferma che, in presenza di una partizione di rete, un sistema distribuito deve scegliere tra consistenza (nessun nodo vede dati obsoleti) e disponibilità (ogni nodo risponde sempre). Non è possibile garantire entrambe simultaneamente.

---

## Dalla Proof of Work alla Proof of Stake

Ethereum nacque con un meccanismo di consenso **Proof of Work**, identico per principio a quello di Bitcoin. Tuttavia, il mining Bitcoin ha costi enormi: consuma quantità sproporzionate di energia, e i mining pool controllano porzioni crescenti della catena, erodendo la decentralizzazione. Le alternative al PoW includono:

- **Proof of Stake** (Ethereum 2.0, Algorand, Cardano, Solana)
- **Delegated Proof of Stake** (Steemit, EOS)
- **Byzantine Consensus** (Hyperledger)

Nel settembre 2022, con l'evento noto come **The Merge**, la rete è passata al **Proof of Stake**.

![Diagramma del Merge: Ethereum Mainnet e Beacon Chain](images/lezione-19-ethereum-accounts-transactions-gas-img-01.jpg)
*Fig. — The Merge (settembre 2022): la Ethereum Mainnet (PoW) converge con la Beacon Chain (PoS), attiva in parallelo dal 2020. Da quel momento, il consenso è gestito interamente da PoS.*

![Diagramma Mermaid](images/mermaid-lezione-25-ethereum-consensus-proof-of-stake-01.png)
*Fig. — Timeline degli upgrade del Consensus Layer di Ethereum 2.0, da Beacon Chain a Deneb.*

La **Beacon Chain** è stata una rete PoS completamente indipendente che ha funzionato in parallelo alla Mainnet Ethereum per quasi due anni. Il suo scopo era supportare la transizione senza interrompere il servizio. **The Merge** del 15 settembre 2022 ha unito la Execution Layer (Mainnet) con la Consensus Layer (Beacon Chain), completando il passaggio da PoW a PoS.

---

## Gasper: LMD GHOST + Casper FFG

Il protocollo di consenso di Ethereum PoS è detto **Gasper** e combina due meccanismi distinti con ruoli complementari:

> [!definition] Gasper
>
> Gasper = **LMD GHOST** (fork choice, liveness) + **Casper FFG** (finality gadget, safety). LMD GHOST sceglie la testa della catena in presenza di fork; Casper FFG aggiunge la finalità ai checkpoint, rendendo certi blocchi irrevocabili.

Questa architettura riflette la posizione di Ethereum rispetto al trade-off del CAP theorem: in condizioni normali, offre sia safety che liveness; in presenza di partizioni di rete, privilegia la liveness (i nodi continuano a produrre blocchi), ma la finalità può interrompersi.

> [!tip] Perché non solo un protocollo?
>
> LMD GHOST da solo garantisce che la catena cresca sempre, ma non fornisce garanzie di irrevocabilità — i blocchi possono sempre essere riorganizzati. Casper FFG da solo richiederebbe una supermajority in ogni round e si bloccherebbe se troppi validatori fossero offline. La combinazione bilancia i due estremi.

---

## I Validatori

### Ruolo e Incentivi

In Ethereum PoS non esistono miner. Al loro posto operano i **validatori** (validators): nodi che bloccano ETH come garanzia e partecipano al consenso. Ogni validatore svolge due ruoli:

- **Block proposer** (raramente): viene selezionato per creare un nuovo blocco in uno slot specifico, scegliendo e ordinando le transazioni pendenti.
- **Attester** (la maggior parte del tempo): vota sui blocchi proposti, confermando quale sia la testa corretta della catena.

### Diventare un Validatore

Per diventare validatore è necessario depositare esattamente **32 ETH** in un apposito *deposit smart contract*. Il deposito ha una funzione analoga al **collaterale** in finanza: un asset offerto come garanzia. Se il validatore si comporta correttamente, guadagna ricompense; se agisce in modo malevolo o negligente, può essere **slashed**, perdendo una porzione dello stake.

> [!note] Perché 32 ETH fissi?
>
> Un importo fisso permette di trattare ogni validatore in modo uguale nel calcolo dei voti. Chiunque può verificare che un validatore abbia depositato la somma corretta consultando il contratto pubblicamente.

Il sistema è altamente partecipativo: attualmente ci sono circa **1 milione** di istanze di validatori attivi, rendendolo genuinamente democratico.

### Staking senza 32 ETH

Chi non dispone di 32 ETH può partecipare tramite **staking pools** come Lido o Rocket Pool, o exchange centralizzati come Coinbase o Binance. In uno staking pool, gli ETH vengono aggregati da operatori professionali; in cambio si riceve un token che accumula le ricompense dello staking e può essere usato nei servizi DeFi.

---

## Slot ed Epoch

A differenza del PoW, che è un protocollo asincrono senza relazione con il tempo reale, il PoS di Ethereum organizza il tempo in unità discrete.

> [!definition] Slot ed Epoch
>
> - **Slot**: finestra temporale di **12 secondi**, durante la quale un comitato di validatori può votare per un beacon block.
> - **Epoch**: sequenza di **32 slot** = **6,4 minuti**. In un'epoch, ogni validatore attivo ha esattamente un'opportunità di partecipare.

![Diagramma Mermaid](images/mermaid-lezione-25-ethereum-consensus-proof-of-stake-02.png)
*Fig. — Struttura temporale di epoch e slot in Ethereum PoS.*

All'interno di ogni slot si svolgono tre fasi: (1) un singolo validatore propone un blocco e lo diffonde via gossip; (2) tutti gli altri membri del comitato emettono il loro voto (attestation); (3) negli ultimi 4 secondi, i voti vengono aggregati e inoltrati al proposer del prossimo slot.

---

## RANDAO: Randomness Decentralizzata

Ethereum ha bisogno di casualità verificabile per scegliere i block proposer e assegnare i validatori ai comitati. Non è possibile affidarsi a un'entità centrale (che potrebbe barare) né a un valore prevedibile (che potrebbe essere sfruttato). La soluzione è **RANDAO**: un protocollo distribuito per generare numeri casuali che nessun singolo partecipante può controllare.

### Come Funziona RANDAO

Il meccanismo segue uno schema commit-reveal in quattro passi:

![Diagramma Mermaid](images/mermaid-lezione-25-ethereum-consensus-proof-of-stake-03.png)
*Fig. — Il protocollo RANDAO: dalla generazione del segreto all'assegnazione dei ruoli.*

Il risultato finale $R = n_1 \oplus n_2 \oplus n_3 \oplus \ldots \oplus n_k$ è imprevedibile perché nessuno conosce tutti i segreti prima della reveal, è inalterabile dopo il commit, è decentralizzato poiché ogni validatore contribuisce, ed è verificabile pubblicamente.

L'output RANDAO viene usato come seed per mescolare (*shuffle*) i validatori e assegnarli a block proposer, comitati, aggregatori e sync committees, con un anticipo di **due epoch**.

---

## LMD GHOST: Fork Choice

### Perché si Formano i Fork

In Ethereum, dove i blocchi vengono prodotti ogni 12 secondi, il tempo di propagazione dei blocchi è dell'ordine di grandezza degli slot stessi. Non tutti i validatori vedono tutti i blocchi in tempo per attestarli o costruirci sopra. Il risultato è un albero di blocchi, non una singola catena.

### L'Algoritmo LMD GHOST

**LMD GHOST** (*Latest Message Driven Greedy Heaviest-Observed Sub-Tree*) è la regola di fork choice di Ethereum. L'intuizione centrale è sostituire la "catena più lunga" di Bitcoin con la "catena con più stake accumulato", usando solo il voto più recente di ogni validatore.

> [!definition] LMD GHOST
>
> Partendo dall'ultimo blocco finalizzato, l'algoritmo scende l'albero scegliendo ricorsivamente il ramo con il maggior peso totale. Il peso di un ramo è la somma del peso di tutti i voti per quel blocco e per tutti i suoi discendenti. Solo il messaggio più recente (LMD) di ogni validatore viene considerato.

Il peso di un voto è proporzionale al **bilancio effettivo** del validatore al momento del voto: deposito iniziale di 32 ETH, più le ricompense accumulate, meno le penalità subite. Quindi non conta il numero di voti, ma la quantità di ETH in staking che li sostiene.

![Diagramma Mermaid](images/mermaid-lezione-25-ethereum-consensus-proof-of-stake-04.png)
*Fig. — LMD GHOST: il ramo superiore (60→50→20) vince sul ramo inferiore più lungo (40→30→30→30) perché ha più stake accumulato.*

> [!tip] Intuizione chiave di LMD GHOST
>
> Un voto per un blocco figlio è implicitamente un voto per tutti i suoi antenati. Se due figli dello stesso blocco padre ricevono voti da validatori diversi, entrambi i gruppi stanno confermando il padre. GHOST sfrutta al massimo tutte le informazioni disponibili, anziché scartarle come farebbe la longest chain rule.

---

## Il Problema del "Nothing at Stake"

In PoW, produrre un blocco è costoso in termini computazionali: questo incentiva i miner a concentrare le risorse su un'unica catena. In PoS naive, creare nuovi blocchi è quasi gratuito, creando il problema del **nothing at stake**: un validatore razionale potrebbe votare per tutte le catene concorrenti contemporaneamente, massimizzando la probabilità di essere sul lato vincente indipendentemente dall'esito.

Le conseguenze sono severe: più fork perché i validatori attestano tutti i rami, risorse sprecate su catene orfane, tempi di finalità più lunghi, e vulnerabilità agli attacchi di double-spending.

### Lo Slashing come Soluzione

Ethereum risolve questo problema con il **slashing**: se un validatore viene trovato in *equivocazione* (ha firmato due blocchi diversi per lo stesso slot, o ha violato le regole di Casper FFG), viene punito con la rimozione di una parte del suo stake e l'espulsione dal protocollo.

> [!warning] Slashing accidentale
>
> La maggior parte degli eventi di slashing non è dolosa: è dovuta a errori operativi come avere due client attivi con la stessa chiave (es. nodo principale + nodo di backup entrambi ON), configurazioni errate di Docker/Kubernetes, o failover senza spegnere l'istanza precedente. Un validatore deve comportarsi come una singola entità.

---

## Casper FFG: Finality Gadget

### Il Concetto di Finality

In Bitcoin la finality è probabilistica: più conferme, meno probabile la reversione, ma mai impossibile. **Casper FFG** (*Friendly Finality Gadget*) è un protocollo *meta-consenso* che aggiunge finality assoluta a un protocollo sottostante. In Ethereum, il protocollo sottostante è LMD GHOST.

> [!definition] Casper FFG
>
> Casper FFG è un overlay su LMD GHOST che opera su scala di epoch (non di singolo slot). Identifica blocchi speciali chiamati **checkpoint** e, tramite un processo di votazione a supermajority, li porta allo stato di *justified* prima, e infine *finalized*.

### Checkpoint, Justification e Finalization

Il primo blocco di ogni epoch è definito **checkpoint**. Ogni validatore produce esattamente un'attestazione per epoch, che contiene due voti:

- **SOURCE**: il checkpoint dell'epoch precedente già giustificato ("costruisco sulla catena giustificata all'epoch $e-1$")
- **TARGET**: il checkpoint dell'epoch corrente ("voto per questa come testa della catena all'epoch $e$")

Il formato di un'attestazione è:

| Campo | Contenuto |
|---|---|
| `slot` | slot 0 dell'epoch $e$ |
| `index` | indice del validatore |
| `source` | checkpoint giustificato dell'epoch $e-1$ |
| `target` | checkpoint candidato dell'epoch $e$ |
| `signature` | firma BLS del validatore |

Quando più di $2/3$ del totale dello stake (pesato per bilancio effettivo) vota per lo stesso checkpoint, quel checkpoint diventa **justified**. Il checkpoint della fonte (source) del round precedente diventa a sua volta **finalized**.

![Diagramma Mermaid](images/mermaid-lezione-25-ethereum-consensus-proof-of-stake-05.png)
*Fig. — Il processo di justification e finalization in Casper FFG: due supermajority consecutive portano C1 alla finalità.*

### Perché Due Supermajority Consecutive Garantiscono la Finalità

La prova è elegante e si basa sul principio di inclusione-esclusione. Siano $S_1$ e $S_2$ i due insiemi di validatori che formano la supermajority in due epoch consecutive. Per definizione:

$$|S_1| \geq \frac{2}{3} N \qquad |S_2| \geq \frac{2}{3} N$$

dove $N$ è il totale dello stake. Applicando il principio di inclusione-esclusione, poiché $|S_1 \cup S_2| \leq N$:

$$|S_1 \cap S_2| = |S_1| + |S_2| - |S_1 \cup S_2| \geq \frac{2}{3}N + \frac{2}{3}N - N = \frac{1}{3}N$$

L'intersezione è quindi almeno $1/3$ dello stake totale. Qualsiasi tentativo di costruire una catena conflittuale richiederebbe a questi validatori di votare in modo inconsistente tra i due epoch, incorrendo nello slashing. Un attacco che reverta un blocco finalizzato costerebbe la bruciatura di almeno $1/3$ di tutto lo stake in Ethereum — miliardi di dollari — rendendo l'attacco economicamente irrazionale.

> [!abstract] Sintesi del meccanismo di finality
>
> C1 si finalizza quando: (1) nel Round 1 più di 2/3 dello stake vota C2 con sorgente C1 (C2 diventa justified); (2) nel Round 2 più di 2/3 dello stake vota C3 con sorgente C2 (C2 diventa justified per la seconda volta; C1 diventa finalized). La sovrapposizione obbligatoria di almeno 1/3 dello stake tra i due round rende impossibile una revisione senza un costo economico proibitivo.

---

## Il Traffico di Rete

La scala di Ethereum PoS è senza precedenti nel consenso distribuito: in 384 secondi (un'epoch), oltre **500.000 messaggi** devono essere propagati rispettando vincoli temporali rigidi. Nessun altro protocollo di consenso è stato progettato per un numero simile di partecipanti attivi.

Per contenere il traffico, Ethereum usa due meccanismi:
- **Message aggregation**: i comitati sono suddivisi in sottoreti; un validatore aggregatore raccoglie le firme di tutti i membri e le combina in una sola usando firme **BLS** (*Boneh-Lynn-Shacham*), che consentono di aggregare $n$ firme in una singola firma verificabile.
- **Node aggregators**: ruoli specializzati all'interno di ogni comitato.

---

## Ricompense e Penalità

Il comportamento dei validatori è regolato da un sistema di incentivi economici:

| Comportamento | Conseguenza |
|---|---|
| Attestazione corretta e tempestiva | Micro-ricompensa proporzionale al bilancio |
| Attestazione inclusa nel blocco successivo | Ricompensa massima |
| Attestazione mancante, tardiva o errata | Penalità |
| Block proposer che include attestazioni | Ricompensa proporzionale al numero di attestazioni |
| Equivocazione (doppio voto/proposta) | Slashing: perdita di stake + espulsione |

---

## Bitcoin vs. Ethereum: confronto finale

![Tabella comparativa tra Ethereum e Bitcoin: caratteristiche principali](images/lezione-19-ethereum-accounts-transactions-gas-img-16.jpg)
*Fig. — Confronto sistematico tra Ethereum (2015, Vitalik Buterin) e Bitcoin (2009, Satoshi Nakamoto): use case, modello blockchain, consenso, supply, velocità, sicurezza e community.*

| Feature | Ethereum | Bitcoin |
|---------|----------|---------|
| Inception | 2015 | 2009 |
| Fondatore | Vitalik Buterin | Satoshi Nakamoto |
| Use case principale | Smart Contracts, DApps, DeFi | Store of value, p2p transactions |
| Tecnologia | Account-based, EVM | UTXO-based |
| Consenso | PoS (da settembre 2022) | PoW |
| Supply massima | Nessun limite fisso | 21 milioni di BTC |
| Linguaggio contratti | Solidity (Turing-completo) | Script (non Turing-completo) |
| P2P layer | Kademlia | Protocollo proprietario |

> [!note] Kademlia in Ethereum
>
> Ethereum usa [[Kademlia]] come protocollo P2P per la peer discovery, a differenza di Bitcoin che ha sviluppato il proprio protocollo di gossip. Kademlia era già stato studiato nelle lezioni precedenti come DHT efficiente.

![Tabella comparativa Bitcoin vs Ethereum](images/lezione-26-ethereum-2-0-fees-and-tries-img-12.jpg)
*Fig. — Confronto su 14 dimensioni: anno di lancio, scopo, consenso, block time, supply model, transaction model, smart contracts, fees, use cases, state model e altro.*

> [!abstract] Differenze strutturali chiave
>
> - **Modello transazionale**: Bitcoin usa UTXO (Unspent Transaction Outputs), Ethereum usa un modello account-based con stato globale.
> - **Smart contract**: Bitcoin ha Script (limitato, non Turing-complete); Ethereum ha l'EVM con Solidity/Vyper (Turing-complete).
> - **Supply model**: Bitcoin ha un cap fisso di 21 milioni; Ethereum non ha cap fisso ma EIP-1559 introduce pressione deflazionistica tramite burn.
> - **Block time**: ~10 minuti per Bitcoin, ~12 secondi per Ethereum.
> - **Use cases**: Bitcoin è ottimizzato per pagamenti e riserva di valore ("digital gold"); Ethereum è una piattaforma programmabile per DeFi, NFT, DAO, dApp.
