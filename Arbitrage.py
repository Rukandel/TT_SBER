import Binance
import Uniswap


# Предположим, что у нас есть данные с Binance и Uniswap
df_binance = df_3h
df_uniswap = df_uniswap_3h

# Сравниваем цены
df_combined = pd.merge(df_binance, df_uniswap, left_index=True, right_index=True, suffixes=('_binance', '_uniswap'))

# Рассчитываем арбитражные возможности
df_combined['price_diff'] = df_combined['Close_uniswap'] - df_combined['Close_binance']
df_combined['arbitrage_opportunity'] = df_combined['price_diff'] > (df_combined['Close_binance'] * 0.001 + df_combined['Close_uniswap'] * 0.0012 + 5)  # Комиссии и газ

# Выводим результаты
print(df_combined[['Close_binance', 'Close_uniswap', 'price_diff', 'arbitrage_opportunity']])

# Заключение
if df_combined['arbitrage_opportunity'].any():
    print("Арбитражные возможности существуют.")
else:
    print("Арбитражные возможности отсутствуют.")