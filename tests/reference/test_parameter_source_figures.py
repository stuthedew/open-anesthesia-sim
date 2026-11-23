"""The arithmetic in `docs/PARAMETERS.md`'s account of the stored partition coefficients and MAC.

Three parts of that document compare a stored value with a published one and
print the result: § "Source hierarchy: what may be cited as the authority for
a value" and § "The blood:gas coefficients" for the blood:gas coefficients,
§ "v0.2.0: isoflurane and desflurane" for the tissue:gas coefficients against
Yasuda, Targ and Eger's Table 1, and § "The MAC-awake fractions" for the MAC
that the MAC-awake band is drawn on. This module redoes each comparison.

Each test reads the published inputs and the result from the text as printed,
takes the stored values from the data files through the loaders, and compares
the result at the number of decimal places the text prints. So a changed
stored value that moves a figure fails here, and so does an edit to the text
that changes a figure without changing its inputs. These tests check the
text's arithmetic. They cannot check that a published input was transcribed
correctly from its paper, which is the citation's job. The one exception is
the blood:gas measurements, which the text gives only as differences, so the
test states each measured mean beside the paper it comes from.
"""

import re
from functools import cache
from pathlib import Path

from anesthesia_sim.core.parameters import (
    MAC_STORED_AT_AGE_YEARS,
    AgentParameters,
    load_agent_parameters,
    load_reference_adult_parameters,
)

PARAMETERS_PATH = Path(__file__).resolve().parents[2] / "docs" / "PARAMETERS.md"

#: The words that stand for a count in the text, as the text spells them.
COUNT_WORDS = {"two": 2, "four": 4, "five": 5, "seven": 7}

#: Each agent's measured blood:gas means, as each agent file's note on the
#: source records them, mean ± SD at 37 °C. The older measurements are Strum
#: and Eger, Anesth Analg 1987;66(7):654-6, abstract, for sevoflurane;
#: Lerman et al., Anesthesiology 1984;61(2):139-43, abstract, adults aged 20 to
#: 40, for isoflurane; and Eger, Anesth Analg 1987;66(10):971-3, abstract, for
#: desflurane. Esper et al., Anesth Analg 2015;120(1):45-50, abstract, measured
#: all three in surgical patients.
OLDER_BLOOD_GAS_MEANS = {"sevoflurane": 0.686, "isoflurane": 1.46, "desflurane": 0.424}
ESPER_BLOOD_GAS_MEANS = {"sevoflurane": 0.74, "isoflurane": 1.45, "desflurane": 0.57}


@cache
def _text() -> str:
    """The whole of `docs/PARAMETERS.md`, with each run of whitespace made one space."""

    return " ".join(PARAMETERS_PATH.read_text(encoding="utf-8").split())


def _one(pattern: str) -> tuple[str, ...]:
    """The groups of the one sentence that `pattern` matches, or a failure naming it."""

    # regex: a search for one sentence's figures through free prose, which no
    # parser reads; the caller's pattern names the sentence's fixed words.
    matches = re.findall(pattern, _text())
    assert len(matches) == 1, (
        f"expected one sentence matching {pattern!r} in docs/PARAMETERS.md, found {matches}. "
        "If the sentence was reworded, update the pattern here so the figure stays checked."
    )
    found = matches[0]

    return found if isinstance(found, tuple) else (found,)


def _as_printed(value: float, printed: str) -> str:
    """`value` to as many decimal places as `printed` has."""

    places = len(printed.split(".")[1]) if "." in printed else 0

    return f"{value:.{places}f}"


def _agent(agent_id: str) -> AgentParameters:
    return load_agent_parameters(agent_id)


def _percent_below(stored: float, measured: float) -> float:
    return (1.0 - stored / measured) * 100.0


#: The agent rows of the table of Yasuda, Targ and Eger's Table 1 in
#: § "Where the tissue:gas coefficients come from", and its columns in order,
#: each named for the stored field.
YASUDA_TABLE_AGENTS = ("sevoflurane", "isoflurane", "desflurane")
YASUDA_TABLE_TISSUES = ("vessel_rich", "muscle", "fat")


@cache
def _yasuda_table() -> dict[tuple[str, str], tuple[float, float, float]]:
    """Each cell of the Yasuda table, as (stored, mean, SD).

    `test_known_limitations_figures.py` reads the same table in the same way.
    The reader is repeated here because one test module importing another
    makes the type checker see that module under two names.
    """

    cells: dict[tuple[str, str], tuple[float, float, float]] = {}
    for line in PARAMETERS_PATH.read_text(encoding="utf-8").splitlines():
        agent = line.split("|")[1].strip() if line.startswith("| ") else ""
        # regex: each "stored vs mean ± SD" cell of one markdown table row.
        found = re.findall(r"(\d+\.\d+) vs (\d+\.\d+) ± (\d+\.\d+)", line)
        if agent not in YASUDA_TABLE_AGENTS or not found:
            continue
        assert len(found) == len(YASUDA_TABLE_TISSUES), f"{agent}'s row has {found}"
        for tissue, (stored, mean, sd) in zip(YASUDA_TABLE_TISSUES, found, strict=True):
            cells[agent, tissue] = (float(stored), float(mean), float(sd))
    assert len(cells) == len(YASUDA_TABLE_AGENTS) * len(YASUDA_TABLE_TISSUES), (
        f"expected one row per agent in docs/PARAMETERS.md's Yasuda table, found {cells}"
    )

    return cells


def test_the_stored_blood_gas_coefficients_sit_below_the_measured_ones_as_printed() -> None:
    """Each stored blood:gas coefficient is below each measurement by the percent printed.

    § "The blood:gas coefficients" prints six differences, one per agent
    against the older measurement and one against Esper et al.'s mean. § "Source
    hierarchy" prints the range they span. Each is recomputed from the stored
    value and the measured mean.
    """

    agents = ("sevoflurane", "isoflurane", "desflurane")
    differences = r"sevoflurane −(\d+\.\d)%, isoflurane −(\d+\.\d)% and desflurane −(\d+\.\d)%"
    older = _one(rf"Against the older measurements the stored values are {differences}")
    esper = _one(rf"Against its means the stored values are {differences}")
    low, high = _one(r"the stored values are (\d+\.\d)% to (\d+\.\d)% below the measured ones")

    computed = []
    for printed_row, means in ((older, OLDER_BLOOD_GAS_MEANS), (esper, ESPER_BLOOD_GAS_MEANS)):
        for agent_id, printed in zip(agents, printed_row, strict=True):
            below = _percent_below(
                _agent(agent_id).blood_gas_partition_coefficient, means[agent_id]
            )
            computed.append(below)
            assert _as_printed(below, printed) == printed, (
                f"{agent_id}'s stored blood:gas is {below:.2f}% below {means[agent_id]}, "
                f"not {printed}%"
            )
    assert _as_printed(min(computed), low) == low
    assert _as_printed(max(computed), high) == high


def _signed_percent(stored: float, mean: float) -> float:
    return (stored / mean - 1.0) * 100.0


def test_the_stored_tissue_coefficients_lie_as_close_to_yasudas_means_as_printed() -> None:
    """How close the nine stored values lie to Yasuda's means, as the text under the table says.

    The paragraph makes four claims, each recomputed from the table's rows.
    The widest gap is 0.71 SD. Two values match the mean exactly. Two more
    lie within 1%, at the signed percents printed. The other five differ by
    the range printed, and the widest of them is isoflurane fat, above the
    mean.
    """

    table = _yasuda_table()
    (widest_sd,) = _one(r"All nine stored values lie within (\d\.\d+) SD of the measured mean")
    (exact,) = _one(r"(\w+) match it exactly")
    close, within, isoflurane_vessel_rich, sevoflurane_muscle = _one(
        r"(\w+) more lie within (\d+)% of it: isoflurane vessel-rich \(\+(\d\.\d)%\) and "
        r"sevoflurane muscle \(\+(\d\.\d)%\)"
    )
    others, low, high = _one(
        r"The other (\w+) differ from it by (\d\.\d)% to (\d\.\d)%, the most for isoflurane fat, "
        r"which lies above the mean"
    )
    sds = [abs(stored - mean) / sd for stored, mean, sd in table.values()]
    gaps = {cell: _signed_percent(stored, mean) for cell, (stored, mean, _sd) in table.items()}
    exact_cells = [cell for cell, (stored, mean, _sd) in table.items() if stored == mean]
    close_cells = {cell for cell, gap in gaps.items() if cell not in exact_cells and abs(gap) < 1}
    other_gaps = {
        cell: abs(gap) for cell, gap in gaps.items() if gap != 0 and cell not in close_cells
    }

    assert _as_printed(max(sds), widest_sd) == widest_sd
    assert len(exact_cells) == COUNT_WORDS[exact.lower()]
    assert float(within) == 1.0
    assert close_cells == {("isoflurane", "vessel_rich"), ("sevoflurane", "muscle")}
    assert len(close_cells) == COUNT_WORDS[close.lower()]
    assert _as_printed(gaps["isoflurane", "vessel_rich"], isoflurane_vessel_rich) == (
        isoflurane_vessel_rich
    )
    assert _as_printed(gaps["sevoflurane", "muscle"], sevoflurane_muscle) == sevoflurane_muscle
    assert len(other_gaps) == COUNT_WORDS[others]
    assert _as_printed(min(other_gaps.values()), low) == low
    assert _as_printed(max(other_gaps.values()), high) == high
    assert max(other_gaps, key=other_gaps.__getitem__) == ("isoflurane", "fat")
    assert gaps["isoflurane", "fat"] > 0


def test_the_vessel_rich_coefficients_match_yasudas_brain_values_as_printed() -> None:
    """Sevoflurane's stored vessel-rich value against Yasuda's four organs, and the two matches.

    The four organ values are read from the paragraph, which quotes them from
    Table 1. Sevoflurane's stored 1.1 is compared with its brain value and with
    the equal-weight mean of the four. Isoflurane's and desflurane's stored
    values are compared with their brain values in the table above the
    paragraph.
    """

    table = _yasuda_table()
    brain, heart, liver, kidney = (
        float(value)
        for value in _one(r"\(sevoflurane (\d\.\d+), (\d\.\d+), (\d\.\d+), (\d\.\d+)[;)]")
    )
    stored, below_brain, above_mean, mean = _one(
        r"Sevoflurane's stored (\d\.\d+) is (\d\.\d)% below its brain value and (\d\.\d)% above "
        r"the equal-weight mean of its four organ values, (\d\.\d+),"
    )
    isoflurane_stored, above_brain, isoflurane_brain, desflurane_stored = _one(
        r"Isoflurane's stored (\d\.\d+) is (\d\.\d)% above its brain value, (\d\.\d+), and "
        r"desflurane's stored (\d\.\d+) equals its brain value"
    )
    organ_mean = (brain + heart + liver + kidney) / 4.0

    assert brain == table["sevoflurane", "vessel_rich"][1]
    assert float(stored) == _agent("sevoflurane").vessel_rich_tissue_gas_partition_coefficient
    assert _as_printed(_percent_below(float(stored), brain), below_brain) == below_brain
    assert _as_printed(organ_mean, mean) == mean
    assert _as_printed(_signed_percent(float(stored), organ_mean), above_mean) == above_mean
    isoflurane = _agent("isoflurane").vessel_rich_tissue_gas_partition_coefficient
    assert float(isoflurane_stored) == isoflurane
    assert float(isoflurane_brain) == table["isoflurane", "vessel_rich"][1]
    assert _as_printed(_signed_percent(isoflurane, float(isoflurane_brain)), above_brain) == (
        above_brain
    )
    desflurane = _agent("desflurane").vessel_rich_tissue_gas_partition_coefficient
    assert float(desflurane_stored) == desflurane == table["desflurane", "vessel_rich"][1]


def _isolated_time_constant_min(agent_id: str, tissue: str, tissue_gas: float) -> float:
    """A tissue group's isolated time constant on the reference adult, in minutes.

    `docs/MODEL.md` § "Tissue groups" defines it as $V_i\\lambda_{i:b}/Q_i$. The
    tissue:blood coefficient is `tissue_gas` over the agent's stored blood:gas
    coefficient, and the flow is the group's perfusion fraction of the
    reference adult's cardiac output. Only the tissue:gas coefficient is
    passed in, so a test can put a published value in place of the stored one
    and keep everything else.
    """

    patient = load_reference_adult_parameters()
    volume_l = float(getattr(patient, f"{tissue}_volume_l"))
    fraction = float(getattr(patient, f"{tissue}_perfusion_fraction"))
    blood_gas = _agent(agent_id).blood_gas_partition_coefficient

    return volume_l * tissue_gas / blood_gas / (fraction * patient.default_cardiac_output_l_min)


def test_storing_yasudas_means_would_move_the_time_constants_as_printed() -> None:
    """The time-constant changes in the *Declined* paragraph, from a time constant's definition.

    Each change is the isolated time constant with Yasuda's mean in place of
    the stored tissue:gas coefficient, against the one with the stored value.
    Every other parameter is stored. The paragraph names three large changes
    with their coefficients, says how many values would change, and bounds
    the other four.
    """

    table = _yasuda_table()
    (changed,) = _one(r"would change (\w+) of the nine stored values")
    named = _one(
        r"Sevoflurane's vessel-rich time constant would move \+(\d\.\d)% \(coefficient "
        r"(\d\.\d+) instead of (\d\.\d+)\), isoflurane's fat −(\d\.\d)% \((\d+\.\d) instead of "
        r"(\d+\.\d)\), and desflurane's fat −(\d\.\d)% \((\d+\.\d) instead of (\d+\.\d)\)"
    )
    others, most = _one(r"The other (\w+) move by (\d\.\d)% or less")
    moves = {}
    for (agent_id, tissue), (stored, mean, _sd) in table.items():
        before = _isolated_time_constant_min(agent_id, tissue, stored)
        after = _isolated_time_constant_min(agent_id, tissue, mean)
        moves[agent_id, tissue] = (after / before - 1.0) * 100.0
    large = (("sevoflurane", "vessel_rich"), ("isoflurane", "fat"), ("desflurane", "fat"))

    assert sum(move != 0 for move in moves.values()) == COUNT_WORDS[changed]
    for index, cell in enumerate(large):
        printed, published, stored = named[3 * index : 3 * index + 3]
        assert (float(stored), float(published)) == table[cell][:2]
        assert _as_printed(abs(moves[cell]), printed) == printed, (
            f"{cell}'s time constant would move {moves[cell]:+.2f}%, not {printed}%"
        )
    assert moves["sevoflurane", "vessel_rich"] > 0
    assert moves["isoflurane", "fat"] < 0 and moves["desflurane", "fat"] < 0
    other_moves = [abs(move) for cell, move in moves.items() if move != 0 and cell not in large]
    assert len(other_moves) == COUNT_WORDS[others]
    assert _as_printed(max(other_moves), most) == most
    assert {agent_id for agent_id, _tissue in moves} == set(YASUDA_TABLE_AGENTS)


def test_a_desflurane_percent_over_the_stored_mac_gives_the_figures_printed() -> None:
    """Dividing Chortkoff's MAC-awake percent by the stored MAC overstates the band by 9.4%.

    The published inputs are read from the paragraph: Chortkoff's 2.60%, the
    7.25% MAC it is a fraction of, Song et al.'s mean and SD, and Rampil's MAC
    for ages 31 to 65. The stored MAC and MAC-awake fraction come from the
    data file. The test recomputes the 36%, the 0.394 and the 9.4%, the
    band's centre, and the two comparisons with Song et al.'s mean.
    """

    agent = _agent("desflurane")
    mac = agent.mac_at_age_40_percent
    fraction = agent.mac_awake.fraction_of_mac
    awake, of_mac, rampil_young = _one(
        r"Chortkoff's MAC-awake of (\d\.\d+)% is (\d+)% of a MAC of about (\d\.\d+)%"
    )
    (stored_mac,) = _one(r"The stored MAC is Mapleson's (\d\.\d)% at age 40")
    divided, by, quotient, published, too_high = _one(
        r"Dividing (\d\.\d+)% by (\d\.\d)% would give (\d\.\d+) instead of the published "
        r"(\d\.\d+), so the band would be drawn (\d\.\d)% too high"
    )
    centre_fraction, centre_mac, centre = _one(
        r"The band's centre is (\d\.\d+) of the stored (\d\.\d)%, or (\d\.\d+)%"
    )
    song_mean, song_sd = _one(r"Song et al. measured (\d\.\d+) ± (\d\.\d+)%")
    rampil_older, older_centre, within = _one(
        r"Rampil's MAC for ages 31-65, (\d\.\d)%, describes that arm's population, and 0\.36 of "
        r"it is (\d\.\d+)%, within (\d\.\d+) percentage points of Song's mean"
    )
    overstated = float(awake) / mac

    assert float(stored_mac) == float(by) == float(centre_mac) == mac
    assert float(published) == float(centre_fraction) == fraction
    assert divided == awake
    assert _as_printed(float(awake) / float(rampil_young) * 100.0, of_mac) == of_mac
    assert _as_printed(overstated, quotient) == quotient
    assert _as_printed((overstated / fraction - 1.0) * 100.0, too_high) == too_high
    assert _as_printed(fraction * mac, centre) == centre
    assert abs(fraction * mac - float(song_mean)) < float(song_sd)
    at_older_mac = fraction * float(rampil_older)
    assert _as_printed(at_older_mac, older_centre) == older_centre
    assert _as_printed(abs(at_older_mac - float(song_mean)), within) == within


def test_katohs_mac_equations_at_age_40_give_the_figures_printed() -> None:
    """Katoh's two MAC equations at age 40, against the stored MAC and the band centres.

    The equations are read from the paragraph, which quotes them from Katoh's
    p. 1013. The age is the one the stored MAC is for. The stored MAC,
    MAC-awake fractions and their SD come from the data files. The paragraph
    says that both differences between the band centres are "much less" than
    the SD of Katoh's fractions. The test reads that as less than half of it,
    with each difference taken as a fraction of Katoh's MAC. The half is this
    test's reading of the words, not a numerical limit.
    """

    isoflurane_intercept, isoflurane_slope, sevoflurane_intercept, sevoflurane_slope = (
        float(value)
        for value in _one(
            r"For isoflurane it is (\d\.\d+) − (\d\.\d+) × age \(yr\) percent, and for "
            r"sevoflurane (\d\.\d+) − (\d\.\d+) × age \(yr\) percent"
        )
    )
    age, sevoflurane_katoh, isoflurane_katoh = _one(
        r"At age (\d+) the equations give (\d\.\d+)% for sevoflurane and (\d\.\d+)% for isoflurane"
    )
    sevoflurane_below, isoflurane_below = _one(
        r"The stored MAC is (\d\.\d)% below Katoh's for sevoflurane and (\d\.\d)% below it for "
        r"isoflurane"
    )
    drawn_sevoflurane, drawn_isoflurane, katoh_sevoflurane, katoh_isoflurane = _one(
        r"The drawn centres are (\d\.\d+)% sevoflurane and (\d\.\d+)% isoflurane, against "
        r"(\d\.\d+)% and (\d\.\d+)% from Katoh's fractions times Katoh's age-40 MAC"
    )
    (katoh_sd,) = _one(r"the standard deviation of Katoh's fractions, (\d\.\d+) of MAC")
    katoh_mac = {
        "sevoflurane": sevoflurane_intercept - sevoflurane_slope * MAC_STORED_AT_AGE_YEARS,
        "isoflurane": isoflurane_intercept - isoflurane_slope * MAC_STORED_AT_AGE_YEARS,
    }
    printed = {
        "sevoflurane": (sevoflurane_katoh, sevoflurane_below, drawn_sevoflurane, katoh_sevoflurane),
        "isoflurane": (isoflurane_katoh, isoflurane_below, drawn_isoflurane, katoh_isoflurane),
    }

    assert int(age) == MAC_STORED_AT_AGE_YEARS
    for agent_id, (at_40, below, drawn, from_katoh) in printed.items():
        agent = _agent(agent_id)
        stored_mac = agent.mac_at_age_40_percent
        fraction = agent.mac_awake.fraction_of_mac
        assert agent.mac_awake.standard_deviation_fraction_of_mac == float(katoh_sd)
        assert _as_printed(katoh_mac[agent_id], at_40) == at_40
        assert _as_printed(_percent_below(stored_mac, katoh_mac[agent_id]), below) == below
        assert _as_printed(fraction * stored_mac, drawn) == drawn
        assert _as_printed(fraction * katoh_mac[agent_id], from_katoh) == from_katoh
        difference = fraction * (katoh_mac[agent_id] - stored_mac) / katoh_mac[agent_id]
        assert 0 < difference < float(katoh_sd) / 2.0, (
            f"{agent_id}: the band sits {difference:.3f} of Katoh's MAC below Katoh's own centre"
        )


#: Yasuda, Targ and Eger's brain:blood partition coefficients, which their
#: abstract gives (Anesth Analg 1989;69(3):370-3, PMID 2774233, read on PubMed
#: on 2026-11-22): 1.70 for sevoflurane, 1.57 for isoflurane and 1.29 for
#: I-653, which is desflurane. Table 2's brain column holds the same figures.
YASUDA_BRAIN_BLOOD = {"sevoflurane": 1.70, "isoflurane": 1.57, "desflurane": 1.29}


def test_yasudas_brain_column_recovers_the_blood_gas_coefficients_printed() -> None:
    """Table 1's brain value over Table 2's recovers each blood:gas coefficient printed.

    Table 2 divides each tissue:gas coefficient by an age-adjusted blood:gas
    coefficient, so dividing Table 1 by Table 2 gives that blood:gas back.
    The brain tissue:gas means are the vessel-rich column of the Yasuda table
    in § "Where the tissue:gas coefficients come from". The paragraph that
    opens "The vessel-rich coefficient is Yasuda's brain value" identifies
    them as the brain values. The test checks the three recovered values and how far each lies
    from the stored blood:gas coefficient, at the printed decimals.
    """

    recovered_printed = _one(
        r"it recovers (\d\.\d+), (\d\.\d+) and (\d\.\d+)\. These are (\d\.\d)% and "
        r"(\d\.\d)% above the stored sevoflurane and isoflurane values and (\d\.\d)% below "
        r"the stored desflurane value"
    )
    recovered = {
        agent_id: _yasuda_table()[agent_id, "vessel_rich"][1] / YASUDA_BRAIN_BLOOD[agent_id]
        for agent_id in YASUDA_TABLE_AGENTS
    }
    gaps = {
        agent_id: _signed_percent(
            recovered[agent_id], _agent(agent_id).blood_gas_partition_coefficient
        )
        for agent_id in YASUDA_TABLE_AGENTS
    }

    printed_values = recovered_printed[:3]
    for agent_id, printed in zip(YASUDA_TABLE_AGENTS, printed_values, strict=True):
        assert _as_printed(recovered[agent_id], printed) == printed, (agent_id, recovered)
    sevoflurane_gap, isoflurane_gap, desflurane_gap = recovered_printed[3:]
    assert gaps["sevoflurane"] > 0.0 and gaps["isoflurane"] > 0.0 and gaps["desflurane"] < 0.0
    assert _as_printed(gaps["sevoflurane"], sevoflurane_gap) == sevoflurane_gap, gaps
    assert _as_printed(gaps["isoflurane"], isoflurane_gap) == isoflurane_gap, gaps
    assert _as_printed(-gaps["desflurane"], desflurane_gap) == desflurane_gap, gaps


#: Yasuda, Targ and Eger's tissue:gas means (Table 1) and tissue:blood means
#: (Table 2), transcribed from page 371 of the full text (Anesth Analg
#: 1989;69(3):370-3, read on 2026-11-23 from the project's private reference
#: corpus), in the order brain, heart, liver, kidney, muscle and fat. I-653 is
#: desflurane.
YASUDA_ORGANS = ("brain", "heart", "liver", "kidney")
YASUDA_TISSUE_GAS = {
    "sevoflurane": (1.15, 1.21, 1.25, 0.78, 2.38, 34.0),
    "isoflurane": (2.09, 2.18, 2.34, 1.39, 4.40, 64.2),
    "desflurane": (0.54, 0.54, 0.55, 0.40, 0.94, 12.0),
}
YASUDA_TISSUE_BLOOD = {
    "sevoflurane": (1.70, 1.78, 1.85, 1.15, 3.13, 47.5),
    "isoflurane": (1.57, 1.61, 1.75, 1.05, 2.92, 44.9),
    "desflurane": (1.29, 1.29, 1.31, 0.94, 2.02, 27.2),
}


def _rounding_share(tissue_gas: float, tissue_blood: float) -> float:
    """How far rounding to the printed two decimals can move one quotient, as a share of it.

    Each printed mean can lie up to half a unit in its last place, 0.005,
    from the value the paper computed. The quotient moves furthest when the
    two means move apart.
    """

    half_unit = 0.005
    quotient = tissue_gas / tissue_blood
    highest = (tissue_gas + half_unit) / (tissue_blood - half_unit)
    lowest = (tissue_gas - half_unit) / (tissue_blood + half_unit)

    return max(highest / quotient - 1.0, 1.0 - lowest / quotient)


def test_yasudas_full_tables_recover_the_blood_gas_ranges_printed() -> None:
    """Each tissue column of Table 1 over Table 2 lies from the stored blood:gas as printed.

    The paragraph gives the rounding limit of the four organ columns, one
    whole-percent range per agent for those columns, and the muscle and fat
    columns one by one. The transcribed brain, muscle and fat tissue:gas
    means are first checked against the Yasuda table in § "Where the
    tissue:gas coefficients come from", and the brain tissue:blood means
    against the abstract's, so a transcription slip in those columns fails
    here rather than moving a printed range. The test also checks that each
    muscle and fat value lies above every organ value by more than both
    roundings together, as the paragraph says.
    """

    for agent_id in YASUDA_TABLE_AGENTS:
        brain, *_, muscle, fat = YASUDA_TISSUE_GAS[agent_id]
        for tissue, transcribed in zip(YASUDA_TABLE_TISSUES, (brain, muscle, fat), strict=True):
            assert _yasuda_table()[agent_id, tissue][1] == transcribed, (agent_id, tissue)
        assert YASUDA_TISSUE_BLOOD[agent_id][0] == YASUDA_BRAIN_BLOOD[agent_id], agent_id

    organ_count = len(YASUDA_ORGANS)
    columns = {
        agent_id: list(zip(YASUDA_TISSUE_GAS[agent_id], YASUDA_TISSUE_BLOOD[agent_id], strict=True))
        for agent_id in YASUDA_TABLE_AGENTS
    }
    gaps = {
        agent_id: [
            _signed_percent(
                tissue_gas / tissue_blood, _agent(agent_id).blood_gas_partition_coefficient
            )
            for tissue_gas, tissue_blood in columns[agent_id]
        ]
        for agent_id in YASUDA_TABLE_AGENTS
    }
    rounding = {
        agent_id: [_rounding_share(*column) * 100.0 for column in columns[agent_id]]
        for agent_id in YASUDA_TABLE_AGENTS
    }

    (limit,) = _one(r"rounding alone can move a recovered value by up to (\d\.\d)%")
    organ_rounding = max(max(rounding[agent_id][:organ_count]) for agent_id in YASUDA_TABLE_AGENTS)
    assert _as_printed(organ_rounding, limit) == limit, rounding

    printed = _one(
        r"Across those four organs, the value recovered is (\d)% to (\d)% above the stored "
        r"sevoflurane value, (\d)% to (\d)% above the stored isoflurane value, and within "
        r"(\d)% of the stored desflurane value"
    )
    sevoflurane_organs = gaps["sevoflurane"][:organ_count]
    isoflurane_organs = gaps["isoflurane"][:organ_count]
    computed = (
        min(sevoflurane_organs),
        max(sevoflurane_organs),
        min(isoflurane_organs),
        max(isoflurane_organs),
        max(abs(gap) for gap in gaps["desflurane"][:organ_count]),
    )
    for value, cell in zip(computed, printed, strict=True):
        assert _as_printed(value, cell) == cell, (computed, printed)

    muscle_and_fat = _one(
        r"The muscle and fat columns recover more, by more than rounding explains: (\d+)% and "
        r"(\d+)% above the stored value for sevoflurane, (\d+)% and (\d+)% for isoflurane, "
        r"and (\d+)% and (\d+)% for desflurane"
    )
    computed_muscle_and_fat = [
        gap for agent_id in YASUDA_TABLE_AGENTS for gap in gaps[agent_id][organ_count:]
    ]
    for value, cell in zip(computed_muscle_and_fat, muscle_and_fat, strict=True):
        assert _as_printed(value, cell) == cell, (computed_muscle_and_fat, muscle_and_fat)

    for agent_id in YASUDA_TABLE_AGENTS:
        highest_organ = max(
            gap + share
            for gap, share in zip(
                gaps[agent_id][:organ_count], rounding[agent_id][:organ_count], strict=True
            )
        )
        lowest_other = min(
            gap - share
            for gap, share in zip(
                gaps[agent_id][organ_count:], rounding[agent_id][organ_count:], strict=True
            )
        )
        assert lowest_other > highest_organ, (agent_id, gaps, rounding)
