"""How far a computed value can be from the exact one, stated once.

Every number this package computes is rounded to a 64-bit float, so it differs
from the exact value of its formula. A comparison on a computed value must
allow for that difference. This module is the one place that says how large
the difference can be, and every comparison in `core/` and `app/` that allows
for rounding reads its allowance from here (`PL-GJ1W`). Before this module,
each comparison chose its own number beside its own use. A comparison where
nobody had thought of rounding had no allowance, which mislabelled a steady
state as elimination (`PL-N559`) and put a chart's last column past the instant
asked for (`PL-9SL5`).

The module has two parts.

**Bounds that follow from the arithmetic.** `propagator_rounding` bounds the
rounding of one propagator, the matrix exponential that advances the state over
one interval. A step applies one propagator, so it is also the bound for one
step. `run_rounding` bounds a run of n steps. `clock_rounding` bounds what
rounding of the clock adds, and `RUNNING_TOTAL_ROUNDING` bounds a compensated
running total. Each is relative: a share of the value's own size, or of the
scale that its docstring names.

**Fixed allowances.** Each constant in the second part is the allowance of one
kind of comparison. Its docstring says what it is measured against, what the
rounding was measured to be, and which test measures it again. A fixed
allowance is not a bound. It is a chosen number, far above the measured
rounding and far below anything a learner could read.

**The bound for n steps is the sum of the steps' bounds** (project owner,
2026-11-11, ratified, over a bound that grows as the square root of n). The
square-root rule holds where the rounding errors are independent and average
zero. A run repeats one propagator n times, so its errors are neither. A state
held at equilibrium in a 10 000 L tissue drifted by 1.6e-12 over 4 308 steps,
which is 38 times the square-root rule's figure. The five worst single steps
found on 2026-11-11 were each repeated 2 000 times, and the error after n steps
stayed at n times the error of one (`PROPAGATOR_ROUNDING_UNITS` records the runs).
`docs/MODEL.md` § "How far a computed value can be from the exact one" gives the
sources.

**The agent balance does not use the summed bound.** It keeps its fixed limit
of one part in 10**9 (project owner, 2026-11-11, ratified, with the decision
above). Summed over the longest run a learner can reach, the bound is about 190
times that limit, so a limit set from it would let a real accounting error
pass. `AGENT_ACCOUNTING_RELATIVE_TOLERANCE` says what this costs.

Two tolerances in `layout/` stay there: `BORDER_ALIGNMENT_TOLERANCE` and
`LAYOUT_SIZE_SUM_TOLERANCE`. They allow for rounding in the shares of a window
that its areas take, and no computed clinical value depends on them.
"""

import math
import sys
from typing import Final

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.matrix_exponential import MAXIMUM_SQUARINGS
from anesthesia_sim.core.supported_ranges import StepCount, require_step_count

MACHINE_EPSILON: Final = sys.float_info.epsilon
"""The spacing of 64-bit floats just above 1, which is 2**-52, about 2.2e-16.

One rounded operation moves its result by at most half of this, as a share of
the result. The bounds below count rounding in this unit.
"""

SMALLEST_FULL_PRECISION_MAGNITUDE: Final = sys.float_info.min / MACHINE_EPSILON
"""The smallest magnitude that a relative rounding bound is measured against, about 1e-292.

Below the smallest normal float, 2.2e-308, a value is stored with fewer than 53
bits, so its rounding is no longer a fixed share of its size. A run that opens
at a fraction of 2e-311 would otherwise be held to a share of 2e-311, which is
finer than the spacing of the floats there. Measuring against this magnitude
instead allows a difference of about 1e-307 for each step. That is some 300
orders of magnitude below any displayed digit.
"""

PROPAGATOR_ROUNDING_UNITS: Final = 10.0
"""How far one step with s squarings can move a fraction, in units of 2**s `MACHINE_EPSILON`.

The number is derived from the arithmetic and is not a measurement. The
derivation gives at most 9.13 for every s up to `MAXIMUM_SQUARINGS`, and this
constant is that figure rounded up. The difference is measured against the
larger of the largest fraction in the state before the step and the delivered
fraction F_D. That scale is the largest fraction in the run.

Each rounded operation on 64-bit floats returns the exact result times
(1 + d), with |d| at most u = 2**-53, which is half of `MACHINE_EPSILON`
(Higham NJ, Mary T. A new approach to probabilistic rounding error analysis.
MIMS EPrint 2018.33, eq. 1.2, p. 3). A product of m such factors lies within
m u / (1 - m u) of 1 (their Lemma 2.2, p. 4). The shift in
`core/matrix_exponential.py` makes every number that the propagator is built
from nonnegative. No subtraction cancels, so a relative bound on each number
carries through sums and products of them. Counting the roundings in each
stage gives these amounts, in units of u:

1. The series: 13.15. Twelve plain additions build the sum, and the identity
   term passes through all of them, which gives 12. The later terms add 1.15,
   because the rows of the k-th sum to at most 0.065**k / k!, and it
   carries at most 4k + 13 roundings. Truncation after twelve terms adds 5e-10.
2. The decay factor: 3.07. Multiplying the shift by the interval rounds once,
   the C library's `exp` is within one unit in the last place (2 u), and
   multiplying the series by the factor rounds once more.
3. Each squaring doubles the error that it receives and adds 2: one rounding
   in each product, and u in each compensated sum.
4. Applying the propagator to the state adds 2 more.

So the step's error is (16.2 + 2) 2**s u, which is 9.11 times 2**s times
`MACHINE_EPSILON`. The second-order terms and the third condition below add
less than 0.02.

The derivation rests on three conditions, and each holds here:

1. Python's `sum` of floats is Neumaier's compensated sum (CPython 3.12 and
   later, `cs_add` in `Python/bltinmodule.c`). For n nonnegative terms its
   result lies within u + (n-1)**2 u**2 / (1 - (n-1) u)**2 of the exact sum,
   as a share of the sum. Ogita, Rump and Oishi prove that bound for their
   Sum2 (Accurate sum and dot product. SIAM J Sci Comput 2005;26(6):1955-1988,
   Proposition 4.5, eq. 4.8, p. 12 of the authors' copy). Sum2 makes the
   same roundings, because Dekker's correction gives the exact error of each
   addition when the larger operand comes first, as `cs_add` arranges (their
   eq. 1.1, p. 2).
2. The C library's `exp` is within one unit in the last place. glibc states
   0.509 units, or 0.511 without fused multiply-add
   (`sysdeps/ieee754/dbl-64/e_exp_data.c`).
3. The fraction rows of the system matrix create agent at a rate r that keeps
   r times the interval at most 2**-9. With F_D read as a fraction, each row
   of the equations sums to zero, so r comes only from rounding of the
   entries and from tissue flows that exceed the cardiac output. The
   settings refuse an excess above 1e-12 L/s plus 1e-9 of the cardiac
   output. At 10 L/min into a 0.01 L venous pool over 24 h that gives
   1.5e-3, and 2**-9 is 2.0e-3.

Underflow below the smallest normal float adds at most 2**-1074 at each
operation, which `SMALLEST_FULL_PRECISION_MAGNITUDE` covers.

The measurement checks that the bound is not vacuous. On 2026-11-11, 240 000
single steps were drawn across the numerical envelope and compared with a
50-digit evaluation. The largest error in a fraction's row of the propagator
was 3.5 units, and the largest error in a state after one step was 3.9 units,
about 40% of the bound. The same error repeats on every step: the five steps
with the largest propagator errors were each repeated 2 000 times, and the
state stayed 2.6 to 3.5 units per step from the 50-digit solution.

`tests/unit/test_rounding.py` derives the bound again from `SERIES_TERMS`,
`MAXIMUM_SERIES_ARGUMENT_NORM` and the size of the state, and requires this
constant to be that bound rounded up. It also holds steps drawn across the
envelope to the bound, and requires the worst steps found to pass 3 units.
`tests/unit/test_generated_runs.py` holds generated runs to `run_rounding`.
`PL-GJ1W` gives the derivation in full. The constant was a measured margin of
3 until 2026-11-11 and of 8 until 2026-11-14.
"""

RUNNING_TOTAL_ROUNDING: Final = 2.0 * MACHINE_EPSILON
"""How far a compensated running total may lie from the exact sum of its terms, as a share of it.

The delivered and exhausted totals are kept by Kahan's compensated summation
(`_compensated_sum` in `core/agent_simulation_validation.py`). That function's
docstring gives the bound: for nonnegative terms, the total lies within one
`MACHINE_EPSILON` of the exact sum, as a share of that sum, and the bound does
not grow with the number of terms at any run length this model supports.
Goldberg states the same bound as each term perturbed by at most twice his
machine epsilon, which is 2**-53 for a 64-bit float (Goldberg D. What every
computer scientist should know about floating-point arithmetic. ACM Comput
Surv 1991;23(1):5-48, doi:10.1145/103162.103163, Theorem 8). This allowance
is twice that. The second `MACHINE_EPSILON` covers the rounding of
the reference that the total is compared with. A plain running sum leaves this
allowance within 51 steps (`PL-XST1`, replayed 2026-11-11).
"""


CLOCK_ROUNDING_UNITS: Final = 1.5
"""How many units in the last place of the later instant a measured interval can be wrong by.

`clock_rounding` gives the three roundings that add up to it.
"""


def propagator_rounding(squarings: int) -> float:
    """Return the bound on one propagator's rounding, as a share of the state's scale.

    The bound is `PROPAGATOR_ROUNDING_UNITS` times 2**squarings times
    `MACHINE_EPSILON`. A step applies one propagator, so this is also the bound
    for one step. With no squarings it is 2.2e-15, and at the cap of 32
    squarings it is 9.5e-6.

    Args:
        squarings: How many times the scaled propagator was squared. The
            matrix exponential module chooses that number from the fastest
            rate in the system and the interval.

    Raises:
        TypeError: `squarings` is not an `int`. A `bool` is refused too,
            because `True` would count as one squaring.
        SimulationConfigurationError: `squarings` is negative or above
            `MAXIMUM_SQUARINGS`. The matrix exponential module refuses to
            build a propagator that needs more, so no bound is stated for one.
    """

    if isinstance(squarings, bool) or not isinstance(squarings, int):
        raise TypeError(f"squarings must be an int, not a {type(squarings).__name__}")

    if squarings < 0:
        raise SimulationConfigurationError(
            f"squarings must be at least zero, and {squarings} is not"
        )

    if squarings > MAXIMUM_SQUARINGS:
        raise SimulationConfigurationError(
            f"squarings must be at most {MAXIMUM_SQUARINGS}, and {squarings} is not; "
            "core/matrix_exponential.py refuses a propagator that needs more, so its "
            "rounding has no stated bound"
        )

    return PROPAGATOR_ROUNDING_UNITS * 2.0**squarings * MACHINE_EPSILON


def run_rounding(squarings: int, steps: StepCount) -> float:
    """Return the bound on the rounding of `steps` steps in a row, as a share of the state's scale.

    The bound is `steps` times `propagator_rounding(squarings)`: each step's
    bound, summed. The module docstring says why it is the sum. A sampled
    window chains one propagator per column, so the same figure bounds a chain
    of that many propagators.

    Args:
        squarings: How many squarings each step's propagator takes.
        steps: How many steps, or chained propagators, the value has behind it.

    Raises:
        TypeError: `steps` was not built as a `StepCount`, or `squarings`
            is not an `int`.
        SimulationConfigurationError: `squarings` is negative or above
            `MAXIMUM_SQUARINGS`.
    """

    require_step_count(steps)

    return propagator_rounding(squarings) * steps


def clock_rounding(instant_s: float, interval_s: float) -> float:
    """Return how far rounding of the clock can move a reading, as a share of its range.

    A run definition measures an interval as the difference of two rounded
    instants. Each instant is within half a unit in the last place of its
    exact value, and the subtraction rounds by at most half a unit more. So
    the difference can be wrong by one and a half units in the last place of
    the later instant. On 2026-11-11 the interval from step 2 356 to step
    6 244 of a 0.01 s step was wrong by 1.25 units. A reading is most
    sensitive to an error in time when one of the system's time constants
    equals the interval. Even then, the reading moves by less than the time
    error divided by the interval. A total that grows in proportion to time,
    such as the agent delivered at a constant setting, moves by exactly that
    share. The figure returned is the time error divided by the interval.

    Args:
        instant_s: The later of the two instants, in seconds.
        interval_s: The interval that the reading was propagated over, in
            seconds.

    Raises:
        SimulationConfigurationError: `instant_s` is negative or not finite,
            or `interval_s` is not finite or not above zero. A reading
            propagated over no interval has no clock rounding to bound.
    """

    if not (math.isfinite(instant_s) and instant_s >= 0.0):
        raise SimulationConfigurationError(
            f"instant_s must be finite and at least zero, and {instant_s!r} is not"
        )

    if not (math.isfinite(interval_s) and interval_s > 0.0):
        raise SimulationConfigurationError(
            f"interval_s must be finite and above zero, and {interval_s!r} is not"
        )

    return CLOCK_ROUNDING_UNITS * math.ulp(instant_s) / interval_s


# The fixed allowances. Each belongs to one kind of comparison.

AGENT_ACCOUNTING_RELATIVE_TOLERANCE: Final = 1e-9
"""The share of the agent handled that may be unaccounted for while a step still passes.

The agent handled is the amount at the start of the accounting period plus the
amount delivered since. In exact arithmetic the balance closes, so everything
this limit admits is rounding (`docs/MODEL.md` § "Mass-balance identity").

The limit is fixed, and it is not the summed bound. A correct 24-hour run of a
shipped agent left a residual below 4e-11, so the limit is at least 25 times
the measured rounding. `run_rounding` for that run at the 1 ms step is 1.9e-7,
about 190 times the limit. A limit that wide would let a real accounting error
pass (`PL-D88N`).

The cost is a documented halt. At the stiffest corners of the numerical
envelope a step needs squarings, and its rounding alone can exceed this limit
within seconds of simulated time. Such a run halts although nothing is wrong
with its accounting. No shipped agent's step needs a squaring, and
`tests/unit/test_numerical_envelope_sweep.py` fails when one does.
"""

AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L: Final = 1e-12
"""A step also passes the agent balance when the unaccounted agent is within 1 picolitre of gas.

A step passes on either limit. While a run has handled less than a millilitre
of agent gas, this limit is the wider of the two. On 2026-09-06 the largest unaccounted amount in a
3600 s run was 1.3e-11 L, for desflurane, and that run passed on the relative
limit (`docs/MODEL.md` § "Selected method (as implemented)").
"""

FLOW_FRACTION_TOLERANCE: Final = 1e-12
"""How far the tissue perfusion fractions may sum from 1.

The fractions are decimal numbers such as 0.76, 0.18 and 0.06. None is exact
in binary, and their sum takes two rounded additions, so a correct set can sum
to 1 with an error of a few times `MACHINE_EPSILON`. This allowance is about
4 500 times `MACHINE_EPSILON`. It must stay far below a transcription error:
the fractions that De Wolf et al. print sum to 0.998, and the loader refuses
them (`docs/MODEL.md` § "Tissue groups"). The value dates from v0.1.0, and no
record says why it is 1e-12 and not another number between those two.
"""

CARDIAC_OUTPUT_TOLERANCE_L_S: Final = 1e-12
"""How far the tissue blood flows may sum from cardiac output, in L/s, whatever the cardiac output.

`UptakeEquationSettings` accepts a difference of up to this amount plus
`CARDIAC_OUTPUT_RELATIVE_TOLERANCE` times the cardiac output. This part lets a
cardiac output of zero pass, which `docs/MODEL.md` § "Supported input ranges"
requires.
"""

CARDIAC_OUTPUT_RELATIVE_TOLERANCE: Final = 1e-9
"""How far the tissue blood flows may sum from cardiac output, as a share of cardiac output.

Each tissue flow is a perfusion fraction times cardiac output, and the
fractions sum to 1 within `FLOW_FRACTION_TOLERANCE`. So a correct set of flows
sums to cardiac output within about 1e-12 of it, and this allowance is a
thousand times that. `CARDIAC_OUTPUT_TOLERANCE_L_S` is added to it. The value
dates from the change to the matrix exponential on 2026-09-05, and no record
says why it is 1e-9.
"""

WASH_IN_ROUNDING_ALLOWANCE: Final = 1e-6
"""How far rounding may put the ratio F_A/F_I above 1 while the run still counts as wash-in.

With cardiac output at zero there is no uptake, so the exact solution has F_A
rise to F_I and stop there. The stepped run settles on a state that differs
from that point by rounding, and in some runs it has F_A above F_I. On
2026-10-26, nine combinations of agent and fresh gas flow were stepped at 0.1 s
for 24 h, and the largest ratio was 1 + 2.2e-14. Twenty-one runs evaluated in
one propagator from their start to 24 h reached at most 1 + 9.6e-14
(`PL-N559`).

The value is set from a clinical requirement, and not from the rounding alone
(project owner, 2026-10-26, ratified, over 1e-9 sized from rounding and over
deriving the value in code). A run of the longest supported length that sat at
the edge of the allowance throughout must lose less than 1% of the agent in the
alveolar gas, the venous blood and the vessel-rich group. At 1e-6 the worst
case, desflurane at an alveolar ventilation of 12 L/min, loses about 0.3%.
`app/wash_in.py` applies the allowance, and `tests/unit/test_wash_in.py` checks
both sides of it: the clinical requirement for every shipped agent, and that
the allowance is at least 1 000 times the rounding at each agent's settled
state.
"""

LIVE_READING_GAP: Final = 1e-6
"""How far a stepped reading and the canonical reading of one instant may differ, as a share of it.

The stepped reading has one propagator behind it for every step. The canonical
reading has one propagator from the last setting change
(`RunDefinition.state_at`). `PL-QVBR` measured the difference on 2026-11-01 for
the three agents, in runs that included a setting change. As a share of the
reading, it was at most 1.4e-10 over 24 h at the 0.1 s step, 2.9e-10 over 6 h
at the 0.01 s step, and 1.2e-9 over 2 h at the 0.001 s step. It grows with the
number of steps. Scaled in proportion to 24 h at the 0.001 s step it is 1.4e-8,
and `run_rounding` for that run is 1.9e-7. This allowance is about five times
the bound and seventy times the scaled measurement.

`app/bookmarks.py` uses it to decide when a MAC target can be judged from the
stepped readings alone. It is ten times finer than `HEIGHT_BAND`, so the zones
around that band's two edges never meet.
"""

HEIGHT_BAND: Final = 1e-5
"""A reading within this share of a MAC target's height counts as at the height.

Two readings of one instant can lie about 1e-14 apart, on opposite sides of a
height. A steady reading also moves by one unit in the last place from step to
step. Compared with the exact height, the first let a run stop on a target
that its branch showed as still running, and the second made a run with a
target at 1.00 ×MAC halt 965 times in its tenth minute (`PL-QVBR`, measured
2026-11-01). `MacTarget` in `app/bookmarks.py` says how a crossing is decided
with the band.

The band is ten times `LIVE_READING_GAP`. It is also far finer than anything
displayed. A percentage shown to two decimals resolves 0.01 percentage points,
which is 0.5% of 1 MAC of sevoflurane, about five hundred times this band.
"""

WHOLE_COUNT_TOLERANCE: Final = 1e-9
"""How far a quotient may lie from a whole number and still be read as that whole number.

A quotient of two decimal quantities can come out just below the whole number
that it equals exactly: 0.7 / 0.1 is 6.999999999999999. The
rounding is a few times `MACHINE_EPSILON` of the quotient. A truly fractional
quotient is far from every whole number: half a step, for a playback rate that
does not fit a whole number of steps into a tick. This allowance lies between
the two. Three comparisons read it: the steps in one playback tick
(`app/playback.py`), the ticks on the chart's percent axis
(`app/chart_frame.py`) and the grid units in a chart spacing
(`app/chart_time_base.py`). Each of them had its own constant of the same
value until `PL-GJ1W`.
"""
