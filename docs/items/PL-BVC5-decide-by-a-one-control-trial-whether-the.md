---
id: PL-BVC5
title: Decide by a one-control trial whether the interface pass builds its controls as a custom Qt style or as style sheets
status: untriaged
feature: interface-pass-design-round
added: 2026-11-11
---

**Problem.** Decide by a one-control trial whether the interface pass builds its controls as a custom Qt style or as style sheets

**The question.** The interface pass will give about six controls five states
each: at rest, under the pointer, pressed, with keyboard focus and
unavailable. That is the most styling the application will ever have. The
controls can be drawn by style sheets, as now, or by a custom Qt style. Writing
them as style sheets and switching later would mean writing them twice, so the
mechanism is chosen before the first control is built.

**What Qt says.** "Styling Approaches for Qt Widgets", read on 2026-11-10 in
the Qt 6.12 documentation, by a helper agent:
https://doc.qt.io/qt-6/qtwidgets-styling-approaches.html

- A style is "the one to use in production applications". Style sheets are "a
  tool for prototyping and for small, local adjustments, not for the production
  look of an application".
- "When a prototype turns into a product, transfer the design to a style. Most
  style sheet constructs have a direct counterpart."
- "A partial rule discards the native look."
- "Style sheets win over programmatic settings", palettes included.
- Each `setStyleSheet()` call "repolishes the widget and all its children, even
  when the string didn't change".
- `QProxyStyle` is "the recommended way to adjust the platform style in a
  production application": https://doc.qt.io/qt-6/qproxystyle.html
- StyleKit is "a Qt Labs module, and its API may change between Qt releases",
  and its widget style "is available since Qt 6.12". The project runs PySide6
  6.11.2, so StyleKit is not an option now.

**What depends on style sheets today** (counted on 2026-11-10).

- `src/anesthesia_sim/app/stylesheets.py` holds 17 functions that compose a
  style sheet, and `app/` calls `setStyleSheet` at 57 places.
- About half of those calls style a control: a button, a selector, a menu, a
  tab or a slider. The rest set a text colour or a panel's surface, which Qt's
  page still allows as local adjustments. An earlier reply to the owner said
  "about a third", which was wrong.
- 17 lines of `tools/contrast_check.py` name one of the 17 functions, and nine
  test files name a style sheet or a palette.
- `.claude/rules/ui-color.md` records four defects in which a style sheet and
  the palette disagreed and a control came out near-black or invisible.
- The second mock-up in `PL-HS9M` needed two image files on disk, a tick and an
  arrow, because a styled check box or selector draws neither.

**Recommendation (session, 2026-11-10, not yet answered by the owner).**
Before the control set is built, draw one control both ways and pick by
measurement. Draw the push button in its five states as a `QProxyStyle` that
wraps Qt's built-in Fusion style, with colours taken from palette roles. It
passes if all three hold:

1. The frame-cost benchmark shows no measurable slowdown. Python runs the
   drawing code, and its cost in this application has not been measured.
2. It looks the same on the owner's Mac in the light and the dark appearance.
3. It needs no image files.

If it passes, build each control in the style and delete that control's style
sheet as it moves. If it fails, build the controls as style sheets and record
which test failed. Type, spacing, corners and colours do not depend on this
choice.

**Why it is the owner's.** A custom style adds drawing code that the project
then maintains, and it changes how every later control is built.

**Approved 2026-11-10.** The owner replied "Agree with recs" to the reply
that recommended this trial (project owner, 2026-11-10, ratified, over
building the controls as style sheets without a trial). The trial changes
files under `src/anesthesia_sim/app/`, so it starts in a session of its own.
Its second test needs the owner: run the trial build on the Mac in the light
and the dark appearance.
