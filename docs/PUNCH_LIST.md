# Punch list

The prioritized queue of discrete, actionable development tasks for this
repository. It exists so that work identified in one session is never lost
when that session ends, and so that a fresh session can pick the right next
task and start it cold without re-deriving the problem.

## How this file relates to the other planning files

Three files, three jobs. Keeping them separate is what keeps each one cheap
to read:

| File | Holds | Churn |
| --- | --- | --- |
| `ROADMAP.md` | The authoritative version and milestone map: which release comes next and what it must contain. | Low |
| `docs/PUNCH_LIST.md` (this file) | The prioritized work queue: every defect, fix, cleanup, optimization, and small feature identified in any session. | High |
| `docs/WORKING_NOTES.md` | Long-form narrative for open threads: diagnoses, options considered and rejected, decision rationale, aspirational direction. | Medium |

Rule of thumb:

- A **release** belongs in `ROADMAP.md`.
- A **task** belongs here.
- **Reasoning too long to fit in a task entry** belongs in
  `docs/WORKING_NOTES.md`, and the task entry here links to it rather than
  duplicating it.

An item large enough to need its own goal, required scope, definition of
done, and out-of-scope list is not a punch-list item: it is a milestone.
Promote it into `ROADMAP.md` and leave a one-line pointer here.

## Capture rule

Any time any session identifies a defect, risk, cleanup, optimization,
inconsistency, or feature idea that is **not** being fixed in that same
session, add an entry here before the session ends. This applies to
findings the project owner raises and to findings a session makes on its
own. Nothing that matters may live only in a conversation.

Adding an entry is cheap and reversible; losing a finding is not. When in
doubt, capture it at `P3` rather than dropping it.

## Entry format

Each entry carries a stable ID and a single metadata line, then a short
brief written for a reader with no memory of the originating conversation.
State facts and decisions, not "the user said" or "we discussed."

```text
### PL-000 Short imperative title
`P1` · `M` · `perf` · ready · added YYYY-MM-DD

**Problem.** What is wrong or missing, concretely.
**Why it matters.** Consequence if left undone. Name the safety or
scientific-correctness implication explicitly when there is one.
**Where.** The files or modules involved.
**First step.** The specific action that starts the work.
**Done when.** The observable condition that closes the item.
**Context.** Optional pointer to the long-form thread, if one exists.
```

Keep an entry to roughly twenty lines. If it needs more, the excess is
narrative and belongs in `docs/WORKING_NOTES.md`.

**IDs** are allocated sequentially and never reused, including for
completed items. The next free ID is one past the highest that appears
anywhere in this file, archive included.

### Priority

| | Meaning | Handling |
| --- | --- | --- |
| `P0` | Safety, correctness, or a broken gate: a displayed value that could mislead, a failing build/test/type check on `main`, or a blocker for in-flight work. | Fix now, ahead of feature work. Own branch, patch version bump. |
| `P1` | Needed before the next milestone can be called done, or a real defect that is not user-misleading. | Next in line. |
| `P2` | Genuine improvement with no deadline pressure. | Queued. |
| `P3` | Worth keeping, not worth doing soon; includes ideas that need scoping before they can even be estimated. | Icebox. |

Anything touching a safety-critical path per `CLAUDE.md` ("Safety-critical
clinical-output standard") starts at `P0` or `P1`. It does not sit in `P2`
because it is small.

### Effort

Sized in units of working session, so a task can be matched to the time and
usage actually available:

- `S` — a small, focused change. Fits comfortably in leftover session time.
- `M` — one focused session, including tests and the quality suite.
- `L` — multi-session, or needs to be scoped into a `ROADMAP.md` milestone
  before implementation starts.

### Status

- `ready` — someone can start from this entry cold.
- `needs-decision` — a design or scoping question must be answered first.
  The question is stated in the entry; answering it is the first step.
- `blocked` — waiting on another item, named in the entry.

### Class

`safety`, `science`, `defect`, `perf`, `ux`, `a11y`, `docs`, `refactor`,
`infra`, `feature`, `planning`.

## Grooming

Reprioritize when new items arrive rather than only appending: a new `P0`
may demote what was previously next, and a resolved blocker may promote a
`blocked` item to `ready`. Move completed items to "Recently completed"
with their commit reference; delete the corresponding `WORKING_NOTES.md`
thread rather than leaving it stale.

### What is checked automatically

`tools/punch_list.py` handles the mechanical half. Run it with `make
punch-list`; `make check` and CI run it too, and a `SessionStart` hook emits
a short digest of the queue at the start of every session. The digest also
names which model an item warrants (`Entry.model_guidance`), deriving it
from the entry's own class tags and status rather than leaving a session to
recall the rule in `CLAUDE.md`. It reports two kinds of finding, and the
split is the point:

- **Errors** mean this file is wrong: a reused id, an entry filed under a
  band its metadata contradicts, a missing brief field, an item marked
  `blocked` that names no blocker, a `safety` or `science` item parked below
  `P1`, a `PL-` reference pointing at nothing. These fail the build, because
  each one silently loses information.
- **Advisories** mean a judgment is due: a brief that has grown into
  narrative, an item still blocked by something that has landed, an item
  that has sat at `P1` for months, a queue with nothing short and ready in
  it for a session with time to spare. These never fail a build. They are
  the reminder that a grooming pass is worth doing.

What the tool deliberately does not do is decide anything. Whether the top
`P1` is still the right next thing, whether an entry should be split, and
whether a priority still reflects reality are judgment calls about this
project; automating them would produce confident nonsense. The tool detects
the conditions, and a session makes the call.

---

## P1 — Next

### PL-021 Reject unknown keys in the parameter-file schemas
`P1` · `S` · `safety` `defect` · ready · added 2026-08-24

**Problem.** No Pydantic model in `core/parameters.py` sets
`extra="forbid"`, so an unknown key in `data/agents/*.json` or
`data/patients/*.json` is silently discarded — at the top level and inside
the nested payloads alike. Verified: adding
`blood_gas_partitition_coefficient: 9.9` alongside the correctly spelled key
loads clean and the model runs at 0.65, and `"muscel"` inside
`tissue_gas_partition_coefficients` is accepted and ignored. A misspelling
that *removes* a required key is already caught as a missing field, so the
exposure is specifically the key an author believes takes effect and does
not: a renamed field, a units-suffixed variant, a typo'd duplicate, or a
field from a schema version the loader does not implement.
**Why it matters.** Safety-critical: every value in these files feeds a
displayed clinical number, so a silently ignored edit leaves the data file
documenting one model while the app runs another. Reported as `P1-4` by the
review harness.
**Where.** `core/parameters.py` (all six `_...Payload` models),
`tests/unit/test_parameters.py`.
**First step.** Add `model_config = ConfigDict(extra="forbid")` to every
payload model; a shared private base is what keeps it from being forgotten
on the seventh.
**Done when.** An unknown key at any nesting level raises, a regression test
covers both the top-level and the nested case, and the harness's `P1-4`
check reports FIXED.

### PL-026 Decide what the interface shows after a halted step
`P1` · `S` · `safety` `ux` · needs-decision · added 2026-08-24

**Problem.** PL-018 made a failed step halt the run, label it "Stopped —
simulation error", and warn that "the values shown may not reflect a
completed step". The compartment metrics and chart traces themselves are
still drawn, at whatever value the abandoned step left them. The step is
not transactional: `RespiratorySystem.advance()` applies its five
sub-exchanges in sequence and a guard can reject the fifth after the first
four have already mutated state.
**Why it matters.** `CLAUDE.md` prefers an obvious failure state to a
plausible-looking number when correctness cannot be established, and a
partially applied step is exactly that case. The banner is a warning after
the fact rather than an interface that prevents the misreading. Against
that: the numbers are also the most direct evidence of where the model
broke down, which has teaching value, and the run cannot be resumed from
them.
**Where.** `app/simulation_view.py` (`_refresh_view`, `_refresh_notice`),
`core/respiratory_system.py` (`advance`, `_advance_step`).
**Decision needed.** Three options, in increasing cost: keep the banner as
the only cue; blank or grey the metrics and freeze the chart at the last
completed step; or make the step transactional so a failure leaves the last
completed state intact and nothing is partial. The third removes the
question entirely but means capturing and restoring six compartments plus
the accounting validator on every step.
**Done when.** What a halted run displays is a recorded decision with its
reasoning, and `docs/MODEL.md`'s interface rules state it.

### PL-023 Gate the coupled dynamics on an independent solution, not just mass balance
`P1` · `M` · `science` `infra` · ready · added 2026-08-24

**Problem.** `core/agent_simulation_validation.py` is the only automatic
correctness gate on the coupled step, and it cannot detect a wrong rate:
every internal transfer is applied as an equal-and-opposite pair, so the
residual sits at ~2e-15 L while the dynamics are visibly wrong — Δt = 10 s
differs from Δt = 0.1 s by 0.157 percentage points of alveolar fraction.
Conservation is necessary and nowhere near sufficient.
**Why it matters.** Any future change to the operator split can shift the
solution materially with every gate still green, and the next milestone's
machine abstraction touches that split. Reported as `P2-1`.
**Where.** `tests/reference/`, `tools/review-verification/verify_physics.py`,
`core/simulation.py`.
**First step.** Promote `verify_physics.py`'s from-scratch RK4 oracle into
`tests/reference/` with pinned vectors. It must keep importing only the
parameter loaders and never a solver from `core/`, or the test becomes a
tautology rather than a verification.
**Done when.** CI checks the coupled six-state solution against an
independent integration, and the tolerance is justified against the measured
first-order splitting error rather than fitted to today's numbers.
**Context.** `docs/WORKING_NOTES.md` § "Open thread: the architecture review
harness".

### PL-003 Scope the next milestone in ROADMAP.md
`P1` · `M` · `planning` · ready · added 2026-08-23

**Problem.** No milestone after v0.2.0 is scoped (v0.2.1 is a validation
hotfix on that baseline, not a milestone). `ROADMAP.md`'s
development rules require a goal, required scope, definition of done, and
an explicit out-of-scope list before implementation begins, and the next
candidate is the modular anesthesia-machine abstraction with normal
single-halogenated-agent interlock behavior.
**Why it matters.** This is the gate on all feature work: items 2-5 of the
planned-milestone list all build on it, and nothing in that direction can
start until it exists. It is also the answer to "are we in a good spot to
move on to the next roadmap feature?"
**Where.** `ROADMAP.md` ("Next milestone" and "Planned milestones").
**First step.** Draft the goal and the out-of-scope list first; the
out-of-scope list is what keeps the milestone narrow.
**Done when.** `ROADMAP.md` carries a fully specified milestone with a
version number assigned, matching the structure of the completed v0.1.0 and
v0.2.0 sections.

## P2 — Queued

### PL-024 Document what the venous pool does to early mixed-venous readings
`P2` · `S` · `docs` `ux` · ready · added 2026-08-24

**Problem.** The venous pool's mixing time constant — 60 · V/Q̇ = 12 s at the
reference 1.0 L and 5 L/min — dominates the displayed mixed-venous value
through the first minute of wash-in. Against a near-instant-mixing
comparison it reads 55% low at 30 s, 34% low at 60 s, and 17% low at 120 s.
Mixed venous is displayed both as a metric and as a chart trace, and neither
`docs/MODEL.md`'s "Known limitations" nor the interface says the early curve
is a mixing artifact rather than tissue uptake.
**Why it matters.** Not a defect: 1.0 L is the Gas Man reference value and
is cited twice in `reference_adult.json`. But a learner reading the first
minute of that trace as uptake draws a wrong conclusion from a correct
number, which is the presentation half of the safety standard rather than a
numerical error. Reported as `P2-4`.
**Where.** `docs/MODEL.md` ("Known limitations", "Venous blood"),
`app/simulation_view.py` (the mixed-venous metric and trace).
**First step.** Write the `docs/MODEL.md` note — it is the smaller half and
needs no interface decision. Whether the display also needs a cue is the
open question, and it can be answered after.
**Done when.** `docs/MODEL.md` states the pool's time constant and its
effect on the first minute, and any interface cue is a deliberate decision
rather than an omission.

### PL-025 Assign a release number to the post-v0.2.1 work
`P2` · `S` · `planning` · needs-decision · added 2026-08-24

**Problem.** `pyproject.toml` still reads `0.2.1` and the interface header
still renders "Version 0.2.1", but the code has moved since: PL-018 added a
third run state, a `failure_reason` field on `SimulationSnapshot`, and a
changed exception contract across `core/`. `ROADMAP.md`'s version table has
no row for any of it. Nothing in `ROADMAP.md` is false today — its v0.2.1
description still describes v0.2.1 — but the displayed version no longer
identifies the behavior a reader is looking at.
**Why it matters.** The version is displayed next to clinical values and is
the handle a reader has for "which model and which interface produced
this", so it is provenance rather than bookkeeping. Low urgency only
because the drift is between an untagged working tree and its last
described release, which is normal mid-development.
**Where.** `pyproject.toml` (`version`), `ROADMAP.md` (version table,
"Current baseline").
**Decision needed.** Whether the remaining harness fixes (PL-021, PL-023)
fold into one release with PL-018 and PL-022 or each gets its own patch
number. Folding argues for cutting the number once they land; separating
argues for bumping now. The roadmap's rule is that a number is chosen for
the capability boundary it crosses, which is a project-owner call.
**Done when.** The version in `pyproject.toml` and the `ROADMAP.md` table
agree with each other and with what the code does.

### PL-027 Confirm the per-frame slider write-back on a live Flet client
`P2` · `S` · `ux` · ready · added 2026-08-24

**Problem.** PL-018 made `_refresh_view` write every parameter slider's
`value` from the snapshot, so a refused setting cannot leave a control
showing a dial position the simulation is not running at. During a run that
write happens on every render tick (5 Hz). Whether Flet's diff treats a
same-value write as a no-op, and whether a write landing mid-drag snaps the
thumb, was not verified: no live client was available in the session that
made the change.
**Why it matters.** The write-back itself is a presentation-correctness fix
and should stay. The unverified part is whether it costs anything or
interferes with dragging — the same class of unknown as PL-010, and worth
settling in the same sitting on a client.
**Where.** `app/simulation_view.py` (`_refresh_view`).
**First step.** Run the app, drag each slider through a full sweep during a
run, and watch for thumb snapping or lag; then check whether frame cost
changed measurably.
**Done when.** Dragging during a run is confirmed smooth on a live client,
or the write-back is narrowed to the cases that need it with the reason
recorded.

### PL-028 Decide the fate of `AlveolarCompartment.time_constant_s`
`P2` · `S` · `refactor` · needs-decision · added 2026-08-24

**Problem.** Deleting `advance_ventilation` (PL-022) left
`AlveolarCompartment.time_constant_s` with no caller in the shipped
package; it was that method's only consumer. It is still correct —
\(60 V_A / \dot{V}_A\), 37.5 s at the reference adult — and still covered by
unit tests, but nothing reads it.
**Why it matters.** It is not merely dead: it is the *ventilation-only*
alveolar time constant, which is not the time constant of the shipped
coupled dynamics (circuit coupling and blood uptake both change it). A
future caller who displays it as "the alveolar time constant" would present
a plausible number for the wrong quantity. `docs/MODEL.md` does not define
it. Same question as PL-004 for the circuit, and worth deciding with it.
**Where.** `core/alveolar.py` (`time_constant_s`),
`tests/unit/test_alveolar.py`.
**Decision needed.** Whether an uncalled but correct descriptive property
is worth keeping on the compartment API. Deleting it removes a
misinterpretation risk and the loader has no use for it; keeping it costs
three lines and preserves a quantity a future ventilation display may want.
Decide it alongside PL-004, which asks the same question for the circuit.
**First step.** Answer that question, then either delete the property with
its two unit tests or extend its docstring to say what it is not.
**Done when.** The property is gone, or its docstring states that it is
ventilation-only and is not the coupled alveolar time constant.

### PL-004 Decide the fate of `SimulationSnapshot.circuit_time_constant_s`
`P2` · `S` · `defect` · needs-decision · added 2026-08-23

**Problem.** The field is still computed on every snapshot but has had no
corresponding display widget since the v0.1.0 UI rewrite. v0.0.2 displayed
it; v0.1.0 does not.
**Why it matters.** A computed-but-unshown value is dead weight that
invites a future reader to assume it is displayed somewhere and trust it.
Small, but it is in the snapshot contract.
**Where.** `core/simulation.py`, `app/simulation_view.py`.
**Decision needed.** Restore the display or remove the field. Restoring it
requires deciding what the value means to a learner in the current
six-compartment model, where it describes only the circuit and not patient
uptake — which is an argument for removal unless it is labeled carefully.
**Done when.** Either the field is gone with its tests updated, or it is
displayed with an unambiguous label and unit.

### PL-005 Replace the full-screen startup window with a sized, centered one
`P2` · `S` · `ux` · ready · added 2026-08-23

**Problem.** `app/main.py` sets `page.window.full_screen = True` on
startup.
**Why it matters.** Full-screen-on-launch is a hostile default and hides
the window controls on some platforms. Prior project decision is to replace
it.
**Where.** `app/main.py`.
**First step.** Choose the sizing approach. Constraints from the prior
decision: no magic pixel dimensions, no monitor-specific assumptions, and
no native display-probing dependency.
**Done when.** The app opens in an adequately sized, centered window that
remains fully visible on different displays.

### PL-006 Clarify what `RespiratorySystem` actually owns
`P2` · `M` · `refactor` · needs-decision · added 2026-08-23

**Problem.** `core/respiratory_system.py` bundles concerns beyond what its
name suggests. "Respiratory system" clinically means the patient's own
lungs and airways, which maps only to `alveoli`. `circuit` is the
anesthesia machine's breathing circuit — equipment, not patient physiology
— and `set_cardiac_output()` forwards to `patient.set_cardiac_output()`,
which is a circulatory concern.
**Why it matters.** The class is the entry point to the scientific core, so
a misleading name and boundary is what a cold reader hits first.
**Where.** `core/respiratory_system.py` and its call sites.
**Decision needed.** Either keep it a thin coordinator (its `advance()` and
accounting already mostly are) and drop the setter delegation so callers
reach `patient`, `circuit`, or `alveoli` directly; or rename it to name the
coupled machine-plus-patient system rather than just the respiratory piece.
**Done when.** The naming and the delegation boundary agree with each
other, call sites are updated, and reference tests are unchanged in
behavior.

### PL-007 Make the payload/public-dataclass pattern self-evident in `core/parameters.py`
`P2` · `S` · `docs` `refactor` · ready · added 2026-08-23

**Problem.** The `_AgentPayload`/`AgentParameters` split — a private
Pydantic validation model paired with a public, frozen,
Pydantic-independent dataclass, repeated for
`_ReferenceAdultPayload`/`ReferenceAdultParameters` — reads as confusing
duplication.
**Why it matters.** The design is correct: it keeps the rest of the core
decoupled from the validation library. But a reader who does not see the
rationale is liable to "simplify" it away.
**Where.** `core/parameters.py`.
**First step.** The module docstring added 2026-08-23 explains the split at
a high level. Decide whether that is sufficient or whether each pair needs
a more local marker — a shared base-naming convention, or a one-line
comment at each `_...Payload` class. PL-021 has since given every payload
model a shared `_StrictPayload` base, so the base-naming half of that
option now exists; what it does not yet carry is why the `_...Payload` /
public-dataclass pair exists at all.
**Done when.** A reader landing on either `_...Payload` class can tell why
it exists without scrolling to the module docstring.

### PL-010 Reuse chart point objects instead of rebuilding them every frame
`P2` · `S` · `perf` · ready · added 2026-08-23

**Problem.** `SimulationView._decimated_points` builds a fresh
`fch.LineChartDataPoint` for every drawn point on every frame. Each one is a
Flet `BaseControl`, measured at ~8.4 us to construct; mutating an existing
point's `x`/`y` instead was measured at ~0.43 us, a 20x difference. With the
payload now bounded at 300 points per trace this costs about 15 ms of the
~17 ms frame, so reuse would take a frame to roughly 2 ms.
**Why it matters.** Pure headroom rather than a defect — the current frame
is already well inside budget. It matters mainly as headroom for PL-009,
where a speed multiplier raises the render rate.
**Where.** `app/simulation_view.py` (`_decimated_points`).
**First step.** Confirm against a live Flet client that in-place mutation of
a point actually repaints. PL-001 deliberately did not take this win because
it could not be verified without a client: a mutation Flet's diff does not
notice would leave the chart silently showing stale data, which is a
presentation-correctness failure, not a cosmetic one.
**Done when.** Frame cost is measurably reduced, and a live client is
confirmed to repaint traces on every frame rather than freezing them.

### PL-011 Bound the controller's concentration history
`P2` · `S` · `perf` · ready · added 2026-08-23

**Problem.** `SimulationController._concentration_history` appends one
sample per `advance()` and nothing ever trims it. At the fixed 0.1 s step
that is 36 000 samples per hour of simulated time, held for the life of the
session.
**Why it matters.** No longer a rendering problem — PL-001 made the render
payload independent of history length — but still unbounded memory growth in
a long teaching session. Lower priority than it looks: a slotted dataclass of
seven floats is on the order of a few hundred bytes, so an hour costs single-
digit MB.
**Where.** `app/controller.py` (`_concentration_history`, `advance`).
**First step.** Decide what the history is *for* now that the chart no longer
consumes all of it. If it is the record of a run (a future export or replay
feature), it should stay complete and the fix is a documented ceiling with an
explicit failure at the limit rather than silent trimming.
**Done when.** Memory growth over a long run is bounded, or the retention
policy is documented and deliberate rather than accidental.

### PL-012 Decide whether the chart should show the whole run
`P2` · `S` · `ux` · needs-decision · added 2026-08-23

**Problem.** The chart shows a scrolling 300 s window
(`MAX_CHART_WINDOW_S`), so on a run longer than five minutes the wash-in
curve scrolls off the left edge and cannot be seen again.
**Why it matters.** Wash-in and washout shape is the thing a learner is
there to see; a window that hides it works against the educational purpose.
The window was also the only thing bounding the drawn span, and PL-001
removed that constraint: with decimation to a fixed per-trace budget,
showing the entire run from t=0 now costs exactly the same as showing five
minutes of it.
**Where.** `app/simulation_view.py` (`MAX_CHART_WINDOW_S`, `_refresh_view`).
**Decision needed.** Show the whole run, keep the scrolling window, or offer
both. Showing the whole run means the x-axis rescales continuously, which
trades a stable time axis for a complete curve; a fixed window keeps the
recent detail legible. This is a teaching-design call, not a technical one.
**Done when.** The displayed time span is a deliberate, documented choice
rather than an artifact of an earlier payload limit.

## P3 — Icebox

### PL-019 Remove `BreathingCircuit`'s agent-unaware delivered-concentration default
`P3` · `S` · `refactor` · ready · added 2026-08-24

**Problem.** `BreathingCircuit.delivered_concentration_fraction` defaults to
`0.08`, a sevoflurane-shaped literal on a class that knows nothing about
agents. Since PL-015 the circuit also carries a vaporizer maximum, so
`BreathingCircuit(max_delivered_concentration_fraction=0.05)` raises unless
the caller remembers to pass a deliverable concentration too.
**Why it matters.** Not a defect: the raise is the intended fail-closed
behavior, and every agent-aware path goes through
`RespiratorySystem.for_agent()`, which sets both values from the data file.
It is a rough edge for a direct core caller, and one more agent-unaware
literal of the kind PL-017 removed from the controller.
**Where.** `core/circuit.py`, `tests/unit/test_circuit.py`,
`tests/reference/test_multi_agent.py`, `tests/reference/test_sevo_patient.py`.
**First step.** Decide the default: `0.0` (vaporizer off, always valid,
but changes what a bare `BreathingCircuit()` simulates and so touches the
reference tests that rely on the 8% start) or no default at all.
**Done when.** Constructing a circuit with a vaporizer maximum below 8%
does not require remembering a second argument, and the reference tests
state their delivered concentration explicitly.

### PL-020 Bring tests and `tools/` under the type-check gate
`P3` · `S` · `infra` · needs-decision · added 2026-08-24

**Problem.** `make check` runs `uv run mypy src`, so `tests/` and `tools/`
are unchecked. `uv run mypy .` reports 24 errors across 5 files on a clean
tree — mostly test fakes passed where a real Flet type is annotated
(`_FakePage` for `Page`) and a re-exported `ft` in `test_bootstrap.py`.
**Why it matters.** Low urgency, and the narrow gate may well be
deliberate: annotating test doubles to satisfy a UI framework's types can
cost more than it returns. But the gap is currently silent, and
`tools/punch_list.py` — which gates every punch-list change in CI — is
unchecked along with the tests.
**Where.** `Makefile` (`check`), `pyproject.toml` (`[tool.mypy]`),
`tests/unit/test_simulation_view.py`, `tests/unit/test_bootstrap.py`.
**Decision needed.** Widen the gate to `tools/` only, to `tests/` as well,
or neither. The 24 errors are almost entirely in the `tests/` half, so
`tools/` alone is close to free while `tests/` is the part that costs
something and returns the least.
**Done when.** The gate covers whatever scope is chosen and passes, or the
narrow gate is documented as deliberate with the reason.

### PL-029 Surface the ISO 5360 color reference in the interface
`P3` · `S` · `ux` `docs` · ready · added 2026-08-24

**Problem.** `AgentColorScheme` records `standard_color_name`,
`standard_color_munsell`, and `standard_color_pantone` for every agent, but
nothing in the interface reads them. A user sees a colored badge with no
indication that the color reproduces a cited standard rather than being
decoration.
**Why it matters.** Not a correctness defect — the provenance is recorded in
`app/theme.py` and `docs/MODEL.md`. But a simulator that deliberately
reproduces a real safety feature teaches more when it says so: a learner who
does not already know the ISO 5360 color convention cannot learn it from an
unlabeled colored badge.
**Where.** `app/simulation_view.py` (header badge and dropdown),
`app/theme.py`.
**First step.** Decide the surface. A tooltip on the badge is cheapest and
adds no persistent clutter, but tooltips are invisible to touch users and
usually to screen-reader users.
**Done when.** The agent's standard color name and its ISO 5360 source are
discoverable from the interface without reading the source, and the chosen
surface works for keyboard and touch users.

### PL-030 Stop rebuilding the agent color objects on every render tick
`P3` · `S` · `perf` · ready · added 2026-08-24

**Problem.** `SimulationView._apply_agent_color_scheme` is called from
`_refresh_view`, so it constructs a fresh `ft.TextStyle` and a fresh
`ft.Border` on every render tick even when the selected agent has not
changed.
**Why it matters.** Trivial in isolation, and not a correctness issue. It is
the same shape of avoidable per-frame allocation that PL-010 tracks for chart
points, and the agent color changes only on an explicit user selection, so
the work is wasted on almost every tick.
**Where.** `app/simulation_view.py` (`_apply_agent_color_scheme`,
`_refresh_view`).
**First step.** Either precompute one `TextStyle` and one `Border` per entry
in `AGENT_COLOR_SCHEMES` at import time, or make `_apply_agent_color_scheme`
a no-op when the agent id is unchanged since the last call.
**Done when.** Switching agents still repaints both the header badge and the
dropdown, and a render tick with an unchanged agent allocates neither object.

### PL-009 Playback speed multiplier
`P3` · `L` · `feature` · needs-decision · added 2026-08-23

**Problem.** No faster-than-real-time playback. Target is real time up to
roughly 120x and beyond, comparable to the Gas Man reference simulator.
**Why it matters.** Wash-in and washout of a low-solubility agent take
clinical minutes to tens of minutes; watching them in real time is a poor
use of a learner's attention.
**Where.** `app/controller.py`, `app/simulation_view.py`; sim time is
already explicit state independent of wall-clock time, so going faster
mostly means calling `advance()` more times per render tick.
**Decision needed.** Scope this into a `ROADMAP.md` milestone before any
implementation starts — it is an `L` and must not be started from this
entry. The scoping has to settle how the multiplier is exposed without
creating a hidden mode, and how it interacts with the fixed
`SIMULATION_STEP_S = 0.1`.
**Note.** The PL-001 blocker is cleared: render cadence is now independent
of simulation cadence, and frame cost no longer grows with run length, so a
multiplier no longer multiplies a growing bottleneck.
**Done when.** A scoped milestone exists in `ROADMAP.md`, or the idea is
deliberately retired.

---

## Milestone work

When the punch list is in good shape and the question is "should we move on
to the next roadmap feature instead?", the answer lives in `ROADMAP.md`, not
here. The current state is: v0.2.1 is the baseline, no later milestone is
scoped yet, and PL-003 above is the task that scopes the next one.

Ideas that are neither a punch-list task nor a scoped milestone —
power-user custom agents, the long-term Gas Man plus SimTiva vision,
publication-quality figure export — stay in `docs/WORKING_NOTES.md` until
someone is ready to scope them.

## Recently completed

Completed items move here with their commit reference, newest first, and
are trimmed once they are no longer useful as recent history. One line
each, in the form the checker reads:

```text
- PL-000 Title of the completed item — `abc1234`
```

- PL-002 Color-code agent selection to real vaporizer colors — `74bec83`
- PL-022 Delete the dead, non-conservative `advance_ventilation` — `956e710`
- PL-018 Keep a core failure from silently killing a running simulation — `4c442ef`
- PL-013 Triage the review harness's four remaining findings — `f51762a`
- PL-014 Land or discard the unmerged punch-list model-guidance work — `7714386`
- PL-015 Reject an out-of-range delivered concentration instead of simulating it — `bc5f823`
- PL-016 Make the agent MAC cross-check fail closed — `bc5f823`
- PL-017 Source the patient defaults from the data file, not controller literals — `bc5f823`
- PL-008 Documentation refresh pass — `2484611`
- PL-001 Bound the chart payload and decouple simulation from render cadence — `3749588`
