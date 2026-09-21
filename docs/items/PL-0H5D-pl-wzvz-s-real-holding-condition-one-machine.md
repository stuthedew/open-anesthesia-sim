---
id: PL-0H5D
title: PL-WZVZ's real holding condition - one machine profile and no chooser - is unexpressible in blocked-by, so every reader of that field will report it promotable the moment PL-TH35 and PL-R1WQ close, as PL-8G48 already found once
priority: P2
effort: S
status: done
feature: wzvz-deferral-integrity
touches: docs/items, subprojects/docket/src/docket
added: 2026-09-21
closed: 2026-09-21
payoff: stops PL-WZVZ arriving at P1 and unbuildable in front of bin/docket next the moment its proxy blockers close in v0.6.0, which is the same false-ready PL-8G48 corrected by hand on 2026-09-20
verify: python3 tools/doc_check.py check && grep -qE '^blocked-by: (PL-[A-Z0-9]{4}, ){2,}PL-[A-Z0-9]{4}' docs/items/PL-WZVZ-make-an-inter-machine-difference-attributable.md
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

## Ratified, 2026-09-21

**Fix 2 — give the condition an item, and block on that** (project owner,
2026-09-21, ratified, over a `blocked-on:` tree predicate evaluated by
`bin/docket check`). What it was chosen over costs a new store field on the gate
every command reads, for a population of one known case; what it buys is that
`blocked-by` carries the truth with no new mechanism, and the unscheduled state
becomes visible in the queue instead of invisible in `ROADMAP.md` prose.

**Two things settled in the same round.**

1. **The deferral itself stands.** `PL-S5Q9`'s disposition — `PL-WZVZ` clears in
   Gate 2 and v0.5.0 ships without it — was re-examined against the tree on
   2026-09-21 at the project owner's question and confirmed, over pulling
   `PL-1FT6`, `PL-R1WQ` and `PL-TH35` forward into v0.5.0 to unblock it.
2. **Pulling those three forward would not have unblocked it**, which is the
   finding this item exists to make legible and which was in no file before
   today. `src/anesthesia_sim/data/machines/` holds one profile, so every
   `Done when.` clause of `PL-WZVZ` naming a *second* machine is unreachable
   whatever happens to its `blocked-by`. The cost side was counted too: the
   three are v0.6.0 `Required scope` items 1, 3, 4 and 5, and item 5 specifies
   the View contract as written *with* the area system and validated against two
   existing views, so `PL-HJPY` and the adapter `PL-W9P6` come with them.

**What to file, and the `blocked-by` each new item carries.** Two items, whose
ids are then added to the `blocked-by` field already on `PL-WZVZ`:

- **A second machine profile** under `src/anesthesia_sim/data/machines/`.
  Its own `blocked-by` is `PL-QW19, PL-2FZ9`: the first because
  `default_fresh_gas_flow_l_min` is a required field no manufacturer publishes,
  so a real profile must invent an unsourced number or cannot be written; the
  second because without it a second profile is not reachable by a run at all.
- **A surface that selects between machines.** Planned-milestone item 40
  deliberately ships a second profile loadable and refused where inadmissible
  *with no chooser*, and planned-milestone item 1 keeps the interlock baseline,
  so nothing schedules one. It is also itself a new display surface, so its own
  `blocked-by` inherits item 34's rule: `PL-TH35, PL-R1WQ`.

Both are specific changes rather than features wanted but not yet ready, which
is the side of `CLAUDE.md`'s intent-routing rule that says write the item now.

**Done when.** The two items above exist, the `blocked-by` field on `PL-WZVZ`
lists their ids alongside the two it already carries, and closing the View
contract and the view registry therefore leaves that item `blocked` rather than
reporting it promotable.
