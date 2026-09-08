---
id: PL-MKFG
title: PL-B9PY sits at needs-decision though v0.5.0's scoping on 2026-09-06 answered the rendering decision its own brief named as the promotion condition, so docket next cannot rank it and PL-8PSW stays blocked behind it
priority: P2
effort: S
status: done
classes: defect
touches: docs/items/PL-B9PY-decompose-simulationview-so-two-runs-can-be.md
added: 2026-09-08
closed: 2026-09-08
pr: 478
verify: bin/docket check && grep -q '^status: ready$' docs/items/PL-B9PY-decompose-simulationview-so-two-runs-can-be.md
---

**Problem.** `PL-B9PY` (decompose `SimulationView` so two runs can be rendered
at once) sat at `needs-decision` though v0.5.0's scoping on 2026-09-06 answered
the rendering decision its own brief named as the promotion condition, so
`bin/docket next` could not rank it and `PL-8PSW` (overlay two branches on one
time axis) stayed blocked behind it.

The brief stated its own gate in prose: it "becomes `ready` the moment that
milestone has a goal, required scope and definition of done", and named the
decision it was waiting on — what v0.5.0's side-by-side comparison renders.
Both were satisfied on 2026-09-06. `ROADMAP.md`'s timeline row 5 records the
milestone as **scoped 2026-09-06**, the section below it carries a goal,
required scope, definition of done and an out-of-scope list, and the rendering
question is answered inside that Required scope by the `PL-8PSW` bullet: two
branches overlaid on one time axis, stacked panels considered and rejected the
same day, the channel assignment settled on 2026-09-07 by `PL-HLD5`.

**Why it matters.** Two days of the item being unrankable, and the cost is not
the delay. `bin/docket next product` returned `PL-WT07`, `PL-ZP7Z` and
`PL-VZL0` while an item in v0.5.0's own Required scope — the ninth of eighteen
— was invisible to it. `PL-8PSW` carries `blocked-by: PL-TFX5, PL-B9PY`, so the
release's headline feature was waiting on a status field rather than on work.
Nothing reported this: `docket check` cannot read a promotion condition written
in prose, and the one advisory that would have fired on the first blocker —
"every blocker has closed" — was deliberately unavailable here, because
`blocked-by` was empty by design while the second blocker was a milestone.

**Where.** `docs/items/PL-B9PY-decompose-simulationview-so-two-runs-can-be.md`
alone. The frontmatter (`status`, plus the `feature` and `verify` a `ready`
item owes) and the four sections written while the item was blocked: the
blocked-on-two-things paragraph, the `needs-decision` justification, the plan
placement, and the **Decision needed.** heading, which is now a decision made.

**Not simply flipping the field.** The identical promotion was attempted and
reverted on 2026-09-03, when `PL-WB0X` closed and the "every blocker has
closed" advisory fired against a field that could not see the second blocker.
Repeating that on a session's own judgment would set the precedent the revert
was meant to remove, so the promotion was put to the project owner as a
decision and taken on their approval, 2026-09-08.

**Done when.** `PL-B9PY` is `ready`, carries the `feature` and `verify` that
status requires, and its brief records the decision as made rather than
needed — with the reverted 2026-09-03 promotion kept, since the distinction
between that attempt and this one is the whole reason the item is safe to
promote now.

**Found.** 2026-09-08, answering the project owner's question about whether
`simulation_view.py` has a maintainability plan. It has one — `PL-WB0X` closed
2026-09-03, `PL-B9PY` is stage 3 — and reading the plan is what surfaced that
its second stage was parked at a status two days out of date.

**The recurrence is `PL-W8XP`'s** (an item blocked on a milestone being scoped
cannot say so: `blocked-by` only names items), which is `ready` and taken up in
the same session. This item is the instance; that one is the representation
that would have let the store say it.
