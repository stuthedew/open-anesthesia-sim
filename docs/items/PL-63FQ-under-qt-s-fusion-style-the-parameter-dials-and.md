---
id: PL-63FQ
title: Under Qt's Fusion style the parameter dials and the trace check boxes draw no keyboard focus mark, so a keyboard user cannot see which dial the arrow keys will move (PL-CXYV covers only Start, Pause and Reset)
priority: P2
effort: S
status: done
classes: defect, ux
feature: interface-design-review
milestone: v0.6.20
touches: src/anesthesia_sim/app, tests/integration/test_keyboard_focus.py, docs/INTERFACE.md, tools/contrast_check.py, docs/items/PL-B45W-tab-does-not-follow-reading-order-it-reaches.md
added: 2026-11-22
closed: 2026-11-22
pr: 2216
tests: tests/integration/test_keyboard_focus.py::test_every_tab_stop_on_the_dashboard_shows_the_focus, tests/integration/test_keyboard_focus.py::test_every_tab_stop_in_both_dialogs_shows_the_focus
---

**Problem.** Under Qt's Fusion style the parameter dials and the trace check boxes draw no keyboard focus mark, so a keyboard user cannot see which dial the arrow keys will move (PL-CXYV covers only Start, Pause and Reset)

**Go-ahead.** The design review that found this was approved by the project owner (project owner, 2026-11-22). It ran offscreen on `a7eb53f`, with screenshots of each Workspace and each View at 1366 by 768 and 1920 by 1080 in `/mnt/project-files/v0.7.0/design-review/`.

**What was measured.** Offscreen, under Qt's Fusion style, a parameter dial
and a trace check box given the focus with `Qt.FocusReason.TabFocusReason`
paint the same pixels as when they are not focused. The Workspace "+" button
does draw a focus border. `PL-CXYV` records the same defect for Start, Pause
and Reset only. Whether the macOS style draws a mark on the owner's machine
is not settled by an offscreen grab.

**Why it matters.** WCAG 2.2 Success Criterion 2.4.7, Focus Visible (Level
AA), says that "the keyboard focus indicator is visible"
(https://github.com/w3c/wcag/blob/main/guidelines/sc/20/focus-visible.html,
read 2026-11-22). The arrow keys move a dial
that has the focus, so a keyboard user who cannot see which dial is focused
can change the wrong setting.

**What to do.** Give every focusable control a focus mark, in the custom Qt
style that `PL-8G4V` moves into the app, since `PL-BVC5` chose that style for
control states. Work it with `PL-CXYV`.

**Done when.** A test renders each focusable control kind with and without
the focus and finds the two images differ.

**Correction, 2026-11-22: the trace check boxes do draw a mark.** The
measurement above gave the focus with `setFocus(Qt.FocusReason.TabFocusReason)`
outside a Tab key event. Qt then clears `WA_KeyboardFocusChange` on the window,
and Fusion draws a focus mark only while that attribute is set. Walking the
real Tab order with key presses, on `f8424d33`, every check box, push button,
Workspace tab, View chooser, Area border and the "+" button drew a mark. The
controls that drew none were the four sliders, every combo box drawn by a
style sheet (the agent, playback, branch-point, time-base and agent cost
selectors), the four scroll areas (the page, the control-change record, each
Area's View holder and each chart's key), the two lists in the bookmark dialog,
and the two plots. A plot takes no key, because its mouse and menu are off in
`app/qt_chart.py`.

**What was built, 2026-11-22.** `FocusRing` in `app/qt_widgets.py`, a child
widget that draws a 2 px ring inside a control's edge while the control has a
focus that came from the keyboard. It is on every control in the list above,
and on Start, Pause and Reset (`PL-CXYV`). A `:focus` rule in a slider's or a
selector's style sheet changed no pixel, which is why the ring is painted in
code. It needs no custom Qt style, so it fits `PL-8G4V`, which moves styling
into a custom style only when a control's look changes. The two plots are no
longer Tab stops. The ring's width, colour and placement are a placeholder look
until the visual pass. The ring is drawn inside a selector's 1 px edge, so all
of its pixels change from the fill to the ring's colour, which meets WCAG 2.2
SC 2.4.13 (Level AAA) as well as SC 2.4.7: "at least as large as the area of a
2 CSS pixel thick perimeter" with "a contrast ratio of at least 3:1 between
the same pixels in the focused and unfocused states"
(https://raw.githubusercontent.com/w3c/wcag/main/guidelines/sc/22/focus-appearance.html,
read 2026-11-22). A slider's ring crosses the edge of its thumb, where the
change is less than 3:1, so the AAA claim holds for the selectors and not
for every control.

**Regression check.** `tests/integration/test_keyboard_focus.py`, without its
two ring tests, which need `FocusRing`, failed on `f8424d33`: 27 dashboard
controls and the 2 dialog lists drew no mark, the plot took Tab focus, and
Start drew the same image at rest and pressed.

**Generator check.** This is the third instance of one fact: a control drawn
by a style sheet draws only the states that the sheet declares, and Fusion's
focus mark does not reach every control. The other two are the disabled
transport state added after `:enabled` alone (`PL-DHBX`) and `PL-CXYV`. The
focus half now fails a test for any control added to any View or either
dialog that is shown when the dashboard opens, because the test walks the
built interface rather than a list. A control shown only later, such as the
agent cost View's keep and discard buttons, is outside the walk. Each such
control today is a push button or a selector, kinds that the walk checks
elsewhere. The pressed
half is tested only for Start, Pause and Reset, and the pressed state of the
other push buttons belongs to the interface pass (`PL-BVC5`). So no live
generator remains for the focus mark, as far as the walk reaches.

