---
id: PL-WC72
title: CI re-runs in full on every main merge while a pull request waits for approval, discarding a green result each time
priority: P3
effort: S
status: done
classes: infra
feature: ci-cost
milestone: v0.4.4
touches: CLAUDE.md
added: 2026-09-05
closed: 2026-09-06
pr: 373
verify: python3 tools/doc_check.py check && grep -qF 'into an open pull request out of habit' CLAUDE.md
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

---

**Decided 2026-09-06 by the project owner: route (b).** Sessions stop merging
`origin/main` into an open pull request out of habit; the two cases that keep
it are a branch genuinely conflicted against its base, and a base-recovery
notice saying the base is green again. Recorded as a resident bullet in
`CLAUDE.md`, immediately after "Commit and push as you go".

**Why resident rather than a check**, against `CLAUDE.md`'s four dispositions.
The decidable half looks available — `git merge-tree` can say whether a merge
was needed — but it is not: the base-recovery case is a fact about a *past* CI
result on the base, which no read of the tree recovers, so a check would fire
on the legitimate merges too. Worse, it could only fire on or after the push
that already spent the run, which makes it a check that costs attention without
changing a decision — the defect `CLAUDE.md` says to retire a check for, not to
build one as. A pre-push hook fires early enough but is scripting exactly the
judgment it must not. A `paths:` rule cannot carry it either: `git merge origin/main`
is preceded by no read, which is the case that section names as the one
path-scoping cannot serve. That leaves resident, which is where it went.

**The measurement named above was not taken, deliberately.** It existed to
decide whether the cost justified a change; route (b) removes runs at no cost
to what CI proves, so the answer does not depend on the number. If a later
session wants it: how many completed `pull_request` runs in a window had a
base-merge as their head commit and were not superseded.

**One caveat this rests on.** If branch protection later requires branches to
be up to date before merging, the first exception widens to "whenever the base
has moved" and most of the saving goes with it. That setting is off today, on
the evidence that pull requests here merge minutes apart without an intervening
base merge each time — but it lives off-tree where nothing can read it, which
is the same blind spot `PL-KPP1` records.

**Not addressed here, and deliberately out of scope.** Route (c) — narrowing
what `quality.yml` runs on such a push — stays unbuilt. It trades away the
guarantee that the merge-result run catches a semantic conflict between two
green branches, and route (b) makes the push it would optimize rare.
