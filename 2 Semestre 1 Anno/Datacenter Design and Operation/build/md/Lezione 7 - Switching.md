## Il Contesto: Perché il Network è Cambiato

Per capire l'architettura attuale degli switch è necessario capire _perché_ è cambiata rispetto al passato. Il docente traccia una periodizzazione sintetica ma illuminante dell'evoluzione dei workload in ambito IT.

Per quasi tre decenni, il panorama applicativo era diviso in due categorie: l'**HPC** (High Performance Computing), dove il calcolo superava la capacità del singolo nodo e si ricorreva a cluster, e le **applicazioni enterprise** — web server, database, middleware — dove la capacità di calcolo disponibile superava di gran lunga quanto necessario e si preferiva concentrare più servizi su un singolo nodo denso di core. In entrambi i casi, la rete era un fattore secondario: le applicazioni enterprise vivevano prevalentemente di traffico Nord-Sud (client verso server), mentre in HPC i nodi comunicavano su interconnessioni specializzate.

Tutto cambia intorno al **2013**, con l'esplosione del paradigma Big Data (Hadoop e simili). L'adozione massiva di SSD, che abbassano la latenza di accesso allo storage da millisecondi a microsecondi, rende conveniente muovere grandi quantità di dati all'interno del data center. Nasce così il cosiddetto traffico **East-West**: comunicazione da server a server all'interno dello stesso datacenter. Questo tipo di traffico esige reti a bassa latenza e alta banda tra i nodi, requisiti molto diversi rispetto al traffico tradizionale.

Il colpo finale al vecchio ordine arriva con l'**AI generativa**. Per la prima volta emerge un workload che richiede simultaneamente: molto calcolo, molta memoria veloce, molte GPU e interconnessioni ad altissima banda. Il bilanciamento del sistema si rompe, e tutti i componenti — CPU, memoria, storage, rete — devono essere ripensati.

> [!tip] Il principio del bilanciamento
> 
> Un sistema è efficiente solo quando tutti i suoi componenti sono dimensionati in modo coerente. Avere una rete da 200 Gbps con CPU che processano al massimo 80 Gbps è uno spreco. La progettazione del data center è sempre un esercizio di bilanciamento.

### La Fine dei Chassis e il Fixed Form Factor

Sul lato networking, un ulteriore cambiatore è stata la velocità di evoluzione della tecnologia. In passato era conveniente investire in chassis modulari costosi (uno switch chassis con schede sostituibili), poiché la vita utile dell'investimento era lunga. Ma quando la capacità dei port ASIC raddoppia ogni pochi anni, il chassis diventava obsoleto prima delle sue schede. Il costo di un chassis a lunga vita non si giustificava più.

La risposta è stata il **fixed form factor switch**: 1 o 2 unità rack, non modulare, ma aggregabile via software in topologie spine-leaf. Questo approccio rende il traffico East-West più prevedibile — sia in latenza che in banda — e consente di aggiornare la rete sostituendo interi switch (commodity hardware) invece di investire in chassis proprietari.

---

## Architettura Interna dello Switch

Uno switch moderno da data center non è un appliance speciale: è fondamentalmente un **computer general purpose** a cui è stato affiancato hardware specializzato per il forwarding dei pacchetti. Il professore insiste su questo punto perché rompe la percezione comune dello switch come "scatola nera" di rete.

> [!definition] Control Plane e Data Plane
> 
> Lo **switch di rete** — come qualsiasi dispositivo di comunicazione complesso — si divide in due piani funzionali distinti:
> 
> - Il **Control Plane** (piano di controllo) è responsabile della _configurazione_, della _gestione_ e del _monitoraggio_. Qui risiedono la logica delle policy, i protocolli di routing, i contatori delle porte, il sistema operativo di rete.
> - Il **Data Plane** (piano dati) è responsabile dell'_esecuzione_: riceve i pacchetti sulle porte ingress, determina la porta egress consultando le tabelle popolate dal control plane, e li instrada alla velocità del silicio.

![Architettura SDN: separazione tra application layer, control plane e data plane (infrastructure layer)](images/Software-defined-networking-SDN-architecture-source-Open-Networking-Foundation-ONF1-36c6af.png)
*Fig. — La separazione funzionale tra i piani di rete secondo l'Open Networking Foundation: application layer (policy e gestione), control plane (logica di routing) e infrastructure layer (forwarding a linerate nel silicio). Nello switch da data center moderno il management coincide tipicamente con il control plane.*

### Il Data Plane: Silicon Commodity

Il data plane è dove si esegue il vero lavoro di forwarding, e oggi è dominato da **ASIC** (Application-Specific Integrated Circuit) forniti da un numero ristretto di vendor. Broadcom è il nome più citato in questo settore: chip come il **Jericho** sono progettati per memorizzare la tabella di routing completa dell'Internet pubblico (e il doppio, stando alle specifiche) e per forwarding a linerate di terabit per secondo. Chiunque voglia costruire uno switch compra il catalogo Broadcom, sceglie il chip in base alle prestazioni desiderate e progetta la scheda attorno ad esso.

Questo ha una conseguenza fondamentale: **il data plane è diventato commodity**. La differenziazione tra vendor non sta più nel silicio ma nel software del control plane e nell'ecosistema di gestione.

> [!note] Non-blocking switching
> 
> Uno switch si dice **non-blocking** quando può commutare simultaneamente tutto il traffico su tutte le sue porte senza che nessun flusso debba aspettare. Con 48 porte da 25 Gbps + 8 uplink da 100 Gbps, il backplane deve reggere: $(48 \times 25 + 8 \times 100) \times 2 = 3.6 \text{ Tbps}$ Il fattore $\times 2$ è perché ogni porta lavora in full-duplex (RX + TX). Gli switch da data center moderni sono progettati per essere non-blocking, e il costo di questa capacità si riflette nell'alimentazione: sono macchine da 700 W, contro i 200 W di una volta.

### Il Control Plane: Linux dentro lo Switch

Al di sopra del data plane c'è il control plane, che è — sorprendentemente per chi non ci ha mai lavorato — un **Linux** che gira su una CPU Intel Celeron o equivalente. Ci sono RAM, storage flash, e una connessione PCIe verso l'ASIC del data plane. Il bus PCIe in uno switch non ha la stessa larghezza di banda di quello di un server: la sua funzione è inviare comandi di configurazione all'ASIC (aggiornare le tabelle di forwarding, cambiare le policy delle porte), non trasportare i dati dei pacchetti.

> [!warning] PCIe tra control e data plane: non è una pipe di dati
> 
> Il bus PCIe che collega control plane e data plane in uno switch è dimensionato per la _configurazione_, non per il _forwarding_. In linea di principio si potrebbero far processare i pacchetti dalla CPU del control plane, ma la banda disponibile non è sufficiente per reggere il volume di traffico che l'ASIC gestisce. Questo limita il tipo di funzioni implementabili nel software rispetto all'hardware.

---

## SONiC e l'Open Networking

Il fatto che il silicio sia commodity ha aperto la porta alla disaggregazione hardware/software, un trend che in ambito server è avvenuto decenni fa (BIOS + OS generico) e che nella rete stava tardando per ragioni miste: tecniche e commerciali.

**ONIE** (Open Network Install Environment) è il bootloader standard per switch che supporta questa disaggregazione. Esattamente come GRUB carica un OS su un PC, ONIE carica un'immagine di Network Operating System sullo switch. Chi compra uno switch ONIE-compatibile può scegliere quale NOS installare, come si fa con un server.

**SONiC** (Software for Open Networking in the Cloud) è il NOS open source sviluppato originariamente da Microsoft per i propri data center Azure e poi donato alla comunità tramite la Linux Foundation. È costruito su Linux, basato su container Docker per la modularità, e utilizza Redis come database in-memory per la comunicazione tra i componenti. Oggi è co-mantenuto da Microsoft, Arista, Dell e molti altri vendor.

![SONiC — architettura ad alto livello con componenti containerizzati](images/TAHKyAT-6370ad.png) _Fonte: Azure/SONiC (GitHub) — Architettura di SONiC: ogni funzione di rete (BGP, LLDP, SNMP, DHCP relay) gira in un container Docker separato e comunica tramite Redis DB._

> [!note] Due immagini OS sullo switch
> 
> Gli switch moderni mantengono due immagini del sistema operativo sul disco: quella _corrente_ in esecuzione e una di _riserva_. Quando si aggiorna il NOS, si scarica la nuova immagine nella slot di riserva, si riavvia il dispositivo, e se qualcosa va storto si torna all'immagine precedente con un comando. Questo pattern di rollback è fondamentale per la resilienza della rete.

Il docente ricorda di aver contribuito personalmente a **Dell Networking OS 10** nel 2014, quando fu introdotta la possibilità di aprire una bash shell direttamente sul control plane. È arrivato a compilare software direttamente sulla CPU dello switch usando Visual Studio Code — il che dà un'idea concreta di cosa significhi "il control plane è un PC".

Sul mercato esiste un ecosistema di NOS: oltre a SONiC (open source), ci sono EOS di Arista, DNOS di Dell, e NOS proprietari di altri vendor. Alcuni vendor offrono SONiC con un layer proprietario opzionale, venduto come licenza aggiuntiva per chi vuole supporto professionale.

---

## La CLI dello Switch: un Linguaggio Modale

La configurazione di uno switch avviene tramite una **CLI modale** — un'interfaccia a riga di comando in cui i comandi disponibili dipendono dal _contesto_ (modalità) corrente. Questo design nasce da esigenze pratiche: i primi switch si configuravano collegando fisicamente un laptop al serial port nella sala server, in ambienti rumorosi, e quindi la CLI doveva essere il più efficiente possibile da digitare. La convenzione nata in casa Cisco è diventata de facto standard, imitata da quasi tutti i vendor successivi.

Le modalità principali sono tre, in ordine gerarchico:

1. **User EXEC** (prompt `>`): sola lettura. Si può ispezionare ma non modificare.
2. **Privileged EXEC** (prompt `#`): si accede con il comando `enable`. Permette operazioni di diagnostica avanzate.
3. **Global Configuration** (prompt `(config)#`): si accede con `configure` o `conf`. Permette la modifica della configurazione.

Da Global Configuration si scende in contesti specifici digitando un identificatore (es. `interface Ethernet 1/1/3` porta nel contesto di quella porta), e si torna al padre con `exit`.

> [!example] Sessione CLI tipica su uno switch
> 
> ```
> Switch> enable
> Switch# configure
> Switch(config)# interface Ethernet 1/1/3
> Switch(config-if-Et1/1/3)# no shutdown
> Switch(config-if-Et1/1/3)# switchport
> Switch(config-if-Et1/1/3)# exit
> Switch(config)# do show interface status
> Switch(config)# do write
> ```
> 
> Il prefisso `do` permette di eseguire comandi del contesto padre senza uscirne. La CLI accetta anche abbreviazioni non ambigue: `conf` per `configure`, `sh run` per `show running-configuration`.

### Running Configuration e Startup Configuration

Uno degli aspetti più peculiari della gestione degli switch — e che sorprende chi arriva dal mondo server — è la separazione tra **running configuration** (configurazione in memoria, attiva) e **startup configuration** (configurazione salvata su disco, caricata al boot).

Ogni modifica sulla CLI agisce _solo sulla RAM_. Se si riavvia lo switch senza aver scritto la configurazione su disco, tutte le modifiche sono perse. Il comando per persistere è `write` (o `copy running-config startup-config`). Questa separazione è voluta: garantisce che lo switch torni sempre in uno stato deterministico al riavvio. Non è possibile che un'installazione incrementale di software (come accade su un OS desktop) lasci lo switch in uno stato inconsistente: si riavvia e si ottiene esattamente la configurazione salvata.

> [!warning] Perdita di configurazione al reboot
> 
> Se si modificano porte, VLAN o routing su uno switch e non si esegue `write`, al successivo riavvio (pianificato o causato da un guasto) _tutte le modifiche saranno perse_. In produzione è prassi comune emettere `write` (o `copy run start`) dopo ogni modifica verificata.

### Naming delle Porte

I nomi delle porte negli switch moderni seguono uno schema **a tre livelli**:

```
<stack_unit>/<slot>/<port>
```

- Il primo numero identifica il **membro dello stack**: quando si aggregano due o più switch fisici in un singolo switch logico (stacking), ogni unità ha il suo numero.
- Il secondo numero identifica lo **slot** o il modulo nella chassi (per switch modulari) o è sempre 1 per switch fixed.
- Il terzo numero è il **numero di porta fisica**.

Esiste anche un quarto livello opzionale per i breakout: una porta QSFP (es. 100 Gbps) può essere spezzata in 4 porte SFP28 (25 Gbps ciascuna), in tal caso si aggiunge un suffisso `/1`, `/2`, `/3`, `/4`. Il nome del tipo di porta include la velocità per ragioni storiche (es. `Ethernet` per 1G, `TenGigabitEthernet` per 10G, semplificato in CLI con abbreviazioni).

---

## VLAN: Broadcast Domain Virtuali

Uno dei concetti più importanti della lezione riguarda le **VLAN** (Virtual LAN). Per capire cosa sia una VLAN occorre prima aver chiaro cosa sia una LAN.

> [!definition] LAN come Broadcast Domain
> 
> Una **LAN** (Local Area Network) è un **dominio di broadcast**: tutti i dispositivi connessi ricevono i pacchetti broadcast inviati da qualsiasi membro. Il meccanismo di accesso al mezzo (CSMA/CD) implica che tutti i nodi "ascoltino" il canale. Questo è ciò che definisce una LAN a livello fisico e di Layer 2.

Una **VLAN** estende questo concetto in modo virtuale: consente di creare **più domini di broadcast indipendenti** sulla stessa infrastruttura fisica. Invece di avere uno switch per segmento di rete, un unico switch può servire N segmenti logicamente separati grazie al VLAN tagging.

### Il Tag IEEE 802.1Q

L'implementazione delle VLAN si basa sullo standard **IEEE 802.1Q**, che introduce un campo aggiuntivo di **12 bit** nell'header del frame Ethernet per trasportare il **VLAN ID** (VID). Con 12 bit si possono rappresentare $2^{12} = 4096$ valori, di cui 4094 utilizzabili (il VID 0 è riservato e il VID 1 è il default).

$$ \text{VLAN ID} \in [1, 4094], \quad \text{bits: } 12 $$

> [!definition] Tagged vs Untagged Port
> 
> - Una porta **untagged** (o _access port_) si connette a dispositivi end-host che non conoscono le VLAN. Lo switch aggiunge il tag quando il frame entra e lo rimuove quando esce. La VLAN assegnata è configurata per porta.
> - Una porta **tagged** (o _trunk port_) si connette a un altro switch o a un host VLAN-aware. I frame transitano con il tag 802.1Q intatto. Una trunk port può trasportare frame di VLAN multiple.

![Formato del frame Ethernet con tag 802.1Q VLAN](images/Ethernet-802-1Q-Insert-864c1f.png) _Fonte: Wikimedia Commons — Il tag 802.1Q (4 byte, TPID 0x8100) viene inserito nell'header Ethernet tra Source MAC e EtherType. I 12 bit del VLAN ID consentono fino a 4094 VLAN distinte._

Internamente allo switch, ogni pacchetto è _sempre_ taggato: se arriva untagged, il primo passo dell'ASIC è assegnarlo alla VLAN di default della porta ingress. I pacchetti viaggiano internamente con il tag, e solo all'uscita su una porta untagged il tag viene rimosso.

> [!example] Comportamento del forwarding VLAN
> 
> Un frame entra su porta `Eth1/1/1` configurata come untagged VLAN 10 → lo switch aggiunge tag VID=10. L'ASIC cerca la MAC destination nella tabella di forwarding filtrando per VID=10 → trova porta `Eth1/1/5` configurata come trunk (tagged). Il frame esce con il tag 802.1Q intatto. Se la MAC destination fosse invece su una porta untagged VLAN 10, il frame uscirebbe senza tag.

### Perché le VLAN sono Critiche

Le VLAN risolvono due problemi fondamentali del data center:

**Sicurezza e segregazione**: le VLAN separano il traffico come se fossero reti fisicamente distinte. Per questo motivo persino le forze militari — che tradizionalmente usavano tre reti fisiche separate (confidenziale, riservato, top secret) — hanno accettato l'uso di tre VLAN su una stessa infrastruttura. La garanzia è che un pacchetto in VLAN A non può mai, per come funziona l'ASIC, raggiungere un host in VLAN B, a meno di una decisione esplicita di routing.

**Flessibilità della topologia**: il cablaggio fisico è costoso e difficile da modificare. Le VLAN permettono di ridisegnare la segmentazione logica della rete semplicemente riconfigurando il tagging delle porte, senza toccare un solo cavo. Questo è stato determinante per rendere i data center agili: si possono creare o eliminare sottoreti in pochi minuti.

> [!note] VLAN e VRF
> 
> Nelle configurazioni avanzate, le VLAN si associano a **VRF** (Virtual Routing and Forwarding) per creare anche tabelle di routing virtuali distinte. Questo completa la separazione logica all'intero Layer 3, non solo Layer 2.

---

## Resilienza e Complessità del Debug di Rete

La lezione si conclude con una riflessione sul perché la rete sia progettata così com'è — funzionale, deterministica, resistente — e sul perché il debug di rete sia particolarmente difficile.

Il docente porta due aneddoti dalla propria esperienza diretta con la rete dell'Università di Pisa:

1. Un **network loop** (ciclo nella topologia di Layer 2) aveva causato un'interruzione. Il loop coinvolgeva migliaia di dispositivi e porte, rendendo il processo di individuazione estremamente lungo — al momento della lezione il loop era ancora presente e in fase di ricerca.
    
2. Un **guasto intermittente** su un collegamento in fibra ottica da 15 km tra due sedi aveva causato un downtime di due-tre giorni. La causa era probabilmente un danno fisico alla fibra (una macchina agricola aveva transitato sopra il cavo interrato). Il link LACP usava due fibre: una funzionante e una degradata. Il risultato era un comportamento intermittente difficilissimo da diagnosticare — metà del traffico funzionava, metà generava errori — con l'apparenza di un problema software o di configurazione.
    

Questi esempi illustrano un principio generale:

> [!tip] La rete è semplice ma i suoi comportamenti emergenti sono complessi
> 
> Un singolo switch fa una cosa sola: ricevere un pacchetto e decidere su quale porta inoltrarlo (store-and-forward). L'algoritmo è banale. Ma quando miliardi di pacchetti al secondo attraversano decine di switch, i comportamenti emergenti sono di una complessità enorme. Non esiste un "debugger" per la rete perché fermare l'esecuzione _cambia_ il comportamento della rete stessa. Per questo tutto in networking — dal design del software alla CLI al doppio boot image — è pensato per ridurre la probabilità di stati inconsistenti.

---

## Conclusioni e Punti Chiave

Questa lezione ha coperto l'intera catena dall'hardware al software negli switch di rete moderni:

- Lo switch è un **computer general purpose** con una CPU x86 (control plane, Linux) e un ASIC specializzato (data plane, silicon commodity da Broadcom et al.) collegati via PCIe.
- La distinzione **control plane / data plane** è il framework concettuale fondamentale per capire qualsiasi dispositivo di rete.
- **SONiC** e **ONIE** rappresentano la direzione del mercato verso la disaggregazione hardware/software, con NOS open source intercambiabili come gli OS sui server.
- La **CLI modale** — heritage Cisco — è ancora lo strumento primario di configurazione, con il meccanismo running/startup config che garantisce il determinismo allo stato di boot.
- Le **VLAN** (IEEE 802.1Q, 12 bit di VLAN ID, 4094 VLAN possibili) sono lo strumento fondamentale per creare broadcast domain virtuali su una stessa infrastruttura fisica, abilitando sia la sicurezza che la flessibilità topologica.
- Il debug della rete è intrinsecamente difficile a causa del volume di traffico e della natura dinamica del sistema: l'approccio funzionale (switch che tornano sempre nello stesso stato al riavvio) è la risposta architettuale a questo problema.

> - Spiega il naming `1/1/3` di una porta su uno switch stack.