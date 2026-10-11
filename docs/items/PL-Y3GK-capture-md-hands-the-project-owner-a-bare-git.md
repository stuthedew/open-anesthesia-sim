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
restore one the sweep deleted" already gives covers both. How often a session
has handed the owner this command since the sweep started on 2026-09-26 was not
measured.
