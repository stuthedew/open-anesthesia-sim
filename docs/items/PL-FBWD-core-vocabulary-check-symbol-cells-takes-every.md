---
id: PL-FBWD
title: core_vocabulary_check.symbol_cells takes every line opening with | under its heading for a Symbols row, so a row inside an HTML comment or a fence, the table under a setext heading, or a second table after a blank line is read into the vocabulary, and a row without its leading pipe is skipped; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/core_vocabulary_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-05
pr: 1358
payoff: the Symbols table is read as GitHub renders it, so no commented, fenced or second-table row reaches the vocabulary check and no row without its leading pipe escapes it
verify: grep -qF '"vocabulary symbols, ' tests/unit/test_doc_check.py
---

**Problem.** core_vocabulary_check.symbol_cells takes every line opening with | under its heading for a Symbols row, so a row inside an HTML comment or a fence, the table under a setext heading, or a second table after a blank line is read into the vocabulary, and a row without its leading pipe is skipped; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

GFM 0.29 § 4.10 (a table ends at a blank line or another block; outer pipes are optional) with CommonMark § 4.6, § 4.5 and § 4.3. Each form adds rows to `symbol_cells` that `roadmap.table_rows` and `statement_lines` do not read: a commented-out row, a pipe line in a fenced example, the table under a setext heading that ends the section, and a second table after a blank line. Loud rather than silent: each misread row draws a false finding. `PL-HRTH` (an escaped `\|`) is a different defect in the same reader. Latent: `docs/MODEL.md`'s Symbols table holds none of these forms.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `09cdc761`, `symbol_cells` returns two rows for a Symbols table followed by a commented-out row, where GitHub renders one.

**Why it matters.** `docs/MODEL.md`'s Symbols table ties each symbol a reader meets to the code that computes it, and this check holds every Code cell to `core/`, so a row read from a comment, a fence or a second table draws a false finding, and one written without its leading pipe is never checked.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** `symbol_cells` reads the first table under the Symbols heading through the table reader `roadmap.table_rows` uses, header row included; a `vocabulary symbols, ...` case in `CONTINUED_STATEMENTS` pins it.
