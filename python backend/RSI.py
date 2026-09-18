import pandas as pd
pd.set_option('display.max_columns',None)
pd.set_option('display.max_rows',None)
pd.set_option('display.width',None)

def calculate_rsi(data,period=14):
    data=pd.Series(data)
    delta=data.diff()
    gain=(delta.where(delta>0,0)).rolling(window=2).mean()
    loss=(-delta.where(delta<0,0)).rolling(window=2).mean()
    rsi = gain / loss
    rsi = 100 - (100 / (1 + rsi))
    return rsi

df=pd.read_csv("Forex2.csv")
df['timestamp']=pd.to_datetime(df['timestamp'])
df.set_index('timestamp',inplace=True)
df['SMA5']=df['close'].rolling(window=5).mean()
df['SMA10']=df['close'].rolling(window=10).mean()
df['RSI']=calculate_rsi(df['close'],period=14)
df['Signal']="Wait"
df.loc[(df['SMA5'] > df['SMA10']) & df['RSI']<30,'Signal']="Buy"
df.loc[df['RSI']>70,'Signal']="Sell"
print(df[['currency_pair','Signal']])
