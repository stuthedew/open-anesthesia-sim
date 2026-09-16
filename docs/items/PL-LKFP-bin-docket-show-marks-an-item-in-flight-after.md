---
id: PL-LKFP
title: bin/docket show marks an item IN FLIGHT after its branch's pull request squash-merged, so PL-2M4X is ready on main and byte-identical on the branch and still says 'do not start' - PL-8MJ3 fixed this for the triage mark only
status: untriaged
added: 2026-09-16
---

**Problem.** bin/docket show marks an item IN FLIGHT after its branch's pull request squash-merged, so PL-2M4X is ready on main and byte-identical on the branch and still says 'do not start' - PL-8MJ3 fixed this for the triage mark only

**Measured 2026-09-16**, on `origin/main` at `2a538ec1`, with `#615`, `#616`
and `#617` all merged within the hour:

| item | status on `main` | branch still named | its copy on that branch |
| --- | --- | --- | --- |
| `PL-2M4X` | `P3 · S · ready` | `origin/claude/pl-syg4-pl-2m4x-triage` (landed as `#616`) | byte-identical to `main` |
| `PL-Y4YX` | `P3 · S · blocked` | `origin/claude/gate-items-triage-batch-g1w5uv` (landed as `#617`) | byte-identical to `main` |

`bin/docket show PL-2M4X` prints `IN FLIGHT on
origin/claude/pl-syg4-pl-2m4x-triage (last commit today) - do not start
PL-2M4X again`, and `bin/docket flight` lists five items of which these and
`PL-SYG4` are three. `git diff refs/remotes/origin/main refs/remotes/origin/<branch>
-- docs/items/<file>` is empty for both. The branches read as ahead by 2 and 9
commits, which is the squash merge: `main` took the content and none of the
commits, so containment never becomes true.

**Why this costs something rather than merely reading oddly.** `PL-2M4X` is
`ready` and startable, and the mark is what `bin/docket next` excludes on - so a
finished merge takes ready work *out* of the queue for every session, and it
stays out until somebody deletes a branch ref that nothing prompts them to
delete. Nothing reports it: the item looks busy, which is indistinguishable from
being busy, and `bin/docket stranded` says the opposite in the same breath -
"No branch carries work its own pull request left behind, across the 20
unmerged branch refs read."

**`PL-8MJ3` is the same defect, fixed once, in one of the two places.** It
closed in v0.4.15 against `triage`'s "already edited on a branch" mark, on
exactly this evidence - a pass told to skip four items, all four byte-identical
to `main` - and the skill records the repair: "It is now checked against the
base's own tip, so a skip is worth obeying." The `IN FLIGHT` mark and
`bin/docket flight` were not moved onto that reading, and they are the louder
of the two: the triage mark advises, this one says *do not start*.

**Not the same finding as `PL-99YZ` or `PL-HX5C`.** Both of those are guards
failing to *see* work that exists; this is a guard seeing work that has already
landed. The two have opposite fixes and only this one hides ready items.

**Where to look.** `subprojects/docket/src/docket/vcs.py` and
`render.py` are what `PL-8MJ3` touched; whatever base-tip comparison it added
for the edited-file mark is what `branches_in_flight` needs too.
