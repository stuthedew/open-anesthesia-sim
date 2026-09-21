---
id: PL-8T3Z
title: PL-K2C8's touches omits .claude/hooks/no-prune-guard.sh, which carries the same incomplete recovery recipe, and its Where sends a fix at PL-CPLD which is now dropped
priority: P2
effort: S
status: dropped
classes: defect, docs
feature: parallel-sessions
touches: docs/items/PL-K2C8-the-docket-skill-s-stranded-branch-recovery.md
added: 2026-09-12
closed: 2026-09-21
reason: `.claude/rules/citation-drift.md`'s closed-brief clause reaches the deliverable as written. `PL-K2C8` is `done` - closed 2026-09-13, shipped v0.4.21 - so its `touches` field and its **Where** section are a historical record: no `bin/docket concurrent` answer reads a closed item's `touches`, and the **Where** pointing at the dropped `PL-CPLD` sends nobody anywhere because nobody will work the item. The live half underneath is not lost - it is `PL-J3TV` (the no-prune hook still prints the pre-`PL-K2C8` three-command restart recipe), filed 2026-09-21 and verified against the hook that day. Re-filed rather than narrowed in place because what survives is different work in a different file, which a title naming `PL-K2C8`'s `touches` would hide. Re-judged in `PL-PT7M`'s pass
---

**Problem.** PL-K2C8's touches omits .claude/hooks/no-prune-guard.sh, which carries the same incomplete recovery recipe, and its Where sends a fix at PL-CPLD which is now dropped

**Confirmed at triage, 2026-09-12.** `PL-K2C8` declares
`touches: .claude/skills/docket/SKILL.md, docs/items` and `PL-CPLD` is
`status: dropped`.

**Why it matters.** Two separate costs, and the first is the one that bites
twice. `touches` is what `bin/docket concurrent` reads, so an omission is a
collision nobody is warned about - and `.claude/hooks/no-prune-guard.sh` is
where `PL-G8TR` is working, which is the same three-item pile-up `PL-77SV`
describes. Worse, the hook prints the recovery recipe to a session at the moment
it is refused a prune, so a fix that corrects the skill and not the hook leaves
the incomplete recipe in the louder of the two places. Second, a `Where` section
pointing at a dropped item sends the next session to a file whose whole content
is the reason nobody should act on it.

**Done when.** `PL-K2C8`'s `touches` names `.claude/hooks/no-prune-guard.sh`,
and its `Where` points at the hook rather than at `PL-CPLD`.
