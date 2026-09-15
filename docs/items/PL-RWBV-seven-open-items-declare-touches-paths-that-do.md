---
id: PL-RWBV
title: Seven open items declare touches paths that do not exist, three of them naming core/run_score.py which PL-ZX12 renamed to run_definition.py
priority: P3
effort: S
status: ready
classes: defect, infra
feature: queue-hygiene
touches: docs/items
added: 2026-09-14
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_a_touches_path_that_neither_exists_nor_is_named_as_new_is_reported' subprojects/docket/tests/test_checks.py
---

**Problem.** Seven open items declare touches paths that do not exist, three of them naming core/run_score.py which PL-ZX12 renamed to run_definition.py

**Recounted 2026-09-15, after the Qt port (#588) landed.** Eight open items now
declare a `touches` path that does not exist, and the composition has moved
since the title was written - `core/run_score.py` appears once, not three times,
so `PL-ZX12`'s rename has mostly been absorbed, while the port has added two of
its own:

| item | path that does not exist |
| --- | --- |
| `PL-5B1N` | `tests/unit/test_simulation_view.py` |
| `PL-8PSW` | `src/anesthesia_sim/app/chart_series.py` (deleted by the port) |
| `PL-928V` | `docs/workflow.md` |
| `PL-CNCF` | `src/anesthesia_sim/core/run_score.py` |
| `PL-LWMS` | `.mailmap` |
| `PL-R808` | `tests/unit/test_left_behind_check.py` |
| `PL-RD3B` | `src/anesthesia_sim/app/run_series.py` |
| `PL-ZG5J` | `tests/benchmarks` |

Two kinds are mixed here and want opposite answers: a path renamed out from
under the item (`run_score.py`, `chart_series.py`, `run_series.py`) is a
re-point, while a path that never existed (`tests/benchmarks`,
`test_left_behind_check.py`, `.mailmap`) is the item declaring where its work
*will* go, which is legitimate and should not be "fixed" into a wrong path.

**Why it matters.** `touches` is load-bearing rather than descriptive. It
decides the workflow/product lane split (`docket.toml`'s `workflow_paths`), the
concurrency graph `bin/docket concurrent` answers from, and delegability against
`protected_paths` and `gate_paths` - and every one of those reads it as a
membership test, so a path that matches nothing fails open and says nothing. An
item naming a renamed module can therefore be offered to two sessions at once,
or offered to a cheaper model because the protected path it really touches is
spelled with a name no longer in `protected_paths`. That last one is the
expensive case: `PL-CNCF`'s `core/run_score.py` is `core/run_definition.py`,
which is protected, and the stale spelling is not.

**Done when.** Every open item's `touches` names a path that exists or a path
its own work creates, and a check decides the difference rather than a reader -
the natural home is `docket check`, beside the guards that already read
`touches`, reporting a path that neither exists nor is named by the item's body
as new.
