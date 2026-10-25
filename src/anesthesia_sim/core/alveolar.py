"""The alveolar gas compartment, one ideal and perfectly mixed volume of lung gas.

The compartment sits between `circuit.py` and `patient.py`. It exchanges agent
with the breathing circuit through ventilation, and with pulmonary blood
through uptake.

Both of those exchanges are terms of the alveolar balance in
`governing_equations.py`, and this class has no method that applies either.
It once had one, `apply_blood_uptake()`, which moved a signed amount of agent
in or out whenever a caller asked. `PL-GS5X` removed it together with the
operator split whose fifth sub-step was its only caller. Nothing outside the
governing equations may move agent between compartments. A method that can do
so is a way to reach a state that does not solve those equations. That method
also evaluated its own result twice, and it accepted a `bool` where
`parameters.py` rejects one (`PL-LKRP`).
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from anesthesia_sim.core.concentration import Fraction, require_fraction
from anesthesia_sim.core.numerical_envelope import CompartmentVolume, require_compartment_volume
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, require_alveolar_ventilation
from anesthesia_sim.core.validation import (
    require_nonnegative_finite,
    require_room_for_the_agent_held,
    require_within_the_capacity,
)


@dataclass(frozen=True, slots=True)
class AlveolarCompartmentState:
    """The alveolar compartment's run state: what a step can change.

    Gas volume and alveolar ventilation are absent for the reason given on
    `BreathingCircuitState`: they are settings, not part of the trajectory.
    """

    agent_amount_l: float


@dataclass(slots=True)
class AlveolarCompartment:
    """One ideal, perfectly mixed alveolar gas compartment.

    **`data/patients/reference_adult.json` is the authority for the first two
    fields, and this class is not.** Every shipped path builds the compartment
    through `AgentUptakeSystem.for_agent()`, which reads
    `alveolar_gas_volume_l` and `default_alveolar_ventilation_l_min` from that
    file and passes both. Neither field has a default, so every caller must
    state the value it means (`PL-M85T`). Before `PL-M85T`, each field
    defaulted to a second copy of the file's value, 2.5 L and 4.0 L/min. Only
    a test kept each copy equal to the file (`PL-DJYF`). The patient file also
    records what is known about where each figure came from: no primary
    measurement is adopted for either.
    """

    gas_volume_l: CompartmentVolume
    alveolar_ventilation_l_min: AlveolarVentilation
    agent_amount_l: float = 0.0

    if not TYPE_CHECKING:  # pragma: no branch - TYPE_CHECKING is False at run time
        # Hidden from `mypy` on purpose. When a class defines `__setattr__`,
        # `mypy` lets code assign any attribute name, typed by the method's
        # `value` parameter. So with this guard visible, a misspelt field
        # written in `src/` would pass `--strict` and fail at run time against
        # the slots. That happens only on the classes that define
        # `__setattr__`. With the guard hidden, `mypy` checks the dataclass's
        # fields and their types as before. This guard is the runtime check for
        # the callers that `mypy` does not check. Its lines are checked by
        # their tests rather than by `mypy` (`PL-LBQY`, found at review).

        def __setattr__(self, name: str, value: object) -> None:
            """Write a field, refusing a value that the compartment's constructor would refuse.

            Each field is stored in one place, its slot. So the field's check is made
            here, and it applies alike to the constructor, the setters and a direct
            assignment that bypasses them. `BreathingCircuit.__setattr__` explains this
            (`PL-LBQY`, `PL-19Y0`). Nothing is written when a value is rejected, and the
            constructor makes no check of its own. `restore_state` is the one write of
            the amount that bypasses this method, and its docstring says why.

            The alveolar partial pressure is the agent amount divided by the gas
            volume. So the two are checked together, by whichever is written second. An
            amount above the volume is rejected, and so is a volume too small for the
            amount already held. The compartment checks this relation, because it
            belongs to neither quantity alone (`.claude/rules/core-domain.md`). Until
            `PL-544D`, the constructor and `set_partial_pressure_fraction` each checked
            the relation, but a direct assignment that bypassed both did not. So an
            amount larger than the volume was stored, although it means a partial
            pressure above one atmosphere. It was rejected only two layers later, when
            `SimulationController.snapshot()` built the fraction (`PL-7DJK`). Until
            `PL-19Y0`, a volume too small for the amount held was stored the same way.
            In one case, a volume of 1e-6 L was written while the compartment held
            0.098 L of sevoflurane. The next step began at a partial pressure near
            98,000 atmospheres. At the end of that step every fraction looked plausible
            but was wrong, and the accounting check still passed (`PL-544D`, found at
            review). `require_room_for_the_agent_held` has the figures. The constructor
            writes the volume first, so the volume is checked against the amount only
            once an amount exists.

            Raises:
                TypeError: `name` is `alveolar_ventilation_l_min` and `value` was
                    not built as an `AlveolarVentilation`
                    (`require_alveolar_ventilation`). Also raised when the volume was
                    not built as a `CompartmentVolume`, which checks it against the
                    numerical envelope (`core/numerical_envelope.py`), or when the
                    amount is not an `int` or a `float` (`require_a_number`).
                SimulationConfigurationError: the amount is negative or not finite.
                    Also raised when the amount would be more than `gas_volume_l`,
                    which is what the compartment holds at a partial pressure of one
                    atmosphere. This last check runs whichever of the amount and the
                    volume is written.
            """

            if name == "gas_volume_l":
                require_compartment_volume(name, value)

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
                # Every compartment holds an agent amount, so the error message
                # names this compartment (`core/validation.py`, `PL-2TZT`).
                require_nonnegative_finite("alveolar agent_amount_l", value)
                require_within_the_capacity(
                    "alveolar agent_amount_l",
                    value,
                    self.gas_volume_l,
                    "alveolar compartment",
                    "Gas compartments",
                )

            super().__setattr__(name, value)

    @property
    def partial_pressure_fraction(self) -> float:
        """The alveolar fraction $`F_A = M_A/V_A`$.

        `docs/MODEL.md` § "Gas compartments" is the definition. The alveolar
        capacity is $`V_A`$, with no partition coefficient, because this is a
        gas phase. That is why this property divides by the volume itself,
        where the blood and tissue compartments divide by a `capacity_l`.
        """

        return self.agent_amount_l / self.gas_volume_l

    def set_alveolar_ventilation(self, alveolar_ventilation_l_min: AlveolarVentilation) -> None:
        """Change ventilation without changing stored alveolar agent.

        The ventilation arrives already checked against the supported range,
        because its type can only be built through that check. Nothing here
        checks it again (`core/supported_ranges.py`). The write itself, in
        `__setattr__`, requires that the value was built as that type.

        Raises:
            TypeError: `alveolar_ventilation_l_min` was not built as an
                `AlveolarVentilation`. Nothing is written when it is refused.
        """

        self.alveolar_ventilation_l_min = alveolar_ventilation_l_min

    def set_partial_pressure_fraction(self, partial_pressure_fraction: Fraction) -> None:
        """Set alveolar state from a partial-pressure-equivalent fraction.

        The fraction arrives already checked against 0 to 1, because its type
        can only be built through that check. Nothing here checks the range
        again (`core/concentration.py`).

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

        Writes the slot directly, bypassing `__setattr__`, so that rolling back
        cannot itself raise (see `BreathingCircuit.restore_state()`). The
        amount was captured from this compartment, and a rollback owes the step
        exactly that state back. A rollback rejected partway would replace the
        step's own error. The compartments due to be restored after this one
        would then still hold the failed step (`AgentUptakeSystem.restore_state`).
        The guard could reject the restore in only one case: if the volume had
        been moved below the held amount in the meantime. Since `PL-19Y0`, only
        a write that bypasses the volume's own guard can do that. The state
        restored is then the one the step began from, already over capacity.
        The fraction that the snapshot computes from it is what rejects it,
        visibly (`PL-7DJK`; `PL-544D`, found at review).
        """

        object.__setattr__(self, "agent_amount_l", state.agent_amount_l)

    def reset(self) -> None:
        """Clear alveolar agent while preserving settings."""

        self.agent_amount_l = 0.0
