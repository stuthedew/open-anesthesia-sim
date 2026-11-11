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

**Added 2026-11-10: Tab may not reach a button on a Mac at all.** Qt's
`Qt::FocusPolicy` documentation says of `Qt::StrongFocus`: "On macOS this will
also be indicate that the widget accepts tab focus when in 'Text/List focus
mode'" (https://doc.qt.io/qt-6/qt.html, the whole page read on 2026-11-10).
So a system setting on the Mac decides whether Tab stops on a button. Which
setting, and its default, are not confirmed: Apple's help page returned no
readable text to a direct request. The owner's check therefore has three
possible results, and each is a different finding: Tab reaches Start and a
mark shows; Tab reaches Start and no mark shows; Tab never reaches Start.

**Added 2026-11-10: a script on the Mac can take the check, with no key
pressed.** The session working `PL-RF2S` sent this, and the two Qt facts in
it were re-read here.

- A cloud session cannot take the check. Its Linux container offers two
  styles, `Windows` and `Fusion` (`QStyleFactory.keys()`, run 2026-11-10),
  and neither is the macOS style.
- A session running on the Mac can. It builds the dashboard under the native
  style and grabs an image of Start three times: at rest, after
  `setDown(True)`, and after `setFocus(Qt.FocusReason.TabFocusReason)`. Images
  that differ show a pressed state or a focus mark.
- `QGuiApplication.styleHints().tabFocusBehavior()` says whether Tab stops on
  a button. Qt documents the property as "the focus behavior on press of the
  tab key" (https://doc.qt.io/qt-6/qstylehints.html, read 2026-11-10), with
  the values `NoTabFocus`, `TabFocusTextControls`, `TabFocusListControls` and
  `TabFocusAllControls` (https://doc.qt.io/qt-6/qt.html). Neither page says
  that the value follows the Mac's keyboard setting, so that link is not
  confirmed.

The `PL-RF2S` session recommended to the owner that the focus and pressed
states be built first and the Mac looked at once afterwards. This session
agrees (2026-11-10): the interface pass defines every state of every control
itself, so the result of the check does not change what is built. The owner
had not answered when this was written.

**The owner's answer, 2026-11-11: Tab never reaches Start.** The owner ran
`make run` on `main` on their Mac and told the session working `PL-RF2S`:
"tab never reaches start. Cycles through tabs "overview, induction,
maintenance" then drop downs "concentration, parameters."" So Tab stops on
the Workspace tabs and the two drop-downs, and on no button.

The link that the pages above left open is in Qt's source. Its Cocoa theme
returns `Qt::TabFocusAllControls` only when
`[NSApplication isFullKeyboardAccessEnabled]` is true, and otherwise
`Qt::TabFocusTextControls | Qt::TabFocusListControls`
(`case TabFocusBehavior` in
https://raw.githubusercontent.com/qt/qtbase/dev/src/plugins/platforms/cocoa/qcocoatheme.mm,
read 2026-11-11). Apple's list of keyboard shortcuts gives the switch:
"Control-F7 or Fn-Control-F7: Change the way Tab moves focus—between
navigation of all controls on the screen, or only text boxes and lists"
(https://support.apple.com/en-us/102650, read 2026-11-11). Apple's page on
keyboard settings names the setting "Keyboard navigation"
(https://support.apple.com/guide/mac-help/keyboard-settings-kbdm162/mac, read
on 2026-11-11 as a search result's extract, because the page's body is not in
its HTML).

So on the owner's Mac that setting is off, and a button takes Tab only when a
reader turns it on. Whether Start shows a focus mark with the setting on is
still not observed.

**Relation to the interface pass.** The pass will define every state of every
control (`PL-HS9M`, `PL-BVC5`). This finding does not wait for it: a focus
mark and a pressed state on these three buttons can land alone.
