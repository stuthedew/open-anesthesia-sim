---
id: PL-MB2W
title: Who holds an item is derived by every reader from commit subjects, touched paths and ref age and never recorded, so each reader misreads every new shape of work until it gets its own exception - twenty verified members, three still open
priority: P2
effort: M
status: needs-decision
classes: defect
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md, .claude/skills/docket/modes/start.md, CLAUDE.md
added: 2026-09-23
payoff: a claim is one fact every reader reads, so a new shape of work stops costing an item per reader
root-cause-of: PL-X3WZ, PL-7790, PL-N1JK, PL-3CTW, PL-VYSP, PL-2BZY, PL-61MD, PL-MFM4, PL-7TVT, PL-N2PP, PL-3QM9, PL-3W3P, PL-8FJK, PL-8GV1, PL-J16N, PL-QP9Z, PL-1MCK, PL-KWCY, PL-VFJ3, PL-8JQQ
generator: live - who holds an item is derived from commit subjects, touched paths and ref age and never recorded, so each new shape of work is misread by some reader until it gets its own exception; PL-T7Y1's audit verified twenty members, four of them (PL-QP9Z, PL-1MCK, PL-KWCY, PL-VFJ3) filed after PL-7TVT closed spent, and three are open
---

**Problem.** No record says who holds an item. Each reader works it out for
itself, from which id leads a commit's subject, where the commit wrote, and how
old the ref is. Three readers are affected, and each has been patched one shape
at a time:

- `vcs.branches_in_flight`, which `docket next`, `flight`, `show` and the
  session-start digest all read;
- `release`'s collision guard;
- the auto-merge arming rule in `CLAUDE.md`.

`PL-T7Y1`'s adversarial audit verified twenty members; the list is in
`PL-5MYR` under "Verified counts". They fall into three groups:

- **`branches_in_flight`.**
  - `vcs._annotates_only` reads a queue-only commit as a note, and
    `vcs._own_edit_claims` promotes three shapes back to claims: `PL-7790`,
    `PL-VYSP` and `PL-8FJK`. Each promotion followed an incident, and further
    shapes followed each one:
    - a block (`PL-8GV1`);
    - a renamed round (`PL-J16N`);
    - a bystander ref collapsing a live mark (`PL-2BZY`, `PL-61MD`);
    - a commit outside the queue led by a captured or triaged id (`PL-3CTW`,
      `PL-VFJ3`);
    - a note read as work (`PL-X3WZ`), and a pass claiming items for another
      id's reason (`PL-3W3P`);
    - a triage pass (`PL-N1JK`) and a rider (`PL-N2PP`) that no guard sees;
    - a branch dropped from the report once an earlier pull request from it
      merged (`PL-8JQQ`).
  - Age cannot tell a live session from an abandoned one (`PL-7TVT`,
    `PL-3QM9`).
- **`release`'s collision guard** cannot see a session that has not cut yet
  (`PL-MFM4`).
- **The arming rule** decides that a branch is safe to merge because only
  item files ride it. It then has to exempt claims, and it took three patches
  in one day to find which ones (`PL-QP9Z`, `PL-1MCK`, `PL-KWCY`). It now
  defers to "a queue-only commit that start mode reads as one", and that
  catalog is still prose that each session applies by judgment.

**Generator check.** This is the head, at family altitude. `PL-5MYR`'s sweep
counted it, and on 2026-09-23 this session checked those leads against the
titles and the code. `PL-T7Y1`'s audit then verified the membership
adversarially.

- **Removed on that audit, because each is a different mechanism:**
  - `PL-RY2R` and `PL-1X2C`: the file-edit mark kept one carrier per id
    before the landing test ran.
  - `PL-X3NY`: whether a pull request is open is a fact of the forge.
  - `PL-WM46`: the batch note parses subjects by regex instead of calling
    `leading_ids`.
- **Added on the same audit:** `PL-8JQQ`, which survived three skeptics of
  three.
- **Heads that fixed one reader each without stopping the mechanism:**
  `PL-8FJK` and `PL-7TVT`. Both closed verdicts now point here.
  - `PL-4Q9B` (clone freshness) and `PL-BHVM` (landing) do not belong.
- **Not `PL-WNCT`'s mechanism.** `PL-WNCT` is about stranding. The arming
  rule came from `PL-WNCT`'s fix, and the three patches to it are claim
  misreads, not stranding.
- **`PL-KWCY`'s own check** found no generator, which was right at its
  altitude and is superseded at this one.
- **Landing is excluded.** The merge authors that fact, so no session can
  record it (`PL-R808`, `PL-LF2C`).

**Why it matters.** It ranks because it is still producing members, and three
of them are open. Each new shape of work costs a collision, a false mark or a
lost claim, in whichever reader it reaches first, and each fix mends only that
reader.

**Decision needed - the project owner's, because it reopens a ratified
decision.** May the design round record claims, reopening `PL-BHVM`'s "derive,
never record" for claims only?

- `PL-BHVM` § "Ratified (project owner, 2026-09-19, ratified)" refused a
  stored claim. The objection is in `vcs.py`'s module docstring: a session that
  crashes "leaves the item marked in-progress forever".
- A ratified decision reopens on ordinary evidence. The twenty members are a
  cost that round did not carry.
- The standard answer to a crashed holder is a lease, a claim that expires
  unless its holder renews it. Gray CG, Cheriton DR, "Leases: an efficient
  fault-tolerant mechanism for distributed file cache consistency", SOSP 1989,
  https://doi.org/10.1145/74851.74870. The round did not weigh it.

**Recommended: yes, for claims only.** Reopening lets the round weigh two
routes and commits to neither:

- a claim recorded under a lease, which one function reads for every reader;
- reading what the branch does to the item: the item's front matter at the
  tip against the base, plus the start commit. This stays within "derive,
  never record".

What reopening costs is that the round has to design a renewal rule, choose an
expiry time, and find a carrier that is neither an index beside the items nor
a shared document. Both of those are recorded dead ends. What declining costs:
the derivation stands, and the next shape is found by an incident, as the last
twenty were.

**Answered 2026-09-23 under `PL-TH9K`: yes** (project owner, 2026-09-23,
ratified, over keeping claims derived under `PL-BHVM`'s refusal). The design
round may record claims under a lease, and landing stays derived. Choosing
between the two routes above is still the round's decision.

**Then the session's decision, once the owner has answered:** which route to
take, and how the arming rule reads the answer from code instead of restating
start mode's catalog. On either route, `PL-VFJ3`'s false claim is answered by
leading a pass's commits with the pass's own id (`CLAUDE.md` § "Housekeeping
you are about to do yourself is filed before you do it").

**The owner's direction, 2026-09-23.** In their words: "I'd rather fix it right once, then fix it twice" (project owner, 2026-09-23). Of the two
routes above, this reading favours the claim recorded under a lease. The
derived route reads what the branch did to the item, which is still an
inference from the branch, and inference is what produced twenty members. The
round still chooses. Its first question is a carrier the dead ends allow.
Two leads, not findings:

- a field on the item's own copy on the branch;
- one ref per claim.

`docs/worker.md` § "Ref operations a session cannot perform" constrains the
second. A session cannot delete a remote branch or push a tag, and nothing
records whether it can push a ref outside `refs/heads/`. So a ref carrier
could never be removed, and its lease would have to expire on the read side.
Reading the direction this way is this session's call, so ordinary evidence
reopens it.

**Done when.**

- One reader decides who holds an item for `branches_in_flight`, `release`'s
  collision guard and the arming decision.
- A queue-only pass that closes or blocks an item it never claimed reads as in
  flight, with no promotion specific to that shape.
- `CLAUDE.md`'s arming rule names that reader instead of restating start
  mode's catalog.
- The three open members (`PL-MFM4`, `PL-J16N`, `PL-VFJ3`) are closed or
  re-scoped against that reader.
