---
id: PL-T73L
title: doc_check's CITATION_RE, UNMARKED_CITATION_RE, QUOTED_SOURCE_RE and ITEM_SECTION_RE quote across a blank line as POSSESSIVE_RE did before PL-BYJ5, so two halves a paragraph break separates are held as one quotation; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit, docs/items/PL-BYJ5-possessive-section-check-s-possessive-re-quotes.md, tools/possessive_section_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-05 triage pass
added: 2026-10-05
closed: 2026-10-05
pr: 1382
payoff: a citation's quotation ends at its paragraph, so two unrelated quoted halves are no longer joined and reported as one citation of text no reader sees
verify: grep -qF 'section citations, a blank line ends the quotation' tests/unit/test_doc_check.py && grep -qF 'unmarked citations, a blank line ends the quotation' tests/unit/test_doc_check.py && grep -qF 'quoted sources, a blank line ends the quotation' tests/unit/test_doc_check.py && grep -qF 'item sections, a blank line ends the quotation' tests/unit/test_doc_check.py
recurrences: 2026-10-05 PL-WJF2 withdrawn 2026-10-05 PL-WJF2
---

**Problem.** doc_check's CITATION_RE, UNMARKED_CITATION_RE, QUOTED_SOURCE_RE and ITEM_SECTION_RE quote across a blank line as POSSESSIVE_RE did before PL-BYJ5, so two halves a paragraph break separates are held as one quotation; latent

**Found 2026-10-05 by `PL-R417`'s link 11 (`#1371`)**, closing `PL-BYJ5`, which bounded `possessive_section_check.POSSESSIVE_RE`'s quotation to the paragraph it opens in. Four patterns in `tools/doc_check.py` still read a quotation as `[^"]` under `re.DOTALL`, so each runs past a blank line, in a blockquote or out of one: `CITATION_RE` and `UNMARKED_CITATION_RE`, the section citations `check_citations` holds; `QUOTED_SOURCE_RE`, a document named and then quoted, which `check_quoted_sources` holds by containment; and `ITEM_SECTION_RE`, an item's brief cited by section. Each takes the two halves of a quotation a paragraph break separates for one, which `_normalized` then joins.

**Why `PL-BYJ5`'s fix does not carry over as it stands.** The possessive check reports only a quotation naming a heading, so bounding its quotation can only remove a report. These four are hard checks. Bounded the same way, a quotation mark that opens a citation and that no paragraph closes would match nothing, and the citation would go unread where today it is held, wrongly joined, as an error naming the joined text. So the bound needs a decline beside it, `UnreadStatement` or an error naming the form as the split HTML markers have, for a quotation a citation opens and its paragraph never closes.

**Latent.** Measured 2026-10-05 over every quoting source, the 38 documents, the live briefs and every docstring, none declined, under the project interpreter: bounded as `PL-BYJ5` bounds the possessive, `CITATION_RE`, `QUOTED_SOURCE_RE` and `ITEM_SECTION_RE` make the same 1,029, 508 and 16 matches they make today. `UNMARKED_CITATION_RE` was not measured.

**Reproduced 2026-10-05** at triage, on `main` at `b67dace8` under python3 3.11.15. Each pattern was searched over a quotation whose two halves a blank line separates, and each matched the whole of it, the blank line inside the captured group. The texts, fenced because this brief is itself read by the four patterns, and quoting them in prose made `doc_check` report two of them against this file:

```text
CITATION_RE           § "Known\n\nlimitations"              -> 'Known\n\nlimitations'
UNMARKED_CITATION_RE  see "Known\n\nlimitations"            -> 'Known\n\nlimitations'
QUOTED_SOURCE_RE      `docs/MODEL.md`, "the clock\n\nruns"  -> 'the clock\n\nruns'
ITEM_SECTION_RE       `PL-0Y7J` § "Done\n\nwhen"            -> 'Done\n\nwhen'
```

**Why it matters.** All four feed hard checks. A quotation mark that opens a citation and is closed only in a later paragraph - a stray mark, or one the next paragraph's quotation closes - is held as one citation of the joined text, so `make check` fails a sound document naming a section or a passage that no reader of it sees, and the edit that quiets it is guesswork. And `doc_check` and `possessive_section_check` now disagree about where one quotation in one document ends.

**Not a recurrence of `PL-BYJ5`.** `docket new` matched this capture to it on its title and recorded a recurrence there, which link 11 withdrew: `PL-BYJ5` named `POSSESSIVE_RE` alone, and these are four other readers of the same fact.

**Generator check.** A member of `PL-R417`: where one statement ends. The quotation runs past the paragraph end that closes it, `PL-BYJ5`'s direction, which `PL-4ZDZ` and `PL-FP7J` read the same way. Recorded in its `root-cause-of:` by link 11.

**Done when.** The four patterns share one reading of a quotation's characters with `POSSESSIVE_RE`, which stops at a paragraph end, and a citation whose quotation its paragraph never closes is refused by name rather than read joined or passed over; `PL-R417`'s guard gains a case per pattern, a blank line ending the quotation and an unclosed one refused, each failing on today's reader.

**As built, 2026-10-05.** `doc_check.QUOTATION_CHAR` is the one reading of a
quotation's characters: any character but the closing mark or a line end, or
a soft break, whose `CONTINUED_LINE` refuses a blank line and a block start.
So a quotation ends with the paragraph it opens in, in a blockquote or out of
one. `POSSESSIVE_RE` takes it in place of its own copy, and the four patterns
in place of a negated mark class under `re.DOTALL`, which went with it, since
none of them used a dot outside a class. Each of the four gained a second
branch, `UNCLOSED_QUOTATION`, which matches the rest of a paragraph its
quotation never closes, and each reader refuses that match by name in
`_unclosed`'s one wording: what opened the quotation, that its paragraph
never closes it, what was therefore not read, and to close it before the
paragraph ends. The severity is the closed form's: an error after a section
mark, an advisory after an unmarked citation's opening word, an error after
a document whose connective claims the words (the mark or the possessive)
and an advisory after one that does not, and an error after an item's mark.
The directed form is known only by the direction after its closing mark, so
an unclosed quotation is none of it and nothing is refused there.
Measured on `main` at `83d2b7f6` under the project interpreter, over every
quoting source with none declined: main's patterns and these make the same
matches with the same captures, 1,029 section citations (567 in the
documents), 126 unmarked (80), 509 quoted sources, 15 item sections and 14
possessives, and none takes the unclosed branch. `PL-R417`'s guard gained
ten cases under the names this item's `verify:` gives and beside them: a
blank line ending each pattern's quotation, the directed form's included,
and an unclosed one refused for each, the advisory after a comma included.
Each fails with main's `doc_check.py` and passes here.

**Left as it was, and filed.** A closed quotation longer than its pattern's
bound, 160 for a section citation and 200 for a quoted source, still matches
neither branch and is passed over, as on main. With the bound lifted, none
appears in what either check reads today; `PL-WJF2` holds it.
