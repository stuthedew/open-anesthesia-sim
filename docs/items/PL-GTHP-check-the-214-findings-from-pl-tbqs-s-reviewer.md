---
id: PL-GTHP
title: Check the 214 findings from PL-TBQS's reviewer replay that name no key defect, most of them marked correct at merge by a blind checker, against main, and file what still holds
status: untriaged
feature: replay-findings
added: 2026-10-24
---

**Problem.** Check the 214 findings from PL-TBQS's reviewer replay that name no key defect, most of them marked correct at merge by a blind checker, against main, and file what still holds

**Where the findings are.** The findings are in `replay/PL-TBQS/findings_by_label.json` at commit `b304302ee`, on `PL-TBQS`'s pull request, under blind labels. `replay/PL-TBQS/labels.json` maps each label to its arm, `scores.json` says which findings named a key defect, and `checks.json` holds the checker's verdict on each. The directory is removed before that pull request merges, so read it from that commit. Of the 269 findings, 55 name a key defect. 2 were marked incorrect and 6 not checkable, so most of the 214 others describe a fault that was real at its merge commit. On `PL-TCBJ`'s ten pull requests they overlap `PL-ZWXD`, which holds that replay's own findings beyond its key, so read that item first and check each fault once.
