# Piattaforme IoT

## Identificazione e Discovery

L'**identificazione** fornisce un metodo univoco per riconoscere le entità all'interno di una piattaforma. Esistono diversi standard a seconda del contesto operativo: gli indirizzi IP per Internet, l'**MSISDN** nella telefonia, gli **URI** sul web, l'**OID** nelle telecomunicazioni e gli **UUID** nei sistemi informatici, molto utilizzati anche nello standard Bluetooth.

La **discovery** è il meccanismo attraverso il quale la piattaforma individua dispositivi, risorse o servizi all'interno di un'infrastruttura IoT, permettendo di interrogarne in modo dinamico le proprietà e le caratteristiche offerte.

---

## Gestione dei Dispositivi

La fase di gestione dei dispositivi parte dall'inizializzazione e configurazione, attività che includono il pairing, la definizione delle impostazioni di sicurezza con la relativa distribuzione delle chiavi crittografiche, la calibrazione dei trasduttori e la localizzazione spaziale degli endpoint. La piattaforma IoT si occupa anche di gestire l'aggiornamento automatico del software e del firmware, di monitorare in tempo reale lo stato dell'hardware — come il livello della batteria e la temperatura interna — e di effettuare attività di diagnostica per il rilevamento di eventuali guasti.

È inoltre contemplato il controllo remoto degli apparati per forzare riavvii o attivare specifiche periferiche, e la manutenzione di accurati log di sistema a scopo di audit. Questi processi di management poggiano spesso su standard industriali consolidati come **OMA DM** e **OMA LWM2M** per terminali e sensori, e **BBF TR-069** per apparecchiature destinate agli utenti finali.

---

## Astrazione, Semantica e Composizione dei Servizi

L'**astrazione** e la **virtualizzazione** nascondono la complessità fisica dell'hardware per trattare i dispositivi IoT come veri e propri servizi, introducendo concetti architetturali chiave come il **digital twin** per l'Industry 4.0.

> [!definition] Digital Twin
>
> Il digital twin è una rappresentazione virtuale di un oggetto o sistema fisico, mantenuta sincronizzata con la sua controparte reale. Nell'Industry 4.0 permette di simulare, monitorare e ottimizzare il comportamento dei dispositivi fisici senza interagire direttamente con essi.

La **semantica** attribuisce significato strutturato ai dati raccolti, permettendo di rappresentare il contesto operativo degli apparati per abilitare un ragionamento logico e favorire l'elaborazione dei flussi informativi da parte dell'intelligenza artificiale.

La **service composition** si incarica di aggregare i servizi di svariati dispositivi IoT e di componenti software preesistenti per dare origine a funzionalità composite o catene di data analytics complesse.

---

## Database NoSQL e MongoDB

I flussi informativi ad alta intensità tipici dell'IoT richiedono soluzioni di archiviazione flessibili e performanti, motivo per cui ci si affida sovente ai database **NoSQL**, pensati per applicazioni real-time e scenari Big Data. I sistemi NoSQL offrono prestazioni eccellenti scalando in modo orizzontale su cluster di macchine e hanno un design più snello e destrutturato rispetto all'approccio relazionale SQL classico.

**MongoDB**, ad esempio, salva le proprie entità non come record tabellari ma come documenti formattati in una sintassi molto vicina al JSON, potendo incorporare array e oggetti nidificati per ridurre l'esecuzione di operazioni costose come le join. I documenti vengono logicamente raggruppati in **collection** — assimilabili alle tabelle — pur non dovendo condividere necessariamente la medesima struttura rigida. Le query su un database MongoDB consentono l'applicazione flessibile di criteri di filtraggio, l'utilizzo di proiezioni per definire i campi da ritornare e l'impiego di modificatori per l'ordinamento e la manipolazione del risultato finale.

---

## Problematiche Tecniche nell'IoT

Lo sviluppo delle reti IoT incontra ostacoli tecnologici che spaziano dall'efficienza energetica alla garanzia delle prestazioni in sistemi su larga scala, passando per la personalizzazione e l'elaborazione dei segnali. È prioritario gestire meccanismi efficienti di comunicazione e **brokerage** capaci di mettere agevolmente in collegamento la molteplicità di produttori di informazioni — i sensori — con i relativi consumatori, siano essi attuatori o servizi di astrazione superiori.

Si impone la necessità di una forte standardizzazione nei formati dei dati a garanzia di interoperabilità. In tale direzione operano protocolli a vari livelli di stack: **Bluetooth**, **IEEE 802.15.4** e **ZigBee** per i livelli più bassi o di rete, affiancati a protocolli applicativi come **MQTT** e **CoAP**. Sussistono inoltre notevoli criticità in merito ai vincoli di latenza e affidabilità generati dal dover instradare su mezzi spesso instabili un traffico di letture veloci, massicce ed eterogenee, sfide che stimolano l'adozione di topologie edge e fog.

---

## Edge, Fog e Cloud Computing

Mentre il **Cloud** gestisce grandi moli di informazioni supportando un tempo di risposta transazionale tramite infrastrutture cablate, in periferia opera l'**Edge Computing**. L'Edge costituisce l'estremità della rete composta prettamente da sensori e attuatori, i quali interagiscono tra loro o convergono tramite gateway dedicati verso la rete internet, offrendo la possibilità di azioni locali real-time nell'ordine di grandezza dei millisecondi.

Il **Fog Computing** risponde a un'esigenza contrapposta a quella dell'accentramento del Cloud, posizionando le risorse di storage e di calcolo in prossimità dei dispositivi emettitori. L'elaborazione a livello Fog filtra, formatta e riduce i volumi dei flussi di rete grezzi estraendo informazioni essenziali prima che queste vengano inviate ai livelli alti dell'infrastruttura, mitigando così l'occupazione di banda, risolvendo colli di bottiglia e abbassando le latenze.

---

## Intelligenza Artificiale e TinyML

L'**intelligenza artificiale** (AI) ricerca modelli comportamentali ottimali operando attraverso logiche a regole inferenziali — curated knowledge basata su reti semantiche e relazioni causa/effetto — o, più comunemente nell'IoT, mediante il **Machine Learning**. Il Machine Learning sostituisce l'approccio classico in cui il programmatore stila l'algoritmo con l'analisi induttiva tramite insiemi di dati. Esposto ad appositi dataset di addestramento e validazione, il sistema definisce un modello con spiccate capacità di generalizzazione, adatto a processare e riconoscere misurazioni o scenari mai incontrati prima.

Tra le principali famiglie algoritmiche si trovano l'**Unsupervised Learning** (usato per cercare in autonomia pattern nascosti nei dati), il **Supervised Learning** (che sfrutta accoppiamenti dati-risultato atteso per elaborare previsioni) e il **Reinforcement Learning** (che evolve attraverso un meccanismo di rinforzo o ricompensa).

> [!note] TinyML
>
> Il paradigma **TinyML** permette di miniaturizzare e implementare modelli di Machine Learning direttamente su processori IoT a bassa potenza, portando capacità inferenziali all'edge senza dipendere da connettività cloud. Questo apre scenari di elaborazione locale estremamente efficienti dal punto di vista energetico.

---

## Federated Learning

> [!definition] Federated Learning
>
> Il **Federated Learning** è un'architettura di intelligenza artificiale distribuita che ovvia alla necessità del Machine Learning tradizionale di accentrare tutti i dati di addestramento su un singolo server. Nel modello federato, ciascun dispositivo edge addestra autonomamente il proprio modello usando dati generati e mantenuti esclusivamente in locale. I soli parametri aggiornati — e non i dati grezzi — vengono inoltrati a un server di aggregazione che ricompila un nuovo modello globale più accurato e lo propaga nuovamente a tutti gli endpoint in un ciclo di perfezionamento ininterrotto.

Questo approccio offre enormi vantaggi in termini di scalabilità e tutela della privacy, poiché i dati sensibili non lasciano mai il dispositivo. Tuttavia il sistema non è esente da rischi.

> [!warning] Attacchi al Federated Learning
>
> Il Federated Learning è soggetto ad attacchi di **poisoning** (avvelenamento). L'avversario può inquinare i dati locali corrompendo le associazioni e inserendo falle volontarie (**Data poisoning**), oppure manipolare direttamente i gradienti e i pesi prima di inviarli all'aggregatore centrale (**Model poisoning**), inquinando silenziosamente l'intera rete. Per difendersi si applicano metodologie di rilevazione anomalie basate sul comportamento atteso dei modelli conformi, meccanismi di reputation e auditing tramite Blockchain.

---

## IoT e Blockchain

La **Blockchain** rappresenta per l'ecosistema IoT un radicale cambio di paradigma, offrendo un registro pubblico distribuito in cui nessuna entità governa in maniera centralizzata lo storico delle transazioni. Le iscrizioni sulla blockchain non sono modificabili e rendono i dati *tamper-evident*, certificando un unico punto della verità per tutti i partecipanti al network.

Uno degli scenari d'uso più frequenti nell'IoT è il controllo della **supply chain**: reti di sensori analizzano lo stato delle merci per tutte le fasi di produzione e transito e firmano le conformità sotto forma di **smart contract** direttamente sul registro distribuito condiviso tra le varie aziende della catena logistica.

---

## Interoperabilità e Standard

L'assenza di standardizzazione produce architetture in totale isolamento, meglio note come **vertical silos**, nelle quali l'intera architettura software e hardware scaturisce da un'unica entità monopolistica e lavora senza poter dialogare con il mondo esterno. Questo tipo di business model vincola il cliente a un singolo produttore creando il fastidioso **vendor lock-in**, causando elevati costi in caso di migrazioni e rendendo di fatto incompatibili gli apparati di diversi costruttori.

Per favorire l'interoperabilità, vi è un continuo proliferare di standard legati al mondo wireless: dai corti e medi raggi in radiofrequenza con le varie iterazioni di **IEEE 802.11** (WiFi), Bluetooth e ZigBee, alle vaste coperture tipiche della famiglia cellulare (2G, 3G, 4G, 5G). La transizione allo standard **5G** apporta particolare valore grazie alle tre macro-aree di applicazione previste:

| Macro-area | Sigla | Applicazione tipica |
|---|---|---|
| Enhanced Mobile Broadband | eMBB | Video HD, realtà virtuale |
| Massive Machine Type Communication | mMTC | Smart city, decine di migliaia di sensori |
| Ultra Reliable and Low Latency Communications | URLLC | Automazione industriale, guida autonoma |

Alle problematiche puramente fisiche si aggiunge la frammentazione nel campo software middleware e nei protocolli applicativi, per i quali diventa spesso obbligatorio inserire nodi di **integration gateway** preposti non solo alla conversione sintattica dei pacchetti, ma anche alla mappatura di comportamenti logici per allineare le diversificate configurazioni presenti sul mercato.

---

## Sicurezza

Una problematica endemica nel mondo IoT riguarda la sicurezza informatica limitata o precaria presente all'interno dei **constrained devices**, i dispositivi embedded di consumo. La forte competizione di mercato e l'incentivo a realizzare l'hardware nel minor tempo e a basso costo si traducono in dispositivi vulnerabili, privi di validi meccanismi integrati per il rilascio di patch sistematiche.

Numerose debolezze derivano da sviste grossolane quali l'adozione di interfacce vulnerabili, la mancanza di adeguata protezione fisica o di crittografia, e soprattutto dall'uso di password in chiaro o scritte direttamente nel codice nativo (**hard-coded credentials**). I requisiti imposti dai principali standard internazionali richiedono esplicitamente di salvaguardare l'integrità, l'affidabilità e la confidenzialità di tutti i dati elaborati o veicolati, fornendo audit adeguati per contrastare minacce interne ed esterne.

Poiché numerosi endpoint faticano a gestire la mutua autenticazione per limiti puramente tecnici, le piattaforme demandano la messa in sicurezza ai **gateway** posti ai bordi della rete, incaricati di validare transazioni, decodificare flussi criptati e gestire dinamicamente eventuali policy centrali, in ottemperanza ai rigidi dettami previsti dalla protezione della privacy personale degli utenti finali.

---

> [!question] Possibili domande d'esame
>
> - Quali sono le differenze tra Edge Computing, Fog Computing e Cloud Computing nell'IoT, e in quali scenari è preferibile ciascun approccio?
> - Come funziona il Federated Learning e quali sono i principali attacchi a cui è soggetto?
> - Perché i database NoSQL sono preferiti ai database relazionali nei contesti IoT? Quali vantaggi offre MongoDB?
> - Cosa si intende per vendor lock-in e vertical silos? Come il 5G e gli standard di interoperabilità cercano di ovviare a questi problemi?
> - Quali sono le principali vulnerabilità di sicurezza nei dispositivi IoT embedded e come vengono mitigate a livello di piattaforma?
