# Embedded Programming e Arduino

## Modelli di Programmazione per Embedded

Il problema della gestione dell'I/O con memoria limitata ha portato allo sviluppo di diversi modelli di programmazione. I due esempi principali sono il **modello Arduino** (event loop sincrono) e il **modello TinyOS** (eventi + task asincroni).

### Il Modello Arduino

![[exam_chessa_embedded_arduino.jpg]]
*Fig. — Modello di esecuzione Arduino: init → loop() ripetuto. I comandi attivano l'hardware; delay() aspetta; il timer fires avvia la ripetizione.*

Arduino adotta un approccio estremamente semplice: il lavoro è definito in una singola funzione `loop()`, eseguita ripetutamente da **un unico thread**. Non c'è sospensione del thread, non ci sono context switch. 

1. **init**: la funzione `setup()` viene eseguita una sola volta all'avvio. Inizializza l'hardware, configura i pin, prepara le comunicazioni seriali.
2. **Main loop**: la funzione `loop()` viene invocata ripetutamente all'infinito dal runtime Arduino.
3. **Command**: dentro `loop()`, il codice interagisce con l'hardware tramite comandi sincroni (es. `analogRead()`, `Serial.println()`).
4. **Delay**: `delay(ms)` blocca l'esecuzione per il tempo specificato (busy waiting o sleep), poi il timer fires riavvia il loop.

Il modello è semplice ma **bloccante**: durante `delay()` il processore non può fare altro. Se un'operazione di I/O richiede tempo, si aspetta semplicemente che si completi. Gli interrupt possono intervenire anche durante il delay, ma il thread principale rimane sospeso.

### Il Modello TinyOS

![[exam_chessa_embedded_tinyos.jpg]]
*Fig. — Modello di esecuzione TinyOS: catena di eventi (Timer → Read → task → Send) senza loop bloccante. Il data processing avviene nel task asincrono.*

TinyOS usa un modello **event-driven** con componenti e interfacce, progettato per massimizzare l'efficienza energetica e gestire attività indipendenti senza sprecare memoria per i contesti dei thread. Non esiste un loop bloccante: il sistema è guidato dagli eventi hardware. La catena tipica:

1. **init**: configura timer e hardware.
2. **Timer handler** (evento): scatta quando il timer fires → avvia una lettura dal sensore (`Start read`).
3. **Read handler** (evento): scatta quando la lettura è completata (`Read done`) → posta un task per il processing.
4. **task**: elabora i dati (*Data processing happens here*) → avvia la trasmissione radio. I task sono unità di elaborazione non-preemptive eseguite sequenzialmente. Un task non aspetta mai (salva memoria).
5. **Send handler** (evento): scatta quando la trasmissione è completa → riconfigura il timer per il prossimo ciclo.

**Vantaggi del modello event-driven**:
- Nessun busy waiting: il processore dorme tra un evento e l'altro.
- Nessuno stack multiplo: un unico stack (run-to-completion semantics).
- Efficienza energetica: il MCU è attivo solo durante gli handler.

**Confronto con Arduino**: Arduino è più semplice da programmare (loop sequenziale), ma meno efficiente in termini energetici. TinyOS è ottimale per nodi a basso consumo dove ogni microsecondo di sleep conta.

---

## Interrupt in Arduino

Sebbene il modello base di Arduino sia la lettura sincrona dei sensori nel loop, Arduino offre anche un'interfaccia per gli **interrupt**, che abilita l'accesso asincrono a sensori e attuatori.

### Interrupt Esterni: `attachInterrupt()`

![[exam_chessa_arduino_interrupt.jpg]]
*Fig. — Esempio di programmazione con interrupt su Arduino: attachInterrupt() collega il pin 2 a interruptSwitchGreen(); count viene resettato e il LED acceso all'interrupt.*

```cpp
volatile int greenLed = 7;
volatile int count = 0;

void setup() {
  Serial.begin(9600);
  pinMode(greenLed, OUTPUT);
  digitalWrite(greenLed, LOW);
  attachInterrupt(0, interruptSwitchGreen, RISING); // 0 = pin 2
}

void loop() {
  count++;
  delay(1000);
  // Gli interrupt vengono ricevuti anche dentro delay!
  Serial.print("waiting:");
  Serial.println(count);
  if (count == 10) {
    count = 0;
    digitalWrite(greenLed, LOW);
    Serial.println("now off");
  }
}

void interruptSwitchGreen() {
  digitalWrite(greenLed, HIGH);
  count = 0;
  Serial.print("now on");
}
```

Arduino Uno dispone di **due pin per interrupt esterni**: INT0 (pin 2) e INT1 (pin 3). `attachInterrupt(0, interruptSwitchGreen, RISING)` collega il pin 2 alla funzione `interruptSwitchGreen`, eseguita automaticamente sul fronte di salita del segnale.

**Punti chiave e regole per gli interrupt handler**:
- `delay()` **non funziona** dentro un interrupt handler
- `millis()` **non viene incrementato** dentro un interrupt handler  
- La variabile `count` è dichiarata `volatile`: indica al compilatore di non ottimizzarla in registro (forza la lettura dalla RAM), perché può essere modificata da handler fuori dal flusso normale, garantendo la coerenza del valore.
- Gli interrupt sono ricevuti **anche durante `delay()`**: il delay non disabilita gli interrupt, quindi l'handler può intervenire in qualsiasi momento.
- I handler devono essere **il più brevi possibile**: solo aggiornamento di strutture dati e comandi all'HW.
- **Utilizzo tipico negli embedded IoT**: gli interrupt sono usati per ricevere dati dal sensore (read done), notificare la fine di una trasmissione radio, o rispondere a eventi fisici senza polling continuo, risparmiando energia.

---

## Calcolo del Duty Cycle e Gestione Energetica

![[exam_chessa_dutycycle_code.jpg]]
*Fig. — Codice Arduino che implementa il duty cycling selettivo dei componenti (sensore, radio) e tabella dei consumi in mA per componente e stato.*

Il **duty cycle** di un componente è la frazione di tempo in cui è attivo rispetto al periodo totale. La strategia fondamentale di risparmio energetico nei dispositivi IoT è attivare ogni componente **solo quando strettamente necessario**.

Il codice mostra il pattern classico:
```
turnOn(analogSensor)   → sensore acceso solo durante lettura
analogRead(A0)         → lettura
turnOff(analogSensor)  → sensore spento

turnOn(radioInterface) → radio accesa solo durante trasmissione
Serial.println(voltage)
turnOff(radioInterface)

idle(380)              → MCU in sleep 380ms
```

> [!example] Calcolo del Duty Cycle
>
> Usando i valori della tabella (es. Tmote Sky):
> - Processore attivo: 8 mA, sleep: 15 μA
> - Radio TX: 17.4 mA, RX: 19.7 mA, sleep: 20 μA
> - Sensore: 5 mA, sleep: 5 μA
> 
> Se le operazioni di sensing + TX durano ~20 ms e il ciclo totale è 400 ms, il duty cycle della radio è 20/400 = 5%. La corrente media risultante è molto inferiore alla corrente di picco, estendendo la vita della batteria di ordini di grandezza.
> Il sistema è attivo solo per circa il 5% del tempo.

### Impatto sulla Vita della Batteria

![[exam_chessa_dutycycle_graph.jpg]]
*Fig. — Grafico log-log: vita della batteria (mesi) vs capacità della batteria (mAh) per duty cycle 100% (model1) e 5% (model2).*

Il grafico mostra l'impatto del duty cycle sulla vita della batteria in scala logaritmica. Due modelli a confronto:

- **Model 1 (100% DC)**: il dispositivo è sempre attivo. La vita della batteria scala linearmente con la capacità ma rimane nell'ordine dei mesi (0.01–0.3 mesi per capacità 500–3000 mAh).
- **Model 2 (5% DC)**: il dispositivo è attivo solo il 5% del tempo. La vita si estende di un fattore ~20: con la stessa batteria, si passa da 0.1 a circa 2–8 mesi.

La scala logaritmica rivela che la relazione vita-capacità non è lineare: il duty cycle agisce moltiplicativamente. Ridurre il duty cycle da 100% a 5% equivale a moltiplicare la capacità effettiva della batteria per 20.

**Conclusione progettuale**: per applicazioni IoT con autonomia di anni, ridurre il duty cycle è molto più efficace che aumentare la capacità della batteria. Una batteria da 3000 mAh a 5% DC dura circa 8 mesi; per durare anni si deve abbassare ulteriormente il duty cycle o usare energy harvesting. La perdita di capacità della batteria del 3%/anno indica che anche con battery standby c'è un degrado nel tempo.
