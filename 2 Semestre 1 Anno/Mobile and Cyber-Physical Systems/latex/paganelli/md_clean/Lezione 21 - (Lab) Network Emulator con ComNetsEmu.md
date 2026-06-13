---
tags:
  - università/mobile-and-cyber-physical-systems
  - network-emulator
  - mininet
  - comnetsemu
  - sdn
  - docker
  - laboratorio
data: 2026-04-14
lezione: "Lab - Network Emulator con ComNetsEmu"
professore: "Federica Paganelli"
---

# Laboratorio: Network Emulator con ComNetsEmu

Questa lezione di laboratorio introduce **ComNetsEmu**, un emulatore di reti progettato per sperimentare ambienti [[SDN]] ([[Software-Defined Networking]]) e [[NFV]] ([[Network Function Virtualization]]) su un singolo computer. Prima di avviare gli esperimenti è necessario installare e configurare l'ambiente: questa guida accompagna passo per passo dall'installazione fino all'esecuzione del primo esempio funzionante.

---

## Cos'è ComNetsEmu

**ComNetsEmu** è un ambiente software-based progettato come *testbed* e emulatore di reti, sviluppato da TU Dresden e Università di Trento come progetto open source. Il suo obiettivo principale è rendere possibile l'emulazione di scenari significativi di SDN e NFV su un singolo laptop, abbassando la barriera di accesso alla sperimentazione su reti programmatiche.

> [!info] Caratteristiche chiave
>
> - **Semplicità**: setup leggero, rapido e automatizzato
> - **Riproducibilità e condivisibilità**: usa template human-friendly (Vagrantfile)
> - **Tecnologie state-of-the-art senza complessità aggiuntiva**: permette di testare concetti avanzati in modo accessibile
> - **Estensibilità**: progettato per essere ampliato con nuovi esempi e applicazioni

ComNetsEmu è costruito come un'estensione di **Mininet**, il popolare emulatore di reti per Linux, al quale aggiunge il supporto per container Docker come unità di elaborazione virtuali. La combinazione di Mininet (per l'emulazione del piano dati) e Docker (come soluzione NFVI) in un unico framework integrato è il tratto distintivo di ComNetsEmu.

---

## Fondamenti: Mininet

Prima di installare ComNetsEmu è utile capire come funziona Mininet, su cui si basa.

**Mininet** è un emulatore di rete che fa girare un insieme di host, switch, router e link su un singolo kernel Linux. Utilizza la virtualizzazione leggera per fare sembrare una macchina singola come una rete completa. Supporta [[OpenFlow]] per l'emulazione di reti SDN.

![Sito ufficiale di Mininet con navigazione e documentazione](images/lezione-21-lab-network-emulator-con-comnetsemu-img-01.jpg)
*Fig. — Il sito ufficiale di Mininet (http://mininet.org/) con la sua documentazione, walkthrough e API di riferimento.*

### Come funziona internamente Mininet

Gli host di Mininet sono **processi** che condividono lo stesso kernel OS, gli stessi PID e file system. Ogni host ha però uno stack di rete **indipendente**, realizzato tramite i *network namespace* di Linux.

> [!definition] Network Namespace
>
> Un *network namespace* fornisce uno stack di rete isolato. I processi al suo interno hanno il proprio set di risorse di rete: interfacce virtuali, tabelle ARP, tabelle di routing. Un nodo virtuale di rete è semplicemente una shell in un network namespace.

### Topologie in Mininet

Una topologia Mininet è composta da entità come `Host`, `Switch`, `Controller` e `Link`. È possibile creare topologie custom tramite script Python estendendo la classe `mininet.topo.Topo` e sovrascrivendo il metodo `build()`.

Il comando più semplice per avviare Mininet con una topologia di default è:

```bash
sudo mn
```

Questo inizializza una topologia predefinita e lancia la CLI interattiva.

#### Esempio: SimpleSwitchTopology

![Schema della SimpleSwitchTopology con uno switch centrale e N host foglia](images/lezione-21-lab-network-emulator-con-comnetsemu-img-02.jpg)
*Fig. — SimpleSwitchTopology: uno switch centrale connesso a N host tramite link individuali.*

> [!tip] Principali classi e metodi Mininet
>
> - `Topo.addSwitch()` — aggiunge uno switch alla topologia
> - `Topo.addHost()` — aggiunge un host alla topologia
> - `Topo.addLink()` — aggiunge un link bidirezionale
> - `Mininet.start()` / `Mininet.stop()` — avvia/ferma la rete
> - `Mininet.pingAll()` — testa la connettività fra tutti i nodi
> - Documentazione API: http://mininet.org/api/annotated.html

### CLI di Mininet

La **CLI** di Mininet è uno strumento interattivo molto utile durante gli esperimenti. Si invoca passando l'oggetto rete al costruttore `CLI(net)`. I comandi principali sono:

```
mininet> net             # mostra la topologia
mininet> pingall         # testa la connettività tra tutti i nodi
mininet> h1 ping h2      # ping da h1 verso h2
mininet> h1 ip a         # mostra le interfacce di h1
mininet> iperf h1 h2     # misura il throughput tra h1 e h2
mininet> links           # mostra tutti i link attivi
mininet> h1 ip link show type veth   # mostra le interfacce veth di h1
mininet> sh ovs-vsctl show           # mostra la configurazione del virtual switch
```

### Veth pairs e piano dati

Ogni host Mininet può avere un'interfaccia Ethernet virtuale chiamata **veth** (*Virtual Ethernet Device*). I dispositivi veth vengono sempre creati in coppie interconnesse: i pacchetti trasmessi su un'interfaccia sono immediatamente ricevuti dall'altra. Si può pensare a un veth come a un cavo Ethernet reale che collega due dispositivi.

![Schema delle veth pairs con due host in namespace separati collegati tramite un software switch](images/lezione-21-lab-network-emulator-con-comnetsemu-img-03.jpg)
*Fig. — Architettura delle veth pairs: Host 1 e Host 2 hanno ciascuno il proprio network namespace con interfacce veth collegate tramite un software switch nel Root Namespace.*

Le coppie veth possono essere connesse a un virtual switch (ad esempio **OpenvSwitch**). I parametri del link virtuale come bandwidth e delay sono configurabili.

![Diagramma dei namespace con firefox e httpd, virtual Ethernet pairs e Software Switch](images/lezione-21-lab-network-emulator-con-comnetsemu-img-04.jpg)
*Fig. — Il piano dati di Mininet: due namespace separati collegati tramite virtual Ethernet pairs e un Software Switch nel Root Namespace. Mininet gestisce automaticamente questa configurazione al posto dell'utility `ip`.*

#### Linux Traffic Control (tc)

Mininet usa `tc` (*traffic control*) per configurare le caratteristiche dei link virtuali:

```bash
# Aggiunge 100ms di delay + jitter di ±10ms sull'interfaccia eth0
tc qdisc add dev eth0 root netem delay 100ms 10ms

# Da dentro Mininet, su h1:
h1 tc qdisc add dev h1-eth0 root netem delay 100ms 10ms
h1 tc qdisc show dev h1-eth0
h1 tc qdisc del dev h1-eth0 root
```

---

## Architettura di ComNetsEmu

ComNetsEmu estende Mininet sostituendo il tipo di host di default con **container Docker**. Questo approccio si chiama *Docker-in-Docker* (o *sibling containers*): si ha un `DockerHost` con container Docker interni che emulano host fisici che eseguono applicazioni containerizzate.

![Architettura ComNetsEmu con server A, server B e client che comunicano tramite data plane e SDN controller](images/lezione-21-lab-network-emulator-con-comnetsemu-img-05.jpg)
*Fig. — Architettura ComNetsEmu: i container rappresentano applicazioni su host virtuali; il piano dati è gestito da virtual switch; il control plane è affidato a un SDN controller.*

La classe `APPContainerManager` orchestra i container Docker interni. Ogni `DockerHost` rimpiazza il tipo host di Mininet ed emula un host fisico che gira applicazioni containerizzate.

### Struttura del repository

| Cartella/File | Contenuto |
|---|---|
| `comnetsemu/` | Modulo Python che estende Mininet |
| `examples/` | Esempi per iniziare con le API ComNetsEmu |
| `app/` | Esempi di network slicing, SDN, ecc. |
| `util/` | Script per la gestione dell'ambiente |
| `test_containers/` | Dockerfile per i programmi di esempio |
| `Vagrantfile` | File Vagrant per il setup della VM |

---

## Setup dell'ambiente

> [!warning] Prerequisiti da installare prima del laboratorio
>
> L'installazione richiede circa **15 minuti** la prima volta. Completala prima della lezione di laboratorio.

### Dipendenze

ComNetsEmu viene eseguito in una VM gestita da **Vagrant**. Le dipendenze da installare sul proprio sistema host sono:

- **Vagrant** >= v2.2.5 — https://developer.hashicorp.com/vagrant/downloads
- **VirtualBox** >= v6.0 — https://www.virtualbox.org/wiki/Downloads

Una volta avviata la VM, al suo interno saranno già presenti:
- Mininet + OpenVswitch + Wireshark
- Ryu SDN controller
- Docker Engine

### Installazione su Linux e Windows

Segui le istruzioni ufficiali:
https://stevelorenz.github.io/comnetsemu/installation.html#option-1-install-in-a-vagrant-managed-vm-highly-recommended

```bash
cd ~
git clone https://git.comnets.net/public-repo/comnetsemu.git
cd ./comnetsemu
```

Prima di avviare la VM, è necessario modificare un Dockerfile.

### Modifica obbligatoria: Dockerfile.dev_test

> [!warning] Passo critico — da non saltare
>
> Prima di eseguire `vagrant up`, devi modificare il file `Dockerfile.dev_test` aggiungendo `netcat` alle dipendenze. Senza questa modifica il client TCP dell'esempio non funzionerà.

```bash
cd test_containers
# Apri il file Dockerfile.dev_test e aggiungi la riga "netcat \\" come mostrato nell'immagine
```

![Contenuto del file Dockerfile.dev_test con la riga netcat da aggiungere evidenziata](images/lezione-21-lab-network-emulator-con-comnetsemu-img-06.jpg)
*Fig. — Il file `Dockerfile.dev_test`: aggiungere la riga `netcat \\` prima di `telnet \\` nella lista dei pacchetti da installare con `apt-get`.*

Il file modificato deve includere `netcat \` nella lista dei pacchetti `apt-get install`. Dopo la modifica, salva il file e torna nella directory principale.

### Avvio della VM

```bash
cd ..
vagrant up comnetsemu
# Attendi circa 15 minuti la prima volta
```

Quando la VM è pronta, il banner di ComNetsEmu viene stampato a schermo. A quel punto:

```bash
# Accedi alla VM via SSH
vagrant ssh comnetsemu

# Quando hai finito, ferma la VM sul terminale locale
vagrant halt
```

### Installazione su Mac

> [!note] Mac — Percorso alternativo con Multipass
>
> L'installazione con Vagrant potrebbe non funzionare su host Mac. In quel caso usa **Multipass**, un gestore di VM leggero sviluppato da Canonical.
> Segui le istruzioni al punto **B** di: https://www.granelli-lab.org/researches/relevant-projects/comnetsemu-labs

### Installazione su Windows

Per host Windows, usa **MobaXterm** come console. Se l'apertura di xterm nell'emulatore non funziona:

```bash
# Salva la configurazione SSH in un file
vagrant ssh-config > vagrant-ssh

# Connettiti con forwarding X11 abilitato
ssh -F vagrant-ssh -Y comnetsemu

# Testa il forwarding X11
xeyes
# oppure
xterm
```

---

## Primo esempio: Echo Server

L'esempio `echo_server` mostra l'uso base dell'emulatore: due host emulati connessi tra loro tramite due switch, dove uno fa da client e l'altro ospita un server TCP che rimanda indietro ciò che riceve.

![Topologia dell'echo server con h1 (bash) e h2 (echo svr) connessi tramite s1 e s2](images/lezione-21-lab-network-emulator-con-comnetsemu-img-07.jpg)
*Fig. — Topologia dell'echo server: `h1` (10.0.0.1) con container `bash` e `h2` (10.0.0.2) con container `echo_server`, collegati da due switch con link da 10 Mbps e 10ms di delay.*

### Struttura del progetto

```bash
cd ~/comnetsemu/examples
mkdir echoMCPS
cd echoMCPS
```

Il progetto richiede quattro file:

| File | Scopo |
|---|---|
| `server.py` | Applicazione server TCP (echo) |
| `Dockerfile` | Containerizza l'applicazione server |
| `build_docker_image.sh` | Script per costruire l'immagine Docker |
| `topology.py` | Definisce la topologia ComNetsEmu |

### File 1: server.py

Il server apre un socket TCP sulla porta 65000, accetta connessioni e rimanda indietro ogni segmento ricevuto (echo):

```python
import socket

# Crea un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind sulla porta 65000 (su tutte le interfacce)
server_address = ("", 65000)
print("starting up on {} port {}".format(*server_address))
sock.bind(server_address)

# In ascolto per connessioni in ingresso
sock.listen(1)

while True:
    print("waiting for a connection")
    connection, client_address = sock.accept()
    try:
        print("connection from", client_address)
        while True:
            data = connection.recv(16)
            print("received {!r}".format(data))
            if data:
                print("sending data back to the client")
                connection.sendall(data)
            else:
                print("no data from", client_address)
                break
    finally:
        connection.close()
```

### File 2: Dockerfile

```dockerfile
FROM python:3.6-alpine3.9
COPY ./server.py /home/server.py
CMD python /home/server.py
```

### File 3: build_docker_image.sh

```bash
docker build -t echo_server --file ./Dockerfile .
```

Per costruire l'immagine:

```bash
bash build_docker_image.sh
```

### File 4: topology.py

```python
from comnetsemu.net import Containernet, VNFManager
from comnetsemu.cli import spawnXtermDocker
from mininet.node import Controller
from mininet.link import TCLink
from mininet.log import info
from mininet.cli import CLI

net = Containernet(controller=Controller, link=TCLink, xterms=False)
mgr = VNFManager(net)

try:
    info("*** Add controller\n")
    net.addController("c0")

    info("*** Creating hosts\n")
    h1 = net.addDockerHost("h1", dimage="dev_test",
         ip="10.0.0.1", docker_args={"hostname": "h1"})
    h2 = net.addDockerHost("h2", dimage="dev_test",
         ip="10.0.0.2", docker_args={"hostname": "h2"})

    info("*** Adding switch and links\n")
    switch1 = net.addSwitch("s1")
    switch2 = net.addSwitch("s2")
    net.addLink(switch1, h1, bw=10, delay="10ms")
    net.addLink(switch1, switch2, bw=10, delay="10ms")
    net.addLink(switch2, h2, bw=10, delay="10ms")

    info("\n*** Starting network\n")
    net.start()

    # Avvia i container applicativi
    srv1 = mgr.addContainer("srv1", "h1", "dev_test", "bash", docker_args={})
    srv2 = mgr.addContainer("srv2", "h2", "echo_server",
           "python /home/server.py", docker_args={})

    # spawnXtermDocker("srv1")
    CLI(net)

finally:
    info("*** Cleanup\n")
    mgr.removeContainer("srv1")
    mgr.removeContainer("srv2")
    net.stop()
    mgr.stop()
```

> [!note] dev_test vs echo_server
>
> `h1` usa l'immagine `dev_test` (che ha bash e netcat) come client. `h2` usa `echo_server` (che ha solo Python e il server). Per questo non è possibile aprire un xterm su `srv2`: l'immagine non include bash.

### Avvio dell'emulazione

```bash
sudo python3 topology.py
```

---

## Test dell'echo server

Una volta avviata la topologia, si apre un xterm sul container `srv1` (il client). Da lì è possibile eseguire i test.

### Verifica connettività

```bash
h1:/# ip a                  # mostra le interfacce del container
h1:/# ping 10.0.0.2         # verifica che h2 sia raggiungibile
```

### Test con netcat

**netcat** (`nc`) è uno strumento da riga di comando che legge e scrive dati attraverso la rete. Lo usiamo come client TCP:

```bash
h1:/# nc 10.0.0.2 65000
Hello server
Hello server        # il server rimanda indietro il messaggio
```

> [!tip] Come funziona
>
> `nc` si connette all'indirizzo IP 10.0.0.2 sulla porta TCP 65000, invia il testo digitato e stampa qualsiasi risposta ricevuta. Se tutto funziona correttamente, la parola "Hello server" comparirà due volte: una per l'input locale e una per l'echo del server.

### Cattura del traffico

Per ispezionare il traffico TCP generato, si può usare `tcpdump` direttamente nel container:

```bash
# Trova il container_id (h1 o h2)
docker ps -a

# Accedi al container
docker exec -it <container_id> bash

# Cattura il traffico TCP
tcpdump tcp

#Comando d'oro per cancellare pod e pulire la memoria e rifar partire topology
  sudo mn -c && sudo docker rm -f $(sudo docker ps -aq) && sudo python3 topology.py
```

---

## Uscire e spegnere la VM

Quando hai finito con gli esperimenti:

```bash
# 1. Esci dalla CLI di Mininet
mininet> exit

# 2. Esci dalla VM (shell SSH)
$ exit

# 3. Ferma la VM sul terminale locale
$ vagrant halt
```

---

## Comandi Docker utili

Durante i laboratori è utile avere familiarità con i comandi base di Docker.

| Comando | Descrizione |
|---|---|
| `ip link list` | Mostra le interfacce di rete disponibili sull'host |
| `sudo lsns -t net` | Elenca i network namespace attivi |
| `sudo ip netns add <name>` | Crea un nuovo namespace |
| `ip netns list` | Elenca i namespace |
| `docker pull <image>` | Scarica un'immagine dal registry |
| `docker run -it -d <image>` | Crea ed avvia un container |
| `docker ps -a` | Elenca tutti i container (anche fermi) |
| `docker exec -it <id> bash` | Accede a un container in esecuzione |
| `docker stop <id>` | Ferma un container in esecuzione |
| `docker kill <id>` | Ferma immediatamente un container |
| `docker images` | Elenca tutte le immagini locali |
| `docker rm <id>` | Elimina un container fermo |
| `docker rmi <image-id>` | Elimina un'immagine locale |
| `docker build <path>` | Costruisce un'immagine da un Dockerfile |
| `docker commit <id> <name>` | Crea una nuova immagine da un container modificato |

> [!question] Possibili domande d'esame
>
> - Qual è la differenza tra Mininet e ComNetsEmu?
> - Come vengono implementati gli host virtuali in Mininet? (network namespace)
> - Cosa sono le veth pairs e a cosa servono?
> - Come si configura il delay di un link virtuale in Mininet con `tc`?
> - Qual è il ruolo di Docker in ComNetsEmu rispetto al tipo di host di default di Mininet?
> - Cosa fa la classe `APPContainerManager` in ComNetsEmu?
> - Qual è la differenza tra `DockerHost` e un host Mininet tradizionale?
