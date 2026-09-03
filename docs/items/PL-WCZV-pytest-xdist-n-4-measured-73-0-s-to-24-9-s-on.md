---
id: PL-WCZV
title: pytest-xdist -n 4 measured 73.0 s to 24.9 s on the full suite with coverage identical at 100 percent; decide whether to take the dependency and where the flag lives
priority: P2
effort: S
status: done
classes: perf, infra
feature: dev-tooling
touches: pyproject.toml, uv.lock, Makefile, .github/workflows/quality.yml
added: 2026-09-03
closed: 2026-09-03
verify: uv run pytest -q tests/unit/test_tools_portability.py && grep -q 'pytest-xdist' pyproject.toml
---

**Problem, or rather the opportunity.** `uv run pytest --cov` is the single largest
item in `make check` - measured 2026-09-03 at 76.0 s of a 115.0 s total, 66% - and it
runs on one core of four. Measured on the same checkout, with `uv run --with
pytest-xdist` so nothing in `uv.lock` moved:

| | wall clock | result |
| --- | --- | --- |
| serial (today) | **73.0 s** | 1210 passed |
| `-n 2` | **39.1 s** | 1210 passed |
| `-n 4` | **24.9 s** | 1210 passed |
| `-n 8` | **23.7 s** | 1210 passed |

The knee is at the core count, as it is for `landed_workers()`. Serial CPU accounting
for the same run: 73.0 s wall against 43.2 s user + 5.2 s sys, so roughly a third of
the serial wall clock is already spent waiting rather than computing - the subprocess
shell-outs in `subprojects/docket/tests`.

**Coverage is unaffected**, which is the property that has to hold before anything
else matters. Both runs report `TOTAL 691 statements, 0 missed, 78 branches, 0
partial, 100%` and clear `--cov-fail-under=100` identically.

**Why it matters.** This is the largest single measured saving available in the local
gate, and it removes work rather than checks - every test still runs and coverage is
byte-identical, which is the same property that made concurrency the right answer for
`PL-LXR3` and caching the wrong one.

**Costs to weigh, not yet resolved.**

- **A dependency.** `pytest-xdist` pulls `execnet`. The dev group is currently exactly
  `mypy`, `pytest`, `pytest-cov`, `ruff`; this makes it five, and `drift.yml` watches
  the toolchain for movement.
- **Ordering.** xdist distributes tests across processes, so any latent inter-test
  dependency that serial ordering hides becomes a failure. 1210 passed at `-n 2`,
  `-n 4` and `-n 8` on this tree, which is evidence rather than proof; the suites that
  shell out and share a working tree (`subprojects/docket/tests`, `tests/unit/
  test_docket_digest_hook.py`) are where it would surface.
- **Where the flag lives.** Not in `[tool.pytest.ini_options] addopts` - for the same
  reason the Makefile gives for keeping `--cov` off it: a session iterating with
  `uv run pytest tests/unit/test_x.py` would pay worker startup for a handful of
  tests and lose. The Makefile line and the CI step are the two places it belongs.
- **CI gain is unmeasured.** GitHub's standard `ubuntu-latest` runner is smaller than
  this four-core container, so the CI saving is not the one measured above and should
  be measured rather than assumed.

**Where.** `pyproject.toml` dev dependency group, `Makefile`'s `check` target,
`.github/workflows/quality.yml`'s `checks` job.

**Done when.** Either the flag is in place with the saving measured on CI as well as
locally, or the decision not to take the dependency is recorded here with its reason.

**Worked.** `pytest-xdist` in the dev group, `-n auto` on the `Makefile` line
and the CI step, and on neither `addopts` nor a config table.

Measured on this checkout after the change, 1230 tests, four cores:

| | wall clock | result |
| --- | --- | --- |
| serial (before) | **78 s** | 1230 passed |
| `-n auto` | **26.9 s** | 1230 passed |
| whole `make check` | **115.0 s -> 59.2 s** | all checks passed |

**Coverage is identical**, which is the property that had to hold before the
wall clock mattered at all: `691 statements, 0 missed, 78 branches, 0 partial,
100%`, clearing `--cov-fail-under=100` exactly as the serial run did. The
threshold stays on the command line and was not relaxed to pay for the
parallelism.

**`-n auto` rather than a pinned number**, which the brief left open. The knee
is at the core count, so a pinned `4` would be right here and wrong on the CI
runner and wrong again on the project owner's machine - and the Makefile line
and the CI step have to stay identical, which a machine-specific number would
make impossible to check by eye. `auto` reads the box it is on and keeps one
string in both places.

**On the ordering risk the brief raised.** xdist distributes tests across
processes, so a latent inter-test dependency that serial ordering hides becomes
a failure - and the suites that shell out and share a working tree were named as
where it would surface. Three consecutive `-n auto` runs passed all 1230 (28.1
s, 26.9 s, 26.3 s), as did `-n 2`, `-n 4` and `-n 8` before the change. That is
evidence rather than proof, and it is the reason the flag went in with the
default `--dist load` rather than a stricter mode: nothing has yet been observed
that `loadfile` or `loadscope` would fix, and reaching for one now would be
guarding a fault nobody has seen.

**CI's saving is measured by CI, not here**, as the brief required - the runner
is smaller than this four-core container. The first run of this pull request is
the measurement.

**What it changes about where the time goes.** `bin/docket check` is now the
largest single item in `make check` at 30.5 s of 59.2 s, having been a quarter
of it. The suite is no longer the thing to look at; the queue's own check is.
`PL-KCQ7` and `PL-PGY4` are the two items that bear on it.
