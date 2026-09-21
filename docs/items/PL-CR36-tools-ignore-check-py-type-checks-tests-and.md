---
id: PL-CR36
title: tools/ignore_check.py type-checks tests and subprojects/docket/tests in one mypy invocation, so a second file named conftest in those trees is a duplicate-module error that stops mypy before it evaluates anything and turns make check red
status: untriaged
added: 2026-09-21
---

**Problem.** tools/ignore_check.py type-checks tests and subprojects/docket/tests in one mypy invocation, so a second file named conftest in those trees is a duplicate-module error that stops mypy before it evaluates anything and turns make check red

**How it surfaced.** `PL-YRYR` added `subprojects/docket/tests/conftest.py`.
`make check` went red on `Duplicate module named "conftest" (also at
"tests/conftest.py")`, and `ignore_check` reported honestly - `type: ignore
directives: not checked - mypy exited 2 without reporting findings, so nothing
was evaluated` - which is the apparatus floor working, not failing. The tool
declined rather than passing a partial read off as a complete one. What is
wrong is that a legal second `conftest.py` cannot exist in either tree at all.

**The fix, measured 2026-09-21.** `--explicit-package-bases` on `run_mypy`'s
invocation resolves it: with it, mypy derives distinct module names from the
paths and checks 91 source files, reporting the 418 pre-existing type errors
those trees carry - which is exactly what `report()` already filters and the
module docstring already expects ("The several dozen type errors those trees
report, which are why the gate excludes them, pass unread"). Without it, mypy
exits 2 having evaluated nothing.

**Why it was not fixed inside `PL-YRYR`.** It touches `tools/ignore_check.py`,
outside that item's `touches`, and a tool whose whole job is to decide whether
an answer is sound owes a test for the case that broke it - so both of the
fix-now rule's first two tests fail and it is an item. `PL-YRYR` routed around
it instead by putting its `conftest.py` at the repository root, which is
outside both trees mypy is given; that is a sound place for it on its own
merits and is not a workaround that would need undoing, but it leaves this
latent for whoever adds the next `conftest.py`.

**Done when** a second `conftest.py` may exist in `tests/` or
`subprojects/docket/tests/` without `ignore_check` declining, with a test that
fails on the current invocation.
