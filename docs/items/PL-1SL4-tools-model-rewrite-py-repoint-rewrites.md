---
id: PL-1SL4
title: tools/model_rewrite.py repoint rewrites citations inside test fixtures, and re-points by body text a section that was rewritten rather than moved
priority: P3
effort: S
status: done
classes: defect
feature: doc-consistency-checks
touches: tools/model_rewrite.py, tests/unit/test_model_rewrite.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-22
closed: 2026-11-27
pr: 2336
payoff: a session that re-points citations after a section rewrite gets correct citations and passing fixture tests, with nothing to revert by hand
tests: tests/unit/test_model_rewrite.py::test_repoint_reads_only_the_comments_and_docstrings_of_a_test_tree, tests/unit/test_model_rewrite.py::test_a_section_mark_before_a_heading_neither_document_holds_is_unplaced
---

**Problem.** tools/model_rewrite.py repoint rewrites citations inside test fixtures, and re-points by body text a section that was rewritten rather than moved

**Found 2026-11-22**, while building `PL-48MX`. `python3 tools/model_rewrite.py
repoint docs/MODEL.md docs/VERIFICATION.md` was run after the clinician's text
replaced the old sections of `docs/MODEL.md`. Two things went wrong, and every
change it made was reverted by hand.

1. It edited string fixtures in `tests/unit/test_doc_check.py` and
   `tests/unit/test_model_rewrite.py`, because `paths` defaults to every
   tracked text file. A fixture that quotes `docs/MODEL.md` § "..." is input
   for a test, not a citation, and the rewrite made those tests fail.
2. It re-pointed a citation of "Governing equations" to `docs/VERIFICATION.md`.
   The old heading was in neither document, and the moved developer text in
   `docs/VERIFICATION.md` held the words, so the second rule of `repoint`
   applied. The equations stay in `docs/MODEL.md`. The rule
   assumes the section moved whole, and a section rewritten in place breaks
   that assumption. "Model boundary" was re-pointed the same way.

**What would fix it.** Leave the test trees out of the default `paths`, or
leave out string literals. Refuse the body-text rule where the source
document lost the heading without the destination gaining it, and report the
citation as unplaced instead.

**Why it matters.** The next session that runs `repoint` after a section rewrite will get failing fixture tests and wrong citations, and has to revert each edit by hand, as `PL-48MX` did.

**Done when.** A test shows that `repoint` leaves the test trees alone by default, and a second test shows that a heading missing from both the source and the destination is reported as unplaced, not re-pointed by body text.

**Generator check.** A one-off: one tool's two assumptions, that every tracked file is prose and that a section moves whole. No head's `misread:` states either.

**Done 2026-11-27.** `repoint` and `misattributed` in `tools/model_rewrite.py` now read a file under a test tree, as `docket.toml`'s `collected_test_paths` lists them, for its comments and docstrings only. `_citing_spans` finds them with `docket.python.docstrings` and the tokenizer. A string literal in a test's body is the test's input, so it is left alone, and so is every test file that is not Python. A test file that Python's tokenizer or parser cannot read, including one nested too deeply to parse, is listed as unread rather than passed over. Leaving the test trees out whole was the brief's first option, and it was not taken: their docstrings and comments hold 285 section citations of the documents, which a move has to re-point.

A quotation after a section mark (`§`) is now re-pointed only where the destination holds it as a heading. The mark says the quotation names a heading, as `tools/doc_check.py`'s `CITATION_RE` reads it, so a heading neither document holds is listed as unplaced instead of following the words the destination happens to hold. A quotation without the mark still follows its words.

**Measured on the tree at `8f404cfa`.** `python3 tools/model_rewrite.py repoint --to docs/VERIFICATION.md`, run with the old tool, re-pointed 13 citations in 5 files, 12 of them string literals in `tests/unit/test_doc_check.py`, `tests/unit/test_model_rewrite.py`, `tests/unit/test_new_prose.py` and `subprojects/docket/tests/test_fences.py`, and listed 38 unplaced. The new tool re-pointed 1, in `ROADMAP.md`, touched no test file and listed 7. The run takes 8 seconds. Both runs were reverted.

**Regression.** Both new tests fail against the tool at `8f404cfa`. `test_repoint_reads_only_the_comments_and_docstrings_of_a_test_tree` fails because the citation in the fixture string was re-pointed to the destination. `test_a_section_mark_before_a_heading_neither_document_holds_is_unplaced` fails because the marked citation of a heading that neither document holds was re-pointed to the destination too.

**Documents checked:** `tools/model_rewrite.py`'s module docstring, which describes `repoint` and now names both rules; `docs/apparatus.md`'s package-map line for the tool, whose one clause on `repoint` is still true; and `docs/maintainer.md`, `docs/WORKING_NOTES.md` and `.claude/skills/`, which describe only `lost`.
