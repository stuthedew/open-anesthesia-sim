---
id: PL-YZ9L
title: On a Mac set to Dark, Qt draws the interface's lettering heavier than under Light, though the interface declares light colours
priority: P3
effort: S
status: done
classes: ux, defect
feature: chrome-colour-audit
touches: src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/main.py
deferred-from: v0.7.0 - present at the freeze, with no real connection to the frozen list or to v0.7.0's Required scope: a lettering weight under the Mac's Dark appearance changes no value and no layout the milestone builds, and its fix needs a Mac
added: 2026-11-11
closed: 2026-11-23
pr: 2298
filed-pr: 2118
payoff: The interface's lettering reads the same on a Mac set to Dark as under Light, as the declared appearance promises.
reenters: PL-KRZW
---

**Problem.** On a Mac set to the Dark appearance, the interface's lettering
is drawn slightly heavier than under Light. The interface declares its own
light colours whatever the host is set to (`PL-KRZW`), so its lettering is
dark on a light surface under both appearances and should be drawn the same.

**Evidence.** `PL-BVC5`'s comparison window, run on the owner's Mac on
2026-11-11, recorded the same five buttons under Light and under Dark. 960
pixels differed across the five buttons, with a largest colour step of 72 of
255. Every differing pixel was in the lettering, and the buttons drawn
without lettering were identical. A style sheet's buttons and a custom
style's buttons differed in the same way.

**Cause, read from Qt's source.** `QCoreTextFontEngine::imageForGlyph`
(`src/gui/text/coretext/qfontengine_coretext.mm`, tag `v6.11.0`, read on
2026-11-11) draws each letter with a black fill unless the platform's colour
scheme is Dark, and with a white fill when it is. Its comment says that
macOS's font smoothing "adjusts its dilation (stem darkening) parameters
based on the fill color". Qt chooses the fill by the host's appearance, and
the interface's surfaces do not follow that appearance.

**Not yet known.** Whether the difference can be seen at life size, and
whether it changes how a value reads. The measurement was at one device
pixel per pixel, enlarged four times.

**One route to try.** Tell Qt or macOS that this application's appearance
is Light, so that the text drawing agrees with the declared colours.
`qt_widgets.declare_application_colours` records that
`styleHints().setColorScheme` was ignored on 2026-09-20 in the container.
Nobody has tried it on a Mac.

**Checked 2026-11-22**, at `d4e8200c`. `grep -rn "setColorScheme\|NSAppearance\|NSRequiresAquaSystemAppearance" src/anesthesia_sim/` finds only the docstring in `qt_widgets.py` that explains why `declare_application_colours` uses a palette instead, so nothing yet tells Qt or macOS that this application's appearance is Light. The fault itself shows only on a Mac, so no session here can reproduce it.

**Why it matters.** The interface promises one appearance whatever the host is set to. Lettering drawn heavier under Dark breaks that promise, and if the change is visible at life size it alters how every label and value reads on the owner's own screen.

**Done when.** On a Mac set to Dark, the interface's lettering is drawn the same as under Light, or the item records, from a view at life size on a Mac, that the difference cannot be seen and why it is left.

**Generator check.** An instance of the fact that `PL-KRZW` (which palette roles each widget takes from the declared theme, and which from the host platform) names, filed after that head closed on 2026-09-22: Qt's text drawing still takes its fill colour from the host's appearance, which the declared palette does not reach.

**Fix built 2026-11-23.** `qt_widgets.declare_application_colours` now calls `application.styleHints().setColorScheme(Qt.ColorScheme.Light)` before it sets the palette. Three sources were read for it. The QStyleHints page (https://doc.qt.io/qt-6/qstylehints.html, Qt 6 documentation) says `setColorScheme` was added in Qt 6.8, is a hint that not every platform supports, and that Qt re-reads the system palette when the scheme changes, which is why the palette is set after it. `QCocoaTheme::requestColorScheme` (`src/plugins/platforms/cocoa/qcocoatheme.mm`, branch `6.10`, read on GitHub) sets `NSApp.appearance` to `NSAppearanceNameAqua` for Light, so on a Mac the request reaches macOS itself. `QCoreTextFontEngine::imageForGlyph`, read for the cause above, chooses the black fill once the scheme is no longer Dark. The new test `tests/integration/test_dark_appearance.py::test_declaring_the_application_asks_for_the_light_colour_scheme_before_its_palette` records the two calls in order. On `main` before the fix it fails with `assert ['palette'] == ['scheme Light', 'palette']`. The container's offscreen platform ignores the request, so only a Mac can show whether the lettering now matches.

**Review fixes, 2026-11-23.** Both blind review passes found that the button-drawing trial (`tests/benchmarks/style_trial.py`, from `PL-BVC5`) filed each recording under `styleHints().colorScheme()`, which now reports Light whatever the Mac is set to (QStyleHints: an explicit scheme "will override the system setting and ignore any changes to the system's color scheme", https://doc.qt.io/qt-6/qstylehints.html, read 2026-11-23). A recording under Dark would have replaced the one under Light. The window now has two buttons, "Record as Light" and "Record as Dark", and the reader names the appearance set in System Settings. One pass also found that `docs/INTERFACE.md` and the `declare_application_colours` docstring still said disabled controls and tooltips follow the host. On a platform that honours the request they now take the platform's light palette, and both texts say so.

**What remains.** The owner opens the trial window on his Mac with `uv run python tests/benchmarks/style_trial.py`, sets System Settings to Light (Appearance in the sidebar, then Light or Dark, from https://support.apple.com/guide/mac-help/use-a-light-or-dark-appearance-mchl52e1c2d2/mac, read 2026-11-23), presses "Record as Light", sets it to Dark and presses "Record as Dark". If both rows say THE SAME PIXELS, the item closes as done. If they still differ, the request did not reach the text drawing, and the item records what the window showed before another route is chosen.

**Confirmed on the owner's Mac, 2026-11-23.** The owner ran the button comparison window after #2273 merged, recorded it with System Settings set to Light and again set to Dark, and both rows read THE SAME PIXELS. Before the fix, the same comparison on 2026-11-11 found 960 differing pixels, all in the lettering. So the light request reaches the text drawing, and the item is done.

**Docs checked at close.** `docs/INTERFACE.md` (the Light request paragraph now records the Mac result), `src/anesthesia_sim/app/qt_widgets.py` (`declare_application_colours` docstring, still true), `tests/benchmarks/style_trial.py` (window and `Recording` docstrings, still true), `.claude/rules/ui-color.md` (says nothing about the scheme request; still true).

**A fault the fix's trial window brought, fixed 2026-11-23.** After the comparison, the owner's Mac printed "QObject: shared QObject was deleted directly. The program is malformed and may crash." The window's two record buttons from #2273 were connected to lambdas that held the window. Run through its real entry point and quit after two recordings, the window failed on exit in 11 of 15 runs in the cloud container at #2273's merge and in 0 of 15 at its parent. With the old trial file and the new `qt_widgets.py` it failed in 0 of 15, and with the new trial file alone in 12 of 15, so the buttons were the cause. Connected to bound methods (`record_light`, `record_dark`), it failed in 0 of 15. The container's failure was a heap abort, `malloc_consolidate(): unaligned fastbin chunk detected`, so the Mac warning is taken to be the same fault, and the owner is asked to confirm it is gone.

