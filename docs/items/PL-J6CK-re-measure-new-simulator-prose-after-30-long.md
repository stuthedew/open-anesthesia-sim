---
id: PL-J6CK
title: Re-measure new simulator prose after 30 long units written under the close-out review step have merged: rate them blind with the PL-Y55Q rubric, keep the step at 30% awkward or less, retire it above
priority: P3
effort: S
status: ready
classes: docs, session-cost
feature: prose-quality
touches: .claude/skills/docket/modes/close-out.md, tools/new_prose.py
added: 2026-10-18
payoff: the close-out prose review is kept on a measured rate, or retired
verify: grep -qE '^\*\*Re-measured [0-9]{4}-' docs/items/PL-J6CK-re-measure-new-simulator-prose-after-30-long.md
---

**Problem.** `PL-PRCS` added a close-out step on 2026-10-18. A fresh reviewer
reads each docstring and comment of 30 words or more that a branch adds or
changes in the simulator, and returns rewrites. The step is a trial. Nobody
yet knows whether it brings new prose closer to the 22% awkward rate that the
`PL-8ZTQ` experiment reached, from the 61% that `PL-Y55Q` measured for long
units written under the resident rule alone.

**When to start.** Once 30 long simulator units written under the step have
merged. Count them on `main` with `python3 tools/new_prose.py --base <sha>`,
where `<sha>` is the squash commit that merged `PL-PRCS`. The tool prints every
long unit changed in the simulator's files since that commit.

**What to do.** Rate those 30 units blind, with the `PL-Y55Q` rubric and
scripts, pooled as that re-measure pooled its verdicts. Keep the step if 30%
or fewer of the pooled verdicts are awkward. Retire it if more are, by removing
step 8 from `.claude/skills/docket/modes/close-out.md` and `tools/new_prose.py`,
because a check that does not change the outcome costs every run and buys
nothing (`CLAUDE.md` § "Prefer deterministic tooling over repeated model
work").

**The cost to weigh it against.** One review of 6 units (708 words, `#1574`)
cost 91,705 tokens in one turn on 2026-10-18. `PL-PRCS` records the
measurement.

**Why it matters.** Each review costs about one subagent's starting context,
on about one pull request in six. Without the re-measure, the step either
keeps that cost with no evidence that it helps, or is dropped with no evidence
that it fails.

**Done when.** The rate is recorded in this item under a paragraph that opens
`**Re-measured DATE.**`, and the step is either kept
with the rate as its evidence or retired.

**Generator check.** One-off. It is the re-measure `PL-PRCS` pre-registered for its own step, not a misread fact.
