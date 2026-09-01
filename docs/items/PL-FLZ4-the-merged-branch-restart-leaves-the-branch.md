---
id: PL-FLZ4
title: The merged-branch restart leaves the branch upstream pointing at a deleted ref, so git status warns the upstream is gone
priority: P3
effort: S
status: dropped
classes: infra, session-cost
feature: dev-tooling
touches: CLAUDE.md
added: 2026-09-01
closed: 2026-09-01
reason: The warning clears itself on the next push, so the fix costs permanent resident context to remove a transient line of git output. `git push -u origin <branch>` - already the standing push instruction - rewrites both `branch.<name>.remote` and `branch.<name>.merge`, and it was observed doing so in the session that captured this. The stop hook this sits next to reads `git rev-parse "origin/$current_branch"`, the ref rather than the configuration, so nothing about `PL-1Q3S`'s defect survives here. Recorded rather than deleted so the warning is recognised as expected the next time somebody meets it.
---

**Problem.** `CLAUDE.md`'s merged-branch restart - `git branch -dr
origin/<branch> && git fetch origin main && git checkout -B <branch>
origin/main` - removes the stale remote-tracking ref, but the branch already
exists, so `checkout -B` keeps its `branch.<name>.remote` and
`branch.<name>.merge` configuration. Those still name the branch GitHub
deleted, and git says so:

    Your branch is based on 'origin/claude/stale-tracking-ref-merge-8oyuen',
    but the upstream is gone.
      (use "git branch --unset-upstream" to fixup)

Observed 2026-09-01, restarting after PR #132 merged.

**Why it matters.** Only that a session reading `git status` between the
restart and its first push meets a warning that looks like a problem and is
not, and spends a turn proving it harmless - the same cost `PL-1Q3S` was filed
to remove, one layer down. Against that: the state lasts until the next push,
the stop hook does not read it, and no command misbehaves while it holds.

**Where.** `CLAUDE.md`'s merged-branch restart bullet. `docs/worker.md` is not
a candidate - a worker makes one branch per batch and never restarts one after
a merge.

**Done when.** Would have been: the restart sequence leaves no dangling
upstream, or the rule says the warning is expected. The cheap form is `git
branch --unset-upstream` appended to the sequence.

**Dropped 2026-09-01, at triage, by the session that captured it.** The fix is
a fourth command on a rule that every session loads at launch, bought to
silence one line of git output on a state that ends at the next push. That is
the wrong side of the trade the resident-line advisory exists to force, and
`PL-1DN9` - captured in the same session and kept - is the contrast: silent,
reviewer-facing, and it does not heal.
