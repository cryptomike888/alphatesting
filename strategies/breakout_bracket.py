import backtrader as bt

class BreakoutBracket(bt.Strategy):
    """20-day high breakout with OCO bracket (TP + SL submitted together)."""
    params = dict(lookback=20, stop_pct=0.02, target_pct=0.05)

    def __init__(self):
        self.high20 = bt.ind.Highest(self.data.high, period=self.p.lookback)

    def next(self):
        if self.position:
            return
        if self.data.close[0] <= self.high20[-1]:
            return
        price = self.data.close[0]
        self.buy_bracket(
            price=price,
            limitprice=price * (1 + self.p.target_pct),
            stopprice=price * (1 - self.p.stop_pct),
        )
