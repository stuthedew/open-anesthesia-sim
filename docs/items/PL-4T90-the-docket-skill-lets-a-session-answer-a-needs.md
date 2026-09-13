---
id: PL-4T90
title: The docket skill lets a session answer a needs-decision item whose answer is direction rather than fact, and PL-8GV5 was closed on a session's own reasoning as a result
status: done
priority: P2
effort: S
classes: docs, session-cost
feature: delegation
touches: .claude/skills/docket/SKILL.md
added: 2026-09-13
closed: 2026-09-13
verify: grep -qF 'never whose' .claude/skills/docket/SKILL.md
---

**Problem.** `.claude/skills/docket/SKILL.md` separated `needs-decision` items
into two kinds and neither covers the one that matters here. It said a question
"this project can answer" is `needs-decision` and countable debt, and a
milestone not yet scoped is `blocked-by: <version>`. A session reading that and
picking a `needs-decision` item off `bin/docket next` has been told the item is
resolvable and nothing has told it *by whom*.

**What it cost.** `PL-8GV5` asked whether `ROADMAP.md` should carry a line of
intent for a dose-dependent haemodynamic response. A session measured the human
volunteer literature, found the dose-response non-monotonic and
carrier-gas-dependent, and closed the item as "do not model it, and carry no
roadmap line". The measurement was sound and was a session's to make. The
disposition - whether a feature enters the roadmap - is direction, and
`CLAUDE.md` assigns it: "The division of labour is theirs to set direction and
yours to make it real." The project owner caught it in the same session and
answered differently: not now, but kept on the roadmap as an option a user
turns on. That is a different project from the one the session recorded, and a
better answer, because an option can state its own uncertainty where a default
cannot.

**Why the status is the trap rather than the session.** Three things point the
same way at once: `needs-decision` reads as an invitation, `bin/docket next`
ranks such items first (`PL-JW39`), and `bin/docket gate` counts them as debt a
session is supposed to clear. Nothing in that path distinguishes a question
settled by evidence from one settled by preference. Both of the other three
items in the same batch - `PL-74R0` and `PL-79YX` - *were* a session's, and
were settled by measurement against briefs that expected argument, so a rule
that told sessions to stop at every `needs-decision` item would be wrong in the
common case.

**Fixed in the same session**, per `CLAUDE.md`'s rule that a behaviour change
takes effect in the session that asks for it. The `docket` skill's
`needs-decision` block gains a third case and a sorting test: sort by *what the
answer rests on*, not by how hard the item looks. Code, a measurement, or a
rule the repository already states - a session's. What the project is for - the
owner's. Most items are both, and the half that does not depend on the answer
is done and reported while the direction half goes in the reply with a
recommendation and the item stays open.

**Not scripted, deliberately.** Which side an item falls on is a judgement
about its content, which is exactly the half `CLAUDE.md` forbids scripting: a
checker guessing at it would be authoritative and wrong. What *could* be
mechanical - a `decided-by: owner` field, or a `docket check` rule that a
`planning`-classed item may not close without one - is a candidate, not a
conclusion, and is not built here. `PL-8GV5` carried `classes: planning, docs`
and that class was visible the whole time, which is weak evidence the signal
already exists; one instance is not enough to design a check around.

**Where.** `.claude/skills/docket/SKILL.md`, the `needs-decision` block under
"Mode: triage".

**Done when.** The skill distinguishes a decision a session may take from one
only the project owner may, on what the answer rests on rather than on the
item's difficulty, and names `PL-8GV5` as the instance. Done in the same
session this was found.

**Found.** 2026-09-13, by the project owner, on the reply closing `PL-8GV5`:
"that seems like a me decision?"
