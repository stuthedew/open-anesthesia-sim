---
id: PL-FFLL
title: Cancel superseded quality runs on a pull request instead of running every push to completion
priority: P3
effort: S
status: ready
classes: infra
feature: dev-tooling
touches: .github/workflows/quality.yml
added: 2026-09-01
verify: grep -q '^concurrency:' .github/workflows/quality.yml && grep -q 'cancel-in-progress' .github/workflows/quality.yml
---

**Problem.** `PL-D9H6` (the doubled `quality.yml` run) removed the *duplicate*
run per commit. It did not address the *superseded* run per pull request: this
project's sessions commit and push as they go, so a branch commonly receives
several pushes while one pull request is open, and each one starts a full
~65-second `checks` run that nobody will read once the next push lands.

**Where.** `.github/workflows/quality.yml`, a new top-level `concurrency:` key.
The standard shape, guarded so a run on the default branch is never cancelled
mid-way and left ambiguous:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}
```

`PL-D9H6` scoped `push` to `main`, so a branch is now seen only through
`pull_request` and `github.ref` is that pull request's merge ref. The group is
therefore unambiguous, and the push-versus-pull-request ref mismatch that would
have made this fiddly before that change no longer arises.

**Why it matters.** It is worth doing and not worth interrupting anything for,
and the arithmetic is why. The saving is CI minutes rather than owner time:
nobody waits on a superseded run, and the pull request's checks list already
shows only the head commit's. Roughly (pushes - 1) x 65 seconds per pull
request, so on a three-push branch about two minutes.

**Considered and rejected as the fix for `PL-D9H6`.** Cancellation was the
other resolution that item named. It was the weaker one for the duplicate,
because a cancelled run still appears in the checks list, so the reader still
sees two entries where they expect one - it changes what the second entry says
rather than removing it. As an addition on top of the trigger scoping it has
none of that problem, because there is no longer a second entry to cancel.

**Done when.** Pushing twice in quick succession to a branch with an open pull
request leaves one completed `checks` run for the newer commit, and a merge to
`main` still runs to completion rather than being cancelled by the next merge.

**Triaged 2026-09-01.** P3, `infra`, `dev-tooling`. The band follows the item's
own arithmetic: the saving is CI minutes rather than owner time, and nobody
waits on a superseded run. `infra` alone rather than `perf` - the cost is the
runner's, not the product's, so it is process work and `perf` would put it in
the debt gate for a saving nothing measures.

**Its `verify:` was run before being written down**, and fails today (exit 1,
no `concurrency:` key in the workflow). Both halves are needed: the first
proves the key exists, the second that it carries the cancellation, so neither
passes on a `concurrency:` block that names a group and cancels nothing.
