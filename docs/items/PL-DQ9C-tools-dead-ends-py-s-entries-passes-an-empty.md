---
id: PL-DQ9C
title: tools/dead_ends.py's entries passes an empty list for the list walker's unread entries, so the session-start digest prints a dead end carried on from the margin cut short, its retrieval id lost, where check refuses the same entry by name; latent
status: untriaged
feature: one-answer
added: 2026-10-10
---

**Problem.** tools/dead_ends.py's entries passes an empty list for the list walker's unread entries, so the session-start digest prints a dead end carried on from the margin cut short, its retrieval id lost, where check refuses the same entry by name; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by this thread.
`_bullets` reads `docs/dead-ends.md` through
`docket.roadmap.document_entry_lines` and puts a line carrying an entry on
from the margin - a lazy continuation line (CommonMark 0.31.2 § 5.2) - on
`unread` rather than ending the entry short. `check` reads that list and
refuses the line by name; `entries`, which `emitted` (the digest) and `budget`
read, passes `[]` and so drops it.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against markdown-it-py 4.2.0, which reads one list item:

```text
- **An index committed beside the items** - rejected: anything an index holds is
recomputable, and an index is one more thing two branches conflict over. `PL-KM3X`
```

`emitted` prints the entry ending at `holds is`, without its id, and `budget`
counts the shorter text; `check` refuses the second line as a continuation
carried on from the margin. Latent: `make check` runs the check, so the form
cannot reach `main`, and the digest prints it only from a working tree that
fails it.

**Generator check.** A member of `PL-R417`: a surface that drops a shared
reader's named decline and answers from the partial reading, the shape
`PL-GMR6` recorded. It is the gap closed `PL-F5B9`'s fix left.

**Done when.** `entries` keeps the walker's unread lines and `emitted` names a
declined entry rather than printing it short; a test pins the form above.
