---
id: PL-29RM
title: In a truncated clone, vcs._written_since reads a grafted commit's whole tree as written since the fork, because git shows a shallow boundary commit as a root, so a restore to content the base holds at the horizon reads as landed - the ever-held misread again, bounded to the horizon's tree; test_a_merge_of_main_read_below_an_uneven_horizon_spends_only_what_a_squash_took passes through it
priority: P2
effort: M
status: ready
classes: defect
feature: pre-fork-content
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-28 triage pass
added: 2026-09-27
payoff: stops a shallow agent clone telling a session its unmerged work has landed when a branch restores a file to the history horizon's version
verify: grep -q 'def test_a_restore_to_the_horizon_tree_does_not_read_as_landed' subprojects/docket/tests/test_vcs.py
---

**Problem.** In a truncated clone, vcs._written_since reads a grafted commit's whole tree as written since the fork, because git shows a shallow boundary commit as a root, so a restore to content the base holds at the horizon reads as landed - the ever-held misread again, bounded to the horizon's tree; test_a_merge_of_main_read_below_an_uneven_horizon_spends_only_what_a_squash_took passes through it

**Why it matters.** Agent containers are shallow clones, and `_written_since`
feeds every reader of whether the base took a branch's change. A branch that
restores a file to the version the base held at the history horizon would read
as landed there - the `#1118` shape, a session told its open work had merged.

**Not reproduced at triage, 2026-09-28:** this clone is not shallow (`git
rev-parse --is-shallow-repository` answered `false`), so no one command shows
the fault here; the mechanism is the brief's.

**Done when.** A grafted boundary commit contributes nothing to
`_written_since`, so content only it wrote reads as not landed - the safe side
the function's docstring already states for a truncated clone's missing
commits - held by a test on a shallow scratch clone.

**Generator check.** An instance of `PL-927J`'s fact (whether the base already
holds a branch commit's change), filed in the commit that closed `PL-927J` as a
site its fix left, so not a post-close instance: ordinary work on the fact's one
reader.
