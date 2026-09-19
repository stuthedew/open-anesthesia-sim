---
id: PL-FZ58
title: Three test files carry 59% of the verify replay's 1458s serial cost, each re-run once per item whose verify: command names it
priority: P2
effort: S
status: done
classes: perf
feature: verify-replay-cost
touches: docs/items
added: 2026-09-19
closed: 2026-09-19
pr: 711
verify: grep -qF 'arriving through the tap rather than the bucket' docs/items/PL-FZ58-three-test-files-carry-59-of-the-verify-replay.md
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

**Answered 2026-09-19. Neither direction above is the work, and the third one
is.** Re-measured on this checkout; the wall-clock figures differ from the
brief's because the box does, so read the ratios rather than the seconds.

**Direction 2 — stop paying the file's runtime per item — is refused, and the
measurement is what refuses it.** 31 open items name one of the three files; 25
of them carry a strippable clause (the other 6 already record a bare `grep`, or
a prerequisite that is not pytest), worth 505.7 s of this checkout's 1,458 s
equivalent. Stripping those 25 in one pass is the alternative `PL-6TP8` offered
and the project owner declined on 2026-09-19, ratifying repair-as-started on the
argument that "the replay's bill falls as the queue turns over rather than in
one day". **That argument holds, on a number the case did not carry:** the queue
closed 672 items in the fourteen dated days to 2026-09-19 — 48/day against 324
open — so a specific 25 drain in about a week, which is faster than a 25-file
pull request would matter. The collision objection is also small today (0 of the
25 files are edited on any of this checkout's 23 non-`main` refs), but that is
not what decides it; the drain rate is. A session reaching this item should not
re-open the decision on the scope being 25 rather than 162.

**Direction 1 — make the three files cheaper — is worth much less than this
brief assumes**, and the clause "which helps every consumer including `make
check`" is the part that does not survive measurement. Serial cost of the whole
suite, 3,180 tests, this checkout:

| file | serial | share |
| --- | --- | --- |
| `tests/reference/test_coupled_dynamics.py` | 74.2 s | 27.2% |
| `tests/reference/test_published_wash_in_and_elimination.py` | 37.5 s | 13.8% |
| `tests/integration/test_simulation_view.py` | 28.4 s | 10.4% |
| **the three files this item names, together** | **63.7 s** | **23.4%** |

A single reference file outweighs all three, and `make check` already runs the
suite at `-n $(cpu*2) --dist worksteal`: 77.8 s wall against 272 s serial on
four cores, which is within 11% of the CPU floor rather than a scheduling loss.
So deleting the three files outright would buy about 16 s of a 78 s run, and
the two files above them are reference validation that `CLAUDE.md`'s
safety-critical standard asks for — not cost to trade away. The three also have
no outlier to remove: their slowest single tests are 2.5 s, 1.3 s and 0.6 s,
and the cost is per-test git-fixture overhead spread across 304 tests.

**What was actually left, and is now fixed: the inflow.** Repair-as-started
drains a *closed* set, and nothing closed it. 82 of 180 open commands carried
the shape, 23 of them written on 2026-09-14 alone, and what prescribed the
replacement was one table in `.claude/skills/docket/SKILL.md`. `PL-09G9` makes
the decidable half a check, so the 59% now provably goes to zero as the queue
turns over instead of being re-fed. That is the reduction this item asked for,
arriving through the tap rather than the bucket.

**Done when** — met. The three files' clauses do not "have to stay"; they drain,
and what needed building was the thing stopping new ones.
