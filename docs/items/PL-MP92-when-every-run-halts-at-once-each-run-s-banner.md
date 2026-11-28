---
id: PL-MP92
title: When every run halts at once, each run's banner interrupts the one before it, so a screen reader user hears only the last run's halt
priority: P3
effort: S
status: done
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_widgets.py, docs/INTERFACE.md, tests/integration/test_qt_widgets.py, tests/integration/simulation_view/test_simulation_view_refusals.py
deferred-from: v0.7.0 - found after the freeze, not safety or science, and no user sees a wrong value from it; it needs two compared runs and a frame that fails, so the release waits only on the owner test drive (filed 2026-11-27)
added: 2026-11-27
closed: 2026-11-28
pr: 2352
filed-pr: 2333
payoff: a screen-reader user hears every run's halt when several runs stop at once
tests: tests/integration/simulation_view/test_simulation_view_refusals.py::test_a_halt_of_every_run_reads_each_compared_run_s_banner_in_one_announcement, tests/integration/test_qt_widgets.py::test_banners_that_change_in_one_action_in_one_window_are_read_as_one_announcement, tests/integration/test_qt_widgets.py::test_a_message_asked_for_twice_in_one_action_is_read_once, tests/integration/test_qt_widgets.py::test_each_message_read_before_another_in_one_announcement_ends_a_sentence, tests/integration/test_qt_widgets.py::test_a_banner_whose_label_is_deleted_before_the_action_ends_is_not_read, tests/integration/test_qt_widgets.py::test_each_window_reads_its_own_announcements
---

**Problem.** When a frame cannot be drawn, `SimulationView` halts every run at once, and each run's banner then changes in the same action. `PL-J7Z5` announces each banner from its own label (`qt_widgets.NoticeLabel`), and a failure interrupts what is being read. So with two runs compared, the second run's announcement interrupts the first, and a screen-reader user hears only that the second run stopped.

**Why it matters.** Qt's documentation for `QAccessible.AnnouncementPoliteness` says an assertive announcement should be conveyed at once, interrupting other speech (read 2026-11-27). The first run's halt is then never heard, although its banner says why it stopped. Each run's banner names its run while two are compared, so joining them loses nothing. I suggest P3, because it needs two runs and a frame that fails.

**Approach.** Collect the announcements made within one return to the event loop in one place per window, and send them as one announcement, assertive if any of them is. The single-label coalescing in `NoticeLabel._announce` is the pattern to extend. The collector must not be a module-level value, because a View can be built more than once (`.claude/rules/ui-areas.md`).

**Done when.** A test that halts two compared runs at once, with the announcement recorder in `tests/integration/announcement_support.py`, shows one assertive announcement that holds both runs' banners.

**How it was found.** Building `PL-J7Z5`, 2026-11-27, while checking what a halt announces.

**Decided 2026-11-28 (triage).** The brief's approach is the one the standard
supports, so it is taken without a question. WAI-ARIA 1.2's definition of `aria-live`
(https://www.w3.org/TR/wai-aria-1.2/, read 2026-11-28) says that for an
assertive region a screen reader "could potentially clear the speech queue of
previous updates", and that "User agents or assistive technologies MAY choose to
clear queued changes when an assertive change occurs." Sending the second halt
as a polite announcement would not help, because a polite announcement waits
for a pause and can still be cleared by the next assertive one. One
announcement holding every message cannot lose any of them. The collector
takes every announcement the window asks for, not only the banners, because
the dashboard's own announcements (a refused branch, a refused mark, the
caption in the branch control's place) can arrive in the same action and are
lost the same way. It is kept per window, as the brief says. A dialog and the
main window that both announced in one action would still make two
announcements. Every announcement comes from the dashboard's window today: each
`RunView`'s banner and the three that `SimulationView` asks for itself. The
other `NoticeLabel`s are built with `announces` False. One collector for the
whole application would have to pick one window's widget as the source of the
other window's message.

**Generator check.** The fact misread is what one window announces in one
action. Each banner held its own announcement, so no record saw two banners
change together. No head's `misread:` states this fact, and no other item
misreads it. `PL-J7Z5` built the announcement from each banner and filed this
item as its known gap, so it is a one-off. The fix makes the window's
collector that record.

**Fix.** `qt_widgets._WindowAnnouncements` is a child of each window. It
collects every request the window makes until control returns to the event
loop, then sends one announcement: each message once, joined by a space,
interrupting if any message does. The messages that interrupt come first, and
each group keeps the order asked for. Each message but the last ends with a
full stop, added where the message has none, so a screen reader pauses
between two. `announce` adds a request
to it rather than sending at once, and `NoticeLabel` adds itself in place of
its own timer. A label's request is read when the announcement is sent, so a
banner written twice in one action is still read as the action leaves it. A
request from a widget deleted before then is dropped, which
`shiboken6.isValid` decides.

**Tests.** In `tests/integration/test_qt_widgets.py`:
`test_banners_that_change_in_one_action_in_one_window_are_read_as_one_announcement`
(three labels, the order and the politeness of the joined message),
`test_a_message_asked_for_twice_in_one_action_is_read_once` (a repeated
message, and a direct request read with the banners),
`test_each_message_read_before_another_in_one_announcement_ends_a_sentence`
(the added full stop, a message read alone as shown, and a message asked for
twice that interrupts the second time),
`test_a_banner_whose_label_is_deleted_before_the_action_ends_is_not_read` and
`test_each_window_reads_its_own_announcements`. In
`tests/integration/simulation_view/test_simulation_view_refusals.py`:
`test_a_halt_of_every_run_reads_each_compared_run_s_banner_in_one_announcement`,
which is the brief's "Done when" test.

**Regression check.** With `src/anesthesia_sim/app/qt_widgets.py` put back to
`origin/main` (aa4dca79) and the new tests kept, `QT_QPA_PLATFORM=offscreen
PYTHONPATH=src python -m pytest -q
tests/integration/simulation_view/test_simulation_view_refusals.py::test_a_halt_of_every_run_reads_each_compared_run_s_banner_in_one_announcement
tests/integration/test_qt_widgets.py::test_banners_that_change_in_one_action_in_one_window_are_read_as_one_announcement`
failed both. The halt test recorded two announcements, Run 1's and then Run 2's
("At index 0 diff: Announcement(message='Run 1: Simulation stopped — an
unexpected error occurred in the simulator, ..."). The widget test recorded
three ("Left contains 2 more items, first extra item:
Announcement(message='Setting refused — too high.', ...").

**Blind review.** Pass 1 found nothing. Pass 2 found two faults, both marked
optional, and both are fixed. The joined messages kept the order asked for, so
a countdown asked for before a refusal was read first, and the refusal that
asked the reader to act could be cut off by the next announcement. The
interrupting messages now come first. Two messages shown with no full stop,
such as "Select an instant to branch at" and a refused mark, ran together with
no pause. Each message but the last now ends with one.

**Documents checked.** `docs/INTERFACE.md`, whose paragraph on banners read
out without moving the focus now says how one window's announcements are
joined and lists the new tests. `docs/ARCHITECTURE.md`, `docs/VERIFICATION.md`,
`README.md` and the rules under `.claude/rules/` say nothing about
announcements, so none changes.
