---
id: PL-D1ZY
title: CLAUDE.md's workflow-first bullet says to retire itself when the workflow release ships, and v0.2.8 has shipped
priority: P2
effort: S
status: done
classes: defect, docs, session-cost
feature: worker-instructions
milestone: v0.2.9
touches: CLAUDE.md, .claude/skills/docket/SKILL.md
added: 2026-09-02
closed: 2026-09-02
pr: 178
verify: '! grep -rqE "Workflow work (comes before|outranks) product work" CLAUDE.md .claude/skills/docket/SKILL.md'
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

**Closed 2026-09-02.** The project owner confirmed the retirement, which this
brief made the condition rather than letting a session infer it from the
shipped release. Retired as a deletion, as the brief proposed: the bullet is
gone from `CLAUDE.md`, and `.claude/skills/docket/SKILL.md`'s two paragraphs
carrying its reasoning half are gone with it.

**Why nothing replaced it.** The three tests that should decide workflow
against product work were already resident and none is phase-scoped, so the
retirement leaves no hole. (1) *Step membership* — `bin/docket next` ranks the
roadmap's current step above everything but `P0`, so while the step is v0.3.0
or v0.4.0 the product leads by construction. (2) *Compounding friction* —
`CLAUDE.md`'s preceding bullet already carries the arithmetic the retired rule
rested on, per-item saving times items remaining, and already requires it be
recommended on sight. (3) *A tool that gives a wrong answer is a defect* —
`CLAUDE.md`'s deterministic-tooling section already says a tool whose output
looks authoritative and is not is worse than none, which is the class PL-T63T,
PL-L9JS and PL-20CQ sit in; they are fixed on the defect's own merits, never as
a workflow-versus-product question.

**What survived from the skill, and why.** Two facts in the deleted paragraphs
were independent of the ordering rule and were kept, rewritten: that work the
roadmap places nowhere ranks on its band alone, sitting between in-scope and
out-of-scope rather than being excluded; and that process work must not be
promoted into `P1`, because `docket check` pins `safety` and `science` there
and the band would stop meaning "a clinician could be misled". The second
matters more now, not less, with the ordering rule gone. Dropped with the rule:
the instruction to apply it by hand to unplaced items, and the classification
note that a product item taken as a test case for a workflow change is workflow
work, which has no consequence once nothing ranks on the distinction.

**Left alone deliberately.** `subprojects/docket/src/docket/plan.py`'s comment
on `PLACEMENT_ORDER` says the priority field "cannot express the phase". Read
in context that is the roadmap step rather than the retired standing decision,
and the behaviour it documents — placement beating band — is unchanged and
still correct, so rewriting it would be churn in the apparatus rather than a
correction.

**Measured.** Resident instructions fall from 512 lines to 505 (`CLAUDE.md`
390 to 383), which `tools/doc_check.py` reports and is the direction
`CLAUDE.md`'s own resident-growth rule wants.
