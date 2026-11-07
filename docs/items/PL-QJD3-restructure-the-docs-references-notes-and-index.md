---
id: PL-QJD3
title: Restructure the docs/references/ notes and index as the copy editor's structure read proposes, so a clinician checking a stored value meets what the paper backs first and each fact once
status: untriaged
feature: repo-copy-edit
touches: docs/references/
added: 2026-11-07
---

**Problem.** Restructure the docs/references/ notes and index as the copy editor's structure read proposes, so a clinician checking a stored value meets what the paper backs first and each fact once

**What the structure read found, and what was done** (the project owner ran
the copy editor's structure read on their Mac on 2026-11-06, on the API credit;
its findings are on branch `claude/repo-copy-edit-api` under
`copy-edit-runs/docs-references-*/structure/`). The owner chose on 2026-11-05
to apply the structure read before the line edit for these files.

- Each paper note now opens with what the paper backs for a clinician, says
  once that the repository holds no copy, and defines the private corpus in its
  reading record. The sentences written for later sessions and for note
  writers are gone from the notes.
- Facts given twice are given once, where a reader checking a value looks: the
  slow-washout group sizes, the equilibration times, the coefficient sources,
  halothane's values (now a table column), the tissue-coefficient source with
  its full citation, the cohort of the *Anesthesiology* study.
- Headings say what their sections hold, and the derivation and the uses of
  each value are grouped.
- The figure-reading method keeps what each step measured. The tooling detail
  moved to `PL-R0NL`.
- `docs/references/README.md` opens with what the directory holds and the three
  tiers, then the documents, then the redistribution and corpus records, then
  the rules for writing notes under one heading. Rule 1 no longer asks a note
  to point at its index entry, because the notes no longer carry that pointer.
  Rule 5 names the third standing a source has: cited in `docs/MODEL.md` for a
  description or a caution. The owner's reason for removing the M4 paper moved
  to `PL-8LXM`.

The structure read's queries that the repository could answer were answered in
the text. The four it could not are filed as `PL-FQFP`, `PL-56DQ`, `PL-JSBW`
and `PL-5XRK`.
