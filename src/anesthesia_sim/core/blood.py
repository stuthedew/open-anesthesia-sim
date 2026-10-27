"""The mixed-venous blood compartment, which pools the outflow of every tissue group.

The pool combines the flow-weighted outflow from every tissue group (see
`patient.py`). Under this model's flow-limited arterial simplification, that
blood then returns to the alveoli as the arterial input.
"""

from dataclasses import dataclass
from math import inf
from typing import TYPE_CHECKING

from anesthesia_sim.core.concentration import Fraction, require_fraction
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.exponential_approach import exponential_approach
from anesthesia_sim.core.numerical_envelope import (
    CompartmentVolume,
    PartitionCoefficient,
    require_coefficient,
    require_compartment_volume,
)
from anesthesia_sim.core.supported_ranges import require_compartment_step
from anesthesia_sim.core.units import SECONDS_PER_MINUTE
from anesthesia_sim.core.validation import (
    require_a_capacity_with_room_for_the_agent,
    require_nonnegative_finite,
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
    """One ideal, well-mixed venous blood compartment.

    The pool holds the patient's one blood:gas partition coefficient
    (`PL-DQL9`). The coefficient is a property of the blood, and the pool is the
    patient's blood. The tissue groups store none, and the patient passes this
    one to each tissue group's methods. `PatientCompartments.from_parameters`
    reads it from the agent's parameter file. The coefficient is written once,
    when the pool is built, so it cannot drift from the value the patient was
    built with.
    """

    volume_l: CompartmentVolume
    blood_gas_partition_coefficient: PartitionCoefficient
    agent_amount_l: float = 0.0

    if not TYPE_CHECKING:  # pragma: no branch - TYPE_CHECKING is False at run time
        # Hidden from `mypy` on purpose, as `AlveolarCompartment.__setattr__`
        # is. When a class defines `__setattr__`, `mypy` lets code assign any
        # attribute name, typed by the method's `value` parameter. So with this
        # guard visible, a misspelt field written in `src/` would pass
        # `--strict` and fail at run time against the slots. With the guard
        # hidden, `mypy` checks the dataclass's fields and their types as
        # before. This guard is the runtime check for the callers that `mypy`
        # does not check. Its lines are checked by their tests rather than by
        # `mypy` (`PL-LBQY`, found at review).

        def __setattr__(self, name: str, value: object) -> None:
            """Write a field, refusing a value that the pool's constructor would refuse.

            Each field is stored in one place, its slot. So the field's check runs here,
            and it applies alike to the constructor, the setters, `advance` and any
            direct assignment that bypasses them. `BreathingCircuit.__setattr__` explains
            this (`PL-LBQY`, `PL-19Y0`). `restore_state` is the one write that bypasses
            this method, and its docstring says why. Nothing is written when a value is
            refused, and the constructor makes no check of its own. Until `PL-19Y0`, the
            constructor made the only check. So an agent amount larger than the capacity
            could be written onto a pool that was already built. The amount was stored,
            and the pool then reported a partial pressure fraction of 1.0000001.

            The pool's partial pressure is its agent amount divided by its capacity, and
            the capacity is the volume times the blood:gas partition coefficient. So the
            three values are checked together. An amount above the capacity is refused.
            So is a volume too small for the amount the pool already holds
            (`require_room_for_the_agent_held`). The constructor writes the amount
            last, after the volume and the coefficient have passed their own checks. So
            the volume is checked against the amount only once an amount exists.

            The blood:gas coefficient is written once, when the pool is built, and a
            later write is refused (`PL-DQL9`). The tissue groups' tissue:blood
            coefficients are formed from it, and the patient checks them only when it is
            built or a compartment is replaced. A later write checks the new value first,
            so a value the constructor would refuse is refused in the constructor's words.
            A copy and a pickle write the coefficient onto a new pool, which has none
            yet, so both still work.

            The volume and the coefficient are checked types, built only inside the numerical
            envelope (`core/numerical_envelope.py`). So their product, the capacity, is
            positive and finite by construction. Before, each factor was checked only as
            positive and finite, and that did not guarantee a positive and finite
            product (`PL-8LQZ`, `PL-FNH3`, `PL-QX2G`). Each refusal names the pool as
            well as the field, as in `"venous volume_l"` (`PL-2TZT`).

            Raises:
                TypeError: the volume was not built as a `CompartmentVolume`, or the
                    coefficient as a `PartitionCoefficient`, or the agent amount is
                    not an `int` or a `float` (`require_a_number`).
                SimulationConfigurationError: the agent amount is negative or not
                    finite, or would be more than the pool holds at a partial
                    pressure of one atmosphere. The last check runs whichever of the
                    amount and the volume is written. Also raised when
                    the blood:gas coefficient is written to a pool that already has one.
            """

            # Every compartment holds an agent amount, and the tissue groups also hold a
            # volume and a blood:gas coefficient. So a refusal names the pool as well as
            # the field (`core/validation.py`, `PL-2TZT`).
            field = f"venous {name}"

            if name == "volume_l":
                require_compartment_volume(field, value)

                if hasattr(self, "blood_gas_partition_coefficient"):
                    require_a_capacity_with_room_for_the_agent(
                        field,
                        value,
                        value,
                        self.blood_gas_partition_coefficient,
                        getattr(self, "agent_amount_l", None),
                        "venous blood",
                        "Blood compartments",
                    )
            elif name == "blood_gas_partition_coefficient":
                require_coefficient(field, value)

                if hasattr(self, name):
                    raise SimulationConfigurationError(
                        f"the venous pool's blood:gas partition coefficient of "
                        f"{self.blood_gas_partition_coefficient} cannot be written again, as "
                        f"{value}, once the pool is built, because every tissue group's "
                        "tissue:blood coefficient is formed from it (docs/MODEL.md, "
                        '"Blood compartments"): build a new system for another agent'
                    )

                # The coefficient is written only onto a new pool, and the constructor, a copy
                # and a pickle all write the agent amount after it. So the amount's own write
                # checks it against the capacity that this coefficient gives.
            elif name == "agent_amount_l":
                require_nonnegative_finite(field, value)
                require_within_the_capacity(
                    field, value, self.capacity_l, "venous blood", "Blood compartments"
                )

            super().__setattr__(name, value)

        def __delattr__(self, name: str) -> None:
            """Refuse to delete any field.

            The write-once check above asks whether the pool already has a
            blood:gas coefficient. A coefficient deleted and written again would
            pass it, as `TissueGroup.__delattr__` explains for the perfusion
            fraction. No field of a built pool is ever meant to be absent, so
            every deletion is refused.

            Raises:
                SimulationConfigurationError: always.
            """

            raise SimulationConfigurationError(
                f"the venous pool's {name} cannot be deleted, because a value written after "
                "it would bypass the checks made when the pool is built: build a new patient"
            )

    @property
    def capacity_l(self) -> float:
        """Equivalent gas capacity at a fraction of one, $`V_v\\lambda_{b:g}`$.

        `docs/MODEL.md` § "Blood compartments" is the definition.
        """

        return self.volume_l * self.blood_gas_partition_coefficient

    @property
    def partial_pressure_fraction(self) -> float:
        """Return the venous partial-pressure-equivalent fraction."""

        return self.agent_amount_l / self.capacity_l

    def time_constant_s(self, blood_flow_l_min: float) -> float:
        """The venous mixing time constant $`\\tau_v = V_v/Q`$.

        `docs/MODEL.md` § "Venous blood" defines it. No partition coefficient
        appears, because the pool and the blood flowing through it are the same
        phase. So the $`\\lambda_{b:g}`$ in `capacity_l` cancels against the
        one in the flow term. That is the whole difference from the tissue
        group's time constant, and it is why this one is a mixing time rather
        than an uptake time.

        It is `inf` at zero flow, as the tissue group's time constant is:
        nothing circulates, so nothing mixes.

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
        """Set the venous state from an equilibrium fraction.

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
        tissues fill, and `AgentUptakeSystem.advance()` is the step that tracks
        that change. The package docstring in `core/__init__.py` explains the
        distinction. `core/exponential_approach.py` holds the formula that advances
        the amount. That formula is exact at zero flow, so this method needs no
        separate branch for zero flow. `docs/MODEL.md` § "Venous blood" gives the
        equation.

        Returns the signed change in venous agent amount.

        Raises:
            TypeError: the tissue return fraction was not built as a
                `Fraction`, which is the type that checks it lies in the range
                0 to 1 (`core/concentration.py`).
            SimulationConfigurationError: `blood_flow_l_min` is negative or not
                finite, or `simulation_step_s` is outside the range that
                `require_compartment_step` accepts (`PL-WP52`, `PL-YT3T`). The
                step must be positive and finite, no shorter than
                `MINIMUM_SIMULATION_STEP_S`, and no longer than the supported run
                length, `MAXIMUM_ELAPSED_SIMULATION_TIME_S`. These checks run
                before anything changes. The error is also raised when the amount
                held is already more than the capacity. Only a write that bypasses
                `__setattr__` can have stored such an amount. This method always
                writes the new amount through `__setattr__`, which refuses an
                amount greater than the capacity. It does so even at zero flow,
                where the new amount equals the amount held.
        """

        require_fraction(
            "venous tissue_return_partial_pressure_fraction",
            tissue_return_partial_pressure_fraction,
        )
        require_compartment_step("venous simulation_step_s", simulation_step_s)
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

        Writes the slot directly, bypassing `__setattr__`, so that rolling back
        cannot itself raise. `AlveolarCompartment.restore_state` gives the
        reasons. The amount was captured from this pool. A rollback rejected
        partway would replace the step's own error. The compartments due to be
        restored after this one would then still hold the failed step
        (`PL-544D`, `PL-19Y0`).
        """

        object.__setattr__(self, "agent_amount_l", state.agent_amount_l)

    def reset(self) -> None:
        """Clear venous agent while preserving parameters."""

        self.agent_amount_l = 0.0
