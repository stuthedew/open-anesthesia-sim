---
id: PL-5NC3
title: docket's roadmap.table_rows ends a table at the first row without outer pipes and silently drops the rows after it, and splits a cell on an escaped pipe, so the version table and the timeline would read short; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/markdown.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: the version table and the timeline are read row for row as GitHub renders them, so a row without its outer pipes or holding an escaped pipe drops nothing
verify: grep -qF '"table rows, ' tests/unit/test_doc_check.py
---

**Problem.** docket's roadmap.table_rows ends a table at the first row without outer pipes and silently drops the rows after it, and splits a cell on an escaped pipe, so the version table and the timeline would read short; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

GFM 0.29 § 4.10: a table runs to a blank line or another block, and its outer pipes are optional (spec example 201). With `| v0.5.21 | Completed` (no trailing pipe) above a full row, `table_rows` and `parse_version_table` both return `[]`, where markdown-it-py 4.2.0 reads both rows; `v0.5.21 | Completed` does the same. Reached through `parse_version_table`, `parse_timeline`, `milestone_states`, `release_train` and `baseline_gate`. A cell holding an escaped `\|` is split there: `| v0.5.22 | Completed \| current baseline |` reads status `Completed \` and `is_baseline` False. Latent: the version table (85 rows) and the timeline (16 rows) agree with markdown-it row for row. The unit read short is the table rather than a row.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `09cdc761`, `table_rows` over a version table whose first body row omits its trailing pipe returns no rows of the two written, and a status cell holding `\|` reads as the cells `['v0.5.22', 'Completed \\', 'current baseline']`.

**Why it matters.** `parse_version_table` and `parse_timeline` are where docket reads which release is current and what the release train holds, so a table read short drops every row after the first one written without its outer pipe, and the version and baseline checks then answer from part of the table without saying so.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** `table_rows` reads a GitHub Flavored Markdown 0.29 table - outer pipes optional, rows running to a blank line or another block's start, `\|` a pipe inside its cell - from one reading of the document's blocks; `table rows, ...` cases in `CONTINUED_STATEMENTS` pin it.
