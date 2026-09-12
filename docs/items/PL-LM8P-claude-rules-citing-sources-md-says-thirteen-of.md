---
id: PL-LM8P
title: .claude/rules/citing-sources.md says thirteen of twenty-six sources entries name a route or a depth, and there are now thirty-five
priority: P3
effort: S
status: ready
classes: docs
feature: worker-instructions
touches: .claude/rules/citing-sources.md
added: 2026-09-07
verify: python3 tools/doc_check.py check && ! grep -qF 'Thirteen of the twenty-six' .claude/rules/citing-sources.md
---

**Problem.** .claude/rules/citing-sources.md says thirteen of twenty-six sources entries name a route or a depth, and there are now thirty-five

The sentence is the rule's argument for itself - *"So this is the existing
convention made compulsory, not an addition"* - so the count is doing work
rather than decorating. It was written when the data files held 26 `sources`
entries; they hold 35 as of 2026-09-07, after `PL-6Q8N`, `PL-8ZJQ` and
`PL-3YZW` added citations to
`src/anesthesia_sim/data/patients/reference_adult.json` and the MAC-awake work
added several to the agent files.

The numerator is not checked here: how many of the 35 name a route and a depth
needs reading each note, which is the pass this item is. What is certain is
that the denominator is wrong, and that a reader who counts will find the
sentence does not describe the tree.

**Whether to fix the number or the sentence is the judgment.** A count in prose
goes stale every time a source is added, and nothing will notice - this one
survived at least three items that changed it. The alternative is to drop the
figures and state the rule without the census ("every note names which route
and how deeply you read; most already do"), which cannot rot. Recommend the
second, and only re-count if the argument genuinely needs the numbers.

`tools/doc_check.py` cannot decide this: the count is a fact about note prose,
and matching "names a route" is exactly the judgment half a checker must not
guess at.

**Found.** `PL-1JDD`, 2026-09-07, in its close-out documentation sweep.


**Why it matters.** The count is the rule's argument for itself - "So this is
the existing convention made compulsory, not an addition" - so a reader who
checks it and finds it does not describe the tree has been given a reason to
doubt the rule rather than follow it. The denominator was 26 when written and is
35 now, after `PL-6Q8N`, `PL-8ZJQ` and `PL-3YZW`, and nothing noticed across at
least three items that changed it.

**Done when.** The sentence no longer depends on a census that rots: the figures
are dropped in favour of the rule stated without them ("every note names which
route and how deeply you read; most already do"), or - only if the argument
genuinely needs the numbers - they are re-counted and the numerator established
by reading the notes. The first is recommended in the brief above and is the
cheaper answer to maintain.
