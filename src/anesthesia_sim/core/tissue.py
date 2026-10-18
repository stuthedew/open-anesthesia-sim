"""One perfusion-limited tissue group (e.g. vessel-rich, muscle, fat):
exchanges agent with arterial blood in proportion to its own blood flow,
independently of every other tissue group.
"""

from dataclasses import dataclass
from math import inf
from typing import TYPE_CHECKING

from anesthesia_sim.core.checked_number import shown
from anesthesia_sim.core.concentration import Fraction, require_fraction
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.exponential_approach import exponential_approach
from anesthesia_sim.core.supported_ranges import CardiacOutput, require_cardiac_output
from anesthesia_sim.core.units import SECONDS_PER_MINUTE
from anesthesia_sim.core.validation import (
    require_nonnegative_finite,
    require_positive_finite,
    require_room_for_the_agent_held,
)

PERFUSION_FRACTION_UPPER_BOUND = 1.0


@dataclass(frozen=True, slots=True)
class TissueGroupState:
    """One tissue group's run state: what a step can change.

    Name, volume, perfusion fraction and partition coefficients are absent
    for the reason given on `BreathingCircuitState`: they are parameters, not
    trajectory. A tissue group stores no blood flow at all. Its flow is its
    perfusion fraction of the patient's cardiac output, formed by
    `blood_flow_l_min_at` wherever it is read (`PL-HQF5`).
    """

    agent_amount_l: float


@dataclass(slots=True)
class TissueGroup:
    """One ideal, perfusion-limited tissue group."""

    name: str
    volume_l: float
    perfusion_fraction: float
    blood_gas_partition_coefficient: float
    tissue_gas_partition_coefficient: float
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
            """Write a field, refusing a value the tissue's constructor would refuse.

            Each field is stored in one place, its slot, so its check is made
            here, for the constructor, the setters, `advance` and an assignment
            made past them alike, as `BreathingCircuit.__setattr__` explains
            (`PL-LBQY`, `PL-19Y0`); `restore_state` is the one write made past
            it, and says why. Nothing is written when a value is refused, and
            the constructor makes no check of its own.

            The tissue's partial pressure is its agent amount divided by its
            capacity, the volume times the tissue:gas coefficient, so the three
            are held together: an amount above the capacity is refused, and so
            is a volume or a coefficient too small for the amount already held,
            which would put the partial pressure above one atmosphere with the
            amount's own check never consulted (`PL-544D`, found at review;
            `require_room_for_the_agent_held`). The constructor writes the
            amount last, after both factors have passed their own checks, so a
            factor is held to the amount only once there is one.

            The perfusion fraction is written once, when the group is built,
            and a later write is refused (`PL-Z0HN`). The patient checks that
            its three fractions sum to 1 only when it is built, and a tissue
            group does not know which patient it belongs to. So a fraction
            changed afterwards would move the group's blood flow, which is its
            fraction of the cardiac output, with no check that the flows still
            add up to the output. The new value is checked first, so a value
            the constructor would refuse is refused in the constructor's
            words. A copy and a pickle write the fraction onto a new group,
            which has none yet, so both still work.

            Raises:
                TypeError: `name` is `name` and `value` is not a `str`, or the
                    value written to any other field is not an `int` or a
                    `float` (`require_a_number`).
                SimulationConfigurationError: the name is blank; the volume, a
                    partition coefficient or the perfusion fraction is not
                    positive and finite, or the perfusion fraction is above 1;
                    the perfusion fraction is written to a group that already
                    has one; the agent amount is negative or not finite; or
                    the agent amount would be more than the tissue
                    holds at a partial pressure of one atmosphere, whichever of
                    the amount, the volume and the tissue:gas coefficient is
                    the one written.
            """

            if name == "name":
                if not isinstance(value, str):
                    raise TypeError(
                        f"name of {shown(value)} has type {type(value).__name__}, not str"
                    )

                if not value.strip():
                    raise SimulationConfigurationError("name must be a nonempty string")
            elif name == "volume_l":
                require_positive_finite(name, value)

                if hasattr(self, "agent_amount_l"):
                    require_room_for_the_agent_held(
                        name,
                        value,
                        value * self.tissue_gas_partition_coefficient,
                        self.agent_amount_l,
                        f"{self.name} tissue",
                        "Tissue compartments",
                    )
            elif name == "perfusion_fraction":
                require_positive_finite(name, value)

                if value > PERFUSION_FRACTION_UPPER_BOUND:
                    raise SimulationConfigurationError("perfusion_fraction must not exceed 1")

                if hasattr(self, "perfusion_fraction"):
                    raise SimulationConfigurationError(
                        f"the {self.name} tissue group's perfusion fraction of "
                        f"{self.perfusion_fraction} cannot be written again, as {value}, once "
                        "the group is built, because the patient checks that its tissue "
                        "fractions sum to 1 only when it is built (docs/MODEL.md, "
                        '"Tissue groups"): build a new patient with the new fractions'
                    )
            elif name == "blood_gas_partition_coefficient":
                require_positive_finite(name, value)
            elif name == "tissue_gas_partition_coefficient":
                require_positive_finite(name, value)

                if hasattr(self, "agent_amount_l"):
                    require_room_for_the_agent_held(
                        name,
                        value,
                        self.volume_l * value,
                        self.agent_amount_l,
                        f"{self.name} tissue",
                        "Tissue compartments",
                    )
            elif name == "agent_amount_l":
                require_nonnegative_finite(name, value)

                if value > self.capacity_l:
                    raise SimulationConfigurationError(
                        "agent_amount_l exceeds the tissue capacity for a concentration "
                        "fraction of 1"
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

        `docs/MODEL.md` § "Tissue compartments" is the definition. The stored
        coefficient is tissue:gas rather than tissue:blood, so this is one
        multiplication and the blood-referenced form is derived from it below
        rather than the other way round.
        """

        return self.volume_l * self.tissue_gas_partition_coefficient

    @property
    def tissue_blood_partition_coefficient(self) -> float:
        """Return the tissue:blood partition coefficient."""

        return self.tissue_gas_partition_coefficient / self.blood_gas_partition_coefficient

    @property
    def partial_pressure_fraction(self) -> float:
        """Return the tissue partial-pressure-equivalent fraction."""

        return self.agent_amount_l / self.capacity_l

    @property
    def venous_outflow_partial_pressure_fraction(self) -> float:
        """The partial-pressure fraction of the blood leaving this tissue.

        Returns `partial_pressure_fraction` unchanged, and is kept as a
        separate name rather than folded into its one caller because that
        equality is an assumption rather than an identity: `docs/MODEL.md`
        § "Assumptions" carries it as "tissue venous blood equilibrates with
        its tissue group", which holds because each group is perfusion
        limited. A diffusion-limited group would need a real calculation
        here, so the site that relies on the assumption is the site that
        should name it.

        It is a *second* quantity on this class rather than an alias, which
        is why it takes a prefix where the tissue's own fraction does not.
        The two agree only in partial pressure: the concentrations either
        side of the tissue-blood boundary differ by
        `tissue_blood_partition_coefficient`. That is the whole reason this
        model states every compartment in partial-pressure-equivalent
        fractions, and this property is where the choice pays for itself -
        written in concentrations, the same physiology would need the
        coefficient applied here.

        `PatientCompartments.tissue_return_partial_pressure_fraction` is the
        one caller, which flow-weights this across the three groups.
        """

        return self.partial_pressure_fraction

    def blood_flow_l_min_at(self, cardiac_output_l_min: CardiacOutput) -> float:
        """Return this group's blood flow $`Q_i = f_iQ`$ at a cardiac output, in L/min.

        The flow is the group's perfusion fraction of the cardiac output
        (`docs/MODEL.md` § "Tissue groups"), and this is the only place the
        product is formed. The group stores no flow of its own, so no write
        can leave its flow out of step with the output (`PL-HQF5`). Its
        callers pass the output of the patient the group belongs to.

        Raises:
            TypeError: `cardiac_output_l_min` was not built as a
                `CardiacOutput` (`core/supported_ranges.py`).
        """

        require_cardiac_output(cardiac_output_l_min)

        return cardiac_output_l_min * self.perfusion_fraction

    def time_constant_s(self, blood_flow_l_min: float) -> float:
        """The perfusion-limited tissue time constant $`\\tau_i = V_i\\lambda_{i:b}/Q_i`$.

        `docs/MODEL.md` § "Tissue uptake and return" defines it, and gives the
        zero-flow case this returns `inf` for: an unperfused tissue exchanges
        nothing, so it never reaches equilibrium. The seconds-per-minute factor
        is here because $`Q_i`$ is given in litres per minute while every time
        in the model is in seconds.

        The step does not read this. `core/governing_equations.py` carries the
        same quantity as `washin_rate_s`, its reciprocal, which states the
        zero-flow case without a branch; this is the form a reader of the
        specification is looking for.

        The flow $`Q_i`$ is an argument, because the group stores none. For a
        group in a patient, it is `blood_flow_l_min_at` the patient's cardiac
        output.

        Raises:
            TypeError: the flow is not an `int` or a `float`.
            SimulationConfigurationError: the flow is negative or not finite.
        """

        require_nonnegative_finite("blood_flow_l_min", blood_flow_l_min)

        if blood_flow_l_min == 0.0:
            return inf

        return (
            SECONDS_PER_MINUTE
            * self.volume_l
            * self.tissue_blood_partition_coefficient
            / blood_flow_l_min
        )

    def set_partial_pressure_fraction(self, partial_pressure_fraction: Fraction) -> None:
        """Set tissue state from a partial-pressure-equivalent fraction.

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
        """Advance exactly for a constant arterial fraction and blood flow.

        This tissue group's own closed form, and not how a run advances: the
        arterial fraction a run presents changes continuously, and the step
        that follows it is `AgentUptakeSystem.advance()`. The package
        docstring in `core/__init__.py` states the distinction;
        `core/exponential_approach.py` is the form the amount is advanced in,
        exact at zero flow with no branch here; `docs/MODEL.md` § "Tissue
        uptake and return" is the equation.

        Returns the signed change in tissue agent amount. A positive value
        represents uptake by the tissue. A negative value represents return
        from the tissue to blood.

        Raises:
            TypeError: the arterial fraction was not built as a `Fraction`,
                which is what checks it against 0 to 1
                (`core/concentration.py`).
            SimulationConfigurationError: `simulation_step_s` is not positive
                and finite, or `blood_flow_l_min` is negative or not finite.
                All three are checked before anything changes. Or the amount
                held is already past the capacity, which only a write past
                `__setattr__` can have stored: the amount advanced is written
                through it, at zero flow too, where it is the amount held,
                unchanged.
        """

        require_fraction("arterial_partial_pressure_fraction", arterial_partial_pressure_fraction)
        require_positive_finite("simulation_step_s", simulation_step_s)
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

        Writes the slot past `__setattr__`, so that rolling back cannot
        itself raise, for the reasons `AlveolarCompartment.restore_state`
        gives: the amount came off this tissue, a rollback refused partway
        would replace the step's own error and leave the compartments restored
        after this one holding the failed step, and a volume or coefficient
        moved under the held amount in the meantime, which since `PL-19Y0`
        only a write past its own guard can make, is left to the quotient the
        snapshot builds, which refuses it visibly (`PL-7DJK`; `PL-544D`, found
        at review).
        """

        object.__setattr__(self, "agent_amount_l", state.agent_amount_l)

    def reset(self) -> None:
        """Clear stored agent while preserving tissue parameters."""

        self.agent_amount_l = 0.0
