---
id: PL-4Q9B
title: PL-6ZQY's checkout-is-a-cache cluster has no causing item: PL-F48B decides tags after a rewrite only, and nothing records which ref operations a session is permitted
status: untriaged
feature: generator-heads
touches: docs/items
added: 2026-09-17
---

**Problem.** PL-6ZQY's checkout-is-a-cache cluster has no causing item: PL-F48B decides tags after a rewrite only, and nothing records which ref operations a session is permitted

**Why it matters.** The ephemeral clone is treated as a faithful copy of the
remote - it is not, because `git fetch` moves neither an existing tag nor a
diverged branch ref - and separately nobody wrote down which ref operations a
session is actually permitted, so procedures end in steps that report success
and do nothing. `PL-TFWR` is that exactly: exit status 0 with `Everything
up-to-date` as the last line, on a deletion that did not happen.

**Why no existing item can head it, and note this is two halves.** `PL-F48B`
heads the *cache* half and only part of it: it is `P3`/`S`, scoped to tags
after a history rewrite, and its `Done when` explicitly permits "the decision
not to is recorded here". It settles nothing about `PL-TFWR`, `PL-XQRK`,
`PL-3V6C` or `PL-G8TR`. The *permissions* half has no item at all: `PL-3V6C`
comes closest and settles one operation (remote branch deletion) rather than
the set, and `PL-XQRK` points at `PL-0XMD`, which is `done` and about HTTP
egress rather than refs.

**What the head has to decide.** Whether one point reconciles the clone against
the remote and where it sits - `vcs.fetch_remote` runs on every command and
would move tags without asking; the session-start hook runs once per container
and already does a conditional `--unshallow` - and, separately, whether the ref
operations a session's token actually permits are recorded rather than
rediscovered. Those may be one item or two; deciding that is part of the head.

**Candidate members (9, unverified).** Cache half: `PL-LT77`, `PL-PNW6`,
`PL-YKXQ`, `PL-90CJ`, `PL-KFWL`. Permissions half: `PL-TFWR`, `PL-XQRK`,
`PL-3V6C`, `PL-G8TR`. `PL-6ZQY` already flags `PL-F48B`, `PL-TFWR`, `PL-XQRK`,
`PL-YKXQ` and `PL-KFWL` as partly overtaken, so confirm those five first.

**Done when.** One item - or two, if the halves separate - poses that decision,
carries a `root-cause-of:` naming the members that survive confirmation, and
the members are re-pointed or dropped against it.

**Where this came from.** `PL-6ZQY` found six clusters under one mechanism -
*the apparatus infers a fact it could have recorded* - and `PL-VX5H` built the
way to rank one: `root-cause-of:` on the item that causes the cluster, which
`docket next` then offers above every band but `P0`. Marking the six on
2026-09-17 found that only two have a causing item in the store. `PL-BHVM` and
`PL-L4YG` carry the field now; this cluster is one of the four that has nobody
to carry it, so it stays flat in `P2` exactly as `PL-VX5H` says a generator
does.

**How the membership below was arrived at, and what it is worth.** A 2026-09-17
pass read every open item's front matter, and each candidate's title and one
quoted sentence from its brief. That is enough to say these are plausibly one
problem and **not** enough to write the `root-cause-of:` line: the field is a
recorded fact rather than an inference, which is the whole of why it outranks a
`safety`-classed `P1`. Confirm each against its brief before writing it. This
is `PL-6ZQY`'s own caveat about its map, arriving at the next step.
