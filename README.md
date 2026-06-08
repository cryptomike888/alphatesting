# alphatesting

Backtrader-based strategy sandbox.

## Setup

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt

## Run a strategy

    python run.py --strategy sma_cross           --ticker SPY --plot
    python run.py --strategy rsi_mean_rev        --ticker QQQ --start 2020-01-01 --plot
    python run.py --strategy breakout_bracket    --ticker AAPL --plot
    python run.py --strategy atr_trail           --ticker SPY --plot

## Structure

- strategies/  one bt.Strategy subclass per file
- run.py       cerebro harness; picks a strategy by --strategy name
- data/        local yfinance cache (gitignored)
- results/     equity curves, trade logs (gitignored)
- notebooks/   exploratory analysis
