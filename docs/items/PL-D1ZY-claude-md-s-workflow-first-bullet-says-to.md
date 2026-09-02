---
id: PL-D1ZY
title: CLAUDE.md's workflow-first bullet says to retire itself when the workflow release ships, and v0.2.8 has shipped
status: untriaged
touches: CLAUDE.md
added: 2026-09-02
---

**Problem.** `CLAUDE.md`'s "Workflow work comes before product work until the
workflow is settled" bullet ends: "Retire this bullet when the workflow
release ships: it is a phase, not a policy." That release has shipped.
`ROADMAP.md` on `main` marks v0.2.8 "Completed / current baseline" and
`pyproject.toml` reads `version = "0.2.8"`, but the bullet is still resident
in `CLAUDE.md` (line 319 on `main` at the time of writing).

**Why it matters.** It is resident text, so it loads in every session before
anything has been read, and it inverts the ordinary priority bands: an item
that removes workflow friction outranks one that adds capability "whatever
the priority bands say". While it stands, every session is told to rank
workflow work above the simulator on the authority of a phase that is over.

That is the direction of error this project names as its main risk in the
same file - the workflow apparatus "is at permanent risk of becoming the work
instead" - and the next two releases are the ones it would distort: v0.3.0
clears twenty entries of product debt and v0.4.0 builds the first teachable
case. Roughly thirty items' worth of sessions would each read a superseded
rule, and any one of them could reorder its work on it.

**Where.** `CLAUDE.md`, the bullet beginning "**Workflow work comes before
product work until the workflow is settled.**" in "The queue, and how the
project owner works". Check whether `docs/worker.md` and
`.claude/skills/docket/SKILL.md` restate or depend on the same rule before
deleting it - the bullet says "the `docket` skill carries why", so the skill
holds the reasoning half and may need the same treatment.

Retiring it is a deletion, not a rewrite: the priority bands and
`bin/docket next`'s own ranking are what the queue falls back to, and both
already exist. If anything from the phase is worth keeping - saying which
side of the rule a piece of work sits on, say - it survives as its own
sentence rather than as the bullet.

**Done when.** The bullet is gone from `CLAUDE.md`, `docs/worker.md` and the
`docket` skill carry nothing that reinstates it, and `make check` passes -
including the resident-line-count report, which should fall. The project
owner confirms the retirement rather than a session inferring it: the
condition is written into the file, but whether the phase is actually over is
theirs to say.

**Notes.** Found 2026-09-02 while verifying that #177 had merged; v0.2.8
merged as #176 shortly before. Not raised by the discussion that found it -
that session was writing a GitHub repository description - so it was captured
rather than fixed, per `CLAUDE.md`'s capture rule, and recommended in the
reply per the compounding-friction rule.
