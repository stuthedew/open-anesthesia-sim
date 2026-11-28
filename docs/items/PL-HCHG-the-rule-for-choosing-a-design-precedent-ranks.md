---
id: PL-HCHG
title: The rule for choosing a design precedent ranks patient monitors and anesthesia workstations first for how a clinical value is drawn, but this is simulation software; compare with simulation programs, Blender and the platform guides instead
priority: P2
effort: S
status: done
classes: docs, ux
touches: .claude/rules/expert-review.md, .claude/skills/docket/modes/design.md, docs/resident-instructions.md
added: 2026-11-28
closed: 2026-11-28
pr: 2345
verify: grep -qF 'use a patient monitor or an anesthesia workstation as the precedent' .claude/rules/expert-review.md
---

**Problem.** The rule for choosing a design precedent ranks patient monitors and anesthesia workstations first for how a clinical value is drawn, but this is simulation software; compare with simulation programs, Blender and the platform guides instead

**Where this comes from.** The owner, 2026-11-28 01:00Z: "Shouldn't use a patient monitor as a comparison. This is simulation software. Not a patient monitor. Please make sure that's a global change." Two threads had already met the case. `PL-JV5H` (the confirmation windows, `#2343`) had taken an IntelliVue monitor as its closest analog, and the owner answered that "Philips monitor is not the same thing as a simulation program". The cause was `.claude/rules/expert-review.md` § "Search the closest analog first", added by `PL-HWZK` (`#2330`) on 2026-11-27. It ranked "the same quantity or signal first", and said that for how a clinical value is drawn "anesthesia workstations, patient monitors and Gas Man rank above Blender". A monitor shows the same quantity, so the rule sent every session to one.

**What changed.** The section now says to compare with simulation software, and names three kinds of precedent in order: Gas Man and other anesthesia or physiology simulators, then Blender for Workspaces, Areas and Views, then the Apple, GNOME and Microsoft desktop guides. It refuses a patient monitor or an anesthesia workstation as the precedent. The three guides are the ones `PL-JV5H` read in full on 2026-11-28. The workstation is refused with the monitor because it is the same class of product, a clinical device, and the old rule named the two together.

The section is resident, and the cap on resident text left room for 72 more characters, so the detail went to `.claude/skills/docket/modes/design.md` step 3, which a design round reads. It says that a general display guideline or paper, such as NUREG-0700 or a study of linked views, stays citable as a source, with a check that a rule written to protect a live value applies to a modelled one. It also says that a monitor may still be named as what a user compares a value with, and a machine's manual as a source of the model's physical data. `docs/resident-instructions.md` § "The closest analog, reworded 2026-11-28" records the move.

**Decisions that cited a monitor, rechecked 2026-11-28.** The search covered every item, rule, skill and standing document for "patient monitor", "monitor", "IntelliVue", "Philips", "IEC 60601-1-8", "workstation" and "closest analog".

1. `PL-JV5H`, the confirmation windows over the readouts. A monitor was the only basis. Redone by its own thread on simulation programs and the desktop guides (`#2343`), and not touched here.
2. `PL-FSXD`, the wash-in plot's limit on the inspired concentration. Its research looked for a monitor's alarm-limit rule, found none, and decided from the United States Pharmacopeia, ASTM E29 and EDQM. The wash-in thread is removing the monitor search (`#2335`), and it is not touched here.
3. `PL-7LZ7`, one axis top for every concentration chart and the schematic (`#2339`, `#2341`). The Philips IntelliVue manual was one of five sources. The decision stands without it: Gas Man, the same class of product showing the same quantity, links its Picture and Graph to one scale (Workbook printed p. 193), and NUREG-0700 guideline 1.3.6-8, Wang Baldonado et al. 2000 and Qu and Hullman 2018 ask for one scale across compared views. Its option 4, a "this chart only" override, took the monitor as its precedent and was not built. Whoever proposes it later needs another source. The closed brief is a record and is not edited (`.claude/rules/citation-drift.md`).
4. `PL-49D5`, no wash-in point while ventilation is stopped. It searched for monitor manuals as the closest analog, read none, and decided from NUREG-0700. Nothing rests on a monitor.
5. `docs/INTERFACE.md` § "Color contrast, and the standard this interface is held to" and `app/theme.py`'s note on `WARNING` (`PL-LL9Y`). They name a monitor's alarm colours only to depart from them, so that the simulator "cannot be mistaken for" a monitor. That agrees with the owner's point, and nothing changes.
6. `docs/INTERFACE.md` § "Displayed precision", "Why not the 0.1 percentage points that agent monitors show". It names the monitor's resolution as the alternative a reader would assume, and rejects it for the simulator's own reason, the legibility of fat and muscle. Nothing changes.
7. The "Modelled" label, the "end-tidal-equivalent" and "inspired" glosses, and the comments beside them in `app/chart_frame.py` and `app/dashboard_frame.py`. They name a monitor as what a user compares a modelled value with, which is a fact about the user and the safety standard's line between modelled and measured values. Nothing changes.

No decision was found whose only basis is a monitor beyond `PL-JV5H`, so nothing goes to the owner.

**Generator check.** The rule was the generator: in two days it sent four sessions to a monitor (`PL-7LZ7`, `PL-JV5H`, `PL-49D5`, `PL-FSXD`). This item fixes it at the rule, so no generator is recorded.

**Done when.** The rule names simulation programs, Blender and the platform guides as the precedents and excludes monitors and workstations, and this brief lists each decision that cited a monitor with its verdict.

**Docs checked.** `.claude/rules/expert-review.md`, `.claude/skills/docket/modes/design.md` and `docs/resident-instructions.md` (changed), `.claude/rules/instruction-writing.md` rule 14 (names "a cited standard, design system or professional product's documentation", still true), `.claude/skills/` (no analog ranking), `docs/interface-provenance.md` (its only "monitor" is a display screen), `docs/INTERFACE.md`, `docs/MODEL.md`, `ROADMAP.md`, `src/anesthesia_sim/app/` and every item brief, by the search above.
