---
id: PL-020
title: Widen the type-check gate past `src`, and ship a `py.typed` marker
priority: P2
effort: S
status: ready
classes: infra
feature: dev-tooling
touches: pyproject.toml, Makefile, README.md, .github/workflows/quality.yml, src/anesthesia_sim/py.typed, subprojects/docket/src/docket/roadmap.py, tests/unit/test_bootstrap.py
added: 2026-08-24
verify: uv run mypy && uv run pytest tests/unit/test_bootstrap.py -k py_typed
---

**Problem.** `make check` and CI both run `uv run mypy src`, so `tests/`,
`tools/`, and `subprojects/docket/src/` are unchecked. The gap is silent:
nothing reports that the type discipline the source is held to stops at the
package boundary.

**Why it matters.** Low urgency - none of it reaches a displayed clinical
value - but `tools/doc_check.py` gates every documentation change in CI and
`subprojects/docket/src/` gates every queue change, and neither is
type-checked by the run that gates them. The question this item existed to
answer was whether widening the gate costs more than it returns.

**Measured 2026-08-25, and re-measured 2026-08-30; the numbers below are the
later run.** It costs much less than the raw number suggests, and the raw
number is misleading in a way worth recording.

`uv run mypy tests tools subprojects/docket/src` reports **79 errors across 24
files**. The great majority are `[import-untyped]` - "Skipping analyzing
`anesthesia_sim.core.…`" - because `src/anesthesia_sim/` has no `py.typed`
marker, so mypy declines to read the project's own annotations from outside
the package. That is not type debt in the tests; it is one missing file, and
it is a packaging defect in its own right: without the marker, no consumer of
this package sees its types either.

Adding an empty `src/anesthesia_sim/py.typed` drops the run to **40 errors in
8 files**, with `uv run mypy src` still clean. Those 40 split:

| Scope | Errors | Character |
| --- | --- | --- |
| `tools/` | 0 | free to gate; `doc_check.py` - the one CI depends on - is clean, provided `subprojects/docket/src` is in the same run, since it imports `docket.roadmap` |
| `subprojects/docket/src` | 1, an `[assignment]` in `docket/roadmap.py` | the only source fix the gate requires |
| `tests/` | 39, of which 26 are `[arg-type]` in `tests/unit/test_simulation_view.py` | the Flet doubles (`_FakePage` where `Page` is annotated), exactly the cost this item predicted |

So the original guess was right about the shape and wrong about the size: the
expensive half is one test file's UI doubles, and everything else is close to
free.

**Re-measured 2026-08-30**, because PL-STNV retired the review harness that
carried this item's whole `tools/` cost. The five `tools/` errors were all in
`tools/review-verification/verify_findings.py` and went with it, so `tools/` is
now clean and the decision below is cheaper than when it was taken. The counts
elsewhere moved with the tree, not with that deletion: `subprojects/docket/src`
has acquired one error since, and `tests/` has grown from 30 to 39.

**Decision (2026-08-25): widen to everything except `tests/`.** Add the
`py.typed` marker, then gate `src`, `tools`, and `subprojects/docket/src` in
`Makefile` and `.github/workflows/quality.yml`. Leave `tests/` out and record
the reason in the same place: annotating a test double to satisfy a UI
framework's types costs real work and returns the least, since a wrongly typed
fake fails the test it is used in. Revisit only if the count outside
`test_simulation_view.py` grows.

**Retitled 2026-08-31**, from "Bring tests and `tools/` under the type-check
gate". The decision above excludes `tests/`, so the original title described
work this item deliberately does not do - and it is the line that would have
appeared in v0.2.8's release notes claiming the tests are gated.

**Where.** `pyproject.toml` (`[tool.mypy] files`), `Makefile` (`check`),
`.github/workflows/quality.yml`, and a new empty `src/anesthesia_sim/py.typed`.
Fixing the one `[assignment]` error in `subprojects/docket/src/docket/roadmap.py`
is the only source change required.

**Done when.** `src/anesthesia_sim/py.typed` exists and is included in the
built package; the gate in both `Makefile` and CI covers `src`, `tools`, and
`subprojects/docket/src` and passes; and the exclusion of `tests/` is
documented next to the gate with the measured reason above.
