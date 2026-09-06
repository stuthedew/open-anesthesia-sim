---
id: PL-YGF3
title: A repository-wide history rewrite silently dropped two commits pushed into its window, and no guard reported the loss
status: done
added: 2026-09-06
closed: 2026-09-06
priority: P2
effort: M
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/README.md, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py, tests/unit/test_no_prune_guard.py, .claude/skills/docket/SKILL.md
verify: uv run pytest subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_rewritten_base_is_told_apart_from_a_branch_that_is_merely_behind' subprojects/docket/tests/test_vcs.py
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

**A branch prune does not finish the job, observed 2026-09-06.** Clearing the
stale remote-tracking branches left the purged PDFs still reachable in the
local clone, because the release tags `v0.3.7` through `v0.4.4` had not been
refreshed and still pointed at pre-rewrite commits. The remote was clean
throughout - all seven branches and all thirty-one tags checked - so this was
local state only, but a clone in that condition still holds the files the
purge existed to remove, and `git log --all` is what shows it. `git fetch
--tags --force` is the missing half. The `git branch -dr` recipe in the
`docket` skill covers branches and says nothing about tags.

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

**Approach, chosen 2026-09-06.** The "not a descendant of what this checkout
last saw" test above needs a memory of the ref's previous value, and the only
thing that holds one is `git reflog refs/remotes/origin/<branch>`. A container
clones fresh, so in the session that matters most - a new one, opened after the
rewrite - that reflog has exactly one entry and the test cannot fire. So the
detection is stateless instead, and reads the shape of the divergence itself:
a rewrite leaves the branch's own commits *duplicated* on the base under new
hashes, matched by author date and subject, which `git log --left-right` prints
from one read of the symmetric difference. The rule is that the **oldest**
commit unique to the branch has a counterpart on the base - the divergence
begins in duplicated history, which is what a rewrite does and what forking and
committing cannot. Ordinary drift matches nothing and stays silent.

Matching on author date and subject rather than on patch id, deliberately: the
rewrite that prompted this stripped a file from history, so the patch of every
commit that touched it changed, and `git cherry` drops merge commits entirely -
one of the two commits actually lost here was a merge.

It lands in `branch_state`/`format_branch_state`, not in `stranded`, because
that is where the destructive advice is printed. `stranded` already recovers
the item *files* off such a branch and its recovery still works; what nothing
did was stop `git merge` or `git checkout -B` being recommended over a history
that is one history under two sets of hashes.
