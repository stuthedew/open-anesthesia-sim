---
id: PL-99YZ
title: Three sessions opened three pull requests for the same red-main fix within four minutes, each having correctly filed its own item first, because every in-flight guard matches an existing PL- id and none of them can see an item that did not exist when the other sessions looked
priority: P2
effort: M
status: ready
classes: defect, infra
feature: parallel-sessions
touches: docs/items
added: 2026-09-15
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
