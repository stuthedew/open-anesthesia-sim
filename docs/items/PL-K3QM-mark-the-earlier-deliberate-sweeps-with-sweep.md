---
id: PL-K3QM
title: Mark the earlier deliberate sweeps with sweep:, so docket inflow's history rows count their filings apart: only PL-K88Z carries it, and candidates include PL-BNYF's queue audit among the items whose work filed three or more apparatus items
priority: P3
effort: M
status: done
classes: housekeeping
feature: convergence-visibility
touches: docs/items, docs/items/PL-MR85-sort-every-paragraph-of-the-instructions-loaded.md, docs/items/PL-LY24-count-for-each-of-the-13-checks-that-guard-the.md, docs/items/PL-8FT2-review-the-340-regular-expressions-in-tools.md, docs/items/PL-GTHP-check-the-214-findings-from-pl-tbqs-s-reviewer.md, docs/items/PL-ZWXD-check-the-other-correct-reviewer-findings-from.md
added: 2026-11-03
closed: 2026-11-23
pr: 2301
payoff: docket inflow's history rows count the filings of deliberate sweeps apart from ordinary inflow
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

**Checked 2026-11-22** against `d4e8200`: partly done. The 2026-11-14 screen marked `PL-BNYF`, `PL-ZKT8` and `PL-R4Y2` with `sweep:`, and those marks are still in their front matter. What is left is to read the remaining 143 of the 163 candidate briefs in full. `bin/docket inflow` and the `sweep:` field both still exist.

**Every candidate read, 2026-11-23.** The filing map now lists 176 items whose work filed three or more workflow-lane items and that carry neither `root-cause-of:` nor `sweep:`. `bin/docket inflow` credits a sweep with every filing of a commit whose subject leads with the sweep's id, so the filing commit is what decides whether a mark counts the right filings. Each candidate was read in that unit, in three groups.

1. **35 candidates filed three or more items in commits that name them alone.** For each, the title, the brief's opening paragraph and the subject of each filing commit were read. `PL-DH17`, `PL-2D1S` and `PL-5MYR` keep the 2026-11-14 verdicts above. Two are deliberate searches and now carry `sweep:`: `PL-MR85` sorted every paragraph of the instructions loaded at launch and filed the moves the sort called for, and `PL-LY24` counted what the 13 workflow-record checks refused in CI and filed the three defects it found. The other 33 are fixes, builds or decisions. Four of them filed work that a decision called for rather than findings of a search, so `sweep:` would describe them wrongly: `PL-P3GZ` (the split of `docs/MODEL.md`), `PL-KGPR` (the four check removals), `PL-LFJZ` (the work of the chosen done-condition form) and `PL-YRLM` (the v0.7.0 scope). `PL-DZM1` recovered stranded work and captured the defects it met, which is ordinary capture.
2. **115 candidates reach three only through commits that lead with several ids.** 29 such commits filed three or more workflow-lane items. Each was read by its subject and, where the subject left it open, its body. One is a search: `PL-GTHP` and `PL-ZWXD` each checked a reviewer replay's findings against `main` and filed what still held (#1830), and both now carry `sweep:`. The rest are the reader sweep that `PL-R417` already heads, triage and grooming passes, gate batches, milestone scoping, and fixes that captured findings as they went. None is a search that an item of its own ran.
3. **26 candidates reach three only through commits that each filed one or two items.** Their titles and filing commits were read. One is a search: `PL-8FT2` reviewed every regular expression left standing without a reason and filed its findings, and now carries `sweep:`. The rest are fixes and triage passes.

Adding the marks moved two history rows of `bin/docket inflow`: the week of 2026-11-02 now counts 2 filings under `+sweep`, and the week of 2026-11-16 counts 11, leaving 30 ordinary filings and no re-entries. No release verdict changes, because a cut reads only the last complete week and these weeks have been cut.

**What no mark can reach.** Four reviews filed their findings in a commit led by the findings' own ids, with no item of their own: the guard hook review (#1980), the 2026-11-10 root-cause audit (#2090, whose leads `PL-VZ57` now carries), the test-suite review (#2128) and the review of the 2026-11-14 merges (#2160). `PL-40ZB` § "A gap this reading found" records it, and this branch adds the capture step that prevents the next one.
