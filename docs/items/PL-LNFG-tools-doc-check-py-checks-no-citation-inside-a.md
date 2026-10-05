---
id: PL-LNFG
title: tools/doc_check.py checks no citation inside a data file's sources note, so a provenance note under src/anesthesia_sim/data/ can name a test file or a docs/MODEL.md section that does not exist and make check still passes; desflurane.json named a missing tests/reference/test_published_wash_in.py until PL-DBGT repaired it, and the notes cite as bare paths and as docs/MODEL.md, 'Section', a form check_citations does not read (split from PL-DBGT's 2026-09-19 re-scope)
priority: P3
effort: M
status: blocked
classes: test
feature: provenance
touches: tools/doc_check.py, tests/unit
blocked-by: PL-R417
added: 2026-10-05
payoff: a provenance note under src/anesthesia_sim/data/ that names a test or a docs/MODEL.md section that does not exist fails make check, instead of standing for weeks as desflurane's did
verify: grep -q 'def test_a_data_note_citing_a_missing_path_or_section_is_an_error' tests/unit/test_doc_check.py
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

**Premise re-checked at triage, 2026-10-05,** on `main` at `b67dace8`:
`check_citations` promises to resolve what "a documentation file" cites, and
`read_docs`, which hands it its input, returns Markdown documents alone; the
only reader of `src/anesthesia_sim/data/` in `tools/doc_check.py` is the
provenance table check, which reads each file's numbers and none of its
`note` strings. So nothing reads a note's citations today, as the title says.

**Why it matters.** A data file's `note` is the provenance record a reviewer
reads to learn why a clinical constant has the value it has and what verifies
it. A note naming a test that does not exist claims a verification nobody can
run, and one naming a `docs/MODEL.md` section that has moved sends the
reviewer to reasoning that is no longer there; `desflurane.json` carried the
first for three weeks with `make check` green. The notes are the one carrier of
provenance prose that no check reads.

**A new check, not a defect in one, so it waits for the generator pause.**
Reaching the notes means a reader of their own two citation forms over input
`check_citations` has never claimed to read, which is the new mechanism
`CLAUDE.md` § "What this project is" holds while any open item carries
`generator: live` - not a fix to what an existing reader gets wrong. On `main`
at `b67dace8`, `bin/docket generators` marks `PL-R417` (readers that take one
physical line for a whole statement) still generating, so `blocked-by:` names
it, as `PL-0Z0F` and `PL-JHHC` wait. Before promoting, check that `bin/docket
generators` marks no head "still generating"; building it sooner is the
owner's call, made by asking (`PL-6Q9L`).

**Generator check.** An instance of `PL-4FBP`'s fact, filed after that head
closed on 2026-09-19: the link between a document sentence and the tree fact
it restates. `PL-DBGT`, the drift this check would have caught, is in
`PL-4FBP`'s `root-cause-of:`; that head's convention reached `docs/MODEL.md`
and `README.md`, and `PL-G424`'s the apparatus documents, and neither reached
a data file's `note`. One instance after the close, so not a generator of its
own; recorded for `PL-04KR`'s re-entry reading. Not a member of `PL-R417`:
nothing here is a statement read across lines.

**Done when.** `make check` resolves every bare repository path and every
`docs/MODEL.md, 'Section'` citation in a `note` string under
`src/anesthesia_sim/data/`, reporting one that names nothing by its data file
and key path, and declining by name a note whose citation it cannot read; a
test in `tests/unit/test_doc_check.py` holds a note naming a missing test file
and one naming a missing section to an error each, and today's notes pass.
