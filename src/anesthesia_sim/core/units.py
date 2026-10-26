"""The factors between units of time and of volume, each written once.

A minute is sixty seconds and an hour is sixty minutes, by definition (SI
Brochure, 9th edition, 2019, Table 8). A litre is a cubic decimetre, so a
cubic metre holds a thousand litres and a litre holds a thousand millilitres.
So nothing here is a measured constant, and nothing carries a provenance note.
The module provides one place to import the factors from. Before it existed,
five core modules each declared `SECONDS_PER_MINUTE` in their own header, and
a reference test borrowed that name to turn minutes into hours (`PL-QRBB`).
The hour in seconds is the product of the other two factors rather than a
third literal, because seven sites had typed `3600` by hand (`PL-06M7`).

It imports nothing from the package, so a module importing it cannot form a
cycle.
"""

from __future__ import annotations

from typing import Final

SECONDS_PER_MINUTE: Final = 60.0
"""Seconds in one minute."""

MINUTES_PER_HOUR: Final = 60.0
"""Minutes in one hour."""

SECONDS_PER_HOUR: Final = SECONDS_PER_MINUTE * MINUTES_PER_HOUR
"""Seconds in one hour, derived from the two above so it cannot disagree with them."""

MILLISECONDS_PER_SECOND: Final = 1000
"""Milliseconds in one second."""

LITRES_PER_CUBIC_METRE: Final = 1000.0
"""Litres in one cubic metre."""

MILLILITRES_PER_LITRE: Final = 1000.0
"""Millilitres in one litre."""
