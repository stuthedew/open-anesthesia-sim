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


def test_rejects_agent_amount_above_circuit_capacity() -> None:
    circuit = BreathingCircuit()

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
        circuit_volume_l=6.0,
        fresh_gas_flow_l_min=FreshGasFlow(6.0),
        delivered_concentration_percent=Percent(100.0),
    )

    circuit.advance(circuit.time_constant_s)

    assert circuit.inspired_partial_pressure_fraction == pytest.approx(1.0 - exp(-1.0))


def test_zero_fresh_gas_flow_preserves_concentration() -> None:
    circuit = BreathingCircuit(
        fresh_gas_flow_l_min=FreshGasFlow(0.0),
        delivered_concentration_percent=Percent(100.0),
        inspired_partial_pressure_fraction=Fraction(0.25),
    )

    circuit.advance(60.0)

    assert circuit.time_constant_s == inf
    assert circuit.inspired_partial_pressure_fraction == 0.25


def test_zero_delivered_concentration_washes_out_circuit() -> None:
    circuit = BreathingCircuit(
        circuit_volume_l=6.0,
        fresh_gas_flow_l_min=FreshGasFlow(6.0),
        delivered_concentration_percent=Percent(0.0),
        inspired_partial_pressure_fraction=Fraction(1.0),
    )

    circuit.advance(circuit.time_constant_s)

    assert circuit.inspired_partial_pressure_fraction == pytest.approx(exp(-1.0))


def test_exact_update_is_independent_of_step_size() -> None:
    """One 60 s step and six hundred 0.1 s steps reach the same fraction.

    Both circuits name their dial rather than taking the default, and the
    first assertion is what makes the second mean something: with the
    vaporizer off this comparison is satisfied by two circuits that both
    stayed at zero, which is agreement about nothing.
    """

    one_step = BreathingCircuit(delivered_concentration_percent=Percent(100.0))
    many_steps = BreathingCircuit(delivered_concentration_percent=Percent(100.0))

    one_step.advance(60.0)

    for _ in range(600):
        many_steps.advance(0.1)

    assert one_step.inspired_partial_pressure_fraction > 0.0
    assert many_steps.inspired_partial_pressure_fraction == pytest.approx(
        one_step.inspired_partial_pressure_fraction, rel=1e-12
    )


@pytest.mark.parametrize("circuit_volume_l", [0.0, -1.0, float("inf")])
def test_rejects_invalid_circuit_volume(circuit_volume_l: float) -> None:
    with pytest.raises(SimulationConfigurationError):
        BreathingCircuit(circuit_volume_l=circuit_volume_l)


@pytest.mark.parametrize("fresh_gas_flow_l_min", [-1.0, float("nan")])
def test_rejects_invalid_fresh_gas_flow(fresh_gas_flow_l_min: float) -> None:
    with pytest.raises(SimulationConfigurationError):
        BreathingCircuit(fresh_gas_flow_l_min=FreshGasFlow(fresh_gas_flow_l_min))


def test_rejects_delivered_concentration_above_the_vaporizer_maximum() -> None:
    """Regression (PL-015): the vaporizer limit is enforced in the core.

    Before the fix the limit lived only in the controller, as a silent
    clamp, and in the UI slider bounds.
    """

    circuit = BreathingCircuit(
        delivered_concentration_percent=Percent(2.0),
        max_delivered_concentration_percent=Percent(5.0),
    )

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        circuit.set_delivered_concentration_percent(Percent(50.0))

    assert circuit.delivered_concentration_percent == 2.0


def test_rejects_construction_above_the_vaporizer_maximum() -> None:
    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        BreathingCircuit(
            delivered_concentration_percent=Percent(8.0),
            max_delivered_concentration_percent=Percent(5.0),
        )


def test_accepts_delivered_concentration_exactly_at_the_vaporizer_maximum() -> None:
    circuit = BreathingCircuit(
        delivered_concentration_percent=Percent(2.0),
        max_delivered_concentration_percent=Percent(5.0),
    )
    circuit.set_delivered_concentration_percent(Percent(5.0))

    assert circuit.delivered_concentration_percent == 5.0


def test_accepts_a_delivered_concentration_of_zero() -> None:
    """The vaporizer off is always a valid dial position: it is washout."""

    circuit = BreathingCircuit(
        delivered_concentration_percent=Percent(2.0),
        max_delivered_concentration_percent=Percent(5.0),
    )
    circuit.set_delivered_concentration_percent(Percent(0.0))

    assert circuit.delivered_concentration_percent == 0.0


@pytest.mark.parametrize("max_delivered_concentration_percent", [0.0, -0.0], ids=repr)
def test_rejects_invalid_vaporizer_maximum(max_delivered_concentration_percent: float) -> None:
    """A vaporizer that delivers nothing has a percent but no maximum.

    Zero, either sign, is the one maximum the circuit itself refuses. A value
    outside 0 to 100 cannot be built as a `Percent` to hand it, and
    `tests/unit/test_concentration.py` pins those on the constructor, as it
    does the dial's (`PL-4R3W`); the dial's own refusal here is the vaporizer
    maximum, pinned above.
    """

    with pytest.raises(
        SimulationConfigurationError,
        match="^max_delivered_concentration_percent must be positive and finite$",
    ):
        BreathingCircuit(
            delivered_concentration_percent=Percent(0.0),
            max_delivered_concentration_percent=Percent(max_delivered_concentration_percent),
        )


def test_accepts_fresh_gas_flow_at_both_ends_of_the_supported_range() -> None:
    """Zero is the vaporizer running into a closed system; the maximum is the
    corner of the settings envelope every reference gate measures at."""

    for fresh_gas_flow_l_min in (0.0, MAXIMUM_FRESH_GAS_FLOW_L_MIN):
        circuit = BreathingCircuit(fresh_gas_flow_l_min=FreshGasFlow(fresh_gas_flow_l_min))

        assert circuit.fresh_gas_flow_l_min == fresh_gas_flow_l_min

        circuit.set_fresh_gas_flow(FreshGasFlow(fresh_gas_flow_l_min))

        assert circuit.fresh_gas_flow_l_min == fresh_gas_flow_l_min


def test_rejects_fresh_gas_flow_above_the_supported_range() -> None:
    """Regression (PL-0MLQ): the range was documented but never enforced.

    A bare circuit is an exact exponential at any flow, so this guard is not
    about the circuit's own arithmetic — it is the model's declared input
    domain, which since `PL-0YYV` the flow's own type carries: the refusal
    here is `FreshGasFlow`'s, before the circuit is reached, on the same
    argument the vaporizer maximum above rests on.
    """

    circuit = BreathingCircuit(fresh_gas_flow_l_min=FreshGasFlow(4.0))

    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        circuit.set_fresh_gas_flow(FreshGasFlow(500.0))

    assert circuit.fresh_gas_flow_l_min == 4.0


def test_rejects_construction_with_fresh_gas_flow_above_the_supported_range() -> None:
    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        BreathingCircuit(fresh_gas_flow_l_min=FreshGasFlow(500.0))


def test_changing_circuit_volume_conserves_stored_agent() -> None:
    """A setter may not create or destroy agent (PL-006).

    Agent is held as a fraction of the volume, so before this guard existed
    `set_circuit_volume` scaled `agent_amount_l` with the volume: halving the
    volume halved the agent in it. `docs/MODEL.md`'s required invariants say
    otherwise in terms - "no compartment creates agent spontaneously" and
    "changing a setting does not reset stored state" - and the conservation
    check that can halt a run is computed from exactly this quantity.
    """

    circuit = BreathingCircuit(circuit_volume_l=6.0)
    circuit.set_agent_amount(0.048288200)

    circuit.set_circuit_volume(3.0)

    assert circuit.agent_amount_l == pytest.approx(0.048288200)
    assert circuit.circuit_volume_l == 3.0
    assert circuit.inspired_partial_pressure_fraction == pytest.approx(0.048288200 / 3.0)

    circuit.set_circuit_volume(12.0)

    assert circuit.agent_amount_l == pytest.approx(0.048288200)
    assert circuit.inspired_partial_pressure_fraction == pytest.approx(0.048288200 / 12.0)


def test_a_circuit_volume_too_small_for_its_agent_is_refused_unchanged() -> None:
    """A refused volume leaves the circuit exactly as it was.

    The alternative - checking capacity after moving the volume - would leave
    a caller who caught the error holding a circuit whose volume had changed
    and whose concentration had not.
    """

    circuit = BreathingCircuit(circuit_volume_l=6.0)
    circuit.set_agent_amount(2.0)

    with pytest.raises(
        SimulationConfigurationError, match="^circuit_volume_l is smaller than stored agent$"
    ):
        circuit.set_circuit_volume(1.0)

    assert circuit.circuit_volume_l == 6.0
    assert circuit.agent_amount_l == pytest.approx(2.0)


def test_a_volume_whose_fraction_is_refused_leaves_the_circuit_unchanged() -> None:
    """The fraction a new volume gives is built before either field is written.

    Since `PL-4R3W` building it is a check, so it can refuse - though only for
    a fraction already held that no write would have accepted, which the
    write past `__setattr__` below stands in for: since `PL-19Y0` the field's
    own write refuses a bare `nan`. Built after the volume was written, a
    refusal there left the volume moved and the fraction not, the partial
    state the docstring rules out.
    """

    circuit = BreathingCircuit(circuit_volume_l=6.0)
    object.__setattr__(circuit, "inspired_partial_pressure_fraction", nan)

    with pytest.raises(
        SimulationConfigurationError,
        match="^inspired_partial_pressure_fraction of nan is outside 0 to 1",
    ):
        circuit.set_circuit_volume(3.0)

    assert circuit.circuit_volume_l == 6.0


def test_a_circuit_volume_exactly_equal_to_its_agent_is_accepted() -> None:
    """The capacity bound is closed, matching `set_agent_amount`'s own."""

    circuit = BreathingCircuit(circuit_volume_l=6.0)
    circuit.set_agent_amount(2.0)

    circuit.set_circuit_volume(2.0)

    assert circuit.inspired_partial_pressure_fraction == pytest.approx(1.0)
    assert circuit.agent_amount_l == pytest.approx(2.0)


def _a_circuit_holding_agent() -> BreathingCircuit:
    """A circuit holding agent at a 2% dial under an 8% vaporizer, on a machine declaring a range.

    Declared, unlike every shipped profile, so that a write can be held to the
    machine's range as well as to the model's envelope.
    """

    return BreathingCircuit(
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
            SimulationConfigurationError,
            "^circuit_volume_l must be positive and finite$",
            id="zero-volume",
        ),
        pytest.param(
            "circuit_volume_l",
            nan,
            SimulationConfigurationError,
            "^circuit_volume_l must be positive and finite$",
            id="nan-volume",
        ),
        pytest.param(
            "circuit_volume_l",
            True,
            TypeError,
            "^circuit_volume_l of True has type bool",
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
            "^max_delivered_concentration_percent must be positive and finite$",
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
            DeliverableFreshGasFlowRange(minimum_l_min=20.0, maximum_l_min=30.0),
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
    """An assignment past the constructor and the setters is refused as they refuse it.

    Each case but the bare flow (`PL-LBQY`) and the misspelt field was
    accepted on a built circuit until `PL-19Y0`, for a snapshot to copy and the
    readout beside the control to show: a sevoflurane dial of 50% against its
    8% vaporizer, a bare-float dial, a zero circuit volume, an inspired
    fraction of 1.5, and a machine range sharing no flow with the model's
    envelope, which left `accepted_fresh_gas_flow_range_l_min` inverted at
    (20.0, 10.0) (`PL-HJ7L`). A relation is refused from either side: the dial
    above the maximum and the maximum under the dial, the flow outside the
    machine's range and the range excluding the flow held. A name that is no
    field passes the guard to the slots, which refuse it, so a misspelt write
    cannot leave the flow it meant unchanged while appearing to succeed.
    Nothing is written when a value is refused.
    """

    circuit = _a_circuit_holding_agent()
    held = astuple(circuit)

    with pytest.raises(error, match=message):
        setattr(circuit, field, value)

    assert astuple(circuit) == held


def test_a_copy_of_a_circuit_is_held_to_the_same_checks() -> None:
    """`replace`, a copy and a pickle each write through `__setattr__`, refusing what it refuses.

    `dataclasses.replace` builds a new circuit through its constructor's
    writes, and a copy and a pickle of a `slots=True` dataclass restore its
    fields one at a time through `__setattr__`, in field order. The dial is
    written before the maximum, so the maximum's write is the one that refuses
    a dial planted past the guard, in the dial's own words (`PL-19Y0`).
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
    """A volume's write checks what its constructor checks; conserving the agent is the setter's.

    The circuit holds its agent as a fraction of its volume, so a volume
    written straight onto the field moves the agent with it: halved on a run
    stepped 60 s, it left half the agent the circuit held. No constructor
    refuses a positive volume, so its write does not either (`PL-19Y0`), and
    the step after it halts on the accounting identity and is rolled back
    rather than carrying the lost agent forward. `set_circuit_volume` is the
    write that conserves the agent, and the same step after it passes.
    """

    written_past = _a_sevoflurane_run_stepped_60_s()
    before = written_past.capture_state()

    written_past.circuit.circuit_volume_l = 3.0

    with pytest.raises(AgentSimulationValidationError, match="^Agent accounting validation failed"):
        written_past.advance(SimulationStep(0.1))

    assert written_past.capture_state() == before

    conserved = _a_sevoflurane_run_stepped_60_s()

    conserved.circuit.set_circuit_volume(3.0)

    assert conserved.advance(SimulationStep(0.1)).agent_accounting.passes_validation


def test_a_bare_circuit_starts_with_the_vaporizer_off() -> None:
    """Regression (PL-019): the class holds no agent-shaped dial position.

    The delivered dial defaulted to 8% - sevoflurane's vaporizer maximum -
    on a class that knows nothing about agents. Two consequences, and the
    second is the one that made it worth removing: declaring any lower
    device limit raised at construction, and the message reported an "8%
    requested" the caller had never written.

    Zero is the only dial position every vaporizer of every agent has, so
    it is the only one this class can hold without knowing which agent is
    in use. `AgentUptakeSystem.for_agent()` sets the real starting dial.
    """

    circuit = BreathingCircuit(max_delivered_concentration_percent=Percent(5.0))

    assert circuit.delivered_concentration_percent == 0.0
    assert circuit.max_delivered_concentration_percent == 5.0

    circuit.advance(60.0)

    assert circuit.inspired_partial_pressure_fraction == 0.0


def test_the_bare_circuit_defaults_match_the_shipped_machine_file() -> None:
    """`PL-4YY1`: the literals in `core/circuit.py` are a checked restatement.

    `data/machines/reference_circle_system.json` is the authority, and
    `AgentUptakeSystem.for_agent()` passes its volume explicitly, so the
    volume default is reached only by a bare unit-test construction. It is
    kept so that a test of circuit physics need not load package data — but a
    reader meeting `circuit_volume_l: float = 6.0` in `core/circuit.py` will
    take it for the model's circuit volume whatever the docstring says, so the
    two are not allowed to drift apart silently.

    The flow default is `TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN`, and since
    `PL-QW19` it is more than a restatement: it is the flow a run opens at when
    its machine profile states none, and its only authority is the rationale
    this file records for storing the same value. So the file has to keep
    stating it, and the constant, the field default and the file have to agree.

    Deliberately not solved by importing the loader into `core/circuit.py`:
    `core/parameters.py` is the one module permitted to import Pydantic
    (`tools/import_boundary_check.py` enforces it), and reading package data
    at class-definition time would make a pure physics class depend on the
    installed distribution's files.
    """

    machine = load_reference_circle_system_parameters()
    circuit = BreathingCircuit()

    assert circuit.circuit_volume_l == machine.circuit_volume_l
    assert circuit.fresh_gas_flow_l_min == machine.default_fresh_gas_flow_l_min
    assert machine.default_fresh_gas_flow_l_min == TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN


def test_for_agent_builds_the_circuit_at_the_machine_file_s_values() -> None:
    """A run from the shipped profile carries its values, and the 90 s they give.

    Before `PL-4YY1` `for_agent()` named neither, so a run took its circuit
    volume and fresh gas flow from `core/circuit.py`'s field defaults and no
    provenance row could name where they came from. Asserting the wash-in time
    constant as well as the two inputs is the point of the pair: the 90 s
    machine lag is the quantity a learner reads off the early rise, and it is
    what a silent change to either value would move.

    It cannot show that the file was read, because the shipped values equal
    those field defaults. A profile stating other values shows it:
    `test_for_agent_builds_the_circuit_at_a_changed_machine_file_volume` for
    the volume and `test_a_profile_stating_its_startup_flow_opens_the_run_at_that_flow`
    for the flow, both below (`PL-H8QP`).
    """

    machine = load_reference_circle_system_parameters()
    circuit = AgentUptakeSystem.for_agent("sevoflurane").circuit

    assert circuit.circuit_volume_l == machine.circuit_volume_l
    assert circuit.fresh_gas_flow_l_min == machine.default_fresh_gas_flow_l_min
    assert circuit.time_constant_s == pytest.approx(90.0)


# --- A profile that states no startup flow (PL-QW19) ---------------------------

# No surveyed machine publishes a startup fresh gas flow, so a machine profile
# may leave `default_fresh_gas_flow_l_min` out and the run supplies its opening
# flow. `for_agent()` reads one hardcoded profile until `PL-2FZ9`, so these
# tests hand it another the way `tests/integration/test_controller.py` hands it
# an edited agent: by replacing the loader it calls. Each profile is the shipped
# file with one thing changed, parsed as the loader parses it.


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
    flow no manufacturer publishes. The volume is moved off the shipped 6.0 L
    so that the run provably came from this profile: the shipped one states
    the same 4.0 L/min as the fallback, so a flow alone could not tell them
    apart. The circuit time constant is asserted beside the flow because it is
    the quantity a learner reads off the early rise: 8.0 L at 4.0 L/min is
    120 s.
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
    """The fallback fills a silence and never replaces a stated flow.

    Needed because the shipped profile states the same 4.0 L/min as the
    fallback, so a `for_agent()` that always took the fallback would pass
    every other test in this file.
    """

    payload = _shipped_machine_payload()
    payload["default_fresh_gas_flow_l_min"] = 2.0

    circuit = _run_built_from(monkeypatch, payload).circuit

    assert circuit.fresh_gas_flow_l_min == 2.0
    assert circuit.time_constant_s == pytest.approx(180.0)


def test_a_silent_profile_whose_range_excludes_the_teaching_default_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The fallback is held to the machine's declared range, not fitted into it.

    Refused by `BreathingCircuit` in the words it uses for a stated flow
    outside the range, rather than opened at a flow the machine cannot set or
    clamped to one nobody chose.
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

# The shipped profile's volume equals `BreathingCircuit`'s field default, so no
# run built from it shows whether `for_agent()` read the volume at all. A run
# built from a profile stating another one does, handed over as the profiles
# above are.


def test_for_agent_builds_the_circuit_at_a_changed_machine_file_volume(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A `for_agent()` that stopped passing the profile's volume fails here.

    It would build the run at the 6.0 L field default instead, and every
    provenance row pointing at `data/machines/reference_circle_system.json`
    would quietly become a claim about a file the model no longer consults.
    3.3 L at the shipped 4.0 L/min is 49.5 s.
    """

    payload = _shipped_machine_payload()
    payload["circuit_volume_l"] = 3.3

    circuit = _run_built_from(monkeypatch, payload).circuit

    assert circuit.circuit_volume_l == 3.3
    assert circuit.time_constant_s == pytest.approx(49.5)


# --- The machine's deliverable flow range (PL-8PS6) --------------------------

# The circuit is the one object holding both claims on the fresh gas flow: the
# model's envelope in `core/supported_ranges.py` and the range a machine
# profile declares. The tests below cover the machine half; the split itself -
# that neither claim can be mistaken for the other - is pinned in
# `tests/unit/test_supported_ranges.py`, beside the envelope it must not widen.


def test_a_declared_range_includes_both_of_its_own_endpoints() -> None:
    """Closed, like every interval `core/supported_ranges.py` declares.

    A machine's minimum-flow floor is a setting the machine reaches, not the
    first one it refuses, and the same for the top of its flowmeter.
    """

    circuit = BreathingCircuit(
        fresh_gas_flow_l_min=FreshGasFlow(1.0),
        deliverable_fresh_gas_flow_range=DeliverableFreshGasFlowRange(
            minimum_l_min=0.5, maximum_l_min=8.0
        ),
    )

    for flow in (0.5, 4.0, 8.0):
        circuit.set_fresh_gas_flow(FreshGasFlow(flow))
        assert circuit.fresh_gas_flow_l_min == flow


def test_construction_is_refused_at_a_flow_the_machine_cannot_deliver() -> None:
    """The constructor is a third way in, so it carries the guard too.

    `BreathingCircuit(fresh_gas_flow_l_min=...)` reaches the field without
    passing `set_fresh_gas_flow`, exactly as `PL-0MLQ` found for the model's
    own envelope.
    """

    with pytest.raises(SimulationConfigurationError, match="machine can deliver"):
        BreathingCircuit(
            fresh_gas_flow_l_min=FreshGasFlow(0.2),
            deliverable_fresh_gas_flow_range=DeliverableFreshGasFlowRange(
                minimum_l_min=0.5, maximum_l_min=8.0
            ),
        )


def test_a_profile_declaring_no_range_leaves_the_model_envelope_alone() -> None:
    """`None` is an absence of claim, and it is what the shipped profile records.

    No operator's manual or manufacturer specification giving a deliverable
    range was reachable for any surveyed machine, so the field is `null` in
    `data/machines/reference_circle_system.json` and the envelope is the only
    bound - which is the behavior that shipped before the field existed.
    """

    circuit = BreathingCircuit()

    assert circuit.deliverable_fresh_gas_flow_range is None

    circuit.set_fresh_gas_flow(FreshGasFlow(MAXIMUM_FRESH_GAS_FLOW_L_MIN))

    assert circuit.fresh_gas_flow_l_min == MAXIMUM_FRESH_GAS_FLOW_L_MIN

    with pytest.raises(SimulationConfigurationError, match="compartment model"):
        circuit.set_fresh_gas_flow(FreshGasFlow(MAXIMUM_FRESH_GAS_FLOW_L_MIN + 1.0))


def test_a_machine_that_overlaps_the_envelope_nowhere_is_refused_when_built() -> None:
    """Said once, rather than discovered one refused setting at a time.

    Every flow such a profile can deliver is outside the model's envelope and
    every flow the model supports is outside the profile's range, so each
    individual refusal would be correct while none of them said that the pair
    is what cannot be simulated.
    """

    with pytest.raises(SimulationConfigurationError) as raised:
        BreathingCircuit(
            deliverable_fresh_gas_flow_range=DeliverableFreshGasFlowRange(
                minimum_l_min=MAXIMUM_FRESH_GAS_FLOW_L_MIN + 2.0,
                maximum_l_min=MAXIMUM_FRESH_GAS_FLOW_L_MIN + 5.0,
            )
        )

    message = str(raised.value)

    assert "no fresh gas flow the model is claimed over" in message
    assert "12.0 to 15.0 L/min" in message
    assert f"{MINIMUM_FRESH_GAS_FLOW_L_MIN} to {MAXIMUM_FRESH_GAS_FLOW_L_MIN} L/min" in message


def test_a_range_touching_the_envelope_at_one_point_is_built() -> None:
    """The overlap test is on the closed intervals, so one shared flow is enough."""

    circuit = BreathingCircuit(
        fresh_gas_flow_l_min=FreshGasFlow(MAXIMUM_FRESH_GAS_FLOW_L_MIN),
        deliverable_fresh_gas_flow_range=DeliverableFreshGasFlowRange(
            minimum_l_min=MAXIMUM_FRESH_GAS_FLOW_L_MIN,
            maximum_l_min=MAXIMUM_FRESH_GAS_FLOW_L_MIN + 5.0,
        ),
    )

    assert circuit.fresh_gas_flow_l_min == MAXIMUM_FRESH_GAS_FLOW_L_MIN


def test_a_range_whose_minimum_is_above_its_maximum_is_refused() -> None:
    """An inverted range refuses every setting while looking like a capability."""

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
    """The one machine property zero is meaningful for: a true off position.

    `_validate_nonnegative_finite` exists in `core/parameters.py` for this
    case alone, and a guard written as "positive and finite" would make a
    machine whose common gas outlet turns off unrepresentable.
    """

    circuit = BreathingCircuit(
        deliverable_fresh_gas_flow_range=DeliverableFreshGasFlowRange(
            minimum_l_min=0.0, maximum_l_min=8.0
        )
    )

    circuit.set_fresh_gas_flow(FreshGasFlow(0.0))

    assert circuit.fresh_gas_flow_l_min == 0.0


def test_for_agent_passes_the_machine_file_s_declared_range_to_the_circuit() -> None:
    """The route, not the value: the shipped profile's range is `None` today.

    What the assertion protects is that a profile which does declare a range
    reaches the circuit, rather than being parsed and dropped at the seam.
    """

    machine = load_reference_circle_system_parameters()
    circuit = AgentUptakeSystem.for_agent("sevoflurane").circuit

    assert machine.deliverable_fresh_gas_flow_range is None
    assert circuit.deliverable_fresh_gas_flow_range is machine.deliverable_fresh_gas_flow_range


# --- The one statement of the intersection (PL-7CRY) --------------------------

# `accepted_fresh_gas_flow_range_l_min` is what the interface's fresh gas flow
# control is bounded by, so it is held here to be exactly the flows the circuit
# accepts: both of its ends taken, and the flow just past each refused, by the
# model's guard or the machine's. "Just past" is far below any step a control
# offers, so the ends are pinned as the closed interval and nothing wider.

_JUST_PAST_AN_END_L_MIN = 1e-6


@pytest.mark.parametrize(
    ("declared", "accepted"),
    (
        # No claim: the model's envelope is the only bound.
        (None, (MINIMUM_FRESH_GAS_FLOW_L_MIN, MAXIMUM_FRESH_GAS_FLOW_L_MIN)),
        # Narrower at both ends: the machine's range.
        ((0.5, 8.0), (0.5, 8.0)),
        # Wider at the top: the machine's floor and the model's ceiling.
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

    The property is read by a control the reader drags, so an end the
    circuit refused would be a setting offered and then turned down, and a
    range narrower than the circuit's would hide flows the run supports.
    """

    lowest, highest = accepted
    circuit = BreathingCircuit(
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
    inspired fraction does not change. The floor itself is accepted, and so is a
    step of 1 s, longer than the run's 0.1 s ceiling, which does not apply to a
    compartment stepped alone. The expected floor, 0.001 s, is written out here
    rather than read from `MINIMUM_SIMULATION_STEP_S`.
    """

    circuit = BreathingCircuit(
        circuit_volume_l=6.0,
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
