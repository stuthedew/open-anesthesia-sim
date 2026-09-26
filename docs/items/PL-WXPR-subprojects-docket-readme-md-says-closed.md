---
id: PL-WXPR
title: subprojects/docket/README.md says closed blockers never fire the prose-dependency advisory, since most in-body mentions name landed work - but PL-8YXJ's count refuted that prediction and docket check now advises on a brief still waiting on a closed item
status: untriaged
added: 2026-09-26
---

**Problem.** subprojects/docket/README.md says closed blockers never fire the prose-dependency advisory, since most in-body mentions name landed work - but PL-8YXJ's count refuted that prediction and docket check now advises on a brief still waiting on a closed item

Found closing `PL-YKBF`, 2026-09-26. The sentence is in
`subprojects/docket/README.md`, in the paragraph opening "**`docket check`
raises a grooming advisory for the half of that which is decidable.**": "Closed
blockers never fire, since most in-body mentions name work that has since
landed." For the undeclared-prerequisite advisory alone the first half still
holds - `_undeclared_prerequisites` skips a closed blocker - but the reason is
the prediction `PL-8YXJ` counted and refuted on 2026-09-22 (7 closed-item hits,
5 of them live waits worded as current), and since then `_ended_waits` in
`subprojects/docket/src/docket/checks.py` gives a closed item named that way an
advisory of its own. The same README says so in the paragraph opening "**A
write that moves `status` or `blocked-by` names the passages it leaves saying
the old state.**", so the two passages disagree, and a reader of the first
learns that naming a closed item in a brief is never reported.

**Why it matters.** A reader deciding whether a stale wait in a brief will be
caught reads the passage about the advisory, which says it will not be.

**Done when.** The sentence says what the check does today: a closed item named
as a prerequisite draws the ended-wait advisory rather than the
undeclared-prerequisite one, and why.
