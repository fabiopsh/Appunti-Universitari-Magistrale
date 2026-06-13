# Lo Standard IEEE 802.15.4

Lo standard IEEE 802.15.4 definisce le specifiche del **physical layer** e del **MAC layer** per le **Low-Rate Wireless Personal Area Network** (*LR-WPAN*, reti personali senza fili a bassa velocità). L'obiettivo è fornire un protocollo radio standardizzato per dispositivi a risorse limitate — sensori, attuatori, nodi IoT — che richiedono bassi consumi energetici piuttosto che elevate velocità di trasmissione.

> [!definition] IEEE 802.15.4
>
> Specifica del physical layer e del MAC layer per reti LR-WPAN (*Low-Rate Wireless Personal Area Network*). Supporta comunicazioni a corto raggio, bassa velocità di trasmissione e coesistenza con IEEE 802.11 (Wi-Fi) e IEEE 802.15.1 (Bluetooth).

Una caratteristica progettuale importante è la coesistenza con altri standard wireless: il physical layer è disegnato per poter operare nello stesso ambiente fisico di IEEE 802.11 e IEEE 802.15.1 senza causare interferenze reciproche devastanti.

## Bande di Frequenza

Lo standard opera su tre bande di frequenza libere da licenza (*licence-free*):

| Banda | Regione | Data rate | Canali |
|---|---|---|---|
| 868–868.6 MHz | Europa | 20 kbps | 1 (canale 0) |
| 902–928 MHz | Nord America | 40 kbps | 10 (canali 1–10) |
| 2400–2483.5 MHz | Mondiale | 250 kbps | 16 (canali 11–26) |

La banda a 2.4 GHz è quella più diffusa perché disponibile a livello globale e garantisce la velocità di trasmissione più alta. La banda a 868 MHz — tipicamente utilizzata in Europa — è quella con il data rate più basso ma offre maggiore robustezza in ambienti con SNR basso.

> [!example] Esempio: banda 868 MHz
>
> - Frequenza centrale: 868.3 MHz
> - Data rate: 20 kbps
> - Modulazione: simboli binari
> - Un solo canale disponibile
> - Dimensione massima del pacchetto: 127 byte

---

## Physical Layer

Il **physical layer** di IEEE 802.15.4 eroga due categorie di servizi verso lo strato superiore: servizi dati e servizi di gestione.

### Servizi del Physical Layer

Il **Data Service** è responsabile della trasmissione e ricezione delle **PPDU** (*PHY Protocol Data Unit*) attraverso il mezzo fisico. Quando una trasmissione fallisce, il physical layer riporta all'upper layer il motivo del fallimento: il ricetrasmettitore potrebbe essere guasto, in modalità ricezione, oppure già impegnato in un'altra operazione.

Il **Management Service** comprende un insieme più ampio di funzionalità:

- Attivazione e disattivazione del ricetrasmettitore radio, per implementare politiche di risparmio energetico.
- **Energy Detection** (ED): misura del livello di energia sul canale.
- **Link Quality Indicator** (LQI): stima della qualità dei pacchetti ricevuti.
- **Channel Selection**: selezione del canale operativo.
- **Clear Channel Assessment** (CCA): verifica se il canale è libero prima di trasmettere.
- Configurazione della **PHY-PIB** (*PHY PAN Information Base*), la struttura dati che mantiene i parametri di configurazione del physical layer.

### Prestazioni del Physical Layer
![[Pasted image 20260408111308.png]]
*Fig. — Confronto di Bit Error Rate (BER) in funzione del SNR tra IEEE 802.15.4 (zona "More Robust"), Bluetooth e altri standard. Lo standard mostra eccellenti prestazioni in ambienti a basso SNR.*

Il grafico mostra che IEEE 802.15.4 mantiene un BER molto basso anche in condizioni di SNR negativo, dove altri standard (come Bluetooth) già soffrono di errori frequenti. Questa robustezza è fondamentale per i tipici ambienti IoT industriali o domestici, dove il canale radio è spesso disturbato.

### Energy Detection

L'**Energy Detection** (ED) è il meccanismo utilizzato per trovare un canale libero e per il *carrier sense*. Il physical layer misura la potenza del segnale sul canale su un intervallo di **8 simboli** e confronta il risultato con una soglia fissata a **10 dB sopra il livello di sensibilità** del ricevitore. Il risultato della rilevazione è restituito come un valore a un byte.

> [!definition] Energy Detection (ED)
>
> Stima del livello di energia media sul canale su una finestra di 8 simboli. Se l'energia supera la soglia (10 dB sopra la sensibilità), il canale è considerato occupato.

### Link Quality Indicator

Il **Link Quality Indicator** (LQI) misura la qualità dei pacchetti dati ricevuti da un nodo. Viene valutato ogni volta che si riceve un pacchetto e il suo valore viene propagato verso i layer di rete e applicazione, dove può essere impiegato nel routing multi-hop — ad esempio in ZigBee — per scegliere il percorso di qualità migliore.

> [!definition] Link Quality Indicator (LQI)
>
> Indicatore di qualità del collegamento radio stimato su ogni pacchetto ricevuto. Basato sull'ED, sul rapporto segnale/rumore o su una combinazione di entrambi. Deve avere almeno 8 livelli distinti.

### Clear Channel Assessment

Il **Clear Channel Assessment** (CCA) determina se il canale è occupato prima di trasmettere. Esistono tre modalità operative:

- **Modalità 1**: usa l'Energy Detection — se l'energia supera la soglia, il canale è occupato.
- **Modalità 2**: usa il *Carrier Sense* — il canale è occupato se il segnale rilevato ha le stesse caratteristiche del trasmettitore.
- **Modalità 3**: combinazione delle modalità 1 e 2 in AND o OR.

### Struttura della PPDU

Il frame del physical layer — la **PPDU** (*PHY Protocol Data Unit*) — è strutturato in tre sezioni principali:

![Struttura della PPDU IEEE 802.15.4](images/lezione-18-the-ieee-802-15-4-standard-img-01.jpg)
*Fig. — Struttura della PPDU: SHR (Synchronization Header), PHR (PHY Header) e PHY Payload (PSDU). Il frame viene trasmesso da sinistra (preamble) a destra (payload MAC).*

- **SHR** (*Synchronization Header*): contiene la sequenza di preambolo e il delimitatore di inizio frame (SFD, *Start-of-Frame Delimiter*). Permette al ricevitore di sincronizzarsi con il trasmettitore.
- **PHR** (*PHY Header*): contiene la lunghezza del frame su 7 bit più 1 bit riservato. Il campo *Frame length* può valere 5 (per i MAC ACK) oppure da 9 a 127 per gli altri tipi di pacchetto.
- **PHY Payload** (PSDU): il MAC frame incapsulato.

---

## MAC Layer

Il **MAC layer** di IEEE 802.15.4 si sovrappone al physical layer e fornisce i meccanismi per l'accesso al mezzo condiviso, la sincronizzazione, la formazione della rete e la sicurezza di base.

### Servizi del MAC Layer

**Data services**: trasmissione e ricezione di **MPDU** (*MAC Protocol Data Unit*) attraverso il physical layer.

**Management services**: sincronizzazione delle comunicazioni, accesso al canale, gestione dei **Guaranteed Time Slot** (GTS), associazione e disassociazione dei dispositivi alla rete.

**Security services**: cifratura dei dati, controllo degli accessi, integrità dei frame, garanzie di freschezza sequenziale.

### Tipi di Dispositivi

> [!definition] Reduced Function Device (RFD)
>
> Dispositivo con capacità ridotte di elaborazione, memoria e comunicazione. Tipicamente sensori o attuatori semplici (interruttori, lampade). Implementa solo un sottoinsieme del MAC layer: può associarsi a una rete esistente, ma dipende da un FFD per comunicare. Ogni RFD può essere associato a un solo FFD alla volta.

> [!definition] Full Function Device (FFD)
>
> Implementa il MAC layer completo. Può fungere da coordinatore di PAN (*PAN coordinator*) o da coordinatore generico di un gruppo di RFD. Il PAN coordinator seleziona l'identificatore di PAN e gestisce le associazioni e disassociazioni dei dispositivi.

### Topologie di Rete

Il MAC layer supporta due topologie fondamentali.

**Topologia a stella (Star)**: un unico FFD funge da PAN coordinator; tutti gli altri nodi — compresi eventuali FFD usati come router — comunicano esclusivamente con lui e si comportano come RFD. Il PAN coordinator sincronizza tutte le comunicazioni nella rete. PAN diverse hanno identificatori distinti e sono indipendenti.

![Topologia Star IEEE 802.15.4](images/lezione-18-the-ieee-802-15-4-standard-img-02.jpg)
*Fig. — Topologia Star: il PAN coordinator (arancione) al centro; FFD blu e RFD rossi collegati direttamente. Anche i router agiscono come RFD in questa topologia.*

**Topologia peer-to-peer**: ogni FFD può comunicare con qualunque altro dispositivo nel suo raggio radio. Un FFD è il PAN coordinator, gli altri FFD sono router; ogni RFD è un end-device connesso a un FFD. Questa topologia permette la formazione di reti mesh e alberi.

![Topologia Peer-to-Peer IEEE 802.15.4](images/lezione-18-the-ieee-802-15-4-standard-img-03.jpg)
*Fig. — Topologia Peer-to-Peer: gli FFD (blu) si interconnettono tra loro; gli RFD (rosso) sono end-device connessi ciascuno a un FFD. Il PAN coordinator è in arancione.*

### Accesso al Canale con Superframe

La modalità *beacon-enabled* struttura il tempo in **superframe**, delimitati dall'invio periodico di un frame beacon da parte del PAN coordinator. Il superframe divide il tempo in due porzioni: una **active period** e una **inactive period**. Durante il periodo inattivo il PAN coordinator e i dispositivi connessi possono entrare in modalità a basso consumo (sleep).

La **active period** comprende fino a **16 time slot** di uguale dimensione, suddivisi in:

- **CAP** (*Contention Access Period*): fino a 15 slot. I dispositivi competono per il canale usando il protocollo **CSMA-CA a slot** (*slotted CSMA-CA*). Un dispositivo attende un numero casuale di slot; se il canale è occupato riprova dopo un altro backoff casuale; se è libero trasmette e mantiene il canale fino alla fine del frame.
- **CFP** (*Contention Free Period*): opzionale, occupa gli ultimi slot del periodo attivo. Diviso in **GTS** (*Guaranteed Time Slot*), ciascuno assegnato dal PAN coordinator a una specifica applicazione. Il GTS è accessibile senza CSMA-CA, garantendo latenza deterministica. Ogni CFP può contenere al massimo 7 GTS, ciascuno composto da uno o più slot.

![Struttura del superframe CAP e CFP](images/lezione-18-the-ieee-802-15-4-standard-img-04.jpg)
*Fig. — Struttura del superframe: il beacon apre il periodo attivo, diviso in CAP (accesso CSMA-CA, arancione) e CFP opzionale con GTS (verde). Segue il periodo inattivo.*

> [!warning] Il CAP non può essere eliminato
>
> Anche quando è presente il CFP, il CAP è necessario per il mantenimento della rete: gestione di associazioni/disassociazioni, richieste di GTS, ecc. Tutte le transazioni basate su contesa devono completarsi prima dell'inizio del CFP. Un dispositivo che trasmette in un GTS deve completare la trasmissione entro il suo GTS assegnato.

> [!tip] Intuizione: CAP vs CFP
>
> Il CAP è come un incrocio senza precedenza fissa (tutti attendono il proprio turno casuale). Il CFP è come una corsia riservata (accede solo chi ha la prenotazione). Le applicazioni real-time o ad alta priorità richiedono GTS nel CFP; le comunicazioni ordinarie usano il CAP.

### Accesso al Canale senza Superframe

Nella modalità *non beacon-enabled*, non esiste struttura a superframe. L'accesso al canale usa **CSMA-CA non a slot** (*unslotted CSMA-CA*). I coordinatori devono essere sempre attivi per ricevere dati dagli end-device.

Il trasferimento in direzione coordinatore → end-device è basato su polling: l'end-device si sveglia periodicamente e interroga il coordinatore per verificare se ci sono messaggi in attesa. Il coordinatore risponde con il messaggio pendente o segnala che non ve ne sono.

---

## Modalità di Trasferimento Dati

IEEE 802.15.4 definisce tre direzioni di trasferimento dati:

1. **End-device → coordinatore (o router)**
2. **Coordinatore (o router) → end-device**
3. **Peer-to-peer**

La topologia a stella usa solo le modalità 1 e 2. La peer-to-peer le supporta tutte e tre.

### Trasferimento in Reti Beacon-Enabled

**Da end-device a coordinatore**: il dispositivo attende il beacon per sincronizzarsi. Se possiede un GTS lo usa senza contesa; altrimenti trasmette nel CAP usando CSMA-CA a slot. Il coordinatore può inviare un ACK opzionale.

**Da coordinatore a end-device**: il coordinatore memorizza il messaggio e segnala nel beacon che c'è un messaggio pendente. L'end-device, che dorme la maggior parte del tempo, ascolta occasionalmente il beacon. Quando rileva un messaggio pendente invia un *Data request* nel CAP (con ACK immediato dal coordinatore). Il coordinatore trasmette il messaggio in uno slot successivo del CAP; l'end-device invia un ACK obbligatorio. Infine il coordinatore rimuove il messaggio dalla lista.

**Peer-to-peer**: tra coordinatore/router e end-device si applicano gli schemi precedenti. Due end-device non possono comunicare direttamente. La comunicazione tra due coordinatori o tra coordinatore e router richiede che il mittente si sincronizzi con il beacon del destinatario — ma le modalità per farlo sono fuori dallo scope dello standard.

### Trasferimento in Reti Non Beacon-Enabled

**Da end-device a coordinatore**: il dispositivo trasmette direttamente con CSMA-CA non a slot; il coordinatore deve essere sempre attivo. L'ACK è opzionale.

**Da coordinatore a end-device**: il coordinatore memorizza il messaggio; l'end-device interroga periodicamente il coordinatore con una *Data request* (CSMA-CA non a slot), riceve ACK, poi il messaggio, poi invia l'ACK finale. Se non ci sono messaggi pendenti il coordinatore risponde con un messaggio vuoto.

**Peer-to-peer**: ogni dispositivo può comunicare con ogni altro nel suo raggio radio. I dispositivi devono restare sempre attivi oppure sincronizzarsi tra loro — ma la sincronizzazione è delegata ai layer superiori.

---

## Servizi e Primitive del MAC Layer

Il MAC layer comunica con il network layer attraverso un modello a **primitive** di tipo SAP (*Service Access Point*). Le quattro primitive sono:

- **Request**: il network layer chiede un servizio al MAC layer.
- **Indication**: il MAC layer notifica un evento al network layer.
- **Response**: il network layer risponde a un'indication.
- **Confirm**: il MAC layer riporta il risultato di una request precedente.

### Data Service

Il **Data Service** usa solo request, confirm e indication:

- **DATA.request**: invocata dal network layer per spedire un messaggio a un altro dispositivo.
- **DATA.confirm**: riporta al network layer il risultato della trasmissione — successo o codice di errore.
- **DATA.indication**: generata dal MAC layer alla ricezione di un messaggio dal physical layer; consegna il messaggio al network layer.

![Diagramma flusso MAC Data Service e protocollo di associazione ZigBee](images/lezione-18-the-ieee-802-15-4-standard-img-05.jpg)
*Fig. — In alto: lato end-device del protocollo ASSOCIATE con i passi della primitiva ASSOCIATE.request. In basso: come il Join Protocol di ZigBee (NWK layer) si appoggia al SCAN + ASSOCIATE del MAC 802.15.4.*

### Management Service

Il **Management Service** include le seguenti primitive principali:

| Primitiva | Funzionalità |
|---|---|
| ASSOCIATE | Richiesta di associazione di un nuovo dispositivo a una PAN |
| DISASSOCIATE | Abbandono di una PAN |
| BEACON-NOTIFY | Fornisce al network layer il beacon ricevuto |
| GET / SET | Lettura/scrittura dei parametri della MAC-PIB |
| GTS | Richiesta di un GTS al coordinatore |
| SCAN | Ricerca di PAN attive |
| COMM-STATUS | Notifica al network layer dello stato di una transazione |
| START | Avvia una PAN e inizia a inviare beacon; usato anche per la device discovery |
| POLL | Richiesta di messaggi pendenti al coordinatore |

Le primitive marcate "O" nella specifica sono opzionali per gli RFD.

---

## Protocollo di Associazione

L'associazione è il processo con cui un dispositivo entra a far parte di una PAN. È pensata per reti beacon-enabled e si compone di una fase sul lato end-device e una sul lato coordinatore.

### Lato End-Device

Il dispositivo che vuole associarsi deve aver identificato in anticipo la PAN di destinazione attraverso il servizio **SCAN** (scansione attiva). Invoca poi la primitiva **ASSOCIATE.request**, che prende come parametri l'identificatore di PAN, l'indirizzo del coordinatore e il proprio indirizzo IEEE a 64 bit esteso. La richiesta viene inviata nel CAP usando CSMA-CA a slot. Il coordinatore invia un ACK immediato — ma questo non implica che la richiesta sia stata accettata.

> [!note] Connessione con ZigBee
>
> Il protocollo di JOIN dello stack ZigBee si appoggia esattamente a SCAN + ASSOCIATE del MAC 802.15.4: il NWK layer invoca NETWORK-DISCOVERY.request → il MAC esegue SCAN → il NWK seleziona una PAN → invoca JOIN.request → il MAC esegue il protocollo ASSOCIATE.

### Lato Coordinatore

Dopo aver ricevuto la richiesta, il MAC layer del coordinatore emette **ASSOCIATE.indication** verso il network layer (NWK), che decide se accettare o rifiutare. In caso di accettazione, il NWK layer:

1. Seleziona un **indirizzo a 16 bit** che il dispositivo utilizzerà in futuro al posto dell'indirizzo a 64 bit.
2. Invoca **ASSOCIATE.response**, passando come parametri l'indirizzo a 64 bit del dispositivo, il nuovo indirizzo a 16 bit e lo status della richiesta.
3. Il MAC layer invia la risposta di associazione usando **trasmissione indiretta** (il dispositivo deve fare polling per recuperarla).

![Diagramma di sequenza del protocollo ASSOCIATE IEEE 802.15.4](images/lezione-18-the-ieee-802-15-4-standard-img-06.jpg)
*Fig. — Diagramma di sequenza completo del protocollo ASSOCIATE: flusso tra NWK/MAC del dispositivo originatore e NWK/MAC del coordinatore. Dopo il pre-defined waiting time, il dispositivo invia una Data request per recuperare la risposta.*

### Completamento del Protocollo

Dopo che il dispositivo ha recuperato la risposta (tramite Data request → ACK → Association response → ACK):

- Il **MAC layer dell'end-device** emette **ASSOCIATE.confirm** al NWK layer.
- Il **MAC layer del coordinatore** emette **COMM-STATUS.Indication** al NWK layer, segnalando che l'associazione è conclusa — con successo o con un codice di errore.

---

## Sicurezza del MAC Layer

IEEE 802.15.4 fornisce un supporto di base alla sicurezza direttamente nel MAC layer. Le funzionalità avanzate — come la gestione delle chiavi e l'autenticazione dei dispositivi — sono delegate ai layer superiori. I servizi di sicurezza sono opzionali. Tutti i servizi di sicurezza si basano su **crittografia simmetrica**; le chiavi crittografiche sono fornite dai layer superiori.

### Controllo degli Accessi

Ogni dispositivo mantiene un **ACL** (*Access Control List*) che elenca i dispositivi con cui può comunicare. I frame ricevuti da dispositivi non presenti nell'ACL vengono scartati.

### Cifratura dei Dati

La cifratura simmetrica si applica ai dati, ai comandi e ai payload dei beacon. La chiave può essere:

- una **group key** condivisa da un gruppo di dispositivi;
- una **link key** condivisa solo tra due peer specifici.

### Integrità dei Frame

L'integrità protegge i frame da modifiche non autorizzate e garantisce che il frame provenga da un dispositivo in possesso della chiave crittografica. Usa la stessa chiave della cifratura e si applica a frame dati, beacon e comandi.

### Freschezza Sequenziale

La **Sequential Freshness** ordina la sequenza dei frame in ingresso per garantire che ogni frame ricevuto sia più recente dell'ultimo frame ricevuto — difesa contro gli attacchi di replay.

> [!abstract] Sintesi della Lezione
>
> IEEE 802.15.4 specifica il physical layer e il MAC layer per reti LR-WPAN. Il physical layer opera su tre bande di frequenza (868 MHz, 902 MHz, 2.4 GHz), con eccellenti prestazioni in ambienti a basso SNR. Il MAC layer distingue due tipi di dispositivi (RFD e FFD), supporta topologie a stella e peer-to-peer, e gestisce l'accesso al canale con o senza superframe. Il superframe è diviso in CAP (accesso CSMA-CA) e CFP opzionale (GTS deterministici). Il protocollo di associazione permette ai dispositivi di unirsi a una PAN esistente. La sicurezza di base — cifratura simmetrica, controllo accessi, integrità, freschezza — è integrata nel MAC layer.

> [!question] Possibili domande d'esame
>
> - Quali sono le bande di frequenza supportate da IEEE 802.15.4 e quali data rate offrono?
> - Qual è la differenza tra RFD e FFD?
> - Come funziona la struttura del superframe? Qual è la differenza tra CAP e CFP?
> - Perché il CAP non può essere eliminato anche quando è presente il CFP?
> - Descrivi il trasferimento di dati da coordinatore a end-device in una rete beacon-enabled.
> - Descrivi il protocollo di associazione dal lato end-device e dal lato coordinatore.
> - Quali servizi di sicurezza offre il MAC layer di IEEE 802.15.4?
> - Qual è la differenza tra accesso al canale beacon-enabled e non beacon-enabled?
