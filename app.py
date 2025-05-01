
import streamlit as st
import json
import pandas as pd
from multi_coin_forecast import predict_coin
from gpt_utils import explain_with_gpt
from telegram_utils import send_telegram_message
from binance_utils import create_client, place_order

st.set_page_config(page_title="RENGÎN.AI Panel", layout="wide")
st.title("🤖 RENGÎN.AI | Çoklu Coin AI İşlem Paneli")

# Kullanıcı Ayarları
st.sidebar.title("🔐 Kullanıcı Ayarları")
api_key = st.sidebar.text_input("Binance API Key", type="password")
api_secret = st.sidebar.text_input("Binance API Secret", type="password")
telegram_token = st.sidebar.text_input("Telegram Bot Token", type="password")
chat_id = st.sidebar.text_input("Telegram Chat ID")

if st.sidebar.button("💾 Ayarları Kaydet"):
    config = {
        "binance": {"api_key": api_key, "api_secret": api_secret},
        "telegram": {"bot_token": telegram_token, "chat_id": chat_id}
    }
    with open("user_config.json", "w") as f:
        json.dump(config, f, indent=4)
    st.sidebar.success("✅ Ayarlar kaydedildi!")

if st.sidebar.button("📩 Telegram Test Mesajı"):
    if telegram_token and chat_id:
        result = send_telegram_message(telegram_token, chat_id, "✅ RENGÎN.AI test mesajı başarılı!")
        st.sidebar.success("📨 Gönderildi" if result else "❌ Hata")
    else:
        st.sidebar.warning("Telegram bilgilerini gir!")

if st.sidebar.button("📦 Binance Test Emri"):
    if api_key and api_secret:
        client = create_client(api_key, api_secret)
        result = place_order(client, "BTCUSDT", "BUY", 0.001, 10000)
        st.sidebar.success(result)
    else:
        st.sidebar.warning("Binance bilgilerini gir!")

# Coin seçimi
with open("coin_list.json") as f:
    all_coins = json.load(f)["available"]

selected_coins = st.multiselect("🔍 Analiz Edilecek Coinler:", all_coins, default=all_coins[:3])

if st.button("🚀 Tahmini Başlat"):
    st.info("Tahminler hesaplanıyor...")
    results = []
    for coin in selected_coins:
        results.append(predict_coin(coin))
    valid = [r for r in results if "error" not in r]
    if valid:
        df = pd.DataFrame(valid)
        df["Kazanç (%)"] = ((df["xgb_pred"] - df["current_price"]) / df["current_price"]) * 100
        df["GPT Açıklama"] = [
            explain_with_gpt(r["symbol"], r["current_price"], r["lstm_pred"], r["xgb_pred"]) for r in valid
        ]
        df = df[["symbol", "current_price", "lstm_pred", "xgb_pred", "Kazanç (%)", "GPT Açıklama"]]
        df.columns = ["Coin", "Güncel Fiyat", "LSTM", "XGBoost", "Kazanç (%)", "GPT Açıklama"]
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Geçerli veri yok.")
