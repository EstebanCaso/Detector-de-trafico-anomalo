import pandas as pd
import numpy as np
from scapy.all import sniff, IP, TCP, UDP
from sklearn.ensemble import IsolationForest
from datetime import datetime
import warnings
import os

warnings.filterwarnings("ignore")

def extract_features(pkt):
    """Extrae características relevantes de un paquete."""
    if IP in pkt:
        src = pkt[IP].src
        dst = pkt[IP].dst
        length = len(pkt)
        proto = pkt[IP].proto
        sport = pkt[TCP].sport if TCP in pkt else (pkt[UDP].sport if UDP in pkt else 0)
        dport = pkt[TCP].dport if TCP in pkt else (pkt[UDP].dport if UDP in pkt else 0)
        timestamp = datetime.now().strftime("%H:%M:%S")
        return [timestamp, src, dst, sport, dport, length, proto]
    return None

def analyze_live_traffic(packet_limit=200):
    """Captura tráfico en vivo y analiza anomalías."""
    print(f"\nCapturando {packet_limit} paquetes... (pulsa Ctrl+C para detener)\n")

    packets = sniff(count=packet_limit)
    print(f"\nCapturados {len(packets)} paquetes.")

    data = []
    for pkt in packets:
        feat = extract_features(pkt)
        if feat:
            data.append(feat)

    df = pd.DataFrame(data, columns=["time", "src", "dst", "sport", "dport", "length", "proto"])

    if df.empty:
        print("No se capturó tráfico IP.")
        return

    # Modelo simple de detección
    numeric_df = df[["sport", "dport", "length", "proto"]]
    model = IsolationForest(contamination=0.05, random_state=42)
    df["anomaly"] = model.fit_predict(numeric_df)

    anomalous = df[df["anomaly"] == -1]

    print(f"\nAnomalías detectadas: {len(anomalous)}\n")

    if len(anomalous) > 0:
        print(anomalous[["time", "src", "dst", "sport", "dport", "length"]].head(20).to_string(index=False))
        # Guarda reporte
        filename = f"anomaly_report_{datetime.now().strftime('%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"\nReporte guardado en: {os.path.abspath(filename)}")
    else:
        print("No se detectaron anomalías evidentes.")

if __name__ == "__main__":
    try:
        analyze_live_traffic(packet_limit=300)
    except KeyboardInterrupt:
        print("\nCaptura interrumpida por el usuario.")
