---
id: PL-GTHP
title: Check the 214 findings from PL-TBQS's reviewer replay that name no key defect, most of them marked correct at merge by a blind checker, against main, and file what still holds
priority: P2
effort: L
status: ready
classes: housekeeping
feature: replay-findings
touches: docs/items
added: 2026-10-24
payoff: every defect the reviewer replay found that still holds on main is queued, instead of lost when the pull request's head can no longer be fetched
verify: grep -qE '^Every finding above is checked against main\.$' docs/items/PL-GTHP-*.md
---

**Problem.** Check the 214 findings from PL-TBQS's reviewer replay that name no key defect, most of them marked correct at merge by a blind checker, against main, and file what still holds

**Where the findings are.** The findings are in `replay/PL-TBQS/findings_by_label.json` at commit `b304302ee`, on `PL-TBQS`'s pull request, under blind labels. `replay/PL-TBQS/labels.json` maps each label to its arm, `scores.json` says which findings named a key defect, and `checks.json` holds the checker's verdict on each. The directory is removed before that pull request merges, so read it from that commit. Of the 269 findings, 55 name a key defect. 2 were marked incorrect and 6 not checkable, so most of the 214 others describe a fault that was real at its merge commit. On `PL-TCBJ`'s ten pull requests they overlap `PL-ZWXD`, which holds that replay's own findings beyond its key, so read that item first and check each fault once.
<!-- absent: replay/PL-TBQS/findings_by_label.json -->
<!-- absent: replay/PL-TBQS/labels.json -->
<!-- absent: scores.json -->
<!-- absent: checks.json -->

**Why it matters.** A blind checker confirmed most of these findings as real at their merge commits. Each one that still reproduces on `main` is a defect that no item records. Many of them are in the simulator's interface, and some may be faults the safety-critical standard covers. The findings exist only on a pull request whose branch is deleted, so the longer they wait, the harder they are to reach.

**How to read them now.** `PL-TBQS`'s branch was deleted when #1750 merged, but GitHub keeps the pull request's head. `git fetch origin pull/1750/head:refs/tmp/pr1750` makes commit `b304302ee` readable, and then `git show b304302ee:replay/PL-TBQS/findings_by_label.json` prints the findings (checked 2026-10-24).

**Done when.** Each of the 214 findings has been checked against `main`. Each one that still reproduces is filed, or named as already covered by an open item, and the brief ends with the line `Every finding above is checked against main.`

**Generator check.** Not owed: the item touches only the queue store. It is a review pass that files findings, not a mechanism.
