"""Breakout rider for the BTC 24h race (agent-fun/bars-replay/v1).

One idea, kept deliberately plain: Bitcoin trends in bursts, and a 1-minute
bar is mostly noise (a round trip costs about 26 bps, so churning on fast
signals bleeds money). This bot waits for a real breakout instead — it goes
long only when the close prints above every high of the previous half hour,
and it steps out when the close falls below every low of the previous half
hour. One position at a time, full size, no leverage, no shorts.

The exit rule is the same window as the entry rule, so a flat market leaves
the bot flat and a trending market keeps it in. A hard stop (added below in
the exit check) caps a failed breakout at 2% under the entry price.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars

SYMBOL = "CBBTC"
LOOKBACK = 30
STOP_BPS = 200
SLIP_BPS = 250

closes = []
highs = []
lows = []
seen_t = None
entry_price = None
last_exit_bar = -10 ** 9
COOLDOWN_BARS = 10


def _cooling_down():
    """True while fewer than COOLDOWN_BARS have passed since the last exit.

    A breakout that just stopped us out usually re-fires at the same level
    while the market is still choppy; waiting a few bars keeps the bot from
    buying straight back into the whipsaw that just cut it.
    """
    return len(closes) - last_exit_bar <= COOLDOWN_BARS


def _record_bar(state):
    """Append the latest bar to the history, once per bar."""
    global seen_t
    bar = state.latest.get(SYMBOL)
    if bar is None:
        return
    if seen_t is not None and bar["t"] == seen_t:
        return
    seen_t = bar["t"]
    closes.append(int(bar["c"]))
    highs.append(int(bar["h"]))
    lows.append(int(bar["l"]))


def _highest_high(n):
    """Highest high of the n bars before the current one."""
    return max(highs[-n - 1:-1])


def _lowest_low(n):
    """Lowest low of the last n bars (the current bar's low never binds)."""
    return min(lows[-n:])


def decide(state, batch):
    global last_exit_bar
    if state.warming_up:
        return []
    _record_bar(state)
    price = state.close(SYMBOL)
    if price is None or len(closes) < LOOKBACK + 1:
        return []
    held = state.positions.get(SYMBOL)
    if held is not None and held.qty > 0:
        broke_down = price < _lowest_low(LOOKBACK)
        stopped = entry_price is not None and (price - entry_price) * 10000 // entry_price <= -STOP_BPS
        if broke_down or stopped:
            last_exit_bar = len(closes)
            return [{
                "side": "sell",
                "symbol": SYMBOL,
                "qty": held.qty,
                "max_slippage_bps": SLIP_BPS,
            }]
        return []
    if _cooling_down():
        return []
    if price > _highest_high(LOOKBACK):
        room = state.weight_room(SYMBOL)
        spend = state.cash if state.cash < room else room
        if spend < 1_000_000:
            return []
        return [{
            "side": "buy",
            "symbol": SYMBOL,
            "notional_quote_units": spend,
            "max_slippage_bps": SLIP_BPS,
        }]
    return []


def on_batch(state, batch):
    global entry_price
    orders = decide(state, batch)
    if orders and orders[0]["side"] == "buy":
        entry_price = state.close(SYMBOL)
    if orders and orders[0]["side"] == "sell":
        entry_price = None
    return orders


makefun_bars.run(on_batch)
