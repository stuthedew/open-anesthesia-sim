---
id: PL-0Y7J
title: doc_check's six other heading readers - _provenance_rows, _subsection_end, _uncheckable_heading_counts, _subsection_line, _list_members and _tags_region - match HEADING_RE a line at a time, so a # line inside a fence or a comment opens or ends the section each reads; latent
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit, docs/items/PL-T1X0-doc-check-s-headings-and-hash-headings-read-a.md, subprojects/docket/src/docket/roadmap.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-05 triage pass
added: 2026-10-05
closed: 2026-10-05
pr: 1382
payoff: a shell sample's comment line in ROADMAP.md or docs/MODEL.md can no longer cut the provenance table, a gate's subsection or the Tags region short, so doc_check reads each section where docket and GitHub do
verify: grep -qF 'provenance rows, a # line inside a fence is no heading' tests/unit/test_doc_check.py && grep -qF 'subsection end, a # line inside a fence is no heading' tests/unit/test_doc_check.py && grep -qF 'uncheckable heading counts, a # line inside a fence is no heading' tests/unit/test_doc_check.py && grep -qF 'subsection line, a # line inside a fence is no heading' tests/unit/test_doc_check.py && grep -qF 'list members, a # line inside a fence is no heading' tests/unit/test_doc_check.py && grep -qF 'tags region, a # line inside a fence is no heading' tests/unit/test_doc_check.py
---

**Problem.** doc_check's six other heading readers - _provenance_rows, _subsection_end, _uncheckable_heading_counts, _subsection_line, _list_members and _tags_region - match HEADING_RE a line at a time, so a # line inside a fence or a comment opens or ends the section each reads; latent

**Found 2026-10-05 by `PL-R417`'s link 11 (`#1371`)**, closing `PL-T1X0`, whose fence half moved `_hash_headings` onto `docket.markdown.headings`. Six other readers in `tools/doc_check.py` still match `HEADING_RE` against every physical line, and none skips a literal block:

- `_provenance_rows`, which finds the provenance table of `docs/MODEL.md` under its `##` heading and stops at the next one;
- `_subsection_end`, where a gate subsection of `ROADMAP.md` stops. Its docstring says it reads that end the way `_gate_entries` does, and docket's `roadmap._subsection_end`, the bound `_gate_entries` takes, reads `markdown.headings` since `PL-HKHP`, so the two already disagree about a fenced `###` line;
- `_uncheckable_heading_counts`, the count-carrying headings under a gate;
- `_subsection_line`, where a milestone's subsection opens;
- `_list_members`, the heading a bound family's list sits under;
- `_tags_region`, which ends the `**Tags.**` region at the next heading.

A `#` line inside a fence or an HTML comment is that block's (CommonMark 0.31.2 § 4.5, § 4.6), so a shell sample's comment, or a heading commented out, ends or opens the section each of these reads: a table or a list cut short, a subsection read past its end, or a region closed early.

**Latent.** Measured 2026-10-05 on `main` at 9258a2ef: no line `HEADING_RE` matches lies inside a fence, an HTML block or an indented code block in `ROADMAP.md`, `docs/MODEL.md`, `README.md`, `CLAUDE.md` or `docs/WORKING_NOTES.md`, read through `markdown.block_lines`.

**Reproduced 2026-10-05** at triage, on `main` at `b67dace8` under python3 3.11.15, and the latent count re-run there, still 0 in each of the five documents. `_provenance_rows` over a `## Parameter provenance` section holding a `sh` fence whose one line is `## a shell comment`, then the provenance header (`Parameter | Selected value | Unit | Source`) and one row, returned no rows and no note, which its caller reports as "no provenance table found under 'Parameter provenance'"; the same text without the fence returned the row. `_tags_region` over `**Tags.** x`, a blank line and a `sh` fence holding `# c` ended the region at the fence's `# c` line. The other four match `HEADING_RE` against each line in turn, as these two do.

**Why it matters.** Each of the six decides what a check holds. Where a fenced `#` line ends a section early - the provenance table, a gate's headings, the `**Tags.**` region - the check fails on a correct document, and the remedy its message invites is to delete or move a correct shell sample. Where one opens a section (`_subsection_line`, `_list_members`) or ends a gate subsection where docket's `roadmap._subsection_end` does not, `doc_check` and docket read different entries from one `ROADMAP.md`, and nothing says so. A shell sample with a comment line is the ordinary way to document a command, so the first written under one of these headings trips it.

**Not a recurrence of `PL-T1X0`.** `docket new` matched this capture to it on the shared path and recorded a recurrence there, which link 11 withdrew: `PL-T1X0` named `_headings` and `_hash_headings` alone, and these are six other readers of the same fact.

**Generator check.** A member of `PL-R417`: where one statement ends. A `#` line inside a fenced block is part of that block, the half `PL-HKHP` fixed in docket and `PL-T1X0` in `_hash_headings`. Recorded in its `root-cause-of:` by link 11.

**Done when.** Each of the six reads its headings through `markdown.headings`, or the block reader's heading blocks, so a `#` line inside a fence or a comment opens and ends no section; `HEADING_RE`, then read by nothing in `tools/doc_check.py`, leaves its import; and `PL-R417`'s guard gains a case per reader, each failing on today's reader.

**As built, 2026-10-05.** The six read their headings through
`docket.markdown.headings`, so a `#` line a fence or an HTML comment holds
opens and ends no section. `_provenance_rows` finds its `##` heading there,
ends the section where docket's `roadmap._section_end` does, and takes its
table from `markdown.tables`, so a table a fence holds is not taken for the
provenance table either; on `docs/MODEL.md` it reads the same 37 rows as
main's reader. `doc_check`'s own `_subsection_end` is gone: the gate count
check imports docket's, the bound `_gate_entries` takes, so the two cannot
disagree about a fenced `###` line again. `_uncheckable_heading_counts`,
`_subsection_line`, `_list_members` and `_tags_region` walk the same
headings, and `_list_members` starts its list where the heading's block
ends, a setext underline included. `HEADING_RE` left `tools/doc_check.py`'s
import, and `TABLE_ROW_RE` with it, whose one reader there was
`_provenance_rows`; nothing else in the repository read either, so both left
`docket.roadmap` too, whose docstring now names `CONTINUED_LINE` as the
primitive it exports. `PL-R417`'s guard gained eight cases, one per reader
under the names this item's `verify:` gives, a table in a fence for
`_provenance_rows` and a `###` heading in a comment for
`_uncheckable_heading_counts`; each fails with main's `doc_check.py` and
passes here. `doc_check check` reports the same over the tree under both
readers, and is clean under the 3.11 floor.
