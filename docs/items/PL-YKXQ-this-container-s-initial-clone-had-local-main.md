---
id: PL-YKXQ
title: This container's initial clone had local main diverged 407 commits into pre-rewrite history, so a session that checks out main gets a stale tree and an old bin/docket
priority: P2
effort: S
status: dropped
classes: defect, infra
feature: dev-tooling
touches: .claude/hooks/docket-digest.sh, tests/unit/test_docket_digest_hook.py, docs/worker.md
added: 2026-09-06
closed: 2026-09-26
reason: not reproduced in a second fresh container, which is the evidence the 2026-09-19 note named for dropping this rather than building the check. On 2026-09-26 local `main` was created from `origin/main` when the container was provisioned (reflog: `branch: Created from refs/remotes/origin/main`, 03:48 UTC, 80 minutes before the session began) and is a clean ancestor - `git rev-list --count origin/main..main` 0, `main..origin/main` 12 - so it lags by what merges during provisioning and can diverge only if the history of `main` is rewritten inside that window; the one rewrite (`PL-SHG5`) predates both clean containers. The lag is announced where a session would step onto it (`git checkout main` printed `Your branch is behind 'origin/main' by 13 commits, and can be fast-forwarded.`), and no docket read takes the local branch where `origin/main` resolves (`DEFAULT_BRANCHES` in `subprojects/docket/src/docket/vcs.py`). Reopen on a second rewrite of `main`, or on a container where `git rev-list --count origin/main..main` is not 0.
verify: grep -q 'rev-list --count main' .claude/hooks/docket-digest.sh && uv run pytest tests/unit/test_docket_digest_hook.py
---

**Problem.** Measured 2026-09-06 at the end of `PL-6Q8N`, in a session started
that same day. The session began on its harness branch, based correctly on
`origin/main` at `1665199`. After the merge of `#399` it ran `git checkout main`
to sync, and landed on `9a10124 Merge pull request #102` - four hundred
merges out of date. `git merge --ff-only origin/main` refused with "Not
possible to fast-forward", and `git rev-list --count main ^origin/main`
returned **407**: the local `main` ref was not behind `origin/main`, it had
diverged into the history the `git filter-repo` pass and force-push replaced
(`PL-YGF3`, `PL-SHG5`).

`git checkout -B main origin/main` fixed it. Release tags `v0.4.0` through
`v0.4.5` were checked in the same pass and all six already pointed at commits
reachable from `origin/main`, so the tag half of `PL-YGF3` did not recur here -
only the branch ref.

**Why it matters, and it is the second consequence that bites.** The obvious
risk is that the purged publisher-copyright material is reachable again in
every fresh container, which is the thing `PL-SHG5` was cleaning up. That one
is bounded: the container is ephemeral, `origin/main` is clean, and a push only
ever sends what is on the branch.

The unbounded one is that **a session that checks out `main` is working the
wrong tree and is not told so.** This session ran `bin/docket branch` and
`bin/docket stranded` from that checkout and got `invalid choice` for both,
because the `bin/docket` at `9a10124` predates those subcommands. A session
that had not just merged something would read that as the tool being broken,
or worse, would read the *item store* at that commit - four hundred merges of
closures, drops and triage decisions ago - and act on it. Nothing in the
working tree says which `main` you are on.

**Where.** Not in this repository's code. The clone is set up by the harness
before the session starts, so the finding is about the environment and about
what a session should check before trusting `main`.

**Candidate answers, in increasing cost.**

1. **A line in `docs/worker.md`**: never `git checkout main` to sync; use
   `git checkout -B main origin/main`, or stay on the branch and read
   `origin/main` directly. Cheapest, and it is the habit that would have
   avoided this outright.
2. **A check.** `git rev-list --count main ^origin/main` is decidable and cheap;
   a non-zero answer means the local `main` is not a prefix of the remote one.
   It could ride the session-start hook, which already refreshes and prints a
   digest, and is the tier `CLAUDE.md` prefers - deterministic, runs free
   after it is written. The judgment half - what to do about it - stays with
   the reader.
3. Nothing, if this proves to be a one-off artifact of how one container was
   provisioned rather than something reproducible.

**Done when.** Either a session is told, before it trusts `main`, how to check
that its local ref matches the remote one - by prose in `docs/worker.md` or by
a check in the session-start hook - or the finding is reproduced against a
second fresh container and dropped as a one-off with that evidence recorded.

**Triaged `ready` on the hook-check answer, which is the direction the
`verify:` command names.** `CLAUDE.md`'s standing approval for putting the
decidable part in code covers it without a decision round: `git rev-list
--count main ^origin/main` is decidable, cheap, and the digest hook already
runs once per container. The third candidate - do nothing, on the grounds that
this was a one-off provisioning artifact - stays available, and taking it means
rewriting this command before the work rather than after.

**Left standing 2026-09-19 by `PL-4Q9B`** (record clone trust and the permitted ref
operations), which closed with the finding that its ten members are not one
mechanism. This item keeps the cheap session-start check it was already `ready` on. Worth knowing for whoever takes it: the pathology is **not** reproduced in the 2026-09-19 container - `git rev-list --count origin/main..main` returns 0, so local `main` is a clean ancestor rather than diverged. That is one more container, not a disproof, and it is the evidence candidate 3 asked for; a second clean one would justify dropping this instead of building the check. Nothing here is blocked on that head; this item stands on
its own merits at its own band.

**Dropped 2026-09-26, on the second clean container.** Measured at the start of
the session that took this item. `git reflog main` holds one entry, `branch:
Created from refs/remotes/origin/main` at 03:48:07 UTC, and the session's own
branch was cut from a fresh fetch at 05:08:29. So a container is cloned ahead of
its session, and its local `main` is `origin/main` as of that clone - here a
current one, since the tip `49aa759d` merged at 03:45:00 and the next merge,
`9bd852c0`, at 03:51:43. A clone like that falls behind by whatever merges while
it waits, which git states on checkout, and cannot diverge unless the history of
`main` is rewritten during the wait. The 2026-09-06 container's `main` sat at
`9a10124`, "Merge pull request #102", while the remote was merging `#399`: it came
from a copy older than the `PL-SHG5` rewrite, and neither container since has
shown one. The check would guard a condition that needs a second rewrite of
`main` to recur, and `CLAUDE.md`'s gate for new tooling - build where the work
recurs - declines it.
