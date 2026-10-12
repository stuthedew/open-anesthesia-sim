"""One perfusion-limited tissue group (e.g. vessel-rich, muscle, fat):
exchanges agent with arterial blood in proportion to its own blood flow,
independently of every other tissue group.
"""

from dataclasses import dataclass
from math import inf
from typing import TYPE_CHECKING

from anesthesia_sim.core.checked_number import require_a_number
from anesthesia_sim.core.concentration import Fraction, require_fraction
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.exponential_approach import exponential_approach
from anesthesia_sim.core.units import SECONDS_PER_MINUTE
from anesthesia_sim.core.validation import require_nonnegative_finite, require_positive_finite

PERFUSION_FRACTION_UPPER_BOUND = 1.0


@dataclass(frozen=True, slots=True)
class TissueGroupState:
    """One tissue group's run state: what a step can change.

    Name, volume, perfusion fraction, partition coefficients and blood flow
    are absent for the reason given on `BreathingCircuitState`: they are
    parameters and settings, not trajectory. Blood flow in particular is
    derived from cardiac output by `PatientCompartments`, and restoring it
    from a snapshot would undo a cardiac-output change the user made.
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
    blood_flow_l_min: float = 0.0
    agent_amount_l: float = 0.0

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise SimulationConfigurationError("name must be a nonempty string")

        require_positive_finite("volume_l", self.volume_l)
        require_positive_finite("perfusion_fraction", self.perfusion_fraction)

        if self.perfusion_fraction > PERFUSION_FRACTION_UPPER_BOUND:
            raise SimulationConfigurationError("perfusion_fraction must not exceed 1")

        require_positive_finite(
            "blood_gas_partition_coefficient", self.blood_gas_partition_coefficient
        )
        require_positive_finite(
            "tissue_gas_partition_coefficient", self.tissue_gas_partition_coefficient
        )
        require_nonnegative_finite("blood_flow_l_min", self.blood_flow_l_min)
        # The agent amount's range was required as the constructor wrote the
        # field, by `__setattr__` below.

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
            """Write a field, refusing an agent amount the tissue cannot hold.

            The one place the amount is stored is this field, so the capacity
            is held here, for the constructor, `set_partial_pressure_fraction`,
            `advance` and an assignment made past them alike, as
            `AlveolarCompartment.__setattr__` explains (`PL-544D`);
            `restore_state` is the one write made past it, and says why.
            Nothing is written when it is refused. The constructor writes the
            amount before `__post_init__` has refused a bad volume or
            coefficient, so each is required to be a number here first, under
            its own name (`require_a_number`), and a capacity that is not
            positive is then left to that refusal, under the parameter's own
            name, rather than read here as the amount exceeding it.

            Raises:
                TypeError: `name` is `agent_amount_l` and `value`, `volume_l`
                    or `tissue_gas_partition_coefficient` is not an `int` or a
                    `float` (`require_nonnegative_finite`, `require_a_number`).
                SimulationConfigurationError: `name` is `agent_amount_l` and
                    `value` is negative, not finite, or more than `capacity_l`,
                    the capacity at a fraction of one.
            """

            if name == "agent_amount_l":
                require_nonnegative_finite(name, value)
                require_a_number("volume_l", self.volume_l)
                require_a_number(
                    "tissue_gas_partition_coefficient", self.tissue_gas_partition_coefficient
                )

                if 0.0 < self.capacity_l < value:
                    raise SimulationConfigurationError(
                        "agent_amount_l exceeds the tissue capacity for a concentration "
                        "fraction of 1"
                    )

            super().__setattr__(name, value)

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

    @property
    def time_constant_s(self) -> float:
        """The perfusion-limited tissue time constant $`\\tau_i = V_i\\lambda_{i:b}/Q_i`$.

        `docs/MODEL.md` § "Tissue uptake and return" defines it, and gives the
        zero-flow case this returns `inf` for: an unperfused tissue exchanges
        nothing, so it never reaches equilibrium. The seconds-per-minute factor
        is here because $`Q_i`$ is held in litres per minute at this boundary
        while every time in the model is in seconds.

        The step does not read this. `core/governing_equations.py` carries the
        same quantity as `washin_rate_s`, its reciprocal, which states the
        zero-flow case without a branch; this is the form a reader of the
        specification is looking for.
        """

        if self.blood_flow_l_min == 0.0:
            return inf

        return (
            SECONDS_PER_MINUTE
            * self.volume_l
            * self.tissue_blood_partition_coefficient
            / self.blood_flow_l_min
        )

    def set_blood_flow(self, blood_flow_l_min: float) -> None:
        """Change tissue blood flow without changing stored agent."""

        require_nonnegative_finite("blood_flow_l_min", blood_flow_l_min)
        self.blood_flow_l_min = blood_flow_l_min

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
        self, arterial_partial_pressure_fraction: Fraction, simulation_step_s: float
    ) -> float:
        """Advance exactly for constant arterial fraction and blood flow.

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
                and finite. Both are checked before anything changes.
        """

        require_fraction("arterial_partial_pressure_fraction", arterial_partial_pressure_fraction)
        require_positive_finite("simulation_step_s", simulation_step_s)

        initial_amount_l = self.agent_amount_l
        self.agent_amount_l = exponential_approach(
            initial_amount_l,
            self.capacity_l * arterial_partial_pressure_fraction,
            simulation_step_s,
            self.time_constant_s,
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
        written under the held amount in the meantime (`PL-19Y0`) is left to
        the quotient the snapshot builds, which refuses it visibly (`PL-7DJK`;
        `PL-544D`, found at review).
        """

        object.__setattr__(self, "agent_amount_l", state.agent_amount_l)

    def reset(self) -> None:
        """Clear stored agent while preserving tissue parameters."""

        self.agent_amount_l = 0.0
