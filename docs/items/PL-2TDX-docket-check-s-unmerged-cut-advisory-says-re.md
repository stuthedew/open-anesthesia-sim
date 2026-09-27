---
id: PL-2TDX
title: docket check's unmerged-cut advisory says re-running make release VERSION=X absorbs what the base took since, but once the cut's notes are written that run exits 1 on the version as shipped and untagged, and only absorbs after the notes file is removed
priority: P3
effort: S
status: done
classes: defect
feature: release-process
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/release.py, subprojects/docket/README.md, subprojects/docket/tests
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
closed: 2026-09-27
pr: 1148
payoff: a session told to absorb work that landed during a release cut can do it with the command the advisory names, instead of meeting a refusal that points at tagging
verify: grep -rq 'def test_absorbing_after_the_notes_are_written_folds_the_new_work_in' subprojects/docket/tests/
recurrences: 2026-09-27 PL-C0C0
---

**Problem.** docket check's unmerged-cut advisory says re-running make release VERSION=X absorbs what the base took since, but once the cut's notes are written that run exits 1 on the version as shipped and untagged, and only absorbs after the notes file is removed

**Why it matters.** The advisory is `_check_cut_window` in
`subprojects/docket/src/docket/checks.py`. It fires on a checkout carrying an
unmerged cut once the base has taken work since, and it names two
dispositions: absorb the work, by merging the base in and re-running `make
release VERSION=X`, "which reclaims what this cut already stamped", or let it
go to the next release. The first does not work at the moment the advisory
fires. By then the cut has written its notes, so `unrecorded_milestones` in
`cmd_release` (`subprojects/docket/src/docket/cli.py`) finds nothing
interrupted and `resuming` is empty. `current` already reads X, so the run
treats vX as a shipped release, refuses it as untagged, and exits 1. Its
message tells the session to tag vX on `origin/main`, which does not yet hold
the notes, and it adds that the tag line "will refuse as it stands". A session
following the advisory gets a refusal pointing somewhere else, with nothing
that says the notes file is what blocks the reclaim.

Observed 2026-09-26 on `PL-9MK6`'s v0.5.13 cut (`#1141`). With
`docs/releases/v0.5.13.md` written, `bin/docket release 0.5.13` exited 1 on
"v0.5.13 shipped and carries no tag". With that file removed, the same run
printed "Resuming an interrupted cut of v0.5.13: 17 of these 18 item(s) were
stamped by the run that stopped", wrote the notes and stamped `PL-YFT4`.

**Done when.** Following the advisory's absorb route on a checkout whose cut
has written its notes folds the new work into that cut, or the advisory names
the step that makes it do so. Either route is open. `cmd_release` could treat
an unmerged cut of the current version on this branch as resumable, or the
advisory could say to remove the notes file before re-running. The first keeps
the advisory's promise and the second keeps the resume rule unchanged. A test
drives the absorb route end to end from a cut with its notes written.
