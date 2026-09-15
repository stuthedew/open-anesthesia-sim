---
id: PL-VZYS
title: A hand-run 'uv run ruff check .' still reads the stale .ruff_cache that PL-QSJM's --no-cache removes from make check and make fix, so the guard sits at the entry point rather than where the tool reads it - the same shape as PL-0MLZ's finding about PYTHONDONTWRITEBYTECODE
priority: P3
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: pyproject.toml, docs/worker.md
added: 2026-09-15
verify: grep -qE 'RUFF_NO_CACHE' pyproject.toml
---

**Problem.** A hand-run 'uv run ruff check .' still reads the stale .ruff_cache that PL-QSJM's --no-cache removes from make check and make fix, so the guard sits at the entry point rather than where the tool reads it - the same shape as PL-0MLZ's finding about PYTHONDONTWRITEBYTECODE

**Why it matters.** `PL-QSJM` put `--no-cache` on the Makefile's two `ruff
check` lines, so the *gate* now asks CI's question. A session iterating by hand
does not: `uv run ruff check .` is what the `docket` skill's own advice produces
(`pytest -q` while iterating, the same habit for ruff), and it still reads
`.ruff_cache`. So after deleting a module, a hand-run ruff reports clean on
imports that no longer resolve.

The residual risk is small, and worth stating rather than overstating: `make
check` is required before a commit and now carries the flag, so this cannot by
itself reach `main`. What it costs is a session's belief about the tree between
edits - the same "guard set by the entry point, bypassed by the most common
invocation" that `PL-0MLZ` records for `PYTHONDONTWRITEBYTECODE` and `PL-TCKV`
for `UV_NATIVE_TLS`. Three instances of one shape is the argument for fixing the
shape: a carrier `uv run` reads, rather than one `make` applies.

**Done when.** A bare `uv run ruff check .` in this checkout does not read a
stale `.ruff_cache` - `[tool.uv]`'s `env` or `env-file` in `pyproject.toml` is
the cheapest candidate, and takes `RUFF_NO_CACHE=true`, which rejects `1` - and
the Makefile flags are either kept as belt-and-braces with a comment saying so,
or removed as redundant. Worth landing with `PL-0MLZ` and `PL-TCKV`, which want
the same carrier.
