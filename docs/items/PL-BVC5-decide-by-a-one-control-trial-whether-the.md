---
id: PL-BVC5
title: Decide by a one-control trial whether the interface pass builds its controls as a custom Qt style or as style sheets
priority: P2
effort: S
status: done
classes: planning
feature: interface-pass-design-round
touches: tests/benchmarks/style_trial.py, tests/benchmarks/style_trial_checks.py
deferred-from: v0.7.0 - captured after the freeze; the interface pass's own work (planned-milestone item 33), not safety or science
added: 2026-11-11
closed: 2026-11-11
pr: 2118
payoff: the interface pass builds its six controls once, in the mechanism that measurement supports
not-delegable: the trial's result rests on the owner's answers and a run on the owner's Mac, which no command can check
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
[superseded 2026-11-10: the owner approved this trial, as "Approved
2026-11-10" below records.] Before the control set is built, draw one control both ways and pick by
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

**Why it matters.** The six controls are built once. A mechanism chosen
without a measurement would either be rewritten later or keep the defects
that `.claude/rules/ui-color.md` records, where a style sheet and the palette
disagreed and a control came out near-black or invisible.

**Trial, 2026-11-11.** The trial is `tests/benchmarks/style_trial.py`, with
its checks in `tests/benchmarks/style_trial_checks.py`. It changes no file
under `src/`. It draws one push button in five states twice from one
placeholder design: as a style sheet, and as `TrialStyle`, a `QProxyStyle`
over Fusion that takes every colour from a declared palette role. At rest and
when unavailable the design is the shipped run controls' button. The pointer,
pressed and focus states are the trial's own.

[The table and the figures under "Test 1" are replaced by "Rerun of test 1
with the corrected order", below. They are kept because the owner's answer
was given on them.]
*Test 1, frame cost.* `uv run python tests/benchmarks/style_trial.py
compare-frame-cost --invocations 20` ran `frame_cost.measure` at its defaults
(300x, 60 minutes of run, 1600 by 1000, 20 frames) in a fresh process per
arm, 20 rotations, in the web container on PySide6 6.11.2. The dashboard as
shipped took 53.9 ms a frame of its 200 ms budget: 27.5 ms of simulation and
26.3 ms of interface. The table gives each arm's mean difference from the
shipped dashboard, paired by rotation, with its 95% confidence interval.

| Arm | Interface, ms per frame | Paint stage alone, ms |
| --- | --- | --- |
| `TrialStyle` is the application's style, every style sheet kept | +0.66 (+0.19 to +1.13) | +0.33 (+0.17 to +0.49) |
| The same, and `TrialStyle` draws the three run controls | +0.37 (-0.16 to +0.90) | +0.20 (+0.04 to +0.36) |
| The application keeps Fusion, and `TrialStyle` is set on the three run controls alone | -0.18 (-0.85 to +0.48) | 0.00 (-0.20 to +0.19) |
| `EveryCallThroughPythonStyle` is the application's style | +1.62 (+1.12 to +2.13) | +0.65 (+0.49 to +0.80) |

The last arm was measured in a second run of 20 rotations against the
shipped dashboard alone. `TrialStyle` reimplements three of a style's
functions, so only calls to those enter Python. The last arm reimplements
eight, which is nearer what a style for six controls needs. In that second
run the simulation stage, which a style cannot change, read 0.79 ms faster
under the second arm (-1.14 to -0.44), so a two-arm rotation carries an order
effect of about that size.

So a slowdown is measurable when the style is the application's style: 0.4
to 0.7 ms a frame with three functions and 1.6 ms with eight, which is 0.2%
to 0.8% of the 200 ms budget. It is not measurable when the style is set on
the controls alone. One repaint of one button took 32.7 microseconds as a
style sheet and 44.8 as the custom style (`paint-cost`, median of 2,000). A
control repaints when its state changes, not on every frame.

*Test 2, the same look in the light and the dark appearance.* Against a
simulated dark host, with the interface's colours declared on it, the custom
style drew the same pixels as under the light host in all five states. A
plain unavailable button, as the guard, drew differently. The owner's Mac has
not been tried yet.

*Test 3, no image files.* Neither arm of the button needs one. The control
that does is the check box. The trial's style sheet styles the indicator and
names no image, and its checked box has no tick. `TrialStyle` paints the
tick with `QPainter`.

*What else the trial showed.*

1. The two arms draw the same button. Both are 54 by 25 pixels for "Start".
   Of 1,350 pixels, 73 to 112 differ, all within 4 pixels of the edge except
   4 in the focus state, where the two round the corner with different code.
2. Style sheets keep working under the custom style. With `TrialStyle` as the
   application's style and every sheet kept, the dashboard at 120 s differed
   from the shipped one only at the six legend check boxes, which
   `TrialStyle` draws. Every widget that a style sheet draws was
   pixel-identical. So controls can move one at a time.
3. An application-wide style restyles every instance of a control with no
   call site. The six legend check boxes changed without any of them being
   named.
4. A style must read the `Active` group of the palette by name. A disabled
   widget's palette resolves to the `Disabled` group, which this project
   leaves to the host.
5. Qt advises against setting a style on single widgets. Its `QWidget::setStyle`
   page says: "Real applications should avoid it and use one consistent GUI
   style instead", and "Setting a widget's style has no effect on existing or
   future child widgets" (https://doc.qt.io/qt-6/qwidget.html, Qt 6.12.0,
   full page fetched and searched on 2026-11-11). So the arm with no measured
   cost is the one Qt advises against.
6. On the owner's Mac the application runs Qt's macOS style today. With a
   style over Fusion as the application's style, every control that no style
   sheet draws, such as a scroll bar or a spin box, takes Fusion's look. The
   `dashboard` command shows it.

**Decision needed.** Two answers from the owner. [Both recorded below, 2026-11-11.]

1. *What the Mac shows.* Run the comparison window and the dashboard under
   the light and the dark appearance, with the steps in the pull request body
   and the reply of 2026-11-11.
2. *Whether test 1 passed.* The test was written as "no measurable
   slowdown". With the style as the application's style, 20 paired runs
   measure one: 0.4 to 1.6 ms of a frame that takes 54 ms and has 200 ms.

**Answer 2, test 1 counts as passed** (project owner, 2026-11-11, ratified).
The owner replied "agree" to the reply that recommended counting the
frame-cost test as passed. It was chosen over counting the test as failed on
its wording, which would have built the controls as style sheets. The style
is to be installed on the application, as Qt advises. Answer 1, what the Mac
shows, is still open.

**The owner's Mac, first run, 2026-11-11.** The owner ran the comparison
window, recorded both appearances, and sent a picture of the window under
Light. Both rows read "DIFFERENT PIXELS under Dark and Light": the style
sheet's row as well as the custom style's. In the picture the two rows look
alike. The window did not yet say where the pixels differ.

The lettering is the likely place, and this is a reading of Qt's source, not
yet a measurement on the Mac. `QCoreTextFontEngine::imageForGlyph`
(`src/gui/text/coretext/qfontengine_coretext.mm` at tag `v6.11.0`, fetched
from GitHub and read on 2026-11-11; PySide6 here is 6.11.2) draws each letter
with a black fill unless the platform's colour scheme is Dark, and with a
white fill when it is. Its comment says that macOS's grey-scale font
smoothing "adjusts its dilation (stem darkening) parameters based on the fill
color", and that "we use the application's current appearance to decide
whether to draw with white or black fill". So the same dark lettering on the
same light surface can be drawn a little heavier under one appearance than
the other, whichever arm draws the button. The declared colours should not
move: `QGuiApplicationPrivate::setPalette` (`qguiapplication.cpp`, same tag)
keeps every role the application set and fills only the others from the
host's theme.

The window now records each row twice, with its lettering and without, and
reports the number of differing pixels, the largest colour step, and whether
the buttons without lettering are the same. It also saves
`out/style-trial-difference.png`, which shows each row under each appearance
and the pixels that differ. If the second run reports that only the
lettering differs, in both rows, the difference belongs to Qt's text drawing
and the shipped style sheets have it too, so it does not count against the
custom style. Whether the two appearances look the same is still the owner's
to say.

**The owner's Mac, second run, 2026-11-11.** The owner recorded Dark and
then Light, and sent the window under each and the difference picture.

- The style sheet's line read "DIFFERENT PIXELS under Dark and Light: 960
  pixels in 5 of 5 buttons, largest colour step 72 of 255. Drawn without
  lettering the buttons are THE SAME". The window's edge cut off the rest of
  the line and the custom style's line.
- The difference picture shows the custom style's row. In both rows the
  differing pixels are the letters of "Start" in all five buttons, and no
  pixel of an edge or a fill.
- In the picture the lettering is heavier under Dark than under Light, by
  the same amount in both rows. `PL-YZ9L` records this for the whole
  interface.
- Of the dashboard with the custom style as the application's style, under
  both appearances, the owner wrote "Item 5 looks the same".

**Answer 1, test 2 counts as passed** (session's reading of the owner's
run, 2026-11-11). The test asks whether the custom style looks the same
under both appearances. Everything the custom style draws is pixel-identical
under both. The lettering differs, Qt's text drawing causes that, and it
differs in the same way under a style sheet. The session took this reading
without asking, because the measurement leaves one reading.

**Result: the trial passes, and the interface pass builds its controls in
the custom style.** Test 1 counts as passed by the owner's answer, test 2 by
the run above, and neither button needs an image file. By the rule the owner
approved on 2026-11-10, each control is built in the style, and that
control's style sheet is deleted as it moves. The style is installed on the
application. `PL-8G4V` moves `TrialStyle` into `src/anesthesia_sim/app/` with
the first control and deletes the trial's two files.

**Blind review, 2026-11-11, and what it changed.** One blind review pass
read the branch and named five points. All five were real.

1. *The pixel count read freed memory.* `difference_between` copied each
   image's buffer after the image was freed. In the web container 40 bytes
   of 5,400 in such a copy were wrong, at the start and the end of the
   buffer, so a difference in the first or the last pixels went uncounted.
   Fixed, with a check. The Mac's count of 960 pixels and its largest
   colour step of 72 came through this fault, so each may be off by a few
   pixels a button. The difference picture reads each pixel by another
   route and shows the same result: only the lettering differs.
2. *The custom style's line on the Mac was never read.* The window did not
   grow with the lines it wrote, so the last line was cut off. Fixed, with
   a check. Test 2's result for the custom style therefore rests on the
   difference picture and on the owner's report of the dashboard, and the
   sentence "Everything the custom style draws is pixel-identical under
   both" in "Answer 1" claims more than was read. What the picture shows is
   that the custom style's rows differ only in the letters of "Start", and
   that the letters keep their colour under both appearances and are
   heavier under Dark. A label that took its colour from the host would
   change colour. The simulated dark host gave the same pixels in all five
   states. The session kept its reading that test 2 passed.
3. *The frame-cost arms ran in the same order in every rotation*, so an
   arm's place in the rotation was added to its difference from the
   shipped dashboard. Fixed: each rotation now starts one arm later
   (`rotation_order`), and the comparison prints each arm's paired
   difference from the first arm, which no code in the tree did before.
   The rerun is below, and it replaces the table under "Test 1".
4. *The trial's check box indicator is a placeholder too.* `PL-8G4V` now
   says so, and says to leave the indicator to Fusion until it is designed.
5. *No code in the tree made the pixel comparison with the shipped
   dashboard.* A scratch script made it. `PL-8G4V` now says to write it as
   a test with the first control.

**Rerun of test 1 with the corrected order, 2026-11-11.** The same command,
all five arms, 20 rotations, in the web container on PySide6 6.11.2. The
shipped dashboard took 55.0 ms a frame: 27.7 ms of simulation and 27.0 ms of
interface. Each figure is the arm's mean difference from the shipped
dashboard, paired by rotation, plus or minus two standard errors.

| Arm | Interface, ms per frame | Paint stage alone, ms | Simulation stage, ms |
| --- | --- | --- | --- |
| `TrialStyle` is the application's style, every style sheet kept | +0.37 ± 0.78 | +0.11 ± 0.26 | +0.25 ± 0.62 |
| The same, and `TrialStyle` draws the three run controls | +0.30 ± 0.78 | +0.14 ± 0.25 | +0.04 ± 0.70 |
| The application keeps Fusion, and `TrialStyle` is set on the three run controls alone | -0.55 ± 0.86 | -0.18 ± 0.31 | -0.43 ± 0.83 |
| `EveryCallThroughPythonStyle` is the application's style | +1.02 ± 0.69 | +0.46 ± 0.25 | -0.80 ± 0.59 |

With three functions reimplemented, the rerun cannot tell the custom
style's cost from zero. With eight, the interface takes about 1 ms more a
frame, which is 0.5% of the 200 ms budget. The simulation stage, which a
style cannot change, still read 0.80 ms faster under the last arm, so this
harness does not resolve a difference smaller than about 1 ms. The first
run's "0.4 to 0.7 ms with three functions and 1.6 ms with eight" was
therefore stated more finely than the harness supports. The owner's answer
that test 1 counts as passed was given on those figures. The rerun's are
smaller, so the answer is unchanged.

[Answered 2026-11-11: see "Answer 1", "Answer 2" and "Result" above.]
**Recommended.** Count test 1 as passed, and install the style on the
application as Qt advises. The test was written to find out whether drawing
in Python costs enough to matter here. It costs at most 0.8% of the frame
budget, and the frame has 146 ms to spare. The cost would matter if it
approached that spare time, and 1.6 ms is 1% of it. If the Mac shows the
same button in both appearances, the trial passes, and the controls are
built in the custom style. The owner decides this because the test's wording
is a decision the owner ratified, and a measurement that meets its purpose
but not its wording goes back to them.

**Done when.** The owner's two answers are recorded here with the choice of
mechanism. If the custom style is chosen, an item moves `TrialStyle` into
`src/anesthesia_sim/app/` with the first control built in it, and the trial's
two files are deleted there. If style sheets are chosen, the two files are
deleted and this item names the test that failed.
