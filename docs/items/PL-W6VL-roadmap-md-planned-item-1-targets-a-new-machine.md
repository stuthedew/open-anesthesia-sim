---
id: PL-W6VL
title: ROADMAP.md planned item 1 targets a new machine as one data file with no change to core/, while item 40 says that target cannot be reached, because a machine is one data file plus one provenance row per number
priority: P3
effort: S
status: untriaged
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
deferred-from: v0.7.0 - filed after the gate froze; the roadmap's arrangement and wording, with no displayed value depending on it
added: 2026-11-07
---

**Problem.** ROADMAP.md planned item 1 targets a new machine as one data file with no change to core/, while item 40 says that target cannot be reached, because a machine is one data file plus one provenance row per number

**Found by** the copy editor's structure read of `ROADMAP.md` (2026-11-06), finding 41 of its outline read. Rows are `ROADMAP.md` at `aff76df1`, before the restructure's first slice (`PL-W0TS`) moved its sections; the quoted words find each passage after the move. The finding is quoted whole, as a block.

```text
- "A machine's whole effect on the model is two rates and one volume in the breathing circuit's row" (8161-8182) and "a machine affects the model only through two rates and one volume" (9597-9604): the fact belongs in item 40, which builds the framework, and item 1 keeps a pointer. Query: item 1 gives the cost target as one data file "with no change to core/" (8184-8188). Item 40 says that target "cannot be reached ... a machine is one data file plus one provenance row per number. The target should say so" (9621-9626).
```

**Why it matters.** Item 1's cost target is what a contributor adding an anesthesia machine aims at. One passage promises no change to `core/`, and the other says the target cannot be reached as written. The rest of the finding, where the machine fact belongs, is slice 7 (`PL-M3MV`).

**Done when.** The roadmap gives one answer, taken from the tree where the tree holds it and from the project owner where it does not, and every passage that stated the other answer is corrected.
