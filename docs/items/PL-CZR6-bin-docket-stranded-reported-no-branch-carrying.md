---
id: PL-CZR6
title: bin/docket stranded reported no branch carrying work its own pull request left behind while claude/sharp-lamport-t545rs carried two PL-X5PK commits pushed an hour after #823 squash-merged from it
priority: P2
effort: S
status: done
classes: defect
feature: stranded-report-fidelity
touches: subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md
added: 2026-09-21
closed: 2026-10-11
pr: 1401
payoff: bin/docket stranded stops calling every branch clear on a content reading the exact check contradicts: its last line says what it read and where the exact answer is
verify: grep -q 'def test_the_left_behind_clear_line_names_the_exact_check' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket stranded reported no branch carrying work its own pull request left behind while claude/sharp-lamport-t545rs carried two PL-X5PK commits pushed an hour after #823 squash-merged from it

**Re-measured 2026-09-21.** `bin/docket stranded` again closed with the line
saying no branch carries work its own pull request left behind, across 16
unmerged branch refs. The branch this item names is gone from the remote now, so
the original instance cannot be replayed; what stands is that the read reports
nothing on a checkout holding 16 unmerged refs, beside `PL-NPWP` recording the
item half of the same command reporting five refs that no longer exist.

**Why it matters.** This is the half of `stranded` built to catch what a squash
merge leaves behind, which is the shape this project's history keeps producing:
the pull request closes, the forge deletes the head branch, and anything pushed
to it after the merge is reachable only from a ref nobody will fetch again. A
reader told nothing is behind has been given the strongest possible claim on the
weakest possible evidence, and no second check anywhere would contradict it.

[superseded 2026-10-11: the exact check answers this, as the next paragraph says]
**Done when.** A commit pushed to a branch after that branch's own pull request
merged is named by the `orphaned` read together with the command that recovers
it, and a test in `subprojects/docket/tests/test_vcs.py` drives that sequence.

**Re-pointed at `tools/left_behind_check.py`, 2026-10-11 (`PL-2C53`).** This
item's question is that check's own, and it answers it wherever GitHub answers.
It reads each branch tip on `origin` against the `refs/pull/<n>/head` its
newest pull request merged at, and names the commits past that head which the
default branch lacks, comparing no content, so a squash against a base that
moved underneath cannot confound it. It runs at every session start
(`.claude/hooks/docket-digest.sh`), and `tools/branch_sweep.py` keeps any branch
it reports, so such a commit is named by the next session's digest and is
never swept. That is the second check the paragraph above says nothing offers.
So no further content reading in `vcs.py` is owed for this shape.
`_commits_by_landing` records `orphaned`'s two silences on it as trades taken
deliberately: a branch whose pre-merge commits were all re-merged against a
moved base, and one whose only wholly landed commit is a queue write. The exact
check is the answer those silences defer to.

**What is still this item's: the line `stranded` prints.** Reproduced
2026-10-11 on a scratch repository. A branch edits `F.txt`, the base edits
another line of it, and the branch squash-merges as `#1`. Then a commit adding
`H.txt` is pushed to the branch. `vcs.orphaned` reports nothing, and
`format_orphaned` prints "No branch carries work its own pull request left
behind, across the 2 unmerged branch refs read." Handed `#1` as merged at the
branch's head before that push, `left_behind_check.examine` names the commit,
and its digest line says "vcs.orphaned does not report it, and this ref
comparison wins". So `bin/docket stranded`, which every reply's refresh runs,
still prints the sentence this item was filed against as a clean result while
the exact check reports the commit. The digest's line does not answer a defect
in what `stranded` prints.

**Done when.** `bin/docket stranded`'s closing line for this half no longer
states a clean result on the content comparison alone. It says the reading
compares content and names `python3 tools/left_behind_check.py --all` as the
exact answer, or carries that check's answer where it can be read. A test in
`subprojects/docket/tests/test_cli.py` pins the line. No new content test in
`vcs.py` is part of this.

**Done 2026-10-11: the check is named, not run.** Re-confirmed first: on real
git, a branch whose work squash-merged against a base that edited another line
of the same file, then took a commit adding `H.txt`, still drew the bare
"No branch carries work its own pull request left behind, across the 1 unmerged
branch ref read." That line now reads "... left behind, judged by file content
across the 1 unmerged branch ref read.", and the line under it says "File
content can miss a commit pushed after the merge:" and then names
`python3 tools/left_behind_check.py --all` as the exact answer, which wins
where the two disagree. When the half finds work, its list closes on the same
sentence instead of "reported by nothing else", which stopped being true when
`PL-R808` built that check. The README's section on this half says the same.

Of the Done-when's two routes, this took naming the check over carrying its
answer. Carrying it would put a GitHub call and a token behind `stranded`, the
command every reply's refresh runs, and need a new `docket.toml` command
setting to reach a repository script. The session-start digest already runs the
check, and `tools/branch_sweep.py` keeps every branch it reports, so what
naming leaves out is a push made after this session's digest ran, which the
named command answers when it is run. `docket` already names a repository
script this way, as `release.TAG_SCRIPT`.

`test_the_left_behind_clear_line_names_the_exact_check` drives the shape above
and pins both lines, and fails on the old line. The finding case's sentence is
pinned in `test_stranded_reports_a_commit_pushed_after_its_pull_request_merged`.
Found working this, filed as `PL-WDQN`: the same line counts a ref whose fork
point a shallow clone lacks among the refs it read, and never names it.
