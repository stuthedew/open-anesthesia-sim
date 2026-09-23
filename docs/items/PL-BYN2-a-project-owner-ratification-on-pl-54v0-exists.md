---
id: PL-BYN2
title: A project-owner ratification on PL-54V0 exists only on origin/claude/upbeat-rubin-v1dktv, whose session has completed with no pull request open, so the one carrier of that decision is an unmerged branch
priority: P2
effort: S
status: done
classes: housekeeping
milestone: v0.5.6
touches: docs/items/PL-54V0-resumed-at-refuses-an-unkeyframed-instant-with.md
added: 2026-09-21
closed: 2026-09-22
pr: 925
payoff: the owner's ratification stops depending on one unmerged branch surviving, and the gate question it settles stays settled
verify: grep -qF 'project owner, 2026-09-21, ratified' docs/items/PL-54V0-resumed-at-refuses-an-unkeyframed-instant-with.md
---

**Problem.** A project-owner ratification on PL-54V0 exists only on origin/claude/upbeat-rubin-v1dktv, whose session has completed with no pull request open, so the one carrier of that decision is an unmerged branch

**Measured 2026-09-21.** `origin/claude/upbeat-rubin-v1dktv` holds one commit,
`cdbbb5bd`, whose subject records the owner's ratification of the `docs` class
on `PL-54V0`. `main`'s copy of that item contains no ratification. No pull
request is open anywhere in this repository. `bin/docket stranded` does name the
item as edited only on that branch, so the queue is not silent about it - but
the row reads like the five beside it that are merely stale copies (`PL-NPWP`),
and nothing distinguishes a branch carrying a decision of record from one
carrying nothing.

**Why it matters.** This is the failure `PL-KQHN` already cost the project once:
a decision the owner made survives only in a carrier that dies, and a later
session reconstructs it from whatever fragment is left. Here the carrier is a
branch with no pull request, on a forge that deletes merged heads and in a
container that is reclaimed. The ratification also does work no other sentence
does - it records that `docs` was chosen over `safety`, which is what keeps the
current milestone's gate from owing that item a disposition - so losing it does
not merely lose a note, it reopens a settled gate question with nothing to
settle it from.

**Done when.** The ratification is on the default branch's copy of `PL-54V0`.

**Closed 2026-09-22, by the stranded sweep that filed `PL-4CPP` as a duplicate
of this item without finding it.** That sweep's record follows, folded here.

**Where it came from.** `cdbbb5bd` on `claude/upbeat-rubin-v1dktv`, committed
2026-09-21 05:42 UTC by the `PL-Z3W6` session, eight minutes after that
branch's pull request `#844` merged at 05:33 UTC. The session had restarted the
branch on `main` and handed off; nothing took the commit. Four of its five files
were `pr:` backfills (`PL-Z3W6`, `PL-P757`, `PL-49R8`, `PL-Q664`) that `main`
already carries by another route. The one line `main` lacked was the kind of
`PL-54V0`'s classing decision: `(session, 2026-09-21)` on `main`, and on the
branch `(project owner, 2026-09-21, ratified, over classing it safety and owing
v0.5.0's gate a disposition for it)`.

**Why it was worth carrying.** `CLAUDE.md` makes that parenthesis the only
record of which kind of decision it was, and the plain form reads as a
session's call the owner never saw. The stale copy was also holding `PL-54V0`
out of triage: `bin/docket show PL-54V0` printed "Its file is already edited on
origin/claude/upbeat-rubin-v1dktv", and `PL-14QR`'s triage pass left it "to the
branch already editing it" - a branch nobody would merge.

**Carried verbatim, line breaks included,** so the two copies are
byte-identical and `stranded` reads them as equal instead of listing the branch
again.

**The rest of the 2026-09-22 sweep, and why nothing else was recovered.**

- `PL-23C7`, `PL-3XWZ` and `PL-8FJK`, listed as only on a branch, each sat on a
  branch with a running session: `claude/pl-4w2l-altitude-recommendation-63dkqj`,
  which merged as `#922` during the pass and brought `PL-23C7` to `main`;
  `claude/vigilant-archimedes-d2uyer`, the v0.5.5 cut; and
  `claude/magical-mccarthy-1dec89`, implementing `PL-8FJK`. Left alone.
- 21 of the 23 entries listed as edited only on a branch sat on those same live
  branches - the release cut's stamping and the altitude decision. Left alone.
- `PL-Q89J` on `claude/modest-galileo-2tkspg` and `PL-CJ5R` on
  `claude/blissful-mendel-ccad0y` are older copies: `main` closed both, with
  `#913` and `#818`. They read as ahead only because `main` later reworded a
  line the branch still holds verbatim. `_standing` in
  `subprojects/docket/src/docket/vcs.py` accepts that miss on purpose ("a copy
  wrongly called `_AHEAD` costs a reader one diff"), so it is not a finding.
- `claude/modest-galileo-2tkspg`'s copy of `PL-8FJK` is the one
  `claude/gallant-shannon-an6236` recovered at `2158cc78`, blob for blob, and
  every commit on `claude/gallant-shannon-an6236` is on
  `claude/magical-mccarthy-1dec89`.

**Outstanding, and the owner's to do: deleting four branches on the remote** -
`claude/upbeat-rubin-v1dktv`, `claude/blissful-mendel-ccad0y`,
`claude/modest-galileo-2tkspg` and `claude/gallant-shannon-an6236`. Once this
merges, none holds anything that `main` or a live branch lacks. Until they are
deleted, every `stranded` pass lists `PL-Q89J` and `PL-CJ5R` again, at one diff
read each.
