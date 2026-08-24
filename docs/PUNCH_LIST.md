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

## P1 — Next

### PL-013 Triage the review harness's four remaining findings
`P1` · `S` · `safety` `science` `defect` · ready · added 2026-08-24

**Problem.** The harness under `tools/review-verification/` reproduces the
independent architecture review of the v0.2.0 baseline on demand. It is now
on the development line (`655e429`), and the three safety-critical findings
it carried are fixed in v0.2.1 (`bc5f823`): `P1-2`, `P1-3`, and `P1-5` all
report FIXED. `P1-1` is filed as PL-018. Four findings are still neither
tracked nor declined: `P1-4` (no `extra='forbid'`), `P1-6` (dead,
non-conservative `advance_ventilation`), `P2-1` (mass balance cannot detect
a wrong rate), and `P2-4` (the venous pool dominates early mixed-venous
values).
**Why it matters.** A reproduced finding that is in no queue is a finding
that will be lost the next time the harness is not run. Two of the four
(`P1-4`, `P1-6`) are safety-relevant: a silently ignored data-file typo and
a non-conservative dead code path both produce plausible wrong numbers.
**Where.** `tools/review-verification/`, `core/parameters.py`,
`core/alveolar.py`, `docs/MODEL.md`.
**First step.** Run `verify_findings.py`, then file each of the four as its
own entry here or record an explicit reason for declining it.
**Done when.** Each of the four is an entry here or explicitly declined
with a reason, and `claude/repo-architecture-review-3h39kh` is deleted.
**Context.** `docs/WORKING_NOTES.md` § "Open thread: the unmerged
architecture review".

### PL-018 Keep a core failure from silently killing a running simulation
`P1` · `M` · `safety` `defect` · ready · added 2026-08-24

**Problem.** Two halves of one failure mode, reported as `P1-1` by the
review harness. `core/` raises bare `ValueError` from its numeric guards,
outside its own `AnesthesiaSimulationError` hierarchy, so a caller cannot
distinguish a simulation failure from a programming error. And
`SimulationView._run_simulation_timer` has no exception handling at all, so
any raise from a step or a setter kills the asyncio task while the UI still
reads "Running" and keeps displaying the last state.
**Why it matters.** A frozen display that still claims to be running is a
stale-state human-factors failure: the reader has no cue that the numbers
stopped advancing. v0.2.1 raises the stakes slightly — controller setters
can now reject an out-of-range delivered concentration, so a raise can
reach a UI callback, though the slider's bounds keep it unreachable today.
**Where.** `core/validation.py`, `core/exceptions.py`, `core/circuit.py`
and the other compartments, `app/simulation_view.py`
(`_run_simulation_timer`, the setter callbacks).
**First step.** Decide whether the core's numeric guards should raise a
`SimulationConfigurationError` subclass or whether
`AnesthesiaSimulationError` should inherit from `ValueError`; the second is
smaller but keeps the two hierarchies conflated.
**Done when.** A raise from `core/` during a run leaves the interface in an
unambiguous stopped/failed state rather than a stale running one, and the
harness's two `P1-1` checks report FIXED.
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

- PL-015 Reject an out-of-range delivered concentration instead of simulating it — `bc5f823`
- PL-016 Make the agent MAC cross-check fail closed — `bc5f823`
- PL-017 Source the patient defaults from the data file, not controller literals — `bc5f823`
- PL-008 Documentation refresh pass — `2484611`
- PL-001 Bound the chart payload and decouple simulation from render cadence — `3749588`
