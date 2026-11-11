---
id: PL-CTXZ
title: Move the seven interface sections of docs/MODEL.md, word for word, to a new interface document for contributors, re-point the code's citations of them, and extend the documentation checks to the new file (stage 1 of the split PL-P3GZ decided)
priority: P1
owner-priority: P1, 2026-11-11, ratified
effort: L
status: done
classes: docs
feature: model-md-structure
touches: docs/, tools/, subprojects/docket/, .claude/, CLAUDE.md, docket.toml, README.md, ROADMAP.md, src/anesthesia_sim/, tests/
added: 2026-11-11
closed: 2026-11-11
pr: 2109
payoff: a contributor finds what the interface must show in one document, and a clinician no longer reads past 60,000 words of interface rules to reach the model
verify: ! grep -qE '^## (Runtime controls|Minimum displayed outputs)$' docs/MODEL.md
---

**Problem.** Move the seven interface sections of docs/MODEL.md, word for word, to a new interface document for contributors, re-point the code's citations of them, and extend the documentation checks to the new file (stage 1 of the split PL-P3GZ decided)

**Why it matters.** The project owner decided on 2026-11-11 to split
`docs/MODEL.md` by reader (`PL-P3GZ`, which holds the design and the
counts). Seven sections state what the interface must do. Their reader is a
contributor who changes the interface, and a clinician reads past them.
They hold 59,940 of the document's 129,000 words, the code cites them 141
times, and most of the 60 open items that will edit `docs/MODEL.md` add to
them. This is the first of three moves, so it also sets up what the other
two reuse.

**What to do.**

1. Create the interface document under `docs/`. The build chooses the file
   name. Move these `##` sections of `docs/INTERFACE.md` into it unchanged:
   "Runtime controls"; "Reset behavior"; "Agent-change behavior";
   "Discarding a run, and the questions that guard it"; "What a branch
   comparison asserts, and what it does not"; "Interface boundary";
   "Minimum displayed outputs".
2. Re-point each citation of a moved section with a script: in `src/`, in
   `tests/`, in the other documents and in the item briefs that are open.
   `tools/doc_check.py` already refuses a docstring citation when the
   document it names holds no such heading.
3. Make everything that reads `docs/MODEL.md` as the specification read
   the new file too. `PL-P3GZ` lists them under "What the split changes
   outside the documents": `CLAUDE.md`, `.claude/rules/plain-writing.md`
   (a row for the new document and its reader), `tools/doc_check.py`,
   `subprojects/docket/src/docket/arming.py`, six tools and the rules,
   skills and agents that name the path. State the list of specification
   documents once, where those tools read it, so that `PL-6PPZ` and
   `PL-FWR6` each add one path.
4. Leave one sentence in `docs/MODEL.md` that names the new document and
   what it holds.
5. Show that the move lost nothing: every value, equation, code span and
   citation of the moved sections is in the new file. `tools/model_rewrite.py
   lost` makes that comparison within one file. Check first whether it can
   compare across two.
6. Re-point the `touches` of `PL-SY7G` (sort the interface document) at the
   new file.

**What it must not do.** Change no word, value, equation, code span or
citation in the moved text. A section that mixes readers moves whole;
sorting its paragraphs is stage 3. Run no copy editor on the moved text: the
owner's hold of 2026-11-10 lasts for this document until its stage 3 item
closes. Set no word target (`PL-J1ZM`).

**Branches in flight.** A branch that edits a moved section ports its edit
to the new file once, when it brings `main` in. Say so in the pull request
body, with the list of moved headings.

**The pause on new workflow mechanisms.** The owner asked for the split, and
pointing the existing checks at the new file keeps them reading the text
they read today. The item builds no new check.

**Done when.** `docs/MODEL.md` holds none of the seven headings, the new
document holds the seven sections word for word, every citation of them
resolves, the checks that read `docs/MODEL.md` read the new file, and
`make check` passes.

**Generator check.** Part of the fix for the cause that `PL-P3GZ` records:
the repository named no home but `docs/MODEL.md` for a test's description,
an interface requirement or a value's source history, so each change added
them there. No new head.

**Built 2026-11-11.** The interface document is `docs/INTERFACE.md`, named
like `docs/MODEL.md` and `docs/ARCHITECTURE.md`.

*The move.* `python3 tools/model_rewrite.py move --to docs/INTERFACE.md` cut
lines 3814 to 9651 of `docs/MODEL.md`, the seven sections, and appended them
to the new file under a title and one opening paragraph. `docs/MODEL.md`
§ "Status" gained one paragraph that names the new document. The moved text
differs from the original in two ways only, both made by the script. In 72
places a section mark that names a section still in `docs/MODEL.md` now has
`` `docs/MODEL.md` `` before it, and in 4 of those the word "above" or "below"
after it is gone, because the documentation check reads those words as "in
this file". The text left in `docs/MODEL.md` gained `` `docs/INTERFACE.md` ``
before 39 marks in the same way. `python3 tools/model_rewrite.py lost` prints
no equation, declaration, code span, citation or number as held fewer times,
and prints those two paths as the only additions.

*The citations.* The same command re-pointed about 380 citations in about 110 files: the
code, the tests, the standing documents and the open briefs. It reads a
mention of `docs/MODEL.md` and the quotation after it, and re-points the
mention when the quotation names a heading that only the new document has, or
words that only the new document holds. Nine citations that the script could
not read were re-pointed by hand: messages in `core/supported_ranges.py`,
`core/circuit.py`, `app/formatting.py` and `app/dashboard_frame.py` whose
section name is split across two string literals or filled in from a variable.
The script took the quotation after a path in a `verify:` command for that
path's own, which is wrong for `grep 'text' path`. So each open item's
`verify:` was then pointed at the document that holds its text, and the six
items whose titles name a moved section were renamed to the file names their
new titles give.

*What reads the new file.* `docket.arming.SPECIFICATION_DOCS` lists the
documents of the specification, and `tools/product_paths.py` passes it on.
`tools/doc_check.py` (the stored-value markers and the two bound families
that moved), `tools/model_rewrite.py` and `tools/model_doc_review.py` read it.
`PL-6PPZ` and `PL-FWR6` each add their document there. Four lists restate a
path and stay separate, because `tools/config_home_check.py` compares each
with its home and names every copy when one differs: `protected_paths`,
`product_paths` and the `simulator` area in `docket.toml`, and
`SECOND_PASS_PATHS` in `docket.arming`. `CLAUDE.md`, `docs/worker.md`, the
reader table in `.claude/rules/plain-writing.md` and the rules, skills and
agents that named `docs/MODEL.md` as the specification name both files.

*What was left.* A mention of `docs/MODEL.md` that names no section was not
re-pointed, because no script can tell which document it means. `PL-10BC`
holds that. The copy editor read only the three passages this item wrote: the
new document's opening paragraph, the new paragraph in `docs/MODEL.md` and
the two entries in `README.md`'s list of documents. It read none of the moved
text, as this brief requires, and none of the passages where only a path
changed.

*What the two blind review passes found.* Twelve findings, nine of them
new, and all were real and fixed on the branch. A test,
`tests/reference/test_mac_awake_washout_figures.py`, still opened
`docs/MODEL.md` to read a section that had moved, so it failed. Where one
path stood before two section names and the move parted the sections, the
second section kept the wrong document: in the three agent files' notes on
`mac_percent`, and in five docstrings and comments. Two refusals named the old
document with no quoted section. The documentation check passed a section
mark that named the wrong one of the two documents, because each document
holds the other's heading words in its pointers. It now refuses one, and
`test_a_section_mark_naming_the_wrong_specification_document_is_refused`
checks that. The opening paragraphs did not say that the supported ranges and
the supported run length are in the new document, and now do.
`tools/model_rewrite.py repoint` now lists each second section name for a
person to read.

**The mutation check, 2026-11-11.** It ran 21 mutants on the lines this
branch changed, and the unit tests caught 17. The 4 that survived changed
only the wording of two refusals that this branch re-pointed: the refusal of
an amount with no derived precision, in `app/formatting.py`, and the refusal
of an instant not built as `CaseInstant`, in `core/supported_ranges.py`.
`test_a_unit_with_no_derived_precision_is_refused` and
`test_a_value_not_built_as_the_type_is_refused_whatever_it_holds` now compare
the end of each message with the sentence written out in the test. Each
failed with its mutant applied by hand: the sentence wrapped in `XX`, in
lower case and in upper case for the first, and wrapped in `XX` for the
second.

The check gave no answer at first, for two causes that were on `main`. This
branch fixed both in `pyproject.toml`, and `PL-GP8G` fixed both on `main`
while the branch was open, so the merge took `main`'s settings. The two
regression tests this branch wrote stay in `tests/unit/test_diff_mutation.py`.

**The copy edit of the last two comments was skipped.** The two tests above
each gained a two-line comment after the last copy edit. The project owner
said "skip copy edit" on 2026-11-11, while the copy editor was reading them,
so the trailer on the commit that records this says it read none.

