---
id: PL-M352
title: Every layout operation is reachable without a drag, through a menu and the keyboard, so the area system does not ship an interaction a keyboard-only reader cannot perform
priority: P2
effort: M
status: ready
classes: feature, ux
feature: interface-areas
touches: src/anesthesia_sim/app/, src/anesthesia_sim/layout/model.py, tests/integration, tests/unit/test_layout_model.py
blocked-by: PL-2KXB
added: 2026-09-16
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
