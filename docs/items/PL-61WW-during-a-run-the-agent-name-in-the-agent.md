---
id: PL-61WW
title: During a run, the agent name in the agent selector loses contrast against the agent colour
status: untriaged
added: 2026-09-06
---

**Problem.** `simulation_view.py:2123` sets `self._agent_dropdown.disabled =
snapshot.is_running`, so the agent selector is disabled for the whole of a run.
Flet/Material then paints the label in the theme's disabled-content grey, which
overrides the explicit `color=` and `text_style=` set at construction
(`simulation_view.py:1082-1083`), while `bgcolor=` / `fill_color=` keep the
saturated agent fill (`simulation_view.py:1080-1081`). Grey-on-magenta is the
result: observed 2026-09-06 on isoflurane, screenshot from the project owner.
Every agent in `AGENT_COLOR_SCHEMES` (`theme.py:79`) is a saturated fill, so
this is not one agent's palette.

**Why it matters.** The moment the label goes unreadable is exactly the moment
the readouts are live and changing, and every number beside it — %, ×MAC,
alveolar and mixed-venous partial pressures — is agent-specific. `CLAUDE.md`'s
safety-critical standard requires that model identity and simulation state
"cannot be easily misread"; an agent name that is hardest to read while the
agent is running inverts that. It is also the wrong-context failure the
standard's presentation clause names: the correct number under the wrong
agent's identity is still a safety failure.

Note the conformance question is *not* the design question here. W3C WCAG
2.1/2.2 SC 1.4.3 (Contrast (Minimum)) exempts "text or images of text that are
part of an inactive user interface component" from any contrast requirement, so
a disabled control is formally exempt. The exemption is about conformance
claims, not about whether this is a defect: the control is inactive but the
information it carries is load-bearing. Whatever is displayed instead should
still meet 4.5:1, or 3:1 if it stays large-and-bold (SC 1.4.3 large-text
threshold: 18.66px bold or 24px regular).

**Where.**

- `src/anesthesia_sim/app/simulation_view.py:2123` — where the run disables it.
- `src/anesthesia_sim/app/simulation_view.py:1065-1103` — dropdown
  construction, and the sibling controls at 1091 and 1103 that take the same
  `foreground` and may have the same problem when disabled.
- `src/anesthesia_sim/app/theme.py:79` — `AGENT_COLOR_SCHEMES`, the `fill` /
  `foreground` pairs.

Worth checking in the same pass whether any *other* control disabled during a
run (the Start button at `simulation_view.py:2233` is the obvious one) is
carrying information rather than just an unavailable action.

**`make check` is green on this, and will stay green after a naive fix.**
`tools/contrast_check.py:347` already declares a requirement for "the agent
name over its ISO 5360 identification color" and it passes — because the pair
it measures is the *enabled* one, `fill` against `foreground`. The colour
actually rendered during a run is Flet/Material's disabled grey, which appears
nowhere in `theme.py`; the tool reads constants out of that file with `ast`, so
a colour the project never declares is not merely undeclared but unreachable.
That is the general shape rather than this one control's bug: every disabled
state in the interface is currently outside the checker's reach.

**Done when.** The running agent's identity is legible throughout a run at the
contrast bar above, and a test pins it. Pin it in
`tools/contrast_check.py`'s `REQUIREMENTS` rather than only in a unit test —
which means the disabled foreground has to become an explicit constant in
`theme.py` instead of a theme default, and that is a reason to prefer the fix
directions below that set the colour explicitly. Candidate directions, none chosen: keep
the label at `scheme.foreground` when disabled rather than letting the theme
grey it; drop `disabled` for a read-only presentation that does not recolour;
or move the running agent's identity out of the control into a label that is
never disabled. The third also answers the mode-awareness question — a disabled
dropdown reads as "unavailable", not as "this is what is running".
