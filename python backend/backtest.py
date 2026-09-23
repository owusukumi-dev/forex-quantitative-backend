import pandas as pd
import numpy as np


def calculate_rsi(data: pd.Series, period: int = 14, wilder: bool = True) -> pd.Series:
    delta = data.diff()
    up = delta.clip(lower=0.0)
    down = -delta.clip(upper=0.0)

    if wilder:
        avg_gain = up.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        avg_loss = down.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    else:
        avg_gain = up.rolling(window=period).mean()
        avg_loss = down.rolling(window=period).mean()

    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    rsi = rsi.where(avg_loss != 0.0, 100.0)
    rsi = rsi.where((avg_gain != 0.0) | (avg_loss != 0.0), 50.0)
    return rsi


def generate_mock_forex_data(periods=5000):
    """Generates synthetic 15-minute EUR/USD OHLCV data."""
    rng = pd.date_range(end=pd.Timestamp.now(), periods=periods, freq='15min')
    np.random.seed(42)

    returns = np.random.normal(0.00001, 0.001, periods)
    price_series = 1.0800 * np.cumprod(1 + returns)

    return pd.DataFrame({
        'open': price_series * (1 - np.random.uniform(0, 0.0005, periods)),
        'high': price_series * (1 + np.random.uniform(0, 0.001, periods)),
        'low': price_series * (1 - np.random.uniform(0, 0.001, periods)),
        'close': price_series,
        'volume': np.random.randint(100, 5000, periods)
    }, index=rng)


def run_backtest(csv_path="NewForexData.csv"):
    try:
        df = pd.read_csv(csv_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        strat_df = pd.DataFrame({
            'open': df['open'].resample('15min').first(),
            'high': df['high'].resample('15min').max(),
            'low': df['low'].resample('15min').min(),
            'close': df['close'].resample('15min').last(),
            'volume': df['volume'].resample('15min').sum()
        }).dropna()
    except FileNotFoundError:
        print(f"[Notice] '{csv_path}' not found. Generating 5000-period market sample for execution...")
        strat_df = generate_mock_forex_data(5000)

    strat_df['SMA20'] = strat_df['close'].rolling(window=20).mean()
    strat_df['SMA5'] = strat_df['close'].rolling(window=5).mean()
    strat_df['RSI'] = calculate_rsi(strat_df['close'], period=14)


    strat_df['Signal'] = 'HOLD'

    strat_df.loc[(strat_df['SMA5'] > strat_df['SMA20']) & (strat_df['RSI'] < 40), 'Signal'] = 'BUY'

    strat_df.loc[strat_df['RSI'] > 70, 'Signal'] = 'SELL'

    position_size = 0.1
    spread_pips = 1.0
    pip_value = 10.0 * position_size
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


    if in_position:
        exit_price = strat_df['close'].iloc[-1] - (spread_pips / 10000.0)
        profit = (exit_price - entry_price) * 10000.0 * pip_value - spread_cost
        equity += profit
        trades[-1].update({
            'exit_time': strat_df.index[-1],
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
