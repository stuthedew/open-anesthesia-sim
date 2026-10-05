"""The alveolar gas compartment: one ideal, perfectly mixed lung-gas volume
that exchanges agent with the breathing circuit (ventilation) and with
pulmonary blood (uptake), sitting between `circuit.py` and `patient.py`.

Both of those exchanges are terms of the alveolar balance in
`governing_equations.py`, and this class holds no method that applies either.
It had one - `apply_blood_uptake()`, which moved a signed amount of agent in
or out on a caller's say-so - and `PL-GS5X` removed it with the operator
split whose fifth sub-step was its only caller. Nothing outside the governing
equations may move agent between compartments: a mutator that can is a way to
reach a state that solves nothing, and it evaluated its own result twice and
accepted a `bool` where `parameters.py` refuses one (`PL-LKRP`).
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from anesthesia_sim.core.concentration import Fraction, require_fraction
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, require_alveolar_ventilation
from anesthesia_sim.core.validation import require_nonnegative_finite, require_positive_finite


@dataclass(frozen=True, slots=True)
class AlveolarCompartmentState:
    """The alveolar compartment's run state: what a step can change.

    Gas volume and alveolar ventilation are absent for the reason given on
    `BreathingCircuitState`: they are settings, not trajectory.
    """

    agent_amount_l: float


@dataclass(slots=True)
class AlveolarCompartment:
    """One ideal, perfectly mixed alveolar gas compartment.

    **`data/patients/reference_adult.json` is the authority for the first two
    fields, and this class is not.** Every shipped path builds the compartment
    through `AgentUptakeSystem.for_agent()`, which reads
    `alveolar_gas_volume_l` and `default_alveolar_ventilation_l_min` from that
    file and passes both explicitly, so the literals below are reached only by
    a bare unit-test construction of alveolar physics. They are kept as
    defaults rather than made required so that such a test does not have to
    load package data to exercise an equation - and
    `test_the_bare_alveolar_defaults_match_the_shipped_patient_file` in
    `tests/unit/test_alveolar.py` fails if the two ever disagree, because a
    reader meeting `2.5` here will take it for the model's alveolar volume
    whatever this paragraph says (`PL-DJYF`, seated on `PL-4YY1`, which found
    and fixed the same restatement on `BreathingCircuit`). The patient file
    also carries what is known about where each figure came from, which is
    that no primary measurement is adopted for either.

    Deliberately not solved by importing the loader here: `core/parameters.py`
    is the one module permitted to import Pydantic
    (`tools/import_boundary_check.py` enforces it), and reading package data at
    class-definition time would make a pure physics class depend on the
    installed distribution's files.
    """

    gas_volume_l: float = 2.5
    alveolar_ventilation_l_min: AlveolarVentilation = AlveolarVentilation(4.0)
    agent_amount_l: float = 0.0

    def __post_init__(self) -> None:
        # The ventilation's type was required as the constructor wrote the
        # field, by `__setattr__` below.
        require_positive_finite("gas_volume_l", self.gas_volume_l)
        require_nonnegative_finite("agent_amount_l", self.agent_amount_l)

        if self.agent_amount_l > self.gas_volume_l:
            raise SimulationConfigurationError(
                "agent_amount_l exceeds the alveolar capacity for a concentration fraction of 1"
            )

    if not TYPE_CHECKING:  # pragma: no branch - TYPE_CHECKING is False at run time
        # Hidden from `mypy` on purpose. A class that defines `__setattr__` is
        # one `mypy` lets assign any attribute name, typed by the method's
        # `value`, so with the guard in view a misspelt field written in `src/`
        # would pass `--strict` and fail at run time against the slots - on
        # these three classes alone. Hidden, `mypy` reads the dataclass's
        # fields and their types as before, and this is the runtime half for
        # the callers it does not read; its three lines are checked by their
        # tests rather than by `mypy` (`PL-LBQY`, found at review).

        def __setattr__(self, name: str, value: object) -> None:
            """Write a field, refusing a ventilation that was not built as an `AlveolarVentilation`.

            The one place a ventilation is stored on the compartment is this
            field, so its type is required here, for the constructor, the setter
            and an assignment made past both alike, as `BreathingCircuit.__setattr__`
            explains (`PL-LBQY`). Nothing is written when it is refused.

            Raises:
                TypeError: `name` is `alveolar_ventilation_l_min` and `value` was
                    not built as an `AlveolarVentilation`
                    (`require_alveolar_ventilation`).
            """

            if name == "alveolar_ventilation_l_min":
                require_alveolar_ventilation(value)

            super().__setattr__(name, value)

    @property
    def partial_pressure_fraction(self) -> float:
        """The alveolar fraction $`F_A = M_A/V_A`$.

        `docs/MODEL.md` § "Gas compartments" is the definition. The alveolar
        capacity is $`V_A`$ with no partition coefficient, this being a gas
        phase, which is why the division is by the volume itself where the
        blood and tissue compartments divide by a `capacity_l`.
        """

        return self.agent_amount_l / self.gas_volume_l

    def set_alveolar_ventilation(self, alveolar_ventilation_l_min: AlveolarVentilation) -> None:
        """Change ventilation without changing stored alveolar agent.

        The ventilation arrives checked against the supported range, which
        its type was built through and nothing here checks again
        (`core/supported_ranges.py`); that it was built as the type is
        required by the write itself, in `__setattr__`.

        Raises:
            TypeError: `alveolar_ventilation_l_min` was not built as an
                `AlveolarVentilation`. Nothing is written when it is refused.
        """

        self.alveolar_ventilation_l_min = alveolar_ventilation_l_min

    def set_partial_pressure_fraction(self, partial_pressure_fraction: Fraction) -> None:
        """Set alveolar state from a partial-pressure-equivalent fraction.

        The fraction arrives checked against 0 to 1, which its type was built
        through and nothing here checks again (`core/concentration.py`).

        Raises:
            TypeError: `partial_pressure_fraction` was not built as a
                `Fraction`. Nothing is written when it is refused.
        """

        require_fraction("alveolar partial_pressure_fraction", partial_pressure_fraction)
        self.agent_amount_l = self.gas_volume_l * partial_pressure_fraction

    def capture_state(self) -> AlveolarCompartmentState:
        """Record run state so a failed step can be rolled back."""

        return AlveolarCompartmentState(agent_amount_l=self.agent_amount_l)

    def restore_state(self, state: AlveolarCompartmentState) -> None:
        """Restore run state previously captured by `capture_state()`.

        Assigns the field directly rather than going through
        `apply_blood_uptake()`, so that rolling back cannot itself raise;
        see `BreathingCircuit.restore_state()`.
        """

        self.agent_amount_l = state.agent_amount_l

    def reset(self) -> None:
        """Clear alveolar agent while preserving settings."""

        self.agent_amount_l = 0.0
