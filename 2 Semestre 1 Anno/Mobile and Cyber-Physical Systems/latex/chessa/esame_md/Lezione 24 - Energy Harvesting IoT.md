# Energy Harvesting IoT

Il problema di fondo dei dispositivi IoT è energetico: alimentarli con una batteria di capacità finita costringe a scegliere tra prestazioni e durata. Una batteria grande permette lunga vita, ma aumenta dimensioni, peso e costo; un processore a basso consumo estende la vita ma limita potenza di calcolo e portata radio. L'**energy harvesting** (raccolta di energia) rappresenta un'alternativa strutturale: invece di ottimizzare il consumo, si raccoglie energia dall'ambiente e si elimina — o si riduce drasticamente — il vincolo della batteria finita.

## Architetture di harvesting e Concetto di Energy Neutrality

### Harvest-Use vs Harvest-Store-Use

**Harvest-Use**: l'energia è raccolta e consumata istantaneamente. Non esiste un buffer. Il dispositivo funziona solo se $P_s(t) \geq P_c(t)$ (potenza sorgente ≥ potenza consumata). Se la sorgente produce meno del necessario il dispositivo si spegne; se produce di più l'eccesso va perduto. Esempi: mulini ad acqua, tag RFID passivi.

**Harvest-Store-Use**: un buffer energetico (batteria ricaricabile o supercapacitore) disaccoppia temporalmente produzione e consumo. L'energia in eccesso ($P_s > P_c$) viene accumulata nel buffer; l'energia in difetto ($P_c > P_s$) viene prelevata dal buffer. Un buffer ideale ha capacità infinita ed efficienza $\eta = 1$. Un buffer reale ha capacità massima $B_{max}$, efficienza $\eta < 1$, e una potenza di leakage $P_{leak}$.

### Concetto di Energy Neutrality

Un dispositivo è **energy neutral** se, in qualsiasi intervallo di tempo, l'energia consumata non supera l'energia raccolta (più la carica iniziale del buffer):

$$\int_0^T P_c(t)\,dt \leq \int_0^T P_s(t)\,dt + B_0 \qquad \forall T$$

Il raggiungimento dell'energy neutrality richiede di adattare il carico in base alla disponibilità energetica prevista — obiettivo del problema di Kansal.

## Analisi Grafica della Potenza e Neutralità Energetica

![[exam_chessa_energy_neutrality_graph.jpg]]
*Fig. — Grafico potenza/tempo: l'area tratteggiata in blu (Ps > Pc) è l'energia raccolta e accumulata nel buffer; l'area punteggiata (Pc > Ps) è l'energia prelevata dal buffer. La retta arancione mostra l'energia immediatamente consumata (Pc=Ps).*

Il grafico mostra due curve di potenza in funzione del tempo:
- $P_s(t)$: potenza prodotta dall'energy harvester (curva decrescente).
- $P_c(t)$: potenza consumata dal dispositivo (curva a forma di U).

Le due aree rappresentano:

$$\int_0^T [P_s(t) - P_c(t)]^+ dt$$

Area in blu (Ps > Pc): energia prodotta in eccesso → accumulata nel buffer. Il buffer si carica.

$$\int_0^T [P_c(t) - P_s(t)]^+ dt$$

Area punteggiata (Pc > Ps): il consumo supera la produzione → energia prelevata dal buffer. Il buffer si scarica.

La retta arancione indica la zona in cui $P_s = P_c$: energia prodotta e immediatamente consumata, senza passare dal buffer. Il sistema è energy neutral se la prima integrale ≥ seconda integrale su tutto l'orizzonte temporale considerato.

## Classificazione delle Sorgenti

Le sorgenti si classificano su due assi:

**Controllabilità**:
- *Completamente controllabile*: energia disponibile su richiesta (torcia shake-to-power, sorgenti RF dedicate).
- *Parzialmente controllabile*: influenzabile ma non deterministica (RFID in ambiente RF non uniforme).
- *Non controllabile*: raccolta solo quando disponibile (sole, vento, calore ambientale).

**Prevedibilità** (per le sorgenti non controllabili):
- *Prevedibile*: esistono modelli affidabili (sole: ciclo giorno/notte + stagioni + meteo).
- *Non prevedibile*: nessun modello affidabile (vibrazioni da terremoti).

## Misurare la carica della batteria

Tutte le tecniche di power management richiedono informazioni fresche sulla carica attuale della batteria e sulla produzione energetica. Entrambe sono quantità non direttamente osservabili e devono essere stimate.

### Stima Stato di Carica tramite ADC

![[exam_chessa_energy_harvesting_table.jpg]]
*Fig. — Tabella con parametri di batteria per tre piattaforme (RPI, Arduino, Tmote): tensioni min/max/ref, livelli di quantizzazione, xmin/xmax e stima Battery charge.*

La tabella mostra come misurare lo **stato di carica** (SoC) di una batteria attraverso la sua tensione terminale, per tre piattaforme hardware. L'idea è che la tensione ai terminali di una batteria è approssimabile come monotona (e in molti tratti lineare) rispetto alla carica residua.

Le colonne chiave:
- $v_{min}$, $v_{max}$: range operativo della batteria (es. Arduino: 7–9 V).
- $v_{ref}$: risoluzione della quantizzazione ADC (es. Arduino: 0.008789 V per LSB).
- **quantization levels (bit)**: risoluzione dell'ADC (10 o 12 bit).
- $x_{min}$, $x_{max}$: valori ADC corrispondenti a $v_{min}$ e $v_{max}$.
- **Battery charge (mAh)**: capacità totale della batteria stimata.

Campionando la tensione tramite ADC e mappando il valore digitale $x$ nell'intervallo $[x_{min}, x_{max}]$, si ottiene una stima lineare della carica rimanente:

$$\text{SoC} \approx \frac{x - x_{min}}{x_{max} - x_{min}} \times B_{cap}$$
$$B = B_{min} + \frac{B_{max} - B_{min}}{x_{max} - x_{min}}(x - x_{min})$$

Questa stima è utile per il task scheduler: sa quanta energia ha disponibile e può pianificare i task di conseguenza.
