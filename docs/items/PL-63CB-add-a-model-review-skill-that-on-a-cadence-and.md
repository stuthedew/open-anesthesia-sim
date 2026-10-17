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
- *Triggers.* A cadence the owner sets, and after any generator or cluster
  appears: the review checks every generator recorded since the last pass.
  The first run doubles as the backfill (`PL-92ZN`) and the CI snapshot
  (`PL-4SFQ`).

**What history can say.** In the sessions sampled on 2026-10-17, model and
effort both track the calendar: Sonnet 5 at high in August, Opus 5 at max in
September, Fable 5.1 or Opus 5.5 at xhigh in October. So the backfill will
show model by period, confounded with a codebase and rule set that changed
over the same weeks, and will say almost nothing about effort, which is
learned prospectively only. October's Fable 5.1 against Opus 5.5 is the first
within-period comparison.

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
