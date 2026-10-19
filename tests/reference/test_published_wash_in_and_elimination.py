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
asserted about elimination is a *regression* pin on the model's own
measured ratios, plus the claims that do hold — the published ordering, the
direction of the disagreement, and independence from the delivered fraction.
`test_five_minute_elimination_ratio_regression_pin` carries the measured
table.

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
   The intent itself is worth least where this module's wash-in direction
   looks: Gas Man's own published agreement with patients is materially worse
   through wash-in than through maintenance (docs/MODEL.md, "Known
   limitations").
3. *The breathing systems differ, and by more than the measurement's own
   spread.* The paragraphs above measure it, at 3.5 to 4.2 published standard
   deviations per cohort. Any statement that this model eliminates more slowly
   than Yasuda's volunteers has to carry it, because most of that difference
   is a rebreathing circuit rather than a patient.
4. *This model has no metabolism, and nothing on the scale of the fourth
   compartment human washout needs; five minutes is inside what both allow.*
   Over five minutes of elimination metabolism is negligible for all three
   shipped agents, and the papers themselves bound it: recovery — agent
   recovered during elimination over agent taken up — was 101 +/- 7% for
   sevoflurane and 101 +/- 6% for isoflurane in the first study, and
   105 +/- 25% for desflurane and 102 +/- 13% for isoflurane in the second,
   against 64 +/- 9% for halothane, which is the same method detecting a
   metabolized agent. Both papers also report multi-day elimination curves.
   Those must not be added here: over days the missing metabolism is no
   longer negligible, and neither is the fat compartment's flow, which
   docs/MODEL.md's "Known limitations" weighs against two human sources that
   disagree about its direction (about twice a resting depot measurement; at
   or a little below what the same papers' washout fits imply) and which acts
   on the slow tail of washout either way. The measured tail leaves what this
   model can follow long before days, though, and inside the 24 hours a run
   is supported for: every washout these papers fitted needed a fourth
   compartment between muscle and fat, which this model has no counterpart
   for, and on the published mean coefficients its term is the largest in
   the measured curve from about 1.8 to 3.1 hours after the 30-minute
   administration until about 20.7 to 29.4 hours (docs/MODEL.md, the
   intertissue-diffusion note under "Known limitations"). At five minutes it
   is about one part in twenty of what remains. So the gap over those hours
   is measured beside this gate rather than gated by it:
   test_late_washout_against_published_fits.py, in this directory, records
   its size and direction over the first 24 hours (docs/MODEL.md, "The first
   24 hours of elimination against the published mean curves") and asserts
   no agreement.

What the wash-in comparison does establish is that six coupled compartments,
an exact propagation of them, a circuit model, and three parameter files
together land inside the measured spread of a human study for three agents at
once, ordered correctly by solubility — which nothing else in this suite can
tell us, because nothing else in it is gated on a human measurement: the
module beside it looks outside the repository too, and asserts nothing about
agreement.

What the elimination comparison adds is different rather than more of the
same. The three agents rank correctly on the way out as well as on the way
in, and the size and sign of this model's departure from a human elimination
measurement are recorded rather than unknown. It also puts a lower bound on
the vessel-rich tissue coefficient, which the wash-in comparison barely sees.
That bound is looser than this docstring said before 2026-10-17, and the next
section gives the numbers.

**How sharp a gate this is, measured rather than assumed.** A validation is
only worth what it can detect. So each stored parameter was multiplied by a
factor, for one agent at a time, and the factor was searched until some
published-data assertion failed. This was first done on 2026-10-17
(`PL-9YHR`) and repeated on 2026-10-18, once the early wash-in points had
joined the gate (`PL-R0NL`). The published-data gate means the assertions
whose expected value is a published measurement: the early wash-in points
from 1 to 25 minutes, the 30-minute wash-in band for each cohort at every
swept fresh gas flow, the sign of the elimination disagreement for each
cohort, and both solubility orderings. `_published_data_gate_failures()` runs
exactly that set, and `StoredParameterChange` applies each change. The
regression pins are left out. A pin fails on any change at all, so it shows
that something moved and never that a published value would have caught the
change.

`docs/MODEL.md` § "What the published-data gate can and cannot resolve" holds
the measured table, and these are its main points:

- **Blood:gas and the vessel-rich group are resolved on both sides.** A
  stored blood:gas value passes from -5% to +5% for sevoflurane, from -1% to
  +5% for isoflurane and from -1% to +10% for desflurane. The vessel-rich
  tissue:gas coefficient passes from -15% to +15%, from -4% to +11% and from
  -6% to +55%. A pass still excludes a structurally wrong model, not a
  mis-parameterized one.
- **A narrow edge is not a narrow uncertainty.** Most lower edges come from
  the 12.5- and 15-minute points, where the shipped model already sits at
  +0.75 to +0.94 SD. A small change crosses +1 SD there, so a -1% edge says
  the model has used most of the band, not that the coefficient is known to
  1%. The figure's reading error is about 0.3 SD.
- **The early points see the alveolar gas volume from above.** It passes
  only up to +19% for sevoflurane, +21% for isoflurane and +33% for
  desflurane, through the 1-minute point.
- **The gate cannot see fat for sevoflurane or isoflurane.** Both pass with
  the fat tissue:gas coefficient, or the fat volume, anywhere from a tenth to
  four times the stored value. A smaller circuit passes down to a tenth for
  those two agents as well, because the early points hold F_I at the airway
  and never see the circuit. Muscle is held only loosely.

Before 2026-10-17 this docstring said the elimination point held the
vessel-rich coefficient to about a fifth either way. That figure came from an
elimination assertion that held the model's own ratio to within one published
SD. It was a regression pin with a wide band, not a comparison with the
published value, so it never measured what a published value can detect.
`PL-RXW0` has since narrowed that pin to 1e-4.

`test_the_published_data_gate_fails_at_a_stated_perturbation` and
`test_the_published_data_gate_passes_at_a_stated_perturbation` hold the
table to the code. The first fails if the gate stops detecting a blood:gas,
vessel-rich or alveolar gas volume change that it detects today. The second
fails if the gate starts detecting a change that the documentation says it
cannot, so that the table is measured again rather than left stale.

The two ratios respond to almost disjoint parts of the parameter set. Here is
the movement per +10% in one coefficient, in each ratio's own published SD
(2026-09-06):

| Perturbed coefficient | Wash-in | Elimination |
| --- | --- | --- |
| Blood:gas | -0.57 to -0.64 | +0.09 to +0.17 |
| Vessel-rich tissue:gas | -0.02 to -0.06 | +0.45 to +0.55 |
| Muscle tissue:gas | -0.08 to -0.15 | -0.09 to -0.12 |
| Fat tissue:gas | -0.00 | -0.00 |

Wash-in at 30 minutes is a blood:gas measurement that barely sees the
vessel-rich group, and elimination at five minutes is a vessel-rich
measurement that barely sees blood:gas. That is not in tension with the
rebreathing above. The circuit sets *where* the elimination ratio sits
against Yasuda, as a fixed offset of the operating point. Among the model's
own parameters, it is vessel-rich solubility that the ratio moves with.
Neither ratio sees fat, which is what a 30-minute load and a 5-minute washout
should look like. That is a further reason not to read either comparison as
covering the slow tail.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass, replace
from functools import cache, partial

import pytest

from anesthesia_sim.app.wash_in import WashInDomain, read_wash_in
from anesthesia_sim.core.agent_simulation_validation import AgentSimulationValidationResult
from anesthesia_sim.core.concentration import Fraction, Percent, fraction_from_percent
from anesthesia_sim.core.parameters import (
    load_agent_parameters,
    load_reference_adult_parameters,
    load_reference_circle_system_parameters,
)
from anesthesia_sim.core.patient import PatientCompartments
from anesthesia_sim.core.simulation_step import MAXIMUM_SIMULATION_STEP_S, SimulationStep
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow
from anesthesia_sim.core.units import SECONDS_PER_MINUTE
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

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
SIMULATION_STEP_S = SimulationStep(MAXIMUM_SIMULATION_STEP_S)

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
DELIVERED_PERCENT = 1.0

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

# The elimination comparison does not agree, so its assertions are regression
# pins rather than agreement claims. Each holds the ratio this model itself
# produces (`MODELLED_ELIMINATION_RATIOS`, `OPEN_CIRCUIT_ELIMINATION_RATIOS`)
# to this absolute tolerance, so any change to washout fails and has to be
# explained. The ratios are stored to four decimals, so rounding them moves
# them by at most 5e-5, and 1e-4 leaves room for that and nothing a model
# change would produce. Until `PL-RXW0` the pin was one published SD, a band
# of 6% to 12% relative, which let desflurane's ratio drift by 12% while every
# table quoting it went stale. It asserts nothing about agreement with Yasuda.
# The distance from the published mean is measured in
# `test_five_minute_elimination_ratio_regression_pin`, and is between +1.0 and
# +5.0 SD.
ELIMINATION_RATIO_PIN_TOLERANCE = 1e-4

# What the shipped parameters produce at the reference operating point,
# measured 2026-09-06 and pinned to the tolerance above. These are model
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
# which the regression pins above and below already hold.
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


# The published apparatus's own dead space, read from the primary source rather
# than assumed. Yasuda 1991 *Anesthesiology* (PMID 2001028) SS "Materials and
# Methods" puts about 50 ml of corrugated Teflon between the tracheal end-tidal
# sampling port and the connection to the nonrebreathing valve, stated there to
# protect the end-tidal sample from contamination with inspired gas. Both
# papers were supplied by the project owner and read on 2026-09-13; neither is
# in PubMed Central and neither is held in this repository.
APPARATUS_DEAD_SPACE_L = 0.050

# **That volume is a series dead space, and in this model a series dead space
# is a ventilation decrement rather than a non-zero F_I.** The distinction is
# the whole of why the diagnostic below is run the way it is, so it is derived
# here rather than asserted.
#
# Take one breath during the elimination, with the fresh gas agent-free, and
# let V_D be the total series dead space - anatomic plus apparatus. At
# end-expiration both dead spaces hold alveolar gas at F_A. Inspiration pushes
# that V_D back into the alveoli and follows it with (V_T - V_D) of agent-free
# gas, so the alveoli receive V_T of gas carrying V_D * F_A of agent and expel
# V_T of gas carrying V_T * F_A. The net is
#
#     V_D * F_A - V_T * F_A = -(V_T - V_D) * F_A
#
# which is exactly this model's `V_A_dot * (F_I - F_A)` with F_I = 0, provided
# V_A_dot is the *true* alveolar ventilation (V_T - V_D) * f. So adding the
# apparatus's 50 ml at constant tidal volume and rate lowers alveolar
# ventilation by 50 ml * f and does nothing else. Treating it instead as a
# non-zero inspired fraction - the shape of the sixth candidate row in
# `docs/MODEL.md` SS "Desflurane's residual" - describes a mixing volume that
# returns a *fraction* of every breath, which is this model's circuit and not
# the published apparatus.
#
# The model carries no respiratory rate, so the decrement cannot be computed
# from stored parameters. These are the rates the diagnostic is run at: the
# conventional range for a paralysed, mechanically ventilated, normocapnic
# adult. **Yasuda measured minute ventilation and derived the alveolar
# fraction from F_M = f_A * F_A + f_D * F_I; the numeric value is in the
# methods text and is not held here** (`PL-ZDWL`), so the range below stands
# in for it and is an assumption of this diagnostic rather than a datum.


@dataclass(frozen=True, slots=True)
class ApparatusDeadSpaceCase:
    """One respiratory rate, and how far desflurane must still miss at it.

    Attributes:
        respiratory_rate_per_min: breaths per minute, which with
            `APPARATUS_DEAD_SPACE_L` fixes the alveolar-ventilation decrement
            the published apparatus's dead space is worth.
        minimum_shortfall_sd: how far below its published elimination mean
            desflurane must still land, in that cohort's published standard
            deviations. Measured 2026-09-13 and asserted with margin.
    """

    respiratory_rate_per_min: float
    minimum_shortfall_sd: float

    @property
    def alveolar_ventilation_l_min(self) -> float:
        """The reference default, less what the apparatus dead space costs.

        The baseline is read from the parameter file rather than restated, so
        this diagnostic follows the reference adult if its default ventilation
        is ever changed instead of silently comparing against a stale number.
        """

        return (
            load_reference_adult_parameters().default_alveolar_ventilation_l_min
            - APPARATUS_DEAD_SPACE_L * self.respiratory_rate_per_min
        )


# Measured 2026-09-13 across the conventional range. Desflurane's open-circuit
# residual is -2.33 SD with no apparatus dead space at all; the shortfalls
# below are what is left of it once the sourced dead space is applied, so the
# largest of them carries 0.44 SD of the 2.33 and the smallest 0.95 SD.
APPARATUS_DEAD_SPACE_CASES = (
    ApparatusDeadSpaceCase(respiratory_rate_per_min=6.0, minimum_shortfall_sd=1.75),
    ApparatusDeadSpaceCase(respiratory_rate_per_min=8.0, minimum_shortfall_sd=1.60),
    ApparatusDeadSpaceCase(respiratory_rate_per_min=10.0, minimum_shortfall_sd=1.40),
    ApparatusDeadSpaceCase(respiratory_rate_per_min=12.0, minimum_shortfall_sd=1.25),
)

# The largest decrement the wash-in comparison will bear: at 50 ml and 11
# breaths per minute every wash-in row is still inside its published spread,
# sevoflurane's nearest the edge at -0.96 SD, and one breath per minute more
# takes it outside (-1.08 SD at 12). Measured 2026-09-13.
LARGEST_ADMISSIBLE_DEAD_SPACE_CASE = ApparatusDeadSpaceCase(
    respiratory_rate_per_min=11.0, minimum_shortfall_sd=1.25
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


@dataclass(frozen=True, slots=True)
class PublishedTimePoint:
    """One point on a published F_A/F_I curve during administration.

    Both papers give the early time course only as Figure 2, a plot of mean
    and SD with each SD drawn as a one-sided bar. So every value here was read
    from a scan of the printed figure, not from a table. Reading the same
    figures' 30-minute points this way lands within 0.006 of the 30-minute
    means the papers' text states, which is the size of a reading error here.
    The note `docs/references/yasuda-1991-figure-2-wash-in.md` gives the
    method, the figure and page, and every value read.

    Attributes:
        agent_id: the agent.
        time_min: minutes from the start of administration. It is the
            protocol's sample time that the plotted point sits at.
        mean: the cohort's mean F_A/F_I, read from the figure.
        standard_deviation: the cohort's SD of F_A/F_I, read as the length of
            the error bar.
        standard_deviation_read_at_min: the sample time whose error bar gave
            `standard_deviation`. It equals `time_min` except at 1 minute for
            three cohorts, where the bar is lost among overlapping marks near
            the axis. There the SD is the cohort's next readable bar, a stand-in
            and not a reading of the 1-minute bar.
        cohort_size: the number of volunteers.
        source: the paper, as `PublishedMeasurement.source` names it.
    """

    agent_id: str
    time_min: float
    mean: float
    standard_deviation: float
    standard_deviation_read_at_min: float
    cohort_size: int
    source: str

    @property
    def label(self) -> str:
        return f"{self.agent_id}/{self.source}/{self.time_min:g}min"

    def distance_in_standard_deviations(self, ratio: float) -> float:
        """How far a modeled F_A/F_I sits from this point's mean, in its SD."""

        return (ratio - self.mean) / self.standard_deviation


def _time_course(
    agent_id: str, source: str, cohort_size: int, rows: tuple[tuple[float, ...], ...]
) -> tuple[PublishedTimePoint, ...]:
    """Build one cohort's points from rows of (time, mean, SD, time the SD was read at)."""

    return tuple(
        PublishedTimePoint(
            agent_id=agent_id,
            time_min=time_min,
            mean=mean,
            standard_deviation=standard_deviation,
            standard_deviation_read_at_min=read_at_min,
            cohort_size=cohort_size,
            source=source,
        )
        for time_min, mean, standard_deviation, read_at_min in rows
    )


# Figure 2 of each paper, read from the page scans on 2026-10-18 (`PL-R0NL`).
# The 30-minute points are left out because `PUBLISHED_MEASUREMENTS` holds the
# values the text states for them. Desflurane's 20-minute point is left out
# because its error bar is hidden behind the marker, so its SD is known only to
# be less than about 0.011. Each row is (minutes, mean, SD, minutes the SD was
# read at).
PUBLISHED_WASH_IN_TIME_COURSE = (
    # Anesth Analg 1991;72:316-24, Figure 2, printed page 320.
    *_time_course(
        "sevoflurane",
        "Anesth Analg 1991;72:316-24",
        7,
        (
            (1.0, 0.563, 0.047, 2.0),
            (2.0, 0.641, 0.047, 2.0),
            (3.0, 0.683, 0.034, 3.0),
            (5.0, 0.733, 0.034, 5.0),
            (7.5, 0.760, 0.031, 7.5),
            (10.0, 0.791, 0.028, 10.0),
            (12.5, 0.801, 0.029, 12.5),
            (15.0, 0.814, 0.025, 15.0),
            (20.0, 0.829, 0.024, 20.0),
            (25.0, 0.839, 0.024, 25.0),
        ),
    ),
    *_time_course(
        "isoflurane",
        "Anesth Analg 1991;72:316-24",
        7,
        (
            (1.0, 0.436, 0.048, 2.0),
            (2.0, 0.495, 0.048, 2.0),
            (3.0, 0.529, 0.040, 3.0),
            (5.0, 0.579, 0.040, 5.0),
            (7.5, 0.616, 0.041, 7.5),
            (10.0, 0.651, 0.038, 10.0),
            (12.5, 0.664, 0.037, 12.5),
            (15.0, 0.682, 0.034, 15.0),
            (20.0, 0.701, 0.035, 20.0),
            (25.0, 0.718, 0.034, 25.0),
        ),
    ),
    # Anesthesiology 1991;74:489-98, Figure 2, printed page 493. This figure
    # plots no point at 1.5 or 2 minutes.
    *_time_course(
        "desflurane",
        "Anesthesiology 1991;74:489-98",
        8,
        (
            (1.0, 0.580, 0.019, 3.0),
            (3.0, 0.731, 0.019, 3.0),
            (5.0, 0.792, 0.019, 5.0),
            (7.5, 0.832, 0.019, 7.5),
            (10.0, 0.840, 0.020, 10.0),
            (12.5, 0.872, 0.020, 12.5),
            (15.0, 0.880, 0.020, 15.0),
            (25.0, 0.900, 0.020, 25.0),
        ),
    ),
    *_time_course(
        "isoflurane",
        "Anesthesiology 1991;74:489-98",
        8,
        (
            (1.0, 0.414, 0.027, 1.0),
            (3.0, 0.520, 0.028, 3.0),
            (5.0, 0.569, 0.032, 5.0),
            (7.5, 0.621, 0.028, 7.5),
            (10.0, 0.641, 0.041, 10.0),
            (12.5, 0.662, 0.028, 12.5),
            (15.0, 0.682, 0.028, 15.0),
            (20.0, 0.708, 0.032, 20.0),
            (25.0, 0.724, 0.027, 25.0),
        ),
    ),
)

# Every sample time some cohort is compared at, in order. One clamped run per
# agent is read at each of them.
EARLY_WASH_IN_SAMPLE_TIMES_MIN = tuple(
    sorted({point.time_min for point in PUBLISHED_WASH_IN_TIME_COURSE})
)

# The points where the model sat outside one SD when the early comparison was
# first run, on 2026-10-18, named by `PublishedTimePoint.label`. The item
# `PL-R0NL` pre-registered that such points get a stated regression band
# rather than the agreement band, and the disagreement is filed as its own
# item. `test_early_wash_in_matches_published_human_measurement` gives the
# distances.
EARLY_WASH_IN_DISAGREEMENTS = frozenset(
    {
        "desflurane/Anesthesiology 1991;74:489-98/1min",
        "desflurane/Anesthesiology 1991;74:489-98/3min",
        "desflurane/Anesthesiology 1991;74:489-98/5min",
        "desflurane/Anesthesiology 1991;74:489-98/7.5min",
        "desflurane/Anesthesiology 1991;74:489-98/10min",
        "isoflurane/Anesthesiology 1991;74:489-98/12.5min",
    }
)

# The top of that regression band. The worst point was +2.10 SD when the
# comparison was first run, and a reading error of 0.006 in a mean is about
# 0.3 SD at desflurane's spread, so 2.5 SD leaves room for the reading and
# catches a change that moves the model further from the measurement.
EARLY_WASH_IN_DISAGREEMENT_CEILING_SD = 2.5

# Every inspired concentration the two protocols used, taken from the cited
# rows above so that the linearity check below covers exactly the range the
# comparisons need it to cover.
PUBLISHED_INSPIRED_PERCENTS = tuple(
    sorted({m.published_inspired_percent for m in PUBLISHED_MEASUREMENTS})
)

# The fresh gas flows at which every wash-in comparison is made. The 30-minute
# comparison runs at `FRESH_GAS_FLOW_L_MIN`, the last of them, and the flow
# sweep runs at all six.
SWEPT_FRESH_GAS_FLOWS_L_MIN = (1.0, 2.0, 4.0, 6.0, 8.0, 10.0)

# The stored parameters a resolving-power case may change, by the record that
# holds each one. Each name is a field of that record, so `getattr` reads the
# shipped value and `dataclasses.replace` builds the changed record.
AGENT_PARAMETER_FIELDS = (
    "blood_gas_partition_coefficient",
    "vessel_rich_tissue_gas_partition_coefficient",
    "muscle_tissue_gas_partition_coefficient",
    "fat_tissue_gas_partition_coefficient",
)
PATIENT_COMPARTMENT_FIELDS = (
    "vessel_rich_volume_l",
    "muscle_volume_l",
    "fat_volume_l",
    "venous_pool_volume_l",
)
ALVEOLAR_GAS_VOLUME_FIELD = "alveolar_gas_volume_l"
CIRCUIT_VOLUME_FIELD = "circuit_volume_l"


@dataclass(frozen=True, slots=True)
class StoredParameterChange:
    """One stored parameter multiplied by a factor before a run starts.

    The resolving-power tests use this to ask whether the published-data
    gate would notice a stored value that is wrong by `factor`. The change
    is applied to the parameter record the value is stored in, and the part
    of the system built from that record is rebuilt from the changed copy
    by the code the shipped system uses. So a changed blood:gas coefficient
    reaches every compartment, and the tissue:blood ratios move inversely,
    exactly as they would if the stored blood:gas value alone were wrong.

    Attributes:
        parameter: the field name, one of `AGENT_PARAMETER_FIELDS`,
            `PATIENT_COMPARTMENT_FIELDS`, `ALVEOLAR_GAS_VOLUME_FIELD` or
            `CIRCUIT_VOLUME_FIELD`.
        factor: what the stored value is multiplied by.
        label: a short name for the test id and the failure message.
    """

    parameter: str
    factor: float
    label: str

    def apply(self, agent_id: str, system: AgentUptakeSystem) -> None:
        """Rebuild the part of an unstepped `system` that this change reaches.

        It must be applied before the first step, while every compartment
        holds no agent and no propagator has been built for the old value.
        Each rebuilt part goes through the constructor or setter that checks
        a shipped value, so a changed value outside what that code accepts
        is refused rather than run.

        Raises:
            ValueError: `parameter` names no field this class knows.
        """

        agent = load_agent_parameters(agent_id)
        patient = load_reference_adult_parameters()

        if self.parameter in AGENT_PARAMETER_FIELDS:
            changed_agent = replace(
                agent, **{self.parameter: getattr(agent, self.parameter) * self.factor}
            )
            system.patient = PatientCompartments.from_parameters(
                agent=changed_agent, patient=patient
            )
        elif self.parameter in PATIENT_COMPARTMENT_FIELDS:
            changed_patient = replace(
                patient, **{self.parameter: getattr(patient, self.parameter) * self.factor}
            )
            system.patient = PatientCompartments.from_parameters(
                agent=agent, patient=changed_patient
            )
        elif self.parameter == ALVEOLAR_GAS_VOLUME_FIELD:
            system.alveoli.gas_volume_l = patient.alveolar_gas_volume_l * self.factor
        elif self.parameter == CIRCUIT_VOLUME_FIELD:
            system.circuit.set_circuit_volume(
                load_reference_circle_system_parameters().circuit_volume_l * self.factor
            )
        else:
            raise ValueError(f"no stored parameter is named {self.parameter!r}")


def _configured_system(
    agent_id: str,
    alveolar_ventilation_l_min: float | None = None,
    cardiac_output_l_min: float | None = None,
    fresh_gas_flow_l_min: float = FRESH_GAS_FLOW_L_MIN,
    delivered_percent: float = DELIVERED_PERCENT,
    vessel_rich_tissue_gas_partition_coefficient: float | None = None,
    change: StoredParameterChange | None = None,
) -> AgentUptakeSystem:
    """Return a fresh system at the published protocol's operating point.

    Nothing has been stepped: this is the setup every run in this module and
    in `test_late_washout_against_published_fits.py` opens from, held in one
    place so that the operating point an elimination runs from is provably
    the one the wash-in comparisons were made at. Three copies of a
    safety-critical setup that must agree is three chances for one of them to
    stop agreeing silently.

    `None` for either patient flow means the reference patient's own default,
    which is what every comparison against a published value uses; the
    sensitivity tests pass explicit values to move off that point.

    `vessel_rich_tissue_gas_partition_coefficient` is the module's only
    parameter override and exists for one test:
    `test_no_measured_tissue_solubility_reaches_desflurane_s_published_elimination`
    asks what the *published human tissue measurements* would produce here,
    which cannot be asked without running a coefficient the data files do not
    hold. It is applied before any step, where the group's stored amount is
    zero and no propagator has been built for the old value, and it goes
    through `dataclasses.replace`, whose constructor checks the new
    coefficient exactly as it checks a shipped one. Every other caller leaves
    it `None` and gets the
    shipped parameter set.

    `change` is the resolving-power tests' override, and `StoredParameterChange`
    documents it. Every comparison against a published value leaves it `None`.
    """

    patient_parameters = load_reference_adult_parameters()
    system = AgentUptakeSystem.for_agent(agent_id)

    if vessel_rich_tissue_gas_partition_coefficient is not None:
        system.patient.vessel_rich = replace(
            system.patient.vessel_rich,
            tissue_gas_partition_coefficient=vessel_rich_tissue_gas_partition_coefficient,
        )

    if change is not None:
        change.apply(agent_id, system)

    system.set_fresh_gas_flow(FreshGasFlow(fresh_gas_flow_l_min))
    system.set_delivered_concentration_percent(Percent(delivered_percent))
    system.set_alveolar_ventilation(
        AlveolarVentilation(
            patient_parameters.default_alveolar_ventilation_l_min
            if alveolar_ventilation_l_min is None
            else alveolar_ventilation_l_min
        )
    )
    system.set_cardiac_output(
        CardiacOutput(
            patient_parameters.default_cardiac_output_l_min
            if cardiac_output_l_min is None
            else cardiac_output_l_min
        )
    )

    return system


@cache
def _wash_in_system(
    agent_id: str,
    alveolar_ventilation_l_min: float | None = None,
    cardiac_output_l_min: float | None = None,
    fresh_gas_flow_l_min: float = FRESH_GAS_FLOW_L_MIN,
    delivered_percent: float = DELIVERED_PERCENT,
    change: StoredParameterChange | None = None,
) -> AgentUptakeSystem:
    """Return the system after 30 minutes of wash-in at one operating point.

    The operating point is `_configured_system()`'s, which documents what
    `None` means for the patient flows and what `change` does.

    F_I is the *circuit* fraction at the moment of measurement, not the
    vaporizer dial. That is the quantity the published studies measured — an
    inspired concentration at the airway — and the two are not equal here:
    alveolar uptake keeps the circuit measurably below the dial for the whole
    run, so dividing by the dial instead would understate every ratio.
    """

    system = _configured_system(
        agent_id,
        alveolar_ventilation_l_min,
        cardiac_output_l_min,
        fresh_gas_flow_l_min,
        delivered_percent,
        change=change,
    )

    for _ in range(round(WASH_IN_DURATION_S / SIMULATION_STEP_S)):
        system.advance(SIMULATION_STEP_S)

    return system


def _wash_in_ratio(
    agent_id: str,
    alveolar_ventilation_l_min: float | None = None,
    cardiac_output_l_min: float | None = None,
    fresh_gas_flow_l_min: float = FRESH_GAS_FLOW_L_MIN,
    delivered_percent: float = DELIVERED_PERCENT,
    change: StoredParameterChange | None = None,
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
        delivered_percent,
        change,
    )

    return (
        system.alveoli.partial_pressure_fraction / system.circuit.inspired_partial_pressure_fraction
    )


def _private_washed_in_system(
    agent_id: str,
    alveolar_ventilation_l_min: float | None,
    cardiac_output_l_min: float | None,
    fresh_gas_flow_l_min: float,
    delivered_percent: float,
    vessel_rich_tissue_gas_partition_coefficient: float | None = None,
    change: StoredParameterChange | None = None,
) -> AgentUptakeSystem:
    """Return an unshared system after the published 30 minutes of wash-in.

    `_wash_in_system()` answers the same question and its instance must not be
    used for an elimination: it is cached and shared with every wash-in
    comparison in this module, so stepping it on would leave each of those
    measuring a washed-out system. Deliberately not cached for the same
    reason - a cached system is a shared mutable one, and both callers here
    step what they are given.

    Both elimination drivers open from this rather than keeping a copy of the
    setup each, and the setup itself is `_configured_system()`'s, which also
    documents the one parameter override
    (`vessel_rich_tissue_gas_partition_coefficient`), the resolving-power
    override (`change`) and what `None` means for the patient flows.
    """

    system = _configured_system(
        agent_id,
        alveolar_ventilation_l_min,
        cardiac_output_l_min,
        fresh_gas_flow_l_min,
        delivered_percent,
        vessel_rich_tissue_gas_partition_coefficient,
        change,
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
    delivered_percent: float = DELIVERED_PERCENT,
    change: StoredParameterChange | None = None,
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

    `change` is the resolving-power override that `_configured_system()`
    documents, and it reaches both limbs of the run.
    """

    system = _private_washed_in_system(
        agent_id,
        alveolar_ventilation_l_min,
        cardiac_output_l_min,
        fresh_gas_flow_l_min,
        delivered_percent,
        change=change,
    )
    alveolar_fraction_at_discontinuation = system.alveoli.partial_pressure_fraction

    system.set_delivered_concentration_percent(Percent(0.0))

    for _ in range(round(ELIMINATION_DURATION_S / SIMULATION_STEP_S)):
        system.advance(SIMULATION_STEP_S)

    return EliminationReading(
        alveolar_fraction_at_discontinuation=alveolar_fraction_at_discontinuation,
        alveolar_fraction=system.alveoli.partial_pressure_fraction,
        inspired_fraction=system.circuit.inspired_partial_pressure_fraction,
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

    system.circuit.set_inspired_partial_pressure_fraction(Fraction(0.0))
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
        peak_inspired_to_starting_alveolar_ratio: the largest ratio this run
            reached of F_I at the end of a step to F_A at the start of the
            same step, which is how far from a true open circuit the driver
            actually got. The denominator is the starting F_A because that is
            the value the bound in
            `test_the_open_circuit_driver_holds_the_inspired_fraction_near_zero`
            is stated against (`PL-RXW0`).
            That test is what reads it.
        agent_accounting: the model's own conservation check at the end of the
            run, carried out rather than asserted here so that a failure can
            name the totals.
    """

    alveolar_fraction_at_discontinuation: float
    alveolar_fraction: float
    peak_inspired_to_starting_alveolar_ratio: float
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
    delivered_percent: float = DELIVERED_PERCENT,
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
    the alveoli and F_I rises from zero to at most `V_A * step / circuit
    volume` of the F_A the step starts from - 1.1e-3 at the shipped step,
    against the 0.30 to 0.32 the same run settles at with rebreathing, and
    first-order in the
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
        delivered_percent,
        vessel_rich_tissue_gas_partition_coefficient,
    )
    alveolar_fraction_at_discontinuation = system.alveoli.partial_pressure_fraction

    system.set_delivered_concentration_percent(Percent(0.0))

    if elimination_fresh_gas_flow_l_min is not None:
        system.set_fresh_gas_flow(FreshGasFlow(elimination_fresh_gas_flow_l_min))

    _discard_circuit_contents(system)
    peak_inspired_to_starting_alveolar_ratio = 0.0

    for _ in range(round(ELIMINATION_DURATION_S / SIMULATION_STEP_S)):
        alveolar_fraction_at_step_start = system.alveoli.partial_pressure_fraction
        system.advance(SIMULATION_STEP_S)
        peak_inspired_to_starting_alveolar_ratio = max(
            peak_inspired_to_starting_alveolar_ratio,
            system.circuit.inspired_partial_pressure_fraction / alveolar_fraction_at_step_start,
        )
        _discard_circuit_contents(system)

    return OpenCircuitEliminationReading(
        alveolar_fraction_at_discontinuation=alveolar_fraction_at_discontinuation,
        alveolar_fraction=system.alveoli.partial_pressure_fraction,
        peak_inspired_to_starting_alveolar_ratio=peak_inspired_to_starting_alveolar_ratio,
        agent_accounting=system.agent_simulation_validation,
    )


@dataclass(frozen=True, slots=True)
class ClampedWashInReading:
    """What one wash-in with the inspired fraction held at the airway gives.

    Attributes:
        ratios: F_A/F_I at each of `EARLY_WASH_IN_SAMPLE_TIMES_MIN`, keyed by
            the time in minutes.
        peak_inspired_deviation: the largest relative distance the circuit's
            F_I reached from the held value at the end of a step, before the
            driver set it back. It is how far from a true clamp the driver
            got, and `test_the_inspired_clamp_holds_the_inspired_fraction`
            reads it.
        agent_accounting: the model's own conservation check at the end of
            the run.
    """

    ratios: dict[float, float]
    peak_inspired_deviation: float
    agent_accounting: AgentSimulationValidationResult


def _hold_inspired_fraction(system: AgentUptakeSystem, inspired_fraction: Fraction) -> None:
    """Set the circuit back to `inspired_fraction`, and record where the agent went.

    This is the whole of what makes the driver below a non-rebreathing
    circuit with the inspired fraction held at the airway. Like
    `_discard_circuit_contents()`, it records the agent it adds as delivered
    and the agent it removes as exhausted. So the model's conservation
    identity `initial + delivered = exhausted + stored` still holds exactly,
    which `test_the_inspired_clamp_neither_creates_nor_loses_agent` asserts.
    """

    before_l = system.circuit.agent_amount_l
    system.circuit.set_inspired_partial_pressure_fraction(inspired_fraction)
    after_l = system.circuit.agent_amount_l
    system.agent_simulation_validator.record_external_agent_transfer(
        delivered_agent_l=max(after_l - before_l, 0.0),
        exhausted_agent_l=max(before_l - after_l, 0.0),
    )


@cache
def _clamped_wash_in(
    agent_id: str, change: StoredParameterChange | None = None
) -> ClampedWashInReading:
    """Wash in with the inspired fraction held at the airway from the first breath.

    **This is a test-only driver, and no setting of the shipped simulator
    reaches the condition it creates.** The shipped circuit starts empty and
    fills at its own time constant, so its F_I lags the dial for the first
    minute or more. Both papers gave the agents as a square wave from a
    non-rebreathing circuit, so their F_I was the cylinder's from the first
    breath (Yasuda et al., Anesth Analg 1991;72:316-24, page 317). Dividing
    the shipped run's F_A by its own lagging F_I would compare a different
    experiment with the published curve.

    The mechanism is `_hold_inspired_fraction()`, applied before the first
    step and after every step. The equations, the propagator, the
    compartments, the step and the patient's operating point are the shipped
    ones, so what this isolates is the breathing system and nothing else.
    The fresh gas flow does not reach the result, because the circuit is set
    back after every step, and the circuit volume reaches it only through the
    size of that within-step drift.

    **It holds F_I to within one step, not exactly.** Within a step the
    patient exhales into the circuit at the alveolar ventilation, so F_I
    drifts toward F_A by at most `V_A * step / circuit volume` of F_I. That
    is 1.1e-3 at the shipped 4 L/min, 0.1 s and 6 L, and
    `test_the_inspired_clamp_holds_the_inspired_fraction` fails if it grows.

    `change` is the resolving-power tests' override, and
    `StoredParameterChange` documents it.
    """

    system = _configured_system(agent_id, change=change)
    inspired_fraction = fraction_from_percent(Percent(DELIVERED_PERCENT))
    sample_steps = {
        round(time_min * SECONDS_PER_MINUTE / SIMULATION_STEP_S): time_min
        for time_min in EARLY_WASH_IN_SAMPLE_TIMES_MIN
    }
    ratios: dict[float, float] = {}
    peak_inspired_deviation = 0.0

    _hold_inspired_fraction(system, inspired_fraction)

    for step in range(1, max(sample_steps) + 1):
        system.advance(SIMULATION_STEP_S)
        peak_inspired_deviation = max(
            peak_inspired_deviation,
            abs(system.circuit.inspired_partial_pressure_fraction - inspired_fraction)
            / inspired_fraction,
        )
        _hold_inspired_fraction(system, inspired_fraction)

        if step in sample_steps:
            ratios[sample_steps[step]] = (
                system.alveoli.partial_pressure_fraction / inspired_fraction
            )

    return ClampedWashInReading(
        ratios=ratios,
        peak_inspired_deviation=peak_inspired_deviation,
        agent_accounting=system.agent_simulation_validation,
    )


def _early_wash_in_failure(
    point: PublishedTimePoint, change: StoredParameterChange | None = None
) -> str | None:
    """Say why the model's F_A/F_I at one published time point is outside its band, or `None`.

    The band is one SD either side of the published mean, as at 30 minutes,
    except at the points in `EARLY_WASH_IN_DISAGREEMENTS`. There the model
    already sat above the band when the comparison was first run, so the
    band is a regression band: no lower than one SD below the mean and no
    higher than `EARLY_WASH_IN_DISAGREEMENT_CEILING_SD` above it.
    """

    ratio = _clamped_wash_in(point.agent_id, change).ratios[point.time_min]
    distance = point.distance_in_standard_deviations(ratio)
    ceiling = (
        EARLY_WASH_IN_DISAGREEMENT_CEILING_SD
        if point.label in EARLY_WASH_IN_DISAGREEMENTS
        else AGREEMENT_TOLERANCE_SD
    )

    if -AGREEMENT_TOLERANCE_SD <= distance <= ceiling:
        return None

    return (
        f"{point.agent_id} with F_I held at the airway washes in to F_A/F_I {ratio:.4f} at "
        f"{point.time_min:g} min, {distance:+.2f} SD from the {point.mean} +/- "
        f"{point.standard_deviation} read from Figure 2 of {point.source} "
        f"(n={point.cohort_size}); the band here is {-AGREEMENT_TOLERANCE_SD:+.1f} to "
        f"{ceiling:+.1f} SD"
    )


def _wash_in_band_failure(
    measurement: PublishedMeasurement,
    fresh_gas_flow_l_min: float,
    change: StoredParameterChange | None = None,
) -> str | None:
    """Say why the 30-minute F_A/F_I is outside one cohort's spread, or `None`.

    This is the wash-in half of the published-data gate, at one fresh gas
    flow. `test_thirty_minute_ratio_matches_published_human_measurement` and
    `test_agreement_survives_every_fresh_gas_flow` assert that it returns
    `None` for the shipped parameter set, and `_published_data_gate_failures()`
    asks it again with a stored parameter changed.
    """

    ratio = _wash_in_ratio(
        measurement.agent_id, fresh_gas_flow_l_min=fresh_gas_flow_l_min, change=change
    )
    distance = measurement.wash_in_distance_in_standard_deviations(ratio)

    if abs(distance) <= AGREEMENT_TOLERANCE_SD:
        return None

    return (
        f"{measurement.agent_id} at {fresh_gas_flow_l_min} L/min fresh gas washes in to "
        f"F_A/F_I {ratio:.4f} at 30 min, {distance:+.2f} SD from the "
        f"{measurement.wash_in_mean} +/- {measurement.wash_in_standard_deviation} measured in "
        f"{measurement.cohort_size} volunteers ({measurement.source})"
    )


def _elimination_direction_failure(
    measurement: PublishedMeasurement, change: StoredParameterChange | None = None
) -> str | None:
    """Say why the model no longer eliminates more slowly than a cohort, or `None`.

    This is the elimination half of the published-data gate. It is the sign
    of the disagreement and not its size, because the size is a regression
    pin of the model's own output (`ELIMINATION_RATIO_PIN_TOLERANCE`), which
    any change at all fails and which is therefore no evidence about any one
    parameter.
    """

    ratio = _eliminate(measurement.agent_id, change=change).ratio

    if ratio > measurement.elimination_mean:
        return None

    return (
        f"{measurement.agent_id} now eliminates to F_A/F_A0 {ratio:.4f}, at or below the "
        f"{measurement.elimination_mean} measured in {measurement.cohort_size} volunteers "
        f"({measurement.source}); the direction this module documents has reversed"
    )


def _ordering_failure(
    ratio_of: Callable[[str], float], expected_order: tuple[str, str, str], what: str
) -> str | None:
    """Say why three agents' ratios are not in a published order, or `None`.

    Both papers were run to show that a less soluble agent approaches its
    inspired fraction faster and leaves faster. `expected_order` lists the
    agents from the highest ratio to the lowest, and `ratio_of` gives each
    agent's ratio.
    """

    ratios = {agent_id: ratio_of(agent_id) for agent_id in expected_order}
    highest, middle, lowest = expected_order

    if ratios[highest] > ratios[middle] > ratios[lowest]:
        return None

    return f"the {what} ratios {ratios} are not in the published order {expected_order}"


# The published wash-in order, highest F_A/F_I at 30 minutes first, and the
# published elimination order, highest F_A/F_A0 at 5 minutes first.
WASH_IN_ORDER = ("desflurane", "sevoflurane", "isoflurane")
ELIMINATION_ORDER = ("isoflurane", "sevoflurane", "desflurane")


def _wash_in_ordering_failure(
    changed_agent_id: str | None = None, change: StoredParameterChange | None = None
) -> str | None:
    """Check the wash-in order, with `change` applied to `changed_agent_id` alone."""

    return _ordering_failure(
        lambda agent_id: _wash_in_ratio(
            agent_id, change=change if agent_id == changed_agent_id else None
        ),
        WASH_IN_ORDER,
        "30-minute wash-in",
    )


def _elimination_ordering_failure(
    changed_agent_id: str | None = None, change: StoredParameterChange | None = None
) -> str | None:
    """Check the elimination order, with `change` applied to `changed_agent_id` alone."""

    return _ordering_failure(
        lambda agent_id: (
            _eliminate(agent_id, change=change if agent_id == changed_agent_id else None).ratio
        ),
        ELIMINATION_ORDER,
        "5-minute elimination",
    )


def _published_data_gate_failures(
    agent_id: str, change: StoredParameterChange | None = None
) -> Iterator[str]:
    """Yield each published-data assertion that one agent's run fails.

    "The published-data gate" is the set of assertions in this module whose
    expected value is a published human measurement rather than this model's
    own output. They are the band at each point of the agent's published
    early wash-in curves, the 30-minute wash-in band for each of the agent's
    cohorts at every swept fresh gas flow, the sign of the elimination
    disagreement for each cohort, and both solubility orderings. The early
    points come first because one clamped run answers all of them. The regression pins and the
    diagnostics are left out, because a pin fails on any change and so says
    nothing about whether a published value could detect one. The gate passes
    when nothing is yielded. It is a generator so that a caller that needs
    only the first failure stops the runs there.
    """

    measurements = [m for m in PUBLISHED_MEASUREMENTS if m.agent_id == agent_id]
    checks: list[Callable[[], str | None]] = [
        *(
            partial(_early_wash_in_failure, point, change)
            for point in PUBLISHED_WASH_IN_TIME_COURSE
            if point.agent_id == agent_id
        ),
        *(
            partial(_wash_in_band_failure, measurement, fresh_gas_flow_l_min, change)
            for measurement in measurements
            for fresh_gas_flow_l_min in SWEPT_FRESH_GAS_FLOWS_L_MIN
        ),
        *(
            partial(_elimination_direction_failure, measurement, change)
            for measurement in measurements
        ),
        partial(_wash_in_ordering_failure, agent_id, change),
        partial(_elimination_ordering_failure, agent_id, change),
    ]

    for check in checks:
        if (failure := check()) is not None:
            yield failure


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

    failure = _wash_in_band_failure(measurement, FRESH_GAS_FLOW_L_MIN)

    assert failure is None, failure


@pytest.mark.parametrize(
    "point",
    PUBLISHED_WASH_IN_TIME_COURSE,
    ids=[point.label for point in PUBLISHED_WASH_IN_TIME_COURSE],
)
def test_early_wash_in_matches_published_human_measurement(point: PublishedTimePoint) -> None:
    """The model's F_A/F_I must follow the published curve from 1 to 25 minutes.

    The run is `_clamped_wash_in()`, which holds F_I at the airway as both
    papers' non-rebreathing circuits did. The expected values were read from
    Figure 2 of each paper (`PublishedTimePoint` says how), and none of them
    came from this model.

    Measured 2026-10-18 at the shipped defaults, as distance from each
    point's mean in that point's SD:

    | Cohort | 1 to 3 min | 5 min | 7.5 to 25 min |
    | --- | --- | --- | --- |
    | Sevoflurane, n=7 | -0.54 to -0.69 SD | -0.22 SD | +0.48 to +0.77 SD |
    | Isoflurane, n=7 | -0.70 to -0.83 SD | -0.19 SD | +0.34 to +0.76 SD |
    | Isoflurane, n=8 | -0.60 to -0.67 SD | +0.08 SD | +0.32 to +1.06 SD |
    | Desflurane, n=8 | +1.79 to +1.82 SD | +1.82 SD | +2.10 SD at 10 min, then +0.94 to +0.28 SD |

    So sevoflurane and isoflurane follow the published curves within one SD,
    a little slow in the first 3 minutes and a little fast after 7.5. The
    one isoflurane point past one SD, +1.06 SD at 12.5 minutes, is within
    the figure's reading error of the band.

    **Desflurane rises faster than its cohort from 1 to 10 minutes**, by
    0.034 to 0.042 in F_A/F_I, and agrees from 12.5 minutes on. The
    operating point is an unlikely cause. The isoflurane breathed by the same eight volunteers
    in the same sitting follows its curve, and sevoflurane and isoflurane
    both sit slightly *below* their curves early, where a ventilation or
    lung volume error would move every agent the same way. So the candidate
    is something only desflurane has, such as its blood:gas or vessel-rich
    tissue:gas coefficient. `PL-RFLN`'s elimination residual is the same
    agent. Those points are held to a regression band, as
    `EARLY_WASH_IN_DISAGREEMENTS` says, so the disagreement cannot grow
    unseen.

    **What this comparison can detect.** It is part of the published-data
    gate, and `docs/MODEL.md` § "What the published-data gate can and cannot
    resolve" gives the factor at which each stored parameter leaves it. A
    doubled alveolar gas volume moves sevoflurane's 1-minute F_A/F_I from
    0.537 to 0.429, -2.85 SD, so the early points catch the error the
    30-minute comparison at 10 L/min could not.
    """

    failure = _early_wash_in_failure(point)

    assert failure is None, failure


def test_every_named_early_disagreement_is_a_published_point() -> None:
    """A label in `EARLY_WASH_IN_DISAGREEMENTS` must name a point that exists.

    A label that matched no point would name a regression band that applies
    to nothing, and the reader of the set would believe a disagreement is
    being held that is not.
    """

    labels = {point.label for point in PUBLISHED_WASH_IN_TIME_COURSE}

    assert EARLY_WASH_IN_DISAGREEMENTS <= labels, (
        f"{sorted(EARLY_WASH_IN_DISAGREEMENTS - labels)} name no point in "
        f"PUBLISHED_WASH_IN_TIME_COURSE"
    )


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_the_inspired_clamp_holds_the_inspired_fraction(agent_id: str) -> None:
    """Show that the clamped wash-in is the condition it claims to be.

    Each step starts with the circuit at the held F_I. Within the step the
    patient exhales alveolar gas into the circuit at the alveolar
    ventilation, so F_I moves toward F_A by at most `V_A * step / V_circuit`
    of the distance between them, which is at most F_I itself. The fresh gas
    carries the same fraction, so it moves F_I nowhere. The bound is
    computed here from the parameter files the run uses. Measured
    2026-10-18, the peak is 1.1075e-3 against a bound of 1.1111e-3 for each
    agent.
    """

    patient_parameters = load_reference_adult_parameters()
    circuit_volume_l = AgentUptakeSystem.for_agent(agent_id).circuit.circuit_volume_l
    bound = (
        patient_parameters.default_alveolar_ventilation_l_min
        / SECONDS_PER_MINUTE
        * SIMULATION_STEP_S
        / circuit_volume_l
    )

    peak = _clamped_wash_in(agent_id).peak_inspired_deviation

    assert peak <= bound, (
        f"{agent_id}'s F_I moves {peak:.6e} of its held value inside a step of the "
        f"clamped wash-in, above the {bound:.6e} that {SIMULATION_STEP_S} s of exhalation "
        f"at {patient_parameters.default_alveolar_ventilation_l_min} L/min into "
        f"{circuit_volume_l} L can produce; the driver no longer holds F_I at the airway"
    )


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_the_inspired_clamp_neither_creates_nor_loses_agent(agent_id: str) -> None:
    """The clamp must record the agent it adds and removes, not create or delete it.

    `_hold_inspired_fraction()` writes the circuit directly, outside
    `advance()`'s own accounting. Agent added and not recorded would read as
    agent the model created. So the model's own conservation check is read
    at the end of the run. Measured 2026-10-18, its relative error is 3e-13
    for each agent, which is rounding.
    """

    accounting = _clamped_wash_in(agent_id).agent_accounting

    assert accounting.passes_validation, (
        f"the clamped wash-in leaves {accounting.unaccounted_agent_l:.3e} L of {agent_id} "
        f"unaccounted for: {accounting.initial_agent_l:.4f} L initial plus "
        f"{accounting.delivered_agent_l:.4f} L delivered against "
        f"{accounting.exhausted_agent_l:.4f} L exhausted and "
        f"{accounting.currently_stored_agent_l:.4f} L stored, a relative error of "
        f"{accounting.relative_error:.2e}"
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
        system.alveoli.partial_pressure_fraction, system.circuit.inspired_partial_pressure_fraction
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

    failure = _wash_in_ordering_failure()

    assert failure is None, failure


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
        _wash_in_ratio(agent_id, delivered_percent=percent)
        for percent in PUBLISHED_INSPIRED_PERCENTS
    ]

    for ratio in ratios:
        assert ratio == pytest.approx(ratios[0], rel=1e-9)


@pytest.mark.parametrize(
    "measurement", PUBLISHED_MEASUREMENTS, ids=[m.label for m in PUBLISHED_MEASUREMENTS]
)
@pytest.mark.parametrize("fresh_gas_flow_l_min", SWEPT_FRESH_GAS_FLOWS_L_MIN)
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

    failure = _wash_in_band_failure(measurement, fresh_gas_flow_l_min)

    assert failure is None, failure


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


@dataclass(frozen=True, slots=True)
class ResolvingPowerCase:
    """One agent run with one stored parameter changed, and what the gate should say.

    The factors were chosen with margin from the edges measured on
    2026-10-18, which `docs/MODEL.md` § "What the published-data gate can and
    cannot resolve" tabulates. A case sits well past an edge or well inside
    one, so an unrelated change of a few hundredths of an SD does not flip
    it. A test placed at an edge itself would sit 0.01 to 0.03 SD from
    flipping (`PL-9YHR`).
    """

    agent_id: str
    change: StoredParameterChange

    @property
    def label(self) -> str:
        return f"{self.agent_id}-{self.change.label}"


def _cases(
    parameter: str, factor: float, label: str, agent_ids: tuple[str, ...] = AGENT_IDS
) -> tuple[ResolvingPowerCase, ...]:
    """Build one case per agent for one stored parameter and factor."""

    change = StoredParameterChange(parameter=parameter, factor=factor, label=label)

    return tuple(ResolvingPowerCase(agent_id=agent_id, change=change) for agent_id in agent_ids)


# Changes the gate detects for every agent, measured 2026-10-18 with the early
# wash-in points in the gate (`PL-R0NL`). The early points set most of these
# edges. Blood:gas leaves the gate at x0.95 to x0.99 below and x1.05 to x1.10
# above, so x1.10 is not used: desflurane passes it, at an edge of x1.097. The
# vessel-rich tissue:gas coefficient leaves it at x0.85 to x0.97 below and
# x1.11 to x1.55 above. The alveolar gas volume leaves it at x1.19 to x1.33
# above, through the 1-minute point.
DETECTED_CHANGES = (
    *_cases("blood_gas_partition_coefficient", 0.90, "blood-gas-x0.90"),
    *_cases("blood_gas_partition_coefficient", 1.15, "blood-gas-x1.15"),
    *_cases("vessel_rich_tissue_gas_partition_coefficient", 0.80, "vessel-rich-tissue-gas-x0.80"),
    *_cases("vessel_rich_tissue_gas_partition_coefficient", 1.75, "vessel-rich-tissue-gas-x1.75"),
    *_cases(ALVEOLAR_GAS_VOLUME_FIELD, 1.50, "alveolar-gas-volume-x1.50"),
)

# Changes the gate cannot detect. Each one is a stored value wrong by the
# stated factor that passes every published-data assertion, so a green gate
# says nothing about whether that value is right. A row that names agents
# leaves out the others because their edge lies inside the factor. Isoflurane
# and desflurane fail with the alveolar gas volume halved, below x0.61 and
# x0.92. Sevoflurane and isoflurane fail with the venous pool doubled, above
# x1.86 and x1.60, and isoflurane's lower venous pool edge is x0.50 itself.
# Fat volume runs for one agent only. A tissue's capacity is its volume times
# its tissue:gas coefficient, so doubling either moves a run identically, and
# the edge searches of 2026-10-17 and 2026-10-18 found the same edges for
# both, for every agent.
UNDETECTED_CHANGES = (
    *_cases("fat_tissue_gas_partition_coefficient", 0.50, "fat-tissue-gas-x0.50"),
    *_cases("fat_tissue_gas_partition_coefficient", 2.00, "fat-tissue-gas-x2.00"),
    *_cases("fat_volume_l", 2.00, "fat-volume-x2.00", ("sevoflurane",)),
    *_cases("muscle_tissue_gas_partition_coefficient", 1.50, "muscle-tissue-gas-x1.50"),
    *_cases(ALVEOLAR_GAS_VOLUME_FIELD, 0.50, "alveolar-gas-volume-x0.50", ("sevoflurane",)),
    *_cases("venous_pool_volume_l", 0.50, "venous-pool-x0.50", ("sevoflurane", "desflurane")),
    *_cases("venous_pool_volume_l", 2.00, "venous-pool-x2.00", ("desflurane",)),
    *_cases(CIRCUIT_VOLUME_FIELD, 0.50, "circuit-volume-x0.50"),
)


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_the_published_data_gate_passes_the_shipped_parameter_set(agent_id: str) -> None:
    """The gate the resolving-power tests ask about must pass unchanged.

    `_published_data_gate_failures()` restates no criterion of its own: it
    calls the same checks the published-data tests above assert. This test
    asserts that it returns nothing for the shipped parameter set, so a
    detection below is a response to the change and not a gate that fails
    on everything.
    """

    failures = list(_published_data_gate_failures(agent_id))

    assert not failures, failures


@pytest.mark.parametrize("case", DETECTED_CHANGES, ids=[case.label for case in DETECTED_CHANGES])
def test_the_published_data_gate_fails_at_a_stated_perturbation(case: ResolvingPowerCase) -> None:
    """The gate must detect a stored value wrong by the stated factor.

    This turns the resolving-power table in `docs/MODEL.md` into an
    assertion. A parameter or solver change that made the gate blind along
    blood:gas, vessel-rich tissue:gas or the alveolar gas volume would
    otherwise leave that table claiming a resolving power the gate no longer has.
    """

    first_failure = next(_published_data_gate_failures(case.agent_id, case.change), None)

    assert first_failure is not None, (
        f"{case.agent_id} with {case.change.parameter} x{case.change.factor} passes every "
        f"published-data assertion; the gate no longer resolves this change, so the "
        f"resolving-power table in docs/MODEL.md must be re-measured"
    )


@pytest.mark.parametrize(
    "case", UNDETECTED_CHANGES, ids=[case.label for case in UNDETECTED_CHANGES]
)
def test_the_published_data_gate_passes_at_a_stated_perturbation(case: ResolvingPowerCase) -> None:
    """The gate must still be unable to detect these changes, as the docs say.

    `docs/MODEL.md` tells a reader that a green gate says nothing about these
    stored values. This test holds that statement true. If a model change
    made the gate sensitive to one of them, the statement would understate
    what the gate shows, and this test fails so that the table is
    re-measured rather than left stale. A failure here is not a defect in the
    model. It is a measurement to redo.
    """

    failures = list(_published_data_gate_failures(case.agent_id, case.change))

    assert not failures, (
        f"{case.agent_id} with {case.change.parameter} x{case.change.factor} now fails the "
        f"published-data gate: {failures}; docs/MODEL.md says the gate cannot resolve this "
        f"change, so its resolving-power table must be re-measured"
    )


@pytest.mark.parametrize(
    "measurement", PUBLISHED_MEASUREMENTS, ids=[m.label for m in PUBLISHED_MEASUREMENTS]
)
def test_five_minute_elimination_ratio_regression_pin(measurement: PublishedMeasurement) -> None:
    """Compare the modelled 5-minute elimination against all four cohorts.

    **This comparison does not agree, and the assertion below is a regression
    pin rather than an agreement claim.** Measured 2026-09-06 at the shipped
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
    `test_five_minute_elimination_ratio_without_rebreathing_regression_pin`
    is that comparison, and the condition it runs in is a diagnostic no
    setting of this simulator reaches.

    What is asserted here is therefore that the model still produces the
    ratios in `MODELLED_ELIMINATION_RATIOS`, to within
    `ELIMINATION_RATIO_PIN_TOLERANCE`. The name says regression pin, because
    the expected values are this model's own outputs and not the published
    means. That is worth asserting for the reason the wash-in comparison
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

    assert abs(ratio - modelled) <= ELIMINATION_RATIO_PIN_TOLERANCE, (
        f"{measurement.agent_id} eliminates to F_A/F_A0 {ratio:.5f} at 5 min against the "
        f"{modelled} this module measured on 2026-09-06, a drift of {drift_sd:.2f} published "
        f"SD; it now sits {published_distance:+.2f} SD from the {measurement.elimination_mean} "
        f"+/- {measurement.elimination_standard_deviation} measured in "
        f"{measurement.cohort_size} volunteers ({measurement.source}). Re-measure this "
        f"module's tables and docs/MODEL.md's rather than widening the pin"
    )


@pytest.mark.parametrize(
    "measurement", PUBLISHED_MEASUREMENTS, ids=[m.label for m in PUBLISHED_MEASUREMENTS]
)
def test_the_model_eliminates_more_slowly_than_every_published_cohort(
    measurement: PublishedMeasurement,
) -> None:
    """State the direction of the disagreement, so it cannot drift unnoticed.

    The regression pin above holds the magnitude and would fail on a move in
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

    failure = _elimination_direction_failure(measurement)

    assert failure is None, failure


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

    failure = _elimination_ordering_failure()

    assert failure is None, failure


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
        _eliminate(agent_id, delivered_percent=percent).ratio
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
def test_five_minute_elimination_ratio_without_rebreathing_regression_pin(
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

    **What is asserted here is a regression pin, not the agreement above.**
    Three rows landing inside the published spread is a result to state, not a
    tolerance to assert: pinning it as one would make a later model change
    that improved desflurane and moved sevoflurane to 1.1 SD look like a
    failure, and would let the same change go unnoticed if it moved
    sevoflurane from -0.15 to +0.95. So the assertion is that the driver still
    produces `OPEN_CIRCUIT_ELIMINATION_RATIOS` to within
    `ELIMINATION_RATIO_PIN_TOLERANCE`, in either direction, exactly as the
    shipped-condition comparison asserts its own measured ratios. The
    distances above are re-derived and named in the failure message, so a
    run that moves says how far it moved and against what.
    """

    ratio = _eliminate_without_rebreathing(measurement.agent_id).ratio
    modelled = OPEN_CIRCUIT_ELIMINATION_RATIOS[measurement.agent_id]
    drift_sd = abs(ratio - modelled) / measurement.elimination_standard_deviation
    published_distance = measurement.elimination_distance_in_standard_deviations(ratio)

    assert abs(ratio - modelled) <= ELIMINATION_RATIO_PIN_TOLERANCE, (
        f"{measurement.agent_id} eliminates into an open circuit to F_A/F_A0 {ratio:.5f} at "
        f"5 min against the {modelled} this module measured on 2026-09-07, a drift of "
        f"{drift_sd:.2f} published SD; it now sits {published_distance:+.2f} SD from the "
        f"{measurement.elimination_mean} +/- {measurement.elimination_standard_deviation} "
        f"measured in {measurement.cohort_size} volunteers ({measurement.source}). This is "
        f"the diagnostic condition, which no setting of the shipped simulator reaches; "
        f"re-measure this module's tables and docs/MODEL.md's rather than widening the pin"
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
    of it is already held by the regression pins on both conditions.

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


@pytest.mark.parametrize(
    "case",
    APPARATUS_DEAD_SPACE_CASES,
    ids=[f"{c.respiratory_rate_per_min:g}bpm" for c in APPARATUS_DEAD_SPACE_CASES],
)
def test_no_apparatus_dead_space_reaches_desflurane_s_published_elimination(
    case: ApparatusDeadSpaceCase,
) -> None:
    """Desflurane's residual is not the published apparatus's dead space either.

    `docs/MODEL.md` SS "Desflurane's residual" rejected rebreathing in the
    published apparatus at an *assumed* F_I/F_A of 0.30. The methods section
    later supplied the apparatus's real volume - about 50 ml of corrugated
    Teflon between the tracheal sampling port and the nonrebreathing valve -
    and this test is what that sourced figure bought (`PL-RFLN`).

    **The framing had to change before the number could be used.** That 50 ml
    is a series dead space, and the derivation beside `APPARATUS_DEAD_SPACE_L`
    shows a series dead space is exactly an alveolar-ventilation decrement of
    V_D * f in this model, not a non-zero inspired fraction. So the run below
    is the open-circuit diagnostic at a reduced ventilation, applied to both
    limbs because the apparatus was present throughout the published protocol.

    Measured 2026-09-13, in each cohort's own published SD, against the
    -2.33 SD desflurane sits at with no dead space at all:

    | f (/min) | V_A | Desflurane | Isoflurane n=8 | Worst wash-in |
    | --- | --- | --- | --- | --- |
    | 6 | 3.70 | -1.89 SD | +1.59 SD | -0.42 SD |
    | 8 | 3.60 | -1.73 SD | +1.82 SD | -0.63 SD |
    | 10 | 3.50 | -1.56 SD | +2.05 SD | -0.85 SD |
    | 12 | 3.40 | -1.38 SD | +2.30 SD | -1.08 SD |

    So the dead space moves desflurane the right way and carries between 0.44
    and 0.95 SD of the 2.33 - a quarter to two fifths of it, never the whole -
    while pushing the isoflurane cohort that was inside its spread at +0.94 SD
    out to between +1.59 and +2.30. It fails the way every other candidate in
    that section fails: it is **common-mode**, moving all four cohorts
    together, and desflurane's residual is differential. The companion test
    below is what asserts that second half.

    This runs the diagnostic open circuit, so the caveat every other use of it
    carries applies here too: no setting of the shipped simulator reaches the
    condition, and nothing here is a statement about what a user sees.
    """

    measurement = next(m for m in PUBLISHED_MEASUREMENTS if m.agent_id == "desflurane")
    ratio = _eliminate_without_rebreathing(
        "desflurane", alveolar_ventilation_l_min=case.alveolar_ventilation_l_min
    ).ratio
    shortfall_sd = -measurement.elimination_distance_in_standard_deviations(ratio)

    assert shortfall_sd > case.minimum_shortfall_sd, (
        f"desflurane eliminating into an open circuit at an alveolar ventilation of "
        f"{case.alveolar_ventilation_l_min:.3f} L/min - the reference default less the "
        f"{APPARATUS_DEAD_SPACE_L * 1000:.0f} ml of apparatus dead space Yasuda 1991 "
        f"Anesthesiology reports, re-inspired at {case.respiratory_rate_per_min:g} breaths "
        f"per minute - reaches F_A/F_A0 {ratio:.4f} at 5 min, only {shortfall_sd:.2f} "
        f"published SD below the {measurement.elimination_mean} +/- "
        f"{measurement.elimination_standard_deviation} measured in "
        f"{measurement.cohort_size} volunteers ({measurement.source}). This module and "
        f"docs/MODEL.md say the published apparatus's dead space carries part of the "
        f"residual and not the whole of it, and that is what has changed - re-open the "
        f"question rather than treating the residual as explained"
    )


def test_the_apparatus_dead_space_moves_every_cohort_together() -> None:
    """Why the published apparatus's dead space cannot be desflurane's residual.

    The test above shows the sourced dead space never closes desflurane's gap.
    This one shows the stronger thing: the gap could not be closed *by this
    mechanism* even if the dead space were larger, because buying desflurane's
    movement costs the two isoflurane cohorts their agreement.

    The run is at the largest decrement the wash-in comparison will bear -
    50 ml at 11 breaths per minute, where sevoflurane's wash-in sits at
    -0.96 SD and one breath per minute more takes it outside its published
    spread. That ceiling is not imposed here; it is the wash-in comparison's
    own, and it is why `PL-73G7` required any candidate for the elimination
    gap to be checked against the wash-in rows in the same pass.

    Measured 2026-09-13 at f = 11, V_A = 3.45 L/min:

    | Cohort | Wash-in | Elimination | Elimination with no dead space |
    | --- | --- | --- | --- |
    | Sevoflurane n=7 | -0.96 SD | +0.95 SD | -0.15 SD |
    | Isoflurane n=7 | -0.82 SD | +1.69 SD | +0.66 SD |
    | Desflurane n=8 | -0.55 SD | -1.48 SD | -2.33 SD |
    | Isoflurane n=8 | -0.64 SD | +2.17 SD | +0.94 SD |

    Desflurane is still 1.48 SD short while both isoflurane cohorts have left
    their published spread entirely. That is the same failure the alveolar
    ventilation row of `docs/MODEL.md`'s candidate table records, which is not
    a coincidence: a series dead space *is* a ventilation decrement here, so
    the apparatus's own volume is that candidate at a sourced magnitude rather
    than a fitted one.

    **One thing this test cannot decide, and it is why the item closed without
    naming a cause.** Whether any decrement is owed at all is undetermined.
    Yasuda derived the alveolar fraction of ventilation from
    F_M = f_A * F_A + f_D * F_I, and the mixing chamber that supplies F_M sits
    beyond the nonrebreathing valve, so the 50 ml that gets re-inspired never
    reaches it: their derived f_A is (V_T - V_D_anat - V_D_app)/V_T and
    already nets the apparatus out. A comparison run at *their* alveolar
    ventilation must therefore not subtract it again. This model runs at 4.0
    L/min, which the parameter file records as a convention with no primary
    source behind it and which is neither quantity. `PL-ZDWL` carries reading
    the value out of the methods text.

    This runs the diagnostic open circuit, so the caveat every other use of it
    carries applies here too: no setting of the shipped simulator reaches the
    condition, and nothing here is a statement about what a user sees.
    """

    case = LARGEST_ADMISSIBLE_DEAD_SPACE_CASE
    alveolar_ventilation = case.alveolar_ventilation_l_min

    for measurement in PUBLISHED_MEASUREMENTS:
        wash_in = _wash_in_ratio(
            measurement.agent_id, alveolar_ventilation_l_min=alveolar_ventilation
        )
        wash_in_sd = measurement.wash_in_distance_in_standard_deviations(wash_in)
        assert abs(wash_in_sd) < AGREEMENT_TOLERANCE_SD, (
            f"{measurement.label} washes in to F_A/F_I {wash_in:.4f} ({wash_in_sd:+.2f} SD) at "
            f"an alveolar ventilation of {alveolar_ventilation:.3f} L/min, outside its published "
            f"spread. This case is meant to be the *largest* dead space the wash-in comparison "
            f"still admits, so either the model or that ceiling has moved and the ceiling has to "
            f"be re-measured before the conclusion below is restated"
        )

    desflurane = next(m for m in PUBLISHED_MEASUREMENTS if m.agent_id == "desflurane")
    desflurane_shortfall_sd = -desflurane.elimination_distance_in_standard_deviations(
        _eliminate_without_rebreathing(
            "desflurane", alveolar_ventilation_l_min=alveolar_ventilation
        ).ratio
    )
    assert desflurane_shortfall_sd > case.minimum_shortfall_sd, (
        f"desflurane is only {desflurane_shortfall_sd:.2f} published SD short at the largest "
        f"apparatus dead space the wash-in comparison admits, so the published apparatus may "
        f"now account for the residual docs/MODEL.md says it cannot - re-open the question"
    )

    for measurement in PUBLISHED_MEASUREMENTS:
        if measurement.agent_id != "isoflurane":
            continue
        ratio = _eliminate_without_rebreathing(
            measurement.agent_id, alveolar_ventilation_l_min=alveolar_ventilation
        ).ratio
        excess_sd = measurement.elimination_distance_in_standard_deviations(ratio)
        assert excess_sd > AGREEMENT_TOLERANCE_SD, (
            f"{measurement.label} eliminates to F_A/F_A0 {ratio:.4f} ({excess_sd:+.2f} SD) at the "
            f"dead space that leaves desflurane {desflurane_shortfall_sd:.2f} SD short, which is "
            f"inside its published spread. The common-mode argument docs/MODEL.md rests on - that "
            f"this mechanism cannot move desflurane without costing isoflurane - is what has "
            f"changed, and the section has to be rewritten rather than this threshold lowered"
        )


@pytest.mark.parametrize("elimination_fresh_gas_flow_l_min", [None, 0.0])
@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_the_open_circuit_driver_holds_the_inspired_fraction_near_zero(
    agent_id: str, elimination_fresh_gas_flow_l_min: float | None
) -> None:
    """Show that the diagnostic is the condition it claims to be.

    A driver that only partly removed the rebreathing would produce numbers
    between the two conditions and label them as one of them, which is the
    failure mode a diagnostic has and an ordinary test does not: nothing else
    in this module would notice, because the ratio it produces is plausible
    either way.

    The residual has an upper bound. Settings are held constant across a
    step, and each step starts with the circuit emptied. Within the step the
    circuit fills from the alveoli at the alveolar ventilation, so
    dF_I/dt <= (V_A / V_circuit) F_A(t). F_A does not rise during a washout,
    so F_I at the end of the step is at most `V_A * step / V_circuit` of F_A
    at the *start* of the step. That is 1.11e-3 at the shipped 4 L/min, 0.1 s
    and 6 L. The bound is computed here from the same parameter files the run
    uses rather than written down, so a change to any of the three moves the
    assertion with it.

    Until `PL-RXW0` the test divided by F_A at the end of the step, after F_A
    had already fallen, and that ratio is not bounded by the same figure. It
    passed at the 10 L/min the run keeps by 1.5e-4 to 4.8e-4 relative, and a
    correct driver exceeded it at lower elimination flows: by a factor of
    1.000911 to 1.001237 at 0 L/min (measured 2026-10-17). So the test also
    runs at 0 L/min, the flow closest to the bound. Measured 2026-10-17 with
    the starting F_A, the peak is 0.99785 to 0.99790 of the bound at the
    run's own flow and 0.99924 to 0.99931 at 0 L/min. The driver is about 280
    times closer to an open circuit than the shipped condition is, which
    settles at 0.30 to 0.32, and the residual is first-order in the step, so
    a shorter step gets proportionally closer.
    """

    patient_parameters = load_reference_adult_parameters()
    circuit_volume_l = AgentUptakeSystem.for_agent(agent_id).circuit.circuit_volume_l
    bound = (
        patient_parameters.default_alveolar_ventilation_l_min
        / SECONDS_PER_MINUTE
        * SIMULATION_STEP_S
        / circuit_volume_l
    )

    peak = _eliminate_without_rebreathing(
        agent_id, elimination_fresh_gas_flow_l_min=elimination_fresh_gas_flow_l_min
    ).peak_inspired_to_starting_alveolar_ratio

    assert peak <= bound, (
        f"{agent_id} reaches an F_I of {peak:.6e} of the step's starting F_A inside a "
        f"step of the open-circuit diagnostic, above the {bound:.6e} that "
        f"{SIMULATION_STEP_S} s of refilling at "
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
