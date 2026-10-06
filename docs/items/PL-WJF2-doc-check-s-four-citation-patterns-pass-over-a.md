---
id: PL-WJF2
title: doc_check's four citation patterns pass over a closed quotation longer than their bound - 160 after a section mark or see/under, 200 after a quoted source or an item's mark - without a word, so a long cited title is neither checked nor reported unread; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, tools/possessive_section_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed at triage 2026-10-05
added: 2026-10-05
closed: 2026-10-05
pr: 1383
payoff: a cited section title or quoted sentence of any length is checked against the tree, so a long one can no longer go stale behind a clean doc-check run, and no citation pattern can stall the check by backtracking
verify: grep -qF 'LONG_QUOTATIONS: dict' tests/unit/test_doc_check.py && grep -qF 'def test_a_quotation_never_closed_fails_its_match_without_backtracking' tests/unit/test_doc_check.py && ! grep -qE 'QUOTATION_CHAR\}\{\{[0-9]+,[0-9]+\}\}' tools/doc_check.py && ! grep -qF '{2,200}' tools/possessive_section_check.py
---

**Problem.** doc_check's four citation patterns pass over a closed quotation longer than their bound - 160 after a section mark or see/under, 200 after a quoted source or an item's mark - without a word, so a long cited title is neither checked nor reported unread; latent

**Found 2026-10-05 by `PL-T73L`** (`PL-R417`'s link 17, `#1382`), which
bounded the four patterns' quotations to the paragraph they open in and
refused one its paragraph never closes by name. The closed branch of each
kept the length bound it had: 160 in `CITATION_RE` and in
`UNMARKED_CITATION_RE`'s two branches, 200 in `QUOTED_SOURCE_RE` and
`ITEM_SECTION_RE`. A quotation its paragraph closes past the bound matches
neither branch - the closed one runs out, and `UNCLOSED_QUOTATION`'s
lookahead refuses a quotation that has its closing mark - so the citation is
passed over: neither compared nor reported unread. That is a partial reading
handed over as a complete one, which `.claude/rules/apparatus-standard.md`'s
floor refuses.

**Latent.** Measured 2026-10-05 on that branch, under the project
interpreter, over every quoting source with none declined, by lifting each
bound and counting the closed matches that appear: none in the documents
`check_citations` reads, and none in what `check_quoted_sources` reads. The
one in the tree is an `under` citation in `PL-6WYD`'s brief whose quotation
runs past 160, and `check_citations` does not read briefs.

**Why it matters.** All five readers - the four above and
`possessive_section_check.POSSESSIVE_RE`, which held the same 200 - answer
for every citation in what they read, and a clean run is taken as every
citation checked. A long title or a long quoted sentence is exactly the
citation a reader cannot check by eye, and it was the one skipped.

**Why the bound was there, as captured.** It stopped a runaway match inside
one paragraph: a stray mark after `see` in a long paragraph would otherwise be
read on to that paragraph's next mark and compared as a title nobody wrote.
So lifting it looked like trading a silent pass-over for a false error, and
the capture put the choice as one between refusing the over-long form by
name, an advisory, and a line in `Report.declined`.

**Decision, 2026-10-05: lift the bound and read the quotation possessively,
rather than report past it.** Taken by the session working the item, as a
choice with one clearly better answer, on three readings of the code and two
measurements.

- *The quotation is already fixed without the bound.* `QUOTATION_CHAR`
  excludes the closing mark and stops at a paragraph end, so a closed
  quotation is exactly the text up to its paragraph's next mark. The bound
  only decided whether that text was read.
- *The bound never prevented the runaway report.* A stray mark nearer its
  neighbour than 160 or 200 characters was compared as a title all along, and
  reported. The report a runaway earns is the same at any distance, and points
  at the line where the unbalanced mark is.
- *Refusing by length would refuse correct prose.* Containment checks a
  quoted sentence of any length exactly, so a 250-character sentence quoted
  verbatim would be refused for nothing, and the remedy on offer, eliding it,
  moves it to the form `check_quoted_sources` skips outright.
- *Measured: lifting adds nothing the readers report today.* Over all 6,838
  quoting sources under the project interpreter, none declined, every match
  of the five patterns keeps its exact span; the one new match is the `under`
  citation in `PL-6WYD`'s brief, which `check_citations` does not read, and
  `make doc-check`'s output is byte-identical before and after.
- *Measured: the lazy repetition backtracks, bound or no bound.* It tries
  every split of a line's trailing spaces between `QUOTATION_CHAR`'s two
  halves before a match fails, three per hard break. A quotation never closed
  across twelve ten-character lines ending in a hard break took 259 ms under
  the old 160 bound, sixteen about 20 s; unbounded and lazy, sixteen lines of
  a longer opener took 42.8 s. Possessive, each takes microseconds, so the
  possessive form is what makes the lift safe, and it removes a hazard the
  bound already had.

**Not a recurrence of `PL-T73L`.** `docket new` matched this capture to it
on the paths they share and recorded a recurrence there, which this capture
withdrew: `PL-T73L` was the paragraph end a quotation ran past, and this is
the length bound inside one paragraph, which `PL-T73L` left as it was.

**Generator check.** Not a member of `PL-R417`: the quotation is read within
its paragraph as CommonMark reads it, and dropped for its length rather than
for where its statement ends.

**Done when.** Each of the four readers, and `POSSESSIVE_RE`, reads a closed
quotation of any length its paragraph closes, possessively, and compares it as
it compares a short one; a test per pattern gives a quotation past the old
bound and gets the comparison's answer, one gives a long title that a heading
holds and gets nothing, and a subprocess test fails any pattern that
backtracks on an unclosed quotation across thirty hard-broken lines.

**As built, 2026-10-05.** `CITATION_RE`, `UNMARKED_CITATION_RE`'s two
branches, `QUOTED_SOURCE_RE`, `ITEM_SECTION_RE` and `POSSESSIVE_RE` take
`QUOTATION_CHAR` with a possessive, unbounded repetition, and `CITATION_RE`'s
comment carries the reasons. `LONG_QUOTATIONS` in
`tests/unit/test_doc_check.py` holds the seven cases, six of which fail on the
old patterns, and
`test_a_quotation_never_closed_fails_its_match_without_backtracking` timed out
at 20 s on the old ones.
