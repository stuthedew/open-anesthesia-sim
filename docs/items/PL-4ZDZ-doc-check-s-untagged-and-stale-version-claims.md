---
id: PL-4ZDZ
title: doc_check's untagged and stale-version claims and its make-mention span reader stop at a block quote's > on a continuation line, and the version list runs on past a blank line, so a quoted claim or make command wrapped onto a second line reads short and a list a paragraph end closes reads long; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: a tags claim or a make command wrapped inside a block quote is read whole, and a version list ends with its paragraph
verify: grep -qF '"untagged claims, ' tests/unit/test_doc_check.py && grep -qF '"make mentions, a code span wrapped inside a block quote' tests/unit/test_doc_check.py
---

**Problem.** doc_check's untagged and stale-version claims and its make-mention span reader stop at a block quote's > on a continuation line, and the version list runs on past a blank line, so a quoted claim or make command wrapped onto a second line reads short and a list a paragraph end closes reads long; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

CommonMark § 5.1: a continuation line's `>` is not part of the paragraph; § 4.8. `PL-XW87` taught the citation patterns to cross it through `GAP`; these readers were not part of that fix.

- `UNTAGGED_CLAIM_RE` and `LIST_SEPARATOR_RE`: "> **Two versions are untagged**: v0.1.0 and" over "> v0.2.0." reads `{0.1.0}` and errors "the sentence says Two untagged, but names 1"; with the claim itself wrapped inside the quote it reads nothing; outside a quote both wraps read right.
- The same list run past a paragraph end: "**One version is untagged**: v0.1.0", a blank line, then "v0.2.0 was tagged a day late..." reads `{0.1.0, 0.2.0}` and errors "says One untagged, but names 2".
- `_make_mentions` applies `MAKE_MENTION_RE` to a span's content with the `>` left in: "> Run `make" over "> check` before committing." names no target, where list-item and paragraph wraps name `check`. `_named_tests` strips `SPAN_BREAK_RE` first; this reader does not.

Latent: `ROADMAP.md` has no block quote and its one exception sentence sits on one line ending with a period; the five wrapped `make` spans in the documents sit outside quotes.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `09cdc761`, `UNTAGGED_CLAIM_RE` finds no claim in "> **Two versions are" over "> untagged**: v0.1.0 and" over "> v0.2.0.", and `_make_mentions` names no target in "> Run `make" over "> check` before committing.", where both read right outside a quote.

**Why it matters.** `check_tags` holds an untagged or stale-version claim's count to the versions it names, and the make-mention reader holds each `make` command a document gives to the Makefile, so a claim or a command wrapped inside a block quote reads short and passes, and a version list read past its paragraph's end fails a correct claim.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** The untagged and stale-version claims read their words and their version list across a soft break inside a block quote, the list ends where its statement does, and `_make_mentions` reads a code span's command with the quote's markers removed, as `_named_tests` does; `untagged claims, ...` and `make mentions, ...` cases in `CONTINUED_STATEMENTS` pin it.
