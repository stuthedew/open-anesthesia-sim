---
id: PL-WFJ9
title: render.py annotates three parameters `object` and pays for it with 12 `type: ignore[attr-defined]`
status: done
priority: P2
effort: S
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_release.py
added: 2026-08-31
closed: 2026-08-31
commit: 807ad55
pr: 104
verify: uv run mypy && ! grep -n "type: ignore" subprojects/docket/src/docket/render.py && uv run pytest subprojects/docket/tests/test_release.py -k both_renderers
---

**Problem.** render.py annotates three parameters `object` and pays for it with 12 `type: ignore[attr-defined]`

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `subprojects/docket/src/docket/render.py` annotates three
parameters `object` where a real type exists: `ready` in `format_digest`
(line 106) and in `format_status` (line 391), and `feature` in the nested
`next_in` (line 410). Every attribute read through them then needs a
suppression, so the file carries 12 `# type: ignore[attr-defined]` and two
`getattr` guards (lines 154 and 451) standing in for what an annotation would
give for free - `getattr(ready, "is_worth_cutting", False)` reads a property
that is declared on the dataclass.

**Why it matters.** Found while landing PL-020 (widen the type-check gate past
`src`), which brought `subprojects/docket/src` under mypy for the first time.
The gate now passes, but it passes *because* of these suppressions: they are
not inert, so nothing reports them, and `render.py` is effectively unchecked
in the places that matter while reading as though it were checked. That is a
worse state than being outside the gate, because the gate now asserts
something about this file that is not true of its digest and status paths -
the two outputs every session reads first.

**No import cycle stands in the way.** `Readiness` is a dataclass in
`release.py`, which imports only `.model`; `Feature` is a dataclass in
`plan.py`, from which `render.py` already imports `Gate` and `effort_total`.
Nothing imports `render` except `cli.py`. So the fix is one import plus three
signature changes, then deleting the 12 suppressions and both `getattr`
guards.

**Where.** `subprojects/docket/src/docket/render.py`.

**Done when.** `format_digest` and `format_status` take `Readiness | None`,
`next_in` takes `Feature`, every `# type: ignore[attr-defined]` in the file is
gone rather than moved, the two `getattr` guards are ordinary attribute reads,
and `uv run mypy` passes.
