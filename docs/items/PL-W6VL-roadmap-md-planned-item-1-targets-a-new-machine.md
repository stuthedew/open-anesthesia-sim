---
id: PL-W6VL
title: ROADMAP.md planned item 1 targets a new machine as one data file with no change to core/, while item 40 says that target cannot be reached, because a machine is one data file plus one provenance row per number
priority: P2
effort: S
status: ready
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
payoff: A contributor adding an anesthesia machine reads one cost target that says it includes a provenance row for each number.
verify: ! grep -qF 'but the target should' ROADMAP.md
---

**Problem.** ROADMAP.md planned item 1 targets a new machine as one data file with no change to core/, while item 40 says that target cannot be reached, because a machine is one data file plus one provenance row per number

**Found by** the copy editor's structure read of `ROADMAP.md` (2026-11-06), finding 41 of its outline read. Rows are `ROADMAP.md` at `aff76df1`, before the restructure's first slice (`PL-W0TS`) moved its sections; the quoted words find each passage after the move. The finding is quoted whole, as a block.

```text
- "A machine's whole effect on the model is two rates and one volume in the breathing circuit's row" (8161-8182) and "a machine affects the model only through two rates and one volume" (9597-9604): the fact belongs in item 40, which builds the framework, and item 1 keeps a pointer. Query: item 1 gives the cost target as one data file "with no change to core/" (8184-8188). Item 40 says that target "cannot be reached ... a machine is one data file plus one provenance row per number. The target should say so" (9621-9626).
```

**Why it matters.** Item 1's cost target is what a contributor adding an anesthesia machine aims at. One passage promises no change to `core/`, and the other says the target cannot be reached as written. The rest of the finding, where the machine fact belongs, is slice 7 (`PL-M3MV`).

**Done when.** Item 1's cost target says that a machine already in the closed set is one data file plus one provenance row in `docs/MODEL.md` for each number in it, with no change to `core/`. Item 40 no longer says the target is wrong.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. Item 1's one-data-file target and the later sentence saying it is not reachable were both in `ROADMAP.md` at `817a4d88`.

**Checked 2026-11-09:** item 1 still ends its scope test with "one data file under `src/anesthesia_sim/data/machines/`. It needs no change to `core/` and no new test of the physics". Item 40 still says that target "cannot be reached under this project's checks", because each number in a data file needs a provenance row in `docs/MODEL.md`, "but the target should say so".

**Generator check.** One-off: a finding from the `ROADMAP.md` structure-read sweep. The fact misread is whether one `ROADMAP.md` passage still agrees with a later record of the same thing. No head's `misread:` states that fact for `ROADMAP.md`, and the cluster came from one deliberate read rather than from a mechanism that keeps producing it.
