---
id: PL-4Q9B
title: Ten items work around the clone being trusted as the remote and around an unrecorded set of permitted ref operations: record both
priority: P2
effort: M
status: done
classes: defect, infra
feature: generator-heads
milestone: v0.4.28
touches: subprojects/docket/src/docket/vcs.py, .claude/skills/docket/SKILL.md, docs/worker.md, docs/items
added: 2026-09-17
closed: 2026-09-19
pr: 685
verify: python3 tools/doc_check.py check && grep -q 'Ref operations a session cannot perform' docs/worker.md
root-cause-of: PL-LT77, PL-PNW6, PL-YKXQ, PL-90CJ, PL-KFWL, PL-TFWR, PL-XQRK, PL-3V6C, PL-G8TR, PL-F48B
misread: The remote's current refs and tags, and whether the clone's local copies still match them
---

**Problem.** Two facts nobody recorded, and ten open items between them. The
ephemeral clone is treated as a faithful copy of the remote - it is not,
because `git fetch` moves neither an existing tag nor a diverged branch ref -
and separately nobody wrote down which ref operations a session is actually
permitted, so procedures end in steps that report success and do nothing.

**Why it matters.** Both halves fail silently, which is the expensive
direction. `git fetch --tags` does not delete a tag the remote dropped, so
`doc_check` goes on failing in every checkout that already had it (`PL-LT77`);
a session ran `git checkout main` after a merge and landed four hundred merges
out of date (`PL-YKXQ`); the release handover's own `git fetch origin main`
exits zero and prints nothing while leaving a withdrawn tag in place
(`PL-PNW6`). On the permissions side `git push origin --delete` ends on
`Everything up-to-date` having deleted nothing (`PL-TFWR`), which is the worst
shape available: a step that looks done.

The self-generating half is that each new command a procedure reaches for is a
new instance. `PL-3V6C` is the cluster reporting itself - `PL-TFWR` and
`PL-XQRK` record *incompatible* causes for one failure, and whichever lands
first writes an unproven mechanism into `CLAUDE.md`, the `docket` skill and
`docs/worker.md`, the near-resident files every future session reads.

**Why this item is the head, and no member is.** Confirmed against the store on
2026-09-18. `PL-F48B` heads the cache half and only part of it: it is `P3`/`S`,
scoped to tags after a history rewrite, and its own `Done when` explicitly
permits "the decision not to is recorded here". It settles nothing about
`PL-TFWR`, `PL-XQRK`, `PL-3V6C` or `PL-G8TR`. The permissions half has no item
at all - `PL-3V6C` comes closest and settles one operation (remote branch
deletion) rather than the set, and `PL-XQRK` points at `PL-0XMD`, which is
`done` and about HTTP egress rather than refs.

**Decision needed.** Two questions, and deciding whether they are one
item or two is part of the head:

- **Reconciling the clone against the remote**: whether one point does it and
  where it sits. `vcs.fetch_remote` runs on every command and would move tags
  without asking; the session-start hook runs once per container and already
  does a conditional `--unshallow`. `CLAUDE.md`'s stale-ref rule and the
  `--prune` prohibition constrain the answer, because a stale
  `origin/<branch>` can be the only surviving copy of a captured item.
- **Recording the permitted set**: which ref operations a session's token
  actually allows - tag push, ref deletion, force update - established once and
  written where a procedure is composed, rather than rediscovered by each
  session that writes a step that silently does nothing.

**The items this explains (10, confirmed 2026-09-18 against each brief).**
Cache half: `PL-LT77`, `PL-PNW6`, `PL-YKXQ`, `PL-90CJ`, `PL-F48B`. Permissions
half: `PL-TFWR`, `PL-XQRK`, `PL-3V6C`, `PL-G8TR`, `PL-KFWL`.

Nine are the 2026-09-17 candidate list, each re-read and still open. `PL-F48B`
is added as a member: the pass named it only as the rejected partial head, and
it is the cache half's clearest instance. `PL-KFWL` sits on the permissions
side rather than the cache side - the `v0.4.8` tag is wrong on the *remote*,
and what makes it standing friction rather than a five-minute fix is that no
session can move it.

`PL-6ZQY` flags `PL-F48B`, `PL-TFWR`, `PL-XQRK`, `PL-YKXQ` and `PL-KFWL` as
partly overtaken, so a session working this head should confirm what is left of
those five before acting on their briefs. Membership is unaffected: an
overtaken brief still names an instance the mechanism produced.

**Done when.** Both questions above are answered and the answers are recorded
where a procedure is composed rather than where a failure was met - the
permitted set as a fact a session can read, the reconciliation point named in
one place - and the ten members are re-pointed at the decision or dropped
against it.

**Where this came from.** `PL-6ZQY` found six clusters under one mechanism -
*the apparatus infers a fact it could have recorded* - and `PL-VX5H` built the
way to rank one: `root-cause-of:` on the item that causes the cluster, which
`docket next` then offers above every band but `P0`. Marking the six on
2026-09-17 found only two with a causing item in the store (`PL-BHVM`,
`PL-L4YG`); this item was filed to record that this cluster had none. On
2026-09-18 it became the head itself rather than a tracker of one, which is the
cheaper of the two endings its own `Done when` offered.

**Answered 2026-09-19, and the answer is that this cluster is not one mechanism.**
The framing was dropped on the session's recommendation (project owner, 2026-09-19, ratified), chosen over
building a central reconciliation point in `vcs.fetch_remote` and a single new
permitted-set fact beside it.

**Question 1 - is there one reconciliation point, and where? No, and the
evidence is against building one.** The only place every command passes through
is `vcs.fetch_remote`, which runs `git fetch --quiet origin`: no `--tags`, no
`--prune`, both deliberate. Neither omission can be reversed there. Forcing
tags on every command moves local tags without asking, which `PL-F48B` (repair
tags after a history rewrite) already argued against and which is now closed on
that reasoning; pruning branches is refused outright by
`.claude/hooks/no-prune-guard.sh`, because a stale `origin/<branch>` can be the
only surviving copy of a captured item. What is left are four unrelated
staleness conditions that fire at four different moments and want four cheap
local fixes - the session-start hook for a diverged branch ref (`PL-YKXQ`),
`doc_check`'s own message for a tag withdrawn on origin (`PL-LT77`), the
release handover for a re-used version number (`PL-PNW6`), and the existing
rewrite-recovery prose for tags after a force-push (`PL-F48B`). A single
reconciler would have to be all four and is permitted to be none of them.

**Measured 2026-09-19, which is what closed `PL-F48B`:** all 54 tags in this checkout
are reachable from `origin/main`, and every local tag object is byte-identical
to the remote's. The condition that item was filed against is not present here,
and the recovery prose `bin/docket branch` prints fires exactly where it is.

**Question 2 - record the permitted set.** Done, in `docs/worker.md`
§ "Ref operations a session cannot perform": a two-row table of what a session
cannot do (push a tag, delete a remote branch), what it sees when it tries,
and whose the operation is. Placed there rather than in `CLAUDE.md` because the
routing ladder puts a document that loads on demand below a check and above
resident prose, and this is read at the moment a cleanup or a release handover
is being composed rather than before a first write.

**The cause is deliberately absent from it, and that is the load-bearing
part.** `PL-3V6C` is right that the two measurements are mutually exclusive and
that neither exonerates the proxy. Settling it needs a live remote deletion read
against the proxy's diagnostics as it fails - destructive and outward-facing, so
this session did not run it. The block says what happens and stops.

**A guard hook was considered and refused.** `no-prune-guard.sh` shows the
shape, and intercepting a tag push or a remote deletion would convert a silent
no-op into an explicit refusal at the moment of the attempt. Against it: the
operation already fails, so the guard buys information rather than safety;
`CLAUDE.md`'s gate for a new mechanism is that it will genuinely run again, and
a session attempts these rarely; and it would block the one experiment that
settles `PL-3V6C`. Prose was the right tier here.

**The ten members, re-pointed.** Closed with this: `PL-XQRK` (the worker.md
line - this block is it), `PL-3V6C` (both briefs corrected), `PL-F48B` (no
automation, on the measurement above). Dropped: `PL-TFWR`, superseded by the
same block. Answered and moved to `ready` with a command that was run:
`PL-LT77`, `PL-PNW6`. Left standing as ordinary items on their own merits, none
of them blocked on this: `PL-YKXQ`, `PL-90CJ`, `PL-G8TR`, `PL-KFWL`.

**What falsifies the "no central point" answer.** A fifth staleness condition
arriving that the four local fixes cannot each absorb, or a change making
`fetch_remote` safe to force tags in - neither of which is on the roadmap.
