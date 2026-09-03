---
id: PL-WCZV
title: pytest-xdist -n 4 measured 73.0 s to 24.9 s on the full suite with coverage identical at 100 percent; decide whether to take the dependency and where the flag lives
status: untriaged
feature: dev-tooling
added: 2026-09-03
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
