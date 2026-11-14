---
id: PL-FCYQ
title: No test replays a recorded control-input timeline into a fresh run and compares the two, though docs/MODEL.md § The control-input timeline requires that the replay reproduces the run
priority: P1
effort: M
status: done
classes: test, safety
feature: tests-detect-wrong-values
touches: tests/integration/test_control_timeline_replay.py
deferred-from: v0.7.0 - not live: checked 2026-11-09: all four control setters in app/controller.py go through _change_setting, which records each accepted change, so no learner sees a setting the timeline left out now; the test guards the next path that might not
added: 2026-11-05
closed: 2026-11-11
pr: 2139
payoff: a setting that changes the curves without a mark on the chart fails a test, so a learner can trust that the marks name every input behind the curves
verify: grep -q 'def test_the_recorded_timeline_reproduces_the_run_step_for_step' tests/integration/test_control_timeline_replay.py
---

**Problem.** No test replays a recorded control-input timeline into a fresh run and compares the two, though docs/MODEL.md § The control-input timeline requires that the replay reproduces the run

**Checked 2026-11-09:** `grep -rn -i "replay" tests` finds no test that applies a run's recorded control timeline to a fresh run and compares the two. `test_identical_runs_produce_identical_snapshots` in `tests/integration/test_sevo_controller.py` runs one hand-written script twice. `_replayed_from_provenance` in `tests/integration/test_controller.py` rebuilds a branch's settings, not its states. Each property of the record has its own test (time stamps, refused settings, unchanged settings, drags), but nothing tests that together they reproduce the run.

**Why it matters.** The chart marks and the change list tell a learner which settings produced the curves they are reading, and `docs/MODEL.md` § "The control-input timeline" rests that claim on the replay. A setting applied by a path that does not record it would change the curves with no mark on the chart. The learner would then read a change in the patient where the cause was an input, and no test would fail. That makes the missing test a gap in a safety-critical display, so it is classed `safety`.

**Done when.** A test runs a case that changes each of the four controls, including a drag over several steps and a refused setting. It then builds a fresh run from the same start, applies each recorded change at its recorded instant, and compares the two runs' states element for element at every step. The fresh run is built without the original run's objects, as `.claude/rules/test-oracles.md` rule 2 asks.

**Generator check.** One-off: a requirement in `docs/MODEL.md` with no test of its own. The fact is whether the control timeline holds every setting the model ran under; no head states it.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Present. At 817a4d88, `docs/MODEL.md` already required that the timeline, "re-applied to a fresh run at the recorded times, must reproduce" the run. The only replay test in `tests/integration/test_controller.py` was `test_a_branch_inherits_its_parent_s_settings_at_the_fork`, which checks a branch's settings and not the run's states. So the item belongs on v0.7.0's frozen list. It is deferred from there on the not-live terms recorded in `deferred-from`.

**Built 2026-11-11.** `tests/integration/test_control_timeline_replay.py` drives a controller through 1,505 steps of sevoflurane. The case sets the dial before Start, drags the fresh gas flow from 5 to 1 L/min over five consecutive steps, moves the dial twice inside one step, moves the cardiac output and back inside one step, offers a 9% setting that the 8% vaporizer refuses, and changes the alveolar ventilation and the cardiac output. The fresh run is an `AgentUptakeSystem` built for the same agent, with nothing taken from the controller. Each recorded change is applied through the core's own setter at the instant the run's clock defines (steps taken times the step), and the two state vectors must be equal after every step. The arithmetic is identical on both sides, so the comparison is exact. A second test leaves each recorded change out in turn and shows that the replay then differs, so every entry in the case acts on the states.

The test is in a file of its own, not in `tests/integration/test_controller.py`, because another branch (`claude/epic-archimedes-vmpesj`) is editing that file. This is a new test of behaviour that already holds, so there is no code before a fix to run it against. As a check that it catches the defect it names, a probe that made the controller skip recording the cardiac output change at 120.5 s turned the comparison false (`fcyq_probe.py`, run by hand, not kept).

**Blind review, one pass: one should-fix and one optional finding, both fixed.** The should-fix: the replay started from the core's defaults, which is right only for a run that was never reset. Reset keeps a run's settings and clears its timeline, so the run after a Reset opens under settings the timeline does not hold. The case now changes two settings, runs, and presses Reset before its recorded run starts, and the fresh run opens under the settings the run opened under, read from `controller.settings()` at that moment. A probe that replays from the defaults instead now fails the comparison. The optional finding: the replay never checked each change's "from" value, which the change list shows the learner. It now asserts, before each change, that the value in force in the fresh run equals the change's `previous_value`, and a probe that alters one entry's `previous_value` is caught.
