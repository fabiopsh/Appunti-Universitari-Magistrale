# 04 - Reti Mobili Software Virtualizzate e Slicing

## Reti Mobili Software Virtualizzate e Slicing

### 1. Software Defined Networking (SDN) ed Architettura

#### Introduzione
Il **Software Defined Networking** è un paradigma architetturale che separa nettamente il **piano di controllo** (*control plane*) dal **piano dati** (*data plane*). Questa astrazione abilita configurazioni e operazioni dinamiche a livello programmatico, eliminando la rigidità dei dispositivi tradizionali.

### Motivazioni ed Evoluzione del Traffico
Le reti tradizionali faticano a gestire la complessità e la variabilità del traffico moderno (cloud, big data, IoT). La domanda è caratterizzata da dinamiche *time-variant*, *spatially dynamic* e *application-sensitive*.
- **Dominio del traffico East-West**: Oltre il 70% del traffico nei data center è interno tra server, mentre le architetture classiche a tre livelli erano ottimizzate per traffico North-South (client-server).
- **Limiti strutturali**: Le reti convenzionali soffrono di un'architettura statica e frammentata, incoerenza delle policy (enforced localmente) e vendor lock-in a causa di hardware proprietario con interfacce chiuse.

![Diagramma del traffico East-West nei data center: percorsi statici e dinamici tra server, con connettività East-West come problema principale](images/lezione-15-lab-sdn-architecture-img-01.jpg)
*Fig. 1 — Traffico East-West nei data center.*

### La Separazione tra Data Plane e Control Plane
- **Data Plane (Forwarding)**: smistamento istantaneo dei pacchetti su scala temporale breve (*fast timescales*).
- **Control Plane (Routing)**: determinazione dei percorsi da sorgente a destinazione su scala temporale più lunga (*slow timescales*).

Nel routing tradizionale, l'unico "knob" per il traffic engineering sono i pesi dei link: non è possibile forzare percorsi specifici senza alterare globalmente il routing, fare load balancing su più percorsi uguali, o differenziare per flusso a parità di destinazione.

![Diagramma di traffic engineering con routing tradizionale: topologia con nodi u, v, w, x, y, z e pesi sui link, evidenziando l'impossibilità di controllare percorsi specifici](images/lezione-15-lab-sdn-architecture-img-02.jpg)
*Fig. 2 — Limiti del routing tradizionale.*

### Il Paradigma SDN: Centralizzazione Logica
SDN sposta la logica di controllo in un controller remoto centralizzato logicamente, calcolando le forwarding table globalmente in modo consistente:
$$ \mathcal{F}: S(t) \rightarrow \{T_1, T_2, \ldots, T_n\} $$
dove $S(t)$ include topologia, stato e policy.

![Architettura SDN con controller remoto: il Remote Controller calcola e installa le forwarding table nei router, con control plane e data plane separati](images/lezione-15-lab-sdn-architecture-img-03.jpg)
*Fig. 3 — Modello SDN con Remote Controller.*

I quattro pilastri:
1. **Generalized flow-based forwarding**.
2. **Separazione control plane / data plane**.
3. **Control plane esterno agli switch**.
4. **Programmabilità** tramite applicazioni.

### Architettura SDN a Tre Livelli
![Architettura SDN a tre livelli: network-control applications (in alto), SDN Controller con northbound e southbound API (al centro), SDN-controlled switches (in basso)](images/lezione-15-lab-sdn-architecture-img-04.jpg)
*Fig. 4 — L'architettura SDN a tre livelli.*

1. **Data-plane switches**: dispositivi commodity che implementano generalized forwarding in hardware. L'API (es. OpenFlow) definisce il controllo.
2. **SDN Controller (Network OS)**: mantiene stato globale, interagisce via NorthBound API con le app e via SouthBound API con gli switch. Fisicamente distribuito per fault-tolerance.
3. **Network-control applications**: il "cervello" unbundled (sviluppato da terzi) che implementa routing, firewall, ecc.

***

### SDN Data Plane e Astrazione Match-Action
Il forwarding generalizzato permette che qualsiasi campo header (L2, L3, L4) sia usato per il **match**, associandolo a un'**azione** (forward, drop, modify, send to controller).
Questa astrazione unifica router, switch, firewall e NAT.

> [!example] Esempi di regole OpenFlow
> - **IP Forward**: `IP Dst = 51.6.0.8` → `forward(port 6)`
> - **Firewall**: `TCP dst-port = 22` → `drop`

#### OpenFlow Switch
Uno switch OpenFlow comunica col controller via un canale sicuro (OpenFlow Channel) e processa pacchetti usando **Flow Tables** organizzate in **Pipeline**.
$$ \text{Packet in} \rightarrow [\text{Table 0}] \rightarrow [\text{Table 1}] \rightarrow \cdots \rightarrow [\text{Table N}] \rightarrow \text{Packet out} $$
Se non c'è match, la *table-miss entry* può redirigere al controller. Le **Group Tables** permettono azioni su più porte (multicast/ALL, load balancing/SELECT).

![Architettura interna di un OpenFlow Switch: porte, pipeline di flow table, group table, e canale OpenFlow verso il controller](images/lezione-15-lab-sdn-architecture-img-06.jpg)
*Fig. 5 — L'OpenFlow Switch.*

***

### SDN Control Plane
Il controller gestisce lo stato di rete, comunica via OpenFlow e offre astrazioni (es. SAL in OpenDaylight o Intent Framework in ONOS).
Messaggi principali di OpenFlow: `features`, `configure`, `modify-state (FlowMod)`, `packet-out` (Controller→Switch) e `packet-in`, `flow-removed`, `port-status` (Switch→Controller).

#### Path Computation e Topology Discovery
Inizialmente le table sono vuote. Al primo pacchetto (*table-miss*), lo switch invia un `Packet-In`. Il controller calcola il percorso e usa `FlowMod` per installare regole procedendo **in ordine inverso** dalla destinazione alla sorgente.

![Diagramma di path computation: un pacchetto da A a B genera un Packet-In verso il controller, che risponde con FlowMod per popolare le flow table di S1 e S2](images/lezione-15-lab-sdn-architecture-img-07.jpg)
*Fig. 6 — Path computation reattiva.*

Al boot, avviene l'**Inizializzazione** con scambio Feature Request/Reply. Poi, la topologia viene scoperta tramite **LLDP** (Link Layer Discovery Protocol, `0x88cc`).
1. Il controller invia *Packet-Out* con LLDP.
2. Lo switch forwarda.
3. Lo switch adiacente riceve e manda *Packet-In* al controller con metadati.
Il controller deduce i link fisici.

![Struttura del frame LLDP: campi Chassis ID, Port ID, Time to Live, End of LLDPDU](images/lezione-15-lab-sdn-architecture-img-09.jpg)
*Fig. 7 — Struttura del frame LLDP.*

***

## 2. SDN Applications e P4 Language

### B4: La WAN SDN di Google
Le WAN tradizionali hanno link costosi sottoutilizzati (30-40%) a causa dell'overprovisioning. **B4** è la rete inter-datacenter SDN di Google che ottimizza il traffico "bulk" elastico (replicazioni) per avvicinarsi al 100% di utilizzo.

![Mappa della rete B4 — connessioni WAN tra i datacenter Google nel mondo](images/lezione-16-lab-sdn-applications-e-p4-language-img-01.jpg)
*Fig. 8 — La rete B4 mondiale.*

La migrazione è avvenuta a stadi, mantenendo **BGP** per la raggiungibilità di base ma delegando al **Central TE Server** (SDN) l'ottimizzazione del traffico e il routing tramite **forwarding multipath** su Tunnel logici IP-in-IP.

![Architettura del Traffic Engineering in B4](images/lezione-16-lab-sdn-applications-e-p4-language-img-07.jpg)
*Fig. 9 — Il TE Server riceve Flow Groups e installa Tunnels tramite controller OpenFlow.*

### Il Linguaggio P4
OpenFlow ha il limite di proporre tabelle hardware rigide. **P4** (*Programming Protocol-Independent Packet Processors*) permette di **programmare il data plane**, definendo header e tabelle stesse.

Un programma P4 contiene:
1. **Parser**: macchina a stati per estrarre header.
2. **Match-Action Pipeline**: logica definita dal programmatore.
3. **Deparser**: serializzazione.

![Flusso di compilazione di un programma P4 verso il target](images/lezione-16-lab-sdn-applications-e-p4-language-img-09.jpg)
*Fig. 10 — Compilazione P4 verso target diversi, interagendo con P4Runtime.*

```p4
parser MyParser(packet_in packet, out headers_t hdr, inout metadata_t meta) {
    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.eth_type) {
            0x0800: parse_ipv4;
            default: accept;
        }
    }
    state parse_ipv4 { packet.extract(hdr.ipv4); transition accept; }
}
```

### Service Function Chaining (SFC)
Comporre funzioni (Firewall, IDS) senza ricablare la rete fisica. SDN permette definizioni logiche dinamiche, deviando il traffico tramite *Service Classifiers*.

![Service Function Chaining con SDN — flusso del traffico attraverso la catena](images/lezione-16-lab-sdn-applications-e-p4-language-img-11.jpg)
*Fig. 11 — Service Function Chaining.*

***

## 3. Network Function Virtualization (NFV)

### Dal Middlebox all'Appliance Software
I middlebox hardware (Firewall, NAT) rendono rigida la rete. **NFV** si basa sul **decoupling** (disaccoppiamento) tra funzioni e hardware proprietario, trasformandole in **VNF** (*Virtualized Network Function*) in esecuzione su server commodity (COTS) come Macchine Virtuali (VM) o Container (CNF).

![Confronto tra il modello tradizionale (appliance approach) e il modello virtualizzato (virtual appliance approach)](images/lezione-20-lab-network-function-virtualization-img-01.jpg)
*Fig. 12 — Modello tradizionale vs NFV.*
Benefici: Flessibilità, Scalabilità elastica (scaling up/down), Innovazione rapida.

### Network Function Forwarding Graph (NF-FG)
Un servizio end-to-end è un grafo logico (VNF-FG) composto da VNF connesse da link virtuali, che l'orchestratore mappa su reti infrastrutturali (*NFVI-PoP*). Il problema del *VNF Placement* consiste nel trovare l'allocazione ottima per ridurre latenza ed overhead.

![Network Service in NFV: il Network Function Forwarding Graph con endpoint e VNF collegate da link logici](images/lezione-20-lab-network-function-virtualization-img-04.jpg)
*Fig. 13 — VNF-FG.*

### Architettura ETSI NFV-MANO
![NFV Reference Architectural Framework con NFVI, VNF, EMS, NFVO, VNFM, VIM e interfacce di riferimento](images/lezione-20-lab-network-function-virtualization-img-07.jpg)
*Fig. 14 — Architettura di riferimento NFV.*

L'infrastruttura è tripartita:
1. **NFVI** (Infrastructure): compute, hypervisor, networking. Switch virtuali come Open vSwitch (OVS) gestiscono le reti virtuali.
2. **VNF**: Le funzioni instanziate.
3. **NFV-MANO** (Management and Orchestration):
   - **NFVO** (Orchestrator): gestisce i *Network Services*.
   - **VNFM** (Manager): gestisce il ciclo di vita (scaling, healing) di singole VNF.
   - **VIM** (Virtualized Infrastructure Manager): gestisce l'hardware fisico sottostante (es. OpenStack).

> [!example] Network Service Descriptor (NSD)
> Formato (es. JSON) che definisce come le VNF compongono il servizio e i link virtuali che le legano.

***

## 4. Emulazione con ComNetsEmu e Mininet

**Mininet** emula host, switch e link in un solo kernel usando i **network namespace** Linux (per l'isolamento degli stack di rete) e interfacce **veth pairs**.
**ComNetsEmu** estende Mininet usando *container Docker* per emulare host SDN/NFV (Docker-in-Docker).

![Diagramma dei namespace con firefox e httpd, virtual Ethernet pairs e Software Switch](images/lezione-21-lab-network-emulator-con-comnetsemu-img-04.jpg)
*Fig. 15 — Namespace isolati in Mininet connessi via veth.*

### Gestione da CLI
I comandi Mininet e `tc` (Traffic Control) permettono test avanzati:
```bash
mininet> h1 ping h2
mininet> iperf h1 h2
h1 tc qdisc add dev h1-eth0 root netem delay 100ms 10ms # Configura ritardo
```

### Esempio: Echo Server in Python
Topologia con due host Docker: `h1` (bash client) e `h2` (echo_server).
```python
**topology.py (Estratto)**
h1 = net.addDockerHost("h1", dimage="dev_test", ip="10.0.0.1")
h2 = net.addDockerHost("h2", dimage="echo_server", ip="10.0.0.2")
net.addLink(switch1, h1, bw=10, delay="10ms")
```
Server testabile con Netcat:
```bash
h1:/# nc 10.0.0.2 65000
```

***

## 5. Multi-Access Edge Computing (MEC)

MEC porta le risorse elaborative ai margini (Edge) per avvicinarle all'utente finale (Base Station, Access Point, micro-data center).
Questo approccio ottimizza la **Formula di Mathis** per il throughput TCP, che dipende inversamente dal Round Trip Time ($RTT$) e dalla perdita di pacchetti ($P_{loss}$).
$$ \text{Throughput} \le \frac{MSS}{RTT \sqrt{P_{loss}}} $$

![Confronto CDF di latenza: cloudlet vicino vs. lontano per tre applicazioni](images/lezione-22-lab-multi-access-edge-computing-mec-img-02.jpg)
*Fig. 16 — CDF: La prossimità (cloudlet vicino) abbatte sensibilmente la latenza.*

### Benefici e Scenari
Oltre al calo di latenza, MEC supporta video analytics locali (non saturando la WAN), funziona da IoT Gateway intelligente e facilita le garanzie privacy.

![Architettura del MEC Framework con livelli di gestione](images/lezione-22-lab-multi-access-edge-computing-mec-img-06.jpg)
*Fig. 17 — Il MEC Framework ETSI.*

### MEC API: Informazioni Locali e Steering
Il MEC framework offre API per consumare servizi di rete in loco:
- **RNIS API**: Condizioni radio, Cell ID (per ottimizzazione video/mobilità).
- **Location API**: Geolocalizzazione e Localizzazione logica.
- **MTS (MultiAccess Traffic Steering) API**: Gestisce il trade-off fondamentale tra *Split traffic* (più bandwidth unendo N link) e *Duplicate traffic* (più affidabilità, ridondando su N link per URLLC).

![Tabella MTS: data rate e affidabilità al variare del numero di link N](images/lezione-22-lab-multi-access-edge-computing-mec-img-07.jpg)
*Fig. 18 — Trade-off MTS tra Throughput (Split) e Affidabilità (Duplicate).*

***

## 6. Network Slicing nel 5G ed Esercizio Pratico

Il 5G accorpa requisiti antitetici: **mMTC** (massiva densità IoT), **URLLC** (latenza ms e affidabilità estrema), **eMBB** (altissima banda).
La soluzione è il **Network Slicing**: creare reti virtuali end-to-end con QoS garantita sulla stessa rete fisica. NFV crea le funzioni, SDN gestisce l'isolamento dei flussi.

![Architettura generica per il network slicing](images/lezione-26-lab-network-slicing-img-01.jpg)
*Fig. 19 — Livelli architetturali per il slicing.*

### Esperimento: Topology Slicing con Ryu
Usando ComNetsEmu, realizziamo un anello di 4 switch (S1-S4) e partizioniamo:
- **Upper Slice**: h1 ↔ h3 su path a 10Mbps (via S2).
- **Lower Slice**: h2 ↔ h4 su path a 1Mbps (via S3).

![Topologia con separazione Upper Slice e Lower Slice evidenziata](images/lezione-26-lab-network-slicing-img-03.jpg)
*Fig. 20 — Separazione Upper/Lower slice.*

**Il Controller Ryu (`topologyslicing.py`)**:
Il partizionamento avviene mappando staticamente le porte in `slice_to_port` per gli switch di ingresso S1 e S4, garantendo un rigido isolamento.
Quando arriva il primo pacchetto (`EventOFPPacketIn`), Ryu estrae `in_port`, legge `slice_to_port` e fissa la flow rule permanente sullo switch con un `OFPFlowMod` via OpenFlow.

```python
out_port = self.slice_to_port[dpid][in_port]
actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
match = datapath.ofproto_parser.OFPMatch(in_port=in_port)
self.add_flow(datapath, 1, match, actions) # Installa per i successivi
self._send_package(msg, datapath, in_port, actions) # Inoltra l'attuale
```

### Esercizio B: Service Chain Firewall
Inserendo manualmente uno switch S5 come Firewall tra S2-eth3 e S2-eth4:
```bash
**S2 redirige l'Upper slice verso S5**
mininet> sh ovs-ofctl add-flow s2 in_port=1,priority=10,actions=output:3
**S5 blocca il traffico ICMP tramite priorità OpenFlow**
mininet> sh ovs-ofctl add-flow s5 icmp,priority=20,actions=drop
mininet> sh ovs-ofctl add-flow s5 in_port=1,priority=10,actions=output:2
```
Il traffico con match TCP/ICMP verrà bloccato prima dell'azione default generica grazie alla **priority** maggiore.
