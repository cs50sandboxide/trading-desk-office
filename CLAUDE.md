# Trading desk — house rules

Loaded into every session. Keep it short; every line is paid for on every turn.

## Desks
`@fundamentals` `@technicals` `@risk` `@news` — see `.claude/agents/`.
Each owns a narrow tool allowlist. That allowlist is the token budget;
widening one is the most expensive edit in this repo.

## What the IBKR connector does and does not have
Read-only: 25 `get_*`/`search_*` tools, no order placement. Sizing is
advisory, the human executes in TWS.
- **No fundamentals** — no financials, estimates, or multiples.
- **No news** — no headline feed. (`whats_new` is the connector changelog.)
- **No indicators** — OHLCV bars only; RSI and friends are computed here.
`@fundamentals` and `@news` therefore run on WebSearch/WebFetch.

## Data discipline (this is where tokens actually go)
1. More than ~30 rows: write it to `data/` and compute over it with pandas.
   Never restate raw OHLCV in a reply.
2. Bound every query — prefer `step_count` over a long `period`.
3. Return a verdict, the 2–3 numbers behind it, and what would falsify it.

## Never
State a number you did not pull from a tool this session. No recalled
prices, no reconstructed financials, no undated headlines.

## Memory
Durable desk state lives in `notes/<desk>.md`. Subagents are stateless —
that file is the only continuity they have.
