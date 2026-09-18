import pandas as pd
import numpy as np

def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = delta.where(delta > 0, 0.0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=period).mean()
    rs = gain / loss
    return 100.0 - (100.0 / (1.0 + rs))

def run_backtest(csv_path="NewForexData.csv"):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Data file {csv_path} not found. Ensure dataset is present in working directory.")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)

    ohlc = {
        'open': df['open'].resample('15min').first(),
        'high': df['high'].resample('15min').max(),
        'low': df['low'].resample('15min').min(),
        'close': df['close'].resample('15min').last(),
        'volume': df['volume'].resample('15min').sum()
    }
    strat_df = pd.DataFrame(ohlc).dropna()

    strat_df['SMA20'] = strat_df['close'].rolling(window=20).mean()
    strat_df['SMA5'] = strat_df['close'].rolling(window=5).mean()
    strat_df['RSI'] = calculate_rsi(strat_df['close'], period=14)

    strat_df['Signal'] = 'HOLD'
    strat_df.loc[(strat_df['SMA5'] > strat_df['SMA20']) & (strat_df['RSI'] < 30), 'Signal'] = 'BUY'
    strat_df.loc[(strat_df['SMA5'] < strat_df['SMA20']) & (strat_df['RSI'] > 70), 'Signal'] = 'SELL'

    position_size = 0.1
    spread_pips = 1.0
    pip_value = 10.0
    spread_cost = spread_pips * pip_value
    in_position = False
    entry_price = 0.0
    equity = 1000.0

    trades = []

    for i in range(len(strat_df)):
        signal = strat_df['Signal'].iloc[i]
        close = strat_df['close'].iloc[i]
        timestamp = strat_df.index[i]

        if signal == 'BUY' and not in_position:
            entry_price = close + (spread_pips / 10000.0)
            in_position = True
            trades.append({
                'entry_time': timestamp,
                'entry_price': entry_price,
                'action': 'BUY'
            })

        elif signal == 'SELL' and in_position:
            exit_price = close - (spread_pips / 10000.0)
            profit = (exit_price - entry_price) * 10000.0 * pip_value - spread_cost
            equity += profit
            in_position = False
            trades[-1].update({
                'exit_time': timestamp,
                'exit_price': exit_price,
                'profit': profit,
                'net_equity': equity
            })

    completed = [t for t in trades if 'profit' in t]
    if completed:
        wins = [t for t in completed if t['profit'] > 0]
        win_rate = (len(wins) / len(completed)) * 100.0
        total_pnl = sum(t['profit'] for t in completed)
        print(f"Backtest Completed: {len(completed)} trades | Win Rate: {win_rate:.2f}% | Total PnL: ${total_pnl:.2f}")
    else:
        print("Backtest executed: No completed round-trip trades generated.")

if __name__ == '__main__':
    run_backtest()