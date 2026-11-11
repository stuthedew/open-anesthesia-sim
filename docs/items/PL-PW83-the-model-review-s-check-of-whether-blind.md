---
id: PL-PW83
title: The model review's check of whether blind review missed faults counts the items a blind pass filed itself as fixes that did not hold, so reviewed pull requests look worse than they are
priority: P3
effort: S
status: done
classes: defect
feature: model-review
milestone: v0.6.18
touches: .claude/skills/model-review/SKILL.md
added: 2026-11-11
closed: 2026-11-11
pr: 2127
payoff: the model review's one unbiased measure of the blind passes stops counting a fault that a pass filed as a fault it missed
verify: grep -q 'filed on the reviewed branch' .claude/skills/model-review/SKILL.md
---

**Problem.** The model review's check of whether blind review missed faults counts the items a blind pass filed itself as fixes that did not hold, so reviewed pull requests look worse than they are

**Where it was found.** A session answering the owner's question "Are the blind review passes providing benefit?" on 2026-11-11 ran step 4 of `.claude/skills/model-review/SKILL.md` § "Check that each blind review pass still finds faults". That step joins the reviewed pull requests' items to the "A fix that did not hold" measure: later items whose `reenters:` names the item, and the item's own live `recurrences:` entries.

**What the count showed.** The comparison took items closed on or after 2026-10-11 by a pull request that owes a pass under today's rule, and counted each re-entry filed within 30 days of the close.

| Group | Items | Pull requests | Item-days followed | Re-entries | Per 100 item-days | Items followed 14 days | Re-entered within 14 days |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Merged before `#1767`, no blind pass | 147 | 73 | 3,659 | 15 | 0.41 | 147 | 9 |
| Merged after it, with a `Blind-review` record | 221 | 112 | 2,642 | 13 | 0.49 | 113 | 6 |

**The defect.** A finding that a blind pass files is a new item, and triage may give it a `reenters:` naming the item under review. The measure then counts it as a fault the review missed, when the review found it. At least 2 of the 13 re-entries in the reviewed group are of that kind: `PL-2T6S` and `PL-TBX9` each name the blind review of the item they re-enter as their finder, and each was filed on the day that item closed. A third, `PL-KG6S`, is a different case and is counted correctly: the passes on a later pull request (`#2022`, `PL-J37P`) filed it against `PL-B6YV`, which `#1927`'s own passes had reviewed two days earlier. No record says which pass filed an item, so the count cannot be corrected from the store. The `Blind-review` trailer records `filed` without the filed item's id.

**A second limit, which no fix removes.** About 6% of items in either group were re-entered within 14 days. Telling 6% from 3% needs about 750 items in each group, at a two-sided 5% significance level and 80% power. So this measure cannot show an effect of the passes for many months, whatever is done about the count.

**Decided 2026-11-11, by the session that fixed it.** The review leaves out each re-entry whose item file reached `main` in the reviewed pull request's own squash commit. Git already records that commit, so no new record is needed. The item as filed offered two other routes, and the count refused both:

- Recording the filed item's id in the `Blind-review` trailer needs a new field, and it leaves the 112 pull requests already reviewed uncorrected.
- Comparing the re-entry's `added:` date with the merge date reads days, and a day cannot order two events on it. Of the 59 `reenters:` filings against items closed on or after 2026-10-11, 21 carry an `added:` date on the day the pull request merged, in UTC. In 14 of those the file reached `main` in the pull request's own squash commit. In the other 7 it reached `main` in a later commit, so the item may have been filed after the merge: `PL-3D2F`, `PL-4S6C`, `PL-H57W`, `PL-JTTD`, `PL-Q80R`, `PL-TLPH` and `PL-YGR6`. A rule on dates would drop those 7 or keep those 14, and either is a miscount.

The rule applies to every group in a comparison, because an authoring session can also file a fault on its own branch. It leaves `PL-KG6S` counted, and leaves out `PL-2T6S` and `PL-TBX9`. Across all lanes, 8 re-entries of items closed by `#1767` or later are left out: `PL-2T6S`, `PL-3PKN`, `PL-501T`, `PL-8W1Q`, `PL-H716`, `PL-MH5T`, `PL-TBX9` and `PL-XX18`. The table above is not recounted here, because its groups hold only pull requests that owe a pass and this session did not rebuild that filter. The next run of the model review recounts it under the new step.

The rule misses one case: a fault found before the merge and filed on another branch. Its file reaches `main` in a later commit, so it stays counted as missed. Nothing in the store or in git separates it from a fault found after the merge.

The "A fix that did not hold" measure itself is unchanged. It is the review's primary outcome for comparing models and effort levels, and whether a fault that a session files on its own branch counts against that session's work is a separate question, which this item does not answer.

**Done when.** Step 4 of `.claude/skills/model-review/SKILL.md` § "Check that each blind review pass still finds faults" tells the review to leave out a re-entry filed on the reviewed branch, gives the command that reads it, and applies the rule to every group compared.

**Why it matters.** Step 4 is the one measure of the passes that the authoring session's judgment cannot bias. Read as it stands, it counts against the passes each fault they file instead of fix.

**Generator check.** A one-off. The fact misread is where a re-entering item was filed: on the reviewed branch, or after its merge. The commit that added the item's file to `main` records it, and step 4 now reads that commit. No head's `misread:` states this fact. Two closed items share the shape and not the fact: `PL-J7YG`, where the rework measure counted citations, and `PL-SW87`, where the red-run measure counted checks that fail by design. Each measure reads a different record, so no one record would have prevented all three.
