---
id: PL-TCKV
title: Every uv run prints a UV_NATIVE_TLS deprecation warning, so every verify command and every test run carries a line nobody acts on
priority: P3
effort: S
status: ready
classes: session-cost, infra
feature: dev-tooling
touches: docs/worker.md, subprojects/docket/src/docket/verify.py
added: 2026-09-14
verify: test -z "$(uv run python -c 'pass' 2>&1 | grep UV_NATIVE_TLS)"
---

**Problem.** Every uv run prints a UV_NATIVE_TLS deprecation warning, so every verify command and every test run carries a line nobody acts on

**Where the existing guard stops, measured 2026-09-15.** `Makefile:21`'s
neighbourhood already translates this: `PL-KY7M` added an `ifdef UV_NATIVE_TLS`
block that re-exports the value as `UV_SYSTEM_CERTS` and unsets the old name, so
every `uv` invocation *through make* is quiet. Everything else is not - a bare
`uv run python tools/import_boundary_check.py` in this session printed the
warning, and so does every `uv run pytest` a session types while iterating and
every `verify:` command the store replays.

**Why it matters.** It is the same shape as `PL-0MLZ` and `PL-VZYS`, and the
three are worth fixing together: the setting is applied by the *entry point*
rather than where the tool reads it, so the most common invocation bypasses it.
The cost here is attention rather than correctness - one unactionable line per
`uv` call, paid by every replayed `verify:` command in a whole-store run, which
is `CLAUDE.md`'s "an advisory nobody acts on" being manufactured at scale. It
trains a session to skim exactly the output where a real advisory also appears.

**Done when.** A bare `uv run` in a fresh web container prints no
`UV_NATIVE_TLS` line - the translation moved to where `uv` reads it rather than
where `make` does - and the Makefile block is either removed as redundant or
kept with a comment saying why it still earns its place.
