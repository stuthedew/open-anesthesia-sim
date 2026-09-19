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

**Re-pointed by `PL-BHVM`'s design round, 2026-09-19 — this is the first build,
and it is wider than the brief above says.** `PL-BHVM` carries the reasoning.
Three amendments:

- **The reachability argument is wrong in its mechanism and right in its
  conclusion.** The brief rests on `_run_git`'s 10-second timeout. Measured on
  2026-09-19 against this repository, the real `diff --numstat` calls run in
  **4.5 ms** — three orders of magnitude of headroom, so a timeout is not the
  trigger. A **non-zero exit** is, and the likely one here is a ref that
  vanishes between the `for-each-ref` that lists it and the `diff` that reads
  it: another session's branch deleted, or a merged branch cleaned up, while
  the digest runs. Verified — git answers `fatal: bad revision`, `_run_git`
  returns `""`, and every path in that call reads as superseded.
- **The cost is measured rather than argued.** Substituting a runner that fails
  only `diff --numstat` and answers everything else truthfully takes
  `branches_in_flight` from **13 `editing` marks to 0**, with `unreadable`
  staying **empty** in both cases. One failed call deletes every in-flight edit
  warning the digest has and nothing says anything went unread. That is
  `.claude/rules/apparatus-standard.md`'s floor breached on
  `FlightReport.unreadable` — the field the floor's own text cites as an
  instance of the code holding to it.
- **It is not confined to `_superseded`.** Under a total git failure
  `stranded`, `lost`, `orphaned` and `merged_pull_requests` decline correctly,
  while `branches_in_flight`, `precedence`, `branch_state` and `default_base`
  each return a confident clean answer. So the fix is the failure channel *and*
  a **fault-injection test that fails the Nth git call and asserts each public
  read declines or keeps the mark** — prose cannot enforce it, since this
  function's docstring already states the right direction in three cases while
  the code inverts two.

**One test changes with it.** `subprojects/docket/tests/test_vcs.py:467`,
`test_no_git_means_no_claims_about_branches`, drives a total git failure and
asserts `branches == ()` — it pins the breach. It sits one file away from
`test_no_git_declines_rather_than_reporting_a_clean_store`, which asserts the
opposite for `stranded`.
