---
id: PL-85NT
title: Repository-level breakage is visible to every session and claimed by none, so five duplicate items were filed for three findings in one evening
status: untriaged
added: 2026-09-15
---

**Problem.** Repository-level breakage is visible to every session and claimed by none, so five duplicate items were filed for three findings in one evening

**Observed 2026-09-15, 21:30-23:50 UTC.** `main` went red when `#593` landed.
Every session's start-up digest said so - *"main is red and no pull request will
show it"* - and no `PL-` id named it, because the work had not been filed. Every
in-flight guard this project has (`flight`, `show`, `next`, `concurrent`, the
digest) matches a `PL-` id, so unfiled work reads as nobody's to all of them,
and keeps reading that way after two sessions have pushed (`PL-CP74`).

**Five confirmed duplicates, counted from the store's own `reason:` fields
rather than from recollection:**

| duplicate | of | finding |
| --- | --- | --- |
| `PL-Y1W6` | `PL-B5VM` | `main` red on `PL-S5YM`'s `-k covered` selector |
| `PL-7VSK` | `PL-B5VM` | the same |
| `PL-HH52` | `PL-Y1W6` | `PL-S5YM`'s brief claims no test exercises the branch |
| `PL-MR6S` | `PL-0HPV` | the verify replay's scope and cost |
| `PL-X0ND` | `PL-SMN4` | a push run on `main` cancelled, leaving no verdict |

Three sessions reached the *identical* diagnosis of the red `main` inside an
hour - same chain, same commit, same selector - and each learned of the others
at a merge. `PL-66FP` is this shape one level up: two sessions cut `v0.3.7`
independently and the second was discarded.

**`PL-MR6S` is the row that widens the diagnosis, and it is the reason this is
not simply a concurrency problem.** `PL-0HPV` was filed 2026-09-14, a day
earlier, and sat open in the queue. A session tonight re-derived it from
scratch. So the failure is *capture does not look for what already exists*, of
which simultaneous sessions are only the acute form. A claim-and-push mechanism
would fix the four same-evening rows and leave this one untouched.

**Two candidate signals were measured before recommending either.** Both scored
against this store, over the five confirmed pairs above, asking where the true
original ranks among all candidates:

| signal | caught cleanly | weak | missed | fires on |
| --- | --- | --- | --- | --- |
| shared rare **title terms** | 2 of 5 | 2 | 1 | 41% of open items |
| shared cited **referents** (`PL-` ids, shas, `#NNN`, paths) | 4 of 5 in the top 4 | 0 | 1 | 32% |

Referents beat titles decisively, and the reason is visible in the data: the
three red-`main` items all cite `#593`, `7ba6108e` and `#1985`, while
`PL-MR6S` and `PL-0HPV` ask one question in two vocabularies and share **no**
referent at all. `PL-X0ND`/`PL-SMN4` share six and rank first.

**So the naive version is refused here rather than proposed.** At those firing
rates neither signal can *refuse* a capture: `CLAUDE.md` reserves hard failure
for exact rules, and a check that fires on a third of captures without changing
a decision is a defect in the check. `PL-LKGL` is the standing warning - the
count nobody ran came back 67% still-real findings. What the measurement
supports is a **print of the three nearest open items**, judged by a reader, not
a gate.

**One design constraint, which rules out the obvious placement.** Referent
matching cannot run inside `bin/docket new`: capture writes a title and nothing
else, so the referents do not exist yet at that moment. It has to run where a
body exists and somebody is already reading it - `bin/docket triage` is that
place, and the print is nearly free there. That placement does **not** help the
same-evening case, where neither session triages before pushing.

**Done when.** Undecided deliberately - the route is the project owner's call,
and `CLAUDE.md`'s four dispositions point different ways here:

1. **`bin/docket triage` prints the nearest open items by shared referent.**
   Cheap, measured, catches the `PL-MR6S` class. Does nothing for the acute case.
2. **The digest's red-`main` line names any open item citing the failing run or
   commit**, and says "no item claims this - `bin/docket new` first" when none
   does. Aimed squarely at the acute case, in the one place every session
   already reads. Needs the same referent match, run against the digest's own
   facts.
3. **Resident text** telling a session to file before touching unowned
   repository work. `CLAUDE.md` already says this, in the housekeeping bullet.
   Tonight every session either had not read it that way or read it after
   diagnosing. So the gap is not an absent rule, which is why this item does not
   propose adding one.

**The number that would have made this wrong was counted, and it reversed the
recommendation.** The question was whether 2026-09-15 was a freak evening, in
which case a digest line buys little. Counting every `dropped` item whose own
`reason:` says duplicate or superseded, grouped by the day the duplicate was
*captured*:

```text
items dropped as a duplicate/superseded: 50 (of 112 dropped overall)
distinct capture-days involved:          16

  2026-08-25   4    2026-09-04   6    2026-09-13   2
  2026-08-30   3    2026-09-05  10    2026-09-14   2
  2026-09-02   5    2026-09-07   3    2026-09-15   4
```

**45% of everything this store has ever dropped was dropped as a duplicate**,
across 16 separate days, and tonight's four is unremarkable - `2026-09-05`
produced ten. So the collision is **chronic, not a burst**, and the acute
same-evening form is a subset of a standing problem rather than the whole of it.

**Bound on that number, stated because it is easy to over-read:** the 50 are
duplicates of *every* kind, including two sessions filing the same idea twice
with no repository breakage involved. It establishes that duplicate capture is
routine here; it does **not** establish that unowned repository work is the
whole cause. Separating those two would need each `reason:` read, which is a
judgment and is not scripted here.

**Recommendation, after the count: 1, then 2** - the reverse of what this brief
said before the number existed. Route 1 acts at triage on every item and so
reaches the chronic class the count reveals; route 2 is narrower, firing only
where `main` is red. Had the count come back showing tonight as an outlier the
order would have stayed 2-then-1, which is what made it worth running. Route 3
is refused on the evidence above.

**Route 1 was then built, measured and thrown away, 2026-09-16.** The project
owner approved it; a `neighbors.py` was written against the real store and
deleted unshipped, because building it properly disproved the numbers this brief
had used to recommend it.

| variant | true original in top 3 | fires on |
| --- | --- | --- |
| shared referents, rare-filtered | 2 of 5 | 84% of open items |
| raw shared count, no filter | 3 of 5 | 84% |
| Jaccard over the referent sets | 1 of 5 | 91% |
| overlap coefficient | 0 of 5 | 93% |
| same-day **and** shared referent | 3 of 5 | 95%, median 19 candidates |

**Why the earlier figure in this brief was too kind, stated plainly because it
is the reason a session was spent on a dead end.** The 4-of-5 above was computed
with rarity fixed over a snapshot taken before tonight's items existed. Once the
duplicates themselves are in the store, `#593` and `7ba6108e` are cited by
enough items to cross any rarity threshold and get filtered out - so the signal
decays precisely as the duplicates it should catch accumulate. `PL-7VSK` scored
4 shared referents under the snapshot and zero under the live store.

**The refutation was already in `docs/dead-ends.md` and was under-weighted:**
*"this store is cross-referenced (86.1%, 2,773 edges)"* (`PL-KM3X`). In a store
where 86% of items cite other items, referent overlap cannot separate a
duplicate from an ordinary citation - which is what 84% firing means. That line
should have killed route 1 before any code was written.

So **route 1 is refused on measurement**, and is recorded in
`docs/dead-ends.md` so it is not proposed again. What survives untested is
route 2, whose match is against the *digest's own facts* - one failing run, one
commit sha - rather than against the whole store, and which therefore does not
inherit the cross-reference density that killed route 1. That is a different
claim and it is unmeasured; it should be measured before it is built, on the
same standard applied here.
