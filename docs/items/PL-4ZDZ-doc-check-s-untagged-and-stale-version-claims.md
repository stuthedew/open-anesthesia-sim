---
id: PL-4ZDZ
title: doc_check's untagged and stale-version claims and its make-mention span reader stop at a block quote's > on a continuation line, and the version list runs on past a blank line, so a quoted claim or make command wrapped onto a second line reads short and a list a paragraph end closes reads long; latent
status: untriaged
feature: one-answer
touches: tools/doc_check.py, tests/unit
added: 2026-10-04
---

**Problem.** doc_check's untagged and stale-version claims and its make-mention span reader stop at a block quote's > on a continuation line, and the version list runs on past a blank line, so a quoted claim or make command wrapped onto a second line reads short and a list a paragraph end closes reads long; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

CommonMark § 5.1: a continuation line's `>` is not part of the paragraph; § 4.8. `PL-XW87` taught the citation patterns to cross it through `GAP`; these readers were not part of that fix.

- `UNTAGGED_CLAIM_RE` and `LIST_SEPARATOR_RE`: "> **Two versions are untagged**: v0.1.0 and" over "> v0.2.0." reads `{0.1.0}` and errors "the sentence says Two untagged, but names 1"; with the claim itself wrapped inside the quote it reads nothing; outside a quote both wraps read right.
- The same list run past a paragraph end: "**One version is untagged**: v0.1.0", a blank line, then "v0.2.0 was tagged a day late..." reads `{0.1.0, 0.2.0}` and errors "says One untagged, but names 2".
- `_make_mentions` applies `MAKE_MENTION_RE` to a span's content with the `>` left in: "> Run `make" over "> check` before committing." names no target, where list-item and paragraph wraps name `check`. `_named_tests` strips `SPAN_BREAK_RE` first; this reader does not.

Latent: `ROADMAP.md` has no block quote and its one exception sentence sits on one line ending with a period; the five wrapped `make` spans in the documents sit outside quotes.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
