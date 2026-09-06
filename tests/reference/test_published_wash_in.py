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

What a pass does establish is that six coupled compartments, an exact
propagation of them, a circuit model, and three parameter files together land
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

from anesthesia_sim.app.wash_in import WashInDomain, read_wash_in
from anesthesia_sim.core.parameters import load_reference_adult_parameters
from anesthesia_sim.core.uptake_system import MAXIMUM_SIMULATION_STEP_S, AgentUptakeSystem

# The measurement's own horizon: both studies administered the potent agent
# for 30 minutes and report F_A/F_I at the end of it.
WASH_IN_DURATION_S = 1800.0

# The second horizon, and the papers' own: elimination begins where the
# 30 minutes above end, and both report F_A/F_A0 five minutes into it. F_A0 is
# the last alveolar fraction during administration, so this run has to be the
# continuation of the wash-in run rather than a fresh one loaded some other
# way - which is why `_eliminate()` below washes in first rather than taking a
# system from `_wash_in_system()`.
ELIMINATION_DURATION_S = 300.0

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
#
# **Which question a band of one SD answers**, since the module now makes the
# claim twice and it is not the conventional one. A deterministic model
# compared against a cohort *mean* would ordinarily be judged against the
# standard error of that mean, SD/sqrt(n), which for these cohorts is a band
# 2.6 to 2.8 times narrower. The claim asserted here is the weaker of the two
# and is deliberately so: that the model is a *plausible individual* drawn
# from the published cohort, not that it reproduces the cohort's mean. The
# distinction is not academic - desflurane's wash-in sits at +0.79 SD, which
# is +2.2 SEM, so the same run that passes the claim this module makes would
# fail the claim it does not make. A reader restating a passing run as
# "reproduces the published mean" has said something this gate never tested.
AGREEMENT_TOLERANCE_SD = 1.0

# The elimination comparison does not agree, so this constant cannot mean what
# `AGREEMENT_TOLERANCE_SD` means and is named apart from it. It is the width of
# a *regression* band - the published SD, applied around the ratio this model
# itself produces (`MODELLED_ELIMINATION_RATIOS`), so that a change moving
# washout by more than one published standard deviation fails and has to be
# explained. It asserts nothing whatever about agreement with Yasuda; the
# distance from the published mean is measured and recorded in
# `test_five_minute_elimination_ratio_against_published_human_measurement`,
# and is between +1.0 and +5.0 SD.
ELIMINATION_REGRESSION_TOLERANCE_SD = 1.0

# What the shipped parameters produce at the reference operating point,
# measured 2026-09-06 and pinned by the regression band above. These are model
# outputs and are deliberately not fields of `PublishedMeasurement`: nothing
# here was published, and a measured value sitting in a row of published ones
# is how a later reader comes to cite a model output as a human measurement.
MODELLED_ELIMINATION_RATIOS = {"sevoflurane": 0.2303, "isoflurane": 0.3195, "desflurane": 0.1603}


@dataclass(frozen=True, slots=True)
class PublishedMeasurement:
    """One agent's two measured ratios, from one published cohort.

    Both quantities come from the same subjects in the same sitting - the
    elimination followed the administration the wash-in figure ends - so
    they belong on one row rather than in two tables that could come to
    disagree about which cohort is which.

    The field names carry which ratio they describe. `mean` alone was
    unambiguous while this module compared one quantity and is not now, and
    a mean whose quantity a reader has to infer is the shape of error
    `CLAUDE.md`'s safety-critical standard treats as part of the value.
    """

    agent_id: str
    wash_in_mean: float
    wash_in_standard_deviation: float
    elimination_mean: float
    elimination_standard_deviation: float
    cohort_size: int
    published_inspired_percent: float
    source: str

    @property
    def label(self) -> str:
        return f"{self.agent_id}/{self.source}"

    def wash_in_distance_in_standard_deviations(self, ratio: float) -> float:
        """How far a modeled F_A/F_I sits from this cohort's mean, in its SDs."""

        return (ratio - self.wash_in_mean) / self.wash_in_standard_deviation

    def elimination_distance_in_standard_deviations(self, ratio: float) -> float:
        """How far a modeled F_A/F_A0 sits from this cohort's mean, in its SDs."""

        return (ratio - self.elimination_mean) / self.elimination_standard_deviation


PUBLISHED_MEASUREMENTS = (
    PublishedMeasurement(
        agent_id="sevoflurane",
        wash_in_mean=0.850,
        wash_in_standard_deviation=0.018,
        elimination_mean=0.157,
        elimination_standard_deviation=0.020,
        cohort_size=7,
        published_inspired_percent=1.0,
        source="Anesth Analg 1991;72:316-24",
    ),
    PublishedMeasurement(
        agent_id="isoflurane",
        wash_in_mean=0.733,
        wash_in_standard_deviation=0.027,
        elimination_mean=0.223,
        elimination_standard_deviation=0.024,
        cohort_size=7,
        published_inspired_percent=0.6,
        source="Anesth Analg 1991;72:316-24",
    ),
    PublishedMeasurement(
        agent_id="desflurane",
        wash_in_mean=0.900,
        wash_in_standard_deviation=0.010,
        elimination_mean=0.140,
        elimination_standard_deviation=0.020,
        cohort_size=8,
        published_inspired_percent=2.0,
        source="Anesthesiology 1991;74:489-98",
    ),
    PublishedMeasurement(
        agent_id="isoflurane",
        wash_in_mean=0.730,
        wash_in_standard_deviation=0.030,
        elimination_mean=0.220,
        elimination_standard_deviation=0.020,
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
def _wash_in_system(
    agent_id: str,
    alveolar_ventilation_l_min: float | None = None,
    cardiac_output_l_min: float | None = None,
    fresh_gas_flow_l_min: float = FRESH_GAS_FLOW_L_MIN,
    delivered_fraction: float = DELIVERED_FRACTION,
) -> AgentUptakeSystem:
    """Return the system after 30 minutes of wash-in at one operating point.

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
    system = AgentUptakeSystem.for_agent(agent_id)

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

    return system


def _wash_in_ratio(
    agent_id: str,
    alveolar_ventilation_l_min: float | None = None,
    cardiac_output_l_min: float | None = None,
    fresh_gas_flow_l_min: float = FRESH_GAS_FLOW_L_MIN,
    delivered_fraction: float = DELIVERED_FRACTION,
) -> float:
    """F_A/F_I after 30 minutes of wash-in at one operating point.

    F_I is the *circuit* fraction at the moment of measurement, not the
    vaporizer dial. That is the quantity the published studies measured - an
    inspired concentration at the airway - and the two are not equal here:
    alveolar uptake keeps the circuit measurably below the dial for the whole
    run, so dividing by the dial instead would understate every ratio.
    """

    system = _wash_in_system(
        agent_id,
        alveolar_ventilation_l_min,
        cardiac_output_l_min,
        fresh_gas_flow_l_min,
        delivered_fraction,
    )

    return system.alveoli.concentration_fraction / system.circuit.circuit_concentration_fraction


@dataclass(frozen=True, slots=True)
class EliminationReading:
    """The three fractions one elimination run leaves behind.

    A value object rather than the system itself, because `_eliminate()` is
    cached and a returned system would be a shared mutable one: a caller
    stepping it further would silently change what every later call to the
    same arguments returns. Nothing outside needs the system, so nothing
    outside gets it.

    Attributes:
        alveolar_fraction_at_discontinuation: F_A0 - the alveolar fraction at
            the moment the vaporizer was closed, which is the papers' own
            definition of the denominator.
        alveolar_fraction: F_A after `ELIMINATION_DURATION_S`.
        inspired_fraction: F_I at the same moment. Not part of the published
            ratio; it is what
            `test_elimination_is_dominated_by_the_rebreathing_circuit`
            and the module docstring's apparatus discussion are about.
    """

    alveolar_fraction_at_discontinuation: float
    alveolar_fraction: float
    inspired_fraction: float

    @property
    def ratio(self) -> float:
        """F_A/F_A0, the quantity both papers report at 5 minutes."""

        return self.alveolar_fraction / self.alveolar_fraction_at_discontinuation


@cache
def _eliminate(
    agent_id: str,
    alveolar_ventilation_l_min: float | None = None,
    cardiac_output_l_min: float | None = None,
    fresh_gas_flow_l_min: float = FRESH_GAS_FLOW_L_MIN,
    delivered_fraction: float = DELIVERED_FRACTION,
) -> EliminationReading:
    """Wash in for the published 30 minutes, then eliminate for five.

    The protocol is the papers': administer at a held inspired concentration
    for 30 minutes, record the last alveolar fraction as F_A0, discontinue,
    and read F_A five minutes later. Discontinuation is the vaporizer closed
    and nothing else - the fresh gas flow, ventilation and cardiac output all
    stay where the wash-in had them - because those are the settings the
    published subjects' own elimination held constant too.

    The system is built here rather than taken from `_wash_in_system()`,
    whose cached instance is shared with every wash-in comparison in this
    module; stepping that one into elimination would leave every later
    wash-in reading measuring a washed-out system.
    """

    patient_parameters = load_reference_adult_parameters()
    system = AgentUptakeSystem.for_agent(agent_id)

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

    alveolar_fraction_at_discontinuation = system.alveoli.concentration_fraction

    system.set_delivered_concentration(0.0)

    for _ in range(round(ELIMINATION_DURATION_S / SIMULATION_STEP_S)):
        system.advance(SIMULATION_STEP_S)

    return EliminationReading(
        alveolar_fraction_at_discontinuation=alveolar_fraction_at_discontinuation,
        alveolar_fraction=system.alveoli.concentration_fraction,
        inspired_fraction=system.circuit.circuit_concentration_fraction,
    )


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
    distance = measurement.wash_in_distance_in_standard_deviations(ratio)

    assert abs(distance) <= AGREEMENT_TOLERANCE_SD, (
        f"{measurement.agent_id} washes in to F_A/F_I {ratio:.4f} at 30 min, "
        f"{distance:+.2f} SD from the {measurement.wash_in_mean} +/- "
        f"{measurement.wash_in_standard_deviation} measured in {measurement.cohort_size} "
        f"volunteers ({measurement.source})"
    )


@pytest.mark.parametrize("agent_id", sorted({m.agent_id for m in PUBLISHED_MEASUREMENTS}))
def test_the_displayed_ratio_is_the_quantity_this_file_validates(agent_id: str) -> None:
    """The interface must draw the number these comparisons were made on.

    Everything above divides the two compartment fractions in place, which
    is the definition the published studies measured. The interface draws
    F_A/F_I through `app/wash_in.py`, which adds a domain to it. Two
    expressions of one quantity is exactly the divergence `CLAUDE.md`
    warns about - the validated number and the displayed number drifting
    apart with nothing to notice - so this asserts they are the same
    number, and that a settled 30-minute wash-in is inside the domain the
    chart will actually draw.

    It is the only place `tests/reference/` reaches into `app/`, and it
    reaches into a Flet-free module holding one arithmetic rule. What it
    buys is that a change to the displayed ratio's definition fails
    against a human measurement rather than against a unit test alone.
    """

    system = _wash_in_system(agent_id)
    reading = read_wash_in(
        system.alveoli.concentration_fraction, system.circuit.circuit_concentration_fraction
    )

    assert reading.domain is WashInDomain.WASH_IN
    assert reading.plotted_ratio == pytest.approx(_wash_in_ratio(agent_id))


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
    distance = measurement.wash_in_distance_in_standard_deviations(ratio)

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

        assert (
            abs(measurement.wash_in_distance_in_standard_deviations(ratio)) > AGREEMENT_TOLERANCE_SD
        ), (
            f"{agent_id} at {alveolar_ventilation_l_min} L/min alveolar ventilation is no "
            f"longer outside the published spread; the sensitivity this module documents "
            f"has changed and its table must be re-measured"
        )

    for cardiac_output_l_min in (4.0, 6.0):
        ratio = _wash_in_ratio(agent_id, cardiac_output_l_min=cardiac_output_l_min)
        movement_sd = abs(ratio - shipped_ratio) / measurement.wash_in_standard_deviation

        assert movement_sd > AGREEMENT_TOLERANCE_SD, (
            f"{agent_id} moves only {movement_sd:.2f} SD when cardiac output goes to "
            f"{cardiac_output_l_min} L/min; the sensitivity this module documents has "
            f"changed and its table must be re-measured"
        )


@pytest.mark.parametrize(
    "measurement", PUBLISHED_MEASUREMENTS, ids=[m.label for m in PUBLISHED_MEASUREMENTS]
)
def test_five_minute_elimination_ratio_against_published_human_measurement(
    measurement: PublishedMeasurement,
) -> None:
    """Compare the modelled 5-minute elimination against all four cohorts.

    **This comparison does not agree, and the assertion below is a regression
    band rather than an agreement claim.** Measured 2026-09-06 at the shipped
    defaults, as distance from each cohort's mean in that cohort's own
    standard deviations:

    | Agent | Cohort | Model | Published | Distance |
    | --- | --- | --- | --- | --- |
    | Sevoflurane | n=7 | 0.2303 | 0.157 +/- 0.020 | +3.67 SD |
    | Isoflurane | n=7 | 0.3195 | 0.223 +/- 0.024 | +4.02 SD |
    | Desflurane | n=8 | 0.1603 | 0.140 +/- 0.020 | +1.02 SD |
    | Isoflurane | n=8 | 0.3195 | 0.220 +/- 0.020 | +4.98 SD |

    Every row is *above* its published mean, which is the model retaining
    more alveolar agent at five minutes than the volunteers did. The module
    docstring carries the measured attribution and it is largely the
    breathing system rather than the tissue return: this model rebreathes and
    the published protocol did not, and holding the inspired fraction at zero
    instead moves the same three agents to -0.25, +0.54 and -2.40 SD.

    What is asserted here is therefore that the model still produces the
    ratios in `MODELLED_ELIMINATION_RATIOS`, to within one published standard
    deviation. That is worth asserting for the reason the wash-in comparison
    is worth asserting - it is the only thing in this repository that looks
    at elimination against an outside number at all - and a change moving it
    is a change to re-measure and explain, in whichever direction it moves.
    A change that moved these rows *inside* the published band would fail
    here too, and should: it would mean this table and the docstring around
    it are describing a model that no longer exists.
    """

    ratio = _eliminate(measurement.agent_id).ratio
    modelled = MODELLED_ELIMINATION_RATIOS[measurement.agent_id]
    drift_sd = abs(ratio - modelled) / measurement.elimination_standard_deviation
    published_distance = measurement.elimination_distance_in_standard_deviations(ratio)

    assert drift_sd <= ELIMINATION_REGRESSION_TOLERANCE_SD, (
        f"{measurement.agent_id} eliminates to F_A/F_A0 {ratio:.4f} at 5 min against the "
        f"{modelled} this module measured on 2026-09-06, a drift of {drift_sd:.2f} published "
        f"SD; it now sits {published_distance:+.2f} SD from the {measurement.elimination_mean} "
        f"+/- {measurement.elimination_standard_deviation} measured in "
        f"{measurement.cohort_size} volunteers ({measurement.source}). Re-measure this "
        f"module's tables and docs/MODEL.md's rather than widening the band"
    )


@pytest.mark.parametrize(
    "measurement", PUBLISHED_MEASUREMENTS, ids=[m.label for m in PUBLISHED_MEASUREMENTS]
)
def test_the_model_eliminates_more_slowly_than_every_published_cohort(
    measurement: PublishedMeasurement,
) -> None:
    """State the direction of the disagreement, so it cannot drift unnoticed.

    The regression band above pins the magnitude and would fail on a move in
    either direction. This pins the sign, which is the part a reader of the
    model needs: the modelled alveolar fraction at five minutes of
    elimination is higher than every published cohort's, so a learner
    watching this simulator's washout is watching a slower recovery than
    these volunteers had, not a faster one.

    Asserted separately from the magnitude because the two would be read
    differently if either changed. A magnitude that moved is a measurement to
    redo; a sign that flipped would mean the model had crossed the published
    values, and every statement in this module about which side it sits on
    would be wrong.
    """

    ratio = _eliminate(measurement.agent_id).ratio

    assert ratio > measurement.elimination_mean, (
        f"{measurement.agent_id} now eliminates to F_A/F_A0 {ratio:.4f}, at or below the "
        f"{measurement.elimination_mean} measured in {measurement.cohort_size} volunteers "
        f"({measurement.source}); the direction this module documents has reversed"
    )


def test_eliminated_agents_are_ordered_by_solubility() -> None:
    """The published elimination ordering must be reproduced.

    This is the part of the elimination comparison that is a validation
    rather than a regression, and it is the one claim here the disagreement
    above does not touch. Both papers report the same ordering - desflurane
    leaves fastest, then sevoflurane, then isoflurane - and it is the
    prediction they were run to test, in the opposite direction from the
    wash-in ordering that `test_published_agents_are_ordered_by_solubility`
    checks. Published: 0.14, 0.157, 0.22-0.223. Modelled: 0.1603, 0.2303,
    0.3195.

    An ordering is what survives the apparatus mismatch the module docstring
    measures, because the rebreathing that displaces every ratio upward
    displaces them all in the same direction. So this is a weaker claim than
    the wash-in ordering and a real one: three agents differing only in their
    partition coefficients rank correctly on the way out as well as on the
    way in.
    """

    by_agent = {agent_id: _eliminate(agent_id).ratio for agent_id in AGENT_IDS}

    assert by_agent["desflurane"] < by_agent["sevoflurane"] < by_agent["isoflurane"]


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_elimination_ratio_does_not_depend_on_the_delivered_fraction(agent_id: str) -> None:
    """One dial setting may stand for four published inspired concentrations.

    The wash-in counterpart of this test carries the argument: the governing
    equations are linear in the delivered fraction, so a ratio of two
    fractions from the same run is independent of it. It is checked again for
    the elimination ratio rather than inherited, because the two ratios are
    not the same quotient - F_A/F_A0 divides the alveolar fraction by an
    earlier value of itself, and a future nonlinearity could leave one of
    them invariant while breaking the other.
    """

    ratios = [
        _eliminate(agent_id, delivered_fraction=percent / 100.0).ratio
        for percent in PUBLISHED_INSPIRED_PERCENTS
    ]

    for ratio in ratios:
        assert ratio == pytest.approx(ratios[0], rel=1e-9)


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_elimination_is_dominated_by_the_rebreathing_circuit(agent_id: str) -> None:
    """Show that this comparison measures the apparatus, not only the patient.

    This is the assertion that keeps the elimination result from being
    over-read, and it is the mirror image of
    `test_agreement_survives_every_fresh_gas_flow`. That test shows fresh gas
    flow is *not* carrying the wash-in result: every agent stays inside its
    published spread from 1 to 10 L/min. Here the same sweep moves the
    elimination ratio across many published standard deviations, measured
    2026-09-06 as distance from the first cohort's mean:

    | Agent | 1 | 2 | 4 | 6 | 8 | 10 L/min |
    | --- | --- | --- | --- | --- | --- | --- |
    | Sevoflurane | +21.91 | +15.68 | +9.22 | +6.25 | +4.64 | +3.67 |
    | Isoflurane | +15.60 | +11.93 | +7.94 | +5.94 | +4.77 | +4.02 |
    | Desflurane | +22.66 | +14.93 | +7.14 | +3.74 | +2.01 | +1.02 |

    The mechanism is in `docs/MODEL.md` § "Model boundary": inspired gas is
    circuit gas, and the circuit is a closed recirculating path except for
    fresh-gas inflow and exhaust, so during elimination the inspired fraction
    settles near V_A/(V_A + fresh gas flow) of the alveolar one - 4/(4+10),
    or 0.29, at the highest supported flow. F_A/F_I divides that term out and
    F_A/F_A0 does not, which is the whole of why one comparison is
    flow-insensitive and the other is not.

    Both the magnitude and the direction are asserted, at the two ends of the
    supported range, so that a future circuit or ventilation change that made
    the elimination ratio flow-insensitive would fail here - and it should,
    because this module's account of why the published values are missed
    would then be wrong.
    """

    measurement = next(m for m in PUBLISHED_MEASUREMENTS if m.agent_id == agent_id)
    lowest_flow = _eliminate(agent_id, fresh_gas_flow_l_min=1.0).ratio
    highest_flow = _eliminate(agent_id, fresh_gas_flow_l_min=FRESH_GAS_FLOW_L_MIN).ratio
    movement_sd = (lowest_flow - highest_flow) / measurement.elimination_standard_deviation

    assert movement_sd > 10.0, (
        f"{agent_id} moves only {movement_sd:.2f} published SD in F_A/F_A0 between 1 and "
        f"{FRESH_GAS_FLOW_L_MIN} L/min fresh gas; this module documents the elimination "
        f"comparison as dominated by rebreathing, and that is no longer measured"
    )


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_the_elimination_run_is_outside_the_displayed_wash_in_domain(agent_id: str) -> None:
    """The interface must refuse to draw a wash-in number for this run.

    The wash-in counterpart of this test asserts that the ratio validated
    here is the ratio the chart draws. Its opposite matters just as much and
    is what `app/wash_in.py` was written for: five minutes into elimination
    the alveolar fraction is about three times the inspired one, so the
    quotient is far above `WASH_IN_EQUILIBRIUM_RATIO` and the reading is
    `WashInDomain.ELIMINATION` with no number to plot.

    Asserting it here, against a run built from a published protocol rather
    than from chosen fractions, is what `tests/unit/test_wash_in.py` cannot
    do: it shows the domain rule excludes a *physiologically real* washout
    that this simulator can be driven into, rather than a constructed pair of
    numbers. A regression that let this run plot would draw a wash-in curve
    for a patient who is waking up.
    """

    reading = _eliminate(agent_id)
    displayed = read_wash_in(reading.alveolar_fraction, reading.inspired_fraction)

    assert displayed.domain is WashInDomain.ELIMINATION
    assert displayed.plotted_ratio is None
