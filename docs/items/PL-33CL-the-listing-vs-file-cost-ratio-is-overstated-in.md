---
id: PL-33CL
title: The listing-vs-file cost ratio is overstated in three places, and drifts
status: dropped
added: 2026-08-24
closed: 2026-08-24
reason: superseded by the move to docs/items/; the tool and skill making the claims were deleted
---

**Problem.** `tools/punch_list.py` claimed the listing cost a twenty-fifth of
reading `docs/PUNCH_LIST.md` and the skill claimed a fortieth, where the
measured figure was a seventeenth.

**Why it matters.** The claims were the stated justification for reading the
listing instead of the file, and a hardcoded multiplier drifts every time the
queue changes length.

**Resolution.** Both files were deleted with the single-file store. The
successor states no ratio at all: with one file per item, reading an item
costs one file, and there is no whole-queue document to compare against.
