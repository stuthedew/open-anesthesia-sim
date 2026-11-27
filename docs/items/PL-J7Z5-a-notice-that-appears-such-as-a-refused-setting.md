---
id: PL-J7Z5
title: A notice that appears, such as a refused setting, a stopped run or the approaching run-length stop, is never announced to a screen reader
priority: P2
effort: S
status: done
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_widgets.py, tests/integration/test_qt_widgets.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-23
closed: 2026-11-27
pr: 2333
payoff: a screen-reader user hears a refused setting, a failure or a stopping run when it happens
tests: tests/integration/test_qt_widgets.py::test_each_new_banner_is_read_out_once_and_a_warning_interrupts, tests/integration/test_qt_widgets.py::test_a_banner_written_twice_in_one_action_is_read_once_as_it_ends, tests/unit/test_dashboard_frame.py::test_a_countdown_keeps_one_topic_while_its_time_left_changes, tests/integration/simulation_view/test_simulation_view_refusals.py::test_a_refused_setting_and_a_halt_are_read_out_at_once_and_once_only, tests/integration/simulation_view/test_simulation_view_run_stops_itself.py::test_the_countdown_and_the_stop_at_the_supported_run_length_are_each_read_out_once
---

**Problem.** When the banner shows a refused setting, a stopped run, a failure or the approaching run-length stop, nothing tells a screen reader. The banner is a `NoticeLabel` whose text changes, and no accessibility event is sent, so a screen-reader user is not told unless they move to the banner.

**Why it matters.** The banner carries the notices that `docs/INTERFACE.md` requires a reader to see at the moment they apply. Qt has offered an announcement event since 6.8, with a polite and an assertive priority, and Qt's documentation says "Assertive should not be used unless the interruption is imperative" (Qt, QAccessible Class, https://doc.qt.io/qt-6/qaccessible.html, read 2026-11-23). This project's floor is PySide6 6.12 (`pyproject.toml`), so the event is available. I suggest P2, because a failure halts the run silently for this reader.

The same applies to the status messages that `docs/INTERFACE.md` names under WCAG 2.2 success criterion 4.1.3, such as the caption that says a pinned Workspace will not draw a comparison. That passage says nothing announces it yet.

**Approach.** Send a `QAccessibleAnnouncementEvent` from the banner when its text changes to a new notice. Use the assertive priority for a failure and a refused setting, which ask the reader to act, and polite for the run-length countdown and the muted stop. Test it with a recorded event handler, since the offscreen platform has no screen reader.

**How it was found.** `PL-QR6Q` built the dashboard offscreen on 2026-11-23, under PySide6 6.12, and walked the tree that `QAccessible.queryAccessibleInterface` returns for the main window, reading each node's role, name, value and description. That tree is what Qt hands to the platform's accessibility interface. It is not what a screen reader says, which `PL-H1D9` checks.

**Done when.** A test with a recorded accessibility event handler shows that each new banner notice sends one announcement, assertive for a failure and a refused setting and polite for the run-length countdown and the muted stop.

**Priority, researched 2026-11-23.** WCAG 2.2 success criterion 4.1.3 Status Messages is Level AA: status messages "can be programmatically determined ... such that they can be presented to the user by assistive technologies without receiving focus" (W3C, WCAG 2.2, https://www.w3.org/TR/WCAG22/, read 2026-11-23). It is above the Level A minimum, and the notices are on screen for a sighted reader, so P2.

**Generator check.** A one-off: Qt sends no event for a label's text change, and nothing here sent one.

**Built 2026-11-27.** `qt_widgets.announce` sends a `QAccessibleAnnouncementEvent`, and `NoticeLabel` sends one for each new banner: the run banner, the bookmark forms' refusals and the branch control's refusal. The branch control's caption that takes its place is announced when it appears or changes. A banner in the warning colour is assertive and any other is polite. `dashboard_frame.Notice` gains a `topic`, which for the countdown is its wording without the time left, so the countdown is read once and not every second. The label announces once control returns to the event loop, as the banner then stands.

**Sources, read 2026-11-27.** Qt 6.12's `QAccessibleAnnouncementEvent` page and the `QAccessible::AnnouncementPoliteness` entry (https://doc.qt.io/qt-6/qaccessible.html): polite waits for "the next graceful opportunity", assertive should "notify the user immediately", and assertive "should not be used unless the interruption is imperative". The Understanding document for WCAG 2.2 SC 4.1.3 (https://www.w3.org/WAI/WCAG22/Understanding/status-messages, read in full): status messages are presented "without receiving focus".

**Decision, 2026-11-27: announce once per return to the event loop.** A halt writes its banner before its frame and again from the frame (`RunView._halt_run`). Announced on each write, the second assertive announcement interrupts the first, so a reader hears the start of a banner that no longer stands. Deferring the announcement to a zero-interval timer owned by the label reads only the banner that stands. A probe showed the two announcements before the change.

**Regression run, 2026-11-27.** `uv run pytest -q -p no:randomly tests/integration/simulation_view/test_simulation_view_refusals.py tests/integration/simulation_view/test_simulation_view_run_stops_itself.py tests/integration/test_qt_widgets.py tests/unit/test_dashboard_frame.py -k "read_out or read_once or countdown_keeps_one_topic"`, with `src/` stashed, failed all five. The dashboard refusal test, which needs no interface the fix added, failed with "assert [] == [Announcement...ssertive: 1>)]", and the countdown test with "assert [] == [<Announcemen...ss.Polite: 0>]". The two label tests failed with "TypeError: NoticeLabel.set_notice() got an unexpected keyword argument 'topic'" and "assert [] == [Announcement...]", and the topic test with "AttributeError: 'Notice' object has no attribute 'topic'".

**Left for later.** When every run halts at once, each run's assertive banner interrupts the one before it. `PL-MP92` holds it.

**Docs swept.** `docs/INTERFACE.md` gains the requirement in § "Color contrast, and the standard this interface is held to", and the pinned-Workspace caption's paragraph no longer says nothing announces it. `docs/ARCHITECTURE.md`, `README.md` and `docs/MODEL.md` needed no change.
