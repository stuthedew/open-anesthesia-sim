---
id: PL-4T49
title: required_checks_check reads an on: value opening on the line after the key, a block-scalar header and an explicit ? paths key as no trigger or no path filter, and a flow mapping spanning lines under jobs: as jobs, so a pull-request workflow can drop out of the reconciliation and the check pass; latent
priority: P3
effort: S
status: done
classes: defect
feature: required-check-trigger-reading
touches: tools/required_checks_check.py, tests/unit/test_required_checks_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-848V's thread, 2026-10-05
added: 2026-10-04
closed: 2026-10-05
pr: 1366
payoff: a pull-request workflow whose on: value opens on the line after the key, or whose jobs: is a flow mapping, is read or refused by name, so the reconciliation cannot pass without it
verify: grep -q 'def test_an_on_value_on_the_line_after_the_key_names_its_events' tests/unit/test_required_checks_check.py && grep -q 'def test_a_flow_mapping_under_jobs_is_refused_by_name' tests/unit/test_required_checks_check.py
recurrences: 2026-10-04 PL-GWQ7 withdrawn 2026-10-04 PL-R417
---

**Problem.** required_checks_check reads an on: value opening on the line after the key, a block-scalar header and an explicit ? paths key as no trigger or no path filter, and a flow mapping spanning lines under jobs: as jobs, so a pull-request workflow can drop out of the reconciliation and the check pass; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

YAML 1.2.2 § 7.3.3, § 7.4, § 8.1 and § 8.2. `_triggers` reads `on:` over `  pull_request` (PyYAML: 'pull_request') and `on:` over `  [push, pull_request]` as no events, and `on: >-` over `  pull_request` as the event `>-`; an explicit `? paths` key with its value on a `:` line escapes the path-filter refusal. `_jobs` and `_key_at` read `jobs:` over `  {lint: {name: Lint, ...}}` as a job named `{lint`, and a flow mapping carried past `jobs:`'s line as a phantom job `runs-on`. A workflow read as triggering nothing drops out of `reporting_jobs`, so the reconciliation passes without it, the shape `PL-H8YD` names. `PL-R417`'s third slice refuses a flow sequence carried past `on:`'s line; these are the forms it left. `PL-848V` (a block sequence and a one-line flow mapping) and `PL-C72H` (a branch filter) are the same function's other misreadings, outside this head; with this item they are members of `PL-848V`, the head for which events a workflow's `on:` names. Latent: every live `on:` is a block mapping.

**Why it matters.** `required_checks_check` exists to fail when a job reporting on pull requests is missing from the required list, or a required name has no job, and a workflow it reads as triggering nothing drops out of that reconciliation, so the check passes while its guarantee is void - the `PL-H8YD` shape. Each form here is ordinary YAML a workflow edit can introduce. Under `jobs:`, a flow mapping read a line at a time names a phantom job, so a required check can read as reported by a job that does not exist while the real ones go unread.

**Reproduced 2026-10-05, at triage.** On Python 3.11.15, against `main` at `f84e31f9`: `_triggers` read `on:` over `  pull_request` and `on:` over `  [push, pull_request]` as no events, `on: >-` over `  pull_request` as the event `>-`, and a `pull_request:` whose `? paths` key carries its value on a `:` line below it as `pull_request` with no path filter refused; `_jobs` read `jobs:` over `  {lint: {name: Lint, runs-on: x}}` as a job `{lint`, and `jobs: {lint: {name: Lint,` over `  runs-on: x}}` as a job `runs-on`.

**Done when.** `required_checks_check` reads its triggers through `PL-848V`'s one reader, which names the events of an `on:` value opening on the line after the key and refuses a block scalar and an explicit `?` key by name, and `_jobs` refuses a `jobs:` value written as a flow mapping, on the key's line or the next, by name. `tests/unit/test_required_checks_check.py` gains `test_an_on_value_on_the_line_after_the_key_names_its_events` and `test_a_flow_mapping_under_jobs_is_refused_by_name`. The head's reader covers the `on:` half and this item's own work the `jobs:` half, so it closes with `PL-848V`.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names. It is also a member of `PL-848V`, recorded there by `PL-R417`'s sweep, whose one reader of a workflow's `on:` closes it.
