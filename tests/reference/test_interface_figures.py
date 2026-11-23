"""The figures in `docs/INTERFACE.md` that no other test computed follow from the code and data.

`docs/INTERFACE.md` argues for what the interface shows with figures: how
wide the height band of a mark is, what a band or a container takes of a
plot, what a percent means in MAC multiples, and what fat holds in a run.
A reader takes each figure on trust. Before `PL-JP7P`, no test computed the
ones in this module, and four of them were wrong. The hover's worked examples
divided by a 1 MAC of 2.0% that sevoflurane no longer has, and the fat values
of a branched run were from a run at that MAC.

Each test reads its figures from the document as printed, with a narrow
pattern for the sentence that states them, as
`test_supported_input_range_figures.py` does. It computes them independently,
from the stored parameters through the loaders, from the display constants,
or from a run of the model built directly at the stated settings. It compares
the two at the precision the document prints. So a change to the model, a
data file or a display constant that moves a figure fails here, and so does
an edit to the text that changes a figure without changing what it came from.
"""

import re
from functools import cache
from pathlib import Path

import contrast_check

from anesthesia_sim.app.chart_frame import COMPARTMENT_TRACES
from anesthesia_sim.app.chart_time_base import TIME_BASE_LADDER
from anesthesia_sim.app.formatting import (
    CHART_AXIS_TOP_MAC,
    MAC_DISPLAY_RESOLUTION_MAC,
    chart_axis_top_percent,
    format_mac_multiple,
    format_percent,
)
from anesthesia_sim.app.theme import PANEL
from anesthesia_sim.core.concentration import Fraction, MacPercent, Percent
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.rounding import HEIGHT_BAND
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

INTERFACE_PATH = Path(__file__).resolve().parents[2] / "docs" / "INTERFACE.md"

AGENTS = ("sevoflurane", "isoflurane", "desflurane")
SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600
MINUTES_PER_HOUR = 60.0

#: The words the document uses for small whole numbers and simple fractions.
NUMBER_WORDS = {"three": 3, "five": 5, "twelve": 12}
FRACTION_WORDS = {"third": 3, "quarter": 4, "fifth": 5}


@cache
def _section(heading: str) -> str:
    """The text under `heading`, to the next heading at its depth or shallower,
    with each run of whitespace made one space."""

    text = INTERFACE_PATH.read_text(encoding="utf-8")
    start = text.index(f"\n{heading}\n")
    depth = len(heading.split(" ", 1)[0])
    # regex: the next markdown heading at this depth or shallower, a fixed
    # line shape.
    after = re.search(rf"\n#{{1,{depth}}} ", text[start + len(heading) + 1 :])
    end = start + len(heading) + 1 + after.start() if after else len(text)

    return " ".join(text[start:end].split())


def _one(heading: str, pattern: str) -> tuple[str, ...]:
    """The groups of the one sentence under `heading` that `pattern` matches."""

    # regex: a search for one sentence's figures through free prose, which no
    # parser reads; the caller's pattern names the sentence's fixed words.
    matches = re.findall(pattern, _section(heading))
    assert len(matches) == 1, (
        f"expected one sentence matching {pattern!r} under {heading!r}, found {matches}. If "
        "the sentence was reworded, update the pattern here so the figure stays checked."
    )
    found = matches[0]

    return found if isinstance(found, tuple) else (found,)


def _as_printed(value: float, printed: str) -> str:
    """`value` to as many decimal places as `printed` has."""

    places = len(printed.split(".")[1]) if "." in printed else 0

    return f"{value:.{places}f}"


def _mac_percent(agent_id: str) -> MacPercent:
    return MacPercent(float(load_agent_parameters(agent_id).mac_at_age_40_percent))


def _isolated_time_constant_min(agent_id: str, group: str) -> float:
    """A tissue group's isolated time constant on the reference adult, in minutes.

    `docs/MODEL.md` § "Tissue groups" defines it as $V_i\\lambda_{i:b}/Q_i$.
    The tissue:blood coefficient is the stored tissue:gas coefficient over
    the stored blood:gas one. The group's flow is its perfusion fraction of
    the reference adult's cardiac output.
    """

    agent = load_agent_parameters(agent_id)
    patient = load_reference_adult_parameters()
    tissue_gas = getattr(agent, f"{group}_tissue_gas_partition_coefficient")
    tissue_blood = tissue_gas / agent.blood_gas_partition_coefficient
    flow_l_min = getattr(patient, f"{group}_perfusion_fraction") * (
        patient.default_cardiac_output_l_min
    )

    return getattr(patient, f"{group}_volume_l") * tissue_blood / flow_l_min


def _nearest_unit_fraction(share: float) -> int:
    """The `n` of the unit fraction 1/n nearest to `share`, such as 5 for a fifth."""

    return round(1.0 / share)


def test_a_mark_s_height_band_is_finer_than_the_mac_readout_by_the_factor_printed() -> None:
    """The band is one part in 100 000 each side, about 500 times finer than 0.01 ×MAC.

    The band's full width at 1 MAC is twice `HEIGHT_BAND` of 1 MAC. The
    readout's step near 1 MAC is `MAC_DISPLAY_RESOLUTION_MAC`. The text
    rounds their ratio to a whole number of hundreds.
    """

    (hundreds,) = _one(
        "### Halting on a marked crossing",
        r"one part in a hundred thousand of the height on either side, about (\w+) hundred "
        r"times finer than a two-decimal readout near 1 MAC",
    )

    assert HEIGHT_BAND == 1.0 / 100_000
    ratio = MAC_DISPLAY_RESOLUTION_MAC / (2.0 * HEIGHT_BAND * 1.0)
    assert round(ratio / 100.0) == NUMBER_WORDS[hundreds], f"the ratio is {ratio:.1f}"


def test_the_isolated_time_constants_are_the_ones_printed() -> None:
    """Sevoflurane's muscle and fat time constants are about 135 min and 42 h.

    Two sections print them. Each is compared at the whole number printed.
    """

    muscle_min = _isolated_time_constant_min("sevoflurane", "muscle")
    fat_h = _isolated_time_constant_min("sevoflurane", "fat") / MINUTES_PER_HOUR

    for heading, pattern in (
        (
            "### What the reader chooses: traces, window and playback rate",
            r"isolated time constant is about (\d+) min for the muscle group and about (\d+) h "
            r"for fat",
        ),
        (
            "### The chart's time base",
            r"isolated time constant is about (\d+) min for muscle and about (\d+) h for fat",
        ),
    ):
        muscle, fat = _one(heading, pattern)
        assert (_as_printed(muscle_min, muscle), _as_printed(fat_h, fat)) == (muscle, fat), heading


def test_the_widest_window_shows_an_induction_and_a_minute_grid_as_printed() -> None:
    """A five-minute induction takes 0.7% of a twelve-hour plot, and a 60 s grid 720 lines."""

    widest_s = TIME_BASE_LADDER[-1].span_s
    (share,) = _one(
        "### The chart's time base",
        r"A twelve-hour window puts a five-minute induction in the leftmost (\d\.\d)% of the plot",
    )
    interval, lines = _one(
        "### The chart's time base",
        r"The (\d+) s interval used before would draw (\d+) gridlines across a twelve-hour axis",
    )

    assert widest_s == NUMBER_WORDS["twelve"] * SECONDS_PER_HOUR
    assert _as_printed(5 * SECONDS_PER_MINUTE / widest_s * 100.0, share) == share
    assert widest_s / float(interval) == float(lines)


def test_the_mac_awake_band_takes_the_share_of_the_plot_printed() -> None:
    """The band is one standard deviation each side of its centre, over the axis's MAC span.

    On the 3 ×MAC axis that is 3.33% of the plot for sevoflurane and 4.20% for
    desflurane, and on a 4 MAC axis 2.50% for sevoflurane.
    """

    heading = "### MAC-awake as a chart reference"
    sevoflurane, desflurane = _one(
        heading,
        r"the band spans (\d\.\d\d)% of the plot height for sevoflurane and (\d\.\d\d)% for "
        r"desflurane",
    )
    ceiling, at_ceiling = _one(heading, r"A (\d) MAC ceiling would shrink the band to (\d\.\d\d)%")

    def share(agent_id: str, axis_top_mac: float) -> float:
        width_mac = (
            2.0 * load_agent_parameters(agent_id).mac_awake.standard_deviation_fraction_of_mac
        )

        return float(width_mac) / axis_top_mac * 100.0

    assert _as_printed(share("sevoflurane", CHART_AXIS_TOP_MAC), sevoflurane) == sevoflurane
    assert _as_printed(share("desflurane", CHART_AXIS_TOP_MAC), desflurane) == desflurane
    assert _as_printed(share("sevoflurane", float(ceiling)), at_ceiling) == at_ceiling


def test_the_dial_maxima_are_the_mac_multiples_printed() -> None:
    """Each dial maximum over the agent's 1 MAC, and desflurane's axis top, are as printed.

    1.8% is a quarter of a MAC of desflurane, to the nearest quarter. 8%
    sevoflurane is 4.44 ×MAC, 18% desflurane is 2.73 ×MAC, and desflurane's
    3 ×MAC axis tops out at 19.8%. Desflurane's maximum is the lowest of the
    three agents' multiples, which is what "the most limited" means.
    """

    heading = "#### The chart's fixed MAC axis"
    sevoflurane_dial, sevoflurane_mac = _one(
        heading, r"sevoflurane's (\d+)% dial setting, which is (\d\.\d\d) ×MAC"
    )
    desflurane_dial, desflurane_mac, desflurane_top = _one(
        heading,
        r"Its (\d+)% maximum is (\d\.\d\d) ×MAC, so desflurane's plot has an empty band from "
        r"\d+% to its (\d+\.\d)% top",
    )
    lowest, highest = _one(
        heading,
        r"the dial maxima run from (\d\.\d\d) ×MAC for desflurane to (\d\.\d\d) ×MAC for "
        r"sevoflurane",
    )
    multiples = {
        agent_id: float(load_agent_parameters(agent_id).max_delivered_concentration_percent)
        / _mac_percent(agent_id)
        for agent_id in AGENTS
    }

    for agent_id, dial in (("sevoflurane", sevoflurane_dial), ("desflurane", desflurane_dial)):
        assert float(load_agent_parameters(agent_id).max_delivered_concentration_percent) == float(
            dial
        )
    assert _as_printed(multiples["sevoflurane"], sevoflurane_mac) == sevoflurane_mac
    assert _as_printed(multiples["desflurane"], desflurane_mac) == desflurane_mac
    assert (lowest, highest) == (desflurane_mac, sevoflurane_mac)
    assert min(multiples, key=multiples.__getitem__) == "desflurane"
    assert max(multiples, key=multiples.__getitem__) == "sevoflurane"
    top = chart_axis_top_percent(_mac_percent("desflurane"))
    assert _as_printed(top, desflurane_top) == desflurane_top

    (fraction,) = _one(
        "### MAC multiples as a display unit",
        r"1\.8% is 1 MAC of sevoflurane and about a (\w+) of a MAC of desflurane",
    )
    assert float(_mac_percent("sevoflurane")) == 1.8
    share = 1.8 / _mac_percent("desflurane")
    assert round(share * FRACTION_WORDS[fraction]) == 1, f"1.8% is {share:.3f} MAC of desflurane"


def test_the_hover_s_percent_is_the_mac_multiples_printed() -> None:
    """1.43% is 0.79 MAC of sevoflurane and 0.22 MAC of desflurane, as the readout rounds them."""

    percent, sevoflurane, desflurane = _one(
        "#### What it shows",
        r"(\d\.\d\d)% is (\d\.\d\d) MAC of sevoflurane and (\d\.\d\d) MAC of desflurane",
    )
    fraction = Fraction(float(percent) / 100.0)

    assert format_mac_multiple(fraction, _mac_percent("sevoflurane")) == f"{sevoflurane} ×MAC"
    assert format_mac_multiple(fraction, _mac_percent("desflurane")) == f"{desflurane} ×MAC"


def _fat_after_a_fork(fork_s: int, instant_s: int) -> tuple[float, float]:
    """Fat's fraction at `instant_s` in a sevoflurane trunk at 1 MAC and in a branch of it.

    The trunk keeps the vaporizer at the agent's stored 1 MAC, with the
    default flows. The branch starts from the trunk's state at `fork_s` and
    turns the vaporizer off. Both are built here, step by step, without the
    controller that the interface uses to branch.
    """

    trunk = AgentUptakeSystem.for_agent("sevoflurane")
    assert trunk.circuit.delivered_concentration_percent == float(_mac_percent("sevoflurane"))
    for _ in range(fork_s):
        trunk.advance()
    branch = AgentUptakeSystem.for_agent("sevoflurane")
    branch.restore_state(trunk.capture_state())
    branch.set_delivered_concentration_percent(Percent(0.0))
    for _ in range(instant_s - fork_s):
        trunk.advance()
        branch.advance()

    return trunk.patient.fat.partial_pressure_fraction, branch.patient.fat.partial_pressure_fraction


def test_the_hover_s_fat_values_after_a_fork_are_the_ones_printed() -> None:
    """At 3492 s the trunk's fat holds 0.028% and the branch's 0.005%, shown as 0.03% and 0.01%."""

    heading = "#### The hover and the run it belongs to"
    (fork_min,) = _one(heading, r"The branch is a second run forked from it at (\d+) min")
    instant_s, trunk_shown, branch_shown = _one(
        heading, r"At (\d+) s the fat value reads either `([^`]+)` or `([^`]+)`"
    )
    trunk_modelled, branch_modelled = _one(
        heading, r"The modelled values are (\d\.\d+)% and (\d\.\d+)%"
    )
    stored_fold, shown_fold = _one(
        heading, r"about a (\w+)fold difference in stored agent that the box shows as (\w+)fold"
    )
    (emergence_min,) = _one(heading, r"a run (\d+) minutes into emergence")
    fork_s = int(fork_min) * SECONDS_PER_MINUTE
    trunk, branch = _fat_after_a_fork(fork_s, int(instant_s))
    mac = _mac_percent("sevoflurane")

    def shown(fraction: float) -> str:
        """The box's value line, with its spaces made one, as the section is read."""

        line = (
            f"{format_percent(Fraction(fraction))}   {format_mac_multiple(Fraction(fraction), mac)}"
        )

        return " ".join(line.split())

    assert (shown(trunk), shown(branch)) == (trunk_shown, branch_shown)
    assert _as_printed(trunk * 100.0, trunk_modelled) == trunk_modelled
    assert _as_printed(branch * 100.0, branch_modelled) == branch_modelled
    assert round(trunk / branch) == NUMBER_WORDS[stored_fold], f"the ratio is {trunk / branch:.2f}"
    shown_ratio = float(format_percent(Fraction(trunk)).rstrip("%")) / float(
        format_percent(Fraction(branch)).rstrip("%")
    )
    assert round(shown_ratio) == NUMBER_WORDS[shown_fold]
    assert (int(instant_s) - fork_s) // SECONDS_PER_MINUTE == int(emergence_min)


def test_fat_holds_the_share_printed_while_its_container_stays_nearly_empty() -> None:
    """At a 1 MAC dial fat holds about a fifth of the agent at one hour and a third at three.

    The share is fat's amount over the run's total stored agent. The fill is
    fat's percent over the top of the scale, which is the concentration
    chart's top of 3 MAC. The sevoflurane sentence also prints fat's tension
    at one hour and a bound on its fill.
    """

    heading = "### The compartment schematic: what its heights, amounts and share bar assert"
    minutes, fifth, tension, fill_bound = _one(
        heading,
        r"At (\d+) min in a run with sevoflurane at a 1 MAC dial, fat holds a (\w+) of all the "
        r"agent in the run, but its tension of (\d\.\d+)% atm fills less than (\d+)% of its "
        r"container's height",
    )
    at_one_hour, at_three_hours = _one(
        heading,
        r"across the simulator's three agents, fat holds a (\w+) of the stored agent at one hour "
        r"and a (\w+) at three hours",
    )
    one_hour_s = int(minutes) * SECONDS_PER_MINUTE
    assert one_hour_s == SECONDS_PER_HOUR

    for agent_id in AGENTS:
        system = AgentUptakeSystem.for_agent(agent_id)
        assert system.circuit.delivered_concentration_percent == float(_mac_percent(agent_id))
        for elapsed_s in range(1, 3 * SECONDS_PER_HOUR + 1):
            system.advance()
            fat = system.patient.fat
            share = fat.agent_amount_l / system.total_stored_agent_l
            if elapsed_s == one_hour_s:
                assert _nearest_unit_fraction(share) == FRACTION_WORDS[at_one_hour], agent_id
                if agent_id == "sevoflurane":
                    assert _nearest_unit_fraction(share) == FRACTION_WORDS[fifth]
                    percent = fat.partial_pressure_fraction * 100.0
                    assert _as_printed(percent, tension) == tension
                    top = chart_axis_top_percent(_mac_percent(agent_id))
                    assert percent / top * 100.0 < float(fill_bound)
        assert _nearest_unit_fraction(share) == FRACTION_WORDS[at_three_hours], agent_id


def test_the_circuit_goes_off_the_schematic_s_scale_at_the_dial_maximum() -> None:
    """At its 8% maximum the sevoflurane circuit passes the 3 MAC top on its way to 4.44 ×MAC.

    The run uses the default flows. Ten minutes is long enough for the
    circuit to pass the top and short of the dial's own multiple.
    """

    dial, multiple = _one(
        "### The compartment schematic: what its heights, amounts and share bar assert",
        r"The circuit rises above the top, towards (\d\.\d\d) ×MAC, when a sevoflurane dial "
        r"is at its (\d+)% maximum",
    )[::-1]
    agent = load_agent_parameters("sevoflurane")
    mac = _mac_percent("sevoflurane")
    assert float(agent.max_delivered_concentration_percent) == float(dial)
    assert _as_printed(float(dial) / mac, multiple) == multiple

    system = AgentUptakeSystem.for_agent("sevoflurane")
    system.set_delivered_concentration_percent(Percent(float(dial)))
    for _ in range(10 * SECONDS_PER_MINUTE):
        system.advance()
    circuit_mac = system.circuit.inspired_partial_pressure_fraction * 100.0 / mac

    assert CHART_AXIS_TOP_MAC < circuit_mac < float(multiple)


def test_the_vapour_per_liquid_figures_are_the_derived_ratios() -> None:
    """1 mL of liquid gives about 183, 196 and 210 mL of vapour, so about 180 to 210.

    Each ratio is derived from the agent's stored density and molar mass at
    20 °C, which `test_published_vapour_to_liquid.py` holds to published
    constants. The text rounds each to a whole millilitre, and the range to
    tens.
    """

    ratios = {
        agent_id: float(load_agent_parameters(agent_id).vapour_volume_per_liquid_volume)
        for agent_id in AGENTS
    }
    (isoflurane,) = _one(
        "#### What the cost readout shows",
        r"One millilitre of liquid isoflurane gives about (\d+) mL of vapour",
    )
    schematic = "### The compartment schematic: what its heights, amounts and share bar assert"
    low, high = _one(
        schematic, r"differ by a factor of about (\d+) to (\d+), depending on the agent"
    )
    sevoflurane, desflurane = _one(
        schematic,
        r"1 mL of liquid gives about (\d+) mL of sevoflurane vapour or about (\d+) mL of "
        r"desflurane vapour",
    )

    assert str(round(ratios["isoflurane"])) == isoflurane
    assert str(round(ratios["sevoflurane"])) == sevoflurane
    assert str(round(ratios["desflurane"])) == desflurane
    assert (round(min(ratios.values()), -1), round(max(ratios.values()), -1)) == (
        float(low),
        float(high),
    )


def test_fat_s_container_drawn_to_scale_takes_the_width_printed() -> None:
    """Drawn with width in proportion to capacity, fat takes about 500 of 600 px for sevoflurane.

    A container whose width is its capacity holds an amount equal to its
    filled area. The capacity of the circuit and the alveoli is their gas
    volume, and that of blood and tissue is their volume times their gas
    partition coefficient, as each compartment reports it. The four smallest
    of the other five containers round to whole pixels in the range printed.
    """

    fat_px, view_px, smallest, largest = _one(
        "### The compartment schematic: what its heights, amounts and share bar assert",
        r"fat's container drawn to scale would take about (\d+) px of a View (\d+) px wide, and "
        r"four of the others would take between (\d+) and (\d+) px each",
    )
    system = AgentUptakeSystem.for_agent("sevoflurane")
    patient = system.patient
    capacities = {
        "circuit": system.circuit.circuit_volume_l,
        "alveoli": system.alveoli.gas_volume_l,
        "venous blood": patient.venous_blood.capacity_l,
        "vessel-rich": patient.vessel_rich.capacity_l,
        "muscle": patient.muscle.capacity_l,
        "fat": patient.fat.capacity_l,
    }
    total = sum(capacities.values())
    widths = {name: capacity / total * float(view_px) for name, capacity in capacities.items()}
    others = sorted(width for name, width in widths.items() if name != "fat")[:4]

    assert round(widths["fat"], -2) == float(fat_px), f"fat takes {widths['fat']:.1f} px"
    assert (round(others[0]), round(others[-1])) == (int(smallest), int(largest)), others


def test_a_swapped_bottle_price_and_volume_moves_the_cost_by_the_share_printed() -> None:
    """At 240.34 per 250 mL, typing each in the other's field changes the cost by 8%.

    The price per millilitre is the bottle price over the bottle volume, so
    a swap multiplies it by the square of their ratio.
    """

    price, volume, change = _one(
        "#### Setting a price",
        r"At Gas Man's sevoflurane default of (\d+\.\d+) for a (\d+) mL bottle .*? a swap changes "
        r"the cost by (\d+) %",
    )
    right = float(price) / float(volume)
    swapped = float(volume) / float(price)

    assert _as_printed(abs(swapped / right - 1.0) * 100.0, change) == change


def test_the_figures_shown_beside_a_cost_multiply_as_printed() -> None:
    """The rounded liquid volume times the price per millilitre gives the products printed.

    The cost itself is computed from the unrounded figures, which
    `test_the_cost_is_computed_from_the_unrounded_figures_not_the_ones_shown`
    in `tests/unit/test_agent_cost.py` checks. This test checks the
    arithmetic the paragraph prints, and each price per millilitre against
    its bottle.
    """

    heading = "#### What the cost readout shows"
    shown_ml, per_ml, product = _one(
        heading, r"In the example above, (\d+) mL times USD (\d\.\d+) is USD (\d+\.\d\d)"
    )
    bottle, bottle_ml, desflurane_ml, desflurane_per_ml, desflurane_product = _one(
        heading,
        r"At USD (\d+\.\d\d) per (\d+) mL bottle, .*? Shown as (\d+) mL and USD (\d\.\d+) per mL, "
        r"the two figures multiply to USD (\d+\.\d\d)",
    )

    assert f"{float(shown_ml) * float(per_ml):.2f}" == product
    assert _as_printed(float(bottle) / float(bottle_ml), desflurane_per_ml) == desflurane_per_ml
    assert f"{float(desflurane_ml) * float(desflurane_per_ml):.2f}" == desflurane_product


def test_the_costs_beside_the_rounded_figures_are_the_unrounded_products() -> None:
    """Exercise 14-1's 60 min and the desflurane example cost what the section prints.

    Each delivered amount is worked out by hand: the dial's fraction times
    the fresh gas flow times the time is the vapour delivered, and the
    agent's stored vapour-to-liquid ratio turns it into liquid. Exercise 14-1
    of the *Workbook for Gas Man* runs isoflurane at 2 % and 8 L/min for
    13 min, then at 1.5 % for 47 min (printed pp. 133-134). The price per
    millilitre is the section's own.
    """

    heading = "#### What the cost readout shows"
    per_ml, cost, unrounded_ml = _one(
        heading,
        r"(\d\.\d+) is USD \d+\.\d\d\. The cost is USD (\d+\.\d\d) because it uses the "
        r"unrounded (\d+\.\d\d) mL",
    )
    bottle, bottle_ml, minutes, percent, flow, desflurane_cost, desflurane_ml = _one(
        heading,
        r"At USD (\d+\.\d\d) per (\d+) mL bottle, (\d+) min of desflurane at (\d+) % and "
        r"(\d+) L/min costs USD (\d+\.\d\d)\. Shown as (\d+) mL",
    )
    isoflurane_vapour_ml = (0.02 * 13.0 + 0.015 * 47.0) * 8.0 * 1000.0
    isoflurane_ml = isoflurane_vapour_ml / float(
        load_agent_parameters("isoflurane").vapour_volume_per_liquid_volume
    )
    desflurane_vapour_ml = float(percent) / 100.0 * float(flow) * float(minutes) * 1000.0
    desflurane_liquid_ml = desflurane_vapour_ml / float(
        load_agent_parameters("desflurane").vapour_volume_per_liquid_volume
    )

    assert f"{isoflurane_ml:.2f}" == unrounded_ml
    assert f"{isoflurane_ml * float(per_ml):.2f}" == cost
    assert f"{desflurane_liquid_ml:.0f}" == desflurane_ml
    assert f"{desflurane_liquid_ml * float(bottle) / float(bottle_ml):.2f}" == desflurane_cost


def test_the_trace_colour_tables_are_what_the_palette_gives() -> None:
    """Every contrast in the two tables of the trace section is the palette's, as printed.

    The first table gives each trace against the panel, and the second each
    pair of traces, under normal vision and three simulated dichromacies,
    with the worst of the four. The contrast and the simulation are
    `tools/contrast_check.py`'s, which `make check` runs against the palette.
    The gridline paragraph's 87% is 3:1 over the lightest trace's contrast as
    displayed.
    """

    text = _section("### The six compartment traces: what separates them")
    colours = {style.label: style.color for style in COMPARTMENT_TRACES}
    names = "|".join(re.escape(label) for label in colours)
    models = contrast_check.VISION_MODELS
    assert models == ("normal", "protanopia", "deuteranopia", "tritanopia")

    def contrast(first: str, second: str, model: str) -> float:
        return contrast_check.contrast_ratio(
            contrast_check.as_seen(first, model), contrast_check.as_seen(second, model)
        )

    def printed_as(computed: list[float], printed: list[str]) -> list[str]:
        return [_as_printed(value, cell) for value, cell in zip(computed, printed, strict=True)]

    # regex: one trace row, a fixed shape of pipe-separated cells.
    single = re.findall(
        rf"\| ({names}) \| `(#[0-9A-Fa-f]{{6}})` \| (\d\.\d\d) \| (\d\.\d\d) \| (\d\.\d\d) \| "
        r"(\d\.\d\d) \|",
        text,
    )
    assert len(single) == len(colours), "the first table has one row per trace"
    for label, written, *printed in single:
        assert colours[label].upper() == written.upper(), label
        computed = [contrast(written, PANEL, model) for model in models]
        assert printed_as(computed, printed) == printed, label

    # regex: one pair row, a fixed shape of pipe-separated cells.
    pairs = re.findall(
        rf"\| ({names}) / ({names}) \| (\d\.\d\d) \| (\d\.\d\d) \| (\d\.\d\d) \| "
        r"(\d\.\d\d) \| \*\*(\d\.\d\d)\*\* \|",
        text,
    )
    assert len(pairs) == 15, "six traces make fifteen pairs"
    for first, second, *printed in pairs:
        computed = [contrast(colours[first], colours[second], model) for model in models]
        computed.append(min(computed))
        assert printed_as(computed, printed) == printed, f"{first} / {second}"

    muscle, mixed_venous_pair = _one(
        "### The six compartment traces: what separates them",
        r"second most widely separated pair among these six \((\d\.\d\d) in the table below, "
        r"after circuit and alveolar at (\d\.\d\d)\)",
    )
    worst = {f"{first} / {second}": float(printed[-1]) for first, second, *printed in pairs}
    ranked = sorted(worst.values(), reverse=True)
    assert (worst["Mixed venous / Muscle"], worst["Circuit / Alveolar"]) == (
        float(muscle),
        float(mixed_venous_pair),
    )
    assert ranked[:2] == [float(mixed_venous_pair), float(muscle)]

    share, lightest = _one(
        "#### The exempt gridline grey",
        r"A gridline at 3:1 would be (\d+)% as dark as the lightest trace \((\d\.\d\d):1\)",
    )
    lightest_contrast = min(contrast(colour, PANEL, "normal") for colour in colours.values())
    assert _as_printed(lightest_contrast, lightest) == lightest
    assert str(round(contrast_check.AA_NON_TEXT / lightest_contrast * 100.0)) == share
