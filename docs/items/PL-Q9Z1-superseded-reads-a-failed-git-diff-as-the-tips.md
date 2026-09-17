---
id: PL-Q9Z1
title: _superseded reads a failed git diff as the tips agreeing about every path, so any silence from git drops every in-flight mark a ref carries - the one direction its own docstring says it must never fail in
status: untriaged
added: 2026-09-17
---

**Problem.** _superseded reads a failed git diff as the tips agreeing about every path, so any silence from git drops every in-flight mark a ref carries - the one direction its own docstring says it must never fail in

**Found while hoisting `_superseded` out of the per-path loop (`PL-DMDF`), and
it is that function's own claim about itself that is wrong.** Its docstring
states the safety direction in one sentence:

> Every silence here - a git that failed, a path git answered for in a shape
> this cannot parse, a binary file git writes as `-` rather than a count -
> leaves the path outstanding and so leaves the branch reported.

Two of those three are inverted in the code. Read
`subprojects/docket/src/docket/vcs.py`:

| The silence | What the docstring claims | What the code does |
| --- | --- | --- |
| git failed, so `_run_git` returned `""` | path left outstanding | **every path superseded** |
| a `--numstat` line this cannot split into three fields | path left outstanding | **that path superseded** |
| a binary file, written `-\t-\tpath` | path left outstanding | path left outstanding |

The mechanism is one branch. `_run_git` collapses every failure to the empty
string, so an empty `--numstat` is indistinguishable from "git could not
answer" - and the reading of an absent path is `superseded.add(path)`, on the
comment "the two tips agree on this path, so the base is missing nothing".
That inference is sound only when git *answered*. Nothing at this layer can
tell the two apart, because `Runner` returns `str` and has no failure channel.

**What it costs, in both callers.** `branches_in_flight` drops the item from
`editing`, so the digest stops saying another branch is in that item file and
two sessions triage it into a merge conflict - the failure `PL-N1JK` records.
`orphaned` narrows its outstanding side to nothing, so a branch carrying work
nothing merged is not reported at all, which is the "wrongly called superseded
would hide work nothing merged" case the same docstring names as the expensive
one.

**Reachable, not theoretical.** `_run_git` gives git a 10-second timeout, and
the pathspec these callers hand over is now a whole ref's outstanding set
rather than one path, so one timeout drops a whole ref's marks rather than one
path's. `PL-DMDF` closed the one *new* cause it introduced - an argv over
`ARG_MAX`, which `subprocess` raises on - by splitting the pathspec at 64 KiB
in `_pathspec_chunks`. The pre-existing causes are untouched, and the blast
radius per failure is now larger.

**Two routes, and the choice is the item.** Give `Runner` a way to say "git
failed" - a sentinel, an exception, or a second return value - and have
`_superseded` leave every path in a failed chunk outstanding; or corroborate
cheaply inside `_superseded`, since a `--numstat` that names nothing while the
ref is known to differ from the base is already suspicious. The first is
honest and reaches every other silence-swallowing read in the module; the
second is local and pins nothing else. Neither is a fix-now: both need a test
that drives a failing git, which is why this is filed rather than folded into
`PL-DMDF`.

**Done when** a `_superseded` call whose git fails leaves every path in that
call outstanding, a test drives the failure rather than asserting the rule
against itself, and the docstring's three-silence sentence is either true or
rewritten to say what the code does.
