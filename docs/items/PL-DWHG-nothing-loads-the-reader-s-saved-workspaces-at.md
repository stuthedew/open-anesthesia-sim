---
id: PL-DWHG
title: Nothing loads the reader's saved Workspaces at launch or writes them: app/main.py never calls layout/store.py's WorkspaceStore, so Save as default, Restore shipped Workspaces and Reset all layouts from PL-WV9K have no home
status: untriaged
feature: interface-areas
added: 2026-10-19
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
