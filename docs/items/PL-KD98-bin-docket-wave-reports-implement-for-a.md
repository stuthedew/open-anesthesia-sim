---
id: PL-KD98
title: bin/docket wave reports 'implement' for a milestone whose Required scope is complete, because the beat reads only the frozen gate list and never the scope's item ids
priority: P2
effort: S
status: done
classes: defect
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_release.py, subprojects/docket/tests/test_roadmap.py, subprojects/docket/README.md
added: 2026-09-05
closed: 2026-09-13
pr: 544
verify: uv run pytest subprojects/docket/tests/test_release.py && grep -q 'def test_the_digest_stops_declining_a_release_for_a_finished_milestone' subprojects/docket/tests/test_release.py
---

**Problem.** `bin/docket wave` chose `IMPLEMENT` for v0.4.0 while twelve of the
milestone's thirteen `Required scope` entries were `done`, and the digest
turned that into an assertion: `No release to offer: the roadmap gives 0.4.0
to "the teachable case", which is unfinished`. The project owner asked for the
cut anyway and was right.

**Why it happens.** `_shipping_the_gate()` in
`subprojects/docket/src/docket/roadmap.py` decides the beat from the *frozen
gate list* and the step's version order alone. A milestone recording both a
gate and a scope of its own falls to the `else` branch and is `IMPLEMENT` by
construction, whatever its scope's real state — the docstring says so
deliberately: "its gate clears so that its scope can be implemented, which is
the cadence's ordinary case".

**Why it matters.** The declining is correct; the *wording* is not.
`.claude/skills/docket/SKILL.md` already tells a session that `wave` "computes
and decides nothing", so a session that reads the skill adds the judgment. But
the digest prints `No release to offer` in every session, ahead of the skill
being loaded, and phrases a non-answer as a verdict. A session that trusts it
declines a release that is due.

**Where.** `subprojects/docket/src/docket/roadmap.py` (`_shipping_the_gate`,
`wave`), `subprojects/docket/src/docket/render.py:1058` (the digest line).

**Two candidate fixes, and the choice is the design work.** Parse `PL-` ids out
of the `Required scope` subsection the way the gate list is parsed, and report
the scope's own split (`12 of 13 scope entries closed`) — the same shape the
gate already gets — leaving the beat to say `implement` with the count beside
it. Or leave the computation alone and soften the digest's assertion to a
declining one, which costs nothing and fixes the misreading without teaching
the tool to read prose it was deliberately kept out of. Prefer the second
unless the first turns out cheap: `Required scope` is prose with ids in it,
and a parser over it is the judgment half `CLAUDE.md` says not to script.

**Done when.** A session standing on a milestone whose Required scope is
complete is not told there is no release to offer.

**The tiebreak the brief names has been measured, 2026-09-13, and it comes back
the opposite way: the first option is not merely cheap, it is three-quarters
already shipped.** `Required scope` is parsed today. `_subsection_ids` reads the
subsection in full, `MilestoneSection.scope_ids` carries the result, and
`SECTION_ID_RE` carries thirty lines of deliberation about exactly this
grammar — why `Required scope` is read in full while the frozen list is read by
its entries' heads, and what an unread prose mention costs. Three shipped
behaviors already rest on it: `Scope.placement`, `MilestoneStates.ships_with`,
and `check_gate_dispositions`. So the brief's reason for preferring the second
option — "a parser over it is the judgment half `CLAUDE.md` says not to
script" — is a rule this project examined and decided the other way, in code, in
a comment written to be read at exactly this moment. Against the live roadmap
`v0.4.0` parses 21 gate entries and 39 `scope_ids`; `v0.5.0`, 160 and 171. The
only piece missing is separating the `Required scope` half from the gate half,
which is one field on `MilestoneSection`.

**But the first option as written does not satisfy this item's own "Done
when", and that is what makes the choice the project owner's rather than this
tiebreak's.** "leaving the beat to say `implement` with the count beside it"
adds a count to `wave` and changes nothing about the digest, which would go on
printing `No release to offer ... which is unfinished` in exactly the session
the item was filed about. Nor can the offer be softened on its own: `_beat_line`
and `_release_advice` are read one above the other, so a digest that offers the
release above a beat saying `implement` is the two-lines-contradicting-each-other
failure `PL-D2GW` and `PL-Q2BJ` already cost this project.

**What the computation actually cannot say.** `_shipping_the_gate` reaches
`RELEASE` on two arrangements — the step is an earlier milestone than the
section recording the gate, or the step is that section and it records no scope
of its own. A milestone recording a gate **and** a `Required scope` is neither,
so `wave` can never print `release` for one, whatever the state of its scope.
That is not a wording defect: `v0.5.0` is that shape, and `v0.4.0` was, so the
beat for the current milestone has no reachable `release` state at all. The
`RESERVED` message's "which is unfinished" is an inference from "the beat is not
`RELEASE`", and for this shape of milestone that inference is unconditional.

**So the third route, which is the one recommended and which needs an answer
before it is built:** give `MilestoneSection` its `Required scope` ids
separately, and let `_shipping_the_gate` take a third arrangement — the step is
the gate's own milestone, that milestone records a scope of its own, and every
id in that scope is closed. The beat then moves to `release`, `release_offer`
sees `plan.beat == RELEASE` and returns `STANDS`, and the digest's existing
wording becomes true without being touched. Where the scope is *not* complete,
`wave` gains the count the first option asked for (`12 of 13 scope entries
closed`) and the digest's decline stays, now resting on a fact rather than on a
construction. Conservative in the same direction as `GateStatus.unknown_ids`: a
scope naming an id the store does not hold is not complete, because its state is
unknown rather than closed.

**Put to the project owner rather than built, because it changes the cadence —
what beat every session is told, and whether a release is offered for the
milestone the project is standing on. Approved 2026-09-13.**

**Done.** `_shipping_the_gate` is now `_release_due`, answering *what* to release
rather than *whether*, with the third arrangement beside the two it already
held. `MilestoneSection` carries `own_scope_ids` — the `Required scope` half
alone, separate from the union `scope_ids` that answers placement, because a
gate can be clear with entries still open and the union would read a milestone
as unfinished on work deferred outside it. `ScopeStatus` and `scope_status()`
split those ids into closed, open and unknown, exactly as `GateStatus` does, and
`Wave` carries the result.

**Three deliberate narrowings, each the safe direction:**

- **No blocker walk**, unlike `GateStatus.clearable`. A gate entry deferred to
  later work is not something *this gate* can be asked to finish; a scope id is
  a different question, because the milestone ships when its scope is done and
  an id it cannot reach yet means it is not ready whoever is at fault. Counting
  one out would offer a release for a milestone with work still in it.
- **An unknown id withholds completeness**, as `GateStatus.unknown_ids` does: a
  typo or a file that never existed leaves the state unknown, not closed.
- **An empty scope is not a finished one.** A section whose frozen list is its
  whole content records no `Required scope` subsection, and reaches `release`
  by the second arrangement rather than through this.

**The arrangement could not rest on `step`, which is what the brief's option 1
would have missed.** `_current_step` puts the project on the row *after* the
last milestone it released — here the `v0.4.x` patch track, which is not a
milestone and carries `(0, 4, -1)`, a track marker rather than a number anything
can be cut at. A third arrangement reading `step.version` would have declined on
the very project that filed the item. For the same reason `Wave` now carries
`release_version` and `release_name`: left to read `plan.step`, `release_offer`
fell through to the bump's own arithmetic and offered `0.4.21` directly above a
beat reading `release v0.5.0` — the two-lines-contradicting-each-other failure
`PL-D2GW` and `PL-Q2BJ` already cost, reintroduced by the fix for it.

**Order matters between the first and third arrangements, and is tested.** Under
Gate 0's exception the frozen list ships as its own earlier version first, so a
gated milestone whose scope happened to be complete must not be offered ahead of
the release its gate earned.

**What a session now sees.** `bin/docket wave` gains a `Scope` block once the
gate is clear — withheld while it is open, where the gate block already says
what is due and `format_wave`'s budget is five lines read beside the digest —
and the beat carries the count that makes it checkable: `implement v0.5.0 — the
case you can branch - its gate is clear, 13 of 21 Required scope ids closed and
8 still open`, or `release ... - its gate is clear and all 21 Required scope ids
have closed`. The digest's own wording is untouched and is now true, which was
the point: `No release to offer ... which is unfinished` was an inference from
"the beat is not `RELEASE`", and for this shape of milestone that inference used
to be unconditional.

**Measured against the live roadmap on the day it landed**, which is also the
item's own worked example recomputed: v0.4.0's `Required scope` is **16 of 17
ids closed**, the one open being `PL-B9PY` (decompose `SimulationView` so two
runs can be rendered at once) — the brief said "twelve of thirteen" counting
entries by eye. v0.5.0 is 10 of 21, v0.5.1 is 1 of 13, and no section names an
id the store does not hold. Today's beat is unchanged: Gate 1 is open, so the
beat is still `clear the gate` and the `Scope` block stays withheld.

**Swept.** `subprojects/docket/README.md`'s `docket wave` paragraph enumerated
what the command reports and was left incomplete by this change; it now carries
the scope split, the beat it decides, and the two narrowings that make it
stricter than the gate's count. Checked and still true without editing:
`docs/ARCHITECTURE.md` (the timeline grammar, and the Python floor the tools are
held to), `docs/WORKING_NOTES.md`, `docs/resident-instructions.md`, `ROADMAP.md`,
`docs/worker.md`, `.claude/skills/docket/SKILL.md`, and the README's own "What a
milestone places, and what it only mentions", which is about placement and is
untouched by the split.
