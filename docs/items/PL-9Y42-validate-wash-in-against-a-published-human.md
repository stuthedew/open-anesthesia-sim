---
id: PL-9Y42
title: Validate wash-in against a published human measurement
priority: P1
effort: S
status: done
classes: science
feature: numerical-domain
milestone: v0.2.9
touches: tests/reference/test_published_wash_in.py, docs/MODEL.md, README.md
added: 2026-08-30
closed: 2026-09-02
pr: 182
verify: uv run pytest tests/reference/test_published_wash_in.py
---

**Problem.** Nothing in this repository has ever been compared to a published
human measurement. Every test in `tests/reference/` checks the implementation
against itself: an analytic exponential, an RK4 oracle of the project's own
equations, mass balance, equilibrium, the zero-flow limit, directional
ordering. All of that is *verification* — the implementation solves the
intended equations correctly. None of it is *validation* — that the equations
represent the phenomenon. `CLAUDE.md` requires validating "against published
reference cases, analytic solutions, independently calculated test vectors, or
other authoritative references whenever available", and for inhaled-agent
wash-in they are available.

**Why it matters.** A model can be numerically flawless and physiologically
wrong, and this suite would report the first as though it settled the second.
The gap is also a claim the project already makes: `README.md:21` describes
"validated, cited partition data", which today rests on the provenance of the
inputs rather than on any test of the output.

**Measured.** At the shipped reference-adult defaults the model gives F_A/F_I
at 30 minutes of 0.853 sevoflurane, 0.741 isoflurane, 0.908 desflurane, against
Yasuda et al. 1991 measuring 0.850 +/- 0.018, 0.733 +/- 0.027 and
0.90 +/- 0.01 respectively — all three within one standard deviation.

- Yasuda N, Lockhart SH, Eger EI 2nd, et al. *Comparison of kinetics of
  sevoflurane and isoflurane in humans.* Anesth Analg 1991;72:316-24.
  PMID 1994760.
- Yasuda N, Lockhart SH, Eger EI 2nd, et al. *Kinetics of desflurane,
  isoflurane, and halothane in humans.* Anesthesiology 1991;74:489-98.
  PMID 2001028.

**Where.** New `tests/reference/test_published_wash_in.py`; `docs/MODEL.md`
"Required tests" and the release gate at `:1351-1368`; `README.md:21`.

**Approach.** Pin all three agents against the published means and SDs, with
the operating point pinned at alveolar ventilation 4.0 L/min and a comment
stating why: the agreement is ventilation-sensitive, holding across
3.5-4.0 L/min and breaking by 5.0. Pinning the point without saying so would
make a later reader think the tolerance is the model's rather than the
scenario's.

Record it in `docs/MODEL.md` under "Required tests" as **validation**,
explicitly distinguished from the "Independent-solution test", which is
verification — the two answer different questions and a reader who conflates
them over-reads both. Add it to the release gate at `:1351-1368` so it cannot
quietly stop running.

**Relation to other items.** PL-ZRSP (plot the F_A/F_I ratio the uptake
literature plots) is complementary rather than overlapping: it *displays* the
ratio, this proves the ratio is right. Land this first, so the curve is
known-correct before it is shown. PL-ZRSP also establishes that F_I is the
modelled circuit concentration rather than the vaporizer dial, which is the
definition this test's measurement uses.


**Appended 2026-09-01 — how independent this validation actually is.** An
external review re-ran the shipped core (`RespiratorySystem.for_agent`, fresh
gas flow 10 L/min so circuit ≈ inspired, delivered fraction 0.01,
reference-adult defaults V_A 4.0 L/min and Q 5.0 L/min, dt 0.1 s, 1800 s) and
reproduced the **Measured.** figures above. Expressed as distance from the
published mean, computed from the review's own numbers:

| Agent | Model | Published (mean ± SD) | Distance |
| --- | --- | --- | --- |
| Sevoflurane | 0.853 | 0.850 ± 0.018 | +0.17 SD |
| Isoflurane | 0.741 | 0.733 ± 0.027 | +0.30 SD |
| Desflurane | 0.908 | 0.900 ± 0.010 | +0.80 SD |

The ventilation sensitivity the **Approach.** already asserts now has numbers
on both sides: at V_A 5.0 the model reads 0.879 / 0.783 / 0.925 (+1.6, +1.9,
+2.5 SD) and at V_A 3.0 it reads 0.812 / 0.680 / 0.880 (−2.1, −2.0, −2.0 SD).
The window that holds is narrow, and 4.0 L/min is the data file's own cited
default rather than a value fitted to make this pass — which is the fact that
makes the agreement worth anything.

**Two caveats the test and its `docs/MODEL.md` entry must carry.** Both bear
on how strongly the result may be stated, and neither is currently anywhere in
this item:

1. **The published subjects were breathing nitrous oxide.** Yasuda's protocols
   administered 65–70% N₂O concurrently, so the measured F_A/F_I curves
   include a second-gas effect this model cannot reproduce — its alveolus is
   fixed-volume and single-gas. The comparison is therefore not perfectly
   matched, and in a direction that is not obviously conservative.
2. **These are Gas Man parameters, derived to reproduce Eger's data.** The
   partition coefficients under test come from the same lineage as the
   measurements being tested against, so passing shows that this
   implementation reproduces its parameter set's intent — not that the
   parameter set is independently right. It could still have failed, which is
   why the test is worth having; it is weaker than "validated against a human
   measurement" and the wording must not claim more.

Both caveats belong in the test's docstring and in the `docs/MODEL.md`
"Required tests" entry, beside the existing verification-versus-validation
distinction. Overstating independence here would be a documentation defect of
exactly the kind that section exists to prevent.

Citations for the two papers, with DOIs, for the record the item already
carries by PMID: Anesth Analg 1991;72:316-24, PMID 1994760,
doi:10.1213/00000539-199103000-00007 (n=7); Anesthesiology 1991;74:489-98,
PMID 2001028, doi:10.1097/00000542-199103000-00017 (n=8).

**Done when.** `tests/reference/test_published_wash_in.py` pins the three
30-minute F_A/F_I values against the published means and SDs with the
ventilation point and its sensitivity documented in the test,
`docs/MODEL.md` records the two citations and names this as validation as
distinct from verification, the release gate lists it, and `README.md:21`'s
validation claim is one the suite supports.
