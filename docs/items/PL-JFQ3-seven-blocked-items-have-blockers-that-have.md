---
id: PL-JFQ3
title: Seven blocked items have blockers that have closed, and since PL-ZF2G promoting one is what returns an anticipated safety finding to the debt gate
priority: P2
effort: M
status: done
classes: planning, docs
feature: debt-gate
touches: docs/items
added: 2026-09-16
closed: 2026-09-20
payoff: puts five startable items in front of bin/docket next that nobody was ever offered, and settles whether PL-ZF2G's carve-out is holding a live safety finding outside the gate built to catch it
not-delegable: the deliverable is a per-item judgment recorded in seven item files - whether each was blocked on something nobody wrote into `blocked-by` - and no command can tell a promotion that was reasoned from one that was typed
---

**Problem.** Seven blocked items have blockers that have closed, and since PL-ZF2G promoting one is what returns an anticipated safety finding to the debt gate

**What was found.** `bin/docket check` reports seven items as "every blocker has
closed; it is ready to promote" - `PL-5NR5`, `PL-LPLD`, `PL-MBP6`, `PL-QR6Q`,
`PL-QRD1`, `PL-W7H9` and `PL-Z3V5`, measured 2026-09-16. The advisory is not new
and nothing about it is broken; what is new is that one of them now has a
consequence beyond its own band.

**Why `PL-ZF2G` changes the weight of it.** `check_gate_reentries` now exempts
an item from the `safety`/`science` gate advisory only where `anticipated` and
`status: blocked` hold together, so the promotion is the event that returns such
a finding to the gate. `PL-W7H9` (`docs, safety, anticipated`) is blocked on
`PL-8PSW`, which is `done`. Promoting it is therefore not only tidying a status:
it is the step that lets the gate see a `safety` finding whose hazard may now be
live, which is the whole mechanism `PL-ZF2G` was filed to install.

**What this is not.** Not a defect in the advisory, which fires correctly and
names exactly the right items, and not a proposal to make `status` follow its
blockers automatically - `PL-ZF2G` considered resolving blockers inside
`check_gate_reentries` and refused it, because it would put a second copy of
`checks.py`'s resolution logic in the tool that reads the store rather than
reasons about it. This is the grooming pass that mechanism assumes somebody
runs.

**The judgment each one needs.** Promotion is not automatic even where the
blockers have closed: an item may have been blocked on a second thing nobody
wrote into `blocked-by`, and for `PL-W7H9` specifically the question is whether
`PL-8PSW` closing actually made its hazard live or merely removed one
prerequisite. Read each item before changing its status; the advisory says the
edge is clear, not that the work is startable.

**Found 2026-09-16** while implementing `PL-ZF2G`.

**Where.** `docs/items/`, the seven items named above.

**Why it matters.** `bin/docket next` reads `status`, so a blocked item whose
blockers have all closed is startable work that nobody is ever offered. Seven of
them is a second queue behind the queue. One carries more than that: `PL-W7H9`
is `docs, safety, anticipated`, blocked on `PL-8PSW`, which is `done` - and since
`PL-ZF2G` the promotion is the *event* that returns an anticipated safety finding
to the debt gate. So the grooming pass nobody runs is what holds a safety finding
outside the gate built to catch it, which is the mechanism working exactly as
designed and reaching nobody.

**Done when** each of the seven - `PL-5NR5`, `PL-LPLD`, `PL-MBP6`, `PL-QR6Q`,
`PL-QRD1`, `PL-W7H9`, `PL-Z3V5` - has been read and either promoted out of
`blocked`, or left blocked with the real blocker written into `blocked-by`; and
`PL-W7H9` records whether `PL-8PSW` closing made its hazard live or merely
removed one prerequisite. Read each item before changing its status: the advisory
says the edge is clear, not that the work is startable.

## Done 2026-09-20: nine, not seven, and they split four ways

**Two more had arrived since the 2026-09-16 measurement** — `PL-FG9D` and
`PL-KZ99`, whose blockers closed on 2026-09-19 and 2026-09-17 — so the pass
covered nine. That is the advisory doing its job rather than drift: it is
computed from the store each run and the brief's list was a snapshot.

**The judgment the brief asked for was the whole of the work, and it did not
split the way the advisory's uniform wording suggests.** Four dispositions:

**Promoted to `ready` (five).** `PL-FG9D` (design the base anesthesia-machine
abstraction) — `PL-4DCG`'s survey landed, so the seven design questions are
answerable against evidence. `PL-LPLD` (time bookmarks and MAC targets) and
`PL-QR6Q` (what `QAccessible` can deliver) — both waited on `PL-25KS`, whose
completion `PL-QR6Q`'s own brief named as the resolving event. `PL-MBP6` (a
README image) — `PL-YCWZ` landed the rendering, and the re-point's *remaining*
objection, that a Qt screenshot cannot ship while the built interface is Flet,
has lapsed with the port: there is no `flet` in `pyproject.toml`, none in
`src/`, and `tools/import_boundary_check.py` forbids it outright. `PL-Z3V5`
(extraction notes) — the 2026-09-19 sweep had already done the reading and left
it blocked only for want of a command, which is written here having been run.

**Left `blocked`, with the real blocker written in (three).** `PL-W7H9`,
`PL-QRD1` → `PL-XJ37`; `PL-KZ99` → `PL-B396`. Each is a case of the closure
removing a prerequisite rather than the reason the work could not start, which
is exactly what the brief warned the advisory cannot see: "the advisory says the
edge is clear, not that the work is startable."

**Dropped as overtaken (one).** `PL-5NR5` (a private reference corpus) — its own
last paragraph said it "closes with `PL-XJ5P` rather than beside it", and
`PL-XJ5P` (`pr: 531`) wrote every clause of its "Done when".

**The `PL-W7H9` question the brief singled out is answered: `PL-8PSW` removed
one prerequisite.** The hazard is a reader taking two curves as a claim about
patients, and no reader can reach two curves —
`src/anesthesia_sim/app/main.py` constructs `SimulationView((controller,))`,
and neither it nor `simulation_view.py` mentions `branch`, `BranchedCase` or
`ResumePoint` anywhere. `PL-8PSW` made a comparison drawable, not reachable.
`PL-XJ37` (`needs-decision`) is the item that makes it reachable, and the
`anticipated`/`blocked` carve-out that `PL-ZF2G` installed is therefore intact
and honest rather than merely unexercised. That finding is the pass's main
result: the mechanism `PL-ZF2G` built is working, and the one grooming pass of
window it leaves has not yet opened.

**One correction worth carrying, since it was a premise rather than a status.**
`PL-QRD1`'s brief expected `PL-8PSW` to settle whether the agent selectors need
locking on a two-run dashboard, on the ground that `PL-8PSW` "is where two runs
first reach a reader". It is not: `dashboard_frame.transport` still computes
`selector_locked=snapshot.is_running` alone. Nothing was settled, and the
question moves intact to `PL-XJ37`.

**Two stale lines fixed in passing**, both recorded in the items they belong to
rather than here: `PL-MBP6` said `assets/branding/` holds a `.gitkeep` when
there is no `assets/` directory at all, and `PL-LPLD` carried the refused
prerequisite `verify:` shape (`uv run pytest -q tests/unit && grep ...`).

**Effect on the store.** `bin/docket check` went from 16 advisories to 7 with 0
errors, and all nine "every blocker has closed; it is ready to promote" lines
are gone. Five `ready` items entered `bin/docket next`'s view that nobody was
ever being offered.
