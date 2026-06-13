---
tags:
  - università/mobile-and-cyber-physical-systems
  - teoria-dei-segnali
  - fourier
  - elaborazione-segnali
data: 2026-04-28
lezione: "Teoria dei Segnali — Introduzione e Serie di Fourier"
professore: "Stefano Chessa"
---
# Teoria dei Segnali: Introduzione e Serie di Fourier

## Perché la Teoria dei Segnali?

I sistemi moderni — reti mobili 4G/5G, dispositivi IoT, sistemi audio — elaborano **segnali** per rappresentare e trasmettere informazione. Capire come questi segnali sono strutturati, come vengono disturbati dal canale trasmissivo, e come possono essere analizzati e trasformati è il fondamento dell'ingegneria delle comunicazioni digitali.

La teoria dei segnali serve a quattro scopi pratici fondamentali. Il primo è **estrarre informazione**: identificare frequenze, pattern ed eventi rilevanti (es. riconoscimento vocale, analisi di segnali biomedici). Il secondo è **rimuovere effetti indesiderati**: filtrare il rumore, compensare distorsioni del canale, mitigare il fading multipath nelle reti wireless. Il terzo è **trasmettere efficientemente l'informazione**: codificare i segnali per il canale (es. OFDM in 4G/5G che distribuisce i dati su più frequenze). Il quarto è **abilitare l'elaborazione digitale**: convertire segnali analogici in forma digitale tramite campionamento e quantizzazione.

![Pipeline di conversione analogico-digitale: da segnale analogico a codifica binaria](images/lezione-25-lab-teoria-dei-segnali-introduzione-e-serie-di-fourier-img-01.jpg)
*Fig. — Dalla sorgente analogica ai bit: campionamento (discretizzazione nel tempo), quantizzazione (discretizzazione dell'ampiezza), codifica binaria.*

---

## Classificazione dei Segnali

> [!definition] Segnale
>
> Un segnale è una variazione di una grandezza fisica che porta informazione. Formalmente è una funzione $f(t): \mathfrak{D} \longrightarrow \mathfrak{C}$ dove il dominio $\mathfrak{D}$ può essere $\mathbb{R}$ (tempo continuo) o $\mathbb{Z}$ (tempo discreto), e il codominio $\mathfrak{C}$ può essere $\mathbb{R}$ (ampiezza continua) o un insieme discreto (ampiezza quantizzata).

Ci concentriamo su **segnali deterministici monodimensionali**: la variabile indipendente è il tempo, e il segnale è noto prima di essere prodotto (al contrario dei segnali aleatori, analizzati con metodi probabilistici).

### Segnali a Tempo Continuo

Quando il dominio è $\mathbb{R}$, il segnale è detto **analogico** (*analog*). Se anche il codominio è $\mathbb{R}$, l'ampiezza è continua; se il codominio è un insieme discreto (es. $\mathbb{Z}$), l'ampiezza è quantizzata.

![Segnali a tempo continuo: ampiezza continua (curva liscia) vs ampiezza quantizzata (gradini)](images/lezione-25-lab-teoria-dei-segnali-introduzione-e-serie-di-fourier-img-02.jpg)
*Fig. — In alto: segnale analogico, continuo in tempo e ampiezza. In basso: segnale continuo in tempo ma quantizzato in ampiezza (segnale a gradini).*

### Segnali a Tempo Discreto

Quando il dominio è $\mathbb{Z}(T) = \{nT, \forall n \in \mathbb{Z}, T \in \mathbb{R}\}$, il segnale è detto **discreto**. Ad esempio $\mathbb{Z}(2) = \{\ldots, -4, -2, 0, 2, 4, \ldots\}$. Un segnale discreto con ampiezza presa da un insieme finito di simboli è detto **digitale** (*digital*), o sequenza simbolica.

![Segnali a tempo discreto: ampiezza continua (campioni a qualsiasi altezza) vs ampiezza quantizzata (campioni su livelli finiti)](images/lezione-25-lab-teoria-dei-segnali-introduzione-e-serie-di-fourier-img-03.jpg)
*Fig. — In alto: segnale discreto con ampiezza continua. In basso: segnale digitale, discreto sia nel tempo che nell'ampiezza.*

### Tabella Riepilogativa

| Tempo | Ampiezza | Tipo |
|---|---|---|
| Continuo ($\mathbb{R}$) | Continua ($\mathbb{R}$) | Segnale analogico |
| Continuo ($\mathbb{R}$) | Discreta ($\mathbb{Z}$) | Segnale quantizzato |
| Discreto ($\mathbb{Z}(T)$) | Continua ($\mathbb{R}$) | Segnale discreto |
| Discreto ($\mathbb{Z}(T)$) | Discreta (insieme finito) | Segnale digitale |

### Bitrate di una Sorgente Digitale

Quando un segnale analogico viene convertito in digitale con frequenza di campionamento $f_c$ campioni/secondo e ogni campione è codificato con $M$ bit:

$$\text{Bitrate} = f_c \cdot M \quad [\text{bit/secondo}]$$

Maggiori $f_c$ e $M$ producono migliore fedeltà ma richiedono maggiore capacità trasmissiva.

---

## Trasmissione e Canale

### Il Modello del Canale

Nella trasmissione di informazione, un trasduttore alla sorgente converte un messaggio in un segnale fisico (es. un'antenna converte energia elettrica in onde elettromagnetiche), il segnale si propaga attraverso il mezzo, e un trasduttore alla destinazione converte il segnale di ritorno in messaggio. Il **canale** non è un mezzo ideale: agisce come un sistema che modifica il segnale.

Le principali forme di degrado sono la **distorsione** (variazione della forma d'onda, es. attenuazione differenziata per frequenza), la **propagazione multipath** (il segnale raggiunge il ricevitore attraverso percorsi multipli con ritardi diversi, causando interferenza), e il **rumore** (segnale indesiderato sovrapposto a quello utile).

> [!definition] SNR — Signal-to-Noise Ratio
>
> Il rapporto segnale-rumore misura la qualità del segnale ricevuto rispetto al rumore di fondo:
> $$SNR_{dB} = 10 \log_{10} \frac{P_{signal}}{P_{noise}}$$

### Teorema di Shannon

Il risultato fondamentale della teoria dell'informazione stabilisce la capacità massima di un canale:

$$C = B \log_2 (1 + SNR)$$

dove $B$ è la banda disponibile in Hz, $SNR$ il rapporto segnale-rumore, e $C$ la capacità del canale in bit/secondo. Questo crea un trade-off inevitabile: ridurre la distorsione di quantizzazione alla sorgente aumenta la quantità di informazione da trasmettere, che deve rientrare entro la capacità $C$.

---

## Serie di Fourier: dal Tempo alla Frequenza

### L'Intuizione Fondamentale

Un segnale periodico può essere visto come una sovrapposizione di componenti sinusoidali, ciascuna con frequenza, ampiezza e fase specifiche. Questo cambio di prospettiva — dal dominio del tempo al **dominio della frequenza** — è cruciale perché il canale trasmissivo agisce in modo diverso su componenti a frequenza diversa. Per analizzare e predire tale comportamento, occorre identificare esplicitamente le componenti frequenziali di un segnale.

La serie di Fourier decompone una funzione come somma di infinite funzioni oscillanti a frequenze diverse. È formalmente un cambio di coordinate: dal dominio del tempo a quello della frequenza. La base di questa decomposizione è un insieme di funzioni $\varphi_n(t)$ ortogonali, analogamente alla decomposizione di un vettore in uno spazio vettoriale.

![Le componenti armoniche $s_0, s_1, s_2, s_3, s_4$ si sommano per costruire il segnale $s(t)$](images/lezione-25-lab-teoria-dei-segnali-introduzione-e-serie-di-fourier-img-04.jpg)
*Fig. — Un segnale si costruisce sommando componenti sinusoidali: la componente costante ($s_0$), la fondamentale ($s_1$) e le armoniche superiori ($s_2, s_3, s_4$). Cambiare i coefficienti cambia il segnale risultante.*

### Segnali Periodici Continui

Un segnale continuo $s(t): \mathbb{R} \to \mathbb{R}$ è **periodico con periodo $T$** se

$$s(t) = s(t + T) \quad \forall t \in \mathbb{R}$$

I segnali periodici si possono studiare interamente nell'intervallo $[0, T]$. La frequenza fondamentale è $f = 1/T$. Un segnale non periodico è detto **aperiodico**.

### Definizione della Serie di Fourier

> [!definition] Serie di Fourier (intervallo $[-\pi, \pi]$)
>
> Data una funzione continua $s(t): \mathbb{R} \to \mathbb{R}$ periodica in $[-\pi, \pi]$:
> $$s(t) = \frac{1}{2} a_0 + \sum_{n=1}^{\infty} \left( a_n \cos(nt) + b_n \sin(nt) \right)$$
> con coefficienti:
> $$a_0 = \frac{1}{\pi} \int_{-\pi}^{\pi} s(t)\, dt \qquad a_n = \frac{1}{\pi} \int_{-\pi}^{\pi} s(t) \cos(nt)\, dt \qquad b_n = \frac{1}{\pi} \int_{-\pi}^{\pi} s(t) \sin(nt)\, dt$$

Il termine $\frac{1}{2} a_0$ è la **componente continua** (media del segnale); i termini $a_n \cos(nt) + b_n \sin(nt)$ sono le **armoniche** di frequenza $n/T$.

### Condizioni di Dirichlet

La serie di Fourier non è definita per qualsiasi funzione. Non sono note le condizioni necessarie, ma esistono condizioni **sufficienti** (teorema di Dirichlet):

> [!theorem] Teorema di Dirichlet
>
> Se $s(t)$ è periodica e **piecewise continuous** (composta da un numero finito di pezzi continui su ogni sottointervallo finito, con limite finito nei punti di discontinuità), allora la serie di Fourier di $s(t)$ esiste e converge in $\mathbb{R}$.

### Esempio: Onda Quadra

Consideriamo il segnale periodico con periodo $2\pi$:

$$s(t) = \begin{cases} 2 & \text{se } -\pi < t < 0 \\ 1 & \text{se } 0 \le t \le \pi \end{cases}$$

Il calcolo dei coefficienti porta a:

$$a_0 = 3, \qquad a_n = 0, \qquad b_n = \begin{cases} 0 & \text{se } n \text{ pari} \\ -\frac{2}{n\pi} & \text{se } n \text{ dispari} \end{cases}$$

La serie risultante, ponendo $n = 2k-1$, è:

$$s(t) = \frac{3}{2} - \sum_{k=1}^{\infty} \frac{2}{(2k-1)\pi} \sin\bigl((2k-1)t\bigr)$$

Solo le armoniche **dispari** contribuiscono, e la loro ampiezza cala come $1/n$.

### Fenomeno di Gibbs

Quando la serie di Fourier approssima una funzione con discontinuità (come un'onda quadra), si osserva un **overshoot** intorno ai punti di salto che non scompare mai, per quanto si aumenti il numero di armoniche. Questo è il **fenomeno di Gibbs**: la serie converge in senso $L^2$, ma nelle vicinanze di ogni discontinuità l'errore rimane del ~9% del salto, indipendentemente dall'ordine di troncamento.

![Fenomeno di Gibbs: con 20 armoniche (sinistra) e 50 armoniche (destra) il salto rimane evidente](images/lezione-25-lab-teoria-dei-segnali-introduzione-e-serie-di-fourier-img-05.jpg)
*Fig. — Fenomeno di Gibbs: aggiungere più armoniche riduce le oscillazioni nel tratto piatto, ma l'overshoot al salto rimane costante (~9% del salto).*

---

## Serie di Fourier con Periodo Arbitrario

La definizione si estende naturalmente a segnali con periodo generico $T$. Tramite la sostituzione $y = 2\pi t / T$, un segnale periodico in $[-T/2, T/2]$ si trasforma in uno periodico in $[-\pi, \pi]$, e i coefficienti diventano:

$$s(t) = \frac{1}{2} a_0 + \sum_{n=1}^{\infty} \left( a_n \cos\frac{2\pi n t}{T} + b_n \sin\frac{2\pi n t}{T} \right)$$

con

$$a_0 = \frac{2}{T} \int_{-T/2}^{T/2} s(t)\, dt \qquad a_n = \frac{2}{T} \int_{-T/2}^{T/2} s(t) \cos\frac{2\pi n t}{T}\, dt \qquad b_n = \frac{2}{T} \int_{-T/2}^{T/2} s(t) \sin\frac{2\pi n t}{T}\, dt$$

---

## Numeri Complessi e Formula di Eulero

Prima di passare alla forma esponenziale della serie, è necessario richiamare i **numeri complessi**. Un numero complesso $\bar{x} = a + jb$ ha parte reale $a$ e parte immaginaria $b$ (con $j = \sqrt{-1}$). Nel piano complesso è rappresentato come un vettore di modulo $|\bar{x}| = \sqrt{a^2 + b^2}$ e fase $\varphi = \tan^{-1}(b/a)$.

> [!definition] Formula di Eulero
>
> $$e^{\pm j\varphi} = \cos\varphi \pm j\sin\varphi$$
>
> Da cui si derivano le formule inverse:
> $$\cos\varphi = \frac{e^{j\varphi} + e^{-j\varphi}}{2} \qquad \sin\varphi = \frac{e^{j\varphi} - e^{-j\varphi}}{2j}$$

Usando l'esponenziale di Eulero, ogni numero complesso si scrive compattamente come $\bar{x} = |x| e^{j\varphi}$, che combina modulo e fase in un unico termine. Questo è particolarmente potente per rappresentare segnali: ampiezza e fase di ogni armonica vengono codificate in un unico coefficiente complesso.

---

## Serie di Fourier in Forma Esponenziale

### La Base Esponenziale

La serie di Fourier generalizzata al dominio complesso usa come base l'insieme di funzioni:

$$e^{j2\pi n F t} \quad \forall n \in \mathbb{Z}$$

poiché $e^{j2\pi n F t} = \cos(2\pi n F t) + j\sin(2\pi n F t)$, ogni elemento della base è una sinusoide complessa alla frequenza $nF$.

> [!definition] Serie di Fourier esponenziale
>
> Dato un segnale periodico $s(t) = s(t+T)$ con frequenza fondamentale $F = 1/T$:
> $$s(t) = \sum_{n=-\infty}^{+\infty} S_n \, e^{j2\pi n F t}$$
>
> dove i coefficienti $S_n$ (in generale complessi) si calcolano come:
> $$S_n = \frac{1}{T} \int_{0}^{T} s(t) \, e^{-j2\pi n F t}\, dt$$

I coefficienti $S_n$ codificano sia ampiezza che fase di ogni armonica: $S_n = |S_n| e^{j\phi_n}$, dove $|S_n|$ è l'ampiezza e $\phi_n = \arg(S_n)$ è la fase dell'armonica $n$-esima.

### Interpretazione Geometrica

Per $n = 0$: la componente continua (media del segnale), $S_0 = \frac{1}{T}\int_0^T s(t)\, dt$.  
Per $n = \pm 1$: frequenza fondamentale $F$, periodo $T$.  
Per $|n| > 1$: armoniche di frequenza $nF$, periodo $T/n$.

> [!tip] Perché la forma complessa?
>
> Con i numeri reali occorrono due coefficienti ($a_n$ e $b_n$) per descrivere ogni armonica. Con la forma complessa basta un solo coefficiente $S_n$ che ne racchiude entrambi. Questo semplifica enormemente la manipolazione matematica e consente di rappresentare segnali $s(t): \mathbb{R} \to \mathbb{C}$, generalizzando la serie per funzioni reali.

### Esempio: Onda Rettangolare con Base Esponenziale

Consideriamo il segnale di periodo $T$ e frequenza $F = 1/T$:

$$s(t) = \begin{cases} 1 & \text{se } |t| \le T/4 \\ 0 & \text{se } T/4 < |t| \le T/2 \end{cases}$$

Il calcolo dei coefficienti dà:

$$S_n = \begin{cases} 1/2 & n = 0 \\ 0 & n \text{ pari} \\ \dfrac{(-1)^k}{-(2k-1)\pi} & n = 2k-1 \end{cases}$$

La serie risultante è quindi:

$$s(t) = \frac{1}{2} + \sum_{k=-\infty}^{+\infty} -\frac{(-1)^k}{(2k-1)\pi} \cos\bigl(2\pi(2k-1)Ft\bigr)$$

Il grafico seguente mostra la convergenza della serie per $T=4$ con $k \in [-1,1]$ (verde), $k \in [-2,2]$ (rosso) e $k \in [-100,100]$ (blu):

![Convergenza della serie di Fourier all'onda rettangolare per k=1, k=2, k=100](images/lezione-25-lab-teoria-dei-segnali-introduzione-e-serie-di-fourier-img-06.jpg)
*Fig. — Al crescere del numero di armoniche considerate (verde → rosso → blu) la serie converge all'onda rettangolare. La forma in blu con k=100 è quasi perfetta, con il solo fenomeno di Gibbs ai salti.*

---

## Lo Spettro di un Segnale

La sequenza ordinata dei coefficienti $\{S_n\}_{n=-\infty}^{+\infty}$ è chiamata **spettro** del segnale. Conoscere lo spettro equivale a conoscere il segnale (dove $s(t)$ è continua; nei punti di discontinuità vale la media dei limiti laterali, per il teorema di Dirichlet).

Poiché i coefficienti $S_n$ sono in generale numeri complessi anche quando $s(t)$ è reale, lo spettro non può essere rappresentato con un singolo grafico 2D. Si usano invece due diagrammi separati, sfruttando la rappresentazione $S_n = |S_n| e^{j\theta_n}$:

- **Spettro di ampiezza**: il grafico di $|S_n|$ in funzione di $n$ (o della frequenza $nF$)
- **Spettro di fase**: il grafico di $\theta_n = \arg(S_n)$ in funzione di $n$

> [!example] Spettro dell'onda quadra antisimmetrica
>
> Per il segnale $s(t) = -1$ se $0 < t \le T/2$, $s(t) = 1$ se $T/2 < t \le T$, i coefficienti sono:
> $$S_n = \begin{cases} 0 & n \text{ pari} \\ \dfrac{2}{n\pi} e^{j\pi/2} & n > 0, \text{ dispari} \\ -\dfrac{2}{n\pi} e^{-j\pi/2} & n < 0, \text{ dispari} \end{cases}$$
> Lo spettro di ampiezza decade come $2/(|n|\pi)$ per gli indici dispari; lo spettro di fase è costante a $+\pi/2$ per $n > 0$ e $-\pi/2$ per $n < 0$.

---

## Segnali Aperiodici e Supporto Limitato

Anche per i segnali aperiodici con supporto limitato a $[a, b)$ — cioè $s(t) = 0$ per $t \notin [a,b)$ — è possibile calcolare la serie di Fourier. Tuttavia, la serie assume implicitamente che il segnale sia periodico con periodo $T = b - a$. La conseguenza è che, invertendo la serie (da $S_n$ a $s(t)$), si ottiene l'**estensione periodica** del segnale originale, non il segnale aperiodico stesso.

$$s^*(t) = \sum_{n=-\infty}^{+\infty} s(t - nT)$$

Questo passaggio è cruciale: la serie di Fourier non può rappresentare segnali davvero aperiodici. Per questi occorre la **Trasformata di Fourier** (argomento delle lezioni successive), che è in un certo senso il limite della serie di Fourier per $T \to \infty$.

---

> [!question] Possibili domande d'esame
>
> - Quali sono le quattro classi di segnali secondo la classificazione tempo/ampiezza? Fai esempi.
> - Cos'è il bitrate di una sorgente digitale? Come dipende da frequenza di campionamento e bit per campione?
> - Enuncia il teorema di Shannon sulla capacità di canale. Come lega SNR, banda e bitrate?
> - Cos'è la serie di Fourier? Scrivi la formula generale e i coefficienti $a_0$, $a_n$, $b_n$.
> - Quali sono le condizioni sufficienti di Dirichlet per l'esistenza della serie di Fourier?
> - Cos'è il fenomeno di Gibbs? Perché non scompare aggiungendo più armoniche?
> - Come si passa dalla serie di Fourier reale a quella in forma esponenziale complessa?
> - Cos'è lo spettro di un segnale? Perché si rappresentano due diagrammi separati (ampiezza e fase)?
> - Perché la serie di Fourier di un segnale aperiodico produce la sua estensione periodica?
> - Calcola i coefficienti della serie di Fourier per un'onda quadra semplice (es. $s(t) = 1$ per $0 < t < T/2$, $s(t) = -1$ per $T/2 < t < T$).
