---
id: PL-WDQN
title: bin/docket stranded's left-behind half counts a ref whose fork point the checkout cannot read among the refs it read, and names it nowhere: vcs.orphaned fills OrphanedReport.unreadable and format_orphaned never prints it, so in a shallow clone an unread branch sits under the all-clear (found working PL-CZR6)
priority: P2
effort: S
status: done
classes: defect
feature: stranded-report-fidelity
milestone: v0.5.24
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-11
closed: 2026-10-12
pr: 1431
payoff: stranded stops printing its all-clear over a branch it could not read, so a shallow clone names the unread ref and what would let it be read instead of counting it as checked
verify: grep -q 'def test_stranded_names_a_ref_whose_fork_point_a_shallow_clone_lacks' subprojects/docket/tests/test_cli.py
reenters: PL-9RFP
---

**Problem.** bin/docket stranded's left-behind half counts a ref whose fork point the checkout cannot read among the refs it read, and names it nowhere: vcs.orphaned fills OrphanedReport.unreadable and format_orphaned never prints it, so in a shallow clone an unread branch sits under the all-clear (found working PL-CZR6)

**Reproduced 2026-10-11 on real git**, with `PL-CZR6`'s line in place. A source
repository forks `claude/old-work` from `main` with one commit, and `main` then
takes four more. A `git clone --depth 1 --no-single-branch` of it holds
`origin/claude/old-work` but not its fork point. `vcs.orphaned` on that clone
returns `refs_read=1` and `unreadable=('origin/claude/old-work',)` with no
branches and no decline. `bin/docket stranded --no-fetch` then prints "No branch
carries work its own pull request left behind, judged by file content across the
1 unmerged branch ref read." The one ref it counts as read is the one it could
not read.

**Re-confirmed 2026-10-11** on main at `16a20a4f`: a depth-1
`--no-single-branch` clone of a scratch source gives `refs_read=1`,
`unreadable=('origin/claude/old-work',)` and no branches, and
`format_orphaned` prints the all-clear "across the 1 unmerged branch ref
read".

**Where.** `vcs._unlanded_refs` puts a candidate whose fork point `_Landings`
cannot resolve into `unreadable` instead of reading it, and `orphaned` returns
`refs_read=len(refs.candidates)`, which still counts it. `render.format_orphaned`
reads `known`, `declined`, `refs_read`, `branches` and `rewritten`, and never
`unreadable`. Nothing else prints that field either: the digest's left-behind
line reads `branches` alone. `OrphanedReport`'s docstring says `unreadable` is
there so "a clean answer from a container holding two refs is not mistaken for
one from a checkout holding twenty". The item half reads each ref's tree by id,
which needs no fork point, so the gap looks confined to this half; that was read,
not tested.

**Why it matters.** It breaks the apparatus floor
(`.claude/rules/apparatus-standard.md`): a partial reading handed over as a
complete one. A shallow clone is how an agent container starts. The session-start
digest deepens it, so the shape is rare once the hook has run, but `stranded` is
the command every reply's refresh runs, and nothing on the page says when it
read less than it counted.

**Generator check.** An instance of `PL-9RFP`'s fact, whether a git read
answered or failed, filed after that head closed on 2026-09-23: the fork-point
read failed, `vcs.orphaned` names the ref in `unreadable`, and `refs_read` and
`format_orphaned` count it as answered. The shape, a caller dropping a decline
its reader names, is the one `PL-JTP1` (open) proposes to make a type error
for six of `PL-R417`'s members; this is a seventh outside that head, since no
statement here continues across lines.

**Done when.** The left-behind half does not count a ref it could not read as
read, and names each one with what would let it be read, as `flight`'s unread
line does. A test in `subprojects/docket/tests/test_cli.py` drives a shallow
clone holding a branch whose fork point it lacks.

**Done 2026-10-12** (`#1431`). `vcs.orphaned` now leaves a ref with no
readable fork point out of `refs_read`, which the all-clear counts, and asks
`is_shallow` only where such a ref exists. `render.format_orphaned` names each
one under its answer, in the clear case and the finding one, with what would
let it be read: `git fetch --unshallow origin` in a shallow clone, and in a full
one the fact that no fetch helps, since a ref there with no fork point shares no
history with the base (a rewrite or an unrelated root, the case `branch_state`
once handed the deepening advice). Pinned by
`test_stranded_names_a_ref_whose_fork_point_a_shallow_clone_lacks` (a depth-1
`--no-single-branch` clone, red on main's code) and
`test_stranded_hands_no_fetch_to_a_ref_a_full_clone_cannot_compare` (an orphan
branch in a full clone, red on main's code) in
`subprojects/docket/tests/test_cli.py`, and `refs_read == 0` beside the unread
ref in `subprojects/docket/tests/test_vcs.py`. The digest needed nothing: its
flight line already names the same refs, read by the same `_unlanded_refs`.
`subprojects/docket/README.md` says what the answer does with such a ref.
