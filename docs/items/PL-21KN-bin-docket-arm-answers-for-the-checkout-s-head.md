---
id: PL-21KN
title: bin/docket arm answers for the checkout's HEAD even where the pull request's own branch on origin is ahead of it, so once someone else has brought main into the pull request it still reports behind N and advises update_pull_request_branch or a merge and push, both of which misfire
status: untriaged
touches: subprojects/docket/src/docket/arming.py
added: 2026-09-26
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
