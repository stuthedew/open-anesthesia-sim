---
id: PL-LS34
title: A setting's preview appears only while a pointer drags its slider, so a keyboard or screen-reader user cannot see what a change would do before making it
priority: P3
effort: M
status: needs-decision
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/chart_frame.py
deferred-from: v0.7.0 - found after the freeze, not safety or science, and no user sees a wrong value from it; a setting applies from the keyboard as it always has, and only its preview is missing there, so the release waits only on the owner test drive (filed 2026-11-28)
added: 2026-11-28
payoff: a keyboard user can see what a setting change would do before making it, as a pointer user can
---

**Problem.** The concentration chart and the wash-in plot draw a preview of a setting only while a pointer holds a setting slider's handle (`qt_widgets.ParameterSlider`, `PL-5B1N`). A key press, a wheel step, a click on the track and a screen reader's own command to set the value each apply the setting at once and draw no preview, because the slider starts a preview only when its handle is pressed or dragged (`_on_thumb_pressed` and `_on_thumb_moved`). `test_a_key_step_applies_at_once_and_previews_nothing` in `tests/integration/test_qt_widgets.py` and `test_a_click_on_a_slider_s_track_applies_at_once_and_draws_no_preview` in `tests/integration/simulation_view/test_simulation_view_controls.py` hold that a key and a click draw no preview. `test_a_value_set_by_assistive_technology_applies_once_in_the_setting_s_unit` in `tests/integration/test_qt_widgets.py` holds that a screen reader's command applies at once. So a user who works from the keyboard, or who cannot drag, never sees what a change would do before making it.

**Why it matters.** WCAG 2.2 SC 2.1.1 (Keyboard, Level A) asks that all functionality be operable through a keyboard interface. Its one exception is input that depends on the path of the movement, and a preview depends only on where the handle stands. SC 2.5.7 (Dragging Movements, Level AA) asks that functionality that uses dragging can also be done by a single pointer without dragging (Understanding SC 2.1.1, https://www.w3.org/WAI/WCAG22/Understanding/keyboard, and Understanding SC 2.5.7, https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements, both read 2026-11-28). `docs/INTERFACE.md` § "Color contrast, and the standard this interface is held to" holds the interface to Level AA and says that keyboard operation beyond the layout is planned and not yet a commitment (`ROADMAP.md` § "20. Accessibility"). How a drag previews and a key applies is a ratified decision (`PL-5B1N`, project owner, 2026-09-27, ratified), so a keyboard route to the preview reopens it on this evidence. I suggest P3, with the rest of `ROADMAP.md` § 20.

**Approach.** A design round decides how a keyboard user and a single click show a setting's preview before it applies, and what then applies it and what cancels it. It should start from how other simulators and the platform guides handle a provisional value, as `.claude/rules/expert-review.md` § "Search the closest analog first" says.

**Decision needed.** How a keyboard user, and a pointer user who does not drag, show a setting's preview before it applies, and what then applies or cancels it. The answer reopens `PL-5B1N`, a ratified decision, so the design round's recommendation goes to the project owner with its sources.

**Recommendation.** None yet, because none is owed before the research. No simulator, Blender or platform guide has been read on how a keyboard shows a provisional value, and the design round reads them first, as `.claude/rules/expert-review.md` § "Search the closest analog first" says.

**Done when.** A keyboard user can show a setting's preview, apply it and cancel it without a pointer, and a test holds a preview from the keyboard.

**How it was found.** Closing `PL-MP1X`, 2026-11-28: before adding the preview to the charts' text alternatives, the check of whether a keyboard reaches a preview found that nothing but a pointer drag does.

**Generator check.** No head states the fact misread here, which is that a preview is functionality every input must reach, not only a pointer. `PL-5B1N` gave the preview to the drag alone and the key press its immediate step, and this is the first item to name the keyboard gap.
