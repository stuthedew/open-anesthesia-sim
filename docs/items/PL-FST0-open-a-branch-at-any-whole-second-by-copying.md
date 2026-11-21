---
id: PL-FST0
title: Open a branch at any whole second by copying its parent's stored states up to that second
priority: P1
effort: M
status: done
classes: feature, safety
feature: run-computed-one-way
touches: src/anesthesia_sim/core, src/anesthesia_sim/app, tests, docs/INTERFACE.md
blocked-by: PL-MH9J
deferred-from: v0.7.0 - filed 2026-11-21, after the gate froze, as the build of the design the owner chose in PL-7CY5; each of the four pull requests leaves main releasable, so the release does not wait for the feature to finish
added: 2026-11-21
closed: 2026-11-21
pr: 2180
tests: tests/integration/controller/test_controller_stored_states.py::test_a_branch_repeats_its_trunks_delivered_and_exhausted_totals_for_nine_minutes
---

**Problem.** Open a branch at any whole second by copying its parent's stored states up to that second

**Why it matters.** A branch can open today only where the run's definition holds a keyframe, which three closed items worked around (`PL-B8MK`, `PL-W4XQ`, `PL-Y2SL`). The owner chose this design on 2026-11-21 in `PL-7CY5` (one rule for computing a run), which holds the counts, the measurements and the sources. The four items of the feature `run-computed-one-way` are built in this order: `PL-SZ6G`, `PL-MH9J`, `PL-FST0`, `PL-Z6C8`.

**What it changes.** A branch opened at second n holds its parent's stored states for seconds 0 to n and steps on from there. A learner can branch at any whole second of a run.

**Done when.** A branch opens at any whole second, and a test shows that the branch's stored states equal its parent's, bit for bit, up to and including that second.

**Generator check.** Work the owner asked for on 2026-11-21, building the design that `PL-7CY5` decided. It is a one-off and not a head: the limit on where a branch opens came from the keyframes, which the stored states replace.

**Built, 2026-11-21.** On the thread's branch, in pull request #2180, after `PL-MH9J`.

**What a branch holds.** A branch's record of stored states is a copy of its parent's record up to and including the fork (`StoredStates.through`), and the branch's steps append to the copy. The branch's record therefore opens at the same second as its parent's, which is 0 for a case. `SimulationState` takes the record as `opening_record` and keeps a copy of it. It accepts the record only where the record ends at the run's clock and the uptake system stands exactly at the record's last state (`AgentUptakeSystem.stands_at`).

**Where a branch opens.** `SimulationController.resumed_at` opens a branch at any whole second the run has reached. It refuses a second the run has not reached, with the record's own message, and the supported run length, as before. The interface is unchanged: it offers the control events, the passed marks and the place where a paused run stands. A learner already reaches any other whole second by marking it or pausing on it, so no control was added (decided in the session, as a placement choice).

**What a branch draws.** A branch's chart still starts at its fork (`began_at_s`), and a reset still returns the branch to its fork. The branch holds the earlier states and does not draw them. Drawing the parent's stretch on the branch's chart would change what a learner sees, and the design round did not ask for it.

**A branch repeats its parent's delivered and exhausted totals bit for bit.** Each total is a running sum kept by compensated summation, and the validator carries a compensation term from each addition to the next (`core/agent_simulation_validation.py`). A stored state held the totals and not the terms, so a branch started its terms at zero and its next additions could round differently. The record now stores the two terms beside each second's state, as a `TotalsCompensation`, and `AgentUptakeSystem.resume_at` takes them. Measured on the code before the change, 2026-11-21, with `/mnt/project-files/release-trajectory/branch_totals_probe.py`: on a default run of 1 800 s, a branch at 600 s with zero terms stored a state that differed from its parent's at 245 of the next 1 200 seconds, and a branch at 60 s at 154 of the next 1 740. With the stored terms, no second differed for any of the seven forks tried. The accounting panel shows each total to 0.1 L of vapour. Whether a last-bit difference ever changed a displayed value was not measured.

Two other routes to equal totals were weighed and not taken:

1. Summing the totals without compensation. It would change the mass-balance residuals and the section of `docs/MODEL.md` that states them, which is outside this item.
2. Restarting each total as a fresh compensated sum at the fork. It is not exact: the measurement above is this route.

**`ResumePoint` no longer carries the state one second before the fork.** The branch reads it from its own record, which now holds it. `ResumePoint` holds no record, so two resume points still compare equal by value.

**Tests, and how they fail on the code before the change.** The expected states in each are stepped in `core/` with no branch taken.

- `PYTHONPATH=<archive of 46f3d3ead>/src .venv/bin/python -m pytest tests/integration/controller/test_controller_stored_states.py -k "any_whole_second or no_setting_moved or reset_branch or two_branches or reached_its_fork"`: 25 of 28 fail. Each fork that is not a setting change fails with "this run holds no keyframe at 96 s, and resumed_at opens at one", and each fork at a setting change fails with `assert 95 == 0`, the second its record opened at. The three that pass are `no_setting_moved` at seconds 40, 95 and 120, where a branch could open before and its totals did not differ over the few seconds stepped.
- `-k nine_minutes` is the variant that needs nothing this item added. It fails there with `assert [63, 64, 65, 66, 67, 71, ...] == []`: a total that the branch showed differed from the stepped total at 62 of 540 seconds.

**Costs, measured 2026-11-21** with `/mnt/project-files/release-trajectory/branch_open_cost.py`, while the test suite was running on the same machine. Opening a branch from a twelve-hour trunk took 0.9 ms at 60 s, 2.3 ms at 6 h and 3.3 ms at 12 h. A branch at 12 h holds 3.8 MB of stored states and terms. A 24-hour record holds 6.2 MB of states and 1.4 MB of terms.

**Left for the documents pass.** `docs/INTERFACE.md` and `docs/ARCHITECTURE.md` still say that a branch opens at a keyframe, a mark or a pause, and that it stores its parent's state at the fork as its first.

**Left for `PL-Z6C8`.** `test_resume_at.py` and about 30 other callers place a system with `resume_at` at a state the run definition computed by formula, with the default terms of zero. They go with the evaluation paths. The validator's docstring still describes the 1 ms step floor.

**Closed 2026-11-21.** The documents pass this brief left was done in `PL-Z6C8`, and a branch's readouts are now required to equal its parent's exactly (`test_a_branch_steps_to_where_its_parent_stepped`).

**Documents checked, 2026-11-21, after `PL-Z6C8`.** `docs/INTERFACE.md` § "Halting on a marked crossing", § "A run stores the state of every second it reaches", § "Each second has one stored state", § "The shared history is identical by construction, not by measurement", § "What the chart draws" and § "A preview of an unapplied setting"; `docs/MODEL.md` § "The reproducibility guarantee", § "Supported simulation step", § "Supported input ranges", § "The numerical envelope", § "How far a computed value can be from the exact one", § "Step-refinement test", § "Prediction agreement test" and § "Stored-state test"; `docs/ARCHITECTURE.md`'s package map and its sections on the run record and on branching; `ROADMAP.md`'s item 12 entry; `.claude/rules/run-is-its-definition.md`. The remaining passages that `PL-5FMC` listed for this build are `PL-LZ54`'s.
