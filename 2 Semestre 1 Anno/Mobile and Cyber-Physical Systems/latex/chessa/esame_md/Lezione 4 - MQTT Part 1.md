# Fondamenti dell'IoT e Architettura del Protocollo MQTT

## Introduzione al Protocollo MQTT

> [!definition] MQTT
>
> **MQTT** (*Message Queuing Telemetry Transport*) è un protocollo di messaggistica leggero di tipo publish/subscribe, progettato per ambienti con risorse limitate e connettività instabile. 

MQTT è stato creato nel 1999. La sua leggerezza si manifesta nel code footprint ridotto, basso consumo di banda e overhead minimo. Dal punto di vista architetturale, MQTT si appoggia su TCP/IP (porta 1883 in chiaro, 8883 con SSL/TLS). 

L'infrastruttura MQTT concentra volutamente la complessità sul lato server (il broker), mantenendo l'implementazione client estremamente semplice. È *data agnostic* (il payload può essere binario, testo, JSON o XML).

---

## Il Paradigma Publish / Subscribe

![[exam_chessa_mqtt_pubsub.jpg]]
*Fig. — Il paradigma publish/subscribe: i publisher inviano messaggi al broker tramite PUBLISH; i subscriber si registrano (SUBSCRIBE) e ricevono notifiche (PUBLISH dal broker); possono anche disdire (UNSUBSCRIBE).*

A differenza del rigido paradigma client/server, il pub/sub implementa uno schema di interazione *loosely coupled*. Gli attori sono due: i **publisher** (pubblicatori) e i **subscriber** (sottoscrittori), che agiscono entrambi come client senza essere a conoscenza dell'esistenza reciproca. I publisher producono eventi interagendo unicamente con il broker; i subscriber esprimono il proprio interesse verso specifici topic e ricevono notifiche.

> [!tip] Pub/Sub e i tre disaccoppiamenti
>
> Il paradigma **publish/subscribe** introduce tre forme di *decoupling* che lo rendono ideale per l'IoT:
> - **Space decoupling**: publisher e subscriber non si conoscono, non condividono IP né porta.
> - **Time decoupling**: non devono essere operativi contemporaneamente.
> - **Synchronization decoupling**: le operazioni sui client non vengono bloccate durante publish o receive.

Il **broker** è il server dell'infrastruttura: riceve tutti i messaggi, li filtra per topic, li distribuisce ai subscriber interessati. Le operazioni fondamentali sono quattro: *Publish*, *Subscribe*, *Notify*, *Unsubscribe*.

---

## Il Modello MQTT: Connessione e Flusso Operativo

MQTT adotta il paradigma pub/sub con filtraggio basato su **topic**. 

### L'Instaurazione della Connessione
L'interazione inizia con un pacchetto **CONNECT**, contenente parametri come: Client ID, Clean Session, Username/Password, Will flags e KeepAlive. Il broker risponde con un **CONNACK**.

### Gestione e Best Practices dei Topic
Il broker usa il **filtraggio basato su topic** (topic-based filtering). I topic sono stringhe gerarchiche separate da `/` (es. `home/firstfloor/bedroom/temperature`). I subscriber possono usare wildcard:
- **`+`**: sostituisce un singolo livello (es. `home/+/temperature`).
- **`#`**: sostituisce tutti i livelli successivi (es. `home/#`).

Il broker non ispeziona il payload, consentendo cifratura end-to-end.

### Pubblicazione e Struttura dei Messaggi
Il publisher invia messaggi tramite **PUBLISH**, composto da `topicName`, `payload`, `packetId`, `retainFlag`, `dupFlag` e `qos`.

---

## I Meccanismi della Quality of Service (QoS)

MQTT definisce tre livelli di garanzia di consegna dei messaggi tra client e broker:

| Livello | Nome | Garanzia | Meccanismo |
|---------|------|----------|------------|
| QoS 0 | At most once | Nessuna | Nessun ACK |
| QoS 1 | At least once | Almeno una consegna | PUBACK (possibili duplicati) |
| QoS 2 | Exactly once | Esattamente una consegna | 4-way handshake |

### QoS 0 — At Most Once
Modalità *best effort*: il messaggio viene inviato una sola volta senza conferma (ACK) e senza memorizzazione. Adatto per dati che invecchiano rapidamente.

### QoS 1 — At Least Once
Garantisce che il messaggio arrivi almeno una volta. Il broker memorizza il messaggio finché non riceve **PUBACK**. Può generare duplicati.

### QoS 2 — Exactly Once

![[exam_chessa_mqtt_qos2.jpg]]
*Fig. — Handshake a quattro fasi del QoS 2 tra MQTT client e broker: PUBLISH → PUBREC → PUBREL → PUBCOMP.*

QoS 2 è il livello più affidabile e garantisce la consegna esattamente una volta, senza duplicati. Il costo è un handshake a quattro fasi:
1. **PUBLISH**: il client invia il messaggio al broker.
2. **PUBREC** (*Publish Received*): il broker conferma la ricezione e memorizza il messaggio.
3. **PUBREL** (*Publish Release*): il client autorizza il broker a procedere con la consegna effettiva.
4. **PUBCOMP** (*Publish Complete*): il broker conferma l'avvenuta consegna.

Il PUBREC garantisce che il messaggio non vada perso; PUBREL + PUBCOMP garantiscono che non venga consegnato due volte. Due fasi non sarebbero sufficienti perché si genererebbero duplicati in caso di ritrasmissione.
