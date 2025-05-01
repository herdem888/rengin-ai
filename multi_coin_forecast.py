
import numpy as np
import pandas as pd
from datetime import datetime
from binance.client import Client
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
from xgboost import XGBRegressor

def fetch_data(symbol, interval=Client.KLINE_INTERVAL_4HOUR, limit=300):
    client = Client()
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['close'] = df['close'].astype(float)
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('date', inplace=True)
    return df[['close']]

def prepare_lstm_data(data):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(data)
    X, y = [], []
    for i in range(60, len(scaled)):
        X.append(scaled[i-60:i])
        y.append(scaled[i])
    return np.array(X), np.array(y), scaler

def train_lstm(X, y):
    model = Sequential()
    model.add(LSTM(64, return_sequences=True, input_shape=(60, 1)))
    model.add(LSTM(64))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=4, batch_size=32, verbose=0)
    return model

def train_xgboost(df):
    df['target'] = df['close'].shift(-1)
    df.dropna(inplace=True)
    for i in range(1, 6):
        df[f'lag_{i}'] = df['close'].shift(i)
    df.dropna(inplace=True)
    X = df[[f'lag_{i}' for i in range(1, 6)]]
    y = df['target']
    model = XGBRegressor(n_estimators=100)
    model.fit(X, y)
    return model

def predict_coin(symbol):
    try:
        df = fetch_data(symbol)
        X, y, scaler = prepare_lstm_data(df)
        lstm = train_lstm(X, y)
        xgb = train_xgboost(df)

        input_lstm = scaler.transform(df[-60:])
        input_lstm = input_lstm.reshape(1, 60, 1)
        pred_lstm = lstm.predict(input_lstm, verbose=0)[0][0]
        lstm_price = scaler.inverse_transform([[pred_lstm]])[0][0]

        last_row = df.iloc[-1]
        x_input = df['close'].shift(1).dropna().tail(5).values.reshape(1, -1)
        pred_xgb = xgb.predict(x_input)[0]

        return {
            "symbol": symbol,
            "current_price": df['close'].iloc[-1],
            "lstm_pred": lstm_price,
            "xgb_pred": pred_xgb
        }

    except Exception as e:
        return {"symbol": symbol, "error": str(e)}
