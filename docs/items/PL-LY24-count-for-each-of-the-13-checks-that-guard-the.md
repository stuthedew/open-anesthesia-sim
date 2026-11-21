---
id: PL-LY24
title: Count, for each of the 13 checks that guard the workflow's own records, how many of its refusals caught a real mistake
status: untriaged
feature: standing-weight
added: 2026-11-20
---

**Problem.** Count, for each of the 13 checks that guard the workflow's own records, how many of its refusals caught a real mistake

**Why it matters.** `make check` runs 29 commands, and 13 of them guard the workflow's own records. They are `bin/docket check`, `tools/branch_id_check.py`, `tools/pr_title_check.py`, `tools/pr_record_check.py`, `tools/pr_body_check.py`, `tools/rules_paths_check.py`, `tools/worker_runs.py`, `tools/dead_ends.py`, `tools/fact_home_check.py`, `tools/config_home_check.py`, `tools/model_home_check.py`, `tools/workflow_paths_check.py` and `tools/fixture_id_check.py`. `CLAUDE.md` § "Prefer deterministic tooling over repeated model work" retires a check that changes no decision, and nobody has counted what these 13 changed. To 2026-10-26, `docs/ci-runs.tsv` records 5,475 runs of the pull-request-title check, and 319 failed. The model review of 2026-10-25 in `docs/model-review.md` found that 195 of 335 failed CI runs came from two checks that fail by design until a later step. `PL-WKKH` (the streamlining questions from the study of the one-shot rewrite) holds the measurements and the sources.

**Answered 2026-11-20.** The owner agreed to the count, before any check is retired (project owner, 2026-11-20, ratified, "Agree with recs", over retiring a check on its description alone).

**What to do.** Build one table of the 13. For each, give the record it guards, its lines of code and of tests, how many times it refused, and how many of those refusals caught a real mistake. Then recommend for each whether to keep it, or to retire it together with the record it guards.

**Done when.** The owner has the table and a recommendation for each check.
