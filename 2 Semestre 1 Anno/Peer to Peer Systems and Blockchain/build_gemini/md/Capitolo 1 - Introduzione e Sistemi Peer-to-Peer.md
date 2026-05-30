# Capitolo 1 - Introduzione e Sistemi Peer-to-Peer

## Il Paradigma Peer-to-Peer

Nel modello **Client-Server** classico i server sono macchine dedicate con IP fisso che erogano servizi; i client li consumano senza comunicare tra loro. Il server è un potenziale collo di bottiglia.

> [!definition] Rete Peer-to-Peer (P2P)
>
> Insieme di entità autonome (**peer**) che si auto-organizzano e condividono risorse distribuite (calcolo, memoria, banda). Il sistema è in grado di adattarsi a un continuo **churn** dei nodi mantenendo connettività e prestazioni ragionevoli senza un'entità centrale. Ogni nodo è contemporaneamente fornitore e consumatore di servizi (funzionalità simmetrica: **servent**).

I server possono esistere per il bootstrap iniziale, ma non sono necessari per lo scambio effettivo delle risorse. Una sfida caratteristica delle reti P2P è il **churn**: i nodi entrano ed escono continuamente, ottenendo spesso un nuovo indirizzo IP ad ogni connessione. Questo rende inutilizzabile l'indirizzamento tramite IP statici e richiede meccanismi applicativi — non a livello IP — per localizzare le risorse.

![A sinistra una rete centralizzata con un singolo server (Single Point of Failure), a destra un'architettura Peer-to-Peer totalmente distribuita e interconnessa.](images/p2p_vs_centralized.png)

Ogni peer che partecipa a una rete P2P deve affrontare quattro problemi fondamentali: come **unirsi** alla rete (*join*), come **scoprire altri peer** (*peer discovery*), come comportarsi sia da fornitore che da consumatore di servizi, e come **prevenire il free riding** — ovvero impedire che alcuni nodi consumino risorse senza contribuire — incentivando la partecipazione e la reciprocità.

### Condivisione di Risorse

Le risorse condivise in una rete P2P si trovano "ai bordi" di Internet: sono direttamente messe a disposizione dai peer, senza nodi speciali per la loro gestione. Possono essere: **ledger** distribuiti, spazio di archiviazione in lettura/scrittura, potenza di calcolo, banda.

La partecipazione può avvenire per motivi molto diversi. Un peer può offrire risorse gratuitamente per contribuire a un progetto collettivo (es. ricerca di vita extraterrestre con SETI, ricerca su terapie contro il cancro). Oppure può essere **ricompensato** per il contributo alla gestione della rete, come avviene per i **Bitcoin miners**. In ogni caso, la proprietà più interessante è quella di **auto-scalabilità**: la partecipazione di un numero crescente di utenti aumenta naturalmente le risorse del sistema e la sua capacità di servire più richieste.

---

## Blockchain: Cos'è e Quando Usarla (Panoramica)

> [!definition] Blockchain
>
> Database condiviso, replicato e consistente, mantenuto senza un'autorità centrale. È **append-only** (solo aggiunta), immutabile e resistente alle manomissioni. In termini di teoria dei giochi: una macchina a stati decentralizzata mantenuta da attori non fidati, incentivati economicamente a comportarsi correttamente. Non può essere spenta o censurata, e i dati non possono essere eliminati.

Le tecnologie fondamentali sono:
- **Firme digitali** — autenticazione
- **Hash crittografici** — immutabilità e integrità
- **Replicazione** — disponibilità tramite copie distribuite
- **Consenso distribuito** — coordinamento tra repliche mutuamente diffidenti

> [!tip] Quando usare la blockchain
>
> Ha senso considerare la blockchain quando: è necessario memorizzare uno stato condiviso in modalità append-only, ci sono più scrittori con diversi gradi di fiducia reciproca, l'applicazione deve girare in modo distribuito, il processo di settlement è complesso e richiede una terza parte fidata, servono integrità/autenticazione/non-ripudio, le regole sono precise e semplici da codificare, e la trasparenza è preferibile alla privacy.

> [!warning] La blockchain non è sempre la soluzione giusta
>
> Ha senso usarla solo se i partecipanti non sono noti o fidati. Se tutte le parti sono fidate, un database tradizionale è preferibile. Se serve solo immutabilità con parti fidate, bastano database con checksum crittografici (es. AWS QLDB, Kafka). Molti usi proposti della blockchain in ambito aziendale rientrano in questa categoria e non ne hanno effettivamente bisogno.

### Bitcoin ed Ethereum

**Bitcoin** nasce nel 2008 dal paper di Satoshi Nakamoto come sistema di cassa elettronica P2P: pagamenti online diretti senza intermediari, con il problema del **double-spending** risolto tramite una catena di blocchi con timestamping basato su hash. Il *Genesis Block* conteneva il messaggio *"Chancellor on brink of second bailout for banks"* — un riferimento esplicito alla crisi finanziaria e all'obiettivo di sottrarre il controllo del denaro alle banche centrali. La *cypherpunk vision* alla base di Bitcoin è che si possa rivoluzionare il mondo costruendo protocolli sicuri.

**Ethereum** espande il concetto: non è solo valuta, ma una piattaforma programmabile. Introduce gli **smart contract**, programmi eseguiti dalla blockchain stessa tramite linguaggi Turing-completi come Solidity. L'intera rete si comporta come un singolo computer globale replicato e consistente (**EVM**, Ethereum Virtual Machine). A differenza di Bitcoin, in cui gli script hanno potere computazionale limitato, Ethereum può risolvere qualunque problema computazionale — con il meccanismo del **gas** per prevenire attacchi denial-of-service.

> [!example] Smart contract assicurativo
>
> Un contratto connesso a un database di voli rimborsa automaticamente il passeggero se il ritardo supera una soglia prestabilita — senza pratiche burocratiche, senza intermediari. Il rimborso in criptovaluta viene trasferito automaticamente al wallet di Bob non appena il ritardo viene verificato.

### Le Sfide: Trilemma della Blockchain

> [!warning] Trilemma della Blockchain
>
> È difficile ottenere contemporaneamente **sicurezza**, **decentralizzazione** e **scalabilità**. Migliorare una delle tre proprietà tende a penalizzare le altre. È una delle grandi sfide scientifiche aperte del settore.

**Privacy:**
Le transazioni su ledger pubblici sono visibili a tutti. Le identità degli utenti possono a volte essere inferite, con rischio di esposizione di dati sensibili. Bilanciare privacy e auditabilità è particolarmente delicato nei protocolli **DeFi**: da un lato richiedono confidenzialità (transazioni, depositi, prestiti senza rivelare importi o indirizzi), dall'altro richiedono auditabilità (verifica del double-spending, conferma della collateralizzazione). Le soluzioni principali sono:

- **Zero Knowledge Proofs (ZKP)**: un *prover* dimostra la validità di un'affermazione a un *verifier* senza rivelare i dati sottostanti. Applicazioni: nascondere dati sensibili mantenendo la correttezza, esecuzione privata di smart contract, verifica d'identità privata on-chain, DeFi privacy-preserving.
- **Fully Homomorphic Encryption (FHE)**: eseguire calcoli su dati cifrati senza decifrarli — il risultato, una volta decifrato, coincide con quello ottenuto dal testo in chiaro. L'idea chiave è: *"posso calcolare sui tuoi dati segreti senza mai vederli"*. Esempio: un protocollo di prestito calcola l'idoneità al credito o il tasso di interesse su saldi cifrati — i saldi restano privati ma il sistema produce risultati corretti.
- **Multiparty Computation (MPC)**: calcolo distribuito tra più parti che collaborano senza rivelare i propri input privati alle altre.

**Scalabilità:**
Le blockchain tradizionali hanno throughput limitato e costi energetici elevati. Le soluzioni principali spostano l'esecuzione **off-chain**, usando la catena principale solo come ancora di fiducia (*trust anchor*) per la validazione finale:

- **Layer-2** (Optimistic Rollups, ZK-rollups): raggruppano molte transazioni off-chain e ne pubblicano solo la prova sulla catena principale.
- **Payment Channel** (Lightning Network): canali di pagamento bidirezionali che consentono scambi diretti tra peer senza toccare la blockchain per ogni transazione.

### Applicazioni

| Applicazione | Descrizione |
|---|---|
| **Criptovalute e Token** | Alternativa alle valute fiat: la blockchain non richiede che un governo emetta moneta né che le banche validino le transazioni. L'offerta è legata a un bene virtuale limitato crittograficamente. La blockchain risolve il double spending e supporta sia token **fungibili** (interscambiabili) che **non fungibili** |
| **NFT** | Prova di proprietà di asset digitali unici (arte, diritti d'autore). Un'opera in .jpeg è facilmente copiabile, ma l'NFT certifica chi è il proprietario originale |
| **DeFi** | Piattaforme come **Uniswap** per il trading diretto tra pari (DEX) con pool di liquidità e market maker automatizzati (AMM). In Uniswap V3, le posizioni di liquidità sono rappresentate come **LP NFTs**: ogni posizione ha parametri distinti e personalizzabili che ne determinano valore e rendimento |
| **Self Sovereign Identity** | L'utente controlla i propri dati e rivela solo le informazioni minime necessarie (minimalismo, portabilità, consenso) |
| **Supply Chain** | Tracciamento provenienza e qualità: es. Walmart-IBM (Hyperledger) per sicurezza alimentare, con sensori IoT che registrano temperatura e posizione. Un altro esempio: ristoranti possono verificare la catena di custodia del pesce, con sensori attaccati al prodotto che registrano posizione, temperatura e umidità lungo tutta la filiera |
| **Intellectual Property** | Il proprietario di un contenuto digitale fa l'hash del contenuto insieme alla propria identità e lo registra sulla blockchain. Se nessun altro può dimostrare di averlo pubblicato prima di quel commit, questo costituisce prova di proprietà — più comodo di un ufficio brevetti e senza dover divulgare i dettagli del contenuto |

---

# Reti Overlay e File Sharing

Il file sharing è stata la prima *killer application* del P2P. Il funzionamento tipico è il seguente: un utente U ha un client P2P sul proprio computer; ad ogni connessione ottiene un nuovo indirizzo IP. U memorizza i file condivisi in una directory, associando a ciascuno dei metadati identificativi (titolo, autore, data di pubblicazione). Quando U vuole trovare un file, invia una query al sistema, riceve la lista dei peer che lo posseggono, sceglie il peer P secondo certi criteri, e avvia il trasferimento diretto. Nel frattempo, altri utenti possono già scaricare da U le parti del file che U ha già ottenuto.

## Dal Centralizzato al P2P

**Napster (2001)** (prima generazione) usava un indice centralizzato dei file su server dedicati, mentre il trasferimento avveniva direttamente tra peer. Ha dimostrato che si può servire una quantità di dati paragonabile a Google con molti meno server, spostando storage e trasferimento direttamente sugli utenti. All'epoca Google impiegava circa 15.000 server, Napster circa 100. Il sistema raggiunge 26,4 milioni di utenti nel 2001, con 10 TB di dati (2 milioni di canzoni, in media 220 per utente). I server si occupano solo di localizzare chi possiede la risorsa — la parte meno costosa del servizio. In questo modello ogni utente è un **servent** (server + client): partecipa "pagando" con le proprie risorse fisiche, contenuti o conoscenza.

- **Punti di forza di Napster**: sistema informativo globale senza grandi investimenti, decentralizzazione dei costi e dell'amministrazione, nessun collo di bottiglia sulle risorse (storage e trasferimento distribuiti tra gli utenti). 
- **Punti di debolezza**: il server resta un singolo punto di fallimento e di controllo, necessario per gestire l'intero sistema — esattamente questo lo ha reso vulnerabile agli attacchi legali per violazione del copyright, poiché l'analisi dell'indice centralizzato permetteva di risalire ai contenuti scambiati tra gli utenti.

La seconda generazione (**Gnutella, Kazaa, BitTorrent**) ha eliminato ogni punto centrale, distribuendo sia la ricerca che il trasferimento.
**Gnutella** rimuove anche l'ultimo punto centrale: nessun indice, connessioni dirette tra peer usate per la ricerca (non per il download). Il risultato è un sistema senza infrastruttura né amministrazione, privo di single point of failure. I punti deboli diventano: alto traffico di rete, assenza di ricerca strutturata, e **free riding** (nodi che consumano risorse senza contribuire).

## Reti Overlay

> [!definition] Overlay Network
>
> Rete logica costruita sopra la rete fisica sottostante (underlay), tipicamente a livello applicativo sopra TCP/IP. I link dell'overlay sono "tunnel" che attraversano la rete fisica: un singolo collegamento logico può passare per decine di router. Più overlay possono coesistere contemporaneamente sulla stessa rete fisica, ciascuno offrendo il proprio servizio specifico non disponibile nell'underlay. I nodi dell'overlay sono spesso end host che fungono anche da nodi intermedi che inoltrano traffico.

![Rappresentazione dei due livelli di rete. L'Overlay logico (in alto) è costruito creando connessioni virtuali tra i peer, che fisicamente si traducono in percorsi complessi attraverso l'Underlay IP (in basso).](images/Pasted-image-20260407110328.png)

Un protocollo P2P definisce formato e semantica dei messaggi tra peer. I peer sono identificati da ID univoci, generalmente calcolati tramite funzioni hash. I pacchetti P2P, analogamente ai pacchetti IP, sono caratterizzati da un **header** e un **payload**. Il protocollo definisce anche una strategia di routing a livello applicativo dello stack TCP/IP, senza dover modificare i router sottostanti.

### Classificazione degli Overlay

| Tipo | Topologia | Lookup | Garanzie |
|---|---|---|---|
| **Centralizzato** | Server centrale | $O(1)$ | Singolo punto di fallimento |
| **Non Strutturato** | Grafo casuale | $O(N)$ | Nessuna garanzia di trovare la risorsa |
| **SuperPeer (Ibrido)** | Gerarchico | $O(hops_{max})$ | Migliore scalabilità del non strutturato |
| **Strutturato (DHT)** | Topologia controllata | $O(\log N)$ | Lookup garantito, garanzie anche su join e leave |

---

## Overlay Non Strutturati

I peer si connettono arbitrariamente: la topologia forma un grafo casuale (es. Gnutella ≤ 0.4, Bitcoin). La rete è resiliente e facile da mantenere, ma la ricerca è costosa — nel caso peggiore $O(N)$. I falsi negativi sono possibili: la risorsa cercata potrebbe esistere ma non essere raggiunta entro il TTL.

### Bootstrapping e Discovery

Un nuovo nodo non conosce nessuno. Il **bootstrapping** avviene tramite due meccanismi complementari: server DNS noti che memorizzano gli indirizzi IP di un insieme di peer stabili (eseguendo script che interagiscono con i peer e aggiornano automaticamente la lista), oppure una **cache interna** in cui ogni client memorizza gli IP dei peer contattati nelle sessioni correnti e precedenti, aggiornata dinamicamente tramite *gossiping* con i vicini.

![Processo di Bootstrap. Il peer in ingresso (azzurro) contatta un repository per ottenere la lista dei descrittori, dopodiché stabilisce le connessioni (link virtuali) con gli altri peer disponibili.](images/Pasted-image-20260407110433.png)

Il processo di partecipazione alla rete si articola in tre fasi:

- **Step 0** — join: il nodo si connette a uno o più peer noti tramite bootstrap.
- **Step 1** — peer discovery: il nodo invia messaggi **Ping** per annunciare la propria presenza; i peer rispondono con **Pong** contenenti le proprie informazioni e inoltrano il Ping ai vicini.
- **Step 2** — searching: il nodo invia una query ai vicini (es. *"do you have any content that matches the string 'Back to Black'?"*); i peer che hanno corrispondenze rispondono, gli altri inoltrano la query per TTL salti.
- **Step 3** — downloading: il trasferimento avviene via connessioni HTTP dirette usando il metodo GET.

### Flooding

L'algoritmo di ricerca base è il **Flooding**: la query viene inviata a tutti i vicini, che la inoltrano a loro volta. Per evitare loop infiniti si usa un **TTL** decrementato ad ogni salto; quando raggiunge zero il messaggio viene scartato. I duplicati si evitano con un ID univoco per ogni messaggio. Le risposte viaggiano all'indietro attraverso le connessioni non transitorie, tramite **Backward Routing**.

```
FloodForward(Query q, Source p):
  if q.id ∈ oldIdsQ: return          // duplicato, scarta
  oldIdsQ ← oldIdsQ ∪ {q.id}
  q.TTL ← q.TTL - 1
  if q.TTL == 0: return              // scaduto, scarta
  foreach s ∈ Neighbors:
    if s ≠ p: send(s, q)             // inoltra a tutti tranne il mittente
```

Il flooding equivale a una **BFS limitata dal TTL**: trova il massimo numero di risultati nel raggio TTL centrato sul nodo sorgente. Garantisce alta resilienza ma genera molto traffico e molti duplicati, scala male, e **non garantisce il ritrovamento della risorsa** (false negative). È usato anche in **Bitcoin** non solo per la ricerca, ma per **propagare le transazioni** nella rete P2P sottostante — dove mantenere la consistenza è la sfida principale.

### Tecniche di Ricerca Avanzate

Le alternative al flooding puro si dividono in due categorie: approcci **BFS-based** (iterative deepening/expanding ring, k-walker random walk, two-level k-walker, directed BFS, modified random BFS) e approcci **DFS-based** (local indices, routing indices, attenuated bloom filter).

**Expanding Ring (Iterative Deepening)** — BFS con TTL crescente. Si parte da un TTL basso (opzionalmente su un sottoinsieme casuale dei vicini); se la ricerca fallisce si ripete incrementandolo fino alla terminazione (risorsa trovata o profondità massima raggiunta). Per non riprocessare gli stessi nodi, quelli al bordo dell'anello *i-esimo* **congelano** la query per un periodo $> W$ (intervallo tra due query successive). Quando la sorgente invia un messaggio `resend` con lo stesso ID e un `NewTTL` maggiore, i nodi interni all'anello precedente lo inoltrano semplicemente; i nodi al bordo lo **scongelano** e inviano la query ai propri vicini con $TTL = NewTTL - PreviousTTL$.

**Random Walk e k-Walker** — Il random walk è modellato come una **catena di Markov** (*drunkard's walk*): il sistema è privo di memoria, la distribuzione di probabilità dello stato futuro dipende solo dallo stato presente, senza direzioni privilegiate. In pratica, il nodo invia la query a *un solo* vicino scelto a caso, che fa lo stesso; il TTL si decrementa ad ogni salto. Se la ricerca fallisce (timeout), la sorgente può riemettere la query lungo un altro cammino casuale. Riduce drasticamente il traffico ma aumenta la latenza.

La variante **k-walker** parallelizza inviando $k$ copie indipendenti, ciascuna che prende il proprio cammino casuale. La terminazione può avvenire per TTL oppure con un **checking method**: i walker periodicamente verificano con la sorgente se la condizione di stop è stata soddisfatta. Si può anche **bilanciare verso nodi ad alto grado** modulando la probabilità di scelta del vicino. Vantaggi e svantaggi: il limite superiore al traffico è $k \times TTL$ messaggi; $k$ walker dopo $T$ passi raggiungono circa lo stesso numero di nodi di 1 walker dopo $k \times T$ passi, riducendo il ritardo di un fattore $k$. Le prestazioni dipendono da $k$, $T$ e dalla popolarità $p$ della risorsa: $k$ e $T$ bassi producono alto ritardo e bassa probabilità di successo; $k$ e $T$ alti producono alto overhead. Una soluzione è impostare i parametri adattativamente in funzione della popolarità.

**Directed BFS e Routing Indices** — I vicini vengono scelti non a caso ma selezionando i "migliori". Un vicino è considerato buono se: ha prodotto risultati in passato, ha bassa latenza, ha il minor numero di hop per i risultati (segno che ha buoni vicini), ed è stabile. Dopo il primo hop, la ricerca può proseguire come un normale BFS.

I **Routing Indices (RI)** formalizzano questa selezione: ogni peer mantiene una struttura dati che, data una query, restituisce la lista dei vicini ordinata per "bontà". Ogni peer ha un indice locale per i propri documenti e un RI che stima quanti documenti sono disponibili per ciascun percorso e per ciascun argomento. Esempio: per il nodo A, tramite il vicino B e i suoi discendenti sono disponibili 100 documenti — 20 nella categoria Database, 10 in Theory, 30 in Languages. Questo permette di inviare la query solo ai vicini più rilevanti per quella specifica ricerca.

---

## Overlay Ibridi (SuperPeer)

> [!definition] SuperPeer
>
> Nodo con maggiore capacità (banda, CPU, disponibilità) che funge da hub locale. I peer normali si connettono ai SuperPeer e depositano l'indice delle proprie risorse. Il flooding per la ricerca avviene solo tra SuperPeer; il trasferimento dei file resta diretto tra peer.

I SuperPeer vengono scelti autonomamente dal sistema in base alle capacità (storage, banda) e alla disponibilità (tempo di connessione), definendo dinamicamente un livello gerarchico nella rete. Periodicamente si scambiano informazioni sulle risorse dei peer collegati e si fanno carico del carico dei nodi più lenti. I peer ordinari caricano la descrizione delle proprie risorse sul SuperPeer, lo interrogano per le query, e partecipano direttamente al trasferimento delle risorse.

Il vantaggio è che il traffico di ricerca è contenuto alla rete dei SuperPeer, migliorando la scalabilità rispetto al non strutturato puro — a scapito di una minore resistenza al churn dei SuperPeer stessi.

> [!note] Differenza tra implementazioni
>
> In **Gnutella v0.6** gli *ultrapeers* sono **auto-promossi** dai nodi stessi in base alle proprie capacità. In **Kazaa**, **Skype** (per il relay) e **eDonkey** (pre-Kad) gli ultrapeers sono invece **staticamente definiti**.

---

## Auto-Organizzazione dei Sistemi P2P

Le reti non strutturate mostrano proprietà emergenti simili a fenomeni fisici e biologici: dall'interazione locale dei peer emerge spontaneamente una struttura globale, senza alcun coordinamento centrale. In Gnutella emerge spontaneamente un **backbone** — una rete di nodi con alto grado di connessione (simili a server) che organizzano il traffico della rete, senza che nessuno lo abbia pianificato.

I sistemi P2P offrono vantaggi su più fronti. Per gli utenti: sfruttamento delle risorse in eccesso (cicli CPU inutilizzati, storage libero, banda disponibile) in cambio di risorse, servizi o partecipazione a reti sociali. Per la comunità: la **proprietà di auto-scalabilità** — la partecipazione di un numero maggiore di utenti aumenta naturalmente le risorse del sistema. Per chi sviluppa applicazioni: riduzione dei costi rispetto al modello client-server (server farm ad alta connettività, replicazione per fault tolerance, disponibilità 24×7 sono tutte responsabilità distribuite tra i peer).

Il successo di un'applicazione P2P dipende in larga misura dalla formazione di una **massa critica** di utenti: una soglia di partecipazione che permette all'applicazione di autosostenersi.

> [!note] Sfide scientifiche aperte
>
> Lo sviluppo di applicazioni P2P su larga scala richiede strumenti nuovi. Le metodologie classiche per i sistemi distribuiti non scalano: un sistema P2P opera su milioni di nodi (non centinaia), e il fallimento o la disconnessione di un nodo è un evento normale, non un'eccezione. Servono: **teoria dei giochi** (cooperazione tra peer, equilibrio di Nash), **nuove tecniche crittografiche**, **nuovi algoritmi di consenso**, **strumenti di analisi di sistemi complessi**.

---

# Overlay Strutturati: DHT e Recupero Distribuito

In un sistema P2P puro, il recupero dei contenuti può seguire due paradigmi opposti.
Il **searching** guida la ricerca attraverso gli attributi del contenuto, in modo analogo a un motore di ricerca (usato nelle reti non strutturate con flooding).
L'**addressing** assegna un identificatore univoco a ogni contenuto — tipicamente il suo hash crittografico — e usa quella chiave per recuperarlo. È il fondamento delle **Distributed Hash Tables (DHT)**: l'hash del contenuto diventa la chiave di accesso, e la DHT instrada la query verso il nodo responsabile di quella chiave con garanzie teoriche precise. Il compromesso è la rinuncia alle query complesse e il costo del mantenimento della struttura di indirizzamento. Questo approccio non è più *location-based* (URL che puntano a una posizione), ma *content-based* (l'identità del dato è il suo hash, come fa IPFS).

Le DHT si collocano nel punto ottimale di compromesso tra l'approccio centralizzato e l'approccio non strutturato:

| Approccio | Costo Comunicazione | Memoria Richiesta | Risultato (Falsi negativi) |
| --- | --- | --- | --- |
| **Flooding** (es. Gnutella) | O(N^2) | O(1) | Falsi negativi possibili (limite TTL) |
| **Server Centralizzato** (es. Napster) | O(1) | O(N) | Nessun falso negativo (ma Single Point of Failure) |
| **DHT** (es. Chord/Kademlia) | O(log N) | O(log N) | Nessun falso negativo (risoluzione garantita) |

Le proprietà chiave che la DHT garantisce rispetto al flooding sono: scalabilità O(log N), assenza di falsi negativi, e *self-organization* — il sistema gestisce autonomamente join e leave dei nodi, sia volontari che per guasto.

## Funzioni Hash Crittografiche

Una **funzione hash crittografica** mappa dati di lunghezza arbitraria in un valore di lunghezza fissa (*digest*), garantendo l'effetto valanga (piccola variazione = digest completamente diverso) e il determinismo. 

> [!example] Output SHA-1 in Java
>
> ```
> SHA1("")    = DA39A3EE5E6B4B0D3255BFEF95601890AFD80709
> SHA1("abc") = A9993E364706816ABA3E25717850C26C9CD0D89D
> SHA1("abd") = CB4CC28DF0FDBE0ECF9D9662E294B118092A5735
> ```

Le famiglie disponibili sono SHA-1, SHA-224, SHA-256, SHA-384 e SHA-512. Ethereum usa **Keccak**. Queste funzioni sono il mattone base sia per il consistent hashing delle DHT sia per i puzzle crittografici della Proof of Work di Bitcoin.

## Il Problema del Rehashing e il Consistent Hashing

Se si distribuiscono i dati su $N$ nodi con la funzione classica $\text{SHA}(x) \bmod N$, quando un nodo viene aggiunto o rimosso, quasi tutte le chiavi devono essere riassegnate, generando un traffico di rete insostenibile (fino al 99% delle chiavi modificate in un sistema con 10 nodi).

> [!definition] Consistent Hashing
>
> Tecnica di hashing in cui sia i contenuti che i nodi vengono mappati nello **stesso spazio di indirizzamento**, organizzato come un **anello circolare** (*ring*) di dimensione $2^M$. Ogni nodo gestisce un **intervallo contiguo** di chiavi dell'anello. Aggiungere o rimuovere nodi richiede di spostare solo una minoranza di elementi — in media $K/n$ chiavi, dove $K$ è il totale delle chiavi e $n$ il numero di nodi.

## Costruzione di una DHT: l'Anello (Es. Chord)

La costruzione di una DHT basata su consistent hashing segue tre passi concettuali: definire uno spazio di identificatori condiviso (modulo $2^M$), connettere i nodi definendo la topologia, e assegnare i dati basandosi sull'hash.

Consideriamo uno spazio di identificatori $\{0, \ldots, 15\}$ organizzato come un anello modulo 16, con cinque nodi in posizioni hashate:
$$H(a) = 6, \quad H(b) = 5, \quad H(c) = 0, \quad H(d) = 11, \quad H(e) = 2$$

![Topologia ad anello logico di Chord. I nodi sono posizionati sull'anello in base al loro hash. Le frecce indicano i puntatori di routing (finger) che permettono salti di lunghezza esponenzialmente crescente nello spazio degli identificatori.](images/mermaid-lezione-3-retrieving-content-e-dht-02.png)

Il **successore** `succ(x)` è il primo nodo sull'anello con identificatore $\geq x$, procedendo in senso orario. I dati vengono memorizzati sul nodo `succ(k)`, dove $k = H(\text{key})$. 

> [!example] Calcolo del successore e Memorizzazione
>
> - `succ(12) = 0` — non ci sono nodi tra 12 e 15, si fa wrap-around all'inizio dell'anello.
> - Se il dato "scudo" ha $H(\text{scudo}) = 12$, verrà memorizzato nel nodo 0.
> - Se il nodo 11 abbandona la rete, le chiavi che gestiva passano al suo successore (il nodo 0), minimizzando il traffico di riassegnazione.

### Node Leave e Node Failure

Una **disconnessione volontaria** prevede il trasferimento organizzato delle chiavi. Un **guasto improvviso** (*node failure*) porta a perdita di dati se non si applicano soluzioni di resilienza, quali: **replicazione dei dati** su $r$ successori, **refresh periodico** (gossip), e **probing periodico** per trovare percorsi alternativi nelle routing table.

### Finger Table e Routing $O(\log N)$

Se il routing procedesse sequenzialmente sul successore diretto, avremmo $O(N)$ hop. Per evitare ciò, protocolli come **Chord** introducono la **Finger Table**:

> [!definition] Finger Table
>
> $$\text{finger}[i] = \text{succ}(n + 2^{i-1}) \quad \text{per } i = 1, \ldots, M$$
>
> Ogni nodo mantiene puntatori a distanze esponenzialmente crescenti ($+1, +2, +4, +8...$).

L'algoritmo di lookup inoltra la query al finger con l'identificatore massimo che non supera la chiave cercata, dimezzando l'intervallo residuo ad ogni step.

![Algoritmo di routing in Chord. La richiesta viene inoltrata iterativamente al nodo conosciuto più distante che non supera la chiave k, avvicinandosi progressivamente (in modo logaritmico) alla destinazione.](images/mermaid-lezione-3-retrieving-content-e-dht-03.png)

> [!tip] Scala del miglioramento
>
> Con $N = 10^6$ nodi, il routing sequenziale richiede fino a 500.000 hop. Con la finger table, i salti scendono a $\log_2(10^6) \approx$ **20 hop**.

## Load Balancing e Virtual Server

Il load imbalance si verifica a causa di spazio di indirizzamento non uniforme, documenti molto pesanti, o hotspot (dati virali e altamente richiesti).
La soluzione standard prevede l'uso di **virtual server**: ogni macchina fisica gestisce più ID virtuali sull'anello, frammentando le responsabilità e distribuendo meglio il carico. Resta comunque la sfida aperta di gestire hotspot eccezionali.

---

# Kademlia (Protocollo DHT Avanzato)

Kademlia è un protocollo DHT (2002) ed è considerato lo standard de facto su Internet (usato in Ethereum, IPFS, BitTorrent Mainline DHT, eMule KAD).
Le peculiarità che lo rendono superiore ai predecessori (come Chord) includono:
- Apprendimento **automatico** del routing osservando il traffico passante.
- Supporto al **parallel routing** (richieste asincrone parallele per abbassare la latenza).
- L'uso della metrica **XOR** per la misurazione delle distanze e la disposizione dei contatti.

## Spazio degli Identificatori e Metrica XOR

Invece di usare una distanza numerica circolare (come Chord), Kademlia tratta gli identificatori (lunghi $M$ bit) in un **trie binario completo**, dove ogni foglia rappresenta un nodo o una chiave. Per assegnare le chiavi ai nodi si può immaginare di calcolare il *Lowest Common Ancestor* nel trie; tuttavia, operativamente, Kademlia definisce la distanza tramite l'operatore **XOR**.

> [!definition] Distanza XOR
>
> $d(x, y) = x \oplus y$. Un contenuto viene memorizzato sul nodo con distanza XOR minima rispetto alla chiave del contenuto stesso. 
> Questa metrica gode di simmetria ($d(x,y)=d(y,x)$) e disuguaglianza triangolare.

La simmetria è fondamentale: se il nodo A riceve una query da B, B e A sono esattamente alla stessa distanza. Questo significa che A può inserire B nella propria routing table gratuitamente (apprendimento simmetrico), cosa non valida nell'anello asimmetrico di Chord. L'unidirezionalità della XOR garantisce che le ricerche per la stessa chiave convergano sempre sullo stesso percorso.

![Albero binario dello spazio delle chiavi di Kademlia. Le foglie rappresentano i nodi. Maggiore è la lunghezza del prefisso condiviso tra due nodi (es. `110` e `111`), minore è la loro distanza secondo la metrica XOR.](images/Pasted-image-20260407111031.png)

## Routing Table e K-Buckets

Ogni nodo mantiene una routing table divisa in $M$ **K-Buckets**.

> [!definition] K-Bucket
>
> Una lista di al massimo $k$ contatti per il vicinato logico (dove la distanza XOR $d \in [2^{i-1}, 2^i)$). I contatti sono ordinati per *recency* (dal meno recente al più recente).

Quando arriva un messaggio, il mittente viene aggiunto in coda se il bucket non è pieno. Se il bucket è pieno, Kademlia esegue un ping al contatto in testa (il più vecchio); se questo risponde, viene mantenuto e il nuovo nodo scartato, altrimenti viene sostituito.
Questa politica **favorisce i nodi vecchi**, sfruttando l'assunto statistico che i peer connessi da più tempo sono i più affidabili, garantendo anche una forte resistenza agli attacchi DoS (uno spam di nuovi nodi fasulli non spiazzerà i vecchi e stabili).

![Partizionamento dello spazio degli ID visto dalla prospettiva del nodo rosso. Ogni sotto-albero corrisponde a un "k-bucket" nella routing table del nodo, permettendo di localizzare qualsiasi chiave in $O(\log N)$ salti.](images/Pasted-image-20260407111152.png)

## Lookup Iterativo e Parallelo

Kademlia supporta il lookup iterativo e, soprattutto, **parallelo** controllato dal parametro $\alpha$. Anziché attendere la risposta di un singolo nodo, il richiedente interroga simultaneamente $\alpha$ contatti (es. $\alpha=3$).

- Ogni iterazione riduce lo spazio di ricerca (prefix match routing) e restituisce fino a $k$ nuovi nodi vicini.
- Procedendo, il lookup si ferma quando i contatti interrogati non restituiscono nodi più vicini di quelli già noti.
- Il routing parallelo abbatte le latenze dovute a timeout e garantisce alta affidabilità al churn di rete.

## Gestione dei Dati (Store e Join)

L'operazione `STORE` prevede la memorizzazione sui $k$ nodi più vicini. I dati sono *soft-state*: devono essere **ripubblicati periodicamente** (es. ogni 24 ore) dall'originatore. 
Kademlia adotta nativamente il **caching lungo il percorso**: un dato appena recuperato viene messo in cache temporanea sui nodi intermedi della ricerca, aiutando a mitigare il problema degli hotspot per contenuti virali.

Un nuovo nodo entra (Join) contattando un bootstrap node noto ed eseguendo `FIND_NODE` prima del suo stesso ID, poi di ID casuali distribuiti nello spazio XOR, popolando gradualmente tutti i suoi K-Buckets in modo fluido e adattivo, superando la rigidità di Chord.

### Sintesi: Chord vs Kademlia

| Aspetto | Chord | Kademlia |
|---|---|---|
| **Metrica** | Distanza numerica (anello) | XOR (Trie Binario) |
| **Simmetria** | No — finger table asimmetriche | Sì — apprendimento mutuale gratuito |
| **Routing** | Ricorsivo o iterativo | Iterativo + parallelo ($\alpha$ nodi) |
| **Lookup** | $O(\log N)$ hop | $O(\log N)$ hop |
| **Aggiornamento routing table** | Messaggi dedicati | Effetto collaterale dei lookup |
| **Tolleranza ai guasti** | Limitata | Alta (parallel routing + bucket policy) |
