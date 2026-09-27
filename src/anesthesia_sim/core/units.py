"""The factors between units of time, each written once.

A minute is sixty seconds and an hour sixty minutes by definition (SI
Brochure, 9th edition, 2019, Table 8), so nothing here is a measured constant
and nothing carries a provenance note. What the module buys is one place to
import them from: five core modules each declared `SECONDS_PER_MINUTE` in
their own header, and a reference test borrowed that name to turn minutes into
hours (`PL-QRBB`).

It imports nothing from the package, so a module importing it cannot form a
cycle.
"""

from __future__ import annotations

from typing import Final

SECONDS_PER_MINUTE: Final = 60.0
"""Seconds in one minute."""

MINUTES_PER_HOUR: Final = 60.0
"""Minutes in one hour."""

MILLISECONDS_PER_SECOND: Final = 1000
"""Milliseconds in one second."""
