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

_None._

## P1 — Next

### PL-001 Bound the chart payload and decouple simulation from render cadence
`P1` · `M` · `perf` · ready · added 2026-08-23

**Problem.** The live graph is slow and buttons feel unresponsive.
`SimulationController._concentration_history` grows without bound, and the
chart rebuilds full point arrays for all six series from that entire
history on every `_refresh_view()`, so the payload sent to the Flet client
grows for as long as the simulation runs. Separately, `advance()` and
`page.update()` are coupled back-to-back at 10 Hz in one coroutine on a
single asyncio event loop, so a slow flush blocks the next button click.
**Why it matters.** This is the most visible current defect in the running
app, and it is the prerequisite for the faster-than-real-time playback goal
(PL-009). Any speed multiplier multiplies whatever the render bottleneck
currently is.
**Where.** `app/controller.py`, `app/simulation_view.py`
(`_run_simulation_timer`, `_refresh_view`).
**First step.** Profile before changing anything — the diagnosis above is
from reading the code, not from a profiler. Confirm which of the two causes
dominates.
**Done when.** Render payload is bounded independent of run length, the
simulation history the controller keeps for accounting is unaffected, UI
responsiveness under a long run is measurably improved, and the accounting
and determinism tests still pass.
**Context.** `docs/WORKING_NOTES.md` § "Open thread: performance". Note
that multithreading is not the expected lever; the fix is architectural.

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

### PL-008 Documentation refresh pass
`P2` · `S` · `docs` · ready · added 2026-08-23

**Problem.** `README.md`, `docs/MODEL.md`, `ROADMAP.md`, and
`docs/WORKING_NOTES.md` have not been swept since the agent-specific
vaporizer-max and 1-MAC-default work (commit `7a867e9`) and the
module-docstring pass.
**Why it matters.** Stale docs are the main cost driver for cold sessions,
which is the problem this punch list exists to solve.
**Where.** `README.md`, `docs/MODEL.md`, `ROADMAP.md`,
`docs/WORKING_NOTES.md`.
**First step.** Diff the docs against the current behavior of the app and
the current contents of `data/agents/*.json`.
**Done when.** No statement in those four files contradicts the code, and
resolved threads have been deleted from `docs/WORKING_NOTES.md` rather than
left in place.

## P3 — Icebox

### PL-009 Playback speed multiplier
`P3` · `L` · `feature` · blocked · added 2026-08-23

**Problem.** No faster-than-real-time playback. Target is real time up to
roughly 120x and beyond, comparable to the Gas Man reference simulator.
**Why it matters.** Wash-in and washout of a low-solubility agent take
clinical minutes to tens of minutes; watching them in real time is a poor
use of a learner's attention.
**Blocked by.** PL-001. A speed multiplier multiplies the current render
bottleneck.
**Where.** `app/controller.py`, `app/simulation_view.py`; sim time is
already explicit state independent of wall-clock time, so going faster
mostly means calling `advance()` more times per render tick.
**Open questions.** How the multiplier is exposed without creating a hidden
mode, and how it interacts with the fixed `SIMULATION_STEP_S = 0.1`.
**Note.** Large enough that it should be scoped into `ROADMAP.md` before
implementation, not started from this entry.
**Context.** `docs/WORKING_NOTES.md` § "Open thread: playback speed".

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

_None yet._
