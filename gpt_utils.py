
import openai
import os
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def explain_with_gpt(symbol, current_price, lstm_pred, xgb_pred):
    prompt = f"""
Coin: {symbol}
Güncel fiyat: {current_price:.2f} USDT
LSTM Tahmini: {lstm_pred:.2f} USDT
XGBoost Tahmini: {xgb_pred:.2f} USDT

Bu tahminlere göre sinyalin neden verildiğini kısa, teknik ve doğal bir dille açıkla:
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"GPT açıklama hatası: {e}"
