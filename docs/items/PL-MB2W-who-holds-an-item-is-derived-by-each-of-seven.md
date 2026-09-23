---
id: PL-MB2W
title: Who holds an item is derived by each of seven readers from commit subjects, touched paths and ref age and never recorded, so each reader misreads every new shape of work until it gets its own exception - twenty items filed 2026-09-19 to 09-23, five still open
priority: P2
effort: M
status: needs-decision
classes: defect
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md, .claude/skills/docket/modes/start.md, CLAUDE.md
added: 2026-09-23
payoff: a claim is one fact every reader reads, so a new shape of work stops costing an item per reader
root-cause-of: PL-X3WZ, PL-7790, PL-N1JK, PL-3CTW, PL-VYSP, PL-2BZY, PL-61MD, PL-RY2R, PL-X3NY, PL-MFM4, PL-1X2C, PL-7TVT, PL-N2PP, PL-3QM9, PL-3W3P, PL-8FJK, PL-8GV1, PL-J16N, PL-QP9Z, PL-1MCK, PL-KWCY, PL-WM46, PL-VFJ3
generator: live - who holds an item is derived by seven readers from commit subjects, touched paths and ref age and never recorded, so each new shape of work is misread by some reader until it gets its own exception; twenty members were filed 2026-09-19 to 09-23, five of them the day PL-7TVT closed spent and four after PL-8FJK's fix merged, and five are open
---

**Problem.** No record says who holds an item. Each reader derives the answer
itself, from which id leads a commit's subject, where the commit wrote, and how
old the ref is. There are seven readers:

- `vcs.branches_in_flight`, which `docket next` and `flight` use
- `show`
- `stranded`
- the session-start digest
- `verify`'s batch note
- `release`'s collision guard
- the auto-merge arming rule in `CLAUDE.md`

Each reader has been patched one shape at a time. `PL-5MYR`'s sweep counted
twenty items filed 2026-09-19 to 09-23, by day 7, 3, 1, 4 and 5. Four earlier
items share the mechanism (`PL-X3WZ`, `PL-7790`, `PL-N1JK`), along with the
second half of `PL-VFJ3`.

- **`flight`, `show` and `next`.** `vcs._annotates_only` reads a queue-only
  commit as a note, and `vcs._own_edit_claims` promotes three shapes back to
  claims (`PL-7790`, `PL-VYSP`, `PL-8FJK`). Each promotion followed an
  incident, and further shapes followed each promotion: a block (`PL-8GV1`), a
  renamed round (`PL-J16N`), bystander refs collapsing live marks (`PL-2BZY`,
  `PL-61MD`, `PL-RY2R`), and an outside-the-queue commit led by a captured or
  triaged id (`PL-3CTW`, `PL-VFJ3`). Other readers also misread the same fact:
  - Age cannot tell a live session from an abandoned one (`PL-7TVT`, `PL-3QM9`).
  - `show` names the reader's own branch (`PL-1X2C`).
  - `stranded` cannot tell pull-request work from abandoned work (`PL-X3NY`).
  - `release` cannot see a session that has not yet cut (`PL-MFM4`).
  - `verify` reads any id in a subject as a batch claim (`PL-WM46`).
- **The arming rule** decides a branch is safe to merge because only item files
  ride it. It then has to exempt claims, and it took three patches in one day
  to find which ones (`PL-QP9Z`, `PL-1MCK`, `PL-KWCY`). It now defers to "a
  queue-only commit that start mode reads as one", which is still prose that
  each session applies by judgment.

**Generator check.** This is the head, at family altitude. `PL-5MYR`'s sweep
counted it, and on 2026-09-23 this session checked those leads against the
titles and the code.

- Four heads each fixed one reader without stopping the mechanism: `PL-4Q9B`,
  `PL-BHVM`, `PL-8FJK` and `PL-7TVT`. Five members arrived the day `PL-7TVT`
  closed `spent`. `PL-8FJK`'s closed verdict now points here.
- It is not `PL-WNCT`'s mechanism. `PL-WNCT` is about stranding. The arming
  rule came from `PL-WNCT`'s fix, and the three patches to it are claim
  misreads, not stranding.
- `PL-KWCY`'s own check found no generator, which was right at its altitude
  and is superseded at this one.
- The landing half of the question is excluded. The merge authors that fact,
  so no session can record it (`PL-R808`, `PL-LF2C`).

**Why it matters.** It ranks because it is still producing members. Five
members are open. Each new shape of work costs a collision, a false mark or a
lost claim in whichever reader it reaches first. Each fix mends only that one
reader.

**Decision needed - the project owner's, because it reopens a ratified
decision.** Should the design round be allowed to record claims, reopening
`PL-BHVM`'s "derive, never record" for claims only?

- **What was decided.** `PL-BHVM` § "Ratified (project owner, 2026-09-19,
  ratified)" refused a stored claim. The objection is in `vcs.py`'s module
  docstring: a session that crashes "leaves the item marked in-progress
  forever".
- **Why it is open to reopening.** A ratified decision reopens on ordinary
  evidence. The twenty members are a cost that round did not carry.
- **The answer to the objection.** The standard answer to a crashed holder is
  a lease: a claim that expires unless its holder renews it. Gray CG, Cheriton
  DR, "Leases: an efficient fault-tolerant mechanism for distributed file cache
  consistency", SOSP 1989, https://doi.org/10.1145/74851.74870. The round did
  not weigh one.

**Recommended: yes, reopen it for claims only.** Reopening lets the round weigh
two routes, and it commits to neither:

- a lease-recorded claim, which one function reads for all seven readers;
- reading what the branch does to the item, meaning the item's front matter at
  the tip against the base, plus the start commit. This stays within "derive,
  never record".

What reopening costs:

- The round has to design a renewal rule.
- It has to choose an expiry time.
- It has to find a carrier that is neither an index beside the items nor a
  shared document. Both are recorded dead ends.

What declining costs: the derivation stands, and the next shape is found by an
incident, as the last twenty were.

**Then the session's decision, once the owner has answered:** which route, and
how the arming rule reads the answer from code instead of restating start
mode's catalog. `PL-VFJ3`'s false claim is answered on either route by leading
a pass's commits with the pass's own id (`CLAUDE.md` § "Housekeeping you are
about to do yourself is filed before you do it").

**Done when.**

- One reader decides who holds an item for all seven readers.
- A queue-only pass that closes or blocks an item it never claimed reads as in
  flight, with no promotion specific to that shape.
- `CLAUDE.md`'s arming rule names that reader instead of restating start mode's
  catalog.
- The five open members are closed or re-scoped against that reader.
