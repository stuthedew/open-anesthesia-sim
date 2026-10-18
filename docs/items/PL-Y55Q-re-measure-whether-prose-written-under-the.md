---
id: PL-Y55Q
title: Re-measure whether prose written under the plain-writing rule reads plainly, and add a review step at close-out only if it does not
priority: P3
effort: M
status: done
classes: docs
feature: prose-quality
milestone: v0.5.28
touches: docs/items/PL-Y55Q-re-measure-whether-prose-written-under-the.md
added: 2026-10-17
closed: 2026-10-18
pr: 1564
payoff: the project learns whether the resident plain-writing rule works in real sessions before anyone adds a costly review step for it
verify: grep -qE '^[*][*]Measured on 2026-[0-9]{2}-[0-9]{2}' docs/items/PL-Y55Q-*.md
not-delegable: the sample is rated blind by two raters against a rubric outside the repository, a judgment no command can check
---

**Problem.** Re-measure whether prose written under the plain-writing rule reads plainly, and add a review step at close-out only if it does not

**Why.** `PL-8ZTQ` added `.claude/rules/plain-writing.md` on the strength of a
small test. With the rule in the writer's prompt, 4 of 18 ratings found a
docstring awkward, against 18 of 18 without it. In real sessions the rule is
one of four resident files and the task prompt says nothing about it, so it
may be followed less. This item checks the rule in real use.

**Start when** at least 30 docstrings or comments under `src/` and `tests/`
were first written after the rule merged. `git log` from the merge date shows
the count.

**What to do.** Draw a blind sample of about 30 units of prose written after
the rule landed. Have two raters score it against the rubric in
`/mnt/project-files/v0.6.0/plain-writing/measure/results.md`, and pool their
verdicts, as the experiment did. Compare the awkward share with 74% for prose
last edited from 2026-09-20 to 2026-10-17 and 22% under the rule in the
experiment.

**The number that changes the decision.** If more than 40% of the pooled
verdicts are awkward, the resident rule is not working as it did in the test.
Then file a review step for new prose at close-out. In the experiment a fresh
review did as well as the rule, at about 220,000 to 260,000 tokens per use. At
40% or less, the rule alone is enough, and this item closes with the count.

**Done when.** The count is recorded here, with the sample and the ratings
under `/mnt/project-files/v0.6.0/plain-writing/`, and either the review step
is filed or this item says why none is needed.

**Why it matters.** The rule is resident in every session at a measured cost.
If it does not work in real use, prose keeps coming out awkward and a review step
is the next lever. If it does, no review step is needed, and that is worth
knowing before one is proposed.

**Generator check.** One-off. It is a measurement the owner asked for in `PL-8ZTQ`, not a defect, so no fact was misread.

**Measured on 2026-10-18: 28 of 60 pooled verdicts AWKWARD (46.7%), above
the 40% line, so the review step is filed as `PL-PRCS`.**

- **Sample.** `git blame origin/main` (1bced7e9) found 301 docstrings and
  comment blocks in `src/` and `tests/` whose every line landed after the rule
  merged (8f9d20f3, #1478, 2026-10-17 06:48Z). Units carried by #1475 to #1489
  were left out, because those pull requests were opened before the rule
  merged and their sessions began without it. That left 272 units from 31
  pull requests. A seeded draw (20261018) took 30 units from 21 pull requests.
  Only 6 of the 272 were in `src/`, and the draw took none of them, so this
  measures new test prose: 19 docstrings and 11 comments.
- **Ratings.** Two blind raters, each a fresh subagent given only the rubric
  from `/mnt/project-files/v0.6.0/plain-writing/measure/results.md` and the
  unit text, found 14 of 30 each. They agreed on 28 of 30 units (Cohen's kappa
  0.87). The pooled share is 46.7%, with a Wilson 95% interval of 35% to 59%
  if the 60 verdicts are treated as independent.
- **Against the two reference points.** The rule did help: prose last edited
  from 2026-09-20 to 2026-10-17 was 74% awkward. But it did not reach the
  experiment's 22%, where the rule sat in the writer's prompt. The interval's
  lower end, 35%, is still above 22%.
- **Where it fails.** Long units carry it: 22 of 36 verdicts for units of 30
  words or more, against 6 of 24 for shorter ones. Docstrings were 21 of 38
  and comments 7 of 22. The blocking defects across both raters were D2
  (private word senses) 13 times, D6 (unclear reference) 11, D4 (overloaded
  sentence) 5, D1 (dropped small words) 4, and D3 and D5 2 each. D1, the
  largest defect before the rule, is now rare. D2 and D6 remain.
- **Caveats.** The raters are the same model family as the writers, as in
  the experiment. The sample is tests only. A branch opened after the rule
  merged may still have been started by a session that loaded the old
  instructions.

The sample, both ratings and the scripts are in
`/mnt/project-files/v0.6.0/plain-writing/remeasure-2026-10-18/`.
