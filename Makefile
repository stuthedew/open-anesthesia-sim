.PHONY: sync check fix test run prebuild

sync:
	uv sync --locked --dev

check: sync
	uv run ruff format --check .
	uv run ruff check .
	uv run mypy src
	uv run pytest

fix:
	uv run ruff format .
	uv run ruff check --fix .

test:
	uv run pytest

run:
	uv run anesthesia-sim

prebuild:
	git status
	$(MAKE) check
