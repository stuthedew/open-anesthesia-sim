---
id: PL-ZH1F
title: RunDefinition.record_change's dial-moved-back branch is tested only on two-segment runs, the one size where segments[:-1] and segments[:1] agree, so a mutant that silently deletes every later stretch (state_at 600 s alveolar 0.01246 against 0.01867) survives all 5734 simulator tests
priority: P1
effort: S
status: ready
classes: safety, test
feature: tests-detect-wrong-values
touches: tests/unit/test_run_definition.py
added: 2026-10-17
payoff: a dial moved and moved back within one step can no longer delete the earlier stretches of a run without a test failing, so the chart trace and branch states stay computed under the settings the case was under
verify: grep -q 'def test_a_change_undone_at_one_instant_keeps_every_earlier_stretch' tests/unit/test_run_definition.py
---

**Problem.** RunDefinition.record_change's dial-moved-back branch is tested only on two-segment runs, the one size where segments[:-1] and segments[:1] agree, so a mutant that silently deletes every later stretch (state_at 600 s alveolar 0.01246 against 0.01867) survives all 5734 simulator tests

**Severity: safety, as a test gap.** The code is correct today. What is
missing is the test that would fail if it regressed. Audit finding
`record_change__mutmut_13`, a real-gap mutant confirmed against the whole
suite.

**Evidence.** The mutant changes `self._segments = self._segments[:-1]` to
`self._segments[:+1]` in `RunDefinition.record_change`
(`src/anesthesia_sim/core/run_definition.py`). That line is in the branch
that drops a stretch when a second change at an instant already opened
returns to the previous stretch's settings: "a dial moved and moved back
before a step ran". The mutant survived the 33 unit files, then the whole
simulator suite at `25ef454b` (`uv run pytest -q -x -n 2 -p no:cacheprovider
tests/unit tests/integration tests/reference`: 5734 passed, 588 s, exit 0).

The branch has two tests:
`test_a_change_undone_before_a_step_runs_leaves_no_segment` in
`tests/unit/test_run_definition.py`, and
`test_a_change_undone_within_one_step_leaves_no_entry` in
`tests/integration/test_controller.py`. Both use exactly two segments. With
two segments, `[:-1]` and `[:1]` give the same result.

Distinguishing input, sevoflurane: the run opens at 0 s under 2%; at 10 s the
dial is set to 3%; at 20 s it is set to 5% and then back to 3% before a step
runs. The shipped code keeps the segments [(0 s, 2%), (10 s, 3%)]. The mutant
keeps only [(0 s, 2%)]. `state_at(600 s)` then gives an alveolar fraction of
0.01246 under the mutant against 0.01867 shipped. A script with two
dial-moved-back events gave opening instants [0, 40] against [0, 10, 20].

**Why it matters.** The controller calls `record_change` on every accepted
change, in `SimulationController._record_control_change`, including while the
run is paused. So dragging a dial past a value and back within one step takes
this branch. If the branch regressed this way, every stretch after the first
would vanish without a sign. The chart trace (`evaluate_anchored`), the states
that branches fork from, the before-and-after MAC multiples and later
keyframes would all be computed under settings the case was never under. The
trace would disagree with the readouts, and nothing would fail or warn.

**Where.** `src/anesthesia_sim/core/run_definition.py` (`record_change`);
`tests/unit/test_run_definition.py`.

**Recommended test.** In `tests/unit/test_run_definition.py`, build three
stretches (0 s at 2%, 10 s at 3%, 20 s at 5%), then record 3% again at the
same 20 s instant. Assert
`[(s.opening.instant_s, s.settings.delivered_concentration_percent) for s in definition.segments] == [(0.0, 2.0), (10.0, 3.0)]`.
The expected value is a literal taken from the docstring's rule that "the
stretch goes entirely". The audit wrote and checked this test (as
`test_k_rc13_a_change_undone_at_one_instant_keeps_every_earlier_stretch`): it
fails on the mutant and passes on the shipped code. Name it in the file's own
style. The general lesson from the triage: a rule about a record or a
collection needs a test with three or more entries.

**Done when.** A test of the dial-moved-back branch on a run of three or more
segments fails under the `[:+1]` mutant and passes on the shipped code.

**Related.** `PL-ZLNN` (ready) adds seeded random multi-control trajectories.
As written it would not catch this. It drives `AgentUptakeSystem` and asserts
conservation, range and no exception, and it never touches `RunDefinition`.
The audit's random differential probe did hit this mutant, because it drove
`RunDefinition` and compared `state_at` with the live run at the same
instants. Adding that comparison to `PL-ZLNN` would catch this whole class,
not just this instance. `PL-HWNG` (ready) has the same shape, a fixture with
too few changes, in `_two_change_run`.

**Provenance.** A read-only test-effectiveness audit on 2026-10-17 found this.
The audit ran mutation testing with mutmut 3.8.0 over `core/` and four
presentation modules against the 33 simulator unit-test files (at
`b9b3c812`). It ran each real-gap survivor against the whole 5734-test
simulator suite (at `25ef454b`). It also used fault injection, stored-value
perturbation, oracle classification and regression-test replay, and an
adversarial second agent verified each finding. Its scratch files are not
durable, so the evidence is written out above. Symbols re-checked against
`9ea87a3c`.
