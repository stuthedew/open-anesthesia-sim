---
id: PL-HB58
title: Validate washout against the same published cohorts the wash-in gate already uses
priority: P1
effort: M
status: done
classes: science, test
feature: numerical-domain
milestone: v0.4.6
touches: tests/reference/test_published_wash_in_and_elimination.py, docs/MODEL.md
added: 2026-09-03
closed: 2026-09-06
pr: 412
verify: uv run pytest tests/reference/test_published_wash_in.py && grep -q 'def test_five_minute_elimination_ratio_against_published_human_measurement' tests/reference/test_published_wash_in.py
---

**Problem.** `tests/reference/test_published_wash_in_and_elimination.py` is this project's only
external validation, and it spends one measured quantity per agent: F_A/F_I at
30 minutes of wash-in. Both cited papers report a second, in the opposite
direction, which nothing here uses - F_A/F_A0 after 5 minutes of *elimination*,
following the same 30-minute administration the wash-in figures come from:

| Cohort | Agent | F_A/F_A0 at 5 min |
| --- | --- | --- |
| Anesth Analg 1991;72:316-24 (n=7) | sevoflurane | 0.157 +/- 0.020 |
| Anesth Analg 1991;72:316-24 (n=7) | isoflurane | 0.223 +/- 0.024 |
| Anesthesiology 1991;74:489-98 (n=8) | desflurane | 0.14 +/- 0.02 |
| Anesthesiology 1991;74:489-98 (n=8) | isoflurane | 0.22 +/- 0.02 |

Both are mean +/- SD, transcribed from the abstracts and verified against
PubMed 2026-09-03:

- Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Liu J, Laster M, Taheri S,
  Peterson NA. Comparison of kinetics of sevoflurane and isoflurane in humans.
  Anesth Analg 1991;72(3):316-24. PMID 1994760.
  doi:10.1213/00000539-199103000-00007
- Yasuda N, Lockhart SH, Eger EI 2nd, Weiskopf RB, Johnson BH, Freire BA,
  Fassoulaki A. Kinetics of desflurane, isoflurane, and halothane in humans.
  Anesthesiology 1991;74(3):489-98. PMID 2001028.
  doi:10.1097/00000542-199103000-00017

Isoflurane appears in both cohorts, as it does for wash-in, so four
comparisons cover three agents.

**Why it matters.** Wash-in at 30 minutes and washout at 5 minutes constrain
different parts of the parameter set. The 30-minute ratio is dominated by
blood solubility and vessel-rich uptake; the 5-minute elimination ratio is
dominated by return *out of* tissue, which is the direction no gate in this
repository tests at all. A model can reproduce uptake and misstate recovery -
that is the classic failure of an under-parameterized tissue compartment, and
it is the half a teaching simulator is most often used to demonstrate.

It also sharpens a gate the module itself documents as coarse. Its measured
discriminating power at the reference point tolerates a solubility error of
-14%/+21% for sevoflurane and -12%/+24% for isoflurane, which is wider than
the spread between published measurements of the same coefficient. A second
comparison in the opposite direction is the cheapest available way to narrow
that, because a parameter change that survives wash-in need not survive
washout.

**Caveats, which are the same two the module already states, plus one.**
The published subjects breathed 65-70% N2O concurrently, which this model
cannot reproduce; the parameters descend from the same Gas Man lineage as the
measurements. New here: the model has no metabolism, which is negligible over
5 minutes of elimination for all three agents but is the reason this must not
be extended to the multi-day elimination curves the same papers report.

**Approach.** Extend the existing module rather than adding a second one - the
operating-point discipline, the `PublishedMeasurement` dataclass, the +/-1 SD
band and `test_operating_point_is_the_parameter_files_own_defaults` all apply
unchanged and are what keep the comparison from being circular. Wash in for
the published 30 minutes at the shipped defaults, record F_A0, set the dial to
zero, run 5 more minutes, and compare F_A/F_A0. Re-measure the perturbation
table with the washout point included and update the module's own docstring
table with it; that measurement is the deliverable as much as the test is,
since it is what tells a later reader how sharp the gate now is.

While there, say which question the +/-1 SD band answers. A deterministic
model compared against a cohort *mean* would conventionally be judged against
the SEM, where desflurane's +0.79 SD on wash-in is +2.2 SEM. The SD band is
defensible - it asks whether the model is a plausible individual - but the
module should state which of the two claims it is making.

**Done when.** `tests/reference/test_published_wash_in_and_elimination.py` compares modelled
F_A/F_A0 at 5 minutes of elimination against all four published cohort values
at the shipped defaults, the module's measured-sensitivity table is re-derived
with the washout point in it, and `docs/MODEL.md` § "Published wash-in
validation test" names the washout comparison alongside the wash-in one.
