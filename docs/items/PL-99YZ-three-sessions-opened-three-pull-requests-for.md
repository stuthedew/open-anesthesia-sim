---
id: PL-99YZ
title: Three sessions opened three pull requests for the same red-main fix within four minutes, each having correctly filed its own item first, because every in-flight guard matches an existing PL- id and none of them can see an item that did not exist when the other sessions looked
priority: P2
effort: M
status: done
classes: defect, infra
feature: parallel-sessions
touches: docs/items
added: 2026-09-15
closed: 2026-10-11
not-delegable: the deliverable is a count over the store's own history - how many same-subject, different-id collisions it contains - and then a recorded decision about whether anything deterministic is worth building for them. No command can run before that count exists, and per the item's own **Done when.** a recorded 'no, the digest line is enough' closes it as legitimately as a check would
---

**Problem.** Three sessions opened three pull requests for the same red-main fix within four minutes, each having correctly filed its own item first, because every in-flight guard matches an existing PL- id and none of them can see an item that did not exist when the other sessions looked

**The facts.** `main` went red on `7ba6108e` (#593) when `PL-S5YM`'s bare
`-k covered` selector began matching a test that merge added. Three sessions
diagnosed it independently and opened three pull requests against the same one
file, `docs/items/PL-S5YM-doc-check-s-covered-directory-branch-now-has-no.md`:

| Pull request | Item filed | Opened |
| --- | --- | --- |
| #598 | `PL-B5VM` | 22:08:12 |
| #599 | `PL-Y1W6` | 22:10:05 |
| #600 | `PL-7VSK` | 22:12:29 |

Four minutes end to end. All three reached the same root cause and each wrote a
different `verify:` into the same field, so whichever merges first leaves the
other two conflicting on that path.

**Every session did the right thing, which is what makes this a finding.**
`CLAUDE.md`'s housekeeping rule says to file the item before starting
unfiled repository work, and all three did - `PL-B5VM`, `PL-Y1W6`, `PL-7VSK`.
That rule exists so the work is visible to `flight`, `show`, `next`,
`concurrent`, `stranded` and the digest, and it worked: each session's own work
was visible under its own id. What it cannot do is the other direction. Every
one of those guards matches an **existing** `PL-` id, and a session filing a new
id cannot be matched against two ids that did not exist when it looked. Filing
first makes you visible; it does not make you look.

**One mechanism would have caught it, and the routing is what failed rather
than the mechanism.** `bin/docket concurrent <id>` has a second half that reads
the files branches have **actually changed** rather than what anybody declared,
and all three branches had touched that one path. The skill routes `concurrent`
from "Mode: start an item", which housekeeping work reaches by way of "file the
item first, then start it under its id" - so the route exists. It is also
bounded by `git fetch` and by what has been pushed, and #598 and #599 were 113
seconds apart.

**The cost is real but not total, and that matters for what is worth
building.** Three independent diagnoses agreed on the mechanism, and #599 found
something the other two missed: `PL-S5YM`'s brief claimed no test exercised the
covered-directory branch, which was false when written -
`test_childless_directory_covers_its_whole_subtree` has existed since `PL-032`,
and only the negative direction is missing. #598 separately counted the class,
finding four more open items on a bare `-k` (`PL-Q8RQ`), and #600 captured
whether `make check` should pay `--verify`'s 150 s (`PL-MR6S`). So the duplicate
spend bought two captures and a correction; what it cost was two pull requests
that must now be closed and their captures rescued.

**Do not propose a mechanism here before counting.** The obvious candidate is
matching on the **path** rather than the id at `bin/docket new` time - "two open
branches already edit this file". Per `.claude/rules/expert-review.md`, the
number to produce first is how often that would fire across the store's history
and how many of those firings would have been real collisions rather than two
sessions legitimately capturing near the same file. A red default branch is the
archetype of a shared subject with unshared ids, and it may also be rare enough
that the answer is a line in the session-start digest rather than a check.

**Done when.** The question is answered with a count rather than an argument:
how many same-subject, different-id collisions the store's history actually
contains, and whether anything deterministic is worth building for them. A
recorded "no, the digest line is enough" closes this as legitimately as a check
does.

**Why it matters.** The cost landed on the project owner rather than on the
sessions: three pull requests against one file, two of which have to be closed
and their captures rescued, and a conflict on that field for whichever two
lose. What makes it an item rather than an apology is that no rule was broken.
Every session filed its item first, exactly as `CLAUDE.md`'s housekeeping rule
requires, and the rule worked in the direction it was written for - each
session's own work was visible under its own id.

The gap is structural and one-directional. Every guard this project has -
`flight`, `show`, `next`, `concurrent`, `stranded`, the digest, and the
session-list read the `docket` skill adds on top of them - matches an
**existing** `PL-` id. A session filing a new id cannot be matched against two
ids that did not exist when it looked. Filing first makes you visible; it does
not make you look. A red default branch is the archetype of the shape, because
it is a shared subject that every session discovers independently and files
under its own fresh id, and `PL-X0ND` shows the same repository has a second
way to produce one.

**The measurement record is `PL-85NT`, dropped into this item 2026-09-16.**
`PL-85NT` (repository-level breakage visible to every session and claimed by
none) was filed the same evening for the same failure and was dropped as
superseded, on its own recommendation, because the diagnosis here is sharper.
What it has that this item does not is measured, and it is not repeated here -
read `docs/items/PL-85NT-repository-level-breakage-is-visible-to-every.md`
before proposing any detector. Three results decide most of the design:

- **The collision is chronic, not a burst.** 45% of everything this store has
  ever dropped (50 of 112) was dropped as a duplicate or superseded, spread
  over 16 separate capture-days; 2026-09-05 produced ten to 2026-09-15's four.
  So a mechanism aimed only at the same-evening case addresses a subset.
- **Route 1 - matching captures by shared referent - was built against the real
  store, measured, and deleted unshipped.** Every variant fired on 84-95% of
  open items while putting the true original in the top three at best 3 times
  in 5, and the signal *decays as duplicates accumulate*, because the shared
  ids stop being rare. `docs/dead-ends.md` carries it. The refutation was
  already available in `PL-KM3X`: in a store where 86.1% of items cite other
  items, referent overlap cannot separate a duplicate from a citation.
- **Route 2 - the digest naming any open item that cites the red streak's runs
  or shas - is measured and unbuilt.** Head-only matching misses two of four
  red-`main` events; widening to every sha from the last green run through the
  failing head returns the item that actually claimed the failure on all four,
  at 6-8 candidate items instead of 0-6. Streaks longer than four are
  unmeasured.

None of that displaces this item's own point, which outranks all three: an
existing command, `bin/docket concurrent <id>`, already reads the files live
branches have changed, and all three colliding branches had touched the one
path. The failure was routing, not detection.

**A fourth instance, 2026-09-16, and it is the sharpest because nobody erred.**
Two sessions triaged `PL-2M4X` and `PL-SYG4` concurrently and reached
materially the same verdict on both (`P3 · M · needs-decision` on `PL-SYG4`
from each, differing only in one class and the feature name). `PL-Q0J1`
carries the account. The mechanism is one level below the three above and is
new: every in-flight guard matches an id against a **commit subject**, and the
leading-id rule names the ids a commit *closes*. A triage pass closes nothing,
so its commits lead with the pass's own id and the items it triaged appear in
no subject at all - making the pass invisible to `flight`, `show` and `next`
*while it is following the rule exactly*. Neither session could have looked
harder. Any detector proposed for this item should be tested against this case
specifically, because filing first would not have helped either of them.

**Removed from `PL-BHVM`'s cluster, 2026-09-19.** That item's design round found
this is a different question from the one it root-causes: `PL-BHVM` asks what
evidence proves a **ref is done**, and this asks how a session's **claim**
becomes visible before any ref carries it. Bundling the two is what made the
cluster look uniform. Nothing here is answered by `PL-BHVM`'s decision, and
nothing here waits on it — `feature: parallel-sessions` is where this belongs.

**A fifth instance, 2026-09-23: main red on `a65b440c` (`PL-KH3Q`), fixed three
times.**

- `795ebbf6`, under `PL-XYQW`'s id, at 01:17:41 UTC. `PL-KH3Q` had been
  captured 39 seconds earlier on a different branch (`37d3d1e0`).
- #934 (`PL-19T3`) ported that commit and merged at 01:35:56. This is the copy
  that landed.
- `6e8331f5`, on `claude/affectionate-fermat-dp9uu8`, at 01:33. That branch had
  claimed `PL-KH3Q` at 01:29 with the empty commit `modes/start.md` prescribes.
  The fix was dropped when the branch merged the base.

The claim worked as designed. `bin/docket show` names that branch as the holder,
and `PL-XYQW`'s later claim (`2b52e486`, 01:31) yields to it. What no claim can
see is a fix already written under another id before the item existed. That is
this item's mechanism exactly: every guard matches the id, and the first fix
carried a different one. All three edited one line of
`subprojects/docket/tests/test_cli.py`. Whether `795ebbf6` had been pushed by
01:29 is not recorded, so it is unknown whether a file-level read such as
`bin/docket concurrent` could have seen it.

**Re-confirmed 2026-10-11: still true, at a different price.** Every guard
still matches an id, and `bin/docket new`'s near-duplicate search
(`duplicates.near_duplicates`) reads only the store in the session's own
checkout, so an item filed on another unmerged branch is invisible to it. Three
things have changed the price since this was filed. A claim is pushed when an
item starts (#987, 2026-09-24), so a branch's work is readable from its first
minutes rather than from its pull request. `bin/docket show` names every other
branch already editing an item's file (`PL-1X2C`, #1046). And `CLAUDE.md` now
stops a session on a `main` red for a reason outside its item until it has told
the owner (2026-09-25, `PL-NZC0`), which is the case this item was filed on.

**Counted 2026-10-11, over the whole history.** Against `origin/main` at
`7f970bbe`, with every pull request head fetched (`git fetch origin
'+refs/pull/*/head:refs/prs/*'`, 1,306 refs) and the store read through
`docket.store.read_items` (2,182 items). An item's capture time is the earliest
author date of any commit, on `main` or on a pull request head, that adds its
file. A duplicate pair is a dropped item whose `reason:` calls it a duplicate
or superseded, paired with the item the reason points at (94) or else the first
other item it names (14), plus 7 drops read by hand whose reasons use neither
word, `PL-7VSK`'s "the same repair" among them. Each later capture is placed by
what the tree its capture commit was made on held of the earlier item. The
scripts and their data are in the Projects trial's shared folder,
`v0.6.0/pl-99yz-count/`, with a note on re-running them.

| Later capture | Pairs | Earlier item in its checkout | On `main`, not in its checkout | Only on another branch | On its own branch | No branch history |
| --- | --- | --- | --- | --- | --- | --- |
| before #793 (2026-09-20) | 89 | 57 | 5 | 9 | 2 | 16 |
| #793 to #987 (2026-09-24) | 18 | 17 | 0 | 1 | 0 | 0 |
| since #987 | 8 | 5 | 0 | 3 | 0 | 0 |
| **Total** | **115** | **79** | **5** | **13** | **2** | **16** |

#793 is `PL-TZ7T`'s near-duplicate search and #987 the pushed claim. The shape
this item names, an original visible only on another branch, is 13 of 115. The
common shape is a capture filed with its original already in its own checkout,
79 of 115, which is a search question rather than a visibility one and is what
#793 answers. Since claims there have been three branch-only pairs, the last
`PL-927J` and `PL-P813` on 2026-09-27, and none in the fourteen days since.

**Work done twice**, read four ways, because a duplicate capture costs a drop
and duplicated work is the cost this item is about: the drop reasons; the 10
pull requests closed unmerged; every pair of pull requests open at once whose
own commits edited one existing item file (365 pairs; the 36 since claims read
by hand, and the 7 of those that rewrote one front-matter field read again);
and every such pair adding an identical line to one shared file outside the
store (89 pairs, nearly all boilerplate).

| When | Done twice | Shape | What answers it now |
| --- | --- | --- | --- |
| 2026-09-03 | The title check's missing `edited` trigger, fixed in #256 (`PL-3V8K`) and again on `PL-0ZP8`'s branch | one fix, two ids | `CLAUDE.md`'s stop on the same check failing twice (inferred) |
| 2026-09-04 | v0.3.7, cut by two sessions (`PL-66FP`) | one cut, no id | the release refusal (#323) and the claimed release train (#995) |
| 2026-09-06 | `PL-X35V` and `PL-ZVS7`, triaged by two passes (`PL-N1JK`) | one item, two answers | triage skips `Its file is already edited on` another branch |
| 2026-09-15 | The red-`main` fix this item was filed on, #598-#600 | one fix, three ids | the stop on red `main` |
| 2026-09-16 | `PL-2M4X` and `PL-SYG4`, triaged by two passes (`PL-Q0J1`, the fourth instance) | one item, two answers | the same skip once either pass has pushed; `PL-XJ22` for the window before |
| 2026-09-23 | The red-`main` fix of the fifth instance | one fix, three ids | the stop on red `main` |
| 2026-09-26 | `PL-QMN0`, triaged by the branch working it and by #1124's pass three minutes later | one item, two answers | nothing yet: `PL-XJ22` |

**This item's shape, one change under different ids or under none, came four
times, all before 2026-09-24, and not once in the 409 pull requests and 550
captures since.** The rows before claims come from drop reasons and the items'
own accounts, so they are a lower bound; only the claim era was read pair by
pair. The one-item rows are a different question: one item's file answered
twice, which the triage skip reads by that item's own id. The 2026-09-26 pass
did read the marks, before the claim reached `origin` (inferred; `PL-XJ22` has
the times), so that window is filed as `PL-XJ22` rather than answered here,
with the near miss of 2026-10-01 (#1278 handed `PL-DHGC` and `PL-W560` back two
minutes after answering them, `a938142c`).

**Red `main`.** 806 `quality.yml` push runs on `main` from 2026-09-15 hold 42
failures in 10 streaks. Nine fell between 2026-09-15 and 09-23, and two of
those produced the duplicate fixes above. One has fallen since claims, on
2026-10-05 (run 4805 on `b67dace8`), and it was a job GitHub never gave a
runner (`PL-7WNJ`), not red code. So most of the quiet since claims is that
`main` has stayed green, and the stop rule is not proven by it.

**What each candidate would have cost**, replayed at every capture with branch
history (1,816, of them 550 since claims) against the pull requests open at
that moment, commit times standing in for push times:

| Key at `bin/docket new` | Fires since claims | Fires, whole history | Branch-only pairs it reaches |
| --- | --- | --- | --- |
| Shares any changed file with another open branch | 89 (16.2%) | 474 (26.1%) | 7 of 13 |
| Shares a file outside `docs/items/` and ten hub files (`ROADMAP.md`, `CLAUDE.md`, `docs/WORKING_NOTES.md`, `uv.lock` and the like) | 55 (10.0%) | 131 (7.2%) | 1 of 13 |
| Shares an existing item file neither branch created | 21 (3.8%) | 260 (14.3%) | 4 of 13 |
| `docket new`'s own key, shared path then title above `DISPLAY_FLOOR`, run against other open branches' new items | 1 (0.2%) | 10 (0.6%); 6 of its 12 candidates real | 6 of 13 |

The last key's one firing since claims is `PL-P813` against `PL-927J`, a real
duplicate, which `bin/docket stranded` found after it was filed (its drop
reason).

**Decided 2026-10-11, by this session: build nothing.** Apparatus-internal and
with one clearly correct option, so it is decided rather than put to the owner.

- The path keys fail on firing rate. The narrowest still fires on 21 of 550
  captures since claims, and there was no collision of this item's shape in
  that period for any of them to catch. A check that fires without changing a
  decision is a defect in the check (`CLAUDE.md` § "Prefer deterministic
  tooling over repeated model work").
- The cross-branch `docket new` key is precise and buys nothing: one hit in 550
  captures, which `stranded` found anyway, and it reaches only 6 of the 13
  branch-only pairs, because the rest were filed on fresh capture branches that
  had changed nothing yet. It would put a read of every other branch's new items
  into `docket new`, which has to cost a session nothing it can notice for the
  capture rule to stay unconditional.
- `PL-85NT`'s route 2, the digest naming items that cite a red streak, is not
  needed: since claims no session has repaired a red `main` it did not cause,
  and `main` has gone red once, for a runner that never came. The digest already
  has its red-`main` line, `tools/main_ci_status.py`'s `advisory()`.

**What would reopen it.** A collision of this item's shape since claims: two
branches writing one change under different ids, or under no id at all, as a
release cut once was. Or branch-only capture duplicates past about one a week
that triage and `bin/docket stranded` leave to be found after a merge. Either
is filed with `bin/docket new`, naming this item.

**`PL-S0MB`'s row moving this item to `open-item-overlap-detection` lapses.**
That build retires `parallel-sessions` for open items only, and this one closes
first, so it keeps the name with the rest of the closed history.

**Done when** is met by the count and the decision above.
