---
id: PL-8JY7
title: A declared `touches` path is never checked against the tree, so it goes stale silently
priority: P3
effort: S
status: ready
classes: infra
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-08-30
verify: uv run pytest subprojects/docket/tests -k "touches and stale" && bin/docket check
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

**Decided (project owner, 2026-08-30): an advisory.** A `touches` path may
legitimately not exist yet — `PL-XH1D` (state how the project is developed)
names `CONTRIBUTING.md` and `PL-LWMS` (normalize commit messages with a
commit-msg hook) names `.mailmap`, both files their own work creates. So "the
path does not resolve" cannot be an error, and nothing decidable separates a
file-to-be-created from a rename left behind. The advisory says only what it
knows — these paths are not in the tree — and leaves the judgment to the
session reading it, which is the line `tools/doc_check.py` already draws.

It takes the shape of the existing no-`touches` advisory in `_groom`, and it
would have caught `item.py` the day it was written. The two rejected options
are recorded so they are not re-proposed: an **error with an escape** (a
trailing `+` marking a path the work creates) puts syntax into a field whose
whole virtue is that it is a comma-separated list of paths; and **doing
nothing** loses a check that costs about twenty lines and then runs free
forever.

**Where.** `subprojects/docket/src/docket/checks.py`, alongside `_groom`'s
existing advisories, using the same standard-library-only path handling as
`model._is_protected`. Tests in `subprojects/docket/tests/test_checks.py`.

**Done when.** `docket check` lists, as an advisory, every item whose declared
`touches` names a path not present in the tree; the run still exits zero; and
tests cover a resolving path, a stale one, and an item declaring no `touches`
at all (which stays the separate advisory it already is).

**Cheapest to land alongside `PL-68XK`** (check that every recorded commit
hash resolves) **or `PL-ZQ9C`** (record an item's pull request). All three edit
`subprojects/docket/src/docket/checks.py`, so `docket concurrent` will flag
them as contending — they want doing in one pass, not in parallel.
