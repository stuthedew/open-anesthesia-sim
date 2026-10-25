---
id: PL-WJJ8
title: On a worker branch, make check's bin/docket check --verify fails the worked item as 'open but its verify: command already passes', because docs/worker.md forbids a worker to set status: done, so a worker that finishes its item correctly can never report the gate green
priority: P2
effort: M
status: done
classes: defect
feature: worker-runs
milestone: v0.6.7
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_checks.py, tools/headless_worker.py, tests/unit/test_headless_worker.py, docs/worker.md, docs/items
added: 2026-10-20
closed: 2026-10-25
pr: 1800
payoff: a worker that finishes its item correctly can report make check green, so a red gate on a worker branch means a real failure
verify: grep -q 'def test_a_worked_item_on_a_worker_branch_passes_the_replay' subprojects/docket/tests/test_checks.py
reenters: PL-6TP8
---

**Problem.** On a worker branch, make check's bin/docket check --verify fails the worked item as 'open but its verify: command already passes', because docs/worker.md forbids a worker to set status: done, so a worker that finishes its item correctly can never report the gate green

**Observed.** The headless worker on `PL-15TY` saw this on 2026-10-20. After the work was committed, `bin/docket check --verify --verify-base origin/main`, one of `make check`'s steps, exited 1 with the error "PL-15TY is open but its `verify:` command already passes (1 of 5 checked)". The worker's `verify:` passing is the intended outcome. The check in `subprojects/docket/src/docket/checks.py` that raises this error reads an open item whose command passes in only two ways: the work landed and nobody closed the item, or the command does not discriminate. On a worker branch there is a third reading. The work is done and awaits review, and `docs/worker.md` forbids the worker to set `status: done` ("Marking work done is the reviewer's"). So the check makes `make check` red on every correctly worked delegated item. Meanwhile `docs/worker.md` asks the worker to report `make check` passing before finishing.

**Done when.** A worker who finishes an item and leaves its status alone, as `docs/worker.md` requires, can get a green `make check`. The check still catches a non-discriminating `verify:` command on an item nobody has worked.

**Why it matters.** Every correctly finished delegated item turns `make check` red on its worker branch, so the worker reports failure and the reviewing session must work out which failure is this known one. A gate that is red on every run whether or not anything is wrong teaches its readers to ignore it. **Checked 2026-10-24:** the error that `_check_landed` in `subprojects/docket/src/docket/checks.py` raises has no reading for a worker branch.

**Generator check.** An instance of the fact "what a `verify:` command's exit status proves about its own item's work", which `PL-6TP8`'s `misread:` states. The check assumes only two causes of a passing command on an open item, and a worker branch is a third. `PL-6TP8` closed on 2026-09-19. Recorded as `reenters: PL-6TP8`.

**Checked 2026-10-25 (`PL-F2NX`, Gate 3's staleness sweep): still true.** `_check_landed` still offers two readings, an item nobody closed or a command that does not discriminate, and nothing in it asks whether the branch is a worker's. `docs/worker.md` still says "Never change an item's `status`".

**Built, 2026-10-25.** `tools/headless_worker.py` names the worker's item in the environment variable `DOCKET_WORKER_ITEM`, whose name `docket.checks.WORKER_ITEM_ENV` owns. `bin/docket check` passes it to `analyze` as `worked`. On that run, `_check_landed` reports the named item's passing command as an advisory saying the work is done and the reviewer closes it, and every other open item whose command passes is still the two-reading error. The variable was chosen over reading the branch name, because the worker branch's name is built in `tools/headless_worker.py` and parsing it in docket would be a second copy of that grammar. It was also chosen over the run record, because the runner commits the record only after the worker finishes, and the worker runs `make check` before that. Tests: `test_a_worked_item_on_a_worker_branch_passes_the_replay` in `subprojects/docket/tests/test_checks.py`, and the worker's environment in `tests/unit/test_headless_worker.py`. `docs/worker.md` says so beside its rule that a worker never changes an item's status.
