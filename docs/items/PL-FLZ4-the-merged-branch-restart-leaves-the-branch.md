---
id: PL-FLZ4
title: The merged-branch restart leaves the branch upstream pointing at a deleted ref, so git status warns the upstream is gone
status: untriaged
added: 2026-09-01
---

**Problem.** The merged-branch restart leaves the branch upstream pointing at a deleted ref, so git status warns the upstream is gone

**Why it matters.**

**Where.**

**Done when.**

**Observed 2026-09-01, restarting after PR #132 merged.** `CLAUDE.md`'s rule -
`git branch -dr origin/<branch> && git fetch origin main && git checkout -B
<branch> origin/main` - removes the stale remote-tracking ref, but the branch
already existed, so `checkout -B` keeps its `branch.<name>.remote` and
`branch.<name>.merge` configuration. Those still name the branch GitHub
deleted, and git says so:

    Your branch is based on 'origin/claude/stale-tracking-ref-merge-8oyuen',
    but the upstream is gone.
      (use "git branch --unset-upstream" to fixup)

**Why it was left out of the rule rather than fixed in it.** The stop hook
reads `git rev-parse "origin/$current_branch"`, which is the *ref* and not the
configuration, so this does not reproduce the defect `PL-1Q3S` closes - the
hook falls through correctly with the config still dangling. And it self-heals:
`git push -u origin <branch>`, which the harness's push instruction already
specifies, rewrites both keys on the next push. Adding a fourth command to a
rule that every session loads at launch, to silence a warning that clears
itself, looked like the wrong trade against the resident-line advisory
`PL-H7XN` exists to raise.

**So the open question is whether it is worth anything at all,** which is a
triage decision rather than a defect report. The case for doing something: a
session that reads `git status` between the restart and its first push meets a
warning that looks like a problem and is not, and proving it harmless costs a
turn - the same cost `PL-1Q3S` was filed to remove, one layer down. The case
for `dropped`: one line of git output, on a state that lasts until the next
push, against permanent resident context.

If it is worth doing, the cheap form is `git branch --unset-upstream` appended
to the restart sequence, or a clause saying the warning is expected. `docs/
worker.md` is not a candidate - a worker never restarts a branch after a merge.
