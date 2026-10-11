---
id: PL-JTP1
title: Six callers drop or bypass a decline their shared reader names, so a reader should return its declines in a type the strict mypy run makes every caller handle
priority: P3
effort: M
status: ready
classes: refactor
feature: reader-checks
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/frontmatter.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/instructions.py, tools/dead_ends.py, tools/doc_check.py, subprojects/docket/tests
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
payoff: A caller that drops a shared reader's declines fails mypy at the pull request that writes it, instead of answering from a partial reading until a sweep files it
verify: ! grep -qF 'unread: list[UnreadEntry] | None = None' subprojects/docket/src/docket/roadmap.py && ! grep -qF 'document_entry_lines(lines, [])' subprojects/docket/src/docket/release.py
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

**Reproduced 2026-10-11** on main at `16a20a4f`:
`docket.roadmap.document_entry_lines` takes its declines through an optional
out-parameter, `unread: list[UnreadEntry] | None = None`, so a caller that
omits it or passes `[]` type-checks under the strict `mypy` run.
`tools/dead_ends.py`'s `entries` passes `[]` through `_bullets` (`PL-DQ9C`),
and `docket.release.notes_ids` passes `[]` as well, there on purpose: its
docstring says a declined bullet still claims the id leading it. So the type
the work introduces needs an explicit way to set a decline aside, which that
caller is the case for.

**Why it matters.** Each of the six is a reader answering from a partial
reading without saying so, which the apparatus floor refuses, and each was
found by a sweep rather than by a tool. A result type carrying the declines
turns the next such caller into a type error at the pull request that writes
it, rather than an item a later sweep files.

**Generator check.** Not a member of `PL-R417`: a guard that would make its
members fail loudly, not a reader that misreads where a statement ends.

**Done when.** Each shared reader that declines a statement returns the
decline in a type its callers must unpack, and none of the six callers can
drop one without a type error.
