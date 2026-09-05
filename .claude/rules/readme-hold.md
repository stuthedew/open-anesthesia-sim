---
paths:
  - "README.md"
---

# `README.md` is frozen

**Do not edit `README.md`.** The project owner stopped README work on
2026-09-05: successive sessions had each improved a paragraph in isolation and
the document as a whole got worse for it. The freeze is deliberate and it holds
until they lift it.

This is not a bar on *reading* it. Read it for context freely. What is
withheld is the edit.

## What to do instead

A wrong or stale statement in `README.md` is still worth recording — file it
(`bin/docket new "..."`) and say in your reply that you did. Do not fix it in
passing, and do not fix it as part of a doc sweep: CLAUDE.md's "sweep the docs
before calling an item done" and `python3 tools/doc_check.py candidates` both
reach this file, and neither overrides this freeze. Sweep the other documents
and note the README line you left alone.

If the change you are about to make feels too small to be worth stopping for,
that is the exact class of change this freeze exists to stop. Every edit in the
sequence that produced it was small.

## Lifting it

`PL-RM83` (decide what `README.md` is for and what belongs in it) is the
owner's decision that unblocks this. `PL-N092` (rewrite README as a
human-readable introduction) is the rewrite itself and is blocked on it. When
the owner lifts the freeze, delete this file in the same commit as the first
README change — a rule stating a hold that is over is worse than no rule.
