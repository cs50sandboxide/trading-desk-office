# trading-desk-office

Six specialist trading desks you can address individually, each wired to the
IBKR connector with a deliberately narrow tool allowlist.

## Roster

| Desk | Address | Covers | IBKR tools |
|---|---|---|---|
| Macro | `@macro` | Regime, rates, FX, commodities, index level | 6 |
| Equities | `@equities` | Single names, peers, theme exposure | 6 |
| Options | `@options` | Chains, strikes, spreads, expiries | 5 |
| Risk | `@risk` | Positions, exposure, margin, attribution | 6 |
| Execution | `@execution` | Live orders, fills, alerts | 6 |
| Quant | `@quant` | Anything needing >30 rows of data | 3 + Bash/pandas |

Ask a desk a question the way you would ask a colleague:

```
@risk what is my largest correlated cluster right now?
@options build me a 30-delta call spread on NVDA for the March expiry
@macro is the front end still pricing cuts?
```

## How it works

```
you ──▶ main session ──▶ Task tool ──▶ desk subagent (own context window)
                                          │
                                          ├─▶ IBKR MCP tools (read-only)
                                          └─▶ notes/<desk>.md  (memory)
                                          │
                          summary only ◀──┘
```

Each desk is a markdown file in `.claude/agents/`. Frontmatter declares the
name, the description used for routing, the tool allowlist, and the model.
The body is the desk's operating procedure.

When you address a desk, it runs in its **own context window** and returns
only its conclusion to the main thread. That isolation is the whole point:
a 400-row option chain is paid for once, inside the options desk, and never
enters the conversation you are reading.

## Read-only

The IBKR connector exposed here is read-only — 25 `get_*`/`search_*` tools
and no order-placement tool. The desks analyse, size, and hand you a ticket;
you enter it in TWS. `@execution` reports on orders and fills but cannot
place, amend, or cancel one.

## Token budget

Resident cost, paid on every turn of the main session:

| Item | Cost |
|---|---|
| `CLAUDE.md` | ~350 tok |
| 6 desk descriptions (for routing) | ~250 tok |
| **Total always-on** | **~600 tok** |

Per-desk cost, paid only when that desk is invoked — its prompt plus its
tool schemas:

| Desk | Schemas | Prompt | Approx total |
|---|---|---|---|
| Risk | ~400 | ~330 | ~730 |
| Execution | ~500 | ~280 | ~780 |
| Equities | ~1,100 | ~310 | ~1,400 |
| Macro | ~1,300 | ~300 | ~1,600 |
| Quant | ~1,500 | ~330 | ~1,800 |
| Options | ~1,900 | ~360 | ~2,300 |

For comparison, granting every desk the full IBKR surface would cost roughly
**6,000 tokens of schema per desk invocation**. The allowlists cut that by
60–85%. Widening one is the single most expensive edit you can make here.

Schema figures are estimated from 11 of the 25 IBKR tool schemas inspected
directly (mean ≈ 243 tokens, range 62–650) and extrapolated to the rest.
Treat them as the right order of magnitude, not exact.

### Where tokens are actually spent

Not on the agents — on the payloads. The three things that can dwarf
everything in the table above:

1. **Unbounded option chains.** A liquid name with no strike bounds returns
   hundreds of rows. Always bound them; `@options` is instructed to.
2. **Long bar series.** `ONE_YEAR` of daily bars is ~250 rows. Use
   `step_count`, or send it to `@quant`.
3. **Re-reading data into context.** `@quant` writes raw series to `data/`
   and returns only the computed statistic. Use it above ~30 rows.

## Memory

Subagents are stateless — a desk starts fresh on every question. Continuity
comes from `notes/<desk>.md`, which each desk reads at the start and appends
to when a view changes. This is a deliberate trade: file-based memory costs
a few hundred tokens per invocation instead of carrying a full conversation
history per desk.

## Layout

```
.claude/agents/     six desk definitions
CLAUDE.md           house rules (loaded every session — keep it short)
notes/              per-desk durable memory
data/              scratch for @quant (gitignored)
```

## Tuning

- **Cheaper**: move `@execution` and `@risk` lookups to `model: haiku`
  (execution already is). Drop desks you do not use — an unused desk still
  costs its description on every turn.
- **Sharper**: `model: opus` on `@risk` and `@options`, the two desks where
  being wrong is expensive.
- **Adding a desk**: copy the closest existing file, give it the smallest
  tool allowlist that answers its questions, keep the body under ~30 lines.
