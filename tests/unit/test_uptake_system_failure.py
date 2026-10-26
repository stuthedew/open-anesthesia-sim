"""How a failed step reports itself, and how a rejected argument does not.

This file is regression cover for the first half of PL-018. A step that broke down used to
raise a bare `ValueError` from deep inside a compartment. A caller could not tell that error
apart from a programming error, and so could not act on it.

It also covers PL-VP7N, which added the other half of the same distinction. A step larger
than `MAXIMUM_SIMULATION_STEP_S` is refused as a configuration error before the step begins.
Since PL-GS5X, that bound is the longest interval over which settings are held constant,
not a limit of numerical applicability, and the refusal it produces is unchanged. PL-YZ17
gives the step a lower bound, `MINIMUM_SIMULATION_STEP_S`, which is refused the same way
for a different reason. The lower bound is numerical: it is the finest step at which the
solution has been shown to be the shipped one.

PL-0MLQ applies the same distinction to the four controls that a user sets. A setting
outside `core/supported_ranges.py` is refused by the compartment it belongs to, which is
where every `AgentUptakeSystem` setter forwards it, and the run in progress stays
trustworthy.

PL-026 closes what PL-018 left open. The step is now transactional, so a failure leaves
every dynamic value bit-identical to its value before the step, rather than leaving the
compartments partly written. The rollback tests below deliberately assert `==` rather than
`pytest.approx`. The claim is not that values were written and then undone approximately.
The claim is that nothing from the failed step survives at all.

PL-GS5X changes how these failures are reached, not what they are. The exact step cannot
drive a compartment out of range, as `_TissueGroupThatCanRefuseAStep` explains. So a
compartment guard's failure is now injected rather than provoked. It joins the accounting
failure and the nonlocal unwind, which could never be provoked either.

PL-006 adds a case where the distinction had been drawn in the wrong place.
`set_circuit_volume` destroyed agent, and the *next* step then failed because of it. That
step reported a numerical error for what was really a defect in the setter.

PL-BNPY closes what PL-026 left open. The rollback depended on two `except` clauses, so it
could only undo what those clauses happened to catch. It is now keyed on whether the step
finished, in a `finally` block, which also covers a `BaseException` unwind.

PL-VYXP is the same kind of defect once more, in `reset()` rather than in a setter. The
accounting anchor was taken from the validator's default of zero instead of from the
compartments. So a compartment that reset to anything other than empty would leave the
residual check reporting a failure against a run that is perfectly accounted for.
"""

from math import inf, nan, nextafter

import pytest

from anesthesia_sim.core.agent_simulation_validation import (
    AgentSimulationValidationResult,
    AgentSimulationValidator,
)
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.concentration import Fraction, Percent
from anesthesia_sim.core.exceptions import (
    AgentSimulationValidationError,
    AnesthesiaSimulationError,
    SimulationConfigurationError,
    SimulationNumericalError,
)
from anesthesia_sim.core.governing_equations import (
    ALVEOLAR_FRACTION,
    FIRST_TISSUE_FRACTION,
    INSPIRED_FRACTION,
    VENOUS_FRACTION,
)
from anesthesia_sim.core.numerical_envelope import CompartmentVolume, PartitionCoefficient
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.simulation_step import (
    MAXIMUM_SIMULATION_STEP_S,
    MINIMUM_SIMULATION_STEP_S,
    SimulationStep,
)
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

# How many steps of the run come before the injected failures below.
#
# A fresh system would fail from an all-zero state. That would make a bit-identical
# comparison vacuous, because every value it had to preserve would be 0.0, and PL-026's
# regression cover exists to avoid exactly that failure mode. 60 s of run leaves all
# eight dynamic values distinct and nonzero.
STEPS_BEFORE_FAILURE = 600

# The full text of the armed fat group's refusal.
#
# The text is asserted whole, not as the bare parameter name, because of PL-SPN6. The
# alveolar compartment, the venous pool and all three tissue groups guard a
# `partial_pressure_fraction`. So an assertion on that name alone would still pass if a
# different one of the five refused first, and the runs below arm exactly one of them.
# The compartment word is what lets the message be traced back to the broken invariant,
# as these tests require. Since `PL-4R3W`, that word is part of the name the fraction is
# built under, and the refused value follows it.
FAT_REFUSAL_TEXT = "fat partial_pressure_fraction of -1.0 is outside 0 to 1"


def _sevoflurane_at_one_mac() -> AgentUptakeSystem:
    return AgentUptakeSystem.for_agent("sevoflurane")


class _TissueGroupThatCanRefuseAStep(TissueGroup):
    """A tissue group that can be armed to refuse the fraction it is given.

    **Why this failure is injected, where it used to be provoked.** Until PL-GS5X, this file
    reached the breakdown path through the model itself. It used an alveolar compartment so
    small that, in one step, the operator split's fifth sub-exchange removed more agent than
    its second sub-exchange had left in it, and the alveolar guard then refused the result.
    No parameter set can do that any more. The step is now one matrix exponential of a
    matrix in which every off-diagonal entry is a transfer rate. So the propagator is
    entrywise nonnegative, and it cannot carry a compartment below zero from a state that
    was in range. That is a property of the construction, not of any particular patient file
    or agent, which is exactly why the old route cannot be rebuilt with different numbers.
    Rounding can carry a compartment above 1 only where its fraction already stands at 1,
    which needs a 100% dial that no supported setting reaches (`core/concentration.py`).

    The guard still has to work, and this class keeps it testable. It stands in for the
    cases that the guard now protects against: a model extension whose matrix is not a pure
    transfer system, or a state that reached a compartment from outside the equations.
    `_AccountingCheckThatFailsOnce` and `_NonlocalUnwind` below inject failures that the
    model could never provoke either, and this class has joined them.

    The fat group is the one armed, because `_write_state_vector` writes it last. When the
    refusal fires, the circuit, the alveoli, the venous pool and two of the three tissue
    groups have all been written, which is the most partial state that a refused fraction
    can leave. The refusal is left to the real constructor rather than raised by hand, so
    that a caller sees the production message. Since `PL-4R3W` the refusal comes from
    `Fraction`, built here under the name that `_write_state_vector` gives the fat fraction.
    `test_a_resume_into_an_impossible_fraction_says_which_compartment_refused` checks that
    name on the production path.
    """

    refuse_next_fraction: bool = False

    def set_partial_pressure_fraction(self, partial_pressure_fraction: Fraction) -> None:
        if self.refuse_next_fraction:
            self.refuse_next_fraction = False
            partial_pressure_fraction = Fraction(
                -1.0, name=f"{self.name} partial_pressure_fraction"
            )

        super().set_partial_pressure_fraction(partial_pressure_fraction)


def _copy_fat_group_as(system: AgentUptakeSystem, group_class: type) -> TissueGroup:
    """Swap the system's fat group for a stand-in holding the same state.

    The group is copied field by field rather than rebuilt from parameters, so the run in
    progress is untouched. The stored amount is the trajectory, and rebuilding it would
    change what the failure is measured against. The group stores no blood flow, because
    the blood flow is formed from the cardiac output (`PL-HQF5`).
    """

    original = system.patient.fat
    replacement = group_class(
        name=original.name,
        volume_l=original.volume_l,
        perfusion_fraction=original.perfusion_fraction,
        blood_gas_partition_coefficient=original.blood_gas_partition_coefficient,
        tissue_gas_partition_coefficient=original.tissue_gas_partition_coefficient,
        agent_amount_l=original.agent_amount_l,
    )
    system.patient.fat = replacement

    return replacement


def _a_run_whose_next_step_a_compartment_refuses(
    steps_first: int = STEPS_BEFORE_FAILURE,
) -> AgentUptakeSystem:
    """Return a sevoflurane run whose next `advance()` is refused partway through the step."""

    system = _sevoflurane_at_one_mac()

    for _ in range(steps_first):
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    _copy_fat_group_as(system, _TissueGroupThatCanRefuseAStep).refuse_next_fraction = True

    return system


class _AccountingCheckThatFailsOnce(AgentSimulationValidator):
    """A validator whose post-step check raises whatever error it is armed with.

    The accounting check is the one failure that `_advance_step` can reach that is not a
    compartment guard. It fires last of all, after every compartment has been written.
    Reaching it with real numbers would mean breaking mass conservation. No supported input
    does that, and no test should teach the model to do it, so the failure is injected here
    instead. The tests cover the rollback wiring, not the accounting arithmetic.
    """

    pending_error: Exception | None = None

    def require_valid_agent_accounting(
        self, currently_stored_agent_l: float
    ) -> AgentSimulationValidationResult:
        if self.pending_error is not None:
            error, self.pending_error = self.pending_error, None
            raise error

        return super().require_valid_agent_accounting(currently_stored_agent_l)


def _sevoflurane_with(validator: AgentSimulationValidator) -> AgentUptakeSystem:
    """Return the reference sevoflurane system, reporting its accounting to a chosen validator."""

    built = AgentUptakeSystem.for_agent("sevoflurane")

    return AgentUptakeSystem(
        circuit=built.circuit,
        alveoli=built.alveoli,
        patient=built.patient,
        agent_simulation_validator=validator,
    )


def test_a_step_that_breaks_down_raises_a_numerical_error() -> None:
    system = _a_run_whose_next_step_a_compartment_refuses(steps_first=0)

    with pytest.raises(SimulationNumericalError) as raised:
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    # This is not a configuration error: the arguments were valid, but the numerics were
    # not. A caller bases its response on exactly this distinction.
    assert not isinstance(raised.value, SimulationConfigurationError)
    assert isinstance(raised.value, AnesthesiaSimulationError)


def test_a_failed_step_names_the_step_and_keeps_the_failing_guard() -> None:
    """The message must still let a reader trace the failure back to the invariant that broke."""

    system = _a_run_whose_next_step_a_compartment_refuses(steps_first=0)

    with pytest.raises(SimulationNumericalError) as raised:
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert f"{MAXIMUM_SIMULATION_STEP_S} s" in str(raised.value)
    assert FAT_REFUSAL_TEXT in str(raised.value)

    cause = raised.value.__cause__
    assert isinstance(cause, SimulationConfigurationError)
    assert FAT_REFUSAL_TEXT in str(cause)


def test_a_resume_into_an_impossible_fraction_says_which_compartment_refused() -> None:
    """Six places hold a fraction, and a refusal must name the one that refused.

    This is regression cover for PL-SPN6, the defect that the assertion above could not have
    caught. PL-9SH6 gave the alveolar compartment, the venous pool and the three tissue
    groups one accessor name. Each passed that name to the shared guard without qualifying
    it, so all five raised the same sentence. A refusal said only that *a* fraction had left
    [0, 1]. Since `PL-4R3W`, the refusal comes from the `Fraction` constructor, reached in
    `_write_state_vector` before any compartment's setter. So the name in the message is the
    one under which that constructor call builds each fraction, and the test checks it at
    all six positions.

    This is not a readability point. The message reaches its reader as a banner rather than
    a traceback. `app/dashboard_frame.py` shows a refused setting word for word, and
    `advance()` wraps a refused step into the notice that the run has halted. So the stack
    frame that would have told the compartments apart is not available where the message is
    read. The collision can also be reached from outside this file's injected failures.
    `require_canonical_state` does not check a fraction's range, so a `resume_at` into a
    malformed state is refused by whichever of the six it reaches first. Each position is
    driven alone, and the run is left as it was.

    The test asserts a prefix and checks that the messages are pairwise distinct, rather
    than comparing against six literal sentences. So a seventh place that holds a fraction
    cannot quietly collide with one already here.
    """

    system = _sevoflurane_at_one_mac()

    for _ in range(STEPS_BEFORE_FAILURE):
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    owners = {
        INSPIRED_FRACTION: "inspired_partial_pressure_fraction",
        ALVEOLAR_FRACTION: "alveolar",
        VENOUS_FRACTION: "venous",
        **{
            FIRST_TISSUE_FRACTION + offset: tissue.name
            for offset, tissue in enumerate(system.patient.tissues)
        },
    }

    assert len(owners) == 6, "a compartment was added or renamed without being covered here"

    before = system.state_vector()
    initial_agent_l = system.agent_simulation_validator.initial_agent_l
    messages = {}

    for position, owner in owners.items():
        malformed = list(before)
        malformed[position] = -1.0

        with pytest.raises(SimulationConfigurationError) as raised:
            system.resume_at(tuple(malformed), initial_agent_l=initial_agent_l)

        assert system.state_vector() == before
        messages[owner] = str(raised.value)

    for owner, message in messages.items():
        assert message.startswith(f"{owner} "), f"{owner} refused without naming itself: {message}"
        assert "of -1.0 is outside 0 to 1" in message, message

    assert len(set(messages.values())) == len(messages), messages


def test_every_compartment_holding_a_fraction_names_itself_refusing_a_bare_float() -> None:
    """A setter given a fraction that nobody built refuses it under the compartment's name.

    Since `PL-4R3W`, this test is the other half of PL-SPN6. A compartment's setter no longer
    checks a range, because the `Fraction` it takes was already built through that check.
    But the setter still refuses a bare `float` with a `TypeError`, because passing one is a
    programming error. The five compartments that share an accessor name must still say
    which one refused. The value is inside 0 to 1, so the type is the only thing refused.
    """

    system = _sevoflurane_at_one_mac()
    compartments = {
        "alveolar": system.alveoli,
        "venous": system.patient.venous_blood,
        **{tissue.name: tissue for tissue in system.patient.tissues},
    }

    assert len(compartments) == 5, "a compartment was added or renamed without being covered here"

    before = system.state_vector()
    messages = {}

    for owner, compartment in compartments.items():
        with pytest.raises(TypeError) as raised:
            compartment.set_partial_pressure_fraction(0.5)

        messages[owner] = str(raised.value)

    assert system.state_vector() == before

    for owner, message in messages.items():
        assert message.startswith(f"{owner} "), f"{owner} refused without naming itself: {message}"

    assert len(set(messages.values())) == len(messages), messages


def test_a_step_above_the_maximum_simulation_step_is_refused() -> None:
    """The defect PL-VP7N fixes: a 30 s step used to return a plausible number.

    The refusal is a configuration error rather than a numerical one, and the difference is
    the whole point. Nothing has been miscalculated, because the argument was refused. So a
    caller holds a run it can still trust, and it can retry with a supported step. Reporting
    the refusal as a numerical failure would tell that caller to throw away state that is
    fine.
    """

    system = _sevoflurane_at_one_mac()

    with pytest.raises(SimulationConfigurationError, match="largest supported step") as raised:
        system.advance(SimulationStep(30.0))

    assert not isinstance(raised.value, SimulationNumericalError)


def test_a_refused_maximum_simulation_step_leaves_the_run_untouched() -> None:
    """A refused step must not have moved the system part of the way."""

    system = _sevoflurane_at_one_mac()
    system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))
    before = system.total_stored_agent_l

    with pytest.raises(SimulationConfigurationError):
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S * 2.0))

    assert system.total_stored_agent_l == before
    assert system.agent_simulation_validation.passes_validation


def test_the_maximum_simulation_step_itself_is_accepted() -> None:
    """The domain is closed at its endpoint, which is the step that ships."""

    system = _sevoflurane_at_one_mac()

    result = system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert result.fresh_gas_exchange.delivered_agent_l > 0.0
    assert result.agent_accounting.passes_validation


def test_the_maximum_simulation_step_does_not_bind_a_bare_compartment() -> None:
    """The bound belongs to the coupled system, not to any one compartment.

    The bound states how long settings may be held constant, which is a property of a step
    that the whole system takes. A compartment advanced alone against a fixed input has no
    settings to hold. `tests/unit/test_circuit.py` steps a circuit on its own by 60 s and
    compares it against the analytic solution. Putting the guard on a compartment would
    break that test, and it would also misstate what the bound is about.
    """

    circuit = BreathingCircuit(
        circuit_volume_l=CompartmentVolume(6.0),
        max_delivered_concentration_percent=Percent(100.0),
        delivered_concentration_percent=Percent(100.0),
    )
    step_s = 60.0

    assert step_s > MAXIMUM_SIMULATION_STEP_S

    circuit.advance_fresh_gas(step_s)

    assert circuit.inspired_partial_pressure_fraction > 0.0


@pytest.mark.parametrize(
    "simulation_step_s", [nextafter(MINIMUM_SIMULATION_STEP_S, 0.0), 1e-6, 1e-14, 5e-324]
)
def test_a_step_below_the_minimum_simulation_step_is_refused_and_changes_nothing(
    simulation_step_s: float,
) -> None:
    """Each of these steps used to be taken, until PL-YZ17 declared a lower bound.

    At 1e-14 s, rounding made what the step changed wrong by about a third, and the result
    was returned as an ordinary step. A step of 5e-324 s, the smallest positive float, was
    taken too. The refusal is a configuration error raised before the step begins, as the
    upper bound's refusal is. So the run that the caller holds is the one it had. The
    message says which step was refused and where the lower bound is argued.
    """

    system = _sevoflurane_at_one_mac()
    system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))
    before = system.capture_state()

    with pytest.raises(SimulationConfigurationError, match="smallest supported step") as raised:
        system.advance(SimulationStep(simulation_step_s))

    assert not isinstance(raised.value, SimulationNumericalError)
    assert system.capture_state() == before
    assert f"{simulation_step_s} s" in str(raised.value)
    assert '"Supported simulation step"' in str(raised.value)


def test_the_minimum_simulation_step_itself_is_accepted() -> None:
    """The domain is closed at its lower bound, as it is at its upper bound."""

    system = _sevoflurane_at_one_mac()

    result = system.advance(SimulationStep(MINIMUM_SIMULATION_STEP_S))

    assert result.fresh_gas_exchange.delivered_agent_l > 0.0
    assert result.agent_accounting.passes_validation


@pytest.mark.parametrize("simulation_step_s", [0.0, -0.1, inf, nan])
def test_an_invalid_step_is_a_configuration_error_and_changes_nothing(
    simulation_step_s: float,
) -> None:
    """A bad argument is rejected before the step starts, so state is intact.

    This is the case that must *not* be reported as a numerical failure:
    nothing was miscalculated, so a caller has no reason to distrust the
    state it already has.
    """

    system = _sevoflurane_at_one_mac()
    before = system.total_stored_agent_l

    with pytest.raises(SimulationConfigurationError, match="simulation_step_s"):
        system.advance(SimulationStep(simulation_step_s))

    assert system.total_stored_agent_l == before


def test_a_rejected_setting_stays_a_configuration_error() -> None:
    """A refused vaporizer dial must not be reported as a broken run."""

    system = _sevoflurane_at_one_mac()
    before = system.circuit.delivered_concentration_percent

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        system.set_delivered_concentration_percent(Percent(50.0))

    assert system.circuit.delivered_concentration_percent == before


def test_the_ordinary_step_is_unaffected() -> None:
    """The wrapper must not change a step that succeeds."""

    system = _sevoflurane_at_one_mac()
    result = system.advance(SimulationStep(0.1))

    assert result.fresh_gas_exchange.delivered_agent_l > 0.0
    assert result.agent_accounting.passes_validation


@pytest.mark.parametrize(
    ("setter_name", "flow_type", "rejected_value"),
    [
        ("set_fresh_gas_flow", FreshGasFlow, 500.0),
        ("set_alveolar_ventilation", AlveolarVentilation, 200.0),
        ("set_cardiac_output", CardiacOutput, 1000.0),
    ],
)
def test_a_setting_outside_the_supported_range_is_refused_by_the_system(
    setter_name: str, flow_type: type[float], rejected_value: float
) -> None:
    """The system refuses the three values that PL-0MLQ found accepted, given as bare floats.

    Each setter of `AgentUptakeSystem` takes its flow as the type that only its guard builds
    (`PL-0YYV`). Built as that type, these values are refused by the guard before any setter
    is called, which `test_supported_ranges.py` checks. Handed in bare, as every caller
    handed them before, they reach the system and are refused at the compartment that it
    forwards them to. The error names the type to build. This test checks that no supported
    entry point into `core/` can put the model outside the domain over which it claims to
    represent a patient, unless the caller builds the type that checks the value.
    """

    system = _sevoflurane_at_one_mac()

    with pytest.raises(TypeError, match=f"not built as {flow_type.__name__}"):
        getattr(system, setter_name)(rejected_value)


@pytest.mark.parametrize(
    ("setter_name", "flow_type", "rejected_value"),
    [
        ("set_fresh_gas_flow", FreshGasFlow, 500.0),
        ("set_alveolar_ventilation", AlveolarVentilation, 200.0),
        ("set_cardiac_output", CardiacOutput, 1000.0),
    ],
)
def test_a_refused_setting_leaves_the_run_trustworthy(
    setter_name: str, flow_type: type[float], rejected_value: float
) -> None:
    """A refused setting is not a failed run, and must not look like one.

    This is the same distinction that the refused step above draws. Nothing has been
    miscalculated, so the caller keeps a run that it can go on stepping and displaying. The
    system must therefore still advance afterwards, and its agent accounting must still
    close.
    """

    system = _sevoflurane_at_one_mac()
    system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))
    before = system.total_stored_agent_l

    with pytest.raises(TypeError, match=f"not built as {flow_type.__name__}") as raised:
        getattr(system, setter_name)(rejected_value)

    assert not isinstance(raised.value, SimulationNumericalError)
    assert system.total_stored_agent_l == before

    result = system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert result.agent_accounting.passes_validation


def test_a_failed_step_leaves_every_dynamic_value_bit_identical() -> None:
    """This tests PL-026's headline claim, and the defect it fixes.

    `_advance_step` writes each compartment in turn, and the guard that fires here rejects
    the last of them after the rest have already been written. Before the rollback, the run
    was left holding those writes. The circuit gas and the alveolar gas had advanced, and
    the venous pool and two of the three tissue groups had advanced with them. That state is
    not a solution of the model at any time, but it is a plausible-looking set of numbers.

    The test uses `==` rather than `pytest.approx`. The claim is not that the values come
    back close. The claim is that they were never left changed.
    """

    system = _a_run_whose_next_step_a_compartment_refuses()
    before = system.capture_state()

    with pytest.raises(SimulationNumericalError):
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert system.capture_state() == before

    # Each value is also named individually, so that a state class that quietly stopped
    # covering a compartment cannot make the comparison above pass by comparing less.
    # These are the eight floats that a step can move.
    assert system.circuit.inspired_partial_pressure_fraction == (
        before.circuit.inspired_partial_pressure_fraction
    )
    assert system.alveoli.agent_amount_l == before.alveoli.agent_amount_l
    assert system.patient.vessel_rich.agent_amount_l == before.patient.vessel_rich.agent_amount_l
    assert system.patient.muscle.agent_amount_l == before.patient.muscle.agent_amount_l
    assert system.patient.fat.agent_amount_l == before.patient.fat.agent_amount_l
    assert system.patient.venous_blood.agent_amount_l == (
        before.patient.venous_blood.agent_amount_l
    )
    assert system.agent_simulation_validator.delivered_agent_l == (
        before.agent_simulation_validator.delivered_agent_l
    )
    assert system.agent_simulation_validator.exhausted_agent_l == (
        before.agent_simulation_validator.exhausted_agent_l
    )


def test_the_state_a_failed_step_leaves_is_the_last_completed_step() -> None:
    """The state is not merely unchanged: it is a state that the model actually produced.

    This is why rolling back settles the display question that PL-018 left open. The values
    that a halted run shows are bit-identical to those of a run that took the same steps and
    simply stopped. They are a real solution of the model, at a real simulation time, and
    not an artifact of how far the failed step got in writing the compartments.
    """

    failed = _a_run_whose_next_step_a_compartment_refuses()
    stopped = _a_run_whose_next_step_a_compartment_refuses()

    with pytest.raises(SimulationNumericalError):
        failed.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert failed.capture_state() == stopped.capture_state()
    assert failed.total_stored_agent_l == stopped.total_stored_agent_l
    assert failed.agent_simulation_validation.passes_validation


def test_a_capacity_written_under_a_held_amount_is_rolled_back_past_the_guard() -> None:
    """The rollback bypasses the capacity guard, so a refused step is undone whole.

    `PL-544D` limits the alveolar and tissue amounts to the compartment's capacity at each
    write, and a rollback is a write. Since `PL-19Y0`, only a write that bypasses the
    volume's own guard can move a capacity below an amount already held. When the rollback
    went through the capacity guard, such a capacity made `restore_state` refuse at the fat
    group. By then the circuit, the alveoli and two tissue groups had been restored. The
    venous pool, which is restored after fat, was left holding the failed step. The error
    raised was a configuration error, which had replaced the step's own error. This was
    found at review on 2026-10-12, on a run at 8% for 300 s whose fat volume was halved
    below the amount held. In that run the step itself then refuses at fat.

    The refusal here is the armed, injected refusal that the file uses throughout. Whether
    a shrunk fat volume makes the *step* refuse depends on the parameter set. At ordinary
    loads the shrunk volume gives fat a time constant shorter than the step, so the
    fraction written is back in range. The rollback's requirement does not depend on the
    parameter set. The volume and the tissue:gas coefficient are written directly,
    bypassing their own guards, because what is under test is the rollback and not how the
    capacity became too small. The state left behind is the one that the step began from.
    In it, fat is over capacity, as it already was, so that the snapshot's `Fraction`
    refuses it.
    """

    system = _a_run_whose_next_step_a_compartment_refuses()
    fat = system.patient.fat
    # Making the capacity half the amount held by changing the volume alone would need about
    # 4e-6 L, which is below the numerical envelope (`PL-QX2G`). So the volume is set to the
    # envelope's smallest value, 0.01 L, and the coefficient is set to make the capacity half
    # the amount held. The capacity, and so fat's row of the system matrix, is the same as
    # before.
    object.__setattr__(fat, "volume_l", CompartmentVolume(0.01))
    object.__setattr__(
        fat,
        "tissue_gas_partition_coefficient",
        PartitionCoefficient(fat.agent_amount_l / fat.volume_l / 2),
    )
    before = system.capture_state()

    with pytest.raises(SimulationNumericalError, match=FAT_REFUSAL_TEXT):
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert system.capture_state() == before
    assert system.patient.venous_blood.agent_amount_l == (
        before.patient.venous_blood.agent_amount_l
    )
    assert fat.partial_pressure_fraction > 1.0


def test_a_failed_step_says_it_was_rolled_back_and_names_the_invariant() -> None:
    """PL-026 moved this diagnosis out of the display and into the message.

    A reader of the halted-run banner needs both halves: which invariant the step broke, and
    that the numbers beside the banner come from the last completed step rather than the
    failed one.
    """

    system = _a_run_whose_next_step_a_compartment_refuses()

    with pytest.raises(SimulationNumericalError) as raised:
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    message = str(raised.value)

    assert "rolled back" in message
    assert "last completed step" in message
    assert f"{MAXIMUM_SIMULATION_STEP_S} s" in message
    assert FAT_REFUSAL_TEXT in message


def _with_tissue_fractions_written_past_their_guard(
    system: AgentUptakeSystem, scale: float
) -> None:
    """Scale each tissue's perfusion fraction, bypassing the tissue's own guard.

    No guarded write can now leave the tissue flows out of step with the
    cardiac output. Each flow is formed from the output (`PL-HQF5`), and a
    fraction is written once (`PL-Z0HN`). This write bypasses that guard, as
    a rollback does, so that the settings record's own refusal can still be
    reached. Scaled by 1.2 at 5.0 L/min, the flows sum to 6.0 L/min.
    """

    for tissue in system.patient.tissues:
        object.__setattr__(tissue, "perfusion_fraction", tissue.perfusion_fraction * scale)


def test_a_stale_record_met_at_step_time_is_a_failed_step_stated_in_litres_per_minute() -> None:
    """A record that the step cannot build is a failed step, in the unit the flows were set in.

    `_propagator_for` builds the settings record when a setting has moved since the last
    step. The record refuses tissue flows that no longer sum to the cardiac output. Until
    `PL-HQF5`, setting a tissue's flow directly left them that way. No guarded write can do
    that now, so this test bypasses the guard on the tissue fractions instead. Before
    `PL-KFNP`, it reached the mismatch by assigning the output to the patient directly,
    bypassing `set_cardiac_output`.

    The test checks three things. First, the refusal is restated like every other guard
    reached inside a step. A `SimulationConfigurationError` out of `advance()` would promise
    a run still worth continuing (`core/exceptions.py`), but this run is refused on every
    later step, and at Reset. Second, the step is rolled back like any other. Third, the two
    flows are named in L/min, the unit that every readout shows and that they were set in.
    The tissue flows sum to 6.0 L/min within float noise, and the message says 6.0
    (`PL-M4M0`).
    """

    system = _sevoflurane_at_one_mac()
    system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))
    before = system.capture_state()

    _with_tissue_fractions_written_past_their_guard(system, 1.2)

    assert sum(
        tissue.blood_flow_l_min_at(system.patient.cardiac_output_l_min)
        for tissue in system.patient.tissues
    ) == pytest.approx(6.0, abs=1e-12)
    assert system.patient.cardiac_output_l_min == 5.0

    with pytest.raises(SimulationNumericalError) as raised:
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    message = str(raised.value)

    assert isinstance(raised.value.__cause__, SimulationConfigurationError)
    assert "rolled back" in message
    assert "perfused at 6.0 L/min in total but cardiac output is 5.0 L/min" in message
    assert "L/s" not in message
    assert system.capture_state() == before


def test_a_failed_step_s_restated_refusal_is_pinned_whole() -> None:
    """The whole failure reason the "Simulation stopped" banner shows for a failed step.

    The test above matches phrases of the message, so it still passes when the step, the
    rollback clause or a flow is wrong (`PL-79PK`). The step is the 0.1 s that the interface
    takes. The tissue flows sum to 6.0 L/min against a cardiac output of 5.0 L/min, as
    above.
    """

    system = _sevoflurane_at_one_mac()
    system.advance(SimulationStep(0.1))
    _with_tissue_fractions_written_past_their_guard(system, 1.2)

    with pytest.raises(SimulationNumericalError) as raised:
        system.advance(SimulationStep(0.1))

    assert str(raised.value) == (
        "the simulation step of 0.1 s could not be completed and was rolled back, leaving "
        "the state the last completed step produced: the tissue groups are perfused at "
        "6.0 L/min in total but cardiac output is 5.0 L/min; the venous balance returns "
        "what the tissues receive, so the two must agree"
    )


def test_simulation_time_does_not_advance_through_a_failed_step() -> None:
    """Elapsed time is part of the same transaction, because of the order of operations.

    `SimulationState.advance()` counts the step only after the system
    returns, so a failure leaves simulated time where the last completed
    step left it. A run whose clock had moved while its compartments had
    not would report a state at a time the model never produced.
    """

    state = SimulationState(uptake_system=(_a_run_whose_next_step_a_compartment_refuses()))
    elapsed_before_s = state.elapsed_s

    with pytest.raises(SimulationNumericalError):
        state.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert state.elapsed_s == elapsed_before_s


def test_a_failed_accounting_check_is_rolled_back_too() -> None:
    """This is the one failure inside a step that is not a compartment guard.

    It fires after every compartment has been written, so it leaves the most complete
    partial step of any failure the model can reach. It reaches `advance()` as an
    `AgentSimulationValidationError` rather than as a `SimulationConfigurationError`. The
    test asserts both halves: the rollback happens, and the specific exception type survives
    it. Restating the error as a plain `SimulationNumericalError` would erase what a caller
    can tell about the failure.
    """

    validator = _AccountingCheckThatFailsOnce()
    system = _sevoflurane_with(validator)
    system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))
    before = system.capture_state()

    armed = AgentSimulationValidationError("agent accounting failed")
    validator.pending_error = armed

    with pytest.raises(AgentSimulationValidationError) as raised:
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert raised.value is armed
    assert system.capture_state() == before


def test_an_unexpected_error_inside_a_step_is_rolled_back_and_re_raised() -> None:
    """A `TypeError` from a future refactor leaves the same partial step.

    So the rollback is wider than the guard it was written for, and the re-raise is
    deliberately narrower. A programming error must still reach the caller as itself, not
    disguised as a modelling failure that the model did not have.
    """

    validator = _AccountingCheckThatFailsOnce()
    system = _sevoflurane_with(validator)
    system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))
    before = system.capture_state()

    validator.pending_error = TypeError("a refactor broke a call signature")

    with pytest.raises(TypeError) as raised:
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert not isinstance(raised.value, AnesthesiaSimulationError)
    assert system.capture_state() == before


def test_a_rolled_back_run_can_still_be_read_and_reset() -> None:
    """This checks, end to end, what the caller is left holding.

    A halted run cannot be resumed, because the model reached a state it could not step
    from, so the same step would fail again. But everything that a halted session does with
    its state has to keep working: reading a concentration for the display, checking the
    accounting for the panel beside it, and clearing the run.
    """

    system = _a_run_whose_next_step_a_compartment_refuses()

    with pytest.raises(SimulationNumericalError):
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert 0.0 < system.alveoli.partial_pressure_fraction <= 1.0
    assert 0.0 < system.circuit.inspired_partial_pressure_fraction <= 1.0
    assert system.agent_simulation_validation.passes_validation

    system.reset()

    assert system.total_stored_agent_l == 0.0


def test_changing_circuit_volume_mid_run_does_not_break_the_next_step() -> None:
    """Regression test for the defect PL-006 part 3 fixes.

    The defect was reproduced against the shipped code before the fix. A sevoflurane system
    stepped for 60 s held agent in the circuit. `set_circuit_volume(3.0)` left exactly half
    of that agent, so a setter destroyed about 24 mL of equivalent agent gas. The next
    `advance(0.1)` then raised `AgentSimulationValidationError`.

    That failure mode is the reason this test belongs with the other failure tests, and not
    only with the circuit's unit tests. The step that failed was correct. What was wrong
    happened before it, so the run was halted and the numerics were blamed for a setter's
    defect. A setter that conserves agent is what makes the two cases distinguishable again.

    `app/controller.py` compensated, so the shipped application never showed this defect.
    That is what made it worth fixing rather than leaving. The invariant was kept only for
    the one caller that knew to go the long way round.
    """

    system = _sevoflurane_at_one_mac()

    for _ in range(600):
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    circuit_agent_before_l = system.circuit.agent_amount_l
    total_agent_before_l = system.total_stored_agent_l

    # The circuit load after 60 s, re-measured under the exact step (`PL-GS5X`), was
    # 0.048305015 L, against the 0.048288200 L that the operator split produced. The two
    # are 1.7e-5 L apart, which is the split's own error at this step and not a change to
    # the model. The value is pinned rather than left implicit, because the assertions
    # below check conservation *of this amount*. A run that silently stopped reaching it
    # would make them compare a number against itself.
    #
    # It was re-measured on 2026-09-07 as 0.048301285 L (`PL-8ZJQ`), when
    # `venous_pool_volume_l` moved from 1.0 L to 1.222 L. A larger venous pool returns
    # slightly less agent to the circuit over the first 60 s. So this number is expected
    # to move with that parameter, and the 3.7e-6 L drop is in the expected direction.
    assert circuit_agent_before_l == pytest.approx(0.048301285)

    system.circuit.set_circuit_volume(CompartmentVolume(3.0))

    assert system.circuit.agent_amount_l == pytest.approx(circuit_agent_before_l)
    assert system.total_stored_agent_l == pytest.approx(total_agent_before_l)

    result = system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert result.agent_accounting.passes_validation


class _AlveolarCompartmentThatKeepsItsAgent(AlveolarCompartment):
    """An alveolar compartment whose `reset()` leaves its store in place.

    It stands in for a compartment that resets to something other than empty.
    `AgentUptakeSystem.reset()` has to anchor that case correctly, and could not before
    PL-VYXP. No shipped compartment behaves this way today. That is the point: the defect
    can be reached only through a compartment that does. A bellows model, or a patient file
    that carries a residual, is the kind of change that would introduce one.
    """

    def reset(self) -> None:
        return


def test_reset_anchors_accounting_to_what_the_compartments_actually_hold() -> None:
    """Regression test for PL-VYXP.

    The defect was measured against the shipped code before the fix, with the alveolus below
    holding 0.05 L. `reset()` anchored `initial_agent_l` at 0.0 against 0.05 L actually
    stored. So the very next accounting check reported `unaccounted = -0.05 L` and
    `passes_validation` False, on a system that had neither created nor lost any agent.

    The direction of the failure is worth recording, because it is the safe direction. An
    anchor that is too low makes the identity come up short, so the check fires rather than
    staying quiet, and a run halts that should not have. Such an anchor cannot hide a real
    drift, except within the accounting tolerance itself. That is what makes this a defect in
    the check rather than a hole in it. It was still worth closing, because a safety net that
    halts a healthy run and blames the numerics teaches a reader to distrust it.
    """

    system = _sevoflurane_at_one_mac()

    retained = _AlveolarCompartmentThatKeepsItsAgent(
        gas_volume_l=system.alveoli.gas_volume_l,
        alveolar_ventilation_l_min=system.alveoli.alveolar_ventilation_l_min,
    )
    retained.set_partial_pressure_fraction(Fraction(0.02))
    # A built system refuses a new part (`PL-N7MM`), so the stand-in goes into a new
    # system. The new system's constructor already anchors the accounting at 0.05 L.
    # The test checks what `reset()` anchors it at afterwards. Before PL-VYXP,
    # `reset()` anchored it at 0.0.
    system = AgentUptakeSystem(circuit=system.circuit, alveoli=retained, patient=system.patient)

    system.reset()

    # Every other compartment cleared, so what the system holds is exactly what the
    # stand-in kept. That is a non-zero baseline, which the anchor has to match.
    assert retained.agent_amount_l == pytest.approx(0.05)
    assert system.total_stored_agent_l == pytest.approx(retained.agent_amount_l)

    assert system.agent_simulation_validator.initial_agent_l == pytest.approx(
        system.total_stored_agent_l
    )

    check = system.agent_simulation_validation

    assert check.unaccounted_agent_l == pytest.approx(0.0)
    assert check.passes_validation


def test_reset_still_anchors_at_zero_when_every_compartment_clears() -> None:
    """The ordinary path is unchanged, which is why the fix is safe to take.

    Every shipped compartment clears itself, so reading the anchor back out of the
    compartments gives exactly the `0.0` that the default supplied. This test asserts that
    equivalence rather than assuming it. So a compartment whose `reset()` later stops
    clearing is caught as a change in what an accounting period starts from, rather than
    silently changing that starting point.
    """

    system = _sevoflurane_at_one_mac()

    for _ in range(100):
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert system.total_stored_agent_l > 0.0

    system.reset()

    assert system.agent_simulation_validator.initial_agent_l == 0.0
    assert system.agent_simulation_validator.delivered_agent_l == 0.0
    assert system.agent_simulation_validator.exhausted_agent_l == 0.0
    assert system.total_stored_agent_l == 0.0
    assert system.agent_simulation_validation.passes_validation


class _NonlocalUnwind(BaseException):
    """A stand-in for `KeyboardInterrupt`, which unwinds without being an `Exception`.

    A real interrupt cannot be delivered at a chosen bytecode. `asyncio.CancelledError` is
    the other `BaseException` that a reader might expect here, but it cannot be reached,
    because `_advance_step()` contains no `await` for a cancellation to arrive at. So this
    class of failure is injected rather than provoked, exactly as
    `_AccountingCheckThatFailsOnce` injects the accounting failure above.
    """


class _TissueGroupThatCanUnwindNonlocally(TissueGroup):
    """A tissue group that can be armed to unwind without an `Exception`.

    It is armed on the fat group for the same reason that `_TissueGroupThatCanRefuseAStep`
    is. `_write_state_vector` writes the fat group last, so the unwind lands after the
    circuit, the alveoli, the venous pool and two tissue groups have been written. That is
    the partial state that the rollback exists to undo.
    """

    unwind_on_next_write: bool = False

    def set_partial_pressure_fraction(self, partial_pressure_fraction: Fraction) -> None:
        if self.unwind_on_next_write:
            self.unwind_on_next_write = False

            raise _NonlocalUnwind("a nonlocal unwind partway through the step")

        super().set_partial_pressure_fraction(partial_pressure_fraction)


def _a_run_that_can_unwind_nonlocally(steps_first: int = 100) -> AgentUptakeSystem:
    """Return a sevoflurane run whose fat group can be armed to unwind."""

    system = _sevoflurane_at_one_mac()

    for _ in range(steps_first):
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    _copy_fat_group_as(system, _TissueGroupThatCanUnwindNonlocally)

    return system


def test_a_nonlocal_unwind_mid_step_is_rolled_back_too() -> None:
    """Regression test for PL-BNPY.

    The defect was measured against the shipped code before the fix. With the unwind armed
    after the circuit had been written, `inspired_partial_pressure_fraction` was left at
    0.0020183972008138854, against 0.0020003856996684967 before the step. A partly applied
    step survived in the live system, which `advance()`'s docstring says cannot happen.

    The two `except` clauses that the rollback had could only undo what they happened to
    catch, and `BaseException` is the one that nobody lists. Keyed instead on whether the
    step finished, the rollback is correct for every way out of the block.
    """

    system = _a_run_that_can_unwind_nonlocally()
    state_before_step = system.capture_state()

    # This is not a vacuous comparison: 10 s of run leaves every dynamic value distinct and
    # nonzero, so a partial write shows up as a difference.
    assert state_before_step.circuit.inspired_partial_pressure_fraction > 0.0
    assert state_before_step.alveoli.agent_amount_l > 0.0

    system.patient.fat.unwind_on_next_write = True

    with pytest.raises(_NonlocalUnwind):
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert system.capture_state() == state_before_step


def test_a_nonlocal_unwind_leaves_the_run_readable_and_steppable() -> None:
    """The state that a nonlocal unwind leaves is a real solution, not a fragment.

    Unlike a step that the model could not complete, nothing here says that the model
    reached a state it cannot step from, because the unwind came from outside the model. So
    the check that tells the two cases apart is that the very next step succeeds from the
    rolled-back state, and that the accounting still closes.
    """

    system = _a_run_that_can_unwind_nonlocally()

    system.patient.fat.unwind_on_next_write = True

    with pytest.raises(_NonlocalUnwind):
        system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    result = system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))

    assert result.agent_accounting.passes_validation
