# Network Function Virtualization

La **Network Function Virtualization** (NFV) rappresenta uno dei cambiamenti di paradigma più significativi nell'ingegneria delle reti degli ultimi anni. L'idea fondamentale è semplice ma rivoluzionaria: spostare le funzioni di rete — firewall, bilanciatori di carico, gateway — dall'hardware proprietario dedicato a software eseguito su infrastruttura virtualizzata generica. 

---

## NFV: l'idea fondamentale

### Decoupling tra funzioni e hardware

Il principio cardine di NFV è il **disaccoppiamento** (*decoupling*) tra le funzioni di rete e l'hardware su cui girano. Le funzioni non sono più implementate in appliance fisiche dedicate, ma come **software** eseguito su infrastruttura virtualizzata standard (macchine virtuali o container su server COTS — *Commercial Off-The-Shelf*).

> [!definition] VNF — Virtualized Network Function
>
> Una **Virtualized Network Function** (VNF) è l'implementazione software di una funzione di rete tradizionalmente realizzata in hardware dedicato (firewall, load balancer, NAT, ecc.), eseguita su risorse virtualizzate (VM o container).

---

## NFV — Forwarding Graph

![[exam_mod2_nfv_forwarding_graph.jpg]]

Questo schema rappresenta il concetto di **VNF Forwarding Graph** (VNF-FG), che è il modo in cui NFV formalizza un servizio di rete end-to-end.

**L'idea fondamentale di NFV:** invece di implementare funzioni di rete (firewall, NAT, load balancer, media gateway) in hardware proprietario dedicato, NFV le implementa come software — chiamate **VNF** (*Virtualized Network Functions*) — eseguito su infrastruttura hardware commodity (server COTS). Il decoupling tra funzione e hardware porta flessibilità, scalabilità e riduzione dei costi.

**Il Forwarding Graph:** un servizio di rete non è una singola funzione, ma una **composizione di funzioni** applicate in sequenza al traffico. Il grafo mostra:
- Il traffico entra da **End Point A**, passa attraverso **VNF-1**, poi attraverso il sotto-grafo **VNF-FG-2** (che a sua volta compone internamente VNF-2A → VNF-2B e VNF-2C in parallelo), poi attraverso **VNF-3**, e infine raggiunge **End Point B**.
- I link logici (tratteggiati) rappresentano connettività virtuale: due VNF sono logicamente connesse, ma possono fisicamente trovarsi su macchine diverse.

**I grafi sono nidificati:** VNF-FG-2 è esso stesso un sotto-grafo all'interno del grafo principale. Questo consente la riusabilità: VNF-FG-2 può essere istanziato in altri servizi senza ridefinirlo.

**L'infrastruttura fisica (NFVI):** le VNF girano su nodi fisici chiamati **NFVI-PoP** (*Network Function Virtualization Infrastructure Point of Presence*). Sono server COTS distribuiti geograficamente, interconnessi da una rete di trasporto fisica. La **Virtualization Layer** (hypervisor o container engine) astrae le risorse fisiche e consente a più VNF di condividere lo stesso hardware.

**Il problema del VNF placement:** dato il grafo logico del servizio, occorre decidere dove deployare fisicamente ogni VNF nell'infrastruttura. Questo è un problema di ottimizzazione NP-hard che considera: latenza end-to-end, capacità dei nodi, banda dei link, costi di deployment, requisiti di QoS per ogni slice di rete.

---

## NFV — Management and Orchestration

![[exam_mod2_nfv_mano.jpg]]

Questo schema mostra il framework di **gestione e orchestrazione NFV** standardizzato da ETSI, che è il "piano di controllo" dell'ecosistema NFV.

**NFV Orchestrator (NFVO):** è il componente di più alto livello. Ha due responsabilità principali:
1. **Network services orchestration**: gestisce il ciclo di vita dei **Network Service (NS)** end-to-end, ovvero istanzia, aggiorna e termina l'intero VNF Forwarding Graph. Può istanziare nuovi VNFM se necessario.
2. **Resource orchestration**: gestisce le risorse globali dell'NFVI, allocandole ai servizi in base alle policy e ai requisiti di QoS.
Il NFVO mantiene due repository: il **NS Catalog** (template dei servizi di rete come Network Service Descriptor) e il **VNF Catalog** (descrittori di ogni VNF, i VNFD).

**VNF Manager (VNFM):** gestisce il **ciclo di vita delle istanze VNF** singole:
- **Istanziazione**: crea una nuova istanza VNF su una VM o container nell'NFVI.
- **Scaling**: aumenta o riduce la capacità di una VNF (scaling out/in orizzontale, scaling up/down verticale) in base al carico.
- **Healing**: rileva e gestisce i fault delle VNF (auto-healing o assistito).
- **Terminazione**: distrugge l'istanza quando non serve più.
Il VNFM comunica con il NFVO tramite **Or-Vnfm** e con il VIM tramite **Vi-Vnfm** (o **Ve-Vnfm** verso le VNF stesse).

**Virtualized Infrastructure Manager (VIM):** controlla e gestisce le risorse fisiche e virtuali dell'NFVI (compute, storage, network). Piattaforme IaaS come **OpenStack** fungono da VIM. Il VIM alloca VM o container alle VNF, configura la rete virtuale (vSwitch, VLAN), e monitora l'utilizzo delle risorse. Un MANO può orchestrare più VIM distribuiti geograficamente.

**Le interfacce di riferimento:**
- **Or-Vi** (NFVO → VIM): l'orchestratore può richiedere risorse direttamente al VIM.
- **S-Ma**: collega sistemi OSS/BSS dell'operatore (Operations Support System / Business Support System) al MANO per l'integrazione con i sistemi aziendali.

> [!note] Implementazioni open source
>
> Le principali implementazioni open source del MANO sono **OSM** (*Open Source MANO*, promossa da ETSI) e **ONAP** (*Open Network Automation Platform*, Linux Foundation). Entrambe sono usate nelle reti 5G commerciali.
