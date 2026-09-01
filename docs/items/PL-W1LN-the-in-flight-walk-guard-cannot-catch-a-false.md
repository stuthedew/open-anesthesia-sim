---
id: PL-W1LN
title: The in-flight walk guard cannot catch a false positive whose walk ends against a commit the base reaches by another path
priority: P3
effort: S
status: ready
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-08-31
verify: uv run pytest subprojects/docket/tests/test_vcs.py -k horizon
---
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

**Triaged 2026-09-01.** P3, `defect`/`infra`, `parallel-sessions`. The
`verify:` command was run first and selects nothing today, so it exits 5 until
a test named for the horizon exists; `-k walk` and `-k contained` both select
passing tests and would prove nothing.

Left out of v0.2.8's frozen list: this records a limit of `PL-MGNC`'s guard
rather than an observed misfire, and its own **Done when.** allows the answer
to be that the topology cannot be produced here. An entry that may turn out to
be undemonstrable is not one to hold a release open with.
