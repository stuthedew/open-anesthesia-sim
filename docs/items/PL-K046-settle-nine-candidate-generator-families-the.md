---
id: PL-K046
title: Settle nine candidate generator families the audit's two rounds disagree on, with one refuter each and a second only where the first disagrees
priority: P2
effort: S
status: ready
classes: housekeeping
feature: generator-identification
touches: docs/items
added: 2026-09-23
payoff: Nine candidate generators are either recorded or refuted, so the owner's question gets a complete answer at a tenth of the first audit's cost
verify: grep -q '^\*\*Settled' docs/items/PL-K046-settle-nine-candidate-generator-families-the.md
---

**Problem.** Settle nine candidate generator families the audit's two rounds disagree on, with one refuter each and a second only where the first disagrees

**Why these are not recorded yet.** In `PL-T7Y1`'s first round, a family
skeptic pass refuted each of these nine by majority. The round's critic
pointed out that several were refuted on grounds the count rule does not
accept, such as being spent or bounded. The second round asked a narrower
question: which items fail on one mechanism, counting spent ones. For every
family, three of three said one mechanism with three or more members. The two
rounds disagree, and the second was framed to count rather than to refute,
and it returned nine of nine. That uniformity is itself a reason to doubt it.
So the audit records none of the nine until one refuter per family has tried to
break it.

**The nine, with the members at least two round-two skeptics verified:**

1. Hard-wrapped markdown read one line at a time: `PL-X94L`, `PL-6G8T`,
   `PL-6SRZ`, `PL-RR1N`. `PL-RR1N` is already under `PL-1P5V`.
2. `tools/doc_check.py` `_resolves` asks the local filesystem rather than the
   tree it checks: `PL-F933`, `PL-MXSL`, `PL-D1NT`, `PL-H0CF`.
3. `doc_check` decides a citation from its surface shape: `PL-KJ63`,
   `PL-V13T`, `PL-316G`, `PL-YSMV`, `PL-MSFB`.
4. Session output whose only carrier is the reply: `PL-H1JD`, `PL-N638`,
   `PL-M21Q`, `PL-NGLM`.
5. A rule stored in a carrier that does not load when it must fire: 12 ids,
   led by `PL-WWDT`, `PL-3V4N`, `PL-RZKZ` and `PL-RWJD`. The widest, and the
   likeliest to be a theme rather than a mechanism.
6. Generator rank and liveness re-derived by each reader: `PL-CJ5R`,
   `PL-BBT8`, `PL-CT07`. If it holds, it belongs on `impairs-generators:`
   rather than `root-cause-of:`.
7. Tools restate docket primitives (from `PL-KVDK:69-76`): `PL-KYW3`,
   `PL-WHQS`, `PL-DPY6`. It overlaps `PL-ZJ6X`.
8. Adopted constants never replayed (`PL-KVDK`): `PL-DGP0`, `PL-W80S`,
   `PL-0HPV`, `PL-S6FL`, `PL-34BG`.
9. Conventions adopted without a migration (`PL-KVDK`): 11 ids, led by
   `PL-7RYB`, `PL-QNMM`, `PL-GL95` and `PL-2J5X`.

The full member lists and each skeptic's reason are in the workflow journal
for run `wf_5c419b9f-f8c`. That journal is session-local, so these lists are
the durable copy.

**Scale.** Two refuters per family, working independently, and a third only
where they split: eighteen to twenty-seven agents, against the 262 the audit
spent. The owner flagged the audit's size on 2026-09-23 ("That's a lot of
agents"). Later that day they asked for each question to be settled once:
"I'd rather fix it right once, then fix it twice" (project owner, 2026-09-23). One refuter, as first scoped, would let a single agent's verdict decide
whether a generator is recorded.

**Order.** Run this before the design rounds on the live heads, because it
decides how many heads the pause holds. That is this session's reading of the
owner's "get things in order now" (2026-09-23).

**Done when.** Each of the nine is recorded as a head, live or spent, with its
members, or is refuted with the reason written here.
