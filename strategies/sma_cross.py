import backtrader as bt

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
