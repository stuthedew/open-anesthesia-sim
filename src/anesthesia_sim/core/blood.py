"""The mixed-venous blood compartment: pools flow-weighted outflow from every
tissue group (see `patient.py`) before it returns to the alveoli as the
arterial input, under this model's flow-limited arterial simplification.
"""

from dataclasses import dataclass
from math import inf
from typing import TYPE_CHECKING

from anesthesia_sim.core.concentration import Fraction, require_fraction
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.exponential_approach import exponential_approach
from anesthesia_sim.core.units import SECONDS_PER_MINUTE
from anesthesia_sim.core.validation import (
    require_nonnegative_finite,
    require_positive_finite,
    require_room_for_the_agent_held,
)


@dataclass(frozen=True, slots=True)
class VenousBloodCompartmentState:
    """The venous pool's run state: what a step can change.

    Volume, partition coefficient and blood flow are absent for the reason
    given on `TissueGroupState`.
    """

    agent_amount_l: float


@dataclass(slots=True)
class VenousBloodCompartment:
    """One ideal, well-mixed venous blood compartment."""

    volume_l: float
    blood_gas_partition_coefficient: float
    blood_flow_l_min: float
    agent_amount_l: float = 0.0

    if not TYPE_CHECKING:  # pragma: no branch - TYPE_CHECKING is False at run time
        # Hidden from `mypy` on purpose, as `AlveolarCompartment.__setattr__`
        # is: a class that defines `__setattr__` is one `mypy` lets assign any
        # attribute name, typed by the method's `value`, so with the guard in
        # view a misspelt field written in `src/` would pass `--strict` and
        # fail at run time against the slots. Hidden, `mypy` reads the
        # dataclass's fields and their types as before, and this is the
        # runtime half for the callers it does not read; its lines are checked
        # by their tests rather than by `mypy` (`PL-LBQY`, found at review).

        def __setattr__(self, name: str, value: object) -> None:
            """Write a field, refusing a value the pool's constructor would refuse.

            Each field is stored in one place, its slot, so its check is made
            here, for the constructor, the setters, `advance` and an assignment
            made past them alike, as `BreathingCircuit.__setattr__` explains
            (`PL-LBQY`, `PL-19Y0`); `restore_state` is the one write made past
            it, and says why. Nothing is written when a value is refused, and
            the constructor makes no check of its own. Until `PL-19Y0` the
            constructor was the only check, so an amount past the capacity
            written onto a built pool was stored and read back as a fraction of
            1.0000001.

            The pool's partial pressure is its agent amount divided by its
            capacity, the volume times the blood:gas coefficient, so the three
            are held together: an amount above the capacity is refused, and so
            is a volume or a coefficient too small for the amount already held
            (`require_room_for_the_agent_held`). The constructor writes the
            amount last, after both factors have passed their own checks, so a
            factor is held to the amount only once there is one. The relation
            the patient holds between this pool's blood flow and the cardiac
            output is the patient's, not this record's (`PatientCompartments`).

            Raises:
                TypeError: `value` is not an `int` or a `float`
                    (`require_a_number`).
                SimulationConfigurationError: the volume or the partition
                    coefficient is not positive and finite; the blood flow or
                    the agent amount is negative or not finite; or the agent
                    amount would be more than the pool holds at a partial
                    pressure of one atmosphere, whichever of the amount, the
                    volume and the coefficient is the one written.
            """

            if name == "volume_l":
                require_positive_finite(name, value)

                if hasattr(self, "agent_amount_l"):
                    require_room_for_the_agent_held(
                        name,
                        value,
                        value * self.blood_gas_partition_coefficient,
                        self.agent_amount_l,
                        "venous blood",
                        "Blood compartments",
                    )
            elif name == "blood_gas_partition_coefficient":
                require_positive_finite(name, value)

                if hasattr(self, "agent_amount_l"):
                    require_room_for_the_agent_held(
                        name,
                        value,
                        self.volume_l * value,
                        self.agent_amount_l,
                        "venous blood",
                        "Blood compartments",
                    )
            elif name == "blood_flow_l_min":
                require_nonnegative_finite(name, value)
            elif name == "agent_amount_l":
                require_nonnegative_finite(name, value)

                if value > self.capacity_l:
                    raise SimulationConfigurationError(
                        "agent_amount_l exceeds venous blood capacity"
                    )

            super().__setattr__(name, value)

    @property
    def capacity_l(self) -> float:
        """Equivalent gas capacity at a fraction of one, $`V_v\\lambda_{b:g}`$.

        `docs/MODEL.md` § "Blood compartments" is the definition.
        """

        return self.volume_l * self.blood_gas_partition_coefficient

    @property
    def partial_pressure_fraction(self) -> float:
        """Return partial-pressure-equivalent venous fraction."""

        return self.agent_amount_l / self.capacity_l

    @property
    def time_constant_s(self) -> float:
        """The venous mixing time constant $`\\tau_v = V_v/Q`$.

        `docs/MODEL.md` § "Venous blood" defines it. No partition coefficient
        appears: the pool and the blood flowing through it are the same phase,
        so the $`\\lambda_{b:g}`$ in `capacity_l` cancels against the one in
        the flow term. That is the whole difference from the tissue constant
        above, and it is why this one is a mixing time rather than an uptake
        time.

        `inf` at zero flow, as there: nothing circulates, so nothing mixes.
        """

        if self.blood_flow_l_min == 0.0:
            return inf

        return SECONDS_PER_MINUTE * self.volume_l / self.blood_flow_l_min

    def set_blood_flow(self, blood_flow_l_min: float) -> None:
        """Change blood flow without changing stored agent.

        Raises:
            TypeError: the flow is not an `int` or a `float`.
            SimulationConfigurationError: the flow is negative or not finite.
                Both are the write's own, in `__setattr__`, and nothing is
                written when it is refused.
        """

        self.blood_flow_l_min = blood_flow_l_min

    def set_partial_pressure_fraction(self, partial_pressure_fraction: Fraction) -> None:
        """Set venous state from an equilibrium fraction.

        Raises:
            TypeError: `partial_pressure_fraction` was not built as a
                `Fraction`, which is what checks it against 0 to 1
                (`core/concentration.py`). Nothing is written when it is
                refused.
        """

        require_fraction("venous partial_pressure_fraction", partial_pressure_fraction)
        self.agent_amount_l = self.capacity_l * partial_pressure_fraction

    def advance(
        self, tissue_return_partial_pressure_fraction: Fraction, simulation_step_s: float
    ) -> float:
        """Mix tissue return into venous blood exactly, for a constant return.

        This pool's own closed form, and not how a run advances: the tissue
        return a run presents changes continuously as the tissues fill, and
        the step that follows it is `AgentUptakeSystem.advance()`. The package
        docstring in `core/__init__.py` states the distinction;
        `core/exponential_approach.py` is the form the amount is advanced in,
        exact at zero flow with no branch here; `docs/MODEL.md` § "Venous
        blood" is the equation.

        Returns the signed change in venous agent amount.

        Raises:
            TypeError: the tissue return fraction was not built as a
                `Fraction`, which is what checks it against 0 to 1
                (`core/concentration.py`).
            SimulationConfigurationError: `simulation_step_s` is not positive
                and finite. Both are checked before anything changes.
        """

        require_fraction(
            "tissue_return_partial_pressure_fraction", tissue_return_partial_pressure_fraction
        )
        require_positive_finite("simulation_step_s", simulation_step_s)

        initial_amount_l = self.agent_amount_l
        self.agent_amount_l = exponential_approach(
            initial_amount_l,
            self.capacity_l * tissue_return_partial_pressure_fraction,
            simulation_step_s,
            self.time_constant_s,
        )

        return self.agent_amount_l - initial_amount_l

    def capture_state(self) -> VenousBloodCompartmentState:
        """Record run state so a failed step can be rolled back."""

        return VenousBloodCompartmentState(agent_amount_l=self.agent_amount_l)

    def restore_state(self, state: VenousBloodCompartmentState) -> None:
        """Restore run state previously captured by `capture_state()`.

        Writes the slot past `__setattr__`, so that rolling back cannot
        itself raise, for the reasons `AlveolarCompartment.restore_state`
        gives: the amount came off this pool, and a rollback refused partway
        would replace the step's own error and leave the compartments restored
        after this one holding the failed step (`PL-544D`, `PL-19Y0`).
        """

        object.__setattr__(self, "agent_amount_l", state.agent_amount_l)

    def reset(self) -> None:
        """Clear venous agent while preserving parameters."""

        self.agent_amount_l = 0.0
