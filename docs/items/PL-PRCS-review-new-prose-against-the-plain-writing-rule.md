---
id: PL-PRCS
title: Review new prose against the plain-writing rule at close-out, since 47% of prose written under the resident rule still read awkwardly in PL-Y55Q's blind re-measure
priority: P3
effort: M
status: needs-decision
classes: docs, session-cost
feature: prose-quality
touches: .claude/skills/docket/modes/close-out.md
deferred-from: v0.6.0 - a workflow cost decision, not part of the layout milestone's scope
added: 2026-10-18
payoff: new prose reads plainly to a careful newcomer, where the resident rule alone left 47% of new test prose awkward
---

**Problem.** Review new prose against the plain-writing rule at close-out, since 47% of prose written under the resident rule still read awkwardly in PL-Y55Q's blind re-measure

**Why.** `PL-Y55Q` re-measured prose written after the plain-writing rule
merged and found 28 of 60 pooled blind verdicts awkward (46.7%), above the
40% line its brief set for adding a review step. The rule helped: prose from
2026-09-20 to 2026-10-17 was 74% awkward. But it did not reach the 22% the
`PL-8ZTQ` experiment measured with the rule in the writer's prompt. The
remaining defects are mostly private word senses (D2) and unclear references
(D6), in units of 30 words or more (22 of 36 verdicts awkward, against 6 of 24
for shorter units). The sample was new test prose; see
`/mnt/project-files/v0.6.0/plain-writing/remeasure-2026-10-18/`.

**What it would add.** A step in the close-out
(`.claude/skills/docket/modes/close-out.md`) that has a fresh reviewer read
the docstrings and comments the branch added or changed and rewrite the
awkward ones against `.claude/rules/plain-writing.md`. In the `PL-8ZTQ`
experiment a fresh review did as well as the rule in the prompt.

**Decision needed.** Whether to add a review step to every close-out that adds prose, and at what scope. In that experiment a fresh review cost
about 220,000 to 260,000 tokens per use, and it would run on every branch that
adds prose. That is a standing cost on every close-out, so it is the owner's
call whether to pay it.

**Recommendation.** Build a narrower and cheaper step rather than the full
review: a subagent at `high` effort that reads only the added or changed
docstrings and comments of 30 words or more in the branch's diff, against the
rule's eight points and its word list, and returns rewrites for the session to
apply. Long units carry two thirds of the awkward verdicts, so this targets
most of the defect at a fraction of the reads. Then re-measure after 30 more
units land, with the same scripts, to see whether it brought the share to the
experiment's level.

**Why it matters.** Prose that reads awkwardly to a newcomer costs every
later reader a re-read, and in the simulator a misread docstring can mislead
about a clinical value. The resident rule alone leaves about half of new
prose awkward.

**Done when.** The decision is recorded here, and either the step is in
`.claude/skills/docket/modes/close-out.md` and a re-measure of 30 later units
is filed, or this item says why no step is added.

**Generator check.** One-off. It is the follow-up `PL-Y55Q` named for this
outcome, not a misread fact.
