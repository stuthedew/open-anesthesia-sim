---
id: PL-FBWD
title: core_vocabulary_check.symbol_cells takes every line opening with | under its heading for a Symbols row, so a row inside an HTML comment or a fence, the table under a setext heading, or a second table after a blank line is read into the vocabulary, and a row without its leading pipe is skipped; latent
status: untriaged
feature: one-answer
touches: tools/core_vocabulary_check.py, tests/unit
added: 2026-10-04
---

**Problem.** core_vocabulary_check.symbol_cells takes every line opening with | under its heading for a Symbols row, so a row inside an HTML comment or a fence, the table under a setext heading, or a second table after a blank line is read into the vocabulary, and a row without its leading pipe is skipped; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

GFM 0.29 § 4.10 (a table ends at a blank line or another block; outer pipes are optional) with CommonMark § 4.6, § 4.5 and § 4.3. Each form adds rows to `symbol_cells` that `roadmap.table_rows` and `statement_lines` do not read: a commented-out row, a pipe line in a fenced example, the table under a setext heading that ends the section, and a second table after a blank line. Loud rather than silent: each misread row draws a false finding. `PL-HRTH` (an escaped `\|`) is a different defect in the same reader. Latent: `docs/MODEL.md`'s Symbols table holds none of these forms.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
