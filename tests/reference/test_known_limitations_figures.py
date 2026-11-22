"""The arithmetic figures behind the known limitations follow from their inputs.

`docs/MODEL.md` sizes each limitation with figures a reader uses to judge how
much it matters, and `docs/PARAMETERS.md` § "The evidence behind the known
limitations" keeps the working behind them. Both are read here as one text.
Many of the figures are arithmetic on a stored parameter, a physical constant
or a published value that the same paragraph states. Before
`PL-19W8`, nothing checked that arithmetic. This module redoes it.

Each test reads the inputs and the result from the text as printed, takes the
stored parameters from the data files through the loaders, and compares the
result at the number of decimal places the text prints it with. So a changed
parameter that moves a figure fails here, and so does an edit to the text that
changes a figure without changing its inputs. The published inputs, such as
Baker and Farmery's coefficients, are read from the text, because each is
restated there beside its citation. These tests check that the text's
arithmetic is right. They cannot check that a published input was
transcribed correctly, which is the citation's job.

One figure is not arithmetic: how much the omitted lung store would change
$F_A/F_I$. Its test adds the store to the model's alveolar gas and runs the
model with and without it, because the text states the model's own response.
The expected values are the printed figures, never a run of the shipped model.
"""

import math
import re
from dataclasses import replace
from functools import cache
from pathlib import Path

from anesthesia_sim.core.governing_equations import (
    ALVEOLAR_FRACTION,
    INSPIRED_FRACTION,
    STATE_SIZE,
    UNIT_STATE,
)
from anesthesia_sim.core.liquid_agent import (
    CELSIUS_ZERO_K,
    MOLAR_GAS_CONSTANT_J_MOL_K,
    REFERENCE_MOLAR_VOLUME_L_MOL,
    STANDARD_ATMOSPHERE_PA,
)
from anesthesia_sim.core.numerical_envelope import CompartmentVolume
from anesthesia_sim.core.parameters import (
    AgentParameters,
    load_agent_parameters,
    load_reference_adult_parameters,
)
from anesthesia_sim.core.prediction import predicted_states_at
from anesthesia_sim.core.supported_ranges import CaseInstant
from anesthesia_sim.core.units import LITRES_PER_CUBIC_METRE
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

MODEL_PATH = Path(__file__).resolve().parents[2] / "docs" / "MODEL.md"
#: The developer's document, whose account of desflurane's wash-in residual
#: restates the lung store's shares.
VERIFICATION_PATH = MODEL_PATH.with_name("VERIFICATION.md")
#: The document that holds the evidence behind the limitations, and the table
#: of Yasuda, Targ and Eger's Table 1.
PARAMETERS_PATH = MODEL_PATH.with_name("PARAMETERS.md")
EVIDENCE_HEADING = "## The evidence behind the known limitations"

#: One standard atmosphere in mmHg, the pressure that `STANDARD_ATMOSPHERE_PA`
#: holds in pascals. The section works in mmHg, and `core/liquid_agent.py`
#: gives 101 325 Pa as 760 mmHg in its comment on that constant.
STANDARD_ATMOSPHERE_MMHG = 760.0
#: The temperature at which the section says the alveolar, venous and tissue
#: stores are natively stated.
BODY_TEMPERATURE_CELSIUS = 37.0


@cache
def _section_text() -> str:
    """The prose of `docs/MODEL.md` and of the evidence section, with each run
    of whitespace made one space.

    The whole of `docs/MODEL.md` is read, because the clinician's text states
    some of these figures where they first matter, outside its known
    limitations.
    """

    model = MODEL_PATH.read_text(encoding="utf-8")
    parameters = PARAMETERS_PATH.read_text(encoding="utf-8")
    start = parameters.index(EVIDENCE_HEADING)
    end = parameters.find("\n## ", start + len(EVIDENCE_HEADING))
    evidence = parameters[start : end if end >= 0 else None]

    return " ".join(f"{model}\n{evidence}".split())


def _one(pattern: str) -> tuple[str, ...]:
    """The groups that every match of `pattern` gives, or a failure naming it.

    A figure may be stated both in `docs/MODEL.md` and in the evidence
    section. Each statement must give the same figures, so that neither copy
    can drift from the other.
    """

    # regex: a search for one sentence's figures through free prose, which no
    # parser reads; the caller's pattern names the sentence's fixed words.
    matches = re.findall(pattern, _section_text())
    assert matches, (
        f"neither docs/MODEL.md nor docs/PARAMETERS.md § 'The evidence behind the known "
        f"limitations' states this as {pattern!r}. If the sentence was reworded, update the "
        f"pattern here so the figure stays checked."
    )
    assert len(set(matches)) == 1, (
        f"the statements matching {pattern!r} give different figures: {sorted(set(matches))}"
    )
    found = matches[0]

    return found if isinstance(found, tuple) else (found,)


def _as_printed(value: float, printed: str) -> str:
    """`value` to as many decimal places as `printed` has."""

    places = len(printed.split(".")[1]) if "." in printed else 0

    return f"{value:.{places}f}"


def _agent(agent_id: str) -> AgentParameters:
    return load_agent_parameters(agent_id)


def _tissue_blood(agent_id: str, tissue: str) -> float:
    """A stored tissue:gas coefficient over the stored blood:gas one."""

    agent = _agent(agent_id)
    tissue_gas = float(getattr(agent, f"{tissue}_tissue_gas_partition_coefficient"))

    return tissue_gas / float(agent.blood_gas_partition_coefficient)


def _molar_volume_l_mol(celsius: float) -> float:
    """V_m = R T / p at one standard atmosphere, in litres per mole."""

    kelvin = celsius + CELSIUS_ZERO_K

    return MOLAR_GAS_CONSTANT_J_MOL_K * kelvin / STANDARD_ATMOSPHERE_PA * LITRES_PER_CUBIC_METRE


def test_the_reference_condition_gap_is_the_ratio_of_molar_volumes() -> None:
    """The 5.8 % overstatement and the 5.5 % shortfall come from 37 °C against 20 °C."""

    (reference,) = _one(r"molar volume at that condition is (\d+\.\d+) L/mol")
    (body,) = _one(r"measured at 37 °C, where the molar volume is (\d+\.\d+) L/mol")
    (overstated,) = _one(r"overstates it by (\d+\.\d) ?%")
    (fewer,) = _one(r"stores hold (\d+\.\d) ?% fewer moles")
    at_body = _molar_volume_l_mol(BODY_TEMPERATURE_CELSIUS)

    assert _as_printed(at_body, body) == body
    assert _as_printed(REFERENCE_MOLAR_VOLUME_L_MOL, reference) == reference
    assert _as_printed((at_body / REFERENCE_MOLAR_VOLUME_L_MOL - 1.0) * 100.0, overstated) == (
        overstated
    )
    assert _as_printed((1.0 - REFERENCE_MOLAR_VOLUME_L_MOL / at_body) * 100.0, fewer) == fewer


def test_the_humidification_dilution_follows_from_the_water_vapour_pressure() -> None:
    """47 mmHg of water leaves 713 mmHg, a 6.2 % dilution and a 6.6 % overstatement."""

    water, rest = _one(r"saturated with water vapou?r at (\d+) mmHg, which leaves (\d+) mmHg")
    (dilution,) = _one(r"diluted by 47/760, or (\d+\.\d) ?%")
    (above,) = _one(r"the undiluted figure is (\d+\.\d) ?% above the humidified one")
    water_mmhg = float(water)
    dry_mmhg = STANDARD_ATMOSPHERE_MMHG - water_mmhg

    assert _as_printed(dry_mmhg, rest) == rest
    assert _as_printed(water_mmhg / STANDARD_ATMOSPHERE_MMHG * 100.0, dilution) == dilution
    assert _as_printed(water_mmhg / dry_mmhg * 100.0, above) == above


def test_the_variable_bypass_overshoot_at_altitude_follows_from_the_fuller_form() -> None:
    """With SVP/(P - SVP), isoflurane's partial pressure at 585 mmHg is 16 % high.

    A variable-bypass vaporizer's output fraction is about k SVP/(P - SVP), so
    its partial pressure is P times that. The ratio at the lower pressure to
    the ratio at 760 mmHg is the overshoot.
    """

    (svp,) = _one(r"Isoflurane's (?:saturated vapour pressure )?is about (\d+) mmHg at 20 °C")
    overshoot, ambient = _one(r"about (\d+)%(?: high)? at (\d+) mmHg")
    svp_mmhg = float(svp)

    def partial_pressure(ambient_mmhg: float) -> float:
        return ambient_mmhg * svp_mmhg / (ambient_mmhg - svp_mmhg)

    ratio = partial_pressure(float(ambient)) / partial_pressure(STANDARD_ATMOSPHERE_MMHG)

    assert _as_printed((ratio - 1.0) * 100.0, overshoot) == overshoot


def test_lowe_and_ernsts_cardiac_output_at_the_reference_weight() -> None:
    """0.2 M^(3/4) at the reference patient's 70 kg is the 4.84 L/min printed."""

    printed, weight = _one(r"(\d+\.\d+) L/min at (\d+) kg")
    reference_weight_kg = load_reference_adult_parameters().weight_kg

    assert float(weight) == reference_weight_kg
    assert _as_printed(0.2 * reference_weight_kg**0.75, printed) == printed


def test_the_fitted_fat_time_constants_imply_the_flows_printed() -> None:
    """Fat:blood over each fitted time constant gives the flows per 100 mL printed.

    The time constants are the two Yasuda 1991 papers' (Table 4 of each), in
    the order sevoflurane and isoflurane, then desflurane and isoflurane.
    """

    sevoflurane, isoflurane, desflurane = _one(
        r"are (\d+) for sevoflurane, (\d+) for isoflurane and (\d+) for desflurane"
    )
    time_constants = _one(r"time constants of ([\d,]+), ([\d,]+), ([\d,]+) and ([\d,]+) minutes")
    flows = _one(
        r"(?:\(Table 4 of each paper\)|their fitted time constants) give "
        r"(\d\.\d), (\d\.\d), (\d\.\d) and (\d\.\d)"
    )

    for agent_id, printed in (
        ("sevoflurane", sevoflurane),
        ("isoflurane", isoflurane),
        ("desflurane", desflurane),
    ):
        assert _as_printed(_tissue_blood(agent_id, "fat"), printed) == printed
    for agent_id, minutes, flow in zip(
        ("sevoflurane", "isoflurane", "desflurane", "isoflurane"),
        time_constants,
        flows,
        strict=True,
    ):
        per_100_ml = _tissue_blood(agent_id, "fat") / float(minutes.replace(",", "")) * 100.0
        assert _as_printed(per_100_ml, flow) == flow, (
            f"{agent_id}'s fat:blood over {minutes} min is {per_100_ml!r} mL/100 mL/min, "
            f"printed as {flow}"
        )


def test_the_muscle_group_equilibrates_in_the_minutes_printed() -> None:
    """The muscle time constants V λ / Q span the 85 to 135 minutes printed."""

    shortest, longest = _one(r"The muscle group equilibrates in (\d+) to (\d+) minutes")
    patient = load_reference_adult_parameters()
    muscle_flow_l_min = float(patient.muscle_perfusion_fraction) * float(
        patient.default_cardiac_output_l_min
    )
    minutes = [
        float(patient.muscle_volume_l) * _tissue_blood(agent_id, "muscle") / muscle_flow_l_min
        for agent_id in ("desflurane", "sevoflurane", "isoflurane")
    ]

    assert (_as_printed(min(minutes), shortest), _as_printed(max(minutes), longest)) == (
        shortest,
        longest,
    ), f"the muscle time constants are {minutes} min"


def test_baker_and_farmerys_set_differs_by_the_percents_printed() -> None:
    """The gaps between Baker and Farmery's set and the stored coefficients, on both scales.

    The fat and muscle gaps are computed from the coefficients the section
    prints. The section prints no vessel-rich coefficient, only that the set's
    are 28% above this model's on the tissue:blood scale. So the test checks
    that the tissue:gas gaps of 18% and 38% follow from that printed 28%, and
    it does not check the 28% itself, which rests on the citation alone.
    """

    fat, fat_above, model_fat = _one(
        r"puts sevoflurane's fat coefficient at (\d+\.\d), (\d+)% above this model's (\d+\.\d)"
    )
    muscle, muscle_below, model_muscle = _one(
        r"isoflurane's muscle coefficient at (\d+\.\d+), (\d+)% below this model's (\d+\.\d+)"
    )
    (vessel_rich_above,) = _one(r"Its vessel-rich figures are (\d+)% above this model's")
    sevoflurane_blood_gas, isoflurane_blood_gas = _one(
        r"own blood:gas values, (\d\.\d) for sevoflurane and (\d\.\d) for isoflurane"
    )
    fat_gas_above, muscle_gas_below = _one(
        r"sevoflurane fat coefficient is (\d+)% above this model's and its isoflurane muscle "
        r"coefficient (\d+)% below"
    )
    sevoflurane_vr, isoflurane_vr = _one(
        r"vessel-rich coefficient is (\d+)% above for sevoflurane and (\d+)% above for isoflurane"
    )

    stored_fat = _tissue_blood("sevoflurane", "fat")
    stored_muscle = _tissue_blood("isoflurane", "muscle")
    assert _as_printed(stored_fat, model_fat) == model_fat
    assert _as_printed(stored_muscle, model_muscle) == model_muscle
    assert _as_printed((float(fat) / stored_fat - 1.0) * 100.0, fat_above) == fat_above
    assert _as_printed((1.0 - float(muscle) / stored_muscle) * 100.0, muscle_below) == (
        muscle_below
    )

    # On the tissue:gas scale each set's tissue:blood value is multiplied by its
    # own blood:gas value.
    sevoflurane = _agent("sevoflurane")
    isoflurane = _agent("isoflurane")
    fat_gas = float(fat) * float(sevoflurane_blood_gas)
    muscle_gas = float(muscle) * float(isoflurane_blood_gas)
    stored_fat_gas = float(sevoflurane.fat_tissue_gas_partition_coefficient)
    stored_muscle_gas = float(isoflurane.muscle_tissue_gas_partition_coefficient)
    assert _as_printed((fat_gas / stored_fat_gas - 1.0) * 100.0, fat_gas_above) == fat_gas_above
    assert _as_printed((1.0 - muscle_gas / stored_muscle_gas) * 100.0, muscle_gas_below) == (
        muscle_gas_below
    )
    for agent, blood_gas, printed in (
        (sevoflurane, sevoflurane_blood_gas, sevoflurane_vr),
        (isoflurane, isoflurane_blood_gas, isoflurane_vr),
    ):
        ratio = (
            (1.0 + float(vessel_rich_above) / 100.0)
            * float(blood_gas)
            / float(agent.blood_gas_partition_coefficient)
        )
        assert _as_printed((ratio - 1.0) * 100.0, printed) == printed


def test_yasudas_muscle_spreads_are_the_percents_printed() -> None:
    """Each muscle SD over its mean is the percent printed beside it."""

    # regex: a search for each "N% for agent (mean ± SD)" figure through free prose.
    rows = re.findall(
        r"(\d+)% (?:of the mean )?for \w+ \((\d+\.\d+) ± (\d+\.\d+)\)", _section_text()
    )
    assert len(rows) == 3, f"expected three 'N% for agent (mean ± SD)' figures, found {rows}"

    for printed, mean, sd in rows:
        assert _as_printed(float(sd) / float(mean) * 100.0, printed) == printed, (
            f"{sd} over {mean} is not {printed}%"
        )


#: The agent rows of the table of Yasuda, Targ and Eger's Table 1 in
#: `docs/PARAMETERS.md` § "Parameter provenance", and its columns in order,
#: each named for the stored field.
YASUDA_TABLE_AGENTS = ("sevoflurane", "isoflurane", "desflurane")
YASUDA_TABLE_TISSUES = ("vessel_rich", "muscle", "fat")


def _yasuda_table() -> dict[tuple[str, str], tuple[float, float, float]]:
    """Each cell of `docs/PARAMETERS.md`'s Yasuda table, as (stored, mean, SD).

    The table restates the paper's Table 1 beside its citation, so it is the
    published input this module reads, as it reads Baker and Farmery's figures.
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


def test_the_yasuda_table_holds_the_stored_coefficients() -> None:
    """The table's stored column is each agent file's tissue:gas coefficient."""

    for (agent_id, tissue), (stored, _mean, _sd) in _yasuda_table().items():
        value = float(getattr(_agent(agent_id), f"{tissue}_tissue_gas_partition_coefficient"))
        assert value == stored, f"{agent_id} {tissue} stores {value}; the table says {stored}"


def test_yasudas_fat_spreads_are_the_percents_printed() -> None:
    """Fat's SD is 17% to 19% of its mean across the three agents, as the section prints."""

    low, high = _one(r"against (\d+)% to (\d+)% for fat")
    spreads = [
        sd / mean * 100.0
        for (_agent_id, tissue), (_stored, mean, sd) in _yasuda_table().items()
        if tissue == "fat"
    ]

    assert _as_printed(min(spreads), low) == low, f"the smallest fat spread is {min(spreads)}%"
    assert _as_printed(max(spreads), high) == high, f"the largest fat spread is {max(spreads)}%"


def test_the_stored_set_differs_from_yasudas_means_by_the_percents_printed() -> None:
    """Seven of nine stored values differ from the means, by at most 9%, in isoflurane's fat."""

    cells_differing, largest, stored_fat, mean_fat = _one(
        r"means in (\w+) of nine cells, by up to (\d+)% \(isoflurane fat, "
        r"(\d+\.\d) against (\d+\.\d)\)"
    )
    table = _yasuda_table()
    gaps = {cell: abs(stored / mean - 1.0) * 100.0 for cell, (stored, mean, _sd) in table.items()}
    widest = max(gaps, key=gaps.__getitem__)

    assert widest == ("isoflurane", "fat")
    assert (float(stored_fat), float(mean_fat)) == table[widest][:2]
    assert _as_printed(gaps[widest], largest) == largest
    differing = sum(stored != mean for stored, mean, _sd in table.values())
    assert cells_differing == ("seven" if differing == 7 else str(differing)), (
        f"{differing} of the nine stored values differ from Yasuda's means"
    )


#: The pattern of the round figures that size the omitted lung store, as
#: `docs/MODEL.md` § "Lung tissue and pulmonary blood" prints them.
LUNG_STORE_INPUTS = (
    r"(\d+) kg of lung tissue with a tissue:blood ratio of (\d\.\d), and (\d\.\d) L of "
    r"pulmonary and arterial blood"
)
#: The pattern of the store's share of each agent's fast pool. Both
#: `docs/MODEL.md` and `docs/VERIFICATION.md` print it.
LUNG_STORE_SHARES = (
    r"(\d+\.\d)% of desflurane's fast pool, (\d+\.\d)% of sevoflurane's and "
    r"(\d+\.\d)% of isoflurane's"
)
LUNG_STORE_AGENTS = ("desflurane", "sevoflurane", "isoflurane")
#: The two times of wash-in at which the section states the store's effect, as
#: the whole seconds a case instant takes.
ONE_MINUTE_S = 60
THIRTY_MINUTES_S = 1800


def _lung_store_gas_equivalent_l(agent_id: str) -> float:
    """The omitted lung store's capacity for an agent, in gas-equivalent litres.

    Lung tissue is taken at 1 kg per litre, so its capacity is its mass times
    its tissue:blood ratio times the agent's blood:gas coefficient. The blood's
    capacity is its volume times the blood:gas coefficient.
    """

    tissue_kg, tissue_blood, blood_l = (float(x) for x in _one(LUNG_STORE_INPUTS))
    blood_gas = float(_agent(agent_id).blood_gas_partition_coefficient)

    return (tissue_kg * tissue_blood + blood_l) * blood_gas


def test_the_omitted_lung_store_is_the_share_of_the_fast_pool_printed() -> None:
    """The store over the alveolar gas, venous blood and vessel-rich group is 20.1, 19.7 and 23.4%.

    The fast pool is the capacity of the alveolar gas, the venous blood and the
    vessel-rich group, each in gas-equivalent litres, from the stored
    parameters. `docs/VERIFICATION.md` states the same shares, and the test
    holds both copies to one calculation.
    """

    printed = _one(LUNG_STORE_SHARES)
    # regex: the same sentence's figures, in the developer's document.
    in_verification = re.findall(
        LUNG_STORE_SHARES, " ".join(VERIFICATION_PATH.read_text(encoding="utf-8").split())
    )
    assert in_verification == [printed], (
        f"docs/VERIFICATION.md gives the lung store's shares as {in_verification}, "
        f"docs/MODEL.md as {printed}"
    )
    patient = load_reference_adult_parameters()
    for agent_id, share in zip(LUNG_STORE_AGENTS, printed, strict=True):
        agent = _agent(agent_id)
        fast_pool_l = (
            float(patient.alveolar_gas_volume_l)
            + float(patient.venous_pool_volume_l) * float(agent.blood_gas_partition_coefficient)
            + float(patient.vessel_rich_volume_l)
            * float(agent.vessel_rich_tissue_gas_partition_coefficient)
        )
        computed = _lung_store_gas_equivalent_l(agent_id) / fast_pool_l * 100.0
        assert _as_printed(computed, share) == share, (
            f"{agent_id}: the lung store is {computed!r}% of the fast pool, printed as {share}%"
        )


def _alveolar_over_inspired(agent_id: str, *, with_lung_store: bool) -> tuple[float, float]:
    """$F_A/F_I$ at one minute and at 30 minutes of wash-in from zero agent.

    With the store, its capacity is added to the alveolar gas volume, so it
    stays at the alveolar partial pressure. Every other setting is the
    agent's default.
    """

    settings = AgentUptakeSystem.for_agent(agent_id).equation_settings()
    if with_lung_store:
        settings = replace(
            settings,
            alveolar_volume_l=CompartmentVolume(
                float(settings.alveolar_volume_l) + _lung_store_gas_equivalent_l(agent_id)
            ),
        )
    no_agent = tuple(1.0 if index == UNIT_STATE else 0.0 for index in range(STATE_SIZE))
    one_minute, thirty_minutes = predicted_states_at(
        settings,
        no_agent,
        CaseInstant(0),
        (CaseInstant(ONE_MINUTE_S), CaseInstant(THIRTY_MINUTES_S)),
    )

    return (
        one_minute[ALVEOLAR_FRACTION] / one_minute[INSPIRED_FRACTION],
        thirty_minutes[ALVEOLAR_FRACTION] / thirty_minutes[INSPIRED_FRACTION],
    )


def test_the_omitted_lung_store_lowers_the_wash_in_by_the_amounts_printed() -> None:
    """The store lowers $F_A/F_I$ by 0.08 to 0.10 at one minute and 0.001 to 0.005 at 30.

    The test compares each agent's model with and without the store, from the
    same settings, and checks the lowest and highest drop across the three
    agents at the printed decimals. A store that kept filling past the first
    minutes would leave a larger drop at 30 minutes than the text allows.
    """

    first_low, first_high, late_low, late_high = _one(
        r"lowers \$`F_A/F_I`\$ by (\d\.\d+) to (\d\.\d+) at one minute of wash-in, but by "
        r"only (\d\.\d+) to (\d\.\d+) at 30 minutes"
    )
    drops = {
        agent_id: tuple(
            without - with_store
            for without, with_store in zip(
                _alveolar_over_inspired(agent_id, with_lung_store=False),
                _alveolar_over_inspired(agent_id, with_lung_store=True),
                strict=True,
            )
        )
        for agent_id in LUNG_STORE_AGENTS
    }
    at_one_minute = [first for first, _late in drops.values()]
    at_thirty_minutes = [late for _first, late in drops.values()]

    assert all(drop > 0.0 for drop in at_one_minute + at_thirty_minutes), drops
    assert (
        _as_printed(min(at_one_minute), first_low),
        _as_printed(max(at_one_minute), first_high),
    ) == (first_low, first_high), f"the drops at one minute are {drops}"
    assert (
        _as_printed(min(at_thirty_minutes), late_low),
        _as_printed(max(at_thirty_minutes), late_high),
    ) == (late_low, late_high), f"the drops at 30 minutes are {drops}"


#: The case lengths, in minutes, over which `docs/MODEL.md` § "Intertissue
#: diffusion: the missing fourth compartment" states its fat figures: "any case
#: from half an hour to four hours".
FAT_CASE_MINUTES = range(30, 241)
#: The time at which it states the fat fractions: "After an hour".
ONE_HOUR_MIN = 60
#: The words the section uses for the two ends of the partial-pressure ratio.
RATIO_IN_WORDS = {"four": 4.0, "six and a half": 6.5}


def _filled(minutes: float, time_constant_min: float) -> float:
    """The fraction of a steady driving partial pressure that a compartment reaches."""

    return 1.0 - math.exp(-minutes / time_constant_min)


def _fourth_compartment_table() -> list[tuple[str, float, float, float, float, str]]:
    """Each cohort row of the section's table, with the model's printed fat time constant.

    A row gives the agent and the published means of the fourth compartment's
    time constant and volume and of the fitted fat group's, from Tables 4 and
    5 of the two Yasuda 1991 papers.
    """

    # regex: each cohort row of the section's markdown table, mean ± SD cells.
    rows = re.findall(
        r"\| (\w+), \*Anesth\w*(?: Analg)?\* 1991 \| ([\d,]+) ± [\d,]+ \| ([\d.]+) ± [\d.]+ \| "
        r"([\d,]+) ± [\d,]+ \| ([\d.]+) ± [\d.]+ \| ([\d,]+) \|",
        _section_text(),
    )
    assert len(rows) == 4, (
        f"expected four cohort rows in the fourth-compartment table, found {rows}"
    )

    return [
        (
            agent.lower(),
            float(tau_fourth.replace(",", "")),
            float(volume_fourth),
            float(tau_fat.replace(",", "")),
            float(volume_fat),
            model_tau,
        )
        for agent, tau_fourth, volume_fourth, tau_fat, volume_fat, model_tau in rows
    ]


def _model_fat_time_constant_min(agent_id: str) -> float:
    """The model's fat group time constant V λ / Q at the default cardiac output."""

    patient = load_reference_adult_parameters()
    fat_flow_l_min = float(patient.fat_perfusion_fraction) * float(
        patient.default_cardiac_output_l_min
    )

    return float(patient.fat_volume_l) * _tissue_blood(agent_id, "fat") / fat_flow_l_min


def test_the_fourth_compartment_and_the_fat_group_fill_as_printed() -> None:
    """The fat figures follow from the published time constants and volumes.

    Each compartment fills as $1 - e^{-t/\\tau}$ from a steady arterial partial
    pressure, which is the assumption the section states. The fourth
    compartment is taken as fat at the model's stored fat solubility, so its
    uptake is its volume times its filled fraction, on the same scale as the
    model's fat group and the fitted one. The test checks the model's time
    constants in the table, the fractions after an hour, the ratio of partial
    pressures and the ratios of uptake over cases of 30 to 240 minutes.
    """

    hour_low, hour_high, trace_low, trace_high = _one(
        r"After an hour it is at (\d+) to (\d+)% of arterial, against the trace's "
        r"(\d\.\d) to (\d\.\d)%"
    )
    ratio_low, ratio_high = _one(r"runs at (four) to (six and a half) times the trace's")
    model_low, model_high, fitted_low, fitted_high = _one(
        r"it takes up (\d\.\d) to (\d\.\d) times as much agent as the model's whole fat "
        r"group, or (\d\.\d) to (\d\.\d) times as much as the studies' fitted fat group"
    )
    _one(r"over any case from half an hour to four hours")
    model_fat_volume_l = float(load_reference_adult_parameters().fat_volume_l)

    fourth_at_hour, trace_at_hour, ratios, over_model, over_fitted = [], [], [], [], []
    for (
        agent_id,
        tau_fourth,
        volume_fourth,
        tau_fat,
        volume_fat,
        model_tau,
    ) in _fourth_compartment_table():
        tau_model = _model_fat_time_constant_min(agent_id)
        assert f"{tau_model:,.0f}" == model_tau, (
            f"{agent_id}: the model's fat time constant is {tau_model!r} min, "
            f"printed as {model_tau}"
        )
        fourth_at_hour.append(_filled(ONE_HOUR_MIN, tau_fourth) * 100.0)
        trace_at_hour.append(_filled(ONE_HOUR_MIN, tau_model) * 100.0)
        for minutes in FAT_CASE_MINUTES:
            fourth = _filled(minutes, tau_fourth)
            ratios.append(fourth / _filled(minutes, tau_model))
            over_model.append(
                volume_fourth * fourth / (model_fat_volume_l * _filled(minutes, tau_model))
            )
            over_fitted.append(volume_fourth * fourth / (volume_fat * _filled(minutes, tau_fat)))

    for computed, low, high in (
        (fourth_at_hour, hour_low, hour_high),
        (trace_at_hour, trace_low, trace_high),
        (over_model, model_low, model_high),
        (over_fitted, fitted_low, fitted_high),
    ):
        assert (_as_printed(min(computed), low), _as_printed(max(computed), high)) == (low, high), (
            f"the computed range is {min(computed)!r} to {max(computed)!r}, printed {low} to {high}"
        )
    # The ratio is printed in words, to the nearest half.
    assert (round(min(ratios) * 2.0) / 2.0, round(max(ratios) * 2.0) / 2.0) == (
        RATIO_IN_WORDS[ratio_low],
        RATIO_IN_WORDS[ratio_high],
    ), f"the ratio of partial pressures runs from {min(ratios)!r} to {max(ratios)!r}"
