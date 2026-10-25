---
id: PL-SC0N
title: A pull request number is an int wherever docket and tools hold one, so a number parsed by hand reaches NewestPullRequest, SubjectPullRequest, Remote.frozen or pr_body_check.recovered unrefused; a PullRequestNumber type that only model.pr_number produces would make mypy refuse it (found building PL-N4FP)
priority: P3
effort: M
status: done
classes: refactor
feature: one-source-of-truth
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/, tools/
added: 2026-10-24
closed: 2026-10-25
pr: 1769
payoff: a hand-parsed number can no longer reach a pull request reader, because mypy refuses any int that model.pr_number did not build
verify: grep -qF 'PullRequestNumber' subprojects/docket/src/docket/model.py
---

**Problem.** A pull request number is an int wherever docket and tools hold one, so a number parsed by hand reaches NewestPullRequest, SubjectPullRequest, Remote.frozen or pr_body_check.recovered unrefused; a PullRequestNumber type that only model.pr_number produces would make mypy refuse it (found building PL-N4FP)

**Why it matters.** `PL-N4FP` made `tools/fact_home_check.py` refuse a hand-written reading of the `pr` field. It cannot recognise digits that only their source shows to be a pull request number. So a number parsed some other way can still reach `vcs.NewestPullRequest`, `vcs.SubjectPullRequest`, `Remote.frozen` or `pr_body_check.recovered`, because each takes a plain `int`. If a type that only `model.pr_number` can build were the only thing those signatures accept, mypy would refuse that path. This is the "parse, don't validate" pattern in `.claude/rules/expert-review.md`, applied to the apparatus.

**Done when.** `docket.model` defines `PullRequestNumber`, and only `model.pr_number` and the forge readers in `docket.vcs` construct it. The four holders named above take it instead of `int`, and `mypy` passes.

**Generator check.** One-off. The type is the structural follow-up that `CLAUDE.md` asks for after fixing a second copy ("make the next copy fail through a checked type"). No reader has misread the fact again since `PL-N4FP`.
