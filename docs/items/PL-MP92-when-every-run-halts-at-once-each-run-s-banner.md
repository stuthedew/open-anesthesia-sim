---
id: PL-MP92
title: When every run halts at once, each run's banner interrupts the one before it, so a screen reader user hears only the last run's halt
priority: P3
effort: S
status: untriaged
classes: defect
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_widgets.py
deferred-from: v0.7.0 - found after the freeze, not safety or science, and no user sees a wrong value from it; it needs two compared runs and a frame that fails, so the release waits only on the owner test drive (filed 2026-11-27)
added: 2026-11-27
filed-pr: 2333
payoff: a screen-reader user hears every run's halt when several runs stop at once
---

**Problem.** When a frame cannot be drawn, `SimulationView` halts every run at once, and each run's banner then changes in the same action. `PL-J7Z5` announces each banner from its own label (`qt_widgets.NoticeLabel`), and a failure interrupts what is being read. So with two runs compared, the second run's announcement interrupts the first, and a screen-reader user hears only that the second run stopped.

**Why it matters.** Qt's documentation for `QAccessible.AnnouncementPoliteness` says an assertive announcement should be conveyed at once, interrupting other speech (read 2026-11-27). The first run's halt is then never heard, although its banner says why it stopped. Each run's banner names its run while two are compared, so joining them loses nothing. I suggest P3, because it needs two runs and a frame that fails.

**Approach.** Collect the announcements made within one return to the event loop in one place per window, and send them as one announcement, assertive if any of them is. The single-label coalescing in `NoticeLabel._announce` is the pattern to extend. The collector must not be a module-level value, because a View can be built more than once (`.claude/rules/ui-areas.md`).

**Done when.** A test that halts two compared runs at once, with the announcement recorder in `tests/integration/announcement_support.py`, shows one assertive announcement that holds both runs' banners.

**How it was found.** Building `PL-J7Z5`, 2026-11-27, while checking what a halt announces.
