
from binance.client import Client

def create_client(api_key, api_secret):
    return Client(api_key, api_secret)

def place_order(client, symbol, side, quantity, price):
    try:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce=Client.TIME_IN_FORCE_GTC,
            quantity=quantity,
            price=str(price)
        )
        return f"✅ Emir ID: {order['orderId']}"
    except Exception as e:
        return f"❌ Emir hatası: {e}"
