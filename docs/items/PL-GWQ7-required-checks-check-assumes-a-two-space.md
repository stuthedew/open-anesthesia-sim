---
id: PL-GWQ7
title: required_checks_check assumes a two-space indent under jobs: and on:, so a workflow indented four spaces is skipped silently; latent
priority: P3
effort: S
status: done
classes: defect
feature: required-check-trigger-reading
touches: tools/required_checks_check.py, tests/unit/test_required_checks_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-05
pr: 1366
payoff: a workflow indented any consistent width is read for its triggers and jobs, so the required-check reconciliation cannot pass by not seeing it
verify: grep -q 'def test_a_workflow_indented_four_spaces_reports_its_jobs' tests/unit/test_required_checks_check.py
---

**Problem.** required_checks_check assumes a two-space indent under jobs: and on:, so a workflow indented four spaces is skipped silently; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

YAML lets a mapping use any indentation consistently; the reader matches its keys at a fixed two-space indent, so a workflow written with four reads as holding no jobs or triggers, with nothing said. Not a member of `PL-R417`; a member of `PL-848V`, the head for which events a workflow's `on:` names. Latent: the six workflows all indent two spaces.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `8cc0698d`, a workflow indented four spaces - `on:` over `pull_request:`, and `jobs:` over a job `test` whose `name: tests` and `runs-on:` sit eight spaces in - gave `_triggers` the empty set, `_jobs` an empty list and `reporting_jobs` no job, where its two-space twin reported `tests`. Indented two spaces under `on:` and four under `jobs:`, `pull_request` was read and no job was; a four-space job declaring `strategy:` came back as no job rather than refused as a matrix; and `_job_name` refused a four-space job's `name: tests` as "a plain scalar carried onto the line after it", reading the next key as its continuation, so mending `_jobs` alone would turn every named job into a refusal. Latent, as the line above says: the six workflows under `.github/workflows` all indent two spaces.

**Why it matters.** YAML lets a block mapping take any indentation it keeps consistent, and a workflow written wider reads to this check as reporting nothing, with nothing said. Its jobs leave the reconciliation, so one reporting on pull requests without being required passes unreported - the `PL-H8YD` failure - and a required one reads as orphaned. The refusals that keep the check from guessing a matrix job's or a reusable workflow's check names are skipped along with it.

**Generator check.** Its `on:` half is a member of `PL-848V`, recorded there by `PL-R417`'s sweep: which events a workflow's `on:` names, missed at an indentation YAML allows. Its `jobs:` half, `_jobs` and `_job_name` reading a job at a fixed indent, is outside that head's fix and a one-off, so this item outlives `PL-848V` unless that work takes `_jobs` too (corrected at triage, 2026-10-04).

**Done when.** A workflow indented four spaces reads as its two-space twin does: `_triggers` names its events, `_jobs` its jobs, `_job_name` each job's check name, and a matrix job is still refused. The `on:` half lands with `PL-848V`'s one reader of a workflow's triggers; the `jobs:` half, `_jobs` and `_job_name`, lies outside that reader, so the head's fix alone does not close this item. `tests/unit/test_required_checks_check.py` gains `test_a_workflow_indented_four_spaces_reports_its_jobs`.
