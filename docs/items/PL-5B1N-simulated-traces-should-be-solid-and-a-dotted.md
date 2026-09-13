---
id: PL-5B1N
title: Simulated traces should be solid and a dotted trace should mean an uncommitted predicted future, but dash pattern is already spent as the six traces' colour-blind-safe channel
status: untriaged
feature: presentation-safety
added: 2026-09-12
---

**Problem.** Project owner, 2026-09-12, as intent for the chart: a *simulated*
trace — the run that has actually happened — should read as a **solid** line,
and a **dotted** line should mean a **predicted future**, shown while a control
is being changed but has not been committed. The named controls are the
vaporizer dial, fresh gas flow and cardiac output, i.e. any control that moves
the trajectory; the trigger is "slider grabbed but not released, or value typed
but not confirmed".

The intent is sound and the mechanism is not available. **Dash pattern is
already spent**, and spent deliberately, as the six compartment traces'
non-colour channel:

- `PL-GVXP` (shipped v0.4.7) measured the pairwise contrast ceiling at about
  1.48 once each of six traces must also clear 3:1 against the panel, so colour
  cannot separate them and dash pattern was made the redundant channel. Which
  style sits on which trace is derived from the colour distances, not chosen
  freely — `app/simulation_view.py:686-732` carries that derivation.
- Today only **Circuit** is solid. Alveolar is long dash, mixed venous short
  dash, vessel-rich even dash, fat dash-dot — and **muscle is literally
  `"dotted"`, `[2, 3]`**. So "solid means simulated" would flatten five traces
  into one style, and "dotted means predicted" would collide with the muscle
  compartment head-on.
- The channel is more crowded still: the 1 MAC and equilibrium reference lines
  and the control marks each carry their own dash pattern
  (`ONE_MAC_LINE_DASH_PATTERN`, `EQUILIBRIUM_LINE_DASH_PATTERN`,
  `CONTROL_MARK_DASH_PATTERN`).

**What the capture is therefore asking for.** The *distinction* the owner wants
— committed run versus uncommitted prediction, visible at a glance while the
control is under the hand — carried on a channel that is still free, rather than
on dash pattern. Candidates, in the order worth trying: reduced alpha or
lightness on a ghost line that keeps the compartment's own colour and dash
pattern intact (which preserves `PL-GVXP` outright and adds an orthogonal
channel); position, since the preview lies entirely to the right of "now" and is
already spatially separated in a way two concurrent traces are not; a tinted
band behind the forward region. Stroke width is the weakest of these — it is
partly load-bearing already, traces carry 2 px and 3 px by importance.

**Why it is a safety question and not a styling one.** A preview curve is a
third epistemic class, distinct from both halves of `CLAUDE.md`'s
modelled-versus-measured rule: it is a *conditional* prediction of an input the
learner has not committed. Three failure modes follow, and any design has to
answer all three:

1. A preview that survives the release of the slider reads as a run that
   happened. It must be bound to the interaction and disappear on commit or
   cancel, not decay or linger.
2. Equal visual weight implies equal confidence. The preview is contingent on a
   value that may never be applied; it should read as lighter than the run.
3. A screenshot taken mid-drag is ambiguous unless the preview is labelled as
   well as styled — the redundant-channel argument `PL-GVXP` made for colour
   applies again here.

**Prerequisites and dependencies.**

- **v0.5.1, the Qt port.** The chart is rewritten on pyqtgraph in that release;
  deciding this against the Flet chart is the work done twice that the port's
  own scoping argument refuses.
- The forward curve is a second integration from the current state under a
  hypothetical control value. It must use the same model and version as the run,
  must be deterministic, and must not touch the run's own state — this is a pure
  read of `core/`, and a preview computed by any other path would be a second
  source of truth for a displayed clinical value.
- Item 8 of "Planned milestones" (the recorded control-input timeline) is the
  natural home for "what the value would become"; check before building a
  parallel path.

**Related.** `PL-GVXP` (six traces separated by more than colour, shipped
v0.4.7) is the constraint. `PL-THXF` (the legend swatch is a solid bar for a
dashed trace) is open and touches the same legend this would have to extend.
