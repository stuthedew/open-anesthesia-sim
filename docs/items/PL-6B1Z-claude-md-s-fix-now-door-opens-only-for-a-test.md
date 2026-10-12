---
id: PL-6B1Z
title: CLAUDE.md's fix-now door opens only for a test-free fix inside the current item's touches, so a small defect found while working something else is filed, triaged and batched instead of fixed where it is found - 176 S defects filed in the two weeks to 2026-10-12, and the door named as taken in two pull-request bodies of about 1,440; the owner asks on 2026-10-12 to fix small defects in place whenever discovered
priority: P2
effort: S
status: needs-decision
classes: docs, session-cost
touches: CLAUDE.md, .claude/skills/docket/modes/capture.md, .claude/rules/citation-drift.md, docs/WORKING_NOTES.md, docs/resident-instructions.md, tools/pr_body_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; a rule change the owner asked for on 2026-10-12, classed by its own design round
added: 2026-10-12
---

**Problem.** CLAUDE.md's fix-now door opens only for a test-free fix inside the current item's touches, so a small defect found while working something else is filed, triaged and batched instead of fixed where it is found - 176 S defects filed in the two weeks to 2026-10-12, and the door named as taken in two pull-request bodies of about 1,440; the owner asks on 2026-10-12 to fix small defects in place whenever discovered

**The ask** (project owner, 2026-10-12, in the v0.6.0 Projects trial's project
chat): "Can we make a rule to fix small defect items in place whenever
discovered?" It arrived beside two others of the same day - batch everything
that waits on his input so the workflow place never halts on it, and no more
items written so that one answer is all they wait for - so the end state is
fewer small defects reaching the queue at all, not a faster queue.

**Why it matters.** The cost of a small defect here is not the fixing but the
bookkeeping around it: a `bin/docket new`, a triage slot filling five fields, a
brief, a place in a batch, a pull request, a close record, and a thread to carry
them. In the two weeks to 2026-10-12, 374 items were filed, 176 of them
S-effort defects; 61 pull requests closed S defects filed in that window, and
37 of those closed one such item alone. The median S defect closed one day after
it was filed, so latency is not what the owner is paying - the apparatus around
each one is.

Where `CLAUDE.md`'s door blocks is specific. Test 1, no new test, excludes every
code defect, because a fix owes a regression test under both of this
repository's standards. Test 2, no file outside the current item's `touches`,
excludes every defect found while working something else, by definition. Test 3
and the cap of two rarely come into it: a session never reaches them. The door
was named as the one taken in two pull-request bodies of about 1,440 (`#532`,
`#595`); a use that did not name it cannot be counted, so that is a floor rather
than a count.

**What was measured, 2026-10-12.** Front matter of every item in `docs/items`
with `added:` on or after 2026-09-28, `effort: S` and `defect` among its
classes, lane computed from `touches` against `docket.toml`'s `workflow_paths`
the way `docket.model`'s `lane` does; a one-off standard-library script in the
thread's scratchpad, not kept, since the question is asked once.

- 176 S defects. 102 are members of a generator head - filed by a sweep that
  found them on purpose, which `CLAUDE.md`'s generator rule governs and this
  rule does not. 74 are not.
- 119 say in their brief that they were found while working another item; 82
  of those are `PL-R417`'s members. 37 are incidental finds by 22 ordinary
  finder items: 19 finders found one, 2 found two, 1 found four (`PL-YZ17`,
  four step-size edge cases of one mechanism, which is the generator rule's
  shape). So a cap of two binds on about one finder in 22, and the one it
  binds on is a cluster the generator rule already takes.
- Lane of the 119: workflow 53, crossing 53 (apparatus code with its tests
  under `tests/unit`), product 13, of which 7 are classed `safety` or
  `science`. About 94% of what the rule would reach is apparatus; the clinical
  floor excludes about 6%, and a product fix found on a workflow branch about
  5%.

**Where.** `CLAUDE.md` § "The queue, and how the project owner works", the
bullet opening "Or fix it now, through a door this narrow" and the housekeeping
bullet's clause pointing at it; `.claude/skills/docket/modes/capture.md`,
whose opening paragraph restates "the three tests" and "the cap of two per
branch"; `.claude/rules/citation-drift.md` § "The decision", which names the
cap; `tools/pr_body_check.py`'s module docstring, which says the fix-now rule
"forbids inline" a commit outside `touches`, which the widened rule will make
false; `docs/WORKING_NOTES.md` § "Settled: when a session may fix a small
finding instead of filing it (PL-3MJH)", which records the narrow design as
what stands; and `docs/resident-instructions.md`, which every edit to the
resident set owes a record. `PL-3MJH`'s own brief is closed and stays as the
record of 2026-09-01 (`.claude/rules/citation-drift.md`). `docs/worker.md`
§ "Rules you may not break" needs nothing: a delegated worker never edits
outside `touches`, and that stays the counterpart of this rule rather than an
exception to it.

**Where the ask overrides 2026-09-01, said plainly.** `PL-3MJH` records three
choices the owner made then, having read Martin Fowler's *Opportunistic
Refactoring* ("I did like the direction your initial 3 rules were headed more
than his more expanded scope"). Two of them this ask overrides, and one it
leaves standing:

- *An extra test or two, in the apparatus only* - set aside then. Overridden:
  a fix that cannot carry its own regression test cannot be a code fix, so
  without this the ask is unmet. The widened door admits the fix's test
  everywhere the door reaches, which under the recommendation below is the
  apparatus and the product paths a branch already waits on a read for.
- *Locality*, test 2, which the owner preferred then over Fowler's "that lack
  of locality shouldn't stop you from making the change now". Overridden:
  "whenever discovered" is the opposite of locality. The two reasons given
  for it - a working queue makes the alternative to fixing a tracked item
  rather than oblivion, and `bin/docket verify` audits the diff against
  `touches` - are both still true, and the second is answered by the record
  the fix now leaves (below) rather than by refusing the fix.
- *Within-branch deferral* - set aside then, and left standing: nobody asked
  for it, and two dispositions, fix now or file, still suffice.

Fowler's page could not be re-read for this round: `martinfowler.com` was
refused at CONNECT with 403 on 2026-10-12, so the quotations are as `PL-3MJH`
recorded them from a reading in full on 2026-09-01.

**Decided in the round**, each an obvious call on a rule this repository
already states or a number above, recorded here so a later session does not
reopen them as questions:

1. **The fix carries its own regression test.** Both standards owe one:
   `CLAUDE.md` § "Architecture and development discipline" for the simulator,
   `.claude/rules/apparatus-standard.md` § "What a test on this side is for"
   for the apparatus, where a test earns its place exactly when its absence
   would let a real defect through. A fix whose test does not fit beside it in
   one commit is an item.
2. **Locality goes, and the record replaces it.** Each fix is its own commit
   led by the current item's id, as now, which is what lets the owner drop it
   in a rebase and what keeps every id-matcher seeing it. Its file is *not*
   added to the item's `touches`: the lane is `touches`-derived and
   `bin/docket concurrent` reads `touches`, so widening them for a fix would
   move the item between lanes and hide the fix from the audit. `bin/docket
   verify --self` names the file as outside `touches` and still ACCEPTs
   (`PL-6QZP`), which is the intended reading, and the pull request body
   carries one line per fix saying what it fixed and where, because a reply
   dies with its session and `docs/pr-bodies` does not (`PL-KQHN`). The
   no-behaviour repair of `PL-G40Z` keeps its own mechanic - declared in
   `touches`, riding the commit already being made - because it has no commit
   of its own to be seen by.
3. **Test 3 stays as the definition of a defect.** No reasonable person could
   prefer the current state: a wrong answer against the code's own stated
   intent, a rule this repository states, or plain fact. A rename, an extracted
   helper, a check somebody might defend - a decision, and decisions are items.
4. **"Small" is one defect, one commit, with its test.** A fix that wants a
   second commit, reaches a second mechanism, or leaves anything to come back
   to is an item. No line count: the one cited for the cap in `PL-3MJH` was
   secondhand, and a commit a reader takes in whole is the unit the rebase
   mechanic already relies on.
5. **The cap stays at two per branch.** Measured above: it binds on about one
   finder in 22, and that finder's four finds were one mechanism, which is the
   generator rule's case rather than this one's - a third find of one
   mechanism is a head to record, not a third fix. A hard count rather than
   judgment, for the reason `PL-3MJH` gives.
6. **A defect an open item already describes is that item's.** It is claimed
   alongside and closed under its own id, as the start mode's batching allows,
   or left to Order item 34's batches - never fixed under another id, because
   `bin/docket record` recovers a closed item's pull request from the newest
   subject naming it, so a fix under another id leaves the item open with its
   fix merged. The coordinator's default reading of the ask, confirmed by the
   count: the inflow the owner is paying for is the unfiled find.
7. **Not for a delegated worker, and not for a session holding no item.**
   `docs/worker.md` forbids a worker any edit outside `touches`, which is the
   audit a delegated review rests on; a session with no item has no id to lead
   the commit and no branch to carry it. A design round's pull request is item
   files only (`.claude/skills/docket/modes/design.md`), so a round files what
   it finds.
8. **The name stays "fix-now".** Every cross-reference uses it and
   `tools/doc_check.py` holds those sentences to the tree; the owner's phrase,
   fix in place, leads the bullet.

**Decision needed.** Where the door stops. Three answers, each defensible, and
the one taken changes what reaches the owner's desk and what the safety floor
keeps out:

- **(a) Everywhere but the clinical floor, and never adding a read hold.** The
  three clinical paths `docs/worker.md` already forbids a worker -
  `src/anesthesia_sim/core/`, `src/anesthesia_sim/data/`, `docs/MODEL.md` -
  and any finding classed `safety` or `science` are filed, not fixed: the item
  is what ranks them `P1`, offers them to the strongest model, and stands as
  the provenance record a clinical fix owes. A fix on the owner's read list
  (`src/`, a test importing the simulator, `docs/MODEL.md`,
  `src/anesthesia_sim/data/`, `README.md`, docket's `arming.py`) is taken only
  where the branch already carries a hold for a read, so a fix never turns a
  workflow pull request that would merge on green into one that waits on the
  owner and stalls the chain behind it; found on a workflow branch, it is filed
  and the product place takes it within the day, as the 13 product finds above
  were. Excludes about 6% and about 5% of incidental finds respectively.
- **(b) Everywhere but the clinical floor.** As (a), but a product fix found
  on a workflow branch is taken and holds that pull request for the owner's
  read, as any `src/` change does, so the chain behind it waits on him for a
  one-commit fix.
- **(c) Everywhere, the clinical floor included.** A `core/` or `data/` defect
  fixed in place with its regression test, the pull request waiting on the
  owner's read as any `src/` change does. Loses the `P1` ranking, the
  strongest-model routing and the item as provenance for exactly the defects
  the safety-critical standard reaches, and puts a clinical fix in a pull
  request titled by another item's id.

**Recommendation: (a).** It takes about 94% of what the narrow door was
refusing, which is where the inflow is; it leaves the safety floor exactly
where `CLAUDE.md` § "Safety-critical clinical-output standard" and the arm rule
already put it; and it serves the owner's same-day ask that the workflow place
never halt on his input, which (b) would undo one incidental fix at a time.
(c) is the Fowler reading, and the floor is the reason this repository has
never taken it.

**Done when.** `CLAUDE.md`'s fix-now bullet states the widened door in the
decided form - the test the fix carries, the record that replaces locality,
the definition of small, the cap, the clinical floor and the read-hold line,
who may not use it - naming what it replaces; `capture.md`,
`citation-drift.md` and `pr_body_check.py`'s docstring say what it now says or
point at it without restating a number it no longer holds;
`docs/WORKING_NOTES.md`'s settled thread records the widening and why;
`docs/resident-instructions.md` records the edit; `make check` is green.

**Generator check.** A one-off, and work the owner asked for: a rule the owner
asked to widen, not a reader misreading a fact. No head's mechanism produces
it, and nothing here reads a fact it could have recorded.

**References.**

- `PL-3MJH` - the 2026-09-01 design, the two widenings set aside, and the
  reading of Fowler's *Opportunistic Refactoring*
  (https://martinfowler.com/bliki/OpportunisticRefactoring.html, refused at
  CONNECT on 2026-10-12).
- `PL-G40Z` - the no-behaviour repair that rides the current commit.
- `PL-6QZP` - what `bin/docket verify --self` does with a file outside
  `touches`: names it, and ACCEPTs.
- `docs/WORKING_NOTES.md` § "Settled: when a session may fix a small finding
  instead of filing it (PL-3MJH)" - why the narrow rule beat the cited source.
