---
id: PL-C47M
title: bin/docket inflow should not count a filing as a re-entry when the pull request that added it is the one that closed the item it re-enters, because that filing was a finding made while the fix was built, not a shipped fix that did not hold
status: untriaged
feature: convergence-visibility
added: 2026-11-14
---

**Problem.** bin/docket inflow should not count a filing as a re-entry when the pull request that added it is the one that closed the item it re-enters, because that filing was a finding made while the fix was built, not a shipped fix that did not hold

**Evidence.** `PL-BB16` read the 11 filings from 2026-10-19 to 10-25 whose
`reenters:` item closed on the day they were filed. Eight were added by the same
squash-merged pull request that closed the item they re-enter, so they were known
before that fix shipped and cannot show that it failed. `PL-04KR` defines a
re-entry as a shipped fix that did not hold, and its own baseline found that
filings made in the closing commit record work found while building, not a
failure. `reentry_faults` in `docket.model` accepts them, because it requires
only that the named item closed on or before the filing's `added:` date.

**What to decide.** No item records the pull request that added it, so the
change needs that fact from a record rather than from a commit subject: either
the parent's `pr:` compared with the pull request that added the filing, or a
field written when the filing is triaged.
