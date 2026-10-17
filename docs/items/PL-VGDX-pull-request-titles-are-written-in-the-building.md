---
id: PL-VGDX
title: Pull request titles are written in the building session's own vocabulary, such as "give the first CI part 2 of every 5 ordinary tests", so the owner cannot tell from a title what will change once it merges
priority: P2
effort: S
status: ready
classes: docs
feature: prose-quality
touches: .claude/rules/plain-writing.md, .claude/skills/docket/modes/start.md, docs/resident-instructions.md
added: 2026-10-17
payoff: a pull request's title says in everyday words what will be different once it merges, so the owner can tell what a pull request does without opening it
verify: grep -q 'A pull request title says what will change once it merges' .claude/rules/plain-writing.md && grep -q 'give the first CI part 2 of every 5' .claude/rules/plain-writing.md && grep -q 'per `.claude/rules/plain-writing.md`' .claude/skills/docket/modes/start.md && grep -q 'Pull request titles, added 2026-10-17' docs/resident-instructions.md
---

**Problem.** Pull request titles are written in the building session's own vocabulary, such as "give the first CI part 2 of every 5 ordinary tests", so the owner cannot tell from a title what will change once it merges

The project owner raised it on 2026-10-17: "Going along with awkward and
unclear wording. The PR titles often dont make much sense. For example: PL-ZWQS:
give the first CI part 2 of every 5 ordinary tests." The session on that pull
request retitled it when he pointed it out, so the work here is the rule for
titles written from now on.

**Cause.** Three places touch a title, and none says what the words after the
ids should be. `tools/pr_title_check.py` requires only that the ids it closes
lead, and its docstring says judging the prose is not its business. The
`docket` skill's start mode said only that the title carries the id.
`.claude/rules/plain-writing.md` named commit messages and pull request bodies
but not titles. So a session writes the title last, from its own working
vocabulary or from the item's title, which `picking.md` says is written for
the implementing session and names a mechanism.

**Calibration from the owner.** `#1523`'s title went through three versions on
2026-10-17. The owner pointed at the first as unclear. Of the two rewrites, he
judged "make CI's two test jobs finish at about the same time" a little too
conversational and the latest, "rebalance the CI test split to offset part 1's
lint steps", as the example to follow. So the target is a terse phrase that
names the change, what it changes and why, in names a reader knows. It is not
the item's `payoff:` sentence, which describes the effect.

**Why it matters.** A pull request title becomes the squash subject on `main`
and is how the owner tells pull requests apart in GitHub and in the
coordinator's reports. A title only its author can read makes the owner open
the pull request to learn what it does.

**Approach.** Extend the existing plain-writing rule rather than add a second
one: it is resident, so it applies at the moment a title is written, which no
read precedes. It gains one paragraph on titles and the owner's three judged
versions as examples, and the start mode's title bullet points at it. No
check: whether a title is plain is the judgment half that `CLAUDE.md` refuses to script, and
the blind ratings behind `PL-8ZTQ` found no cheap count that separates plain
prose from awkward.

**Done when.** `.claude/rules/plain-writing.md` names pull request titles,
says what follows the ids, and carries the three `#1523` titles as examples;
the start mode points at it; and `docs/resident-instructions.md` records the change to a resident file.

**Generator check.** Not a generator. The fact misread is what the words
after a title's ids are for, and one rule paragraph states it. No other open
item records a title the owner could not read, and the prose items under
`prose-quality` concern docstrings and documents rather than titles.
