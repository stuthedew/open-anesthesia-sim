---
id: PL-MP1X
title: The concentration chart's and the wash-in plot's text alternatives leave out the predicted curve a held drag draws, so a screen reader is not told what the preview shows
priority: P3
effort: S
status: done
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_chart_frame.py, docs/INTERFACE.md
deferred-from: v0.7.0 - found after the freeze, not safety or science, and no user sees a wrong value from it; a preview needs a pointer drag, so the release waits only on the owner test drive (filed 2026-11-28)
added: 2026-11-28
closed: 2026-11-28
pr: 2361
payoff: a screen-reader user who drags a setting hears that a preview is drawn, and of which setting and value, as the plot's label tells a sighted user
tests: tests/unit/test_chart_frame.py::test_each_chart_s_text_alternative_names_a_preview_while_a_drag_draws_one
---

**Problem.** While a reader holds a drag on a setting, the concentration chart and the wash-in plot draw the run's predicted curve under the new setting as a preview (`chart_frame.RunFrame.preview`). Neither chart's text alternative mentions it. `chart_frame.latest_values_lines` and `chart_frame.latest_wash_in_lines` read only the drawn run, so a screen-reader user hears the same description during a drag as before it.

**Why it matters.** WCAG 2.2 SC 1.1.1 asks that a text alternative serve the same purpose as the graphic (Understanding SC 1.1.1, https://www.w3.org/WAI/WCAG22/Understanding/non-text-content, read 2026-11-27). The preview is how the interface shows what a change would do before it is made. The chart's off-scale notice already names a clipped preview's peak, because nothing else on screen states a preview's values (`dashboard_frame.off_scale_notice`, `PL-5B1N`). A drag needs a pointer, so a keyboard or screen-reader user may rarely see a preview at all, which is the reason to check first whether the preview can be reached without one. I suggest P3.

**Approach.** First find out whether a keyboard adjustment of a dial shows a preview. If it does not, record that the preview is reachable only by pointer, and that the text alternative therefore has nothing to add, as a dated paragraph here. If it does, add one sentence per previewed run to each description, worded as the hover words a preview point, with the instant at the preview's end.

**Done when.** Either the dated paragraph above, or a test that holds a preview on each chart and reads its sentence in the description.

**How it was found.** The second blind review of `PL-R1M6`, 2026-11-28, noted that the wash-in description says nothing during a preview. The concentration chart's description, which `PL-T9RB` built, leaves it out in the same way.

**Generator check.** No head states the fact misread here, which is what a chart's text alternative has to cover: every curve the chart draws, a preview among them. `PL-T9RB` and `PL-R1M6` built the two descriptions from the drawn run alone, and this is the first item to name the gap.

**Checked 2026-11-28: only a pointer drag shows a preview.** A key press, a wheel step, a click on the track and a screen reader's own command to set the value each apply the setting at once and draw no preview. In `src/anesthesia_sim/app/qt_widgets.py`, `ParameterSlider` starts a preview only when its handle is pressed or dragged (`_on_thumb_pressed` and `_on_thumb_moved`), and `_SettingSlider.apply_from_assistive_technology` applies a screen reader's value as one input, like a key press. `test_a_key_step_applies_at_once_and_previews_nothing` in `tests/integration/test_qt_widgets.py` and `test_a_click_on_a_slider_s_track_applies_at_once_and_draws_no_preview` in `tests/integration/simulation_view/test_simulation_view_controls.py` hold that a key and a click draw no preview. So a keyboard user never meets a preview, and a screen-reader user meets one only while dragging with a pointer. That user still hears only the drawn run, so this item's gap stands. The check found a second gap: the preview has no keyboard route at all, which WCAG 2.2 SC 2.1.1 asks for at Level A. `PL-LS34` records it.

**Checked 2026-11-28: the hover never words a preview point.** `chart_frame.RunPreview`'s docstring says the hover reads only `RunFrame.times_s` and `RunFrame.wash_in`, so the approach's "worded as the hover words a preview point" has nothing to copy. The only words the screen gives a preview are its label, such as "Preview: Fresh gas flow 6.0 L/min, not applied" (`dashboard_frame.preview_label`), and the off-scale notice's peak for a clipped preview. A text alternative states no value the screen does not show, as `chart_frame.latest_values_lines` says. So each description gains the preview's label as one line, after the run's values, and states no predicted value.

**Fixed 2026-11-28.** `chart_frame.preview_label_lines` gives one sentence for each run that draws a preview: the label the plot draws in the preview's region, with a full stop, such as "Preview: Fresh gas flow 6.0 L/min, not applied.". `dashboard_frame.concentration_chart_description` and `dashboard_frame.wash_in_plot_description` read it after the runs' values. The concentration chart draws the preview's region and label even with every compartment unchecked (`qt_chart.ConcentrationChart.draw`), so its description gives the label after the no-traces sentence too. Neither description gives a predicted value, because `docs/INTERFACE.md` § "A preview of an unapplied setting" says no value on a preview curve is printed as a reading. `docs/INTERFACE.md` gains a paragraph after the wash-in plot's text alternative that says so.

**Regression check.** The new test fails on the code before the fix (`git stash push src/anesthesia_sim/app/chart_frame.py src/anesthesia_sim/app/dashboard_frame.py`, then `pytest tests/unit/test_chart_frame.py::test_each_chart_s_text_alternative_names_a_preview_while_a_drag_draws_one`), with "At index 2 diff: '1 MAC sevoflurane (age 40) = 1.8%, reference adult (alveolar).' != 'Preview: Fresh gas flow 6.0 L/min, not applied.'".

**Blind review.** `PL-596J`'s record lists the four findings of the passes that ran on this branch. Items 3 and 4 there are this item's, and both are fixed.

**Documents checked.** `docs/INTERFACE.md` gains a paragraph after the wash-in plot's text alternative, and its § "A preview of an unapplied setting" needed no change. `PL-LS34` no longer carries the descriptions, since this item adds them.
