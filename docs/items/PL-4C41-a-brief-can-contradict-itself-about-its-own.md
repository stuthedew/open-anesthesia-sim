---
id: PL-4C41
title: A brief can contradict itself about its own sequencing and no check sees it
priority: P3
effort: S
status: ready
classes: docs, infra
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/roadmap.py, docs/items/PL-WB0X-split-simulation-view-py-formatting-and-chart.md
added: 2026-09-01
verify: bin/docket check && grep -qF 'def check_sequencing_placement' subprojects/docket/src/docket/checks.py
---

**Problem.** An item's brief can state placements for its own work that
cannot all be true, and nothing in the store, in `make check` or in
`tools/doc_check.py` notices. `PL-WB0X` (split `simulation_view.py`) is the
live instance, and it states three:

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
`CLAUDE.md`'s "Find the decidable part and put it in code" and its converse,
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

**Expect building the check to force a decision.** If the rule lands, `make
check` stays red until `PL-WB0X` states one placement rather than three. That
is the right forcing function and should be worked, not suppressed — but it
means the work is not purely additive, and whoever takes it needs the project
owner's answer on where `PL-WB0X` actually belongs.

**Not this item.** Resolving `PL-WB0X`'s own placement is a question about the
plan, not about tooling, and it is answered by whichever of `PL-WB0X` or
`PL-DHV7` is started first. What this item owns is the general record and the
narrow check; the instance is its acceptance test.

**Found.** Outside review, relayed by the project owner on 2026-09-01 in a
capture-only session. Verified in this checkout against `ROADMAP.md` and
`PL-WB0X`'s brief as they stand.

**Done when.** Either `docket check` gains a rule that flags an item whose
brief orders itself against another item in a direction `ROADMAP.md`'s
milestone placement contradicts, and that rule names `PL-WB0X` when run
against the store as it stands; or the item is `dropped` with the reason
that the decidable sliver does not earn its upkeep, leaving this brief as
the record.
