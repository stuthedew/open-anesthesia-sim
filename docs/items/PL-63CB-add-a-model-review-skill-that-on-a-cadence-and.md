---
id: PL-63CB
title: Add a model-review skill that, on a cadence and after any generator or cluster, joins closed items to the sessions that worked them, scores each by how the work held up, screens every recorded attribute for associations, and brings recommendations with their evidence and n
priority: P2
effort: M
status: ready
classes: session-cost, infra
feature: model-evidence
touches: .claude/skills/model-review, docs/model-review.md, docs/maintainer.md
added: 2026-10-17
payoff: model and effort are chosen per item type from measured reliability and cost rather than a cautious default, and the owner is handed the recommendations instead of having to ask
verify: grep -q 'model-review' docs/maintainer.md && grep -q 'pre-registered' .claude/skills/model-review/SKILL.md
---

**Problem.** Add a model-review skill that, on a cadence and after any generator or cluster, joins closed items to the sessions that worked them, scores each by how the work held up, screens every recorded attribute for associations, and brings recommendations with their evidence and n

**Why it matters.** The owner's objective, stated 2026-10-17: reliability
first and savings second; no burden on item or project sessions; the review
proactive, so the owner is handed findings and never has to formulate the
question; and the attributes that predict failure discovered by the review
rather than nominated in advance, because some will be ones nobody has
thought of. This item is the procedure that meets all four, as a skill that
loads only when the owner starts a review and costs every other session
nothing.

**Decision rules** (project owner, 2026-10-17, ratified, over resident prose,
over a tool that computes the analysis, and over per-session self-assessment).

- *A downgrade needs a pre-registered trial.* Before the trial starts, the
  register names the item type, the sample size, the outcome, the window and
  the decision rule, and the result applies to that type only. The bar is the
  rule of three: with zero failures in n trials the 95% upper bound on the
  failure rate is about 3/n, so three clean items bound it only to below 63%,
  thirty to below 10%, sixty to below 5% (Hanley JA, Lippman-Hand A. If
  nothing goes wrong, is everything all right? JAMA 1983;249(13):1743-1745).
- *An upgrade needs one traced cluster.* A generator or cluster whose members
  were worked on a cheaper setting is enough to trial the stronger one.
- *Screen everything recorded.* Features come from the item's front matter,
  its brief text, its diff shape, its pull request history, the session
  record (`PL-92ZN`) and the outcome signals (`PL-4SFQ`), plus judgment
  features such as decision versus implementation. Report effect size and n
  for each association, control the false discovery rate (Benjamini Y,
  Hochberg Y. J R Stat Soc B 1995;57(1):289-300), and treat every hit as a
  hypothesis for a prospective trial, never as a conclusion.
- *Confounding by indication.* `Item.model_guidance` sends safety, science and
  open-decision items to the strongest model by rule, so a naive comparison is
  biased against the stronger model. Condition on the item's attributes, and
  take the clean answer from prospective assignment within a type where both
  settings are plausible. Never randomize safety-critical work (Psaty BM et
  al. J Am Geriatr Soc 1999;47(6):749-754).
- *Design fallout.* A design or decision item is scored by downstream rework:
  later items citing it that are classed defect or refactor, with their
  sessions' cost; its decisions later reopened or refuted, which
  `docs/dead-ends.md` and reopening notes record; and churn on the files its
  pull request introduced (Nagappan N, Ball T. Use of relative code churn
  measures to predict system defect density. ICSE 2005). Re-scored at every
  pass; verdicts here arrive late by construction.
- *The report.* A short list of findings and recommendations, each with its
  evidence and n, each marked "trial this" or "change the default", each a
  decision for the owner. It also reports what was not asked: a model
  over-used on trivial work, a session type with high cost and little output,
  a feature whose apparatus cost outran its product payoff.
- *Triggers.* Monthly, and after any generator or cluster appears: the
  review checks every generator recorded since the last pass (project owner,
  2026-10-19, ratified, over a weekly or a quarterly cadence; a 30-day outcome
  window makes a shorter cadence mostly re-score the same items).
  The first run doubles as the backfill (`PL-92ZN`) and the CI snapshot
  (`PL-4SFQ`).

**What history can say.** The first draft of this paragraph rested on a
sample and said Sonnet 5 at high in August. The ledger (`PL-92ZN`) corrects
it. Counting the 888 listed sessions on 2026-10-19 by the model that served
the last turn: August's 78 were mostly Opus 5 at high or xhigh, with 4 on
Sonnet 5. September's 707 were mostly Opus 5 at max (439), with Opus 5.5 at
max (139) and both models at xhigh. October's 103 so far are Opus 5.5 at
xhigh, max and high. So model and effort still track the calendar, confounded
with a codebase and rule set that changed over the same weeks. But September
already holds a within-period comparison of Opus 5 against Opus 5.5 at max,
which the first review can use. Effort is still learned mostly
prospectively.

**Done when.** `.claude/skills/model-review/SKILL.md` exists, carries the
pre-registration template, the rules above with the rule-of-three table, the
screening procedure, the outcome measures from `PL-4SFQ`, the design-fallout
scoring, the report format and the triggers, and says how the ledger and the
CI snapshot are refreshed; a hypothesis register, recommended
`docs/model-review.md`, holds each pre-registered trial and each review's
dated findings; `docs/maintainer.md` § "Match model capability to the work"
points at the skill; and the first review has run and written its findings to
the register.

**Generator check.** Work the owner asked for on 2026-10-17; a one-off.

**Effort monitoring (project owner, 2026-10-19).** From 2026-10-19 every
session opens at `high`, as the owner's own judgement (`docs/maintainer.md`,
`PL-6XZG`). The owner asked to be told when there is statistically significant
evidence that working at `high` caused real-world issues, such as a poor design
choice that needed rework or unintended behavior. Each monthly run does this:

1. **Unit and groups.** The unit is a closed item, joined to the sessions that
   worked it through the ledger. Items worked only at `high` on Opus 5.5 form
   one group. Items worked only at `xhigh` or `max` on Opus 5.5 form the other.
   Items worked at mixed levels are counted and left out.
2. **Outcomes.** The outcome measures `PL-4SFQ` defines: later items naming it
   as the cause of rework, recurrences and reopenings, red CI runs on its pull
   request, review findings, and churn on its files within 30 days.
3. **Adequate data first.** Before any test, compute the number of items each
   group needs to detect the smallest difference worth acting on, and state
   it. Until both groups reach it, report the counts and "not yet adequate",
   not a result.
4. **Adjust and correct.** Compare the groups within lane (product or
   workflow) and item size, for example with a logistic regression or a
   stratified comparison. Monthly looks at the same question inflate false
   positives, so correct the significance level for repeated looks.
5. **Say what it cannot show.** Every session after 2026-10-19 runs at `high`,
   so later comparison groups are historical. Some overlap exists already: from
   2026-09-22 to 2026-10-19 the ledger holds Opus 5.5 sessions at `high` (189),
   `max` (242) and `xhigh` (59). But 174 of the 189 at `high` are Projects
   threads, a different way of working, and only 71 of the 242 at `max` are.
   So compare within origin as well. The groups also differ in date, project
   phase (product focus began 2026-09-25) and the apparatus around them. A significant difference is therefore an association that points at
   a cause, not proof of one. The report says so.
6. **The trial, once `PL-HYRM` starts it.** Each new cloud session is
   assigned `xhigh` or `high` automatically, and the assignment is recorded
   (`docs/maintainer.md`, `PL-HYRM`). Analyze sessions by the level they were
   assigned (intention to treat), and report as a second result the level
   they actually ran at. Report how many ran at a
   level other than the one assigned. This comparison is randomized, so it
   is the primary result once it has adequate data. The historical
   comparison above becomes a supporting one. Projects threads are not
   assigned and are analyzed apart.
7. **Report.** When the corrected test is significant, put it to the owner:
   the effect with its 95% confidence interval, the counts, the confounders,
   and a recommendation.
