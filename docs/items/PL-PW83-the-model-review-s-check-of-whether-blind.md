---
id: PL-PW83
title: The model review's check of whether blind review missed faults counts the items a blind pass filed itself as fixes that did not hold, so reviewed pull requests look worse than they are
status: untriaged
added: 2026-11-11
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

**Options.** Record the filed item's id in the `Blind-review` trailer, and have the review leave those ids out of the re-entry count. Or have the review leave out every re-entry filed before the pull request merged, since a pass runs before the merge. The second needs no new record, but it also drops a fault the authoring session found itself before the merge.

**Recommendation:** the second option, as a change to the skill's step 4 wording alone. It reads two dates the store already holds, and a fault filed before the merge was not missed by review in either case.

**Why it matters.** Step 4 is the one measure of the passes that the authoring session's judgment cannot bias. Read as it stands, it counts against the passes each fault they file instead of fix.
