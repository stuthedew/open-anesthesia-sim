---
id: PL-FSH9
title: No workflow sets timeout-minutes, so one hung job costs 360 minutes - twelve percent of a month's allowance
status: done
feature: ci-cost
touches: .github/workflows/quality.yml, .github/workflows/pr-title.yml, .github/workflows/drift.yml
priority: P3
effort: S
classes: infra
added: 2026-09-05
closed: 2026-09-05
verify: grep -q 'timeout-minutes' .github/workflows/quality.yml && grep -q 'timeout-minutes' .github/workflows/pr-title.yml && grep -q 'timeout-minutes' .github/workflows/drift.yml
---

**Problem.** No workflow sets timeout-minutes, so one hung job costs 360 minutes - twelve percent of a month's allowance

**Why it matters.**

**Where.**

**Done when.**
