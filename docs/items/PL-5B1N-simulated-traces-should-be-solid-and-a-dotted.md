---
id: PL-5B1N
title: Simulated traces should be solid and a dotted trace should mean an uncommitted predicted future, but dash pattern is already spent as the six traces' colour-blind-safe channel
priority: P2
effort: M
status: blocked
classes: feature
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py, src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/chart_time_base.py, src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/theme.py, tools/contrast_check.py, docs/MODEL.md, tests/integration/test_qt_chart.py, tests/integration/test_qt_widgets.py, tests/unit/test_chart_frame.py, tests/unit/test_chart_time_base.py, tests/unit/test_theme.py, tests/unit/test_contrast_check.py
blocked-by: v0.7.0
added: 2026-09-12
verify: grep -qF 'PREVIEW_REGION' src/anesthesia_sim/app/theme.py && grep -qF 'preview' tests/integration/test_qt_chart.py
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
  freely — `app/chart_frame.py`'s `trace_style` carries that derivation.
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

**Why it matters.** It is a safety question rather than a styling one. A preview curve is a
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

- **The Qt port.** The chart is rewritten on pyqtgraph in that release;
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

**Triaged 2026-09-13.** `P2`, `M`, `feature`, `needs-decision`.

**`needs-decision` rather than blocked on the port's version, which was tried and is wrong.**
The brief's prerequisite is real - answering the channel question against the Flet
chart is the work done twice, since the port rewrites the chart on pyqtgraph and
redecides dash patterns, alpha and stroke widths with it. But `blocked-by:
<version>` holds only until that version is *scoped*, and the port was scoped
2026-09-10, so `docket check` promotes the item straight back out - it says so
outright. The carve-out is for a milestone nobody has scoped yet, which is
`PL-B9PY`'s case and not this one.

So the sequencing lives in the brief, where a session picking the item up reads it,
rather than in a status that cannot carry it. The question is genuinely open and
genuinely answerable, which is what `needs-decision` is for.

**Classed `feature`, not `safety`, deliberately.** The brief is right that the
design is a safety question - a preview is a third epistemic class beside modelled
and measured, and its three failure modes are real. But nothing misleads a reader
today, because no preview is drawn: the safety obligation binds whoever *builds*
it, which is what the brief already records. Classing it `safety` would pin it
`P1` and make it debt by `docket.toml`'s `debt_classes`, so a gate would hold a
release open for a feature that cannot be built until the port lands - debt and
blocked at once, which is the contradiction `blocked-by` exists to avoid.

**What the port should carry forward regardless.** Whoever ports the chart should
leave the non-colour channel documented as *spent* - `PL-GVXP`'s derivation is
load-bearing and the port is where it would most easily be lost - so that this
item's candidate list still holds when it unblocks.

**Decision needed.** Which still-free channel carries committed-run versus
uncommitted preview, given that dash pattern is spent as the six traces'
colour-blind-safe redundant channel (`PL-GVXP`, shipped v0.4.7) and that the
owner's named mechanism - solid for simulated, dotted for predicted - collides
with it head-on: muscle is literally `"dotted"`. The brief ranks the candidates
(ghost line at reduced alpha or lightness keeping colour and dash intact;
position, since the preview lies wholly right of "now"; a tinted forward band) and
argues stroke width is weakest, being partly load-bearing already. Answer it
against the ported pyqtgraph chart rather than the Flet one, and answer all three
failure modes the brief names, since a preview is a third epistemic class beside
modelled and measured.

**Answered 2026-09-27.** Position, region and label carry the distinction: a
*now* edge at the run's reach, a tinted forward region to the axis's right
edge, an in-plot label naming the control and the unapplied value, and the
preview traces in each compartment's own colour and dash pattern one width
step thinner (project owner, 2026-09-27, ratified, over an alpha ghost, which
fails the 3:1 floor at every opacity under 0.85, over solid for the run and
dotted for the preview, which collides with the muscle trace, and over a
legend-only marker). With it, as put and agreed: during a preview the window
keeps its span and re-anchors so the reach sits at the plot's midpoint; a
pointer drag applies on release, keyboard steps stay immediate, and a typed
entry previews on each parse and commits on Enter; both plots draw it, per run
in compare mode, and it never answers a hover; and the build is deferred to
Gate 3 (project owner, 2026-09-27, ratified, over building it now as the next
item of the presentation-safety chain), which `PL-YBFB` records in
`ROADMAP.md`'s gate section. Q1 to Q5 under "Design round 2026-09-27:
recommendations" below carry the reasoning. Status `ready`; `touches` widened
as that section's "For the build" lists.

**Moved to `blocked` on 2026-10-03, with `blocked-by: v0.7.0`, when `PL-YBFB`
wrote the deferral above into `ROADMAP.md`'s v0.6.0 gate section.** The design
is unchanged and still decided; what moved is how the store holds the Gate 3
deferral. `bin/docket wave` counts a gate entry apart from the work the gate
can clear only where the entry's `blocked-by` leaves the frozen list, and it
reads no group heading (`PL-18BD`), so at `ready` this entry went on counting
as Gate 2 work. Naming the milestone while the status still said `ready` would
say the work both can and cannot start, and `blocked` also stops `bin/docket
next` offering a build the owner chose not to start now. `v0.7.0` is the
milestone Gate 3 clears before, as it was for `PL-Y04W`'s Gate 3 deferral. A
milestone blocker clears when its milestone is scoped, so `bin/docket check`
names this item ready to promote once v0.7.0 is scoped. A build the owner picks
sooner sets the status back to `ready` and drops the edge first.

**Done when.** A learner changing the vaporizer dial, fresh gas flow or
cardiac output without committing sees the resulting trajectory drawn from the
run's reach forward, inside a tinted region the run never enters, one width
step thinner than the run, in each compartment's own colour and dash pattern,
with an in-plot label naming the control and the unapplied value; the preview
is bound to the interaction - created on press, gone on release or cancel -
and the run keeps its setting until release; it is computed by a second
`RunDefinition` opened at the run's reach, a pure deterministic read of
`core/` at the run's own model and version, touching none of the run's state;
both plots draw it and the hover never answers from it. `PL-GVXP`'s derivation
still holds afterwards, and the tests beside each touched module cover the
preview appearing, disappearing on both exits, coinciding with the run at the
run's own setting, and never being drawn outside its region, at the run's
width, or without its label.

[superseded 2026-09-27: the channel clause and the last clause changed with
the decision above, which keeps each compartment's dash pattern inside the
preview deliberately; the current done-when precedes this] **Done when.** A
learner changing the vaporizer dial, fresh gas flow or cardiac output without
committing sees the resulting trajectory on a channel that does not compete
with the six compartments' dash patterns; the preview is bound to the
interaction and gone on commit or cancel; it reads as lighter than the run and
is labelled as well as styled, so a screenshot taken mid-drag is not
ambiguous; and it is computed by a pure deterministic read of `core/` at the
run's own model and version, touching none of the run's state. `PL-GVXP`'s
derivation still holds afterwards, and the interface's tests - since the Qt
port, `tests/unit/test_chart_frame.py` and `tests/unit/test_dashboard_frame.py` -
cover the preview appearing, disappearing on both exits, and never being
drawn in a style a compartment uses.

## Design round 2026-09-27: recommendations

Recommendations, not decisions: the thread that records the project owner's
answer marks each `(project owner, DATE, ratified)` or replaces it. Answered
against the pyqtgraph chart, as the brief requires, at tree `aeb00392`.

**What is fixed and what is open.** The owner specified the *distinction*
(2026-09-12): the run that happened reads as the run, and the trajectory a
control would give while it is grabbed and not released reads as a
prediction, gone at release. Open is the channel, because dash is spent
(`PL-GVXP`), and what follows from taking the specification at its word.

**Read on 2026-09-27.**

- The axis is a fixed-width viewport: `following_window` keeps
  `CHART_LIVE_HEADROOM_FRACTION` = 2% of the span empty right of the newest
  sample (36 s of a thirty-minute base), and `fitted_window` gives the rung's
  full width with the run at the left. There is no room for a preview by
  default, and the span may not change (`PL-012`: the slope is the encoding).
- `RunDefinition` refuses to evaluate past `reached_s` - *"that would be a
  prediction rather than the run"* - so a preview cannot be the run's own
  definition asked further ahead. It is a second definition opened at the
  run's reach: `RunDefinition(hypothetical_settings, run.state_at(reached_s),
  opened_at_s=reached_s)`, then `advance_to(horizon)` and `evaluate(...)`.
  Same settings type, same governing equations, the canonical state, nothing
  of the run's touched, deterministic. That is the one path; a preview
  computed any other way is a second source of truth for a displayed value.
- A drag applies live today: `ParameterSlider.valueChanged` reaches
  `_on_slider_moved`, which emits `value_changed`, which reaches the
  controller's setter on every move, grouped as one adjustment by
  `begin_control_adjustment` on press. No slider has a typed entry; the
  `QLineEdit` and `QDoubleSpinBox` in `qt_widgets.py` are the bookmark dialog's.
- In compare mode a control applies to every drawn run
  (`_apply_to_every_run`), each capped at two compartments
  (`COMPARED_COMPARTMENT_CAP`), with run identity on width (2 px and 3 px).
- The hover answers running or paused, over drawn points only.
- Alpha cannot carry "lighter" without breaking the floor. Blended over
  `PANEL` (Qt composites in sRGB), the traces' ratios fall to: at 0.85,
  circuit 4.39, alveolar 2.93, mixed venous 4.34, vessel-rich 4.04, muscle
  2.83, fat 3.56; at 0.75, 3.57 / 2.57 / 3.61 / 3.49 / 2.49 / 2.96. Two traces
  are under SC 1.4.11's 3:1 at 0.85 and four at 0.75, so a ghost line is
  either not lighter or not conformant.

**Q1. The channel.** **Recommendation: position, region and label carry the
distinction; the traces keep their colour and dash pattern and lose one width
step.** Concretely: (i) a *now* edge at the run's reach - the left edge of a
`LinearRegionItem` running from the reach to the axis's right edge, stroked in
`MUTED` as the reference lines are, with a light fill (a `PREVIEW_REGION`
colour and fill opacity in `theme.py` in the class of
`MAC_AWAKE_BAND_FILL_OPACITY`, the fill recorded exempt on `PL-HKTB`'s ground:
the edge and the label carry the information); (ii) the preview traces in
each compartment's own colour and dash pattern, so `PL-GVXP`'s separation
holds inside the preview exactly as outside it, at the run's width less one
pixel (3 to 2, 2 to 1), which keeps the compare-mode width order between two
runs' previews; (iii) a label inside the region, `INK` on a `PANEL` box as the
hover readout is drawn, naming the control and the uncommitted value in the
slider's own words - the setting's `name` and `value_text` - and saying it is
not applied. That answers the three failure modes: *bound*, because region,
label and traces are created in the `sliderPressed` slot and destroyed in the
`sliderReleased` slot that applies the value, nothing decays; *lighter*,
because the preview is thinner and sits inside a tinted region the run never
enters; *labelled*, because the label is in the plot, so a screenshot carries
it. No legend row: a row that appears and vanishes is the stale-state hazard
`TraceLegend` was built to remove. *Refused:* an alpha ghost (the floor,
above); solid for the run and dotted for the preview (collides with muscle and
flattens five traces into one style - the brief's own finding); a legend-only
marker (a screenshot cropped to the plot loses it).

**Q2. The horizon and the axis.** **Recommendation: during a preview the
window keeps its span and re-anchors so that the reach sits at the plot's
midpoint** - half the chosen base of run, half of preview (fifteen minutes at
the thirty-minute base, six hours at twelve), clamped at zero early in a run.
The span is unchanged, so the slope encoding survives; the window already
slides continuously while following, and this is a slide of half a span at
press and back at release, in the same slots that draw and clear the preview.
*Refused:* extending the axis (the rescale `PL-012` rejected); a fixed horizon
constant (a number to justify, and it either does not fit the base or forces
the rescale); drawing only into the 2% headroom (36 s is not a preview).

**Q3. What a drag does to the run - the consequence of the specification.**
Today the run follows the slider live. "Grabbed but not released" being
uncommitted means the run keeps its setting until release, and one change is
recorded at release, landing on the tick boundary as `PL-NBWP` states.
**Recommendation: take it as specified.** Pointer drags apply on release;
keyboard steps on a focused slider stay immediate, since a key press is a
discrete committed input, which is how `begin_control_adjustment`'s docstring
already reads it, and draw no preview; a typed entry, when one exists,
previews on each parse, commits on Enter and cancels on Escape. The control
timeline gets simpler - one entry per drag - and the adjustment grouping
stays for keyboard runs. This is learner-visible and the owner's: while
dragging, the run on screen no longer moves with the hand; the preview does.

**Q4. Scope of the drawing.** Both plots: the wash-in ratio is derived from
the same frame, and a lower plot that ignored the preview would show two
futures. Per run in compare mode, each from its own reach under the setting
`_apply_to_every_run` would give it. The preview never answers a hover.
While the run plays, the preview is recomputed each render frame from the
current reach - one more `evaluate` per run per frame, against a frame cost
measured at 5.5-8.6 ms median today (`PL-SQJ1`, 2026-09-27). One test the
design implies: a preview at the run's *current* setting coincides with what
the run then draws, so releasing where you started leaves nothing to
reconcile.

**Q5. Where the build sits.** Deciding this clears nothing by itself: the gate
counts an entry cleared at `done` or `dropped`, and this is `feature`-classed,
so once decided it is debt no longer but still open on the frozen list. Three
dispositions: build now, inside Gate 2 and in front of v0.6.0's
implementation; defer the build to Gate 3 the way `PL-DB64` moved five
entries; drop (no: the owner specified it). **Recommendation: record the
design here, set `ready`, and defer the build to Gate 3.** It is feature work
rather than debt, the chart it draws on is the pyqtgraph one v0.6.0 wraps in
an Area rather than rewrites, so nothing is done twice either way, and an M
feature in front of the layout milestone is a scheduling choice that is the
owner's. *Alternative:* build it now, as the next item of the
presentation-safety chain.

**For the build.** `touches` grows to `src/anesthesia_sim/app/qt_chart.py`,
`chart_frame.py`, `chart_time_base.py`, `qt_widgets.py`, `run_view.py`,
`theme.py`, `tools/contrast_check.py`, `docs/MODEL.md` (a section naming the
preview as a third epistemic class beside modelled and measured, and what
drawing one may imply) and the tests beside each. The done-when's last clause
changes: the preview *does* use each compartment's style, deliberately, and is
never drawn outside its region, at the run's width, or without its label.
