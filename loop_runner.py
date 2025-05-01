import time
import json
from datetime import datetime
from multi_coin_forecast import predict_coin
from gpt_utils import explain_with_gpt
from telegram_utils import send_telegram_message
from binance_utils import create_client, place_order

# Kullanıcı ayarlarını yükle
with open("user_config.json") as f:
    config = json.load(f)

telegram_token = config["telegram"]["bot_token"]
chat_id = config["telegram"]["chat_id"]

with open("coin_list.json") as f:
    coins = json.load(f)["available"]

def run_forecast_loop():
    while True:
        print(f"🔁 Tahmin başlatılıyor... {datetime.now()}")
        
        for coin in coins:
            result = predict_coin(coin)
            if "error" not in result:
                gain = ((result["xgb_pred"] - result["current_price"]) / result["current_price"]) * 100
                if gain >= 4:  # %4 üzeri fırsatlar için
                    explanation = explain_with_gpt(
                        result["symbol"],
                        result["current_price"],
                        result["lstm_pred"],
                        result["xgb_pred"]
                    )
                    message = (
                        f"📈 RENGÎN.AI Sinyali ({result['symbol']})\n"
                        f"Anlık: {result['current_price']:.2f} USDT\n"
                        f"LSTM: {result['lstm_pred']:.2f} | XGB: {result['xgb_pred']:.2f}\n"
                        f"🎯 Beklenen Kazanç: %{gain:.2f}\n"
                        f"🧠 Açıklama: {explanation}"
                    )
                    send_telegram_message(telegram_token, chat_id, message)
                    print("📤 Telegram gönderildi:", result["symbol"])

        print("⏱️ 1 saat bekleniyor...\n")
        time.sleep(3600)  # 1 saat bekle

if __name__ == "__main__":
    run_forecast_loop()
