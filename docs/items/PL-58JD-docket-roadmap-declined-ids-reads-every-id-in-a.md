---
id: PL-58JD
title: docket.roadmap._declined_ids reads every id in a deferral subsection's prose as disposed, and on 2026-09-23 that disposed PL-FD5Q through a sentence saying it was absent from the list: the first counterexample to PL-H6VQ's measured finding that the narrowing would catch none
status: untriaged
added: 2026-09-23
---

**Problem.** docket.roadmap._declined_ids reads every id in a deferral subsection's prose as disposed, and on 2026-09-23 that disposed PL-FD5Q through a sentence saying it was absent from the list: the first counterexample to PL-H6VQ's measured finding that the narrowing would catch none

**Found 2026-09-23**, fixing `#953`'s red `checks` job. `tools/doc_check.py`
listed ten triaged items as owing a v0.6.0 gate disposition but not `PL-FD5Q`,
also triaged to `defect` in that pass. Its only mention in a deferral subsection
was the other 2026-09-23 pass's sentence saying it "is absent: this pass left it
untriaged". `_declined_ids` runs `re.findall(ID_PATTERN, ...)` over the whole
subsection, so that sentence read as its disposition. `#953` gave it a real
entry, so the instance is gone from the tree. The mechanism is not:
`PL-H6VQ`'s count on 2026-09-21 was 97 prose-only dispositions a narrowing would
break, against none it would catch, and this is the first it would have caught.

**Generator check.** A member of `PL-WD5Z` (gate dispositions are ids
mentioned in `ROADMAP.md` prose). The regex reads prose as dispositions because
prose is where dispositions are recorded. It is the `_declined_ids` shape
`PL-H6VQ` measured in `tools/doc_check.py`, carried into `docket.roadmap` when
`PL-J6HP` gathered the gate readers, and it was filed the day `PL-J6HP` closed
as `spent`.
