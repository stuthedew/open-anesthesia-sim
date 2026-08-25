---
id: PL-020
title: Bring tests and `tools/` under the type-check gate
priority: P3
effort: S
status: needs-decision
classes: infra
feature: dev-tooling
touches: pyproject.toml, tests/unit/test_bootstrap.py, tests/unit/test_simulation_view.py
added: 2026-08-24
---

**Problem.** `make check` runs `uv run mypy src`, so `tests/` and `tools/`
are unchecked. `uv run mypy .` reports 24 errors across 5 files on a clean
tree — mostly test fakes passed where a real Flet type is annotated
(`_FakePage` for `Page`) and a re-exported `ft` in `test_bootstrap.py`.
**Why it matters.** Low urgency, and the narrow gate may well be
deliberate: annotating test doubles to satisfy a UI framework's types can
cost more than it returns. But the gap is currently silent, and
`tools/punch_list.py` — which gates every punch-list change in CI — is
unchecked along with the tests.
**Where.** `Makefile` (`check`), `pyproject.toml` (`[tool.mypy]`),
`tests/unit/test_simulation_view.py`, `tests/unit/test_bootstrap.py`.
**Decision needed.** Widen the gate to `tools/` only, to `tests/` as well,
or neither. The 24 errors are almost entirely in the `tests/` half, so
`tools/` alone is close to free while `tests/` is the part that costs
something and returns the least.
**Done when.** The gate covers whatever scope is chosen and passes, or the
narrow gate is documented as deliberate with the reason.
