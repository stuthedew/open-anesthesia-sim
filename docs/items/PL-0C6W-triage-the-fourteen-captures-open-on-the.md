---
id: PL-0C6W
title: Triage the fourteen captures open on the morning of 2026-09-16
priority: P2
effort: S
status: done
classes: planning
feature: planning-cadence
touches: docs/items
added: 2026-09-16
closed: 2026-09-16
pr: 611
not-delegable: a triage pass is proven by the store's state at the moment it ran, and that state moves - captures arrive untriaged by design - so no command run afterwards separates 'the pass happened' from 'nothing has been captured since'. `bin/docket check`, already on `make check`, is the standing proof that what the pass wrote is valid (same argument as PL-2B7B, PL-Q2PX and PL-LYX2)
---

**Problem.** Triage the fourteen captures open on the morning of 2026-09-16

**Why it matters.** An untriaged item is in no band, so `bin/docket next`
cannot offer it and `bin/docket gate` cannot count it as debt: fourteen of them
is a second queue nobody reads, and `docket.toml`'s `untriaged_stale_days = 14`
exists to stop that becoming permanent. Most of this batch carries a debt class
or reaches `needs-decision`, so it is what the *next* gate counts - Gate 1 is
frozen under v0.5.0, and a finding made after a freeze goes to the following
gate unless its problem predates it.

Filed before the pass began, per `CLAUDE.md`'s housekeeping rule: a triage pass
takes a branch and a commit of its own, and every in-flight guard this project
has matches a `PL-` id, so unfiled it would read as nobody's work to all of
them and keep reading that way after the push.

**Done when.** Every capture in the batch carries `priority`, `effort`,
`classes`, `touches` and a `feature`; each is at `ready` with a `verify:`
command that has been run and watched fail for the right reason, at `ready`
with a `not-delegable` reason where no command can prove it, at
`needs-decision` with a `**Decision needed.**` section stating the question, or
`dropped` with a `reason` and a `closed` date; each brief carries
**Problem.**, **Why it matters.** and **Done when.**; and `make docket` and
`make check` pass.

Two of the fourteen are deliberately not this pass's. `PL-SYG4` and `PL-2M4X`
were being triaged concurrently by another session (branch
`claude/quirky-newton-tf1moa`), which the in-flight mark cannot see because a
triage pass writes nothing outside `docs/items/` - the `PL-N1JK` case. They are
left to that session and stay untriaged here.
