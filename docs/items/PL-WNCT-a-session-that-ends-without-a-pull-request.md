---
id: PL-WNCT
title: A session that ends without a pull request strands its captures on its branch and nothing at session end names them: ten recovery items were filed 09-19 to 09-21, against nine in 09-05 to 09-15
priority: P2
effort: M
status: done
classes: defect, infra
feature: generator-identification
milestone: v0.5.7
touches: CLAUDE.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the first 2026-09-23 triage pass
added: 2026-09-22
closed: 2026-09-23
pr: 941
payoff: captures and ratified decisions stop living only on branches nobody will merge, and the recovery items that carry them across - twelve in three days - stop being filed
verify: grep -qF 'pull request at its first push and arms auto-merge' CLAUDE.md
root-cause-of: PL-DN5K, PL-JF5Z, PL-T2YR, PL-QNQJ, PL-V3QB, PL-HZ1B, PL-Q0W8, PL-BYN2, PL-DZM1, PL-K13H, PL-F8Q7, PL-GL3Z, PL-4CPP, PL-H3LC, PL-VSJZ, PL-KT7C, PL-CPLD, PL-1VFK, PL-JYR4, PL-ZGK2, PL-YMKV
generator: spent - since #941 a branch carrying only item files opens its pull request at its first push and arms auto-merge, so a captures-only session no longer ends holding its captures by rule; a push after a merge is PL-3D2M's mechanism, which bin/docket branch and tools/left_behind_check.py report, a work branch ending before its pull request is the remainder this brief accepted, and the arming patches since are PL-MB2W's
misread: Whether pushed branch work has an open pull request that will carry it to main
---

**Problem.** A session that ends without a pull request strands its captures on its branch and nothing at session end names them: ten recovery items were filed 09-19 to 09-21, against nine in 09-05 to 09-15

**Reproduced 2026-09-23.** `bin/docket stranded`, after its own fetch, names
four items that exist only on a branch - `PL-1PBV` on
`origin/claude/exciting-mccarthy-fa8o39`, and `PL-KH3Q`, `PL-PXZ3` and
`PL-Z0SM` on `origin/claude/inspiring-bardeen-38yf9z` - and sixteen more whose
only edits are on branches. Read against the harness's session list the same
minute, no pull request is open for either branch: the first branch's session
reports itself completed and is disconnected, and a second session is copying
`PL-1PBV` across by hand; the second branch's session is out of budget and
handing off. So the mechanism is producing today, and its recovery is already
being done informally.

**The count, redone 2026-09-23 from each title and brief.** These are
recovery items whose cause is a session ending with pushed work that no open
pull request carries, either because it opened none or because its pull
request merged before its last push:

- **09-19 to 09-21, twelve:** `PL-DN5K`, `PL-JF5Z`, `PL-T2YR`, `PL-QNQJ`,
  `PL-V3QB`, `PL-HZ1B`, `PL-Q0W8`, `PL-BYN2`, `PL-DZM1`, `PL-K13H`, `PL-F8Q7`,
  `PL-GL3Z`. `PL-F8Q7` is also `PL-WFFX`'s. `PL-BXNH` is `PL-WFFX`'s alone,
  squash bodies the merge client dropped, and is not counted here.
- **09-22, two more for a stranding already recovered:** `PL-4CPP` and
  `PL-H3LC`, both `PL-BYN2`'s `PL-54V0` ratification again.
- **09-05 to 09-15, seven with this cause:** `PL-VSJZ`, `PL-KT7C`, `PL-CPLD`,
  `PL-1VFK`, `PL-JYR4`, `PL-ZGK2`, `PL-YMKV`. The window's other recoveries
  have other or unrecorded causes: a history rewrite (`PL-HG5D`) and deleted
  branches (`PL-KBFN`, `PL-ZYDF`).

As a share of everything filed, that is 12 of 311 against 7 of 580, which is
3.9% against 1.2%. The rise is not only more sessions.

**Why it matters.** An item that exists only on an unmerged branch is invisible
to `bin/docket next`, to the session-start digest and to every debt gate. Two of
these carried ratified project-owner decisions `main` did not hold, `PL-DMDF`
(in `PL-DZM1`) and `PL-54V0` (in `PL-BYN2`), and a decision nobody merged is
one a later session takes again, differently. Each recovery is also an item of
its own under `CLAUDE.md`'s housekeeping rule, so every stranding returns as
queue inflow. One ratification came back three times.

**Generator check.** Head. One mechanism, shared by 21 recovery items that no
head named: a session can end holding pushed work that no open pull request
carries, and nothing at the end of its turn says so. It is not `PL-R808`
(spent), which finds what a merged pull request left behind at the next
session's start and still leaves each recovery an item. Nor is it `PL-7TVT`
(spent), which reads whether a branch's session is live, not whether its work
lands.

**The fix at the mechanism: give a pushed capture its route to `main` when it
is pushed.** `CLAUDE.md` § "Commit and push as you go" says "a branch carrying
only captured items is not a pull request". So every session whose branch
holds only item files ends holding them by rule. That covers an ideation
session, a review, a triage pass, and one that stops for length. The harness's
stop hook asks only for a push, and a push that lands nowhere satisfies it. The
fix drops that limit for item files. A branch whose commits touch only
`docs/items/` opens its pull request at its first push, with auto-merge on, so
the captures land when CI is green whether or not the session is still there.
A session that dies then leaves an open pull request that `flight`, GitHub and
the owner can all see, rather than a bare ref that `bin/docket stranded` finds a
session later as a new recovery. A push after a merge is the same case, which
`capture.md` already carries forward as a new pull request. Building it means:

- a `CLAUDE.md` edit that removes a clause rather than adding one;
- a `capture.md` step: push, open the pull request, enable auto-merge;
- one repository setting only the owner holds, "Allow auto-merge".

It reverses an owner rule dated 2026-08-31 whose kind is unrecorded, so
ordinary evidence reopens it, and this count is that evidence. It adds no check
and no field. What it leaves: captures riding a work branch whose session dies
mid-work still wait for that work's pull request.

The weaker alternative is a turn-end reminder naming the items on the branch
that `main` lacks. Offline, it cannot see whether a pull request carries them.
It would also fire on every turn of every work session before its pull request
opens, which is the kind of check `CLAUDE.md` retires.

**Decision needed.** Should a branch carrying only item files open its pull
request at its first push and merge itself when green? That reverses
`CLAUDE.md`'s "a branch carrying only captured items is not a pull request"
(project owner, 2026-08-31).

**Recommended: yes.** It costs one pull request and one CI run per such
session, one repository setting, and a longer pull-request list. It buys the
end of most of the twelve recoveries counted above in three days. Ratified
decisions stop living only on refs a prune can take.

**Done when.** A capture pushed by a session that then ends reaches `main` or
an open pull request without a later session filing an item to recover it. Or
the owner has declined the change, and this brief records the recovery route
as the generator's accepted cost.

**Decided 2026-09-23: yes** (project owner, 2026-09-23, ratified, over keeping
"a branch carrying only captured items is not a pull request"). `CLAUDE.md` §
"The queue, and how the project owner works" now says a branch carrying only
item files opens its pull request at its first push and arms auto-merge. The
first push carrying anything else disarms it first, because otherwise green CI
would merge half-finished work. The recommendation above did not name that
hazard. The repository setting was already on: the owner armed auto-merge on
`#936`, which GitHub refuses where a repository disallows it. `capture.md`
needed nothing, since `CLAUDE.md` was the only place the old rule was stated.
