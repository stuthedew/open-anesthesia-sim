---
id: PL-WC72
title: CI re-runs in full on every main merge while a pull request waits for approval, discarding a green result each time
priority: P3
effort: S
status: needs-decision
classes: infra
feature: ci-cost
touches: .github/workflows/quality.yml
added: 2026-09-05
---

**Problem.** An open pull request that has already gone green re-runs the whole
of `quality.yml` — sync, ruff, mypy, the full suite, docket, doc_check,
contrast — every time its branch takes `origin/main` in, and sessions take
`origin/main` in routinely while waiting for approval.

**The mechanism, checked rather than assumed** (triage, 2026-09-06). It is not
GitHub re-evaluating the merge ref when the base moves; that fires no event and
no run. It is the branch-side merge. `quality.yml` triggers on `pull_request`,
whose default types include `synchronize`, and a merge commit pushed to the
head branch is a `synchronize` like any other push. Worked instance: commit
`813134e`, "Merge remote-tracking branch 'origin/main' into
claude/github-process-optimization-5rkrv8", parents `16947f7` and `a891e7f`,
fired quality run 1370 at 2026-09-05T23:49:43Z — a full run whose only new
content was `main`, which `main`'s own run 1368 had already tested green four
minutes earlier.

So the title's "on every main merge" is right about the trigger and wrong about
the direction: it is every merge *into* the branch, not every merge *to* main.

**Why it matters, and why it is smaller than it looks.** Two things already
absorb part of it. The repository is public, so standard runners are free and
the cost is the runner slot rather than the minute — `quality.yml`'s own
concurrency comment makes that argument. And `cancel-in-progress` is `true` off
`main`, so a base-merge run followed quickly by another push is cancelled
rather than completed; run 1370 above was in fact cancelled 107 seconds later
by the next push. What is left is the base-merge that is *not* quickly followed
by another push — the branch that merges `main` in and then sits waiting for
approval, which is precisely the case in the title.

**How much that actually costs is unmeasured**, and measuring it is the first
half of this decision rather than something to assert: the number wanted is how
many completed `pull_request` runs in a window had a base-merge as their head
commit and were not superseded. Twenty of the twenty-five most recent runs at
the time of triage were `pull_request` runs across five concurrent branches, so
the population is not small, but the fraction is not known.

**Decision needed.** Which of the three routes below to take — accept the
re-runs, merge `origin/main` into open branches less often, or make
`quality.yml` cheaper on a base-merge push — and whether to measure the
frequency first. They land in different files, which is why this is
`needs-decision` rather than `ready`: the declared `touches` above is the
capture's guess and only route (c) makes it true.

- **(a) Accept it.** Runners are free, `cancel-in-progress` covers the noisy
  half, and the run that fires is the one that tests the merge result — which
  is the question a reviewer is actually asking.
- **(b) Merge `main` in less often.** The apparatus, not the workflow: sessions
  currently merge `origin/main` on conflict, on a base-recovery notice, and
  otherwise out of habit. Narrowing that to the first two removes most of these
  runs at zero risk to what CI proves. Touches `CLAUDE.md` or
  `.claude/rules/`, not `.github/`.
- **(c) Make the workflow cheaper on such a push.** Cheapest to state and the
  riskiest of the three: a merge that brings in only `main` still changes what
  the branch means, and a semantic conflict between two green branches is
  exactly what the merge-result run exists to catch. Skipping or narrowing it
  trades away the guarantee rather than the cost.

**Recommendation to weigh, not a decision taken:** (b), because it is the only
one that removes runs without removing a guarantee, and (a) as the fallback if
the measurement above comes back small.

**Where.** `.github/workflows/quality.yml`'s `on:` and `concurrency:` blocks
under route (c); `CLAUDE.md`'s drive-to-green rules under route (b).

**Done when.** The route is chosen and recorded — including "accept it", which
closes this item with a `reason` rather than a change — and if a change follows,
the measurement above is what justifies it.
