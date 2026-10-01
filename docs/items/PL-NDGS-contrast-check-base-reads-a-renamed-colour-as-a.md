---
id: PL-NDGS
title: contrast_check --base reads a renamed colour as a new one, so renaming a colour KNOWN_SHORTFALLS lists fails make check with no way to split the rename from the entry's move
priority: P3
effort: S
status: ready
classes: defect
feature: dev-tooling
touches: tools/contrast_check.py, tests/unit/test_contrast_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-09-30
payoff: a listed colour can be renamed in one change without failing make check
verify: grep -q 'def test_renaming_a_listed_colour_passes_the_base_check' tests/unit/test_contrast_check.py
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

**Why it matters.** A rename is the refactor least likely to be held back, and here it fails `make check` with no route that lands the rename and the entry's move apart, so the cheapest response is to keep a misleading colour name. Latent: the list is empty (read 2026-10-01).

**Done when.** Renaming a listed colour passes `--base`, with a test, while a new constant reusing an existing value still counts as a new colour.

**Generator check.** See `PL-L1NX`: the same design choice, a second consequence.
