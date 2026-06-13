# Campionamento, Quantizzazione e DFT

## Da Segnale Analogico a Digitale: Campionamento e Quantizzazione

I sistemi digitali moderni lavorano esclusivamente con dati discreti. Un segnale analogico continuo deve essere convertito in una sequenza di valori discreti. Questo processo si articola in due fasi: **campionamento** e **quantizzazione**. Dopo il filtraggio anti-aliasing (passa-basso con $f_{taglio} = f_c/2$), avviene il campionamento, seguito dalla quantizzazione e infine dalla codifica binaria.

### Il Campionamento e il Teorema di Nyquist-Shannon

**Campionare** un segnale $s(t)$ significa estrarre i valori che il segnale assume a istanti discreti regolarmente spaziati. Il parametro chiave è la frequenza di campionamento $f_c = 1/T_c$.

Affinché un segnale di banda $B$ (frequenza massima $f_{max}$) sia ricostruito perfettamente dai suoi campioni, la frequenza di campionamento deve soddisfare il **Teorema di Nyquist-Shannon**:
$$f_c \geq 2 \cdot f_{max}$$

La frequenza $f_{Nyquist} = f_c/2$ è la massima frequenza rappresentabile senza aliasing.

### Aliasing

![[exam_mod2_sampling_aliasing.jpg]]

Campionare introduce un'ambiguità: da un insieme finito di campioni non si può distinguere univocamente quale segnale li ha generati. L'**aliasing** è la distorsione che si verifica quando il segnale rosso (alta frequenza) e il segnale blu (bassa frequenza) producono **identici campioni** (i punti neri). Il segnale a bassa frequenza è l'**alias** di quello ad alta frequenza: un'identità fantasma creata dal sottocampionamento. 

Se nel segnale originale sono presenti frequenze superiori a $f_{Nyquist}$, queste appaiono come frequenze più basse nello spettro discreto, rendendo impossibile la ricostruzione.

**Come prevenire l'aliasing:** si applica un **filtro anti-aliasing** (filtro passa-basso analogico) prima del campionatore, che elimina tutte le componenti con $f > f_c/2$. Solo dopo si campiona. Questo garantisce che il segnale digitale rappresenti fedelmente l'originale entro la banda di interesse.
Esempi: 
- Audio CD: frequenza di campionamento 44.1 kHz, per limiti uditivi di ~20 kHz.
- Telefonia: 8 kHz.
- WiFi e reti cellulari: i ricevitori campionano il segnale RF ad almeno $2 \times B_{canale}$.

### Quantizzazione

![[exam_mod2_quantization.jpg]]

La **quantizzazione** è il secondo passo nella conversione analogico-digitale. Dopo aver campionato il segnale nel tempo, ogni campione deve essere approssimato al livello discreto più vicino tra un insieme finito di valori possibili (usando un numero finito di bit).

Dato un campione con valore reale, si sceglie il **livello di quantizzazione** $y_k$ più vicino e si assegna il codice binario. Se si usano $M$ bit per campione, si hanno $2^M$ livelli di quantizzazione, spaziati di un passo $\Delta = \frac{s_{max} - s_{min}}{2^M}$.

**L'errore di quantizzazione:** l'approssimazione introduce un errore inevitabile $e = s(t) - y_k$, che ha valore assoluto al massimo $\Delta/2$. Nel grafico in basso si vede chiaramente che l'errore è un segnale oscillante (dovuto all'arrotondamento al gradino) con ampiezza piccola ($\approx \Delta/2$) e frequenza elevata. Questo errore viene tipicamente modellato come rumore bianco uniforme.

**Trade-off:**
- Aumentare $M$ (più bit per campione) riduce $\Delta$ e quindi l'errore di quantizzazione, ma aumenta il **bitrate** richiesto: $\text{Bitrate} = f_c \times M$ bit/s.
- Il **SNR di quantizzazione** cresce approssimativamente di 6 dB per ogni bit aggiunto: $\text{SNR}_{dB} \approx 6.02 \cdot M + 1.76$ dB.

## Trasformata Discreta di Fourier (DFT)

La **Trasformata di Fourier Discreta** (DFT) è la versione *calcolabile da un computer* dell'analisi di Fourier: opera su un segnale discreto di lunghezza finita $N$ e produce $N$ coefficienti frequenziali.

**La formula:**
dato un segnale campionato $s_n$ (con $n = 0, 1, \ldots, N-1$), la DFT calcola il coefficiente $S_f$ per ogni frequenza discreta $f = 0, 1, \ldots, N-1$:
$$S_f = \sum_{n=0}^{N-1} s_n \, e^{-j\frac{2\pi f}{N}n}$$

**Interpretazione:**
- Ogni coefficiente $S_f$ è un numero complesso: il suo **modulo** $|S_f|$ è l'ampiezza del contributo alla frequenza $f$, la sua **fase** $\arg(S_f)$ è lo sfasamento della componente sinusoidale corrispondente.
- La DFT assume implicitamente che il segnale di $N$ campioni sia la ripetizione periodica di un pattern. È il corrispettivo discreto della serie di Fourier.

**L'algoritmo FFT:** 
Il calcolo diretto della DFT ha complessità $O(N^2)$. L'algoritmo **FFT** (*Fast Fourier Transform*) riduce la complessità a $O(N \log N)$ sfruttando la simmetria del fattore. Per $N = 1024$ punti, la FFT è ≈100 volte più veloce della DFT diretta.
**Applicazioni pratiche:** Analisi spettrale, filtraggio digitale (e compressione JPEG tramite DCT), e implementazione dell'**OFDM** (Orthogonal Frequency Division Multiplexing) in 4G/5G, che crea il segnale con una IFFT e lo demodula con una FFT.
