"""How a failed step reports itself, and how a rejected argument does not.

Regression cover for the first half of PL-018: a step that breaks down
used to raise a bare `ValueError` from deep inside a compartment, which a
caller could not tell apart from a programming error and so could not act
on.

Also cover for PL-VP7N, which added the other half of the same distinction:
a step larger than `MAXIMUM_SIMULATION_STEP_S` is refused as a
configuration error before the step begins, because the operator split has
no measured error bound there and the number it would return would be wrong
in the first digit the interface displays.

PL-0MLQ applies the same distinction to the four controls a user sets. A
setting outside `core/supported_ranges.py` is refused by the compartment it
belongs to, which is what every `AgentUptakeSystem` setter forwards to, and
the run in progress stays trustworthy.

PL-026 closes what PL-018 left: the step is now transactional, so a failure
leaves every dynamic value bit-identical to its pre-step value rather than
partway through the five sub-exchanges. The rollback tests below assert
`==` rather than `pytest.approx` deliberately — the claim is that nothing
was written and then undone approximately, but that nothing survives the
failed step at all.

PL-006 adds the case where the distinction had been drawn in the wrong
place: `set_circuit_volume` destroyed agent and the *next* step failed for
it, reporting a numerical error for what was a setter's defect.

PL-BNPY closes what PL-026 left: the rollback hung off two `except`
clauses, so it could only undo what those clauses thought to catch. It is now
keyed on whether the step finished, in a `finally`, which covers a
`BaseException` unwind too.

PL-VYXP is the same shape once more, in `reset()` rather than in a setter:
the accounting anchor was taken from the validator's zero default instead of
from the compartments, so a compartment that reset to anything other than
empty would leave the residual check reporting a failure against a run that
is perfectly accounted for.
"""

from math import inf, nan

import pytest

from anesthesia_sim.core.agent_simulation_validation import (
    AgentSimulationValidationResult,
    AgentSimulationValidator,
)
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.exceptions import (
    AgentSimulationValidationError,
    AnesthesiaSimulationError,
    SimulationConfigurationError,
    SimulationNumericalError,
)
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.patient import PatientCompartments
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.supported_ranges import MAXIMUM_CARDIAC_OUTPUT_L_MIN
from anesthesia_sim.core.uptake_system import MAXIMUM_SIMULATION_STEP_S, AgentUptakeSystem

# An alveolar gas volume no patient has, and that is the point: after PL-VP7N
# no supported step can break the split on the reference adult, so the only
# way to reach the breakdown path through the public interface is a system
# whose capacity is smaller than one supported step's transfer. That is not a
# hypothetical shape - it is what a future parameter set (a paediatric patient
# file, a far more soluble agent) could produce at a step this module still
# accepts, which is why the guard has to stay and has to be covered.
#
# The arithmetic: one step of blood uptake removes about
# Q * lambda_b/g * dt = (10/60) * 1.3 * 0.1 = 0.022 L of isoflurane per unit
# alveolar fraction, at the model's maximum supported cardiac output. A lung holding
# less than that at a fraction of 1 cannot supply it, so the alveolar guard
# rejects the negative amount the split asks it to hold.
BREAKDOWN_ALVEOLAR_GAS_VOLUME_L = 0.005


def _sevoflurane_at_one_mac() -> AgentUptakeSystem:
    return AgentUptakeSystem.for_agent("sevoflurane")


def _lungs_too_small_for_one_supported_step() -> AgentUptakeSystem:
    """A system whose alveolar store one supported step would overdraw."""

    agent = load_agent_parameters("isoflurane")
    patient_parameters = load_reference_adult_parameters()
    system = AgentUptakeSystem(
        circuit=BreathingCircuit(
            delivered_concentration_fraction=(agent.mac_percent / 100.0),
            max_delivered_concentration_fraction=(
                agent.max_delivered_concentration_percent / 100.0
            ),
        ),
        alveoli=AlveolarCompartment(
            gas_volume_l=BREAKDOWN_ALVEOLAR_GAS_VOLUME_L,
            alveolar_ventilation_l_min=(patient_parameters.default_alveolar_ventilation_l_min),
        ),
        patient=PatientCompartments.from_parameters(agent=agent, patient=patient_parameters),
    )
    system.set_cardiac_output(MAXIMUM_CARDIAC_OUTPUT_L_MIN)

    return system


# A lung small enough that the guard fires at the model's maximum cardiac
# output but not at the reference adult's, so a run can reach a real
# trajectory and only then break down. The all-zero state a fresh system
# fails from would make a bit-identical comparison vacuous - every value it
# had to preserve would be 0.0 - which is the failure mode PL-026's
# regression cover has to avoid. 60 s of run leaves all eight dynamic values
# distinct and nonzero, and is well inside the window: the guard still fires
# at 0.1 s of run and stops firing only after about 600 s, as the alveolar
# store catches up with what one step of uptake asks of it.
ROLLBACK_ALVEOLAR_GAS_VOLUME_L = 0.015
ROLLBACK_STEPS_BEFORE_FAILURE = 600


def _a_run_that_breaks_down_when_cardiac_output_is_raised() -> AgentUptakeSystem:
    """A system 60 s into a valid run, one raised setting from breaking down."""

    agent = load_agent_parameters("isoflurane")
    patient_parameters = load_reference_adult_parameters()
    system = AgentUptakeSystem(
        circuit=BreathingCircuit(
            delivered_concentration_fraction=(agent.mac_percent / 100.0),
            max_delivered_concentration_fraction=(
                agent.max_delivered_concentration_percent / 100.0
            ),
        ),
        alveoli=AlveolarCompartment(
            gas_volume_l=ROLLBACK_ALVEOLAR_GAS_VOLUME_L,
            alveolar_ventilation_l_min=(patient_parameters.default_alveolar_ventilation_l_min),
        ),
        patient=PatientCompartments.from_parameters(agent=agent, patient=patient_parameters),
    )

    for _ in range(ROLLBACK_STEPS_BEFORE_FAILURE):
        system.advance(MAXIMUM_SIMULATION_STEP_S)

    system.set_cardiac_output(MAXIMUM_CARDIAC_OUTPUT_L_MIN)

    return system


class _AccountingCheckThatFailsOnce(AgentSimulationValidator):
    """A validator whose post-step check raises whatever it is armed with.

    The accounting check is the one failure `_advance_step` can reach that
    is not a compartment guard, and it fires last of all - after every
    compartment has been written. Reaching it with real numbers would mean
    breaking mass conservation, which no supported input does and which no
    test should teach the model to do, so it is injected here instead. What
    is under test is the rollback wiring, not the accounting arithmetic.
    """

    pending_error: Exception | None = None

    def require_valid_agent_accounting(self, check: AgentSimulationValidationResult) -> None:
        if self.pending_error is not None:
            error, self.pending_error = self.pending_error, None
            raise error

        super().require_valid_agent_accounting(check)


def _sevoflurane_with(validator: AgentSimulationValidator) -> AgentUptakeSystem:
    """The reference sevoflurane system, accounting to a chosen validator."""

    built = AgentUptakeSystem.for_agent("sevoflurane")

    return AgentUptakeSystem(
        circuit=built.circuit,
        alveoli=built.alveoli,
        patient=built.patient,
        agent_simulation_validator=validator,
    )


def test_a_step_that_breaks_down_raises_a_numerical_error() -> None:
    system = _lungs_too_small_for_one_supported_step()

    with pytest.raises(SimulationNumericalError) as raised:
        system.advance(MAXIMUM_SIMULATION_STEP_S)

    # Not a configuration error: the arguments were valid, the numerics
    # were not. A caller keys its response off exactly this distinction.
    assert not isinstance(raised.value, SimulationConfigurationError)
    assert isinstance(raised.value, AnesthesiaSimulationError)


def test_a_failed_step_names_the_step_and_keeps_the_failing_guard() -> None:
    """The message must stay diagnosable back to the invariant that broke."""

    system = _lungs_too_small_for_one_supported_step()

    with pytest.raises(SimulationNumericalError) as raised:
        system.advance(MAXIMUM_SIMULATION_STEP_S)

    assert f"{MAXIMUM_SIMULATION_STEP_S} s" in str(raised.value)
    assert "resulting_agent_amount_l" in str(raised.value)

    cause = raised.value.__cause__
    assert isinstance(cause, SimulationConfigurationError)
    assert "resulting_agent_amount_l" in str(cause)


def test_a_step_above_the_maximum_simulation_step_is_refused() -> None:
    """The defect PL-VP7N fixes: 30 s used to return a plausible number.

    It is a configuration error rather than a numerical one, and the
    difference is the whole point. Nothing has been miscalculated - the
    argument was refused - so a caller holds a run it can still trust and
    can retry with a supported step. Reporting it as a numerical failure
    would tell that caller to throw away state that is fine.
    """

    system = _sevoflurane_at_one_mac()

    with pytest.raises(SimulationConfigurationError, match="applicability domain") as raised:
        system.advance(30.0)

    assert not isinstance(raised.value, SimulationNumericalError)


def test_a_refused_maximum_simulation_step_leaves_the_run_untouched() -> None:
    """A refused step must not have moved the system part of the way."""

    system = _sevoflurane_at_one_mac()
    system.advance(MAXIMUM_SIMULATION_STEP_S)
    before = system.total_stored_agent_l

    with pytest.raises(SimulationConfigurationError):
        system.advance(MAXIMUM_SIMULATION_STEP_S * 2.0)

    assert system.total_stored_agent_l == before
    assert system.agent_simulation_validation.passes_validation


def test_the_maximum_simulation_step_itself_is_accepted() -> None:
    """The domain is closed at its endpoint, which is the step that ships."""

    system = _sevoflurane_at_one_mac()

    result = system.advance(MAXIMUM_SIMULATION_STEP_S)

    assert result.fresh_gas_exchange.delivered_agent_l > 0.0
    assert result.agent_accounting.passes_validation


def test_the_maximum_simulation_step_does_not_bind_a_bare_compartment() -> None:
    """The bound is the coupled split's, not any one compartment's.

    A compartment advanced alone is solved exactly at any step, so there is
    no splitting error to bound and nothing to refuse; `tests/unit/
    test_circuit.py` steps a circuit on its own 60 s and compares it against
    the analytic solution. Putting the guard on a compartment would break
    that test and would also misstate where the error comes from.
    """

    circuit = BreathingCircuit(delivered_concentration_fraction=1.0)
    step_s = 60.0

    assert step_s > MAXIMUM_SIMULATION_STEP_S

    circuit.advance_fresh_gas(step_s)

    assert circuit.circuit_concentration_fraction > 0.0


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
        system.advance(simulation_step_s)

    assert system.total_stored_agent_l == before


def test_a_rejected_setting_stays_a_configuration_error() -> None:
    """A refused vaporizer dial must not be reported as a broken run."""

    system = _sevoflurane_at_one_mac()
    before = system.circuit.delivered_concentration_fraction

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        system.set_delivered_concentration(0.5)

    assert system.circuit.delivered_concentration_fraction == before


def test_the_ordinary_step_is_unaffected() -> None:
    """The wrapper must not change a step that succeeds."""

    system = _sevoflurane_at_one_mac()
    result = system.advance(0.1)

    assert result.fresh_gas_exchange.delivered_agent_l > 0.0
    assert result.agent_accounting.passes_validation


@pytest.mark.parametrize(
    ("setter_name", "rejected_value"),
    [
        ("set_fresh_gas_flow", 500.0),
        ("set_alveolar_ventilation", 200.0),
        ("set_cardiac_output", 1000.0),
    ],
)
def test_a_setting_outside_the_supported_range_is_refused_by_the_system(
    setter_name: str, rejected_value: float
) -> None:
    """The three values PL-0MLQ found accepted, refused at the coupled system.

    `AgentUptakeSystem` forwards each of these to the compartment that owns
    the setting, so this is cover for the forwarding rather than a second
    guard: what it holds is that no supported entry point into `core/` can
    put the model outside the domain its error bound is measured over.
    """

    system = _sevoflurane_at_one_mac()

    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        getattr(system, setter_name)(rejected_value)


@pytest.mark.parametrize(
    ("setter_name", "rejected_value"),
    [
        ("set_fresh_gas_flow", 500.0),
        ("set_alveolar_ventilation", 200.0),
        ("set_cardiac_output", 1000.0),
    ],
)
def test_a_refused_setting_leaves_the_run_trustworthy(
    setter_name: str, rejected_value: float
) -> None:
    """A refused setting is not a failed run, and must not read like one.

    This is the same distinction the refused step above draws: nothing has
    been miscalculated, so the caller keeps a run it can go on stepping and
    displaying. The system must therefore be advanceable afterwards, and its
    agent accounting must still close.
    """

    system = _sevoflurane_at_one_mac()
    system.advance(MAXIMUM_SIMULATION_STEP_S)
    before = system.total_stored_agent_l

    with pytest.raises(SimulationConfigurationError) as raised:
        getattr(system, setter_name)(rejected_value)

    assert not isinstance(raised.value, SimulationNumericalError)
    assert system.total_stored_agent_l == before

    result = system.advance(MAXIMUM_SIMULATION_STEP_S)

    assert result.agent_accounting.passes_validation


def test_a_failed_step_leaves_every_dynamic_value_bit_identical() -> None:
    """PL-026's headline claim, and the defect it fixes.

    `_advance_step` applies five sub-exchanges in sequence, and the guard
    that fires here rejects the fifth after the first four have already
    written their compartments. Before the rollback the run was left
    holding those four writes: circuit and alveolar gas advanced, tissues
    and venous blood advanced against the alveolar fraction, and the
    delivery totals recorded - a state that is not a solution of the model
    at any time, but is a plausible-looking set of numbers.

    `==` rather than `pytest.approx`: the claim is not that the values come
    back close, it is that they were never left changed.
    """

    system = _a_run_that_breaks_down_when_cardiac_output_is_raised()
    before = system.capture_state()

    with pytest.raises(SimulationNumericalError):
        system.advance(MAXIMUM_SIMULATION_STEP_S)

    assert system.capture_state() == before

    # Named individually as well, so that a state class that quietly stopped
    # covering a compartment cannot make the comparison above pass by
    # comparing less. These are the eight floats a step can move.
    assert system.circuit.circuit_concentration_fraction == (
        before.circuit.circuit_concentration_fraction
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
    """Not merely unchanged, but a state the model actually produced.

    This is why rolling back settles the display question PL-018 left open.
    The values a halted run shows are bit-identical to those of a run that
    took the same steps and simply stopped - a real solution of the model,
    at a real simulation time - rather than an artifact of how far into the
    failed step the operators got.
    """

    failed = _a_run_that_breaks_down_when_cardiac_output_is_raised()
    stopped = _a_run_that_breaks_down_when_cardiac_output_is_raised()

    with pytest.raises(SimulationNumericalError):
        failed.advance(MAXIMUM_SIMULATION_STEP_S)

    assert failed.capture_state() == stopped.capture_state()
    assert failed.total_stored_agent_l == stopped.total_stored_agent_l
    assert failed.agent_simulation_validation.passes_validation


def test_a_failed_step_says_it_was_rolled_back_and_names_the_invariant() -> None:
    """The diagnosis PL-026 moved out of the display and into the message.

    A reader of the halted-run banner needs both halves: which invariant
    the step broke, and that the numbers beside the banner are the last
    completed step rather than the failed one.
    """

    system = _a_run_that_breaks_down_when_cardiac_output_is_raised()

    with pytest.raises(SimulationNumericalError) as raised:
        system.advance(MAXIMUM_SIMULATION_STEP_S)

    message = str(raised.value)

    assert "rolled back" in message
    assert "last completed step" in message
    assert f"{MAXIMUM_SIMULATION_STEP_S} s" in message
    assert "resulting_agent_amount_l" in message


def test_simulation_time_does_not_advance_through_a_failed_step() -> None:
    """Elapsed time is part of the same transaction, by ordering.

    `SimulationState.advance()` adds the step only after the system
    returns, so a failure leaves simulated time where the last completed
    step left it. A run whose clock had moved while its compartments had
    not would report a state at a time the model never produced.
    """

    state = SimulationState(uptake_system=(_a_run_that_breaks_down_when_cardiac_output_is_raised()))
    elapsed_before_s = state.elapsed_s

    with pytest.raises(SimulationNumericalError):
        state.advance(MAXIMUM_SIMULATION_STEP_S)

    assert state.elapsed_s == elapsed_before_s


def test_a_failed_accounting_check_is_rolled_back_too() -> None:
    """The one in-step failure that is not a compartment guard.

    It fires after every compartment has been written, so it leaves the
    most complete partial step of any failure the model can reach, and it
    reaches `advance()` as an `AgentSimulationValidationError` rather than
    as a `SimulationConfigurationError`. Both halves are asserted: the
    rollback happens, and the specific exception type survives it, because
    restating it as a plain `SimulationNumericalError` would erase what a
    caller can tell about the failure.
    """

    validator = _AccountingCheckThatFailsOnce()
    system = _sevoflurane_with(validator)
    system.advance(MAXIMUM_SIMULATION_STEP_S)
    before = system.capture_state()

    armed = AgentSimulationValidationError("agent accounting failed")
    validator.pending_error = armed

    with pytest.raises(AgentSimulationValidationError) as raised:
        system.advance(MAXIMUM_SIMULATION_STEP_S)

    assert raised.value is armed
    assert system.capture_state() == before


def test_an_unexpected_error_inside_a_step_is_rolled_back_and_re_raised() -> None:
    """A `TypeError` from a future refactor leaves the same partial step.

    The rollback is therefore wider than the guard it was written for, and
    the re-raise is deliberately narrower: a programming error must still
    arrive at the caller as itself, not dressed up as a modelling failure
    the model did not have.
    """

    validator = _AccountingCheckThatFailsOnce()
    system = _sevoflurane_with(validator)
    system.advance(MAXIMUM_SIMULATION_STEP_S)
    before = system.capture_state()

    validator.pending_error = TypeError("a refactor broke a call signature")

    with pytest.raises(TypeError) as raised:
        system.advance(MAXIMUM_SIMULATION_STEP_S)

    assert not isinstance(raised.value, AnesthesiaSimulationError)
    assert system.capture_state() == before


def test_a_rolled_back_run_can_still_be_read_and_reset() -> None:
    """What the caller is left holding, end to end.

    A halted run is not resumable - the model reached a state it could not
    step from, so the same step would fail again - but everything a halted
    session does with its state has to keep working: reading a
    concentration for the display, checking the accounting for the panel
    beside it, and clearing the run.
    """

    system = _a_run_that_breaks_down_when_cardiac_output_is_raised()

    with pytest.raises(SimulationNumericalError):
        system.advance(MAXIMUM_SIMULATION_STEP_S)

    assert 0.0 < system.alveoli.concentration_fraction <= 1.0
    assert 0.0 < system.circuit.circuit_concentration_fraction <= 1.0
    assert system.agent_simulation_validation.passes_validation

    system.reset()

    assert system.total_stored_agent_l == 0.0


def test_changing_circuit_volume_mid_run_does_not_break_the_next_step() -> None:
    """Regression test for the defect PL-006 part 3 fixes.

    Reproduced against the shipped code before the fix, and the numbers here
    are that measurement rather than values read off the corrected run: a
    sevoflurane system stepped 60 s held 0.048288200 L of agent in the
    circuit, `set_circuit_volume(3.0)` left 0.024144100 L of it - 24.1 mL of
    equivalent agent gas destroyed by a setter - and the next `advance(0.1)`
    raised `AgentSimulationValidationError`.

    That failure mode is the reason this belongs with the other failure
    tests rather than only with the circuit's unit tests. The step that
    failed was correct; what was wrong happened before it, so the run was
    halted and the numerics blamed for a setter's defect. A conserving setter
    is what makes the two distinguishable again.

    `app/controller.py` compensated, so the shipped application never showed
    this. That is what made it worth fixing rather than leaving: the
    invariant held only for the one caller who knew to go the long way round.
    """

    system = _sevoflurane_at_one_mac()

    for _ in range(600):
        system.advance(MAXIMUM_SIMULATION_STEP_S)

    circuit_agent_before_l = system.circuit.agent_amount_l
    total_agent_before_l = system.total_stored_agent_l

    assert circuit_agent_before_l == pytest.approx(0.048288200)

    system.circuit.set_circuit_volume(3.0)

    assert system.circuit.agent_amount_l == pytest.approx(circuit_agent_before_l)
    assert system.total_stored_agent_l == pytest.approx(total_agent_before_l)

    result = system.advance(MAXIMUM_SIMULATION_STEP_S)

    assert result.agent_accounting.passes_validation


class _AlveolarCompartmentThatKeepsItsAgent(AlveolarCompartment):
    """An alveolar compartment whose `reset()` leaves its store in place.

    Stands in for a compartment that resets to something other than empty,
    which is the case `AgentUptakeSystem.reset()` has to anchor correctly and
    could not before PL-VYXP. No shipped compartment behaves this way today -
    that is the point, since the defect is reachable only through one that
    does, and a bellows model or a patient file carrying a residual is the
    shape that would introduce it.
    """

    def reset(self) -> None:
        return


def test_reset_anchors_accounting_to_what_the_compartments_actually_hold() -> None:
    """Regression test for PL-VYXP.

    Measured against the shipped code before the fix, with the alveolus below
    holding 0.05 L: `reset()` anchored `initial_agent_l` at 0.0 against
    0.05 L actually stored, so the very next accounting check reported
    `unaccounted = -0.05 L` and `passes_validation` False, on a system that
    had neither created nor lost any agent at all.

    The failure direction is worth recording because it is the safe one. An
    anchor that is too low makes the identity short, so the check fires
    rather than staying quiet, and a run halts that should not have; it
    cannot mask a real drift except within the accounting tolerance itself.
    That is what makes this a defect in the check rather than a hole in it -
    and still worth closing, because a safety net that halts a healthy run
    and blames the numerics teaches a reader to distrust it.
    """

    system = _sevoflurane_at_one_mac()

    retained = _AlveolarCompartmentThatKeepsItsAgent(
        gas_volume_l=system.alveoli.gas_volume_l,
        alveolar_ventilation_l_min=system.alveoli.alveolar_ventilation_l_min,
    )
    retained.set_concentration_fraction(0.02)
    system.alveoli = retained

    system.reset()

    # Every other compartment cleared, so what the system holds is exactly
    # what the stand-in kept - a non-zero baseline the anchor has to match.
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

    Every shipped compartment clears itself, so reading the anchor back out
    of them is exactly the `0.0` the default supplied. This asserts that
    equivalence rather than assuming it, so a compartment whose `reset()`
    later stops clearing is caught as a change in what an accounting period
    starts from rather than silently rewriting it.
    """

    system = _sevoflurane_at_one_mac()

    for _ in range(100):
        system.advance(MAXIMUM_SIMULATION_STEP_S)

    assert system.total_stored_agent_l > 0.0

    system.reset()

    assert system.agent_simulation_validator.initial_agent_l == 0.0
    assert system.agent_simulation_validator.delivered_agent_l == 0.0
    assert system.agent_simulation_validator.exhausted_agent_l == 0.0
    assert system.total_stored_agent_l == 0.0
    assert system.agent_simulation_validation.passes_validation


class _NonlocalUnwind(BaseException):
    """Stands in for `KeyboardInterrupt`: unwinds without being an `Exception`.

    A real one cannot be delivered at a chosen bytecode, and
    `asyncio.CancelledError` - the other `BaseException` a reader might
    expect here - is unreachable, because `_advance_step()` contains no
    `await` for a cancellation to arrive at. So the class of failure is
    injected rather than provoked, exactly as `_AccountingCheckThatFailsOnce`
    injects the accounting failure above.
    """


class _PatientCompartmentsThatCanUnwindNonlocally(PatientCompartments):
    """Patient compartments that can be armed to unwind without an `Exception`.

    `PatientCompartments.advance()` is the third of `_advance_step()`'s five
    sub-exchanges, so arming it puts the unwind after the circuit and the
    circuit-alveolar exchange have already written and before the rest has -
    the partial state the rollback exists to undo.
    """

    unwind_on_next_advance: bool = False

    def advance(self, arterial_fraction: float, simulation_step_s: float) -> float:
        if self.unwind_on_next_advance:
            self.unwind_on_next_advance = False

            raise _NonlocalUnwind("a nonlocal unwind partway through the step")

        return super().advance(
            arterial_fraction=arterial_fraction, simulation_step_s=simulation_step_s
        )


def _a_run_that_can_unwind_nonlocally() -> _PatientCompartmentsThatCanUnwindNonlocally:
    """A sevoflurane system 10 s in, whose patient side can be armed to unwind."""

    agent = load_agent_parameters("sevoflurane")
    patient_parameters = load_reference_adult_parameters()
    patient = _PatientCompartmentsThatCanUnwindNonlocally.from_parameters(
        agent=agent, patient=patient_parameters
    )

    return patient


def test_a_nonlocal_unwind_mid_step_is_rolled_back_too() -> None:
    """Regression test for PL-BNPY.

    Measured against the shipped code before the fix: with the unwind armed
    after the circuit had been written, `circuit_concentration_fraction` was
    left at 0.0020183972008138854 against 0.0020003856996684967 before the
    step - a partly applied step surviving in the live system, which
    `advance()`'s docstring says cannot happen.

    The two `except` clauses it had could only undo what they thought to
    catch, and `BaseException` is the one nobody enumerates. Keyed on whether
    the step finished instead, the rollback is right for every way out of the
    block.
    """

    system = _sevoflurane_at_one_mac()
    system.patient = _a_run_that_can_unwind_nonlocally()

    for _ in range(100):
        system.advance(MAXIMUM_SIMULATION_STEP_S)

    state_before_step = system.capture_state()

    # Not a vacuous comparison: 10 s of run leaves every dynamic value
    # distinct and nonzero, so a partial write shows up as a difference.
    assert state_before_step.circuit.circuit_concentration_fraction > 0.0
    assert state_before_step.alveoli.agent_amount_l > 0.0

    system.patient.unwind_on_next_advance = True

    with pytest.raises(_NonlocalUnwind):
        system.advance(MAXIMUM_SIMULATION_STEP_S)

    assert system.capture_state() == state_before_step


def test_a_nonlocal_unwind_leaves_the_run_readable_and_steppable() -> None:
    """The state a nonlocal unwind leaves is a real solution, not a fragment.

    Unlike a step the model could not complete, nothing here says the model
    reached a state it cannot step from - the unwind came from outside it -
    so the distinguishing check is that the very next step succeeds against
    the rolled-back state and the accounting still closes.
    """

    system = _sevoflurane_at_one_mac()
    system.patient = _a_run_that_can_unwind_nonlocally()

    for _ in range(100):
        system.advance(MAXIMUM_SIMULATION_STEP_S)

    system.patient.unwind_on_next_advance = True

    with pytest.raises(_NonlocalUnwind):
        system.advance(MAXIMUM_SIMULATION_STEP_S)

    result = system.advance(MAXIMUM_SIMULATION_STEP_S)

    assert result.agent_accounting.passes_validation
