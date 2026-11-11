---
id: PL-CXYV
title: Start, Pause and Reset look the same pressed, keyboard-focused and at rest
status: untriaged
added: 2026-11-11
---

**Problem.** Start, Pause and Reset look the same pressed, keyboard-focused and at rest

**Measured.** On 2026-11-10 the dashboard was built offscreen on
`0.6.16+g0b1c8b65` under Qt's Fusion style. The Start button was grabbed at
rest, then with `setDown(True)`, then with the keyboard focus given by
`setFocus(Qt.FocusReason.TabFocusReason)` and `hasFocus()` true. All three
images were identical, pixel for pixel.

**Why.** `transport_button_stylesheet` in
`src/anesthesia_sim/app/stylesheets.py` declares the enabled and the disabled
state and no other. `outlined_button_stylesheet` and `filled_button_stylesheet`
declare one state each. A button whose border and background come from a style
sheet draws only the states that the sheet declares.

**Why it matters.** WCAG 2.2 Success Criterion 2.4.7, Focus Visible, is Level
AA: "Any keyboard operable user interface has a mode of operation where the
keyboard focus indicator is visible."
https://github.com/w3c/wcag/blob/main/guidelines/sc/20/focus-visible.html.
WCAG 2.2 Level AA is this interface's stated target. A learner who uses the
keyboard cannot see which run control Enter or Space will press, and a learner
who clicks sees no response from the button.

**Not yet checked.** The owner's Mac draws with the macOS style, which may add
a focus mark of its own. The owner was asked on 2026-11-10 to press Tab and
look at Start, and has not answered. The View chooser and the Workspace tabs
already declare a focus border.

**Relation to the interface pass.** The pass will define every state of every
control (`PL-HS9M`, `PL-BVC5`). This finding does not wait for it: a focus
mark and a pressed state on these three buttons can land alone.
