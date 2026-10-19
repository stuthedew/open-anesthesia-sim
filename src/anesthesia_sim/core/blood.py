"""The mixed-venous blood compartment: pools flow-weighted outflow from every
tissue group (see `patient.py`) before it returns to the alveoli as the
arterial input, under this model's flow-limited arterial simplification.
"""

from dataclasses import dataclass
from math import inf
from typing import TYPE_CHECKING

from anesthesia_sim.core.concentration import Fraction, require_fraction
from anesthesia_sim.core.exponential_approach import exponential_approach
from anesthesia_sim.core.simulation_step import require_at_least_the_smallest_step
from anesthesia_sim.core.units import SECONDS_PER_MINUTE
from anesthesia_sim.core.validation import (
    require_a_capacity,
    require_nonnegative_finite,
    require_positive_finite,
    require_room_for_the_agent_held,
    require_within_the_capacity,
)


@dataclass(frozen=True, slots=True)
class VenousBloodCompartmentState:
    """The venous pool's run state: what a step can change.

    Volume and partition coefficient are absent for the reason given on
    `TissueGroupState`. The pool stores no blood flow at all: its flow is the
    patient's cardiac output, which only the patient stores (`PL-HQF5`).
    """

    agent_amount_l: float


@dataclass(slots=True)
class VenousBloodCompartment:
    """One ideal, well-mixed venous blood compartment."""

    volume_l: float
    blood_gas_partition_coefficient: float
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

            Each field is stored in one place, its slot. So the field's check runs here,
            and it applies alike to the constructor, the setters, `advance` and any
            direct assignment that bypasses them. `BreathingCircuit.__setattr__` explains
            this (`PL-LBQY`, `PL-19Y0`). `restore_state` is the one write that bypasses
            this method, and its docstring says why. Nothing is written when a value is
            refused, and the constructor makes no check of its own. Until `PL-19Y0`, the
            constructor made the only check. So an agent amount larger than the capacity,
            written onto a pool already built, was stored, and the pool then reported a
            partial pressure fraction of 1.0000001.

            The pool's partial pressure is its agent amount divided by its capacity, and
            the capacity is the volume times the blood:gas partition coefficient. So the
            three values are checked together. An amount above the capacity is refused.
            So is a volume or a coefficient too small for the amount the pool already
            holds (`require_room_for_the_agent_held`). The constructor writes the amount
            last, after the volume and the coefficient have passed their own checks. So
            a factor is checked against the amount only once an amount exists. The volume
            and the coefficient are also checked against each other, as a tissue group's
            are. Whichever is written second must leave a capacity that is positive and
            finite (`require_a_capacity`, `PL-8LQZ`, `PL-FNH3`). Each refusal names the
            pool as well as the field, as in `"venous volume_l"` (`PL-2TZT`).

            Raises:
                TypeError: `value` is not an `int` or a `float`
                    (`require_a_number`).
                SimulationConfigurationError: the volume or the partition
                    coefficient is not positive and finite, or the two multiply
                    to a capacity that is zero or not finite. Also raised when
                    the agent amount is negative or not finite, or would be more
                    than the pool holds at a partial pressure of one atmosphere.
                    That last check applies whichever of the amount, the volume
                    and the coefficient is written.
            """

            # Every compartment holds an agent amount, and the tissue groups also hold a
            # volume and a blood:gas coefficient. So a refusal names the pool as well as
            # the field (`core/validation.py`, `PL-2TZT`).
            field = f"venous {name}"

            if name == "volume_l":
                require_positive_finite(field, value)

                if hasattr(self, "blood_gas_partition_coefficient"):
                    require_a_capacity(
                        field,
                        value,
                        value,
                        self.blood_gas_partition_coefficient,
                        "venous blood",
                        "Blood compartments",
                    )

                if hasattr(self, "agent_amount_l"):
                    require_room_for_the_agent_held(
                        field,
                        value,
                        value * self.blood_gas_partition_coefficient,
                        self.agent_amount_l,
                        "venous blood",
                        "Blood compartments",
                    )
            elif name == "blood_gas_partition_coefficient":
                require_positive_finite(field, value)

                # The constructor, a copy and a pickle write the volume
                # first, so it is always there to multiply.
                require_a_capacity(
                    field, value, self.volume_l, value, "venous blood", "Blood compartments"
                )

                if hasattr(self, "agent_amount_l"):
                    require_room_for_the_agent_held(
                        field,
                        value,
                        self.volume_l * value,
                        self.agent_amount_l,
                        "venous blood",
                        "Blood compartments",
                    )
            elif name == "agent_amount_l":
                require_nonnegative_finite(field, value)
                require_within_the_capacity(
                    field, value, self.capacity_l, "venous blood", "Blood compartments"
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

    def time_constant_s(self, blood_flow_l_min: float) -> float:
        """The venous mixing time constant $`\\tau_v = V_v/Q`$.

        `docs/MODEL.md` § "Venous blood" defines it. No partition coefficient
        appears: the pool and the blood flowing through it are the same phase,
        so the $`\\lambda_{b:g}`$ in `capacity_l` cancels against the one in
        the flow term. That is the whole difference from the tissue constant
        above, and it is why this one is a mixing time rather than an uptake
        time.

        `inf` at zero flow, as there: nothing circulates, so nothing mixes.

        The flow $`Q`$ is an argument, because the pool stores none. For the
        pool in a patient, it is the patient's cardiac output.

        Raises:
            TypeError: the flow is not an `int` or a `float`.
            SimulationConfigurationError: the flow is negative or not finite.
        """

        require_nonnegative_finite("venous blood_flow_l_min", blood_flow_l_min)

        if blood_flow_l_min == 0.0:
            return inf

        return SECONDS_PER_MINUTE * self.volume_l / blood_flow_l_min

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
        self,
        tissue_return_partial_pressure_fraction: Fraction,
        simulation_step_s: float,
        blood_flow_l_min: float,
    ) -> float:
        """Mix tissue return into venous blood exactly, for a constant return and flow.

        This method is the venous pool's own closed-form solution. It is not how a
        run advances. In a run, the tissue return changes continuously as the
        tissues fill, and `AgentUptakeSystem.advance()` is the step that follows
        that change. The package docstring in `core/__init__.py` explains the
        distinction. `core/exponential_approach.py` holds the form in which the
        amount is advanced. That form is exact at zero flow, so this method needs
        no separate branch for it. `docs/MODEL.md` § "Venous blood" gives the
        equation.

        Returns the signed change in venous agent amount.

        Raises:
            TypeError: the tissue return fraction was not built as a
                `Fraction`, which is the type that checks it lies in the range
                0 to 1 (`core/concentration.py`).
            SimulationConfigurationError: `simulation_step_s` is not positive
                and finite, or is shorter than `MINIMUM_SIMULATION_STEP_S`
                (`core/simulation_step.py`, `PL-WP52`), or `blood_flow_l_min` is
                negative or not finite. These checks run before anything
                changes. The error is also raised when the amount held is
                already more than the capacity. Only a write that bypasses
                `__setattr__` can have stored such an amount. The new amount is
                always written through `__setattr__`, which refuses an amount
                past the capacity. That includes zero flow, where the new amount
                is the amount held, unchanged.
        """

        require_fraction(
            "venous tissue_return_partial_pressure_fraction",
            tissue_return_partial_pressure_fraction,
        )
        require_at_least_the_smallest_step("venous simulation_step_s", simulation_step_s)
        time_constant_s = self.time_constant_s(blood_flow_l_min)

        initial_amount_l = self.agent_amount_l
        self.agent_amount_l = exponential_approach(
            initial_amount_l,
            self.capacity_l * tissue_return_partial_pressure_fraction,
            simulation_step_s,
            time_constant_s,
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
