---
id: PL-3SGR
title: The stop hook demands a push for fully pushed work when the clone is shallow, because --depth 1 implies --single-branch and git push never creates the remote-tracking ref the hook reads
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
touches: .claude/hooks/stop_hook_patch.py, tests/unit/test_stop_hook_patch.py
added: 2026-09-07
closed: 2026-09-12
verify: uv run pytest tests/unit/test_stop_hook_patch.py && grep -q 'def test_a_pushed_branch_with_no_remote_tracking_ref_is_not_asked_to_push_again' tests/unit/test_stop_hook_patch.py
---

**Problem.** The stop hook demands a push for fully pushed work when the clone is shallow, because --depth 1 implies --single-branch and git push never creates the remote-tracking ref the hook reads

Observed 2026-09-07 on `PL-GZP6`'s branch, after three successful pushes. The
stop hook reported "has 3 unpushed commit(s) and no remote branch", while
`git ls-remote origin claude/pl-gzp6-model-required-tests` returned exactly
the local `HEAD` - the work was entirely pushed.

**The cause is a second one, distinct from `PL-483K`'s.** That item is the
same false demand arising from `git checkout -B` off `origin/main` leaving the
upstream pointed at `main`. This one needs no restart and no recovery: the
session's clone was made with `git clone --depth 1`, which implies
`--single-branch`, so `remote.origin.fetch` was
`+refs/heads/main:refs/remotes/origin/main` alone. `git push` sends the branch
and writes `branch.<name>.merge`, but with that refspec no
`refs/remotes/origin/<branch>` is ever created, so `git status -sb` shows a
bare branch name with no upstream and `git rev-parse @{u}` fails outright.
Anything reading tracking state concludes the branch was never pushed.

The `--depth 1` clone is what the session harness's own `add_repo` result
instructs a session to run, so this is the default path rather than an unusual
one, and every session working from a fresh remote container meets it.

**Repair, once known:**

```text
git config --unset-all remote.origin.fetch
git config --add remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
git fetch origin <branch>
git branch --set-upstream-to=origin/<branch>
```

Note that fetching the ref alone is not enough - `--set-upstream-to` still
refuses with "starting point is not a branch" until the refspec is widened,
because git will not treat a ref outside the configured refspec as a
remote-tracking branch. No prune is involved, so
`.claude/hooks/no-prune-guard.sh` is not in the way.

**Why it matters.** The hook's demand is indistinguishable from a real one, and
the obvious response to it - push again - changes nothing and reports
"Everything up-to-date", which reads like the failure the message describes. A
session could reasonably conclude its push is broken and start recovering
work that was never at risk.

**Approach.** Undecided, and it may be one fix with `PL-483K` rather than two:
both are the hook trusting tracking state that can be absent or wrong for
reasons unrelated to whether the commits reached the remote. The robust test
is against the remote - compare `git rev-parse HEAD` with
`git ls-remote origin <branch>` - rather than against `@{u}`, which is local
bookkeeping. Triage may prefer to fold this into `PL-483K` as a second
reproduction; it is filed separately because the cause and the repair differ
and neither is reachable from that item's text.

**Where.** `.claude/hooks/stop_hook_patch.py`; `PL-483K` is the sibling cause.

**Done when.** The stop hook does not demand a push for a branch whose commits
are already on the remote, in a `--depth 1` clone where no
`refs/remotes/origin/<branch>` exists. The test is the shallow, single-branch
case specifically, since that is the one the current correction does not reach.

Re-checked 2026-09-12: `.claude/hooks/stop_hook_patch.py` rewrites the harness
test to `git rev-list HEAD --not --remotes --count`, which reads local
`refs/remotes/*` only. That is `PL-WW08`'s fix for a *stale* tracking ref and it
does not address a *missing* one, so this item is untouched by it and the two
are distinct after all.

**Sequencing.** `PL-483K` is the sibling cause - the same false demand arising
from `git checkout -B` leaving the upstream on `main` - and it is already
`ready` against the same two files. Both are the hook trusting local tracking
state, and a single fix that compares `HEAD` against `git ls-remote origin
<branch>` answers both. Work them together rather than in sequence.
