---
id: PL-QJD3
title: Restructure the docs/references/ notes and index as the copy editor's structure read proposes, so a clinician checking a stored value meets what the paper backs first and each fact once
status: done
feature: repo-copy-edit
touches: docs/references/
added: 2026-11-07
closed: 2026-11-07
pr: 2046
verify: grep -q '^# Cited sources and their readings' docs/references/README.md && grep -q '^## Values recorded from the paper' docs/references/katoh-1993-anesth-analg-mac-awake-washout.md
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

The closing prose review read the 41 changed passages and rewrote 35. Its rewrite of the index's "Extraction notes" section was not taken, because it cut rules for writing notes that `.claude/rules/citing-sources.md` does not hold (the licence check before adding a file, rewriting history with `git filter-repo`, reading PDF metadata).

**Done when.** Each note opens with what its paper backs, states each fact once, and every stored value and page it records is still there.

**Generator check.** The owner asked for this work (2026-11-05, "copy edit entire repo", and "Structure first" for these files). It is one area of a repository-wide copy edit, not a defect, so no mechanism caused it.
