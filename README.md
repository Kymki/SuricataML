# SuricataML
Suricate powered by Machine Learning (Beta)


Rilevamento di anomalie e falsi positivi con Suricata e eve.json

Questo repository contiene uno script Python che consente di analizzare un file eve.json generato da Suricata, rilevando potenziali falsi positivi utilizzando un algoritmo di rilevamento delle anomalie basato su Isolation Forest.

Installazione

Requisiti
Python 3.x: È necessario avere Python 3 installato nel sistema. È possibile verificarlo con il comando:
python3 --version
Dipendenze: Lo script richiede alcune librerie Python. Per installarle, basta eseguire il comando:
pip install -r requirements.txt
Creazione del file requirements.txt
Se il file requirements.txt non è presente, può essere creato con il seguente contenuto:

```
pandas
scikit-learn
```

Successivamente, sarà possibile installare le dipendenze con:

```
pip install -r requirements.txt
```

Preparazione del file eve.json
Il file eve.json deve essere un output generato da Suricata in formato JSON. Questo può essere ottenuto dalla configurazione di Suricata, generalmente localizzata in /etc/suricata/suricata.yaml.

Uso

Passaggio 1: Esecuzione dello script Python
Dopo aver installato le dipendenze e preparato il file eve.json, si può eseguire lo script Python per rilevare anomalie. È necessario sostituire "path_to_your_eve.json" con il percorso effettivo del file eve.json.

Esecuzione dello script Python:
python detect_anomalies.py
Output: Lo script mostrerà gli alert che vengono considerati anomalie, i quali potrebbero essere falsi positivi. Questi alert si discostano dal comportamento normale della rete, secondo il modello di rilevamento delle anomalie.
Logstash e Elasticsearch

Se si desidera utilizzare il file eve.json con Logstash per l'ingestione in Elasticsearch e successivamente visualizzare i dati in Kibana, seguire i passaggi sottostanti.

Passaggio 2: Configurazione di Logstash
File di configurazione Logstash: È necessario creare un file di configurazione per Logstash che legga il file eve.json, lo trasformi (se necessario) e lo invii a Elasticsearch.
Un esempio di file di configurazione per Logstash (eve_logstash.conf) potrebbe essere il seguente:

```

input {
  file {
    path => "/path/to/your/eve.json"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    codec => json
  }
}

filter {
  # Aggiungere filtri o trasformazioni, se necessario
}

output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "suricata-eve-%{+YYYY.MM.dd}"
  }
}

```


path: È necessario modificare il percorso per riflettere la posizione del file eve.json.
sincedb_path: Se si intende fare una lettura continua del file, è possibile specificare una posizione per evitare che Logstash legga gli stessi dati più volte. Impostato su /dev/null per una lettura una tantum.
codec => json: Assicura che Logstash legga correttamente i dati JSON.
Avvio di Logstash:
Dopo aver creato il file di configurazione, Logstash può essere avviato con il seguente comando:

```
bin/logstash -f eve_logstash.conf
```

Questo comando inizia a leggere il file eve.json e inviarlo a Elasticsearch, dove i dati verranno indicizzati come suricata-eve-*, pronti per essere analizzati e visualizzati in Kibana.
Esplorazione dei dati su Kibana

Dopo che i dati sono stati inviati a Elasticsearch tramite Logstash, è possibile aprire Kibana (assicurandosi che sia in esecuzione su 

```
localhost:5601 
```

o su un altro host configurato).
Accedere alla sezione "Discover" di Kibana e cercare l'indice suricata-eve-*.
A questo punto, si potranno esplorare gli alert generati da Suricata, creare dashboard, visualizzazioni, ed effettuare un'analisi approfondita del traffico di rete.