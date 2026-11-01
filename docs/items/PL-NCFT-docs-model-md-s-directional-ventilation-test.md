---
id: PL-NCFT
title: docs/MODEL.md's Directional ventilation test requires a faster approach of F_A toward F_I, but test_higher_ventilation_increases_early_alveolar_fraction asserts only that F_A is higher at 30 s
priority: P2
effort: S
status: done
classes: test, docs
feature: invariant-test-gaps
touches: docs/MODEL.md, tests/reference/test_sevo_patient.py
added: 2026-09-19
closed: 2026-11-01
pr: 1913
verify: grep -q 'def test_higher_ventilation_closes_the_alveolar_to_inspired_gap_faster' tests/reference/test_sevo_patient.py
---

**Problem.** docs/MODEL.md's Directional ventilation test requires a faster approach of F_A toward F_I, but test_higher_ventilation_increases_early_alveolar_fraction asserts only that F_A is higher at 30 s

**Where.** `docs/MODEL.md` § "Required tests", the "Directional ventilation
test" subsection: "With otherwise identical conditions, increasing alveolar
ventilation must accelerate the approach of F_A toward F_I." The test that
stands for it, `test_higher_ventilation_increases_early_alveolar_fraction` in
`tests/reference/test_sevo_patient.py`, runs two systems for 30 s at 2 and
8 L/min and asserts that the higher-ventilation alveolar partial-pressure
fraction is the greater. It never reads F_I and never forms the approach the
specification names.

**Why it matters.** Under a rebreathing circuit F_I itself moves with
ventilation, so "F_A is higher" and "F_A approaches F_I faster" are not the
same claim; the second is the one the specification makes and the one a reader
of the F_A/F_I trace relies on. Found 2026-09-19 by `PL-4FBP`'s measurement of
the 38 required statements against `tests/`: one of the two held partially.

**Done when.** Either the test asserts the specified quantity - the F_A/F_I
ratio, or the gap between F_I and F_A, closing faster at the higher ventilation
over the same horizon - or the specification is narrowed to what the test
asserts, with the reason written beside it; and the annotation pass
(`PL-2M9N`) names the test beside the heading.

**Resolution, 2026-11-01.** The test now asserts the specified quantity. It is
renamed `test_higher_ventilation_closes_the_alveolar_to_inspired_gap_faster`
and requires F_A/F_I to be higher at 8 than at 2 L/min at every whole second
of the first minute of the default sevoflurane wash-in. It keeps the old
assertion that F_A itself is higher at 30 s. Measured 2026-11-01: F_A/F_I is
0.155 against 0.460 at 30 s and 0.248 against 0.605 at 60 s, while F_I itself
is lower at 8 L/min (0.0047 against 0.0053 at 30 s). Because F_I differs
between the two runs, F_A alone does not measure the approach to F_I. `docs/MODEL.md` names the test beside the
heading and says why it compares the ratio.
