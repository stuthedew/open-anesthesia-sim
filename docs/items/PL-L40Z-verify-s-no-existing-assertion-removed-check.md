---
id: PL-L40Z
title: verify's 'no existing assertion removed' check greps the substring 'assert' across every removed line including Markdown prose, so a documentation rewrite REJECTs for sentences that are not assertions - 6 of the last 7 release cuts removed such a line from ROADMAP.md alone
status: dropped
classes: defect, infra
feature: verify-close-out
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-17
closed: 2026-09-17
reason: Superseded by PL-7TYC, which merged as #660 at c5e9776 minutes before this item was picked up. Its is_assertion_line asks the same file question this item's Approach named - only a file Python executes can hold an assertion - so both halves of the Done when are already satisfied. Replaying the eight release cuts v0.4.20-v0.4.27 through the current predicate: the substring grep flags 23 removed lines across six of the eight, every one of them ROADMAP.md prose and five of them the v0.4.27 case this item was found on; the current predicate flags none of the 23. test_prose_removed_from_a_document_is_never_an_assertion and test_a_genuinely_removed_assertion_is_still_reported pin both directions. Kept rather than deleted so the measurement is not run a third time. The one finding PL-7TYC does not carry - that falsifies: is structurally unreachable for an item filed and closed on one branch, not merely awkward when discovered mid-work - is appended to PL-TKFD, where that decision is made.
not-delegable: Nothing to do - the fix merged on main before this item was started, and the regression tests it asks for came with it.
---

**Problem.** verify's 'no existing assertion removed' check greps the substring 'assert' across every removed line including Markdown prose, so a documentation rewrite REJECTs for sentences that are not assertions - 6 of the last 7 release cuts removed such a line from ROADMAP.md alone

**Found 2026-09-17** on `PL-TM9J`'s own close-out - the v0.4.27 cut - where
`bin/docket verify --self PL-TM9J` returned `REJECT` on
`no existing assertion removed - 5 line(s)` with every one of the five a line of
`ROADMAP.md` prose.

**Where.** `subprojects/docket/src/docket/verify.py:886`:

```python
removed_assertions = [line.strip() for line in removed if "assert" in line]
```

`removed` is the net removed lines of the whole diff, with no file filter and no
shape test. Any removed line containing the substring `assert` is an assertion,
including a Markdown sentence that merely uses the word - "tests assert on the
real interface rather than on a stand-in", "what a branch comparison asserts",
"no capability boundary in what the interface asserts".

**This is not `PL-TKFD`, and the difference decides the fix.** `PL-TKFD` is
about a session that genuinely falsifies an assertion and has no route to
declare it, because `falsifies:` is read from the base. Here **nothing the check
exists to defend was removed at all**: a superseded sentence of release prose is
not an assertion weakened to let bad work through, not one moved or reworded
with its subject intact, and not one an item was commissioned to delete - which
are the three cases the code comment above the grep names as its subject. So the
fix is to stop matching prose, not to widen the declaration route.

**Measured, because `PL-TKFD` asks for instances to count before that route is
widened.** Across the last seven release-cut commits, counting only removed
`ROADMAP.md` lines containing `assert` in the cut commit itself:

| cut | assert-bearing removed lines |
| --- | --- |
| v0.4.20 | 1 |
| v0.4.21 | 2 |
| v0.4.22 | 6 |
| v0.4.23 | 4 |
| v0.4.24 | 4 |
| v0.4.25 | 2 |
| v0.4.26 | 0 |

Six of seven. The mechanism is structural rather than incidental: every cut
rewrites § "Current baseline", and a baseline section routinely says what the
release's tests assert - so the check fails on the one operation that *must*
rewrite that prose. v0.4.26 is the exception because its baseline section
happened to use "assert" only in lines that survived the rewrite.

**And a release-cut item can never use `falsifies:` anyway**, which is worth
separating from `PL-TKFD`'s mid-work case: the item is created and closed in one
session, so `origin/main` holds no copy of it and there is no base declaration to
read. `verify` says so itself - "a new item file - origin/main holds no copy to
differ from". Any item filed and closed on one branch is in the same position,
which is most housekeeping work.

**Why it matters.** It is the third instance of the family `PL-69JZ`, `PL-7XTS`,
`PL-K82G` and `PL-L4KX` were each written for: the audit the close-out procedure
requires, refusing work the same procedure prescribes. Each instance costs the
same thing, and it is not the wasted turn - it is that a session learns the
`REJECT` block is where correct work goes to be argued with, and reads past the
protected-path failure printed three lines above it. `CLAUDE.md` calls a check
that fires every run without changing a decision a defect in the check.

**Approach.** The cheapest sufficient fix is a file filter: run the assertion
grep over the diff's code files only, leaving `.md` out. That matches what the
check defends - a test assertion or a guard - and it is decidable from the path
rather than from the line. A shape test on the line (`assert `, `assertRaises`,
`self.assert`) is the alternative and is worse: it is a second guess at the same
question, and it would still match a prose line quoting a test. Whether a
removed assertion inside a fenced code block in a Markdown file should count is
the one real question, and the answer is probably no - the README's examples are
documentation of assertions, not assertions.

**Done when.** A release cut that rewrites § "Current baseline" reaches `ACCEPT`
with no declaration; a test in `subprojects/docket/tests/test_verify.py` pins a
removed Markdown prose line containing `assert` as not counted, and a removed
test assertion in a `.py` file as still counted.

**Dropped 2026-09-17: fixed by `PL-7TYC` before this item was started.** Everything
above describes the tree as it stood at `ae1ba2a`. `PL-7TYC` merged as `#660` at
`c5e9776`, replacing the substring grep with `is_assertion_line`, whose first
question is the file filter this item's **Approach** section recommended -
`ASSERTION_BEARING_SUFFIX = ".py"`, so a removed `.md` line is prose whatever its
shape. It answers the fenced-code-block question the same way this item did, and
for the same reason.

Measured rather than read, by replaying each release cut's own diff through the
current predicate:

| cut | flagged by the substring grep | flagged now |
| --- | --- | --- |
| v0.4.20 | 0 | 0 |
| v0.4.21 | 2 | 0 |
| v0.4.22 | 6 | 0 |
| v0.4.23 | 4 | 0 |
| v0.4.24 | 4 | 0 |
| v0.4.25 | 2 | 0 |
| v0.4.26 | 0 | 0 |
| v0.4.27 | 5 | 0 |

All 23 are `ROADMAP.md`, and the five on v0.4.27 are the ones this item was found
on. The left column differs from the table above for v0.4.20 because this replay
counts the squash commit on `origin/main` rather than the branch; the mechanism
claim is unaffected.

`PL-QJQL` carries the opposite direction - `pytest.raises` and `pytest.warns`,
which the new shape test cannot see - and is open. `PL-TKFD` carries the
`falsifies:` reachability question, with this item's structural half appended to
it.
