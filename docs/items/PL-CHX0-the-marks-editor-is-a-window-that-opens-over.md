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

**Corrected 2026-11-21: option A cannot be kept on Linux.** Qt's page "Window and Dialog Widgets" (Qt 6.12, https://doc.qt.io/qt-6/application-windows.html, read 2026-11-21, quoted in short passages) says under "Wayland Peculiarities" that "programmatically setting or getting the position of a top-level window from the client-side is typically not supported", and that "Qt will ignore calls to set the top-level position of a window". A position read back is always (0, 0). Under "X11 Peculiarities" it says "All Qt can do is to send certain hints to the window manager", which may obey or ignore them. So on a Wayland desktop the application can neither place the editor nor tell where the reader has dragged it, and a check of its position would pass while the editor covers the readouts. `docs/INTERFACE.md` § "What this list requires once the layout is the reader's" already refuses a reading that "rests the guarantee on where the window manager has put things" (`PL-WLWY`). The options are restated below.

- **A. Keep the editor off the required values, as a window.** Place it below the always-shown region and refuse a position over a required value. This works on macOS and Windows. On Linux under Wayland it does nothing, and the check would report the readouts as shown while they are covered.
- **B. Move the editor's fields into the Bookmarks View.** No window opens. The learner edits marks in an Area, and the layout already keeps the always-shown region outside every Area, on every platform. The cost is room: in the Default Workspace at 1366 by 768 the Bookmarks Area is about 590 by 150 pixels, so the two forms scroll inside it until the learner drags its border (mock-up rendered 2026-11-21 by forcing the dialog into the View). The Bookmarks View already exists since `PL-9YPR`, so this is a change to one View and the deletion of `BookmarkDialog`, not a new layout mechanism.
- **C. Exempt the editor**, and say in the document that a window the reader opened and can move may cover values. The learner sees no change, and the rule has one more exception.
- **D. Make the editor block the window, and make every run wait while it is open**, as the Reset and new-case questions do (`PL-TPBH`). The editor still covers readouts, but nothing under it changes until it closes. This reverses the reason `BookmarkDialog`'s docstring gives for being non-modal, and it needs a sentence in `docs/INTERFACE.md` saying why a covered value is allowed while every run waits. That sentence is missing for the three questions too today.

**Recommendation: B** (marked as the session's recommendation, 2026-11-21). It is the only option under which the rule holds on every platform the simulator supports, because it removes the window rather than trying to steer it. It needs ordering against v0.7.0, because the schematic milestone does not name it. D is the cheaper fallback if the owner wants the gap closed sooner, at the price of a written exception that also covers the questions.

**Answered 2026-11-21: B.** The marks editor's fields move into the Bookmarks View, and `BookmarkDialog` is deleted, so no window of the application can cover a required readout (project owner, 2026-11-21, ratified, by the decision card in the interface spec check's thread, over A, a window kept off the readouts that Wayland cannot enforce, C, an exemption, and D, a blocking editor during which every run waits).

**Done when.** No window opens to edit marks: the Bookmarks View holds both forms and their add and remove buttons, `BookmarkDialog` is gone, a test builds the dashboard with a run playing and finds no top-level window but the main one after the reader edits a mark, and `docs/INTERFACE.md` says the marks are edited in the Bookmarks View and drops the sentence that runs go on while the bookmark editor is open.
