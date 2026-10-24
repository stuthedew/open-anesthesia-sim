---
id: PL-R4Y2
title: Simulator defects per product item closed have stayed at about 0.7 to 0.8 a week while apparatus defects fell, and a recorded head explains only 16% of product defects: run the generator question over the open product defects, starting with stale state after a halt
priority: P2
effort: L
status: ready
classes: housekeeping
feature: defect-review-2026-10
touches: docs/items
added: 2026-10-19
payoff: the stale-state defects a learner can see get their root cause fixed once, instead of each one being found and patched separately
verify: grep -qE '^\*\*Re-measured\.' docs/items/PL-R4Y2-*.md
---

**Problem.** Simulator defects per product item closed have stayed at about 0.7 to 0.8 a week while apparatus defects fell, and a recorded head explains only 16% of product defects: run the generator question over the open product defects, starting with stale state after a halt

**How it was measured.** A defect review on 2026-10-19 read `docs/items` with `docket.store.read_items` and placed each item with `Item.lane(workflow_paths)`. A defect is an item whose `classes` include `defect` or `safety`. An organic defect is one filed before any head's `root-cause-of:` named it and carrying no `reenters:`. The scripts lived in the session's scratchpad and are gone, so this paragraph is the method.

**Scope** (project owner, 2026-10-19): every product defect, closed ones included (222 on 2026-10-19), not only the 28 open ones the review recommended. The closed ones carry most of the history of where defects come from.

**Evidence.** Organic workflow defects per workflow pull request fell from about 1.0 a week through 2026-09-20 to 0.41, 0.33, 0.60 and 0.20. Product defects per product item closed show no trend: 0.64, 0.14, 0.69, 0.26, 0.83, 0.79 and 0.77 for the weeks of 2026-08-31 to 10-12. A head explains 35 of 222 product defects (16%), against 44% in the workflow lane and 59% for items that cross lanes. By a keyword count of titles, about 36 of the 91 product defects filed since 2026-09-25 are stale state after a halt, a failed frame or a reset. Only 11 of them are members of `PL-X7D5` (the run screen's single writer) or `PL-5JTH` (dashboard panels restated on a halt). Stale state is a failure the safety-critical standard in `CLAUDE.md` names explicitly. A second cluster is a quantity's range checked by hand (about 15). A third is float extremes such as overflow, subnormal steps and rounding noise (about 10).

**What to do.** Ask every product defect triage's generator question (`.claude/skills/docket/modes/triage.md`): which fact did it misread? Record a head wherever three or more share one, open or closed. Delegate the reading to subagents and keep only their verdicts here. Start with stale state, because `PL-X7D5` and `PL-5JTH` landed only on 2026-10-17 and 2026-10-19.

**Done when.** Every product defect has an answer to the generator question, heads are recorded where they exist, and the product rate is re-measured two weeks after `PL-5JTH`.

**Why it matters.** Product defects are the ones a learner can see, and stale state after a halt is a failure the safety-critical standard names. While no head explains 84% of them, each is found and patched one at a time, and the rate does not fall.

**Generator check.** One-off. This item asks the generator question; it does not misread a fact itself. Record the re-measured rate under a `**Re-measured.**` heading here.
