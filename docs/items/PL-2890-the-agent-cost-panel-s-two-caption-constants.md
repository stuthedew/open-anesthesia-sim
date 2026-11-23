---
id: PL-2890
title: The agent cost panel's two caption constants are still named templates, though neither holds a field to fill
status: untriaged
feature: stale-source-claims
added: 2026-11-23
filed-pr: 2306
---

**Problem.** `LIQUID_CAPTION_TEMPLATE` and `VAPOUR_CAPTION_TEMPLATE` in `src/anesthesia_sim/app/agent_cost.py` are plain strings. Neither has held a field since `PL-RJN9`, and `PL-PZSF` removed the `.format` call that once filled them. A reader of the name looks for the fields and the call that fills them. Both are public, listed in `__all__`, and `tests/unit/test_display_units.py` imports them.

`PL-PZSF` found it on 2026-11-23.

**What to do.** Rename them `LIQUID_CAPTION` and `VAPOUR_CAPTION`, in `agent_cost.py`, its `__all__` and the test.
