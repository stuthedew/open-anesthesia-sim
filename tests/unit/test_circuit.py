import copy
import json
import pickle
import re
from dataclasses import astuple, replace
from importlib.resources import files
from math import exp, inf, nan, nextafter

import pytest

from anesthesia_sim.core import uptake_system
from anesthesia_sim.core.circuit import (
    TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN,
    BreathingCircuit,
    DeliverableFreshGasFlowRange,
)
from anesthesia_sim.core.concentration import Fraction, Percent
from anesthesia_sim.core.exceptions import (
    AgentSimulationValidationError,
    SimulationConfigurationError,
)
from anesthesia_sim.core.numerical_envelope import CompartmentVolume
from anesthesia_sim.core.parameters import (
    load_reference_circle_system_parameters,
    parse_breathing_circuit_parameters,
)
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MINIMUM_FRESH_GAS_FLOW_L_MIN,
    FreshGasFlow,
)
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

# This pattern matches the end of a shared guard's error message. The message
# names the refused value and the reason it was refused (`PL-T137`). The
# guard's own tests pin each reason. The tests here pin the field's name.
REFUSAL_REASON = r", and [^ ]+ is (?:not finite|not greater than zero|negative)$"


def test_rejects_agent_amount_above_circuit_capacity() -> None:
    circuit = BreathingCircuit(
        circuit_volume_l=CompartmentVolume(6.0), max_delivered_concentration_percent=Percent(100.0)
    )

    with pytest.raises(
        SimulationConfigurationError,
        match=(
            r"^circuit agent_amount_l of 6.1 L is more than the 6.0 L the breathing circuit "
            r'holds at a partial pressure of one atmosphere \(docs/MODEL.md, "Gas compartments"\)$'
        ),
    ):
        circuit.set_agent_amount(6.1)


def test_one_time_constant_reaches_expected_fraction() -> None:
    circuit = BreathingCircuit(
        max_delivered_concentration_percent=Percent(100.0),
        circuit_volume_l=CompartmentVolume(6.0),
        fresh_gas_flow_l_min=FreshGasFlow(6.0),
        delivered_concentration_percent=Percent(100.0),
    )

    circuit.advance(circuit.time_constant_s)

    assert circuit.inspired_partial_pressure_fraction == pytest.approx(1.0 - exp(-1.0))


def test_zero_fresh_gas_flow_preserves_concentration() -> None:
    circuit = BreathingCircuit(
        circuit_volume_l=CompartmentVolume(6.0),
        max_delivered_concentration_percent=Percent(100.0),
        fresh_gas_flow_l_min=FreshGasFlow(0.0),
        delivered_concentration_percent=Percent(100.0),
        inspired_partial_pressure_fraction=Fraction(0.25),
    )

    circuit.advance(60.0)

    assert circuit.time_constant_s == inf
    assert circuit.inspired_partial_pressure_fraction == 0.25


def test_zero_delivered_concentration_washes_out_circuit() -> None:
    circuit = BreathingCircuit(
        max_delivered_concentration_percent=Percent(100.0),
        circuit_volume_l=CompartmentVolume(6.0),
        fresh_gas_flow_l_min=FreshGasFlow(6.0),
        delivered_concentration_percent=Percent(0.0),
        inspired_partial_pressure_fraction=Fraction(1.0),
    )

    circuit.advance(circuit.time_constant_s)

    assert circuit.inspired_partial_pressure_fraction == pytest.approx(exp(-1.0))


def test_exact_update_is_independent_of_step_size() -> None:
    """One 60 s step and six hundred 0.1 s steps reach the same fraction.

    Both circuits set their dial explicitly rather than taking the default.
    The first assertion is what gives the second one meaning. With the
    vaporizer off, two circuits that both stayed at zero would satisfy the
    comparison, and that agreement would prove nothing.
    """

    one_step = BreathingCircuit(
        circuit_volume_l=CompartmentVolume(6.0),
        max_delivered_concentration_percent=Percent(100.0),
        delivered_concentration_percent=Percent(100.0),
    )
    many_steps = BreathingCircuit(
        circuit_volume_l=CompartmentVolume(6.0),
        max_delivered_concentration_percent=Percent(100.0),
        delivered_concentration_percent=Percent(100.0),
    )

    one_step.advance(60.0)

    for _ in range(600):
        many_steps.advance(0.1)

    assert one_step.inspired_partial_pressure_fraction > 0.0
    assert many_steps.inspired_partial_pressure_fraction == pytest.approx(
        one_step.inspired_partial_pressure_fraction, rel=1e-12
    )


@pytest.mark.parametrize("circuit_volume_l", [0.0, -1.0, float("inf")])
def test_rejects_invalid_circuit_volume(circuit_volume_l: float) -> None:
    with pytest.raises(
        SimulationConfigurationError,
        match="^circuit_volume_l of .* is outside the numerical envelope of 0.01 to 10000 L",
    ):
        BreathingCircuit(
            max_delivered_concentration_percent=Percent(100.0),
            circuit_volume_l=CompartmentVolume(circuit_volume_l, name="circuit_volume_l"),
        )


@pytest.mark.parametrize("fresh_gas_flow_l_min", [-1.0, float("nan")])
def test_rejects_invalid_fresh_gas_flow(fresh_gas_flow_l_min: float) -> None:
    with pytest.raises(SimulationConfigurationError):
        BreathingCircuit(
            circuit_volume_l=CompartmentVolume(6.0),
            max_delivered_concentration_percent=Percent(100.0),
            fresh_gas_flow_l_min=FreshGasFlow(fresh_gas_flow_l_min),
        )


def test_rejects_delivered_concentration_above_the_vaporizer_maximum() -> None:
    """Regression (PL-015): the vaporizer limit is enforced in the core.

    Before the fix the limit lived only in the controller, as a silent
    clamp, and in the UI slider bounds.
    """

    circuit = BreathingCircuit(
        circuit_volume_l=CompartmentVolume(6.0),
        delivered_concentration_percent=Percent(2.0),
        max_delivered_concentration_percent=Percent(5.0),
    )

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        circuit.set_delivered_concentration_percent(Percent(50.0))

    assert circuit.delivered_concentration_percent == 2.0


def test_rejects_construction_above_the_vaporizer_maximum() -> None:
    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        BreathingCircuit(
            circuit_volume_l=CompartmentVolume(6.0),
            delivered_concentration_percent=Percent(8.0),
            max_delivered_concentration_percent=Percent(5.0),
        )


def test_accepts_delivered_concentration_exactly_at_the_vaporizer_maximum() -> None:
    circuit = BreathingCircuit(
        circuit_volume_l=CompartmentVolume(6.0),
        delivered_concentration_percent=Percent(2.0),
        max_delivered_concentration_percent=Percent(5.0),
    )
    circuit.set_delivered_concentration_percent(Percent(5.0))

    assert circuit.delivered_concentration_percent == 5.0


def test_accepts_a_delivered_concentration_of_zero() -> None:
    """A dial at zero, with the vaporizer off, is always valid, because it gives washout."""

    circuit = BreathingCircuit(
        circuit_volume_l=CompartmentVolume(6.0),
        delivered_concentration_percent=Percent(2.0),
        max_delivered_concentration_percent=Percent(5.0),
    )
    circuit.set_delivered_concentration_percent(Percent(0.0))

    assert circuit.delivered_concentration_percent == 0.0


@pytest.mark.parametrize("max_delivered_concentration_percent", [0.0, -0.0], ids=repr)
def test_rejects_invalid_vaporizer_maximum(max_delivered_concentration_percent: float) -> None:
    """Zero is a valid percent but not a valid vaporizer maximum, because it would deliver nothing.

    Zero, of either sign, is the one maximum that the circuit itself refuses.
    A value outside 0 to 100 cannot be built as a `Percent` to pass to the
    circuit. `tests/unit/test_concentration.py` pins those values on the
    constructor, as it does for the dial (`PL-4R3W`). The dial refusal that
    this file pins, above, is a dial set above the vaporizer maximum.
    """

    with pytest.raises(
        SimulationConfigurationError,
        match="^max_delivered_concentration_percent must be positive and finite" + REFUSAL_REASON,
    ):
        BreathingCircuit(
            circuit_volume_l=CompartmentVolume(6.0),
            delivered_concentration_percent=Percent(0.0),
            max_delivered_concentration_percent=Percent(max_delivered_concentration_percent),
        )


def test_accepts_fresh_gas_flow_at_both_ends_of_the_supported_range() -> None:
    """The circuit accepts a fresh gas flow at both ends of the supported range.

    Zero is the vaporizer running into a closed system. The maximum is the
    corner of the settings envelope at which every reference gate measures.
    """

    for fresh_gas_flow_l_min in (0.0, MAXIMUM_FRESH_GAS_FLOW_L_MIN):
        circuit = BreathingCircuit(
            circuit_volume_l=CompartmentVolume(6.0),
            max_delivered_concentration_percent=Percent(100.0),
            fresh_gas_flow_l_min=FreshGasFlow(fresh_gas_flow_l_min),
        )

        assert circuit.fresh_gas_flow_l_min == fresh_gas_flow_l_min

        circuit.set_fresh_gas_flow(FreshGasFlow(fresh_gas_flow_l_min))

        assert circuit.fresh_gas_flow_l_min == fresh_gas_flow_l_min


def test_rejects_fresh_gas_flow_above_the_supported_range() -> None:
    """Regression (PL-0MLQ): the range was documented but never enforced.

    A bare circuit is an exact exponential at any flow, so this guard is not
    about the circuit's own arithmetic. It enforces the model's declared input
    domain. Since `PL-0YYV`, the flow's own type carries that domain. So the
    refusal here comes from `FreshGasFlow`, before the circuit is reached. The
    reasoning is the same as for the vaporizer maximum above.
    """

    circuit = BreathingCircuit(
        circuit_volume_l=CompartmentVolume(6.0),
        max_delivered_concentration_percent=Percent(100.0),
        fresh_gas_flow_l_min=FreshGasFlow(4.0),
    )

    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        circuit.set_fresh_gas_flow(FreshGasFlow(500.0))

    assert circuit.fresh_gas_flow_l_min == 4.0


def test_rejects_construction_with_fresh_gas_flow_above_the_supported_range() -> None:
    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        BreathingCircuit(
            circuit_volume_l=CompartmentVolume(6.0),
            max_delivered_concentration_percent=Percent(100.0),
            fresh_gas_flow_l_min=FreshGasFlow(500.0),
        )


def test_changing_circuit_volume_conserves_stored_agent() -> None:
    """A setter may not create or destroy agent (PL-006).

    The circuit stores agent as a fraction of its volume. So before this guard
    existed, `set_circuit_volume` scaled `agent_amount_l` with the volume, and
    halving the volume halved the agent in it. `docs/MODEL.md`'s required
    invariants rule that out in so many words: "no compartment creates agent
    spontaneously" and "changing a setting does not reset stored state". The
    conservation check that can halt a run is also computed from exactly this
    quantity.
    """

    circuit = BreathingCircuit(
        max_delivered_concentration_percent=Percent(100.0), circuit_volume_l=CompartmentVolume(6.0)
    )
    circuit.set_agent_amount(0.048288200)

    circuit.set_circuit_volume(CompartmentVolume(3.0))

    assert circuit.agent_amount_l == pytest.approx(0.048288200)
    assert circuit.circuit_volume_l == 3.0
    assert circuit.inspired_partial_pressure_fraction == pytest.approx(0.048288200 / 3.0)

    circuit.set_circuit_volume(CompartmentVolume(12.0))

    assert circuit.agent_amount_l == pytest.approx(0.048288200)
    assert circuit.inspired_partial_pressure_fraction == pytest.approx(0.048288200 / 12.0)


def test_a_circuit_volume_too_small_for_its_agent_is_refused_unchanged() -> None:
    """A refused volume leaves the circuit exactly as it was.

    The alternative is to check the capacity after changing the volume. A
    caller who caught the error would then hold a circuit whose volume had
    changed but whose concentration had not.
    """

    circuit = BreathingCircuit(
        max_delivered_concentration_percent=Percent(100.0), circuit_volume_l=CompartmentVolume(6.0)
    )
    circuit.set_agent_amount(2.0)

    with pytest.raises(
        SimulationConfigurationError,
        match=(
            r"^circuit_volume_l of 1.0 is too small for the 2.0 L of agent the breathing "
            r"circuit holds: it would leave room for 1.0 L at a partial pressure of one "
            r'atmosphere \(docs/MODEL.md, "Breathing circuit"\)$'
        ),
    ):
        circuit.set_circuit_volume(CompartmentVolume(1.0))

    assert circuit.circuit_volume_l == 6.0
    assert circuit.agent_amount_l == pytest.approx(2.0)


def test_a_volume_whose_fraction_is_refused_leaves_the_circuit_unchanged() -> None:
    """The fraction a new volume gives is built before either field is written.

    Since `PL-4R3W`, building the fraction is a check, so it can refuse. It
    refuses only when the circuit already stores a fraction that no write would
    have accepted. The test plants one by bypassing `__setattr__`, because
    since `PL-19Y0` the field's own write refuses a bare `nan`. When the
    fraction was built after the volume was written, a refusal left the volume
    changed and the fraction not. The setter's docstring rules out that partial
    state.
    """

    circuit = BreathingCircuit(
        max_delivered_concentration_percent=Percent(100.0), circuit_volume_l=CompartmentVolume(6.0)
    )
    object.__setattr__(circuit, "inspired_partial_pressure_fraction", nan)

    with pytest.raises(
        SimulationConfigurationError,
        match="^inspired_partial_pressure_fraction of nan is outside 0 to 1",
    ):
        circuit.set_circuit_volume(CompartmentVolume(3.0))

    assert circuit.circuit_volume_l == 6.0


def test_a_circuit_volume_exactly_equal_to_its_agent_is_accepted() -> None:
    """The capacity bound is closed, matching `set_agent_amount`'s own."""

    circuit = BreathingCircuit(
        max_delivered_concentration_percent=Percent(100.0), circuit_volume_l=CompartmentVolume(6.0)
    )
    circuit.set_agent_amount(2.0)

    circuit.set_circuit_volume(CompartmentVolume(2.0))

    assert circuit.inspired_partial_pressure_fraction == pytest.approx(1.0)
    assert circuit.agent_amount_l == pytest.approx(2.0)


def _a_circuit_holding_agent() -> BreathingCircuit:
    """Return a circuit with agent, a 2% dial, an 8% vaporizer maximum and a declared flow range.

    Unlike every shipped profile, this machine declares a flow range. So a
    write can be checked against the machine's range as well as the model's
    envelope.
    """

    return BreathingCircuit(
        circuit_volume_l=CompartmentVolume(6.0),
        fresh_gas_flow_l_min=FreshGasFlow(4.0),
        delivered_concentration_percent=Percent(2.0),
        inspired_partial_pressure_fraction=Fraction(0.01),
        max_delivered_concentration_percent=Percent(8.0),
        deliverable_fresh_gas_flow_range=DeliverableFreshGasFlowRange(
            minimum_l_min=0.5, maximum_l_min=8.0
        ),
    )


@pytest.mark.parametrize(
    ("field", "value", "error", "message"),
    [
        pytest.param(
            "circuit_volume_l",
            0.0,
            TypeError,
            "^circuit_volume_l of 0.0 was not built as CompartmentVolume, it is float",
            id="zero-volume",
        ),
        pytest.param(
            "circuit_volume_l",
            nan,
            TypeError,
            "^circuit_volume_l of nan was not built as CompartmentVolume, it is float",
            id="nan-volume",
        ),
        pytest.param(
            "circuit_volume_l",
            True,
            TypeError,
            "^circuit_volume_l of True was not built as CompartmentVolume, it is bool",
            id="bool-volume",
        ),
        pytest.param(
            "fresh_gas_flow_l_min",
            4.0,
            TypeError,
            "^fresh_gas_flow_l_min of 4.0 was not built as FreshGasFlow",
            id="bare-flow",
        ),
        pytest.param(
            "fresh_gas_flow_l_min",
            FreshGasFlow(9.0),
            SimulationConfigurationError,
            "^fresh_gas_flow_l_min of 9.0 is outside what this machine can deliver, "
            "0.5 to 8.0 L/min",
            id="flow-the-machine-cannot-set",
        ),
        pytest.param(
            "delivered_concentration_percent",
            0.5,
            TypeError,
            "^delivered_concentration_percent of 0.5 was not built as Percent",
            id="bare-dial",
        ),
        pytest.param(
            "delivered_concentration_percent",
            Percent(50.0),
            SimulationConfigurationError,
            r"^delivered_concentration_percent exceeds the vaporizer maximum "
            r"\(50% requested, 8% maximum\)$",
            id="dial-past-the-vaporizer-maximum",
        ),
        pytest.param(
            "inspired_partial_pressure_fraction",
            1.5,
            TypeError,
            "^inspired_partial_pressure_fraction of 1.5 was not built as Fraction",
            id="bare-fraction-past-one",
        ),
        pytest.param(
            "inspired_partial_pressure_fraction",
            Percent(1.0),
            TypeError,
            "^inspired_partial_pressure_fraction of 1.0 is a Percent, not a Fraction",
            id="percent-for-a-fraction",
        ),
        pytest.param(
            "max_delivered_concentration_percent",
            10.0,
            TypeError,
            "^max_delivered_concentration_percent of 10.0 was not built as Percent",
            id="bare-maximum",
        ),
        pytest.param(
            "max_delivered_concentration_percent",
            Percent(0.0),
            SimulationConfigurationError,
            "^max_delivered_concentration_percent must be positive and finite" + REFUSAL_REASON,
            id="zero-maximum",
        ),
        pytest.param(
            "max_delivered_concentration_percent",
            Percent(1.0),
            SimulationConfigurationError,
            r"^max_delivered_concentration_percent of 1% is below the 2% the dial is set to, "
            r"and a vaporizer maximum must be at or above its dial$",
            id="maximum-under-the-dial",
        ),
        pytest.param(
            "deliverable_fresh_gas_flow_range",
            DeliverableFreshGasFlowRange(
                minimum_l_min=MAXIMUM_FRESH_GAS_FLOW_L_MIN * 2.0,
                maximum_l_min=MAXIMUM_FRESH_GAS_FLOW_L_MIN * 3.0,
            ),
            SimulationConfigurationError,
            "^this machine can deliver no fresh gas flow the model is claimed over",
            id="range-outside-the-envelope",
        ),
        pytest.param(
            "deliverable_fresh_gas_flow_range",
            DeliverableFreshGasFlowRange(minimum_l_min=5.0, maximum_l_min=8.0),
            SimulationConfigurationError,
            "^fresh_gas_flow_l_min of 4.0 is outside what this machine can deliver, "
            "5.0 to 8.0 L/min",
            id="range-excluding-the-flow-held",
        ),
        pytest.param(
            "deliverable_fresh_gas_flow_range",
            (0.5, 8.0),
            TypeError,
            r"^deliverable_fresh_gas_flow_range of \(0.5, 8.0\) has type tuple",
            id="range-as-a-tuple",
        ),
        pytest.param(
            "fresh_gas_flow",
            FreshGasFlow(2.0),
            AttributeError,
            "^'BreathingCircuit' object has no attribute 'fresh_gas_flow'",
            id="misspelt-field",
        ),
    ],
)
def test_a_direct_write_is_held_to_the_constructors_checks(
    field: str, value: object, error: type[Exception], message: str
) -> None:
    """An assignment that bypasses the constructor and the setters is refused as they refuse it.

    Until `PL-19Y0`, a built circuit accepted every case here except the bare
    flow (`PL-LBQY`) and the misspelt field. A snapshot would then copy the
    value, and the readout beside the control would show it. The accepted
    values included a sevoflurane dial of 50% against its 8% vaporizer, a
    bare-float dial, a zero circuit volume, an inspired fraction of 1.5, and a
    machine range sharing no flow with the model's envelope. That last one
    left `accepted_fresh_gas_flow_range_l_min` inverted at (20.0, 10.0)
    (`PL-HJ7L`). A relation between two fields is refused from either side:
    the dial above the maximum and the maximum below the dial, and the flow
    outside the machine's range and the range excluding the current flow. The
    guard passes a name that is not a field on to the slots, which refuse it.
    So a misspelt write cannot appear to succeed while leaving the intended
    flow unchanged. When a value is refused, nothing is written.
    """

    circuit = _a_circuit_holding_agent()
    held = astuple(circuit)

    with pytest.raises(error, match=message):
        setattr(circuit, field, value)

    assert astuple(circuit) == held


def test_a_copy_of_a_circuit_is_held_to_the_same_checks() -> None:
    """`replace`, a copy and a pickle each write through `__setattr__`, so they refuse what it does.

    `dataclasses.replace` builds a new circuit through the writes that its
    constructor makes. A copy and a pickle of a `slots=True` dataclass restore
    its fields one at a time through `__setattr__`, in field order. The dial is
    written before the maximum. So when a dial was planted by bypassing the
    guard, the maximum's write is the one that refuses it, with the message a
    refused dial gives (`PL-19Y0`).
    """

    circuit = _a_circuit_holding_agent()
    past_the_maximum = (
        r"^delivered_concentration_percent exceeds the vaporizer maximum "
        r"\(50% requested, 8% maximum\)$"
    )

    with pytest.raises(SimulationConfigurationError, match=past_the_maximum):
        replace(circuit, delivered_concentration_percent=Percent(50.0))

    smuggled = copy.copy(circuit)
    object.__setattr__(smuggled, "delivered_concentration_percent", Percent(50.0))

    with pytest.raises(SimulationConfigurationError, match=past_the_maximum):
        copy.copy(smuggled)

    with pytest.raises(SimulationConfigurationError, match=past_the_maximum):
        pickle.loads(pickle.dumps(smuggled))


def _a_sevoflurane_run_stepped_60_s() -> AgentUptakeSystem:
    system = AgentUptakeSystem.for_agent("sevoflurane")

    for _ in range(600):
        system.advance(SimulationStep(0.1))

    return system


def test_a_volume_written_past_set_circuit_volume_is_refused_by_the_next_steps_accounting() -> None:
    """A volume write checks what the constructor checks, and only the setter conserves the agent.

    The circuit stores its agent as a fraction of its volume, so a volume
    written straight onto the field changes the amount of agent with it. On a
    run stepped for 60 s, halving the volume left half the agent that the
    circuit held. No constructor refuses a volume inside the numerical
    envelope, so the field's write does not refuse one either (`PL-19Y0`).
    Instead, the next step halts on the accounting identity and is rolled back,
    rather than carrying the lost agent forward. `set_circuit_volume` is the
    write that conserves the agent, and the same step passes after it.
    """

    written_past = _a_sevoflurane_run_stepped_60_s()
    before = written_past.capture_state()

    written_past.circuit.circuit_volume_l = CompartmentVolume(3.0)

    with pytest.raises(AgentSimulationValidationError, match="^Agent accounting validation failed"):
        written_past.advance(SimulationStep(0.1))

    assert written_past.capture_state() == before

    conserved = _a_sevoflurane_run_stepped_60_s()

    conserved.circuit.set_circuit_volume(CompartmentVolume(3.0))

    assert conserved.advance(SimulationStep(0.1)).agent_accounting.passes_validation


def test_a_bare_circuit_starts_with_the_vaporizer_off() -> None:
    """Regression (PL-019): the class has no default dial position that suits only one agent.

    The delivered dial defaulted to 8%, which is sevoflurane's vaporizer
    maximum, on a class that knows nothing about agents. That had two
    consequences. Declaring any lower device limit raised an error at
    construction. And the message reported an "8% requested" that the caller
    had never written. The second consequence is the one that made the
    default worth removing.

    Zero is the only dial position that every vaporizer of every agent has.
    So it is the only default this class can use without knowing which agent
    is in use. `AgentUptakeSystem.for_agent()` sets the real starting dial.
    """

    circuit = BreathingCircuit(
        circuit_volume_l=CompartmentVolume(6.0), max_delivered_concentration_percent=Percent(5.0)
    )

    assert circuit.delivered_concentration_percent == 0.0
    assert circuit.max_delivered_concentration_percent == 5.0

    circuit.advance(60.0)

    assert circuit.inspired_partial_pressure_fraction == 0.0


@pytest.mark.parametrize("missing", ["circuit_volume_l", "max_delivered_concentration_percent"])
def test_a_circuit_cannot_be_built_without_its_volume_or_its_vaporizer_maximum(
    missing: str,
) -> None:
    """Neither value has a default, so every caller must state the one it means (`PL-M85T`).

    The volume used to default to 6.0 L, a second copy of the value in
    `data/machines/reference_circle_system.json`. Only a test kept that copy
    equal to the file (`PL-4YY1`). The vaporizer maximum used to default to
    100%, which no agent's vaporizer delivers, so a circuit built without it
    accepted any dial setting. `AgentUptakeSystem.for_agent()` passes both from
    the data files.
    """

    given = {
        "circuit_volume_l": CompartmentVolume(6.0),
        "max_delivered_concentration_percent": Percent(8.0),
    }
    del given[missing]

    with pytest.raises(TypeError, match=f"missing 1 required .*argument: '{missing}'"):
        BreathingCircuit(**given)  # type: ignore[arg-type]


def test_the_flow_default_matches_the_shipped_machine_file() -> None:
    """The flow default, its constant and the shipped machine file agree (`PL-QW19`).

    `TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN` is the one default that `PL-M85T`
    kept, because it is more than a copy of a file value. It is the flow a run
    opens at when its machine profile states none. Its only authority is the
    rationale that the shipped file records for storing the same value. So the
    file has to keep stating the value, and the constant, the field default and
    the file have to agree.
    """

    machine = load_reference_circle_system_parameters()
    circuit = BreathingCircuit(
        circuit_volume_l=machine.circuit_volume_l, max_delivered_concentration_percent=Percent(8.0)
    )

    assert circuit.fresh_gas_flow_l_min == machine.default_fresh_gas_flow_l_min
    assert machine.default_fresh_gas_flow_l_min == TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN


def test_for_agent_builds_the_circuit_at_the_machine_file_s_values() -> None:
    """A run built from the shipped profile uses its values, and the 90 s time constant they give.

    Before `PL-4YY1`, `for_agent()` passed neither value. So a run took its
    circuit volume and fresh gas flow from the field defaults in
    `core/circuit.py`, and no provenance row could name where they came from.
    This test asserts the wash-in time constant as well as the two inputs. The
    90 s machine lag is the quantity a learner reads off the early rise, and a
    silent change to either value would move it.

    This test cannot show that the file was read for the flow, because the
    shipped flow equals the field default. A profile that states other values
    shows it. `test_for_agent_builds_the_circuit_at_a_changed_machine_file_volume`
    covers the volume, and
    `test_a_profile_stating_its_startup_flow_opens_the_run_at_that_flow` covers
    the flow. Both tests are below (`PL-H8QP`).
    """

    machine = load_reference_circle_system_parameters()
    circuit = AgentUptakeSystem.for_agent("sevoflurane").circuit

    assert circuit.circuit_volume_l == machine.circuit_volume_l
    assert circuit.fresh_gas_flow_l_min == machine.default_fresh_gas_flow_l_min
    assert circuit.time_constant_s == pytest.approx(90.0)


# --- A profile that states no startup flow (PL-QW19) ---------------------------

# No surveyed machine publishes a startup fresh gas flow, so a machine profile
# may leave `default_fresh_gas_flow_l_min` out, and the run then supplies its
# opening flow. Until `PL-2FZ9` lands, `for_agent()` reads one hardcoded
# profile. So these tests give it a different profile the same way
# `tests/integration/test_controller.py` gives it an edited agent: by replacing
# the loader that it calls. Each profile is the shipped file with one thing
# changed, parsed the way the loader parses it.


def _shipped_machine_payload() -> dict[str, object]:
    text = (
        files("anesthesia_sim.data.machines")
        .joinpath("reference_circle_system.json")
        .read_text(encoding="utf-8")
    )
    payload = json.loads(text)
    assert isinstance(payload, dict)

    return payload


def _run_built_from(
    monkeypatch: pytest.MonkeyPatch, payload: dict[str, object]
) -> AgentUptakeSystem:
    machine = parse_breathing_circuit_parameters(payload)
    monkeypatch.setattr(uptake_system, "load_reference_circle_system_parameters", lambda: machine)

    return AgentUptakeSystem.for_agent("sevoflurane")


def test_a_profile_omitting_the_default_fresh_gas_flow_falls_back_to_the_teaching_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`PL-QW19`: a profile that states no startup flow loads and runs.

    Before, the key was required, so a real machine's profile had to carry a
    flow that no manufacturer publishes. The test changes the volume from the
    shipped 6.0 L, to prove that the run came from this profile. The shipped
    profile states the same 4.0 L/min as the fallback, so the flow alone could
    not tell the two apart. The test also asserts the circuit time constant,
    because that is the quantity a learner reads off the early rise. 8.0 L at
    4.0 L/min gives 120 s.
    """

    payload = _shipped_machine_payload()
    del payload["default_fresh_gas_flow_l_min"]
    payload["circuit_volume_l"] = 8.0

    circuit = _run_built_from(monkeypatch, payload).circuit

    assert circuit.circuit_volume_l == 8.0
    assert circuit.fresh_gas_flow_l_min == TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN
    assert circuit.time_constant_s == pytest.approx(120.0)


def test_a_profile_stating_its_startup_flow_opens_the_run_at_that_flow(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The fallback applies only when the profile states no flow, and never replaces a stated one.

    This test is needed because the shipped profile states the same 4.0 L/min
    as the fallback. So a `for_agent()` that always took the fallback would
    pass every other test in this file.
    """

    payload = _shipped_machine_payload()
    payload["default_fresh_gas_flow_l_min"] = 2.0

    circuit = _run_built_from(monkeypatch, payload).circuit

    assert circuit.fresh_gas_flow_l_min == 2.0
    assert circuit.time_constant_s == pytest.approx(180.0)


def test_a_silent_profile_whose_range_excludes_the_teaching_default_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The fallback must lie in the machine's declared range, and is not adjusted to fit it.

    `BreathingCircuit` refuses it, in the words it uses for a stated flow
    outside the range. The run is not opened at a flow the machine cannot
    set, and the flow is not clamped to a value nobody chose.
    """

    payload = _shipped_machine_payload()
    del payload["default_fresh_gas_flow_l_min"]
    payload["deliverable_fresh_gas_flow_range"] = {"minimum_l_min": 0.5, "maximum_l_min": 3.0}

    refusal = (
        f"fresh_gas_flow_l_min of {TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN} is outside "
        "what this machine can deliver, 0.5 to 3.0 L/min"
    )
    with pytest.raises(SimulationConfigurationError, match=re.escape(refusal)):
        _run_built_from(monkeypatch, payload)


# --- A profile stating another volume (PL-H8QP) -------------------------------

# Until `PL-M85T`, the shipped profile's volume was also `BreathingCircuit`'s
# field default. So no run built from that profile showed whether
# `for_agent()` read the volume at all. A run built from a profile that states
# a different volume does show it. That profile is handed over in the same way
# as the profiles above.


def test_for_agent_builds_the_circuit_at_a_changed_machine_file_volume(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A `for_agent()` that stopped passing the profile's volume fails here.

    Such a `for_agent()` would build the run at another volume, or fail to
    build it. Every provenance row pointing at
    `data/machines/reference_circle_system.json` would then quietly become a
    claim about a file the model no longer consults. 3.3 L at the shipped
    4.0 L/min gives a time constant of 49.5 s.
    """

    payload = _shipped_machine_payload()
    payload["circuit_volume_l"] = 3.3

    circuit = _run_built_from(monkeypatch, payload).circuit

    assert circuit.circuit_volume_l == 3.3
    assert circuit.time_constant_s == pytest.approx(49.5)


# --- The machine's deliverable flow range (PL-8PS6) --------------------------

# The circuit is the one object that holds both claims about the fresh gas
# flow: the model's envelope in `core/supported_ranges.py` and the range that a
# machine profile declares. The tests below cover the machine's range.
# `tests/unit/test_supported_ranges.py` pins the split itself, so that neither
# claim can be mistaken for the other. It does so beside the envelope, which
# the machine's range must not widen.


def test_a_declared_range_includes_both_of_its_own_endpoints() -> None:
    """A declared range is closed, like every interval that `core/supported_ranges.py` declares.

    A machine's minimum flow is a setting the machine can reach, not the first
    setting it refuses. The same is true of the top of its flowmeter.
    """

    circuit = BreathingCircuit(
        circuit_volume_l=CompartmentVolume(6.0),
        max_delivered_concentration_percent=Percent(100.0),
        fresh_gas_flow_l_min=FreshGasFlow(1.0),
        deliverable_fresh_gas_flow_range=DeliverableFreshGasFlowRange(
            minimum_l_min=0.5, maximum_l_min=8.0
        ),
    )

    for flow in (0.5, 4.0, 8.0):
        circuit.set_fresh_gas_flow(FreshGasFlow(flow))
        assert circuit.fresh_gas_flow_l_min == flow


def test_construction_is_refused_at_a_flow_the_machine_cannot_deliver() -> None:
    """The constructor is a third way to set the flow, so it applies the guard too.

    `BreathingCircuit(fresh_gas_flow_l_min=...)` sets the field without going
    through `set_fresh_gas_flow`. `PL-0MLQ` found the same gap for the model's
    own envelope.
    """

    with pytest.raises(SimulationConfigurationError, match="machine can deliver"):
        BreathingCircuit(
            circuit_volume_l=CompartmentVolume(6.0),
            max_delivered_concentration_percent=Percent(100.0),
            fresh_gas_flow_l_min=FreshGasFlow(0.2),
            deliverable_fresh_gas_flow_range=DeliverableFreshGasFlowRange(
                minimum_l_min=0.5, maximum_l_min=8.0
            ),
        )


def test_a_profile_declaring_no_range_leaves_the_model_envelope_alone() -> None:
    """`None` means the profile makes no claim, and it is what the shipped profile records.

    No operator's manual or manufacturer specification giving a deliverable
    range was reachable for any surveyed machine. So the field is `null` in
    `data/machines/reference_circle_system.json`, and the envelope is the only
    bound. That is the behavior that shipped before the field existed.
    """

    circuit = BreathingCircuit(
        circuit_volume_l=CompartmentVolume(6.0), max_delivered_concentration_percent=Percent(100.0)
    )

    assert circuit.deliverable_fresh_gas_flow_range is None

    circuit.set_fresh_gas_flow(FreshGasFlow(MAXIMUM_FRESH_GAS_FLOW_L_MIN))

    assert circuit.fresh_gas_flow_l_min == MAXIMUM_FRESH_GAS_FLOW_L_MIN

    with pytest.raises(SimulationConfigurationError, match="compartment model"):
        circuit.set_fresh_gas_flow(FreshGasFlow(MAXIMUM_FRESH_GAS_FLOW_L_MIN + 1.0))


def test_a_machine_that_overlaps_the_envelope_nowhere_is_refused_when_built() -> None:
    """The mismatch is reported once, rather than discovered one refused setting at a time.

    Every flow that such a profile can deliver is outside the model's
    envelope, and every flow the model supports is outside the profile's
    range. So each separate refusal would be correct, but none of them would
    say that it is the pairing of this machine with the model that cannot be
    simulated.
    """

    with pytest.raises(SimulationConfigurationError) as raised:
        BreathingCircuit(
            circuit_volume_l=CompartmentVolume(6.0),
            max_delivered_concentration_percent=Percent(100.0),
            deliverable_fresh_gas_flow_range=DeliverableFreshGasFlowRange(
                minimum_l_min=MAXIMUM_FRESH_GAS_FLOW_L_MIN + 2.0,
                maximum_l_min=MAXIMUM_FRESH_GAS_FLOW_L_MIN + 5.0,
            ),
        )

    message = str(raised.value)

    assert "no fresh gas flow the model is claimed over" in message
    assert "12.0 to 15.0 L/min" in message
    assert f"{MINIMUM_FRESH_GAS_FLOW_L_MIN} to {MAXIMUM_FRESH_GAS_FLOW_L_MIN} L/min" in message


def test_a_range_touching_the_envelope_at_one_point_is_built() -> None:
    """The overlap test is on the closed intervals, so one shared flow is enough."""

    circuit = BreathingCircuit(
        circuit_volume_l=CompartmentVolume(6.0),
        max_delivered_concentration_percent=Percent(100.0),
        fresh_gas_flow_l_min=FreshGasFlow(MAXIMUM_FRESH_GAS_FLOW_L_MIN),
        deliverable_fresh_gas_flow_range=DeliverableFreshGasFlowRange(
            minimum_l_min=MAXIMUM_FRESH_GAS_FLOW_L_MIN,
            maximum_l_min=MAXIMUM_FRESH_GAS_FLOW_L_MIN + 5.0,
        ),
    )

    assert circuit.fresh_gas_flow_l_min == MAXIMUM_FRESH_GAS_FLOW_L_MIN


def test_a_range_whose_minimum_is_above_its_maximum_is_refused() -> None:
    """An inverted range refuses every setting while appearing to describe what a machine can do."""

    with pytest.raises(SimulationConfigurationError, match="minimum above its maximum"):
        DeliverableFreshGasFlowRange(minimum_l_min=8.0, maximum_l_min=0.5)


@pytest.mark.parametrize("value", (-1.0, -0.0001, float("nan"), inf, -inf))
def test_a_range_end_that_is_negative_or_not_finite_is_refused(value: float) -> None:
    """A machine delivers no negative flow, and `nan` compares false against both ends."""

    with pytest.raises(SimulationConfigurationError):
        DeliverableFreshGasFlowRange(minimum_l_min=value, maximum_l_min=8.0)

    with pytest.raises(SimulationConfigurationError):
        DeliverableFreshGasFlowRange(minimum_l_min=0.5, maximum_l_min=value)


def test_a_range_may_be_floored_at_zero() -> None:
    """Zero is meaningful for one machine property: a true off position.

    `_validate_nonnegative_finite` exists in `core/parameters.py` for this
    case alone. A guard written as "positive and finite" would make it
    impossible to describe a machine whose common gas outlet turns off.
    """

    circuit = BreathingCircuit(
        circuit_volume_l=CompartmentVolume(6.0),
        max_delivered_concentration_percent=Percent(100.0),
        deliverable_fresh_gas_flow_range=DeliverableFreshGasFlowRange(
            minimum_l_min=0.0, maximum_l_min=8.0
        ),
    )

    circuit.set_fresh_gas_flow(FreshGasFlow(0.0))

    assert circuit.fresh_gas_flow_l_min == 0.0


def test_for_agent_passes_the_machine_file_s_declared_range_to_the_circuit() -> None:
    """This tests the route, not the value, because the shipped profile's range is `None` today.

    The assertion protects the path by which a profile that does declare a
    range reaches the circuit. Without it, the range could be parsed and then
    dropped on its way from the profile to the circuit.
    """

    machine = load_reference_circle_system_parameters()
    circuit = AgentUptakeSystem.for_agent("sevoflurane").circuit

    assert machine.deliverable_fresh_gas_flow_range is None
    assert circuit.deliverable_fresh_gas_flow_range is machine.deliverable_fresh_gas_flow_range


# --- The one statement of the intersection (PL-7CRY) --------------------------

# `accepted_fresh_gas_flow_range_l_min` sets the bounds of the interface's fresh
# gas flow control. So these tests require it to be exactly the flows that the
# circuit accepts. Both of its ends must be accepted, and the flow just past
# each end must be refused, by the model's guard or the machine's. "Just past"
# is far smaller than any step a control offers, so the ends are pinned as the
# closed interval and nothing wider.

_JUST_PAST_AN_END_L_MIN = 1e-6


@pytest.mark.parametrize(
    ("declared", "accepted"),
    (
        # No claim: the model's envelope is the only bound.
        (None, (MINIMUM_FRESH_GAS_FLOW_L_MIN, MAXIMUM_FRESH_GAS_FLOW_L_MIN)),
        # Narrower at both ends: the machine's range.
        ((0.5, 8.0), (0.5, 8.0)),
        # Wider at the top: the machine's minimum and the model's maximum.
        ((0.5, 15.0), (0.5, MAXIMUM_FRESH_GAS_FLOW_L_MIN)),
        # Touching the envelope at one flow: that flow alone.
        (
            (MAXIMUM_FRESH_GAS_FLOW_L_MIN, 15.0),
            (MAXIMUM_FRESH_GAS_FLOW_L_MIN, MAXIMUM_FRESH_GAS_FLOW_L_MIN),
        ),
    ),
)
def test_the_accepted_range_is_exactly_the_flows_the_circuit_accepts(
    declared: tuple[float, float] | None, accepted: tuple[float, float]
) -> None:
    """Both ends are settings the circuit takes, and the flow past either is refused.

    A control that the learner drags reads this property. So an end that the
    circuit refused would be a setting offered and then turned down. A range
    narrower than the circuit's would hide flows that the run supports.
    """

    lowest, highest = accepted
    circuit = BreathingCircuit(
        circuit_volume_l=CompartmentVolume(6.0),
        max_delivered_concentration_percent=Percent(100.0),
        fresh_gas_flow_l_min=FreshGasFlow(lowest),
        deliverable_fresh_gas_flow_range=(
            None
            if declared is None
            else DeliverableFreshGasFlowRange(minimum_l_min=declared[0], maximum_l_min=declared[1])
        ),
    )

    assert circuit.accepted_fresh_gas_flow_range_l_min == accepted

    for end in accepted:
        circuit.set_fresh_gas_flow(FreshGasFlow(end))
        assert circuit.fresh_gas_flow_l_min == end

    for past in (lowest - _JUST_PAST_AN_END_L_MIN, highest + _JUST_PAST_AN_END_L_MIN):
        with pytest.raises(SimulationConfigurationError):
            circuit.set_fresh_gas_flow(FreshGasFlow(past))


@pytest.mark.parametrize("simulation_step_s", [nextafter(1e-3, 0.0), 1e-6, 1e-14, 5e-324])
def test_a_step_below_the_floor_is_refused_when_the_circuit_is_stepped_alone(
    simulation_step_s: float,
) -> None:
    """`PL-WP52`: the circuit stepped on its own refuses a step shorter than 1 ms.

    Rounding grows as the step shrinks in the circuit stepped alone, as it does in
    a run. Over 10 000 steps of 1e-14 s, a 6 L circuit's wash-in at 6 L/min was 4%
    wrong. Both `advance_fresh_gas` and `advance` refuse the step, and the
    inspired fraction does not change. The 1 ms minimum itself is accepted, and so
    is a step of 1 s, longer than the run's 0.1 s maximum, which does not apply to
    a compartment stepped alone. The expected minimum, 0.001 s, is written out here
    rather than read from `MINIMUM_SIMULATION_STEP_S`.
    """

    circuit = BreathingCircuit(
        max_delivered_concentration_percent=Percent(100.0),
        circuit_volume_l=CompartmentVolume(6.0),
        fresh_gas_flow_l_min=FreshGasFlow(6.0),
        delivered_concentration_percent=Percent(2.0),
    )
    refusal = (
        rf"^circuit simulation_step_s of {re.escape(str(simulation_step_s))} s is shorter "
        r"than the smallest supported step of 0\.001 s, below which rounding is a "
        r'growing share of what each step changes \(docs/MODEL.md, "Supported '
        r'simulation step"\)$'
    )

    with pytest.raises(SimulationConfigurationError, match=refusal):
        circuit.advance_fresh_gas(simulation_step_s)

    with pytest.raises(SimulationConfigurationError, match=refusal):
        circuit.advance(simulation_step_s)

    assert circuit.inspired_partial_pressure_fraction == 0.0

    circuit.advance_fresh_gas(0.001)
    circuit.advance(1.0)

    assert circuit.inspired_partial_pressure_fraction > 0.0


@pytest.mark.parametrize(
    "simulation_step_s", [nextafter(86_400.0, inf), 1e6, 1e308, 1.7976931348623157e308]
)
def test_a_step_past_the_run_length_is_refused_when_the_circuit_is_stepped_alone(
    simulation_step_s: float,
) -> None:
    """`PL-YT3T`: the circuit stepped on its own refuses a step longer than 24 h.

    Before the ceiling, a step near 1e308 s overflowed the count of time constants
    elapsed to `inf`, and the exhaust came back as `inf` or `nan`. Both
    `advance_fresh_gas` and `advance` refuse the step, and the inspired fraction does
    not change. The ceiling itself is accepted. The expected ceiling, 86 400 s, is
    written out here rather than read from `MAXIMUM_ELAPSED_SIMULATION_TIME_S`.
    """

    circuit = BreathingCircuit(
        max_delivered_concentration_percent=Percent(100.0),
        circuit_volume_l=CompartmentVolume(6.0),
        fresh_gas_flow_l_min=FreshGasFlow(6.0),
        delivered_concentration_percent=Percent(2.0),
    )
    refusal = (
        rf"^circuit simulation_step_s of {re.escape(str(simulation_step_s))} s is longer "
        r"than the supported run length of 86400 s \(24 h\), the most simulated time "
        r"this model is claimed to represent a patient over, so no single step may be "
        r'longer \(docs/MODEL.md, "Supported simulation step"\)$'
    )

    with pytest.raises(SimulationConfigurationError, match=refusal):
        circuit.advance_fresh_gas(simulation_step_s)

    with pytest.raises(SimulationConfigurationError, match=refusal):
        circuit.advance(simulation_step_s)

    assert circuit.inspired_partial_pressure_fraction == 0.0

    circuit.advance(86_400.0)

    assert circuit.inspired_partial_pressure_fraction == pytest.approx(0.02, rel=1e-15)


@pytest.mark.parametrize(
    ("starting_fraction", "dial_percent", "delivered_l", "exhausted_l"),
    [
        # Wash-in: 10 L/min for 86 400 s admits 14 400 L at 2%, which is 288 L of
        # agent. The empty 0.01 L circuit keeps 0.01 x 0.02 = 2e-4 L of it.
        (0.0, 2.0, 288.0, 288.0 - 2e-4),
        # The dial equals the circuit: everything delivered leaves. This case
        # returned an exhaust of nan (0 x inf) at a step near 1e308 s.
        (0.02, 2.0, 288.0, 288.0),
        # Washout with the dial off: the 0.01 x 0.05 = 5e-4 L held all leaves.
        (0.05, 0.0, 0.0, 5e-4),
    ],
)
def test_the_circuit_stepped_alone_at_the_ceiling_returns_a_finite_exchange_at_the_envelope_corner(
    starting_fraction: float, dial_percent: float, delivered_l: float, exhausted_l: float
) -> None:
    """`PL-YT3T`: at the step ceiling and the envelope's stiffest circuit, the exchange is exact.

    The circuit is the smallest that the numerical envelope admits, 0.01 L, at the
    largest supported fresh gas flow, 10 L/min, stepped by the 86 400 s ceiling. That
    is about 1.4e6 time constants, the most any accepted step can elapse. The circuit
    ends at the dial's fraction, and the expected amounts are worked by hand in the
    parameter list, from the flow, the step, the volume and the fractions. They are
    not read from the code under test.
    """

    circuit = BreathingCircuit(
        max_delivered_concentration_percent=Percent(100.0),
        circuit_volume_l=CompartmentVolume(0.01),
        fresh_gas_flow_l_min=FreshGasFlow(10.0),
        delivered_concentration_percent=Percent(dial_percent),
    )
    circuit.set_inspired_partial_pressure_fraction(Fraction(starting_fraction))

    exchange = circuit.advance_fresh_gas(86_400.0)

    assert circuit.inspired_partial_pressure_fraction == pytest.approx(
        dial_percent / 100.0, rel=1e-15, abs=0.0
    )
    assert exchange.delivered_agent_l == pytest.approx(delivered_l, rel=1e-12, abs=0.0)
    assert exchange.exhausted_agent_l == pytest.approx(exhausted_l, rel=1e-12, abs=0.0)
