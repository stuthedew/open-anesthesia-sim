---
id: PL-K5NY
title: SimulationView.add_run admits a controller the case never sanctioned, so an unrelated run is drawn as Run 2 of a case it is not part of
priority: P1
effort: S
status: done
classes: defect, safety
feature: branch-run-set-integrity
milestone: v0.5.0
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py
added: 2026-09-20
closed: 2026-09-20
pr: 788
payoff: stops two unrelated runs being drawn as one patient under two managements, which is the whole claim a comparison makes
verify: grep -q 'def test_add_run_refuses_a_run_the_case_never_sanctioned' tests/integration/test_simulation_view.py
---

**Problem.** SimulationView.add_run admits a controller the case never sanctioned, so an unrelated run is drawn as Run 2 of a case it is not part of

**Why it matters.** Two curves drawn on one time axis assert that they are one
patient under two managements - that is the whole claim `BranchedCase` exists to
carry, and `docs/ARCHITECTURE.md` § "What a branch is" states it. `add_run`
checks the displayed-run cap and the shared agent, and nothing else, so a
controller that is not in `self._case` is placed as "Run 2", drawn in the same
`ChartFrame` against the same ×MAC ruler, and labelled by `run_label` exactly as
a real branch would be. `view.case.runs` then has one entry while the chart has
two.

`CLAUDE.md`'s safety-critical standard is what makes this more than tidiness:
a comparison is a clinically meaningful display, and one that silently asserts
a shared patient and a shared pre-branch history where there is neither is a
wrong claim wearing a correct chart. The guard belongs where the run enters,
not in a caller's discipline.

**Found 2026-09-20** by the adversarial review of `#784`, and reproduced: a
fresh `SimulationController()` passed to `add_run` on a case dashboard is
accepted, named "Run 2" and drawn, while `stranger in case.runs` is `False`.

**Done when.**

1. `add_run` refuses a controller that is not a branch of the dashboard's own
   case, naming what it refused.
2. The refusal message says which case the run is not part of, per
   `.claude/rules/sources-and-docstrings.md`.
3. A regression test covers it.

**Classed `safety` and seated `P1`, deliberately.** `CLAUDE.md`'s standard is
explicit that presentation correctness is part of safety: "the correct number
with the wrong units, label, patient context, stale state, model name/version,
or provenance is still a safety failure". A stranger run drawn as "Run 2" of
this case is exactly the wrong *patient context* - every number on it is
computed correctly and every one of them is attributed to a case it was never
part of.

Unreachability was weighed and does not lower it. No shipped path calls
`add_run` with a stranger today, but `PL-QRD1` is this project's own worked
example of a defect that sat unreachable until an entry point was built, and
the guard costs three lines.
