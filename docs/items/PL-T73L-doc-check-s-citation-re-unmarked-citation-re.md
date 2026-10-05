---
id: PL-T73L
title: doc_check's CITATION_RE, UNMARKED_CITATION_RE, QUOTED_SOURCE_RE and ITEM_SECTION_RE quote across a blank line as POSSESSIVE_RE did before PL-BYJ5, so two halves a paragraph break separates are held as one quotation; latent
status: untriaged
feature: one-answer
touches: tools/doc_check.py, tests/unit, docs/items/PL-BYJ5-possessive-section-check-s-possessive-re-quotes.md
added: 2026-10-05
---

**Problem.** doc_check's CITATION_RE, UNMARKED_CITATION_RE, QUOTED_SOURCE_RE and ITEM_SECTION_RE quote across a blank line as POSSESSIVE_RE did before PL-BYJ5, so two halves a paragraph break separates are held as one quotation; latent

**Found 2026-10-05 by `PL-R417`'s link 11 (`#1371`)**, closing `PL-BYJ5`, which bounded `possessive_section_check.POSSESSIVE_RE`'s quotation to the paragraph it opens in. Four patterns in `tools/doc_check.py` still read a quotation as `[^"]` under `re.DOTALL`, so each runs past a blank line, in a blockquote or out of one: `CITATION_RE` and `UNMARKED_CITATION_RE`, the section citations `check_citations` holds; `QUOTED_SOURCE_RE`, a document named and then quoted, which `check_quoted_sources` holds by containment; and `ITEM_SECTION_RE`, an item's brief cited by section. Each takes the two halves of a quotation a paragraph break separates for one, which `_normalized` then joins.

**Why `PL-BYJ5`'s fix does not carry over as it stands.** The possessive check reports only a quotation naming a heading, so bounding its quotation can only remove a report. These four are hard checks. Bounded the same way, a quotation mark that opens a citation and that no paragraph closes would match nothing, and the citation would go unread where today it is held, wrongly joined, as an error naming the joined text. So the bound needs a decline beside it, `UnreadStatement` or an error naming the form as the split HTML markers have, for a quotation a citation opens and its paragraph never closes.

**Latent.** Measured 2026-10-05 over every quoting source, the 38 documents, the live briefs and every docstring, none declined, under the project interpreter: bounded as `PL-BYJ5` bounds the possessive, `CITATION_RE`, `QUOTED_SOURCE_RE` and `ITEM_SECTION_RE` make the same 1,029, 508 and 16 matches they make today. `UNMARKED_CITATION_RE` was not measured.

**Not a recurrence of `PL-BYJ5`.** `docket new` matched this capture to it on its title and recorded a recurrence there, which link 11 withdrew: `PL-BYJ5` named `POSSESSIVE_RE` alone, and these are four other readers of the same fact.

**Generator check.** A member of `PL-R417`: where one statement ends. The quotation runs past the paragraph end that closes it, `PL-BYJ5`'s direction, which `PL-4ZDZ` and `PL-FP7J` read the same way. Recorded in its `root-cause-of:` by link 11.

**Done when.** The four patterns share one reading of a quotation's characters with `POSSESSIVE_RE`, which stops at a paragraph end, and a citation whose quotation its paragraph never closes is refused by name rather than read joined or passed over; `PL-R417`'s guard gains a case per pattern, a blank line ending the quotation and an unclosed one refused, each failing on today's reader.
