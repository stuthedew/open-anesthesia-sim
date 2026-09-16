---
id: PL-LKFP
title: bin/docket show marks an item IN FLIGHT after its branch's pull request squash-merged, so PL-2M4X is ready on main and byte-identical on the branch and still says 'do not start' - PL-8MJ3 fixed this for the triage mark only
priority: P2
effort: S
status: done
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-16
closed: 2026-09-16
verify: uv run pytest subprojects/docket/tests/test_vcs.py && grep -q 'def test_an_item_the_base_took_without_closing_is_not_reported_in_flight' subprojects/docket/tests/test_vcs.py
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

**The title's last clause was wrong, and the root cause is narrower.** It said
`PL-8MJ3` fixed this for the triage mark only. `PL-8MJ3` is a different guard,
and the one that should have caught this - `_closed_on_base` - was already
there and already correct. Traced 2026-09-16:

- `_work_already_on_base` asks whether every blob a ref introduces is one the
  base has ever held. **One shared file defeats it forever.** The squash
  resolves `ROADMAP.md` against a base that has moved, and later merges rewrite
  lines the branch added, so the branch's own copy is a blob the base has never
  held. Both branches measured were outstanding on that path and on no other:
  six item blobs of seven landed byte for byte on `#616`'s, thirteen of
  fourteen on `#617`'s.
- `_superseded` answers half of it. Run against the two: it cleared `#617`'s
  `ROADMAP.md` (removals only) and not `#616`'s, whose diff from the base adds
  four stale lines - an entry count and a re-wrapped bullet the base has since
  rewritten. A rewrite reads as an addition, which that test cannot call
  superseded without also calling real work superseded.
- `_closed_on_base` is the guard that *does* fire on a merged branch, and it
  fires per id rather than per ref. It is why `PL-C92D`, `PL-Q0J1` and
  `PL-99YZ` left the report on the same fetch that kept `PL-2M4X`. **The gap is
  a triage pass**, which lands its items at `ready`, `blocked` or
  `needs-decision`. The work merged; the item stayed open; the claim survived.

**The fix is that guard's second half**, `_taken_on_base`, asked of the same
set and at the same call site. An id leaves the report when both hold: the
base's copy of the item's own file is byte-identical to the ref's, so the ref
carries no unmerged change to that item; and the base took a commit leading
with that id at or after the ref's fork point, so the base has already had this
ref's work under this name.

Both halves are load-bearing and each has a test. File identity alone would
drop a session that pushed its first failing test under its item's id before
touching the item file. The fork point alone would count the item's own capture
commit, which every branch forks from. Every silence - no fork point, no file
on either side, a blob git would not resolve - keeps the claim, which is the
direction this module fails in by construction.

**Checked against the real refs before the test was written.** With the two
squash-merged tips still in the object store, `_taken_on_base` drops `PL-2M4X`,
`PL-SYG4` and `PL-Y4YX` and keeps a claim the base took nothing under.
