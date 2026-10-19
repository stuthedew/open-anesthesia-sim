---
id: PL-87BR
title: Have the API-credit runner commit a record of each headless run to the worker's branch, and refuse the branch's merge until the reviewing session adds the review's outcome, so headless work can be compared with chat sessions
priority: P2
effort: M
status: ready
classes: feature
touches: tools/worker_runs.py, tools/headless_worker.py, tests/unit/test_worker_runs.py, tests/unit/test_headless_worker.py, docs/worker-runs, docket.toml, tools/rules_paths_check.py, Makefile, .github/workflows/quality.yml, docs/apparatus.md, docs/maintainer.md
deferred-from: v0.6.0 - a workflow-lane runner feature outside the layout release
added: 2026-10-19
payoff: every headless worker run leaves a record in the repository of its model, effort, cost and review outcome, so headless and chat work can be compared
verify: grep -q 'worker_runs.py check' Makefile && grep -q 'worker_runs' tools/headless_worker.py
---

**Problem.** Nothing in the repository records that an item was done by a headless worker on the API credit (`tools/headless_worker.py`), or how its review went. The runner's ledger holds each run's model, effort, cost and turns, but only on the owner's Mac. `docs/session-ledger.tsv` is filled from cloud sessions, so a headless run never appears there. The branch name `claude/<id>-worker` marks a run, but the daily sweep deletes the branch. The first run, on PL-3R6L (#1681), is recorded only because the reviewing session typed its facts into the pull request body, which this repository's squash keeps as the commit message (`73013ffc`).

**Why it matters.** The owner wants to compare headless work with chat-session work, so that a difference in quality between the two shows up in the record rather than in someone's memory (project owner, 2026-10-19).

**Decided** (project owner, 2026-10-19, ratified, over the reviewing session copying the run's facts into the pull request body by hand, which nothing enforces): the runner writes the record, and a check refuses the merge until the review's outcome is in it.

**The design.**

1. A new standard-library module, `tools/worker_runs.py`, owns the record format, so the runner, the reviewer and the check read one definition. It has three commands: write (the runner calls it), `review` (the reviewing session runs it), and `check` (`make check` and CI run it).
2. After a run whose branch reached the remote, the runner writes `docs/worker-runs/<branch without claude/>-<started, %Y%m%dT%H%M%S>.json` in the clone. It holds the run's ledger fields: item, model, effort, branch, started, finished, exit code, cost, error flag, subtype, turns, denials and reason. It also holds the four token counts from the result's `usage`, as Claude Code reported them: input, cache read, cache write and output. It omits the clone's local path. It ends with `"review": null`. The runner commits it as `<id>: record the headless run` and pushes, through `docket.vcs` like every other git call in the runner. One file per run means no two worker branches edit the same file.
3. The reviewing session runs `python3 tools/worker_runs.py review <file> --outcome accepted|fixed|sent-back --note "<one line>"` before opening the pull request. `fixed` means the reviewer committed fixes, as on #1681. `sent-back` means the branch is not merged as it stands.
4. `python3 tools/worker_runs.py check` fails on any record whose `review` is missing or malformed, or whose fields do not match the format. It is wired into `make check` and into CI's `quality.yml` the way `tools/rules_paths_check.py` is, so a worker branch cannot go green until its review is written.
5. Also: add `docs/worker-runs` to `docket.toml`'s `workflow_paths`, and list it in `tools/rules_paths_check.py`'s `LANE_ONLY` with the records. Add the module and its directory to `docs/apparatus.md`. Add the review step to `docs/maintainer.md` § "Spend the monthly API credit on delegable items". Add `tests/unit/test_worker_runs.py` to `workflow_paths`. A run that pushed nothing writes no record, because it has no branch to carry one; the local ledger keeps it.

**Done when.** A pushed run's branch carries its record, `make check` fails on a record with no review, and passes once `review` writes one. Tests cover the write from a fake run, the review command and each refusal of the check.

**Generator check.** A one-off: the fact "this item was worked headless, and here is how its review went" had no record anywhere, so this writes the first one rather than adding a second reader.
