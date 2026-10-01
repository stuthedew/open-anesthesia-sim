---
id: PL-4C41
title: A brief can contradict itself about its own sequencing and no check sees it
priority: P3
effort: S
status: dropped
classes: docs, infra
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/roadmap.py, docs/items/PL-WB0X-split-simulation-view-py-formatting-and-chart.md
added: 2026-09-01
closed: 2026-10-01
reason: Measured 2026-10-01 on main at the end of every day since filing (28 snapshots, 244 to 1,885 items): the decidable sliver fired 8 times, all narration naming a closed item; kept to open pairs it had nothing to read on any day; and it would have missed PL-WB0X itself, whose Gate 1 placement was prose no milestone section parsed. It does not earn its upkeep; the brief records the count and what would reopen it.
verify: grep -qF 'def check_sequencing_placement' subprojects/docket/src/docket/checks.py && bin/docket check
---

**Problem.** An item's brief can state placements for its own work that
cannot all be true, and nothing in the store, in `make check` or in
`tools/doc_check.py` notices. `PL-WB0X` (split `simulation_view.py`) was the
live instance. It stated three (line numbers as of 2026-09-01; the
contradiction itself was resolved 2026-09-02, see **Instance resolved** below):

1. Its **Sequencing** section requires stage 1 (`app/formatting.py`) to land
   *before* `PL-DHV7` (MAC multiples as a display unit), which `ROADMAP.md`
   lists in v0.4.0's **Required scope** (`:1105`) and among the six items
   "Cleared by v0.4.0 itself" (`:1089`). `PL-DHV7` is safety- and
   science-classed, and the sequencing argument is that doing it against an
   extracted, Flet-free formatter is materially safer.
2. Its **Where it belongs on the plan** section defers the whole item to
   **Gate 1**, which `ROADMAP.md`'s cadence table records as "Frozen when
   v0.5.0 is scoped… **Ships inside v0.5.0**, not as its own release"
   (`:287`).
3. The same section then names "a `v0.3.x` patch step" as its natural home.

(1) and (3) agree: a v0.3.x step precedes v0.4.0. (2) contradicts (1) — work
that ships inside v0.5.0 cannot precede an item that ships in v0.4.0. The
Gate 1 deferral is repeated in `ROADMAP.md:1062`, so the contradiction now
sits in two documents and neither one carries both halves.

**Why it matters.** `subprojects/docket/README.md` states the store's whole
premise: "every item carries a brief written for a stranger… An item that
cannot be started cold is a bug in the item." A self-contradicting sequencing
claim defeats that specifically. The session that meets it has to reconstruct
the release plan to work out which half to believe — which is the reading the
brief exists to spare it — and it degrades quietly, because `docket next`
ranks by the roadmap's milestone placement and never reads the brief's prose.
The item can therefore be offered at a time one of its own sentences calls
too late, with nothing anywhere saying so.

The consequence is bounded, which is why this is `P3`: it costs a session a
lookup and a judgment call, never a wrong clinical value. It is filed because
the record is the value — the next person to notice this should find that it
has already been noticed, with the instance named.

**Where.**

- `docs/items/PL-WB0X-split-simulation-view-py-formatting-and-chart.md` —
  the "Sequencing" and "Where it belongs on the plan" sections.
- `ROADMAP.md:287` (Gate 1 ships inside v0.5.0), `:1062` (the deferral),
  `:1089` and `:1105` (PL-DHV7 in v0.4.0).
- `subprojects/docket/src/docket/checks.py` and `roadmap.py` — where a check
  would go, and where milestone placement is already parsed.
- `tools/doc_check.py` — declines this deliberately and correctly; it decides
  whether a cited path exists, never whether the sentence around it holds.

**What is decidable, and what is not.** This is the design work, per
`CLAUDE.md` § "Find the decidable part and put it in code" and its converse,
"Do not script the judgment."

*Decidable.* A brief that names another item with an ordering word — "before
`PL-XXXX`", "after `PL-XXXX`" — while `ROADMAP.md` places the two items in
milestones that order them the other way. Both halves already exist in code:
`roadmap.py` parses milestone placement for `docket next`, and item bodies
are already read by `docket triage`. The surface is a small closed set of
phrasings over ids matching `PL-[A-Z0-9]{4}`.

*Not decidable.* Whether two passages of prose are describing the same work;
whether "deferred to Gate 1" is a placement claim or a note about which gate
counts the item as debt; whether a stated ordering is still wanted or is a
leftover from an earlier plan. A check that guessed at any of these would
emit authoritative-looking output about a judgment it cannot make, which
`CLAUDE.md` names as worse than no check at all.

So the candidate rule is narrow, and its value is unproven: one instance
across 230 item files. **A legitimate outcome of this item is `dropped` with
a reason** — that the decidable sliver fires too rarely to earn its upkeep —
which leaves this brief standing as the record. That is the honest close, not
a failure to finish, and `subprojects/docket/README.md` is explicit that a
dropped item keeps its file precisely so the finding is not re-raised.

**Instance resolved 2026-09-02, which changes what this item can be tested
against.** The project owner settled `PL-WB0X`'s placement: stages 1 and 2 (the
two pure-module extractions) are in v0.4.0's Required scope, and stage 3 (the
`SimulationView` decomposition proper) left that brief for `PL-B9PY` (decompose
`SimulationView` so two runs can be rendered at once) and stayed at Gate 1. One
item cannot sit in two milestones, so splitting was the resolution rather than
choosing one of the three. `PL-WB0X` and `ROADMAP.md` now state one placement
each and agree.

The consequence for this item is that **it no longer has a live instance to
fire on**, so the acceptance test below was rewritten. That is a real weakening
of the case for the check: the value was always "one instance across 230 item
files", and it is now zero known instances. A rule with no instance is a rule
whose upkeep is paid against a hypothesis. Weigh that when deciding whether to
build it or to drop it — either close is honest, and this brief is the record
in both cases.

**Not this item.** Resolving `PL-WB0X`'s own placement was a question about the
plan, not about tooling. It has been answered. What this item owns is the
general record and the narrow check.

**Found.** Outside review, relayed by the project owner on 2026-09-01 in a
capture-only session. Verified in this checkout against `ROADMAP.md` and
`PL-WB0X`'s brief as they stand.

**Done when.** Either `docket check` gains a rule that flags an item whose
brief orders itself against another item in a direction `ROADMAP.md`'s
milestone placement contradicts, and that rule is shown to fire — against a
fixture reproducing `PL-WB0X`'s three placements as they stood on 2026-09-01,
since the store itself no longer contains an instance; or the item is `dropped`
with the reason that the decidable sliver does not earn its upkeep, leaving
this brief as the record. The second is now the more likely close, per
**Instance resolved** above.

**Measured 2026-10-01, and dropped on it.** The number that would have made
building it right, named before the count: on some day since filing, the rule
as it can be specified catches at least one real contradiction, and its false
fires do not outnumber its real ones.

*The rule as counted.* An ordering cue within one clause of an id - `before`,
`ahead of`, `prior to`, `precede(s/d)`, `preceding` (this item first), or
`after`, `follow(s/ed/ing)`, `sequenced after`, `sequenced behind`, `behind`,
`once` (this item second) - in an open item's body, with the clause window
`_cue_pattern` in `subprojects/docket/src/docket/checks.py` uses; kept where
`roadmap.parse_milestones` places the two items in different milestone
sections, and fired where the stated order runs against the versions'. Run on
`main` as it stood at the end of each UTC day from 2026-09-01 to 2026-10-01: 28
days with a new commit, 244 items growing to 1,885. A scratch script,
deliberately not committed, since it was going to run once.

*What it found.*

- **Eight distinct firings, all false.** Each is narration naming a closed
  item, never a sequencing claim: "Before `PL-LHBY` that was safe by accident"
  (`PL-FPY2`); "that table had eight rows before `PL-XWCY` and has nine after
  it" (`PL-DBGT`, still firing today); "Message before `PL-9SH6`" (`PL-SPN6`);
  "Before `PL-YDL6` an absent entry meant no commit named a number at all"
  (`PL-QNYF`); "the same before-and-after scan `PL-0RZ0` ran" (`PL-1K9G`); "in
  hand before they are asked, is the measurement `PL-0RZ0` owes" (`PL-QYBW`);
  and two quoting a since-dropped "before `PL-011`" edge as history (`PL-4RBD`,
  `PL-C4PH`).
- **The obvious repair has nothing to read.** Kept to pairs whose items are
  both open, the rule met no hit across two milestones on any of the 28 days,
  including every day from 2026-09-14 on, when two sections each placed open
  items (v0.4.26 beside v0.5.0, then v0.5.0 beside v0.6.0, scoped two releases
  early). That is structural rather than luck: the rolling wave
  (`ROADMAP.md` § "The planning model: a rolling wave") details one milestone
  at a time, and today's 40 cue hits in open briefs split into 33 naming an
  item no section places, five naming a closed item, and two between open
  items that share v0.6.0, where there is no order to contradict.
- **It would have missed the instance it was filed on.** On 2026-09-01
  `PL-WB0X`'s brief did read "before PL-DHV7", and v0.4.0's Required scope
  placed `PL-DHV7`. No section placed `PL-WB0X`: its Gate 1 placement was the
  prose under "One presence-qualifying finding deliberately deferred to Gate 1"
  in v0.4.0's own section, and v0.5.0 had no section until 2026-09-06. Reading
  that sentence as a placement is the judgment the *Not decidable* paragraph
  above excludes.

*An earlier count agrees.* `PL-ZBRB` (2026-09-04) measured the same two cues
for the prose-prerequisite advisory and left both out, `after` reading as
narration about eight times to three real waits; the comment above
`DECLARING_CUES` in `checks.py` carries it. And the declared half of this
concern already reaches every session: `roadmap.gate_status` follows
`blocked-by` from each frozen entry and collects the open blockers its gate
does not hold, which the session-start digest prints as the entries "blocked
outside it".

*What would reopen it.* A contradiction in the store that this rule, as
specified, would catch - the founding one was not - recorded here as an
instance, with this count re-run before anything is built. Or a cadence that
keeps two scoped milestones holding open items as its normal state, which
would give the rule something to read.
