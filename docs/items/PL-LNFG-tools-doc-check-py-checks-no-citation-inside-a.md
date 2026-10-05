---
id: PL-LNFG
title: tools/doc_check.py checks no citation inside a data file's sources note, so a provenance note under src/anesthesia_sim/data/ can name a test file or a docs/MODEL.md section that does not exist and make check still passes; desflurane.json named a missing tests/reference/test_published_wash_in.py until PL-DBGT repaired it, and the notes cite as bare paths and as docs/MODEL.md, 'Section', a form check_citations does not read (split from PL-DBGT's 2026-09-19 re-scope)
status: untriaged
added: 2026-10-05
---

**Problem.** tools/doc_check.py checks no citation inside a data file's sources note, so a provenance note under src/anesthesia_sim/data/ can name a test file or a docs/MODEL.md section that does not exist and make check still passes; desflurane.json named a missing tests/reference/test_published_wash_in.py until PL-DBGT repaired it, and the notes cite as bare paths and as docs/MODEL.md, 'Section', a form check_citations does not read (split from PL-DBGT's 2026-09-19 re-scope)

**Found 2026-10-05 working `PL-DBGT`**, whose 2026-09-19 re-scope named this
as its work before `PL-PT7M` classed that item as a live-document repair; it
is split out here rather than built there (`PL-DBGT` carries why).

**What a reader of the notes has to handle.** `check_citations` in
`tools/doc_check.py` resolves code-spanned paths, Markdown links and section
marks in the documents `read_docs` hands it. A data file's `note` strings do
not use those forms: they cite a path bare
(`tests/reference/test_published_wash_in_and_elimination.py`) and a section as
the document, a comma and the title in single quotes (`docs/MODEL.md,
'Source hierarchy'`). Handing the notes to `check_citations` as they stand
would therefore check nothing.

**Measured 2026-10-05, after `PL-DBGT`'s repair.** Across
`src/anesthesia_sim/data/`, 44 `note` strings carry 48 bare path citations,
and the files carry 24 section citations in the quoted form. Every one
resolves, so the check would be preventive today. The one known miss,
`desflurane.json`'s nonexistent test path, stood from at least 2026-09-13
until this date.
