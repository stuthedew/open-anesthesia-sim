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
