# Network Slicing con SDN

![[exam_mod2_network_slicing.jpg]]

## Contesto: il 5G e la necessità del Network Slicing

Il 5G non è semplicemente un incremento di velocità rispetto al 4G: è una riprogettazione fondamentale dell'architettura di rete, motivata dalla coesistenza di tre categorie di servizio con requisiti radicalmente diversi tra loro:
- **mMTC (massive Machine Type Communications)**: comunicazione tra un numero elevatissimo di dispositivi (fino a 200.000/km²), IoT a bassa potenza. I requisiti dominanti sono la massima efficienza energetica e la scalabilità.
- **URLLC (Ultra-Reliable Low-Latency Communications)**: servizi che richiedono simultaneamente bassissima latenza (≤ 5 ms o ≤ 1 ms) e alta affidabilità (es. guida autonoma, controllo industriale).
- **eMBB (Enhanced Mobile Broadband)**: servizi ad alta densità di dati (streaming 4K/8K, realtà aumentata), dove il requisito primario è l'alta capacità di trasmissione.

La coesistenza di questi tre profili rende impossibile ottimizzare un'unica rete per tutti contemporaneamente. La soluzione è il **network slicing**: sulla stessa infrastruttura fisica vengono create più reti virtuali logiche separate (*slice*), ognuna ottimizzata per il proprio caso d'uso, con le proprie caratteristiche di QoS, banda, latenza e isolamento. La separazione logica garantisce che i requisiti di una slice non vengano degradati dalle altre.

## Il concetto di Network Slicing

Il network slicing sfrutta le risorse dell'infrastruttura fisica per creare multiple **sotto-reti virtuali** (slice), ciascuna delle quali si comporta come una rete indipendente.

Senza SDN, separare il traffico richiederebbe VLAN, configurazione manuale di ogni switch, o hardware dedicato. Con **SDN** (Software-Defined Networking), è sufficiente un controller centralizzato che installa le regole di forwarding appropriate per ogni flusso, realizzando lo slicing in software.

## Topologia dell'esperimento

L'esperimento implementa il network slicing usando l'emulatore **ComNetsEmu** e il controller SDN **Ryu** (scritto in Python).

La topologia è un **anello di quattro switch** (S1, S2, S3, S4) con quattro host (h1, h2, h3, h4).
L'obiettivo è imporre un **partizionamento rigido** della topologia per creare due slice indipendenti:
- **Upper Slice**: h1 ↔ h3, interconnessi esclusivamente tramite i link a 10 Mbps (il percorso via S2).
- **Lower Slice**: h2 ↔ h4, interconnessi esclusivamente tramite i link a 1 Mbps (il percorso via S3).

## Implementazione con Ryu: TrafficSlicing

Il cuore dell'implementazione del Network Slicing nel codice Python per il controller Ryu è il dizionario `slice_to_port`. Per ogni switch (identificato dal `dpid`) e per ogni porta di ingresso (`in_port`), specifica la porta di uscita:

```python
self.slice_to_port = {
    1: {1: 3, 3: 1, 2: 4, 4: 2},  # S1 (dpid=1)
    4: {1: 3, 3: 1, 2: 4, 4: 2},  # S4 (dpid=4)
    2: {1: 2, 2: 1},               # S2 (dpid=2)
    3: {1: 2, 2: 1},               # S3 (dpid=3)
}
```

Il gestore `_packet_in_handler` viene chiamato dal controller Ryu ogni volta che uno switch riceve un pacchetto che non ha una flow entry corrispondente (*packet-in*). Il controller legge il `dpid` dello switch e la porta di ingresso, cerca nel dizionario la porta di uscita, installa una **flow rule** nello switch (con `self.add_flow`) e forwarda il pacchetto:

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

Da quel momento in poi, i pacchetti che corrispondono al match vengono gestiti direttamente dallo switch senza coinvolgere il controller. L'isolamento è garantito logicamente dal partizionamento delle porte su S1 e S4.
