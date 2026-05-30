# Capitolo 8 - Laboratorio Reti P2P e Analisi di Bitcoin

## P2P Networks in Bitcoin ed Ethereum

Questo capitolo apre la sezione applicativa della parte P2P: anziché discutere in astratto le proprietà delle reti overlay, si guarda come due blockchain reali — Bitcoin ed Ethereum — abbiano implementato, ciascuna a modo suo, il livello di comunicazione peer-to-peer su cui tutto il resto (consenso, propagazione delle transazioni, sincronizzazione degli stati) si appoggia.

L'obiettivo è fare da ponte tra la teoria (classificazione degli overlay, Kademlia, DHT) e ciò che si troverà effettivamente installando un client Bitcoin Core o un nodo `geth`. La chiave di lettura è il confronto: **Bitcoin ha scelto un overlay non strutturato** basato su gossip, **Ethereum uno strutturato** basato su Kademlia — due risposte molto diverse allo stesso problema, scoprire peer con cui parlare senza conoscere la topologia globale.

> [!info] Informazioni organizzative
>
> Il modulo di laboratorio segue in modo "organico" il modulo teorico: la scaletta degli argomenti si adatta a quelli già visti a lezione. Il materiale di riferimento è costituito dai link inseriti nelle slide di ogni laboratorio, e le domande possono essere poste in ufficio (333 Dip. Informatica) o via Teams su richiesta. Ogni studente lavora con il proprio dispositivo (*bring your own device*).

### Il problema di base delle reti P2P

Prima di confrontare i due approcci conviene ricordare qual è il problema comune. In una rete peer-to-peer un nodo possiede **solo informazioni topologiche locali**: non conosce — e, per ragioni di privacy e resistenza agli attacchi, **non deve** conoscere — la topologia complessiva. Ogni partecipante vede soltanto i propri vicini diretti.

Questa limitazione non è solo una scelta di design: è un requisito di sicurezza. Una rete in cui ogni nodo pubblica la lista completa dei peer sarebbe banalmente attaccabile, perché un avversario potrebbe ricostruire mappature globali e scegliere bersagli mirati.

Una rete P2P ben progettata deve essere resistente ad almeno tre famiglie di attacchi:

- **Sybil attack**: l'avversario crea un numero arbitrario di identità fittizie per influenzare la rete (routing, consenso, gossip)
- **Eclipse attack**: l'avversario circonda un nodo vittima con peer sotto il suo controllo, isolandolo dal resto della rete
- **Partizionamento**: l'avversario divide la rete in componenti non comunicanti, permettendo ad esempio di presentare stati divergenti a due sottoinsiemi di vittime

> [!warning] Bootstrapping problem
>
> Come fa un nodo appena avviato a scoprire il primo peer a cui connettersi, se per definizione non conosce nessuno? Questa "gallina-uovo" è nota come **bootstrapping problem** e viene tipicamente risolta con una lista di nodi di fiducia hardcoded nel client o con query DNS. È un punto di fragilità: chi controlla quei seed controlla potenzialmente anche chi riesce a entrare nella rete.

La scelta architetturale fondamentale, fatta questa premessa, è fra due famiglie di overlay:

![Le due grandi famiglie di overlay P2P utilizzate dalle principali blockchain.](images/mermaid-lezione-5-lab-p2p-networks-in-bitcoin-ed-ethereum-01.png)

In entrambi i casi lo scopo è lo stesso: **abilitare la comunicazione per un'applicazione decentralizzata**. Le strade scelte per raggiungerlo sono molto diverse.

### Bitcoin: overlay non strutturato e gossip

#### Struttura generale

Bitcoin — almeno nella sua forma attuale, senza considerare Lightning — è una **rete di comunicazione P2P il cui unico scopo è scambiarsi informazioni su uno stato globale condiviso**. Le informazioni sono transazioni e blocchi; lo stato globale è il set UTXO.

Le scelte progettuali del livello network di Bitcoin si possono riassumere così:

| Aspetto | Scelta di Bitcoin |
|---|---|
| Overlay | Non strutturato, **gossip** |
| Bootstrapping | Lista DNS + hardcoded |
| Privacy | Randomizzazione (nessuna geolocalizzazione) |
| Sicurezza | Connessioni cifrate solo dalla v27+ (apr. 2024) |
| Trasporto | TCP |

> [!note] Cifratura tardiva
>
> Fino all'aprile 2024 le connessioni tra nodi Bitcoin erano in chiaro. Questo permetteva, a chi era posizionato sulla rete (ISP, punti di interscambio), di distinguere facilmente il traffico Bitcoin e fare fingerprinting. La v27 introduce finalmente il supporto nativo al cifrato, con BIP 324.

#### Node discovery in Bitcoin

Un nodo appena avviato segue un protocollo relativamente semplice per entrare a far parte della rete:

1. **Ottiene una lista di indirizzi candidati** da DNS di fiducia o da una lista hardcoded: ad esempio `nslookup seed.bitcoin.sipa.be` restituisce gli IP di una serie di nodi "seeder" mantenuti da sviluppatori noti della community. L'elenco hardcoded nel sorgente vive in `src/chainparamsseeds.h`.
2. **Invia un messaggio `version`** a uno o più di questi peer per tentare la connessione.
3. Se il peer accetta, risponde con un messaggio **`verack`** (version acknowledgement).
4. Da quel momento il nodo può chiedere altri peer a chi già conosce tramite il messaggio **`getaddr`**, ricevendo in risposta una lista di indirizzi di altri partecipanti alla rete.
5. Periodicamente, il nodo **annuncia se stesso** (cioè invia la propria `addr`) ad alcuni vicini scelti casualmente, così che l'informazione della sua presenza si propaghi per gossip.

![Handshake iniziale di un nuovo nodo Bitcoin: dal seed DNS all'inserimento attivo nella rete.](images/mermaid-lezione-5-lab-p2p-networks-in-bitcoin-ed-ethereum-02.png)

Una volta stabilita la rete di vicini, i messaggi applicativi veri e propri — transazioni e blocchi — vengono propagati con un meccanismo a tre fasi: `inv` annuncia la disponibilità di un oggetto (un hash), `getdata` lo richiede, infine arriva il `block` o `tx`. Tecniche come **trickle** e **diffusion** randomizzano i tempi di propagazione per ridurre la possibilità che un osservatore risalga al nodo originatore di una transazione.

#### Gestione delle connessioni

Un nodo Bitcoin mantiene un numero di connessioni "target" tra **8 e 11**, e un massimo configurabile (di default **125**). Il parametro `-maxconnections=<num>` controlla quest'ultimo. La logica concreta risiede in `src/net.h` nel repository di Bitcoin Core.

> [!tip] Perché 8 connessioni
>
> Il numero basso non è casuale: pochi peer stabilmente connessi bastano a garantire la raggiungibilità (ogni messaggio fa solo pochi hop prima di propagarsi a tutta la rete), limitano il consumo di banda e — soprattutto — rendono più costoso per un avversario circondare un nodo. Con 125 come limite massimo c'è spazio per accettare connessioni in ingresso da altri nodi.

#### Monitoraggio della rete

Essendo Bitcoin una rete aperta, chiunque può scansionarla e tenerne conteggio. Due strumenti spesso citati:

- [bitnodes.io](https://bitnodes.io/) — conta i nodi raggiungibili e mostra grafici storici
- [21.ninja](https://21.ninja/) — visualizza la propagazione dei blocchi

Questi dashboard sono utili in due sensi: danno un'idea di quanti nodi sono "full" (oggi dell'ordine di decine di migliaia) e, guardando la serie temporale, permettono di correlare eventi (hard fork, aggiornamenti software) con variazioni nella topologia.

#### Attacchi specifici al layer P2P di Bitcoin

Oltre ai Sybil/eclipse classici, la scarna sicurezza di rete di Bitcoin ha prestato il fianco storicamente a:

- **DNS poisoning** dei seed: se l'attaccante compromette la risoluzione DNS di un seed, può imporre a tutti i nuovi nodi una visione parziale della rete
- **Network listening**: l'intercettazione in chiaro del traffico (risolta solo con la v27)
- **Fingerprinting tramite il "addresses cookie"**: sfruttando il modo in cui i nodi memorizzano e ripropagano le `addr` si può ricostruire una mappa implicita dei peer, violando la privacy topologica

> [!note] Riferimento
>
> L'articolo di Biryukov et al. (<https://arxiv.org/pdf/1410.6079>) è un classico su come il livello di rete di Bitcoin leaks informazioni che minano la privacy degli utenti.

### Ethereum: overlay strutturato con Kademlia

Ethereum risponde allo stesso problema di Bitcoin — scambiare informazioni sullo stato globale — ma con un impianto più sofisticato, sia perché nato dopo (con più esperienza di attacchi), sia perché le sue esigenze applicative (molti sub-protocolli) lo richiedono.

| Aspetto | Scelta di Ethereum |
|---|---|
| Overlay | Strutturato, **Kademlia** |
| Bootstrapping | Lista hardcoded di *bootnodes* |
| Privacy | Randomizzazione nella scelta dei vicini |
| Sicurezza | Connessioni **autenticate e cifrate** |
| Trasporto | **UDP** per node discovery, **TCP** per comunicazione |

#### Perché una DHT per il P2P

Kademlia è una DHT — una *distributed hash table* — e l'argomento per cui una DHT sia preferibile a un gossip non strutturato è ormai consolidato:

- **Decentralizzazione**: non serve coordinarsi per costruire la propria tabella di routing
- **Fault tolerance / dinamismo**: la struttura si adatta al *churn* (nodi che entrano ed escono continuamente), entro limiti ragionevoli
- **Scalabilità e load balancing**: la quantità di informazione locale cresce come $O(\log n)$ nel numero di nodi, e il routing richiede $O(\log n)$ hop

> [!tip] Il log magico
>
> Le DHT "log/log" sono il punto di equilibrio ideale: uno stato di routing piccolo che garantisce comunque latenze basse. Questo è ciò che permette a una rete con decine di migliaia di nodi Ethereum di continuare a scoprire peer in tempi ragionevoli.

#### Come Kademlia è adattato in Ethereum

Le differenze rispetto al Kademlia "da manuale" sono interessanti e riflettono la diversa finalità. In Kademlia tradizionale si usa la DHT per cercare **valori associati a chiavi**. In Ethereum **non si fanno value lookup**: la DHT serve esclusivamente per trovare peer vicini — dove "vicino" non significa vicino geograficamente, ma vicino nello spazio degli identificatori.

| Dimensione | Kademlia "classico" | Kademlia di Ethereum |
|---|---|---|
| Chiavi vs nodi | Spazi distinti, key lookup | Stesso spazio, **solo node lookup** |
| Dimensione ID | Tipicamente 160 bit | **512 bit** (chiave pubblica) |
| Hash per distanza | SHA-1 | **Keccak-256** |
| Numero di bucket | 160 | **256** |
| Elementi per bucket | $k = 20$ | $k = 16$ |
| Meccanismo di reputazione | Uptime | Reputazione complessa (ping/pong + metriche) |

Gli **identificatori dei peer** in Ethereum sono la chiave pubblica stessa (già casuale per costruzione), e la distanza è calcolata come XOR tra due ID, prendendo il bit più significativo — esattamente lo schema di Kademlia. La tabella di routing è organizzata in 256 bucket, uno per ogni possibile "prefisso di distanza", ciascuno contenente fino a 16 elementi.

> [!definition] Enode (Ethereum Node Identifier)
>
> Il formato con cui un nodo Ethereum è identificato a livello di network è:
>
> ```
> enode://<public-key>@<IP>:<TCP-port>?discport=<UDP-discovery-port>
> ```
>
> Esempio reale:
>
> ```
> enode://6f8a80d14311c39f...cac9f77166ad92a0@10.3.58.6:30303?discport=30301
> ```
>
> La parte prima della `@` è la chiave pubblica a 512 bit (codificata esadecimale); poi l'IP, la porta TCP per la comunicazione autenticata, e la porta UDP dedicata alla *discovery* Kademlia.

> [!warning] Privacy e ricostruzione della tabella
>
> La tabella di routing di un nodo viene usata per **conoscere** i peer, ma non necessariamente per **connettersi** direttamente a loro. Questo è uno scudo di privacy: se un avversario riuscisse a ricostruire interamente le tabelle di routing di altri nodi, potrebbe dedurne informazioni sensibili. I vicini di comunicazione effettivi vengono scelti a caso tra i peer responsivi di tutti i bucket.

#### Stack a livelli (tiered stack)

La comunicazione in Ethereum è stratificata in modo che ogni livello si occupi di una sola responsabilità:

![Lo stack tiered di Ethereum: RLPx fornisce serializzazione e trasporto cifrato, DEVp2p gestisce le connessioni, e diversi sub-protocolli usano lo stesso canale in multiplex.](images/mermaid-lezione-5-lab-p2p-networks-in-bitcoin-ed-ethereum-03.png)

- **RLPx** (*Recursive Length Prefix* serialization + crittografia) è il livello che rende possibile trovare peer e parlare con loro in modo sicuro. Definisce l'handshake iniziale e la serializzazione binaria dei messaggi.
- **DEVp2p** è il protocollo che stabilisce e mantiene le connessioni persistenti su cui poi si parlano i sub-protocolli.
- **Sub-protocolli** come `eth` (transazioni, blocchi, stato), `snap` (sync veloce), `les` (light client) viaggiano sulla stessa connessione DEVp2p in **multiplexing**.

#### Node discovery in pratica

La scoperta dei peer avviene in due fasi distinte, sui due trasporti diversi:

**Fase UDP (Kademlia)** — localizzare peer:

1. Il nodo chiede i "vicini di se stesso" a uno dei **bootnode** hardcoded (vedi `params/bootnodes.go` nel repository go-ethereum).
2. Ricevuta la lista iniziale, iterativamente invia `findnode` ai peer appena scoperti per riempire i bucket.
3. Si effettua un **bonding** via `ping/pong` per verificare che i peer siano vivi.

**Fase TCP (RLPx + DEVp2p)** — stabilire la comunicazione vera e propria:

1. **Handshake RLPx**: verifica versioni, stabilisce chiavi effimere, autentica la controparte. Documentazione ufficiale: `devp2p/rlpx.md#initial-handshake`.
2. **Messaggio `Hello`** per comunicare le capability: quali sub-protocolli si è in grado di parlare. Da qui in poi il multiplexing è possibile.

Importante: indipendentemente da quale sub-protocollo applicativo si usi, è sempre RLPx a fornire il canale sottostante di autenticazione e cifratura.

![Le due fasi della scoperta e connessione in Ethereum: UDP per trovare peer, TCP per parlarci in sicurezza.](images/mermaid-lezione-5-lab-p2p-networks-in-bitcoin-ed-ethereum-04.png)

#### Monitorare la rete Ethereum

Come per Bitcoin, anche Ethereum ha dashboard pubbliche. [etherscan.io/nodetracker](https://etherscan.io/nodetracker) è il riferimento più usato per avere un quadro del numero di nodi attivi e della loro distribuzione geografica.

### Esempio pratico: connettersi con `geth` a una rete privata

La parte operativa del laboratorio mostra come usare `geth` (il client Go di Ethereum) per entrare in una piccola rete privata, bypassando o controllando il meccanismo di discovery.

#### Opzioni rilevanti

Due flag da ricordare:

- `--bootnodes enode://...,enode://...` permette di specificare *manualmente* la lista di bootnode invece di affidarsi a quelli hardcoded. Serve per reti private.
- `--nodiscover` disabilita del tutto la node discovery: utile quando si vuole una rete chiusa di nodi noti a priori.

#### Procedura passo-passo

> [!example] Avvio di un nodo su una rete privata
>
> 1. Installare `geth` seguendo la [guida ufficiale](https://geth.ethereum.org/docs/getting-started/installing-geth).
> 2. Creare una cartella di lavoro per i dati del nodo:
>    ```bash
>    mkdir testLecture1
>    ```
> 3. Procurarsi il file di genesi `testlecture1.json` (il significato dei suoi campi verrà discusso più avanti nel corso).
> 4. Inizializzare il datadir con il file di genesi:
>    ```bash
>    geth --datadir testLecture1/ init testlecture1.json
>    ```
> 5. Avviare il nodo con una `networkid` custom e una porta dedicata, aprendo la console JavaScript interattiva:
>    ```bash
>    geth --datadir ~/testLecture1/ --networkid 35353 --port 3333 --vmdebug console
>    ```

Una volta dentro la console si possono ispezionare e manipolare i peer:

- `admin.nodeInfo` — stampa la propria `enode`, da condividere con altri per farsi trovare
- `admin.peers` — elenca i peer attualmente connessi
- `admin.addPeer("enode://...")` — aggiunge esplicitamente un peer di cui si conosce l'enode, senza passare dalla discovery

> [!tip] Reti private e `--nodiscover`
>
> In un laboratorio con pochi nodi conosciuti, disabilitare la discovery e usare `admin.addPeer` è la strada più semplice per ottenere una rete pulita, dove si ha controllo totale su chi parla con chi. Riprodurre questo scenario è essenziale per poter osservare in maniera deterministica il comportamento dei protocolli ai livelli superiori (consenso, smart contract, ...).

### Attacchi alla topologia di Ethereum

Il design di Kademlia è stato pensato per **scoraggiare** (non impedire) la ricostruzione completa della routing table altrui. Due sono le strategie che un avversario può tentare:

- **Usare il set noto degli ID esistenti**: invece di cercare ID casuali nello spazio a 512 bit (enorme), ci si concentra sugli ID dei peer effettivamente presenti nella rete. Questo riduce drasticamente lo spazio di ricerca.
- **Brute force mirato**: poiché in pratica solo i bucket con prefisso corto comune sono popolati (gli altri sarebbero dedicati a "distanze" in cui statisticamente non c'è nessuno), si concentra lo sforzo lì.

La difesa principale — lo **hash step** con Keccak-256 applicato agli ID — rende il costo della ricostruzione dipendente dal target e non lineare: non basta fare 256 richieste `findnode`, bisogna scegliere bene i target per coprire i bucket popolati.

> [!question] Domanda aperta di ricerca
>
> Quando un nodo riceve un `findnode`, risponde con un messaggio `neighbors` contenente i 16 nodi più vicini trovati nella propria tabella. Quanti messaggi `findnode`, con quali target, sono necessari per scaricare completamente la routing table di un nodo?
>
> È una domanda non banale. I lavori di riferimento sono Henningsen et al. (<https://ieeexplore.ieee.org/document/8969695>) e Marcus et al. (<https://eprint.iacr.org/2018/236.pdf>), che analizzano eclipse attack e ricostruzione di tabelle Kademlia in Ethereum.

> [!abstract] Bitcoin vs Ethereum al layer P2P
>
> Entrambe le reti rispondono allo stesso problema — propagare informazioni in una rete aperta senza conoscere la topologia globale — ma con filosofie opposte. **Bitcoin** privilegia la semplicità di un gossip non strutturato: poche connessioni, propagazione randomizzata, sicurezza di rete aggiunta solo tardivamente. **Ethereum** investe in un overlay strutturato via Kademlia, con autenticazione e cifratura by design, e uno stack tiered (RLPx / DEVp2p / sub-protocolli) che gli permette di ospitare comodamente molti protocolli applicativi sulla stessa infrastruttura. La differenza non è cosmetica: influenza la resilienza agli attacchi di eclipse, la facilità di fingerprinting, e la capacità di evolvere il protocollo aggiungendo nuovi sub-protocolli senza rompere la rete.

## Bitcoin con bitcoinj

Ci dedichiamo ora a Bitcoin visto "dall'interno" tramite la libreria **bitcoinj**. Dopo aver discusso il layer P2P in astratto, in questa sezione si scrive vero codice Java che apre connessioni verso la rete Bitcoin, stampa informazioni sui peer, scarica un blocco di esempio dalla **testnet**, genera indirizzi di tutti i tipi previsti dal protocollo (legacy, SegWit, Taproot) e infine ispeziona il famoso **genesis block** estraendone il messaggio di Satoshi.

> [!info] Obiettivi concreti
>
> - Installare Bitcoin Core e importare `bitcoinj` in un progetto Java
> - Scrivere un client che si collega alla rete testnet e richiede un blocco specifico dato il suo hash
> - Generare chiavi ECDSA e derivarne indirizzi di tipi diversi (P2PKH, P2WPKH)
> - Scaricare e decodificare il genesis block di Bitcoin, in particolare la `coinbase` e il messaggio testuale in essa contenuto
> - **Esercizio 1**: scrivere un programma che genera indirizzi fino a trovarne uno con un prefisso scelto (vanity address)

### Strumenti e link di riferimento

Il laboratorio si appoggia su due strumenti principali. **Bitcoin Core** è il client di riferimento, scaricabile dal sito ufficiale:

- [bitcoin.org/en/download](https://bitcoin.org/en/download)

Per scrivere codice che parla con la rete Bitcoin dall'interno di un'applicazione Java si usa **bitcoinj**, una libreria molto matura che astrae il protocollo di rete, la serializzazione dei messaggi e la gestione delle chiavi:

- Sito ufficiale: [bitcoinj.org](https://bitcoinj.org/)
- JAR direttamente scaricabile da Maven Central: [bitcoinj-core-0.17.jar](https://search.maven.org/remotecontent?filepath=org/bitcoinj/bitcoinj-core/0.17/bitcoinj-core-0.17.jar)
- Javadoc della versione 0.17: [bitcoinj.org/javadoc/0.17/](https://bitcoinj.org/javadoc/0.17/)

> [!tip] Perché `bitcoinj`
>
> Scrivere da zero un client che parli il protocollo di Bitcoin è un'impresa: bisogna implementare la serializzazione dei messaggi, la gestione delle connessioni, le regole di consenso, la verifica degli header, ecc. `bitcoinj` fornisce tutto questo come API Java, permettendo di concentrarsi sulla logica applicativa. È la stessa libreria usata in produzione da wallet come **BitcoinJ Wallet** e da svariate soluzioni enterprise che integrano Bitcoin.

### Esempio di connessione alla rete

Il seguente blocco di codice mostra come bastino poche decine di righe per collegarsi alla **testnet3**, scoprire i peer tramite DNS, e scaricare un blocco noto.

L'**hash del blocco** di riferimento è preso da [blockstream.info](https://blockstream.info/testnet/block/0000000000000adc6423b570d751efcdf5e019d3d955fee155c28925913cb667) — un explorer che permette di navigare la testnet.

#### Struttura del programma

```java
public static void connectionTest() throws InterruptedException {
    NetworkParameters netParams = TestNet3Params.get();

    BlockStore blockStore = new MemoryBlockStore(netParams.getGenesisBlock());
    BlockChain blockChain;

    try {
        blockChain = new BlockChain(netParams.network(), blockStore);
        PeerGroup peerGroup = new PeerGroup(netParams, blockChain);
        peerGroup.setUserAgent("Sample App", "1.0");
        peerGroup.addPeerDiscovery(new DnsDiscovery(netParams));
        peerGroup.start();

        Thread.sleep(10000);
        printNetStats(peerGroup);

        for (Peer p : peerGroup.getConnectedPeers()) {
            System.out.println(p.getAddr());
        }

        while (peerGroup.getConnectedPeers().isEmpty())
            Thread.sleep(5000);

        Sha256Hash blockHash = Sha256Hash.wrap(
            "0000000000000adc6423b570d751efcdf5e019d3d955fee155c28925913cb667");
        Block block;
        boolean flag = true;

        try {
            while (flag) {
                Peer pFirst = peerGroup.getConnectedPeers()
                    .get(peerGroup.getConnectedPeers().size() - 1);
                Future<Block> future = pFirst.getBlock(blockHash);
                block = future.get(5, TimeUnit.SECONDS);
                System.out.println("Here is the block: " + block);
                flag = false;
            }
        } catch (TimeoutException ex) {
            // do nothing, just try a new peer
        } catch (ExecutionException ex) {
            // do nothing, just try a new peer
        }

        Thread.sleep(10000);
        printNetStats(peerGroup);
        peerGroup.stop();

    } catch (BlockStoreException ex) {
        System.getLogger(P2PBClab1project.class.getName())
            .log(System.Logger.Level.ERROR, (String) null, ex);
    }
}

public static void printNetStats(PeerGroup peerGroup) {
    System.out.println("\n\nNETWORK INFO:");
    System.out.println("Max connections: " + peerGroup.getMaxConnections());
    System.out.println("Current connections: " + peerGroup.numConnectedPeers());
    System.out.println("Chain height: " + peerGroup.getMostCommonChainHeight());
    System.out.println("\n\n");
}
```

#### Cosa fa, passo per passo

Il flusso concettuale è lineare e ricalca esattamente la discovery vista nella lezione precedente:

![Pipeline dell'esempio di connessione: tutto ruota attorno a `PeerGroup`, l'astrazione `bitcoinj` che gestisce il pool di connessioni P2P.](images/mermaid-lezione-10-lab-bitcoin-con-bitcoinj-01.png)

La chiave è il `PeerGroup`: rappresenta un insieme di connessioni gestite automaticamente, incluso il mantenimento del numero target di peer e la ri-connessione in caso di timeout. `DnsDiscovery` è il meccanismo di bootstrapping che interroga i seed DNS.

La richiesta del blocco specifico (`peer.getBlock(hash)`) restituisce un `Future` — quindi è asincrona — e il loop `while(flag)` tenta la richiesta su peer diversi finché uno risponde entro 5 secondi. Questo pattern è tipico delle reti P2P: nessun peer specifico ha il "dovere" di rispondere, quindi il client deve essere preparato a ritentare.

> [!warning] Blocco di esempio su testnet
>
> L'hash `0000000000000adc6423b570d751efcdf5e019d3d955fee155c28925913cb667` si riferisce a un blocco **testnet**, non mainnet. È importante perché in testnet le regole di PoW sono rilassate (difficulty molto più bassa) e gli indirizzi hanno un prefisso diverso. Cambiare `TestNet3Params` in `MainNetParams` fa sì che il client si colleghi alla rete di produzione e tenti di recuperare blocchi reali — occhio alla quantità di dati!

### Indirizzi Bitcoin e loro tipologie

Una volta collegati alla rete, si passa a generare chiavi e indirizzi. Esistono diversi tipi di indirizzo in Bitcoin mainnet:

> [!definition] Tipi di indirizzo Bitcoin (mainnet)
>
> | Tipo | Prefisso | Descrizione |
> |---|---|---|
> | **Legacy P2PKH** | `1...` | Pay-to-Public-Key-Hash — il formato storico |
> | **Legacy P2SH** | `3...` | Pay-to-Script-Hash — script generici (multisig, timelock, ...) |
> | **Nested SegWit P2SH-P2WPKH/P2WSH** | `3...` | SegWit impacchettato in un P2SH per compatibilità — solo transizionale |
> | **SegWit nativo P2WPKH/P2WSH** | `bc1q...` | Bech32, witness version 0 |
> | **Taproot P2TR** | `bc1p...` | Bech32m, witness version 1 — singole firme Schnorr o Tapscript |

Il nested SegWit (`3...`) è stato utile durante la transizione per permettere a wallet che non conoscevano il nuovo formato `bc1q` di inviare fondi a destinatari SegWit, ma oggi è essenzialmente deprecato: i nuovi wallet preferiscono generare direttamente `bc1q` (SegWit v0) o `bc1p` (Taproot) per beneficiare delle fee ridotte e delle nuove funzionalità.

#### Generare un indirizzo da una chiave

```java
public static void createNewAddr() {
    NetworkParameters netParams1 = TestNet3Params.get();

    ECKey key = new ECKey();
    System.out.println("We created key " + key);
    Address addressFromKey = key.toAddress(ScriptType.P2PKH, netParams1.network());

    System.out.println("On the " + netParams1.network() +
        " network, we can use this address " + addressFromKey);

    NetworkParameters netParams2 = MainNetParams.get();
    addressFromKey = key.toAddress(ScriptType.P2PKH, netParams2.network());
    System.out.println("On the " + netParams2.network() +
        " network, we can use this address " + addressFromKey);

    addressFromKey = key.toAddress(ScriptType.P2WPKH, netParams2.network());
    System.out.println("On the " + netParams2.network() +
        " network, we can use this address " + addressFromKey);
}
```

L'esempio mostra tre cose importanti:

1. **Una stessa chiave ECDSA** (`ECKey key = new ECKey()`) può essere usata per derivare più indirizzi.
2. Lo stesso hash della chiave pubblica produce **indirizzi con prefisso diverso** a seconda della rete (testnet vs mainnet) perché il byte di version cambia.
3. Lo stesso hash produce anche **indirizzi formattati diversamente** a seconda dello `ScriptType` scelto: con `P2PKH` si ottiene un indirizzo legacy `1...`, con `P2WPKH` si ottiene un SegWit nativo `bc1q...`. La chiave privata è la stessa, ma lo script di lock differisce, e quindi cambia l'encoding dell'indirizzo.

> [!tip] Chiave → indirizzo non è iniettivo sul tipo
>
> Una stessa chiave genera indirizzi di tipo diverso perché l'indirizzo è una funzione di (hash della chiave pubblica, tipo di script, rete). Se si invia denaro al P2PKH di una chiave, non è automaticamente spendibile con la firma sul P2WPKH della stessa chiave: lo script di unlock è diverso. Il proprietario della chiave può firmare per entrambi, ma deve sapere a quale dei suoi indirizzi gli è stato inviato il denaro.

#### Esercizio 1 — Vanity address

> [!example] Esercizio 1: vanity address
>
> **Consegna**: scrivere un programma che genera un indirizzo Bitcoin il cui encoding **inizia con una stringa scelta** dall'utente (es. `1Fabio...`, `bc1qgold...`).
>
> **Approccio**: non esiste un modo per costruire una chiave che produca un indirizzo con un prefisso specifico senza invertire la funzione hash (cosa infattibile). L'unica strada è **brute force**: generare chiavi casuali una dopo l'altra, calcolare l'indirizzo corrispondente, controllare se inizia con la stringa desiderata, e se no ripetere.
>
> ```java
> String target = "1Fab";
> while (true) {
>     ECKey key = new ECKey();
>     Address addr = key.toAddress(ScriptType.P2PKH, MainNetParams.get().network());
>     if (addr.toString().startsWith(target)) {
>         System.out.println("Found: " + addr);
>         System.out.println("Private key: " + key.getPrivateKeyAsWiF(MainNetParams.get().network()));
>         break;
>     }
> }
> ```
>
> Il tempo di esecuzione cresce **esponenzialmente** nella lunghezza del prefisso (approssimativamente un fattore 58 per ogni carattere aggiunto nel Base58): 3-4 caratteri si trovano in secondi, 6-7 in minuti, 10+ richiedono hardware dedicato.

> [!warning] Sicurezza delle vanity address
>
> Per chiavi cercate brute force su hardware proprio non c'è problema — la chiave privata resta locale. Si diffidi però dei servizi online che generano vanity address "per conto vostro": se il servizio genera la chiave e poi la invia, può trattenerne una copia e svuotare il wallet quando vi viene inviato denaro. L'unico pattern sicuro è lo **split-key vanity**, in cui la parte entropica proviene da voi e il servizio fornisce solo capacità di calcolo.

### Inspezione del genesis block

L'ultima parte di questa fase è l'ispezione del blocco 0 di Bitcoin — il **genesis block**, minato da Satoshi Nakamoto il 3 gennaio 2009.

> [!definition] Genesis block di Bitcoin
>
> Il blocco con hash `0x000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f` è il primo blocco della blockchain di Bitcoin. È **hardcoded** nel codice di ogni client e serve come radice di fiducia da cui far partire la verifica dell'intera catena. La sua ricompensa coinbase (50 BTC) è spendibile in teoria ma è considerata non-spendibile di fatto perché l'UTXO corrispondente non è mai stato incluso nel UTXO set di Bitcoin Core.
>
> Riferimento: [en.bitcoin.it/wiki/Genesis_block](https://en.bitcoin.it/wiki/Genesis_block)

#### Codice per leggere il genesis

```java
// 0x000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f
public static void getBtcGenesis() throws InterruptedException {
    NetworkParameters netParams = MainNetParams.get();

    Block genesis = netParams.getGenesisBlock();

    System.out.println(genesis);

    TransactionInput txIn = genesis.getTransactions().get(0).getInput(0);

    System.out.println(bytesToHex(txIn.getScriptBytes()));

    String message = hexToAscii(bytesToHex(txIn.getScriptBytes()));

    System.out.println(message);

    printBlockInfo(genesis);
    printTxInfo(genesis.getTransactions().get(0));
}

public static void printBlockInfo(Block blk) throws InterruptedException {
    System.out.println("Hash       " + blk.getHashAsString());
    System.out.println("Prev Hash  " + blk.getPrevBlockHash());
    System.out.println("Timestamp  " + blk.getTimeSeconds());
    System.out.println("Timestamp  " + blk.time());
}
```

#### Il messaggio di Satoshi

La parte più suggestiva è la decodifica del **coinbase script** della prima (e unica) transazione del genesis block. In una transazione normale l'input contiene la firma che sblocca l'UTXO speso; in una coinbase, che non spende nulla, il campo `scriptSig` è libero e Satoshi lo ha sfruttato per incidere un messaggio leggibile in ASCII:

```
The Times 03/Jan/2009 Chancellor on brink of second bailout for banks
```

È il titolo del *Times* di Londra di quel giorno. Serve a due scopi: **dimostrare che il blocco è stato minato non prima del 3 gennaio 2009** (non si può predire un titolo di giornale futuro), e lasciare traccia storica del contesto politico-finanziario in cui Bitcoin nasce — una risposta esplicita alla crisi bancaria e ai salvataggi pubblici.

> [!tip] Timestamping incorporato nel protocollo
>
> La tecnica di scrivere un riferimento pubblico verificabile (come un titolo di giornale) in un blocco per dimostrarne la datazione "non prima di" è essenzialmente un **timestamping crittografico** fatto in modo manuale. In seguito è stato formalizzato da servizi come OpenTimestamps, che permettono di inserire hash di documenti arbitrari nella blockchain di Bitcoin come prova di esistenza a una certa data.

#### Cosa estraiamo dal genesis

Eseguendo `printBlockInfo` e `printTxInfo` si vede concretamente la struttura di un blocco Bitcoin:

- **Hash** del blocco — `000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f`
- **Prev hash** — tutti zeri, perché non c'è un blocco precedente
- **Timestamp** — 1231006505 secondi Unix, cioè 3 gennaio 2009 18:15:05 UTC
- **Transazione coinbase** con il messaggio di cui sopra e un output di 50 BTC al public key di Satoshi (in formato P2PK, non P2PKH: è lo stile più vecchio)

> [!abstract] Risultati della prima fase con bitcoinj
>
> - Connessione alla **testnet Bitcoin** e scaricamento di un blocco richiesto per hash
> - **Generazione chiavi ECDSA** e derivazione indirizzi legacy (`P2PKH`) o SegWit nativi (`P2WPKH`)
> - Esercizio su vanity address tramite brute-force
> - Ispezione diretta del **genesis block** di Bitcoin con il messaggio di Satoshi decodificato

## Bitcoin Transactions e Scripts

Entriamo ora nel cuore della serializzazione del protocollo: si scrive codice Java per **ispezionare una transazione campo per campo**, **decodificare gli script** di input e output mostrandoli come sequenze di opcode leggibili, e si affronta il caso speciale delle transazioni con `OP_RETURN` — l'opcode usato per inserire dati arbitrari nella blockchain.

> [!info] Obiettivi di analisi delle transazioni
>
> - Scrivere una funzione `printTxInfo` che stampa in modo leggibile tutti i campi di una `Transaction` di bitcoinj
> - Scrivere una funzione `printScriptAsOpCodes` che trasforma il bytecode grezzo di uno script Bitcoin in una sequenza testuale di opcode, gestendo correttamente i dati push e l'`OP_RETURN`
> - Scaricare transazioni reali dalla blockchain in formato **raw hex**, deserializzarle, ispezionarle e verificare il risultato
> - Vedere esempi concreti di tre tipi di transazione: **legacy**, **SegWit**, con **OP_RETURN**

### Riferimenti utili

- [Deconstructing a Bitcoin transaction](https://dev.to/thunderbiscuit/deconstructing-a-bitcoin-transaction-4l2n) — descrizione campo-per-campo molto chiara
- [SegWit recap](https://learnmeabitcoin.com/technical/upgrades/segregated-witness/) — come il witness cambia la struttura e perché
- [Opcode Explained](https://opcodeexplained.com/opcodes/) — lista dettagliata di tutti gli opcode
- [OP_RETURN](https://learnmeabitcoin.com/technical/script/return/) — approfondimento sull'opcode
- [blockchain.info raw transaction endpoint](https://blockchain.info/rawtx/a637ad18fabee7ad3ccd51e317091a6e16991311c0c9b83233b140b66b114448?format=hex) — esempio che restituisce l'hex della transazione
- [Blockchain.com Decode Transaction](https://www.blockchain.com/explorer/assets/btc/decode-transaction) — tool web per verificare la decodifica

### Struttura di una transazione Bitcoin

Prima di scrivere codice conviene fissare mentalmente i campi. Una transazione Bitcoin, nel formato serializzato, si compone di:

![I campi di una transazione Bitcoin. `marker`/`flag` e `witness data` sono presenti solo nelle transazioni SegWit.](images/mermaid-lezione-11-lab-bitcoin-transactions-e-scripts-01.png)

La distinzione cruciale per il codice è fra transazione **legacy** e **SegWit**: nelle legacy la firma vive dentro `scriptSig` (un campo dell'input); nelle SegWit viene spostata in una sezione separata (`witness data`) in fondo alla transazione, lasciando `scriptSig` vuoto. Questo cambia il layout binario e richiede il parser di gestire i due casi. Bitcoinj si occupa di distinguerli automaticamente leggendo il **marker byte** (`0x00`) e il **flag byte** (`0x01`) che, se presenti subito dopo la version, segnalano una transazione SegWit.

> [!definition] Coinbase transaction
>
> La prima transazione di ogni blocco è la **coinbase**, che crea nuovi bitcoin (il block reward) e non ha un input spendibile precedente: il suo unico input ha `previous outpoint` con hash tutto-zero e indice `0xFFFFFFFF`, e `scriptSig` è lasciato libero dal miner per inserirvi dati arbitrari (tipicamente il numero del blocco per l'altezza — BIP 34 — o messaggi testuali, come fece Satoshi nel genesis).

### `printTxInfo` — stampare una transazione in modo leggibile

Il seguente codice stampa una `Transaction` di bitcoinj in formato umano, costringendo a distinguere i casi (coinbase vs regolare, con vs senza witness) e a ricavare gli indirizzi dai rispettivi script.

```java
public static void printTxInfo(Transaction tx) throws InterruptedException {
    // txHash, isCoinbase, weight, hasWitness
    StringBuilder line = new StringBuilder();
    boolean isCoinbase = false;
    boolean hasWitness = false;
    line.append(tx.getTxId().toString());
    line.append(",");
    if (tx.isCoinBase()) {
        isCoinbase = true;
        line.append("1");
    } else {
        isCoinbase = false;
        line.append("0");
    }
    line.append(",");
    line.append("" + tx.getWeight());
    line.append(",");
    if (tx.hasWitnesses()) {
        hasWitness = true;
        line.append("1");
    } else {
        hasWitness = false;
        line.append("0");
    }
    System.out.println("General info : " + line.toString());

    line = new StringBuilder();
    if (isCoinbase) {
        // check if it has messages inside input scripts
        boolean first = true;
        for (TransactionInput ii : tx.getInputs()) {
            if (first) first = false;
            else line.append("\n");
            line.append("Coinbase input script message? " +
                hexToAscii(bytesToHex(ii.getScriptBytes())));
        }
    } else {
        // not coinbase so there is at least one input
        // prevTx_Id, prevTxPos, script:
        boolean first = true;
        for (TransactionInput ii : tx.getInputs()) {
            if (first) first = false;
            else line.append("\n");
            line.append("Prev txHash " + ii.getOutpoint().hash().toString());
            line.append("\nPrev txPos  " + ii.getOutpoint().index());
            line.append("\nscriptSig   " + bytesToHex(ii.getScriptBytes()));
            if (ii.hasWitness()) {
                line.append("\nwitness     " + ii.getWitness().toString());
            }
        }
    }
    System.out.println("Inputs :\n" + line.toString());

    line = new StringBuilder();
    // addr, amount, outScriptBytes
    // there is always at least one output
    boolean first = true;
    for (TransactionOutput oo : tx.getOutputs()) {
        if (first) first = false;
        else line.append("\n");
        byte[] outScript = oo.getScriptBytes();
        String outAddr = ScriptParser.addrFromOut(outScript);
        int outType = ScriptParser.typeFromOut(outScript);
        if (outAddr == null) {
            // writes '#UNKNOWN#' as address if not decodable
            outAddr = "#UNKNOWN#";
        }
        line.append("Addr " + outAddr);
        line.append("\nAmount " + oo.getValue().getValue());
        line.append("\nscript " + bytesToHex(outScript));
        line.append("\nscript " + printScriptAsOpCodes(outScript));
        line.append("\nscript type " + ScriptTypeCustom.typeName(outType));
    }
    System.out.println("Outputs :\n" + line.toString());
}
```

#### Cosa vale la pena notare

- **`getTxId()`** restituisce il doppio SHA-256 dei campi "non witness" della transazione. Per le SegWit è utile perché rende l'ID immune dalla *malleability*: modificare la firma non cambia l'ID della transazione.
- **`getWeight()`** è la metrica usata da Bitcoin per calcolare le fee dopo SegWit: i byte witness contano 1, quelli non-witness contano 4. Il limite di blocco è 4M weight units.
- **Caso coinbase**: si stampa il contenuto dello `scriptSig` interpretato come ASCII, per vedere l'eventuale messaggio del miner.
- **Caso regolare**: per ogni input si stampa la coppia `(prev hash, prev index)` che identifica l'UTXO speso, il `scriptSig` in hex, e il witness se presente.
- **Per gli output**: si usa un `ScriptParser` custom che tenta di decodificare lo `scriptPubKey` in un indirizzo.

> [!tip] Indirizzo = pattern riconosciuto nello script
>
> Un **indirizzo non è un campo della transazione**: è una **reinterpretazione** dello `scriptPubKey` quando quest'ultimo ha una forma "nota". `OP_DUP OP_HASH160 <20B> OP_EQUALVERIFY OP_CHECKSIG` → P2PKH, `OP_HASH160 <20B> OP_EQUAL` → P2SH, e così via. Se lo script è arbitrario (es. un multisig bare, un timelock), non c'è un indirizzo standard da mostrare.

### `printScriptAsOpCodes` — decodificare uno script Bitcoin

Gli script di Bitcoin sono sequenze di byte che il parser deve interpretare come un misto di **opcode** (singoli byte con nome simbolico) e **push di dati** (un byte che dichiara la lunghezza, seguito dai dati).

```java
public static String printScriptAsOpCodes(byte[] script) {
    StringBuilder line = new StringBuilder();
    for (int i = 0; i < script.length;) {
        int val = Utilities.readUnsignedByte(script[i]);
        line.append(ScriptOpCodes.getOpCodeName(val));
        line.append(" ");
        i++;
        if ((val >= 1) && (val <= 75)) {
            for (int j = 0; j < val; j++) {
                line.append(byteToHex(script[i]));
                line.append(" ");
                i++;
            }
        } else if (val == 106) {
            while (i < script.length) {
                line.append(hexToAscii(byteToHex(script[i])));
                line.append(" ");
                i++;
            }
        }
    }
    return line.toString();
}
```

#### Logica del parser

Il parser ha tre rami:

- **Byte 1–75**: è un'istruzione implicita `OP_PUSHBYTES_N` — il byte stesso indica quanti byte successivi sono dati da pushare nello stack. Si stampano come hex.
- **Byte 106 (`OP_RETURN`)**: segnala che la transazione è "unspendable" e che tutto ciò che segue sullo script è **puro dato arbitrario**, interpretato come ASCII (per comodità: qualsiasi contenuto è ammesso).
- **Altri opcode**: si stampa solo il nome simbolico (es. `OP_DUP`, `OP_HASH160`, `OP_CHECKSIG`).

> [!warning] Parser semplificato
>
> La funzione non gestisce gli opcode di push a lunghezza esplicita (`OP_PUSHDATA1`, `OP_PUSHDATA2`, `OP_PUSHDATA4`, valori 76-78), che servono a pushare quantità di dati superiori a 75 byte. Per uno script P2PKH o P2SH standard non è un problema — gli hash sono 20 byte e le firme stanno sotto i 75. Per script più complessi bisognerebbe estendere il parser.

#### Esempio: decodifica di uno `scriptPubKey` P2PKH

Prendendo un output di tipo P2PKH, lo `scriptPubKey` in hex è tipicamente:
```
76 a9 14 <20-byte-hash> 88 ac
```
Passato a `printScriptAsOpCodes` restituisce:
```
OP_DUP OP_HASH160 OP_PUSHBYTES_20 <hex dell'hash> OP_EQUALVERIFY OP_CHECKSIG
```
— che è esattamente lo script canonico di pagamento a hash di chiave pubblica.

### OP_RETURN: dati arbitrari sulla blockchain

> [!definition] OP_RETURN
>
> `OP_RETURN` (opcode `0x6A`, decimale 106) termina immediatamente l'esecuzione dello script facendolo **fallire sempre**. Un output il cui `scriptPubKey` inizia con `OP_RETURN` non è mai spendibile: non esiste alcuna sequenza di `scriptSig` che possa farlo valutare a `true`. In compenso, i nodi Bitcoin accettano in coda all'opcode **fino a 80 byte** di dati arbitrari, che vengono così incisi permanentemente nella blockchain.

Il caso d'uso tipico è **timestamping**: si prende l'hash di un documento, lo si inserisce come payload di un `OP_RETURN`, si firma la transazione. Da quel momento esiste una prova pubblica e immutabile che il documento esisteva al timestamp del blocco che contiene la transazione. È l'idea alla base di servizi come [OpenTimestamps](https://opentimestamps.org/).

> [!tip] Perché OP_RETURN invece di mettere i dati nello scriptSig
>
> Si potrebbe teoricamente mettere dati arbitrari nello `scriptSig` di un input, ma quell'approccio crea **UTXO non spendibili che restano nel UTXO set** per sempre, gonfiandolo inutilmente. `OP_RETURN` è riconosciuto dai nodi come *provably unspendable*: l'output associato viene **escluso dal UTXO set**, quindi non pesa sulle prestazioni della rete. È la ragione per cui Bitcoin Core lo ha standardizzato.

### Leggere transazioni reali

Si possono scaricare transazioni vere dalla blockchain di produzione e farle digerire al parser:

1. Prendere un TXID noto
2. Chiedere l'hex grezzo con `https://blockchain.info/rawtx/<txid>?format=hex`
3. Passarlo a `bitcoinj` con `Transaction.read()`
4. Stampare con `printTxInfo`

```java
public static void readRawTx() throws InterruptedException {

    // String rawHex = "020000000180b98c54dbab5106d5a1449f4e5fdb9146deca1d48e93d66
    // 6c5d9290b7c37a3f010000006b483045022100f0e32ceb205a5056694611afcffe4c1f0e63e9c5738
    // 2607045ff2c3d9b5b7b3f0220111f0323e56d7462a9299833166569f1a68e1f5090b49bea64f541c4
    // 94109c6c012102d0648f06a31d47112f1ff7848c85ce54b772c513bc3337c98f081c19d3dca260fff
    // fffff02006d7c4d000000001976a91474d463a046e3175142464740db692fa0762a93e88accad5e5
    // f1b50000001976a914c98fc6bd9c2fd88533f28e6797cfa2a0a0e18ecf88ac00000000";

    // first segwit
    // dfcec48bb8491856c353306ab5febeb7e99e4d783eedf3de98f3ee0812b92bad
    // String rawHex = "01000000000101740e5e391018c5e9dc79f324f9607c9c46d21b02f66da
    // baa870b4add871d6379f01000000171600148d7a0a3461e3891723e5fdf8129caa0075060cffffff
    // fff01fcf60200000000001600148d7a0a3461e3891723e5fdf8129caa0075060cff02483045022100
    // 88025cffdaf69d310c6fed11832edd9c19b6a912c132262701ad0e6133227d9202207d73bbf777abd
    // 2aeae995d684e6bb1a048c5ac722e16de48bdd35643df7decf001210283409659355b6d1cc3c32dec
    // d5d561abaac86c37a353b52895a5e6c196d6f44800000000";

    // opreturn
    // d84f8cf06829c7202038731e5444411adc63a6d4cbf8d4361b86698abad3a68a
    String rawHex = "010000000178ded99d5bd03110a4e43d2cd7cddb3032af3e362d12ed0b8d"
        + "35cf811baf00255600000004948304502210fc323c40c6eb030c405bbacb478e6848b115c2bdbc5f7"
        + "8b275072ccecccacaf8a02207102afeb0a16c2caf7dd07a06d642d1ee0286ebe5f7c4d7092c78af4b0"
        + "4a44e101ffffffff02e80300000000000001976a9140910f9bbafabf5f653080ba23487d80a1dca614"
        + "388ac00000000000000000a6a084557204369616Ff2100000000";

    byte[] ba = hexStringToByteArray(rawHex);
    ByteBuffer bf = ByteBuffer.wrap(ba);
    Transaction tx = Transaction.read(bf);
    System.out.println("Tx ID: " + tx.getTxId());
    System.out.println("Inputs: " + tx.getInputs().size());
    System.out.println("Inputs: " + tx.getOutputs().size());
    printTxInfo(tx);
}
```

| Caso | TXID | Cosa mostra |
|---|---|---|
| **Legacy** (quello attivo nell'esempio iniziale) | — | Struttura classica: input con `scriptSig` pieno, nessun witness, un paio di output P2PKH |
| **SegWit** (primo esempio SegWit del docente) | `dfcec48b…bad` | Marker `0x00` + flag `0x01` dopo la version, `scriptSig` vuoto, firma spostata nel witness alla fine |
| **OP_RETURN** | `d84f8cf0…68a` | Uno degli output è un `OP_RETURN` con payload ASCII decodificabile |

> [!example] Workflow di verifica
>
> 1. Scommentare uno dei tre rawHex nel codice
> 2. Eseguire `readRawTx()` e leggere l'output stampato
> 3. Aprire nel browser `blockchain.com/explorer/assets/btc/decode-transaction`
> 4. Incollare lo stesso rawHex e confrontare i campi: version, input count, output count, TXID, tipo di script per ogni output
> 5. Se il codice è corretto, i due output coincidono campo per campo

## Script Classification e blk.dat

Facciamo un salto di livello: invece di guardare transazioni **una alla volta**, scriviamo un **parser dell'intera blockchain** che legge i file `blk*.dat` in cui Bitcoin Core salva i blocchi sul disco e produce statistiche aggregate (numero di transazioni, coinbase, witness, distribuzione dei tipi di script, indirizzi non decodificabili).

Prima si completa il parser di script costruendo le utility che **classificano** un output in una delle categorie standard e che da uno `scriptPubKey` **ricavano l'indirizzo** nel formato appropriato. Poi si applica il parser all'intera blockchain usando `BlockFileLoader` di bitcoinj.

```java
public static void readRawTxAndDecode(String rawHexTx) {
    byte[] ba = hexStringToByteArray(rawHexTx);
    ByteBuffer bf = ByteBuffer.wrap(ba);
    Transaction tx = Transaction.read(bf);

    for (TransactionInput in : tx.getInputs()) {
        byte[] inScript = in.getScriptBytes();
        System.out.println("INPUT script hex "     + bytesToHex(inScript));
        System.out.println("INPUT script OPcodes " + bytesToOpcode(inScript));
    }

    for (TransactionOutput out : tx.getOutputs()) {
        byte[] outScript = out.getScriptBytes();
        System.out.println("OUTPUT script hex "     + bytesToHex(outScript));
        System.out.println("OUTPUT script OPcodes " + bytesToOpcode(outScript));
        System.out.println("OUTPUT script Type "    + ScriptParser.typeFromOut(outScript));
        String outAddr = ScriptParser.addrFromOut(outScript);
        if (outAddr == null) outAddr = "#UNKNOWN#";
        System.out.println("OUTPUT script address " + outAddr);
    }
}
```

### `ScriptTypeCustom` — la tassonomia dei tipi di script

Per rendere il risultato del parser manipolabile si definisce una classe con costanti numeriche:

```java
public class ScriptTypeCustom {
    // type of script used 1=P2PK 2=P2PKH 3=P2SH 4=P2MS 5=other
    public static final int UNKNOWN = 0;
    public static final int P2PK    = 1;
    public static final int P2PKH   = 2;
    public static final int P2SH    = 3;
    public static final int RETURN  = 4;
    public static final int EMPTY   = 5;
    public static final int P2WPKH  = 6;
    public static final int P2WSH   = 7;
    public static final int SUPPORTEDSCRIPTTYPES = 8;

    // multisig example: txhash da738e29f64e90ae46dcc3e6b4154041d6324abbe7919e722d486a4a3148b7dc

    public static String typeName(int code) {
        switch (code) {
            case UNKNOWN: return "UNKNOWN";
            case P2PK:    return "P2PK";
            case P2PKH:   return "P2PKH";
            case P2SH:    return "P2SH";
            case RETURN:  return "PROVABLY UNSPENDABLE";
            case EMPTY:   return "ANYONE CAN SPEND";
            case P2WPKH:  return "P2WPKH";
            case P2WSH:   return "P2WSH";
            default:      return "ERROR - UNRECOGNIZED SCRIPT CODE";
        }
    }
}
```

- **`RETURN` → "PROVABLY UNSPENDABLE"**: un output con `OP_RETURN` non è mai spendibile, il nodo lo sa a priori e lo esclude dal UTXO set.
- **`EMPTY` → "ANYONE CAN SPEND"**: uno script vuoto valuta banalmente a `true`, quindi il primo chiunque può creare una transazione che lo spende. In pratica è un errore, ma esiste qualche transazione con output simili nei primi blocchi della blockchain.

### `ScriptParser.typeFromOut` — classificare un output per pattern matching

Ogni tipo di script ha una **forma canonica** in termini di opcode; basta verificare se lo `scriptPubKey` ha esattamente quella forma.

```java
public class ScriptParser {
    private static final int OP_DUP           = 118;
    private static final int OP_HASH160       = 169;
    private static final int OP_EQUALVERIFY   = 136;
    private static final int OP_CHECKSIG      = 172;
    private static final int OP_CHECKSIGVERIFY = 173;
    private static final int OP_EQUAL         = 135;
    private static final int OP_RETURN        = 106;
    // between 1 and 75 it is a relevant op_push_data@ i.e. number of bytes to be pushed to the stack
    private static final int OP_PUSHDATA20 = 20;
    private static final int OP_PUSHDATA32 = 32;
    private static final int OP_PUSHDATA33 = 33;
    private static final int OP_PUSHDATA65 = 65;
    private static final int OP_0 = 0;

    private static boolean isOpCode(byte b, int opcode) {
        return Utilities.readUnsignedByte(b) == opcode;
    }

    public static int typeFromOut(byte[] script) {
        if ((script == null) || (script.length < 1))
            return ScriptTypeCustom.EMPTY;
        // no empty script
        if (isOpCode(script[0], OP_RETURN))
            return ScriptTypeCustom.RETURN;
        else if (isOpCode(script[0], OP_DUP) && (script.length >= 23)) {
            // P2PKH
            if (isOpCode(script[1], OP_HASH160) && isOpCode(script[2], OP_PUSHDATA20))
                return ScriptTypeCustom.P2PKH;
            else return ScriptTypeCustom.UNKNOWN;
        } else if (isOpCode(script[0], OP_PUSHDATA65) && (script.length >= 66)) {
            return ScriptTypeCustom.P2PK;
        } else if ((script.length == 66) &&
                   ((isOpCode(script[script.length - 1], OP_CHECKSIG))
                 || (isOpCode(script[script.length - 1], OP_CHECKSIGVERIFY)))) {
            // old broken P2PK
            return ScriptTypeCustom.P2PK;
        } else if (isOpCode(script[0], OP_HASH160)) {
            if ((script.length >= 23) && isOpCode(script[1], OP_PUSHDATA20)
                && (isOpCode(script[script.length - 1], OP_EQUAL)
                 || isOpCode(script[script.length - 1], OP_EQUALVERIFY))) {
                // P2SH 160
                return ScriptTypeCustom.P2SH;
            } else return ScriptTypeCustom.UNKNOWN;
        } else if (isOpCode(script[0], OP_0)) {
            // support for native segwit
            if (isOpCode(script[1], OP_PUSHDATA20) && (script.length == 22)) {
                // P2WPKH
                return ScriptTypeCustom.P2WPKH;
            } else if (isOpCode(script[1], OP_PUSHDATA32) && (script.length == 34)) {
                // P2WSH
                return ScriptTypeCustom.P2WSH;
            } else return ScriptTypeCustom.UNKNOWN;
        } else return ScriptTypeCustom.UNKNOWN;
    }
}
```

| Tipo | Lunghezza | Pattern |
|---|---|---|
| **P2PKH** | 25 byte | `OP_DUP OP_HASH160 <20B pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG` |
| **P2PK** (moderno) | 67 byte | `<65B pubKey uncompressed> OP_CHECKSIG` |
| **P2PK** (rotto/vecchio) | 66 byte | forma storica mal-formattata che finisce con `OP_CHECKSIG(VERIFY)` |
| **P2SH** | 23 byte | `OP_HASH160 <20B scriptHash> OP_EQUAL` |
| **P2WPKH** | 22 byte | `OP_0 <20B pubKeyHash>` |
| **P2WSH** | 34 byte | `OP_0 <32B scriptHash>` |
| **RETURN** | variabile | inizia con `OP_RETURN` |
| **EMPTY** | 0 byte | script vuoto |

> [!warning] Il caso "old broken P2PK"
>
> Nei primissimi blocchi di Bitcoin alcuni script P2PK hanno una forma non perfettamente canonica (mancano byte di push espliciti, o usano `OP_CHECKSIGVERIFY` invece di `OP_CHECKSIG`). Il parser gestisce questo caso di recupero per evitare di classificarli come `UNKNOWN`. È il tipo di dettaglio storico che emerge solo quando si analizza la blockchain dall'inizio.

> [!example] Esercizio — aggiungere Taproot
>
> **P2TR** (Taproot) ha forma:
>
> ```
> OP_1 <32B x-only pubKey>
> ```
>
> ovvero la witness version `0x51` (`OP_1`) seguita da un push di 32 byte. Basta aggiungere una costante `P2TR = 8` in `ScriptTypeCustom`, aumentare `SUPPORTEDSCRIPTTYPES`, e nel parser aggiungere un ramo analogo a `OP_0`:
>
> ```java
> } else if (isOpCode(script[0], OP_1)) {
>     if (isOpCode(script[1], OP_PUSHDATA32) && (script.length == 34))
>         return ScriptTypeCustom.P2TR;
>     else return ScriptTypeCustom.UNKNOWN;
> }
> ```
>
> Rimane da aggiungere `typeName`, l'encoding Bech32m (diverso dal Bech32 di SegWit v0!) in `addrFromOut`, e il supporto al tipo in tutte le statistiche. Vedi [learnmeabitcoin.com/technical/script/p2tr](https://learnmeabitcoin.com/technical/script/p2tr/) per il formato completo.

### `ScriptParser.addrFromOut` — ricavare l'indirizzo dallo script

Una volta classificato il tipo, estrarre l'indirizzo significa applicare l'encoding giusto all'hash giusto.

```java
public static String addrFromOut(byte[] script) {
    if ((script == null) || (script.length < 1)) return null;
    // no empty script
    if (isOpCode(script[0], OP_RETURN))
        return null;
    else if (isOpCode(script[0], OP_DUP) && (script.length >= 23)) {
        // it is P2PKH
        if (isOpCode(script[1], OP_HASH160) && isOpCode(script[2], OP_PUSHDATA20)) {
            byte[] res = new byte[20];
            System.arraycopy(script, 3, res, 0, 20);
            return getAddressFromPubHash(res);
        } else return null;
    } else if (isOpCode(script[0], OP_PUSHDATA65) && (script.length >= 66)) {
        // it is P2PK
        byte[] res = new byte[65];
        System.arraycopy(script, 1, res, 0, 65);
        return getAddressFromPubKey(res);
    } else if ((script.length == 66) &&
               ((isOpCode(script[script.length - 1], OP_CHECKSIG))
             || (isOpCode(script[script.length - 1], OP_CHECKSIGVERIFY)))) {
        // old broken version of P2PK without initial length byte
        byte[] res = new byte[65];
        System.arraycopy(script, 0, res, 0, 65);
        return getAddressFromPubKey(res);
    } else if (isOpCode(script[0], OP_HASH160)) {
        if ((script.length >= 23) && isOpCode(script[1], OP_PUSHDATA20)
            && (isOpCode(script[script.length - 1], OP_EQUAL)
             || isOpCode(script[script.length - 1], OP_EQUALVERIFY))) {
            // it is P2SH 160
            byte[] res = new byte[20];
            System.arraycopy(script, 2, res, 0, 20);
            return getAddressFromScriptHash(res);
        } else return null;
    } else if (isOpCode(script[0], OP_0)) {
        // support for native segwit
        if (isOpCode(script[1], OP_PUSHDATA20) && (script.length == 22)) {
            // P2WPKH
            byte[] res = new byte[20];
            System.arraycopy(script, 2, res, 0, 20);
            return SegwitAddress.fromHash(MainNetParams.get(), res).toBech32();
        } else if (isOpCode(script[1], OP_PUSHDATA32) && (script.length == 34)) {
            // P2WSH
            byte[] res = new byte[32];
            System.arraycopy(script, 2, res, 0, 32);
            return SegwitAddress.fromHash(MainNetParams.get(), res).toBech32();
        } else return null;
    } else return null;
}
```

```java
// PRE: b is long 20
public static String getAddressFromPubHash(byte[] b) {
    // add version "00"
    byte[] version = { 0 };
    // base58check encoding
    return Base58.encodeChecked(version[0], b);
}

// PRE: b is long 65
public static String getAddressFromPubKey(byte[] b) {
    // get hash160 from pubkey
    // perform sha256
    // perform ripemd160
    // encode hash160
    return getAddressFromPubHash(sha256Ghash160(b));
}

// PRE: b is long 20
public static String getAddressFromScriptHash(byte[] b) {
    // add version "05"
    byte[] version = { 5 };
    // base58check encoding
    return Base58.encodeChecked(version[0], b);
}
```

> [!tip] I due encoding
>
> - **Base58Check** per gli indirizzi legacy (P2PK, P2PKH, P2SH): version byte + payload + checksum (doppio SHA-256, primi 4 byte), il tutto codificato in Base58 (niente `0`, `O`, `I`, `l` per evitare confusione visiva)
> - **Bech32** per SegWit nativo (P2WPKH, P2WSH): include il witness program, una HRP (`bc` per mainnet) e un checksum con proprietà di error-correction molto migliori
>
> I version byte per gli indirizzi Base58Check mainnet: **`0x00`** per P2PK/P2PKH (prefisso `1`), **`0x05`** per P2SH (prefisso `3`).

### Bitcoin Core — i file blk.dat

> [!definition] blk*.dat
>
> Bitcoin Core, una volta sincronizzato, **non** tiene i blocchi in un database relazionale: li memorizza in una sequenza di file binari denominati `blk00000.dat`, `blk00001.dat`, ecc., ciascuno grande circa 128 MB, contenuti tipicamente in `~/.bitcoin/blocks/`. Ogni file contiene una serie di blocchi concatenati, ciascuno preceduto da un *magic number* (`0xF9BEB4D9` per mainnet) e dalla lunghezza del blocco. I blocchi **non sono necessariamente in ordine di altezza** — vengono scritti nell'ordine in cui arrivano durante la sincronizzazione, che in presenza di riorganizzazioni può non coincidere con quello della catena canonica.
>
> Riferimento: [learnmeabitcoin.com/technical/block/blkdat](https://learnmeabitcoin.com/technical/block/blkdat/)

Perché parsare i blk.dat invece di usare la JSON-RPC di Bitcoin Core? Perché è **drasticamente più veloce**: non c'è overhead di IPC né di serializzazione JSON, si legge direttamente il binario che il nodo stesso ha scritto. Per analisi di grandi quantità di blocchi è l'unico approccio praticabile.

### `BCParser` — analizzare l'intera blockchain

Costruiamo una classe `BCParser` che scorre tutti i file blk.dat e raccoglie statistiche.

```java
public class BCParser {

    // Location of block files
    String chaindataFolder;
    int DEBUGtotalTxs;
    int DEBUGcoinbaseCounter;
    int DEBUGwitnessTxs;
    int DEBUGnullAddresses;
    int[] DEBUGscriptTypes;

    public BCParser(String f) {
        chaindataFolder = f;
        DEBUGtotalTxs = 0;
        DEBUGcoinbaseCounter = 0;
        DEBUGwitnessTxs = 0;
        DEBUGnullAddresses = 0;
        DEBUGscriptTypes = new int[ScriptTypeCustom.SUPPORTEDSCRIPTTYPES];
        for (int i = 0; i < DEBUGscriptTypes.length; i++)
            DEBUGscriptTypes[i] = 0;
    }

    // The method returns a list of files in a directory according to a certain
    // pattern (block files have name blkNNNNN.dat)
    public static List<File> buildList(String PREFIX) {
        List<File> list = new LinkedList<File>();
        for (int i = 0; true; i++) {
            File file = new File(PREFIX + String.format(Locale.US, "blk%05d.dat", i));
            if (!file.exists()) break;
            list.add(file);
        }
        return list;
    }
}
```

La `buildList` costruisce la lista dei file blk.dat scandendo ordinatamente `blk00000.dat`, `blk00001.dat`, ... finché ne trova uno mancante. Questa lista viene passata al `BlockFileLoader` di bitcoinj.

```java
public void parseNoUtxo(File out, int n) throws IOException {
    NetworkParameters np = MainNetParams.get();
    // Creates a BlockFileLoader object by passing a list of .dat files.
    BlockFileLoader loader = new BlockFileLoader(np, buildList(chaindataFolder));
    BufferedWriter bw = new BufferedWriter(new FileWriter(out));

    int blockCounter = 0;
    // NOTE: blocks are not ordered, so this is NOT the same as block height!!
    for (Block block : loader) {
        if (blockCounter >= n) break;
        if (blockCounter % 20000 == 0) {
            System.out.println("Analysed " + blockCounter + " NOT ORDERED blocks.");
            System.out.println(blockCounter + " - " + block.getHashAsString());
        }
        parseBlockExact(block, bw);
        blockCounter++;
    } // End of iteration over blocks
    bw.close();

    System.out.println("TotalTxs " + DEBUGtotalTxs
        + " , of which coinbases are " + DEBUGcoinbaseCounter
        + " and " + DEBUGwitnessTxs + " are witness transactions.");
    System.out.println("Scripts found :");
    int ttemp = 0;
    for (int i = 0; i < DEBUGscriptTypes.length; i++) {
        System.out.println(DEBUGscriptTypes[i] + " " + ScriptTypeCustom.typeName(i));
        ttemp += DEBUGscriptTypes[i];
    }
    System.out.println("Total : " + ttemp + " (" + DEBUGnullAddresses + " null addresses).");
}
```

> [!warning] I blocchi non sono ordinati
>
> Il commento nel codice è importante: `BlockFileLoader` restituisce i blocchi **nell'ordine in cui sono stati scritti sul disco**, che non coincide con l'altezza. Il 20000-esimo blocco processato **non è il blocco 20000 della catena**. Se serve l'ordine per altezza bisogna ricostruirlo a parte, usando i `prevBlockHash` per fare il chaining.

#### `parseBlockExact` — processare un singolo blocco

```java
/**
 * Outputs script info for the given block as:
 * one tx per line
 * generalInfo ':' InputsInfo (empty if coinbase) ':' OutputsInfo
 * generalInfo := timeStamp',' blockHash',' txHash',' isCoinbase',' txSizeEstimate
 */
public void parseBlockExact(Block block, BufferedWriter bw) throws IOException {
    boolean isCoinbase;
    boolean first;
    StringBuilder line;
    for (Transaction tx : block.getTransactions()) {
        DEBUGtotalTxs++;
        // write tx general infos:
        // timestamp, blockHash, txHash, isCoinbase, estimatedSize, hasWitness
        line = new StringBuilder();
        line.append(block.time());
        line.append(",");
        line.append(block.getHashAsString());
        line.append(",");
        line.append(tx.getTxId().toString());
        line.append(",");
        if (tx.isCoinBase()) {
            isCoinbase = true;
            line.append("1");
        } else {
            isCoinbase = false;
            line.append("0");
        }
        line.append(",");
        line.append(tx.getVsize());
        line.append(",");
        if (tx.hasWitnesses()) {
            DEBUGwitnessTxs++;
            line.append("1");
        } else {
            line.append("0");
        }
        line.append(":");
        if (isCoinbase) {
            DEBUGcoinbaseCounter++;
        } else {
            // not coinbase so there is at least one input
            // save inputs in the format
            // |prevTx_Id,prevTxPos|*
            first = true;
            for (TransactionInput ii : tx.getInputs()) {
                if (first) first = false;
                else line.append(";");
                //line.append(Utilities.byteArrayToHexString(ii.getScriptBytes()));
                line.append(ii.getOutpoint().hash().toString());
                line.append(",");
                line.append(ii.getOutpoint().index());
            }
        }
        line.append(":");
        // save outputs in the format
        // |addr,amount,scriptType|[:addr,amount,scriptType]*
        // there is always at least one output
        first = true;
        for (TransactionOutput oo : tx.getOutputs()) {
            if (first) first = false;
            else line.append(";");
            byte[] outScript = oo.getScriptBytes();
            String outAddr = ScriptParser.addrFromOut(outScript);
            int outType = ScriptParser.typeFromOut(outScript);
            DEBUGscriptTypes[outType]++;
            if (outAddr == null) {
                // writes '#num' as address if not decodable
                outAddr = "#" + DEBUGnullAddresses;
                DEBUGnullAddresses++;
            }
            line.append(outAddr);
            line.append(",");
            line.append(oo.getValue().getValue());
            line.append(",");
            line.append(outType);
        }
        bw.write(line.toString());
        bw.newLine();
    }
}
```

Ogni riga rappresenta una transazione e ha la forma:
```
timestamp,blockHash,txHash,isCoinbase,vsize,hasWitness : inputs : outputs
```
dove:
- **`inputs`** (vuoto se coinbase): `prevTxHash,prevTxPos;prevTxHash,prevTxPos;...`
- **`outputs`**: `addr,amount,scriptType;addr,amount,scriptType;...`

Gli indirizzi non decodificabili vengono rimpiazzati con un progressivo `#0`, `#1`, ... in modo da avere comunque un identificatore univoco per riga.

![Pipeline di `BCParser`: dai file blk.dat al CSV-like con statistiche aggregate sulla blockchain intera.](images/mermaid-lezione-13-lab-script-classification-e-blk-dat-01.png)

> [!tip] Il limite: niente UTXO set
>
> Il parser scritto in questo laboratorio si chiama `parseNoUtxo` per una ragione: non ricostruisce il set degli output non spesi. Per farlo bisognerebbe, per ogni input, cercare l'output corrispondente (prevTxHash + prevTxPos) e rimuoverlo dalla collezione degli UTXO vivi. È fattibile ma richiede molto più lavoro e memoria.

## Anonimato e Deanonimizzazione

In questa sezione si affrontano due temi correlati: il completamento della pipeline di parsing del `blk.dat` con la gestione degli UTXO, e l'analisi dell'anonimato in Bitcoin. Il filo conduttore è che la blockchain è pubblica e persistente: tutto ciò che avviene su di essa è osservabile, e l'unica protezione offerta nativamente è la **pseudonimia**, non l'anonimato vero.

### Completamento della pipeline: dal blk.dat al CSV con UTXO

Nelle lezioni precedenti si era costruito un formato CSV custom per rappresentare le transazioni Bitcoin estratte dal `blk.dat`. Il formato aveva due problemi principali: i blocchi non erano ordinati per altezza, e le transazioni non contenevano informazioni dirette sugli UTXO (cioè, gli input referenziavano le transazioni precedenti per hash, non per valore). Il metodo `cleanExactNoUtxo` in Java risolve il primo problema in modo sequenziale: prima inferisce una mappa da block hash a block height (`inferBlockHeightMap`), poi sostituisce gli hash dei blocchi con le altezze numeriche (`replaceBlockHashes`), quindi ordina le transazioni per altezza del blocco (`sortPreservingTxOrder`), e infine sostituisce gli hash delle transazioni e degli indirizzi con ID numerici incrementali a partire da zero. Il risultato è un file ordinato con ID compatti, adatto a successive elaborazioni.

Il metodo `fillItUtxo` affronta invece il secondo problema: leggendo il CSV ordinato, mantiene in memoria una mappa `TreeMap<TxOutputIds, TxOutputCouple>` che tiene traccia degli output non ancora spesi. Per ogni input di ogni transazione, consulta questa struttura per recuperare il valore e l'indirizzo sorgente, aggiungendoli al record dell'input nel CSV. Quando un UTXO viene consumato, viene rimosso dalla mappa. Il codice gestisce anche casi limite come le transazioni coinbase (che non hanno input reali), le incoerenze nel dataset e i fee negativi.

> [!warning] Complessità e ordinamento
>
> Il metodo `fillItUtxo` funziona correttamente **solo** su un file già ordinato per block height. Senza ordinamento, gli UTXO verrebbero cercati prima di essere creati, causando errori di lookup sistematici. La separazione tra `cleanExactNoUtxo` e `fillItUtxo` riflette proprio questa dipendenza sequenziale.

### Anonimato in Bitcoin: pseudonimia e i suoi limiti

Bitcoin non è anonimo: è **pseudonimo**. In un sistema anonimo, le transazioni non sono riconducibili ad alcun attore. In Bitcoin, ogni transazione è firmata con la chiave privata dell'indirizzo mittente, e l'intera storia delle transazioni è pubblica e permanente nella blockchain. L'identità reale di chi controlla un indirizzo non è direttamente visibile, ma le sue azioni (movimenti di fondi, tempi, importi) sono completamente tracciate.

Un utente può generare un numero arbitrario di indirizzi diversi — è anzi pratica consigliata usarne uno nuovo per ogni transazione. Ma questo non rompe la pseudonimia: significa solo che la stessa persona reale controlla più pseudonimi. Le euristiche di clustering riescono spesso a raggruppare questi indirizzi ricondizionandoli allo stesso utente.

Un ulteriore punto di debolezza è che le transazioni vengono diffuse nella rete P2P principalmente dai loro creatori tramite **gossip**. Chi le crea le ha firmate, quindi conosce le chiavi private degli input: è il proprietario degli indirizzi. Questa osservazione è alla base degli attacchi di network listening.

### Attacchi di deanonimizzazione

Un attacco di deanonimizzazione mira a collegare le identità reali del mondo fisico con gli indirizzi pseudonimi della blockchain. Il processo si articola in tre stadi progressivi:

![Pipeline di deanonimizzazione: dalla blockchain al grafo delle identità reali.](images/mermaid-lezione-17-lab-bitcoin-anonimato-e-deanonimizzazione-01.png)

Il primo stadio è puramente passivo: si costruisce il **transaction graph** dalla blockchain pubblica, dove i nodi sono indirizzi e gli archi rappresentano flussi di fondi. Il secondo stadio applica **euristiche di clustering** per raggruppare indirizzi che probabilmente appartengono allo stesso utente, ottenendo un **users graph** dove i nodi sono cluster. Il terzo stadio arricchisce il users graph con **informazioni esterne** per etichettare i cluster con identità reali, producendo l'**identities graph**.

#### Clustering euristico

Le euristiche si basano sull'osservazione del comportamento reale degli utenti Bitcoin e sui vincoli tecnici del protocollo. Generano falsi positivi e falsi negativi. La prassi è preferire la riduzione dei falsi positivi a scapito di un aumento dei falsi negativi.

> [!definition] Common Inputs Heuristic (euristica degli input comuni)
>
> Tutti gli indirizzi usati come input in una stessa transazione appartengono allo stesso utente. La logica è che per firmare gli input di una transazione servono le chiavi private corrispondenti: solo chi le possiede tutte può costruire quella transazione. Quindi gli indirizzi di input condividono necessariamente lo stesso proprietario.

Graficamente, una transazione con input multipli `addr_1, addr_2, ..., addr_n` produce un arco tra tutti gli indirizzi nel users graph, che vengono riuniti nello stesso cluster. L'implementazione efficiente si riduce a trovare le **componenti connesse** del grafo degli input, ottenibile con una BFS in complessità lineare.

> [!definition] Change Address Heuristic (euristica dell'indirizzo di resto)
>
> Quando si spende un UTXO, il valore in eccesso rispetto all'importo inviato viene restituito al mittente su un nuovo indirizzo, detto *change address* (indirizzo di resto). L'euristica assume che tale indirizzo appartenga allo stesso utente degli indirizzi di input.

Identificare il change address non è banale: in una transazione con più output, quale è il destinatario e quale è il resto?

> [!tip] Criteri per identificare un change address (versione raffinata)
>
> L'indirizzo $c$ è un change address nella transazione $t$ se e solo se:
> - $t$ non è una transazione coinbase
> - $|\text{outputs}(t)| > 1$ (almeno due output: uno di destinazione, uno di resto)
> - $\text{inputs}(t) \cap \text{outputs}(t) = \emptyset$ (nessun "self-change" diretto)
> - Nessun altro indirizzo negli output di $t$ è già noto come change address o appartiene al cluster del mittente
> - È la **prima volta** che $c$ compare nella blockchain
> - Nessun altro indirizzo negli output soddisfa contemporaneamente queste condizioni (univocità)

La condizione di prima comparsa è particolarmente rilevante: un utente attento genera un indirizzo fresco per ogni resto, quindi un indirizzo mai visto prima è un forte indizio che si tratti di un change address.

#### Raccolta di informazioni esterne

Anche le euristiche più raffinate lavorano solo su dati on-chain. Per associare cluster a identità reali si ricorre a fonti esterne:

- **Timing analysis**: se due transazioni avvengono in rapida successione, possono essere collegate allo stesso utente o dispositivo.
- **Amount analysis**: importi molto precisi o ricorrenti possono rivelare pattern di utilizzo.
- **Log interni di servizi terzi**: exchange, wallet custodial e marketplace raccolgono dati KYC e indirizzi di consegna fisici. Se le autorità accedono a questi log, l'associazione indirizzo–identità è diretta.
- **Dust attack**: l'attaccante invia una quantità minuscola di BTC (*dust*) a un indirizzo bersaglio. Se il wallet della vittima usa automaticamente quel UTXO come input in una transazione futura, quell'indirizzo viene collegato tramite la common inputs heuristic ad altri indirizzi dello stesso utente.

Un caso emblematico di informazione esterna è il tweet di WikiLeaks del 14 giugno 2011 che pubblicava esplicitamente il proprio indirizzo di donazione Bitcoin.

#### Network listening

Il network listening è una tecnica che mira a correlare un indirizzo Bitcoin con l'indirizzo IP del suo proprietario, sfruttando le proprietà del protocollo di diffusione delle transazioni.

Le assunzioni di base sono due: il primo nodo a diffondere una nuova transazione nella rete è con alta probabilità il suo creatore, e il creatore, avendo firmato la transazione, conosce le chiavi private degli input e quindi è il proprietario degli indirizzi corrispondenti.

L'attaccante inserisce nella rete P2P un gran numero di **nodi ascoltatori** sotto il proprio controllo, con connettività elevata e connessioni veloci. Grazie all'alta connettività, questi nodi ricevono le transazioni appena diffuse quasi in contemporanea con i vicini del creatore. Triangolando i tempi di ricezione tra tutti i nodi ascoltatori, si stima quale nodo della rete ha originato la transazione. L'IP del nodo originante viene quindi associato all'indirizzo Bitcoin degli input.

> [!warning] Limiti del network listening
>
> L'IP di un nodo non equivale sempre all'identità del proprietario: NAT, VPN, Tor e proxy possono nasconderlo. Per questo l'attaccante può raffinare la stima combinando IP con l'insieme degli *entry node* usati dalla vittima. Inoltre, solo i **full node** sono direttamente targetizzabili, poiché i light client non propagano le transazioni direttamente.

#### Topology discovery

Il network listening è spesso accoppiato con la **scoperta della topologia** della rete P2P. Conoscere la topologia aumenta la precisione della triangolazione, perché permette di modellare accuratamente il percorso di propagazione del gossip. Poiché Bitcoin non ha un overlay strutturato, l'unico modo per conoscere la topologia è chiedere direttamente ai nodi la loro lista di vicini. Questo processo può **corrompere le liste di connessione** degli altri nodi (pollution attack) e può causare effetti simili a un DoS sulla rete.

### Dataset: Users Graph 2013 e caso Wikileaks

Come caso di studio pratico, il laboratorio utilizza un sottoinsieme della blockchain del 2013 relativo a WikiLeaks: i blocchi dalla height 130863 alla 131006 (144 blocchi), contenenti 6094 transazioni che coinvolgono 8129 indirizzi. L'indirizzo di donazione di WikiLeaks (`1HB5XMLmzFVj8ALj6mfBsbifRoD4miY36v`) è l'anchor noto nel dataset. Il Users Graph 2013 dell'intera blockchain di quell'anno, una volta costruito e labelizzato, mostra cluster identificabili con servizi noti come Mt. Gox, Silk Road, BTC-e, Bitstamp e altri exchange o marketplace, evidenziando come la deanonimizzazione pratica fosse già possibile a quell'epoca.

> [!abstract] Assignment del laboratorio
>
> Costruire il **users graph** come mappa indirizzo → cluster ID applicando la **common inputs heuristic** al dataset Wikileaks sopra descritto. Il tip suggerito è di ridurre il problema al calcolo delle **componenti connesse** del grafo degli input, risolvibile con una BFS in complessità lineare $O(V + E)$.

### Tracciamento dei furti: taint analysis

La natura pubblica e immutabile della blockchain può essere usata anche in senso difensivo. Quando un furto di Bitcoin viene reso pubblico, l'indirizzo del ladro diventa noto a tutta la community. Gli utenti onesti possono tracciare i movimenti dei fondi rubati e applicare **blacklisting** sugli indirizzi del ladro.

> [!definition] Taint Analysis (analisi della contaminazione)
>
> Il **taint value** dell'indirizzo $A$ rispetto all'indirizzo $B$ è la percentuale dei fondi attualmente in possesso di $A$ che possono essere fatti risalire a $B$. Formalmente misura la dipendenza economica tra due indirizzi lungo la catena delle transazioni.

La taint analysis è uno strumento di base per seguire fondi rubati ma non tiene conto della *proprietà*: sa che i fondi sono passati per un certo indirizzo, ma non chi lo controlla. Due casi storici illustrano l'applicazione:

- **Furto allinvain** (13/06/2011, 25.001 BTC): l'analisi del transaction graph mostrò i fondi convergere verso il servizio MyBitcoin attraverso una serie di transazioni intermedie.
- **Ransomware TorrentLocker 2 (CryptoWall 2)** (15/09/2014, target: PA italiana): il malware richiedeva riscatti in Bitcoin. Tracciando gli indirizzi delle vittime note fu possibile seguire parte dei fondi raccolti e identificare gli exchange usati per il cashout.

### Contromisure per la privacy

#### CoinJoin e CoinShuffle

**CoinJoin** (2013) è la prima contromisura collaborativa: più utenti si accordano per unire i propri input in un'unica transazione grande, firmata collettivamente. L'accordo può avvenire tramite un server di rendezvous centralizzato o tramite consensus decentralizzato. Si possono costruire catene di transazioni CoinJoin per aumentare l'offuscamento. I limiti principali sono che l'anonimato all'interno di ogni transazione è limitato al numero di partecipanti, che esiste linkabilità interna (gli output sono ancora osservabili), che è vulnerabile a DoS da parte di partecipanti malevoli, e che nascondere gli IP dei partecipanti richiede strumenti aggiuntivi.

**CoinShuffle** (2014) migliora CoinJoin introducendo un protocollo di shuffling crittografico degli output che elimina la linkabilità interna: nemmeno il server di coordinamento può sapere quale output corrisponde a quale input.

#### Tecniche di offuscamento

Indipendentemente da CoinJoin, esistono tecniche individuali per spezzare il tracciamento della proprietà:

| Tecnica | Descrizione |
|---|---|
| **Split** | Divide un UTXO in molti output piccoli verso indirizzi diversi |
| **Aggregation** | Aggrega molti UTXO piccoli in uno grande per rompere il grafo |
| **Peeling chain** | Invia una quantità fissa ripetutamente, mantenendo un "residuo" che scorre verso un indirizzo fresco a ogni passo |
| **Binary tree** | Struttura ad albero di transazioni per distribuire i fondi su molteplici rami |

La **peeling chain** è particolarmente visibile nell'analisi on-chain: genera una sequenza lineare di transazioni dove ogni nodo ha un output di importo fisso (il pagamento) e uno di importo decrescente (il residuo). Si riconosce facilmente e non offre vera protezione a un analista esperto.

#### Mixer

I **mixer** (o tumbler) sono servizi che accettano Bitcoin da un utente e restituiscono la stessa quantità (meno fee) prelevandola dai fondi di altri utenti, spezzando così completamente la catena di proprietà on-chain. Non esiste link diretto tra l'indirizzo di invio e quello di ricezione.

> [!warning] Problemi dei mixer
>
> - Sono **terze parti centralizzate**: richiedono fiducia e introducono un single point of failure
> - Addebitano **commissioni**
> - Devono proteggere e **distruggere permanentemente** i log interni
> - Per importi grandi il processo è lento e insicuro (rischio di deanonimizzazione o furto da parte del mixer stesso)
> - Catene di mixer aumentano i costi e la probabilità di furto ad ogni hop
>
> Alternativa pratica: il **chain hopping**, ovvero spostare i fondi su una blockchain diversa (es. Monero) per poi tornare su Bitcoin con un indirizzo nuovo, sfruttando la migliore privacy nativa di quella chain.
