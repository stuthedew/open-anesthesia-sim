---
id: PL-Z0SM
title: Merge skew has turned main red twice - #476 and #477 (PL-33WM), then #930 and #933 on 2026-09-23 - because parallel sessions merge minutes apart on pull requests whose CI ran on a base without the other, so no pull request ever shows the red
priority: P3
effort: S
status: done
classes: infra
touches: CLAUDE.md, ROADMAP.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-23 triage pass
added: 2026-09-23
closed: 2026-09-23
verify: grep -qF '**Answered 2026-09-23: hold**' docs/items/PL-Z0SM-*.md
---

**Problem.** Merge skew has turned main red twice - #476 and #477 (PL-33WM), then #930 and #933 on 2026-09-23 - because parallel sessions merge minutes apart on pull requests whose CI ran on a base without the other, so no pull request ever shows the red

**Found 2026-09-23 while diagnosing `PL-KH3Q`.** The first instance is
`PL-33WM` (#476 added a presence check on a base #477's CI never saw); the
second is `PL-KH3Q` (#930 and #933, nine minutes apart). Two in about 460
pull requests, both while several sessions were merging within the hour.
The remedies this class has - a merge queue, or requiring a branch to be up to
date before it merges - are new workflow mechanisms, so the `PL-6Q9L` pause
holds them, and any of them has to answer `PL-J786` (dropped: a green `checks`
run before any merge) and `PL-WC72` (CI cost of re-running on every base move).
Captured for the count, not proposed: what would change the answer is the
instance rate once the pause lifts.

**Why it matters.** Each instance turns `main` red for every open pull request
at once, and the drive-to-green rules then have each session port the same fix:
after `#930` and `#933`, four branches ported one test fix, and `PL-GHHW` is the
stranded-work confusion that followed. No pull request ever shows the red, so
nothing before the merge can catch it.

**Done when.** The answer is recorded under the question, dated and with its
kind; then either the chosen remedy is in place, or the hold stands with its
trigger stated here and the item closes as held.

**Decision needed.** The `PL-6Q9L` pause that held this capture has ended - no
open item carries `generator: live` - so the question it deferred is live: adopt
a remedy for merge skew, or hold at two instances?

- **Require branches to be up to date before merging** (branch protection's
  strict status checks). Closes the class, at a `quality.yml` run per open pull
  request each time `main` moves - the cost `PL-WC72` exists to avoid - and it
  reverses `CLAUDE.md`'s rule against bringing the base into an open pull
  request out of habit.
- **A merge queue.** The same guarantee with the re-runs batched. Whether GitHub
  offers one to a user-owned repository was not checked in this pass; check
  before choosing it.
- **Hold.** Settings unchanged; `bin/docket new`'s recurrence matching counts
  the next instance onto this item.

**Recommended: hold, with the number that would change it named now.** Two
instances in about 460 pull requests is 0.4%, and each was repaired by one
follow-up pull request (`PL-33WM`, `PL-KH3Q`), while strict checks cost a full
run on every open pull request at every merge. Adopt strict checks at a third
instance within 30 days of the last (2026-09-23): that rate would mean parallel
merging has become the norm rather than a burst, and the re-runs would then be
cheaper than the ports.

**Answered 2026-09-23: hold** (project owner, 2026-09-23, ratified, over
requiring branches to be up to date before merging now, and over a merge queue).
Strict up-to-date checks are adopted at a third instance within 30 days of the
last, so by 2026-10-23. The count is not left to `bin/docket new`'s recurrence
matching, which needs a capture's paths to overlap this item's. A third instance
triaged into the workflow lane also reaches this item through that lane's
generator check, which asks whether a capture re-enters an item closed within 30
days; one triaged into the product lane, as `PL-33WM`'s `ROADMAP.md` fix would
be, relies on the session that diagnoses it finding this item. Closed on this
answer, per **Done when.**

**Generator check.** Not a generator: two instances, and the cause is an
external behaviour nothing models - CI proves a merge against the base as it
stood when the pull request was pushed, not as it stands at merge.
