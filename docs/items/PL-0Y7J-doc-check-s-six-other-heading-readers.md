---
id: PL-0Y7J
title: doc_check's six other heading readers - _provenance_rows, _subsection_end, _uncheckable_heading_counts, _subsection_line, _list_members and _tags_region - match HEADING_RE a line at a time, so a # line inside a fence or a comment opens or ends the section each reads; latent
status: untriaged
feature: one-answer
touches: tools/doc_check.py, tests/unit, docs/items/PL-T1X0-doc-check-s-headings-and-hash-headings-read-a.md
added: 2026-10-05
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

**Not a recurrence of `PL-T1X0`.** `docket new` matched this capture to it on the shared path and recorded a recurrence there, which link 11 withdrew: `PL-T1X0` named `_headings` and `_hash_headings` alone, and these are six other readers of the same fact.

**Generator check.** A member of `PL-R417`: where one statement ends. A `#` line inside a fenced block is part of that block, the half `PL-HKHP` fixed in docket and `PL-T1X0` in `_hash_headings`. Recorded in its `root-cause-of:` by link 11.

**Done when.** Each of the six reads its headings through `markdown.headings`, or the block reader's heading blocks, so a `#` line inside a fence or a comment opens and ends no section; `HEADING_RE`, then read by nothing in `tools/doc_check.py`, leaves its import; and `PL-R417`'s guard gains a case per reader, each failing on today's reader.
