---
id: PL-JW39
title: docket next ranks a needs-decision item first, so every fresh session opens on work whose next step is the owner's answer
status: untriaged
added: 2026-09-06
---

**Problem.** `bin/docket next` sorts on band, roadmap placement and feature
progress, and does not consider `status`. So a `needs-decision` item outranks
every `ready` one below it and is offered as the thing to work on now.
Observed 2026-09-06: `PL-6Q8N` (the reference adult's eleven physiologic
parameters have no primary source at all) was moved `ready` to
`needs-decision` because its next step is the project owner's answer, and
`next` went on returning it as suggestion 1 of 3.

The status word is printed in the line - `(M, needs-decision, science-tagged)`
- so a session that reads it carefully is not misled. That is the whole of the
protection, and it sits inside a parenthesis alongside effort and class.

**Why it matters.** `next` is what a fresh session runs first, and its top
answer is the one that gets started. An item whose next step is a decision
cannot be worked by a session at all: the honest outcome is to read the brief,
find the open question and stop, which is a session's opening spent for
nothing. The queue holds 13 P1 items, so the cost is not that there was
nothing else to do.

**Not obviously a bug, which is why this is a question rather than a fix.** A
`needs-decision` item is a question for the project owner, and `bin/docket
gate` counting it is how the question reaches them; suppressing it from `next`
entirely could bury exactly the items that most need attention, and a session
running *with* the owner present can productively work one by answering it.
The defect, if there is one, is the unconditional first place rather than the
inclusion.

**Where.** `subprojects/docket/` - the ranking in the `next` command, and
whatever `docket next`'s output line does to make status legible.

**Done when.** Either `next` stops ranking a `needs-decision` item above
startable work, or it says in its reason line that the item's next step is a
decision rather than code - and the choice between those is recorded.
