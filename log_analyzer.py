
import pandas as pd
import matplotlib.pyplot as plt
import os

def analyze_logs(log_file="signals_log.csv"):
    if not os.path.exists(log_file):
        print("Log dosyası bulunamadı.")
        return

    df = pd.read_csv(log_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['gain'] = ((df['sell_price'] - df['buy_price']) / df['buy_price']) * 100

    # Günlük bazda kazançları hesapla
    df['date'] = df['timestamp'].dt.date
    daily_gain = df.groupby('date')['gain'].sum()

    # Grafik çiz
    plt.figure(figsize=(10,5))
    daily_gain.plot(kind='bar', title="📊 Günlük Toplam Kâr/Zarar (%)")
    plt.ylabel("%")
    plt.xlabel("Tarih")
    plt.tight_layout()
    plt.savefig("daily_gain_chart.png")
    print("✅ Grafik oluşturuldu: daily_gain_chart.png")
