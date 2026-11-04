---
id: PL-PHP4
title: The paused docs/MODEL.md rewrite of the step-refinement test says the three runs agree to better than one part in a trillion without saying that this shows only that the time step is short enough, so a clinician can read it as the model matching patients
priority: P2
effort: S
status: done
classes: docs
feature: prose-quality
milestone: v0.6.15
touches: docs/MODEL.md, tests/reference/test_sevo_patient.py
added: 2026-11-03
closed: 2026-11-03
pr: 1950
payoff: a reader of the step-refinement test learns it shows only that the time step is short enough, and a developer gets a measured figure for an approximate method's gaps
verify: sh -c '! grep -n 1.4e-11 docs/MODEL.md tests/reference/test_sevo_patient.py && grep -n "does not show that the model" docs/MODEL.md'
---

**Problem.** The drafts of `docs/MODEL.md` § "Step-refinement test" that
`PL-70B2` wrote on 2026-11-02 (#1950, paused with `PL-ZT47`) end the main
paragraph with "The current method's runs agree to better than one part in a
trillion (measured 2026-10-03)". The paragraph never says what that agreement
shows. It shows that the 0.1 s time step is short enough for the equations to
be solved accurately, which is verification. It does not show that the
equations match a patient, which is validation. A clinician reading "agree to
one part in a trillion" in a section about a release check can take it as a
claim about the model's accuracy for patients.

The fresh reviewer that ran the prose review's test set on 2026-11-03 raised
this, in `docs/prose-review/runs/2026-11-03T015621Z.json` (`PL-CWRZ`). The
same reply also could not tell whether the draft's 1.4e-11 and 1e-14 are
relative or absolute gaps. The paragraph on main at about line 4548 gives
1.4e-11 for a first-order method and calls 1e-14 the gate's bound, so the
resumed rewrite should say which each is.

**Why it matters.** `CLAUDE.md`'s safety-critical standard asks that
displayed values and their documentation not imply more certainty than the
model supports, and `.claude/rules/expert-review.md` asks that verification be
kept apart from validation.

**Done when.** The step-refinement section of `docs/MODEL.md`, as the resumed
rewrite leaves it, says in one sentence that the test shows only that the
time step is short enough, and not that the model matches patients. It also
says whether each of 1.4e-11 and 1e-14 is a relative or an absolute gap.

**Found while fixing it, 2026-11-03: the 1.4e-11 was wrong.** Both figures
are absolute gaps in fraction. The 1.4e-11 that `docs/MODEL.md` and the
comment on `STEP_REFINEMENT_SETTLED_GAP` gave for "a first-order method" has
no record behind it. It entered with the exact step (#376, `d8deea50`) with no
measurement, and it contradicts the record beside it: the operator split, a
first-order method, left the mixed-venous fraction 1.4e-6 apart between 0.1 s
and 0.025 s. Euler's method on the same equations, using `_build_derivative`
from `tests/reference/test_coupled_dynamics.py` at its default operating
point (5% sevoflurane, 4 L/min fresh gas, 4 L/min ventilation, 5 L/min
cardiac output), gives these successive-halving gaps after 60 s:

| Fraction | 0.1 s vs 0.05 s | 0.05 s vs 0.025 s | First gap, relative |
| --- | --- | --- | --- |
| alveolar | 1.77e-6 | 8.83e-7 | 0.021% |
| mixed venous | 8.52e-7 | 4.25e-7 | 0.150% |
| vessel-rich | 9.59e-7 | 4.79e-7 | 0.078% |

So the rewrite says "up to 1.8e-6" for Euler's method, and the margin of the
1e-14 bound is more than eight orders of magnitude, not three. The script was
a 15-line loop of `s = s + h * derivative(s)` from an empty state, run with
`uv run python` from the repository root.

**Generator check.** Not a generator. The missing verification sentence is
one instance of `PL-H76S`'s prose failure, which is spent (#1962). The wrong
1.4e-11 is a single unrecorded figure, copied once from the specification
into the test comment, and no other figure in the section lacks a record.
