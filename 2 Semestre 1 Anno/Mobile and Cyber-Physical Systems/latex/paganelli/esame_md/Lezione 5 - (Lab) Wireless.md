# Lezione 5 - (Lab) Wireless

## Il Problema del Terminale Nascosto (Hidden Terminal Problem)

A causa dell'attenuazione con la distanza (o per la presenza di ostacoli fisici come montagne e palazzi), due nodi potrebbero non essere in grado di percepirsi a vicenda, pur essendo entrambi nel raggio di un terzo nodo intermedio. Se A e C vogliono comunicare con B, ma A e C sono fuori portata l'uno per l'altro, entrambi potrebbero iniziare a trasmettere contemporaneamente — inconsapevoli della reciproca interferenza — causando una collisione disastrosa al ricevitore B. Questo è il **Problema del Terminale Nascosto** (*Hidden Terminal Problem*), e non può essere rilevato dal classico meccanismo CSMA/CD.

![[Pasted image 20260429160400.png]]

Il problema del **terminale nascosto** nasce da una limitazione fisica fondamentale delle reti wireless: la potenza del segnale radio cala con il quadrato della distanza, e la comunicazione può avvenire solo tra nodi sufficientemente vicini. In questo scenario, A e C vogliono entrambi trasmettere a B, ma A e C si trovano fuori dal raggio radio l'uno dell'altro.

Supponiamo che A stia già trasmettendo verso B. La stazione C, prima di trasmettere, esegue il **Carrier Sense**: ascolta il canale per verificare se è libero. Poiché C non riesce a sentire il segnale di A (sono fuori portata), C conclude erroneamente che il canale sia libero e inizia a trasmettere verso B (o verso D). Il risultato è che i segnali di A e di C si sovrappongono fisicamente nell'antenna di B, generando una **collisione** che B riceve come segnale incomprensibile. Né A né C rilevano la collisione, perché ciascuna sente solo il proprio segnale (che è enormemente più forte di qualsiasi segnale di ritorno).

Questo è il motivo per cui il protocollo **CSMA/CD**, standard nelle reti Ethernet cablate, non può essere usato nelle reti wireless: il meccanismo di rilevamento delle collisioni richiede che il trasmettitore possa ascoltare il canale mentre trasmette, il che è impossibile in radio (il self-signal del trasmettitore è ordini di grandezza più forte di qualsiasi segnale debole in arrivo).

> [!tip] Il punto chiave
>
> Con CSMA classico, il Carrier Sense viene eseguito dal trasmettitore, ma quello che conta è lo stato del canale **al ricevitore**. Il terminale nascosto è "nascosto" solo rispetto al trasmettitore corrente, non rispetto al ricevitore.

La soluzione a questo problema è il meccanismo **RTS/CTS**.
