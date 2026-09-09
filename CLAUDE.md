# Trading desk — house rules

Loaded into every session. Keep it short; every line here is paid for on
every turn.

## Desks
Address a desk directly, e.g. `@macro what is the front end pricing?`
See `.claude/agents/` for the roster. Each desk owns a narrow IBKR tool
allowlist — that allowlist is the token budget, do not widen it casually.

## Data discipline (this is where tokens actually go)
1. **Bound every query.** Option chains and long bar series are the only
   things in this repo that can blow a context window. Always pass
   `min_strike`/`max_strike`, and prefer `step_count` over a long `period`.
2. **Compute, don't read.** More than ~30 rows: have `@quant` pull it to
   `data/` and run pandas. Never reason over hundreds of raw OHLCV rows.
3. **Return a verdict, not a table.** A desk reports its conclusion, the
   2-3 numbers behind it, and what would falsify it.

## Standing facts
- IBKR access here is **read-only**. There is no order-placement tool.
  Sizing is advisory; the human executes in TWS.
- Quote data may be delayed depending on the account's subscriptions.
  State the timestamp on any price you act on.
- Never state a number you did not pull from a tool this session. No
  recalled prices, no plausible-looking fills.

## Memory
Durable desk state lives in `notes/<desk>.md`. Read it at the start of a
question, append to it when a view changes. Subagents are stateless — this
file is the only continuity they have.
