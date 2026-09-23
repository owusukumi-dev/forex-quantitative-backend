# Secure Market Sentinel: Macro Surveillance & Quantitative Engine

A quantitative trading project combining **Python, Node.js, Express, MySQL, and a web dashboard** to collect macroeconomic events, generate technical signals, and backtest trading strategies across Gold and Forex markets.

---

## Architecture

```text
Economic Calendar
       ↓
Python Ingestion
       ↓
Macro Event Filtering
       ↓
Node.js / Express
       ↓
Web Dashboard
       ↓
MySQL Signal Storage
       ↓
Quantitative Analysis & Backtesting
```

### Main Components

* `main.py` — Economic calendar scraper and macro-event filter
* `server.js` — Express server and Python process bridge
* `homepage.html` — Market dashboard and risk calculator
* `main2.py` — Gold analysis, SMA signals, and MySQL storage
* `RSI.py` — SMA + RSI strategy
* `backtest.py` — 15-minute backtesting and synthetic price generation

---

## Features

* Economic event scraping with `curl_cffi`
* Chrome TLS/browser impersonation
* Python ↔ Node.js process communication
* REST API for market signals
* Live macroeconomic dashboard
* Position sizing calculator
* MySQL signal storage
* SMA and RSI strategies
* 15-minute OHLCV backtesting
* Synthetic price generation using geometric random walks
* Spread and execution-cost modelling
* Drawdown tracking

---

## Strategy & Mathematics

### Position Sizing

$$
Lot\ Size =
\frac{Account\ Balance \times Risk\ Fraction}
{|Entry - Stop\ Loss|}
$$

### RSI

$$
RS =
\frac{EMA_{14}(Up\ Moves)}
{EMA_{14}(Down\ Moves)}
$$

$$
RSI =
100-\frac{100}{1+RS}
$$

### Synthetic Price Generation

$$
S_t =
S_0\prod_{i=1}^{t}(1+r_i)
$$

where

$$
r_i \sim \mathcal{N}(\mu,\sigma^2)
$$

---

## Why I Built This

I'm a trader, and I kept seeing bots generate signals and execute strategies.

So I decided to build one myself.

It started with the RSI and moving-average strategies. Then I started asking where the signals should actually come from. Markets don't move in isolation, and macroeconomic events can change the environment around a trade.

That pushed the project beyond a strategy script into a full pipeline: **collect the macro data, process it, combine it with market signals, store it, and put it on a dashboard.**

---

## What Surprised Me

**Scraping is harder than it looks.**

I initially thought it was basically:

> fetch page → parse HTML → done.

Then I started getting blocked, redirected, and served content that wasn't what I expected.

That was my first real look at the cat-and-mouse game behind modern web scraping.

---

## The Hardest Part

Finding a scraper that actually worked.

I went through several libraries before landing on `curl_cffi`.

The important part wasn't just finding another library. I had to understand **why** the previous approaches were failing in the first place.

---

## What I Learned

I learned a lot about what sits between a simple request and the data you actually receive.

I also gained a much better understanding of how the different pieces of a real application fit together:

**Python → Node.js → API → Database → Frontend**

And probably the most memorable lesson was CAPTCHA.

Before this project, it was just something annoying that appeared when I was browsing.

Then I became the guy trying to automate around one.

That gave me a completely different perspective on why those systems exist.

---

## Directory Structure

```text
quantEngine/
├── python backend/
│   ├── main.py
│   ├── main2.py
│   ├── backtest.py
│   ├── RSI.py
│   └── market_signals.json
├── server/
│   └── server.js
├── public/
│   ├── homepage.html
│   └── style.css
├── package.json
└── README.md
```

---

## Setup

### Python

```bash
pip install pandas numpy yfinance curl_cffi matplotlib mysql-connector-python
```

### Node.js

```bash
npm install
npm start
```

The dashboard runs at:

```text
http://localhost:5000
```

### Backtesting

```bash
cd "python backend"
python backtest.py
```

---

## Project Status

An educational quantitative systems project exploring **market data, macroeconomic events, technical strategies, backtesting, and full-stack data pipelines**.
