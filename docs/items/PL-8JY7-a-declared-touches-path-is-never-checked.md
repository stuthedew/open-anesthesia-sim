---
id: PL-8JY7
title: A declared `touches` path is never checked against the tree, so it goes stale silently
status: untriaged
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-08-30
---

**Problem.** `docket check` validates that a `verify:` command is present, that
a `blocked` item names its blocker and that a `done` item records a commit, but
it never asks whether the paths in `touches:` exist. Found while triaging
`PL-ZQ9C` (record an item's pull request, so provenance survives squash-merge),
which declared `subprojects/docket/src/docket/item.py` — a file renamed to
`model.py` at some point before the item was captured. The declaration had
never been read by anything.

**Why it matters.** `touches` is not documentation; it is the input to
`docket concurrent`, and the skill already says an absence of overlap proves
only that nobody foresaw a collision. A path that resolves nowhere is worse
than a missing one: it makes the item look analysed while contributing nothing
to the conflict graph, so two sessions can be told they may run together on
the strength of a filename that has not existed for weeks. It is also
decidable by reading the tree, which is where `CLAUDE.md` says the work
belongs.

**Worth deciding, and it decides whether this is worth building at all.** A
`touches` path may legitimately not exist yet — `PL-XH1D` names
`CONTRIBUTING.md` and `PL-LWMS` names `.mailmap`, both files their work
creates. So "the path does not resolve" cannot be an error, and the tool
cannot tell a file-to-be-created from a rename left behind. Three options, in
order of preference:

  - An **advisory**, in the shape of the existing no-`touches` one: list the
    unresolved paths and let a session judge. Cheap, honest about what it
    knows, and would have caught `item.py` the day it was written.
  - An **error with an escape**, e.g. a trailing `+` marking a path the work
    creates. Stronger, but it puts syntax in a field whose whole virtue is
    that it is a comma-separated list of paths.
  - **Nothing**, on the grounds that one stale path in 129 items is not a
    pattern.

**Where.** `subprojects/docket/src/docket/checks.py`, alongside `_groom`'s
existing advisories, using the same standard-library-only path handling as
`model._is_protected`. Tests in `subprojects/docket/tests/test_checks.py`.

**Done when.** `docket check` reports an item whose declared `touches` names a
path that is neither present in the tree nor plausibly created by the work, the
report is an advisory rather than an error, and a test covers both a resolving
path and a stale one.
