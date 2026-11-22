---
id: PL-C47M
title: bin/docket inflow should not count a filing as a re-entry when the pull request that added it is the one that closed the item it re-enters, because that filing was a finding made while the fix was built, not a shipped fix that did not hold
priority: P2
effort: M
status: ready
classes: defect
feature: convergence-visibility
touches: subprojects/docket/src/docket/inflow.py, subprojects/docket/src/docket/model.py, subprojects/docket/tests/test_inflow.py, .claude/skills/docket/modes/triage.md
deferred-from: v0.7.0 - present at the freeze, but a queue-count defect in the workflow lane with no connection to anything on the frozen list or in v0.7.0 Required scope; no learner sees it
added: 2026-11-14
payoff: the re-entry count shows only fixes that shipped and then failed, so a fix that held is not mistaken for a generator
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

**Checked 2026-11-22.** `reentry_faults` in `docket.model` still checks only that a `reenters:` item closed on or before the filing's `added:` date, and `docket.inflow` counts every filing that carries `reenters:`. Neither reads which pull request added the filing. The same was true at the freeze (`git show 0947408:subprojects/docket/src/docket/inflow.py`).

**Why it matters.** `docket inflow` is how a session tells whether a fix held. It counts re-entries per week, and names a closed item that three filings re-enter. In the week `PL-BB16` read, 8 of the 11 re-entries filed on their parent's closing day were added by the pull request that closed that parent. So the count reported fixes failing before they had shipped, and a session reading it could treat a fix that held as a generator.

**Recommendation.** Record the pull request that added a filing as a fact, rather than inferring it. Comparing the parent's `pr:` with the filing's pull request still needs that second number, and today only the squash commit's subject shows it, which `.claude/rules/apparatus-standard.md` refuses as a source. Which field and when it is written is the working session's choice. The triage mode's sentence that "every attributed child to date was filed in the commit that closed its parent" describes the case this item excludes, so the work updates it too.

**Done when.** `docket inflow` does not count a filing as a re-entry when the pull request that added it is the one that closed the item it names. A test shows one such filing left out beside a counted filing from a later pull request. The pull request that added a filing is read from a record, not from a commit subject.

**Generator check.** The fact misread is which pull request added an item's file. No head states it. `PL-HMZZ` states which pull request carried an item's work, which `pr:` records, but nothing records the pull request that added a filing. This is a one-off, and that record is its fix.
