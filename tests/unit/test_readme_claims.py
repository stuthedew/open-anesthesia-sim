"""Hold the capability facts that `README.md` states to the code that decides them.

`README.md` § "What it simulates" tells a reader three things the interface
offers: the playback rates, the range of chart time bases, and the agents. Each
is decided by a constant in the package, and nothing else compares the front
page with those constants. Without these tests, adding a playback rate, moving
the time-base floor or ceiling, or shipping a fourth agent would leave the
README stating the old value with every other check passing (`PL-GQWP`).

Each test fails with a message that names the sentence to update.
"""

import re
from pathlib import Path

from anesthesia_sim.app.chart_time_base import SELECTABLE_TIME_BASES
from anesthesia_sim.app.formatting import format_playback_rate
from anesthesia_sim.app.playback import SUPPORTED_PLAYBACK_RATES
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES, load_agent_parameters

#: The README, read as one string with its line breaks folded into spaces, so a
#: sentence matches whatever the line wrapping.
README_TEXT = " ".join(
    (Path(__file__).parents[2] / "README.md").read_text(encoding="utf-8").split()
)


def test_the_readme_lists_every_offered_playback_rate_in_order() -> None:
    """The README lists the rates the interface offers, in the interface's own labels."""

    multipliers = [
        format_playback_rate(rate.multiplier).removesuffix(" real time")
        for rate in SUPPORTED_PLAYBACK_RATES
    ]
    # Anchored at "played at **" and closed by the bold, so the README cannot
    # list a rate before or after the ones the interface offers and still pass.
    sentence = f"played at **{', '.join(multipliers[:-1])} or {multipliers[-1]} real time**"

    assert sentence in README_TEXT, (
        f"README.md § 'Playback speed and time base' must list the offered rates as '{sentence}'"
    )


def test_the_readme_gives_the_selectable_time_base_range() -> None:
    """The README's range runs from the narrowest to the widest time base the selector offers.

    The README writes the range in words. The expected spans, 900 s and
    43,200 s, are the fifteen minutes and twelve hours that the project owner
    settled on for the selector on 2026-09-04 (`app/chart_time_base.py`).
    """

    spans_s = [time_base.span_s for time_base in SELECTABLE_TIME_BASES]

    assert (min(spans_s), max(spans_s)) == (900.0, 43200.0), (
        "the selectable time bases changed: update README.md § 'Playback speed and time base', "
        "then this test's expected range"
    )
    assert "from fifteen minutes to twelve hours" in README_TEXT


def test_the_readme_names_exactly_the_shipped_agents() -> None:
    """The README's list of agents is the list of built-in agent files, by display name."""

    match = re.search(r"one volatile agent at a time \(([^)]*)\)", README_TEXT)
    assert match is not None, (
        "README.md § 'The model' no longer lists the agents in its first sentence"
    )
    named = set(re.split(r", | or ", match.group(1)))
    shipped = {
        load_agent_parameters(agent_id).display_name.lower() for agent_id in AGENT_DATA_FILENAMES
    }

    assert named == shipped, (
        f"README.md § 'The model' names {sorted(named)}; the built-in agents are {sorted(shipped)}"
    )
