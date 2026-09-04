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
# `-n auto` is on this line for that same reason and not in `addopts`: worker
# startup is a fixed cost the whole suite absorbs and a single scoped test file
# does not, so a session iterating on one file would pay it and lose.
#
# It buys the largest saving measured anywhere in this gate, and it removes no
# check - every test still runs and coverage is identical. Measured 2026-09-04
# on this four-core container, same checkout, warm caches:
#
#     serial    84.4 s   1224 passed   691 stmts 0 missed, 78 branches 0 partial, 100%
#     -n auto   29.6 s   1224 passed   691 stmts 0 missed, 78 branches 0 partial, 100%
#
# The saving is larger than the CPU accounting alone predicts because about a
# third of the serial wall clock was already spent waiting rather than
# computing: `subprojects/docket/tests` shells out to `git` once or twice per
# test, 532 tests at roughly 30 ms each. Parallelism recovers that wait, which
# is why it beats every proposal to delete tests instead - deleting the whole
# docket suite would have returned 29.8 s of a 122 s gate against this line's
# 54.8 s, and at the cost of the checks (`PL-KCQ7`).
#
# `auto` rather than a fixed `-n 4`: GitHub's standard Linux runner is four
# vCPUs on a public repository and two on a private one, so a hardcoded number
# oversubscribes the smaller machine and pins the larger one to a number that
# stops being right when either the runner or this container changes. Test
# outcomes do not depend on the worker count - the property checked below - and
# only wall clock does. `PL-WCZV`.
	uv run pytest -n auto --cov=anesthesia_sim.core --cov-branch --cov-fail-under=100
	bin/docket check
	python3 tools/doc_check.py check
# Bare `python3` for the reason `doc_check.py` above uses it: standard library
# only, so it runs in a checkout with no virtualenv. It reads the color
# constants out of `app/` with `ast` rather than importing them, because
# `app/simulation_view.py` imports Flet.
	python3 tools/contrast_check.py

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

# `-n auto` for the reason the `check` target above gives at length: this is
# the whole suite too, so worker startup is amortized. A session debugging one
# file runs `uv run pytest <file>` directly and pays neither. `PL-WCZV`.
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
