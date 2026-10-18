---
id: PL-1KQ9
title: A machine profile can open the run at a fresh gas flow off the slider's 0.1 L/min grid - 2.25 L/min, or 0.25 L/min under a declared range floored there, which the control offers from 0.3 - so the slider sits on a neighbouring step while the run holds the stated flow and the readout rounds it (found building PL-7CRY)
priority: P3
effort: S
status: ready
classes: defect, ux
feature: anesthesia-machine
touches: src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_dashboard_frame.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-12 triage pass
added: 2026-10-12
payoff: no run opens at a fresh gas flow that the slider and the readout beside it cannot both state
verify: grep -q "def test_an_opening_fresh_gas_flow_off_the_slider_grid_is_refused" tests/unit/test_dashboard_frame.py
---

**Problem.** A machine profile can open the run at a fresh gas flow off the slider's 0.1 L/min grid - 2.25 L/min, or 0.25 L/min under a declared range floored there, which the control offers from 0.3 - so the slider sits on a neighbouring step while the run holds the stated flow and the readout rounds it (found building PL-7CRY)

`PL-7CRY` bounds the fresh gas flow control by the run's accepted range,
offered at the slider's 0.1 L/min resolution with each end moved to the nearest
step inside it (`offered_range` in `app/dashboard_frame.py`). Nothing holds a
profile's opening flow, `default_fresh_gas_flow_l_min`, to that grid:
`core/parameters.py` checks it positive and finite, and
`AgentUptakeSystem.for_agent` builds it as a `FreshGasFlow`, which checks the
model's envelope. So a profile stating 2.25 L/min opens the run at 2.25, while
the slider sits at 2.2 (`slider_position` rounds half to even) and the readout
reads 2.2. One stating 0.25 L/min under a range floored at 0.25 opens at 0.25,
the slider is held by Qt at the offered floor of 0.3, and the readout reads 0.2,
so the slider and the readout beside it disagree and neither states the flow
the run holds.

**Not live.** The shipped profile states 4.0 L/min and declares no range, and
no setting the reader makes reaches it, since every value the slider emits is a
step. It needs a profile authored off the grid.

**Two routes, for triage.** Refuse an opening flow off the control's grid when
the profile loads, so that the slider can state every flow a run opens at; or
state the opening flow at its own precision and let the slider stand for the
nearest step.

**Not a recurrence of `PL-7CRY`,** which `docket new` matched on shared paths:
that item bounds the control's range, and this one is the opening value inside
it.

**Why it matters.** The slider and the readout beside it are the reader's
statement of the flow the run holds, and here neither is: the readout rounds
2.25 to 2.2, and at the floor the slider stands at 0.3 beside a readout of 0.2
over a run at 0.25. A displayed setting that differs from the one the model
runs at is the wrong-context failure `CLAUDE.md`'s standard counts as a safety
failure, held at `P3` only because no profile reaches it.

**Decision needed.** Which of the two routes above. **Recommendation: refuse
an opening flow off the control's grid, where the dashboard builds the control
for the run**, so the grid stays the interface's fact and the core never learns
it. The Qt port's rule that a slider position is a printed value (cited in
`app/` as `PL-25KS`, decision D4) rules out the second route, under which the
slider would stand for a flow the run does not hold, and the safety standard
prefers an obvious failure to a plausible readout. The cost is a profile author
meeting an error at launch rather than a run that opens.

**Done when.** No run opens at a fresh gas flow the slider cannot state -
refused where the profile is loaded under the recommended route, or stated at
its own precision by slider and readout alike under the other - and a test in
`tests/unit/test_dashboard_frame.py` pins 2.25 L/min and the 0.25 L/min floor.

**Decided 2026-10-18 in the product decision batch's design round: refuse
an opening flow off the control's grid, where the dashboard builds the
control for the run.** This is the recommendation above, taken as an obvious
call rather than put to the project owner, because two rules this repository
already states leave only one route. The Qt port's decision D4 (`PL-25KS`)
makes a slider position a printed value. The second route would let the
slider stand at a flow the run does not hold, so it breaks D4. The
safety-critical standard in `CLAUDE.md` prefers an obvious failure to a
plausible-looking value, and the refusal is that failure. A third route, a
finer slider grid, was considered and refused: a profile can state a flow at
any precision, so a finer grid moves the defect and does not remove it. The
check belongs in `app/`, beside `offered_range`, because the grid is the
interface's fact and `core/` should not learn it. One rule covers both cases
in the problem statement. 2.25 L/min is off the 0.1 L/min grid, and 0.25 L/min
under a range floored there lies outside the offered range, which starts at
0.3. The refusal names the profile's flow, the grid and the offered range, as
`.claude/rules/sources-and-docstrings.md` asks of a refusal. The premise was
re-read at `21174fd3`. `core/parameters.py` still checks
`default_fresh_gas_flow_l_min` only as positive and finite, and the shipped
profile's 4.0 L/min is on the grid, so no shipped run is refused.
