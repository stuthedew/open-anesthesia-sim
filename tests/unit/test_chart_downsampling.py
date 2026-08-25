"""Unit tests for chart sample selection.

The properties under test are presentation-correctness properties, not
cosmetic ones: a selection that drops the newest sample makes the graph
disagree with the numeric readouts, and one that drops an extreme shows a
curve the simulation never produced.
"""

import pytest

from anesthesia_sim.app.chart_downsampling import first_index_at_or_after, select_envelope_indices


def _elapsed_s(time_s: float) -> float:
    return time_s


def test_first_index_at_or_after_finds_window_start() -> None:
    times_s = [0.0, 0.1, 0.2, 0.3, 0.4]

    assert first_index_at_or_after(times_s, 0.0, _elapsed_s) == 0
    assert first_index_at_or_after(times_s, 0.2, _elapsed_s) == 2
    assert first_index_at_or_after(times_s, 0.25, _elapsed_s) == 3


def test_first_index_at_or_after_handles_window_outside_the_samples() -> None:
    times_s = [1.0, 2.0, 3.0]

    assert first_index_at_or_after(times_s, 0.0, _elapsed_s) == 0
    assert first_index_at_or_after(times_s, 99.0, _elapsed_s) == 3
    assert first_index_at_or_after([], 5.0, _elapsed_s) == 0


def test_select_envelope_indices_returns_everything_when_it_already_fits() -> None:
    values = [0.0, 1.0, 2.0, 3.0]

    assert select_envelope_indices(values, max_points=4) == [0, 1, 2, 3]
    assert select_envelope_indices(values, max_points=10) == [0, 1, 2, 3]


def test_select_envelope_indices_handles_empty_and_single_sample() -> None:
    assert select_envelope_indices([], max_points=8) == []
    assert select_envelope_indices([1.5], max_points=8) == [0]


def test_select_envelope_indices_rejects_a_budget_with_no_room_to_bucket() -> None:
    with pytest.raises(ValueError, match="at least 4"):
        select_envelope_indices([0.0, 1.0, 2.0, 3.0, 4.0], max_points=3)


def test_select_envelope_indices_respects_the_budget() -> None:
    values = [float(index % 7) for index in range(3000)]

    for max_points in (4, 5, 10, 51, 300):
        indices = select_envelope_indices(values, max_points=max_points)

        assert len(indices) <= max_points
        assert indices == sorted(set(indices))
        assert all(0 <= index < len(values) for index in indices)


def test_select_envelope_indices_always_keeps_the_newest_sample() -> None:
    """The right-hand end of a trace must equal the numeric readout."""

    values = [float(index) for index in range(1000)]

    for max_points in (4, 9, 64, 300):
        indices = select_envelope_indices(values, max_points=max_points)

        assert indices[0] == 0
        assert indices[-1] == len(values) - 1


def test_select_envelope_indices_keeps_a_transient_spike() -> None:
    """A brief excursion must survive decimation at any reduction ratio."""

    values = [1.0] * 1000
    values[437] = 9.0
    values[812] = -4.0

    indices = select_envelope_indices(values, max_points=8)

    assert 437 in indices
    assert 812 in indices


def test_select_envelope_indices_spans_the_full_value_range() -> None:
    values = [float((index * 37) % 101) for index in range(2000)]

    indices = select_envelope_indices(values, max_points=20)
    selected = [values[index] for index in indices]

    assert min(selected) == min(values)
    assert max(selected) == max(values)


def test_select_envelope_indices_matches_a_hand_computed_case() -> None:
    # Ten samples, budget 6 -> two buckets of five: indices 0-4 and 5-9.
    # Bucket one: minimum 1.0 at index 1, maximum 8.0 at index 3.
    # Bucket two: minimum 0.0 at index 7, maximum 5.0 at index 5.
    # Endpoints 0 and 9 are always kept.
    values = [4.0, 1.0, 2.0, 8.0, 3.0, 5.0, 2.0, 0.0, 1.0, 3.0]

    assert select_envelope_indices(values, max_points=6) == [0, 1, 3, 5, 7, 9]


def test_select_envelope_indices_is_deterministic() -> None:
    values = [float((index * 17) % 53) for index in range(5000)]

    first = select_envelope_indices(values, max_points=128)
    second = select_envelope_indices(values, max_points=128)

    assert first == second


def test_select_envelope_indices_handles_a_flat_trace() -> None:
    values = [2.5] * 500

    indices = select_envelope_indices(values, max_points=10)

    assert indices[0] == 0
    assert indices[-1] == 499
    assert all(values[index] == 2.5 for index in indices)
