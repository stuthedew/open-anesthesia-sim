---
id: PL-JVK4
title: docs/interface-provenance.md says it covers the outside model studied, not this project's source tree, yet names app/view_registry.py, app/area_layout.py and LayoutModel methods: narrow the claim or move the details to docs/ARCHITECTURE.md (copy editor structure read, 2026-11-05)
status: untriaged
feature: interface-provenance-structure
added: 2026-11-05
---

**Problem.** docs/interface-provenance.md says it covers the outside model studied, not this project's source tree, yet names app/view_registry.py, app/area_layout.py and LayoutModel methods: narrow the claim or move the details to docs/ARCHITECTURE.md (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/interface-provenance.md at cfb15a4a, before the line edit):

- **Query on what the document covers:** rows 17-19 say "This file covers the outside model that was studied, not the project's source tree", and they send the reader to `docs/ARCHITECTURE.md` for the project's own code. Yet rows 912-915, 972-981 and 1013-1054 name this project's modules and methods: `app/view_registry.py`, `app/area_layout.py`, `LayoutModel.borders()`, `LayoutModel.resize()` and `LayoutModel.join()`. Either rows 17-19 narrow their claim, or those details move to `docs/ARCHITECTURE.md` and the entries point there. Which should it be?
