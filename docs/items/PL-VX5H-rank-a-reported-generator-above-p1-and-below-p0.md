---
id: PL-VX5H
title: Rank a reported generator above P1 and below P0 in docket next, because P1 grows as development proceeds so a generator promoted only within its own band is never reached
status: done
feature: convergence-visibility
added: 2026-09-17
closed: 2026-09-17
priority: P2
effort: M
classes: infra
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_model.py, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_plan.py, subprojects/docket/README.md, tools/generator_check.py, tests/unit/test_generator_check.py, docs/ARCHITECTURE.md, docs/items
verify: uv run pytest subprojects/docket/tests/test_plan.py subprojects/docket/tests/test_model.py tests/unit/test_generator_check.py -q && grep -q 'def test_a_generator_outranks_a_safety_classed_p1' subprojects/docket/tests/test_plan.py
---

**Problem.** Rank a reported generator above P1 and below P0 in docket next, because P1 grows as development proceeds so a generator promoted only within its own band is never reached

**Decision (project owner, 2026-09-17).** A cluster that
`tools/generator_check.py` reports ranks **above `P1` and below `P0`**. Not a
promotion within its own band, which was the session's recommendation and is
refused: *"We constantly add more P1 as we develop, so these never get done and
the bugs pile up."* Band-relative promotion moves a generator to the top of a
band that is itself growing, so the generator's position is unchanged in
absolute terms and the pile-up continues. The decision is about what a
generator competes with, not where it sits in a list.

**What this is worth today: nothing.** `generator_check` reports no cluster on
this tree, so the new rank is unreachable until one appears. That is the
intended shape - the mechanism exists so the *next* generator is ranked
correctly on the day it is detected rather than after somebody notices it - but
it means this cannot be validated against a real reported cluster and its test
must construct one.

**One question the build must answer first, and must not decide on its own.**
`P1` currently holds 3 items, all product-lane. `CLAUDE.md`'s safety-critical
standard is a floor rather than a preference, so an apparatus generator
outranking a `safety`- or `science`-classed `P1` would put workflow tooling
ahead of a clinical-output defect. Two readings of the decision are available
and it does not distinguish them: generators outrank *all* `P1`, or generators
outrank `P1` except `safety`/`science`-classed items. Put it to the project
owner before building; do not infer it.

**Done when.** `docket next` places a reported generator between `P0` and `P1`
under the answer to that question; a test constructs a reported cluster and
asserts the ordering against both a `P0` and a `P1`; and the rank is visible in
`docket next`'s stated reason, so a session can see why it was offered.

**Decision reaffirmed and widened (project owner, 2026-09-17).** Asked whether
`safety`- and `science`-classed `P1` should be exempt, the answer was no: a
generator ranks above **everything but `P0`**. The session's recommendation to
carve out the clinical bands is refused and must not be re-proposed without a
new argument. The rule is now resident in `CLAUDE.md`.

**The definition changed with it, and it is not what `generator_check.py`
measures.** The owner's test is *"the root cause of more than 2 PLs"* - three
or more downstream items traced to one mechanism. `generator_check.py` measures
something else: a ratio over a `touches` path, `r >= 1.0`, gated behind
`MIN_CLOSED = 8` closures. The two disagree in the direction that matters. On
2026-09-17 the ratio test reported **no** generators while `PL-6ZQY` had
already named **six** clusters under one root cause, `PL-BHVM` among them at
nineteen items. A test that can only fire after eight closures reports the weed
once it has seeded, which is the failure the owner's metaphor names.

**Why the citation count cannot be the test either.** Items cited by more than
two other open items number 33 on this tree. Citation is not causation - an
item is cited for context, for provenance, for a stale line reference - and
promoting 33 items above `P1` would mean nothing. This is the judgment half
`CLAUDE.md` refuses to script.

**So record the fact rather than infer it**, which is `PL-6ZQY`'s own remedy
turned on this problem. Proposed and not yet built:

1. A `root-cause-of:` front-matter field naming three or more item ids. A
   session that identifies a generator writes it; nothing guesses it.
2. `docket check` validates every id resolves, and that the field carries at
   least three.
3. `docket next` ranks any item carrying it above every band but `P0`, and says
   so in its stated reason.
4. `generator_check.py` moves from verdict to **candidate surfacing** - it
   prints clusters worth a session's judgment (shared `feature`, citation
   density, the ratio it already computes) without claiming any is a generator.
   Its `MIN_CLOSED = 8` gate is wrong for the new definition and comes out.

**Done when** all four hold, and `PL-BHVM` carries a `root-cause-of:` listing
the items it explains, since it is the worked example the rule was written for.

**Built 2026-09-17.** All four parts, each with tests.

1. `root-cause-of:` on the `Item` model, parsed and rendered like any other
   list field.
2. `docket check` holds every id to naming a real item, holds the list to three
   *distinct* ids, and refuses a self-reference. `model.root_cause_faults` is
   one rule read by both the checker and the ranking, so they cannot disagree
   about what a claim is.
3. `docket next` ranks a sound claim directly below `P0` - above
   `PLACEMENT_ORDER` as well as above `band`, which is what "above everything
   but `P0`" has to mean - and the reason opens "Ranked as a generator" and
   names the ids. The digest's `Top:` line carries the same mark, without which
   every session would open on a `P2` leading a queue with `P1`s in it and
   nothing saying the ranking meant it. An unsound claim ranks on its band:
   `docket check` runs separately, so a typo must not buy a promotion.
4. `generator_check.py` is candidate surfacing. `MIN_CLOSED = 8` is gone, and
   the floor is now the definition's own - three open items. It shows a cluster
   only where a signal fires (three open items sharing a `feature`, one cited by
   three or more other open items, or `r >= 1.0`), prints all three, and says
   plainly that none of them is a generator. A path with no closures declines
   the ratio rather than printing `0.00`.

**Marking the known generators found that four of the six have no causing
item.** `PL-BHVM` carries `root-cause-of:` naming its ten still-open instances,
and `PL-L4YG` (triage has no write command) names five. The other four clusters
`PL-6ZQY` describes have nobody to carry the field, and the nearest candidates
are each scoped narrower than their cluster - writing the field onto one would
record a claim its own brief contradicts *and* promote a narrow item above
every band but `P0`, where nobody could work the cluster from it:

- **What a `verify:` command proves** - `PL-LKGL` is `done` and refused the
  general contract; `PL-0M32` is one sub-question. Filed as `PL-6TP8`.
- **The roadmap is prose the tooling parses** - `PL-6P9Y` moves exactly one id
  and says so in its own triage note. Filed as `PL-HWW1`.
- **Prose that asserts facts about the tree** - `PL-036` records the general
  case as settled: *"whether a documented statement is still true stays
  human."* Filed as `PL-4FBP`.
- **The checkout is a cache nobody validates** - `PL-F48B` decides tags after a
  rewrite only, and the permitted-ref-operations half has no item at all. Filed
  as `PL-4Q9B`.

The four carry `feature: generator-heads` and each records its cluster's
candidate members, unverified, with what the head would have to decide. Whether
to write a head for each and mark it is the project owner's call, since a
generator outranks a `safety`-classed `P1` and these four heads would be a
session's composition rather than a found fact.
