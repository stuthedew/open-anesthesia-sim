---
id: PL-CCVP
title: A refused branch at a second the run stores no state for gives the instant in raw seconds ('121 s'), while the other branch refusals give it as the chart's elapsed time
status: untriaged
feature: replay-findings
added: 2026-11-23
filed-pr: 2271
---

**Problem.** `core/stored_states.py` raises "this run stores no state at {instant_s} s: ..." when a branch or a replay asks for a second the run holds no state for. The message reaches the branch panel through `refused_branch_notice`. Once `PL-3JTH` (the branch refusals name the on-screen control and the chart's time) merges, every other branch refusal gives its instant through `app/formatting.py`'s `format_elapsed`, as "2m" or "24h", the form the chart's time axis uses. This one still says "121 s", so a learner meets two forms of time in one panel.

**Why it was not fixed in `PL-3JTH`.** `core/` may not import `app/`, so the core message cannot call `format_elapsed`. Two routes: the controller catches the core refusal and re-raises it with the instant formatted, or the elapsed-time format moves to a module both layers may import. The second keeps one home for the format; read `docs/ARCHITECTURE.md` § "Layering" before choosing.

**Done when.** A refused branch at an unstored second names the instant in the same form as the other branch refusals, and a test drives that refusal through the branch panel.
