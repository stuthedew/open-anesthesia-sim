"""Unit tests for the run's recorded history and what the chart reads from it.

`RunHistory` stores a run by series - one substance's values for one
quantity - rather than by instant, which is what lets a frame read a few
hundred aggregates instead of walking the visible window once per trace.
The properties here are the ones that storage shape puts at risk: that each
series still holds *its own* values, that a sample read back is the sample
recorded, that a run refuses samples of substances it is not recording, and
that the wash-in domain's stretches are the ones `app/wash_in.py` specifies.

A swapped pairing between a quantity and the field it reads would be a
presentation-correctness failure of the kind
`tests/unit/test_simulation_view.py`'s
`test_chart_traces_stay_bound_to_their_own_compartment` guards at the other
end of the same path: a curve labelled for one compartment carrying
another's values.
"""

import math

import pytest

from anesthesia_sim.app.controller import (
    COMPARTMENT_QUANTITIES,
    RecordedQuantity,
    RecordedSeries,
    RunHistory,
    SimulationHistorySample,
)
from anesthesia_sim.app.wash_in import WASH_IN_DENOMINATOR_FLOOR_FRACTION, WASH_IN_EQUILIBRIUM_RATIO

_AGENT = "sevoflurane"

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


def _sample(
    elapsed_s: float, scale: float = 1.0, substance_id: str = _AGENT
) -> SimulationHistorySample:
    return SimulationHistorySample(
        elapsed_s=elapsed_s,
        substances={
            substance_id: {quantity: value * scale for quantity, value in _DISTINCT.items()}
        },
    )


def _pair(alveolar: float, circuit: float, substance_id: str = _AGENT) -> SimulationHistorySample:
    """A sample carrying only the two fractions the wash-in ratio is formed from."""

    return SimulationHistorySample(
        elapsed_s=0.0,
        substances={
            substance_id: {
                RecordedQuantity.CIRCUIT: circuit,
                RecordedQuantity.ALVEOLAR: alveolar,
                RecordedQuantity.MIXED_VENOUS: 0.0,
                RecordedQuantity.VESSEL_RICH: 0.0,
                RecordedQuantity.MUSCLE: 0.0,
                RecordedQuantity.FAT: 0.0,
            }
        },
    )


def test_each_series_holds_its_own_value() -> None:
    """The recorder's pairing, audited value by value."""

    history = RunHistory.of([_sample(0.0)])

    for quantity, expected in _DISTINCT.items():
        series = RecordedSeries(_AGENT, quantity)
        assert history.value(series, 0) == pytest.approx(expected), quantity


def test_a_run_records_the_substances_it_was_built_for() -> None:
    history = RunHistory.of([_sample(0.0)])

    assert history.substances == (_AGENT,)


def test_two_substances_recorded_together_keep_their_own_values() -> None:
    """The shape the record exists for, exercised before a second agent needs it.

    One substance is recorded today, so nothing else here can tell a store
    that keys by substance from one that keys by compartment alone and
    happens to be asked for one substance. Two entries, each with distinct
    values, is what separates them: a store that dropped the substance key
    would return the second's values under the first's name.
    """

    history = RunHistory.of(
        [
            SimulationHistorySample(
                elapsed_s=0.0,
                substances={
                    _AGENT: dict(_DISTINCT),
                    "nitrous-oxide": {
                        quantity: value * 3.0 for quantity, value in _DISTINCT.items()
                    },
                },
            )
        ]
    )

    assert history.substances == (_AGENT, "nitrous-oxide")

    for quantity, expected in _DISTINCT.items():
        assert history.value(RecordedSeries(_AGENT, quantity), 0) == pytest.approx(expected)
        assert history.value(RecordedSeries("nitrous-oxide", quantity), 0) == pytest.approx(
            expected * 3.0
        )


def test_a_sample_of_another_substance_is_refused_rather_than_recorded() -> None:
    """A series shorter than the ones beside it draws every value at the wrong instant."""

    history = RunHistory.of([_sample(0.0)])

    with pytest.raises(ValueError, match="sevoflurane"):
        history.record(_sample(0.1, substance_id="desflurane"))

    assert len(history) == 1


def test_a_sample_must_carry_every_compartment() -> None:
    """A missing compartment is refused where it is written, not where it is read."""

    with pytest.raises(ValueError, match="must record exactly"):
        SimulationHistorySample(
            elapsed_s=0.0,
            substances={_AGENT: {quantity: 0.0 for quantity in COMPARTMENT_QUANTITIES[:-1]}},
        )


def test_a_sample_may_not_carry_a_derived_quantity() -> None:
    """`WASH_IN_RATIO` is formed by the recorder; supplying one asserts it was measured."""

    with pytest.raises(ValueError, match="must record exactly"):
        SimulationHistorySample(
            elapsed_s=0.0, substances={_AGENT: {quantity: 0.0 for quantity in RecordedQuantity}}
        )


def test_a_recorded_sample_cannot_be_changed_underneath_its_holder() -> None:
    """Two levels of mapping, both read-only, so a kept sample stays the sample recorded."""

    values = {quantity: 0.01 for quantity in COMPARTMENT_QUANTITIES}
    sample = SimulationHistorySample(elapsed_s=0.0, substances={_AGENT: values})

    values[RecordedQuantity.CIRCUIT] = 0.99

    assert sample.substances[_AGENT][RecordedQuantity.CIRCUIT] == pytest.approx(0.01)

    with pytest.raises(TypeError):
        sample.substances[_AGENT][RecordedQuantity.CIRCUIT] = 0.99  # type: ignore[index]


def test_a_run_of_no_samples_cannot_name_its_own_substances() -> None:
    with pytest.raises(ValueError, match="no samples"):
        RunHistory.of([])


def test_a_substance_may_be_recorded_once_only() -> None:
    with pytest.raises(ValueError, match="once only"):
        RunHistory([_AGENT, _AGENT])


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
    ratios = history.aggregates(RecordedSeries(_AGENT, RecordedQuantity.WASH_IN_RATIO))

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

    assert history.wash_in_stretches(_AGENT, 0, 5) == [(1, 3), (4, 5)]


def test_a_wash_in_stretch_is_clipped_to_the_window_asked_for() -> None:
    history = RunHistory.of([_pair(alveolar=0.004, circuit=0.02) for _ in range(20)])

    assert history.wash_in_stretches(_AGENT, 0, 20) == [(0, 20)]
    assert history.wash_in_stretches(_AGENT, 5, 12) == [(5, 12)]
    assert history.wash_in_stretches(_AGENT, 20, 20) == []


def test_a_sample_exactly_at_equilibrium_is_inside_the_domain() -> None:
    """`WASH_IN_EQUILIBRIUM_RATIO` is where uptake stops, not where it is excluded."""

    history = RunHistory.of([_pair(alveolar=0.02, circuit=0.02)])

    assert history.aggregates(RecordedSeries(_AGENT, RecordedQuantity.WASH_IN_RATIO)).value(
        0
    ) == pytest.approx(WASH_IN_EQUILIBRIUM_RATIO)
    assert history.wash_in_stretches(_AGENT, 0, 1) == [(0, 1)]
