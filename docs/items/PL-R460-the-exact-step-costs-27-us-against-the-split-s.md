---
id: PL-R460
title: The exact step costs 27 us against the split's 18 us per step at held settings, and 1.2 ms on every settings change
priority: P2
effort: M
status: done
classes: perf
feature: numerical-domain
milestone: v0.4.23
touches: src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/matrix_exponential.py, tests/unit/test_state_capture.py, tests/unit/test_matrix_exponential.py, tests/unit/test_governing_equations.py, docs/WORKING_NOTES.md
added: 2026-09-06
closed: 2026-09-14
pr: 556
verify: uv run pytest tests/unit/test_state_capture.py tests/unit/test_matrix_exponential.py tests/unit/test_governing_equations.py && grep -q '_propagator_cache_key' src/anesthesia_sim/core/uptake_system.py
not-delegable: the Done-when is a judgment on a profile rather than a pass/fail. Both outcomes - the per-step cost back under 18.4 us, or a measurement saying why it should not be - are read off timings against a figure measured on one machine, and a threshold assertion tight enough to discriminate would flake on any other. The change itself is to the propagator cache key in `core/`, which `protected_paths` withholds from delegation whatever proves it: that key is what makes a stale propagator unrepresentable rather than merely unlikely, so replacing it with a cheaper one is a safety-critical edit wearing a performance hat.
---

**Problem.** `PL-GS5X` predicted a speed-up and asked for a measurement rather
than an assumption. The measurement says the opposite. On this machine,
2026-09-06, `AgentUptakeSystem.advance(0.1)`:

| | Per step |
| --- | --- |
| Settings held (propagator cached) | 26.8 us |
| Any setting moved (propagator rebuilt) | 1200 us |
| The operator split it replaced | 18.4 us (`docs/WORKING_NOTES.md`) |

The item's expectation was that a cached propagator would make each step "one
7x7 matrix-vector product - 49 multiply-adds and no transcendentals, against
the five `exp()` calls the split makes every step". The matrix-vector product
is indeed cheap; what it does not cover is everything around it.

**Where the 27 us goes.** Profiled the same day:

```text
propagate()                 11.6 us   the 9x9 product itself
_propagator_for(0.1)         6.9 us   of which equation_settings() is 6.2
state_vector()               0.8 us
the rest                     ~7 us    capture_state, write-back, the result
```

`equation_settings()` builds four frozen dataclasses and runs about twenty
validation guards on every step, to produce the key the propagator cache is
compared against. That key exists for a good reason - keyed by value, a stale
propagator is unrepresentable rather than merely unlikely - but it is being
rebuilt at full cost to answer a question whose answer is "no" on all but a few
steps of a run. A raw tuple of floats read straight off the compartments would
answer the same question, with the validated settings constructed only when it
differs.

`propagate()` at 11.6 us for 81 multiply-adds is about 143 ns each, which is
Python rather than the algorithm.

**Why it matters, and why it is worth an item rather than a shrug.** Nothing today is too slow: at
60x playback the run loop takes 600 steps per 0.1 s tick, which is 16 ms of a
100 ms budget against 11 ms before. The 1.2 ms rebuild during a slider drag is
1.2% of a frame. What makes it worth recording is that `PL-T691` makes the run
a closed-form function of its control timeline and evaluates the propagator per
chart segment rather than per step, so the rebuild cost moves onto the frame
path - and `docs/WORKING_NOTES.md` line ~945 carries a 3.3 ms frame figure
measured against a *different* implementation (Pade-13) that should be
re-measured against this one before that design leans on it.

**Not a correctness question.** What the exact step bought is in
`docs/MODEL.md` § "Selected method (as implemented)": the solution rather than
a first-order approximation of it, mass balance closing at rounding, and a
propagator that cannot drive a compartment out of range. This item is about
what it cost.

**Done when.** Either the per-step cost at held settings is back at or below
the split's 18.4 us, or a measurement says why it should not be and the figures
above are corrected where they are quoted.

**Done 2026-09-14, on the second branch of the Done-when: the per-step cost is
down 27.7% but not under the split, and the figures are corrected where they
are quoted.**

**Measured, best of five, on the 2026-09-14 container.**
`SimulationState.advance(0.1)` at held settings: **33.98 us before, 24.56 us
after.** The two eras cannot be compared in absolute microseconds - this
container is slower than the machine of 2026-09-06 - so the figure to carry is
the ratio. The exact step was 1.46x the split there (26.8 against 18.4); at
0.723 of its former cost it is now about **1.06x the split**.

**Two changes, both of which the brief's own profile pointed at.**

- **The propagator cache key is a raw tuple of floats** read straight off the
  compartments, where it was the `UptakeEquationSettings` object.
  `equation_settings()` cost 7.2 us of the step to build four frozen
  dataclasses and run about twenty validation guards, on every step, to answer
  a question whose answer is "no" on all but a few steps of a run.
  `_propagator_for()` went from 8.2 us to 1.2 us.
- **`propagate()` sums each row with `map(mul, ...)`** rather than a generator
  over `range(size)`: 5.0 us against 8.5 us, bit-identical. This is in
  `core/matrix_exponential.py`, which this item's `touches` did not name and
  now does - the brief analysed the cost ("143 ns each, which is Python rather
  than the algorithm") without predicting the fix would land there.
  `strict=True` on the `map` was measured at a further 1.8 us and rejected: the
  lengths are established three lines above by `_require_square` and the state
  check, so it re-checks on every step of every run and can never fire.

**The safety property this item's `not-delegable` note names is what the tests
are for.** Replacing the key is "a safety-critical edit wearing a performance
hat": the settings object made a stale propagator unrepresentable *because* it
was the same object the matrix was built from, and a raw tuple gives that up
unless it is complete. Three tests hold it:

- `test_the_propagator_cache_key_covers_every_equation_setting` counts key
  entries against `dataclasses.fields()` of both settings classes, so a field
  added to the settings with no entry in the key fails rather than
  reintroducing the stale propagator.
- `test_moving_any_setting_moves_the_propagator_cache_key` moves each of the
  eleven, writing straight onto the compartment where no setter exists, which
  is the path with no guard of its own.
- `test_the_system_matrix_does_not_depend_on_a_tissue_group_s_name` holds the
  one settings field the key leaves out.

The guards did not stop running. They are skipped only where the key is
unchanged, which is where the values are the ones already validated when that
propagator was built; any change moves the key and the rebuild validates first.

**A property of `sum` turned out to be load-bearing and is now pinned.**
CPython's `sum` is Neumaier-compensated on floats, so the products
`1.0, 1e16, -1e16` sum to exactly 1.0 where a naive left fold gives 0.0. That
is *why* the two spellings are bit-identical rather than merely close - both
hand `sum` the same floats and the compensation makes the result independent of
how they were produced - and it is also why the obvious next step, an explicit
accumulator loop, would be faster and would not be the same function.
`test_propagate_sums_each_row_with_the_compensation_sum_provides` is what
stops that being discovered later.

**`docs/WORKING_NOTES.md` corrected in three places.** The 18.4 us step figure
is marked as the split's and given the before/after ratio; the second quote of
it is annotated; and the 3.3 ms frame figure the note itself asked to have
re-measured **is 7.64 ms**, or 14.13 ms across five inter-event segments. That
matters more than the per-step number: `PL-T691` was to lean on it, and 14 ms
of a 16.7 ms frame at 60 fps is not the headroom 3.3 ms implied. The per-column
cost is the smaller half once there is more than one segment, so the number to
design against is the segment count.

**Why the remaining 6% is not worth chasing here.** What the exact step buys is
in `docs/MODEL.md` § "Selected method (as implemented)" and this brief already
states it: the solution rather than a first-order approximation, mass balance
closing at rounding, and a propagator that cannot drive a compartment out of
range. Paying 6% for that is obviously right where paying 46% was worth an
item. The next reduction available is `propagate()`'s per-step guards at about
3 us, and those are deliberate and documented - trading them for speed in the
one function every step runs is the trade `CLAUDE.md` puts correctness above.
