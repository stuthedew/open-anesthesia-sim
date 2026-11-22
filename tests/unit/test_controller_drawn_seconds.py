"""Tests of how the controller chooses the seconds a chart window draws."""

from __future__ import annotations

import pytest

from anesthesia_sim.app.controller import _ALVEOLAR_SERIES, _with_extremes
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
        _with_extremes(0, 4, (CaseInstant(0), CaseInstant(4)), series)
