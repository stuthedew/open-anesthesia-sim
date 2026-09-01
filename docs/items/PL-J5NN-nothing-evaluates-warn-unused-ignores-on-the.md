---
id: PL-J5NN
title: Nothing evaluates warn_unused_ignores on the test trees, so a new inert type: ignore is invisible again the moment PL-CMCB's audit is taken
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.2.8
touches: Makefile, pyproject.toml, tools/ignore_check.py, tests/unit/test_ignore_check.py
added: 2026-09-01
closed: 2026-09-01
pr: 174
verify: uv run pytest tests/unit/test_ignore_check.py && uv run python tools/ignore_check.py
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

**Closed 2026-09-01. Route 2, approved by the project owner.** `make check` now
runs `tools/ignore_check.py` directly below the gate. It reports
`type: ignore directives: 8 evaluated, 0 inert` on a clean tree, and fails
naming the file and line when one goes inert.

**Route 1 is not merely blunt, it is unsound, and this was measured rather than
argued.** The surgical form - add `tests` to `[tool.mypy] files` and silence the
noisy codes per module - cannot work at all:

```
mypy --disable-error-code=arg-type subprojects/docket/tests
→ 6 × Unused "type: ignore" comment  [unused-ignore]
```

Disabling the code a directive names makes that directive suppress nothing, so
all six live splat directives report as unused. It is the same false-verdict
failure as the missing `MYPYPATH`, arriving by a second route, and it would have
been discovered only after someone deleted six live suppressions. Recorded here
because the argument against route 1 in this item was about *cost*, and the real
objection is *correctness*.

**The cold-run compromise.** Running every check with `--no-incremental` costs
12.2s against 0.5s warm, on every `make check`, to defend against a staleness
case nobody has characterised - three rapid edit-and-check cycles failed to
reproduce it. Running always-warm risks the one error that matters, a false
inert verdict, which invites deleting a live suppression. So the cache is used
and an *accusation* is confirmed without it: a finding re-runs cold before it
is reported. Clean stays 0.5s; only a finding pays the 12s, and only while there
is a finding to pay for.

**What the tool refuses to call clean.** An unresolved import, a mypy crash, and
mypy missing entirely all report "not checked" rather than "0 inert", and an
unresolved import outranks an inert finding - with imports broken, that finding
is precisely what cannot be trusted. A check that cannot tell "nothing is inert"
from "nothing was read" is the failure this tool exists to avoid.

Directives are found by tokenizing rather than grepping, so the marker in
`verify.py`'s `SUPPRESSIONS` tuple, the one named in `test_release.py`'s prose,
and the one `test_verify.py` writes into a fixture file as a string literal are
not counted as directives. A test pins that against the live tree and fails if
the string-literal occurrence ever disappears, since it would then prove
nothing.
