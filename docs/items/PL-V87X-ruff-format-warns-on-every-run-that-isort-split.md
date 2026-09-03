---
id: PL-V87X
title: ruff format warns on every run that isort.split-on-trailing-comma conflicts with skip-magic-trailing-comma
priority: P3
effort: S
status: done
classes: infra
feature: dev-tooling
milestone: v0.3.1
touches: pyproject.toml
added: 2026-09-01
closed: 2026-09-02
pr: 236
verify: grep -qF 'split-on-trailing-comma = false' pyproject.toml && uv run ruff format --check .
---

**Problem.** Every `ruff format` run - so every `make fix`, and `make check`'s
`ruff format --check .` - prints:

```text
warning: The isort option `isort.split-on-trailing-comma` is incompatible with
the formatter `format.skip-magic-trailing-comma=true` option. To avoid
unexpected behavior, we recommend either setting
`isort.split-on-trailing-comma=false` or `format.skip-magic-trailing-comma=false`.
```

`pyproject.toml` sets `[tool.ruff.format] skip-magic-trailing-comma = true` and
configures no isort section, so the warning is raised against ruff's default
`isort.split-on-trailing-comma = true`. Observed 2026-09-01 while working
PL-921W; it predates that work and is unrelated to it.

**Why it matters.** Two costs, both small and both permanent. The behavior ruff
is warning about is real: `I` is in the lint selection, so the import sorter
splits an import on a magic trailing comma that the formatter would then join,
which is a fixpoint the two tools disagree about. And a warning printed on
every run of the quality gate is a warning nobody reads - it trains a session
to skim past `make check`'s output, which is where a real advisory would also
appear.

**Where.** `pyproject.toml`, `[tool.ruff.format]` and a new
`[tool.ruff.lint.isort]`.

**Approach.** Ruff names both resolutions. Setting
`isort.split-on-trailing-comma = false` keeps the repository's current
formatting - `skip-magic-trailing-comma = true` is a deliberate choice about
how the code looks - and is one line. Check whether it changes any formatting
first: `uv run ruff format --diff .` after the edit should print nothing.

**Done when.** `make check` and `make fix` run clean, and the choice is
recorded beside the setting.

**Triaged 2026-09-01.** Fields only - the **Approach.** above already names the
resolution and how to check it, and nothing in it needs deciding first.

`P3`, `infra`, beside the other quality-gate items in `dev-tooling`. It is
process work by every class it carries, so the triage rule keeps it out of the
top band whatever the annoyance.

The `verify:` command exits 1 on 2026-09-01 and pairs the two halves the item
owes: `grep` proves the setting landed, and `ruff format --check .` proves it
changed no formatting. `grep` alone would pass on a tree where the setting was
added and the code left unformatted; the format check alone passes today.

**Closed 2026-09-02.** `pyproject.toml` gained a `[tool.ruff.lint.isort]`
section setting `split-on-trailing-comma = false`, resolving the conflict
toward the formatter: `skip-magic-trailing-comma = true` is a deliberate
formatting decision, so the sorter is told the same thing rather than the
formatter being reversed to silence the warning.

**Re-banded on the way out.** This was filed `P3` as a config nit and worked
ahead of most of `P2`, because the cost is not the warning. An evidence-led
review of agentic software engineering names check accumulation as the failure
mode for this kind of apparatus - gates grow "slower and noisier until people
and agents route around it" - and a warning printed on every `make check` is
the leading indicator of it. Measured before the fix: `make check` printed 104
lines, 7 of them warnings. Six were `UV_NATIVE_TLS`, set by the remote
container rather than by this repository; the seventh was this one, which fired
everywhere. Its cost was paid by every other advisory in the suite, not by
itself. `PL-ZBJ0` carries the general rule this instance produced.

