"""Unit tests for the run's recorded history and what the chart reads from it.

`RunHistory` stores a run by quantity rather than by instant, which is what
lets a frame read a few hundred aggregates instead of walking the visible
window once per trace. The properties here are the ones that storage shape
puts at risk: that each quantity still holds *its own* values, that a sample
read back is the sample recorded, and that the wash-in domain's stretches
are the ones `app/wash_in.py` specifies.

A swapped pairing between a quantity and the field it reads would be a
presentation-correctness failure of the kind
`tests/unit/test_simulation_view.py`'s
`test_chart_traces_stay_bound_to_their_own_compartment` guards at the other
end of the same path: a curve labelled for one compartment carrying
another's values.
"""

import math

import pytest

from anesthesia_sim.app.controller import RecordedQuantity, RunHistory, SimulationHistorySample
from anesthesia_sim.app.wash_in import WASH_IN_DENOMINATOR_FLOOR_FRACTION, WASH_IN_EQUILIBRIUM_RATIO

# One distinct value per compartment, so a pairing that reads the wrong
# field shows up as a wrong number rather than as a coincidence.
_DISTINCT = {
    RecordedQuantity.CIRCUIT: 0.061,
    RecordedQuantity.ALVEOLAR: 0.052,
    RecordedQuantity.MIXED_VENOUS: 0.043,
    RecordedQuantity.VESSEL_RICH: 0.034,
    RecordedQuantity.MUSCLE: 0.025,
    RecordedQuantity.FAT: 0.016,
}


def _sample(elapsed_s: float, scale: float = 1.0) -> SimulationHistorySample:
    return SimulationHistorySample(
        elapsed_s=elapsed_s,
        circuit_concentration_fraction=_DISTINCT[RecordedQuantity.CIRCUIT] * scale,
        alveolar_concentration_fraction=_DISTINCT[RecordedQuantity.ALVEOLAR] * scale,
        mixed_venous_concentration_fraction=_DISTINCT[RecordedQuantity.MIXED_VENOUS] * scale,
        vessel_rich_partial_pressure_fraction=_DISTINCT[RecordedQuantity.VESSEL_RICH] * scale,
        muscle_partial_pressure_fraction=_DISTINCT[RecordedQuantity.MUSCLE] * scale,
        fat_partial_pressure_fraction=_DISTINCT[RecordedQuantity.FAT] * scale,
    )


def _pair(alveolar: float, circuit: float) -> SimulationHistorySample:
    """A sample carrying only the two fractions the wash-in ratio is formed from."""

    return SimulationHistorySample(
        elapsed_s=0.0,
        circuit_concentration_fraction=circuit,
        alveolar_concentration_fraction=alveolar,
        mixed_venous_concentration_fraction=0.0,
        vessel_rich_partial_pressure_fraction=0.0,
        muscle_partial_pressure_fraction=0.0,
        fat_partial_pressure_fraction=0.0,
    )


def test_each_quantity_holds_its_own_field() -> None:
    """The recorder's pairing, audited value by value."""

    history = RunHistory.of([_sample(0.0)])

    for quantity, expected in _DISTINCT.items():
        assert history.value(quantity, 0) == pytest.approx(expected), quantity


def test_a_sample_reads_back_as_it_was_recorded() -> None:
    """Column storage must be a lossless rearrangement of the recorded rows."""

    recorded = [_sample(index * 0.1, scale=1.0 + index) for index in range(64)]
    history = RunHistory.of(recorded)

    assert len(history) == len(recorded)
    assert [history.sample(index) for index in range(len(recorded))] == recorded


def test_a_window_is_a_range_over_the_run_it_was_taken_from() -> None:
    recorded = [_sample(index * 0.1) for index in range(50)]
    history = RunHistory.of(recorded)

    window = history.window_from(2.0)

    assert window.run is history
    assert window.index_offset == 20
    assert window.stop_index == 50
    assert window.sample_count == 30
    assert window.samples == tuple(recorded[20:])


def test_a_window_past_the_end_of_the_run_is_empty() -> None:
    history = RunHistory.of([_sample(index * 0.1) for index in range(10)])

    window = history.window_from(99.0)

    assert window.sample_count == 0
    assert window.samples == ()


def test_a_growing_run_does_not_move_an_existing_windows_samples() -> None:
    """A window is a range, so what it names cannot change underneath a frame.

    This is what replaced copying the samples out (`PL-D9WD`): the hazard
    the copy guarded against was one trace drawn half from one instant and
    half from the next, and an append-only history bounded by an explicit
    stop closes it structurally instead.
    """

    history = RunHistory.of([_sample(index * 0.1) for index in range(30)])
    window = history.window_from(1.0)
    before = window.samples

    for index in range(30, 200):
        history.record(_sample(index * 0.1, scale=9.0))

    assert window.samples == before
    assert window.stop_index == 30


def test_the_wash_in_ratio_is_recorded_alongside_the_states_it_is_formed_from() -> None:
    below_floor = WASH_IN_DENOMINATOR_FLOOR_FRACTION / 2.0
    history = RunHistory.of(
        [_pair(alveolar=0.0, circuit=below_floor), _pair(alveolar=0.01, circuit=0.02)]
    )
    ratios = history.aggregates(RecordedQuantity.WASH_IN_RATIO)

    # Rule 1 of `app/wash_in.py`: no agent in the circuit, so no quotient.
    assert math.isnan(ratios.value(0))
    assert ratios.value(1) == pytest.approx(0.5)


def test_the_wash_in_stretches_are_the_domains_own() -> None:
    """A stretch runs while both of the domain's rules hold, and stops when either does not."""

    below_floor = WASH_IN_DENOMINATOR_FLOOR_FRACTION / 2.0
    history = RunHistory.of(
        [
            _pair(alveolar=0.0, circuit=below_floor),  # 0: no quotient at all
            _pair(alveolar=0.004, circuit=0.02),  # 1: inside
            _pair(alveolar=0.010, circuit=0.02),  # 2: inside
            _pair(alveolar=0.030, circuit=0.02),  # 3: past equilibrium
            _pair(alveolar=0.018, circuit=0.02),  # 4: inside again
        ]
    )

    assert history.wash_in_stretches(0, 5) == [(1, 3), (4, 5)]


def test_a_wash_in_stretch_is_clipped_to_the_window_asked_for() -> None:
    history = RunHistory.of([_pair(alveolar=0.004, circuit=0.02) for _ in range(20)])

    assert history.wash_in_stretches(0, 20) == [(0, 20)]
    assert history.wash_in_stretches(5, 12) == [(5, 12)]
    assert history.wash_in_stretches(20, 20) == []


def test_a_sample_exactly_at_equilibrium_is_inside_the_domain() -> None:
    """`WASH_IN_EQUILIBRIUM_RATIO` is where uptake stops, not where it is excluded."""

    history = RunHistory.of([_pair(alveolar=0.02, circuit=0.02)])

    assert history.aggregates(RecordedQuantity.WASH_IN_RATIO).value(0) == pytest.approx(
        WASH_IN_EQUILIBRIUM_RATIO
    )
    assert history.wash_in_stretches(0, 1) == [(0, 1)]
