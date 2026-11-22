---
id: PL-JV5H
title: The Reset, new-case and Workspace questions are windows that cover required readouts while open, with every run waiting, and docs/INTERFACE.md's occlusion rule has no sentence that allows it (found while building PL-CHX0)
status: untriaged
added: 2026-11-22
---

**Problem.** The Reset, new-case and Workspace questions are windows that cover required readouts while open, with every run waiting, and docs/INTERFACE.md's occlusion rule has no sentence that allows it (found while building PL-CHX0)

**Found 2026-11-22 while building `PL-CHX0`**, and named in that item's brief. `docs/INTERFACE.md` § "What this list requires once the layout is the reader's" says that no value the list requires may be covered while the application treats it as shown, and that the rule applies to the application's own windows. The questions that block the window (Reset, a new case, a Workspace change) are such windows and sit over the dashboard while open. Every run waits while one is open (`PL-TPBH`), so nothing under it changes, but the document has no sentence saying why a covered value is allowed then. Qt cannot place a top-level window under Wayland (Qt 6.12, "Window and Dialog Widgets", § "Wayland Peculiarities", cited in `PL-CHX0`), so a placement rule cannot close this either.
