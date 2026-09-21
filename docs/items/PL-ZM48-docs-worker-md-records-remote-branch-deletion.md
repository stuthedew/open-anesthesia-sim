---
id: PL-ZM48
title: docs/worker.md records remote-branch deletion as exit status 0, and PL-3V6C as two incompatible causes, but one 2026-09-20 transcript carries the 403 and the Everything up-to-date line together at exit 1
priority: P2
effort: S
status: done
classes: defect, docs
feature: remote-ref-deletion
milestone: v0.5.2
touches: docs/worker.md, docs/items, docs/WORKING_NOTES.md
added: 2026-09-20
closed: 2026-09-21
pr: 863
payoff: a session composing a branch cleanup reads one established cause instead of two candidates, and stops being told the push exits 0 when it exits 1
verify: grep -qF 'PL-ZM48' docs/worker.md
---

**Problem.** docs/worker.md records remote-branch deletion as exit status 0, and PL-3V6C as two incompatible causes, but one 2026-09-20 transcript carries the 403 and the Everything up-to-date line together at exit 1

**Measured 2026-09-20**, deleting `claude/tender-keller-omy3ec` (pull request
#691, merged) with the project owner's explicit instruction to clean up
branches — the authorization `PL-3V6C` says no session had, which is why the
cause stayed open:

```
$ git push origin --delete claude/tender-keller-omy3ec
fatal: --negotiate-only needs one or more --negotiation-tip=*
warning: push negotiation failed; proceeding anyway with push
error: RPC failed; HTTP 403 curl 22 The requested URL returned error: 403
send-pack: unexpected disconnect while reading sideband packet
fatal: the remote end hung up unexpectedly
Everything up-to-date
--- exit status: 1 ---

$ git ls-remote --heads origin claude/tender-keller-omy3ec
ef83cd8fc5b3c70670789e3f8c4999579817970d	refs/heads/claude/tender-keller-omy3ec
```

`curl "$HTTPS_PROXY/__agentproxy/status"` at the same moment returned
`recentRelayFailures: []`.

**Three corrections follow, and the first two are the load-bearing ones.**

1. **`PL-3V6C`'s premise is wrong.** It reasoned that "a push cannot both be
   silently swallowed and be refused with a status code, so at most one of these
   is the failure this project actually meets". The transcript above carries
   `HTTP 403` *and* `send-pack: unexpected disconnect` *and* `Everything
   up-to-date`, in that order, from one command. `PL-TFWR` and `PL-XQRK` did not
   measure different failures; they read different lines of the same output.
   `PL-3V6C` is `done` and closed on the conclusion that the cause was
   unestablished, which was the right call on the evidence it had.
2. **The exit status is 1, not 0.** `docs/worker.md` says both operations "fail
   in the worst available shape: exit status 0, with a last line that reads as
   success". Half of that holds — `Everything up-to-date` is still the last
   line, so a session reading only the last line is still misled — but a session
   checking `$?`, or running the push unchained, gets a non-zero status. The
   table's `What a session sees` cell for branch deletion should carry the 403
   as the established cause rather than `or`-ing two candidates, and the
   exit-status claim should be scoped to the tag-push row, which this did not
   re-measure.
3. **`recentRelayFailures: []` is confirmed worthless as evidence here**, exactly
   as `PL-3V6C` argued: it was empty while a 403 was being returned.

**Why it matters.** The table is what a session reads before composing a branch
cleanup, and it currently offers two candidate causes without choosing. A
session told "the proxy drops ref deletions" concludes something different from
one told "GitHub refuses the ref" — `PL-4Q9B` names that as the generating
hazard. One is now established and the record can say so.

**Done when.** `docs/worker.md` § "Ref operations a session cannot perform"
names HTTP 403 as the measured cause of the branch-deletion failure with this
item's date, scopes the exit-status-0 claim to the tag-push row it was measured
on, and `PL-3V6C` carries a note that its mutual-exclusivity premise was
falsified.
