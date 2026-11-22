---
id: PL-RLRG
title: docs/MODEL.md's paragraphs for a clinician carry item ids and decision records such as '(project owner, 2026-09-04, ratified', and nothing refuses them: tools/model_rewrite.py ids lists them and no check or close-out step runs it
priority: P2
effort: M
status: done
classes: defect, docs
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/MODEL.md, .claude/skills/docket/modes/close-out.md
deferred-from: v0.7.0 - present at the freeze and not on the frozen list; found by the 2026-11-10 audit; it changes how the specification reads and no value in it
added: 2026-11-10
closed: 2026-11-22
pr: 2237
payoff: a clinician reading docs/MODEL.md meets no record of who decided what and when, and a session that adds one fails the build
tests: tests/unit/test_doc_check.py::test_a_decision_record_in_a_paragraph_for_a_clinician_is_refused, tests/unit/test_doc_check.py::test_an_item_id_in_a_list_item_or_table_of_the_model_document_is_refused, tests/unit/test_doc_check.py::test_an_item_id_or_a_date_the_model_document_does_not_show_is_not_refused, tests/unit/test_doc_check.py::test_a_decision_record_split_by_a_line_wrap_is_refused
---

**Problem.** docs/MODEL.md's paragraphs for a clinician carry item ids and decision records such as '(project owner, 2026-09-04, ratified', and nothing refuses them: tools/model_rewrite.py ids lists them and no check or close-out step runs it

**Checked 2026-11-10:** `grep -c 'project owner, 20' docs/MODEL.md` prints 20, and one of the matches is "(project owner, 2026-09-04, ratified". `tools/model_rewrite.py` has an `ids` command that lists the item ids a section cites. `grep -rn 'model_rewrite.py ids'` over `Makefile`, `.github`, `.claude` and `tools/` finds no caller.

**Why it matters.** `.claude/rules/plain-writing.md` names the first reader of `docs/MODEL.md` as a clinician who does not know this repository's own names, and says "Decision history goes in the item". A decision record in a clinician's paragraph is text for a later session. `PL-J1ZM` (prose over-explains) has been answered three times with more rule text, and `PL-ZYHX` measured that writing rules with a check had no violations while rules without one recurred.

**The pause on new workflow mechanisms.** The project owner lifted it for this item on 2026-11-10.

**Done when.** `make check` refuses a decision record, the text "(project owner, " followed by a date, in a `docs/MODEL.md` paragraph outside a note that opens "**For developers.**". It starts from a baseline of the 20 present today, and the baseline may only shrink. The count of item ids per section, which `tools/model_rewrite.py ids` already prints, is shown at close-out as an advisory, because the rule allows an id as a pointer. Read `PL-P3GZ` first (decide whether to split `docs/MODEL.md` by reader, on pull request #2088): a split changes which file the check reads, not the rule.

**Generator check.** An instance of `PL-J1ZM`'s fact (what a reader can do without), found while that head is open. The audit's reviewer reported that the head's members also show the opposite defect, private compressed wording (`PL-VGDX`, `PL-2K0K`); `PL-VZ57` carries that lead.

**Checked 2026-11-22** against `d4e8200`: partly done. The decision records in paragraphs for a clinician fell from 20 to 5 since 2026-11-10. A count over whole paragraphs finds "(project owner, 2026-09-13)" twice, "(project owner, 2026-09-04, ratified" once, "(project owner, 2026-09-20" in the circuit-volume paragraph and "(project owner, 2026-09-06)" in the paragraph on the open-circuit diagnostic. None of the five is in a note that opens "**For developers.**". `grep -n "project owner" tools/doc_check.py` finds no check that refuses them, and `tests/unit/test_doc_check.py` has no `test_a_decision_record_in_a_paragraph_for_a_clinician_is_refused`. So the check is still unbuilt, and its starting baseline would now be 5, not 20. `PL-48MX` (replace what is left of `docs/MODEL.md` with the accepted description) is still blocked, so the file the check reads has not changed yet.

**Done 2026-11-22**, on `claude/project-thread-v9awbd` from `c0e9861e`.

**The text half was already done.** The restructure (`PL-48MX`, #2222) left `docs/MODEL.md` with no decision record and no item id: `grep -c "project owner" docs/MODEL.md` and `grep -c "PL-[0-9A-Z]\{4\}" docs/MODEL.md` both print 0 at `c0e9861e`.

**The pause did not apply.** `bin/docket generators` on 2026-11-22 marks three heads "still generating": `PL-GJ1W`, `PL-LHCL` and `PL-RF2S`. Each declares paths under `src/anesthesia_sim/` or `docs/MODEL.md` in `touches`, so none is in the workflow lane that `docket.toml`'s `workflow_paths` defines, and the rule in `.claude/skills/docket/modes/triage.md` pauses new workflow mechanisms only for a live workflow-lane head. The owner had also lifted the pause for this item on 2026-11-10.

**The check.** `check_model_reader_text` in `tools/doc_check.py`, run by `make check` through `analyze`, refuses two things in the text `docs/MODEL.md` shows (paragraphs, list items, headings and tables, code spans included; HTML comments are not shown and are not read):

1. A decision record, "(project owner, " followed by an ISO date, read with `ISO_DATE_RE` from `docket.instructions`.
2. An item id, read with the store's own `ID_PATTERN`.

**It refuses item ids outright, where the brief asked for an advisory count at close-out, and it has no baseline.** Both choices follow from the restructure. The baseline of decision records was 20 when the item was filed and is now 0, so the check refuses every one and there is nothing to shrink. The brief kept ids as an advisory because `.claude/rules/plain-writing.md` rule 5 allows an id as a pointer. Since `PL-48MX`, `docs/MODEL.md` holds no note for developers (`.claude/rules/sources-and-docstrings.md`), its reader is a clinician who does not know this repository's names (`.claude/rules/document-readers.md`), and it holds no id. An advisory counting ids per section would print zeros at every close-out and change no decision, which `.claude/rules/apparatus-standard.md` § "A check earns its place every run, or it is retired" counts as a defect in a check. So no step was added to `.claude/skills/docket/modes/close-out.md`, and `tools/model_rewrite.py ids` stays a tool for rewrites. An id a developer needs goes in `docs/VERIFICATION.md` or `docs/PARAMETERS.md`, and the refusal message says so. If the owner wants ids allowed as pointers in `docs/MODEL.md`, deleting the second loop of `check_model_reader_text` restores the brief's version.

Tests: `test_a_decision_record_in_a_paragraph_for_a_clinician_is_refused`, `test_an_item_id_in_a_list_item_or_table_of_the_model_document_is_refused` and `test_an_item_id_or_a_date_the_model_document_does_not_show_is_not_refused` in `tests/unit/test_doc_check.py`. They call a function that `c0e9861e` lacks. The variant that needs no new interface: in a worktree at `c0e9861e`, appending "The circuit volume was chosen for teaching (project owner, 2026-09-04, ratified), see `PL-48MX`." to `docs/MODEL.md` and running `uv run python tools/doc_check.py check` printed "documentation: 0 errors" and exited 0. On this branch the same planted text fails with "docs/MODEL.md:N records a decision" and "names the item `PL-48MX`".

Files checked: `docs/MODEL.md`, `.claude/rules/sources-and-docstrings.md`, `.claude/rules/document-readers.md`, `.claude/rules/plain-writing.md` and `.claude/skills/docket/modes/close-out.md`. None states a rule the check contradicts, and none lists `doc_check`'s checks by name.

**Blind review of #2237, 2026-11-22: fixed.** Both passes found that the check read `docs/MODEL.md` one line at a time, so a decision record split by a hard wrap passed: "(project\nowner, 2026-09-04, ratified)" and "(project owner,\n2026-09-04, ratified)" gave no error. The check now blanks every line the reader is not shown, joins the rest, and matches the record with a `GAP` (a space or a soft break, `markdown.SOFT_BREAK`) at each of its two spaces. The error gives the line on which the record starts. New test: `test_a_decision_record_split_by_a_line_wrap_is_refused`, with one case for each wrap point. Against the line-at-a-time check, `uv run pytest -q tests/unit/test_doc_check.py -k split_by_a_line_wrap` failed both cases with `assert 0 == 1` (`where 0 = len([])`), "2 failed".
