---
id: PL-V2X5
title: GitHub refuses to arm auto-merge on a pull request that is already green and current ('already in clean status'), and a session merges only by arming, so arming on green under the owner's merge rule and docs/maintainer.md's ask-the-session-to-merge route both leave such a pull request waiting on the owner's click; seen on #1086
status: untriaged
touches: docs/maintainer.md
added: 2026-09-26
---

**Problem.** GitHub refuses to arm auto-merge on a pull request that is already green and current ('already in clean status'), and a session merges only by arming, so arming on green under the owner's merge rule and docs/maintainer.md's ask-the-session-to-merge route both leave such a pull request waiting on the owner's click; seen on #1086

**Evidence, 2026-09-26.** `#1086` (PL-GPJ7 step 2) went green on a head current with `main`, `bin/docket arm` answered `hold` for a read only, and the thread went to arm it on green, as the owner's merge rule has it. `enable_pr_auto_merge` answered: "The pull request is already in clean status (all checks passed). Auto-merge only applies when checks are pending — you can merge directly." `CLAUDE.md` has a session merge only by arming, so the green pull request waited on the owner's **Squash and merge**. The same state defeats `docs/maintainer.md`'s "ask the session that opened the pull request to merge it" whenever the branch is already current, since that route arms and brings the base in, and there is no base to bring.

**What arming while CI is pending would change.** A session that arms at its last push, rather than on green, never meets the clean state; a thread told to arm on green arms into the refusal. Which of those the owner's rule means, and whether `docs/maintainer.md` should say a current, green pull request is his to merge, is the triage question.
