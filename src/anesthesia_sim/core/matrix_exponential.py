"""The exact propagator of a linear, time-invariant compartment system.

Every setting is held constant during a simulation step. Within that step the
compartment system is therefore linear and time-invariant, and

$$
y(t+\\Delta t) = \\exp(A\\,\\Delta t)\\,y(t)
$$

is its exact solution, with no truncation error at any step size. This module
computes that matrix exponential and nothing else. It contains no physiology,
no units and no compartment names. The file that assembles $`A`$ can then be
read as the governing equations, and this one can be read as arithmetic.

This module serves the step that `docs/MODEL.md` § "Selected method (as
implemented)" describes. That section says the same thing from the other side:
this module "computes $`\\exp(A\\Delta t)`$ and carries no physiology".
**Nothing here implements a governing equation.** Every formula below is
numerical method, and it is labelled as numerical method, not physiology, on
purpose. A reader looking for the model should go to `governing_equations.py`,
and should stop here only for the arithmetic that advances the model.

Moler and Van Loan survey nineteen ways to compute the matrix exponential, and
they recommend none without qualification. The three sections below say which
method this module takes, and why, against their analysis (Moler C, Van Loan C.
Nineteen dubious ways to compute the exponential of a matrix, twenty-five years
later. SIAM Review 2003;45(1):3-49. doi:10.1137/S00361445024180. The article
was read in full text from the PDF supplied by the project owner on 2026-09-06.
On that date this environment's egress proxy refused the publisher, so the
volume, issue, pages and PII above were read off the article's own first page
rather than from an index. Confirmed 2026-09-19: the publisher
(`epubs.siam.org`) is still refused, but the bibliographic indexes (`doi.org`,
`api.crossref.org`, `api.openalex.org`) are now reachable. Checking against
Crossref's record for the registered DOI showed that the identifier above had
carried a spurious trailing `10`, and it was corrected).

## Scaling and squaring, their Method 3

Their Method 1 sums the exponential's Taylor series in $`A`$ directly, and they
reject it. With $`A=\\left[\\begin{smallmatrix}-49&24\\\\-64&31\\end{smallmatrix}\\right]`$
it needed 59 terms and returned $`-22.26`$ for an entry whose true value is
$`-0.7358`$ (pp. 9-10). The cause is roundoff, not truncation. Intermediate
terms reach $`e^{17}`$ while the answer is $`O(1)`$, and the cancellation
between them uses up the working precision. Their remedy is Method 3 (p. 12).
Choose $`m=2^{s}`$ so that $`\\exp(A\\Delta t/m)`$ is computed over an interval
short enough that the terms do not grow. Then recover the full interval by
repeated squaring,

$$
\\exp(A\\,\\Delta t) = \\left[\\exp(A\\,\\Delta t/2^{s})\\right]^{2^{s}} .
$$

Within scaling and squaring, they prefer a Pade approximant to a truncated
series. This module does *not* take that half of their method, for two reasons
that they give themselves. First, Pade needs the inverse of its denominator
matrix, whose condition number grows like $`e^{(\\alpha_1-\\alpha_n)/2}`$ with
the spread of the eigenvalues (p. 11). This system's rates span three orders of
magnitude, from circuit turnover at about $`2\\times10^{-2}\\ \\mathrm{s^{-1}}`$
to fat at about $`10^{-4}\\ \\mathrm{s^{-1}}`$. Second, Pade would put a linear
solve in a safety-critical path, in a package that has no linear-algebra
dependency and does not want one. The cancellation in the series is what made
Pade worth its cost, and once the argument is scaled that cancellation is gone.

## The shift: nonnegativity by construction rather than by margin

$`A`$ is a **Metzler** matrix. Every off-diagonal entry is a transfer rate
between compartments and is nonnegative, and every diagonal entry is minus the
total rate leaving that compartment. The exponential of a Metzler matrix is
entrywise nonnegative, which is the statement that an exact step cannot drive a
compartment's contents negative. Every compartment in this package refuses a
negative amount. So a propagator entry of $`-10^{-18}`$, which would be an
artifact of the summation, would halt a run, and the run would report a
numerical failure of the model.

Scaling alone leaves that property depending on a margin. The terms of the
scaled series still alternate in sign, so the argument that the leading term
dominates has to be made again whenever the parameters or the matrix's
structure change. Shifting removes the question. With

$$
\\mu = \\max_i\\left(-A_{ii}\\right) \\geq 0,
\\qquad
B = A + \\mu I \\geq 0 \\ \\text{entrywise},
$$

and because $`\\mu I`$ commutes with every matrix,
$`\\exp(A\\Delta t) = e^{-\\mu\\Delta t}\\exp(B\\Delta t)`$. Every term of the
series for $`\\exp(B\\Delta t)`$ is then a sum of products of nonnegative
numbers, so nothing cancels. The scalar factor is positive. Squaring a
nonnegative matrix keeps it exactly nonnegative. The propagator is therefore
nonnegative *in floating point*, not only in exact arithmetic. The same
construction is used on the generator of a continuous-time Markov chain, where
it is called uniformization. A compartment system has the same sign structure,
so the same argument applies to it.

**What it costs, stated rather than left to be discovered.** The shift
computes $`e^{-\\mu\\Delta t}`$ and $`\\exp(B\\Delta t)`$ separately. A state
whose own rate is far below $`\\mu`$ is therefore recovered, over the scaled
interval, as the product of two rounded factors. It lands within a few units in
the last place of its true value rather than exactly on it. Each squaring can
then double that error, so after $`s`$ squarings the state carries an error of
up to about $`2^{s}\\varepsilon`$, with $`\\varepsilon = 2^{-52}`$. An
hour-long interval takes sixteen squarings, which gives a bound of
$`1.5\\times10^{-11}`$. The analytic comparisons in the tests measure
$`2\\times10^{-12}`$. This module stops at `MAXIMUM_SQUARINGS`, because past it
the bound exceeds one part in a million. Accuracy that falls as the number of
squarings grows is a known weakness of the method, not of this module. Higham's
revision of the method is "typically more accurate, owing to the fewer required
squarings" (Higham NJ. The scaling and squaring method for the matrix
exponential revisited. SIAM J Matrix Anal Appl 2005;26(4):1179-1193.
doi:10.1137/04061101X).

**One kind of state is exempt from that cost, exactly.** A row of $`A`$ with no
nonzero entry belongs to a state that nothing moves, such as the constant
forcing state. Its row of $`\\exp(A\\Delta t)`$ is the identity's row at every
interval. The shift would recover that row's diagonal entry as $`1+\\delta`$,
and the squarings would raise it to $`(1+\\delta)^{2^{s}}`$. That was measured
at $`2.28\\times10^{222}`$ with the alveolar volume driven to 1e-19 L
(`PL-2MD9`). So the module writes that row as the identity's before the
squarings, and the squarings then keep it exact to the last bit.
`_with_constant_rows_restored` explains why they do. This is the simplest case
of a published remedy. For a triangular matrix, Al-Mohy and Higham "compute the
diagonal elements in the squaring phase as exponentials instead of from
powers" of the approximant. A state that nothing moves is a one-by-one diagonal
block whose exponential is one (Al-Mohy AH, Higham NJ. A new scaling and
squaring algorithm for the matrix exponential. SIAM J Matrix Anal Appl
2009;31(3):970-989. doi:10.1137/09074721X). Both Higham citations were read
from their abstracts in Crossref's records on 2026-10-03, not in full text.

## The series constants, derived rather than inherited

`MAXIMUM_SERIES_ARGUMENT_NORM` sets how small the scaled argument is made. It
is tighter than the $`\\lVert A\\rVert/m \\leq 1`$ that Moler and Van Loan call
the common criterion (p. 12), because a tighter scaling lets the series be
truncated at a fixed order instead of a tuned one. `SERIES_TERMS` is that
order. Together the two constants bound the truncation error. With
$`\\lVert X\\rVert_\\infty \\leq \\theta`$, the tail after $`N`$ terms is

$$
\\left\\lVert\\sum_{k>N}\\frac{X^{k}}{k!}\\right\\rVert
\\leq
\\frac{\\theta^{N+1}}{(N+1)!}\\cdot\\frac{1}{1-\\theta/(N+2)} ,
$$

which at $`\\theta = 1/16`$ and $`N = 12`$ is
$`2^{-52}/13! \\times 1.005 = 3.6\\times10^{-26}`$, compared with
$`\\lVert\\exp X\\rVert_\\infty \\geq 1`$. That is ten orders of magnitude below
double precision's $`2.2\\times10^{-16}`$. Truncation therefore does not limit
the result, and the whole error budget is spent on the squarings, which
`MAXIMUM_SQUARINGS` bounds.

Both constants are fixed values rather than the result of a search. Moler and
Van Loan's inverse error analysis (p. 12) supports choosing the cheapest
$`(q,j)`$ pair for a target tolerance, which would run faster. It would also
make the returned value depend on a table lookup keyed on $`\\lVert A\\rVert`$.
`CLAUDE.md` instead requires a rule that a reviewer can read, and the same
result for identical inputs. Fixing the constants costs a few matrix
multiplications on a small matrix, and the whole propagator is rebuilt only
when a setting changes.
"""

from collections.abc import Sequence
from math import ceil, exp, isfinite, log2
from operator import mul

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.validation import require_positive_finite

Matrix = tuple[tuple[float, ...], ...]
"""A square matrix, stored immutably because a propagator outlives its step.

`AgentUptakeSystem` keeps the propagator for the settings it was built at and
reuses it until a setting changes. A caller that could write into that cached
object would silently change what every later step computes, and no guard
anywhere in its path would notice. `CLAUDE.md`'s safety-critical standard ranks
preventing exactly that class of failure above convenience.
"""

MAXIMUM_SERIES_ARGUMENT_NORM = 0.0625
"""The largest scaled $`\\lVert B\\Delta t\\rVert_\\infty`$ at which the series is summed.

The value is exactly $`2^{-4}`$, so the tail bound for `SERIES_TERMS` below is
exact in binary rather than rounded: $`\\theta^{13} = 2^{-52}`$.
"""

SERIES_TERMS = 12
"""The order at which the Taylor series is truncated.

The module docstring bounds the tail at $`3.6\\times10^{-26}`$ relative to the
result. That is ten orders of magnitude below double precision, so truncation
does not limit the result.
"""

MAXIMUM_SQUARINGS = 32
"""The largest number of squarings this module performs for one result.

A result that would need more squarings is refused as not established.

Each squaring can double the relative error that the scaled propagator carries
into it, and that error is not zero. The shift described in the module
docstring leaves a rounding error of its own in every state whose own rate is
far below $`\\mu`$. After $`s`$ squarings the bound is about
$`2^{s}\\varepsilon`$, with $`\\varepsilon = 2^{-52}`$, and the shipped system
follows that bound. It was measured on 2026-10-03 on sevoflurane at the 0.1 s
step. The alveolar volume was driven down a decade at a time, and every entry
was compared with a high-precision evaluation of the same exponential. At every
decade from none to 45 squarings, the worst entry's error stayed between 0.6
and 2.7 times the bound: $`6.0\\times10^{-16}`$ at none, $`6.5\\times10^{-11}`$
at 18 and $`6.3\\times10^{-7}`$ at 31. At 51 squarings it was 174%
(`PL-2MD9`).

A cap of thirty-two puts the bound at $`2^{32}\\cdot2^{-52} = 2^{-20}`$, about
one part in a million. The most squarings any supported input needs is 19. That
is at the 24-hour horizon that `RunDefinition.state_at` can be asked for, at the
widest supported flows. The cap therefore leaves a factor of $`2^{13}`$ in rate
or interval before it refuses anything a run can reach. What it does refuse is
the regime that the alveolar sweep found. At 1e-18 L the propagator was wrong by
about 100% in every entry, yet the run advanced three steps with its accounting
check passing. The check passed because the same failure had affected every
term of the accounting identity.
"""


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

    The interval is an argument rather than a fixed simulation step, because
    the propagator of a linear time-invariant system is exact over any
    horizon. A caller that wants one step and a caller that wants an hour
    differ only in the interval they pass.

    Args:
        matrix: the system matrix. It must be square and Metzler: every
            off-diagonal entry is nonnegative, as a transfer rate is.
        interval_s: the interval to propagate over, in seconds.

    Raises:
        SimulationConfigurationError: `matrix` is not square, contains a
            non-finite entry, or has a negative off-diagonal entry. It is also
            raised when `interval_s` is not positive and finite, when the
            interval needs more than `MAXIMUM_SQUARINGS` squarings, or when
            the number of squarings it needs overflows. All of these are
            checked before any arithmetic, so a refused call computes nothing.
            Two more conditions are checked on the result of the squarings,
            and raise it too: an entry that is not finite, and the zero matrix.
    """

    size = _require_square(matrix, "matrix")
    _require_finite(matrix, "matrix")
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
    propagator = _with_constant_rows_restored(matrix, propagator)

    for _ in range(squarings):
        propagator = multiply(propagator, propagator)

    _require_finite(propagator, "the propagator")
    _require_a_nonzero_propagator(propagator)

    return propagator


def propagate(propagator: Matrix, state: Sequence[float]) -> tuple[float, ...]:
    """Advance a state vector by one application of `propagator`.

    This is the one function in this module that runs on every simulation
    step rather than once per settings change, so its checks are chosen for
    that cost. It checks the shapes, because a shape mismatch would silently
    return a plausible vector for a different system. It checks the state,
    because the state is the argument that varies. It does not check the
    propagator's own entries again. Those are checked where they are produced,
    since `matrix_exponential` validates both its input and its result, and
    the object is immutable. Checking them here would cost time on every step
    and change no decision.

    The product is written with `map(mul, ...)` rather than as a generator
    over `range(size)`. The same floats reach `sum` in the same order, and the
    index arithmetic and the two subscript operations per term move into C.
    Every result is bit-identical, so the determinism that `CLAUDE.md`
    requires is unaffected. Determinism also rests on a stronger reason than
    the matching order: `sum`'s float path is Neumaier-compensated, and its
    result does not depend on how the terms were produced. The test
    `test_propagate_sums_each_row_with_the_
    compensation_sum_provides` pins that behaviour, because an explicit
    accumulator loop would be faster still but would not be the same function.
    On the 9x9 matrix that the model steps, this function measured 5.0 us
    against 8.5 us. Together with the cache key in `uptake_system.py`, the
    whole step measured 23.8 us against 32.7 us (`PL-R460`).

    Raises:
        SimulationConfigurationError: `propagator` is not square, `state` is
            not the same length as it, or `state` holds a non-finite value.
    """

    size = _require_square(propagator, "propagator")

    if len(state) != size:
        raise SimulationConfigurationError(
            f"state has {len(state)} entries but the propagator is {size}x{size}"
        )

    for index, value in enumerate(state):
        if not isfinite(value):
            raise SimulationConfigurationError(f"state[{index}] is {value}, which is not finite")

    # `strict=False`: `_require_square` has established that every row is `size`
    # long, and the check above has established that `state` is too, so the
    # lengths cannot differ here. `strict=True` would check that again on every
    # step of every run and could never fail. It measures 2.0 us of the 8.3 us
    # that this function costs.
    return tuple(sum(map(mul, row, state, strict=False)) for row in propagator)


def _require_square(matrix: Matrix, name: str) -> int:
    """Return the size of a square matrix, or refuse a ragged or empty one."""

    size = len(matrix)

    if size == 0:
        raise SimulationConfigurationError(f"{name} has no rows")

    for index, row in enumerate(matrix):
        if len(row) != size:
            raise SimulationConfigurationError(
                f"{name} has {size} rows but row {index} has {len(row)} entries, "
                "so it is not square"
            )

    return size


def _require_finite(matrix: Matrix, name: str) -> None:
    """Require every entry to be a finite number.

    This is separate from the shape check because the two are needed in
    different places. The shape is checked wherever a matrix is used, and the
    entries only where a matrix is produced or supplied. `matrix_exponential`
    calls this function on its input and again on its result. The second call
    is the stronger check: a non-finite entry that arose during the series or
    the squarings is caught when it is built, rather than at the compartment
    it would later reach.
    """

    for index, row in enumerate(matrix):
        for column, value in enumerate(row):
            if not isfinite(value):
                raise SimulationConfigurationError(
                    f"{name}[{index}][{column}] is {value}, which is not finite"
                )


def _require_a_nonzero_propagator(propagator: Matrix) -> None:
    """Refuse the all-zero matrix, which the squarings can produce and `_require_finite` accepts.

    $`\\exp(A\\,\\Delta t)`$ is nonsingular for every finite $`A`$ and every
    finite interval, because its determinant is
    $`e^{\\operatorname{tr}(A)\\Delta t}`$, which is positive. So the zero
    matrix is not the propagator of any system and can only be a
    floating-point artifact. That makes this check exact rather than a
    tolerance. There is no margin to choose, and no legitimate argument
    approaches the zero matrix from one side.

    The zero matrix was first reached by driving
    `AlveolarCompartment.gas_volume_l` to 1e-300 L, which needs 995 squarings.
    The shift's round trip leaves the scaled diagonal entry of every slow
    state, and of the constant state, at $`1-2^{-53}`$ rather than at one.
    After 62 squarings that entry is $`e^{-512}`$, and the 63rd squaring makes
    it zero. Every squaring after that keeps the whole matrix at zero. This is
    the mechanism that `PL-2MD9` measured, with the opposite sign. The result
    was finite and entrywise nonnegative, so it had both properties that this
    module states. `propagate()` then returned the zero state vector: every
    compartment empty, nothing delivered and nothing exhausted. The
    mass-balance identity in `agent_simulation_validation.py` passed on that
    result, because every term of the identity had been reduced to zero too,
    and zero does balance zero. A concentration of exactly 0.0 was reported,
    and no guard anywhere in the path objected (`PL-3PRZ`).

    **The model no longer produces the zero matrix, for two reasons**
    (`PL-2MD9`). First, a run at that volume now stops earlier, refused at
    `MAXIMUM_SQUARINGS`. Second, a matrix with a constant state cannot produce
    the zero matrix at any interval. `_with_constant_rows_restored` writes that
    state's row as the identity's, and the squarings keep it. The only case
    that still reaches this check is a matrix with no constant state in which
    every mode decays below the smallest subnormal number.

    **Individual zero entries are left alone, including on the diagonal.** A
    mode that has genuinely decayed below the smallest subnormal number
    correctly returns 0.0. `exp(-0.5 * 3600)` is a real number that no double
    can hold, and `test_diagonal_matrix_matches_scalar_decay` propagates
    exactly that case. The failure differs from genuine decay in that
    *nothing* survives it.

    Args:
        propagator: the matrix the squarings produced.

    Raises:
        SimulationConfigurationError: every entry is zero.
    """

    if any(value != 0.0 for row in propagator for value in row):
        return

    raise SimulationConfigurationError(
        f"the propagator is the {len(propagator)}x{len(propagator)} zero matrix, which is "
        "singular and so is the exponential of nothing; its entries have underflowed and "
        "it no longer solves the system"
    )


def _require_metzler(matrix: Matrix) -> None:
    """Require every off-diagonal entry to be nonnegative, as a transfer rate is.

    The shift described in the module docstring guarantees an entrywise
    nonnegative propagator only for a Metzler matrix. This check is therefore
    the precondition of that guarantee, not a convention. Refusing the matrix
    here names the offending entry. Accepting it would return a propagator
    that can drive a compartment negative, and the failure would then be
    reported somewhere else.
    """

    for row, matrix_row in enumerate(matrix):
        for column, value in enumerate(matrix_row):
            if row != column and value < 0.0:
                raise SimulationConfigurationError(
                    f"matrix[{row}][{column}] is {value}, but an off-diagonal entry is a "
                    "transfer rate and must not be negative"
                )


def _squarings_for(shifted: Matrix, interval_s: float) -> int:
    """Return how many squarings scale the series argument's norm down to the bound or below.

    Raises:
        SimulationConfigurationError: more than `MAXIMUM_SQUARINGS` squarings
            are needed. Past that number, the error the squarings can amplify
            exceeds one part in a million, so the result could not be
            established. At the 0.1 s step, this happens for an alveolar
            volume from 1e-11 L to 1e-308 L (`PL-2MD9`).
        SimulationConfigurationError: dividing the norm by the series bound
            overflows. The norm itself is finite in this case: at an alveolar
            volume of 1e-309 L it is 1.2e+307. The division by $`2^{-4}`$ is
            what reaches `inf`. `log2` of that is `inf`, and `ceil` of it
            raises `OverflowError`. `OverflowError` is not one of this
            module's documented failures, and it is outside the hierarchy in
            `core/exceptions.py` that a caller catches by type. So
            `AgentUptakeSystem.advance()` neither restates it nor rolls back
            on it by type, and only its `finally` clause saves the state
            (`PL-3PRZ`).
    """

    norm = max(sum(row) for row in shifted) * interval_s

    if norm <= MAXIMUM_SERIES_ARGUMENT_NORM:
        return 0

    scaled_norm = norm / MAXIMUM_SERIES_ARGUMENT_NORM

    if not isfinite(scaled_norm):
        raise SimulationConfigurationError(
            f"the shifted matrix has a row sum of {norm} over {interval_s} s, and "
            f"scaling it to the series bound of {MAXIMUM_SERIES_ARGUMENT_NORM} overflows, "
            "so the number of squarings is not computable; the rates in this matrix are "
            "too large to propagate in double precision"
        )

    squarings = ceil(log2(scaled_norm))

    if squarings > MAXIMUM_SQUARINGS:
        raise SimulationConfigurationError(
            f"the shifted matrix has a row sum of {norm} over {interval_s} s, which "
            f"takes {squarings} squarings to scale to the series bound of "
            f"{MAXIMUM_SERIES_ARGUMENT_NORM}; past {MAXIMUM_SQUARINGS} the rounding error "
            "they amplify can exceed one part in a million, so the result could not be "
            "established in double precision"
        )

    return squarings


def _shifted_series(shifted: Matrix, interval_s: float) -> Matrix:
    """Sum the Taylor series of `exp(shifted * interval_s)`.

    Every entry of `shifted` is nonnegative, so every term is nonnegative and
    nothing cancels in the sum below. The caller shifted the matrix to obtain
    that property, as the module docstring explains.
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


def _with_constant_rows_restored(matrix: Matrix, propagator: Matrix) -> Matrix:
    """Return `propagator` with each constant state's row written as the identity's.

    A row of `matrix` with no nonzero entry belongs to a state that nothing
    moves. That state's row of every power $`A^{k}`$, $`k \\geq 1`$, is zero,
    so its row of $`\\exp(A\\,\\Delta t)`$ is the identity's row at every
    interval. This holds exactly, not to within a tolerance. The shift does
    not preserve it. The shift puts $`\\mu`$ on the diagonal where $`A`$ has
    zero. The series returns about $`e^{\\mu h}`$ there, the decay multiplies
    that by $`e^{-\\mu h}`$, and the round trip lands at $`1+\\delta`$ rather
    than exactly on one. Each squaring squares that entry. Each squaring also
    multiplies the entry into the column through which every other row reads
    the state. So the error, which the squarings raise to
    $`(1+\\delta)^{2^{s}}`$, affects the forcing terms as well as the state
    (`PL-2MD9`).

    When the row is written back before the squarings, it leaves them nothing
    to amplify, and they keep it exact to the last bit. With row $`i`$ equal
    to $`e_i^{T}`$, every entry of row $`i`$ of the product is a sum in which
    one term is multiplied by one and every other term by zero. None of those
    operations rounds.

    The function finds these rows by inspecting `matrix`, not by name, so this
    module still contains no physiology. `governing_equations.UNIT_STATE` is
    the one such row that the model has, and any other state with an empty
    equation would be kept the same way.
    """

    size = len(matrix)

    return tuple(
        tuple(float(row == column) for column in range(size))
        if all(value == 0.0 for value in matrix_row)
        else propagator_row
        for row, (matrix_row, propagator_row) in enumerate(zip(matrix, propagator, strict=True))
    )
