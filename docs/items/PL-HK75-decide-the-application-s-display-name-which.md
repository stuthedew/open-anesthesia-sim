---
id: PL-HK75
title: Decide the application's display name, which still reads "Working Title"
priority: P2
effort: S
status: needs-decision
classes: ux
feature: project-introduction
touches: src/anesthesia_sim/app_metadata.py
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

**Decision needed.** What `APP_DISPLAY_NAME` should read. The rest of
`app_metadata.py` has already settled on a name in two other forms -
`APP_BUNDLE_ID` is `org.openanesthesia.simulator` and `APP_AUTHOR` is
"Open Anesthesia Simulator contributors" - so "Open Anesthesia Simulator" is
the answer the file already implies, and the decision is whether to take it or
name the product something else. It is the project owner's call, not a
session's.

**Done when.** `APP_DISPLAY_NAME` holds the chosen name and the window title
and page header show it. The code change behind the decision is one line.
