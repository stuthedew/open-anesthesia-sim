---
id: PL-7TYC
title: docket verify's no existing assertion removed check greps for the substring assert, so removing any of the 90 non-test source lines containing that word REJECTs a correct close-out
status: untriaged
feature: verify-close-out
added: 2026-09-17
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
