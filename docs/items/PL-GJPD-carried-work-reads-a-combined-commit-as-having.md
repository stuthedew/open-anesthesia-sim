---
id: PL-GJPD
title: _carried_work reads a combined commit as having carried the work, so the triage pass that closed PL-3CBS is recorded as its pull request because it also edited ROADMAP.md - three of main's 698 answerable closures disagree with their stored pr
status: untriaged
feature: commit-provenance
added: 2026-09-19
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
