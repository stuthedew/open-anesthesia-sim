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

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "The refilling-queue ground". This item is also named in paragraphs quoted in the brief of `PL-J3TV`. The paragraph that disposed of it counts it among its entries without naming it, and is quoted in `PL-0QQP`'s brief.

> - PL-8T3Z (S) PL-K2C8's touches omits .claude/hooks/no-prune-guard.sh, which carries the same incomplete recovery recipe, and its Where sends a fix at PL-CPLD which is now dropped — dropped 2026-09-21
