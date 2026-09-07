---
id: PL-8B1K
title: Two citations into docs/WORKING_NOTES.md name sections that no longer exist
priority: P3
effort: S
status: done
verify: python3 tools/doc_check.py check && ! grep -q 'near-term to-dos' src/anesthesia_sim/core/uptake_system.py && ! grep -q 'Splitting error outside' docs/items/PL-042-bound-the-splitting-error-across-the-settings.md
classes: docs
feature: dev-tooling
touches: src/anesthesia_sim/core/uptake_system.py, docs/items/PL-042-bound-the-splitting-error-across-the-settings.md
added: 2026-09-01
closed: 2026-09-07
---

**Problem.** Two places cite a `docs/WORKING_NOTES.md` section by name, and
neither section is in the file any more. Threads there are rewritten and
deleted as they resolve — which the file's own header asks for — so a citation
by section title decays silently.

- `src/anesthesia_sim/core/uptake_system.py:5-9` sends a reader to the
  `"near-term to-dos"` open thread "for a scoped cleanup of this class's
  boundaries". No such heading exists; `grep -n 'near-term to-dos'
  docs/WORKING_NOTES.md` returns nothing.
- `docs/items/PL-042-bound-the-splitting-error-across-the-settings.md:37`
  ended its brief with

  ```text
  **Context.** `docs/WORKING_NOTES.md`, "Splitting error outside the gate's
  operating point".
  ```

  No such heading exists, and no line of the file contains the word
  "splitting". Shown fenced because `check_quoted_sources` reads an unfenced
  one as this item's own citation.

**Why it matters.** The `uptake_system.py` one is the live half: it is a
module docstring on a `core/` class, so a contributor reading the class is
sent to a document that will not answer, and the thing it promises — a scoped
cleanup of the class's boundaries — does exist, as `PL-006` (clarify what
`AgentUptakeSystem` actually owns), which already carries both this file and
`docs/WORKING_NOTES.md` in its `touches`. The `PL-042` one is in a closed
item's record (`status: done`, closed 2026-08-26), so it misleads only a
reader reconstructing that decision's history.

**Where.** The two lines above. Recommended fix: repoint the docstring at
`PL-006` rather than at a section title, and either repoint or drop the
**Context.** line in `PL-042`. Prefer citing an item id over a section title
anywhere a citation has to survive the thread being rewritten.

**Related.** `PL-X2XX` is why neither was caught: `tools/doc_check.py` reads
neither file. Landing that one turns both of these into `make check` errors,
so it is the cheaper order — fix them as the check surfaces them.

**Done when.** Neither citation names a heading that does not exist, and each
points at something that will still answer after the next thread is rewritten.
