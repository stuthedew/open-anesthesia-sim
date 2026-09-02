from math import exp, inf

import pytest

from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.supported_ranges import MAXIMUM_FRESH_GAS_FLOW_L_MIN


def test_rejects_agent_amount_above_circuit_capacity() -> None:
    circuit = BreathingCircuit()

    with pytest.raises(
        SimulationConfigurationError, match="^agent_amount_l exceeds circuit capacity$"
    ):
        circuit.set_agent_amount(6.1)


def test_one_time_constant_reaches_expected_fraction() -> None:
    circuit = BreathingCircuit(
        circuit_volume_l=6.0, fresh_gas_flow_l_min=6.0, delivered_concentration_fraction=1.0
    )

    circuit.advance(circuit.time_constant_s)

    assert circuit.circuit_concentration_fraction == pytest.approx(1.0 - exp(-1.0))


def test_zero_fresh_gas_flow_preserves_concentration() -> None:
    circuit = BreathingCircuit(
        fresh_gas_flow_l_min=0.0,
        delivered_concentration_fraction=1.0,
        circuit_concentration_fraction=0.25,
    )

    circuit.advance(60.0)

    assert circuit.time_constant_s == inf
    assert circuit.circuit_concentration_fraction == 0.25


def test_zero_delivered_concentration_washes_out_circuit() -> None:
    circuit = BreathingCircuit(
        circuit_volume_l=6.0,
        fresh_gas_flow_l_min=6.0,
        delivered_concentration_fraction=0.0,
        circuit_concentration_fraction=1.0,
    )

    circuit.advance(circuit.time_constant_s)

    assert circuit.circuit_concentration_fraction == pytest.approx(exp(-1.0))


def test_exact_update_is_independent_of_step_size() -> None:
    """One 60 s step and six hundred 0.1 s steps reach the same fraction.

    Both circuits name their dial rather than taking the default, and the
    first assertion is what makes the second mean something: with the
    vaporizer off this comparison is satisfied by two circuits that both
    stayed at zero, which is agreement about nothing.
    """

    one_step = BreathingCircuit(delivered_concentration_fraction=1.0)
    many_steps = BreathingCircuit(delivered_concentration_fraction=1.0)

    one_step.advance(60.0)

    for _ in range(600):
        many_steps.advance(0.1)

    assert one_step.circuit_concentration_fraction > 0.0
    assert many_steps.circuit_concentration_fraction == pytest.approx(
        one_step.circuit_concentration_fraction, rel=1e-12
    )


@pytest.mark.parametrize("circuit_volume_l", [0.0, -1.0, float("inf")])
def test_rejects_invalid_circuit_volume(circuit_volume_l: float) -> None:
    with pytest.raises(SimulationConfigurationError):
        BreathingCircuit(circuit_volume_l=circuit_volume_l)


@pytest.mark.parametrize("fresh_gas_flow_l_min", [-1.0, float("nan")])
def test_rejects_invalid_fresh_gas_flow(fresh_gas_flow_l_min: float) -> None:
    with pytest.raises(SimulationConfigurationError):
        BreathingCircuit(fresh_gas_flow_l_min=fresh_gas_flow_l_min)


@pytest.mark.parametrize("delivered_concentration_fraction", [-0.01, 1.01, float("nan")])
def test_rejects_invalid_delivered_concentration(delivered_concentration_fraction: float) -> None:
    with pytest.raises(SimulationConfigurationError):
        BreathingCircuit(delivered_concentration_fraction=(delivered_concentration_fraction))


def test_rejects_delivered_concentration_above_the_vaporizer_maximum() -> None:
    """Regression (PL-015): the vaporizer limit is enforced in the core.

    Before the fix the limit lived only in the controller, as a silent
    clamp, and in the UI slider bounds.
    """

    circuit = BreathingCircuit(
        delivered_concentration_fraction=0.02, max_delivered_concentration_fraction=0.05
    )

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        circuit.set_delivered_concentration(0.50)

    assert circuit.delivered_concentration_fraction == 0.02


def test_rejects_construction_above_the_vaporizer_maximum() -> None:
    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        BreathingCircuit(
            delivered_concentration_fraction=0.08, max_delivered_concentration_fraction=0.05
        )


def test_accepts_delivered_concentration_exactly_at_the_vaporizer_maximum() -> None:
    circuit = BreathingCircuit(
        delivered_concentration_fraction=0.02, max_delivered_concentration_fraction=0.05
    )
    circuit.set_delivered_concentration(0.05)

    assert circuit.delivered_concentration_fraction == 0.05


def test_accepts_a_delivered_concentration_of_zero() -> None:
    """The vaporizer off is always a valid dial position: it is washout."""

    circuit = BreathingCircuit(
        delivered_concentration_fraction=0.02, max_delivered_concentration_fraction=0.05
    )
    circuit.set_delivered_concentration(0.0)

    assert circuit.delivered_concentration_fraction == 0.0


@pytest.mark.parametrize(
    "max_delivered_concentration_fraction", [0.0, -0.01, 1.01, float("nan"), float("inf")]
)
def test_rejects_invalid_vaporizer_maximum(max_delivered_concentration_fraction: float) -> None:
    with pytest.raises(SimulationConfigurationError):
        BreathingCircuit(
            delivered_concentration_fraction=0.0,
            max_delivered_concentration_fraction=(max_delivered_concentration_fraction),
        )


def test_accepts_fresh_gas_flow_at_both_ends_of_the_supported_range() -> None:
    """Zero is the vaporizer running into a closed system; the maximum is the
    corner of the settings envelope every reference gate measures at."""

    for fresh_gas_flow_l_min in (0.0, MAXIMUM_FRESH_GAS_FLOW_L_MIN):
        circuit = BreathingCircuit(fresh_gas_flow_l_min=fresh_gas_flow_l_min)

        assert circuit.fresh_gas_flow_l_min == fresh_gas_flow_l_min

        circuit.set_fresh_gas_flow(fresh_gas_flow_l_min)

        assert circuit.fresh_gas_flow_l_min == fresh_gas_flow_l_min


def test_rejects_fresh_gas_flow_above_the_supported_range() -> None:
    """Regression (PL-0MLQ): the range was documented but never enforced.

    A bare circuit is an exact exponential at any flow, so this guard is not
    about the circuit's own arithmetic — it is the model's declared input
    domain, and the circuit is where every path that can change the flow
    passes through, the same argument the vaporizer maximum above rests on.
    """

    circuit = BreathingCircuit(fresh_gas_flow_l_min=4.0)

    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        circuit.set_fresh_gas_flow(500.0)

    assert circuit.fresh_gas_flow_l_min == 4.0


def test_rejects_construction_with_fresh_gas_flow_above_the_supported_range() -> None:
    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        BreathingCircuit(fresh_gas_flow_l_min=500.0)


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
    assert circuit.circuit_concentration_fraction == pytest.approx(0.048288200 / 3.0)

    circuit.set_circuit_volume(12.0)

    assert circuit.agent_amount_l == pytest.approx(0.048288200)
    assert circuit.circuit_concentration_fraction == pytest.approx(0.048288200 / 12.0)


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


def test_a_circuit_volume_exactly_equal_to_its_agent_is_accepted() -> None:
    """The capacity bound is closed, matching `set_agent_amount`'s own."""

    circuit = BreathingCircuit(circuit_volume_l=6.0)
    circuit.set_agent_amount(2.0)

    circuit.set_circuit_volume(2.0)

    assert circuit.circuit_concentration_fraction == pytest.approx(1.0)
    assert circuit.agent_amount_l == pytest.approx(2.0)


def test_a_bare_circuit_starts_with_the_vaporizer_off() -> None:
    """Regression (PL-019): the class holds no agent-shaped dial position.

    `delivered_concentration_fraction` defaulted to 0.08 - sevoflurane's
    vaporizer maximum - on a class that knows nothing about agents. Two
    consequences, and the second is the one that made it worth removing:
    declaring any lower device limit raised at construction, and the
    message reported an "8% requested" the caller had never written.

    Zero is the only dial position every vaporizer of every agent has, so
    it is the only one this class can hold without knowing which agent is
    in use. `AgentUptakeSystem.for_agent()` sets the real starting dial.
    """

    circuit = BreathingCircuit(max_delivered_concentration_fraction=0.05)

    assert circuit.delivered_concentration_fraction == 0.0
    assert circuit.max_delivered_concentration_fraction == 0.05

    circuit.advance(60.0)

    assert circuit.circuit_concentration_fraction == 0.0
