---
id: PL-K3QM
title: Mark the earlier deliberate sweeps with sweep:, so docket inflow's history rows count their filings apart: only PL-K88Z carries it, and candidates include PL-BNYF's queue audit among the items whose work filed three or more apparatus items
priority: P3
effort: M
status: ready
classes: housekeeping
feature: convergence-visibility
touches: docs/items
added: 2026-11-03
payoff: docket inflow's history rows count the filings of deliberate sweeps apart from ordinary inflow
verify: grep -q '^sweep:' docs/items/PL-BNYF-*.md
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

**Blocked on the generator pause.** Marking the history is apparatus housekeeping, which `CLAUDE.md` holds while a workflow-lane head carries `generator: live`. `PL-J1ZM` is that head on 2026-11-04. The pause lifted on 2026-11-14, when the owner stopped `PL-J1ZM` and its `generator:` became `spent`.

**Why it matters.** Only the last complete week feeds the release-time
predictions, so this changes no verdict. It changes how the history rows read
when the owner looks back over the table.

**Done when.** Each candidate's brief has been read, and each deliberate search among them carries `sweep:`, `PL-BNYF` first.

**Generator check.** One-off: bookkeeping that `PL-CJGH` left for the items closed before `sweep:` existed.
