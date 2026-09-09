#!/usr/bin/env python3
"""Claude Code hook: track which trading desk is working.

Reads one hook event on stdin, updates office/state.json, exits 0.
Never raises — a crashing hook blocks the CLI.

Wire it to SubagentStart, SubagentStop, PreToolUse, PostToolUse, SessionEnd.
Costs zero model tokens: hook payloads never enter the context window.
"""

import json
import os
import sys
import time
from pathlib import Path

DESKS = ["fundamentals", "technicals", "risk", "news"]
STATE = Path(__file__).resolve().parent / "state.json"


def load():
    try:
        return json.loads(STATE.read_text())
    except Exception:
        return {"desks": {d: {"status": "resting"} for d in DESKS}, "ids": {}}


def save(state):
    state["updated"] = time.time()
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    os.replace(tmp, STATE)


def start(state, desk, agent_id=None, task=None):
    if desk not in DESKS:
        return
    state["desks"][desk] = {
        "status": "working",
        "since": time.time(),
        "task": (task or "")[:120],
    }
    if agent_id:
        state.setdefault("ids", {})[agent_id] = desk


def stop(state, desk):
    if desk in DESKS:
        state["desks"][desk] = {"status": "resting", "since": time.time()}


def debug(raw):
    """Set DESK_HOOK_DEBUG=1 to dump raw payloads to office/debug.log.

    Use this to discover the exact `agent_type` string your agents report —
    plugin-supplied agents may be namespaced (e.g. "trading-desk:risk").
    Whatever appears there must match DESKS above and in index.html.
    """
    if os.environ.get("DESK_HOOK_DEBUG") != "1":
        return
    with open(STATE.parent / "debug.log", "a") as f:
        f.write(json.dumps(raw) + "\n")


def main():
    raw = json.load(sys.stdin)
    debug(raw)
    event = raw.get("hook_event_name", "")
    state = load()

    if event == "SubagentStart":
        start(state, raw.get("agent_type"), raw.get("agent_id"))

    elif event == "SubagentStop":
        stop(state, state.get("ids", {}).get(raw.get("agent_id", "")))

    elif event in ("PreToolUse", "PostToolUse"):
        # Fallback for Claude Code versions that fire the Agent tool without
        # a native SubagentStart. subagent_type is the desk name verbatim.
        if raw.get("tool_name") in ("Task", "Agent"):
            ti = raw.get("tool_input") or {}
            desk = ti.get("subagent_type")
            if event == "PreToolUse":
                start(state, desk, task=ti.get("description") or ti.get("prompt"))
            elif not (raw.get("tool_response") or {}).get("agentId"):
                # Sync agent finished. Async ones end via SubagentStop.
                stop(state, desk)

    elif event in ("SessionEnd", "Stop"):
        for d in DESKS:
            stop(state, d)

    save(state)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
