---
id: PL-HK75
title: Decide the application's display name, which still reads "Working Title"
status: untriaged
added: 2026-09-02
---

**Problem.** `src/anesthesia_sim/app_metadata.py` sets
`APP_DISPLAY_NAME = "Working Title"`. That string is the window title and the
largest text on the interface — `simulation_view.py`'s `mount()` draws it at
size 26 above everything else — so every screenshot, every demonstration and
every bug report carries it. Found while rendering the app to check a label
change for PL-NV9W; nothing in `docs/items/` or `ROADMAP.md` tracks it.

**Why it matters.** Lowest-stakes of the presentation findings, but it is the
first thing a reader sees and the only string on the page that names the
product. `APP_BUNDLE_ID` is already `org.openanesthesia.simulator` and
`APP_AUTHOR` already "Open Anesthesia Simulator contributors", so the
placeholder is now the odd one out rather than a consistent stand-in.

**Where.** `src/anesthesia_sim/app_metadata.py`; displayed by
`src/anesthesia_sim/app/simulation_view.py` `mount()` and by
`src/anesthesia_sim/app/main.py` as the window title.

**Done when.** The name is the project owner's decision, not a session's:
this item is a decision to put to them, and the code change behind it is one
line.
