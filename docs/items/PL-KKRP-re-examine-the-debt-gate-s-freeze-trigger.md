---
id: PL-KKRP
title: Re-examine the debt gate's freeze trigger: scoping a milestone has not frozen its gate for the last two milestones scoped, so the cadence's beat 1 no longer describes what the project does
status: needs-decision
added: 2026-09-16
priority: P2
effort: M
classes: planning
touches: ROADMAP.md, .claude/skills/docket/SKILL.md
---

**Problem.** Re-examine the debt gate's freeze trigger: scoping a milestone has not frozen its gate for the last two milestones scoped, so the cadence's beat 1 no longer describes what the project does

**Why it matters.** `ROADMAP.md` § "The debt gate" -> "The cadence" beat 1 says
"Scoping is the act that freezes the list", and that has not described the last
two milestones this project scoped. v0.4.26 took no gate by its own exception,
and v0.6.0 took one on 2026-09-16 because it was scoped two releases out of turn
and freezing Gate 2 on the day would have produced a gate holding none of
v0.5.0's findings. Two exceptions in a row is a fact about the trigger rather
than about the two milestones.

**Decision needed.** Whether beat 1's trigger should read "the gate freezes
when the preceding milestone ships" - which is what has actually happened both
times and what the timeline already encodes - or whether the rule stands with
exceptions recorded against it. The second is what is written today. This is the
project owner's, because it is a change to how the project's own cadence works
rather than a fact about the tree.

**Why it was not settled in the session that needed it.** A rule excepted twice
wants re-examining deliberately, not amending in passing by the session whose
work depends on the second exception.

**Done when.** § "The cadence" states one trigger that describes what the
project does, the recorded exceptions are folded into it or kept as exceptions
deliberately, and `.claude/skills/docket/SKILL.md`'s freeze-a-gate mode agrees
with it.

## Design round 2026-10-03: what the timeline already encodes

Read against `ROADMAP.md` on origin/main at v0.5.22:

- Gate 1 froze 2026-09-06, the day v0.5.0 was scoped; v0.4.0 had shipped the day before (tag `v0.4.0`, 2026-09-05). The scoping day was also the first day its predecessor had shipped.
- Gate 2 froze 2026-09-21, the day v0.5.0 shipped, five days after v0.6.0 was scoped out of turn on 2026-09-16 - the exception § "The cadence" records (project owner, 2026-09-16, ratified).
- Timeline rows 8 and 10 already read "Frozen when v0.6.0 ships" and "Frozen when v0.7.0 ships" for Gates 3 and 4. v0.7.0 and v0.8.0 have timeline rows and no sections yet, so whenever they are scoped their gates freeze on the ship trigger too.

So every gate still to freeze is written on the ship trigger, and beat 1's "Scoping is the act that freezes the list" describes none of them. The two triggers are not alternatives, either. A list frozen before its predecessor ships holds none of that milestone's findings, which is the exception's own reasoning; a list frozen before the milestone is scoped has no section to be recorded in. Both gates this project has frozen under the rule froze on the *later* of the two days: Gate 1 because scoping came second, Gate 2 because shipping did. v0.4.26 is not a third case for either reading - it was a patch on the `v0.4.x` track, which freezes no gate by the cadence's own terms, so it says patches do not gate and nothing about this trigger.

**Recommendation: rewrite beat 1's trigger as the conjunction the project has actually followed - the list freezes when the milestone is scoped and the milestone before it has shipped, on the later of those two days - and fold the 2026-09-16 exception into it as the instance that showed the rule's shape.** Concretely: beat 1 keeps "Scope the milestone here" and loses "Scoping is the act that freezes the list"; beat 2 gains the trigger sentence; the paragraphs headed "The exception, and why it is the rule's purpose" and "Twice in a row now" become one dated paragraph of history citing this item; "A milestone whose gate has not been recorded has not been scoped" becomes "a scoped milestone carries its gate heading from the day it is scoped, empty until the freeze"; and `.claude/skills/docket/modes/release.md`'s freeze mode (lines 9-22) states the same trigger in one sentence instead of a rule with an exception. `bin/docket wave` reads the timeline rows and the "Debt gate" subsection headings, not the beat's wording (`subprojects/docket/src/docket/roadmap.py`, `GATE_SUBSECTION`), so no tool changes. Cost: about fifteen lines of prose across the two files this item already declares, one pull request.

The alternative the brief names, keeping "scoping freezes the list" with exceptions recorded against it, would make every remaining gate an exception to its own rule, which is the state this item was filed to end. Reopening the 2026-09-16 decision is on ordinary evidence: it was ratified, and the evidence is that the timeline has since been written the other way for every gate ahead.
