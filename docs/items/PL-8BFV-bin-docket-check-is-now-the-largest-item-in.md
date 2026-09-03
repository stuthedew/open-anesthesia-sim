---
id: PL-8BFV
title: bin/docket check is now the largest item in make check - 30.5 s of 59.2 s after PL-WCZV, where it was a quarter
status: untriaged
feature: dev-tooling
added: 2026-09-03
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
