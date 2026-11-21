---
id: PL-CHX0
title: The marks editor is a window that opens over required readouts while a run plays, and nothing applies the occlusion rule of docs/INTERFACE.md to it: decide where it may sit
status: untriaged
feature: interface-matches-its-spec
added: 2026-11-21
---

**Problem.** The marks editor is a window that opens over required readouts while a run plays, and nothing applies the occlusion rule of docs/INTERFACE.md to it: decide where it may sit

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `docs/INTERFACE.md` § "What this list requires once the layout is the reader's" says "**No value this list requires may be covered while the application treats it as shown.**" and that the rule applies to "the application's own windows and panels", because "The application creates and places these, and can check their state." The marks editor is such a window. `BookmarkDialog` in `app/qt_widgets.py` is non-modal, and `SimulationView._open_bookmark_dialog` in `app/simulation_view.py` calls `show()` on it with no placement and no check of what it covers. `_seen_by_reader` in the same file tests only that a widget is visible, not minimized and not of zero size, so a value under the editor still counts as shown.

Reproduction, offscreen at 1366 by 768: build `SimulationView((case.trunk,), case=case)`, show it, start the run, call `view._open_bookmark_dialog()`, and compare `view._bookmark_dialog.frameGeometry()` with the global rectangle of each widget in `view.runs[0].unconditional_widgets()`. Output:

```
dialog isWindow: True modal: False visible: True geom: QRect(318, 79, 484, 614)
region global: QRect(18, 18, 1334, 182) intersects dialog: True
values under the dialog: ['delivered_concentration', 'circuit_concentration', 'alveolar_concentration', 'mixed_venous_concentration', 'vessel_rich_concentration']
run running while dialog open: True
```

The position is the offscreen platform's. A desktop may place the editor elsewhere, and the reader can drag it anywhere. The questions that block the window (Reset, new case) also sit over the dashboard, but every run waits while one of those is open.

**Why it matters.** The editor is the one window of the application that can cover required values while a run plays. In this run it covered the delivered concentration and four of the six compartment readouts until the learner moved or closed it.

**Decision needed.** May the marks editor cover the readouts while a run plays? The choice is the owner's because it decides whether a required value is on screen.

- **A. Keep the editor off the required values.** It opens below the always-shown region, and the check that already guards the other windows also refuses a position over a required value. A learner who opens the editor still sees every readout. A learner who drags it over the readouts sees it stop at their edge.
- **B. Move the editor's fields into the Bookmarks View.** No window opens. The learner edits marks in an Area, and the layout's existing rules keep the readouts in view. This is the larger change.
- **C. Exempt the editor**, and say in the document that a window the reader opened and can move may cover values. The learner sees no change, and the rule has one more exception.

**Recommendation: A.** It keeps the rule whole with the smallest change, and it leaves B open for the milestone that reworks the marks.

**Done when.** The marks editor cannot rest over a required value while a run plays, in the form the owner chooses, a test opens it on a playing run and checks every widget of the unconditional set against its geometry, and `docs/INTERFACE.md` says what the editor does.
