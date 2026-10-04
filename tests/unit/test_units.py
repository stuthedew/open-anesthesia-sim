"""`core/units.py` holds each factor between units of time once, at its definition.

A minute is 60 s and an hour 60 min, so 3600 s, by definition (SI Brochure, 9th
edition, 2019, Table 8). These are pins against that definition rather than
restatements of the code: a mistyped factor fails here before it reaches a
flow conversion, a duration on the clock or a supported-range message.
"""

from __future__ import annotations

from anesthesia_sim.core.units import (
    MILLISECONDS_PER_SECOND,
    MINUTES_PER_HOUR,
    SECONDS_PER_HOUR,
    SECONDS_PER_MINUTE,
)


def test_each_factor_is_its_si_definition() -> None:
    assert SECONDS_PER_MINUTE == 60.0
    assert MINUTES_PER_HOUR == 60.0
    assert SECONDS_PER_HOUR == 3600.0
    assert MILLISECONDS_PER_SECOND == 1000


def test_the_hour_in_seconds_agrees_with_the_minute_and_the_hour() -> None:
    """One home for the hour in seconds, so it cannot drift from its factors (`PL-06M7`)."""
    assert SECONDS_PER_HOUR == SECONDS_PER_MINUTE * MINUTES_PER_HOUR
