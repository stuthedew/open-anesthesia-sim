---
id: PL-PHP4
title: The paused docs/MODEL.md rewrite of the step-refinement test says the three runs agree to better than one part in a trillion without saying that this shows only that the time step is short enough, so a clinician can read it as the model matching patients
status: untriaged
added: 2026-11-03
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
