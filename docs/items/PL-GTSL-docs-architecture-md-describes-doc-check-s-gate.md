---
id: PL-GTSL
title: docs/ARCHITECTURE.md describes doc_check's gate-count, version-table and release-tag checks but never the resident-instruction check, the one whose output prints on every run
priority: P3
effort: S
status: ready
classes: docs
touches: docs/ARCHITECTURE.md
added: 2026-09-05
verify: python3 tools/doc_check.py check && grep -q 'check_resident_instructions' docs/ARCHITECTURE.md
---
**Problem.** `docs/ARCHITECTURE.md` describes `tools/doc_check.py`'s
gate-count, version-table and release-tag checks, and never
`check_resident_instructions` — the one whose output prints on every run.

**Why it matters.** That document is where a contributor learns what
`doc_check.py` decides and what it deliberately leaves to judgment. The check a
reader is most likely to actually meet is the one it does not explain, so the
advisory arrives with no account of what it is asking for or where the answer
is recorded. `PL-X925` is about to point that advisory at
`docs/resident-instructions.md`; a reader sent to the ledger by an advisory the
architecture document never mentions has to reconstruct the mechanism from the
message alone.

**Where.** `docs/ARCHITECTURE.md`, the `tools/doc_check.py` section, beside the
three checks already described.

**Done when.** `docs/ARCHITECTURE.md` describes `check_resident_instructions` —
what it measures, that it is an advisory rather than a gate, and what a session
is expected to do with it — and `make doc-check` passes.
