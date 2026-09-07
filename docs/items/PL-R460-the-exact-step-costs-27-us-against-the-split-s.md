---
id: PL-R460
title: The exact step costs 27 us against the split's 18 us per step at held settings, and 1.2 ms on every settings change
priority: P2
effort: M
status: ready
classes: perf
feature: numerical-domain
touches: src/anesthesia_sim/core/uptake_system.py, docs/WORKING_NOTES.md
added: 2026-09-06
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
