---
id: PL-NGF7
title: tools/contrast_check.py can see no disabled-state colour, because none of them is a constant in theme.py
priority: P2
effort: M
status: done
classes: infra, test
feature: presentation-safety
milestone: v0.4.26
touches: tools/contrast_check.py, src/anesthesia_sim/app/theme.py, src/anesthesia_sim/app/simulation_view.py, tests/unit/test_contrast_check.py
added: 2026-09-06
closed: 2026-09-16
pr: 621
verify: uv run pytest tests/unit/test_contrast_check.py && grep -q 'def test_a_disabled_selector_is_an_error' tests/unit/test_contrast_check.py
---

> **Deferred to the Qt port, which dissolves this rather than fixing it** (project
> owner, 2026-09-10). The unreachable colours are Flet/Material's; Qt supplies
> no such theme, so the port's `theme.py` declares them and the tool can measure
> them. Clearing this first would build a mechanism to measure a half of the
> interface that is about to stop existing. The deferral is recorded in Gate 1's
> own section, as a frozen list requires. **Expected disposition: `dropped`, not
> `done`.**

**Problem.** `tools/contrast_check.py` extracts colour constants from
`src/anesthesia_sim/app/theme.py` with `ast`, deliberately, so it runs in a
bare checkout. Every colour a control takes when Flet/Material disables it
comes from the Material theme rather than from `theme.py`, so it is not merely
undeclared in `REQUIREMENTS` — it is unreachable to the tool that would measure
it. `make check` is therefore green on the whole disabled half of the
interface, and will stay green however that half renders.

**Why it matters.** The tool's docstring is honest about its own scope: it
decides "whether a declared requirement meets its declared ratio", and lists
"which pairs actually appear on screen together" among what it must never
decide. So this is a coverage gap in what a person declared, not an arithmetic
defect. But the practical reading of a green contrast check is that the
interface's colour pairs are covered, and one whole rendering state is not —
the state the app spends most of its time in, since a run disables controls.
`PL-61WW` (agent name loses contrast against the agent colour during a run) is
the instance that surfaced it; that one control is fixable without closing this.

**Where.**

- `tools/contrast_check.py` — the `ast` extraction, and `REQUIREMENTS`.
- `src/anesthesia_sim/app/theme.py` — where a disabled foreground would have to
  become an explicit constant for any of it to be measurable.
- `src/anesthesia_sim/app/simulation_view.py` — the `disabled=` assignments;
  `2123` (agent dropdown) and `2233` (Start) are the two known.

**Done when.** Either every control disabled during normal operation takes an
explicit foreground from `theme.py` with a declared requirement measuring it,
or the tool states in its docstring that disabled states are out of scope and
says what covers them instead. The second is a legitimate answer — but it has
to be a decision somebody took, not the current situation, which is that
nothing covers them and nothing says so.

**Decision needed.** Does every control disabled during normal operation take
an explicit foreground from `theme.py` with a declared requirement measuring
it, or does `tools/contrast_check.py` state in its docstring that disabled
states are out of scope and name what covers them instead? The second is a
legitimate answer and the item is explicit that it has to be a decision
somebody took: today nothing covers them and nothing says so.

**Classed `infra, test` rather than `defect`, and it can be overruled.** The
tool's docstring already disclaims deciding which pairs appear on screen
together, so nothing it asserts is false - what is missing is coverage a reader
of a green check assumes. `PL-61WW` is the instance and is fixable without
closing this.

## Measured 2026-09-16: the port does not dissolve this, and the deferral's premise is false

**The blockquote above says "Qt supplies no such theme, so the port's
`theme.py` declares them and the tool can measure them". Measured against the
finished port, both halves are wrong.** `PL-25KS` completed the port, so this
is now a fact about the shipped tree rather than a prediction.

**Qt supplies exactly such a theme.** `QPalette` carries a `Disabled` colour
group that the platform style fills in, and the style resolved in this
container (Fusion) gives every disabled text role `#BEBEBE`:

| group | WindowText | ButtonText | Text | Button | Base |
| --- | --- | --- | --- | --- | --- |
| `Active` | `#000000` | `#000000` | `#000000` | `#EFEFEF` | `#FFFFFF` |
| `Disabled` | `#BEBEBE` | `#BEBEBE` | `#BEBEBE` | `#EFEFEF` | `#EFEFEF` |

Read off `QApplication.palette()` and confirmed per widget on a disabled
`QPushButton`, `QComboBox` and `QLabel`, all three of which resolve
`#BEBEBE`. `#BEBEBE` appears nowhere in `src/anesthesia_sim/app/theme.py`, so
it is unreachable to `tools/contrast_check.py`'s `ast` extraction in exactly
the way Flet/Material's disabled grey was. The toolkit changed; the gap did
not.

**And `theme.py` declares nothing of the kind.** Grepped across
`src/anesthesia_sim/app/`: no `QPalette` construction, no `setPalette`, and no
`:disabled` selector in any of the 27 `setStyleSheet` call sites. Nothing in
the shipped tree declares a disabled colour at all.

**It is worse than undeclared - it is platform-dependent.** `app/main.py`
constructs `QApplication(sys.argv[:1])` and never calls `setStyle`, so the
style is whatever the platform supplies: Fusion here, the native style on the
project owner's machine. `#BEBEBE` is this container's number, not the
product's. So the disabled half of the interface renders a colour that is
undeclared, unmeasured *and* different on the machine a learner uses, which is
a reproducibility gap as well as a coverage one.

**Five controls are disabled during normal operation**, so this is not
hypothetical: `qt_widgets.py:793` (the splitter handle, disabled by design),
`run_view.py:577` (the agent dropdown), and `run_view.py:580-582` (start,
pause, reset).

**What this changes.** The deferral stands on its own second ground - clearing
this before the port would have measured a half of the interface about to stop
existing - but its *expected disposition* does not. This is not `dropped`: the
port did not dissolve it, and the same decision the item already names is still
owed.

**The safety-critical half is already covered, by a check rather than by this
item.** ISO 5360 Table 2 footnote b makes displaying an agent colour an
obligation to display the *right* one, so an agent-identity control rendered in
an undeclared grey would be a safety defect rather than a coverage gap - which
is what `PL-61WW` was. It cannot happen: `run_view.py:577-578` writes
`setDisabled(lock.selector_locked)` beside `setHidden(lock.selector_locked)`
with the same operand, so the selector draws nothing while it cannot be used,
and `tools/agent_identity_check.py` holds the identity set to that pairing
rather than trusting it. Its line on `make check` reads *"4 disabled-state
write(s) ... 1 of them on identity controls and each paired with its hide; none
rendered disabled"*. So `theme.py`'s claim that the `PL-61WW` fix was
structural is true, by hiding rather than by not disabling.

**What is left is therefore the ordinary half, and it is narrower than this
item was written against.** The controls that do render disabled are the
splitter handle and the start, pause and reset buttons - plain controls
carrying no identity, no value and no clinical meaning, whose labels are the
only thing at stake. That is squarely inside the WCAG exemption below. The gap
is real and the reproducibility point stands; the thing that would have made it
urgent does not apply.

**One standards fact that bears on which answer to take.** WCAG 2.2 exempts
disabled controls from both contrast criteria - SC 1.4.3 excludes text that is
"part of an inactive user interface component", and SC 1.4.11 applies "except
for inactive components or where the appearance of the component is determined
by the user agent and not modified by the author". So the item's second
acceptable answer - the tool states that disabled states are out of scope and
says what covers them instead - is not a concession but the standards-aligned
reading, and it can cite the exception rather than merely assert a scope. That
does not make it automatically right here: the exemption is about conformance,
and an agent-identity control is an obligation this project took on from ISO
5360 rather than from WCAG. Verify both citations at
https://www.w3.org/TR/WCAG22/#contrast-minimum and
https://www.w3.org/TR/WCAG22/#non-text-contrast before the decision is written
down.

## Closed 2026-09-16: the second answer, taken as a decision and then made self-enforcing

**The project owner chose the second of the two answers this item names** -
`tools/contrast_check.py` states that disabled states are out of scope and says
what covers them instead - over the first, declaring an explicit foreground for
every disabled control. Not `dropped`: the measurement above showed the port
did not dissolve this, so a decision was still owed, and this is it.

**Why the second answer rather than the first.** Declaring a foreground for
every disabled control would mean choosing a value the product does not
currently choose, purely so a tool could measure it. That is a real cost in the
wrong place: `#BEBEBE` is Fusion's, the native style's number differs, and
overriding it would make this project responsible for looking right on every
platform's disabled controls in exchange for measuring something no clinician
reads. The first answer buys coverage of a surface with no clinical content.

**What the docstring now says**, in three parts, so that the next reader gets
the decision rather than an absence:

- **The measurement.** `QPalette`'s `Disabled` group is filled in by the
  platform style - `#BEBEBE` for every disabled text role under Fusion,
  confirmed per widget - and `app/main.py` never calls `setStyle`, so the value
  is the platform's rather than the product's. There is nothing for an `ast`
  extraction to reach.
- **What covers them.** The safety-relevant half is
  `tools/agent_identity_check.py`: no control carrying agent identity may be
  *rendered* disabled, enforced as the `setDisabled`/`setHidden` pairing. What
  is left is the splitter handle and the start, pause and reset buttons, and
  W3C WCAG 2.2 SC 1.4.3 exempts "text ... that is part of an inactive user
  interface component" from any contrast requirement.
- **What is not claimed.** SC 1.4.11's own exception wording was **not** read at
  the source: `w3.org` returns `EGRESS_BLOCKED` here, as `PL-JX0Z` recorded
  across five routes, so nothing rests on it. The argument stands on SC 1.4.3,
  which this repository already quotes verbatim in
  `tools/agent_identity_check.py`, and on the measurement above.

**And the scope note cannot rot, which is the half that makes this more than a
comment.** This item exists because *"nothing covers them and nothing says so"*
- so an answer that was only prose would be the same shape one layer up: a
sentence asserting a premise, with nothing checking the premise still holds.
`check_disabled_states_are_the_style_s` fails the build the moment a
`:disabled` rule or a `setPalette` call appears under `app/`, because at that
moment the colour is author-chosen, measurable, and covered by nothing. The
error says to declare it in the theme and add a requirement, never to delete
the check. Three tests pin it: the `:disabled` form fires, the `setPalette`
form fires, and an ordinary enabled-state stylesheet does not - the last so
that a check firing on everything cannot pass the first two.

**A hard error rather than an advisory**, on `CLAUDE.md`'s rule that hard
failure is for exact rules: either a module under `app/` writes one of those
two forms or it does not, and the violation is exactly the event that voids the
scope decision.
