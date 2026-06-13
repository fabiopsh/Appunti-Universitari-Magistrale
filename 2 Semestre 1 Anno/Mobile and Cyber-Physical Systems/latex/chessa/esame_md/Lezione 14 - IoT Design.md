# IoT Design (Appunti d'Esame)

## Duty Cycle e Efficienza Energetica

La soluzione alla sfida energetica nell'IoT si chiama **duty cycle** (ciclo di lavoro). Il duty cycle è la frazione di un periodo in cui il sistema (o un suo componente) è attivo. L'idea è di sfruttare i periodi di inattività per mettere in sleep tutti i componenti possibili, riducendo al minimo il consumo.
Applicarlo in modo aggressivo è la leva principale per estendere la vita della batteria, attivando ogni componente **solo quando strettamente necessario**.

### Esempio pratico: il codice Arduino e Calcolo del Duty Cycle

![[exam_chessa_dutycycle_code.jpg]]
*Fig. — Codice Arduino che implementa il duty cycling selettivo dei componenti (sensore, radio) e tabella dei consumi in mA per componente e stato.*

Il codice mostra il pattern classico per minimizzare i consumi spegnendo esplicitamente ogni componente quando non serve:
```c
void loop() {
    turnOn(analogSensor);   // sensore acceso solo durante lettura
    int sensorValue = analogRead(A0); // lettura
    turnOff(analogSensor);  // sensore spento
    
    float voltage = sensorValue * (5.0 / 1023.0);
    
    turnOn(radioInterface); // radio accesa solo durante trasmissione
    Serial.println(voltage);
    turnOff(radioInterface);
    
    idle(380);  // MCU in sleep per 380 ms
}
```

Usando i valori della tabella (es. Tmote Sky):
- **Processore**: attivo 8 mA, sleep 15 μA
- **Radio**: TX 17.4 mA, RX 19.7 mA, sleep 20 μA
- **Sensore**: attivo 5 mA, sleep 5 μA

Il duty cycle di ciascun componente si calcola come:
$$DC_\text{componente} = \frac{t_\text{attivo}}{T_\text{periodo}}$$

Se le operazioni di sensing + TX durano ~20 ms e il ciclo totale è 400 ms, il duty cycle della radio è $20/400 = 5\%$. La corrente media risultante è molto inferiore alla corrente di picco, estendendo la vita della batteria di ordini di grandezza.
La perdita di capacità della batteria del 3%/anno indica che anche con battery standby c'è un degrado nel tempo.

---

## Effetto del duty cycle sulla vita della batteria

![[exam_chessa_dutycycle_graph.jpg]]
*Fig. — Grafico log-log: vita della batteria (mesi) vs capacità della batteria (mAh) per duty cycle 100% (model1) e 5% (model2).*

Il grafico mostra l'impatto del duty cycle sulla vita della batteria in scala logaritmica. Due modelli a confronto:

- **Model 1 (100% DC)**: il dispositivo è sempre attivo. La vita della batteria scala linearmente con la capacità ma rimane nell'ordine dei mesi (0.01–0.3 mesi per capacità 500–3000 mAh).
- **Model 2 (5% DC)**: il dispositivo è attivo solo il 5% del tempo. La vita si estende di un fattore ~20: con la stessa batteria, si passa da 0.1 a circa 2–8 mesi.

La scala logaritmica rivela che la relazione vita-capacità non è lineare: il duty cycle agisce moltiplicativamente. Ridurre il duty cycle da 100% a 5% equivale a moltiplicare la capacità effettiva della batteria per 20.

**Conclusione progettuale**: per applicazioni IoT con autonomia di anni, ridurre il duty cycle è molto più efficace che aumentare la capacità della batteria. Una batteria da 3000 mAh a 5% DC dura circa 8 mesi; per durare anni si deve abbassare ulteriormente il duty cycle o usare energy harvesting. Ad alti DC, aumentare la capacità della batteria ha un effetto quasi trascurabile.
