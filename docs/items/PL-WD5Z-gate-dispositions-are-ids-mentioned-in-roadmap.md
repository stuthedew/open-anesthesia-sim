---
id: PL-WD5Z
title: Gate dispositions are ids mentioned in ROADMAP.md prose rather than a field on the item, a second store of queue state that four items filed 2026-09-22 and 09-23 each disagree with (PL-58JD, PL-59QW, PL-FD5Q, PL-VFJ3), after three heads each fixed a reader of it
priority: P2
effort: M
status: done
classes: refactor, infra
feature: gate-disposition-store
milestone: v0.5.9
touches: ROADMAP.md, subprojects/docket/src/docket, subprojects/docket/tests, subprojects/docket/README.md, tools/doc_check.py, tests/unit/test_doc_check.py, tests/unit/test_docket_gate.py, docket.toml, .claude/skills/docket/modes/triage.md, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed as a generator head
added: 2026-09-23
closed: 2026-09-23
pr: 970
payoff: a debt item captured during a frozen gate carries its own disposition, so triage stops going red in CI over a ROADMAP.md entry and the gate's deferral list can no longer disagree with the store
verify: grep -q 'def test_an_open_debt_item_the_gate_neither_places_nor_defers_is_an_error' subprojects/docket/tests/test_checks.py
root-cause-of: PL-58JD, PL-59QW, PL-VFJ3
generator: spent - route 1 moved the disposition onto the item, so a debt capture during a freeze owes its own deferred-from: field, which bin/docket check requires, and nothing reads ROADMAP.md prose for one; the second store the three members came from no longer exists
misread: A debt item's gate disposition: whether a milestone's gate clears it, defers it, or still owes one
---

**Problem.** A debt item's gate disposition (declined to a later gate,
deferred, or cleared by the milestone itself) is recorded as the item's id
appearing in a `ROADMAP.md` subsection, inside sentences written for a human
reader. The item file does not carry it. So the disposition is queue state
held in a second store beside the items, and each way the two stores can
disagree has become an item of its own:

- **A second place to write**, which the triage mode never mentions: `#953`
  followed the mode, went red in `checks` on eleven debt captures with no
  v0.6.0 entry, and its fix commit then marked the items it led with as in
  flight (`PL-VFJ3`).
- **Status narrated in prose that nothing re-reads** when the item moves:
  `PL-YZJD`'s deferral entry still read "At `needs-decision`" with the item
  `done`, found by comparing all 27 deferral entries by hand (`PL-59QW`).
- **Parsed back out by a regex over whole subsections**, so a sentence saying
  an item was *absent* disposed of it (`PL-58JD`). That is the `_declined_ids`
  shape `PL-H6VQ` measured in `tools/doc_check.py` on 2026-09-20, now in
  `docket.roadmap`, where `PL-J6HP` gathered the gate readers.
- **A question answered from the wrong section**: `bin/docket wave` counts
  five of v0.6.0's own Required-scope items as outside work the gate waits on
  (`PL-FD5Q`).

**Generator check.** One mechanism shared by four open items that no head
names. Three closed heads worked on readers of this same record: `PL-HWW1`
(Required scope, 2026-09-19), `PL-2T03` (the release train, 2026-09-19) and
`PL-J6HP` (gate facts parsed once in `docket.roadmap`, closed 2026-09-23 as
`spent`). Each fixed how the prose is read, and none changed the fact that it
is prose. `PL-FD5Q`, `PL-58JD` and `PL-59QW` all landed within a day of
`PL-J6HP`'s `spent` verdict. Sharing a file is not sharing a mechanism, so the
claim is narrower than "`ROADMAP.md`". It is that a disposition is an id
*mentioned* in prose rather than a field on the item it disposes of.

**Why it matters.** It is `live` because every debt capture made while a gate
is frozen owes a new entry (`PL-VFJ3`), and this item's own capture owed one.
So the mechanism's inflow tracks capture volume, which is the busiest flow the
workflow lane has. It is also a dead end already refused under another name. A
disposition list in a shared document is "one shared queue document", which
this project rejected because "it serializes every writer, which is the
property one-file-per-item exists to buy" (`subprojects/docket/src/docket/model.py`).
A branch that captures debt during a freeze and a branch that triages it both
have to write the same subsection.

**Decision needed.** Where a gate disposition lives. There are three routes:

1. **On the item.** A front-matter field carries the disposition and its
   reason, and `docket set` writes it. `ROADMAP.md`'s Declined subsections are
   then rendered from the field or reduced to a pointer. `docket check` can
   require the field of a debt capture made during a freeze, which retires
   `PL-VFJ3`'s instruction instead of adding one, and there is nothing left to
   narrate (`PL-59QW`) or mis-parse (`PL-58JD`). Cost: every existing entry
   has to be migrated (`PL-H6VQ` counted 97 prose-only dispositions on
   2026-09-20), the gate section of `ROADMAP.md` changes shape, and the new
   field is admitted under the `PL-6Q9L` pause only because it fixes a live
   generator.
2. **Structured lines in `ROADMAP.md`.** Each entry gets its own line and the
   disposition is the id that leads it, with prose after the id and no
   narrated status. This keeps the gate readable in the document the owner
   reads, and it fixes the parse (`PL-58JD`). It leaves the second place to
   write (`PL-VFJ3`) and the narration (`PL-59QW`) to checks, which is the
   pattern the three heads above already followed.
3. **Keep the representation and fix the four instances.** This is the
   cheapest route today. On the evidence of three heads, the expected outcome
   is more members.

**Recommended: route 1.** It is the only route that removes the second store
rather than guarding it, and it is the answer the project already gave for
every other kind of queue state. Route 2 is the fallback if the gate should
stay readable in `ROADMAP.md` itself. It costs a second store held together by
checks, which is where the current members came from.

**Decided: route 1, the disposition on the item** (project owner, 2026-09-23,
ratified, over route 2's structured lines in `ROADMAP.md` and route 3's four
instance fixes). The decision round checked the case against the tree first,
and four findings changed it:

- **The migration is 39 entries, not 97.** v0.6.0's five deferral subsections
  hold 39 entry ids, 24 open and 15 closed, and their 10 prose-only ids
  dispose of nothing still owed. `PL-H6VQ`'s 97 counted v0.5.0's gate, which
  shipped. `check_gate_dispositions` reads only the current gate
  (`_current_gate`), and `bin/docket wave` does the same.
- **Route 1 closes both halves of `PL-VFJ3`.** The second half is the fix
  commit that marked its leading ids in flight. That happened because the
  commit wrote `ROADMAP.md`. A commit whose whole diff is under `docs/items/`
  is annotation, not a claim (`vcs._annotates_only`). So a triage pass that
  records a disposition on the item cannot mark anything in flight, whatever
  ids lead its commit. That removes what set off this instance. It does not
  remove the general mechanism, a claim read from a commit's shape. That
  mechanism belongs to `PL-MB2W`, re-filed as a head in `#967`, which also
  lists `PL-VFJ3`, so closing it here counts toward both heads.
- **The prose had already drifted where nothing reads it.** All four of
  v0.6.0's post-freeze subsections are headed "Declined to Gate 2". v0.6.0's
  gate *is* Gate 2 ("The timeline", row 6), so the target should be Gate 3.
  The heading grammar reads only the verb, so four triage passes copied the
  error forward.
- **`PL-FD5Q` is not this mechanism, so it is off `root-cause-of:`.**
  `GateStatus.outside_items` never subtracts Required scope. That is a reader
  defect, and moving the disposition onto the item does not fix it. It is
  fixed in this item's branch as its own commit, because both changes rewrite
  `docket.roadmap`'s gate readers. The other three members still make this a
  generator.

**Build plan.** This was written for the session that builds it, because the
decision round stopped for length.

1. **The field.** `deferred-from: vX.Y.Z - <why>`, one line on the item. The
   version names the gate the item is excused from, not the gate it goes to.
   A target is what "Declined to Gate 2" got wrong, and the next freeze takes
   every open debt item anyway. Add `Item.deferred_from`, put it in
   `FIELD_ORDER` after `blocked-by`, and add it to `_front_matter_values` and
   the parse. `bin/docket set <id> --deferred-from "..."` writes it. That is
   a new flag beside `--payoff`, and it writes through
   `with_front_matter_field`, which does not reorder keys. Document it in the
   item format in `subprojects/docket/README.md`.
2. **The rule moves into `bin/docket check`** (`checks.py`), the `make docket`
   the triage mode already runs. Port `check_gate_dispositions` and its tests,
   including `test_this_repository_records_a_disposition_for_every_open_debt_item`.
   While a current gate exists (`roadmap.current_gate`), an open item that is
   debt must be placed (`MilestoneSection.scope_ids`) or carry `deferred-from:`
   naming that gate's version. Debt means a debt class or `needs-decision`.
   The error prints `bin/docket set <id> --deferred-from "vX.Y.Z - <why>"`. Also
   refuse a malformed value: an unparsable version, a version whose section
   records no gate, or an empty reason. Refuse an item the current gate both
   places and defers. With no readable roadmap, decline the way `checks.py`'s
   milestone blockers already do. Delete the rule from `tools/doc_check.py`,
   together with `_deferral_headings` and the comment block above it.
3. **The prose parse goes.** Delete `DEFERRAL_VERBS`, `DECLINED_HEADING_RE`,
   `_deferral_subsections`, `_declined_ids`, `_deferral_entries`, and
   `MilestoneSection.deferral_entries` and `.deferred_ids`, along with their
   tests. The `Declined`, `Deferred` and `Sequenced` subsections in released
   sections stay as history that nothing parses.
4. **`bin/docket wave`**. `render._deferral_lines` lists the items whose
   `deferred_from` names the gate's version, with the same open, shipped,
   unreleased and dropped split it prints now.
5. **Migration.** A throwaway script writes `deferred-from: v0.6.0 - <ground>`
   on each of the 39 ids, open and closed alike, so `wave`'s count is
   unchanged. It takes each ground from its subsection's opening paragraph,
   compressed to a clause. Diff `wave` before and after.
6. **`ROADMAP.md`.** Replace v0.6.0's five deferral subsections with one short
   subsection that states the post-freeze ground once and points at
   `bin/docket wave`. Rewrite § "The debt gate" → "Recording it" so a deferral
   is recorded on the item and `bin/docket check` requires it. Remove every
   sentence that names a deleted symbol from the current and future sections.
   Leave completed sections and `docs/releases/` alone, since those record
   what was true at the time.
7. **The `PL-FD5Q` rider.** Its own commit, led by `PL-FD5Q`, to its own
   Done-when and `verify:`.

**Done when.** `bin/docket check` fails an open debt item that the current
gate neither places nor defers through `deferred-from:`, and a test over the
real tree pins that. `bin/docket wave` lists the deferrals from the field. The
prose parse is deleted, and v0.6.0's deferrals are one pointer subsection. The
closing commit leads with `PL-58JD`, `PL-59QW` and `PL-VFJ3`, which close
through the change, and with this item. `PL-FD5Q` is closed by its own commit.
`make check` is green.
