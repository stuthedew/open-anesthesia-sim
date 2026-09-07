---
id: PL-LYX2
title: Triage the thirty-one captures open on 2026-09-06
priority: P2
effort: S
status: done
classes: planning
feature: planning-cadence
milestone: v0.4.7
touches: docs/items
added: 2026-09-06
closed: 2026-09-06
pr: 416
not-delegable: a triage pass is proven by the store's state at the moment it ran, and that state moves - captures arrive untriaged by design - so no command run afterwards separates 'the pass happened' from 'nothing has been captured since'. `bin/docket check`, already on `make check`, is the standing proof that what the pass wrote is valid (same argument as PL-81SK, PL-2TCS, PL-SN5S and PL-MPTN)
---

**Problem.** Thirty-one captures reached the queue with `status: untriaged` and
no fields, most of them from the 2026-09-06 sessions around the v0.4.6 cut.
Capture deliberately skips `priority`, `effort`, `classes`, `touches` and
`feature` so that an idea costs one command; folding them into the queue is a
separate pass.

**Why it matters.** An untriaged item is invisible to `bin/docket next` and to
`bin/docket gate`, so thirty-one findings - six of them provenance or
displayed-value work that pins to the safety band - sat where no session would
be offered them and where the Gate 1 count could not see them.
`untriaged_stale_days` is 14, past which a capture has become a second queue
nobody reads.

**Where.** `docs/items/`, the thirty-one files carrying `status: untriaged` on
2026-09-06.

**What the pass decided.**

- **Nine capture stubs were removed rather than filled.** `bin/docket new`
  writes `**Problem.** <title>` above three empty headings; nine sessions had
  appended a full brief below that stub instead of replacing it, and
  `_section_text` judges the first matching heading, so each read as a brief
  with nothing under **Why it matters.** Deleting the stub is the whole fix
  where a real brief follows it.
- **`PL-SR8F` was verified at the source before being classed.**
  `docs/MODEL.md`'s "two orders milder" gloss was checked against the two
  tables in its own section: 1.4x10^-1 pp against 6.7x10^-3 pp at 1x is 1.3
  orders, and 1.0x10^1 pp against 1.5 pp at 300x is 0.8 orders. The claim is
  wrong at both ends, which is what made it `safety` rather than `docs` alone.
- **`PL-VKJ1` was dropped, not triaged.** Its Done-when was already satisfied
  by `#397`, which dropped all three of the README entries it names, each with
  a reason.
- **`PL-73G7` was left untriaged deliberately.** Its file is already edited on
  `origin/claude/pl-hb58-close-out`, and a second answer here is a second
  resolution of the same file.
- **Four items entered the safety band blocked rather than startable**, so the
  band ends the pass at exactly its limit of twelve startable: `PL-3YZW` and
  `PL-7HDS` behind sources nobody has reached, plus the two already there.

- **Two further captures arrived mid-pass and were folded in.** `#413` merged
  `PL-61WW` (the agent name loses contrast against the agent colour during a
  run) and `PL-NGF7` (the contrast checker can see no disabled-state colour)
  while this pass was running. `PL-61WW` is the sixth item to enter the safety
  band, and `#412` closing `PL-HB58` in the same window made room for it, so
  the band still ends at twelve startable.
- **`PL-73G7` was triaged by the branch that held it**, in `#412`, which is the
  outcome skipping it was for.

**Done when.** Every item captured before 2026-09-06 carries `priority`,
`effort`, `classes`, `touches` and a status past `untriaged`, or is closed with
a reason; `bin/docket check` reports 0 errors; and every item set to `ready`
names a `verify:` command that was run and watched fail, or records in
`not-delegable` why no command can prove it.
