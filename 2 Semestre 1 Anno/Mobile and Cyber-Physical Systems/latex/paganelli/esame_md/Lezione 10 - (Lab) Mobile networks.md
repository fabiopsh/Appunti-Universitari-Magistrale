# Lezione 10 - (Lab) Mobile networks

La mobilità nelle reti di telecomunicazione moderne si estende lungo un ampio spettro: dall'assenza totale di spostamento fino a scenari in cui un dispositivo attraversa reti di operatori diversi mantenendo attive le proprie sessioni. Questo capitolo analizza le architetture che rendono possibile tale mobilità — in particolare nelle reti 4G/5G — esaminando i meccanismi di registrazione, i due approcci di routing (indiretto e diretto) e le procedure di _handover_ tra stazioni base.

## Lo Spettro della Mobilità e la Home Network

Dal punto di vista infrastrutturale, la mobilità non è una proprietà binaria ma uno spettro continuo. L'estremo di maggiore interesse è l'**alta mobilità**: un dispositivo che cambia rete mantenendo attive le connessioni in corso. Per gestire questo livello di mobilità è indispensabile il concetto di **home network**: una fonte autorevole e centralizzata che registra la posizione attuale del dispositivo e dalla quale le altre entità di rete possono ottenerla.

Nelle reti cellulari **4G/5G** la home network corrisponde alla rete dell'operatore con cui l'utente ha sottoscritto il contratto (es. Verizon, Orange). Il database centrale che memorizza identità e servizi abilitati è l'**Home Subscriber Server (HSS)**. L'identità globale del dispositivo è codificata nella **SIM card**.

Quando il dispositivo lascia la copertura del proprio operatore entra in una **visited network** (roaming). La rete visitata ha accordi commerciali con altre reti per garantire accesso ai dispositivi in transito. Durante le operazioni in roaming il dispositivo mantiene il proprio indirizzo permanente associato alla home network, ma ottiene temporaneamente un indirizzo IP locale nel range della rete visitata, tipicamente assegnato tramite NAT.

## Routing Indiretto (Triangle Routing)

![[exam_mod2_mobile_networks_I.jpg]]

Nel **routing indiretto** (o *triangle routing*) — modalità standard per le reti 4G LTE e per Mobile IP — l'idea di base è che quando il Correspondent vuole inviare dati al dispositivo mobile:

1. Il Correspondent invia il pacchetto all'**indirizzo permanente** del mobile, che appartiene alla home network.
2. Il **Home network gateway** (o P-GW) riceve il pacchetto, lo **incapsula** in un tunnel (tipicamente usando il protocollo GTP — *GPRS Tunneling Protocol*) e lo forwarda al Visited network gateway (S-GW/P-GW locale).
3. Il **Visited network gateway** decapsula il pacchetto, applica la traduzione **NAT** (perché il dispositivo ha un IP locale) e lo consegna al dispositivo.
4. Le risposte del dispositivo possono seguire il percorso inverso oppure essere inviate direttamente al Correspondent.

Il percorso forma un **triangolo**: Correspondent → Home → Visited → Mobile, anche se Correspondent e mobile fossero fisicamente vicini. Questo è il costo dell'approccio, ma il vantaggio è notevole: ogni cambio di rete visitata è completamente **trasparente** per il Correspondent. La nuova rete si registra presso l'HSS e l'endpoint del tunnel viene aggiornato silenziosamente lato home network, senza che il Correspondent debba fare nulla.

> [!note] Continuità delle sessioni TCP
>
> Quando il dispositivo si sposta in una nuova rete visitata, possono andare persi alcuni datagrammi in transito. Tuttavia le sessioni TCP rimangono attive: dal punto di vista del corrispondente, la posizione del mobile è un dettaglio interno alla home network gestito trasparentemente dal meccanismo di tunneling.

## Routing Diretto

![[exam_mod2_mobile_networks_II.jpg]]

Nel **routing diretto**, l'alternativa al triangle routing per le reti mobili, il Correspondent non invia i pacchetti all'indirizzo permanente del mobile, ma ottiene prima il suo **care-of address** nella rete visitata. La procedura è la seguente:

1. Il Correspondent interroga l'**HSS** della home network (tramite un protocollo apposito) per ottenere l'indirizzo corrente del dispositivo mobile nella rete visitata (il care-of address).
2. Il Correspondent invia i pacchetti **direttamente** al care-of address nella visited network, bypassando la home network.
3. Il Visited network gateway riceve il pacchetto e lo consegna al dispositivo mobile.

**Vantaggi rispetto al routing indiretto:** il percorso è più corto (nessun triangolo), la latenza è ridotta, e non si sovraccarica inutilmente la home network.

**Svantaggi e problemi:** l'approccio **non è trasparente** per il Correspondent, che deve eseguire attivamente la query all'HSS. Inoltre, se il dispositivo cambia rete visitata durante una sessione attiva, il Correspondent ha interrogato l'HSS **solo all'inizio della sessione** e non conosce il nuovo care-of address. Servono quindi meccanismi aggiuntivi per aggiornare dinamicamente il flusso dati (es. forwarding dalla vecchia visited network alla nuova, o re-query dell'HSS), a differenza del routing indiretto dove è sufficiente cambiare l'endpoint del tunnel.

> [!tip] Confronto diretto vs indiretto
>
> | Aspetto | Routing Indiretto | Routing Diretto |
> |---|---|---|
> | Percorso pacchetti | Triangolo (via home) | Diretto alla visited |
> | Trasparenza per Correspondent | Sì | No (deve interrogare HSS) |
> | Gestione cambio rete | Automatica (re-tunnel) | Complessa (deve aggiornare il Correspondent) |
> | Latenza | Maggiore (percorso più lungo) | Minore |
> | Adottato in LTE/4G | Sì (per default) | Solo con ottimizzazione esplicita |

## L'Architettura Pratica: Mobilità nelle Reti 4G e Handover

![[exam_mod2_mobile_networks_III.jpg]]

Quando un dispositivo entra in una rete 4G visitata, la gestione della mobilità e la transizione tra celle sono gestite tramite un'architettura ben definita.

**Architettura del piano dati:** quando il dispositivo è associato a una BS, il traffico dati fluisce attraverso due tunnel GTP in cascata:
- **Tunnel BS ↔ S-GW**: connette la Base Station corrente al Serving Gateway. Quando il dispositivo cambia Base Station, non occorre ricreare il tunnel — è sufficiente aggiornare l'indirizzo IP dell'endpoint sul lato BS.
- **Tunnel S-GW ↔ P-GW**: connette il Serving Gateway al PDN Gateway (il gateway verso Internet nella home network), realizzando il routing indiretto.

**Procedura di handover tra Base Station:** l'handover si attiva quando il dispositivo si sposta e la qualità del segnale sulla BS corrente degrada. La procedura completa si articola in sette passi:

1. La **source BS** rileva il degrado del segnale (o il sovraccarico) e decide di avviare l'handover. Sceglie la **target BS** (sulla base delle misure di segnale riportate dal dispositivo) e le invia una **Handover Request**.
2. La **target BS** pre-alloca le risorse radio necessarie e risponde con un **Handover Request ACK** contenente i parametri di configurazione per il dispositivo.
3. La **source BS** notifica al dispositivo il cambio imminente; da questo momento il dispositivo può già trasmettere tramite la nuova BS — dal punto di vista del dispositivo l'handover è già avvenuto.
4. La **source BS** smette di trasmettere al dispositivo e inizia a **forwardare** i datagrammi in arrivo verso la target BS (che li recapita al dispositivo via radio).
5. La **target BS** informa l'**MME** (*Mobility Management Entity*) di essere la nuova BS per il dispositivo.
6. L'**MME** istruisce lo **S-GW** di aggiornare l'endpoint del tunnel dati alla nuova target BS. La source BS riceve conferma e può liberare le proprie risorse radio.
7. Il traffico fluisce ora attraverso il **nuovo tunnel** dalla target BS allo S-GW, mentre il tunnel S-GW ↔ P-GW rimane invariato.

> [!tip] Chi decide l'handover?
>
> È un punto classico da esame: sia la decisione di avviare l'handover sia la scelta della target BS spettano alla **source BS** — non all'MME. L'MME viene coinvolto solo nella fase finale per aggiornare il piano dati. Questo riflette la separazione tra control plane (MME gestisce la mobilità a livello di rete) e data plane (le BS gestiscono la qualità del segnale radio).
