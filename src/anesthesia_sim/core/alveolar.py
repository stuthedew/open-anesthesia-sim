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
from anesthesia_sim.core.validation import (
    require_nonnegative_finite,
    require_positive_finite,
    require_room_for_the_agent_held,
)


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

    if not TYPE_CHECKING:  # pragma: no branch - TYPE_CHECKING is False at run time
        # Hidden from `mypy` on purpose. A class that defines `__setattr__` is
        # one `mypy` lets assign any attribute name, typed by the method's
        # `value`, so with the guard in view a misspelt field written in `src/`
        # would pass `--strict` and fail at run time against the slots - on
        # the classes that define one alone. Hidden, `mypy` reads the
        # dataclass's fields and their types as before, and this is the
        # runtime half for the callers it does not read; its lines are checked
        # by their tests rather than by `mypy` (`PL-LBQY`, found at review).

        def __setattr__(self, name: str, value: object) -> None:
            """Write a field, refusing a value the compartment's constructor would refuse.

            Each field is stored in one place, its slot, so its check is made
            here, for the constructor, the setters and an assignment made past
            them alike, as `BreathingCircuit.__setattr__` explains (`PL-LBQY`,
            `PL-19Y0`). Nothing is written when a value is refused, and the
            constructor makes no check of its own. `restore_state` is the one
            write of the amount made past this, and says why.

            The alveolar partial pressure is the agent amount divided by the
            gas volume, so the two are held together, by whichever is written
            second: an amount above the volume is refused, and so is a volume
            too small for the amount already held. That relation is the
            compartment's to check rather than either quantity's
            (`.claude/rules/core-domain.md`). Until `PL-544D` the constructor
            and `set_partial_pressure_fraction` each made it while an
            assignment made past both did not, so an amount past the volume - a
            partial pressure above one atmosphere - was stored, and refused
            only when `SimulationController.snapshot()` built the fraction two
            layers later (`PL-7DJK`). Until `PL-19Y0` a volume too small for
            the amount held was written the same way: 1e-6 L under 0.098 L of
            sevoflurane completed the next step and propagated a partial
            pressure near 98,000 atmospheres into every other compartment
            (`PL-544D`, found at review). The constructor writes the volume
            first, so it is held to the amount only once there is one.

            Raises:
                TypeError: `name` is `alveolar_ventilation_l_min` and `value`
                    was not built as an `AlveolarVentilation`
                    (`require_alveolar_ventilation`); or the volume or the
                    amount is not an `int` or a `float` (`require_a_number`).
                SimulationConfigurationError: the volume is not positive and
                    finite; the amount is negative or not finite; or the
                    amount would be more than `gas_volume_l`, what the
                    compartment holds at a partial pressure of one atmosphere,
                    whichever of the two is the one written.
            """

            if name == "gas_volume_l":
                require_positive_finite(name, value)

                if hasattr(self, "agent_amount_l"):
                    require_room_for_the_agent_held(
                        name,
                        value,
                        value,
                        self.agent_amount_l,
                        "alveolar compartment",
                        "Gas compartments",
                    )
            elif name == "alveolar_ventilation_l_min":
                require_alveolar_ventilation(value)
            elif name == "agent_amount_l":
                require_nonnegative_finite(name, value)

                if value > self.gas_volume_l:
                    raise SimulationConfigurationError(
                        "agent_amount_l exceeds the alveolar capacity for a concentration "
                        "fraction of 1"
                    )

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

        Writes the slot past `__setattr__`, so that rolling back cannot
        itself raise; see `BreathingCircuit.restore_state()`. The amount came
        off this compartment, and what a rollback owes the step is that state
        back exactly: a rollback refused partway would replace the step's own
        error and leave the compartments restored after this one holding the
        failed step (`AgentUptakeSystem.restore_state`). The one way the guard
        could refuse it is a volume moved under the held amount in the
        meantime, which since `PL-19Y0` only a write past the volume's own
        guard can make; the state restored is then the one the step began
        from, over capacity as it already was, and the quotient the snapshot
        builds from it is what refuses it, visibly (`PL-7DJK`; `PL-544D`,
        found at review).
        """

        object.__setattr__(self, "agent_amount_l", state.agent_amount_l)

    def reset(self) -> None:
        """Clear alveolar agent while preserving settings."""

        self.agent_amount_l = 0.0
