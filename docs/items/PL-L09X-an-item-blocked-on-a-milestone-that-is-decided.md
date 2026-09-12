---
id: PL-L09X
title: An item blocked on a milestone that is decided but not yet named has no honest status: bare blocked errors, and blocked-by only accepts a version the roadmap already places
priority: P2
effort: M
status: done
classes: defect, infra
feature: planning-cadence
milestone: v0.4.14
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests/test_checks.py
added: 2026-09-10
closed: 2026-09-12
pr: 496
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_an_item_the_scoped_milestone_places_is_not_ready_to_promote' subprojects/docket/tests/test_checks.py
---

**Problem.** An item blocked on a milestone that is decided but not yet named has no honest status: bare blocked errors, and blocked-by only accepts a version the roadmap already places


**Found 2026-09-10**, trying to record that `PL-GS3R` ships after the PySide6
port. Both halves of the finding are one attempt each:

| Written as | `docket check` says |
| --- | --- |
| `status: blocked`, no `blocked-by` | error: "marked blocked but names no blocking item or milestone" |
| `blocked-by: v0.5.0` | accepted, then advises "v0.5.0 is scoped ... ready to promote" |

**Neither is honest here.** The first is refused. The second would name the
wrong blocker - the port is not `v0.5.0`, which is the branched-run milestone -
and would then read as promotable, which is the opposite of the truth.

**Why the gap exists, and why it is narrow.** `_check_references` holds a
milestone blocker "to something real ... a typo would otherwise read as a
dependency on something that is never going to be scoped, which is
indistinguishable from a live block and never fires". That reasoning is right
and this item does not propose weakening it. What it names is the state between
a milestone being *decided* and being *scoped*: real, sometimes days long, and
currently unrepresentable.

**What it costs while unrepresentable.** `PL-GS3R` is `P1` and `safety`-classed,
so it ranks at the top of `bin/docket next` as startable work, while the one
thing a session must not do is build it - on the toolkit being replaced. The
guard is a paragraph at the top of its brief, which works only for a session
that reads the brief before acting, and nothing enforces it. That is the
"gives a wrong answer silently" test in `CLAUDE.md`'s compounding-friction rule.

**Not proposing a mechanism yet**, deliberately: the cheapest fix may simply be
that scoping a milestone is fast enough that the window never matters, in which
case this closes as "not worth a mechanism" with the reasoning recorded. Worth
deciding once rather than re-meeting; the alternatives worth costing are a
`blocked-by` entry that names a milestone the roadmap has *reserved* but not
scoped, and a `blocked-reason:` free-text field that blocks without an edge and
is therefore invisible to ranking.


## The diagnosis above is half right; the gap is larger (2026-09-10, same day)

**What was found on scoping `v0.5.1`.** `PL-GS3R` now carries
`blocked-by: v0.5.1`, and `docket check` immediately advises: *"v0.5.1 is
scoped and every other blocker has closed; it is ready to promote."*

**So `blocked-by: <version>` does not mean what this item assumed.** It means
**blocked until that milestone is *scoped*** - which is exactly what `PL-W8XP`
built it for, and its own title says so: "an item blocked on a milestone being
scoped". The reasoning is sound: until a milestone is scoped you do not know
what it requires, so the item cannot be designed. `PL-B9PY` is the worked
example - it "could not be designed until v0.5.0 settled what a side-by-side
comparison renders".

**What has no expression at all is "ships *with* milestone X".** That is
`PL-GS3R`'s case: it is fully designed - the chord-width rule is settled and
recorded - and what it waits for is the port to *land*, because building it on
Flet costs frame time the port makes free. Scoping `v0.5.1` did not unblock it
and never could.

**The original framing - "decided but not yet named" - was a symptom.** Naming
the milestone closed nothing; it moved the item from one wrong state to a less
wrong one. The real gap is that `blocked-by` carries one relation where the
project needs two.

**`blocked` is still the better of the two available states, and that is why it
stays.** `bin/docket next` excludes blocked items, so the `P1` `safety` hazard
this item was filed over is gone: the only route to promoting `PL-GS3R` now runs
through a groomer reading its brief, which says on its first line that the fix
ships with the port. At `ready` it ranked top of the queue as startable work.
The cost is a standing false advisory on every `docket check`, which is
precisely what `CLAUDE.md`'s "a check earns its place every run" is against -
an advisory that fires without changing a decision trains a reader to skim past
the ones that would.

**Two shapes worth costing, neither proposed yet.** A second relation -
`awaits: v0.5.1`, blocked until *shipped* rather than until scoped - which is
honest and adds a field. Or reading the milestone's own Required scope: `v0.5.1`
names `PL-GS3R` in it, so a checker could resolve "this item is claimed by a
scoped, unshipped milestone" from what is already written, and add no field at
all. The second is cheaper and is the one to price first.

**Re-banded from the original.** This is no longer a one-day window that closed
itself. It is a standing false advisory plus a relation the store cannot express,
with one live instance, and the recommendation to close it as "not worth a
mechanism" is withdrawn.

**Decision needed.** Whether to add a second relation, and which shape. The two
costed above: an `awaits: <version>` field meaning blocked until that milestone
*ships* rather than until it is scoped; or resolving the same fact from what is
already written, by reading the milestone's own `Required scope` - `v0.5.1`
names `PL-GS3R` in it - and adding no field at all. The second is cheaper and is
the one to price first.

**Why it matters.** There is a live instance and it is costing a false advisory
on every run. `bin/docket check` says of `PL-GS3R` that "v0.5.1 is scoped and
every other blocker has closed; it is ready to promote", which is the opposite
of the truth: the item ships *with* the port and cannot be promoted ahead of it.
An advisory that fires without changing a decision is what `CLAUDE.md`'s "a
check earns its place every run" is against, and this one has been standing
since v0.5.1 was scoped. Confirmed still firing 2026-09-12.

**Done when.** `bin/docket check` stops advising that `PL-GS3R` is ready to
promote while the milestone it ships with is unshipped, without weakening
`_check_references`' refusal of a blocker the roadmap places nowhere - or the
decision is recorded that the false advisory is cheaper than the mechanism, in
which case this item is `dropped` with that reasoning.

## Answered 2026-09-12 (project owner): read it from the Required scope

**The decision.** The cheaper of the two shapes costed above: no new field.
`MilestoneStates` gains `claimed` (each milestone section's own `scope_ids`)
and `released`, and `ships_with(version, identifier)` is true when the
milestone has not shipped and its own scope names the item. `checks.py` skips
the "ready to promote" advisory for those.

**Narrow deliberately.** A scoped, unshipped milestone that does *not* name the
item leaves the original advisory correct - that item was waiting on the
scoping round, and the scoping round has happened - so suppressing it too would
trade a false advisory for a missing one, which is worse. `_check_references`'
refusal of a blocker the roadmap places nowhere is untouched.

**What it cost and what it bought.** No field, no edit to any item, and one
read of what `ROADMAP.md` already says. `bin/docket check` now reports zero
advisories against this store; it had reported the same false one on every run
since `v0.5.1` was scoped.

**The `awaits:` field is not built, and this records why.** Once the relation
can be read from the roadmap, a second field would be a second place to state
it and a second thing to keep true - and the roadmap's `Required scope` is
where a reader already looks to find out what a milestone carries.
