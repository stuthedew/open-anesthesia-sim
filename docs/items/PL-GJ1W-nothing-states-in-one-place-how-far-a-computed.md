---
id: PL-GJ1W
title: Nothing states in one place how far a computed value in core/ or app/ can be from the exact one, so each comparison picks its own allowance (13 tolerance constants, and none where nobody thought of rounding) and no test runs generated settings over many steps: seven items from 2026-10-25 to 2026-11-01 on error that accumulates or a rounded result compared exactly
priority: P1
effort: L
status: ready
classes: safety
feature: numbers-outside-their-valid-range
touches: src/anesthesia_sim/core, tests/unit, docs/MODEL.md
deferred-from: v0.7.0 - filed 2026-11-11, after the gate froze; a large structural change whose design waits on the owner's answer
added: 2026-11-11
payoff: a learner is not shown a run that halts, a trend labelled the wrong way or two readings that disagree because of rounding in the last digits
not-delegable: a root cause built in several pull requests that change core/ signatures or comparison allowances, each read by the project owner, and run at extra-high effort
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

**Decided 2026-11-11: build the design below** (project owner, 2026-11-11,
ratified, over building the range part alone and over building neither).
It was the owner's because it changes the allowance of comparisons a learner's readings depend on, and adds test time to every run of the suite.

1. One module in `core/` states the rounding a computed value can carry: for
   one propagator, for one step, and for a run of n steps. Each figure is
   either a bound that is tight enough to use, as the propagator's 2**s times
   machine epsilon is, or a measurement with its margin and a test that
   measures it again. A worst-case bound summed over every step is not used:
   `PL-D88N` measured it 58 times looser than the 1e-9 it would replace.
   Every allowance in `core/` and `app/` that exists because of rounding
   reads this module, and the 13 separate constants go.
2. A generated test draws settings across the supported ranges and at their
   edges, changes them during a run, and steps thousands of times inside one
   action. It asserts after every action what must always hold: the agent
   balance closes; every fraction stays between the lowest and highest of the
   opening state and the delivered concentration; the stepped and canonical
   readings agree; two routes to one instant agree; the same actions replayed
   give the same bits. Between setting changes the system is linear with a
   known exact solution, so the test also compares the state with the
   50-digit reference that `tests/unit/test_numerical_envelope.py` already
   has. Each assertion allows the rounding that the module in 1 states, and
   no more. The test steers its draws toward the largest residual, with
   Hypothesis's `target`.
3. A weekly job runs the full 24 h at the 1 ms step floor, which is 8.64e7
   steps and too long for every commit.

**What could still get past it.** A property nobody stated. A threshold that
a computed value lands on exactly, unless the test draws its thresholds from
the run's own readings. Growth that appears only past the length a per-commit
test can run, which is what the weekly job and the stated bound are for.

**Established practice, read 2026-11-11.** A background reader opened each
source below and quoted it; two quotes were checked against the downloaded
text. The session's network refused the publishers of Oberkampf and Roy 2010,
Roache 2002, Salari and Knupp 2000, ASME V&V 40, the FDA's 2023 guidance and
Higham 2002, so none of those was read and nothing here rests on them.

- Verification standards separate finding errors in the code from estimating
  the error of one calculation, and list round-off under the second, apart
  from discretization error (Anderson AE, Ellis BJ, Weiss JA. Comput Methods
  Biomech Biomed Engin 2007;10(3):171-184, doi:10.1080/10255840601160484,
  section 4.1; Galappaththige S et al. PLoS Comput Biol 2022,
  doi:10.1371/journal.pcbi.1010541). Code verification ranks an exact
  analytical solution first as the thing to compare against (Anderson,
  section 4.2.1). That is design part 2's 50-digit reference.
- A tolerance needs a source: "consider them equal if they are within some
  error bound E ... raises as many questions as it answers. What should the
  value of E be?" (Goldberg D. ACM Comput Surv 1991;23(1):5-48,
  doi:10.1145/103162.103163, p. 28). A tighter tolerance in a test finds more
  faults (Kelly, cited in Kanewala U, Bieman JM. Inf Softw Technol
  2014;56(10):1219-1232, arXiv:1804.01954, section 3.3).
- A worst-case rounding bound is pessimistic, and replacing its
  size-dependent constants by their square roots is the stated rule of thumb
  (Croci M et al. R Soc Open Sci 2022;9:211631, doi:10.1098/rsos.211631,
  section 6.1). Unbiased rounding grows as the square root of the number of
  steps in a billion-step integration, and compensated summation cuts it by
  one to two orders of magnitude (Rein H, Spiegel DS. MNRAS
  2015;446(2):1424-1437, arXiv:1409.4779). That matches what `PL-D88N` and
  `PL-XST1` measured here, and it is why part 1 measures run-length growth.
- Carrying an interval with every value was weighed and refused: "the bounds
  can blow up catastrophically" (Johansson F. IEEE Trans Comput
  2017;66(8):1281-1292, arXiv:1611.02831, section 1; Goldberg p. 27).
- Generated tests have stated limits. Random generation "is not especially
  good at satisfying difficult properties" (MacIver DR et al. J Open Source
  Softw 2019;4(43):1891, doi:10.21105/joss.01891). A stateful Hypothesis test
  runs 50 actions by default, so a defect that needs millions of steps is out
  of its reach, which is what part 3 is for. A relation checked this way is a
  necessary property only (Chen TY et al. Computer 2016;49(6):48-55,
  doi:10.1109/MC.2016.176), and a hand-chosen list of relations "can miss
  some important" ones (Kanewala and Bieman, section 3.3).

**Build order, one pull request each.** (a) The generated test, with each of
the seven members replayed against it with its fix reverted and the result
recorded here per member. The prediction put to the owner was five of seven:
not `PL-XST1`, which needs the weekly run, and `PL-QVBR` only once the test
draws thresholds from the run's own readings. If fewer than five fail, say so
here before building further. (b) The module that states the rounding, and
each allowance moved onto it. (c) The weekly 24 h run at the 1 ms step.
`PL-LHCL`'s walking test lands first where the two touch the same signature.

**Part (a) built, 2026-11-11: `tests/unit/test_generated_runs.py`.** Each
plan is a shipped agent, or volumes and coefficients drawn from the numerical
envelope, with the flows and the dial drawn across their supported ranges. A
plan has up to four actions, and each action changes at most one setting and
takes up to 2 000 steps. After every action the test checks seven things: the
range of every fraction, the agent balance, each running total against an
exact sum, the state against the 50-digit solution, the stepped state against
the canonical one, a sampled window's last column, and the wash-in reading.
It then replays the plan and requires the same bits. Each run of the suite
draws 100 plans, always the same ones, in about 11 s.

**Replays, 2026-11-11.** Each row reverts one fix in the working tree, runs
`uv run pytest tests/unit/test_generated_runs.py -q -x`, and restores the
tree. "Drawn plans needed" was measured before the three listed plans below
were added. Every row was run again after the blind review's fixes, at 100
drawn plans and then at 1 000, with the same result. The failure messages are
from that second run.

| Item | What was reverted | Fails in the suite's run | Drawn plans needed | Failure |
| --- | --- | --- | --- | --- |
| `PL-XST1` | `record_external_agent_transfer` adds each transfer with a plain `+`. | Yes | 100 | "a running total against the exact sum of its step amounts: a difference of 3.25e-19 is 1.08 times its rounding allowance", after 51 steps. |
| `PL-D88N` | No code: the fix kept the tolerance and documented the halt. The test's acceptance of that halt was removed. | Yes, on a listed plan | 1 000 | `AgentSimulationValidationError` with a relative error of 1.04e-9, after 24 steps. |
| `PL-9B1M` | `MAXIMUM_INPUT_FRACTION = 1.0`. | Yes, on a listed plan | 300 | "alveolar partial_pressure_fraction of 1.000000000000001 is outside 0 to 1", after 1 step. |
| `PL-81Q2` | No code: the item changed none. The squarings were removed from the test's allowances for the canonical state and the window. | No | 1 000 | "the stepped state against the canonical state: a difference of 2.37e-12 is 1.09 times its rounding allowance", after 103 steps. The 59-column chain that the item measured was not reached. |
| `PL-N559` | `WASH_IN_ROUNDING_ALLOWANCE = 0.0`. | Yes, on a listed plan | 1 000 | "a run that only washes in is described as elimination", after 1 step with every flow at zero. |
| `PL-9SL5` | `RunDefinition.evaluate` forms every column time as `start_s + column * spacing_s`. | Yes | 100 | "the last column is at 238.2 and not at the 238.20000000000002 asked for". |
| `PL-QVBR` | The reverse of #1917's changes to `app/bookmarks.py` and `app/controller.py`. | No | Passed at 1 000 | None. The test sets no MAC target and opens no branch. |

Six of the seven fail the test with their fix reverted. The prediction was
five. `PL-XST1` was predicted to need the weekly run. It fails within 51 steps,
because the test holds each running total to twice Kahan's bound of the exact
sum, and a plain sum leaves that bound at once. `PL-QVBR` passes, as predicted.

**What the replays show about the test's reach.** The 100 drawn plans alone
catch two of the seven, `PL-XST1` and `PL-9SL5`. The conditions of `PL-N559`,
`PL-9B1M` and `PL-D88N` are listed in the test as three fixed plans, so the
suite's run covers them. A new defect of their kind would be found by the
drawn plans only after 300 to 1 000 draws, which take 25 to 80 s. So the
weekly run in (c) needs several thousand draws as well as the 24 h run.

**Measured while building: rounding grows in proportion to the steps at the
envelope's slow corners.** Design part 1 refuses a bound summed over every
step, on `PL-D88N`'s measurement of shipped agents. That does not hold across
the envelope. A state held at equilibrium in a 10 000 L tissue drifted by
1.6e-12 over 4 308 steps. Over 600 drawn plans the largest drift was 0.79 of
the summed bound with its margin of three, and 38 times a bound that grows as
the square root of the steps. The test therefore allows the summed bound for
a stepped state.

**Decided 2026-11-11: for (b), the module states the figure for n steps as
the summed bound, and the agent balance keeps its fixed 1e-9** (project owner,
2026-11-11, ratified, over design part 1's refusal of a bound summed over
every step). The owner's words were "If this would be best practice then
agree", so the sources were read before the decision was recorded. They
support it. The worst-case bound for n operations grows in proportion to n. A
bound that grows as the square root of n holds only where the rounding errors
are independent and average zero. Both papers say that this fails when the
same operation repeats or the errors share a sign, and one step repeated n
times is that case.

- Higham NJ, Mary T. A new approach to probabilistic rounding error analysis.
  SIAM J Sci Comput 2019;41(5):A2815-A2835, doi:10.1137/18M1226312. Read as
  MIMS EPrint 2018.33, https://eprints.maths.manchester.ac.uk/2731/1/paper.pdf.
  Section 5: "under the assumption that rounding errors are independent and
  of zero mean", the bounds are of the order of the square root of n times u
  "instead of nu". Section 4.2: "two cases where Model 2.1 is invalid and the
  probabilistic bound does not hold. In the first case the rounding errors
  have nonzero mean and in the second case they are dependent."
- Connolly MP, Higham NJ, Mary T. Stochastic rounding and its probabilistic
  backward error analysis. SIAM J Sci Comput 2021;43(1):A566-A585,
  doi:10.1137/20M1334796. Read as MIMS EPrint 2020.12,
  https://eprints.maths.manchester.ac.uk/2778/1/paper.pdf. Section 7, on a
  sum that stops changing under round to nearest: "This leads to necessarily
  negative rounding errors", and the error then grows as nu.
- Croci et al. 2022, section 6.1, already cited above: the two assumptions
  "are often satisfied in practice, but it is easy to construct examples where
  either of the assumptions fails and the backward error almost attains the
  worst-case bound". Read at https://pmc.ncbi.nlm.nih.gov/articles/PMC8905452/.

A background reader opened each source and quoted it on 2026-11-11. The two
MIMS quotations were then checked against the downloaded text. None of the
three papers analyses a propagator applied n times, so the measurement above
is the evidence for this model and the papers are the reason it was expected.
The publishers' own pages, and Higham's *Accuracy and Stability of Numerical
Algorithms*, were refused by the session's network and were not read.

**Blind review, 2026-11-11: four findings, all fixed.** The test held the
agent balance to the relative bound alone, where the model passes a step on
either bound. It accepted a halt wherever a step needed a squaring, and now
accepts one only where the summed rounding of the steps taken has reached
1e-9. Its allowances were pooled over the whole run, and are now summed action
by action. Its coefficients were not drawn across the whole envelope. After
the fixes, over 1 000 drawn plans, the largest difference was 0.95 of its
allowance: the stepped state against the 50-digit solution, over 35 steps.
The margin of three on one propagator's bound is therefore nearly used.

**Allowances the test states for now, which (b) moves into the module.** Three
have no home in `core/` yet: the rounding of the clock, which the run
definition reads as a difference of two rounded instants; a floor of about
1e-292 below which a float no longer carries 53 bits; and twice Kahan's bound
for a running total.

**Part (b) built, 2026-11-11: `src/anesthesia_sim/core/rounding.py`.** The
module has two parts. The first holds the bounds that follow from the
arithmetic: `propagator_rounding` for one propagator, which is also the bound
for one step; `run_rounding` for n steps, which is n times that, as the owner
decided; `clock_rounding`; `RUNNING_TOTAL_ROUNDING`, twice Kahan's bound; and
`SMALLEST_FULL_PRECISION_MAGNITUDE`, the floor of about 1e-292. The last three
are the allowances that the test stated for itself after part (a). The second
part holds each fixed allowance, with what it is measured against, what the
rounding measured and the test that measures it again. The agent balance keeps
its fixed 1e-9 there.

**What moved, and what did not.** Ten constants moved with their values
unchanged: the two agent-balance tolerances, `FLOW_FRACTION_TOLERANCE`, the two
cardiac-output tolerances, `WASH_IN_ROUNDING_ALLOWANCE`, `LIVE_READING_GAP`,
`HEIGHT_BAND`, and the three constants of 1e-9 that read a quotient as a whole
count. Those three became one, `WHOLE_COUNT_TOLERANCE`, read by
`app/playback.py`, `app/chart_frame.py` and `app/chart_time_base.py`. No
comparison changed its allowance. Three things stayed, each decided by the
session:

- `BORDER_ALIGNMENT_TOLERANCE` and `LAYOUT_SIZE_SUM_TOLERANCE` stay in
  `layout/`. The design names `core/` and `app/`, and these two allow for
  rounding in the shares of a window, which no computed clinical value reads.
- `MINIMUM_RELATIVE_SCALE_L` stays in `core/agent_simulation_validation.py`.
  It keeps the relative error from being 0/0 and allows for no rounding.
- The names of the moved constants are unchanged, so every mention in
  `docs/MODEL.md`, the data files and the release notes still names them.

The problem statement counts 13 tolerance constants, six of them 1e-9. The
count of 13 is right and includes the two in `layout/`. Seven of them were
1e-9.

**A bound is stated only up to 32 squarings.** `propagator_rounding` refuses a
number of squarings above `MAXIMUM_SQUARINGS`, because the matrix exponential
module never builds such a propagator. The test used to compute an allowance
for one and then discard it when the run definition refused. It now requires
that refusal.

**The steps of `run_rounding` are a `StepCount`,** the existing checked count.
`squarings`, the three results and the two arguments of `clock_rounding` are
plain numbers. They are listed in `tests/unit/test_bare_numbers.py` with the
reason, and its count rose from 173 to 180. `PL-LHCL` is the item that gives
such values checked types.

**Sources read again for the module and `docs/MODEL.md`, 2026-11-11.** Higham
and Mary 2019 (sections 4.2 and 5) and Connolly, Higham and Mary 2021
(section 7) were read as their MIMS EPrints, in the text extracted from each
downloaded PDF. Croci et al. 2022 section 6.1 was read by a background reader
in the full text at PubMed Central. Goldberg 1991, Theorem 8, was read in the
Oracle reprint: each term is perturbed by at most twice his machine epsilon,
which is 2**-53 for a 64-bit float. Croci et al. state the two assumptions as
"zero mean and mean independence", for round to nearest.

**A wrong example found and corrected.** The comment on the chart's grid
tolerance said that 0.9 s over 0.01 s can come out just below 90. In 64-bit
floats that quotient is exactly 90. The module and its test use 0.7 / 0.1,
which is 6.999999999999999.

**Blind review of (b), 2026-11-11: two passes, five findings, all fixed.**
Each was checked against the code before it was fixed.

1. Pass 1, blocking, and pass 2, should-fix: a step inside the numerical
   envelope exceeds the bound with its margin of 3. Reproduced: the plan that
   pass 1 gave fails the generated test with "a difference of 1.277e-14 is
   1.13 times its rounding allowance". Fixed by the margin of 8, below.
2. Pass 1, optional: no drawn or listed plan needed more than 32 squarings
   over one segment, so the branch that requires the run definition's refusal
   never ran. A listed plan now holds the stiffest corner for 1 700 s, which
   needs 33. The window check also asked the module for the squarings of the
   window's spacing under a short segment's matrix, which could pass the cap
   once a longer plan existed. It is now capped at 32.
3. Pass 2, optional: an interval between two rounded instants can be wrong by
   more than one unit in the last place of the later instant. Reproduced: 1.25
   units from step 2 356 to step 6 244 at 0.01 s, and 1.17 units from step
   82 188 to step 326 590 at 0.1 s. Each instant carries half a unit and the
   subtraction half more, so `clock_rounding` now returns 1.5 units over the
   interval.
4. Pass 2, optional: two property tests in `tests/unit/test_rounding.py` had
   no `derandomize` setting. They have it now.

**Decided in the session, 2026-11-11: the margin on one propagator's bound is
8, not 3.** The design's part 1 allows "a measurement with its margin and a
test that measures it again", and the margin of 3 was that. It was set from a
shipped agent's sweep (0.6 to 2.7, 2026-10-03) and the envelope's corners
(2.5, 2026-10-26), and neither covers the inside of the envelope. No simulator
code reads the bound, so the change moves no learner-visible comparison. It
moves the allowances of `tests/unit/test_generated_runs.py`,
`tests/unit/test_numerical_envelope_sweep.py` and `tests/unit/test_rounding.py`,
and the figures in `docs/MODEL.md`. What was measured, all in leading terms,
2**s times 2**-52:

- 240 000 propagators drawn across the envelope, four seeds of 60 000, each
  compared with a 50-digit exponential. The largest error in a fraction's row
  was 3.47, at 7 squarings. The largest at each number of squarings from none
  to 19 was 3.23, 3.29, 3.30, 3.23, 3.33, 3.18, 3.08, 3.47, 2.94, 3.24, 2.87,
  3.08, 3.08, 3.27, 3.08, 3.00, 2.81, 2.75, 2.69 and 1.18.
- 120 000 states after one step, with the opening fraction drawn as well:
  3.63 at most, and 18 above 3.
- The corner that pass 2 reported, with 400 opening fractions: 3.91 at most.
- The five worst propagators, each stepped 1, 30, 300 and 2 000 times: the
  state stayed 2.6 to 3.5 per step from the 50-digit solution at every length.
  So the error of one step repeats, and the summed bound is the right shape.

The margin is about twice the largest of these, and a power of two so that the
bound is exact in binary. Routes weighed and refused: a margin of 4 or 5,
which leaves 2% to 28% above 3.91 and would fail again on correct code in the
weekly run's thousands of draws; and a bound proved from a count of the
rounded operations. A first-order count by this session put that near 8.5
with no squarings, but the session did not check the count against a published
analysis, so the module does not state it (inferred, not verified). With the
margin of 8 the summed bound for 24 h at the 1 ms step is 1.5e-7, which is 154
times the agent balance's 1e-9 and 6.5 times below `LIVE_READING_GAP`. The
test that held `LIVE_READING_GAP` to ten times the bound now holds it to five
times, as a warning distance. At the interface's 0.1 s step the summed bound
for 24 h is 1.5e-9, above the agent balance's limit. The balance does not rest
on the bound: a correct 24-hour run of a shipped agent left a residual below
4e-11.

**Replays after the review's fixes, 2026-11-11.** Each row reverts one fix on
a clean tree at `b76478c0`, runs `uv run pytest
tests/unit/test_generated_runs.py -q -x`, and restores the tree. The reverts
are the ones in the table of part (a), made where the code now is:
`PL-N559`'s is `WASH_IN_ROUNDING_ALLOWANCE = 0.0` in `core/rounding.py`, and
`PL-81Q2`'s passes zero squarings to `propagator_rounding` and `run_rounding`
for the canonical state and the window.

| Item | Fails in the suite's run | Failure |
| --- | --- | --- |
| `PL-XST1` | Yes | "a running total against the exact sum of its step amounts: a difference of 3.33e-16 is 1.4 times its rounding allowance", after 34 steps. |
| `PL-D88N` | Yes, on a listed plan | `AgentSimulationValidationError` with a relative error of 1.04e-9. |
| `PL-9B1M` | Yes, on a listed plan | "alveolar partial_pressure_fraction of 1.000000000000001 is outside 0 to 1". |
| `PL-81Q2` | No. It also passes at 1 000 drawn plans. | None. |
| `PL-N559` | Yes, on a listed plan | "a run that only washes in is described as elimination", after 1 step with every flow at zero. |
| `PL-9SL5` | Yes | "the last column is at 0.08099999999999999 and not at the 0.081 asked for", after 81 steps. |
| `PL-QVBR` | No | None. The reverse of #1917 applied to `app/bookmarks.py` and left a conflict in `app/controller.py`. The test imports neither module, so it passes whatever they hold. |

Five of the seven fail. Before the margin changed, at `d05f089d`, the same
replays gave six: `PL-81Q2` passed the suite's run and failed at 1 000 drawn
plans, with "the stepped state against the canonical state: a difference of
4.21e-12 is 1.03 times its rounding allowance" after 97 steps. That failure
was 3% past an allowance that correct code also exceeds, by up to 30%. With
the margin at 8, the allowance for the steps taken covers what removing the
squarings from the canonical state and the window takes away. The weekly run
in (c) should replay `PL-81Q2` at its several thousand draws.

**Prose review skipped.** The project owner said "skip copy edit" on
2026-11-11, so the copy editor read none of the branch's docstrings and
comments, and did not edit the pull request's title and body. The
`Prose-review:` record says read 0.

**Done when.** The module in 1 exists and each rounding allowance reads it.
The generated test in 2 exists, and each of the seven members is replayed
against it with its fix reverted, with the result recorded here per member.
The weekly job in 3 runs. `docs/MODEL.md` states the bounds.

**Generator check.** This is a head. No other head's `misread:` states the
fact. `PL-58D7`'s fact is the input domain of an operation, and three of the
seven members were filed under it.
