---
id: PL-YZKK
title: PL-PGZF was triaged apart from PL-CNCF on 'different functions, different modules', but assemble_chart_frame reaches PL-CNCF's cost through drawn_window, so the two tables are one curve and nothing in either item says so
status: untriaged
added: 2026-09-16
---

**Problem.** PL-PGZF was triaged apart from PL-CNCF on 'different functions, different modules', but assemble_chart_frame reaches PL-CNCF's cost through drawn_window, so the two tables are one curve and nothing in either item says so

**The disposition is defensible; the reason given is not.** `#617` triages
`PL-PGZF` to `P3 · M · ready` and keeps it separate from `PL-CNCF` on the
ground that they are "different functions, different modules". That is true of
where the code lives and false of what was measured. `assemble_chart_frame`
reaches `PL-CNCF`'s cost through one call chain - `_run_frame` ->
`SimulationController.drawn_window` -> `RunDefinition.evaluate_anchored`
(`src/anesthesia_sim/app/chart_frame.py:645`,
`src/anesthesia_sim/app/controller.py:852`) - so `PL-CNCF`'s 6.15 ms at 150
columns and `PL-PGZF`'s 8.39 / 11.80 / 15.42 ms at 102 / 601 / 1 069 drawn
instants are the same curve sampled at different budgets, the second one
including the frame's own packaging. Applied generally, "different functions,
different modules" would separate any caller from its callee as unrelated
performance findings.

**What that costs if nothing says otherwise.** Two open items describing one
cost, each with its own `Done when`, is an invitation to size two fixes - and
the fix is the same fix, sitting in `evaluate_anchored`. `PL-CNCF` carries the
trace and the memoisation hazard as of `claude/check-inflight-sessions-uz5d7s`;
`PL-PGZF` carries nothing pointing back.

**Why this is an item rather than an edit.** `bin/docket show PL-PGZF` reports
its file already edited on `origin/claude/gate-items-triage-batch-g1w5uv`
(`#617`, nine commits, green, open), so a second edit collides at merge. The
work is one sentence in `PL-PGZF`'s brief naming `PL-CNCF` as the same cost one
level up, added once `#617` has landed.

**Not a defect in the triage pass.** It ran without the call-chain trace, which
was made in a session it could not see - the same invisibility `PL-Q0J1` and
`PL-99YZ` record from the other direction.
