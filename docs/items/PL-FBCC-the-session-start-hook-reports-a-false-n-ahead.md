---
id: PL-FBCC
title: The session-start hook reports a false 'N ahead' count in a shallow clone
status: untriaged
added: 2026-08-31
---

**Problem.** `.claude/hooks/docket-digest.sh` reports the working branch's
position with `git rev-list --left-right --count origin/main...HEAD`. In a
shallow clone - which is what an agent session's container is - there is no
merge base once `origin/main` advances past the graft boundary, so the
symmetric difference degenerates into "everything on each side of the shallow
window". Observed on 2026-08-31: a branch with zero commits of its own was
reported as `is 1 behind origin/main and 98 ahead`. Deepening the history with
`git fetch --deepen=100 origin` made the same command answer `1 0`.

**Why it matters.** The line exists to stop a session stacking work on merged
history or working from a stale base, and both of those are read off the two
counts. A false "98 ahead" says the branch carries work it does not, which is
exactly the state the session is told to protect - so the check misleads in
the direction of not merging, in the case it was written for.

**Where.** `.claude/hooks/docket-digest.sh`, `branch_state()`.

**First step.** Either deepen before counting (`git fetch --deepen=<n>`, cost
bounded and paid once per session) or ask `git merge-base HEAD origin/main`
first and print no counts when it is empty, saying the clone is too shallow to
tell. The second is honest and free; the first gives the real answer. They
compose: deepen, then fall back to the honest message if a merge base still
does not resolve.

**Done when.** A shallow container whose `origin/main` has advanced reports
either the true counts or an explicit "cannot tell from this clone", never a
fabricated one.
