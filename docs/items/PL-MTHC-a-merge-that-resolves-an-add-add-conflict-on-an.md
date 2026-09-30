---
id: PL-MTHC
title: A merge that resolves an add/add conflict on an item file by keeping one side drops the other side's edits and nothing reports it - #1210 overwrote the PL-8ZGY brief corrections #1199 had put on main
priority: P2
effort: M
status: done
classes: defect
feature: queue-hygiene
touches: subprojects/docket/src/docket, .claude/skills/docket/modes/capture.md, subprojects/docket/tests, subprojects/docket/README.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-28 triage pass
added: 2026-09-27
closed: 2026-09-30
pr: 1249
payoff: a merge can no longer silently drop an item brief's corrections by keeping the other branch's copy
not-delegable: the first step is finding which route made the copy, which decides the file the fix goes in and the test that proves it
---

**Problem.** A merge that resolves an add/add conflict on an item file by keeping one side drops the other side's edits and nothing reports it - #1210 overwrote the PL-8ZGY brief corrections #1199 had put on main

**Evidence, 2026-09-27.** `0207afd7` recovered `PL-8ZGY`'s file onto
`claude/cool-meitner-pjnueb` from `claude/pl-w40l-kidkwe` while `#1199` was
still open there, so two branches each held a copy. `9d71a82c` corrected the
copy on `#1199`'s branch, with the owner's agreement; `#1199` merged as
`30820c98`; `82f71f2a` resolved the add/add conflict that followed by keeping
the other branch's copy whole; and `#1210` (`887fd223`) then put the
uncorrected brief on `main`. Every check passed throughout. Add/add conflicts
on item files recur - `PL-KBFN`, `PL-8KPD` and `PL-MQH0` each work around one -
so the triage that takes this asks whether one mechanism explains them.
Restored on `claude/pl-8zgy-restore-brief`.

**Why it matters.** Every check passed while the owner's agreed corrections to
a brief were lost; they came back only because a session noticed (`#1215`,
`2d61cd3d` on `main`, records the loss). A brief is where decisions are
recorded, so a silent loss is a lost decision.

**Generator check.** `PL-KBFN`, `PL-8KPD` and `PL-MQH0` each waited on the fact
this merge misread - an item created on an unmerged branch exists nowhere else,
so a copy elsewhere is a second, independent add - rather than misreading it.
One misreading item is not a generator. The lead to check first is `PL-WNCT`'s
fact (whether pushed branch work has an open pull request that will carry it to
`main`): the copy was taken while `#1199` was open and would have carried it.

**Done when.** The route that put a second copy of the item on another branch
while an open pull request carried the first is found, and it refuses or
reports such a copy, held by a test; or this brief records why neither is
decidable and the capture skill's recovery step says to wait for the open pull
request.

**Resolution, 2026-09-30.** The route was `bin/docket claim`'s refusal of an
id `HEAD` holds no copy of. It said "commit a capture before claiming it"
whatever held the item, and `0207afd7`'s own message gives it as the reason
for the copy: "this branch cannot claim it without a copy in its own store".
The copy was then made by `stranded`'s recovery, a `git checkout` of the file
off a branch whose pull request was open. Both now read `PL-WNCT`'s fact
through `open_pull_requests_command`:

- `claim`, asked for an item `HEAD` holds no copy of, reads after its fetch
  which branches hold the file and asks the forge once. Where a pull request
  is open on one, it refuses naming that pull request and says to wait for it
  and bring the default branch in; where the forge says none is open, it
  points at `stranded`'s recovery; where the forge could not be asked, it says
  both. Only an item no branch holds still gets "commit a capture".
- `claim` refuses a copy already committed where the base lacks the item,
  another branch with an open pull request adds it too, and this branch's add
  is the later of the two by author date, which is `0207afd7`'s shape. Every
  other shape is claimed: the earlier add is told of the later copy, one add
  shared through history says nothing, and a forge nobody asked is said.
- `stranded` withholds the `git checkout` for an item a pull request open on
  its branch carries, printing the pull request to wait for instead, and says
  beneath the list when the forge was not asked. The capture skill's recovery
  step and the docket README say the same.

Held by `test_an_item_only_another_branch_holds_is_refused_with_where_it_is`,
`test_a_later_copy_of_an_item_an_open_pull_request_carries_is_refused` and
`test_every_other_shape_of_a_second_copy_is_claimed_and_at_most_told` in
`subprojects/docket/tests/test_claiming.py`, and
`test_stranded_hands_an_item_a_pull_request_carries_the_pull_request_not_a_checkout`
in `subprojects/docket/tests/test_cli.py`. Checked live on 2026-09-30 against
`PL-2FY6`, then only on `claude/gifted-pasteur-iwimhy` with `#1248` open:
`stranded` printed the pull request and no checkout, and `claim PL-2FY6`
refused naming `#1248`, writing nothing.

Not covered, and deliberately: a copy of an item on a branch that has no pull
request open yet but is live, which is the judgment `stranded` leaves the
reader; and the merge itself, which still resolves an add/add conflict however
the session resolves it. Both need the copy to have been made first, and the
two routes that made it now say to wait.
