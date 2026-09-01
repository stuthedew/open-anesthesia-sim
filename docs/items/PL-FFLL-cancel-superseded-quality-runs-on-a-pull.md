---
id: PL-FFLL
title: Cancel superseded quality runs on a pull request instead of running every push to completion
status: untriaged
added: 2026-09-01
---

**Problem.** Cancel superseded quality runs on a pull request instead of running every push to completion

**Why it matters.**

**Where.**

**Done when.**

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

**Why it is not urgent, and the arithmetic.** The saving is CI minutes, not
owner time: nobody waits on a superseded run, and the pull request's checks
list already shows only the head commit's. Roughly (pushes - 1) x 65 seconds
per pull request, so on a three-push branch about two minutes. Worth doing,
worth doing cheaply, and not worth interrupting product work for.

**Considered and rejected as the fix for `PL-D9H6`.** Cancellation was the
other resolution that item named. It was the weaker one for the duplicate,
because a cancelled run still appears in the checks list, so the reader still
sees two entries where they expect one - it changes what the second entry says
rather than removing it. As an addition on top of the trigger scoping it has
none of that problem, because there is no longer a second entry to cancel.

**Done when.** Pushing twice in quick succession to a branch with an open pull
request leaves one completed `checks` run for the newer commit, and a merge to
`main` still runs to completion rather than being cancelled by the next merge.
