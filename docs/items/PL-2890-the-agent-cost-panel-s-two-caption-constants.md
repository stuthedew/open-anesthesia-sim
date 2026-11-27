---
id: PL-2890
title: The agent cost panel's two caption constants are still named templates, though neither holds a field to fill
priority: P3
effort: S
status: ready
classes: refactor
feature: stale-source-claims
touches: src/anesthesia_sim/app/agent_cost.py, tests/unit/test_display_units.py
deferred-from: v0.7.0 - its problem is new since the freeze and no release schedules it, so it is deferred on the terms of § "Deferring to the next gate"; not safety or science (triage 2026-11-27)
added: 2026-11-23
filed-pr: 2306
payoff: a developer reading the agent cost captions is not sent looking for fields and a fill call that do not exist
---

**Problem.** `LIQUID_CAPTION_TEMPLATE` and `VAPOUR_CAPTION_TEMPLATE` in `src/anesthesia_sim/app/agent_cost.py` are plain strings. Neither has held a field since `PL-RJN9`, and `PL-PZSF` removed the `.format` call that once filled them. A reader of the name looks for the fields and the call that fills them. Both are public, listed in `__all__`, and `tests/unit/test_display_units.py` imports them.

`PL-PZSF` found it on 2026-11-23.

**What to do.** Rename them `LIQUID_CAPTION` and `VAPOUR_CAPTION`, in `agent_cost.py`, its `__all__` and the test.

**Why it matters.** A developer reading `_TEMPLATE` looks for the fields and the call that fills them, finds neither, and has to work out that the name is out of date before trusting the caption.

**Reproduced 2026-11-27.** On `main` at `f653c1eb`, both constants in `src/anesthesia_sim/app/agent_cost.py` are f-strings with no field left to fill, no `.format` call reads either of them, and `__all__` still lists both names.

**Done when.** The constants are named `LIQUID_CAPTION` and `VAPOUR_CAPTION` in `agent_cost.py`, its `__all__` and `tests/unit/test_display_units.py`, and no name ending in `_CAPTION_TEMPLATE` is left under `src/` or `tests/`.

**Generator check.** One-off. A name outlived its fields when `PL-RJN9` removed them and `PL-PZSF` removed the `.format` call. No head states the fact, which is whether a constant is filled in before it is shown.
