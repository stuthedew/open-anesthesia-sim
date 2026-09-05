---
id: PL-SDHR
title: The verify replay is 87s of the checks job's 152s, and nothing in the workflow records what it now costs
status: untriaged
feature: ci-cost
touches: .github/workflows/quality.yml, subprojects/docket/src/docket/verify.py
added: 2026-09-05
---

**Problem.** `bin/docket check --verify` is the most expensive step in CI, by
a margin, and it is the one step whose cost grows with the size of the queue
rather than with the size of the change.

Measured on run `33998014593` (quality, pull request #364, 2026-09-05), from
the step timings the Actions API reports:

| Step | Wall clock |
| --- | --- |
| checkout, setup-python, five floor commands | 9 s |
| setup-uv, `uv sync --locked --dev` | 4 s |
| ruff format, ruff check, mypy | 6 s |
| `pytest -n … --cov` (1820 tests) | 48 s |
| **`bin/docket check --verify`** | **87 s** |
| the four remaining tool checks | 1 s |
| **job total** | **152 s** |

So the replay is **57% of the job** and costs nearly twice the whole test
suite. It runs on every push to every open pull request.

**Why it grows.** 111 open items carry a `verify:` command and **79 of them
invoke `uv run pytest`** (counted 2026-09-05). Each is a separate pytest
process - interpreter start, conftest import, collection - re-running test
files the suite three steps above has already run. The pool is eight wide
(`landed_workers()`, capped), and `PL-LXR3`/`PL-9NKK` measured sixteen and
twenty-four as *slower*, so width is not the lever. Nothing dedupes: all 111
commands are distinct, checked 2026-09-05, so there is no repeated command to
collapse.

**Why it matters.** Every item added to the queue makes every future pull
request slower, which is the shape that ends badly on a multi-year horizon.
It is also the step that decides whether a session waits two minutes or four
for a green pull request, and this repository routinely has five or six
sessions pushing at once.

**Decision needed.** What the replay is for on a *pull request*, given it
answers a question about the queue rather than about the commit. `PL-P3B6`
moved it here from `make check` on exactly that reasoning, and said "CI wall
clock is not what that item was optimizing" - which was true then and is the
open question now. Four options:

1. **Leave it.** 87 s and rising, paid per push.
2. **Run the full replay on `push: main` only.** Every merge still gets the
   complete answer; a pull request stops paying for it. The finding lands in
   the merge run's log rather than on the pull request, which is the cost -
   and an advisory nobody reads is a retirement candidate under `CLAUDE.md`.
3. **On a pull request, replay only the items the branch touches** - decidable
   from the diff, and exactly the set the session is answerable for - with the
   full sweep on `push: main`. Keeps a finding on the pull request that names
   the session's own items.
4. **Split it into its own job.** Parallel with `checks` rather than serial
   after it, so the wall clock is `max` instead of `sum`. Buys the two minutes
   back for a reviewer but spends more billable minutes, not fewer, because a
   second job rounds up on its own - which is the trade `PL-D551` just made in
   the other direction.

**Recommended: 3.** It keeps a per-pull-request answer about the work in front
of the session, moves the store-wide sweep to the one place it is a fact about
`main`, and it is decidable rather than heuristic. 2 is the cheap version if
the scoped replay is judged not worth the code.

**Where.** `.github/workflows/quality.yml`'s `bin/docket check --verify` step,
and `subprojects/docket/src/docket/verify.py`'s `landed` report if the scope
becomes an argument.

**Done when.** The replay's cost on a pull request is bounded by the change
rather than by the queue, or the decision is recorded that 87 s and rising is
the price and why.

**Found while working the CI-cost items 2026-09-05**, measuring where the
checks job's time actually goes before optimizing anything.
