
# The ZigBee Standard — Part 1

## Obiettivi e Caratteristiche

Lo standard **ZigBee** è un protocollo di comunicazione concepito specificamente per le reti di sensori wireless (**wireless sensor networks**), sviluppato e promosso dalla **ZigBee Alliance**. Le sue applicazioni spaziano dalla **home automation** (domotica e _ambient assisted living_) all'assistenza sanitaria (**health care**), dall'elettronica di consumo all'automazione industriale, fino a impieghi estremi come le missioni di esplorazione su Marte.

![[Pasted image 20260309111850.png]]
*Panoramica delle applicazioni ZigBee nei diversi domini.*

I requisiti di progetto (**main requirements**) che ZigBee deve soddisfare sono tre: la rete deve operare in modo completamente autonomo senza intervento umano, i dispositivi devono avere una durata della batteria molto elevata lavorando a basso data rate, e deve essere garantita la piena interoperabilità tra dispositivi di produttori differenti.

Le caratteristiche principali (**main features**) che ne derivano sono coerenti con questi requisiti: ZigBee è basato su standard aperti, ha costi ridotti, può essere impiegato globalmente, è affidabile e auto-rigenerante (_self-healing_), scala a un numero elevato di nodi, è facile da distribuire sul campo e garantisce sicurezza delle comunicazioni insieme a una lunghissima durata della batteria.

---

## Rapporto con IEEE 802.15.4 e Architettura a Strati

ZigBee è costruito sopra lo standard **IEEE 802.15.4**, rilasciato nel 2003 e revisionato nel 2006. ZigBee stesso è stato pubblicato per la prima volta a fine 2004 e revisionato nel 2006; entrambe le prime revisioni sono distribuite gratuitamente.

![[Pasted image 20260309111918.png]]
*Corrispondenza tra i livelli ISO/OSI e gli standard IEEE 802.15.4 e ZigBee.*

In termini di stack protocollare, IEEE 802.15.4 copre il **Physical layer** e il **MAC layer**, gestendo reti a basso data rate definite _Wireless Personal Area Networks_. Questo standard è infrastructure-less, a corto raggio, supporta topologie a stella e peer-to-peer e può coesistere con IEEE 802.11 e Bluetooth (IEEE 802.15.1). Opera su bande di frequenza libere da licenza: 868–868.6 MHz (Europa) a 20 kbps, 902–928 MHz (Nord America) a 40 kbps, e 2400–2483.5 MHz (mondiale) a 250 kbps.

ZigBee aggiunge sopra questi livelli il **Network layer** e l'**Application layer**. Il livello applicativo è articolato in tre componenti: l'**Application Framework**, che ospita fino a 240 **Application Objects (APO)** numerati da 1 a 240, ciascuno rappresentante un'applicazione ZigBee definita dall'utente; il **ZigBee Device Object (ZDO)**, che fornisce i servizi per organizzare gli APO in un'applicazione distribuita; e l'**Application Support sublayer (APS)**, che eroga servizi di dati e gestione sia agli APO sia allo ZDO.

---

## Servizi e Primitive di Comunicazione

Ogni livello dello stack eroga servizi di dati e di gestione al livello superiore tramite quattro tipologie di **Service Primitives**. La **Request** è invocata dal livello superiore per richiedere un servizio al livello inferiore. L'**Indication** è generata dal livello inferiore verso quello superiore per notificare il verificarsi di un evento. La **Response** è invocata dal livello superiore per completare una procedura iniziata da una precedente Indication. La **Confirm** è generata dal livello inferiore per comunicare al livello superiore l'esito di una o più Request precedenti. Non tutti i servizi utilizzano tutte e quattro le primitive.

In uno schema di comunicazione end-to-end, un oggetto applicativo incapsula i dati in un **APDU**, che passa al servizio dati APS diventando **NPDU**. Il livello **NWK** aggiunge le proprie intestazioni producendo un **MPDU** tramite il NWK data service; il livello **MAC** genera la **PPDU** tramite il MAC data service, che viene infine trasmessa fisicamente dal **PHY** data service verso la destinazione, dove il processo si inverte.

![[Pasted image 20260309111946.png]]
*Flusso di incapsulamento dei dati attraverso i livelli dello stack ZigBee, da sorgente a destinazione.*

---

## Il Network Layer: Topologie e Servizi

### Tipologie di Dispositivi

Il Network Layer definisce tre ruoli distinti. Il **Network Coordinator** è un dispositivo completamente funzionale (**FFD**, _full functional device_) che crea e gestisce l'intera rete. I **Router** sono anch'essi FFD e dispongono di capacità di instradamento. Gli **End-device** sono dispositivi a funzionalità ridotta (**RFD**, _reduced functional device_) o FFD che operano come nodi semplici senza capacità di routing.

Le topologie gestite dal Network Layer sono tre. La topologia a **stella** si mappa direttamente sulla struttura IEEE 802.15.4 e utilizza il meccanismo del _superframe_. La topologia ad **albero** può anch'essa avvalersi del superframe. La topologia a **mesh** opera invece tipicamente senza superframe, affidandosi a comunicazioni dirette nodo-nodo.

### Tabella dei Servizi

| **Name**              | **Request** | **Indication** | **Confirm** | **Description**                                                       |
| --------------------- | :---------: | :------------: | :---------: | --------------------------------------------------------------------- |
| **DATA**              |      X      |       X        |      X      | Trasmissione dati.                                                    |
| **NETWORK-DISCOVERY** |      X      |                |      X      | Ricerca di PAN esistenti.                                             |
| **NETWORK-FORMATION** |      X      |                |      X      | Creazione di una nuova PAN (coordinator).                             |
| **PERMIT-JOINING**    |      X      |                |      X      | Consente l'associazione di nuovi dispositivi alla PAN.                |
| **START-ROUTER**      |      X      |                |      X      | (Re-)inizializza il superframe del coordinator o di un router.        |
| **JOIN**              |      X      |       X        |      X      | Richiesta di unirsi a una PAN esistente.                              |
| **DIRECT-JOIN**       |      X      |                |      X      | Forza un end-device a unirsi alla PAN del coordinator o di un router. |
| **LEAVE**             |      X      |       X        |      X      | Lasciare una PAN.                                                     |
| **RESET**             |      X      |                |      X      | Resetta il livello di rete.                                           |
| **SYNC**              |      X      |                |      X      | Sincronizza o estrae dati pendenti dal coordinator o da un router.    |
| **GET**               |      X      |                |      X      | Legge i parametri del livello di rete.                                |
| **SET**               |      X      |                |      X      | Imposta i parametri del livello di rete.                              |

---

## Network Formation

Prima di comunicare, un dispositivo ZigBee deve formare una nuova rete assumendo il ruolo di **ZigBee Coordinator**, oppure unirsi a una rete esistente come router o end-device. Il ruolo viene scelto a tempo di compilazione (_compile-time_).

La **Network Formation** è avviata dal Coordinator — solo se non è già parte di un'altra PAN — tramite la primitiva **NETWORK-FORMATION.request**. Il processo si articola in una sequenza di interazioni con il livello MAC: dapprima vengono eseguiti un energy scan e un active scan (tramite **SCAN.request** e **SCAN.confirm**) per identificare il canale meno rumoroso e verificare l'assenza di reti limitrofe che potrebbero generare conflitti. Individuato il canale, viene selezionato un **PAN ID** non ancora in uso, dopodiché il Coordinator si auto-assegna l'indirizzo di rete a 16 bit **0x0000**. Invoca quindi **SET.request** al livello MAC per configurare PAN identifier e indirizzo del dispositivo, e infine emette **START.request** (confermata da **START.confirm**) affinché il MAC inizi a trasmettere i beacon. La sequenza si chiude con la **NETWORK-FORMATION.confirm** verso il livello applicativo.

---

## Ingresso in una Rete Esistente

Un dispositivo può unirsi a una rete in due modi: tramite associazione classica avviata dal dispositivo stesso, oppure tramite **Direct join**, in cui è il coordinator o un router a forzare un end-device ad aggregarsi alla propria PAN.

### Join through Association (child-side)

Il dispositivo avvia una **NETWORK-DISCOVERY** emettendo una **SCAN.request** di tipo active scan per individuare le PAN disponibili. Ricevuta la **NETWORK-DISCOVERY.confirm**, seleziona la PAN di interesse e invia una **JOIN.request** contenente l'identificatore della rete e un flag che indica se intende aggregarsi come router o come end-device.

A livello NWK, la JOIN.request porta alla selezione di un nodo genitore **P** appartenente alla PAN nel vicinato del dispositivo. Il comportamento varia in base alla topologia: in una rete a stella P è necessariamente il coordinator e il dispositivo si aggancia come end-device; nelle topologie ad albero P può essere il coordinator o un router, e il dispositivo può aggregarsi sia come router sia come end-device.

Tramite il protocollo di associazione MAC (primitive **ASSOCIATE.request** e **ASSOCIATE.confirm**), il nodo P assegna al nuovo dispositivo un **indirizzo breve a 16 bit** (_short address_), che viene consegnato al livello NWK tramite **JOIN.confirm** e utilizzato per tutte le comunicazioni successive.

> [!note] Direct Join
>
> Nel Direct Join è il coordinator o un router a prendere l'iniziativa, forzando un end-device ad aggregarsi alla propria PAN tramite la primitiva **DIRECT-JOIN.request**. Non richiede che il dispositivo target avvii autonomamente una Network Discovery.

---

## Struttura ad Albero e Indirizzamento

Le relazioni genitore-figlio stabilite durante il joining costruiscono una topologia logica ad albero in cui il Coordinator funge da radice, i router sono nodi interni (o foglie), e gli end-device sono esclusivamente foglie.

Questa struttura viene sfruttata per l'assegnazione sistematica degli indirizzi di rete. Al momento della formazione, il Coordinator viene configurato con tre parametri statici:

- $R_m$: numero massimo di router figli per ogni nodo router.
- $D_m$: numero massimo di end-device figli per ogni nodo router.
- $L_m$: profondità massima dell'albero.

In base a questi valori, ogni router riceve un intervallo specifico di indirizzi da distribuire ai propri discendenti. L'ampiezza dell'intervallo assegnato a un router alla profondità $d$ è calcolata tramite la funzione ricorsiva $C_{skip}$:

$$
C_{skip}(d) = \begin{cases} 1 & \text{se } d = L_m \\ 1 + R_m \cdot C_{skip}(d+1) + D_m & \text{altrimenti} \end{cases}
$$

Il valore $C_{skip}(d)$ rappresenta il numero totale di indirizzi (incluso il proprio) che ogni router alla profondità $d$ deve riservare per sé e per tutti i suoi discendenti. Se un router ha indirizzo $A$ e si trova alla profondità $d$, i suoi $R_m$ figli router ricevono rispettivamente gli indirizzi $A+1$, $A+1+C_{skip}(d+1)$, $A+1+2\cdot C_{skip}(d+1)$, …, e i suoi $D_m$ end-device ricevono gli indirizzi successivi a tutti i blocchi dei router.

> [!example] Esempio con $R_m=2$, $D_m=2$, $L_m=3$
>
> - $C_{skip}(3) = 1$
> - $C_{skip}(2) = 1 + 2 \cdot 1 + 2 = 5$
> - $C_{skip}(1) = 1 + 2 \cdot 5 + 2 = 13$
> - $C_{skip}(0) = 1 + 2 \cdot 13 + 2 = 29$ → la radice (coordinator, $A=0$) gestisce $[0\text{–}28]$
>
> Il primo figlio router riceve $A=1$ e gestisce $[1\text{–}13]$; il secondo $A=14$ e gestisce $[14\text{–}26]$; gli end-device del coordinator sono 27 e 28.

È preferibile che i dispositivi si aggreghino il più in alto possibile nell'albero per minimizzare il numero di hop. Sebbene gli indirizzi vengano assegnati secondo una struttura ad albero, la connettività fisica può comunque formare una mesh.

> [!warning] Rigidità dell'indirizzamento
>
> Il modello è riconosciuto come rigido: se un sottoalbero è localmente saturo, un nuovo dispositivo non riesce ad aggregarsi tramite quel nodo. Il vantaggio è la piena decentralizzazione — nessun router deve consultare il coordinator, non esistono rischi di collisione e non sono necessari algoritmi di accordo distribuito. La connettività fisica può comunque formare una mesh, anche se gli indirizzi sono distribuiti secondo logica ad albero.

---

## Routing

Il Network Layer supporta tre modalità di instradamento: broadcast, **Tree routing** e **Mesh routing**.

### Tree Routing

Nel Tree routing i pacchetti seguono gerarchicamente la struttura genitore-figlio dell'albero fino alla destinazione, basandosi esclusivamente sull'indirizzo di rete. È un approccio semplice ma rigido, e consente l'uso dei beacon poiché ogni router di inoltro sincronizza il proprio superframe con il nodo limitrofo.

### Mesh Routing

Il Mesh routing è più flessibile e si ispira a protocolli per reti ad hoc come **AODV**. Se il mittente è un end-device, il pacchetto viene inoltrato direttamente al suo nodo genitore. Se il mittente è un router o il coordinator, viene consultata la **Routing Table (RT)**, che contiene per ogni entry il **Destination Address** (16 bit), il **Next-hop Address** (16 bit) e l'**Entry Status** (3 bit: _Active_, _Discovery\_underway_, _Discovery\_failed_, _Inactive_).

Quando nella Routing Table non è presente un'entry valida, il router avvia il **Route Discovery Protocol**: viene diffuso in broadcast un messaggio **RREQ** (Route Request) contenente l'RREQ ID, l'indirizzo di destinazione e il path cost inizialmente a 0. I nodi intermedi propagano l'RREQ aggiornando il _Forward Cost_ in base alle stime di qualità del link fornite dall'interfaccia IEEE 802.15.4. Un nodo intermedio che conosce già il percorso verso la destinazione **può rispondere autonomamente** con un RREP senza attendere la destinazione; la destinazione risponde sempre. Il **RREP** (Route Reply) viene inviato in unicast lungo il percorso inverso: durante il ritorno ogni nodo aggiorna la propria Routing Table con il _Residual Cost_. La **Route Discovery Table (RDT)** traccia per ogni scoperta: RREQ ID (8 bit), Source Address (16 bit), Sender Address (16 bit, hop precedente a costo minore), Forward Cost (8 bit, basato su link quality estimation), Residual Cost (8 bit, compilato dal RREP) ed Expiration time (16 bit, millisecondi alla scadenza).

> [!example] Esempio di Routing Table nel Mesh
>
> Nella rete con $R_m=2$, $D_m=2$, $L_m=3$, supponiamo che il nodo 3 debba raggiungere il nodo 25. Poiché non esiste un'entry valida, viene avviato il Route Discovery. Al termine, le routing table risultanti possono essere:
>
> | Nodo | Destination | Next-hop |
> |------|-------------|----------|
> | 3    | 25          | 15       |
> | 14   | 25          | 25       |
> | 25   | —           | —        |
>
> Il nodo 3 instrada verso 15 (che ha un link diretto con 25), non necessariamente seguendo il percorso ad albero.

> [!tip] Trade-off Mesh vs Tree
>
> Mesh routing è più robusto e flessibile ma non supporta il beaconing. Tree routing consente il beaconing ma segue cammini rigidi. Le due modalità **possono coesistere nella stessa rete ZigBee**: ogni router può mantenere sia informazioni per il mesh routing che per il tree routing, e l'algoritmo di instradamento può passare dinamicamente da un modo all'altro — ad esempio usando il tree routing quando il beaconing è necessario e passando al mesh quando è preferibile un percorso ottimale.

---

> [!question] Possibili domande d'esame
>
> - Quali sono i requisiti principali e le caratteristiche dello standard ZigBee? Come si relaziona con IEEE 802.15.4?
> - Descrivere le quattro Service Primitives e il ruolo di ciascuna nello stack protocollare.
> - Come avviene la Network Formation? Descrivere la sequenza di primitive coinvolte tra NWK e MAC.
> - Quali sono le differenze tra Join through Association e Direct Join?
> - Come funziona l'indirizzamento ad albero? Cosa sono $R_m$, $D_m$, $L_m$? Definire e applicare la formula $C_{skip}$.
> - Data una rete con $R_m$, $D_m$, $L_m$ noti, calcolare il range di indirizzi assegnato a un router che si aggrega come $k$-esimo figlio di un dato nodo a profondità $d$.
> - Confrontare Tree routing e Mesh routing: meccanismi, vantaggi, limitazioni e compatibilità con il beaconing. Possono coesistere?
> - Come funziona il Route Discovery Protocol? Quali informazioni contiene la Route Discovery Table? Un nodo intermedio può rispondere all'RREQ?
