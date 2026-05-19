# Architettura e Gestione dei Datacenter

La lezione esplora l'infrastruttura fondamentale dei datacenter moderni: non solo i componenti tecnologici, ma le sfide ingegneristiche, fisiche e legali legate alla loro progettazione. Il filo conduttore è la tensione permanente tra due esigenze opposte — la **ridondanza** totale richiesta dall'utente e l'**efficienza** economica richiesta dal fornitore — che determina ogni scelta progettuale, dal pavimento ai cavi di rame.

## Fondamenti e Vincoli della Progettazione

### La Complessità del Datacenter e la Ricerca dell'Efficienza

Un datacenter non è un ambiente complesso per l'elevato numero di componenti diversi; alla base, gli "ingredienti" sono pochi: un edificio che ospita un insieme di armadi di server (**rack**), l'alimentazione elettrica, gli apparati di rete, il cablaggio e un sistema di raffreddamento (**cooling**). La vera complessità deriva dalle enormi risorse necessarie per farlo funzionare e dalla continua ricerca dell'efficienza.

Fino a poco tempo fa, l'aria veniva usata come principale mezzo di raffreddamento non perché fosse il più efficiente in assoluto, ma perché era economica e immediatamente disponibile. Oggi questa scelta viene messa in discussione man mano che la densità energetica dei rack cresce.

> [!tip] Efficienza come metrica economica
>
> Intel dimostrò che modificare la temperatura operativa di design delle CPU di un solo grado Celsius poteva generare risparmi energetici per milioni di dollari. Più di recente, Dell immette sul mercato **AI rack** da 200 kW progettati per operare a 40°C: la soglia elevata riduce drasticamente l'energia spesa per il raffreddamento, e poiché il rack è fisicamente sigillato, gli operatori non devono lavorare in quelle temperature.

### Il Paradigma "Always On" e i Tre Pilastri della Sicurezza

I fornitori di servizi cloud non possono permettersi di spegnere i datacenter per la manutenzione: gli utenti pretendono disponibilità 24/7. L'interruzione del servizio è percepita come un evento eccezionale — basti pensare che se i server Google vanno offline anche solo per mezz'ora, la notizia finisce sui telegiornali di tutto il mondo.

Creare un datacenter perfetto e infallibile è però impossibile, perché la ridondanza ha costi altissimi. Le aziende devono quindi valutare quante copie dei dati siano necessarie in base al rischio che intendono tollerare. Una disconnessione momentanea genera frustrazione ma è tollerata; perdere anche un solo file nello storage è considerato un errore imperdonabile.

> [!definition] CIA Triad — Disponibilità, Integrità, Riservatezza
>
> La progettazione dei servizi si basa su tre pilastri normativi e tecnici:
> - **Disponibilità** (*Availability*): il servizio deve essere sempre raggiungibile.
> - **Integrità** (*Integrity*): i dati non devono essere corrotti o alterati.
> - **Riservatezza** (*Confidentiality*): i dati non devono essere accessibili a soggetti non autorizzati.
>
> Il [[GDPR]] sanziona la violazione di **tutti e tre** i pilastri: non solo le fughe di dati, ma anche la corruzione e la mancata disponibilità.

> [!example] Università La Sapienza — violazione senza furto di dati
>
> In seguito a un grave attacco informatico che ha bloccato i servizi per una settimana senza sottrarre materialmente dati, La Sapienza ha dovuto comunque segnalare la violazione alle autorità, proprio a causa della mancata **disponibilità** dei propri sistemi. Nel mondo digitale, l'incapacità di accedere ai propri dati o ai sistemi di pagamento equivale a un danno economico tangibile.

### Disastri, Ridondanza e Normative Geografiche

Per garantire la continuità, le infrastrutture devono poter essere aggiornate in ogni parte senza mai interrompere il servizio. Le normative impongono vincoli fisici stringenti: i datacenter devono essere mantenuti a una distanza di sicurezza di almeno **10 chilometri** l'uno dall'altro, per proteggersi da catastrofi che colpiscono una specifica area.

> [!warning] Il caso di Bruxelles
>
> Un provider aveva collocato due datacenter "distinti" all'interno della stessa piazza cittadina. Un vasto incendio li rase al suolo entrambi, costringendo l'azienda a comunicare ai clienti la **perdita totale** dei dati. La distanza geografica tra i siti non è una preferenza di design, è un requisito di sopravvivenza.

A questi vincoli si aggiungono obblighi legali di posizionamento: il **GDPR** impone di mantenere i dati all'interno dei confini dell'Unione Europea. Le grandi piattaforme cloud mitigano i rischi investendo in infrastruttura propria: Microsoft, ad esempio, possiede una rete globale di cavi oceanici privati, riducendo la dipendenza tecnica da terzi. Per evitare *single points of failure*, queste aziende stipulano contratti con cinque diversi operatori di rete, pretendendo che non condividano nemmeno un segmento di infrastruttura tra di loro; analogamente, si interfacciano con fornitori di energia che, per contratto, devono attingere da centrali elettriche rigorosamente distinte.

> [!example] Netflix e il tornado nel New Jersey
>
> Nonostante ogni precauzione, disastri su scala globale accadono. La piattaforma Netflix è rimasta inaccessibile per quasi una settimana quando un devastante tornado ha raso al suolo le strutture Amazon nel New Jersey, privando l'intera macro-area di energia elettrica e distruggendo le facility fisiche.

---

## Vincoli Fisici e Legacy Tecnologica

### I Limiti Fisici della Progettazione (Hard Thresholds)

A differenza del lavoro di un informatico — dove si applica il principio dell'induzione matematica per scalare algoritmi all'infinito — il mondo dell'ingegneria comporta limitazioni intrinseche che non possono essere scavalcate.

> [!definition] Hard Threshold
>
> Soglia fisica oltre la quale un design non può essere semplicemente "ingrandito", ma è necessario riprogettare radicalmente la tecnologia da zero usando approcci diversi.

Un esempio concreto: in elettronica un **relè** elettromagnetico è utile per accendere o spegnere la corrente per dispositivi comuni, ma non viene mai usato in sistemi pesanti come gli ascensori. L'enorme quantità di ampere richiesta fonderebbe in pochi istanti la bobina di rame del componente. Questa logica si ripete a ogni scala nella progettazione di datacenter: il cablaggio elettrico, il raffreddamento, la struttura portante — ciascuno presenta soglie oltre le quali occorre cambiare tecnologia.

### L'Eredità degli Standard e il Pavimento Flottante

Molte soluzioni di ingegneria dei datacenter odierni si basano su standard fisici vecchi di decenni, mantenuti in vita per evitare i costi enormi di riprogettazione e sostituzione di massa. Nel mondo del networking, avendo già posato oltre 70 miliardi di metri di cavo Ethernet (RJ45), si è preferito forzare le vecchie architetture via cavo a spingere 2.5 o 5 Gbps, invece di ricablare interi edifici in vista delle moderne antenne Wi-Fi ad alta velocità. Questo stallo ha prodotto una scissione: i "campus network" sono rimasti sull'Ethernet standard (spesso alimentando i dispositivi tramite **PoE**, *Power over Ethernet*), mentre il cuore dei datacenter è migrato verso standard specifici più veloci e stabili.

Tra i residui tecnologici adattati vi è il **pavimento flottante** (*floating floor*): una griglia rialzata su piedistalli metallici incrociati, con mattonelle rimovibili posate sopra.

> [!definition] Floating Floor (Pavimento Flottante)
>
> Struttura rialzata di un datacenter composta da piedistalli metallici e mattonelle rimovibili. Nei vecchi uffici le mattonelle reggevano ~500 kg/m²; nei datacenter moderni, dove lo storage pesa molto di più, si usano pannelli in polvere di marmo compattata strutturati per reggere da **1 a 1,5 tonnellate per metro quadrato**.

![Pavimento flottante di un datacenter con mattonella sollevata](images/Tile-lifter-in-use-raised-floor-665fb3.jpg)
*Fonte: Wikimedia Commons (Jonathan Lamb, Public Domain) — Mattonella del pavimento flottante sollevata con ventosa; sotto sono visibili cavi e condotte.*

Mantenere il pavimento flottante offre due vantaggi ingegneristici fondamentali:

1. **Accesso immediato** a tutta l'infrastruttura elettrica e idraulica nascosta sotto il pavimento, senza dover spostare i rack.
2. **Condotto di raffreddamento**: la cavità sotto il pavimento diventa un plenum isolato per spingere enormi quantità di aria fredda verso l'alto, attraverso mattonelle forate posizionate strategicamente davanti ai rack.

Tenere i passaggi separati sotto il pavimento evita anche potenziali cortocircuiti: il pericolo di innescare incendi è severo, specie in presenza di batterie al litio — notoriamente inestinguibili con le procedure standard e severamente vietate nelle stive degli aerei proprio per questo motivo.

---

## Strategie di Raffreddamento

### Aria, Acqua e Olio

Per massimizzare l'efficienza termica, l'intero edificio del datacenter viene isolato all'estremo dall'ambiente esterno. Non mancano eccezioni creative: il complesso di Aruba, ad esempio, immette liberamente l'aria gelida esterna in inverno ed espelle il flusso caldo verso fuori, risparmiando energia.

Il principio fondamentale del raffreddamento a rack è la separazione fisica tra **corridoio freddo** (*cold aisle*) — da cui i server aspirano l'aria fresca — e **corridoio caldo** (*hot aisle*) — da cui espellono il calore. Questa separazione evita che l'aria fredda e quella calda si mescolino prima di raggiungere i server, massimizzando l'efficienza termica.

![Diagramma hot aisle / cold aisle con contenimento del corridoio freddo](images/Cold-Aisle-Containment-e2b761.png)
*Fonte: Wikimedia Commons (CC BY-SA 3.0 DE) — Schema di contenimento del corridoio freddo: il flusso blu (aria fredda) entra dal basso, attraversa i server e fuoriesce come flusso rosso (aria calda) sul corridoio opposto.*

Dato che la logistica delle condotte idrauliche sta diventando l'elemento centrale delle server farm moderne, si privilegia sempre di più l'acqua per le sue eccezionali proprietà termiche. Ricalcando il meccanismo biologico del sudore umano, i datacenter più grandi impiegano attivamente la **dispersione tramite evaporazione**. Nonostante sia una tecnica incredibilmente efficiente, il suo costo ambientale è elevato: circa l'**80% dell'acqua iniettata viene evaporata**. Sebbene questa acqua ritorni nell'atmosfera come pioggia senza essere distrutta, la dispersione massiccia locale crea sacche artificiali di umidità che rischiano di alterare il microclima circostante.

> [!warning] Il problema idrico negli USA
>
> I massicci impieghi idrici agro-industriali combinati a quelli dei datacenter hanno sostanzialmente prosciugato le risorse basate sul fiume Colorado. Questo ha spinto alcune aziende a pianificare la migrazione delle proprie sedi verso il Sud America — Argentina in primis — in cerca di riserve idriche intoccate. L'acqua usata deve essere desalinizzata e ripulita a fondo, il che aggiunge ulteriore complessità logistica.

Un'alternativa d'avanguardia è la **total immersion cooling**: i server vengono immersi in vasche ricolme di olio minerale o vegetale. A differenza dell'acqua, l'olio isola chimicamente i contatti e non conduce elettricità, disperdendo il calore con grande efficacia — tecnica usata anche per overclock estremi nei PC da gaming.

> [!note] Limiti dell'immersion cooling
>
> - L'**olio vegetale** tende rapidamente a irrancidire, sprigionando odori acri.
> - L'**olio minerale** è molto costoso da approvvigionare in quantità industriali.
> - Ogni operazione di manutenzione su schede madri immerse diventa una procedura sporca e complessa.
>
> Per queste ragioni, l'industria ha preferito affinare il raffreddamento localizzato tramite tubazioni ad acqua pura anti-versamento, accettandone la complessità tecnica.

---

## Infrastruttura Elettrica

### Scale Up vs Scale Out

> [!definition] Scale Up vs Scale Out
>
> - **Scale Up**: si aumenta la capacità di un singolo apparato (es. si aggiunge RAM a un server esistente).
> - **Scale Out**: si replica il numero di macchine separate per distribuire il carico (es. si aggiungono nuovi server al cluster).

Nel contesto dell'approvvigionamento elettrico, un intero edificio è **costretto a operare in logica Scale Up**: all'aumentare del consumo dell'infrastruttura, occorrono cavi di rame via via più voluminosi e spessi. Scalare elettricamente è dolorosamente costoso, soprattutto per il prezzo del rame. A titolo di esempio, il cablaggio per supportare soli 80 kW di picco in un piccolo complesso accademico — trascinando il fascio dalla cabina esterna ai server — è arrivato a costare circa **25.000 €**. Per minimizzare la resistenza elettrica intrinseca con correnti molto elevate, i tecnici sostituiscono i fasci di cavi intrecciati con **sbarre di rame pieno** (*busbars*), singole e dritte.

### Fondamenti Elettrici: Potenza, Corrente Alternata e Distribuzione

Un datacenter richiede una concentrazione energetica enorme, che può essere fornita da rinnovabili, combustibili fossili o nucleare. Nelle logiche macro-aziendali americane in espansione, si intravede l'uso di reattori di ultimissima generazione — tecnologicamente più puri e sicuri, con materiali radioattivi come il torio — che generano circa un decimo delle scorie rispetto all'uranio tradizionale.

Per gestire questo flusso, l'ingegnere deve dominare il concetto di **potenza effettiva**, che non si ricava semplicemente dai Volt, ma dal prodotto:

$$
P_{\text{apparente}} = V \times I \quad [\text{VA}]
$$

$$
P_{\text{reale}} = V \times I \times \cos\phi \quad [\text{W}]
$$

dove $\cos\phi$ (**Cosfi**, o *fattore di potenza*) è il coseno dell'angolo di sfasamento tra tensione e corrente. I moderni trasformatori *switching* — presenti sia nei server farm sia nel piccolo alimentatore del laptop — hanno un Cosfi variabile: scende a circa **0.56** quando i componenti sono inattivi (*idle*), ma sale fino a **0.96** sotto carico computazionale intenso.

> [!tip] Perché il Cosfi è cruciale negli acquisti
>
> Durante le gare di acquisto per apparecchiature industriali, esigere trasformatori con un elevato *power factor* è una scelta economicamente discriminante: apparecchi con basso Cosfi disperdono una quota significativa dell'energia prelevata dalla rete, aumentando i costi operativi nel lungo periodo.

Nonostante l'elettronica digitale lavori esclusivamente in **Corrente Continua** (*DC — Direct Current*), tutti i datacenter globali ricevono energia in **Corrente Alternata Trifase** (*AC — Alternating Current*), standardizzata a **380 V** in Europa. Le ragioni sono storiche e fisiche: far transitare enormi flussi di corrente continua scalda i conduttori in modo molto più pericoloso, e le scosse in DC sono fisiologicamente più letali di quelle in AC a parità di energia. Sarà ogni singolo server, nell'ultima maglia della rete, a convertire la corrente alternata in continua attraverso il proprio alimentatore interno.

> [!definition] UPS (Uninterruptible Power Supply)
>
> Componente al vertice della piramide di distribuzione elettrica del datacenter. Non si tratta dei piccoli dispositivi domestici anti-blackout, ma di **interi armadi e batterie industriali** destinati a stabilizzare la linea e garantire continuità in caso di interruzione della rete esterna. Gli interruttori di sezionamento — talmente potenti da non poter essere azionati manualmente a mani nude — vengono commutati da **molle metalliche precompresse**, che il meccanismo rilascia automaticamente per garantire la massima velocità di intervento e proteggere il personale.

> [!definition] PDU (Power Distribution Unit)
>
> Centraline di gestione che suddividono progressivamente il carico elettrico lungo la gerarchia di distribuzione. La rete elettrica segue un'architettura ad albero: dalla cabina esterna si scende attraverso PDU di piano, fino ai **Rack PDU** dove ogni server inserisce il proprio cavo di alimentazione.

L'architettura di distribuzione elettrica segue quindi questo percorso gerarchico:

**Rete Trifase Esterna → UPS → PDU di edificio → PDU di piano → Rack PDU → Server**

> [!abstract] Sintesi — Infrastruttura Elettrica
>
> La progettazione elettrica di un datacenter è vincolata da hard threshold fisici non aggirabili: cavi più grossi, costosi e difficili da gestire. La corrente arriva dall'esterno in AC trifase a 380 V, viene stabilizzata dall'UPS e distribuita gerarchicamente tramite PDU fino ai server, che la convertono in DC internamente. Il fattore di potenza è una metrica economica critica da valutare in fase di acquisto delle apparecchiature.

---

## Glossario

> [!definition] Scale Up / Scale Out
>
> Tecniche per rispondere al fabbisogno crescente di risorse. **Scale Up** aumenta la capacità di un singolo nodo (più RAM, CPU più potente); **Scale Out** distribuisce il carico su un numero maggiore di nodi separati. In ambito elettrico, i datacenter sono forzati a operare in Scale Up, con tutti i costi che ne derivano.

> [!definition] CIA Triad (Disponibilità, Integrità, Riservatezza)
>
> Il trittico fondamentale su cui si basa la progettazione protettiva dei servizi digitali. Garantire **Disponibilità** significa che il servizio è sempre raggiungibile; **Integrità** significa che i dati sono corretti e non manomessi; **Riservatezza** significa che solo i soggetti autorizzati possono accedervi. Il GDPR sanziona la violazione di ciascuno dei tre pilastri.

> [!definition] Fattore di Potenza (Cosfi, $\cos\phi$)
>
> Rapporto tra la potenza reale (W) e la potenza apparente (VA): $\cos\phi = P / S$. Quantifica quanto efficacemente l'energia prelevata dalla rete viene effettivamente convertita in lavoro utile. Un Cosfi basso indica dispersione energetica. Nei trasformatori switching dei server, varia tra ~0.56 (idle) e ~0.96 (sotto carico).

> [!definition] Floating Floor (Pavimento Flottante)
>
> Struttura rialzata del datacenter su piedistalli metallici, con mattonelle rimovibili che reggono fino a 1–1,5 t/m². Serve un duplice scopo: accesso facilitato all'infrastruttura nascosta sotto il pavimento, e creazione di un plenum per la distribuzione dell'aria fredda di raffreddamento verso i rack.

> [!definition] UPS (Uninterruptible Power Supply)
>
> Primo stadio di ingresso della rete elettrica nel datacenter. Sistema industriale di grosse dimensioni — non il piccolo dispositivo domestico — composto da batterie e meccanismi di commutazione automatica, progettato per garantire continuità di alimentazione e proteggere l'intera infrastruttura da fluttuazioni e blackout della rete esterna.

