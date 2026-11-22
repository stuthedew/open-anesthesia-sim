---
id: PL-B45W
title: Tab does not follow reading order: it reaches the control-change record and the Workspace '+' button first, and the agent selector, Start, Reset, Playback and the four parameter dials only after every Area
status: untriaged
feature: interface-design-review
added: 2026-11-22
---

**Problem.** Tab does not follow reading order: it reaches the control-change record and the Workspace '+' button first, and the agent selector, Start, Reset, Playback and the four parameter dials only after every Area

**Go-ahead.** The design review that found this was approved by the project owner (project owner, 2026-11-22). It ran offscreen on `a7eb53f`, with screenshots of each Workspace and each View at 1366 by 768 and 1920 by 1080 in `/mnt/project-files/v0.7.0/design-review/`.

**What was measured.** Walking Qt's focus chain in the Default Workspace at
1366 by 768 gives this order: the control-change record's scroll area, the
page's scroll area, the Workspace "+" button, the three Workspace tabs, the
Concentrations Area (chooser, time base, the six trace check boxes, the plot),
the Parameters, Bookmarks and Branch choosers, three Area borders, then the
agent selector, Start, Reset and Playback, then the four parameter dials, Edit
bookmarks, and the Branch selector and button. The dials belong to the
Parameters Area but are reached about twenty stops after its chooser.

**Why it matters.** WCAG 2.2 Success Criterion 2.4.3, Focus Order (Level A),
says that "focusable components receive focus in an order that preserves
meaning and operability"
(https://github.com/w3c/wcag/blob/main/guidelines/sc/20/focus-order.html,
read 2026-11-22). A keyboard user who wants to start a run tabs past every
Area first, and a user who tabs to the Parameters Area does not reach its
dials next. The order comes from when each widget was built, not from
where it sits.

**What to do.** Set the chain each time the Areas are drawn: the
unconditional region from left to right (agent, Start, Pause, Reset,
Playback), the control-change record, the Workspace tabs and "+", then each
Area in reading order with its chooser followed by its View's own controls,
and the Area borders last. Blender gives no model for Tab here, so this
follows the platform's reading order.

**Done when.** A test walks the focus chain in each shipped Workspace and
finds the transport controls before any Area, and each View's controls
directly after its own chooser.
