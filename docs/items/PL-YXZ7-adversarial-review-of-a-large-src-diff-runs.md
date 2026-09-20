---
id: PL-YXZ7
title: Adversarial review of a large src/ diff runs before the pull request opens, not after it merges
priority: P2
effort: S
status: done
classes: infra
touches: .claude/skills/docket/modes/close-out.md
added: 2026-09-20
closed: 2026-09-20
pr: 795
payoff: stops a defect a passing suite cannot see reaching main and turning one commit into three items and a second pull request
verify: grep -q 'Review the diff adversarially before the pull request opens' .claude/skills/docket/modes/close-out.md
---

**Problem.** Adversarial review of a large src/ diff runs before the pull request opens, not after it merges

**Why it matters.** `#784` was opened with `make check` green and merged on
that, and an adversarial review run *afterwards* found three real defects in
it - one of them `safety`-classed, all three reproduced against real widgets
before being filed (`PL-LQ19`, `PL-K5NY`, `PL-J12Z`). The review would have
found them just as well an hour earlier, when they would have cost one commit
instead of three items, a second pull request and a permanent record of
`PL-VKJW` and `PL-QRD1` closing against work that was incomplete.

Nothing was wrong with the review. What was wrong was its place in the order:
`CLAUDE.md`'s pull-request bullet says the request arrives as soon as the work
is finished and its checks are green, and "its checks are green" was read as
the whole of the bar. For a change this size it is not - `make check` proves
the suite passes, which is exactly what a defect nobody wrote a test for
survives.

**Recorded 2026-09-20 (project owner, ratified, over leaving the review to a
session's own judgment case by case).** The case put was that the threshold
should be roughly 200 changed lines under `src/`, and that below it the
ordinary quality suite and a session's own adversarial re-read are enough.
Ratified rather than specified, so ordinary evidence reopens it - a measured
false-alarm rate, a session that spends an hour finding nothing, or a cheaper
mechanism that catches the same class.

**Routed to the `docket` skill's close-out mode rather than into `CLAUDE.md`.**
`.claude/skills/docket/modes/close-out.md` is what a session reads at the exact
moment the rule fires: it already carries the closure commit, the docs sweep
and the `--self` audit, and `CLAUDE.md` already directs any queue workflow -
"closing an item out" among them - into this skill. That is disposition 2 of
the four `CLAUDE.md` § "A behavior change takes effect in the session that asks
for it" ranks, and it costs zero resident context where disposition 4 would
have cost a paragraph in the file whose growth that section is about.

A deterministic check was considered first, as that section asks, and refused:
what is decidable is the size of the diff, and what is not is whether a review
happened or was any good. A check could only fire on the size and then ask a
session to attest - which is scripting the judgment half, and which
`CLAUDE.md` refuses because a tool that guesses at judgment is worse than no
tool.

**Done when.**

1. `.claude/skills/docket/modes/close-out.md` carries the step, with its
   trigger, what the review has to do to count, and what `#784` cost without
   it.
2. The step says plainly what it is *not*: below the threshold, `make check`
   and a session's own adversarial re-read are the whole of the bar.
