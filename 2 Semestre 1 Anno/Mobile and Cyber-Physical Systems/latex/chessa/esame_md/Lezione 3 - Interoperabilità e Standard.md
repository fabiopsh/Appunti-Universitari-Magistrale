# Interoperabilità e Standard nell'IoT

Il concetto di **interoperabilità** rappresenta una delle sfide cruciali nello sviluppo dell'Internet of Things. Implementare una soluzione IoT "dal basso", ovvero dal livello fisico fino all'applicazione, non costituisce di per sé un problema tecnico insormontabile; tuttavia, questo approccio porta spesso alla creazione di quelli che vengono definiti *vertical silos*.

![[exam_chessa_interoperability.jpg]]
*Fig. — Rete IoT eterogenea: dispositivi di produttori diversi (colori diversi) comunicano attraverso gateway di integrazione.*

Lo schema mostra una rete in cui dispositivi appartenenti a ecosistemi diversi devono comunicare tra loro. Il problema fondamentale è proprio l'**interoperabilità**.

> [!definition] Vertical Silos
>
> In questo modello, una soluzione funziona esclusivamente all'interno del proprio ecosistema: i dispositivi proprietari comunicano solo con l'infrastruttura dello stesso fornitore, rendendo incompatibili i prodotti di terze parti.

Questa strategia di design è spesso intenzionale e risponde a un modello di business basato sul *vendor lock-in*.

> [!definition] Vendor Lock-in
>
> La pratica di "ingabbiare" il cliente con l'obiettivo di prevenire l'utilizzo di componenti di altri produttori e imporre costi elevati per l'eventuale migrazione verso soluzioni alternative. Tale migrazione comporta spesso la completa riprogettazione e il dispiegamento di un nuovo sistema, con il rischio di entrare semplicemente in un altro silos.

Storicamente, il problema dell'interoperabilità risiedeva principalmente a livello hardware, ma nell'IoT moderno la questione si è spostata prevalentemente a livello software. La soluzione universalmente riconosciuta per mitigare queste barriere è l'introduzione e l'adozione di **standard** condivisi.

## La Necessità e la Complessità degli Standard

Gli standard nascono dalla necessità di ridurre i costi di sviluppo tecnologico attraverso accordi tra diversi produttori, in un regime di **coopetition** (cooperazione tra competitor). Solitamente, la standardizzazione avviene quando una tecnologia diventa matura. 

Tuttavia, la proliferazione degli standard (come Wi-Fi, ZigBee, Bluetooth) ha spostato il problema dell'interoperabilità ai livelli middleware e applicativo. Oggi esistono numerosi protocolli di livello applicativo (MQTT, CoAP, LWM2M, ecc.), creando una situazione in cui l'incompatibilità non è solo tra silos verticali, ma anche tra standard differenti.

Per gestire questa eterogeneità si ricorre agli **Application-level gateway**. Questi dispositivi non si limitano a tradurre protocolli di basso livello: mappano comportamenti applicativi differenti l'uno nell'altro, operando come interpreti semantici tra ecosistemi incompatibili.

## Configurazioni di Integrazione

Le architetture IoT possono assumere configurazioni molto diverse in base all'omogeneità dei dispositivi e dei protocolli coinvolti. La tabella seguente riassume i quattro tipi principali:

| Tipo | Fornitore | Protocollo | Necessità di gateway |
|------|-----------|------------|----------------------|
| A | Unico | Unico | No |
| B | Multiplo | Unico (condiviso) | No o minimale |
| C | Multiplo | Diversi | Sì — Integration Gateway per la traduzione |
| D | Multiplo | Eterogenei e distribuiti | Sì — gateway multipli con mappature complesse |

Al crescere della complessità, dal Tipo A al Tipo D, il gateway di integrazione deve gestire un numero esponenziale di mappature tra protocolli allo stesso livello. La sfida non è solo tecnica ma organizzativa: ogni nuovo fornitore o protocollo aggiunto alla rete moltiplica le combinazioni da gestire.

---

## Sicurezza nell'IoT

![[exam_chessa_iot_security.jpg]]
*Fig. — Architettura di sicurezza IoT: dispositivi vincolati (C), gateway (G), applicazioni (A) e relative misure di sicurezza per ogni livello.*

Lo schema mostra un'architettura IoT a strati in cui la sicurezza deve essere garantita a ogni livello: tra dispositivi periferici e gateway (autenticazione + trasferimento sicuro), e tra gateway e cloud/applicazione (sicurezza dei dati a riposo + autenticazione).

La sicurezza nei sistemi cyber-fisici e nell'IoT ha raggiunto un punto di crisi. A differenza dei sistemi IT tradizionali, i dispositivi IoT sono spesso sistemi embedded economici, prodotti con forti incentivi a ridurre costi e tempi di immissione sul mercato (*Time-to-Market*), a discapito della sicurezza. La conseguenza sono centinaia di milioni di dispositivi vulnerabili, privi di meccanismi di patching efficaci.

Le conseguenze variano dall'inserimento di dati falsi nella rete alla compromissione delle operazioni fisiche.

## Requisiti di Sicurezza secondo ITU-T Y.2066

La raccomandazione **Y.2066** dell'ITU-T identifica i requisiti fondamentali per la sicurezza IoT organizzandoli in tre aree concettuali distinte:

1. **Sicurezza della comunicazione**: garantire la riservatezza e l'integrità dei dati in transito o il trasferimento tra dispositivi e piattaforme.
2. **Sicurezza della gestione dei dati**: proteggere riservatezza e integrità quando i dati sono archiviati o elaborati (*data at rest*).
3. **Sicurezza della fornitura del servizio**: prevenire accessi non autorizzati ai servizi e proteggere le informazioni private degli utenti.

A questi si aggiungono l'**autenticazione mutua** (entrambe le parti si verificano reciprocamente) e la capacità di audit di sicurezza.

## Il Ruolo del Gateway nella Sicurezza

In un'architettura IoT, il gateway agisce spesso come punto centrale di applicazione delle policy di sicurezza. 
- Gestisce identificazione e autenticazione di ogni dispositivo connesso.
- Protegge la privacy dei dispositivi periferici.
- Supporta manutenzione, aggiornamento firmware e autodiagnosi remota.
- Applica policy di configurazione dinamiche.

> [!warning] Dispositivi vincolati e limiti di sicurezza
>
> I **dispositivi vincolati** (*constrained devices*) pongono ostacoli concreti, spesso non disponendo di hardware crittografico dedicato, rendendo impraticabile la cifratura dei dati archiviati. Con la diffusione del *Massive IoT*, la privacy diventa una criticità per l'enorme mole di dati sensibili raccolti.
