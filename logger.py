
import csv
from datetime import datetime

def log_signal(symbol, buy_price, sell_price):
    with open("signals_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), symbol, buy_price, sell_price])
