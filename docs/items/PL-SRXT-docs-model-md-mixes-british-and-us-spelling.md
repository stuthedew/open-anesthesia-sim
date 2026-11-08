---
id: PL-SRXT
title: docs/MODEL.md mixes British and US spelling (modelled 40 times against modeled 22, vapour 60 against vapor 90 on 2026-11-08), though PL-XF89 settled the tree on US spelling, and the copy editor leaves the British forms in place
status: untriaged
added: 2026-11-08
---

**Problem.** docs/MODEL.md mixes British and US spelling (modelled 40 times against modeled 22, vapour 60 against vapor 90 on 2026-11-08), though PL-XF89 settled the tree on US spelling, and the copy editor leaves the British forms in place

**Where it was found.** `PL-F0Q2`'s debug run of the copy editor on
§ "Delivery-limit and MAC parameters" (run `fix6-p043`, 2026-11-08) left "not
modelled" beside "None of these are modeled here", and "gas–vapour blender",
in one section. The counts above are `grep -c` on `docs/MODEL.md` as it stood
before `#2049`.

**Recommendation.** Spelling is decidable from the text, so it belongs in a
script rather than in the copy editor's instructions, where every rule added
restarts the section-by-section debug. Replace the British forms across the
document in one commit, then make a check refuse them. While a workflow-lane
generator is live, the check is captured and not built; the one-time
replacement is ordinary document work. `PL-4BGX` (the vaporizer-class
paragraph) also asks for "gas-vapor blender", the source's term.
