---
id: PL-WDQN
title: bin/docket stranded's left-behind half counts a ref whose fork point the checkout cannot read among the refs it read, and names it nowhere: vcs.orphaned fills OrphanedReport.unreadable and format_orphaned never prints it, so in a shallow clone an unread branch sits under the all-clear (found working PL-CZR6)
status: untriaged
feature: stranded-report-fidelity
added: 2026-10-11
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

**Done when.** The left-behind half does not count a ref it could not read as
read, and names each one with what would let it be read, as `flight`'s unread
line does. A test in `subprojects/docket/tests/test_cli.py` drives a shallow
clone holding a branch whose fork point it lacks.
