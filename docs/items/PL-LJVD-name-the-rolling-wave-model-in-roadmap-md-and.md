---
id: PL-LJVD
title: Name the rolling-wave model in ROADMAP.md and state the prohibition on a second long-range plan
priority: P3
effort: S
status: ready
classes: infra
feature: planning-cadence
touches: ROADMAP.md
added: 2026-08-26
---

**Problem.** `ROADMAP.md` implements rolling-wave planning without naming it:
a fixed vision boundary ("What MVP means here"), a coarse far horizon (timeline
rows 4-9, "not yet scoped"), a detailed near horizon (v0.3.0 and v0.4.0 with
all four required subsections), and an elaboration ritual at each boundary
(the debt gate's four beats). A reader has to infer the model from its parts,
and a session has no name to reason with.

**Why it matters.** Naming it is cheap and makes the existing rules cohere —
"rows 4 to 8 are the intended order and are not yet scoped" reads as an
arbitrary restriction until it is recognized as progressive elaboration, at
which point it reads as the point. It also gives the missing prohibition
somewhere to live: nothing currently states that a second long-range,
task-by-task implementation plan must not be maintained alongside this one.
`ROADMAP.md` implies it; the closed external proposal in PRs #59/#60 stated it
well, and then violated it in the same file by duplicating the release train.

**Scope.** One short section in `ROADMAP.md`, near "The plan": the model's
name, what each horizon is detailed to, and the prohibition with its reason —
a second long-range plan goes stale faster than it can be kept authoritative,
and there is no check that can catch prose drifting from prose.

Deliberately *not* a new document. The rules that govern session behavior
belong in `CLAUDE.md`, which is always loaded; the rules that govern the
timeline belong in `ROADMAP.md`, which is loaded when the timeline matters. A
third file would be loaded never — which is what made the external proposal
inert regardless of its content.

**Done when.** `ROADMAP.md` names the model, states the horizon depths, and
carries the prohibition. No new file is created.

**Context.** Design round with the project owner, 2026-08-26. The vocabulary
came from a closed external proposal (PRs #59/#60) and is genuinely useful;
the proposal's remedy — 74 lines restating `ROADMAP.md` and `CLAUDE.md` in a
new file, plus a duplicate release train that went stale within the hour — was
not adopted.
