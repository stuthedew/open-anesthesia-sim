---
id: PL-4Q9B
title: Ten items work around the clone being trusted as the remote and around an unrecorded set of permitted ref operations: record both
priority: P2
effort: M
status: needs-decision
classes: defect, infra
feature: generator-heads
touches: subprojects/docket/src/docket/vcs.py, .claude/skills/docket/SKILL.md, docs/worker.md, docs/items
added: 2026-09-17
root-cause-of: PL-LT77, PL-PNW6, PL-YKXQ, PL-90CJ, PL-KFWL, PL-TFWR, PL-XQRK, PL-3V6C, PL-G8TR, PL-F48B
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
