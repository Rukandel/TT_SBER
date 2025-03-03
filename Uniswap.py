import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta


# Функция для запроса данных из The Graph
def fetch_swap_data(pool_id, start_timestamp, end_timestamp):
    query = """
    {
      swaps(
        first: 1000,
        where: {
          pool: "%s",
          timestamp_gte: %d,
          timestamp_lte: %d
        },
        orderBy: timestamp,
        orderDirection: asc
      ) {
        timestamp
        amount0
        amount1
      }
    }
    """ % (pool_id, start_timestamp, end_timestamp)

    try:
        response = requests.post('https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3', json={'query': query})
        response.raise_for_status()  # Проверка на ошибки HTTP
        data = response.json()

        if 'errors' in data:
            print("GraphQL Error:", data['errors'])
            return []

        if 'data' not in data or 'swaps' not in data['data']:
            print("No data found for pool:", pool_id)
            return []

        return data['data']['swaps']
    except Exception as e:
        print(f"Error fetching data for pool {pool_id}: {e}")
        return []


# Функция для преобразования данных в DataFrame
def prepare_data(swaps):
    data = []
    for swap in swaps:
        timestamp = int(swap['timestamp'])
        amount0 = float(swap['amount0'])
        amount1 = float(swap['amount1'])
        price = abs(amount1 / amount0)  # Цена WETH в USDT
        data.append([timestamp, price])

    df = pd.DataFrame(data, columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    return df


# Функция для построения свечного графика
def plot_candlestick(df):
    df.set_index('timestamp', inplace=True)
    df_resampled = df['price'].resample('3T').ohlc()

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(df_resampled.index, df_resampled['close'], label='Цена WETH/USDT', color='blue')
    ax.set_title('3-х часовой свечной график цены WETH/USDT')
    ax.set_xlabel('Время')
    ax.set_ylabel('Цена (USDT)')
    ax.legend()
    ax.grid(True)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# Основная функция
def main():
    pools = {
        'v3_0x4e68Ccd3E89f51C3074ca5072bbAC773960dFa36': '0x4e68Ccd3E89f51C3074ca5072bbAC773960dFa36',
        'v3_0x11b815efB8f581194ae79006d24E0d814B7697F6': '0x11b815efB8f581194ae79006d24E0d814B7697F6',
        'v3_0xc7bBeC68d12a0d1830360F8Ec58fA599bA1b0e9b': '0xc7bBeC68d12a0d1830360F8Ec58fA599bA1b0e9b',
        'v2_0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852': '0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852'
    }

    start_timestamp = int(datetime(2023, 11, 27).timestamp())
    end_timestamp = int((datetime(2023, 11, 27) + timedelta(days=1)).timestamp())

    all_data = pd.DataFrame()

    for pool_name, pool_id in pools.items():
        print(f"Fetching data for pool: {pool_name}")
        swaps = fetch_swap_data(pool_id, start_timestamp, end_timestamp)
        if swaps:
            df = prepare_data(swaps)
            df['pool'] = pool_name
            all_data = pd.concat([all_data, df])

    if not all_data.empty:
        plot_candlestick(all_data)
    else:
        print("No data available to plot.")


if __name__ == "__main__":
    main()