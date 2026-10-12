---
id: PL-1KQ9
title: A machine profile can open the run at a fresh gas flow off the slider's 0.1 L/min grid - 2.25 L/min, or 0.25 L/min under a declared range floored there, which the control offers from 0.3 - so the slider sits on a neighbouring step while the run holds the stated flow and the readout rounds it (found building PL-7CRY)
status: untriaged
feature: anesthesia-machine
added: 2026-10-12
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
