---
id: PL-QHCW
title: No record says which commit a release was cut on: release.md hands the owner a tag placed by hand from a moving ref, and each reader then takes the tag for the cut - six items, three open
priority: P2
effort: M
status: needs-decision
classes: defect
feature: release-process
touches: .claude/skills/docket/modes/release.md, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_release.py, subprojects/docket/tests/test_cli.py, tools/doc_check.py, tests/unit/test_doc_check.py, ROADMAP.md, docs/items/PL-NZC0-a-claude-code-projects-trial-needs-project.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed as a generator head
added: 2026-09-23
payoff: The commit a release was cut on becomes a recorded fact, so the tag and its readers stop disagreeing
root-cause-of: PL-VYK1, PL-6YYR, PL-KFWL, PL-BKDP, PL-YKSD, PL-6SV4, PL-53Y6
generator: live - release.md:191 still hands the owner git tag -a from origin/main and cli.py:2694 prints an unfilled MERGE_COMMIT, so no record says which commit a cut was made on; three members are open
misread: Which commit a release was cut on, if it was cut at all
---

**Problem.** No record says which commit a release was cut on: release.md hands the owner a tag placed by hand from a moving ref, and each reader then takes the tag for the cut - six items, three open

**Found 2026-09-23** by `PL-T7Y1`'s generator audit. It came up in the inflow
sweep and survived three skeptics, and no recorded head covers it.

**The mechanism.** A release is recorded in the tree by the cut: the
`pyproject.toml` version, `docs/releases/` notes and the `ROADMAP.md` version
row. It is recorded outside the tree by a tag the owner pushes by hand. The
handover is `git tag -a v0.3.0 origin/main` (`.claude/skills/docket/modes/release.md:191`),
and `cli._hand_off` (`cli.py:2694`) prints an unfilled `MERGE_COMMIT`. So the
tag lands wherever `origin/main` has moved to by then. Each reader then takes
the tag for the cut:

- `_check_tag_versions` (`tools/doc_check.py:2891`) compares only the version
  at the tag.
- `cli._untagged_warning` (`cli.py:2827`) greps `Release vX.Y.Z`, which no
  v0.4 or v0.5 cut subject matches.

**Members.** `PL-VYK1`, `PL-6YYR` and `PL-KFWL` (open, ready); `PL-BKDP`,
`PL-YKSD` (done); `PL-6SV4` (dropped). `PL-6SV4` reproduced the state on
2026-09-23.

**Why it matters.** Every tag since v0.4 has been read against a cut it may not sit on, and a later commit that declares the same version passes `_check_tag_versions`. So a wrong tag is silent, and nothing but a person checking by hand catches it.

**Decision needed.** Record the cut commit when the cut merges (the squash sha, read back by the cut's own close-out), or keep the hand-placed tag and close this head spent? Recommendation: record it, because three members are open and every one re-derives the same missing fact.

**The owner's direction, 2026-09-23.** In their words: "I'd rather fix it right once, then fix it twice" (project owner, 2026-09-23). Against this
decision it rules out keeping the hand-placed tag and closing this head spent.
The design round decides where the cut commit is recorded, then makes the tag
and every reader of it use that record. Reading the direction this way is this
session's call, so ordinary evidence reopens it.

**Recommendation, 2026-09-25 (this session's, marked; waiting on the owner's
answer). Record nothing new: define the cut commit from the tree, in one
function, and make the tag block and every reader of it use that definition.**

*The definition.* A release's cut is the first-parent commit on the default
branch that added `docs/releases/vX.Y.Z.md`. The merge writes that fact at the
moment it happens, so nothing has to be written at a moment nothing can write:
the squash sha does not exist until the merge, which is what defeats every
"record it at the cut" shape. `tools/doc_check.py`'s `_tag_spans` already reads
the cut this way - the commit that *added* the notes file, "deliberately not
inferred from the subject line" - so the definition is adopted rather than
invented. It moves into one function in `docket.release` that `_tag_spans`,
`_check_tag_versions`, `cli._hand_off` and `cli._untagged_warning` all call;
`tools/doc_check.py` already imports `docket` for `GitRunner` and `tags`, so no
new dependency. First-parent, because the five merge-commit tags of the v0.2.x
era sit on the merge, not on the branch-side commit inside it, and
`_tag_spans` reads without it today. A notes file added twice yields two
commits, and the function declines rather than picking one: an ambiguous cut
is a question, not an answer.

*Counted before it was recommended.* Measured 2026-09-25 on a full clone
(`git rev-parse --is-shallow-repository` false; 74 `vX.Y.Z` tags on `origin`):

- 68 tags have a notes file, and all 68 sit exactly on the first-parent commit
  that added it: 63 squash commits from v0.2.8 on, and five merge commits,
  v0.2.3 to v0.2.7, which match only under `--first-parent`. The other six,
  v0.0.1 to v0.2.2, predate release notes and are untouched by the new check.
- The version-bump definition `PL-6SV4` tried, `git log -S'version = "X.Y.Z"'
  -- pyproject.toml`, matches 66 of 74 and loses v0.2.0, the stale-version
  exception. The notes file is the one artifact only a cut writes, and it is
  what `_tag_spans` reads, so the tag check and the span check name one commit.
- Since v0.3.0, 58 tags. For 8 of them - v0.3.0, v0.3.3, v0.3.5, v0.3.7,
  v0.3.8, v0.3.9, v0.4.32 and v0.5.8 - `origin/main` had already moved past
  the cut, by one to six commits, when the tag was placed. Every one still
  landed right, and the block cannot claim credit: whether `git tag -a vX.Y.Z
  origin/main` tagged the cut depended on when the owner's fetch ran, and a
  later commit still declaring the version passes `_check_tag_versions`, so a
  miss would have been silent. That is the exposure, 8 of 58, and it is closed
  below.

So the tightened check fails nothing on `main` at its first run, which is the
count `PL-YKSD` learned to take before turning a check on.

*What each consumer becomes.*

1. **The tag block** - release.md's, and the one `cli._hand_off` prints - names
   the cut by the definition rather than by `origin/main` or `MERGE_COMMIT`:

   ```bash
   git fetch origin main
   git tag -a v0.5.12 "$(git log --first-parent --diff-filter=A --format=%H origin/main -- docs/releases/v0.5.12.md)" -m "v0.5.12"
   git push origin v0.5.12
   ```

   The same three lines tag the same commit whenever they are run, which is
   `PL-VYK1`'s Done when. Run before the merge, the lookup is empty and `git
   tag` stops on `Failed to resolve ''` before anything is pushed - the
   refusal `PL-6YYR` (c) asked for, in the command rather than beside it. And
   `_hand_off` can print it before the pull request exists, the constraint
   `PL-6SV4` recorded against a `(#N)` lookup. The printed line is rendered
   from the function's own git arguments, so the block and the Python readers
   cannot disagree about the rule. After the merge the session pastes the
   block and shows the resolved sha and subject beside it, so the owner sees
   what will be tagged before running it.
2. **`cli._untagged_warning`** resolves the untagged release's cut through the
   function and prints its sha and subject, replacing the `--grep="Release
   vX.Y.Z"` line that matches no cut since v0.3.x.
3. **`tools/doc_check.py`'s `_check_tag_versions`** holds each tag that has a
   notes file to the cut commit, not only to the version: a tag pointing
   anywhere else is an error naming the tag, the commit it points at, the cut
   commit with its subject, and the repair. The version comparison stays for
   the six tags with no notes file, and the v0.2.0 stale-version sentence is
   untouched. `_tag_spans` takes its `cut` from the same function. One test,
   `test_a_tag_ahead_of_its_own_cut_is_named` - `PL-KFWL`'s own `verify:` -
   on a fixture whose tag sits one commit past the notes-add and still
   declares the version, refused by name.
4. **`ROADMAP.md`'s Tags statement** says the tag goes on the commit that added
   the release's notes file, which `tools/doc_check.py` holds it to, in place
   of "on the merge commit".

*Why not the other shapes.* A `cut:` field on the release item, written by
`docket record` after the merge the way `pr:` is, exists only once somebody
runs `record`, which is after the tag needed it; it is recomputable from the
tree, which is the digest's dead end against a committed index; and it is a
copy free to drift, `PL-YKSD`'s own reason for not reading the tag a second
time in `bin/docket release`. A line in the notes file or in the roadmap row
has the same timing gap. A GitHub Release object is outside the tree.

*Considered, and not recommended now: CI placing the tag.* A workflow on push
to `main` that tags the commit adding a new notes file would remove the hand
step entirely. This route does not foreclose it - it would reuse the
definition, the check and the warning and replace only the printed block, and
nothing stored depends on the choice, so taking the block first is not a loan.
It is not taken now because whether a `GITHUB_TOKEN` tag push is permitted
here is unverified (`PL-N936` is the session-side failure; the runner is
another path), and because it removes a step the owner does by hand rather
than fixing what that step reads, which is more than this head asks.

*Build scope: one thread, one pull request.* `docket.release` for the
function, `cli.py` for both printers, `tools/doc_check.py` for the check and
the spans, release.md and `ROADMAP.md`, with the two tests named. It closes
`PL-VYK1`, `PL-KFWL` and `PL-6YYR` - the last on clauses (b) and (c), with
(a), a second refusal inside `bin/docket release`, recorded as declined for
`PL-YKSD`'s reason - and `PL-LRM0`, whose `verify:` passes once those two are
no longer both `ready`. The commit closing them leads with all four ids.
`touches` above is widened to that footprint now, so `bin/docket concurrent`
answers for the build. Once it merges, `generator:` reads spent: the block and
both readers name the cut, so nothing hands this head another member. Effort
M as filed; nothing here reaches the simulator.

**Decided (project owner, 2026-09-25, ratified): the recommendation above -
derive the cut from the notes file's first-parent add and make the block and
every reader use it - over a `cut:` field written after the merge, and over
CI placing the tag.** The owner's words: "Agree with recs". Ratified rather
than specified, so ordinary evidence reopens it. The build is Stream B's
PL-QHCW build thread; the status stays `needs-decision` here because the
design round was instructed to change none, and the build's first commit
moves it.

**Done when.** The commit a release was cut on is recorded when the cut
merges, and the tag and its readers use it. Or the owner decides the hand-placed
tag stays, and this head is closed spent with that recorded. It is a design
question, and while an open item carries `generator: live` any new check waits.

**Moved out of the trial (project owner, 2026-09-26, ratified, over leaving
it to Stream B and over building `PL-VYK1`'s part alone).** The owner named
`PL-VYK1` in their own session; this build closes it, so it is built there,
on `claude/focused-davinci-dklbov`, under a claim on this item and all four
members. `PL-NZC0` records the Stream B change. A half-build was declined
because it writes the shared function and leaves the `doc_check` half, so the
head stays live and Stream B still owes a thread.

**Build plan, 2026-09-26 (this session; the design above, refined before any
code).** Re-confirmed against `96287589`: the tag block is now
`release.md:233`, `cli._hand_off` is `cli.py:3457` with `MERGE_COMMIT` at
`:3495`, `cli._untagged_warning` is `cli.py:3715` with the `--grep` line at
`:3728`, and `tools/doc_check.py` has `_check_tag_versions` at `:2799` and
`_tag_spans` at `:2917`.

*One refinement, measured: no reader runs the lookup from a branch's `HEAD`.*
A branch that has merged the default branch in has its own merge commit on
its first-parent line, and that merge added the notes file compared with its
first parent. On a scratch branch forked at `fe2046f7^` that merged
`fe2046f7`, `git log --first-parent --diff-filter=A HEAD --
docs/releases/v0.5.11.md` named the branch's merge `4308874b`, not the cut
`fe2046f7`. Read from `HEAD`, `doc_check` would fail `make check` on every
branch that brought `main` in after a release. So the printed block reads
`origin/main`, and `doc_check` reads the tags themselves. A tag sits on its
cut when its own commit added its own notes file, compared with its first
parent: the same definition, applied to named commits. One read covers every
tag: `git log --no-walk --first-parent --diff-filter=A --format=%x00%H
--name-only <tag commits> -- docs/releases`. It took 11 ms for 74 tags, against
1.29 s for one lookup per tag, and it reproduced the count above: 68 on their
cut, 0 off it, 6 with no notes. The per-tag lookup from the tag's own history
runs only for a tag that fails, to name the cut in the error.

*Where it lives.* The definition is pure and goes in `docket.release`:
`notes_path`, `CUT_FLAGS = ("--first-parent", "--diff-filter=A")`,
`cut_query(version, ref)` and `tag_commands(version, remote, branch)`.
`tag_commands` renders the printed line with `shlex.join` from `cut_query`.
The git reads go in `docket.vcs`: `find_cut(version, ref, root, runner)`
returns a `Cut(commits, read)` whose `.commit` is empty unless exactly one
commit is named, and `notes_added(commits, root, runner)` is the batch read.
`vcs` imports `release`, so `release` cannot run git without closing the
cycle.

*Consumers.*
1. `cli._hand_off` prints `tag_commands(name)`: fetch, the `"$(git log
   ...)"` tag line, and push.
2. `cli._untagged_warning(version, root, git)` prints the same three lines.
   Under them it names the commit the lookup resolves to here, from
   `default_base`, with its short sha and subject. If it resolves to nothing,
   or to more than one commit, it says so.
3. A `doc_check` helper `_release_cuts(root, names, run)` holds each release
   tag whose notes file is in this tree. `_check_tag_versions` reports a tag
   off its cut by name: the tag, its commit, the cut from the tag's own
   history with its subject (or that none is in it), and the `git tag -d`
   caveat. Only then does it skip the version error for that tag. Tags with
   no notes keep the version check alone, and a shallow or silent read is
   declined. `_tag_spans` takes `cut` from the same helper, in place of its
   own `--diff-filter=A HEAD` read.
4. The `release.md` block and `ROADMAP.md:135`'s Tags statement ("The tag
   goes on the merge commit") say the tag goes on the commit that added the
   release's notes file.

*Tests.*
- `test_release.py`: the printed commands, run by a shell in a clone,
  tag the cut however late they run and refuse before the merge.
- `find_cut` names nothing for an absent notes file and declines one
  added twice.
- `test_cli.py`: the hand-off assertion at `:2248`, and the untagged
  warning naming the cut.
- `test_doc_check.py`: `test_a_tag_ahead_of_its_own_cut_is_named`, which is
  `PL-KFWL`'s `verify:`; a tag behind its cut; and a tag on its cut quiet on
  a branch that merged `main` in.

*Members at close.*
- `PL-6YYR`'s clause (a), a second refusal inside `bin/docket release`, is
  declined for `PL-YKSD`'s reason: a second copy of the tag read is free to
  drift. Its `verify:` names that clause's test, so it is rewritten to (b)
  and (c).
- `PL-LRM0` passes once `PL-6YYR` and `PL-KFWL` are no longer both
  `ready`.
- The closing commit leads with all five ids, and `generator:` reads spent.
