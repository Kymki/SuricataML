import json
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder

# Funzione per caricare e preparare i dati
def load_and_prepare_data(file_path):
    """
    Carica il file eve.json e prepara i dati per il modello.
    Restituisce un DataFrame e la lista degli alert.
    """
    # Carica i dati da 'eve.json'
    with open(file_path, 'r') as f:
        data = [json.loads(line) for line in f]

    # Estrazione delle caratteristiche degli alert
    features = []
    for alert in data:
        feature = {
            'src_ip': alert.get('src_ip', 'unknown'),
            'dst_ip': alert.get('dst_ip', 'unknown'),
            'src_port': alert.get('src_port', 0),
            'dst_port': alert.get('dst_port', 0),
            'alert_type': alert.get('alert', {}).get('signature', 'unknown'),
            'protocol': alert.get('proto', 'unknown'),
            'timestamp': alert.get('@timestamp', 'unknown'),
            'original_alert': alert  # Salva l'intero alert per scriverlo nel nuovo file
        }
        features.append(feature)

    # Creazione di un DataFrame per una facile manipolazione
    df = pd.DataFrame(features)

    # Pre-processing: codifica delle variabili categoriche (ad esempio, IP, tipo di allarme, protocollo)
    label_encoder = LabelEncoder()
    df['src_ip'] = label_encoder.fit_transform(df['src_ip'].astype(str))
    df['dst_ip'] = label_encoder.fit_transform(df['dst_ip'].astype(str))
    df['alert_type'] = label_encoder.fit_transform(df['alert_type'].astype(str))
    df['protocol'] = label_encoder.fit_transform(df['protocol'].astype(str))

    # Sostituisci il timestamp con la differenza di tempo tra gli allarmi
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['time_diff'] = df['timestamp'].diff().fillna(pd.Timedelta(0)).dt.total_seconds()

    # Seleziona solo le colonne numeriche per il modello
    df_numeric = df[['src_ip', 'dst_ip', 'src_port', 'dst_port', 'alert_type', 'protocol', 'time_diff']]

    return df, df_numeric, features

# Funzione per rilevare anomalie
def detect_anomalies(df_numeric):
    """
    Rileva le anomalie utilizzando Isolation Forest.
    """
    model = IsolationForest(contamination=0.05)  # Stima il 5% di outlier
    df_numeric['anomaly'] = model.fit_predict(df_numeric)

    # '1' indica normale, '-1' indica anomalia
    anomalies = df_numeric[df_numeric['anomaly'] == -1]

    return anomalies

# Funzione per scrivere le anomalie nel nuovo file eve_anomalies.json
def write_anomalies_to_file(anomalies, features, output_path):
    """
    Scrive gli alert anomali nel file eve_anomalies.json.
    """
    # Filtra gli alert che sono stati identificati come anomalie
    anomaly_indexes = anomalies.index.tolist()
    anomaly_alerts = [features[i] for i in anomaly_indexes]

    # Scrivi le anomalie nel nuovo file JSON
    with open(output_path, 'w') as f:
        for alert in anomaly_alerts:
            json.dump(alert['original_alert'], f)
            f.write('\n')  # Scrivi ogni alert su una nuova riga

# Funzione principale
def main(file_path, output_path):
    """
    Carica il file JSON, rileva le anomalie e scrive gli alert anomali su un nuovo file.
    """
    # Carica e prepara i dati
    df, df_numeric, features = load_and_prepare_data(file_path)

    # Rileva anomalie (falsi positivi potenziali)
    anomalies = detect_anomalies(df_numeric)

    # Scrivi le anomalie rilevate in un nuovo file JSON
    if not anomalies.empty:
        print(f"Anomalie rilevate. Le anomalie sono state scritte nel file: {output_path}")
        write_anomalies_to_file(anomalies, features, output_path)
    else:
        print("Nessuna anomalia rilevata.")

# Esegui lo script
if __name__ == "__main__":
    input_file = "path_to_your_eve.json"  # Sostituisci con il percorso corretto del tuo file eve.json
    output_file = "eve_anomalies.json"    # Nome del file di output
    main(input_file, output_file)
