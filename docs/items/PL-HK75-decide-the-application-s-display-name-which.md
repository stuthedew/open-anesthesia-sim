---
id: PL-HK75
title: Decide the application's display name, which still reads "Working Title"
priority: P3
effort: S
status: done
classes: ux
feature: presentation-safety
touches: src/anesthesia_sim/app_metadata.py, tests/unit/test_simulation_view.py
added: 2026-09-02
closed: 2026-09-02
verify: uv run pytest tests/unit/test_simulation_view.py -k app_metadata && grep -q 'APP_DISPLAY_NAME = "Open Anesthesia Simulator"' src/anesthesia_sim/app_metadata.py
---

**Problem.** `src/anesthesia_sim/app_metadata.py` sets
`APP_DISPLAY_NAME = "Working Title"`. That string is the window title and the
largest text on the interface — `simulation_view.py`'s `mount()` draws it at
size 26 above everything else — so every screenshot, every demonstration and
every bug report carries it. Found while rendering the app to check a label
change for PL-NV9W; nothing in `docs/items/` or `ROADMAP.md` tracked it.

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

**Worked.** The project owner chose "Open Anesthesia Simulator" (2026-09-02),
which is the name the other two identity constants already carried, so the
three now agree.

`test_the_header_shows_the_application_name_from_app_metadata` was added with
it, and it guards the harder half. The one-line change is not the failure mode
worth testing — a literal creeping into the header is, because
`app_metadata.py` is the single place the name is declared and `app/main.py`
also reads it for the window title, so a hardcoded copy would leave the header
and the window disagreeing after the next rename. The test asserts against the
mounted control tree rather than the import, so a header rebuilt from a
literal fails even while the import still resolves; confirmed by hardcoding
the header and watching it fail. This suite has caught the same class of bug
once before, in the delivered-concentration label that was hardcoded to one
agent.
