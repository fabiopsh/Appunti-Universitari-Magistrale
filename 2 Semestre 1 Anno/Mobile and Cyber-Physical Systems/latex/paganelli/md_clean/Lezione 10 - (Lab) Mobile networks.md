
# Mobile Networks — Mobilità nelle Reti Cellulari

La mobilità nelle reti di telecomunicazione moderne si estende lungo un ampio spettro: dall'assenza totale di spostamento fino a scenari in cui un dispositivo attraversa reti di operatori diversi mantenendo attive le proprie sessioni. Questo capitolo analizza le architetture che rendono possibile tale mobilità — in particolare nelle reti 4G/5G — esaminando i meccanismi di registrazione, i due approcci di routing (indiretto e diretto) e le procedure di _handover_ tra stazioni base.

---

## Lo Spettro della Mobilità e la Home Network

Dal punto di vista infrastrutturale, la mobilità non è una proprietà binaria ma uno spettro continuo. A un estremo si trovano dispositivi completamente statici; procedendo si incontrano dispositivi che cambiano rete solo tra una sessione e l'altra, o che si muovono tra Access Point dello stesso operatore. L'estremo di maggiore interesse è l'**alta mobilità**: un dispositivo che cambia rete mantenendo attive le connessioni in corso.

Per gestire questo livello di mobilità è indispensabile il concetto di **home network**: una fonte autorevole e centralizzata che registra la posizione attuale del dispositivo e dalla quale le altre entità di rete possono ottenerla. Senza di essa non esiste modo affidabile di recapitare traffico a un nodo in movimento.

### Reti 4G/5G vs ISP/WiFi

Nelle reti cellulari **4G/5G** la home network corrisponde alla rete dell'operatore con cui l'utente ha sottoscritto il contratto (es. Verizon, Orange). Il database centrale che memorizza identità e servizi abilitati è l'**Home Subscriber Server (HSS)**. L'identità globale del dispositivo — inclusa la sua rete di appartenenza — è codificata nella **SIM card**.

![[Screenshot 2026-03-10 alle 14.37.18.png]]
*Fig. — Struttura della home network in un'architettura 4G/5G.*

Quando il dispositivo lascia la copertura del proprio operatore entra in una **visited network**, condizione nota come _roaming_. La rete visitata ha accordi commerciali con altre reti per garantire accesso ai dispositivi in transito.

![[Pasted image 20260313143711.png]]
*Fig. — Relazione tra home network e visited network in uno scenario di roaming.*

Le reti **ISP/WiFi** presentano un'architettura radicalmente diversa: manca una nozione globale di home. L'autenticazione avviene tramite server locali, le credenziali variano da rete a rete e la mobilità fluida è difficile da realizzare. Esistono eccezioni accademiche come _eduroam_ e architetture teoriche come **Mobile IP**, ma quest'ultima non ha mai raggiunto un'adozione commerciale significativa.

---

## Approcci alla Gestione della Mobilità

I progettisti di rete hanno valutato due filosofie principali per permettere a un nodo corrispondente di raggiungere un dispositivo mobile.

Il primo approccio affida la mobilità direttamente ai router, che annuncerebbero la posizione del nodo mobile attraverso i consueti protocolli di routing. Tecnicamente Internet potrebbe supportarlo tramite il _longest prefix match_, ma l'approccio è stato scartato per mancanza di scalabilità: propagare la posizione di miliardi di dispositivi mobili nelle tabelle di routing globali è impraticabile.

Il secondo approccio, quello effettivamente implementato, sposta la complessità ai margini della rete (_edge_), lasciando che siano i sistemi terminali a gestirla. Questo dà origine a due tecniche: il **routing indiretto** e il **routing diretto**.

---

## La Fase di Registrazione

Indipendentemente dalla tecnica di routing adottata, la home network deve sempre conoscere la posizione corrente del dispositivo. Questo avviene tramite la **registrazione**: il dispositivo si associa a un _mobility manager_ nella rete visitata, il quale comunica la posizione aggiornata all'HSS domestico. Al termine della procedura, il mobility manager della rete visitata è a conoscenza della presenza del dispositivo e l'HSS domestico conosce la sua posizione remota.

![[Pasted image 20260313143813.png]]
*Fig. — Procedura di registrazione tra visited network e home network.*

Durante le operazioni in roaming il dispositivo mantiene il proprio indirizzo permanente associato alla home network, ma ottiene temporaneamente un indirizzo IP nel range della rete visitata, tipicamente assegnato tramite NAT.

---

## Routing Indiretto e Routing Diretto

Nel **routing indiretto** — modalità standard per le reti 4G LTE e per Mobile IP — il nodo corrispondente invia il datagramma all'indirizzo permanente del dispositivo mobile. Il gateway della home network lo riceve, lo incapsula in un tunnel e lo inoltra al gateway della rete visitata, che decapsula il pacchetto, applica la traduzione NAT e lo consegna al dispositivo. Le risposte possono seguire il percorso inverso oppure essere inviate direttamente al corrispondente.

Perché questo meccanismo funzioni servono tre protocolli specifici:

1. **Protocollo di associazione** dispositivo–rete visitata: il dispositivo si associa alla rete visitata e si disassocia quando la lascia.
2. **Protocollo di registrazione** rete visitata–HSS domestico: la rete visitata comunica all'HSS la posizione del dispositivo.
3. **Protocollo di tunneling** tra i due gateway: il gateway domestico incapsula il datagramma originale; il gateway visitato lo decapsula, applica il NAT e lo consegna al dispositivo.

Questo schema genera il cosiddetto _triangle routing_: se corrispondente e dispositivo si trovano nella stessa rete, i dati compiono un percorso inutilmente lungo fino alla home network. Il vantaggio, però, è notevole: ogni cambio di rete visitata è completamente trasparente per il corrispondente — la nuova rete si registra presso l'HSS e il traffico viene reindirizzato nel nuovo tunnel senza azioni da parte del corrispondente.

> [!note] Continuità delle sessioni durante il cambio di rete
>
> Quando il dispositivo si sposta in una nuova rete visitata, possono andare persi alcuni datagrammi in transito. Tuttavia le sessioni TCP rimangono attive: dal punto di vista del corrispondente, la posizione del mobile è un dettaglio interno alla home network.

Nel **routing diretto** il corrispondente interroga l'HSS domestico per ottenere il _care-of-address_ del dispositivo nella rete visitata e invia i datagrammi direttamente a quell'indirizzo, eliminando le inefficienze del triangle routing. Tuttavia l'approccio non è trasparente per il corrispondente, che deve gestire esplicitamente la richiesta dell'indirizzo. Inoltre, se il dispositivo cambia rete durante una sessione attiva, il problema è più complesso: il corrispondente ha interrogato l'HSS **solo all'inizio della sessione** e non conosce il nuovo indirizzo; sono quindi necessari meccanismi aggiuntivi per aggiornare dinamicamente il flusso dati, a differenza del routing indiretto dove è sufficiente cambiare l'endpoint del tunnel.

---

## L'Architettura Pratica: Mobilità nelle Reti 4G

Quando un dispositivo entra in una rete 4G visitata, la gestione della mobilità si sviluppa attraverso quattro fasi distinte che coinvolgono progressivamente il piano di controllo, il piano dati e infine la transizione tra celle.

- Il punto di ingresso è l'**associazione alla Base Station (BS)**: il dispositivo si aggancia alla stazione radio base della rete visitata e si identifica tramite il proprio **IMSI** (_International Mobile Subscriber Identity_), che codifica sia l'identità del dispositivo sia la sua home network di appartenenza.

- A questo punto entra in gioco il **piano di controllo**: la BS coinvolge la **Mobility Management Entity (MME)** locale, che usa l'IMSI per contattare l'HSS domestico. L'HSS restituisce all'MME i parametri di autenticazione, crittografia e servizi abilitati per quell'utente, e al tempo stesso viene aggiornato sulla nuova posizione del dispositivo. È qui che avviene la registrazione vera e propria: da questo momento l'HSS domestico sa dove si trova l'utente.

- Una volta autenticato l'utente, l'MME configura il **piano dati** stabilendo i tunnel necessari a far fluire il traffico. Poiché si adotta routing indiretto, tutto il traffico deve transitare per la home network. Vengono creati due tunnel distinti, entrambi usando il protocollo **GTP** (_GPRS Tunneling Protocol_):
  - **Tunnel BS ↔ S-GW**: quando il dispositivo cambia Base Station, non occorre ricreare il tunnel — è sufficiente aggiornare l'indirizzo IP dell'endpoint sul lato BS.
  - **Tunnel S-GW ↔ P-GW** (home network): implementa il routing indiretto verso la home network.

- La quarta fase è l'**handover tra Base Station**, che si attiva quando il dispositivo si sposta e la qualità del segnale sulla BS corrente degrada. La procedura completa si articola in sette passi:

  1. La **BS sorgente** decide di avviare l'handover (per degrado del segnale o sovraccarico) e seleziona la _target BS_, inviandole una **Handover Request**.
  2. La **target BS** pre-alloca le risorse radio e risponde con un **Handover Request ACK** contenente le informazioni di configurazione per il dispositivo.
  3. La **BS sorgente** notifica il dispositivo del cambio imminente; da questo momento il dispositivo può già trasmettere tramite la nuova BS — l'handover sembra completato dal punto di vista del dispositivo.
  4. La **BS sorgente** smette di trasmettere al dispositivo e inizia a **forwardare** i datagrammi in arrivo verso la target BS (che li recapita al dispositivo via radio).
  5. La **target BS** informa l'**MME** di essere la nuova BS per il dispositivo.
  6. L'**MME** istruisce lo **S-GW** di aggiornare l'endpoint del tunnel dati alla nuova target BS. La BS sorgente riceve conferma e può liberare le proprie risorse radio.
  7. I datagrammi del dispositivo fluiscono ora attraverso il **nuovo tunnel** dalla target BS allo S-GW.

> [!tip] Perché la BS sorgente decide l'handover
>
> Sia la decisione di avviare l'handover sia la scelta della target BS spettano alla **BS sorgente** (non all'MME). L'MME viene coinvolto solo nella fase finale per aggiornare il piano dati. Questo è un punto frequente nelle domande d'esame.

![[Pasted image 20260313145859.png]]
*Fig. — Sequenza di messaggi durante un handover tra due Base Station in 4G.*

---

## Mobile IP e Impatto sui Protocolli di Trasporto

L'architettura **Mobile IP** (RFC 5944), standardizzata circa vent'anni fa, anticipava molti dei concetti oggi presenti nel 4G: il _home agent_ univa i ruoli dell'attuale HSS e P-GW, mentre il _foreign agent_ corrispondeva all'accoppiata MME/S-GW. La registrazione avveniva tramite estensioni ICMP. All'epoca WiFi per i dati e reti 2G/3G per la voce erano considerati sufficienti, e Mobile IP non ha mai raggiunto una diffusione commerciale rilevante.

Sul fronte dell'impatto sui protocolli superiori, in teoria il layer wireless dovrebbe essere trasparente: il modello _best-effort_ di IP rimane invariato e TCP/UDP girano regolarmente su reti mobili. In pratica le prestazioni degradano sensibilmente. Errori di bit sui link radio e interruzioni transitorie durante gli handover vengono interpretati da TCP come sintomi di congestione di rete, inducendolo a ridurre la _congestion window_ in modo ingiustificato. A questo si aggiungono la limitatezza di banda dei link wireless e i ritardi che penalizzano il traffico in tempo reale.

---

> [!question] Possibili domande d'esame
>
> - Qual è la differenza tra routing indiretto e routing diretto? Vantaggi e svantaggi di ciascuno.
> - Cos'è il triangle routing e quando si manifesta?
> - Quali tre protocolli sono necessari per implementare il routing indiretto?
> - Descrivi le quattro fasi della gestione della mobilità in 4G: quali entità sono coinvolte in ciascuna?
> - Qual è il ruolo di MME, HSS, S-GW e P-GW nell'architettura 4G?
> - Quali due tunnel vengono creati nella fase di configurazione del piano dati? Perché sono separati?
> - Come avviene un handover tra due Base Station? Descrivi i sette passi. Quale entità decide di avviarlo e quale sceglie la target BS?
> - Perché nel routing diretto un cambio di rete durante una sessione è più complesso che nel routing indiretto?
> - Perché le perdite radio degradano le prestazioni TCP nelle reti mobili?
