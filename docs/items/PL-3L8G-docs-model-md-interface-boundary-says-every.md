---
id: PL-3L8G
title: docs/MODEL.md § 'Interface boundary' says every drawn instant is a whole number of hundredths so the hover prints the exact instant, but the hover note says instants are given at the run's step (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: ready
classes: defect, docs
feature: model-md-structure
touches: docs/MODEL.md
deferred-from: v0.7.0 - a new problem: the whole-hundredths claim was written by PL-T5NJ's work clearing Gate 3 (#1840, 2026-10-25), after the freeze, and not safety or science
added: 2026-11-05
payoff: the hover's claim to print the exact instant names the step length it depends on, so a change to the step cannot make it silently false
verify: ! grep -qF 'instant falls on a whole hundredth of a second, so the hover readout can give' docs/MODEL.md
---

**Problem.** docs/MODEL.md § 'Interface boundary' says every drawn instant is a whole number of hundredths so the hover prints the exact instant, but the hover note says instants are given at the run's step (copy editor structure read, 2026-11-05)

**Checked 2026-11-09:** § "Interface boundary" says "Each drawn instant falls
on a whole hundredth of a second, so the hover readout can give the exact time
of the state it shows" (lines 5931 to 5933). § "The chart's hover readout"
says that the chart's columns fall on whole hundredths "and every other drawn
instant falls on a simulation step" (lines 8798 to 8800). Both hold today only
because the interface's step is 0.1 s (`SIMULATION_STEP_S` in
`app/dashboard_frame.py`). Neither passage says so, and the supported step
range goes down to 1 ms (`MINIMUM_SIMULATION_STEP_S`), at which a control
change could fall between two hundredths. The comment on
`HOVER_INSTANT_RESOLUTION_S` in `app/chart_frame.py` makes the same unstated
assumption.

**Why it matters.** The hover readout prints an instant that the document
calls exact. That claim depends on the step length, which neither passage
names, so a later change to the step would make the printed instant inexact
without any sentence becoming visibly wrong.

**Done when.** One passage states the condition: drawn instants on a
simulation step are whole hundredths because the interface's step is 0.1 s.
The other passage points to it, and the sentence in § "Interface boundary"
gives that reason in place of its bare "so". Where no test holds the
condition, the sentence uses the document's ``no test yet (`PL-XXXX`)`` form.

**Generator check.** One-off: a finding from the `docs/MODEL.md`
structure-read sweep of 2026-11-05.
