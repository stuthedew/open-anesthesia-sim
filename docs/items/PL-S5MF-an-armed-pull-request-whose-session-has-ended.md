---
id: PL-S5MF
title: An armed pull request whose session has ended stalls at behind: main now requires branches to be up to date and GitHub's auto-merge never updates one, so PL-WNCT's promise that a capture reaches main after its session ends no longer holds
priority: P2
effort: S
status: needs-decision
classes: infra, docs
touches: subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed at capture by PL-6MW8's session, 2026-09-23
added: 2026-09-23
payoff: a capture whose session has ended reaches main even when main moved during its one CI run
---

**Problem.** An armed pull request whose session has ended stalls at behind: main now requires branches to be up to date and GitHub's auto-merge never updates one, so PL-WNCT's promise that a capture reaches main after its session ends no longer holds

**Found 2026-09-23 while working `PL-6MW8`** (the `CLAUDE.md` half of adopting
strict up-to-date checks). With "Require branches to be up to date before
merging" on, a pull request merges only once its branch contains `main`'s tip.
GitHub's auto-merge never brings the base in. It "merges a pull request
automatically after all required reviews and status checks pass" (GitHub Docs,
*Automatically merging a pull request*), and the strict row of *About protected
branches* puts the update on the author: "you'll need to bring the head branch
up to date after other collaborators update the target branch". The merge
queue is the feature that removes that step. It is available only "in any
public repository owned by an organization" (*Managing a merge queue*), and
this repository is owned by a user account. No page says in so many words that
auto-merge does not update a branch. The reading rests on those pages and on
third-party actions that exist only to do the update (`tibdex/auto-update`,
`adRise/update-pr-branch`). Confidence is medium-high rather than certain.

So a captures-only pull request, armed at its first push under `PL-WNCT`,
merges by itself only if `main` stays still for its one CI run, which took
142-300 s on 2026-09-23. Otherwise it waits at `behind`. `CLAUDE.md` now puts
the update on the session that armed it. A pull request whose session has
ended waits until somebody notices.

**Why it matters.** `PL-WNCT` drained 21 items, and its `generator:` reads
"spent" on the premise that "a captures-only session no longer ends holding its
captures by rule". Under strict checks that holds only while `main` stays still
for one CI run. 50 commits reached `main` on 2026-09-23 by 20:40 UTC, in bursts
several minutes apart, so the window is missed most often in the hours when
most sessions are running. The stall is visible rather than silent. The digest's
"Filed on a branch, not yet on origin/main" line and `bin/docket stranded` both
name the item. What is missing is who acts on it, and the one call that does.

**Decision needed.** How a captures-only pull request that falls behind reaches
`main` once its session has ended:

1. **Name it where every session already looks.** `bin/docket flight` already
   reads a branch's open pull request from `refs/pull/*`. Whether that branch
   is behind `origin/main` can be read offline, and a captures-only branch is
   armed by rule. So its line could say "pull request #N is behind main and will
   not merge until the base is brought in", and give the call
   (`update_pull_request_branch`). Every session's digest would then carry the
   fix. It needs no credential and no new CI. It still waits for some session
   to start and act. It changes docket's output, so the generator pause holds
   it.
2. **A workflow on push to `main` that updates the newest armed, green, behind
   pull request**, the `adRise/update-pr-branch` pattern. This one is fully
   unattended. It needs a new workflow, and a fine-grained personal access
   token or App token stored as a repository secret. An update made with
   `GITHUB_TOKEN` creates its `pull_request` runs "in an approval-required
   state" (GitHub Docs, *Triggering a workflow*), so the required checks would
   never pass on their own. The owner creates and rotates the token.
3. **Accept it.** The owner clicks *Update branch* on any pull request they
   find behind (`docs/maintainer.md`). Captures are small, and a stalled one is
   named in every digest.

**Recommended: 1.** It is the half that can be decided from the repository,
placed in the report every session already reads. It needs no secret, and it
keeps `docket`'s rule that it prints and does not act. Take 2 only if the new
line is seen being skipped. The generator pause holds either one until the
pause lifts or the owner names this item.

**Done when.** The chosen route is in place, or "accept it" is recorded with
its reason, and a captures-only pull request that falls behind after its
session ends either reaches `main` or is named with its one-call fix in the
digest.

**Generator check.** Not a generator: it has no members yet. It is the one way
back into `PL-WNCT`'s drained mechanism. So count against this item any
stranded-capture recovery filed after 2026-09-23 whose branch had an armed
pull request open.
