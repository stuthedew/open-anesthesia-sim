"""Compare the shipped model against published human measurements, in both
directions: 30 minutes of wash-in, and the five minutes of elimination that
followed it in the same volunteers.

Every other module in `tests/reference/` checks the implementation against
itself — an analytic exponential, an RK4 oracle of this project's own
equations, mass balance, equilibrium, the zero-flow limits, directional
ordering. All of that is **verification**: the implementation solves the
intended equations correctly. None of it is **validation**: that the
equations describe the phenomenon. A model can be numerically flawless and
physiologically wrong, and a suite made only of the first would report that
as though it had settled the second.

This module is the validation half, and it is the only test here whose
expected values come from outside the repository. Yasuda et al. measured both
directions in two volunteer studies, and this module uses all eight figures:

- Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Liu J, Laster M, Taheri S,
  Peterson NA. *Comparison of kinetics of sevoflurane and isoflurane in
  humans.* Anesth Analg 1991;72(3):316-24. PMID 1994760,
  doi:10.1213/00000539-199103000-00007. Seven volunteers; F_A/F_I at 30 min
  of 0.850 +/- 0.018 for sevoflurane and 0.733 +/- 0.027 for isoflurane, at
  inspired concentrations of 1.0% and 0.6% respectively; F_A/F_A0 after 5 min
  of elimination of 0.157 +/- 0.020 and 0.223 +/- 0.024.
- Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Johnson BH, Freire BA,
  Fassoulaki A. *Kinetics of desflurane, isoflurane, and halothane in
  humans.* Anesthesiology 1991;74(3):489-98. PMID 2001028,
  doi:10.1097/00000542-199103000-00017. Eight volunteers; F_A/F_I at 30 min
  of 0.90 +/- 0.01 for desflurane and 0.73 +/- 0.03 for isoflurane, at
  inspired concentrations of 2.0% and 0.4% respectively; F_A/F_A0 after 5 min
  of elimination of 0.14 +/- 0.02 and 0.22 +/- 0.02.

All eight are mean +/- SD, read from the two abstracts and checked against
PubMed on 2026-09-06. F_A0 is each paper's own definition — the last alveolar
fraction recorded during the 30-minute administration — so the elimination
ratio is anchored to the end of the wash-in the same subjects had just
completed, and the two comparisons here are one continuous protocol rather
than two.

Isoflurane therefore appears twice, in two independent cohorts, and both are
compared in both directions. That is not redundancy: an agent the model
matches in one cohort and misses in the other would say something about the
measurement's own spread that a single comparison hides.

**Why both directions.** They constrain nearly disjoint parts of the
parameter set, which is measured further down rather than assumed: the
30-minute wash-in ratio responds to blood:gas and barely to the vessel-rich
group, and the 5-minute elimination ratio does the reverse. Return *out of*
tissue is a direction no other gate in this repository exercises at all, and
a model can reproduce uptake and misstate recovery — the classic signature of
an under-parameterized tissue compartment. Recovery is also the half a
teaching simulator is most often used to demonstrate.

**The two directions return different verdicts, and the difference is the
most useful thing in this module.** The wash-in comparison agrees for every
agent and cohort, inside the published spread. The elimination comparison
does not: at the shipped defaults the model holds more alveolar agent at five
minutes than every cohort did, by +1.0 to +5.0 published SD. So what is
asserted about elimination is a *regression* band around the model's own
measured ratios, plus the claims that do hold — the published ordering, the
direction of the disagreement, and independence from the delivered fraction.
`test_five_minute_elimination_ratio_against_published_human_measurement`
carries the measured table.

**Why the elimination comparison misses, measured rather than guessed.** It
is largely apparatus, and the mechanism is a difference between the two
ratios rather than anything about tissue. F_A/F_I has the inspired fraction
in its denominator, so whatever a breathing system does to F_I divides out of
it — which is why `test_agreement_survives_every_fresh_gas_flow` finds the
wash-in comparison inside the published spread at every flow from 1 to
10 L/min. F_A/F_A0 has no such term: it is the alveolar fraction against its
own value five minutes earlier, so agent returning to the alveoli *from the
circuit* is counted exactly as though it had come back out of the patient.

This model always rebreathes. `docs/MODEL.md` § "Model boundary" gives it one
ideal circuit that is a closed recirculating path except for fresh-gas inflow
and exhaust, and inspired gas *is* circuit gas, so through an elimination the
inspired fraction settles near V_A/(V_A + fresh gas flow) of the alveolar
one — 4/(4+10), or 0.29, at the highest supported flow, and measured at 0.30
to 0.32 for the three agents at five minutes.

The published protocols did not. Neither abstract states the breathing system
directly, so this is an inference and is flagged as one - but it is a narrow
one: both report mixed expired concentrations and the volume of agent
recovered during elimination against the volume taken up, and neither
quantity can be had without collecting the whole expirate rather than
returning it to the subject. Their elimination therefore ran at an inspired
fraction at or near zero, which this model cannot be set to at any supported
flow. Confirming it against the papers' own methods sections needs the full
texts, which are not in PubMed Central and are not held in `docs/references/`.

Measured 2026-09-06 and re-measured 2026-09-07, in each cohort's own
standard deviations. Both columns are the shipped parameter set, whose
`venous_pool_volume_l` `PL-8ZJQ` raised from 1.0 L to Davis and Mapleson's
1.222 L; a larger venous pool returns more agent to the lungs, so every
shipped row moved 0.11 to 0.13 SD further above its published mean when it
did - the same direction this module attributes to the circuit rather than to
tissue return, and a tenth of the gap it adds to:

| Agent | Shipped, 10 L/min | Open circuit | Published |
| --- | --- | --- | --- |
| Sevoflurane | +3.79 SD | -0.15 SD | 0.157 +/- 0.020 |
| Isoflurane | +4.15 SD | +0.66 SD | 0.223 +/- 0.024 |
| Desflurane | +1.13 SD | -2.33 SD | 0.14 +/- 0.02 |

The second isoflurane cohort, left out of the table for width, moves from
+5.13 SD to +0.94 SD.

**The open-circuit column is a diagnostic, and the shipped simulator cannot be
put in the condition that produced it.** It comes from
`_eliminate_without_rebreathing()` below, a driver that exists only in this
module: after each step of the elimination it discards whatever the patient
exhaled into the circuit and records it as agent exhausted, so the inspired
fraction is held at zero instead of settling near a third of the alveolar one.
No fresh gas flow, dial position or patient setting reaches that condition,
and no interface control offers it. `PL-W21J` weighed a supported
non-rebreathing mode against this driver and the project owner chose the
driver on 2026-09-06, because a mode changes the model boundary and adds one
more thing the interface would have to make visible. So every number in that
column is a statement about this model's tissue return with the apparatus
taken away, and none of them is a statement about the simulator anybody runs.
Any restatement of them owes that sentence in the same breath.

**What the diagnostic separates, which is the reason it was built.** The
apparatus accounts for the whole of the gap for sevoflurane and for both
isoflurane cohorts: three of the four sit inside the published spread once it
is removed, from +3.79 to +5.13 SD outside it. It over-accounts for
desflurane, which crosses its published mean and settles 2.33 SD below - so
without rebreathing this model washes desflurane out *faster* than Yasuda's
volunteers did. That residual is a disagreement about tissue return with the
apparatus no longer available to explain it, and it is not a coefficient this
repository could correct:
`test_no_measured_tissue_solubility_reaches_desflurane_s_published_elimination`
below carries what was ruled out, and `docs/MODEL.md` "Desflurane's residual,
and why the parameter file was not changed" carries the rest of it and what is
left open. Neither column is a validation of the shipped simulator's
elimination, and no test here claims one.

**Four caveats bound how strongly either comparison may be read.** The first
two are the module's originals and apply to both directions; the third and
fourth are the elimination's own.

1. *The published subjects were breathing nitrous oxide.* Both protocols ran
   65-70% N2O concurrently with the potent agent, so the measured curves
   carry a second-gas effect this model cannot reproduce: its alveolus is
   fixed-volume and single-gas, and docs/MODEL.md's "Known limitations"
   excludes nitrous oxide, simultaneous gases, and concentration and
   second-gas effects alike, while its "Assumptions" states outright that
   carrier gases are assumed not to affect kinetics. The comparison is
   therefore not perfectly matched, and the mismatch is not in an obviously
   conservative direction. It reaches the elimination ratio through its
   denominator as well as its numerator, since F_A0 is itself a measurement
   made under N2O.
2. *These are Gas Man parameters, derived to reproduce Eger's data.* The
   partition coefficients under test descend from the same lineage as the
   measurements being tested against (docs/MODEL.md, "Parameter provenance").
   Passing shows that this implementation reproduces its parameter set's
   intent — not that the parameter set is independently right. The test could
   still have failed, which is what makes it worth running; it is weaker than
   "validated against a human measurement" and must not be described as more.
3. *The breathing systems differ, and by more than the measurement's own
   spread.* The paragraphs above measure it, at 3.5 to 4.2 published standard
   deviations per cohort. Any statement that this model eliminates more slowly
   than Yasuda's volunteers has to carry it, because most of that difference
   is a rebreathing circuit rather than a patient.
4. *This model has no metabolism, which is why five minutes is the limit.*
   Over five minutes of elimination metabolism is negligible for all three
   shipped agents, and the papers themselves bound it: recovery — agent
   recovered during elimination over agent taken up — was 101 +/- 7% for
   sevoflurane and 101 +/- 6% for isoflurane in the first study, and
   105 +/- 25% for desflurane and 102 +/- 13% for isoflurane in the second,
   against 64 +/- 9% for halothane, which is the same method detecting a
   metabolized agent. Both papers also report multi-day elimination curves.
   Those must not be added here: over days the missing metabolism is no
   longer negligible, and neither is the fat compartment's flow, which
   docs/MODEL.md's "Known limitations" records as about twice the reachable
   resting measurement and therefore acting directly on the slow tail of
   washout.

What the wash-in comparison does establish is that six coupled compartments,
an exact propagation of them, a circuit model, and three parameter files
together land inside the measured spread of a human study for three agents at
once, ordered correctly by solubility — which nothing else in this suite can
tell us, because nothing else looks outside the repository.

What the elimination comparison adds is different rather than more of the
same. The three agents rank correctly on the way out as well as on the way
in; the size and sign of this model's departure from a human elimination
measurement are recorded rather than unknown; and the vessel-rich tissue
coefficient, which the wash-in comparison barely constrains at all, is held
to about a fifth either way. The sharpness measurements below are where that
last claim comes from.

**How sharp a gate this is, measured rather than assumed.** A validation is
only worth what it can detect, so the discriminating power was re-measured
with the elimination point in it, by perturbing each agent's blood:gas
partition coefficient until some assertion in this module failed. The
perturbation rebuilds the system from a modified `AgentParameters`, so every
compartment sees the same coefficient; tissue:gas coefficients stay shipped,
which means tissue:blood moves inversely, exactly as it would if the
blood:gas measurement alone were wrong (2026-09-06):

| Agent | lambda_b:g | Reference point alone | With the flow sweep | With elimination |
| --- | --- | --- | --- | --- |
| Sevoflurane | 0.65 | -14% / +21% | -14% / +6% | -14% / +6% |
| Isoflurane | 1.3 | -11% / +24% | -11% / +12% | -11% / +12% |
| Desflurane | 0.42 | -3% / +30% | -3% / +10% | -3% / +10% |

The first two columns are a re-measurement of the table this module carried
from 2026-09-02, and reproduce it to within a percentage point everywhere
(isoflurane's edges move by one, desflurane's lower edge by one), which is
the resolution of the search rather than a change in the model.

Three things follow, and all three bear on how a run may be described.
The third is the longest, because what the elimination point is worth is
not visible in the table above it.

This is a **coarse gate**. At the reference point alone a solubility error of
a fifth would survive for two of the three agents — larger than the spread
between published human measurements of the same coefficient — so a pass
excludes a structurally wrong model, not a mis-parameterized one. It is
tightest for desflurane and in the direction of *lower* solubility, because
that agent already sits at +0.79 SD on wash-in and has little room left above
the mean.

The **flow sweep is doing real work**, not decoration: it roughly halves the
tolerated upward error for every agent, because a parameter change that
survives at one flow does not survive at all of them. That is the reason
`test_agreement_survives_every_fresh_gas_flow` is written as a comparison
against the published values at each flow rather than as a check that the
flows agree with each other.

The **elimination point adds nothing to that table**, which is the honest
reading of its last column — and it is not the whole measurement, because
blood:gas is the wrong parameter to judge it on. The two ratios respond to
almost disjoint parts of the parameter set. Movement per +10% in one
coefficient, in each ratio's own published SD (2026-09-06):

| Perturbed coefficient | Wash-in | Elimination |
| --- | --- | --- |
| Blood:gas | -0.57 to -0.64 | +0.09 to +0.17 |
| Vessel-rich tissue:gas | -0.02 to -0.06 | +0.45 to +0.55 |
| Muscle tissue:gas | -0.08 to -0.15 | -0.09 to -0.12 |
| Fat tissue:gas | -0.00 | -0.00 |

Wash-in is a blood:gas measurement that barely sees the vessel-rich group;
elimination at five minutes is a vessel-rich measurement that barely sees
blood:gas. That is not in tension with the rebreathing above: the circuit
sets *where* the elimination ratio sits against Yasuda, as a fixed offset of
the operating point, while among the model's own parameters it is
vessel-rich solubility the ratio moves with.

Neither sees fat at all, which is what a 30-minute load and a 5-minute
washout should look like, and is a further reason not to read either
comparison as covering the slow tail.

Repeating the perturbation search on the vessel-rich coefficient instead
gives what the elimination point is actually worth:

| Agent | Wash-in and its flow sweep | With elimination |
| --- | --- | --- |
| Sevoflurane | at least -90% / +25% | -16% / +19% |
| Isoflurane | at least -90% / +50% | -13% / +16% |
| Desflurane | at least -90% / +57% | -20% / +24% |

The lower edges in the middle column are the search bound rather than a
measurement: the wash-in comparison and its flow sweep were still passing at
a tenth of the shipped vessel-rich coefficient, so before this module
compared an elimination that parameter was, downward, essentially
unconstrained by anything in this repository. The elimination point closes it
to about a fifth either way. That is what the second direction buys, and it
is worth more than the blood:gas column suggests.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cache

import pytest

from anesthesia_sim.app.wash_in import WashInDomain, read_wash_in
from anesthesia_sim.core.agent_simulation_validation import AgentSimulationValidationResult
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.uptake_system import (
    MAXIMUM_SIMULATION_STEP_S,
    SECONDS_PER_MINUTE,
    AgentUptakeSystem,
)

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
MODELLED_ELIMINATION_RATIOS = {"sevoflurane": 0.2328, "isoflurane": 0.3227, "desflurane": 0.1626}

# The same quantity with the rebreathing circuit taken away, produced by
# `_eliminate_without_rebreathing()` and measured 2026-09-07. Kept in a second
# dictionary rather than as a third column of one, because these are the
# outputs of a condition the shipped simulator has no setting for and the ones
# above are the outputs of the condition it ships in: a reader who took a value
# from the wrong one would be describing a breathing system that does not
# exist. Same reason as above, they are model outputs and not fields of
# `PublishedMeasurement`.
OPEN_CIRCUIT_ELIMINATION_RATIOS = {
    "sevoflurane": 0.1541,
    "isoflurane": 0.2388,
    "desflurane": 0.0935,
}

# How far removing the rebreathing circuit has to move each cohort's comparison
# before this module's account of the elimination gap is still true. Measured
# 2026-09-07 at 3.45 to 4.20 published SD, and asserted at 3.0 -
# `test_removing_the_rebreathing_circuit_is_what_moves_the_elimination_comparison`
# carries the per-cohort table. The margin is wide deliberately: what is being
# pinned is that the apparatus term is the large one, not its fourth digit,
# which the regression bands above and below already hold.
MINIMUM_APPARATUS_MOVEMENT_SD = 3.0


@dataclass(frozen=True, slots=True)
class TissueSolubilityCeiling:
    """One published human brain:blood coefficient, used as an upper bound.

    `test_no_measured_tissue_solubility_reaches_desflurane_s_published_elimination`
    runs desflurane's elimination with its vessel-rich coefficient raised to
    each of these and asks whether the published five-minute ratio comes
    within reach. They are ceilings rather than candidate parameters: nothing
    here is proposed as a replacement for what
    `data/agents/desflurane.json` holds, and the test asserts that the
    comparison still misses rather than that it improves.

    Attributes:
        tissue_blood_partition_coefficient: the ceiling itself, as a
            tissue:blood ratio. It is multiplied by desflurane's own stored
            blood:gas coefficient to get the tissue:gas coefficient the model
            takes, so the run changes one number and keeps the agent's
            solubility in blood where its own primary measurement puts it.
        minimum_shortfall_sd: how far below the published elimination mean
            the run must still land, in that cohort's published standard
            deviations.
        what_it_is: the measurement, for the failure message. These are
            read from the abstract of Yasuda N, Targ AG, Eger EI II.
            *Solubility of I-653, sevoflurane, isoflurane, and halothane in
            human tissues.* Anesth Analg 1989;69(3):370-3, PMID 2774233,
            which reports brain:blood as 1.29 +/- 0.05 for I-653
            (desflurane), 1.57 +/- 0.10 for isoflurane and 1.70 +/- 0.09 for
            sevoflurane, mean +/- SD; checked against PubMed on 2026-09-08.
    """

    tissue_blood_partition_coefficient: float
    minimum_shortfall_sd: float
    what_it_is: str


# Two ceilings, and the second is deliberately absurd for this agent. The
# first is what desflurane's own measurement will bear; the second is the
# highest brain:blood any of the three shipped agents was measured at, which
# desflurane cannot have without inverting the ordering the source paper was
# written to report. Both still miss, which is the finding (`PL-73G7`).
DESFLURANE_TISSUE_SOLUBILITY_CEILINGS = (
    TissueSolubilityCeiling(
        tissue_blood_partition_coefficient=1.39,
        minimum_shortfall_sd=1.5,
        what_it_is="desflurane's own measured brain:blood of 1.29 +/- 0.05, at mean + 2 SD",
    ),
    TissueSolubilityCeiling(
        tissue_blood_partition_coefficient=1.70,
        minimum_shortfall_sd=0.75,
        what_it_is="sevoflurane's measured brain:blood of 1.70, the highest of the three agents",
    ),
)


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


def _private_washed_in_system(
    agent_id: str,
    alveolar_ventilation_l_min: float | None,
    cardiac_output_l_min: float | None,
    fresh_gas_flow_l_min: float,
    delivered_fraction: float,
    vessel_rich_tissue_gas_partition_coefficient: float | None = None,
) -> AgentUptakeSystem:
    """Return an unshared system after the published 30 minutes of wash-in.

    `_wash_in_system()` answers the same question and its instance must not be
    used for an elimination: it is cached and shared with every wash-in
    comparison in this module, so stepping it on would leave each of those
    measuring a washed-out system. Deliberately not cached for the same
    reason - a cached system is a shared mutable one, and both callers here
    step what they are given.

    Both elimination drivers open from this rather than keeping a copy of the
    setup each, so the operating point an elimination runs from is provably
    the one the wash-in comparisons were made at. Three copies of a
    safety-critical setup that must agree is three chances for one of them to
    stop agreeing silently.

    `vessel_rich_tissue_gas_partition_coefficient` is the module's only
    parameter override and exists for one test:
    `test_no_measured_tissue_solubility_reaches_desflurane_s_published_elimination`
    asks what the *published human tissue measurements* would produce here,
    which cannot be asked without running a coefficient the data files do not
    hold. It is applied to a system that has not been stepped, where the
    group's stored amount is zero and no propagator has been built for the old
    value, and it goes through `dataclasses.replace` rather than an attribute
    write so that `TissueGroup.__post_init__` validates the new coefficient
    exactly as it validates a shipped one. Every other caller leaves it `None`
    and gets the shipped parameter set.
    """

    patient_parameters = load_reference_adult_parameters()
    system = AgentUptakeSystem.for_agent(agent_id)

    if vessel_rich_tissue_gas_partition_coefficient is not None:
        system.patient.vessel_rich = replace(
            system.patient.vessel_rich,
            tissue_gas_partition_coefficient=(vessel_rich_tissue_gas_partition_coefficient),
        )

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

    The system comes from `_private_washed_in_system()` rather than from
    `_wash_in_system()`, whose cached instance is shared with every wash-in
    comparison in this module; stepping that one into elimination would leave
    every later wash-in reading measuring a washed-out system.
    """

    system = _private_washed_in_system(
        agent_id,
        alveolar_ventilation_l_min,
        cardiac_output_l_min,
        fresh_gas_flow_l_min,
        delivered_fraction,
    )
    alveolar_fraction_at_discontinuation = system.alveoli.concentration_fraction

    system.set_delivered_concentration(0.0)

    for _ in range(round(ELIMINATION_DURATION_S / SIMULATION_STEP_S)):
        system.advance(SIMULATION_STEP_S)

    return EliminationReading(
        alveolar_fraction_at_discontinuation=alveolar_fraction_at_discontinuation,
        alveolar_fraction=system.alveoli.concentration_fraction,
        inspired_fraction=system.circuit.circuit_concentration_fraction,
    )


def _discard_circuit_contents(system: AgentUptakeSystem) -> None:
    """Empty the circuit to the atmosphere, and record where the agent went.

    This is the whole of what makes the driver below an open circuit, and it
    is deliberately two operations rather than one. Zeroing the circuit
    fraction on its own would delete agent from a system that checks its own
    conservation: `AgentSimulationValidator` holds the identity `initial +
    delivered = exhausted + stored`, so agent taken out of the circuit and
    recorded nowhere reads as agent the model lost, and the next `advance()`
    halts the run on it. Recording the same amount as exhausted is what a
    non-rebreathing circuit does physically - the expirate leaves the system
    instead of being returned to the patient - so the identity still holds
    exactly, which `test_the_open_circuit_driver_neither_creates_nor_loses_agent`
    asserts rather than assumes.

    Both halves go through the public setters the shipped code uses, so this
    changes the apparatus and never the equations: what the patient does with
    the gas it is given is the model's, unmodified.
    """

    discarded_agent_l = system.circuit.agent_amount_l

    system.circuit.set_circuit_concentration_fraction(0.0)
    system.agent_simulation_validator.record_external_agent_transfer(
        delivered_agent_l=0.0, exhausted_agent_l=discarded_agent_l
    )


@dataclass(frozen=True, slots=True)
class OpenCircuitEliminationReading:
    """What one elimination driven at an inspired fraction of zero leaves.

    A type of its own rather than a flag on `EliminationReading`, because the
    two describe different breathing systems and only one of them describes
    the simulator that ships. A single type carrying both would let a reading
    taken under the diagnostic reach a comparison written for the shipped
    condition, which is the class of error `CLAUDE.md` treats as part of the
    value rather than beside it.

    Attributes:
        alveolar_fraction_at_discontinuation: F_A0 - the alveolar fraction at
            the moment the vaporizer was closed, which is the papers' own
            definition of the denominator. The wash-in that produced it is the
            shipped one, rebreathing and all, because that limb is already
            inside the published spread at every supported flow and F_A0 is
            defined at the end of it.
        alveolar_fraction: F_A after `ELIMINATION_DURATION_S`.
        peak_inspired_to_alveolar_ratio: the largest F_I/F_A this run reached
            at any step boundary, which is how far from a true open circuit
            the driver actually got.
            `test_the_open_circuit_driver_holds_the_inspired_fraction_near_zero`
            is what reads it.
        agent_accounting: the model's own conservation check at the end of the
            run, carried out rather than asserted here so that a failure can
            name the totals.
    """

    alveolar_fraction_at_discontinuation: float
    alveolar_fraction: float
    peak_inspired_to_alveolar_ratio: float
    agent_accounting: AgentSimulationValidationResult

    @property
    def ratio(self) -> float:
        """F_A/F_A0, the quantity both papers report at 5 minutes."""

        return self.alveolar_fraction / self.alveolar_fraction_at_discontinuation


@cache
def _eliminate_without_rebreathing(
    agent_id: str,
    alveolar_ventilation_l_min: float | None = None,
    cardiac_output_l_min: float | None = None,
    fresh_gas_flow_l_min: float = FRESH_GAS_FLOW_L_MIN,
    delivered_fraction: float = DELIVERED_FRACTION,
    elimination_fresh_gas_flow_l_min: float | None = None,
    vessel_rich_tissue_gas_partition_coefficient: float | None = None,
) -> OpenCircuitEliminationReading:
    """Wash in as shipped, then eliminate into an open circuit.

    **This is a test-only driver, and no setting of the shipped simulator
    reaches the condition it creates.** `docs/MODEL.md` gives the model one
    ideal circuit that is a closed recirculating path except for fresh-gas
    inflow and exhaust, so inspired gas is circuit gas and F_I settles near
    `V_A/(V_A + fresh gas flow)` of F_A through any elimination - 0.29 at the
    highest supported flow. The published protocols collected the whole
    expirate instead, so theirs ran at an inspired fraction at or near zero.
    Every use of this function owes that sentence wherever it states a number.

    The mechanism is `_discard_circuit_contents()` applied at the start of the
    elimination and after every step of it: whatever the patient exhaled into
    the circuit leaves the system as exhausted agent instead of being offered
    back on the next breath. Nothing else changes. The equations, the
    propagator, the compartments, the step and the operating point are the
    shipped ones, and the wash-in limb is not touched at all - so what this
    isolates is the apparatus and nothing else about the model.

    **It is an open circuit to within one step, not exactly.** Settings are
    held constant across a step, so within each one the circuit refills from
    the alveoli and F_I rises from zero to at most `V_A * step /
    circuit volume` of F_A - 1.1e-3 at the shipped step, against the 0.30 to
    0.32 the same run settles at with rebreathing, and first-order in the
    step: measured 1.111e-3, 1.111e-4 and 5.555e-5 at steps of 0.1, 0.01 and
    0.005 s. What that residual is worth in the answer was measured the same
    way on 2026-09-07: sevoflurane's ratio moves from 0.154059 at the shipped
    0.1 s step to 0.153984 at 0.005 s, which is 0.004 published SD, and the
    other two agents move less. So the numbers this driver produces are the
    F_I = 0 limit to about three parts in ten thousand, and the residual is
    reported rather than assumed away -
    `test_the_open_circuit_driver_holds_the_inspired_fraction_near_zero`
    fails if it grows.

    `elimination_fresh_gas_flow_l_min` changes the fresh gas flow at the
    moment of discontinuation and defaults to leaving it where the wash-in had
    it. Only
    `test_the_open_circuit_elimination_does_not_depend_on_fresh_gas_flow`
    passes it, to separate what the flow does to the elimination limb from
    what it does to the state the elimination starts from.

    `vessel_rich_tissue_gas_partition_coefficient` is forwarded to
    `_private_washed_in_system()`, which documents it; it replaces a shipped
    coefficient and so changes both limbs of the run, which is what the one
    test that passes it wants.
    """

    system = _private_washed_in_system(
        agent_id,
        alveolar_ventilation_l_min,
        cardiac_output_l_min,
        fresh_gas_flow_l_min,
        delivered_fraction,
        vessel_rich_tissue_gas_partition_coefficient,
    )
    alveolar_fraction_at_discontinuation = system.alveoli.concentration_fraction

    system.set_delivered_concentration(0.0)

    if elimination_fresh_gas_flow_l_min is not None:
        system.set_fresh_gas_flow(elimination_fresh_gas_flow_l_min)

    _discard_circuit_contents(system)
    peak_inspired_to_alveolar_ratio = 0.0

    for _ in range(round(ELIMINATION_DURATION_S / SIMULATION_STEP_S)):
        system.advance(SIMULATION_STEP_S)
        peak_inspired_to_alveolar_ratio = max(
            peak_inspired_to_alveolar_ratio,
            system.circuit.circuit_concentration_fraction / system.alveoli.concentration_fraction,
        )
        _discard_circuit_contents(system)

    return OpenCircuitEliminationReading(
        alveolar_fraction_at_discontinuation=alveolar_fraction_at_discontinuation,
        alveolar_fraction=system.alveoli.concentration_fraction,
        peak_inspired_to_alveolar_ratio=peak_inspired_to_alveolar_ratio,
        agent_accounting=system.agent_simulation_validation,
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
    | Sevoflurane | n=7 | 0.8528 | 0.850 +/- 0.018 | +0.16 SD |
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
    | Sevoflurane | n=7 | 0.2328 | 0.157 +/- 0.020 | +3.79 SD |
    | Isoflurane | n=7 | 0.3227 | 0.223 +/- 0.024 | +4.15 SD |
    | Desflurane | n=8 | 0.1626 | 0.140 +/- 0.020 | +1.13 SD |
    | Isoflurane | n=8 | 0.3227 | 0.220 +/- 0.020 | +5.13 SD |

    Re-measured 2026-09-07 at `venous_pool_volume_l` = 1.222 L, which moved
    every row 0.11 to 0.13 SD further above its mean (`PL-8ZJQ`).

    Every row is *above* its published mean, which is the model retaining
    more alveolar agent at five minutes than the volunteers did. The module
    docstring carries the measured attribution and it is largely the
    breathing system rather than the tissue return: this model rebreathes and
    the published protocol did not, and running the same five minutes through
    `_eliminate_without_rebreathing()` instead moves the same three agents to
    -0.15, +0.66 and -2.33 SD.
    `test_five_minute_elimination_ratio_without_rebreathing_against_published_human_measurement`
    is that comparison, and the condition it runs in is a diagnostic no
    setting of this simulator reaches.

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
    checks. Published: 0.14, 0.157, 0.22-0.223. Modelled 2026-09-07: 0.1626,
    0.2328, 0.3227.

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
    elimination ratio across many published standard deviations, re-measured
    2026-09-07 as distance from the first cohort's mean:

    | Agent | 1 | 2 | 4 | 6 | 8 | 10 L/min |
    | --- | --- | --- | --- | --- | --- | --- |
    | Sevoflurane | +21.99 | +15.78 | +9.35 | +6.38 | +4.77 | +3.79 |
    | Isoflurane | +15.69 | +12.04 | +8.07 | +6.07 | +4.91 | +4.15 |
    | Desflurane | +22.73 | +15.03 | +7.26 | +3.86 | +2.13 | +1.13 |

    End to end that is a movement of 11.5 to 21.6 published SD, which
    `test_the_open_circuit_elimination_does_not_depend_on_fresh_gas_flow` is
    the counterpart of: with the circuit discarded each step the same sweep
    moves by 4e-6 SD.

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


@pytest.mark.parametrize(
    "measurement", PUBLISHED_MEASUREMENTS, ids=[m.label for m in PUBLISHED_MEASUREMENTS]
)
def test_five_minute_elimination_ratio_without_rebreathing_against_published_human_measurement(
    measurement: PublishedMeasurement,
) -> None:
    """Compare the same five minutes against all four cohorts, apparatus removed.

    **The condition below is a diagnostic and the shipped simulator cannot be
    put in it.** `_eliminate_without_rebreathing()` holds the inspired
    fraction at zero by discarding the circuit after every step, which is
    what the published protocols' expirate collection did and what no fresh
    gas flow, dial position or patient setting in this simulator reaches.
    Nobody running the application sees these numbers, and any restatement of
    them that drops this paragraph has claimed something about the shipped
    model that is not true of it.

    What is left once the apparatus is gone, measured 2026-09-07 as distance
    from each cohort's mean in that cohort's own standard deviations, beside
    the shipped condition the module's other elimination tests measure:

    | Agent | Cohort | Shipped | Open circuit | Published |
    | --- | --- | --- | --- | --- |
    | Sevoflurane | n=7 | +3.79 SD | 0.1541, -0.15 SD | 0.157 +/- 0.020 |
    | Isoflurane | n=7 | +4.15 SD | 0.2388, +0.66 SD | 0.223 +/- 0.024 |
    | Desflurane | n=8 | +1.13 SD | 0.0935, -2.33 SD | 0.14 +/- 0.02 |
    | Isoflurane | n=8 | +5.13 SD | 0.2388, +0.94 SD | 0.22 +/- 0.02 |

    **Three of the four cohorts land inside the published spread, and
    desflurane misses on the other side.** That is the answer the driver was
    built to get, and it is worth having in both halves. For sevoflurane and
    for isoflurane in both cohorts, the rebreathing circuit accounts for the
    whole of a gap that was 3.8 to 5.1 published SD wide - so this model's
    vessel-rich return does reproduce a human elimination once the apparatus
    difference is taken out, which nothing in this repository could say
    before. For desflurane it over-accounts: the model crosses its published
    mean and settles 2.33 SD below it, washing out faster than the volunteers
    did rather than more slowly. That residual is a real disagreement about
    tissue return with the circuit no longer available to explain it. What it
    is not is the next test, and `docs/MODEL.md` "Desflurane's residual, and
    why the parameter file was not changed" carries the whole account.

    **What is asserted here is a regression band, not the agreement above.**
    Three rows landing inside the published spread is a result to state, not a
    tolerance to assert: pinning it as one would make a later model change
    that improved desflurane and moved sevoflurane to 1.1 SD look like a
    failure, and would let the same change go unnoticed if it moved
    sevoflurane from -0.15 to +0.95. So the assertion is that the driver still
    produces `OPEN_CIRCUIT_ELIMINATION_RATIOS` to within one published SD, in
    either direction, exactly as the shipped-condition comparison asserts its
    own measured ratios. The distances above are re-derived and named in the
    failure message, so a run that moves says how far it moved and against
    what.
    """

    ratio = _eliminate_without_rebreathing(measurement.agent_id).ratio
    modelled = OPEN_CIRCUIT_ELIMINATION_RATIOS[measurement.agent_id]
    drift_sd = abs(ratio - modelled) / measurement.elimination_standard_deviation
    published_distance = measurement.elimination_distance_in_standard_deviations(ratio)

    assert drift_sd <= ELIMINATION_REGRESSION_TOLERANCE_SD, (
        f"{measurement.agent_id} eliminates into an open circuit to F_A/F_A0 {ratio:.4f} at "
        f"5 min against the {modelled} this module measured on 2026-09-07, a drift of "
        f"{drift_sd:.2f} published SD; it now sits {published_distance:+.2f} SD from the "
        f"{measurement.elimination_mean} +/- {measurement.elimination_standard_deviation} "
        f"measured in {measurement.cohort_size} volunteers ({measurement.source}). This is "
        f"the diagnostic condition, which no setting of the shipped simulator reaches; "
        f"re-measure this module's tables and docs/MODEL.md's rather than widening the band"
    )


@pytest.mark.parametrize(
    "measurement", PUBLISHED_MEASUREMENTS, ids=[m.label for m in PUBLISHED_MEASUREMENTS]
)
def test_removing_the_rebreathing_circuit_is_what_moves_the_elimination_comparison(
    measurement: PublishedMeasurement,
) -> None:
    """Pin the size of the apparatus term, which is this module's whole account.

    The module docstring, `docs/MODEL.md` and two other tests here all say
    that most of the elimination disagreement is a breathing system rather
    than a patient. Until this driver existed that claim rested on a flow
    sweep, which shows the ratio is *sensitive* to the circuit without saying
    how much of the gap the circuit owns. Running the same five minutes with
    the circuit taken away answers it directly, measured 2026-09-07 in each
    cohort's own standard deviations:

    | Agent | Cohort | Shipped | Open circuit | Moved by |
    | --- | --- | --- | --- | --- |
    | Sevoflurane | n=7 | +3.79 SD | -0.15 SD | 3.94 SD |
    | Isoflurane | n=7 | +4.15 SD | +0.66 SD | 3.49 SD |
    | Desflurane | n=8 | +1.13 SD | -2.33 SD | 3.46 SD |
    | Isoflurane | n=8 | +5.13 SD | +0.94 SD | 4.20 SD |

    The movement is asserted rather than either endpoint, and downward rather
    than merely large, because that is the claim the surrounding prose makes
    and the one that would have to be withdrawn if it stopped holding. It is
    asserted at `MINIMUM_APPARATUS_MOVEMENT_SD` with a wide margin under the
    smallest measured value: what a reader needs from this test is that the
    apparatus term is several times the published spread, and the fourth digit
    of it is already held by the regression bands on both conditions.

    Note what the table does *not* say. The movement exceeds the shipped gap
    for sevoflurane and desflurane and not for isoflurane, so "the apparatus
    accounts for the gap" is true of three cohorts by arriving inside their
    spread and true of desflurane only by overshooting it. A summary that
    rounded this to "removing the circuit fixes the comparison" would be
    describing desflurane backwards.
    """

    shipped_distance = measurement.elimination_distance_in_standard_deviations(
        _eliminate(measurement.agent_id).ratio
    )
    open_circuit_distance = measurement.elimination_distance_in_standard_deviations(
        _eliminate_without_rebreathing(measurement.agent_id).ratio
    )
    movement_sd = shipped_distance - open_circuit_distance

    assert movement_sd > MINIMUM_APPARATUS_MOVEMENT_SD, (
        f"{measurement.agent_id} moves only {movement_sd:+.2f} published SD when the "
        f"rebreathing circuit is removed, from {shipped_distance:+.2f} to "
        f"{open_circuit_distance:+.2f} SD against {measurement.source}; this module and "
        f"docs/MODEL.md attribute most of the elimination disagreement to the breathing "
        f"system, and that attribution is what has changed"
    )


@pytest.mark.parametrize(
    "ceiling",
    DESFLURANE_TISSUE_SOLUBILITY_CEILINGS,
    ids=[f"{c.tissue_blood_partition_coefficient}" for c in DESFLURANE_TISSUE_SOLUBILITY_CEILINGS],
)
def test_no_measured_tissue_solubility_reaches_desflurane_s_published_elimination(
    ceiling: TissueSolubilityCeiling,
) -> None:
    """Desflurane's open-circuit residual is not a solubility this file could hold.

    The test above leaves desflurane 2.33 published SD *below* its cohort's
    mean once the rebreathing circuit is gone - washing out faster than the
    volunteers did, and on the opposite side from every other row. The
    module's own sensitivity table says that ratio is a vessel-rich
    tissue:gas measurement (+0.45 to +0.55 published SD per +10%), so the
    obvious reading is that desflurane's vessel-rich coefficient is too low.
    This test is what closes that reading off, and it is the reason
    `data/agents/desflurane.json` was not changed (`PL-73G7`).

    Raising the coefficient alone does reach the published mean: at
    lambda_(vrg:b) = 2.24, against the shipped 1.286, the ratio lands on 0.140
    and the wash-in row stays inside its spread at +0.55 SD, because the
    vessel-rich group is fully equilibrated after 30 minutes and its capacity
    is nearly invisible in F_A/F_I (measured 2026-09-08). What rules the
    change out is not this model but the tissue measurement. Run the same
    solve against each cohort's published ratio and the coefficients it
    demands are:

    | Agent | Demanded | Yasuda 1989 measured brain:blood | Distance |
    | --- | --- | --- | --- |
    | Sevoflurane | 1.74 | 1.70 +/- 0.09 | +0.42 SD |
    | Isoflurane | 1.45 | 1.57 +/- 0.10 | -1.24 SD |
    | Desflurane | 2.24 | 1.29 +/- 0.05 | +19 SD |

    Two of the three land on the measurement. Desflurane's demand is nineteen
    standard deviations above its own and above what either other agent
    demands - it would make desflurane the *most* tissue-soluble of the three,
    inverting the ordering the source paper exists to report. So the
    residual cannot be this coefficient, and the assertion below is the
    contrapositive: give desflurane a vessel-rich coefficient the published
    human tissue data will bear and its elimination still misses on the same
    side. Measured 2026-09-08:

    | Coefficient given | F_A/F_A0 at 5 min | Against 0.14 +/- 0.02 |
    | --- | --- | --- |
    | 1.286, shipped | 0.0935 | -2.33 SD |
    | 1.39, its own mean + 2 SD | 0.0998 | -2.01 SD |
    | 1.70, sevoflurane's | 0.1167 | -1.17 SD |

    **The two thresholds differ because the two ceilings claim different
    things.** At desflurane's own measurement the residual is asserted to
    exceed 1.5 SD, which still leaves 0.5 SD of margin under the measured
    2.01 and says the published ratio is nowhere near reachable. At
    sevoflurane's coefficient it is asserted only to exceed 0.75 SD, because
    the measured 1.17 is genuinely close to the published spread's edge: a
    reader should take from this that no admissible value reaches the
    published *mean*, and not that the gap survives every conceivable value.
    Asserting 1.0 at both would have hidden that difference behind a margin
    of 0.17 SD.

    This runs the diagnostic open circuit, so the caveat every other use of
    it carries applies here too: no setting of the shipped simulator reaches
    the condition, and nothing here is a statement about what a user sees.
    """

    measurement = next(m for m in PUBLISHED_MEASUREMENTS if m.agent_id == "desflurane")
    blood_gas = load_agent_parameters("desflurane").blood_gas_partition_coefficient
    ratio = _eliminate_without_rebreathing(
        "desflurane",
        vessel_rich_tissue_gas_partition_coefficient=(
            ceiling.tissue_blood_partition_coefficient * blood_gas
        ),
    ).ratio
    shortfall_sd = -measurement.elimination_distance_in_standard_deviations(ratio)

    assert shortfall_sd > ceiling.minimum_shortfall_sd, (
        f"desflurane given a vessel-rich tissue:blood coefficient of "
        f"{ceiling.tissue_blood_partition_coefficient} ({ceiling.what_it_is}) eliminates "
        f"into an open circuit to F_A/F_A0 {ratio:.4f} at 5 min, only {shortfall_sd:.2f} "
        f"published SD below the {measurement.elimination_mean} +/- "
        f"{measurement.elimination_standard_deviation} measured in "
        f"{measurement.cohort_size} volunteers ({measurement.source}). This module and "
        f"docs/MODEL.md say the residual is out of reach of any vessel-rich solubility "
        f"the human tissue measurements support, and that is what has changed - re-open "
        f"the question rather than raising the shipped coefficient to meet it"
    )


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_the_open_circuit_driver_holds_the_inspired_fraction_near_zero(agent_id: str) -> None:
    """Show that the diagnostic is the condition it claims to be.

    A driver that only partly removed the rebreathing would produce numbers
    between the two conditions and label them as one of them, which is the
    failure mode a diagnostic has and an ordinary test does not: nothing else
    in this module would notice, because the ratio it produces is plausible
    either way.

    The residual has a closed form. Settings are held constant across a step,
    so between two discards the circuit refills from the alveoli at the
    alveolar ventilation and F_I reaches at most `V_A * step / V_circuit` of
    F_A, which is 1.11e-3 at the shipped 4 L/min, 0.1 s and 6 L. The bound is
    computed here from the same parameter files the run uses rather than
    written down, so a change to any of the three moves the assertion with it.
    Measured 2026-09-07 at 1.111e-3 for all three agents, against the 0.30 to
    0.32 the same runs settle at with rebreathing: the driver is about 280
    times closer to an open circuit than the shipped condition is, and
    first-order in the step, so a shorter step gets proportionally closer.
    """

    patient_parameters = load_reference_adult_parameters()
    circuit_volume_l = AgentUptakeSystem.for_agent(agent_id).circuit.circuit_volume_l
    bound = (
        patient_parameters.default_alveolar_ventilation_l_min
        / SECONDS_PER_MINUTE
        * SIMULATION_STEP_S
        / circuit_volume_l
    )

    peak = _eliminate_without_rebreathing(agent_id).peak_inspired_to_alveolar_ratio

    assert peak <= bound, (
        f"{agent_id} reaches F_I/F_A of {peak:.3e} inside a step of the open-circuit "
        f"diagnostic, above the {bound:.3e} that {SIMULATION_STEP_S} s of refilling at "
        f"{patient_parameters.default_alveolar_ventilation_l_min} L/min into "
        f"{circuit_volume_l} L can produce; the driver is no longer an open circuit and "
        f"the numbers it produces are between the two conditions rather than at one of them"
    )


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_the_open_circuit_driver_neither_creates_nor_loses_agent(agent_id: str) -> None:
    """The diagnostic must move agent out of the system, not delete it.

    `_discard_circuit_contents()` writes a compartment directly, which is the
    one thing in this module that steps outside `advance()`'s own accounting.
    Zeroing the circuit and forgetting to record the agent as exhausted would
    leave the model's conservation identity short by everything the patient
    exhaled - and the failure would not be loud in the direction that matters,
    because agent removed from the circuit and unrecorded looks exactly like a
    model that eliminates well.

    So the model's own check is read at the end of the run rather than
    trusted. It is the same `AgentSimulationValidator` that can halt a live
    simulation, holding `initial + delivered = exhausted + stored`; measured
    2026-09-07 at a relative error of 3e-13, which is arithmetic rather than
    accounting.
    """

    accounting = _eliminate_without_rebreathing(agent_id).agent_accounting

    assert accounting.passes_validation, (
        f"the open-circuit diagnostic leaves {accounting.unaccounted_agent_l:.3e} L of "
        f"{agent_id} unaccounted for after 5 minutes - {accounting.initial_agent_l:.4f} L "
        f"initial plus {accounting.delivered_agent_l:.4f} L delivered against "
        f"{accounting.exhausted_agent_l:.4f} L exhausted and "
        f"{accounting.currently_stored_agent_l:.4f} L stored, a relative error of "
        f"{accounting.relative_error:.2e}; the driver is deleting agent rather than "
        f"discarding it, and every ratio it produces is wrong in the fast direction"
    )


@pytest.mark.parametrize("agent_id", AGENT_IDS)
@pytest.mark.parametrize("elimination_fresh_gas_flow_l_min", (0.0, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0))
def test_the_open_circuit_elimination_does_not_depend_on_fresh_gas_flow(
    agent_id: str, elimination_fresh_gas_flow_l_min: float
) -> None:
    """The mirror of `test_elimination_is_dominated_by_the_rebreathing_circuit`.

    That test measures the shipped elimination moving across 11.5 to 21.6
    published standard deviations between 1 and 10 L/min, because F_I settles at
    `V_A/(V_A + fresh gas flow)` of F_A and the published ratio has no term to
    divide it out. This one measures the same sweep with the circuit
    discarded each step, over the whole supported flow range including zero,
    and finds a spread of 4e-6 published SD (2026-09-07), against the 11.5 to
    21.6 SD the shipped condition moves over the narrower 1 to 10 L/min.

    That is the strongest single piece of evidence that the driver removes the
    apparatus term rather than shrinking it, and it is stronger than the
    residual bound the previous test asserts: a driver that merely reduced
    rebreathing would still carry the flow dependence, because the dependence
    is in what the circuit returns and not in how much of it there is.

    Only the elimination limb's flow is swept. The wash-in stays at
    `FRESH_GAS_FLOW_L_MIN`, so what is held fixed is the state the elimination
    opens from - which does still depend on the flow it was loaded at, by 0.23
    to 0.32 published SD across the same range. That residual belongs to the
    initial condition rather than to the apparatus, and separating the two is
    the reason `_eliminate_without_rebreathing()` takes the flow twice.
    """

    reference = _eliminate_without_rebreathing(agent_id).ratio
    swept = _eliminate_without_rebreathing(
        agent_id, elimination_fresh_gas_flow_l_min=elimination_fresh_gas_flow_l_min
    ).ratio
    measurement = next(m for m in PUBLISHED_MEASUREMENTS if m.agent_id == agent_id)
    movement_sd = abs(swept - reference) / measurement.elimination_standard_deviation

    assert movement_sd < 1e-4, (
        f"{agent_id} moves {movement_sd:.2e} published SD in F_A/F_A0 when the open-circuit "
        f"elimination runs at {elimination_fresh_gas_flow_l_min} L/min fresh gas rather than "
        f"{FRESH_GAS_FLOW_L_MIN}; the diagnostic is supposed to have removed the flow "
        f"dependence entirely, and it has not"
    )
