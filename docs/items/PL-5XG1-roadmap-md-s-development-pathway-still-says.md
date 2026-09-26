---
id: PL-5XG1
title: ROADMAP.md's Development pathway still says Phase 1 follows v0.4.0 unchanged, while the timeline places Phase 1's substance generalization at v0.9.0 behind four releases, which its own known-risk paragraph argues against
status: untriaged
touches: ROADMAP.md
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

**What `PL-LJVD` already did about it.** Its section at the head of
§ "The plan" makes the timeline hold the order of every release it names, and
narrows the pathway's opening sentence and the catalogue's to the work the
timeline has not named, so a reader is no longer handed two orders. The
paragraphs underneath still assert the old one.

**Two parts, and only the first is a session's.**

1. Rewrite the pathway to the part it holds: what lies past the timeline's
   last named release. Sentences about releases the timeline has placed are
   dropped or dated as history, not re-pointed at new version numbers, since
   re-pointing makes the next copy of the order.
2. Whether the known-risk argument still stands against the order the
   timeline holds is the order features come in, which is the owner's. The
   rows record each move's reason (item 34's placement rounds, `PL-NMTF` and
   `PL-YHWG`); none says the single-agent rework was weighed. The likely
   answer: the two layout releases are substance-agnostic, on the reordering
   note's own argument that the view consumes a `SimulationSnapshot`, and the
   rework concentrates in v0.8.0's schematic, which draws where one agent is.
   Put that to the owner with the count, rather than deciding it in the
   rewrite.
