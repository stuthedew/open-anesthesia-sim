---
id: PL-5NC3
title: docket's roadmap.table_rows ends a table at the first row without outer pipes and silently drops the rows after it, and splits a cell on an escaped pipe, so the version table and the timeline would read short; latent
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests
added: 2026-10-04
---

**Problem.** docket's roadmap.table_rows ends a table at the first row without outer pipes and silently drops the rows after it, and splits a cell on an escaped pipe, so the version table and the timeline would read short; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

GFM 0.29 § 4.10: a table runs to a blank line or another block, and its outer pipes are optional (spec example 201). With `| v0.5.21 | Completed` (no trailing pipe) above a full row, `table_rows` and `parse_version_table` both return `[]`, where markdown-it-py 4.2.0 reads both rows; `v0.5.21 | Completed` does the same. Reached through `parse_version_table`, `parse_timeline`, `milestone_states`, `release_train` and `baseline_gate`. A cell holding an escaped `\|` is split there: `| v0.5.22 | Completed \| current baseline |` reads status `Completed \` and `is_baseline` False. Latent: the version table (85 rows) and the timeline (16 rows) agree with markdown-it row for row. The unit read short is the table rather than a row.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
