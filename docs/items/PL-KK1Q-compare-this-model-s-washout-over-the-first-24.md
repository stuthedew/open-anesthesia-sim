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

**Closed 2026-09-27.** `tests/reference/test_late_washout_against_published_fits.py`
runs the gate's 30-minute wash-in and 24 hours of elimination at the shipped
0.1 s step, in both of the gate's conditions (shipped rebreathing circuit at
10 L/min; open circuit through the gate's test-only driver), and holds model
over fit at the papers' own sampling minutes (5, 30, 60, 120, 240, 400, 600,
800, 1400) and at 1440 to 1% of what it measured, and every crossing hour to
0.1 h: 28 tests, about 65 s on four workers, every one a regression band and
none an agreement claim. The fits are compared as published, un-normalised
(the amplitudes sum to 0.912-0.937; normalising would lower every ratio 7 to
10%), and the run's fifth minute is held to the gate's pinned ratios to four
decimals so the two modules share one protocol.

**Result.** The shipped tail runs below the fitted mean curves from 6.9-8.4 h
(3.4 h for desflurane) until 20.7-21.8 h (15.3 h), by a third at the widest
near 13 h (0.67, 0.68, 0.74) and by half for desflurane near 8 h (0.51): the
fourth compartment's era, which the model has no term for. It runs above them
by 12-52% from 0.8-2.0 h until that, while the rebreathing circuit holds it
up, and again at 24 h by 15-29% (a factor of 2.2 for desflurane), still
growing at the boundary as the fitted curve keeps falling on the fourth
compartment's time constant. With the apparatus taken away the tissue return
alone is a third to a half of the mean curve over hours 8-13 (0.34-0.46).
Metabolism bound: a test-only first-order sink on the vessel-rich group at
Yasuda's own fitted k20 = 0.0094 min⁻¹ removes 7.8% (shipped) and 7.2% (open)
of the 30-minute uptake, above Kharasch's 2-5%, and moves the tail 1.9-2.9%
after 30 minutes: about an eighth of the excess where the model runs above,
and a widening where it runs below.

**Recorded** in `docs/MODEL.md` § "The first 24 hours of elimination against
the published mean curves" (tables in both conditions, crossing hours, the
reading, three caveats, the metabolism bound, what a learner sees, the tests
by name); caveat 4's closing sentence, § "Supported run length", the "two
omissions" paragraph and the intertissue-diffusion note under § "Known
limitations" now point at it, and the desflurane-residual sentence calling
the gate the only written-down departure is qualified to the *measured*
washout. The gate module's docstring mirror of caveat 4, `README.md` and the
extraction note in `docs/references/README.md` were swept in the same commit;
`touches` widened to the last two for it.

**Verdict on § "Supported run length".** The result does not move the 24
hours, and the reasoning is recorded there: the departures are the missing
fourth compartment and the fat group's own size, present from the first hour
and at the last, not the two omissions the number is argued against growing
past negligible over the span; shortening would not take the tail out of
them, extending would add the late excess. Ratified by the project owner on
2026-09-27 ("Agree with recs. Merge"), over shortening or extending the span
on the measured departures; the record carries it as ratified.

**Caveats the record carries, so the numbers are not read sharper than they
are.** The mean-coefficient curve runs 0.33-1.84 published SD (3.5-24%) above
the measured five-minute means of the same cohorts, so every ratio understates
the model against the volunteers' mean; the fourth compartment's amplitude SD
is 59-112% of its mean, so the middle-stretch shortfall is known to about a
factor of two; nitrous oxide and parameter lineage as in the gate.

**Filed from this work:** `PL-95NW`, a test of whether the model's slower
muscle return explains the open-circuit tail's closest approach over hours 2
to 4, an inference the record marks as untested.
