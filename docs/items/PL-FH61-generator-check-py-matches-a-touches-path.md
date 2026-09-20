---
id: PL-FH61
title: generator_check.py matches a touches path exactly, so an item declaring docs/items/<one file> is a singleton cluster: 6 of PL-G424's 21 members are invisible to it that way, and concurrent's 'same area' containment reading is the general form of the rule that would gather them
priority: P2
effort: S
status: ready
classes: infra
feature: generator-identification
touches: tools/generator_check.py, tests/unit/test_generator_check.py
added: 2026-09-19
payoff: settles whether the generator scan hides real clusters or is right to match exactly, so the apparatus-drift family stops being re-argued from scratch
verify: grep -q 'def test_an_item_declaring_one_item_file_joins_its_directory_cluster' tests/unit/test_generator_check.py
---

**Problem.** generator_check.py matches a touches path exactly, so an item declaring docs/items/<one file> is a singleton cluster: 6 of PL-G424's 21 members are invisible to it that way, and concurrent's 'same area' containment reading is the general form of the rule that would gather them

**Why it matters.** `tools/generator_check.py` is how a session is *shown* the
clusters worth judging for a root cause, and `CLAUDE.md` ranks a recorded
generator above every band but `P0`. A family the script cannot gather is one
nobody is prompted to look at, so the ranking never gets the chance to apply.
`PL-G424`'s apparatus-drift family is the measured case: 21 members, of which 8
declare `docs/WORKING_NOTES.md` and 5 declare `docs/items` - carried by those
two clusters - while 6 declare a single item file each and are therefore six
clusters of one.

A containment reading would gather those six. `bin/docket concurrent` already
has one: its "Same area only" tier compares a declared path against the paths
below it rather than for equality, so `docs/items/PL-G424-....md` and
`docs/items` are the same area there and different clusters here. Two commands
reading one field two ways is the drift worth closing, whichever way it lands.

**This is not `impairs-generators:`, and that was checked rather than
assumed** (triage, 2026-09-20). `CLAUDE.md` puts a *defect* in the machinery
that finds and ranks generators at the generator's own tier. Nothing here is
broken: `generator_check.py`'s module docstring already states this exact
boundary in its "What it can and cannot see" paragraph, with the same 21-member
measurement and the same split of 8, 5 and 6 - and the script is explicitly
advisory, exits 0 whatever it finds, and "reports candidates and decides
nothing". A documented limit of a deliberately non-deciding tool is an
enhancement to propose, not a function that broke, so this seats in its band
like any other item.

**Count before building, which is the thing this item is really for.** The
containment reading does not obviously improve the signal: folding the six
single-file declarations into `docs/items` adds them to a cluster that already
held 24 open items when it was last measured, which surfaces a large generic
path rather than the apparatus-drift family. The docstring's own conclusion is
that "a sweep that reads the briefs is the only detector for that shape".
So the measurement comes first - what clusters change, and whether any newly
shown cluster is one a session would act on - and recording that the exact
match is right is a legitimate outcome.

**Done when.** The containment reading is measured against this store, and
either `generator_check.py` clusters on containment with a test pinning the
`PL-G424` case, or the item is dropped with the count recorded and the
docstring's boundary paragraph naming `concurrent`'s different reading as
deliberate.
