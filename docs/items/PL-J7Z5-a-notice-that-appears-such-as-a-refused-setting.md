---
id: PL-J7Z5
title: A notice that appears, such as a refused setting, a stopped run or the approaching run-length stop, is never announced to a screen reader
priority: P2
effort: S
status: ready
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_widgets.py, tests/integration/test_qt_widgets.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-23
payoff: a screen-reader user hears a refused setting, a failure or a stopping run when it happens
---

**Problem.** When the banner shows a refused setting, a stopped run, a failure or the approaching run-length stop, nothing tells a screen reader. The banner is a `NoticeLabel` whose text changes, and no accessibility event is sent, so a screen-reader user is not told unless they move to the banner.

**Why it matters.** The banner carries the notices that `docs/INTERFACE.md` requires a reader to see at the moment they apply. Qt has offered an announcement event since 6.8, with a polite and an assertive priority, and Qt's documentation says "Assertive should not be used unless the interruption is imperative" (Qt, QAccessible Class, https://doc.qt.io/qt-6/qaccessible.html, read 2026-11-23). This project's floor is PySide6 6.12 (`pyproject.toml`), so the event is available. I suggest P2, because a failure halts the run silently for this reader.

The same applies to the status messages that `docs/INTERFACE.md` names under WCAG 2.2 success criterion 4.1.3, such as the caption that says a pinned Workspace will not draw a comparison. That passage says nothing announces it yet.

**Approach.** Send a `QAccessibleAnnouncementEvent` from the banner when its text changes to a new notice. Use the assertive priority for a failure and a refused setting, which ask the reader to act, and polite for the run-length countdown and the muted stop. Test it with a recorded event handler, since the offscreen platform has no screen reader.

**How it was found.** `PL-QR6Q` built the dashboard offscreen on 2026-11-23, under PySide6 6.12, and walked the tree that `QAccessible.queryAccessibleInterface` returns for the main window, reading each node's role, name, value and description. That tree is what Qt hands to the platform's accessibility interface. It is not what a screen reader says, which `PL-H1D9` checks.

**Done when.** A test with a recorded accessibility event handler shows that each new banner notice sends one announcement, assertive for a failure and a refused setting and polite for the run-length countdown and the muted stop.

**Priority, researched 2026-11-23.** WCAG 2.2 success criterion 4.1.3 Status Messages is Level AA: status messages "can be programmatically determined ... such that they can be presented to the user by assistive technologies without receiving focus" (W3C, WCAG 2.2, https://www.w3.org/TR/WCAG22/, read 2026-11-23). It is above the Level A minimum, and the notices are on screen for a sighted reader, so P2.

**Generator check.** A one-off: Qt sends no event for a label's text change, and nothing here sent one.
