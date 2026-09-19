---
id: PL-DLMM
title: Record the citation-drift decision as ratified rather than as a session's own: PL-G424 and .claude/rules/citation-drift.md both say the project owner did not take it, which is now false
priority: P2
effort: S
status: done
classes: docs
feature: generator-heads
milestone: v0.4.30
touches: .claude/rules/citation-drift.md, docs/items
added: 2026-09-19
closed: 2026-09-19
pr: 727
verify: grep -qF '(project owner, 2026-09-19, ratified, over extending the' .claude/rules/citation-drift.md
---

**Problem.** Record the citation-drift decision as ratified rather than as a session's own: PL-G424 and .claude/rules/citation-drift.md both say the project owner did not take it, which is now false

**Why it matters.** `CLAUDE.md` § "Working with the project owner" makes the
distinction load-bearing: a decision the owner **ratified** reopens on ordinary
evidence - a measurement, a cost the case did not carry, a constraint that has
since appeared - while one they **specified** needs a compelling argument. It
also says why the record is the only carrier: "the reply that put the case is
gone", so without the word written down a later session cannot tell a design
they authored from one they nodded at.

Both artifacts of `PL-G424` were written before the owner had answered, and both
said plainly that they had not: the rule read "(project owner's session,
2026-09-19)" and the item's `Decided` section opened "Taken by this session on
measurement, not by the project owner." Correct when written, false as of the
owner's "agree with recs" in the same sitting.

**What was recorded.** `(project owner, 2026-09-19, ratified, over extending the
live-versus-dated-assertion convention across the apparatus documents)` - the
clause names what it was chosen over, per the same rule - in
`.claude/rules/citation-drift.md`, with a paragraph stating the reopening bar,
and on `PL-G424`'s `Decided` section.

**This is not a closed brief being repaired, and the distinction matters** since
the rule this very item records is what forbids that. `PL-G424` is `done`, and
`.claude/rules/citation-drift.md` says drift in a closed brief is not a finding.
That clause is about a *citation to the tree* going stale underneath a sentence
nobody rewrote. This is the opposite: completing the provenance of the decision
the brief exists to record, which `CLAUDE.md` requires at the moment the answer
arrives. A later session meeting both should read the closed-brief clause as
covering tree facts, never as sealing a decision record against the decision
being taken.

**Found.** The sitting that closed `PL-G424`, 2026-09-19, on the owner's answer
arriving after the pull request had merged.

**Done when.** `.claude/rules/citation-drift.md` and `PL-G424`'s `Decided`
section both carry `(project owner, 2026-09-19, ratified, ...)` with the clause
naming what it was chosen over, and the rule states the reopening bar that
`ratified` carries, so a later session weighing evidence against it knows which
bar applies without leaving the file.
