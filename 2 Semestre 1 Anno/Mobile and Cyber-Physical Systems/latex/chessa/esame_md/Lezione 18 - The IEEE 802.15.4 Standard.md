# Lo Standard IEEE 802.15.4

Lo standard IEEE 802.15.4 definisce le specifiche del **physical layer** e del **MAC layer** per le **Low-Rate Wireless Personal Area Network** (*LR-WPAN*, reti personali senza fili a bassa velocità). L'obiettivo è fornire un protocollo radio standardizzato per dispositivi a risorse limitate — sensori, attuatori, nodi IoT — che richiedono bassi consumi energetici piuttosto che elevate velocità di trasmissione.

## IEEE 802.15.4 - I (Struttura del Superframe)

![[exam_chessa_ieee802154_superframe.jpg]]
*Fig. — Struttura del superframe IEEE 802.15.4: Beacon frame → CAP (Contention Access Period, slot 0–6) → CFP (Contention Free Period, GTS1 e GTS2, slot 7–11) → Inactive period (slot 12–14) → prossimo Beacon.*

La modalità *beacon-enabled* struttura il tempo in **superframe**, delimitati dall'invio periodico di un frame beacon da parte del PAN coordinator. Il superframe divide il tempo in due porzioni: una **active period** e una **inactive period**. Durante il periodo inattivo il PAN coordinator e i dispositivi connessi possono entrare in modalità a basso consumo (sleep).

La **active period** comprende fino a **16 time slot** di uguale dimensione, suddivisi in:

- **Beacon frame**: il coordinatore trasmette periodicamente un beacon che annuncia l'inizio del superframe, contiene i parametri della rete e la lista dei dispositivi con dati pendenti.
- **CAP** (*Contention Access Period*): fino a 15 slot. I dispositivi competono per il canale usando il protocollo **CSMA-CA a slot** (*slotted CSMA-CA*). Un dispositivo attende un numero casuale di slot; se il canale è occupato riprova dopo un altro backoff casuale; se è libero trasmette e mantiene il canale fino alla fine del frame. Usato per traffico non deterministico (dati aperiodici).
- **CFP** (*Contention Free Period*): opzionale, occupa gli ultimi slot del periodo attivo. Diviso in **GTS** (*Guaranteed Time Slot*), ciascuno assegnato dal PAN coordinator a una specifica applicazione per comunicazioni deterministiche a bassa latenza. Il GTS è accessibile senza CSMA-CA, garantendo latenza deterministica. Ogni CFP può contenere al massimo 7 GTS, ciascuno composto da uno o più slot.

**Inactive period**: tutti i dispositivi (incluso il coordinatore) possono dormire per risparmiare energia. La durata del periodo inattivo determina il duty cycle della rete: un inactive period lungo → basso duty cycle → lunga vita della batteria → latenza più alta.

> [!warning] Il CAP non può essere eliminato
>
> Anche quando è presente il CFP, il CAP è necessario per il mantenimento della rete: gestione di associazioni/disassociazioni, richieste di GTS, ecc. Tutte le transazioni basate su contesa devono completarsi prima dell'inizio del CFP. Un dispositivo che trasmette in un GTS deve completare la trasmissione entro il suo GTS assegnato.

---

## IEEE 802.15.4 - II (Indirect Data Transfer)

![[exam_chessa_ieee802154_indirect.jpg]]
*Fig. — Trasferimento dati indiretto in IEEE 802.15.4: il dispositivo si sveglia al beacon, invia una Data request al coordinatore, riceve ACK e poi i dati.*

Il trasferimento **indiretto** è usato quando il destinatario è un dispositivo che dorme la maggior parte del tempo (RFD, end-device). Il coordinatore non può trasmettere dati in modo asincrono perché il dispositivo potrebbe essere in sleep.

**Da coordinatore a end-device**:
1. Il **coordinatore** memorizza il messaggio e trasmette un **Beacon** che include (nella lista *pending addresses*) l'indirizzo dei dispositivi per cui ha dati in coda.
2. Il **dispositivo**, che dorme la maggior parte del tempo, si sveglia al beacon, ascolta occasionalmente il beacon, legge la lista, se vede il proprio indirizzo invia una **Data request** al coordinatore nel CAP.
3. Il **coordinatore** risponde con un **Acknowledgement** immediato.
4. Il **coordinatore** trasmette i **dati** accodati in uno slot successivo del CAP.
5. Il **dispositivo** risponde con un **Acknowledgement** obbligatorio.
6. Infine il coordinatore rimuove il messaggio dalla lista.

Il device può poi tornare in sleep. Il vantaggio è che il dispositivo non deve rimanere sveglio ad aspettare dati: si sveglia solo al beacon (duty cycle controllato), controlla se ci sono dati per lui, li recupera e dorme di nuovo.

---

## IEEE 802.15.4 - III (Protocollo di Associazione)

![[exam_chessa_ieee802154_association.jpg]]
*Fig. — Protocollo di associazione IEEE 802.15.4: sequenza di messaggi tra NWK e MAC layer del dispositivo (sinistra) e del coordinatore/router (destra).*

L'associazione è il processo con cui un dispositivo entra a far parte di una PAN. È pensata per reti beacon-enabled e si compone di una fase sul lato end-device e una sul lato coordinatore. Lo schema mostra il protocollo di **associazione** visto a livello di primitives NWK-MAC.

### Lato End-Device

Il dispositivo che vuole associarsi deve aver identificato in anticipo la PAN di destinazione attraverso il servizio **SCAN** (scansione attiva). 

1. Il NWK del dispositivo emette `ASSOCIATE.request` al proprio MAC layer. Prende come parametri l'identificatore di PAN, l'indirizzo del coordinatore e il proprio indirizzo IEEE a 64 bit esteso.
2. Il MAC invia un **Association request** frame al coordinatore. La richiesta viene inviata nel CAP usando CSMA-CA a slot.
3. Il coordinatore MAC risponde con **Acknowledgement** immediato — ma questo non implica che la richiesta sia stata accettata.

### Lato Coordinatore e Completamento

Dopo aver ricevuto la richiesta, il MAC layer del coordinatore emette **ASSOCIATE.indication** verso il network layer (NWK), che decide se accettare o rifiutare. In caso di accettazione, il NWK layer:

4. Il coordinatore NWK riceve `ASSOCIATE.indication` e prepara la risposta con `ASSOCIATE.response`, selezionando un **indirizzo a 16 bit** che il dispositivo utilizzerà in futuro al posto dell'indirizzo a 64 bit.
5. Il dispositivo aspetta un **pre-defined waiting time** (il coordinatore deve elaborare la richiesta e decidere se accettarla). Il MAC layer invia la risposta di associazione usando **trasmissione indiretta**.
6. Il dispositivo MAC invia una **Data request** per recuperare la risposta del coordinatore.
7. Il coordinatore MAC risponde con **Acknowledgement** + **Association response** (contenente l'indirizzo a 16 bit assegnato e lo status della richiesta).
8. Il dispositivo MAC invia **Acknowledgement** finale.
9. Il dispositivo NWK riceve `ASSOCIATE confirm` con l'indirizzo assegnato.
10. Il coordinatore NWK riceve `COMM.STATUS.indication`, segnalando che l'associazione è conclusa — con successo o con un codice di errore.
