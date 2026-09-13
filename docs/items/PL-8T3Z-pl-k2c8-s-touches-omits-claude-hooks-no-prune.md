---
id: PL-8T3Z
title: PL-K2C8's touches omits .claude/hooks/no-prune-guard.sh, which carries the same incomplete recovery recipe, and its Where sends a fix at PL-CPLD which is now dropped
priority: P2
effort: S
status: ready
classes: defect, docs
feature: parallel-sessions
touches: docs/items/PL-K2C8-the-docket-skill-s-stranded-branch-recovery.md
added: 2026-09-12
verify: python3 tools/doc_check.py check && grep -q '^touches:.*no-prune-guard.sh' docs/items/PL-K2C8-the-docket-skill-s-stranded-branch-recovery.md
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
