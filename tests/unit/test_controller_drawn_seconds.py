"""Tests of how the controller chooses the seconds a chart window draws."""

from __future__ import annotations

import pytest

from anesthesia_sim.app.controller import (
    _ALVEOLAR_SERIES,
    _INSPIRED_SERIES,
    _axis_spacing_s,
    _with_extremes,
)
from anesthesia_sim.core.governing_equations import FRACTION_STATE_NAMES
from anesthesia_sim.core.supported_ranges import CaseInstant


def test_an_alveolar_series_longer_than_the_inspired_one_is_refused() -> None:
    """The F_A/F_I ratio is formed second by second, so two series of unequal length are refused.

    Each series should hold one fraction for every second of the window.
    Paired anyway, the ratio would divide one second's alveolar fraction by
    another second's inspired fraction, or silently stop early, and the
    chart would draw a peak or trough of the ratio at the wrong second
    (`PL-DN13`).
    """

    series = [[0.01, 0.02, 0.03, 0.02, 0.01] for _ in FRACTION_STATE_NAMES]
    series[_ALVEOLAR_SERIES] = [0.01, 0.02, 0.03, 0.02, 0.01, 0.02]

    with pytest.raises(ValueError):
        _with_extremes(0, 4, (CaseInstant(0), CaseInstant(4)), series, (True,) * 5)


def test_a_ventilation_series_shorter_than_the_fractions_is_refused() -> None:
    """Each second's ratio is formed with that second's ventilation, so a shorter series is refused.

    Paired anyway, a second would be judged by another second's ventilation,
    and a ratio reached at zero ventilation could be searched as a wash-in
    fraction (`PL-49D5`).
    """

    series = [[0.01, 0.02, 0.03, 0.02, 0.01] for _ in FRACTION_STATE_NAMES]

    with pytest.raises(ValueError):
        _with_extremes(0, 4, (CaseInstant(0), CaseInstant(4)), series, (True,) * 4)


def test_a_second_reached_at_zero_ventilation_is_left_out_of_the_ratio_search() -> None:
    """The first ventilated second after an apnoea is drawn where the ratio is lowest.

    Seconds 0 and 1 were reached at zero alveolar ventilation, so they have no
    ratio to draw (rule 3 of `app/wash_in.py`). The ratio at second 2, 0.3, is
    the lowest of the rest and below the column at second 6, 0.6. Compared
    with second 0's ratio of 0.2, it would not be below both ends, and it
    would be left out (`PL-49D5`).
    """

    alveolar = [0.004, 0.005, 0.006, 0.008, 0.009, 0.010, 0.012]
    series = [[0.01] * len(alveolar) for _ in FRACTION_STATE_NAMES]
    series[_INSPIRED_SERIES] = [0.02] * len(alveolar)
    series[_ALVEOLAR_SERIES] = alveolar
    ventilated = (False, False, True, True, True, True, True)

    assert _with_extremes(0, 6, (CaseInstant(0), CaseInstant(6)), series, ventilated) == (
        CaseInstant(0),
        CaseInstant(2),
        CaseInstant(6),
    )


def test_an_axis_of_zero_width_is_spaced_one_second_and_a_wider_one_by_its_columns() -> None:
    """The grid spacing is a whole number of seconds, never less than one, at every axis width.

    An axis of zero width is one instant, and its spacing is one second, so
    neither window sets a minimum of its own (`PL-WZDM`). A two-minute axis in
    150 columns would put them 120 / 149 = 0.81 s apart, which is raised to
    one second. A fifteen-minute axis gives 900 / 149 = 6.04 s and an hour
    3600 / 149 = 24.2 s, each rounded down to a whole second. Three columns
    over ten seconds stand at 0, 5 and 10 s, so they are 5 s apart.
    """

    assert _axis_spacing_s(30.0, 30.0, 150) == 1
    assert _axis_spacing_s(0.0, 120.0, 150) == 1
    assert _axis_spacing_s(0.0, 900.0, 150) == 6
    assert _axis_spacing_s(0.0, 3600.0, 150) == 24
    assert _axis_spacing_s(0.0, 10.0, 3) == 5
