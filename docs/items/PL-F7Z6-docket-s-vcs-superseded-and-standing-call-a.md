---
id: PL-F7Z6
title: docket's vcs._superseded and _standing call a change that only removes lines removals-only, so a ref that cuts a line out of a continued paragraph or a bracketed list reads as superseded or behind though it holds a statement the base lacks; latent
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests
added: 2026-10-04
---

**Problem.** docket's vcs._superseded and _standing call a change that only removes lines removals-only, so a ref that cuts a line out of a continued paragraph or a bracketed list reads as superseded or behind though it holds a statement the base lacks; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

The compared file's own format decides what a statement is: a CommonMark paragraph continues across lines (§ 6.7), and a Python bracket joins its lines (Language Reference § 2.1.6). Both docstrings state the line test as their rule ("deletes lines and adds none, so the base holds everything the ref holds and more").

- `_standing`: base "**Decision.** Run the full suite", "before every commit,", "except a commit touching only docs/items/."; a ref that drops the middle line reads `behind`, though it now holds a different rule the base does not.
- `_superseded`: a ref dropping that middle line, or `"b",` from `ALLOWED = (` / `"a",` / `"b",` / `)`, reads both paths as superseded.

Callers: `stranded`, `orphaned`, `landed_whole` (which feeds the RESTART or MERGE call) and `claims._editing`. **The fix is to decline, not to compare statements:** comparing statement sets says `ahead` wrongly for nine live copies (`PL-YBFB` on eight refs, `PL-JW9J` on one) where the base inserted lines into an existing paragraph, and content alone cannot tell a ref that cut a line from a base that extended the statement. The readers' own cost model settles the direction - "a path wrongly called superseded would hide work nothing merged" - so where the line test says removals-only but the ref holds a statement the base lacks, the answer is outstanding. Latent: of 236 removals-only copies on today's refs, none holds a statement the base lacks, and none of the nine reaches `_standing`.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
