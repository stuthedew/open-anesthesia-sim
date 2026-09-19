---
id: PL-Q9Z1
title: _superseded reads a failed git diff as the tips agreeing about every path, so any silence from git drops every in-flight mark a ref carries - the one direction its own docstring says it must never fail in
status: done
added: 2026-09-17
closed: 2026-09-19
priority: P2
effort: M
classes: defect
feature: git-silence-channel
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_vcs_silence.py, subprojects/docket/tests/test_cli.py
verify: uv run pytest subprojects/docket/tests/test_vcs.py && grep -qr 'def test_one_silenced_git_call_never_leaves_a_read_looking_clean' subprojects/docket/tests/
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


---

## Built 2026-09-19

**The channel is a `str` subclass, `GitSilence`, and the choice was between the
three the brief named.** A second return value or an exception both change
`Runner`, which is `(args, root) -> str` and is the seam every one of the
module's fifty-odd call sites and every test fake is written to - so either
would have meant editing all of them to fix eight of them, and the edit is the
kind that looks mechanical and is not. A `str` subclass is invisible to a caller
with no use for it: a silence still reads, strips, splits and compares as the
`""` a failure has always collapsed to. What it costs is that the marker
survives no string operation, so it can only be read off the runner's own return
value, and a reader added later would not know to. `_Silences` is the answer to
that, below.

**The classification is git's exit codes, measured against git 2.43.0 rather
than recalled**, one probe per shape this module issues. Exit 1 is git answering
"no" - `rev-parse --verify --quiet` on a ref that is not there, `merge-base` on
unrelated histories - and 128 and 129 are git not answering. Treating every
non-zero exit as a failure was the first design and is wrong: it fires on every
checkout without an `origin/main`, which is an advisory nobody reads.

**One exception, and it is forced rather than chosen: `show <rev>:<path>`.** Git
exits 128 for a path a revision does not hold, and every caller of that shape
reads the empty string as "the base does not carry that file". The deciding fact
is that `GitRunner`'s other serving path agrees: `cat-file --batch` prints
`missing` and exits 0 for an absent path *and* for an absent revision alike, so
classifying the fatal exit as a failure would make the two paths disagree about
one question. The cost is named in `_asks_for_a_blob` rather than hidden: a
revision that vanished mid-read is indistinguishable there from a file that was
never in it, and this layer cannot separate them without a second process per
blob.

**`_Silences` is what made the breadth affordable.** A public read puts tens of
questions to git through a dozen helpers, and the floor binds the answer rather
than any one of them - so the wrapper counts what went unanswered beneath a read
and hands it a `declined` reason, instead of a flag threaded through every
signature in the module. Sixteen reads now carry it.

**The number that would have killed it, counted before building on it.** A
`declined` that fires in the ordinary case is worse than none. Measured on this
repository 2026-09-19: eight public reads put **174** questions to git and
**none** went unanswered, so the field is silent in the steady state.

**What the sweep found beyond the four `PL-BHVM` named.** That round measured a
*total* git failure, under which `stranded`, `lost`, `orphaned` and
`merged_pull_requests` decline correctly. Under a *single* silenced call they do
not: `stranded` dropped an item that exists on one branch and nowhere else,
`lost` dropped a deleted item, and `closed_by`, `closures_on_base`,
`records_on_base`, `filed_with_work` and `cut_window` each lost a finding with
`declined` empty. Five more breaches than the design round could see, all found
by the sweep rather than by reading.

**The sweep refuses a vacuous pass**, which is the part worth keeping. A read the
fixture gives nothing to find can lose nothing, so it would pass whatever it
does with a silence - the shape of check `CLAUDE.md` retires rather than keeps.
It fails instead, which is what drove the fixture from three branches to six and
is how `orphaned`, `filed_with_work` and `cut_window` came to be covered at all.
Findings are compared as sets rather than counts, so a silence that swaps one
finding for another is caught too.

**Three reads cannot decline at all** - `tags`, `changed_items` and
`default_base` answer with a bare collection or string - and are held by a test
that *asserts the breach* against `PL-ZPDM` rather than left looking covered.
Asserted rather than marked expected-to-fail, which was the first shape and was
wrong twice over: a test marked that way does not run, so it reads as a hole
whatever reason is attached to it, and `bin/docket verify` cannot read that
reason - it sees a suppression marker and refuses, correctly. A positive assertion is
the same signal in the form of a record, and fails the same day the gap closes.

**Two consumers refuse rather than proceed on a silence.** `bin/docket release`
runs both duplicate-release guards by looking for *evidence* that another
session is cutting, so their clean answer and their unread answer are the same
shape; before this they were the same value, and cutting on one is the v0.3.7
collision (`PL-66FP`) arriving through the guard built to stop it.
`cmd_trend` says when its history has a hole in it, because a missing stretch is
exactly what changes the shape of a trend.

**Not taken here:** `GitRunner` memoizes a silence as a silence, so the mark
survives the cache and a second caller sees what the first did. Whether a
failure should be memoized at all is `PL-MM7F`, which this unblocks.
