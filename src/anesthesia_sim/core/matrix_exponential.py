"""The exact propagator of a linear, time-invariant compartment system.

Every setting is held constant across a simulation step, so the compartment
system is linear and time-invariant *within* that step and

$$
y(t+\\Delta t) = \\exp(A\\,\\Delta t)\\,y(t)
$$

is its exact solution, with no truncation error at any step size. This module
computes that matrix exponential and nothing else: it carries no physiology,
no units and no compartment names, so that the file which assembles $`A`$ can
be read as the governing equations and this one can be read as arithmetic.

Moler and Van Loan survey nineteen ways to compute it and recommend none
without qualification; the three paragraphs below say which one is taken here
and why, against their analysis (Moler C, Van Loan C. Nineteen dubious ways
to compute the exponential of a matrix, twenty-five years later. SIAM Review
2003;45(1):3-49. doi:10.1137/S0036144502418010. Read in full text from the
PDF supplied by the project owner, 2026-09-06; the publisher and the
bibliographic indexes are both refused by this environment's egress proxy, so
the volume, issue, pages and PII above are read off the article's own first
page rather than from an index).

## Scaling and squaring, their Method 3

Summing the Taylor series of $`A`$ directly is their Method 1, and they reject
it: with $`A=\\left[\\begin{smallmatrix}-49&24\\\\-64&31\\end{smallmatrix}\\right]`$
it needed 59 terms and returned $`-22.26`$ for an entry whose true value is
$`-0.7358`$ (pp. 9-10). The cause is roundoff, not truncation - intermediate
terms reach $`e^{17}`$ while the answer is $`O(1)`$, and the cancellation
consumes the working precision. Their remedy is Method 3 (p. 12): choose
$`m=2^{s}`$ so that $`\\exp(A\\Delta t/m)`$ is computed where the terms do not
grow, and recover the interval by repeated squaring,

$$
\\exp(A\\,\\Delta t) = \\left[\\exp(A\\,\\Delta t/2^{s})\\right]^{2^{s}} .
$$

Inside that frame they prefer a Pade approximant to a truncated series, and
that half is *not* taken here, for two reasons they give themselves. Pade
needs the inverse of its denominator matrix, whose condition number grows like
$`e^{(\\alpha_1-\\alpha_n)/2}`$ in the spread of the eigenvalues (p. 11) - and
this system's rates span three orders of magnitude, from circuit turnover at
about $`2\\times10^{-2}\\ \\mathrm{s^{-1}}`$ to fat at about
$`10^{-4}\\ \\mathrm{s^{-1}}`$. And it would put a linear solve in a
safety-critical path in a package that has no linear-algebra dependency and
does not want one. Once the argument is scaled the series' own cancellation is
gone, which is what made Pade worth its cost.

## The shift: nonnegativity by construction rather than by margin

$`A`$ is a **Metzler** matrix - every off-diagonal entry is a transfer rate
between compartments and is nonnegative, every diagonal is minus the total
rate leaving that compartment - and the exponential of a Metzler matrix is
entrywise nonnegative. That is the statement that an exact step cannot drive a
compartment's contents negative, and every compartment in this package refuses
a negative amount, so a propagator entry of $`-10^{-18}`$ would halt a run and
report a numerical failure of the model for an artifact of the summation.

Scaling alone leaves that property resting on a margin: the terms of the
scaled series still alternate in sign, and the argument that the leading term
dominates has to be re-made whenever the parameters or the matrix's structure
change. Shifting removes it as a question. With

$$
\\mu = \\max_i\\left(-A_{ii}\\right) \\geq 0,
\\qquad
B = A + \\mu I \\geq 0 \\ \\text{entrywise},
$$

and $`\\mu I`$ commuting with everything,
$`\\exp(A\\Delta t) = e^{-\\mu\\Delta t}\\exp(B\\Delta t)`$. Every term of
$`\\exp(B\\Delta t)`$'s series is then a sum of products of nonnegative
numbers, so nothing cancels; the scalar is positive; and squaring a
nonnegative matrix keeps it nonnegative exactly. The propagator is therefore
nonnegative *in floating point* and not only in exact arithmetic. This is the
construction used on a continuous-time Markov generator, where it is called
uniformization; a compartment system has the same sign structure and inherits
the argument.

**What it costs, stated rather than left to be discovered.** The shift
computes $`e^{-\\mu\\Delta t}`$ and $`\\exp(B\\Delta t)`$ separately, so a state
whose own rate is far below $`\\mu`$ - the constant forcing state, whose exact
propagator entry is 1 - is recovered as a product of two rounded factors and
lands within a few units in the last place of its true value rather than on
it. Measured over the intervals this module is exercised at, that is at most
$`2\\times10^{-15}`$ relative, against the $`10^{-12}`$ the squarings
themselves contribute at an hour-long interval. It is bounded by
$`e^{\\mu\\Delta t/2^{s}}`$, which the scaling holds below
$`e^{1/16} = 1.065`$ whatever the matrix.

## The two constants, derived rather than inherited

`MAXIMUM_SERIES_ARGUMENT_NORM` is how small the scaled argument is made -
tighter than the $`\\lVert A\\rVert/m \\leq 1`$ Moler and Van Loan call the
common criterion (p. 12), because a tighter scaling is what lets the series be
truncated at a fixed order instead of a tuned one. `SERIES_TERMS` is that
order. Together they bound the truncation error: with
$`\\lVert X\\rVert_\\infty \\leq \\theta`$, the tail after $`N`$ terms is

$$
\\left\\lVert\\sum_{k>N}\\frac{X^{k}}{k!}\\right\\rVert
\\leq
\\frac{\\theta^{N+1}}{(N+1)!}\\cdot\\frac{1}{1-\\theta/(N+2)} ,
$$

which at $`\\theta = 1/16`$ and $`N = 12`$ is
$`2^{-52}/13! \\times 1.005 = 3.6\\times10^{-26}`$, against
$`\\lVert\\exp X\\rVert_\\infty \\geq 1`$. That is ten orders of magnitude below
double precision's $`2.2\\times10^{-16}`$, so truncation is not what limits the
result and the whole error budget is spent on the squarings.

Both constants are stated rather than searched for. Their inverse error
analysis (p. 12) supports choosing the cheapest $`(q,j)`$ pair for a target
tolerance, which would run faster; it would also make the returned value
depend on a table lookup keyed on $`\\lVert A\\rVert`$, where `CLAUDE.md`
requires a rule a reviewer can read and the same answer for identical inputs.
The cost of fixing them is a few matrix multiplies on a matrix small enough
that the whole propagator is rebuilt only when a setting changes.
"""

from collections.abc import Sequence
from math import ceil, exp, isfinite, log2

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.validation import require_positive_finite

Matrix = tuple[tuple[float, ...], ...]
"""A square matrix, held immutably because a propagator outlives its step.

`AgentUptakeSystem` keeps the propagator for the settings it was built at and
reuses it until a setting changes. A caller that could write into that cached
object would change what every later step computes, silently and without a
guard anywhere in its path, which is exactly the class of failure
`CLAUDE.md`'s safety-critical standard puts above convenience.
"""

MAXIMUM_SERIES_ARGUMENT_NORM = 0.0625
"""How small $`\\lVert B\\Delta t\\rVert_\\infty`$ is scaled to before the series.

Exactly $`2^{-4}`$, so `SERIES_TERMS`'s tail bound below is exact in binary
rather than rounded: $`\\theta^{13} = 2^{-52}`$.
"""

SERIES_TERMS = 12
"""Where the Taylor series is truncated, with the tail bounded in the module
docstring at $`3.6\\times10^{-26}`$ relative - ten orders below double
precision, so truncation is not what limits the result."""


def multiply(left: Matrix, right: Matrix) -> Matrix:
    """Return the matrix product, requiring conformable square operands.

    Raises:
        SimulationConfigurationError: the operands are not square matrices of
            the same size.
    """

    size = _require_square(left, "left")

    if _require_square(right, "right") != size:
        raise SimulationConfigurationError(
            f"cannot multiply a {size}x{size} matrix by a "
            f"{len(right)}x{len(right)} one; the sizes must match"
        )

    return tuple(
        tuple(sum(left_row[k] * right[k][column] for k in range(size)) for column in range(size))
        for left_row in left
    )


def matrix_exponential(matrix: Matrix, interval_s: float) -> Matrix:
    """Return `exp(matrix * interval_s)`, entrywise nonnegative by construction.

    The interval is an argument rather than a fixed simulation step: the
    propagator of a linear time-invariant system is exact over any horizon,
    and a caller that wants one step and a caller that wants an hour differ
    only in what they pass here.

    Args:
        matrix: the system matrix, square and Metzler - off-diagonal entries
            nonnegative, which is what a transfer rate is.
        interval_s: the interval to propagate over, in seconds.

    Raises:
        SimulationConfigurationError: `matrix` is not square, holds a
            non-finite entry, or has a negative off-diagonal entry; or
            `interval_s` is not positive and finite. Every one of these is
            checked before any arithmetic, so a refused call computes nothing.
    """

    size = _require_square(matrix, "matrix")
    _require_metzler(matrix)
    require_positive_finite("interval_s", interval_s)

    shift = max(0.0, max(-matrix[index][index] for index in range(size)))
    shifted = tuple(
        tuple(value + shift * (row == column) for column, value in enumerate(matrix_row))
        for row, matrix_row in enumerate(matrix)
    )

    squarings = _squarings_for(shifted, interval_s)
    scaled_interval_s = interval_s / 2**squarings

    propagator = _shifted_series(shifted, scaled_interval_s)
    decay = exp(-shift * scaled_interval_s)
    propagator = tuple(tuple(value * decay for value in row) for row in propagator)

    for _ in range(squarings):
        propagator = multiply(propagator, propagator)

    return propagator


def propagate(propagator: Matrix, state: Sequence[float]) -> tuple[float, ...]:
    """Advance a state vector by one application of `propagator`.

    Raises:
        SimulationConfigurationError: `propagator` is not square, `state` is
            not the same length as it, or `state` holds a non-finite value.
            The length check is the one that matters: a mismatched pair would
            otherwise be silently truncated to the shorter of the two and
            return a plausible vector for a different system.
    """

    size = _require_square(propagator, "propagator")

    if len(state) != size:
        raise SimulationConfigurationError(
            f"state has {len(state)} entries but the propagator is {size}x{size}"
        )

    for index, value in enumerate(state):
        if not isfinite(value):
            raise SimulationConfigurationError(f"state[{index}] is {value}, which is not finite")

    return tuple(sum(row[column] * state[column] for column in range(size)) for row in propagator)


def _require_square(matrix: Matrix, name: str) -> int:
    """Return the size of a square matrix of finite entries, or refuse it."""

    size = len(matrix)

    if size == 0:
        raise SimulationConfigurationError(f"{name} has no rows")

    for index, row in enumerate(matrix):
        if len(row) != size:
            raise SimulationConfigurationError(
                f"{name} has {size} rows but row {index} has {len(row)} entries, "
                "so it is not square"
            )

        for column, value in enumerate(row):
            if not isfinite(value):
                raise SimulationConfigurationError(
                    f"{name}[{index}][{column}] is {value}, which is not finite"
                )

    return size


def _require_metzler(matrix: Matrix) -> None:
    """Require nonnegative off-diagonal entries, which a transfer rate is.

    The shift in the module docstring guarantees an entrywise nonnegative
    propagator only for a matrix of this class, so this is the precondition
    of that guarantee rather than a convention. Refusing here names the
    offending entry, where accepting it would return a propagator that can
    carry a compartment negative and report the failure somewhere else.
    """

    for row, matrix_row in enumerate(matrix):
        for column, value in enumerate(matrix_row):
            if row != column and value < 0.0:
                raise SimulationConfigurationError(
                    f"matrix[{row}][{column}] is {value}, but an off-diagonal entry is a "
                    "transfer rate and must not be negative"
                )


def _squarings_for(shifted: Matrix, interval_s: float) -> int:
    """Return how many squarings bring the series argument under the bound."""

    norm = max(sum(row) for row in shifted) * interval_s

    if norm <= MAXIMUM_SERIES_ARGUMENT_NORM:
        return 0

    return ceil(log2(norm / MAXIMUM_SERIES_ARGUMENT_NORM))


def _shifted_series(shifted: Matrix, interval_s: float) -> Matrix:
    """Sum the Taylor series of `exp(shifted * interval_s)`.

    Every entry of `shifted` is nonnegative, so every term is nonnegative and
    the sum below cancels nothing. That is the property the caller's shift was
    performed to obtain; see the module docstring.
    """

    size = len(shifted)
    argument = tuple(tuple(value * interval_s for value in row) for row in shifted)

    term: Matrix = tuple(
        tuple(float(row == column) for column in range(size)) for row in range(size)
    )
    total = term

    for order in range(1, SERIES_TERMS + 1):
        term = multiply(term, argument)
        term = tuple(tuple(value / order for value in row) for row in term)
        total = tuple(
            tuple(left + right for left, right in zip(total_row, term_row, strict=True))
            for total_row, term_row in zip(total, term, strict=True)
        )

    return total
