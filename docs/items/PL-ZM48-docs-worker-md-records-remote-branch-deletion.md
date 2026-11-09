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

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "Its problem did not exist at the 2026-09-06 freeze, so the snapshot rule defers it on its own terms".

> - PL-ZM48 (S) `docs/worker.md` records a remote-branch deletion as exiting 0, and `PL-3V6C` as two incompatible causes, where one 2026-09-20 transcript carries the 403 and the `Everything up-to-date` line together at exit 1

> **`PL-ZM48`, added 2026-09-20, after the freeze and declined with it.** It corrects `docs/worker.md` § "Ref operations a session cannot perform". That section's branch-deletion row offers two candidate causes without choosing between them, and it states an exit status of 0. A live deletion attempt run that day, under the project owner's instruction to clean the branches up, returned `HTTP 403` at exit 1. `Everything up-to-date` was still the last line, and the ref was intact. So the two causes that `PL-3V6C` called mutually exclusive are successive lines of one transcript. The text that `PL-ZM48` corrects was written under `PL-4Q9B` in v0.4.28, after this gate was frozen on 2026-09-06. So the problem does not predate the freeze. It qualifies on no other ground either. It is classed `defect` rather than `safety` or `science`, and `docs/worker.md` lies wholly inside `docket.toml`'s `workflow_paths`. The cost of deferring it is bounded, because the half of the row that a session acts on is correct and unchanged. A session reading the row learns that it cannot delete a remote branch, which is true. Only the stated cause and the exit status are wrong, and `PL-ZM48` carries the transcript that settles both.

> **The list entry alone would be wrong about which ground it declines on**, which is why that paragraph is carried here rather than recorded as superseded (`PL-QNQJ`, 2026-09-20). This subsection's heading names the refilling-queue ground. Its opening prose says plainly that those entries "pass the presence test as squarely as those do, and they are deferred anyway". `PL-ZM48` does not pass that test, because the text it corrects is thirteen days younger than the freeze. So it is declined on the ground on which `PL-09G9` and `PL-YFXG` are recorded above, each in a paragraph of its own and for the reason given there. Saying so is cheaper than stretching the refilling-queue argument over an entry it does not fit.

> **It is a day late because it was stranded in the half nothing reads.** The paragraph was written on `origin/claude/practical-brown-wr7u6i`, and the session on that branch opened no pull request. `PL-T2YR` recovered the two *item files* from that ref. That is the comparison `bin/docket stranded` makes: it reads item ids out of both trees. `PL-T2YR` left this prose behind, because neither half of that command looks at prose (`PL-BYMX`). `PL-2FQ5` is the deletion of the ref itself, which is the project owner's to do under `PL-K2C8`.
