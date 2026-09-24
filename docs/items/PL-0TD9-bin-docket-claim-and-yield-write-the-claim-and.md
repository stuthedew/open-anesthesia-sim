---
id: PL-0TD9
title: bin/docket claim and yield write the claim, and start mode is rewritten around them
priority: P2
effort: M
status: ready
classes: defect
feature: claim-record
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, .claude/skills/docket/modes/start.md, .claude/skills/docket/modes/picking.md, subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_claims.py, subprojects/docket/src/docket/claiming.py, subprojects/docket/tests/test_claiming.py, subprojects/docket/README.md
blocked-by: PL-3FYK
deferred-from: v0.6.0 - filed after the freeze by PL-MB2W's design round (2026-09-24), and not safety or science; generator work, which the pause on new mechanisms exists for
added: 2026-09-24
payoff: part of the claim record that ends PL-MB2W's generator: one recorded fact decides who holds an item
verify: grep -q 'bin/docket claim' .claude/skills/docket/modes/start.md && grep -q 'Yield: ' subprojects/docket/src/docket/cli.py
recurrences: 2026-09-24 PL-DDYD
---

**Problem.** bin/docket claim and yield write the claim, and start mode is rewritten around them

**Part of `PL-MB2W`'s design** (who holds an item is recorded as a claim; design round of 2026-09-24, in `PL-MB2W` under "Design round, 2026-09-24"). Read that section's spec before starting: this brief names only this item's slice of it.

`claim` fetches, refuses with exit 3, accepts --over with --reason and an ancestor continuation, commits empty with the attribution lines in one paragraph, pushes only when there is no upstream, then fetches and re-reads, and exits 4 when the push fails. Delete start.md:50-78. The handoff line in picking.md gains `claim --over`. `yield <ID>` writes `Yield:`. `claim --over` needs the owner's word or `get_session` showing the holder ARCHIVED or failed, and the reason goes in the claim commit's body.

**Why it matters.** `PL-MB2W` is a live generator: twenty items were each a new shape of work that some reader misread, because who holds an item is inferred from commit subjects, touched paths and ref age. This item is one slice of replacing that inference with a recorded claim, and the generator stops producing members only once the slices through `PL-DDYD` land.

**Done when.**

- `bin/docket claim` and `bin/docket yield` behave as the brief says, with exit codes 3 and 4 tested.
- `start.md` tells a session to run `bin/docket claim` in place of the empty-commit recipe.

**Build order.** After `PL-3FYK`.

**Rider: `PL-SW2K`** (the legacy marker; project owner, 2026-09-24, ratified). Re-point `claims.CUTOVER_MARKER` at a file this item creates, so a commit reads as made before claims were recorded exactly when it predates the `claim` command, and update `test_claims.py`'s legacy test to match. Same pull request; the closing commit leads with both ids.
