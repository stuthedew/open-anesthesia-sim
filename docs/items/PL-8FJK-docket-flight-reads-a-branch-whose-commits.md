---
id: PL-8FJK
title: docket flight reads a branch whose commits touch only item files as capture or triage, so items a grooming branch is closing stay offerable: #914 drops PL-027, PL-043 and PL-ZBR6 and none reads as in flight
status: untriaged
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-22
---

**Problem.** `vcs._annotates_only` reads any commit whose whole diff sits in
the queue directory as capture or triage, never as work. A grooming branch is
exactly that, and it *closes* items. Observed 2026-09-22: #914
(`claude/oldest-items-relevance-a0awgl`, PL-Y4YG, which grooms the ten oldest
open items) drops PL-027 (confirm the slider write-back on a Flet client),
PL-043 (dial increments) and PL-ZBR6 (core raise-branch coverage), and
rewrites seven more. `bin/docket show` prints no in-flight mark for any of
them, and `docket flight` does not list the branch.

**Why it matters.** `docket next` offers an item that a branch is closing, so a
second session can start work that another has already decided to drop. That
is the "two sessions on one piece of work" error `_annotates_only`'s own
docstring calls the costlier of its two failure modes. PL-Q89J (`docket next
--oldest`, #913) makes the collision likely rather than rare. It hands out the
oldest items first, and those are the items a grooming pass targets.

**Direction, for triage.** The docstring records that PL-X3WZ's eight false
marks needed "nothing finer" than the path test. This is the counterexample.
Whether a queue-only commit changes an item's `status` to `done` or `dropped`
is decidable from the diff, and it separates closing an item from recording
one.
