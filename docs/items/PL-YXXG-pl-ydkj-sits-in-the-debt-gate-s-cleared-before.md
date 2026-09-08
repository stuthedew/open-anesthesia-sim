---
id: PL-YXXG
title: PL-YDKJ sits in the debt gate's 'cleared before v0.5.0 begins' group, but PL-2FM6's brief says decide it after PL-2FM6 lands and PL-2FM6 is v0.5.0's own scope
priority: P3
effort: S
status: done
classes: planning, docs
closed: 2026-09-08
verify: grep -q '^blocked-by: PL-2FM6$' docs/items/PL-YDKJ-*.md && grep -qF 'Cleared by v0.5.0 itself — 10 entries' ROADMAP.md && grep -qF 'product lane — 39 entries' ROADMAP.md
feature: teachable-case
touches: ROADMAP.md, docs/items
added: 2026-09-08
---

**Problem.** Gate 1 places `PL-YDKJ` (decide whether the chart should keep
patching one control per plotted point) in **"Cleared before v0.5.0 begins,
the product lane"**, so a session working the gate is expected to answer it
now. Two other documents say not to:

- `PL-2FM6`'s brief (delete `RunHistory` and draw the chart from the
  closed-form sampler): "`PL-YDKJ` ... is the open decision this interacts
  with, and it should be decided **after** this lands rather than before -
  the point-movement rate is its main input, and this item changes it."
  `PL-2FM6` is in **"Cleared by v0.5.0 itself"**, so it lands after the gate.
- `PL-YDKJ`'s own Decision needed: "Answer it only when a scale, a trace
  count or a render cadence is actually blocked by the ceiling; as of
  2026-09-04 nothing is."

So the gate asks for a decision whose stated main input arrives one release
later, and whose own trigger condition is not met.

**Why it matters.** `PL-YDKJ` is a *sizing* question - its own closing note
reduces it to `2 * P^2 * T / window_seconds`, in the drawn point count `P` and
how often those points change. `PL-2FM6` changes both halves: it evaluates
columns on an absolute grid anchored at `t = 0` so a following window reuses
all but its newest column, and it adds a column at every control event. A
decision taken now is taken against a point-movement rate the next item
replaces, which is the one failure mode `PL-2FM6` names.

This is the shape v0.4.1 already cleared once - "three contradictions inside
the next release's own briefs ... each of which would have stopped a worker on
day one", including the `PL-GS5X`/`PL-X9KD` deadlock. Nothing catches it
automatically: `PL-YDKJ` carries no `blocked-by`, so the undeclared-prose-
prerequisite advisory has no edge to check, and `docket check` reports clean.

**Options.**

1. Move `PL-YDKJ` from "Cleared before v0.5.0 begins, the product lane" to
   "Cleared by v0.5.0 itself" and give it `blocked-by: PL-2FM6`. The gate
   total is unchanged at 132; only which side of "before v0.5.0 begins" it
   sits on moves. This is the disposition the two briefs already argue for.
2. Decide it now as option 1 of `PL-YDKJ` itself ("Accept it. Document the
   ceiling and stop tuning the selection. Costs nothing now."), which clears
   the gate entry honestly but records a sizing decision against a rate
   `PL-2FM6` is about to change.
3. Leave it and let the worker who reaches it re-derive this - the outcome
   this item exists to prevent.

Moving an entry between the frozen gate's groups is the project owner's call
(the freeze is theirs, ROADMAP.md, 2026-09-06), which is why this is an item
rather than an edit.

**Done when.** `ROADMAP.md`'s Gate 1 and `PL-YDKJ`'s frontmatter agree with
`PL-2FM6`'s brief on when `PL-YDKJ` is answered, and the reasoning is recorded
wherever the disagreement is resolved.

**Closed 2026-09-08, option 1** (project owner, same day). `PL-YDKJ`'s gate entry
moved from "Cleared before v0.5.0 begins, the product lane" (now 39 entries) to
"Cleared by v0.5.0 itself" (now 10), and the item gained `blocked-by: PL-2FM6`
with `status: blocked`, so the edge is machine-readable rather than prose two
briefs apart. One departure from the recommendation as written: membership of
that group otherwise means "appears in v0.5.0's Required scope", and `PL-YDKJ`
is a `P3` whose own trigger condition is unmet, so it would not survive there as
a nineteenth Required-scope entry. The group therefore carries a note saying
`PL-YDKJ` is in it as a consequence of `PL-2FM6` rather than as scope of its
own; Required scope stays at eighteen items and the gate total at 132.
