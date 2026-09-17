---
id: PL-TKFD
title: A session that discovers mid-work that its work falsifies an assertion cannot declare falsifies: on the base, so verify --self has no clean route for the case the field was built for
status: untriaged
feature: verify-close-out
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
