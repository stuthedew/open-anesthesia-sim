---
id: PL-4V6B
title: Decide whether the decision archive should be separated from the work queue
priority: P3
effort: M
status: done
classes: infra, planning
feature: docket-store
touches: subprojects/docket, docs/items, docs/dead-ends.md
added: 2026-09-13
closed: 2026-10-03
pr: 1298
verify: grep -qF 'a reading surface of their own was refused 2026-10-03' docs/dead-ends.md
---

**Problem.** Decide whether the decision archive should be separated from the work queue
**Why it matters.** `docs/items/` now serves two purposes that pull in
different directions. It is the work queue - what to do next, what is in
flight, what a gate still owes - and it is also the project's decision archive:
several hundred closed and dropped items whose value is the recorded reasoning,
which is what stops a refuted approach being re-proposed. The capture is one
line and does not say which failure it saw, so the first thing the decision has
to settle is what "separated" would mean: separate directories, a separate
rendered view, or only a separate way of reading the same files.

**What is already settled, so the answer starts here rather than from
scratch.** `PL-KM3X` (partition closed item bodies out of the live store) was
dropped on the same day this was captured, on three measured grounds: no
measurable parse cost (76 ms of an 830 ms command whose cost is git); a
partition that would not fix the one real threshold, which is directory entry
count and which a second file per item makes worse; and the shape argument -
this store is cross-referenced (86.1%, 2,773 edges), and cross-referenced
record stores stay flat. The third is not a performance argument and reaches
any split of the files, so moving closed items into their own directory is
already refuted and is in `docs/dead-ends.md`. What `PL-KM3X` does not answer is
whether the archive is a distinct kind of record wanting its own reading
surface, which is what this capture appears to ask.

**Done when.** Either a decision is recorded that the queue and the decision
archive stay one store, with the reasoning added to `docs/dead-ends.md` so the
question is not re-opened a third time; or a mechanism is named that separates
the reading without separating the files, and items are written for it.

**Decision needed.** Does the decision archive get a reading surface of its own, and if so one that does not move the files - given that `PL-KM3X` already refuted moving them?

## Decided 2026-10-03 - one store; the archive's reading surfaces exist, and none moves a file

What "separated" could mean, and where each reading already stands on
2026-10-03:

1. **Separate directories** - refuted by `PL-KM3X` on 2026-09-13, and in
   `docs/dead-ends.md` since.
2. **A committed index or rendered view** - in `docs/dead-ends.md` too: "An
   index, database or manifest committed beside the items - rejected: anything
   an index holds is recomputable."
3. **A separate way of reading the same files** - already built, which is the
   half the capture did not count:
   - `bin/docket show <id>` prints a closed item in full, and is the retrieval
     path `docs/dead-ends.md` names for itself;
   - `docs/dead-ends.md` carries the refuted approaches into every session's
     context at start, budgeted at 30 entries and 4,000 bytes, with 11 entries
     and 2,304 bytes used;
   - `bin/docket generators` reads the closed heads and what each still
     explains;
   - the standing documents cite a decision by id where it binds: 144
     `(project owner, DATE ...)` citations across `CLAUDE.md`, `ROADMAP.md`,
     `docs/MODEL.md`, the rules, the docket skill, `docs/maintainer.md` and
     `docs/WORKING_NOTES.md`, against 226 closed items carrying such a marker
     and 27 open ones (counted with `grep`).

The one lookup with no command behind it is a decision found by topic rather
than by id, and that is `rg '(project owner, 2026' docs/items` with a word
beside it. `CLAUDE.md` § "Prefer deterministic tooling" refuses wrapping it:
not around what a tool already does, and where the benefit is unclear the
answer is no. Nothing measured says a session has failed to find a recorded
decision; what the capture feared, a refuted approach re-proposed, is the case
the dead-ends tier is resident for, and this capture - filed the day `PL-KM3X`
was dropped - is itself the instance that tier is meant to stop.

**Recommendation:** record that the queue and the decision archive stay one
store, and extend `docs/dead-ends.md`'s `PL-KM3X` entry by one clause so the
third reading is refused where the first two already are. **Decided
2026-10-03** by the design-round session as an obvious call, over naming a
mechanism that separates the reading without separating the files - a
`decisions` command or a rendered archive - which would wrap a `grep` that
nothing shows anybody has needed. The clause is written in this round: one
line, in the file whose preamble asks for exactly that edit ("add one, merge
two, remove one"), with the file declared in `touches` so the edit rides this
item's own commit.
