---
id: PL-R808
title: Build the exact left-behind check as a tools/ script comparing a branch tip against refs/pull/<n>/head, declining where those refs are not fetched
status: ready
feature: parallel-sessions
priority: P2
effort: M
classes: infra, defect
touches: tools, tests/unit
added: 2026-09-12
verify: uv run pytest tests/unit/test_tools_portability.py -q && test -f tools/left_behind_check.py && grep -q 'refs/pull' tools/left_behind_check.py
---

**Problem.** Build the exact left-behind check as a tools/ script comparing a branch tip against refs/pull/<n>/head, declining where those refs are not fetched

**Unblocked by `PL-VV4D`**, which decided on 2026-09-12 to build the exact
comparison and to put it in `tools/` beside `vcs.orphaned` rather than in place
of it. That item carries the reasoning and the costs accepted; this one is the
build.

**The invariant.** A pull request merges the head it was opened against, and
GitHub freezes `refs/pull/<n>/head` at that head when the pull request closes.
So: does the branch tip point *past* the pull-request head that merged? Equal or
an ancestor means nothing was left behind; a descendant means exactly the
commits between them were, named with no content comparison - no squash
confound, no rename confound, no blob identity.

**Constraints carried from the decision.**

- `tools/` script, standard library only, so a hook or a bare checkout can run
  it without the project virtualenv. Not a `docket` command: `PL-SK88` decided
  `docket` must not learn about the harness.
- It must **decline** where `refs/pull/*` have not been fetched, rather than
  guess or report a clean answer. A checkout that cannot see the refs knows
  nothing, and saying so is the whole point of preferring it to a heuristic.
- `vcs.orphaned` stays as the portable half and is not touched.

**Known test vectors**, from `PL-VV4D`: `#312`'s release branch, where the tip
equals `refs/pull/312/head` and the exact check must stay silent where the
content comparison fired falsely; and `#284`, where the branch stood at
`9fee36c` against a frozen `refs/pull/284/head` of `7f87bf5`, so the one commit
between them is the loss.

**Still to decide as part of the build:** where it is wired - CI, the digest, or
`make check` - and what it prints when it and `vcs.orphaned` disagree, which is
the case a reader most needs help with.

**Why it matters.** `vcs.orphaned` is what stands between a commit pushed after
a merge and being lost, and today it answers by comparing *content*, which a
squash merge rewrites on its way in. That heuristic has produced recorded false
positives in `PL-JHJ3`, `PL-XLQ5`, `PL-Y31G`, `PL-JBRC` and `PL-8MJ3` - a
detector firing on branches carrying nothing, which `CLAUDE.md` calls the worst
shape a check can have, because it trains a reader to skim the output where a
real finding also appears. Those four are now blocked on this item rather than
worked individually: each is the same heuristic failing a new way, and patching
them one at a time is what has kept the cluster at r = 1.05, generating more
items than it closes.

**Done when.** A standard-library script under `tools/` decides whether a
branch left work behind by comparing its tip against `refs/pull/<n>/head`, with
no content question in it; it declines explicitly where those refs have not
been fetched rather than reporting a clean answer; `vcs.orphaned` is unchanged
and still answers in a bare checkout; the two known vectors behave - silent on
`#312` where the tip equals the frozen head, and naming exactly the one commit
on `#284` between `9fee36c` and `7f87bf5`; and a test under `tests/unit/`
covers both vectors and the declines-when-unfetched path.

