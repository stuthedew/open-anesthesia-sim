"""Measure how far one published SD of each partition coefficient moves what the interface shows.

`docs/INTERFACE.md` § "Displayed precision" sets the finest precision of each
displayed value from these shifts. A digit far finer than the shift that one
measured SD of a coefficient causes would claim a resolution the parameters do
not support. This module holds every figure that the section states about those
shifts: the displacement table under "Why the readouts show two decimals", the
shifts of the agent-accounting panel's exhausted total, and the shifts of a
compartment's amount and share on the schematic.

**Which SD each coefficient is perturbed by.** Each SD is the published SD of
the coefficient that the model stores, taken as a fraction of its published
mean and applied to the stored value. Each run changes one coefficient by
plus one SD and by minus one SD, keeps every other parameter at its stored
value, and takes the larger shift of the two.

1. The three tissue:gas coefficients take their SDs from Yasuda, Targ and Eger,
   Anesth Analg 1989;69:370-373, Table 1 (p. 371), human tissue:gas partition
   coefficients at 37 °C, read at full text from the project owner's reference
   corpus. The stored vessel-rich coefficient is the paper's brain value, so it
   takes the brain row's SD. Table 2 of the same paper gives tissue:blood
   coefficients. Its brain row, 3.9% to 6.4% of the mean, is the SD that
   `docs/MODEL.md` used for every tissue until `PL-TDX0`.
2. The blood:gas coefficient takes its SD from the measurement made in the
   laboratory whose tissue values the model stores, where that measurement
   reports one: Eger, Anesth Analg 1987;66:971-973 for desflurane (I-653),
   and Strum and Eger, Anesth Analg 1987;66:654-656 for sevoflurane, each read
   in its PubMed abstract. No SD for isoflurane's adult blood:gas coefficient
   from that laboratory has been read: Lerman et al., Anesthesiology
   1984;61:139-143, give the adult mean 1.46 in their abstract and no SD.
   Isoflurane therefore takes the SD of Esper et al. 2015, 1.45 ± 0.12 in 41
   surgical patients, as each agent file's note on that source quotes it.

**Operating point and timing.** Every run starts from an empty system at the
agent's 1 MAC dial setting, with the reference adult's ventilation and cardiac
output and the reference circle system's opening fresh gas flow, which is what
`AgentUptakeSystem.for_agent` builds. The accounting-panel test also runs at the
agent's dial maximum and 10 L/min. The settings do not change during a run, so
the propagator over any interval is exact (`docs/MODEL.md` § "Selected method
(as implemented)"). The runs are therefore read every second, and then at
3 h and 24 h, without stepping through the 0.1 s steps in between.

**What these tests hold, and what they do not.** They pin the document's
figures to the model as shipped, so their expected values are the model's own
outputs, rounded. They are not an independent check that the model is right,
which is why they live here rather than in `tests/reference/`. Each documented
figure is the measured value rounded to two significant figures, and each test
requires that rounding to reproduce the figure exactly. So a change of a few
percent in any shift fails, and so does a document figure that came from
different SDs.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from functools import cache

import pytest

from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.governing_equations import (
    EXHAUSTED_AGENT_L,
    STATE_SIZE,
    UNIT_STATE,
    build_system_matrix,
)
from anesthesia_sim.core.matrix_exponential import matrix_exponential, propagate
from anesthesia_sim.core.numerical_envelope import PartitionCoefficient
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.patient import PatientCompartments
from anesthesia_sim.core.supported_ranges import MAXIMUM_FRESH_GAS_FLOW_L_MIN, FreshGasFlow
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

AGENTS = ("desflurane", "sevoflurane", "isoflurane")

BLOOD_GAS = "blood_gas_partition_coefficient"
VESSEL_RICH = "vessel_rich_tissue_gas_partition_coefficient"
MUSCLE = "muscle_tissue_gas_partition_coefficient"
FAT = "fat_tissue_gas_partition_coefficient"
COEFFICIENTS = (BLOOD_GAS, VESSEL_RICH, MUSCLE, FAT)

# The six displayed compartments, in the order of the model's state vector
# (`core/governing_equations.py`: inspired, alveolar, venous, then the tissues
# in `PatientCompartments.tissues` order).
COMPARTMENTS = ("circuit", "alveoli", "venous blood", "vessel-rich", "muscle", "fat")


@dataclass(frozen=True)
class PublishedMeasurement:
    """One published mean and SD, and where it was read."""

    mean: float
    sd: float
    source: str

    @property
    def relative_sd(self) -> float:
        """Return the SD as a fraction of the mean."""

        return self.sd / self.mean


_YASUDA_TABLE_1 = "Yasuda, Targ and Eger 1989, Table 1, p. 371"

PUBLISHED_SDS: dict[str, dict[str, PublishedMeasurement]] = {
    "desflurane": {
        BLOOD_GAS: PublishedMeasurement(0.424, 0.024, "Eger 1987, abstract (PMID 3631593)"),
        VESSEL_RICH: PublishedMeasurement(0.54, 0.02, f"{_YASUDA_TABLE_1}, brain"),
        MUSCLE: PublishedMeasurement(0.94, 0.35, f"{_YASUDA_TABLE_1}, muscle"),
        FAT: PublishedMeasurement(12.0, 2.0, f"{_YASUDA_TABLE_1}, fat"),
    },
    "sevoflurane": {
        BLOOD_GAS: PublishedMeasurement(
            0.686, 0.047, "Strum and Eger 1987, abstract (PMID 3605675)"
        ),
        VESSEL_RICH: PublishedMeasurement(1.15, 0.07, f"{_YASUDA_TABLE_1}, brain"),
        MUSCLE: PublishedMeasurement(2.38, 1.03, f"{_YASUDA_TABLE_1}, muscle"),
        FAT: PublishedMeasurement(34.0, 6.0, f"{_YASUDA_TABLE_1}, fat"),
    },
    "isoflurane": {
        BLOOD_GAS: PublishedMeasurement(1.45, 0.12, "Esper et al. 2015, abstract"),
        VESSEL_RICH: PublishedMeasurement(2.09, 0.10, f"{_YASUDA_TABLE_1}, brain"),
        MUSCLE: PublishedMeasurement(4.40, 1.97, f"{_YASUDA_TABLE_1}, muscle"),
        FAT: PublishedMeasurement(64.2, 12.3, f"{_YASUDA_TABLE_1}, fat"),
    },
}

# The readouts' display resolution, in percentage points. It is restated
# rather than imported because the counts below are claims about the section's
# arithmetic, which the document states for this resolution.
ONE_COUNT_PP = 0.01

# How long the readout table's runs last, and the samples of the schematic's
# amounts: every second for the first 20 minutes, then 1 h, 3 h and 24 h.
READOUT_WINDOW_S = 3600
SCHEMATIC_EVERY_SECOND_UNTIL_S = 1200
LATER_SAMPLES_S = (3600, 10800, 86400)


def two_figures(value: float) -> float:
    """Return `value` rounded to two significant figures."""

    return float(f"{value:.1e}")


@dataclass(frozen=True)
class Sample:
    """The six displayed fractions, the six amounts in litres of vapour, and the exhausted total."""

    time_s: int
    fractions: tuple[float, ...]
    amounts_l: tuple[float, ...]
    exhausted_l: float


def _system(
    agent_id: str, coefficient: str | None, factor: float, at_dial_maximum: bool
) -> AgentUptakeSystem:
    system = AgentUptakeSystem.for_agent(agent_id)
    agent = load_agent_parameters(agent_id)

    if coefficient is not None:
        changed = replace(
            agent,
            **{
                coefficient: PartitionCoefficient(
                    getattr(agent, coefficient) * factor, name=coefficient
                )
            },
        )
        system = AgentUptakeSystem(
            circuit=system.circuit,
            alveoli=system.alveoli,
            patient=PatientCompartments.from_parameters(
                agent=changed, patient=load_reference_adult_parameters()
            ),
        )

    if at_dial_maximum:
        system.set_delivered_concentration_percent(
            Percent(agent.max_delivered_concentration_percent)
        )
        system.set_fresh_gas_flow(FreshGasFlow(MAXIMUM_FRESH_GAS_FLOW_L_MIN))

    return system


@cache
def _run(
    agent_id: str, coefficient: str | None, sign: int, at_dial_maximum: bool
) -> tuple[Sample, ...]:
    """Return the samples of one run, with `coefficient` moved by `sign` SDs.

    Each amount is the compartment's capacity times its partial pressure
    fraction, as `docs/MODEL.md` § "Agent amount" defines it: the volume for a
    gas space, and the volume times the tissue:gas or blood:gas coefficient for
    blood and tissue. The capacities are worked out here from the equation
    settings rather than read from the compartments.
    """

    factor = 1.0
    if coefficient is not None:
        factor += sign * PUBLISHED_SDS[agent_id][coefficient].relative_sd

    settings = _system(agent_id, coefficient, factor, at_dial_maximum).equation_settings()
    blood_gas = settings.blood_gas_partition_coefficient
    capacities = (
        settings.circuit_volume_l,
        settings.alveolar_volume_l,
        settings.venous_volume_l * blood_gas,
        *(t.volume_l * t.tissue_blood_partition_coefficient * blood_gas for t in settings.tissues),
    )
    matrix = build_system_matrix(settings)
    one_second = matrix_exponential(matrix, 1.0)

    state: tuple[float, ...] = tuple(1.0 if i == UNIT_STATE else 0.0 for i in range(STATE_SIZE))
    samples = []

    def record(time_s: int) -> None:
        fractions = state[:6]
        samples.append(
            Sample(
                time_s,
                fractions,
                tuple(c * f for c, f in zip(capacities, fractions, strict=True)),
                state[EXHAUSTED_AGENT_L],
            )
        )

    for time_s in range(1, READOUT_WINDOW_S + 1):
        state = propagate(one_second, state)
        record(time_s)

    previous = READOUT_WINDOW_S
    for time_s in LATER_SAMPLES_S[1:]:
        state = propagate(matrix_exponential(matrix, float(time_s - previous)), state)
        record(time_s)
        previous = time_s

    return tuple(samples)


def _perturbed_runs(
    agent_id: str, coefficient: str, at_dial_maximum: bool = False
) -> tuple[tuple[Sample, ...], ...]:
    return tuple(_run(agent_id, coefficient, sign, at_dial_maximum) for sign in (1, -1))


def _worst_readout_displacement_pp(agent_id: str, coefficient: str) -> float:
    """Return the largest shift of any readout in the first hour, in percentage points."""

    base = _run(agent_id, None, 0, False)
    return max(
        abs(changed.fractions[i] - original.fractions[i]) * 100
        for run in _perturbed_runs(agent_id, coefficient)
        for original, changed in zip(base, run, strict=True)
        if original.time_s <= READOUT_WINDOW_S
        for i in range(6)
    )


def test_each_tissue_coefficient_s_sd_is_the_sd_of_the_coefficient_the_model_stores() -> None:
    """The SD of each tissue coefficient comes from the row whose mean the stored value matches.

    The stored tissue:gas coefficients descend from Yasuda's Table 1, and each
    lies within 0.71 SD of its row's mean (`docs/MODEL.md` § "Parameter
    provenance"). Table 2's brain:blood means, 1.29, 1.70 and 1.57, lie many
    SDs from the stored vessel-rich coefficients, so taking an SD from that
    table, as the section did until `PL-TDX0`, fails here.
    """

    for agent_id in AGENTS:
        agent = load_agent_parameters(agent_id)
        for coefficient in (VESSEL_RICH, MUSCLE, FAT):
            published = PUBLISHED_SDS[agent_id][coefficient]
            assert abs(getattr(agent, coefficient) - published.mean) <= published.sd, (
                agent_id,
                coefficient,
            )


@pytest.mark.parametrize(
    ("coefficient", "percent_of_mean"),
    [
        (BLOOD_GAS, (5.7, 8.3)),
        (VESSEL_RICH, (3.7, 6.1)),
        (MUSCLE, (37.0, 45.0)),
        (FAT, (17.0, 19.0)),
    ],
)
def test_the_relative_sds_are_those_the_section_states(
    coefficient: str, percent_of_mean: tuple[float, float]
) -> None:
    """Each row's SDs, as a percentage of the mean, span the range `docs/INTERFACE.md` states."""

    relative = [PUBLISHED_SDS[agent_id][coefficient].relative_sd * 100 for agent_id in AGENTS]
    assert (two_figures(min(relative)), two_figures(max(relative))) == percent_of_mean


# The displacement table in `docs/INTERFACE.md` § "Why the readouts show two
# decimals": for each coefficient, the smallest and largest over the three
# agents of the worst shift of any readout in the first hour, in percentage
# points.
DISPLACEMENT_TABLE_PP = {
    BLOOD_GAS: (2.0e-2, 8.2e-2),
    VESSEL_RICH: (1.0e-2, 4.9e-2),
    MUSCLE: (1.5e-1, 9.0e-1),
    FAT: (3.4e-3, 3.6e-2),
}


@pytest.mark.parametrize("coefficient", COEFFICIENTS)
def test_one_sd_of_each_coefficient_displaces_the_readouts_as_the_table_states(
    coefficient: str,
) -> None:
    """Each row's range, and desflurane giving the largest shift in every row."""

    shifts = {
        agent_id: _worst_readout_displacement_pp(agent_id, coefficient) for agent_id in AGENTS
    }

    assert (two_figures(min(shifts.values())), two_figures(max(shifts.values()))) == (
        DISPLACEMENT_TABLE_PP[coefficient]
    )
    assert max(shifts, key=shifts.__getitem__) == "desflurane"


def test_one_sd_is_a_third_of_a_count_to_ninety_counts_of_the_last_digit() -> None:
    """The counts that the section derives from the table, for the bound on the last digit."""

    smallest = min(low for low, _ in DISPLACEMENT_TABLE_PP.values()) / ONE_COUNT_PP
    largest = max(high for _, high in DISPLACEMENT_TABLE_PP.values()) / ONE_COUNT_PP

    assert (round(smallest, 2), round(largest)) == (0.34, 90)


# The exhausted total's shift from one SD, as `docs/INTERFACE.md`
# § "The agent-accounting panel" states it: the largest over the four
# coefficients, in litres of vapour, at 1 h and at 24 h.
EXHAUSTED_SHIFT_L = {
    (False, "desflurane"): (0.089, 0.68),
    (False, "sevoflurane"): (0.033, 0.61),
    (False, "isoflurane"): (0.026, 0.62),
    (True, "desflurane"): (0.32, 2.1),
    (True, "sevoflurane"): (0.17, 2.5),
    (True, "isoflurane"): (0.16, 2.8),
}


def _exhausted_shift_l(
    agent_id: str, at_dial_maximum: bool, time_s: int, coefficients: tuple[str, ...] = COEFFICIENTS
) -> float:
    def exhausted(run: tuple[Sample, ...]) -> float:
        return next(s.exhausted_l for s in run if s.time_s == time_s)

    base = exhausted(_run(agent_id, None, 0, at_dial_maximum))
    return max(
        abs(exhausted(run) - base)
        for coefficient in coefficients
        for run in _perturbed_runs(agent_id, coefficient, at_dial_maximum)
    )


@pytest.mark.parametrize("at_dial_maximum", [False, True], ids=["1 MAC", "dial maximum"])
@pytest.mark.parametrize("agent_id", AGENTS)
def test_the_run_totals_litre_step_at_each_agent_s_dial_maximum(
    agent_id: str, at_dial_maximum: bool
) -> None:
    """The exhausted total's one-SD shift at 1 h and 24 h, at 1 MAC and at the dial maximum."""

    measured = tuple(
        two_figures(_exhausted_shift_l(agent_id, at_dial_maximum, t)) for t in (3600, 86400)
    )
    assert measured == EXHAUSTED_SHIFT_L[(at_dial_maximum, agent_id)]
    for time_s in (3600, 86400):
        assert _exhausted_shift_l(agent_id, at_dial_maximum, time_s, (MUSCLE,)) == (
            _exhausted_shift_l(agent_id, at_dial_maximum, time_s)
        ), "the muscle coefficient's SD gives the largest shift"


def _schematic_samples(run: tuple[Sample, ...]) -> list[Sample]:
    return [
        s for s in run if s.time_s <= SCHEMATIC_EVERY_SECOND_UNTIL_S or s.time_s in LATER_SAMPLES_S
    ]


@dataclass(frozen=True)
class AmountShift:
    """One compartment's amount at one sample, and the largest shift one SD gives it."""

    agent_id: str
    compartment: str
    time_s: int
    amount_ml: float
    shift_ml: float
    share_shift_pp: float


@cache
def _amount_shifts() -> tuple[AmountShift, ...]:
    shifts = []
    for agent_id in AGENTS:
        base = _schematic_samples(_run(agent_id, None, 0, False))
        changed_runs = [
            _schematic_samples(run)
            for coefficient in COEFFICIENTS
            for run in _perturbed_runs(agent_id, coefficient)
        ]
        for k, original in enumerate(base):
            total = sum(original.amounts_l)
            for i, compartment in enumerate(COMPARTMENTS):
                shift_l = max(
                    abs(run[k].amounts_l[i] - original.amounts_l[i]) for run in changed_runs
                )
                share_shift = max(
                    abs(run[k].amounts_l[i] / sum(run[k].amounts_l) - original.amounts_l[i] / total)
                    for run in changed_runs
                )
                shifts.append(
                    AmountShift(
                        agent_id,
                        compartment,
                        original.time_s,
                        original.amounts_l[i] * 1000,
                        shift_l * 1000,
                        share_shift * 100,
                    )
                )
    return tuple(shifts)


# The largest shift of each compartment's amount from one SD, as a percentage
# of the amount, over the three agents and every sample
# (`docs/INTERFACE.md` § "A compartment's amount and share on the schematic").
LARGEST_RELATIVE_AMOUNT_SHIFT_PERCENT = {
    "circuit": 3.3,
    "alveoli": 7.9,
    "venous blood": 17.0,
    "vessel-rich": 8.2,
    "muscle": 44.0,
    "fat": 8.2,
}


def test_one_sd_shifts_each_compartment_s_amount_by_the_share_the_section_states() -> None:
    """The largest relative shift in each compartment, and the largest shift in millilitres."""

    largest = {
        compartment: max(
            s.shift_ml / s.amount_ml
            for s in _amount_shifts()
            if s.compartment == compartment and s.amount_ml > 0
        )
        * 100
        for compartment in COMPARTMENTS
    }
    assert {c: two_figures(v) for c, v in largest.items()} == LARGEST_RELATIVE_AMOUNT_SHIFT_PERCENT

    widest = max(_amount_shifts(), key=lambda s: s.shift_ml)
    assert (widest.agent_id, widest.compartment, widest.time_s, two_figures(widest.shift_ml)) == (
        "isoflurane",
        "muscle",
        86400,
        700.0,
    )


def test_a_two_figure_amount_s_finest_step_is_a_twenty_fourth_of_an_sd() -> None:
    """Where two significant figures put one step finest against one SD, and how fine.

    One step of two significant figures is a tenth of the amount's leading
    power of ten, and never less than 0.01 mL (`app/formatting.py`). Amounts
    below 0.005 mL read `<0.01 mL vapour` and show no step.
    """

    def step_ml(amount_ml: float) -> float:
        return max(10.0 ** (math.floor(math.log10(amount_ml)) - 1), 0.01)

    finest = min(
        (s for s in _amount_shifts() if s.amount_ml >= 0.005 and s.shift_ml > 0),
        key=lambda s: step_ml(s.amount_ml) / s.shift_ml,
    )
    assert (finest.agent_id, finest.compartment, finest.time_s, round(finest.amount_ml)) == (
        "sevoflurane",
        "muscle",
        10800,
        923,
    )
    assert round(finest.shift_ml / step_ml(finest.amount_ml)) == 24


def test_one_sd_moves_a_compartment_s_share_by_at_most_ten_percentage_points() -> None:
    """The largest shift of a compartment's share of the agent held, from one SD."""

    widest = max(_amount_shifts(), key=lambda s: s.share_shift_pp)
    assert (
        widest.agent_id,
        widest.compartment,
        widest.time_s,
        two_figures(widest.share_shift_pp),
    ) == ("isoflurane", "muscle", 86400, 9.8)
