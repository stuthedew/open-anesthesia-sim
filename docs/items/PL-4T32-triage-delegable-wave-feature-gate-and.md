---
id: PL-4T32
title: triage, delegable, wave, feature, gate and generators still answer from the working tree's copy of each item behind origin/main, where the digest, list, status, concurrent, next, show and picks read the base's newer copy through cli._load_to_read
priority: P2
effort: S
status: done
classes: defect
feature: one-snapshot
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/README.md, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - a workflow-lane defect in docket's read commands, which the layout milestone does not reach
added: 2026-10-19
closed: 2026-10-19
payoff: every read command answers from the same copy of each item, so delegable cannot hand a worker an item main has closed and triage cannot offer one main has triaged
verify: grep -q 'def test_every_other_read_command_reads_the_base_s_copy_behind_main' subprojects/docket/tests/test_cli.py && ! grep -q 'also still read the working tree' subprojects/docket/README.md
---

**Problem.** triage, delegable, wave, feature, gate and generators still answer from the working tree's copy of each item behind origin/main, where the digest, list, status, concurrent, next, show and picks read the base's newer copy through cli._load_to_read

**Why it matters.** Found closing `PL-KS01`, which moved the digest, `list`,
`status` and `concurrent` onto `cli._load_to_read`, the loader that reads the
default branch's newer copy of each item. That item's brief named only those
four, so the other read commands were left as they were. Behind a closure on
`origin/main`, `delegable` can still offer a worker an item that `main` has
closed, and `triage` can list an item that `main` has already triaged.
`triage` is followed by edits to the working tree's files, so whether it
should read the base's copy is a real question rather than a plain defect.

**Done when.** Each of these commands either loads the store through
`cli._load_to_read`, or the README's `PL-Y48N` paragraph gives the reason it
reads the working tree's copy.

**Generator check.** Not a head. With `PL-Y48N` and `PL-KS01` it is the third
filing on one fact: which copy of an item a read command answers from. Each
earlier fix moved only the commands its brief named. This item moves the last
read commands of the items onto `cli._load_to_read`, and the README names each
command that still reads the working tree's copy and why, so the mechanism has
no command left to hand it another member.

**Done 2026-10-19.** `triage`, `delegable`, `wave`, `feature`, `gate` and
`generators` load the store through `cli._load_to_read` and print
`_say_read_from_base` with their answers. `triage` reads the base's copy as
well, because an item the base has already triaged should not be offered for a
second answer that the merge would discard; `set` still writes the working
tree's file. `flight`, `stranded` and `branch` report on refs, and `trend` and
`inflow` count this checkout's own history and fetch nothing, so they stay on
the working tree's copy, and the README's `PL-Y48N` paragraph says so.
`test_every_other_read_command_reads_the_base_s_copy_behind_main` fails on the
code before the change, at `triage did not say it read the base's copy`.
