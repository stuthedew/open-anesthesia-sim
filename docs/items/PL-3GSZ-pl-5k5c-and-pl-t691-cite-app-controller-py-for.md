---
id: PL-3GSZ
title: PL-5K5C and PL-T691 cite app/controller.py for ControlInput and ControlChange, which PL-RD3B moved to app/control_record.py, and doc_check resolves the path rather than the symbol so nothing caught it
priority: P3
effort: S
status: ready
classes: docs
feature: queue-hygiene
touches: docs/items
added: 2026-09-15
verify: python3 tools/doc_check.py check && grep -q 'app/control_record.py' docs/items/PL-5K5C-record-the-model-s-sea-level-assumption-and-the.md && grep -q 'app/control_record.py' docs/items/PL-T691-the-run-is-its-control-input-timeline-hold.md
---

**Problem.** PL-5K5C and PL-T691 cite app/controller.py for ControlInput and ControlChange, which PL-RD3B moved to app/control_record.py, and doc_check resolves the path rather than the symbol so nothing caught it

**Why it matters.** Both citing items are open, so the next session to start
either is handed a path that no longer exists and has to rediscover where
`ControlInput` and `ControlChange` went. `PL-RD3B` moved them to
`app/control_record.py` and closed on 2026-09-15; both citations were written
before that, and nothing re-reads a citation once it is written.

The class is invisible to the tooling in two separate ways, which is why this
is filed rather than fixed in passing. `tools/doc_check.py` resolves the *path*
in a citation and never asks whether the symbol named beside it still lives
there, so `app/controller.py` resolves cleanly while the sentence around it is
wrong - and `PL-1RTM` is the second gap, where the queue's path citations are
not resolved at all. Fixing `PL-1RTM` does not catch this one: the path is
real, and only the pairing is stale.

**Done when.** `PL-5K5C` and `PL-T691` cite `app/control_record.py` for
`ControlInput` and `ControlChange`, and `python3 tools/doc_check.py check`
passes.
