---
id: PL-TZ7T
title: bin/docket new files a duplicate title without noticing: PL-LBR6 sat ready for six days with the record rename diagnosed and a verify command written while PL-5QLP and PL-QMC0 were filed as fresh discoveries of the same mechanism
priority: P2
effort: S
status: done
classes: infra
feature: slug-rename-on-write
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/duplicates.py, subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/concurrency.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_duplicates.py
added: 2026-09-19
closed: 2026-09-20
pr: 793
payoff: stops one defect being diagnosed three times - it has happened five times now, and each duplicate costs a full brief written by a session that could not know the first existed
verify: grep -q 'def test_new_names_an_existing_item_with_a_near_identical_title' subprojects/docket/tests/test_cli.py
root-cause-of: PL-BHBZ, PL-4FD2, PL-5QLP, PL-QMC0
recurrences: 2026-08-30 PL-TH7P
---

**Problem.** bin/docket new files a duplicate title without noticing: PL-LBR6 sat ready for six days with the record rename diagnosed and a verify command written while PL-5QLP and PL-QMC0 were filed as fresh discoveries of the same mechanism

**What it cost, 2026-09-19.** `PL-LBR6` sat `ready` for six days with the
`docket record` rename diagnosed and a `verify:` command written against it,
while `PL-5QLP` and `PL-QMC0` were filed as fresh discoveries of the same
mechanism - one writer renaming an item file as a side effect of writing a
field. Three items, one cause, and the two later ones were each captured by a
session that had no way to know the first existed. All three have since closed
under `feature: slug-rename-on-write`, so the grouping was recoverable; what
was not recovered is the two diagnoses paid for twice.

**Why it matters.** `CLAUDE.md`'s capture rule is deliberately unconditional -
"Do not ask whether to record it" - and that is right, because the alternative
is losing findings. The cost it accepts is exactly this one, and it is paid at
the only moment the duplicate is cheap to catch: `bin/docket new` has the
title, the store, and a session's attention, and says nothing. Every later
mechanism that could catch it is more expensive - `feature:` grouping needs
somebody to already know the items are one problem, and the apparatus backlog
sweep that found this cluster read 145,000 tokens across twelve agents.

This is the last of `feature: slug-rename-on-write`'s three open items, so it
is also what closes a group at 5/8 rather than adding to a standing theme.

**Done when** (key corrected 2026-09-20 - the measurement below refutes the
title-only version this line first carried, so read it before building). `bin/docket new` names the existing **open** items sharing a declared
`touches` path, ranked by title similarity and printed top-first
to the one being filed, prints them with their status, and files the item
anyway - a warning rather than a refusal, because the capture rule may not be
made conditional on a similarity score, and a near-duplicate that is genuinely
a second instance is a legitimate filing.

**Fourth and fifth occurrences, recorded 2026-09-20, which is what seats the
`root-cause-of:` above.** `PL-STC4`'s brief documents two more duplicate
captures of one defect - `PL-BHBZ`, filed by a concurrent session four minutes
after this pass's triage commit, and `PL-4FD2`, found independently while
grouping. Both describe `verify`'s suppression check reading prose as code;
all three sit in `feature: verify-false-reject` and one of them will be dropped
with a `reason`. With `PL-5QLP` and `PL-QMC0` that is four items filed for
mechanisms the store already carried, which is the generator threshold met on
recorded evidence rather than on inference: each was captured by a session that
had no way to know the first existed, and the diagnosis was paid for twice each
time.

The cost is now measurable rather than anecdotal. `PL-STC4` and `PL-4FD2` each
carry an independent analysis of the same check, written hours apart, and
`PL-BHBZ` a third. Whoever works `verify-false-reject` reads three briefs to
recover one defect.

**Measured 2026-09-20, and it refutes the key this brief names.** "Done when"
above says `bin/docket new` should name "the existing items whose titles are
close to the one being filed". Title closeness does not work. Over the 1,362
items in the store, scoring pairs by Jaccard overlap of title content words:

| threshold | known duplicate pairs caught (of 13) | pairs flagged store-wide |
| --- | --- | --- |
| 0.45 | 0 | 58 |
| 0.30 | 0 | 168 |
| 0.20 | 8 | 768 |
| 0.15 | 11 | 2,234 |

There is no usable setting. The known duplicates score 0.121-0.276 against each
other, because each session describes the same defect from the angle that bit
it - "reads prose as code", "reads every added line regardless of file type",
"greps every added line for the three marker substrings". Meanwhile the only
clusters title similarity *does* find at a usable threshold are the items meant
to recur: sixteen "Triage the N captures on DATE", and three groups of release
cuts and tags. It fires on exactly the wrong set.

**`touches` is the key that works.** Nine of the thirteen known duplicate pairs
share a declared `touches` path. Narrowing candidates to items sharing one and
*then* ranking by title similarity puts the true duplicate in the **top 3 for 8
of 9** pairs, against candidate sets of 55-111. So the shape is: shared path
selects, title ranks, and `new` prints the top few rather than the whole set.

**Two wrinkles the design has to answer.**

- **A fresh capture has no `touches`.** `PL-0KQP` is the miss: `bin/docket new`
  writes no `touches`, so all four of its pairs score no shared path. The
  session filing it was on a branch whose commits touch
  `subprojects/docket/src/docket/verify.py`, so the working tree can supply
  candidate paths where the item does not.
- **Only open items should count.** A triage pass or a release cut is `done`
  within hours, so scoring against open items alone drops the recurring-by-design
  clusters for free - and what it still catches there is real, `PL-Z0C7` being a
  second session cutting `v0.4.31` while `PL-R5VS` was open.

**This does not settle what happens after detection.** The project owner asked
on 2026-09-20 whether repeat filing attempts should be counted and used to raise
priority. That is a live design question above this item rather than inside it,
and the measurement here only fixes the key.


**Built 2026-09-20, and the one number the brief did not fix.** The key is as
measured above: shared `touches` selects, title similarity orders inside that
selection, closed items are dropped, and the command warns without refusing.
What the measurement did not settle is how close a title has to be to be worth
printing once the path has already selected it, and the answer matters because
most of this store declares `cli.py` or `verify.py` - a typical capture selects
34 to 83 candidates on the path alone.

A floor of zero was measured and refused: at that setting 323 of 325 open items,
probed as simulated captures, print three candidates each, which is a warning
firing every run without changing a decision. The break-even was stated before
counting - a floor is wrong if it suppresses a real duplicate - and the count
settled it: the nine known path-sharing pairs score 0.133 to 0.244, so **0.10
suppresses none of them** while cutting the captures that print anything from
323/325 to 179/325 and the lines printed from 2.89 to 1.07. 0.15 was refused
for suppressing two of the nine, at 0.133 and 0.143. `DISPLAY_FLOOR` in
`subprojects/docket/src/docket/duplicates.py` carries those numbers, because
that is where somebody changing the constant will look.

Verified against the real store rather than only against fixtures: filing
`PL-4FD2`'s own title reproduced the defect on `origin/main`'s code - the id and
nothing else - and named all three open members of the suppression cluster on
this branch.
