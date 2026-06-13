# The ZigBee Standard — Part 1 (Appunti d'Esame)

## Architettura a Strati e Application Layer

![[exam_chessa_zigbee_applayer.jpg]]
*Fig. — Stack protocollare ZigBee: dall'IEEE 802.15.4 (MAC) fino all'Application Layer, con Application Framework, ZDO e APS.*

ZigBee è costruito sopra lo standard IEEE 802.15.4 (PHY + MAC). Sopra questi livelli, ZigBee aggiunge il Network Layer e l'Application Layer. Il livello applicativo è articolato in tre componenti:

- **Application Framework**: ospita fino a 240 **Application Objects (APO)**, ciascuno associato a un endpoint (numerato da 1 a 240). Ogni APO è identificato univocamente dalla coppia `<indirizzo di rete, endpoint>`. Più APO sullo stesso dispositivo possono corrispondere ad applicazioni diverse che operano simultaneamente.
- **ZigBee Device Object (ZDO)**: occupa l'endpoint 0 ed è la componente gestionale del nodo. Fornisce:
  - Device & Service Discovery (trova altri nodi e i loro servizi)
  - Binding Management (crea/modifica le binding table dell'APS)
  - Network Management (gestisce join/leave e routing table)
- **Application Support Sublayer (APS)**: fa da intermediario tra APO/ZDO e il Network Layer. Fornisce:
  - *Data Service*: trasmissione messaggi con acknowledgment end-to-end
  - *Binding Service*: creazione di connessioni logiche tra endpoint
  - *Group Management*: indirizzamento multicast tramite Group Table

L'APS filtra i pacchetti per endpoint e profile ID, scartando quelli non destinati ad applicazioni registrate.

---

## Topologie di Rete e Routing

![[exam_chessa_zigbee_topologies.jpg]]
*Fig. — Le tre topologie ZigBee: Star (sinistra), Tree (centro), Mesh (destra). Nodo giallo = coordinatore, nodi blu = router, nodi rossi = end-device.*

Il Network Layer definisce tre ruoli distinti: il **Network Coordinator** (FFD che crea la rete), i **Router** (FFD con capacità di instradamento) e gli **End-device** (RFD o FFD senza capacità di routing).

ZigBee supporta tre topologie di rete:
- **Star (Stella)**: tutti i dispositivi comunicano direttamente con il coordinatore. Si mappa direttamente sulla struttura IEEE 802.15.4 e supporta il meccanismo del superframe/beacon. Semplice ma non scalabile: ogni dispositivo deve essere nel raggio radio del coordinatore.
- **Tree (Albero)**: il coordinatore è la radice, i router sono nodi interni, gli end-device sono foglie. Può usare il superframe. Il routing segue la struttura gerarchica (tree routing): i pacchetti salgono verso la radice e poi scendono verso la destinazione. Il vantaggio è la semplicità; lo svantaggio è la rigidità e i percorsi spesso subottimali.
- **Mesh**: topologia più flessibile in cui i router possono comunicare direttamente tra loro indipendentemente dalla struttura ad albero. Usa mesh routing (ispirato ad AODV, Route Discovery Protocol con RREQ/RREP). Non supporta il beaconing. È più robusto: percorsi alternativi sono disponibili se un link cade.

> [!tip] Coesistenza
> Tree routing e Mesh routing possono coesistere nella stessa rete: ogni router mantiene sia la logica ad albero che la routing table mesh, passando dinamicamente dall'uno all'altro.

---

## Ingresso in una Rete Esistente (Join through Association)

![[exam_chessa_zigbee_join.jpg]]
*Fig. — Sequenza di primitives tra Application Layer, Network Layer e MAC Layer durante il processo di join di un dispositivo ZigBee.*

Lo schema mostra il processo con cui un dispositivo si unisce a una rete ZigBee esistente attraverso il meccanismo di **associazione** (iniziativa child-side). Si tratta di un'interazione a tre livelli (Application, Network, MAC) tramite service primitives:

1. **Application layer** emette `NETWORK-DISCOVERY.request` al Network Layer.
2. **Network Layer** emette `SCAN.request` al MAC: viene eseguito un active scan per trovare le PAN disponibili.
3. **MAC** esegue lo scan e risponde con `SCAN.confirm`.
4. **Network Layer** risponde all'applicazione con `NETWORK-DISCOVERY.confirm`, che elenca le PAN trovate.
5. **Application layer** sceglie una PAN e invia `JOIN.request` al Network Layer (indicando se aggregarsi come router o end-device).
6. **Network Layer** seleziona un nodo genitore P nel vicinato (nelle reti a stella P è il coordinatore; in quelle ad albero/mesh P può essere router o coordinatore) e avvia il protocollo di associazione MAC tramite `ASSOCIATE.request`.
7. **MAC** esegue il protocollo di associazione: il coordinatore/router assegna un **indirizzo breve a 16 bit** al nuovo dispositivo.
8. **MAC** risponde con `ASSOCIATE.confirm` → **Network Layer** risponde con `JOIN.confirm` all'applicazione, rendendo operativo l'indirizzo per comunicazioni successive.

---

## Struttura ad Albero e Indirizzamento

![[exam_chessa_zigbee_addrtree.jpg]]
*Fig. — Albero di indirizzi ZigBee con $R_m=2$, $D_m=2$, $L_m=3$: ogni nodo gestisce un intervallo di indirizzi calcolato con la formula $C_{skip}$.*

Le relazioni genitore-figlio stabilite durante il joining costruiscono una topologia logica ad albero, sfruttata per l'assegnazione sistematica e decentralizzata degli indirizzi di rete.
Il coordinatore viene configurato con tre parametri:
- $R_m$: massimo numero di router figli per nodo
- $D_m$: massimo numero di end-device figli per nodo
- $L_m$: profondità massima dell'albero

La dimensione del blocco di indirizzi assegnato a un router a profondità $d$ è data dalla formula:
$$C_{skip}(d) = \begin{cases} 1 & \text{se } d = L_m \\ 1 + R_m \cdot C_{skip}(d+1) + D_m & \text{altrimenti} \end{cases}$$

Il valore $C_{skip}(d)$ rappresenta il numero totale di indirizzi (incluso il proprio) che ogni router alla profondità $d$ deve riservare per sé e per i suoi discendenti. 
Se un router ha indirizzo $A$ e si trova a profondità $d$:
- I suoi figli router ricevono in ordine: $A+1$, $A+1+C_{skip}(d+1)$, $A+1+2 \cdot C_{skip}(d+1)$, …
- I suoi end-device ricevono gli indirizzi successivi a tutti i blocchi riservati ai router.

> [!example] Nell'immagine: $R_m=2$, $D_m=2$, $L_m=3$
> - $C_{skip}(3)=1$
> - $C_{skip}(2)=5$
> - $C_{skip}(1)=13$
> - $C_{skip}(0)=29$
> Coordinator (addr=0) gestisce [0–28]. Il primo figlio router riceve addr=1 e gestisce [1–13]; il secondo figlio router riceve addr=14 e gestisce [14–26]. Gli end-device del coordinator ricevono 27 e 28.

**Vantaggio**: Completamente decentralizzato, nessun rischio di collisione, nessun coordinamento globale necessario.
**Svantaggio**: Rigido — se un sottoalbero è saturo, nuovi dispositivi non possono aggiungersi tramite quel nodo anche se ci fosse necessità. La connettività fisica può comunque formare una mesh.
