---
id: PL-KK1Q
title: Compare this model's washout over the first 24 h against Yasuda 1991's published five-compartment mean fits, to measure whether the modelled tail runs fast or slow where only the five-minute point is validated today
priority: P1
effort: M
status: done
classes: science, test
feature: late-washout-evidence
touches: tests/reference, docs/MODEL.md, README.md, docs/references/README.md
added: 2026-09-26
closed: 2026-09-27
pr: 1175
payoff: a reader of the washout tail learns how far, and from which hour, the modelled curve departs from measured human washout, instead of only which way the missing terms push it
verify: grep -rq 'def test_the_first_24_hours_of_elimination_against_the_published_mean_curves' tests/reference/ && grep -qF 'PL-KK1Q' docs/MODEL.md
---

**Problem.** Compare this model's washout over the first 24 h against Yasuda 1991's published five-compartment mean fits, to measure whether the modelled tail runs fast or slow where only the five-minute point is validated today

**Found 2026-09-26 while working `PL-WMCJ`.** The figures are in `docs/MODEL.md` § "Known limitations", the intertissue-diffusion note that item added, which carries the table, the pages of both Yasuda 1991 papers read from the private reference corpus, and how each ratio and crossing time was computed.

**Premise checked 2026-09-27.** `docs/MODEL.md` § "Published wash-in and
elimination validation test" compares elimination at five minutes only, and its
caveat 4 refuses the Yasuda papers' multi-day curves for the pass/fail
comparison. The intertissue-diffusion note under "Known limitations" says of
the late washout: "Whether it does fall below the measured tail over those
hours has not been measured".

**Why it matters.** The chart draws a washout tail to 24 hours, and all that is
said of how it compares with human washout is structural: which terms are
missing and which way that pushes. How far, and from which hour, the modelled
curve departs from the measured mean is unmeasured, so a reader of the tail has
a direction and no size. The published mean hybrid coefficients (Tables 1 and 2
of both Yasuda 1991 papers, read at full text on 2026-09-26 per the note's
sources) make it a computation rather than an experiment.

**Done when.** A test under `tests/reference/` runs this model through the
studies' 30-minute administration and 24 hours of elimination, under the
conditions the five-minute elimination comparison in
`tests/reference/test_published_wash_in_and_elimination.py` reproduces, and
compares FA/FA0 with each of the four cohorts' published mean five-compartment
curve at stated times. `docs/MODEL.md` records the ratios, the hours at which
the modelled curve runs above or below the measured one, how much of any gap
sevoflurane's missing metabolism could account for, and the test that computes
them, citing `PL-KK1Q`; the note's "has not been measured" sentence gives way
to the result; and the record says whether the result bears on § "Supported run
length"'s 24 hours, putting that question to the project owner if it does. It
is a measurement recorded beside the validation test, not a new pass/fail gate,
so caveat 4's refusal of the multi-day curves stands.

**Published hybrid coefficients, read at the source 2026-09-27 for this
chain** (mean values; SDs on the pages). Each washout is
$`F_A/F_{A0} = \sum_i A_i e^{-t/\tau_i}`$ with $`A_i`$ printed as
$`A_i \times 100`$ and $`\tau_i`$ in minutes, compartments in the order lungs,
vessel-rich group, muscle group, fourth compartment, fat group:

- *Anesth Analg* 1991;72:316-24, Tables 1 and 2, p. 321 (text layer):
  sevoflurane $`A`$ = 63.6, 24.7, 4.60, 0.717, 0.028 and $`\tau`$ = 0.46,
  9.17, 81.7, 437, 2230; isoflurane $`A`$ = 55.7, 26.9, 7.19, 1.296, 0.072 and
  $`\tau`$ = 0.39, 9.80, 85.0, 474, 2310.
- *Anesthesiology* 1991;74:489-98, Table 1 on p. 494 and Table 2 on p. 495
  (page images): desflurane $`A`$ = 64.4, 22.5, 4.86, 0.775, 0.031 and
  $`\tau`$ = 0.441, 5.78, 48.9, 300, 1350; isoflurane $`A`$ = 57.2, 28.4,
  5.93, 1.125, 0.080 and $`\tau`$ = 0.380, 8.72, 80.0, 482, 2110.

The $`A_i`$ do not sum exactly to 100 (means of per-subject fits), so a
comparison normalises the curve or states that it does not. The mammillary
fat-group and fourth-compartment values (Tables 4 and 5) are in
`docs/MODEL.md` § "Known limitations" and `PL-HBH2`'s closing note.
