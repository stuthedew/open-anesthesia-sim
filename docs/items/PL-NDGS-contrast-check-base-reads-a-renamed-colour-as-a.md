---
id: PL-NDGS
title: contrast_check --base reads a renamed colour as a new one, so renaming a colour KNOWN_SHORTFALLS lists fails make check with no way to split the rename from the entry's move
status: untriaged
feature: dev-tooling
added: 2026-09-30
---

**Problem.** contrast_check --base reads a renamed colour as a new one, so renaming a colour KNOWN_SHORTFALLS lists fails make check with no way to split the rename from the entry's move

**Where.** `tools/contrast_check.py`, `shortfalls_added_with_their_colour`,
which `PL-VJFQ` built and whose docstring states this price. It compares names
rather than values alone, so a new constant holding a value another already has
still counts as a new colour. The rename moves the requirement's key and so the
entry's, and the two cannot land apart without `stale_shortfalls` firing. No
listed colour has ever been renamed, and the list is empty today.

**Not a recurrence of `PL-KJXS`** (a `QByteArray` handed to a Qt entry point
that keeps its pointer). `bin/docket new` matched the two titles on the words
around "fails make check", and nothing else about them is shared.
