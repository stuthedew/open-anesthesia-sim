---
id: PL-MP5L
title: The rationale that a closed generator head still owes a misread: line, because a later capture is compared against a closed head's stated fact, is written out in Item.misread's comment, _check_misread's docstring and the docket README; PL-0TB3 cut the sibling rationale to the README and left this one out of scope
priority: P3
effort: S
status: ready
classes: docs
feature: generator-identification
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/checks.py
added: 2026-09-26
payoff: the closed-head rule for misread: is argued in one place, so the next change to it cannot leave three source copies giving the old reason
verify: ! grep -rqF --include=*.py 'an instance of a closed' subprojects/docket/src/docket
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

**Reproduced 2026-09-26** on `78b1a02b`: all three copies stand as quoted, and
there is a fourth. `misread_faults`'s docstring, in the same `model.py`, has a
paragraph opening "**Required on every sound head, closed ones included**" that
quotes the same triage landing and gives the same `PL-7TVT` example. `grep
-rnF --include=*.py 'an instance of a closed' subprojects/docket/src/docket`
finds exactly the three source copies: two in `model.py` and one in
`checks.py`.

**Why it matters.** Each source copy repeats the README's reasoning. When the
rule changes, a session has to find and edit every copy, and any copy it
misses keeps stating the old reason. `.claude/rules/apparatus-standard.md`
calls "prose restating" bloat, and `PL-0TB3` cut the sibling rationale for the
same reason.

**Done when.** The closed-head rationale is stated once, in the README
paragraph opening "`docket check` requires it on **every sound head, open or
closed**". `Item.misread`'s comment, `misread_faults`'s docstring and
`_check_misread`'s docstring each keep at most a clause saying closed heads are
held too and naming `PL-5MYR`. No source file under
`subprojects/docket/src/docket/` quotes the triage landing ("an instance of a
closed head's mechanism").

**Generator check.** A one-off, for the reason `PL-0TB3` gave for its sibling.
One session (`PL-5MYR`'s) wrote the rationale at each function it touched, and
no head's `misread:` states a fact this misreads. This is not a re-entry: it is
the remainder that `PL-0TB3` named and kept out of scope, filed when
`PL-0TB3` closed so the note would survive.
