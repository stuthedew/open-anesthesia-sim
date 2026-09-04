---
id: PL-WCZV
title: pytest-xdist -n 4 measured 73.0 s to 24.9 s on the full suite with coverage identical at 100 percent; decide whether to take the dependency and where the flag lives
status: done
priority: P2
effort: S
classes: session-cost, infra
feature: dev-tooling
touches: pyproject.toml, Makefile, .github/workflows/quality.yml
verify: uv run pytest -n auto --cov=anesthesia_sim.core --cov-branch --cov-fail-under=100 && grep -qF 'uv run pytest -n auto' Makefile && grep -qF 'uv run pytest -n auto' .github/workflows/quality.yml
added: 2026-09-03
closed: 2026-09-04
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

## Taken (project owner, 2026-09-04)

`pytest-xdist>=3.8.0,<4.0` is in the dev group, and `-n auto` is on the `pytest`
line in `Makefile`'s `check` target and in `quality.yml`'s `checks` job. Each of
the four costs above, answered:

**The dependency.** Taken. The dev group is now five: `mypy`, `pytest`,
`pytest-cov`, `pytest-xdist`, `ruff`, plus `execnet` transitively. `drift.yml`
resolves it monthly along with everything else, which is the watch that makes a
fifth dev dependency affordable on a multi-year horizon.

**Ordering.** Four consecutive `-n auto` runs on this tree: 29.6 s, 28.9 s,
29.2 s, 29.4 s, **1224 passed** every time, against 1224 passed and 84.4 s
serial. Coverage byte-identical in both modes - `691 statements, 0 missed, 78
branches, 0 partial, 100%`, clearing `--cov-fail-under=100`. Still evidence
rather than proof, and the suites named above are still where a latent
inter-test dependency would surface first; a failure appearing only under `-n`
is a real bug in the tests and is fixed there rather than by dropping the flag.

**Where the flag lives.** As reasoned above - the `Makefile` line and the CI
step, never `addopts`.

**`auto` rather than the measured `-n 4`.** GitHub's standard Linux runner is
four vCPUs on a public repository and two on a private one, so a hardcoded `-n
4` oversubscribes the smaller machine and stops being right the moment either
the runner or the dev container changes. `auto` reads whatever it lands on. Test
outcomes do not depend on the worker count - that is the property the four runs
above check - and only wall clock does.

**CI gain, measured.** [pending - filled in from the first `checks` run on this
branch against the last run on `main`]

**Local saving, measured 2026-09-04** on the four-core container, warm caches:
**84.4 s to 29.6 s**, which is 54.8 s off a 122 s gate. That is the largest
single saving available in it, and larger than deleting the entire
`subprojects/docket` suite would have returned (29.8 s) - which is what
`PL-KCQ7` asked about and answered no to.
