---
id: PL-KRZW
title: Decide what the interface does under a dark system appearance, now that every colour it declares is a light-theme value
priority: P2
effort: M
status: done
classes: defect, ux
feature: platform-palette
touches: src/anesthesia_sim/app/main.py, src/anesthesia_sim/app/qt_widgets.py, tests/integration/test_dark_appearance.py, docs/MODEL.md
added: 2026-09-17
closed: 2026-09-22
payoff: the window stops mixing a light interface with the host's dark scroll bars and splitter handles, and a widget added later inherits the theme rather than the host
verify: grep -q 'def test_the_chrome_draws_the_theme_rather_than_the_host_palette' tests/integration/test_dark_appearance.py
---

**Problem.** Decide what the interface does under a dark system appearance, now
that every colour it declares is a light-theme value.

`PL-DHBX` fixed the instance - three transport buttons taking their labels from
the host palette. The question it did not answer is the general one: this
interface hard-codes a light theme (`PANEL` `#FFFFFF`, `BACKGROUND` `#F4F7FA`,
`INK` `#243B53`) and never tells Qt so, while Qt's palette follows the system
appearance by default. The two disagree on every machine set to Dark, and the
interface currently wins only where a colour happens to be declared.

**Why it matters.** Two things ride on the answer, and they pull in different
directions.

The first is that the whole contrast apparatus is computed against those two
light surfaces. `tools/contrast_check.py`'s 24 requirements, `docs/MODEL.md` §
"Color contrast, and the standard this interface is held to", and the
dichromacy floors the six chart traces were re-picked against are all measured
on `PANEL` and `BACKGROUND`. If the interface ever rendered dark, every one of
those measurements would be against a surface not on screen - which is a
safety-apparatus failure rather than an aesthetic one. That argues for
declaring the light scheme and being done.

The second is that declaring it is not guaranteed to work.
`QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Light)` exists
since Qt 6.8, and Qt 6.11's own documentation says: "doing so is a hint to the
system, and overriding the color scheme is not supported on all platforms."
So it cannot be the mechanism a legibility guarantee rests on - which is why
`PL-DHBX` declared the button's colours instead. It can still be worth setting
as a belt-and-braces measure that also covers the chrome no stylesheet reaches:
scrollbars, splitter handles, tooltips, native dialogs.

**Decision needed.** Does the application declare a Light colour scheme to Qt,
leave the host appearance alone as it does today, or grow a second palette and
support dark appearance properly? The three are set out below with what each
costs; the recommendation is the first.

**The three options, as they stand.**

1. **Declare Light and keep declaring every colour.** The hint covers the
   chrome where the platform honours it; the declared colours cover everything
   that carries meaning whether or not it does. Costs a macOS reader in Dark
   appearance a light-appearing window.
2. **Declare nothing and keep declaring every colour.** Today's state after
   `PL-DHBX`. The chrome follows the host and the content does not, which is
   the mixed appearance in the `PL-DHBX` screenshots.
3. **Support dark appearance properly.** A second palette, every requirement
   re-measured against it, the six traces re-picked against dark surfaces under
   four vision models, and `docs/MODEL.md` restated for both. This is interface
   work at the scale of the `v0.5.x` interface-pass row, not a fix.

**Recommendation to put to the project owner: option 1**, with option 3 raised
as a roadmap line rather than an item. The apparatus reason is the strong one -
a contrast table measuring surfaces that are not on screen is worse than a
window that ignores the system appearance - and option 3 cannot be done
cheaply or half-way without producing exactly that.

**Put to the project owner 2026-09-17 and deferred.** The recommendation above
was given with `PL-DHBX`'s fix; the answer was to take the recommendations that
had to be decided in that session and to defer anything opening a new topic,
which this does. It stays `needs-decision` rather than being closed: the
question is unchanged and still answerable, and nothing in the interface is
waiting on it - `PL-DHBX` declared every colour that carries meaning, so this
decides the chrome.

**What this is not.** Not a question about the transport buttons, which are
fixed. Not blocked on the interface pass being scoped: the decision is
answerable now and options 1 and 2 are both one line or none.

**Done when** the project owner has chosen, the choice is recorded in
`docs/MODEL.md` § "Color contrast, and the standard this interface is held to"
with the reasoning, and - for option 1 - `app/main.py` declares the scheme and
a test holds it.

## Reopened by the project owner's own screen, 2026-09-20

**The paragraph above saying "nothing in the interface is waiting on it" was
false when it was written, and is only true again by repair.** The owner
reported the bookmark editor rendering six near-black boxes inside a white
dialog under a dark host appearance. `PL-DHBX` declared every colour that
carried meaning *in the controls that existed then*; `PL-LPLD` added six input
controls that declare none, the legend's six check-box indicators had never
declared theirs, and the three selector popups drew the host's surface. Those
are `PL-RKRY`, `PL-7W9N` and `PL-0NVN`, all fixed - so the interface is no
longer waiting on this decision, and this item is once again about the chrome.
What is different is that the sentence is now held by a test rather than by an
argument: `tests/integration/test_dark_appearance.py` walks the rendered tree
under a dark host palette and fails on any content widget resolving to it.

**Option 1 has a stronger form than the one set out above, and the difference
is measured.** The three options were framed with
`QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Light)` as the
mechanism, correctly noting that Qt documents it as a hint that "is not
supported on all platforms" - and it was observed being ignored outright on
2026-09-20: after setting it, `styleHints().colorScheme()` still reported
`Unknown` under the `offscreen` plugin. So it remains no basis for a
legibility guarantee.

`QApplication.setPalette` is not a hint. It is authoritative for every widget
at any depth, and it is the *only* mechanism that reaches a widget under a
stylesheet ancestor: a stylesheet makes everything beneath it resolve from the
**application** palette rather than from the styled widget, which is what made
three popups and a list's scroll bar unreachable from the widget that contained
them. So option 1's real form is one line in `app/main.py` applying the same
role set `qt_widgets.declare_interface_colours` already declares.

**What that would buy, and what it would cost.** It would cover the chrome this
item is about, and it would close the class structurally - a content widget
added later could not arrive undeclared, where today a test catches it after
the fact. Against that: the cost already recorded here, a light-appearing window
on a machine set to Dark, and one new one. An application palette assigned
wholesale replaces the `Disabled` colour group too, and
`.claude/rules/ui-color.md` makes a second declared disabled colour a decision
rather than a style choice. It would therefore have to be written the way
`declare_interface_colours` is - `Active` and `Inactive` groups only, leaving
`Disabled` to the platform - which is a constraint on the implementation rather
than an argument against it.

**Recommendation, unchanged in direction and firmer in mechanism: option 1, as
an application palette rather than as a colour-scheme hint.** The apparatus
reason given above is the strong one and is untouched: 24 contrast requirements,
`docs/MODEL.md` § "Color contrast, and the standard this interface is held to",
and the dichromacy floors the six traces were re-picked against are all measured
on PANEL and BACKGROUND, and an interface that renders anything else is
measuring surfaces that are not on screen.

**Done when** the project owner has chosen; the choice is recorded in
`docs/MODEL.md` § "Color contrast, and the standard this interface is held to",
whose closing paragraph now names this item as the open question; and - for
option 1 - `app/main.py` applies the palette and a test holds the chrome the
way `test_dark_appearance.py` holds the content widgets.

## Decided: option 1, as an application palette

**"Agree with krzw recs" (project owner, 2026-09-20, ratified)** - chosen over
leaving the host appearance alone (option 2, today's state) and over growing a
second palette for dark support (option 3, interface-pass scale). Ratified
rather than specified: it was this session's recommendation, given with the two
measured findings above, so ordinary evidence reopens it.

**The mechanism is `QApplication.setPalette`, not
`styleHints().setColorScheme`.** The hint was observed being ignored outright
on 2026-09-20 (`colorScheme()` still reporting `Unknown` after it was set), and
Qt documents it as unsupported on some platforms, so nothing may rest on it. An
application palette is authoritative, and it is the only thing that reaches a
widget under a stylesheet ancestor - a stylesheet makes everything beneath it
resolve from the *application* palette rather than from the styled widget.

**What to build.**

1. `declare_application_colours(application)` in `app/qt_widgets.py`, beside
   `declare_interface_colours` and sharing its `_DECLARED_ROLES`. It writes the
   `Active` and `Inactive` colour groups only, leaving `Disabled` as the
   platform supplied it, for the reason that function's docstring gives.
2. `main()` calls it immediately after the `QApplication` is constructed and
   before any widget exists, so nothing is built under the host's palette.
   **The call goes in that function rather than as a bare
   `app.setPalette(...)` in `main.py`**: `check_authored_disabled_colours_are_measured`
   admits a `setPalette` only from a function some requirement cites by name,
   and `main` is not where a colour is drawn. Cite the new function in the same
   `why` entries that already cite `declare_interface_colours`.
3. **Keep the per-widget declarations.** They are not made redundant by this:
   `tests/integration/test_dark_appearance.py` asserts that a widget's own
   declaration survives a *hostile* application palette, which is the property
   that fails if the only declaration is global - and a view is built by tests,
   and could be embedded, without `main()` ever running. The application
   palette covers the chrome and anything that declares nothing; the per-widget
   call is what a view carries with it.

**Done when** `app/main.py` applies the palette through that function;
`tests/integration/test_dark_appearance.py` holds the chrome with a vacuity
guard - a scroll bar or splitter handle resolving to the host's palette before
the call and to the theme's after - and mirrors the existing `Disabled`-group
assertion for the application; `docs/MODEL.md` § "Color contrast, and the
standard this interface is held to" records the choice and its reasoning in
place of the closing paragraph that currently calls this an open question; and
the test module's own docstring stops saying the chrome is deliberately not
asserted.

**`theme.py` needs no change**, despite being in `touches` from before this
decision: the ten roles map onto constants that already exist, and no new
colour or pair is introduced.
