---
id: PL-YT8N
title: BreathingCircuit.advance_fresh_gas reports a negative exhaust, as low as -3.3e-16 L, at admitted flows from 1e-15 to 1e-6 L/min, because 1 - exp(-dt/tau) loses its digits to cancellation when dt/tau is small; the exhaust it integrates cannot be negative (found fixing PL-B26Y)
priority: P1
effort: S
status: done
classes: safety, defect
feature: numerical-domain
touches: src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/__init__.py, tests/unit/test_compartment_primitives.py
added: 2026-10-05
closed: 2026-10-11
pr: 1413
payoff: the circuit's closed form never reports agent flowing back in through the exhaust, so a balance summed from it holds only physically possible amounts at every admitted flow
verify: grep -q 'def test_the_circuit_exhaust_is_never_negative_at_an_admitted_flow' tests/unit/test_compartment_primitives.py
recurrences: 2026-10-11 PL-XWFP
---

**Problem.** BreathingCircuit.advance_fresh_gas reports a negative exhaust, as low as -3.3e-16 L, at admitted flows from 1e-15 to 1e-6 L/min, because 1 - exp(-dt/tau) loses its digits to cancellation when dt/tau is small; the exhaust it integrates cannot be negative (found fixing PL-B26Y)

**Measured 2026-10-05, fixing `PL-B26Y`.** A 6 L circuit loaded to a fraction
of 1e-6 under a 100% dial, at `FreshGasFlow(1e-12)`, returns
`exhausted_agent_l=-3.3173277925717057e-16` from `advance_fresh_gas(0.1)`,
beside 1.67e-15 L delivered:
`uv run python -c "from anesthesia_sim.core.circuit import BreathingCircuit; from anesthesia_sim.core.concentration import Fraction, Percent; from anesthesia_sim.core.supported_ranges import FreshGasFlow; c = BreathingCircuit(circuit_volume_l=6.0, fresh_gas_flow_l_min=FreshGasFlow(1e-12), delivered_concentration_percent=Percent(100.0), inspired_partial_pressure_fraction=Fraction(1e-6)); print(c.advance_fresh_gas(0.1))"`.
`main` before that fix printed `-3.317327792571707e-16`. The exhaust it stands
for, the flow times the inspired fraction integrated over the step, is about
1.7e-21 L here and cannot be negative. A walk over flows from 5e-324 to 10
L/min, steps of 0.1, 1 and 60 s and three circuit states (the default one, the
one above, and a washout from 2%) found 11 negative exhausts in 126 finite
cases, all at flows from 1e-15 to 1e-6 L/min, the largest -3.3e-16 L. The
closed form before `PL-B26Y` and after it gave the same 11.

**Why.** `1.0 - exp(-dt/tau)` subtracts two numbers within an ulp of 1 when
`dt/tau` is small, so its absolute error is up to half an ulp of 1, about
5.6e-17, and the exhaust multiplies it by the circuit's volume: 6 L times that
is the 3.3e-16 L above. Where the washout the term stands for is smaller than
that, its sign is the rounding's.

**Reach.** As `PL-B26Y`'s: not a run's path, whose exhaust is
`AgentUptakeSystem.advance()`'s accounting, but the circuit's own closed form,
which `BreathingCircuit.advance`, a notebook or a test calls, and a negative
amount of agent folded into a balance is a plausible-looking wrong value.

**What a fix has to decide.** `-expm1(-dt/tau)` keeps the digits, but the
stored fraction is updated with `exp(-dt/tau)`, so using it in the exhaust
alone would trade the sign for a circuit balance that closes less well, by
about the same 3e-16 L. Using it in both would write the fraction update as
`i + (d - i) * -expm1(-dt/tau)` rather than `d + (i - d) * exp(-dt/tau)`, which
is exact at zero flow without a branch, and so would move the analysis
`src/anesthesia_sim/core/__init__.py` § "Zero flow is tested with `== 0.0`,
never against a tolerance" and `tests/unit/test_compartment_primitives.py` rest
on (`PL-79YX`), and `tissue.py` and `blood.py` update their fractions in the
same `d + (i - d) * exp(-dt/tau)` form.

**Re-run 2026-10-05, at triage: it still holds.** The command above, against
`main` at `b67dace8` after `PL-B26Y` merged, printed
`FreshGasExchange(delivered_agent_l=1.6666666666666668e-15,
exhausted_agent_l=-3.3173277925717057e-16)`.

**Why it matters.** An exhausted amount is agent leaving the circuit, which
cannot be negative, and the circuit's closed form reports it as the
difference between what was delivered and what the circuit kept, so at these
flows the sign is the rounding's rather than the physics'. The size is far
below anything clinical, but a caller summing the exhaust into a balance - a
scavenged-agent total, a conservation check in a notebook or a test - is
handed an impossible value that looks like a number, and `CLAUDE.md` prefers an
obvious failure or a correct value to a plausible wrong one on this path, as
`PL-B26Y` was classed for the `nan` at the same function's other edge.

**Done when.** `BreathingCircuit.advance_fresh_gas` reports an exhaust of zero
or more at every admitted flow, step and circuit state, the 126 cases of the
walk above included, while the circuit's balance - delivered less exhausted
equals the change in what the circuit holds - closes no worse than today across
them. Whether `-expm1(-dt/tau)` goes in the exhaust alone or in the fraction
update as well, and so whether `core/__init__.py`'s zero-flow analysis and
`tissue.py` and `blood.py`'s matching form move with it, is the implementer's
call from the trade-off above; if the fraction update moves, the zero-flow
claim and its tests are brought along in the same change. A test in
`tests/unit/test_compartment_primitives.py` named
`test_the_circuit_exhaust_is_never_negative_at_an_admitted_flow` pins it at
flows from 1e-15 to 1e-6 L/min.

**Done 2026-10-11.** Re-confirmed first: the command above printed the same
`-3.3173277925717057e-16` on `main` at `16a20a4f`.

**Neither route the brief weighed meets "Done when", measured.** `-expm1` in
the exhaust alone fixes the brief's own state and still exhausts
-2.5e-32 L from a circuit filling from empty at 1e-14 L/min over 1 s, and its
balance misses by up to 5.1e-16 L where the circuit holds 6e-6 L, the 3e-16 L
the brief predicted. `-expm1` in the fraction update too closes the balance,
but with the exhaust still written as delivered less kept it exhausts
-1.9e-34 L from empty under a 100% dial at 1e-15 L/min, and -3.9e-34 L under a
2% one at 1e-13 L/min, each over 0.1 s. Delivered less kept is a difference
of near-equal amounts wherever the circuit keeps nearly all it is given,
however many digits either carries, so its sign is the rounding's there in
any form.

**What was built.** The fraction is `i + (d - i) * g`, with
`g = -expm1(-dt/tau)` and `dt/tau` formed as the gas the step admits over the
circuit's volume, so no time constant is formed to overflow. The exhaust is
the flow times the integral of the inspired fraction written as
`lower * A + (d - lower) * F + (i - lower) * K`: `A` the gas admitted, `K = V g`
the circuit's starting gas that left, `F = V (dt/tau - g)` the fresh gas that
left, and `lower` the smaller of the two fractions. Every term is
nonnegative because `0 <= g <= dt/tau`, which `expm1` keeps (no violation in
400,004 samples from 5e-324 to 1e3). At the dial the exhaust is exactly what
was delivered, and at zero flow every amount is a product with zero, so the
zero-flow branch is gone; `core/__init__.py`'s zero-flow section and the
test docstrings resting on it moved with it, as this brief asked. The
patient compartments keep their `d + (i - d) * exp(-dt/tau)` form and their
branches, which store an amount and so still need them.

**The same split without `lower`, `i * K + d * F`,** is also nonnegative
and reads more simply, but at the dial it misses what was delivered by up to
a rounding in 685 of 2,280 equilibrium cases where the old form is exact, so
the split stays.

**Measured 2026-10-11, the new code bit for bit against the candidate in all
28,676 cases below.** "Rounding" is one ulp of the largest amount the step
involves - delivered, exhausted or held - and the residual is delivered less
exhausted less the change in what the circuit holds, in exact rationals.

| Walk | Negative exhausts, old to new | Worst residual, litres | Worst residual, roundings |
| --- | --- | --- | --- |
| The brief's walk, rebuilt: 14 flows from 5e-324 to 10 L/min, 0.1, 1 and 60 s, its three states | 2 to 0 | 3.9e-16 to 6.0e-16 | 3.6e5 to 0.79 |
| 6,270 cases: 2, 6 and 8 L, 38 flows, 11 states, 1 ms to 1 h | 478 to 0 | 2.0e-14 to 3.0e-14 | 6e15 to 4 |
| 20,000 random cases | 1,068 to 0 | 2.6e-14 to 3.0e-14 | 9e15 to 9 |
| 2,280 at the dial | 0 to 0 | 0 to 0 | 0 to 0 |

The rebuilt walk finds 2 negatives where the brief's found 11, since its
flows are not the brief's, which were not recorded.

**"Closes no worse than today" is read in roundings** (project owner,
2026-10-11, ratified, over reading it in absolute litres). It is the only
reading under which the two forms can be compared across amounts three
hundred orders apart. In litres the worst case grows, at the largest
steps, from one rounding of a litre-sized amount to a few: the old exhaust
was defined from the balance, which closed it tightly there and gave it the
rounding's sign at small flows, and an exhaust whose sign is structural is
computed independently, so its balance carries both sides' rounding. The
rebuilt walk's worst moves from a step delivering 1.7 mL, 3.6e5 roundings
off, to one delivering 4 L, under one.

**Tests.** `test_the_circuit_exhaust_is_never_negative_at_an_admitted_flow`
and `test_the_circuit_balance_closes_within_the_rounding_of_what_the_step_moves`
each walk ten decades from 1e-15 to 1e-6 L/min, three steps and four states,
two of them a circuit filling from empty. Of their 120 cases each, the old
code fails 35 and 45; `-expm1` in the exhaust alone 1 and 90; `-expm1`
throughout with delivered less kept 2 and 0. The fraction written back as
`d + (i - d) * exp(-dt/tau)` fails `test_zero_flow_is_an_exact_no_op` and 90
balance cases.

**Found and filed:** `PL-XWFP`, the patient compartments' closed forms
reporting uptake as a return at flows below 3e-13 L/min.

