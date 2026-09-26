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

**`bin/docket show <id>` tells you which thread concerns your work; do not
read this file to find out.** That instruction used to read "read this file at
the start of a task that touches one of its open threads", which cannot be
followed — evaluating the condition means doing the thing it gates, so it
resolved in practice either to reading the whole file every session or to
reading none of it and losing the continuity this file exists for (`PL-7QKY`).
That cost is not static: the file was 34.5 KB when the item was written and is
95 KB now, roughly 24k tokens, against `CLAUDE.md`'s turns-times-context
discipline.

So the discovery is a command now. `show` splits this file at its `##`
headings and prints a `file:line` for each thread naming the id, marking
whether the thread is *about* that item — its heading names the id — or merely
*mentions* it. It says nothing about what a thread contains: whether one is
still true is a judgment, and a generated precis of a stale thread would be
read as current. Follow the pointer, then decide.

**What that asks of a thread's heading.** Put the ids a thread is about in its
`##` heading. Ids in the body are found too, so nothing is lost by forgetting,
but the heading is what distinguishes a thread a session should open from one
that cited the id in passing.

Update the relevant section (not just append) as a thread progresses. Write
entries so a reader with no memory of the originating conversation can act on
them: state facts and decisions, not "the user said" or "we discussed."

When a thread here is fully resolved (implemented, tested, and merged), its
outcome belongs in `ROADMAP.md`/`docs/MODEL.md`/commit history as
appropriate, and its entry here should be deleted rather than left stale.

**`bin/docket check` now names candidates for that deletion, and only
candidates.** One grooming advisory lists each `##` section whose heading says
the thread is open and whose every cited `PL-` id has closed - three of the
four it named when it was built had already been filed as separate items, one
at a time, by six different sessions (`PL-DG84`). Two things follow for
whoever writes here. **Head an open thread `Open thread:` or `Open:`, and a
resolved one with what it resolved to** - `Settled:`, `Decided:`, `Measured`,
`Built`, `Shelved` - because the heading is the half a check can read, and a
live thread headed anything else is one the advisory will never name. And
**the judgment stays with the reader**: whether the outcome is now recorded
somewhere that maintains itself is what decides deletion, and no check will
decide it. A section citing no id is never named at all, direction with no
item being the third thing this file is for.

**The repository's own current state is not a thread here.** It is
`ROADMAP.md` § "Current baseline", which each release rewrites, where a
section here is written once and then describes whatever was true that day.
A `## Repository state as of this writing` section stood at the top of this
file describing the v0.2.0 baseline until v0.5.0, forty releases on
(`PL-DL4M`).

## Open thread: the v0.2.8 gate's membership test - PL-MGNC, PL-H8MQ, PL-HXYY

**What the gate's admission test actually is** (project owner, 2026-08-31).
The frozen list is a *scope*, not a set of items: a finding is inside it if it
contributes to the goal the release states — a low-friction workflow before
the two long milestones are run through it — and outside it if it is a
different goal. `ROADMAP.md` § "What the freeze closes, and what it does not"
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

**Superseded 2026-09-19 by `PL-HWW1`, on the half of the rule above that says
how to place an id.** "Print the id inside `Required scope`" is no longer
enough and is no longer what the parser does: `Required scope` is read from
each entry's `(queue item ...)` slot rather than whole, so **an id cited in an
entry's prose places nothing**. The reason is the same over-read one level
down. Naming the id that re-briefed an entry is how this document records
provenance, so following its own idiom added a member to the release every
time, and the count drifted as the file was maintained correctly - v0.5.0 read
26 ids against its own stated twenty. What a session writing the next milestone
section needs is therefore one sentence: **declare each entry's members in a
`(queue item ...)` slot after its title**, and cite whatever else the prose
wants. `tools/doc_check.py` fails an entry that declares nothing where the
section's other entries declare, so this is no longer a convention with no
check behind it - which is the objection that killed the marker candidate two
paragraphs up. The frozen list is unchanged, still read by its entries' heads.

`PL-6P9Y` closed with it: an id under the **anchor's own** `Explicitly out of
scope` heading is now reported as ruled out rather than unplaced, and sorts
below out-of-scope work. Another section's exclusions stay silent - one the
project has passed says what was true then, and one it has not reached is a
decision that milestone's own scoping round may revisit.

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
lookup table, which the five composed sub-steps prevented. `PL-GS5X` made the
change in the `v0.4.x` track - the track promises no particular patch number,
so it took whichever one it landed on - `PL-P0BB` settled the state vector as
fractions, and `PL-X9KD` re-derives every published statement the splitting
error justified. `docs/MODEL.md` § "Selected method (as implemented)" is
rewritten around what ships; this thread is closed.

**What was actually built, 2026-09-06 (`PL-GS5X`).** Two modules, not one:
`core/governing_equations.py` assembles the system matrix and holds no
arithmetic, `core/matrix_exponential.py` computes the propagator and holds no
physiology. The matrix is 9x9 - the six fractions, the cumulative delivered and
exhausted amounts, and the constant that carries the fresh-gas forcing. Signed
transfers were considered as rows and rejected: they would have cost the matrix
the Metzler property the propagator's nonnegativity rests on, and both are
recoverable exactly from the balances instead.

It bears on the playback multiplier (`PL-SN2C`, shipped v0.4.0), and the
bearing has now changed direction: an exact step makes a larger step a
fidelity-free choice, where the scoping that preceded that item had assumed it
was not. The conclusion survives anyway - the multiplier stays steps-per-tick
and the step stays 0.1 s - but for determinism rather than for accuracy, which
is the ground `docs/MODEL.md` already gave and which `PL-SN2C`'s brief has
been moved onto.

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

## Shelved, then resumed: UI structure/form mockups

**The project owner asked again on 2026-09-08, so the condition below is met
and this thread now lives in `ROADMAP.md`** — Planned-milestone item 33, "Run
the interface pass", with the interface-pass row of "The
timeline" giving it a position - written `v0.5.x` and sitting between v0.5.0 and
v0.6.0 then, and `v0.7.x` sitting after item 34's two releases since 2026-09-16
(`PL-PHKP`). What was decided that
day: the placement above, and that the structural half of an overhaul is not
polish and does not wait for it (`PL-2CS8` consolidates the display constants,
`PL-NGF7` decides the theme object, `PL-B9PY` is the component seam). No design
round was authorised, so the paragraph below still governs the mockups
themselves: they are a record of what was tried, not a starting point.

**The component seam landed on 2026-09-14.** `PL-B9PY` (decompose
`SimulationView` so two runs can be rendered at once) split the class in two:
`RunView` holds one run - its controller, readouts, four settings, transport,
notices and the lines it draws - and `SimulationView` holds what two runs
share, the two charts, their axes, the window both are drawn in, the time base
and the compartment selection. That is the seam the interface pass would
restructure against, and it is the shape `PL-25KS` (port the dashboard to
PySide6) was built to from the start rather than ported into, on 2026-09-15:
`RunView` in `app/run_view.py`, `SimulationView` in `app/simulation_view.py`,
and what either claims in `app/dashboard_frame.py`. Of the
three named above, `PL-2CS8` (consolidate the scattered display constants)
closed in `v0.4.11`; `PL-NGF7` (`contrast_check.py` can see no disabled-state
colour) is deferred to the Qt port, which dissolves it rather than fixing it, and
its expected disposition is `dropped`.

One correction the resumption is worth recording. The assessment below is of
"the current v0.1.0 interface", and it was accurate then; ten interface-changing
releases later it is a statement about a baseline rather than about today, and
quoting it as a live objection would be quoting a stale measurement. What
survives unchanged is the principle in § "Long-term vision" below — UI/UX ambition
follows scientific-core maturity — and that principle is what places item 33
after the MVP rather than before it.

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
UI cannot be designed on top of functionality this early — see § "Long-term
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
new idea - it is already `ROADMAP.md` § "Planned milestones" item 13 ("Add
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

## Settled: when a session may fix a small finding instead of filing it (PL-3MJH)

**Built on 2026-09-07, as designed.** `CLAUDE.md`'s capture bullet had exempted
a finding "identified in a session **and not fixed in that same session**"
while no instruction anywhere said when a session might enter that exemption.
It was dead text, and every session captured - so a two-line typo fix cost a
`docket new`, a five-field triage slot, a hand edit to close, and a queue line
read past until it closed. `CLAUDE.md` now carries the three mechanical tests,
the two-per-branch cap and the recording mechanic (the fix's own commit under
the current item's id), and the `docket` skill's capture mode routes to them
rather than restating them. The design was not widened on the way in.

Two things the build had to settle that the design did not name. The
**housekeeping bullet immediately below** demanded an item for any work taking
a commit of its own, which is the exact shape the new rule prescribes, so both
it and the skill's housekeeping mode carve the admitted fix out on the ground
that rule rests on - the commit still leads with the current item's id, so
every id-matcher still sees it. And **a session holding no item cannot use the
rule at all**, having no `touches` for test 2 and no id to lead a commit;
stated as a consequence rather than as a fourth test. `docs/worker.md` needed
nothing: "Do not start anything not on your list" already denies a delegated
worker this rule.

Two things from that discussion are worth having here rather than in the item,
because they bear on decisions beyond it.

**Gate placement, and the precedent it did not set.** The case was made that
this belongs on v0.2.8's frozen list: a defect in machinery that release's Goal
already names ("the instructions a session reads before it does anything
else"), present before the 2026-08-30 freeze, and prose-only so it does not
trip the "new tools, better tools" exclusion at `ROADMAP.md` § "Explicitly out
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

- `PL-ZQ35` (closed) - the README freeze rule's own unanchored `README.md`
  entry against three files of that name. The collision was already real: the
  freeze was loading on the queue tool's reference manual, alongside
  `apparatus-standard.md`, whose own text says every sentence of it is wrong
  when applied to a README. Both the freeze rule and the root README have
  since been deleted under `PL-WB5K`; the measurement stands, its example
  does not.
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
scripted; `PL-LLWN`'s check decides anchoring only. `PL-3V4N` was a separate
defect in the same file - a path-scoped rule fires on a *read*, so the freeze
was missed entirely by a session that edited the README without opening it -
and anchoring neither helped nor hindered it. It is dropped: `PL-WB5K` deleted
the freeze rule and the README together, so there is no longer a write to gate.
The general form survives it, and applies to any future rule scoped this way.

## Decided: no numpy, and the reason is fit rather than dependency avoidance (2026-09-05)

Raised by the project owner while deciding `PL-011`'s compaction - explicitly
not for its own sake, but to check that avoiding it is not making the work
unreasonably hard. Recorded because the question spans more than one item and
will be asked again.

**The answer is no, and the measurements say why.** numpy is not currently a
dependency, transitively or otherwise: `flet[all]`, `flet-charts` and `pydantic`
are the three declared, and none pulls it in.

- **The read path is already 0.8% of the frame budget, and flat.**
  `select_indices` with the shipped 150-column budget costs 0.22-0.24 ms per
  series - about **1.5 ms per frame for all seven** - and it does not change
  between a 15-minute and a 12-hour window, because `PL-D9WD`'s cache made it
  O(columns) rather than O(window). Against the 200 ms budget there is nothing
  for vectorization to win.
- **The write path is append-dominated, which is numpy's weakest operation.**
  `record()` including ladder maintenance costs 0.46 us per sample per series,
  so **3.2 us per run tick for all seven, against `advance()` at 18.4 us**
  (the operator split's figure; the exact step that replaced it measures 24.6 us
  on the 2026-09-14 container - see the `PL-R460` correction above, which does
  not disturb this bullet's conclusion).
  numpy has no append: the ladder would need hand-rolled capacity doubling, or
  `np.append`, which reallocates and is quadratic. `array` gives amortized
  append for free, so **numpy would make the compaction harder, not easier**.

**The strongest candidate for it is already solved in the standard library.**
`PL-GS5X` (replace the operator split with the exact matrix exponential) was
the one piece of real numerical work in the queue, and its plan was the
~30-line `math`-only implementation in this repository's history at
`git show 475fb92^:tools/review-verification/verify_physics.py` - scaling and
squaring with a 24-term Taylor series.

**What shipped differs from that plan in two ways worth recording**, because a
future reader who follows the history link will not find them there. The series
truncates at 12 terms rather than 24, against a scaled argument bounded at
1/16 rather than the harness's looser bound, with the truncation error derived
(3.6e-26 relative) rather than assumed. And the matrix is shifted before the
series is summed, so every term is nonnegative and the propagator is entrywise
nonnegative in floating point rather than by margin - the property that keeps
an exact step from driving a compartment below zero through a rounding
artifact. The harness had neither.

**The one argument left, recorded rather than settled.** `scipy.linalg.expm`
carries published backward-error analysis (Al-Mohy and Higham 2009) where a
hand-rolled Taylor series carries whatever this project proves about it, and
`CLAUDE.md`'s safety standard prefers validated methods to hand-rolled ones on
a safety-critical path. That is `PL-GS5X`'s call when it is worked - the owner
already chose the exact step with the stdlib implementation named - and it is
not a reason to take the dependency for chart storage.

**Two of its three measurements describe code being deleted, and the
conclusion survives anyway (added 2026-09-05, `PL-VSJZ`).** The read-path and
write-path figures above are `select_indices` and `RunHistory.record`, which
`PL-2FM6` and `PL-8LXM` remove: under `PL-T691` the chart evaluates a closed
form rather than reading back recorded samples, so neither call site exists to
be vectorized. The answer is still no, on ground the note did not have: a
standard-library matrix exponential renders a 600-column frame in 3.3 ms over
a 1 h window and 3.6 ms over 30 days, because chart columns are uniformly
spaced and one exponential serves a whole inter-event segment. That
measurement was taken against a Pade-13 scaling-and-squaring implementation;
what `PL-GS5X` shipped is scaling and squaring with a shifted truncated Taylor
series, which rejects Pade by name for needing a linear solve whose denominator
conditions badly on this system's eigenvalue spread. numpy would win nothing
there either. Kept rather than rewritten: the question is what recurs, and the
note records that it was asked and answered before.

**Re-measured against the shipped propagator, 2026-09-14 (`PL-R460`), and it
is 7.6 ms rather than 3.3 ms.** A 600-column frame over a 1 h window costs
7.64 ms with one inter-event segment and 14.13 ms with five, after that item's
optimizations. The split is 1.3 ms per `matrix_exponential` call and 6.3 us
per `propagate` call, so one segment is 1.3 ms of exponential against 3.8 ms
of column evaluation and each further segment adds its own 1.3 ms.

The conclusion the note drew - that this is not a reason to take numpy - still
holds, and the timing conclusion "a handful of small matrix multiplies per
segment" was right about the shape. What was wrong is the magnitude, by 2.3x,
and it is the magnitude `PL-T691` would be leaning on: 14 ms of a 16.7 ms
frame at 60 fps is not the headroom 3.3 ms implied. The number to design
against is the segment count, since the per-column cost is the smaller half
once there is more than one.

**Not a live question, and that is the answer (2026-09-16, `PL-3SQT`).** The
port changed what this note is about rather than answering it again. pyqtgraph
requires `numpy>=1.25.0` outright, so numpy is installed in every environment
this project has and `uv.lock` names the version - and no module under `src/`
imports it. Nothing is being avoided, and nothing is bending in order to avoid
it: `app/qt_chart.py` hands pyqtgraph `list(...)` because a list is one of the
two types `PlotCurveItem` takes, and producing arrays upstream instead would
recover 0.04-0.14% of a frame (measured 2026-09-16, six traces, three plot
widths).

So there is no current need and nothing to declare either way, and this note
records that rather than a new argument. What is dead is the 2026-09-05
reasoning: both figures it rested on measure code `PL-2FM6` and `PL-8LXM`
deleted, so it should not be cited. **Decide it in the commit that wants it** -
a package this project calls is one it declares, and until one does,
`pyproject.toml` lists what the project depends on and nothing else. (Project
owner, 2026-09-16: do not take a position on numpy until it is relevant. The
longer re-argument `PL-3SQT` first wrote here was the thing that rule was aimed
at, and was cut to this.)

## Decided: control resolution is not what the interface promised at speed - PL-X9KD, PL-NBWP, PL-NBCJ (2026-09-06)

`PL-X9KD` re-derived `MAXIMUM_SIMULATION_STEP_S` as a *declared control-resolution
tolerance*: a control change lands at the next step boundary, so it is displaced by
up to one step, and the displacement is exactly proportional to the step with no
threshold anywhere in it. Measured at 0.1 s, in percentage points of one atmosphere,
desflurane binding: 6.7e-3 pp for a case-opening dial change, 1.4e-1 pp for a
ventilator start. The criterion is the model's own parameter uncertainty - one SD of
a measured partition coefficient is worth 9e-4 to 6.8e-2 pp.

Two threads came out of that and they were coupled, which is why they are here
rather than only in their own items. **The coupling is now cut, and one of the two
is closed** (2026-09-06).

`PL-NBWP` **- closed.** The derivation above holds at 1x playback and nowhere else.
`steps_per_tick` is the multiplier and `simulation_view.py`'s burst is a synchronous
loop with no `await`, so control resolution is `SIMULATION_TICK_INTERVAL_S x
multiplier` - 30 simulated seconds at 300x. `app/playback.py` said a faster playback
is "a scheduling change and never a modelling one", which is true of a run nobody
touches and false of one where a slider moves.

Decided: keep the behaviour, correct the claims, and publish the grid per rate
against what one step of it costs a displayed compartment - up to about 10 pp at
300x on an abrupt manoeuvre, measured rather than extrapolated, since the
displacement saturates and a linear estimate over-states 300x by four times. Two
measurements settled the rejected options and are the part worth remembering here:
a step costs 33 us, so a burst is at worst a tenth of the tick and simulated time is
standing still when most control events arrive; and frames are two grid steps apart
at every rate, so a finer grid would resolve control timing the display cannot show.
The item carries both in full.

`PL-NBCJ` **- closed the same day.** Whether the step should move to 0.05 s so an
abrupt manoeuvre stays inside one parameter SD. Decided: it stays at 0.1 s, and the
ventilator start being timed to about twice one parameter SD is accepted. `PL-NBWP`
is what settled it, by narrowing the benefit: above 1x the playback grid is
`multiplier x 0.1` s and dominates the step outright, so halving the step would have
changed nothing for a reader at any rate but the slowest, while doubling the
propagations per simulated second and forcing the tick structure to be revisited.

**Why this thread is kept rather than deleted.** The three items ran together and
`PL-NBCJ` was decided on a measurement made for `PL-NBWP`, which no single item is
written from the vantage point of.

`PL-ZVS7` **- closed 2026-09-07, and it was the thread's largest exposure.** None of
the published figures - the 1x tolerance table, the per-rate grid, or the step they
were all measured at - was held by a test, so the whole of what these three items
established rested on prose in two files.
`tests/reference/test_control_resolution.py` now re-measures every one of them from
the parameter files at each run and pins the step beside them. It found on its first
run that `docs/MODEL.md` overstated how much milder an ordinary dial change is than
the binding manoeuvre - "two orders ... at every rate" against a measured 21x at 1x
narrowing to 6.9x at 300x, because the binding manoeuvre's displacement saturates
while an ordinary one stays nearly linear in the delay. Corrected there, and the
corrected relation is now asserted rather than stated.

`PL-X35V` is the remaining tail: the disclosure reaches only a reader with
`docs/MODEL.md` open, and the rate control itself still says nothing.

## Open thread: what makes desflurane wash out too fast - PL-W21J, PL-73G7, PL-RFLN

`docs/MODEL.md` is the authority for this and carries the whole account, in
"Desflurane's residual, and why the parameter file was not changed" under the
published wash-in validation test. This entry exists so that a session reading
the notes rather than the model spec finds the thread, and it deliberately does
not restate it.

The short version. `PL-W21J` built a test-only open-circuit driver so the
elimination comparison could be run at the inspired fraction of zero the
published protocols had. With the apparatus difference gone the model
reproduces sevoflurane and both isoflurane cohorts, and washes desflurane out
2.33 published SD too fast - the one comparison in this repository that misses
a human measurement in the direction of overstating recovery. `PL-73G7` closed
the parameter question: the vessel-rich coefficient the disagreement demands is
nineteen standard deviations above Yasuda 1989's measured human brain:blood and
would invert the measured solubility ordering of the three shipped agents, so
`data/agents/desflurane.json` was not changed and a test now asserts that a
coefficient raised to the measurement's own ceiling still misses. Five other
candidates were ruled out the same way.

**Closed 2026-09-13.** `PL-RFLN` read the methods sections, which the project
owner supplied into the private reference corpus, and excluded the published
apparatus: its 50 ml of Teflon is a series dead space, which in this model is an
alveolar-ventilation decrement rather than a non-zero `F_I`, and applied as one
it is common-mode - it never closes desflurane without pushing both isoflurane
cohorts out of their spreads. `PL-ZDWL` then found the study publishes no
ventilation at all, and that its own pulmonary clearance for the desflurane
cohort is 4.11 L/min against this model's 4.0, so the decrement points away from
the study rather than toward it.

`PL-03ZG` struck the second candidate. End-tidal sampling in a dispersed lung
needed a bias growing as solubility *falls* and raising `F_A/F_A0`; Carpenter &
Eger 1989, the one human measurement of that gradient, has it larger for *more*
soluble agents and negative through an elimination, which deepens the residual
rather than explaining it.

What is left is the published value itself, which nothing this project runs can
settle. `docs/MODEL.md` records that as the single remaining candidate.

**`docket check` names this thread on every grooming pass, and that is
correct.** All three of its items have closed while the question has not, so it
satisfies both clauses of the stale-open-thread advisory built for `PL-DG84`.
It is the permanent false fire that advisory was chosen knowing about - the
reason it can never be a hard failure. The thread goes when the published value
is settled, not before.

## Measured and answered: a server-rendered chart is not the way out - PL-YDKJ, PL-2FM6, PL-2QMK, PL-YSZN (2026-09-08)

`PL-YDKJ` option 3 - "render server-side; one image per frame is one patch" -
said "almost certainly too slow to redraw at 5 Hz in Python, and would lose
live interaction - worth a measurement before dismissing." Measured, at the
project owner's request. **The answer is no, and two of the reasons are
structural rather than a matter of tuning.**

**The transport is better than the item assumed.**
`flet_charts.MatplotlibChart` does not push a base64 image field through the
control tree. Frames go over a dedicated `ft.DataChannel` as WebAgg-style
packets - a full PNG, an incremental diff PNG composited onto a client-side
backbuffer, or raw premultiplied RGBA - so they skip both the msgpack encode
*and* the control-tree walk, with backpressure on a Dart-side ack. The chart
would become one control that never changes. That is the right shape, and it
is why the measurement was worth taking rather than reasoning about.

**What it costs.** Six traces, 282 points each, 1000x360 logical pixels,
matplotlib 3.x through `FigureCanvasWebAggCore`, 40 frames each, on the same
4-vCPU container as `PL-YSZN`:

| Variant | Render | Diff PNG | Total | KiB/frame |
| --- | ---: | ---: | ---: | ---: |
| Scrolling window, full redraw @1x | 30.0 ms | 14.4 ms | 44.4 ms | 27.0 |
| Sweep, blitted lines @1x | 1.3 ms | 8.3 ms | 9.6 ms | 2.3 |
| Scrolling window, full redraw @2x | 34.7 ms | 47.5 ms | 82.1 ms | 55.4 |
| Sweep, blitted lines @2x | 2.2 ms | 32.5 ms | 34.8 ms | 7.3 |

Against the shipped path after `PL-KP7H` and `PL-R2YM`: `page.update()` is
20.3 ms for the whole page at 300x, of which the ~2 080 point controls are
about half - so **the chart costs about 10 ms a frame today**, on 5 KiB. Every
row above also still pays the page's own ~10 ms floor, because the rest of the
control tree is walked either way.

So the best image variant ties at 1x and loses 3.5x at 2x, and the variant
matching how the chart actually behaves loses 4x to 8x.

**Three structural findings, which outlive the numbers.**

1. **The diff-PNG saving does not exist in the mode this chart is in.** A
   scrolling window moves every pixel, so the "diff" is the whole frame. The
   protocol pays only under a sweep display, which is `PL-YDKJ` option 4.
2. **Blitting requires fixed axes**, so the cheap render also requires option
   4: a scrolling window invalidates the cached background every frame.
   Options 3 and 4 are therefore not independent - **3 is only viable on top
   of 4**, and the item lists them as alternatives.
3. **Option 4 alone buys the Flet path nothing.** `PL-YSZN` measured
   `page.update()` on a chart where nothing had changed since the last one at
   the cost of a full frame, both linear in the number of point *controls* and
   indifferent to how many moved. A sweep is O(1) in operations *sent*, which
   was `PL-Q197`'s bottleneck, and O(n) in the walk, which is today's. The
   item's "domain-native and O(1)" is true of the transport it was written
   against and false of the cost that now dominates.

**The one argument the measurement supports.** The two paths scale on
different quantities: Flet's on point count, the image's on pixels. More
traces, more columns or a second plot are free on the image path and linear on
this one, which is exactly the ceiling `PL-YDKJ` exists to name. Nothing is
against that ceiling today.

**Two costs the item does not list.**

- **numpy, and it is already decided.** matplotlib pulls numpy, pillow and
  pyparsing among others, against this file's "Decided: no numpy" (2026-09-05)
  - which was settled on fit rather than on dependency avoidance, and whose
  reasoning does not cover a rendering backend. Option 3 reopens that
  question rather than being covered by it.
- **It gives back `PL-KP7H`.** The paused-only hover is Flet controls
  answering a hover. matplotlib's WebAgg canvas has its own event model, so
  `PL-KP7H` and `PL-YLKR` would both be rebuilt against it.

**And one benefit that cuts the other way, which is not a performance
argument.** `PL-2QMK` records that no session in the web container can
visually confirm a chart change, because Flet's web renderer fetches Flutter
assets the egress proxy denies - which blocks `PL-90Y6`, `PL-3355`, `PL-W8DQ`,
`PL-GVXP` and the rest of `presentation-safety`. A matplotlib figure
rasterizes in any container and can be asserted on in an ordinary test. That
is the strongest thing option 3 has, it is about testability rather than
speed, and it should be argued on those terms if it is argued at all.

**Recommendation: option 1.** Accept that the chart patches one control per
plotted point, document the ceiling, and size the drawn column budget against
it - `CHART_COLUMN_BUDGET_PER_SERIES` is the lever, and halving it halves the
chart's share of a frame. Revisit only when a scale the budget cannot absorb
actually arrives, or when `PL-2QMK` becomes the binding constraint.

**Recorded here rather than in `PL-YDKJ`** because
`origin/claude/m4-implementation-status-be2syh` is holding that file - it moves
the item to `blocked-by: PL-2FM6` - and a second edit would collide at merge.
`PL-18ND` carries the one finding that bears on that block.

## Built and measured: the Qt spike runs, and the frame's dominant cost moved - PL-55DH, PL-X9T3, PL-QXSB, PL-2FM6, PL-YSZN (2026-09-08)

`PL-55DH` built the PySide6 + pyqtgraph spike the project owner approved:
the concentration chart and the readout row behind the *existing*
`SimulationController`, in a throwaway tree outside the package that nothing
under `src/anesthesia_sim/` imported. It ran a real case end to end, and
`--self-check` asserted every trace's newest drawn point against the readout
printed beneath it.

**The spike itself is gone**, deleted whole by `PL-7SVX` once the port landed,
which is what it was built to allow. The tables below are what survives of it,
and they are the record the decision to leave Flet rests on - there is no
source tree left to re-run, so a figure here is re-derived only by rebuilding
the measurement rather than by re-reading the spike.

**It was scoped against a read path that was deleted while it was being
built.** `PL-55DH` says "the shipped column budget", meaning M4 selection over
recorded samples at `CHART_COLUMN_BUDGET_PER_SERIES`. `PL-2FM6`, `PL-4RBD` and
`PL-8LXM` merged mid-session: `RunHistory`, `history_window` and the M4
decimation module are gone, and `SimulationController.drawn_window` is the
only read path. The spike was rebuilt on it, which is a simplification -
one evaluation serves all six traces - and the source selector it was going to
need became a **column-budget control** instead. With M4 gone, "would Qt make
decimation optional" is "can the column budget be raised", which is the same
question in the architecture that replaced it.

### Measured, offscreen, on the same 4-vCPU container as `PL-YSZN`

Median of the last 120 frames, at the shipped 150-column budget, six traces,
five-Hz render cadence, `--self-check` driving its own ticks:

| Stage | Qt at 1x | Qt at 300x | Flet at 1x (`PL-YSZN`) | Flet at 300x |
| --- | ---: | ---: | ---: | ---: |
| `advance` | 0.08 ms | 8.7 ms | 0.18 ms | 26.2 ms |
| `refresh` | 5.2 ms | 6.2 ms | 1.6 ms | 4.6 ms |
| `handoff` / `page.update` | 1.0 ms | 1.2 ms | 26.6 ms | 45.5 ms |

**Only the third row is a comparison.** The first two are
not comparable across PL-2FM6 (`PL-C92D`, 2026-09-16). `PL-YSZN` measured the Flet column on
2026-09-08, before `PL-2FM6` merged the same day, and that merge changed what
two of the three stages *are* rather than how fast they run:

- **`advance`** included recording a sample into `RunHistory` on every step.
  `RunHistory` is gone, so the Flet figure counts work the Qt figure never
  does. Its threefold fall is the history recording going, not Qt.
- **`refresh` / `_refresh_view`** was a binary search over recorded samples
  plus M4 selection. The chart's read is now a closed-form evaluation of the
  run definition, so the Qt figure counts work the Flet figure never did. Its
  rise is the new read path, not Qt.

Reading either row as a Qt-against-Flet result would be reading a toolkit
difference off an architecture change, in opposite directions.

**The `handoff` / `page.update` row is unaffected and is the toolkit
comparison.** Handing a finished frame to the toolkit is the same job on both
sides of `PL-2FM6`, which is why the decision `PL-QXSB` took rests on it alone.

**Re-measurement is out of scope, deliberately.** `PL-C92D` was written to
re-take the Flet column on the post-`PL-2FM6` tree; it was re-scoped on
2026-09-12, because `PL-QXSB` has since decided to leave Flet and the tree
that would be re-measured is one this project has since deleted (`PL-7SVX`). What
was worth keeping is this caveat, for a later reader asking why the interface
left Flet - not three comparable rows nobody will act on.

On the row that *is* a comparison, the result holds and is the one `PL-QXSB`
predicted: **handing the frame to the toolkit costs 1.0-1.2 ms against Flet's
26.6-45.5 ms**, because Qt has no diff to walk. That is 26x at 1x and 39x at
300x.

### The finding that was not predicted: `refresh` now dominates

`refresh` is 5.2-6.2 ms, and **6.18 ms of a 6.24 ms frame read is
`controller.drawn_window`** - the closed-form run definition evaluation. The percent
conversion is 0.06 ms and `controller.snapshot()` is 0.02 ms. Measured
directly on a 1 800 s run at the fitted 15-minute base:

| Columns | `drawn_window` |
| ---: | ---: |
| 150 (shipped) | 6.15 ms |
| 600 | 9.69 ms |
| 2 400 | 25.81 ms |

Two consequences, and the second is the larger.

**The column budget is now bounded by evaluation cost, not by the toolkit.**
`CHART_COLUMN_BUDGET_PER_SERIES` is 150 because Flet charged ~24.5 us per
point control per frame. Qt removes that constraint entirely - `PL-QXSB`
measured 648 000 points in 1.96 ms - but raising the budget now costs about
8.7 us per column in `drawn_window` instead. So the answer to "can the budget
be raised" is yes, and by a factor of about four rather than of four hundred.

**At 1x the chart read is about eighty times the simulation.** A frame
advances two steps (0.08 ms) and then spends 6.2 ms evaluating 150 columns of
a run it already advanced. Inside Flet that is invisible under 26-45 ms of
`page.update()`; on any toolkit without a diff it is the frame. `PL-CNCF`
carries it.

### What this container still cannot answer, and it is the load-bearing half

`paint` measured 24-34 ms here and means nothing: no GPU, a software
rasteriser, an offscreen platform plugin, which `PL-QXSB` already found gives
18-28 ms *including for a frame where nothing changed*. `timer lateness` is
zero because the check drives its own frames. Both are exactly what `PL-X9T3`
exists to measure on the owner's own hardware, and the spike now reports them
on screen for that purpose.

### One capability confirmed rather than argued

`PL-2QMK` records that no session in the web container can visually confirm a
chart change, because Flet's web renderer fetches Flutter assets the egress
proxy denies. `qt_spike.py --screenshot` writes a PNG of the running interface
in that very container, with a dial change drawn in it. So the claim `PL-QXSB`
made for Qt is now exercised rather than asserted: headless screenshot review
of the real interface is available, which is what `PL-90Y6`, `PL-3355`,
`PL-W8DQ`, `PL-GVXP` and the rest of `presentation-safety` are waiting on.
That is a point for Qt independent of speed, and it is the one `PL-QXSB` said
would be worth the most.

### The result that bears on a different decision: `PL-GS3R`

`PL-GS3R` is `P1`, `safety` and `needs-decision`: after `PL-2FM6` the drawn
polyline still departs from the run by **0.26 MAC** at the 12-hour base, moved
from the control change - genuinely fixed - to the steep early wash-in, because
the chart rules a straight line between adjacent columns and a fixed budget
spread across twelve hours chords the same width M4's buckets did. Its first
route is to buy resolution with more columns, and it prices that route against
Flet's per-point charge: "`CHART_COLUMN_BUDGET_PER_SERIES` times traces drawn
times about 24.5 us is the chart's share of a frame ... doubling columns
roughly doubles that share."

**That charge is the one Qt does not have**, so the route costs something else
entirely there. Measured on the spike, 1 800 s at 300x, median of 120 frames:

| Columns | Points drawn | `refresh` | `handoff` | Flet's chart share by its own model |
| ---: | ---: | ---: | ---: | ---: |
| 150 (shipped) | 900 | 6.20 ms | 1.28 ms | 22 ms |
| 600 | 3 600 | 9.14 ms | 1.51 ms | 88 ms |
| 2 400 | 14 400 | 22.22 ms | 2.08 ms | 353 ms |

**`handoff` moves from 1.28 ms to 2.08 ms for sixteen times the points**, which
is the array transport doing exactly what `PL-QXSB` said it would. The whole
cost of more columns is the run definition evaluation, and it is the same cost
on either
toolkit.

So `PL-GS3R`'s route 1 is affordable on Qt and is not on Flet. On `PL-GS3R`'s
own error model - halving the chord width quarters the error - four times the
columns takes 0.26 MAC to roughly 0.016 MAC, for 10.7 ms of Python against a
200 ms frame. The same move on Flet adds about 88 ms of chart share to frames
`PL-YSZN` already measured at 42.8-51.8 ms saturated. Sixteen times the columns
is 24.3 ms on Qt and 353 ms on Flet, which is more than the entire frame.

**This is the strongest thing the spike found, and it is not a speed argument.**
`PL-QXSB` weighs a toolkit against 20x on a frame nobody is waiting on. What
this says instead is that the toolkit choice decides whether an open
safety-classed fidelity defect can be closed by the cheap route or has to be
closed by the expensive one - `PL-GS3R`'s route 2, a curvature-adaptive grid,
which its own brief calls "the right answer numerically, and the expensive
one". Neither item currently sees the other; that is what this paragraph is
for.

## Measured on real hardware: the Qt spike's paint cost and input latency - PL-X9T3, PL-55DH, PL-QXSB, PL-CNCF (2026-09-10)

`PL-X9T3` closed. The project owner ran the Qt spike on their own
machine - macOS, build `0.4.12+g7e0ff5bb`, which is `main` at `7e0ff5b` - and
read the instrument panel at both ends of the rate ladder. This is the half no
session in the web container could produce, and `PL-QXSB` was right that the
container's own figure was an artifact rather than a measurement.

Medians and p90 of the last 120 frames, six traces, the shipped 150-column
budget, antialiasing on, 200 ms render budget:

| Stage | 1x median | 1x p90 | 300x median | 300x p90 |
| --- | ---: | ---: | ---: | ---: |
| `advance` | 0.19 ms | 0.30 ms | 11.06 ms | 16.43 ms |
| `refresh` | 8.84 ms | 11.02 ms | 7.57 ms | 8.13 ms |
| `handoff` | 1.23 ms | 1.74 ms | 0.67 ms | 0.76 ms |
| `paint` | 9.21 ms | 10.35 ms | 8.04 ms | 8.91 ms |
| **whole frame** | **19.5 ms** | | **27.3 ms** | |
| `timer lateness` | 0.01 ms | 0.85 ms | 0.00 ms | 2.46 ms |

At 1x the window was "Fit run" at the one-minute rung, 252 points over six
traces; at 300x a two-hour window, 294 points.

### The three things it answers

**1. Paint is 8-9 ms, and the container overstated it fourfold.** `PL-QXSB`
measured 18-28 ms offscreen *including for a frame where nothing changed*, and
`PL-55DH` measured 24-34 ms the same way, both on a software rasteriser with no
GPU. Saying those were artifacts rather than numbers was correct: on real
hardware the widget's own `paintEvent` costs 8.04 ms at 300x and 9.21 ms at 1x,
near-constant because it redraws the same scene complexity either way. It is a
third of the frame at 300x and about half of it at 1x - the largest single term
at 1x - but it is 4-5% of the 200 ms budget.

**2. Input latency is 0.85-2.46 ms p90, against Flet's 20-30 ms.** This is the
number that matters most, because it is what "laggy" named: `PL-QXSB` was raised
on "It shouldn't be this laggy", and 20-30 ms p90 is where `PL-KP7H` and
`PL-R2YM` left Flet after halving it. Qt is an order of magnitude better at both
rates.

**The comparison is cross-machine and survives being so.** Flet's figure was
taken on the 4-vCPU container; Qt's is on the owner's Mac, and no session can
take both on one machine (`PL-2QMK` - Flet's renderer will not load in the
container). A machine difference of 10-30x is not available, and the *mechanism*
is what the gap is made of rather than the hardware: Flet's event loop is
blocked by the control-tree diff on every frame, and Qt has no diff to be
blocked by. `PL-YSZN`'s finding that an *idle* `page.update()` costs what a full
one does is the same fact from the other side.

**3. The whole frame - including paint - costs less than Flet's diff alone.**
19.5 ms at 1x and 27.3 ms at 300x, against `page.update()`'s 26.6-45.5 ms, which
was Flet's Python side only: its rendering happened in a separate Flutter
process that `PL-YSZN` never measured and that `PL-Q197` found pegged at 100%
CPU. So Qt uses 10-14% of the render budget for everything Flet spent 13-23% of
it failing to finish.

### Two things worth noticing that were not the question

**`advance` is now the largest stage at 300x** - 11.06 ms, above paint's 8.04 -
and the owner's machine runs it about 27% slower than the container did (8.7
ms). Nothing here explains that and nothing depends on it; within one machine
the ratios are what carry, and `advance` is the same call on either toolkit.

**At 1x the chart read costs 46 times the simulation** - `refresh` 8.84 ms
against `advance` 0.19 ms - which is `PL-CNCF` confirmed on real hardware. The
container put 99% of that stage in `controller.drawn_window`, and nothing about
the toolkit changes it: it is the run definition evaluation, and it is the same
cost on
Flet. Inside Flet it was invisible under 26-45 ms of diff.

### What this does to `PL-QXSB`, which is the decision it feeds

The premise that item was opened on is gone - the owner reports the Flet build
as no longer noticeably slow after `PL-2FM6` - so the lag argument is spent, and
that is recorded in `PL-X9T3` rather than re-derived here. What these numbers
add is that the *remaining* case is now measured rather than argued:

- **Headroom**: 10-14% of the frame budget against Flet's 13-23% for less work.
- **Latency**: an order of magnitude, on the axis a reader actually feels.
- **Fidelity affordability**: `PL-GS3R`'s cheapest route out of 0.26 MAC of
  chord error is more columns, and `handoff` moves 1.28 to 2.08 ms for sixteen
  times the points (`PL-55DH`, container). The whole cost of that route is the
  run definition evaluation, which both toolkits pay; the per-point charge that made it
  unaffordable is Flet's alone.
- **Headless verification**: `PL-2QMK`, exercised rather than argued -
  `qt_spike.py --screenshot` writes a PNG of the running interface in the very
  container where Flet's renderer cannot load.

None of those four is speed. That is the shape the decision should be taken in.

### The 600-column reading, and what it corrects (2026-09-10)

Taken by the project owner on the same machine and build, to price `PL-GS3R`'s
first route: the `Columns` selector at 600 rather than the shipped 150, at 300x,
a two-hour window with the run at 6 399 s - so the drawn range fills 89% of the
axis and 600 columns yield **3 204 points over six traces**, against 294 in the
150-column reading, whose run filled only 32%.

| Stage | 150 columns, 294 points | 600 columns, 3 204 points |
| --- | ---: | ---: |
| `refresh` | 7.57 ms | 18.24 ms |
| `handoff` | 0.67 ms | 1.69 ms |
| `paint` | 8.04 ms | 21.57 ms |
| `advance` | 11.06 ms | 7.90 ms |
| **whole frame** | **27.3 ms** | **49.4 ms** |
| `timer lateness` p90 | 2.46 ms | 0.49 ms |

**The pair is confounded and the useful number survives it.** Columns went up
fourfold and the fill went up 2.8-fold, so the points went up 10.9-fold and
neither factor can be isolated from these two readings. What does not need
isolating is the operative figure: **3 204 drawn points cost 49.4 ms of a 200 ms
budget**, which is the worst realistic case for a 600-column setting.

**Two corrections to what this file said before.**

**Paint scales strongly with points.** 8.04 to 21.57 ms - it is the largest
single stage at 600 columns, above the run definition evaluation. The earlier
claim that
it is near-constant held across *rates* at a fixed column count and does not
generalise; that sentence is now qualified where it appears above.

**"Qt makes the point count stop mattering" is wrong, and it was never quite
what was measured.** `PL-QXSB`'s 0.51 to 1.96 ms for 380 times the points was
`setData` alone - the `handoff` term - and that holds: 0.67 to 1.69 ms here for
eleven times the points. The *whole frame* does scale. Fitting the two readings
gives about **8.7 us per drawn point** across `refresh`, `handoff` and `paint`
together, of which `handoff` is 0.35 us.

**The comparison that survives all of this is still decisive, and it is now
sharper.** Qt spends about 8.7 us to evaluate a point, hand it over and paint
it. Flet spends **24.5 us per point control just discovering whether it
changed** (`PL-YSZN`), before its Flutter client draws anything - and that term
is charged whether or not the point moved. So at 3 204 points Flet would spend
about 78 ms on the diff alone, against 49 ms for Qt's entire frame including
paint.

**One gap, stated rather than papered over**: the panel was read while
**paused**, so `refresh`, `handoff` and `paint` are current but `advance` is the
last 120 frames recorded before the pause, and the lateness figure does not
establish what latency does under a running 49 ms frame. Nothing in the decision
turns on it - 49 ms of a 200 ms budget leaves the loop idle three quarters of
the time - but it is not measured.

## Settled, then measured: root-cause batching does lower the spawn rate, but the design cannot say why - PL-CSHL, PL-BHVM

`PL-CSHL` was a pre-registered test with its prediction fixed before the work:
close the `vcs.py` cluster's open items as one batch and count what they spawn
against that cluster's own baseline of 1.05 new items per closure. It ran at
N=9 - two of the eleven `ready` items did not close - and **spawned 3, against
the 9.5 H0 predicted and a rejection threshold of 4**, so H0 is rejected and the
observed rate is 0.33.

**What the result does not license.** `PL-BHVM`'s root-cause account was already
refuted before the batch began: twenty of twenty ref-lifecycle items came back
`unaffected` and all three structure lenses proposed zero `blocked-by` edges. The
low count is therefore not evidence for consolidation. What the batch actually
shows is narrower - five of the nine items turned on one question, *what evidence
proves a ref's work is on the base*, and two rules settled them.
`_annotates_only` was already in the module and decided three; `_superseded` was
written once for `PL-XLQ5` and then answered `PL-8MJ3` unchanged. Reuse of a
decided rule, not consolidation of items.

**And the confound is not separable in this design.** One session closing nine
items has fewer chances to file than nine sessions closing one each, for reasons
unrelated to root causes: a session already holding the whole module recognises a
second finding as the same finding, and findings that would have ended a session
and been captured on the way out were fixed in place instead. Batching and
root-cause structure predict the same low count here. Testing them apart means
closing nine *unrelated* items in one session and comparing, which is one item's
worth of work rather than a redesign.

**The methodological note worth keeping.** A pre-registered spawn count rewards
not filing, and the session doing the counting is the one under that pressure. The
three items were filed on the capture rule and counted against the result. Any
future run should expect the same pressure and say how it handled it.

## Open: item 34's two releases, and the one ordering question left

**Scoped 2026-09-16** (project owner, on `PL-NMTF`). `ROADMAP.md`
planned-milestone item 34 - the Blender-style area/workspace system - was placed
on the timeline and split across two releases: **v0.6.0 "the layout is the
reader's"** (Areas, the View contract, the View registry, Workspaces,
persistence, the unconditional display region and every layout operation) and
**v0.7.0 "the second screen"** (break-out of an Area into its own top-level
window). The schematic moved to v0.8.0 and multi-substance to v0.9.0.

Three decisions are recorded where they belong and are not repeated here:
v0.6.0's section carries the goal, scope and definition of done; § "The debt
gate" -> "The cadence" carries why this scoping froze no gate; and
`docs/MODEL.md` carries what a second top-level window owes the display.

**The one question this note was opened for is now answered** (project owner,
2026-09-16, ratified on `PL-PHKP`). The interface pass - planned-milestone item
33 - **runs after item 34 rather than before it**, and its timeline row moved
from between MVP and Gate 2 to after v0.7.0, renumbering `v0.5.x` to `v0.7.x`
as a patch track takes the number of the release it follows. The reason: item 34
and break-out introduce an area header (the *View's* own, per the provenance
read), a workspace tab strip, a live splitter handle and a drag affordance, none
of which exists to be styled today, so a pass run first would be partly redone.
What that costs is a styled interface two releases later, and `PL-BNYF`'s
separation of arrangement from appearance means the composition of each existing
surface would mostly have survived being rearranged - both recorded in item 33's
entry so a later session can weigh the trade rather than only read the outcome.
Nothing was blocked on the answer either way.

**Two measurements taken on 2026-09-16 that the build work will want.** Both
were run rather than recalled, on PySide6 6.11.2 / Qt 6.11.2. First,
`QSplitter.saveState()` is 35 bytes for a three-pane splitter and is
*byte-identical* for the same three children in reverse order - it records no
widget identity at all - and `restoreState()` returns `True` restoring a
three-pane state into a two-pane splitter and a two-pane state into a
three-pane one, leaving the third at zero. That is stronger than the form
`PL-C842` recorded and is why the layout model owns persistence. Second, and
the trap for v0.7.0: a secondary window built the obvious way,
`QWidget(main, Qt.Window)`, has `main` as its *transient parent*, and Qt counts
only primary windows - top-level, no transient parent - when deciding the last
window has closed, so closing the main window quits the application while the
break-out window is still visible. The rule v0.6.0's region is built for needs
the main window to *veto its own close* instead; `PL-Y04W` carries it.

**A third, filed rather than left here**: PySide6 6.11.2 frees a temporary
`QByteArray` that Qt still points at, through `QDataStream`, `QBuffer` and four
more entry points (`PL-NDKC`), measured in full on 2026-09-26 in a thread of its
own that `bin/docket show PL-NDKC` finds. The forecast first written here, that the persistence work
meets it when it decodes a saved blob, did not survive `PL-C842`: the saved
workspace is JSON.

## Measured: PySide6 frees a temporary QByteArray that Qt still points at, at six entry points - PL-NDKC (2026-09-26)

**The trap.** A Qt object built over a `QByteArray` that nothing else
references reads or writes freed memory. Found 2026-09-16 while re-measuring
`QSplitter.saveState()` for the v0.6.0 scoping, and measured on 2026-09-26
against PySide6 6.11.2 / Qt 6.11.2 on CPython 3.14.7, Linux x86-64 - the
versions `uv.lock` resolves. 6.11.2 was also the newest PySide6 on PyPI that
day, so no upgrade escapes it.

Six Qt entry points keep the `QByteArray *` they are given. PyQt6 6.11.0's sip
declarations for QtCore, QtGui and QtWidgets name seven `QByteArray *`
parameters, all in QtCore: these six, and `QIODevice::readLineInto(QByteArray *,
qint64)`, which writes into the array during the call and keeps nothing. Each
form below ran 25 times, one process per run. The readers read back an `int32`
and a `QString` first written through a stream over a named array, or a line of
text, and the writers wrote one key and its value:

| Qt's C++ signature | Python calls that bind it on PySide6 6.11.2 | Over a temporary, 25 runs each |
| --- | --- | --- |
| `QDataStream(QByteArray *, OpenMode)` | `QDataStream(array, mode)`, two arguments only | segfault on the first read, every run (exit 139) |
| `QBuffer(QByteArray *, QObject *)` | `QBuffer(array)` | opened and read through `QDataStream(buffer)`: `0` and `''` every run, with `stream.status()` still `Ok` |
| `QBuffer::setBuffer(QByteArray *)` | `buffer.setBuffer(array)` | read through `QDataStream(buffer)`: `0` and `''` with `Ok`, every run; read with `readAll()`, `read()` or `data()`: segfault, every run |
| `QTextStream(QByteArray *, OpenMode)` | `QTextStream(array)` and `QTextStream(array, mode)` | segfault in `readAll()`, every run, one argument or two |
| `QXmlStreamWriter(QByteArray *)` | `QXmlStreamWriter(array)` | segfault while writing, every run |
| `QCborStreamWriter(QByteArray *)` | `QCborStreamWriter(array)` | segfault while writing, every run |

And the forms that read or wrote correctly:

| Constructed as | Outcome, 25 runs each |
| --- | --- |
| `QDataStream(QByteArray(blob))` - one argument, no mode | correct every run |
| any of the six, given an array bound to a name | correct every run |
| `QBuffer()`, then `setData(QByteArray(blob))` or `setData(blob)` | correct every run |
| `QTextStream`, `QXmlStreamWriter` or `QCborStreamWriter` over a `QBuffer()` opened for writing, read back with `buffer.data()` | correct every run |
| `QDataStream(blob, ...)`, `QDataStream(blob)`, `QBuffer(blob)` or `QTextStream(blob)`, `blob` a Python `bytes` | refused: `ValueError`, "called with wrong argument values" |

**PySide6 keeps no reference to the array at any of the six.** `sys.getrefcount`
on a named array reads the same before and after each of the six calls, while
`QReadLocker(lock)`, which PySide6's typesystem does give a `reference-count`,
raises its lock's count by one. So once the caller's last reference goes, the
array is freed with Qt still pointing at it.

The `QDataStream` segfault's faulthandler C stack, innermost first:
`QBuffer::readData`, from `QIODevicePrivate::read`, from
`QDataStream::readBlock`, all in `libQt6Core.so.6`.

**The silent rows are the worse ones, and no row is a guarantee.** They return
values a decoder would accept, and `status()` - whose `ReadPastEnd` and
`ReadCorruptData` are how Qt reports a bad read - says `Ok`. Nor is the outcome
fixed per entry point. `setBuffer` read zeros through a stream and segfaulted
through `readAll()`. A `QBuffer` over a temporary whose `size()` and then
`data()` were called reported the right size and then segfaulted inside
`data()`. And a second session on the same versions, running its own scripts
five times each on 2026-09-26, saw `QXmlStreamWriter` return normally 5 of 5 -
writing into freed memory with nothing reported - and `QCborStreamWriter`
segfault 1 of 5, where the scripts here segfaulted 25 of 25 for both. This is
undefined behaviour, so each row is what this build's allocator and that script
happened to leave in the freed memory, not a property anything can rely on.

**Why.** All six end in a `QBuffer` holding the caller's pointer. `QBuffer`'s
constructor and `setBuffer` store it, and the four stream constructors -
`QDataStream::QDataStream(QByteArray *a, OpenMode)`,
`QTextStream::QTextStream(QByteArray *array, OpenMode)`,
`QXmlStreamWriter::QXmlStreamWriter(QByteArray *array)` and
`QCborStreamWriter::QCborStreamWriter(QByteArray *data)` - wrap it in
`new QBuffer` and open that buffer before they return. Qt documents
`QBuffer::QBuffer(QByteArray *byteArray, QObject *parent)` as: "The caller is
responsible for ensuring that byteArray remains valid until the QBuffer is
destroyed, or until setBuffer() is called to change the buffer. QBuffer doesn't
take ownership of the QByteArray." PySide6 keeps nothing alive for any of them:
their entries in the 6.11.2 wheel's typesystems/typesystem_core_common.xml carry
no `reference-count`, the element the same file uses to hold a pointer argument
alive elsewhere, as on `QReadLocker(QReadWriteLock*)`. So a temporary's wrapper
is released when the call returns, and takes the C++ array with it. The
one-argument `QDataStream::QDataStream(const QByteArray &a)` fills its buffer
with `setData(a)` instead, which copies, and that is why it is safe. Qt gives
`QTextStream` the same copying overload, `QTextStream(const QByteArray &,
OpenMode)`, but the 6.11.2 typesystem removes it (`remove="all"`), so in Python
every `QTextStream` over a `QByteArray` binds the pointer, one argument or two.
Qt's sources at the tag the wheel bundles:
https://github.com/qt/qtbase/blob/v6.11.2/src/corelib/serialization/qdatastream.cpp,
https://github.com/qt/qtbase/blob/v6.11.2/src/corelib/io/qbuffer.cpp,
https://github.com/qt/qtbase/blob/v6.11.2/src/corelib/serialization/qtextstream.cpp,
https://github.com/qt/qtbase/blob/v6.11.2/src/corelib/serialization/qxmlstream.cpp
and
https://github.com/qt/qtbase/blob/v6.11.2/src/corelib/serialization/qcborstreamwriter.cpp.

**Not a PySide quirk, and reported: PYSIDE-232.** PyQt6 6.11.0 / Qt 6.11.0
fails the `QDataStream` and `QBuffer` forms under the same reproduction, 25 runs
of 25 each: the `QDataStream` form segfaults through the same three frames, and
the `QBuffer` form segfaults rather than reading zeros. PyQt6's sip declarations
give none of the six a KeepReference - five mark the array Constrained, and
`QXmlStreamWriter`'s carries no annotation - so it too leaves the array's
lifetime to the caller. PySide's development branch declared all six exactly as
6.11.2 does on 2026-09-26, so no fix is in progress. A report does exist:
PYSIDE-232, "Crash with QDataStream and QByteArray"
(https://bugreports.qt.io/browse/PYSIDE-232), which a second session's web
search found on 2026-09-26 after the search here had reported none. Nobody here
has read it: this environment's proxy refuses bugreports.qt.io (403 on
2026-09-26), so its status, its date and whether it reaches past `QDataStream`
are unknown. In C++ the mistake does not compile - g++ 13 rejects taking a
temporary's address with "taking address of rvalue" - so this is a C++ safety
rule lost on the way to Python: the calling code breaks Qt's documented
contract, and neither binding stops it, although Python's own promise is that
pure-Python code cannot corrupt memory. Whether to add the six-entry-point
reproduction to PYSIDE-232 or to file a new report citing it waits on someone
reading it from outside this environment.

**The rule: never pass a `QByteArray` where Qt's C++ signature takes
`QByteArray *`.** Let Qt own the bytes, or copy them. The first table above
lists the six signatures and the Python calls that bind them. A call does not
show which overload it binds, and two read alike: `QDataStream(array)` with one
argument binds `const QByteArray &` and copies, while `QTextStream(array)` with
one argument binds the pointer. `PL-KJXS` is the check that would enforce the
rule, filed rather than built here.

- **This project's own data goes through the standard library**, not Qt's
  binary stream: JSON bytes into and out of `QMimeData.setData` for a drag
  payload, measured round-tripping on 2026-09-26. Qt's own documentation says
  `QDataStream`'s binary format "has evolved since Qt 1.0, and is likely to
  continue evolving", so bytes saved through it are tied to a Qt version, where
  JSON is readable, diffable and testable without Qt.
- **Where Qt needs an I/O device**, `QBuffer()` with no argument owns its
  storage and cannot dangle: an in-memory PNG written through
  `QImage.save(buffer, "PNG")` encoded and decoded correctly on 2026-09-26, and
  text, XML and CBOR written through `QTextStream`, `QXmlStreamWriter` and
  `QCborStreamWriter` over one came back byte for byte from `buffer.data()`.
- **Reading bytes Qt itself wrote** - a stock item view's drag data, say - is
  the one case that needs a stream, and the one-argument `QDataStream(array)` is
  Qt's own read-only constructor, which copies, so a temporary is safe there.
- **Do not lean on `stream.status()` to catch it.** The silent rows read `Ok`.

**What avoiding it costs: nothing planned.** Saved layouts are JSON under
`PL-C842`, and so is the saved-workspace file `PL-SSQW` decides. Scenario
save/load, planned-milestone item 9, persists simulation state, and
`tools/import_boundary_check.py` already refuses any `PySide6` import under
`core/`, so no stream could reach it. Qt's opaque geometry and splitter blobs go
back to Qt undecoded, if they are kept at all.

**Where it will be met.** Nowhere yet: nothing under `src/` or `tests/`
calls any of the six on 2026-09-26. And not where `PL-NDKC` first said.
Under `PL-C842` the saved workspace `PL-SSQW` decides is versioned JSON written
from the `LayoutModel`, and no view calls `saveState()`, so the persistence path
decodes no Qt blob. The candidates are the Qt code built around the model:

- a drag payload in `QMimeData` for `PL-2KXB`'s Area swap. Qt's own Draggable
  Icons example decodes one with `QDataStream dataStream(&itemData,
  QIODevice::ReadOnly)`, which is safe in C++ over its named `itemData` and is
  the trap in a Python port that passes `event.mimeData().data(...)` straight
  into the call
  (https://github.com/qt/qtbase/blob/v6.11.2/examples/widgets/draganddrop/draggableicons/dragwidget.cpp);
- a `saveGeometry()` blob, if `PL-Y04W`'s break-out persists window placement
  that way and decodes it to validate it;
- any test that decodes a Qt state blob, as the 2026-09-16 measurement did.

**The reproduction**, one form per process: `python -X faulthandler repro.py
refcount` first, then `temporary`, `qbuffer`, `textstream`, `xml` and `safe`.
The `refcount` form is the deterministic one; the others show what the freed
memory did on this build:

```python
import sys

from PySide6.QtCore import (
    QBuffer,
    QByteArray,
    QCborStreamWriter,
    QDataStream,
    QIODevice,
    QReadLocker,
    QReadWriteLock,
    QTextStream,
    QXmlStreamWriter,
)

READ = QIODevice.OpenModeFlag.ReadOnly
written = QByteArray()
out = QDataStream(written, QIODevice.OpenModeFlag.WriteOnly)
out.writeInt32(42)
out.writeQString("hello, workspace")
del out
blob = bytes(written.data())


def set_buffer(array):
    buffer = QBuffer()
    buffer.setBuffer(array)
    return buffer


if sys.argv[1] == "refcount":  # the six print n -> n; the control prints n -> n + 1
    lock = QReadWriteLock()
    before = sys.getrefcount(lock)
    locker = QReadLocker(lock)
    print("control QReadLocker(lock)", before, "->", sys.getrefcount(lock))
    locker.unlock()
    for name, keep in [
        ("QBuffer(array)", QBuffer),
        ("QBuffer().setBuffer(array)", set_buffer),
        ("QDataStream(array, READ)", lambda array: QDataStream(array, READ)),
        ("QTextStream(array)", QTextStream),
        ("QXmlStreamWriter(array)", QXmlStreamWriter),
        ("QCborStreamWriter(array)", QCborStreamWriter),
    ]:
        array = QByteArray(blob)
        before = sys.getrefcount(array)
        kept = keep(array)
        print(name, before, "->", sys.getrefcount(array))
        del kept  # before the array it points at is rebound and freed
elif sys.argv[1] == "temporary":  # segfaults in QBuffer::readData
    stream = QDataStream(QByteArray(blob), READ)
    print(stream.readInt32(), repr(stream.readQString()), stream.status())
elif sys.argv[1] == "qbuffer":  # reads 0 and '' with status Ok
    buffer = QBuffer(QByteArray(blob))
    buffer.open(READ)
    stream = QDataStream(buffer)
    print(stream.readInt32(), repr(stream.readQString()), stream.status())
elif sys.argv[1] == "textstream":  # segfaults, with one argument as with two
    text = QTextStream(QByteArray(b"hello, workspace"))
    print(repr(text.readAll()))
elif sys.argv[1] == "xml":  # segfaults while writing
    writer = QXmlStreamWriter(QByteArray())
    writer.writeStartDocument()
    writer.writeTextElement("k", "v")
    writer.writeEndDocument()
else:  # "safe": reads 42 and 'hello, workspace'
    stream = QDataStream(QByteArray(blob))
    print(stream.readInt32(), repr(stream.readQString()), stream.status())
```

**Re-measure on any PySide6 upgrade.** Run `refcount` first. A fix made the way
PySide already keeps `QReadLocker`'s lock alive shows as that entry point's
count rising by one, like the control's, and a fix to one entry point says
nothing about the other five. The other forms are illustrations rather than the
test, since their outcome is undefined behaviour and has varied by script. The
rule above does not depend on a fix: it avoids the pointer-taking signatures
rather than working around them, so it costs nothing to keep after one.

## The generator tier has a second entrance, and one question left open

`PL-G5ZH` gave the tier a second way in (project owner, 2026-09-19): a defect
in the machinery that *identifies and ranks* generators ranks at the same
priority as a generator. The thread is here rather than only in that item
because it has an open decision belonging to no item's own work, and because
the design turned on a count a later session would otherwise redo.

**The count that decided the design.** Deriving the claim from `touches` -
promote anything touching `plan.py`, `model.py`, `checks.py`, `render.py`,
`cli.py` or `generator_check.py` - would have promoted **36 of 322 open items**
above every `P1` (20 `P2`, 16 `P3`, measured 2026-09-19). That is the same
objection `tools/generator_check.py` already records against citation density
at 33: promoting that many means nothing. The machinery is a few functions
inside files that do many other things, so `impairs-generators:` is a recorded
judgment like `root-cause-of:`, and `generator_paths` is only its falsifier -
it refutes a claim on code the item never goes near (286 of the 322) and
establishes none.

**Do not re-propose the path-derived version** without a new argument that
survives that number.

**The obligation comes with the rank** (project owner, 2026-09-19, `PL-4MPJ`).
`CLAUDE.md`'s two endings for a generator - fix it in this session, or end the
reply with a prompt starting a fresh one - bind a machinery defect too. The
session recommended the opposite, on the grounds that a prose claim should not
compel an interruption the way a measured three-item cluster does; the answer
was to extend them, which makes this a *specified* decision and raises the bar
to reopen it from ordinary evidence to a compelling argument.

What that recommendation was worth keeping is the asymmetry it named, since
that is what a reopening would have to answer: a generator's warrant is three
named, resolvable, checked items, and an `impairs-generators:` claim's warrant
is one session's prose. The obligation is now the same for both.

**Closed alongside it:** `PL-C97K`, the store's only machinery defect, merged
in `#693` before the field existed. `PL-GYRX` asked for the retrofit and is
dropped - a closed item is never ranked, so the field would record a claim
nothing acts on. No open item carries the field today; the first live use is
the next machinery defect captured.

## All six of PL-6ZQY's clusters now have a head - PL-6TP8, PL-HWW1, PL-4FBP, PL-4Q9B became theirs

`PL-VX5H` built the way to rank a generator: `root-cause-of:` on the item that
causes a cluster, which `docket next` then offers above every band but `P0`.
Applying it to the six clusters `PL-6ZQY` found under one mechanism - *the
apparatus infers a fact it could have recorded* - turned up something its own
description
does not say - **naming a mechanism is not the same as having an item that
would settle it**, and on 2026-09-17 only two of the six had one.

**Resolved 2026-09-18**, on the project owner's instruction to close the four.
Each tracking item *became* the head it was filed to say was missing, rather
than closing in favour of a new one: the diagnosis, the decision and the
membership were already written in it, so promoting it cost no new item and
closing it would have thrown that away. The paragraphs below are kept because
the reasoning behind each failed candidate is what a session reopening one of
the four decisions will need.

`PL-BHVM` and `PL-L4YG` carry the field. The other four do not, and the point
worth keeping is *why the obvious candidate failed in each case*, because the
failure has one shape: a real item, correctly filed, scoped deliberately
narrower than the mechanism it sits under.

- **`PL-036`** (prose that asserts facts about the tree) is the clearest. Its
  `Decided` section records the general case as closed - *"Recorded, and not to
  be revisited by tooling: whether a documented statement is still true stays
  human"* - and its `Done when` implements one link, fifteen bullets under
  `docs/MODEL.md` "Minimum displayed outputs". Marking it would have recorded a
  claim its own brief refuses.
- **`PL-6P9Y`** (the roadmap is prose the tooling parses) says in its own triage
  note that it is `P3` "because it moves exactly one id today".
- **`PL-F48B`** (the checkout is a cache) is scoped to tags after a history
  rewrite, and its `Done when` permits recording the decision *not* to act. The
  permitted-ref-operations half of that cluster has no item at all.
- **What a `verify:` command proves** has no candidate: `PL-LKGL` is the
  measurement, is `done`, and explicitly refused the general contract.

The four were filed under `feature: generator-heads` with their candidate
members recorded and **deliberately not marked**: the field is what lifts an
item above a `safety`-classed `P1`, and its worth is that it is a recorded fact
rather than an inference, so four heads composed by the session that had just
built the ranking would have been inferences wearing that authority. That
reservation was about *who* was writing the claim and on what evidence, not
about whether it should exist, and `PL-VX5H`'s open end is what the owner
closed on 2026-09-18.

What was done differently on the second pass is the part worth keeping. Each
candidate list was re-read against its own item's brief rather than carried
over, which moved membership in both directions: `PL-6P9Y` and `PL-F48B` were
named only as *rejected heads* by the first pass and are members; `PL-LBW5`
joined the `verify:` cluster; and five items whose titles read as `verify:`
work - `PL-8T83`, `PL-SHTR`, `PL-BGMK`, `PL-PFK1`, `PL-0HPV` - were left out
on their briefs, each naming a cost or a different consumer rather than a
reading of an exit status. `PL-4FBP`'s list is recorded as a **confirmed floor
rather than a census**: the prose-asserts-facts cluster is visibly larger than
the fifteen it names, and the items left out are named in it so the next
session does not re-derive them.

**The general finding, which outlives all five items.** `PL-6ZQY`'s map is a
list of *mechanisms*, and the queue holds *items*. Nothing in the project
connects the two, so a cluster can be correctly diagnosed, correctly recorded,
and still have nowhere for the diagnosis to live - which is the same failure the
map itself names, one level up: the apparatus inferring a fact (which item heads
this cluster) that it could have recorded.

**First of the four resolved, 2026-09-19: `PL-4Q9B`, and it closed by
dispersing rather than by building.** Worked as a head, the clone-trust cluster
turned out not to be one mechanism. Its first question - whether one
reconciliation point could stand for the clone against the remote - answers
*no*: `vcs.fetch_remote` is the only place every command passes through, and
neither of its omissions can be reversed there, since forcing tags moves local
tags without asking on every invocation and pruning is refused outright. The
four staleness conditions fire at four moments and want four cheap local fixes.
Its second question - record the permitted ref operations - is now
`docs/worker.md` § "Ref operations a session cannot perform", stating the
symptom and whose the operation is and **naming no cause**, because `PL-3V6C`'s
two measurements are mutually exclusive and neither is established.

**That last clause was falsified on 2026-09-21 by `PL-ZM48`, and the thread is
closed.** The two measurements are not mutually exclusive: one 2026-09-20
`git push origin --delete` returned `HTTP 403`, then `send-pack: unexpected
disconnect`, then `Everything up-to-date`, at exit status 1 - so `PL-TFWR` and
`PL-XQRK` were reading different lines of one output, and the contradiction
`PL-3V6C` was filed on never existed. The section now gives that sequence as the
deletion row, and separates what the error's shape rules out from what it
establishes; who returns the 403 is still unmeasured, so no mechanism is
asserted. The wider lesson survives unchanged and is arguably sharper: the head
was right that nothing was established, and wrong about why.

**The generalisable part, for the three heads still open.** A `root-cause-of:`
field is a *hypothesis* that one mechanism explains its members, and working
the head is what tests it. This one failed the test, and the failure was worth
the pass: five members closed or dropped, two answered and moved to `ready`,
and the four left standing are visibly independent rather than presumed
related. So "the head did not survive contact" is a successful outcome for a
generator, not a wasted one - what it must not do is close having built a
central mechanism the members did not want. `PL-6TP8`, `PL-HWW1` and `PL-4FBP`
should each expect the same question to be live.

**One of the four heads split on 2026-09-19, and the reason generalizes.**
`PL-HWW1` was filed holding eight members under one diagnosis - milestone
membership is scraped rather than recorded. Measured against the code, three
are that - `PL-4PC5`, `PL-6P9Y`, `PL-C4RS`, all about `### Required scope`
having no grammar - and four are a *different* mechanism: `PL-Y1L0`,
`PL-J45M`, `PL-7CSP` and `PL-B5DW` re-derive the release train's arrangement
by comparing version numbers, where § "The timeline" is already a parsed,
grammar-checked table whose row order *is* the arrangement. They are now
`PL-2T03`, under `feature: timeline-arrangement`. `PL-SVRW` left the list
entirely as an ordinary consolidation.

The distinction is worth carrying because `PL-6ZQY`'s map names only the first
half of it. *Infers a fact it could have recorded* and *re-derives a fact it
already has* look identical from the symptom - a heuristic patched at one call
site - and want opposite fixes: the first needs a place to write the fact
down, the second needs the existing record to be read. A head composed from
symptoms will mix them, which this one did. The test that separated them was
cheap: ask whether the document already states the fact somewhere with a
grammar. For arrangement it does; for membership it does not.

## The evidence layer has no failure channel, so every reader re-decides what silence means — PL-Q9Z1, PL-MM7F, PL-73P0 (closed 2026-09-22)

`PL-BHVM` closed on 2026-09-19 as a design round, and this is the thread that
outlives it. The item asked whether the apparatus should *record* evidence
rather than infer it; `vcs.py`'s module docstring had already refused that, in
its opening paragraphs, because an abandoned session leaves an item marked
in-progress forever. So the framing was closed rather than answered, and the
round's finding is one level down.

`_run_git` *returned* `""` for a non-zero exit, a missing git and a timeout
alike, so absence-of-evidence and evidence-of-absence were the same value -
the diagnosis as it stood on 2026-09-19, before `PL-Q9Z1` gave the runner the
`GitSilence` marker that `answered()` reads. Every caller then adjudicated that
silence on its own: eight `known()` properties, 54 references to `declined`, and
67 lines of prose settling it one read at a time — and two calls inside
`branches_in_flight` settling it in opposite directions.

**The measurement is the part worth keeping**, because the cost had been argued
and never counted. Substituting a runner that fails one subcommand and answers
everything else truthfully, against the real repository: failing `diff
--numstat` alone takes `branches_in_flight` from 13 `editing` marks to **0**,
with `unreadable` staying **empty** in both cases, while failing `diff --raw`
over-reports to 24 and so fails safe. Under a total failure the module splits
four-four: `stranded`, `lost`, `orphaned` and `merged_pull_requests` decline
correctly; `branches_in_flight`, `precedence`, `branch_state` and
`default_base` each return a confident clean answer.

That is `.claude/rules/apparatus-standard.md`'s floor breached on
`FlightReport.unreadable` — **the field the floor's own text cites as proof the
code already holds to it**. Which is why this is a defect against a written
standard rather than a new policy question, and why the fix is an enforcement
a session cannot forget: a fault-injection test that fails the Nth git call and
asserts each public read declines or keeps the mark. Prose demonstrably cannot
do it — `_superseded`'s docstring states the correct direction in three cases
while the code inverts two of them, and `test_vcs.py:467` asserts the inverted
one.

**Two corrections this thread should not lose.** `PL-Q9Z1`'s brief argues
reachability from `_run_git`'s 10-second timeout; the real `diff --numstat`
calls run in 4.5 ms, so that mechanism is off by three orders of magnitude. The
conclusion survives on a different one — a non-zero exit, most plausibly a ref
that vanishes between the `for-each-ref` that lists it and the `diff` that
reads it, which happens here whenever a branch is deleted while the digest
runs. And the `r_vcs` ratio is not what makes this a generator: the count of
items each choosing their own answer to one question is.

**Where it goes next.** `PL-Q9Z1` is the head and carries the channel plus the
test; `PL-MM7F` (the memo caching a failed call) closed against that channel on
2026-09-19 - `GitRunner` stores an answer and never a silence, so a transient
fault is retried by the next caller instead of being served to every one of
them for the rest of the command, and the healthy case is unchanged because all
106 of the digest's memo hits are genuine answers; `PL-73P0` (`default_base`
guessing `"main"`) is untriaged and sits upstream of every comparison in the
module.
`PL-SY1J` may resolve against `PL-Q9Z1` without its own diagnosis, since
`precedence` returns `carriers=()` *and* `unreadable=()` on failed evidence.

**Built 2026-09-19, and the sweep out-measured the round.** `PL-Q9Z1` landed the
channel: `_run_git` returns `GitSilence` for a call git did not answer,
`_Silences` carries a read's silences into its `declined`, and
`subprojects/docket/tests/test_vcs_silence.py` holds every public read to
declining or keeping its marks, one silenced call at a time.

The four-four split above is a measurement of a *total* git failure, and that is
the least informative test available. Every read here has an early gate - an
unresolvable base, no refs - that a total failure trips, so it declines for a
reason that has nothing to do with the silence and the reading looks compliant.
Failing **one** call at a time reaches the middle of a read, which is where the
conflation lives, and there **nine** reads were in breach rather than four:
`stranded` dropped an item existing on one branch and nowhere else, `lost`
dropped a deleted item, and `closed_by`, `closures_on_base`, `records_on_base`,
`filed_with_work` and `cut_window` each lost a finding with `declined` empty.
Any future measurement of this kind should start one call at a time.

Two properties of the sweep are what make it worth its size, and both were
learned from it failing. It **refuses a vacuous pass** - a read the fixture
gives nothing to find can lose nothing, so it would pass whatever it does with a
silence, which is the check `CLAUDE.md` retires rather than keeps; that is what
drove the fixture to six branches and is how `orphaned`, `filed_with_work` and
`cut_window` came to be covered at all. And a **registry guard** fails when a
read taking a runner is added without saying which half it is in, because
nothing made the last new read answer the question.

`PL-SY1J`'s guess above is confirmed in part: `precedence` now declines on
failed evidence and prints that its ordering is partial. Whether the
2026-09-16 observation had a second cause is still its own item.

**`PL-ZPDM` closed two of the three reads the sweep could not cover (2026-09-22).**
`tags` answers with a `TagSet` and `changed_items` with a `ChangedItems`, both
carrying `declined`, and both are in the sweep now. What the close found is that
the brief had the release gate's direction backwards: it read the `tags` silence
as a refusal, and `release.is_untagged` has held a project with no tags to
nothing since the gate was written on 2026-08-30 - so the empty set a silence
produced was free passage, and the one gate guarding a gap nothing can repair
afterwards skipped itself whenever git failed. `cmd_release` refuses on
`declined` now; `cmd_check` declines the `verify:` replay rather than scoping it
to nothing; `doc_check.check_tags` keeps its silence, which is now a decision it
takes rather than the accident of one empty set.

`default_base` was the third of that shape and closed as `PL-73P0` on
2026-09-22, which ends the thread: every public read in `vcs.py` is in the
sweep, the gap list is empty, and the machinery that recorded a gap went with
it rather than sitting there parametrized over nothing.

**Two things that close found are worth keeping, because neither was in the
brief.** The first is that the failure is not one case but two, and the brief
named the harmless one. "No candidate resolves" is visible the moment anyone
looks. The costly one is a candidate resolving *only because a preferred probe
went unanswered*: `main` is a real ref, it resolves, nothing looks wrong, and a
fresh clone's local `main` can trail the remote by many commits - which is the
fallback `default_base`'s own docstring already measured at 20 paths reported
outside a commission whose true answer was 4. Marking only the first would have
left that one live and looked like a fix. The silence sweep is what found it:
it failed on the second case within a minute of the first being written.

The second is that the brief's measured example had gone stale, and in the
direction that matters. It records `branch_state` returning `behind=0, ahead=0`
under a total silence - "you are current with the base" - and that is no longer
reproducible: `_Silences` and `_branch_state`'s own re-probe both landed since,
and it declines in both failure states. What was still live was narrower and
worse. `bin/docket verify` passes no wrapped runner, `verify.changed_paths`
discards `_run`'s exit status, and `_run` returns *combined* stdout and stderr -
so a base that does not resolve makes git's three-line fatal message come back
as three changed paths. Measured 2026-09-22: the commission audit reported
`fatal: ambiguous argument 'main...HEAD'...` as a path outside the commission
and named neither of the two files the branch had actually changed. Confidently
wrong in both directions at once, on the check whose whole job is to certify a
branch's scope. `verify` refuses on an unresolved base now; the underlying
stderr-as-paths defect fires for any bad `--base` and is filed as `PL-9RFP`.

## Decided: three silently-wrong checks go ahead of product work - PL-VKGJ, PL-STC4, PL-T83R (2026-09-19)

**(project owner, 2026-09-19, ratified**, over letting the three rank on their
`P2` band alongside everything else and be picked up whenever `bin/docket next`
reached them.) The decision came out of a read-only survey of the open workflow
lane and is a *sequencing* decision only: no priority was changed, because
`docket check` pins `P1` to `safety` and `science` and `CLAUDE.md` forbids
promoting process work into that band to move it up the order.

**They are one problem, which is why they move together.** Each is a check or a
report that answers confidently and wrongly, which is the first of `CLAUDE.md`'s
three compounding-friction tests — a check passing while the guarantee it stands
for is void:

- `PL-VKGJ` — the session-start digest under-reports the grooming debt. Filed
  on a 10-vs-19 measurement; re-measured live on 2026-09-19 at **9 vs 13**
  (`bin/docket digest | grep -i groom` against `bin/docket check`). The cause is
  `checks.py`'s `if closures is None: return` guard, which every command but
  `check` takes, so the `pr`-backfill advisories are structurally invisible to
  the digest. The guard is deliberate; nothing indicates the printed *count* was
  meant to exclude them.
- `PL-STC4` — `docket verify`'s suppression check reads prose. On `PL-VHVJ`'s
  own branch it reported 13 flagged lines of which 12 were that item's brief,
  code comments and docstrings. It is one of the four *absolute* integrity
  checks in `verify --self`, so its false positives train a reader to skim the
  block where a real protected-path failure prints. The removed-assertion check
  beside it already took the two narrowings that would fix it.
- `PL-T83R` — `main`'s quality run failed on **32.7%** of the pushes that
  reached a verdict (74 of 226) between 2026-09-05 and 2026-09-16, with
  unbroken red stretches of 50, 9 and 5. The 50-run stretch spanned 37 hours.
  A red-`main` digest line that is right a third of the time is the second
  friction test — an advisory being routed around.

**The three are deliberately *not* given one shared `feature:`, and this note
is the carrier instead.** `PL-CSV0`'s triage pass landed as `#720` while this
was being written and seated `PL-VKGJ` into `queue-hygiene`; `PL-T83R` already
carried `ci-cost`; only `PL-STC4` had none, and it went into
`verify-false-reject` beside `PL-4FD2`, which describes the same defect
independently. Two of the three therefore sit in existing groups that name real
completions, and stripping those for a tidier label would cost more than it
buys - `bin/docket feature` counts what completes, not what a reply grouped.

So the cross-group sequencing decision has no `feature:` to live in, which is
what this section is for. A session asking "are the silently-wrong checks dealt
with" reads this paragraph and then `bin/docket show` on the three ids; there is
no single command behind it, and that is the accepted cost of leaving three
good groups intact. That is a session's call under rule 14 - its blast radius is
one field on each of three items.

**`PL-STC4` is probably a duplicate of `PL-4FD2`**, filed apart because
`bin/docket new` does not detect a duplicate title (`PL-TZ7T`). Both are now in
`verify-false-reject`; whether they merge is for whoever works them.

**`PL-G424` was escalated in the same sitting and is not part of this group.**
It is the one open generator head (apparatus-side citation drift, 21 open
members) and it stood at `status: untriaged`, which makes it invisible to
`bin/docket next` despite ranking above every band but `P0`. It is inside
`PL-CSV0`'s pass.

**What the survey found that nothing had stated.** Seven of the eight recorded
generator heads are `done` and **64 of their 87 members are still open** -
`PL-4FBP` closed with 24 of 24 open, `PL-BHVM` with 7 of 8. That is not a
defect: `CLAUDE.md` says `root-cause-of:` names the items a head *explains*,
not the ones it closes, so a head stops the inflow and leaves the stock. It is
worth writing down because those 64 are the well-organised, safe-to-chip-at
half of the backlog, and because nothing in the store says so.

## Decided: a repeat filing is evidence, and it feeds the generator tier - not the band (2026-09-20)

**(project owner, 2026-09-20, ratified**, over the mechanism they first
described - counting repeat filings and raising the item's `priority:`.)

**The observation is theirs and it is the sharper half.** Asked why so many open
items named `verify` and prose, the answer was a cluster of five captures of one
defect. Their follow-up was the part that had been missed: if we keep *trying*
to file the same item, the defect keeps firing, so the attempt is a signal about
recurrence rather than only a cost to suppress.

**Two corrections the design took.**

- **`priority:` cannot carry it.** `docket check` pins `P1` to `safety` and
  `science`, and `CLAUDE.md` forbids promoting process work into that band to
  move it up the order - the 2026-09-19 check-sequencing decision above hit this
  and had to move three items by sequencing instead. Every item this counter
  would ever fire on is workflow work, so an automatic bump is unavailable. The
  **generator tier** is the lever that exists, sits above every band but `P0`,
  and already means what a recurrence count measures: "every session it stands
  through pays it again."
- **It surfaces, it does not promote.** `subprojects/docket/README.md` calls
  `root-cause-of:` "the one place in the store where a typo would buy a
  promotion". A title-similarity heuristic writing that field reintroduces
  exactly the hazard `docket check`'s validation closes, on a match that is a
  judgment about prose. So the count is recorded as auditable fact and a reader
  decides.

**What the mechanism keys on, measured rather than assumed.** Title similarity
is refuted: over the 1,362-item store it catches 0 of 13 known duplicate pairs
at any usable threshold, and the only clusters it *does* find are the items
meant to recur - sixteen triage passes, plus release cuts and tags. Shared
`touches` catches 9 of 13, and narrowing by shared path then ranking by title
puts the true duplicate in the top 3 for 8 of 9. `PL-TZ7T` carries the full
table.

**The feature is `recurrence-signal`, four items.** `PL-TZ7T` (detect at
`docket new`, key corrected), `PL-X5JR` (record the recurrence and surface at
three), `PL-THLT` (infer candidate paths from the working tree, the gap
`PL-0KQP` fell through), `PL-4JHS` (backfill what the store already paid for).
`PL-G21K` is the separate defect underneath the cluster that started this.

**Amended 2026-09-20 on build, both halves measured** (project owner, ratified).
Two constants moved from what this section specified, and they turned out to be
one question:

- **The threshold is two recurrences, not three.** "Three keeps one threshold in
  the project" was right about the principle and wrong about the arithmetic: a
  generator is the root cause of three or more *items*, and the item carrying
  the recurrences is itself the first filing, so two recurrences is the same
  cluster size. At a literal three the slug-rename cluster - `PL-LBR6` with
  `PL-5QLP` and `PL-QMC0`, recorded as a generator by hand - could never have
  surfaced. `MIN_RECURRENCES` is now derived as `MIN_ROOT_CAUSE_ITEMS - 1`.
- **The similarity floor is 0.15, not the 0.10 it shipped with** (`PL-DGP0`,
  filed by `claude/practical-cerf-nx84jg`, the branch that yielded `PL-TZ7T`).
  Measured through the shipped function over 18 pairs in five recorded clusters:
  0.15 loses two *pairs* and no *cluster*, while cutting the captures that print
  anything from 55% to 22%.

**They interact, which is the part worth remembering.** At the literal three,
0.15 surfaced nothing and 0.10 surfaced one cluster, so the floor genuinely
mattered and the pair-recall argument that chose 0.10 was sound on its own
terms. Correcting the threshold is what made the higher floor free. Neither
constant should be moved without re-measuring the other.

**The backward sweep ran, and the backfill it fed is done (2026-09-20).**
`PL-JKML` read 400 pairs in full over the open store, put all 42 non-distinct
verdicts to an independent reviewer told to refute them, and **17 stood - a 60%
refutation rate**, which is the number to carry: reading two briefs and finding
one defect is not a reliable verdict on its own. `PL-BYMX`/`PL-SH9Q` was one of
the casualties, so the three-way this paragraph used to predict is not one;
what survives there is `PL-KSCW` absorbing `PL-SH9Q`, with `PL-MBTZ` grouped
beside it as a complementary half rather than a duplicate.

`PL-4JHS` then wrote those confirmed pairs into `recurrences:` - thirteen
entries on nine anchors - and the honest result is smaller than its `payoff:`
line claimed. **Exactly one anchor surfaces**: `PL-W7WL`, at three filings
(`PL-66X4`, `PL-2M5T`, `PL-3HMQ`). `plan.recurring` names open items only, and
the two other anchors reaching the threshold - `PL-STC4` and `PL-LBR6` - are
both closed, so their entries are record rather than signal. *(Amended
2026-09-21 by `PL-CJ5R`: it also excludes an item in flight on a branch, for
the same reason it excludes a closed one - the promotion moves a queue
position the item no longer has. `PL-W7WL`'s own promotion was ratified while
it was being implemented and would have written a no-op. It has since closed
with `#817`, so the one anchor this paragraph reports as surfacing no longer
does, and `PL-SHTR` at two filings is the whole of the named set.)* The backfill's
real deliverable is that five open anchors now sit at one filing instead of
zero, so the *next* re-filing of any of them crosses the threshold rather than
the third. `PL-4JHS`'s own brief carries the table.


## main's red is the queue, not the tree - PL-T83R's 109 failures attributed by failing step (2026-09-20)

**Closes the middle third of the "three silently-wrong checks" thread above.**
`PL-T83R` was filed on a rate - 32.7% of `main` pushes reaching a verdict
failed - and asked for the 74 to be attributed before anything was designed,
because "if most of the 74 are that class, the answer is different". They were.

**All 819 completed `main` push runs of `quality.yml` from 2026-08-22 to
2026-09-20**, with the failing step of each of the 109 failures read from
`/repos/.../actions/runs/{id}/jobs`:

| first failing step | all 109 | the item's 74 |
| --- | --- | --- |
| `verify replay, the whole store` | 93 (85.3%) | 73 (98.6%) |
| the bare `bin/docket check` | 14 (12.8%) | 0 |
| the pytest/coverage line | 1 | 1 |
| no job ran (startup failure) | 1 | 0 |

**Not one of the 109 was a defect in `src/`** - the single pytest failure is
`test_this_repository_records_a_disposition_for_every_open_debt_item`, which
asserts on `ROADMAP.md`. In all 93, the bare `bin/docket check` step passed
*earlier in the same job on the same tree*, along with `ruff`, `mypy` and the
suite at 100% branch coverage; the bare run is the same validation without
`--verify`, so the cause is isolated to the one report `--verify` adds without
reading a log at all.

**The rate turned out to be the wrong statistic, and that is worth carrying
past the item.** 74 failures are **8 episodes**: merges keep arriving while
`main` is red, so the per-push rate counts the outage once per merge. Two
episodes - 37.7 h and 44.3 h - hold 87% of the window's red time, and each
ended in one cheap commit (`#432` closed two items whose work had landed,
`#493` rewrote one command that did not discriminate). Measured as wall clock
instead, `main` was red **39.0%** of the window and **6.1%** of 2026-09-16 →
2026-09-20, with episode length down to about an hour. The defect was time to
green, not frequency - and it was shrinking on its own before anything changed.

**So the class was not suppressed.** Per `.claude/rules/expert-review.md`,
making `already_passing` an advisory on `main` is right only if enough of what
it hides would not have mattered: the count is **93 of 93 real**, every one a
store defect somebody later fixed. The line was made precise instead - it now
names the failing step, and where the replay failed alone it says the red is
the queue and hands over `bin/docket check --verify`.

**What is still open here.** `PL-JTHW` (the same file: a `cancelled` `main` run
is passed over in silence, so a commit with no verdict looks like one nobody
asked about) is the remaining hole in the same line, and is untouched by this.
Whether a *second* consecutive red should read differently from the first was
not designed: at 8 episodes over 10 days there is no evidence it would change a
decision, and inventing a rule for it now would be the altitude error
`.claude/rules/expert-review.md` warns about.

## v0.6.0's headline is the area/View system itself, which reshaped three things on 2026-09-21

A design round after v0.5.0 shipped, asked as "reassess where we are and
finalize the plan to v0.6.0". The plan needed no finalizing - v0.6.0 was scoped
2026-09-16 and re-affirmed 09-17 - so what the round produced is three ratified
decisions and one defect, none of which is implemented. `PL-M3X6` and
`PL-C4W8` carry the detail; this thread is what spans them.

**The project owner's argument, and it is the spine of all three.** UI decisions
about layout and location - where a y-axis control lives, how many readout
columns fit, what an axis is scaled against - are informed by what a View looks
like. Settling them now against a monolithic GUI means settling them twice.
Stated plainly at the end: **the app should not look as it does now at v0.6.0;
the modular workspace/area/View system is the headline feature.** A session
reply in this round said the opposite - that v0.6.0 leaves the app looking much
as it does today - and was corrected. That reply had conflated the visual pass
over the *existing* dashboard (item 33, `v0.7.x`, correctly deferred) with the
appearance of the surfaces this milestone *creates*, which nothing owns.

**1. `PL-M3X6` - Required-scope entry 20.** Entries 1-19 are all mechanism and
none says what any of it looks like, while § "Explicitly out of scope" sends
"the visual composition of each surface" to item 33. The membership test is
*does this surface exist in the application today* - the new-versus-inherited
axis, deliberately not furniture-versus-content, because the unconditional
region is content and the two failure states are states, and all three qualify.
Seven members, and the pixel budget across them: a tab strip, Area headers and
live handles all take screen from the chart, on a window where `PL-Z4K6`
already questions seven readout columns at 1366 px.

**2. The gate reclassification, recorded on `PL-C4W8`.** An entry v0.6.0 would
re-decide carries `feature: interface-areas` and is cleared *by* the milestone.
This is re-labelling, not renegotiation: `plan.py`'s rule is "Cleared by the
milestone itself: open debt carrying its feature", the freeze holds, every entry
stays on the list, nothing defers to Gate 3. The bucket holds one member today
(`PL-VN6M`). The line: **ownership, placement and sizing move; units, wording,
arithmetic and guards do not.** Answered per entry against the tree, never per
feature in bulk - and against a live counter-precedent, since the same
"it will be redone anyway" argument was made for the Qt port absorbing item 33
and falsified by measurement at 10 insertions and 29 deletions in `theme.py`.

**3. `PL-D8KW` - the defect, and it is upstream of everything above.** Cadence
beat 3 requires a staleness sweep before any gate entry is worked, and three
places name `PL-6ZQY` as the standing instrument: `ROADMAP.md:6172`,
`ROADMAP.md:5394` and `.claude/skills/docket/modes/release.md:43`. `PL-6ZQY`
closed 2026-09-19, two days before Gate 2 froze, and its brief ends "What this
item still owes: Nothing." A session follows the instruction, reads `done`, and
skips the beat with nothing failing.

**Measured in the round, for whoever picks this up.** Gate 2 stands at 183
entries, 168 clearable: 110 S, 58 M; 113 `ready`, 47 `needs-decision`, 8
blocked; 95 apparatus, 43 product, 27 both. 41 of the 168 are learner-visible,
11 of those need an owner decision. v0.6.0's own 23 Required-scope items are
4 L, 16 M, 3 S at dependency depth 4, and **only two are startable** -
`PL-1FT6` alone unblocks 8 directly and gates 20 transitively, which is the
schedule risk in this milestone. Gate 1's precedent: 185 entries frozen
2026-09-06, 184 cleared by 2026-09-21, alongside v0.5.0's own scope.

**Nothing here is built.** `PL-M3X6` and `PL-C4W8` are both `untriaged`, the
`ROADMAP.md` edit for entry 20 has not been made, and the reclassification has
been applied to no entry. The session stopped at 158k of spend, not for the
work.

## Gate 2's staleness sweep answered question 1 and was stopped from writing question 2, 2026-09-21

`PL-C4W8` ran beat 3 against the 168 clearable entries of the list frozen
2026-09-21. `PL-D8KW` landed in the same branch. What spans them, and what the
next session needs:

**Question 1's answer is nothing like the precedent predicted, and the
difference is explainable.** The 2026-09-19 pass put 13% of a verified sweep
and 32% of an unverified map dead or overstated, so `PL-C4W8` expected roughly
22 to 54 of 168. The measured rate is far lower: 2 dead and 5 overstated across
the entries swept, around 5%. The reason is visible in the two drops - both
were killed by a *single large event*, the 2026-09-15 PySide6 port (`PL-3JP0`)
and one queue-tool fix (`PL-Z9K5`). Gate 1's entries had a Flet-to-Qt rewrite
sitting in the middle of their lifetime; Gate 2's were filed almost entirely
after it, against a tree that has since only been added to. A staleness rate is
a fact about how much upheaval a window contained, not a constant of the store,
and the next gate should re-derive it rather than inherit either number.

**Question 2 was answered and deliberately not written.** `PL-YVP7` carries it.
`plan.py`'s `gate()` puts an entry inside the milestone only when
`item.feature == feature`; `feature:` holds one string; and 147 of the 170
clearable entries already carry one. So "the entry carries `feature:
interface-areas`" is not a label added beside what an entry has - it is written
over it, destroying the membership `bin/docket feature` reports completion
against. Every confirmed candidate is in that 147: `PL-CNCF` and `PL-PGZF`
carry `chart-readout`, `PL-WZVZ` carries `anesthesia-machine`. The sweep
recorded its verdicts and stopped rather than spend a ratified decision's
mechanism on entries it would damage.

**The verdicts themselves are sound and should not be re-derived.** Two entries
turn on the mechanism the milestone names outright - `simulation_view.py`'s
`plot_width_px=max(concentration, wash_in)`, the column budget read across
sibling plots that stop being siblings - and that was checked directly against
the tree rather than taken from a report. `PL-WZVZ` is the one to leave alone
whatever is decided: it is `safety`-classed, inherited from Gate 1, and
`ROADMAP.md`'s gate section writes out by name where it sits and why.

**The counter-precedent held up.** The Qt port was argued to redecide the
visuals and did not (10 insertions, 29 deletions in `theme.py`). Sweeping for
question 2 found the same discipline pays: three of the design round's six
named candidates - `PL-V67Q`, `PL-QYBW`, `PL-Z4K6` - came back NOT on
inspection. `PL-Z4K6` is the sharpest case, since `ROADMAP.md` already reasons
that two of its three levers wait on planned-milestone item 33 in `v0.7.x`
rather than on this milestone. Titles read in a design round are not evidence,
which is what this pass existed to demonstrate.
