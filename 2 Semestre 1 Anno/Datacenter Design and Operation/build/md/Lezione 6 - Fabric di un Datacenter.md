## Il Cablaggio Fisico nel Data Center

### Perché il cablaggio è una scelta progettuale

Quando si stende un cavo in un data center, non si esegue un'operazione meccanica neutra: si sta prendendo una decisione architetturale. Il cablaggio fisico determina la geometria della comunicazione tra i rack, e quella geometria diventa poi un limite duro per le performance delle applicazioni che girano sopra.

I motivi per cui il cablaggio è rilevante sono essenzialmente tre.

**Perdita di segnale.** Ogni connettore introdotto causa una piccola attenuazione. All'interno del data center, dove i percorsi sono brevi, questa perdita è trascurabile e non rappresenta un vincolo pratico.

**Numero di hop.** Ogni switch attraversato da un pacchetto introduce latenza. Un singolo switch Ethernet moderno introduce circa **600 nanosecondi** di latenza. Sembra poco, ma ci sono workload — condivisione di memoria tra GPU, accesso a modelli AI distribuiti — in cui anche pochi microsecondidi aggiunta rendono il sistema inutilizzabile.

**Flessibilità topologica.** La geometria del cablaggio determina quanti percorsi fisici esistono tra due rack, quanto traffico est-ovest può scorrere, e quanto è difficile riconfigurare la rete in caso di aggiunta o rimozione di macchine.

> [!tip] La latenza end-to-end: il gap nascosto
> 
> Un singolo switch Ethernet introduce ~600 ns, ma appena si sale al livello TCP/IP la latenza può arrivare a **70 microsecondi**. Per contesto: un accesso DRAM locale è nell'ordine dei 60–100 ns. Attraversare anche un solo hop TCP introduce una penalità equivalente a centinaia di accessi in memoria. Per workload come i modelli LLM distribuiti su GPU — in lezione è citato GLM-4 con 750 miliardi di parametri in architettura Mixture of Experts — questa latenza diventa il collo di bottiglia dell'intero sistema.

### Patch panel e zone funzionali

Dato che non è pratico — né riconfigurabile — tirare cavi diretti da ogni rack a ogni altro rack, la soluzione standard è il **patch panel**: un pannello passivo che funge da punto di smistamento intermedio, permettendo di "teletrasportare" logicamente una connessione da una zona del data center all'altra semplicemente spostando un cordone, senza rifare il cablaggio strutturale.

Il cablaggio strutturale presuppone una divisione in **zone funzionali** del data center. Poiché collegare tutto con tutto è fisicamente impraticabile (un grafo completo su N rack richiederebbe $\binom{N}{2}$ cavi), si assegnano ruoli alle aree: zona telco per i link verso l'esterno, zone compute, zone storage, e così via.

> [!warning] Conseguenze di un cablaggio sbagliato
> 
> Se la geometria del cablaggio non rispecchia il reale pattern di comunicazione dei workload, i pacchetti saranno costretti a percorsi subottimali: più hop, più latenza, meno banda. Questo si traduce in limitazioni di performance visibili sulle VM, anche su cloud pubblici come AWS o Azure — sono il risultato diretto delle scelte fisiche fatte da Microsoft o Amazon al momento dell'installazione del data center.

### Organizzazione fisica dei rack: pod e corridoi

In un data center, i rack vengono tipicamente organizzati in **pod di distribuzione**: insiemi di rack fisicamente adiacenti, disposti su due file che si affacciano su un corridoio freddo confinato per il raffreddamento. La prossimità fisica rende accettabile, in alcuni casi, collegare rack adiacenti direttamente senza patch panel, eliminando le pareti laterali dei rack e facendo passare i cavi internamente da un rack al successivo.

La distinzione fondamentale rimane tra traffico **est-ovest** (server-a-server all'interno del data center) e traffico **nord-sud** (server verso l'esterno): hanno pattern e requisiti di latenza radicalmente diversi, e ogni scelta di cablaggio li impatta in modo diverso.

---

## I Transceiver: dal Cavo allo Switch

### Il problema dei connettori ottici

Quando le velocità di rete hanno superato la soglia in cui RJ45 e doppino rame sono sufficienti, si è passati alla fibra ottica. Ma qui emerge un problema economico: la fibra monomodale OS2 consente distanze fino a **40 km**, ma all'interno di un data center non si superano i 300 metri. Acquistare laser di potenza industriale pensati per decine di chilometri è uno spreco enorme.

La soluzione è stata separare il trasmettitore ottico dallo switch attraverso un **transceiver modulare**: un piccolo modulo attivo che si inserisce in uno slot dedicato dello switch, converte il segnale elettrico in ottico e viceversa, e determina il tipo di fibra, la lunghezza d'onda e la distanza massima supportata.

> [!definition] Transceiver (modulo SFP/QSFP)
> 
> Modulo attivo hot-pluggable che si inserisce in uno slot del backplane dello switch. Converte segnali elettrici in ottici e viceversa. Il firmware del modulo espone allo switch le proprie caratteristiche (velocità, tipo di fibra, range). Questo consente il **mix and match**: slot 1 con fibra multimodale corto raggio, slot 3 con monomodale lungo raggio, slot N con rame per debug — tutto sullo stesso switch.

### La famiglia SFP: evoluzione degli standard

L'ecosistema dei transceiver si organizza intorno a famiglie standardizzate. Conoscere questi nomi è competenza operativa fondamentale in un data center.

**SFP28** è lo standard dominante per le porte server-facing nei leaf switch. Supporta **25 Gbps** per lane e viene declinato in varianti per distanza: _SR (Short Range)_ a 850 nm su fibra multimodale per distanze fino a ~100 m, _LR (Long Range)_ a 1310 nm su fibra monomodale per distanze fino a ~10 km, e _ER (Extended Range)_ per portate ancora maggiori.

Quando l'SFP28 ha raggiunto il suo limite fisico (la densità di segnale non scalava oltre 25 Gbps con quel form factor), si è passati a **QSFP** (_Quad SFP_): stesso concetto ma con **4 lane interne**. Le varianti della famiglia QSFP sono:

|Standard|Banda totale|Struttura interna|Note|
|---|---|---|---|
|QSFP+|40 Gbps|4×10G NRZ|Prima generazione|
|QSFP28|100 Gbps|4×25G NRZ|Standard attuale per uplink leaf↔spine|
|QSFP56|200 Gbps|4×50G PAM4|Uplink spine-to-spine|
|QSFP-DD|fino a 800 Gbps|8×100G PAM4|Ultima generazione, double density|

> [!note] Il salto a PAM4 e la logica dell'incremento
> 
> Il passaggio da QSFP28 a QSFP56 non aumenta il numero di lane (rimangono 4), ma cambia la modulazione da NRZ a PAM4: invece di codificare 1 bit per simbolo, PAM4 codifica 2 bit per simbolo, raddoppiando la banda a parità di frequenza. Il QSFP-DD raddoppia ulteriormente le lane da 4 a 8, mantenendo le stesse dimensioni fisiche esterne ma con una scheda di contatti più profonda.

### Codici colore e decodifica del modulo

I transceiver usano **codici colore** convenzionali: il blu identifica tipicamente la fibra monomodale, il nero o grigio la multimodale. Sul corpo del modulo è inciso il codice completo: tipo (es. SFP28), velocità (25G), lunghezza d'onda (850 nm → multimodale, 1310 nm → monomodale), range (SR/LR/ER).

**Perché la multimodale domina il data center?** Perché le distanze interne raramente superano i 100–300 metri, e la fibra multimodale è significativamente più economica sia nei cavi che nei laser. In lezione è stato fatto un confronto pratico: un modulo SFP28 SR (multimodale) costa circa €45; ne servono due (uno per estremo) più il cavo ottico (~€10), per un totale di ~€100. Un cavo DAC (_Direct Attach Cable_) in rame ha un costo simile, ma la soluzione a transceiver offre modularità: si sostituiscono i moduli per aggiornare la velocità senza cambiare il cavo.

> [!tip] Evoluzione della banda per transceiver nel tempo
> 
> 2005: 1 Gbps → 2010: 10 Gbps → 2015: 25–40 Gbps → 2020: 100–200 Gbps → 2024: 400–800 Gbps. In vent'anni, un fattore 800×. Ogni generazione ha richiesto nuovi form factor e nuovi laser, ma il principio di modularità degli slot è rimasto invariato.

---

## Gli Switch: dai Chassis Modulari al Form Factor Fisso

### L'era dei chassis

Fino ai primi anni 2000, lo switch tipico di un data center era un **chassis modulare**: un armadio di grandi dimensioni nel quale si inserivano _line card_ — schede con più porte Ethernet — e un modulo **RPM** (_Routing Processing Module_) responsabile del coordinamento attraverso un _backplane_ condiviso.

Questi switch erano costosissimi, quindi tipicamente un data center ne aveva **due** per ridondanza, e tutti i cavi del data center confluivano verso questi due switch centrali. Da questa architettura fisica nacque naturalmente una topologia a stella: un unico punto di smistamento centrale attorno al quale tutto era organizzato.

> [!note] Eredità nella nomenclatura delle porte
> 
> La notazione `X/Y` delle porte Ethernet (es. `0/1` = _line card 0, porta 1_) è una diretta eredità della struttura bidimensionale del chassis. Sugli switch moderni a form factor fisso non esiste più la line card, ma la convenzione è rimasta in tutto il software di gestione di rete.

### La crisi del backplane e la transizione

Il modello a chassis aveva senso economico finché la banda cresceva lentamente. Ma quando la velocità Ethernet ha cominciato a raddoppiare ogni pochi anni — da 1G a 10G a 25G — il **backplane** del chassis non riusciva più a stare al passo. Progettare un backplane capace di supportare la velocità attuale significava che tra due anni sarebbe già obsoleto, e il chassis costoso acquistato aveva già schede mezze vuote.

La risposta è stata la transizione agli **switch a form factor fisso**: switch compatti, tipicamente 1U, con un numero fisso di porte, montabili direttamente top-of-rack. Questi switch sono più economici, più facili da sostituire, e avvicinano il punto di switching ai server riducendo la lunghezza dei cavi e il numero di hop.

---

## Topologia di Rete: da 3-Tier a Spine-and-Leaf

### Architettura 3-tier

Il concentrare lo switching in pochi chassis centrali produsse la topologia **3-tier**: _access layer_ vicino ai server, _distribution layer_ di aggregazione intermedia, _core layer_ con i grandi chassis centrali. Tutto il traffico doveva passare per il core. Questo era accettabile finché il traffico dominante era nord-sud.

![Traffico nord-sud nell'architettura 3-tier](images/three-tier-architecture-traffic-5d3d84.png) _Fig. 1 — In architettura 3-tier il traffico tipico è nord-sud: i client accedono ai server dall'esterno. Core e distribution switch gestiscono questi flussi in modo efficiente._

Con l'avvento dei microservizi, del cloud e dell'AI, il traffico est-ovest è diventato dominante: ogni richiesta applicativa coinvolge decine di servizi che si parlano tra loro all'interno del data center.

![Inefficienze della 3-tier con traffico est-ovest](images/three-tier-inefficiencies-a922f0.png) _Fig. 2 — Con traffico east-west dominante, ogni comunicazione server-a-server deve risalire access → distribution → core → distribution → access: latenza variabile, colli di bottiglia sugli uplink._

### STP: soluzione necessaria ma costosa

Per garantire ridondanza occorrono percorsi fisici multipli, ma più percorsi creano loop in Ethernet.

> [!warning] Loop e broadcast storm
> 
> In Ethernet, un loop causa un **broadcast storm**: un frame broadcast rimbalza all'infinito amplificandosi, satura tutta la banda e rende la rete inutilizzabile in pochi secondi. È un problema concreto che si presenta ogni volta che un cavo crea accidentalmente un ciclo nella topologia.

> [!definition] Spanning Tree Protocol (STP / RSTP)
> 
> Protocollo di livello 2 (IEEE 802.1D / 802.1W) che costruisce dinamicamente un albero di copertura della rete, **disabilitando i link che formerebbero cicli**. In caso di guasto di un link attivo, ricalcola l'albero e riabilita un link precedentemente disabilitato. STP converge in decine di secondi; RSTP in qualche secondo.

![STP blocca i link ridondanti nella topologia 3-tier](images/three-tier-spanning-tree-fa1cb3.png) _Fig. 3 — STP in azione: i link ridondanti (tratteggiati/rossi) vengono disabilitati per eliminare i loop. Il cavo fisico è presente e pagato, ma non trasporta traffico._

Il costo di STP è duplice. Primo: **spreco di risorse** — il link ridondante è fisicamente presente e pagato (cavo, transceiver, porta dello switch), ma non trasporta traffico. Secondo: **lentezza di convergenza** — STP originale impiega fino a **50 secondi** per convergere dopo un guasto, RSTP qualche secondo. Un'interruzione di 50 secondi è accettabile per traffico web a basso carico; è un disastro se il fabric collega VM alle proprie unità di storage virtuali (la VM perderebbe il disco per tutta la durata).

### Spine-and-Leaf: la topologia dominante oggi

> [!definition] Spine-and-Leaf
> 
> Topologia di rete a due livelli in cui i **leaf switch** raccolgono i server (tipicamente top-of-rack, uno per rack) e i **spine switch** interconnettono i leaf. Ogni leaf è collegato a ogni spine, producendo un grafo bipartito regolare. Il cammino tra qualsiasi coppia di server è costante: leaf → spine → leaf, ovvero **2 hop fisici, 1 hop logico**.

I leaf switch non si parlano mai direttamente: tutto il traffico est-ovest passa obbligatoriamente per uno spine. Questo garantisce latenza **uniforme e predicibile** indipendentemente da dove si trovano i due server.

![Architettura spine-and-leaf](images/leaf-spine-architecture-919c04.png) _Fig. 4 — Spine-and-leaf: ogni leaf si connette a tutti gli spine. Qualunque comunicazione server-a-server attraversa esattamente uno spine, con latenza costante. Aggiungere capacità significa aggiungere leaf (scale-out orizzontale)._

### Ridondanza senza STP: link aggregation active-active

Con spine-and-leaf la ridondanza si ottiene tramite **link aggregation**: due spine switch fisicamente distinti vengono fatti operare come un singolo switch logico (tramite protocolli come vPC di Cisco, MLAG di Arista, o il protocollo standard LACP). Ogni leaf vede due cavi verso lo spine ma li tratta come un'unica interfaccia logica ad alta banda. Lo schema è **active-active**: entrambi i link trasportano traffico contemporaneamente.

> [!example] Aggregazione di banda con spine pair
> 
> Se ogni link leaf↔spine è da 25 Gbps, aggregando due spine si hanno 50 Gbps di banda disponibile tra un leaf e lo strato spine. Un singolo stream TCP rimane limitato a 25 Gbps (non si può dividere un flusso su due link), ma due stream paralleli possono usare link diversi, sommando a 50 Gbps totali. Se uno spine cade, la banda degrada da 50 a 25 Gbps ma la connettività non si interrompe — nessun STP da aspettare.

### Confronto 3-tier vs Spine-and-Leaf

|Dimensione|3-tier / Chassis|Spine-and-Leaf|
|---|---|---|
|Latenza|Variabile (dipende dal path)|Fissa e bassa (1 hop logico)|
|Banda|Limitata dalla gerarchia|Aggregata e scalabile|
|Link ridondanti|Disabilitati da STP (sprecati)|Attivi — active-active|
|Traffico est-ovest|Subottimale|Nativo e ottimizzato|
|Convergenza dopo guasto|Secondi (RSTP)|Istantanea (degradazione banda)|
|Scalabilità|Verticale (upgrade chassis)|Orizzontale (aggiungere leaf)|

> [!abstract] Perché spine-and-leaf ha vinto
> 
> Tre ragioni sintetizzano il dominio di spine-and-leaf nei data center moderni. Prima: **latenza a 1 hop** — qualunque server raggiunge qualunque altro con latenza predicibile. Seconda: **banda aggregata** — nessun costo per link inutilizzati, tutto l'hardware lavora. Terza: **east-west friendly** — il traffico interno al data center, fondamentale per microservizi, storage distribuito e GPU cluster AI, non deve più risalire gerarchie di switch lente.

---

## Data Center vs Campus Network

Spine-and-leaf è pensata per il traffico **est-ovest** dominante nei data center. Nelle **reti campus** — università, uffici, reti Wi-Fi — il traffico è prevalentemente **nord-sud**: gli utenti accedono a risorse esterne. Per questo le reti campus continuano a usare architetture gerarchiche tipo 3-tier con STP: la convergenza lenta è accettabile, e lo spreco dei link ridondanti non è critico.

> [!note] La rete Wi-Fi del campus
> 
> La rete wireless universitaria è un'architettura north-south, non spine-leaf. Questo spiega perché in Wi-Fi spesso non si riesce a pingare altri dispositivi collegati alla stessa access point: il traffico non è ottimizzato per la comunicazione laterale.

---

## Conclusioni e Punti Chiave

Questa lezione ha tracciato il percorso dal cavo fisico all'architettura di rete, mostrando come ogni scelta a basso livello si rifletta in caratteristiche osservabili ad alto livello. Capire queste scelte fisiche è essenziale per comprendere perché una VM su AWS ha certi limiti di banda, o perché un'applicazione distribuita su rack diversi si comporta diversamente da una co-locata sullo stesso rack.

Il corso proseguirà con le infrastrutture **convergenti e iperconvergenti** — tecnologie che dipendono direttamente dalla capacità del fabric spine-and-leaf di gestire traffico est-ovest con latenza controllata e banda prevedibile.

> - In quale contesto si usa ancora un'architettura 3-tier? Perché è accettabile lì ma non in un data center?