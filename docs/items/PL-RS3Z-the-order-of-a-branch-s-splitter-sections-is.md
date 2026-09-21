---
id: PL-RS3Z
title: The order of a branch's splitter sections is unasserted; the test counts them without checking where they land
priority: P2
effort: S
status: ready
classes: test
feature: branch-display-tests
touches: tests/integration/test_simulation_view.py
added: 2026-09-20
payoff: catches a branch whose readouts land below both charts instead of beside the trunk's, which a count-only assertion cannot see
verify: grep -q 'def test_the_branchs_sections_land_beside_the_trunks_in_order' tests/integration/test_simulation_view.py
---

**Problem.** The order of a branch's splitter sections is unasserted; the test counts them without checking where they land

**Found 2026-09-20** by the adversarial review of `#784`, and upheld against
refutation. `PL-VKJW` is what made two runs reachable from a shipped entry
point for the first time, so this is that change's to answer rather than a
pre-existing gap.

**Why it matters.** `SimulationView._restack_sections` exists for a stated
reading purpose: every run's readouts first, then every run's settings, then the
charts, "so a reader compares like against like down one column". Order is the
whole of what that method does - `QSplitter.addWidget` moves a section it
already holds, so re-adding in order *is* the reordering.

`test_the_run_added_after_construction_is_named_and_given_its_own_sections`
asserts `_stacked_sections(view).count() == sections_before + 2` and nothing
about position. A `_restack_sections` that appended the branch's two sections
after the charts - readouts, settings, charts, readouts, settings - would give
the same count and pass, while putting the branch's numbers below the plots and
separating them from the trunk's by the full height of both charts. That is a
comparison the reader has to scroll to make, which is the failure the method was
written to prevent.

**Verified 2026-09-20**: the body of that test in
`tests/integration/test_simulation_view.py` reads `_stacked_sections(view).count()`
before and after the fork and compares the two; no assertion indexes the
splitter. `test_no_handle_of_the_restacked_splitter_becomes_draggable` iterates
the handles but asserts only that each is disabled.

**Done when.** A test indexes the restacked splitter after a fork and holds the
documented order - both runs' readouts, then both runs' settings, then the
charts - so a section added in the wrong place fails rather than counts.
