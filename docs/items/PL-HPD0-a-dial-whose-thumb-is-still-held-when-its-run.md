---
id: PL-HPD0
title: A dial whose thumb is still held when its run starts over (an agent change or a Reset) applies its release value to the new run, though the preview of that value ended at the start-over (found building PL-1WFW)
priority: P2
effort: S
status: done
classes: defect
feature: interface-design-review
touches: src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/run_surfaces.py, src/anesthesia_sim/app/views.py, docs/INTERFACE.md, tests/integration/simulation_view/test_simulation_view_controls.py, tests/integration/simulation_view/test_simulation_view_views.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-22
closed: 2026-11-27
pr: 2334
payoff: a user who holds a dial through a reset does not set the new run without meaning to
tests: tests/integration/simulation_view/test_simulation_view_controls.py::test_a_thumb_held_when_the_run_starts_over_is_let_go_and_its_release_applies_nothing
---

**Problem.** A dial whose thumb is still held when its run starts over (an agent change or a Reset) applies its release value to the new run, though the preview of that value ended at the start-over (found building PL-1WFW)

**Found 2026-11-22** by the worker building `PL-1WFW`. That item ends a held preview when its run starts over or is renamed, so no label names an agent or run that is gone. The thumb is still down, though, and its release applies the value to the new run as an ordinary change. Whether a release after a start-over should apply is open: a user who held the dial through a key press that reset the run may not mean to set the new run. The behaviour is unchanged from before `PL-1WFW`.

**Why it matters.** A user who held a dial while a key press reset the run can set the new run without meaning to. The value is shown, so nothing is hidden, but the change was not the user's choice for that run.

**Decision needed.** When a run starts over while a dial's thumb is held, should the release apply the value to the new run, or should the gesture end at the start-over and the release do nothing?

**Recommendation (provisional).** End the gesture at the start-over, so the release applies nothing, because the preview it belonged to has already ended and the user never saw the value previewed on the new run. Research on how platforms treat a drag whose target is replaced is owed before this reaches the owner.

**Done when.** The decision is recorded here, and a test holds a dial across an agent change and a Reset and shows what the release does.

**Decided 2026-11-27, from the sources below: the gesture ends at the start-over, and the release applies nothing.** Each of the five input systems read below cancels a pointer gesture when something takes it away, and tells the program not to act on it. None of them lets such a gesture finish as if it had not been interrupted, so the research shows one option clearly correct and it is taken without asking (`.claude/rules/instruction-writing.md` rule 10). Each was read in full on 2026-11-27 from the page named:

1. Android, `MotionEvent.ACTION_CANCEL` (https://developer.android.com/reference/android/view/MotionEvent): "The current gesture has been aborted. You will not receive any more points in it. You should not perform any action that you normally would as a result of this gesture." And: "After an ACTION_CANCEL event, you should assume that all pointers that were down have been lifted."
2. Windows, `WM_CANCELMODE` (https://learn.microsoft.com/en-us/windows/win32/winmsg/wm-cancelmode): the system sends it "when a dialog box or message box is displayed", and "the DefWindowProc function cancels internal processing of standard scroll bar input, cancels internal menu processing, and releases the mouse capture."
3. W3C Pointer Events Level 3, § 4.1.3.3 "Suppressing a pointer event stream" (https://www.w3.org/TR/pointerevents3/): the user agent "MUST suppress a pointer event stream" when "The user agent has opened a modal dialog or menu", and the first step of suppressing one is "Fire a pointercancel event."
4. Apple UIKit, `UIResponder.touchesCancelled(_:with:)` (the page's JSON at https://developer.apple.com/tutorials/data/documentation/uikit/uiresponder/touchescancelled(_:with:).json): a responder should "clean up any state associated with handling the touch sequence."
5. Qt Quick, `MouseArea.canceled` (https://doc.qt.io/qt-6/qml-qtquick-mousearea.html): emitted "when mouse events have been canceled, because another item stole the mouse event handling", and "to reset the logic when the MouseArea has lost the mouse handling to the Flickable, canceled should be handled in addition to released."

A start-over is that case: the run the drag acted on is gone, and the user never saw the held value previewed on the new run. Applying it would set the new run with a value the user chose for another.

**Fixed 2026-11-27.** `_SettingSlider.cancel_hold` in `app/qt_widgets.py` puts the handle back at the value the slider holds and marks it not held, with its signals blocked. Until the button that held it is released, a move of the pointer moves nothing, and the release runs Qt's own release with signals blocked, so Qt no longer counts the handle as pressed and nothing is applied. A new press clears the mark. `ParameterSlider.cancel_hold` also forgets that a preview was shown, so no `preview_ended` follows, and `ParameterControls.cancel_holds` calls it for all four dials. `views.RunDials.show_dials` compares the presentation's start-over count, `RunPresentation.case`, with the one it last showed, and lets go of every held thumb before writing the new run's settings. The frame for a Reset or an agent change is drawn at once (`SimulationView.present`), so no release can come between the start-over and the let-go. `RunView` still drops the preview itself at the start-over, because the chart reads it in the same frame. A branch opened or dropped does not start the run over, so a held thumb there still previews on its next move, as before.

Two neighbouring cases were left as they are. A key held across a start-over repeats into the new run, but each repeat is a single input that applies at once and shows its value, as any key press does. Under Qt's Fusion style, a left button held on the track repeats a step in the same way. Neither carries a value chosen for the run that was discarded.

**Regression test.** `test_a_thumb_held_when_the_run_starts_over_is_let_go_and_its_release_applies_nothing` in `tests/integration/simulation_view/test_simulation_view_controls.py` presses the flow handle with the mouse, drags it, starts the run over by a Reset and by an agent change, moves further and releases, under Fusion and under the macOS slider hints. It checks that the handle was let go, followed no move, and that the release changed neither the settings nor the record of changes. Run against the code before the fix (`git stash push -- src/`, then `uv run pytest -q -p no:randomly -k let_go_and_its_release` on that file), all four cases failed at `assert held_after_start_over is False` with `assert True is False`. The two `PL-1WFW` tests in `tests/integration/simulation_view/test_simulation_view_views.py` that held a thumb across an agent change and a Reset asserted that it was still held. They now assert that it was let go.

**Docs swept 2026-11-27:** `docs/INTERFACE.md` § "A preview of an unapplied setting" (the Timing cue is rewritten, and its note for developers names the code and the test), and `docs/ARCHITECTURE.md`, `docs/MODEL.md`, `docs/VERIFICATION.md`, `README.md` and `ROADMAP.md`, searched for "held", "start over" and "release". Only `docs/INTERFACE.md` described this behaviour.

**Generator check.** A one-off, found building `PL-1WFW`; the behaviour predates it.
