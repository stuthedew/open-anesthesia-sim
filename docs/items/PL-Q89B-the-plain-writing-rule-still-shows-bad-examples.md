---
id: PL-Q89B
title: The plain-writing rule still shows bad examples (point 2's stacked clause and a Before text for each of its three examples), which Anthropic's Sonnet 5 guide says work less well than positive examples
priority: P3
effort: S
status: done
classes: docs
feature: prose-quality
touches: .claude/rules/plain-writing.md
deferred-from: v0.7.0 - its problem is new since the freeze and no release schedules it, so it is deferred on the terms of § "Deferring to the next gate"; not safety or science
added: 2026-11-14
closed: 2026-11-14
pr: 2148
payoff: the writing rule shows a session only the version of each example to copy
verify: ! grep -q 'Do not stack clauses' .claude/rules/plain-writing.md && ! grep -q '^Before: ' .claude/rules/plain-writing.md && ! grep -q 'Too cryptic' .claude/rules/plain-writing.md
---

**Problem.** `.claude/rules/plain-writing.md` still shows bad examples. Point 2
quotes a stacked clause ("Each entry the plan was not read whole at") before
its fix, and § "Examples" gives a "Before" text for the `docs/MODEL.md`
paragraph, the docstring (two of them) and the pull request titles.
`PL-BFHK` restored the five machine-writing patterns without bad examples, on
the sources it records. The same sources apply to these.

**The source.** Anthropic, "Prompting Claude Sonnet 5", § "Response length and
verbosity", read 2026-11-14: "Positive examples showing how Claude can
communicate with the appropriate level of concision tend to be more effective
than negative examples or instructions that tell the model what not to do."
`PL-BFHK` gives the page's address.

**Question for the owner.** Keep only the good text of each example, and drop
each "Before" and point 2's bad sentence?

**Recommendation.** Yes. Keep each "After" text, and keep the pull request
title example's "Plain" version with the reason it is plain. It is the
owner's call because the owner accepted these examples in `PL-ZDZ0` and
`PL-J1ZM`.

**Answer** (project owner, 2026-11-14, ratified, over keeping the
before-and-after pairs): drop the bad versions. Done on `PL-BFHK`'s branch.
Point 2 now shows only the clause written well. Each example keeps its good
text, and the pull request title example keeps only the title the owner
chose. Point 3's word pairs ("returns", not "answers") stay: they name the
private sense to replace, which the card did not ask about.

**Generator check.** One-off, the second half of `PL-BFHK`.
