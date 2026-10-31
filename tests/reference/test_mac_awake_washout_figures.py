"""The washout figures that `docs/MODEL.md` prints for the MAC-awake band match the model.

`docs/MODEL.md` § "MAC-awake as a chart reference" gives one measured
emergence. Sevoflurane runs for 3 hours at the opening dial of 2.0% and the
default fresh gas flow of 4 L/min. Then the vaporizer is turned off and the
fresh gas flow is raised to 10 L/min. The section prints six figures from that
run, and a learner reads them as what the model does. They depend on the
partition coefficients, the volumes, the ventilation, the cardiac output and
the protocol. Before `PL-PTDZ` no test held them, so a parameter change would
have left the specification teaching a wake-up time that the model no longer
produces.

This test runs the protocol and compares each result with the figure the
document prints, read from the document itself. A figure is held to the
number of decimal places the document prints it with. So a change that moves
a result fails here, and so does an edit to the document that changes a
figure without the model. The test pins the specification to the model. It
does not validate the model against patients; `PL-39KH` and the section
itself say what the figures do and do not show.

A crossing time is where the trace passes the threshold, found by linear
interpolation between the two 0.1 s steps on either side of it. Reading the
first step below the threshold instead would add up to 0.1 s, which can move
a figure printed to 0.01 min across a rounding boundary.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import pytest

from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.parameters import load_agent_parameters
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.supported_ranges import FreshGasFlow
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

MODEL_PATH = Path(__file__).resolve().parents[2] / "docs" / "MODEL.md"
SECTION_HEADING = "### MAC-awake as a chart reference"

AGENT_ID = "sevoflurane"
STEP = SimulationStep(0.1)
MAINTENANCE_S = 3 * 60 * 60
#: The fresh gas flow after the vaporizer is turned off, which the section
#: states in its own words.
WASHOUT_FRESH_GAS_FLOW_L_MIN = 10.0
#: A bound on the washout's length, so that a model that never crosses a
#: threshold fails here instead of looping. The latest figure is near 7.3 min.
WASHOUT_LIMIT_S = 60 * 60
SECONDS_PER_MINUTE = 60.0


@dataclass(frozen=True)
class Washout:
    """What the protocol produces, in the units the document prints."""

    maintenance_alveolar_percent: float
    maintenance_alveolar_mac: float
    band_centre_percent: float
    alveolar_crossing_min: float
    vessel_rich_crossing_min: float
    mapleson_band_centre_percent: float
    vessel_rich_mapleson_crossing_min: float


@dataclass(frozen=True)
class PrintedFigures:
    """The section's figures as printed, each kept as text so its decimal places are known."""

    maintenance_alveolar_percent: str
    maintenance_alveolar_mac: str
    alveolar_crossing_min: str
    vessel_rich_crossing_min: str
    crossing_ratio: str
    band_centre_percent: str
    vessel_rich_crossing_min_again: str
    mapleson_band_centre_percent: str
    mapleson_mac_percent: str
    vessel_rich_mapleson_crossing_min: str


def _section_text() -> str:
    """The section's prose, with each run of whitespace made one space."""

    text = MODEL_PATH.read_text(encoding="utf-8")
    start = text.index(SECTION_HEADING)
    end = text.find("\n### ", start + len(SECTION_HEADING))

    return " ".join(text[start : end if end >= 0 else None].split())


def _one(pattern: str, text: str) -> tuple[str, ...]:
    """The groups of the one match of `pattern`, or a failure that says what moved."""

    matches = re.findall(pattern, text)
    assert len(matches) == 1, (
        f"docs/MODEL.md § 'MAC-awake as a chart reference' should state this once, as "
        f"{pattern!r}, and it states it {len(matches)} times. If the sentence was reworded, "
        f"update the pattern here so the figure stays checked."
    )
    found = matches[0]

    return found if isinstance(found, tuple) else (found,)


@cache
def _printed() -> PrintedFigures:
    text = _section_text()
    number = r"(\d+\.\d+)"
    percent, mac = _one(rf"alveolar fraction only to {number}%, or {number} MAC", text)
    (alveolar,) = _one(rf"alveolar trace crosses the band's centre at {number} min", text)
    vessel_rich, ratio = _one(
        rf"vessel-rich trace crosses it at {number} min, {number} times later", text
    )
    centre, again = _one(
        rf"vessel-rich trace crosses sevoflurane's drawn band centre of {number}% at "
        rf"{number} min",
        text,
    )
    mapleson_centre, mapleson_mac, mapleson_crossing = _one(
        rf"It crosses {number}%, the same fraction of Mapleson's {number}%, at {number} min", text
    )

    return PrintedFigures(
        maintenance_alveolar_percent=percent,
        maintenance_alveolar_mac=mac,
        alveolar_crossing_min=alveolar,
        vessel_rich_crossing_min=vessel_rich,
        crossing_ratio=ratio,
        band_centre_percent=centre,
        vessel_rich_crossing_min_again=again,
        mapleson_band_centre_percent=mapleson_centre,
        mapleson_mac_percent=mapleson_mac,
        vessel_rich_mapleson_crossing_min=mapleson_crossing,
    )


def _crossing_min(
    system: AgentUptakeSystem,
    traces: dict[str, Callable[[AgentUptakeSystem], float]],
    thresholds: dict[str, float],
) -> dict[str, float]:
    """Step the washout and return the minute at which each named trace falls through its threshold.

    The time is interpolated linearly between the two steps on either side of
    the crossing.
    """

    previous = {name: trace(system) for name, trace in traces.items()}
    crossings: dict[str, float] = {}
    elapsed_s = 0.0

    while len(crossings) < len(thresholds):
        assert elapsed_s < WASHOUT_LIMIT_S, f"no crossing within an hour for {thresholds}"
        system.advance(STEP)
        elapsed_s += STEP

        for name, threshold in thresholds.items():
            now = traces[name.split(":")[0]](system)
            before = previous[name.split(":")[0]]

            if name not in crossings and before > threshold >= now:
                fraction_of_step = (before - threshold) / (before - now)
                crossed_s = elapsed_s - STEP + fraction_of_step * STEP
                crossings[name] = crossed_s / SECONDS_PER_MINUTE

        previous = {name: trace(system) for name, trace in traces.items()}

    return crossings


@pytest.fixture(scope="module")
def washout() -> Washout:
    """Run the section's protocol once for every figure."""

    agent = load_agent_parameters(AGENT_ID)
    mac_percent = float(agent.mac_percent)
    band_fraction_of_mac = float(agent.mac_awake.fraction_of_mac)
    band_centre = band_fraction_of_mac * mac_percent / 100.0
    # The section's Mapleson MAC is a published value restated beside its
    # citation in the same section, so the test reads it from there.
    mapleson_centre = band_fraction_of_mac * float(_printed().mapleson_mac_percent) / 100.0

    system = AgentUptakeSystem.for_agent(AGENT_ID)

    for _ in range(round(MAINTENANCE_S / STEP)):
        system.advance(STEP)

    alveolar_fraction = system.alveoli.partial_pressure_fraction
    system.set_delivered_concentration_percent(Percent(0.0))
    system.set_fresh_gas_flow(FreshGasFlow(WASHOUT_FRESH_GAS_FLOW_L_MIN))
    crossings = _crossing_min(
        system,
        {
            "alveolar": lambda s: s.alveoli.partial_pressure_fraction,
            "vessel_rich": lambda s: s.patient.vessel_rich.partial_pressure_fraction,
        },
        {
            "alveolar": band_centre,
            "vessel_rich": band_centre,
            "vessel_rich:mapleson": mapleson_centre,
        },
    )

    return Washout(
        maintenance_alveolar_percent=alveolar_fraction * 100.0,
        maintenance_alveolar_mac=alveolar_fraction * 100.0 / mac_percent,
        band_centre_percent=band_centre * 100.0,
        alveolar_crossing_min=crossings["alveolar"],
        vessel_rich_crossing_min=crossings["vessel_rich"],
        mapleson_band_centre_percent=mapleson_centre * 100.0,
        vessel_rich_mapleson_crossing_min=crossings["vessel_rich:mapleson"],
    )


def _as_printed(value: float, printed: str) -> str:
    """`value` to as many decimal places as `printed` has."""

    return f"{value:.{len(printed.split('.')[1])}f}"


FIGURES: dict[str, Callable[[Washout, PrintedFigures], tuple[float, str]]] = {
    "maintenance alveolar percent": lambda w, p: (
        w.maintenance_alveolar_percent,
        p.maintenance_alveolar_percent,
    ),
    "maintenance alveolar MAC": lambda w, p: (
        w.maintenance_alveolar_mac,
        p.maintenance_alveolar_mac,
    ),
    "alveolar crossing": lambda w, p: (w.alveolar_crossing_min, p.alveolar_crossing_min),
    "vessel-rich crossing": lambda w, p: (w.vessel_rich_crossing_min, p.vessel_rich_crossing_min),
    "vessel-rich over alveolar crossing time": lambda w, p: (
        w.vessel_rich_crossing_min / w.alveolar_crossing_min,
        p.crossing_ratio,
    ),
    "drawn band centre": lambda w, p: (w.band_centre_percent, p.band_centre_percent),
    "vessel-rich crossing, restated": lambda w, p: (
        w.vessel_rich_crossing_min,
        p.vessel_rich_crossing_min_again,
    ),
    "band centre at Mapleson's MAC": lambda w, p: (
        w.mapleson_band_centre_percent,
        p.mapleson_band_centre_percent,
    ),
    "vessel-rich crossing of the band at Mapleson's MAC": lambda w, p: (
        w.vessel_rich_mapleson_crossing_min,
        p.vessel_rich_mapleson_crossing_min,
    ),
}


@pytest.mark.parametrize("figure", list(FIGURES))
def test_the_mac_awake_washout_figures_match_the_model(washout: Washout, figure: str) -> None:
    """Each figure the section prints is what the protocol produces, to the places printed."""

    value, printed = FIGURES[figure](washout, _printed())

    assert _as_printed(value, printed) == printed, (
        f"docs/MODEL.md § 'MAC-awake as a chart reference' prints the {figure} as {printed}, "
        f"and the model now gives {value!r}. Update the section's figure, and check that "
        f"the sentence around it is still true."
    )
