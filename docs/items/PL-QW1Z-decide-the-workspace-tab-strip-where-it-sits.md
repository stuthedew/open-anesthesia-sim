---
id: PL-QW1Z
title: Decide the Workspace tab strip: where it sits, active against inactive, how rename, duplicate and delete surface, and how a shipped Workspace is told from one the learner saved
priority: P2
effort: S
status: done
classes: ux, planning
feature: interface-areas
milestone: v0.5.23
touches: src/anesthesia_sim/app/, docs/items
added: 2026-10-11
closed: 2026-10-11
pr: 1395
payoff: the Workspace tab strip says, by where it sits and how it looks, exactly what a tab switches and which Workspaces are the learner's own
verify: grep -qF 'Answered 2026-10-11' docs/items/PL-QW1Z-decide-the-workspace-tab-strip-where-it-sits.md
---

**Problem.** Decide the Workspace tab strip: where it sits, active against
inactive, how rename, duplicate and delete surface, and how a shipped Workspace
is told from one the learner saved. `ROADMAP.md` § "v0.6.0 - the layout is the
reader's" -> "Required scope" entry 20, member 1. Entry 11 (`PL-WV9K`) decided
what the strip operates on and entry 14 (`PL-2KXB`) builds it; neither says
what it looks like.

**What is already decided and binds this.** From `PL-WV9K` § "Answers
2026-09-27": a Workspace carries `origin` (`shipped:<id>` or `mine`); shipped
Workspaces are editable in place, with "Reset this Workspace" (shipped origin
only), "Restore shipped Workspaces" and "Reset all layouts"; the last Workspace
cannot be deleted, by construction; layouts are saved by an explicit "Save as
default" in the layout menu, with no dirty marker (owner-specified); a tab
switch never touches the run; "Pin current run" lives on the tab. Blender is
the reference (`docs/interface-provenance.md` § "What a later design thread
owes this study"). Its Workspace tabs sit in the Topbar, switch on click,
rename on double-click, add from a "+" at the strip's end, and carry a
right-click menu with Duplicate, Delete, Reorder to Front and to Back, and
Delete Other Workspaces (Blender Manual, `interface/window_system/workspaces.html`,
read 2026-10-11, paraphrased); the strip is
`layout.template_ID_tabs(window, "workspace", new="workspace.add",
menu="TOPBAR_MT_workspace_menu")` in `scripts/startup/bl_ui/space_topbar.py`
(`blender/blender` `main`, read at raw.githubusercontent.com on 2026-10-11).

## Design round 2026-10-11

**Q1. Where the strip sits.** **Recommendation: below the unconditional region
and directly above the Areas, spanning the layout container's width - not at
the top of the window, where Blender's Topbar puts it.** A tab's extent tells
the reader what the tab switches, and here a tab switches only the layout
container: the region above it keeps the run, the readouts and the transport
exactly as they were (`PL-WV9K` Q6). Put the strip at the window's top, above
the region, and it claims the region as the tab's page, which is false, and is
the wrong-context reading the clinical-output standard names. *Alternative
refused:* Blender's position at the window top. Blender can afford it because
nothing above its Areas is run-bound; this project's region is, which is the
whole reason it is outside the container.

**Q2. The tabs themselves.** **Recommendation: text tabs in one row, never
scrolled into a drop-down; the active tab in `INK` bold with a 2 px `PRIMARY`
indicator along its lower edge; inactive tabs in `MUTED` regular on the
`BACKGROUND` canvas, hover lifting an inactive label to `INK`.** The active tab
is told apart by weight and by a shape, so it survives colour-vision
deficiency and a greyscale print. The pairs clear the project's bars - `MUTED`
on `BACKGROUND` 4.65:1 against `tools/contrast_check.py`'s `AA_TEXT` 4.5,
`PRIMARY` on `BACKGROUND` 5.60:1 against `AA_NON_TEXT` 3.0 (computed from
`app/theme.py`'s values on 2026-10-11) - and are declared in that module's
`REQUIREMENTS` when built, per `.claude/rules/ui-color.md`. Height is one text
row: the `METRIC_NAME_SIZE` line height plus the vertical padding a `QTabBar`
gives (`PM_TabBarTabVSpace` 8, `qcommonstyle.cpp`, qt/qtbase `dev`, read
2026-10-11), 27 px at the offscreen fallback font and the same row unit as the
Area header (`PL-MS34`). The strip holds nothing but the tabs and a "+" at its
end: no caption, no "Workspaces:" label (`.claude/rules/ui-reader.md`).
*Alternative refused:* Blender's filled tabs (`wcol_tab` inner `0x1d1d1d`,
selected `0x303030`, `release/datafiles/userdef/userdef_default_theme.c`),
whose selected tab merges into the header surface beneath it. Here the Areas
are separate `PANEL` cards on the canvas with seams between them, so there is
no continuous surface for a filled tab to merge into, and a filled tab over a
seam reads as a card of its own.

**Q3. How rename, duplicate and delete surface.** **Recommendation:** rename by
double-click on the tab, by F2 while the strip has keyboard focus, and from the
tab's context menu, editing in place in the tab; duplicate and delete from the
context menu (right-click, the keyboard Menu key, Shift+F10); and "+" at the
strip's end duplicates the *current* Workspace and opens the new tab in rename
mode. The context menu, in this order: Rename, Duplicate, Move left, Move
right, Pin current run (or Unpin), Reset this Workspace (shipped origin only),
Delete. Delete asks first, in a dialog naming the Workspace and whether it is
shipped (restorable through "Restore shipped Workspaces") or the learner's own
(not restorable), because a saved layout has no undo; the last Workspace's
Delete is disabled with its reason in the tooltip, which is the structural
floor `PL-WV9K` carries shown rather than warned. Keyboard reach for all of it
is entry 15's (`PL-M352`). *Alternative refused:* a "+" opening a template menu
as Blender's does. The shipped Workspaces are already tabs, so the only
template a learner has is a Workspace they can see, and Duplicate is that.

**Q4. Shipped against the learner's own.** **Recommendation: order and a
separator, not a glyph.** Shipped Workspaces come first in the strip, the
learner's own after a thin vertical `GRIDLINE` rule, and Move left and Move
right stay within the group. The context menu says the rest: Reset this
Workspace appears only on a shipped tab, and the Delete dialog names the
origin. *Alternatives refused:* a mark on every learner-saved tab (a dot,
italics, an icon), which is a standing explanation the reader has to learn and
`ui-reader.md` refuses; Blender's answer, which is no distinction at all,
because `ROADMAP.md` item 34 asks for shipped presets *alongside* the learner's
own and `PL-WV9K` gave the two different reset semantics, so a reader must be
able to tell which they are about to reset.

[superseded 2026-10-11: answered below, every recommendation ratified]
**Decision needed.** Q1-Q4 above, each learner-visible: the strip below the
region rather than at the window top (Q1); one-row text tabs with an indicator
under the active one (Q2); double-click, F2 and a context menu for rename,
duplicate and delete, with a Delete that asks (Q3); order and a separator, not
a glyph, for shipped against the learner's own (Q4). The recommendation beside
each is the session's; agreeing with the recommendations ratifies all four.

**Done when.** Q1-Q4 are recorded with the owner's kind and date, this item
closes on that record, and `PL-2KXB` builds the strip to it, declaring the
colour pairs it introduces in `tools/contrast_check.py`.

**Why it matters.** The strip is the first thing a learner sees of the
Workspace system and the surface through which they learn the layout is
theirs; left to `QTabBar`'s default it is a document-tab row at the window top,
which says the wrong thing about what a tab switches.

**Generator check.** A one-off, and work the owner asked for: one of the
members `ROADMAP.md` Required-scope entry 20 names, scoped on 2026-09-21
(`PL-M3X6`) and filed by its round on 2026-10-11. `touches` reaches
`docs/items` only because the item closes on its own record once answered; no
apparatus fact was misread.

## Answers 2026-10-11

**Answered 2026-10-11: Q1-Q4 ratified** (project owner, 2026-10-11, ratified,
over the alternatives each question names - Blender's Topbar position, filled
tabs, a template menu on "+" and a glyph on every learner-saved tab), given in
the project thread as "Agree with recs" after the recommendations were put one
line each with the mock-up (https://claude.ai/artifact/3KmFvWB3nXmjLBHKogNiNE)
and the 1366 by 768 floor confirmed by the same word. This item closes on that
record; the build items named in its Done-when carry the look.
