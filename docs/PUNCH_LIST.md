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
| `P1` | Needed before the next milestone can be called done, a real defect that is not user-misleading, or `session-cost` work whose payoff compounds across every later session. | Next in line. |
| `P2` | Genuine improvement with no deadline pressure. | Queued. |
| `P3` | Worth keeping, not worth doing soon; includes ideas that need scoping before they can even be estimated. | Icebox. |

Anything touching a safety-critical path per `CLAUDE.md` ("Safety-critical
clinical-output standard") starts at `P0` or `P1`. It does not sit in `P2`
because it is small.

`session-cost` work also starts at `P1`, for a different reason: it is not
urgent in itself, but it is the multiplier on everything below it. Every
token this project spends re-deriving context, re-reading a rule that sits in
the cached prefix of every request, or grepping by hand what a script could
decide is a token not spent fixing a defect. Deferring that work to "when
there is time" is what guarantees there is never time — the queue is worked
in sessions, and a cheaper session works more of the queue. This does not
outrank a `safety` or `science` item; it runs alongside them, and the band's
running order says which goes first.

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
`infra`, `feature`, `planning`, `session-cost`.

`perf` and `session-cost` are different axes and are not interchangeable.
`perf` is the running application: frames, memory, render payloads — what a
user experiences. `session-cost` is the cost of developing it: context resent
on every turn, work a session redoes because nothing recorded it, judgment
spent on what a script could decide. An item can be one without being the
other, and the priority rule above applies only to `session-cost`.

## Grooming

Reprioritize when new items arrive rather than only appending: a new `P0`
may demote what was previously next, and a resolved blocker may promote a
`blocked` item to `ready`. Delete a resolved `WORKING_NOTES.md` thread
rather than leaving it stale.

An item leaves the queue in exactly two ways, and both are written down:

- **Completed.** It moves to "Recently completed" with its commit
  reference. Once it stops being recent it moves again, to "Archive".
- **Closed without action.** It is dropped, folded into another entry, or
  superseded, and it goes straight to "Archive" with the date and a
  one-clause reason.

There is no third path. Deleting an entry outright is the one outcome this
file exists to prevent: git history is a weak fallback, because recovering
a dropped item requires already knowing it existed, and without the reason
a finding was rejected the same finding gets re-raised and re-argued in a
later session.

### What is checked automatically

`tools/punch_list.py` handles the mechanical half of grooming. Run it with
`make punch-list`; `make check` and CI run it too, and a `SessionStart` hook
emits a short digest of the queue at the start of every session.
`python3 tools/punch_list.py list` prints one line per open item, which is
the cheap way to see the queue without reading these briefs.

What matters here is the split between the two things it reports, because
they are addressed to different readers:

- **Errors** mean this file is wrong — a reused id, a missing brief field, a
  `safety` or `science` item parked below `P1`, a `PL-` reference pointing
  at nothing. Each one silently loses information, so they fail the build.
  References resolve against the archive as well as the queue, so archiving
  an item never breaks a pointer to it.
- **Advisories** mean a judgment is due, usually about the shape of the top
  band rather than the length of the file. They never fail a build, and they
  are a call to put a grooming pass to the project owner, not licence to
  start one.

`tools/doc_check.py` does the same job for the documentation itself and runs
beside it in `make check`, `make doc-check`, and CI: it decides the
package-map, provenance-table, and citation questions, and its `candidates`
mode prints the documentation lines a diff puts in question.

Neither tool decides anything that needs judgment — whether the top `P1` is
still the right next thing, whether a priority reflects reality, whether a
statement in another document is still *true*. They detect the conditions;
a session makes the call. For the exact checks and their thresholds, read
the tools; for the workflows that act on them, use the `punch-list` skill.

---

## P1 — Next

**Running order, updated 2026-08-24.** The simulator's own correctness leads
this band. `session-cost` work is a multiplier on every session after it and
is worth promoting, but the promotion has no natural ceiling and it had taken
four of seven P1 slots ahead of the science and safety items; PL-035 and
PL-036 went to `P2` in that pass, and PL-034 landed. PL-037 stays because it
is `S`, certain, and prevents a whole wasted session. PL-023 landed, and the
measurements it produced opened PL-040. So: PL-026 and PL-040 first — both
are safety-tagged questions about what the interface shows, both are
answerable in a conversation rather than a session, and deciding them
together is cheaper than deciding them apart; then PL-037; then PL-003, which
is milestone scoping and follows the band.

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

### PL-040 Stop displaying more decimals than the model can support
`P1` · `S` · `safety` `ux` · needs-decision · added 2026-08-24

**Problem.** `SimulationView._format_percent` renders every concentration as
`f"{fraction * 100.0:.3f}%"` — thousandths of a percentage point. The
operator split is not accurate to that. Measured against the independent
solution added by PL-023, the shipped step disagrees with the true solution
by up to 2.5e-5 in fraction, i.e. 0.0025 percentage points, so the third
displayed decimal is numerical noise and the second is at the edge of it.
Parameter uncertainty is coarser again.
**Why it matters.** `CLAUDE.md` requires displayed precision to be justified
by model fidelity and interpretability, and forbids presentation implying
more certainty than the model supports. A trainee reading `2.134%` may
reasonably infer the simulator resolves thousandths of a percent; it does
not, and clinical agent monitors report 0.1 percentage point.
**Where.** `app/simulation_view.py` (`_format_percent` and the chart axis
labels sharing its scale), `docs/MODEL.md` § "Minimum displayed outputs",
and the view-formatting tests in `tests/unit/`.
**Decision needed.** How many decimals each displayed quantity earns, and
whether the answer is uniform. Two decimals suit circuit, alveolar, and
mixed-venous values, but muscle and fat sit near 1e-6 fraction early in a run
and would read `0.00%` for minutes, erasing the wash-in the display exists to
teach. Uniform reduction, per-compartment precision, and a
significant-figures rule are all defensible; the rationale is what must be
recorded, not a precision tuned by eye.
**Done when.** Displayed precision is a recorded decision tied to model
fidelity, `docs/MODEL.md` states it alongside the displayed outputs, and the
formatting tests pin it.

### PL-037 Check the branch is current against `main` before starting an item
`P1` · `S` · `session-cost` `infra` · ready · added 2026-08-24

**Problem.** Nothing in `CLAUDE.md` or the punch-list skill tells a session
to verify its branch against `main` before it starts work. A session that
picks up a branch whose pull request has already been merged stacks new
commits on merged history; one that starts from a stale base does the work
against code that has since moved.
**Why it matters.** Both cost a full rework cycle — the most expensive kind
of waste, since it is paid at the end of a session in merge conflicts rather
than at the start in one command. This actually happened: the session that
landed PL-032 was asked to check, found its own branch had been merged as
PR 19, and had to restart the branch from `main` before continuing.
**Where.** `.claude/skills/punch-list/SKILL.md` (a step before "Mode:
recommend what to work on" hands off, and in "Mode: hotfix"), possibly
`CLAUDE.md`'s "Punch list and work selection".
**First step.** Write the check as the three commands it actually takes:
`git fetch origin main`, `git rev-list --left-right --count origin/main...HEAD`,
and — when the branch is behind with nothing ahead — restart it from `main`
rather than merging into it.
**Done when.** The handoff a recommendation produces names the check, so a
fresh session runs it before its first edit rather than discovering the
problem at push time.

### PL-003 Scope the next milestone in ROADMAP.md
`P1` · `M` · `planning` · ready · added 2026-08-23

**Problem.** No milestone after v0.2.0 is scoped (v0.2.1 is a validation
hotfix on that baseline and v0.2.2 a hardening release on it, neither of
them a milestone). `ROADMAP.md`'s
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

### PL-038 Verify what a mid-session `CLAUDE.md` edit actually invalidates
`P2` · `S` · `session-cost` `docs` · ready · added 2026-08-24

**Problem.** `CLAUDE.md`'s "Session and tool-use efficiency" section says to
edit `CLAUDE.md` and the core docs in their own session, because "they sit in
the cached prefix of every request, so editing one partway through a session
invalidates that cache for the rest of it." Anthropic's documentation
describes a different mechanism: `CLAUDE.md` is read at session start and
delivered as a user message, and is re-injected from disk only after
compaction. On that description an edit to the file on disk does not alter
the copy already in the message history, and so does not invalidate the
prefix mid-session.
**Why it matters.** If the claim is wrong it is costing sessions directly, in
the least visible way: it pushes work onto a second session — a cold cache
and a re-read of the same files — to avoid a penalty that may not exist. The
advice is also load-bearing for how this repository schedules its own
process work.
**Where.** `CLAUDE.md`, "Session and tool-use efficiency", the bullet
beginning "Edit `CLAUDE.md` and the core docs in their own session".
**First step.** Check the current Claude Code documentation on how memory
files are loaded and what survives compaction, then edit a `CLAUDE.md`
mid-session and compare reported cache-read and cache-write token counts on
the turns either side of the edit.
**Done when.** The bullet states what actually happens, and either keeps the
same-session recommendation with a correct reason or drops it.
**Context.** Raised by the punch-list workflow review of 2026-08-24, which
relied on the same documentation while assessing what is resident in context.

### PL-039 Stop attributing band-level prose to the entry above it
`P2` · `S` · `defect` `infra` · ready · added 2026-08-24

**Problem.** `tools/punch_list.py` ends an entry's body at the next `###` or
`##` heading, so any prose written between entries — a band-level note, a
running-order paragraph — is parsed as part of the preceding entry. This is
not theoretical: the P1 band's running-order note was silently counted into
PL-037's body, pushing it to 35 lines and firing a spurious
`MAX_ENTRY_LINES` advisory against an entry that was within its brief.
**Why it matters.** The line count is the visible symptom; `Entry.blockers`
is the real one. It reads `PL-` references out of the same body, so a band
note that mentions an item would be read as a dependency of whichever entry
happens to sit above it, and a `blocked` item could be promoted or held on a
reference nobody wrote about it.
**Where.** `tools/punch_list.py`, `parse()` and `Entry.blockers`;
`tests/unit/test_punch_list_tool.py`.
**First step.** Decide whether band notes are legal in the format at all. If
they are, end an entry's body at the first blank-line-separated block that
is not part of its brief, and give the file's "Entry format" section a line
saying where a band note may go. If they are not, make one an error.
**Done when.** A band-level note between two entries changes neither the
preceding entry's line count nor its blockers, with a test that fails on
today's parser.
**Context.** Found while grooming the P1 band on 2026-08-24; the stale note
that triggered it was rewritten in the same pass.

### PL-036 Extend `doc_check.py` to the statements it currently cannot decide
`P2` · `M` · `docs` `infra` `session-cost` · needs-decision · added 2026-08-24

**Problem.** `tools/doc_check.py` checks that cited things *exist*. It
cannot check that a sentence about them is *true*: a `must` in
`docs/MODEL.md` the code no longer satisfies, a shipped feature still
described as deferred, a displayed value whose units the interface changed.
**Why it matters.** Those are the remaining close-out failure modes, and
they are the ones with clinical consequence — `CLAUDE.md` calls a stale
statement about what a value means a safety issue, not tidiness.
**Where.** `tools/doc_check.py`, `docs/MODEL.md` ("Required invariants",
"Minimum displayed outputs").
**Decision needed.** Whether any of it is mechanizable without producing
confident nonsense. One candidate is concrete: `docs/MODEL.md`'s "Minimum
displayed outputs" could name the `SimulationSnapshot` field behind each
displayed value, making the list checkable against the dataclass the way the
provenance table is now checkable against the JSON. Whether the `must`
statements can be tied to named tests is the harder half.
**Done when.** Either a further check is implemented, or the decision that
this half stays human is recorded with its reasoning.

### PL-035 Consider a `**Docs.**` entry field naming the docs a task will touch
`P2` · `S` · `docs` `infra` `session-cost` · needs-decision · added 2026-08-24

**Problem.** Close-out has to work out which documents a change could have
invalidated after the change is written. The session that captured the item
often already knew — it just had nowhere in the entry format to say so.
**Why it matters.** `tools/doc_check.py candidates` narrows the sweep from a
diff, but it only finds documents that already name something the diff
touched. A document that *should* mention a new feature and does not is
exactly what it cannot see, and is a failure mode that has happened here.
**Where.** `docs/PUNCH_LIST.md` (entry format), `tools/punch_list.py`
(`_check_entry`), `.claude/skills/punch-list/SKILL.md` (capture mode).
**Decision needed.** Whether an optional field earns its cost. Against: an
optional field that is usually omitted is noise, and a wrong guess at
capture time may be worse than no guess. For: it is free to write when the
capturing session already knows, and close-out reads it for nothing. Decide
also whether the checker should validate that the named paths exist, which
`doc_check.py`'s resolver already does for prose.
**Done when.** The field is either in the format spec and validated, or the
decision not to add it is recorded in "Archive" with its reason.

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

### PL-004 Decide the fate of the two uncalled descriptive time constants
`P2` · `S` · `defect` `refactor` · needs-decision · added 2026-08-23

**Problem.** Two correct but uncalled quantities sit in the core.
`SimulationSnapshot.circuit_time_constant_s` is computed on every snapshot
but has had no display widget since the v0.1.0 UI rewrite.
`AlveolarCompartment.time_constant_s` — \(60 V_A / \dot{V}_A\), 37.5 s at
the reference adult — lost its only consumer when PL-022 deleted
`advance_ventilation`. Both are unit-tested; neither is read by shipped
code, and `docs/MODEL.md` defines neither.
**Why it matters.** Neither is merely dead. Each is a single-mechanism time
constant that is *not* the time constant of the shipped coupled dynamics:
the circuit one excludes patient uptake, the alveolar one excludes circuit
coupling and blood uptake. A future caller displaying either as "the time
constant" would present a plausible number for the wrong quantity, and a
computed-but-unshown value invites a reader to assume it is trusted output.
**Where.** `core/simulation.py`, `core/alveolar.py`,
`app/simulation_view.py`, `tests/unit/test_alveolar.py`.
**Decision needed.** Whether an uncalled but correct descriptive quantity
earns its place on the core API. Deleting removes the misinterpretation
risk and costs the loader nothing; keeping costs a few lines and preserves
quantities a future display may want. One question asked twice — answer it
once, for both.
**Done when.** Each value is gone with its tests updated, or its docstring
names the mechanism it describes and says it is not the coupled time
constant; any restored display carries an unambiguous label and unit.

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

### PL-010 Stop rebuilding render objects on every frame
`P2` · `S` · `perf` · ready · added 2026-08-23

**Problem.** Two allocations repeat on every render tick.
`SimulationView._decimated_points` builds a fresh `fch.LineChartDataPoint`
for every drawn point (~8.4 us each, against ~0.43 us to mutate an existing
point's `x`/`y`); at the bounded 300 points per trace that is about 15 ms of
the ~17 ms frame. `_apply_agent_color_scheme` constructs a fresh
`ft.TextStyle` and `ft.Border` even when the selected agent has not changed,
which is almost every tick.
**Why it matters.** Headroom rather than a defect — the frame is already
well inside budget. It matters as headroom for PL-009, where a speed
multiplier raises the render rate.
**Where.** `app/simulation_view.py` (`_decimated_points`,
`_apply_agent_color_scheme`).
**First step.** The chart points need a live Flet client: confirm in-place
mutation actually repaints. PL-001 declined this win because a mutation
Flet's diff does not notice would leave the chart silently showing stale
data — a presentation-correctness failure, not a cosmetic one. The colour
objects need no client if they are precomputed per `AGENT_COLOR_SCHEMES`
entry at import time and still assigned every tick.
**Done when.** Frame cost is measurably reduced, a live client is confirmed
to repaint traces every frame, and switching agents still repaints both the
header badge and the dropdown.

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
here. The current state is: v0.2.2 is the baseline, no later milestone is
scoped yet, and PL-003 above is the task that scopes the next one.

Ideas that are neither a punch-list task nor a scoped milestone —
power-user custom agents, the long-term Gas Man plus SimTiva vision,
publication-quality figure export — stay in `docs/WORKING_NOTES.md` until
someone is ready to scope them.

## Recently completed

Completed items move here with their commit reference, newest first. Once
one has stopped being useful as recent history it moves down to "Archive"
rather than being deleted. One line each, in the form the checker reads:

```text
- PL-000 Title of the completed item — `abc1234`
```

- PL-041 Put the item ID where the branch name cannot carry it — `fb01800`
- PL-023 Gate the coupled dynamics on an independent solution, not just mass balance — `f5cd82b`
- PL-034 Trim `CLAUDE.md`'s punch-list section of what the skill restates — `22e7876`
- PL-032 Mechanize the decidable half of the close-out doc sweep — `3f786b5`
- PL-033 Record the reference patient's weight in the provenance table — `ebcf990`
- PL-025 Assign a release number to the post-v0.2.1 work — `3099980`
- PL-031 Record resolved punch-list items in a durable archive — `f5b77ec`
- PL-021 Reject unknown keys in the parameter-file schemas — `3465dcf`
- PL-002 Color-code agent selection to real vaporizer colors — `74bec83`

## Archive

The permanent record of everything that has left the queue and is no longer
recent history. One line each, newest first. This section is never trimmed:
`tools/punch_list.py` resolves the ids here exactly as it resolves open
ones, so a `PL-` reference from `ROADMAP.md` or `docs/WORKING_NOTES.md`
keeps working long after the item itself is gone.

Two forms, in the shapes the checker reads:

```text
- PL-000 Title of the completed item — `abc1234`
- PL-000 Title of the closed item — closed YYYY-MM-DD, why
```

The reason on a closed line is the whole point of the line. An item closed
without one gets re-raised by the next session that notices the same thing.

- PL-030 Stop rebuilding the agent color objects on every render tick —
  closed 2026-08-24, folded into PL-010: the same per-frame allocation in
  the same render tick, decided and fixed together
- PL-028 Decide the fate of `AlveolarCompartment.time_constant_s` —
  closed 2026-08-24, folded into PL-004: one question about an uncalled
  descriptive time constant, asked twice
- PL-022 Delete the dead, non-conservative `advance_ventilation` — `956e710`
- PL-018 Keep a core failure from silently killing a running simulation — `4c442ef`
- PL-013 Triage the review harness's four remaining findings — `f51762a`
- PL-014 Land or discard the unmerged punch-list model-guidance work — `7714386`
- PL-015 Reject an out-of-range delivered concentration instead of simulating it — `bc5f823`
- PL-016 Make the agent MAC cross-check fail closed — `bc5f823`
- PL-017 Source the patient defaults from the data file, not controller literals — `bc5f823`
- PL-008 Documentation refresh pass — `2484611`
- PL-001 Bound the chart payload and decouple simulation from render cadence — `3749588`
