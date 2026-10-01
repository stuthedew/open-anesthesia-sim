---
id: PL-C72H
title: required_checks_check.py reads a branch-filtered pull_request trigger as reporting, but GitHub's workflow-syntax page says a run skipped by a branch filter leaves its checks Pending too, so a branches-ignore naming the protected branch, or a branches list leaving it out, would read as agreement while merges hang
status: untriaged
added: 2026-10-01
---

**Problem.** required_checks_check.py reads a branch-filtered pull_request trigger as reporting, but GitHub's workflow-syntax page says a run skipped by a branch filter leaves its checks Pending too, so a branches-ignore naming the protected branch, or a branches list leaving it out, would read as agreement while merges hang
