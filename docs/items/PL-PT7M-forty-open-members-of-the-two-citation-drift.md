---
id: PL-PT7M
title: Forty open members of the two citation-drift heads have no drain plan: PL-4FBP and PL-G424 both closed their mechanism, and the 40 repairs they named sit in the flat P2 band as forty independent items with no batch, no check and no disposition
priority: P2
effort: M
status: done
classes: planning, docs, housekeeping
feature: citation-drift-drain
touches: docs/items, docs/WORKING_NOTES.md
added: 2026-09-21
closed: 2026-09-21
payoff: 40 items the project has already decided about stop being offered as work, and the open count stops carrying non-findings
verify: test "$(grep -cE '^\| PL-[A-Z0-9]{3,4} \|' docs/items/PL-PT7M-forty-open-members-of-the-two-citation-drift.md)" -eq 40
---

**Problem.** Forty open members of the two citation-drift heads have no drain plan: PL-4FBP and PL-G424 both closed their mechanism, and the 40 repairs they named sit in the flat P2 band as forty independent items with no batch, no check and no disposition

**Measured 2026-09-21, over the whole store.** Eleven `root-cause-of:` heads
and one `impairs-generators:` head are recorded; all twelve are closed. Their
99 distinct members are not: 60 are still open, and the count is *unchanged*
from `PL-XF5V`'s measurement of 2026-09-20 - same 60, same per-head split, no
drain in a day. Two heads carry two thirds of it:

| Head | What its close fixed | Members | Still open |
| --- | --- | ---: | ---: |
| `PL-4FBP` | a live assertion must name what it asserts | 24 | 21 |
| `PL-G424` | `.claude/rules/citation-drift.md`, apparatus side | 21 | 19 |

The other five undrained heads - `PL-BHVM` (6), `PL-4Q9B` (6), `PL-6TP8` (4),
`PL-G21K` (3), `PL-L4YG` (1) - total 20 and are ordinary tails. Four heads
(`PL-2T03`, `PL-6T44`, `PL-HWW1`, `PL-TZ7T`) are genuinely drained.

**The 40 are not one kind of work, which is the finding.** Read individually
rather than counted, they split three ways:

- **9 are check-building**, all under `PL-4FBP`: `PL-036`, `PL-2M9N`,
  `PL-5N7T`, `PL-9LXK`, `PL-4RHP`, `PL-DHJ7`, `PL-8LDF`, `PL-41YP`, `PL-GQWP`
  each propose binding one class of prose claim to the tree in
  `tools/doc_check.py`. These are the leverage - a check retires its repair
  class forever - and they are ordinary engineering items that happen to sit
  under a drift head.
- **27 are single live-document repairs**: 7 in `docs/WORKING_NOTES.md`, 6 in
  open item briefs, 3 in `CLAUDE.md` or the docket skill, the rest in
  `ROADMAP.md`, `docs/ARCHITECTURE.md` and `README.md`.
- **4 are not startable**: `PL-NWTM` carries a `blocked-by` edge of its own,
  and `PL-Z5FG`, `PL-6QZP`, `PL-QV5Y` sit at `needs-decision`.

**37 of the 40 were filed before `.claude/rules/citation-drift.md` existed**
(project owner, 2026-09-19, ratified), and that rule disposes of some of them
outright: drift in a closed brief is not a finding, and re-pointing a line
number is banned rather than asked for more carefully. `PL-38PN` and `PL-JXVD`
are that exact shape - two generations of line-number repair - and `PL-RFSL`
already records that `PL-38PN`'s remaining deliverable is refused by the rule.
Nobody has re-judged the rest against it.

**What is not the answer.** Dropping the tail wholesale is the move `PL-LKGL`
refuted: the count nobody ran came back 67% still-real findings. The re-judging
below is a per-item test against a ratified rule, not a bar being raised.

**Recommendation (a session's, not the project owner's), in order:**

1. **Re-judge all 40 against `.claude/rules/citation-drift.md`.** Drop what the
   closed-brief clause and the line-anchor ban refuse, with `reason:` naming
   the clause. This is a reading pass over 40 briefs, not an editing pass, and
   it is the only step that needs no decision.
2. **Sweep the 27 live-document repairs in one pass per file**, not as 27
   items. The rule already says a drift repair rides the commit a session is
   already making; what is missing is one pass that clears the standing
   backlog, and the members cluster in four files.
3. **Rank the 9 check-building members on their own merits**, outside any
   drift sweep. `tools/doc_check.py` is where the class ends.

**Decided (project owner, 2026-09-21, ratified)**, over working the whole
three-step recommendation now and over deferring all of it behind `v0.5.0`:
**step 1 only.** Re-judge the 40 against `.claude/rules/citation-drift.md` and
drop what it refuses. The 27-repair editing sweep is **deferred** behind
`v0.5.0`'s product beat - none of the 27 blocks a learner-visible behavior - and
the 9 check-building members are **out of this item**, to be ranked on their own
merits like any other `tools/doc_check.py` work.

**Why it matters.** 37 of the 40 were filed against a convention that did not
exist yet, and the rule that now governs them refuses some outright. Until they
are re-judged, `bin/docket next` offers work the project has already decided not
to do, and every count of the open queue - including `PL-04KR`'s convergence
baseline - carries items that are not findings. It is also the cheapest 40-item
movement available: a reading pass against a written rule, with no editing and
no decision left in it.

**Done when.** Every one of the 40 open members of `PL-4FBP` and `PL-G424` has
been read against `.claude/rules/citation-drift.md` and either

- dropped, with `reason:` naming the clause that refuses it - the closed-brief
  clause, or the line-anchor ban; or
- kept, with the kind it is (check-building, live-document repair, or not
  startable).

Either way it gets one row in a disposition table in this brief, of the shape
`| PL-XXXX | kept/dropped | clause or kind |`, so the next session reads the
outcome instead of re-deriving it. That table is what this item's `verify:`
counts - 40 rows, one per member, whatever each row says. `PL-38PN` and `PL-JXVD` are the two known
candidates for the line-anchor ban and `PL-RFSL` already holds the finding for
one of them, so neither is a fresh judgment.

**Not a bar being raised.** Each drop cites a clause of a ratified rule against
one item's own brief. Nothing here changes what may be captured in future, which
is the move `PL-LKGL` refuted.

**Where it came from.** The project owner asked on 2026-09-21 whether the
generators and their clusters were dealt with. Answering it took a script over
the whole store - the read `PL-XF5V` exists to replace - and the answer was
"the heads yes, the clusters no", with these two heads accounting for 40 of the
60 open members.

## Disposition, 2026-09-21

**Worked: step 1, as decided.** All 40 open members were read against
`.claude/rules/citation-drift.md`. **Six are dropped** - five for the
closed-brief clause, one for the line-anchor ban - and 34 are kept. Nothing was
dropped for being small, for being old, or for being a drift repair: each drop
names a clause of a ratified rule against that item's own deliverable, which is
the test `PL-LKGL` refuted a bar-raising proposal for failing.

**Two of the six had a live half, and neither was discarded with the item.**
`PL-8T3Z` asked for `PL-K2C8`'s `touches` and **Where** to be corrected, which
the clause refuses now that `PL-K2C8` is `done` - but the finding underneath it
is that `.claude/hooks/no-prune-guard.sh` still prints the three-command restart
recipe `PL-K2C8` replaced, in the louder of the two places: the message a
session reads at the moment it is refused a prune. That is `PL-J3TV`, filed and
verified against the hook the same day. `PL-MSFB` is narrowed rather than
dropped: its `PL-6194` half expired on the item's own stated condition when
`PL-6194` closed, its `docs/WORKING_NOTES.md` half is untouched, and its
`verify:` no longer greps a closed item's file.

**The line-anchor drops cost nothing, because the repair the rule prescribes
was made instead.** `PL-Z5FG` and `PL-JXVD` between them named citations in one
live brief, `PL-HXKC`. All eight of its entries already carried the symbol
beside the number, so this commit struck the numbers and kept the symbols -
`.claude/rules/citation-drift.md`'s own remedy, riding the current item's commit
exactly as the rule says such a repair should. Two of the eight symbols had
drifted as well (`require_concentration_fraction` is now `require_fraction`,
and `apply_blood_uptake` no longer exists), and both are marked in that brief
for whoever takes it.

**No live-document repair has already been done.** Twenty-one of the 22 carry a
`verify:` command that runs without the project virtualenv; all 21 were run on
2026-09-21 and all 21 still fail, so none of those rows is a close-out waiting
to be noticed. The 22nd (`PL-21RC`, the apparatus enumerations missing
`docs/maintainer.md`) and the 9 check-building members run under `uv run
pytest` and were not re-run; the 3 not-startable rows carry no command. That
covers the group the deferral is about and leaves the two groups whose
disposition is their own.

**What the pass did not do**, per the decision above: no editing sweep of the
live-document repairs, and no ranking of the check-building members. The 22
live-document rows are the sweep that is deferred behind `v0.5.0`; the 9
check-building rows rank on their own merits as ordinary `tools/doc_check.py`
work.

| Member | Disposition | Clause, or the kind it is |
| --- | --- | --- |
| PL-38PN | dropped | closed-brief clause - repoints `PL-VM40` and `PL-L2F2`, both `done`; the line-anchor ban refuses it again |
| PL-JXVD | dropped | line-anchor ban - a second generation of line repair, and the rule's own worked example |
| PL-Z5FG | dropped | line-anchor ban; `PL-0NQ1` half is closed-brief. `PL-HXKC`'s citations re-anchored to symbols in this commit |
| PL-2GQW | dropped | closed-brief clause - `PL-L9JS` is `done`, and no live document carries the disproved recursion claim |
| PL-5F26 | dropped | closed-brief clause - `PL-1XPX` is `done`, and `ROADMAP.md` already dates `PL-TCD1` correctly |
| PL-8T3Z | dropped | closed-brief clause - `PL-K2C8` is `done`. Live half re-filed as `PL-J3TV` (the no-prune hook's stale recipe) |
| PL-036 | kept | check-building - `docs/MODEL.md`'s minimum displayed outputs, bound to `SimulationSnapshot` |
| PL-2M9N | kept | check-building - `docs/MODEL.md`'s Required tests headings resolved to real test functions |
| PL-5N7T | kept | check-building - `docs/ARCHITECTURE.md`'s prose enumeration held to `quality.yml`'s run steps |
| PL-8LDF | kept | check-building - `docs/MODEL.md`'s eighteen required invariants each named to a test |
| PL-9LXK | kept | check-building - a prose claim about a stored value's source tier held to the data files |
| PL-41YP | kept | check-building - a test that each required displayed output reaches the rendered view |
| PL-4RHP | kept | check-building - `ROADMAP.md`'s Declined-to-Gate count, or the decision to state none |
| PL-DHJ7 | kept | check-building - the live `ROADMAP.md` subset counts, on `PL-GLBF`'s pattern |
| PL-GQWP | kept | check-building - `README.md`'s playback ladder, time-base range and agent list held to the code |
| PL-NWTM | kept | not startable - `blocked`, and a `safety`-classed structural item rather than a citation repair |
| PL-6QZP | kept | not startable - `needs-decision`; prose drift in `CLAUDE.md`, which no clause reaches |
| PL-QV5Y | kept | not startable - `needs-decision`; a stale measurement in the `Makefile`, explicitly outside the rule |
| PL-0R06 | kept | live-document repair - `docs/WORKING_NOTES.md`'s matplotlib note |
| PL-037Y | kept | live-document repair - `docs/WORKING_NOTES.md`'s gloss of `PL-NGF7` |
| PL-245B | kept | live-document repair - `docs/WORKING_NOTES.md`; its remedy already names a symbol, not a line |
| PL-4HKS | kept | live-document repair - `docs/WORKING_NOTES.md`'s pre-Qt-port playback numbers |
| PL-60CQ | kept | live-document repair - `docs/WORKING_NOTES.md`'s `PL-024` entry, superseded by the 1.222 L pool |
| PL-75R0 | kept | live-document repair - `docs/WORKING_NOTES.md`'s resolved no-README thread |
| PL-B5LB | kept | live-document repair - `docs/ARCHITECTURE.md` and `CONTRIBUTING.md` on what `doc_check.py` covers |
| PL-BHJW | kept | live-document repair - `docs/WORKING_NOTES.md` names CI's deleted `floor` job |
| PL-C7XV | kept | live-document repair - `docs/WORKING_NOTES.md`'s two placements under one decision date |
| PL-C25K | kept | live-document repair - `ROADMAP.md` v0.2.8 asserts the dropped `PL-J786` is in effect |
| PL-CPLX | kept | live-document repair - the `docket` skill's out-of-turn example names a shipped release |
| PL-DBGT | kept | live-document repair - `desflurane.json`'s provenance note; a stored data file, so the closest to safety-critical in the set |
| PL-DL4M | kept | live-document repair - `docs/WORKING_NOTES.md`'s two `Open thread` headings and v0.2.0 baseline |
| PL-FV7G | kept | live-document repair - `ROADMAP.md`'s v0.4.14 row reads as a live claim |
| PL-GTSL | kept | live-document repair - `docs/ARCHITECTURE.md` omits `check_resident_instructions` |
| PL-LM8P | kept | live-document repair - `.claude/rules/citing-sources.md`'s thirteen-of-twenty-six census |
| PL-MSFB | kept | live-document repair, narrowed - the `PL-6194` half struck (closed-brief), `docs/WORKING_NOTES.md` half stands |
| PL-N32Y | kept | live-document repair - `ROADMAP.md` calls the stored tissue:gas coefficients tissue:blood |
| PL-T9XJ | kept | live-document repair - `docs/resident-instructions.md` names two resident files of three |
| PL-WVJ0 | kept | live-document repair - the `docket` skill says `show` prints no placement |
| PL-YZKK | kept | live-document repair - `PL-PGZF` and `PL-CNCF` are both open, so both briefs are live |
| PL-21RC | kept | live-document repair - `docs/maintainer.md` missing from all three apparatus enumerations |

**Counts.** 6 dropped, 34 kept: 9 check-building, 22 live-document repairs, 3
not startable. The original reading of the 40 put 27 in the live-document group
and 4 in the not-startable one; five of those 27 and one of those 4 are the six
drops.

**The `verify:` command was repointed, and this is why.** As filed it counted
rows matching `^\| PL-[A-Z0-9]{4} \|` - four characters after the prefix. One
of the 40 members is `PL-036`, a legacy three-character id, so the command
could count at most 39 and the item could never have verified however complete
the table was. The pattern is now `{3,4}` and the count is exactly 40. This is
a false-fail rather than a goalpost moved: no row was added or removed to make
it pass, and the same command still fails if a row goes missing.

**Five stale `verify:` commands were cleared with the drops, and that is
`PL-BX1C`.** `bin/docket verify --self` runs a `dropped` item's stored command
although the skill says a dropped item has none, so all five drops that carried
one printed `FAIL ... REJECT` with `make check` green and every other guard
passing; `PL-Z5FG`, which carried none, went straight to `ACCEPT`. Worse than
stale, three of the five asserted the opposite of the decision recorded beside
them - `PL-8T3Z`'s command asked that `PL-K2C8`'s `touches` name the hook,
which is precisely what the closed-brief clause refuses. The commands are
deleted, on `PL-BX1C`'s own precedent from `PL-TFWR`, and the count that item
now carries was taken here: 34 of 170 `dropped` items were holding one, leaving
29.

**Four of the six drops were `Declined to Gate 2` entries and now carry their
drop date** in `ROADMAP.md`, per `PL-0VFF`'s rule that an entry dropped rather
than shipped records the date. None of the six was on the frozen list, so
v0.5.0's gate is unchanged by this pass: 185 entries, 2 open here and 1 blocked
outside it.

