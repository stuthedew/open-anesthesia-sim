---
id: PL-LY24
title: Count, for each of the 13 checks that guard the workflow's own records, how many of its refusals caught a real mistake
priority: P2
effort: M
status: done
classes: planning
feature: standing-weight
milestone: v0.6.19
touches: docs/items/PL-LY24-count-for-each-of-the-13-checks-that-guard-the.md, docs/ci-runs.tsv, docs/items/PL-CR81-projects-threads-in-the-v0-7-0-project-run.md, docs/items/PL-6LJS-the-pull-request-title-check-and-the-pull.md, docs/items/PL-BBTV-tools-model-home-check-py-refuses-a-model-name.md, docs/items/PL-C3K1-tools-rules-paths-check-py-keeps-the-apparatus.md, docs/items/PL-KGPR-decide-which-of-the-13-checks-on-the-workflow-s.md
added: 2026-11-20
closed: 2026-11-21
pr: 2176
not-delegable: The work is a count of CI refusals sorted by reading each one, and a recommendation to the owner; no command can prove it.
sweep: counts what each of the 13 workflow-record checks refused in CI, and files each defect the count finds
---

**Problem.** Count, for each of the 13 checks that guard the workflow's own records, how many of its refusals caught a real mistake

**Why it matters.** `make check` runs 29 commands, and 13 of them guard the workflow's own records. They are `bin/docket check`, `tools/branch_id_check.py`, `tools/pr_title_check.py`, `tools/pr_record_check.py`, `tools/pr_body_check.py`, `tools/rules_paths_check.py`, `tools/worker_runs.py`, `tools/dead_ends.py`, `tools/fact_home_check.py`, `tools/config_home_check.py`, `tools/model_home_check.py`, `tools/workflow_paths_check.py` and `tools/fixture_id_check.py`. `CLAUDE.md` § "Prefer deterministic tooling over repeated model work" retires a check that changes no decision, and nobody has counted what these 13 changed. To 2026-10-26, `docs/ci-runs.tsv` records 5,475 runs of the pull-request-title check, and 319 failed. The model review of 2026-10-25 in `docs/model-review.md` found that 195 of 335 failed CI runs came from two checks that fail by design until a later step. `PL-WKKH` (the streamlining questions from the study of the one-shot rewrite) holds the measurements and the sources.

**Answered 2026-11-20.** The owner agreed to the count, before any check is retired (project owner, 2026-11-20, ratified, "Agree with recs", over retiring a check on its description alone).

**What to do.** Build one table of the 13. For each, give the record it guards, its lines of code and of tests, how many times it refused, and how many of those refusals caught a real mistake. Then recommend for each whether to keep it, or to retire it together with the record it guards.

**Done when.** The owner has the table and a recommendation for each check.

**Counted 2026-11-21.** The count reads every failed CI run in `docs/ci-runs.tsv`, refreshed on 2026-11-21 with `python3 tools/ci_runs.py refresh` to 18,649 runs from 2026-08-22 to 2026-11-21. A refusal is a run in which the check's own step failed. For each refusal the session read the step's log from GitHub, which keeps logs for 90 days, and the commit that followed on the branch. It sorted each refusal into one of four kinds:

1. **Caught a mistake.** The refused change was wrong by a rule outside the check's own record: a malformed item, a second copy of a fact, a test id the store could never mint, an item left open after its work landed.
2. **Asked for the check's own record.** The change was right, and the refusal asked for an entry that only the check's record holds: a claim, a pull request number, a review line, a path added to a list. A hold that fails by design until a later step is counted here.
3. **Wrong or misdirected.** The check refused correct work, or blamed a branch for another branch's closure.
4. **Not attributable.** The branch is gone and nothing shows what followed.

`bin/docket check` has two rows, its store rules and its replay of `verify:` commands, because they fail for different reasons. "Items" counts the items whose `touches` name the check's code, which is how much upkeep it has cost. "Runs" counts the CI runs since the check was added in which its workflow finished.

| Check | Record it guards | Lines of code and tests | Items | Runs | Refusals | Caught a mistake | Asked for its own record | Wrong or misdirected | Not attributable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `bin/docket check` | Every item file in `docs/items/` | 4,762 and 5,697 (`checks.py`) | 159 | 7,236 | 37 | 8 | 26 | 2 | 1 |
| `bin/docket check --verify` | The `verify:` command of each open item | 3,508 and 4,297 (`verify.py`) | 110 | 7,236 | 146 | 90 | 49 | 0 | 7 |
| `tools/branch_id_check.py` | Claims, and the item ids a branch carries | 616 and 803 | 21 | 6,311 | 12 | 0 | 10 | 2 | 0 |
| `tools/pr_title_check.py` | The ids at the front of each squash commit's subject | 318 and 581 | 13 | 6,809 | 185 | 137 | 0 | 28 | 20 |
| `tools/pr_record_check.py` | The `pr:` field on each closed item | 152 and 374 | 7 | 5,152 | 156 | 3 | 149 | 3 | 1 |
| `tools/pr_body_check.py` | Bodies recovered into `docs/pr-bodies/` | 786 and 827 | 34 | 4,955 | 71 | 0 | 71 | 0 | 0 |
| `tools/rules_paths_check.py` | The `paths:` of each rule in `.claude/rules/` | 538 and 391 | 18 | 6,069 | 6 | 0 | 6 | 0 | 0 |
| `tools/worker_runs.py` | Records of headless worker runs in `docs/worker-runs/` | 273 and 144 | 7 | 2,259 | 2 | 0 | 2 | 0 | 0 |
| `tools/dead_ends.py` | The entries of `docs/dead-ends.md` | 512 and 433 | 13 | 5,537 | 0 | 0 | 0 | 0 | 0 |
| `tools/fact_home_check.py` | One reader for each fact the workflow tools share | 923 and 568 | 17 | 2,908 | 7 | 5 | 0 | 2 | 0 |
| `tools/config_home_check.py` | Copies of 23 configuration facts | 405 and 187 | 2 | 1,963 | 2 | 2 | 0 | 0 | 0 |
| `tools/model_home_check.py` | Model ids, held to `docket.toml`'s `[models]` table | 126 and 77 | 1 | 1,840 | 5 | 1 | 0 | 4 | 0 |
| `tools/workflow_paths_check.py` | Which lane each tracked path belongs to | 421 and 760 | 14 | 5,872 | 1 | 0 | 1 | 0 | 0 |
| `tools/fixture_id_check.py` | `PL-` ids in tests and examples | 665 and 865 | 17 | 4,797 | 2 | 2 | 0 | 0 | 0 |

What the refusals were, check by check:

1. **`bin/docket check`.** The 8 mistakes were an item written by an outside agent with an invalid id and unknown fields (3 refusals), two items sharing one id, a front-matter key written twice, a class outside the vocabulary, and two items left at `blocked` after their blockers closed. Of the 26 record requests, 20 asked for a closed item's pull request number before `PL-HMZZ` moved that job to the number check. The 2 wrong refusals were items moved on purpose to another branch.
2. **`bin/docket check --verify`.** The 90 catches are 9 episodes on `main` in September: an item left open after its work landed, or a `verify:` command that passed without the work. One episode kept `main` red for 50 pushes over a day (`PL-0GTC`). The 49 record requests are 41 refusals on the branch doing that item's own work, before it wrote the closure, and 8 on release-tag items. The last refusal on `main` was on 2026-09-23, the day after `make check` began replaying each branch's own items before a push (`PL-0HPV`).
3. **`tools/branch_id_check.py`.** Ten refusals were branches whose commit subjects already named their items, so other sessions could see them; the refusal asked only for a claim. Two were the owner's own README edit made on GitHub's web page.
4. **`tools/pr_title_check.py`.** In 137 refusals the title left out an item that the same pull request closed or dropped, and 74 refusals cleared with a title edit and no commit. Since `PL-HMZZ` on 2026-09-25, a title's ids reach only the one-line history of `main`, which `git log --oneline`, `bin/docket trend` and `filed_with_work` read. The 28 misdirected refusals blamed a branch for an item that the pull request it was built on had closed (`PL-6LJS`).
5. **`tools/pr_record_check.py`.** 149 refusals came before `PL-86DN` on 2026-10-25, when every pull request failed it by design until `bin/docket record N` was pushed. Since then it has refused 6 times: 3 closures written without the number, and 3 on a branch built on another pull request's branch (`PL-6LJS`).
6. **`tools/pr_body_check.py`.** All 71 refusals were on 2026-09-26, from the `--check` mode that `PL-3PH2` retired later the same day. The `--anchors` mode that runs now has never refused.
7. **`tools/rules_paths_check.py`.** No refusal found a misanchored glob, which is its main rule. All 6 asked for a new workflow path to be added to the apparatus path set, which the check keeps in three copies (`PL-C3K1`).
8. **`tools/worker_runs.py`.** Both refusals were the hold it was built to make, until a reviewer wrote the run's review. The record holds 4 runs, all from 2026-10-20, and none since.
9. **`tools/fact_home_check.py`.** It caught 3 walks of the tree that bypassed `tracked_files`, one path bound under two names in two modules, and constants defined twice in hooks. Its 2 wrong refusals were four constants that shared a name but held different facts, and the fix renamed them.
10. **`tools/config_home_check.py`.** It caught a copy of the clinical paths list in `arming.py` and the tool list in `docs/apparatus.md`, each edited so that it no longer matched its home.
11. **`tools/model_home_check.py`.** It caught a model id written into an open item's instructions (`PL-LJY8`, which two more local commits also fixed). Its 4 wrong refusals were model names inside the web address of a cited prompting guide (`PL-BBTV`).
12. **`tools/workflow_paths_check.py`.** Its one refusal asked for two new tracked files to be placed on a side of the lane boundary.
13. **`tools/fixture_id_check.py`.** Both refusals were test ids the store could never mint (`PL-AA01` and three like it, and `PL-0RE0`). The session did not check whether those tests would have passed vacuously.

**What the count cannot see.** A session runs `make check`, and a push hook runs `bin/docket check --verify`, `branch_id_check` and `doc_check`, before CI does. A refusal fixed before the push never reaches CI, and nothing records it. So every number above is a lower bound. Commit subjects show a few such local catches (three for `PL-LJY8`); a search of all commit messages found no others. Where a step failed, GitHub skips the steps after it, so a check that runs late is undercounted again.

**Recommendation for each check.** Keep a check that catches mistakes in work, or whose record something else reads to route work. Retire one that has refused nothing, or only asked for its own record, once nothing else needs that record. `PL-KGPR` holds the decision.

1. **Keep `bin/docket check`.** Every `bin/docket` command reads the store through it, and it caught 8 mistakes.
2. **Decide `bin/docket check --verify` with `PL-LFJZ`** (the count of what a test-name done-condition would have prevented). While open items carry `verify:` commands, the replay is the only thing that notices an item left open after its work landed, which it did 9 times. If `PL-LFJZ` replaces those commands, retire the replay with them.
3. **Retire `tools/branch_id_check.py`.** It caught no mistake in 12 refusals, and it has cost 21 items. `bin/docket claim` writes the claim it asks for.
4. **Keep `tools/pr_title_check.py`, and fix `PL-6LJS`.** Its 137 catches are small, but they are real, and a title cannot be edited after the merge.
5. **Keep `tools/pr_record_check.py`.** Since `PL-86DN` it has refused 6 times in four weeks, and 3 of those were real.
6. **Retire `tools/pr_body_check.py --anchors`, and keep `docs/pr-bodies/` as a closed archive.** It has never refused, and it has cost 34 items.
7. **Keep `tools/rules_paths_check.py`, and fix `PL-C3K1`.** A misanchored glob fails silently, and the check costs little to run.
8. **Retire `tools/worker_runs.py` and `docs/worker-runs/` unless `PL-6FX6`** (the first month of API-credit worker runs) **goes ahead.** No worker has run since 2026-10-20.
9. **Retire the `check` half of `tools/dead_ends.py`.** It has never refused. The `emit` half feeds the session-start digest and stays.
10. **Keep `tools/fact_home_check.py`.** It caught 5 second copies, which `CLAUDE.md` names as the project's core design rule.
11. **Keep `tools/config_home_check.py`.** Both its refusals were copies that had drifted, one of them the clinical paths list.
12. **Keep `tools/model_home_check.py`, and fix `PL-BBTV`.**
13. **Keep `tools/workflow_paths_check.py`.** Its one refusal made the lane decision it exists to force, and it is cheap.
14. **Keep `tools/fixture_id_check.py`.** Both refusals were ids that tests could not use.

The scripts and the per-refusal sorting are in the project's shared folder, `/mnt/project-files/v0.7.0/check-count/`.

**Generator check.** One-off. It is a measurement the owner asked for, and no fact was misread to cause it.
