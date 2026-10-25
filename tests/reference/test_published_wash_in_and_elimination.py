"""Compare the shipped model with published human wash-in and elimination measurements.

Both directions come from the same volunteers: 30 minutes of wash-in, then the
five minutes of elimination that followed it.

Every other module in `tests/reference/` checks the implementation against
itself. Those modules use an analytic exponential, an RK4 oracle built from
this project's own equations, mass balance, equilibrium, the zero-flow limits
and directional ordering. All of that is **verification**, which shows that the
implementation solves the intended equations correctly. None of it is
**validation**, which shows that the equations describe the real phenomenon. A
model can be numerically flawless and physiologically wrong. A suite made only
of verification tests would report such a model as though it had passed
validation too.

This module is the validation half. It is the only test here whose expected
values come from outside the repository. Yasuda et al. measured both
directions in two volunteer studies, and this module uses all eight of their
figures:

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

All eight figures are mean +/- SD. They were read from the two abstracts and
checked against PubMed on 2026-09-06. F_A0 follows each paper's own
definition: it is the last alveolar fraction recorded during the 30-minute
administration. So the elimination ratio is anchored to the end of the wash-in
that the same subjects had just completed, and the two comparisons here form
one continuous protocol rather than two.

Isoflurane appears twice, in two independent cohorts, because both studies
included it. Both cohorts are compared in both directions. This is not
redundancy. If the model matched
isoflurane in one cohort and missed it in the other, that would reveal
something about the measurement's own spread that a single comparison hides.

**Why both directions.** The two directions constrain nearly disjoint parts of
the parameter set. This is measured further down rather than assumed. The
30-minute wash-in ratio responds to blood:gas and barely to the vessel-rich
group, and the 5-minute elimination ratio does the reverse. No other gate in
this repository tests the return of agent *out of* tissue at all. A model can
reproduce uptake and still misstate recovery, which is the classic signature
of an under-parameterized tissue compartment. Recovery is also the half that a
teaching simulator is most often used to demonstrate.

**The two directions give different verdicts, and the difference is the most
useful thing in this module.** The wash-in comparison agrees, inside the
published spread, for every agent and cohort. The elimination comparison does
not. At the shipped defaults the model retains more alveolar agent at five
minutes than every cohort did, by +1.0 to +5.0 published SD. So the
elimination assertions are a *regression* pin on the model's own measured
ratios, plus the claims that are true: the published ordering, the direction
of the disagreement, and independence from the delivered fraction.
`test_five_minute_elimination_ratio_regression_pin` gives the measured table.

**Why the elimination comparison misses, measured rather than guessed.** The
miss comes largely from the breathing apparatus. The mechanism is a difference
between the two ratios, not anything about tissue. F_A/F_I has the inspired
fraction in its denominator, so whatever a breathing system does to F_I
divides out of the ratio. That is why
`test_agreement_survives_every_fresh_gas_flow` finds the wash-in comparison
inside the published spread at every flow from 1 to 10 L/min. F_A/F_A0 has no
such term. It divides the alveolar fraction by its own value five minutes
earlier. So agent that returns to the alveoli *from the circuit* is counted
exactly as though it had come back out of the patient.

This model always rebreathes. `docs/MODEL.md` § "Model boundary" gives it one
ideal circuit. That circuit is a closed recirculating path except for
fresh-gas inflow and exhaust, and inspired gas *is* circuit gas. So during an
elimination the inspired fraction settles near V_A/(V_A + fresh gas flow)
times the alveolar fraction. At the highest supported flow that factor is
4/(4+10), or 0.29. It was measured at 0.30 to 0.32 for the three agents at
five minutes.

The published protocols did not rebreathe. Neither abstract states the
breathing system directly, so this is an inference, and it is flagged as one.
It is a narrow inference, though. Both papers report mixed expired
concentrations, and both report the volume of agent recovered during
elimination against the volume taken up. Neither quantity can be measured
without collecting the whole expirate instead of returning it to the subject.
So their elimination ran at an inspired fraction at or near zero, and this
model cannot be set to that fraction at any supported flow. Confirming the
inference against the papers' own methods sections needs the full texts. They
are not in PubMed Central and are not held in `docs/references/`.

The table below was measured on 2026-09-06 and re-measured on 2026-09-07, in
each cohort's own standard deviations. Both model columns use the shipped
parameter set. `PL-8ZJQ` raised that set's `venous_pool_volume_l` from 1.0 L to
Davis and Mapleson's 1.222 L. A larger venous pool returns more agent to the
lungs, so the change moved every shipped row 0.11 to 0.13 SD further above its
published mean. That is the same direction that this module attributes to the
circuit rather than to tissue return, and the shift is a tenth of the gap
that it adds to:

| Agent | Shipped, 10 L/min | Open circuit | Published |
| --- | --- | --- | --- |
| Sevoflurane | +3.79 SD | -0.15 SD | 0.157 +/- 0.020 |
| Isoflurane | +4.15 SD | +0.66 SD | 0.223 +/- 0.024 |
| Desflurane | +1.13 SD | -2.33 SD | 0.14 +/- 0.02 |

The second isoflurane cohort, left out of the table for width, moves from
+5.13 SD to +0.94 SD.

**The open-circuit column is a diagnostic, and the shipped simulator cannot be
put in the condition that produced it.** The column comes from
`_eliminate_without_rebreathing()` below, a driver that exists only in this
module. After each step of the elimination, the driver discards whatever the
patient exhaled into the circuit and records it as exhausted agent. So the
inspired fraction is held at zero instead of settling near a third of the
alveolar fraction. No fresh gas flow, dial position or patient setting
produces that condition, and no interface control offers it. `PL-W21J` weighed
a supported non-rebreathing mode against this driver. The project owner chose
the driver on 2026-09-06, because a mode would change the model boundary and
add one more thing that the interface would have to make visible. So every
number in that column describes this model's tissue return with the apparatus
taken away. None of them describes the simulator that anybody runs. Anyone
who restates those numbers must state that limit in the same sentence.

**What the diagnostic separates, which is the reason it was built.** The
apparatus accounts for the whole gap for sevoflurane and for both isoflurane
cohorts. Those three of the four rows sat +3.79 to +5.13 SD outside the
published spread, and they fall inside it once the apparatus is removed. For
desflurane the apparatus accounts for more than the gap. Desflurane crosses
its published mean and settles 2.33 SD below it, so without rebreathing this
model washes desflurane out *faster* than Yasuda's volunteers did. That
residual is a disagreement about tissue return, and the apparatus can no
longer explain it. It is also not a coefficient that this repository could
correct.
`test_no_measured_tissue_solubility_reaches_desflurane_s_published_elimination`
below records what was ruled out. `docs/MODEL.md` "Desflurane's residual, and
why the parameter file was not changed" gives the rest of the account and
what is left open. Neither column validates the shipped simulator's
elimination, and no test here claims that it does.

**Four caveats limit how much either comparison can show.** The first two are
the module's original caveats and apply to both directions. The third and
fourth apply to the elimination alone.

1. *The published subjects were breathing nitrous oxide.* Both protocols gave
   65-70% N2O together with the potent agent, so the measured curves include
   a second-gas effect that this model cannot reproduce. The model's alveolus
   has a fixed volume and holds a single gas. docs/MODEL.md's "Known
   limitations" excludes nitrous oxide, simultaneous gases, and concentration
   and second-gas effects alike. Its "Assumptions" section states outright
   that carrier gases are assumed not to affect kinetics. So the comparison
   is not perfectly matched, and the mismatch does not obviously err in a
   conservative direction. The mismatch affects the elimination ratio through
   its denominator as well as its numerator, because F_A0 is itself a
   measurement made under N2O.
2. *These are Gas Man parameters, derived to reproduce Eger's data.* The
   partition coefficients under test come from the same lineage as the
   measurements they are tested against (docs/MODEL.md, "Parameter
   provenance"). A pass shows that this implementation reproduces what its
   parameter set intends, not that the parameter set is independently right.
   The test could still have failed, which is what makes it worth running.
   But a pass is weaker than "validated against a human measurement" and must
   not be described as more. The parameter set's intent is also least
   reliable during wash-in, which is the direction this module's first
   comparison examines. Gas Man's own published agreement with patients is
   materially worse during wash-in than during maintenance (docs/MODEL.md,
   "Known limitations").
3. *The breathing systems differ, and the difference is larger than the
   measurement's own spread.* The paragraphs above measure its effect at 3.5
   to 4.2 published standard deviations per cohort. Any statement that this
   model eliminates more slowly than Yasuda's volunteers must carry this
   caveat, because most of that difference comes from a rebreathing circuit
   rather than from a patient.
4. *This model has no metabolism, and it has nothing on the scale of the
   fourth compartment that human washout needs. Neither gap matters at five
   minutes.* Over five minutes of elimination, metabolism is negligible for
   all three shipped agents, and the papers themselves bound it. Recovery is
   the agent recovered during elimination divided by the agent taken up. It
   was 101 +/- 7% for sevoflurane and 101 +/- 6% for isoflurane in the first
   study, and 105 +/- 25% for desflurane and 102 +/- 13% for isoflurane in
   the second. For halothane it was 64 +/- 9%, which shows that the same
   method does detect a metabolized agent. Both papers also report multi-day
   elimination curves. Those curves must not be added here, because over
   days the missing metabolism is no longer negligible. Neither is the fat
   compartment's flow. docs/MODEL.md's "Known limitations" weighs that flow
   against two human sources, which disagree about whether it is too high or
   too low. It is about twice a resting depot measurement, and at or a little
   below what the same papers' washout fits imply. Either way, the flow acts
   on the slow tail of washout. The measured tail departs from what this
   model can follow long before days have passed, though, and within the 24
   hours for which a run is supported. Every washout that these papers fitted
   needed a fourth compartment between muscle and fat, and this model has no
   counterpart for it. On the published mean coefficients, that
   compartment's term is the largest in the measured curve from about 1.8 to
   3.1 hours after the 30-minute administration until about 20.7 to 29.4
   hours (docs/MODEL.md, the intertissue-diffusion note under "Known
   limitations"). At five minutes the term is about one part in twenty of
   what remains. So the gap over those hours is measured beside this gate
   rather than enforced by it. test_late_washout_against_published_fits.py,
   in this directory, records the gap's size and direction over the first 24
   hours (docs/MODEL.md, "The first 24 hours of elimination against the
   published mean curves"). It asserts no agreement.

What the wash-in comparison does establish is this. Six coupled compartments,
an exact propagation of them, a circuit model and three parameter files
together land inside the measured spread of a human study for three agents at
once, ordered correctly by solubility. Nothing else in this suite can show
that, because no other test in it asserts agreement with a human measurement.
The module beside this one also looks outside the repository, but it asserts
nothing about agreement.

What the elimination comparison adds is different rather than more of the
same. The three agents rank correctly on the way out as well as on the way
in, and the size and sign of this model's departure from a human elimination
measurement are recorded rather than unknown. It also puts a lower bound on
the vessel-rich tissue coefficient, to which the wash-in comparison barely
responds.
That bound is looser than this docstring said before 2026-10-17, and the next
section gives the numbers.

**How sharp a gate this is, measured rather than assumed.** A validation is
only worth what it can detect. So each stored parameter was multiplied by a
factor, for one agent at a time, and the factor was varied until some
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
- **The early points detect too large an alveolar gas volume.** The volume
  passes only up to +19% for sevoflurane, +21% for isoflurane and +33% for
  desflurane. Above those values the 1-minute point fails.
- **The gate cannot detect fat for sevoflurane or isoflurane.** Both agents
  pass with the fat tissue:gas coefficient, or the fat volume, anywhere from a
  tenth to four times the stored value. A smaller circuit passes down to a
  tenth for those two agents as well, because the early points hold F_I fixed
  at the airway and so never respond to the circuit. Muscle is constrained
  only loosely.

Before 2026-10-17 this docstring said the elimination point constrained the
vessel-rich coefficient to about a fifth either way. That figure came from an
elimination assertion that kept the model's own ratio within one published
SD. It was a regression pin with a wide band, not a comparison with the
published value, so it never measured what a published value can detect.
`PL-RXW0` has since narrowed that pin to 1e-4.

`test_the_published_data_gate_fails_at_a_stated_perturbation` and
`test_the_published_data_gate_passes_at_a_stated_perturbation` keep the
table in step with the code. The first fails if the gate stops detecting a
blood:gas, vessel-rich or alveolar gas volume change that it detects today. The second
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

Wash-in at 30 minutes is a blood:gas measurement that barely responds to the
vessel-rich group, and elimination at five minutes is a vessel-rich
measurement that barely responds to blood:gas. That does not conflict with the
rebreathing account above. The circuit sets *where* the elimination ratio sits
against Yasuda, as a fixed offset of the operating point. Among the model's
own parameters, it is vessel-rich solubility that the ratio moves with.
Neither ratio responds to fat, which is what a 30-minute load and a 5-minute
washout should look like. That is a further reason not to read either
comparison as covering the slow tail.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass, replace
from functools import cache, partial

import pytest

from anesthesia_sim.app.wash_in import WashInDomain, read_wash_in
from anesthesia_sim.core.agent_simulation_validation import AgentSimulationValidationResult
from anesthesia_sim.core.concentration import Fraction, Percent, fraction_from_percent
from anesthesia_sim.core.numerical_envelope import CompartmentVolume, PartitionCoefficient
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

# The length of the measured wash-in. Both studies gave the potent agent for
# 30 minutes and report F_A/F_I at the end of it.
WASH_IN_DURATION_S = 1800.0

# The length of the measured elimination, also taken from the papers.
# Elimination begins when the 30 minutes above end, and both papers report
# F_A/F_A0 five minutes into it. F_A0 is the last alveolar fraction during
# administration, so the elimination run must continue the wash-in run rather
# than start from a system loaded some other way. That is why `_eliminate()`
# below washes in first rather than taking a system from `_wash_in_system()`.
ELIMINATION_DURATION_S = 300.0

# The step is imported rather than restated as 0.1, so this module measures the
# model as shipped, not a finer version of it that no user ever sees. Raising
# the supported step is a safety-critical change to every displayed value
# (docs/MODEL.md, "Supported simulation step"). If the step is ever raised,
# this validation should move with it and be re-measured. It should not keep
# running quietly at a step the interface no longer uses.
SIMULATION_STEP_S = SimulationStep(MAXIMUM_SIMULATION_STEP_S)

# The operating point. Alveolar ventilation and cardiac output are *not*
# chosen here. The code below reads them from the reference-patient data file,
# and `test_operating_point_is_the_parameter_files_own_defaults` fails if that
# ever stops being true. This matters more than anything else in the module.
# The agreement is sensitive to both settings, as
# `test_agreement_is_sensitive_to_ventilation_and_cardiac_output` shows. So an
# operating point picked to make the comparison pass would make the whole
# result circular. The operating point is instead the shipped default. It is
# cited to the Gas Man workbook and was fixed long before anyone compared this
# model with Yasuda's data.
#
# Fresh gas flow is the one setting that is chosen here. Both protocols held an
# inspired concentration at the airway. So the model's F_I, which is the
# circuit fraction and not the vaporizer dial, should have settled by 30
# minutes rather than still be rising. A 6 L circuit at 10 L/min has a time
# constant of 36 s, so it has settled. The choice barely matters either way.
# `test_agreement_survives_every_fresh_gas_flow` shows that every agent stays
# inside the published spread at every flow from 1 to 10 L/min, so the result
# does not depend on the pinned value.
FRESH_GAS_FLOW_L_MIN = 10.0

# One dial setting serves four published protocols that used four different
# inspired concentrations. This works because the governing equations are
# linear in the delivered fraction, so F_A/F_I does not depend on it.
# `test_ratio_does_not_depend_on_the_delivered_fraction` asserts this rather
# than assuming it, over the published concentrations themselves. Those
# concentrations are read from `PUBLISHED_MEASUREMENTS` below rather than
# restated, so the checked range cannot drift from the cited one.
DELIVERED_PERCENT = 1.0

# The published spread is the tolerance. Nothing here is fitted. The width of
# this band is the standard deviation that Yasuda reported. So a parameter or
# solver change that moves an agent outside its measured human spread fails,
# and one that keeps it inside does not.
#
# **Which question a band of one SD tests.** The module now makes this claim
# twice, and it is not the conventional one. A deterministic model compared
# with a cohort *mean* would ordinarily be judged against the standard error of
# that mean, SD/sqrt(n). For these cohorts that band is 2.6 to 2.8 times
# narrower. The claim asserted here is the weaker of the two, deliberately. It
# is that the model is a *plausible individual* drawn from the published
# cohort, not that it reproduces the cohort's mean. The distinction matters in
# practice. Desflurane's wash-in sits at +0.79 SD, which is +2.2 SEM. So the
# run that passes the claim this module makes would fail the claim it does not
# make. A reader who restates a passing run as "reproduces the published mean"
# has claimed something that this gate never tested.
AGREEMENT_TOLERANCE_SD = 1.0

# The elimination comparison does not agree, so its assertions are regression
# pins rather than agreement claims. Each pin requires the ratio this model
# produces (`MODELLED_ELIMINATION_RATIOS`, `OPEN_CIRCUIT_ELIMINATION_RATIOS`)
# to stay within this absolute tolerance of its stored value. So any change to
# washout fails and has to be explained. The ratios are stored to four
# decimals, so rounding moves them by at most 5e-5. A tolerance of 1e-4 leaves
# room for that rounding and for nothing a model change would produce. Until
# `PL-RXW0` the pin was one published SD, a relative band of 6% to 12%. That
# band let desflurane's ratio drift by 12% while every table that quoted it
# went stale. The pin asserts nothing about agreement with Yasuda. The distance
# from the published mean is measured in
# `test_five_minute_elimination_ratio_regression_pin`, and is between +1.0 and
# +5.0 SD.
ELIMINATION_RATIO_PIN_TOLERANCE = 1e-4

# The ratios that the shipped parameters produce at the reference operating
# point, measured on 2026-09-06 and pinned to the tolerance above. These are
# model outputs, so they are deliberately not fields of `PublishedMeasurement`.
# Nothing here was published. A model value stored in a row of published ones
# could lead a later reader to cite a model output as a human measurement.
MODELLED_ELIMINATION_RATIOS = {"sevoflurane": 0.2328, "isoflurane": 0.3227, "desflurane": 0.1626}

# The same ratios with the rebreathing circuit taken away, produced by
# `_eliminate_without_rebreathing()` and measured on 2026-09-07. They are kept
# in a second dictionary rather than as a third column of one. These values
# come from a condition that the shipped simulator has no setting for, while
# the values above come from the condition it ships in. A reader who took a
# value from the wrong dictionary would be describing a breathing system that
# does not exist. For the same reason as above, they are model outputs and not
# fields of `PublishedMeasurement`.
OPEN_CIRCUIT_ELIMINATION_RATIOS = {
    "sevoflurane": 0.1541,
    "isoflurane": 0.2388,
    "desflurane": 0.0935,
}

# How far removing the rebreathing circuit must move each cohort's comparison
# for this module's account of the elimination gap to remain true. The movement
# was measured on 2026-09-07 at 3.45 to 4.20 published SD, and is asserted at
# 3.0.
# `test_removing_the_rebreathing_circuit_is_what_moves_the_elimination_comparison`
# gives the per-cohort table. The margin is deliberately wide. The point being
# pinned is that the apparatus term is the large one, not its fourth digit,
# which the regression pins above and below already enforce.
MINIMUM_APPARATUS_MOVEMENT_SD = 3.0


@dataclass(frozen=True, slots=True)
class TissueSolubilityCeiling:
    """One published human brain:blood coefficient, used as an upper bound.

    `test_no_measured_tissue_solubility_reaches_desflurane_s_published_elimination`
    runs desflurane's elimination with its vessel-rich coefficient raised to
    each of these values. It then checks whether the run comes within reach of
    the published five-minute ratio. The values are ceilings, not candidate
    parameters. Nothing here is proposed to replace the value in
    `data/agents/desflurane.json`, and the test asserts that the comparison
    still misses, not that it improves.

    Attributes:
        tissue_blood_partition_coefficient: the ceiling itself, as a
            tissue:blood ratio. It is multiplied by desflurane's own stored
            blood:gas coefficient to give the tissue:gas coefficient that the
            model uses. So the run changes one number and keeps the agent's
            blood solubility at the value its own primary measurement gives.
        minimum_shortfall_sd: how far below the published elimination mean
            the run must still land, in that cohort's published standard
            deviations.
        what_it_is: a description of the measurement, for the failure
            message. The values are read from the abstract of Yasuda N,
            Targ AG, Eger EI II. *Solubility of I-653, sevoflurane,
            isoflurane, and halothane in human tissues.* Anesth Analg
            1989;69(3):370-3, PMID 2774233, which reports brain:blood as
            1.29 +/- 0.05 for I-653 (desflurane), 1.57 +/- 0.10 for
            isoflurane and 1.70 +/- 0.09 for sevoflurane, mean +/- SD. They
            were checked against PubMed on 2026-09-08.
    """

    tissue_blood_partition_coefficient: float
    minimum_shortfall_sd: float
    what_it_is: str


# Two ceilings, and the second is deliberately absurd for this agent. The
# first is the highest value that desflurane's own measurement supports. The
# second is the highest brain:blood measured for any of the three shipped
# agents. Desflurane cannot have that value without inverting the ordering
# that the source paper was written to report. Both ceilings still miss the
# published ratio, and that is the finding (`PL-73G7`).
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
# than assumed. In Yasuda 1991 *Anesthesiology* (PMID 2001028) SS "Materials
# and Methods", about 50 ml of corrugated Teflon sits between the tracheal
# end-tidal sampling port and the connection to the nonrebreathing valve. The
# paper says this volume protects the end-tidal sample from contamination with
# inspired gas. Both papers were supplied by the project owner and read on
# 2026-09-13. Neither is in PubMed Central, and neither is held in this
# repository.
APPARATUS_DEAD_SPACE_L = 0.050

# **That volume is a series dead space. In this model a series dead space
# lowers the alveolar ventilation rather than raising F_I above zero.** This
# distinction is the whole reason the diagnostic below is run the way it is,
# so it is derived here rather than asserted.
#
# Take one breath during the elimination, with agent-free fresh gas. Let V_D be
# the total series dead space, anatomic plus apparatus. At end-expiration both
# dead spaces hold alveolar gas at F_A. Inspiration pushes that V_D back into
# the alveoli, followed by (V_T - V_D) of agent-free gas. So the alveoli
# receive V_T of gas carrying V_D * F_A of agent, and they expel V_T of gas
# carrying V_T * F_A. The net is
#
#     V_D * F_A - V_T * F_A = -(V_T - V_D) * F_A
#
# This is exactly this model's `V_A_dot * (F_I - F_A)` with F_I = 0, provided
# that V_A_dot is the *true* alveolar ventilation (V_T - V_D) * f. So adding
# the apparatus's 50 ml at constant tidal volume and rate lowers alveolar
# ventilation by 50 ml * f and does nothing else. Treating the dead space
# instead as a non-zero inspired fraction would describe a mixing volume that
# returns a *fraction* of every breath. That is this model's circuit, not the
# published apparatus. The sixth candidate row in `docs/MODEL.md` SS
# "Desflurane's residual" has that non-zero inspired fraction shape.
#
# The model has no respiratory rate, so the decrement cannot be computed from
# stored parameters. The diagnostic is run at the rates below, which span the
# conventional range for a paralysed, mechanically ventilated, normocapnic
# adult. **Yasuda measured minute ventilation and derived the alveolar
# fraction from F_M = f_A * F_A + f_D * F_I. The numeric value is in the
# methods text and is not held here** (`PL-ZDWL`). So the range below stands
# in for it, and that range is an assumption of this diagnostic, not a datum.


@dataclass(frozen=True, slots=True)
class ApparatusDeadSpaceCase:
    """One respiratory rate, and how far desflurane must still miss at it.

    Attributes:
        respiratory_rate_per_min: breaths per minute. Together with
            `APPARATUS_DEAD_SPACE_L`, it sets how much the published
            apparatus's dead space lowers the alveolar ventilation.
        minimum_shortfall_sd: how far below its published elimination mean
            desflurane must still land, in that cohort's published standard
            deviations. Measured 2026-09-13 and asserted with margin.
    """

    respiratory_rate_per_min: float
    minimum_shortfall_sd: float

    @property
    def alveolar_ventilation_l_min(self) -> float:
        """Return the reference default ventilation, less what the apparatus dead space removes.

        The baseline is read from the parameter file rather than restated. So
        if the reference adult's default ventilation is ever changed, this
        diagnostic follows it instead of silently comparing against a stale
        number.
        """

        return (
            load_reference_adult_parameters().default_alveolar_ventilation_l_min
            - APPARATUS_DEAD_SPACE_L * self.respiratory_rate_per_min
        )


# Measured on 2026-09-13 across the conventional range. With no apparatus dead
# space at all, desflurane's open-circuit residual is -2.33 SD. The shortfalls
# below are what is left of that residual once the sourced dead space is
# applied. At the largest shortfall the dead space accounts for 0.44 SD of the
# 2.33, and at the smallest it accounts for 0.95 SD.
APPARATUS_DEAD_SPACE_CASES = (
    ApparatusDeadSpaceCase(respiratory_rate_per_min=6.0, minimum_shortfall_sd=1.75),
    ApparatusDeadSpaceCase(respiratory_rate_per_min=8.0, minimum_shortfall_sd=1.60),
    ApparatusDeadSpaceCase(respiratory_rate_per_min=10.0, minimum_shortfall_sd=1.40),
    ApparatusDeadSpaceCase(respiratory_rate_per_min=12.0, minimum_shortfall_sd=1.25),
)

# The largest decrement that the wash-in comparison allows. At 50 ml and 11
# breaths per minute, every wash-in row is still inside its published spread.
# Sevoflurane's row is nearest the edge, at -0.96 SD, and one more breath per
# minute takes it outside (-1.08 SD at 12). Measured on 2026-09-13.
LARGEST_ADMISSIBLE_DEAD_SPACE_CASE = ApparatusDeadSpaceCase(
    respiratory_rate_per_min=11.0, minimum_shortfall_sd=1.25
)


@dataclass(frozen=True, slots=True)
class PublishedMeasurement:
    """One agent's two measured ratios, from one published cohort.

    Both quantities come from the same subjects in the same sitting. The
    wash-in figure was taken at the end of the administration, and the
    elimination followed that administration. So they belong on one row, not
    in two tables that could come to disagree about which cohort is which.

    Each field name says which ratio it describes. A field named `mean` alone
    was unambiguous while this module compared one quantity, but it is not
    now. A reader who has to infer which quantity a mean describes can
    misread it, and `CLAUDE.md`'s safety-critical standard treats that kind of
    error as part of the value.
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
    figures' 30-minute points this way gives values within 0.006 of the
    30-minute means that the papers' text states. That difference is the size
    of a reading error here. The note
    `docs/references/yasuda-1991-figure-2-wash-in.md` gives the method, the
    figure and page, and every value read.

    Attributes:
        agent_id: the agent.
        time_min: minutes from the start of administration. It is the
            protocol's sample time at which the point is plotted.
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

# Every sample time at which some cohort is compared, in order. One clamped run
# per agent is read at each of these times.
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

# The top of that regression band. When the comparison was first run, the worst point was
# +2.10 SD. A reading error of 0.006 in a mean is about 0.3 SD at desflurane's spread. So a
# ceiling of 2.5 SD leaves room for that reading error. It still catches a change that moves
# the model further from the measurement.
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

# The stored parameters that a resolving-power case may change, grouped by the
# record that stores each one. Each name is a field of that record, so
# `getattr` reads the shipped value and `dataclasses.replace` builds the
# changed record.
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
    is applied to the parameter record that stores the value. The part of the
    system built from that record is then rebuilt from the changed copy, by
    the same code that the shipped system uses. So a changed blood:gas
    coefficient affects every compartment, and the tissue:blood ratios move
    inversely, exactly as they would if the stored blood:gas value alone were
    wrong.

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

    def apply(self, agent_id: str, system: AgentUptakeSystem) -> AgentUptakeSystem:
        """Rebuild the part that this change affects, and return the system that holds it.

        The change must be applied before the first step, while every
        compartment holds no agent and no propagator has been built for the
        old value. Each rebuilt part goes through the constructor or setter
        that checks a shipped value. So a changed value that this code would
        not accept is refused rather than run. A built system refuses a new
        patient (`PL-N7MM`). So a change to the patient builds a new system,
        which holds the new patient and the other parts of the unstepped
        `system`. Every other change is written onto `system`, which is
        returned.

        Raises:
            ValueError: `parameter` names no field this class knows.
        """

        agent = load_agent_parameters(agent_id)
        patient = load_reference_adult_parameters()

        if self.parameter in AGENT_PARAMETER_FIELDS:
            changed_coefficient = PartitionCoefficient(
                getattr(agent, self.parameter) * self.factor, name=self.parameter
            )
            changed_agent = replace(agent, **{self.parameter: changed_coefficient})

            return AgentUptakeSystem(
                circuit=system.circuit,
                alveoli=system.alveoli,
                patient=PatientCompartments.from_parameters(agent=changed_agent, patient=patient),
            )

        if self.parameter in PATIENT_COMPARTMENT_FIELDS:
            changed_volume = CompartmentVolume(
                getattr(patient, self.parameter) * self.factor, name=self.parameter
            )
            changed_patient = replace(patient, **{self.parameter: changed_volume})

            return AgentUptakeSystem(
                circuit=system.circuit,
                alveoli=system.alveoli,
                patient=PatientCompartments.from_parameters(agent=agent, patient=changed_patient),
            )

        if self.parameter == ALVEOLAR_GAS_VOLUME_FIELD:
            system.alveoli.gas_volume_l = CompartmentVolume(
                patient.alveolar_gas_volume_l * self.factor, name=self.parameter
            )
        elif self.parameter == CIRCUIT_VOLUME_FIELD:
            system.circuit.set_circuit_volume(
                CompartmentVolume(
                    load_reference_circle_system_parameters().circuit_volume_l * self.factor,
                    name=self.parameter,
                )
            )
        else:
            raise ValueError(f"no stored parameter is named {self.parameter!r}")

        return system


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

    The system has not been stepped. Every run in this module and in
    `test_late_washout_against_published_fits.py` starts from this setup. It
    is kept in one place so that an elimination provably runs from the same
    operating point as the wash-in comparisons. Three copies of a
    safety-critical setup that must agree would give three chances for one of
    them to drift silently.

    `None` for either patient flow means the reference patient's own default.
    Every comparison against a published value uses that default. The
    sensitivity tests pass explicit values to move off that point.

    `vessel_rich_tissue_gas_partition_coefficient` overrides one stored
    coefficient directly, and it exists for one test.
    `test_no_measured_tissue_solubility_reaches_desflurane_s_published_elimination`
    asks what the *published human tissue measurements* would produce here.
    That question needs a run with a coefficient that the data files do not
    hold. The override is applied before any step, while the group's stored
    amount is zero and no propagator has been built for the old value. It goes
    through `dataclasses.replace`, whose constructor checks the new
    coefficient exactly as it checks a shipped one. Every other caller leaves
    it `None` and gets the shipped parameter set.

    `change` is the resolving-power tests' override, and `StoredParameterChange`
    documents it. Every comparison against a published value leaves it `None`.
    """

    patient_parameters = load_reference_adult_parameters()
    system = AgentUptakeSystem.for_agent(agent_id)

    if vessel_rich_tissue_gas_partition_coefficient is not None:
        system.patient.vessel_rich = replace(
            system.patient.vessel_rich,
            tissue_gas_partition_coefficient=PartitionCoefficient(
                vessel_rich_tissue_gas_partition_coefficient,
                name="vessel_rich_tissue_gas_partition_coefficient",
            ),
        )

    if change is not None:
        system = change.apply(agent_id, system)

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
    vaporizer dial. The circuit fraction is what the published studies
    measured, as an inspired concentration at the airway. The two are not
    equal here. Alveolar uptake keeps the circuit measurably below the dial
    for the whole run, so dividing by the dial instead would understate every
    ratio.
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
    """Return F_A/F_I after 30 minutes of wash-in at one operating point.

    F_I is the *circuit* fraction at the moment of measurement, not the
    vaporizer dial. The circuit fraction is what the published studies
    measured, as an inspired concentration at the airway. The two are not
    equal here. Alveolar uptake keeps the circuit measurably below the dial
    for the whole run, so dividing by the dial instead would understate every
    ratio.
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

    `_wash_in_system()` returns a system in the same state, but its instance
    must not be used for an elimination. That instance is cached and shared
    with every wash-in comparison in this module. Stepping it further would
    leave each of those comparisons measuring a washed-out system. This
    function is deliberately not cached, for the same reason. A cached system
    is a shared mutable one, and both callers here step the system they are
    given.

    Both elimination drivers start from this function rather than each
    keeping its own copy of the setup. The setup itself comes from
    `_configured_system()`, which also documents the direct coefficient override
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

    This is a value object rather than the system itself, because
    `_eliminate()` is cached and a returned system would be shared and
    mutable. A caller that stepped it further would silently change what
    every later call with the same arguments returns. No caller outside needs
    the system, so none gets it.

    Attributes:
        alveolar_fraction_at_discontinuation: F_A0, the alveolar fraction at
            the moment the vaporizer was closed. This is the papers' own
            definition of the denominator.
        alveolar_fraction: F_A after `ELIMINATION_DURATION_S`.
        inspired_fraction: F_I at the same moment. It is not part of the
            published ratio. It is the quantity that
            `test_elimination_is_dominated_by_the_rebreathing_circuit`
            and the module docstring's apparatus discussion are about.
    """

    alveolar_fraction_at_discontinuation: float
    alveolar_fraction: float
    inspired_fraction: float

    @property
    def ratio(self) -> float:
        """Return F_A/F_A0, the quantity both papers report at 5 minutes."""

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

    The protocol is the papers' own. Give the agent at a held inspired
    concentration for 30 minutes, record the last alveolar fraction as F_A0,
    discontinue, and read F_A five minutes later. Discontinuing means closing
    the vaporizer and nothing else. The fresh gas flow, ventilation and
    cardiac output all stay at their wash-in values, because the published
    protocols also held those settings constant through elimination.

    The system comes from `_private_washed_in_system()` rather than from
    `_wash_in_system()`, whose cached instance is shared with every wash-in
    comparison in this module. Stepping that instance into elimination would
    leave every later wash-in reading measuring a washed-out system.

    `change` is the resolving-power override that `_configured_system()`
    documents, and it applies to both the wash-in and the elimination.
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

    This function alone is what makes the driver below an open circuit, and it
    is deliberately two operations rather than one. Zeroing the circuit
    fraction on its own would delete agent from a system that checks its own
    conservation. `AgentSimulationValidator` enforces the identity `initial +
    delivered = exhausted + stored`. So agent taken out of the circuit and
    recorded nowhere is treated as agent the model lost, and the next
    `advance()` halts the run because of it. Recording the same amount as exhausted is
    what a non-rebreathing circuit does physically: the expirate leaves the
    system instead of being returned to the patient. So the identity still
    holds exactly, which
    `test_the_open_circuit_driver_neither_creates_nor_loses_agent` asserts
    rather than assumes.

    Both halves go through the public setters that the shipped code uses. So
    this function changes the apparatus and never the equations. What the
    patient does with the gas it receives is left to the unmodified model.
    """

    discarded_agent_l = system.circuit.agent_amount_l

    system.circuit.set_inspired_partial_pressure_fraction(Fraction(0.0))
    system.agent_simulation_validator.record_external_agent_transfer(
        delivered_agent_l=0.0, exhausted_agent_l=discarded_agent_l
    )


@dataclass(frozen=True, slots=True)
class OpenCircuitEliminationReading:
    """The result of one elimination run at an inspired fraction of zero.

    This is a type of its own rather than a flag on `EliminationReading`. The
    two types describe different breathing systems, and only one of them
    describes the simulator that ships. A single type for both would let a
    reading taken under the diagnostic reach a comparison written for the
    shipped condition. `CLAUDE.md` treats that class of error as part of the
    value rather than as a side issue.

    Attributes:
        alveolar_fraction_at_discontinuation: F_A0, the alveolar fraction at
            the moment the vaporizer was closed. This is the papers' own
            definition of the denominator. The wash-in that produced it is the
            shipped one, rebreathing included. That wash-in is already inside
            the published spread at every supported flow, and F_A0 is defined
            at its end.
        alveolar_fraction: F_A after `ELIMINATION_DURATION_S`.
        peak_inspired_to_starting_alveolar_ratio: the largest ratio, over the
            run, of F_I at the end of a step to F_A at the start of the same
            step. It shows how far from a true open circuit the driver
            actually got. The denominator is the starting F_A because the
            bound in
            `test_the_open_circuit_driver_holds_the_inspired_fraction_near_zero`
            is stated against that value (`PL-RXW0`). That test reads this
            field.
        agent_accounting: the result of the model's own conservation check at
            the end of the run. It is returned rather than asserted here, so
            that a failing test can name the totals.
    """

    alveolar_fraction_at_discontinuation: float
    alveolar_fraction: float
    peak_inspired_to_starting_alveolar_ratio: float
    agent_accounting: AgentSimulationValidationResult

    @property
    def ratio(self) -> float:
        """Return F_A/F_A0, the quantity both papers report at 5 minutes."""

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

    **This is a test-only driver, and no setting of the shipped simulator can
    produce the condition it creates.** `docs/MODEL.md` gives the model one
    ideal circuit, which is a closed recirculating path except for fresh-gas
    inflow and exhaust. So inspired gas is circuit gas, and during any
    elimination F_I settles near `V_A/(V_A + fresh gas flow)` times F_A. That
    factor is 0.29 at the highest supported flow. The published protocols
    collected the whole expirate instead, so their elimination ran at an
    inspired fraction at or near zero. Wherever a number from this function is
    stated, this limit must be stated with it.

    The mechanism is `_discard_circuit_contents()`, applied at the start of
    the elimination and after every step of it. Whatever the patient exhaled
    into the circuit leaves the system as exhausted agent instead of being
    offered back on the next breath. Nothing else changes. The equations, the
    propagator, the compartments, the step and the operating point are the
    shipped ones, and the wash-in is not touched at all. So the driver
    isolates the apparatus and nothing else about the model.

    **It is an open circuit to within one step, not exactly.** Settings are
    held constant across a step, so within each step the circuit refills from
    the alveoli. F_I rises from zero to at most `V_A * step / circuit volume`
    times the F_A at the start of the step. That is 1.1e-3 at the shipped
    step, against the 0.30 to 0.32 that the same run settles at with
    rebreathing. The residual is first-order in the step. It was measured at
    1.111e-3, 1.111e-4 and 5.555e-5 at steps of 0.1, 0.01 and 0.005 s. Its
    effect on the result was measured the same way on 2026-09-07.
    Sevoflurane's ratio moves from 0.154059 at the shipped 0.1 s step to
    0.153984 at 0.005 s, which is 0.004 published SD, and the other two agents
    move less. So the numbers this driver produces match the F_I = 0 limit to
    about three parts in ten thousand. The residual is reported rather than
    assumed away, and
    `test_the_open_circuit_driver_holds_the_inspired_fraction_near_zero`
    fails if it grows.

    `elimination_fresh_gas_flow_l_min` changes the fresh gas flow at the
    moment of discontinuation. By default the flow stays at its wash-in value.
    Only `test_the_open_circuit_elimination_does_not_depend_on_fresh_gas_flow`
    passes it. That test separates the flow's effect on the elimination from
    its effect on the state that the elimination starts from.

    `vessel_rich_tissue_gas_partition_coefficient` is passed on to
    `_private_washed_in_system()`, which documents it. It replaces a shipped
    coefficient, so it changes both the wash-in and the elimination. That is
    what the one test that passes it needs.
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
    """The result of one wash-in with the inspired fraction held at the airway.

    Attributes:
        ratios: F_A/F_I at each of `EARLY_WASH_IN_SAMPLE_TIMES_MIN`, keyed by
            the time in minutes.
        peak_inspired_deviation: the largest relative difference between the
            circuit's F_I at the end of a step and the held value, before the
            driver set it back. It shows how far from a true clamp the driver
            got. `test_the_inspired_clamp_holds_the_inspired_fraction` reads
            it.
        agent_accounting: the result of the model's own conservation check
            at the end of the run.
    """

    ratios: dict[float, float]
    peak_inspired_deviation: float
    agent_accounting: AgentSimulationValidationResult


def _hold_inspired_fraction(system: AgentUptakeSystem, inspired_fraction: Fraction) -> None:
    """Set the circuit back to `inspired_fraction`, and record where the agent went.

    This function alone is what makes the driver below a non-rebreathing
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

    **This is a test-only driver, and no setting of the shipped simulator can
    produce the condition it creates.** The shipped circuit starts empty and
    fills at its own time constant, so its F_I lags the dial for the first
    minute or more. Both papers gave the agents as a square wave from a
    non-rebreathing circuit, so their F_I was the cylinder's fraction from the
    first breath (Yasuda et al., Anesth Analg 1991;72:316-24, page 317).
    Dividing the shipped run's F_A by its own lagging F_I would compare a
    different experiment with the published curve.

    The mechanism is `_hold_inspired_fraction()`, applied before the first
    step and after every step. The equations, the propagator, the
    compartments, the step and the patient's operating point are the shipped
    ones. So the driver isolates the breathing system and nothing else. The
    fresh gas flow does not affect the result, because the circuit is set
    back after every step. The circuit volume affects it only through the
    size of the drift within a step.

    **It holds F_I fixed to within one step, not exactly.** Within a step the
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
    calls it again with a stored parameter changed.
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

    This is the elimination half of the published-data gate. It checks the
    sign of the disagreement and not its size. The size is checked by a
    regression pin on the model's own output
    (`ELIMINATION_RATIO_PIN_TOLERANCE`). Any change at all fails that pin, so
    the pin is no evidence about any one parameter.
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
    points come first because one clamped run serves all of them. The
    regression pins and the diagnostics are left out, because a pin fails on
    any change and so says nothing about whether a published value could
    detect one. The gate passes when nothing is yielded. The function is a
    generator so that a caller that needs only the first failure stops the
    runs there.
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

    Desflurane has the least room, at four fifths of a standard deviation.
    That is a property of the measurement rather than of the model. Its
    published spread is the tightest of the three, at +/- 0.01, because a
    poorly soluble agent's curve is flat by 30 minutes and there is little
    left to vary. A future change that moves desflurane out of this band
    should be treated as a real disagreement to explain, not as a tolerance
    to widen.
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
    operating point is an unlikely cause. The isoflurane breathed by the same
    eight volunteers in the same sitting follows its curve. Sevoflurane and
    isoflurane both sit slightly *below* their curves early, whereas a
    ventilation or lung volume error would move every agent the same way. So
    the candidate cause is something only desflurane has, such as its blood:gas
    or vessel-rich tissue:gas coefficient. `PL-RFLN`'s elimination residual
    concerns the same agent. Those points are checked against a regression
    band, as `EARLY_WASH_IN_DISAGREEMENTS` says, so the disagreement cannot
    grow unseen.

    **What this comparison can detect.** It is part of the published-data
    gate. `docs/MODEL.md` § "What the published-data gate can and cannot
    resolve" gives, for each stored parameter, the factor at which a change
    makes the gate fail. A doubled alveolar gas volume moves sevoflurane's
    1-minute F_A/F_I from 0.537 to 0.429, -2.85 SD, so the early points catch
    the error the 30-minute comparison at 10 L/min could not.
    """

    failure = _early_wash_in_failure(point)

    assert failure is None, failure


def test_every_named_early_disagreement_is_a_published_point() -> None:
    """A label in `EARLY_WASH_IN_DISAGREEMENTS` must name a point that exists.

    A label that matched no point would name a regression band that applies
    to nothing. A reader of the set would then believe that a disagreement is
    being tracked when it is not.
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
    carries the same fraction, so it does not move F_I. The bound is
    computed here from the parameter files the run uses. As measured on
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
    `advance()`'s own accounting. Agent added without being recorded would
    look like agent the model created. So the model's own conservation check
    is read at the end of the run. As measured on 2026-10-18, its relative
    error is 3e-13 for each agent, which is rounding error.
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

    Everything above divides the two compartment fractions directly, which
    matches the definition the published studies measured. The interface
    draws F_A/F_I through `app/wash_in.py`, which adds a domain to it. Two
    expressions of one quantity are exactly the divergence that `CLAUDE.md`
    warns about. The validated number and the displayed number could drift
    apart with nothing to notice. So this test asserts that they are the
    same number, and that a settled 30-minute wash-in is inside the domain
    the chart will actually draw.

    This is the only place where `tests/reference/` imports from `app/`, and
    the module it imports is Flet-free and holds one arithmetic rule. In
    return, a change to the displayed ratio's definition fails against a
    human measurement, not only against a unit test.
    """

    system = _wash_in_system(agent_id)
    reading = read_wash_in(
        system.alveoli.partial_pressure_fraction, system.circuit.inspired_partial_pressure_fraction
    )

    assert reading.domain is WashInDomain.WASH_IN
    assert reading.plotted_ratio == pytest.approx(_wash_in_ratio(agent_id))


def test_published_agents_are_ordered_by_solubility() -> None:
    """The model must reproduce the ordering the studies were run to show.

    Both papers were written to test one prediction: that a less soluble
    agent approaches its inspired concentration faster. Matching three means
    while getting their order wrong would be a coincidence rather than a
    model. So the ordering is asserted separately from the values. Three
    independent tolerances that happen to overlap cannot pass this part.
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

    So changing a default in that file must break this test loudly, because
    the change moves the flows the comparison runs at. It must not quietly
    leave a hard-coded 4.0 and 5.0 behind that still pass but no longer
    describe the shipped model.
    """

    patient_parameters = load_reference_adult_parameters()

    assert patient_parameters.default_alveolar_ventilation_l_min == 4.0
    assert patient_parameters.default_cardiac_output_l_min == 5.0


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_ratio_does_not_depend_on_the_delivered_fraction(agent_id: str) -> None:
    """One dial setting may stand for four published inspired concentrations.

    The two protocols used 0.4%, 0.6%, 1.0% and 2.0%, depending on agent and
    cohort. Those values are `PUBLISHED_INSPIRED_PERCENTS`, read from the
    cited rows themselves. Every comparison above runs at 1.0%. That
    substitution is valid only because the governing equations are linear in
    the delivered fraction, which makes F_A/F_I independent of it. So the
    claim is checked across the published range rather than asserted in a
    comment.

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
    """Fresh gas flow is the one setting chosen here, and the result does not depend on it.

    Alveolar ventilation and cardiac output come from the data file, but
    `FRESH_GAS_FLOW_L_MIN` was picked to match the protocols' held inspired
    concentration. A reader may fairly ask how much of the agreement that
    choice bought. The answer is none of it. Across the whole supported flow
    range above zero, every agent stays inside its published spread. The
    endpoints differ by at most about one standard deviation (desflurane,
    -0.33 SD at 1 L/min to +0.79 SD at 10 L/min).

    Zero is excluded because it is not an operating point of these
    protocols. With no fresh gas the circuit never carries agent, so F_I is
    zero and the ratio is undefined rather than wrong.
    """

    failure = _wash_in_band_failure(measurement, fresh_gas_flow_l_min)

    assert failure is None, failure


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_agreement_is_sensitive_to_ventilation_and_cardiac_output(agent_id: str) -> None:
    """Show how much of the tolerance the operating point uses up.

    A validation that agrees at one operating point and nowhere else is worth
    less than one that agrees over a range. A reader cannot tell which kind
    this is from a passing test alone. So the sensitivity is measured rather
    than described. The table was measured on 2026-09-02, in each cohort's
    own standard deviations, against the first published value for each
    agent:

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
      by more than a published standard deviation. The effect is comparable
      to the ventilation axis, in the opposite direction. But the agents do
      not leave the band in both directions. At 4 L/min all three fall
      outside it. At 6 L/min all three remain inside, and desflurane actually
      moves *closer* to its published mean than it is at the shipped default.
      So the claim asserted here is the movement, not the exit, because the
      movement is what is true.

    That is exactly why cardiac output belongs beside ventilation. A reader
    given only the ventilation axis would underestimate how specific this
    operating point is. A reader told that both axes leave the band would
    overestimate it.

    The window is narrow, and saying so is the point. This is a comparison at
    one physiological operating point. It does not show that the model tracks
    Yasuda's data across the ventilation and perfusion axes. What keeps the
    comparison from being circular is not a wide window. It is the fact that
    the operating point was not chosen to make it pass, which
    `test_operating_point_is_the_parameter_files_own_defaults` asserts.
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


# Changes that the gate detects for every agent, measured on 2026-10-18 with
# the early wash-in points included in the gate (`PL-R0NL`). The early points
# set most of these edges. A blood:gas change fails the gate at x0.95 to x0.99
# below and x1.05 to x1.10 above. So x1.10 is not used, because desflurane
# passes it: desflurane's edge is x1.097. A vessel-rich tissue:gas change
# fails the gate at x0.85 to x0.97 below and x1.11 to x1.55 above. An alveolar
# gas volume change fails it at x1.19 to x1.33 above, at the 1-minute point.
DETECTED_CHANGES = (
    *_cases("blood_gas_partition_coefficient", 0.90, "blood-gas-x0.90"),
    *_cases("blood_gas_partition_coefficient", 1.15, "blood-gas-x1.15"),
    *_cases("vessel_rich_tissue_gas_partition_coefficient", 0.80, "vessel-rich-tissue-gas-x0.80"),
    *_cases("vessel_rich_tissue_gas_partition_coefficient", 1.75, "vessel-rich-tissue-gas-x1.75"),
    *_cases(ALVEOLAR_GAS_VOLUME_FIELD, 1.50, "alveolar-gas-volume-x1.50"),
)

# Changes that the gate cannot detect. Each one is a stored value, wrong by the
# stated factor, that still passes every published-data assertion. So a
# passing gate says nothing about whether that value is right. A row that names
# agents leaves out the others, because their edge lies inside the factor.
# Isoflurane and desflurane fail when the alveolar gas volume is halved,
# because they fail below x0.61 and x0.92 respectively. Sevoflurane and
# isoflurane fail when the venous pool is doubled, because they fail above
# x1.86 and x1.60 respectively. Isoflurane's lower venous pool edge is x0.50
# itself. The fat volume case runs for one agent only. A tissue's capacity is
# its volume times its tissue:gas coefficient, so doubling either one changes a
# run identically. The edge searches of 2026-10-17 and 2026-10-18 found the
# same edges for both, for every agent.
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
    """The gate that the resolving-power tests use must pass with no change applied.

    `_published_data_gate_failures()` restates no criterion of its own. It
    calls the same checks that the published-data tests above assert. This
    test asserts that it yields nothing for the shipped parameter set. So a
    failure detected below is a response to the change, not a gate that fails
    on everything.
    """

    failures = list(_published_data_gate_failures(agent_id))

    assert not failures, failures


@pytest.mark.parametrize("case", DETECTED_CHANGES, ids=[case.label for case in DETECTED_CHANGES])
def test_the_published_data_gate_fails_at_a_stated_perturbation(case: ResolvingPowerCase) -> None:
    """The gate must detect a stored value wrong by the stated factor.

    This turns the resolving-power table in `docs/MODEL.md` into an
    assertion. Suppose a parameter or solver change made the gate unable to
    detect a change in blood:gas, vessel-rich tissue:gas or the alveolar gas
    volume. Without this test, that table would still claim a resolving power
    that the gate no longer has.
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

    `docs/MODEL.md` tells a reader that a passing gate says nothing about
    these stored values. This test keeps that statement true. If a model
    change made the gate sensitive to one of them, the statement would
    understate what the gate shows. This test then fails, so that the table
    is re-measured rather than left stale. A failure here is not a defect in the
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

    The table was re-measured on 2026-09-07 with `venous_pool_volume_l` =
    1.222 L. That change moved every row 0.11 to 0.13 SD further above its
    mean (`PL-8ZJQ`).

    Every row is *above* its published mean, which means the model retains
    more alveolar agent at five minutes than the volunteers did. The module
    docstring gives the measured cause, which is largely the breathing system
    rather than tissue return. This model rebreathes and the published
    protocol did not. Running the same five minutes through
    `_eliminate_without_rebreathing()` instead moves the same three agents to
    -0.15, +0.66 and -2.33 SD.
    `test_five_minute_elimination_ratio_without_rebreathing_regression_pin`
    makes that comparison. It runs in a diagnostic condition that no setting
    of this simulator can produce.

    So what this test asserts is that the model still produces the ratios in
    `MODELLED_ELIMINATION_RATIOS`, to within
    `ELIMINATION_RATIO_PIN_TOLERANCE`. Its name says regression pin, because
    the expected values are this model's own outputs and not the published
    means. The pin is worth asserting for the same reason as the wash-in
    comparison. It is the only thing in this repository that compares
    elimination with an outside number at all. A change that moves the
    result must be re-measured and explained, in whichever direction it
    moves. A change that moved these rows *inside* the published band would
    fail here too, and it should. It would mean that this table and the
    docstring around it describe a model that no longer exists.
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

    The regression pin above fixes the magnitude and would fail on a move in
    either direction. This test pins the sign, which is the part a reader of
    the model needs. The modelled alveolar fraction at five minutes of
    elimination is higher than every published cohort's. So a learner
    watching this simulator's washout sees a slower recovery than these
    volunteers had, not a faster one.

    The sign is asserted separately from the magnitude, because a change in
    each would mean something different. A magnitude that moved is a
    measurement to redo. A sign that flipped would mean that the model had
    crossed the published values, and every statement in this module about
    which side it sits on would be wrong.
    """

    failure = _elimination_direction_failure(measurement)

    assert failure is None, failure


def test_eliminated_agents_are_ordered_by_solubility() -> None:
    """The published elimination ordering must be reproduced.

    This is the part of the elimination comparison that is a validation
    rather than a regression pin. It is the one claim here that the
    disagreement above does not affect. Both papers report the same
    ordering: desflurane leaves fastest, then sevoflurane, then isoflurane.
    That is the prediction the papers were written to test, in the opposite
    direction from the wash-in ordering that
    `test_published_agents_are_ordered_by_solubility` checks. Published:
    0.14, 0.157, 0.22-0.223. Modelled 2026-09-07: 0.1626, 0.2328, 0.3227.

    An ordering survives the apparatus mismatch that the module docstring
    measures, because the rebreathing displaces every ratio upward, all in the
    same direction. So this claim is weaker than the wash-in ordering, but it
    is real. Three agents that differ only in their partition coefficients
    rank correctly on the way out as well as on the way in.
    """

    failure = _elimination_ordering_failure()

    assert failure is None, failure


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_elimination_ratio_does_not_depend_on_the_delivered_fraction(agent_id: str) -> None:
    """One dial setting may stand for four published inspired concentrations.

    The wash-in counterpart of this test gives the argument. The governing
    equations are linear in the delivered fraction, so a ratio of two
    fractions from the same run does not depend on it. The claim is checked
    again for the elimination ratio rather than assumed to carry over,
    because the two ratios are not the same quotient. F_A/F_A0 divides the
    alveolar fraction by an earlier value of itself. A future nonlinearity
    could leave one ratio invariant while breaking the other.
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

    This assertion keeps the elimination result from being over-read, and it
    mirrors `test_agreement_survives_every_fresh_gas_flow`. That test shows
    that the wash-in result does *not* depend on fresh gas flow: every agent
    stays inside its published spread from 1 to 10 L/min. Here the same sweep
    moves the elimination ratio across many published standard deviations.
    The table was re-measured on 2026-09-07, as distance from the first
    cohort's mean:

    | Agent | 1 | 2 | 4 | 6 | 8 | 10 L/min |
    | --- | --- | --- | --- | --- | --- | --- |
    | Sevoflurane | +21.99 | +15.78 | +9.35 | +6.38 | +4.77 | +3.79 |
    | Isoflurane | +15.69 | +12.04 | +8.07 | +6.07 | +4.91 | +4.15 |
    | Desflurane | +22.73 | +15.03 | +7.26 | +3.86 | +2.13 | +1.13 |

    From one end of the sweep to the other, that is a movement of 11.5 to
    21.6 published SD.
    `test_the_open_circuit_elimination_does_not_depend_on_fresh_gas_flow` is
    the counterpart: with the circuit discarded each step, the same sweep
    moves the ratio by 4e-6 SD.

    `docs/MODEL.md` § "Model boundary" gives the mechanism. Inspired gas is
    circuit gas, and the circuit is a closed recirculating path except for
    fresh-gas inflow and exhaust. So during elimination the inspired fraction
    settles near V_A/(V_A + fresh gas flow) times the alveolar fraction. At
    the highest supported flow that factor is 4/(4+10), or 0.29. F_A/F_I
    divides that term out and F_A/F_A0 does not. That is the whole reason one
    comparison is insensitive to flow and the other is not.

    Both the magnitude and the direction are asserted, at the two ends of the
    supported range. So a future circuit or ventilation change that made the
    elimination ratio insensitive to flow would fail here. It should fail,
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
    here is the ratio the chart draws. The opposite case matters just as
    much, and `app/wash_in.py` was written for it. Five minutes into
    elimination the alveolar fraction is about three times the inspired
    fraction. So the quotient is far above `WASH_IN_EQUILIBRIUM_RATIO`, and
    the reading is `WashInDomain.ELIMINATION` with no number to plot.

    This test checks the rule against a run built from a published protocol
    rather than from chosen fractions, which `tests/unit/test_wash_in.py`
    cannot do. It shows that the domain rule excludes a *physiologically
    real* washout that this simulator can be driven into, not just a
    constructed pair of numbers. A regression that let this run plot would
    draw a wash-in curve for a patient who is waking up.
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
    """Compare the same five minutes against all four cohorts, with the apparatus removed.

    **The condition below is a diagnostic, and the shipped simulator cannot be
    put in it.** `_eliminate_without_rebreathing()` holds the inspired
    fraction at zero by discarding the circuit after every step. The
    published protocols' expirate collection had the same effect, and no
    fresh gas flow, dial position or patient setting in this simulator can
    produce it. Nobody running the application sees these numbers. Any
    restatement of them that drops this paragraph claims something about the
    shipped model that is not true of it.

    The table shows what is left once the apparatus is gone, beside the
    shipped condition that the module's other elimination tests measure. It
    was measured on 2026-09-07, as distance from each cohort's mean in that
    cohort's own standard deviations:

    | Agent | Cohort | Shipped | Open circuit | Published |
    | --- | --- | --- | --- | --- |
    | Sevoflurane | n=7 | +3.79 SD | 0.1541, -0.15 SD | 0.157 +/- 0.020 |
    | Isoflurane | n=7 | +4.15 SD | 0.2388, +0.66 SD | 0.223 +/- 0.024 |
    | Desflurane | n=8 | +1.13 SD | 0.0935, -2.33 SD | 0.14 +/- 0.02 |
    | Isoflurane | n=8 | +5.13 SD | 0.2388, +0.94 SD | 0.22 +/- 0.02 |

    **Three of the four cohorts land inside the published spread, and
    desflurane misses on the other side.** That is the answer the driver was
    built to find, and both halves of it are useful. For sevoflurane, and for
    isoflurane in both cohorts, the rebreathing circuit accounts for the
    whole of a gap that was 3.8 to 5.1 published SD wide. So this model's
    vessel-rich return does reproduce a human elimination once the apparatus
    difference is taken out, which nothing in this repository could show
    before. For desflurane the circuit accounts for more than the gap. The
    model crosses its published mean and settles 2.33 SD below it, washing
    out faster than the volunteers did rather than more slowly. That residual
    is a real disagreement about tissue return, and the circuit can no longer
    explain it. The next test shows what the residual is not, and
    `docs/MODEL.md` "Desflurane's residual, and why the parameter file was
    not changed" gives the whole account.

    **What is asserted here is a regression pin, not the agreement above.**
    Three rows inside the published spread is a result to state, not a
    tolerance to assert. Asserting it as a tolerance would make a later model
    change that improved desflurane and moved sevoflurane to 1.1 SD look like
    a failure. It would also let a change that moved sevoflurane from -0.15
    to +0.95 go unnoticed. So the assertion is that the driver still produces
    `OPEN_CIRCUIT_ELIMINATION_RATIOS` to within
    `ELIMINATION_RATIO_PIN_TOLERANCE`, in either direction, exactly as the
    shipped-condition comparison asserts its own measured ratios. The failure
    message recomputes the distances above, so a run that moves reports how
    far it moved and against what.
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
    """Pin the size of the apparatus term, on which this module's whole account rests.

    The module docstring, `docs/MODEL.md` and two other tests here all say
    that most of the elimination disagreement comes from the breathing system
    rather than the patient. Until this driver existed, that claim rested on a
    flow sweep. A flow sweep shows that the ratio is *sensitive* to the
    circuit, but not how much of the gap the circuit causes. Running the same
    five minutes with the circuit taken away answers that question directly.
    The table was measured on 2026-09-07, in each cohort's own standard
    deviations:

    | Agent | Cohort | Shipped | Open circuit | Moved by |
    | --- | --- | --- | --- | --- |
    | Sevoflurane | n=7 | +3.79 SD | -0.15 SD | 3.94 SD |
    | Isoflurane | n=7 | +4.15 SD | +0.66 SD | 3.49 SD |
    | Desflurane | n=8 | +1.13 SD | -2.33 SD | 3.46 SD |
    | Isoflurane | n=8 | +5.13 SD | +0.94 SD | 4.20 SD |

    The test asserts the movement rather than either endpoint, and it asserts
    a downward movement rather than merely a large one. That is the claim the
    surrounding prose makes, and the one that would have to be withdrawn if it
    stopped being true. The threshold is `MINIMUM_APPARATUS_MOVEMENT_SD`, with
    a wide margin below the smallest measured value. What a reader needs from
    this test is that the apparatus term is several times the published
    spread. The regression pins on both conditions already fix its fourth
    digit.

    Note what the table does *not* say. The movement exceeds the shipped gap
    for sevoflurane and desflurane, but not for isoflurane. So "the apparatus
    accounts for the gap" is true of three cohorts because they arrive inside
    their spread, and true of desflurane only because it overshoots. A
    summary that rounded this to "removing the circuit fixes the comparison"
    would describe desflurane backwards.
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
    """Desflurane's open-circuit residual is not a solubility the parameter file could store.

    The test above leaves desflurane 2.33 published SD *below* its cohort's
    mean once the rebreathing circuit is gone. So desflurane washes out faster
    than the volunteers did, on the opposite side from every other row. The
    module's own sensitivity table says that this ratio mainly measures the
    vessel-rich tissue:gas coefficient (+0.45 to +0.55 published SD per
    +10%). So the obvious explanation is that desflurane's vessel-rich
    coefficient is too low. This test rules that explanation out, and it is
    the reason `data/agents/desflurane.json` was not changed (`PL-73G7`).

    Raising the coefficient alone does reach the published mean. At
    lambda_(vrg:b) = 2.24, against the shipped 1.286, the ratio lands on
    0.140. The wash-in row stays inside its spread, at +0.55 SD, because the
    vessel-rich group is fully equilibrated after 30 minutes and its capacity
    barely affects F_A/F_I (measured 2026-09-08). What rules the change out
    is not this model but the tissue measurement. Solving the same way
    against each cohort's published ratio gives the coefficient each agent
    would require:

    | Agent | Demanded | Yasuda 1989 measured brain:blood | Distance |
    | --- | --- | --- | --- |
    | Sevoflurane | 1.74 | 1.70 +/- 0.09 | +0.42 SD |
    | Isoflurane | 1.45 | 1.57 +/- 0.10 | -1.24 SD |
    | Desflurane | 2.24 | 1.29 +/- 0.05 | +19 SD |

    Two of the three land on the measurement. Desflurane's required value is
    nineteen standard deviations above its own measurement, and above what
    either other agent requires. It would make desflurane the *most*
    tissue-soluble of the three, inverting the ordering that the source paper
    was written to report. So the residual cannot be this coefficient. The
    assertion below is the contrapositive. Give desflurane a vessel-rich
    coefficient that the published human tissue data support, and its
    elimination still misses on the same side. Measured 2026-09-08:

    | Coefficient given | F_A/F_A0 at 5 min | Against 0.14 +/- 0.02 |
    | --- | --- | --- |
    | 1.286, shipped | 0.0935 | -2.33 SD |
    | 1.39, its own mean + 2 SD | 0.0998 | -2.01 SD |
    | 1.70, sevoflurane's | 0.1167 | -1.17 SD |

    **The two thresholds differ because the two ceilings make different
    claims.** At desflurane's own measurement, the residual is asserted to
    exceed 1.5 SD. That still leaves 0.5 SD of margin below the measured
    2.01, and it says the published ratio is nowhere near reachable. At
    sevoflurane's coefficient, the residual is asserted only to exceed 0.75
    SD, because the measured 1.17 is genuinely close to the edge of the
    published spread. A reader should conclude that no admissible value
    reaches the published *mean*, not that the gap survives every
    conceivable value. Asserting 1.0 at both would have hidden that
    difference behind a margin of 0.17 SD.

    This test runs the diagnostic open circuit, so the caveat on every other
    use of it applies here too. No setting of the shipped simulator can
    produce the condition, and nothing here describes what a user sees.
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
    later supplied the apparatus's real volume: about 50 ml of corrugated
    Teflon between the tracheal sampling port and the nonrebreathing valve.
    This test uses that sourced figure (`PL-RFLN`).

    **The framing had to change before the number could be used.** That 50 ml
    is a series dead space. The derivation beside `APPARATUS_DEAD_SPACE_L`
    shows that in this model a series dead space lowers the alveolar
    ventilation by exactly V_D * f, and does not give a non-zero inspired
    fraction. So the run below is the open-circuit diagnostic at a reduced
    ventilation. The reduction applies to both the wash-in and the
    elimination, because the apparatus was present throughout the published
    protocol.

    The table below was measured on 2026-09-13, in each cohort's own
    published SD, for comparison with desflurane's -2.33 SD with no dead
    space at all:

    | f (/min) | V_A | Desflurane | Isoflurane n=8 | Worst wash-in |
    | --- | --- | --- | --- | --- |
    | 6 | 3.70 | -1.89 SD | +1.59 SD | -0.42 SD |
    | 8 | 3.60 | -1.73 SD | +1.82 SD | -0.63 SD |
    | 10 | 3.50 | -1.56 SD | +2.05 SD | -0.85 SD |
    | 12 | 3.40 | -1.38 SD | +2.30 SD | -1.08 SD |

    So the dead space moves desflurane the right way and accounts for between
    0.44 and 0.95 SD of the 2.33. That is about a fifth to two fifths of the
    residual, never the whole of it. Meanwhile it pushes the isoflurane cohort
    that was inside its spread at +0.94 SD out to between +1.59 and +2.30. It
    fails the way every other candidate in that section fails. It is
    **common-mode**, moving all four cohorts together, while desflurane's
    residual is differential, separating desflurane from the others. The
    companion test below asserts that second half.

    This test runs the diagnostic open circuit, so the caveat on every other
    use of it applies here too. No setting of the shipped simulator can
    produce the condition, and nothing here describes what a user sees.
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
    """Show why the published apparatus's dead space cannot be desflurane's residual.

    The test above shows that the sourced dead space never closes
    desflurane's gap. This test shows something stronger. The gap could not
    be closed *by this mechanism* even if the dead space were larger, because
    moving desflurane far enough costs the two isoflurane cohorts their
    agreement.

    The run uses the largest decrement that the wash-in comparison allows:
    50 ml at 11 breaths per minute. There sevoflurane's wash-in sits at
    -0.96 SD, and one more breath per minute takes it outside its published
    spread. That ceiling is not imposed here. It comes from the wash-in
    comparison itself, and it is why `PL-73G7` required any candidate for the
    elimination gap to be checked against the wash-in rows in the same pass.

    Measured 2026-09-13 at f = 11, V_A = 3.45 L/min:

    | Cohort | Wash-in | Elimination | Elimination with no dead space |
    | --- | --- | --- | --- |
    | Sevoflurane n=7 | -0.96 SD | +0.95 SD | -0.15 SD |
    | Isoflurane n=7 | -0.82 SD | +1.69 SD | +0.66 SD |
    | Desflurane n=8 | -0.55 SD | -1.48 SD | -2.33 SD |
    | Isoflurane n=8 | -0.64 SD | +2.17 SD | +0.94 SD |

    Desflurane is still 1.48 SD short, while both isoflurane cohorts have left
    their published spread entirely. That is the same failure that the
    alveolar ventilation row of `docs/MODEL.md`'s candidate table records.
    This is not a coincidence. A series dead space *is* a ventilation
    decrement here, so the apparatus's own volume is that same candidate, at
    a sourced magnitude rather than a fitted one.

    **One thing this test cannot decide, and it is why the item closed without
    naming a cause.** It is undetermined whether any decrement should be
    applied at all. Yasuda derived the alveolar fraction of ventilation from
    F_M = f_A * F_A + f_D * F_I. The mixing chamber that supplies F_M sits
    beyond the nonrebreathing valve, so the 50 ml that gets re-inspired never
    reaches it. So their derived f_A is (V_T - V_D_anat - V_D_app)/V_T, which
    already subtracts the apparatus. A comparison run at *their* alveolar
    ventilation must therefore not subtract it again. This model runs at 4.0
    L/min. The parameter file records that value as a convention with no
    primary source behind it, and it is neither of those quantities.
    `PL-ZDWL` tracks reading the value out of the methods text.

    This test runs the diagnostic open circuit, so the caveat on every other
    use of it applies here too. No setting of the shipped simulator can
    produce the condition, and nothing here describes what a user sees.
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
    between the two conditions and label them as one of them. A diagnostic
    can fail that way and an ordinary test cannot. Nothing else in this
    module would notice, because the ratio such a driver produces is
    plausible either way.

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
    had already fallen, and that ratio is not limited by the same bound. At
    the 10 L/min that the run keeps, the old test passed with a relative
    margin of 1.5e-4 to 4.8e-4. At lower elimination flows a correct driver
    exceeded the bound, by a factor of 1.000911 to 1.001237 at 0 L/min
    (measured 2026-10-17). So the test also runs at 0 L/min, the flow closest
    to the bound. Measured on 2026-10-17 with the starting F_A, the peak is
    0.99785 to 0.99790 of the bound at the run's own flow, and 0.99924 to
    0.99931 of it at 0 L/min. The driver is about 280 times closer to an open
    circuit than the shipped condition, which settles at 0.30 to 0.32. The
    residual is first-order in the step, so a shorter step gets
    proportionally closer.
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

    `_discard_circuit_contents()` writes to a compartment directly. Like the
    inspired-fraction clamp, it bypasses `advance()`'s own accounting.
    Zeroing the circuit and forgetting to record the agent as exhausted would
    leave the model's conservation identity short by everything the patient
    exhaled. That error would not stand out in the direction that matters,
    because agent removed from the circuit without being recorded looks
    exactly like a model that eliminates well.

    So the model's own check is read at the end of the run rather than
    trusted. It is the same `AgentSimulationValidator` that can halt a live
    simulation, and it enforces `initial + delivered = exhausted + stored`.
    On 2026-09-07 its relative error was measured at 3e-13, which is
    arithmetic rounding rather than an accounting error.
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
    """Mirror `test_elimination_is_dominated_by_the_rebreathing_circuit` in an open circuit.

    That test measures the shipped elimination moving across 11.5 to 21.6
    published standard deviations between 1 and 10 L/min. It moves because F_I
    settles at `V_A/(V_A + fresh gas flow)` of F_A, and the published ratio has
    no term to divide that out. This test runs the same sweep with the circuit
    discarded each step, over the whole supported flow range including zero.
    It finds a spread of 4e-6 published SD (2026-09-07), against the 11.5 to
    21.6 SD that the shipped condition moves over the narrower range of 1 to
    10 L/min.

    That is the strongest single piece of evidence that the driver removes the
    apparatus term rather than shrinking it. It is stronger than the residual
    bound that `test_the_open_circuit_driver_holds_the_inspired_fraction_near_zero`
    asserts. A driver that merely reduced
    rebreathing would still show the flow dependence, because the dependence
    lies in what the circuit returns, not in how much of it there is.

    Only the flow during elimination is swept. The wash-in stays at
    `FRESH_GAS_FLOW_L_MIN`, so the state that the elimination starts from is
    held fixed. That state does still depend on the flow it was loaded at, by
    0.23 to 0.32 published SD across the same range. That residual belongs to
    the initial condition rather than to the apparatus. Separating the two is
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
