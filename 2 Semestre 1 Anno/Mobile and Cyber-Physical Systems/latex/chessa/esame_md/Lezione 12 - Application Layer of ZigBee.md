# Application Layer of ZigBee (Appunti d'Esame)

## L'Application Framework e gli Endpoints

L'**Application Layer** del protocollo ZigBee si compone di tre elementi fondamentali: l'**Application Framework**, lo **ZigBee Device Object (ZDO)** e l'**Application Support Sublayer (APS)**.

All'interno dell'Application Framework, ogni **Application Object (APO)** è associato a uno specifico **Endpoint**, identificato da un numero compreso tra 1 e 240. L'Endpoint 0 è strettamente riservato allo ZDO. Grazie a questo sistema, un singolo dispositivo ZigBee può eseguire molteplici applicazioni simultaneamente. Ogni APO è identificato in modo univoco dalla combinazione tra l'indirizzo di rete del dispositivo ospitante e il suo numero di endpoint.

Un **Cluster** è una collezione di comandi e attributi che definiscono l'interfaccia per una specifica funzionalità del dispositivo (ad esempio, OnOff). È identificato da un codice a 16 bit.
Un **Application Profile** è la specifica del comportamento di un'intera classe di applicazioni (es. Home Automation).

---

## Tabella APS, Binding e Indirizzamento Indiretto

![[exam_chessa_zigbee_aps.jpg]]
*Fig. — Esempio di APS Binding Table: ogni entry mappa un endpoint sorgente con cluster e destination address/endpoint.*

L'**Application Support Sublayer (APS)** funge da livello di trasporto leggero che eroga Data Service, Binding Service e Group Management. L'APS filtra i pacchetti per scartare quelli destinati a endpoint non registrati o profili non compatibili, e genera gli acknowledgment end-to-end.

La tabella mostra la **APS Binding Table**, il meccanismo con cui ZigBee implementa l'**indirizzamento indiretto**. Un dispositivo sorgente (che conosce solo il proprio endpoint e il cluster di interesse) non ha bisogno di conoscere l'indirizzo di rete del destinatario: consulta la binding table.

Le colonne della tabella sono:
- **Src Addr (64 bit)**: indirizzo MAC a 64 bit del dispositivo sorgente.
- **Src EP**: endpoint sorgente (1–240).
- **Cluster ID**: il cluster di riferimento (es. `0x0006` = OnOff Cluster).
- **Dest Addr (16/64 bit)**: indirizzo di destinazione (short 16 bit o MAC 64 bit).
- **Addr/Grp**: `A` = indirizzo unicast, `G` = indirizzo di gruppo (multicast).
- **Dest EP**: endpoint destinazione (vuoto per i gruppi).

Questo meccanismo è fondamentale: se un dispositivo cambia indirizzo di rete a 16 bit (dopo un reset), l'APS usa la **Address Map Table** (che associa indirizzi 16-bit agli immutabili MAC 64-bit) per ripristinare i binding automaticamente. Il binding può essere configurato solo su esplicita richiesta dello ZDO di un coordinatore o di un router.

---

## Cluster e Binding tra Dispositivi (Modello Client-Server)

![[exam_chessa_zigbee_binding.jpg]]
*Fig. — Esempio di binding ZigBee: Configuration tool configura un on/off switch, che controlla una Simple lamp e un Dimmer switch, il quale controlla una Dimmable lamp.*

La **ZigBee Cluster Library (ZCL)** introduce un modello gerarchico Client-Server per l'accesso e la manipolazione di un Dominio Funzionale. Lo schema illustra come il binding colleghi dispositivi tramite cluster. Ogni rettangolo contiene le lettere C (Client) o S (Server) per ciascun cluster supportato.

- **Il Server** è colui che ospita fisicamente lo stato (memorizza gli **attributi**).
- **Il Client** è il dispositivo che invia comandi per manipolare gli attributi sul Server.

Nell'esempio:
- La **Configuration tool** (solo C) si lega all'**On/off switch** (S+C) per configurarlo.
- L'**On/off switch** (come client) controlla la **Simple lamp** (S = solo server OnOff).
- Il **Dimmer switch** (S+C) riceve configurazioni (S) e controlla la **Dimmable lamp** che implementa sia OnOff (S) che Level Control (S).

Il binding è unidirezionale: si va da client a server. Viene creato tramite `BIND.request` allo ZDO e memorizzato nella binding table dell'APS. Un singolo client può essere legato a più server (fan-out).

---

## Lo ZigBee Device Object (ZDO)

Lo **ZDO** è la speciale applicazione gestionale del nodo attaccata all'Endpoint 0. I principali servizi esposti includono:
- **Device e Service Discovery**: recupera indirizzi fisici/rete e informazioni sui servizi.
- **Binding Management**: processa e attua fisicamente tutte le richieste di modifica alle tabelle di binding dell'APS.
- **Node e Network Management**: gestisce join, leave e lo smistamento di informazioni sulle routing table.
