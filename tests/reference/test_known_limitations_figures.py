"""The arithmetic figures in `docs/MODEL.md` § "Known limitations" follow from their inputs.

The section sizes each limitation with figures a reader uses to judge how much
it matters. Many of them are arithmetic on a stored parameter, a physical
constant or a published value that the same paragraph states. Before
`PL-19W8`, nothing checked that arithmetic. This module redoes it.

Each test reads the inputs and the result from the section as printed, takes
the stored parameters from the data files through the loaders, and compares
the result at the number of decimal places the section prints it with. So a
changed parameter that moves a figure fails here, and so does an edit to the
section that changes a figure without changing its inputs. The published
inputs, such as Baker and Farmery's coefficients, are read from the section,
because each is restated there beside its citation. These tests check that the
section's arithmetic is right. They cannot check that a published input was
transcribed correctly, which is the citation's job.
"""

import re
from functools import cache
from pathlib import Path

from anesthesia_sim.core.liquid_agent import (
    CELSIUS_ZERO_K,
    MOLAR_GAS_CONSTANT_J_MOL_K,
    REFERENCE_MOLAR_VOLUME_L_MOL,
    STANDARD_ATMOSPHERE_PA,
)
from anesthesia_sim.core.parameters import (
    AgentParameters,
    load_agent_parameters,
    load_reference_adult_parameters,
)
from anesthesia_sim.core.units import LITRES_PER_CUBIC_METRE

MODEL_PATH = Path(__file__).resolve().parents[2] / "docs" / "MODEL.md"
SECTION_HEADING = "## Known limitations"

#: One standard atmosphere in mmHg, the pressure that `STANDARD_ATMOSPHERE_PA`
#: holds in pascals. The section works in mmHg, and `core/liquid_agent.py`
#: gives 101 325 Pa as 760 mmHg in its comment on that constant.
STANDARD_ATMOSPHERE_MMHG = 760.0
#: The temperature at which the section says the alveolar, venous and tissue
#: stores are natively stated.
BODY_TEMPERATURE_CELSIUS = 37.0


@cache
def _section_text() -> str:
    """The section's prose, with each run of whitespace made one space."""

    text = MODEL_PATH.read_text(encoding="utf-8")
    start = text.index(SECTION_HEADING)
    end = text.find("\n## ", start + len(SECTION_HEADING))

    return " ".join(text[start : end if end >= 0 else None].split())


def _one(pattern: str) -> tuple[str, ...]:
    """The groups of the one match of `pattern` in the section, or a failure naming it."""

    # regex: a search for one sentence's figures through free prose, which no
    # parser reads; the caller's pattern names the sentence's fixed words.
    matches = re.findall(pattern, _section_text())
    assert len(matches) == 1, (
        f"docs/MODEL.md § 'Known limitations' should state this once, as {pattern!r}, and it "
        f"states it {len(matches)} times. If the sentence was reworded, update the pattern "
        f"here so the figure stays checked."
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

    body, reference = _one(r"The ratio behind both figures is (\d+\.\d+)/(\d+\.\d+)")
    (overstated,) = _one(r"\*\*The size is (\d+\.\d) %")
    (fewer,) = _one(r"stores hold (\d+\.\d) % fewer moles")
    at_body = _molar_volume_l_mol(BODY_TEMPERATURE_CELSIUS)

    assert _as_printed(at_body, body) == body
    assert _as_printed(REFERENCE_MOLAR_VOLUME_L_MOL, reference) == reference
    assert _as_printed((at_body / REFERENCE_MOLAR_VOLUME_L_MOL - 1.0) * 100.0, overstated) == (
        overstated
    )
    assert _as_printed((1.0 - REFERENCE_MOLAR_VOLUME_L_MOL / at_body) * 100.0, fewer) == fewer


def test_the_humidification_dilution_follows_from_the_water_vapour_pressure() -> None:
    """47 mmHg of water leaves 713 mmHg, a 6.2 % dilution and a 6.6 % overstatement."""

    water, rest = _one(r"of the 760 mmHg available, (\d+) mmHg is water and (\d+) mmHg is left")
    (dilution,) = _one(r"That is a dilution of 47/760, or (\d+\.\d) %")
    (above,) = _one(r"the undiluted figure is (\d+\.\d) % above the humidified one")
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

    (svp,) = _one(r"Isoflurane's saturated vapour pressure is about (\d+) mmHg at 20 °C")
    overshoot, ambient = _one(r"about (\d+)% high at (\d+) mmHg")
    svp_mmhg = float(svp)

    def partial_pressure(ambient_mmhg: float) -> float:
        return ambient_mmhg * svp_mmhg / (ambient_mmhg - svp_mmhg)

    ratio = partial_pressure(float(ambient)) / partial_pressure(STANDARD_ATMOSPHERE_MMHG)

    assert _as_printed((ratio - 1.0) * 100.0, overshoot) == overshoot


def test_lowe_and_ernsts_cardiac_output_at_the_reference_weight() -> None:
    """0.2 M^(3/4) at the reference patient's 70 kg is the 4.84 L/min printed."""

    printed, weight = _one(r"which is (\d+\.\d+) L/min at (\d+) kg")
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
    flows = _one(r"\(Table 4 of each paper\) give (\d\.\d), (\d\.\d), (\d\.\d) and (\d\.\d)")

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
    """The gaps between Baker and Farmery's set and the stored coefficients, on both scales."""

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
