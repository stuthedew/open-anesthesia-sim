---
id: PL-0H5D
title: PL-WZVZ's real holding condition - one machine profile and no chooser - is unexpressible in blocked-by, so every reader of that field will report it promotable the moment PL-TH35 and PL-R1WQ close, as PL-8G48 already found once
status: untriaged
feature: wzvz-deferral-integrity
touches: docs/items, subprojects/docket/src/docket
added: 2026-09-21
---

**Problem.** PL-WZVZ's real holding condition - one machine profile and no chooser - is unexpressible in blocked-by, so every reader of that field will report it promotable the moment PL-TH35 and PL-R1WQ close, as PL-8G48 already found once

**Why it matters.** `PL-WZVZ` is held by two conditions and only one of them is
in a field. Its `blocked-by: PL-TH35, PL-R1WQ` records the display-surface rule
(planned-milestone item 34: no new display surface before the View contract and
the view registry). Its *other* condition — `src/anesthesia_sim/data/machines/`
holds one profile and there is no selection surface, so there is nothing to
compare — lives in the item's own prose and in `ROADMAP.md`'s Gate 1 deferral,
and in no field any command reads. That omission is deliberate and correct:
naming a version would assert a placement the roadmap has not made, and no open
item delivers a second profile or a chooser, so there is no id to name either.
Planned-milestone item 40 keeps it that way by design — a second profile
*loadable* and refused where inadmissible, with no chooser and no displayed
value changing.

**The consequence is dated.** When `PL-TH35` and `PL-R1WQ` close inside v0.6.0,
`blocked-by` empties and every reader of it — `bin/docket check`'s promote
advisory, `wave`'s gate count, `next`'s ranking — reports `PL-WZVZ` startable.
Promoting it is what ends the `anticipated` exemption (`PL-P909`), so it
arrives at `P1`, `safety`-classed, at the front of `bin/docket next`, and its
`Done when.` clauses ("selecting between machines", "a comparison of two runs on
different machines") cannot be met by any work in the tree.

**It has already happened once, on this exact item.** On 2026-09-20 `PL-FG9D`
and `PL-4DCG` closed, `bin/docket check` reported `PL-WZVZ` ready to promote,
and `PL-8G48` found it unbuildable by reading against the tree — then repaired
it by substituting `PL-TH35` and `PL-R1WQ` as proxy blockers. That repair is
what expires in v0.6.0. Nothing caught the first instance but a session
happening to look; nothing is positioned to catch the second.

**Not a generator, on the count.** The adjacent mechanism — an item left
`blocked` after its blockers close — has three items (`PL-JFQ3`, `PL-CHQY`,
`PL-8G48`, all `done`) and is instrumented: `check`'s promote advisory is what
finds those. This is the inverse case, where the advisory fires correctly and
its answer is wrong because the holding condition is unexpressible. That has one
instance (`PL-8G48`'s read against the tree) plus this predicted one. One and
one is not three, so it is filed as an ordinary item; a third instance makes the
count and the claim should be re-examined then.

**Two candidate fixes, and the second is the recommendation.**

1. *Express tree conditions in a field.* A `blocked-on:` taking a predicate over
   the tree — "more than one profile under `src/anesthesia_sim/data/machines/`"
   — which `check` evaluates. Decidable, and it would fire here. It is also a new
   store field on the gate every command reads, for a population of one known
   case; `CLAUDE.md`'s "the gate is whether it will genuinely run again" is not
   obviously met.
2. *Give the condition an item, and block on that.* File the missing work — a
   second machine profile, and a surface that selects between them — as items,
   even if neither is scheduled by any milestone section, and have `PL-WZVZ`
   name them. `blocked-by` then carries the truth with no new mechanism, and the
   unscheduled state becomes visible in the queue instead of invisible in prose.
   The cost is items nobody can work yet, which is what
   `CLAUDE.md`'s intent-routing rule warns against — except that this is a
   *specific change*, not a feature wanted but not yet ready, which is the side
   of that rule that says write the item now. `PL-QW19` is evidence the first
   half is already a real, scoped problem rather than a placeholder: the first
   real machine profile cannot be written at all until
   `default_fresh_gas_flow_l_min` has a source.

**Done when.** The condition that actually holds `PL-WZVZ` is recorded somewhere
`bin/docket check` reads, so that closing `PL-TH35` and `PL-R1WQ` does not
report it promotable; and the route chosen is written down beside the choice, so
the next unexpressible condition is not re-argued from scratch.
