---
id: PL-DWHG
title: Nothing loads the reader's saved Workspaces at launch or writes them: app/main.py never calls layout/store.py's WorkspaceStore, so Save as default, Restore shipped Workspaces and Reset all layouts from PL-WV9K have no home
priority: P2
effort: M
status: done
classes: feature
feature: interface-areas
milestone: v0.6.0
touches: src/anesthesia_sim/app/main.py, src/anesthesia_sim/app/workspace_tabs.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app_metadata.py, src/anesthesia_sim/layout/store.py, tests/integration, tests/unit/test_bootstrap.py, docs/ARCHITECTURE.md
added: 2026-10-19
closed: 2026-10-19
pr: 1661
payoff: a learner's arranged Workspaces survive a restart once saved, and a deleted or broken layout can be put back from the Layout menu
verify: grep -q 'def test_save_restore_and_reset_all_are_reachable_from_the_keyboard' tests/integration/test_layout_keyboard.py
---

**Problem.** Nothing loads the reader's saved Workspaces at launch or writes them: app/main.py never calls layout/store.py's WorkspaceStore, so Save as default, Restore shipped Workspaces and Reset all layouts from PL-WV9K have no home

**Why it matters.** `ROADMAP.md` v0.6.0's Definition of done asks that a
learner can "save their own; and find them on the next launch". `PL-SSQW`
built the store and `PL-WV9K` § "Answers 2026-09-27" decided its use: the
next launch loads `workspaces.json`, or the shipped set when no file exists,
and "Save as default" in the layout menu writes the whole set after a
confirmation. `PL-SSQW`'s brief left wiring the store, and `app/main.py`
setting the organization and application names Qt needs for the directory,
to `PL-W9P6`'s adapter, which closed without it. `PL-2KXB` hands the
dashboard a `WorkspaceSet` but does not read it from the store. Each fallback
the store reports (`Loaded`'s notice) must be shown in the interface, never
silently (`PL-WV9K` Q5).

**Done when.** `app/main.py` resolves the user-data directory once, loads the
set through `WorkspaceStore.load(shipped_workspaces())`, hands it to the
dashboard, and shows the store's notice where one is given. "Save as
default", "Restore shipped Workspaces" (re-adds the deleted shipped ones) and
"Reset all layouts" (replaces the set after a confirmation) are reachable
from the layout menu `PL-M352` builds, with Save disabled and its reason
shown during a read-only session. Once Restore exists, the tab strip's Delete
question for a shipped Workspace names it (`app/workspace_tabs.py`'s
`_DELETE_SHIPPED_TEXT`). Tests use `tmp_path` and never write outside it.

*Found by* `PL-2KXB`, 2026-10-19, while wiring the tab strip.

**Handover, 2026-10-19.** The thread that built `PL-M352` (#1655, merged)
stopped here because it had used up its context budget. It had not claimed this item yet.
The next session should do three things in order:

1. Triage this item first, because it blocks `PL-G5SX`. Its `touches` should
   cover `src/anesthesia_sim/app/main.py`, `src/anesthesia_sim/app/workspace_tabs.py`,
   `src/anesthesia_sim/app/simulation_view.py` and `tests/integration`.
2. Put the three entries in `LayoutMenu.fill` in `app/workspace_tabs.py`,
   after the "This Workspace" submenu and behind a separator. `fill` rewrites
   the menu each time it opens. It clears old submenus through `_clear`, so
   any new submenu must be created inside `fill`. Save is shown disabled,
   with its reason as the tooltip, during a read-only session, as the Area
   menu does for an unavailable entry.
3. Drive each entry with keys in a test under `tests/integration/`, as
   `tests/integration/test_layout_keyboard.py`'s `_choose_by_keys` does, and
   use `tmp_path` for the store's directory.

**Built 2026-10-19 (#1661).** `app/main.py`'s `open_workspaces` resolves the
directory and loads the set, and the dashboard hands the store and its notice
to the tab strip. The Layout menu ends with the three entries behind a
separator. These calls were taken in the build, as placeholders where they
are look, wording or placement (project owner's rule of 2026-10-18):

- The store's notice, a failed save and a finished save each show on one
  wrapped line under the tabs, with a Dismiss button. Failures are in
  `WARNING`, a finished save in `INK`.
- "Save as default" asks first, naming the file it writes or replaces, with
  Save and Cancel. Without a store, or where the load turned saving off, the
  entry is disabled and its tooltip is the reason.
- "Restore shipped Workspaces" puts back only the shipped Workspaces whose
  origin is gone from the set, as their files hold them, each after the
  nearest earlier shipped one the set holds. It keeps the current Workspace
  current and asks nothing, since it removes nothing. Where one of the
  reader's Workspaces already has a shipped name, the entry is unavailable
  and says which name. It is not renamed on the reader's behalf.
- "Reset all layouts" asks first and writes nothing, as Blender's Load
  Factory Settings does not save.
- Qt is given the organization name `OpenAnesthesia` and the application
  name `Open Anesthesia Simulator`. On Linux the file is
  `~/.local/share/OpenAnesthesia/Open Anesthesia Simulator/workspaces.json`,
  measured with PySide6's `QStandardPaths` on 2026-10-19.

**Owner read not needed (2026-10-19).** The menu entries carry out
`PL-WV9K`'s recorded answers, and their wording is a placeholder. No clinical
value, or what one means, changes. The branch's long docstrings and comments
were rewritten in plain English after a review that read 21 and rewrote 16.
