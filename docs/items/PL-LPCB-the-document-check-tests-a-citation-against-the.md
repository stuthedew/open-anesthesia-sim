---
id: PL-LPCB
title: The document check tests a § citation against the cited document's headings only where the citation sits in a docstring with the § mark and the document named on the same line, so a citation in a # comment, a possessive such as docs/MODEL.md's note, or a bare § strands silently when a section moves or is renamed
priority: P1
effort: M
status: done
classes: defect
feature: doc-consistency-checks
touches: .claude/hooks/guard.py, .claude/hooks/hook_input.py, .claude/hooks/owner_ask_guard.py, .claude/hooks/thread_hooks.py, .claude/rules/ui-areas.md, .claude/thread-probe-plugin/hooks/probe.py, docs/apparatus.md, src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/display_units.py, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/preferences.py, src/anesthesia_sim/app/view_contract.py, src/anesthesia_sim/app/view_registry.py, src/anesthesia_sim/core/supported_ranges.py, subprojects/docket/README.md, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/python.py, tests/integration/controller/controller_support.py, tests/integration/controller/test_controller_bookmarks.py, tests/integration/controller/test_controller_stored_states.py, tests/unit/test_agent_cost.py, tests/unit/test_dashboard_frame.py, tests/unit/test_doc_check.py, tests/unit/test_thread_probe.py, tools/doc_check.py, tools/github_refusals_check.py, tools/import_boundary_check.py, tools/model_rewrite.py, tools/required_checks_check.py, tools/skill_start_eval.py, docs/items/PL-WZVZ-make-an-inter-machine-difference-attributable.md
deferred-from: v0.7.0 - a workflow check with no link to what v0.7.0 ships: it decides no value a learner sees, and the citations it strands are filed as found
added: 2026-11-22
closed: 2026-11-22
pr: 2211
payoff: a section move that would strand a citation fails the document check at once, instead of reaching the queue as one item per stranded citation
tests: tests/unit/test_doc_check.py::test_a_section_mark_in_python_is_refused_once_its_heading_is_renamed, tests/unit/test_doc_check.py::test_a_section_mark_naming_words_that_are_no_heading_is_refused, tests/unit/test_doc_check.py::test_a_mark_after_a_document_and_a_comma_is_held_to_its_headings, tests/unit/test_doc_check.py::test_a_bare_mark_names_the_document_its_passage_named_last, tests/unit/test_doc_check.py::test_a_section_mark_in_a_code_span_or_an_outside_source_without_it_is_not_read
root-cause-of: PL-10BC, PL-GC7Z, PL-Q2DK, PL-97S1, PL-CVTG
generator: spent - the document check now reads a section mark in a comment, after a possessive and bare, and holds each to the cited headings
misread: Which heading of which document a § citation in a comment, possessive or bare § names
---

**Problem.** The document check tests a § citation against the cited document's headings only where the citation sits in a docstring with the § mark and the document named on the same line, so a citation in a # comment, a possessive such as docs/MODEL.md's note, or a bare § strands silently when a section moves or is renamed

Found by the triage pass of 2026-11-22. Five items name one fact: which section, in which document, a citation names. Each was a citation the document check could not test.

1. `PL-97S1` (done): two citations of a `docs/MODEL.md` note with no section mark.
2. `PL-CVTG` (done): open items still naming `docs/MODEL.md` for sections `PL-CTXZ` moved to `docs/INTERFACE.md`.
3. `PL-10BC` (open): code comments and docstrings citing `docs/MODEL.md` for text `#2109` moved, many written as a `#` comment, a possessive or a bare §.
4. `PL-GC7Z` (open): a `#:` comment above `REFERENCE_CONDITION_LABEL` citing a note without its section.
5. `PL-Q2DK` (open): two citations of a `ROADMAP.md` heading that has since gained the word "Completed", which the check passes because the new heading still holds the old words.

`PL-97S1`'s record gives the cause: the check reads a citation only in a docstring, and passes it when the cited document holds the words anywhere.

**Why it matters.** `PL-48MX` and `PL-SY7G`, the later stages of splitting `docs/MODEL.md` and `docs/INTERFACE.md` by reader, will move more sections. Each move strands every citation the check cannot read, and each stranded citation becomes a queue item found by hand. A reader who follows a stranded citation to a clinical document finds the wrong section or none.

**Done when.** The document check reads a § citation wherever this repository writes one: in a docstring, in a `#` or `#:` comment, in a possessive form, and as a bare § whose document is named on the line before. It refuses a citation whose heading the cited document does not hold exactly, rather than one whose words appear anywhere in it. A test shows each form refused after a heading is renamed.

**Generator check.** This item is the head. The misread fact is which heading of which document a § citation names, and no earlier head's `misread:` states it.

**Done 2026-11-22.** `tools/doc_check.py` now reads a § citation in four
places it did not, and holds each to the cited document's headings.

1. **Comments.** `_quoting_sources` yields each run of Python comment, `#`
   and `#:` alike, beside the docstrings. Before this, 87 marked citations in
   comments were read by nothing.
2. **Headings, not words.** A quotation after the section mark, in
   `check_quoted_sources`, is tested with `_cites_heading` against the cited
   document's headings and bold leads, the test `check_citations` already
   applied to a Markdown document's own marks. Tested by containment, the
   `ROADMAP.md` milestone headings that gained "Completed: " passed, because
   the new heading still holds the old words. A quotation after any other
   connective is still tested by containment, since this project quotes a
   sentence that way as often as a title.
3. **The possessive with the mark.** `POSSESSIVE` admits a mark after the
   possessive, so `` `ROADMAP.md`'s § "X" `` is a section citation. The
   pattern used to take the possessive, meet the mark where it wanted the
   quotation, and read nothing.
4. **The bare mark.** In a docstring or a comment, a § citation with no source
   directly before it names the document its passage named last, in a code
   span or bare. Where the passage names none, the mark must name a heading
   of some documentation file, as `check_citations` requires of a Markdown
   document's mark. A mark in a code span is a literal and is not read. An
   outside source's section is written without the mark, as the documents
   already did.

The refusal names the document that does have the heading, where one does, so
a section that moved is sent to where it went.

**What the new check found, all fixed in this change.** 35 errors on the tree
at `a7eb53f`:

1. Sections that moved from `docs/MODEL.md` to `docs/INTERFACE.md`: § "F_A/F_I
   as a displayed ratio" in `app/formatting.py`; § "A cost at the reader's
   price" in `app/preferences.py` and twice in `tests/unit/test_agent_cost.py`;
   § "Supported run length" in `core/supported_ranges.py`; § "Halting on a
   marked crossing" in `tests/integration/controller/test_controller_bookmarks.py`.
   These are entries 2, 3, 4 and 5 of `PL-10BC`'s list.
2. Sections that no longer exist: § "The canonical evaluation rule", which
   #2180 replaced, now `docs/INTERFACE.md` § "Each second has one stored
   state", in `tests/integration/controller/controller_support.py`; and
   `docs/MODEL.md` § "State vector", which `docs/MODEL.md` never had, now
   `core/governing_equations.py` § "The state vector", in
   `tests/integration/controller/test_controller_stored_states.py`.
3. `ROADMAP.md` milestone headings that gained "Completed: " (`PL-Q2DK`), in
   `app/area_layout.py`, `app/view_contract.py` (twice), `app/view_registry.py`,
   `app/dashboard_frame.py`, `tests/unit/test_dashboard_frame.py`,
   `tools/import_boundary_check.py` (four places, three of them in the
   messages it prints), `.claude/rules/ui-areas.md` and `PL-WZVZ`'s brief.
4. A bold lead cited with a lower-case first letter, in
   `subprojects/docket/README.md`.
5. Bare marks after a document that did not hold the section:
   `tests/unit/test_formatting.py`, whose document was written bare and is now
   read; `tools/doc_check.py`, now naming `ROADMAP.md`; and `tools/model_rewrite.py`,
   whose example now names two real sections.
6. Marks naming a section of an outside page, now written as "section":
   `.claude/hooks/guard.py`, `hook_input.py`, `owner_ask_guard.py` and
   `thread_hooks.py`, `.claude/thread-probe-plugin/hooks/probe.py`,
   `subprojects/docket/src/docket/python.py`, `tests/unit/test_thread_probe.py`,
   `tools/github_refusals_check.py` (twice), `tools/required_checks_check.py`,
   `tools/skill_start_eval.py`, and a fixture's heading in a helper docstring of
   `tests/unit/test_doc_check.py`.
7. A comment in `subprojects/docket/src/docket/checks.py` quoting `PL-RTG9`'s
   brief in words it no longer holds, now a paraphrase, and a comment example in
   `tools/doc_check.py` quoting a `docs/WORKING_NOTES.md` thread since removed.

`PL-GC7Z`'s comment in `app/display_units.py` is rewritten in the form
`PL-97S1` gave `core/liquid_agent.py`, with the mark before the note's name.

**Tests.** The new tests in `tests/unit/test_doc_check.py` fail on the
check before this change, nine cases of ten; the tenth is the code-span case,
which passes on both. Six existing tests now expect the heading refusal where
they expected the containment one.

**Docs checked.** `tools/doc_check.py`'s module docstring and the docstrings of
`_quoting_sources` and `check_quoted_sources`; the comments above
`CITATION_RE`, `CITATION_CONNECTIVE` and `QUALIFIED_RE`; `docs/apparatus.md`'s
entry for `doc_check.py`, now naming comments and the heading test;
`.claude/rules/citation-drift.md`, which describes `check_citations` and
`check_line_citations` and needed no change; `tools/possessive_section_check.py`,
which reads `_quoting_sources` and now reads comments too, and reports nothing.

**Blind review, 2026-11-22.** Two passes ran on the branch.

1. Pass 2, should-fix, fixed: a mark after a document and a comma, a colon, a
   parenthesis or `under`, as in `` `docs/MODEL.md`, § "Time" ``, was read by
   nothing, since `QUOTED_SOURCE_RE` takes one connective and `QUALIFIED_RE`
   told the other readers to leave it. `CONNECTED_MARK_RE` reads it now, in
   documents, live briefs and Python alike. The tree held none that failed.
2. Pass 1, optional, fixed: `check_quoted_sources`' docstring said case is
   folded, which is now true of its containment test only. It says so.
3. Pass 1, optional, filed as `PL-MWL0`: a mark after a code-spanned Python
   file, or after an item id and a connective other than the mark or the
   possessive, is still read by nothing.
