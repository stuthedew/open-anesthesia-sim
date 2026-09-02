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
	uv run pytest
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

test:
	uv run pytest

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
