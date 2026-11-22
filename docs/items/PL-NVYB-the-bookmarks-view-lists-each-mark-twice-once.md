---
id: PL-NVYB
title: The Bookmarks View lists each mark twice: once read-only with every run's standing, and once in the marks editor's selectable list below it, so a learner scrolls past the same marks two times in one small Area
status: untriaged
added: 2026-11-22
---

**Problem.** The Bookmarks View lists each mark twice: once read-only with every run's standing, and once in the marks editor's selectable list below it, so a learner scrolls past the same marks two times in one small Area

**Found 2026-11-22 while building `PL-CHX0`** (the marks editor moved into the Bookmarks View). The View shows the two read-only lists of marks, each with every run's standing, and below them the two editor forms, each with its own selectable list of the same marks. The dialog that `PL-CHX0` deleted had the same second list, but in a window of its own. In the Default Workspace at 1366 by 768 the Bookmarks Area is about 590 by 116 pixels, so a learner scrolls past each mark twice. Merging the two lists would touch the wrapped rows of `PL-FPY2` and the withdrawal on a halt of `PL-F5KT`, so it was left out of `PL-CHX0`.
