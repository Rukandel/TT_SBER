import requests
import pandas as pd
import mplfinance as mpf
from datetime import datetime, timedelta

# Получаем данные за 24 часа с интервалом 1 минута
symbol = "ETHUSDT"
interval = "1m"  # 1 минута
start_date = "2024-11-27"
end_date = "2024-11-28"
url = f"https://api.binance.com/api/v3/klines"

# Преобразуем дату в timestamp
start_time = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)  # в миллисекундах
end_time = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)  # в миллисекундах

params = {
    "symbol": symbol,
    "interval": interval,
    "startTime": start_time,
    "endTime": end_time,
}

response = requests.get(url, params=params)

# Проверка на успешность запроса
if response.status_code == 200:
    data = response.json()
else:
    print("Ошибка запроса:", response.status_code)
    data = []

# Преобразуем полученные данные в DataFrame
df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"])

# Преобразуем timestamp в дату и время
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Преобразуем данные в формат чисел
df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].apply(pd.to_numeric)

# Преобразуем данные с интервалом 1 минута в данные с интервалом 3 часа
df_3h = df.resample('3h', on='timestamp').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
}).dropna()

# Строим свечной график для интервала 3 часа
mpf.plot(df_3h, type='candle', style='charles', title=f'{symbol} 3-Hour Candlestick Chart', ylabel='Price (USDT)', volume=True)

# Преобразуем данные с интервалом 1 минута в данные с интервалом 5 часов
df_5h = df.resample('5H', on='timestamp').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
}).dropna()

# Строим свечной график для интервала 5 часов
mpf.plot(df_5h, type='candle', style='charles', title=f'{symbol} 5-Hour Candlestick Chart', ylabel='Price (USDT)', volume=True)
