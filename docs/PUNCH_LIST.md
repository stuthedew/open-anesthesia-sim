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
a short digest of the queue at the start of every session. It reports two
kinds of finding, and the split is the point:

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

## P0 — Now

### PL-015 Reject an out-of-range delivered concentration instead of simulating it
`P0` · `S` · `safety` `defect` · ready · added 2026-08-24

**Problem.** `SimulationController.set_delivered_concentration`
(`app/controller.py:225`) passes its argument straight through to
`RespiratorySystem` and then to the circuit with no bound check. The
vaporizer maximum is applied only in `_build_state`, as
`min(requested_fraction, max_fraction)`. Calling the setter with 0.50 on
isoflurane (5.0% maximum) is accepted and simulated as 50%.
**Why it matters.** The whole simulation then runs from a delivered
concentration no real vaporizer can produce, and every downstream displayed
value — circuit, alveolar, arterial, tissue curves — is a plausible-looking
number from an impossible input. Today only the UI slider bounds the value,
so the guard is in the presentation layer rather than the model.
**Where.** `app/controller.py` (`set_delivered_concentration`,
`_build_state`), `core/respiratory_system.py:115`, `core/circuit.py`.
**First step.** Validate in `core/`, not the controller: reject a fraction
outside `(0, max]` with an `AnesthesiaSimulationError` subclass. Make
`_build_state` reject too rather than silently clamping — silent coercion
of a safety-critical input is what `CLAUDE.md` forbids — and update the
docstring that currently documents the clamp.
**Done when.** Both paths reject out-of-range input, a regression test
covers the 50%-on-a-5%-vaporizer case, and the `P1-2` check in PL-013's
harness reports FIXED.

### PL-016 Make the agent MAC cross-check fail closed
`P0` · `S` · `safety` `science` `defect` · ready · added 2026-08-24

**Problem.** `_AgentPayload._mac_percent_must_not_exceed_vaporizer_max`
(`core/parameters.py:199`) reads `max_delivered_concentration_percent` out
of `info.data`. Pydantic populates `info.data` in field-declaration order,
so the key is present only because `max_delivered_concentration_percent`
happens to be declared first. Reorder the two fields — or let the maximum
fail its own validation — and `info.data.get` returns `None`, the guard
returns the value unchecked, and an agent file declaring 40% MAC on a 5%
vaporizer loads clean.
**Why it matters.** This is the only cross-field check on the agent data
files, and MAC drives the default delivered concentration
(`_build_state` starts at 1 MAC). A guard that silently no-ops on a field
reordering is worse than no guard: it reads as validation coverage that
does not exist.
**Where.** `core/parameters.py` (`_AgentPayload`),
`data/agents/*.json`.
**First step.** Replace the `field_validator` with a
`model_validator(mode="after")`, which sees every field regardless of
declaration order.
**Done when.** The check fires independent of field order, a regression
test declares the fields in the failing order and asserts rejection, and
the `P1-5` check in PL-013's harness reports FIXED.

### PL-017 Source the patient defaults from the data file, not controller literals
`P0` · `S` · `safety` `science` `defect` · ready · added 2026-08-24

**Problem.** `SimulationController.__init__` hardcodes
`alveolar_ventilation_l_min = 4.0` and `cardiac_output_l_min = 5.0` as
Python literals. `data/patients/reference_adult.json` declares the same two
values with their citations, but nothing reads
`default_alveolar_ventilation_l_min` outside the schema, and
`default_cardiac_output_l_min` reaches only `core/patient.py`. Edit the
data file to 6.5 / 5.5 and the running app still uses 5.0 / 4.0.
**Why it matters.** The numbers agree today, so the duplication is
invisible; that is what makes it dangerous. The data file carries the
provenance under `docs/MODEL.md`, so the app is running values whose
citation trail points at a file it does not actually consult. Any future
correction to the cited defaults would silently not take effect.
**Where.** `app/controller.py` (`__init__`), `core/parameters.py:236-237`,
`core/patient.py:59`, `data/patients/reference_adult.json`.
**First step.** Drop the literals and take both defaults from the loaded
`PatientParameters`, keeping the constructor arguments as explicit
overrides.
**Done when.** Changing the data file changes the app's starting values, a
regression test asserts that, and the `P1-3` check in PL-013's harness
reports FIXED.

## P1 — Next

### PL-013 Land the review harness and triage its six remaining findings
`P1` · `M` · `safety` `science` `defect` · ready · added 2026-08-24

**Problem.** The branch `claude/repo-architecture-review-3h39kh` carries the
only surviving record of an independent architecture review of the v0.2.0
baseline: an executable harness under `tools/review-verification/` that
reproduces nine findings on demand. It was never merged, and none of the
nine findings appear in this file. Re-run against `main` on 2026-08-24, all
nine still reproduce and all three physics claims still hold.
**Why it matters.** Three of the nine were safety-critical enough to
promote to `P0` (PL-015, PL-016, PL-017), and the harness is what proves
they are fixed. Deleting the branch discards the evidence for all nine and
the only independent check on the physics claims in `docs/MODEL.md`.
**Where.** `tools/review-verification/` on that branch; `core/` validation
and parameter loading; `app/simulation_view.py` timer.
**First step.** Cherry-pick `0ccfa44` onto `main` (it applies cleanly —
four new files, no overlap) and re-run both scripts, so the P0 fixes have a
check to flip. The three safety findings are split out as PL-015, PL-016,
and PL-017; the six that remain are listed in the working-notes thread.
**Done when.** The harness is on `main`, each remaining finding is either an
entry here or explicitly declined with a reason, and the branch is
deleted.
**Context.** `docs/WORKING_NOTES.md` § "Open thread: the unmerged
architecture review".

### PL-002 Color-code agent selection to real vaporizer colors
`P1` · `M` · `ux` `safety` · ready · added 2026-08-23

**Problem.** The agent dropdown and selected-agent display are visually
neutral. Clinical vaporizers use a standardized per-agent color-keyed fill
system (the North American convention is commonly cited to ASTM D4774) so
that an agent is never mistaken for another at a glance.
**Why it matters.** This mirrors a real safety feature rather than being
styling. A wrong color-to-agent mapping would be actively misleading rather
than merely neutral, which makes it a presentation-correctness issue under
`CLAUDE.md`.
**Where.** `app/simulation_view.py` (dropdown and header construction),
`app/theme.py`.
**First step.** Verify the agent-to-color mapping against an authoritative
current source. Do not implement from recalled colors.
**Done when.** Each agent's control and header display carry the verified
color, text contrast against each fill is checked (including for
color-vision deficiency, since color must not be the only cue), and the
source for the mapping is cited where the constants live.

### PL-003 Scope the next milestone in ROADMAP.md
`P1` · `M` · `planning` · ready · added 2026-08-23

**Problem.** No milestone after v0.2.0 is scoped. `ROADMAP.md`'s
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

### PL-014 Land or discard the unmerged punch-list model-guidance work
`P2` · `S` · `infra` `docs` · ready · added 2026-08-24

**Problem.** The branch `claude/punch-list-tracking-u1159v` holds two
unmerged commits (`cd3b255`, `7015d3f`) that add `Entry.model_guidance` and
`_with_guidance` to `tools/punch_list.py`, with tests, so the startup digest
names which model a recommended item warrants instead of leaving the rule to
a session's memory. `main` has the general model-matching rule in
`CLAUDE.md` but not this mechanization.
**Why it matters.** Small and self-contained, but it is real work that is
lost if the branch is pruned, and the rule it automates is the one that
decides whether a safety-critical item gets the strongest model.
**Where.** `tools/punch_list.py`, `tests/unit/test_punch_list_tool.py`,
`CLAUDE.md`, `.claude/skills/punch-list/SKILL.md`.
**First step.** Cherry-pick both commits onto `main`. The only conflict is
in this file, where the branch still lists PL-001 as open; take `main`'s
side and drop that block.
**Done when.** The commits are on `main` with the quality suite green, or
the branch is deleted with a stated reason for declining them.

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
comment at each `_...Payload` class.
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
here. The current state is: v0.2.0 is the baseline, no later milestone is
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

- PL-008 Documentation refresh pass — `2484611`
- PL-001 Bound the chart payload and decouple simulation from render cadence — `3749588`
