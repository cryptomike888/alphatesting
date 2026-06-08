import backtrader as bt

class AtrTrail(bt.Strategy):
    """SMA crossover entry, ATR-multiple trailing stop exit."""
    params = dict(fast=20, slow=50, atr_period=14, atr_mult=3)

    def __init__(self):
        sma_f = bt.ind.SMA(period=self.p.fast)
        sma_s = bt.ind.SMA(period=self.p.slow)
        self.cross = bt.ind.CrossOver(sma_f, sma_s)
        self.atr   = bt.ind.ATR(period=self.p.atr_period)
        self.trail = None

    def next(self):
        if not self.position:
            if self.cross > 0:
                self.buy()
                self.trail = self.data.close[0] - self.p.atr_mult * self.atr[0]
        else:
            self.trail = max(self.trail,
                             self.data.close[0] - self.p.atr_mult * self.atr[0])
            if self.data.close[0] <= self.trail:
                self.close()
