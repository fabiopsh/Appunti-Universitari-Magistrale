La **sicurezza** all'interno dello standard ZigBee si fonda su un'architettura rigorosa, progettata per fornire quattro servizi essenziali a ogni nodo: lo stabilimento delle chiavi (**key establishment**), il loro trasporto logico (**key transport**), la protezione crittografica dei frame dati (**frame protection**) e la gestione remota e sicura dei dispositivi (**device management**). Queste quattro colonne portanti forniscono i blocchi fondamentali su cui si regge ogni policy di sicurezza all'interno del protocollo.

## Scelte di Design per la Sicurezza

Per garantire la robustezza del sistema, ZigBee impone precise e vincolanti scelte architetturali. In primo luogo, vige la regola per cui ==il livello di rete che genera originariamente un frame è sempre il diretto responsabile della sua messa in sicurezza iniziale== (ad esempio, un comando nato a livello NWK deve rigorosamente utilizzare la NWK security prima di essere inoltrato).

Se l'obiettivo dell'infrastruttura è proteggersi in modo proattivo dal furto di servizio (_theft of service_), allora la protezione a livello NWK va applicata in modo tassativo a tutti i frame che transitano; l'unica eccezione concessa riguarda le delicate fasi di _join_ quando un nuovo dispositivo entra nella rete.

L'architettura incoraggia fortemente il riutilizzo pratico del materiale crittografico tra i vari livelli di uno stesso dispositivo, e consiglia l'uso di link-key per aggiungere un ulteriore strato di sicurezza che accompagni il dato per tutto il tragitto end-to-end (dalla sorgente esatta alla destinazione finale). Un'applicazione software di terze parti ha sempre la libertà di introdurre meccanismi crittografici aggiuntivi, ma la loro gestione ricadrà interamente sulle spalle dell'applicazione stessa, senza coinvolgere il protocollo.

> [!warning] Attenzione: Gestione delle Anomalie
> 
> Ogni _Application Profile_ sviluppato deve sempre includere procedure di emergenza per gestire gli errori. Le eccezioni o i fallimenti nei processi di _securing_ e _unsecuring_ dei pacchetti non vanno mai ignorati, perché spesso sono i primissimi sintomi di una grave perdita di sincronizzazione del materiale crittografico o denotano l'attività di un attacco hacker in corso. È di vitale importanza rilevare tempestivamente le perdite di sincronizzazione dei contatori o il loro _overflow_, le perdite di sincronizzazione delle chiavi stesse, e far scadere proattivamente le chiavi per forzarne un aggiornamento periodico.

## L'Architettura di Sicurezza ZigBee

All'interno dello strato ISO-OSI, ogni livello fa la sua parte. Il **Network Layer (NWK)** ha il preciso compito di garantire il trasporto sicuro dei propri frame. Sfruttando le chiavi crittografiche fornite dal livello superiore, il NWK provvede alla cifratura del messaggio (_encryption_), alla verifica della sua integrità e al controllo della cosiddetta _freshness_: un meccanismo per assicurarsi che il dato sia "fresco" (non un duplicato) così da rigettare i _replay attacks_. Va però ricordato che, per forza di cose, alcuni pacchetti operativi (come i primissimi messaggi di associazione) viaggiano in chiaro.

Salendo, l'**Application Support Sublayer (APS)** fa il lavoro sporco. Deve garantire il trasporto sicuro dei frame a livello APS, implementare materialmente tutti i protocolli matematici per lo stabilimento e il trasporto delle chiavi e offrire i servizi base per il _device management_. Sopra l'APS siede lo **ZigBee Device Object (ZDO)**, il vero amministratore della sicurezza: lo ZDO governa le policy del nodo, ordina le operazioni da svolgere ed emette le primitive con cui istruisce fisicamente l'APS a gestire le chiavi crittografiche.

> [!important] Focus: Ottenimento e Tipologia delle Chiavi a 128 bit
> 
> Un nodo può ottenere nuovo materiale crittografico per pre-installazione in fabbrica (pre-caricato nel firmware), tramite **Key transport** (una chiave inviata via radio da un nodo all'altro) o per **Key establishment**(un accordo crittografico tra due nodi per derivare un segreto comune).
> 
> Le chiavi utilizzate sono tutte a 128-bit e si dividono in tre famiglie:
> 
> - **Network key:** Condivisa da tutti i nodi di una rete. Ottenuta per trasporto o pre-installazione. Può essere di tipo _standard_ o _high-security_.
>     
> - **Link keys:** Segreti univoci condivisi tra _due soli_ dispositivi (ottenuti per trasporto, establishment o pre-installazione). Si dividono in _uniche_ o _globali_ (queste ultime usate come default per parlare con il Trust Center).
>     
> - **Master key:** Ottenuta per trasporto o pre-installazione, questa chiave non cifra i messaggi operativi, ma viene passata attraverso speciali funzioni matematiche monodirezionali (_one-way functions_) al solo scopo di derivare in modo sicuro nuove Link Key per l'infrastruttura.
>     

## Stabilimento delle Chiavi e Servizi APS

Quando due nodi (un _initiator_ e un _responder_) devono accordarsi senza scambiarsi chiavi in chiaro, l'APS avvia il protocollo **Symmetric-Key Key Establishment (SKKE)**. È un elegante protocollo di tipo _challenge-response_ diviso in quattro momenti:

1. **Trust Provisioning:** Ci si basa su informazioni fiduciarie preesistenti (la **Master Key**). Tale radice può essere pre-installata in fabbrica, spinta da un terzo dispositivo delegato, oppure generata da dati inseriti a mano dall'utente (come PIN o password).
    
2. **Scambio Dati Effimeri:** I nodi si sfidano inoltrandosi a vicenda stringhe effimere, tipicamente un numero casuale (_random number_).
    
3. **Derivazione della Chiave:** Sfruttando l'entropia del numero casuale e il segreto della chiave madre, i dispositivi calcolano internamente, tramite un algoritmo, l'identica Link Key.
    
4. **Conferma:** Prima di inviare dati sensibili, i nodi si scambiano un rapido messaggio di conferma incrociata per avere l'assoluta certezza di aver computato correttamente lo stesso valore.

## Il Ruolo Indispensabile del Trust Center

==In ogni singola rete sicura ZigBee deve esserci uno e un solo Trust Center==. È il pilastro fidato della topologia: a lui è demandata per intero l'operazione di distribuzione delle chiavi operative per amministrare centralmente sia la rete che le configurazioni delle applicazioni end-to-end.

> [!note] Contesto: Configurazione Gerarchica del Trust Center
> 
> Nelle installazioni _high-security_ (bancarie o industriali critiche), il Trust Center è solitamente un macchinario ad-hoc corazzato, pre-caricato in fabbrica con il suo indirizzo univoco e la Master Key di base. Nelle installazioni più domestiche o commerciali, in alternativa, questo arduo compito è semplicemente assorbito dal Coordinator della rete o assegnato, per delega esplicita, a uno specifico router.

Ma cosa accade a un nuovo device che esegue la procedura di unione (join) alla rete? Esso è obbligato a chiedere i permessi e ottenere le chiavi dal Trust Center tramite vari protocolli.

Nelle reti a bassa sicurezza (_low-security_), il Trust Center semplifica la procedura inviando subito la Master Key vitale su un trasporto temporaneamente non sicuro (_unsecured transport_). Se però il dispositivo nuovo arrivato ha già pre-caricata al suo interno la Master Key di sistema, i due nodi sfrutteranno immediatamente quel segreto noto per erigere una corazza (_secure communication link_) dentro la quale il Trust Center spingerà in sicurezza tutte le altre chiavi operative.

Per riassumere l'intero quadro tecnico, le architetture ZigBee poggiano saldamente i propri piedi sul protocollo IEEE 802.15.4 (per la trasmissione e gli strati bassi), affidando al proprio **Network Layer** i complessi processi di associazione e formazione topologica e demandando al ricco mondo dell'**Application Sublayer**, unito al Framework Applicativo e allo ZDO, le logiche che governano comportamento e sicurezza.

> [!summary] Glossario
> 
> - **Key Establishment (SKKE):** Meccanismo tramite cui due dispositivi ZigBee dialogano sfidandosi a colpi di numeri casuali (_challenge-response_) per derivare indipendentemente la stessa chiave di cifratura basandosi su un segreto comune condiviso a monte.
>     
> - **Trust Center:** Entità logica univoca presente su una rete ZigBee, considerata del tutto affidabile. Eroga chiavi crittografiche per consentire la sicurezza end-to-end e valida gli accessi.
>     
> - **Freshness:** Un attributo di sicurezza del Network Layer necessario ad attestare che un pacchetto dati è del tutto nuovo, proteggendo il nodo contro malintenzionati che tentano di rispedire comandi registrati in passato.
>     
> - **Master Key:** Chiave madre a 128 bit il cui unico ed esclusivo fine non è cifrare il traffico di tutti i giorni, ma fare da perno per calcolare crittograficamente la generazione di nuove chiavi di legame (_Link keys_).
>