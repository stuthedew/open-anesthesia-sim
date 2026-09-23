---
id: PL-6MW8
title: PL-Z0SM's trigger fired on 2026-09-23 (third merge-skew instance within 30 days, #967 then #970): adopt strict up-to-date status checks on main and revise CLAUDE.md's rule against merging origin/main into an open pull request out of habit
priority: P2
effort: S
status: done
classes: docs, infra
feature: merge-skew
touches: CLAUDE.md, docs/maintainer.md, docs/resident-instructions.md
added: 2026-09-23
closed: 2026-09-23
payoff: a pull request green on a stale base can no longer merge into a red main
verify: grep -qF 'into an open pull request once, when' CLAUDE.md && ! grep -qF 'costs nothing that CI proves' CLAUDE.md
not-delegable: the setting is the project owner's, in main's branch protection, which no session can change
---

**Problem.** PL-Z0SM's trigger fired on 2026-09-23 (third merge-skew instance within 30 days, #967 then #970): adopt strict up-to-date status checks on main and revise CLAUDE.md's rule against merging origin/main into an open pull request out of habit

**The trigger.** `PL-Z0SM` (merge skew) was answered "hold" on 2026-09-23
(project owner, ratified), and the answer named what would change it: "Strict
up-to-date checks are adopted at a third instance within 30 days of the last."
`PL-70VB` is that third instance. #967 and #970 each passed CI on their own
base, and the two together turned `main` red at 17:18 the same day.

**Why it matters.** Each instance fails every open pull request at once. With
several sessions merging within the hour, that now happens more often than a
full `quality.yml` run per open pull request per merge would cost, which is the
break-even `PL-Z0SM` named.

**Done when.** `main`'s protection requires branches to be up to date before
merging, and the `CLAUDE.md` bullet "Do not merge `origin/main` into an open
pull request out of habit" says that a stale base is now refused at merge. It
must no longer argue that bringing the base in wastes a green run. The setting
is the project owner's to change. The `CLAUDE.md` edit follows it in the same
session that confirms the setting is on.


**Done 2026-09-23.** The owner turned the setting on and confirmed it in another
session. It shows independently too: #976 reported `mergeable_state: behind` the
same afternoon. GitHub reports that state only when the base branch requires
branches to be up to date (GraphQL `BEHIND`, "The head ref is out of date").
`GET /repos/stuthedew/open-anesthesia-sim/branches/main` reports the required
checks, `checks` and `pr-title`, at `enforcement_level: non_admins`. So the
owner can still bypass by hand. That is left as it is, as an escape hatch for
a broken CI, and `docs/maintainer.md` says to decline the bypass for ordinary
merges.

**Who brings the base in, and when.** Decided in this session, on the owner's
delegation.

- **When: once, when `behind` is the only thing between the pull request and
  its merge.** An update made earlier goes stale at the next merge to `main`
  and pays a full `quality.yml` run again. Each run took 142-300 s on
  2026-09-23, a day on which 50 commits reached `main`.
- **Who, for a pull request waiting on the owner: the owner, with *Update
  branch*, at merge time.** Only the owner knows when a merge is coming. The
  button sits next to the merge button, which GitHub will not use while the
  branch is behind, except through the admin bypass. *Enable auto-merge* in the
  same visit lands the pull request when its run goes green
  (`docs/maintainer.md`).
- **Who, for a pull request armed for auto-merge that is green with nothing
  else open: the session that armed it**, with `update_pull_request_branch`,
  the same server-side merge the button makes. GitHub's auto-merge never
  updates a branch. It "merges a pull request automatically after all
  required reviews and status checks pass", and the strict row of *About
  protected branches* says "you'll need to bring the head branch up to date".
  A session's GitHub calls authenticate as the owner (`GET /user` returns
  `stuthedew`, and `pull_request` runs on `claude/*` branches show that actor
  with no approval step). So the run starts on its own. An update made with
  `GITHUB_TOKEN` would not start on its own: its run is created "in an
  approval-required state".
- **Kept:** a genuine conflict, and a base-recovery notice. **Added:** a push
  being made anyway, which costs no extra run and matches `bin/docket
  branch`'s "Merge origin/main before your first edit, not at push time" line.
- **Rejected:** having sessions bring the base in at each check-in. That costs
  one run per check-in while `main` keeps moving, the cost this item was meant
  to avoid. The merge queue is the mechanism that would batch the updates, and
  it is available only to organization-owned repositories.

**The cost, stated honestly.** Each update is one run. Another is due only when
a merge lands between the update and the merge, so n pull requests ready at
once can take up to n-1 extra runs. That is one run per merge landing ahead of
the pull request, not one per move of `main` while it waits.

**Resident set: +234 characters, and what they replace.** The edit replaces
`PL-WC72`'s argument that a base merge "discards a green result" and that "a
stale base costs nothing that CI proves", both false under strict checks. It
also drops the restart clause, which has a row in `docs/resident-instructions.md`
§ "What was routed out". What is net new cannot be cut. It is the who and when
the owner asked for, plus a 51-character qualifier on the capture-arming bullet
naming `PL-S5MF`, so that bullet stays true. The owner's steps went to
`docs/maintainer.md` rather than into the resident set.

**Found, and handled elsewhere.** `PL-S5MF` records that an armed capture pull
request whose session has ended now stalls behind, with a recommendation.
`PL-46VF`, the hook that would deny habit merges, is dropped because this
change reversed the rule it would route. `tools/main_ci_status.py`'s "main is
red and no pull request will show it" was checked and still holds for every
pull request that has not brought the base in, which under this rule is every
one waiting on review. `PL-5MYR`'s two merge-skew lines are dated audit
records, not claims about now.

Sources, all read on docs.github.com on 2026-09-23: *About protected branches*
(the strict row, and admins exempt by default); *Automatically merging a pull
request*; *Keeping your pull request in sync with the base branch* (*Update
branch* and *Update with rebase*); *Managing a merge queue* (organization-owned
repositories only); the REST *Update a pull request branch* endpoint; and
*Triggering a workflow* (`GITHUB_TOKEN` updates are approval-required).
