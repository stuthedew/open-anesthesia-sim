---
id: PL-21KN
title: bin/docket arm answers for the checkout's HEAD even where the pull request's own branch on origin is ahead of it, so once someone else has brought main into the pull request it still reports behind N and advises update_pull_request_branch or a merge and push, both of which misfire
priority: P2
effort: S
status: ready
classes: defect
feature: remote-copy
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py
blocked-by: PL-MT3R
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-26 triage pass
added: 2026-09-26
payoff: arm stops advising an update for a pull request already level with main, so neither misfiring remedy gets run
verify: grep -q 'def test_arm_reads_the_pull_requests_branch_on_the_remote_not_head' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket arm answers for the checkout's HEAD even where the pull request's own branch on origin is ahead of it, so once someone else has brought main into the pull request it still reports behind N and advises update_pull_request_branch or a merge and push, both of which misfire

**What was seen.** On 2026-09-26 at 01:18Z, while `#1041` (the `PL-MB2W`
close-out) waited on CI, its branch on origin was brought up to date with
`main` by a GitHub *Update branch* made outside this checkout: the merge commit
`39d0eb86` on top of `c08ace60`. After `git fetch origin`, this checkout's
`claude/pl-mb2w-closeout-i7pg11` was still at `c08ace60`, and `bin/docket arm
--no-fetch` answered:

```
behind 1 - origin/main has 1 commit claude/pl-mb2w-closeout-i7pg11 lacks, and main merges only an up-to-date branch
  Bring it in once - `update_pull_request_branch`, or merge origin/main and push - then ask again.
```

The pull request already held `origin/main`'s tip, so the answer was wrong
about the pull request it names. Both remedies it offers misfire. There is
nothing for `update_pull_request_branch` to bring in, and its
`expectedHeadSha` from this checkout is stale. A local merge of `origin/main`
then push is refused as a non-fast-forward, because origin holds a merge commit
`HEAD` lacks. What was needed was `git merge --ff-only
origin/claude/pl-mb2w-closeout-i7pg11`, after which `arm` answered `arm`.

**Where it comes from.** `arming.arm` counts `rev-list --count HEAD..<base>`
and diffs `<base>...HEAD`, both from `HEAD`. It never compares `HEAD` with
`origin/<branch>`, although its docstring says it answers for "the pull request
`HEAD`'s branch would open, or has open". Answering for `HEAD` is right when
`HEAD` is what is about to be pushed. It is wrong when origin's copy of the
branch has commits `HEAD` lacks, because then `HEAD` cannot be pushed as it
stands.

**Not yet checked.** The same reading would also miss a commit that another
writer pushed to the branch and that touches a path outside the store. `arm`
could then answer `arm` for a pull request that lands that path. This is
inferred from the code and not reproduced. It needs two writers on one branch,
so it is rarer than the *Update branch* case above.

**A direction, not a decision.** Where `origin/<branch>` exists and is not an
ancestor of `HEAD`, say so before anything else: origin's branch has N commits
this checkout lacks, fast-forward (or merge) it and ask again. That makes it an
`unknown` or `hold` answer, not `behind`. This may be one more member of
`PL-XBV4` (read commands answering from different moments without saying
which): `arm` fetched, then answered from a checkout that lagged what it had
fetched. Whoever triages this should decide whether it belongs there.

**Premise confirmed by reading, 2026-09-26, against `78b1a02b`.** One grep of
`arming.py` found `HEAD` in two reads only: `rev-list --count HEAD..<base>` and
`diff --name-only <base>...HEAD`. Nothing in the module reads `refs/remotes`
or the branch's copy on origin.

**Why it matters.** `CLAUDE.md` has a session ask `arm` before arming and
before every later push while a pull request is open. A wrong `behind` sends
it to a remedy that fails at the moment the pull request is otherwise ready:
`update_pull_request_branch` with a stale `expectedHeadSha`, or a merge and
push refused as a non-fast-forward. The case under **Not yet checked.** would
matter more, though it is inferred rather than reproduced. It would answer
`arm` for a pull request landing a path outside the store, which is the
direction the gate exists to refuse.

**Done when.** Where the pull request's branch on the remote has commits `HEAD`
lacks, `arm` says so before anything else and answers `unknown` or `hold`, not
`behind`, naming what brings them in. A real-git test holds the *Update branch*
shape: the branch's copy on the remote carries a merge of the base that `HEAD`
lacks. The second writer's case under **Not yet checked.** is either covered by
the same read or recorded as not arising.

**Generator check.** An instance of `PL-4Q9B`'s fact, "The remote's current
refs and tags, and whether the clone's local copies still match them". It is
the fourth since that head closed on 2026-09-19, after `PL-WX87`, `PL-KX73` and
`PL-C3MN`, and belongs to `PL-MT3R`. It is not `PL-XBV4`'s, which is the moment
a read's sources were taken. `arm` had fetched, so its refs were fresh. It read
the local branch where the pull request's copy on the remote was the answer,
and a fresher fetch would not have moved that local branch.

**Blocked, triage 2026-09-26, on `PL-MT3R`'s decision.** The record that head
recommends is where `arm` would read the branch's copy on the remote from, so
the direction above waits on it rather than reading `origin/<branch>` alone.
