---
id: PL-GJ1W
title: Nothing states in one place how far a computed value in core/ or app/ can be from the exact one, so each comparison picks its own allowance (13 tolerance constants, and none where nobody thought of rounding) and no test runs generated settings over many steps: seven items from 2026-10-25 to 2026-11-01 on error that accumulates or a rounded result compared exactly
priority: P1
effort: L
status: needs-decision
classes: safety
feature: numbers-outside-their-valid-range
touches: src/anesthesia_sim/core, tests/unit, docs/MODEL.md
deferred-from: v0.7.0 - filed 2026-11-11, after the gate froze; a large structural change whose design waits on the owner's answer
added: 2026-11-11
payoff: a learner is not shown a run that halts, a trend labelled the wrong way or two readings that disagree because of rounding in the last digits
root-cause-of: PL-D88N, PL-XST1, PL-9B1M, PL-81Q2, PL-N559, PL-9SL5, PL-QVBR
generator: live - each of the seven was fixed at its own comparison with its own allowance, and nothing states the rounding a computed value carries or tests generated settings over many steps, so the next exact comparison of a rounded result is found by a reviewer
misread: How far a computed value can be from the exact one, and so what a comparison on it proves
---

**Problem.** Nothing states in one place how far a computed value in core/ or app/ can be from the exact one, so each comparison picks its own allowance (13 tolerance constants, and none where nobody thought of rounding) and no test runs generated settings over many steps: seven items from 2026-10-25 to 2026-11-01 on error that accumulates or a rounded result compared exactly

**The seven members, and what each fix built** (read from each item on
2026-11-11).

| Item | What went wrong | Fixed by | Found by |
| --- | --- | --- | --- |
| `PL-XST1` | Plain `+=` over 8.64e7 steps drifted the accounting totals to 1.0e-9, 2.4% short of a false halt at 18.96 h | Kahan summation | An estimate from reading the code |
| `PL-D88N` | The fixed 1e-9 accounting tolerance halts a run at the stiffest envelope corners in 4.3 s, on rounding the propagator's own bound allows | Kept fixed, documented, and a test that shipped settings need zero squarings | A blind review |
| `PL-9B1M` | One step from a full state rounds a fraction up to 3.5e-11 past 1 and is refused; the display path drew 1.000033 | An input ceiling of 0.99 | The envelope sweep |
| `PL-81Q2` | 59 chained 32-squaring propagators accumulate 3.3e-5 on the display path | Measured, no change | A review of `PL-9B1M` |
| `PL-N559` | At zero cardiac output F_A settles a few units in the last place above F_I, and an exact `> 1.0` labelled the steady state as elimination | `WASH_IN_ROUNDING_ALLOWANCE = 1e-6` | A reviewer replay |
| `PL-9SL5` | `start_s + column * spacing_s` put the last column one rounding unit past `stop_s` in about one window in forty | Pin the last column | A reviewer replay |
| `PL-QVBR` | The stepped and canonical readings of one step differ by about 1e-14, so a MAC target decided by exact comparison read reached on the trunk and not on its branch | `HEIGHT_BAND = 1e-5` and `LIVE_READING_GAP = 1e-6` | A lifecycle review |

**The cause.** A computed value differs from the exact one by rounding, and
the difference grows with the number of operations behind it. Nothing in the
tree states that difference in one place. `core/matrix_exponential.py` states
it for one propagator (2**s times machine epsilon after s squarings), and
`docs/MODEL.md` states 4.9e-14 between the stepped and canonical readings.
Every comparison that has to allow for it picked its own number:
`src/anesthesia_sim/` defines 13 tolerance constants, six of them 1e-9 and
three 1e-12, each beside its own use. A comparison where nobody thought of
rounding has no allowance at all, which is `PL-N559`, `PL-9SL5` and `PL-QVBR`.

No test exercises this. The mass-balance check runs on every step of a real
run, which is why three of the seven surfaced as a halt and not as a wrong
value. But the tests step from listed settings, mostly once. The envelope
sweep steps once from each of 96 corners. No test draws settings across the
ranges, changes them during a run, steps thousands of times, and asserts what
must hold after every step.

This is a second cause, separate from `PL-LHCL`'s. `PL-LHCL` is about a
number that came in outside its range. Every input here was inside its range.

**Why it matters.** A learner reads the label "elimination", the word
"reached" and the last column of a chart. Each of these was wrong, or halted
a correct run, because of rounding in the last digits.

**Decision needed.** The design below, put to the project owner on 2026-11-11.
**Recommended: take it.** It is the owner's because it changes the allowance
of comparisons a learner's readings depend on, and adds test time to every
run of the suite.

1. One module in `core/` states the rounding a computed value can carry: for
   one propagator, for one step, and for a run of n steps. Every allowance in
   `core/` and `app/` that exists because of rounding is computed from it, and
   the 13 separate constants go.
2. A generated test draws settings across the supported ranges and at their
   edges, changes them during a run, steps thousands of times, and asserts
   after every action what must always hold: the agent balance closes; every
   fraction stays between the lowest and highest of the opening state and the
   delivered concentration; the stepped and canonical readings agree; two
   routes to one instant agree; the same actions replayed give the same bits.
   Each assertion allows the rounding that the module in 1 states, and no
   more.
3. A weekly job runs the full 24 h at the 1 ms step floor, which is 8.64e7
   steps and too long for every commit.

**What could still get past it.** A property nobody stated. A threshold that
a computed value lands on exactly, unless the test draws its thresholds from
the run's own readings. Growth that appears only past the length a per-commit
test can run, which is what the weekly job and the stated bound are for.

**Done when.** The module in 1 exists and each rounding allowance reads it.
The generated test in 2 exists, and each of the seven members is replayed
against it with its fix reverted, with the result recorded here per member.
The weekly job in 3 runs. `docs/MODEL.md` states the bounds.

**Generator check.** This is a head. No other head's `misread:` states the
fact. `PL-58D7`'s fact is the input domain of an operation, and three of the
seven members were filed under it.
