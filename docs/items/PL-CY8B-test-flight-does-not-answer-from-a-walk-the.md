---
id: PL-CY8B
title: test_flight_does_not_answer_from_a_walk_the_clone_truncated asserts PL-M01 is absent, but PL-M01 is not an id ID_PATTERN matches, so that assertion cannot fail
priority: P3
effort: S
status: ready
classes: defect
feature: parallel-sessions
touches: subprojects/docket/tests/test_cli.py
added: 2026-09-13
verify: ! grep -q 'PL-M0{number}' subprojects/docket/tests/test_cli.py && uv run pytest subprojects/docket/tests/test_cli.py
---

**Problem.** test_flight_does_not_answer_from_a_walk_the_clone_truncated asserts PL-M01 is absent, but PL-M01 is not an id ID_PATTERN matches, so that assertion cannot fail

**Found while building `PL-W1LN`'s reproduction, 2026-09-13.** `_shallow_pair`
writes its default-branch commits with subjects `PL-M01 Main work 1` through
`PL-M06`. `store.ID_PATTERN` matches `PL-` followed by either **three digits** or
**four** characters from the consonant-safe alphabet, and `M01` is neither - three
characters, one of them a letter. So those subjects carry no id any reader
credits, and the test's most specific assertion,

```python
assert "PL-M01" not in out
```

cannot fail: the string was never a candidate for the output whether the guard
fired or not. The sibling fixture this item's finder built had to spell its ids
`PL-M1QJ`, `PL-M3NW` and so on precisely because the `PL-M0n` form is invisible,
which is how the gap surfaced.

**Why it matters.** A test assertion that cannot fail is worse than an absent one,
because it reads as coverage. This one names the exact claim a reader would most want
covered - that the default branch's *own* ids are kept out of the in-flight line -
and it has never been able to check it. `CLAUDE.md`'s objection to a check that
passes while the guarantee it stands for is void applies to a test as squarely as to
a linter.

**What is and is not still proved.** The test's other assertions are sound and
carry the finding it was written for: `"No branch carries an item id" in out` and
`"1 ref cannot be compared with origin/main" in out` both fail if the guard stops
working, because `PL-K7QX` - a valid id - is on the branch. So the guard is
genuinely covered; what is not covered is the narrower claim that the *default
branch's own* ids are suppressed, which is the half the `PL-M01` line was meant to
make and the half `PL-W1LN`'s new test makes with valid ids.

**Approach.** Respell `_shallow_pair`'s six subjects to the id grammar, as the
uneven-horizon fixture beside it already does, and keep the absence assertion -
it becomes load-bearing rather than vacuous. Check the other negative id
assertions in the suite for the same shape while there: any `not in out` against a
malformed id is the same defect.

**Done when.** `_shallow_pair`'s commits carry ids `ID_PATTERN` matches, the
absence assertion in `test_flight_does_not_answer_from_a_walk_the_clone_truncated`
fails if the guard is removed, and no other test in the suite asserts the absence
of a string that could never have appeared.

**Blocked.** 2026-09-26, on the slam-dunk run's `claude/pl-batch-08-yc0dvu`,
against `origin/main` at `d49d392c`. The respelling is doable inside `touches`,
but the second clause of **Done when** is not true of the tree, so the item is
not the slam dunk it was taken as. What was run and what came back:

1. `_shallow_pair` writes ten default-branch commits, not six (`PL-M01` to
   `PL-M06` before the fork and `PL-M07` to `PL-M010` after it). All ten were
   respelled to ids `ID_PATTERN` matches (`PL-M1BC` to `PL-MB0Y`), with the
   absence assertion kept on the first.
2. The walk guard was then removed (`claims._history`'s `if not
   parents.strip(): return None` replaced by `pass`) and
   `test_flight_does_not_answer_from_a_walk_the_clone_truncated` run. It failed
   only at `"1 ref cannot be compared with origin/main" in out`. The absence
   assertion passed, and the output began "No branch holds an item".

The reason is `PL-N162`: `flight` answers from `claims.holdings`, where a
commit subject's id is attribution and holds nothing. So `main`'s own commits
cannot reach the report whether or not the guard fires, and no respelling makes
the absence assertion the one that catches a missing guard. The guard itself is
still covered, by the `1 ref cannot be compared` assertion. The respelling was
reverted, and nothing else here changed.

**Decision needed: respell for the grammar alone, with the guard clause of
Done when dropped, or drop the item?**

**Recommendation:** respell, and replace "the absence assertion ... fails if
the guard is removed" with "the absence assertion names a string a reader could
credit". That removes the fixture's two `not-an-id` markers and makes the
assertion a real check that `main`'s own ids stay out of the report, at no cost
beyond this item's `S`. Dropping it would leave a fixture that
`tools/fixture_id_check.py` has to be told is not spelling ids.
