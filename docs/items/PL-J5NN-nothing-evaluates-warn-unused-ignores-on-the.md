---
id: PL-J5NN
title: Nothing evaluates warn_unused_ignores on the test trees, so a new inert type: ignore is invisible again the moment PL-CMCB's audit is taken
status: untriaged
feature: dev-tooling
touches: Makefile, pyproject.toml
added: 2026-09-01
---

**Problem.** `PL-CMCB` audited the ten `type: ignore` directives under `tests/`
and `subprojects/docket/tests/` by hand on 2026-09-01 and found every one live.
That verdict is a snapshot, and it starts decaying immediately: `[tool.mypy]
files` is `["src", "tools", "subprojects/docket/src"]`, so `warn_unused_ignores`
still never reads either test tree, and the eight directives left after that
audit are unevaluated again from the moment it was taken.

The set is not static either. `PL-CMCB` was written at 14:26 on 2026-08-31
listing nine directives; `PL-3CBS` (#128) added a tenth at
`subprojects/docket/tests/test_checks.py` five hours later the same evening.
Nothing objected, because nothing looks.

**Why it matters.** This is the standing half of the defect `PL-ZN0N` and
`PL-69J3` closed for `noqa` and `PL-CMCB` closed once for `type: ignore`. An
inert directive reads as a deliberate exemption and is not one, and the reader
who trusts it concludes the type checker has an opinion where it has never
looked. `RUF100` makes every other entry in `[tool.ruff.lint] select` mean what
it says by failing on an inert `noqa`; nothing plays that role for mypy here,
so the `type: ignore` half is re-audited by hand or not at all.

**Where.** `pyproject.toml`'s `[tool.mypy] files` and the comment above it;
`Makefile`'s `check` target.

**Approach.** Three routes, measured 2026-09-01 with a cleared cache.

1. **Widen `[tool.mypy] files` to include the test trees.** The comment above
   `files` is the standing decision against this and it still holds: `mypy
   tests` alone reports 40 errors in 8 files, and both trees together report 54
   in 11. Most are hand-built Flet doubles and deliberately wrong arguments -
   the invalid-input tests `CLAUDE.md`'s safety standard requires - so closing
   them means a suppression on each, which `docs/worker.md` forbids a delegated
   worker from writing. Not recommended.

2. **A scoped run whose output is filtered to `[unused-ignore]`,** wired into
   `make check`. The other 54 errors are irrelevant to it, because
   `warn_unused_ignores` is a per-line judgment: mypy reports an unused
   directive whether or not the file has other errors. Verified by planting
   `_INERT: int = 1  # type: ignore[arg-type]` in `test_model.py`, which the
   filter caught while the 54 passed through unread. This is the recommendation.

3. **Do nothing and re-audit by hand.** `PL-CMCB` cost about ten mypy runs plus
   the judgment; the cost recurs whenever anybody thinks to look, which over
   the two months this repository has existed is once.

**The trap route 2 has to avoid, and it is not theoretical.** The run must have
`MYPYPATH="subprojects/docket/src:tools"`. Without it, `mypy
subprojects/docket/tests` reports **all six live splat directives as unused** -
`docket` does not resolve, so `Item`, `Config` and `LandedReport` degrade to
`Any`, the splat produces no error, and every ignore over one looks inert. A
naive runner would have reported six false verdicts and someone would have
deleted six live suppressions. So the runner has to fail on
`[import-not-found]` and `[import-untyped]` as well, or its own headline result
is unsound. `tests/unit/test_doc_check.py` needs `tools` on the path for the
same reason.

Note also that the strip-and-re-run method used to confirm each directive by
hand is sensitive to mypy's incremental cache: editing one file twice in quick
succession produced a false "no error at this line", which read as an inert
directive until the cache was cleared and the error reappeared. Any tool built
here should clear the cache or run out of tree.

**Done when.** A new inert `type: ignore` anywhere under `tests/` or
`subprojects/docket/tests/` fails `make check`, the check cannot report a false
inert verdict when an import fails to resolve, and the comment above
`[tool.mypy] files` says which of the two mechanisms now covers the test trees
so the next reader does not re-derive the 40-vs-54 measurement.
