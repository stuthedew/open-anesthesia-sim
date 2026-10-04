---
id: PL-DSMK
title: ROADMAP.md renders four passages differently from what they say: a ' - ' dash wrapped to the start of a line opens a list item at lines 2679, 3988 and 7992, the last splitting the section citation 'Completed: v0.4.26 - the interface moves to Qt' so no reader finds it, and no blank line before line 2636 makes its bold paragraph a lazy continuation of PL-V6M0's list entry (CommonMark 0.31.2 sections 5.2 and 5.3)
priority: P3
effort: S
status: done
classes: docs, defect
touches: ROADMAP.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-04
pr: 1343
payoff: ROADMAP.md renders as the prose it is, so the v0.4.26 citation it split is found by the close-out sweep and docket can refuse a lazily continued list entry without firing on v0.5.0's frozen list
verify: grep -qF '§ "Completed: v0.4.26 - the interface moves to Qt" → "Required scope" item 2' ROADMAP.md && ! grep -qE '^ *- (so both are seated|and this milestone ships|not because a unit or a price|the contrast is the lesson|the interface moves to Qt|.docs/MODEL.md. § "The chart)' ROADMAP.md
---

**Problem.** ROADMAP.md renders four passages differently from what they say: a ' - ' dash wrapped to the start of a line opens a list item at lines 2679, 3988 and 7992, the last splitting the section citation 'Completed: v0.4.26 - the interface moves to Qt' so no reader finds it, and no blank line before line 2636 makes its bold paragraph a lazy continuation of PL-V6M0's list entry (CommonMark 0.31.2 sections 5.2 and 5.3)

**Reproduced 2026-10-04, and the shape is seven passages, not four.** Rendered
with markdown-it-py 4.2.0 in its `commonmark` preset, every passage the title
names is what it says: a list item opens at the dash before "`docs/MODEL.md` §
"The chart's hover readout: what the tooltip may show"" (§ "Completed: v0.5.0 -
the case you can branch" → "Debt gate: the frozen list"), at "- so both are seated `P2`" (→ "Declined to Gate 2 on the
refilling-queue ground"), and at "- the interface moves to Qt" (§ "Planned
milestones", item 34), and PL-V6M0's entry absorbs the paragraph "**Two more
arrived from the Targ, Yasuda and Eger 1989 circuit paper**". A scan for every
list that interrupts a paragraph found three more of the title's dash shape,
each a spaced hyphen wrapped to an indented line start, which opens a nested
list inside the numbered entry it sits in: "- and this milestone ships `swap`"
and "- not because a unit or a price" (§ "v0.6.0 - the layout is the reader's"
→ "Required scope", entry 11), and "- the contrast is the lesson" (§ "Planned
milestones", item 30). This item fixes all seven: the capture counted lines a
dash opens at the margin, and the same fault at an indent is the same fault.
The same shape outside `ROADMAP.md` is outside this item's `touches`, and is
filed on its own.

**Why it matters.** A reader of the rendered file is shown a bullet where the
prose has a parenthetical, and a gate paragraph folded into one entry of the
frozen list. The citation is the expensive one: § "Completed: v0.4.26 - the
interface moves to Qt" split by a list item is the one wrapped citation of 124
that `PL-R417` slice 1's `mentions` could not find (`#1332`), so the close-out
sweep cannot name it as a place to check. The blank line is what `PL-MFVV`
waits on: once docket's list walker refuses a lazy continuation by name, that
line fails `make check` on v0.5.0's frozen list until it is there.

**Done when.** No line of `ROADMAP.md` opens a list item its prose does not
mean - each dash rewrapped to the end of the line before it, or the paragraph
rewrapped - so the seven passages render as the prose they are; the v0.4.26
citation reads on one line; and the paragraph after PL-V6M0's entry stands
apart from it, which `PL-MFVV`'s walker then holds. The blank line cannot be
grepped for, so `verify:` pins the citation and the dash lines, and the blank
line is held by the check `PL-MFVV` adds.
