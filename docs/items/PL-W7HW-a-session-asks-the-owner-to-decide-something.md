---
id: PL-W7HW
title: A session asks the owner to decide something without first researching current best practice, where the owner wants the research done first so that a clear answer is taken without asking and any real question carries it
priority: P2
effort: S
status: done
classes: infra
feature: decision-ownership
milestone: v0.6.22
touches: .claude/rules/instruction-writing.md, .claude/skills/docket/modes/design.md, .claude/skills/docket/modes/triage.md, .claude/skills/docket/modes/coordinator.md, docs/maintainer.md, docs/resident-instructions.md, subprojects/docket/src/docket/arming.py
added: 2026-11-22
closed: 2026-11-22
pr: 2251
payoff: the owner is asked only what research cannot settle, and every question reaches the owner with the published evidence and a recommendation drawn from it
verify: grep -qF 'Research best practice before asking' .claude/rules/instruction-writing.md
---

**Problem.** A session asks the owner to decide something without first researching current best practice, where the owner wants the research done first so that a clear answer is taken without asking and any real question carries it

**Asked for by the project owner on 2026-11-22**, in the project thread
"Research best practice before any owner ask": "Whenever it asks for me to
decide something make sure it researches best practice first to either find a
clear choice that doesn't need me or to better inform the recommendation. Make
this repo wide". Earlier the same day the owner had answered several asks in a row
with "follow best practice" and "whatever is best practice", and then "For
items that need me, research best practice for all".

**Why it matters.** `CLAUDE.md` § "Proactive expert review and domain best
practices" already says to consult the source before forming a
recommendation. Nothing said that a question to the owner must wait for that
research, or that research which settles the question removes the question.
So sessions kept putting questions to the owner that a published standard already
answered, and the owner answered them by pointing back at best practice.

**Where the rule lives.** Rule 10 of `.claude/rules/instruction-writing.md`,
which already decides what every question, card and read ask to the owner
must carry. A question can be written in any reply, which no read of a file
precedes, so a path-scoped rule or a skill would load too late; rule 10 is
resident. The places that produce asks point at it rather than restating it:
the design round's steps, triage's paragraph on writing a recommendation into
a brief, the coordinator's reporting rules, `bin/docket arm`'s instructions
for an `Owner-ask:` record, and `docs/maintainer.md`'s description of that
record. `docs/resident-instructions.md` records the move.

**Not built: a check that an `Owner-ask:` record names a source.** Whether
research was done well is judgment, and a required field would be met by a
token citation. The record's `checked` part already carries what was checked,
and the instructions now say the research goes there.

**Generator check.** A one-off: an instruction the owner gave in their own
words, not a fact that a reader misread.

**Done when.** Rule 10 holds the research step, each place above points at
it, and `make check` passes.

**Docs checked 2026-11-22.** Read for statements this change makes untrue:
`CLAUDE.md` § "Working with the project owner" and § "Proactive expert review
and domain best practices", rules 10 and 14 of
`.claude/rules/instruction-writing.md`, `.claude/skills/docket/modes/design.md`,
`.claude/skills/docket/modes/triage.md` § "Mode: triage",
`.claude/skills/docket/modes/coordinator.md` § "Reporting to the owner",
`.claude/skills/pull-request/SKILL.md`'s paragraph on asking the owner,
`docs/maintainer.md`'s description of the `Owner-ask:` record, and `READ_ASK`
in `subprojects/docket/src/docket/arming.py`. None needed more than the
pointers this change adds.
