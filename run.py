"""
Generic cerebro runner.
    python run.py --strategy sma_cross --ticker SPY --start 2018-01-01 --plot
"""
import argparse, importlib, sys
from pathlib import Path
import backtrader as bt
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def load_strategy(name):
    mod = importlib.import_module(f"strategies.{name}")
    for obj in vars(mod).values():
        if isinstance(obj, type) and issubclass(obj, bt.Strategy) and obj is not bt.Strategy:
            return obj
    sys.exit(f"No bt.Strategy subclass found in strategies/{name}.py")

def fetch(ticker, start, end):
    cache = Path("data") / f"{ticker}_{start}_{end or 'now'}.parquet"
    if cache.exists():
        return pd.read_parquet(cache)
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(0)
    df.to_parquet(cache)
    return df

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--ticker",   default="SPY")
    ap.add_argument("--start",    default="2018-01-01")
    ap.add_argument("--end",      default=None)
    ap.add_argument("--cash",     type=float, default=100_000)
    ap.add_argument("--commission", type=float, default=0.001)
    ap.add_argument("--plot", action="store_true")
    args = ap.parse_args()

    Strategy = load_strategy(args.strategy)
    df = fetch(args.ticker, args.start, args.end)

    cerebro = bt.Cerebro()
    cerebro.addstrategy(Strategy)
    cerebro.adddata(bt.feeds.PandasData(dataname=df))
    cerebro.broker.setcash(args.cash)
    cerebro.broker.setcommission(commission=args.commission)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

    for name, an in [("sharpe", bt.analyzers.SharpeRatio),
                     ("dd",     bt.analyzers.DrawDown),
                     ("trades", bt.analyzers.TradeAnalyzer),
                     ("sqn",    bt.analyzers.SQN)]:
        cerebro.addanalyzer(an, _name=name)

    print(f"Strategy: {Strategy.__name__}  |  {args.ticker} {args.start} -> {args.end or 'now'}")
    print(f"Start: ${cerebro.broker.getvalue():,.0f}")
    res = cerebro.run()[0]
    end = cerebro.broker.getvalue()
    print(f"End:   ${end:,.0f}  ({(end/args.cash - 1)*100:+.1f}%)")
    sharpe = res.analyzers.sharpe.get_analysis().get("sharperatio")
    print(f"Sharpe: {sharpe:.3f}" if sharpe else "Sharpe: n/a")
    print(f"MaxDD:  {res.analyzers.dd.get_analysis().max.drawdown:.2f}%")
    t = res.analyzers.trades.get_analysis()
    closed = t.total.closed if "closed" in t.total else 0
    won    = t.won.total if closed and "won" in t else 0
    print(f"Trades: {closed}  Win%: {(won/closed*100 if closed else 0):.0f}%")
    print(f"SQN:    {res.analyzers.sqn.get_analysis()['sqn']:.2f}")

    if args.plot:
        eq = np.array(res.observers.broker.lines.value.array, dtype=float)
        eq = eq[~np.isnan(eq)]
        dates = df.index[-len(eq):]
        fig, (a1, a2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True,
                                     gridspec_kw={"height_ratios": [2, 1]})
        a1.plot(df.index, df["Close"], color="#888", lw=1)
        a1.set_title(f"{args.ticker} close"); a1.grid(alpha=.3)
        a2.plot(dates, eq, color="navy", lw=1.2)
        a2.axhline(args.cash, color="grey", ls="--", lw=.8)
        a2.set_title(f"Equity - final ${eq[-1]:,.0f}"); a2.grid(alpha=.3)
        plt.tight_layout(); plt.show()

if __name__ == "__main__":
    main()
