---
id: PL-GKX6
title: bin/docket delegable offers an item whose work creates a new tracked file outside every workflow_paths and product_paths entry, while its touches omit docket.toml, so tools/workflow_paths_check.py fails make check and the worker must block (PL-928V, docs/workflow.md)
priority: P3
effort: S
status: ready
classes: defect
feature: worker-runs
touches: subprojects/docket/src/docket/model.py, subprojects/docket/tests/test_model.py
added: 2026-10-20
payoff: a paid worker run is never spent on an item it can only block on
verify: grep -q 'def test_an_item_touching_an_unplaced_path_is_not_delegable' subprojects/docket/tests/test_model.py
---

**Problem.** bin/docket delegable offers an item whose work creates a new tracked file outside every workflow_paths and product_paths entry, while its touches omit docket.toml, so tools/workflow_paths_check.py fails make check and the worker must block (PL-928V, docs/workflow.md)

**Observed 2026-10-20.** `PL-928V` declares `touches: docs/workflow.md,
README.md, docs/consultant-brief.md`. The file `docs/workflow.md` does not
exist yet, and no entry in `workflow_paths` or `product_paths` covers it. Once
the file is tracked, `tools/workflow_paths_check.py` refuses it, and placing
it needs an edit to `docket.toml`. A worker may not edit outside `touches`, so
the item could only be blocked. Triage or `bin/docket delegable` could catch
this before the item is handed over: a `touches` path that does not exist yet
and that neither list places will always need `docket.toml` as well.

**Reviewed 2026-10-24.** Adding `docket.toml` to such an item's `touches` is
not a fix either: `docket.toml` is in `gate_paths`, so the item stops being
delegable. The catch this item asks for therefore withholds the item rather
than proposing a wider `touches`. `PL-928V` carries the decision for its own
case.

**Why it matters.** A worker run is paid from the monthly API credit. An item offered by `bin/docket delegable` that the worker can only block on wastes that run and a reviewing session's time. **Checked 2026-10-24:** `Item.delegability` in `subprojects/docket/src/docket/model.py` reads `protected_paths` and `gate_paths` only, and never asks whether `workflow_paths` or `product_paths` places a `touches` path. `PL-928V` now declares `docket.toml` in its `touches`, so it is withheld as touching the checks; this item is about the next such item.

**Done when.** `Item.delegability` withholds an item whose `touches` names a path that neither `workflow_paths` nor `product_paths` places, with a reason saying that placing it needs `docket.toml`, and `subprojects/docket/tests/test_model.py` has `test_an_item_touching_an_unplaced_path_is_not_delegable`.

**Generator check.** A one-off. The fact is which list places a path, and `tools/workflow_paths_check.py` already reads it; `delegability` is a reader that never asked. No head's `misread:` states that fact, and no other open item misreads it.
