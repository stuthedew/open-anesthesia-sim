---
id: PL-VZ8P
title: pytest -n auto leaves about 20 percent on the table because much of the suite waits on subprocesses rather than CPU
priority: P3
effort: S
status: done
classes: session-cost, infra
feature: dev-tooling
milestone: v0.4.0
touches: Makefile, .github/workflows/quality.yml
added: 2026-09-05
closed: 2026-09-05
pr: 328
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_makes_doubled_dollar_is_not_read_as_a_drift' tests/unit/test_doc_check.py
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

**Decision taken** (project owner, 2026-09-05): option 2, the computed rule.
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

**What landed.** `-n $(python3 -c 'import os; print(os.cpu_count() * 2)')
--dist worksteal` in `Makefile`'s `check` target and `quality.yml`'s `checks`
job, with the measurements in a comment beside it. `python3` rather than `nproc`
because `nproc` is GNU coreutils and absent on macOS, and because
`os.cpu_count()` is exactly what xdist's own `auto` falls back to here - so the
line is literally twice what `auto` would have picked.

Re-measured on the merged base, 1577 tests rather than the 1534 the table above
was taken on: **34.2 s -> 26.3 s**, a larger win than first measured, because the
suite grew by 43 mostly I/O-bound tests.

Two things the decision turned out to carry that the item did not foresee:

- **`make test` keeps `-n auto`.** A computed width resolves to an integer, and
  `--pdb` rejects an integer - verified 2026-09-05, `-n auto --pdb` passes and
  `-n 8 --pdb` errors with `--pdb is incompatible with distributing tests`. That
  copy-safety is a documented property of that target (`PL-FX3N`), and `check`
  can spend it only because it is a gate that takes no arguments. `make test`
  takes `--dist worksteal` alone, which `--pdb` tolerates.
- **`PL-D3M2` was never a by-eye promise - it was already a check, and the
  change broke it.** `tools/doc_check.py`'s `check_coverage_gate` compares the
  two lines by exact string equality, and its docstring said `-n auto` had been
  chosen partly to keep them identical. A computed width is spelled `$$(...)`
  in a recipe and `$(...)` in a workflow, so `make check` failed on the one
  character Make requires. Fixed where the check lives rather than beside it:
  the Makefile side collapses `$$` to `$` first, which is a documented rule of
  Make rather than a judgment, so the comparison stays exact and every other
  difference is still a drift. A first attempt added a parallel test under
  `tests/unit/` and was deleted as duplication once the existing check
  surfaced.

**Done when.** Landed.
