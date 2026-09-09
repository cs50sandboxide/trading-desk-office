# trading-desk-office

Four specialist desks you address directly in chat, plus a status board that
shows which of them is working and which is resting.

## Desks

| Desk | Covers | Data source |
|---|---|---|
| `@fundamentals` | Financials, growth story, what drives firm value | **Web** + IBKR themes/peers |
| `@technicals` | Volume, RSI, MAs, support/resistance, momentum | IBKR bars → computed here |
| `@risk` | Correlation vs. book, drawdown, margin, portfolio impact | IBKR account + computed |
| `@news` | Headlines, catalysts, event calendar, macro | **Web** + IBKR themes |

```
@technicals is NVDA overbought on the daily?
@risk what does a 5% NVDA position do to my concentration?
@news what's on the calendar for NVDA in the next month?
```

## Your prompts go in these files

Each `.claude/agents/*.md` has a `<!-- PASTE YOUR PROMPT -->` marker. Put
your existing `trading-desk` persona above it and keep the plumbing section
below it — that section documents which tools exist, in what order to call
them, and which data the connector does **not** have. The frontmatter
(`tools:`) is the token budget and should stay as written.

## The office board

```
Claude Code ──hook──▶ office/desk_hook.py ──▶ office/state.json ──▶ index.html
```

Four cards, one per desk. Green pulsing lamp = working, with elapsed time
and the task you gave it. Grey = resting. Polls every 2s.

**This costs zero model tokens.** Hooks are subprocess calls; their payloads
never enter a context window. The board is free.

### Run it

```bash
./office/serve.sh     # → http://localhost:8787
```

### Setup

None. The hooks ship in `.claude/settings.json` and resolve their own path
via `$CLAUDE_PROJECT_DIR`, so opening this repo in Claude Code is the whole
installation. Nothing touches your global settings.

`SubagentStart` carries `agent_type` — the desk name verbatim from the
frontmatter — so the board knows *which* desk lit up. `SubagentStop` carries
only `agent_id`, so the hook remembers the id→desk mapping from start. The
`Task` matcher is a fallback for Claude Code builds that spawn agents
without firing a native `SubagentStart`.

The hook swallows all exceptions and exits 0 — it can never block your CLI.

### If every desk stays grey

The board keys on the `agent_type` string the hook receives, and it must
match `DESKS` in `office/desk_hook.py` and in `index.html`. A plugin-supplied
agent may report a namespaced name (`trading-desk:risk`), which silently
matches nothing. To see the real string:

```bash
DESK_HOOK_DEBUG=1   # then run a desk and read office/debug.log
```

Update both `DESKS` lists to whatever appears there.

### Requires Claude Code

Hooks exist in the Claude Code CLI and desktop app only. There is no hook
system in claude.ai Cowork or the web app, so the desks must live here as
repo files rather than as Cowork agents. That is the trade that keeps the
board free: the alternative — having each desk report its own status — costs
roughly 4,000–6,000 tokens of tool schema per invocation, more than the
desks themselves.

## Token budget

Always-on, every turn of the main session:

| Item | Cost |
|---|---|
| `CLAUDE.md` | ~320 tok |
| 4 desk descriptions (routing) | ~170 tok |
| Office board | **0** |
| **Total** | **~490 tok** |

Per invocation, only for the desk you called:

| Desk | Schemas | Prompt | Approx |
|---|---|---|---|
| `@news` | ~900 | ~380 | ~1,300 |
| `@fundamentals` | ~950 | ~350 | ~1,300 |
| `@technicals` | ~1,300 | ~350 | ~1,650 |
| `@risk` | ~1,700 | ~430 | ~2,100 |

Granting a desk the full IBKR surface instead would cost roughly **6,000
tokens of schema per invocation**. Estimated from 11 of the 25 schemas read
directly (mean ≈ 243 tok, range 62–650) and extrapolated; right order of
magnitude, not exact.

**The real cost is payloads, not desks.** A year of daily bars is ~250 rows;
a correlation across a ten-name book is ten of those. That is why
`@technicals` and `@risk` write series to `data/` and reply with statistics
only. Adding a fifth desk is nearly free. Letting one desk read raw bars
into the conversation is not.

## Layout

```
.claude/agents/   four desk definitions — paste your prompts here
CLAUDE.md         house rules (loaded every session — keep it short)
office/           status board: hook + state.json + index.html
notes/            per-desk durable memory
data/             scratch for computed series (gitignored)
```
