---
id: PL-SMN4
title: "A push run on main can be cancelled by a later merge, so a commit lands with no whole-store verify at all: quality.yml's concurrency comment claims every commit on main keeps its own run"
priority: P2
effort: S
status: done
classes: defect, infra
feature: ci-cost
touches: .github/workflows/quality.yml, tests/unit/test_ci_concurrency.py, tools/main_ci_status.py, docs/ARCHITECTURE.md, docket.toml
added: 2026-09-15
closed: 2026-09-16
pr: 615
verify: grep -q 'github.sha' .github/workflows/quality.yml && uv run pytest tests/unit/test_ci_concurrency.py
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

---

**Closed 2026-09-16 with the first candidate shape, and the rate is worse than
either brief above guessed.**

**The count, which neither instance report ran.** Every completed `main` push
run of `quality.yml` from this concurrency block landing on 2026-09-05
(`b4f8626c`, `#357`) to 2026-09-16 01:22 UTC, read from
`/repos/.../actions/workflows/quality.yml/runs?branch=main&event=push&status=completed`:

| runs | cancelled | share |
| --- | --- | --- |
| 257 | 31 | **12.1%** |

Every one of the 31 was alive between 8 and 215 seconds and returned
`total_count: 0` from its `/jobs` endpoint - cancelled while pending, never
having started a job, which is the mechanism this item's first brief inferred
and its second confirmed. They cluster in adjacent pairs and triples (1527/1528,
1543/1544/1545, 1614/1615, 1638/1639, 1666/1667, 1829/1830, 1850/1852,
2041/2042), which is the signature of the single pending slot rather than of
anything a person did.

So the framing to keep is the second brief's rather than the first's. This was
never a freak burst: roughly **one commit in eight on `main` got no whole-store
`bin/docket check --verify` at all**, for eleven days, while the comment above
the block said every commit kept its own run.

**Two further instances, found while closing this.** Runs 2041 (`a0ffc9cc`,
`#612`) and 2042 (`2fed8975`, `#613`) were both evicted in the eight minutes
before this session started - and 2042 is the run for the commit that recorded
the *second* instance in this very item. Four instances now, three of them
inside two hours.

**What shipped.** A per-commit concurrency group for `main` pushes:

```yaml
group: ${{ github.workflow }}-${{ github.ref }}-${{ github.ref == 'refs/heads/main' && github.sha || 'pr' }}
```

No two `main` pushes share a group, so there is no pending slot for a later
merge to take. `pull_request` keeps the shared per-ref lane its cancellation
depends on - `github.sha` is the merge commit there and moves on every push, so
keying that lane on it would cancel nothing and give back the saving `PL-QD9K`
measured at 5 superseded runs in 51.

`cancel-in-progress` is deliberately left conditional rather than flattened to
`true` now that it is unreachable on `main`: editing the new segment away then
degrades to this defect rather than to the worse one of cancelling a `main` run
mid-flight.

**`queue: max` was the other shape, and it is ruled out on a fact rather than a
preference.** GitHub added it in May 2026 (`github.blog/changelog/
2026-05-07-github-actions-concurrency-groups-now-allow-larger-queues`): up to
100 pending runs in FIFO order instead of one, which reaches the same guarantee
by serializing where this reaches it by separating. It cannot be combined with
`cancel-in-progress: true`, and `queue` is a fixed `single | max` enum with no
expression form - unlike `cancel-in-progress` beside it - so it cannot be
scoped to `main` pushes while pull requests keep theirs. Adopting it would
break every pull request's run. Read from SchemaStore's
`github-workflow.json`, fetched directly; `docs.github.com` and `github.blog`
are both blocked by this container's egress proxy, so that is the schema's
declaration rather than GitHub's own prose, and it is the half worth
re-checking if anyone revisits this.

Serializing would also have been the weaker answer here even if it fitted. The
run's product is a verdict about one commit, and several of those computed
concurrently against different tips conflict with nothing - while a queue
delays the last merge of a burst by a full run per commit ahead of it, which is
exactly when `tools/main_ci_status.py` is being read for a red `main`.

**`tests/unit/test_ci_concurrency.py`** renders the group the way GitHub would,
for a `main` push and for a pull request, and asserts the property rather than
the spelling: two `main` shas get different groups, two pushes to one pull
request share one, the flag is off on `main` and on for a pull request, and
`queue` is not `max`. Its expression reader refuses any form it does not model
instead of returning something, so a rewrite fails the test rather than quietly
passing it. Watched failing against the pre-fix block first: `AssertionError:
assert 'quality-refs/heads/main' != 'quality-refs/heads/main'`.

**`tools/main_ci_status.py`'s docstring is corrected, not its behavior.** It
said "The workflow cancels superseded runs, so the newest completed run on
`main` is regularly one that never finished judging anything" - a description
of this defect, presented as normal operation, in the one tool whose silence
was hiding it. It now says what holds after the fix and names the residual:
a cancelled `main` run is no longer routine, still means that commit has no
whole-store verdict, and is still passed over without a word. That is `PL-JTHW`
- a behavior change owing a test, so outside `CLAUDE.md`'s fix-now door.
