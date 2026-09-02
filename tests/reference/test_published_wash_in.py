"""Compare the shipped wash-in against a published human measurement.

Every other module in `tests/reference/` checks the implementation against
itself — an analytic exponential, an RK4 oracle of this project's own
equations, mass balance, equilibrium, the zero-flow limits, directional
ordering. All of that is **verification**: the implementation solves the
intended equations correctly. None of it is **validation**: that the
equations describe the phenomenon. A model can be numerically flawless and
physiologically wrong, and a suite made only of the first would report that
as though it had settled the second.

This module is the validation half, and it is the only test here whose
expected values come from outside the repository. `F_A/F_I` at 30 minutes of
wash-in is the classic measured quantity in the uptake literature, and Yasuda
et al. published it for all three shipped agents in two volunteer studies:

- Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Liu J, Laster M, Taheri S,
  Peterson NA. *Comparison of kinetics of sevoflurane and isoflurane in
  humans.* Anesth Analg 1991;72(3):316-24. PMID 1994760,
  doi:10.1213/00000539-199103000-00007. Seven volunteers; F_A/F_I at 30 min
  of 0.850 +/- 0.018 for sevoflurane and 0.733 +/- 0.027 for isoflurane, at
  inspired concentrations of 1.0% and 0.6% respectively.
- Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Johnson BH, Freire BA,
  Fassoulaki A. *Kinetics of desflurane, isoflurane, and halothane in
  humans.* Anesthesiology 1991;74(3):489-98. PMID 2001028,
  doi:10.1097/00000542-199103000-00017. Eight volunteers; F_A/F_I at 30 min
  of 0.90 +/- 0.01 for desflurane and 0.73 +/- 0.03 for isoflurane, at
  inspired concentrations of 2.0% and 0.4% respectively.

Isoflurane therefore appears twice, in two independent cohorts, and both are
compared below. That is not redundancy: an agent the model matches in one
cohort and misses in the other would say something about the measurement's
own spread that a single comparison hides.

**Two caveats bound how strongly a pass may be read, and neither is small.**

1. *The published subjects were breathing nitrous oxide.* Both protocols ran
   65-70% N2O concurrently with the potent agent, so the measured curves
   carry a second-gas effect this model cannot reproduce: its alveolus is
   fixed-volume and single-gas, and docs/MODEL.md's "Known limitations"
   excludes nitrous oxide, simultaneous gases, and concentration and
   second-gas effects alike, while its "Assumptions" states outright that
   carrier gases are assumed not to affect kinetics. The comparison is
   therefore not perfectly matched, and the mismatch is not in an obviously
   conservative direction.
2. *These are Gas Man parameters, derived to reproduce Eger's data.* The
   partition coefficients under test descend from the same lineage as the
   measurements being tested against (docs/MODEL.md, "Parameter provenance").
   Passing shows that this implementation reproduces its parameter set's
   intent — not that the parameter set is independently right. The test could
   still have failed, which is what makes it worth running; it is weaker than
   "validated against a human measurement" and must not be described as more.

What a pass does establish is that six coupled compartments, a first-order
operator split, a circuit model, and three parameter files together land
inside the measured spread of a human study for three agents at once,
ordered correctly by solubility — which nothing else in this suite can tell
us, because nothing else looks outside the repository.

**How sharp a gate this is, measured rather than assumed.** A validation is
only worth what it can detect, so the discriminating power was measured by
perturbing each agent's blood:gas partition coefficient until the comparison
failed (2026-09-02, all other parameters shipped):

| Agent | lambda_b:g | Reference point alone | With the flow sweep |
| --- | --- | --- | --- |
| Sevoflurane | 0.65 | -14% / +21% | -14% / +6% |
| Isoflurane | 1.3 | -12% / +24% | -12% / +13% |
| Desflurane | 0.42 | -4% / +30% | -4% / +11% |

Two things follow, and both bear on how a passing run may be described.

This is a **coarse gate**. At the reference point alone a solubility error of
a fifth would survive for two of the three agents — larger than the spread
between published human measurements of the same coefficient — so a pass
excludes a structurally wrong model, not a mis-parameterized one. It is
tightest for desflurane and in the direction of *lower* solubility, because
that agent already sits at +0.79 SD and has little room left above the mean.

The **flow sweep is doing real work**, not decoration: it roughly halves the
tolerated upward error for every agent, because a parameter change that
survives at one flow does not survive at all of them. That is the reason
`test_agreement_survives_every_fresh_gas_flow` is written as a comparison
against the published values at each flow rather than as a check that the
flows agree with each other.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

import pytest

from anesthesia_sim.core.parameters import load_reference_adult_parameters
from anesthesia_sim.core.respiratory_system import MAXIMUM_SIMULATION_STEP_S, RespiratorySystem

# The measurement's own horizon: both studies administered the potent agent
# for 30 minutes and report F_A/F_I at the end of it.
WASH_IN_DURATION_S = 1800.0

# Imported rather than restated as 0.1, so this measures the model as
# shipped rather than a finer version of it no user ever sees. Raising the
# supported step is a safety-critical change to every displayed value
# (docs/MODEL.md, "Supported simulation step"); if it is ever raised, this
# validation should move with it and be re-measured, not keep quietly running
# at a step the interface no longer uses.
SIMULATION_STEP_S = MAXIMUM_SIMULATION_STEP_S

# The operating point. Alveolar ventilation and cardiac output are *not*
# chosen here: they are read from the reference-patient data file below, and
# `test_operating_point_is_the_parameter_files_own_defaults` fails if that
# ever stops being true. This matters more than anything else in the module.
# The agreement is sensitive to both axes — see
# `test_agreement_is_sensitive_to_ventilation_and_cardiac_output` — so an
# operating point picked to make the comparison pass would make the whole
# result circular. It is instead the shipped default, cited to the Gas Man
# workbook, fixed long before anyone compared this model to Yasuda.
#
# Fresh gas flow is chosen here, and is the one setting that is. Both
# protocols held an inspired concentration at the airway, so the model's F_I
# — the circuit fraction, not the vaporizer dial — should be settled rather
# than still rising at 30 minutes. A 6 L circuit at 10 L/min has a time
# constant of 36 s, so it is. This choice is nearly free either way:
# `test_agreement_survives_every_fresh_gas_flow` shows every agent stays
# inside the published spread at every flow from 1 to 10 L/min, so the pinned
# value is not carrying the result.
FRESH_GAS_FLOW_L_MIN = 10.0

# One dial setting serves four published protocols that used four different
# inspired concentrations, because the governing equations are linear in the
# delivered fraction and F_A/F_I is therefore independent of it. That is
# asserted rather than assumed, in
# `test_ratio_does_not_depend_on_the_delivered_fraction`, over the published
# concentrations themselves — read off `PUBLISHED_MEASUREMENTS` below rather
# than restated, so the checked range cannot drift from the cited one.
DELIVERED_FRACTION = 0.01

# The published spread is the tolerance. Nothing here is fitted: the width of
# this gate is the standard deviation Yasuda reported, so a parameter or
# solver change that moves an agent outside its measured human spread fails,
# and one that stays inside it does not.
AGREEMENT_TOLERANCE_SD = 1.0


@dataclass(frozen=True, slots=True)
class PublishedMeasurement:
    """One agent's measured 30-minute F_A/F_I from one published cohort."""

    agent_id: str
    mean: float
    standard_deviation: float
    cohort_size: int
    published_inspired_percent: float
    source: str

    @property
    def label(self) -> str:
        return f"{self.agent_id}/{self.source}"

    def distance_in_standard_deviations(self, ratio: float) -> float:
        """How far a modeled ratio sits from this cohort's mean, in its SDs."""

        return (ratio - self.mean) / self.standard_deviation


PUBLISHED_MEASUREMENTS = (
    PublishedMeasurement(
        agent_id="sevoflurane",
        mean=0.850,
        standard_deviation=0.018,
        cohort_size=7,
        published_inspired_percent=1.0,
        source="Anesth Analg 1991;72:316-24",
    ),
    PublishedMeasurement(
        agent_id="isoflurane",
        mean=0.733,
        standard_deviation=0.027,
        cohort_size=7,
        published_inspired_percent=0.6,
        source="Anesth Analg 1991;72:316-24",
    ),
    PublishedMeasurement(
        agent_id="desflurane",
        mean=0.900,
        standard_deviation=0.010,
        cohort_size=8,
        published_inspired_percent=2.0,
        source="Anesthesiology 1991;74:489-98",
    ),
    PublishedMeasurement(
        agent_id="isoflurane",
        mean=0.730,
        standard_deviation=0.030,
        cohort_size=8,
        published_inspired_percent=0.4,
        source="Anesthesiology 1991;74:489-98",
    ),
)

AGENT_IDS = ("sevoflurane", "isoflurane", "desflurane")

# Every inspired concentration the two protocols used, taken from the cited
# rows above so that the linearity check below covers exactly the range the
# comparisons need it to cover.
PUBLISHED_INSPIRED_PERCENTS = tuple(
    sorted({m.published_inspired_percent for m in PUBLISHED_MEASUREMENTS})
)


@cache
def _wash_in_ratio(
    agent_id: str,
    alveolar_ventilation_l_min: float | None = None,
    cardiac_output_l_min: float | None = None,
    fresh_gas_flow_l_min: float = FRESH_GAS_FLOW_L_MIN,
    delivered_fraction: float = DELIVERED_FRACTION,
) -> float:
    """Return F_A/F_I after 30 minutes of wash-in at one operating point.

    `None` for either patient flow means the reference patient's own default,
    which is what every comparison against a published value uses; the
    sensitivity tests pass explicit values to move off that point.

    F_I is the *circuit* fraction at the moment of measurement, not the
    vaporizer dial. That is the quantity the published studies measured — an
    inspired concentration at the airway — and the two are not equal here:
    alveolar uptake keeps the circuit measurably below the dial for the whole
    run, so dividing by the dial instead would understate every ratio.
    """

    patient_parameters = load_reference_adult_parameters()
    system = RespiratorySystem.for_agent(agent_id)

    system.set_fresh_gas_flow(fresh_gas_flow_l_min)
    system.set_delivered_concentration(delivered_fraction)
    system.set_alveolar_ventilation(
        patient_parameters.default_alveolar_ventilation_l_min
        if alveolar_ventilation_l_min is None
        else alveolar_ventilation_l_min
    )
    system.set_cardiac_output(
        patient_parameters.default_cardiac_output_l_min
        if cardiac_output_l_min is None
        else cardiac_output_l_min
    )

    for _ in range(round(WASH_IN_DURATION_S / SIMULATION_STEP_S)):
        system.advance(SIMULATION_STEP_S)

    return system.alveoli.concentration_fraction / system.circuit.circuit_concentration_fraction


@pytest.mark.parametrize(
    "measurement", PUBLISHED_MEASUREMENTS, ids=[m.label for m in PUBLISHED_MEASUREMENTS]
)
def test_thirty_minute_ratio_matches_published_human_measurement(
    measurement: PublishedMeasurement,
) -> None:
    """The model must land inside the published spread for every agent.

    Measured 2026-09-02 at the shipped defaults, as distance from each
    cohort's mean in that cohort's own standard deviations:

    | Agent | Cohort | Model | Published | Distance |
    | --- | --- | --- | --- | --- |
    | Sevoflurane | n=7 | 0.8528 | 0.850 +/- 0.018 | +0.15 SD |
    | Isoflurane | n=7 | 0.7413 | 0.733 +/- 0.027 | +0.31 SD |
    | Desflurane | n=8 | 0.9079 | 0.900 +/- 0.010 | +0.79 SD |
    | Isoflurane | n=8 | 0.7413 | 0.730 +/- 0.030 | +0.38 SD |

    Desflurane has the least room, at four fifths of a standard deviation,
    and that is a property of the measurement rather than of the model: its
    published spread is the tightest of the three at +/- 0.01, because a
    poorly soluble agent's curve is flat by 30 minutes and there is little
    left to vary. A future change that moves desflurane out of this band
    should be read as a real disagreement to explain, not as a tolerance to
    widen.
    """

    ratio = _wash_in_ratio(measurement.agent_id)
    distance = measurement.distance_in_standard_deviations(ratio)

    assert abs(distance) <= AGREEMENT_TOLERANCE_SD, (
        f"{measurement.agent_id} washes in to F_A/F_I {ratio:.4f} at 30 min, "
        f"{distance:+.2f} SD from the {measurement.mean} +/- "
        f"{measurement.standard_deviation} measured in {measurement.cohort_size} "
        f"volunteers ({measurement.source})"
    )


def test_published_agents_are_ordered_by_solubility() -> None:
    """The model must reproduce the ordering the studies were run to show.

    Both papers exist to test one prediction: that a less soluble agent
    approaches its inspired concentration faster. Matching three means while
    getting their order wrong would be a coincidence rather than a model, so
    the ordering is asserted separately from the values — this is the part
    that cannot be passed by three independent tolerances all happening to
    overlap.
    """

    by_agent = {agent_id: _wash_in_ratio(agent_id) for agent_id in AGENT_IDS}

    assert by_agent["desflurane"] > by_agent["sevoflurane"] > by_agent["isoflurane"]


def test_operating_point_is_the_parameter_files_own_defaults() -> None:
    """The comparison must run at shipped defaults, not at fitted flows.

    This is the assertion that makes the module's result mean anything. The
    agreement is sensitive to alveolar ventilation and cardiac output, so if
    either could be tuned here the test would be measuring the tuning. Both
    come from `reference_adult.json`, whose values are cited to the Gas Man
    workbook and were fixed in v0.1.0, long before this comparison existed.

    Changing a default in that file must therefore break this test loudly —
    by moving the flows the comparison runs at — rather than quietly leaving
    a hard-coded 4.0 and 5.0 behind, still passing and no longer describing
    the shipped model.
    """

    patient_parameters = load_reference_adult_parameters()

    assert patient_parameters.default_alveolar_ventilation_l_min == 4.0
    assert patient_parameters.default_cardiac_output_l_min == 5.0


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_ratio_does_not_depend_on_the_delivered_fraction(agent_id: str) -> None:
    """One dial setting may stand for four published inspired concentrations.

    The two protocols used 0.4%, 0.6%, 1.0% and 2.0% depending on agent and
    cohort — `PUBLISHED_INSPIRED_PERCENTS`, read off the cited rows
    themselves — while every comparison above runs at 1.0%. That
    substitution is legitimate only because the governing equations are
    linear in the delivered fraction, which makes F_A/F_I independent of it,
    so the claim is checked across the published range rather than asserted
    in a comment.

    A future change that broke this linearity (a saturable uptake term, a
    concentration-dependent coefficient) would invalidate every comparison in
    this module, and would fail here first.
    """

    ratios = [
        _wash_in_ratio(agent_id, delivered_fraction=percent / 100.0)
        for percent in PUBLISHED_INSPIRED_PERCENTS
    ]

    for ratio in ratios:
        assert ratio == pytest.approx(ratios[0], rel=1e-9)


@pytest.mark.parametrize(
    "measurement", PUBLISHED_MEASUREMENTS, ids=[m.label for m in PUBLISHED_MEASUREMENTS]
)
@pytest.mark.parametrize("fresh_gas_flow_l_min", (1.0, 2.0, 4.0, 6.0, 8.0, 10.0))
def test_agreement_survives_every_fresh_gas_flow(
    measurement: PublishedMeasurement, fresh_gas_flow_l_min: float
) -> None:
    """Fresh gas flow is the one setting chosen here, and it is not load-bearing.

    Alveolar ventilation and cardiac output come from the data file, but
    `FRESH_GAS_FLOW_L_MIN` was picked to match the protocols' held inspired
    concentration, and a reader is entitled to ask how much of the agreement
    that choice bought. The answer is none of it: across the whole supported
    flow range above zero, every agent stays inside its published spread,
    with the endpoints differing by at most about one standard deviation
    (desflurane, -0.33 SD at 1 L/min to +0.79 SD at 10 L/min).

    Zero is excluded because it is not an operating point of these
    protocols: with no fresh gas the circuit never carries agent, so F_I is
    zero and the ratio is undefined rather than wrong.
    """

    ratio = _wash_in_ratio(measurement.agent_id, fresh_gas_flow_l_min=fresh_gas_flow_l_min)
    distance = measurement.distance_in_standard_deviations(ratio)

    assert abs(distance) <= AGREEMENT_TOLERANCE_SD, (
        f"{measurement.agent_id} at {fresh_gas_flow_l_min} L/min fresh gas gives "
        f"F_A/F_I {ratio:.4f}, {distance:+.2f} SD from {measurement.source}"
    )


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_agreement_is_sensitive_to_ventilation_and_cardiac_output(agent_id: str) -> None:
    """Show how much of the tolerance the operating point is spending.

    A validation that agrees at one operating point and nowhere else is worth
    less than one that agrees over a range, and a reader cannot tell which
    this is from a passing test alone. So the sensitivity is measured rather
    than described. Measured 2026-09-02, in each cohort's own standard
    deviations, against the first published value for each agent:

    | Agent | V_A 3.0 | V_A 4.0 | V_A 5.0 | Q 4.0 | Q 5.0 | Q 6.0 |
    | --- | --- | --- | --- | --- | --- | --- |
    | Sevoflurane | -2.13 | +0.15 | +1.62 | +1.38 | +0.15 | -0.97 |
    | Isoflurane | -1.95 | +0.31 | +1.85 | +1.56 | +0.31 | -0.80 |
    | Desflurane | -1.99 | +0.79 | +2.52 | +2.18 | +0.79 | -0.45 |

    V_A 4.0 and Q 5.0 are the shipped defaults. Two distinct claims follow,
    and they are asserted separately because they are not equally strong:

    - **Ventilation.** One litre per minute either way puts all three agents
      outside their published spread. This is the sharp axis.
    - **Cardiac output.** One litre per minute either way moves every agent
      by more than a published standard deviation — comparable to the
      ventilation axis and in the opposite direction — but the band is not
      left in both directions: at 4 L/min all three fall outside it, while at
      6 L/min all three remain inside, and desflurane in fact moves *closer*
      to its published mean than the shipped default puts it. So the claim
      asserted here is the movement, not the exit, because the movement is
      what is true.

    Cardiac output belongs beside ventilation for exactly that reason. A
    reader given only the ventilation axis would under-read how specific this
    operating point is; a reader told both axes leave the band would
    over-read it.

    The window is narrow, and saying so is the point: this is a comparison at
    one physiological operating point, not a demonstration that the model
    tracks Yasuda across the ventilation and perfusion axes. What keeps it
    from being circular is not a wide window but the fact — asserted in
    `test_operating_point_is_the_parameter_files_own_defaults` — that the
    point was not chosen for it.
    """

    measurement = next(m for m in PUBLISHED_MEASUREMENTS if m.agent_id == agent_id)
    shipped_ratio = _wash_in_ratio(agent_id)

    for alveolar_ventilation_l_min in (3.0, 5.0):
        ratio = _wash_in_ratio(agent_id, alveolar_ventilation_l_min=alveolar_ventilation_l_min)

        assert abs(measurement.distance_in_standard_deviations(ratio)) > AGREEMENT_TOLERANCE_SD, (
            f"{agent_id} at {alveolar_ventilation_l_min} L/min alveolar ventilation is no "
            f"longer outside the published spread; the sensitivity this module documents "
            f"has changed and its table must be re-measured"
        )

    for cardiac_output_l_min in (4.0, 6.0):
        ratio = _wash_in_ratio(agent_id, cardiac_output_l_min=cardiac_output_l_min)
        movement_sd = abs(ratio - shipped_ratio) / measurement.standard_deviation

        assert movement_sd > AGREEMENT_TOLERANCE_SD, (
            f"{agent_id} moves only {movement_sd:.2f} SD when cardiac output goes to "
            f"{cardiac_output_l_min} L/min; the sensitivity this module documents has "
            f"changed and its table must be re-measured"
        )
