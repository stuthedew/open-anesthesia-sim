---
id: PL-HKHP
title: docket's heading scans - roadmap's table_rows, baseline_heading, _subsection_ids, _subsection_text, _section_end and parse_milestones, checks._labels and notes.read - take each physical line a heading pattern matches for a heading, so a ## line inside a multi-line HTML comment or a fence opens a section and a setext heading opens none; latent
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/notes.py, subprojects/docket/src/docket/markdown.py, subprojects/docket/README.md, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-04
pr: 1358
payoff: a commented-out or fenced heading opens no section and a setext one opens its own, so milestones, working-notes threads and answers are read from the headings the page shows
verify: grep -qF '"docket headings, ' tests/unit/test_doc_check.py
---

**Problem.** docket's heading scans - roadmap's table_rows, baseline_heading, _subsection_ids, _subsection_text, _section_end and parse_milestones, checks._labels and notes.read - take each physical line a heading pattern matches for a heading, so a ## line inside a multi-line HTML comment or a fence opens a section and a setext heading opens none; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

CommonMark 0.31.2 § 4.6 kind 2 (an HTML comment runs to its `-->`), § 4.5 (a fence) and § 4.3 (a setext heading's text and underline are two lines). `statement_lines` reads each such block whole; these scans do not go through it.

- `parse_milestones` over a `## v9.9.9` section with its own Required scope, commented out across lines, returns a phantom section whose own scope is `PL-MNPQ`; a milestone template in a fenced block does the same.
- `baseline_heading("<!--\n## Current baseline: v9.9.9\n-->\n\n## Current baseline: v0.5.22\n")` returns `(2, '9.9.9')`, and `table_rows` takes a commented-out version table's row before the live one.
- A setext heading ("Explicitly out of scope for v9.9.0" over `====`) under a Required scope list is not seen, so the entry under it is read as scope.
- `checks._answered_beneath` reads a commented `## Answers 2026-09-30` as an answer, which would make `_check_item` refuse the status, and misses a setext one.
- `notes.read` takes a `##` line inside a fence or a multi-line comment for a thread and misses a setext thread heading, so `docket show` names the wrong thread and the stale-open-thread advisory names a phantom.

Related forms the same scans miss: an ATX heading indented one to three spaces (§ 4.2), and `_subsection_text` and `_subsection_ids` reading ids inside any HTML comment into `own_scope_ids` and `excluded_ids`. Latent: ROADMAP.md's one comment (line 380) sits on one line, its one fence (488-491) holds no heading, no document the scans read uses a setext heading, and `docs/WORKING_NOTES.md`'s 26 headings are all ATX outside fences.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `09cdc761`, `baseline_heading` over a commented-out `## Current baseline: v9.9.9` above the live `## Current baseline: v0.5.22` returns `(2, '9.9.9')`; `notes.read` takes a `##` line inside a fence for a thread and misses a setext one; `parse_milestones` lists only `Required scope` for a section whose `Explicitly out of scope` heading is written setext; and `_answered_beneath` returns "Answered 2026-09-30" for an answer heading inside a comment.

**Why it matters.** These scans decide which milestone a section is, which subsection holds the frozen list, the scope and the exclusions, which release is the baseline, which thread a working note belongs to, and whether a brief's question is answered, so a commented-out or fenced template, or a heading written setext, moves each of those answers without an error.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** Each scan named above reads headings as CommonMark 0.31.2 does - ATX headings indented up to three spaces and setext headings, none inside an HTML block, a fence or a paragraph - from one reading of the document's blocks, and `_subsection_text` and `_subsection_ids` read no id from an HTML block or a fence; `docket headings, ...` cases in `CONTINUED_STATEMENTS` pin it.
