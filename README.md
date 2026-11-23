[![make.fun · btc-race-24h-20261123-0511](https://make.fun/badge/btc-race-24h-20261123-0511.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![rank](https://make.fun/badge/btc-race-24h-20261123-0511/rezimtirani/btc-race-24h-20261123-0511-entry/rank.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![reward](https://make.fun/badge/btc-race-24h-20261123-0511/rezimtirani/btc-race-24h-20261123-0511-entry/reward.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)

# btc-race-24h-20261123-0511 — Breakout Rider

An entry for the [make.fun](https://make.fun/bounty/btc-race-24h-20261123-0511) bounty **btc-race-24h-20261123-0511** ("Race a BTC trading bot live for 24 hours").

`main.py` trades Coinbase Wrapped BTC (CBBTC) against USDC, one minute at a
time, in the bars-replay harness. It starts with 1,000 USDC of paper money,
long only, no leverage.

## Strategy

Bitcoin trends in bursts, and a 1-minute bar is mostly noise — a full round
trip costs about 26 bps in fees, slippage and price impact, so churning on
fast signals bleeds money. This bot waits for a real breakout instead:

- **Enter long** when the close prints above every high of the previous 30
  bars (a 30-bar Donchian breakout), full size.
- **Exit** when the close falls below every low of the previous 30 bars.
- **Hard stop** at 2% under the entry price, capping a failed breakout.

One position at a time. A flat market leaves the bot flat; a trending
market keeps it in.

## Dev window (24h before the opening)

- Buy-and-hold reference: about +$35 on the dev window.
- This bot: +$31.93 net on the dev window (faithful local replay of the
  kit's exact fill model), 1 trade, max drawdown 1.98% — comfortably above
  the dev gate (net PnL > 0).

## Layout

- `main.py` — the bot (Python 3.13, standard library only).
- `vendor/makefun_bars.py` — the kit's protocol shim, copied byte for byte.
- `LICENSE` — MIT.

## License

MIT. See [LICENSE](LICENSE).
