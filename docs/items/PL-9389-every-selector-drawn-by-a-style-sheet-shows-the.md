---
id: PL-9389
title: Every selector drawn by a style sheet shows the platform's drop-down button through its rounded frame, as a bracket and shadow in the right corner, because the sheet styles the frame and not the button
priority: P2
effort: S
status: ready
classes: defect, ux
feature: interface-design-review
touches: src/anesthesia_sim/app/stylesheets.py, src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/app/run_view.py, tests
deferred-from: v0.7.0 - captured after the freeze; a drawing defect in the selectors, and no displayed value is wrong
added: 2026-11-22
payoff: every selector shows one clean arrow in its own colours, with no platform button showing through its frame
---

**Problem.** Every selector drawn by a style sheet shows the platform's drop-down button through its rounded frame, as a bracket and shadow in the right corner, because the sheet styles the frame and not the button

**Found by** the project owner on his Mac, in the Branch View's "From"
selector (screenshot in the thread, 2026-11-22). The same bracket shows
offscreen under Fusion on every selector that uses `selector_stylesheet` or
`agent_selector_stylesheet`: the agent selector, playback rate, time base,
Branch "From", and the agent cost View's agent and unit selectors. The design
review on 2026-11-22 missed it.

**Cause.** The two style sheets draw a combo box's frame and padding, and no
rule for its drop-down button. Qt's style sheet reference treats that button
as a part with its own rule, `::drop-down`, placed by default in the top right
corner of the padding rectangle (https://doc.qt.io/qt-6/stylesheet-reference.html,
the QComboBox entry, read 2026-11-22). With no rule for it, the platform style
draws its usual button there, inside the sheet's rounded frame.

**Why it matters.** The selector's frame looks broken at its right corner,
on every selector, including the agent selector that carries the agent's
ISO 5360 colour. Nothing about the value shown is wrong, but a control that
looks broken invites doubt about the screen around it.

**What was tried.** A `::drop-down` rule with no border and no fill stops the
button being drawn, and the arrow goes with it. A style sheet can draw the
arrow only from an image file, through `::down-arrow`. An image file would
hold a second copy of a theme colour, and the agent selector's arrow must take
each agent's foreground. The border trick that draws a triangle in a web
browser draws a rectangle in Qt (measured offscreen).

**Fix.** Both sheets carry a `::drop-down` rule that draws nothing, and right
padding of `MENU_ARROW_SIZE + 2 * MENU_ARROW_GAP` px, as the View chooser has.
`SelectorComboBox` in `app/qt_widgets.py` paints the arrow into that space: a
triangle `MENU_ARROW_SIZE` px wide in the colour the sheet gives the text,
drawn without smoothing. Every styled selector is built as one, and
`FocusedComboBox` and `TimeBaseSelector` inherit it. No colour changes: the
arrow uses the text's pair, which `tools/contrast_check.py` already holds to
4.5:1, above the 3:1 that SC 1.4.11 asks of a graphic.

**Regression run on the code before the fix.** The test needs
`SelectorComboBox`, so the variant builds a plain `QComboBox` with
`selector_stylesheet()` and checks the same pixels
(`scratchpad/regress_9389.py`, run on `f5c8227`). It fails with
`AssertionError: ['#555555', '#768493', '#8693A0', '#AAAAAA', '#BBC2C9', '#CCD1D7', '#EEF0F2', '#FFFFFF']`:
the platform button's greys, and no INK.

**Done when.** The arrow space of every styled selector holds only its fill
and its text colour, and every combo box in every View whose sheet hides the
platform button is a `SelectorComboBox`.

**Generator check.** One cause, six selectors: two style sheets that style the
frame and leave the button to the platform. Both carry the rule now, and
`test_every_selector_in_every_view_draws_its_own_arrow` fails a selector built
with either sheet that does not draw its arrow. Not a generator of other items.
