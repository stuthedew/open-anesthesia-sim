---
id: PL-K046
title: Settle nine candidate generator families the audit's two rounds disagree on, with one refuter each and a second only where the first disagrees
priority: P2
effort: S
status: done
classes: housekeeping
feature: generator-identification
touches: docs/items
added: 2026-09-23
closed: 2026-10-18
pr: 1591
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

**Settled 2026-10-18: two families are new heads, both spent; four belong to
heads already recorded; three are refuted.** Two refuters checked each family
independently. Each was told to try to break the claim and to read the 66
existing heads' `misread:` lines first. A third refuter decided where the two
disagreed, on families 4, 5 and 9, which makes 21 agents in all. Every member
was closed by then except `PL-QNMM` and `PL-GL95`, so no verdict below changes
what `docket next` offers.

1. **Hard-wrapped Markdown read one line at a time: belongs to `PL-R417`**
   (2 of 2). Its fact, "Where one statement ends, in a format that lets a
   statement continue across physical lines", covers the family, and its
   mechanism table already holds `PL-6SRZ` and `PL-RR1N`. `PL-X94L` was fixed
   in #451 before `PL-R417` existed, so it was never listed, and is added to
   `PL-R417`'s `root-cause-of:`. `PL-6G8T` stays with `PL-GPJ7`: its reader
   took a line opening with a heading's words for the heading, which is not a
   statement read as ending too early.
2. **doc_check asks the local disk rather than the tree: a new head on
   `PL-H0CF`, spent** (2 of 2). `PL-F933`, `PL-MXSL`, `PL-D1NT` and `PL-H0CF`
   each took "this path exists on the disk running the check" as "this path is
   in the repository". The ignored directories `.venv/` and `out/` passed in a
   session and failed in CI, and `/root/...` could be read by root and not by
   CI's runner. No head's `misread:` stated that fact. It is spent because
   `_covered_by_gitignore` (#593) and `_repository_paths` (#1300) now give one
   verdict everywhere. Both refuters noted the weak side: the four items are two
   defects, each filed twice. `PL-0M7L` is left out, because its fault was a
   glob that could not be parsed.
3. **doc_check decides a citation from its surface shape: belongs to
   `PL-GPJ7`** (2 of 2). Its fact, "Whether a sentence makes the claim a hard
   gate checks, when the gate recognises it by wording", is this family's fact
   for every gate, not only `doc_check`. `PL-KJ63`, `PL-V13T` and `PL-316G`
   predate `PL-GPJ7` and are added to its `root-cause-of:`. `PL-YSMV` was
   already there. `PL-MSFB` stays with `PL-G424`, because it was prose that
   went stale, not a citation misread.
4. **A session output whose only carrier is the reply: a new head on
   `PL-H1JD`, spent** (2 of 3). `PL-H1JD`, `PL-N638`, `PL-M21Q` and `PL-NGLM`
   each treated the reply as something a later session could read: a tag
   request, a feature grouping, a recommendation and ten sweep verdicts. The
   refuter against it argued that rule 14 already recorded the fact before the
   last three were filed. The third refuter found that rule 14 then covered
   only a closing-block line sent to `bin/docket new`. `PL-M21Q`'s and
   `PL-NGLM`'s own briefs read that rule and found it did not cover them. It is
   spent, not live: no member has been filed since 2026-09-19, and a search of
   every item filed after 2026-09-20 found none of this shape.
5. **A rule stored in a carrier that does not load when it must fire:
   refuted** (2 of 3). The members misjudged different things: the moment
   their own rule fires (`PL-WWDT`, `PL-3V4N`, `PL-G40Z`), an incomplete
   `paths:` list (`PL-RZKZ`, `PL-3YRT`), a rule placed in `docs/worker.md`
   (`PL-5DN3`, `PL-RWJD`), and what compaction restores (`PL-384P`). The one
   refuter for a head proposed a narrower fact, that a path-scoped rule loads
   only on a read. The third refuter found that `CLAUDE.md` stated that fact
   from #116 (2026-08-31), before any member was filed, and that each member's
   brief quotes it correctly. `PL-BTSW` records a breach of the rule that
   `PL-3V4N` misplaced, so it is not a second instance. Which moment a rule
   must fire at is a separate judgment for each rule, and `CLAUDE.md`'s
   routing question is already where that judgment is made.
6. **Generator rank and liveness re-derived by each reader: belongs to
   `PL-Q4DF`** (2 of 2). Its fact is "Whether a generator-tier item holds its
   rank now, passes it to its blockers, or ranks nowhere", and
   `plan.tier_standings` is now the one function its readers ask. `PL-CJ5R` is added
   to its `root-cause-of:`. `PL-CT07` is not: one refuter held that it misread
   whether any open item carries `generator: live`, which is the record rather
   than the rank, and its own brief calls it a one-off.
7. **Tools restate docket primitives: belongs to existing heads** (2 of 2).
   `PL-KYW3` and `PL-DPY6` are already under `PL-ZJ6X`, "Which strings are
   valid item ids". `PL-WHQS` restated `CLOSED_STATUSES` in four places, which
   is "Which spelling of a repeated predicate is the answer". It is added to
   `PL-KGYT`'s `root-cause-of:`, which already holds `PL-DHGC`, the same
   closed-status spelling in `tools/item_reads.py`.
8. **Adopted constants never replayed: refuted** (2 of 2). The five members
   misread five different things. `PL-0HPV` quoted a cost from before
   `--verify-base`. `PL-W80S` measured the wrong quantity. `PL-DGP0` was a
   floor set wrongly and fixed in the same branch. `PL-S6FL` was an off-by-one
   from the start. `PL-34BG` was a write that nothing could undo. `PL-0HPV`
   also already heads a different fact.
9. **Conventions adopted without a migration: refuted** (2 of 3). The wide
   family spans different conventions, most of them under heads of their own.
   The narrow trio `PL-7RYB`, `PL-QNMM` and `PL-GL95` is one planned
   migration in three pieces. `PL-XWH4` filed `PL-QNMM` in the commit that
   introduced the ratified-or-specified notation, and `PL-7RYB`'s fix filed
   `PL-GL95`. No reader misread a marker. `PL-1YT5` and `PL-DLMM` each wrote a
   marker after the rule existed, which is a different fact.

**Two leads below the count, recorded so a later check can find them.**
`PL-DLMM` and `PL-7PWM` may share a fact: a decision record owed after the
merge that the owner's answer arrives behind. `PL-1YT5` and `PL-DLMM` each
recorded a ratified decision in the wrong form when it was written. Each pair
has two members, one short of a generator.
