
# Cablaggio e Tecnologie di Trasmissione

La progettazione e la gestione di un data center moderno richiedono una visione olistica che abbraccia discipline diverse: dalla termodinamica all'idraulica, fino alle tecnologie di trasmissione ottica ed elettrica. Questa lezione richiama le strategie di raffreddamento già introdotte, approfondisce la gestione del ciclo di vita dell'infrastruttura, e affronta le tecnologie di cablaggio di rete che costituiscono il vero e proprio "sistema nervoso" del data center.

## Raffreddamento e Distribuzione Elettrica

### Da CRAC all'In-Row Cooling

La dissipazione del calore è indissolubilmente legata alla distribuzione elettrica. Nelle architetture tradizionali, il raffreddamento era basato su unità **CRAC** (*Computer Room Air Conditioning*), che prelevavano l'aria calda dal soffitto per reimmetterla fredda attraverso un pavimento flottante. Questa architettura presenta severi limiti legati alla **densità di potenza**: funziona in modo efficiente solo fino a 5–8 kilowatt per rack, soglia oltre la quale raffreddare l'intera stanza diventa impraticabile ed energeticamente svantaggioso.

Lo standard odierno privilegia l'**in-row cooling**, un sistema che delocalizza la produzione del freddo rispetto al punto di utilizzo, sfruttando l'acqua come mezzo di trasporto termico. Ogni unità è dotata di sensori e attuatori gestibili digitalmente tramite HTTP e Web API, permettendo di aumentare dinamicamente la velocità delle ventole solo nelle zone dove si registrano picchi di calore, senza dover sovrarraffreddare l'intera infrastruttura.

### Raffreddamento a Liquido: Opportunità e Rischi

Quando la densità di potenza supera le capacità dell'aria, il **liquid cooling** diventa una necessità. Questo introduce però rischi concreti: l'acqua minerale comune conduce elettricità, creando un rischio reale di cortocircuito e incendio in rack che assorbono dai 30 ai 200 kilowatt. Le alternative presentano i propri compromessi: l'olio minerale è termicamente efficiente ma costoso e difficile da gestire, mentre i fluidi a base di glicole offrono capacità termica elevata e non conducono elettricità, ma a un costo significativo.

> [!warning] La gestione idraulica nei data center
>
> I circuiti di raffreddamento ad acqua operano in modo analogo al radiatore di un'automobile, introducendo variabili nuove per i team IT: l'accumulo di depositi minerali che ostruiscono tubi di piccolo diametro, la gestione della pressione per garantire il corretto flusso senza rotture, e la necessità di idraulici specializzati — una figura professionale storicamente estranea al mondo IT.

Anche la distribuzione elettrica segue una struttura ad albero, con una linea principale che si suddivide fino ai singoli rack. La progettazione prevede margini di **overbooking** (sovrassegnazione) che consentono di aggiornare le cabine elettriche in futuro senza dover ricablare l'intera infrastruttura. Se dieci anni fa 15 kW per rack erano sufficienti per l'**HPC** (*High Performance Computing*), oggi il limite minimo per installazioni ad alte prestazioni parte dai 30 kW a salire.

---

## Ciclo di Vita del Data Center e Horizon Effect

Un data center non si progetta per qualche anno: il suo orizzonte temporale è tipicamente di un decennio o più. Quando si definisce un'architettura si stabiliscono confini fisici difficilmente valicabili in seguito, rendendo la stima della futura densità di potenza una decisione strategica con conseguenze a lungo termine.

> [!definition] Horizon Effect
>
> L'incapacità di vedere oltre le necessità immediate durante la fase di progettazione, che costringe a costosi riprogettamenti prematuri. Una stima troppo conservativa della futura densità di potenza può rendere obsoleto un data center in pochi anni dall'apertura.

Un esempio virtuoso è il data center universitario di San Piero a Grado (Pisa). Progettato con una potenza di 15 kW/rack, ha servito egregiamente per dieci anni. Nel successivo ampliamento è stata adottata una soluzione ibrida **air-to-liquid** — che utilizza l'aria esterna per refrigerare il liquido destinato alle CPU — consentendo di supportare simultaneamente server raffreddati ad aria e server raffreddati a liquido per la ricerca avanzata.

Per governare infrastrutture con migliaia di oggetti su archi temporali così lunghi è imprescindibile un software di inventario. Strumenti open source come **RackTables** permettono di mappare minuziosamente la posizione dei rack, tracciare i log di errore e gestire database multi-brand, garantendo un controllo capillare sull'intera infrastruttura.

---

## Fondamenti della Trasmissione su Fibra Ottica

La rete è il sistema vascolare del data center e risponde a vincoli fisici insuperabili: esiste una capacità massima oltre la quale non si può andare. A differenza dei cavi in rame — in cui gli elettroni viaggiano a circa il 60% della velocità della luce ($0.6c$) — la **fibra ottica** sfrutta la luce stessa, raggiungendo velocità di propagazione nettamente superiori e azzerando la dissipazione termica lungo la tratta.

### Il Principio della Riflessione Totale Interna

Il funzionamento della fibra ottica si basa sulle leggi dell'ottica geometrica. Quando un raggio di luce colpisce la superficie di separazione tra due mezzi, subisce in parte una riflessione e in parte una rifrazione. La **legge di Fresnel** stabilisce che l'angolo di riflessione è pari all'angolo di incidenza. Se però l'angolo di incidenza supera un determinato **angolo limite**, la rifrazione cessa del tutto e si ottiene una *riflessione totale interna*: è esattamente questo fenomeno che intrappola i fotoni all'interno del cavo.

Il nucleo della fibra è rivestito da un materiale minerale riflettente chiamato **Cladding**, che forza i fotoni a rimbalzare contro i bordi senza fuoriuscire. Per la trasmissione non si utilizza luce bianca comune — che un prisma separerebbe nelle diverse lunghezze d'onda — bensì un **laser**, capace di generare un fascio di fotoni uniforme e coerente.

> [!note] Degrado del segnale e fattori esterni
>
> A ogni rimbalzo si perde una frazione microscopica di fotoni a causa delle inevitabili imperfezioni del materiale, imponendo limiti pratici alle distanze di trasmissione. I fattori esterni possono aggravare il degrado: nella rete metropolitana di Pisa, un cavo interrato sul Ponte di Mezzo è stato progressivamente compresso dal passaggio degli autobus urbani, alterando la geometria interna delle fibre e causando una grave degradazione del segnale — risolta solo con costosi scavi stradali.

---

## Tipologie di Fibra Ottica

### Monomodale e Multimodale

Non tutte le fibre ottiche sono uguali, e l'incompatibilità tra sorgenti laser e tipologia di cavo rende fondamentale la corretta identificazione della categoria.

La **fibra monomodale** (*single-mode*) dispone di un *core* estremamente sottile — circa 9 micrometri — che consente un unico percorso rettilineo per la luce, limitando al minimo i rimbalzi e quindi la dispersione del segnale. Questo permette di coprire distanze immense, dai 10 ai 40 chilometri, operando tipicamente a lunghezze d'onda di 1310 nm o 1550 nm. È certificata dagli standard della famiglia **OS**. Pur essendo più costosa e complessa da produrre, garantisce una stabilità impareggiabile: è la scelta preferita non solo per i collegamenti geografici metropolitani, ma anche — in installazioni d'eccellenza come l'Università di Pisa — all'interno del data center stesso.

La **fibra multimodale** (*multi-mode*) possiede un *core* più largo, fino a 50 micrometri, che consente ai fotoni di seguire percorsi multipli. Questo aumenta il numero di rimbalzi e, conseguentemente, la perdita di segnale, rendendola adatta a distanze brevi. Opera a lunghezze d'onda attorno agli 850 nm ed è certificata dagli standard della famiglia **OM**. È la scelta predominante all'interno della maggior parte dei data center per via dei costi di produzione inferiori.

Recentemente sono stati introdotti i **cavi in silicio** (*Silicon Photonics*): non essendo in puro vetro, risultano ancora più economici, sebbene coprano larghezze di banda e distanze inferiori. Si trovano spesso nelle reti domestiche **FTTH** (*Fiber To The Home*), dove il requisito massimo è tipicamente 1 Gigabit al secondo.

| **Standard** | **Tipo** | **Core** | **Distanza Max (1 Gbps)** | **Note** |
|---|---|---|---|---|
| **OM1** | Multimodale | 62.5 µm | 275 m | 10G/40G non supportati |
| **OM2** | Multimodale | 50 µm | 550 m | Miglioramento progressivo |
| **OM3** | Multimodale | 50 µm | 1000 m | Laser ottimizzato 850 nm |
| **OM4** | Multimodale | 50 µm | 550 m a 10G | Standard moderno nei DC |
| **OS1 / OS2** | Monomodale | 9 µm | 10–40 km | Massima distanza, uso metropolitano e DC d'eccellenza |

---

## Connettori Ottici

### SC, LC e Architettura Simplex

Un cavo, per essere utile, deve terminare in un connettore. Esistono due macro-categorie: i **connettori passivi**, semplici terminali meccanici, e i **connettori attivi**, che includono un **transceiver** elettronico che alimenta e converte il segnale per il dispositivo ospite.

Tra i connettori passivi, il **connettore SC** è di dimensioni relativamente ingombranti, ma offre una superficie di contatto ampia che riduce al minimo la dispersione della luce nel punto di giunzione. È lo standard d'elezione per cablaggi metropolitani e collegamenti geografici gestiti dai *carrier* telefonici. Il **connettore LC** è invece estremamente compatto e ottimizzato per l'alta densità di porte: è lo standard assoluto all'interno dei rack dei data center. I vecchi standard FC e ST sono oggi da considerarsi obsoleti.

![Connettori ottici LC (a sinistra) e SC (a destra) a confronto](images/Lc-sc-fiber-connectors-d94aa0.jpg)
*Fig. — I connettori LC e SC sono i due standard dominanti per la fibra ottica: LC per l'alta densità nei rack, SC per i cablaggi metropolitani.*

> [!tip] La direzionalità della fibra ottica
>
> A differenza dei cavi in rame, un singolo filo di fibra ottica trasporta la luce in una sola direzione. Per avere una comunicazione full-duplex è sempre necessaria una **coppia di cavi**: uno per trasmettere (TX) e uno per ricevere (RX). I connettori LC vengono spesso accoppiati tramite una clip meccanica in plastica che può essere sfilata per invertire i due connettori quando è necessario far coincidere correttamente i canali TX e RX sui due estremi della connessione.

---

## Cavi in Rame e Standard Ethernet

### Il Dominio del Rame

Sebbene esistano reti dedicate all'HPC come **InfiniBand**, lo standard Ethernet su cavi in rame ricopre ancora un ruolo dominante, con oltre 70 miliardi di metri di cavo installati nel mondo. I moderni cavi Ethernet utilizzano il connettore **RJ45**, che circa trent'anni fa ha sostituito l'antico RJ11 telefonico. All'interno della guaina si trovano 8 fili intrecciati a formare 4 coppie: le reti a 10 e 100 Megabit ne utilizzavano solo due, rendendo storicamente semplice il passaggio a 1 Gigabit — fu sufficiente abilitare le due coppie rimaste inutilizzate all'interno dello stesso cavo.

L'assemblaggio manuale avviene inserendo i fili secondo uno schema cromatico preciso all'interno del plug RJ45 e utilizzando una pressa crimpatrice, che forza piccoli contatti metallici "a lama" a tagliare la guaina dei singoli fili, stabilendo la connessione elettrica.

![Connettore RJ45 Ethernet](images/Ethernet-RJ45-connector-p1160054-3256e0.jpg)
*Fig. — Il connettore RJ45 con i suoi 8 pin; le 4 coppie di fili intrecciati sono visibili all'interno della guaina.*

### La Sfida dei 10 Gigabit

Il superamento del muro di 1 Gigabit su rame si è rivelato una titanica sfida ingegneristica, legata alle interferenze elettromagnetiche e alle alte frequenze necessarie. La tabella seguente riassume l'evoluzione degli standard:

| **Categoria** | **Capacità Max Pratica** | **Frequenza Max** | **Note** |
|---|---|---|---|
| **Cat 5 / 5e** | 1 Gbps | 100 MHz | Standard storico e diffusissimo |
| **Cat 6** | 1 Gbps (10G a corto raggio) | 250 MHz | Il più installato; i 10G su Cat 6 sono sconsigliati |
| **Cat 6A** | 2.5 / 5 / 10 Gbps | 500 MHz | Massima evoluzione pratica; raccomandato per i 10G in rame |
| **Cat 7 / Cat 8** | Oltre 10 Gbps | Oltre 600 MHz | Raramente adottati; cavi estremamente spessi e rigidi |

> [!warning] Il costo della ridondanza e i limiti del Cat 7/8
>
> Cat 7 e Cat 8 sono teoricamente disponibili ma praticamente inutilizzabili: la rigidità dei cavi li rende simili a "tubi di ferro", rendendo il cablaggio fisicamente impraticabile in ambienti affollati. Sul piano economico, due cavi in rame ad alte prestazioni — necessari per garantire la ridondanza vitale di un server ed eliminare il *single point of failure* — possono pesare sul budget fino a 300 dollari: un costo non trascurabile moltiplicato per centinaia di server.

---

## Gestione del Cablaggio

Gestire razionalmente il cablaggio (*cable management*) non è una questione estetica: è una necessità funzionale critica con impatto diretto sull'efficienza energetica. La tendenza ad aggregare la larghezza di banda ha portato ad avere fino a 4 cavi per server. In un armadio contenente 30 server, ciò si traduce in oltre 120 cavi. Se si aggiunge la prassi comune di ordinare cavi di lunghezze standard — per esempio 2 metri — per uniformare il magazzino, il risultato è un significativo accumulo di cavo in eccesso.

Se i cavi non vengono instradati in percorsi ordinati, formano una barriera fisica sul retro del rack che ostruisce le bocchette di estrazione dell'aria calda prodotta dai server. Il sistema di raffreddamento rileva l'innalzamento anomalo delle temperature e costringe le ventole ad accelerare drasticamente, con conseguente spreco energetico e usura prematura dell'hardware. Il cablaggio disordinato, in altre parole, degrada le prestazioni termiche dell'intero rack.

> [!abstract] Sintesi della lezione
>
> Il data center moderno è un sistema strettamente integrato in cui le scelte di cablaggio, raffreddamento e distribuzione elettrica si condizionano a vicenda. La transizione dal raffreddamento ad aria al liquid cooling segue la crescita della densità di potenza per rack. La fibra ottica è il medium di trasmissione dominante per distanze superiori ai pochi metri, con la scelta tra monomodale e multimodale che dipende dalla distanza e dal budget. Il rame rimane rilevante per i collegamenti finali, ma Cat 6A è oggi il limite pratico oltre il quale la fibra diventa obbligata. Il cable management, infine, non è un dettaglio: un cablaggio disordinato degrada le prestazioni termiche dell'intero rack.

