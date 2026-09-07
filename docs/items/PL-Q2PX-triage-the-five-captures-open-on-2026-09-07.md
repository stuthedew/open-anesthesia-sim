---
id: PL-Q2PX
title: Triage the five captures open on 2026-09-07
priority: P2
effort: S
status: done
classes: planning
feature: planning-cadence
touches: docs/items
added: 2026-09-07
closed: 2026-09-07
not-delegable: a triage pass is proven by the store's state at the moment it ran, and that state moves - captures arrive untriaged by design - so no command run afterwards separates 'the pass happened' from 'nothing has been captured since'. `bin/docket check`, already on `make check`, is the standing proof that what the pass wrote is valid (same argument as PL-LYX2)
---

**Problem.** Five captures reached the queue with `status: untriaged` and no
fields, all of them from the 2026-09-07 sessions that closed `PL-Y5WR` (halt a
run at the supported 24-hour run length), `PL-GVXP` (separate the six chart
traces by line style) and `PL-ZVS7` (pin the control-resolution tolerance
table). Capture deliberately skips `priority`, `effort`, `classes`, `touches`
and `feature` so that recording an idea costs one command; folding them into the
queue is a separate pass.

**Why it matters.** An untriaged item is invisible to `bin/docket next` and to
`bin/docket gate`, so a finding sits where no session would be offered it and
where the Gate 1 count cannot see it. Two of these five turned out to belong in
the safety-adjacent bands once read: `PL-WT07` states a margin in the
authoritative model spec that is off by about a factor of seven in the
reassuring direction, and `PL-HLD5` records that a scoped `ROADMAP.md` sentence
specifies a chart channel assignment already measured as unreachable.

**Where.** `docs/items/`, the five files carrying `status: untriaged` on
2026-09-07: `PL-CZFY`, `PL-H2K2`, `PL-HLD5`, `PL-THXF`, `PL-WT07`.

**PL-HLD5 is not triaged here; it was yielded.** `PL-GVXP`'s session took it
on `origin/claude/gate-items-al6kr2` and answered it as `#427` (compartment
keeps line style, the run takes width), closing it rather than parking it.
`bin/docket show PL-HLD5` names that branch as the holder, so this pass
restored the file to `origin/main`'s copy and touches it no further: a
`needs-decision` triage would have been a second, worse resolution of a
question already settled.

**Done when.** Each of the remaining four carries `priority`, `effort`, `classes`,
`touches` and a `feature`; each holds a full brief; each `ready` item names a
`verify:` command that was run and watched fail before it was written down; and
each item whose next step is a decision is at `needs-decision` with a
**Decision needed.** section rather than answered in the pass.

**Note on the four skipped marks.** `bin/docket triage` reported four of the
five as `Its file is already edited on <branch>`, which `SKILL.md` says to skip.
All four were false positives — each branch's copy of the item file is identical
to `origin/main`'s, both branches having squash-merged as `#421` and `#422`. The
marks were checked rather than obeyed, and the defect behind them is `PL-8MJ3`.
