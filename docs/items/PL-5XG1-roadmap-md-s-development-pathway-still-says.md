---
id: PL-5XG1
title: ROADMAP.md's Development pathway still says Phase 1 follows v0.4.0 unchanged, while the timeline places Phase 1's substance generalization at v0.9.0 behind four releases, which its own known-risk paragraph argues against
priority: P2
effort: S
status: blocked
classes: docs
touches: ROADMAP.md
blocked-by: PL-V1Y7
deferred-from: v0.6.0 - filed after the gate froze, and a question of release order that no v0.6.0 entry waits on
added: 2026-09-26
payoff: A session reading the roadmap meets one answer for multi-substance - off the timeline until single-agent works, and the owner's condition for its return - instead of a pathway and a timeline that disagree.
verify: ! grep -qE 'v0\.[0-9]+\.0 — multi-substance' ROADMAP.md && ! grep -q 'held with its count by' ROADMAP.md && grep -q 'workspaces all working' ROADMAP.md
---

**Problem.** ROADMAP.md's Development pathway still says Phase 1 follows v0.4.0 unchanged, while the timeline places Phase 1's substance generalization at v0.9.0 behind four releases, which its own known-risk paragraph argues against

**Evidence, 2026-09-26.** § "Development pathway" opens "The numbered list
below is the catalogue; this is the order it is intended to be worked in, and
why", and its reordering note (project owner, 2026-08-25) ends "v0.4.0 is that
work; Phase 1 follows it unchanged." § "The timeline" puts Phase 1's substance
generalization and items 6 and 7 at v0.9.0, after v0.5.0 (shipped 2026-09-21),
v0.6.0, v0.7.0 and v0.8.0, each placed by a dated decision on its own row. The
pathway's closing paragraph, "The known risk", argues that "every milestone
built before the substance generalization is code written against the
single-agent assumption, and would have to be revisited afterwards" - the cost
the timeline's order now pays four times. Phase 2's and Phase 3's lists also
read as future work, though v0.4.0 and v0.5.0 shipped several of their items.

**Why it matters.** The pathway is where a session looks for the order of
work the timeline has not placed, and its reasons are what a session quotes
when it argues for an order. A reason stated as live and silently overturned
gets quoted against the plan that overturned it, and nothing checks two prose
orders against each other.

**What `PL-LJVD` already did about it.** Its section at the head of
§ "The plan" makes the timeline hold the order of every release it names, and
narrows the pathway's opening sentence and the catalogue's to the work the
timeline has not named, so a reader is no longer handed two orders. The
paragraphs underneath still assert the old one.

**Two parts, and only the first is a session's.**

1. Rewrite the pathway to the part it holds: what lies past the timeline's
   last named release. Sentences about releases the timeline has placed are
   dropped or dated as history, not re-pointed at new version numbers, since
   re-pointing makes the next copy of the order. Then delete the sentence
   `PL-LJVD` added to the pathway's opening, "The phases below still read as
   the whole order", which marks them stale until this lands.
2. Whether the known-risk argument still stands against the order the
   timeline holds is the order features come in, which is the owner's. The
   rows record each move's reason (item 34's placement rounds, `PL-NMTF` and
   `PL-YHWG`); none says the single-agent rework was weighed. The likely
   answer: the two layout releases are substance-agnostic, on the reordering
   note's own argument that the view consumes a `SimulationSnapshot`, and the
   rework concentrates in v0.8.0's schematic, which draws where one agent is.
   Put that to the owner with the count, rather than deciding it in the
   rewrite.

**Part 1 done, 2026-09-26.** The pathway now orders only what the timeline
has not placed. Each phase keeps its name and intent, because `docs/MODEL.md`,
`app/controller.py`, `app/theme.py` and the timeline's own row for items 6 and
7 cite phases by name. Shipped entries are dated history, and the sentence
marking the phases stale is gone. No version number was written for placed
work, because `PL-V1Y7` renumbers these same rows.

**Part 2: the count, 2026-09-26.** Where the known-risk argument binds, one
release at a time, by this session's reading of each entry:

- **v0.6.0 builds nothing against it.** None of its 19 Required-scope entries
  builds a surface that reads one agent's values. Entry 7's unconditional
  region is declared by tier, with a tier per modelled substance (`PL-NWTM`).
  Entries 5, 9, 11 and 16 carry per-View state that gains a substance field
  later, and entry 12's schema-version policy absorbs that as an addition.
- **Break-out**, which `PL-V1Y7` takes off the timeline, has its per-window
  region shape already split per substance (`PL-W54S`).
- **The interface pass** (item 33) restyles and reads no new value. A readout
  row composed for one agent is recomposed when a second arrives.
- **The schematic (item 27) is the one release built against it.** Its entry
  "needs per-compartment agent amounts exposed on the snapshot", and
  `SimulationSnapshot` is the one single-agent seam, kept flat by decision
  until Phase 1, when "the mapping arrives with it" (`docs/MODEL.md`,
  `PL-TCD1`). Built first, it adds its amount fields flat and draws one agent's
  picture, and both are revisited when the mapping lands.
- **Sunk either way:** 102 lines across 10 `app/` modules name a single-agent
  snapshot field today, `controller.py` excluded. That grep covers
  `agent_id`, `agent_display_name`, `agent_mac_percent`, the six
  `*_partial_pressure_fraction` fields and `delivered_agent_l`. No reorder
  saves them.

**Recommendation (session, 2026-09-26), not taken - see the decision below:
put the substance generalization with items 6 and 7 ahead of the schematic, as
part of `PL-V1Y7`'s renumbering.**

- **Why this release, and why now.** The argument binds exactly one release,
  and that release is still cheap to move. Neither row is scoped, and no item
  carries either as `milestone:`. Only three other open items and 24 lines of
  standing documents name the two versions, and `PL-V1Y7` rewrites those rows
  anyway. Once the schematic is scoped its items carry the order, and the swap
  stops being free.
- **What it costs.** The schematic's lesson, where the agent is as against
  where its tension is, arrives one release later. The coupled-gas work, the
  plan's likeliest stall, comes one release sooner, so a stall there would now
  hold the schematic too.
- **The alternative.** Keep the order, and record on the schematic's row that
  the argument was weighed and accepted for that release alone.

**Decision (project owner, 2026-09-26): neither order - multi-substance comes
off the timeline**, over both orders put above. In the owner's words:
"Multi-substance is not an urgent priority and I feel like it will complicate
things. Really want to get layout and single substance working well. Let's
change it to a medium term goal but off the current roadmap for now. Add it
back once we have a really fleshed out single agent set up with workspaces all
working etc. I think I want to see how a single agent works and figure out the
kinks etc. before we complicate with multisubstance."

- **The known risk is accepted, knowingly, for every release the timeline
  names.** What is placed before the generalization returns is built for one
  agent by design, and the count above is the price: the schematic's
  per-compartment amounts on a single-agent snapshot, and the 102 lines across
  10 `app/` modules that already read single-agent fields.
- **"Medium term, off the current roadmap" is the Far horizon.** § "The plan"
  details three: the scoped milestones, the timeline's unscoped rows, and
  § "Development pathway". The owner took it out of the second, so it rejoins
  the timeline's Beyond row in pathway order, with the condition for its return
  written beside it.
- **The return condition is the owner's judgment, not a state a check can
  read:** "a really fleshed out single agent set up with workspaces all
  working". A session placing the timeline's next row after the schematic puts
  the question to the owner rather than placing the generalization by pathway
  order.

**Why the edit waits for `PL-V1Y7`'s pull request, #1134.** It renumbers the
same rows - break-out off, the schematic to v0.7.0, multi-substance to v0.8.0 -
and its session is past its budget, so a conflict left on its side would have
nobody to resolve it. This branch brings `main` in once #1134 lands and edits
what #1134 wrote.

**What the edit touches, measured on #1134's branch, 2026-09-26.** In
`ROADMAP.md`: the multi-substance row, Gate 4's "ships inside v0.8.0" and the
Beyond row in § "The timeline"; § "The plan"'s renumbering history ("both moved
back one"); catalogue item 34's note that multi-substance moved "to v0.8.0 as a
consequence"; and this branch's Phase 1 sentence and known-risk sentence in
§ "Development pathway". Outside it: the UI-structure thread's renumbering line
in `docs/WORKING_NOTES.md`, and `PL-L6QR`'s `blocked-by` note if it names that
release. `docs/MODEL.md`, `src/` and `tests/` name neither version.

**Done when.** The pathway orders only what the timeline has not placed (done
2026-09-26); the timeline names no multi-substance release, and its Beyond row
carries the generalization with items 6 and 7, this decision dated, and the
condition for its return; and the known risk's last sentence points at that
row instead of at this item.
