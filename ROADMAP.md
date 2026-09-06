# Project roadmap

This file is the authoritative version and milestone map for the project. If a
build guide, issue, or conversation conflicts with this file, update the
conflicting artifact or amend this file deliberately in the same change.

Scope of this file: releases only. Discrete tasks — defects, fixes,
cleanups, optimizations, and small features — are tracked and prioritized
in `docs/items/`, not here. An item is a milestone rather than a
queue item when it needs its own goal, required scope, definition of
done, and explicit out-of-scope list.

## Versioning decision

The project uses milestone-based semantic versioning during early development.
The next release number is chosen for the capability boundary it crosses, not
by mechanically incrementing the patch number.

**One deliberate exception, v0.3.0 (project owner, 2026-08-26).** That rule
would make clearing Gate 0 a patch: it crosses no capability boundary — two
safety fixes, four refactors, two tooling defects and a perf fix, after which
the simulator does nothing it could not do before. It is nonetheless released
as the minor v0.3.0, because clearing the inherited pre-MVP backlog is the
boundary this project most needs to be able to point at, and a patch number
would bury it.

**This is an exception and not a precedent.** It applies to Gate 0 alone,
which is unlike every gate that follows it: Gate 0 is the accumulated backlog
from before the debt gate existed, twenty items deep, while Gate 1 onward hold
the findings of a single milestone. Later gates ship *inside* the milestone
they gate and take no version of their own — see "The cadence" under "The
debt gate". Absent a further deliberate exception recorded here, the
capability-boundary rule above governs.

| Version | Status | Milestone |
| --- | --- | --- |
| v0.0.1 | Completed | Initial runnable prototype: deterministic simulation clock, controller/view separation, basic charting and controls, and project quality tooling. |
| v0.0.2 | Completed | Analytically validated ideal breathing-circuit wash-in and washout with no patient uptake. |
| v0.1.0 | Completed | First patient sevoflurane uptake and distribution model - the "Sevo works" milestone. |
| v0.2.0 | Completed | Isoflurane and desflurane added as additional loadable volatile agents. |
| v0.2.1 | Completed | Validation hotfix: the vaporizer maximum is enforced in the core and rejects rather than clamps, the agent MAC cross-check fails closed, and the cited reference-adult defaults reach the running app. |
| v0.2.2 | Completed | Hardening and interface-provenance release on the same model: a failed step halts the run visibly instead of leaving it reading "Running", the parameter schemas reject unknown keys, agent selection carries its ISO 5360 identification color, and a dead non-conservative ventilation path is deleted. |
| v0.2.3 | Completed | Hardening and verification release on the same model: displayed concentrations are rounded to the resolution the solver actually supports, the chart payload is bounded and the render cadence decoupled from the simulation's, and the coupled dynamics are gated on an independent RK4 solution rather than on mass balance alone. Six further items rebuilt the development queue, swept the documentation, and recorded release provenance. |
| v0.2.4 | Completed | Verification and delegation release on the same model: fourteen previously untested capacity and validation guards in the scientific core and the controller now have tests, `_halt_run`'s deliberate suppression is covered by a test rather than only a comment, and work whose success a command can prove can be handed to a cheaper model and verified in one step. |
| v0.2.5 | Completed | Licensing, documentation and planning release: the project is licensed Apache-2.0, v0.3.0 through the MVP is scoped onto one timeline with its debt gates, Phase 0 is retired in favour of the standing debt gate, and `docs/worker.md` states what a delegated worker decides for itself. No source file changed. |
| v0.2.6 | Completed | Delegation and release-tooling release on the same model: work whose success a command can prove now has to name that command and have run it, `docket` computes the debt gate and the cadence beat instead of a session transcribing them, and the release path stopped leaving `uv.lock` stale, while drift between this table and the version file became something a check catches - caught, not prevented, since nothing writes the row. The one scientific item widened the splitting-error bound to the whole settings envelope. No equation, parameter, or numerical method changed. |
| v0.2.7 | Completed | Session-discipline and applicability-domain release on the same model: the simulation step now refuses inputs outside the operator split's stated applicability domain and the splitting-error bound is measured across setting changes rather than one held operating point, while ten process items closed the three channels by which product work leaked into discussions that were not about it, gave multi-step instructions a written standard, and cleared three live tooling defects. No equation or parameter changed, and the numerical method is unchanged - it is now guarded at the domain it was always specified for. |
| v0.2.8 | Completed | The workflow works: thirty-eight frozen entries of development machinery the project already runs on - the merge path, the release script, the queue's ranking, the in-flight answer six commands read, the type-check and lint gates, and the instructions a session reads before it does anything. Seventy items in all. No simulator change: `src/` differs from v0.2.7 by three comments, and `docs/MODEL.md` only by the math syntax GitHub renders and by recording why the operator split is kept over an exact matrix exponential. No equation, parameter, numerical method, unit or displayed value changed. |
| v0.2.9 | Completed | Validation, accessibility and tooling patch on the same model, changing no source file at all: `src/` is identical to v0.2.8. Modelled wash-in is compared against published human measurements for the first time — verification became validation, with the two caveats that bound how strongly it may be stated recorded beside it — the interface gained a recorded WCAG 2.2 AA conformance target whose contrast ratios `make check` computes rather than a comment asserts, and three live defects in the queue's own ranking are closed. No equation, parameter, numerical method, unit or displayed value changed. |
| v0.2.10 | Completed | Interface-safety and accessibility patch on the same model: the supported input ranges became the model's own and are refused in `core/` rather than only bounded by the sliders, the alveolar readout stopped calling a modelled value "end-tidal", every readout now names its compartment above a smaller clinical gloss and shares one baseline with its neighbours, two colours that failed WCAG AA on clinical text were replaced, and the application acquired a name. Five tooling items closed live defects in the queue's ranking, its verify timeout, and the cost `make check` pays to run it. No equation, parameter, or numerical method changed, and no displayed number changed. |
| v0.2.11 | Completed | Transactional-step and core-boundary patch on the same model: a simulation step that cannot be completed is now rolled back in full, so a halted run shows the last completed step rather than four of five sub-exchanges applied in order, and the entry point to the scientific core is named `AgentUptakeSystem` for what it owns rather than for anatomy that is one of its four compartments. `BreathingCircuit.set_circuit_volume()` conserves the agent in the circuit, closing a setter that destroyed 24 mL of it and made the *next* step fail for it. Two documentation items and one tooling item closed alongside. No equation, parameter, or numerical method changed; the only displayed values that differ are the ones a halted run shows, which is what the release is for. |
| v0.2.12 | Completed | Provenance and parallelism patch on the same model, changing no equation, parameter or numerical method and leaving `src/anesthesia_sim/data/` byte-identical to v0.2.11: `docs/MODEL.md`'s prose values are now held to the data files they restate rather than only its provenance table, so a data-file edit can no longer leave a stated figure quietly wrong, and a figure derived from several values reports that it needs recomputing when an input moves. The in-flight answer that keeps two sessions off one item reached only `docket show`; it now reaches `docket triage`, reads the harness's session list for a session that has pushed nothing, and answers in a shallow checkout instead of declining. `src/` changes in three files and only twice over: two uncalled descriptive time constants are deleted, and the boundary between a load-time payload and the public type it produces is documented at the classes themselves. |
| v0.3.0 | Completed | The foundation: Gate 0's inherited backlog cleared, 21 of 21 frozen entries closed across the v0.2.6 to v0.3.0 patch series — the splitting-error bound widened across setting changes, the simulation step made transactional and bounded to the split's applicability domain, the `core/` boundary refactors, and the live tooling defects. This cut carries the last two gate entries: the render loop stopped rebuilding what it could move (6.3x cheaper frame), and `BreathingCircuit` stopped defaulting to one agent's vaporizer maximum. No new capability, and no equation, parameter or numerical method changed; see the versioning exception above for why it is a minor. |
| v0.3.1 | Completed | Provenance-integrity and rollback patch on the same model, adding no capability and changing no equation, parameter or numerical method: `src/anesthesia_sim/data/` is byte-identical to v0.3.0, `docs/MODEL.md` is unchanged, and `src/` changes in one file. `AgentUptakeSystem.advance()`'s rollback moved off its `except` clauses onto the unwind path, closing a measured hole where a `BaseException` left a partly applied step in the live system, and `reset()` now anchors the mass-balance accounting period to what the compartments hold rather than to a zero it did not itself establish. The rest is the queue's own record of what closed an item: the retired `commit:` hash a squash discards is replaced by the pull request number, recovered from file history and refused at the pull-request title; duplicate front-matter keys, undeclared `classes:` and `feature:` values, and a merge that deletes a captured item became errors rather than silent corruption; a `verify:` command is owed as an error when a grandfathered item closes; and a scheduled job reports whether the tree still builds on a toolchain nobody pinned. |
| v0.3.2 | Completed | Provenance-honesty patch, and the release that decided how this project's numbers may be cited. Every shipped Python file is byte-identical to v0.3.1 and every stored numeric value is unchanged; what moved is what the citations claim about them. `docs/MODEL.md` gained a three-tier source hierarchy — primary measurement, secondary synthesis, reference implementation — and only the first may be named as the authority for a stored value, which makes the shipped parameter set Gas Man's and says so, where the agent files had let a journal's name stand in for a measurement nobody made. The isoflurane blood:gas question is recorded rather than answered: 1.3 is stored, 1.46 is what Lerman et al. measured in adults, and the 11% gap is the widest in the project. Alongside it, the numerical method's future is settled — the operator split is to be replaced by an exact matrix exponential so the code that computes a value is the governing equations, with the state vector decided as fractions — and two live defects close: the conservation guard's three sensitivity constants are pinned, and the pull-request title check moved to a workflow that can observe the rename it asks for. No capability, equation, parameter or numerical method changed. |
| v0.3.3 | Completed | Delegation and interface-boundary patch on the same model, adding no capability and changing no equation, parameter, numerical method, unit or displayed value: `src/anesthesia_sim/data/` is byte-identical to v0.3.2 and the one `src/` change is behavior-preserving. The queue's own provenance stopped needing a person: a closed item's pull request number is written by `bin/docket record`, riding whatever commit the session was already making, after the job meant to write it at merge time proved unlandable - a push made with `GITHUB_TOKEN` starts no workflow, so `main`'s required status checks can never report on the commit it pushes, and every configuration that would accept the push weakens that gate instead. That closes the `delegation` feature at 12 of 12. Alongside it, `app/simulation_view.py`'s displayed-precision formatters and chart-series assembly moved into two Flet-free modules, so `docs/MODEL.md`'s displayed-precision derivation now terminates in a function that can be read, cited and tested without loading the interface - stages 1 and 2 of v0.4.0's Required scope, landed ahead of the milestone. `core/` gained a 100% statement-and-branch coverage gate over the saturation it already had, before v0.4.1's exact-step solver arrives to be measured against it, and the pull-request title check now runs at the declared Python floor. |
| v0.3.4 | Completed | Documentation- and tooling-truth patch: every shipped Python file is byte-identical to v0.3.3 and `src/anesthesia_sim/data/` is unchanged, so no equation, parameter, numerical method, unit or displayed value moved. The whole release is the project correcting statements it was making about itself. `docs/MODEL.md` had named v0.2.3 as the current released baseline for thirteen releases, and still recorded the operator split as kept on a decision the 2026-09-03 re-scope reversed; both are corrected, and the specification now names no current version at all, because a second copy of one goes stale silently at every release. Two checks that reported a false state were repaired and retired: the top-band advisory no longer counts blocked items a session cannot start, and `doc_check`'s baseline-tag advisory is gone, because a local checkout cannot tell a release never tagged from one tagged since it last fetched. |
| v0.3.5 | Completed | Gate-measurement patch changing no shipped code at all: `src/` and `src/anesthesia_sim/data/` are byte-identical to v0.3.4 and `docs/MODEL.md` is unchanged, so no equation, parameter, numerical method, unit or displayed value moved. The release is the project's own quality gate learning what it costs, saying so truthfully, and getting roughly twice as fast. `pytest-xdist` at `-n auto` took the suite from 78 s to 27 s with coverage byte-identical at 100%, `make check` from 115.0 s to 59.2 s and the CI step 28%, and `make test` — the whole-suite target a session reaches for while iterating — followed at 88.5 s to 31.8 s; no test was skipped, disabled or relaxed to pay for it. Two advisories that quoted figures measured once and left to go stale now print what the run actually cost. The two questions those measurements raised — the docket suite's share of the wall clock, and `bin/docket check` becoming the gate's largest item — were decided as accept-with-evidence rather than left open, each carrying the numbers that would have to change to reopen it. And two silent-divergence holes closed: the local and merge coverage gates are held to one command by a check rather than by two comments asking to be kept the same, and the guard that keeps two sessions off one item now reads what files it touches, not only who is on it. |
| v0.3.6 | Completed | The first two teachable-case items, and the first release since v0.2.3 to change what a learner sees: every compartment is displayed in MAC multiples alongside percent, on a chart that gained a percent axis left and a MAC axis right, and two horizontal clinical references - a band at the running agent's population MAC-awake, one standard deviation either side of the published mean, and a line at its nominal 1 MAC - so the gap between them shows the decrement required for arousal rather than only the endpoint. Display and provenance work rather than model work: no equation, parameter, numerical method or solver step moved, `core/` computes neither reference, and what the agent files gained is three measured constants with primary citations checked against source, stored as fractions of MAC so they survive a change to `mac_percent`. `docs/MODEL.md` records what a MAC multiple on a non-alveolar compartment does and does not assert, that the band is read against the vessel-rich trace and not the alveolar one, and that the interface displays no time-to-wake-up figure of any kind. Alongside them, `core-boundaries` closes: one module may import Pydantic and a check enforces it. The queue itself learned to answer per lane, so two simultaneous sessions no longer rank onto the same item. |
| v0.3.7 | Completed | The run records its own inputs, and the interface stopped degrading under one: every setting change the model was stepped under is now recorded with the simulated time it took effect, marked on the chart as a third kind of series - vertical, labelled as a record of a user input rather than of anything measured - and listed beside it as the acts that produced it. The record is faithful rather than tidy: a slider reports continuously while dragged, so one turn of a dial is several settings the run really was computed under, and the display groups them on a boundary the interface declares rather than on a time threshold the coming playback multiplier would invalidate. Changes superseded within one simulation step collapse into the one the step integrated, because the rest describe a run that did not happen, and the recorded value is read back off the compartment rather than taken from the caller. Alongside it the render stall closed: what saturated the Flutter client was 2 700 discrete control mutations a frame, not data volume, and anchoring the chart's decimation to the run rather than to the moving window leaves a steady frame moving the newest bucket and the final sample. Two features close - `delegation` at 13 of 13 with the stop hook's comparison point corrected, and `provenance` with three review-article PDFs filed as cited references - and three defects in how the queue answers. Display and interface work: no equation, parameter, numerical method or solver step moved, and `core/` neither records the timeline nor knows it exists. |
| v0.3.8 | Completed | The wash-in curve the literature teaches from, and the render path that can carry it. F_A/F_I is plotted on its own bounded axis beneath the compartment chart, broken into segments wherever the ratio leaves its domain rather than joined by a line across the gap, labelled as a ratio against modelled inspired rather than against the vaporizer dial, and carrying the constant-F_I caveat in `docs/MODEL.md`: it is the textbook wash-in curve only while the dial is held, and a learner who misses that reads a dial change as uptake. Underneath it, what one frame reads stopped growing with the run. The snapshot carried a copy of every sample ever recorded - 4.08 ms at half a million samples, five times a second - and the chart discarded all but the visible few hundred; the controller now answers for a window cut at the axis the caller is about to draw, so a frame reads at most the visible window's own width divided by `SIMULATION_STEP_S` samples whether the run is a minute or a week old, and the decimation scan reads each sample once where it read about 2.8 times. Display and interface work: no equation, parameter, numerical method or solver step moved, and the ratio is a quotient of two modelled states `core/` already held. Alongside them, the literature route this environment actually has - direct HTTP to publishers is refused, the PubMed server answers - is recorded where a session about to write provenance will read it rather than only where a delegated worker would, and two sessions that discover they are on one item gained a rule for which of them yields. |
| v0.3.9 | Completed | What a frame costs, what a learner is allowed to look at, and what a run *is*. Decimation had rescanned every sample in the visible window on every frame — 62.6 ms at a four-hour window and 207.7 ms at twelve, against a 200 ms frame budget — and now reads precomputed M4 aggregates held on a dyadic grid anchored to absolute sample index, merged tier to tier without revisiting a raw sample, so a frame costs what it draws rather than what the window holds. Beside it, a checkbox per compartment: the reference implementation's own affordance, the two-trace comparison a question like *why does fat lag muscle* actually needs, and the one lever on render cost that trades no fidelity, since a trace nobody is looking at is not a resolution loss. Underneath both, simulated time became the number of steps taken times the run's step rather than a sum accumulated a step at a time, and `docs/MODEL.md` states as a guarantee what had been an implementation detail: a run is a function of its inputs and its step count and of nothing else, so a machine that wakes the loop late runs slower and never differently — with the four things that guarantee does not cover named beside it. Interface and determinism work: no equation, parameter, numerical method or solver step moved, `src/anesthesia_sim/data/` is byte-identical to v0.3.8, and no displayed number changes — the recorded sample times differ in their last bits, about 35 ns after four hours, which no readout, axis or trace resolves. Three apparatus defects close alongside: a commit pushed after its own pull request merged is reported rather than silently dropped, the check that reports it stopped calling merged work lost, and `docket next` reserves what it recommends, so two sessions handed the same answer do not both start it. |
| v0.4.0 | Completed | The teachable case: the release that makes the model's lessons observable at all. A case runs at 1, 5, 20, 60 or 300x in steps that never change size, on a time base spanning fifteen minutes to twelve hours that defaults to fitting the run, against a vertical axis fixed at 0-3 x MAC for every agent rather than at one agent's vaporizer dial maximum - so the three obstacles this milestone was scoped on are answered together: the reservoirs that cause context-sensitive emergence (muscle at 135 min, fat at 42 h for sevoflurane) become reachable in minutes of wall clock, a 1 MAC run fills the plot instead of its bottom quarter, and three agents whose MACs differ threefold are finally comparable. Changing agent is now an explicit new case that names what will be lost before discarding it. Underneath, the recorded run is keyed by substance and quantity rather than by six flat compartment floats, so nitrous oxide will add a substance rather than reshape the record v0.5.0's forking proof is written against. Interface work on an untouched model: `src/anesthesia_sim/core/` and `src/anesthesia_sim/data/` are byte-identical to v0.3.9 and every changed source file is under `app/`, so no equation, parameter, numerical method or solver step moved, and the v0.0.2 circuit, v0.1.0 sevoflurane and v0.2.0 multi-agent reference tests are unchanged and passing. Twelve of the milestone's thirteen Required-scope entries have landed; `PL-011`'s retention rule is the thirteenth and was dropped on 2026-09-05, superseded by the score architecture rather than deferred, with the outcome recorded in place in that section. The remaining twenty-one items of the thirty-six are apparatus: the release script's own in-flight guard after two sessions cut v0.3.7 independently, the resident-instruction budget, and eleven live defects in the queue's ranking and its checks. |
| v0.4.1 | Completed | The apparatus patch, changing no shipped code at all: `src/`, `tests/` and `docs/MODEL.md` are byte-identical to v0.4.0, so no equation, parameter, numerical method, unit or displayed value moved and the reference cases pass against exactly the code that validated them. The fourth release to change nothing shipped, and it comes straight after the largest capability release the project has had, because cutting v0.4.0 walked the plan end to end for the first time in weeks and found it out of agreement with the tooling that reads it. `bin/docket wave` was classifying the `v0.4.1` row as a milestone - which freezes a debt gate - and that gate computed to **105 entries against Gate 0's 21**; the row is now `v0.4.x`, a patch track that freezes none, and the beat reads *scope v0.5.0* as the timeline always intended. The score architecture (`PL-T691`, `PL-2FM6` and three more) is placed in v0.5.0, where forking needs it and where `PL-011`'s dropped retention debt is actually paid. The advisory that catches an undeclared prose prerequisite was reading only the first id after a cue, so "blocked on A and on B" never checked B - it had a live instance in `PL-VZL0` and reported clean. Three contradictions inside the next release's own briefs are cleared, each of which would have stopped a worker on day one, including a two-item deadlock where `PL-GS5X` and `PL-X9KD` each waited on the other. Every CI job gained a `timeout-minutes` bound against a 360-minute default, superseded pull-request runs are cancelled for the runner slot rather than the now-free minute, and `CLAUDE.md` finally states when investing in the apparatus is correct rather than only warning against it. Eleven items. This is not the exact matrix exponential - that is the `v0.4.x` track's content and has not started. |
| v0.4.2 | Completed / current baseline | The apparatus patch that closes `docket-store`, changing no shipped code: `src/` and `docs/MODEL.md` are byte-identical to v0.4.1 and the only file under `tests/` that moved is the new check's own suite, so no equation, parameter, numerical method, unit or displayed value moved. Its subject is the instruction budget every session pays and the guards that keep work visible. Resident text can now *shrink*: 563 characters whose carriers already existed were routed out of `CLAUDE.md`, and resident rules gained the retirement test that checks have had since `PL-ZBJ0` — until now a rule could only be added, because nothing said when one had stopped earning its place, and the total falls 44 545 to 44 166 characters. Beside it `tools/rules_paths_check.py` gained its second rule: a `paths:` entry that is anchored and points at nothing is refused, the same silent failure as the `./` spelling v0.4.0 closed, arriving in the form that reads as correct at every glance — a transposed directory name — and the message names the nearest existing ancestor rather than only the offence. Two provenance guards close: seven items stranded on abandoned branches are recovered, two of them created by the score-architecture drops, and the pull-request title check stopped racing the retitle it asks for, which had been showing a red run that meant nothing on a green pull request. Landing during this release's own pull request, the gate learned what it costs to run: the `floor` job billed a whole minute for eight seconds of work and held one of twenty account-wide concurrent job slots, so its steps moved inside `checks` *ahead of* the uv install — which strengthens the no-virtualenv claim rather than weakening it, because at that point no virtualenv exists to fall back on — and a spending limit and usage alert now exist, where the first sign of Actions overage had been the invoice. `README.md`'s status section is corrected too: it understated the operator split's disagreement with the exact solution as 1.2e-2 percentage points where `docs/MODEL.md` gives 2.3e-2 over the same domain, which is the kind of divergence between a summary and its specification that the `v0.4.x` track exists to remove. Nine items, one of which is the v0.4.1 cut itself. |

**Tags.** Every version the table above marks Completed carries an annotated
tag. Which ones those are is deliberately not restated here - the table is the
list, and a second copy is a second thing to keep true, which it twice was not.
`tools/doc_check.py` reads the completed rows against `git tag` instead, so a
release that shipped without one fails the check rather than waiting to be
noticed. `git describe --contains` therefore resolves for every commit up to
and including the latest release - verified on 2026-08-30 across the whole of
`main`; the commits it does not resolve are the unreleased ones after the
newest tag, which the next release's tag will cover. That span is the
provenance guarantee PL-J3ZK was opened to restore.

The tag goes on the merge commit, so between cutting a release and pushing its
tag the newest version is Completed and carries none. That window is reported
as an advisory rather than an error: failing it would turn `make check` red on
every release branch, which is the failure PL-8HJ2 removed arriving by another
door. `bin/docket release` refuses to cut the *next* release while that tag is
still missing, which is what stops the window from staying open.

A version that has genuinely gone out untagged is named in a bold sentence
here, and the checker holds the count that sentence states to the versions it
names. There are none.

**The gap is closed, 2026-08-30.** v0.1.0 (`97cc66a`) and v0.2.0 (`796bf4f`)
were the last two, and were recorded for a time as untaggable: `main` appeared
to have three unrelated roots and `git merge-base 796bf4f 97cc66a` returned
nothing. That was measured in a shallow checkout, where boundary commits
report as parentless. In the full history there is one root, `97cc66a`
(v0.1.0) is an ancestor of `796bf4f` (v0.2.0), and that is an ancestor of
`bc5f823` — so the tags were placed where the release commits actually are.
The superseded reasoning is kept here because a shallow checkout will produce
it again for anyone who repeats the measurement.

There is no active v0.0.3 milestone. Any guide that labels the first patient
sevoflurane build as v0.0.3 is superseded by this roadmap.

## Current baseline: v0.4.2

v0.4.2 changes no shipped code. `src/` and `docs/MODEL.md` are byte-identical
to v0.4.1, and the two files under `tests/` that moved are both about the
apparatus — a new check's own suite and the portability suite that follows the
CI restructure — so no equation, parameter, numerical method, unit or displayed
value moved, and the reference cases pass against exactly the code that
validated them. What changed is `.github/workflows/`, `.claude/`, `CLAUDE.md`,
`README.md`, `ROADMAP.md`, `docs/`, `tools/` and `tests/unit/`.

It is the fifth such release — v0.2.5, v0.2.9, v0.3.5 and v0.4.1 were the
others — and the second in a row. That is worth stating plainly rather than
glossing: two consecutive releases have shipped no simulator change. Both are
the cost of cutting v0.4.0, which walked the plan end to end for the first time
in weeks and surfaced a run of apparatus defects that would each have cost a
session. `CLAUDE.md`'s statement that the apparatus is not judged by its share
of the queue was written during this pair, and this pair is why.

**Note what this release is not.** It is not the exact matrix exponential.
That work — planned-milestone item 29, "the code is the model" — is the
`v0.4.x` track's content and still has not started.

### Release narrative

**The resident instruction set could only grow (`PL-4H01`, `PL-NJTZ`).**
`CLAUDE.md` § "A check earns its place every run, or it is retired" gives every
check a retirement rule, and `PL-ZBJ0` carries the evidence for it. Resident
*rules* had no equivalent. `PL-H7XN` built a measurement and `PL-JK0M` ran the
routing pass, but neither answered when a rule has stopped earning the context
it costs — so the file could be added to on argument and removed from only by
someone willing to make the case from scratch each time. The asymmetry is the
defect: a budget with no retirement test is a ratchet.

There is now a test for it, and 563 characters went out through it — the lane
sentence, the finish-a-feature bullet and a quality-suite line duplicated from
its own carrier, each retired because something else already states it. The
resident total falls from 44 545 to 44 166 characters. The direction matters
more than the size: this is the first release in which the number went down
because a rule was *retired* rather than because prose was tightened.

**A rule's declared scope and its real scope could differ silently
(`PL-DNYL`).** `tools/rules_paths_check.py` shipped in v0.4.0 refusing an
unanchored `paths:` entry, which also matches its name at any depth, and the
`./` spelling, which matches nothing at all. It said nothing about an entry
that is anchored and points somewhere that does not exist.
`/scr/anesthesia_sim/core/**` passes the first rule and delivers its rule to
nobody, and it is worse than `./` on that check's own test: `./` is at least
visibly unusual, while a transposed directory name reads as correct at every
glance. Both failures are silent, and a rule is trusted in a way a check is
not — these files carry the standards a session is held to, so one that never
loads means work judged against a bar nobody applied.

It is a hard error rather than an advisory, on the project owner's decision
that a rule may not declare scope ahead of the code it governs: the rule is
written when the path exists. The message names the nearest existing ancestor,
which is what turns "this path is wrong" into "it stopped being real here".
What the check still refuses to decide is whether a glob describes the *right*
set of files — that is judgment, it differs per rule, and a tool guessing at it
would be the "worse than no tool" case.

**The gate learned what it costs (`PL-D551`, `PL-W9DW`).** The `floor` job
existed to prove the bare-interpreter contract: that `tools/` and `bin/docket`
run at the declared Python floor with no virtualenv. It proved it at the price
of a whole billable minute for eight seconds of work, and of one slot against
the account-wide twenty-concurrent-job cap — which is what actually throttles
several sessions at once, now that minutes are not the only constraint. Its
steps moved inside `checks`, *before* the uv install.

The order is the design rather than an implementation detail. A separate job
only assumed isolation; running these steps before uv is installed makes the
claim stronger, because at that point no virtualenv and no `UV_*` variable
exists to leak from. It also fails fast — a broken documentation reference now
costs one billable minute instead of five, since the suite never starts.
Alongside it, a spending limit and a usage alert: until now the first sign of
Actions overage would have been the invoice.

**Two guards that report on work were reporting wrongly (`PL-VSJZ`,
`PL-X1S4`).** Seven items existed only on branches nobody would merge,
including two created by the score-architecture drops themselves; they are
recovered into the store, where every command that ranks or counts work can see
them. And the pull-request title check was racing the rename it asks for: a
closing commit pushed before the retitle ran the check against the old title,
so a pull request that was correct showed a red run that meant nothing — the
precise failure mode `CLAUDE.md` names when it says an advisory nobody can act
on trains a session to skim the output where a real one appears.

## The plan

One timeline. Debt clearing and feature milestones are steps on the same
plan, in the order they happen — the gates are not a background assumption
behind the features, they are half the work.

### What MVP means here

**The MVP is complete when a learner can run a case, branch it at a decision
point, and compare the two managements side by side — in the unit clinicians
reason in, on a time base that spans a case.**

That is the Graph and the Overlay of the Gas Man reference simulator, which
is the design this project is building on. Everything after it extends a
working teaching tool rather than working toward one. The boundary is drawn
there because comparison is what isolates the variable under study: running
one case teaches a curve, and running the same case two ways teaches why the
curve moved. A simulator that cannot do the second is a demonstration, not a
teaching tool.

Two *feature* releases reach it, and both are interface releases on the
existing, already-validated model — preceded by the v0.2.8 patch, which
makes the loop they will be built through reliable, and by v0.3.0, which
adds no capability and exists to clear the ground they are built on:

- **v0.3.0, the foundation** — Gate 0's inherited backlog cleared. No new
  capability; see the versioning exception under "Versioning decision".
- **v0.4.0, the teachable case** — one case end to end, in clinical units, at
  a speed and on a time base that make its lessons observable at all.
- **v0.5.0, the case you can branch** — bookmarks, forking from them, and
  side-by-side comparison of the branches.

### The timeline

| # | Step | What it is | Size |
| --- | --- | --- | --- |
| 1 | **v0.2.8 — the workflow works** | Scoped below. Its own frozen list of thirty-eight entries: the development machinery the project already runs on, fixed before two long milestones are run through it. No simulator change. | 2 M, 35 S |
| 2 | **v0.3.0 — the foundation** | Gate 0's frozen debt list, recorded under v0.4.0 below: the entries outside that milestone's own scope, released as a minor by deliberate exception. | 4 M, 17 S |
| 3 | **v0.4.0 — the teachable case** | **Shipped 2026-09-05.** Scoped below. 13 items, of which 6 are gate-0 debt the milestone cleared itself. Twelve landed and the thirteenth, `PL-011`'s retention rule, was dropped as superseded; its Required-scope entry records why. | 7 M, 6 S |
| — | **v0.4.x — the code is the model** | Planned-milestone item 29, shipping as a patch in the `v0.4.x` track. A patch, not a milestone. "No behavior changes" held until the 2026-09-03 re-scope and no longer does: the exact step moves the displayed value in its last digit. Moved from ahead of v0.4.0 to behind it (project owner, 2026-09-02): the placement's real constraint is that it precede item 6's substance generalization, and v0.4.0 changes no equation, so gating the teachable case on an unscoped pass over `core/` bought nothing. Scoped and then re-scoped 2026-09-03: the owner's bar is that a reviewer follow `core/` without a lookup table, which naming alone cannot reach, so the operator split is replaced by the exact matrix exponential (`PL-GS5X`). Still a patch, `v0.4.1` — it crosses no capability boundary; see item 29 for why, and for why no exception is recorded. **It freezes no gate and takes no section of its own (project owner, 2026-09-05).** The cadence's four beats run for *milestones*; Gate 1 is frozen when v0.5.0 is scoped, as row 4 records and as three of v0.4.0's own deferrals assume; and no patch in this project has ever had a section — v0.2.1 through v0.3.9 each took a version-table row and a baseline section at ship time and nothing more. That this was ever in question is a tooling artefact worth recording: `bin/docket wave` read this row as a milestone because it was written `v0.4.1` where item 29 already called it the `v0.4.x` row, and the gate it therefore asked to freeze was 105 entries against Gate 0's 21 — five times the largest gate this project has cleared, and 62% of the open queue. The row is now written `v0.4.x`, which is what makes the beat agree with the plan. **Eight items**, `PL-P0BB` having shipped in v0.3.2: `PL-GS5X` and `PL-X9KD` under `numerical-domain`, and `PL-H46J`, `PL-212V`, `PL-3TLK`, `PL-9SH6`, `PL-VZL0`, `PL-FZ6T` under `core-domain-language` — plus `PL-X2XX`, which `PL-VZL0` requires and which neither list named until `PL-GGCN` taught the checker to read the second half of a compound prerequisite. Swapping `PL-P0BB` out for `PL-X2XX` leaves the effort totals unchanged. `PL-3TLK` leads; the rest of the naming work follows the exact step. `PL-011` was carried here at the v0.4.0 cut and is **not** part of this step: it was dropped 2026-09-05, superseded by `PL-T691` and `PL-2FM6`. Those two, with `PL-P1Z3`, `PL-8LXM` and `PL-49R8`, are the score architecture the 2026-09-05 design round filed into `numerical-domain` behind `PL-GS5X`, and they are **v0.5.0's, not this track's** (project owner, 2026-09-05) — row 5 carries the reasoning. **This track promises no particular patch number,** which is what `v0.4.x` means: patches are cut as work accumulates and the exact step takes whichever number it lands on. Saying "ships as v0.4.1" would be a promise the release path cannot keep — `docket release` offers the next free number to whatever is finished, so any patch cut before the exact step lands would take it. | 1 L, 6 M, 2 S |
| 4 | **Gate 1** | Frozen when v0.5.0 is scoped. Contents unknown by construction: v0.4.0's own findings land here. Ships inside v0.5.0, not as its own release. | — |
| 5 | **v0.5.0 — the case you can branch** | Planned-milestone items 8 (replay half), 26 (bookmarks), 12 (forking), 11 (comparison). **The score architecture belongs here (project owner, 2026-09-05):** `PL-T691` (hold keyframes at every control event and answer any window in closed form), `PL-2FM6` (delete `RunHistory` and draw the chart from the closed-form sampler), `PL-P1Z3`, `PL-8LXM` and `PL-49R8`, filed into `numerical-domain` by the 2026-09-05 design round and chained behind `PL-GS5X`. It is placed here rather than in the v0.4.x track for two reasons that point the same way. It is what forking *is*: item 12's required property — a branch reproduces its parent element-wise at every recorded sample — is nearly free once a run is a closed-form function of its control timeline, and expensive against a recorded sample store. And it is `1 P1 L` plus four more against a patch track whose whole content is otherwise `1 L, 6 M, 2 S`, so admitting it there would roughly double a patch and put a `P1 L` inside one. `PL-011` was dropped on its promise, so this is also where that debt is actually paid: until `PL-T691` and `PL-2FM6` land, the run's sample store grows unbounded. | — |
| — | **MVP complete** | A learner can run, branch, and compare a case. | — |
| 6 | **Gate 2** | Frozen when v0.6.0 is scoped; ships inside it. | — |
| 7 | **v0.6.0 — the schematic** | Planned-milestone item 27: Gas Man's Picture, showing where the agent *is* rather than where its tension is. | — |
| 8 | **Gate 3** | Frozen when v0.7.0 is scoped; ships inside it. | — |
| 9 | **v0.7.0 — multi-substance and nitrous oxide** | Planned-milestone items 6 and 7, and the substance generalization Phase 1 describes. | — |
| 10+ | **Beyond** | The machine and its interlocks (items 1-5), save/load and replay (9, 10), then intravenous agents (13-15), in "Development pathway" order. | — |

**Rows 1 and 2 are the only releases whose whole content is a frozen list,
and they are not the same kind of thing.** Row 2 is Gate 0's release: that
gate earns a version of its own because it clears the backlog inherited from
before the debt gate existed, which is the exception recorded under
"Versioning decision" above, and an exception rather than a pattern. Row 1
is not a gate at all — v0.2.8's frozen list is its own scope, recorded under
a gate heading because that subsection is what `bin/docket wave` reads, and
the second of the two groups it lists is new workflow capability rather than
debt.
Gates 1 onward hold one milestone's findings and ship inside the milestone
they gate, which is why rows 4, 6 and 8 carry no version.

Rows 5 to 9 are the intended order and are not yet scoped; each becomes real
only when it gets its own goal, required scope, definition of done and
out-of-scope list here, per the development rules. Row 5's internal ordering —
forking and comparison ahead of save/load and replay — is a deliberate
departure from "Development pathway"'s Phase 3 sequence, on the grounds that
branching within one session is the teaching payload while persistence is a
convenience; it is recorded here as a proposal rather than a decision, and
Phase 3's stated order stands until v0.5.0 is scoped.

### Why the gates are on this list and not behind it

A gate that lives in a separate document, or in a session's memory, is
renegotiated every time it is inconvenient. Put on the timeline it is a step
with a size, and skipping it is visible as skipping a step. The cadence that
generates rows 2, 4, 6 and 8 is specified under "The debt gate" below; the
rule is that scoping a milestone freezes its gate, and the gate clears before
that milestone's implementation begins.

## Completed: v0.1.0 - first patient sevo model

### Goal

Extend the existing circuit model into the smallest useful, testable
volatile-anesthetic patient model:

```text
delivered sevo -> breathing circuit -> alveoli -> blood
               -> vessel-rich group / muscle / fat -> mixed venous return
```

This milestone uses sevoflurane only. It should demonstrate recognizable
wash-in, uptake, tissue distribution, mixed-venous return, and washout while
preserving deterministic behavior and explicit units.

### Required scope

- Keep the v0.0.2 circuit model and its analytic regression tests.
- Add an explicit alveolar gas compartment driven by alveolar ventilation.
- Add sevoflurane blood:gas and tissue:blood partition data with source
  provenance and validation.
- Add cardiac output and perfusion-limited vessel-rich, muscle, and fat tissue
  groups.
- Compute mixed-venous return from tissue outflow and couple it back to the
  lung-blood exchange.
- Allow fresh gas flow, delivered sevo concentration, alveolar ventilation,
  and cardiac output to change during a run without resetting state.
- Expose at least delivered, circuit/inspired, alveolar/end-tidal, and
  mixed-venous or representative tissue concentrations in snapshots and the
  interface.
- Track agent delivered, exhausted, and stored in gas, blood, and tissue
  compartments so mass balance can be checked within a documented numerical
  tolerance.
- Preserve explicit simulation time, deterministic results, and separation of
  the scientific core from Flet.
- Document equations, units, assumptions, parameter sources, numerical method,
  and model limitations in `docs/MODEL.md`.
- Add unit, integration, invariant, and independent reference tests before the
  release is tagged.

### Definition of done

v0.1.0 is complete only when:

- the locked Python 3.14 environment passes Ruff formatting and linting, strict
  mypy, pytest, and GitHub Actions;
- the v0.0.2 circuit reference behavior remains unchanged;
- zero-flow and zero-ventilation limits behave safely;
- concentrations remain finite and nonnegative;
- increasing ventilation or cardiac output produces the expected directional
  effects in documented reference scenarios;
- wash-in and washout are stable across supported step sizes;
- total sevoflurane mass closes within the stated tolerance;
- Start, Pause, Reset, and live parameter changes behave deterministically;
- the user interface states that this is an educational model, not a clinical
  prediction; and
- no deferred feature has entered the release accidentally.

All criteria above were met at tag time; see `docs/MODEL.md`'s "Release
gate" section for the corresponding scientific-documentation checklist.

### Explicitly out of scope for v0.1.0

- Desflurane, isoflurane, nitrous oxide, or simultaneous gases.
- Vaporizer interlocks, agent switching, direct injection, flush, or automated
  end-tidal control.
- Multiple alveolar units, dead space, shunt, or ventilation-perfusion
  mismatch.
- Metabolism, renal or hepatic clearance, ECMO, or cardiopulmonary bypass.
- MAC, BIS/eBIS, nociceptive response, hemodynamic response, or decision
  support.
- IV anesthetics and effect-site models.
- Scenario persistence, replay, comparison, or forking.
- Packaging, signing, or release installers beyond what is needed to run and
  test the milestone.

## Completed: v0.2.0 - isoflurane and desflurane

### Goal

Prove that the v0.1.0 patient model (circuit, alveolar, tissue, and venous
compartments; the governing equations in `docs/MODEL.md`) is agent-generic
rather than sevoflurane-specific, by adding isoflurane and desflurane as
additional validated, data-driven volatile agents with independent
reference cases. No governing equation changes for this milestone; only new
per-agent data and the loading capability to select among agents.

### Required scope

- Add `data/agents/isoflurane.json` and `data/agents/desflurane.json`,
  schema-validated like `data/agents/sevoflurane.json`, with cited
  blood:gas and tissue:gas partition coefficients and source provenance.
- Extend `core/parameters.py`'s agent loading so an agent can be selected
  by id rather than only ever loading sevoflurane
  (`load_sevoflurane_parameters()` is currently the sole, hardcoded path
  `RespiratorySystem.default()` uses). Consider migrating this module's
  JSON validation to Pydantic while touching it: the boilerplate in its
  `_require_*` helpers compounds with each new agent schema, and the
  module is isolated behind plain dataclass returns, so the switch is
  low-risk here.
- Add independent reference tests for isoflurane and desflurane wash-in,
  uptake, and washout, following the same directional-solubility,
  equilibrium, and mass-balance pattern already used for sevoflurane in
  `tests/reference/test_sevo_patient.py`.
- Document both new agents' parameter provenance in `docs/MODEL.md`, and
  note any agent-specific numerical considerations worth recording (e.g.
  desflurane's low blood:gas solubility) even though they don't change the
  governing equations.
- Preserve the v0.0.2 circuit and v0.1.0 sevoflurane reference tests
  unchanged.

### Definition of done

v0.2.0 is complete only when:

- `isoflurane.json` and `desflurane.json` pass the same schema and range
  validation as `sevoflurane.json`;
- each new agent has independent reference tests demonstrating correct
  directional solubility behavior and mass-balance closure within the
  documented tolerance;
- the v0.0.2 circuit and v0.1.0 sevoflurane reference tests remain
  unchanged and passing;
- `docs/MODEL.md` documents both new agents' parameter provenance;
- Ruff formatting and linting, strict mypy, pytest, and GitHub Actions all
  pass.

### Explicitly out of scope for v0.2.0

- A UI control for selecting which agent is running. Agent switching and
  interlock behavior belong to the anesthesia-machine milestone (item 1 in
  "Planned milestones" below); this milestone only needs the model to be
  capable of running as isoflurane or desflurane, not to expose that choice
  in the interface yet. (Recorded as this milestone's scope at tag time. A
  basic picker was in fact added afterwards in commit `00791b1`; it restarts
  the run rather than switching mid-run, so the interlock and
  residual-washout work this excluded is still outstanding.)
- Vaporizer-specific delivery-device physics (e.g. desflurane's heated,
  pressurized vaporizer requirement) — this milestone models uptake and
  distribution only, not the delivery device.
- Halothane, enflurane, ether, or xenon: a further-future stretch beyond
  this milestone. Halothane has reasonable modern published data despite
  being clinically obsolete, but enflurane, ether, and xenon are sparser to
  source and should each get their own provenance check before being
  added, not be assumed available just because the Gas Man reference
  simulator depicts them.
- Nitrous oxide: not a halogenated volatile, so out of scope here; covered
  separately by items 6-7 in "Planned milestones" below.
- Any change to the v0.1.0 governing equations themselves — this milestone
  proves they are agent-generic, not that they change per agent.

All criteria above were met at tag time. `isoflurane.json` and
`desflurane.json` load through the same `load_agent_parameters(agent_id)`
path added for this milestone (`load_sevoflurane_parameters()` is now a
thin wrapper over it, so no existing call site changed behavior);
`tests/reference/test_multi_agent.py` covers directional solubility and
mass-balance closure for both new agents; and `docs/MODEL.md`'s parameter
provenance table and new "v0.2.0: isoflurane and desflurane" subsection
record both agents' sourcing.

## Completed: v0.2.8 - the workflow works

### Goal

Make the development loop reliable before two long milestones are run through
it. Everything in this release is machinery the project already depends on:
the merge path, the release script, the queue's ranking, the session-start
digest, the type-check and lint gates, and the instructions a session reads
before it does anything else. None of it touches the simulator.

It comes first because of `CLAUDE.md`'s standing decision of 2026-08-30 —
workflow work outranks product work until the workflow is settled — and that
decision exists because friction in the loop is paid again in every future
session, while a deferred feature is paid for once. v0.3.0 clears twenty
entries of inherited product debt and v0.4.0 builds the first teachable case
on top of it. Both are long runs through the same loop, and running them
through a merge path that does not wait for CI, a release script that stops
halfway, and a `docket next` that ranks work the current milestone excludes
costs more than fixing those does.

It is a patch by the ordinary rule under "Versioning decision" above: it
crosses no capability boundary, adds nothing to the simulator, and changes no
equation, parameter, numerical method, unit or displayed value. Gate 0's
minor-version exception is not extended to it and is not needed.

### Debt gate: the frozen list

**Frozen 2026-08-30, the day this release was scoped, at seventeen entries.**
More have been admitted since — under the completion rule and the scope test
beneath this list, and one at the project owner's direction — so the entries
below, rather than that original seventeen, are its whole content. What the freeze does and does not close is set
out beneath the list; an entry records its own outcome as it closes, per
"The cadence" below.

**It is a frozen scope, not a fourth gate in the cadence.** The first group
below is debt by "What counts", all classed `defect`, and the second is new
workflow capability, which
that section says explicitly is *not* debt and does not hold a gate. The list
is recorded under a heading named "Debt gate" because that subsection is what
`bin/docket wave` reads: a release records a gate to say that it comes ahead
of one already open, and the beat then follows it rather than contradicting it
(queue item `PL-NSN9`, a self-gating milestone reporting the wrong beat). The
numbered gates are unaffected — Gate 0 is still recorded under v0.4.0 below,
still binds v0.4.0, and becomes the nearest gate again the moment this release
ships.

How many entries are closed is **not recorded here**, for the reason given in
the v0.4.0 section: a count written into a document goes stale the next time an
item closes. `bin/docket wave` reads these entries against `docs/items/` and
reports the split.

Nor is the list's *size* restated in prose here, for the same reason. It is
stated in the group headings below and in the two table rows naming this
release, and `tools/doc_check.py` holds those three to the entries.

*The loop is visibly broken without these — twenty-two entries:*

- PL-J786 (S) Require a green `checks` run before any merge into main
- PL-64LS (S) Detect items stranded on an unmerged branch
- PL-8HJ2 (S) `make release` stops mid-way on the ROADMAP table it does not
  write, so every release ends in a red test
- PL-M5FK (S) This file's tag statements go stale on every release, and no
  check reads them
- PL-1TPM (S) `docket next` ranks work the current milestone excludes, with no
  sign that it does
- PL-019F (S) The "what should we work on next" rule answers one level below
  the roadmap step that should decide it
- PL-5YK8 (S) The `verify:` advisory nags about grandfathered items, so it can
  never reach zero
- PL-H7XN (M) `CLAUDE.md` keeps every rule resident whether or not a session
  needs it, which reduces adherence to the ones it does
- PL-NSN9 (S) A milestone that gates itself reports `implement` when its gate
  clears, where `release` is due
- PL-J295 (S) The release-train check reads a tag missing from a shallow clone
  as a release that was never tagged, so `make check` fails on unmodified
  `main` in every web-session container. Added after the freeze because it
  completes `PL-XCYB`, further down this list: that entry established that a
  check must refuse to answer in a shallow checkout rather than answer
  wrongly, and fixed the pull-request reader; the tag reader has the identical
  exposure and was missed. See the rule beneath this list.
- PL-KWC1 (S) `docket flight` reads item ids from branch names only, so a
  branch the web harness named carries none and is invisible — and `docket
  next` therefore hands out items another session is already implementing.
  Added after the freeze because it completes PL-64LS above: that entry made a
  branch's stranded items visible to a session, reading the same refs through
  the same module, and left the in-flight signal blind on every branch this
  project actually produces.
- PL-1CYR (S) Nothing re-checks the branch against `main` once a session is
  underway, so a discussion that becomes implementation builds on a base that
  moved while it was talking. Added 2026-08-31 at the project owner's
  direction rather than under the completion rule: it is new scope, admitted
  because the staleness is paid by every session that opens as a discussion,
  which is how this project is normally worked. Closed 2026-08-31 (pull request
  125): the check is `bin/docket branch`, so the question can be asked again at
  any moment rather than only at session start, and the hook keeps only the
  fetch.
- PL-D2GW (S) The session digest offers a release whose version names a
  milestone whose gate is still open, so the line every session reads first
  tells it to cut v0.2.8 while entries of v0.2.8 are unfinished. Admitted
  2026-08-31 under the scope test: the digest and the release script are both
  machinery this release's goal names. It reopens on every later release that
  records a gate — v0.3.0 shipping Gate 0 is the next — which is exactly the
  run this release exists to protect.
- PL-Q2BJ (S) The digest's `Top:` line still leads with work the current step
  excludes, contradicting the beat printed two lines below it. Admitted
  2026-08-31 under the scope test: it is `PL-1TPM`'s defect on the surface
  every session reads whether it asked or not.
- PL-CPSY (S) A squash-merged branch whose ref survives reports its items in
  flight forever, so `docket next` withholds work that is finished and
  startable. Admitted 2026-08-31 under the scope test: squash-merge is the
  merge path `PL-S4M2` installed for this release, and the queue's ranking is
  what reads it. Closed 2026-08-31 (pull request 121): a branch is finished
  when its content has landed, which is asked before the commit walk rather
  than inside it.
- PL-S1P1 (S) The refs whose history could not be read are dropped before the
  in-flight ids reach `docket next`, so a partial answer is presented as a
  complete one everywhere except `docket flight`. Admitted 2026-08-31 under
  the scope test. `PL-CPSY` and `PL-MGNC`, the other two holes in that
  function, both closed on 2026-08-31 ahead of it - one answered before the
  commit walk and one inside it, neither needing this one's lines. What they
  left is a larger `unreadable` half for this item to carry to the callers,
  and `PL-YSXF` (an unread ref loses the id its own branch name carries) is
  the same hole from inside the function: one pass. Closed 2026-08-31 (pull
  request 123): `in_flight_ids` is gone and every caller takes the
  `FlightReport` itself, so the gap travels with the answer rather than being
  dropped at the boundary, and one sentence appears under all six.
- PL-YSXF (S) A ref named as unread loses the item id its own branch name
  carries, which needs no history to read, so `docket next` offers an item a
  live session is holding. Admitted 2026-08-31 under the scope test, at the
  project owner's direction once `PL-S1P1` had closed: it is the fourth and
  last hole in the function the three entries above are about, and the only
  one where the checkout knew the answer for certain and threw it away. The
  guards `PL-MGNC` added are what widened it, so it grew rather than staying
  where `PL-KWC1` left it.
- PL-MGNC (S) A readable merge-base does not make the in-flight commit walk
  complete, so a shallow clone — the normal state of a session container —
  reports merged items as in flight. Admitted 2026-08-31 under the scope test,
  and the only member of this family observed firing: the digest that opened
  the session reassessing this gate named twenty-seven ids, eighteen of them
  closed and one of them `PL-NSN9`, an open entry of this list. Closed
  2026-08-31 (pull request 122): the walk now has to stop against a commit the
  default branch accounted for rather than because the checkout ran out of
  history, and the reproduction the brief asked for builds the intermediate
  depth with real git.
- PL-3CBS (S) Nothing notices that an open item's work already landed on
  `main`, so `docket next` offers work that is finished and the gate's own open
  count overstates what is left. Admitted 2026-08-31 under the scope test: it
  corrupts the two numbers this release is steered by, in the direction nobody
  double-checks. It was not among the nine captures reassessed that day and was
  admitted on the same reading immediately afterwards.
- PL-3576 (S) `docket check`'s offered-item advisory is computed from an
  in-flight answer that may be partial and says nothing about it, so a shallow
  checkout is told to groom an item that is not the one about to be offered.
  Admitted 2026-09-01 under the scope test: `PL-S1P1` above carried the unread
  refs to six readers of that answer and left `check` out as a placement
  question rather than as out of scope, so this is the seventh and last of them.
- PL-1Q3S (S) A merged pull request leaves a stale remote-tracking ref, so the
  stop hook counts every commit landed since as unpushed and tells the session
  to push a branch identical to `main`. Admitted 2026-09-01 under the scope
  test: the hook is outside the repository, but the deliverable is a line in the
  instructions a session reads — one of the six pieces of machinery the goal
  names — and it fires after every merged pull request, several times a session.
  The "workable here" limit below excludes a finding *nothing in the tree can
  close*; this one closes with a repository edit and is marked `not-delegable`
  only because confirming it means ending a session.
- PL-HDY6 (S) The scope reader counts any id a milestone's section names, so
  `docket next` reports an id the section names *to exclude* as in scope for
  the current step. Admitted 2026-09-01 under the scope test, after the four
  above and on the same reading: it is the queue's ranking misdirecting a
  session on `main` today, telling it that `PL-68XK` clears this gate on the
  strength of the paragraph below that says `PL-68XK` does not. The fix is not
  simply to prefer this subsection - v0.4.0 names nine open ids as its own
  Required scope rather than as gate entries, and those are in scope - so the
  item carries both candidate rules and what each costs.

*Stops new debt being introduced — sixteen entries:*

- PL-ZQ9C (M) Record an item's pull request, so provenance survives
  squash-merge
- PL-S4M2 (S) Switch main to squash-merge, so each item lands as one commit.
  Blocked by PL-ZQ9C above and ordered after it deliberately: squash-merge
  discards the branch history that today is the only record of which pull
  request closed an item, so the provenance has to be recorded before it is
  discarded, not after.
- PL-F5HB (S) The project runs a Python 3.14 release candidate, not 3.14 final
- PL-020 (S) Widen the type-check gate past `src`, and ship a `py.typed`
  marker
- PL-W5LG (S) Hold CI config to the same path checks as the documentation
- PL-ZN0N (S) Enable ruff RUF100 so inert `noqa` directives fail the build
- PL-69J3 (S) Clear the inert `noqa` directives RUF100 will catch, and record
  why the deliberate suppressions exist
- PL-STNV (S) Retire the review-verification harness and capture its last live
  finding
- PL-XCYB (S) A provenance check must refuse to answer in a shallow checkout,
  not answer wrongly. Added after the freeze because it completes PL-ZQ9C
  above: that item's check asserts a `(#N)` subject on a commit reachable from
  main, and a web session's checkout is shallow, so the check as specified
  reports sound provenance as broken. See the rule beneath this list.
- PL-WFJ9 (S) `render.py` reads `Readiness` and `Feature` through `object`
  annotations and twelve `type: ignore[attr-defined]`, so the widened gate
  passes over the digest and `status` outputs without checking them. Added
  after the freeze because it completes PL-020 above: that entry's whole claim
  is that `subprojects/docket/src` is type-checked, and it was not, in the two
  outputs every session reads first. See the rule beneath this list.
- PL-DL1X (S) `docket release` stamps every item file before it bumps the
  version, so a failed bump leaves the store recording a release that did not
  happen. Admitted 2026-08-31 under the scope test: the release script is
  machinery this release's goal names, and the residue is a provenance error
  of the kind the release path exists to prevent.
- PL-921W (S) The formatter target applies to `tools/`, which must run under
  bare `python3`, and nothing guards it the way `subprojects/docket/` is
  guarded. Admitted 2026-08-31 under the scope test: the lint gate is named in
  the goal, and this is the same second-site miss as `PL-J295`, one tool over.
- PL-QDH7 (S) `tools/` promises standard-library-only imports and nothing
  guards it, the way the parse floor now is. Admitted 2026-09-01 under the
  scope test: the lint gate is named in the goal, and this is the other half
  of `PL-921W`'s promise, left unguarded where that item guarded the first.
- PL-CMCB (S) All ten `type: ignore` directives sit under `tests/`, outside
  `[tool.mypy] files`, so `warn_unused_ignores` has never evaluated one.
  Admitted 2026-08-31 under the scope test: it is the mypy half of what
  `PL-ZN0N` and `PL-69J3` did for `noqa`. The weakest of the seven — inert
  reporting rather than a loop that misfires — and the first to drop if this
  list needs shortening.
- PL-RWZV (S) The brief check tests for a literal marker, so an elaborated
  heading fails and an empty section passes. Admitted 2026-09-01 under the
  scope test: it is a `docket check` misfire, the same machinery as `PL-5YK8`
  above, and it is the gate deciding whether an item may reach `ready` at all.
  Two of the captures triaged on 2026-09-01 carried exactly the empty-section
  stub it accepts.
- PL-H8MQ (S) `ROADMAP.md` states this release's entry count in six places, and
  its group and debt splits in three more, with nothing holding any of them to
  the list. Admitted 2026-09-01 under the scope test: measured that day, three
  different totals — eighteen, thirty-one and thirty-two — were live in this
  file at once, so a session reading it to learn how much of the release is left
  read a number that was wrong. Every admission pays the correction by hand,
  the four of 2026-09-01 included.

**Two items on the approved list are not entries.** `PL-J3ZK` (restore the tag
provenance) and `PL-20ZR` (the workflow-before-features ordering is
re-explained every session) were on the list the project owner approved and
closed before it was written here. Recording a closed item as a frozen entry
would make this release report a size it never had to clear.

**Seven entries are marked `not-delegable`,** which is high for a
release this size and is worth knowing before the work is planned: PL-J786 and
PL-S4M2 change GitHub repository configuration that no session in this project
can reach; PL-8HJ2 can only be proved by cutting a release; PL-ZQ9C leaves a
migration choice open that rewrites the provenance of every closed item;
PL-1Q3S fixes a repository-side habit whose effect is only visible when a
session ends, in a hook no session can read; and
PL-H7XN's test is that no rule was lost, which is a reading of the file rather
than a command; and PL-CMCB's deliverable is a verdict on ten suppressions
rather than an exit code.

**What the freeze closes, and what it does not** (project owner, 2026-08-30).
The list is closed to new *scope*: new behavior, new capability, another
workflow idea raised while this release runs. It is not closed to what an entry
already on it needs in order to actually be done. A finding made after the
freeze that addresses something a frozen entry is fixing belongs here, recorded
with what it completes. Freezing exists to fix a specific set of problems, so
shipping an entry known to be half-fixed would keep the list's length at the
cost of its purpose.

This is "The gate is a snapshot, not a moving target" read correctly rather
than a new rule: that section already says a finding which continues or
completes an item inside the frozen list belongs to the same list. This
paragraph said the opposite when the section was first written, and was wrong.

**The list is a scope, not a set of items** (project owner, 2026-08-31). That
is what decides membership, and the completion rule above is one case of it
rather than the test itself. This release's scope is the goal stated at the
top of this section: a development loop reliable enough to run two long
milestones through, across the machinery the goal names — the merge path, the
release script, the queue's ranking, the session-start digest, the type-check
and lint gates, and the instructions a session reads before it does anything.
A finding that a *named* piece of that machinery misfires is inside this scope
however late it is found and whatever entry it does or does not complete,
because leaving it out ships a release titled "the workflow works" while the
workflow it names does not.

So "new scope" means a different goal — a new workflow capability, a better
tool nobody is blocked by, an idea raised because this release made someone
think of it. It does not mean a newly discovered instance of the goal already
frozen. A defect in already-named machinery is the third case, and it is
admitted: this paragraph previously offered only "new scope" and "completes an
entry", and nine findings triaged on 2026-08-31 were sent to the queue for
being neither, when seven of them were defects in the digest, the release
script, the merge path and the lint gate that this release exists to make
reliable.

Two limits keep that from reopening the list for everything. The finding must
be a **defect** in machinery this section's goal names — not an improvement to
it, and not machinery the goal is silent about; and it must be **workable
here**, so a finding whose cause is outside this repository is captured and
left out however well it fits, because an entry nothing in the tree can close
would hold the gate open forever.

A `safety`- or `science`-classed finding goes to Gate 0 rather than here — it
is about the simulator, which this release does not touch. A `P0` is a hotfix
on its own branch under the `docket` skill and joins no list.

**Four entries were added under the completion rule — PL-J295, PL-KWC1,
PL-XCYB and PL-WFJ9, all above.** The rest were added under the scope test
rather than this one, each marked as such in the list with the date and the
reasoning; that test is beneath it. PL-XCYB is paired with PL-ZQ9C rather than queued behind it. It was found while handing
PL-ZQ9C to a session, by checking whether that item's proposed migration was
feasible, and it makes the difference between a provenance check that is right
and one that fails loudly against correct data in the environment most sessions
run in. Shipping PL-ZQ9C without it would close an entry known to be
half-fixed, which is the outcome the rule above exists to prevent, so the two
are worked together and closed together.

PL-WFJ9 is the same case a step later, and was found by the entry it completes
rather than before it: widening the type-check gate to `subprojects/docket/src`
made `render.py`'s suppressions visible for the first time, and they are why
the widened gate passes over that file. PL-020 could be reported closed without
it, which is exactly the half-fixed close the rule prevents - the gate would
assert that docket's source is checked while the digest and `status` renderers,
the first thing a session reads and the answer to "what next", were not. It is
worked with PL-020 rather than behind it.

PL-68XK (check that a recorded commit hash resolves) is a different case and is
*not* admitted by this rule: it predates the freeze and was excluded from the
approved list deliberately. It was nonetheless entangled with PL-ZQ9C, so its
brief has been refreshed rather than worked - and what the refresh had to say
changed once PL-ZQ9C landed, and then closed entirely. `pr:` sat beside
`commit:` and made it optional, narrowing PL-68XK from "validate the field that
makes a closure traceable" to the smaller job of holding a present `commit` to
one that resolves. PL-T63T then answered the question one step upstream - what
the field should record at all - and the project owner chose to retire it, since
21 of the 42 hashes that could be checked resolved nowhere. PL-68XK was dropped
with it: there is no longer a field for it to validate. The shallow-checkout
discipline PL-XCYB built is unaffected and still serves the `pr:` check.

### Definition of done

- Every entry on the frozen list above is `done`, or `dropped` with its reason
  recorded. `bin/docket wave` reports the split against `docs/items/`.
- `make check` passes: `ruff format`, `ruff check`, `mypy`, `pytest`,
  `docket check`, and `tools/doc_check.py`.
- The two entries that change repository configuration rather than the tree —
  PL-J786 (a green `checks` run required before merge) and PL-S4M2
  (squash-merge) — are confirmed in effect on a real pull request, not merely
  described as done. Neither can be verified by a command in this repository,
  which is why both are marked `not-delegable`.
- No equation, parameter, numerical method, unit or displayed value has
  changed, and the v0.0.2 circuit and v0.1.0 sevoflurane reference tests pass
  unaltered. Three entries reach into `src/` and `tests/` and are bounded to
  what their briefs describe: PL-020 may add type annotations, PL-ZN0N and
  PL-69J3 may add, remove or annotate `noqa` directives. If any of them turns
  out to require a change to a modelled value, that is a finding for Gate 0
  and a scoped item of its own, not this release's work.

### Explicitly out of scope for v0.2.8

- Anything on Gate 0's frozen list, recorded under v0.4.0 below. That gate is
  untouched by this release and clearing it is still what v0.3.0 ships.
- Any simulator change at all: `src/anesthesia_sim/core/`,
  `src/anesthesia_sim/app/`, and the scientific content of `docs/MODEL.md`. A
  release whose whole claim is that the loop is now reliable cannot also be
  the one that moves the model.
- Workflow capability beyond the entries on that list — new tools, better
  tools, an idea this release made someone think of. The queue holds more
  process items than this release ships, and they wait for the next one. What
  the scope test admits is a defect in machinery the goal already names, which
  is not this; a release that absorbs every workflow idea raised while it runs
  never ships.

## Completed: v0.3.0 - the foundation

### Goal

Clear the inherited backlog, so feature work starts from a codebase whose
known defects are closed rather than carried. This release adds no
capability: after it the simulator does what it did before, correctly, with
its verification gate widened to the inputs the interface can actually reach
and its failure path unable to leave partial state behind.

Its contents are exactly Gate 0's items that fall outside the teachable
case's own scope — those listed under "Debt gate: the frozen list" in
the v0.4.0 section below. It has no scope of its own to specify, which is why
this section is short: the frozen list *is* the specification, and nothing
may be added to it (see "The gate is a snapshot, not a moving target").

It is a minor rather than a patch by deliberate exception, recorded under
"Versioning decision" above. That exception covers Gate 0 alone.

### Definition of done

- Every item on Gate 0's frozen list that is outside the v0.4.0 milestone's
  Required scope is `done`, or `dropped` with its reason recorded.
- `make check` passes: `ruff format`, `ruff check`, `mypy`, `pytest`,
  `docket check`, and `tools/doc_check.py`.
- No equation, parameter, or numerical method has changed, and the v0.0.2
  circuit and v0.1.0 sevoflurane reference tests still pass unaltered. The
  two safety items on the list tighten a verification bound and make the step
  transactional; neither is licensed to change a modelled value, and if
  either turns out to require one, that is a finding for the next gate and a
  scoped item of its own, not this release's work.

### Explicitly out of scope for v0.3.0

- Anything in the v0.4.0 milestone's Required scope, including the six gate-0
  items that milestone clears itself.
- Any item captured after Gate 0 was frozen whose problem did not already
  exist at the freeze. A finding that *was* present re-enters by the
  presumption in "The gate is a snapshot, not a moving target", as does
  anything at `P0` or classed `safety`/`science` regardless of presence. This
  bullet previously named only the `P0`/`safety`/`science` half, which made it
  narrower than "The gate is a snapshot" and than step 4 of "The cadence";
  those two agreed with each other and this one did not (queue item PL-9PMV).
- New capability of any kind. A release whose whole claim is "the ground is
  now solid" cannot also be the one that moves the ground.

## Completed: v0.4.0 - the teachable case

### Goal

Make the model teachable. The science is sound and its lessons were
unreachable when this milestone was scoped, for three measurable reasons.
They are stated below as they stood on 2026-08-25 and are not amended as the
milestone closes them: a Goal records the problem a release was taken on to
solve, and rewriting it into the past one clause at a time would leave the
section describing neither the problem nor the product. All three are answered
by the Required scope below, which is where this milestone's outcomes are
recorded.

- the run advances at 1x real time (`app/simulation_view.py`, one 0.1 s step
  per 0.1 s sleep), while the compartments that make uptake and distribution
  worth teaching have time constants of 135 min (muscle) and 42 h (fat) for
  sevoflurane at reference settings - so the reservoirs that cause
  context-sensitive emergence cannot be observed at all;
- the chart shows a rolling five-minute window on an axis labelled in
  seconds and scaled to the vaporizer's dial maximum, so a 1 MAC run occupies
  the bottom quarter of the plot and everything slower than the vessel-rich
  group scrolls away flat; and
- every value is a percentage of an atmosphere, so three agents whose MACs
  differ threefold are displayed as though their numbers were comparable.

The end state: a learner runs one case from induction to emergence - in
compressed time they can sit through, in the unit clinicians reason in, on a
time base that spans a case - changes something, sees on the record when they
changed it, turns the vaporizer off, and watches it come down against a
labelled reference.

This milestone changes no equation, parameter, or numerical method. It is a
minor rather than a patch because it adds a displayed clinical unit, a new
time base, and a run-rate control: capability boundaries in what the
interface asserts, even though the model behind them is untouched.

It promotes planned-milestone item 25 (playback multiplier) in full and the
recording half of item 8 (control-input timeline). It does not promote item
26 (bookmarks) or item 12 (forking), but it is designed so that neither is
blocked - see "Designed for forking" below.

### Debt gate: the frozen list

**Frozen 2026-08-25, the day this milestone was scoped.** Twenty open items
are debt by "The debt gate" below — classed `defect`, `safety`, `science`,
`refactor` or `perf`, or at `needs-decision`. Six of them are inside this
milestone's own Required scope and are cleared by it, per "Debt inside the
milestone's own scope". The other fourteen clear before implementation begins.
The list itself stays frozen; an entry records its own outcome as it closes,
per "The cadence" below.

**Cleared before v0.4.0 begins — 21 entries, 22 item ids** (14 and 15 at the
freeze; seven were added later, per the three notes beneath this list). These
are exactly what v0.3.0, the foundation release, ships.

Count entries, not ids: the PL-Z4GF/PL-SWFM entry below holds two ids for one
problem, so both numbers above are true and only the first is the gate's size.

How many of them are closed is **not recorded here**, because a count written
into a document is a count that goes stale the next time an item closes — this
paragraph said "5 done and 9 remaining as of 2026-08-26" while one of the nine
it named had already been closed. `bin/docket wave` reads the entries below
against `docs/items/` and reports the split, so the answer is computed from the
same files that would be used to check it.

*Core correctness — all safety- or science-classed, all wanting the
strongest model:*

- PL-026 (M) Make the simulation step transactional so a halt leaves no
  partial state
- PL-042 (S) Bound the splitting error across the settings envelope, not one
  point
- PL-VP7N (M) Refuse a simulation step outside the operator split's
  applicability domain. Added after the freeze; see below.
- PL-SLHS (S) Bound the splitting error across setting changes, not one held
  operating point. Added after the freeze; see below.
- PL-9Y42 (S) Validate wash-in against a published human measurement. Added
  after the freeze; see below.
- PL-0MLQ (M) Refuse a setting outside the documented supported input range.
  Added after the freeze; see below.

*Presentation safety — `safety`-classed, and the one entry whose defect is not
in `core/`:*

- PL-NV9W (S) Label the alveolar readout end-tidal-equivalent, as
  `docs/MODEL.md` requires. Added after the freeze; see below.

*Core boundaries — the whole `core-boundaries` feature, all `refactor`:*

- PL-006 (M) Clarify what `RespiratorySystem` actually owns
- PL-004 (S) Decide the fate of the two uncalled descriptive time constants
- PL-007 (S) Make the payload/public-dataclass pattern self-evident in
  `core/parameters.py`
- PL-019 (S) Remove `BreathingCircuit`'s agent-unaware delivered-concentration
  default

*Live process machinery that does not reliably work — `defect` by the rule
under "What counts":*

- PL-G049 (S) A `verify:` command that has never been run is not a
  specification
- PL-674D (S) `docket release` bumps `pyproject.toml` but leaves `uv.lock`
  stale, breaking `make check`
- PL-0RFH (S) `docs/worker.md` buries the carve-out that lets a worker decide
  anything at all
- PL-R0SR (S) `docs/worker.md` should say that corrections arrive by pulling
  the branch, never in chat
- PL-4F6P (S) A `**Worked.**` note said "nothing the brief did not specify"
  for a test that reached into a private class
- PL-N2N1 (S) — **done** (commit `ebefcc2`). `docket release` does not update
  this file's version table or baseline heading. Added after the freeze; see
  below.
- PL-K79K (S) — **done** (commit `54bdb5b`). The session-start digest told
  every session to run `bin/docket triage`, which did not exist. Added after
  the freeze; see below.

**Two entries added 2026-08-30 under the presence rule, both cleared in the
same batch that added them.** Per "The gate is a snapshot, not a moving
target", a finding re-enters this gate when the problem it describes was
already present at the freeze, whatever id it is filed under or however long
after the freeze it was noticed.

The first continues the PL-Z4GF/PL-SWFM entry's scope: the same document
drifting for the same reason, this time its mechanism half rather than one
more instance of it. That entry is the case the presence rule was written for.

The second advertised a command that does not exist, and had done so since
`6f1b5b1` on 2026-08-24 — the day before this list was frozen. Present at the
freeze by date, and `defect` by "What counts" above: a live mechanism `main`
depends on that does not work.

Neither extends what the gate has left to run: both are closed.

**Four entries added 2026-08-30 from an outside review of the repository,
which recorded nothing of its own.** All four re-enter this gate rather than
deferring to Gate 1, on both of the grounds "The gate is a snapshot, not a
moving target" allows, and they are the only findings of that review that do:

- *By the presence rule.* Each describes a problem present in the tree before
  2026-08-25. `core/` has never had an upper bound on the simulation step; the
  splitting-error gate has held one operating point constant since it was
  written; nothing in the repository has ever been compared to a published
  human measurement; and the unhedged `"Alveolar / end-tidal"` label has been
  in the interface since `74bec83` on 2026-08-23, two days before the freeze.
- *By the safety/science exception.* PL-VP7N is `safety`, PL-SLHS is
  `safety`/`science`, PL-9Y42 is `science`, PL-NV9W is `safety` — the classes
  this milestone's out-of-scope list names as re-entering regardless of when
  they were captured.

PL-NV9W was added three entries later than the others, and the delay is worth
recording because it shows where the rule is easy to miss. The review proposed
it at `P2`, which would have left it outside the exception; `docket check`
refuses to seat a `safety`-classed item below `P1`, so triaging it honestly
raised it — and *that* is what brought it inside this rule. The consequence was
followed through once the project owner confirmed the priority. A finding's
gate membership can therefore change as a side effect of classing it correctly,
which is a thing to check at triage rather than only at capture.

Unlike the two entries above, these four do extend what the gate has left to
run, by four items. That is the rule working as intended rather than a gate
being widened: each is a statement `docs/MODEL.md` already makes that the
implementation does not keep, and v0.3.0's whole claim is that the ground is
solid. Shipping that release with a `must fail` that does not fail, a release
bound a shipped trajectory exceeds, and no validation against a human
measurement would make the claim untrue on the day it was made.

The ten other findings from the same review are in the queue and clear at
Gate 1: they are either post-freeze in substance, or classed outside the
exception.

**One entry admitted 2026-09-02, having been missed rather than deferred.**
PL-0MLQ (refuse a setting outside the documented supported input range) is
`safety`-classed at `P1` and qualifies on both of the same grounds as the four
above: the four compartment setters have never enforced `docs/MODEL.md`
§ "Supported input ranges", so the problem was in the tree at the freeze, and
the `safety` class re-enters it regardless of presence. It was captured
2026-08-30, the same day those four were admitted by exactly this rule, and was
named nowhere in this file — not here, not in v0.3.0's out-of-scope list, and
not among the ten findings deferred to Gate 1.

Its omission was an oversight, not a judgement, and recording that matters
because the alternative reading is available: a later reader finding a
`safety`-classed continuation of a frozen entry absent from the list could take
the absence for a deliberate deferral. It was not one, and the exception is in
any case written as not deferrable.

The pairing rule under "The cadence" — an entry is worked with the entry it
completes, not after it — cannot be satisfied here, because PL-VP7N, the entry
PL-0MLQ continues, shipped in v0.2.7. It therefore stands as its own entry.

The failure was invisible to the tool as well as to the reader: `bin/docket
wave` computes the gate's split by reading the entries recorded here against
`docs/items/`, so an entry that was never written down cannot be counted, and
the gate reported one entry short of its real size for three days. That is the
failure mode "a gate nobody wrote down is a gate that gets renegotiated"
describes, arriving through omission rather than through argument. PL-Y4Q4
carries the diagnosis.

Like the four above, this extends what the gate has left to run, by one `M`
item — the step-2 size in "The timeline" moves from `3 M, 17 S` to `4 M, 17 S`
to match.

**One presence-qualifying finding deliberately deferred to Gate 1, and later
split.** PL-WB0X (split `simulation_view.py`) describes a module that has been
oversized since long before the freeze, so the presumption admits it. It was
deferred anyway, which "The gate is a snapshot" permits provided the reason is
stated: it is an `M` restructure of the interface layer with no connection to
anything on the frozen list, and v0.3.0's claim is that it adds no capability
and clears only inherited debt. Pulling in unrelated pre-existing debt because
it is old is the refilling-queue problem the gate replaced Phase 0 to solve.

**That deferral stands and is not reopened here: none of this item shipped in
v0.3.0.** What was settled on 2026-09-02 (project owner) is where the rest of
it goes. Its brief stated three placements that could not all hold — stage 1
before PL-DHV7, which ships in v0.4.0; the whole item at Gate 1, which ships
inside v0.5.0; and "a `v0.3.x` patch step" — which is the contradiction PL-4C41
was filed against. The resolution is to split the item rather than to pick one
of the three, because one item cannot sit in two milestones: stages 1 and 2,
the two pure-module extractions, are named in v0.4.0's Required scope above,
where they gate that milestone's MAC unit and its chart work; stage 3, the
`SimulationView` decomposition proper, is now queue item PL-B9PY and stays at
Gate 1, where only v0.5.0's two-runs-at-once comparison requires it.

*Documentation, performance, and the one decision that is the project
owner's:*

- PL-Z4GF **and PL-SWFM** (S) — **both done** (commits `d40ff83`, `6e19632`).
  One entry holding two ids: PL-Z4GF closed the README half of its original
  scope, and the remainder — this file's own duplicated v0.2.3 table row and
  stale "Current baseline" heading — surfaced later under the separate id
  PL-SWFM. Per "The gate is a snapshot, not a moving target" and its presence
  rule below (project owner, 2026-08-25), that problem was already inside
  this frozen scope, so it cleared here rather than at the next gate,
  regardless of which id or session it surfaced under.
- PL-010 (S) Stop rebuilding render objects on every frame
- PL-Y2GG (S) — **done.** Apache-2.0, chosen by the project owner (commit
  `d40ff83`).

**Cleared by v0.4.0 itself (6 items).** Each appears in Required scope above:
PL-DHV7 (MAC as a displayed unit), PL-VM40 (simulated time from a step count),
PL-F52R (the MAC-awake reference band), PL-ZRSP (the F_A/F_I trace), PL-R3KB
(agent selection discarding a run), PL-011 (bounding the concentration
history) — the last of these cleared by being `dropped` on 2026-09-05 with its
reason recorded, which "What counts" admits as clearing and which the Required
scope above sets out in full. Six of six.

Findings made while clearing this gate go to Gate 1, except `P0` and
`safety`/`science` findings, which re-enter here.

### Required scope

- **Simulated time becomes an exact function of step count** (queue item
  PL-VM40). `SimulationState.elapsed_s` accumulates `+= simulation_step_s`
  per step today; derive it from an integer step counter instead, and fix the
  step at 0.1 s. The run loop advances a fixed number of steps per tick and
  never catches up to the wall clock: a slow machine runs slower, it does not
  run differently.

  *Landed 2026-09-04.* `SimulationState` holds the step count and the step it
  is taking, and reports `elapsed_s` as their product. "Fix the step at 0.1 s"
  ended up fixed *per run* rather than hard-coded: a step differing from the
  one a run has already taken is refused rather than counted, and reset frees
  it. The interface's own cadence is still 0.1 s, and a step-refinement study
  can still take a whole run at a smaller one. `docs/MODEL.md` states the
  guarantee, and the four things it does not cover, under "The reproducibility
  guarantee".
- **A playback multiplier** (queue item PL-SN2C), implemented as steps per
  tick and never as a larger step, with the current rate visible beside the
  clock at all times.
- **The interface layer's two pure-module extractions** (queue item PL-WB0X,
  stages 1 and 2 only): the displayed-precision formatters into a Flet-free
  module of their own, and the chart-series shaping into a module beside
  `app/chart_downsampling.py`. Both are behavior-unchanged and held to the
  existing view tests; PL-WB0X's brief names the modules. Stage 1 lands before
  the MAC unit below: that item rewrites every formatter and extends
  `docs/MODEL.md`'s "Displayed precision" derivation, which today terminates in
  a private static method on a Flet view class, so the one function the
  specification reasons about cannot be read, cited or tested without loading
  the whole interface. Stage 2 lands before the chart work, which four items of
  this milestone touch in the same place. Stage 3, the `SimulationView`
  decomposition proper, is **not** in scope: it is queue item PL-B9PY and stays
  at Gate 1, because only v0.5.0's side-by-side comparison of two branches
  needs it (project owner, 2026-09-02).
- **MAC multiples as a display unit** across every readout and both chart
  axes, alongside percent, with the agent's `mac_percent` provenance
  traceable from the display (queue item PL-DHV7).
- **A case-length time base**: minutes rather than seconds, a selectable
  scale plus a fit-the-run scale (queue item PL-SSBP). Scoped as "15, 30 and
  60 minute scales" and settled wider (project owner, 2026-09-04): 15 minutes
  to 12 hours, geometrically spaced, because the three-scale list was written
  while anything past an hour cost more per frame than the budget allowed and
  `PL-D9WD`'s bucket cache lifted that. The gridline interval derives from
  the selected scale rather than being fixed, and the axis is labelled in
  units it carries itself - `3m`, `1h30m`, `12h` - because a bare number
  means minutes on one scale and hours on another and looks the same on
  both. "Fit run" is the default and always contains the run: past the
  widest listed scale the ladder doubles rather than showing part of a case
  under a name that claims the whole of it.
- **A vertical scale denominated in MAC** (queue item PL-CC23) rather than in
  the vaporizer's dial maximum, which is what makes a cross-agent comparison
  honest. Scoped as "fits the run" and decided otherwise (project owner,
  2026-09-04): a fitted axis rescales a rising curve mid-lesson, and the item's
  own requirement that the rule be stable within a run rules it out. The axis
  is fixed at 0 to 3 x MAC for every agent - three being exactly desflurane's
  dial maximum in MAC - with a trace above the ceiling named rather than left
  to draw as a plateau. `docs/MODEL.md` s "The chart's vertical range is
  denominated in MAC, and fixed" carries the reasoning.
- **A recorded control-input timeline** (queue item PL-DR1Z): every fresh gas
  flow, vaporizer
  dial, alveolar ventilation and cardiac-output change stamped with the
  simulated time it took effect, held with the state it describes, and
  marked on the chart. The recording half of planned-milestone item 8, not
  the replay half. Recorded as `(simulated_time, control, value)` entries
  rather than a fixed struct of named controls: nitrous oxide (planned item
  6) adds a control this milestone cannot enumerate in advance, and a struct
  would need a field added — and every past sample migrated or left with a
  meaningless default — when it lands. A tuple form costs nothing today and
  needs no such migration later.

  *Landed 2026-09-04 as a frozen `ControlChange` record rather than a literal
  tuple, preserving the property this paragraph asks for.* The migration
  argument is about a struct with **one field per control**; a record with one
  `control` field holding a stable identifier has the same immunity — nitrous
  oxide adds an identifier and migrates nothing — while carrying what the
  entry actually needs, which is more than three values: the item's own brief
  requires the old value as well as the new, and the implementation adds the
  history index the mark is placed from, the unit both values are in, and the
  adjustment a drag's several settings belong to. A bare 3-tuple could not
  hold those and would have had to grow into an unnamed 7-tuple. See
  `docs/MODEL.md` § "The control-input timeline".
- **`SimulationHistorySample` keyed by substance, not by six flat named
  compartment floats** (queue item PL-W3DD). There is exactly one substance
  today, so this changes representation, not behavior. It matters because item 12
  (forking, promoted below to "Designed for forking") writes its
  element-wise reproducibility proof directly against this record's shape:
  reshaping it *after* that proof exists means reworking an
  already-validated safety property instead of a plain refactor. Nitrous
  oxide (planned item 6) needs a second substance in the same record, and
  the MAC readout becomes a fold over it rather than a rewrite.

  *Landed 2026-09-05, reaching the store and the chart's binding as well as
  the record.* The bullet names the record, but a row keyed by substance
  above a store keyed by compartment alone would have had to refuse or pool
  a second substance, which is the half-migration it exists to avoid. So
  `RunHistory` is keyed by `RecordedSeries` — substance and quantity — with
  its substances fixed when it is built and a sample of any other set
  refused; the wash-in stretches are per substance for the same reason the
  quotient is; and a chart trace is bound to a `RecordedSeries` rather than
  to a bare quantity, paired with the agent the drawing frame's own snapshot
  names. Nothing displayed changed. See `docs/MODEL.md` § "Interface
  boundary".
- **Changing agent becomes an explicit new case** rather than a selector
  that silently discards the run and its history (queue item PL-R3KB).
- **A MAC-awake reference band** on the chart (queue item PL-F52R): a cited
  population median for return of responsiveness, drawn as a band and
  labelled as a population reference, never as a per-patient time
  prediction.
- **An F_A/F_I trace** (queue item PL-ZRSP), the ratio the uptake literature
  plots, with the interpretive caveat that it means what the textbook curve
  means only while inspired concentration is held constant.
- **A bounded concentration history** (queue item PL-011), which stops being
  optional once a four-hour run at 10 Hz records 144,000 samples.

  *Not landed, and not deferred either: dropped 2026-09-05, the day of the
  cut.* This is the one Required-scope entry the milestone shipped without, and
  it is recorded here rather than removed, because a scope list whose unmet
  entry is simply deleted cannot be audited afterwards.

  It went out of the release at `needs-decision`, carried nominally to v0.4.1,
  and closed the same day. The design round that followed the cut settled it in
  the one direction nobody had costed: the score architecture **removes** this
  store rather than bounding it. Once state is a closed-form function of the
  run's control-input timeline (`PL-T691`), the controller holds a score plus
  one keyframe per control event - about 140 KiB for a 30-day ICU case, against
  the 3.16 GB this entry existed to bound - and `PL-2FM6` deletes `RunHistory`
  outright. Deciding an eviction rule for a store that is about to be deleted
  spends a decision for nothing, so the question was retired rather than
  answered. `PL-011`'s measurements survive in `PL-T691`'s brief.

  What this release did to the numbers is still worth stating, because it is
  what made the growth reachable at all and because the score work is not yet
  scheduled: before the playback multiplier, twelve simulated hours meant
  sitting in front of the application for twelve hours; at 300x it is 2.4
  minutes and about 55 MB, a simulated day is 8 minutes and 110 MB, and a
  simulated week is 34 minutes and roughly 770 MB. Until `PL-T691` and
  `PL-2FM6` land, that growth is unbounded and nothing tracks it - which is the
  cost of dropping rather than deferring, recorded here so it is visible.

- **A documentation sweep** (queue item PL-RCTQ): `docs/MODEL.md`'s interface
  boundary, minimum
  displayed outputs and displayed-precision sections, and `README.md`.

### Designed for forking

Forking a case at a point on it, to compare two managements of the same
patient, is planned-milestone item 12 and is not built here. Item 12's
required property - a branch reproduces its parent exactly at every recorded
sample up to the branch point, element-wise rather than within a tolerance -
is expensive to retrofit and cheap to preserve, so this milestone preserves
it:

- deriving elapsed time from an integer step count removes the accumulation
  order that would otherwise make a resimulated prefix differ from a
  straight-through one;
- fixing the step at 0.1 s regardless of playback rate removes the step-size
  divergence;
- never catching up to the wall clock removes the machine-speed dependence
  in the number of steps taken, which is the subtlest of the three and would
  otherwise make every run irreproducible on a different computer; and
- the control-input timeline is what lets a point *between* recorded samples
  be reached by resimulation at all; and
- the substance-keyed history record (above) is what keeps item 6 (nitrous
  oxide) from reshaping the record item 12's reproducibility proof is written
  against, after that proof exists.

What is deliberately *not* designed for in advance: per-compartment agent
amounts in the snapshot, a schematic view, run comparison, or a snapshot
policy. Those are cheap to add when their milestone arrives, and adding
unused structure now would be speculative generality rather than
groundwork. The distinction is whether retrofitting invalidates recorded
runs or merely adds a field.

### Definition of done

v0.4.0 is complete only when:

- two runs given identical inputs produce element-wise identical recorded
  history at every playback multiplier, asserted by test, and identical
  history on a machine of any speed;
- the simulation step is 0.1 s at every playback multiplier, asserted by
  test;
- a learner can read every graphed compartment in MAC multiples and in
  percent, and can trace the agent's MAC value to its cited source from the
  display;
- a three-hour case can be run, watched, and read end to end in a few
  minutes of wall clock, with the muscle and fat curves visibly diverging
  from the alveolar one;
- every control change during a run is recorded with the simulated time it
  took effect, and is visible on the chart;
- the recorded history is keyed by substance rather than by flat named
  compartment floats, so item 12's reproducibility proof is written against a
  shape a second substance will not change (queue item PL-W3DD);
- changing agent cannot discard a run without the user being told what will
  be lost and confirming;
- the MAC-awake band and the F_A/F_I trace each carry, at the point of
  display, what they do and do not assert;
- `docs/MODEL.md` states the MAC transformation, what a MAC multiple on a
  non-alveolar compartment does not claim, the reproducibility guarantee
  above, and the interface's new obligations;
- the v0.0.2 circuit, v0.1.0 sevoflurane and v0.2.0 multi-agent reference
  tests remain unchanged and passing, and no equation, parameter or
  numerical method has changed; and
- Ruff formatting and linting, strict mypy, pytest, and GitHub Actions all
  pass.

### Explicitly out of scope for v0.4.0

- Nitrous oxide, coadministered gases, and the concentration and second-gas
  effects (items 6-7). This milestone is deliberately taken ahead of them;
  see the note in "Development pathway".
- The multi-substance patient state (Phase 1). Nothing here requires it, and
  the view already consumes an immutable snapshot, so the MAC readout is the
  only piece that changes shape when a second substance lands.
- The anesthesia-machine abstraction, interlocks, agent switching with
  residual washout, direct injection, and end-tidal control (items 1-5).
- Run bookmarks (item 26), forking (item 12), save/load (item 9), replay
  (item 10) and run comparison (item 11) - the replay half of item 8's
  timeline included. Only recording is in scope.
- A schematic compartment view (item 27) and agent cost (item 28).
- A second patient, weight-based scaling, age-adjusted MAC, dead space,
  airway sampling delay, or any depth, BIS or effect-site model.
- Horizontal panning of the chart window (queue item PL-Z7LY), which the
  fit-run scale makes optional rather than necessary.

## Development rules for scientific milestones

- Define equations, units, assumptions, and reference cases before changing the
  scientific core.
- Keep simulation code independent of Flet, wall-clock time, filesystem state,
  and display dimensions.
- Store model parameters as validated data with schema version and provenance;
  do not place executable equations in data files.
- Preserve deterministic results for identical initial state, events, and time
  steps.
- Treat mass accounting and independent reference cases as release gates, not
  optional diagnostics.
- Keep each milestone narrow. New ideas belong below until promoted into a
  scoped release — or in `docs/items/` when they are a task rather
  than a release.

## Keeping the toolchain current

**When a dependency or the interpreter moves, a scheduled run notices and the
owner decides. Nothing upgrades on a schedule, and nothing gates on it.**

This is a multi-year project, so every version constraint in `pyproject.toml`
will be wrong eventually — `requires-python` pins a single CPython minor and
CPython ships one a year; Flet is pre-1.0 and its 1.0 is excluded by an upper
bound; the dev tools are unbounded floors whose behaviour changes underneath
the gate. The failure being guarded against is not a stale pin. It is returning
after a gap to a tree that no longer builds, where the upgrade that would fix
it is several versions wide and the cost of coming back exceeds what a hobby
project will pay.

It is not hypothetical here. `pyproject.toml` records the instance: pydantic
2.12.4 began passing `prefer_fwd_module=` to `typing._eval_type`, a keyword
CPython added between 3.14.0rc2 and 3.14.0 final, and parameter loading in the
scientific core stopped working. One dependency, one patch version, one
interpreter build.

**What notices.** `.github/workflows/drift.yml`, monthly and on demand. Two
questions, both of which `quality.yml` is right not to ask:

- *`dependencies`* — the newest release each bound in `pyproject.toml` already
  allows, resolved with `uv sync --upgrade`. A failure means a dependency broke
  us inside a range this project has already said it accepts.
- *`interpreter`* — the newest stable CPython, with the upper bound on
  `requires-python` relaxed in the runner only. A failure means the next
  interpreter is not ready for this tree, or this tree is not ready for it.

It also prints what exists *beyond* the declared bounds without failing on it,
because crossing a major bound is a deliberate migration and not something CI
should attempt. That step is how the availability of a Flet 1.0 or a pydantic 3
reaches anyone at all.

**What does not happen.** No automated dependency pull requests, and no
version-bump campaign. The current pins are correct today; the point is knowing
when one stops being correct, not raising numbers on a schedule. Automated
bumps were considered and rejected on the evidence this project already cites
about narrow versus broad automation: broad automation accumulates noise until
it is routed around, which is the failure `PL-ZBJ0` records.

**Why it reports rather than gates.** The versions it resolves are outside
anyone's control here, so gating would let an unrelated upstream release block
this project's own work. A red run is news to act on when convenient, not a
stop signal.

**And it is retired if it stops being news.** `CLAUDE.md`'s retirement test
applies: a check that fires every run without changing a decision is a defect
in the check. If this becomes weather, delete the workflow rather than working
around it.

## The debt gate

**Recorded technical debt is cleared before a new milestone begins.** Phase 0
applies this once, to get out of a queue that had stopped shrinking. This
section makes it standing: it runs again before every milestone, not only the
first.

The reason is that debt is cheapest to clear while the code it describes is
still the code someone remembers. A defect carried across a milestone boundary
has to be re-diagnosed against a codebase that has since moved, and a decision
left unanswered stops being a decision anyone can make. Deferred debt is not
kept; it is paid for twice or silently dropped.

### What counts

Debt is what the queue already records, minus new work. An open item is debt
when it is classed `defect`, `safety`, `science`, `refactor` or `perf`, or when
its status is `needs-decision` — an unanswered decision is debt whatever it is
about.

An item classed `feature` or `planning` is **not** debt. It is the work the
gate exists to protect, and counting it would make the rule say "do everything
before doing anything", which no gate can open.

**Process work is debt once the mechanism is live, not before.** Building a new
capability into the tooling is new work and does not hold a gate. A mechanism
that `main` already depends on and that does not reliably work is debt, and is
classed `defect` like any other defect — the class carries the rule, so there
is nothing extra to track. The distinction is state, not layer: an unbuilt
tooling idea costs nothing to carry, while a half-working mechanism the project
is already running on charges interest every session, which is what debt means.
Half-finished process machinery must not be in production use; either it is
made to work reliably, or it is abandoned and removed.

A caution the first pass through this got wrong: classing tooling breakage as
`infra` rather than `defect` makes it indistinguishable from a capability
nobody has built yet. `docket release` leaving `uv.lock` stale and breaking
`make check` at every release is a defect; adding release tagging is not. If
the class does not separate them, the gate cannot either.

Clearing means `done` **or** `dropped` with the reason recorded. Deciding
something is not worth doing is a legitimate way to clear it, and often the
right one; what is not legitimate is leaving it open and starting anyway.

### The gate is a snapshot, not a moving target

**What a freeze closes is new scope, not the completeness of a fix** (project
owner, 2026-08-30). A frozen list exists to fix a specific set of problems;
refusing the finding that one of its entries needs in order to actually be
fixed preserves the list's length at the cost of its purpose. The rule below is
how that is applied, and it is deliberately not symmetric: new work is kept
out, and what an entry needs is let in.

**And it is worked with the entry it completes, not after it** (project owner,
2026-08-30). Admitting a finding to the list and then working it as a separate
piece of work later reintroduces exactly what admitting it prevented: the first
entry ships half-fixed while the thing that finishes it waits in the queue. So
pair them - one branch, one review, closed together - and the issue is fully
addressed before anything else starts.

**When a milestone is scoped, the debt list is frozen at that moment.** A
finding re-enters this gate — rather than waiting for the next one — when the
problem it describes was already *present* at that moment, whatever id it is
filed under or however long after the freeze it happened to be noticed. It
defers to the next gate only when the problem itself is new: introduced by
work done while clearing this gate or implementing the milestone it protects.

This is the part that makes the rule survivable rather than a deadlock. Work
generates findings — clearing thirteen items in one session generated fourteen
new ones, which is normal and is the capture rule doing its job. Against a
gate that reopens for everything noticed after freezing, that is a queue which
can never empty and a milestone which can never start; the rule would then be
abandoned rather than followed, which is worse than not having it. Presence
rather than discovery time is what keeps it from reopening for *that* kind of
finding while still closing the gap where a stranded branch or a slow session
means the same problem gets rediscovered under a new id (queue item `PL-64LS`).

**Friction that compounds is the clearest presence case** (project owner,
2026-08-30). A finding whose cost is paid again by every remaining entry - a
tool that answers the wrong question, a check that cries wolf, a command that
ends red on success - was almost always present at the freeze and merely
invisible until the gate's own work started paying it. Deferring one is a
decision to pay it once per remaining entry, so it re-enters, and it is worked
early rather than merely admitted.

The test is arithmetic, not enthusiasm: name what each remaining entry pays and
multiply by how many remain. `PL-0RS6` qualified at eighteen entries times a
twelve-command detour apiece, which is a large fraction of the saving the
release exists to deliver. Work that is merely valuable, cleaner or more
interesting - rewriting a working tool in another language, adopting a nicer
abstraction - makes no remaining entry cheaper, so it fails the test and waits
for the roadmap however appealing it is. If the per-entry saving cannot be
named, the finding does not qualify.

**Presence is a presumption, not an absolute rule.** Favor it: a finding that
continues or completes an item already inside the frozen list belongs to this
gate, recorded with what it continues — `PL-SWFM` continuing `PL-Z4GF`'s
already-frozen scope is the case that motivated writing this down. Where a
specific reason argues otherwise — the finding has no real connection to
anything frozen, or pulling it in would recreate the refilling-queue problem
the debt gate replaced Phase 0 to solve — a session may defer a
presence-qualifying finding to the next gate anyway, or decline to pull in one
that only superficially resembles frozen scope. Either way it must say so and
say why: silently reinterpreting which gate a finding belongs to is the
renegotiation freezing the list exists to prevent.

Two further exceptions re-enter the current gate regardless of presence:
anything at `P0`, and anything classed `safety` or `science`. Those are not
deferrable by this project's own standard, and a gate that let them wait would
be inverting the reason it exists.

### The cadence

The gate is a recurring step on the plan, not a precondition assumed in the
background. Every milestone runs the same four beats, and "The plan" above
shows them on one timeline with the milestones they gate:

1. **Scope** the milestone here — goal, required scope, definition of done,
   explicit out-of-scope list. Scoping is the act that freezes the list.
2. **Freeze and record** the debt list in that milestone's own section, as
   item ids, on the day it was frozen.
3. **Clear** it — every item `done`, or `dropped` with its reason — before
   implementation of the milestone begins.
4. **Implement** the milestone. A finding made while clearing or implementing
   goes to the next gate unless the problem it describes predates the freeze
   (per "The gate is a snapshot" above) or is `P0`/`safety`/`science`, either
   of which re-enters this one.

A milestone whose gate has not been recorded has not been scoped, whatever
else has been written about it.

Which beat is due is computed rather than recalled: `bin/docket wave` reads
the version, the timeline above, the milestone sections and the frozen list
each one records, and reports the step and the beat that leaves. It reports
only what those files decide — not whether a gate should open early, and not
whether what is written beside a step is still true.

**A gate does not get a version.** Cleared gate work ships inside the
milestone it gates: it lands between that milestone's predecessor and its own
release, so the milestone's release notes carry it, and no interim release is
cut partway through clearing. `docket release` will offer one as soon as a
few gate items are finished — decline it, or the gate work scatters across
patch releases and the milestone ships carrying only its feature work.

Gate 0 is the single exception, released as v0.3.0 for the reason recorded
under "Versioning decision". It is exempt because it holds the backlog
inherited from before this mechanism existed; every later gate holds one
milestone's findings and is ordinary maintenance, which is not a thing to
version.

### Debt inside the milestone's own scope

**Debt that the milestone itself exists to clear is cleared *by* it, not
before it.** This carve-out is necessary rather than convenient: v0.4.0 was
scoped in part *because* six safety, science, defect and perf items were all
symptoms of the same thing, and requiring them to be cleared before the
milestone that clears them is a rule with no satisfying order.

The test is whether the item appears in the milestone's "Required scope". If
it does, it is milestone work and is listed in the frozen gate under a heading
that says so; the gate is open when everything *outside* the milestone's scope
is clear. If it does not, it is cleared first, whatever it is about.

This does not weaken the `safety`/`science` re-entry rule above. Such an item
inside the scope is still not deferrable — it just cannot be finished earlier
than the work it is part of, and the milestone's definition of done is what
holds it.

### Recording it

Record the frozen list in the milestone's own section here, as the item ids it
had to clear. A gate nobody wrote down is a gate that gets renegotiated, and
the point of freezing the list is that it cannot be.

## Development pathway

The numbered list below is the catalogue; this is the order it is intended to
be worked in, and why. Phases are groupings of intent, not scoped milestones —
each item still has to be specified individually before implementation, per
the development rules above.

The organizing goal is a mature inhalational simulator before any intravenous
work begins: the science first, then an interface that can actually drive it,
then reproducibility, then IV.

**Phase 0 — foundation. Superseded by the standing debt gate, 2026-08-25.**

Phase 0 is not closed, and on its own terms it cannot be. Its closing
conditions are reproduced below unchanged, followed by their state at the date
above.

Its original text: no new feature work until the existing queue is closed out.
Not because features are unwelcome, but because the last stretch of work felt
like whack-a-mole, and it is worth being precise about why: the queue holds
almost no defects. What it holds is decisions nobody has made. At the time
that was written, nine of twenty-four open items sat at `needs-decision` — over
a third of the queue could not be picked up by anyone, so it never visibly
shrank however much work got done. "All bugs squashed" is not a closing
condition, since absence of defects cannot be demonstrated. These were:

| Phase 0 closing condition | State on 2026-08-25 |
| --- | --- |
| no open item classed `safety`, `science` or `defect` | **Not met.** 6 safety/science and 8 defect-classed items open. |
| no open item classed only as process work (`session-cost`, `docs`, `infra`) | **Not met.** 11 such items open. |
| no item left at `needs-decision` | **Met**, and deliberately unmet again the same day: PL-Y2GG (the license choice) was moved *to* `needs-decision` because it holds a decision only the project owner can make, and recording that is more honest than a `ready` nobody can act on. |
| every outstanding branch merged and a release cut | **Met** for merges — `claude/pl-64ls-promote` is gone from the remote — and v0.2.4 is cut. |

**Why superseded rather than pursued.** The first two conditions ask the queue
to reach zero in categories that every working session refills. The queue held
24 open items when Phase 0 was written and holds 48 now: it doubled during the
period Phase 0 was meant to be draining it, which is not a failure of effort
but the capture rule working as designed. A gate that requires a refilling
queue to empty is a gate that never opens, and the honest outcomes for such a
rule are that it gets quietly abandoned or that it blocks all work forever.

"The debt gate" above is the mechanism that replaced it, and it is strictly
better for the same purpose: it freezes a list at a moment rather than chasing
a moving one, so it is always finite and always openable, and it recurs before
every milestone rather than once. Everything Phase 0 was trying to buy — debt
cleared while the code it describes is still fresh, decisions answered rather
than accumulated — the gate buys on a cadence instead of in one push.

So Phase 0 is retired as a phase. Its unmet conditions are not carried forward
as a backlog; the items behind them are in the current frozen gate, where they
can be worked and finished. Implementing a planned milestone is no longer held
by Phase 0, only by its own gate.

**Phase 1 — scientific maturity.** Generalize the patient's state from one
agent to N simultaneously present substances, then items 6 and 7 (nitrous
oxide, concentration and second-gas effects), then item 1 (machine abstraction
with interlocks), then item 2 (agent switching with residual washout).

The generalization leads because three separate items need the same thing:
holding more than one substance at once, with per-substance kinetics. Agent
switching needs the residual of the old agent while the new one washes in;
nitrous oxide needs a second gas throughout; the second-gas effect needs the
coupling between them. Doing it once, deliberately, is the difference between
one design decision and three special cases.

It also settles the intravenous question without a speculative abstraction.
"A substance with compartmental kinetics and an effect site" is the same shape
an intravenous agent needs, so IV becomes an extension rather than a rewrite —
but only if the generalization is designed as substances rather than as
"volatile agent, plus nitrous oxide as a special case". That framing is a
requirement of this phase, not an optional nicety.

Nitrous oxide sits before any interface work for two reasons: the second-gas
effect is the phenomenon this class of simulator is most used to teach, so
without it there is no credible inhalational simulator to build an interface
on; and it changes the core equations, so an interface built on a single-gas
core would be reworked when it lands.

**Reordering (project owner, 2026-08-25): the teachable case is taken ahead
of Phase 1.** As written below, Phase 1's substance generalization and nitrous
oxide precede all interface work, on the reasoning that an interface built on
a single-gas core would be reworked. That ordering was reconsidered once the
interface was measured against what a learner can actually do with it: the
run advances at 1x real time and the chart spans five minutes, so neither the
muscle nor the fat curve can be observed, and no lesson in uptake and
distribution currently reaches anyone. Building coupled-gas equations first
would produce a more capable engine that still teaches nobody, and would do it
without the feedback from real teaching use that should shape what the
multi-gas display looks like. The rework this accepts is bounded and known:
the view consumes an immutable `SimulationSnapshot`, so the time base,
playback, event marks and axis handling are substance-agnostic, and the MAC
readout - which becomes a MAC sum when a second substance lands - is the piece
that changes. v0.4.0 is that work; Phase 1 follows it unchanged.

**Phase 2 — an interface that can drive the machine.** Consolidate the
display constants named in item 24 first, then item 24 itself, then items 5,
3 and 4 (end-tidal control, override mode, direct injection), then item 8
(scenario events), item 20 (accessibility), item 25 (playback speed), and
item 26 (run bookmarks).

The consolidation leads because item 24 already names it as a prerequisite,
and because every control added before it spreads the same scattered defaults
further.

Item 26 comes last of those because it depends on both: bookmarks are what
make a playback multiplier usable, and their MAC-threshold kind waits on MAC
becoming a displayed unit at all (PL-DHV7 in the queue). Item 8 is the one
Phase 2 entry Phase 3 cannot start without — its control-input timeline is
what save/load, replay and forking each restore from.

**Phase 3 — reproducibility and comparison.** Items 9, 10, 11 and 12 in that
order (save/load, deterministic replay, side-by-side comparison, forking),
on top of item 8's control-input timeline.

This phase is also groundwork, which is why it precedes intravenous work
rather than following it. Save/load and forking both force the whole
simulation state to be explicit and copyable, and that discipline is enforced
by working features rather than by intention — a more reliable foundation for
adding a drug subsystem than any abstraction designed in advance of one.

**Phase 4 — intravenous agents.** Items 13, 14 and 15 (intravenous
pharmacokinetics and effect site, hypnosis/eBIS, nociceptive response).

**Alongside, as opportunity allows.** Items 21 and 22 (performance,
documentation) are continuous rather than phased. Items 16 to 19
(renal/hepatic dysfunction, cardiopulmonary bypass, ECMO, species profiles)
and item 23 (packaging and distribution) are deliberately later: each is an
extension of a mature model rather than a step toward one.

**The known risk** is that Phase 1 front-loads the hardest work in the plan.
Coupled-gas equations with reference cases are real scientific work and the
most likely place to stall. That is accepted deliberately: every milestone
built before the substance generalization is code written against the
single-agent assumption, and would have to be revisited afterwards.

## Planned milestones

This section is the catalogue of intent; "Development pathway" above gives
the order the items are intended to be worked in. Each item is deliberately
left unspecified (no goal, required scope, or definition of done) until it
is actually promoted into a scoped milestone per the development rules
above — and each item is kept to one improvement, so scoping one does not
implicitly drag others along with it. Exact version numbers after v0.2.3
remain provisional and must be assigned when each milestone is fully
specified.

1. Add a modular anesthesia-machine abstraction with normal
   single-halogenated-agent interlock behavior — the safety baseline every
   later machine feature below builds on. The default fresh gas flow belongs
   to it: today a literal in `core/circuit.py` that `docs/MODEL.md` restates
   without provenance, and the one number in that document's accuracy table
   tracing to no cited file. Scoping this milestone gives it a versioned data
   file and a provenance row (`PL-8DJ7`).
2. Add agent switching with residual washout accounting, after item 1.
   Requires the multi-substance patient state described in "Development
   pathway" — residual washout means holding two agents at once.
3. Add an optional experimental-override mode that can bypass standard
   interlocks, clearly labeled as non-standard, after item 1.
4. Add direct agent injection into the circuit, bypassing the vaporizer and
   its interlocks, after item 1.
5. Add automated end-tidal control (closed-loop titration to a target
   end-tidal concentration), after item 1.
6. Add nitrous oxide coadministration as a second inhaled gas, only after
   coupled-gas equations and reference cases are defined. Model the patient's
   state as a set of substances rather than as a volatile agent with nitrous
   oxide bolted on: the same generalization is what items 2 and 7 need, and
   what decides whether item 13 is an extension or a rewrite.
7. Add concentration and second-gas effects for coadministered gases, after
   item 6.
8. Add scenario events (timed parameter or state changes during a run),
   built on a recorded control-input timeline: every fresh gas flow,
   vaporizer dial, ventilation and cardiac-output change stamped with the
   simulated time it took effect, held alongside the state it describes
   rather than in the view. The controller today records concentrations but
   nothing records *why* they moved, so a run's inputs are unrecoverable
   once made. This is the prerequisite under items 9 to 12, and it is easy
   to mistake for solved: a state snapshot lets a run be *restored*, but not
   a point *between* snapshots reached, because that needs the same inputs
   re-applied over the same interval — so "resimulate from the nearest prior
   snapshot", the fallback in every snapshot-interval design, cannot be
   implemented without it. It is also what makes a run reproducible and
   citable; a curve without its input history is not a result anyone can
   check. Hence the 8-to-12 ordering in "Development pathway" above is not
   negotiable.
9. Add scenario save/load.
10. Add deterministic replay of a saved scenario, after item 9.
11. Add side-by-side comparison of multiple scenario runs on a shared time
    axis, each curve unambiguously labelled as to which run and which
    settings produced it. Delivered with item 12, which produces the runs
    worth comparing.
12. Add simulation forking (branch a running simulation into an independent
    copy). This is the educational payload of the group: comparing two
    managements of the same case — coast on low flow versus hold 0.5 MAC,
    then compare time to a wake-up threshold — isolates the variable under
    study, where building the case twice differs by everything that was not
    reproduced identically.

    *Scope (project owner, 2026-08-25).* Flat, not a tree: one trunk run
    with N branches taken from points on it. Sub-forks of forks are
    deliberately out — they multiply without bound and buy little over
    re-branching from the trunk.

    *Branch points (project owner, 2026-08-25, confirmed against the Gas Man
    Owner's Manual, "Replaying Simulations" and "Edit menu — Rewind").*
    Supersedes this note's original framing, which treated bookmarks as the
    branch mechanism and an arbitrary point as a rare, resimulated fallback.
    A branch point is not only a placed bookmark: any recorded
    control-input-timeline event — a fresh-gas-flow, vaporizer, ventilation,
    or cardiac-output change, whether or not a bookmark sits there — is
    itself a valid branch point. This matches Gas Man's own behavior: making
    a substantive change during replay truncates the run at that point, and
    continuing extends it "with new, alternate results, just as it would
    have done had the original simulation included the revising adjustment."
    This project's forking generalizes that single-track truncate-and-continue
    behavior — Gas Man keeps one active timeline, overwritten past the change
    point — into true forking, where the pre-change branch is kept rather
    than discarded, so both are available for item 11's side-by-side
    comparison. Because item 8's control-input timeline already stamps every
    such change with its simulated time, resimulating from any of them is not
    a rare fallback but the ordinary case — cheap, per the measurement below,
    and needing nothing beyond item 8's own data. Bookmarks (item 26) remain
    useful as the *named, threshold-triggered* subset a learner can
    fast-forward to and fork from repeatably; they are not the only subset
    that qualifies.

    *Required property.* A branch taken at time t must reproduce its
    parent's state exactly at every recorded sample up to t — asserted
    element-wise, not within a tolerance. Resimulating from a stored point
    while the parent was simulated straight through can diverge *before* the
    branch point, and that divergence is subtle, will not show up in a
    nominal test, and destroys the one thing forking is for, since a learner
    reading the comparison cannot see it. Two of the three causes this note
    named are closed as of PL-VM40 (v0.4.0's Required scope): accumulation
    order for `elapsed_s`, since simulated time is now the step count times
    the run's step, and a different number of steps per frame, since the run
    loop takes a fixed number per tick and never catches up. What is left is
    a different step size, which `docs/MODEL.md`'s "The reproducibility
    guarantee" states it does not cover, and whatever a branch restores from
    a stored point rather than resimulating. If exactness is unreachable, the
    divergence must be bounded, documented in `docs/MODEL.md`, and shown to
    the user rather than implied to be absent.

    *Measured 2026-08-25, so the storage question is designed around the
    right cost.* The full dynamic state is six concentrations plus elapsed
    time and the control settings — a snapshot is about the size of one
    history sample, so snapshot density is nearly free. Resimulation is also
    cheap: `SimulationState.advance` measured at 8.9 us per 0.1 s step, so
    reconstructing a 3-hour run from t=0 is about 1 s and 24 hours about 8 s.
    What is *not* cheap is the per-step concentration history itself.
13. Add IV pharmacokinetic and effect-site models, after item 12 (simulation
    forking) is available.
14. Add a modular hypnosis/eBIS effect model, with explicit model version and
    provenance.
15. Add a modular nociceptive-response effect model, with explicit model
    version and provenance.
16. Add validated renal/hepatic dysfunction modifiers, where supported by the
    selected model.
17. Add validated cardiopulmonary bypass modeling, where supported by the
    selected model.
18. Add validated ECMO modeling, where supported by the selected model.
19. Add species-specific patient/model profiles without treating non-human
    patients as scaled humans.
20. Improve accessibility (keyboard navigation, contrast, screen-reader
    support, color-vision-safe encodings).
21. Improve performance, working from the open entries in
    `docs/items/`. The render payload and the simulation/render
    cadence coupling are both resolved; what remains there is the
    controller's still-unbounded concentration history and further headroom
    in how chart points are built.
22. Continue documentation work.
23. Add packaging, signing, and distribution work for shipping the app.
24. Add a user-facing preferences/settings panel (theme, chart window, slider
    ranges, and similar display settings). Pre-requisite: consolidate the
    UI/display constants currently scattered across `app/theme.py`,
    `app/simulation_view.py`'s module-level constants, and the default
    values duplicated between `core/*.py` dataclasses and
    `app/controller.py`, into one settings module the panel can read from
    and write to, rather than adding a fourth scattered location. This
    panel must never expose the scientific parameters in `data/**/*.json`
    (partition coefficients, tissue volumes, etc.) for editing — those stay
    validated, versioned, and cited, changed only through deliberate
    scientific review per `CLAUDE.md`'s safety-critical standard, not an ad
    hoc settings screen.

25. Add a playback speed multiplier, so a run can be advanced faster or slower
    than real time without changing the simulation's own time step. Kept
    separate from deterministic replay (item 10): replay reproduces a recorded
    run, while this changes the rate at which any run is displayed.
    *Shipped in v0.4.0 as `PL-SN2C` - see "Completed: v0.4.0 - the teachable
    case" above. Five rates (1, 5, 20, 60, 300x), implemented as steps per
    tick so the simulation's own step never changes size.*
26. Add run bookmarks that halt a run at a target, after item 25. There is
    currently no way to say "run fast until something happens, then stop": a
    learner comparing gas-management strategies has to watch the clock and
    pause by hand, which is neither repeatable nor possible at speed.
    Bookmarks are what make fast-forward usable, and they are the branch
    points a learner deliberately returns to by name — item 12's "Branch
    points" note treats every control-input-timeline event as a valid branch
    point, not bookmarks alone, but the bookmark set is still what a
    snapshot policy should key on: it is the subset a learner is expected to
    revisit repeatedly, so it is worth keeping cheap to reach even where an
    arbitrary timeline point is not.

    *Scope floor (project owner, 2026-08-25, confirmed against the Gas Man
    Owner's Manual, "Using Bookmarks," and current-application screenshots
    the project owner supplied).* The Gas Man reference simulator's bookmark
    set is the minimum, and is two distinct mechanisms under one dialog
    ("Place or Remove a Bookmark"), not one kind with two flavors: **time
    bookmarks** — an absolute simulated time (hours/min/sec), which is all
    the manual's own "Using Bookmarks" section describes and is the older of
    the two — and **MAC targets** — a percent of MAC on a chosen graphed
    compartment (circuit, alveolar, vessel-rich, muscle, fat or mixed-venous,
    not the alveolar trace only), added to the application after that manual
    text was written and confirmed only from the current UI, not the manual.
    Keep both as first-class, separately listed collections rather than
    merging them into one "bookmark" type with a kind field — that is the
    shape Gas Man's own dialog uses, and it is what lets a UI list bookmarks
    and targets separately the way the reference does. The MAC kind cannot
    be specified in a unit the application does not have, so PL-DHV7 (MAC as
    a displayed unit) lands first.

    *Required properties.* Crossings are tested on every simulation step,
    not once per rendered frame: testing per frame overshoots by the whole
    frame's worth of simulated time, and the faster the playback multiplier
    the worse it gets, so the same bookmark would halt at a different
    concentration depending on how fast the user was running and the
    displayed halt value would not be the value asked for — a
    presentation-correctness failure of the kind `CLAUDE.md` treats as
    safety-critical, and one that also breaks reproducibility of any branch
    taken from that bookmark. Crossing direction is explicit — rising,
    falling or either — and shown wherever a bookmark is listed, since the
    same threshold means opposite things during wash-in and washout. A
    threshold above a compartment's asymptote is unreachable, so a bookmark
    needs a distinct "not reached, run-time cap hit" outcome that reads
    differently from "reached" rather than stopping silently. Bookmarks are
    part of the saved scenario rather than session-local, so item 12 can
    branch from them.

27. Add a schematic compartment view alongside the graph - the interactive
    "Picture" of the Gas Man reference simulator, in which the machine,
    circuit, lungs and tissue groups are drawn to scale and fill as agent
    enters them. This teaches something the graph structurally cannot: the
    graph plots partial pressure, so fat reads near zero for hours while
    holding more agent than every other compartment combined. Where the drug
    *is*, in millilitres, and where the *tension* is are different questions,
    and confusing them is a standard novice error. Needs per-compartment agent
    amounts exposed on the snapshot, which the core already computes and the
    snapshot does not yet carry.
28. Add agent cost, from the exhausted-agent amount the model already tracks.
    The economic argument for low fresh gas flow is a standard teaching point
    and currently the one lesson in this class of simulator that the
    application has the numbers for and does not draw. Depends on nothing;
    kept out of the v0.4.0 scope because it is an addition rather than a
    prerequisite.

29. Make `core/` read like the domain, as one deliberate pass over the whole
    package rather than opportunistically. `CLAUDE.md` sets the bar — a
    clinician who knows uptake and distribution should recognize the
    physiology without a translation step — but it was written after most of
    `core/` was, so it governs new code and has never been applied backwards.
    The purpose is the project owner's own fluency in the code: reviewing the
    coupled-gas equations of items 6 and 7 is the hardest scientific work on
    this plan, and doing it against code that reads like the textbook is a
    different task from doing it against code that does not.

    *Placement (project owner, 2026-08-26; revised 2026-09-02).* After
    v0.4.0 and ahead of item 6's substance generalization. The second half
    is the original constraint and is unchanged: that change restructures
    every compartment, and settling the vocabulary first makes it a
    transformation of well-named code instead of a renaming and a
    restructuring at once. The accepted cost is that some of this is
    revisited when compartments become per-substance; what survives is the
    convention, which is the part that is expensive to invent twice.

    The first half moved, and what it cost is worth recording. Placed
    between v0.3.0 and v0.4.0, this unscoped pass over `core/` was the gate
    on the whole teachable-case milestone, and it bought nothing there:
    v0.4.0 changes no equation, parameter or numerical method, so the
    fluency it exists to provide is not exercised until items 6 and 7.
    Nothing between v0.4.0 and v0.7.0 touches `core/` either — v0.5.0 and
    v0.6.0 are interface releases on an unchanged model — so the step is
    free anywhere in that span, and it now sits immediately after v0.4.0 as
    the `v0.4.x` row of "The timeline", which keeps the benefit as early as
    the constraint allows.

    *Scoped 2026-09-03 (project owner), and the three open questions are
    answered. Re-scoped the same day, and it is no longer a patch.*

    **The bar, stated by the project owner 2026-09-03:** a reviewer who knows
    the standard variables and equations of the textbook should be able to
    follow `core/` and recognize them, without referring to `docs/MODEL.md` and
    without a lookup table. That is a sharper test than the one-line bar in
    `.claude/rules/core-domain.md`, and it is what the answers below are held
    to.

    **Naming alone cannot reach it, which is what the re-scope found.** The
    alveolar balance's two terms are computed in two different steps of the
    operator split, separated by a third, and the pulmonary uptake term is
    never formed at all; three of the five composed sub-steps are objects of
    the splitting scheme rather than of the domain. The equations exist in the
    repository in exactly the right form — in the independent RK4 oracle, which
    may not be imported from `core/` without making the verification a
    tautology. So the split is replaced by the exact matrix exponential
    (`PL-GS5X`), under which assembling the system matrix *is* transcribing the
    governing equations, and the code that computes the answer is the code a
    reviewer recognizes. `PL-SPMQ` carries the measurement and the options that
    were weighed.

    That supersedes `PL-6GS0`, which decided in v0.2.8 to keep the split. That
    decision weighed accuracy and step size and was right on them; the
    readability requirement was not in its frame. `PL-X9KD` re-derives every
    published statement that was justified by the splitting error: § "Displayed
    precision", the supported step bound, and the pinned reference states.

    *Version: a patch in the `v0.4.x` track, and no exception is recorded for
    it (project owner, 2026-09-03; the specific number released 2026-09-05).*
    The class is the decision and it is unchanged; what was dropped is the
    promise of `v0.4.1` in particular, which the release path cannot keep —
    `docket release` gives the next free number to whatever is finished, so a
    patch cut before this work lands takes it. The number this ships under is
    whatever the cut assigns. This was briefly recorded as a minor earlier the same
    day, reasoning from the size of the change; "Versioning decision" above
    chooses by the **capability boundary crossed**, and this step crosses none.
    The simulator models the same system with the same parameters, the same
    four controls, the same three agents, and the learner can do nothing they
    could not do before. Two things do change and neither is a capability: the
    displayed value moves in its last digit, which v0.2.11 shipped as a patch
    already, and the *guarantee* strengthens from "within a measured bound of
    the stated equations" to "the exact solution of them". The step bound may
    well survive with a different justification rather than disappear, so even
    the accepted-input set may be unchanged — `PL-X9KD` settles that.

    The temptation is to number it up so the change can be pointed at, which is
    exactly the argument the v0.3.0 exception made and which that exception
    says is not a precedent. The release row and baseline section are where a
    change gets pointed at; v0.2.8's row already records why the split was kept
    over an exact matrix exponential, and this release's row records why it no
    longer is.

    Nine items carry it. `PL-GS5X` and `PL-X9KD` under `numerical-domain`, six
    under `core-domain-language`, and `PL-X2XX`, which `PL-VZL0` requires and
    which went unlisted here until `PL-GGCN` taught the checker to read the
    second half of a compound prerequisite. `PL-P0BB` was a tenth and is not:
    the state-vector decision it recorded shipped in v0.3.2, so counting it
    made the step look as though it still had an open design question at its
    head when the question is answered. Corrected 2026-09-05 (`PL-YYL2`); the
    timeline row above carries the same list and the same correction.

    **What "reads like the domain" means concretely.** Not a symbol-to-
    identifier mapping, which was the shape guessed at here before the pass
    was measured. Identifiers in this project carry their unit or kind
    (`alveolar_ventilation_l_min`), which a bare symbol cannot do, and the
    compartment object already supplies the subscript, so $`F_A`$ in code is
    `alveoli.<accessor>` rather than any single identifier. The mapping is
    therefore from a symbol to an **expression**, held as a fourth column of
    `docs/MODEL.md` § "Symbols" (`PL-H46J`), which makes the pass finite and
    checkable at once. Beside it sits one name per modelled quantity:
    `core/` currently gives the partial-pressure-equivalent fraction eight
    names across four compartments, which `PL-9SH6` collapses to one.

    **Whether equations belong in the code or are cited from it.** Both, and
    the line between them is sharper than "per-case". `docs/MODEL.md` writes
    the differential equations while `core/` implements their analytic
    solutions, and the spec carries a solved form in exactly one place, so a
    docstring restating the solved form is the missing half rather than a
    second source of truth. The rule is therefore: cite always, restate only
    the solved form the spec lacks, never restate what it states (`PL-VZL0`).

    **How much of the bar is decidable.** Three rules, all mechanical:
    every Code cell resolves to a real attribute, the retired accessor names
    never reappear, and a partition-coefficient identifier names both phases
    in order (`PL-FZ6T`). A unit-suffix check was considered and rejected —
    the suffixes are already near-universal, so it would be a pure ratchet
    whose vocabulary needs maintaining. What stays judgment is the question
    the bar is written as: would a reader who knows the domain guess this?

    **What the sources changed.** Two references, supplied by the project
    owner during scoping, settled questions the pass could not settle from
    inside the tree. Hendrickx and De Wolf establish that the domain's
    gas-phase cascade is $`F_D \rightarrow F_I \rightarrow F_A`$ and has no
    $`F_C`$, so the middle state is named after its container rather than the
    clinical quantity, and the $`F_A/F_I`$ curve this simulator exists to draw
    has a denominator that cannot be found by name in the code (`PL-3TLK`);
    they also record that in the gas phase "fraction", "concentration" and
    "partial pressure" are interchangeable, which settles the accessor name
    against a convention distinguishing them. Baker and Farmery name one
    partition coefficient three different ways within a single chapter, which
    is why the naming rule for ratios is worth enforcing mechanically rather
    than left to a reader's recall (`PL-212V`).

    No behavior, equation, parameter, or numerical method changes, so it
    crosses no capability boundary and takes a patch version rather than a
    minor, per "Versioning decision".

30. Add patient factors - age, sex and weight as inputs - so a
    learner can see how patient characteristics change the anesthetic. This
    is a core teaching component rather than a later extension: the
    reference adult in `data/patients/reference_adult.json` is a placeholder
    for it, and "how would this differ in this patient" is the question a
    compartment model exists to answer. Today the application's only
    statement about patient variability is that there is none.

    Built-in patient profiles stay read-only and support a "duplicate and
    customize" workflow carrying lineage and schema metadata, so a modified
    profile can always be traced to the cited one it was derived from. That
    requirement predates this item, where it sat as an unattached sentence at
    the end of this section with nothing to own it.

    *Body composition defaults, and is editable per case (project owner,
    2026-09-02).* A case opens with a body composition already set rather
    than asking the learner to supply one, and case settings expose it for
    editing when changing it is the point of the run. That answers the
    derivation question below in one direction: the default is *derived* from
    the case's other patient inputs, so an edit overrides a value that was
    already there rather than filling a blank. Two consequences follow,
    neither of them in this item's scope as it currently stands. The derived
    value has to be visible and attributed wherever it acts - which rule
    produced it, and whether it is still the default or has been overridden -
    because a silently substituted body composition that moves fat uptake is
    exactly the plausible-but-unexplained clinical value the safety standard
    refuses. And an edited composition is a covariate set nobody sourced, so
    the supported-range refusal below binds the edit control exactly as it
    binds the input: accepting a hand-entered composition outside the
    parameter set's domain is the same failure as extrapolating to it. There
    is no case-settings surface today - the interface's only patient is the
    single hard-coded `data/patients/reference_adult.json` - so this names an
    intended surface rather than an existing one.

    *MAC basis (project owner, 2026-09-02).* `mac_percent` moves from the
    flat Gas Man values the agent files now carry - sevoflurane 2.0,
    isoflurane 1.2, desflurane 6.0 - to the Mapleson MAC40 basis, in the
    release that adds age. Nickalls and Mapleson (Br J Anaesth
    2003;91(2):170-4) is already cited in all three of `data/agents/*.json`
    with a note recording that it is *not* used because this model has no age
    parameter; this is that note becoming live. Their meta-analysis has
    log10 MAC falling linearly and in parallel for every inhaled agent at
    about 6% per decade for age >= 1 year, expressed from MAC at 40 years,
    with MAC40 reported as 1.17% isoflurane, 1.80% sevoflurane and 6.60%
    desflurane - figures to confirm against the primary paper when this is
    scoped rather than to copy from here, per the provenance standard every
    other parameter in `data/` is held to. Those are not the values the files
    carry, so the displayed MAC changes at every age *including* 40. This is
    therefore a parameter-set change needing a provenance row and a release
    note, not a new input field, and it lands after `PL-DHV7` (MAC multiples
    as a display unit): an age-adjusted MAC with no MAC unit to show it in
    changes nothing a learner sees.

    *Placement (project owner, 2026-09-02).* Phase 1, ahead of the substance
    generalization. That generalization is this plan's stated known risk and
    the most likely place to stall, and a core teaching component does not
    belong behind it; and once compartments hold N substances, changing how
    compartment volumes and flows are *derived* touches N times the surface,
    which is the argument that already places item 29 ahead of that work.

    *Scaling: not through body composition (project owner, 2026-09-02).*
    Weight scales the compartments directly. A route in which weight, height
    and sex first produce a body-composition estimate, and that estimate
    scales the compartments, was proposed and declined; sex is therefore a
    covariate in its own right rather than something acting through fat mass.

    The trade is worth recording rather than arguing, because scoping will
    meet it. Fat is the pivotal compartment for volatile agents - tissue:gas
    coefficients of 34 (sevoflurane), 70 (isoflurane) and 13 (desflurane) -
    so between two patients of the same mass and different composition it is
    the fat compartment that separates them, and a rule keyed on total mass
    cannot express that difference. What the direct route buys is one fewer
    layer of unsourced derivation: a body-composition estimate needs its own
    formula with its own provenance, and an unsourced scalar in front of the
    dominant compartment is the "plausible but incorrect clinical value"
    `CLAUDE.md` forbids just as surely as no scalar at all. Whichever rule is
    chosen, it is sourced before it ships. `Meybohm et al. 2021`, already
    cited in `data/patients/reference_adult.json`, is the obese case explored
    with the same reference simulator this project draws its parameters from,
    and is where scoping should start reading.

    *An out-of-range covariate: agreed in principle, cutoffs unresearched
    (project owner, 2026-09-02).* Bounding a covariate and reporting when one
    is outside its bound - blocking, logging, or both - is accepted as the
    right shape. What is **not** settled is where any cutoff sits, and no
    number is written into `core/` until it is researched and sourced on the
    terms every other value in `data/` is held to. A bound invented to have a
    bound would refuse the paediatric or obese case a learner most wants, on
    a number nobody can cite, which is worse than no bound at all.

    So this is a research question before it is an implementation one, and it
    is part of scoping this milestone rather than a queue item that could be
    picked up ahead of it. Two things frame it. `core/supported_ranges.py` is
    the nearest pattern and its argument still holds - a silently extrapolated
    patient would simulate, display and chart a value the parameter set cannot
    support - but it is not the same case: those four are operating settings
    inside a run, where refusing costs nothing, while a covariate defines the
    case itself, and refusing to construct a 3 kg or a 200 kg patient refuses
    the question a learner came with. That asymmetry is why the mechanism is
    open rather than inherited.

    *The teaching payoff needs item 11.* A single trace cannot show an effect
    - the contrast is the lesson - so what this milestone is *for* only fully
    arrives with side-by-side comparison (item 11) and the two-run rendering
    `PL-B9PY` holds. That is a reason to scope item 11 knowing this is one of
    its uses, not a reason to hold this behind it.

31. Ship a primary-literature partition-coefficient set alongside the Gas Man
    set, selectable, so one case can be run under both and the difference read
    off the same axes. Building the primary set is the prerequisite and the
    larger half: `vessel_rich` is a lumped compartment while Yasuda 1989
    reports per-organ coefficients, so a group-weighting scheme has to be
    constructed and justified before any tissue value may be called primary.
    Shipping both rather than replacing is the point — "how much does the
    parameter set matter?" is a question no commercial simulator lets a
    resident ask, and it teaches the provenance lesson better than any note in
    a data file can. `PL-D6LX` carries the analysis and the verified primary
    values; the project owner chose this route on 2026-09-03.

Item 1 (isoflurane and desflurane) has been promoted into a fully scoped
milestone, delivered as v0.2.0 — see "Completed: v0.2.0" above — so it no
longer appears here. Further volatile agents beyond isoflurane and desflurane (halothane,
enflurane, ether, xenon; not nitrous oxide, which is covered by items 6-7
above) remain an unscoped later idea, to be added back here as its own item
once someone is ready to scope it.

32. Make the repository presentable to a first-time visitor, as one pass. The
    project owner deferred the README rewrite here on 2026-09-05 rather than
    running it as soon as its scope was settled, and expects a number of similar
    human-facing pieces to collect at the same point: written to one reader over
    one week they cohere in a way the same documents written singly over months
    do not.

    **The repository went public before this pass, not after** (project owner,
    2026-09-05: "public today. Will do human facing pass in the nearish
    future."). So this is no longer a gate and blocks nothing — `PL-XYRN` is
    closed against that decision and `PL-N092` (rewrite README as a human-
    readable introduction) is released and `ready`. The pass is owed to a reader
    who can already arrive, which is a stronger reason to run it than the one it
    was deferred under, and it is now the only thing that will surface it:
    nothing is blocked on it and no check reports it, so it waits for a session
    offering to scope this milestone or for the owner to ask. Until it runs, the
    repository is public with no root `README.md` at all — deleted deliberately
    under `PL-WB5K` and its absence now enforced by `tools/readme_hold_check.py`,
    which `PL-N092` removes as part of the rewrite.

None of items 1-32 mix scientific-core and UI/tooling concerns within a
single milestone; where one depends on another (e.g. 2-5 on 1, 7 on 6, 10
on 9, 13 on 12), that dependency is noted inline rather than bundled into
one item.
