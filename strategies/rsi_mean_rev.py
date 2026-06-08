import backtrader as bt

class RsiMeanRev(bt.Strategy):
    params = dict(rsi_period=14, oversold=30, overbought=70,
                  stop_pct=0.03, target_pct=0.06)

    def __init__(self):
        self.rsi = bt.ind.RSI(period=self.p.rsi_period)
        self.entry_price = None

    def next(self):
        if not self.position:
            if self.rsi < self.p.oversold:
                self.buy()
                self.entry_price = self.data.close[0]
        else:
            chg = (self.data.close[0] / self.entry_price) - 1
            if (chg <= -self.p.stop_pct
                or chg >= self.p.target_pct
                or self.rsi > self.p.overbought):
                self.close()
