---
id: PL-FZ58
title: Three test files carry 59% of the verify replay's 1458s serial cost, each re-run once per item whose verify: command names it
status: untriaged
feature: verify-replay-cost
added: 2026-09-19
---

**Problem.** Three test files carry 59% of the verify replay's 1458s serial cost, each re-run once per item whose verify: command names it

**Where it comes from.** Measured 2026-09-19 on this checkout: 179 candidate
`verify:` commands, 1458 s run serially, 204 s wall at eight workers. Grouping
every command by the pytest target it names:

| target | items running it | serial | median |
| --- | --- | --- | --- |
| `subprojects/docket/tests/test_cli.py` | 14 | **415 s** | 40.2 s |
| `tests/unit/test_doc_check.py` | 12 | **292 s** | 28.4 s |
| `subprojects/docket/tests/test_verify.py` | 4 | **152 s** | 53.9 s |

Three files, **859 s — 59% of the store's whole serial cost.** Each item's
command runs the file from scratch, so the file's own runtime is multiplied by
the number of open items whose discriminator happens to live in it.

**Why it matters.** The replay's floor is `serial / workers` — 182 s of the
204 s measured — so this is the cost, not any one command. `PL-G6J5` retired
the outlier advisory on the finding that no single command is what the run
waits for; this is what is there instead, and no per-command test can express
it. It also grows the wrong way: every item triaged to `ready` whose
discriminator sits in one of these three files adds that file's full runtime
again.

**Two directions, and they are not exclusive.** Either make the three files
cheaper, which helps every consumer including `make check` — `test_cli.py` at
40 s for one file is the first thing to look at. Or stop paying the file's
runtime per item: `PL-6TP8` (project owner, 2026-09-19, ratified) already
decided a `verify:` should be the `grep` for the test the work adds and
*nothing ahead of it*, on the grounds that the suite is run separately by
`make check`, `docs/worker.md`'s loop and CI. The commands recorded before that
date still carry the `pytest` clause, and these three files are where it costs
most — so this is that decision's backlog, quantified.

**Done when** the 59% is measurably reduced, or the item records why the
pytest clauses in these three files' commands have to stay.
