"""Tests for `CompartmentAgentAmounts`, the snapshot's record of each compartment's agent.

`tests/reference/test_compartment_amounts_against_oracles.py` checks each amount against
oracles independent of `core/`. This module checks the record itself: which
records it refuses, that it cannot be changed once built, and that its six
amounts add up to the snapshot's `stored_agent_l` exactly, so that the share
bar divides the parts by their own total (`PL-KFTM`).
"""

from collections.abc import Callable
from math import inf, nan

import pytest

from anesthesia_sim.app.controller import CompartmentAgentAmounts, SimulationController
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow

# Six distinct amounts, so that a record which returned a neighbour's amount
# would fail every lookup test below.
DISTINCT_AMOUNTS_L = {
    RecordedQuantity.CIRCUIT: 0.21,
    RecordedQuantity.ALVEOLAR: 0.07,
    RecordedQuantity.MIXED_VENOUS: 0.013,
    RecordedQuantity.VESSEL_RICH: 0.042,
    RecordedQuantity.MUSCLE: 0.0031,
    RecordedQuantity.FAT: 0.00057,
}


def test_each_compartment_returns_its_own_amount() -> None:
    record = CompartmentAgentAmounts(DISTINCT_AMOUNTS_L)

    assert [record.of(quantity) for quantity in COMPARTMENT_QUANTITIES] == [
        0.21,
        0.07,
        0.013,
        0.042,
        0.0031,
        0.00057,
    ]


def test_the_wash_in_ratio_is_refused_because_it_holds_no_agent() -> None:
    record = CompartmentAgentAmounts(DISTINCT_AMOUNTS_L)

    with pytest.raises(SimulationConfigurationError, match="wash_in_ratio is not a compartment"):
        record.of(RecordedQuantity.WASH_IN_RATIO)


@pytest.mark.parametrize(
    "keys",
    [
        COMPARTMENT_QUANTITIES[:-1],
        (*COMPARTMENT_QUANTITIES, RecordedQuantity.WASH_IN_RATIO),
        (COMPARTMENT_QUANTITIES[1], COMPARTMENT_QUANTITIES[0], *COMPARTMENT_QUANTITIES[2:]),
        (),
    ],
    ids=["one missing", "a seventh key", "two swapped", "empty"],
)
def test_a_record_without_exactly_the_six_compartments_in_order_is_refused(
    keys: tuple[RecordedQuantity, ...],
) -> None:
    with pytest.raises(SimulationConfigurationError, match="must hold circuit, alveolar"):
        CompartmentAgentAmounts(dict.fromkeys(keys, 0.0))


@pytest.mark.parametrize("amount_l", [-1e-12, nan, inf])
def test_a_negative_or_non_finite_amount_is_refused(amount_l: float) -> None:
    amounts = dict(DISTINCT_AMOUNTS_L)
    amounts[RecordedQuantity.MUSCLE] = amount_l

    with pytest.raises(SimulationConfigurationError, match="muscle agent amount in litres"):
        CompartmentAgentAmounts(amounts)


def test_an_amount_that_is_not_a_number_is_refused() -> None:
    amounts: dict[RecordedQuantity, object] = dict(DISTINCT_AMOUNTS_L)
    amounts[RecordedQuantity.FAT] = "0.5"

    with pytest.raises(TypeError, match="fat agent amount in litres"):
        CompartmentAgentAmounts(amounts)  # type: ignore[arg-type]


def test_an_empty_compartment_is_accepted() -> None:
    """Zero is the amount every compartment holds before the vaporizer opens."""

    record = CompartmentAgentAmounts(dict.fromkeys(COMPARTMENT_QUANTITIES, 0.0))

    assert all(record.of(quantity) == 0.0 for quantity in COMPARTMENT_QUANTITIES)


def test_a_later_edit_to_the_mapping_passed_in_changes_no_amount() -> None:
    amounts = dict(DISTINCT_AMOUNTS_L)
    record = CompartmentAgentAmounts(amounts)
    amounts[RecordedQuantity.FAT] = 99.0

    assert record.of(RecordedQuantity.FAT) == 0.00057
    with pytest.raises(TypeError):
        record.amounts_l[RecordedQuantity.FAT] = 99.0  # type: ignore[index]


def _snapshots_of_a_changing_run(agent_id: str) -> list[tuple[CompartmentAgentAmounts, float]]:
    """Return the record and the stored total at five instants of a run whose settings change.

    The run opens the vaporizer, raises the flow, stops ventilation, lowers the
    cardiac output and closes the vaporizer, so the instants cover wash-in,
    a circuit that fills without the patient, and wash-out.
    """

    controller = SimulationController(agent_id=agent_id)
    changes: tuple[Callable[[], None], ...] = (
        lambda: None,
        lambda: controller.set_fresh_gas_flow(FreshGasFlow(8.0)),
        lambda: controller.set_alveolar_ventilation(AlveolarVentilation(0.0)),
        lambda: controller.set_cardiac_output(CardiacOutput(2.5)),
        lambda: controller.set_delivered_concentration_percent(Percent(0.0)),
    )
    observed: list[tuple[CompartmentAgentAmounts, float]] = []
    controller.start()

    for change in changes:
        change()
        for _ in range(1200):
            controller.advance(SimulationStep(0.1))
        snapshot = controller.snapshot()
        observed.append((snapshot.compartment_agent_amounts, snapshot.stored_agent_l))

    return observed


@pytest.mark.parametrize("agent_id", ["sevoflurane", "isoflurane", "desflurane"])
def test_the_six_amounts_add_up_to_the_stored_total_exactly(agent_id: str) -> None:
    """The share bar's denominator is the sum of its own parts, to the last bit.

    `core/` sums the circuit and the alveoli, then the patient: the three
    tissue groups in order, then venous blood
    (`AgentUptakeSystem.total_stored_agent_l`). Adding the record's amounts in
    that order must give the snapshot's `stored_agent_l` with no rounding
    difference at all. A record whose amounts came from anywhere else, or a
    total that summed something else, would differ.
    """

    for record, stored_agent_l in _snapshots_of_a_changing_run(agent_id):
        patient_l = (
            record.of(RecordedQuantity.VESSEL_RICH)
            + record.of(RecordedQuantity.MUSCLE)
            + record.of(RecordedQuantity.FAT)
            + record.of(RecordedQuantity.MIXED_VENOUS)
        )
        summed_l = record.of(RecordedQuantity.CIRCUIT) + record.of(RecordedQuantity.ALVEOLAR)
        summed_l += patient_l

        assert stored_agent_l > 0.0
        assert summed_l == stored_agent_l
