---
id: PL-7YZH
title: Test the two failure paths in `simulation_view.py` that a command cannot prove
priority: P1
effort: S
status: done
classes: safety
feature: core-guard-coverage
milestone: v0.2.4
touches: tests/unit/test_simulation_view.py
added: 2026-08-25
closed: 2026-08-25
commit: 29b44d6
pr: 41
---

**Problem.** Two failure paths in `app/simulation_view.py` are never
exercised. Line 109 raises `RuntimeError("AGENT_COLOR_SCHEMES must define
exactly the built-in volatile agents")` at import time. Lines 1162 and 1168
are `_halt_run`'s deliberately swallowed render failure. Reproduce with:

```
uv run pytest --cov=src/anesthesia_sim --cov-report=json -q
```

then read `coverage.json` for missing lines that are `raise` or `except`.

**Why it matters.** Overall coverage is 96%, which is exactly why this never
surfaced: these lines sit in a module that is well covered in aggregate, so
the number stays high while the failure branch beneath it is never exercised.
Line 109 is what stands between an agent shipping without its ISO 5360
identification color and a display that identifies a drug by the wrong one.
`_halt_run` is what stands between a failed render during a halt and an
exception propagating out of the stop path.

**Where.** The tests, not the source: both paths are believed correct.

**Note on `_halt_run`.** `app/simulation_view.py:1160-1168` swallows an
exception from `_refresh_and_render` on purpose, and both the `noqa` and the
comment explaining it are right: the run is already stopped, and a frozen
display over a stopped simulation is at worst uninformative, where one over a
*running* simulation is actively misleading. What is missing is a test that
the path behaves that way — that a render failure during a halt leaves the
controller stopped and does not propagate. Do not "fix" the suppression. (The
`noqa` there is itself inert under the current ruleset; that is PL-69J3's
subject, not this item's.)

**Note on line 109.** Covering a module-level `raise` means re-executing the
module body with `AGENT_COLOR_SCHEMES` patched — `importlib.reload` plus a
monkeypatched mapping — which is fiddly enough to be worth stating up front.

**Why this item is not delegable, deliberately.** It was cut down from a
version covering all seventeen uncovered guard lines. The fourteen mechanical
ones moved to PL-QGZV, PL-3TMW, PL-5BTB, PL-T6DC, PL-7QS3 and PL-LHHG, each
provable by a single per-module `--cov-fail-under=100` command. These two are
what is left after that split: neither can be proved by a clean coverage gate,
because `simulation_view.py` will still carry thirteen uncovered
Flet-construction lines (PL-YMY7) when they are done. Bundling them with the
mechanical fourteen would have made the whole batch unprovable, which is the
distinction the delegation tier turns on.

**Done when.** Both paths are exercised — line 109 asserting the `RuntimeError`
and its message, `_halt_run` asserting that a render failure leaves the
controller stopped and does not propagate — and `make check` is green.

**Closed.** Both paths are exercised. `_halt_run` has two tests - one that the
reason records the exception *type* as well as its message, since a bare
message loses the difference between a modelling failure and a `TypeError`
from a refactor; and one that a render failure during a halt still leaves the
run stopped and propagates nothing, which is the documented intent of the
suppression. The suppression was not touched.

The module-level guard is covered by reloading the module with the colour
table one entry short, and reloading it again in a `finally` so every later
test sees the genuine table.

`simulation_view.py` now reports 11 uncovered statements, and they are exactly
the Flet-construction paths PL-YMY7 describes - 402, 472-473, 486, 529-539,
572, 621, 650, 724, 795. That confirms PL-YMY7's claim rather than closing it:
whether those want a rendering harness is still open, and belongs with PL-027.
