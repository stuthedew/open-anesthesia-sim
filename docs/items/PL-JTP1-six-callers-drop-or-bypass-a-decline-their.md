---
id: PL-JTP1
title: Six callers drop or bypass a decline their shared reader names, so a reader should return its declines in a type the strict mypy run makes every caller handle
status: untriaged
feature: reader-checks
added: 2026-10-10
---

**Problem.** Six of link 23's members read their format through a shared
reader and then lose the decline it names: `PL-L4X3`, `PL-4DM0`, `PL-63Y5` and
`PL-DQ9C` drop it, and `PL-J8ML` and `PL-7CQ5` fall back to a line at a time
without saying so. A decline a caller can ignore is a check repeated at each
way in, which `.claude/rules/expert-review.md` § "Domains to review against,
and the design principles they carry" refuses under "Parse, don't validate".
If each shared reader returned its declines in its result type, the strict
`mypy` run that already covers docket, `tools` and `.claude/hooks` would make
every caller handle one.

**Found 2026-10-10** by the parsing review in `PL-R417`'s closing sweep thread
(link 23). The owner chose to have `PL-R417`'s last batch add the review's two
differential tests in CI, and this follow-up to be filed as an ordinary item.

**Generator check.** Not a member of `PL-R417`: a guard that would make its
members fail loudly, not a reader that misreads where a statement ends.

**Done when.** Each shared reader that declines a statement returns the
decline in a type its callers must unpack, and none of the six callers can
drop one without a type error.
