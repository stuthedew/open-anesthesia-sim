---
id: PL-7TYC
title: docket verify's no existing assertion removed check greps for the substring assert, so removing any of the 90 non-test source lines containing that word REJECTs a correct close-out
priority: P2
effort: S
status: done
classes: defect, infra
feature: verify-close-out
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, subprojects/docket/README.md
added: 2026-09-17
closed: 2026-09-17
pr: 660
verify: uv run pytest subprojects/docket/tests/test_verify.py && grep -q 'def test_the_matcher_itself_is_not_an_assertion' subprojects/docket/tests/test_verify.py
---

**Problem.** docket verify's no existing assertion removed check greps for the substring assert, so removing any of the 90 non-test source lines containing that word REJECTs a correct close-out

**Found 2026-09-17** on `PL-K82G`'s own close-out, which is the sharpest place
it could have surfaced: the item that gave the assertion check its first passing
route was refused by the same check, for a different reason, on the commit that
built the route.

**The line.** `bin/docket verify --self PL-K82G` printed

```text
FAIL  no existing assertion removed - 1 line(s)
        dropped = [line.strip() for line in removed if "assert" in line]
```

That is `verify.py`'s own matcher, which `PL-K82G` replaced. It is not an
assertion. It contains the word because it is the code that looks for
assertions.

**A third over-report class, and `falsifies:` is the wrong remedy for it.**
`PL-VP40` folded out a line removed and restored; `PL-K82G` folded out a line
the item was commissioned to falsify. Both are about *assertions*. This one is
about lines that are not assertions at all - `"assert" in line` is a substring
grep with no test for statement shape, so a comment, a docstring, a string
literal, a variable name or a matcher all match. Declaring such a line
`falsifies:` would be false: nothing was falsified.

**Counted rather than guessed, because n=1 does not justify a change to an
absolute check.** 90 lines across 20 non-test files contain the word, against
5,574 in the test trees where the check is aimed. Twelve of the 20 are the
simulator's own: `core/uptake_system.py`, `core/parameters.py`,
`core/concentration.py`, and nine modules under `app/`. So this is not confined
to the apparatus - an ordinary `core/` item that removes one of those lines gets
a red integrity check on correct work, and `CLAUDE.md`'s standard for `src/`
means those are the close-outs that can least afford a gate nobody reads.

**Why it matters.** It is `CLAUDE.md`'s second compounding-friction test, on the
one check that is supposed to be unarguable: a refusal that fires on correct
work trains a reader to skim the block where a real weakening is printed. It is
the cost `PL-69JZ` named, `PL-7XTS` widened the blast radius of, and `PL-K82G`
and `PL-L4KX` removed two of three causes of.

**Not fixed in that session, deliberately.** `CLAUDE.md`'s fix-now door needs
the fix to want no new test, and this one owes a regression test by any reading.
It is also a real design question rather than a narrowing: what counts as an
assertion. A statement-shape test (`^\s*assert\b`, plus `pytest.raises`,
`assertEqual` and friends) is the obvious candidate and would have passed this
branch, but it gives up lines a reformatter has wrapped, and whether that
matters wants looking at rather than assuming.

**Done when.** A removed line that merely mentions `assert` no longer counts as
a removed assertion; a genuinely removed assertion still does, including the
shapes the current grep catches that a naive anchor would miss; and a test pins
both directions. The check keeps erring toward reporting where it cannot tell,
since that is the direction that is safe.

**Worked 2026-09-17.** `is_assertion_line` in
`subprojects/docket/src/docket/verify.py` replaces the substring grep with two
decidable tests: the file is one Python executes, and the line has the shape of
an assertion - `assert` opening a statement, or a call to a name beginning
`assert` (`assertEqual`, `assert_called_once_with`, `assert_allclose`).

**The open question, answered by counting rather than assumed.** The brief
asked whether anchoring gives up assertions a reformatter has wrapped. It does
not: `assert` is a keyword and opens its statement, so a wrapped assert still
carries it on the first line, which is the line a whole-statement deletion puts
in the diff. Where only a continuation line is removed the anchor sees nothing
- and neither did the substring grep, since a continuation carries no `assert`
- so this is not a loss against the behaviour being replaced.

**What the tightening suppresses, measured three ways with `ast` as the oracle**
rather than a reading of the lines, because a check that stops reporting fails
silently where the over-report announced itself:

- across 867 commits of history, 200 removed lines carrying the word stop being
  reported; **none** is an assertion;
- across the test trees, where the check is aimed, 271 of 5,574 lines stop being
  reported; **none** is an assertion - 229 prose, 37 comments, 5 definitions or
  imports;
- in non-test source, the 90 exposed lines the brief counted fall to 4. One of
  the 4 is a real `assert` in `subprojects/docket/src/docket/vcs.py` that is
  meant to be reported; the other three are docstring lines a reflow happened to
  start with the word, left on the page because the check still errs toward
  reporting where it cannot tell.

The larger half of that by count is the file test, not the line test: every
close-out edits its own item's `.md` and every release edits `ROADMAP.md`, so
the documentation tree is where the grep met a session most often. All 26
predicate-positive lines outside `.py` in the tree are prose; the only `assert`
in CI, shell or `Makefile` is a comment.

**Both directions are pinned** in `subprojects/docket/tests/test_verify.py`.
The four "not reported" tests fail against the old grep. Four of the seven
"still reported" shapes - `unittest`, `mock`, `numpy` and the `if cond: assert
x` one-liner - fail against the naive `^\s*assert` anchor, which is what keeps
a later tightening from quietly giving them up.

**Not widened to `pytest.raises`.** `with pytest.raises(ValueError):` is a real
assertion that carries no `assert` substring, so it was invisible to the old
grep and stays invisible to this one - 60 such lines were removed across the
history read here. That is a pre-existing hole rather than one this change
opens, and closing it would add back over-reports of exactly the kind removed
here whenever a `raises` block is restructured. Filed as its own item.
