---
id: PL-QSJM
title: make check's ruff passes on a stale __pycache__ where CI fails: a deleted first-party module's leftover .pyc keeps its import sorted as first-party
status: untriaged
added: 2026-09-15
---

**Problem.** make check's ruff passes on a stale __pycache__ where CI fails: a deleted first-party module's leftover .pyc keeps its import sorted as first-party

**Evidence, 2026-09-15 (PL-25KS, #588).** The port deleted
`src/anesthesia_sim/app/chart_series.py`. `spikes/qt/qt_spike.py` and
`spikes/qt/chart_sources.py` still imported a constant from it. CI's
`uv run ruff check .` reported both import blocks unsorted (I001): ruff resolves
first-party by looking for the module under `src`, found nothing, and sorted the
line as third-party. The local `make check` on the same tree passed, and the one
filesystem difference was `src/anesthesia_sim/app/__pycache__/chart_series.cpython-314.pyc`,
left from before the delete. Removing that file and re-running ruff on the
original imports reproduced CI's two errors exactly. So a session that deletes
a module and runs `make check` gets a green ruff on any import of it that
remains, until CI's clean checkout says otherwise.

**Shape of a fix.** Decidable and recurring, so it belongs in tooling rather
than in prose: a step in `make check` (or the Makefile's ruff target) that
removes `__pycache__` directories under `src/`, `tests/`, `tools/` and
`subprojects/` before ruff runs, or a `PYTHONDONTWRITEBYTECODE=1` in the
project's environment so the bytecode is never written. Measure first whether
ruff actually reads the `.pyc` (the experiment above says it does, on
ruff 0.16.4) so the fix names the mechanism it defeats.
