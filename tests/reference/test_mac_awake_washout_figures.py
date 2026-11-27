"""The washout figures that `docs/INTERFACE.md` prints for the MAC-awake band match the model.

`docs/INTERFACE.md` § "MAC-awake as a chart reference" gives one emergence
measured on the model. Sevoflurane runs for 3 hours at the opening vaporizer
dial setting of 1.80% and the default fresh gas flow of 4 L/min. Then the
vaporizer is turned off and the fresh gas flow is raised to 10 L/min. The
section prints figures from that run, and a user takes them as what the
model does. They depend on the partition coefficients, the volumes, the
ventilation, the cardiac output and the protocol. Before `PL-PTDZ`, no test
checked them. A parameter change would have left the specification teaching a
wake-up time that the model no longer produces.

This test reads the protocol from the section and checks that the run starts
at the dial setting and flow that the section names. It then runs the protocol
and compares each result with the figure that the document prints, read from
the document itself. Each figure is compared at the number of decimal places
that the document prints it with. So a change that moves a result fails here,
and so does an edit to the document that changes a figure without changing the
model. The test pins the specification to the model. It does not validate the
model against patients. `PL-39KH` and the section itself say what the figures
do and do not show.

A crossing time is the moment at which the trace passes the threshold. The
test finds it by linear interpolation between the two one-second steps on
either side of the crossing. Taking the first step below the threshold instead
would add up to 1 s, which is more than the 0.01 min that the document prints
a crossing to. On 2026-11-21 each of the three interpolated crossings was
within 1.3e-5 min of the crossing found by bisection on the model's exact
solution (`RunDefinition.state_at`).
"""

import re
from collections.abc import Callable
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import pytest

from anesthesia_sim.app.formatting import mac_awake_band_percent
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.parameters import load_agent_parameters
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import FreshGasFlow
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

INTERFACE_PATH = Path(__file__).resolve().parents[2] / "docs" / "INTERFACE.md"
SECTION_HEADING = "### MAC-awake as a chart reference"

AGENT_ID = "sevoflurane"
SECONDS_PER_HOUR = 3600
#: A bound on the washout's length, so that a model that never crosses a
#: threshold fails here instead of looping. The latest figure is near 7.3 min.
WASHOUT_LIMIT_S = 60 * 60
SECONDS_PER_MINUTE = 60.0


@dataclass(frozen=True)
class Washout:
    """What the protocol produces, in the units the document prints."""

    maintenance_alveolar_percent: float
    maintenance_alveolar_mac: float
    maintenance_vessel_rich_mac: float
    band_centre_percent: float
    alveolar_crossing_min: float
    vessel_rich_crossing_min: float


@dataclass(frozen=True)
class PrintedFigures:
    """The section's protocol and figures as printed, each kept as text so its places are known."""

    maintenance_hours: str
    opening_dial_percent: str
    opening_fresh_gas_flow_l_min: str
    washout_fresh_gas_flow_l_min: str
    maintenance_alveolar_percent: str
    maintenance_alveolar_mac: str
    maintenance_vessel_rich_mac: str
    alveolar_crossing_min: str
    vessel_rich_crossing_min: str
    crossing_ratio: str
    band_centre_percent: str
    vessel_rich_crossing_min_again: str


def _section_text() -> str:
    """The section's prose, with each run of whitespace made one space."""

    text = INTERFACE_PATH.read_text(encoding="utf-8")
    start = text.index(SECTION_HEADING)
    end = text.find("\n### ", start + len(SECTION_HEADING))

    return " ".join(text[start : end if end >= 0 else None].split())


def _one(pattern: str, text: str) -> tuple[str, ...]:
    """The groups of the one match of `pattern`, or a failure that says what moved."""

    # regex: each figure is read from a sentence of prose in docs/INTERFACE.md,
    # and only a pattern can fix the words around a number and capture it.
    matches = re.findall(pattern, text)
    assert len(matches) == 1, (
        f"docs/INTERFACE.md § 'MAC-awake as a chart reference' should state this once, as "
        f"{pattern!r}, and it states it {len(matches)} times. If the sentence was reworded, "
        f"update the pattern here so the figure stays checked."
    )
    found = matches[0]

    return found if isinstance(found, tuple) else (found,)


@cache
def _printed() -> PrintedFigures:
    text = _section_text()
    number = r"(\d+\.\d+)"
    whole = r"(\d+)"
    hours, dial, opening_flow = _one(
        rf"It ran sevoflurane for {whole} hours at the opening dial of {number}%, which is the "
        rf"stored 1 MAC, and the default fresh gas flow of {whole} L/min",
        text,
    )
    (washout_flow,) = _one(
        rf"The vaporizer was then turned off and the fresh gas flow raised to {whole} L/min", text
    )
    percent, mac = _one(rf"alveolar fraction only to {number}%, or {number} MAC", text)
    (vessel_rich_mac,) = _one(rf"the vessel-rich trace reached only {number} MAC", text)
    (alveolar,) = _one(rf"alveolar trace crosses the band's centre at {number} min", text)
    vessel_rich, ratio = _one(
        rf"vessel-rich trace crosses it at {number} min, {number} times later", text
    )
    centre, again = _one(
        rf"vessel-rich trace crosses sevoflurane's drawn band centre of {number}% at "
        rf"{number} min",
        text,
    )
    return PrintedFigures(
        maintenance_hours=hours,
        opening_dial_percent=dial,
        opening_fresh_gas_flow_l_min=opening_flow,
        washout_fresh_gas_flow_l_min=washout_flow,
        maintenance_alveolar_percent=percent,
        maintenance_alveolar_mac=mac,
        maintenance_vessel_rich_mac=vessel_rich_mac,
        alveolar_crossing_min=alveolar,
        vessel_rich_crossing_min=vessel_rich,
        crossing_ratio=ratio,
        band_centre_percent=centre,
        vessel_rich_crossing_min_again=again,
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
    elapsed_s = 0

    while len(crossings) < len(thresholds):
        assert elapsed_s < WASHOUT_LIMIT_S, f"no crossing within an hour for {thresholds}"
        system.advance()
        elapsed_s += SIMULATION_STEP_S

        for name, threshold in thresholds.items():
            now = traces[name.split(":")[0]](system)
            before = previous[name.split(":")[0]]

            if name not in crossings and before > threshold >= now:
                fraction_of_step = (before - threshold) / (before - now)
                crossed_s = elapsed_s - SIMULATION_STEP_S + fraction_of_step * SIMULATION_STEP_S
                crossings[name] = crossed_s / SECONDS_PER_MINUTE

        previous = {name: trace(system) for name, trace in traces.items()}

    return crossings


@pytest.fixture(scope="module")
def washout() -> Washout:
    """Run the section's protocol once for every figure."""

    printed = _printed()
    agent = load_agent_parameters(AGENT_ID)
    mac_percent = float(agent.mac_at_age_40_percent)
    # The centre of the band as the chart draws it, through the function the
    # chart calls, so a change to how the band is placed reaches this test.
    band_lower, band_upper = mac_awake_band_percent(
        fraction_of_mac=agent.mac_awake.fraction_of_mac,
        standard_deviation_fraction_of_mac=agent.mac_awake.standard_deviation_fraction_of_mac,
        mac_percent=agent.mac_at_age_40_percent,
    )
    band_centre = (band_lower + band_upper) / 2.0 / 100.0

    system = AgentUptakeSystem.for_agent(AGENT_ID)
    # The section says the run opened at the stored 1 MAC and the default
    # flow, so the run built here must open where the section says it did.
    opening = (
        system.circuit.delivered_concentration_percent,
        mac_percent,
        system.circuit.fresh_gas_flow_l_min,
    )
    assert opening == (
        float(printed.opening_dial_percent),
        float(printed.opening_dial_percent),
        float(printed.opening_fresh_gas_flow_l_min),
    ), f"the run opens at (dial %, stored MAC %, flow L/min) = {opening}, not as the section says"

    for _ in range(int(printed.maintenance_hours) * SECONDS_PER_HOUR // SIMULATION_STEP_S):
        system.advance()

    alveolar_fraction = system.alveoli.partial_pressure_fraction
    vessel_rich_fraction = system.patient.vessel_rich.partial_pressure_fraction
    system.set_delivered_concentration_percent(Percent(0.0))
    system.set_fresh_gas_flow(FreshGasFlow(float(printed.washout_fresh_gas_flow_l_min)))
    crossings = _crossing_min(
        system,
        {
            "alveolar": lambda s: s.alveoli.partial_pressure_fraction,
            "vessel_rich": lambda s: s.patient.vessel_rich.partial_pressure_fraction,
        },
        {"alveolar": band_centre, "vessel_rich": band_centre},
    )

    return Washout(
        maintenance_alveolar_percent=alveolar_fraction * 100.0,
        maintenance_alveolar_mac=alveolar_fraction * 100.0 / mac_percent,
        maintenance_vessel_rich_mac=vessel_rich_fraction * 100.0 / mac_percent,
        band_centre_percent=band_centre * 100.0,
        alveolar_crossing_min=crossings["alveolar"],
        vessel_rich_crossing_min=crossings["vessel_rich"],
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
    "maintenance vessel-rich MAC": lambda w, p: (
        w.maintenance_vessel_rich_mac,
        p.maintenance_vessel_rich_mac,
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
}


@pytest.mark.parametrize("figure", list(FIGURES))
def test_the_mac_awake_washout_figures_match_the_model(washout: Washout, figure: str) -> None:
    """Each figure the section prints is what the protocol produces, to the places printed."""

    value, printed = FIGURES[figure](washout, _printed())

    assert _as_printed(value, printed) == printed, (
        f"docs/INTERFACE.md § 'MAC-awake as a chart reference' prints the {figure} as {printed}, "
        f"and the model now gives {value!r}. Update the section's figure, and check that "
        f"the sentence around it is still true."
    )
