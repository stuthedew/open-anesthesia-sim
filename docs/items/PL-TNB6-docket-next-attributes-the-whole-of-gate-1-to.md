---
id: PL-TNB6
title: docket next attributes the whole of Gate 1 to the v0.4.x step, where the plan makes Gate 1 its own row that no patch may ship
priority: P2
effort: S
status: done
classes: defect, infra
feature: planning-cadence
milestone: v0.4.24
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/tests/test_plan.py, subprojects/docket/tests/test_cli.py
added: 2026-09-06
closed: 2026-09-14
pr: 560
verify: uv run pytest subprojects/docket/tests/test_plan.py && grep -q 'def test_the_gate_reason_says_which_step_is_current_not_which_clears_the_gate' subprojects/docket/tests/test_plan.py
---

**Problem.** Every ranked item in `bin/docket next` now carries a placement
line of this shape:

```text
On the debt gate recorded under v0.5.0 - the case you can branch;
v0.4.x - the code is the model clears it.
```

Read as written, the second clause says the `v0.4.x` step clears Gate 1.
"The timeline" does not: row 3 is the `v0.4.x` track, row 4 is Gate 1, and
row 5 is v0.5.0, so the gate is a step of its own *after* the patch track.
Only 3 of the gate's 119 entries belong to the `v0.4.x` step; the other 116
clear before v0.5.0's implementation begins, and 9 of those are cleared by the
milestone itself.

**Why it matters.** "The cadence" says a gate does not get a version: cleared
gate work ships inside the milestone it gates, and `docket release` offering
one partway through is to be declined "or the gate work scatters across patch
releases and the milestone ships carrying only its feature work." A session
that reads this line as the plan's own answer would conclude the opposite -
that clearing the gate is the current patch track's job, and therefore that a
patch may carry it. That is a wrong answer given confidently by the command
every session opens with, on the one question the cadence exists to settle.

It became reachable on 2026-09-06, when Gate 1 was recorded; before that there
was no frozen gate for the line to attribute.

**What is not yet established.** Whether the clause means "the current step" and
is merely worded as though it means "the clearing step", or whether the
placement logic genuinely attributes a gate to the step it finds current. The
distinction decides whether this is a message fix or a reading fix, and it
wants someone to read the code rather than the output.

**Where.** Whatever builds the placement sentence for a ranked item -
`subprojects/docket/src/docket/` - and its tests. `ROADMAP.md` needs no change:
the timeline and "The cadence" already say what is true.

**Done when.** The line either names the step that actually clears the gate, or
says which step is current without implying it clears anything, and a test
pins whichever wording is chosen against a store with a frozen gate and a
current step that is not the gate.

**Closed 2026-09-14. It is a message fix, which is what the brief left open.**
`Scope.step_label` carries the row the project stands on and nothing else, and
`milestone_scope` attributes no gate to it: the label is passed in by `wave`
whenever the step's version differs from the gated milestone's, and the reading
underneath was already right. Only the sentence built from it was wrong.

**The second wording was taken.** The line now reads "On the debt gate recorded
under v0.5.0 — the case you can branch, which clears before that milestone is
implemented; the project stands on v0.4.x — the code is the model." Naming the
step that actually clears the gate was the other option and it cannot be built
from what `Scope` holds: the gate is a timeline row of its own, `Scope` carries
no row for it, and the milestone the gate is recorded under is already the
first clause. This says which step is current and leaves the clearing where
"The cadence" puts it.

The same claim was asserted twice — `test_plan.py` on the reason line and
`test_cli.py` end to end through `docket next` — so `tests/test_cli.py` joined
this item's `touches`. Both now assert the new wording and that "clears it"
appears nowhere in the output.
