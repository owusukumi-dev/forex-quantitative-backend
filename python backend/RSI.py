import pandas as pd
import yfinance as yf  

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)

def calculate_rsi(data, period=14):
    data = pd.Series(data)
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

ticker = "EURUSD=X"
df = yf.download(ticker, period="3mo", interval="1d")

df.reset_index(inplace=True)
df.rename(columns={'Date': 'timestamp', 'Close': 'close', 'Datetime': 'timestamp'}, inplace=True)
df['currency_pair'] = ticker

df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

df['SMA5'] = df['close'].rolling(window=5).mean()
df['SMA10'] = df['close'].rolling(window=10).mean()
df['RSI'] = calculate_rsi(df['close'], period=14)
df['Signal'] = "Wait"

df.loc[(df['SMA5'] > df['SMA10']) & (df['RSI'] < 30), 'Signal'] = "Buy"
df.loc[df['RSI'] > 70, 'Signal'] = "Sell"

print(df[['currency_pair', 'close', 'RSI', 'Signal']].tail(50))