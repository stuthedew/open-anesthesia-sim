---
id: PL-J6HP
title: Gate facts - which entries a milestone clears itself, which are deferred, which closed entries carry the release that took them, how many a heading holds - live in ROADMAP.md prose that plan.py, roadmap.py and tools/doc_check.py each read on their own, so every new phrasing or fact arrives as a new item
priority: P2
effort: M
status: done
classes: defect, infra
feature: gate-list-integrity
milestone: v0.5.7
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/, subprojects/docket/README.md, tools/doc_check.py, tests/unit/test_doc_check.py, ROADMAP.md, docs/ARCHITECTURE.md
added: 2026-09-23
closed: 2026-09-23
pr: 937
payoff: each gate fact is read once, so a new way of writing one changes a parser instead of arriving in the queue as an item
verify: grep -q 'def test_parse_milestones_reads_every_deferral_subsection' subprojects/docket/tests/test_roadmap.py && grep -q 'def test_a_required_scope_entry_outside_the_self_cleared_group_is_reported' tests/unit/test_doc_check.py
root-cause-of: PL-H6VQ, PL-Z891, PL-YVP7, PL-B60Q, PL-JN3F, PL-RFHH
generator: spent - for the readers: every gate fact its six members re-derived now has one reader in docket.roadmap, read by bin/docket wave and tools/doc_check.py alike; the record itself stayed prose, and PL-59QW and PL-58JD, filed after this closed, are that record's, which PL-WD5Z carries live from 2026-09-23
---

**Problem.** `ROADMAP.md` records a debt gate's facts as prose, and each reader
re-derives them with a grammar of its own. `plan.gate()` decides what a
milestone clears itself by `feature`; `roadmap.gate_status` decides it by
`Required scope`, which is the rule the roadmap states; `tools/doc_check.py`
reads the deferral subsections with its own heading pattern and id extraction.
Counts and marks - how many entries a heading holds, the release a closed
deferral carries - sit in prose that no reader checks at all.

**Why it matters.** `PL-KVDK`'s first pass recorded this generator live on
`PL-RFHH`, the open item closest to the fix at the time. It moved here on
2026-09-23, when `PL-RFHH` closed on rewording `bin/docket gate` and `bin/docket
wave` so that neither prints the other's answer under its name. That removes
the collision and leaves this mechanism running, and closing a head on a
partial fix is how `PL-HWW1`, the earlier head for gate prose, went on to seven
more instances. Members: `PL-H6VQ` and `PL-Z891` (`doc_check`'s deferral
reading), `PL-YVP7` and `PL-RFHH` (two readings of what a milestone clears
itself), `PL-JN3F` (a heading count nothing reads) and `PL-B60Q` (a marking rule
stated inside one milestone's subsection).

**Generator check.** The head of one - see above.

**Decision needed.** Which route stops the mechanism. One is a single reader:
every gate fact parsed once in `docket.roadmap`, with `tools/doc_check.py` and
`plan.gate()` taking that parse instead of re-deriving it. The other moves the
facts out of prose into records no reader can mis-parse. Count the readers and
the facts each route has to carry before choosing. The first changes no stored
format, so it is the one to cost first.

**Done when.** Each gate fact the roadmap records has one reader, so a new
phrasing of one changes that reader instead of arriving as an item.

## Counted 2026-09-23: the two routes differ on one fact of eight

**Recommended: one reader, and the derived facts stop being written down.**
Parse deferrals in `docket.roadmap` beside the frozen list and `Required
scope`, derive the current gate once, and stop `ROADMAP.md` carrying hand
copies of facts the store or the parse already holds. Do not move deferrals
into structured records unless the falsifier below fires. Decided the same day;
see the next section.

**The count**, read against the tree on 2026-09-23. Eight kinds of gate fact,
and the two routes carry the same thing on seven of them:

| Fact | Kind | Readers today | One reader carries | Records carry |
| --- | --- | --- | --- | --- |
| Frozen-list membership | decided | 1, `roadmap._gate_entries` | nothing | nothing |
| `Required scope` membership | decided | 1, the declaration slot (`PL-HWW1`) | nothing | nothing |
| Exclusions | decided | 1, `MilestoneSection.excluded_ids` | nothing | nothing |
| Deferrals | decided | 1, but in `tools/doc_check.py` (`_declined_ids`), so no `bin/docket` command can see one | move the parse into `docket.roadmap` | an item field, 16 v0.6.0 entries migrated, `PL-HWW1`'s refusal reopened |
| Which gate is current | derived | 2: `roadmap.wave`, and two identical blocks in `doc_check` | one function | the same |
| What a milestone clears itself | derived | 1 derivation (`gate_status`), plus a hand copy nothing holds | hold the copy to the parse | the same |
| The release that took a closed deferral | derived | 0 | print it from the store, stop writing it | the same |
| Counts | derived | 1 checker (`check_gate_counts`, `PL-4RHP`) | nothing | nothing |

`plan.gate()` reads none of them since `#928`: it reads no roadmap at all, and
its output says it partitions the store by `feature`. **Decision needed.**
above names it as a reader, which was true before that merge.

**Two measurements behind the derived rows.**

- *The release mark copies a field.* Across v0.5.0's refilling-queue list and
  v0.6.0's two deferral subsections, 82 entries have closed. 48 carry a mark,
  and every one of the 48 equals the item's `milestone:`, which `bin/docket
  release` stamps. The other 34 carry none, and 30 of those sit in the list
  that states the marking rule. So the rule copies a field the store already
  holds, and it has missed 41% of the time.
  Re-read after the v0.5.6 cut (`#931`), the same day: that release shipped
  `PL-RFHH`, a v0.6.0 deferral entry, and left the entry unmarked, as
  `PL-B60Q` predicted. The count is now 84 closed, 48 marked, 36 unmarked, and
  every mark still equals `milestone:`.
- *The self-clear copy is wrong today.* v0.6.0's frozen list groups 12 entries
  under "Cleared by v0.6.0 itself - 12 entries". The rule gives 14: `PL-CNCF`
  and `PL-PGZF` are named in `Required scope` but sit under the "Cleared before
  v0.6.0 begins" groups, because `#862` named them after `#850` had grouped the
  list. `check_gate_counts` holds only the heading's count, and that agrees
  (12 entries under it). This is a live instance of the mechanism. It is
  recorded here rather than filed on its own, because it is part of this
  item's done-when (`capture.md`: a finding that completes an in-progress item
  is not a new item).

**The members, sorted by mechanism.** Two are the deferral reader not matching
the document (`PL-H6VQ`, `PL-Z891`). Two are a derived fact derived a second
way (`PL-YVP7`, `PL-RFHH`). Two are a derived fact written by hand
(`PL-JN3F`, `PL-B60Q`). Structured records only reach the first pair. The
other four need the same fix under either route.

**Why one reader, and not records, for deferrals.**

1. **Nothing measured asks for more.** Both deferral members were `doc_check`'s
   reader failing to match the document, which one reader plus the existing
   dispositions error covers. In v0.6.0, reading only the entries' leading ids
   would drop no disposition: 16 entries, and 8 ids cited in prose, none of
   them open undisposed debt.
2. **The churn is modest.** Since the 2026-09-21 freeze, 16 deferral entries
   landed in 4 commits, out of 81 on `main`.
3. **Records reopen a refusal.** `PL-HWW1` refused both a per-item membership
   field and a sidecar file or fenced block (ratified, 2026-09-19), on the
   ground that two statements drift. That can be reopened on ordinary
   evidence, and item 2 above is the only candidate: deferrals are made one at
   a time at triage, not in a single scoping act. It is not enough on its own.
4. **Reversibility.** One reader changes no stored format, so nothing is
   downstream of it, and a later move to records is not made any more
   expensive. Records are the one-way door: every deferral written into item
   files after they land becomes principal to repay if they are undone.

**What would change it, stated before building.** If a deferral phrasing or
reading produces another item after one reader lands, move deferrals into an
item field. The parse in `docket.roadmap` is the one thing that move would
replace.

**What one reader carries, concretely.**

- Deferrals: `DEFERRAL_VERBS`, `DECLINED_HEADING_RE`, `_section_end` and
  `_declined_ids` (about 135 lines, mostly docstring) move into
  `parse_milestones`, as the entries' leading ids plus every id beneath, which
  is the dispositions check's reading, kept unchanged. `check_gate_dispositions`
  reads the parse. Neither name is renamed: `ROADMAP.md` and release notes cite
  both.
- The current gate: one function over `release_train(...).ahead`, called by
  `wave` and by both `doc_check` blocks.
- Self-clear: `doc_check` holds the "Cleared by vX.Y.Z itself" group's
  membership to the frozen entries `Required scope` names. The build moves
  `PL-CNCF` and `PL-PGZF` into that group and updates the three group counts
  (12 to 14, 45 to 44, 12 to 11).
- The mark: `bin/docket wave` prints each current-gate deferral's state and
  release from the store. v0.5.0's marking rule becomes a pointer to that
  output. The existing 48 marks stay, since a release name does not go stale.
  This is `PL-B60Q` re-scoped: its filed check would demand a hand copy of
  `milestone:` on 34 entries at once, and again on every release after.

**Left alone deliberately.** Prose counts (`PL-16HD`, `PL-DHJ7`) belong to
`PL-4FBP`'s stale-statement cluster, where the reader is the check, so neither
route touches them. The lane groups and v0.6.0's one-entry "Deferred to Gate 3"
group are a person's organisation of the list. They agree with the store
today, nothing has been filed on them, and the list's own text names `bin/docket
wave` as the authority.

## Decided 2026-09-23: one reader

**One reader in `docket.roadmap`, and derived gate facts are no longer written
into `ROADMAP.md`** (project owner, 2026-09-23, ratified, over moving deferrals
into an item field). The owner agreed with the recommendation above as put,
including what one reader carries. That covers `PL-B60Q`, which is folded into
this build and closes with it. Because this is ratified, the falsifier above
reopens it on ordinary evidence: another item filed about reading deferrals
after this lands.

`touches` now lists the decided route's footprint. `plan.py` is off it, since
it reads no gate fact. `render.py` and `cli.py` are on it, for `bin/docket
wave` printing each deferral's state and release. The tests and the docket
README are on it too.


## Built 2026-09-23

As decided, with no departure from "What one reader carries":

- `parse_milestones` carries each section's `deferral_entries` (the entries'
  leading ids) and `deferred_ids` (every id beneath a deferral heading, prose
  included - `_declined_ids`' reading, unchanged). `DEFERRAL_VERBS`,
  `DECLINED_HEADING_RE`, `_section_end` and `_declined_ids` moved from
  `tools/doc_check.py` with their names; both readings share one bound
  (`_deferral_subsections`). v0.6.0 parses to 16 entries; of the 8 ids named
  only in prose, four are closed, one is on the frozen list and three carry no
  debt class, so the entry reading drops nothing still owed a disposition.
- `current_gate(train)` is the one answer; `wave` calls it, and
  `tools/doc_check.py`'s re-entry, disposition and self-cleared rules call it
  through `_current_gate`, at the version table's baseline row, which
  `check_baseline` holds equal to `pyproject.toml`.
  `test_the_gate_rules_read_the_gate_wave_reads` fails under the old
  version-order pick (mutation run by hand).
- `check_self_cleared_group` holds the current gate's "Cleared by vX.Y.Z
  itself" group to the entries `Required scope` declares, in both directions.
  The current gate only: v0.5.0's released list keeps `PL-YDKJ` in that group
  on purpose, with a paragraph saying why. It fired on exactly `PL-CNCF` and
  `PL-PGZF` before the move; the three counts are now 14, 44 and 11.
- The mark is `PL-B60Q`, closed in the same commit.

**Generator: spent.** Every fact its six members re-derived now has one reader
or none to drift from, as the front matter says. The falsifier stated above
still stands: another item filed about reading deferrals reopens the choice of
records over one reader, on ordinary evidence, since the decision was ratified.
