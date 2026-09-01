---
id: PL-V87X
title: ruff format warns on every run that isort.split-on-trailing-comma conflicts with skip-magic-trailing-comma
status: untriaged
added: 2026-09-01
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
