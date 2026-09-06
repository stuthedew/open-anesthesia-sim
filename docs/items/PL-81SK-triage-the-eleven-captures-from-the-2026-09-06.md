---
id: PL-81SK
title: Triage the eleven captures from the 2026-09-06 sessions
priority: P2
effort: S
status: done
classes: planning
feature: planning-cadence
touches: docs/items
added: 2026-09-06
closed: 2026-09-06
not-delegable: a triage pass is proven by the store's state at the moment it ran, and that state moves - captures arrive untriaged by design - so no command run afterwards separates 'the pass happened' from 'nothing has been captured since'. `bin/docket check`, already on `make check`, is the standing proof that what the pass wrote is valid (same argument as PL-2TCS, PL-SN5S and PL-MPTN)
---

**Problem.** Eleven captures from the 2026-09-06 sessions reached the queue with
`status: untriaged` and no fields: `PL-1KTV`, `PL-5TRV`, `PL-74R0`, `PL-B1WW`,
`PL-BHJW`, `PL-N936`, `PL-NBCJ`, `PL-NBWP`, `PL-R460`, `PL-RC0M` and `PL-W6NY`.
Capture deliberately skips `priority`, `effort`, `classes`, `touches` and
`feature` so that an idea costs one command; folding them into the queue is a
separate pass.

**Why it matters.** An untriaged item is invisible to `bin/docket next`, so
eleven findings — two of them about displayed clinical values — sat where no
session would be offered them. `untriaged_stale_days` is 14, past which a
capture has become a second queue nobody reads.

**Where.** `docs/items/`, the eleven files above.

**What the pass decided.**

- `PL-N936` (a session cannot push a tag) closed rather than triaged. `a575f8d`
  ("PL-N936: record that a session cannot push a tag...", #375, on
  `origin/main`) both created the item and made the `SKILL.md` edit its **Done
  when.** asks for, and left the status at `untriaged`. Verified against all
  four clauses before closing; triaging it would have offered finished work to
  the next session.
- Two items classed for the safety band. `PL-NBWP` (playback's burst makes
  control resolution rate-dependent) is `safety` — the mechanical claims were
  re-verified in the tree, and what is wrong is what the reader is told, which
  `CLAUDE.md` counts as a safety failure. `PL-NBCJ` (whether the step moves to
  0.05 s) is `science`, matching its parent `PL-X9KD`, and is `blocked` on
  `PL-NBWP` per its own "should probably be decided first".
- `PL-B1WW` (the oracle step is not converged) classed `test`, **not**
  `science`, and the reasoning is written into the item so it can be overruled:
  the gate is conservative rather than wrong, so nothing incorrect can reach a
  reader through it.
- `PL-BHJW` left outside any feature: its sibling `PL-HDDJ` sits in `ci-cost`,
  which is finished and in the unreleased set, and filing a one-word doc fix
  there would reopen a completed feature.
- Five items to `needs-decision` (`PL-1KTV`, `PL-74R0`, `PL-B1WW`, `PL-NBWP`,
  `PL-RC0M`), each with a `**Decision needed.**` line; three to `ready`
  (`PL-5TRV`, `PL-BHJW`, `PL-W6NY`) plus `PL-R460`; one `blocked`; one closed.
- `bin/docket record` wrote the two `pr` numbers the base was owed
  (`PL-HDDJ`, `PL-KPP1`, both #377) in the same pass.

**Done when.** `bin/docket check` reports zero untriaged and zero errors, every
item set to `ready` names a `verify:` command that was run and watched fail, or
a `not-delegable` reason, and `make check` is green.
