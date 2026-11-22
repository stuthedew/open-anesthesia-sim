---
id: PL-P5W1
title: A copy of a run opened from a system whose amounts were written directly can be refused before its first step, because about one amount in eight does not survive the fraction round trip that the copy's check makes (found at blind review of PL-DQWL)
status: done
feature: replay-findings
milestone: v0.6.21
touches: src/anesthesia_sim/core/simulation.py, tests/unit/test_simulation.py
added: 2026-11-22
closed: 2026-11-22
pr: 2245
tests: tests/unit/test_simulation.py::test_a_run_opened_from_directly_written_amounts_copies_before_its_first_step
---

**Problem.** A copy of a run opened from a system whose amounts were written directly can be refused before its first step, because about one amount in eight does not survive the fraction round trip that the copy's check makes (found at blind review of PL-DQWL)

**Found by.** The first blind review pass on the second design of `PL-DQWL`,
2026-11-22. A run built with no opening record stores the fraction it reads,
amount divided by volume. Since `PL-HXNL`, a copy or a pickle rebuilds the run
through its constructor, which checks with `AgentUptakeSystem.stands_at` that
the system stands at that state. That check writes the fraction back, and for
about one amount in eight the product differs from the amount in the last bit,
so the copy is refused. Checked in this session: 36 of 300 random alveolar
amounts from 0.001 to 0.2 L, written directly with the accounting anchored to
match, were refused.

**Why it matters.** Only a direct write to a compartment's amount reaches it,
which no code in `src/` makes, and a trunk opens from an empty system whose
fractions are exactly 0. The refusal is the safe side.

**What was tried.** Placing the system at the stored state when the run opens
(`resume_at`) removed the refusal, but it writes through each compartment's
guard when the run is built, so a system that a test builds to fail inside a
step failed at construction instead
(`tests/unit/test_uptake_system_failure.py::test_simulation_time_does_not_advance_through_a_failed_step`).
A fix has to make the copy's check compare what the run itself last read
(`SimulationState._resting_state`) rather than writing a state into the system.

**What was built.** `SimulationState.__post_init__` now accepts an opening
record in either of two ways. The system's own reading of its state and its
compensation terms equals the record's last state and terms exactly, in which
case nothing is written. Otherwise `AgentUptakeSystem.stands_at` decides, as
before. A copy or a pickle rebuilds the run through that check, so a system
that reads back exactly what the run stored is accepted without the fraction
round trip. This is the comparison the brief asked for. It reads the system
rather than `_resting_state`, because a copy carries the record and the
system but rebuilds the field (`field(init=False)`), and an exact match of
the system's reading with the record's last entry is the same fact at the
copy's opening. A branch still goes through `stands_at`, since `resume_at`
has just written its state.

**Sources.** Researched after the merge, at the owner's question of
2026-11-22, and they support the design as built.

1. Goldberg, "What Every Computer Scientist Should Know About
   Floating-Point Arithmetic", ACM Computing Surveys, March 1991, read in
   full in Oracle's edited reprint
   (https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html) on
   2026-11-22. Theorem 7 proves that dividing and then multiplying by the
   same number returns the original only when both are integers and the
   divisor has the form 2^i + 2^j. An amount and a volume in litres are
   neither, so a check that divides and multiplies back cannot be exact in
   general. A sample of 10,000 random alveolar amounts (0.001 to 0.2 L) over
   random volumes (1 to 6 L) gave 9.7% that did not return to themselves,
   which matches the brief's one in eight. So the check compares what the
   system reads with what the run stored, which takes no arithmetic.
2. The Python standard library's `pickle` documentation
   (https://docs.python.org/3/library/pickle.html, read 2026-11-22), § "Pickling
   Class Instances". It says that `__init__` is usually not invoked when an
   instance is unpickled, and that a type relying on an invariant must
   establish it another way. `PL-HXNL` made a copy rebuild through the
   constructor for that reason. This item keeps that route and only makes
   its check exact.

**Regression test.** `tests/unit/test_simulation.py::test_a_run_opened_from_directly_written_amounts_copies_before_its_first_step`
copies and pickles runs opened from forty directly written alveolar amounts,
0.001 to 0.19 L, and steps each copy beside its run. Against
`src/anesthesia_sim/core/simulation.py` from `origin/main` 0a65c401 it fails,
for both the deepcopy and the pickle case, with
`SimulationConfigurationError: the uptake system does not stand at the state
the opening record stores for 0 s`. Command: `uv run pytest -q -p no:randomly
tests/unit/test_simulation.py -k directly_written`.

**Generator check.** The fact is which state a run's record holds for the
second it opened at, which the run-is-its-definition rule states. The check
that read it wrote the state back instead of reading it, which is the same
shape as `PL-MH9J`'s finding that a fraction read back from a compartment can
differ in the last bit from the one written. This item is a found gap in
`PL-HXNL`'s check, filed by review, and not a fix that failed to hold, so no
`reenters:` is recorded.

**Docs checked.** `docs/MODEL.md`, `docs/VERIFICATION.md`,
`docs/INTERFACE.md` and `docs/PARAMETERS.md` for the copy check
(`stands_at`, "copied or loaded"): none describes how a copy is checked, so
none changed. `.claude/rules/run-is-its-definition.md` § "Read a reached
second's state from the record" still applies unchanged.
