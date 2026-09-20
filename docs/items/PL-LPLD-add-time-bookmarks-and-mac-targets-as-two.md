---
id: PL-LPLD
title: Add time bookmarks and MAC targets as two separately listed collections
priority: P2
effort: M
status: ready
classes: feature, ux
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, tests/unit
blocked-by: PL-25KS
added: 2026-09-06
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
