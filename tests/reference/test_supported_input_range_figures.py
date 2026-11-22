"""The figures in `docs/INTERFACE.md` § "Supported input ranges" follow from the model and its data.

The section argues for each supported range and for the 24-hour run length
with figures that a reader takes on trust. Three of its paragraphs state
figures that no other test computed:

1. how $F_A/F_I$ at five minutes rises as cardiac output falls toward zero,
   which `docs/MODEL.md` § "The four controls" repeats;
2. how far a long sevoflurane run goes past the exposure range of the
   studies that Kharasch's review of its metabolism draws on;
3. what fraction of sevoflurane's fat time constant the 24 hours are.

Each test reads the figures from the text as printed, with a narrow pattern
for the sentence that states them, and computes them independently: from a
run of the model built directly at the stated settings, or from the stored
parameters through the loaders. It compares the two at the number of decimal
places the text prints. So a change to the model or to a data file that moves
a figure fails here, and so does an edit to the text that changes a figure
without changing what it was computed from.
"""

import math
import re
from functools import cache
from pathlib import Path

from anesthesia_sim.core.governing_equations import (
    ALVEOLAR_FRACTION,
    INSPIRED_FRACTION,
    STATE_SIZE,
    UNIT_STATE,
)
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.prediction import predicted_states_at
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    CardiacOutput,
    CaseInstant,
)
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

DOCS = Path(__file__).resolve().parents[2] / "docs"
INTERFACE_PATH = DOCS / "INTERFACE.md"
MODEL_PATH = DOCS / "MODEL.md"
SECTION_HEADING = "### Supported input ranges"
FOUR_CONTROLS_HEADING = "### The four controls"

SECONDS_PER_HOUR = 3600.0
MINUTES_PER_HOUR = 60.0
FIVE_MINUTES_S = 300

#: The agent that both paragraphs about the run length are written for.
SEVOFLURANE = "sevoflurane"


def _section(path: Path, heading: str) -> str:
    """The text under `heading`, to the next heading at its depth or shallower,
    with each run of whitespace made one space."""

    text = path.read_text(encoding="utf-8")
    start = text.index(f"\n{heading}\n")
    depth = heading.split(" ", 1)[0]
    # regex: the next markdown heading at this depth or shallower, a fixed
    # line shape.
    after = re.search(rf"\n#{{1,{len(depth)}}} ", text[start + len(heading) + 1 :])
    end = start + len(heading) + 1 + after.start() if after else len(text)

    return " ".join(text[start:end].split())


@cache
def _supported_ranges_text() -> str:
    return _section(INTERFACE_PATH, SECTION_HEADING)


def _one(pattern: str, text: str | None = None) -> tuple[str, ...]:
    """The groups of the one sentence that `pattern` matches, or a failure naming it."""

    # regex: a search for one sentence's figures through free prose, which no
    # parser reads; the caller's pattern names the sentence's fixed words.
    matches = re.findall(pattern, _supported_ranges_text() if text is None else text)
    assert len(matches) == 1, (
        f"expected one sentence matching {pattern!r} in the section, found {matches}. If "
        "the sentence was reworded, update the pattern here so the figure stays checked."
    )
    found = matches[0]

    return found if isinstance(found, tuple) else (found,)


def _as_printed(value: float, printed: str) -> str:
    """`value` to as many decimal places as `printed` has."""

    places = len(printed.split(".")[1]) if "." in printed else 0

    return f"{value:.{places}f}"


def _five_minute_figures(text: str) -> dict[float, str]:
    """Each cardiac output in L/min that the sentence names, with its printed $F_A/F_I$.

    The sentence lists pairs such as "0.60 at 10 L/min" and ends with "0.96 at
    zero", which is a cardiac output of 0 L/min.
    """

    (listed,) = _one(r"at five minutes is (.*? at zero)", text)
    # regex: each "ratio at flow" pair in the one sentence the caller found.
    pairs = re.findall(r"(\d\.\d+) at (zero|\d+(?:\.\d+)? L/min)", listed)

    return {
        0.0 if flow == "zero" else float(flow.removesuffix(" L/min")): ratio
        for ratio, flow in pairs
    }


def _alveolar_over_inspired_at_five_minutes(cardiac_output_l_min: float) -> float:
    """$F_A/F_I$ five minutes into a sevoflurane wash-in from zero agent.

    Every setting but the cardiac output is the agent's default, which is
    the reference adult's ventilation, the reference circuit's fresh gas flow
    and the agent's 1 MAC on the dial. The run starts with no agent anywhere,
    so the ratio does not depend on the dial setting: the model is linear in
    the delivered fraction.
    """

    system = AgentUptakeSystem.for_agent(SEVOFLURANE)
    system.set_cardiac_output(CardiacOutput(cardiac_output_l_min))
    no_agent = tuple(1.0 if index == UNIT_STATE else 0.0 for index in range(STATE_SIZE))
    (state,) = predicted_states_at(
        system.equation_settings(), no_agent, CaseInstant(0), (CaseInstant(FIVE_MINUTES_S),)
    )

    return state[ALVEOLAR_FRACTION] / state[INSPIRED_FRACTION]


def test_alveolar_wash_in_at_five_minutes_quickens_as_cardiac_output_falls() -> None:
    """$F_A/F_I$ at five minutes is the figure printed at each of five cardiac outputs.

    The figures are the reason the section gives for supporting zero cardiac
    output, and `docs/MODEL.md` § "The four controls" states them again for a
    clinician. Both statements must list the same five pairs. Each figure is
    compared with a run of the model at that cardiac output, at the two
    decimals printed. The test also checks the direction the figures teach:
    the lower the cardiac output, the higher the ratio.
    """

    interface = _five_minute_figures(_supported_ranges_text())
    model = _five_minute_figures(_section(MODEL_PATH, FOUR_CONTROLS_HEADING))

    assert interface == model, (
        f"docs/INTERFACE.md prints {interface} and docs/MODEL.md prints {model}"
    )
    assert len(interface) == 5, f"expected five cardiac outputs, found {sorted(interface)}"
    computed = {flow: _alveolar_over_inspired_at_five_minutes(flow) for flow in interface}
    for flow, printed in interface.items():
        assert _as_printed(computed[flow], printed) == printed, (
            f"at a cardiac output of {flow} L/min, F_A/F_I at five minutes is "
            f"{computed[flow]:.4f}, not {printed}"
        )
    by_falling_flow = [computed[flow] for flow in sorted(computed, reverse=True)]
    assert by_falling_flow == sorted(by_falling_flow)


def test_a_long_sevoflurane_run_leaves_the_measured_exposure_range_as_printed() -> None:
    """The hours and MAC-hours that place a long run outside the measured exposure range.

    The paragraph takes the top of the measured range, 9.5 MAC-hours, from
    Kharasch's review, so this test reads it from the text. It then checks
    three pieces of arithmetic on it. A run held at 1 MAC end-tidal gains one
    MAC-hour per hour, so it leaves the range after as many hours as the
    range's top, and reaches as many MAC-hours as the run length has hours.
    Sevoflurane's vaporizer maximum over its MAC is the multiple printed, and
    a run held at that maximum for the whole run length reaches the most
    MAC-hours printed. The maximum, the MAC and the run length come from the
    data file and from `core/supported_ranges.py`, not from the text.
    """

    agent = load_agent_parameters(SEVOFLURANE)
    run_length_h = MAXIMUM_ELAPSED_SIMULATION_TIME_S / SECONDS_PER_HOUR
    _lowest, highest = _one(r"over (\d+\.\d+) to (\d+\.\d) MAC-hours only")
    leaves_h, at_limit = _one(
        r"leaves the measured range at about (\d+\.\d) hours, and reaches about (\d+) "
        r"MAC-hours at the limit"
    )
    maximum, multiple, mac = _one(
        r"vaporizer delivers at most (\d+)%, (\d+\.\d) times its (\d+\.\d+)% MAC"
    )
    (most,) = _one(r"reaches at most about (\d+) MAC-hours")
    one_mac_hour_per_hour = 1.0

    assert _as_printed(float(highest) / one_mac_hour_per_hour, leaves_h) == leaves_h
    assert _as_printed(run_length_h * one_mac_hour_per_hour, at_limit) == at_limit
    assert float(maximum) == agent.max_delivered_concentration_percent
    assert float(mac) == agent.mac_at_age_40_percent
    dial_multiple = agent.max_delivered_concentration_percent / agent.mac_at_age_40_percent
    assert _as_printed(dial_multiple, multiple) == multiple
    assert _as_printed(dial_multiple * run_length_h, most) == most


def _isolated_fat_time_constant_h(agent_id: str) -> float:
    """The fat group's isolated time constant on the reference adult, in hours.

    `docs/MODEL.md` § "Tissue groups" defines it as $V_i\\lambda_{i:b}/Q_i$,
    where the tissue:blood coefficient is the stored tissue:gas coefficient
    over the stored blood:gas one, and the group's flow is its perfusion
    fraction of the reference adult's cardiac output.
    """

    agent = load_agent_parameters(agent_id)
    patient = load_reference_adult_parameters()
    tissue_blood = (
        agent.fat_tissue_gas_partition_coefficient / agent.blood_gas_partition_coefficient
    )
    flow_l_min = patient.fat_perfusion_fraction * patient.default_cardiac_output_l_min

    return patient.fat_volume_l * tissue_blood / flow_l_min / MINUTES_PER_HOUR


def test_the_run_length_is_the_fraction_of_the_fat_time_constant_printed() -> None:
    """24 hours is about 0.6 of sevoflurane's fat time constant of about 42 h.

    The time constant is computed from the stored parameters by the
    definition in `docs/MODEL.md` § "Tissue groups". The paragraph then says
    that a single compartment filling exponentially has gone "a little over two
    fifths" of the way to equilibrium by the end of the run. That is
    $1 - e^{-t/\\tau}$, and the test reads the phrase as a value above 0.40
    and below 0.45. The 0.45 is this test's reading of "a little over", not a
    numerical limit: at 0.45 the text would say "nearly half".
    """

    (time_constant,) = _one(r"isolated time constant of about (\d+) h")
    run_length, fraction = _one(r"(\d+) hours is about (\d\.\d) of the isolated time constant")
    tau_h = _isolated_fat_time_constant_h(SEVOFLURANE)
    run_length_h = MAXIMUM_ELAPSED_SIMULATION_TIME_S / SECONDS_PER_HOUR
    filled = 1.0 - math.exp(-run_length_h / tau_h)

    assert float(run_length) == run_length_h
    assert _as_printed(tau_h, time_constant) == time_constant
    assert _as_printed(run_length_h / tau_h, fraction) == fraction
    assert 0.40 < filled < 0.45, f"a single exponential has gone {filled:.3f} of the way"
