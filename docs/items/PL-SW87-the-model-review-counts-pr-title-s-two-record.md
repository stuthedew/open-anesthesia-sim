---
id: PL-SW87
title: The model review counts pr-title's two record holds, which fail by design, as red CI runs: 195 of the 335 red runs since 2026-09-21, which makes red runs per pull request appear to double
priority: P2
effort: S
status: done
classes: infra
feature: model-review
milestone: v0.6.9
touches: tools/ci_runs.py, docs/ci-runs.tsv, .claude/skills/model-review/SKILL.md, tests/unit/test_ci_runs.py, docs/apparatus.md
added: 2026-10-25
closed: 2026-10-26
pr: 1839
payoff: the model review's red-run measure counts only runs that found something, so its comparisons between models, effort levels and weeks stop carrying a by-design hold
verify: grep -q 'failed_steps' tools/ci_runs.py && grep -q 'failed_steps' .claude/skills/model-review/SKILL.md
---

**Problem.** The model review's "Red CI runs on its pull request" measure
counts every run whose `conclusion` is `failure`. Two steps of the required
`pr-title` job fail by design until a later hand step: "every closure records
this pull request's number" (`tools/pr_record_check.py`), and "the pull
request's body is recorded in the tree", which `#1068` added and `#1118`
retired on 2026-09-26. `PL-2D1S` classified the 335 red runs on the pull
requests of items closed from ISO week 39 to week 43. 132 were the number
hold and 63 the body record, 195 in all.

**What that does to the measure.** The share of closed items whose pull
request had a red run went from 17% in week 38 to 30% in week 39, the week
both holds landed. Counting only red runs outside the two holds, the share
was 12%, 11%, 22%, 10% and 22% in weeks 39 to 43, against 18%, 23% and 17% in
weeks 36 to 38. So the apparent doubling is the holds. The first review, on
2026-10-25, read it as a rise "whatever the setting" and filed `PL-2D1S`.

**Why it matters.** The review uses red runs to compare models, effort
levels and origins. A hold that fails one closing pull request in five,
whatever setting worked it, adds noise to every such comparison and invents a
trend over time.

**Why the record must be kept now.** `docs/ci-runs.tsv` holds one row per run
and no job or step. GitHub deletes a run, its jobs and its logs 90 days after
it ran, so which step failed must be copied while the run exists, as the run
rows already are (`PL-4SFQ`).

**What to build.**

1. `tools/ci_runs.py refresh` asks GitHub's jobs endpoint
   (`/actions/runs/{id}/jobs?filter=latest`) for each run whose `conclusion`
   is `failure` and has no recorded steps yet. It stores the names of the
   failed steps in a new `failed_steps` column. That is about 70 requests a
   week. The aggregate step "both parts succeeded" is left out, because it
   fails whenever a test part fails.
2. The model review skill's measure table counts red runs without the two
   hold steps, and names them by step, so a later hold is added in one place.
3. The same row of the table reads `pull_requests` for the join, but GitHub
   empties that column once the branch is deleted, and the first run joined
   only 1 item through it. It joined through the pull request's head branch
   and the time it was open instead. Write that join into the row.

**Done when.** A refresh fills `failed_steps` for the failed runs it reads,
with a test that pins the aggregate step's exclusion. The skill's red-run row
excludes the two hold steps and states the head-branch join.

**Done 2026-10-26.** `tools/ci_runs.py refresh` now reads the jobs of every
failed run that has no recorded steps, through GitHub's jobs endpoint with
`filter=latest`, and writes the failed steps' names to a new `failed_steps`
column as a JSON list. The aggregate step "both parts succeeded" is left out.
An empty list means the run failed no step of its own, an empty field means
the jobs are not read yet, and `unavailable` means GitHub no longer has them.
A later attempt of a run is read again. A JSON list was chosen over a
separator, because a step with no name of its own is named after its command:
the first refresh joined names with "; " and split the pytest step's
`import os; print(...)` in two. The model review skill's red-run row now
leaves out the runs whose failed steps are only the two holds, counts a run
with an empty list as not red, and joins through the head branch and the time
the pull request was open.

The refresh read all 643 red runs from 2026-08-22 on. 220 failed only the two
holds, 7 failed no step of their own, and 416 failed something else. One step
not examined here fails often: "pull request title names the items it
closes" failed in 102 red runs. Whether part of that is by design, such as a
draft opened by `bin/docket claim` before its title is written, is filed as
`PL-J35R`.

