---
id: PL-5XG1
title: ROADMAP.md's Development pathway still says Phase 1 follows v0.4.0 unchanged, while the timeline places Phase 1's substance generalization at v0.9.0 behind four releases, which its own known-risk paragraph argues against
priority: P2
effort: S
status: needs-decision
classes: docs
touches: ROADMAP.md
deferred-from: v0.6.0 - filed after the gate froze, and a question of release order that no v0.6.0 entry waits on
added: 2026-09-26
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

**Recommendation (session, 2026-09-26): put the substance generalization with
items 6 and 7 ahead of the schematic, as part of `PL-V1Y7`'s renumbering.**

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

Either answer is recorded, dated, on the timeline row it concerns. The known
risk's last sentence then points at that row instead of at this item.

**Decision needed.** Does the known-risk argument still stand against the
timeline's order? Answer by choosing one: move the substance generalization
with items 6 and 7 ahead of the schematic, as part of `PL-V1Y7`'s renumbering
(recommended above), or keep the order and record the weighing on the
schematic's row.

**Done when.** The pathway orders only what the timeline has not placed (done
2026-09-26), and the answer above is recorded, dated, on the timeline row it
concerns, with the known risk's last sentence pointing there.
