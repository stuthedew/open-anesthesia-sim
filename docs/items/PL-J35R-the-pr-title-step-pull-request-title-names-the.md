---
id: PL-J35R
title: The pr-title step 'pull request title names the items it closes' failed in 102 of the 643 red CI runs recorded in docs/ci-runs.tsv from 2026-08-22 to 2026-10-26; find whether some of those fail by design, such as a draft opened by bin/docket claim with a title written from the item, and if so add the step to the model review's hold list
priority: P3
effort: S
status: done
classes: infra
feature: model-review
milestone: v0.6.12
touches: .claude/skills/model-review/SKILL.md
added: 2026-10-26
closed: 2026-11-01
pr: 1911
payoff: the model review's red-run measure stops counting pull request titles that fail only until the title is edited, if that is what most of the 102 failures are
verify: grep -qE '^\*\*Measured\.' docs/items/PL-J35R-*.md
---

**Problem.** The pr-title step 'pull request title names the items it closes' failed in 102 of the 643 red CI runs recorded in docs/ci-runs.tsv from 2026-08-22 to 2026-10-26; find whether some of those fail by design, such as a draft opened by bin/docket claim with a title written from the item, and if so add the step to the model review's hold list

**Why it matters.** The model review compares red CI runs per pull request across models, effort levels and weeks. `PL-SW87` took the two `pr-title` record holds out of that count, because they fail by design until a later hand step. This step was left in. If many of its 102 failures are the expected order of work rather than mistakes, the red-run measure still carries a by-design share, and a week with more claims or more fix-now closures looks worse than it was.

This step differs from the two holds in one way that matters. It also catches real mistakes, such as a title that leaves out an item the branch closes. So adding the whole step to the hold list would hide those. The likely answer is a rule that leaves out only the by-design failures, not the step.

**Done when.** The 102 failures, or every one still readable, are sorted by cause, with counts, under a `**Measured.**` paragraph in this item. A deterministic signal to try first: `pr-title` runs again when the title is edited, so a failed run followed by a green `pr-title` run on the same `head_sha` was cleared by a title edit with no new commit. Then one of three outcomes follows, chosen on the counts. If the step fails only by design, it joins the hold list in `.claude/skills/model-review/SKILL.md`. If it fails by design in a subset that a rule over `docs/ci-runs.tsv` can name, that rule goes into the skill's red-run row. If the by-design share is small, the item records that and the count stays as it is.

**Generator check.** Not a generator. This item asks a measurement question that `PL-SW87`'s refresh opened, and no reader misread a fact. The fact it would settle, which CI steps fail by design, is held once, in the model review skill's hold list, and this item adds to that record rather than copying it.

**Measured.** All 102 failures were still readable on 2026-11-01, and every one printed the same message: "this branch closes X, but the title does not lead with Y". So every failure is a closure pushed while the pull request's title did not yet lead with that item's id. None is by design. The close-out mode has said to retitle before pushing a closure since 2026-09-05 (`PL-X1S4`), and `make check` has run the same title check locally since then (`PL-J3BB`), against the working tree since 2026-09-27 (`PL-T8PT`). No step of the written procedure makes the title lag the closure. The failures sort into three shapes, read from each run's log:

| Shape | Runs |
| --- | --- |
| The title leads with some of the closed ids but leaves out a rider closed beside them, such as a capture, a triaged duplicate or a second claimed item | 83 |
| The title leads with the branch's headline item, which is still open, and the branch closed a different item first | 18 |
| The title leads with no id at all | 1 |

How each was cleared, from the next `pr-title` run on the same branch in `docs/ci-runs.tsv`: 51 by a retitle with no new commit that went green, 10 by a retitle that still failed, 28 by a further push that still failed, 7 by a push that went green, and 6 ran inside `quality.yml` before the check moved to its own workflow. The 102 runs fall in 68 streaks on 59 branches. 27 came before the retitle-first rule merged (2026-09-05 22:45Z), and 37 came after `make check` read the title from the working tree (2026-09-27 13:24Z). The hypothesis in the title does not hold: a draft that `bin/docket claim` opens leads with the claimed ids (`_draft_at_claim` in `subprojects/docket/src/docket/cli.py`), and the last of the 102 runs (2026-10-25 22:41Z) came before claims began opening drafts (`#1832`, 23:02Z).

**Outcome.** The by-design share is zero, so the step stays in the red-run count. A red title run means a session pushed a closure without the retitle that the close-out mode asks for first, and `make check` would have caught it before the push. That is a slip in the work, which is what the measure exists to compare. The model review skill's red-run row now says so, so a later review does not ask again. The per-run table and the script that classified the clearing runs are in the project's shared folder, `v0.7.0/pl-j35r-title-failures.tsv` and `v0.7.0/pl-j35r-classify.py`.
