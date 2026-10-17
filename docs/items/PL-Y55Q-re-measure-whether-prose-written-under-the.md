---
id: PL-Y55Q
title: Re-measure whether prose written under the plain-writing rule reads plainly, and add a review step at close-out only if it does not
status: untriaged
feature: prose-quality
added: 2026-10-17
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
