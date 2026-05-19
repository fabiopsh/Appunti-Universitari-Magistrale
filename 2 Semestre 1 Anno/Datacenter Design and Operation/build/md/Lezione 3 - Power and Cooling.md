# Gestione dell'Energia e del Raffreddamento nei Data Center

L'infrastruttura di un Data Center moderno è un ecosistema estremamente complesso, paragonabile a un'orchestra in cui ogni elemento — alimentazione, reti, raffreddamento e rack — deve funzionare in perfetta armonia con gli altri. In questo capitolo esploreremo le dinamiche fisiche, economiche e gestionali che governano alimentazione e raffreddamento: dal mercato dei fornitori e dalle criticità della manutenzione, al rischio del surriscaldamento, ai parametri di efficienza energetica come il **PUE** (*Power Usage Effectiveness*), fino all'evoluzione delle architetture di condizionamento ad aria con i sistemi **CRAC**.

---

## Il Mercato dei Vendor e la Strategia di Acquisizione

Acquistare le singole parti di un Data Center per assemblarle autonomamente è un errore strategico considerevole. Poiché ogni componente influenza direttamente gli altri, è fondamentale affidarsi a ecosistemi integrati forniti da vendor specializzati. Al giorno d'oggi ogni parte del Data Center è considerabile "attiva": anche elementi passivi come rack e schede di controllo sono dotati di display e interfacce accessibili via protocollo HTTP.

Esistono pochi fornitori al mondo capaci di gestire le competenze necessarie per installazioni ad alta potenza. **Schneider Electric** domina le installazioni elettriche e ha acquisito **APC** (storica azienda specializzata in rack e gruppi di continuità). Un altro colosso è **Vertiv** (ex Emerson), nata come produttrice di *chiller* (refrigeratori industriali). In Italia il mercato è presidiato da **Riello** per sistemi elettrici e UPS, e **Climaveneta** per i chiller.

---

## La Manutenzione e il Ciclo di Vita

Quando si acquista un Data Center, in realtà non si compra solo hardware: si "sposa" il produttore attraverso un contratto di manutenzione. Il modello di business è analogo a quello delle automobili di fascia alta — BMW o Mercedes — dove l'accesso alle centraline e la riparazione richiedono strumenti proprietari che solo il produttore può fornire.

> [!warning] Costi dell'infrastruttura
>
> I costi sono imponenti: la ristrutturazione di un DC di piccole dimensioni parte da circa **250.000–300.000 €**, mentre impianti più grandi oscillano tra **2 e 5 milioni di €**. Acquistare un pezzo di ricambio da tenere in magazzino — per esempio un chiller da **100.000 €** — è economicamente insostenibile e logisticamente impraticabile per via degli ingombri fisici.

I contratti di manutenzione garantiscono interventi "Next Business Day" o entro **4 ore**, con monitoraggio remoto 24/7. Il costo annuo di questi contratti oscilla tra il **10% e il 30%** dell'investimento originale. Se si decide di non rinnovare, dopo alcuni anni i vendor non garantiscono più la disponibilità dei ricambi — specialmente per macchine con oltre **12 anni** di vita — costringendo di fatto l'operatore a un costoso aggiornamento totale. Il ciclo di vita tipico di un intero Data Center si aggira intorno ai **10 anni**.

---

## Surriscaldamento: Una Minaccia Critica per il Silicio

Dal punto di vista concettuale, un Data Center richiede le stesse risorse di un'abitazione domestica: rete, corrente, raffreddamento. La differenza è nella scala: mentre un contatore domestico eroga **3–5 kW**, un Data Center necessita facilmente di **1 Megawatt** per alimentare migliaia di server.

Questo fabbisogno energetico massiccio si traduce in un enorme rilascio di calore. Se il sistema di raffreddamento si guasta, la situazione degenera rapidamente: le ventole dei server, dotate di sensori termici, percepiscono l'aumento di temperatura e accelerano per compensare. Ma spostando aria già calda, il loro stesso attrito immette ulteriore energia termica nella stanza. Si innesca un **effetto esponenziale**: in assenza di aria fredda, la temperatura della sala può raggiungere **60–70°C** in tempi brevissimi, a tal punto che l'unica soluzione di emergenza è l'apertura fisica delle porte dell'edificio.

> [!warning] Surriscaldamento vs. blackout
>
> Il surriscaldamento è storicamente più pericoloso di una semplice interruzione di corrente. Un blackout tradizionale danneggiava i dischi rigidi meccanici — la testina rischiava di graffiare il piatto al momento dello stop improvviso — ma con la diffusione degli **SSD** questa mortalità si è drasticamente ridotta. Il calore estremo, invece, può sciogliere i componenti plastici e danneggiare irreparabilmente il **silicio** delle componenti elettroniche, rendendole inutilizzabili.

> [!example] La termodinamica del rack a 40°C
>
> Alcuni vendor certificano che i server, con vita utile media di **5 anni**, possano operare per **40 giorni all'anno a 40°C**. Sembra un limite elevato, ma bisogna considerare il **Delta T** del rack: la differenza di temperatura tra l'aria fredda in ingresso (*inlet*) e l'aria espulsa sul retro è tipicamente di circa **15°C**. Se l'aria in ingresso è a 40°C, sul retro del rack si raggiungono facilmente 55–60°C. I dischi meccanici per *cold storage* (archiviazione economica) possono arrivare a temperature superficiali operative di **100°C** — letteralmente abbastanza calde da cuocerci sopra.

> [!example] Il guasto dei chiller pisani
>
> Durante una settimana di luglio con temperature esterne superiori ai **38°C**, i vecchi chiller del Data Center pisano — progettati in anni in cui quei picchi non si registravano — sono andati in blocco termico perché le loro dimensioni non consentivano di dissipare un tale carico. In sole **due ore** la sala macchine ha raggiunto i **50°C**, costringendo a spegnere tutto e a versare letteralmente acqua fredda sulle scocche dei chiller per poterli riavviare. Questo episodio dimostra quanto i servizi Internet siano vulnerabili alle condizioni fisiche dell'ambiente.

---

## Anomalie Elettriche e i "Bug"

Non solo il calore, ma anche le interruzioni elettriche causano gravi disservizi. I **UPS** (*Uninterruptible Power Supply*, gruppi di continuità) intervengono durante le micro-interruzioni di rete per dare il tempo ai generatori diesel di avviarsi. In un caso specifico, continue micro-interruzioni da **10–15 secondi** non furono tollerate dall'elettronica di controllo dei chiller — non messi sotto UPS per motivi di costo. I chiller, interpretando quel disturbo come un pericolo, si spensero autonomamente, causando la caduta di tre impianti di refrigerazione. La soluzione fu l'acquisto di un UPS dedicato esclusivamente ai chiller per stabilizzarne l'alimentazione.

> [!example] L'origine del termine "bug"
>
> Un serpente in cerca di calore durante l'inverno si infilò in una cabina di distribuzione ad alta tensione, attaccandosi alle bobine e causando un cortocircuito fatale che spense l'intero Data Center — lasciando a terra solo il proprio corpo carbonizzato. Il termine informatico **"bug"** deriva proprio da questo tipo di incidenti: veri insetti e roditori che causavano blackout masticando cavi o cortocircuitando componenti.

---

## L'Efficienza Energetica e il PUE

Sprecare energia non comporta solo perdite economiche dirette, ma impone costi indiretti: componenti elettriche e cavi più spessi e costosi per reggere i picchi. In uno scenario in cui i costi energetici sono passati da **300.000 € a 1.000.000 € all'anno** — complice il conflitto in Ucraina — misurare l'efficienza è diventato cruciale.

> [!definition] PUE — Power Usage Effectiveness
>
> Il **PUE** è il parametro adimensionale standard per misurare l'efficienza energetica di un Data Center. Si calcola come:
>
> $$
> \text{PUE} = \frac{\text{Total Facility Power}}{\text{IT Equipment Power}}
> $$
>
> Il *Total Facility Power* è la somma del consumo IT, dell'illuminazione e — soprattutto — del dispendio per il raffreddamento. Poiché l'assorbimento IT compare sia al numeratore che al denominatore, il valore ideale teorico in assenza di overhead è **1**. Il PUE è sempre maggiore di 1: più alto è il valore, peggiore è l'efficienza. Alcuni utilizzano l'inverso della formula per ottenere un indice compreso tra 0 e 1, ma il concetto non muta.

| Valore PUE | Interpretazione |
|---|---|
| ≤ 1.2 | Eccellente — standard moderno |
| < 1.3 | Raccomandato dall'UE per DC Hyperscale |
| 1.15 | PUE annuo del Green DC Università di Pisa a pieno carico |
| 1.8 – 2.0 | Valore medio italiano — molto negativo |
| > 2.0 | Per ogni kW di IT si spende più di 1 kW solo per raffreddarlo |

### Le Insidie del PUE

Sebbene essenziale, il PUE può nascondere informazioni fuorvianti. La prima domanda da porsi davanti a qualsiasi valore dichiarato è: *"Su quale arco temporale e a quali condizioni è stato misurato?"*

> [!warning] Trappole nel confronto tra PUE
>
> **Impatto stagionale.** Refrigerare d'inverno costa molto meno che d'estate. Esibire un PUE istantaneo misurato a gennaio (es. 1.05) è "barare". È necessario calcolare un **PUE annuo** (*Yearly PUE*), mediando la curva stagionale lungo l'intero anno. In Europa il picco dei consumi è in estate; in Australia — con le stagioni traslate di sei mesi — il picco cade tra dicembre e gennaio.
>
> **Saturazione del Data Center.** Un DC quasi vuoto (es. con un solo server) può mostrare un PUE pessimo perché il compressore dei chiller gira "a vuoto" rispetto al carico IT. Al contrario, lo stesso DC pieno lavorerà all'efficienza progettata.
>
> **Dimensioni dell'impianto.** Per un piccolo rack di 5 server con un budget di **1.000.000 € annui**, potrebbe essere economicamente più vantaggioso installare un normale condizionatore domestico — accettando un PUE di 2.0 — piuttosto che affrontare l'investimento multimilionario di un impianto industriale ottimizzato.

---

## Data Center Orbitali: il PUE Perfetto

L'ossessione per il PUE ha spinto aziende a progettare **Data Center Orbitali nello spazio**. In assenza di atmosfera, lo smaltimento del calore e l'assorbimento dell'energia solare sono enormemente facilitati, permettendo di avvicinarsi a un PUE teorico di **1** (valori realistici stimati: 1.01–1.07). Questi sistemi avrebbero un ciclo di vita di **10–15 anni**, al termine del quale i moduli verrebbero de-orbitati per bruciare nell'atmosfera o — idealmente — recuperati e sostituiti.

> [!note] Latenza nelle comunicazioni orbitali
>
> Per comunicazioni *point-to-point*, la latenza non sarebbe un problema insormontabile: la luce percorre distanze nell'aria pressoché istantaneamente, mentre viaggia a circa **0.6c** nei cavi in rame a terra. La vera sfida attuale rimane la quantità di detriti in orbita (*orbital debris*), che rende pericolosa qualsiasi installazione stabile.

---

## L'Architettura ad Aria: Sistemi CRAC

Poiché l'acqua è un conduttore termico nettamente superiore all'aria — che funge anzi da ottimo isolante termico — il raffreddamento ad aria è economico ma decisamente non ottimale. Negli anni '90 si mantenevano temperature di sala macchine di circa **17°C**; oggi lo standard operativo si attesta a **26–27°C**. Nel 2000, nel data center Tiscali in Sardegna, un rack consumava appena **3 kW** e lo si raffreddava tenendo le finestre aperte. Con l'innalzamento delle potenze (*High Density Computing*), si sono rese necessarie architetture più sofisticate.

> [!definition] CRAC — Computer Room Air Conditioning
>
> Il **CRAC** è la prima architettura industriale di raffreddamento ad aria, ancora in uso in strutture classiche — come alcuni building Aruba, con carichi web server prevedibili di circa 300 W per server. Prevede macchinari verticali disposti nella stanza, un **pavimento sopraelevato** (*raised floor* o *floating floor*) e piastrelle forate (*perforated tiles*) posizionate con cura di fronte ai rack.

Il principio fisico alla base è la **convezione**: l'aria calda tende naturalmente a salire. Il ciclo di funzionamento è il seguente: il macchinario CRAC aspira l'aria calda dalla parte alta della stanza, genera aria fredda e la immette a pressione al di sotto del pavimento flottante. L'aria fredda viaggia nel *plenum* sottostante e risale solo attraverso le piastrelle perforate poste di fronte ai rack.

![Sollevamento di una piastrella dal pavimento sopraelevato (raised floor) di un data center](images/Tile-lifter-in-use-raised-floor-878fd6.jpg)
*Fig. — Il pavimento sopraelevato (*raised floor*) è la caratteristica strutturale che rende possibile il sistema CRAC: il *plenum* sottostante distribuisce l'aria fredda verso le piastrelle perforate posizionate davanti ai rack.* Viene poi aspirata dalle ventole frontali dei server, li raffredda, ed esce come aria calda sul retro, risalendo verso il soffitto per ricominciare il ciclo.

> [!tip] La regola d'oro del CRAC
>
> **Non mescolare mai aria calda con aria fredda.** Mescolare i due flussi annullerebbe il lavoro termodinamico speso per generare il raffreddamento, abbassando drasticamente l'efficienza. In alcuni DC specializzati come quelli Aruba, i rack sono dotati di una porta frontale in vetro antiesplosione con griglie di aerazione posizionate *all'interno* — tra il cristallo e i server — per canalizzare chirurgicamente il flusso freddo direttamente nell'IT senza dispersioni.

> [!warning] Il limite dell'architettura CRAC
>
> Con le odierne densità di potenza — fino a decine di kW per rack — lo spazio fisico si satura. Se il soffitto non è abbastanza alto e il *plenum* sotto il pavimento non è sufficientemente profondo, il volume d'aria calda diventa così imponente che la convezione viene vinta: l'aria calda scende di nuovo sui server, mandando il sistema in blocco termico. L'architettura CRAC incontra quindi un limite strutturale nelle installazioni *high-density* moderne.

---

> [!abstract] Sintesi
>
> La gestione dell'energia e del raffreddamento in un Data Center intreccia fisica termodinamica, economia e ingegneria dei sistemi. Il **PUE** è lo strumento standard per misurare l'efficienza, ma va sempre interpretato su base annua e in relazione al carico effettivo — un valore istantaneo è quasi sempre fuorviante. Le architetture di raffreddamento, dai sistemi **CRAC** tradizionali a soluzioni più moderne, devono affrontare densità di potenza crescenti mantenendo la separazione netta tra flussi di aria calda e fredda. Il *vendor lock-in* e i contratti di manutenzione rappresentano il vero costo nascosto di un'infrastruttura che, per sua natura, non può mai fermarsi.
