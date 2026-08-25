---
id: PL-JD2P
title: Cover the module-level agent-color guard in `simulation_view.py`
status: dropped
reason: Duplicate of PL-7YZH, which was filed on main for the same guard and carries the better brief
added: 2026-08-25
closed: 2026-08-25
---

**Problem.** `app/simulation_view.py` line 109 raises
`RuntimeError("AGENT_COLOR_SCHEMES must define exactly the built-in volatile
agents")` at import time, and never executes under the test suite.

**Why it was dropped.** PL-7YZH was filed on `main` covering the same guard,
independently and on the same day, as part of a sweep of all seventeen
uncovered guard lines. Its brief is better: it carries the reproduce command,
the full table, and the `_halt_run` analysis this item lacked. PL-7YZH has
been re-cut to cover exactly the two `simulation_view.py` paths that a
coverage command cannot prove, which is what this item was for.

Recorded rather than deleted so the finding is not re-raised: the guard is
covered by PL-7YZH, not overlooked.
