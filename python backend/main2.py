import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mysql.connector


ticker="GC=F"

market_data=yf.download(ticker,period="5y",interval="1d")
#print(market_data)
market_data['SMA_50']=market_data['Close'].rolling(window=50).mean()
market_data['SMA_200']=market_data['Close'].rolling(window=200).mean()
market_data['SMA_100']=market_data['Close'].rolling(window=100).mean()

#plt.figure(figsize=(10,5))

#plt.plot(market_data['Close'], label='Raw Gold Price', color='green', alpha=0.5)
#plt.plot(market_data['SMA_50'], label='50-Day Momentum (Short)', color='blue')
#plt.plot(market_data['SMA_200'], label='200-Day Macro Trend (Long)', color='red')
#market_data['SMA_100'].plot(label='100-Day Momentum (Mid)',color='yellow')

#Visual display
#plt.title(f"Gold Analysis")
#plt.ylabel("Price (USD)")
#plt.legend()
#plt.grid(True)

#plt.show()
market_data['Position']=np.where(market_data['SMA_50']>market_data['SMA_200'],1,0)
market_data['Signal']=market_data['Position'].diff()
trigger_trade=market_data[market_data['Signal']!=0].dropna()
print(trigger_trade[['Close','SMA_50','SMA_200','Signal']])

#This changes the whatever is in the index column into a real column
trigger_trade=trigger_trade.reset_index()

#For each first element in each of the columns in trigger_trade,select and store
trigger_trade.columns=[col[0] for col in trigger_trade.columns]

#rename , the first column of trigger trade with Date
trigger_trade.rename(columns={trigger_trade.columns[0]:'Date'}, inplace='True')

trigger_trade.to_json('market_signals.json', orient='records', date_format='iso')

db_config={
    'user': 'root',
    'password':'',
    'host':'localhost',
    'database':'macro_trading'
}


def save_to_db(data, ticker):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    query = """
    INSERT INTO market_signals (ticker, trade_date, close_price, sma_50, sma_200, signal_type)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    for _, row in data.iterrows():
        cursor.execute(query, (ticker, row['Date'], row['Close'], row['SMA_50'], row['SMA_200'], row['Signal']))

    conn.commit()
    cursor.close()
    conn.close()
    print("Data successfully vaulted in MySQL.")


# Trigger the save
save_to_db(trigger_trade, "GC=F")