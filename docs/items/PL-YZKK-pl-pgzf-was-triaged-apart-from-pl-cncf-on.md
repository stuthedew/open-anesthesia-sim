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

**Updated after `#617` merged (2026-09-16).** The paragraph above about a
colliding edit is spent: `#617` is on `main` at `2a538ec1`, `PL-PGZF` is
`P3 · M · ready`, `classes: perf`, `feature: chart-readout`, and the edit this
item asks for is unblocked. Two things its landed front matter settles that the
pull-request body did not:

- **The separation is better supported than the reason given for it.**
  `PL-PGZF`'s `verify:` is
  `python3 tools/doc_check.py check && grep -qF 'measured at the window-following budget' docs/WORKING_NOTES.md`
  and its `touches` is `src/anesthesia_sim/app/chart_frame.py, docs/WORKING_NOTES.md`,
  so its declared work is to *record* the measurement. `PL-CNCF`'s `Done when`
  is to reduce the cost or accept it with a number. Those are different pieces
  of work over one cause, which is a sound split - and it is not the split
  "different functions, different modules" describes.
- **What is still owed is one sentence**, in `PL-PGZF`'s brief, naming
  `PL-CNCF` as the same cost one call level up so that the two `Done when`s
  are not read as two fixes. The call chain and the memoisation hazard are
  already written into `PL-CNCF` on `claude/check-inflight-sessions-uz5d7s`.
