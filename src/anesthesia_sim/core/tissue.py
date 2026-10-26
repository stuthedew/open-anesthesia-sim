"""One perfusion-limited tissue group, such as the vessel-rich group, muscle or fat.

The group exchanges agent with arterial blood in proportion to its own blood
flow, independently of every other tissue group.
"""

from dataclasses import dataclass
from math import inf
from typing import TYPE_CHECKING

from anesthesia_sim.core.checked_number import shown
from anesthesia_sim.core.concentration import Fraction, require_fraction
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.exponential_approach import exponential_approach
from anesthesia_sim.core.numerical_envelope import (
    CompartmentVolume,
    PartitionCoefficient,
    require_coefficient,
    require_compartment_volume,
    tissue_blood_partition_coefficient,
)
from anesthesia_sim.core.supported_ranges import (
    CardiacOutput,
    require_cardiac_output,
    require_compartment_step,
)
from anesthesia_sim.core.units import SECONDS_PER_MINUTE
from anesthesia_sim.core.validation import (
    require_a_capacity_with_room_for_the_agent,
    require_nonnegative_finite,
    require_positive_finite,
    require_within_the_capacity,
)

PERFUSION_FRACTION_UPPER_BOUND = 1.0


@dataclass(frozen=True, slots=True)
class TissueGroupState:
    """One tissue group's run state: what a step can change.

    The name, volume, perfusion fraction and partition coefficients are left
    out, for the reason given on `BreathingCircuitState`: they are parameters,
    not part of the trajectory. A tissue group stores no blood flow at all. Its
    flow is its perfusion fraction of the patient's cardiac output, which
    `blood_flow_l_min_at` computes wherever the flow is read (`PL-HQF5`).
    """

    agent_amount_l: float


@dataclass(slots=True)
class TissueGroup:
    """One ideal, perfusion-limited tissue group."""

    name: str
    volume_l: CompartmentVolume
    perfusion_fraction: float
    blood_gas_partition_coefficient: PartitionCoefficient
    tissue_gas_partition_coefficient: PartitionCoefficient
    agent_amount_l: float = 0.0

    if not TYPE_CHECKING:  # pragma: no branch - TYPE_CHECKING is False at run time
        # These methods are hidden from `mypy` on purpose, as
        # `AlveolarCompartment.__setattr__` is. For a class that defines
        # `__setattr__`, `mypy` allows assignment to any attribute name, typed
        # by the method's `value`. So if `mypy` could see the guard, a misspelt
        # field written in `src/` would pass `--strict` and then fail at run
        # time against the slots. With the methods hidden, `mypy` checks the
        # dataclass's fields and their types as before. The guard is the
        # run-time check for the callers that `mypy` does not check. Its lines
        # are checked by their tests rather than by `mypy` (`PL-LBQY`, found at
        # review).

        def __setattr__(self, name: str, value: object) -> None:
            """Write a field, refusing a value that the tissue's constructor would refuse.

            Each field is stored in one place, its slot. So the field's check runs here,
            and it applies alike to the constructor, the setters, `advance` and any
            direct assignment that bypasses them. `BreathingCircuit.__setattr__` explains
            this (`PL-LBQY`, `PL-19Y0`). `restore_state` is the one write that bypasses
            this method, and its docstring says why. Nothing is written when a value is
            refused, and the constructor makes no check of its own.

            The tissue's partial pressure is its agent amount divided by its capacity, and
            the capacity is the volume times the tissue:gas partition coefficient. So the
            three values are checked together. An amount above the capacity is refused.
            So is a volume or a coefficient too small for the amount the tissue already
            holds. Such a value would put the partial pressure above one atmosphere
            without the amount's own check ever running (`PL-544D`, found at review).
            `require_room_for_the_agent_held` makes this check. The constructor writes
            the amount last, after the volume and the coefficient have passed their own
            checks. So the volume and the coefficient are checked against the amount only
            once an amount exists.

            The volume and both coefficients are checked types, built only inside the
            numerical envelope (`core/numerical_envelope.py`). So the capacity is
            positive and finite by construction. Before, each factor was checked only as
            positive and finite, and that did not guarantee a positive and finite
            product (`PL-8LQZ`, `PL-FNH3`). The two coefficients are also checked against
            each other. Whichever is written second must leave a tissue:blood coefficient
            inside the envelope too, because the quotient of two coefficients inside it
            can lie far outside it (`PL-QX2G`).

            Each refusal names the group as well as the field, as in `"muscle volume_l"`,
            because all three groups hold every field (`PL-2TZT`).

            The perfusion fraction is written once, when the group is built, and a later
            write is refused (`PL-Z0HN`). The patient checks that its three fractions sum
            to 1 only when the patient is built, and a tissue group does not know which
            patient it belongs to. A fraction changed afterwards would change the group's
            blood flow, which is its fraction of the cardiac output. Nothing would then
            check that the flows still add up to the cardiac output. A later write checks
            the new value first, so a value that the constructor would refuse is refused
            in the constructor's words. A copy and a pickle write the fraction onto a new
            group, which has none yet, so both still work.

            Raises:
                TypeError: the field written is `name` and `value` is not a `str`.
                    Also raised when the volume was not built as a
                    `CompartmentVolume`, or a coefficient as a
                    `PartitionCoefficient`, or when the value written to any other
                    field is not an `int` or a `float` (`require_a_number`).
                SimulationConfigurationError: the name is blank. Also raised when
                    the perfusion fraction is not positive and finite, or is above
                    1, or is written to a group that already has one. Also raised
                    when the two coefficients would make a tissue:blood
                    coefficient outside the numerical envelope. Also raised when
                    the agent amount is negative or not finite, or would be more
                    than the tissue holds at a partial pressure of one atmosphere.
                    That last check applies whichever of the amount, the volume
                    and the tissue:gas coefficient is written.
            """

            if name == "name":
                if not isinstance(value, str):
                    raise TypeError(
                        f"name of {shown(value)} has type {type(value).__name__}, not str"
                    )

                if not value.strip():
                    raise SimulationConfigurationError("name must be a nonempty string")

                super().__setattr__(name, value)

                return

            # All three groups have every field below, so an error message names the
            # group as well as the field (`core/validation.py`, `PL-2TZT`). The
            # constructor writes the name first, so `self.name` is already set here.
            field = f"{self.name} {name}"
            compartment = f"{self.name} tissue"

            if name == "volume_l":
                require_compartment_volume(field, value)

                if hasattr(self, "tissue_gas_partition_coefficient"):
                    require_a_capacity_with_room_for_the_agent(
                        field,
                        value,
                        value,
                        self.tissue_gas_partition_coefficient,
                        getattr(self, "agent_amount_l", None),
                        compartment,
                        "Tissue compartments",
                    )
            elif name == "perfusion_fraction":
                require_positive_finite(field, value)

                if value > PERFUSION_FRACTION_UPPER_BOUND:
                    raise SimulationConfigurationError(f"{field} must not exceed 1")

                if hasattr(self, "perfusion_fraction"):
                    raise SimulationConfigurationError(
                        f"the {self.name} tissue group's perfusion fraction of "
                        f"{self.perfusion_fraction} cannot be written again, as {value}, once "
                        "the group is built, because the patient checks that its tissue "
                        "fractions sum to 1 only when it is built (docs/MODEL.md, "
                        '"Tissue groups"): build a new patient with the new fractions'
                    )
            elif name == "blood_gas_partition_coefficient":
                require_coefficient(field, value)

                if hasattr(self, "tissue_gas_partition_coefficient"):
                    tissue_blood_partition_coefficient(
                        self.tissue_gas_partition_coefficient,
                        value,
                        name=f"{self.name} tissue_blood_partition_coefficient",
                    )
            elif name == "tissue_gas_partition_coefficient":
                require_coefficient(field, value)
                # The constructor, a copy and a pickle write the blood:gas
                # coefficient and the volume first, so both are always there.
                tissue_blood_partition_coefficient(
                    value,
                    self.blood_gas_partition_coefficient,
                    name=f"{self.name} tissue_blood_partition_coefficient",
                )

                require_a_capacity_with_room_for_the_agent(
                    field,
                    value,
                    self.volume_l,
                    value,
                    getattr(self, "agent_amount_l", None),
                    compartment,
                    "Tissue compartments",
                )
            elif name == "agent_amount_l":
                require_nonnegative_finite(field, value)
                require_within_the_capacity(
                    field, value, self.capacity_l, compartment, "Tissue compartments"
                )

            super().__setattr__(name, value)

        def __delattr__(self, name: str) -> None:
            """Refuse to delete any field.

            The write-once check above asks whether the group already has a
            fraction. A fraction deleted and written again would pass it
            (`PL-Z0HN`, found at review). No field of a built group is ever
            meant to be absent, so every deletion is refused.

            Raises:
                SimulationConfigurationError: always.
            """

            raise SimulationConfigurationError(
                f"the {self.name} tissue group's {name} cannot be deleted, because a value "
                "written after it would bypass the checks made when the group is built: "
                "build a new patient"
            )

    @property
    def capacity_l(self) -> float:
        """Equivalent gas capacity at a tissue fraction of one, $`V_i\\lambda_{i:g}`$.

        `docs/MODEL.md` § "Tissue compartments" defines it. The stored
        coefficient is tissue:gas rather than tissue:blood, so the capacity is
        one multiplication. The tissue:blood coefficient is derived from the
        stored one below, rather than the other way round.
        """

        return self.volume_l * self.tissue_gas_partition_coefficient

    @property
    def tissue_blood_partition_coefficient(self) -> PartitionCoefficient:
        """Return the tissue:blood partition coefficient, $`\\lambda_{i:g}/\\lambda_{b:g}`$.

        `core/numerical_envelope.py` forms the quotient and builds it as a checked
        type. Every write of either factor has already checked that the quotient
        lies inside the envelope, so reading it here never raises.
        """

        return tissue_blood_partition_coefficient(
            self.tissue_gas_partition_coefficient,
            self.blood_gas_partition_coefficient,
            name=f"{self.name} tissue_blood_partition_coefficient",
        )

    @property
    def partial_pressure_fraction(self) -> float:
        """Return the tissue partial-pressure-equivalent fraction."""

        return self.agent_amount_l / self.capacity_l

    @property
    def venous_outflow_partial_pressure_fraction(self) -> float:
        """The partial-pressure fraction of the blood leaving this tissue.

        It returns `partial_pressure_fraction` unchanged. It is kept as a
        separate name, rather than folded into its one caller, because that
        equality is an assumption rather than an identity. `docs/MODEL.md`
        § "Assumptions" states it as "tissue venous blood equilibrates with
        its tissue group", which holds because each group is perfusion
        limited. A diffusion-limited group would need a real calculation
        here. So the place that relies on the assumption is the place that
        should name it.

        It is a *second* quantity on this class rather than an alias. That is
        why its name has a prefix and the tissue's own fraction does not. The
        two agree only in partial pressure. The concentrations on either side
        of the tissue-blood boundary differ by a factor of
        `tissue_blood_partition_coefficient`. That difference is the whole
        reason this model states every compartment in
        partial-pressure-equivalent fractions, and this property is where
        that choice pays for itself. Written in concentrations, the same
        physiology would need the coefficient applied here.

        The one caller is
        `PatientCompartments.tissue_return_partial_pressure_fraction`, which
        weights this value by each group's share of cardiac output and sums it
        across the three groups.
        """

        return self.partial_pressure_fraction

    def blood_flow_l_min_at(self, cardiac_output_l_min: CardiacOutput) -> float:
        """Return this group's blood flow $`Q_i = f_iQ`$ at a cardiac output, in L/min.

        The flow is the group's perfusion fraction of the cardiac output
        (`docs/MODEL.md` § "Tissue groups"), and this is the only place where
        the product is computed. The group stores no flow of its own, so no
        write can leave its flow out of step with the cardiac output
        (`PL-HQF5`). Its callers pass the cardiac output of the patient to
        which the group belongs.

        Raises:
            TypeError: `cardiac_output_l_min` was not built as a
                `CardiacOutput` (`core/supported_ranges.py`).
        """

        require_cardiac_output(cardiac_output_l_min)

        return cardiac_output_l_min * self.perfusion_fraction

    def time_constant_s(self, blood_flow_l_min: float) -> float:
        """The perfusion-limited tissue time constant $`\\tau_i = V_i\\lambda_{i:b}/Q_i`$.

        `docs/MODEL.md` § "Tissue uptake and return" defines it. That section
        also gives the zero-flow case, for which this method returns `inf`: an
        unperfused tissue exchanges nothing, so it never reaches equilibrium.
        The seconds-per-minute factor appears here because $`Q_i`$ is given in
        litres per minute, while every time in the model is in seconds.

        The simulation step does not call this method.
        `core/governing_equations.py` represents the same quantity as
        `washin_rate_s`, its reciprocal, which expresses the zero-flow case
        without a branch. This method gives the form that a reader of the
        specification looks for.

        The flow $`Q_i`$ is an argument, because the group stores none. For a
        group in a patient, the flow is what `blood_flow_l_min_at` returns for
        the patient's cardiac output.

        Raises:
            TypeError: the flow is not an `int` or a `float`.
            SimulationConfigurationError: the flow is negative or not finite.
        """

        require_nonnegative_finite(f"{self.name} blood_flow_l_min", blood_flow_l_min)

        if blood_flow_l_min == 0.0:
            return inf

        return (
            SECONDS_PER_MINUTE
            * self.volume_l
            * self.tissue_blood_partition_coefficient
            / blood_flow_l_min
        )

    def set_partial_pressure_fraction(self, partial_pressure_fraction: Fraction) -> None:
        """Set the tissue state from a partial-pressure-equivalent fraction.

        Raises:
            TypeError: `partial_pressure_fraction` was not built as a
                `Fraction`, which is what checks it against 0 to 1
                (`core/concentration.py`). Nothing is written when it is
                refused.
        """

        require_fraction(f"{self.name} partial_pressure_fraction", partial_pressure_fraction)
        self.agent_amount_l = self.capacity_l * partial_pressure_fraction

    def advance(
        self,
        arterial_partial_pressure_fraction: Fraction,
        simulation_step_s: float,
        blood_flow_l_min: float,
    ) -> float:
        """Advance the tissue exactly for a constant arterial fraction and blood flow.

        This method is the tissue group's own closed-form solution. It is not how
        a run advances. In a run, the arterial fraction changes continuously, and
        `AgentUptakeSystem.advance()` is the step that tracks that change. The
        package docstring in `core/__init__.py` explains the distinction.
        `core/exponential_approach.py` holds the formula that advances the amount.
        That formula is exact at zero flow, so this method needs no separate branch
        for zero flow. `docs/MODEL.md` § "Tissue uptake and return" gives the
        equation.

        Returns the signed change in tissue agent amount. A positive value
        represents uptake by the tissue. A negative value represents return
        from the tissue to blood.

        Raises:
            TypeError: the arterial fraction was not built as a `Fraction`,
                which is the type that checks it lies in the range 0 to 1
                (`core/concentration.py`).
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
            f"{self.name} arterial_partial_pressure_fraction", arterial_partial_pressure_fraction
        )
        require_compartment_step(f"{self.name} simulation_step_s", simulation_step_s)
        time_constant_s = self.time_constant_s(blood_flow_l_min)

        initial_amount_l = self.agent_amount_l
        self.agent_amount_l = exponential_approach(
            initial_amount_l,
            self.capacity_l * arterial_partial_pressure_fraction,
            simulation_step_s,
            time_constant_s,
        )

        return self.agent_amount_l - initial_amount_l

    def capture_state(self) -> TissueGroupState:
        """Record run state so a failed step can be rolled back."""

        return TissueGroupState(agent_amount_l=self.agent_amount_l)

    def restore_state(self, state: TissueGroupState) -> None:
        """Restore run state previously captured by `capture_state()`.

        It writes the slot directly, bypassing `__setattr__`, so that rolling
        back cannot itself raise. The reasons are those that
        `AlveolarCompartment.restore_state` gives. The amount was captured
        from this tissue, so a rollback must restore exactly that amount. A
        rollback refused partway would replace the step's own error, and
        would leave the compartments restored after this one still holding
        the failed step. The guard could refuse only if a volume or
        coefficient had been changed in the meantime so that the capacity is
        less than the stored amount. Since `PL-19Y0`, only a write that
        bypasses that value's own guard can make such a change. The quotient
        that the snapshot builds then rejects it, visibly (`PL-7DJK`;
        `PL-544D`, found at review).
        """

        object.__setattr__(self, "agent_amount_l", state.agent_amount_l)

    def reset(self) -> None:
        """Clear stored agent while preserving tissue parameters."""

        self.agent_amount_l = 0.0
