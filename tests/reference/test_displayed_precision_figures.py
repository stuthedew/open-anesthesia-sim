"""The figures that `docs/INTERFACE.md` § "Displayed precision" prints match the model.

The section argues for the number of decimals each readout shows, and it backs
the argument with figures taken from runs of the model. A reader trusts the
argument only as far as those figures are right. Before `PL-19W8`, no test
computed them, and two blind reviews found three of them wrong
(`PL-B6YV`, `#1927`).

This module covers the figures that do not depend on the partition
coefficients' standard deviations. They are:

1. the lower limit on decimals: how long muscle and fat read `0.0%` at one
   decimal, and when each first shows a nonzero reading at two decimals;
2. the MAC readout's step in percentage points of each agent;
3. which compartment amounts read below the run totals' 0.1 L step for the
   first hour.

Each run is the section's own condition: the agent's stored 1 MAC on the dial,
the default flows, and the reference adult, stepped at 0.1 s for one hour.

Each figure is read from the section as printed and compared with the run at
the precision the section prints it with, as
`test_mac_awake_washout_figures.py` does. So a change to the model that moves
a figure fails here, and so does an edit that changes a figure without
changing the model.
"""

import re
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from anesthesia_sim.app.formatting import (
    MAC_DISPLAY_RESOLUTION_MAC,
    format_agent_volume,
    format_percent,
)
from anesthesia_sim.core.concentration import Fraction
from anesthesia_sim.core.parameters import load_agent_parameters
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

INTERFACE_PATH = Path(__file__).resolve().parents[2] / "docs" / "INTERFACE.md"
SECTION_HEADING = "### Displayed precision"

#: The section lists its per-agent figures in this order.
AGENTS = ("desflurane", "sevoflurane", "isoflurane")
STEP = SimulationStep(0.1)
RUN_S = 3600
SECONDS_PER_MINUTE = 60.0
ONE_DECIMAL_ZERO = "0.0"

#: A figure printed in whole seconds is the first 0.1 s step at which the
#: readout changes, rounded to the nearest second. This numerical limit is
#: that rounding: half a second either way, so a step at exactly x.5 s
#: matches either neighbour.
WHOLE_SECOND_LIMIT_S = 0.5
#: A figure printed in minutes to one decimal is a step time rounded to
#: 0.1 min. This numerical limit is that rounding: 0.05 min either way.
TENTH_MINUTE_LIMIT_MIN = 0.05


@dataclass(frozen=True)
class AgentRun:
    """What one hour at 1 MAC shows, for one agent, in the units the section prints."""

    muscle_first_two_decimal_s: float
    fat_first_two_decimal_s: float
    muscle_first_one_decimal_min: float
    fat_first_one_decimal_min: float | None
    fat_percent_at_end: float
    venous_amount_reads_below_step: bool
    alveolar_amount_reads_below_step: bool
    alveolar_first_reads_step_s: float | None


def _section_text() -> str:
    """The section's prose, with each run of whitespace made one space."""

    text = INTERFACE_PATH.read_text(encoding="utf-8")
    start = text.index(SECTION_HEADING)
    end = text.find("\n### ", start + len(SECTION_HEADING))

    return " ".join(text[start : end if end >= 0 else None].split())


def _one(pattern: str) -> tuple[str, ...]:
    """The groups of the one match of `pattern` in the section, or a failure naming it."""

    # regex: a search for one sentence's figures through free prose, which no
    # parser reads; the caller's pattern names the sentence's fixed words.
    matches = re.findall(pattern, _section_text())
    assert len(matches) == 1, (
        f"docs/INTERFACE.md § 'Displayed precision' should state this once, as {pattern!r}, "
        f"and it states it {len(matches)} times. If the sentence was reworded, update the "
        f"pattern here so the figure stays checked."
    )
    found = matches[0]

    return found if isinstance(found, tuple) else (found,)


def _one_decimal_percent(fraction: float) -> str:
    """The reading at one decimal place of percent, as a one-decimal readout would show it."""

    return f"{fraction * 100.0:.1f}"


@cache
def _run(agent_id: str) -> AgentRun:
    """Run one agent for an hour at its stored 1 MAC with the default flows."""

    system = AgentUptakeSystem.for_agent(agent_id)
    assert system.circuit.delivered_concentration_percent == float(
        load_agent_parameters(agent_id).mac_percent
    ), f"{agent_id} does not open at its stored 1 MAC, which is the section's condition"
    patient = system.patient
    first: dict[str, float] = {}
    venous_below = True
    alveolar_below = True

    for index in range(1, round(RUN_S / STEP) + 1):
        system.advance(STEP)
        elapsed_s = index * STEP
        for name, compartment in (("muscle", patient.muscle), ("fat", patient.fat)):
            fraction = compartment.partial_pressure_fraction
            if f"{name}:2" not in first and format_percent(Fraction(fraction)) != "<0.01%":
                first[f"{name}:2"] = elapsed_s
            if f"{name}:1" not in first and _one_decimal_percent(fraction) != ONE_DECIMAL_ZERO:
                first[f"{name}:1"] = elapsed_s
        venous_below &= format_agent_volume(patient.venous_blood.agent_amount_l) == "<0.1 L"
        reads_below = format_agent_volume(system.alveoli.agent_amount_l) == "<0.1 L"
        if alveolar_below and not reads_below:
            first["alveoli"] = elapsed_s
        alveolar_below &= reads_below

    fat_one_decimal_s = first.get("fat:1")

    return AgentRun(
        muscle_first_two_decimal_s=first["muscle:2"],
        fat_first_two_decimal_s=first["fat:2"],
        muscle_first_one_decimal_min=first["muscle:1"] / SECONDS_PER_MINUTE,
        fat_first_one_decimal_min=(
            None if fat_one_decimal_s is None else fat_one_decimal_s / SECONDS_PER_MINUTE
        ),
        fat_percent_at_end=patient.fat.partial_pressure_fraction * 100.0,
        venous_amount_reads_below_step=venous_below,
        alveolar_amount_reads_below_step=alveolar_below,
        alveolar_first_reads_step_s=first.get("alveoli"),
    )


def _three() -> str:
    """A pattern for three whole numbers listed as "a, b and c"."""

    return r"(\d+), (\d+) and (\d+)"


def test_the_first_nonzero_two_decimal_readings_match_the_model() -> None:
    """Muscle and fat first read above `<0.01%` at the times the lower-limit paragraph prints."""

    muscle = _one(rf"muscle first shows a nonzero value at {_three()} seconds")
    fat = _one(rf"and fat at {_three()} seconds, for desflurane, sevoflurane and isoflurane")

    for agent_id, muscle_s, fat_s in zip(AGENTS, muscle, fat, strict=True):
        run = _run(agent_id)
        for what, printed, value in (
            ("muscle", muscle_s, run.muscle_first_two_decimal_s),
            ("fat", fat_s, run.fat_first_two_decimal_s),
        ):
            assert abs(value - int(printed)) <= WHOLE_SECOND_LIMIT_S, (
                f"§ 'Displayed precision' says {agent_id}'s {what} first reads above <0.01% at "
                f"{printed} s, and the model first does at {value:.1f} s. Update the figure."
            )


def test_the_one_decimal_erasure_times_match_the_model() -> None:
    """At one decimal, muscle and desflurane's fat read `0.0%` for the minutes printed."""

    muscle = _one(
        r"Muscle reads `0.0%` for its first (\d+\.\d) minutes with desflurane, (\d+\.\d) "
        r"minutes with sevoflurane and (\d+\.\d) minutes with isoflurane"
    )
    (desflurane_fat,) = _one(r"Desflurane's fat fraction stays at `0.0%` for its first (\d+\.\d)")

    for agent_id, printed in zip(AGENTS, muscle, strict=True):
        value = _run(agent_id).muscle_first_one_decimal_min
        assert abs(value - float(printed)) <= TENTH_MINUTE_LIMIT_MIN, (
            f"{agent_id}'s muscle reads 0.0% for {value:.2f} min at one decimal, and the "
            f"section prints {printed} min"
        )
    value_or_none = _run("desflurane").fat_first_one_decimal_min
    assert value_or_none is not None, "desflurane's fat reads 0.0% for the whole hour"
    assert abs(value_or_none - float(desflurane_fat)) <= TENTH_MINUTE_LIMIT_MIN, (
        f"desflurane's fat reads 0.0% for {value_or_none:.2f} min at one decimal, and the "
        f"section prints {desflurane_fat} min"
    )


def test_the_fat_fractions_at_one_hour_match_the_model() -> None:
    """Sevoflurane's and isoflurane's fat read `0.0%` all hour, at the percents printed."""

    sevoflurane, isoflurane = _one(
        r"fat fractions read `0.0%` for the whole hour \((0\.\d+)% and (0\.\d+)% at 3600 s\)"
    )
    (desflurane,) = _one(r"for its first \d+\.\d minutes and reaches (\d\.\d)%")

    for agent_id, printed in (("sevoflurane", sevoflurane), ("isoflurane", isoflurane)):
        run = _run(agent_id)
        assert run.fat_first_one_decimal_min is None, (
            f"{agent_id}'s fat reads above 0.0% at one decimal within the hour"
        )
        places = len(printed.split(".")[1])
        assert f"{run.fat_percent_at_end:.{places}f}" == printed, (
            f"{agent_id}'s fat is {run.fat_percent_at_end!r}% at 3600 s, printed as {printed}%"
        )
    reached = _run("desflurane").fat_percent_at_end
    assert f"{reached:.1f}" == desflurane, (
        f"desflurane's fat is {reached!r}% at 3600 s, and the section says it reaches {desflurane}%"
    )


def test_the_mac_step_in_percentage_points_matches_each_stored_mac() -> None:
    """One 0.01 MAC step is the percentage points the MAC paragraph prints for each agent."""

    sevoflurane, isoflurane, desflurane = _one(
        r"One step is (0\.\d+) percentage points of sevoflurane, (0\.\d+) of isoflurane and "
        r"(0\.\d+) of desflurane"
    )

    for agent_id, printed in (
        ("sevoflurane", sevoflurane),
        ("isoflurane", isoflurane),
        ("desflurane", desflurane),
    ):
        step_pp = MAC_DISPLAY_RESOLUTION_MAC * float(load_agent_parameters(agent_id).mac_percent)
        places = len(printed.split(".")[1])
        assert f"{step_pp:.{places}f}" == printed, (
            f"one MAC step of {agent_id} is {step_pp!r} percentage points, printed as {printed}"
        )


def test_the_amounts_below_the_run_totals_step_match_the_model() -> None:
    """Venous blood, and two agents' alveoli, read below 0.1 L for the hour; desflurane's do not.

    The paragraph says "about two minutes" for desflurane's alveoli. The test
    reads that as the first time the amount reads 0.1 L, rounded to whole
    minutes.
    """

    _one(
        r"venous blood reads below resolution for a whole hour at 1 MAC with every agent the "
        r"simulator offers, and so do the alveoli with sevoflurane and isoflurane"
    )
    _one(r"Desflurane's alveoli read 0\.1 L from (about two minutes)")

    for agent_id in AGENTS:
        assert _run(agent_id).venous_amount_reads_below_step, (
            f"{agent_id}'s venous blood reads 0.1 L or more within the hour"
        )
    for agent_id in ("sevoflurane", "isoflurane"):
        assert _run(agent_id).alveolar_amount_reads_below_step, (
            f"{agent_id}'s alveoli read 0.1 L or more within the hour"
        )
    first_s = _run("desflurane").alveolar_first_reads_step_s
    assert first_s is not None, "desflurane's alveoli read below 0.1 L for the whole hour"
    assert round(first_s / SECONDS_PER_MINUTE) == 2, (
        f"desflurane's alveoli first read 0.1 L at {first_s:.1f} s, not about two minutes"
    )
