---
id: PL-SRXT
title: docs/MODEL.md mixes British and US spelling (modelled 40 times against modeled 22, vapour 60 against vapor 90 on 2026-11-08), though PL-XF89 settled the tree on US spelling, and the copy editor leaves the British forms in place
priority: P3
effort: M
status: ready
classes: docs
feature: model-md-structure
touches: docs/MODEL.md, docs/INTERFACE.md
added: 2026-11-08
payoff: the specification reads as one edited document in the project's US spelling, while every quoted interface label still matches the screen
verify: ! grep -qF 'modelled fractions with that solution' docs/MODEL.md && ! grep -qF 'The vapour-to-liquid ratio is derived' docs/INTERFACE.md
---

**Problem.** docs/MODEL.md mixes British and US spelling (modelled 40 times against modeled 22, vapour 60 against vapor 90 on 2026-11-08), though PL-XF89 settled the tree on US spelling, and the copy editor leaves the British forms in place

**Where it was found.** `PL-F0Q2`'s debug run of the copy editor on
§ "Delivery-limit and MAC parameters" (run `fix6-p043`, 2026-11-08) left "not
modelled" beside "None of these are modeled here", and "gas–vapour blender",
in one section. The counts above come from `grep -c` on `docs/MODEL.md` as it
stood before `#2049`.

**Recommendation.** Spelling is decidable from the text, so it belongs in a
script, which gives the same result every run, rather than in the copy
editor's instructions, which a model applies differently from run to run. Replace the British forms across the
document in one commit, then make a check refuse them. While a workflow-lane
generator is live, the check is captured and not built. The one-time
replacement is ordinary document work. `PL-4BGX` (the vaporizer-class
paragraph) also asks for "gas-vapor blender", the source's term.

**Checked 2026-11-09:** On cfd4a4b6, `grep -o -i` counts in `docs/MODEL.md` give modelled 53 against modeled 19, vapour 71 against vapor 101 (the second count includes "vaporizer"), and litre 110 against liter 27. The two run-found instances in § "Delivery-limit and MAC parameters" are gone, but the mix remains. Some British forms quote the interface exactly and must stay as they are while the interface uses them. `src/anesthesia_sim/app/` prints "Modelled concentrations: {agent}", the hover marker "Modelled", "mL vapour" and "millilitres of liquid". `PL-XF89` settled US spelling for `README.md` and `pyproject.toml`, not for the interface's strings.

**Why it matters.** Mixed spelling in one document makes it look unedited, and a reader may wonder whether "modelled" and "modeled" mark two different things. The bigger risk is the opposite fix: changing a quoted interface label in the document so that it no longer matches what the learner sees on screen.

**Done when.** `docs/MODEL.md`'s own prose uses US spelling throughout (modeled, vapor, liter, behavior). Text quoted from the interface, from a source or from a code name stays exactly as written there. Whether the interface's own labels change to US spelling is a separate item, and so is a check that refuses British forms. That check is captured, not built, while a workflow-lane generator is live.

**Generator check.** One-off: a spelling inconsistency found by a copy-editor debug run. No head's `misread:` states that fact.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Present. At 817a4d88, `docs/MODEL.md` already mixed the spellings: `grep -o -i` counts modelled 39 against modeled 27, and vapour 24. The item is classed `docs` only, which is not debt, so v0.7.0's gate does not take it: it stays off the frozen list and needs no deferral.
