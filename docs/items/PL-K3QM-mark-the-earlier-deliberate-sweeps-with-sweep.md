---
id: PL-K3QM
title: Mark the earlier deliberate sweeps with sweep:, so docket inflow's history rows count their filings apart: only PL-K88Z carries it, and candidates include PL-BNYF's queue audit among the items whose work filed three or more apparatus items
status: untriaged
feature: convergence-visibility
added: 2026-11-03
---

**Problem.** Mark the earlier deliberate sweeps with sweep:, so docket inflow's history rows count their filings apart: only PL-K88Z carries it, and candidates include PL-BNYF's queue audit among the items whose work filed three or more apparatus items

**How to find the candidates.** Found while building `PL-CJGH`. Map each item
to the items whose work filed it with `docket.vcs.filing_parents(root, "HEAD",
"docs/items")`, and list the parents that filed three or more apparatus items
and carry no `root-cause-of:`. On 2026-11-03 that list held about 80 items. Most
are fixes that captured findings as they went, which is ordinary inflow. Few are
sweeps: `PL-BNYF` (an audit of the queue against the area model) is the clearest
one besides `PL-K88Z`. Whether an item was a deliberate search is a judgment on
its brief, so each needs reading.

**Why it matters.** Only the last complete week feeds the release-time
predictions, so this changes no verdict. It changes how the history rows read
when the owner looks back over the table.
