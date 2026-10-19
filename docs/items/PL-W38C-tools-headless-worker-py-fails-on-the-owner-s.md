---
id: PL-W38C
title: tools/headless_worker.py fails on the owner's Mac: it starts bin/docket, a bash script, with the Python interpreter, and the how-to runs it with python3, which is Xcode's 3.9 there, below the tools' 3.11 floor
priority: P2
effort: S
status: done
feature: api-credit-runs
touches: tools/headless_worker.py, tests/unit/test_headless_worker.py, docs/maintainer.md
added: 2026-10-19
closed: 2026-10-19
verify: uv run pytest -q tests/unit/test_headless_worker.py
---

**Problem.** tools/headless_worker.py fails on the owner's Mac: it starts bin/docket, a bash script, with the Python interpreter, and the how-to runs it with python3, which is Xcode's 3.9 there, below the tools' 3.11 floor

**Found 2026-10-19, on the owner's first dry run.** It failed with
`ImportError: cannot import name 'UTC' from 'datetime'` under
`/Applications/Xcode.app/.../Python3.framework/Versions/3.9`. Two defects sat
behind it. The how-to said to run the tool with `python3`, which on macOS is
Xcode's 3.9. And the runner started `bin/docket`, a bash script, with
`sys.executable`, which fails under any Python; the tests had replaced that
call with a stub, so they never ran it.

**Fixed.** The runner now calls `docket.cli.main` in its own process, so the
queue is read with the runner's Python. A new `check_tools` refuses before any
spend when `claude`, `uv` or a `python3` of at least 3.11 is missing from the
run's `PATH`. `docs/maintainer.md` now starts the runner with
`uv run python`. `tests/unit/test_headless_worker.py` runs the real queue
read, which fails on the old code with the `SyntaxError` from `bin/docket`'s
`set -euo pipefail` line, and tests both refusals of `check_tools`.

**Generator check.** Not a head: one tool's two defects, found on its first
real use.

