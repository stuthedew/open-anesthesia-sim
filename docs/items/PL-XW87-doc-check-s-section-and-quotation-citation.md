---
id: PL-XW87
title: doc_check's section and quotation citation patterns (CITATION_RE, UNMARKED_CITATION_RE, DIRECTION_RE, QUOTED_SOURCE_RE with ITEM_SECTION_RE) and possessive_section_check's POSSESSIVE_RE cross a soft break but stop at a blockquote's > marker, so a citation wrapped inside a blockquote is never checked; latent
status: untriaged
feature: one-answer
touches: tools/doc_check.py, tools/possessive_section_check.py, tests/unit, docs/items/PL-RX0W-a-possessive-quotation-of-an-item-brief-such-as.md
added: 2026-10-04
---

**Problem.** doc_check's section and quotation citation patterns (CITATION_RE, UNMARKED_CITATION_RE, DIRECTION_RE, QUOTED_SOURCE_RE with ITEM_SECTION_RE) and possessive_section_check's POSSESSIVE_RE cross a soft break but stop at a blockquote's > marker, so a citation wrapped inside a blockquote is never checked; latent

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`)**, a read-only pass over every reader outside the 2026-10-04 sweep, which reproduced it by importing the function; CommonMark readings checked with markdown-it-py 4.2.0. In a temporary root, `See §\n"No such heading"` and `` `docs/A.md` §\n"Words not in A" `` give one `check_citations` and one `check_quoted_sources` error; the same lines prefixed with `> ` give none, though CommonMark reads one paragraph, because the gap pattern stops at the marker. `ITEM_SECTION_RE`, `UNMARKED_CITATION_RE` and `POSSESSIVE_RE` were reproduced at the pattern only. Latent. Not a recurrence of `PL-RX0W`, which `bin/docket new` matched it to on shared words: that item is a possessive quotation of an item brief, which `QUOTED_SOURCE_RE` never reads, and this is a citation in a blockquote.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
