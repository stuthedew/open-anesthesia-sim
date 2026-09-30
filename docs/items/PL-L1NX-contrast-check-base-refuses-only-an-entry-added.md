---
id: PL-L1NX
title: contrast_check --base refuses only an entry added with its colour: an entry the base already holds goes on excusing its pair when a change makes that colour worse, since the list stores an item id and no ratio
status: untriaged
feature: dev-tooling
added: 2026-09-30
---

**Problem.** contrast_check --base refuses only an entry added with its colour: an entry the base already holds goes on excusing its pair when a change makes that colour worse, since the list stores an item id and no ratio

**Where.** `tools/contrast_check.py`, `shortfalls_added_with_their_colour`,
which `PL-VJFQ` built. An entry already on the base is skipped whatever the
change does to its colours. That is correct for a partial fix, and
`test_an_entry_the_base_already_has_is_not_added_by_a_partial_fix` pins it. It
is also what lets a change make a listed pair worse and stay green. The list is
empty today, so nothing is exposed yet.
