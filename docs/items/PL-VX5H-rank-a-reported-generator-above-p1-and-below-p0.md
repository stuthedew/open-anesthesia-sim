---
id: PL-VX5H
title: Rank a reported generator above P1 and below P0 in docket next, because P1 grows as development proceeds so a generator promoted only within its own band is never reached
status: untriaged
feature: convergence-visibility
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_plan.py
added: 2026-09-17
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
