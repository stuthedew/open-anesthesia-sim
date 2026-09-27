---
id: PL-WKLJ
title: The unmerged-cut advisory keeps naming in-progress work after the absorb route is taken, because cut_window reads landed ids off commit subjects and a re-cut can only fold in closures; reading each landed id's status on the base would leave only what the notes should name
priority: P3
effort: S
status: ready
classes: defect
feature: release-process
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-27
payoff: a release session that has taken the absorb route stops being told to absorb unfinished work, so the advisory names only closures the notes really miss and stays worth reading
verify: grep -rq 'def test_a_capture_landing_during_the_cut_is_not_named_after_the_absorb_route' subprojects/docket/tests/
---

**Problem.** The unmerged-cut advisory keeps naming in-progress work after the absorb route is taken, because cut_window reads landed ids off commit subjects and a re-cut can only fold in closures; reading each landed id's status on the base would leave only what the notes should name

**Why it matters.** `PL-C0C0` measured the window from the commit that wrote
the cut's notes, so a base merge no longer ends the report. That also means
nothing ends it before the cut merges, and some of what it reports can never
be absorbed. `_landed_since` in `subprojects/docket/src/docket/vcs.py` takes
the ids leading the base's subjects. A capture, a design round or a triage
pass leads with an id it does not close. A re-cut stamps only finished work,
so after the absorb route `_check_cut_window` in
`subprojects/docket/src/docket/checks.py` still names those ids. It keeps
advising the route the session has just taken. In the 40 newest commits on
`main` at `23f95714`, 12 of 54 leading ids were not closed by the commit they
lead, going by whether its diff sets the item's `status:` to done or dropped.
At that rate an hour-long release window typically has one. The advisory's
last sentence says an id may be in-progress work, so the report is true. What
it costs is attention: an advisory that fires after its own remedy trains the
release session to skim it.

**Done when.** After the absorb route, the advisory names only work that
closed on the base without being named in the cut's notes. An id whose status
cannot be read is named as unread, not dropped. A test drives a capture landing
on the base during the cut.

One candidate is to read each landed id's item file from the base's tree,
bounded like `_landed_since` at 40, and keep ids whose `status:` there is done
or dropped. The trade is that `CutWindow`'s docstring calls subject-derived the
right accuracy for an advisory, and `PL-8M8H` is where the same read was
refused for acting on its own. Reading status from the base is closure-accurate
whether or not the base was merged in. The checkout's own store is not: before
a merge it holds the base's closures as still open.

**Generator check.** The fact is which items a base commit *closed*, as
distinct from the ids leading its subject, which name what it is about;
`_landed_since` reads the second for the first, and `_check_cut_window` names
what it returns. No head's `misread:` states it and no open item misreads it: a
one-off. Nor is it a re-entry of `PL-C0C0` (closed 2026-09-27), whose fix moved
where the window starts and made no claim about what it names; this is the edge
that move exposed.
