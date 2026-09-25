---
id: PL-TKFD
title: A session that discovers mid-work that its work falsifies an assertion cannot declare falsifies: on the base, so verify --self has no clean route for the case the field was built for
priority: P3
effort: M
status: needs-decision
classes: infra
feature: verify-close-out
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-17
---

**Problem.** A session that discovers mid-work that its work falsifies an assertion cannot declare falsifies: on the base, so verify --self has no clean route for the case the field was built for

**Found 2026-09-17** building `PL-K82G`, and it is that field's known residual
cost rather than a defect in it.

`docket verify` reads `falsifies:` from the **base's** copy of the item, which is
what makes the declaration the commission's rather than the worker's - the
property `PL-K82G`'s own case rests on, and one its stated guard
(`front_matter_check`) could not hold, because that guard is an advisory in
`--self` by design.

The cost is at the other end. A session that discovers *mid-work* that its work
falsifies an assertion cannot put the declaration where `verify` reads it: it
cannot merge to `main` itself, so the only copy it can write is on its own
branch, where the fold correctly ignores it. It is then back where `PL-K82G`
started - a red integrity check on correct work, talked past in a reply.

**What is already better**, and why this is P3-shaped rather than urgent: the
`REJECT` now says exactly what happened and what the route is, where before it
said only that an assertion was removed. A session meeting it has something to
put to the project owner rather than a judgement call to rationalise. So this is
friction on a rarer path, not a silent wrong answer.

**Why it matters.** The declaration only lands in the commission if somebody
writes it at triage, which means noticing at triage that an item's work will
falsify a test - a harder thing to see than it looks, and not something triage is
currently asked to do. If most real cases turn out to be mid-work discoveries,
the field's coverage is much smaller than `PL-K82G` assumed and the item's
"reopen on ordinary evidence" clause is what that is.

**Decision needed.** Whether to widen the route, and there are three candidates,
none obviously right: ask `bin/docket triage` for a `falsifies:` where an item's
work is a deletion; accept a declaration committed to the branch *before* the
first commit that removes the assertion, which is weaker than the base but is
still not written beside the deletion; or leave it and let the `REJECT` carry the
conversation. Do not answer it on this item's own reasoning alone - wait until
there are two or three real instances to count, per `.claude/rules/expert-review.md`.

**A second instance, and it widens the question rather than repeating it
(`PL-L40Z`, 2026-09-17).** That item was found on `PL-TM9J`'s close-out - the
v0.4.27 cut - and its own diagnosis carried an observation this item does not:
the gap is not only about *when* a session learns it will falsify something. An
item **filed and closed on one branch** has no copy on the base at all, so there
is no moment at which any declaration could have been read. `verify` says so
itself, and silently: `commissioned_falsification` returns `("", "")` where the
base store holds no file for the id - "could not look" deliberately collapsed
into "looked, declares nothing", because that is what every capture looks like.
So the caller raises nothing, and the item has no route rather than a late one.

It is not a rare shape. **452 of the 842 closed items in the store, 54%, carry
the same `added` and `closed` date** - filed and finished in one sitting, which
is what most housekeeping work and every release cut looks like. Read that as a
proxy rather than a count: it over-reports where a capture merged before the
session that closed it and under-reports a branch spanning midnight, and neither
correction is large enough to change the order of magnitude.

The consequence for the three candidates above is worth recording without
settling anything, because it separates them where this item's own framing did
not. Only the **second** reaches this class. Asking `bin/docket triage` for a
`falsifies:` cannot: an item filed and closed on one branch is never triaged
before it is worked, so there is no pass at which the question would be put.
Accepting a declaration committed to the branch before the first commit that
removes the assertion can, because that ordering is available to a session that
created the item itself. Leaving the `REJECT` to carry the conversation leaves
this class with no route at all rather than a late one.

That is one instance and a count, not the two or three this item asked to wait
for. It is recorded here rather than as a fifth item in `verify-close-out`
because it is evidence for the decision this item already poses, not a second
question.

**Done when.** The decision above is recorded - in this item, in
`.claude/skills/docket/SKILL.md`, or in `subprojects/docket/README.md`'s account
of what `falsifies:` is for - and either a route exists for a session that
discovers the falsification mid-work and for an item filed and closed on one
branch, with a test under `subprojects/docket/tests/test_verify.py` driving it,
or the reasoning for leaving the `REJECT` to carry the conversation is written
where the next session meeting one will read it.

## Narrowed by PL-C4W8's Gate 2 staleness sweep, 2026-09-21

**One of the three cases now has a route.** `PL-ZMGR` (commit `21da2f7a`, #798)
taught `self_declared_falsification` to honour a branch's own `falsifies:` when
the commission is at `needs-decision` and the branch closes it - which lands
after this brief was written and is not mentioned in it. So a session deciding a
`needs-decision` item and discovering mid-work what its answer falsifies is no
longer unrouted.

**Two cases remain, and they are what is left of this item.** The exemption
gates strictly on `commission.status == "needs-decision"`, so a **`ready`
item's** mid-work discovery - this brief's primary framing - still has no
route. And an item **captured and closed on one branch** is still refused, which
`PL-ZMGR`'s own brief records as deliberate rather than as an oversight.

Re-scope to those two before working it; the `needs-decision` case above is
done and should not be rebuilt.

## Folded into PL-B8HZ's design round, 2026-09-25

The rule recommended there (`PL-B8HZ` § "Design round, 2026-09-25") reads
`falsifies:` as a waiver, and a waiver is the base's. The two cases left open
above get routes rather than code, and the recommendation is to record them here
and in `.claude/skills/docket/modes/close-out.md` and close this item with the
head's build.

- **A `ready` item's mid-work discovery.** The waiver is amended where the
  commission lives. An item-only branch from `origin/main` carrying
  `bin/docket set <id> --falsifies '...'` is what `CLAUDE.md`'s capture rule
  opens a pull request for at first push and arms - `bin/docket arm` answers
  `arm`, since the change lies under the store and no claim is bound to that
  branch - and once it merges, the work branch brings `main` in and
  `verify --self` reads the declaration from the base. On a solo project this
  buys visibility and order rather than a second author: the declaration is a
  commit of its own on `main`, before the work merges, and that is all that is
  claimed for it.
- **An item captured and closed on one branch.** The same route in its natural
  order: capture on its own branch with the declaration, let it merge, work
  from the merged base. The refusal of a declaration written on the capturing
  branch (`PL-ZMGR`, ratified) stands, because the assertion it would waive is
  in the base tree whether or not the base holds the item.

Neither is a fourth candidate beside the three above. Both are the second
candidate's ordering - declare before the commit that removes the assertion -
made concrete on the base instead of on the branch, and neither needs a new
mechanism. Sized by `PL-YZJD`'s count, about 2 folds in 502 close-outs, the
round trip is paid rarely, and honouring the branch's waiver instead is refused
for the reason the head records: a wrong waiver switches an integrity check off.

**Ratified with the head, 2026-09-25** (project owner, 2026-09-25, ratified,
over accepting a declaration committed to the branch before the removing
commit, and over leaving the `REJECT` to carry the conversation): both routes
above are the record, `PL-B8HZ`'s build writes them into
`.claude/skills/docket/modes/close-out.md`, and this item closes with it.
