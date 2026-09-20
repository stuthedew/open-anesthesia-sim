---
id: PL-LPLD
title: Add time bookmarks and MAC targets as two separately listed collections
priority: P2
effort: M
status: done
classes: feature, ux
feature: scenario-branching
touches: src/anesthesia_sim/app/bookmarks.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/simulation_view.py, tests/unit, tests/integration, docs/ARCHITECTURE.md
blocked-by: PL-25KS
added: 2026-09-06
closed: 2026-09-20
payoff: lets a learner run fast to the moment they care about and return to it by name, instead of watching the clock and overshooting by minutes of simulated time at 300x
verify: grep -rq 'class TimeBookmark' src/anesthesia_sim/ && grep -rq 'class MacTarget' src/anesthesia_sim/
---

**Problem.** There is no way to say "run fast until something happens, then
stop". A learner comparing gas-management strategies watches the clock and
pauses by hand, which at 300x overshoots by minutes of simulated time, differs
on every attempt, and cannot be returned to.

**Why it matters.** Bookmarks are what make the playback multiplier usable for
anything precise, and they are the branch points a learner deliberately returns
to by name. `ROADMAP.md`'s planned item 12 treats every control-input-timeline
event as a valid branch point rather than bookmarks alone, but the bookmark set
is still the subset a learner is expected to revisit repeatedly.

**Scope floor, from the Gas Man reference simulator** (`ROADMAP.md` planned
item 26, project owner 2026-08-25). Two distinct mechanisms under one dialog,
not one kind with a flavour field:

- **time bookmarks** - an absolute simulated time;
- **MAC targets** - a percent of MAC on a chosen graphed compartment (circuit,
  alveolar, vessel-rich, muscle, fat or mixed-venous, not the alveolar trace
  alone).

Keep them as two separately listed collections, which is the shape the
reference's own dialog uses and what lets a UI list them separately. Crossing
direction is explicit - rising, falling or either - and shown wherever a
bookmark is listed, because the same threshold means opposite things during
wash-in and washout.

**Where.** `src/anesthesia_sim/app/controller.py` holds the collections;
`simulation_view.py` lists and edits them.

**Done when.** Both kinds can be created, listed and removed; each carries its
crossing direction where it is shown; and a MAC target names the compartment it
is read against. Detection itself is `PL-CTD7`.

## Promoted 2026-09-20 under `PL-JFQ3`, and its `verify:` repaired

`PL-25KS` (port the dashboard to PySide6) is `done`, `closed: 2026-09-15`,
`milestone: v0.4.26`, `pr: 588`, so `simulation_view.py` and `controller.py` are
on the toolkit that will ship and the collections can be built where they will
stay.

**Detection is still `PL-CTD7` and is still not this item.** `docs/ARCHITECTURE.md`
§ "What a branch is" states the current position in terms — "A **bookmark is
not yet one of those instants**, and how it becomes one is open. Bookmarks are
`PL-LPLD` and the halt that stops a run on the step crossing one is `PL-CTD7`;
neither is built." This item is the two collections; the halt, and whether a
bookmark instant is forkable at all (`PL-B8MK`), are not.

**The command was the refused prerequisite shape** — `uv run pytest -q
tests/unit && grep -rq 'class TimeBookmark' src/anesthesia_sim/` — where the
`pytest` run over a collected test path proves nothing `make check` does not
already prove and made the exit unreadable. Replaced with the two clauses that
actually discriminate, one per collection, both confirmed exiting 1 on this tree
before being written down.

## Built 2026-09-20, and the one place this reads the brief against its letter

**Crossing direction is on `MacTarget` and not on `TimeBookmark`.** The
`Done when` above says "each carries its crossing direction where it is
shown", which read across both kinds would put a rising/falling/either control
on a time bookmark. Simulated time only advances - `advance()` moves it
forward, nothing moves it back within a run, and `reset()` returns a run to its
own beginning rather than running it backwards - so an instant has exactly one
crossing, and a direction beside it is a control offering a choice that does
not exist. The brief's own reason for the field names a threshold and not an
instant: "the same threshold means opposite things during wash-in and
washout". So the field is on the kind that reason reaches.

**A target is held as a `MacMultiple`, where the scope floor says "a percent of
MAC".** Same quantity, in the unit every compartment on this interface is
already read in, so a target is compared against a readout with no conversion
at all; `core/concentration.py` records what a second form of one
concentration has cost this project. `PL-CTD7`'s own brief already writes the
example as "0.8 MAC".

**`WASH_IN_RATIO` may not carry a target.** It is a quotient of two
compartments rather than a concentration, so a multiple of MAC of it is not a
quantity the model holds - and it is the one member of `RecordedQuantity` a
compartment picker could otherwise offer.

**Three points where a run starts over were decisions rather than
consequences**, and each has a test naming which way it went: `reset()` keeps
the marks, `set_agent()` keeps them although it destroys the run, and a branch
inherits its trunk's. The last is the opposite of the control timeline and
settles by the same test - a timeline is the record of what was done to a run,
a mark is a question about what is still to come, and a comparison is two
managements answering one question.

**The panel is the dashboard's rather than a run's.** `SimulationView` holds
the only thing that writes a mark and writes it to every displayed run, so the
copies the controllers hold stay equal by construction. Two runs compared at
two different heights, because a learner typed one of them twice, is what that
arrangement makes unreachable.

**A target's height is bounded in the control by what the running agent can
reach** - `max_delivered_concentration_percent / agent_mac_percent`, since no
compartment exceeds the delivered concentration and the vaporizer bounds that.
The bound is the dialog's rather than `MacTarget`'s because it is the agent's
rather than the mark's.

Detection is still `PL-CTD7` and is still not built: nothing here compares a
mark against a state, and `test_the_panel_says_nothing_about_whether_a_mark_has_been_reached`
is what keeps a drawn row from implying otherwise.
