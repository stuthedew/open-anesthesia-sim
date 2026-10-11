---
id: PL-Y3GK
title: capture.md hands the project owner a bare git push origin --delete for a branch the branch sweep keeps that should go anyway, so the one deletion left to a hand is the only one that keeps no refs/archive copy, and no report names the non-item files such a branch may carry (found in PL-BYMX's design round)
status: untriaged
touches: .claude/skills/docket/modes/capture.md
added: 2026-10-11
---

**Problem.** capture.md hands the project owner a bare git push origin --delete for a branch the branch sweep keeps that should go anyway, so the one deletion left to a hand is the only one that keeps no refs/archive copy, and no report names the non-item files such a branch may carry (found in PL-BYMX's design round)

**Found in `PL-BYMX`'s design round, 2026-10-11.** That round closed `PL-BYMX`
on "nothing at all": `bin/docket stranded` keeps its item-keyed reading and
asserts nothing about the files a branch no pull request merged carries outside
the queue, because every narrowing of that comparison that is not noise comes
down to `tools/branch_sweep.py`'s own rule, and the sweep copies each branch it
deletes to `refs/archive/` first. That answer rests on a deletion being a
restore away. One deletion path is not.

`.claude/skills/docket/modes/capture.md`, in the paragraph opening "None of the
three deletes the branch on the remote; the branch sweep does.", has a session
name a branch to the owner only where `python3 tools/branch_sweep.py` keeps one
that should go anyway, with `git push origin --delete` for them to run. That
push removes the ref and copies nothing to `refs/archive/`. A branch the sweep
keeps is one some reading still holds - a lapsed claim holds one until its item
closes on the default branch or another session takes it over, since
`claims._finished_claim` reads a lapsed claim as unfinished - and the session
judging that it should go anyway has `stranded`'s item reading to go on and
nothing for the branch's other files. Where no pull request was ever opened from
the branch, no pull-request ref keeps its commits either.

**The likely fix, for triage to weigh.** Hand the owner the sweep's own push,
which copies and deletes in one transaction, leased on the tip it was judged at,
so that every deletion of a `claude/` branch, by the sweep or by hand, keeps an
archive copy, and the restore `docs/maintainer.md` § "Sweep branches now, or
restore one the sweep deleted" already gives covers both.

**The path has run once since the sweep started, and kept nothing**, read from
the sweep's 16 run logs (2026-09-26 to 2026-10-11) and `origin`'s refs on
2026-10-11. `claude/project-thread-qt3onr` was kept by every run from
2026-09-26 to 2026-10-03 on "unfinished work on PL-QMN0", and was gone before
the 2026-10-04 run with no `refs/archive/` copy. The sweep archived only
`claude/gifted-pasteur-iwimhy` in those runs, and GitHub deletes a head branch
only when its own pull request merges, where this branch's one pull request,
`#1127`, closed unmerged; so it was deleted by hand (inferred). Its work outside
the queue was `PL-QMN0`'s fix, which `#1138` dropped and recorded as kept at
`59ea9d1c`, `#1127`'s head, so nothing known was lost. Whatever it carried past
that head is no longer readable from here.

**Before the sweep, a hand deletion cost a queue record too**, so what this path
loses is not only the files outside the queue: once the ref is gone,
`stranded`'s item half has nothing to read either. `#1092` closed unmerged on
2026-09-26 carrying a measurement appended to `PL-X3NY`, and its branch,
`claude/cleanup-unused-branches-bcecxv`, was gone before the sweep's first run
that evening (20:21 UTC, ten `claude/` branches read). The sweep keeps a branch
for an edit to an open item that `main` lacks, so only a hand deletion could
have taken it. `refs/pull/1092/head` kept the paragraph, and `PL-BYMX`'s design
round restored it to `PL-X3NY` on 2026-10-11.
