---
id: PL-YBWT
title: The off-scale notice's rationale calls 8% sevoflurane the standard induction setting, which overstates it
priority: P3
effort: S
status: done
classes: defect
feature: teachable-case
milestone: v0.4.0
touches: src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py, docs/MODEL.md
added: 2026-09-04
closed: 2026-09-04
pr: 321
verify: python3 tools/doc_check.py check && grep -qF 'is a common inhalational-induction setting' docs/MODEL.md
---

**Problem.** `PL-CC23` justified the off-scale notice - the line naming a
compartment trace drawn above the top of the chart - by observing that
sevoflurane's 8 % dial is 4.00 MAC and so exceeds the fixed 3 MAC ceiling.
It described 8 % as "the standard inhalational-induction setting", in
`docs/MODEL.md`, in two source comments, in a docstring and in a test
docstring.

**Why it matters.** "Standard" asserts a practice norm. 8 % sevoflurane is
common - it is what a vaporizer's dial maximum is reached for, and it is what
makes the off-scale case a real one rather than a contrived one - but calling
it *the standard* claims more than the evidence in this repository supports,
and none of the five statements carried a citation. Every other clinical
number in this change traces to an agent file's own cited provenance, which
is the standard `docs/MODEL.md` holds itself to; this sentence did not, and it
is the sentence doing the load-bearing work for why a clipped trace matters.

The consequence is small and the principle is not. `CLAUDE.md` treats a
displayed or documented clinical claim as safety-critical because a reader may
act on it, and an unsourced practice norm in the authoritative model
specification is exactly the kind of statement a reader would take on trust.

**Resolution.** Reworded to "a common inhalational-induction setting"
throughout, and the surrounding framing from "a technique rather than an edge
case" to "in common use rather than an edge case" (project owner, 2026-09-04:
"I would describe 8% as common. Not necessarily standard"). The argument the
sentence exists to make is unaffected - a setting in common use is already
enough to make the off-scale case worth handling - so nothing downstream of it
changed, and no test assertion moved.

**Done when.** No statement in `src/`, `tests/` or `docs/` calls 8 %
sevoflurane the standard induction setting.
