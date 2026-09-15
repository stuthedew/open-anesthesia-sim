---
id: PL-WLWY
title: docs/MODEL.md's Minimum displayed outputs assumes one fixed layout, so planned-milestone item 34's removable areas would let a learner delete the readouts that are the stated safety floor for hiding a chart trace
status: untriaged
added: 2026-09-15
---

**Problem.** docs/MODEL.md's Minimum displayed outputs assumes one fixed layout, so planned-milestone item 34's removable areas would let a learner delete the readouts that are the stated safety floor for hiding a chart trace

**Why it matters.** This is the central safety-critical design problem under
planned-milestone item 34 (Blender-style window management), and nothing
records it today. `docs/MODEL.md` § "Minimum displayed outputs" is written
against an application with one layout. It divides the display in two: the
**numeric readouts**, which must carry all six compartment concentrations and
are not the reader's to remove, and the **chart's compartment traces**, which
are. The sentence that makes hiding a trace safe is "a required value must not
leave the display with the curve that draws it" - the readouts are the floor
the chart's show/hide control stands on, and `PL-16ZC` was closed on exactly
that reasoning.

Item 34's areas are removable by construction. A learner who deletes or
replaces the readout area has removed the floor, and every show/hide
affordance the document permits becomes unsafe at once - not by a defect in
the chart, but because the guarantee it relies on was in a different area.
Under `CLAUDE.md`'s clinical-output standard a required value absent from the
display is the same failure as a covered one, which item 34's own tiling
argument already names.

**The shape of the fix, and the precedent is in the reference implementation
the owner named.** Blender's own window system exempts two regions from the
area system entirely: the Topbar and the Statusbar are not areas, cannot be
split, joined or closed, and persist across every workspace. That is the
cheapest available answer here and it keeps the layout system as free as
Blender's: put the required values in a persistent strip *outside* the
splitter tree, so no workspace can remove them and the minimum-display
contract is satisfied structurally rather than by validation.

The alternative - validating each workspace against a minimum-display
contract and refusing to save or apply one that fails - is the fallback for
anything that cannot fit a strip. It is strictly worse where the strip works:
it warns after the fact where the strip prevents, which is the ordering
`.claude/rules/expert-review.md` asks for.

**What must not happen** is item 34 shipping with the question unasked, because
the failure is silent: a learner with a customized workspace sees a chart that
behaves exactly as documented and a display that no longer meets the document.

**Done when.** `docs/MODEL.md` § "Minimum displayed outputs" states what it
requires of a *customizable* layout - which values may never leave the display
whatever the workspace, and by what mechanism that is guaranteed - and
`ROADMAP.md` item 34 names the constraint as part of its intent rather than
leaving it to be discovered during scoping.
