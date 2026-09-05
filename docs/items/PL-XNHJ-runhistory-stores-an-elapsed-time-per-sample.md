---
id: PL-XNHJ
title: RunHistory stores an elapsed time per sample that is an affine function of the sample index for every live run
priority: P3
effort: S
status: ready
classes: perf
feature: teachable-case
touches: src/anesthesia_sim/app/controller.py, tests/unit/test_run_history.py
added: 2026-09-05
verify: uv run pytest tests/unit/test_run_history.py && grep -q 'def test_elapsed_times_of_a_uniform_run_are_not_stored' tests/unit/test_run_history.py
---

**Problem.** `RunHistory._elapsed_s` is an `array("d")` holding one
recorded time per sample. For every *live* run those times are
`(index + k) * simulation_step_s`: `SimulationState.elapsed_s` is
`step_count * simulation_step_s` ("one multiplication, rounded once"), the step
is fixed for a run's whole length, and `record` is called once per `advance()`.
So the array stores an affine function of its own index.

**Why it matters.** Measured 2026-09-05 under `PL-8GLL`: the array is 8.0 B of
the 127.9 B a sample retains, about 6%. Small on its own, and worth recording
because `PL-011` (bound the controller's concentration history) is deciding a
retention policy against that per-sample figure, and this is the one component
of it that is pure redundancy rather than data.

**Where.** `app/controller.py` - `RunHistory.__init__`, `record`, `elapsed_s`,
`times_s`.

**The catch, which is why this is not a straight deletion.** `RunHistory.of`
builds a history from arbitrary recorded samples for tests and for a caller
replaying a stored run, and `record` requires only that a sample's time not
precede the previous one. So uniform spacing is a property of a live run, not
of the class. `times_s()` also hands the array out as a `Sequence[float]` that
callers `bisect` over, so a replacement has to be indexable and length-bearing
rather than merely iterable - which a small computed sequence satisfies.

**Done when.** Either the elapsed times of a uniformly-sampled run are computed
rather than stored, with the general case still accepted, or the redundancy is
recorded as a deliberate choice with its 8 B/sample cost stated.

**Which branch closes it.** The `verify:` command proves the first: the
elapsed times are computed and `tests/unit/test_run_history.py` still holds the
general case. If the measurement argues for keeping the array, that is
`status: dropped` carrying the 8 B/sample cost in `reason:`, which is where this
store records a deliberate no - not a `done` with nothing changed.

**Found.** Measuring per-sample retention for `PL-8GLL`, 2026-09-05.
