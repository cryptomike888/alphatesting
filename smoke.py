import backtrader as bt
import yfinance as yf

class SmaCross(bt.Strategy):
    params = dict(fast=10, slow=30)

    def __init__(self):
        sma_f = bt.ind.SMA(period=self.p.fast)
        sma_s = bt.ind.SMA(period=self.p.slow)
        self.cross = bt.ind.CrossOver(sma_f, sma_s)

    def next(self):
        if not self.position and self.cross > 0:
            self.buy()
        elif self.position and self.cross < 0:
            self.close()

cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCross)

df = yf.download("SPY", start="2018-01-01", end="2024-12-31", auto_adjust=True)
if isinstance(df.columns, type(df.columns)) and df.columns.nlevels > 1:
    df.columns = df.columns.get_level_values(0)   # yfinance 0.2.x returns MultiIndex

cerebro.adddata(bt.feeds.PandasData(dataname=df))
cerebro.broker.setcash(100_000)
cerebro.broker.setcommission(commission=0.001)
cerebro.addsizer(bt.sizers.PercentSizer, percents=95)
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
cerebro.addanalyzer(bt.analyzers.DrawDown,    _name="dd")
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")

print(f"Start: ${cerebro.broker.getvalue():,.0f}")
res = cerebro.run()
print(f"End:   ${cerebro.broker.getvalue():,.0f}")

s = res[0]
print(f"Sharpe: {s.analyzers.sharpe.get_analysis().get('sharperatio')}")
print(f"MaxDD:  {s.analyzers.dd.get_analysis().max.drawdown:.2f}%")
print(f"Trades: {s.analyzers.trades.get_analysis().total.closed}")

# Delete: cerebro.plot(style="candle")
# Replace with:

import matplotlib.pyplot as plt
import numpy as np

# Pull equity curve from broker observer
equity = np.array(s.observers.broker.lines.value.array, dtype=float)
equity = equity[~np.isnan(equity)]
dates  = df.index[-len(equity):]

# Pull executed trades for markers
buys, sells = [], []
for t in s._trades.values():
    for trade_list in t.values():
        for tr in trade_list:
            buys.append((bt.num2date(tr.dtopen),  tr.price))
            if tr.isclosed:
                sells.append((bt.num2date(tr.dtclose), tr.pnlcomm))

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True,
                                gridspec_kw={"height_ratios": [2, 1]})

ax1.plot(df.index, df["Close"], color="#999", lw=1, label="SPY close")
if buys:
    bx, by = zip(*buys);   ax1.scatter(bx, by, marker="^", color="g", s=60, label="buy",  zorder=5)
if sells:
    sx, _  = zip(*sells);  ax1.scatter(sx, [df.loc[d, "Close"] for d in sx],
                                       marker="v", color="r", s=60, label="sell", zorder=5)
ax1.set_title("SMA(10/30) Crossover — SPY"); ax1.legend(); ax1.grid(alpha=.3)

ax2.plot(dates, equity, color="navy", lw=1.2)
ax2.fill_between(dates, equity, equity.min(), alpha=.1, color="navy")
ax2.axhline(100_000, color="grey", ls="--", lw=.8)
ax2.set_title(f"Equity — final ${equity[-1]:,.0f}"); ax2.grid(alpha=.3)

plt.tight_layout(); plt.show()