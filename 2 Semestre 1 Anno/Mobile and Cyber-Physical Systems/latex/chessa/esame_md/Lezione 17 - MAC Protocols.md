# MAC Protocols (Appunti d'Esame)

Nei sistemi IoT, il protocollo MAC deve minimizzare il consumo energetico riducendo il **duty cycle**. Esistono vari approcci, tra cui la sincronizzazione (S-MAC) e il preamble sampling (B-MAC, X-MAC).

## Sincronizzazione: S-MAC (Sensor-MAC)

![[exam_chessa_smac.jpg]]
*Fig. — S-MAC: i nodi A–F hanno schedule sincronizzati (verde = listen, rosso = active/TX). La latenza multi-hop si accumula: il pacchetto da A deve aspettare i periodi di ascolto di ogni hop successivo.*

**S-MAC** riduce il consumo energetico tramite **sincronizzazione locale**: nodi vicini si accordano su un periodo di ascolto comune (listen period) e dormono nel resto del tempo.

**Meccanismo**:
1. Ogni nodo trasmette periodicamente un pacchetto **SYNC** che annuncia il proprio schedule.
2. I vicini che ricevono il SYNC adottano lo stesso schedule o mantengono il proprio e memorizzano quello del vicino.
3. Nel **listen period**: esecuzione di CSMA/CA con RTS/CTS prima di trasmettere.
4. Nel **sleep period**: la radio è spenta.

**Problema della latenza multi-hop**: in un percorso multi-hop, ogni nodo deve aspettare il periodo di ascolto del nodo successivo. La latenza totale si accumula ad ogni salto (es. latenza proporzionale a $n \cdot t_{sleep}/2$).
**Adaptive duty cycle**: per mitigare questo, se un nodo riceve un RTS o CTS in sorveglianza, capisce che c'è traffico nelle vicinanze e mantiene la radio accesa per il resto della trasmissione, anticipando che potrebbe essere il prossimo hop.

---

## Preamble Sampling: B-MAC

![[exam_chessa_bmac.jpg]]
*Fig. — B-MAC: il mittente (in alto) invia un lungo preamble seguito dai data; il ricevitore (in basso) si sveglia, ascolta, individua il preamble, rimane sveglio e riceve i data.*

**B-MAC** usa il **preamble sampling** (Low Power Listening, LPL) ed elimina del tutto la sincronizzazione:

- **Lato ricevitore**: si sveglia periodicamente (ogni $t_{check}$), campiona il canale per un breve istante. Se rileva il preambolo, rimane sveglio e riceve i dati; altrimenti si riaddormenta subito.
- **Lato mittente**: quando deve trasmettere, invia un **preambolo lungo** per una durata $> t_{check}$, per garantire che qualunque sia il momento in cui il ricevitore si sveglia, trovi il preambolo "in aria". Dopo il preambolo, invia i dati effettivi.

**Trade-off e Ottimizzazione**:
![[exam_chessa_bmac_graph.jpg]]
*Fig. — Grafico B-MAC: vita del trasmettitore (anni) vs intervallo di check t_check (ms), per diverse frequenze di campionamento (1 sample/min, 1/5 min, 1/10 min, 1/20 min).*

Il trade-off fondamentale riguarda come la frequenza di trasmissione e $t_{check}$ influenzano la batteria del **trasmettitore**.
Al crescere di $t_{check}$, il preambolo deve essere più lungo, quindi il trasmettitore consuma di più per ogni trasmissione. Tuttavia, la vita del trasmettitore ha un **massimo** per un valore ottimale di $t_{check}$:
- $t_{check}$ troppo breve → il ricevitore si sveglia spesso, preambolo corto (basso overhead per TX ma alto per RX).
- $t_{check}$ troppo lungo → preambolo lunghissimo, overhead troppo alto per il TX.

---

## Evoluzione: X-MAC vs B-MAC

![[exam_chessa_xmac.jpg]]
*Fig. — Confronto LPL (B-MAC, righe superiori) e X-MAC (righe inferiori): X-MAC usa preamble corti con indirizzo target; il ricevitore invia early ACK; mittente e ricevitore risparmiano tempo ed energia.*

**X-MAC** migliora B-MAC risolvendo lo spreco energetico del preambolo lungo e l'overhearing (nodi non destinatari che restano svegli inutilmente durante il lungo preambolo):

- **Mittente**: invia una sequenza di **short preambles** (strobe) contenenti ciascuno l'indirizzo del destinatario target.
- **Ricevitore target**: si sveglia, legge il proprio indirizzo nel preambolo, e invia immediatamente un **early ACK**.
- **Mittente**: ricevendo l'ACK, interrompe i preamboli e trasmette subito i dati.
- I **non-destinatari** vedono il proprio indirizzo assente nel preambolo e si riaddormentano subito.

Il risultato è un forte risparmio sia per il mittente (preambolo più corto in media) sia per il ricevitore (meno overhearing).
