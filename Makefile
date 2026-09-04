.PHONY: sync check fix test run prebuild docket doc-check release

sync:
	uv sync --locked --dev

check: sync
	uv run ruff format --check .
	uv run ruff check .
# No paths: `[tool.mypy] files` in pyproject.toml names what the gate covers,
# and says why `tests/` is not in it.
	uv run mypy
# Under `uv run`, unlike `doc_check.py` below: this one shells out to mypy, so
# it needs the virtualenv the gate above runs in. It reads `warn_unused_ignores`
# over the two test trees `files` excludes, which nothing else evaluates.
	uv run python tools/ignore_check.py
# `--cov=` takes the dotted module, never a path, and the run is the whole
# suite: coverage of `core/` is the union of everything that exercises it, so
# the threshold is only reachable from a whole-suite run. Deliberately not in
# `[tool.pytest.ini_options] addopts` nor in a `[tool.coverage]` table - either
# would apply the threshold to the scoped `uv run pytest tests/unit/test_x.py`
# a session runs while iterating, which would fail for a reason unrelated to
# the change under it. Measured 2026-09-03: 92.8 s with the flag against
# 92.4 s without, so the gate is free. `PL-22Z3`.
#
# `-n auto` is off `addopts` for exactly the same reason, and it is the reason
# that argument generalizes: a session iterating on one test file would pay
# worker startup for a handful of tests and lose. Here it is the largest item
# in this target and the suite otherwise runs on one core of however many the
# box has - measured 2026-09-03, 1230 tests: 78 s serially against 27 s at
# `-n auto`, with coverage identical at 691 statements / 78 branches / 100%.
# Coverage holding is what makes the flag admissible rather than the wall
# clock, which is why the threshold stays on this line and is not relaxed to
# pay for the parallelism. `PL-WCZV`.
	uv run pytest -n auto --cov=anesthesia_sim.core --cov-branch --cov-fail-under=100
	bin/docket check
	python3 tools/doc_check.py check
# Bare `python3` for the reason `doc_check.py` above uses it: standard library
# only, so it runs in a checkout with no virtualenv. It reads the color
# constants out of `app/` with `ast` rather than importing them, because
# `app/simulation_view.py` imports Flet.
	python3 tools/contrast_check.py
# Under `uv run`, unlike the two lines above, and for a reason that is about
# the *input* rather than the tool: this one reads every module under
# `src/anesthesia_sim/` with `ast`, and that source targets 3.14. PEP 695
# (3.12) type parameters in `app/chart_downsampling.py` are a `SyntaxError` to
# the 3.11 parser these tools promise to run under, and `ast.parse`'s
# `feature_version` only ever narrows the accepted syntax - it cannot teach an
# older parser a newer language. So the parser has to be the one the source is
# written for. `tools/ignore_check.py` above is the same category for a
# different reason; the tool itself stays standard-library-only and parses at
# the floor, which is what `tests/unit/test_tools_portability.py` holds it to.
# `PL-Y0RZ`.
	uv run python tools/import_boundary_check.py

fix:
	uv run ruff format .
	uv run ruff check --fix .
# The mutating half of `bin/docket check`'s missing-`pr` advisory. `check`
# reports which landed closures owe a pull request number and which number the
# base names for each; this writes them, so the field rides the commit the
# session is about to make instead of costing one of its own (`PL-N5WZ`).
# Here rather than in `check` for the reason `ruff format` is: `check` runs in
# CI, where mutating the tree is not the job.
	bin/docket record

# `-n auto` for the reason the `check` line above gives, which transfers
# unchanged: what keeps the flag off `addopts` is the scoped
# `uv run pytest tests/unit/test_x.py` a session runs while iterating, and this
# target is always the whole suite. Measured 2026-09-04, four cores, 1230
# tests: 88.5 s serially against 31.8 s, both passing. `PL-FX3N`.
#
# It costs neither `-x` nor the debugger, which is what made this not
# automatic. The recipe takes no arguments, so a run wanting either is already
# a direct `uv run pytest -x tests/unit/test_x.py` that never came through here
# - and `-n auto` is safe to copy into one anyway: given `--pdb` it sets
# `numprocesses = 0` and distribution off rather than erroring
# (`xdist/plugin.py`, `pytest_cmdline_main`), where a pinned `-n 4` raises
# `--pdb is incompatible with distributing tests`. `-x` stops the run under
# both; under `-n` the in-flight workers finish first, so more tests run before
# it stops.
#
# This is not the coverage gate. `.github/workflows/quality.yml`'s pytest step
# has to stay identical to the `check` line above, and deliberately not to this
# one, which shares the flag and nothing else (`PL-D3M2`).
test:
	uv run pytest -n auto

# Named for the store it validates. `make check` runs `bin/docket check` too;
# this target exists so a session can validate the store on its own, after
# editing an item and before committing it.
docket:
	bin/docket check

doc-check:
	python3 tools/doc_check.py check

# The documented way to cut a release: everything about one that a command can
# do, and nothing that it cannot. `bin/docket release` writes the new version
# into pyproject.toml and stops, but uv.lock records the project's own version
# too, so a `uv sync --locked` afterwards fails with "the lockfile needs to be
# updated". That fired on both releases before the relock was sequenced here;
# `5e9a8f6` and `3ed704a` each carry a hand-run one-line uv.lock bump.
#
# The sequencing lives here rather than in docket because a lockfile is a
# generated artifact and the tool that generates it is a toolchain fact, which
# is what this file is for. docket stays standard-library-only and
# package-manager-agnostic.
#
# It deliberately stops short of `make check`. ROADMAP.md's version-table row
# and baseline section are release prose - what the release was *for* - and
# nothing writes them, so running the check here fails on edits nobody has
# been asked for yet, with the tree half updated. `bin/docket release` names
# those edits instead; make them, then run `make check`, which is what proves
# they landed.
#
# This project names its versions rather than incrementing them (see
# ROADMAP.md, "Versioning decision"), so pass the version:
#
#     make release VERSION=0.3.0
release:
	bin/docket release $(VERSION)
	uv lock
	@echo
	@echo "uv.lock relocked. Make the ROADMAP.md edits named above, then run: make check"

run:
	uv run anesthesia-sim

prebuild:
	git status
	$(MAKE) check
