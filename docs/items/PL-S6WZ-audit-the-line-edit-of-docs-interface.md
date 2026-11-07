---
id: PL-S6WZ
title: Audit the line edit of docs/interface-provenance.md (#2045) section by section for dropped statements, qualifiers, requirements and reasons, as PL-B7V7 did for the machine docs, and restore each: #2045 was checked only for dropped names, numbers and dates, and it dropped at least the unknown-region-type warning and the 'oversight' conclusion the restructure brief PL-T8RL cites
priority: P2
effort: M
status: done
classes: defect, docs
feature: interface-provenance-structure
touches: docs/interface-provenance.md
deferred-from: v0.7.0 - a contributor document's wording, with no displayed value or schematic behaviour depending on it
added: 2026-11-07
closed: 2026-11-07
pr: 2053
payoff: a contributor reads each reason, qualifier and correction the study recorded about Blender, none lost to the line edit
verify: grep -q 'deliberate narrowing of Blender' docs/interface-provenance.md && grep -q 'They are vestigial' docs/interface-provenance.md
---

**Problem.** Audit the line edit of docs/interface-provenance.md (#2045) section by section for dropped statements, qualifiers, requirements and reasons, as PL-B7V7 did for the machine docs, and restore each: #2045 was checked only for dropped names, numbers and dates, and it dropped at least the unknown-region-type warning and the 'oversight' conclusion the restructure brief PL-T8RL cites

**Why it matters.** `#2045` (`PL-ZMBN`) line-edited the document with the copy editor and checked the result only for dropped Blender names, numbers, dates and item ids. The same edit, checked the same way, had dropped or weakened statements in most sections of `docs/MODEL.md` (`PL-95SW`) and of the machine documents (`PL-B7V7`). A contributor designing a Workspace, Area or View reads this document to learn what was adopted, refused, and why. A lost "only" or a lost reason changes what that contributor builds.

**How.** The document as it stood before `#2045` (`cfb15a4a`) and after it (`3c8ea4f1`, before `PL-T8RL`'s restructure) have the same headings. Each of the 29 sections the edit changed goes to a reviewer, who lists every statement, qualifier, requirement, scope limit or reason that the old text had and the new text lacks anywhere in the document, quoting both. Each finding is checked against the text, and each confirmed loss is restored at the place where `PL-T8RL`'s restructure now keeps that topic. This runs on the restructure's branch, so that two branches do not edit the same file (coordinator, 2026-11-07).

**Done when.** Every section `#2045` changed has been compared, and each statement the comparison found missing or weakened is back in the restructured document, or is recorded here with the reason it was not restored.

**Generator check.** The copy editor dropping requirements, qualifiers and reasons caused these losses. That mechanism is filed as `PL-F0Q2`, and every other copy edit waits for its fix (project owner, 2026-11-07). This item is one more instance of it, found because `PL-T8RL`'s brief cited two statements that the line edit had removed.

**What was found.** Three reviewers compared the 29 changed sections, each with the whole of both texts in front of it, and every finding was checked against both texts before anything was restored. The line edit had removed no name, number or date, but it had removed or weakened statements in most sections. They fall into four kinds:

1. **Reasons and conclusions.** Examples are why the document exists and the question the owner asked on 2026-09-16, that the prose licence is the constraint most likely to be got backwards, that Blender's minimum-size fields are vestigial and why the reading widened from headers to implementation, that the isolation finding falsified the expectation the research set out to test, why arguing from expressive power is a trap, that the six-operation result came from trying to falsify the opposite, that Blender is no evidence *at all* for this project's safety argument, and that collapsing a required value is the failure the unconditional set exists to prevent.
2. **The study's corrections of its own first version.** "Gizmo-driven" was withdrawn, "the main region has no role" was too strong, the claims that the interface renamed the screen "layout" and that a temporary window adds a hidden screen were first-version claims no page confirms, Non-Modal was first described wrongly, the tablet limit is Blender's own account rather than an implication, and the first reading overstated Blender's silence about a missing editor. The line edit had kept the corrected statements and dropped the record that they were corrections.
3. **Qualifiers and scope.** Examples are a View given no route to its container *at all*, *by construction*, as a deliberate narrowing of Blender's contract; `bScreen` as an ID block; the flag set *on the main database*; *shipped* rather than *default* workspaces; RNA as the layer `bpy` reads; the window-maximize claim read *at source* because the Manual page was unreachable; the unconditional region *outside that window's own area system*; and the occlusion rule being `docs/MODEL.md`'s, cited rather than restated.
4. **Attribution.** Each documentation licence is tied to its team again, and the reason the README credited Blender only from v0.6.0 is back.

**What was done.** Fifty-one edits put each finding back at the place where `PL-T8RL`'s restructure keeps its topic, in the restructure's own words where the two overlap. The verify line greps two of the restored phrases, which neither `origin/main` nor the restructure commit contains.

**Not restored, and why.**

- The line edit's use of "View" where the old text said "Editor" for this project's occupant of an Area. That was the deliberate `PL-ZMBN` fix (commits `90e12f79` and `d223f1da`), and the document's opening paragraph now gives the reason.
- `RGN_ALIGN_FLOAT` described as an alignment. The reviewer flagged it, but Blender's `DNA_screen_types.h` at commit `931bb2e7` declares it in `eRegion_Alignment`, so the line edit's wording is correct.
- "Layout menu" where the old text said "Workspace menu". The code names it "Layout" (`workspace_tabs.py`, `LAYOUT_MENU_LABEL`), so the line edit corrected a stale name.
- Changed bold opening phrases of Adopted and Diverged entries. Only closed items quote the old phrases, and the documentation check passes.
- The terms "extend-drag" and "snap-merge". Only the closed `PL-3J2P` uses them, and the document describes both behaviours in full.
- "This file is about the outside model we studied, not about our tree." `PL-JVK4` questions exactly that claim, so restoring it would prejudge that item.
