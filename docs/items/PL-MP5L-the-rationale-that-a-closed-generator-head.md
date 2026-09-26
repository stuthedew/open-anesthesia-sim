---
id: PL-MP5L
title: The rationale that a closed generator head still owes a misread: line, because a later capture is compared against a closed head's stated fact, is written out in Item.misread's comment, _check_misread's docstring and the docket README; PL-0TB3 cut the sibling rationale to the README and left this one out of scope
status: untriaged
feature: generator-identification
added: 2026-09-26
---

**Problem.** The rationale that a closed generator head still owes a misread: line, because a later capture is compared against a closed head's stated fact, is written out in Item.misread's comment, _check_misread's docstring and the docket README; PL-0TB3 cut the sibling rationale to the README and left this one out of scope

Found 2026-09-26 while closing `PL-0TB3`, whose brief noted it ("The closed-head
paragraph written three times by the same commit is the same shape") and kept it
out of scope; that note closes with `PL-0TB3`, so it is filed here. The three
copies: the paragraph opening "**Required on a closed head too, unlike
`generator`.**" in `Item.misread`'s comment (`subprojects/docket/src/docket/model.py`),
the paragraph opening "Closed heads are held too" in `_check_misread`'s
docstring (`subprojects/docket/src/docket/checks.py`), and the paragraph opening
"`docket check` requires it on **every sound head, open or closed**" in
`subprojects/docket/README.md` § "What the front matter is, exactly". The README
copy is the fullest. `PL-0TB3`'s route would apply: keep the README's, and cut
each source copy to a clause naming `PL-5MYR`.
