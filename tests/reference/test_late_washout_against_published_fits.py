"""Measure this model's first 24 hours of elimination against the mean
five-compartment washout curves Yasuda et al. fitted to the volunteers the
five-minute gate compares against.

**This module is a measurement recorded beside a gate, and it is not a second
gate.** `test_published_wash_in_and_elimination.py` compares five minutes of
elimination against a measured human mean and refuses, in its caveat 4, to
carry that comparison into the papers' multi-day curves: over the hours this
module covers the measured washout is carried by a compartment this model does
not have, so a comparison there measures an omission rather than a parameter.
That refusal stands. What this module adds is the *size* of the omission, from
which hour and in which direction, so that a reader of the washout tail has a
number where the intertissue-diffusion note under `docs/MODEL.md` § "Known
limitations" could give only a direction (`PL-KK1Q`). Every assertion below is
a regression band around what this module itself measured, on 2026-09-27 and,
for the muscle group's variation and the open circuit's modes, on 2026-10-03;
the reading such a band supports; or a property of the published
coefficients. None asserts agreement with a human washout, and none may be
restated as one.

**What is compared.** Both papers fit each volunteer's elimination to a sum of
five exponentials, $`F_A/F_{A0} = \\sum_i A_i e^{-t/\\tau_i}`$, and publish the
mean and SD of every coefficient (Tables 1 and 2 of each, read at the source
2026-09-27: *Anesth Analg* 1991;72:316-24 p. 321 through the private corpus's
text layer, *Anesthesiology* 1991;74:489-98 pp. 494-95 as page images). The
curve built from the mean coefficients is `PublishedWashoutFit.ratio_at()`, and
it is compared as published, un-normalised: the amplitudes sum to 0.912-0.937
rather than 1 at discontinuation, since they are means of per-subject fits, and
normalising would raise every fitted value, and lower every ratio here, by 7 to
10%. The model runs the same protocol as the gate - the shipped 30-minute
wash-in at the reference operating point, `_configured_system()`'s, then the
vaporizer closed - for 24 hours, the supported run length, at the shipped
0.1 s step, sampled once a minute. Two conditions, exactly the gate's two:
*shipped*, the rebreathing circuit at 10 L/min, which is the tail the chart
draws; and *open circuit*, `_discard_circuit_contents()` after every step,
which no setting of the shipped simulator reaches and which every restatement
of its numbers owes that sentence. The stated times are the papers' own
sampling times inside the first day (*Anesth Analg* p. 317: 5, 30, 60, 120,
240, 400, 600, 800 and 1400 min among them), where the fit passes near a
measured sample rather than interpolating, plus 1440 min.

**The result, as model over fit at those times** (2026-09-27; the four cohorts
in the order sevoflurane and isoflurane from *Anesth Analg*, desflurane and
isoflurane from *Anesthesiology*):

| Minutes | Sevo, shipped | Iso, shipped | Des, shipped | Iso 2, shipped |
| ---: | ---: | ---: | ---: | ---: |
| 5 | 1.20 | 1.33 | 1.11 | 1.42 |
| 30 | 0.61 | 0.71 | 0.75 | 0.88 |
| 60 | 0.81 | 0.87 | 0.93 | 1.08 |
| 120 | 1.01 | 1.07 | 1.11 | 1.33 |
| 240 | 1.20 | 1.26 | 0.88 | 1.52 |
| 400 | 1.02 | 1.07 | 0.55 | 1.23 |
| 600 | 0.74 | 0.78 | 0.56 | 0.86 |
| 800 | 0.67 | 0.68 | 0.80 | 0.74 |
| 1400 | 1.23 | 1.11 | 2.09 | 1.15 |
| 1440 | 1.29 | 1.15 | 2.18 | 1.20 |

| Minutes | Sevo, open | Iso, open | Des, open | Iso 2, open |
| ---: | ---: | ---: | ---: | ---: |
| 5 | 0.80 | 0.98 | 0.64 | 1.05 |
| 30 | 0.43 | 0.51 | 0.53 | 0.63 |
| 60 | 0.58 | 0.64 | 0.65 | 0.79 |
| 120 | 0.70 | 0.77 | 0.76 | 0.95 |
| 240 | 0.82 | 0.85 | 0.58 | 1.04 |
| 400 | 0.67 | 0.69 | 0.36 | 0.79 |
| 600 | 0.47 | 0.48 | 0.37 | 0.53 |
| 800 | 0.43 | 0.42 | 0.54 | 0.46 |
| 1400 | 0.81 | 0.71 | 1.39 | 0.74 |
| 1440 | 0.85 | 0.74 | 1.46 | 0.77 |

**Read in three stretches, which the crossing hours mark.** In the shipped
condition the modelled tail crosses the fitted curve four times in 24 hours.
It sits above it at five minutes, which is the apparatus term the gate
records; falls below it from 6 to 13 minutes until 0.8 to 2.0 hours, by up to
15 to 44% around 15 to 25 minutes; runs above it until 3.4 hours for desflurane
and 6.9 to 8.4 hours for the other three, by 12 to 52% at the widest; runs
*below* it from there until 15.3 hours for desflurane and 20.7 to 21.8 hours
for the others, by a third at the widest (0.67, 0.68 and 0.74 at 13 to 14
hours) and by a half for desflurane (0.51 at 8 hours); and finishes above it,
by 15 to 29% at 24 hours and by a factor of 2.2 for desflurane. With the
apparatus taken away the tail runs below the fitted curve from the third
minute for the whole 24 hours in two cohorts and for most of them in the other
two, at a third to a half of it between 8 and 13 hours (0.34 to 0.46). The
middle stretch is the answer the note asked for: the fourth compartment's term
is the largest in every fitted curve from 1.8 to 3.1 hours until 20.7 to 29.4
hours (`test_the_fourth_compartment_is_the_largest_term_over_the_recorded_hours`),
this model has no such term, and over those hours its tail falls faster than
the measured mean - later than the third hour in the shipped condition,
because the rebreathing circuit and the muscle group's slow return hold it
above the curve until the seventh (with the circuit's return taken away the
same hours sit at or below it), and from the start with the apparatus gone.
The model's muscle group returns more slowly than the fitted muscle term: read
off the curve as the fitted term was, as a mode of the open-circuit system,
its term is 1.89 to 2.02 times as slow and 0.51 to 0.73 times as large
(`test_the_model_s_apparent_muscle_and_fat_terms_against_the_fitted_ones`).
That is what puts the peak of model over fit in hours 2 to 4: with the
group's coefficient lowered until its isolated time constant is the fitted
one's, which brings the apparent one to 1.09 to 1.28 times it, six-hour runs
peak before the second hour in both conditions and every cohort, and the tail
at four hours is 24 to 60% lower
(`test_the_muscle_group_s_slow_return_places_the_tail_s_rise_in_hours_2_to_4`;
`docs/MODEL.md` has the numbers). The late excess is the model's fat term,
1.5 to 2.1 times the fitted fat term's small amplitude (0.028 to 0.080%, with
SDs of 53 to 94% of the means), and it is still growing at 24 hours - the
ratio rises between minutes 1400 and 1440 in every cohort - because the
fitted curve is still falling on the fourth compartment's time constant while
the model is already on its fat term's, 1.14 to 1.36 times every fitted fat
time constant.

**Three things bound how sharply any of that may be read.**

1. *The fitted mean curve is not the measured mean, and where it can be
   checked it runs high.* At five minutes, the one time both exist, the mean
   coefficients give 0.194, 0.243, 0.147 and 0.228 against the measured
   0.157 ± 0.020, 0.223 ± 0.024, 0.14 ± 0.02 and 0.22 ± 0.02: above by 1.84,
   0.83, 0.33 and 0.39 published SD, or 3.5 to 24%
   (`test_the_fitted_mean_curves_run_above_their_own_measured_five_minute_means`).
   A sum of exponentials built from mean coefficients over-states the mean of
   the subjects' curves wherever a time constant varies between subjects, and
   every one of these does, with SDs of 10 to 52% of the means. So every ratio
   above is, to an extent that is 3.5 to 24% at the one point it can be
   measured, an understatement of the model against the volunteers' mean: for
   sevoflurane the open-circuit model sits 0.15 SD below the measured
   five-minute mean and 20% below the fitted curve at the same instant, and
   the whole of that 20% is the fit's own. Nothing here corrects for it,
   because no measured mean exists at the later times to correct against;
   both papers plot them (Figures 3 and 4), on logarithmic axes no number is
   taken from.
2. *The term that carries the measured curve over the middle stretch is as
   uncertain between subjects as it is large.* The fourth compartment's
   amplitude is 0.717 ± 0.800, 1.296 ± 1.237, 0.775 ± 0.482 and 1.125 ± 0.669
   (×100), SDs of 59 to 112% of the means, so a tail a third to a half below
   the mean curve over those hours is inside the spread of the volunteers'
   own curves. The direction and the mechanism are settled - the model has no
   term there and the open-circuit driver puts its tissue return alone at a
   third to a half of the mean - and the size is known to about a factor of
   two and no better.
3. *The published subjects breathed nitrous oxide throughout, and the
   parameters under test descend from the lineage of the data* - caveats 1
   and 2 of the gate, which apply here unchanged.

**How much of the gap sevoflurane's missing metabolism could account for:
little, and in the wrong direction over the middle stretch.** This model has
no metabolism; a human has, and for sevoflurane it is 2 to 5% of the absorbed
dose (Kharasch 1995, cited under `docs/MODEL.md` § "Supported run length").
`_metabolise()` below is a test-only first-order sink on the vessel-rich
group, sited where the papers' own mammillary model sites hepatic elimination
(*Anesth Analg* p. 318, "the second compartment (vessel-rich group; k20)"),
run at that paper's fitted sevoflurane rate constant, k20 = 0.0094 min⁻¹
(Table 3, p. 321; SD 0.0171, so the cohort could not tell it from zero). In
this model it removes 7.8% of the 30-minute uptake by 24 hours in the shipped
condition and 7.2% in the open circuit - above Kharasch's range, which makes
it a bound. It lowers the shipped tail by 4.5% at five minutes and by 1.9 to
2.9% from 30 minutes on, the open tail by 5.0% and then 1.3 to 1.8%
(`test_sevoflurane_s_missing_metabolism_moves_the_tail_by_a_few_percent`).
So where the shipped model runs above the fitted curve, metabolism could
account for about an eighth of the excess where it is widest - 2.8 of the
20.4 points at four hours, 3.1 of the 28.6 at 24 - and where it runs below,
metabolism widens the gap by the same few percent. The reason is where the sink looks: hepatic
clearance sees the arterial partial pressure, which through the tail is the
alveolar one, and never the stores that feed it.

**What a learner sees of it.** The departures above are in $`F_A/F_{A0}`$,
and at the gate's 1% dial $`F_{A0}`$ is 0.805, 0.672 and 0.876% of an
atmosphere for sevoflurane, isoflurane and desflurane, so the shipped
alveolar trace falls below the readout's 0.01 percentage points
(`docs/MODEL.md` § "Displayed precision") at 2.8, 4.2 and 1.9 hours, before
the stretch over which it runs below the measured mean, and on the chart's
linear axis, fixed at 3 MAC, it is a few pixels high well before that. A
higher dial scales $`F_{A0}`$ with it and keeps the trace above the floor for
longer - a 6% desflurane dial until about the fifth hour, inside its stretch.

**Sources**, none the authority for a stored value: the two Yasuda papers the
gate's docstring cites in full, read again at the source 2026-09-27 for the
coefficients, their SDs, the sampling schedule (*Anesth Analg* p. 317), the
hybrid and mammillary methods (p. 318) and Table 3 of each (pp. 321 and 495);
and Kharasch ED, *Biotransformation of sevoflurane*, Anesth Analg
1995;81(6 Suppl):S27-38, PMID 7486145, for the 2 to 5%.
"""

from __future__ import annotations

import cmath
import math
import pickle
from collections.abc import Callable
from dataclasses import dataclass, replace
from functools import cache
from typing import Literal

import numpy
import pytest
from test_published_wash_in_and_elimination import (
    MODELLED_ELIMINATION_RATIOS,
    OPEN_CIRCUIT_ELIMINATION_RATIOS,
    PUBLISHED_MEASUREMENTS,
    SIMULATION_STEP_S,
    WASH_IN_DURATION_S,
    PublishedMeasurement,
    _configured_system,
    _discard_circuit_contents,
)

from anesthesia_sim.core.agent_simulation_validation import AgentSimulationValidationResult
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.units import MINUTES_PER_HOUR, SECONDS_PER_MINUTE
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

try:
    import fcntl
except ImportError:  # Windows, where `washout_curve` shares nothing between workers
    fcntl = None

# The supported run length, in the minutes the published coefficients are
# stated in. A run of exactly this length is what `docs/MODEL.md` § "Supported
# run length" argues for, so the measurement ends where the claim does.
ELIMINATION_DURATION_MIN = 1440

# How long a run that varies the muscle group's coefficient eliminates for.
# Six hours holds the stretch the variation asks about, hours 2 to 4, and the
# fall after it, in both conditions and every cohort; the whole day would cost
# four times the steps and read nothing more about that stretch.
MUSCLE_VARIATION_DURATION_MIN = 360

# Once a minute is fine enough to place a crossing to the tenth of an hour
# and coarse enough to keep 24 hours of samples small; every step in between
# is still the shipped 0.1 s, so nothing about the model is coarsened.
SAMPLE_INTERVAL_S = 60.0
STEPS_PER_SAMPLE = round(SAMPLE_INTERVAL_S / SIMULATION_STEP_S)

# The papers' own sampling times inside the first day (*Anesth Analg* p. 317),
# so the fitted curve is read where a measured sample constrained it rather
# than between samples, with 1440 min added for the run-length boundary. The
# 5-minute entry is the gate's own point and ties this module to it.
STATED_MINUTES = (5, 30, 60, 120, 240, 400, 600, 800, 1400, 1440)

# Yasuda et al.'s fitted rate constant for hepatic elimination of sevoflurane
# from the vessel-rich group, k20, mean 0.0094 ± 0.0171 min⁻¹ (*Anesth Analg*
# Table 3, p. 321). Read into `_metabolise()` as the size of the sink, and
# checked against Kharasch's range through the share of uptake it removes.
HEPATIC_ELIMINATION_RATE_CONSTANT_PER_MIN = 0.0094

# The upper end of the 2 to 5% of absorbed sevoflurane Kharasch 1995 finds
# metabolized. The sink above removes more than this in this model, which is
# what lets its effect on the tail be read as a bound.
KHARASCH_UPPER_METABOLISED_SHARE = 0.05

Condition = Literal["shipped", "open circuit"]
CONDITIONS: tuple[Condition, ...] = ("shipped", "open circuit")

# Regression bands around this module's own measurements, not agreement
# claims. One percent of the ratio, and a tenth of an hour on a crossing
# placed to the minute: a parameter change that moves the tail by more fails
# and has to be re-measured here and in `docs/MODEL.md`, never absorbed by
# widening the band.
RATIO_REGRESSION_TOLERANCE = 0.01
CROSSING_TOLERANCE_H = 0.1
METABOLISED_SHARE_TOLERANCE = 0.002
TAIL_REDUCTION_TOLERANCE = 0.003


@dataclass(frozen=True, slots=True)
class PublishedWashoutFit:
    """One cohort's mean five-compartment hybrid washout, as published.

    Attributes:
        amplitudes_percent: $`A_i \\times 100`$, Table 1 of the source, in the
            compartment order the papers give - lungs, vessel-rich group,
            muscle group, fourth compartment, fat group.
        amplitude_sds_percent: the SDs printed beside them, mean ± SD.
        time_constants_min: $`\\tau_i`$ in minutes, Table 2 of the source.
        time_constant_sds_min: the SDs printed beside those.
    """

    agent_id: str
    source: str
    cohort_size: int
    amplitudes_percent: tuple[float, float, float, float, float]
    amplitude_sds_percent: tuple[float, float, float, float, float]
    time_constants_min: tuple[float, float, float, float, float]
    time_constant_sds_min: tuple[float, float, float, float, float]

    @property
    def label(self) -> str:
        return f"{self.agent_id}/{self.source}"

    @property
    def value_at_discontinuation(self) -> float:
        """The fitted curve at t = 0, which is below 1 for every cohort."""

        return sum(self.amplitudes_percent) / 100.0

    def term_at(self, index: int, minutes: float) -> float:
        """One compartment's exponential, as a fraction of F_A0."""

        return (
            self.amplitudes_percent[index]
            / 100.0
            * math.exp(-minutes / self.time_constants_min[index])
        )

    def ratio_at(self, minutes: float) -> float:
        """F_A/F_A0 on the published mean coefficients, un-normalised."""

        return sum(self.term_at(index, minutes) for index in range(5))

    def leading_term_at(self, minutes: float) -> int:
        """The index of the largest of the five terms at one instant."""

        return max(range(5), key=lambda index: self.term_at(index, minutes))

    def hours_at_which_terms_are_equal(self, first: int, second: int) -> float:
        """When two terms cross: ln(A_i/A_j) / (1/tau_i - 1/tau_j), in hours.

        The same arithmetic the intertissue-diffusion note under
        `docs/MODEL.md` § "Known limitations" was computed by, so the hours it
        prints are held here rather than re-derived by hand.
        """

        amplitude_ratio = self.amplitudes_percent[first] / self.amplitudes_percent[second]
        rate_difference = (
            1.0 / self.time_constants_min[first] - 1.0 / self.time_constants_min[second]
        )
        return math.log(amplitude_ratio) / rate_difference / MINUTES_PER_HOUR

    @property
    def measurement(self) -> PublishedMeasurement:
        """The gate's row for the same volunteers, for the five-minute check."""

        (row,) = [
            m
            for m in PUBLISHED_MEASUREMENTS
            if m.agent_id == self.agent_id and m.source == self.source
        ]
        return row


PUBLISHED_FITS = (
    PublishedWashoutFit(
        agent_id="sevoflurane",
        source="Anesth Analg 1991;72:316-24",
        cohort_size=7,
        amplitudes_percent=(63.6, 24.7, 4.60, 0.717, 0.028),
        amplitude_sds_percent=(2.9, 3.5, 3.14, 0.800, 0.018),
        time_constants_min=(0.46, 9.17, 81.7, 437, 2230),
        time_constant_sds_min=(0.08, 4.08, 42.6, 163, 730),
    ),
    PublishedWashoutFit(
        agent_id="isoflurane",
        source="Anesth Analg 1991;72:316-24",
        cohort_size=7,
        amplitudes_percent=(55.7, 26.9, 7.19, 1.296, 0.072),
        amplitude_sds_percent=(3.1, 4.0, 4.04, 1.237, 0.044),
        time_constants_min=(0.39, 9.80, 85.0, 474, 2310),
        time_constant_sds_min=(0.09, 4.31, 42.1, 162, 930),
    ),
    PublishedWashoutFit(
        agent_id="desflurane",
        source="Anesthesiology 1991;74:489-98",
        cohort_size=8,
        amplitudes_percent=(64.4, 22.5, 4.86, 0.775, 0.031),
        amplitude_sds_percent=(4.8, 3.8, 1.92, 0.482, 0.029),
        time_constants_min=(0.441, 5.78, 48.9, 300, 1350),
        time_constant_sds_min=(0.042, 1.64, 21.7, 107, 230),
    ),
    PublishedWashoutFit(
        agent_id="isoflurane",
        source="Anesthesiology 1991;74:489-98",
        cohort_size=8,
        amplitudes_percent=(57.2, 28.4, 5.93, 1.125, 0.080),
        amplitude_sds_percent=(3.6, 3.4, 2.09, 0.669, 0.042),
        time_constants_min=(0.380, 8.72, 80.0, 482, 2110),
        time_constant_sds_min=(0.058, 2.12, 26.0, 127, 320),
    ),
)

AGENT_IDS = ("sevoflurane", "isoflurane", "desflurane")

# The compartment order the papers give, as indices into the tuples above.
MUSCLE_GROUP, FOURTH_COMPARTMENT, FAT_GROUP = 2, 3, 4


@dataclass(frozen=True, slots=True)
class RecordedComparison:
    """What this module measured for one cohort in one condition, 2026-09-27.

    Attributes:
        ratios: model over fit at each of `STATED_MINUTES`.
        crossing_hours: every hour at which model over fit passed through 1
            between one minute's sample and the next, from the second minute
            on, to the resolution of the sampling.
    """

    ratios: tuple[float, ...]
    crossing_hours: tuple[float, ...]


# Model outputs, not published values, and kept apart from `PUBLISHED_FITS`
# for the reason the gate keeps its modelled ratios out of its published rows:
# a measured number sitting among published ones is how a later reader comes
# to cite a model output as a human measurement.
RECORDED_COMPARISONS: dict[tuple[str, Condition], RecordedComparison] = {
    ("sevoflurane/Anesth Analg 1991;72:316-24", "shipped"): RecordedComparison(
        ratios=(1.201, 0.610, 0.808, 1.006, 1.204, 1.023, 0.737, 0.667, 1.225, 1.286),
        crossing_hours=(0.13, 1.98, 6.88, 20.65),
    ),
    ("sevoflurane/Anesth Analg 1991;72:316-24", "open circuit"): RecordedComparison(
        ratios=(0.795, 0.426, 0.576, 0.704, 0.815, 0.666, 0.468, 0.427, 0.806, 0.846),
        crossing_hours=(0.05,),
    ),
    ("isoflurane/Anesth Analg 1991;72:316-24", "shipped"): RecordedComparison(
        ratios=(1.329, 0.708, 0.872, 1.070, 1.255, 1.070, 0.777, 0.684, 1.106, 1.154),
        crossing_hours=(0.17, 1.62, 7.33, 21.78),
    ),
    ("isoflurane/Anesth Analg 1991;72:316-24", "open circuit"): RecordedComparison(
        ratios=(0.983, 0.509, 0.641, 0.766, 0.854, 0.686, 0.478, 0.423, 0.710, 0.742),
        crossing_hours=(0.08,),
    ),
    ("desflurane/Anesthesiology 1991;74:489-98", "shipped"): RecordedComparison(
        ratios=(1.109, 0.753, 0.927, 1.111, 0.881, 0.547, 0.562, 0.800, 2.086, 2.180),
        crossing_hours=(0.10, 1.30, 3.38, 15.30),
    ),
    ("desflurane/Anesthesiology 1991;74:489-98", "open circuit"): RecordedComparison(
        ratios=(0.638, 0.530, 0.647, 0.760, 0.582, 0.356, 0.373, 0.536, 1.394, 1.457),
        crossing_hours=(0.03, 19.18),
    ),
    ("isoflurane/Anesthesiology 1991;74:489-98", "shipped"): RecordedComparison(
        ratios=(1.417, 0.879, 1.077, 1.329, 1.521, 1.225, 0.857, 0.741, 1.150, 1.197),
        crossing_hours=(0.22, 0.78, 8.42, 21.05),
    ),
    ("isoflurane/Anesthesiology 1991;74:489-98", "open circuit"): RecordedComparison(
        ratios=(1.049, 0.632, 0.792, 0.952, 1.035, 0.785, 0.527, 0.457, 0.738, 0.769),
        crossing_hours=(0.10, 2.45, 4.58),
    ),
}

# The hours the intertissue-diffusion note prints for the fourth compartment's
# lead, re-derived here from the coefficients: when its term overtakes the
# muscle group's, and when the fat group's overtakes it.
RECORDED_FOURTH_COMPARTMENT_LEAD_H: dict[str, tuple[float, float]] = {
    "sevoflurane/Anesth Analg 1991;72:316-24": (3.11, 29.38),
    "isoflurane/Anesth Analg 1991;72:316-24": (2.96, 28.73),
    "desflurane/Anesthesiology 1991;74:489-98": (1.79, 20.69),
    "isoflurane/Anesthesiology 1991;74:489-98": (2.66, 27.52),
}

# How far each fitted curve sits above the measured five-minute mean of the
# same cohort, in that cohort's published SD.
RECORDED_FIT_ABOVE_MEASUREMENT_AT_FIVE_MINUTES_SD: dict[str, float] = {
    "sevoflurane/Anesth Analg 1991;72:316-24": 1.84,
    "isoflurane/Anesth Analg 1991;72:316-24": 0.83,
    "desflurane/Anesthesiology 1991;74:489-98": 0.33,
    "isoflurane/Anesthesiology 1991;74:489-98": 0.39,
}
FIVE_MINUTE_DISTANCE_TOLERANCE_SD = 0.02

# The hepatic sink's outputs for sevoflurane: the share of the 30-minute
# uptake it removes by 24 hours, and how far it lowers F_A/F_A0 at each of
# `STATED_MINUTES` against the same run without it.
RECORDED_METABOLISED_SHARE: dict[Condition, float] = {"shipped": 0.0780, "open circuit": 0.0715}
RECORDED_TAIL_REDUCTIONS: dict[Condition, tuple[float, ...]] = {
    "shipped": (0.0447, 0.0286, 0.0194, 0.0206, 0.0229, 0.0255, 0.0269, 0.0263, 0.0241, 0.0240),
    "open circuit": (
        0.0502,
        0.0177,
        0.0133,
        0.0140,
        0.0153,
        0.0168,
        0.0174,
        0.0168,
        0.0155,
        0.0155,
    ),
}


@dataclass(frozen=True, slots=True)
class RecordedMuscleVariation:
    """What a muscle group at the fitted time constant did, for one cohort in one condition.

    Attributes:
        rise_as_stored: where model over fit peaks after its early dip on the
            stored coefficient, as (hours, ratio), read from the 24-hour run.
        rise_at_fitted_time_constant: the same peak with the muscle group's
            coefficient lowered until its isolated time constant is the fitted
            muscle term's.
        ratio_at_four_hours_at_fitted_time_constant: model over fit at 240 min
            with that coefficient; the stored one's is in `RECORDED_COMPARISONS`.
        crossing_hours_at_fitted_time_constant: as `RecordedComparison`'s,
            over the six hours the varied run lasts.
    """

    rise_as_stored: tuple[float, float]
    rise_at_fitted_time_constant: tuple[float, float]
    ratio_at_four_hours_at_fitted_time_constant: float
    crossing_hours_at_fitted_time_constant: tuple[float, ...]


# Measured 2026-10-03 (`PL-95NW`). Model outputs, kept apart from
# `PUBLISHED_FITS` for the reason `RECORDED_COMPARISONS` is.
RECORDED_MUSCLE_VARIATIONS: dict[tuple[str, Condition], RecordedMuscleVariation] = {
    ("sevoflurane/Anesth Analg 1991;72:316-24", "shipped"): RecordedMuscleVariation(
        rise_as_stored=(4.15, 1.205),
        rise_at_fitted_time_constant=(1.28, 1.005),
        ratio_at_four_hours_at_fitted_time_constant=0.770,
        crossing_hours_at_fitted_time_constant=(0.15, 1.07, 1.60),
    ),
    ("sevoflurane/Anesth Analg 1991;72:316-24", "open circuit"): RecordedMuscleVariation(
        rise_as_stored=(3.92, 0.815),
        rise_at_fitted_time_constant=(1.13, 0.700),
        ratio_at_four_hours_at_fitted_time_constant=0.497,
        crossing_hours_at_fitted_time_constant=(0.07,),
    ),
    ("isoflurane/Anesth Analg 1991;72:316-24", "shipped"): RecordedMuscleVariation(
        rise_as_stored=(4.08, 1.255),
        rise_at_fitted_time_constant=(1.97, 1.101),
        ratio_at_four_hours_at_fitted_time_constant=0.959,
        crossing_hours_at_fitted_time_constant=(0.22, 0.73, 3.65),
    ),
    ("isoflurane/Anesth Analg 1991;72:316-24", "open circuit"): RecordedMuscleVariation(
        rise_as_stored=(3.72, 0.856),
        rise_at_fitted_time_constant=(1.45, 0.775),
        ratio_at_four_hours_at_fitted_time_constant=0.619,
        crossing_hours_at_fitted_time_constant=(0.10,),
    ),
    ("desflurane/Anesthesiology 1991;74:489-98", "shipped"): RecordedMuscleVariation(
        rise_as_stored=(2.27, 1.120),
        rise_at_fitted_time_constant=(0.65, 0.960),
        ratio_at_four_hours_at_fitted_time_constant=0.367,
        crossing_hours_at_fitted_time_constant=(0.13,),
    ),
    ("desflurane/Anesthesiology 1991;74:489-98", "open circuit"): RecordedMuscleVariation(
        rise_as_stored=(2.17, 0.762),
        rise_at_fitted_time_constant=(0.62, 0.662),
        ratio_at_four_hours_at_fitted_time_constant=0.236,
        crossing_hours_at_fitted_time_constant=(0.05,),
    ),
    ("isoflurane/Anesthesiology 1991;74:489-98", "shipped"): RecordedMuscleVariation(
        rise_as_stored=(3.78, 1.524),
        rise_at_fitted_time_constant=(1.65, 1.363),
        ratio_at_four_hours_at_fitted_time_constant=1.092,
        crossing_hours_at_fitted_time_constant=(4.48,),
    ),
    ("isoflurane/Anesthesiology 1991;74:489-98", "open circuit"): RecordedMuscleVariation(
        rise_as_stored=(3.47, 1.047),
        rise_at_fitted_time_constant=(1.23, 0.966),
        ratio_at_four_hours_at_fitted_time_constant=0.698,
        crossing_hours_at_fitted_time_constant=(0.12,),
    ),
}

# The coefficient that gives each cohort's fitted muscle time constant, as a
# share of the stored one, which is the fitted constant over the stored
# isolated one; and what the muscle group then holds at discontinuation, as a
# share of what it holds on the stored coefficient.
RECORDED_MUSCLE_COEFFICIENT_SHARES: dict[str, float] = {
    "sevoflurane/Anesth Analg 1991;72:316-24": 0.6035,
    "isoflurane/Anesth Analg 1991;72:316-24": 0.6697,
    "desflurane/Anesthesiology 1991;74:489-98": 0.5775,
    "isoflurane/Anesthesiology 1991;74:489-98": 0.6303,
}
RECORDED_MUSCLE_STORE_SHARES: dict[str, float] = {
    "sevoflurane/Anesth Analg 1991;72:316-24": 0.9462,
    "isoflurane/Anesth Analg 1991;72:316-24": 0.9609,
    "desflurane/Anesthesiology 1991;74:489-98": 0.9039,
    "isoflurane/Anesthesiology 1991;74:489-98": 0.9537,
}
MUSCLE_STORE_SHARE_TOLERANCE = 0.002

# The fourth hour: one of the papers' own sampling times, and the end of the
# stretch the reading about the muscle group names.
FOUR_HOURS_MIN = 240

# The states `_open_circuit_system_per_min()` writes an equation for, in its
# order, which is also the order of `WashoutCurve.fractions_at_discontinuation`.
OPEN_CIRCUIT_STATES = ("alveolar", "mixed venous", "vessel-rich group", "muscle group", "fat group")

# How closely the open circuit's modes reproduce the stepped open-circuit run,
# as a share of the run, at every minute from `RECONSTRUCTION_FROM_MINUTE` on.
# What separates them is the driver's: `_discard_circuit_contents()` empties
# the circuit after each 0.1 s step, so within a step the patient re-breathes
# a little of what it exhaled, and the stepped run lies above the modes by up
# to 0.08%. Halving the step halved that, 0.052 to 0.026% at five minutes and
# 0.061 to 0.030% at four hours for sevoflurane (measured once, 2026-10-03,
# `PL-921Y`). Before the fifth minute the fast terms carry the curve, and the
# stepped run departs from them by up to 1.6%, at the first.
MODE_RECONSTRUCTION_TOLERANCE = 0.0008
RECONSTRUCTION_FROM_MINUTE = 5

# A band around values the stored parameters fix exactly: eigenvalues of a
# matrix built from them and a decomposition of one stepped state, rather than
# a stepped run's samples, so it can be tighter than the curve's 1% and still
# hold every value `docs/MODEL.md` prints from them at three figures.
APPARENT_TERM_TOLERANCE = 0.002


@dataclass(frozen=True, slots=True)
class RecordedApparentTerms:
    """One agent's muscle and fat terms as its open-circuit modes give them.

    The model's curve is the same for both isoflurane cohorts, so these are
    per agent; what differs between those cohorts is the fit.

    Attributes:
        muscle_time_constant_min: the muscle group's mode's time constant, the
            apparent one, read off the curve as the fitted one was.
        muscle_amplitude_percent: that mode's amplitude, $`A \\times 100`$ of
            F_A0, the papers' unit.
        fat_time_constant_min: the fat group's mode's time constant.
        fat_amplitude_percent: that mode's amplitude, as above.
        isolated_muscle_time_constant_min: the muscle group's time constant
            with nothing returned to it in arterial blood, the arithmetic
            `docs/MODEL.md` compared with the fitted one before `PL-921Y`.
        isolated_fat_time_constant_min: the same for the fat group.
    """

    muscle_time_constant_min: float
    muscle_amplitude_percent: float
    fat_time_constant_min: float
    fat_amplitude_percent: float
    isolated_muscle_time_constant_min: float
    isolated_fat_time_constant_min: float


# Measured 2026-10-03 (`PL-921Y`). Model outputs, kept apart from
# `PUBLISHED_FITS` for the reason `RECORDED_COMPARISONS` is.
RECORDED_APPARENT_TERMS: dict[str, RecordedApparentTerms] = {
    "sevoflurane": RecordedApparentTerms(
        muscle_time_constant_min=154.5,
        muscle_amplitude_percent=2.37,
        fat_time_constant_min=2653,
        fat_amplitude_percent=0.05968,
        isolated_muscle_time_constant_min=135.4,
        isolated_fat_time_constant_min=2528,
    ),
    "isoflurane": RecordedApparentTerms(
        muscle_time_constant_min=161.4,
        muscle_amplitude_percent=4.307,
        fat_time_constant_min=2860,
        fat_amplitude_percent=0.1225,
        isolated_muscle_time_constant_min=126.9,
        isolated_fat_time_constant_min=2603,
    ),
    "desflurane": RecordedApparentTerms(
        muscle_time_constant_min=92.58,
        muscle_amplitude_percent=2.466,
        fat_time_constant_min=1543,
        fat_amplitude_percent=0.06308,
        isolated_muscle_time_constant_min=84.68,
        isolated_fat_time_constant_min=1496,
    ),
}

# The muscle group's apparent time constant with the coefficient
# `test_the_muscle_group_s_slow_return_places_the_tail_s_rise_in_hours_2_to_4`
# runs, which makes the isolated one the fitted one's.
RECORDED_APPARENT_MUSCLE_TIME_CONSTANTS_AT_FITTED_ISOLATED_MIN: dict[str, float] = {
    "sevoflurane/Anesth Analg 1991;72:316-24": 93.40,
    "isoflurane/Anesth Analg 1991;72:316-24": 108.4,
    "desflurane/Anesthesiology 1991;74:489-98": 53.53,
    "isoflurane/Anesthesiology 1991;74:489-98": 102.1,
}


@dataclass(frozen=True, slots=True)
class WashoutCurve:
    """One elimination, sampled once a minute: 24 hours unless a run is shorter.

    A value object rather than the system, for the reason the gate's readings
    are: `_washout_curve()` is cached, and a returned system would be a shared
    mutable one. It is also what `washout_curve` hands from one xdist worker to
    another, as a pickle.

    Attributes:
        muscle_tissue_gas_partition_coefficient: the coefficient the run gave
            the muscle group in place of the stored one, `None` for the stored.
        alveolar_fraction_at_discontinuation: F_A0, the papers' own denominator.
        fractions_at_discontinuation: the alveolar, mixed venous and three
            tissue groups' partial-pressure fractions at discontinuation, in
            `OPEN_CIRCUIT_STATES`' order: the state `_open_circuit_modes()`
            decomposes the open circuit's elimination from.
        ratios_by_minute: F_A/F_A0 at each whole minute of elimination, index
            0 being discontinuation itself, so `ratios_by_minute[5]` is the
            gate's five-minute point.
        agent_taken_up_l: what the patient held at discontinuation plus what
            the sink had already removed, which is the uptake over the
            administration; the share below is taken of this.
        muscle_agent_at_discontinuation_l: what the muscle group alone held at
            discontinuation, the store its return draws on.
        agent_metabolised_l: the sink's total by the end of the run, zero
            without one.
        agent_accounting: the model's own conservation check at the end of
            the run, carried out so a failure can name the totals.
    """

    agent_id: str
    condition: Condition
    hepatic_elimination_rate_constant_per_min: float
    muscle_tissue_gas_partition_coefficient: float | None
    alveolar_fraction_at_discontinuation: float
    fractions_at_discontinuation: tuple[float, float, float, float, float]
    ratios_by_minute: tuple[float, ...]
    agent_taken_up_l: float
    muscle_agent_at_discontinuation_l: float
    agent_metabolised_l: float
    agent_accounting: AgentSimulationValidationResult

    def ratio_at(self, minutes: int) -> float:
        return self.ratios_by_minute[minutes]

    @property
    def metabolised_share_of_uptake(self) -> float:
        return self.agent_metabolised_l / self.agent_taken_up_l


@dataclass(frozen=True, slots=True)
class OpenCircuitModes:
    """The open circuit's F_A/F_A0 as the sum of its system's exponential modes.

    $`F_A/F_{A0} = \\sum_k A_k e^{-t/\\tau_k}`$ holds exactly for the five
    equations `_open_circuit_system_per_min()` writes out, from the state the
    modes were decomposed from: the form Yasuda et al. fitted to each
    volunteer's curve, read off the model's rather than fitted to it, so a
    mode's time constant is an apparent one, as a fitted one is. Sevoflurane's
    and isoflurane's two fastest modes are a complex-conjugate pair, a damped
    oscillation that falls e-fold in about a quarter of a minute, so a time
    constant and an amplitude are complex in general; the pair's imaginary
    parts cancel in the sum, and the three slower modes are real.

    Attributes:
        time_constants_min: $`\\tau_k`$, fastest first.
        amplitudes: $`A_k`$ as fractions of F_A0, in the same order. They sum
            to 1, since the decomposition is of the state itself.
        dominant_states: for each mode, the state in `OPEN_CIRCUIT_STATES` its
            part of the state at discontinuation is largest in, which is what
            names a mode for a compartment.
    """

    time_constants_min: tuple[complex, ...]
    amplitudes: tuple[complex, ...]
    dominant_states: tuple[str, ...]

    def ratio_at(self, minutes: float) -> float:
        """F_A/F_A0 at one instant, the real part of the modes' sum."""

        total = sum(
            amplitude * cmath.exp(-minutes / time_constant)
            for amplitude, time_constant in zip(
                self.amplitudes, self.time_constants_min, strict=True
            )
        )
        return total.real


def _metabolise(system: AgentUptakeSystem, rate_constant_per_min: float) -> float:
    """Remove one step's first-order hepatic loss from the vessel-rich group.

    **A test-only sink; no setting of the shipped simulator reaches it, and
    `docs/MODEL.md` § "Known limitations" records that the model has no
    metabolism.** It is sited on the vessel-rich group because that is where
    the papers' own mammillary model sites hepatic elimination - "the second
    compartment (vessel-rich group; k20)", *Anesth Analg* p. 318 - and the
    liver is a vessel-rich organ in this model's lumping. Applied after each
    step, it is an operator split: the loss over the step is taken at the
    end of it rather than inside the propagator, an error second order in
    the rate times the step, which is 1.6 × 10⁻⁵ here.

    The removed agent goes through `record_external_agent_transfer()` as
    exhausted, because the validator has no column for a metabolic loss and
    agent removed and recorded nowhere reads as agent the model lost, which
    halts the next `advance()` (the same identity `_discard_circuit_contents()`
    honours). So the exhausted total of a run with this sink includes what it
    metabolised; the curve keeps its own metabolised total apart.
    """

    vessel_rich = system.patient.vessel_rich
    before = vessel_rich.agent_amount_l
    vessel_rich.set_partial_pressure_fraction(
        vessel_rich.partial_pressure_fraction
        * math.exp(-rate_constant_per_min * SIMULATION_STEP_S / SECONDS_PER_MINUTE)
    )
    removed = before - vessel_rich.agent_amount_l
    system.agent_simulation_validator.record_external_agent_transfer(
        delivered_agent_l=0.0, exhausted_agent_l=removed
    )
    return removed


@cache
def _washout_curve(
    agent_id: str,
    condition: Condition,
    hepatic_elimination_rate_constant_per_min: float = 0.0,
    muscle_tissue_gas_partition_coefficient: float | None = None,
    elimination_duration_min: int = ELIMINATION_DURATION_MIN,
) -> WashoutCurve:
    """Wash in as the gate does, then eliminate in one condition, for 24 hours by default.

    The wash-in is the shipped one whatever the condition, rebreathing and
    all, because that limb is inside the published spread at every supported
    flow and F_A0 is defined at the end of it; the open circuit begins at
    discontinuation, exactly as `_eliminate_without_rebreathing()` begins it.
    With no sink the sequence of `advance()` calls is the gate's own through
    the fifth minute, which
    `test_the_twenty_four_hour_run_opens_from_the_five_minute_gate_s_own_ratio`
    holds it to. With one, the sink runs through the administration as well,
    since a human's does.

    `muscle_tissue_gas_partition_coefficient` is a coefficient the data files
    do not hold, for the one question that needs it: whether the muscle
    group's slow return is what fills hours 2 to 4 (`PL-95NW`). It is applied
    as `_configured_system()` applies its own override, before any step, where
    the group's stored amount is zero and no propagator has been built, and
    through `dataclasses.replace` so that `TissueGroup.__post_init__` validates
    it exactly as it validates a shipped one. The group's blood flow, already
    set from the cardiac output, is carried over unchanged.
    """

    system = _configured_system(agent_id)
    if muscle_tissue_gas_partition_coefficient is not None:
        system.patient.muscle = replace(
            system.patient.muscle,
            tissue_gas_partition_coefficient=muscle_tissue_gas_partition_coefficient,
        )
    metabolised = 0.0

    for _ in range(round(WASH_IN_DURATION_S / SIMULATION_STEP_S)):
        system.advance(SIMULATION_STEP_S)
        if hepatic_elimination_rate_constant_per_min:
            metabolised += _metabolise(system, hepatic_elimination_rate_constant_per_min)

    alveolar_fraction_at_discontinuation = system.alveoli.partial_pressure_fraction
    fractions_at_discontinuation = (
        alveolar_fraction_at_discontinuation,
        system.patient.mixed_venous_partial_pressure_fraction,
        system.patient.vessel_rich.partial_pressure_fraction,
        system.patient.muscle.partial_pressure_fraction,
        system.patient.fat.partial_pressure_fraction,
    )
    agent_taken_up_l = system.patient.total_agent_amount_l + metabolised
    muscle_agent_at_discontinuation_l = system.patient.muscle.agent_amount_l

    system.set_delivered_concentration_percent(0.0)
    if condition == "open circuit":
        _discard_circuit_contents(system)

    ratios = [1.0]
    for _ in range(elimination_duration_min):
        for _ in range(STEPS_PER_SAMPLE):
            system.advance(SIMULATION_STEP_S)
            if condition == "open circuit":
                _discard_circuit_contents(system)
            if hepatic_elimination_rate_constant_per_min:
                metabolised += _metabolise(system, hepatic_elimination_rate_constant_per_min)
        ratios.append(
            system.alveoli.partial_pressure_fraction / alveolar_fraction_at_discontinuation
        )

    return WashoutCurve(
        agent_id=agent_id,
        condition=condition,
        hepatic_elimination_rate_constant_per_min=hepatic_elimination_rate_constant_per_min,
        muscle_tissue_gas_partition_coefficient=muscle_tissue_gas_partition_coefficient,
        alveolar_fraction_at_discontinuation=alveolar_fraction_at_discontinuation,
        fractions_at_discontinuation=fractions_at_discontinuation,
        ratios_by_minute=tuple(ratios),
        agent_taken_up_l=agent_taken_up_l,
        muscle_agent_at_discontinuation_l=muscle_agent_at_discontinuation_l,
        agent_metabolised_l=metabolised,
        agent_accounting=system.agent_simulation_validation,
    )


@pytest.fixture(scope="session")
def washout_curve(
    request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory
) -> Callable[..., WashoutCurve]:
    """`_washout_curve()`, computed once per pytest run however many xdist workers read it.

    A curve is 864,000 steps after the wash-in, about 17 s on one core, and
    `_washout_curve()`'s cache lives in one process, so every xdist worker
    that ran a test needing a curve used to compute it again: 18 computations
    of the 8 distinct curves (`PL-F08Y`). Now the first worker to need a
    curve computes it under a lock and publishes it where every worker of the
    run can read it, and a worker needing the same curve meanwhile waits on
    the lock and reads what was published. Sending each curve's tests to one
    worker with `--dist loadgroup` computes each curve once too, and was
    measured and set aside: it slowed the rest of the suite by 8 to 11 s, and
    the whole run by 19 s against this (`PL-F08Y` has the figures).

    The directory is the run's own base temporary directory, the parent of
    each worker's, which pytest makes afresh for every run and empties when
    one is named with `--basetemp`. A curve published there cannot be served
    to a later run built from different source, which is the hazard `PL-0MLZ`
    closed for bytecode. For the same reason, whether to share turns on
    `workerinput`, which xdist sets on a worker's own configuration, and not
    on `PYTEST_XDIST_WORKER`, which a pytest started inside a worker would
    inherit: that run's base directory's parent outlives it. A curve is
    written whole and then renamed into place, and the lock is `flock`, which
    the kernel releases if the worker holding it dies, so a crash leaves the
    next worker to compute the curve rather than read half of one or wait for
    ever.
    Without xdist one process runs every test and its cache is the whole
    story. Windows has no `fcntl`, so there each worker computes what it
    needs, as every worker did before.
    """

    if fcntl is None or not hasattr(request.config, "workerinput"):
        return _washout_curve

    store = tmp_path_factory.getbasetemp().parent / "washout-curves"
    store.mkdir(exist_ok=True)

    @cache
    def shared(
        agent_id: str,
        condition: Condition,
        hepatic_elimination_rate_constant_per_min: float = 0.0,
        muscle_tissue_gas_partition_coefficient: float | None = None,
        elimination_duration_min: int = ELIMINATION_DURATION_MIN,
    ) -> WashoutCurve:
        name = (
            f"{agent_id}, {condition}, {hepatic_elimination_rate_constant_per_min}, "
            f"{muscle_tissue_gas_partition_coefficient}, {elimination_duration_min}"
        )
        published = store / f"{name}.pickle"
        with (store / f"{name}.lock").open("w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if published.exists():
                curve: WashoutCurve = pickle.loads(published.read_bytes())
                return curve
            curve = _washout_curve(
                agent_id,
                condition,
                hepatic_elimination_rate_constant_per_min,
                muscle_tissue_gas_partition_coefficient,
                elimination_duration_min,
            )
            partial = store / f"{name}.partial"
            partial.write_bytes(pickle.dumps(curve))
            partial.replace(published)
            return curve

    return shared


def _crossing_hours(curve: WashoutCurve, fit: PublishedWashoutFit) -> tuple[float, ...]:
    """Every hour at which the model passes through the fitted curve.

    Read from the second minute's sample on, so the first-minute transient -
    the model's lung term against the fit's - is where the sign starts rather
    than a crossing of its own.
    """

    hours = []
    previously_above = curve.ratio_at(1) > fit.ratio_at(1)
    for minute in range(2, len(curve.ratios_by_minute)):
        above = curve.ratio_at(minute) > fit.ratio_at(minute)
        if above != previously_above:
            hours.append(minute / MINUTES_PER_HOUR)
            previously_above = above
    return tuple(hours)


def _muscle_coefficient_at_the_fitted_time_constant(fit: PublishedWashoutFit) -> float:
    """The muscle tissue:gas coefficient that gives the fitted muscle term's time constant.

    The isolated group's time constant is its volume times its tissue:gas
    coefficient over its blood flow times the blood:gas coefficient, the
    arithmetic `docs/MODEL.md` compared with the fitted one until `PL-921Y`
    read the model's term off its curve instead. This solves it for the
    coefficient, on the reference adult the run is configured from, so the
    volume, the flow and the blood:gas coefficient stay the stored ones and
    only the muscle group's solubility moves. The apparent time constant it
    leaves the group, the one that compares with the fitted, is 1.09 to 1.28
    times the fitted
    (`test_the_model_s_apparent_muscle_and_fat_terms_against_the_fitted_ones`),
    so the variation takes the muscle term most of the way to the fitted one.
    """

    patient = load_reference_adult_parameters()
    agent = load_agent_parameters(fit.agent_id)
    blood_flow_l_min = patient.muscle_perfusion_fraction * patient.default_cardiac_output_l_min

    return (
        fit.time_constants_min[MUSCLE_GROUP]
        * blood_flow_l_min
        * agent.blood_gas_partition_coefficient
        / patient.muscle_volume_l
    )


def _rise_toward_the_fitted_curve(
    curve: WashoutCurve, fit: PublishedWashoutFit
) -> tuple[float, float]:
    """Where model over fit peaks after its early dip, as (hours, ratio).

    Every run here turns the same three times in its first day: model over
    fit dips inside the first half hour, rises to a peak, and falls to a
    trough the fat group's return later lifts it out of. This is the peak:
    the first maximum after the first minimum, read from the second minute
    on, as `_crossing_hours()` reads, to the minute the curve is sampled at.
    """

    ratios = [
        curve.ratio_at(minute) / fit.ratio_at(minute)
        for minute in range(len(curve.ratios_by_minute))
    ]
    turns = [
        minute
        for minute in range(2, len(ratios) - 1)
        if (ratios[minute] - ratios[minute - 1]) * (ratios[minute + 1] - ratios[minute]) < 0
    ]
    dips = [minute for minute in turns if ratios[minute] < ratios[minute - 1]]
    peaks = [
        minute
        for minute in turns
        if ratios[minute] > ratios[minute - 1] and dips and minute > dips[0]
    ]
    if not peaks:
        raise AssertionError(
            f"{fit.label}, {curve.condition}: model over fit never rises to a peak after a "
            f"dip within {len(ratios) - 1} min, so there is no rise toward the curve to place"
        )
    return peaks[0] / MINUTES_PER_HOUR, ratios[peaks[0]]


def _open_circuit_system_per_min(
    agent_id: str, muscle_tissue_gas_partition_coefficient: float | None = None
) -> numpy.ndarray:
    """The open circuit's elimination as $`dF/dt = M F`$, written out from the specification.

    F is the alveolar, mixed venous and three tissue groups' partial-pressure
    fractions, in `OPEN_CIRCUIT_STATES`' order, at the reference patient's
    default ventilation and cardiac output, which is `_configured_system()`'s
    operating point. Each row is the equation `docs/MODEL.md` § "Governing
    equations" gives for its state, with the inspired fraction held at zero:
    the limit `_discard_circuit_contents()` approaches by emptying the circuit
    after every step. Only the parameter loaders are reused, as
    `test_coupled_dynamics.py`'s `_build_derivative()` reuses them; nothing
    here reaches the implementation under test, so the stepped run's agreement
    with these equations' modes is evidence rather than an identity.

    `muscle_tissue_gas_partition_coefficient` replaces the stored coefficient
    as `_washout_curve()`'s does, with the group's blood flow unchanged.
    """

    agent = load_agent_parameters(agent_id)
    patient = load_reference_adult_parameters()
    blood_gas = agent.blood_gas_partition_coefficient
    muscle_tissue_gas = (
        agent.muscle_tissue_gas_partition_coefficient
        if muscle_tissue_gas_partition_coefficient is None
        else muscle_tissue_gas_partition_coefficient
    )
    # Volume, share of cardiac output and tissue:blood coefficient, per group.
    tissues = (
        (
            patient.vessel_rich_volume_l,
            patient.vessel_rich_perfusion_fraction,
            agent.vessel_rich_tissue_gas_partition_coefficient / blood_gas,
        ),
        (patient.muscle_volume_l, patient.muscle_perfusion_fraction, muscle_tissue_gas / blood_gas),
        (
            patient.fat_volume_l,
            patient.fat_perfusion_fraction,
            agent.fat_tissue_gas_partition_coefficient / blood_gas,
        ),
    )
    ventilation_l_min = patient.default_alveolar_ventilation_l_min
    cardiac_output_l_min = patient.default_cardiac_output_l_min
    alveolar_volume_l = patient.alveolar_gas_volume_l
    venous_volume_l = patient.venous_pool_volume_l
    alveolar, venous = 0, 1

    system = numpy.zeros((len(OPEN_CIRCUIT_STATES), len(OPEN_CIRCUIT_STATES)))

    # Alveolar gas, breathing nothing in: ventilation out, pulmonary uptake out.
    system[alveolar, alveolar] = (
        -(ventilation_l_min + cardiac_output_l_min * blood_gas) / alveolar_volume_l
    )
    system[alveolar, venous] = cardiac_output_l_min * blood_gas / alveolar_volume_l

    # Venous pool: each group's outflow in, mixed at the cardiac output.
    system[venous, venous] = -cardiac_output_l_min / venous_volume_l

    # Each group, perfusion-limited and driven by arterial blood, which is
    # alveolar.
    for state, (volume_l, perfusion_fraction, tissue_blood) in enumerate(tissues, start=2):
        blood_flow_l_min = cardiac_output_l_min * perfusion_fraction
        rate_per_min = blood_flow_l_min / (volume_l * tissue_blood)
        system[state, alveolar] = rate_per_min
        system[state, state] = -rate_per_min
        system[venous, state] = blood_flow_l_min / venous_volume_l

    return system


def _open_circuit_modes(
    agent_id: str,
    fractions_at_discontinuation: tuple[float, ...],
    muscle_tissue_gas_partition_coefficient: float | None = None,
) -> OpenCircuitModes:
    """Decompose the open circuit's elimination into its modes, from one state.

    `numpy.linalg.eig` is LAPACK's general eigensolver, and the state is
    expanded on the eigenvectors by a linear solve; each mode's amplitude is
    its eigenvector's alveolar entry times its weight, over F_A0.
    """

    system = _open_circuit_system_per_min(agent_id, muscle_tissue_gas_partition_coefficient)
    rates_per_min, vectors = numpy.linalg.eig(system)
    weights = numpy.linalg.solve(vectors, numpy.array(fractions_at_discontinuation))
    fastest_first = sorted(range(len(rates_per_min)), key=lambda mode: rates_per_min[mode].real)
    alveolar_fraction_at_discontinuation = fractions_at_discontinuation[0]

    return OpenCircuitModes(
        time_constants_min=tuple(complex(-1.0 / rates_per_min[mode]) for mode in fastest_first),
        amplitudes=tuple(
            complex(vectors[0, mode] * weights[mode] / alveolar_fraction_at_discontinuation)
            for mode in fastest_first
        ),
        dominant_states=tuple(
            OPEN_CIRCUIT_STATES[int(numpy.argmax(numpy.abs(vectors[:, mode] * weights[mode])))]
            for mode in fastest_first
        ),
    )


def _isolated_time_constants_min(agent_id: str) -> tuple[float, float]:
    """The muscle and fat groups' time constants with nothing returned to them in arterial blood.

    Each is the group's volume times its tissue:gas coefficient over its blood
    flow times the blood:gas coefficient, on the reference adult: the
    arithmetic `_muscle_coefficient_at_the_fitted_time_constant()` inverts.
    """

    agent = load_agent_parameters(agent_id)
    patient = load_reference_adult_parameters()
    blood_gas = agent.blood_gas_partition_coefficient
    cardiac_output_l_min = patient.default_cardiac_output_l_min

    muscle = (
        patient.muscle_volume_l
        * agent.muscle_tissue_gas_partition_coefficient
        / (patient.muscle_perfusion_fraction * cardiac_output_l_min * blood_gas)
    )
    fat = (
        patient.fat_volume_l
        * agent.fat_tissue_gas_partition_coefficient
        / (patient.fat_perfusion_fraction * cardiac_output_l_min * blood_gas)
    )
    return muscle, fat


@pytest.mark.parametrize("condition", CONDITIONS)
@pytest.mark.parametrize("fit", PUBLISHED_FITS, ids=[f.label for f in PUBLISHED_FITS])
def test_the_first_24_hours_of_elimination_against_the_published_mean_curves(
    fit: PublishedWashoutFit, condition: Condition, washout_curve: Callable[..., WashoutCurve]
) -> None:
    """Hold the ratio table and the crossing hours to what was measured.

    The module docstring carries the reading; this pins the numbers it reads
    from, in both conditions, so that a change to a parameter or to the
    propagator that moves the tail against the published curves by more than
    a percent, or moves a crossing by more than a tenth of an hour, fails
    here and is re-measured rather than silently absorbed. It asserts nothing
    about agreement: a change that brought every ratio to 1.0 would fail it.
    """

    curve = washout_curve(fit.agent_id, condition)
    recorded = RECORDED_COMPARISONS[fit.label, condition]

    for minutes, expected in zip(STATED_MINUTES, recorded.ratios, strict=True):
        ratio = curve.ratio_at(minutes) / fit.ratio_at(minutes)
        assert abs(ratio - expected) <= RATIO_REGRESSION_TOLERANCE * expected, (
            f"{fit.label}, {condition}: at {minutes} min the model's F_A/F_A0 is "
            f"{curve.ratio_at(minutes):.5f} against the fitted {fit.ratio_at(minutes):.5f}, a "
            f"ratio of {ratio:.3f} where this module measured {expected} on 2026-09-27. "
            "Re-measure this module's tables and docs/MODEL.md's rather than widening the band"
        )

    crossings = _crossing_hours(curve, fit)
    assert len(crossings) == len(recorded.crossing_hours) and all(
        abs(found - expected) <= CROSSING_TOLERANCE_H
        for found, expected in zip(crossings, recorded.crossing_hours, strict=True)
    ), (
        f"{fit.label}, {condition}: the model now crosses the fitted curve at "
        f"{tuple(round(h, 2) for h in crossings)} h where this module measured "
        f"{recorded.crossing_hours} on 2026-09-27; the stretches the module docstring and "
        "docs/MODEL.md describe have moved"
    )


@pytest.mark.parametrize("condition", CONDITIONS)
@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_the_twenty_four_hour_run_opens_from_the_five_minute_gate_s_own_ratio(
    agent_id: str, condition: Condition, washout_curve: Callable[..., WashoutCurve]
) -> None:
    """The fifth minute of this run is the gate's five-minute point.

    Same setup, same discontinuation, same driver for the open circuit, so
    the ratio at five minutes must agree with the value the gate pins to four
    decimals. This is what makes the tables above a continuation of the
    gate's comparison rather than a second protocol that could drift from it.
    """

    pinned = (
        MODELLED_ELIMINATION_RATIOS if condition == "shipped" else OPEN_CIRCUIT_ELIMINATION_RATIOS
    )[agent_id]
    ratio = washout_curve(agent_id, condition).ratio_at(5)

    assert abs(ratio - pinned) <= 1e-4, (
        f"{agent_id}, {condition}: F_A/F_A0 at five minutes of this run is {ratio:.5f}, "
        f"where the gate pins {pinned}; the two runs no longer share a protocol"
    )


@pytest.mark.parametrize("fit", PUBLISHED_FITS, ids=[f.label for f in PUBLISHED_FITS])
def test_the_published_coefficients_sum_below_one_at_discontinuation(
    fit: PublishedWashoutFit,
) -> None:
    """Record that the curves are compared un-normalised, and by how much.

    The amplitudes are means of per-subject fits and sum to 0.912 to 0.937,
    not 1. The module compares the curve as published; this pins the sum so
    that the 7 to 10% the docstring says normalising would move every ratio
    by cannot drift from the coefficients.
    """

    assert 0.91 <= fit.value_at_discontinuation <= 0.94, (
        f"{fit.label}: the published amplitudes sum to {fit.value_at_discontinuation:.4f} at "
        "discontinuation, outside the 0.912 to 0.937 the module docstring records"
    )


@pytest.mark.parametrize("fit", PUBLISHED_FITS, ids=[f.label for f in PUBLISHED_FITS])
def test_the_fitted_mean_curves_run_above_their_own_measured_five_minute_means(
    fit: PublishedWashoutFit,
) -> None:
    """Bound the fit against the data at the one time both are published.

    This is caveat 1 of the module docstring as a number: the curve built
    from mean coefficients sits above the measured five-minute mean of the
    same cohort in every case, by 0.33 to 1.84 published SD. Every ratio in
    the tables is an understatement of the model against the volunteers'
    mean to that extent, and the sign is what makes it an understatement
    rather than an overstatement, so both are pinned.
    """

    measurement = fit.measurement
    distance_sd = measurement.elimination_distance_in_standard_deviations(fit.ratio_at(5))
    recorded = RECORDED_FIT_ABOVE_MEASUREMENT_AT_FIVE_MINUTES_SD[fit.label]

    assert distance_sd > 0, (
        f"{fit.label}: the fitted curve gives {fit.ratio_at(5):.4f} at five minutes, at or "
        f"below the measured {measurement.elimination_mean}; the direction caveat 1 rests on "
        "has reversed"
    )
    assert abs(distance_sd - recorded) <= FIVE_MINUTE_DISTANCE_TOLERANCE_SD, (
        f"{fit.label}: the fitted curve sits {distance_sd:+.2f} SD from the measured "
        f"five-minute mean where the module records {recorded:+.2f}; a coefficient or a "
        "published value has changed"
    )


@pytest.mark.parametrize("fit", PUBLISHED_FITS, ids=[f.label for f in PUBLISHED_FITS])
def test_the_fourth_compartment_is_the_largest_term_over_the_recorded_hours(
    fit: PublishedWashoutFit,
) -> None:
    """Hold the hours the intertissue-diffusion note prints to the coefficients.

    `docs/MODEL.md` § "Known limitations" says the fourth compartment's term
    is the largest in the measured curve from about 1.8 to 3.1 hours until
    about 20.7 to 29.4 hours. Those were computed by hand on 2026-09-26; this
    re-derives them from the published coefficients and checks that the term
    does lead at every stated time inside the window that lies within the
    24 hours, so the sentence cannot outlive the arithmetic.
    """

    overtakes_muscle_h = fit.hours_at_which_terms_are_equal(MUSCLE_GROUP, FOURTH_COMPARTMENT)
    overtaken_by_fat_h = fit.hours_at_which_terms_are_equal(FOURTH_COMPARTMENT, FAT_GROUP)
    recorded_start_h, recorded_end_h = RECORDED_FOURTH_COMPARTMENT_LEAD_H[fit.label]

    assert abs(overtakes_muscle_h - recorded_start_h) <= 0.05, (
        f"{fit.label}: the fourth compartment overtakes the muscle group at "
        f"{overtakes_muscle_h:.2f} h, not the {recorded_start_h} h the note records"
    )
    assert abs(overtaken_by_fat_h - recorded_end_h) <= 0.05, (
        f"{fit.label}: the fat group overtakes the fourth compartment at "
        f"{overtaken_by_fat_h:.2f} h, not the {recorded_end_h} h the note records"
    )
    elimination_end_h = ELIMINATION_DURATION_MIN / MINUTES_PER_HOUR
    for minutes in STATED_MINUTES:
        hours = minutes / MINUTES_PER_HOUR
        if overtakes_muscle_h < hours < min(overtaken_by_fat_h, elimination_end_h):
            assert fit.leading_term_at(minutes) == FOURTH_COMPARTMENT, (
                f"{fit.label}: at {minutes} min the largest term is compartment "
                f"{fit.leading_term_at(minutes) + 1}, not the fourth"
            )


@pytest.mark.parametrize("condition", CONDITIONS)
@pytest.mark.parametrize("fit", PUBLISHED_FITS, ids=[f.label for f in PUBLISHED_FITS])
def test_the_muscle_group_s_slow_return_places_the_tail_s_rise_in_hours_2_to_4(
    fit: PublishedWashoutFit, condition: Condition, washout_curve: Callable[..., WashoutCurve]
) -> None:
    """Vary the muscle group's coefficient, to test what fills hours 2 to 4.

    `PL-KK1Q` read the tail's rise toward the fitted curve over hours 2 to 4
    off the time constants alone: the model's isolated muscle group returns
    on a constant 1.5 to 1.7 times the fitted muscle term's, an isolated
    constant against an apparent one, which `PL-921Y` later read like for
    like at 1.89 to 2.02. This runs the counterfactual instead (`PL-95NW`):
    the same protocol with the group's tissue:gas coefficient lowered until
    its isolated time constant is the cohort's fitted one, everything else
    stored.

    It checks first that the change moves the rate of return and not the
    store: the group holds 4 to 10% less at discontinuation, because over a
    30-minute wash-in it is far from equilibrium and takes up agent about as
    fast as its blood flow brings it, whatever its capacity. A variation
    that emptied the store would lower the tail for a reason the reading
    does not name. Then it holds where the rise peaks on each coefficient,
    and the four-hour ratio and the crossings on the lowered one, to what
    was measured on 2026-10-03, and asserts the reading itself: the rise
    peaks after the second hour as stored and before it at the fitted time
    constant, and the tail at four hours is lower.
    """

    coefficient = _muscle_coefficient_at_the_fitted_time_constant(fit)
    stored_coefficient = load_agent_parameters(fit.agent_id).muscle_tissue_gas_partition_coefficient
    as_stored = washout_curve(fit.agent_id, condition)
    varied = washout_curve(fit.agent_id, condition, 0.0, coefficient, MUSCLE_VARIATION_DURATION_MIN)
    recorded = RECORDED_MUSCLE_VARIATIONS[fit.label, condition]

    share = coefficient / stored_coefficient
    assert abs(share - RECORDED_MUSCLE_COEFFICIENT_SHARES[fit.label]) <= 1e-4, (
        f"{fit.label}: the fitted muscle time constant now takes {share:.4f} of the stored "
        f"coefficient where this module recorded {RECORDED_MUSCLE_COEFFICIENT_SHARES[fit.label]}; "
        "a stored muscle, blood or flow parameter has changed"
    )
    assert varied.agent_accounting.passes_validation, (
        f"{fit.label}, {condition}: the lowered coefficient broke the model's agent accounting: "
        f"{varied.agent_accounting}"
    )

    store_share = (
        varied.muscle_agent_at_discontinuation_l / as_stored.muscle_agent_at_discontinuation_l
    )
    assert store_share >= 0.9, (
        f"{fit.label}: the lowered coefficient leaves the muscle group holding {store_share:.1%} "
        "of its stored amount at discontinuation, so the variation moves the store as well as "
        "the rate of return, and the tail it draws no longer tests the rate alone"
    )
    assert abs(store_share - RECORDED_MUSCLE_STORE_SHARES[fit.label]) <= (
        MUSCLE_STORE_SHARE_TOLERANCE
    ), (
        f"{fit.label}: the muscle group holds {store_share:.4f} of its stored amount at "
        f"discontinuation where this module measured {RECORDED_MUSCLE_STORE_SHARES[fit.label]}"
    )

    rise_as_stored = _rise_toward_the_fitted_curve(as_stored, fit)
    rise_varied = _rise_toward_the_fitted_curve(varied, fit)
    for which, (hours, ratio), (expected_hours, expected_ratio) in (
        ("stored", rise_as_stored, recorded.rise_as_stored),
        ("fitted time constant", rise_varied, recorded.rise_at_fitted_time_constant),
    ):
        assert (
            abs(hours - expected_hours) <= CROSSING_TOLERANCE_H
            and abs(ratio - expected_ratio) <= RATIO_REGRESSION_TOLERANCE * expected_ratio
        ), (
            f"{fit.label}, {condition}, {which}: the rise toward the curve now peaks at "
            f"{ratio:.3f} at {hours:.2f} h where this module measured {expected_ratio} at "
            f"{expected_hours} h on 2026-10-03; re-measure it here and in docs/MODEL.md"
        )
    assert rise_varied[0] < 2.0 < rise_as_stored[0], (
        f"{fit.label}, {condition}: the rise toward the curve peaks at {rise_as_stored[0]:.2f} h "
        f"as stored and {rise_varied[0]:.2f} h at the fitted time constant, so the muscle "
        "group's rate of return no longer decides whether it falls in hours 2 to 4"
    )

    four_hours = varied.ratio_at(FOUR_HOURS_MIN) / fit.ratio_at(FOUR_HOURS_MIN)
    four_hours_as_stored = as_stored.ratio_at(FOUR_HOURS_MIN) / fit.ratio_at(FOUR_HOURS_MIN)
    expected = recorded.ratio_at_four_hours_at_fitted_time_constant
    assert four_hours < four_hours_as_stored, (
        f"{fit.label}, {condition}: at four hours the tail is {four_hours:.3f} of the fitted "
        f"curve at the fitted time constant and {four_hours_as_stored:.3f} as stored"
    )
    assert abs(four_hours - expected) <= RATIO_REGRESSION_TOLERANCE * expected, (
        f"{fit.label}, {condition}: at four hours the tail is {four_hours:.3f} of the fitted "
        f"curve at the fitted time constant where this module measured {expected}"
    )

    crossings = _crossing_hours(varied, fit)
    expected_crossings = recorded.crossing_hours_at_fitted_time_constant
    assert len(crossings) == len(expected_crossings) and all(
        abs(found - crossing) <= CROSSING_TOLERANCE_H
        for found, crossing in zip(crossings, expected_crossings, strict=True)
    ), (
        f"{fit.label}, {condition}: at the fitted time constant the tail now crosses the curve at "
        f"{tuple(round(h, 2) for h in crossings)} h where this module measured "
        f"{expected_crossings} on 2026-10-03"
    )


def _shortfalls_from_the_stepped_run(
    curve: WashoutCurve, modes: OpenCircuitModes
) -> dict[int, float]:
    """The modes' F_A/F_A0 over the stepped run's, less 1, at each minute from the fifth."""

    return {
        minute: modes.ratio_at(minute) / curve.ratio_at(minute) - 1.0
        for minute in range(RECONSTRUCTION_FROM_MINUTE, len(curve.ratios_by_minute))
    }


@pytest.mark.parametrize("fit", PUBLISHED_FITS, ids=[f.label for f in PUBLISHED_FITS])
def test_the_model_s_apparent_muscle_and_fat_terms_against_the_fitted_ones(
    fit: PublishedWashoutFit, washout_curve: Callable[..., WashoutCurve]
) -> None:
    """Read the model's muscle and fat terms off its own curve, as the fits were read.

    A fitted time constant is an apparent one, read off the whole washout, and
    `docs/MODEL.md` compared the fitted muscle and fat constants with the
    model's isolated ones, which leave out the agent arterial blood brings
    back to a group during the washout (`PL-921Y`). Like for like is the
    model's own curve read the same way, which is its open-circuit system's
    modes.

    It checks first that the modes are the stepped run: decomposed from the
    state the open-circuit run held at discontinuation, they reproduce it to
    within `MODE_RECONSTRUCTION_TOLERANCE` at every minute from the fifth,
    with the run above them, where the driver's re-breathing puts it; and the
    three slowest are real, the two slowest the muscle and fat groups'. Then
    it holds
    both terms, the isolated constants and, at the coefficient
    `test_the_muscle_group_s_slow_return_places_the_tail_s_rise_in_hours_2_to_4`
    runs, the apparent muscle constant, to what was measured on 2026-10-03.
    Last it asserts the reading `docs/MODEL.md` gives: the muscle term is
    slower than the fitted one and smaller, and the fat term slower and
    larger; each isolated constant is shorter than the apparent one; and the
    varied coefficient takes the apparent muscle constant most of the way to
    the fitted one, not all of it.
    """

    coefficient = _muscle_coefficient_at_the_fitted_time_constant(fit)
    runs = {
        "stored": washout_curve(fit.agent_id, "open circuit"),
        "varied": washout_curve(
            fit.agent_id, "open circuit", 0.0, coefficient, MUSCLE_VARIATION_DURATION_MIN
        ),
    }
    modes = {
        "stored": _open_circuit_modes(fit.agent_id, runs["stored"].fractions_at_discontinuation),
        "varied": _open_circuit_modes(
            fit.agent_id, runs["varied"].fractions_at_discontinuation, coefficient
        ),
    }

    for which, run in runs.items():
        amplitudes_sum = sum(modes[which].amplitudes)
        assert abs(amplitudes_sum - 1.0) <= 1e-12, (
            f"{fit.label}, {which}: the modes' amplitudes sum to {amplitudes_sum}, not to the "
            "state they were decomposed from"
        )
        shortfalls = _shortfalls_from_the_stepped_run(run, modes[which])
        worst = max(shortfalls, key=lambda minute: abs(shortfalls[minute]))
        assert abs(shortfalls[worst]) <= MODE_RECONSTRUCTION_TOLERANCE, (
            f"{fit.label}, {which}: the open circuit's modes depart from the stepped run by "
            f"{shortfalls[worst]:+.4%} at minute {worst}, so they no longer describe the curve "
            "the model draws, and nothing read off them is the model's"
        )
        assert all(shortfall < 0.0 for shortfall in shortfalls.values()), (
            f"{fit.label}, {which}: the stepped run falls below its modes at some minute, "
            "where re-breathing within each step can only hold it above them"
        )
        assert modes[which].dominant_states[-2:] == ("muscle group", "fat group"), (
            f"{fit.label}, {which}: the two slowest modes are mostly "
            f"{modes[which].dominant_states[-2:]}, so they are no longer the muscle and fat "
            "groups' returns and cannot be set against the fitted muscle and fat terms"
        )
        for mode in (-3, -2, -1):
            time_constant = modes[which].time_constants_min[mode]
            amplitude = modes[which].amplitudes[mode]
            assert time_constant.imag == 0.0 and abs(amplitude.imag) <= 1e-12 * abs(amplitude), (
                f"{fit.label}, {which}: the {modes[which].dominant_states[mode]}'s mode is "
                f"complex, tau {time_constant} min and A {amplitude}, so it is not a term of "
                "the fitted form"
            )

    muscle_min, fat_min = (modes["stored"].time_constants_min[mode].real for mode in (-2, -1))
    muscle_percent, fat_percent = (
        100.0 * modes["stored"].amplitudes[mode].real for mode in (-2, -1)
    )
    varied_muscle_min = modes["varied"].time_constants_min[-2].real
    isolated_muscle_min, isolated_fat_min = _isolated_time_constants_min(fit.agent_id)
    recorded = RECORDED_APPARENT_TERMS[fit.agent_id]
    for name, measured, expected in (
        ("muscle term's time constant, min", muscle_min, recorded.muscle_time_constant_min),
        ("muscle term's amplitude, %", muscle_percent, recorded.muscle_amplitude_percent),
        ("fat term's time constant, min", fat_min, recorded.fat_time_constant_min),
        ("fat term's amplitude, %", fat_percent, recorded.fat_amplitude_percent),
        (
            "isolated muscle time constant, min",
            isolated_muscle_min,
            recorded.isolated_muscle_time_constant_min,
        ),
        (
            "isolated fat time constant, min",
            isolated_fat_min,
            recorded.isolated_fat_time_constant_min,
        ),
        (
            "apparent muscle time constant at the varied coefficient, min",
            varied_muscle_min,
            RECORDED_APPARENT_MUSCLE_TIME_CONSTANTS_AT_FITTED_ISOLATED_MIN[fit.label],
        ),
    ):
        assert abs(measured - expected) <= APPARENT_TERM_TOLERANCE * expected, (
            f"{fit.label}: the {name} is now {measured:.5g} where this module measured "
            f"{expected} on 2026-10-03; re-measure it here and in docs/MODEL.md"
        )

    fitted_muscle_min = fit.time_constants_min[MUSCLE_GROUP]
    fitted_fat_min = fit.time_constants_min[FAT_GROUP]
    assert (
        muscle_min > fitted_muscle_min and muscle_percent < fit.amplitudes_percent[MUSCLE_GROUP]
    ), (
        f"{fit.label}: the model's muscle term is {muscle_percent:.2f}% on {muscle_min:.1f} min "
        f"against the fitted {fit.amplitudes_percent[MUSCLE_GROUP]}% on {fitted_muscle_min} min, "
        "no longer slower and smaller"
    )
    assert fat_min > fitted_fat_min and fat_percent > fit.amplitudes_percent[FAT_GROUP], (
        f"{fit.label}: the model's fat term is {fat_percent:.3f}% on {fat_min:.0f} min against "
        f"the fitted {fit.amplitudes_percent[FAT_GROUP]}% on {fitted_fat_min} min, no longer "
        "slower and larger"
    )
    assert isolated_muscle_min < muscle_min and isolated_fat_min < fat_min, (
        f"{fit.agent_id}: an isolated time constant, {isolated_muscle_min:.1f} or "
        f"{isolated_fat_min:.0f} min, is no longer shorter than the apparent one, "
        f"{muscle_min:.1f} or {fat_min:.0f} min, which recirculation alone should make it"
    )
    assert fitted_muscle_min < varied_muscle_min < muscle_min and (
        varied_muscle_min - fitted_muscle_min < muscle_min - varied_muscle_min
    ), (
        f"{fit.label}: with the isolated constant made the fitted one's, the apparent muscle "
        f"constant is {varied_muscle_min:.1f} min, against {fitted_muscle_min} fitted and "
        f"{muscle_min:.1f} stored, no longer most of the way to the fitted one"
    )


@pytest.mark.parametrize("condition", CONDITIONS)
def test_sevoflurane_s_missing_metabolism_moves_the_tail_by_a_few_percent(
    condition: Condition, washout_curve: Callable[..., WashoutCurve]
) -> None:
    """Bound what the omitted metabolism could do to the sevoflurane tail.

    The sink runs at Yasuda et al.'s own fitted hepatic rate constant and
    removes more of the uptake than the top of Kharasch's range, which is
    what makes its effect a bound rather than an estimate; that share is
    asserted first, because the bound is worth nothing without it. Then the
    reduction it makes in F_A/F_A0 at every stated time is held to what was
    measured - 4.5 to 5.0% at five minutes and under 3% after - against
    departures from the fitted curve that reach 20 to 50%, which is the
    module docstring's "little". The model's own conservation identity is
    checked across the removals too, as it is for the open-circuit discards.
    """

    without = washout_curve("sevoflurane", condition)
    with_sink = washout_curve("sevoflurane", condition, HEPATIC_ELIMINATION_RATE_CONSTANT_PER_MIN)

    assert with_sink.agent_accounting.passes_validation, (
        f"{condition}: the sink broke the model's agent accounting: {with_sink.agent_accounting}"
    )

    share = with_sink.metabolised_share_of_uptake
    assert share >= KHARASCH_UPPER_METABOLISED_SHARE, (
        f"{condition}: the sink removes {share:.1%} of the 30-minute uptake by 24 hours, below "
        f"the {KHARASCH_UPPER_METABOLISED_SHARE:.0%} that makes its effect a bound"
    )
    assert abs(share - RECORDED_METABOLISED_SHARE[condition]) <= METABOLISED_SHARE_TOLERANCE, (
        f"{condition}: the sink removes {share:.4f} of the uptake where this module measured "
        f"{RECORDED_METABOLISED_SHARE[condition]}"
    )

    for minutes, expected in zip(STATED_MINUTES, RECORDED_TAIL_REDUCTIONS[condition], strict=True):
        reduction = 1.0 - with_sink.ratio_at(minutes) / without.ratio_at(minutes)
        assert abs(reduction - expected) <= TAIL_REDUCTION_TOLERANCE, (
            f"{condition}: at {minutes} min the sink lowers F_A/F_A0 by {reduction:.4f} where this "
            f"module measured {expected}"
        )
        if minutes > 5:
            assert reduction <= 0.03, (
                f"{condition}: at {minutes} min the sink lowers F_A/F_A0 by {reduction:.1%}, more "
                "than the few percent the module docstring bounds it to"
            )

    fit = PUBLISHED_FITS[0]
    widest_departure = max(
        abs(without.ratio_at(minutes) / fit.ratio_at(minutes) - 1.0)
        for minutes in STATED_MINUTES
        if minutes > 5
    )
    assert widest_departure >= 0.2, (
        f"{condition}: the widest departure from the fitted curve after five minutes is "
        f"{widest_departure:.2f}, no longer the 20 to 50% the sink's few percent is read against"
    )
