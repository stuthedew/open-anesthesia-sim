---
id: PL-ZN0N
title: Enable ruff RUF100 so inert noqa directives fail the build
priority: P3
effort: S
status: done
classes: infra
feature: dev-tooling
touches: pyproject.toml
added: 2026-08-25
pr: 105
closed: 2026-08-31
---

**Problem.** `pyproject.toml` sets ruff's `select = ["E", "F", "I", "UP", "B"]`.
`RUF100` is not among them, so a `noqa` naming a rule the project does not
enable, or suppressing a rule that no longer fires, is invisible.

**Why it matters.** PL-69J3 found ten such directives in one pass, and they
were only found because someone ran the rule by hand. An inert suppression
reads as a deliberate exemption and is not one.

**Where.** `pyproject.toml` (`[tool.ruff.lint]`).

**Notes.** From PL-B043. `CLAUDE.md` says not to build around what an existing
linter already does — this is one line, and strictly better than any detector
we would write. There are 13 `noqa` directives in the tree; expect the change
to surface any that have gone inert since PL-69J3.

**Done when.** `RUF100` is enabled and `make check` is green.
