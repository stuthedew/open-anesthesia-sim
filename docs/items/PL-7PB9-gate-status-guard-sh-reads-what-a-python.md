---
id: PL-7PB9
title: gate-status-guard.sh reads what a Python interpreter runs only as a tools/ check script, so a gate run as a module - python3 -m pytest -q 2>&1 | tail, or uv run python -m mypy | tail - is read as no gate and loses its status unrefused
status: untriaged
added: 2026-09-26
---

**Problem.** gate-status-guard.sh reads what a Python interpreter runs only as a tools/ check script, so a gate run as a module - python3 -m pytest -q 2>&1 | tail, or uv run python -m mypy | tail - is read as no gate and loses its status unrefused

**Found 2026-09-26 working `PL-QMN0`**, as hook payloads on `6efd8c41`:
`python3 -m pytest -q 2>&1 | tail`, `python3 -m mypy | tail`, `python -m ruff
check . | tail` and `uv run python -m mypy | tail` all pass the gate guard,
while `uv run pytest | tail` and `python3 tools/doc_check.py check | tail` are
refused. `gate()` in `.claude/hooks/gate-status-guard.sh` hands an
interpreter's arguments to `check_script`, which looks for a `tools/*_check.py`
path or `dead_ends.py check` and nothing else, so a listed gate run as a module
reads as an interpreter running no check. `pytest`, `mypy` and `ruff` each run
as a module (`python -m pytest` is pytest's own documented spelling), and the
guard's list names them as programs only.

Not the same fact as `PL-QMN0`'s. That item is about which word `uv run` runs
past its own options; this one is which spellings of a listed gate the guard
recognises once it has the right word, so an interpreter's `-m` is a question
for `gate()`'s list, not for `shell_split.py`'s option grammars. `uv run -m
pytest`, where `-m` is uv's own `--module`, is `PL-QMN0`'s and is read there.
