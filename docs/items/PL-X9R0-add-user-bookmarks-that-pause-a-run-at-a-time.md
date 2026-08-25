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

**Scope floor (owner, 2026-08-25).** The reference simulator's bookmark set
is the minimum to implement, and the owner states it as two kinds:

1. **Time points** - halt at an absolute simulated time.
2. **Percent of MAC, on every graphed compartment** - circuit, alveolar,
   vessel-rich, muscle, fat, and mixed-venous alike, not the alveolar trace
   only.

Recorded from the project owner's own account of the software; the vendor
documentation could not be consulted from the session that captured this
(gasmanweb.com and its help mirror are both refused by the environment's
network egress policy). Treat the two kinds above as the specification and
the wording as second-hand.

**Prerequisite.** Kind 2 cannot be specified in a unit the application does
not have: MAC is currently internal only. PL-DHV7 has to land first.

**Design notes.** Two things the bookmark kinds above leave open, both of
which change behaviour and neither of which is inferable from the reference
simulator's feature list:

- *Crossing direction.* The same threshold means different things during
  wash-in and washout. A bookmark at 0.8 MAC on the VRG set while the VRG is
  already above 0.8 either fires immediately or never, depending on an
  unstated rule. Make direction explicit - rising, falling, or either - and
  show it wherever the bookmark is listed.
- *Thresholds that are never reached.* Compartments approach their
  asymptotes; a threshold set above one is unreachable, and a run that chases
  it forever is the failure mode the run-time cap (PL-011) exists to catch.
  The bookmark needs a distinct "not reached, run-time cap hit" outcome that
  reads differently from "reached", rather than a silent stop.

Crossing detection has its own item (PL-PFM1). Bookmarks must be part of the
saved scenario, not session-local, if they are to serve as branch points
(PL-RRWV).

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
