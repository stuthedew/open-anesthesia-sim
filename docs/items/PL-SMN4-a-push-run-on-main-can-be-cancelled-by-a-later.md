---
id: PL-SMN4
title: "A push run on main can be cancelled by a later merge, so a commit lands with no whole-store verify at all: quality.yml's concurrency comment claims every commit on main keeps its own run"
priority: P2
effort: S
status: ready
classes: defect, infra
feature: ci-cost
touches: .github/workflows/quality.yml
added: 2026-09-15
verify: grep -qE 'concurrency' .github/workflows/quality.yml && grep -q 'PL-SMN4' .github/workflows/quality.yml
---

**Problem.** `.github/workflows/quality.yml` sets

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}
```

and its comment states the guarantee that buys: "cancelling there would mean a
merge landing while an earlier merge was still being verified silently drops
that commit's only check. Every commit on `main` keeps its own run." **That
guarantee does not hold.**

**Observed 2026-09-15, 22:59 UTC.** Three pull requests merged within thirteen
seconds, and the middle one's run was cancelled:

| run | commit | pull request | created | outcome |
| --- | --- | --- | --- | --- |
| 1999 | `84b23720` | #595 | 22:59:44 | in progress |
| 2000 | `25abc218` | #597 | 22:59:50 | **cancelled** at 22:59:58 |
| 2001 | `17403970` | #598 | 22:59:57 | queued |

Run 2000 was cancelled **one second after run 2001 was created**, on a
`push`-triggered run to `main` where `cancel-in-progress` evaluates to `false`.
Nobody cancelled it by hand in that second.

**The mechanism is an inference, and is labelled as one.** The reading
consistent with the evidence is that a concurrency group holds at most one
*pending* run, so a newer pending run displaces an older pending one
regardless of `cancel-in-progress` — which governs only whether a run already
*in progress* is cancelled. That was not confirmed against GitHub's
documentation: `docs.github.com` is blocked by this container's egress proxy.
Confirm it before designing the fix around it.

**Why it matters.** The whole-store `bin/docket check --verify` runs **only**
on push to `main` — that is `PL-0ZGK`'s finding, and the reason the
session-start digest carries a red-`main` line at all. A cancelled push run is
therefore strictly worse than a failing one: a failing run is surfaced by that
digest line, and a cancelled run is surfaced by nothing. The store check that
runs in exactly one place did not run, and no signal says so.

**Scope it honestly, which narrows it.** `main` is linear and the store checks
assert things about the *current* store, so the next successful push run covers
the state accumulated across the skipped commit. What is genuinely lost is
narrower: that commit's own test run never happened, so a defect introduced and
then removed across the cancelled window is never seen; and the guarantee the
comment states is simply untrue, which is the part that misleads a reader
reasoning about coverage. It is `P2` on the false-guarantee rather than on the
coverage hole.

**Why it is not already captured.** `PL-QD9K`, which shipped this concurrency
block, is `dropped`. `PL-0ZGK`, which put the red-`main` line in the digest, is
`done` and is about the replay being *invisible when it fails* — not about it
never running.

**Done when.** A commit merged to `main` while another `main` run is pending
still gets its own completed quality run, or `quality.yml`'s comment stops
claiming it does and says what actually holds. Either way the comment cites
`PL-SMN4`, which the `verify:` above reads. Candidate shapes, cheapest first:
give `main` pushes a per-commit concurrency group (`${{ github.sha }}`) so no
two ever share one; or accept the queue and add a check that a commit on `main`
carries a completed run.

**Update 2026-09-16: the mechanism is confirmed, and the inference above was
right.** Folded in from `PL-X0ND`, a duplicate capture of this same run,
dropped in the 2026-09-16 triage pass (`PL-0C6W`).

Two pieces of evidence, neither available to the session that wrote the
paragraph above.

**The run never started a job.**
`GET /repos/stuthedew/open-anesthesia-sim/actions/runs/35033624911` returns
`conclusion: cancelled` with `run_started_at` and `updated_at` eight seconds
apart, and `.../runs/35033624911/jobs` returns `total_count: 0`. A run cancelled
with no job ever created was cancelled while *pending*, which is the state this
item's inference named and is not the shape a hand cancellation leaves.

**GitHub's documentation states the rule.** The egress block that stopped the
original confirmation is still in place for `docs.github.com`, but the sentence
is quoted in indexed copies and in GitHub's own community threads: "By default,
any existing pending job or workflow in the same concurrency group will be
canceled and the new queued job or workflow will take its place. By default,
only one job or workflow run can be pending in a concurrency group at a time."

- <https://docs.github.com/actions/writing-workflows/choosing-what-your-workflow-does/control-the-concurrency-of-workflows-and-jobs>
- <https://github.com/orgs/community/discussions/41518> - the same behaviour
  reported as a defect by users, worth reading before assuming this repository
  is misconfigured.

So `cancel-in-progress` governs the in-progress run and nothing else, and the
queue slot behind it holds exactly one run. Runs 1999, 2000 and 2001 all shared
the group `quality-refs/heads/main`: 1999 was *in progress* and protected by
`cancel-in-progress: false`; 2000 was *pending* and protected by nothing; 2001
arrived seven seconds later and took the slot. That also answers the objection
that a concurrency group would have taken the oldest first - 1999 survived
because in-progress and pending runs are governed by different rules, not
because of ordering.

**What this settles for the fix.** The first candidate shape below - a
per-commit concurrency group on `main` pushes - is the one the mechanism
supports, and the obvious-looking alternative of adjusting `cancel-in-progress`
is ruled out: it does not reach the queue at all. Nothing here is a
misconfiguration to correct; the expression evaluates exactly as written, and
what is wrong is that `concurrency` cannot deliver what the comment promises.

**Second instance, 2026-09-16 01:14 UTC - and it took the commit that was
unblocking `main`.** Observed live from the session that caused it (`PL-0C6W`,
the 2026-09-16 triage pass), which is why the timings are to the second.

| run | commit | pull request | created | outcome |
| --- | --- | --- | --- | --- |
| 2036 | `df3b1de` | #610 - *"This unblocks `main`"* | 01:13:38 | **cancelled** at 01:14:14 |
| 2037 | `18bc132` | #611 | 01:14:13 | pending, then ran |

Run 2036 was cancelled **one second after** run 2037 was created, on the
mechanism confirmed above: 2036 was pending in `quality-refs/heads/main`, and
2037 arriving took the single slot. Two merges, thirty-five seconds apart, was
enough - the first instance needed three inside thirteen seconds.

**Three things this changes about the item.**

1. **It is not rare.** Two instances in two hours and fifteen minutes, on an
   ordinary evening's merges. The first brief could reasonably be read as
   describing a freak burst; this one cannot.
2. **It fires hardest exactly when it costs most.** `df3b1de` was the fix for a
   red `main` - `PL-GN8C`'s `verify:` command matching a sentence about another
   book, which had `bin/docket check --verify` failing on the default branch.
   So the one commit whose verdict everybody was waiting for is the one that
   lost it. That is not a coincidence to note and move past: an outage is
   precisely when merges cluster, so the failure's rate is *correlated* with
   the moments its verdict matters. Any threshold analysis of whether to fix
   this has to price that correlation rather than the average rate.
3. **Two merges is the real threshold, not three.** The scope paragraph above
   reasons about a commit lost between an in-progress run and a later merge.
   What actually happened is simpler and more common: one run in progress, one
   pending, one arriving. On a repository where a person merges several
   approved pull requests in a sitting - which is how this one is worked - that
   is the normal shape rather than a burst.

**The recovery is still linear-history luck, and it is worth saying plainly.**
`18bc132` contains `df3b1de`, so run 2037 covers the accumulated store state
and `main`'s tip is verified either way. What is permanently unknown is whether
`df3b1de` *alone* was green. Nothing reports that, which is the reporting half
this item's **Done when.** names as its second candidate shape.
