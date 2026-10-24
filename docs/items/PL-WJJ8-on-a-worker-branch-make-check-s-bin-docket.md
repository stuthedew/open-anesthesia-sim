---
id: PL-WJJ8
title: On a worker branch, make check's bin/docket check --verify fails the worked item as 'open but its verify: command already passes', because docs/worker.md forbids a worker to set status: done, so a worker that finishes its item correctly can never report the gate green
status: untriaged
added: 2026-10-20
---

**Problem.** On a worker branch, make check's bin/docket check --verify fails the worked item as 'open but its verify: command already passes', because docs/worker.md forbids a worker to set status: done, so a worker that finishes its item correctly can never report the gate green

**Observed.** The headless worker on `PL-15TY` saw this on 2026-10-20. After the work was committed, `bin/docket check --verify --verify-base origin/main`, one of `make check`'s steps, exited 1 with the error "PL-15TY is open but its `verify:` command already passes (1 of 5 checked)". The worker's `verify:` passing is the intended outcome. The check in `subprojects/docket/src/docket/checks.py` that raises this error reads an open item whose command passes in only two ways: the work landed and nobody closed the item, or the command does not discriminate. On a worker branch there is a third reading. The work is done and awaits review, and `docs/worker.md` forbids the worker to set `status: done` ("Marking work done is the reviewer's"). So the check makes `make check` red on every correctly worked delegated item. Meanwhile `docs/worker.md` asks the worker to report `make check` passing before finishing.

**Done when.** A worker who finishes an item and leaves its status alone, as `docs/worker.md` requires, can get a green `make check`. The check still catches a non-discriminating `verify:` command on an item nobody has worked.
