---
id: PL-HGN6
title: The line between the owner's decisions and a session's is consequence, not what the answer rests on: a granular editorial choice is a session's even when it turns on what the project wants
priority: P2
effort: S
status: done
classes: infra
feature: decision-ownership
milestone: v0.4.28
touches: .claude/rules/instruction-writing.md, .claude/skills/docket/SKILL.md, docs/resident-instructions.md
added: 2026-09-19
closed: 2026-09-19
verify: python3 tools/doc_check.py check && grep -qF 'turns on consequence, not on what the' .claude/rules/instruction-writing.md
---

**Problem.** The line between the owner's decisions and a session's is consequence, not what the answer rests on: a granular editorial choice is a session's even when it turns on what the project wants

**Said by the project owner, 2026-09-19**, after a session closed `PL-HWW1`
and handed `PL-C4RS`'s remaining question back as a decision: "I'll say what
feature order I want or if we need to change big picture stuff, but granular
stuff, unless it's incredibly consequential, I don't care to comment on all
the time unless you have a very specific question for me."

**Why the instructions produced that reply.** Two places drew the line at
*what the answer rests on* rather than at consequence. The `docket` skill's
triage section said "Where the answer rests on what the project should *want*
- whether a feature enters `ROADMAP.md`, which of two defensible products this
is, **what a scope word means** - it is the project owner's", and rule 14 of
`.claude/rules/instruction-writing.md` gave three dispositions for a question
without saying which was which. `PL-C4RS`'s remaining half is literally what a
scope word means, so the session followed the rule and got the wrong answer:
the question was whether v0.5.0's `Required scope` should keep declaring two
ids a patch track had already cleared, whose blast radius is one section's
phrasing.

**The correction.** The test is consequence. Theirs are feature order, what
the project is for, behavior a learner would see, and anything the
safety-critical standard reaches. A choice whose options are all defensible
and whose blast radius is one document's phrasing, one internal structure or
one item's disposition is a session's - decided, stated in a line, and carried
on from. Resting on "what the project wants" does not by itself make a
question theirs.

**Where it went, and why not elsewhere.** Rule 14, because the moment it
governs is the closing block being written - a session choosing between
deciding and handing over, which happens after any skill has finished. The
skill's triage section was corrected to point at rule 14 rather than restate
it, since rule 14 is resident and reaches triage anyway; one rule in two
places is the drift the routing rule exists to stop.
`docs/resident-instructions.md` records the 199-character growth against the
test that file applies.

**Not routed to a check.** Nothing decidable is left once the rule is stated:
whether a consequence is large is the judgment, and a script that guessed at
it would be the "do not script the judgment" failure with an authoritative
voice.

**Done 2026-09-19, in the session that was told.** `CLAUDE.md`'s
behaviour-change rule: the capture is the record and the edit is the change,
and both land before the session ends. The instance that produced it,
`PL-C4RS`, was then decided rather than asked about - and the answer turned
out to be already recorded in `ROADMAP.md`, which is the sharpest form of the
finding: the session asked the owner for a decision they had taken on
2026-09-08 and written down.
