---
id: PL-NXRJ
title: direct-merge-guard.sh refuses every merge_pull_request call, so a pull request the owner says Merge on that GitHub will not arm, being already green and current, waits on the owner's Squash and merge; since 2026-10-03 main's protection binds admins, so GitHub itself refuses a stale or red merge from a session
priority: P2
effort: S
status: ready
classes: infra, docs
feature: review-hold
touches: .claude/hooks/direct-merge-guard.sh, tests/unit/test_direct_merge_guard.py, CLAUDE.md, docs/maintainer.md
added: 2026-10-03
payoff: a pull request the owner says Merge on that is already green and current merges without the owner's click, and only while GitHub itself refuses a stale or red merge from the owner's account
verify: grep -qF 'enforcement_level' .claude/hooks/direct-merge-guard.sh && grep -qF 'def test_a_merge_is_let_through_while_the_base_binds_admins' tests/unit/test_direct_merge_guard.py && ! grep -qF 'so a session merges only by arming auto-merge' CLAUDE.md && grep -qF 'PL-NXRJ' docs/maintainer.md
---

**Problem.** direct-merge-guard.sh refuses every merge_pull_request call, so a pull request the owner says Merge on that GitHub will not arm, being already green and current, waits on the owner's Squash and merge; since 2026-10-03 main's protection binds admins, so GitHub itself refuses a stale or red merge from a session

**Evidence, 2026-10-03.** The owner answered "Merge" on `#1281` (`PL-4NG0`),
green on a head current with `main`. `enable_pr_auto_merge` refused ("already in
clean status"), `.claude/hooks/direct-merge-guard.sh` refused
`merge_pull_request` as `PL-S17R` built it to, and the merge waited on the
owner, who asked why a session can arm auto-merge but not squash-merge, and said
that merging everything by hand "takes the autopilot out of this". GitHub's
branch record for `main` (`GET /repos/stuthedew/open-anesthesia-sim/branches/main`,
unauthenticated) read `protection.required_status_checks.enforcement_level:
non_admins`: the required checks `checks` and `pr-title`, and the up-to-date rule
`PL-6MW8` set, bound everyone but an admin. A session's GitHub calls are the
owner's, an admin's, and that exemption is the whole of the case `PL-V2X5`
refused a session's direct merge on: "the API can pin the head and not the base,
so a merge that lands between the read and the call leaves the branch behind,
and this one merges anyway."

GitHub names the switch that closes it. "By default, the restrictions of a
branch protection rule don't apply to people with admin permissions to the
repository ... You can optionally apply the restrictions to administrators ...
too", under **Do not allow bypassing the above settings** ([About protected
branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches),
read 2026-10-03); the REST field behind it, `enforce_admins`, will "Enforce all
configured restrictions for administrators" ([Branch
protection](https://docs.github.com/en/rest/branches/branch-protection), read
2026-10-03). Neither `PL-V2X5` nor `PL-S17R` weighed it, and nothing in the tree
named it before this item.

**Answered 2026-10-03: turn it on** (project owner, 2026-10-03, ratified, over
keeping a pull request already green and current the owner's Squash and merge,
`PL-V2X5`). Chosen on a decision card in the Ship v0.6.0 project, whose
consequence read: "Sessions merge clean pull requests themselves; you lose the
admin override on main until you switch it off." The owner switched the setting
on for `main`, and the branch record then read `enforcement_level: everyone`
(12:13Z). It reopens `PL-V2X5`'s ratified answer on a constraint that answer's
case did not carry. The project's own instructions had asked for a direct
squash merge in this case since 2026-09-27; `PL-S17R`'s hook refused it from
2026-09-30, on `PL-V2X5`'s answer.

**What changes.** The hook asks GitHub, at each call, for the pull request's
base and that branch's record, and lets the merge through only where the record
reads `everyone`: GitHub then refuses the merge itself unless the required
checks pass on a head current with the base, the conditions auto-merge waits
for. Anything else, and a record it cannot read, is refused with the route that
stays: arm while a check is pending, or tell the owner the Squash and merge is
theirs. It reads at the call rather than once because the owner can switch the
setting off again, to merge past a red check, and a stale merge would then pass
on a fact that had stopped being true. The merge method needs no check: the
repository allows squash merges alone (`allow_merge_commit` and
`allow_rebase_merge` false, read 2026-10-03). `CLAUDE.md`'s merge bullet and
`docs/maintainer.md`'s exception say the same, and `docs/maintainer.md`'s step
2 stops describing an admin bypass the setting has removed.

**Why it matters.** Every pull request the owner says "Merge" on that is already
green and current waits on a click in the browser, which is the wait the owner's
merge rule exists to spare them, and the hook refuses a merge GitHub now holds to
the checks it was protecting.

**Done when.** A session's `merge_pull_request` call is let through while the
base's branch record reads `everyone`, and refused, naming what was read or
could not be, otherwise; tests pin both directions, the base read from the pull
request rather than assumed, and the unanswered read; `CLAUDE.md`'s merge
bullet and `docs/maintainer.md` say a session merges such a pull request itself.

**Generator check.** One-off. The admin exemption explains `PL-V2X5` and
`PL-S17R`, two items, so it is not a generator, and it is closed at its source
now that the setting is on. The fact this item reads, whether an admin is bound,
is GitHub's own record, read at the call by one reader.
