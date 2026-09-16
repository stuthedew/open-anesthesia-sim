---
id: PL-WLWY
title: docs/MODEL.md's Minimum displayed outputs assumes one fixed layout, so planned-milestone item 34's removable areas would let a learner delete the readouts that are the stated safety floor for hiding a chart trace
priority: P2
effort: M
status: done
closed: 2026-09-16
classes: docs, ux
touches: docs/MODEL.md, ROADMAP.md
added: 2026-09-15
verify: python3 tools/doc_check.py check && grep -qF 'no workspace may remove' docs/MODEL.md
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

**Approach settled 2026-09-15 (project owner), and it is stricter than the
precedent it came from.** The required values live in a persistent region
**outside the splitter tree**, so that no workspace layout can remove them and
the contract is satisfied structurally rather than by validating each saved
layout. The owner agreed to that shape in the same exchange that settled item
34's tiling default.

**Correction to the case first made for it.** That recommendation was argued
from Blender's Topbar and Status Bar as regions exempt from the area system and
therefore always present. The first half holds - they are not areas, and no
split, join or workspace switch touches them - but the second does not: the
Blender Manual's § "Status Bar" documents *Show Status Bar* in the Window menu,
and dragging from the bottom edge, as ways to hide it. So Blender's own strip is
hideable and this project's may not be, and the reason is the difference between
the two applications rather than a detail: Blender has no class of value whose
absence is a safety failure, and this one does. Follow Blender for the
structure - a region outside the area system - and depart from it on
hideability, saying so where the departure is recorded.

**The caveat on that correction is discharged, and the source is stronger than
the correction was.** It was written from search results, `docs.blender.org`
being blocked by this environment's egress proxy. The project owner supplied
the § "Areas" and § "Workspaces" pages directly on 2026-09-16, and they say
more than the *Show Status Bar* toggle did: **Focus Mode** (View -> Area ->
Focus Mode, Ctrl-Alt-Spacebar) hides the Topbar, the Status Bar **and** the
editor's secondary regions together. So neither of Blender's two out-of-area
regions is unconditionally present, and this project departs from the precedent
further than the first correction said. `docs/MODEL.md` cites Focus Mode rather
than the toggle.

**What break-out added to the question rather than answering** (project owner,
2026-09-15, recorded at `ROADMAP.md` item 34). An area may be broken out into
its own top-level window. So there can be more than one window, and a
broken-out one can be dragged over the window carrying the strip. Three
candidate readings, and choosing between them is this item's real work:

1. **Every top-level window carries the strip.** Verifiable and structural, and
   it costs a compartment readout row inside a small broken-out view.
2. **The contract binds the application, not the window** - the required values
   must be visible somewhere. Unverifiable once the window manager is involved,
   which is the property that rules it out under this project's own preference
   for preventing over warning.
3. **The contract binds the window that can be alone on screen.** The main
   window always carries the strip and cannot be closed while break-outs
   exist; a broken-out window is a secondary view that names the run it shows.
   `docs/MODEL.md` already requires a readout to name its run in compare mode,
   on the ground that "position alone fails the reader who has looked away and
   back" - a broken-out window on a second monitor is the strongest form of
   position carrying meaning, so that rule reaches this case already rather
   than needing a new one.

**Done when.** `docs/MODEL.md` § "Minimum displayed outputs" states what it
requires of a customizable, multi-window layout - which values no workspace may
remove, by what mechanism that is guaranteed, and what a second window owes -
and `ROADMAP.md` item 34 names the constraint rather than leaving it to be
discovered during scoping.

**Extended 2026-09-15 to cover an in-window floating panel** (`PL-T86Q`). Item
34 no longer forecloses floating: tiled-first is sequencing, and the option to
take an area out into a floating window is wanted later. It points here for the
constraint floating is subject to, so this item owes an answer covering both
shapes rather than windows alone:

- a **second top-level window** dragged over the one carrying the minimum
  display, which the three readings above are about; and
- a **floating panel inside a window**, overlapping the tiled areas beneath it,
  which none of them reaches.

They are one question stated at the right level: *nothing may cover a value the
display is required to show while the application still believes it is showing
it.* Answer it as a property of the display - which values, guaranteed by what
mechanism, surviving any layout the learner chose - rather than as a rule about
window types, and both shapes fall out of it. A per-mechanism answer is what
produced the overreach `PL-T86Q` had to correct.

**Closed 2026-09-16 on the project owner's decision**, taken as a deliberate
stepping stone: "ultimately, will be able to resize everything however, but
this is down the road ... I'm ok with starting with a relatively more rigid
structure as a stepping stone to more mature resizing apparatus down the road."
`docs/MODEL.md` § "Minimum displayed outputs" gains "What this list requires
once the layout is the reader's", and `ROADMAP.md` item 34 names the answer
instead of pointing here.

**The answer was not the one this item was filed expecting, and the count is
why.** The brief argued for a persistent strip carrying "the required values",
without counting what that is. The list runs to roughly twenty obligations
across six surfaces - a seven-panel readout row, a five-line accounting panel,
transport and status, the concentration chart, the F_A/F_I plot and the
control-input timeline - and two of those rows *are* charts, which no strip can
hold. That is `.claude/rules/expert-review.md`'s rule arriving on this item's
own recommendation: name the number, then go and count it.

**What replaced it is a three-way split, by what a reader can misread a value
without:**

- **Unconditional** - simulated time, the rate, run state, halt reason, agent
  identity, and the delivered plus six compartment concentrations in both units
  with 1 MAC stated. No workspace may remove them and nothing may cover them,
  guaranteed by a region outside the area system rather than by validating each
  saved layout.
- **Reachable rather than simultaneously visible** - the agent accounting and
  the mass-balance residual, which state whether the *model* conserves mass and
  are not values a reader titrates against.
- **Conditional** - a chart carries its MAC-awake band, 1 MAC line, control
  marks and time-base statement *if a chart is shown*; an F_A/F_I plot carries
  its equilibrium rule and undefined domain *if it is shown*. A reference
  exists so a trace is not read without its anchor, so with no trace there is
  nothing to anchor.

The control-input timeline splits the same way: the record unconditional, its
chart marks conditional.

**The rule underneath all three is the one that has to survive.** No value the
list requires may be covered while the application still believes it is showing
it. Stated once on the display, it binds an in-window floating panel, a
broken-out window dragged back over the main one, and any later mechanism,
without being re-argued per window type - which is what `PL-T86Q` had to
correct when it was argued per mechanism.
