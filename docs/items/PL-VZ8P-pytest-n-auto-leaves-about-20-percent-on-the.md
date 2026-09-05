---
id: PL-VZ8P
title: pytest -n auto leaves about 20 percent on the table because much of the suite waits on subprocesses rather than CPU
priority: P3
effort: S
status: needs-decision
classes: session-cost, infra
feature: dev-tooling
touches: Makefile, .github/workflows/quality.yml
added: 2026-09-05
---

**Problem.** `-n auto` sets one worker per CPU, which is right for a CPU-bound
suite. A large part of this one is not: `subprojects/docket/tests` shells out to
git, and `test_verify.py` runs literal `sleep` commands. A blocked worker holds a
core it is not using.

Measured 2026-09-05, four cores, 1534 tests, whole suite, `--cov` on:

| invocation | wall |
| --- | --- |
| `-n auto` (the current line) | 27.0 s (26.5 / 27.3 / 27.4) |
| `-n auto --dist worksteal` | 25.6 s |
| `-n 8` | 27.5 s |
| **`-n 8 --dist worksteal`** | **21.4 s** (21.6 / 21.2 / 21.5) |
| `-n 6 --dist worksteal` | 19.8 s |
| `-n 16 --dist worksteal` | 24.3 s |

Neither change helps alone; the pair does. Oversubscribing gives the scheduler
somewhere to go while a worker waits on a subprocess, and `worksteal` is what
stops the extra workers idling on an unlucky static split. Past about 2.5x cores
it degrades again.

Coverage is identical under the winning form - 730 statements, 92 branches,
100% - which is the admissibility test the `-n auto` comment in the `Makefile`
already sets for a parallelism flag (`PL-WCZV`).

**Why it matters.** It is `make check`'s whole remaining cost. After `PL-P3B6`
took the verify replay out, the gate is 29.1 s and pytest is 27.0 s of it;
everything else measures under a second warm except `tools/ignore_check.py` at
3.2 s, which shells out to mypy twice and is inherent. So this is the only lever
left above noise.

**Where.** The pytest line in `Makefile`'s `check` target, the identical line in
`.github/workflows/quality.yml`'s `checks` job, and `make test`.

**Decision needed.** Which is why this is `needs-decision` rather than `ready`.
A pinned `-n 8` contradicts a stated design principle: the `Makefile` comment
says `-n auto` "reads this runner rather than carrying a width pinned here, so
the two lines stay identical across machines of different sizes", and `PL-D3M2`
turns on those two lines being checkable against each other by eye. Three ways
out, and the choice is the project owner's:

1. Pin `-n 8`. Simplest, eye-identical across the two files, wrong on a box that
   is not four cores.
2. Express the rule instead - `-n $$(( $$(nproc) * 2 ))` in the `Makefile` and
   `-n $(( $(nproc) * 2 ))` in the workflow. Keeps the "reads this runner"
   property; costs the literal eye-identity `PL-D3M2` wants.
3. Take `--dist worksteal` only, and leave the width alone. Worth 1.4 s rather
   than 5.6 s, and gives up most of the win, but changes no principle.

`-n logical` is not a fourth option: it was measured and equals `-n auto` here,
because psutil is absent so xdist falls back to `os.cpu_count()`.

**Done when.** The pytest invocation in `Makefile` and `quality.yml` carries
whichever form the owner picks, with the measurements above in a comment beside
it, and coverage still reports 730/92/100%.
