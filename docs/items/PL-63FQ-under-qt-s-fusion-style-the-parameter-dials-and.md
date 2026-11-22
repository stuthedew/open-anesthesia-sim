---
id: PL-63FQ
title: Under Qt's Fusion style the parameter dials and the trace check boxes draw no keyboard focus mark, so a keyboard user cannot see which dial the arrow keys will move (PL-CXYV covers only Start, Pause and Reset)
status: untriaged
feature: interface-design-review
added: 2026-11-22
---

**Problem.** Under Qt's Fusion style the parameter dials and the trace check boxes draw no keyboard focus mark, so a keyboard user cannot see which dial the arrow keys will move (PL-CXYV covers only Start, Pause and Reset)

**Go-ahead.** The design review that found this was approved by the project owner (project owner, 2026-11-22). It ran offscreen on `a7eb53f`, with screenshots of each Workspace and each View at 1366 by 768 and 1920 by 1080 in `/mnt/project-files/v0.7.0/design-review/`.

**What was measured.** Offscreen, under Qt's Fusion style, a parameter dial
and a trace check box given the focus with `Qt.FocusReason.TabFocusReason`
paint the same pixels as when they are not focused. The Workspace "+" button
does draw a focus border. `PL-CXYV` records the same defect for Start, Pause
and Reset only. Whether the macOS style draws a mark on the owner's machine
is not settled by an offscreen grab.

**Why it matters.** WCAG 2.2 Success Criterion 2.4.7, Focus Visible (Level
AA), says that "the keyboard focus indicator is visible"
(https://github.com/w3c/wcag/blob/main/guidelines/sc/20/focus-visible.html,
read 2026-11-22). The arrow keys move a dial
that has the focus, so a keyboard user who cannot see which dial is focused
can change the wrong setting.

**What to do.** Give every focusable control a focus mark, in the custom Qt
style that `PL-8G4V` moves into the app, since `PL-BVC5` chose that style for
control states. Work it with `PL-CXYV`.

**Done when.** A test renders each focusable control kind with and without
the focus and finds the two images differ.
