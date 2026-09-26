---
id: PL-979D
title: The squash commit on main is composed by whichever merge path lands it and nothing records the pull request's body at the merge, so each new way a path rewrites it - emptied, replaced, hard-wrapped, a subject frozen at arming - arrives as its own item: PL-WFFX's fact, reopened by three instances filed after it closed
priority: P2
effort: M
status: ready
classes: defect
feature: pr-body-integrity
touches: tools/pr_body_check.py, tests/unit/test_pr_body_check.py
blocked-by: PL-HMZZ
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-25
payoff: the reasoning behind each merged change survives however it was merged, and a new merge path's rewrite stops producing an item
verify: grep -q -- '--record' tools/pr_body_check.py
root-cause-of: PL-Y1W0, PL-BZHX, PL-PNJF, PL-M7W1
generator: live - the merge paths still compose the squash body their own way (a hard-wrapping path landed 9 of 10 table bodies broken since 2026-09-22) and nothing records the pull request's body, so each new rewrite arrives as its own item
misread: The squash commit's subject and body as the merge sends them, not as the pull request shows them
---

**Problem.** The squash commit on main is composed by whichever merge path lands it and nothing records the pull request's body at the merge, so each new way a path rewrites it - emptied, replaced, hard-wrapped, a subject frozen at arming - arrives as its own item: PL-WFFX's fact, reopened by three instances filed after it closed

Found 2026-09-25 by the triage pass, from the post-close test in `.claude/skills/docket/modes/triage.md`. `PL-WFFX` closed `spent` on the empty `commit_message` from the GitHub iPhone app. Three items stating its `misread:` were filed after it closed: `PL-Y1W0` (eight bodies non-empty but different from their pull request's), `PL-BZHX` (bodies hard-wrapped at about 72 columns: 96 of the 140 bodies carrying a table since 2026-09-10 have broken rows, two landed unwrapped, so at least two merge paths exist) and `PL-PNJF` (27 differing bodies that `--recover` cannot record). `PL-M7W1` (the squash subject frozen when auto-merge is armed) is still open from before.

**Why it matters.** The squash body is the permanent record of why a change was made, and the project reads it back (`tools/pr_body_check.py`, `docket check`'s pull-request recovery). `PL-WFFX`'s fix removed one merge path's failure, and the fact itself stayed live: every other path still composes the body its own way, and no copy of the pull request's body is kept to compare against or recover from.

**Decision needed.** Which of two things is the permanent record of a pull request's reasoning. One option is the squash body, in which case every merge path used here has to be pinned to one that sends the body verbatim. The other is a copy recorded in the tree before the merge, in which case a path's rewrite stops mattering.

**Recommendation:** the copy recorded before the merge, built with `PL-HMZZ`, whose design round (#1011) already chose to record the carrying pull request before the merge, enforced by the pull request's own check. The body can ride the same record. That ends the whole family instead of chasing each merge path, and it turns `PL-BZHX` and `PL-PNJF` into recovery work against the record. It is the owner's call because it changes where the project's permanent history lives.

**Answered 2026-09-25** (project owner, 2026-09-25, ratified, over pinning every merge path to one that sends the body verbatim): a copy recorded in the tree before the merge, built with `PL-HMZZ`. `PL-HMZZ`'s build (#1056, 2026-09-26) is the writer and
check this rides.

**What the answer leaves to decide: the form of the copy, and who writes and
checks it.** `PL-HMZZ`'s record is one number on each closure, written by the
closing branch and refused by the pull request's own required check when
absent (`PL-HMZZ` § "Decided 2026-09-25: record before the merge"). A body is
a document, and a pull request that closes nothing has no closure to carry it:
41 of the 105 pull requests merged above `#921` are named by no item's `pr:`,
and this design round's own pull request is one. So the body cannot literally
ride the `pr:` line. What it rides is the same shape - written on the branch
while the pull request is open, at the one point that knows the pull request's
number and body, and held by the same required check - and that shape is what
this round puts to the owner, because the build would otherwise choose it
unasked.

**Recommendation, second round (design round, 2026-09-25, after the answer).**
Three parts, mirroring `PL-HMZZ`'s:

1. **The record is `docs/pr-bodies/<N>.md`, one file per pull request,
   written before the merge.** The store already exists - 201 files, every one
   written after its merge, for a body the merge dropped or a pull request
   that had none - and one file per pull request is the shape
   `docs/dead-ends.md` chose over a shared document. A new mode of
   `tools/pr_body_check.py`, `--record N` (or bare, finding the branch's open
   pull request as `pr_title_check.py --discover` does), fetches the pull
   request's body from the API, as `--recover` already does without a token,
   and writes it verbatim under a front matter of `pr:` and `recorded:` (the
   date). No `commit:` and no `merged:`, because before the merge neither
   exists - which is `PL-73G8`'s dangling-sha defect not arising. The session
   runs it once the pull request is open and again after any edit to the
   body, and commits the file on the branch: it rides the push `PL-HMZZ`'s
   number already costs on a closing pull request, and costs one push of its
   own on one that closes nothing. It is fetched rather than written from what
   the session sent, because the API's copy is what the merge sends and what a
   reader on GitHub meets, and the server rewrites bodies silently
   (`PL-1DN9`): the recorded file is the read-back `CLAUDE.md`'s
   commit-and-push bullet asks for, made a diff a session can run, which
   answers `PL-DMNX`'s question as a consequence rather than as a step of its
   own.
2. **The guarantee is a step in `pr-title.yml`'s required job, which already
   runs on `edited`.** It reads `github.event.pull_request.body` through the
   environment, as the title step reads the title, and fails unless the body
   is empty or `docs/pr-bodies/<N>.md` exists on the head holding the same
   body - compared exactly after `\r\n` and trailing whitespace, with none of
   `--compare`'s whitespace collapse or hash masking, since both sides come
   from the same source. `edited` is the trigger that matters: a body edited
   after the copy was recorded re-runs the check on the head, turns it red,
   and holds the merge until the copy is recorded again. That is what makes
   the copy the record rather than a snapshot - nothing can merge with a body
   the tree does not hold - and it is why the arm-time freeze (six of
   `PL-Y1W0`'s 27 are exactly `auto_merge.commit_message`) stops mattering:
   what the merge sends is no longer the record. Standard library, a sibling
   of `tools/pr_title_check.py`, needing no lift from the generator pause,
   since it is the fix for a live head.
3. **The readers change sides.** The squash body on `main` becomes a derived
   copy, useful in `git log` and nothing more: its wrap (`PL-BZHX`), its
   freeze at arming (`PL-M7W1`'s body half) and its rewrite by any client stop
   being defects in the record. `--compare` loses its job as a defect
   detector, and stays a hand-run measurement or is retired, the build's call
   under `CLAUDE.md`'s rule that a check earns its place every run. The
   default mode keeps its one line, which after this rule can only name a
   pre-rule merge or an admin bypass of the check, with `--recover` as the
   remedy. The module docstring, `docs/maintainer.md` § "Merge on the Mac or
   by auto-merge, never in the GitHub app" and `docs/ARCHITECTURE.md`'s line
   for the tool all say today that the pull request's description *is* the
   squash commit message and the permanent record; each is rewritten to say
   the file is, and the squash body is its copy.

**Forward only, no backfill.** 714 squash commits on `origin/main` carry a body
and no file (2,962,558 characters, against 1.3 MB in the 201 files there
now). Their pull requests still hold the intact form on GitHub, and `--record
N` can fetch any one on request, with the header saying it was recovered after
the merge on a date rather than recorded before it. Fetching all 714 is a
script run whenever it is wanted, so nothing is lost by not doing it now, and
doing it doubles the store for bodies `git log` already holds in a wrapped
form. Counted both ways, as `.claude/rules/expert-review.md` asks: the wrap is
in 166 of the 248 tabled bodies on `main` (67%), which is the case for a
backfill, and that count is why it is a separate yes or no rather than part of
this one.

**Why this and not the alternatives.**

- *Pin every merge path so the squash sends the body verbatim*: refused by the
  owner's answer above.
- *The closing item's file as the record*: a pull request closes none or
  several, an item's file is the item's rather than the change's, and `verify`
  would then read every body as an out-of-`touches` edit to an item.
- *CI writes the file at the merge*: a `GITHUB_TOKEN` push starts no workflow
  and `main` is protected (`PL-N5WZ`, in the digest's dead ends).
- *Record what the session sent rather than what GitHub holds*: the file
  cannot be named before the number exists, and the merge sends GitHub's
  copy, so where the server rewrote the body the record would hold text no
  reader on GitHub and no merge ever sees.
- *A `git notes` ref*: not fetched by default, invisible in a checkout, and
  orphaned by a rewrite like the one that remapped every hash on 2026-09-06.

**What it costs.** One file per pull request, about 4 KB at the measured
average. One extra push on the 40 in 100 pull requests that close nothing; on
the rest the file rides the push `PL-HMZZ`'s number already costs. A red
`pr-title` run on every pull request between its opening and its first record,
the same window `PL-HMZZ` accepts for the number. A body edited by hand after
its session has gone holds the merge until a session records it again, which is
the guarantee doing its job and goes in `docs/maintainer.md`. Two rules must
learn the path before it lands, or every pull request holds: `arming.py` arms
only a net change under the store, so `docs/pr-bodies/` joins the set that arms
on green (a record, never a change to read; `PL-K6B2`, ready, changes that set,
so the build lands after it or inside it), and `verify` considers only paths
under the store for its sanctioned kinds, so a record file in the diff reads as
outside `touches` until it is sanctioned as `record` beside `pr`. The build
touches `tools/pr_body_check.py` and its test, `.github/workflows/pr-title.yml`,
`subprojects/docket/src/docket/arming.py` and `verify.py`,
`docs/maintainer.md`, `docs/ARCHITECTURE.md`,
`.claude/skills/docket/modes/close-out.md` and `docs/pr-bodies/`; `touches`
is widened when the build starts, not by this round.

**The members, under this answer.** `PL-BZHX`: decided - the wrap is a property
of a derived copy, so no detector, no merge-path instruction, and no
measurement of which path wraps; it closes with the build, when the docstring
it cites stops calling the squash body the permanent record. `PL-PNJF`: decided
for every pull request merged after the build, where the record is the file
whatever the merge sends, and narrowed for the 27 to the header - two
provenances, recorded before the merge or recovered after it on a date, which
is `PL-73G8`'s ask on the same lines, so the three land as one header change in
the build. `PL-M7W1`: its body half closes here; its subject half is
`PL-HMZZ`'s, whose part 3 retires the inference the squash subject exists to
feed, and the recommendation is written beside its own question. `PL-Y1W0`
stays closed. The form is recorded below, and each note says so.

**Decision needed, second round.** Whether the record takes this form: the
file under `docs/pr-bodies/`, the session's `--record` before the merge, the
`edited`-triggered required check, forward only. It is the owner's because it
adds a required step to every pull request and a file to the tree for each,
and because the backfill is a separate yes or no.

**Decided 2026-09-25: this form** (project owner, 2026-09-25, ratified, over
the same form with a backfill of the 714 unrecorded bodies, and over another
form). The build follows the recommendation above as written: the record is
`docs/pr-bodies/<N>.md`, written by the session with `--record` while its
pull request is open, held by a step in `pr-title.yml`'s required job, with
the squash body on `main` a derived copy; forward only, the backfill left as
its own decision. The members take the dispositions written above. The
build's touches are named under "What it costs" and are declared when it
starts. `PL-HMZZ`'s build landed in #1056 on 2026-09-26, and its writer and
check are what this rides; nothing holds this item now.

**Done when.** One of the two is recorded here as the answer, and each open member is re-scoped or closed against it.

**Generator check.** This is a head: `PL-WFFX`'s `misread:`, restated word for word so the two sort together, with three instances filed after `PL-WFFX` closed.
