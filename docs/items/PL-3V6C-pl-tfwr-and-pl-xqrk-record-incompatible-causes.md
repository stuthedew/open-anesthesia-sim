---
id: PL-3V6C
title: PL-TFWR and PL-XQRK record incompatible causes for the same remote-deletion failure and both ruled out the git proxy on a field that does not record policy denials, so whichever lands first writes an unproven cause into the instructions
priority: P2
effort: S
status: ready
classes: defect, docs
feature: dev-tooling
touches: docs/items/PL-TFWR-a-session-cannot-delete-a-remote-branch-the-git.md, docs/items/PL-XQRK-a-session-cannot-delete-a-remote-branch-git.md
added: 2026-09-12
not-delegable: Establishing which cause is real means attempting a remote ref deletion from a live agent session and reading the proxy's own diagnostics at the moment it fails. Nothing in this tree can run that, and no command can prove the resulting sentence is true; what a reviewer can check is that neither brief asserts a cause the evidence does not carry.
---

**Problem.** PL-TFWR and PL-XQRK record incompatible causes for the same remote-deletion failure and both ruled out the git proxy on a field that does not record policy denials, so whichever lands first writes an unproven cause into the instructions

**Confirmed at triage, 2026-09-12.** Both items are open at `ready`, both were
measured on 2026-09-04, and they describe the same operation failing in two
mutually exclusive ways:

| | `PL-TFWR` | `PL-XQRK` |
| --- | --- | --- |
| symptom | `send-pack: unexpected disconnect`, then `Everything up-to-date`, **exit 0** | **HTTP 403** |
| cause asserted | "the deletion ref appears to be dropped on the way through" - the proxy | "it is GitHub refusing the ref deletion ... the session's token carries no `delete_ref` permission" |
| evidence offered against the other cause | `recentRelayFailures` empty | `recentRelayFailures: []` |

A push cannot both be silently swallowed and be refused with a status code, so
at most one of these is the failure this project actually meets - and they reach
opposite conclusions from the *same* observation, an empty
`recentRelayFailures`.

**That observation does not carry either conclusion.** `recentRelayFailures` is
a record of relay-level failures. A request the proxy declines on policy is not
a relay failure, so an empty list is equally consistent with the proxy refusing
the ref deletion; the container's own `/root/.ccr/README.md` lists `403` among
the proxy-side outcomes a tool should expect, beside the cut transfers that
`PL-TFWR` saw. Neither item's exoneration of the proxy is established.

**Why it matters.** Both items' declared work is writing the cause into
`CLAUDE.md`, `.claude/skills/docket/SKILL.md` and `docs/worker.md` - resident or
near-resident instructions. Whichever lands first puts an unproven mechanism in
front of every future session, and the second then either contradicts it or
quietly loses. A wrong cause is worse here than no cause: `PL-N936` records the
same `unexpected disconnect` / `Everything up-to-date` pair for **tag** pushes,
so a session told "the proxy drops deletion refs" will generalise it, and a
session told "the token lacks `delete_ref`" will not think to retry anything.
`CLAUDE.md` names a confidently wrong signal as worse than a failing one, and
this is that shape about to be written down.

**Done when.** One cause is established by observation, or neither is: both
briefs describe the symptom they measured and stop short of naming a mechanism
the evidence does not carry, and neither cites `recentRelayFailures` as proof
that the proxy was not involved.
