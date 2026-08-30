---
id: PL-9Y42
title: Validate wash-in against a published human measurement
priority: P1
effort: S
status: ready
classes: science
feature: numerical-domain
touches: tests/reference/test_published_wash_in.py, docs/MODEL.md, README.md
added: 2026-08-30
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

**Done when.** `tests/reference/test_published_wash_in.py` pins the three
30-minute F_A/F_I values against the published means and SDs with the
ventilation point and its sensitivity documented in the test,
`docs/MODEL.md` records the two citations and names this as validation as
distinct from verification, the release gate lists it, and `README.md:21`'s
validation claim is one the suite supports.
