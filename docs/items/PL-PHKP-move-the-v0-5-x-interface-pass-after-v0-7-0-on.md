---
id: PL-PHKP
title: Move the v0.5.x interface pass after v0.7.0 on the timeline: item 34 and break-out introduce the area header, workspace tab strip and drag affordances that a visual pass run before them would have to be redone for
priority: P3
effort: S
status: done
classes: planning, docs
feature: interface-areas
milestone: v0.4.26
touches: ROADMAP.md, docs/WORKING_NOTES.md
added: 2026-09-16
closed: 2026-09-16
pr: 634
verify: python3 tools/doc_check.py check && grep -qF 'v0.7.x — the interface pass' ROADMAP.md
---

**Problem.** Move the v0.5.x interface pass after v0.7.0 on the timeline: item 34 and break-out introduce the area header, workspace tab strip and drag affordances that a visual pass run before them would have to be redone for

**Why it matters.** The row was placed on 2026-09-08 as `v0.5.x`, between v0.5.0
and v0.6.0, when v0.6.0 meant the schematic. Scoping planned-milestone item 34
into v0.6.0 and v0.7.0 on 2026-09-16 changed what the row sits in front of
without changing the row, so the placement was left standing on a premise that
had moved.

**The decision** (project owner, 2026-09-16, ratified - chosen over leaving it
ahead of item 34). It runs **after** v0.7.0. Item 34 and break-out introduce an
area header, a workspace tab strip, a live splitter handle and a drag affordance;
none exists today, and `docs/interface-provenance.md` § "What an editor must
implement" establishes from Blender's source that the header is the *Editor's*
own rather than the container's. So a visual pass run first would decide palette,
type scale and spacing across one set of surfaces and then meet four more.

**What the other side bought.** A styled interface two releases sooner, and
`PL-BNYF` had already separated the two questions - arrangement is item 34's,
appearance is this row's - so the composition of each *existing* surface would
mostly have survived being rearranged. The accepted cost is that the interface
keeps its current visual language until after v0.7.0. Nothing in either release
was blocked on the answer, which is why the row was left in place while the
question was open rather than moved on a guess.

**Done when.** The interface-pass row sits after v0.7.0 on "The timeline" and is
renumbered `v0.7.x` - a patch track takes the number of the release it follows,
which is mechanical rather than a second decision - item 33's entry records the
placement and the trade-off it was chosen over, and every reference to the row's
old name and position moves with it.

**Where.** `ROADMAP.md` "The timeline" (the row itself), § "Completed: v0.4.26" (the
un-absorption paragraph naming the row), planned-milestone item 33's placement
paragraphs; `docs/WORKING_NOTES.md` § "Shelved, then resumed: UI structure/form
mockups" and the item-34 scoping thread that recorded this as open.
