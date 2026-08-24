.PHONY: sync check fix test run prebuild docket doc-check

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

run:
	uv run anesthesia-sim

prebuild:
	git status
	$(MAKE) check
