---
id: PL-X9WZ
title: git ls-remote --heads for a branch deleted on merge exits 0 with empty output, and a force-with-lease push to it fails 'stale info' rather than 403 - a third shape PL-ZM48's two candidate causes do not cover
priority: P3
effort: S
status: blocked
classes: docs
touches: docs/worker.md, docs/items
blocked-by: PL-ZM48
added: 2026-09-21
payoff: the third observed shape of a deleted-branch push is attached to the item that decides the documented cause, so PL-ZM48 resolves against three data points rather than two
---

**Problem.** git ls-remote --heads for a branch deleted on merge exits 0 with empty output, and a force-with-lease push to it fails 'stale info' rather than 403 - a third shape PL-ZM48's two candidate causes do not cover

**Measured 2026-09-21**, restarting `claude/triage-f1ahwf` after `#812`
squash-merged and GitHub deleted the branch. Offered as a third data point for
`PL-ZM48` (docs/worker.md records remote-branch deletion as exit status 0, and
`PL-3V6C` as two incompatible causes) rather than as a competing diagnosis -
that item is where the question lives.

What the transcript carries, in order:

- `git push -u --force-with-lease origin claude/triage-f1ahwf` failed with
  `! [rejected] claude/triage-f1ahwf -> claude/triage-f1ahwf (stale info)` and
  `error: failed to push some refs`. Not a 403, and not `Everything
  up-to-date`: the lease was refused because the local remote-tracking ref
  named a commit the remote no longer had, the branch being gone entirely.
- `git ls-remote --heads origin claude/triage-f1ahwf` printed **nothing** and
  exited **0**. So the exit status cannot distinguish "branch absent" from
  "branch present", and only the empty stdout says which.
- `git branch -dr origin/claude/triage-f1ahwf` then a plain `git push -u`
  succeeded as a new branch.

**Why the `ls-remote` half matters more than the push half.** A session
checking whether its merged branch still exists will reach for `ls-remote` and
read its exit status, which is the one thing that carries no information here.
The pre-push hook in this repository already prints the correct recipe and is
what unblocked this session; what is missing is any statement that the check
preceding it answers 0 either way.

**Done when.** `PL-ZM48`'s resolution accounts for this shape - a lease
refused as `stale info` against a deleted branch, and `ls-remote` exiting 0 on
absence - or this item is dropped with the reason that shape is already
covered.

**Why it matters.** `docs/worker.md` and `PL-3V6C` between them tell a session
what to expect when it checks whether a merged branch still exists, and neither
covers this shape. A session that reads `git ls-remote --heads`'s **exit status**
rather than its stdout gets 0 whether the branch is there or not, so the check
it reached for to avoid a destructive mistake silently cannot answer — the
silent-wrong-answer shape `CLAUDE.md` asks to be caught. The cost is bounded
(the pre-push hook prints the working recipe, which is what unblocked the
observing session), which is why this is a data point for `PL-ZM48` rather than
its own fix: the question of what the documented cause actually is lives there,
and answering it twice in two items is how the two drift apart.
