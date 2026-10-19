---
id: PL-F5KT
title: When a halt cannot restate the bookmark panel and withdraws it (BookmarksPanel.withdraw), an open BookmarkDialog keeps the last frame's rows, so it lists a mark as to come on a failed run while the panel beside the chart shows none; reachable only with a frame failure and a mark-set divergence that bypasses _apply_to_every_run (found reviewing PL-YHR3)
priority: P3
effort: S
status: done
classes: defect, ux
feature: every-control-restates-the-halt
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/qt_widgets.py, tests/integration/test_simulation_view.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 product-defect sweep
added: 2026-10-19
closed: 2026-10-19
pr: 1675
payoff: the marks editor never lists a mark as to come on a failed run while the panel beside the chart has withdrawn it
verify: grep -q 'def test_a_withdrawn_bookmark_panel_withdraws_the_open_dialog' tests/integration/test_simulation_view.py
---

**Problem.** When a halt cannot restate the bookmark panel and withdraws it (BookmarksPanel.withdraw), an open BookmarkDialog keeps the last frame's rows, so it lists a mark as to come on a failed run while the panel beside the chart shows none; reachable only with a frame failure and a mark-set divergence that bypasses _apply_to_every_run (found reviewing PL-YHR3)

**Why it matters.** The dialog and the panel beside the chart are one listing in
two places (`BookmarkDialog.set_panel`). When the halt withdraws the panel because
the standings cannot be worked out, the dialog went on listing the last frame's
rows, so a reader with it open saw a mark as to come on a run that every other
control said had failed, and its Remove buttons stayed live against those rows.

**Done when.** A halt that withdraws the bookmark panel withdraws the dialog's two
lists and their Remove buttons as well, and the next drawn frame shows them again.
An integration test opens the dialog, makes the standings raise with every frame
failing, and asserts the lists and buttons are hidden.

**Regression check 2026-10-19.** Run with `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/integration/test_simulation_view.py -k <test>` against `src/` as `origin/main` 6fd84bd5 held it. `test_a_withdrawn_bookmark_panel_withdraws_the_open_dialog` fails on the code before the fix at `assert all(widget.isHidden() for widget in withdrawn)`.
