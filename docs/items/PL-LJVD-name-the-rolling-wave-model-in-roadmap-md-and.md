---
id: PL-LJVD
title: Name the rolling-wave model in ROADMAP.md and state the prohibition on a second long-range plan
priority: P3
effort: S
status: done
classes: infra
feature: planning-cadence
touches: ROADMAP.md, docs/items/PL-5XG1-roadmap-md-s-development-pathway-still-says.md
added: 2026-08-26
closed: 2026-09-26
pr: 1117
payoff: ROADMAP.md says which section holds the order of each release and why later rows carry no detail, so the pathway's stale Phase 1 sentence stops reading as a second order and no second plan of releases is started beside the file
verify: grep -qiF 'rolling-wave planning' ROADMAP.md && grep -qF 'No second plan of releases is kept beside this one' ROADMAP.md && grep -qF 'The order is held once, by horizon.' ROADMAP.md
---

**Problem.** `ROADMAP.md` runs rolling-wave planning without naming it. A
detailed near horizon (each scoped, unshipped milestone's own section), a
coarse middle one (the timeline's rows not yet scoped), a far one
(§ "Development pathway" over § "Planned milestones"), one moment at which
detail moves inward (beat 1 of § "The cadence") and an outer boundary that
bounded the first waves (§ "What MVP means here") are all there, and a reader
has to infer the model from its parts. Nothing states that a second plan of
releases must not be kept beside this one.

**Why it matters.** Naming it is cheap and makes the existing rules cohere:
"Rows 9, 11 and 13 are the intended order and are not yet scoped" reads as an
arbitrary restriction until it is recognized as progressive elaboration, at
which point it reads as the method. It also gives the missing prohibition
somewhere to live. A second plan goes stale faster than it can be kept
authoritative, and no check can catch prose drifting from prose.

**Re-confirmed 2026-09-26, and the shape has changed.** Filed 2026-08-26, 283
`ROADMAP.md` commits ago. What still holds: `grep -ciE 'rolling.wave|progressive
elaboration' ROADMAP.md` prints 0, and no sentence in `ROADMAP.md`,
`CLAUDE.md`, `docs/` or `.claude/rules/` forbids a second plan. The nearest are
"One timeline." at the head of § "The plan", which is about debt and features
sharing one timeline, and the file's opening paragraph, which says what to do
when another artifact conflicts with it rather than that none should be kept.
What moved: the brief named its horizons by row and version ("timeline rows
4-9", "v0.3.0 and v0.4.0"), and both went stale when v0.2.8, the `v0.4.x`
track, the Qt port and the `v0.7.x` track were inserted - the drift this item
is about, reaching the item that describes it. So the brief now names its
horizons by section.

**A second statement of the order already exists inside the file, and has
drifted.** § "Development pathway" says of itself "this is the order it is
intended to be worked in", and its reordering note ends "v0.4.0 is that work;
Phase 1 follows it unchanged". § "The timeline" puts Phase 1's substance
generalization at v0.9.0, after v0.5.0, v0.6.0, v0.7.0 and v0.8.0. So stating
the horizons has to include which of the two holds the order of a release the
timeline names, or the section describes a model the file does not follow.
The pathway's stale paragraphs are `PL-5XG1`'s.

**Scope.** One section at the head of § "The plan": the model's name with a
citation for it; what each horizon is detailed to and where it is written;
which section holds the order; how detail moves inward; and the prohibition,
with its reason and its instance. Plus the two sentences elsewhere in
`ROADMAP.md` that give the pathway the whole catalogue's order - its own
opening and § "Planned milestones"' - narrowed to agree. Nothing below the
pathway's opening is rewritten here.

**Pitched no wider than the hazard**, per `.claude/rules/expert-review.md`
§ "Say what would falsify it, then record the instance rather than the rule".
Two things would falsify "no second plan": a check able to hold two prose plans
in step, which does not exist and is not planned - a *generated* view cannot
drift, so `bin/docket wave` and the session digest's plan line are outside the
rule by construction - or a second party whose plan has to live elsewhere,
which nothing on the roadmap brings. A dated record of a decision that names a
version - `docs/WORKING_NOTES.md`'s item-34 thread, `docs/ARCHITECTURE.md`'s
"as of 2026-09-16" note, `docs/MODEL.md`'s second-window decision - is history
and stays legal; restating the sequence of releases or a milestone's scope is
what the rule refuses. A survey of the standing documents on 2026-09-26 found
no restatement of that kind outside `ROADMAP.md`.

Deliberately *not* a new document, as decided in the design round: the rules
governing the timeline belong in `ROADMAP.md`, which is read when the timeline
matters, and a third file would be read never - which is what made the
external proposal inert regardless of its content.

Worked at the project owner's request of 2026-09-26 while `PL-MT3R` carries
`generator: live`, which lifts `CLAUDE.md`'s pause on new workflow rules for
that request (`PL-6Q9L`).

**Done when.** `ROADMAP.md` names the model, states each horizon's depth and
which section holds the order, and carries the prohibition. No new file is
created.

**Context.** Design round with the project owner, 2026-08-26. The vocabulary
came from a closed external proposal, pull requests #59 and #60, whose
`docs/PLANNING.md` wrote "Do not maintain a second long-range task-by-task
implementation plan" and in the same file restated the order as "v0.3.0
foundation -> v0.4.0 teachable case -> Gate 1 -> v0.5.0 branch and compare ->
Gate 2 -> v0.6.0 schematic -> Gate 3 -> v0.7.0 multi-substance/N2O -> beyond"
(read from #60's diff, 2026-09-26). v0.2.8 was inserted ahead of that sequence
on 2026-08-30, and on 2026-09-16 the schematic moved to v0.8.0 and
multi-substance to v0.9.0. The proposal's remedy - 74 lines restating
`ROADMAP.md` and `CLAUDE.md` in a new file - was not adopted.

<!-- absent: docs/PLANNING.md -->
