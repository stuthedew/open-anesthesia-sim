---
id: PL-20ZR
title: The 'workflow before features' ordering is re-explained every session because nothing records it
priority: P2
effort: S
status: done
closed: 2026-08-30
classes: session-cost, infra
commit: 889bd3e
pr: 81
feature: planning-cadence
touches: ROADMAP.md, CLAUDE.md, subprojects/docket/src/docket/plan.py
added: 2026-08-30
---

**Problem.** The project owner wants workflow/process work finished before
product work resumes, and has had to say so in every new session. Nothing in
the tree records that ordering, so each session reads the queue, sees eight
P1 safety items on top, and proposes those.

The priority field cannot express it. `docket check` rejects `safety`- and
`science`-classed items below P1, and all eight current P1 items carry one of
those classes, so they are pinned to the top band and cannot be demoted.
`plan.py`'s ranking is band-first - the feature-underway preference is a
tie-breaker *inside* a band, never across bands - so no arrangement of P2
process work is ever picked ahead of them. The only way to express the
ordering in the priority field is to raise 23 process items into P1, which
puts the top band at 31 against a `top_band_limit` of 12 and, more seriously,
makes P1 mean both "a clinician could be misled" and "the release script is
annoying". That is the one field encoding the safety-critical standard, and
it stops carrying information the moment it means both.

**Why it matters.** Re-explaining a standing decision every session is the
exact cost `CLAUDE.md`'s "deterministic tooling" section exists to remove:
work re-derived at full context in every session that needs it. It is also
lossy - a session that is not told simply does the wrong thing, and the owner
only finds out when the reply comes back proposing safety work.

**Where.** `ROADMAP.md`'s timeline is the mechanism that already reaches every
session: `docket wave` computes the beat from it and the session-start digest
prints that beat before anything else. A workflow-hardening step on the
timeline is self-announcing in a way a priority edit is not.

**The gap that remains after the beat.** With the beat set, `docket wave` says
"harden the workflow" while `docket next` still answers with P1 safety work,
because nothing teaches the ranking about the beat. The `docket` skill covers
this by telling a session to follow the beat when the two disagree, which
works but is soft. Closing it properly means `plan.py` preferring items
carrying the active step's feature ahead of band order, with `P0` still first.
Decide whether that is worth building or whether the skill rule suffices.

**Done when.** A session starting cold proposes workflow work without being
told to, and the ordering is stated somewhere a reader can find the reasoning
rather than only its effect.

**Closed, 2026-08-30.** `CLAUDE.md` carries the rule under "The queue, and how
the project owner works": workflow work outranks product work until the
workflow is settled, with the reasoning, the reason the priority field cannot
carry it, and its own retirement condition. `CLAUDE.md` loads at launch, so a
session starting cold reads it before it reads the queue - which is this
item's stated "done when".

The beat, which would carry the same ordering at no per-session cost, is
`PL-NSN9`'s to settle and is deliberately not held open here.
