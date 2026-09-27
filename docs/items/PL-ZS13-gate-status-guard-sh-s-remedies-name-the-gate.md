---
id: PL-ZS13
title: gate-status-guard.sh's remedies name the gate it matched rather than the command it refused, so for python3 tools/possessive_section_check.py --help 2>&1 | tail the line it calls the one you want was set -o pipefail; tools/possessive_section_check.py 2>&1 | tail -45, which exits 126 since no tools/*_check.py is executable - met 2026-09-27 triaging PL-N6JP
status: untriaged
added: 2026-09-27
---

**Problem.** gate-status-guard.sh's remedies name the gate it matched rather than the command it refused, so for python3 tools/possessive_section_check.py --help 2>&1 | tail the line it calls the one you want was set -o pipefail; tools/possessive_section_check.py 2>&1 | tail -45, which exits 126 since no tools/*_check.py is executable - met 2026-09-27 triaging PL-N6JP

**Met 2026-09-27, triaging `PL-N6JP`.** The guard refused `python3
tools/possessive_section_check.py --help 2>&1 | tail -4` and offered, as the
spelling "you want", `set -o pipefail; tools/possessive_section_check.py 2>&1
| tail -45`. Run as printed it exits 126, `Permission denied`: all 18
`tools/*_check.py` are mode `100644` in git and none has a shebang. The line
also drops the `--help` the refused command carried.

**Why.** `gate()` returns the gate "spelled for the message", and every remedy
line is built from that name; for a check run through an interpreter it is
`check_script`'s token alone, the script's path. Read from `gate()` rather
than met: `pytest`, `mypy` and `ruff` come back as the bare name, so `uv run
pytest -q tests/unit/t.py | tail` is offered `set -o pipefail; pytest 2>&1 |
tail -45`, without `uv run` and without the file it named; a `make` or
`bin/docket` gate comes back runnable, less its other arguments.

**Why it matters.** The header's case for the guard is that its remedy is one
token, so sessions do not learn to route around it. A remedy that fails when
copied costs the retry the refusal was meant to be the whole price of, and the
line it calls the one you want is the one a session copies.
