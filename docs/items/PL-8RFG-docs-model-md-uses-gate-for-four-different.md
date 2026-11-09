---
id: PL-8RFG
title: docs/MODEL.md uses 'gate' for four different checks (step-refinement, independent-solution, published-data and release), so a clinician cannot tell them apart; give each its own name (copy editor structure read, 2026-11-05)
priority: P3
effort: S
status: untriaged
feature: model-md-structure
touches: docs/MODEL.md
added: 2026-11-05
payoff: a reader can tell which check a passage means, and so what passing it says about the model
verify: ! grep -qiE '\bthe gate\b' docs/MODEL.md
---

**Problem.** docs/MODEL.md uses 'gate' for four different checks (step-refinement, independent-solution, published-data and release), so a clinician cannot tell them apart; give each its own name (copy editor structure read, 2026-11-05)

**Checked 2026-11-09:** The restructure removed two of the four senses:
"step-refinement gate" and "independent-solution gate" no longer appear.
`grep -n -i '\bgate\b' docs/MODEL.md` still finds three, on 31 lines that say
"the gate":

1. § "Mass-balance identity" calls the relative-residual threshold "the
   release gate" (lines 1440 to 1487).
2. § "What the published-data gate can and cannot resolve" defines "the gate"
   as its set of published-data checks. That section and § "The first 24 hours
   of elimination against the published mean curves" then call it just "the
   gate".
3. § "Release gate" is the list of conditions for a release.

The halt gate (`halt_gate`, line 4951) is a fourth, named in the code.

**Why it matters.** A reader who meets "the gate" in § "The first 24 hours of
elimination", far from its definition, cannot tell whether it means the
published-data checks or the release conditions. So they cannot tell what
passing it says about the model.

**Done when.** Each check has its own name, used wherever it is meant: for
example "the published-data checks", "the mass-balance tolerance" and "the
release conditions". No sentence in the document says just "the gate".

**Generator check.** One-off: a finding from the `docs/MODEL.md`
structure-read sweep of 2026-11-05.

**Present at the Gate 3 freeze (checked 2026-11-09).** The passage this item
fixes was already in its file at `817a4d88`, the commit that froze Gate 3, so
under ROADMAP.md § "The gate is a snapshot, not a moving target" the item
joins v0.7.0's frozen list rather than being deferred by its capture date.
