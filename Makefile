.PHONY: sync check fix test run prebuild docket doc-check release

sync:
	uv sync --locked --dev

check: sync
	uv run ruff format --check .
	uv run ruff check .
	uv run mypy src
	uv run pytest
	bin/docket check
	python3 tools/doc_check.py check

fix:
	uv run ruff format .
	uv run ruff check --fix .

test:
	uv run pytest

punch-list:
	bin/docket check

doc-check:
	python3 tools/doc_check.py check

# The documented way to cut a release. `bin/docket release` writes the new
# version into pyproject.toml and stops, but uv.lock records the project's own
# version too, so the next command a release runs - `make check`, whose first
# step is `uv sync --locked` - fails with "the lockfile needs to be updated".
# That fired on both releases since the command existed; `5e9a8f6` and
# `3ed704a` each carry a hand-run one-line uv.lock bump.
#
# The sequencing lives here rather than in docket because a lockfile is a
# generated artifact and the tool that generates it is a toolchain fact, which
# is what this file is for. docket stays standard-library-only and
# package-manager-agnostic.
#
# This project names its versions rather than incrementing them (see
# ROADMAP.md, "Versioning decision"), so pass the version:
#
#     make release VERSION=0.3.0
release:
	bin/docket release $(VERSION)
	uv lock
	$(MAKE) check

run:
	uv run anesthesia-sim

prebuild:
	git status
	$(MAKE) check
