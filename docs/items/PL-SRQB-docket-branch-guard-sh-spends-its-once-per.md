---
id: PL-SRQB
title: docket-branch-guard.sh spends its once-per-session claim question on a detached HEAD or main, where branch_id_check --hint is silent, so the first edit on a new work branch is never asked
status: untriaged
feature: guard-review-2026-11
added: 2026-11-03
---

**Problem.** docket-branch-guard.sh spends its once-per-session claim question on a detached HEAD or main, where branch_id_check --hint is silent, so the first edit on a new work branch is never asked
