---
id: PL-3CTW
title: A commit that leads with a captured id and also reaches outside the queue claims that id, so a finding filed alongside another item's work reads 'do not start these again' for the life of the branch
priority: P2
effort: S
status: done
classes: defect
touches: subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-19
closed: 2026-09-19
verify: grep -q 'def test_the_digest_sends_an_unlanded_claim_to_stranded_rather_than_refusing_it' subprojects/docket/tests/test_vcs.py
---

**Problem.** A commit that leads with a captured id and also reaches outside the queue claims that id, so a finding filed alongside another item's work reads 'do not start these again' for the life of the branch

**Observed 2026-09-19, and it cost the opening of a session.** The session
started on `PL-RY2R` and `PL-61MD` read in its own start-up digest: `In flight
on a branch: PL-2BZY, PL-61MD, PL-6P9Y, PL-HWW1, PL-RY2R - do not start these
again`. Both were startable. They had been *filed* on
`origin/claude/tender-keller-omy3ec` by commit `6d2298a`, whose subject is
`PL-RY2R, PL-61MD: file the two remaining collapses, and name the group` and
whose diff also carries `PL-2BZY`'s 159-line `vcs.py` implementation.

**Mechanism.** `leading_ids` reads every id at the front of the subject and
`_annotates_only` withholds the claim only where the *whole* diff sits inside
the queue. A commit that files a finding while implementing something else
satisfies neither test: it leads with the captured ids, and its diff reaches
`src/`. So both captured ids are credited as work in flight.

This is `PL-X3WZ`'s harm through the opposite door. That item stopped a
queue-only commit being read as work; this is a work commit being read as a
claim on the ids it merely captured. `CLAUDE.md` makes both halves mandatory -
capture before the session ends, and lead every subject with its ids - so the
collision is produced by following the rules rather than by breaking them, and
it fires on exactly the commits whose purpose is to hand work to a later
session.

**What it costs.** The mark's whole job is to stop two sessions on one item.
Here it withholds an item nobody holds, for as long as the branch lives, and
`bin/docket next` excludes it under the strongest wording the tool has. A
capture is the one commit shape that should never claim anything.

**A candidate mechanism, not yet a decision.** `_deciding_on_base` and
`_queue_only_work` both answer a question of this kind by asking the *base*
rather than the commit, and the base separates these two cases cleanly: an id
the base does not hold at all is one this commit is filing, because a capture
creates the file. So a leading id whose item the base has no copy of could be
read as captured rather than claimed, independent of what else the diff
touched. That needs counting against the store before it is adopted - how many
historical claims it would withdraw, and whether any of them were real work on
an item whose file had not yet merged - which is the measurement this item owes
and the reason it is not a fix-now.

**Not fixed in the session that found it**, per `CLAUDE.md`'s fix-now door: it
needs a new regression test, so the first test fails outright.

**Measured 2026-09-19, and the candidate above is refuted.** Replayed over the
1,024 commits reachable from `origin/main`, with each commit's own first parent
standing in for the base - the substitution `_modified_by` already makes for
this question. 522 of them lead with an id and reach past the queue, carrying
913 `(commit, id)` claims between them. The candidate withdraws **263 of the
913**, and **221 of those 263 (84%) are not captures at all**: the item file
they create stands at `done` (177), `dropped` (26), `ready` (9),
`needs-decision` (8) or `blocked` (1), which is an item filed *and finished* on
one branch. That is not a rule being broken but three of this project's own
rules being kept - `CLAUDE.md`'s housekeeping rule ("file the item first, then
work under its id"), its behavior-change rule ("record it like any other
finding and then make the edit before the session ends"), and its fix-now door
each produce a branch whose item the base has never held. Withdrawing their
claims reintroduces `PL-PRHN`'s more expensive error, two sessions on one piece
of work, across 221 commits in order to clear a false mark from 22.

**The obvious narrowing is refuted too, and by a thinner margin than it
looks.** Add the item's own status, read from the branch's copy, so that a
leading id is read as *filed* only where the base lacks it **and** the branch
still calls it `untriaged`. That withdraws 22 of the 913 - and **12 of the 22
are commits that did the item's own work**, their non-queue diff landing inside
the item's declared `touches`. `PL-M2SD` (#670) filed its item and shipped
`tools/generator_check.py` with it, never triaging it; `PL-1T6T` (#624),
`PL-2XM2` and `PL-N936` did the same to `CLAUDE.md` and the `docket` skill. A
session that files a finding and fixes it in the same breath has no reason to
triage what it is about to close, so `untriaged` does not mean "nobody is
working this".

**And no `touches`-based discriminator can work either, which the motivating
case settles on its own.** `6d2298a`'s non-queue diff is `vcs.py`, and `vcs.py`
is the first path `PL-RY2R` declares in `touches` - so the overlap test that
separates the twelve above reads this capture as real work as well. A capture
riding another item's work, and an item filed and worked on one branch, are
indistinguishable from the commit, from the item, and from the diff between
them. What separates them is intent, and the repository records no intent.

**A correction to this item's own cost statement.** `bin/docket next` does not
exclude a base-absent id. It filters the items its own store holds
(`subprojects/docket/src/docket/render.py:210`), and an item whose file has not
merged is in no other session's store to be filtered; the digest's line is the
unconditional one, printing `flight.ids` whatever the store holds
(`render.py:381`). So the harm splits in two, and only the later half reaches
`next`:

- **Before the capture merges**, the digest alone names the id, under "do not
  start these again" - while `bin/docket stranded` names that same branch as the
  place to recover the item from. Two commands, one branch, opposite advice.
  That is what cost the opening of the session on 2026-09-19.
- **After the capture merges by another route**, the item is on the base and
  `next` does exclude it. A squash merge leaves none of the branch's commits
  reachable from `main`, so the capture commit stays unmerged indefinitely, and
  `_taken_on_base` does not spend the claim because the squash subject led with
  the *implementing* item's ids and never with the captured ones.

**What is left is a decision, not another measurement.** The claim cannot be
withdrawn soundly at any width tested, so the route that remains does not
withdraw it: keep every claim, and report an id whose item the base has no copy
of as what it is - filed on a branch and not yet merged, which is the same
branch `stranded` already points at - rather than as work not to start. It
takes nothing away, so it cannot reintroduce two sessions on one item, and it
fails toward the mark in the direction `_annotates_only` and `PL-PRHN` both
chose. That is a different mechanism at a different layer from the one this
item describes, so it is the project owner's to approve under `CLAUDE.md`'s
gate rather than a session's to substitute.

**Decided: keep every claim, and re-word the report for an id the base has no
copy of** (project owner, 2026-09-19, ratified) - chosen over dropping this item
with the refutation as its reason and leaving the digest contradicting
`bin/docket stranded`. The withdrawal this item was filed to propose is refused
at all three widths measured above; nothing is taken away, so the mark keeps
failing in the direction `_annotates_only` and `PL-PRHN` chose, and what changes
is only what the reader is told about an id whose item is not in their store.

**Why it matters.** The mark exists to stop two sessions landing on one item,
and on a base-absent id it cannot do that job: no other session's store holds
the item, so nothing can offer it and nothing needs withholding. What the mark
does instead is tell a session not to start the very item `bin/docket stranded`
is telling it to recover, on the one commit shape - a capture - whose whole
purpose is to hand work to a later session. It fires on rule-following
sessions and it fires hardest at the moment of handover.

**Done when.** An id claimed only by a commit that filed it, whose item the
base does not hold, is reported by the digest in terms a reader can act on
without contradicting `bin/docket stranded`; every claim currently raised is
still raised; and a regression test pins the digest's wording for a base-absent
id against a live in-flight claim on an id the base does hold.
