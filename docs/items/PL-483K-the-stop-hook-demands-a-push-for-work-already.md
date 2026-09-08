---
id: PL-483K
title: The stop hook demands a push for work already pushed after a branch is restarted per the merged-PR recovery, because checkout -B from origin/main leaves the upstream pointing at main
priority: P2
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: .claude/hooks/stop_hook_patch.py, tests/unit/test_stop_hook_patch.py
added: 2026-09-06
verify: uv run pytest tests/unit/test_stop_hook_patch.py && grep -q 'def test_a_branch_restarted_from_the_default_branch_is_not_asked_to_push_again' tests/unit/test_stop_hook_patch.py
---

**Problem.** Observed 2026-09-06. `PL-GYH2`'s pull request merged while a
recheck was in flight, so the session followed the web harness's own
merged-pull-request procedure - restart the branch from the default branch,
keeping its name:

```
git checkout -B claude/pl-gyh2-gas-volumes origin/main
```

That sets `branch.<name>.merge` to `refs/heads/main`. The follow-up commit was
then pushed and a new pull request opened, so nothing was outstanding - but the
container's stop hook reported "Branch has 1 unpushed commit(s) and no remote
branch. Please push these changes", because it compares against the upstream,
which is now `main`, and the branch is legitimately one commit ahead of it.

The second clause compounds it: `git clone --depth 1` is single-branch, so
`remote.origin.fetch` is `+refs/heads/main:refs/remotes/origin/main` and no
`origin/<branch>` tracking ref exists to compare against even after a
successful push. `git branch --set-upstream-to` then refuses with "not a
branch", so the obvious repair does not work either; what does is adding a
refspec for `refs/heads/claude/*` and re-fetching.

**Why it matters.** It is a false alarm arriving at the exact moment a session
is finishing, saying the one thing most likely to be acted on without checking.
The safe response is to verify against `git ls-remote` - which showed the
remote branch head identical to `HEAD` - but the *obvious* response is to push
again, and on a differently-shaped branch that is how abandoned work gets
recreated. `PL-WW08` fixed a neighbouring case for this repository and
`PL-90CJ` reports it upstream; this one is a different mechanism - the upstream
is wrong rather than stale - and it fires on the recovery path the harness
itself prescribes, so it will recur every time a session's pull request merges
mid-flight.

**Candidate fixes**, in order of where the defect really is:

1. The harness's merged-pull-request procedure should say to restore tracking
   after the restart, or use a form that does not repoint it.
2. `.claude/hooks/stop_hook_patch.py` already rewrites this hook for this
   repository and could compare against `refs/remotes/origin/<branch>`, or
   against `git ls-remote`, rather than against whatever the upstream happens
   to be.
3. The clone instruction could fetch the `claude/*` refspec, which also makes
   `docket flight` and `docket stranded` see sibling branches - and see
   `PL-KX9N` for a sharper reason to widen what a session clones.

**Where.** `.claude/hooks/stop_hook_patch.py`; the harness's own procedure,
which is outside this repository (`PL-90CJ` is the existing route for that).

**Done when.** A session that restarts its branch by the harness's own
merged-pull-request recovery is not told, at the moment it finishes, to push
work it has already pushed - and the candidate taken is recorded here. The two
candidates outside this repository are `PL-90CJ`'s to carry rather than this
item's.

**Found by** `PL-GYH2`.

**Observed again 2026-09-07, with no restart involved, which widens this
item's trigger and makes its `Done when` too narrow.** A session that cloned
fresh (`git clone --depth 1`, per the harness's own `add_repo` instruction),
created `claude/pl-gbbz-prose-prerequisites` from `main`, committed twice,
pushed with `git push -u` and opened `#434` was told at the stop hook:
"Branch has 2 unpushed commit(s) and no remote branch."

`git ls-remote origin refs/heads/claude/pl-gbbz-prose-prerequisites` returned
the same sha as `HEAD` - the work was fully pushed. So the second clause above
is not a compounding factor on the restart path; it is a sufficient cause on
its own, and `git push -u` reports "set up to track" while silently storing no
tracking ref, because the single-branch refspec does not cover the destination.
The repair this brief already names is what worked:

    git fetch origin <branch>:refs/remotes/origin/<branch>
    git config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
    git branch --set-upstream-to=origin/<branch>

The order matters - `--set-upstream-to` still refuses with "not a branch" until
the refspec is widened, even once the tracking ref exists.

**So the `Done when` below is satisfiable while the defect still fires.** It
asks only that a session restarting its branch by the merged-pull-request
recovery not be told to push again; on this evidence the condition should be
that *no* session is told to push work `git ls-remote` shows is pushed,
whatever shape its branch has. Candidate 3 (fetch the `claude/*` refspec) now
looks like the one that covers both paths, since it removes the cause rather
than teaching the comparison to tolerate it.

**Found again by** `PL-GBBZ`.


**Observed twice more 2026-09-07, on branches outside `claude/*`, which
narrows candidate 3.** A session working `PL-F5GN` cloned fresh
(`git clone --depth 1`) and pushed two branches with `git push -u`:
`codex/batch-PL-F5GN`, the batch branch `docs/worker.md` prescribes for a
worker run, and later `chore/docket-record-452`. Neither ended up with a
`refs/remotes/origin/<branch>`, and `git ls-remote` returned `HEAD`'s sha for
both, so both were fully pushed.

Neither name matches `claude/*`, so candidate 3 as written - fetch the
`claude/*` refspec - would have left both of these firing. The cause does not
turn on what the branch is called: `remote.origin.fetch` covers only `main`,
so the repair has to widen to `+refs/heads/*:refs/remotes/origin/*`, or to the
branch actually being pushed, rather than to one prefix. `docs/worker.md`
mandates `codex/batch-<id>-<id>-...` for a worker run, so a worker's branches
are never `claude/*` by construction and a `claude/*` refspec would miss every
delegated batch.

**The two branches failed differently, and the second failure is the dangerous
one.** `chore/docket-record-452` produced the stop-hook message this item is
named for. `codex/batch-PL-F5GN` never reached the stop hook: the missing
tracking ref surfaced earlier, as a *push* rejection. After rebasing onto a
moved `main`, `git push --force-with-lease` was refused with `stale info`,
because the lease had no `refs/remotes/origin/<branch>` to read. The stop-hook
message invites a redundant push, which is harmless. This one invites dropping
`--force-with-lease` for a bare `--force`, which is not, and it arrives at the
one moment the branch is legitimately being rewritten. What made the force
safe was confirming with `git ls-remote` that the remote head was the
session's own pre-rebase commit; the refspec repair this brief already names
is what removes the need to make that judgment at all.

**Found again by** `PL-F5GN`.
