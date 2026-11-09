---
id: PL-6LBQ
title: ROADMAP.md planned item 27 says fat holds a third of the agent at three hours, while v0.7.0's Goal table gives 30% at 180 min
priority: P3
effort: S
status: untriaged
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
---

**Problem.** ROADMAP.md planned item 27 says fat holds a third of the agent at three hours, while v0.7.0's Goal table gives 30% at 180 min

**Found by** the copy editor's structure read of `ROADMAP.md` (2026-11-06), finding 58 of its outline read. Rows are `ROADMAP.md` at `aff76df1`, before the restructure's first slice (`PL-W0TS`) moved its sections; the quoted words find each passage after the move. The finding is quoted whole, as a block.

```text
- Query: item 27 says fat holds "a third at three hours" (8465-8477), but v0.7.0's Goal table gives 30% at 180 min (6933).
```

**Why it matters.** Fat's share of the agent at three hours is a model result that the schematic shows. The two passages state it differently, and one of them may not match what the model computes.

**Done when.** The roadmap gives one answer, taken from the tree where the tree holds it and from the project owner where it does not, and every passage that stated the other answer is corrected.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. "A third at three" in item 27 and the Goal table's 180 min row were both written in `817a4d88`.
