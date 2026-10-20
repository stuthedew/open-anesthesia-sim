---
id: PL-9CS6
title: Cut v0.6.0 from the 64 items finished since v0.5.42
status: done
resource: release-train
added: 2026-10-20
closed: 2026-10-20
pr: 1700
verify: grep -q '^## Current baseline: v0.6.0' ROADMAP.md
---

**Problem.** Cut v0.6.0 from the 64 items finished since v0.5.42

**Fixed in place during the cut** (2026-10-20). The real-tree gate test,
`test_this_repository_records_a_disposition_for_every_open_debt_item`, asserted
that a gate is always current. Shipping v0.6.0 with v0.7.0 not yet scoped leaves
no section ahead of the baseline recording a frozen list, so CI failed on a
correct roadmap. The test now requires the baseline's release train and accepts
a missing gate only where that train records none.
