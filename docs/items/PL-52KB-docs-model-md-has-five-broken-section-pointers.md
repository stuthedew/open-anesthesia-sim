---
id: PL-52KB
title: docs/MODEL.md has five broken section pointers: Desflurane's residual sends the reader to a sensitivity run 'under Parameter provenance' (it is in 'What the published-data gate can and cannot resolve'); Known limitations says the Yasuda citation is in 'Parameter provenance'; two pointers name headings that do not exist ('The chart's vertical range is denominated in MAC, and fixed', 'Why the axis is fixed rather than fitted'); 'Mass-balance test' cites 'the release tolerances documented above' with no section (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: done
classes: defect, docs
feature: model-md-structure
touches: docs/MODEL.md, src/anesthesia_sim/app/formatting.py
added: 2026-11-05
closed: 2026-11-11
pr: 2112
payoff: a reader who follows a pointer to check a figure lands in the section that holds its support
verify: ! grep -qF 'The sensitivity measured under § "Parameter provenance"' docs/MODEL.md && ! grep -qF 'with the release tolerances documented above' docs/MODEL.md
---

**Problem.** docs/MODEL.md has five broken section pointers: Desflurane's residual sends the reader to a sensitivity run 'under Parameter provenance' (it is in 'What the published-data gate can and cannot resolve'); Known limitations says the Yasuda citation is in 'Parameter provenance'; two pointers name headings that do not exist ('The chart's vertical range is denominated in MAC, and fixed', 'Why the axis is fixed rather than fitted'); 'Mass-balance test' cites 'the release tolerances documented above' with no section (copy editor structure read, 2026-11-05)

**Checked 2026-11-09:** After the restructure, three of the five pointers are
still wrong and two are gone. `grep -n` finds these three:

1. § "Desflurane's residual, and why the parameter file was not changed" cites
   "The sensitivity measured under § "Parameter provenance"" (line 10402).
   That section measures no sensitivity. The table of edges is in § "What the
   published-data gate can and cannot resolve".
2. § "Known limitations" says "The Yasuda, Targ and Eger citation is in
   § "Parameter provenance"" (lines 12093 to 12094). The full citation is in
   § "Desflurane's residual" (line 10440).
3. § "Mass-balance test" cites "the release tolerances documented above"
   (line 11288) without naming a section. The tolerance is set in § "Mass-balance
   identity" (from line 1440) and in § "Numerical method" (line 1597).

Neither "The chart's vertical range is denominated in MAC, and fixed" nor "Why
the axis is fixed rather than fitted" appears anywhere now.

**Why it matters.** A reader who follows one of these pointers to check a
figure lands in a section that does not hold it, and may conclude that the
figure has no support.

**Done when.** Each of the three pointers names the section that holds what it
points to.

**Generator check.** One-off: a finding from the `docs/MODEL.md`
structure-read sweep of 2026-11-05.

**Present at the Gate 3 freeze (checked 2026-11-09).** The passage this item
fixes was already in its file at `817a4d88`, the commit that froze Gate 3, so
under ROADMAP.md § "The gate is a snapshot, not a moving target" the item
joins v0.7.0's frozen list rather than being deferred by its capture date.

**After the decision to split, 2026-11-11.** The project owner decided on
2026-11-11 to split `docs/MODEL.md` by reader (`PL-P3GZ`), which ends the
hold of 2026-11-10 on this item. It stays startable, because it is on
v0.7.0's frozen list and making it wait on the split would take it off the
release's gate. A pointer fixed before `PL-CTXZ`, `PL-6PPZ` or `PL-FWR6`
moves its section moves with the text. A pointer fixed afterwards is fixed
in the document that then holds it, and may name a section of another
document.

**Done 2026-11-11.** Each of the three pointers now names the section that
holds what it points to.

1. § "Desflurane's residual, and why the parameter file was not changed" now
   points to the sensitivity table in § "What the published-data gate can and
   cannot resolve". That table, measured on 2026-09-06, gives each ratio's
   movement per +10% in one coefficient: +0.45 to +0.55 SD in the
   five-minute elimination ratio for the vessel-rich tissue:gas coefficient,
   and +0.09 to +0.17 SD for blood:gas. It is the measurement the sentence
   describes. `git log -S` shows that § "Parameter provenance" never held it:
   the pointer was wrong from the day `PL-73G7` wrote it.
2. § "Known limitations" now says the full Yasuda, Targ and Eger citation is in
   § "Desflurane's residual, and why the parameter file was not changed",
   the only place in the document that gives it in full.
3. § "Mass-balance test" now names § "Mass-balance identity". It also says
   which of that section's two bounds is which. The "either condition"
   formulas are the run-time thresholds, and the relative residual must also
   stay within the release gate. The old wording called both "the release
   tolerances", which contradicted § "Mass-balance identity"'s statement that
   the release gate is the relative residual alone. The two tests named in the
   section's note for developers assert both bounds.

The check of 2026-11-09 was wrong that "Why the axis is fixed rather than
fitted" appears nowhere. The comment above `CHART_AXIS_TOP_MAC` in
`src/anesthesia_sim/app/formatting.py` still named it, wrapped across two
lines, so a one-line search missed it. The second blind review pass found it.
The comment now names the paragraph "The axis is fixed rather than fitted" in
`docs/MODEL.md` § "F_A/F_I as a displayed ratio". The other missing name, "The
chart's vertical range is denominated in MAC, and fixed", is gone: the
paragraph now opens "The chart's vertical range is set in MAC, and fixed", and
both places that point to it use that wording.

None of the three edits lies in, or points into, the seven interface sections
that `PL-CTXZ` (#2109) is moving. No copy editor run was made on these
passages: the project owner's hold of 2026-11-11 keeps copy editor runs off
`docs/MODEL.md` until `PL-48MX` closes, and his separate pause of the copy
editor still applies.
