---
id: PL-V1Y7
title: ROADMAP.md schedules break-out into a second window as v0.7.0, the milestone right after v0.6.0, but the project owner wants it as an eventual to-do rather than soon
priority: P2
effort: M
status: ready
classes: planning
feature: interface-areas
touches: ROADMAP.md, docs/MODEL.md, docs/ARCHITECTURE.md, docs/interface-provenance.md, docs/WORKING_NOTES.md, docs/items/PL-904Y-split-the-whole-interface-visibility-predicate.md, docs/items/PL-HJPY-pl-c842-s-layoutmodel-has-no-representation-for.md, docs/items/PL-L6QR-re-run-the-area-model-queue-audit-when-roadmap.md, docs/items/PL-M3X6-add-required-scope-entry-20-to-v0-6-0-every.md, docs/items/PL-W54S-decide-what-a-broken-out-top-level-window-owes.md, docs/items/PL-WZVZ-make-an-inter-machine-difference-attributable.md, docs/items/PL-Y04W-build-break-out-an-area-taken-into-its-own-top.md
added: 2026-09-26
payoff: The release after v0.6.0 becomes the schematic rather than a second-window release the owner wants only eventually, and Gate 3 no longer inherits break-out's L build item as debt to clear first.
verify: ! grep -qF -- '— the second screen**' ROADMAP.md && ! grep -qF -- '**v0.9.0 —' ROADMAP.md && grep -qF '*Break-out unscheduled' ROADMAP.md && grep -q '^status: dropped' docs/items/PL-Y04W-build-break-out-an-area-taken-into-its-own-top.md
---

**Problem.** ROADMAP.md schedules break-out into a second window as v0.7.0, the milestone right after v0.6.0, but the project owner wants it as an eventual to-do rather than soon

**Why it matters.** § "The timeline" is the order the project works in, and
every reader of the plan takes a row as intent to build it next: `bin/docket
wave` reserves its number, the session digest's plan line reads it, and a
session scoping the milestone after v0.6.0 would scope break-out. It also puts
the schematic and multi-substance a release further off than the owner's
priorities place them, and Gate 3 would freeze with `PL-Y04W`, break-out's
`L` build item, on its list as debt to clear before the next milestone begins.

**Reproduced 2026-09-26**, before any edit: `grep -nF -- '— the second
screen**' ROADMAP.md` prints the timeline row at line 458, and `bin/docket wave`
prints `Reserved  0.6.0, 0.7.0, 0.8.0, 0.9.0 - spent by ROADMAP.md`.

**Decided (project owner, 2026-09-26).** Break-out - an Area taken into its own
top-level window - is wanted eventually and not soon. In their words: "This is
something I don't want to rule out doing eventually. Not something that needs
done soon. ... More just the eventual to-do type of thing." Their own words, so
specified rather than ratified.

**What that makes true**, by `.claude/skills/docket/modes/ideas.md`'s routing,
where "I want this feature eventually" is one line of intent in § "Planned
milestones" and no items. The session that took the decision recommends:

1. Timeline row 9, "v0.7.0 - the second screen", comes off the timeline.
   Break-out stays in planned-milestone item 34 as its unscheduled second half.
2. What followed moves up one, as the 2026-09-16 renumbering did in the other
   direction: the interface pass `v0.7.x` becomes `v0.6.x`, the schematic
   `v0.8.0` becomes `v0.7.0`, multi-substance and nitrous oxide `v0.9.0` becomes
   `v0.8.0`. Gate 3's and Gate 4's rows then read true as written; Gate 5 goes.
3. v0.6.0 keeps both of its reservations unchanged: Required scope entry 1's
   window set in the saved layout root (`PL-HJPY`) and entry 7's per-window
   shape of the unconditional region (`PL-W54S`). They are what "not ruling it
   out" costs. Without them break-out later is a schema migration against every
   Workspace a learner has saved, and entry 7's tiering also serves the
   intravenous agents (`PL-NWTM`). Only the sentences naming v0.7.0 as their
   consumer change: entry 7's last sentence, the break-out bullet under
   "Explicitly out of scope for v0.6.0", and the `v0.7.x` row's placement
   argument.
4. `PL-Y04W` (build break-out; `safety`, `anticipated`; `blocked-by: v0.7.0`)
   would unblock wrongly once the schematic takes v0.7.0. Recommended: drop it
   with a reason, because an eventual feature is intent rather than an `L`
   item by the same routing, and have item 34 cite it for its Qt
   transient-parent measurement. The requirement it enforces stays in
   `docs/MODEL.md` § "Minimum displayed outputs" -> "What this list requires
   once the layout is the reader's". Its hazard is not live: nothing creates a
   second window.
5. `docs/MODEL.md`'s sentence that item 34 builds break-out "in v0.7.0", and
   the live references elsewhere - on 2026-09-26, four other documents and five
   open items named v0.7.0 and four open items "the second screen". Closed
   briefs are records.

**When.** Before v0.6.0 ships: Gate 3 freezes then, and would take `PL-Y04W`
onto its list.

**Done when.** `ROADMAP.md`'s timeline carries no break-out row and item 34
records break-out as unscheduled; `bin/docket wave` reserves no version for it;
no open item waits on a version for break-out.
