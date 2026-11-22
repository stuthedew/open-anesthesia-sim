---
id: PL-35L9
title: The wash-in View writes F_A/F_I with underscores, a programmer's notation, where the anesthesia literature writes FA/FI with subscripts
status: untriaged
feature: interface-design-review
added: 2026-11-22
---

**Problem.** The wash-in View writes F_A/F_I with underscores, a programmer's notation, where the anesthesia literature writes FA/FI with subscripts

**Go-ahead.** The design review that found this was approved by the project owner (project owner, 2026-11-22). It ran offscreen on `a7eb53f`, with screenshots of each Workspace and each View at 1366 by 768 and 1920 by 1080 in `/mnt/project-files/v0.7.0/design-review/`.

**What a learner sees.** "Wash-in: F_A/F_I, alveolar as a fraction of the
modelled circuit", a legend row "F_A/F_I (solid)", "Now: F_A/F_I = 0.77", an
axis title "F_A/F_I" and "F_I = modelled circuit, not the vaporizer dial"
(`view-wash_in-1920x1080.png`).

**Why it matters.** The underscore is how a programmer writes a subscript. The
learner knows the ratio as FA/FI with the A and I set as subscripts, which
is how `docs/INTERFACE.md` § "F_A/F_I as a displayed ratio" typesets it.

**What to do.** Write the subscripts as subscripts: rich text with `<sub>` in
the labels, and the plot's axis title as HTML, which pyqtgraph accepts. Keep a
plain "FA/FI" for the accessible name. Every string changes in the approved
wording list.

**Done when.** No visible string in the wash-in View contains "F_A" or "F_I",
and the approved wording list shows the new forms.
