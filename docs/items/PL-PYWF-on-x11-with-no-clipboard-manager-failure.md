---
id: PL-PYWF
title: On X11 with no clipboard manager, failure details copied with Copy details are lost when the application closes, and the refused-Reset banner tells the user to close and reopen it (found in PL-XWCH)
priority: P3
effort: S
status: done
classes: defect
feature: interface-design-review
touches: src/anesthesia_sim/app/dashboard_frame.py, tests/integration/approved_interface_strings.json
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-23
closed: 2026-11-27
pr: 2342
filed-pr: 2269
payoff: a user on Linux keeps the failure details they copied when the banner tells them to restart
tests: tests/unit/test_dashboard_frame.py::test_a_refused_reset_names_the_way_out_in_the_banner, tests/integration/simulation_view/test_simulation_view_run_stops_itself.py::test_a_refused_reset_names_no_setting_and_sends_the_reader_to_restart
---

**Problem.** On X11 with no clipboard manager, failure details copied with Copy details are lost when the application closes, and the refused-Reset banner tells the user to close and reopen it (found in PL-XWCH)

**Why it matters.** A user told to close and reopen the application loses the failure details they copied, on a Linux desktop with no clipboard manager, and cannot report the failure.

**Done when.** The refused-Reset banner tells the user to paste the details somewhere before closing, or the details are also saved to a file whose path the banner names. A test pins the banner text.

**Wording decided 2026-11-23.** Tell the user to paste the details before closing. This is a placeholder under the owner's rule that wording is the session's.

**Generator check.** A one-off: an X11 clipboard rule, which keeps a copy only while the owning application runs.

**Reproduced 2026-11-23.** `src/anesthesia_sim/app/dashboard_frame.py` still names closing and reopening the application as the way out.

**Done 2026-11-27.** The refused-Reset banner's way out now reads: "No setting can repair this, because only a fault in the simulator causes it. To keep the failure details, use Show details, then Copy details, and paste them elsewhere before closing, because closing the application can clear the copy. Then close and reopen the application to start a new run." (`REFUSED_RESET_WAY_OUT_TEXT`). It names both buttons in the order they are pressed, because the Copy details button stays hidden until Show details is pressed (`FailureDetails` in `app/qt_widgets.py`), and a refused Reset always gives the run new details, which folds them away. The first draft named only Copy details and said that button was on screen. Both blind review passes found that it is not. The sentence reads the two buttons' labels from their constants, and `test_a_refused_reset_names_no_setting_and_sends_the_reader_to_restart` now presses them in the banner's order.

The owner's rule of 2026-11-27 replaced the placeholder above: wording is decided from a cited source (`PL-HWZK`). Two sources say why the copy is lost. Qt 6's `QClipboard` documentation, "Notes for X11 Users", says that X11 has "the concept of ownership". The freedesktop.org Clipboard Manager Specification, "Responsibilities of clipboard owners", says that an owner that exits with no clipboard manager running "should simply exit", so nothing serves the copy afterwards. Both were read on 2026-11-27. The wording follows NUREG-0700 Rev. 3 (O'Hara, Brookhaven National Laboratory for the U.S. Nuclear Regulatory Commission, July 2020; full text from https://www.osti.gov/servlets/purl/1644018, read 2026-11-27), guideline 2.7.5-2, p. 2-89: "For conditions that may require special user attention to protect against information loss, an explicit alert or advisory message, or both, should prompt appropriate user action." The steps are in the order the user takes them.

Documents checked: `docs/INTERFACE.md` (the paragraph on a refused Reset now says to keep the details first, and names both buttons in their order), `README.md`, `docs/MODEL.md`, `docs/VERIFICATION.md` and `docs/PARAMETERS.md` (none quotes the banner; unchanged).
