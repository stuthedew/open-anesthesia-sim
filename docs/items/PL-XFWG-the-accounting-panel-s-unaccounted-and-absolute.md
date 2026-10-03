---
id: PL-XFWG
title: The accounting panel's Unaccounted and Absolute error lines always read the same string since PL-3PJZ printed each as the power of ten it lies below and dropped the sign, so the panel shows one fact twice; whether one line should carry it is a change to what a learner sees
priority: P3
effort: S
status: ready
classes: ux
feature: presentation-safety
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/formatting.py, tests/unit/test_dashboard_frame.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-03 triage pass
added: 2026-10-03
payoff: the accounting panel states the run's unaccounted agent once, so a learner is not sent looking for a difference between two identical lines
verify: grep -q 'def test_the_accounting_panel_prints_the_residual_once' tests/unit/test_dashboard_frame.py && ! grep -qF 'Absolute error' src/anesthesia_sim/app/dashboard_frame.py
falsifies: Absolute error
---

**Problem.** The accounting panel's Unaccounted and Absolute error lines always read the same string since PL-3PJZ printed each as the power of ten it lies below and dropped the sign, so the panel shows one fact twice; whether one line should carry it is a change to what a learner sees

**Reproduced 2026-10-03 at triage.** `absolute_error_l` is
`abs(unaccounted_agent_l)` (`core/agent_simulation_validation.py:91`), and
`format_agent_residual` prints only the decade a value lies below, without its
sign, so the two lines read alike for every input: `-5.601e-14` and
`5.601e-14` give `<1e-13 L` on both, `0.0` gives `0 L` on both, `-3e-10` gives
`<1e-09 L` on both. The formatter's own docstring says as much ("Both lines
therefore read alike").

**Why it matters.** A line a learner reads twice in identical words invites a
search for a difference that is not there, and the panel spends a line saying
nothing new. Which line goes, if either, changes what a learner sees, so the
answer is the project owner's.

**Decision needed.** Keep both residual lines, or show the residual once.

**Recommendation:** show it once, as "Unaccounted", the line that closes the
amounts printed above it; with the sign dropped, "Absolute error" says nothing
it does not. The signed values stay where they mean something, in the notice a
failing check prints to six figures. The alternative worth weighing is keeping
"Absolute error" instead, since it is the quantity the check holds against its
tolerance.

**Answered 2026-10-03** (project owner, 2026-10-03, ratified, over keeping both
residual lines and over keeping "Absolute error" in place of "Unaccounted"): show
the residual once, as "Unaccounted".

[superseded 2026-10-03: the answer above] **Done when.** The answer is recorded
beneath the question, and the panel shows what it decided, with a test pinning
the residual lines.

**Done when.** The accounting panel prints one residual line, "Unaccounted",
and no "Absolute error" line; `format_agent_residual`'s docstring no longer
speaks of two lines reading alike; the test pinning `Absolute error: <1e-12 L`
in `tests/unit/test_dashboard_frame.py` pins the single line instead; and a test
named `test_the_accounting_panel_prints_the_residual_once` asserts that no
residual is printed twice. The failure notice keeps its signed six-figure
values.
