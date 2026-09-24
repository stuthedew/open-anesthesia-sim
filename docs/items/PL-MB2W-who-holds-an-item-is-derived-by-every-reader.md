---
id: PL-MB2W
title: Who holds an item is derived by every reader from commit subjects, touched paths and ref age and never recorded, so each reader misreads every new shape of work until it gets its own exception - twenty verified members, two still open
priority: P2
effort: S
status: blocked
classes: defect
feature: parallel-sessions
touches: subprojects/docket/README.md, subprojects/docket/src/docket/vcs.py, docs/items, CLAUDE.md
blocked-by: PL-3FYK, PL-NST2, PL-0TD9, PL-N162, PL-FX5Q, PL-DDYD, PL-331V, PL-J9S0
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged to needs-decision as a generator head by PL-TH9K's session
added: 2026-09-23
payoff: a claim is one fact every reader reads, so a new shape of work stops costing an item per reader
root-cause-of: PL-X3WZ, PL-7790, PL-N1JK, PL-3CTW, PL-VYSP, PL-2BZY, PL-61MD, PL-MFM4, PL-7TVT, PL-N2PP, PL-3QM9, PL-3W3P, PL-8FJK, PL-8GV1, PL-J16N, PL-QP9Z, PL-1MCK, PL-KWCY, PL-VFJ3, PL-8JQQ
generator: live - who holds an item is derived from commit subjects, touched paths and ref age and never recorded, so each new shape of work is misread by some reader until it gets its own exception; PL-T7Y1's audit verified twenty members, four of them (PL-QP9Z, PL-1MCK, PL-KWCY, PL-VFJ3) filed after PL-7TVT closed spent, and two are open (PL-VFJ3 closed in #970)
misread: Who holds an item now, and whether that holder is still live
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
  https://doi.org/10.1145/74850.74870 (the Operating Systems Review reprint is 10.1145/74851.74870). The round did not weigh it.

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

## Design round, 2026-09-24

Run by the session that claimed this item in `7d312a83`, after the first session failed at startup on 2026-09-23. That session's claim branch, `claude/beautiful-brahmagupta-r5ebp0`, had already been deleted from origin in a stale-branch cleanup, so there was no claim left to proceed past. Method: eighteen agents. Five readers mapped the claim code, the twenty members, the lease and git evidence, a lease-term measurement over 300 merged pull requests, and the release guard and arming rule. Three designs were drawn independently (a commit-trailer carrier, a front-matter carrier, and an unconstrained one), and each faced three adversarial lenses: a replay of every member, the constraints and dead ends, and generator growth. A synthesis judge chose among them. All three designs came back holds-with-fixes, and the trailer design won once its fixes were absorbed.

**How it works.** A session takes an item by running `bin/docket claim`, which commits an empty `Claim: PL-X <branch>` trailer on its own branch. Every reader then asks one function, `claims.holdings()`, instead of inferring from subjects and paths, and leading ids go back to meaning attribution only. The claim lives only on the holder's branch, so nothing lands in the store and nothing conflicts. It ends in one of five ways:

- a `Yield:` trailer;
- the branch's copy closing the item;
- a takeover (`claim --over`);
- landing, which stays derived;
- seven days without a commit on the branch.

A branch that changes an item's `status` (a grooming pass dropping or blocking it) holds that item under one status rule, with no promotion specific to that shape. `bin/docket arm` answers the arming question from the same reader.

**Recommended.** The branch-bound trailer design wins. Its reader is a new `claims.holdings()` in its own module, and it takes grafts from the other two designs and from all nine verdicts. A `Claim:` trailer on the holder's own branch records who holds an item. Landing stays derived, as the owner decided on 2026-09-23 (ratified). Leading ids go back to meaning attribution only. The one generic status rule covers every disposition.

Why not the `held:` field. It is the one-way door the "count what undoing it would cost" rule warns about. Every squash carries it into the item store, which lasts for years. It conflicts with a concurrent `status` or `classes` edit (tested with real git). A second hold on an item with a leftover `held:` line makes the writer raise, because `with_front_matter_field` refuses to write a field the item already records (model.py:1543). A trailer adds nothing to `docs/items/`, and a copy that reaches main is inert because base commits are never read for claims. The only live claims are empty commits on unlanded refs, and the lease bounds how many there are.

Why not "open". It uses the same carrier but keeps the reader inside the 6,456-line vcs.py. It ties the holder to a ref, so two sessions on one ref cannot be told apart. Its 24h lease puts the error on the expensive side.

Grafts:
- From frontmatter: the item names its own resource, so the release train needs no flag.
- From the generator lenses: a 7-day lease, plus an explicit takeover with `claim --over <ref>`.
- From the constraints lenses: `claim` never pushes onto a branch that already has an upstream, and cuts stay a hold of their own.
- From the replay lenses: a claim needs the item to exist at the fork and on the base, landing is judged per claim, and a CI check refuses a claim that orders behind another.

This run went past the dead claim. `claude/beautiful-brahmagupta-r5ebp0` is gone from origin, so there was nothing to take over. The only PL-MB2W claim is this session's own 7d312a83.

### Spec

**Carrier.** A trailer in the last paragraph of a commit on the holder's own branch. Only `claim` and `yield` write it.
- Grammar: `Claim: <ID> <branch> [<session>] [over <ref>@<hash>]` and `Yield: <ID> <branch>`. The subject stays `<IDs>: start`.
- Read with `git log --no-merges --format=%H%x1f%aI%x1f%cI%x1f%(trailers:key=Claim,valueonly,separator=%x1e)… <base>..R`. This needs git 2.22; an older git declines.
- A claim counts for ref R only when R's name, without `origin/`, equals `<branch>`. Bystanders, cherry-picked recoveries and merged-in branches hold nothing, and a local branch folds into its tracking ref.
- Base commits are never read for claims.
- `<session>` comes from `CLAUDE_CODE_REMOTE_SESSION_ID` (a lead). It decides `mine` and is printed for `get_session`. It never decides order.

**Write path: `bin/docket claim <ID>… [--over <ref> --reason "…"]`.**
1. Fetch. If the fetch fails, refuse, unless `--no-fetch` is given.
2. Exit 3 and write nothing when a live claim on another ref orders first. Two exceptions: `--over` names that claim, or that ref's tip is an ancestor of HEAD (a continuation).
3. Refuse on a detached HEAD, or on an id HEAD does not hold.
4. Make one empty commit, with the attribution lines in the same paragraph.
5. Push only when HEAD has no upstream. Otherwise print `arm`'s verdict ("hold - disarm, then push").
6. After the push, fetch and re-read. If the claim is not first, exit 3 with the yield line. If the push fails, exit 4 and say the claim is local.

`yield <ID>` writes `Yield:`. A session has two things to remember: `claim` at pickup and for each rider, and `yield` when it stops without closing.

**Other holds.**
- **Disposition.** R holds X when all of these are true:
  - X exists at fork(R) and on the base;
  - R's tip `status:` differs from the fork copy and from the base copy;
  - the base has not superseded R's copy (the existing test for `editing`).

  It is read by id prefix, so a rename does not matter, and it reads `status` only. Other field edits stay `editing`, which is why PL-3W3P's 96-item pass holds nothing. It runs on R's lease, never orders against claims, and never holds arming.
- **Cut.** A notes file on an unlanded ref that is not mine, which is today's `cuts_in_flight` read. It always refuses a release.
- **Branch-name id.** The id in a branch named for its item, under the same lease.

**Lease.**
- Term: 7 days, with no ε.
- Renewal: R's non-merge commits, dated by `%cI`. The owner's Update-branch merge never renews.
- A claim is live while all of these hold: no `Yield`, no `over` supersedes it, it has not landed, and no gap longer than the term appears in [the claim, the later non-merge commits, now].
- A broken chain revives only through a new `claim`, which gets a later stake.
- Order, not fencing: `(%aI, hash)`. The author date survives a rebase, and `over` sorts ahead of the claim it names.
- Each invocation uses one UTC `now`.

Evidence for the term:
- Across 300 PRs, the longest gap inside a live session was 8.43h (#967), and the longest wait from last session commit to merge was 8.61h (#968).
- Main's gaps over 24h in 34 days were 27.1h, 39.9h, 44.6h and 92.1h. These are owner absences, and a session waiting on the owner cannot renew.
- 7 days clears 92.1h by 1.8 times. The cost is dead claims held up to 7 days, and it measures at 0 open items today.
- Revisit: shorten the term if dead claims on open items need more than 3 `--over` takeovers in 30 days. Lengthen it after any false lapse.

**Fence.** `branch_id_check`, run in CI, fails a branch whose claim orders behind another live claim on the same id.

**Release.** A claim ends in one of five ways:
- `Yield`;
- the branch's copy reaches done or dropped (and blocked, pending the owner);
- an `over` supersedes it;
- it lapses;
- it lands. Landing is derived: containment or squash-content (vcs.py:1729-1766), closed on the base (vcs.py:1823), or the landed prefix. The landed prefix is the newest commit k in `base..R` whose added blobs have all been on the base, and it spends every claim at or before k. That replaces `_taken_on_base` and stops reading leading ids on the base.

**The reader.**
```python
def holdings(root, *, now, items_dir="docs/items", include_remote=True, include_head=True, term=LEASE_TERM, runner=None) -> Holdings
```
- `Hold` fields: key, ref, kind (claim, disposition or cut), state (live, lapsed or released), since, renewed, session, status, mine, on_base, legacy.
- `Holdings` offers `ids`, `order(key)`, `holder(resource)`, `lapsed_open()` and `flight() -> FlightReport`.

Its four consumers:
1. **In flight.** `branches_in_flight` becomes `holdings().flight()`, and about 30 call sites stay unchanged. `precedence` becomes `order`, and `settled_branches` reads released holds.
2. **Release guard.** `_cuts` and `cmd_release` refuse on a live `holder("release-train")` that is not mine, or on a cut hold that is not mine. `cmd_release` also refuses when HEAD holds no train claim. The resource comes from an item field, `resource: release-train`, which release mode stamps at filing.
3. **`arm`.**
4. **`claim`.**

**Arming command.** `bin/docket arm` answers for HEAD:
- `arm` (exit 0): the net `base...HEAD` diff lies under `items_dir`, no unreleased claim is bound to this branch, and the branch is not behind main;
- `hold` (exit 1): names the claim or the paths;
- `behind N` (exit 1): the PL-S5MF clause;
- `unknown` (exit 2): the base is not established, or a ref could not be read.

CLAUDE.md's bullet becomes: "Whether it arms is `bin/docket arm`'s answer, asked before arming and before every later push while a pull request is open."

**Deleted.**
- From vcs.py: the claim use of `_annotates_only`; `_Walk`'s claim fields and `credit_claims`; `_queue_only_touches` and `_queue_only_work`; `_deciding_on_base`, `_modified_by` and `_own_edit_claims`; `_closed_at_ref`, which becomes `status_at`; `_claimed_again_since` and `_taken_on_base`; `Carrier`, `_head_carries` and precedence's re-walk.
- Prose: start.md:50-78; CLAUDE.md's arming catalog; the stale claims about subject parsing at CLAUDE.md:408 and 488, the guard bullet in instruction-writing.md's rule 14, and README.md:1534; and the "no item id by design" lines at vcs.py:4066, cli.py:2570 and README.md:1535.
- Kept: the landing machinery, `leading_ids`, `editing`, `unattributed`, and the guards for unread and unbounded refs.

**Migration.** A claim commit is legacy when its own tree lacks `subprojects/docket/src/docket/claims.py`. The test is exact, needs no clock, and still holds after the branch merges main. A legacy commit is read by the old explicit rules only, under the same lease and with no promotions:
- an empty `<ids>: start` commit, bound to its ref;
- ids leading a commit that reaches outside the queue.

The new CI clauses skip legacy commits. A later item removes this path once `flight` prints `legacy refs: 0`.

**Forgetful session.** Three catches:
- The first-edit hook adds "this branch claims nothing: `bin/docket claim <id>`" to an edit outside `items_dir`.
- `branch_id_check`, run by `make check` and by CI, fails a `claude/*` branch that has a non-legacy commit reaching outside `items_dir` and no live claim. The check is per branch, not per id, so captured or triaged ids are never pushed into claims.
  - *Built by `PL-J9S0` as no claim in any state* (2026-09-24): a branch releases its claim by closing its item, so "no live claim" read literally fails every finished pull request. A branch named for its item holds it by the name. "The queue" is the items, the roadmap and the working notes, since triage and design rounds write all three, and "outside `items_dir`" alone would make a triage pass claim the ids it triaged. `PL-J9S0` records the reasoning.
- `flight` lists an `unclaimed:` row for each such branch, which is where the count comes from.

Residual: a queue-only round that forgets to claim. This is stated rather than audited.

### Why the other two designs lost

**Frontmatter (`held:` on the item's own copy).** Every verdict held-with-fixes. It lost on the one-way-door count and on conflicts.
- The constraints lens reproduced a merge conflict with a concurrent triage `status` edit and with a grooming `classes` edit, in scratch/conflict. Today's empty start commit never conflicts.
- The replay lens showed that any hand-merged round or partial landing leaves `held:` on main, and the next `hold` then raises `ValueError` (model.py:1543).
- A rider hold edits another item's file, and verify rejects that (verify.py:2174-2187), so the design would need a new sanctioned-edit kind.
- `git grep '^held: '` also matches brief bodies.
- Every squash leaves residue in the store, so the cost of undoing it grows with each item touched on main. That fails "count what undoing it would cost".

Its good ideas are grafted in: the item names its resource, lapse is judged on the read side, and the lease is long. Everything else in the design can be fixed, but its carrier cannot.

**Open (trailer read inside `branches_in_flight`).** Same carrier, weaker structure.
- The replay lens rated one issue blocking: a rightful successor, whether a handoff or this very run, has no way past a live dead claim. The generator lens rated a second blocking: a 24h lease that lapses in every owner absence. Main had four such absences over 24h in 34 days, and the fencing then tells the session that holds the work to yield.
- It keys the holder to a ref, so PL-8JQQ's two sessions on one ref cannot be told apart.
- It deduplicates carriers to whichever renewed last, which brings back PL-2BZY's collapse whenever a session merges another branch into its own.
- Dispositions carry no lease and no check that the item existed at the fork. On the current refs that is 10 latent false holds, 8 of them captures.
- It keeps the reader inside vcs.py.

Its per-claim precedence and its break-then-reclaim chain are grafted in.

**Trailer, as submitted.** It won only after the fixes it needed:
- a 24h lease, raised to 7 days;
- `claim`'s default push onto an armed branch, which reproduced PL-QP9Z;
- `--no-push` stamps that could outrank a claim already published;
- `cuts_in_flight` narrowed to CutOn, which blinded the guard to a forgetful release session;
- `--release` as a flag the session has to remember;
- legacy status decided from the merge-base, which moves when main is merged in;
- the per-id `unclaimed` remedy, which forced attribution into claims (PL-VFJ3, PL-3CTW).

### Verifier findings the spec absorbed

Blocking, both absorbed:
- **Takeover.** The replay lens on the open design, echoed by all six trailer and frontmatter lenses: a successor could not get past a live dead claim. Added `claim --over <ref> --reason`. It writes `over <ref>@<hash>`, sorts ahead of the claim it names, and is backed by get_session or the owner's word. A continuation, where HEAD contains the old tip, is accepted automatically.
- **Lease on the expensive side.** The generator lens on the open design. The term is now 7 days, measured against a 92.1h owner absence, and paired with takeover.

Fixable, absorbed:
- **Armed branch.** `claim` never pushes when an upstream exists, and prints `arm`'s verdict instead.
- **Invisible or late claims.** `claim` fetches before and after its push. `--no-push` is gone.
- **Ordering.** It is called ordering, with the fence in CI. `since` is `%aI`, renewal is `%cI` from non-merge commits only, and there is one threshold and one `now`.
- **Dispositions.** They need the item at the fork and on the base, and pass the supersession test. They read status only, carry the lease, and never order against claims or hold arming.
- **`_taken_on_base` lost.** Replaced by the landed-prefix test.
- **Legacy.** Decided per commit tree. CI skips legacy commits.
- **Release.** The resource is an item field, cut holds are kept, and `cmd_release` needs HEAD's train claim.
- **`arm`.** It gains `behind` (PL-S5MF) and `unknown`.
- **Check.** Per branch, not per id.
- **Prose.** Four more stale passages were added to the list.
- **Lapsed rows.** Only open items are listed.
- **Shallow clones.** The unbounded and unreadable guards are inherited.
- **Rebase.** Documented as a renewal.
- **Figure.** 2 of 200, not 182, reach main with a branch trailer, and they are inert anyway.

Rejected:
- **An audit of queue-only rounds.** It would rebuild the promotions.
- **Treating any front-matter change as a disposition.** PL-3W3P's 96-item `verify:` pass would come back.
- **Renewing only on commits led by the claimed id.** That reads attribution again, and the landed prefix covers it.
- **Parsing `%B` in Python.** Declaring git 2.22 is cheaper than copying git's trailer rules.
- **A weak hold that only `next` reads.** Pre-registered instead: add it back if more than 1 in 20 work branches reach a push unclaimed.

### The members against this design

- `PL-X3WZ`: Answered. Leading ids never claim, so captures, triage, record and recovery commits hold nothing. The claim use of _annotates_only is deleted.
- `PL-7790`: Answered. The session that runs `claim` holds a queue-only deliverable. Promotion A is deleted.
- `PL-N1JK`: Answered for status moves, which become dispositions. Edits to other fields stay `editing` on purpose (see PL-3W3P).
- `PL-3CTW`: Answered. Captured ids are attribution only, and the CI check is per branch, so it never pushes them into claims.
- `PL-VYSP`: Partly answered. A round claims at pickup, which is start mode's first step. A round that forgets to claim is a stated residual.
- `PL-2BZY`: Answered. A claim is bound to its branch token, so a bystander ref that carries the commit holds nothing.
- `PL-61MD`: Answered, for the same reason as PL-2BZY. `own_edits` is deleted.
- `PL-8JQQ`: Partly answered. The landed-prefix test spends the claim that landed, and continued work claims again. The gap between the merge and the next push remains.
- `PL-3W3P`: Answered. A `verify:` rewrite changes no status, so it shows only as `editing`.
- `PL-8FJK`: Answered. A close is a disposition under the one status rule, and promotion C is deleted.
- `PL-8GV1`: Answered, with no rule specific to this shape (done-when 2). A block is a disposition. It stays dropped, and item 1 tests it.
- `PL-J16N`: Re-scope while still open. Its claim half is moot: no claim reader reads rename paths, and dispositions read by id prefix. It becomes the fake runner's `--name-only` rename fidelity, with a real-git test, because `editing` still reads diff paths.
- `PL-N2PP`: Partly answered. A rider is one `claim` call. The window before the first push cannot be closed by any carrier that lives on a ref.
- `PL-7TVT`: Partly answered. A dead claim lasts at most 7 days and prints its session id, so `get_session` plus `--over` can take it over.
- `PL-3QM9`: Not a claim problem. Date arithmetic, already fixed.
- `PL-QP9Z`: Answered. `arm` holds the branch while a claim is unreleased, and `claim` never pushes onto an upstream.
- `PL-1MCK`: Answered. `arm` reads trailers whichever push carried them, and there is no catalog.
- `PL-KWCY`: Answered. Closure in the branch's own copy releases the claim. Whether blocked also releases it waits on the owner.
- `PL-MFM4`: Closed by item 5. The release-train resource comes from an item field and is claimed at filing. `_cuts` and `cmd_release` refuse, and the cut hold is kept.
- `PL-VFJ3`: Already closed (#970). The mechanism is gone, since leading ids never claim. Fix the brief's 'three open' drift.

### Open questions

**The owner's: Should a claim also be released when the branch's own copy moves to `blocked`, not only when it is closed? PL-KWCY's arming rule currently says 'until its item is closed'.** It changes the wording of PL-KWCY's ratified arming rule. CLAUDE.md says a ratified decision reopened on ordinary evidence goes back to the owner. The question is held in `PL-3FYK`, which defines the constant.

*Recommendation:* Yes. A session that blocks its own item has stopped working it. Holding the claim strands a queue-only branch that never arms. It is one constant (`RELEASING_STATUSES`), so no item waits on the answer.

**Answered 2026-09-24: yes** (project owner, 2026-09-24, ratified, over holding the claim until the item closes). Recorded in `PL-3FYK`, and `CLAUDE.md`'s arming bullet was amended in the same session. The owner also agreed with the round's decided recommendations below.

**Decided by the round, which ordinary evidence reopens:**

- Carrier: a `Claim:` trailer bound to the branch, or a `held:` field on the item? Decided: The trailer. It is decided. (The owner delegated the carrier to the round. It is apparatus, and nothing a learner sees changes.)
- How long is the lease? Decided: 7 days, renewed by non-merge commits. Shorten it if dead claims on open items need more than 3 `--over` takeovers in 30 days. Lengthen it after any false lapse. (A measured, reversible constant in the apparatus.)
- What evidence does `claim --over` need? Decided: The owner's word, or `get_session` showing ARCHIVED or failed. The reason goes in the claim commit's body. (A procedure detail with a small blast radius.)
- Should CI fail a branch whose claim orders behind another live claim? Decided: Yes. Build it in item 6, after checking that CI's `fetch-depth: 0` checkout holds every head (currently a lead). (It enforces the ordering already decided, and item 6 verifies the premise first.)
- Should branches that claim nothing get a weak hold that only `next` reads, as a fallback? Decided: No. Pre-register a re-add if more than 1 in 20 post-cutover work branches reach a push unclaimed, counted from `flight`'s `unclaimed:` rows. (The break-even is stated, and the choice is reversible.)
- Should a queue-only round that forgets to claim get a check? Decided: No. It is a stated residual, because a check would re-derive the promotions. File an item if one auto-merges mid-round. (An apparatus trade-off with the reasoning recorded.)

### Build

Filed under `feature: claim-record`, in build order. This item is blocked on the first eight and closes with its own remaining work: the close-out that was the synthesis's item 7 (the `vcs.py` docstring changes from "derive, never record" to "claims recorded, landing derived", the README gets a claims section and states the git floor, `PL-J16N` is re-scoped to rename fidelity in the fake runner, and the answered members are closed). `PL-CH3Z` follows once `flight` prints `legacy refs: 0`, and does not block this item.

1. `PL-3FYK`: Record who holds an item as a Claim trailer bound to the holder's own branch, read by one claims.holdings reader under a 7-day lease
2. `PL-NST2`: claims.holdings reads status dispositions, the landed prefix, the item resource field and cut holds, and adapts to FlightReport
3. `PL-0TD9`: bin/docket claim and yield write the claim, and start mode is rewritten around them
4. `PL-J9S0`: branch_id_check fails a work branch that holds no claim and a claim that orders behind another live claim, and the first-edit hook says to claim
5. `PL-N162`: Rewire branches_in_flight, precedence and settled_branches onto claims.holdings
6. `PL-FX5Q`: Delete the claim inference and the three promotions from vcs.py, with their tests
7. `PL-DDYD`: bin/docket arm decides auto-merge arming, and CLAUDE.md names it instead of restating start mode's catalog
8. `PL-331V`: Model the release train as a claimed resource, so the release collision guard sees a session that has filed a release item but not cut
9. `PL-CH3Z`: Delete the legacy claim reading once bin/docket flight prints legacy refs: 0

### Not measured

Not measured, and any of these could overturn a choice:
- **Push times.** None are recorded, so the lease rests on commit gaps only.
- **Owner absence.** Nothing measures an absence longer than 7 days while a session waits.
- **Clock skew.** Skew between containers is unmeasured.
- **CI refs.** Whether CI's `fetch-depth: 0` checkout holds every head is a lead. The CI fence depends on it, and item 6 checks it first.
- **Session id variable.** Whether `CLAUDE_CODE_REMOTE_SESSION_ID` is present in every container is a lead. It is `cse_01ML3…` here, while `get_session` uses the `session_` prefix.
- **Landed-prefix test.** Its cost on long branches is untested. Its behaviour where the squash-content test cannot prove landing (PL-LKFP's ROADMAP.md case) leaves the claim live until a yield or the lease.
- **Empty commits on GitHub.** Whether GitHub's rebase-style Update branch drops empty claim commits is unknown. Update with merge keeps them, and maintainer.md already advises merge.
- **Unverified primary sources.** Kleppmann and Chubby were checked only through snippets or secondary notes, and the Gray and Cheriton term figure is a lead.
- **Repeat misses.** How often a forgetful queue-only round or a two-session ref will recur after cutover is unmeasured. Both are pre-registered, not measured.
- **Lapse counts.** The 0-open-items count behind the 7-day cost came from local `origin/claude/*` refs that were not freshly fetched.

### References

- Gray CG, Cheriton DR. Leases: an efficient fault-tolerant mechanism for distributed file cache consistency. SOSP 1989, pp. 202-210. https://doi.org/10.1145/74850.74870. The OSR 23(5) version is https://doi.org/10.1145/74851.74870, and its abstract is at https://api.openalex.org/works/doi:10.1145/74851.74870.
- Kleppmann M. How to do distributed locking (2016), on fencing tokens: https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html. Checked through search snippets only.
- Redis docs, distributed locks, 'implement fencing tokens': https://raw.githubusercontent.com/redis/docs/main/content/develop/clients/patterns/distributed-locks.md
- Kubernetes coordination/v1 LeaseSpec: https://raw.githubusercontent.com/kubernetes/api/master/coordination/v1/types.go
- client-go leader election, 'does not guarantee ... fencing', and the skew rule: https://raw.githubusercontent.com/kubernetes/client-go/master/tools/leaderelection/leaderelection.go
- Chubby sequencers and lock-delay, secondary notes only: https://github.com/jguamie/system-design/blob/master/notes/chubby-lock-service.md
- git RelNotes 2.22.0, %(trailers:key=,valueonly,separator=): https://raw.githubusercontent.com/git/git/master/Documentation/RelNotes/2.22.0.adoc
- git RelNotes 2.32.0, commit --trailer: https://raw.githubusercontent.com/git/git/master/Documentation/RelNotes/2.32.0.adoc
- GitHub squash commit message settings: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/configuring-commit-squashing-for-pull-requests
- GitHub REST repos, squash_merge_commit_title and squash_merge_commit_message: https://docs.github.com/en/rest/repos/repos
- GitHub merge methods, rebase drops commits that were empty to begin with: https://docs.github.com/en/pull-requests/reference/pull-request-merges
- Code: subprojects/docket/src/docket/vcs.py:1729-1766 (landing), :1823 (closed on base), :2207-2278 (promotions deleted), :4171 (cuts_in_flight); model.py:67 (OPEN_STATUSES), :1543 (writer raises on an existing field); .claude/skills/docket/modes/start.md:29-78; .github/workflows/quality.yml:140 (fetch-depth 0)
