---
id: PL-GJPD
title: _carried_work reads a combined commit as having carried the work, so the triage pass that closed PL-3CBS is recorded as its pull request because it also edited ROADMAP.md - three of main's 698 answerable closures disagree with their stored pr
priority: P2
effort: M
status: ready
classes: defect
feature: commit-provenance
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-19
payoff: stops the store recording a confident, well-formed and wrong pull request as the provenance of a closed change, which no check would report
verify: grep -q 'def test_a_combined_commit_that_carried_no_part_of_the_item' subprojects/docket/tests/test_vcs.py
---

**Problem.** _carried_work reads a combined commit as having carried the work, so the triage pass that closed PL-3CBS is recorded as its pull request because it also edited ROADMAP.md - three of main's 698 answerable closures disagree with their stored pr

**Found 2026-09-19 closing `PL-YFXG`**, in the audit that item's fix was
measured with, and unchanged by it.

`_carried_work` in `subprojects/docket/src/docket/vcs.py` asks whether the
closure commit's diff reached outside `docs/items/`. That is a *proxy* for "it
carried the work", and a commit doing two things at once defeats it.

`#129` (`d2ac0c5`) is a triage pass, which is the shape `PL-YDL6` exists to
refuse - it wrote `PL-3CBS`'s `status: done` while `#128` had done the work and
left the item at `ready`. But it also edited `ROADMAP.md` and
`docs/WORKING_NOTES.md`, so `_annotates_only` answers `False`, `_carried_work`
answers `True`, and `_number_closing` recovers `129` against a stored `128`.
The worked example in `_number_closing`'s own comment escapes the guard that
comment describes.

**Measured over the whole store**, `origin/main` at `c979d94`: 698 of 927
closed items have an answerable closure, and three disagree with the `pr` the
store holds.

| item | recovered | stored | why |
| --- | --- | --- | --- |
| `PL-3CBS` | 129 | 128 | triage pass that also edited `ROADMAP.md` |
| `PL-64LS` | 109 | 108 | same shape |
| `PL-21GS` | 499 | 225 | declares `docs/items/, docs/releases/` |

**Nothing is written wrong today**, which is why this is an item rather than a
`P0`: `bin/docket record` writes only where the field is absent, and all three
already hold the better answer. It fires on the next closure of this shape
whose `pr` is missing, and `docket check` would then report no error at all -
the field is present and well formed, which is `PL-KX9N`'s failure mode.

**Do not repair the three by hand.** `docket check` errors on rewriting a
closed item's recorded provenance, and the stored numbers are the correct ones.

**Likely shape of a fix.** The question `_carried_work` is really asking is
whether *this item's* work is in the diff, and the item already declares where
its work lives. `PL-YFXG` used that declaration for the queue-only half;
reading it for the general case - does the diff intersect the item's `touches`
- would answer both, and would have declined `#129` for `PL-3CBS`, whose
`touches` names four `subprojects/docket` paths that `#129` never goes near.
Count what it would change across the store before adopting it: the first half
of that measurement is in `PL-YFXG`'s close-out.

**Why it matters.** `pr:` is how a reader gets from a closed item back to the
change that made it, and it is the only route left - `commit:` was retired
(`PL-T63T`) because a squash merge discards the branch commit. A wrong number
does not look wrong: the field is present, well formed, and points at a real
pull request that really did touch the item's file, so `bin/docket check`
reports nothing. That is `PL-KX9N`'s failure mode, and it is why this is worth
an item rather than a note - the store would carry a confident, traceable, false
provenance line for a safety-critical project's own change history.

The three measured disagreements are not the damage. `bin/docket record` writes
only where the field is absent, and all three already hold the correct number,
so nothing in the store is wrong today. The damage is the next closure of this
shape: a commit that both closes an item and edits a file outside `docs/items/`
for an unrelated reason - which `CLAUDE.md`'s leading-id rule and its capture
rule together make ordinary rather than contrived.

Confirmed at triage, 2026-09-20: `PL-3CBS` stores `pr: 128`, which is the
number the recovery disagrees with.

**Done when.** A closure commit that carried no part of *this item's* work is
declined as its pull request even when its diff reaches outside `docs/items/`,
with the `PL-3CBS` case driven as a test; and the count of what the new reading
changes across the store is recorded before it is adopted, per the item's own
note above.
