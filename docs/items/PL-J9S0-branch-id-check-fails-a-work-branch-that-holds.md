---
id: PL-J9S0
title: branch_id_check fails a work branch that holds no claim and a claim that orders behind another live claim, and the first-edit hook says to claim
priority: P2
effort: S
status: blocked
classes: defect
feature: claim-record
touches: tools/branch_id_check.py, tests/unit/test_branch_id_check.py, .claude/hooks/docket-branch-guard.sh
blocked-by: PL-0TD9
deferred-from: v0.6.0 - filed after the freeze by PL-MB2W's design round (2026-09-24), and not safety or science; generator work, which the pause on new mechanisms exists for
added: 2026-09-24
payoff: part of the claim record that ends PL-MB2W's generator: one recorded fact decides who holds an item
---

**Problem.** branch_id_check fails a work branch that holds no claim and a claim that orders behind another live claim, and the first-edit hook says to claim

**Part of `PL-MB2W`'s design** (who holds an item is recorded as a claim; design round of 2026-09-24, in `PL-MB2W` under "Design round, 2026-09-24"). Read that section's spec before starting: this brief names only this item's slice of it.

First verify that CI's fetch-depth 0 holds every head. Fail a non-legacy branch that does work outside the queue and holds no live claim. Fail a claim that orders behind another live claim. Skip legacy commits. The check is per branch, not per id, so captured or triaged ids are never pushed into claims (`PL-3CTW`, `PL-VFJ3`). The first-edit hook adds "this branch claims nothing: `bin/docket claim <id>`" to an edit outside `items_dir`.

**Why it matters.** `PL-MB2W` is a live generator: twenty items were each a new shape of work that some reader misread, because who holds an item is inferred from commit subjects, touched paths and ref age. This item is one slice of replacing that inference with a recorded claim, and the generator stops producing members only once the slices through `PL-DDYD` land.

**Done when.**

- `tools/branch_id_check.py` fails the two cases in the brief and skips legacy commits, with tests.

**Build order.** After `PL-3FYK`.
