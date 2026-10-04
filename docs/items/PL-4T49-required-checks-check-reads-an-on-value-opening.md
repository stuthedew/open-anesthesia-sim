---
id: PL-4T49
title: required_checks_check reads an on: value opening on the line after the key, a block-scalar header and an explicit ? paths key as no trigger or no path filter, and a flow mapping spanning lines under jobs: as jobs, so a pull-request workflow can drop out of the reconciliation and the check pass; latent
status: untriaged
feature: one-answer
touches: tools/required_checks_check.py, tests/unit/test_required_checks_check.py
added: 2026-10-04
recurrences: 2026-10-04 PL-GWQ7 withdrawn 2026-10-04 PL-R417
---

**Problem.** required_checks_check reads an on: value opening on the line after the key, a block-scalar header and an explicit ? paths key as no trigger or no path filter, and a flow mapping spanning lines under jobs: as jobs, so a pull-request workflow can drop out of the reconciliation and the check pass; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

YAML 1.2.2 § 7.3.3, § 7.4, § 8.1 and § 8.2. `_triggers` reads `on:` over `  pull_request` (PyYAML: 'pull_request') and `on:` over `  [push, pull_request]` as no events, and `on: >-` over `  pull_request` as the event `>-`; an explicit `? paths` key with its value on a `:` line escapes the path-filter refusal. `_jobs` and `_key_at` read `jobs:` over `  {lint: {name: Lint, ...}}` as a job named `{lint`, and a flow mapping carried past `jobs:`'s line as a phantom job `runs-on`. A workflow read as triggering nothing drops out of `reporting_jobs`, so the reconciliation passes without it, the shape `PL-H8YD` names. `PL-R417`'s third slice refuses a flow sequence carried past `on:`'s line; these are the forms it left. `PL-848V` (a block sequence and a one-line flow mapping) and `PL-C72H` (a branch filter) are the same function's other misreadings, outside this head; with this item they are members of `PL-848V`, the head for which events a workflow's `on:` names. Latent: every live `on:` is a block mapping.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
