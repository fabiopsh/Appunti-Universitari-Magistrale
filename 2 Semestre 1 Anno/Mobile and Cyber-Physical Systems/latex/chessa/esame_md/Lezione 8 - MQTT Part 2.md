# MQTT: Meccanismi di Affidabilità

Questa sezione approfondisce i meccanismi che rendono il protocollo MQTT robusto in contesti IoT: sessioni persistenti, messaggi trattenuti, testamento e keep alive.

## Meccanismi di Affidabilità

### Sessioni Persistenti

Quando un dispositivo IoT si disconnette (per sleep, copertura persa, reset), rischia di perdere le sottoscrizioni attive e i messaggi pubblicati durante l'assenza. Le **persistent session** risolvono questo problema.

> [!definition] Sessione Persistente (*Persistent Session*)
>
> Meccanismo attivato impostando `cleanSession = false` nel CONNECT. Il broker conserva per quel `clientId`:
> - Tutte le sottoscrizioni attive
> - I messaggi non consegnati con QoS 1 o 2
> - I messaggi in attesa di completamento del flusso QoS 2

Alla riconnessione con lo stesso `clientId`, la sessione viene ripristinata automaticamente. Il broker segnala la presenza di una sessione precedente tramite il flag *Session Present* nel CONNACK.

### Messaggi Trattenuti (*Retained Messages*)

Nel pub/sub classico, un nuovo subscriber non sa quando arriverà il primo messaggio. I **retained message** risolvono questo: un messaggio pubblicato con `retainFlag = true` viene conservato dal broker (uno per topic). 

Ogni nuovo subscriber riceve immediatamente l'ultimo messaggio trattenuto al momento dell'iscrizione, senza aspettare la prossima pubblicazione fisiologica.

> [!example] Esempio: stato di un dispositivo domestico
>
> Un dispositivo pubblica il proprio stato su `home/devices/device1/status` con payload `"ON"` e `retainFlag = true`. Un nuovo client che si iscrive riceve immediatamente `"ON"`.

### Last Will & Testament

Quando un dispositivo si disconnette *normalmente* (DISCONNECT), può notificare gli altri esplicitamente. Per le **disconnessioni anomale** (crash, timeout, interruzione di rete) non esiste tale possibilità.

> [!definition] Last Will & Testament
>
> Messaggio pre-configurato consegnato al broker al momento del CONNECT. Se il broker rileva una disconnessione anomala, pubblica quel messaggio automaticamente. Il testamento ha topic, payload, QoS e retained flag propri.

Il broker invia il testamento in quattro circostanze: 
- Errore di I/O sulla connessione.
- Mancato invio di PINGREQ entro il keep alive.
- Chiusura brusca TCP senza DISCONNECT.
- Chiusura forzata per errore di protocollo.

Se il client si disconnette con DISCONNECT regolare, il testamento viene scartato.

> [!tip] Pattern potente
>
> Un dispositivo pubblica il proprio stato (`"ON"`) come retained message. Configura anche un testamento con payload `"OFF"` e retain flag attivo sullo stesso topic. Se va in crash, il broker pubblica automaticamente `"OFF"` come retained message — tutti i client (connessi e futuri) vedono lo stato corretto.

### Keep Alive

TCP può mantenere una connessione apparentemente attiva anche quando il peer è irraggiungibile. Il **Keep Alive** risolve questo problema: il client dichiara un intervallo (campo a 16 bit nel CONNECT) entro cui si impegna a inviare almeno un pacchetto. 

Se non lo fa, il broker chiude la connessione e invia il testamento. Il client invia **PINGREQ** se non ha altro traffico; il broker risponde con **PINGRESP**. Il valore `0` disabilita il meccanismo.
