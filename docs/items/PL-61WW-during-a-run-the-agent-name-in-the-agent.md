---
id: PL-61WW
title: During a run, the agent name in the agent selector loses contrast against the agent colour
priority: P1
effort: M
status: done
classes: safety, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/theme.py, tools/contrast_check.py, tests/unit/test_simulation_view.py
added: 2026-09-06
closed: 2026-09-07
pr: 460
verify: uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_the_agent_name_stays_legible_while_the_run_disables_the_selector' tests/unit/test_simulation_view.py
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

**Triaged `safety`, P1, on the brief's own argument rather than on the WCAG
question.** The exemption for an inactive component decides a conformance claim
and not whether this is a defect: the label carries model identity, which
`CLAUDE.md` requires not be easily misread, and it is least readable exactly
while the agent-specific readouts are live. The `verify:` command names the
test the work owes rather than a fix direction, so it holds under any of the
three candidates - run 2026-09-06 before the work: exit 1, with the file's 174
tests passing and the test absent.

**It crosses the lane boundary**, reaching `src/` and `tools/contrast_check.py`
both, so neither `bin/docket next product` nor `next workflow` will offer it.
That matches its sibling `PL-W8DQ` and is what the Done-when asks for: pinning
the requirement in the checker is the half that keeps the fix from silently
regressing.

**Fixed by replacing the selector during a run, not by restyling it**
(2026-09-07). The third candidate direction, chosen over the other two on
these grounds:

- *Keep the label at `scheme.foreground` when disabled* would have depended on
  Flet/Material honouring an override of its own disabled-content colour. The
  unit test would pin the attribute this project sets, not the colour the
  widget paints, so a green test would have proved nothing about the screen -
  the exact failure mode the brief describes `make check` already having.
- *Drop `disabled` for a read-only presentation* is a behaviour change rather
  than a presentation one: it would let a selection reach `_handle_agent_change`
  mid-run, and what happens to a running case when `set_agent` rebuilds around
  it is a design question this item did not ask.
- *Move the identity into a control that is never disabled* is what landed.
  `_running_agent_display` is a static chip carrying `_running_agent_text` (the
  agent's name, bold) and `_running_agent_lock_text` ("Locked while running"),
  drawn in the agent's own `foreground` on its own `fill` and bordered like
  `_agent_header_badge` - the border being what keeps the sevoflurane chip's
  shape against a page it is 1.27:1 against. `_refresh_view` swaps it with
  `_agent_dropdown` on `is_running`; the dropdown stays `disabled` as well as
  hidden, since an off-screen control must not be operable.

**How the checker requirement was met, which is not what the Done-when
anticipated.** The Done-when expected the disabled foreground to become an
explicit constant in `app/theme.py` so `REQUIREMENTS` could reach it. Under
this direction there is no disabled foreground to declare: the pair rendered
during a run *is* `<agent>.foreground` on `<agent>.fill`, which the three agent
entries already measure. Those three entries were rewritten instead, to name
all three places the pair is drawn - `_subtitle_text`, `_agent_dropdown`,
`_running_agent_display` - and to record why the entry had stopped describing
what was on screen. `check_citations` resolves every one of those symbols, so
the coverage claim is now audited rather than asserted. Adding a constant for a
colour nothing renders would have been a worse answer to the same requirement.

**The brief's side question, answered.** No other control disabled during a run
carries information. `_start_button` is disabled while running, failed, or at
the supported run length, and `_pause_button` while not running; both name an
unavailable *action*, and neither is the only statement of the state it
reflects - `_status_text` says which of the four states the run is in, in words.

**Found and not fixed here:** `PL-K8YM` (docs/MODEL.md does not record the
chip or the never-disabled bar) and `PL-97VB` (nothing stops a future
identity-carrying control being disabled).
