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

[superseded 2026-10-18: refined and measured in the design round below]
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

## Design round, 2026-10-18

The round measured what the step would cost before putting it to the owner.
The scripts and the trial's inputs are in
`/mnt/project-files/v0.6.0/plain-writing/prcs-design-2026-10-18/`.

**How often it would run.** From the plain-writing rule's merge (8f9d20f3) to
684c1f66, 77 pull requests merged. 40 of them (52%) added at least one
docstring or comment of 30 words or more in a Python file. The median pull
request added 1 such unit (71 words). The 90th percentile added 14 units
(about 1,100 words), and the largest added 29 (1,960 words). Only 13 of the 77
pull requests (17%) added such a unit to the simulator, meaning `src/` or a
test that imports the product package. Those 13 carried 106 of the 332 long
units.

**What one review cost.** A fresh subagent at `high` effort reviewed the 17
long units that #1526 (`PL-R0NL`) added, the second largest set in the
period. It was allowed to open the cited lines of code. It used 7 tool calls
and 2.3 minutes, and the harness reported 118,411 tokens. Its context was
already about 80,000 tokens before it read anything, because every subagent
starts with the system prompt and the resident instructions. Each tool call
then costs another turn at that size, so the number of turns, not the length
of the prose, sets the cost. It found 12 of the 17 units awkward, close to the
re-measure's 61% for long units, and its rewrites kept every number. It also
noticed that the test module states desflurane's worst early point as
+2.10 SD in one docstring and +2.11 SD in a comment, which is filed as its own
item.

**Decided in the round.** Each follows from the measurement or from a rule
this repository already states, so none is put to the owner.

1. **Only units of 30 words or more.** In the re-measure, short units were
   awkward in 6 of 24 verdicts (25%), close to the experiment's 22% with the
   rule in the writer's prompt. Long units were awkward in 22 of 36 (61%).
2. **A script lists the units, so the reviewer reads no files.** Which
   docstrings and comments a diff added or changed, and how many words each
   has, is decidable from the diff. A standard-library tool under `tools/`
   prints each unit with its path, line range and the surrounding code. The
   reviewer then needs one turn, which should bring the cost close to the
   80,000-token starting context on a typical branch. That figure is
   inferred from the trial and is measured when the step is built. This is
   `CLAUDE.md`'s standing approval to put the decidable part in code.
3. **A fresh reviewer, not the writing session re-reading its own prose.**
   The defects that remain are private word senses (D2) and unclear
   references (D6). A writer cannot see either in their own text, because they
   already know what each word and each "it" means. This is the curse of
   knowledge (Pinker, *The Sense of Style*, 2014, chapter 3). Hinds found that
   experts misjudge what a novice will find hard, and that the debiasing
   methods she tried did not correct it (Hinds PJ, "The curse of expertise:
   the effects of expertise and debiasing methods on predictions of novice
   performance", *J Exp Psychol Appl* 1999;5(2):205-221; read here only
   through secondary accounts). The `PL-8ZTQ` experiment tested a fresh
   reviewer and found it as good as the rule at writing time. It did not test
   self-review.
4. **The session applies the rewrites and checks each one.** A rewrite that
   changes a number, a unit, a condition or a citation is rejected, because
   the safety-critical standard binds a docstring's facts.
5. **`high` effort**, which `.claude/rules/apparatus-standard.md` sets as the
   default for a subagent the apparatus spawns.
6. **A pre-registered re-measure.** After 30 long units written under the
   step have merged, the `PL-Y55Q` scripts and rubric rate them blind. If 30%
   or fewer of the pooled verdicts are awkward, the step stays. If more are,
   the step does not earn its cost and is retired, per `CLAUDE.md`'s rule that
   a check earns its place every run.

**Decision needed.** Should close-out pay for a fresh review of new long
prose, and on which branches?

- **A. Every branch** that adds or changes a docstring or comment of 30 words
  or more, in either lane. That is about half of all pull requests. Each
  review costs about one subagent's starting context, about 80,000 tokens,
  more on a large branch.
- **B. Simulator branches only:** units in `src/` or in a test that imports
  the product package. That is about one pull request in six, and about a
  third of the long units. Apparatus prose keeps the rule alone.
- **C. No step.** The resident rule alone, which leaves about 47% of new
  prose awkward.

**Recommendation: B.** A misread docstring in the simulator can mislead a
reader about a clinical value, which is the case this item names. In the
apparatus a misread costs a session a re-read. B buys the review where the
safety-critical standard already asks for more, at about a third of A's
cost. The re-measure in point 6 then draws from simulator units only. If it
shows the step works, extending it to the apparatus is a one-line change to
the step's trigger.
