---
id: PL-X9R0
title: Add user bookmarks that pause a run at a time or a concentration threshold
status: untriaged
feature: scenario-branching
added: 2026-08-25
---

**Problem.** There is no way to say "run fast until something happens, then
stop". A learner comparing gas-management strategies has to watch the clock
and pause by hand, which is neither repeatable nor possible at high playback
speed.

**Why it matters.** Bookmarks are the interaction that makes fast-forward
usable: set a target ("VRG reaches 0.8 MAC", "elapsed 3:00:00"), run at high
speed, and the run halts there. The project owner's model for this is Gas
Man. They are also the natural branch points for PL-RRWV — the owner expects
users to fork at a bookmark far more often than at an arbitrary time — so the
bookmark set is what a snapshot policy should key on.

**Where.** New core concept (bookmark definitions and crossing detection
belong in `core/`, not in a UI callback); `app/controller.py` for the halt;
`app/simulation_view.py` for setting and listing them.

**Design notes.** Two kinds: absolute simulated time, and a monitored
quantity crossing a threshold. A MAC-denominated threshold needs MAC to be a
first-class displayed quantity first — `mac_percent` exists per agent in
`core/parameters.py` and the data files, but MAC presentation was explicitly
out of scope for v0.1.0, so check where that stands before promising a
"0.8 MAC" bookmark rather than a percent-atmosphere one. Crossing detection
has its own item (PL-PFM1). Bookmarks must be part of the saved scenario, not
session-local, if they are to be branch points.

**Done when.** A bookmark can be set, is reached deterministically at any
playback speed, halts the run at (not past) the target, and survives save and
reload.
