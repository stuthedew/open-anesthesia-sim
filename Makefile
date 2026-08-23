.PHONY: sync check fix test run prebuild punch-list

sync:
	uv sync --locked --dev

check: sync
	uv run ruff format --check .
	uv run ruff check .
	uv run mypy src
	uv run pytest
	python3 tools/punch_list.py check

fix:
	uv run ruff format .
	uv run ruff check --fix .

test:
	uv run pytest

punch-list:
	python3 tools/punch_list.py check

run:
	uv run anesthesia-sim

prebuild:
	git status
	$(MAKE) check
