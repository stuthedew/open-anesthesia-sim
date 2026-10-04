---
id: PL-YSMD
title: docket's roadmap.list_entry_lines ends an entry at a blank line, opens one at an ordered marker past 1 inside a paragraph, and reads entries inside an HTML comment or a fence but none on an empty marker line, so gates, scopes, dead ends and release notes read entries CommonMark does not; live in form, no answer changed
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests, tests/unit
added: 2026-10-04
recurrences: 2026-10-04 PL-HKHP withdrawn 2026-10-04 PL-R417, 2026-10-04 PL-BLKJ withdrawn 2026-10-04 PL-R417, 2026-10-04 PL-J0C6 withdrawn 2026-10-04 PL-R417
---

**Problem.** docket's roadmap.list_entry_lines ends an entry at a blank line, opens one at an ordered marker past 1 inside a paragraph, and reads entries inside an HTML comment or a fence but none on an empty marker line, so gates, scopes, dead ends and release notes read entries CommonMark does not; live in form, no answer changed

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

Checked against `roadmap.statement_lines` and markdown-it-py 4.2.0, the walker under `list_entries`, `document_entry_lines` and through them `_gate_entries`, `_scope_entries`, `doc_check._list_members`, `dead_ends._bullets` and `release.notes_bullets` misreads five forms:

- **A loose item's later paragraph** (CommonMark 0.31.2 § 5.2) belongs to no entry and nothing declines it. Under `### Required scope`, `- **Real entry**: ...` followed by a blank line and `  **Admitted 2026-09-30** as (queue item `PL-BCDF`).` reads as an entry declaring no queue item, and `doc_check.check_scope_declarations` reports a false error; under MODEL.md's "Minimum displayed outputs" `_list_members` drops the indented line naming the member's test.
- **An ordered marker past 1 wrapped to a line's start** (§ 5.2: only a list starting at 1 may interrupt a paragraph) opens a phantom entry: a gate paragraph wrapping "...dropped to" onto "21. PL-ZZZZ was withdrawn when its feature was cut." reads `PL-ZZZZ` as a frozen entry.
- **An entry inside an HTML comment block** (§ 4.6 kind 2) **or a fence** (§ 4.5) is read: a `docs/dead-ends.md` entry commented out is emitted into every session's start digest while `dead_ends.check` passes, and a notes bullet inside a comment holding a blank line is reported by `release.unreferenced`. Without a blank line inside, the `-->` line is declined as a lazy line - a decline, for the wrong reason.
- **An item opening on an empty marker line** (`-`, then `  PL-CCCC Title on the next line — #5`) reads as nothing, and nothing goes on `unread`.
- `LIST_ENTRY_RE` reads a spaced thematic break (`- - -`, § 4.1) as an entry and never reads a `+` bullet or a `1)` item - not continuations, but the same pattern's reading of where an entry starts.

Live in form: 21 ROADMAP.md entries carry a second paragraph (ROADMAP.md:5928, "1. **The layout model**", is one); none of the dropped paragraphs holds a `(queue item` slot and gate ids come from the entry head, so no answer changes today. The other forms are latent: no tracked document the walker reads holds them.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
