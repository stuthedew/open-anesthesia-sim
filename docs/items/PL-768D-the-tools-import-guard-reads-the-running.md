---
id: PL-768D
title: The tools/ import guard reads the running interpreter's stdlib, not the floor's
status: untriaged
added: 2026-09-01
---

**Problem.** `tests/unit/test_tools_portability.py`'s import guard, added by
`PL-QDH7`, allows any name in `sys.stdlib_module_names`. That frozenset is the
standard library of the interpreter *running the test* - the project
virtualenv, on the 3.14 `pyproject.toml` pins - not of the 3.11 floor
`subprojects/docket/pyproject.toml` declares, which is the interpreter the
tools actually have to run under. A module added to the standard library
between the two is therefore allowed by the guard and absent where it matters.
Demonstrable in one command in this container, where bare `python3` really is
3.11.15 and the virtualenv 3.14.7: `annotationlib` and `compression` are in
3.14's set and not in 3.11's.

**Why it matters.** It is a hole in a guard whose entire purpose is closing
one, and it fails *open* - the guard passes and `make check`'s final
`python3 tools/doc_check.py check` raises `ModuleNotFoundError`, which is the
exact failure `PL-QDH7` was written to prevent. The reverse direction is safe:
a module removed after the floor (PEP 594's dead batteries) is missing from the
running interpreter's set and rejected here while still importable at the
floor, which is a false positive and loud. CI does not cover the gap either -
`.github/workflows/quality.yml` runs `uv run python tools/doc_check.py check`,
under the virtualenv, so the test suite is the only guard the promise has.

Narrow in practice, which is why it was documented rather than closed:
CPython added two top-level modules across 3.12-3.14, and neither is one a
documentation checker would reach for. Recorded so the judgment is on the
record rather than implied by its absence.

**Where.** `tests/unit/test_tools_portability.py`, the `VENDORED` frozenset and
`test_no_tool_imports_outside_the_standard_library` beside it. The test's
docstring already names the bound and the two live examples, so closing this
means deleting that paragraph as well as widening the check.

**Done when.** The guard rejects an import of a module that exists in the
running interpreter's standard library but not at the declared floor, and the
docstring no longer records the gap as open.

**Options, none yet chosen.** The standard library carries no versioned module
index, so nothing derives the floor's set the way `sys.stdlib_module_names`
derives the running one. Three routes: subtract a small hand-written set of
names added after the floor, which closes it exactly but goes stale as a false
positive when the floor rises (loud, so arguably the right kind of stale); ask
the bare `python3` on PATH for its own `sys.stdlib_module_names` by
subprocess, which answers for the interpreter `make check` really uses but
makes the test's verdict depend on the machine and buys nothing in CI, where
that interpreter is the virtualenv's; or accept the bound and drop this item
with a reason. Triage should pick before any code is written.
