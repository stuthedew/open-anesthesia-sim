---
id: PL-MXTY
title: triage.md says `docket check` promotes a milestone-blocked item once the milestone is scoped, but check only advises and never writes a status, so a reader of the triage mode can believe promotion is automatic and leave the item blocked
priority: P3
effort: S
status: done
classes: docs
feature: blocked-means-blocked
milestone: v0.5.23
touches: .claude/skills/docket/modes/triage.md
added: 2026-10-11
closed: 2026-10-12
pr: 1427
payoff: a reader of the triage mode learns that a milestone-blocked item is promoted by a session reading it, not by docket check, so it is not left blocked waiting for a promotion nothing performs
verify: grep -qF 'advises that it is ready to promote' .claude/skills/docket/modes/triage.md
---

**Problem.** triage.md says `docket check` promotes a milestone-blocked item once the milestone is scoped, but check only advises and never writes a status, so a reader of the triage mode can believe promotion is automatic and leave the item blocked

**Where.** `.claude/skills/docket/modes/triage.md`, the paragraph opening
"Except where the decision is a milestone being scoped": "`docket check`
promotes it once that section carries its four subsections". The code that
sentence describes is the milestone branch of the "ready to promote" walk in
`subprojects/docket/src/docket/checks.py`, which appends an advisory ("... is
scoped and every other blocker has closed; it is ready to promote") and writes
nothing. No command writes `status: ready` on an item's behalf, by design:
`plan.promotable`'s docstring carries the 6-of-13 count that settled it, and
`PL-162Y` (dropped) declined to have `next` name milestone-cleared items too,
so for this shape the check advisory is the only signal.

**Found** 2026-10-11 answering the owner's question "does triage promote
these, or how do they get promoted once blockers are resolved?" - the sentence
gives exactly the wrong answer to it.

**Done when.** The sentence says `docket check` *advises* that the item is
ready to promote, and that a session promotes it with `bin/docket set <id>
--status ready` after reading it against the tree - one word and one clause.

**Generator check.** An instance of `PL-G424`'s fact - the link between a
document sentence and the tree fact it restates - whose head is closed and
recorded spent; one more instance does not make it live, and the sentence is
repaired where it stands.

**Fixed 2026-10-12, riding `PL-2349`**, which edits the same paragraph of
`.claude/skills/docket/modes/triage.md`: the sentence now says `docket check`
*advises* that a milestone-blocked item is ready to promote and that a session
promotes it with `bin/docket set <id> --status ready` after reading it against
the tree, and adds that an item blocker is stricter - `check` refuses the item
left `blocked` once every one has closed.
