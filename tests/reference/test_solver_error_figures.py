"""The solver's error figure that `docs/INTERFACE.md` prints matches the model.

`docs/INTERFACE.md` § "Displayed precision" argues that the equation solver
does not limit how many decimals a readout can show. It backs that with one
figure: how far the simulator's values for the compartments that hold little
agent lie from the same equations solved with far more digits, over the first
ten seconds of a run. It also says where in those ten seconds the largest
difference falls. Before `PL-19W8`, no test computed the figure.

The reference uses no solver from `core/`. It is the run's own system
matrix, built from the same settings and raised to the 0.1 s step at 50
significant digits by `_decimal_exponential` in
`tests/unit/test_numerical_envelope.py`. It is then
applied to the run's opening state once per step, also at 50 digits. So the
reference and the simulator solve the same linear equations from the same
start, and the difference between them is the simulator's own arithmetic
error: the rounding in its 0.1 s propagator and in each step's product.

The figure is read from the section as printed and compared with the
measurement at the precision the section prints it with, as
`test_mac_awake_washout_figures.py` does. So a change to the solver that moves
the figure fails here, and so does an edit that changes the figure without
changing the solver.
"""

import re
import sys
from dataclasses import dataclass
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


@dataclass(frozen=True)
class SolverError:
    """The largest relative difference from the reference, over the sparse compartments."""

    anywhere: float
    at_end: float


def _section_text() -> str:
    """The section's prose, with each run of whitespace made one space."""

    text = INTERFACE_PATH.read_text(encoding="utf-8")
    start = text.index(SECTION_HEADING)
    end = text.find("\n### ", start + len(SECTION_HEADING))

    return " ".join(text[start : end if end >= 0 else None].split())


def _one(pattern: str) -> tuple[str, ...]:
    """The groups of the one match of `pattern` in the section, or a failure naming it."""

    # regex: a search for one sentence's figure through free prose, which no
    # parser reads; the pattern names the sentence's fixed words.
    matches = re.findall(pattern, _section_text())
    assert len(matches) == 1, (
        f"docs/INTERFACE.md § 'Displayed precision' should state this once, as {pattern!r}, "
        f"and it states it {len(matches)} times. If the sentence was reworded, update the "
        f"pattern here so the figure stays checked."
    )
    found = matches[0]

    return found if isinstance(found, tuple) else (found,)


@cache
def _printed_error() -> str:
    """The section's figure, as `9e-15` would be written for a printed `9\\times10^{-15}`."""

    mantissa, exponent = _one(
        r"the venous blood and the three tissue groups read `<0\.01%` for the whole of the "
        r"first ten seconds\. The simulator's values for these compartments differ from the "
        r"same equations solved to 50 significant digits by at most "
        r"\$`(\d)\\times10\^\{(-\d+)\}`\$ of each value"
    )

    return f"{mantissa}e{exponent}"


def _as_printed(value: float) -> str:
    """`value` to the one significant figure that the section prints, in the same form."""

    mantissa, exponent = f"{value:.0e}".split("e")

    return f"{mantissa}e{int(exponent)}"


@pytest.fixture(scope="module")
def solver_error() -> SolverError:
    """Run ten seconds of the default sevoflurane run beside its 50-digit reference."""

    system = AgentUptakeSystem.for_agent(AGENT_ID)
    matrix = build_system_matrix(system.equation_settings())
    anywhere = 0.0
    relative = 0.0

    with localcontext() as context:
        context.prec = REFERENCE_DIGITS
        # The reference's own error is far below anything measured here: at
        # 50 digits neither the series nor its squarings come near double
        # precision, as `_decimal_exponential`'s docstring says.
        propagator = _decimal_exponential(matrix, STEP_TEXT)
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

            relative = max(
                float(abs(Decimal(simulated[state]) - reference[state]) / reference[state])
                for state in SPARSE_STATES
            )
            anywhere = max(anywhere, relative)

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

    return SolverError(anywhere=anywhere, at_end=relative)


def test_the_largest_solver_error_in_the_first_ten_seconds_is_the_printed_figure(
    solver_error: SolverError,
) -> None:
    """The largest relative difference anywhere in the ten seconds is the section's figure.

    The comparison is at one significant figure, as the section prints it. This
    is a numerical limit from the rounding of the printed figure: the
    measurement may lie anywhere that rounds to it, half a unit of its one
    digit either way.
    """

    printed = _printed_error()

    assert _as_printed(solver_error.anywhere) == printed, (
        f"docs/INTERFACE.md § 'Displayed precision' prints the solver's largest relative error "
        f"as {printed}, and the model now gives {solver_error.anywhere!r}. Update the section's "
        f"figure, and check that the sentence around it is still true."
    )


def test_the_largest_solver_error_falls_near_ten_seconds(solver_error: SolverError) -> None:
    """The difference at ten seconds itself rounds to the section's figure too.

    The section says the difference is at its largest near ten seconds. On
    2026-11-14 the largest, 9.479e-15 in fat, fell at 9.9 s, and the value at
    10 s was 9.476e-15. The comparison is at the same one significant figure,
    so it carries the same numerical limit as the test above: the rounding of
    the printed figure.
    """

    printed = _printed_error()

    assert _one(r"so it is at its largest near ten seconds")
    assert _as_printed(solver_error.at_end) == printed, (
        f"docs/INTERFACE.md § 'Displayed precision' says the solver's error is at its largest "
        f"near ten seconds, at {printed}, and the model gives {solver_error.at_end!r} there. "
        f"Update the sentence."
    )
