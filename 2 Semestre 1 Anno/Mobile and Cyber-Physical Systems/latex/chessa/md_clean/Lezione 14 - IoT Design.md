### Anatomia di un nodo IoT

Un dispositivo IoT tipico è un sistema a basso costo, bassa potenza e di piccole dimensioni. I suoi componenti essenziali sono un **microprocessore** (spesso un MCU da pochi MHz come l'ATmega128L), una piccola quantità di **memoria**, un **ricetrasmettitore radio** (Wireless NIC) e una **scheda sensori** (sensor board) che può misurare accelerazione, pressione, umidità, luce, temperatura, GPS e molto altro. A queste si aggiungono eventuali **attuatori** e una fonte di energia, tipicamente una batteria o celle solari.

> [!definition] Nodo IoT (Mote)
>
> Un dispositivo IoT è un sistema embedded autonomo, composto da processore, memoria, radio e sensori, progettato per operare con risorse molto limitate di calcolo, memoria, banda e soprattutto energia.

### Principali sfide nel design

Il design di un nodo IoT è vincolato da quattro risorse finite: potenza di calcolo, memoria, capacità della batteria e larghezza di banda della comunicazione. Da questi vincoli discendono le sfide principali che il progettista deve affrontare:

**Efficienza energetica**: i sensori sono alimentati a batteria o tramite energy harvesting. Ogni operazione — campionamento, elaborazione, trasmissione — ha un costo energetico che deve essere minimizzato attraverso soluzioni hardware e software ad hoc.

**Adattabilità**: le condizioni della rete cambiano nel tempo (nodi che si scaricano, topologia che evolve), quindi servono protocolli di gestione della rete dinamici e meccanismi di riprogrammazione remota.

**Protocolli a bassa complessità e overhead**: le risorse limitate impongono protocolli leggeri a tutti i livelli dello stack (MAC, routing, applicazione), il che rende impossibile portare direttamente soluzioni pensate per reti cablate.

**Sicurezza**: la comunicazione wireless è intrinsecamente più esposta ad attacchi. La sicurezza va garantita a tutti gli strati dello stack, ma con un overhead accettabile.

**Comunicazione multi-hop**: la bassa potenza trasmissiva limita il raggio di copertura radio. I dati devono spesso attraversare più nodi intermedi per raggiungere il gateway (comunicazione multi-hop), richiedendo protocolli di routing dedicati.

**Mobilità e storage/pre-processing**: nodi mobili richiedono routing dinamico; elaborare i dati in locale (edge processing) prima di trasmetterli può ridurre drasticamente i consumi radio.

---

## La Legge di Moore e l'IoT

### La legge e le sue interpretazioni

Prima di occuparsi di efficienza energetica, vale la pena chiedersi: il progresso tecnologico risolverà autonomamente i vincoli IoT? La risposta richiede di capire cosa ci offre davvero la Legge di Moore.

> [!definition] Legge di Moore
>
> Il numero di transistor che possono essere integrati economicamente in un chip cresce esponenzialmente, raddoppiando circa ogni due anni.

La Legge di Moore non ha un'unica lettura: il raddoppio dei transistor si può "spendere" in tre modi diversi, e tutti e tre sono rilevanti per l'IoT:

1. **Stesse dimensioni, più prestazioni, stesso costo**: le prestazioni dei processori raddoppiano ogni due anni. Questo è il paradigma dei server e dei desktop.
2. **Stesso costo, metà dimensioni**: il chip si rimpicciolisce, e con esso si riduce il consumo energetico. Cruciale per i wearable e per qualsiasi applicazione in cui lo spazio conta.
3. **Stesse prestazioni, metà costo**: la stessa funzionalità diventa progressivamente più economica. Essenziale in IoT dove si deployano migliaia o milioni di nodi e il costo unitario è determinante.

Per dare un'idea concreta della portata di questa crescita: l'**Intel 4004** del 1971 integrava 2.300 transistor e lavorava a 740 KHz con 4 KB di memoria programma. L'**Intel Core i9-7980XE** del 2017 raggiunge 1,8 miliardi di transistor, 4,4 GHz di frequenza, 165 W di TDP e supporta fino a 128 GB di RAM. Un salto di sei ordini di grandezza in poco più di 40 anni.

### Perché la Legge di Moore non basta per l'IoT

Nell'IoT tutte e tre le interpretazioni della Legge di Moore trovano applicazione: ci sono applicazioni che richiedono sensori piccoli e a basso consumo, altre che necessitano di maggiore potenza di calcolo in-loco, e il costo è critico in quasi tutte. Tuttavia, la Legge di Moore **non risolverà automaticamente** i vincoli IoT, almeno nel breve termine.

Il motivo fondamentale è che i dispositivi IoT non usano i processori più avanzati: usano i processori più **economici** che soddisfano i requisiti dell'applicazione. Spesso si tratta di MCU progettati anni fa e ancora in produzione (come l'ATmega128L di Atmel). Acquistare il chip più recente e potente non è la strategia IoT: la scala di deployment — migliaia o milioni di nodi — rende il costo per unità il fattore dominante.

> [!tip] Intuizione chiave
>
> La Legge di Moore va usata per rendere i nodi IoT **più piccoli e più economici**, non necessariamente più potenti. La sfida del design efficiente rimane comunque aperta, perché la crescita della capacità delle batterie è molto più lenta di quella dei transistor.

---

## Efficienza Energetica

### Il problema: Intel vs Duracell

C'è un'asimmetria fondamentale nel progresso tecnologico che tocca direttamente l'IoT. Le prestazioni dei processori, la capacità delle memorie e quella dei dischi rigidi sono cresciute in modo esponenziale nell'arco degli ultimi decenni. La **capacità energetica delle batterie** invece è rimasta quasi piatta: la chimica delle batterie evolve molto più lentamente della microelettronica.

![](images/lezione-14-iot-design-img-01.jpg)
*Fig. — Il confronto "Intel vs Duracell": le curve di processore, HD e memoria crescono esponenzialmente nel tempo, mentre quella della batteria rimane quasi orizzontale. Il gap energetico si allarga progressivamente.*

Questo significa che più un nodo è capace di fare (più calcolo, più trasmissioni), più la batteria diventa il collo di bottiglia. Non si può semplicemente aspettare che le batterie migliorino: bisogna progettare per consumare meno.

### Dove va l'energia: laptop vs sensore

Per capire dove concentrare gli sforzi di ottimizzazione, è utile confrontare la distribuzione del consumo energetico in un laptop (sistema general-purpose) con quella di un sensore wireless.

![](images/lezione-14-iot-design-img-02.jpg)
*Fig. — Ripartizione del consumo energetico in un laptop: lo schermo domina con il 48%, seguito dal chipset (23%), processore (10%), grafica (9%), HD (6%) e rete (4%). In un sistema general-purpose lo schermo è il primo target di ottimizzazione.*

In un laptop lo **schermo** assorbe quasi la metà dell'energia totale (48%), e le tecniche di risparmio energetico si concentrano su di esso (backlight dimming, display off automatico). Il processore incide solo per il 10%.

![](images/lezione-14-iot-design-img-03.jpg)
*Fig. — Ripartizione del consumo energetico in un sensore wireless: il Wireless NIC e il processore+chipset si equivalgono al 40% ciascuno, mentre sensing e ADC pesano il 20%. Non c'è schermo, quindi la radio diventa il componente critico.*

In un sensore wireless lo scenario è radicalmente diverso. **Non c'è schermo**. Il consumo è distribuito tra la scheda radio (NIC wireless, 40%), il processore e chipset (40%), e il campionamento con conversione A/D (20%). Processore e radio sono i due target principali per l'ottimizzazione.

### Consumi della radio: un dettaglio cruciale

Per comprendere perché la radio è così critica, vediamo i consumi di una tipica interfaccia WiFi:

- **Sleep mode**: 10 mA
- **Listen mode** (in ascolto): 180 mA
- **Receive mode** (ricezione attiva): 200 mA
- **Transmit mode** (trasmissione): 280 mA

Due osservazioni importanti:
1. La differenza tra sleep e listen è enorme: la radio in ascolto consuma 18 volte più della radio in sleep. Il semplice fatto di tenere la radio accesa e in ascolto è estremamente costoso.
2. In alcuni sensori il consumo in trasmissione è **inferiore** a quello in ricezione. Questo sembra controintuitivo ma dipende dai circuiti di amplificazione e dalla specifica implementazione hardware.

Su un sensore di classe Mote con interfaccia radio a bassa potenza i valori sono molto più contenuti: sleep a 0,016 mW, ascolto a 12,36 mW, ricezione a 12,50 mW, trasmissione tra 12,36 mW e 17,76 mW a seconda della potenza trasmissiva. Si conferma che il costo del "listen" è quasi pari al "receive": **tenere la radio accesa è costoso anche quando non si trasmette nulla**.

> [!warning] Radio accesa = energia sprecata
>
> Il consumo in modalità listen è paragonabile a quello in ricezione, e ordini di grandezza superiore allo sleep. La radio deve essere spenta il più possibile. Lo stesso vale per il processore: anche il turn-on/turn-off ha un costo energetico non trascurabile.

---

## Duty Cycle

### Motivazione: spegnere per risparmiare

La soluzione alla sfida energetica si chiama **duty cycle** (ciclo di lavoro). L'attività di un nodo IoT è tipicamente ripetitiva: campiona il sensore, elabora, trasmette, attendi, ricomincia. L'idea è di sfruttare i periodi di inattività per mettere in sleep tutti i componenti possibili, riducendo al minimo il consumo.

> [!definition] Duty Cycle (DC)
>
> Il duty cycle è la frazione di un periodo in cui il sistema (o un suo componente) è attivo. Si esprime come rapporto o percentuale: DC = t_attivo / T_periodo. Un DC del 100% significa sistema sempre attivo; un DC dell'1% significa attivo solo l'1% del tempo.

Il duty cycle ha senso per sistemi che operano in modo **ciclico**: eseguono la loro attività periodicamente e rimangono inattivi per la parte restante del periodo. Applicarlo in modo aggressivo è la leva principale per estendere la vita della batteria.

### Esempio pratico: il codice Arduino

Consideriamo un semplice programma Arduino che legge un sensore analogico e trasmette il valore via seriale, con una pausa di 380 ms tra un'iterazione e l'altra. La ripartizione temporale di un singolo ciclo di 400 ms è:

| Fase | Durata | Componenti attivi |
|------|--------|-------------------|
| Campionamento | 4 ms | Processore + Sensore |
| Elaborazione | 1 ms | Solo Processore |
| Trasmissione | 15 ms | Processore + Radio |
| Attesa (`idle`) | 380 ms | Nessuno (tutti in sleep) |

Il codice ottimizzato, che accende e spegne esplicitamente ogni componente quando non serve, è:

```c
void loop() {
    turnOn(analogSensor);
    int sensorValue = analogRead(A0);
    turnOff(analogSensor);
    
    float voltage = sensorValue * (5.0 / 1023.0);
    
    turnOn(radioInterface);
    Serial.println(voltage);
    turnOff(radioInterface);
    
    idle(380);  // tutto in sleep per 380 ms
}
```

Il duty cycle di ciascun componente si calcola come:

$$DC_\text{componente} = \frac{t_\text{attivo}}{T_\text{periodo}}$$

- **Processore**: attivo per 4+1+15 = 20 ms su 400 ms → $DC_p = 20/400 = 5\%$
- **Radio**: attiva per 15 ms su 400 ms → $DC_r = 15/400 = 3,75\%$
- **Sensore**: attivo per 4 ms su 400 ms → $DC_s = 4/400 = 1\%$

Il diagramma energia-tempo chiarisce visivamente questa struttura a stati:

![](images/lezione-14-iot-design-img-04.jpg)
*Fig. — Diagramma stati/energia vs tempo per il codice di esempio: il consumo istantaneo varia a scalini in base ai componenti attivi. Il lungo periodo di idle (380 ms) abbassa drasticamente il consumo medio.*

### Calcolo del consumo energetico

Il consumo totale di energia di un nodo si calcola sommando i contributi di ciascun componente. Per un componente generico con duty cycle $dc$ il costo energetico per unità di tempo è:

$$E_\text{componente} = dc \cdot C_\text{active} + (1 - dc) \cdot C_\text{idle}$$

dove $C_\text{active}$ e $C_\text{idle}$ sono i correnti (in mA) rispettivamente in stato attivo e in sleep. Poiché si usa corrente continua e la tensione è (quasi) costante, si può esprimere tutto in **mAh** — sia l'energia consumata che la carica immagazzinata nella batteria.

Per il microprocessore il costo per ciclo è:

$$E_\mu = C_\mu^{full} \cdot dc_\mu + C_\mu^{idle} \cdot (1 - dc_\mu)$$

Per la radio, che ha due stati attivi (trasmissione e ricezione):

$$E_\rho = C_\rho^T \cdot dc_\rho^T + C_\rho^R \cdot dc_\rho^R + C_\rho^{idle} \cdot (1 - dc_\rho^T - dc_\rho^R)$$

Il costo totale per ciclo è la somma di tutti i componenti:

$$E = E_\mu + E_\rho + E_\lambda + E_\sigma$$

dove $E_\lambda$ è il costo del logger (memoria flash) e $E_\sigma$ quello della scheda sensori.

### Calcolo del lifetime

La vita utile del dispositivo dipende da quanta energia ha a disposizione (capacità della batteria $B_0$) e da quanto ne consuma per ciclo ($E$). Ignorando la perdita di carica della batteria per autoscarica, il lifetime in numero di cicli è:

$$Lifetime = \frac{B_0}{E}$$

Se si tiene conto dell'autoscarica della batteria (perdita percentuale $\varepsilon$ per ciclo), la carica residua segue la ricorrenza:

$$B_n = B_{n-1} \cdot (1 - \varepsilon) - E$$

Risolvendo la ricorrenza si ottiene:

$$B_n = B_0 \cdot (1-\varepsilon)^{n-1} + \frac{E \cdot ((1-\varepsilon)^n - 1)}{\varepsilon}$$

Il lifetime in cicli è il valore di $n$ per cui $B_n = 0$. In pratica il dispositivo smette di funzionare prima, quando la tensione scende sotto una soglia minima.

### Effetto del duty cycle sulla vita della batteria

I due grafici seguenti mostrano empiricamente l'impatto del duty cycle sulla vita di un nodo basato su specifiche hardware reali (Mote-class):

![](images/lezione-14-iot-design-img-05.jpg)
*Fig. — Vita della batteria in mesi vs capacità (mA-hr) per due modelli: DC al 100% e DC al 5%. Scala logaritmica sull'asse Y. A parità di capacità, il modello con DC al 5% ha una vita circa 10-15 volte superiore.*

![](images/lezione-14-iot-design-img-06.jpg)
*Fig. — Vita del sensore (mesi) vs duty cycle per batterie da 2000 e 3000 mA-hr. La curva scende rapidamente: già passare dall'1% al 3% di DC dimezza approssimativamente il lifetime. L'effetto della capacità della batteria diventa trascurabile ad alti DC.*

Questi grafici mostrano due cose fondamentali. Prima cosa: ridurre il duty cycle è molto più efficace che aumentare la capacità della batteria — a DC alto le due curve per 2000 e 3000 mAh si sovrappongono, segno che la batteria più grande non aiuta quasi più. Seconda cosa: anche un DC basso ma non zero (5%) porta a lifetime dell'ordine dei mesi, non degli anni. Per applicazioni con deployment di lunga durata è necessario DC molto bassi o [[Energy Harvesting]].

### Esempio numerico: soluzione dell'esercizio base

Con le specifiche della Mote (ATmega128L: 8 mA full, 15 μA sleep; Radio: 20 mA xmit, 20 μA sleep; Sensor Board: 5 mA full, 5 μA sleep; Batteria: 2000 mAh) e il codice di esempio (periodo 400 ms, sensore 4 ms, calcolo 1 ms, trasmissione 15 ms, idle 380 ms):

- $dc_p = 5\%$, $dc_r = 3,75\%$, $dc_s = 1\%$

Il consumo per ora risulta 1,243 mAh, ripartito tra:

| Componente | Contributo idle | Contributo attivo |
|------------|-----------------|-------------------|
| Processore | 0,014 mAh | 0,4 mAh |
| Radio | 0,019 mAh | 0,75 mAh |
| Sensore | 0,005 mAh | 0,055 mAh |
| **Totale** | 0,038 mAh | 1,205 mAh |

**Lifetime ≈ 2000 / 1,243 ≈ 1609 ore** (circa 67 giorni).

### La complessità nascosta: spegnere la radio è una decisione globale

Spegnere il processore è una scelta locale: lo scheduler del nodo sa quando il processore non serve e può metterlo in sleep autonomamente. Spegnere la radio è invece una **decisione globale**: un nodo con radio spenta non può ricevere messaggi, non può fungere da router in una rete multi-hop, non può ricevere comandi o aggiornamenti. Un'intera rete di nodi che si addormentano nello stesso momento sarebbe inutile.

Questo crea un trade-off fondamentale: più i nodi dormono, meno consumano, ma peggiore è la capacità di comunicare. La soluzione sta nei **protocolli MAC** (Medium Access Control) progettati per l'IoT, che sincronizzano i nodi e coordinano chi può dormire e quando. Questi protocolli implementano strategie di risparmio energetico a livello di rete, e saranno oggetto delle lezioni successive.

---

## Esercizi: Calcolo di DC e Lifetime

### Esercizio 1 — Monitoraggio Frequenza Cardiaca (invio raw)

In questo scenario un dispositivo campiona un fotodiodo sul polso a 20 Hz (campionamento da 0,5 ms, richiede processore + sensore attivi), e invia ogni 5 campioni consecutivi al server (trasmissione da 2 ms ogni 0,25 s, richiede processore + radio). Il calcolo HR è demandato al server.

- $dc_\text{sampling} = 0,5\,ms / 50\,ms = 0,01$ (1%)
- $dc_\text{radio} = 2\,ms / 250\,ms = 0,008$ (0,8%)
- $dc_\text{processor} = dc_\text{sampling} + dc_\text{radio} = 0,018$ (1,8%)

Consumo per ora: 0,3935 mAh → **Lifetime ≈ 5082 ore (~212 giorni)**.

### Esercizio 2 — Monitoraggio HR con calcolo in-device

In questo scenario il dispositivo calcola HR localmente (ogni 2 s, elaborazione da 5 ms, solo processore) e trasmette solo 1 pacchetto ogni 10 s (2 ms di trasmissione).

- $dc_\text{sampling} = 0,01$ (identico al caso precedente)
- $dc_\text{processing} = 5\,ms / 2000\,ms = 0,0025$
- $dc_\text{radio} = 2\,ms / 10000\,ms = 0,0002$
- $dc_\text{processor} = 0,01 + 0,0025 + 0,0002 = 0,0127$

Consumo per ora: 0,1954 mAh → **Lifetime ≈ 10.235 ore (~426 giorni)**.

> [!tip] Edge processing vs cloud offloading
>
> Il confronto tra i due esercizi rivela un principio fondamentale nell'IoT: elaborare i dati in-loco (**edge processing**) invece di inviare tutti i campioni grezzi al server può ridurre drasticamente le trasmissioni radio — il componente più energivoro dopo il processore. Nonostante il calcolo HR aggiunga un piccolo overhead al processore, il risparmio sulla radio più che compensa, raddoppiando circa il lifetime.

---

## Conclusioni e Punti Chiave

La lezione ha costruito un quadro coerente intorno al problema energetico nell'IoT. I vincoli di processing, memoria, batteria e comunicazione non saranno risolti automaticamente dalla Legge di Moore, che nell'IoT viene usata principalmente per ridurre costi e dimensioni piuttosto che per aumentare le prestazioni. La sfida energetica persiste perché la capacità delle batterie non cresce al ritmo dei transistor.

L'efficienza energetica si ottiene comprendendo dove va l'energia (radio e processore sono i componenti dominanti, non lo schermo come nel laptop) e applicando il duty cycle per spegnere ogni componente quando non è necessario. Il modello formale permette di calcolare con precisione il consumo per ciclo e il lifetime atteso. La prossima lezione approfondirà i protocolli MAC per l'IoT, che risolvono il problema della coordinazione del duty cycle a livello di rete.

> [!question] Possibili domande d'esame
>
> - Quali sono le tre interpretazioni della Legge di Moore e come si applicano all'IoT?
> - Perché la Legge di Moore non risolve automaticamente i problemi di design IoT nel breve termine?
> - Qual è la differenza nella distribuzione del consumo energetico tra un laptop e un sensore wireless?
> - Perché tenere la radio in modalità "listen" è quasi costoso quanto ricevere dati?
> - Come si calcola il duty cycle di un componente a partire dalla specifica comportamentale del firmware?
> - Dati i parametri hardware di un Mote, saper calcolare: duty cycle di ciascun componente, consumo orario in mAh, lifetime in ore/cicli.
> - Perché spegnere la radio è una "decisione globale" mentre spegnere il processore è "locale"?
> - Qual è il trade-off tra edge processing e invio dei campioni grezzi al server in termini di lifetime?


---

## Approfondimento: Specifiche Reali di una Mote e Modelli di DC

### Specifiche hardware della Mote-class sensor

Per rendere concreto tutto il discorso teorico, le slide riportano le specifiche misurate di un sensore di classe Mote basato su ATmega128L. Questi numeri sono il riferimento per tutti gli esercizi numerici del corso.

![](images/lezione-14-iot-design-img-07.jpg)
*Fig. — Specifiche hardware complete di una Mote-class sensor: consumo di corrente in ogni stato per microprocessore, radio (con distinzione ricezione/trasmissione), logger (memoria flash) e sensor board. La perdita di carica annua della batteria è del 3%.*

Osservando la tabella emergono dettagli importanti: la radio in ricezione (19,7 mA) consuma leggermente più di quella in trasmissione (17,4 mA) — un effetto già citato che spiega perché il solo ascoltare sia così costoso. Il logger in scrittura (15 mA) ha un consumo paragonabile alla radio, mentre in lettura scende a 4 mA e in sleep a soli 2 μA. Il processore in sleep consuma appena 15 μA.

### Due modelli a confronto: DC 100% vs DC 5%

![](images/lezione-14-iot-design-img-08.jpg)
*Fig. — Tabella di confronto tra il modello con duty cycle al 100% (tutto sempre acceso) e il modello con duty cycle al 5%, con la percentuale di tempo trascorsa in ciascuno stato per ogni subsistema. Il logger mantiene un DC del 3% in entrambi i modelli.*

Il confronto tra il modello a DC 100% e quello al 5% è illuminante. Nel modello a pieno regime tutti i componenti sono sempre attivi. Nel modello al 5%, grazie alle chiamate `turnOn`/`turnOff`, il processore è attivo solo il 5% del tempo, la radio il 5% diviso tra tx (1%) e rx (4%), e il sensor board appena l'1%. Il logger mantiene un proprio duty cycle del 3% indipendente dagli altri, con parte delle scritture e letture in parallelo ad altri componenti.

![](images/lezione-14-iot-design-img-09.jpg)
*Fig. — Rappresentazione grafica degli stati per ciascun subsistema nei due modelli (DC 100% in alto, DC 5% in basso). Nel modello a DC 5% i componenti trascorrono quasi tutto il periodo nello stato idle (marrone scuro), con brevi finestre di attività (arancione).*

### Duty cycle: la flessibilità della "forma" del ciclo

Un punto spesso sottovalutato è che il duty cycle specifica solo la **frazione** di tempo attivo, non il suo posizionamento all'interno del periodo. Lo stesso DC del 10% può corrispondere a un burst di attività all'inizio del periodo, uno alla fine, due burst distribuiti, o qualsiasi altra configurazione temporale. Ciò che conta per il consumo medio è la frazione totale.

![](images/lezione-14-iot-design-img-10.jpg)
*Fig. — Esempi di un componente con DC al 10%: la finestra di attività (arancione) può posizionarsi in qualsiasi punto del periodo. Il consumo medio è identico in tutti i casi; ciò che cambia è la latenza di risposta e la sincronizzabilità con gli altri nodi.*

Questa flessibilità è sfruttata dai protocolli MAC dell'IoT per sincronizzare le finestre di ascolto dei vari nodi: se tutti i vicini sono svegli negli stessi istanti, la comunicazione è possibile anche con DC molto bassi.

---

## Esercizio Extra-1: Calcolo Completo con Attività Separate

Questo esercizio è più realistico perché distingue tre fasi operative separate — campionamento, elaborazione e trasmissione — ognuna con la propria durata e i propri componenti attivi.

**Specifiche hardware**: ATmega128L (8 mA full, 0,015 mA sleep), Radio (1 mA xmit, 0,02 mA sleep), Sensor Board (5 mA full, 0,005 mA sleep), Batteria 2000 mAh.

**Comportamento del firmware** (periodo = 1/0,1 Hz = 10 s):
- Campionamento a 0,1 Hz → ogni 10 s, durata 0,5 ms → processore + sensore attivi
- Elaborazione dopo ogni campionamento, durata 2 ms → solo processore attivo
- Trasmissione dopo ogni elaborazione, durata 1 ms → processore + radio attivi

### Calcolo dei duty cycle

Il periodo è 10 secondi (frequenza 0,1 Hz). Le tre attività si svolgono in sequenza nello stesso ciclo, quindi il tempo attivo totale per ciclo è 0,5 + 2 + 1 = 3,5 ms su 10.000 ms.

$$dc_\text{sampling} = \frac{0,5\,\text{ms}}{10.000\,\text{ms}} = 0,00005 \quad (0,005\%)$$

$$dc_\text{processing} = \frac{2\,\text{ms}}{10.000\,\text{ms}} = 0,0002 \quad (0,02\%)$$

$$dc_\text{transmitting} = \frac{1\,\text{ms}}{10.000\,\text{ms}} = 0,0001 \quad (0,01\%)$$

Poiché processore è attivo in tutte e tre le fasi:

$$dc_\text{processor} = dc_\text{sampling} + dc_\text{processing} + dc_\text{transmitting} = 0,00035$$

Il sensor board è attivo solo durante il campionamento: $dc_\text{sensor} = 0,00005$.
La radio è attiva solo durante la trasmissione: $dc_\text{radio} = 0,0001$.

### Calcolo del consumo per ora

Applicando la formula $E = dc_\text{active} \cdot C_\text{active} + (1 - dc_\text{active}) \cdot C_\text{idle}$ a ciascun componente:

**Sensor board**:
$$E_\text{sensor} = 0,00005 \cdot 5\,\text{mA} + 0,99995 \cdot 0,005\,\text{mA} \approx 0,00025 + 0,004999 = 0,00525\,\text{mAh}$$

**Processore**:
$$E_\mu = 0,00035 \cdot 8\,\text{mA} + 0,99965 \cdot 0,015\,\text{mA} \approx 0,0028 + 0,01499 = 0,01779\,\text{mAh}$$

**Radio**:
$$E_\rho = 0,0001 \cdot 1\,\text{mA} + 0,9999 \cdot 0,02\,\text{mA} \approx 0,0001 + 0,01999 = 0,02010\,\text{mAh}$$

**Totale per ora**: $E_\text{tot} = 0,00525 + 0,01779 + 0,02010 \approx 0,0431\,\text{mAh}$

**Lifetime**: $Lifetime = \frac{2000\,\text{mAh}}{0,0431\,\text{mAh/h}} \approx 46.358\,\text{ore} \approx 5,3\,\text{anni}$

> [!abstract] Sintesi esercizio extra-1
>
> Grazie a un duty cycle di appena lo 0,035% per il processore e ancora meno per radio e sensore, il consumo orario è ridottissimo (0,043 mAh). Con una batteria da 2000 mAh il lifetime teorico supera i 5 anni. Questo mostra come applicazioni a bassa frequenza di campionamento (0,1 Hz) permettano duty cycle estremi e vita utile pluriennale — il paradigma ideale per il monitoraggio ambientale o strutturale.

> [!warning] Attenzione alle semplificazioni
>
> In tutti gli esercizi si trascura il costo energetico del turn-on e turn-off dei componenti, che in realtà ha un peso non nullo. Si trascura anche l'autoscarica della batteria (3% annuo per la Mote reale). Questi effetti diventano rilevanti quando il DC è molto basso e il lifetime è nell'ordine degli anni: la batteria potrebbe scaricarsi per autoscarica prima che si esaurisca per consumo attivo.
