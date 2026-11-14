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
verify: grep -q '^\*\*Every candidate read, ' docs/items/PL-K3QM-*.md
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

**Done, 2026-11-14.** The filing map listed 163 items whose work filed three or more workflow-lane items and that carry no `root-cause-of:`. Each was screened in three ways: by its title, by a search of its brief for words such as audit, inventory, survey and sweep, and by the subject of each commit that filed its findings. About twenty briefs were then read in full. Three items now carry `sweep:`, beside `PL-K88Z`:

1. `PL-BNYF` audited the open queue and `ROADMAP.md` against the area and workspace layout model, and its commit filed 14 items.
2. `PL-ZKT8` ran the prompt audit over the resident instructions and the docket skill, and filed the four contradictions it found.
3. `PL-R4Y2` asked the generator question of every product defect, and recorded each shared cause it found as a root-cause item.

Most of the other candidates are ordinary fixes that captured findings as they went. Many reach three filings only because one commit closed several items at once, and the filing map credits every id in that subject with each capture the commit made. These close calls stay unmarked:

1. `PL-DH17` leads the commit that filed the eleven findings of the 2026-11-10 root-cause audit (#2090). Its own work was the copy edit of replies, and it was dropped as moot, so `sweep:` would describe it wrongly. The audit has no item of its own to mark.
2. `PL-J503`, `PL-CFWP` and `PL-3DD9` lead the commit that filed 40 findings of a reader sweep. That sweep was `PL-R417`'s, which carries `root-cause-of:`, and `docket inflow` already counts a head's filings apart.
3. `PL-2D1S` traced one cause, the rise in red CI runs, rather than searching a surface.
4. `PL-CMCB` audited the ten `type: ignore` directives, but only one of its three filings came from that audit.
5. `PL-5MYR` was found by a sweep, but its own work was a fix.

**Left open, 2026-11-14.** The done-when asks for each candidate's brief to be
read. The screen above read about 20 of 163 in full, so the item stays ready
for the remaining 143. The three marks stand.
The `verify:` command now looks for a paragraph opening "**Every candidate
read, DATE.**", which the session that reads the remaining briefs writes. The
old command passed as soon as `PL-BNYF` was marked.
