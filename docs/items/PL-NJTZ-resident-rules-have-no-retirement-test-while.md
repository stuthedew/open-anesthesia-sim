---
id: PL-NJTZ
title: Resident rules have no retirement test while checks do, so the resident set can only grow
priority: P2
effort: S
status: needs-decision
classes: session-cost, planning
touches: CLAUDE.md, docs/resident-instructions.md
added: 2026-09-05
---
**Problem, stated against the asymmetry.** `CLAUDE.md:205` gives checks a
retirement test: "**A check earns its place every run, or it is retired.** ... A
check that fires every run without changing a decision is a defect in the
check." Resident rules have no equivalent. What they have instead is a
protection against removal - `CLAUDE.md:299`, "never delete a rule for being
wordy" - and a refused ceiling. So the resident set can only grow.

**Measured.** 2026-09-01 to 2026-09-05, resident went 35,721 to 44,545
characters, +25% in five days. The one pass that ever removed anything
(`PL-JK0M`) took out 770 characters and was overtaken by the next commit, which
added 5,149 (`PL-WWDT`). `PL-4H01` finds only 563 further characters of
defensible routing, so routing is running an order of magnitude behind growth.

**Why the ceiling refusal does not answer this.**
`docs/resident-instructions.md` refused a numeric ceiling and the refusal is
right: "a limit is met by deleting a rule to reach a number, which is the one
outcome this pass must not produce, and no number the tool could hold would know
which rules a session must see before it reads anything."

That refusal addressed *ceilings*. It did not consider a **qualitative**
retirement test, which is what checks already get and rules do not. The shape
would mirror `CLAUDE.md:205` rather than impose a number: a resident rule whose
failure mode a check now catches, or which no session has violated since it was
written, is a retirement candidate. No number, no deleting-to-hit-a-target, and
the ledger's "never delete a rule for being wordy" stands untouched - wordiness
is still not a reason; obsolescence would be.

**Why it matters.** Every resident rule was added because a session got
something wrong once. Nothing ever asks whether that is still true. The cost is
paid by every session forever, and by the project's own evidence it is an
adherence cost rather than a context-rot one: at ~11,100 tokens against sessions
measured at 304k-436k, resident text is roughly 3% of context, but 408 lines
against Anthropic's documented 200-line target is where adherence degrades
("Bloated CLAUDE.md files cause Claude to ignore your actual instructions").

**Decision needed.** Whether to add a retirement test at all, and whether it
lives beside `CLAUDE.md:205`'s check-retirement wording or in
`docs/resident-instructions.md` as a rule for the ledger rather than for
sessions. The second costs no resident characters, which is the point.

**Done when.** A resident rule has a stated condition under which it is removed,
and the condition is not a character count.
