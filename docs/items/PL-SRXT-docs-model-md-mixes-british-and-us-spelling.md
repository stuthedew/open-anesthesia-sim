---
id: PL-SRXT
title: docs/MODEL.md mixes British and US spelling (modelled 40 times against modeled 22, vapour 60 against vapor 90 on 2026-11-08), though PL-XF89 settled the tree on US spelling, and the copy editor leaves the British forms in place
priority: P3
effort: M
status: done
classes: docs
feature: model-md-structure
milestone: v0.6.20
touches: docs/MODEL.md, docs/VERIFICATION.md, docs/INTERFACE.md, docs/items/PL-KXRB-the-interface-s-labels-spell-modelled-vapour.md
added: 2026-11-08
closed: 2026-11-22
pr: 2235
payoff: the specification reads as one edited document in the project's US spelling, while every quoted interface label still matches the screen
verify: ! grep -qF 'The ratio is a modelled value' docs/MODEL.md
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

**Checked 2026-11-22** against `d4e8200`: still applies. `docs/MODEL.md` still mixes the spellings: whole-word `grep -o -i -w` counts give modelled 13 against modeled 17, litre 26 against liter 24, millilitre 11 against milliliter 0, and behaviour 6 against behavior 5. Both sentences that the `verify:` line looks for are still present, in `docs/MODEL.md` and `docs/INTERFACE.md`. The counts fell because #2109 (`PL-CTXZ`) moved the interface sections to `docs/INTERFACE.md`, which now holds most British forms (modelled 42, vapour 40, litre 74), many of them quoted interface labels that stay while `PL-KXRB` is open. One sequencing risk: `PL-48MX` will replace what is left of `docs/MODEL.md`, which is the reason `PL-XLDN` and `PL-YKKC` wait on it, so a spelling pass on `docs/MODEL.md` now lands partly in text that `PL-48MX` rewrites. The `docs/INTERFACE.md` half does not have that risk.

**Done 2026-11-22.** The prose of `docs/MODEL.md` now uses US spelling. These are the whole-word counts from `grep -o -i -w` on this branch, before and after the change:

- modelled 9 and 0, against modeled 5 and 14.
- vapour 7 and 2, against vapor 16 and 21.
- litre 1 and 0, and litres 1 and 0, against liter 0 and 1, and liters 0 and 1.
- millilitres 2 and 0, against milliliters 0 and 2.
- labelled 4 and 0, centre 1 and 0, manoeuvre 3 and 0, randomised 1 and 0, and dialled 1 and 0.
- behaviour 0 before the change.

The two "vapour" that remain are the unit labels "L vapour" and "mL vapour", which the screen shows (`AGENT_VAPOUR_LITRES` and `AGENT_VAPOUR_MILLILITRES` in `src/anesthesia_sim/app/display_units.py`). The quotation keeps them while `PL-KXRB` (the spelling of the interface's labels) is open. The reference list keeps each source's own spelling: the journal titles with *Anaesth* and *Anaesthesia*, "inhaled anaesthetics" and "An electric analogue". No heading held a British form, so no heading changed. The two sentences that the earlier `verify:` line looked for now read "modeled" in `docs/VERIFICATION.md` and "vapor" in `docs/INTERFACE.md`. The rest of those two files is unchanged, because other branches are editing them. That line joined two searches, and a closing item keeps only one, so `verify:` now looks for one sentence of `docs/MODEL.md` that this change rewrote.

Files checked:

1. `docs/MODEL.md` in full, for British forms.
2. `src/anesthesia_sim/app/display_units.py`, `formatting.py`, `chart_frame.py` and `dashboard_frame.py`, for each label that the document quotes.
3. `src/`, `tests/`, `tools/`, `docs/` and `ROADMAP.md`, for any quotation of a changed sentence. None quotes one.
4. `tests/reference/test_mac_awake_washout_figures.py`, which reads "the band's centre" from `docs/INTERFACE.md` and not from `docs/MODEL.md`.
