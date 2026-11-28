---
id: PL-PN2C
title: Concentration legend boxes have names that do not contain the label each one shows
priority: P3
effort: S
status: done
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/qt_chart.py, tests/integration/test_keyboard_focus.py, tests/integration/test_qt_chart.py, tests/integration/simulation_view/test_simulation_view_two_runs.py, tests/integration/approved_interface_strings.json, docs/INTERFACE.md, ROADMAP.md
deferred-from: v0.7.0 - found after the freeze, not safety or science, and no user sees a wrong value from it: each box shows its words and its checked state, and only its spoken name differs from them (triage 2026-11-28)
added: 2026-11-28
closed: 2026-11-28
pr: 2362
filed-pr: 2358
payoff: a speech-input user can say a legend box's shown words to click it, and a screen-reader user hears the words the box shows
tests: tests/integration/test_keyboard_focus.py::test_each_button_and_box_is_named_starting_with_the_words_it_shows, tests/integration/test_qt_chart.py::test_each_compartment_box_is_named_by_the_words_it_shows
---

**Problem.** Each compartment's box in the concentration chart's legend shows
its legend words, such as "Alveolar (solid)", from `trace_legend_label` in
`app/dashboard_frame.py`. A screen reader calls the same box "Draw the
Alveolar compartment on the chart", from `TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE`.
The name does not start with the words shown, and does not contain them. Every
other named control here starts its name with the label it shows, which
`docs/INTERFACE.md` applies as WCAG 2.2 SC 2.5.3 ("Label in Name").

The adversarial review of `PL-XV64` found this on 2026-11-28. It is older than
that item: the template is on `main` unchanged, and `PL-XV64` only adds the
Area's name after it.

**Why it matters.** A speech-input user clicks a control by saying the words it shows, and a screen-reader user hears its name. Understanding SC 2.5.3 (Label in Name, Level A; https://www.w3.org/WAI/WCAG22/Understanding/label-in-name, read 2026-11-28) says a mismatch makes the spoken command fail, and gives a text-to-speech user words that differ from the ones on screen. Its advice is "Where practical, make the control's text label and name match".

**Generator check.** Three items filed on 2026-11-28 share one cause: text a screen reader is told was written apart from the words the screen shows, and nothing compared the two. They are `PL-596J` (the band's line left out the legend's qualifier), `PL-MP1X` (the descriptions left out a preview's drawn label) and this item. The first two now build their lines from the words the chart draws. This item names each box by its own words, and adds a check over every button and box shown in each shipped Workspace that its name starts with the words it shows, so a later control cannot repeat the fault unseen. No head is filed, because these fixes remove the second copy in each place.

**Done when** each box's name starts with the words the box shows, a test
writes out the expected name for at least three compartments by hand, and
`docs/INTERFACE.md` names that test.

**Fixed 2026-11-28.** `TraceLegend.name_boxes` in `app/qt_chart.py` names each compartment's box by `trace_legend_label`, the words the box shows, such as "Alveolar (long dash)", and adds the Area's name where two Areas show the chart. `TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE` is gone. The action words "Draw the Alveolar compartment on the chart" were first moved into each box's accessible description, then dropped, because Qt 6.12's macOS bridge hands a description to VoiceOver as the element's label and the name as its title (`qcocoaaccessibilityelement.mm` at tag v6.12.0 of `qt/qtbase`, read 2026-11-28), so a description could be read there in place of the box's words. A screen reader still says the box is a check box and whether it is checked, so its words and its state together say which trace it shows or hides. `PL-2XRN` records the five other controls that carry a description.

The fix's shape: `tests/integration/test_keyboard_focus.py` gains `test_each_button_and_box_is_named_starting_with_the_words_it_shows`, which walks every button and box shown in each shipped Workspace, with one run and with two compared, and fails where a name does not start with the words shown, compared word by word without case, punctuation or Qt's mnemonic mark. `qt_widgets.label_control` already refused such a name for a control labelled by a separate label, and nothing did for a button or a box. `docs/INTERFACE.md`'s paragraph on Label in Name says so, and names both new tests.

**Regression check.** Both new tests fail on the code before the fix (`git stash push src/anesthesia_sim/app/qt_chart.py src/anesthesia_sim/app/dashboard_frame.py`, then `pytest "tests/integration/test_keyboard_focus.py::test_each_button_and_box_is_named_starting_with_the_words_it_shows"`), with "QCheckBox shows 'Circuit (solid)' but is named 'Draw the Circuit compartment on the chart'" for each of the six boxes and no other button or box.

**Blind review.** Two rounds of two passes ran.

1. Round 1, pass 1, optional: the new check compared characters, so "Settings" passed as starting with "Set". Fixed: it compares whole words.
2. Round 1, pass 2, should-fix: nothing showed what each platform's bridge does with the description. Fixed: the Qt 6.12 bridges were read, and the description was dropped because macOS reads it as the label.
3. Round 1, pass 2, optional: `docs/INTERFACE.md` said every button and box is named so, while the test walks only what each shipped Workspace shows at first, with one run or two. Fixed: the paragraph says what the test covers.
4. Round 2, pass 1, optional, and round 2, pass 2, optional, repeated: the whole-interface walk test asserted only the boxes' words, which the walk yields as shown text, so it no longer showed that the walk reads accessible names. Fixed: it also asserts the legend scroll box's "Concentration chart legend", which only a screen reader is told.
5. Round 2, pass 2, should-fix: `PL-2XRN` listed five layout controls and was deferred, while the same macOS mapping could give a Mac user the schematic's modelled values without the run and instant that only its name carries. Fixed: `PL-2XRN` now lists every widget with a description, is classed `safety`, and is on v0.7.0's frozen list.

**Documents checked.** `docs/INTERFACE.md`'s paragraph on Label in Name, which gains the boxes' naming and the two tests, its list of the controls that add the Area's name (points 4 and 5), which still holds because the boxes add it as before, and the sentence under the table of the six compartment traces on the legend's words, which needed no change. `docs/ARCHITECTURE.md`'s lines for `qt_chart.py` and `dashboard_frame.py` are still true. `ROADMAP.md`'s frozen list gains `PL-BQB6` and `PL-2XRN`.
