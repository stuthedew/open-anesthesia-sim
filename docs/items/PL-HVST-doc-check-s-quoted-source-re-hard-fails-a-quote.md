---
id: PL-HVST
title: doc_check's QUOTED_SOURCE_RE hard-fails a quote set beside a document name by a possessive, colon, comma, parenthesis or no connective, so proposed or since-deleted wording quoted beside CLAUDE.md fails make check; 422 of 465 matches already use the explicit section mark
priority: P3
effort: S
status: done
classes: defect
feature: exact-gates
milestone: v0.5.12
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-25
closed: 2026-09-26
pr: 1086
payoff: a brief or document can quote wording proposed for, or since deleted from, a named document without make check refusing it as a misquotation
verify: grep -q 'def test_a_proposal_quoted_beside_a_document_is_not_an_error' tests/unit/test_doc_check.py
---

**Problem.** doc_check's QUOTED_SOURCE_RE hard-fails a quote set beside a document name by a possessive, colon, comma, parenthesis or no connective, so proposed or since-deleted wording quoted beside CLAUDE.md fails make check; 422 of 465 matches already use the explicit section mark

Reproduced: an item quoting proposed wording as `` `CLAUDE.md`: "Hand off at 120,000..." `` and one quoting since-deleted wording both fail. Both false refusals came through the non-`§` connectives; the 43 matches using them (possessive 16, none 10, comma 8, colon 4, under 3, paren 2) are the one-time rewrite cost of going `§`-only.

Re-confirmed 2026-09-25 against 46954a81 in a scratch root: a document quoting a proposed sentence after a colon connective fails `check_quoted_sources` with an error that the quotation is not in the named file. In the documents alone 13 non-`§` matches remain, 5 of them in `ROADMAP.md` and 4 in `docs/ARCHITECTURE.md`; the rest of the 43 sit in live briefs.

**Before building, count one thing.** The possessive is also how this project quotes a sentence rather than cites a section - `tools/possessive_section_check.py` says so in its docstring - and its 16 matches are containment-checked for drift today, which going `§`-only gives up. If neither reproduced refusal came through the possessive, keeping it hard and demoting the colon, comma, parenthesis, `under` and bare forms removes both refusals and keeps that drift check.

**Generator check.** PL-GPJ7's fact: the gate reads a document name beside a quotation as a claim that the document holds those words, recognised by whatever connective sits between them, and a quoted proposal makes no such claim.

**Why it matters.** A hard gate refusing correct prose teaches sessions to reword rather than to read, which `CLAUDE.md` retires a check for.

**Done when.** Only `§` forms are hard errors; the other connectives are an advisory or not read; a test holds a quoted proposal through a clean run.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

**Built 2026-09-26, as step 2 of `PL-GPJ7`'s split.** The count came first, as asked: both reproduced refusals came through a colon and a comma and neither through the possessive, so the possessive stays hard beside `§` (`CLAIMING_CONNECTIVE_RE`), which is the head's Split rather than the Done-when's `§`-only. After a colon, comma, parenthesis, `under` or nothing, a quotation the file lacks is an advisory rather than an error, still read for drift, since containment cannot tell a proposal from a misquotation; a named document that does not exist takes the same severity. Counted on this tree over the documents, the live briefs and the docstrings: 423 `§` and 15 possessive quotations stay hard, and 28 move - 10 bare, 9 comma, 4 colon, 3 `under`, 2 parenthesis - every one contained today. `test_a_proposal_quoted_beside_a_document_is_not_an_error` holds all five through a clean run. The `under` and parenthesis tests now assert the advisory, which is the commissioned change to what they pinned; the other quoted-source tests keep their assertions, on the `§` form where a comma could no longer fail them.
