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
