---
id: PL-WCZV
title: pytest-xdist -n 4 measured 73.0 s to 24.9 s on the full suite with coverage identical at 100 percent; decide whether to take the dependency and where the flag lives
priority: P2
effort: S
status: done
classes: perf, infra
feature: dev-tooling
milestone: v0.3.5
touches: pyproject.toml, uv.lock, Makefile, .github/workflows/quality.yml
added: 2026-09-03
closed: 2026-09-03
pr: 276
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

**CI's saving is measured by CI, not here**, as the brief required - and it is
much smaller than the local one, which is the number worth carrying rather than
the flattering one. Measured on `quality.yml`'s `checks` job, the pytest step
alone:

| | CI step | this container |
| --- | --- | --- |
| serial (run 33806497510, 2026-09-03) | **69 s** | 78 s |
| `-n auto` (run 33819958377, 2026-09-04) | **50 s** | 26.9 s |
| saving | **28%** | 65% |

The GitHub-hosted runner is narrower than this four-core box, so `auto` resolves
to fewer workers and the knee arrives sooner. That is the argument for `auto`
rather than a pinned width working in the direction that matters: the same
string gives each machine what it can use, and nobody has to keep a number
current for a runner they cannot see.

**How much narrower, from the log rather than by inference** (added 2026-09-04,
`PL-KCQ7`'s session, which reproduced this measurement before finding the two
had collided). The `checks` step prints `created: 2/2 workers` and `2 workers
[1224 items]`: **two**, not four. The cause is not the runner image but this
repository's visibility - GitHub's standard Linux runner is four vCPUs on a
public repository and two on a private one, and this repository is private. So
two cores bought 1.37x where four bought 2.85x, and nothing is misconfigured.

That turns the `auto` argument above from a principle into a measurement: a
pinned `-n 4` would have put four workers on two cores every CI run from the
day it landed. It also means the CI figure improves on its own if this
repository is ever made public, with no edit here. Reproduced independently at
67 s serial (runs 33818974668 and 33820263730) against 49 s at `-n auto` (run
33820466910), which is the same 27-28% this item already records.

It also relocates the cost on CI. `bin/docket check` was already the largest
step there - 72 s against pytest's 69 s on the pre-change run - and pytest
dropping to 50 s makes that gap decisive rather than marginal. `PL-8BFV` is
where that is recorded.

**What it changes about where the time goes.** `bin/docket check` is now the
largest single item in `make check` at 30.5 s of 59.2 s, having been a quarter
of it. The suite is no longer the thing to look at; the queue's own check is.
`PL-KCQ7` and `PL-PGY4` are the two items that bear on it.
