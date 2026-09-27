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
verify: grep -q 'UV_SYSTEM_CERTS' pyproject.toml
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

**On the `verify:` above, and why it is not the obvious one.** The obvious
command - run `uv` and grep its stderr for the warning - is *environmentally*
rather than *causally* discriminating, and it failed CI on 2026-09-15 by
passing there while the work was untouched: this container exports
`UV_NATIVE_TLS` and a GitHub runner does not, so the warning the command looks
for is simply absent on the runner. `docket check --verify` caught it as an
open item whose command already passes, which is exactly the accusation
`PL-3DXV` describes. What replaces it names something only the work creates -
the translation appearing in `pyproject.toml`, whose `[tool.uv]` table already
exists at line 119 and which `PL-0MLZ` independently reads as the cheapest
carrier. Re-point it if the work chooses `uv.toml` or `.env` instead.

**Note 2026-09-27, from `PL-VZYS`'s design round: the carrier the paragraph
above names does not exist.** uv 0.12.19's `[tool.uv]` table has no `env` or
`env-file` field - the `Options` struct in uv's `uv-settings` crate at tag
0.12.19 carries neither, and `uv sync` on a `pyproject.toml` declaring one
warns "unknown field" and applies nothing. `uv.toml` reads the same struct, so
it is not a route either. `.env` is read only when `uv run --env-file` or
`UV_ENV_FILE` asks for it, which is the entry-point shape this item was filed
to escape. So `grep -q 'UV_SYSTEM_CERTS' pyproject.toml` can pass only on a
line that does nothing, and no route inside the repository quiets a bare `uv
run`: the variable is exported by the container before any file here is read.
Recommendation: the translation belongs where the export is - the environment's
own variable renamed from `UV_NATIVE_TLS` to `UV_SYSTEM_CERTS`, which is a
setting of the Claude Code environment that only the project owner can change,
outside any checkout - with the Makefile block kept until a fresh container is measured
quiet, and the `verify:` re-pointed at that measurement rather than at a
`pyproject.toml` line. `PL-VZYS` § "Design round 2026-09-27" carries the source
reads.
