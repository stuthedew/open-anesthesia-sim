---
id: PL-KK1Q
title: Compare this model's washout over the first 24 h against Yasuda 1991's published five-compartment mean fits, to measure whether the modelled tail runs fast or slow where only the five-minute point is validated today
priority: P1
effort: M
status: ready
classes: science, test
feature: late-washout-evidence
touches: tests/reference, docs/MODEL.md
added: 2026-09-26
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
