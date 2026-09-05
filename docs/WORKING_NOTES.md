# Working notes

This file is a running, cross-session log of open threads, diagnoses, and
rationale, not yet promoted into `ROADMAP.md` (version/milestone decisions)
or `docs/MODEL.md` (scientific model specification). It exists so that a new
conversation can pick up context without re-deriving it, and so that
decisions made in one conversation are visible to another.

**Scope decides what belongs here, not length.** An item file takes as much
narrative as a thread needs — `PL-H7XN` runs to 15 KB — so "too long for a
brief" places nothing here, and one item's own reasoning belongs in that
item, where the session that starts it will read it without being sent
anywhere. A thread belongs here when it is one of the three things no single
item can hold:

- **About more than one item.** Why a cluster is one design pass rather than
  three, what closing each one revealed, and why a nearby finding was
  excluded. No item is written from that vantage point.
- **Outliving its item.** Measurements and reasoning still needed after the
  item that produced them was dropped, or promoted into `ROADMAP.md` and
  removed from the queue.
- **Having no item at all.** Direction that is real but not yet workable, and
  the record of a direction tried and shelved.

It is not the task queue. Discrete, actionable work is tracked and
prioritized in `docs/items/`, and threads here cite the `PL-` ids they
concern. A queue item that points back here for its own reasoning is the
split applied wrongly: that reasoning belongs in the item. Anything outside
this file that has to cite it should cite an item id rather than a section
title — titles here are rewritten and deleted as threads resolve, so a
citation by title decays silently.

Any session working on this repository should read this file at the start
of a task that touches one of its open threads, and update the relevant
section (not just append) as the thread progresses. Write entries so a
reader with no memory of the originating conversation can act on them:
state facts and decisions, not "the user said" or "we discussed."

When a thread here is fully resolved (implemented, tested, and merged), its
outcome belongs in `ROADMAP.md`/`docs/MODEL.md`/commit history as
appropriate, and its entry here should be deleted rather than left stale.

## Repository state as of this writing

- `build/v0.1.0-sevo-patient` was fast-forward merged into `main` and the
  remote branch deleted; `main` is now the v0.2.0 baseline (isoflurane and
  desflurane added as additional loadable agents, all loaded through
  `load_agent_parameters(agent_id)` in `core/parameters.py`). All three are
  selectable in the running app: a basic picker was added in `00791b1`,
  after v0.2.0 closed and outside its scope. It restarts the run at the new
  agent's 1 MAC rather than switching mid-run — residual-agent washout
  across a switch is still the anesthesia-machine milestone's work, and
  `SimulationController.set_agent`'s docstring is the place that says so.
  Work now happens on a per-session branch merged into `main` by pull
  request, not directly on `main`; `CLAUDE.md` says how that branch, its
  commits, and the pull request carry the queue item's ID.
- `docs/MODEL.md` and `ROADMAP.md` are up to date with the v0.2.0
  implementation: the arterial-blood simplification is documented
  explicitly (flow-limited, `F_a \equiv F_A`, no separate compartment,
  matching the Gas Man reference simulator's mammillary structure), the
  parameter provenance table covers all three agents from the cited data
  files, and `tests/reference/test_multi_agent.py` covers directional
  solubility and mass-balance closure for isoflurane and desflurane.
- `simulation_view.py` is tested through a minimal fake `Page`/`Controller`
  pattern documented at the top of `tests/unit/test_simulation_view.py`,
  which is still where its presentation logic is covered. The pure modules
  it delegates to are tested without that pattern: the displayed-value
  formatters in `tests/unit/test_formatting.py`, the sample selection in
  `tests/unit/test_chart_downsampling.py`, the run's own recorded history in
  `tests/unit/test_run_history.py`, the recorded control changes in
  `tests/unit/test_control_timeline.py` and the wash-in ratio and its domain
  in `tests/unit/test_wash_in.py`, while `app/chart_series.py` is covered
  through the view, where a trace can be read back off the chart it was
  drawn on (PL-WB0X). The wash-in ratio is covered twice over on purpose:
  `tests/reference/test_published_wash_in.py` asserts that the number the
  chart draws is the number the Yasuda comparison was made on, so the two
  cannot drift apart (PL-ZRSP). The one thing that
  pattern cannot answer - whether Flet's diff reports what a frame changed -
  is `tests/integration/test_chart_patching.py`'s, which drives a real
  `flet.messaging.session.Session` over a recording connection instead
  (PL-010). The simulation and render loops are covered too (started as
  tasks, driven for a bounded slice of real time, then cancelled);
  `mount()`'s layout composition remains uncovered and has no formatting or
  domain logic to verify.
- Rendering is bounded and independent of run length: the chart is sent
  only the samples inside its visible window, reduced to at most
  `CHART_COLUMN_BUDGET_PER_SERIES` columns per trace (`app/chart_series.py`)
  by M4 (`app/chart_downsampling.py`), and the loops run at
  separate cadences. **Closed by PL-010, 2026-09-02.** What that left
  standing for another release was the *read* rather than the draw: the
  snapshot still copied every recorded sample on every frame, so the frame
  was bounded downstream of a cost that was not. PL-0VM7 moved the cut to
  the controller - the view asks `history_window()` for the axis it is
  about to draw - so the property now holds at the boundary as well as at
  the chart. The repaint mechanism
  was left unchanged here because no live Flet client was available to
  confirm it; one has now been run - Chromium against the `flet_web` server -
  and an in-place mutation of a `LineChartDataPoint` does repaint. The frame
  therefore moves the points the chart already holds rather than rebuilding
  them, which took the render tick from 16.6 ms to 2.6 ms at the saturated
  window. What the browser proved by hand, the integration test above holds.

  **Reopened and closed again by PL-Q197, 2026-09-04.** "Bounded and
  independent of run length" was true of the *payload* and false of the
  traffic. Bounding how many points are drawn does not bound how many of them
  *move*, and the selection was re-derived per frame against a sample count
  that changed per frame, so every drawn point took a different sample every
  frame: about 2 700 patch operations where 24 had been enough, stepping up
  the moment decimation engaged at 30 s of runtime. Measured on the recording
  connection, the client was sent some 18 000 control mutations a second - only
  ~50 kB, so the cost was the count and not the volume - which saturated the
  Flutter process while Python sat under half a core, and left slider readouts
  queued behind a backlog that never drained. Buckets are now anchored to
  absolute sample index; the per-frame count is what
  `test_a_growing_run_does_not_grow_the_traffic_it_sends` holds.

  **Reopened once more and closed by PL-D9WD, 2026-09-04.** The traffic was
  then bounded and the *work* was not: anchoring fixed which samples a frame
  chooses, but choosing them still meant one pass over every sample the
  window spans, and the settled scale list reaches twelve hours. Measured
  over the whole chart frame - six traces plus the wash-in plot - 1.9 ms at
  five minutes, 23.8 ms at an hour and 431 ms at twelve, against a 200 ms
  frame budget. Three separate passes made that up and all three are gone:
  the window copied its samples out, each trace built a list of one field
  per sample, and the wash-in plot reclassified every visible sample against
  its domain. The run is now stored by quantity with a dyadic ladder of M4
  aggregates over each, so a frame reads a few hundred completed aggregates
  and touches raw values only at the two unaligned ends of the window: 1.7
  to 3.4 ms at every width from five minutes to twelve hours, flat. What
  keeps it flat is `test_reading_a_window_costs_the_same_however_wide_it_is`
  and `test_a_frame_never_materializes_the_window_as_rows`; the second is
  there because rows are the obvious shape to reach for and one use of them
  anywhere in a frame puts the whole cost back.

## Open thread: the v0.2.8 gate's membership test - PL-MGNC, PL-H8MQ, PL-HXYY

**What the gate's admission test actually is** (project owner, 2026-08-31).
The frozen list is a *scope*, not a set of items: a finding is inside it if it
contributes to the goal the release states — a low-friction workflow before
the two long milestones are run through it — and outside it if it is a
different goal. `ROADMAP.md`'s "What the freeze closes, and what it does not"
now carries that test, with the two limits that keep it from reopening the
list for everything: the finding must be a **defect** in machinery the goal
names, and it must be **workable in this tree**.

Why it needed writing down: the paragraph previously offered only two
dispositions, "new scope" and "completes a frozen entry", and a finding that
was neither went to the queue. The nine captures triaged on 2026-08-31 were
all triaged that way and all excluded, each with a correct answer to the
completion question. Seven of them were defects in the session-start digest,
the release script, the merge path and the lint gate — the machinery the
release's own goal enumerates — and are now entries. The reassessment did not
change intent; it recorded a test that was being applied from memory in one
place and from the written rule in another.

**The two excluded, and why.** `PL-KKX4` (a web session started with no
checkout) fails the workable-here limit: its cause is outside the repository
and its own `not-delegable:` field says the only action available is to record
a second sighting, so it would hold the gate open indefinitely. `PL-SRCP` was
dropped at triage as a duplicate of `PL-3CBS`.

**Two more admitted on the same reading, 2026-08-31,** bringing the list to
thirty-two entries with eleven open. `PL-MGNC` was found while reassessing: a
shallow clone's incomplete `^base` walk made the digest report twenty-seven
ids in flight, eighteen of them closed and one of them `PL-NSN9`, an open
entry of this gate. `PL-3CBS` (docket has no way to notice that an open item's
work already landed on main) was not one of the nine and qualified on the same
reading.

**The `vcs.py` cluster is one piece of work, not three.** `PL-CPSY`,
`PL-S1P1` and `PL-MGNC` are three holes in `branches_in_flight` and its return
value — a stale ref never excluded, the unreadable refs dropped from the ids,
and a walk that under-excludes when the merge-base resolves but the history
does not reach it. They collide on `touches` by construction. Taking them
together is one design pass over that function; taking them separately is
three, each invalidating the last.

**`PL-CPSY` landed on its own, 2026-08-31** (pull request 121), so the cluster
is two. The stale-ref hole turned out to be separable: it is answered before
the commit walk, by asking whether every blob a candidate ref adds has been on
the default branch's history, so it changes which refs reach the walk and not
how the walk reads them. `PL-MGNC` (the `^base` walk under-excludes in a
shallow clone) and `PL-S1P1` (the unread refs never reach `docket next`) are
still one pass: `PL-MGNC`'s fix is to stop trusting a walk the history cannot
support, which means marking those refs unreadable, which is the value
`PL-S1P1` is about carrying to the callers.

Worth knowing before that session starts: the incident `PL-MGNC` records -
twenty-seven ids in flight, eighteen closed - was produced by
`origin/claude/roadmap-release-write-failure-nhsjwo`, a squash-merged ref that
`PL-CPSY` now excludes before the walk begins. So the observed symptom is
gone, and reproducing `PL-MGNC` needs a ref that is genuinely unlanded *and* a
clone truncated below its fork point.

**`PL-MGNC` landed on its own too, 2026-08-31** (pull request 122), so the
cluster is one. It also separated, the other way round: its fix is inside the
walk - a walk must stop against a commit the default branch accounted for,
never because the checkout ran out of history, and the commit with no parents
such a walk ends on is the signature - while `PL-S1P1` is about the callers
that never see the refs it declines. Neither needed the other's lines.

The reproduction the note above asked for is `_shallow_pair` in
`test_cli.py`: real git, the default branch fetched to a depth that leaves it
grafted and the branch fetched past that graft, which one merge of the default
branch into a branch is enough to reach round. That merge is the ordinary
shape here, because resolving a conflict leaves one behind.

`PL-S1P1` (the unread refs never reach `docket next`) is now worth more than
it was, and that is `PL-MGNC`'s doing: `unreadable` has two ways of filling
rather than one, so the half of the answer `in_flight_ids` discards is a
larger half. `PL-YSXF` (a ref named as unread loses the id its own branch name
carries) is the same hole seen from inside `branches_in_flight` and was
captured in the same session; the two are one pass.

**`PL-S1P1` landed, 2026-08-31** (pull request 123), and it closed as a type
change rather than a line of output: `in_flight_ids` is gone, `FlightReport`
carries an `ids` property, and the six answers that rank or mark against
in-flight work take the report. The gap now travels with the answer instead of
being dropped at the boundary, which is what stops the next caller re-opening
it. `_flight` also stopped resolving its root with `find_root()` while every
other command resolved it from the store.

`PL-YSXF` is what is left of the cluster, and it did *not* come with
`PL-S1P1`: this pass carried the gap to the callers, that one narrows the gap
itself - a ref whose *name* proves an id needs no history at all, and the name
loop never sees it because `unreadable` is filtered out before it runs. It is
still the cheapest thing to do next in that function, the design pass over it
having just been paid for. It is untriaged and was captured after v0.2.8's
freeze, so admitting it is a decision rather than an assumption.

**`PL-YSXF` was admitted and landed the same day, 2026-08-31** (pull request
124), at the project owner's direction, in the session that had just closed
`PL-S1P1` and still had the function loaded. That closes the `vcs.py` cluster:
four holes in `branches_in_flight` - a stale ref never excluded, a walk that
under-excluded, the unread refs dropped before the callers, and the name read
discarded with the commit read - none of which needed another's lines, and all
four found within two days of each other because each fix made the next one
visible.

What is left of that function is `PL-W1LN` (the parentless commit is the
signature of every shape observed, not a proof that a walk is complete), which
is a different question: the guards decide *whether* to believe a walk, and
that one asks whether the signature they key on is sufficient. Nothing in the
cluster's four fixes bears on it.

**The membership test was applied to the whole open queue on 2026-09-01,** not
only to new captures, which is what this thread was for. Eight untriaged items
were triaged and every open item was read against the two limits. Five were
admitted, taking the list to thirty-seven entries with eleven open: `PL-3576`
(`docket check`'s offered-item advisory reads a flight answer that may be
partial), `PL-1Q3S` (a merged pull request's stale tracking ref makes the stop
hook demand a push), `PL-RWZV` (the brief check passes an empty section),
`PL-H8MQ` (the entry count is stated in six places and held to none) and
`PL-HDY6` (the scope reader counts a mention as membership).

`PL-HDY6` was found *after* the first four had merged, while verifying the gate
state on `origin/main` - `bin/docket next` ranked `PL-68XK` second with the
reason "In scope for v0.2.8", read out of the paragraph in that section which
says `PL-68XK` is not admitted. It is the only one of the five that was
misdirecting the ranking on `main` rather than costing a correction later, and
it is worth noticing that the pass which wrote the exclusions down is what made
the reader mis-place them: the more carefully this project records why an item
is *not* an entry, the more ids `Scope.placement` counts as one.

Three exclusions are worth recording because each names a boundary the test
draws:

- **The delegation gate is not named machinery.** `PL-L9JS` (eight open items
  carry a `verify:` command that passes without their work) and `PL-MZH2`
  (`PL-D9H6`'s command is quoted so a shell cannot run it) are both real
  defects in `docket verify`, and `docket verify` is not one of the six pieces
  the goal enumerates. They are queue work, not gate work, and `PL-L9JS` is
  cheapest paid per item as each is started.
- **An improvement to correct behaviour is not a defect in it.** `PL-K2ZK`
  (deepen the clone so the in-flight read answers) and `PL-01CK` (the content
  test's walk cost) both ask machinery that works to work better. `PL-MGNC`
  made the declining answer correct deliberately.
- **A recorded limit is not an observed misfire.** `PL-W1LN` stays out: its
  own **Done when.** allows the answer that the topology cannot be produced
  here, and an entry that may turn out to be undemonstrable cannot be one a
  release waits on.

`PL-Y08X` was dropped as a duplicate of `PL-D2GW`, its measurement folded in.
`PL-3CBS` was closed: its work merged as pull request 128 and the status was
never set, so the gate had been reporting seven entries open when it was six -
found by the check `PL-3CBS` itself added, on its first run against the store.
`PL-T63T` (half the recorded `commit:` hashes resolve nowhere) is excluded on
the precedent `ROADMAP.md` already records for `PL-68XK`, and the two are one
decision: what the field should mean under squash-merge, then what should check
it.

**`PL-HDY6` closed 2026-09-01 (pull request 131), and the rule it settled is
worth writing down because every future milestone section is written against
it.** A section places an id from two structures and nothing else: the frozen
list, read by its *entries' heads*, and `Required scope`, read whole.
Everything else - goal, definition of done, commentary on an entry, exclusion
paragraph - is prose and places nothing.

The brief's obvious candidate, "read the section's lists and ignore its
paragraphs", does not fix the case that found the defect: `PL-68XK` is also
named mid-entry inside the `PL-HDY6` bullet, so a bullet-wide read still counts
it. Reading the list by its entries' heads is what handles that, and it costs
nothing because `_gate_entries` already read it that way - the two halves are
now the same parse rather than two that could drift. The other candidate, a
marker a writer adds to an exclusion, was rejected because `doc_check` cannot
tell an exclusion from a mention and so could never hold anyone to it: a
convention with no check behind it fails in exactly the way the defect did.

What follows for whoever writes the next section: **scope written only into
prose is placed nowhere.** Print the id inside `Required scope` to place it.
v0.4.0 was already paying that - its gate prose said `PL-VM40`, `PL-F52R` and
`PL-ZRSP` "appear in Required scope above" and their ids did not, so those
bullets now print them. `PL-D1ST` captures the rest of that subsection, where
bullets describe queue items whose ids appear nowhere in the file at all
(`PL-SN2C` is the clearest). `PL-6P9Y` captures the one exclusion that *is*
decidable and is still read as silence: an `Explicitly out of scope` heading
means exclusion as plainly as `Required scope` means membership. Both are queue
work rather than gate entries - an improvement to correct behaviour, and
roadmap content rather than machinery.

## Open thread: playback speed (target: real-time up to ~120x and beyond, "like Gas Man") - PL-009

Not scoped yet. The performance blocker this waited on has landed: render
cadence is now independent of simulation cadence, and frame cost no longer
grows with run length, so a multiplier no longer multiplies a growing
bottleneck.

What a speed multiplier now costs is bounded and known. Stepping the model
is nearly free (~0.011 ms per step, flat), so going faster means calling
`advance()` more times per render tick rather than rendering more often. A
frame currently costs ~17 ms of which ~15 ms is chart-point construction, so
PL-010 (point reuse, measured 20x cheaper) is the headroom to spend if a
high multiplier makes the render rate the constraint again.

Half of this is now decided rather than open. PL-VP7N put the operator
split's applicability domain in the core as `MAXIMUM_SIMULATION_STEP_S`, and
a step above it is refused, so the multiplier cannot be a larger step even
if someone wanted it to be: it is steps per tick, and that is enforced
rather than merely written down. What "a larger step is a model-fidelity
question" was pointing at has an answer - `docs/MODEL.md` § "Supported
simulation step" - and the answer is that the supported step and the shipped
step are the same number.

Still undecided, and the reason this stays `needs-decision` rather than
`ready`: how the multiplier is exposed without creating a hidden mode - a
learner who does not notice a 120x setting will misread the time axis
entirely. Being an `L`, it needs scoping into a `ROADMAP.md` milestone
before implementation.

## Open thread: what the v0.2.0 architecture review left behind - PL-024, PL-6GS0

An independent architecture review of the v0.2.0 baseline (commit `3251ebf`)
reported 21 findings and shipped an executable harness under `tools/` rather
than a prose write-up alone, so that every numeric claim could be re-run
instead of trusted. Eight findings had a crisp programmatic reproduction; the
rest were design, presentation and documentation judgements a script cannot
adjudicate.

**The harness is retired** (PL-STNV, 2026-08-30). Seven of its eight defect
checks reported FIXED and each is a closed item: `P1-1` PL-018, `P1-2` PL-015,
`P1-3` PL-017, `P1-4` PL-021, `P1-5` PL-016, `P1-6` PL-022. The eighth, `P2-1`,
had two halves and both are closed - the step-size half by PL-VP7N's
applicability-domain guard, which now refuses the coarse step the check itself
used and so stops it running at all, and the mass-balance half by PL-023's
independent RK4 oracle. Its three physics checks were CONFIRMED and two of
them are now release gates in `tests/reference/test_coupled_dynamics.py`. What
was left was a second verification path for checks the reference suite already
makes, plus a script reporting a defect nobody could act on because it was
never in the queue - which is worse than no harness, because it looks like
tracking. Recover it with `git log --diff-filter=D -- tools/review-verification`
if a claim ever needs re-running.

That mass balance cannot detect a wrong *rate* is not a defect and will not
be re-found: it is a standing property of equal-and-opposite accounting,
recorded in `docs/MODEL.md` § "Selected method (as implemented)" and gated by
the independent-solution test beside it.

**PL-024 - the venous pool's grip on the first minute.** The one check that
still reproduced at retirement, and a documentation and presentation gap
rather than a defect: 1.0 L is the Gas Man reference value and is cited twice
in `reference_adult.json`, so the number is the one the reference
implementation uses and its meaning is unstated. (Amended 2026-09-03: this
originally read "so the number is right", which is the inference
`docs/MODEL.md` § "Source hierarchy" now forbids — a tier-3 citation says
what a program runs on, not that a value was measured. `PL-6Q8N` carries the
sourcing question for this parameter and the other ten.)
Its mixing time constant is 60 - V/Q̇ = 12 s at the reference 1.0 L and
5 L/min, which dominates the displayed mixed-venous value early in wash-in.
Measured against a near-instant 0.01 L pool, sevoflurane at 5% delivered:

```text
t=  30 s   pooled 0.00013   near-instant 0.00030    -55.5%
t=  60 s   pooled 0.00100   near-instant 0.00152    -34.5%
t= 120 s   pooled 0.00482   near-instant 0.00582    -17.2%
```

**PL-6GS0 - the exact-step question.** The review's central architectural
recommendation was that the coupled system is linear and time-invariant within
a step, so one matrix exponential is exact where the pairwise split is
$`O(\Delta t)`$. The review itself deferred it in favour of promoting the RK4
oracle into CI, which landed as `tests/reference/test_coupled_dynamics.py`. The
measured comparison it rests on is carried in the item rather than here, since
the harness that produced it is gone.

**Revisited and reversed, 2026-09-03** (project owner). The deferral stood for
three releases and this note said so; it no longer does. `PL-SPMQ` measured what
the split costs a *reader* rather than what it costs the numbers, and the
project owner chose the exact matrix exponential on that ground - `ROADMAP.md`
planned-milestone item 29's bar is that a reviewer follow `core/` without a
lookup table, which the five composed sub-steps prevent. `PL-GS5X` makes the
change in v0.4.1, `PL-P0BB` settled the state vector as fractions, and `PL-X9KD`
re-derives every published statement the splitting error justified.
`docs/MODEL.md` § "Selected method (as implemented)" carries the supersession
(`PL-B875`).

It bears on the playback-speed thread above, and the bearing has now changed
direction: an exact step makes a larger step a fidelity-free choice, which is
exactly what that thread assumed it was not. The conclusion survives anyway -
the multiplier stays steps-per-tick and the step stays 0.1 s - but for
determinism rather than for accuracy, which is the ground `docs/MODEL.md`
already gave and which `PL-SN2C`'s brief has been moved onto.

## Open thread: scenario branching, bookmarks, and what a snapshot is for - PL-DHV7, ROADMAP items 8, 11, 12 and 26

**Where the work went, 2026-08-25.** Triaged after capture. Only PL-DHV7
(MAC as a displayed unit) is startable against the code as it stands and
stays in the queue. The other four items named below were promoted into
`ROADMAP.md`'s planned milestones and dropped from the queue, each with its
reason recorded in its file: PL-WRKL into item 8, PL-RRWV into items 11 and
12, PL-JW30 into item 12 as a required property, PL-PFM1 into item 26 as one,
and PL-X9R0 into item 26 itself. The measurements and reasoning below are
what those roadmap entries were written from, and are kept here because a
scoped milestone will need them again. The thread stays open until item 26 is
scoped.


Raised by the project owner 2026-08-25, as context behind an earlier
suggestion (from a different assistant) that the simulation store periodic
history snapshots. Captured here because the mechanism and the goal came
apart on inspection, and the reasoning should not have to be re-derived.

**The goal.** Compare two managements of the *same* case without rebuilding
the case. The owner's worked example: run three simulated hours, then wake
the patient by turning the vaporizer off and coasting on low flow for fifteen
minutes before opening the flows, and watch what the vessel-rich group does.
Then go back to just before the coast, branch, and instead hold 0.5 MAC on
normal flows until 3:15 before turning everything off - and compare time to
the wake-up threshold. Same case, one variable, two curves. The wash-in
equivalent is the same shape: branch at t=0 and compare low-flow/high-dial
against high-flow/maintenance-dial.

**How the owner expects it to be driven.** Bookmarks, in the Gas Man sense:
set a target - an absolute simulated time, or a monitored concentration
crossing a threshold ("VRG reaches 0.8 MAC") - run at high playback speed,
and the run halts there. Build the case as a sequence of bookmark-to-bookmark
fast-forwards, and branch at a bookmark. Branching from an arbitrary
mid-interval time is the rare case, not the normal one. Sub-forks of forks
are explicitly out of initial scope: one trunk, N branches off it.

**The mechanism that was proposed, and why it does not survive contact.**
Snapshot at fixed intervals; to reach an arbitrary point, restore the nearest
prior snapshot and resimulate the remainder. The stated aim was to avoid
duplicate simulation time - "storage rather than resimulation". Three
measurements, taken 2026-08-25 against the code as it stands, put that
trade-off somewhere other than where it was assumed to be:

- *A snapshot is nearly free.* The complete dynamic state is six
  concentrations (circuit, alveolar, mixed-venous, VRG, muscle, fat) plus
  `elapsed_s` and the four control settings. That is about the size of one
  `SimulationHistorySample` (88 B as an object). Snapshot density is not a
  cost worth optimizing at this model size.
- *Resimulation is nearly free too.* `SimulationState.advance` measures
  8.9 us per 0.1 s step. Reconstructing a 3-hour run from t=0 costs about
  1 s; 24 hours about 8 s. The interactive case the owner described would not
  perceptibly benefit from a snapshot at all.
- *The per-step history is the expensive thing.* 36 000 samples per simulated
  hour, ~88-256 B each: single-digit MB per hour, ~2.3-6.6 GB at the 30-day
  run-time cap the owner is considering. That is PL-011, and it is the
  storage question that actually needs an answer.

So the snapshot-interval design optimizes the cheap axis. It is not wrong,
it is just not where the constraint is.

**Re-measured 2026-09-05 (`PL-8GLL`), and two of the three numbers above have
moved.** They are left standing as the dated record of what the 2026-08-25
reasoning was done from; these are what the same quantities measure against
the code as it now stands, after `PL-D9WD` replaced the per-step list of rows
with per-series arrays and a dyadic aggregate ladder, and `PL-W3DD` re-keyed a
row by substance.

- *A snapshot is still nearly free, and it is now a built thing rather than a
  size estimate.* `AgentUptakeSystem.capture_state()` returns an
  `AgentUptakeSystemState`, which is the six concentrations *plus* the
  validator's three accounting totals - so a restored state resumes the
  mass-balance identity rather than restarting it. The bullet above was right
  that snapshot density is not worth optimizing.
- *Resimulation costs about twice what the bullet says.* `SimulationState.advance`
  measures **18.4 us per 0.1 s step** (200 000 steps in 3.67 s), not 8.9 us.
  A 3-hour run reconstructs from t=0 in **2.0 s** and 24 hours in **15.9 s**,
  against the 1 s and 8 s above. The conclusion survives the correction: 2 s is
  still imperceptible for the interactive case the owner described.
- *The per-step history is still the expensive thing, and it is now measured
  rather than estimated: **127.9 B per sample**, one substance.* Not the
  `~88-256 B each` above, which sized a `SimulationHistorySample` object that
  is no longer what a run retains. Measured by `tracemalloc` over a recorded
  run, marginal between 100 000 and 200 000 samples so the fixed overhead is
  out of it. **Half of it is the ladder, not the samples**: 64.0 B is the
  elapsed array plus seven series' `array("d")` of values, and the remaining
  63.9 B is the M4 aggregates over them. That split is what `PL-011` turns on -
  evicting raw samples once consolidated removes 64 B of 128 B and leaves a
  cost still linear in run length, so it is a factor of two rather than a
  bound.

At 127.9 B per sample and the fixed 0.1 s step, one substance: 4.6 MB per
simulated hour, 0.11 GB per simulated day, 0.77 GB per simulated week, and
**3.3 GB at the 30-day cap** - half the 6.6 GB the bullet above projected, and
still a bound in name only. The rate that matters for a session left running is
**1.38 GB per wall-clock hour at the 300x maximum playback rate**
(`app/playback.py`'s `SUPPORTED_PLAYBACK_RATES`), which is what makes this
reachable by accident rather than only by a 30-day run nobody would sit through.

**What the mechanism was missing.** Resimulating from a snapshot to an
arbitrary later point requires re-applying the control inputs over that
interval - and nothing currently records them. `SimulationController` records
concentrations, never the fresh-gas-flow, vaporizer, ventilation, or cardiac
output changes that produced them. Without that timeline the fallback path in
any interval-snapshot scheme cannot be built, and neither can replay or
export-with-provenance. `ROADMAP.md`'s planned-milestone order already
encodes this - scenario events (8), save/load (9), replay (10), comparison
(11), forking (12) - which is worth knowing before anyone reorders it.
Recorded as PL-WRKL, now `ROADMAP.md` item 8.

**Two correctness traps, recorded so they are not discovered late,** and
now carried as required properties of the roadmap items they constrain.
PL-PFM1 (item 26): a threshold bookmark must be tested every simulation step, not once
per rendered frame, or it overshoots by a speed-dependent amount and halts at
a concentration other than the one asked for - which also makes any branch
taken there unreproducible. PL-JW30 (item 12): a branch created by resimulation while
its parent was simulated straight through can diverge from the parent
*before* the branch point by floating-point rounding, which is precisely the
divergence a strategy comparison is meant to rule out; it is a required
property of item 12.

**Bookmark set, settled 2026-08-25.** The owner names the reference
simulator's two kinds as the floor: absolute time points, and percent of MAC
on *every* graphed compartment - circuit, alveolar, VRG, muscle, fat, venous -
not the alveolar trace alone. The vendor documentation could not be checked
from the capturing session (gasmanweb.com and its help mirror are both
refused by the environment's network egress policy), so this is recorded as
the owner's account rather than as a citation. Full detail in PL-X9R0, now `ROADMAP.md` item 26.

That answers the MAC question by forcing it: MAC-per-compartment bookmarks
cannot be built while MAC is internal-only, so making MAC a displayed unit
(PL-DHV7) moves from "someday" to a prerequisite. Its hard part is not the
division - it is that a MAC multiple on a tissue compartment asserts
something narrower than it appears to, and the label has to say which.

## Aspirational: power-user custom agents (not scoped, not started)

The project owner's stated future direction, raised while discussing
whether `core/parameters.py`'s `AGENT_DATA_FILENAMES` dict should stay a
hardcoded enumeration of built-in agents (decision: yes, for now - see
that conversation's reasoning; a directory-scan loader alone wouldn't
give power users this anyway since it only reaches packaged files).

The idea: eventually let power users (e.g. for research use) add their
own custom agent parameter sets, analogous to how 3D-printer slicers
handle filament profiles - built-in presets, "duplicate an existing
profile and modify it," and "create from scratch," gated behind an
explicit warning since these aren't the vetted built-in agents.

Not scoped or designed. Key considerations for whoever scopes this,
noted now so they aren't lost:

- **Provenance/trust must stay visible everywhere the agent appears**
  (dropdown, header, charts, any export) - a custom agent has none of
  the peer-reviewed citation backing the built-in `sources` field
  requires, and presenting a user-authored curve with the same visual
  authority as a cited built-in one would violate this repo's
  presentation-correctness standard (CLAUDE.md). Likely needs a
  first-class "verified built-in vs. user-supplied" distinction in the
  data model itself, not just a UI label bolted on after the fact.
- Storage has to live outside the installed package - `core/parameters.py`
  currently only loads via `importlib.resources` against packaged
  `data/agents/*.json`; custom agents need a separate on-disk location
  (e.g. a user config directory) and their own load path.
- The existing Pydantic validation (ranges, required fields, rejection of
  keys the schema does not declare, the
  mac_percent <= max_delivered_concentration_percent cross-check) should
  still apply to custom agents - it catches structurally invalid data
  (typos, absurd values) even though it can't and shouldn't try to
  verify real-world plausibility the way a citation does.
- "Duplicate and modify" falls out naturally once custom-agent storage
  exists, since every built-in agent's JSON is already fully
  self-contained - cloning one as a starting point is close to free.

## Shelved: UI structure/form mockups

Explored, then explicitly shelved (project owner's call) in favor of
maturing the scientific core first. Do not resume this without the
project owner asking again.

What happened: three static wireframe directions were built as a Claude
Design canvas artifact (today's screen recreated faithfully, a
"vitals-first" restructure, and a zoned Inputs/Monitor/Diagnostics
layout) — https://claude.ai/code/artifact/cb5e540b-5e87-4812-ae29-ec2d1a45ef5e.
The project owner's assessment: the current v0.1.0 interface is
intentionally minimal ("hello world"), and the three mockups were just
better-organized versions of that same shallow functionality. A mature
UI cannot be designed on top of functionality this early — see "Long-term
vision" below. The artifact link is kept here only as a record of what
was tried; it is not a starting point to resume from, since real UI work
later should be informed by whatever the scientific core looks like at
that point, not by these sketches.

## Long-term vision (aspirational north star, not a scoped milestone)

The project owner's stated ambition, for future planning only - explicitly
not to be turned into near-term scope or used to justify any UI work now:
something with the scientific credibility of Gas Man (gasmanweb.com, the
flow-limited mammillary uptake/distribution model this project's own
sevoflurane/patient parameters are already drawn from) combined with
SimTiva (simtiva.app, an open-source TIVA/TCI simulator built on
STANPUMP/Shafer PK-PD - effect-site concentration, Cp/Ce target-controlled
infusion, propofol-opioid interaction) - at a level of execution and
interaction quality neither reference tool actually has, phrased by the
owner as "what version 18 would look like if version 6 incorporated
SimTiva functionality" against Gas Man's real-world v4.x.

Concretely, this points at IV/TIVA pharmacokinetic and effect-site
modeling integrated with the existing inhaled-agent model. That is not a
new idea - it is already `ROADMAP.md`'s "Planned milestones" item 13 ("Add
IV pharmacokinetic and effect-site models, after item 12 (simulation
forking) is available"). The vision here is the same destination with much higher
ambition on execution and UX quality, and possibly a different order,
not a different target.

Explicit sequencing principle from this discussion: UI/UX ambition
follows scientific-core maturity, not the other way around. High
production values on top of a not-yet-validated model would be a worse
outcome than the current honestly-minimal interface, not a better one -
consistent with `CLAUDE.md`'s standard that presentation polish must
never imply more certainty or completeness than the model actually
supports. This vision should only move into `ROADMAP.md` as a real,
scoped milestone (goal, required scope, definition of done, explicit
out-of-scope list) once the project owner is ready to schedule it - not
before.

Also noted, further down the road than the above: mature figure export -
generating a publication-quality static graph from a simulation run, of
the kind someone would put in a paper, as opposed to the live interactive
dashboard chart. This implies its own rendering path (vector/high-res
output, print-appropriate axis and label sizing, customizable styling)
separate from the Flet live chart, and - per the same presentation-
correctness standard above - exported figures should carry the model
name/version, parameter provenance, and units they were generated from,
not just the plotted curve. Aspirational only; not scoped.

## Open: when a session may fix a small finding instead of filing it (PL-3MJH)

`CLAUDE.md`'s capture bullet exempts a finding "identified in a session **and
not fixed in that same session**", but no instruction anywhere says when a
session may enter that exemption. It is therefore dead text, and every session
captures - so a two-line typo fix costs a `docket new`, a five-field triage
slot, a hand edit to close, and a queue line read past until it closes. The
design that closes this is worked out in full in `PL-3MJH` (three mechanical
tests, a two-per-branch cap, the fix recorded as its own commit under the
current item's id). It is not built: the project owner judged it too
complicated to land now and deferred it.

Two things from that discussion are worth having here rather than in the item,
because they bear on decisions beyond it.

**Gate placement, and the precedent it did not set.** The case was made that
this belongs on v0.2.8's frozen list: a defect in machinery that release's Goal
already names ("the instructions a session reads before it does anything
else"), present before the 2026-08-30 freeze, and prose-only so it does not
trip the "new tools, better tools" exclusion at `ROADMAP.md`'s "Explicitly out
of scope for v0.2.8". The project owner declined, directing it to "the next
gate or two" - Gate 0 (under v0.4.0) or Gate 1. The reasoning stands and the
placement did not: a release 6 entries of 38 from done is the wrong place for a
design still being argued, whatever the scope test permits. Future admissions
to a nearly-cleared frozen list should weigh how settled the design is, not
only whether the scope test admits it.

**The narrow rule beat the cited source.** Martin Fowler's *Opportunistic
Refactoring* (martinfowler.com/bliki/OpportunisticRefactoring.html, 1 Nov 2011)
was supplied and read in full. It argues for a wider remit than `PL-3MJH`
adopts - fix regardless of locality, add a test or two if needed, judge for
yourself when to stop. `PL-3MJH` diverges on all three, deliberately, and
records why: this project has a working queue, so Fowler's "another day often
doesn't come" does not hold; `bin/docket verify` audits a diff against an
item's declared `touches`, so ignoring locality corrupts the audit; and
"knowing when to call it a day" is the judgement an agent session is likeliest
to rationalise past, so it is a hard count instead. Fowler's own test for
whether this work is worth doing at all is met: "be aware of any time you feel
discouraged from doing a small refactoring... Any such barrier is a smell that
should prompt a conversation."

## Open: the project's one-line self-description (PL-4MHK, PL-N092)

The GitHub repository's "About" description is empty, and the project has no
settled one-line statement of what it is. Three rounds of drafts were reviewed
on 2026-09-01 and every one was rejected; the wording was deferred rather than
decided, so nothing from that discussion is an approved form of words.

**What was tried, and why each direction failed.** Recorded so the next
attempt starts past these rather than at them.

1. *Feature-dense.* Drafts naming the compartments, the three agents, and the
   live-adjustable settings. Rejected as reading like a keyword list rather
   than a sentence - the same failure `PL-N092` records for `README.md`,
   arriving at one-sentence scale.
2. *One plain sentence built on a verb*, following the vapor from the
   vaporizer into the patient and back out again. Closer on register, rejected
   on accuracy: it describes only what runs today, which frames the project as
   a volatile-agent simulator when that is the current build rather than the
   goal.
3. *Destination plus current state* - naming anesthetic pharmacology broadly,
   or the case-comparison MVP, with the volatile-only present marked as such.
   Also rejected; no further reason was recorded.

**Constraints any future draft has to meet.** None of these was the reason a
draft was rejected, so they are floors rather than the unsolved part:

- The educational-only limit belongs in the description itself, not one click
  away in `README.md`. That field is often the only sentence read before an
  impression forms, which puts it inside `CLAUDE.md`'s presentation-
  correctness standard.
- Anything claimed as planned must match `ROADMAP.md`. Intravenous agents are
  planned-milestone item 13, sequenced after simulation forking and therefore
  after the MVP, so "planned" is accurate and "soon" is not.
- GitHub's field holds 350 characters. Every draft so far fit inside 270, so
  length has never been the binding constraint.

**Related, and the order to take them in.** `PL-N092` rewrites `README.md` as
a human-readable introduction and settles the same register question at length
and with room to get it right; a one-liner is easier to derive from a finished
README than to invent alongside one. `PL-4MHK` carries the package-metadata
half - `pyproject.toml`'s vague `description` and its absent `classifiers` -
and says the same thing about sequencing. Repository topics were proposed in
the same discussion and not applied; they are independent of the wording and
can be set whenever.

## Settled: `.claude/rules/` path globs are unanchored - PL-ZQ35, PL-H588, PL-LLWN

Measured on 2026-09-05 while closing `PL-ZQ35`: a `paths:` entry in a
`.claude/rules/*.md` file matches its name at **any depth** unless it begins
with `/`, and `./` matches nothing at all. `PL-LLWN` carries the table. The
probe was throwaway rule files and target files at the repository root and
under `subprojects/docket/`, run because no documentation states the
behavior - the published description settles only *when* a path-scoped rule
fires (on a read), not *what* its glob matches.

**Why these are one pass rather than three findings.** Every rule's glob was
written as if it were relative to the repository root and none of them is, so
they fail together and for one reason. They differ only in how visible the
failure is today:

- `PL-ZQ35` (closed) - `readme-hold.md`'s `README.md` against three files of
  that name. The collision was already real: the freeze was loading on the
  queue tool's reference manual, alongside `apparatus-standard.md`, whose own
  text says every sentence of it is wrong when applied to a `README.md`.
- `PL-H588` (dropped) - `expert-review.md`'s `src/**` and `tests/**` reached
  `subprojects/docket/src/` and `tests/`, so the simulator's specialist
  standard loaded on the apparatus: `PL-6SBB`'s leak running the other way,
  with the tie-break in `CLAUDE.md` ("the simulator wins") resolving it the
  wrong way there. Overtaken the same day by `PL-WWDT`, which deleted that
  file's `paths:` outright - see the thread below.
- `PL-LLWN` - the class fix, and a check holding every entry to a leading
  `/`. The remaining globs match one file today and widen silently the moment
  a second file of that name appears, which `subprojects/` exists to make
  likely.

**Closed 2026-09-05.** `PL-LLWN` added `tools/rules_paths_check.py`, wired
into `make check` and CI's `floor` job, and anchored the nine entries that were
still bare. The rule is exact - every `paths:` entry begins with `/` - so it is
a hard error, and the message names the replacement spelling rather than only
the offence. The `./` row above is called out separately in it, since "add a
leading slash" reads as cosmetic against an entry that matches nothing.

`PL-DNYL` closed the same day, adding the second rule: an anchored entry whose
literal prefix resolves to nothing is a rule that silently never fires, and the
tree answers that outright. The project owner settled the question it hung on -
a rule may not declare scope ahead of the code it governs, so it is an error
rather than an advisory. The message names the nearest existing ancestor, which
is what turns a transposed segment from "this path is wrong" into "it stopped
being real here".

What the check deliberately does not do, and this is now settled rather than
pending, is decide whether a glob describes the *right* set of files. That is
judgment, it differs per rule, and a tool guessing at it is the "worse than no
tool" case. Both rules it does carry ask only whether an entry is anchored and
whether it points at anything - one answered by the text, one by the tree.

**Excluded deliberately.** Whether a rule's glob describes the *right* set of
files is judgment, differs per rule, and is the "worse than no tool" case if
scripted; `PL-LLWN`'s check decides anchoring only. `PL-3V4N` is a separate
defect in the same file - a path-scoped rule fires on a *read*, so the freeze
is missed entirely by a session that edits `README.md` without opening it -
and anchoring neither helps nor hinders it.

## Open thread: which moment a rule has to reach, not which tree it governs - PL-WWDT, PL-H588

`PL-WWDT` came out of the thread above and changed how the routing question is
asked here. The globs thread treated `paths:` as a question about *scope* -
which part of the tree a rule governs. The project owner's correction on
2026-09-05 was that the prior question is *when*: "I absolutely want expert
standard to apply in design round as well. That's equally if not more critical
because I'm relying on you to help me decide on best approach to implementation
of my ideas for features."

That is not a scoping preference, it is the four dispositions applied properly.
`docs/resident-instructions.md` already names three moments a path-scoped rule
cannot reach - "receives a request, decides an approach, or writes a reply" -
and its "What stays resident" section had a group for the first and the third
and none for the second. `.claude/rules/expert-review.md`, the file that says
what an approach is judged against, was the one sitting in the missing group.

**The consequence for `PL-H588`, which is why the two threads are one.** The
recommendation this session first made - narrow `expert-review.md`'s `docs/**`
so it stops reaching the apparatus - was wrong, and wrong in the dangerous
direction. `docs/**` matches `docs/items/**`, which was the only way the rule
reached a design round at all; narrowing it would have removed the standard
from the conversation while looking like a tidy-up. A glob that is
over-broad by accident can be doing load-bearing work, and the fix is to
establish the delivery first and scope second, never the reverse.

**What is settled.** Split a rule by the moment it must fire, then scope what
is left. `expert-review.md` lost its `paths:` and is resident; the
code-and-provenance half went to `.claude/rules/sources-and-docstrings.md`,
which fires with a file already open. Resident cost +4721 characters, recorded
in the ledger with the argument.

**Compression: declined** (project owner, 2026-09-05, "leave it"). The
resident half stays as moved - verbatim, +4721 characters. Do not re-open this
as a tidy-up; it was put to the owner with the number attached and answered.

**What is still open.** Whether the scope paragraph now at the top of
`expert-review.md` is enough to keep the specialist standard off the apparatus.
That is the risk `PL-H588` named, and making the file resident makes it larger
rather than smaller: the standard now loads on every session, including one
working only in `subprojects/docket/`. Nothing but practice will say, and the
symptom to watch for is a session over-investing in the apparatus while citing
the right file - which is `PL-6SBB` exactly, in the other direction.
