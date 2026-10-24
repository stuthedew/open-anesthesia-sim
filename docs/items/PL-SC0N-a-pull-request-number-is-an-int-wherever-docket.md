---
id: PL-SC0N
title: A pull request number is an int wherever docket and tools hold one, so a number parsed by hand reaches NewestPullRequest, SubjectPullRequest, Remote.frozen or pr_body_check.recovered unrefused; a PullRequestNumber type that only model.pr_number produces would make mypy refuse it (found building PL-N4FP)
status: untriaged
feature: one-source-of-truth
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/, tools/
added: 2026-10-24
---

**Problem.** A pull request number is an int wherever docket and tools hold one, so a number parsed by hand reaches NewestPullRequest, SubjectPullRequest, Remote.frozen or pr_body_check.recovered unrefused; a PullRequestNumber type that only model.pr_number produces would make mypy refuse it (found building PL-N4FP)
