# Capitolo 2 - Fondamenti Crittografici e Strutture Dati

## Crittografia per P2P e Blockchain

Due strumenti crittografici sono alla base di blockchain e DHT: le **funzioni di hash** (collegano i blocchi rendendoli tamper-proof) e le **firme digitali** (impediscono agli utenti di ripudiare le proprie azioni). Strumenti più avanzati — zero knowledge, strutture dati autenticate, accumulatori crittografici — verranno trattati più avanti nel corso.

---

### Funzioni di Hash Crittografiche

Una funzione di hash converte una stringa binaria di lunghezza arbitraria (anche 0) in una stringa di lunghezza fissa. L'output — detto *digest*, *fingerprint* o informalmente *checksum* — ha sempre la stessa dimensione indipendentemente dall'input (video, audio, testo, eseguibili).

Per le strutture dati ordinarie, una funzione hash deve essere: deterministica, efficiente da calcolare (es. `y = x mod table_dim`), pseudo-casuale per distribuire uniformemente gli elementi, minimizzare le collisioni. Le funzioni hash **crittografiche** aggiungono ulteriori proprietà di sicurezza.

#### Proprietà Fondamentali

**Determinismo** — La stessa funzione hash applicata più volte allo stesso documento produce sempre lo stesso risultato.

**Fast Computation** — L'hash deve essere computazionalmente efficiente da calcolare.

**One-Way (Pre-image Resistance)** — Dato un hash $y$, deve essere computazionalmente impossibile trovare un $x$ tale che $H(x) = y$. Con SHA-1 (160 bit) un attacco brute-force richiederebbe $2^{71}$ anni.

**Avalanche Effect** — Un singolo bit di differenza nell'input produce un hash completamente diverso; cambiare anche solo 1 bit modifica tutto l'output.

**Collision Resistance** — Le collisioni esistono matematicamente (per il *Pigeonhole Principle*: con più input che output, almeno un output deve corrispondere a più di un input), ma devono essere computazionalmente impossibili da costruire intenzionalmente.

> [!example] Pigeonhole Principle
>
> Se si scelgono 51 numeri interi tra 1 e 100, almeno due devono essere consecutivi. Dimostrazione: le "buche" sono le coppie {1,2}, {3,4}, ..., {99,100} — 50 coppie per 51 numeri. Per il principio del piccione, almeno una buca contiene due piccioni.

**Weak Collision Resistance (Second Pre-image Resistance)** — Dato un input $x$ noto, deve essere difficile trovare un $x' \neq x$ tale che $H(x') = H(x)$. Questo previene, ad esempio, la distribuzione di software corrotto spacciato per autentico: un attaccante non può generare un file malevolo con lo stesso hash del software legittimo.

#### Il Paradosso del Compleanno e la Sicurezza Effettiva

Per trovare una collisione in modo garantito bastano $2^n + 1$ input distinti (per Pigeonhole). Tuttavia il **Birthday Paradox** abbassa drasticamente il limite pratico:

In una stanza di $n$ persone scelte a caso, $n = 23$ è sufficiente perché la probabilità che due condividano il compleanno superi il 50%. Questo perché la seconda persona deve evitare 1 compleanno su 365, la terza 2 su 365, ecc.; il prodotto delle probabilità di "nessuna collisione" scende rapidamente. Formalmente, con $\sqrt{2^n} = 2^{n/2}$ input casuali si ha già alta probabilità di collisione.

Per una funzione hash con $n$-bit di output, bastano $\approx 2^{n/2}$ input casuali per trovare una collisione con probabilità 0,5. La sicurezza effettiva è quindi **metà dei bit di output**.

> [!warning] Quantificazione brute force
>
> Se un computer calcola 10.000 hash/sec, calcolare $2^{128}$ hash richiederebbe $10^{27}$ anni. Anche se tutti i computer mai costruiti dall'umanità avessero calcolato sin dall'inizio dell'universo, la probabilità di aver trovato una collisione sarebbe infinitesimamente piccola.

| Algoritmo | Bit output | Sicurezza effettiva | Stato |
|---|---|---|---|
| MD2, MD4 | 128 bit | 64 bit | Ritirati — vulnerabili |
| MD5 | 128 bit | 64 bit | Vulnerabile (ok per app non di sicurezza) |
| SHA-1 | 160 bit | 80 bit | Ritirato — debole |
| SHA-256 | 256 bit | 128 bit | Usato da Bitcoin — sicuro |
| SHA-512 | 512 bit | 256 bit | Corrente — massima sicurezza |

Almeno **80 bit** di sicurezza sono necessari. Le funzioni hash hanno storicamente una vita utile di circa **10 anni**. Lo standard attuale è **SHA-3** (Keccak), adottato anche da Ethereum.

> [!warning] Hash non crittografici
>
> La **parità a blocco a 8 bit**: è banale trovare una collisione invertendo un numero pari di bit nella stessa colonna. Il **CRC** (Cyclic Redundancy Check) è il resto di una divisione polinomiale lunga — ottimo per rilevare burst error nelle comunicazioni, ma facile da collidere intenzionalmente. CRC è stato usato erroneamente nel protocollo **WEP** (Wired Equivalent Privacy) dove si richiedeva integrità crittografica.

#### Cryptanalysis

Oltre al brute force, la **crittoanalisi** cerca debolezze logiche nell'algoritmo: scorciatoie, buchi nella funzione. Una funzione si dice *broken* quando è possibile trovare collisioni significativamente più velocemente del brute force.

#### Proprietà Avanzate

**Hiding** — Dato $H(R \| x)$, deve essere impossibile ricavare informazioni su $x$. Formalmente: $H$ è *hiding* se, scelto $R$ da una distribuzione con alta min-entropy (nessun valore più probabile degli altri), dato $H(R \| x)$ è computazionalmente impossibile trovare $x$.

Le funzioni base non garantiscono hiding se lo spazio di input è piccolo e prevedibile (es. password), rendendole vulnerabili ai **Rainbow Table Attack**: si pre-calcolano le hash di tutte le password possibili in una tabella; al login si cerca il hash nel database. La soluzione è concatenare un valore casuale $R$ a 256 bit ad alta min-entropy: $H(R \| x)$, rendendo lo spazio di ricerca enorme.

**Puzzle-Friendliness** — Per qualsiasi output target $y$ e valore casuale $k$ ad alta min-entropy, trovare $x$ tale che $H(k \| x) = y$ richiede un attacco esaustivo in tempo $\approx 2^n$, senza scorciatoie algoritmiche. Questa proprietà implica che nessuna strategia di risoluzione è significativamente migliore della ricerca esaustiva.

---

### Applicazioni delle Funzioni di Hash

#### Applicazioni non-blockchain

**Gestione password** — I sistemi memorizzano $H(\text{password})$ invece del testo in chiaro. Anche in caso di compromissione del database, le password originali non sono recuperabili.

**Integrity checks (anti-tampering)** — Si calcolano checksum per i file da scaricare o trasmettere. Prima di aprire o eseguire un file, si calcola il suo hash e lo si confronta con il checksum atteso: se coincidono, il file non è stato alterato o corrotto.

**Data deduplication** — Se due file hanno lo stesso hash, sono identici — senza dover confrontare i file interi. Usato ad esempio da **eMule** con MD5 per verificare che due file siano identici anche se descritti da keyword diverse.

**DHT** — Le chiavi vengono hashate per localizzare il nodo responsabile in modo efficiente e deterministico.

#### Applicazioni blockchain

**Hash Pointers** — Un hash pointer è sia un riferimento a una posizione (dove si trova il dato) sia un hash crittografico del dato in quella posizione. Permette di verificare che i dati non siano stati alterati. Bitcoin usa una **hash chain** (blockchain) per memorizzare il ledger delle transazioni: ogni blocco contiene l'hash del blocco precedente, garantendo la *tamper-freeness* — modificare un blocco invalida tutti i successivi.

![Struttura a blocchi collegati tramite hash crittografico](images/blockchain_structure.png)
*Figura 1: Concetto di Blockchain. Ogni blocco contiene un riferimento crittografico (hash) al blocco precedente, creando una catena immutabile in cui alterare un blocco invaliderebbe tutti i successivi.*

**Commitment Scheme** — Permette di "chiudere in una busta" una decisione senza terze parti fidate.

**Hash Puzzles (Proof of Work)** — Trovare $x$ tale che $H(r \| x) \in S$.

---

### Commitment Scheme

#### Motivazione: Sasso-Carta-Forbici online

Alice e Bob giocano a sasso-carta-forbici via Internet senza terze parti fidate. Il problema: chi va per primo perde, perché l'avversario può adattarsi. La soluzione è che chi va per primo *si impegna* a una scelta senza rivelarla.

Il flusso con commitment crittografico ($R_A$ = valore casuale scelto da Alice):

$$A \to B: h_A = H(R_A \| \text{paper})$$
$$B \to A: \text{scissors}$$
$$A \to B: R_A, \text{paper}$$

Bob verifica che $h_A = H(R_A \| \text{paper})$. Se sì, sa che Alice non ha barato.

- Bob non riesce a determinare la scelta di Alice perché non conosce $R_A$ (*hiding* + *pre-image resistance*)
- Alice non può cambiare idea dopo aver ricevuto "scissors": dovrebbe trovare $R'_A$ tale che $H(R_A \| \text{paper}) = H(R'_A \| \text{stone})$ → violazione della **second-preimage resistance**

La proprietà per cui il mittente non può cambiare il valore impegnato si chiama **binding**.

#### API e Implementazione

```
com   ← commit(value, nonce)     // sigilla il valore
                                 // pubblica com
match ← verify(com, nonce, value) // apre la busta
```

Implementazione con funzione hash:
- `commit(msg, nonce)` = $H(\text{msg} \| \text{nonce})$
- `verify(com, nonce, msg)` = $(H(\text{msg} \| \text{nonce}) == \text{com})$

L'uso del `nonce` (number used once) garantisce la proprietà hiding anche quando lo spazio dei messaggi è piccolo.

---

### Search Puzzle (Proof of Work)

Un search puzzle consiste in: una funzione hash crittografica $H$, un valore casuale $r$, un insieme target $S$. La soluzione è un valore $x$ tale che:

$$H(r \| x) \in S$$

Si tratta di un **partial pre-image attack**: si deve trovare parte dell'input affinché l'output appartenga a un insieme (non a un singolo valore come nella pre-image resistance). La difficoltà si modula definendo la dimensione di $S$: un $S$ più grande rende il puzzle più facile. In **Bitcoin**, $S$ è definito dal numero di zeri iniziali richiesti nell'hash SHA-256 del blocco.

La puzzle-friendliness garantisce che non esistano scorciatoie: l'unico metodo è il tentativo esaustivo.

---

### Crittografia Asimmetrica e Firme Digitali

La crittografia asimmetrica usa una coppia di chiavi: una **chiave privata** ($K^-$), nota solo al proprietario, e una **chiave pubblica** ($K^+$), derivata matematicamente da essa ma non invertibile. La proprietà fondamentale è la **reciprocità**: ciò che una chiave cifra, l'altra decifra, e viceversa.

**Cifratura (riservatezza)** — Alice cifra un messaggio con la chiave *pubblica* di Bob; solo Bob, con la sua chiave *privata*, può decifrarlo.

**Vantaggi rispetto alla crittografia simmetrica**: nessun bisogno di concordare preventivamente una chiave condivisa. Chi vuole ricevere messaggi cifrati deve solo rendere pubblica la propria chiave pubblica. Finché la chiave privata è tenuta segreta, nessun altro può decifrare.

#### Firme Digitali

> [!definition] Firma Digitale
>
> Meccanismo equivalente a una firma autografa ma molto più sicuro. Fornisce tre garanzie: **autenticazione** (il messaggio è stato creato dal mittente riconosciuto), **non ripudio** (il mittente non può negare di aver firmato — la firma può essere portata in tribunale come prova), **integrità** (il messaggio non è stato alterato durante la trasmissione).

Il flusso è l'**inverso della cifratura**: il mittente firma con la propria chiave *privata*, chiunque può verificare con la chiave *pubblica*.

**Firma naive**: Bob firma $m$ cifrando con la sua chiave privata $K^-_B$, creando $K^-_B(m)$. Invia ad Alice la coppia $(m, K^-_B(m))$. Alice verifica applicando la chiave pubblica: $K^+_B(K^-_B(m)) = m$. Se coincide, sa che solo Bob — possessore di $K^-_B$ — ha potuto firmare.

Poiché firmare asimmetricamente un messaggio lungo è computazionalmente costoso, in pratica si firma solo il **digest**:

$$\text{firma} = K^-_B(H(m))$$

Il verificatore calcola $H(m)$ e lo confronta con $K^+_B(\text{firma})$: se coincidono, l'autenticità è garantita.

Per avere simultaneamente **riservatezza + integrità**: il mittente firma con la propria chiave privata e cifra il pacchetto completo con la chiave pubblica del destinatario. Il destinatario decifra con la propria chiave privata e verifica con la chiave pubblica del mittente.

#### API Standard

```
(sk, pk) := generateKeys(keysize)    // sk = signing key, pk = public key
sig      := sign(sk, message)        // cifra con sk → firma
isValid  := verify(pk, message, sig) // decifra sig con pk, confronta con message
```

Proprietà richiesta: `verify(pk, message, sign(sk, message)) == true`.

**Sfida principale**: cosa impedisce a un avversario di imparare a firmare messaggi analizzando la chiave pubblica? Le costruzioni basate su problemi hard (fattorizzazione, logaritmo discreto) rendono questo computazionalmente impossibile.

| Algoritmo | Base matematica | Note |
|---|---|---|
| RSA | Fattorizzazione di numeri primi (one-way trapdoor function) | Standard storico |
| DSA | Logaritmo discreto | Standard NIST |
| ECDSA | Logaritmo discreto su curve ellittiche | Usato da Bitcoin |

**Bitcoin e ECDSA**: ogni transazione Bitcoin contiene in input una firma e una chiave pubblica; in output il codice (script) per la procedura di verifica.

#### Certification Authorities

La debolezza degli schemi asimmetrici è la **weak authentication**: verificare la firma garantisce solo che chi ha firmato possiede la chiave privata corrispondente — non che sia davvero chi afferma di essere.

> [!example] Pizza Prank
>
> Alice crea un ordine di pizze a nome di Bob, lo firma con la *propria* chiave privata, e invia alla pizzeria la propria chiave pubblica spacciandola per quella di Bob. La pizzeria verifica la firma (correttamente), consegna le pizze a Bob. La weak authentication non basta.

Le **Certification Authority (CA)** risolvono il problema: emettono certificati digitali che legano crittograficamente un'identità alla sua chiave pubblica, firmando essi stessi il certificato con la propria chiave privata (di cui tutti si fidano).

---

### Hash vs Cifratura

> [!note] Differenza concettuale
>
> La **cifratura** è bidirezionale: con la chiave giusta si cifra e si decifra. L'**hashing** è irreversibile per definizione: non esiste un'operazione di "de-hashing". Sono strumenti complementari, non intercambiabili.

---

### RIPEMD-160 e Bitcoin

Bitcoin usa **due** funzioni hash: SHA-256 per il Proof of Work e **RIPEMD-160** (160 bit, output) per la derivazione degli indirizzi wallet. Il doppio hash `RIPEMD160(SHA256(pubkey))` produce l'indirizzo Bitcoin a partire dalla chiave pubblica.

---

## Strutture Dati per DHT e Blockchain

### Hash Pointer

> [!definition] Hash Pointer
>
> Un puntatore tradizionale indica *dove* si trova un dato. Un hash pointer indica *dove* si trova il dato **e** ne contiene l'hash crittografico, permettendo di verificare che non sia stato alterato. È un puntatore *tamper-evident*.

L'idea è costruire strutture dati concatenando componenti tramite hash pointer invece di puntatori normali. Per calcolare l'hash pointer a un blocco, si fa l'hash dell'intero blocco **incluso** il suo hash pointer al blocco precedente.

L'esempio più noto è la **blockchain**: ogni blocco contiene l'hash pointer al blocco precedente. Modificare il blocco $k$ invalida il suo hash, quindi non coincide con il puntatore nel blocco $k+1$. In una blockchain **Proof of Work**, ogni blocco contiene anche la prova che il PoW è stato eseguito con successo: modificare i dati richiede di rieseguire il PoW per tutti i blocchi successivi — computazionalmente impossibile.

Gli hash pointer funzionano su qualsiasi struttura senza cicli: liste, alberi, DAG. Applicazioni:
- **Bitcoin/Ethereum**: catena di blocchi con SHA-256 e RIPEMD-160 (doppio hash)
- **IPFS**: Merkle DAG
- **eMule** (*Advanced Intelligent Corruption Handling*): prima applicazione storica; verifica che i blocchi di un file scaricato dalla rete non siano stati manomessi, sfruttando i Merkle Tree

---

### Filtri di Bloom

#### Il Problema

Dato un insieme $S = \{s_1, s_2, \ldots, s_n\}$ con $n$ molto grande, vogliamo rispondere alla domanda "l'elemento $k$ appartiene a $S$?" usando poca memoria. Memorizzare tutti gli elementi esplicitamente è proibitivo. La soluzione è un'approssimazione: si accetta un trade-off tra spazio occupato e probabilità di falsi positivi.

> [!definition] Filtro di Bloom
>
> Struttura dati probabilistica per membership query. Può rispondere:
> - "$k$ **non** appartiene a $S$" → **garantito** (nessun falso negativo)
> - "$k$ **forse** appartiene a $S$" → con una certa probabilità di falso positivo

#### Costruzione

Un filtro di Bloom è un vettore $B[1 \ldots m]$ di $m$ bit (inizialmente tutti a 0) e $k$ funzioni di hash $h_1, \ldots, h_k$, indipendenti e uniformemente distribuite, ciascuna mappante in $[1, m]$. Non è necessario che siano crittografiche: bastano funzioni veloci. Esempio: $h_i(x) = MD5(x \| i)$.

**Inserimento** di un elemento $x \in S$: si calcolano $h_1(x), \ldots, h_k(x)$ e si impostano a 1 i bit corrispondenti. Un bit può essere target di più di un elemento.

**Lookup** di un elemento $y$: si calcolano $h_1(y), \ldots, h_k(y)$.
- Se **tutti** i bit corrispondenti sono 1 → $y$ è *probabilmente* in $S$
- Se **anche uno solo** è 0 → $y$ è *certamente* assente

I falsi positivi accadono quando tutti i bit di un elemento estraneo sono già stati impostati a 1 da altri elementi.

#### Probabilità di Falso Positivo

L'analisi si può modellare col paradigma **balls and bins**: inserire $n$ elementi con $k$ funzioni equivale a lanciare $kn$ palline in $m$ secchi.

Con $n$ elementi inseriti, la probabilità che un bit specifico sia ancora a 0 è:

$$p' = \left(1 - \frac{1}{m}\right)^{kn} \approx e^{-kn/m}$$

La probabilità di un falso positivo (tutti i $k$ bit a 1 per un elemento assente) è:

$$P_{fp} = \left(1 - e^{-kn/m}\right)^k$$

Questa dipende da due parametri:
- **$m/n$** (bit per elemento): per $k$ fisso, al crescere di $m$ la $P_{fp}$ **decresce esponenzialmente**
- **$k$** (numero di funzioni di hash): fissato $m/n$, la $P_{fp}$ prima decresce poi **risale** all'aumentare di $k$. Con pochi bit per elemento (es. $m/n = 2$) troppe funzioni riempiono il filtro di 1 e peggiorano il risultato; con $m/n = 10$ aumentare $k$ diminuisce sempre la $P_{fp}$

> [!example] Regola pratica
>
> Il filtro diventa efficace quando $m = c \cdot n$ con $c$ costante. Con $m = 8n$ (8 bit per elemento) e $k \approx 5\text{–}6$ funzioni, la probabilità di falso positivo è circa $2\%$ — buon compromesso con un numero limitato di bit.

#### Operazioni sugli Insiemi

| Operazione | Metodo | Note |
|---|---|---|
| Unione $S_1 \cup S_2$ | OR bit a bit di $B_1$ e $B_2$ | Esatto (stessi $m$ e $k$) |
| Intersezione $S_1 \cap S_2$ | AND bit a bit di $B_1$ e $B_2$ | Approssimato — un bit a 1 in entrambi può venire da elementi diversi non nell'intersezione |
| Cancellazione | Non supportata | Azzerare un bit rimuoverebbe anche altri elementi che lo condividono |

Per supportare la cancellazione si usano i **Counting Bloom Filter**: ogni entry è un contatore invece di un bit. L'inserimento incrementa, la cancellazione decrementa.

#### Applicazioni Reali

| Sistema | Uso |
|---|---|
| **Bitcoin (SPV client)** | I client mobili costruiscono un filtro con gli indirizzi di interesse e lo inviano a un nodo completo (bandwidth saving + privacy). Il nodo filtra le transazioni rilevanti senza trasmettere l'intera blockchain |
| **Ethereum** | I *log bloom* negli header dei blocchi riassumono gli eventi degli smart contract. Esempio: trovare tutti i token venduti da un utente in un blocco di 500 transazioni — si interroga il log bloom per la presenza dell'utente e si analizza il blocco solo in caso di match, evitando il parsing sequenziale |
| **Google Chrome** | Filtro locale per verificare se un URL è in un database di siti malevoli, prima di fare una query remota al server |
| **Google BigTable** | Evita costosi disk lookup cercando prima nel filtro, aumentando le performance delle query al database |

---

### Merkle Tree

#### Il Problema dell'Authenticated File Storage

Alice salva un file $F$ (contenuto $D$) su un server remoto e cancella la copia locale. Quando lo recupera, come verifica che il server non abbia restituito un file alterato $D' \neq D$?

- **Soluzione 1** (banale): non cancellare $D$ — inutile se manca la memoria
- **Soluzione 2** (hash singolo): Alice conserva $H(D)$; verifica confrontando $H(D') = H(D)$. Funziona per il file intero, ma se Alice vuole solo un frammento deve scaricare tutto e ricalcolare l'hash
- **Soluzione 3** (Merkle Tree): aggiungere struttura al commitment — non un singolo hash ma una gerarchia di hash

> [!definition] Merkle Tree
>
> Struttura dati introdotta da **Ralph Merkle nel 1979** per sintetizzare grandi quantità di dati con verifica efficiente. È un albero binario completo di hash costruito da un insieme iniziale $\{x_1, \ldots, x_n\}$ (con $n$ potenza di 2):
> - Le **foglie** contengono l'hash di ciascun dato: $y_i = H(x_i)$
> - I **nodi interni** contengono l'hash della concatenazione dei figli: $H(\text{figlio\_sx} \| \text{figlio\_dx})$
> - La **radice** (**Merkle Root Hash**) riassume crittograficamente l'intero dataset

#### Costruzione

Con $n$ dati $x_1, x_2, \ldots, x_n$ e funzione hash $H$:
- Ogni nodo interno memorizza $H(x \| y) = H(\text{concatenazione dei figli})$
- Il commitment finale è il Merkle Root $y_{2n-1}$
- **Costo di costruzione**: $O(n)$ spazio e $O(n)$ hash
  
![Albero di Merkle: struttura ad albero binario basata su hash crittografici](images/Pasted-image-20260407112004.png)
*Figura 2: Albero di Merkle. I dati originali si trovano nelle foglie ($x_1 \ldots x_8$). Ogni nodo intermedio è calcolato come l'hash della concatenazione dei suoi nodi figli, fino alla Root ($y_{15}$).*

#### Merkle Proof (Proof of Inclusion)

Protocollo file storage:
1. Alice invia $D$ al server; il server memorizza $(F, D)$
2. Alice calcola il **Merkle Tree Root** (MTR) da $D$, conserva MTR ($O(1)$ — 256 bit), cancella $D$
3. Più tardi: Alice chiede al server il chunk $x_i$
4. Il server (Prover) restituisce $x_i$ + **prova di inclusione** $p$ (gli hash dei fratelli lungo il percorso foglia→radice)
5. Alice (Verifier) verifica $p$ rispetto al MTR conservato

> [!example] Merkle Proof Concreta
>
> Per dimostrare che $D = x_4$ appartiene all'albero, si esibiscono i fratelli lungo il percorso: $y_3$, $y_9$, $y_{14}$.
>
> La verifica ricalcola:
> - $z_4 = H(D)$
> - $z_{10} = H(y_3 \| z_4)$
> - $z_{13} = H(y_9 \| z_{10})$
> - $z_{15} = H(z_{13} \| y_{14})$
>
> Si controlla che $z_{15} = y_{15}$ (la radice fidata). Se sì, il chunk è autentico.

| Proprietà | Valore |
|---|---|
| Costo costruzione | $O(n)$ spazio e hash |
| Spazio commitment | $O(1)$ — solo il Merkle Root (256 bit) |
| Dimensione prova | $O(\log n)$ hash |
| Costo di verifica | $O(\log n)$ operazioni |
| Falsi negativi | Impossibili — se $x_i \in \{x_1,\ldots,x_n\}$ la prova è sempre costruibile |
| Falsi positivi | Impossibili — una prova falsa richiederebbe trovare una collisione hash |

#### Proof of Non-Membership

Per dimostrare che $\text{Data} \notin \{x_1, \ldots, x_n\}$: si ordinano le foglie e si trovano $x_i < \text{Data} < x_{i+1}$; si dimostrano le inclusioni di $x_i$ e $x_{i+1}$.

#### Applicazioni

- **Bitcoin**: memorizza le transazioni in ogni blocco
- **Ethereum**: usa Merkle-Patricia Tries per stato e transazioni
- **IPFS**: Merkle DAG
- **Apache Cassandra**: verifica dell'integrità dei dati replicati

---

### Trie, Patricia Trie e Merkle Patricia Trie

#### Trie (Prefix Tree / Radix Tree)

Il nome *trie* viene da "retrieval". È una struttura ad albero per stringhe in cui ogni arco è etichettato con un carattere (o lettera dell'alfabeto); un percorso dalla radice a un nodo *marcato* forma una stringa valida. Con l'alfabeto inglese ogni nodo può avere fino a 26 figli.

**Ricerca**: si scende dall'alto seguendo i caratteri della stringa; se si trova il percorso e il nodo finale è marcato → successo; se si è bloccati o il nodo finale è non marcato → fallimento.

**Problema**: la maggior parte dei nodi ha un solo figlio, creando lunghe catene inutili (es. "Ann", "Anna", "Annab", "Annabe", "Annabel" formano un percorso senza biforcazioni). Lo spazio richiesto è elevato.

#### Patricia Trie

**PATRICIA** = *Practical Algorithm To Retrieve Information Coded In Alphanumeric* (1960). È una versione compressa del trie: le catene di nodi a figlio unico vengono **compresse in un singolo arco** con etichetta multipla (la concatenazione delle etichette dei nodi compressi). Il risultato è un albero in cui ogni nodo interno ha **almeno due figli**.

Il Patricia Trie funziona anche come **dizionario di coppie (chiave, valore)**: le chiavi sono le stringhe rappresentate nell'albero, i valori sono memorizzati nei nodi terminali. Usato in Ethereum per lo stato dei contratti.

#### Nibble

In Ethereum le chiavi sono stringhe esadecimali suddivise in **nibble** (mezzo byte = 4 bit = 1 carattere esadecimale). Questo permette una condivisione più **granulare** dei prefissi: 16 possibili direzioni per ogni nodo interno (anziché 256 per i byte interi).

#### Merkle Patricia Trie (Ethereum)

> [!definition] Merkle Patricia Trie
>
> Struttura ibrida introdotta nel **Yellow Paper di Ethereum** e ora usata nella maggior parte delle blockchain EVM-based. Combina:
> - La **compressione dei prefissi** del Patricia Trie → ricerca veloce e deterministica
> - La **garanzia crittografica** dei Merkle Tree → integrità e tamper-proof validation
>
> Usata da Ethereum per memorizzare lo stato degli account/contratti e le transazioni.

Le coppie (chiave, valore) in Ethereum possono essere:
- `(indirizzo account → saldo)`
- `(identificatore transazione → importo trasferito)`

I nodi del Merkle Patricia Trie sono di tre tipi:

| Tipo | Contenuto | Ruolo |
|---|---|---|
| **Leaf node** | Nibble finali della chiave + valore | Nodo terminale; memorizza il valore |
| **Extension node** (shared node) | Nibble condivisi (prefisso comune) + hash pointer al branch node | Compressione del prefisso comune |
| **Branch node** | Array di 16 elementi (uno per nibble 0–F) + eventuale valore | Punto di biforcazione tra prefissi |

> [!example] Costruzione MPT
>
> Inserzione di 'do' → creazione di un nodo foglia.
> Inserzione di 'puppy' → il prefisso comune (in esadecimale '646f') genera uno shared node + branch node; la nuova foglia viene collegata tramite un **hash pointer** (l'hash del nodo foglia stesso) → questa è la componente *Merkle* dell'albero. Il nibble '6' è condiviso tra tutti i prefissi → viene creato un nodo dedicato al livello di nibble.

Un singolo hash pointer alla radice del MPT garantisce l'integrità crittografica dell'intero stato di Ethereum: qualunque modifica cambia la radice.

---

### Riepilogo

| Struttura | Problema risolto | Complessità | Garanzie |
|---|---|---|---|
| **Hash Pointer** | Tamper-evidence su strutture concatenate | $O(1)$ per verifica | Qualunque manomissione è rilevabile |
| **Filtro di Bloom** | Membership query su insiemi enormi | $O(k)$ insert/lookup | No falsi negativi; falsi positivi controllabili con $m/n$ e $k$ |
| **Merkle Tree** | Autenticazione di frammenti di dati | $O(n)$ costruzione, $O(\log n)$ prova/verifica | Nessun falso positivo né negativo |
| **Merkle Patricia Trie** | Stato globale distribuito e verificabile | $O(\log n)$ lookup | Integrità crittografica + ricerca efficiente per prefisso |
