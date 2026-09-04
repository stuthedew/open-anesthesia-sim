---
id: PL-8BFV
title: bin/docket check is now the largest item in make check - 30.5 s of 59.2 s after PL-WCZV, where it was a quarter
priority: P2
effort: M
status: done
classes: perf, infra
touches: subprojects/docket/src/docket/verify.py, Makefile
feature: dev-tooling
added: 2026-09-03
closed: 2026-09-04
not-delegable: the outcome is a decision to accept a standing cost, so there is no state a command could find different afterwards. A command could only grep this file for its own conclusion, which proves the sentence was written rather than that the cost is acceptable - and whether it is acceptable is the judgment this item exists to record
---

**Problem.** Not a defect - a change in where the time goes, recorded because it
moves what is worth working on next.

Measured on this checkout, four cores, warm caches, before and after `PL-WCZV`
put `-n auto` on the suite:

| step | before | after |
| --- | --- | --- |
| `pytest --cov` | 76.0 s (66%) | **26.9 s (45%)** |
| `bin/docket check` | 28.8 s (25%) | **30.5 s (51%)** |
| `mypy` | 7.6 s | 7.6 s |
| everything else | ~2.5 s | ~2.5 s |
| **total** | **115.0 s** | **59.2 s** |

**Why it matters.** Every previous session's answer to "what is slow" was the
suite, and that is no longer true: the queue's own check is now more than half
of `make check` and it is the half that grows with the store. The suite's cost
is roughly fixed per test and now spread across cores; the check's is 82
subprocesses whose count rises with every item triaged to `ready`.

**What is already known about it**, so the next session does not re-derive it:

- The pool is at its concurrency floor - measured 31.6 s at four workers, 28.0 s
  at eight, 32.4 s at sixteen, 32.5 s at twenty-four (`PL-PGY4`). More width is
  not the lever.
- Deduplication is not the lever either: all 82 commands are textually distinct,
  because each pairs a pytest run with a `grep` for its own test name.
- `uv run` overhead is not the lever: measured 13 ms against `.venv/bin/python`
  directly. The 0.64 s median is pytest import and collection.
- Caching by tree state and asking fewer items were both considered and rejected
  under `PL-LXR3`, and that reasoning has not changed.
- 29.2 s of the suite's own time tests `subprojects/docket` rather than the
  simulator (`PL-KCQ7`), which is the same apparatus this check belongs to.

**So the open levers are the ones nobody has costed**: fewer candidates,
cheaper candidates, or moving the landed probe out of the local gate and
leaving it to CI - where it is already the largest step at 72 s of a 164 s job.
Each trades something real, which is why this is a capture rather than a
recommendation.

**Done when.** A decision is recorded, including the decision to accept it.

**Decision needed.** Which of the three uncosted levers to spend a session on,
or whether to accept the cost. Fewer candidates and cheaper candidates both
weaken what the check proves; moving the landed probe out of the local gate
keeps the proof and pays for it at CI instead, ~2.6 min later, where it is
already the largest step. Accepting it is a real answer and gets more defensible
as the queue's growth slows.

**Decided (project owner, 2026-09-04): accept it. No change.** The four levers
were measured against each other before the decision rather than argued from
the shape of the code; what follows is the evidence, so this is not reopened
without new information.

**The frame.** A pool's wall clock is `max(slowest single command, total work /
workers)`. Measured on this store, 82 candidates at eight workers:

| term | measured |
| --- | --- |
| slowest single command (`PL-GS5X`) | **28.8 s** |
| total work / 8 | 201.4 / 8 = **25.2 s** |
| observed pool | **30.6 s** |

The two terms are within 15% of each other, so the check sits almost exactly at
the crossover between the regimes `PL-FRGP` describes. That is what makes this
hard to reason about from intuition: **a lever that moves only one term buys
almost nothing**, because the other immediately binds.

**Where the cost actually is.** Not in the length of the queue:

| | share of the 201.4 s total | remainder / 8 |
| --- | --- | --- |
| top 1 command | 14.3% | 21.6 s |
| top 5 | 49.1% | 12.8 s |
| top 10 | 68.4% | 8.0 s |
| the 57 commands under 1 s | 15.1% | - |

Fifty-seven of eighty-two commands cost 30 s between them. Each newly `ready`
item adds about 0.09 s to the pool (0.69 s median / 8 workers). The pool went
10.1 s to 30.6 s in two days while candidates grew only 49 to 82 - that
tripling was heavy commands arriving, not the queue lengthening.

**The four levers, measured.**

- **Fewer candidates** (scope the probe to what `next` offers). `docket next`
  names 12 ids against 82 candidates - but `PL-HKF4` is *both* in that set and
  the third-heaviest command at 18.7 s, and the pool is floor-bound on its
  slowest member. So the saving depends on which heavy commands happen to sit
  near the top of the queue, which is the worst property a gate can have. It
  also costs the already-passes advisory, which is the check's main product and
  named nine real landed-but-unclosed items. Rejected under `PL-LXR3` for that
  reason; the measurement makes it worse than that item knew.
- **Cheaper candidates** (narrow the heavy commands). The largest headroom:
  narrowing the top five takes the aggregate term to 12.8 s. But each `verify:`
  is a specification of what proves its item done, so narrowing one means
  proving less - and `PL-GS5X`'s reference test is the point of that item, the
  case `PL-5TN8` identified as genuinely un-narrowable.
- **Move the landed probe out of the local gate.** Removes 30.5 s locally and
  nothing on CI, where the same check is 70 s of a 142 s job. It relocates cost
  rather than removing it, and buys the relocation with a slower answer to the
  question the queue depends on.
- **Deduplicate by pytest invocation.** Newly measured here and not previously
  considered: the 82 commands make 79 pytest invocations across only **28
  distinct files**, and `subprojects/docket/tests/test_cli.py` runs **ten**
  times. Running each distinct pytest half once and applying each item's `grep`
  separately is not the caching `PL-LXR3` rejected - every command still runs
  against the current tree in this run, so no answer can move. Measured: serial
  work falls 201.4 s to 134.3 s, a third, and **the pool falls only 30.6 s to
  27.3 s**, because `PL-GS5X` still sets the floor. A 3.3 s win for real parser
  complexity.

**Why accepting is right rather than merely cheapest.** The reason this became
worth asking about was that the cost had tripled unseen: a healthy store printed
nothing about what the check cost, so nobody could notice the number move. That
is fixed, in the two items that preceded this one - `PL-9NKK` puts the count,
elapsed, serial total and worst-case margin on every run, and `PL-FRGP` makes
the advisory tell the truth about what narrowing a heavy command would buy. The
blindness was the problem; 30 s is a price.

**Revisit when the instrumentation says to**, which is now something it can do:
when the cost line shows the serial total climbing without heavy commands
arriving, or when the slowest command approaches the 120 s limit and the check
starts declining instead of answering. The dedup lever stays available and
becomes interesting only paired with narrowing `PL-GS5X`, since dedup collapses
the four `test_cli.py` commands into one - that pairing is the only route
measured that would roughly halve the check.
