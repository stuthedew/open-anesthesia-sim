---
id: PL-L1NX
title: contrast_check --base refuses only an entry added with its colour: an entry the base already holds goes on excusing its pair when a change makes that colour worse, since the list stores an item id and no ratio
priority: P3
effort: S
status: done
classes: defect
feature: contrast-base-entry-reading
milestone: v0.5.28
touches: tools/contrast_check.py, tests/unit/test_contrast_check.py, .claude/rules/ui-color.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-09-30
closed: 2026-10-18
pr: 1548
payoff: an excused contrast shortfall can only stay as bad as it was when excused, never get worse unnoticed
verify: grep -q 'def test_a_listed_pair_made_worse_is_refused' tests/unit/test_contrast_check.py
---

**Problem.** contrast_check --base refuses only an entry added with its colour: an entry the base already holds goes on excusing its pair when a change makes that colour worse, since the list stores an item id and no ratio

**Where.** `tools/contrast_check.py`, `shortfalls_added_with_their_colour`,
which `PL-VJFQ` built. An entry already on the base is skipped whatever the
change does to its colours. That is correct for a partial fix, and
`test_an_entry_the_base_already_has_is_not_added_by_a_partial_fix` pins it. It
is also what lets a change make a listed pair worse and stay green. The list is
empty today, so nothing is exposed yet.

**Why it matters.** `contrast_check` holds the interface's colour pairs to a contrast floor, and `KNOWN_SHORTFALLS` is its only exception list; an entry excusing a pair at any ratio lets a change make a listed pair worse and stay green. Latent: the list is empty (read 2026-10-01).

**Done when.** An entry records the ratio it excuses, `--base` refuses a change that lowers a listed pair below it, and a test pins that refusal beside the partial-fix test.

**Generator check.** The fact is what a `KNOWN_SHORTFALLS` entry excuses, a choice `PL-VJFQ` made; `PL-NDGS` is a second consequence of the same choice, so two, below a head's three. One-off pair under `dev-tooling`.

**Built 2026-10-18.** A `KNOWN_SHORTFALLS` entry is now `Shortfall(item, ratio)`. The ratio must equal what the pair measures (`Report.misrecorded`), and under `--base` a pair measuring below the base entry's ratio is refused (`shortfalls_made_worse`). The base's copy is read with `ast` as before. `test_a_listed_pair_made_worse_is_refused` needs the new `Shortfall` interface, so against the code before the fix it fails at collection rather than on its assertion.
