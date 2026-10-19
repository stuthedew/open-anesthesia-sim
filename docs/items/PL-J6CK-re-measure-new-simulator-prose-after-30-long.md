---
id: PL-J6CK
title: Re-measure new simulator prose after 30 long units written under the close-out review step have merged: rate them blind with the PL-Y55Q rubric, keep the step at 30% awkward or less, retire it above
priority: P3
effort: S
status: done
classes: docs, session-cost
feature: prose-quality
milestone: v0.5.35
touches: .claude/skills/docket/modes/close-out.md, tools/new_prose.py
added: 2026-10-18
closed: 2026-10-19
pr: 1627
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

**Re-measured 2026-10-19.** The step is kept. Of 60 pooled blind verdicts on
30 long units written under it, 13 were awkward: 21.7%, with a Wilson 95%
interval of 13% to 34%. That meets the 30% bar and matches the 22% that the
`PL-8ZTQ` experiment reached.

- **Which units count as written under the step.** `tools/new_prose.py --base
  20eb2fd2` printed 173 long units on `main` at `af596190`. Not all of them
  passed through the review. #1599 and #1604 had finished their work before
  their branches took in the step. Six simulator branches held it: #1606,
  #1609, #1612, #1617, #1618 and #1619. Only #1619's pull request body records
  the review, as step 8 asks ("read 48 docstrings and comments ... 38 were
  rewritten"). So the decision rests on #1619's units. A unit was eligible
  when `git blame` gave every one of its rows to a single pull request after
  20eb2fd2. That left 31 units from #1619, and 30 were drawn.
- **A comparison drawn at the same time.** 30 more units were drawn from the
  76 eligible units of the five branches that recorded no review. The 60 were
  shuffled together, so neither rater could tell the groups apart. Those
  units were awkward in 35 of 60 verdicts (58.3%, 95% interval 46% to 70%).
  That is the 61% that `PL-Y55Q` measured for long units under the resident
  rule alone. The step lowers the rate when it runs, but five of the six
  branches skipped it. `PL-W04Z` is filed for that.
- **How it was rated.** Two fresh subagents rated blind, each reading only
  the `PL-Y55Q` rubric and the units. The second read them in reverse order.
  For #1619's units they agreed on 27 of 30 (kappa 0.71). Rater 1 found 7
  awkward and rater 2 found 6. The blocking defects were D2 (private word
  senses) 7 times, D4 (overloaded sentence) 4, D6 (unclear reference) 3 and D1
  (dropped small words) 2. 25 of the 30 units are in `src/`, where `PL-Y55Q`
  sampled none.
- **Caveats.** All 30 decisive units come from one pull request and one
  session, so the interval, which treats the verdicts as independent, is too
  narrow. Its upper end, 34%, is above the bar. The raters are the same model
  family as the writers and the reviewer. Branches that skipped the step may
  differ from #1619 in other ways, so the comparison is not a controlled one.
- **Material.** `/mnt/project-files/v0.6.0/plain-writing/remeasure-2026-10-19/`
  holds `population.py`, `sample.py` (seed 20261019), the units, both raters'
  tables, `join.py` and `summary.txt`.
