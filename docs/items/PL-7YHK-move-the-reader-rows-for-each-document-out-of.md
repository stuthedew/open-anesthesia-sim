---
id: PL-7YHK
title: Move the reader rows for each document out of the resident plain-writing rule into a rule that loads with those documents, so that adding a specification document does not push the instructions loaded at launch over their cap
priority: P1
effort: S
status: done
classes: housekeeping
feature: model-md-structure
touches: .claude/rules/plain-writing.md, .claude/rules/document-readers.md, tools/new_prose.py, tests/unit/test_new_prose.py, docs/resident-instructions.md
added: 2026-11-22
closed: 2026-11-22
pr: 2204
payoff: a new specification document can join the checks without the instructions every session loads at launch passing their cap, and each document's reader loads with the document
tests: tests/unit/test_new_prose.py::test_a_document_rule_without_the_reader_table_is_refused_by_name
---

**Problem.** Move the reader rows for each document out of the resident plain-writing rule into a rule that loads with those documents, so that adding a specification document does not push the instructions loaded at launch over their cap

**Why now.** `tools/doc_check.py` fails `make check` when the instruction
files loaded at launch hold more than `RESIDENT_CAP` characters (55,120, set
on 2026-11-20, `PL-G3KZ`). `main` held 55,114 on 2026-11-22. `PL-6PPZ` adds
`docs/VERIFICATION.md` to three resident lists that
`tools/config_home_check.py` holds to `SPECIFICATION_DOCS`, to the sentence in
`CLAUDE.md` that names the authoritative specification, and to the reader
table, which `test_every_product_document_has_a_reader_except_the_release_notes`
requires. That is about 500 characters, and `PL-FWR6` adds as many again.
`docs/resident-instructions.md` § "The cap of 2026-11-21" says such an edit
moves a rule to a check, a skill or a path-scoped rule.

**What to do.** Move each row of the table in `.claude/rules/plain-writing.md`
whose kind of text is a document into a new path-scoped rule,
`.claude/rules/document-readers.md`, whose `paths:` are those documents. The
rows for docstrings, comments, string literals, replies, item briefs, the
workflow's files, commit messages and pull requests stay resident, because a
session writes those without opening a document first. `tools/new_prose.py`
reads the readers from both files. Record the move in
`docs/resident-instructions.md`.

**Generator check.** Not a generator. The cap is working as intended: it
turned the growth that each new specification document brings into a routing
decision. Each document's rows are needed only once the document is open, so
the path-scoped rule delivers them at that moment, and no reader changes.

**Done 2026-11-22**, in pull request #2204. Ten rows moved to
`.claude/rules/document-readers.md`, with the new row for
`docs/VERIFICATION.md`, and `.claude/rules/plain-writing.md` points at it.
That cut about 2,450 characters from the instructions loaded at launch.
`tools/new_prose.py` reads both tables and names the file whose table it
cannot read. The move is recorded in `docs/resident-instructions.md`
§ "What was routed out".

**Files checked** for a sentence that says the reader table is in
`.claude/rules/plain-writing.md` alone: `CLAUDE.md`, `docs/apparatus.md`,
`docs/resident-instructions.md`, every rule and skill under `.claude/`,
`tools/new_prose.py` and its test.
