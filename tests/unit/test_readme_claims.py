"""Check the capability facts that `README.md` states against the code that decides them.

`README.md` § "What it simulates" tells a reader three things the interface
offers: the playback rates, the range of chart time bases, and the agents. Each
is decided by a constant in the package, and nothing else compares the README
with those constants. Without these tests, someone could add a playback rate,
move the narrowest or widest time base, or ship a fourth agent, and the README
would go on stating the old value while every other check passed (`PL-GQWP`).

The README's image of the window shows six modelled concentrations, and its alt
text lists them. The last test runs the default case for the same simulated
time as the image and compares the run's readouts with those in the alt text
(`PL-MBP6`). A change to the model that moves a readout then fails here until
the image is retaken.

Each test fails with a message that names the sentence to update.
"""

import sys
from pathlib import Path

from anesthesia_sim.app.chart_time_base import SELECTABLE_TIME_BASES
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import SIMULATION_STEP_S
from anesthesia_sim.app.formatting import format_percent, format_playback_rate
from anesthesia_sim.app.playback import SUPPORTED_PLAYBACK_RATES
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES, load_agent_parameters

# `tests/benchmarks/` is not a package, so the screenshot script is imported by its path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmarks"))
import readme_screenshot

#: The README is read as one string, with its line breaks folded into spaces, so
#: a sentence matches however the lines wrap.
README_TEXT = " ".join(
    (Path(__file__).parents[2] / "README.md").read_text(encoding="utf-8").split()
)


def test_the_readme_lists_every_offered_playback_rate_in_order() -> None:
    """The README lists the rates the interface offers, in the interface's own labels."""

    multipliers = [
        format_playback_rate(rate.multiplier).removesuffix(" real time")
        for rate in SUPPORTED_PLAYBACK_RATES
    ]
    # The expected text starts at "played at **" and ends at the closing "**", so
    # the test fails if the README lists a rate before or after the offered ones.
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

    _, found, rest = README_TEXT.partition("one volatile agent at a time (")
    assert found, "README.md § 'The model' no longer lists the agents in its first sentence"
    listed, _, _ = rest.partition(")")
    named = {name for part in listed.split(", ") for name in part.split(" or ")}
    shipped = {
        load_agent_parameters(agent_id).display_name.lower() for agent_id in AGENT_DATA_FILENAMES
    }

    assert named == shipped, (
        f"README.md § 'The model' names {sorted(named)}; the built-in agents are {sorted(shipped)}"
    )


def test_the_readme_image_shows_the_readouts_the_default_case_reaches() -> None:
    """The alt text's six readouts are what the default case shows at the image's simulated time.

    The run is the one `tests/benchmarks/readme_screenshot.py` renders: a new controller
    with its default settings, started and advanced in the interface's own steps up to that
    time (`readme_screenshot.SIMULATED_S`).
    """

    controller = SimulationController()
    controller.start()
    for _ in range(round(readme_screenshot.SIMULATED_S / SIMULATION_STEP_S)):
        controller.advance(SIMULATION_STEP_S)
    snapshot = controller.snapshot()
    readouts = {
        "circuit": snapshot.inspired_partial_pressure_fraction,
        "alveolar": snapshot.alveolar_partial_pressure_fraction,
        "mixed venous": snapshot.mixed_venous_partial_pressure_fraction,
        "vessel-rich group": snapshot.vessel_rich_partial_pressure_fraction,
        "muscle": snapshot.muscle_partial_pressure_fraction,
        "fat": snapshot.fat_partial_pressure_fraction,
    }

    for name, fraction in readouts.items():
        expected = f"{name} {format_percent(fraction)}"
        assert expected in README_TEXT, (
            f"the default case now shows '{expected}' after {readme_screenshot.SIMULATED_S:g} s: "
            "retake the README image with tests/benchmarks/readme_screenshot.py and update "
            "its alt text and caption"
        )
