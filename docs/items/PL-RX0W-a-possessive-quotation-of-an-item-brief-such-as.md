---
id: PL-RX0W
title: A possessive quotation of an item brief, such as PL-CNJ1's "writes nothing" in PL-SSQW, is read by no check: QUOTED_SOURCE_RE reads only a .md document and PL-QYN4 holds only the section mark after an item id; of the eleven such quotations on 2026-09-26 the one that misses quotes across emphasis (the brief has writes **nothing**), so reading them needs doc_check's comparison to fold markup first
priority: P3
effort: S
status: done
classes: defect
touches: tools/doc_check.py, tests/unit/test_doc_check.py, subprojects/docket/tests/test_checks.py, docs/items/PL-TH35-define-the-common-view-contract-every-app-view.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
closed: 2026-10-19
pr: 1620
payoff: a quotation attributed to an item brief with a possessive is held to that brief, so a misquoted brief is caught as a misquoted document already is
verify: grep -q 'def test_a_possessive_quotation_of_an_item_brief_is_held_to_it' tests/unit/test_doc_check.py
recurrences: 2026-10-04 PL-XW87 withdrawn 2026-10-04 PL-XW87, 2026-10-04 PL-BYJ5 withdrawn 2026-10-04 PL-R417, 2026-10-06 PL-CZ28 withdrawn 2026-10-06 PL-R417
---

**Problem.** A possessive quotation of an item brief, such as PL-CNJ1's "writes nothing" in PL-SSQW, is read by no check: QUOTED_SOURCE_RE reads only a .md document and PL-QYN4 holds only the section mark after an item id; of the eleven such quotations on 2026-09-26 the one that misses quotes across emphasis (the brief has writes **nothing**), so reading them needs doc_check's comparison to fold markup first

Found 2026-09-26 working `PL-QYN4`, which holds a section mark after a code-spanned item id to that item's brief by containment and was scoped to the mark alone. Counted that day over what `check_quoted_sources` reads (the documents, the live briefs and the docstrings), the possessive after an item id stood eleven times, ten of them contained in the cited brief. The eleventh is the example in the title: `docs/items/PL-CNJ1-the-qt-spike-writes-screenshots-to-a-caller.md` writes the phrase with its last word in bold, and `_comparable` folds case, dashes and quote style but not emphasis, so a faithful quotation would be refused. The same limit holds after a document today, and nothing trips it only because no such quotation stands in the tree. Not taken into `PL-QYN4`, because it is a second connective and needs the comparison changed first; the other connectives after an item id are not citations of the brief at all (`under "X"` names the heading an item is listed under elsewhere), so the possessive is the only one left.

**Reproduced 2026-09-26** on `origin/main` (`6efd8c41`): `QUOTED_SOURCE_RE`
finds no quotation in `` `PL-CNJ1`'s "writes everything to disk" `` and finds
the same words after `` `docs/MODEL.md`'s ``, and `_comparable("writes
nothing")` is not contained in `_comparable("the spike writes **nothing**
there")`.

**Why it matters.** A possessive attributes the words to the brief as it does
to a document, where the check already holds it, so after an item id a
misquotation stands unread. None stands today: ten of the eleven such
quotations are contained, and the eleventh is faithful across emphasis.

**Done when.** A possessive quotation after a code-spanned item id is held to
that item's brief as one after a document is, with emphasis folded in the
comparison, pinned in `tests/unit/test_doc_check.py`, and all eleven standing
quotations pass.

**Generator check.** One-off: the possessive is what `PL-QYN4` scoped out on
purpose, not a sibling its fix should have covered, and no head's `misread:`
states which quotations `check_quoted_sources` reads.

**Done 2026-10-19.** `ITEM_SECTION_RE` now takes either claiming connective
after a code-spanned item id, the section mark or the possessive, from the one
`CLAIMING_CONNECTIVE` pattern that `CLAIMING_CONNECTIVE_RE` compiles. A new
`_without_emphasis` removes the delimiters that CommonMark pairs, as
`docket.markdown.emphasis` pairs them, from each statement of the cited file
and from the quotation. So a faithful quotation of `writes **nothing**` passes,
and a `*` that pairs with nothing stays. This applies after a document too.
Two possessive quotations written since 2026-09-26 then failed, because each
paraphrased its brief in quotation marks. They were repaired in place: the
`PL-TH35` brief now names the run-not-present state of `PL-7Z84` without
quotation marks, and a docstring in `subprojects/docket/tests/test_checks.py`
now says its sentence is adapted from `PL-JNWS`. Regression: `uv run pytest -q
tests/unit/test_doc_check.py -k possessive_quotation_of_an_item_brief` against
the code before the fix fails with "assert False" on the misquoted brief.
