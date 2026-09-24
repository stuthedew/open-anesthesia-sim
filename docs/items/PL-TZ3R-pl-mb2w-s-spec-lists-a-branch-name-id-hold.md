---
id: PL-TZ3R
title: PL-MB2W's spec lists a branch-name-id hold under 'Other holds', but no item in the claim-record build carries it, so claims.holdings has no reading for a branch named for its item
status: dropped
feature: claim-record
added: 2026-09-24
closed: 2026-09-24
reason: folded into PL-N162, whose brief, Done-when and touches now carry the branch-name-id hold as a fourth kind of hold in claims.holdings, per PL-MB2W's spec under 'Other holds'. The rewire is the change that would lose the reading, so the hold and the regression it prevents land in one pull request rather than two items racing one file.
---

**Problem.** PL-MB2W's spec lists a branch-name-id hold under 'Other holds', but no item in the claim-record build carries it, so claims.holdings has no reading for a branch named for its item
