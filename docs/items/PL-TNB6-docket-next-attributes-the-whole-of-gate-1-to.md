---
id: PL-TNB6
title: docket next attributes the whole of Gate 1 to the v0.4.x step, where the plan makes Gate 1 its own row that no patch may ship
status: untriaged
added: 2026-09-06
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
