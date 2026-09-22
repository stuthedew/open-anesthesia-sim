---
id: PL-BMY5
title: SimulationState can be constructed already past the supported run length, and only the next advance refuses it
priority: P2
effort: S
status: ready
classes: defect
feature: numerical-domain
touches: src/anesthesia_sim/core/simulation.py, tests/unit/test_simulation.py
added: 2026-09-14
verify: grep -q 'def test_a_state_past_the_supported_run_length_is_refused_at_construction' tests/unit/test_simulation.py && uv run pytest tests/unit/test_simulation.py
---

**Problem.** SimulationState can be constructed already past the supported run length, and only the next advance refuses it

**Measured 2026-09-14.** `SimulationState(step_count=1_000_000,
simulation_step_s=0.1)` constructs without complaint and reports
`elapsed_s` of 100 000 s - 27.8 h, past the 24 h
`MAXIMUM_ELAPSED_SIMULATION_TIME_S`. Only the *next* `advance()` refuses, with
`SimulationDomainLimitError`.

**Why it is not caught.** `__post_init__` runs `_require_step_count` and
`require_supported_simulation_step`, and neither knows about the run length;
`require_supported_run_length` is reached only from `advance()`, which asks
whether there is room for one *more* step. So a state handed a count that is
already outside the envelope is accepted, and everything that reads it - a
snapshot, a readout, a chart axis - presents it as an ordinary run until
somebody tries to step it.

**Why it matters more than it used to.** Nothing in `src/` constructs a
mid-run `SimulationState` today, so this is currently reachable only from a
test. `PL-J2TD`'s fork is the first thing that would: if a branch continues its
parent's step count - one of the two clock arrangements put to the project
owner on 2026-09-14 - then a branch is *always* constructed mid-run, and this
is the natural place to refuse one taken past the envelope.

**The fix is one line**, and it is the stance `core/supported_ranges.py` takes
everywhere else - refused rather than clamped: call
`require_supported_run_length(step_count, simulation_step_s)` from
`__post_init__` where the step is known. It needs the boundary case thought
through, since a run standing *exactly* at the cap is a legal state to be in
and an illegal one to step from, and `require_supported_run_length` is written
for the second question.

**Verified 2026-09-14.** `SimulationState.__post_init__`
(`core/simulation.py:68-77`) calls `_require_step_count` - whole and nonnegative -
and `require_supported_simulation_step`, and does **not** call
`require_supported_run_length`. That guard is reached only on the advancing
path, at `core/simulation.py:130`. So a state carrying a `step_count` whose
implied elapsed time is past the supported run length constructs cleanly and is
refused only by the next advance.

**Why it matters.** The same argument as `PL-73ZN` one level down, and it
matters more here because `SimulationState` is what a branch is *opened at*: a
fork resumes into a canonical keyframe state, so a state accepted at
construction is a state a branch can be built on. `CLAUDE.md` asks for ranges
and model applicability to be validated before calculation; this validates them
one operation late.

**Why not `safety`.** As with `PL-73ZN`, the advance refuses before any state is
produced or displayed, so the failure is a late error rather than a plausible
wrong value. Do these two in one branch - they are one rule applied at two
levels, and splitting them across sessions means writing the same argument
twice.

**Done when.** `SimulationState.__post_init__` refuses a `step_count` and
`simulation_step_s` pair whose implied elapsed time exceeds the supported run
length, using `require_supported_run_length` rather than a restated bound, and
`tests/unit/test_simulation.py` covers construction at and just past the edge.
