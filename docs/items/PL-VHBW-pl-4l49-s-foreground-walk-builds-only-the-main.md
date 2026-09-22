---
id: PL-VHBW
title: PL-4L49's foreground walk builds only the main dashboard, so a control added to NewCaseDialog or BookmarkDialog declares nothing and is still measured by nothing
status: untriaged
added: 2026-09-22
---

**Problem.** PL-4L49's foreground walk builds only the main dashboard, so a control added to NewCaseDialog or BookmarkDialog declares nothing and is still measured by nothing

`test_every_control_that_paints_its_own_content_declares_a_foreground` walks
`SimulationView` and its children, which is everything `main.py` shows at rest.
Neither dialog is built until a reader opens it, so neither is in the walk - and
both carry text controls a reader reads: the new-case confirmation's title,
statement and two buttons, and the bookmark editor's two lists, its entry and
its spin box.

They are not uncovered today. `tests/integration/test_dark_appearance.py`
builds both under a dark host palette and fails on any content widget resolving
to it (`PL-RKRY`, `PL-7W9N`, `PL-0NVN`), which is what caught the six controls
that had declared nothing. What is missing is the *coverage* half: that module
names the widget kinds it checks, so a control of a kind it does not name joins
silently, which is the failure `PL-4L49` was filed against for the dashboard.

**Likely shape.** Extend the walk rather than write a second one: build each
dialog under the same alien palette and run `_content_painters` over it, sharing
`FOREGROUND_NOT_DECLARED`. Where it lives is the open question - the dialogs are
constructed in `tests/integration/test_qt_widgets.py` and in
`test_dark_appearance.py`, and the mapping is read by `tools/contrast_check.py`
from `tests/integration/test_simulation_view.py`, so moving it costs that
reader a path change.

**Done when** every control a reader can reach - the dashboard and both
dialogs - is held to declaring a foreground by one walk, and the report line's
count covers all of them.
