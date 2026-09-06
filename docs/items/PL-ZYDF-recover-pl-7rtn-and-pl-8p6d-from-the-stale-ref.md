---
id: PL-ZYDF
title: Recover PL-7RTN and PL-8P6D from the stale ref of the deleted capture-item-pr-checks branch
priority: P2
effort: S
status: done
classes: infra
feature: parallel-sessions
milestone: v0.4.5
touches: docs/items/
added: 2026-09-06
closed: 2026-09-06
verify: test -f docs/items/PL-7RTN-an-open-pull-request-can-carry-no-check-runs-at.md && test -f docs/items/PL-8P6D-checks-do-not-run-on-a-pull-request-opened-by.md
---

**Problem.** `claude/capture-item-pr-checks-cj5zhp` was deleted from the remote
on 2026-09-06, in the branch sweep that cleared nine merged branches. It was
not one of the nine: it carried `PL-7RTN` (an open pull request can carry no
check runs at all, so a branch merges with nothing having gated it) and
`PL-8P6D` (checks refuse a pull request whose branch carries no item id, so the
owner's own web edits and any contributor's pull request fail CI), and neither
existed on any other ref.

**Why it matters, and why it was still recoverable.** `git fetch` does not
prune, so `refs/remotes/origin/claude/capture-item-pr-checks-cj5zhp` survived
in this checkout after the branch was gone from the remote — which is the
precise case `.claude/hooks/no-prune-guard.sh` exists to preserve, and what
`PL-HKF4` came within one prune of losing. `bin/docket stranded` still named
both items and printed their recovery lines, because it reads the refs the
checkout holds rather than the remote.

That window is not durable. It closes when this container is reclaimed, and it
closes for every other checkout that never fetched the branch at all. No other
session had it.

**What the two items are about, which is why losing them would have stung.**
Both are findings about the checks that gate merges: one that a pull request
can carry no check runs and merge ungated, one that `branch_id_check` refuses a
pull request whose branch has no item id — which is exactly the shape of the
project owner's own web edits (`#394`, "Add pre-release warning to README",
leads with no id) and of any outside contributor's first pull request, now that
the repository is public.

**Where.** Recovered by `git checkout origin/claude/capture-item-pr-checks-cj5zhp --`
onto `claude/public-launch-cleanup-zxw9qn`, in the commit this item leads. Both
arrive `untriaged`, which is the shape they were captured in.

**Done when.** Both item files stand on the default branch.
