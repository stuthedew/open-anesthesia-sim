---
id: PL-S2LW
title: ROADMAP.md's baseline says v0.7.0 and v0.8.0 are given to milestone sections, but there is no v0.8.0 section, and § "The plan" lists only rows 5, 7, 9 and v0.4.26 as having sections
priority: P2
effort: S
status: done
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
closed: 2026-11-10
pr: 2082
payoff: A session cutting a patch can tell from the baseline whether v0.8.0 is free, instead of reading of a section that does not exist.
verify: ! grep -qF 'test-driven `main`. v0.7.0 and v0.8.0' ROADMAP.md
---

**Problem.** ROADMAP.md's baseline says v0.7.0 and v0.8.0 are given to milestone sections, but there is no v0.8.0 section, and § "The plan" lists only rows 5, 7, 9 and v0.4.26 as having sections

**Found by** the copy editor's structure read of `ROADMAP.md` (2026-11-06), finding 52 of its outline read. Rows are `ROADMAP.md` at `aff76df1`, before the restructure's first slice (`PL-W0TS`) moved its sections; the quoted words find each passage after the move. The finding is quoted whole, as a block.

```text
- Query: 279-286 says "v0.7.0 and v0.8.0 are 'given to milestone sections'", but there is no v0.8.0 section, and 471-477 lists only rows 5, 7, 9 and v0.4.26 as having sections.
```

**Why it matters.** Which release numbers are already spent decides what number the next release takes. The passage names a section that does not exist.

**Done when.** § "Current baseline" names only the versions that have a milestone section, or says what else reserves v0.8.0 (its timeline row) in the terms of § "Versioning decision" → "Which numbers a patch cut may take", so a reader can tell whether v0.8.0 is free for a patch cut.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. "v0.7.0 and v0.8.0 are given to milestone sections" was in `ROADMAP.md` at `817a4d88`, with no v0.8.0 heading.

**Checked 2026-11-09:** § "Current baseline" still says "v0.7.0 and v0.8.0 are given to milestone sections". There is no v0.8.0 section; v0.8.0 has only timeline row 11. § "The plan" correctly lists rows 5, 7 and 9 and the v0.4.26 row as having sections. Each release cut copies the phrase from the baseline before it, and 59 cut briefs carry "given to milestone sections".

**Generator check.** One-off: a finding from the `ROADMAP.md` structure-read sweep. The fact misread is whether one `ROADMAP.md` passage still agrees with a later record of the same thing. No head's `misread:` states that fact for `ROADMAP.md`, and the cluster came from one deliberate read rather than from a mechanism that keeps producing it.

**Done 2026-11-10.** § "Current baseline" now says only that v0.7.0 has its own milestone section, so no patch release may take that number, in the terms of § "Versioning decision" → "Which numbers a patch cut may take". It no longer names v0.8.0, which has a timeline row and no section. No release tool writes the phrase, so the next cut copies the corrected baseline. The 59 closed cut briefs that carry the old phrase are records and are left as they are.
