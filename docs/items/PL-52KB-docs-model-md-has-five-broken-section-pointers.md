---
id: PL-52KB
title: docs/MODEL.md has five broken section pointers: Desflurane's residual sends the reader to a sensitivity run 'under Parameter provenance' (it is in 'What the published-data gate can and cannot resolve'); Known limitations says the Yasuda citation is in 'Parameter provenance'; two pointers name headings that do not exist ('The chart's vertical range is denominated in MAC, and fixed', 'Why the axis is fixed rather than fitted'); 'Mass-balance test' cites 'the release tolerances documented above' with no section (copy editor structure read, 2026-11-05)
priority: P2
effort: S
status: ready
classes: defect, docs
feature: model-md-structure
touches: docs/MODEL.md
added: 2026-11-05
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
