---
id: PL-YGF3
title: A repository-wide history rewrite silently dropped two commits pushed into its window, and no guard reported the loss
status: untriaged
added: 2026-09-06
---

**Problem.** On 2026-09-06 the copyrighted-PDF purge rewrote every commit on
`main` and on the open feature branches. It snapshotted
`claude/fresh-gas-flow-range-4bom2g` at `2966d9b`, the branch's triage commit.
Two commits pushed after that snapshot - the `origin/main` merge that resolved
the branch's conflicts, and `PL-N1JK`'s capture - were not carried onto the
rewritten history and exist on no surviving ref. The session that wrote them
recovered them only because it still held them in a live checkout.

**Why it matters, and why no existing guard covers it.** Every loss guard this
project has assumes the ref survives and the commit is the thing at risk:

- `bin/docket stranded` looks for an item on a branch and absent from the
  default branch. Here the branch ref still existed, pointing at a *rewritten
  ancestor* of the lost work - so the branch looked healthy and shorter, not
  lost. It reported `claude/fresh-gas-flow-range-4bom2g` under "left on a
  branch after its pull request merged", which is a different condition with a
  different remedy.
- The no-prune guard (`PL-JK0M`, `PL-HKF4`) protects a stale `origin/<branch>`
  from `git fetch --prune`. A rewrite does not prune the ref; it *replaces* it,
  which the guard does not see.
- `docket check`, `flight` and `next` all read items, and the lost commits'
  items had never reached the default branch, so nothing was owed and nothing
  fired.

The session-start digest did report the branch as 699 behind and 703 ahead,
which is the signal - but it reads as ordinary drift, and the reflex it invites
(`git reset --hard origin/main`, which is what was asked for) is precisely the
action that would have destroyed the only surviving copy.

**What made it recoverable, which is luck rather than design.** The session was
still live with the files in its working tree, so it could copy them out before
resetting. A fresh session, or the same session after its container was
reclaimed, would have had nothing to copy - and no report anywhere saying two
commits were missing.

**Observed 2026-09-06, and wider than one branch.** Of the nine remote refs,
only `main` and `claude/fresh-gas-flow-range-4bom2g` descend from the rewritten
history. The other seven - among them
`claude/desflurane-tec6-vaporizer-kulwij`, which holds four captures including
`PL-SHG5`'s copyright finding - still sit on the pre-rewrite history and are
not ancestors of anything on `main`.

Nothing is lost while those refs exist: the item files are readable off each
branch and `bin/docket stranded` prints the `git checkout` line for them. What
is lost is the ability to merge them, and two ordinary actions destroy them
outright - a prune, which `.claude/hooks/no-prune-guard.sh` already refuses,
and a `git reset --hard origin/main` on the branch, which nothing refuses and
which is the natural reflex on seeing a four-figure ahead/behind count. That
second one is the gap.

**Where.** `subprojects/docket/src/docket/` - whatever `stranded` uses to
classify a branch, which currently cannot distinguish "this branch was
rewritten and lost commits" from "this branch is behind". The session-start
digest, which prints the ahead/behind counts without saying that a large
symmetric divergence means a rewrite rather than drift. `PL-1Q3S` and `PL-PF8H`
carry the two existing ways a ref goes stale; this is a third.

**Done when.** Either something reports a branch whose remote ref has been
replaced by a commit that is not a descendant of what this checkout last saw -
which is the decidable half, and is what distinguishes a rewrite from ordinary
drift - or the digest's ahead/behind line says plainly that a symmetric
divergence of this size means history was rewritten and that `reset --hard` is
destructive until the branch's own content has been copied out.
