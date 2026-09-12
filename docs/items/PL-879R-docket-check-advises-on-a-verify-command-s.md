---
id: PL-879R
title: docket check advises on a verify: command's outcome but never its shape, so a grep for an id, or for a file another item is known to create, is only reported once it has already started passing
priority: P2
effort: S
status: needs-decision
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-10
---

**Problem.** docket check advises on a verify: command's outcome but never its shape, so a grep for an id, or for a file another item is known to create, is only reported once it has already started passing

**Raised by `PL-X7VY`** (main is red: `PL-XH1D`'s `verify:` passes because
`PL-78JQ` created the `CONTRIBUTING.md` it tests for), whose brief names it as
worth considering once that item is fixed and not required by it. Filed rather
than built, because it is a judgment about a command's wording and the line
between the decidable half and the judgment half has not been drawn yet.

**The evidence that it is a class.** Two commands broke the same rule on the
same day - a `verify:` must name something *only this item's work* creates.
`PL-XH1D`'s discriminating half was `test -f CONTRIBUTING.md`, satisfied when
`PL-78JQ` created the file. `PL-X9T3`'s was `grep -q 'PL-X9T3'
docs/WORKING_NOTES.md`, satisfied when `PL-55DH` wrote a section whose heading
cites that id. Neither command ever discriminated; another item's work merely
made that visible, and in both cases the outcome check reported it only after
it had started passing - on `main`, where no pull request shows it.

**What a shape check could decide, and what it could not.** Decidable from the
text alone: a discriminating half that is a bare `grep` for an item id, since
any note may legitimately cite one; a `grep` for a path the item's own
`touches` does not name; a `test -f` on a file some other open item's `touches`
declares. Not decidable: whether the phrase a `grep` names is one only this
item's work can produce, which is the judgment `CLAUDE.md` says not to script -
a tool that guessed at it would be worse than none, because its output would
look authoritative.

**Weigh it against the check that already works.** `_check_landed` in
`subprojects/docket/src/docket/checks.py` catches both instances above as an
error, late but reliably, and `CLAUDE.md`'s "A check earns its place every run,
or it is retired" is the bar a new advisory has to clear. So the question this
item answers is not "would a shape check find these" - it would - but whether
the subset it can decide without guessing is large enough to be worth an
advisory that fires on every run.

**Why it matters.** The outcome check reports the defect at the latest possible
moment: after the item was written, after it was pushed, and after some
unrelated item's work has satisfied the command. A shape check would report it
at the moment it is written, which is the only moment its author is still
holding the reasoning. Nothing is failing today - this is a question about
moving an existing finding earlier, not about a gap in coverage.

**Done when.** Either the decidable subset is implemented in `checks.py` with
tests, or this item is `dropped` with the reason recorded - that the subset is
too small, or too noisy, to earn a check that fires on every run.

**Decision needed.** Whether the decidable subset - a discriminating half that
is a bare `grep` for an item id, a `grep` for a path the item's own `touches`
does not name, or a `test -f` on a file another open item's `touches` declares -
is large enough to be worth an advisory that fires on every run. `_check_landed`
already catches both known instances as an error, reliably but late; this would
move the finding to the moment the command is written, at the cost of a check
that must clear `CLAUDE.md`'s "a check earns its place every run, or it is
retired".

Re-checked 2026-09-12: `checks.py` carries shape checks for re-entrancy
(`reenters_verify`), for reading the project check's own output
(`reads_check_output`), for multi-line commands and for a `verify:` with no
`touches` - so the shape half is an established pattern here rather than a new
kind of check. What none of them inspects is whether the command is
*tautological*, which is this item's subset.
