---
id: PL-MT3R
title: The remote's current heads have been read from the clone's own copies by four readers since PL-4Q9B closed - a harness-written tracking ref, the upstream setting, a rival's unpruned tracking ref, the local branch - so what the remote holds wants one record per command, consulted by claim, yield and arm
priority: P2
effort: M
status: needs-decision
classes: defect
feature: remote-copy
touches: subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_claiming.py, subprojects/docket/tests/test_claims.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-26 triage pass
added: 2026-09-26
payoff: what the remote holds is one record every command reads, so a new reader stops taking a clone's copy for the remote's and costing an item
root-cause-of: PL-WX87, PL-KX73, PL-C3MN, PL-21KN
generator: live - five readers in claiming.py, arming.py, claims.py and vcs.py still take a local copy for the remote's: claiming._on_copy a rival's tracking ref, arming.arm HEAD for the pull request's branch, claims.holdings and vcs.cuts_in_flight every refs/remotes ref as live, one for a branch the remote deleted included, and claiming.yield_claims the local branch; only claiming._on_remote asks the remote, for the checkout's own branch, so each new reader picks its own copy again
misread: The remote's current refs and tags, and whether the clone's local copies still match them
---

**Problem.** The remote's current heads have been read from the clone's own copies by four readers since PL-4Q9B closed - a harness-written tracking ref, the upstream setting, a rival's unpruned tracking ref, the local branch - so what the remote holds wants one record per command, consulted by claim, yield and arm

The fact is `PL-4Q9B`'s, in its own words: "The remote's current refs and
tags, and whether the clone's local copies still match them". That head closed
on 2026-09-19, and #685 answered its reconciliation question with "no single
point". Since then four readers have taken a copy the clone holds for the
remote's:

- `PL-WX87` (#1024, done): `claim` read the tracking ref the harness writes at
  session start, for a branch nobody had pushed, as the branch's copy on the
  remote, and skipped its push. Fixed for the checkout's own branch alone:
  `claiming._on_remote` asks `git ls-remote`.
- `PL-KX73` (#1020, done): the upstream setting, which the harness points at
  `main`, stood where the branch's own copy would be. `claiming._branch` now
  reads a default-branch upstream as none.
- `PL-C3MN` (open): `claiming._displaced` reads a rival's
  `refs/remotes/origin/<rival>` through `_on_copy`, and no fetch here prunes,
  so a rival branch the remote deleted still withdraws this branch's claim.
- `PL-21KN` (open): `arming.arm` reads `HEAD` as the pull request's branch and
  never `origin/<branch>`, so after an *Update branch* made elsewhere it said
  `behind 1` of a pull request already level with `main`. It had fetched: the
  refs were fresh, and the copy was the wrong one.

`PL-WX87` recorded itself as the first post-close instance and `PL-KX73` as
the second, adding that "a third would count as a generator whose fix did not
hold". `PL-C3MN` is the third and `PL-21KN` the fourth.

**Readers counted, 2026-09-26, against `78b1a02b`**, by one grep of
`claiming.py`, `arming.py`, `claims.py` and `vcs.py` for `ls-remote`,
`refs/remotes`, `%(upstream`, `include_remote`, `HEAD..` and `...HEAD`. One
reader asks the remote: `claiming._on_remote`, for the checkout's own branch
only. Five still take a local copy for the remote's:

- `claiming._on_copy`: a rival's tracking ref (`PL-C3MN`).
- `arming.arm`: `HEAD..<base>` and `<base>...HEAD`, never `origin/<branch>`
  (`PL-21KN`).
- `claims.holdings`: `vcs._unlanded_refs(include_remote=True)` reads every ref
  under `refs/remotes` as a live holder, including one for a branch the remote
  has deleted. It is where
  `_on_copy`'s rivals come from, and what every read command's holds rest on.
- `vcs.cuts_in_flight`: the same listing. Its docstring says what it names "a
  second checkout would read identically", which a tracking ref for a branch
  the remote deleted is not.
- `claiming.yield_claims`: it reads "already ended" from the local branch,
  where an unpushed yield stands, and returns before it asks the remote.
  That is `PL-NNLM`, recorded as `PL-1X56`'s re-entry, and the record asked
  for here would answer it too.

`stranded`, `orphaned` and the ref walk read `refs/remotes` on purpose, as the
surviving copy of a deleted branch's work, and are not counted.

**Why it matters.** Each instance so far was fixed at its own reader, and the
next reader to need the remote's copy picked its own local stand-in. `PL-C3MN`
was filed in the very commit that landed `PL-WX87`'s fix (`fc46439f`), and
`PL-21KN` ten minutes after it. What they get wrong is who holds an item
(`PL-C3MN` can leave one held by nobody) and whether a pull request may merge
(`PL-21KN` advised two remedies that both misfire). Those are the two answers
the claim record and `arm` exist to make trustworthy. `PL-4Q9B`'s own falsifier
for "no single point" was "A fifth staleness condition arriving that the four
local fixes cannot each absorb". None of its four local fixes reaches any of
these four readers.

**Done when.** One record of what the remote holds, of the form decided below,
is built once per command and consulted by every reader above that now takes a
local copy for the remote's. `PL-C3MN` and `PL-21KN` close against it, each with
the real-git test its own **Done when.** names. A new reader then has one record
to consult, not a copy to pick.

**Decision needed.** Which single record answers "what does the remote hold"
for `claim`, `yield` and `arm`.

**Recommendation:** one `git ls-remote --heads origin` listing per command,
held beside `PL-XBV4`'s snapshot (`vcs.Snapshot`, landed in #1054), and
consulted by every reader that now takes a local copy for the remote's. One
round trip answers every branch at once, which `PL-C3MN`'s rival check needs
and `PL-WX87`'s per-branch `ls-remote` cannot give. It reads the remote without
writing the clone, so `vcs.fetch_remote` goes on refusing `--prune`, and a
deleted branch's tracking ref stays the surviving copy `stranded` exists to
find, which is `PL-4Q9B`'s constraint. Where the listing fails, a reader says
the remote's copy is unknown, as `_on_remote` does now. It costs one round
trip per command beside the fetch `PL-XBV4`'s snapshot already makes.
`PL-XBV4`'s build landed in #1054 on 2026-09-26, so nothing waits on it now,
and re-read on the merged tree that day, `vcs.fetch_remote` still refuses
`--prune`.

Against:
- **`git fetch --prune`.** Among the open members it fixes `PL-C3MN` only. It
  leaves a local branch behind its copy on origin (`PL-21KN`) and the upstream
  setting (`PL-KX73`) as they were. It also deletes the tracking refs that are
  a deleted branch's only surviving copy.
- **Per-reader fixes.** That is the pattern that produced these four instances.

**The nearest head is `PL-XBV4` (done 2026-09-26, #1054), and they stay separate.** Its fact is
the moment a read's sources were taken: "How fresh the refs, working tree and
forge state a read command answered from are". This one is which copy is the
remote's. A fetch made a second ago still leaves every copy these readers
misread. `arm` had fetched when it said `behind 1` (`PL-21KN`). A fetch never
deletes a tracking ref the remote no longer has (`PL-C3MN`), and never touches
the upstream setting (`PL-KX73`). Dating the refs, which is what
`vcs.Snapshot.refs_at` does, cannot reveal any of them. The listing belongs
beside the snapshot because both are one read of the remote per command, not
because they share a fact.

**Generator check.** A head: `PL-4Q9B`'s fact, misread by four readers since
that head closed on 2026-09-19. Three post-close instances count as a generator
whose fix did not hold, and this is four. `PL-4Q9B`, `PL-WX87` and `PL-KX73` are
closed and left as they stand.
