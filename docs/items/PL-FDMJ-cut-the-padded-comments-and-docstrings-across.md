---
id: PL-FDMJ
title: Cut the padded comments and docstrings across tests/
priority: P2
effort: M
status: ready
classes: docs
feature: prose-quality
touches: tests
added: 2026-09-05
not-delegable: readability is judged by a person, and no command separates a trimmed comment from a padded one. A length ceiling would be met by deleting the sentence naming what a test is defending, which is the one thing this item must keep
---

**Problem.** The comments and docstrings in `tests/` are, in the project
owner's reading (2026-09-05), far too verbose and poorly written. One of two
halves split out of `PL-XXBD` (rewrite the code comments across `src/` and
`tests/`), which was `L` and therefore unstartable from the queue.

**Measured 2026-09-05:** 4,530 of `tests/`'s 17,356 lines are comment or
docstring prose - 26% of the tree, and almost exactly the same volume as
`src/`'s 4,644, which is what makes the `src`/`tests` split an even one.
`tests/unit` holds 3,271 of it, `tests/reference` 807 and `tests/integration`
452.

**Why it matters.** The standard is **human readability**: a person opening the
file should reach the point faster and understand more. Wordiness is the defect
and cutting it is the fix. This is deliberately *not* the standard `PL-JK0M`
applies to the agent-facing instruction files.

**The qualifier, which is what a test docstring is for.** A test's prose says
what behavior it is defending and why that behavior matters - often the only
record of a bug that a regression test exists to keep dead. Cut the padding
around that sentence; never cut the sentence. A citation to a published
reference case, a tolerance and the reason for it, and a named `PL-` id are all
facts rather than prose.

**Three files are out of scope**, and by the project's own boundary rather than
by preference: `tests/unit/test_contrast_check.py`,
`tests/unit/test_doc_check.py` and `tests/unit/test_import_boundary_check.py`
are named in `docket.toml`'s `workflow_paths`, which counts them apparatus
rather than product - so `CLAUDE.md`'s "working reliably and staying
streamlined" governs them, not the specialist standard this item applies. The
same reasoning kept `docs/WORKING_NOTES.md` out of the prose split.

**Where.** `tests/`, less the three files above.

**Done when.** Every comment and docstring under `tests/` outside those three
files has been read and, where it was padded, cut: nothing restating the line
below it, no docstring paragraph repeating its own first sentence. Every
statement of what a test defends, every reference citation and every tolerance
rationale is still on the page. `make check` passes, and the suite still
reports 1,759 tests at 100% core coverage.
