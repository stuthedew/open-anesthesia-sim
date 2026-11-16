---
id: PL-8RFG
title: docs/MODEL.md uses 'gate' for four different checks (step-refinement, independent-solution, published-data and release), so a clinician cannot tell them apart; give each its own name (copy editor structure read, 2026-11-05)
priority: P3
effort: S
status: done
classes: defect, docs
feature: model-md-structure
touches: docs/MODEL.md
added: 2026-11-05
closed: 2026-11-16
pr: 2168
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

**Done 2026-11-16.** Each check in `docs/MODEL.md` now has one name, used
wherever it is meant, and no sentence says just "the gate":

1. The relative-residual threshold in § "Mass-balance identity"
   (`MASS_BALANCE_RELATIVE_GATE`) is "the mass-balance tolerance". The section
   called it "the release gate", which was also the name of § "Release gate".
   The same name now appears in § "Mass-balance test", in the developer note
   on the reference-condition gap, and in the mass-balance bullet of
   § "Release gate", which now points to § "Mass-balance identity".
2. The set of checks against published measurements in people keeps its
   existing name, "the published-data gate", which its section heading and the
   test module (`tests/reference/test_published_wash_in_and_elimination.py`)
   already use. Every bare "the gate" in § "What the published-data gate can
   and cannot resolve" and § "The first 24 hours of elimination against the
   published mean curves" now says "the published-data gate".
3. § "Release gate" keeps its heading and is now the only use of "release
   gate" in the document.
4. "The directional gates in `tests/reference/test_sevo_patient.py`" now says
   "directional checks", since they are ordinary test assertions.

No heading was renamed, so no citation changed. The halt gate (`halt_gate`) is
named in code only. "A frozen gate list" and `check_gate_counts` in § "How
this document is held to the tree" refer to the queue's debt gate, not to a
check of the model, and were left as they are. Pull request #2121 changes
none of the lines this item changed. Docs sweep: `grep -n -i '\bgates\?\b'`
over `docs/MODEL.md` and `docs/INTERFACE.md`, including words split across a
line break.
