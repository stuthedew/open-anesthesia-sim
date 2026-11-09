---
id: PL-S2LW
title: ROADMAP.md's baseline says v0.7.0 and v0.8.0 are given to milestone sections, but there is no v0.8.0 section, and § "The plan" lists only rows 5, 7, 9 and v0.4.26 as having sections
priority: P3
effort: S
status: untriaged
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
---

**Problem.** ROADMAP.md's baseline says v0.7.0 and v0.8.0 are given to milestone sections, but there is no v0.8.0 section, and § "The plan" lists only rows 5, 7, 9 and v0.4.26 as having sections

**Found by** the copy editor's structure read of `ROADMAP.md` (2026-11-06), finding 52 of its outline read. Rows are `ROADMAP.md` at `aff76df1`, before the restructure's first slice (`PL-W0TS`) moved its sections; the quoted words find each passage after the move. The finding is quoted whole, as a block.

```text
- Query: 279-286 says "v0.7.0 and v0.8.0 are 'given to milestone sections'", but there is no v0.8.0 section, and 471-477 lists only rows 5, 7, 9 and v0.4.26 as having sections.
```

**Why it matters.** Which release numbers are already spent decides what number the next release takes. The passage names a section that does not exist.

**Done when.** The roadmap gives one answer, taken from the tree where the tree holds it and from the project owner where it does not, and every passage that stated the other answer is corrected.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. "v0.7.0 and v0.8.0 are given to milestone sections" was in `ROADMAP.md` at `817a4d88`, with no v0.8.0 heading.
