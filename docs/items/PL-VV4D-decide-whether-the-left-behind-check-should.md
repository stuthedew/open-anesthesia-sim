---
id: PL-VV4D
title: Decide whether the left-behind check should compare against refs/pull/<n>/head, which is exact but makes the check GitHub-specific
status: untriaged
feature: parallel-sessions
added: 2026-09-04
---

**Problem.** Decide whether the left-behind check should compare against refs/pull/<n>/head, which is exact but makes the check GitHub-specific

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `vcs.orphaned` detects a commit left behind by comparing *content*:
which of a branch's introduced paths the base has held, narrowed to commits none
of whose paths reached it. Every content comparison is a heuristic, because a
squash merge rewrites content on its way in - which is what made the check fire
falsely on its first live run (`PL-JHJ3`), and what the current rule works
around rather than removes.

**The exact test.** A pull request merges the head it was opened against, and
GitHub freezes `refs/pull/<n>/head` at that head when the pull request closes.
So the invariant is a ref comparison and nothing else: *does the branch tip
point past the pull-request head that merged?* Equal or an ancestor means
nothing was left behind. A descendant means exactly the commits between them
were, named without any content question - no squash confound, no rename
confound, no blob identity.

Checked against the two known cases. `#312`'s release branch: tip equals
`refs/pull/312/head`, so silent, where content comparison fired. `#284`: the
branch stood at `9fee36c` while `refs/pull/284/head` froze at `7f87bf5`, so the
one commit between them is the loss, exactly.

**What it costs, and why it is a decision rather than a fix.**

- `refs/pull/*` is a GitHub ref namespace. It is git rather than an API - no
  token, no round trip beyond a fetch - but it is still this harness, and
  `PL-SK88` decided that `docket` must not learn about the harness and that
  such a check lives outside it. So this would be a `tools/` script, wired into
  CI or the digest, not a `docket` command.
- It needs those refs fetched. All 311 of this repository's fetch in 1.9 s, so
  cost is not the objection; a checkout that has not fetched them answers
  nothing, which is a decline the current check does not need.
- Two detectors for one failure is its own cost. Either `orphaned` stays as the
  portable half and the exact check sits beside it, or `orphaned` is retired and
  the detection becomes GitHub-only - and a queue this project runs from a bare
  checkout has reasons to prefer the first.

**Decision needed.** Whether to add the exact `refs/pull/<n>/head` comparison at
all, and if so whether it replaces `vcs.orphaned` or sits beside it in `tools/`
as the precise half while `orphaned` stays the portable one.
