---
id: PL-GKX6
title: bin/docket delegable offers an item whose work creates a new tracked file outside every workflow_paths and product_paths entry, while its touches omit docket.toml, so tools/workflow_paths_check.py fails make check and the worker must block (PL-928V, docs/workflow.md)
status: untriaged
added: 2026-10-20
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
