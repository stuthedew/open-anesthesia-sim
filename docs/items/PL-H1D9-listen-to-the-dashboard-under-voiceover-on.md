---
id: PL-H1D9
title: Listen to the dashboard under VoiceOver on macOS once the names are in place, because the headless check reads what Qt hands the platform, not what a screen reader says
priority: P2
effort: S
status: blocked
classes: test
feature: presentation-safety
blocked-by: PL-9QY5, PL-N5JB, PL-RK9Z, PL-T9RB, PL-J7Z5
added: 2026-11-23
payoff: the owner hears what a screen-reader user hears, so the accessible names are checked against speech and not only against what Qt reports
---

**Problem.** The 2026-11-23 check of `PL-QR6Q` read what Qt hands to the platform's accessibility interface. It did not hear what a screen reader says, which also depends on the platform bridge and the screen reader.

**Why it matters.** Only a run under a real screen reader shows whether the names and values that `PL-9QY5`, `PL-N5JB`, `PL-RK9Z`, `PL-T9RB` and `PL-J7Z5` add are spoken as intended. The project owner works on a Mac, where VoiceOver is built in.

**Approach.** Once those items are done, the owner turns VoiceOver on (Command-F5), opens the app, starts a run and moves through the controls and readouts with VoiceOver's keys, noting what is spoken for each setting slider, each readout and the banner. Record what was heard against what each item intended. This needs the owner's machine, so it is blocked on the five items and then on the owner.

**Done when.** The owner has listened under VoiceOver and what was heard for each setting slider, readout and banner is recorded here against what each item intended, with the date. Any difference is filed as its own item.
