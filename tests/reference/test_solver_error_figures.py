"""The solver error bound that `docs/INTERFACE.md` prints holds for the model.

`docs/INTERFACE.md` § "Displayed precision" argues that the equation solver
does not limit how many decimals a readout can show. It backs that with one
bound: how far the simulator's values for the compartments that hold little
agent may lie from the same equations solved with far more digits, over the
first ten seconds of a run. Before `PL-19W8`, no test computed it.

The reference uses no solver from `core/`. It is the run's own system
matrix, built from the same settings and raised to the 0.1 s step at 50
significant digits by `_decimal_exponential` in
`tests/unit/test_numerical_envelope.py`. It is then
applied to the run's opening state once per step, also at 50 digits. So the
reference and the simulator solve the same linear equations from the same
start, and the difference between them is the simulator's own arithmetic
error: the rounding in its 0.1 s propagator and in each step's product.

The bound is read from the section as printed, as
`test_mac_awake_washout_figures.py` reads its figures. So a change to the
solver that breaks the bound fails here, and so does an edit that tightens the
bound below what the solver achieves.
"""

import re
import sys
from decimal import Decimal, localcontext
from functools import cache
from pathlib import Path

import pytest

from anesthesia_sim.app.formatting import format_percent
from anesthesia_sim.core.concentration import Fraction
from anesthesia_sim.core.governing_equations import (
    ALVEOLAR_FRACTION,
    DELIVERED_AGENT_L,
    EXHAUSTED_AGENT_L,
    FIRST_TISSUE_FRACTION,
    INSPIRED_FRACTION,
    STATE_SIZE,
    TISSUE_GROUP_COUNT,
    VENOUS_FRACTION,
    build_system_matrix,
)
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

# The 50-digit matrix exponential lives with the unit test that first needed
# it. Its directory is put on the path, as pytest does when it collects that
# directory, so both tests use the one module and the one function.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "unit"))

from test_numerical_envelope import _decimal_exponential

INTERFACE_PATH = Path(__file__).resolve().parents[2] / "docs" / "INTERFACE.md"
SECTION_HEADING = "### Displayed precision"

AGENT_ID = "sevoflurane"
STEP = SimulationStep(0.1)
STEP_TEXT = "0.1"
RUN_S = 10
#: The run length as the section writes it. A new `RUN_S` needs its words here.
RUN_WORDS = {10: "ten"}
STEPS = round(RUN_S / STEP)
REFERENCE_DIGITS = 50
BELOW_RESOLUTION = "<0.01%"

#: The compartments that the section says hold little agent: those that read
#: `<0.01%` for the whole of the first ten seconds.
SPARSE_STATES = (
    VENOUS_FRACTION,
    *(FIRST_TISSUE_FRACTION + offset for offset in range(TISSUE_GROUP_COUNT)),
)
#: The compartments that fill fast enough to show a reading within ten seconds.
FILLED_STATES = (INSPIRED_FRACTION, ALVEOLAR_FRACTION)


def _section_text() -> str:
    """The section's prose, with each run of whitespace made one space."""

    text = INTERFACE_PATH.read_text(encoding="utf-8")
    start = text.index(SECTION_HEADING)
    end = text.find("\n### ", start + len(SECTION_HEADING))

    return " ".join(text[start : end if end >= 0 else None].split())


def _one(pattern: str) -> tuple[str, ...]:
    """The groups of the one match of `pattern` in the section, or a failure naming it."""

    # regex: a search for one sentence's bound through free prose, which no
    # parser reads; the pattern names the sentence's fixed words.
    matches = re.findall(pattern, _section_text())
    assert len(matches) == 1, (
        f"docs/INTERFACE.md § 'Displayed precision' should state this once, as {pattern!r}, "
        f"and it states it {len(matches)} times. If the sentence was reworded, update the "
        f"pattern here so the bound stays checked."
    )
    found = matches[0]

    return found if isinstance(found, tuple) else (found,)


@cache
def _printed_bound() -> float:
    """The section's bound on the relative difference, `1e-13` for a printed `10^{-13}`."""

    (exponent,) = _one(
        rf"In a {AGENT_ID} run at the default settings, "
        r"the venous blood and the three tissue groups read `<0\.01%` for the whole of the "
        rf"first {RUN_WORDS[RUN_S]} seconds\. The simulator's values for these compartments "
        rf"differ from the same equations solved to {REFERENCE_DIGITS} significant digits by "
        r"less than \$`10\^\{(-\d+)\}`\$ of each value"
    )

    return 10.0 ** int(exponent)


@pytest.fixture(scope="module")
def solver_error() -> float:
    """The largest relative difference from the reference, over the sparse compartments.

    It runs ten seconds of the default sevoflurane run beside its 50-digit
    reference, and takes the largest difference at any step.
    """

    system = AgentUptakeSystem.for_agent(AGENT_ID)
    matrix = build_system_matrix(system.equation_settings())
    anywhere = 0.0

    with localcontext() as context:
        # `_decimal_exponential` sets the context's precision itself, and each
        # step's product below runs at the precision it leaves. The check
        # keeps the section's "50 significant digits" true of both. The
        # reference's own error is far below anything measured here: at 50
        # digits neither the series nor its squarings come near double
        # precision, as `_decimal_exponential`'s docstring says.
        propagator = _decimal_exponential(matrix, STEP_TEXT)
        assert context.prec == REFERENCE_DIGITS
        reference = [Decimal(value) for value in system.state_vector()]

        for _ in range(STEPS):
            system.advance(STEP)
            reference = [
                sum(
                    (propagator[row][column] * reference[column] for column in range(STATE_SIZE)),
                    Decimal(0),
                )
                for row in range(STATE_SIZE)
            ]
            # The simulator starts each step's two running totals at zero
            # (`AgentUptakeSystem.state_vector`). No other row reads them, so
            # this only keeps the reference's state the same as the run's.
            reference[DELIVERED_AGENT_L] = Decimal(0)
            reference[EXHAUSTED_AGENT_L] = Decimal(0)
            simulated = system.state_vector()

            anywhere = max(
                anywhere,
                *(
                    float(abs(Decimal(simulated[state]) - reference[state]) / reference[state])
                    for state in SPARSE_STATES
                ),
            )

            for state in SPARSE_STATES:
                assert format_percent(Fraction(simulated[state])) == BELOW_RESOLUTION, (
                    f"state {state} reads above {BELOW_RESOLUTION} within the first {RUN_S} s, "
                    f"so it no longer holds little agent as the section says"
                )

    for state in FILLED_STATES:
        assert format_percent(Fraction(system.state_vector()[state])) != BELOW_RESOLUTION, (
            f"state {state} still reads {BELOW_RESOLUTION} at {RUN_S} s, so the section's "
            f"compartments that hold little agent should include it"
        )

    return anywhere


def test_the_solver_error_in_the_first_ten_seconds_is_below_the_printed_bound(
    solver_error: float,
) -> None:
    """The largest relative difference anywhere in the ten seconds is below the section's bound.

    The bound is a numerical limit from the rounding of double-precision
    arithmetic, whose spacing relative to a value is about 2.2e-16. On
    2026-11-14 the largest difference was 9.5e-15, about 43 times that spacing,
    in fat at 9.9 s. A printed bound of 1e-13 is about 450 times the spacing,
    or about 4.5 times it for each of the 100 steps. That leaves room for a
    change in the order of the arithmetic, while staying far below any
    displayed digit.

    The bound must also stay within 100 times the measurement. A bound that is
    true but far too loose, such as the 2e-4 this section printed before
    2026-11-14, would tell a reader the solver is ten orders of magnitude less
    accurate than it is.
    """

    bound = _printed_bound()

    assert solver_error < bound, (
        f"docs/INTERFACE.md § 'Displayed precision' says the solver's values differ from the "
        f"50-digit reference by less than {bound:.0e} of each value, and the model now gives "
        f"{solver_error!r}. Find what made the solver less accurate before changing the bound."
    )
    # A choice of how close a printed bound must be, not a numerical limit: a
    # factor of 100 keeps the bound within two orders of magnitude.
    assert bound < 100 * solver_error, (
        f"docs/INTERFACE.md § 'Displayed precision' gives {bound:.0e} as the bound, more than "
        f"100 times the measured {solver_error!r}. Print a bound closer to the measurement."
    )
