---
tags:
  - università/mobile-and-cyber-physical-systems
  - network-slicing
  - SDN
  - ryu
  - openflow
  - ComNetsEmu
  - mininet
data: 2026-05-05
lezione: "26 - Lab: Network Slicing con SDN"
professore: "Federica Paganelli"
---

# (Lab) Network Slicing con SDN e ComNetsEmu

Questa lezione hands-on mette in pratica il concetto di **network slicing** partendo dalla teoria del 5G per arrivare a un'implementazione funzionante basata su [[Lezione 15 - (Lab) SDN Architecture|SDN]] con il controller Ryu e l'emulatore ComNetsEmu. L'obiettivo centrale è dimostrare come sia possibile partizionare una singola infrastruttura fisica in sotto-reti logicamente isolate, ciascuna con garanzie proprie di banda e connettività.

---

## Contesto: il 5G e la necessità del Network Slicing

Il 5G non è semplicemente un incremento di velocità rispetto al 4G: è una riprogettazione fondamentale dell'architettura di rete, motivata dalla coesistenza di tre categorie di servizio con requisiti radicalmente diversi tra loro.

> [!definition] mMTC — massive Machine Type Communications
>
> Comunicazione tra un numero elevatissimo di dispositivi (fino a 200.000/km²), tipicamente sensori a bassa potenza e costo. I requisiti dominanti sono la **massima efficienza energetica** e la **scalabilità della connessione**, non la latenza o la banda.

> [!definition] URLLC — Ultra-Reliable Low-Latency Communications
>
> Servizi che richiedono simultaneamente **bassa latenza** (≤ 5 ms per sistemi di trasporto intelligenti, ≤ 1 ms per motion control industriale) e **alta affidabilità**. Esempi: guida autonoma, robot industriali, smart grid.

> [!definition] eMBB — Enhanced Mobile Broadband
>
> Servizi ad alta densità di dati: streaming 4K/8K, realtà aumentata e virtuale, ologrammi. Il requisito primario è la **capacità di trasmissione** e la copertura ampia.

La coesistenza di questi tre profili rende impossibile ottimizzare un'unica rete per tutti contemporaneamente. La soluzione è il **network slicing**: invece di una rete monolitica con compromessi su tutto, si creano più reti virtuali end-to-end sopra la stessa infrastruttura fisica, ognuna ottimizzata per il proprio caso d'uso.

---

## Network Slicing: il concetto

Il network slicing sfrutta le risorse dell'infrastruttura fisica per creare multiple **sotto-reti virtuali** (slice), ciascuna delle quali si comporta come una rete indipendente dal punto di vista delle applicazioni che vi girano sopra.

Ogni slice è definita in termini di:
- **funzionalità** — quali funzioni di rete sono presenti
- **QoS** — banda garantita, latenza massima, tasso di perdita tollerato
- **isolamento** — le slice non interferiscono tra loro né in termini di prestazioni né di sicurezza

### Ruolo di NFV e SDN

Le due tecnologie abilitanti del network slicing sono [[Lezione 20 - (Lab) Network Function Virtualization|NFV]] e [[Lezione 15 - (Lab) SDN Architecture|SDN]], con ruoli complementari.

**NFV** (Network Function Virtualization) si occupa di *implementare* le funzioni di rete di ogni slice come Virtual Network Functions (VNF) eseguite su hardware commodity. L'isolamento tra slice è garantito dalla virtualizzazione: ogni VNF vede solo le risorse assegnatele, indipendentemente dalle altre slice sulla stessa macchina fisica.

**SDN** (Software-Defined Networking) si occupa di *governare* il comportamento del traffico all'interno di ogni slice. Una volta definita la slice, il controller SDN monitora e impone i requisiti di QoS installando le flow rule appropriate sugli switch.

### Architettura generica per il Network Slicing

![Architettura generica per il network slicing](images/lezione-26-lab-network-slicing-img-01.jpg)

*Fig. — Architettura generica per il network slicing: le slice (sinistra) poggiano sull'infrastruttura virtualizzata, gestita dal framework MANO (destra).*

Il piano di gestione (MANO) si articola su più livelli:

- **Slicing Management**: punto di ingresso per la definizione delle slice
- **NFVO** (NFV Orchestrator): orchestra le risorse NFV a livello di sistema
- **SDNO** (SDN Orchestrator): orchestra le risorse SDN
- **VNFM** (VNF Manager): gestisce il ciclo di vita di ogni singola VNF (creazione, scaling, terminazione)
- **VIM** (Virtualized Infrastructure Manager): controlla direttamente le risorse virtualizzate (compute, storage, network)
- **SDN Controller**: implementa la logica di forwarding sugli switch

### Il caso d'uso 5G con RAN

In un deployment 5G reale, l'architettura a slice percorre tutta la rete dall'accesso radio al core cloud. La **Radio Access Network (RAN)** è scomposta in tre unità funzionali:

- **Radio Unit (RU)**: l'hardware radio fisico, tipicamente sull'antenna
- **Distributed Unit (DU)**: elabora i livelli MAC e Fisico, distribuita vicino alla RU
- **Centralized Unit (CU)**: gestisce i protocolli di livello superiore (RRC, PDCP) e può essere ospitata nel cloud

Slice diverse (UHD, Phone, Massive IoT, Mission-critical IoT) attraversano la stessa RAN ma mantengono path di dati separati sia nell'Edge Cloud (NFV) sia nel Core Cloud (NFV), con controller SDN dedicati a ogni livello.

---

## Topologia dell'esperimento

L'esperimento implementa il network slicing su scala ridotta usando **ComNetsEmu** come emulatore e **Ryu** come controller SDN. La rete è organizzata come segue.

### Descrizione della rete fisica

![Topologia ad anello con quattro switch e quattro host](images/lezione-26-lab-network-slicing-img-02.jpg)

*Fig. — Topologia ad anello: il percorso superiore (S1→S2→S4) a 10 Mbps è destinato alla slice video; quello inferiore (S1→S3→S4) a 1 Mbps alla slice HTTP. Le linee tratteggiate rappresentano il control plane.*

La topologia è un **anello di quattro switch** (S1, S2, S3, S4) con host alle estremità:

- S1 ha quattro porte: eth1 verso S2, eth2 verso S3, eth3 verso h1, eth4 verso h2
- S4 ha la stessa struttura speculare: eth1 verso S2, eth2 verso S3, eth3 verso h3, eth4 verso h4
- S2 e S3 sono semplicemente di transito: due porte, una verso S1 e una verso S4
- I link superiori (via S2) hanno banda 10 Mbps; quelli inferiori (via S3) hanno banda 1 Mbps

### Obiettivo: il Topology Slicing

L'obiettivo non è realizzare un instradamento tradizionale (dove tutti gli host si raggiungono), ma imporre un **partizionamento rigido** della topologia:

- **Upper Slice**: h1 ↔ h3, interconnessi esclusivamente tramite i link a 10 Mbps (via S2)
- **Lower Slice**: h2 ↔ h4, interconnessi esclusivamente tramite i link a 1 Mbps (via S3)

> [!warning] Isolamento completo
>
> h1 e h2 non possono comunicare tra loro, anche se sono entrambi collegati a S1. Il controller impone che il traffico entrante da eth3 (h1) esca solo da eth1 (verso S2), e il traffico da eth4 (h2) esca solo da eth2 (verso S3). La separazione è logica, non fisica.

![Topologia con separazione Upper Slice e Lower Slice evidenziata](images/lezione-26-lab-network-slicing-img-03.jpg)
*Fig. — Le due slice risultanti: la linea arancione separa l'Upper Slice (S1-eth1/eth3 ↔ S2 ↔ S4-eth1/eth3) dalla Lower Slice (S1-eth2/eth4 ↔ S3 ↔ S4-eth2/eth4).*

Ogni host ha quindi una propria **vista della rete**: dal punto di vista di h1, la rete è semplicemente un collegamento diretto verso h3 a 10 Mbps; h2 e h4 sono invisibili.

---

## Implementazione con Ryu e Mininet

Il laboratorio si basa su due script Python nella directory `comnetsemu/app/realizing_network_slicing/`:

1. `network.py` — definisce la topologia e avvia Mininet
2. `topologyslicing.py` — applicazione Ryu che programma il comportamento degli switch

### network.py: definizione della topologia

Lo script costruisce la topologia usando le API di Mininet. I punti chiave sono la configurazione dei link con limitazione di banda (`TCLink`) e l'assegnazione di DPID univoci agli switch.

```python
host_config = dict(inNamespace=True)
http_link_config = dict(bw=1)   # 1 Mbps
video_link_config = dict(bw=10) # 10 Mbps

# Switch con DPID esplicito
for i in range(4):
    sconfig = {"dpid": "%016x" % (i + 1)}
    self.addSwitch("s%d" % (i + 1), **sconfig)

# Link tra switch: ordine importante per i numeri di porta!
self.addLink("s1", "s2", **video_link_config)  # s1-eth1 ↔ s2-eth1
self.addLink("s2", "s4", **video_link_config)  # s2-eth2 ↔ s4-eth1
self.addLink("s1", "s3", **http_link_config)   # s1-eth2 ↔ s3-eth1
self.addLink("s3", "s4", **http_link_config)   # s3-eth2 ↔ s4-eth2

# Host: h1,h2 su s1; h3,h4 su s4
self.addLink("h1", "s1")  # → s1-eth3
self.addLink("h2", "s1")  # → s1-eth4
self.addLink("h3", "s4")  # → s4-eth3
self.addLink("h4", "s4")  # → s4-eth4
```

> [!tip] Ordine dei link = numeri di porta
>
> In Mininet, le porte di uno switch vengono numerate nell'ordine in cui i link vengono aggiunti. Poiché S1 ottiene prima il link verso S2 (eth1), poi verso S3 (eth2), poi h1 (eth3) e h4 (eth4), le porte hanno esattamente questi numeri. Lo stesso vale per S4. Questo dettaglio è fondamentale per capire la tabella `slice_to_port` in `topologyslicing.py`.

La rete viene avviata con un **controller remoto** (Ryu) in ascolto su `127.0.0.1:6633`, e `autoStaticArp=True` per evitare che i pacchetti ARP broadcast debbano essere gestiti dalla logica di slicing.

### Programmare una rete SDN con Ryu

**Ryu** è un framework per controller SDN scritto in Python. Si basa su un modello a **eventi**: l'applicazione si registra per ricevere notifiche di specifici eventi di rete (arrivo di un pacchetto, connessione/disconnessione di uno switch, cambio di link) e reagisce installando o modificando le flow rule.

![Architettura Ryu: Ryu app sopra il layer Ryu sopra l'OF Switch](images/lezione-26-lab-network-slicing-img-04.jpg)

*Fig. — Stack Ryu: la Ryu app riceve eventi (frecce ③) e invia comandi (frecce ④) al layer Ryu, che comunica con l'OF Switch tramite OpenFlow (frecce ②⑤).*

Una **Ryu app** è una classe Python che:
1. Estende `ryu.base.app_manager.RyuApp`
2. Dichiara la versione di OpenFlow supportata (`OFP_VERSIONS`)
3. Registra handler per specifici eventi con il decoratore `@set_ev_cls`

### topologyslicing.py: la logica del controller

#### Inizializzazione e slice_to_port

Il cuore della logica di slicing è il dizionario `slice_to_port`, che mappa per ogni switch (identificato dal DPID) quale porta di uscita usare a seconda della porta di ingresso:

```python
self.slice_to_port = {
    1: {1: 3, 3: 1, 2: 4, 4: 2},  # S1: eth1↔eth3 (upper), eth2↔eth4 (lower)
    4: {1: 3, 3: 1, 2: 4, 4: 2},  # S4: stesso schema di S1
    2: {1: 2, 2: 1},               # S2: forwarding diretto
    3: {1: 2, 2: 1},               # S3: forwarding diretto
}
```

> [!example] Lettura della tabella per S1
>
> Per S1 (dpid=1): se un pacchetto arriva su eth1 (da S2, upper path), viene inoltrato su eth3 (verso h1). Se arriva su eth3 (da h1), torna su eth1 (verso S2). Specularmente, eth2 (da S3, lower path) ↔ eth4 (verso h2). Il traffico di h1 non può mai raggiungere eth2 o eth4, garantendo l'isolamento.

La separazione è quindi **esclusivamente statistica su S1 e S4**: S2 e S3 non devono fare nulla di speciale, perché non ricevono mai traffico cross-slice (la separazione avviene prima di loro).

#### Gestione degli eventi OpenFlow

La classe gestisce due eventi principali:

**`switch_features_handler`** (evento `EventOFPSwitchFeatures`, fase `CONFIG_DISPATCHER`): viene invocato quando uno switch si connette al controller per la prima volta. Installa la **table-miss flow entry** con priorità 0 e match vuoto (corrisponde a qualsiasi pacchetto): l'azione è inviare al controller con `OFPP_CONTROLLER`. Questa regola garantisce che i primi pacchetti di ogni flusso vengano consegnati all'applicazione.

**`_packet_in_handler`** (evento `EventOFPPacketIn`, fase `MAIN_DISPATCHER`): viene invocato ogni volta che uno switch riceve un pacchetto senza una flow rule corrispondente e lo manda al controller. La logica è:

1. Legge il DPID dello switch e la porta di ingresso
2. Consulta `slice_to_port` per determinare la porta di uscita
3. Installa una **flow rule permanente** con `add_flow` (così i pacchetti successivi dello stesso flusso non passeranno più dal controller)
4. Invia immediatamente il pacchetto corrente con `_send_package`

```python
def _packet_in_handler(self, ev):
    msg = ev.msg
    datapath = msg.datapath
    in_port = msg.match["in_port"]
    dpid = datapath.id

    out_port = self.slice_to_port[dpid][in_port]

    actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
    match = datapath.ofproto_parser.OFPMatch(in_port=in_port)
    self.add_flow(datapath, 1, match, actions)
    self._send_package(msg, datapath, in_port, actions)
```

**`add_flow`** costruisce e invia un messaggio `OFPFlowMod` al datapath (lo switch), che modifica la flow table installando la nuova regola. Da quel momento in poi, i pacchetti che corrispondono al match vengono gestiti direttamente dallo switch senza coinvolgere il controller.

> [!note] Reactive vs Proactive flow installation
>
> Questa applicazione usa l'approccio **reattivo**: le regole vengono installate al primo pacchetto. In alternativa, un controller **proattivo** potrebbe installare tutte le regole all'avvio (`switch_features_handler`) senza aspettare traffico reale. Per questo schema di slicing statico, l'approccio proattivo sarebbe più efficiente poiché elimina la latenza del primo pacchetto.

---

## Esercizi

### Esercizio A: esecuzione e verifica

L'avvio richiede due terminali distinti (il controller e Mininet devono girare in parallelo):

```bash
# Terminale 1 — avvia il controller Ryu
ryu-manager topology_slicing.py

# Terminale 2 — avvia Mininet (richiede sudo)
sudo python3 network.py
```

Una volta avviata la rete, si possono eseguire le verifiche:

**1. Verifica dell'isolamento (ping)**

Il ping deve avere successo solo tra host della stessa slice. Se la slicing funziona correttamente:
- `h1 ping h3` → successo (upper slice)
- `h2 ping h4` → successo (lower slice)
- `h1 ping h2` → fallimento (cross-slice, non esiste path)

**2. Verifica della banda (iperf)**

```bash
# Nel terminale Mininet
mininet> iperf h1 h3   # deve mostrare ~10 Mbps
mininet> iperf h2 h4   # deve mostrare ~1 Mbps
```

**3. Ispezione delle flow rule installate**

```bash
mininet> sh ovs-ofctl dump-flows s1
```

Dopo il primo ping tra h1 e h3, devono essere visibili due flow entry su S1:
- match `in_port=1` → action `output:3`
- match `in_port=3` → action `output:1`

La regola di default (table-miss, priorità 0) ha action `CONTROLLER`, visibile anche prima del ping.

**4. Cattura e analisi dei messaggi OpenFlow**

Per osservare il ciclo completo di comunicazione controller-switch, si può catturare il traffico sulla porta 6633 con tcpdump e analizzarlo in Wireshark:

```bash
# Apri un nuovo terminale
sudo tcpdump -i any port 6633 -w ofcapturedel.pcap

# Cancella le flow rule su s1 per forzare nuovi PACKET_IN
mininet> sh ovs-ofctl del-flows s1 table=0,in_port="s1-eth1"
mininet> sh ovs-ofctl del-flows s1 table=0,in_port="s1-eth3"

# Genera traffico e osserva i messaggi
mininet> h1 ping h3
```

In Wireshark si possono distinguere tre tipi di messaggi OpenFlow rilevanti:
- `PACKET_IN`: lo switch invia il pacchetto al controller (manca la flow rule)
- `PACKET_OUT`: il controller risponde con l'azione immediata per il pacchetto corrente
- `FLOW_MOD`: il controller installa la regola permanente sullo switch

> [!question] Possibili domande d'esame
>
> - Quante coppie PACKET_IN / PACKET_OUT vengono scambiate durante un ping h1↔h3? Perché?
> - Qual è l'azione di default installata da `switch_features_handler`? A cosa serve?
> - Perché il controller non riceve tutti i pacchetti del ping, ma solo i primissimi?
> - Cosa succederebbe se si eliminassero le flow rule di S2 durante una comunicazione attiva?

> [!tip] Risposta alla prima domanda
>
> Per il primo ping (ICMP Echo Request + Reply) ci sono **due scambi** PACKET_IN/PACKET_OUT: uno per il pacchetto dal h1 verso h3 (che imposta la regola su S1, S2, S4 nel percorso di andata) e uno per la risposta da h3 verso h1. I ping successivi non generano PACKET_IN perché le flow rule sono già installate.

---

### Esercizio B: service chain con un firewall

La **service chain** (o *function chaining*) è il meccanismo con cui il traffico viene deviato attraverso una sequenza di funzioni di rete prima di raggiungere la destinazione. Nell'esercizio B si simula l'inserimento di un firewall (S5) nel percorso dell'upper slice.

![Topologia Esercizio B con switch S5 come firewall inline collegato a S2](images/lezione-26-lab-network-slicing-img-05.jpg)

*Fig. — Topologia Esercizio B: S5 è inserito tra S2-eth3 e S2-eth4, creando un percorso inline per filtrare il traffico dell'upper slice.*

Il percorso fisico del pacchetto diventa: h1 → s1 → **s2-eth1** → **s2-eth3** → **s5-eth1** → **s5-eth2** → **s2-eth4** → **s2-eth2** → s4 → h3.

**Procedura:**

1. **Modifica `network.py`**: aggiungere lo switch S5 e due link verso S2
   ```python
   self.addSwitch("s5", **{"dpid": "%016x" % 5})
   self.addLink("s2", "s5")  # s2-eth3 ↔ s5-eth1
   self.addLink("s5", "s2")  # s5-eth2 ↔ s2-eth4
   ```

2. **Non modificare `topologyslicing.py`**: il controller gestirà S5 con le regole di table-miss (invia al controller), ma noi installeremo le regole manualmente con `ovs-ofctl`.

3. Avviare controller e Mininet, verificare la connettività h1↔h3 (deve funzionare, S5 viene gestito con il comportamento di default).

4. **Terminare il controller** con Ctrl-C.

5. **Modificare manualmente le flow rule su S2** per redirigere il traffico attraverso S5:
   ```bash
   # Traffico in arrivo da s1 (eth1) → manda a s5 (eth3) invece che a s4 (eth2)
   mininet> sh ovs-ofctl add-flow s2 in_port=1,priority=10,actions=output:3
   # Traffico di ritorno da s5 (eth4) → manda verso s4 (eth2)
   mininet> sh ovs-ofctl add-flow s2 in_port=4,priority=10,actions=output:2
   ```

6. **Aggiungere flow rule su S5** per i tre scenari richiesti:

   **a) Tutto il traffico è permesso (forwarding semplice)**
   ```bash
   mininet> sh ovs-ofctl add-flow s5 in_port=1,priority=10,actions=output:2
   mininet> sh ovs-ofctl add-flow s5 in_port=2,priority=10,actions=output:1
   ```

   **b) Blocca i pacchetti ICMP** (ping non funziona, iperf TCP sì)
   ```bash
   mininet> sh ovs-ofctl add-flow s5 icmp,priority=20,actions=drop
   mininet> sh ovs-ofctl add-flow s5 in_port=1,priority=10,actions=output:2
   mininet> sh ovs-ofctl add-flow s5 in_port=2,priority=10,actions=output:1
   ```

   **c) Blocca il traffico TCP** (iperf non funziona, ping sì)
   ```bash
   mininet> sh ovs-ofctl add-flow s5 tcp,priority=20,actions=drop
   mininet> sh ovs-ofctl add-flow s5 in_port=1,priority=10,actions=output:2
   mininet> sh ovs-ofctl add-flow s5 in_port=2,priority=10,actions=output:1
   ```

**Comandi utili per l'esercizio B:**

| Comando | Funzione |
|---|---|
| `ovs-ofctl del-flows <sw> in_port=<p>` | Rimuove tutte le regole con quella porta in ingresso |
| `ovs-ofctl del-flows <sw> <proto>` | Rimuove regole per protocollo (icmp, tcp, udp…) |
| `ovs-ofctl add-flow <sw> <match>,priority=<p>,actions=<a>` | Aggiunge una flow rule |
| `sudo tcpdump -i s5-eth1` | Sniffa pacchetti sull'interfaccia virtuale di s5 |

> [!note] Priority nelle flow rule
>
> OpenFlow sceglie la regola con **priorità più alta** tra quelle che fanno match su un pacchetto. Impostare la regola di drop a priorità 20 e il forwarding generico a 10 garantisce che i pacchetti ICMP (o TCP) vengano bloccati prima di essere inoltrati. L'ordine di inserimento non conta, conta solo la priorità numerica.

> [!question] Possibili domande d'esame
>
> - Come si implementa una service chain senza modificare il controller SDN?
> - Qual è la differenza tra un approccio di slicing basato su porte fisiche e uno basato su header di pacchetto (es. VLAN, IP)?
> - Perché nella topologia con S5 è necessario terminare il controller prima di installare le regole manuali?
> - Come si verificherebbe che i pacchetti TCP vengono effettivamente droppati da S5 e non semplicemente non raggiungono S4?
