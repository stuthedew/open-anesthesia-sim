---
id: PL-ZLNN
title: No test drives a trajectory where several controls change at moments nobody scripted
priority: P2
effort: M
status: ready
classes: test
feature: numerical-domain
touches: tests/reference/test_coupled_dynamics.py
added: 2026-09-03
verify: uv run pytest 'tests/reference/test_coupled_dynamics.py::test_lockstep_oracle_step_matches_the_pinned_one' && grep -q 'def test_a_randomised_trajectory_stays_conservative_and_in_range' tests/reference/test_coupled_dynamics.py
---

**Problem.** Every gate in `tests/reference/` drives a fixed script. The
envelope gates hold one `OperatingPoint` for a whole run;
`SETTING_CHANGE_SCENARIOS` turns the controls once, at a moment chosen by the
author, on two hand-designed trajectories. Between them they cover runs in
which nobody moves a slider and runs in which somebody moves them once, in a
pattern someone thought of.

A user moves four sliders repeatedly, in combinations nobody enumerated. That
class of trajectory is driven by no test.

**Why it matters, and what it is not.** Measured 2026-09-03: 200 randomised
runs of 20 simulated minutes each - 66 simulated hours, each control moved to
a random supported value roughly every 10 s, across all three agents - produced
zero failures. Worst accounting residual 1.76e-13 relative, against a guard
that trips at 1e-9; no fraction outside [0, 1]; no halt. So this is **not** a
defect report: the model is robust over exactly the trajectories it is not
tested on, which is the good outcome and the reason this is P2 and classed
`test` alone.

What it costs is that the robustness is unattested. `AgentUptakeSystem.advance()`
can raise `SimulationNumericalError` and halt a run, `_advance_step()` applies
five sub-exchanges whose guards can each reject a value the step itself
produced, and the argument that none of them fires in ordinary use currently
rests on two scripted trajectories plus the reasoning in
`uptake_system.py`'s comments. A regression that made some slider combination
halt a run - which the user sees as the simulation stopping mid-case - would
be found by a user rather than by CI.

The probe also cost almost nothing: 2.4 million steps in well under a minute,
because the core runs at roughly 70,000 steps/s. A gate a hundredth that size
still covers the trajectory class.

**Where.** `tests/reference/test_coupled_dynamics.py`
(`SETTING_CHANGE_SCENARIOS`, `ALL_GATE_TRAJECTORIES`).

**Approach.** A seeded randomised trajectory test alongside the existing gates.
Fix the seed so the run is reproducible and `CLAUDE.md`'s determinism
requirement holds; assert what is invariant rather than what is exact -
accounting passes, every fraction finite and in [0, 1], no raise, simulation
time advances by exactly the steps taken. Keep it to a few simulated minutes
per agent so it stays inside the suite's 86 s.

**Prefer the standard library to a new dependency, but say why in the test.**
Hypothesis is the better tool for this and would shrink a failing case to a
minimal one, which is most of the value of property-based testing. Against it:
it is a new dependency on a project whose `drift.yml` exists because
dependencies are a multi-year liability, and a seeded `random.Random` covers
the trajectory class without one. Recommend the standard library first and
revisit if a failure ever needs shrinking - but record the trade in the test's
docstring rather than leaving a later reader to assume nobody considered it.

**Done when.** A seeded test drives several controls to random supported values
at random moments over a multi-minute run for each agent, and asserts
conservation, range and non-raising throughout.
