---
id: PL-LF2C
title: PL-VV4D's exact left-behind check rests on refs/pull/<n>/head being permanent, and GitHub is about to unreference 90 of them, so the check needs a third decline condition and one of its two test vectors dies
priority: P2
effort: S
status: ready
classes: defect, docs
feature: parallel-sessions
touches: docs/items/PL-R808-build-the-exact-left-behind-check-as-a-tools.md, subprojects/docket/src/docket/vcs.py
added: 2026-09-12
verify: python3 tools/doc_check.py check && grep -qF 'not a superset' subprojects/docket/src/docket/vcs.py
---

**Problem.** PL-VV4D's exact left-behind check rests on refs/pull/<n>/head being permanent, and GitHub is about to unreference 90 of them, so the check needs a third decline condition and one of its two test vectors dies

**Observed 2026-09-12**, from GitHub Support's reply on ticket 4733783 (the
copyright purge `PL-0SCG` tracks), shown to the session by the project owner.

**What Support said.** Their tooling found references to the sensitive commit
SHA in 90 pull requests - `297` through `386` inclusive - and: *"Based on your
request, we will just delete their internal references, which will make the
diffs and the sensitive data inaccessible, but preserve the comment history."*
Confirmation to follow.

**The collision, measured before writing this.** All 90 of `297..386` currently
have a `refs/pull/<n>/head` on the remote, out of 500 pull heads total. And
`#312` - one of the two test vectors `PL-VV4D` recorded and `PL-R808` carries
into its Done-when - is inside that range:

```text
refs/pull/284/head  7f87bf5971e4b0947c6604aca979f295f24e5c38   outside the range
refs/pull/312/head  7d1615f51773a8310cafc5cce282ff2f262481ea   INSIDE 297-386
```

**Why this is a premise failure and not a test-data problem.** `PL-VV4D`'s
decision, recorded and approved earlier the same day, states the invariant as:
*"A pull request merges the head it was opened against, and GitHub freezes
`refs/pull/<n>/head` at that head when the pull request closes. So the invariant
is a ref comparison and nothing else."* "Freezes" was read as permanent. It is
not: the ref is deletable on request, and this repository has just requested it
for 90 pull requests. So the exact check must handle a pull request that
certainly existed and certainly merged, whose frozen head is **gone** - which is
a distinct third case from "no network" and from "not fetched", and in which the
check cannot answer at all.

That does not overturn `PL-VV4D`'s decision. The exact test is still exact where
the ref exists, and `vcs.orphaned` still stands as the portable half for
everything else - which is now doing more work than the decision credited it
with. What changes is that the exact half is not a superset of the portable one
even in principle, so retiring `orphaned` later is foreclosed rather than merely
deferred.

**`PL-VV4D` is closed and is not rewritten** - a closed item's record says what
was decided and on what basis, and this finding post-dates it. This item is the
amendment, and `PL-R808` (the build) carries the consequences.

**Why it matters.** Two of this item's three Done-when clauses are already
satisfied: `PL-R808`'s brief now carries the third decline condition and has
replaced the `#312` vector with `#499`. The clause left is the one that outlives
both items, and it is the reason this was not simply folded into `PL-R808`.

`PL-VV4D` decided to build the exact check *beside* `vcs.orphaned` rather than in
place of it, and costed that as a deferral - the portable content comparison
stays for now, and retiring it later stays available. That is no longer true.
With `refs/pull/<n>/head` deletable on request, and 90 of this repository's own
already requested under support ticket 4733783, the exact test cannot answer at
all for a pull request whose frozen head is gone, and `vcs.orphaned` is the only
thing that can. The exact check is therefore not a superset of the portable one
even in principle, and retiring `orphaned` is foreclosed rather than deferred.

That consequence lives nowhere a future session would meet it. `PL-VV4D` is
closed and is not rewritten - a closed item records what was decided and on what
basis, and this finding post-dates it. So a session reading `vcs.orphaned`'s
docstring in a year, seeing the exact check exists, will reach for exactly the
tidy-up this item exists to prevent, and the report it deletes is the one
standing between a commit and being lost.

**Where the remaining clause lands.** `vcs.orphaned`'s own docstring in
`subprojects/docket/src/docket/vcs.py`, which is the file a session proposing the
retirement has open.

**Done when.** `PL-R808` states the third decline condition - a pull request
whose head ref no longer resolves - and says what the check reports then; its
`#312` vector is replaced with one outside `297..386`; and the
not-a-superset consequence is recorded where a later session proposing to retire
`vcs.orphaned` will meet it.
