---
id: PL-2WBR
title: docs/interface-provenance.md cites Blender's Copyright Rules handbook with no address or reading date, and the list of pages read leaves it out (copy editor structure read, 2026-11-05)
priority: P3
effort: S
status: ready
classes: defect, docs
feature: interface-provenance-structure
touches: docs/interface-provenance.md
added: 2026-11-05
payoff: a contributor checking the study protocol's rule on copying can open the Blender page it rests on and see when it was read
verify: grep -qF 'handbook/communication/copyright_rules' docs/interface-provenance.md
---

**Problem.** docs/interface-provenance.md cites Blender's Copyright Rules handbook with no address or reading date, and the list of pages read leaves it out (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/interface-provenance.md at cfb15a4a, before the line edit):

- **Query on the Copyright Rules handbook:** rows 84-88 cite Blender's Copyright Rules handbook with no address or reading date, and the list of pages read does not include it. What are its address and reading date?

**Checked 2026-11-09:** `grep -n -i 'copyright' docs/interface-provenance.md` finds the claim in § "Reading is not a restricted act; copying, translating and porting are": "Blender's own Copyright Rules handbook draws the same line between studying and copying". It carries no address and no reading date. § "Pages read on 2026-10-25" lists "the two licence pages", `developer.blender.org/docs/license/` and the Manual's `copyright.html`, but neither is the handbook page. The claim entered with `PL-FTP5` on 2026-09-16, before any `blender.org` page could be read from the container. A probe on 2026-11-09 found the page: `https://developer.blender.org/docs/handbook/communication/copyright_rules/` answered 200, with the title "Copyright Rules - Blender Developer Documentation". The licence page links to it.

**Why it matters.** The study protocol rests its rule on what may be copied partly on this handbook. A contributor checking the rule cannot find the page, and cannot tell whether the claim was ever read at its source.

**Done when.** The page is read, and the sentence says what it states, with the address above and the reading date. The page is added to the list of pages read, under a heading dated for that reading. If the page does not say what the sentence claims, the sentence is corrected to what it does say.

**Generator check.** One-off: a finding from the `docs/interface-provenance.md` structure read (`PL-ZMBN`). The claim predates the first reading of any `blender.org` page and was never sourced.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** `git show 817a4d88:docs/interface-provenance.md` already cites "Blender's own Copyright Rules handbook" with no address or reading date (row 81). So the problem was present at the freeze, commit `817a4d88` (2026-10-24), and this finding belongs on v0.7.0's frozen list rather than deferred.

**Done 2026-11-16.** The page at https://developer.blender.org/docs/handbook/communication/copyright_rules/ was downloaded whole with `curl` through the proxy (HTTP 200) and read as text in full. It does not say what the sentence claimed. It asks for original mockups and designs that build on Blender's own design history, bars copyrighted elements of proprietary software from Blender because they would breach that software's licence agreement, and asks contributors to avoid referring to proprietary software and keep to public information where a mention is essential. It says nothing about studying versus copying, nor about lifted prose or reading another program's source. So the sentence in § "Reading is not a restricted act; copying, translating and porting are" was corrected to what the page states, with its address and reading date, and now says plainly that the page does not draw this study's line between studying and copying. The page was paraphrased, not quoted, because it is CC-BY-SA 4.0 (§ "The prose is the encumbered half, not the source"). A new § "Pages read on 2026-11-16" at the end of the document lists it. Docs sweep: `grep -rn -i 'copyright rules'` outside `docs/items/` finds only `docs/interface-provenance.md` and this item's line on `ROADMAP.md`'s frozen list, which needs no change; `docs/interface-provenance.md` § "How this study was conducted, and where it could not reach" and § "What the code cannot answer: Blender's stated reasoning" were checked and still describe the 2026-10-25 reading correctly.
