# Teoria dei Segnali: Serie di Fourier

## Serie di Fourier: dal Tempo alla Frequenza

![[exam_mod2_fourier_series.jpg]]

Questo schema illustra il concetto fondamentale della **Serie di Fourier**: qualsiasi segnale periodico può essere decomposto in una somma (infinita) di funzioni sinusoidali a frequenze multiple della frequenza fondamentale.

### L'Intuizione Fondamentale

Un segnale periodico può essere visto come una sovrapposizione di componenti sinusoidali, ciascuna con frequenza, ampiezza e fase specifiche. Questo cambio di prospettiva — dal dominio del tempo al **dominio della frequenza** — è cruciale perché il canale trasmissivo agisce in modo diverso su componenti a frequenza diversa. Sapere quali frequenze compongono un segnale — cioè conoscere il suo **spettro** — permette di:
- Predire come il segnale si deformerà attraverso il canale.
- Dimensionare la **banda** necessaria (quante armoniche servono per rappresentare il segnale fedelmente).
- Progettare filtri per rimuovere componenti indesiderate.

La serie di Fourier decompone una funzione come somma di infinite funzioni oscillanti a frequenze diverse. È formalmente un cambio di coordinate: dal dominio del tempo a quello della frequenza. La base di questa decomposizione è un insieme di funzioni ortogonali.

### Segnali Periodici Continui

Un segnale continuo $s(t): \mathbb{R} \to \mathbb{R}$ è **periodico con periodo $T$** se
$$s(t) = s(t + T) \quad \forall t \in \mathbb{R}$$
I segnali periodici si possono studiare interamente nell'intervallo $[0, T]$. La frequenza fondamentale è $f = 1/T$.

### Definizione della Serie di Fourier

Data una funzione continua $s(t): \mathbb{R} \to \mathbb{R}$ periodica in $[-\pi, \pi]$:
$$s(t) = \frac{1}{2} a_0 + \sum_{n=1}^{\infty} \left( a_n \cos(nt) + b_n \sin(nt) \right)$$
con coefficienti:
$$a_0 = \frac{1}{\pi} \int_{-\pi}^{\pi} s(t)\, dt \qquad a_n = \frac{1}{\pi} \int_{-\pi}^{\pi} s(t) \cos(nt)\, dt \qquad b_n = \frac{1}{\pi} \int_{-\pi}^{\pi} s(t) \sin(nt)\, dt$$

**Interpretazione fisica:** Ogni segnale periodico è la "somma di sinusoidi". Il termine $\frac{1}{2} a_0$ è la **componente continua** (il valor medio del segnale). I termini successivi sono le **armoniche**: la **fondamentale** con frequenza $f_0 = 1/T$, la **prima armonica** con frequenza $f_1 = 2/T = 2f_0$, la seconda armonica a $3f_0$, e così via.

### Condizioni di Dirichlet

La serie di Fourier non è definita per qualsiasi funzione. Le **condizioni di Dirichlet** garantiscono l'esistenza della serie: è sufficiente che il segnale sia *piecewise continuous* (composta da un numero finito di pezzi continui su ogni sottointervallo finito, con limite finito nei punti di discontinuità). In corrispondenza delle discontinuità la serie converge alla media dei limiti sinistro e destro.

### Fenomeno di Gibbs

Quando la serie di Fourier approssima una funzione con discontinuità (come un'onda quadra), si osserva un **overshoot** intorno ai punti di salto che non scompare mai, per quanto si aumenti il numero di armoniche. Questo è il **fenomeno di Gibbs**: l'errore rimane del ~9% dell'ampiezza del salto, indipendentemente dall'ordine di troncamento. Le oscillazioni nel tratto piatto si riducono, ma il picco al salto rimane costante.
