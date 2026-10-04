---
id: PL-YSMD
title: docket's roadmap.list_entry_lines ends an entry at a blank line, opens one at an ordered marker past 1 inside a paragraph, and reads entries inside an HTML comment or a fence but none on an empty marker line, so gates, scopes, dead ends and release notes read entries CommonMark does not; live in form, no answer changed
priority: P3
effort: M
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/markdown.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: a gate, scope, dead-end or release-notes entry is read as the item the rendered page shows, so none is counted that is not there or dropped that is
verify: grep -qF '"list entries, ' tests/unit/test_doc_check.py
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

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `09cdc761`, `list_entry_lines` under `### Required scope` returns `[(2, 3), (5, 6)]` for a loose entry whose second paragraph declares `(queue item PL-BCDF)`, so the declaration belongs to no entry; `[(3, 4)]` for "21. PL-ZZZZ was withdrawn." wrapped inside a gate paragraph; `[(3, 4)]` for an entry inside an HTML comment; `[]` for a marker standing alone over "  PL-CCCC Title on the next line"; and `[(2, 3)]` for `- - -` above a `+` entry and a `1)` entry, which it never reads.

**Why it matters.** The frozen list, `Required scope`, `docs/dead-ends.md` and every release's notes are read through this walker, so each form above is a gate entry, a scope declaration, a dead end or a released item a session is shown, or not shown, against what the rendered page says, and nothing declines any of the five.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** The walker reads each top-level list item as CommonMark 0.31.2 does - its later paragraphs and nested blocks included, any bullet or ordered marker, an item opening on an empty marker line, no marker inside an HTML block or a fence, a thematic break taken for none, an ordered marker past 1 carrying a paragraph on - and still declines a line carried on from the margin by name; `list entries, ...` cases in `CONTINUED_STATEMENTS` pin each form.
