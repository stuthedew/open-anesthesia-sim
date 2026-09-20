---
id: PL-205P
title: An item whose verify: reads the remote flips to passing with no commit, so main goes red for every commit until it is closed and no pull request can show it
priority: P2
effort: S
status: done
classes: defect, infra
feature: replay-hermeticity
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests, docs/items
added: 2026-09-20
closed: 2026-09-20
payoff: stops main going red - through a release cut, twice - for a finding no commit caused and no branch could have shown, while keeping the error on the case a commit does cause
verify: uv run pytest subprojects/docket/tests/test_verify.py subprojects/docket/tests/test_checks.py -q -k 'outside_the_tree or reported_apart or reads_the_remote or only_reads_the_tree_is_still' | grep -q '8 passed'
---

**Problem.** An item whose `verify:` reads the remote flips from failing to
passing with no commit at all. When it flips, `main`'s whole-store replay goes
red and stays red for every commit until somebody closes the item, and no pull
request can ever show it - because on the branch, at the moment the branch ran,
the command was still failing.

**The filed hypothesis was refuted, 2026-09-20.** This item was filed reading
the asymmetry as a scope bug: that `--verify-base` computes scope by diffing
against a base where a newly added item file does not exist, so an item the
branch *adds* is invisible to the pull-request replay. Two independent
measurements say otherwise.

- **Directly.** `git diff --name-only <base>...HEAD -- docs/items` lists added
  files like any other. A synthetic item added on a branch off `origin/main`
  with `status: ready` and `verify: true` was put through `bin/docket check
  --verify --verify-base origin/main`: `scoped to 1 item(s) this branch
  changed against origin/main`, and the command **exits 1** with `PL-9Z9Z is
  open but its verify: command already passes (1 of 1 checked)`. The branch's
  own check already fails in exactly the case the brief said it could not.
- **In the run this item was filed from.** `#744`'s `checks` job (run
  35484299201, head `2aebe030`) reports `verify: 18 commands in 16.6s (111.4s
  serially), scoped to 20 item(s) in scope: 8 this branch changed and 12 whose
  verify: command reads a file it changed against origin/main`. The branch
  changed exactly eight item files and `PL-66Z5` is one of them, so it **was in
  scope, and its command did run**. It did not report, because at 02:36 the
  answer was still "not done".
- **By that same pull request reddening itself, one push earlier.** Run
  35484029306, head `2f57de0b`, 02:30:14, **failed**: `PL-T2YR is open but its
  verify: command already passes (1 of 19 checked)`, on the same
  `20 item(s) in scope: 8 this branch changed` line. `git show 4bfcf00b
  --name-status` records `A docs/items/PL-T2YR-…md` - **the branch added that
  file too**. So the mechanism the brief says cannot work had already worked, on
  this very branch, six minutes before the run the brief cites as proof that it
  does not.

**What is actually happening.** `already_passing` reads exit 0 as a fact about
the tree. That holds only where the command is a function of the tree. Five
open-store items have carried a `verify:` that is not - each one reading
`git ls-remote` against `origin`, because the work they record is work only the
project owner can do and the remote is the only place it is visible:

| item | `verify:` | the work |
| --- | --- | --- |
| `PL-THPB`, `PL-XR8K`, `PL-6TQH`, `PL-8GQW` | `git ls-remote --tags origin vX.Y.Z \| grep -q …` | the owner pushes a release tag |
| `PL-66Z5` | `! git ls-remote --heads origin '<ten refs>' \| grep -q .` | ten superseded branch refs are deleted |

For those, the command's answer is a fact about the *world at the moment it
ran*. Nothing in any commit changes it, and no commit can fix it. `main` is
then red, and the commits it names are innocent.

**Both episodes are this, and neither is a scope failure.** Every red `main`
run in each cluster names one item, and `main` goes green on the commit that
closes it:

| span | red `main` commits | the finding, on every one | green again at |
| --- | ---: | --- | --- |
| `1f703f21` → `386cdf22`, 2026-09-19 22:32-23:12 | **6** | `PL-8GQW is open but its verify: command already passes` | `2863f4fa`, which closed `PL-8GQW` |
| `4bfcf00b` → `286da007`, 2026-09-20 02:37-03:06 | **4** | `PL-66Z5 is open but its verify: command already passes` | `a91f3d7a`, which closed `PL-66Z5` |

Read against the log rather than from memory, the filed account was wrong in
three places and they are corrected above: the first span was **six** commits,
not four; it followed the **v0.4.30** cut (`fe32c6ff`, 22:28:57), not v0.4.31;
and the sentence it attributes to `ROADMAP.md`'s v0.4.31 baseline section is
not in `ROADMAP.md` and never was - `git log -S` finds it only in this item.

`PL-8GQW` is the clearest case, because **no branch was involved at all**.
`#730` added it at 22:28:57 with the tag absent, so the command correctly
failed and `main` was green. The owner then pushed `v0.4.30`. From that instant
`main` was red, on six commits by five unrelated sessions, and the repository
had not changed. A scoped replay cannot cover a file no branch touched, and
widening the scope to the whole store would not have helped either: see below.

**The blunt fix was measured and does not work.** Running the whole-store
replay on `pull_request` too - the brief's second candidate, costed at 147.7 s
per run - would have prevented **neither** first red:

- `PL-8GQW`: the pull request whose merge went red first (`PL-5MT4`, run
  35472981960) ran 22:19:10-22:21:14, before `#730` had even added the file.
- `PL-66Z5`: its command ran on the branch **twice** - 02:30:14 and 02:36:27 -
  and failed both times, so the ten refs still stood at 02:36:27. `main`'s run
  began 02:37:09 and reached its replay some minutes later, by which time they
  were gone. Identical tree, identical command, opposite answers: the whole
  store would have answered exactly as the scope did.

It would have surfaced each within one *subsequent* pull request. That is the
honest benefit, and it is bought for 147.7 s on every pull request forever,
growing with the queue - re-buying precisely what `PL-P3B6` and `PL-SDHR`
removed. The number that would change this: it is worth it only if a
non-hermetic flip is common enough that catching it one pull request later
beats catching it on the next `docket check` a session runs. Five items in the
store's history have ever been non-hermetic, four of them the same release-tag
line, one per release.

**The project has already decided this question, on the other side of the same
window.** `ROADMAP.md`: "between cutting a release and pushing its tag the
newest version is Completed and carries none. That window is reported as an
advisory rather than an error: failing it would turn `make check` red on every
release branch." The `already_passing` finding is that identical window seen
from the far end - once the tag lands, the item is open with a passing command
until a session closes it. One end is an advisory by decision; the other fails
the default branch's required check. That inconsistency is the defect, not the
scope.

**What was built.** `verify.reaches_outside_tree` decides whether a recorded
command's answer depends on more than the tree, by `shlex`-tokenizing it and
looking for a network command word - `curl`, `wget`, `gh`, `ssh`, `scp`,
`rsync`, `nc`, or `git` immediately followed by `ls-remote`, `fetch`, `push`,
`pull` or `clone`. `already_passing` carries the matching ids in a new
`LandedReport.external`, subtracted from `blocked` because that clause's
certainty - "work nobody can start has not landed, so the command does not
discriminate" - does not survive a command the world can answer. `checks.py`
renders `external` as a **grooming advisory** and leaves everything else an
error exactly as before.

Wrong in the safe direction by construction: an unparseable command, and
anything the predicate does not recognize, reads as hermetic, so the finding
keeps today's severity and only a command the predicate is sure about is
softened.

**The trap it had to survive, and does.** The classifier reads the command
*being run*, not text inside it. `PL-K2C8`'s `verify:` is `grep -q 'git push
origin --delete' .claude/skills/docket/SKILL.md && …` - a network verb as a
**search string**, opening no socket. `shlex` collapses that quoted argument
into one token, so it never matches the bare `git` the scan looks for, where a
substring search would call it non-hermetic and silently downgrade a finding
that must stay an error. It is the only such case in the store and it is the
first regression test.

**What deliberately did not move.** A hermetic command that already passes is
still a hard error. That case *is* caused by a commit, and the scoped replay
already catches it on the branch - which is what reddened `2f57de0b` over
`PL-T2YR` before `#744` merged. Softening it would have thrown away the finding
the check exists for in order to repair a case it never covered.

**Done when** - met. An item whose `verify:` reads the remote and has flipped to
passing is reported where a session will act on it and does not fail `main`; an
item whose `verify:` is a function of the tree still fails as it does today;
and `subprojects/docket/tests/` drives both halves, the `PL-K2C8` shape
included.

**Do not re-derive the refutation.** The scoped replay covers added items. That
is measured twice above, and `git diff --name-only <base>...HEAD` is why.
