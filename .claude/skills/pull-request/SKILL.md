---
name: pull-request
description: Open, arm, update and merge this repository's pull requests, and act on their CI. Use it when approved work is finished and green and its pull request should open; at a branch's first push; before arming auto-merge, and before each later push while a pull request is open; when a pull request is behind main; when a check fails on a pull request; and after creating or updating a pull request's title or body.
---

# pull-request

This skill holds the pull request procedure that `CLAUDE.md` loaded in every
session until `PL-S2NL` moved it here on 2026-10-24. A session needs it only at
a push or a pull request. So `CLAUDE.md` keeps one sentence that names those
moments, and two hooks point here when they arrive:
`.claude/hooks/push-check-guard.sh` after a push of this repository, and
`.claude/hooks/pr-body-email-guard.sh` after a pull request is created or
updated. `PL-SN2Z` measured why both carriers are kept. A skill named by a
resident sentence started on every test request that named its moment, but
nothing measured a moment that arrives in the middle of a task, as a push does.

## Open the pull request with the work

**Once the owner has approved a piece of work, the pull request opens as soon
as that work is finished and its checks are green** (project owner,
2026-08-31). Do not ask first, because the approval *was* the invitation.

Where the **web harness says not to open one unless the owner explicitly
asks**, this rule is that ask, standing rather than per pull request, so a
session reading both proceeds rather than stalls. A session-level
auto-pull-request switch set *off* is that same case and not a third: it stops
the harness opening one unasked and does not withdraw this ask (project owner,
2026-09-19, ratified, over treating the switch as a withdrawal and asking per
pull request while it is off).

**A branch carrying only item files opens its pull request at its first push
and arms auto-merge**, so a capture reaches `main` even when its session ends
before any work does (project owner, 2026-09-23, ratified, over "a branch
carrying only captured items is not a pull request", `PL-WNCT`).
`.github/workflows/update-armed.yml` brings `main` in if `main` moves past it
first (`PL-S5MF`). Where a claim rides that first push, open the pull request as
a draft, as `.claude/skills/docket/modes/start.md` explains.

## Ask `bin/docket arm` before arming and before every later push

**Whether a pull request arms is `bin/docket arm`'s answer, asked before
arming and before every later push while a pull request is open.** **The owner
reads only a real decision or a high-risk change, and housekeeping merges on
green** (project owner, 2026-10-17, `PL-DKBG`). Which one a change is stays
your call. Record it as an `Owner-read:` trailer, whose form and test `arm`
prints. Workflow items need no merge confirmation (project owner, 2026-10-12,
`PL-KPM2`). `arm` gives one of three answers:

- **`arm`**: mark the pull request ready and arm auto-merge. Name in the report
  each path outside the store that it armed.
- **`hold`**: leave it unarmed. `arm` holds for a claim, for a simulator change
  that no `Owner-read:` record covers, for a record saying `needed`, and for an
  edit to a test that pins `arm`'s answers. Disarm the pull request before the
  push that brings the hold, or green CI merges half the work. While the hold
  is a claim, keep the pull request a draft. Once no claim holds it, record the
  judgment or ask the owner, as `arm` says. A pull request held for the owner
  merges on their word alone.
- **`behind N`**: bring `origin/main` in and ask again.

`subprojects/docket/src/docket/arming.py` carries the rules and the decisions
behind them (`PL-QP9Z`, `PL-1MCK`, `PL-KWCY`, `PL-3FYK`, `PL-H14W`).

## Bring `origin/main` in once

**Bring `origin/main` into an open pull request once, when it is armed or being
merged and `behind` is all that stops it; again only if another merge lands
first.** `main` refuses a branch that is not up to date (project owner,
2026-09-23, ratified, over a merge queue, which a user-owned repository cannot
have). Each base merge re-runs `quality.yml`, so a merge taken while the pull
request waits on review is stale by its merge and paid again. A pull request
that is behind while it waits on review is neither red nor conflicted, and is
not work.

At merge time the owner's *Update branch* brings `main` in
(`docs/maintainer.md`). An armed pull request is brought up to date by
`.github/workflows/update-armed.yml` on each push to `main` (`PL-S5MF`), since
auto-merge never updates a branch. The refusal binds an admin too. A session's
GitHub calls are the owner's, so a session squash-merges a pull request that
GitHub will not arm because it is already green and current (project owner,
2026-10-03, ratified, over the owner's click, `PL-NXRJ`).

Bring `main` in sooner only on a genuine conflict, on a notice that `main` is
green again, or before editing work the session will push anyway, as
`bin/docket branch` prints (`PL-6MW8`, revising `PL-WC72`).

## When a check fails

**`main` red for a reason outside the item stops the session.** Say so to the
owner before any retry, and wait (project owner, 2026-09-25, ratified, in the
Projects trial's instructions, `PL-NZC0`).

**A check that fails again on the same pull request stops it too, unless the
session reproduced the new failure and found a cause no earlier failure of
that check there had.** Then it fixes that cause and carries on. A repeated
cause, a failure it cannot explain, or a need for a stronger model stops it.
The reply then says what failed, why, and what it wants, and asks nothing where
nothing needs weighing.

**Four failed runs of one check on one pull request stop it whatever the
causes.** That reply says the check failed four times and names each cause. It
asks the owner a real question with options and a recommendation, such as a
retry on a stronger model, a narrower or split change, or setting the item
aside, and never only whether to try again (project owner, 2026-10-19,
ratified, over a stop at every second failure; the question at four is the
owner's own, `PL-M44T`).

## Read the published body back

**After creating or updating a pull request, read the published title and body
back and compare them with what was sent.** The server rewrites bodies silently
and still returns success. An angle-bracket placeholder such as `<id>` is taken
for an HTML tag and vanishes, in a code span or not (`PL-1DN9`). An update also
strips a `_Generated by_` footer and puts none back, so end an updated body
with the `🤖 Generated with` lines (`PL-N2DN`).
