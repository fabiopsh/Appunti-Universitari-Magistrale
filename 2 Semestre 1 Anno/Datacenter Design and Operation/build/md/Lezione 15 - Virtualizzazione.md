---
tags:
  - università/datacenter-design-and-operation
  - virtualizzazione
  - container
  - kubernetes
  - docker
  - hypervisor
data: 2026-05-07
lezione: "Virtualizzazione e Containerizzazione"
professore: "Antonio Cisternino"
---
# Virtualizzazione e Containerizzazione

La lezione affronta due tecnologie fondamentali per il datacenter moderno: i **container** e le **macchine virtuali** (VM). Il professore presenta intenzionalmente i container per primi, anche se storicamente sono venuti dopo la virtualizzazione, perché permettono di capire più facilmente il principio di isolamento. La virtualizzazione vera e propria — quella basata su hypervisor — è invece la tecnologia che ha reso possibile il cloud computing così come lo conosciamo oggi.

---

## Container

### Il principio fondamentale: cgroups e namespace

Un container non è un sistema operativo separato, ma una *vista* ristretta del sistema operativo esistente. Il meccanismo sottostante si chiama **cgroup** (control group), un modulo del kernel Linux che permette di raggruppare processi e limitare quali risorse di sistema essi possono nominare.

> [!tip] Il potere del nome
>
> In informatica, nominare una risorsa è l'unica condizione necessaria per potervi accedere. Un indirizzo di memoria è un nome. Un PID è un nome. Se una risorsa non è nominabile — cioè non è visibile nel namespace del processo — non esiste per quel processo. I cgroup sfruttano proprio questo principio: mostrano ai processi del container solo le risorse del proprio gruppo.

Concretamente, quando un processo all'interno di un container esegue una chiamata di sistema per elencare le risorse disponibili (altri processi, interfacce di rete, filesystem), il kernel filtra la risposta mostrando solo quelle appartenenti al suo cgroup. Il risultato è l'illusione di avere un sistema operativo dedicato, pur condividendo lo stesso kernel con tutti gli altri container sulla macchina.

Qui emerge la differenza fondamentale rispetto alle VM: **tutti i container condividono lo stesso kernel**. Questo ha implicazioni di sicurezza rilevanti: una vulnerabilità nel kernel colpisce simultaneamente tutti i container in esecuzione. Un esempio recente e concreto è **CVE-2026-31431 "Copy Fail"**: un bug introdotto nell'agosto 2017 nel modulo crittografico `authencesn` del kernel Linux, rimasto silente per quasi dieci anni e scoperto nel 2026 grazie ad analisi assistita da AI (strumento Xint Code). Un exploit di soli 732 byte di Python standard è sufficiente per ottenere privilegi di root su tutte le principali distribuzioni Linux (Ubuntu, RHEL, Amazon Linux, SUSE). Poiché il page cache del kernel è condiviso tra tutti i processi — inclusi quelli appartenenti a container diversi — la vulnerabilità non è solo una local privilege escalation ma anche un **container escape** e un vettore di compromissione di nodi Kubernetes. Al momento della lezione non esisteva una patch generale: la raccomandazione era disabilitare il modulo se non strettamente necessario.

### Il filesystem differenziale

Un container ha il proprio filesystem, ma questo non è una copia completa: è un **filesystem differenziale** a strati (layer). Ogni immagine container è definita da una sequenza di layer sovrapposti. Quando si crea un container a partire da un'immagine base, si aggiunge semplicemente un nuovo layer che registra solo le differenze rispetto a quello precedente — esattamente come un disco differenziale nelle VM.

> [!example] Vantaggi del filesystem a layer
>
> Se dieci container derivano dalla stessa immagine base (ad esempio Ubuntu), i layer comuni esistono una sola volta su disco. Al download, se un layer è già presente localmente, non viene riscaricato. Questo si traduce in risparmio di spazio e download incrementali.

Il rovescio della medaglia è **prestazionale**: il filesystem differenziale è una struttura dati complessa. Quando si accede a un file, il sistema deve cercarlo nel layer corrente e, se non lo trova, risalire ai layer precedenti. Più layer ci sono, più operazioni di I/O sono necessarie. Per i dati che richiedono prestazioni elevate — come i file di un database — è quindi consigliabile montare una directory reale del filesystem host.

### Volumi e variabili d'ambiente

Due meccanismi permettono di iniettare configurazione e dati dall'esterno nel container senza modificarne il filesystem interno:

**Variabili d'ambiente**: prima dell'era dei container erano considerate un mezzo di configurazione obsoleto e scomodo. Docker le ha riportate in auge perché rappresentano il modo più semplice per iniettare parametri in un container senza dover accedere al suo filesystem interno. La configurazione viene specificata al momento del lancio del container e non richiede di modificare l'immagine.

**Volumi**: un volume è una directory (o file) del filesystem host montata in una posizione specifica all'interno del container. Il container la vede come parte del proprio filesystem, ma i dati risiedono fisicamente sull'host. I casi d'uso principali sono:
- Persistenza dei dati oltre il ciclo di vita del container (es: directory dati di un database)
- Condivisione di dati tra più container
- Iniezione di file di configurazione o certificati senza ricostruire l'immagine

> [!warning] Dati persistenti nei container
>
> Se si esegue un database in un container senza montare un volume per la directory dati, tutti i dati vengono persi quando il container viene eliminato. Montare la directory `/var/lib/postgresql/data` (o equivalente) su un volume host è pratica obbligatoria in produzione.

### Rete nei container

Ogni container ha il proprio network namespace: il suo `localhost` è diverso dal `localhost` dell'host e da quello degli altri container. In Docker, ogni container riceve un indirizzo IP nel range `172.x.x.x` della rete interna Docker. I container non comunicano tra loro tramite `localhost`, ma tramite questi indirizzi IP privati o tramite il nome del servizio definito in Docker Compose.

Il mapping delle porte (`ports`) nel file di Compose permette di esporre verso l'esterno una porta del container su una porta dell'host. Poiché tutti i container condividono la stessa interfaccia di rete fisica, non è possibile che due container siano in ascolto contemporaneamente sulla porta 80 dell'host: il port mapping risolve il conflitto assegnando porte diverse esternamente.

> [!note] Sicurezza della rete condivisa
>
> Nei container la scheda di rete fisica (**NIC**, *Network Interface Card*) dell'host è condivisa tra tutti i container in esecuzione — è lo stesso hardware che gestisce il traffico di tutti. Nelle VM, invece, ogni macchina virtuale riceve una scheda di rete virtuale dedicata (vNIC), emulata dall'hypervisor, con il proprio MAC address e la propria identità di rete completa. Questa è una delle differenze di isolamento più significative tra i due approcci.

### Docker Compose

Docker Compose permette di descrivere un'applicazione multi-container come composizione di servizi in un file YAML. Il professore mostra un esempio con tre servizi: un frontend (Nginx come reverse proxy), un application server (backend su porta 8080) e un database (SQL Server su porta 1433).

> [!example] Anatomia di un docker-compose.yml
>
> - **`image`**: specifica l'immagine da scaricare da Docker Hub (o da un registry privato come quello di Microsoft). Il tag `latest` è una convenzione: quando si pubblica, si tagga l'immagine più recente con `latest` oltre alla versione specifica.
> - **`environment`**: variabili d'ambiente iniettate nel container (es: password SA per SQL Server, EULA acceptance). Nei file di sviluppo si accetta di avere password in chiaro; in produzione si usano secret manager.
> - **`volumes`**: mappatura `host_path:container_path`, opzionalmente con `:ro` per sola lettura. Utile per montare certificati, credenziali, e directory dati.
> - **`ports`**: mappatura `host_port:container_port`. Se le porte sono uguali si può scrivere solo il numero.
> - **`depends_on`**: ordine di avvio tra i servizi.
> - **`networks`**: i servizi nella stessa rete si vedono tra loro; quelli in reti diverse no.

L'architettura tipica con Nginx come reverse proxy è raccomandata perché i server applicativi (Tomcat, Kestrel, ecc.) non sono progettati per gestire direttamente il traffico web ad alta concorrenza. Nginx, invece, è ottimizzato per questo e funge da punto di terminazione TLS, da load balancer e da proxy verso i backend.

![Diagramma Mermaid](images/mermaid-lezione-15-virtualizzazione-01.png)
*Fig. — Architettura di un'applicazione multi-container con Docker Compose: Nginx riceve le connessioni esterne e le inoltra al backend; il database monta un volume host per la persistenza.*

### Orchestrazione: Kubernetes

Una volta che si è in grado di eseguire più container, nasce spontaneamente il bisogno di orchestrarli su più macchine. Kubernetes (abbreviato K8s) nasce in Google proprio per questo: scalare i servizi di ricerca su cluster di migliaia di macchine. Il caso d'uso originale è semplice: se ho 1000 richieste concorrenti, voglio istanziare automaticamente N repliche del container che serve la richiesta e bilanciarle.

> [!definition] Kubernetes
>
> Piattaforma open source per l'orchestrazione di container su cluster di macchine. Permette di definire lo stato desiderato del sistema (numero di repliche, risorse allocate, regole di networking) e si occupa autonomamente di mantenerlo.

L'architettura è composta da un **control plane** (nodo master che coordina tutto il cluster) e da **worker node** su cui girano i container. I container sono raggruppati in **pod** — la più piccola unità deployabile in Kubernetes, tipicamente un container o un gruppo strettamente accoppiato.

> [!tip] Canary deployment e rolling updates
>
> Kubernetes permette di avere contemporaneamente la versione 1 e la versione 2 di un servizio. Il reverse proxy in ingresso (Ingress controller) decide la percentuale di traffico da inviare a ciascuna versione. Si aggiorna così gradualmente il software senza interruzioni di servizio (rolling update) o si testa la nuova versione su una piccola percentuale di utenti (canary deployment).

---

## Virtualizzazione

### VM vs Container: la differenza fondamentale

La differenza chiave è il livello di isolamento: i container condividono il kernel del sistema operativo host; le VM no. Una VM contiene il proprio sistema operativo completo, compreso il kernel. Questo significa che:

- Su una macchina si possono eseguire simultaneamente una VM Linux e una VM Windows (impossibile con i container, che devono condividere il kernel dell'host)
- Una vulnerabilità del kernel non attraversa il confine della VM
- Le VM hanno overhead maggiore (dimensione su disco, memoria, tempo di avvio)

> [!note] WSL2 e i container Linux su Windows
>
> Su Windows, i container Linux vengono eseguiti dentro una VM Linux leggera gestita da Hyper-V (WSL2). Non è una violazione del principio: i container condividono il kernel della VM Linux, non direttamente il kernel Windows.

### L'Hypervisor

L'**hypervisor** è il software che implementa la virtualizzazione: prende le risorse fisiche della macchina (CPU, memoria, rete, storage) e le suddivide in slice assegnate a ciascuna VM. È responsabile di:

- **Scheduling della CPU**: distribuire i core fisici tra le VM
- **Gestione della memoria**: isolare gli spazi di indirizzamento
- **I/O virtualizzato**: presentare a ogni VM disk controller, interfacce di rete e altri dispositivi come se fossero fisici
- **Virtual console**: permettere l'accesso grafico alla VM

![Diagramma Mermaid](images/mermaid-lezione-15-virtualizzazione-02.png)
*Fig. — Architettura di un sistema di virtualizzazione: l'hypervisor si interpone tra l'hardware fisico e le VM, esponendo risorse virtualizzate a ciascuna.*

### Il Virtual Switch

Accanto all'hypervisor, il **virtual switch** è il componente che rende le VM indistinguibili da macchine fisiche dal punto di vista della rete. Poiché più VM girano sullo stesso host fisico, serve un'infrastruttura di rete interna che:

- Assegni a ogni VM un'identità di rete completa (MAC address, IP, VLAN)
- Gestisca il traffico est-ovest tra VM dello stesso host senza passare dalla scheda di rete fisica (traffico puramente in-memory, molto più veloce)
- Colleghi le VM alla rete fisica usando la scheda di rete fisica dell'host come uplink verso lo switch esterno

Il virtual switch implementa in software le stesse funzionalità di un switch fisico: broadcast domain, VLAN tagging, forwarding basato su MAC. In VMware questo componente si chiama **vSwitch** (o **Distributed Switch** nelle configurazioni enterprise).

### Live Migration

La capacità più potente della virtualizzazione è la **live migration** (chiamata **vMotion** in VMware): spostare una VM in esecuzione da un server fisico a un altro **senza interruzione del servizio**.

> [!tip] Perché la live migration è rivoluzionaria
>
> Un sito web che serve pagine può essere spostato da una macchina fisica a un'altra mentre continua a rispondere alle richieste HTTP. Questo rende possibile la manutenzione dell'hardware senza downtime, il bilanciamento del carico tra server e la gestione automatica dei guasti. È la tecnologia che ha reso il cloud computing economicamente viable.

Il meccanismo si basa sul fatto che lo stato completo di una VM (memoria, registri CPU, stato dei device) è una struttura dati nel software dell'hypervisor. Copiare questa struttura da un host all'altro, sincronizzare le ultime modifiche e commutare il controllo è tecnicamente complesso ma possibile. Lo storage condiviso (SAN o NAS) elimina il problema di dover spostare anche i disk file.

### CPU Virtualization: anelli e istruzioni hardware

Il problema tecnico più sottile della virtualizzazione è la **virtualizzazione della CPU**. Un kernel di sistema operativo esegue istruzioni privilegiate che accedono direttamente all'hardware (gestione degli interrupt, manipolazione della memoria fisica, configurazione del timer). Se si esegue un kernel "ospite" dentro una VM, queste istruzioni devono essere intercettate e gestite dall'hypervisor prima di raggiungere la CPU fisica.

Le CPU x86 (e ARM) non hanno solo due livelli di privilegio (supervisor/user): l'Intel 386 ne aveva già 16, chiamati **ring** (da ring 0, il più privilegiato, a ring 15). Il kernel normalmente gira in ring 0 e le applicazioni in ring 3.

Le prime implementazioni di virtualizzazione sfruttavano questi ring intermedi per interporre il kernel ospite tra il kernel dell'hypervisor e le applicazioni, ma era un'architettura fragile. La soluzione definitiva è arrivata con l'introduzione di **istruzioni hardware dedicate alla virtualizzazione**:

- **Intel VT-x** (Virtualization Technology for x86)
- **AMD-V** (AMD Virtualization)

Queste estensioni aggiungono strutture dati (VMCS su Intel) per salvare e ripristinare efficientemente lo stato completo di una VM durante i context switch tra VM diverse, interrupt virtuali separati da quelli fisici, e timer virtuali indipendenti.

> [!warning] Context switch tra VM vs tra processi
>
> Un context switch tra processi salva/ripristina i registri del processo. Un context switch tra VM deve salvare/ripristinare l'intero stato del kernel ospite (registri + stato MMU + interrupt controller virtuale + timer). Senza supporto hardware è un'operazione ordini di grandezza più costosa.

### I principali hypervisor

> [!abstract] Panorama dei vendor
>
> - **VMware** (ora Broadcom): leader storico del mercato enterprise. Fondato nel 1997-98, acquisito da Dell tramite EMC², poi ceduto a Broadcom. Il cambio di ownership ha portato a una riorganizzazione radicale del licensing che ha spinto molti clienti a cercare alternative — operazione resa difficile dalla maturità tecnica insostituibile di VMware in ambito enterprise.
> - **Hyper-V** (Microsoft): integrato in Windows Server e nelle versioni Pro/Enterprise di Windows. Microsoft è stata per un periodo il maggior contributore al kernel Linux, contribuendo i moduli per la virtualizzazione tramite Hyper-V (usati anche da WSL2).
> - **KVM** (Kernel-based Virtual Machine): modulo integrato nel kernel Linux; base di molte distribuzioni cloud, incluso OpenStack.
> - **Proxmox**: soluzione open source basata su KVM, usata molto in ambienti homelab e PMI. Non raggiunge le prestazioni e la maturità di VMware in ambito enterprise.

### Snapshot e Checkpoint

Un **checkpoint** (o snapshot) è una fotografia istantanea dello stato completo di una VM in un dato momento: contenuto della memoria, stato dei registri CPU, stato del disco. Viene implementato attraverso lo stesso meccanismo del filesystem differenziale: al momento dello snapshot, il file del disco virtuale viene congelato e tutte le scritture successive vanno in un nuovo file differenziale.

> [!example] Demo: snapshot e ripristino
>
> Durante la lezione il professore dimostra la potenza degli snapshot:
> 1. Crea una VM Ubuntu su Hyper-V con un virtual disk VHDX
> 2. Installa Ubuntu
> 3. Prende un checkpoint (il file disco si divide: base frozen + differenziale attivo)
> 4. Esegue `rm -rf /` all'interno della VM, distruggendo il filesystem
> 5. Ripristina il checkpoint precedente → la VM riparte esattamente nello stato in cui era prima del disastro, memoria inclusa

> [!warning] Performance overhead degli snapshot
>
> Ogni accesso al disco di una VM con snapshot attivi richiede una ricerca a cascata attraverso i layer: prima nel differenziale corrente, poi in quello precedente, e così via. Più snapshot ci sono, più operazioni I/O multiple si sommano per ogni accesso. Mantenere snapshot a lungo su VM in produzione (che scrivono continuamente sul disco per aggiornamenti, log, ecc.) degrada significativamente le prestazioni e aumenta lo spazio su disco ben oltre la dimensione nominale allocata alla VM. È una cattiva pratica comune nei team di datacenter operation.

