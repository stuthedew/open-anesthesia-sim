---
id: PL-W1LN
title: The in-flight walk guard cannot catch a false positive whose walk ends against a commit the base reaches by another path
status: untriaged
added: 2026-08-31
---

**Problem.** The in-flight walk guard cannot catch a false positive whose walk ends against a commit the base reaches by another path

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `PL-MGNC` made `_unmerged_commits` refuse a walk that ran off the
end of the history, detecting it by the commit with no parents such a walk
ends on. That catches every shape observed and the reproduction built for it,
but it is not the same claim as "the walk is complete".

A commit the default branch holds below its own grafted horizon is a false
positive whether or not the walk reaches a parentless commit afterwards. The
uncaught shape is a walk that descends past the horizon and then terminates
against some *other* commit the default branch does reach - possible where the
default branch's visible history is a merge structure whose paths are truncated
unevenly. The walk ends cleanly, and the ids it collected below the horizon are
reported.

**Why it matters.** Bounded rather than urgent: the failure direction is the
dangerous one - ids wrongly reported here are withheld from `docket next` - but
the topology needed is narrower than the one that fired on 2026-08-31, and
nothing has been seen taking it. Recorded so the guard's limit is written down
rather than inferred from its absence.

**Where.** `subprojects/docket/src/docket/vcs.py` - `_unmerged_commits`.

**Done when.** Either the shape is reproduced with real git and the guard
covers it, or it is shown to need a history this project cannot produce and
this is dropped with that reasoning in its `reason`.
