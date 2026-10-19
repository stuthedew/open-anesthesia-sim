---
id: PL-M352
title: Every layout operation is reachable without a drag, through a menu and the keyboard, so the area system does not ship an interaction a keyboard-only reader cannot perform
priority: P2
effort: M
status: done
classes: feature, ux
feature: interface-areas
milestone: v0.5.41
touches: src/anesthesia_sim/app/, src/anesthesia_sim/layout/model.py, tests/integration, tests/unit/test_layout_model.py
blocked-by: PL-2KXB
added: 2026-09-16
closed: 2026-10-19
pr: 1655
payoff: a keyboard-only reader can perform every layout operation the mouse can, so the area system ships no interaction that shuts them out
verify: grep -q 'def test_every_layout_operation_is_reachable_from_the_keyboard' tests/integration/test_layout_keyboard.py
---

**Problem.** Every layout operation is reachable without a drag, through a menu and the keyboard, so the area system does not ship an interaction a keyboard-only reader cannot perform

**Why it matters.** An area system whose whole operation set is corner and
border drags is unusable from a keyboard, and retrofitting reachability after
the affordances exist is the expensive order. This is deliberately *not*
planned-milestone item 20's general accessibility pass arriving early: the rule
is only that this milestone does not introduce an interaction a keyboard-only
reader cannot perform.

**Done when.** Split, join, resize, swap, close, Workspace switch, rename,
duplicate and delete are each reachable from a menu and from the keyboard, and
a test drives the full operation set without synthesising a drag.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" item 15.

**Checked 2026-10-19,** against `origin/main` at `2026b35f`. The brief still
holds, but `PL-2KXB` has already built half of it. Split, join, swap and close
are in each Area's menu. That menu is a header button in the tab order, and
Space or Enter opens it. Rename, duplicate and delete are in the tab's context
menu, which the Menu key and Shift+F10 open, and F2 renames the focused tab.
Three things are still missing:

1. Resize has no route but a border drag. The handles take the focus only on
   a click, so no key reaches them.
2. Switching Workspace has a keyboard route (Tab to a tab, then Space) but no
   menu route.
3. The "layout drop-down menu" that `PL-WV9K` § "Answers 2026-09-27" gives
   this item does not exist yet. `PL-DWHG` puts Save as default, Restore
   shipped Workspaces and Reset all layouts in it.

So `touches` gains `layout/model.py` and its unit tests, for the one query the
resize route needs.

**Built 2026-10-19.** Each of the three gaps above now has a menu route and a
keyboard route, and `tests/integration/test_layout_keyboard.py` drives all
nine operations with key presses alone.

1. *Resize.* Each border is a tab stop. An arrow key along its axis moves it
   by `AREA_KEYBOARD_STEP` (20 px). Shift moves it alone and Escape puts back
   the layout drawn when it took the focus, as in a drag. It stops in
   WARNING at an Area's least size, as a drag does. Each Area's menu lists its
   borders under Resize, and choosing one gives that border the focus. Blender
   has no keyboard resize to copy, so this follows the W3C WAI-ARIA APG
   "Window Splitter" pattern without its Enter (collapse), which `PL-K285`
   refuses. `LayoutModel.edges()` is the query it needed: the nearest border
   on each side of an Area.
2. *Workspace switch.* Ctrl+PgUp and Ctrl+PgDn step through the tabs and wrap
   round, as Blender binds them (Manual "Workspaces";
   `space_workspace_cycle_invoke` wraps).
3. *The layout menu.* A "Layout" button at the tab strip's right end, after
   "+". It lists every Workspace with the current one checked, then Previous
   and Next Workspace, then "This Workspace", which holds the tab menu's own
   entries. `PL-DWHG` adds Save, Restore and Reset to it.

*Placeholders* (the 2026-10-18 rule on look, wording and placement): the
labels "Layout", "Resize", "Left border" and its three siblings, and "This
Workspace"; the 20 px step; the button at the strip's end. `PL-QW1Z` Q2 kept
the strip to its tabs and "+", but that answer was about captions, and the
later placeholder rule covers placement.

*Refused.* A menu bar of its own: it costs a row of height on Windows and
Linux, where `PL-QLZ5` was recovering 70 to 80 px of chart height. Blender
also puts its menus and Workspace tabs in one row.
`docs/interface-provenance.md` records both the adoption and the divergence.

*Reviewed before the pull request.* Two independent passes and a prose
review ran on the branch. The state pass reproduced four defects, each fixed
here with a regression test that fails on the code before its fix:

1. Ctrl+PgUp or Ctrl+PgDn during a tab rename discarded the typed name.
   `cycle` now takes the name first. Before the fix the test failed with
   `assert 'Default' == 'Mine'`.
2. Escape after a mouse drag of a border that already had the keyboard focus
   undid the drag. A press now ends the keyboard resize.
3. Switching windows reset where Escape returns to. The focus reasons for a
   window switch or a popup now leave the keyboard resize in place.
4. The Layout menu and the Area menu kept every submenu they had ever written,
   one more per opening. Both now delete the old submenus.

The test pass ran 30 mutants. Seven survived. The new tests kill the five that
change behaviour: `edges` returning the farthest border, "This Workspace"
acting on the first tab, a keyed border stopping one step short of the least
size, a wrong "Top border" label, and Escape dropping the focused border's
state. The two left are a dropped accessible description, now asserted, and a
mouse-focus guard that the press fix above makes redundant. It also found the
splitter's drawable length written three times, now one helper,
`_drawable_px`.
