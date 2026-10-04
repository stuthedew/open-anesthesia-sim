---
id: PL-XW87
title: doc_check's section and quotation citation patterns (CITATION_RE, UNMARKED_CITATION_RE, DIRECTION_RE, QUOTED_SOURCE_RE with ITEM_SECTION_RE) and possessive_section_check's POSSESSIVE_RE cross a soft break but stop at a blockquote's > marker, so a citation wrapped inside a blockquote is never checked; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, tools/possessive_section_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-04
pr: 1352
payoff: a citation wrapped inside a blockquote is checked like any other, so a renamed section or a drifted quotation there no longer passes as resolved
verify: grep -qF '"citations, a section mark wrapped in a blockquote"' tests/unit/test_doc_check.py && grep -qF '"possessive citations, ' tests/unit/test_doc_check.py
---

**Problem.** doc_check's section and quotation citation patterns (CITATION_RE, UNMARKED_CITATION_RE, DIRECTION_RE, QUOTED_SOURCE_RE with ITEM_SECTION_RE) and possessive_section_check's POSSESSIVE_RE cross a soft break but stop at a blockquote's > marker, so a citation wrapped inside a blockquote is never checked; latent

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`)**, a read-only pass over every reader outside the 2026-10-04 sweep, which reproduced it by importing the function; CommonMark readings checked with markdown-it-py 4.2.0. In a temporary root, `See §\n"No such heading"` and `` `docs/A.md` §\n"Words not in A" `` give one `check_citations` and one `check_quoted_sources` error; the same lines prefixed with `> ` give none, though CommonMark reads one paragraph, because the gap pattern stops at the marker. `ITEM_SECTION_RE`, `UNMARKED_CITATION_RE` and `POSSESSIVE_RE` were reproduced at the pattern only. Latent. Not a recurrence of `PL-RX0W`, which `bin/docket new` matched it to on shared words: that item is a possessive quotation of an item brief, which `QUOTED_SOURCE_RE` never reads, and this is a citation in a blockquote.

**Reproduced 2026-10-04, at triage.** `See §\n"No such heading"` in a README draws `check_citations`' error, and the same lines inside a blockquote draw none; so too for `QUOTED_SOURCE_RE`, `ITEM_SECTION_RE`, `UNMARKED_CITATION_RE` and `POSSESSIVE_RE`.

**Why it matters.** A citation wrapped inside a blockquote is never checked, so a renamed section or a drifted quotation there passes the gate that exists to catch it, while the run says every citation resolved.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** Each pattern's gaps are `doc_check.GAP`, read past a blockquote's `>` as CommonMark reads a paragraph, pinned by `citations, ...`, `quoted sources, ...` and `possessive citations, ...` cases in `PL-R417`'s guard.

**Built 2026-10-04 (`#1352`).** Every gap in `CITATION_RE`, `UNMARKED_CITATION_RE`, `DIRECTION_RE`, `MARKED_RE`, `QUALIFIED_RE`, `QUOTED_SOURCE_RE`, `ITEM_SECTION_RE`, `CITATION_CONNECTIVE`, `CLAIMING_CONNECTIVE_RE` and `possessive_section_check.POSSESSIVE_RE` is a `GAP`, so a blank line or a block's opening now ends a citation as it ends the paragraph. A soft break is known by the line it opens onto, so `MARKED_RE` and `QUALIFIED_RE` search a window that takes the match's first character, and `DIRECTION_RE` matches at the quotation's end rather than in a 24-character slice. Over the documents, the queue and the docstrings the four citation patterns match the same 561, 80, 514 and 15 sites as before, and doc_check and the possessive check report the same. Seven guard cases, each failing on main's patterns.
