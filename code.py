import json
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder

# Funzione per caricare e preparare i dati
def load_and_prepare_data(file_path):
    # Carica i dati da 'eve.json'
    with open(file_path, 'r') as f:
        data = [json.loads(line) for line in f]
    
    # Estrazione delle caratteristiche dagli alert
    features = []
    for alert in data:
        feature = {
            'src_ip': alert.get('src_ip'),
            'dst_ip': alert.get('dst_ip'),
            'src_port': alert.get('src_port'),
            'dst_port': alert.get('dst_port'),
            'alert_type': alert.get('alert', {}).get('signature'),
            'protocol': alert.get('proto'),
            'timestamp': alert.get('@timestamp')
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
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['time_diff'] = df['timestamp'].diff().fillna(pd.Timedelta(0)).dt.total_seconds()

    # Seleziona solo le colonne numeriche per il modello
    df_numeric = df[['src_ip', 'dst_ip', 'src_port', 'dst_port', 'alert_type', 'protocol', 'time_diff']]

    return df, df_numeric

# Funzione per rilevare anomalie
def detect_anomalies(df_numeric):
    # Creazione del modello di rilevamento delle anomalie (Isolation Forest)
    model = IsolationForest(contamination=0.05)  # Settaggio della percentuale di outlier stimata
    df_numeric['anomaly'] = model.fit_predict(df_numeric)

    # '1' indica una normale, '-1' indica un'anomalia
    anomalies = df_numeric[df_numeric['anomaly'] == -1]

    return anomalies

# Funzione principale
def main(file_path):
    # Carica e prepara i dati
    df, df_numeric = load_and_prepare_data(file_path)

    # Rileva anomalie (falsi positivi potenziali)
    anomalies = detect_anomalies(df_numeric)

    # Stampa gli alert considerati anomalie
    if not anomalies.empty:
        print("Allarmi anomali (potenziali falsi positivi):")
        print(anomalies)
    else:
        print("Nessuna anomalia rilevata.")

# Inserisci il percorso del file 'eve.json' qui
if __name__ == "__main__":
    file_path = "path_to_your_eve.json"  # Sostituisci con il percorso corretto del tuo file eve.json
    main(file_path)
