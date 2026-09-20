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
| v0.4.2 | Completed | The apparatus patch that closes `docket-store`, changing no shipped code: `src/` and `docs/MODEL.md` are byte-identical to v0.4.1 and the only file under `tests/` that moved is the new check's own suite, so no equation, parameter, numerical method, unit or displayed value moved. Its subject is the instruction budget every session pays and the guards that keep work visible. Resident text can now *shrink*: 563 characters whose carriers already existed were routed out of `CLAUDE.md`, and resident rules gained the retirement test that checks have had since `PL-ZBJ0` — until now a rule could only be added, because nothing said when one had stopped earning its place, and the total falls 44 545 to 44 166 characters. Beside it `tools/rules_paths_check.py` gained its second rule: a `paths:` entry that is anchored and points at nothing is refused, the same silent failure as the `./` spelling v0.4.0 closed, arriving in the form that reads as correct at every glance — a transposed directory name — and the message names the nearest existing ancestor rather than only the offence. Two provenance guards close: seven items stranded on abandoned branches are recovered, two of them created by the score-architecture drops, and the pull-request title check stopped racing the retitle it asks for, which had been showing a red run that meant nothing on a green pull request. Landing during this release's own pull request, the gate learned what it costs to run: the `floor` job billed a whole minute for eight seconds of work and held one of twenty account-wide concurrent job slots, so its steps moved inside `checks` *ahead of* the uv install — which strengthens the no-virtualenv claim rather than weakening it, because at that point no virtualenv exists to fall back on — and a spending limit and usage alert now exist, where the first sign of Actions overage had been the invoice. `README.md`'s status section is corrected too: it understated the operator split's disagreement with the exact solution as 1.2e-2 percentage points where `docs/MODEL.md` gives 2.3e-2 over the same domain, which is the kind of divergence between a summary and its specification that the `v0.4.x` track exists to remove. Nine items, one of which is the v0.4.1 cut itself. |
| v0.4.3 | Completed | The release where the gate learned what it costs, and the repository went public — and the second overtook the first. `src/` is byte-identical to v0.4.2 and `docs/MODEL.md`'s only change is one cross-reference following the deleted README, so no equation, parameter, numerical method, unit or displayed value moved; the sixth such release and the third in a row. **The measured half.** The `checks` job ran 152 s, of which `bin/docket check --verify` was **87 s** — more than the whole 1 820-test suite — because the replay runs every open item's own `verify:` command and 79 of the 111 that carry one start a fresh `uv run pytest`. That bill grew with the size of the queue rather than with the size of the change, and was paid on every push to every open pull request. `--verify-base` now scopes it to the items a branch actually changed, read from the diff, with the whole-store sweep kept on `push` to the default branch where its answer is a fact about that branch — 102 commands in 74.6 s becomes one in 5.5 s, and the job **152 s → 59 s** on run 34000293113. It is `PL-P3B6`'s argument one step on: if a pre-commit gate cannot have changed whether some other item's work merged, neither can a pull request. A scoped run says what it was scoped to on `docket check`'s own cost line, including when the scope held nothing to run, because a narrowed run reporting no findings is otherwise indistinguishable from a store that holds none. Three smaller gate repairs sit around it: `drift.yml` had resolved a newer `pytest-xdist` every month and never run it — a declared dependency upgraded and untested, which is the hole that workflow exists to close — and now runs `-n auto --dist worksteal` on both suites; `tools/contrast_check.py` had been parsing 3.14 `app/` source under the 3.11 floor, green only because the two files it reads happen to carry no 3.12+ syntax, which since v0.4.2 folded that job into `checks` would have reddened the whole job before uv was installed; and the pull-request title check, the one gate no session could run before pushing, now discovers the title from the branch's own open pull request and skips silently on every way that lookup can fail, so `make check` stays green offline. **The published half** is smaller in the diff and larger in consequence. The repository is public — *to stop the Actions billing, not as a publication decision* — which makes the minute arithmetic three of these items were built on moot: standard runners are free and unlimited on public repositories, and what the work still buys is wall clock and the runner slots that throttle parallel sessions. `README.md` was deleted rather than corrected and stays deleted under a check; the human-facing pass `PL-XYRN` gated is deliberately unrun; and both are recorded where a later session would otherwise read a public repository with no front door as a gap rather than a decision. Which leaves the quietest thread: the concurrency comment claimed the repository was public and runners free while it was private, was corrected to private-and-billed, and was wrong again within hours — so its argument now rests on the runner slot, which holds under either answer, with the billing position dated and stated once rather than woven through the reasoning. Twelve items, one of which is the v0.4.2 cut itself. |
| v0.4.4 | Completed | **The code is the model.** The first release in four to touch `src/`, and the first since v0.4.0 in which a displayed number moves. The operator split is gone: each step is now one exact propagation of the whole coupled nine-state system, `exp(AΔt)y`, with `core/governing_equations.py` assembling $`A`$ as a transcription of the balance equations this document states and `core/matrix_exponential.py` computing the propagator without carrying a unit or a compartment name. Scaling and squaring with a shifted Taylor series, about sixty lines of arithmetic on plain lists, adding no dependency. **Accuracy was not the motivation and was not a cost either** — the split was kept once on accuracy, in 2026-08-30, and that decision was right on its own terms; what overturned it was `ROADMAP.md` item 29's bar, that a reviewer who knows the standard variables should follow `core/` without a lookup table. Three of the split's five composed sub-steps were objects of the splitting scheme rather than of the physiology, the alveolar balance's two terms were computed in different sub-steps separated by a third, and the pulmonary uptake rate this document specifies was never formed at all. Measured against the same from-scratch RK4 oracle, the exponential's worst disagreement is eight orders of magnitude smaller than the split's. **Then the harder half, which is what the release is really about.** Three published statements were derived from an error that no longer exists, and each is re-derived from measurement rather than assumed to still hold. § "Displayed precision" had a numerical ceiling (a third decimal was noise) and a legibility floor; the ceiling is gone, since the shipped residual is about 1.6e-12 percentage points, nine orders below the last displayed digit. Its replacement is **model fidelity**: one published standard deviation of a partition coefficient displaces a displayed compartment by 8.7e-4 to 6.8e-2 percentage points, so two decimals puts the last digit between a seventh of one SD and seven times it and a third would put it at a seventieth — false precision. `MAXIMUM_SIMULATION_STEP_S` turned out to have **no derivation at all**: sweeping the step from 1e-3 s to 1e300 s found no numerical ceiling, the propagator entrywise nonnegative at every one of 4374 (settings, step) combinations tested, and control-timing displacement exactly proportional to the step with no knee anywhere — so it is recorded as a *declared tolerance* in percentage points and seconds, not dressed up as a limit. And the splitting-error constants are retired with their reasons recorded in place, after checking coverage rather than after the fact: two of the four retiring tests were reproduced exactly by the new gate, two were not, so the step gate gained the setting-change trajectories and a new `HELD_RUN_ROUNDING_BOUND` replaced the only test driving the shipped solver past 900 s. **The dependency stopped running backwards.** The step bound and the supported input ranges were both justified *through* the two-decimal readout, so a purely presentational move to one decimal would have licensed a step ten times longer; both are now stated in their own units, and a test fails if anything in `core/` reads the display count again. `src/anesthesia_sim/data/` is byte-identical to v0.4.3, so no parameter moved — what moved is the method, and the displayed value in its last digit. Thirteen items, one of which is the v0.4.3 cut itself. |
| v0.4.5 | Completed | **Going public, finished.** v0.4.3 made the repository public to stop Actions minutes being billed rather than as a publication decision, and left the human-facing pass deliberately unrun; this release runs that pass and finds what the sideways route had left behind. Two publisher-copyright full texts — Baker & Farmery 2011 and Schüttler & Schwilden 2008 — were being redistributed from a public repository, against `docs/references/README.md`'s own statement that removing them was a prerequisite for going public. They came out on the day the breach was found, by a `git filter-repo` pass and a force-push rather than a delete commit, because both blobs were in the history from the commit that added them; GitHub Support ticket 4733783 covers the pre-rewrite commits still pinned by `refs/pull/*/head` refs the repository owner cannot reach. **The durable half is a check.** `make check` had passed on the broken state, because `doc_check` verifies the paths `docs/MODEL.md` cites and nothing verified that a file named in the reference index is present; it now refuses an entry naming a file the directory does not hold — the decidable half in code, with whether an entry *should* keep its file left to a person. **The rewrite's own costs are recorded rather than absorbed.** It stripped every commit signature, force-updated branch refs to a snapshot taken before the push and dropped two commits pushed into that window, and left four captures reachable on one branch only. Both losses were recovered, and `bin/docket stranded` learned to tell a rewritten history from an ordinary divergence. A branch deleted in this release's own cleanup held the last copy of two more items, recovered from the stale remote-tracking ref that `git fetch` does not prune — the case the no-prune guard exists to preserve. **And the front door exists.** `README.md` is written against the audience, boundary and status questions `PL-RM83` settled — two domain-literate readers, nothing whose truth is tied to a model version, capability rather than a version string — and retires the check that guarded the file's absence, together with both its invocations, in the same commit that writes it; `pyproject.toml` now describes the project and classifies its maturity, audience and subject. **The one thing that reached `src/` is prose.** `app/playback.py` had said that playing a run faster is "never a modelling one" without qualification: true for a run nobody touches, false for one in which a control moves, because the tick burst has no yield in it and the reachable simulated instants are therefore `multiplier × 0.1` s apart — 0.1 s at 1x and 30 s at 300x. Nothing arrives late and no displayed value is stale; what coarsens is which instants can be chosen, and pause-change-resume stays exact at every rate. `MAXIMUM_SIMULATION_STEP_S` stays 0.1 s on the same finding, argued rather than defaulted: 0.05 s would double the propagations per simulated second and buy tighter timing at 1x alone, since above it the interface's own grid dominates. Three files under `src/` changed and every changed line is a comment or a docstring — all three are AST-identical to v0.4.4 with docstrings stripped — and `src/anesthesia_sim/data/` is byte-identical, so no equation, parameter, numerical method, solver step or displayed value moved. Eighteen items, one of which is the v0.4.4 cut itself. |
| v0.4.6 | Completed | **Provenance read at the source, and three checks that were asserting more than they knew.** `src/anesthesia_sim/core/` is byte-identical to v0.4.5 and every stored value in `src/anesthesia_sim/data/` is unchanged, so no equation, parameter, numerical method, solver step or displayed value moved; what changed under `data/` is entirely what the citations claim. **The reference patient's numbers had never been traced to a document anybody opened.** `PL-6Q8N` set out to read Mapleson's 1963, 1964 and 1973 papers, named in the file as its primary lineage — and found them unreachable from a session: all three return PubMed metadata only, none has an abstract, none is in PMC, and every publisher, index and vendor route is refused by the egress proxy. Re-aimed on the project owner's decision at what PubMed can actually deliver, five of the eleven parameters gained a measurement of the same quantity cited alongside and explicitly *not* adopted — Hudgel and Devadatta's helium-dilution FRC read with Wahba's ~20% reduction under general anaesthesia brackets the lung gas volume at 2.51 L against a stored 2.5; Cattermole et al.'s 686 subjects in the 50–75 kg band give a cardiac-output median of 5.51 L/min against a stored value 9.3% below it; Janssen et al.'s whole-body MRI gives a skeletal-muscle mass whose apparent agreement with the stored 33.0 is *coincidence*, that cohort of men having averaged about 86 kg rather than 70; and Heinonen et al.'s PET measurement of resting adipose perfusion is close to half what the stored fat flow fraction implies. The other six record why no comparison exists rather than leaving the silence to read as an oversight. The fat gap is the one that reaches a learner: time constant is `V·λ/Q`, so a factor of two on fat flow is a factor of two on how much agent fat has taken up by the end of a case and on the slow tail of every washout curve — recorded in `docs/MODEL.md` § "Known limitations" rather than fixed, because one depot in six subjects does not overturn a whole-body lumped compartment. **Then the project owner supplied the Gas Man Workbook, and the guess collapsed.** `PL-XTMB` read it at the source: the Model Parameters table is Appendix B, page 168, and the citation had been pointing at page 183's interface controls, which carry none of the values. The file's own claim to be sourced entirely from that table was false — it supplies **seven of the eleven**; cardiac output appears only as the sum of the flow column; weight and alveolar ventilation are interface defaults with no number in it; and `venous_blood_volume_l` = 1.0 is absent altogether, the table's `Blood` row reading 5.00 L, which leaves a stored value its cited source does not contain (`PL-3YZW`). And the lineage is not Mapleson at all: printed beneath the table, *"Values for volume, flow and relative flow are taken from Lowe and Ernst, 1981"*. That book is recorded as located and unread, inside the Workbook's own note rather than as a citation line of its own — an unread document with its own entry is the Mapleson failure one link later, and the schema made the point first by refusing the empty `url` a 1981 monograph would need. **Three checks were measuring something other than what they claimed.** `tools/contrast_check.py` cited `simulation_view` line numbers for its eight requirements and all eight were wrong, and it could not express a requirement met by either of two channels at all; the mass-balance release gate's absolute tolerance tracked whichever dial its test happened to run at rather than a stated bound; and `docket.toml`'s `workflow_paths` named three `tools` tests by path, so the other seven and every new one fell on the product side of the lane boundary that exists to keep two sessions apart. **Two queue mechanics and one model-boundary correction** close beside them: the closure walk follows renames, so an item renamed after it closed no longer recovers the renaming commit's pull request; the conflict graph is tiered, so a shared file orders work instead of forbidding it — which matters because 27 of Gate 1's entries declare `docs/MODEL.md`; and `SimulationController.set_circuit_volume` is gone, both gas volumes established as data-file parameters rather than controls, with the bound restated on physiological rather than numerical grounds. That restatement then produced the release's third correction: `PL-GYH2` had landed the sentence "the exact propagator solves the governing equations for any positive volumes whatever", written from the argument rather than from a measurement, and run it is false — below 1e-9 L the alveolar compartment raises, at 1e-100 L the step rolls back, and at 1e-300 L it advances and returns exactly zero with the accounting passing. `PL-GJYL` replaced it with the measured statement. **And the first comparison in the elimination direction.** `PL-HB58` extended the project's only external validation to the second quantity both Yasuda papers report on the same volunteers, $`F_A/F_{A0}`$ at five minutes of elimination — and it does not agree: the model holds more alveolar agent at five minutes than every cohort did, by +1.0 to +5.0 published SD. Most of that is apparatus rather than physiology, and it is measured rather than argued: $`F_A/F_I`$ carries the inspired fraction in its denominator so a breathing system divides out of it, $`F_A/F_{A0}`$ has no such term, and this model's rebreathing circuit cannot be set below about 29% of the alveolar fraction at any supported flow — so agent returning from the circuit is counted as though it came back out of the patient. The values are therefore asserted as a *regression* band that claims nothing about agreement, while the published ordering by solubility, the independence from delivered fraction and the sign of the departure are asserted as the validations they are. What the second direction buys is a different axis rather than a tighter one: the wash-in comparison and its flow sweep were still passing at a tenth of the shipped vessel-rich tissue coefficient, and the elimination point closes that tolerance to about a fifth either way. Thirteen items, one of which is the v0.4.5 cut itself. |
| v0.4.7 | Completed | **Three claims the model made without defending, and the first stored parameter to leave the Gas Man set.** Each of the three had been asserted in prose and enforced by nothing, and each turned out to be wrong or unenforced in a way only the enforcement could show. **The run length was a memory limit wearing a modelling limit's clothes.** A 30-day cap was set on 2026-08-25 to size a concentration history that no longer exists, was carried forward as though it described the model, and was enforced nowhere at all: nothing in `core/` or `app/` bounded elapsed simulated time, so a run could reach day 45 of a 30-day cap and go on displaying two-decimal concentrations. It is now **24 hours**, and the number moved *down* by more than an order of magnitude because the question changed: the item proposed the fat group's ~42 h time constant as a scale to take multiples of, which inverts the relationship - many multiples of the slowest mode is precisely the regime `docs/MODEL.md` § "Published wash-in and elimination validation test" already refuses to validate over, having rejected the Yasuda papers' own multi-day elimination curves because over days the missing metabolism is no longer negligible and neither is the fat group's flow. What binds a run length is what the model omits, so the fat time constant is a floor and not a multiplier. Sevoflurane is the binding agent at 2% to 5% of the absorbed dose, beginning within minutes rather than late (Kharasch 1995, marked tier 2 in both the code and the specification, because 24 hours is a declared envelope argued against the omission and not a figure computed from a metabolic rate). Enforcement is an integer step-count comparison derived once per step size, so the boundary falls at the same step on every machine and deterministic replay holds across it; the interval is closed like the four flow ranges, a run completing exactly 864 000 steps of 0.1 s to land on 86 400.0 s before the next is refused. And reaching it is **not a failure**: `SimulationDomainLimitError` subclasses the execution branch so a caller that knows only the base classes still stops the run, while `app/` reads the specific type to say "Stopped - supported run length reached" in place of a failure banner describing a rollback that did not happen. Telling a learner the simulator broke when it stopped exactly where the specification says it must spends the one signal the interface has for a real fault. **The control-resolution tolerance was three published numbers no test computed.** § "Supported simulation step" publishes the displacements the step bound *is* since `PL-X9KD` retired its accuracy derivation, and `grep` for them across the suite returned one unrelated comment: a change to an equation, a partition coefficient, the reference adult's volumes or the supported envelope would have moved them silently while both documents kept asserting the old figures. `tests/reference/test_control_resolution.py` now drives each manoeuvre twice from an empty system in lockstep, differing only in when the control change lands, and every published figure reproduced - 6.66e-3, 5.03e-2 and 1.43e-1 pp at 1x, and 1.43e-1, 6.95e-1, 2.51, 5.83 and 1.04e1 pp down the per-rate column - with the gate mutation-checked rather than assumed, a 0.2 s step, a 2 L/min wider ventilation envelope, an 0.42 to 0.50 desflurane blood:gas and a 2.5 to 2.8 L alveolar volume each failing it. **It found a defect on its first run**: the specification read "the case opening is two orders milder at every rate" where it is 21x milder at 1x and 6.9x at 300x, the binding manoeuvre's displacement saturating while the case opening's stays nearly linear in the delay, so a reader budgeting an ordinary dial change at 60x would have inferred about 0.06 pp against a true 0.375 pp. **The six chart traces were separable only to normal vision.** Contrast composes along a bounded axis, so no palette of six clears 3:1 pairwise and the fix could never have been a re-pick; the traces now carry line style as a second channel, and `tools/contrast_check.py` gained the Brettel 1997 projection with a hard floor holding every trace to 3:1 against the panel in four vision models. That floor immediately found what no normal-vision check could see - `MUSCLE_COLOR` at 3.19:1 as displayed and **2.98:1** simulated for deuteranopia - and corrected the specification's own dichromacy claim about the ISO 5360 agent colours from "1.1-1.4" to a measured 1.06 to 1.48. **And the venous pool got a source, which it had never had.** `venous_blood_volume_l` = 1.0 L entered at v0.1.0 under a Workbook citation belonging to its neighbours; the Workbook's Blood row reads 5.00 L and no 1.0 L figure appears in it anywhere. Davis and Mapleson 1981 states, for models of inhaled anaesthetics specifically, that the two venous pools may be combined into one of **1222 ml**, 23.6% of their standard man's 5189 ml blood volume - the same object as this model's single well-stirred venous pool - and that value is adopted on the project owner's decision, the first parameter in `reference_adult.json` to carry a source other than Gas Man. It is tier 2 and stays unadopted-as-measurement: the Appendix derives the pool from ICRP (1975) blood distribution to reproduce circulation times rather than measuring it. The competing hypothesis was tested and failed - `PL-8ZJQ` had suspected 1.0 L was an arterial compartment under a venous name, on Lerou and Booij's arterial fraction of 0.2, and Davis and Mapleson's own arterial pool for an inhaled-anaesthetic model is 799 ml at 15.4%, so the coincidence does not survive the primary source. The key is renamed `venous_pool_volume_l` in the same change, because it names a mixing volume and read as the physiologic venous blood volume. **This is the first release since v0.4.4 in which a displayed number moves, and the only one in which a stored parameter does.** The mixed-venous time constant V_v/Q goes from 12.0 s to 14.7 s at the stored 5.0 L/min, visible on the mixed-venous trace through the first minute of every simulation; the 30-minute F_A/F_I wash-in distances are unchanged to two decimal places, the pool being long equilibrated by then, and the 5-minute F_A/F_A0 elimination ratios move 0.11 to 0.13 published SD *further* from their cohort means - the same direction the module already attributes to this model's rebreathing circuit rather than to tissue return. No equation, numerical method or solver step moved. Three apparatus items close beside them: `bin/docket record` had written pull-request numbers a shallow clone could not verify, `bin/docket trend` makes the workflow-to-product balance a command rather than a session's derivation, and thirty-one captures from one day were triaged into the queue. Ten items, one of which is the v0.4.6 cut itself. |
| v0.4.8 | Completed | **The gate that was measuring itself, and the run that became its own score.** No displayed value moves: the only change in `core/uptake_system.py` makes two private readers public, and the new `core/run_definition.py` is not yet on the path the chart draws from - `PL-2FM6` moves it there. **The reference gate had been reporting its own oracle's error.** `tests/reference/test_coupled_dynamics.py` measured the shipped exact step against an RK4 oracle whose step was never converged during a transient, so 86 to 99.8 percent of every residual it printed was the oracle's own truncation rather than anything about the shipped code - a verification instrument reading itself, and passing while it did. The oracle step is now pinned at `ORACLE_STEP_S = 0.0125` under a lockstep test that fails if it drifts, and the agreement it can now assert is `EXACT_STEP_ORACLE_TOLERANCE = 4e-13` (`PL-B1WW`). Beside it, v0.4.7's venous pool change had moved every measured residual in that same file while none of its documented tables were re-derived, so the file's prose described a tree one release out of date; the tables are recomputed and the stale nine-to-sixty-seven-fold claim is gone (`PL-D3XX`). **A run is now describable as the settings it was computed under, rather than as samples of itself.** The governing equations are linear and time-invariant while a setting is held, so `matrix_exponential` solves each such stretch exactly over any horizon and `core/run_definition.py` can hold a run as its control-input timeline: memory stops growing with the run - about 70 KiB of score against the 3.16 GB of samples the same 30-day case at fifty changes a day records today - and a window costs what it draws rather than what preceded it (`PL-T691`). **The rule that carries determinism once the step is no longer fixed is enforced rather than described.** A fixed 0.1 s step made one instant's answer unique by leaving every caller the same width to take, and a propagator exact over any horizon takes that away. So `docs/MODEL.md` § "The canonical evaluation rule" separates the canonical path - one propagation per stretch, composed in recording order, bit-identical on re-evaluation rather than equal within a tolerance - from the display path that reuses one propagator across a window's columns; and the program refuses to confuse them, the display path returning `DisplayState`, which is structurally not a state vector and deliberately not a subclass of one, so a drawn value cannot become a keyframe, an exported figure or a branch's opening state by having the right shape (`PL-P1Z3`). **Two claims the model made about itself are corrected.** The fixed alveolar volume *blocks* nitrous oxide rather than merely omitting it, which is a modelling boundary and not an unimplemented feature (`PL-L2F2`); and the case-opening displacement called "two orders milder at every rate" was 0.8 to 1.3 orders by the figures in its own sentence, which told a reader sizing the ordinary manoeuvre against the binding one the wrong ratio (`PL-SR8F`). A third had gone stale rather than wrong: the step-atomicity section still named a class renamed four releases earlier (`PL-0GTC`). Two presentation-safety items land with them: the planned v0.5.0 branch comparison puts the run on line width so the compartment keeps line style rather than colour alone (`PL-HLD5`), and the trace-against-trace 3:1 bar was checked against SC 1.4.11 at the source, where both carve-outs that would have relaxed it turn out to be conditioned on an absence of overlap this chart does not have - six traces that start together, converge and cross, which is the lesson rather than an accident - making the bar a supported exceedance rather than either a requirement or an arbitrary strictness (`PL-JX0Z`). Eight apparatus items close beside them, the load-bearing one being the capture rule's own exemption: `CLAUDE.md` had exempted a finding fixed in the same session without giving any session a way to enter that exemption, so every one-line fix became a queue item (`PL-3MJH`). |
| v0.4.9 | Completed | **The release where the checks were found to be checking less than they claimed.** No displayed value moves: no equation, parameter, unit, numerical method or solver step changed, and the agent and patient files gained provenance metadata - `schema_version` 2, a `tier` and `adopted` flag per source, and a `provenance_gap` naming what is unadopted - without one stored number moving. **What moved is how much of the apparatus was actually checking.** `main`'s quality run had failed on three consecutive merges with nothing surfacing it, because the whole-store `verify:` replay runs only on push to `main` (`PL-0ZGK`). The reference oracle's independence check walked only `ast.ImportFrom`, so a plain `import` went past the guard that makes that module evidence rather than a tautology (`PL-F5GN`). `require_valid_agent_accounting()` read nothing from the object it judged, so it would have accepted a result from another accounting period (`PL-X204`). Two tests `docs/MODEL.md` requires were documented and never implemented (`PL-GZP6`). The citation check quoted section titles as `[^"\n]+`, so any title long enough to wrap was unexamined rather than reported (`PL-X94L`), and it read neither the queue nor a single source docstring, which is where this project writes most of its citations (`PL-X2XX`); the two stale ones that found are fixed (`PL-8B1K`). A `verify:` command could re-enter `docket check` without bound (`PL-20CQ`), and a count labelled "open" excluded the untriaged items, understating the queue by exactly the number printed beside it (`PL-4WQS`). Source tier became machine-readable rather than prose (`PL-1JDD`), which immediately exposed a tier-2 source standing as the authority for `venous_pool_volume_l` and now says what it owes (`PL-FJGY`). v0.4.8's own tag had been pushed onto a commit where no release was cut (`PL-BKDP`). |
| v0.4.10 | Completed | **The release where the apparatus stopped being implicit.** No stored value moves: `src/anesthesia_sim/data/` changes only in what its entries say about their own numbers, and `core/` only in `circuit.py`'s docstrings. What moved is that the machine around the model - what a flow number counts, at what altitude, on which class of vaporizer, through which breathing circuit, and out of which book each parameter came - is now stated where a reader meets it. **Fresh gas flow was never the flowmeter setting.** The model reads it as flow at the common gas outlet, carrier gas plus the vapour the vaporizer added, and the two differ by `1/(1 - F_D)` - 22% at desflurane's 18% dial maximum. `docs/MODEL.md` and `BreathingCircuit` now say so (`PL-CXYT`), and so does the one place a user actually reads: the control carries "common gas outlet" as a smaller second line under its label, in the idiom the metric panels already use for "Alveolar / end-tidal-equivalent" (`PL-71CF`). The user-visible consequence is the circuit time constant `V_C/V_F`, which is what the wash-in curve is about. **The model is at sea level, and the delivered-concentration dial is a class of vaporizer rather than a universal control** (`PL-5K5C`) - both recorded rather than assumed. **The elimination comparison was measuring a breathing circuit, and now says how much.** `tests/reference/test_published_wash_in_and_elimination.py` gained a test-only open-circuit driver that discards the circuit after every step of the washout and records the agent as exhausted, which is the condition Yasuda's expirate collection ran at and one no setting of this simulator reaches; the apparatus is worth **3.5 to 4.2 published SD** per cohort, and with it removed sevoflurane and both isoflurane cohorts land inside the published spread that the shipped condition missed by +3.8 to +5.1 SD (`PL-W21J`). Desflurane crosses to 2.33 SD on the *other* side, and `PL-73G7` records that as a disagreement no parameter closes rather than one to tune away. **Agent identity had been reaching the screen in Material's disabled grey** - fixed on the running-agent control (`PL-61WW`), with the general rule for every identity-carrying control decided and left as one check to build (`PL-97VB`). **Lowe and Ernst 1981 was read at the source**, by interlibrary loan: page 56 says the figure's volumes and flows are collected and cited onward, so the book is tier 2, nothing is promoted or adopted, and of the seven values the Gas Man Workbook credits to it three reproduce and four do not (`PL-7HDS`). **And the resident provenance rule was contradicting the shipped parameter set.** "A reference implementation is never the authority for a constant" loads in every session, while twelve partition coefficients and ten of the reference patient's eleven parameters are adopted from one on a recorded decision; the letter now says what the spirit always did, which is never a *silent* authority (`PL-X19T`, `PL-J302`). `PL-KTKP` closes beside them: the v0.5.0 debt gate had under-reported by eleven safety- and science-classed entries for two days, and those eleven were the whole of its `P1` band. Twelve items, one of which is the v0.4.9 cut itself. |
| v0.4.11 | Completed | **The release where the interface's cost was measured rather than guessed.** No equation, parameter, numerical method or solver step moves: `src/anesthesia_sim/core/` is byte-identical to v0.4.10, and `src/anesthesia_sim/data/` changes only in what two provenance entries say about their own numbers - one of them recording that the stored 5.0 L/min cardiac output is *kept* against Lowe and Ernst's allometric 4.84, because this file stores compartment volumes as fixed litres and scaling only the flow would make every time constant proportional to M^(-3/4), an artifact of scaling one half of a coupled pair (`PL-YKSM`). **The project owner reported the interface as laggy at speed, and the first finding was that it is not the simulation.** The model is 42 us a step, enough to sustain about 2 400x real time, and at 300x it occupies 12% of a tick; `page.update()` cost 20-52 ms of a 200 ms frame, 98% of it Flet's Python-side control-tree walk against 2% for the msgpack encode, on a patch of 3-5 KiB. **The cost is the walk rather than the changes it finds**: an update on a chart where nothing had changed since the last one costs what a full frame costs, both linear in the number of point controls at about 24.5 us each, with 64% of a frame in `object_patch._compare_dataclasses` (`PL-YSZN`). **Half of it was a tooltip nothing ever wrote text into.** Every `LineChartDataPoint` carries a default `LineChartDataPointTooltip` holding a full seventeen-field `TextStyle`, and Flet's diff descends into both on every point on every frame. The hover is now offered while the run is paused and withdrawn while it plays - which costs nothing, because `_run_render_timer` takes no frame while the run is stopped, and a value read under a cursor on a trace advancing a simulated minute per frame was never readable anyway (`PL-KP7H`). **And a dragged slider was drawing a whole frame per pointer move**, 59.1 ms each, so a drag emitting thirty a second asked for 1.8 s of event-loop time per second and the readouts arrived *later* than a tick rather than sooner; the frame is coalesced onto the render tick, leaving 3.4 ms, with a refusal and the frame that clears one still drawn immediately because those are the only states where a dial and the simulation disagree (`PL-R2YM`). Together: delivered playback rises from 73-91% of the rate the dropdown claims to 84-94%, and input-delay p90 roughly halves. **`PL-YDKJ` is decided rather than deferred**, both escape routes having been measured: a server-rendered chart is 44.4 ms a frame in the mode this chart is in, and a sweep display buys this path nothing because the walk is indifferent to what moved - O(1) in operations sent, which was `PL-Q197`'s bottleneck, and O(n) in the walk, which is today's. The accepted ceiling is written at `CHART_COLUMN_BUDGET_PER_SERIES`, where a session sizing the chart will be holding it. **What none of that reaches is a floor**: an idle page of about a hundred controls still costs 10.3 ms, five times a second, to discover that nothing moved - so `PL-QXSB` asks whether the interface should stay on Flet at all and is admitted to v0.5.0's gate, because that milestone's defining feature is a second chart. PySide6 with pyqtgraph measures 0.51 ms for the same frame and barely scales - 380 times the points costs four times the frame - while PyQt is ruled out by licensing rather than preference, this project being Apache-2.0 against PyQt6's GPLv3-or-commercial. **The interface also says less, and says who it is for.** The concentration chart's explanatory prose is cut to legend and labels (`PL-6580`), the reader it is written for is named in a rule every session editing `app/` loads (`PL-B89V`), and the running build is on screen so a fix verified by eye can be attributed to the build that drew it (`PL-YKF8`). **Beside them, the apparatus caught its own checks reporting more than they checked.** `bin/docket verify`'s item-front-matter guard compared `git show <base>:<bare filename>`, so the lookup always failed, the miss was swallowed as a new item file, and the check reported PASS on every branch including one that marked its own item done (`PL-20PT`); forty-two open items carried neither a gate placement nor a recorded deferral, which is the one disposition the presence rule forbids (`PL-36R4`), and the check that closes that hole immediately turned `main` red on the first item to arrive after it, because that item had merged on a base whose CI predated the check (`PL-33WM`). Twenty-one items, one of which is the v0.4.10 cut itself, completing the `delegation` feature. |
| v0.4.12 | Completed | **The release where a run stopped being a record of itself.** The chart drew by summarising a store of recorded samples; it now evaluates the run's score at the instants it plots, and the store is gone with the summariser. `RunHistory`, `HistoryWindow`, `SimulationHistorySample` and the M4 decimation module are deleted - 671 lines of a careful implementation, removed because the architecture deleted the problem it solved rather than because it was wrong - along with the Jugel et al. 2014 paper it was founded on and every citation of both. Net 860 lines out. **The change was made for a safety reason rather than for tidiness.** `PL-4RBD` was banded a `P2` fidelity defect on a 0.04 percentage-point error measured at a chart window the interface had not had for four releases; re-measured against the shipped time bases, the alveolar trace departed from the run by 0.65 pp at a 12-hour base - 0.32 MAC of sevoflurane - drawn with nothing to say the shape between plotted points was inferred. It is `P1` `safety`, and the fix is structural: a control event now gets its own column, read from the keyframe the score already holds, so it is exact rather than placed. **What that did and did not buy is measured and recorded.** The kink at a dial change is gone. The curvature is not: columns sit at the spacing the time base implies and the chart rules a straight line between them, so the worst departure fell to 0.53 pp, 0.26 MAC, and moved to the steep early wash-in where a learner watching an induction is looking. `PL-GS3R` carries that measurement, the three routes out of it, and the decision the project owner owes. Beside the simulator work, the branch-id rule stops failing the owner's own web edits and any contributor's pull request, and `CONTRIBUTING.md` exists now the repository is public. No equation, parameter, numerical method or solver step moves. |
| v0.4.13 | Completed | **The release where the reference patient's provenance chain was followed to its end, and found to contain no measurement.** No displayed value moves and no stored value moves: no equation, parameter, unit, numerical method, solver step or interface element changed, and `src/anesthesia_sim/core/` is byte-identical to v0.4.12. `src/anesthesia_sim/data/` changes only in what its entries say about their own numbers. **What moved is how much of that provenance is known.** The Gas Man Workbook names Lowe and Ernst 1981 for seven of the reference patient's eleven values; that book cites four references on page 56 for its own figure 4.1b, and over one afternoon the project owner supplied all four by interlibrary loan and direct download. They are two documents one link apart: ICRP Committee II's 'standard man' table at page 151, which Mapleson 1963 also cites for his volumes, and which gives organ masses and **no blood flows at all**; and Mapleson himself, who compiles his flows from about twenty sources - some of them animal, one row an `Estimate`, and one 'chosen merely to complete cardiac output', which is 19.9% of his total. Lowe and Ernst's other two references are Mapleson's table lumped and relabelled, reproducing it in nine rows of nine. **The chain reaches tier 1 nowhere, and figure 4.1b's flow column reproduces from none of the four**: on Mapleson's own rows the vessel-rich share is 59.0-63.0% against Lowe's 76%. `reference_adult.json` gains five `sources` entries and its `provenance_gap` is rewritten to say that, stated as what was checked rather than as what exists - **it does not follow that no origin exists**, and the field says so. **Two other decisions are recorded rather than built.** The PySide6 spike was run on the project owner's own hardware and the interface will leave Flet, scoped as v0.5.1 and not started here. And `docs/MODEL.md`'s cardiac-output limitation stops setting Lowe's derived 4.84 L/min beside Cattermole's measured 5.51 L/min as though they were evidence of the same kind. `doc-consistency-checks` is complete, and `tools/doc_check.py` can now express a one-entry gate group without silently attributing it to the group above. | 11 items |
| v0.4.14 | Completed | **The release where the project's own checks stopped refusing correct work.** Nothing computational moved, and this one can say so more strongly than the last: `git rev-parse v0.4.13:src HEAD:src` resolves to the same tree object at both ends, so the whole of `src/` is byte-identical - `core/`, `app/` and `data/` alike - where v0.4.13 could claim only `core/`. `docs/MODEL.md` is byte-identical and `.github/` untouched, so no equation, parameter, unit, numerical method, solver step, displayed value or CI gate moved; the three changed files under `tests/` exercise `tools/` and none imports `anesthesia_sim`. **Fifteen of the seventeen items are one defect wearing different clothes:** a piece of the apparatus produced a signal a session could act on, and the signal was false. **Five are `bin/docket verify` refusing exactly what the instructions mandate** - a branch carrying a capture (`PL-66PR`), a close-out letting `docket record` ride its commit (`PL-ZYQC`), an item whose declared work *is* editing `.claude` (`PL-69JZ`), the front matter that closing an item necessarily edits (`PL-B5YN`), and a batch branch audited as one item (`PL-4LT9`) - all five the same inability to tell a delegated worker from a session reviewing its own branch. **The repair is deliberately partial and the gap is recorded rather than implied:** two shapes are exempt unconditionally, the other three only under the new opt-in `verify --self`, and nothing on the documented close-out path names that mode yet - `PL-7XTS` was filed in this range to say so. `PL-4LT9` is *reported rather than repaired* by explicit decision; `item_commits` still matches every subject, so the new check never blocks. **Two are the stop hook demanding a push for work already pushed**, from unrelated causes: `--depth 1` implies `--single-branch`, so `git push` never creates the ref the hook reads (`PL-3SGR`), and the merged-PR recovery's `checkout -B` repoints the upstream (`PL-483K`) - whose dangerous variant is that the same missing ref makes `--force-with-lease` refuse with `stale info` and invites a bare `--force` mid-rebase. What shipped widens `remote.origin.fetch` at session start and deliberately never fetches and never prunes. **Three named a wrong cause with complete confidence**, which is worse than failing: eleven missing-row errors pointing a session at the safety-critical provenance table when the fault was a decoy table 300 lines above (`PL-ZBZZ`), a checker erroring on an elaborated `**Decision needed**` heading its own README permits (`PL-VJ1X`), and stale `.pyc` bytecode producing a `make check` failure unreachable from the source in front of the reader (`PL-01GD`). **Three reported nothing or the wrong number:** one unparseable glob token aborting the whole documentation gate on a traceback (`PL-0M7L`), `docket next` understating the queue by exactly the untriaged pile (`PL-ZWBK`), and `docket check` advising every run that a `P1` `safety` item was ready to promote when it must ship behind an unshipped port (`PL-L09X`). `PL-KY7M` removes ten deprecation lines per run; `PL-BBDD` is the same class at opposite polarity, an uncovered `ruff.toml` letting a delegated diff relax the linter and still report ACCEPT. **They were found by running the tools rather than reading them:** `PL-3B47`'s pass over the 46 untriaged captures closed 23 ids, eight of them dropped as duplicates, already fixed, or overtaken by the Qt port. **Seventeen items, one of which is the v0.4.13 cut itself.** Two debts leave with it rather than inside it: `PL-01GD` shipped with no test at all (`PL-H9GV`), and the same triage pass wrote into this document a sentence calling every drawn chart point an M4 representative of roughly 120 recorded samples - a path `PL-2FM6` deleted in v0.4.12 (`PL-DZFJ`). |
| v0.4.15 | Completed | **The release where the project's own checks stopped reaching past what they could decide.** Nothing a learner can observe moved: `src/anesthesia_sim/core/` and `app/` resolve to the same tree objects as at `v0.4.14`, `.github/` is untouched, and the whole of `src/` changes in one string - the `note` on `reference_adult.json`'s Frayn and Karpe entry, which said a review "cannot be the authority for a stored value" where `docs/MODEL.md`'s own source hierarchy admits a tier-2 source on a recorded decision and the entry needed instead to say that no such decision has been taken for this parameter (`PL-S3Q0`). **Ten of the thirty-three entries are one defect in ten places: a check answering a question it could not decide, confidently, and charging a session for the difference.** Four are in the documentation and queue checkers - the top-band advisory prescribing a demotion `docket check` itself rejects as an error, on a band where twelve of thirteen items are class-pinned and one is demotable (`PL-CW14`); and `doc_check` reading a shell regex in an item's `verify:` front matter as LaTeX (`PL-WTQ1`), reading any double-quoted phrase as a section citation, so quoting a measured figure hard-fails (`PL-KJ63`), and attributing a candidate line to the alphabetically first matching term rather than the most specific (`PL-Z0G0`). Six are the `vcs.py` ref-lifecycle cluster, closed as one root-cause round: shipped items reported in flight in every digest because their refs outlived their merges (`PL-6BDX`), a triage skip-mark still firing after the branch it named had merged, which told one pass to skip four of its five items (`PL-8MJ3`), and four ways of calling a branch merged, stranded or left-behind by comparing content that a squash or a history rewrite leaves unchanged (`PL-JBRC`, `PL-XLQ5`, `PL-Y31G`, `PL-YDL6`). **Two sit either side of that line.** `PL-JSRH` closes a gap rather than a false positive - nothing stopped a branch rewriting a closed item's `closed:` or `milestone:`, which are records - and `PL-R6D8` is the same error in prose, a docstring claiming `git log --source` attributes a shared commit to the ref named first, which it does not. **`PL-W1LN` is the judgment running the other way:** the in-flight walk guard cannot catch a false positive whose walk ends against a commit the base reaches by another path, and the limit was reproduced, accepted and pinned rather than papered over. **`PL-3833` adds the one check that was missing** - an item filename drifted from its title - as an *advisory*, because the remedy needs judgment the tool does not have. **The cluster carried a pre-registered test and rejected its null** (`PL-CSHL`): against the cluster's own spawn rate of 1.05, nine closures predicted 9.5 new items and produced 3, rejecting H0 one-sided at 5% - recorded with the threat to the inference in the same breath, that one session closing nine items has fewer opportunities to file than nine sessions closing one, which this design cannot separate from a root-cause effect. **Nine entries are the documentation stating something untrue**, two safety- and three science-classed: `docs/MODEL.md` still saying all eleven reference-patient parameters are the Gas Man default patient (`PL-7KDC`), naming two mass-balance tolerance constants that do not exist in the code (`PL-L7JB`, `PL-MS54`), omitting lung tissue and pulmonary blood from its known limitations - worth about twenty percent of every agent's fast pool (`PL-Q5NS`) - and this file calling every drawn chart point an M4 representative of a bucket `PL-2FM6` deleted in v0.4.12 (`PL-DZFJ`), and not saying that cardiac-output scaling is planned-milestone item 30's obligation or that weight scaling is only safe as a coupled package (`PL-MMWX`). **Gate 1 passed half inside this range.** `PL-27S8` writes the rule that governs the next proposal to tighten anything - name what the suppressed side would have to be worth for the proposal to be wrong, then go and count it - and `PL-MGF9` is the first thing it would have caught, dropped rather than built because the advisory it specified could not fire and `bin/docket trend` had taken its job five days after it was captured. |
| v0.4.16 | Completed | **The release where one quantity stopped being stated two ways.** All thirteen entries are the same shape: two statements of one fact, drifted apart or free to drift. **Nothing computational moved** - `src/anesthesia_sim/data/` and `.github/` are byte-identical to `v0.4.15`, and `src/anesthesia_sim/core/` changes in docstrings, one moved constant and one rename, so no equation, parameter, unit, numerical method or solver step is touched. **What a reader sees is the clock.** `PL-SSBP` gave the chart a time base spanning a case, so an axis tick read `1h30m` while the clock and every recorded control stamp beside it read `5400.0 s`, and locating a control mark meant dividing by 3600 by hand; `PL-Y5WR`'s 24-hour envelope then made the clock's top reading `86400.0 s`, seven characters of tenths on a quantity a reader thinks about in hours. The clock, the stamps and the axis now share one compound form - `45s`, `1m30s`, `1h23m45.6s`, `24h` - built in one function, dropping a zero component and keeping a tenth only where there is one, so a stamp still resolves the `0.1 s` step the simulation advances by (`PL-Q4M4`, `PL-CZFY`). The old docstring's argument for two forms, that "a compound duration form would round the stamp away", was checkable and false; `format_elapsed` now also raises rather than printing `-1.0 s`. **Two error boundaries were false where they were stated:** `core/parameters.py` promised in its own docstring that every raise reaching a caller is a `SimulationConfigurationError` while a missing, unreadable or truncated data file escaped as `OSError`, `UnicodeDecodeError` or `JSONDecodeError` - three types where the audit named two, because the file is opened as text (`PL-B32L`) - and `_apply_setting` caught a narrower class than the timer paths beside it, so an unexpected raise escaped into Flet's dispatch (`PL-YK2V`). `FLOW_FRACTION_TOLERANCE` stood at `1e-12` in two modules guarding the two perfusion-sum checks independently; one definition now, identical value, so no threshold moved (`PL-TCW5`). **The provenance line stopped answering when it could not:** `APP_VERSION` falls back to `unknown`, which is a version-shaped string, and the header subtitle is the interface's only link between a displayed number and the model behind it, so a build that cannot identify itself now says "Version unavailable (this build is not traceable)" (`PL-KCWD`). **Three names had outlived what they name** - `RunScore` is `RunDefinition`, in the package that should read like the domain (`PL-ZX12`); the wash-in validation module and its `docs/MODEL.md` section cover elimination too (`PL-B9VL`); and `docs/MODEL.md` named sevoflurane in its headings, Purpose and symbol table four releases after three agents shipped (`PL-KGNF`). **And the citation tying `core/` to the specification is enforced rather than asserted.** `PL-VZL0` cites `docs/MODEL.md` from every `core/` function implementing a governing equation, precisely so a section rename cannot silently orphan it - and `tools/doc_check.py` read the comma form and not the section-mark form this repository writes, leaving 285 of the tree's 324 document-section citations unchecked while the run reported that they all resolve. Recognising the form surfaced eighteen errors: eleven were one false positive, a citation wrapped across two lines of a blockquote, and seven were genuinely stale pointers in closed items (`PL-V13T`). Five gate entries deferred to the Qt port by owner decision are `blocked` rather than counted as debt the gate could clear (`PL-D143`). Thirteen items, one of which is the v0.4.15 cut itself. |
| v0.4.17 | Completed | **The release where `core/` said what it meant.** Four Gate 1 `needs-decision` entries, all of them about the core's own vocabulary rather than its arithmetic, and **no number the model produces moves**: `src/anesthesia_sim/data/` and `.github/` are byte-identical to `v0.4.16`, and every reference test carrying a pinned published or canonical value - `test_canonical_evaluation.py`, `test_coupled_dynamics.py`, `test_published_wash_in_and_elimination.py`, `test_circuit_wash_in.py`, `test_multi_agent.py`, `test_control_resolution.py` - is byte-identical too and still passes. Every executable line that changed is a type annotation erased at runtime, or a hand-written `* 100.0` replaced by an identically-defined named conversion, or the deletion of a method with no caller. **Three of the four decisions were settled by a measurement that changed the answer the brief expected.** `PL-74R0` asked which of five public `advance` methods should survive the exact step that replaced the operator split: one 60 s step against six hundred 0.1 s steps put the circuit, tissue and venous closed forms within 1.1e-14 of themselves and `PatientCompartments.advance` **25% apart**, which is not a closed form at all but the first-order split `PL-GS5X` deleted, kept alive as a public method with no error bound and a docstring giving a reader nothing to suspect. It is gone; the three exact ones stay, documented, and the criterion deciding them was already written in `alveolar.py` - nothing outside the governing equations may move agent between two modelled compartments. `PL-79YX` asked whether six `== 0.0` guards deserved any words: they turned out to be **three different arguments**, two of them load-bearing rather than stylistic - `V/0.0` raises in Python, and the circuit's exhausted-agent integral is `inf * 0.0` and therefore `nan` at zero flow for every state - while the item's own 2026-09-02 walk had been run at a loaded fraction where the third argument is invisible, so deleting either `advance` guard had been leaving the whole suite green. `PL-WVSK` asked whether a concentration fraction and a percent should differ at the type level, against a brief naming two implicit conversions: there were **twelve**, across six modules, six of them on the path to a displayed clinical value, and `docs/MODEL.md` had been asserting that "the interface alone converts" since the agent files began carrying a MAC. `core/concentration.py` now owns the factor and both directions, with `Fraction` and `Percent` as `NewType`s whose limits are documented rather than implied - erased at runtime, useless against a wrong magnitude, and unable to reach inside the equations at all, since `Fraction(0.5) * 2.0` is a plain `float`. **The fourth was the project owner's and a session took it.** `PL-8GV5` asked whether `ROADMAP.md` should carry intent for a dose-dependent haemodynamic response; the session measured the human volunteer literature - cardiac index unchanged under desflurane alone, falling dose-dependently in the same volunteers with nitrous oxide, and falling then returning to baseline at 2.0 MAC under sevoflurane - and then closed the item on that measurement. Whether a feature enters the roadmap is direction, not fact. The owner's answer was different and better: not now, and kept as **planned item 35, an option a user turns on**, because an overlay can state the uncertainty those three studies describe where a default behaviour cannot. `PL-4T90` is the routing gap fixed in the same session - the `docket` skill now sorts a `needs-decision` item by what its answer rests on rather than by how hard it looks. Eleven items, one of which is the v0.4.16 cut itself, and one of which - `PL-1YDK` - was a duplicate of `PL-8PT6` that had turned `main` red by passing its own `verify:` command. |
| v0.4.18 | Completed | **The release where the project checked what it tells the next session.** Twelve of the seventeen entries are a statement this repository makes — to a session or to a reader — that was wrong, missing, or unreachable: the gate's own counts and deferrals (`PL-SL70`, `PL-9S30`), a recommendation that never said how the item it named related to the gate (`PL-J790`), `docs/MODEL.md`'s symbol map (`PL-H46J`, `PL-212V`) and a margin its prose called comfortable at three percent (`PL-WT07`), the architecture pointer no session was shown (`PL-39K7`), the apparatus test bar that was never written down (`PL-N6Y0`), a v0.4.0 Goal still in the present tense about problems since fixed (`PL-DXQC`), and the README's scope word (`PL-XF89`). Two go further and measure reception instead of correcting prose: `PL-VV16` instruments which item files sessions actually open, and `PL-NB35` gives failed approaches a bounded startup tier so they are not rediscovered. **Nothing a learner can observe was recomputed**, and this release says so with a measurement rather than a byte comparison: `src/anesthesia_sim/data/` and `.github/` are byte-identical to `v0.4.17`, and `core/` holds exactly the same 401 numeric literals before and after, so `PL-9SH6`'s accessor rename across every compartment moved not one number. The reference suite is *not* byte-identical this time, because that rename reaches it — what is measured instead is that no numeric literal was removed from it, so every pinned published and canonical value still stands. `PL-V6M0` is the one safety entry: `_apply_setting` caught the exception hierarchy's base class, so a `SimulationExecutionError` would have been reported as a refused setting over a run that kept producing readings. Seventeen items. |
| v0.4.19 | Completed | **The release where three questions were answered and `core/` did not change a line.** The second half of that is a tree-object identity rather than a reading of the diff: `src/anesthesia_sim/core/` resolves to `7a49512` at both `v0.4.18` and this release, and `src/anesthesia_sim/data/` to `d5a26cf`, so every equation, constant, numerical method, unit and stored parameter is byte-identical and not one number the model produces was recomputed; `tests/reference/` gained 251 lines and lost none, so every pinned published and canonical value still stands. All three `P1` entries settle a question instead of adding behavior. `PL-1XPX` decides what the readouts show while two branches are displayed — both runs, paired per compartment, each naming its run in text — and refuses a difference readout on a domain ground rather than a layout one, because the arithmetic difference of two alveolar fractions is not a quantity with a conventional clinical reading; the readout cap that was recommended and approved is recorded as refused by `docs/MODEL.md` § "Minimum displayed outputs", which already forbids a required value leaving the display with the curve that draws it. `PL-RFLN` removes a candidate for desflurane's five-minute washout residual: the published apparatus's dead space is an alveolar-ventilation decrement rather than an inspired fraction, and at the published magnitude it closes only a quarter to two fifths of the 2.33 published SD while pushing an isoflurane cohort that was inside its spread out of it — the common-mode failure every earlier candidate died of, now pinned by two mutation-checked reference tests, with the parameter file again unchanged. `PL-XJ5P` closes the hole under `.claude/rules/citing-sources.md`'s promise that "there is a route": a private reference corpus is adopted as the terminal route, verified end to end from a session before the rule was written, and what a *miss* means is written down — record the gap and put the reading to the owner, rather than narrowing the claim or taking a search summary for a reading. Three interface entries apply the same standard from the reader's side: the readout row names the substance its numbers belong to (`PL-TCD1`), the new-case dialog's carry-over sentence names only settings the reader can actually set (`PL-0Q1T`), and the wash-in panel's 786 characters of standing prose are gone (`PL-F9TQ`). Two more turn a convention into something that runs: `PL-FZ6T` holds `core/` to `docs/MODEL.md` in code — every Symbols Code cell must resolve to a real attribute, the retired accessor names may not reappear, and a partition-coefficient identifier must name both phases outward from the gas phase — and `PL-RC0M` replays a blocked item's `verify:` command so it cannot rot unnoticed and redden whichever pull request unblocks it. `PL-B667` states the upper bound `core/` has always enforced in five places. Ten items. |
| v0.4.20 | Completed | **The release where four stored values' sources were read back against the publications, and not one number moved.** The second half is measured rather than asserted: every numeric value in every data file that existed at `v0.4.19` is identical at this release - all twelve partition coefficients, the eleven reference-patient parameters, every MAC and MAC-awake - and `src/anesthesia_sim/app/` and `.github/` resolve to the same tree objects. `src/anesthesia_sim/core/` is *not* byte-identical, and this release cannot make v0.4.19's claim: `PL-4YY1` moved `circuit_volume_l = 6.0` and `default_fresh_gas_flow_l_min = 4.0` out of `core/circuit.py`'s dataclass field defaults into a new `data/machines/reference_circle_system.json` - machine parameters as their own kind, beside patients and agents - changing neither value, and `AgentUptakeSystem.for_agent()` now passes both explicitly so that every scientific constant a run uses comes from a cited file. **They had been invisible to the only tool built to catch exactly this:** `tools/doc_check.py`'s `check_provenance` walks *data files* in both directions, so a constant that never entered one could not be missing from anything. The new file records that the Workbook's published circuit volume is 8.0 L against this project's 6.0, kept on the project owner's ruling of 2026-09-01 that the value is not critical, and what the departure is worth - $`\tau_C = V_C / \dot V_F`$ is 90 s here against 120 s at 8.0 L, a 25 percent shorter machine lag, which is the part of the early rise belonging to the apparatus rather than to uptake and the most-taught point about a circle system. `default_fresh_gas_flow_l_min` has no published counterpart at all, and the `provenance_gap` says so rather than leaving the silence to read as an oversight. The literals stay in `circuit.py` as defaults so a bare unit test can exercise circuit physics without loading package data, pinned to the file by `test_the_bare_circuit_defaults_match_the_shipped_machine_file`. **The other three read a source and came back with a negative, which is the outcome this kind of work mostly has.** `PL-0NQ1`: `reference_adult.json` stores vessel-rich perfusion 0.76, and De Wolf et al. 2012's Table 1 - the same table all twelve partition coefficients come from - prints 75.8 / 18 / 6, which sums to 99.8. The stored value does not move and *could not*: `_perfusion_fractions_must_sum_to_one` and `core/patient.py` independently reject any set differing from 1.0 by more than `FLOW_FRACTION_TOLERANCE = 1e-12`, so a session deciding the published figure was right would discover that only after editing the file. What the difference is worth is recorded instead - $`\tau = V_i / (Q_i \lambda)`$ scales inversely with perfusion, so 0.76 against 0.758 moves the vessel-rich time constant by 0.26 percent - and the finding as relayed was corrected rather than smoothed: the review said this file cites De Wolf, and it does not; the three *agent* files do, which makes the finding sharper, since the table carrying the discrepant number is one this file never cites. `PL-ZP7Z`: the Workbook's page-168 note says its volatile coefficients are Yasuda, Targ and Eger's and, one sentence later, that sevoflurane's are "taken from the package insert and Abbott data" - and its reference 45 is `Anesthesiology 69:A615`, the 1988 ASA meeting *abstract*, not the 1989 *Anesthesia & Analgesia* paper the agent files cite. The arithmetic is close and settles nothing about the route: 1.70 x 0.65 = 1.1050 against a stored 1.1, desflurane 1.29 x 0.42 = 0.5418 against 0.54, isoflurane 1.57 x 1.3 = 2.0410 against 2.1, missed by 2.9 percent and still inside half the measurement's own standard deviation. **The tier stays at 3 and would stay there even if the attribution were confirmed** - a program's statement about its own provenance is the program talking - and the one comparison that would settle it needs Yasuda 1989's tissue:gas tables, which are in neither PubMed Central nor the private corpus. `PL-ZDWL` is the flattest negative of the three and the one that closes a question: `PL-RFLN` had left the operating-point ventilation load-bearing, both Yasuda papers were read at full text from the private corpus, and **neither publishes a ventilation at all** - it was titrated per subject to normocapnia at an end-tidal carbon dioxide of 5.5-6.5 percent rather than set to a figure, with no $`\dot V_E`$ and no $`f_A`$ reported in either paper. What the *Anesthesiology* paper does settle is the definition the derivation needed, doses to the alveoli as $`F_I \dot V_A \times 30`$ min "where $`\dot V_A = f_A \dot V_E`$", so $`f_A`$ is the alveolar fraction of *total* minute ventilation; the candidate table's second row is recorded as still unreadable from the text rather than becoming a sourced result. Five items, one of which is the v0.4.19 cut itself. |  5 items |
| v0.4.21 | Completed | **The release where the stored coefficients were checked against the measurement they descend from, and the specification learned to argue backwards from harm.** Nothing a reader of the simulator sees changed, and that is measured: `src/anesthesia_sim/app/` and `tests/reference/` resolve to the same tree objects as at `v0.4.20` (`7586231`, `e519afd`), so no interface changed and no pinned reference state was recomputed; every numeric leaf of all five data files is identical across the two trees - zero differences, the whole of that diff being source metadata - and `src/anesthesia_sim/core/` changed by one docstring. **The document three releases could not reach arrived.** Yasuda, Targ and Eger's *Solubility of I-653, sevoflurane, isoflurane, and halothane in human tissues*, Anesth Analg 1989;69(3):370-3 (PMID 2774233), was supplied by the project owner and read at full text; `PL-B9K7` checked its Table 1 - tissue:gas, 14 autopsy specimens, 6-10 per tissue, mean age 65.8 +/- 14.4 yr - against the nine stored tissue:gas coefficients and found **all nine inside 0.71 SD of the measured mean**, two of them (sevoflurane fat 34.0, desflurane vessel-rich 0.54) the measurement itself. A set assembled from anywhere else does not do that, and the Workbook's self-contradiction for sevoflurane resolves in Yasuda's favour on the same arithmetic. `PL-FN5F` split the decision and the project owner took both halves: **adopt the paper, do not store its figures.** One flag moves - the Yasuda entry becomes `"adopted": true` in all three agent files, its `tier` having already been `primary`, because what was wrong was the flag saying the stored values came from somewhere else when they came from there - and De Wolf et al.'s authority narrows to `blood_gas_partition_coefficient` alone, that paper having measured no coefficient, which is exactly why its table could turn out to be somebody else's measurement passed along. Provenance counts move from 25 tier-3 values to 16 and from 9 tier-1 to 18. Storing the published figures was refused on three costs: it would move displayed time constants by -8.3 to +4.5 percent, require recomputing every pinned reference state, and end the property the cross-agent comparison rests on - today all twelve coefficients carry one implementation's identical rounding, so every agent shares the same error, which is what a MAC-normalized comparison needs. **Two findings from the same reading are not about provenance and are now in the files:** the vessel-rich coefficient is Yasuda's *brain* value rather than a weighted group - Table 1 measures brain, heart, liver and kidney separately (sevoflurane 1.15, 1.21, 1.25, 0.78) and no weighting lands where the stored figures land, so a learner reading the vessel-rich trace is reading a brain trace - and the paper is **not** a source for the stored blood:gas values, having measured none. `PL-8GJ6` closed by dissolving: the companion paper's own reference 10 confirms `Anesthesiology 69:A615` is the human-tissues abstract, and what it reports stopped mattering once the full text was held. `PL-LS3H` quantifies what the ideal circuit omits from that companion paper (PMID 2764290) - plastic/gas and rubber/gas coefficients for every component, the PVC mask pad reaching 51.7, 104, 170 and 323 for desflurane, sevoflurane, isoflurane and halothane, the ranking holding at every equilibration time from 7.5 min to 9 weeks - so `docs/MODEL.md` "Known limitations" and `core/circuit.py`'s docstring now carry the measured cost and the consequence a learner needs: the inert circuit is most nearly true for desflurane and least for halothane. No equation changed, and the item says why not. **The specification learned to argue in the other direction.** `PL-BLHV` writes the positive intended-use statement `docs/MODEL.md` never had, drawing the exclusion **at the data** rather than at physical proximity - which would forbid a resident running the simulator on a workstation during a case, carrying no hazard, and permit a run built from a real patient's weight, age and cardiac output at a desk, which is a prediction about that patient - and records **Class C uniformly**, on Annex B.4.3's rule that a software failure's probability is *set to 1*, after the brief's own "undocumented classification defaults to Class C" claim was found in no reachable source and corrected rather than written down. `PL-FDBK` adds the first hazard table: six rows of how a reader could be misled, what stops it, and the test that holds the stop, with `check_named_tests` in `tools/doc_check.py` resolving every test name the document cites so the last column cannot decay into decoration - scoped to the specification on a count rather than a preference, 161 names cited tree-wide and the 21 that resolve to nothing all in `docs/items/`, where a forward reference is correct. **Fourteen apparatus items, nine of them a command asserting something untrue**: a commit count for a branch with none (`PL-NB4D`), a diff line that had been removed (`PL-VP40`), a checkbox contradicting the figure above it (`PL-VFVW`), a rules block missing a rule it presented as complete (`PL-F4JS`), an argument order that swallowed the title (`PL-YNCW`), a placeholder a shell read as redirection (`PL-HKF4`), a recovery that cleared the wrong ref (`PL-K2C8`), a beat calling a finished milestone unfinished while the owner asked for that release and was right (`PL-KD98`), and a feature survey with no plan placement (`PL-BZCM`). Beside them: a lane that sent apparatus work to a simulator session (`PL-GVNS`), an exclusion inside a scope bullet read as membership (`PL-NBCS`), nine items recovered from five abandoned branches (`PL-ZGK2`) and the undeclared `blocked-by` edge the first check after that recovery surfaced (`PL-YPWT`), and a lost handover fixed with a rule rather than a mechanism (`PL-H1JD`). Twenty-one items, one of which is the v0.4.20 cut itself. |  21 items |
| v0.4.22 | Completed | **The release where what this project says about itself was checked against what is true.** Nothing a reader of the simulator sees changed, and that is measured rather than asserted: `src/anesthesia_sim/app/`, `tests/reference/` and `.github/` resolve to the same tree objects as at `v0.4.21` (`7586231`, `e519afd`, `5aa42db`), so no interface element, no pinned reference state and no CI gate moved. The whole of `src/` changes in two files and neither changes a number - `core/alveolar.py` gains a docstring, `data/machines/reference_circle_system.json` gains one `sources` entry and a rewritten `provenance_gap` - so `2.5`, `4.0` and `6.0` stand where they stood, and no equation, parameter, unit, numerical method or solver step is touched. **The science half is the specification understating what it knows.** `PL-QBKQ`: `reference_circle_system.json` said a measured circle-system volume "has not been sought yet", and one had been - Targ, Yasuda and Eger's 9860 ml by water filling, which does *not* close the gap because it includes a latex reservoir bag standing in for the patient's lungs, and the apparatus's own share cannot be recovered from a volume obtained by filling that bag with water. What it supplies is a measured **upper bound**, ordering three figures of which one is measured: this project's 6.0 L, Gas Man's published 8.0 L, and that 9.86 L. The like-for-like comparison is the one to read - apparatus plus lung is 6.0 + 2.5 = 8.5 L against 9.86, 13.8% below, where the bare 6.0 reads as 39% below. `PL-XWCY`: the same paper strikes circuit-wall absorption as the cause of desflurane's washout residual and, in the same measurement, says a real circle system measurably retards sevoflurane and isoflurane relative to ideal - a named, quantified mechanism this model has no term for, bearing on cohorts already sitting at +3.79 and +4.15 SD. `PL-DJYF`: `AlveolarCompartment` restated the reference patient's 2.5 L and 4.0 L/min as dataclass defaults while `reference_adult.json` stored both with their provenance, the same restatement `PL-4YY1` found on `BreathingCircuit`; the docstring now names the file as the authority and `test_the_bare_alveolar_defaults_match_the_shipped_patient_file` fails if the two ever disagree, because a reader meeting `2.5` in `core/` will take it for the model's alveolar volume whatever the prose says. **The safety half is what a displayed value may say when nothing around it qualifies it.** `PL-YLKR` derives the chart's hover readout the way § "Displayed precision" derives the numeric readouts - three lines with the qualifiers ahead of the number, every number through `app/formatting.py`, the readouts' own resolution with the argument for a finer one answered rather than inherited, and which series answer at all. The measurement that decides it: `pyqtgraph.ScatterPlotItem` defaults `tip` to `'x: {x:.3g}\ny: {y:.3g}'`, which on the fat compartment at 48.3 s of a 1 MAC sevoflurane hour prints `3.52e-05` where the readout beside it says `<0.01%` - five decimal places past the derived resolution, no unit, on a chart carrying two axes a factor of two apart. Its build is split to `PL-YVHK` behind the port, which is also where the second finding lands: `ScatterPlotItem` ships `hoverable` set to `False` and a plotted line carries no hover at all, so a port silent about it *loses* the affordance rather than inheriting it (`PL-DNHM`), against a milestone whose definition of done is parity. `PL-3M3K` corrects the brief that said the paused-only restriction transfers whole to Qt; it was a property of Flet's per-frame per-point diff. **The apparatus half is commands answering confidently and wrongly.** `bin/docket branch` told a session whose pull request had already merged to merge the base in rather than restart, which is exactly the push that loses the work (`PL-8M8H`); `bin/docket concurrent` was dominated by `docs/MODEL.md` - 16 of one probe's 22 rule-outs shared only that file - so it refused nearly everything and discriminated nothing, and now groups the tier by path, rarest first, so the strong evidence reads as strong (`PL-PGZK`); work landing between a release cut and its merge sat inside the tag's span and outside its notes with nothing reconciling the two (`PL-028F`); `ROADMAP.md`'s subset counts were hand-maintained and unchecked, and the one a field can decide now is (`PL-GLBF`); the contrast table's reasons cited line numbers that drift, and now cite symbols (`PL-J7C5`); and `PL-16ZC` sat in the gate's clearable set with no deferral marker, so a session clearing the gate would have built a Flet control `v0.5.1` deletes (`PL-NR2K`). `PL-JYR4` closed by its branch merging rather than by work on it. Fifteen items, one of which is the v0.4.21 cut itself. | 15 items |
| v0.4.23 | Completed | **The release where standing decisions were re-taken by counting, and the counts moved them.** `.claude/rules/expert-review.md` asks for the number that would change your mind *before* anything is tightened, and most of this release is that rule run against positions the project had already settled - four of which did not survive it. **No stored scientific value moved, and that is a tree-object identity rather than a reading of the diff:** `src/anesthesia_sim/data/` resolves to `6960c78` at both `v0.4.22` and here, so every partition coefficient, reference-patient parameter, MAC and MAC-awake stands where it stood. `src/` does change, in nine files, and the pinned reference states are the evidence that no number followed - `tests/reference/` differs in exactly three lines, all of them one redundant parenthesis removed, with every expected value untouched. **The core half is two guards that passed on ground they no longer described.** `PL-3PRZ`: at an alveolar volume of 1e-300 L the run advanced, returned a concentration of exactly zero, and the agent-accounting check passed - `CLAUDE.md`'s "prefer an obvious failure to a plausible-looking number" inverted in the one regime the guard was expected to cover most easily, while every larger absurd volume from 1e-9 to 1e-100 L failed loudly. The mechanism is not the one the brief assumed: it is not the amounts that underflow but the **propagator**, which becomes the zero matrix, and `_require_finite` accepted it because the zero matrix is finite and entrywise nonnegative - both properties `core/matrix_exponential.py` states of its output held of a matrix that solved nothing. A second failure surfaced in the same sweep at 1e-309 L, where the row sum is finite at 1.2e+307, the scaling to the series bound reaches `inf`, and `ceil(log2(inf))` raised a bare `OverflowError` outside `core/exceptions.py` and outside the module's documented failures. **Two stronger invariants were tried first and both measured too strict, which is why the weakest sufficient one shipped** - a strictly positive diagonal refuses `exp(-0.5 * 3600)`, a real number no double can hold, and the provable per-entry bound is violated at ulp level by `test_propagating_twice_matches_propagating_once`. Measured across every decade from 1e0 to 1e-323 L, before and after: the same 120 volumes advance, so nothing that worked is refused, and the 116 silent zero-propagator cases plus the one `OverflowError` account exactly for the rise from 77 refusals to 194. The shape worth carrying forward is stated rather than left implicit - **a residual formed from quantities that a single failure can reach together proves nothing when that failure occurs** - and `PL-2MD9` carries the remainder, a constant state row drifting to 2.28e+222 between 1e-8 and 1e-19 L against `UNIT_STATE`'s own docstring guarantee, whose remedy is a change to the numerical method rather than another guard on the result. **`PL-R460` is the release's cleanest reversal, and it reversed a prediction this project made about itself.** `PL-GS5X` predicted that a cached propagator would make each step one matrix-vector product and asked for a measurement rather than an assumption; the measurement says the opposite. At held settings the exact step costs 26.8 us against the operator split's 18.4 us, and **1200 us on every settings change**. The profile says where - `propagate()` 11.6 us for the product itself, `_propagator_for()` 6.9 of which `equation_settings()` is 6.2, `state_vector()` 0.8 - so a propagator cache key closes the settings-change cost, and the residual 6 percent is deliberately not chased, the next 3 us available being `propagate()`'s own per-step guards. Two properties are now pinned that were previously load-bearing and unstated: the cache key is checked entry-by-entry against `dataclasses.fields()` of both settings classes, so a settings field added with no entry fails rather than reintroducing a stale propagator, and CPython's Neumaier-compensated `sum` is what makes the two spellings bit-identical rather than merely close, which is also why the obvious next optimization would be a different function. **A second number in the same measurement matters more than the first:** `docs/WORKING_NOTES.md` asked for its 3.3 ms frame figure to be re-measured, and it is **7.64 ms, or 14.13 ms across five inter-event segments** - 14 ms of a 16.7 ms frame at 60 fps is not the headroom 3.3 ms implied, and `PL-T691` was to lean on it. **The presentation half is three claims about what a reader sees, each checked against the code rather than the prose.** `PL-8XPQ` builds `tools/glyph_check.py` into `make check` and CI, after U+2192 drew as a replacement box in the control-change list on 2026-09-04 - the arrow in `5.60%` to `0.95%`, which is the one thing that line exists to state, failing silently and invisibly to the whole test suite. Both open questions were answered on evidence and both the other way from the brief: per character rather than per Unicode block, because Latin-1 Supplement would admit thousands on the evidence of the three this interface has shown; and the scope widens rather than narrows, `core/` being covered because a `SimulationConfigurationError` is rendered verbatim into the banner and `data/` because `display_name` reaches the readouts, each measured to hold no refused character today so the cost was zero and two silent routes closed. Documentation is excluded structurally - a bare expression statement - after U+00A7 was found only in attribute docstrings, where a first-statement test would have missed it and put a prose character into a list that means *this was rendered*. `PL-LL9Y` asks and answers the alarm-colour question the project had never asked: **deliberately diverge**, with `WARNING = "#8A4B08"` unchanged and no hex constant in `app/theme.py` moved. IEC 60601-1-8 governs visual alarm *signals* - priority encoded by colour together with a flash rate - and this interface has none of it, all five `WARNING` surfaces being bold coloured text with no indicator, no filled banner, no flash and no priority tier; the project owner supplied the half a session could not, that a teaching tool which looks unmistakably unlike a monitor cannot be mistaken for one. It is recorded beside the constant and, in `docs/MODEL.md`, deliberately adjacent to the ISO 5360 agent colours, because the two are opposite answers about different colours and the difference should be visible rather than inferred - the agent colours adopted *because* Table 2 footnote b obligates them, and nothing obligating this one. The priority-to-colour mapping is still not written down and no longer needs to be: it cannot be reached from this environment and three independent secondary sources disagree about the low-priority colour, which `docs/MODEL.md` now says rather than implying a reading of a text nobody opened. `PL-11YF` qualifies the specification's unconditional claim that the six readouts "sit in one row", with the widths read from `METRIC_GRID_COLUMNS` - seven panels side by side at 1200 CSS pixels and wider, four from 992, two from 768, one below - and the finding is the asymmetry the brief could not have known: the ordinal reading weakens below 1200 but only its *invitation* narrows, the 1 485 000 pair comparisons behind the ordering claim comparing displayed values rather than positions, while **the uniform resolution holds at every width**, its argument resting on glyph alignment within a column rather than on a single line. Qualifying that one as though it weakened would have recorded a claim weaker than the code supports. **`PL-JRS3` answers what a Qt port costs the two checks guarding the accessibility floor, by porting the tree and running them.** The dependency is split and not as the question assumed: `contrast_check.py` reads values and survives, `agent_identity_check.py` reads Flet's control objects and goes silent - and its silence is worse than nothing, printing "6 control(s) carry the agent colour, none of them rendered disabled" and exiting 0 on a tree where all six are driven by `setEnabled()` with no paired hide, a sentence a reader cannot tell from the same sentence earned. Where it does fail loudly it misdiagnoses, reporting that the writer never writes the six controls when the writer writes all six through `setStyleSheet`. A latent third finding is filed rather than fixed: a hex constant in any module that is neither `theme.py` nor `simulation_view.py` is measured by nothing, a probe placing a selection colour at 1.07:1 drew `0 errors`, and nothing exploits it today only because no such constant exists under `src/` - the decomposed Qt view being exactly what creates the modules that would. `PL-6194` sweeps 50 redundant parentheses across 15 files and **proves rather than tests** it: every file's `ast.dump` is byte-identical before and after, asserted per file before writing, which is the verification this class of change is entitled to and which `make check` being green is the weaker statement of. Its own re-measurement disagreed with the prediction the brief had recorded to keep the question closed - `tests/` went from 6 occurrences to 15 in eleven days, so somebody typed nine new ones - and that is filed as `PL-YNYK` for the owner rather than acted on. **The apparatus half is four settled positions re-counted, and three of the four moved.** `PL-B73C` reverses a decline whose premise had expired: it rested on the repository holding exactly one ref attributable to no item, and re-measurement found 10 unlanded heads, 10 with no id in the name and **0** with no leading id in any subject, `PL-JX2T` having closed `origin/Review_articles` in `v0.3.7`. So the steady state is silence, `flight` and the digest name such a ref with no suppression rule at all, and the most promising of the four designs considered would have been machinery for an empty set - what keeps the set empty being `tools/branch_id_check.py` rather than luck. It refuses to overclaim twice: an unread ref is never called unattributed, and a local branch collapses with its tracking ref before comparison, without which the session running the check reported its own branch as nameless - a live bug on the first real run. `PL-JQVB` answers one question no and the other with a number nobody had counted. The four dispositions gain nothing, because a pasted brief reaches only the sessions someone pastes it into, which is the property `PL-1H3H` built it for rather than a gap - decisively, a consultant reviewing the apparatus would otherwise load, by opening the thing under review, the rule telling it that tree is not worth reviewing. And skills are measured on a **second line** rather than folded into the resident total, because a skill never invoked costs a session nothing and one total cannot mean both quantities. The count that settled it, taken from the tags across `v0.4.0` to `v0.4.22`: 19 253 characters of instruction text added over twenty-two patch releases, of which the growth instrument reported 3 135 - **16 percent** - and none at all over the last two releases, `CLAUDE.md` having not moved since `v0.4.18` while the skill gained 1 729. The two sets now stand at 50 570 resident characters against 113 203 reachable on demand. `PL-WGXJ` gives the apparatus standard the floor it never had, binding the answer-giving surface rather than the path list: what the apparatus tells a session must be true, or must say what it could not read, a partial reading handed over as a complete one being the violation because at the point of use the two are indistinguishable. The property was chosen by counting - of 41 open apparatus-only `defect` items, about 35 describe a command, check or brief handing a session a confident answer that is wrong or incomplete, recorded in the rule as an order of magnitude rather than a statistic, with the four clear exceptions named - and the strongest justification is measured rather than argued: `PL-MVC2` records a class misspelt as `safey`, which matched no rule, so work a clinician could be misled by stayed seatable in the bottom band while the check reported zero errors. It costs **zero resident characters**, being path-scoped, and asks for no polish, coverage target, abstraction or prose, so it cannot be quoted as the specialist standard arriving by another door - `PL-6SBB` running the other way. `PL-7790` closes the residual `PL-X3WZ` left, and the reading is the item's own declared `touches` rather than the commit's paths: a queue-only commit stakes a claim when the item's copy **on the base** declares a `touches` that never leaves `docs/items/`, which costs back none of `PL-X3WZ`'s eight false marks and excludes a capture for free, the choice of tree being the clause. Two measurements changed the answer here too - none of the eleven unlanded refs carried an id in its name, every branch being harness-generated before its session starts, so the branch-name cover is structurally unavailable in this repository; and the bound that said "the mark returns on the first commit outside the queue" fails hardest on exactly the items whose whole deliverable is a queue edit. A live instance was running while it was decided: `origin/claude/loving-ride-mo6njm` carried "PL-XR8K: close the v0.4.22 tag item" with its whole diff in `docs/items/`, and `flight` named only `PL-JRS3`. `PL-7QKY` un-circularises `docs/WORKING_NOTES.md`'s own instruction, which could not be evaluated without doing the thing it gated: `bin/docket show <id>` now points at the threads concerning that id, through a new standard-library `notes.py`, reading bodies as well as headings because headings alone would have printed nothing for 75 of 106 ids and silence is indistinguishable from "no thread concerns your item". It points and does not summarize, since a generated precis of a stale thread would be read as current, and it is silent in the three cases where there is nothing to say. The file's cost is now stated where the instruction is: 34.5 KB when the item was written, **95 KB and 1 603 lines** now. A test was caught passing vacuously while writing it - `store.ID_ALPHABET` excludes vowels, so an invented `PL-AAAA` matched nothing and the assertion held for the wrong reason. Fourteen items, two of which are the `v0.4.22` cut and its tag. | 14 items |
| v0.4.24 | Completed | **The release where `core/` settled what its dimensionless numbers are called, and nothing it computes moved.** The second half of that sentence is a tree-object identity rather than a reading of the diff: `tests/reference/` resolves to `42ce3b2` at both `v0.4.23` and here, so every published-reference expected value is byte-identical and still met, and `src/anesthesia_sim/data/` resolves to `6960c78` at both, unmoved now across three releases. Eleven files under `src/` change and **not one numeric literal in executable code does** - every changed line carrying a number is a docstring or a comment. **Six of the ten items complete `core-domain-language` at 16 of 16**, and they are one question rather than six: how many dimensionless kinds `core/` carries, which of them a type may separate, and which names describe a quantity against a range. `PL-6KNM` renames `require_concentration_fraction` to `require_fraction` on the evidence that all eleven call sites in `core/` pass a `..._partial_pressure_fraction`, so not one passes a concentration and a reader met two names for one kind on one line. `PL-BQ46` adds `MacMultiple` beside `Fraction` and `Percent`, and the hazard it refuses is reachable and arithmetic rather than hypothetical: sevoflurane's MAC-awake band is 0.34 +/- 0.05 MAC against a MAC of 2.0%, drawn at **0.58-0.78%**, and a circuit fraction at the vaporizer's own 8% maximum passed into the same call clears every runtime guard - 0.08 - 0.05 is still positive - and draws the band at **0.06-0.26%**, below the awakening concentration, where a falling trace crosses it late or never with nothing on screen saying so. `PL-KL2Q` states at the aliases which vocabulary a new field takes, by layer rather than by quantity, and records the merged `Annotated` form as priced and refused. `PL-BDNB` renames one integral and records four deliberate leaves at their bindings. `PL-XP6W` gives § "Symbols" the f_i row its own § "Tissue groups" already used. **The one change a learner could notice is `PL-1PSX`**, and its own brief did not survive measurement. `SimulationView._refresh_view` regrouped the whole recorded control timeline every frame - 0.88 ms at a thousand entries, 8.8 ms at ten thousand, 94.6 ms at a hundred thousand against a 200 ms frame - for an answer identical to the previous frame's on every frame that recorded nothing. The item blamed the playback multiplier, reasoning that a drag emits at the event rate while simulated time advances at the multiplied rate; it does not. A change is recorded only once per simulation step and a step is a property of the tick, so 600 slider events at 60 Hz record **100 entries at 1x, 5x, 20x, 60x and 300x alike**, and one entry for a drag made while paused. The item also proposed keying the cache on the record's length, which would have displayed a wrong value: `_record_control_change` *replaces* the newest entry when one control moves twice inside a step, leaving the record the same length and a different record, so the panel would have stated a setting the run was never computed under. The key is the record's identity, and both regression tests were confirmed to fail against the length-keyed version. No ceiling was put on the record, and the reason is recorded rather than assumed: a cap would retire the beginning of a case, and it would bound nothing, `RunDefinition._segments` growing one stretch *and one keyframe* per accepted change and being unbounded too. **The plan reader was wrong about the gate in two ways**, both in the commands every session opens with. `PL-WZBX`: `wave` counted debt the milestone itself exists to clear as clearable *before* it, moving Gate 1 from `3 this gate can clear` to `0 ... 2 the milestone clears itself`, and the beat from `clear the gate` to `implement v0.5.0`. `PL-TNB6`: `next` told every session that `v0.4.x` clears Gate 1, where the timeline makes the gate a row of its own that no patch may ship. **And one closure that never landed is the release's sharpest lesson.** `PL-6TQH` asked the owner to tag `v0.4.23`; the tag went up, the session that cut the release ended `failed` before closing the item, and `docket check --verify` on the next push to `main` errored because an open item's command already passed. `main` was red for seven hours and **no pull request could have shown it** - `quality.yml` replays the whole store only on a push to `main`, a pull request getting `--verify --verify-base` scoped to its own diff. Ten items, two of which are the `v0.4.23` cut and its tag. | 10 items |
| v0.4.25 | Completed | **The release where the run became forkable underneath the interface, and the last Flet build was tagged.** A patch, because a learner cannot reach the first half: `PL-XJ37` records that nothing in the interface lets a learner take a fork or select between runs, so a case runs as it did in v0.4.24 and every displayed value is the same value. Three measurements: `src/anesthesia_sim/data/` resolves to `6960c78` here as at `v0.4.24`, `v0.4.23` and `v0.4.22`, unmoved across four releases; eight files under `src/` change, three in `core/`, and **every numeric constant the diff adds to executable code is a 0, a 1 or a 2** - an index, a count, a lower bound - measured by parsing both revisions with `ast` and diffing the constants; `tests/reference/` changes in one file and the change is the fork-reproduction probe list moving onto the case's own axis, no published-reference expected value with it. **A branch's definition opens at the fork instant on the case's own axis** (`PL-ZMRT`, project owner, 2026-09-14): with a fork at 900 s, `(900.0 + 1e-6) - 900.0` is `9.999999974752427e-07` rather than `1e-6`, so a child asked for its own first microsecond propagated over a different interval from its parent; after the change the branch agrees with its parent at **all 601 shared case instants**, where a definition opened at its own zero differs at **354 of 601**, and `PL-2R2C` dissolved with it - a branch's drawn columns went from 2 of 8 shared with the trunk to 8 of 8. `SimulationController.origin_s` and both subtractions are gone. **`PL-3LZB` is `P1` `safety` and had to land first**: `RunDefinition`'s lower bound was the literal `0.0` and `_segment_index_at` wrapped, so a definition opening after zero answered from its *last* segment instead of refusing - `state_at(0.0)`, `state_at(100.0)` and `state_at(599.9)` all returned 0.005664 alveolar fraction on a definition opening at 600 s, and `evaluate_anchored(0, 500, 100)` drew a varying curve across a span the run did not exist for. A strict no-op on the v0.4.24 tree and reachable the moment a branch opens at 600 s. `PL-TFX5` forks a run at any control-input event, flat rather than as a tree; `PL-J2TD` is what a fork resumes into, a live run opened at a canonical keyframe state guarded by `require_canonical_state` and `resume_at`, advancing by the ordinary path; `PL-B9PY` decomposes `SimulationView` so two runs render, the 211 existing tests unchanged except for reaching the sole run through `view.runs[0]`. Five of the twelve are v0.5.0's own Required-scope ids shipped early in the `v0.4.x` track. **`PL-RKWB` moved the Qt port ahead of v0.5.0's display half**, and this cut takes the number that section held, as its own risk paragraph provided for: the heading moved to `v0.4.26` and nothing else moved with it - because `PL-YVM1` found the earlier renumber had left **51 references in 29 open items, `app/theme.py` and `docs/MODEL.md`** naming the port `v0.5.1`, all six of its build items among them, invisible to `tools/doc_check.py` because none was a section citation, and adopted the rule that outside this file the port is named by what it is, never by a version. `PL-6T4L` stopped the digest offering v0.5.0 with 8 of 22 scope entries open; `PL-H27D` corrected eight statements `PL-ZMRT`'s own sweep never reached; `PL-5328` re-briefed `PL-RD3B` against the tree `PL-2FM6` left; `PL-1V3X` is the v0.4.24 cut. | 12 items |
| v0.4.26 | Completed | **The release where the interface was rewritten and the model was not.** `app/` moves from Flet to PySide6 and pyqtgraph - 15 files, +7 488/-5 357, seven modules added and the Flet chart-series module deleted - against a definition of done that was *parity* with v0.4.25 rather than improvement, and the runtime dependencies swap with it (`flet[all]` and `flet-charts` out, `PySide6-Essentials` and `pyqtgraph` in). **No stored scientific value moved, and that is a parse of both revisions rather than a reading of the diff:** the three agent files under `src/anesthesia_sim/data/agents/` are byte-identical to v0.4.25, and the two data files that do change carry citation text only - all 15 numeric leaves across both are identical. `core/` changes in one file, in one hunk of two lines, and it is a docstring cross-reference following `app/simulation_view.py`'s split into `app/run_view.py`; `tests/reference/` changes in one file, re-pointing the import allowlist and one assertion at `app/dashboard_frame.py` with no expected value touched. **The patch number survives the one surface that grew.** `PL-8PSW` drew two branches on one axis - v0.5.0's comparison display, landed early at the project owner's direction - and the release still crosses no learner-facing boundary, because `fork_at`, `fork_points_s` and `branches` have no caller outside `app/controller.py`: nothing in the interface creates the second run the overlay draws, and only tests reach it. **Three `P1` `safety` items rode the port** rather than being built twice on a toolkit about to be deleted. `PL-2K1R` put "Model outputs - not measurements." under the readouts, which is the first thing in this interface distinguishing a modelled value from a measured one. `PL-YVHK` implemented the hover readout to the derivation `docs/MODEL.md` already carried. `PL-GS3R` replaced the fixed 150-column drawing budget with a chord-width rule, after re-measuring the worst drawn departure at every rung of `TIME_BASE_LADDER`: 0.53 pp on the alveolar trace (0.26 MAC) at the fastest supported settings, and 3.8 pp (0.64 MAC) for a desflurane overpressure induction. **`PL-2QMK` closed at last**, after the whole of the Flet build: Qt renders offscreen in the container Flet's web renderer could not reach, so `PL-YCWZ`'s headless tests assert on the real interface and a session can look at the chart change it just made. The apparatus half is the larger by count - `PL-9GP1` corrected three values the provenance notes denied were in Appendix C of the Gas Man Workbook, `PL-QSJM` caught `make check`'s ruff passing where CI failed on an mtime-keyed cache, `PL-Y6W9` fixed eight tests red on the owner's own machine and green in CI, and five triage passes cleared 107 captures. | 94 items |
| v0.4.27 | Completed | **The release where the audit every close-out runs stopped refusing the work it prescribes.** No shipped code moves: `src/`, `tests/` and `docs/MODEL.md` are byte-identical to v0.4.26 by tree object, so no equation, parameter, numerical method, unit or displayed value changes. The subject is `bin/docket verify --self`, the audit the `docket` skill's close-out requires. Two of its four absolute integrity checks had no passing route for work that was correct - `PL-K82G` for an item whose own work makes a rendered string false, `PL-L4KX` for a `dropped` or `not-delegable:` item that has no command to run - so a correct close-out returned `REJECT`, which is how a reader is trained to skim the block where a real protected-path failure prints. Both new exemptions are read from the **base's** copy of the item rather than from the working tree, which is the build's own correction to the case that authorised it: in `--self` the front-matter guard is advisory, because the close-out sets `status: done` in the same commit as the work, so a declaration read off the branch would have been a self-grant with no guard at all in the one mode that fires routinely. The cost is filed rather than hidden (`PL-TKFD`). `PL-C6XD` is the same duplicated-logic drift one layer down: `render._release_advice` and `render.format_status` each carried an independent copy of the `RESERVED` verdict's wording, so `bin/docket digest` and `bin/docket status` could disagree about whether a release may be cut, and no surface printed the reserved set at all - both now render from one place, and `bin/docket wave` gained the `Reserved` line this cut read to establish that 0.5.0 through 0.9.0 are spent. The two decisions carry no code by design. `PL-MQHN` settles that a setting's tier is decided by *instance multiplicity* rather than Workspace membership - can a reader sensibly have two of these on screen at once? - which is what `PL-WV9K` reads before the Workspace object exists. `PL-YHWG` re-affirms item 34's placement after v0.5.0 against the modularity argument, on a count the reopening had not run, and writes the ordering principle into this file as a rule binding a new *surface* and not a new *value*, with its expiry named. `PL-06YW`, the v0.4.26 cut, closes here. | 6 items |
| v0.4.28 | Completed | **The release where the queue stopped mistaking a live claim for a spent one, and a `verify:` command stopped being twelve separate promises.** Fifty-eight items, second only to v0.4.26's 94 among the releases that record a count, and two of them are reachable by a learner. Both are presentation fixes rather than new capability, which is why the number is a patch: `PL-DHBX` gives the Start, Pause and Reset buttons an explicit colour, their labels having been illegible under the macOS Dark appearance, and `PL-MN4J` makes the chart hover name which of two drawn runs it is reading - v0.5.0's own `Required scope` entry, shipped early in the `v0.4.x` track as a seventh after v0.4.25's five and v0.4.26's `PL-8PSW`. **No stored scientific value moved, by tree object rather than by reading the diff:** `src/anesthesia_sim/data/` resolves to `d9f9c5b` at both `v0.4.27` and here and `tests/reference/` to `fcb3eca`, so every published-reference expected value is byte-identical and still met, and the three files that change under `src/` are all under `app/`. **`docs/MODEL.md` gains 314 lines** for `PL-S6WW`, the one Gate 1 frozen entry here: the specification asserted agent amounts were gas volumes "at one documented reference temperature and pressure" and documented no temperature anywhere, where a liquid-equivalent conversion moves 5.8% between a 20 C and a 37 C reference. **Six items are one bug seen six ways.** `branches_in_flight` collapsed its carriers to one ref per id *before* the tests that decide whether a ref is spent, so a landed claim on a bystander branch silently dropped a live one and `bin/docket next` offered work another session already held - `PL-2BZY`, `PL-61MD` and `PL-RY2R` are the three collapses, `PL-Q9Z1` is `_superseded` reading a failed `git diff` as the tips agreeing about every path, the one direction its own docstring forbids, `PL-VYSP` is a design round whose whole output is item files and which therefore could never raise the mark at all, and `PL-3CTW` is the opposite error - a capture commit claiming the ids it only filed. `PL-BHVM` is the design round underneath them: nineteen items had been re-deciding what evidence proves a ref done, seventeen of them in `vcs.py`. **And `verify:` became one contract instead of twelve patches** (`PL-6TP8`): what an exit status proves, to whom, and why a health check ahead of the discriminating clause proves nothing twice - it was 99.7% of the pull-request replay's serial cost. `PL-7TYC`, `PL-K1WS` and `PL-QJQL` repair the audit's assertion check, which grepped for the substring `assert` across 90 non-test source lines, never asked whether a removed assertion had a replacement, and could not see `pytest.raises` at all. **Session start lost its fan-out**: `PL-0J9K` replaced 389 `git show` processes with one `git cat-file --batch`, `PL-MMVF` memoized 82 duplicate subprocesses out of 192, `PL-DMDF` stopped asking one `git diff` per item file, and `PL-XD3C` bounded a walk that was O(unmerged refs) and so got slower every month on a long-lived clone. `PL-TM9J`, the v0.4.27 cut, closes here. | 58 items |
| v0.4.29 | Completed | **The release where the queue's own writers stopped moving the files that other items point at.** Twenty items, all apparatus, and a patch because nothing crosses a capability boundary: `git diff --stat v0.4.28..HEAD -- src/` reports no file changed at all, `src/anesthesia_sim/data/` resolves to `d9f9c5b` at both refs so no stored scientific value moved, and `tests/reference/` resolves to `fcb3eca` so every published-reference expected value is byte-identical and still met. **Five are one defect (`slug-rename-on-write`): `bin/docket record` and `bin/docket release` each re-derived an item file's slug from its current title while writing an unrelated field**, so a file whose name predated a retitle was moved by a command nobody asked to move anything - the v0.4.28 cut itself renamed `PL-XQRK`'s file that way, scored `R099` at commit `5901ba4` (`PL-QMC0`), and in `bin/docket record` the same write is a delete-plus-add two sessions are told git will merge, reverting to a duplicate-id error (`PL-5QLP`, `PL-LBR6`). `PL-Y5JX` is why the nine drifted files were not simply renamed first: an item's `touches` may name another item's file path, and `PL-3V6C` names two. `PL-YTDN` then did the renames and `PL-JF5Z` recovered `PL-5QLP` off a branch a prune would have taken; this cut stamped twenty items and renamed nothing. **Three more are the `verify:` replay.** `PL-G6J5` set out to fix the per-command outlier advisory and the measurement retired it instead - a pool of test-suite commands has a high median, so the 30x ratio never clears - while the cost turned out to be three files carrying 59% of the 1 458 s, each re-run once per item naming it (`PL-FZ58`); `PL-09G9` makes `docket set` refuse the shape that causes it, `PL-6TP8`'s contract having been prose alone against 82 of 180 open commands. `PL-VHVJ` stopped `verify`'s suppression list substring-matching `xfail` out of pytest's `--maxfail`. **Two Gate 1 entries correct what the roadmap specifies rather than anything that runs:** `PL-H4N8` (science) moves planned item 28's agent cost from the exhausted amount to the delivered one, which understates mid-run by exactly what is still stored, and `PL-QBX0` (safety) widens item 24's preferences gate past `data/**/*.json` to the three ISO 5360 identification colours and the contrast-checked palette in `app/theme.py`. `PL-PZ8D` and `PL-TPCH` close `owner-decisions-2026-09-19`; `PL-JB3Z` closes `apparatus-capture-criteria` by costing four capture filters and refusing all of them, the five bad items in 166 having been mis-observed rather than over-captured. `PL-ZG5J` lands the headless frame-cost harness and `PL-V1F4` repaired its stale route. `PL-T2LH`, the v0.4.28 cut, closes here. | 20 items |
| v0.4.30 | Completed | **The release where the machinery that finds root causes learned to look at the queue itself.** Eight items, all apparatus, and a patch because nothing crosses a capability boundary: `git diff --stat v0.4.29..HEAD -- src/` reports no file changed at all, `src/anesthesia_sim/data/` resolves to `d9f9c5b` at both `v0.4.29` and here so no stored scientific value moved, and `tests/reference/` resolves to `fcb3eca` so every published-reference expected value is byte-identical and still met. **It completes `generator-heads` at 7 of 7** - the programme of recorded root causes that `CLAUDE.md` ranks above everything but a `P0` - and in the same release repairs the tool that ranks them. **`tools/generator_check.py` was blind to the generator the project was working through it** (`PL-LSR0`): `clusters()` partitions open items by a single declared `touches` path and `STORE_PATHS` held `docs/items`, `docs/WORKING_NOTES.md` and `docs/dead-ends.md` out of that partition, an exclusion borrowed from `docket trend` - correct there, because churn counts the files a *commit* changes and every capture changes the store, and wrong here, because on the `touches` axis a capture declares its own subject. The three paths carried 24, 18 and 0 open items when it was measured and removed, and of `PL-G424`'s 21 members 8 declare `docs/WORKING_NOTES.md` and 5 declare `docs/items`, so the blind spot covered both clusters carrying the family. Ranking was the second half: size was the first tiebreak, so that 8-member cluster sorted ninth behind clusters nobody had cited, under a display limit of six; how many other open items name the path now breaks ties ahead of size, and the readings are still deliberately not combined into a score. **`PL-G424` itself was decided by counting** - all 676 line citations in the store classified, 48.0% stale in closed briefs (196/408), 15.6% in open ones (36/231) and 0.0% in the standing documents (0/5) - which killed the obvious route, since extending `PL-4FBP`'s annotation convention across the apparatus would have checked 2,286 id mentions to find nothing. `.claude/rules/citation-drift.md` records what was adopted instead: a closed brief is a historical record rather than a live assertion, so drift there is not a finding; an open brief and a standing document are live and repaired in place; and a line number is not a citation anchor. Only resolvability is scripted, in `tools/doc_check.py`. `PL-DLMM` corrects that file and the item, which both said the project owner had not taken a decision they had ratified. **`PL-YFXG` left `main` red with no documented way out**: `_number_closing` declines a pull-request number when the closing commit changed nothing outside `docs/items/`, which is right about a closure separated from its work and wrong about an item whose work *is* the queue - `PL-YTDN`'s `ceb9385` (#712) changed 12 files, all in the store, and carried both. `PL-TQFB` excuses a `housekeeping` item its `**Why it matters.**` and `**Done when.**` sections, measured against 22 triage-pass items carrying 1,127 lines of brief of which 12 repeat one rationale and 2 hold a finding. `PL-6ZQY` swept the crossing lane and corrected ten briefs that overstated what was left; `PL-CSV0` folded the day's twelve captures into the queue. `PL-GL5P`, the v0.4.29 cut, closes here. | 8 items |
| v0.4.31 | Completed / current baseline | **The release where a recommendation started saying what it buys, and where the model split got a name at each end.** Fourteen items, and a patch because nothing crosses a capability boundary - measured by tree object rather than read off the diff: `git diff --stat v0.4.30..HEAD -- src/` reports exactly one file changed, `core/matrix_exponential.py`, and the whole of it is inside the module docstring (`PL-5MT4`: a cited DOI carried a spurious trailing `10` and did not resolve, the registered identifier being `10.1137/S00361445024180`, and the provenance note beside it claimed both the publisher and the bibliographic indexes were refused by the egress proxy when as of 2026-09-19 only the publisher is); `src/anesthesia_sim/data/` resolves to `d9f9c5b` at both `v0.4.30` and here, so no stored scientific value moved; and `tests/reference/` resolves to `fcb3eca` at both, so every published-reference expected value is byte-identical and still met. **It completes `model-capability-routing`, 4 of 4.** `docs/maintainer.md` told the owner to run "the strongest available model" and named no model at either end of the split, so `bin/docket next`'s per-item strong-model flag and its `delegable` mark both resolved to nothing a reader could act on (`PL-13PB`, `PL-9FNV`), and its `opusplan` recommendation named a model family where the thing being selected for is a capability (`PL-V8QG`). `PL-4MVC` is the same gap in the tool: `docket list` printed the delegable mark and `docket next` - the one command that actually hands over work - did not. **It completes `recommendation-rationale`, 4 of 4.** `next`'s reason line called the debt gate a "frozen list", the store's internal name and the one wording that never says "gate", so on this project's configuration no recommendation had ever announced a gate item as a gate item (`PL-MN0F`); the lane line and the session-start digest named the other lane's pick with a bare id and no reason at all (`PL-Z27P`); and `payoff:` now carries one plain-language line of what closing an item buys, required at `ready` from 2026-09-20 on `verify:`'s dated-cutover pattern and advisory before it (`PL-WYKF`) - with `PL-0SVP` adding the rule to `docket triage`'s own rule list, so a pass meets it there rather than in a refusal it could not have predicted. **The science half is one entry, and it is the first Gate 1 frozen entry this train has carried since v0.4.29.** `PL-7DMJ` records the alveolar water-vapour simplification in `docs/MODEL.md`: alveolar gas is saturated at 47 mmHg, so a dry inspired fraction is diluted by 47/760 - 6.2 % - before any uptake, and the note says why inserting the factor on $`F_I`$ alone would move all four validated wash-in ratios outside their published spread rather than toward the phenomenon. `PL-MPWP` follows it onto `ROADMAP.md` as planned-milestone item 39, the per-compartment gas-phase condition both that note and its temperature sibling stop at. `PL-BSYZ` re-dated the egress refusal in `.claude/rules/citing-sources.md` from a standing fact to a measurement, and the two release-process items close here: `PL-SW0D`, the v0.4.30 cut, and `PL-8GQW`, its tag. | 14 items |

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

**What that span includes, and why the notes are the narrower record**
(`PL-028F`, decided 2026-09-14). The notes are rendered at the *cut* and the
tag goes on the *merge*, so anything that merges while the release branch is
open is inside the tag's span and named in no release notes until the next
release claims it. That is not rare and it is not visible afterwards: measured
2026-09-14 across 47 tagged spans, 12 closing pull requests merged inside a
tag's span its own notes never named, in 11 distinct spans - close to one
release in four - and a squash merge gives the release commit one date, so
`main`'s own history cannot say how long the branch was open.

So the two records answer different questions, deliberately. **The tag span is
what shipped**; `git describe --contains` is authoritative for that and is the
provenance guarantee above. **The notes are what the cut stamped**, which is
the release's own account of the work it was for. Where they differ, the work
is described in the *next* release's notes, and this project already writes
that convention down for the one case that recurs every time - a release's own
cut item, which the next release names.

Nothing reconciles them automatically, and that was the decision rather than an
omission. Re-stamping at merge would need a job fired by the merge, which
cannot write to `main` here: a push made with `GITHUB_TOKEN` starts no
workflow, so the required status checks can never report on it (`PL-N5WZ`).
Every variant that does land needs a person at the merge anyway, and absorbing
a newcomer means the release narrative describes work that session did not do,
which is a judgment no tool should take. `bin/docket check` therefore raises an
advisory on a checkout carrying an unmerged cut, naming what the base has taken
since and both dispositions, while re-running `make release VERSION=X` would
still absorb it.

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
## Current baseline: v0.4.31

v0.4.31 is the release in which a recommendation started saying what it buys,
and the model split got a name at each end.

Fourteen items. It is a patch on the `v0.4.x` track because nothing here crosses
a capability boundary, which is § "Versioning decision"'s test, and because
every number above it is spent - v0.5.0 through v0.9.0 are given to milestone
sections. **Almost nothing a learner can reach moves, and the exception is a
citation:** `git diff --stat v0.4.30..HEAD -- src/` reports exactly one file
changed, `core/matrix_exponential.py`, and all nine changed lines are inside
the module docstring; `src/anesthesia_sim/data/` resolves to `d9f9c5b` at both
`v0.4.30` and here, so no stored scientific value moved; and
`tests/reference/` resolves to `fcb3eca` at both, so every published-reference
expected value is byte-identical and still met. No equation, parameter,
numerical method, unit or displayed value is touched.

**It completes two features, and the pair is one problem seen from two ends.**
`model-capability-routing` (4 of 4) is about the project knowing which model a
piece of work warrants; `recommendation-rationale` (4 of 4) is about the
project being able to say why it is offering that work at all. Both were
opened by the same observation from the project owner - that sessions kept
putting apparatus items in front of them with nothing a reader could weigh.

### The split had no names at either end

`bin/docket next` has told sessions for some time which model an item warrants:
`safety`- and `science`-classed work and any item whose next step is an
unresolved decision want the strongest available model, and a large share of
the queue is marked `delegable` for a cheaper one. `docs/maintainer.md` is
where that is meant to become actionable, and it named no model at either end.

- `PL-13PB` - the strong end read "the strongest available model", which is a
  policy rather than a value. Nobody reading it could resolve the per-item
  flag into a thing to select.
- `PL-9FNV` - the cheap end named nothing at all, and the safe default when a
  session cannot resolve "delegable" is to keep running the strongest model,
  so the mark bought nothing.
- `PL-V8QG` - the recommended split was Claude Code's `opusplan` mode, which
  names a model *family*. What is being selected for is a capability, so the
  recommendation is wrong the moment the strongest model is not an Opus.

`PL-4MVC` is the same gap in the tool rather than the document: `docket list`
printed the delegable mark and `docket next` did not, so the one command that
actually hands over work was silent about the 141 open items a cheaper model
could have taken.

### A recommendation that says what it buys

Three renderers share one relation, `Scope.placement`, and only the one that
hands over work was unreadable. `docket show` said "on the debt gate recorded
under ...", `docket status` printed `[gate]`, and `docket next`'s reason line
said "on v0.5.0's **frozen list**" - the store's internal name for the
recorded list, and the one wording that never says "gate". The branch carrying
it is the ordinary arrangement, a milestone clearing its own gate, so on this
project's configuration no gate item had ever been offered as a gate item
(`PL-MN0F`). The ranking was correct throughout; only the noun was wrong.

`PL-Z27P` is the same failure one level up. Two lines name an item with no
room for a sentence - `docket next`'s closing lane line and the session-start
digest's `By lane` line - and between them they are the only places the
workflow lane reaches the project owner at all. Both printed a bare id, which
cannot tell a `P1` on the debt gate from a `P3` the roadmap places nowhere.
Both now carry the pick's band and its gate relation, from a
`placement_clause` that agrees with the other two renderers and names a gate
only while one is open.

Band and gate relation are facts in the store, so printing them scripts
nothing. What the work *buys* is judgment, and `PL-WYKF` is where that stops
being re-derived every session: `payoff:` holds one plain-language line of
what closing an item changes for the reader, and `docket show`, `docket next`
and the digest print it wherever they name an item. It follows `verify:`'s
dated-cutover pattern exactly - required at `ready` from 2026-09-20, an
advisory before that raised only for the items `docket next` is about to
offer, and nothing already closed backfilled. The checker holds it to presence
and nothing else, because whether a line states a consequence or restates the
title is judgment, and a checker guessing at that would be authoritative and
wrong.

`PL-0SVP` is the same field arriving one surface late. `render._triage_rules`
exists to state the rules a triage pass's answers have to satisfy, read from
`docket.toml` and the checker rather than from anybody's memory, and it named
the `verify:` gate while saying nothing about the new one - so a pass writing
`--status ready` met a refusal the rule list had never mentioned. It is in the
release for the same reason the three above are: the cost of a rule nobody can
read ahead of time is paid by whoever next tries to follow it.

Two decisions inside it are worth knowing. It is scoped to **every** item
rather than to the workflow lane, against this project's own earlier
recommendation, because the count reversed it: lane-scoping charges 157 items
instead of 267 but leaves 31 open items - those crossing both halves or
declaring no `touches` - with no rule at all, and those are disproportionately
the large cross-cutting work where the sentence is worth most. And unlike
`verify:` there is no exemption, since some work has no command that can run
beforehand but no work has no consequence.

### Water vapour, recorded rather than corrected

`PL-7DMJ` is a Gate 1 frozen entry, `science`-classed, and the first frozen
entry this release train has carried since v0.4.29. `docs/MODEL.md` named
water vapour nowhere. Alveolar gas is saturated at body temperature, so 47 of
the 760 mmHg available is water and a dry inspired fraction is diluted by
47/760 - 6.2 % - before any uptake has occurred, while the alveolar equation
carries $`\dot V_A(F_I - F_A)`$ with no such factor. Nine smaller
simplifications were listed and this one was not, so a reader sizing the model
against a real circle system could not see it.

The constant is computed rather than quoted: 47.12 mmHg at 37.0 °C from the
IAPWS-95 saturation equation (Wagner W, Pruß A. *The IAPWS Formulation 1995
for the Thermodynamic Properties of Ordinary Water Substance for General and
Scientific Use.* J Phys Chem Ref Data 2002;31(2):387-535,
doi:10.1063/1.1461829). The conventional 47 is that value rounded, and the two
agree to 0.3 %.

**The equation is not changed, and the note says why in measurements rather
than in argument.** The governing equations are linear in $`F_I`$, so applying
the factor to the inspired term multiplies every computed $`F_A/F_I`$ by
713/760 exactly - and that ratio is the one quantity this model is validated
against. The four published cohorts move from +0.16, +0.31, +0.79 and +0.38 SD
to -2.78, -1.39, -4.84 and -1.15 SD. What fails there is double counting
rather than physics: the published ratios are analyser readings taken from
real airways, so humidification is already inside the measured value, and the
stored tissue:gas and blood:gas coefficients are equilibrated at 37 °C with a
gas-phase water content recorded nowhere this project has read. The note says
so explicitly, so that a later reader does not "fix" it by inserting 713/760.

`PL-MPWP` follows it onto the roadmap. Two "Known limitations" notes - this
one and its temperature sibling, which sizes the 5.8 % fewer moles the stores
hold than their 20 °C label implies - both stop at the same unbuilt change and
pointed at nothing, so a reader asking whether it will be fixed got no answer.
Planned-milestone item 39 records three things neither note could: the lift is
one per-compartment condition rather than two separate corrections;
**correcting the water half alone is worse than neither**; and nothing
displayed today depends on it, every concentration shown being a dimensionless
fraction and every partition coefficient a ratio, so the trajectories, the
mass-balance identity and the MAC multiples are all invariant to it. It
reaches a reader only where an amount leaves the unit, which is the
liquid-equivalent consumption figure item 28 plans. That is what makes it
intent rather than debt, which is why it is one unscoped roadmap line and not
a queue item nobody can work.

### The rest

`PL-5MT4` is the release's only `src/` change and the reason the citation
exception above is stated. `core/matrix_exponential.py` cited Moler and Van
Loan with a DOI carrying a spurious trailing `10`, which does not resolve; the
registered identifier is `10.1137/S00361445024180`, corrected against
Crossref's own record. The provenance parenthetical beside it claimed the
publisher *and* the bibliographic indexes were both refused by this
environment's egress proxy, and as of 2026-09-19 only the publisher
(`epubs.siam.org`) still is - `doi.org`, Crossref and OpenAlex are reachable,
which is how the bad identifier was caught at all. `PL-BSYZ` is that same
correction applied where it would have done the most damage:
`.claude/rules/citing-sources.md` stated the refusal as a standing fact
measured 2026-09-04, so it would have gone on telling every session not to
retry those hosts for as long as the sentence stood. Both are now dated
measurements rather than standing facts.

The two `release-process` items close here. `PL-SW0D` is the v0.4.30 cut
itself, and `PL-8GQW` is its tag - filed because a session cannot push a tag
ref from this environment and the push is the project owner's, and left open
after the owner pushed it. An open item whose `verify:` command already passes
is a store error, and the whole-store replay runs on every push to the default
branch, so that one line was what reddened `main` for four commits while
`ruff`, `mypy` and all 3243 tests were green. Pull requests run the *scoped*
replay, which is why no pull request showed it.

**The debt gate stands at 171 of 175 cleared.** `PL-JVHL` - the hover
answering for whichever run is marginally nearer - is the one remaining entry
workable here, and it sits at `needs-decision` rather than at implementation:
both targeting rules the item proposed measure identical to today's behaviour,
so what is left is a decision about what the readout *shows*. `PL-WZVZ`,
`PL-Z34C` and `PL-8PS6` wait on work outside the gate.

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
| — | **v0.4.x — the code is the model** | Planned-milestone item 29, shipping as a patch in the `v0.4.x` track. A patch, not a milestone. "No behavior changes" held until the 2026-09-03 re-scope and no longer does: the exact step moves the displayed value in its last digit. Moved from ahead of v0.4.0 to behind it (project owner, 2026-09-02): the placement's real constraint is that it precede item 6's substance generalization, and v0.4.0 changes no equation, so gating the teachable case on an unscoped pass over `core/` bought nothing. Scoped and then re-scoped 2026-09-03: the owner's bar is that a reviewer follow `core/` without a lookup table, which naming alone cannot reach, so the operator split is replaced by the exact matrix exponential (`PL-GS5X`). Still a patch — it crosses no capability boundary; see item 29 for why, and for why no exception is recorded. (Written `v0.4.1` until 2026-09-06, which contradicted this row's own rule that the track promises no particular patch number; v0.4.1 and v0.4.2 both shipped without the exact step, as that rule predicted.) **It freezes no gate and takes no section of its own (project owner, 2026-09-05).** The cadence's four beats run for *milestones*; Gate 1 is frozen when v0.5.0 is scoped, as row 4 records and as three of v0.4.0's own deferrals assume; and no patch in this project has ever had a section — v0.2.1 through v0.3.9 each took a version-table row and a baseline section at ship time and nothing more. That this was ever in question is a tooling artefact worth recording: `bin/docket wave` read this row as a milestone because it was written `v0.4.1` where item 29 already called it the `v0.4.x` row, and the gate it therefore asked to freeze was 105 entries against Gate 0's 21 — five times the largest gate this project has cleared, and 62% of the open queue. The row is now written `v0.4.x`, which is what makes the beat agree with the plan. **Eight items**, `PL-P0BB` having shipped in v0.3.2: `PL-GS5X` and `PL-X9KD` under `numerical-domain`, and `PL-H46J`, `PL-212V`, `PL-3TLK`, `PL-9SH6`, `PL-VZL0`, `PL-FZ6T` under `core-domain-language` — plus `PL-X2XX`, which `PL-VZL0` requires and which neither list named until `PL-GGCN` taught the checker to read the second half of a compound prerequisite. Swapping `PL-P0BB` out for `PL-X2XX` leaves the effort totals unchanged. `PL-3TLK` leads; the rest of the naming work follows the exact step. `PL-011` was carried here at the v0.4.0 cut and is **not** part of this step: it was dropped 2026-09-05, superseded by `PL-T691` and `PL-2FM6`. Those two, with `PL-P1Z3`, `PL-8LXM` and `PL-49R8`, are the score architecture the 2026-09-05 design round filed into `numerical-domain` behind `PL-GS5X`, and they are **v0.5.0's, not this track's** (project owner, 2026-09-05) — row 5 carries the reasoning. **This track promises no particular patch number,** which is what `v0.4.x` means: patches are cut as work accumulates and the exact step takes whichever number it lands on. Saying "ships as v0.4.1" would be a promise the release path cannot keep — `docket release` offers the next free number to whatever is finished, so any patch cut before the exact step lands would take it — any number that is genuinely *free*, which since 2026-09-16 excludes one this file has given to a milestone section ahead of the current one (project owner, ratified, on `PL-KQHN`). | 1 L, 6 M, 2 S |
| 4 | **Gate 1** | **Frozen 2026-09-06**, the day v0.5.0 was scoped, and recorded in that milestone's own section below rather than here. Contents were unknown by construction and are now the list: v0.4.0's findings, the queue's own defects, and the model-specification debt. Ships inside v0.5.0, not as its own release — except for the three items "The timeline" had already placed on the `v0.4.x` step, which that patch carries. | — |
| — | **v0.4.26 — the interface moves to Qt** | **Shipped 2026-09-17**, all 28 Required-scope ids closed (`PL-06YW`). **Scoped 2026-09-10**, on `PL-QXSB`'s decision the same day, and it has its own section below. The port `PL-55DH` spiked and `PL-X9T3` measured: the dashboard, the chart and the theme move to PySide6 + pyqtgraph, and nothing a learner can do is lost. **It absorbed planned-milestone item 33, the interface pass, and that absorption was reversed on 2026-09-16** (project owner, on `PL-L9RD`). The argument was that a restyle of a dashboard about to be rewritten is the same work twice, since porting redecides palette, type scale, spacing and layout regardless. The port that landed did not redecide them: its whole effect on `app/theme.py` is 10 insertions and 29 deletions, and the only constant whose value it touched is `ELAPSED_VALUE_WIDTH`, removed as a Flet layout width with no Qt equivalent - no palette entry, type size, padding or radius has moved since 2026-09-10. The port re-expressed the *widgets* and carried the *visual language* across intact, so the premise of the absorption did not come true and item 33 returns to the interface-pass row it held, which moved after item 34 on 2026-09-16 and is now `v0.7.x` (`PL-PHKP`). What the port keeps is the **reservation** rather than the pass: the layout containers are built once here with their splitter handles inert, which is Required scope item 2 and is unaffected. **Moved ahead of v0.5.0 on 2026-09-14** (project owner, on `PL-RKWB`), from the row it held after MVP. The question put was whether v0.5.0's work would be redone after the port, and **the count says mostly not**: of v0.5.0's eight open Required-scope ids, one is wholly inside the rewritten surface (`PL-8PSW`, the two-branch overlay), two have a slice there, and five never touch it - because `tools/import_boundary_check.py` confines Flet to three modules and the milestone's landed work (`PL-T691`, `PL-J2TD`, `PL-TFX5`, `PL-B9PY`) all sits on the surviving side. **Three other grounds carried it, and they are the reasons of record.** `PL-8PSW` is the most presentation-safety-loaded item in the milestone and on Flet it is built where no session can look at it (`PL-2QMK`), while the spike already screenshots offscreen in that same container and `PL-YCWZ` adds headless rendering tests over the real interface. `PL-GS3R` and `PL-YVHK` are both `P1` and `safety`-classed and both sat blocked behind this port for the whole of a milestone. And this port's definition of done is parity against a **closed** enumeration, which is cheapest to check before compare mode - the largest new visual surface in the project - joins the list. **The operative form of the decision is narrower than the move**: nothing new is built in `app/simulation_view.py` or the Flet chart-series module before the port, and v0.5.0's port-neutral spine (`PL-CTD7`, `PL-B8MK`, `PL-Z3W6`, `PL-W7H9`, `PL-49R8`) is untouched by it. **A patch number for a 5 133-line rewrite** because § "Versioning decision" chooses the number for the capability boundary crossed and this crosses none; v0.2.8 is the precedent for machinery at this scale taking one. **It no longer needs a section for the mechanical reason it had one** - every item that waited on it now names the port item doing the work rather than a version, so `blocked-by` resolves with no placed version - and it keeps one because a rewrite this size is not a patch-track row. **Gate 2's freeze is unchanged**: still when v0.5.0 ships, because that gate holds v0.5.0's findings and this port takes no gate of its own. | 2 L, 2 M, 3 S |
| 5 | **v0.5.0 — the case you can branch** | Planned-milestone items 8 (replay half), 26 (bookmarks), 12 (forking), 11 (comparison). **The score architecture belongs here (project owner, 2026-09-05):** `PL-T691` (hold keyframes at every control event and answer any window in closed form), `PL-2FM6` (delete `RunHistory` and draw the chart from the closed-form sampler), `PL-P1Z3`, `PL-8LXM` and `PL-49R8`, filed into `numerical-domain` by the 2026-09-05 design round and chained behind `PL-GS5X`. It is placed here rather than in the v0.4.x track for two reasons that point the same way. It is what forking *is*: item 12's required property — a branch reproduces its parent element-wise at every recorded sample — stops being a property a test has to establish and becomes one the representation cannot violate, because the branch's prefix is the parent's own score rather than a reproduction of it. **That reason was stated wrongly here until 2026-09-06 (`PL-QYPX`)**: the original said the property is "expensive against a recorded sample store", and it is not — v0.4.0's own "Designed for forking" already preserves it, and copying a parent's samples up to the branch point satisfies it trivially. What is expensive against a sample store is holding *two* of them, which is `PL-011`'s dropped growth debt doubled. The placement is unchanged and better supported; only the argument moved. And it is `1 P1 L` plus four more against a patch track whose whole content is otherwise `1 L, 6 M, 2 S`, so admitting it there would roughly double a patch and put a `P1 L` inside one. `PL-011` was dropped on its promise, so this is also where that debt is actually paid: until `PL-T691` and `PL-2FM6` land, the run's sample store grows unbounded. **Four of the five shipped in the `v0.4.x` track instead** - `PL-T691` and `PL-P1Z3` in v0.4.8, and `PL-2FM6` with `PL-8LXM` brought forward on 2026-09-08 when `PL-4RBD` was re-measured at 0.32 MAC and re-banded `P1` `safety`; the debt-gate section carries that decision. The placement argument above stands for what it placed, and is left as written. **Scoped 2026-09-06**, which froze Gate 1 - a list now standing at 175 entries, its post-freeze additions dated in that section; the goal, required scope, definition of done and out-of-scope list are in the "v0.5.0 - the case you can branch" section below, and sixteen items carry it. **Five more shipped early the same way**, in v0.4.25 (2026-09-14, `PL-G7RD`): `PL-TFX5`, `PL-J2TD`, `PL-ZMRT`, `PL-B9PY` and `PL-5328`, ahead of the port; the scope list is unchanged and they are closed against it. **`PL-8PSW` makes a sixth**, in v0.4.26 (2026-09-17, `PL-06YW`): the two-branch overlay, asked for by id and built on the port's own chart rather than twice, on the same disposition - its Required-scope entry below records what shipped and is unchanged. **`PL-MN4J` makes a seventh**, in v0.4.28 (2026-09-19, `PL-T2LH`): the chart hover naming which of two drawn runs it reads, on the same disposition - its Required-scope entry below records what shipped and is unchanged too. | — |
| — | **MVP complete** | A learner can run, branch, and compare a case. | — |
| 6 | **Gate 2** | **Frozen when v0.5.0 ships, not when the milestone below is scoped** (project owner, 2026-09-16, ratified - chosen over freezing it on the scoping day as beat 1 says, and over deferring the whole scoping round until v0.5.0 ships). Row 7 was scoped two releases early, so the cadence's own trigger would have frozen this list before v0.5.0 had been implemented — leaving it holding none of v0.5.0's findings, which is the one thing a gate is defined to hold. § "The cadence" records the exception and the item that re-examines the trigger; v0.6.0's own section says where the frozen list goes when the moment comes. Ships inside v0.6.0. | — |
| 7 | **v0.6.0 — the layout is the reader's** | Planned-milestone item 34's tiled half: the layout model, the View contract, the view registry, workspaces, persistence, the unconditional display region, and every layout operation. **Scoped 2026-09-16** (project owner, ratified on `PL-NMTF` - chosen over inserting item 34 ahead of v0.5.0, and over one undivided milestone with break-out inside it). The serialized layout format carries a multi-window root from v1; nothing in this release creates a second window. Break-out is row 9, deliberately — see that section's "Explicitly out of scope" for why the split costs nothing structural. **The placement was reopened and re-affirmed on 2026-09-17** (project owner, ratified - chosen over moving item 34 ahead of v0.5.0, on the argument that every interface question settled before the area model is settled against a layout that is going away): v0.5.0's Required scope is 13 of 20 `done` and the compare surface is among the closed, so the tail a re-order would protect is 4 M and 3 S against this row's own 4 L, 16 M, 3 S. Planned-milestone item 34's entry carries the count, and the standing rule that round produced - **no new display surface is built before this release**, until item 34's View contract and view registry ship. | 4 L, 16 M, 3 S |
| 8 | **Gate 3** | Frozen when v0.6.0 ships; ships inside v0.7.0. | — |
| 9 | **v0.7.0 — the second screen** | Planned-milestone item 34's break-out half: an area taken into its own top-level window, itself a full window with its own areas. Not yet scoped. What it owes the display is already decided rather than left to its scoping — `docs/MODEL.md` § "Minimum displayed outputs" → "What this list requires once the layout is the reader's" carries the tier split (project owner, 2026-09-16, ratified - chosen over `PL-W54S`'s own two live readings, every window carrying the whole region and the main window carrying it alone), because it decides the shape v0.6.0 builds the unconditional region in. | — |
| — | **v0.7.x — the interface pass** | Planned-milestone item 33: one deliberate visual design pass over the whole interface - palette, type scale, spacing rhythm, density and the visual composition of each surface - rather than the per-defect corrections the queue has been making one at a time. **Arrangement is item 34's and not this row's** (`PL-BNYF`, 2026-09-16); the entry for item 33 carries why. A patch track rather than a numbered milestone, because it crosses no capability boundary. **Restored here 2026-09-16**, having been absorbed into v0.4.26 on 2026-09-10 and un-absorbed when that port turned out not to have redecided the visuals; the row that release's own entry reversed is this one. **Moved here from between MVP and Gate 2 on 2026-09-16** (project owner, ratified - chosen over leaving it ahead of item 34, on the argument that item 34 and break-out introduce an area header, a workspace tab strip, a live splitter handle and a drag affordance, none of which exists to be styled today; what the other side bought was a styled interface two releases sooner, and `PL-BNYF`'s separation of arrangement from appearance means the composition of each surface would mostly have survived the move). It renumbers from `v0.5.x` to `v0.7.x` as a consequence: a patch track takes the number of the release it follows, which is mechanical rather than a second decision. `PL-PHKP` carries it. It is a design round with the project owner before it is items: the owner framed it as "a decent size overhaul (theme, style, overall polish)" and as not urgent, wanted after the simulator works. | — |
| 10 | **Gate 4** | Frozen when v0.7.0 ships; ships inside v0.8.0. | — |
| 11 | **v0.8.0 — the schematic** | Planned-milestone item 27: Gas Man's Picture, showing where the agent *is* rather than where its tension is. (Written `v0.6.0` until 2026-09-16, when item 34 took that number and this moved down two.) | — |
| 12 | **Gate 5** | Frozen when v0.8.0 ships; ships inside v0.9.0. | — |
| 13 | **v0.9.0 — multi-substance and nitrous oxide** | Planned-milestone items 6 and 7, and the substance generalization Phase 1 describes. (Written `v0.7.0` until 2026-09-16, for the same reason as row 11.) | — |
| 14+ | **Beyond** | The machine and its interlocks (items 1-5), save/load and replay (9, 10), then intravenous agents (13-15), in "Development pathway" order. | — |

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
they gate, which is why rows 4, 6, 8, 10 and 12 carry no version.

Rows 5 and 7 are scoped and have their own sections below, as does the
`v0.4.26` row above them — v0.5.0 on 2026-09-06, the Qt port on 2026-09-10 and
moved ahead of row 5 on 2026-09-14, and v0.6.0 on 2026-09-16. Rows 9, 11 and 13
are the intended order and are not yet scoped; each becomes real only when it
gets its own goal, required scope, definition of done and out-of-scope list
here, per the development rules.

**Row 7 is the first milestone scoped out of turn, and the reason is recorded
because the cadence assumes otherwise.** Every earlier milestone was scoped
when it was next; this one was scoped while two releases still sat ahead of it,
because the design was already settled — `PL-3J2P` fixed the representation,
`PL-C842` the container and `PL-FTP5` the provenance, and a queue audit
(`PL-BNYF`) had filed fourteen prerequisites against a build item that did not
exist. Scoping was what those fourteen were waiting on. The consequence is row
6's, and § "The cadence" carries it: beat 1 no longer immediately precedes beat
4, so the freeze that beat 1 normally performs is dated to v0.5.0's ship
instead.

Row 5's internal ordering — forking and comparison ahead of save/load and
replay — was recorded here as a proposal rather than a decision, on the grounds
that branching within one session is the teaching payload while persistence is
a convenience. Scoping it decided the question, and the decision is the
proposal: v0.5.0 takes items 26, 12 and 11 with only the *replay driver* half of
item 8, and puts save/load (item 9) and a user-facing replay control (item 10)
out of scope. That is a deliberate departure from "Development pathway"'s Phase
3 sequence, which no longer stands for these four items.

### Why the gates are on this list and not behind it

A gate that lives in a separate document, or in a session's memory, is
renegotiated every time it is inconvenient. Put on the timeline it is a step
with a size, and skipping it is visible as skipping a step. The cadence that
generates rows 2, 4, 6, 8, 10 and 12 is specified under "The debt gate" below;
the rule is that scoping a milestone freezes its gate, and the gate clears
before that milestone's implementation begins. Row 6 is where that rule has an
exception rather than an application, and § "The cadence" states it: a
milestone scoped out of turn freezes its gate at the moment the cadence
*intended* — when the milestone before it ships — rather than on the day it was
scoped.

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

**Two of the three counts above are deliberately left to the reader**
(`PL-GLBF`, 2026-09-13). "Seven entries are marked `not-delegable`" is checked
by `tools/doc_check.py`, because `not-delegable:` is a field on each item and
the number is a query over it. The two in the bullets above are not, and the
nearest field is a near miss rather than a gap: `touches:` records the files an
item is *expected to change*, where these sentences record the scope an item is
*permitted to reach*. On the second one's own three ids a checker over
`touches:` computes two against a correct three - `PL-ZN0N` declares
`pyproject.toml` and nothing else, and may still annotate `noqa` directives in
`src/`. A check built on it would fail a correct sentence, which is worse than
no check. Both are safe to leave unchecked for a second reason that holds only
here: this list is frozen and every id on it is closed, so neither number can
drift again. The same shape in a *live* section can, and that is a separate
question rather than one this note settles.

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
  the Flet chart-series module (deleted with `PL-25KS`). Both are behavior-unchanged and held to the
  existing view tests; PL-WB0X's brief names the modules. Stage 1 lands before
  the MAC unit below: that item rewrites every formatter and extends
  `docs/MODEL.md`'s "Displayed precision" derivation, which today terminates in
  a private static method on a Flet view class, so the one function the
  specification reasons about cannot be read, cited or tested without loading
  the whole interface. Stage 2 lands before the chart work, which four items of
  this milestone touch in the same place.
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
- Stage 3 of the interface layer's decomposition - the `SimulationView`
  decomposition proper (queue item PL-B9PY). Stages 1 and 2 are in scope
  above; stage 3 stays at Gate 1, because only v0.5.0's side-by-side
  comparison of two branches needs it (project owner, 2026-09-02).

## Completed: v0.4.26 - the interface moves to Qt

**Scoped 2026-09-10**, on `PL-QXSB`'s decision the same day. `PL-55DH` built
the spike, `PL-X9T3` measured it on the project owner's own machine, and the
owner chose to move.

**Moved ahead of v0.5.0 on 2026-09-14** (project owner, on `PL-RKWB`), from the
position after MVP that it held when it was scoped. The question put was whether
v0.5.0's work would have to be redone after the port.

**Counted rather than answered from the shape of the question**, which is the
same method § "Sequenced past v0.5.0" used on 2026-09-14 when the general form
of this was asked about the gate entries. Of v0.5.0's eight open Required-scope
ids, **one** is wholly inside the surface this port rewrites - `PL-8PSW`, the
two-branch overlay - two have a slice there (`PL-RD3B`, `PL-LPLD`, both of whose
durable halves are in `app/controller.py`), and five never touch it at all
(`PL-CTD7`, `PL-B8MK`, `PL-Z3W6`, `PL-W7H9`, `PL-49R8`).
Exactly three modules imported Flet - `app/main.py`, `app/simulation_view.py`
and the chart-series module - and `tools/import_boundary_check.py` held `flet` and
`flet_charts` to those three between them from `PL-9KDK` until `PL-25KS` freed all
three and confined both packages to no module at all, whose unused-allowance
error then asks each port commit that frees a module to drop its entry - and the milestone's landed work - `PL-T691`'s score, `PL-J2TD`'s keyframe opening,
`PL-TFX5`'s fork, `PL-B9PY`'s decomposition - all sits on the surviving side.
**So the premise of the question did not hold, and the move was taken on three
other grounds:**

1. **`PL-8PSW` would otherwise be built blind.** `PL-2QMK` records that no
   session in the web container can visually confirm a chart change, because
   Flet's renderer fetches Flutter assets the egress proxy denies; the Qt spike
   rendered offscreen in that same container once `libegl1` was installed
   (`PL-VHLZ`), and Required scope item 6 has since landed headless rendering
   tests over the real interface in
   `tests/integration/test_qt_rendering.py`. `PL-7J96`, the Flet equivalent, is `dropped` as superseded -
   so the Flet build gets no automated rendering check at all. `PL-8PSW` is the
   most presentation-safety-loaded item in v0.5.0: six channels already spent,
   a two-compartment cap the design rests on, and every curve owing an
   attribution to its run.
2. **Two `P1` `safety`-classed items sat blocked behind this port.** `PL-GS3R`
   (0.26 MAC of drawn departure at the 12 h base, worst in the steep early
   wash-in) and `PL-YVHK` (the hover readout). Both are designed; both waited
   only on the toolkit, and ordering v0.5.0 first kept them blocked for the
   whole of a milestone.
3. **The parity target is smaller now than it will ever be again.** This
   milestone's definition of done is parity against a **closed** enumeration.
   Landing v0.5.0 first would add compare mode - the largest new visual surface
   in the project - to the list that has to be checked.

**What was decided is narrower than "move the milestone", and that is the form
to apply**: nothing new is built in `app/simulation_view.py` or
the Flet chart-series module before this port. v0.5.0's port-neutral spine is untouched
and still ships on its own schedule; only its display half waits. `PL-8PSW` and
`PL-LPLD`'s bookmark list are the two open items that moved.

**Why this number, which is a patch number for a rewrite of the whole
dashboard.** § "Versioning decision" chooses the number for the capability
boundary a release crosses, and a learner can do nothing after this port that
they could not do before - the same argument the interface-pass row made for the
restyle it replaces (that row was written `v0.5.x` until 2026-09-16 and is
`v0.7.x` since, having moved after item 34). v0.2.8 is the precedent for machinery at this scale taking
a patch: thirty-eight frozen entries, no simulator change.

**Why it takes a section, which no patch in this project ever has - and the
reason has changed.** It was mechanical: `blocked-by: vX.Y.Z` resolves only
against a version the roadmap *places*, a patch-track row is not a version, and
`PL-GS3R` - `P1`, `safety`-classed - would otherwise have sat at the top of
`bin/docket next` as startable work guarded only by a paragraph in its brief
(`PL-L09X`). **That reason is spent as of 2026-09-14.** Every item that waited
on this port now names the port *item* that does the work - `PL-G59B` for the
chart, `PL-25KS` for the dashboard, `PL-L9RD` for the theme - which is the shape
`PL-3355`'s brief had already argued for and `PL-16ZC` already used. Nothing
resolves against this heading any more, so the number below is free to move
without dragging a `blocked-by` field with it.

The section stays for an ordinary reason instead: a rewrite of 5 133 lines with
its own goal, required scope, definition of done and out-of-scope list is a
milestone by this file's own test, whatever number it ships under.

**The one risk, recorded rather than engineered around - and it has happened
once.** `bin/docket release` offers the next free number to whatever is
finished, so a patch cut before this lands *would have taken* this section's
number - the hazard the `v0.4.x` row names, and no longer the default it
describes: the decision two paragraphs below is that the guard withholds it. `v0.4.25` was cut on 2026-09-14 (`PL-G7RD`) from
ten finished items, and this heading moved to `v0.4.26` with nothing else moving
with it: no item's `blocked-by` named a version, and `PL-YVM1` had swept the
last prose that did.

**That rename was cheap once and is not cheap now**, which is the part "a rename
each time, not a re-scope" got wrong. The port's own work has put the number
back. Counted 2026-09-16, eight sites in five files outside this one name
`v0.4.26`: three in `tools/import_boundary_check.py`, two of those inside error
messages a developer reads; two in `docs/ARCHITECTURE.md`; and one each in
`subprojects/docket/src/docket/roadmap.py`, `.claude/skills/docket/SKILL.md` and
`subprojects/docket/README.md`. Four carry the section-citation form
`tools/doc_check.py` validates, so a rename that missed them fails `make check`;
the other four name the number bare, where no check reads it. **Re-counted after
`PL-7SVX` closed in `#638`** - the last of this section's Required scope, and the
one item whose `touches` covered the two largest of those files - and the eight
sites are unchanged. So the count above is this section's settled total rather
than a reading taken mid-flight, which is what makes it usable for deciding the
question below.

**A patch cut no longer takes this number** (project owner, 2026-09-16,
ratified, on `PL-KQHN`). `PL-VFD8` and `PL-188T` taught the reserved-version
guard to answer from every version the roadmap names ahead of the current one,
so a bump arriving at this section's number is withheld and named rather than
offered as free; the decision is that the withholding **stands**. A cut at this
number is a deliberate act rather than the release path's default, taken with
the rename cost counted above as its named price. Chosen over keeping the
mechanic and narrowing `PL-VFD8`'s reservation to match, on two measurements the
mechanic predates: that rename cost, and `PL-Y1L0`'s finding that a cut at
`0.4.26` *or* `0.4.27` drops this section out of `wave`'s unreleased set and
moves the beat to v0.5.0 - reversing `PL-RKWB` - with nothing reporting it.
`PL-G7RD`'s 2026-09-14 renumber stands as what happened and is superseded as
practice.

**Ordinary patch numbering is untouched by that.** This track still promises no
particular number, and a cut still takes the next number that is genuinely
*free*. What changed is what free means: a number this file has given to a
milestone section ahead of the current one is not one, which is exactly what
`#606` taught the guard to see.

**The one question the reorder leaves open is this number, and it is recorded
rather than settled.** § "The cadence" says a gate does not get a version and
that no interim release is cut partway through clearing one - and five of the
fixes this port carries are Gate 1 entries. The reading taken here is that this
port is a milestone that *carries* gate fixes rather than being gate work:
§ "Debt inside the milestone's own scope" makes the test whether the item
appears in the milestone's `Required scope`, and all five appear at item 8. The
alternative - that it ships inside v0.5.0 with no version of its own - is
recorded in `PL-RKWB` and would change this heading and nothing else.

**It absorbed planned-milestone item 33, and no longer does** (project owner,
2026-09-16, on `PL-L9RD`). The argument was that a restyle of a dashboard about
to be rewritten is the same work done twice: porting rewrites `theme.py`, every
layout and every density decision regardless, so palette, type scale, spacing
rhythm and layout would be decided once, during the port, rather than applied to
Flet and then again to Qt.

**The premise was measured against the port that actually landed, and it did not
hold.** `ae8fc7bc` (`#588`, `PL-25KS` and eleven others) changed `app/theme.py`
by 10 insertions and 29 deletions, and the only constant whose value it touched
is one it removed - `ELAPSED_VALUE_WIDTH`, a Flet layout width with no Qt
equivalent. Not one palette entry, type size, padding or radius changed, and
nothing in `BACKGROUND`, `PANEL`, `PRIMARY`, `ACCENT`, `INK`, `MUTED`,
`WARNING`, `APP_TITLE_SIZE`, `METRIC_VALUE_SIZE`, `PAGE_PADDING`,
`PANEL_PADDING` or `PANEL_RADIUS` has moved since 2026-09-10. The port
re-expressed the **widgets** and carried the **visual language** across intact.

So item 33 returns to the interface-pass row of "The timeline" (written
`v0.5.x` then and `v0.7.x` since 2026-09-16, when it moved after item 34),
where it was placed on 2026-09-08, and this milestone keeps two things that are
not the pass itself. The first is `app/theme.py` expressed for Qt, which is
`Required scope` item 3. The second is the **reservation** described at item 2:
the layout containers are built once here with their splitter handles inert, and
**item 34** is what turns them live - the area system, not the visual pass.
A reservation is cheap and a design round is not, which is the distinction the
absorption blurred.

**Item 34 rather than item 33, corrected 2026-09-16 (`PL-BNYF`).** The
un-absorption note above was written to pull the visual pass back out of this
port, and in passing it attached the reservation's next step to item 33, which
`Required scope` item 2 below and item 34's own entry both give to item 34.
Item 33 decides how the interface *looks*; what a reader may do to its
*arrangement* - split, join, swap, break out, save as a workspace - is item
34's whole content. A session scoping the interface pass off the uncorrected
sentence would have believed it owned building split and join.

**One question is left open on purpose, and it is not in this scope.** Where
the Qt styling layer *lives* - 27 `setStyleSheet` sites composing CSS strings
from `app/theme.py`'s constants, with partial helpers in the view modules,
against a `theme.py` whose own comment forbids it a toolkit import - is
`PL-Y4YX`. It is named here rather than under `Required scope` deliberately:
naming an id in that list *places* it in this milestone, and the owner approved
un-absorbing the interface pass rather than a refactor of where styling lives.
The port ships with the styling composed where it is today.

**Gate 2's freeze is deferred, deliberately, and moving this port did not
disturb it.** "The debt gate"'s cadence would freeze it as this milestone is
scoped. Gate 2 is meant to hold *v0.5.0's* findings, and v0.5.0 has not been
implemented, so a gate frozen today would be empty by construction and would
then refuse the findings it exists for. It freezes when v0.5.0 ships, and this
port takes no gate of its own - as was already true when it sat after MVP - so
its own findings go to Gate 2 alongside v0.5.0's. **This is now the first of
two instances rather than a one-off**: v0.6.0 was scoped on 2026-09-16 under the
same reasoning, and § "The debt gate" -> "The cadence" is where both are
recorded and where the exception has its condition written down, so the argument
is not re-derived per milestone.

**What the move does change is Gate 1, and in the direction `PL-D143`
asked for.** Nine of the twelve entries that gate could not clear were waiting
on this port; with the port ahead of v0.5.0 they clear before the milestone
they gate begins, instead of after the release that follows it. Gate 1's own
§ "Sequenced past v0.5.0" carries the revised disposition.

### Goal

**Run the same simulator on PySide6 + pyqtgraph, with nothing a learner can do
today lost, and the interface pass done once on the way.**

The measured case is in `docs/WORKING_NOTES.md` under "Measured on real
hardware", and none of it is speed. The lag this question was opened on is gone:
the owner reports the Flet build as no longer noticeably slow after `PL-2FM6`.
Four grounds survive:

- **Input latency** 0.85-2.46 ms p90 against Flet's 20-30 ms, which is the axis
  "laggy" named. The mechanism rather than the hardware is the gap: Flet's event
  loop is blocked by a control-tree diff every frame, and Qt has no diff.
- **`PL-GS3R` is a safety decision this one decides.** Its cheapest route out of
  0.26 MAC of chord error is more columns: 49.4 ms of a 200 ms budget on Qt
  against about 78 ms for Flet's diff alone, before its client renders anything.
- **`PL-2QMK`**, exercised rather than argued - the spike writes a PNG of the
  running interface in the very container where Flet's renderer cannot load.
  Most of `presentation-safety` waits on that.
- **Headroom** for the schematic (planned-milestone item 27), which is a second
  large visual surface on a toolkit charged per control present per frame.
  (Written "v0.6.0's schematic" until 2026-09-16, when item 34 took that number
  and the schematic moved to v0.8.0 - named by item number here, per the
  `PL-YVM1` rule this port already adopted, so it cannot go stale again.)

### Required scope

1. **The chart** (queue item `PL-G59B`). Six compartment traces, the two
   clinical references, both axes, the control marks and the wash-in plot, on
   pyqtgraph. `PL-GS3R`'s
   chord-width column rule lands here rather than separately - the port is what
   makes it affordable, and it is the reason `PL-GS3R` is sequenced behind this.

   *`PL-YVHK`, the chart's hover readout, lands here too* (project owner,
   2026-09-14, splitting `PL-YLKR`). What it shows is already decided:
   `docs/MODEL.md` § "The chart's hover readout: what the tooltip may show"
   derives it, in v0.4.x, so this is a build against a written specification
   rather than a design round inside a port. **It is parity rather than new
   capability**, and the distinction is load-bearing here: `ScatterPlotItem`
   ships `hoverable` set to `False` and a plotted line carries no hover at
   all, so a port silent about it *loses* the Flet build's hover instead of
   reproducing it. Building it on Flet first was refused because the same
   content is roughly 1 870 per-point strings there and one format callable
   here - see that item for the measurement.
2. **The dashboard** (queue item `PL-25KS`). The readout row, the parameter
   controls, the agent selector, the transport, the new-case dialog and the
   notice banner -
   `app/simulation_view.py`, 4 321 lines as measured 2026-09-14.

   *It reserves for planned-milestone item 34 and builds none of it (project
   owner, 2026-09-12).* Each of those surfaces becomes an independent widget
   inside nested `QSplitter`s rather than a fixed layout, and **the splitter
   handles stay inert**: item 34 is what turns them live and adds the split/join
   affordance, the workspace tabs and the savable presets.

   The reservation is close to free, because the components it needs are
   already owed. `PL-B9PY` decomposes `SimulationView` in v0.5.0 and records
   that "the Qt view is built decomposed from the start", so what this decides
   is only the container those components go into - nested splitters rather
   than fixed layouts. The alternative is laying out every panel twice, which
   is the argument this milestone makes for *reserving* for **item 34** here
   rather than building it - the reservation survived the un-absorption above,
   because a layout container genuinely is built once by this port. (Written
   "item 33" until 2026-09-16, `PL-BNYF`: the fourth and last site where the
   un-absorption note's wording had attached the layout reservation to the
   visual pass, two lines after this same scope item gives it to item 34.)

   *The inert handles are the deliberate half, not an oversight.* A draggable
   splitter is something a learner can do that they cannot do today, so live
   handles would be new capability - which § "Fixes this port carries" excludes
   "whatever its size", and which would put a fourth entry beside `PL-16ZC` on
   the wrong side of that line. Parity below means "identical except for this
   list", and it is checkable only while the enumeration stays closed. Flipping
   the handles live is item 34's first step and costs a line.
3. **The theme** (queue item `PL-L9RD`). `app/theme.py` re-expressed for Qt,
   with the six compartment colours and their dash patterns intact and both
   tools that read the file still describing it. **The visual pass is not
   here** - item 33 was un-absorbed on 2026-09-16 and is the interface-pass row
   again, which moved after item 34 later the same day and is now `v0.7.x`
   (`PL-PHKP`); see the note above for the measurement that reversed it, and for the
   styling-layer question this port deliberately leaves open.
4. **The two checks that read the theme** (queue items `PL-BXB2`, `PL-V53R`
   and `PL-0PJG`; moved into the slot 2026-09-19, when `PL-HWW1` made a
   declaration the record of membership - the three are the re-pointings this
   entry describes and the three the release stamped `v0.4.26`).
   `tools/contrast_check.py` and
   `tools/agent_identity_check.py` both read `theme.py` and
   `simulation_view.py` by path until 2026-09-14. `PL-JRS3` measured what a
   port does to them (2026-09-14) rather than reasoning it: `contrast_check`
   read values and failed loudly when a module it named moved or a colour it
   knew disappeared, but a colour declared in any *other* module was measured
   by nothing (`PL-BXB2`); `agent_identity_check` keyed on one method name in
   one file, so a class moving out of it was outside both rules, and it
   printed "none of them rendered disabled" from an empty measurement set
   (`PL-V53R`, `PL-0PJG`). The Qt view is built decomposed from the start, so
   both re-pointings landed before the first port commit rather than with it,
   done 2026-09-14: each reads every module under `app/` and names none by
   path, and an empty measurement set is an error.
   `PL-NGF7` is the other, and the port *dissolves* it rather than fixing
   it - see § "Items this port moots or transforms" below, and Gate 1's
   own disposition of it.
5. **Packaging and dependencies** (queue item `PL-3SQT`). PySide6-Essentials,
   pyqtgraph and numpy enter; `flet` and `flet-charts` leave. numpy arriving under a plotting
   library reopens the scope of `docs/WORKING_NOTES.md`'s "Decided: no numpy"
   rather than contradicting its conclusion, and that note is re-argued rather
   than cited either way.
6. **Headless rendering tests** (queue item `PL-YCWZ`), which is what `PL-2QMK`
   has been waiting for and what makes the rest of `presentation-safety`
   workable. With this port ahead of v0.5.0 it also means `PL-8PSW` is the first
   large display this project builds with a rendering check in place rather
   than after one.
7. **Deletion** (queue item `PL-7SVX`). The Qt spike tree goes, and so does
   every Flet import. `PL-C92D` retires the Flet frame-cost table that predates the port.
8. **The queued fixes named below** (queue items `PL-3355`, `PL-Q4VH`,
   `PL-THXF`, `PL-W8DQ`, `PL-TG60` and `PL-005`), on the rule stated there.
   The six moved from this sentence into the declaration slot on 2026-09-19,
   which is where `PL-HWW1` put membership; they are named here and
   not only under that heading because `MilestoneStates.ships_with` reads
   `Required scope` and nothing else: it is what separates `blocked-by:
   <this milestone's version>` meaning *ships with this milestone* from the same field meaning
   *waits for it to be scoped*, which is the relation `PL-L09X` costed and
   the roadmap already carries rather than a field anyone writes twice.

### Fixes this port carries, and why that is not scope creep

**Asked by the project owner, 2026-09-10**: "if we already had things we needed
to fix, wouldn't it make sense to fix those as part of the port, and not just
reintroduce old bugs still needing fixed?" Yes, and the rule is narrow enough
to keep this a patch.

**The rule: a queued fix rides the port when the port rewrites the code the
defect lives in, and it changes nothing a learner can do.** Everything else
waits. That is not a taste judgment - it follows from what a port is. Porting a
known defect means deliberately reproducing it in code being written from
scratch, then rewriting the same lines again to fix it. The fix is cheaper
inside the port than either side of it.

**What it does not license.** New capability stays out, whatever its size,
which is what keeps § "Versioning decision"'s patch argument true. A defect in
`core/` or in the Flet-free modules stays out too - the port does not touch
them, so fixing one there is unrelated work wearing this milestone's name.

**The enumeration is the point.** "Parity with the Flet build" is this
milestone's checkable definition of done, and a port that also changes behaviour
cannot be diffed against the old build to prove nothing was lost. So every
carried fix is named here in advance, and parity means *identical except for
this list*. That is stricter than an unenumerated parity, not looser.

**Defects in the rewritten surface** - reproduce none of these:

- `PL-3355` - the readouts wrap their value onto a second line at some widths.
- `PL-Q4VH` - the percent axis is labelled at a different interval from the
  gridlines it rules.
- `PL-THXF` - the legend swatch is a solid bar for a trace that is dashed, so
  the legend misdescribes the chart it explains.
- `PL-W8DQ` - the four slider active tracks miss the WCAG non-text minimum.
- `PL-TG60` - six decimals printed on an exhaust integral good to three.
- `PL-005` - the startup window is full-screen rather than sized and centred.

**Decisions the port has to make anyway**, so they are made deliberately rather
than by default: `PL-YTX9` (whether a hidden trace keeps its legend entry),
`PL-CZFY` and `PL-Q4M4` (the elapsed-time readout reads in seconds while the
axis reads in hours), `PL-LL9Y` (the warning and alert colours against the
medical alarm-colour convention), and `PL-2K1R` (an interpretation disclaimer beside the use disclaimer, stating that the readouts and traces are modelled rather than measured - text the dashboard states, not a control a learner operates, so a decision rather than capability; project owner, 2026-09-14).

**`PL-16ZC` is out (project owner, 2026-09-10)**, and it is the case that shows
where the line is. A show/hide control for the clinical references and the
control marks is small, and it is squarely in the rewritten surface - but it is
a control that does not exist today, so it is new capability, and the rule
admits fixes rather than features. It stays a queue item on its own merits.

**It is nonetheless sequenced behind this port** (project owner, 2026-09-14, on
`PL-NR2K`), which is not a reversal of the line above but its consequence: a
fix in the rewritten surface rides the port, and a *feature* in the rewritten
surface waits for it, because either one written on Flet first is written
twice. Gate 1 § "Sequenced past v0.5.0, so not clearable before it begins"
carries the disposition and the reasoning. It is not in this milestone's
Required scope and does not ship with it; what it waits on is `PL-G59B`
landing, after which it is an ordinary queue item against the Qt chart.

### Items this port moots or transforms

Recorded because the cost of missing them is not a defect - it is work done and
thrown away.

- **`PL-B9PY`** was listed here on 2026-09-10 as work the port would throw
  away, and **that was wrong**. Gate 1 places it under "Cleared by v0.5.0
  itself", not ahead of v0.5.0: decomposing `SimulationView` so two runs render
  is what the branched-run milestone *is*, so it could not wait for a port that
  then shipped after it without deferring the MVP. **It landed on Flet on
  2026-09-14, before this port moved ahead of v0.5.0**, so the ordering question
  it raised is closed rather than re-opened: the decomposition exists and this
  port inherits it. The duplication is real and was the accepted price of
  shipping the MVP first. **What this port owes it is the shape, not the code**:
  the Qt view is built decomposed from the start, so `PL-B9PY`'s design is a
  required input to `PL-25KS` rather than a pass to redo. It is also the reason
  the move costs less than it would have a week ago - the shape the Qt view
  needs is already designed and already reviewed.
- **`PL-NGF7`** is a defect *of Flet*: every colour a control takes when
  Material disables it comes from the Material theme rather than from
  `theme.py`, so `tools/contrast_check.py` cannot reach it. Qt supplies no such
  theme, so the port dissolves the defect rather than fixing it. It is also
  placed ahead of v0.5.0 today.
- **`PL-F0L8`** asks what accessibility Flet's rendering backend can deliver.
  After the port the question is `QAccessible`'s, which is a different
  investigation against a different backend.
- **`PL-7J96`** ("nothing in this repository draws the interface") is what
  `PL-YCWZ` now does. **Decided for `PL-YCWZ` (project owner, 2026-09-13), and
  `PL-7J96` is `dropped` as superseded.** `PL-YCWZ`'s capability was demonstrated
  rather than assumed - the Qt spike rendered the interface offscreen inside the
  web container before the decision was taken - where `PL-7J96` would have built
  a Playwright renderer for the interface this milestone replaces. What that
  accepts is that the shipped Flet build gets no automated wrapping check before
  the port; the two defects `PL-7J96` records are filed and dispositioned
  separately, so what is given up is the gate rather than the fixes. Its Gate 1
  line stays written where the freeze put it, per § "The gate is a snapshot, not
  a moving target". `PL-MBP6` was blocked on it and is re-pointed at `PL-YCWZ`.
- **`PL-NC2P`** and **`PL-YMY7`** are coverage items over `app/main.py` and
  `app/simulation_view.py`'s Flet-construction paths - files this milestone
  replaces.
- **`PL-027`** confirms the per-frame slider write-back on a live Flet client.

**`PL-NGF7` is deferred to this milestone (project owner, 2026-09-10)**, and
the deferral is recorded in Gate 1's own section rather than only here, because
that gate is frozen and "The gate is a snapshot" requires a deferral to say so
and say why. `PL-B9PY` is not moved, for the reason in its entry above.

### Definition of done

- Every capability the Flet build has, the Qt build has. No learner-visible
  regression, checked against the readout labels, the hedges `PL-NV9W`
  requires, the MAC axis, both clinical references and the control timeline.
- `make check` green, including the two theme-reading checks re-pointed rather
  than passing vacuously.
- A headless rendering test asserts on the real interface, and `PL-2QMK` closes
  on it.
- `PL-GS3R`'s worst drawn departure re-measured at every rung of
  `TIME_BASE_LADDER` and recorded in `docs/MODEL.md`.
- `docs/ARCHITECTURE.md` describes the interface that exists.
- The Qt spike tree is deleted and no module imports Flet.

### Explicitly out of scope for v0.4.26

- **Any new learner-facing capability.** This release adds none, which is what
  makes it a patch - and it is the line the carried-fix rule below is drawn
  against, not an exception to it. **One item landed against this line and did
  not cross it**, at the project owner's direction: the two-run overlay is built,
  and `fork_at`, `fork_points_s` and `branches` have no caller outside
  `app/controller.py`, so nothing in the interface creates the second run it
  draws. The display shipped ahead of the capability it displays. The id and the
  reasoning are in § "Current baseline: v0.4.26" → "The comparison display landed
  early, and the patch survives it", deliberately rather than here: `docket next`
  reads this heading, so an id named under it is placed out of scope.
- **The branched run.** v0.5.0's bookmarks and forking are that milestone's, and
  this one does not touch them. **Its comparison *display* is the exception
  above**, drawn here rather than there so that the largest new visual surface in
  the project was built once, on Qt, in a container a session can look at -
  which is one of the three grounds this file already gave for moving the port
  ahead of v0.5.0.
- **Anything under `core/`.** The port's whole tractability rests on `core/`,
  `app/controller.py`, `app/formatting.py`, `app/chart_time_base.py`,
  `app/playback.py`, `app/wash_in.py` and `app/control_timeline.py` surviving
  untouched - `tools/import_boundary_check.py` enforces that boundary and the
  spike proved it by driving the real `SimulationController` with no adaptation
  whatever.
- **The schematic** (planned-milestone item 27, v0.8.0), which this makes
  affordable and does not begin.
- **The area system** (planned-milestone item 34, v0.6.0), which Required scope
  item 2 reserves for - nested splitters with inert handles - and does not
  build. Turning those handles live is that milestone's first step.
- **Flet's web target**, which is given up rather than reimplemented. Nothing
  ships it today.

## v0.5.0 - the case you can branch

**Its display half now builds on Qt (project owner, 2026-09-14, on `PL-RKWB`).**
The Qt port moved ahead of this milestone - § "Completed: v0.4.26 - the interface moves to
Qt" carries the decision, the count behind it and the three grounds - so
`PL-8PSW`, the two-branch overlay, and `PL-LPLD`'s bookmark list are built once,
on pyqtgraph, rather than on Flet and then again. **Nothing else about this
milestone moves.** Its goal, required scope, definition of done and out-of-scope
list are unchanged; its port-neutral spine - `PL-CTD7`, `PL-B8MK`, `PL-Z3W6`,
`PL-W7H9`, `PL-49R8`, and the durable halves of `PL-RD3B` and `PL-LPLD` - is
untouched by the port and ships on the schedule it had. The milestone still
keeps its number and its meaning: it is the release that crosses the branching
capability boundary, and the port crosses none.

**What this costs and what it buys, recorded so it is not re-litigated.** It
costs the MVP its place in the queue for the length of the port. It buys
`PL-8PSW` a toolkit a session can actually look at (`PL-2QMK`), unblocks two
`P1` `safety`-classed items that were waiting on the toolkit (`PL-GS3R`,
`PL-YVHK`), and makes it possible for Gate 1 to reach zero before the milestone
it gates begins, which § "Sequenced past v0.5.0" records as the structural debt
`PL-D143` named and could not pay.

### Goal

Make the comparison possible. v0.4.0 made one case observable — compressed
time, clinical units, a case-length axis — and a single curve teaches a curve.
What a single curve cannot teach is *why* it moved, because that needs a second
curve differing in exactly one thing. Stated as they stand on 2026-09-06, the
day this milestone was scoped, three gaps:

- there is no way to halt a run at a target, so the playback multiplier that
  made a twelve-hour case reachable is unusable for anything precise. A learner
  comparing gas-management strategies watches the clock and pauses by hand,
  which at 300x overshoots by minutes of simulated time, differs every attempt,
  and cannot be returned to;
- there is no way to take two managements from one point on a case. Building
  the case twice is the only route available, and the two runs then differ by
  everything that was not reproduced identically — which is the one thing a
  comparison must not do, because the learner reading it cannot see which
  differences they caused; and
- there is no way to display two runs at once. `SimulationView` binds one
  controller, and the readouts, the chart traces, the clinical references and
  the control marks each assume a single run behind them.

Underneath those sits a fourth, a debt rather than a gap: the run's sample
store is unbounded. `PL-011` was dropped on 2026-09-05 on the promise that the
score architecture removes that store rather than bounds it, and a comparison
holds two runs, so this is the milestone where the promise is kept or the debt
doubles.

The end state: a learner runs a case, marks the decision point, forks there,
manages the two branches differently, and reads both on one time axis — the
branch point marked, every curve attributable to the run and the settings that
produced it, and the pre-branch history identical between the two because it is
the same history rather than a reproduction of it.

**This milestone completes the MVP** as "What MVP means here" defines it: run a
case, branch it at a decision point, compare the two managements side by side.
It is a minor rather than a patch because it crosses a capability boundary the
four releases before it did not — the application comes to hold more than one
run, and asserts a relationship between them.

**It changes `core/`, and it changes what the numerical method can be asked,
not what it computes.** The exact matrix exponential landed ahead of this
milestone (`PL-GS5X`, pull request 376), and the score architecture below turns
a run from a sequence of applied steps into a closed-form function of its
control-input timeline. The governing equations, the parameters, and the exact
solution of them are unchanged; what changes is that a time in a run can be
answered without having stepped to it. That is what makes a branch's pre-branch
history *the same object* as its parent's rather than a reproduction, which is
the property item 12 requires and the property a test can most easily be
written to pass for the wrong reason.

It promotes planned-milestone item 26 (bookmarks), item 12 (forking), item 11
(side-by-side comparison), and the replay half of item 8 — the resimulation
driver only. A user-facing replay control is item 10 and stays behind item 9's
save/load, which is out of scope here (project owner, 2026-09-06).

### Debt gate: the frozen list

**Frozen 2026-09-06, the day this milestone was scoped.** Every open item that
is debt by "The debt gate" below — classed `defect`, `safety`, `science`,
`refactor` or `perf`, or at `needs-decision` — is on this list. It is by a wide
margin the largest gate this project has held: Gate 0 held twenty-one and
v0.2.8's frozen scope thirty-eight. The size is stated in the group headings
below and in the timeline row naming this release, and `tools/doc_check.py`
holds those numbers to the list. How many are *closed* is deliberately not
recorded here, for the reason the v0.4.0 section gives: a count written into a
document goes stale the next time an item closes. `bin/docket wave` reads these
against `docs/items/` and reports the split.

**Three groups, and only the third is a precondition.** The first is the
`v0.4.x` track's own remaining work, which "The timeline" places *ahead* of
this gate and which ships as a patch rather than inside this milestone. That
looks like an exception to "A gate does not get a version" and is not one:
those items were already placed on an earlier step when this list was frozen,
and a gate frozen today cannot retrospectively claim a step the plan had
already passed to. The second is debt inside this milestone's own Required
scope, cleared by it per "Debt inside the milestone's own scope". The third is
everything else, and it clears before implementation of this milestone begins.

**Fifteen items were untriaged at the freeze, so the list could not decide
them.** An untriaged item has no `classes` yet, so nothing can say whether it
is debt, and freezing against the store means freezing against what the store
knows. That is a hole rather than an exemption, and "The gate is a snapshot"
closes it: each was captured *before* this freeze, so the problem each
describes was present at it, and any the triage pass classes as debt re-enters
this gate rather than waiting for Gate 2. The list below is the record of what
was decidable on the day; a re-entering item is added to it with the date and
the reason, exactly as v0.4.0's three post-freeze notes record theirs.

**The hole is closed, and it cost eight entries.** The 2026-09-06 triage pass
classed the eleven captures that were not this session's own, and eight of them
are debt: they are the sixth group below. Three - `PL-NBWP`, `PL-NBCJ` and
`PL-B1WW` - are `P1` `safety` or `science` findings about the step size, the
playback burst's control resolution and the reference gate's oracle, which is
the class of finding this rule exists to catch rather than defer. Of this
session's own four, `PL-QYPX` and `PL-3P2P` closed with the change that scoped
this milestone, `PL-D9GM` is `planning` and `PL-M26Q` is `infra` - a tooling
capability nobody has built, which "What counts" says explicitly is not debt -
so none of them adds to the list.

**How the third group is meant to be worked.** It splits almost evenly between
the two lanes `docket.toml` declares, and the two halves share no files, so
they run concurrently in two sessions rather than in series — which is what the
lane split was built for. The product half is also ordered against the work:
much of it names `app/controller.py`, `core/` and `docs/MODEL.md`, which
`PL-T691` restructures, so clearing it *after* that restructure would mean
re-diagnosing each item against code that had moved. That is the exact cost
"The debt gate" opens by naming, and it is the reason this list was frozen
whole rather than narrowed (project owner, 2026-09-06).

**Reconciled 2026-09-19 (`PL-C4RS`).** Three entries sat under headings saying
the opposite of what the milestone's own scope said of them, and § "Debt inside
the milestone's own scope" makes `Required scope` the test, so the document
gave two answers to a question it says has one. After this pass,
the three ids below now sit under headings that agree with `Required scope`,
and each placement is stated rather than implied:

- `PL-2FM6` (delete `RunHistory`) and `PL-8LXM` (delete the M4 decimation
  path) are under "Cleared by the `v0.4.x` track, ahead of this gate", and
  they have left `Required scope`, which is what the note under that heading
  already recorded on 2026-09-08: "Required scope below drops to sixteen
  items". The entries were never removed, so the two structures had disagreed
  since. What v0.5.0 required of them, and that the patch track shipped it, is
  recorded in prose under `Required scope` instead, where it places nothing.
- `PL-GVXP` (separate the six chart traces by more than colour) is under
  "Cleared before v0.5.0 begins, the product lane" and is not in `Required
  scope`. It never was an entry there: it was cited inside the `PL-8PSW`
  entry's prose, and `PL-HWW1` made a declaration rather than a mention the
  record of membership on 2026-09-19, so the disagreement ended with the
  parse rather than with an edit.

**Cleared by the `v0.4.x` track, ahead of this gate — 7 entries**

**Two moved here from "Cleared by v0.5.0 itself" on 2026-09-08, and one added** (project
owner), and the reason is a measurement rather than a preference. `PL-4RBD`
was re-measured against the time bases the interface actually ships — its
`P2` banding rested on a 0.04 pp figure taken at a chart window removed four
releases ago — and at the 12 h base the MAC-bearing alveolar trace departed
from the run by 0.65 pp, **0.32 MAC**, drawn with nothing to say the shape
between plotted points was inferred. It is now `P1`, `safety`. Its own fix
pins only the kink; the rest is ordinary curvature drawn as a chord across a
4 096-sample bucket, which no selection of recorded extremes can reach. So
the sampler had to arrive for the safety item to close properly, and
`PL-2FM6` came forward with it. `PL-T691` and `PL-P1Z3` had already shipped
in v0.4.8 under the same group heading, so this continues that rather than
breaking a line. Required scope below drops to sixteen items. The gate total rises by two, for
`PL-ZX12` and `PL-GS3R`: `PL-2FM6` and `PL-8LXM` moved between groups rather
than joining.

- PL-9SH6 (M) Give the partial-pressure-equivalent fraction one accessor name across every compartment in core/
- PL-X2XX (M) doc_check's citation check reads neither docs/items/*.md nor source docstrings, so nothing holds the queue's or the code's citations to the docs they name
- PL-VZL0 (S) Cite MODEL.md from every core/ function implementing a governing equation, and restate the solved form the spec lacks
- PL-2FM6 (M) Delete RunHistory and draw the chart from the closed-form sampler instead of from recorded samples
- PL-8LXM (M) Delete chart_downsampling.py, its tests, the M4 paper and every citation of them
- PL-GS3R (M) — **added 2026-09-08, `safety`.** The drawn chart's worst error
  moved from the control change to the steep early wash-in, and `PL-4RBD`'s
  0.32 MAC only fell to 0.26 MAC: uniform columns chord across the same width
  the old buckets did. Measured after `PL-2FM6` landed and so captured well
  after the freeze, but it re-enters this gate under the rule that admits a
  `safety` finding regardless of presence — and the problem it describes is
  older than the freeze, since the same chord error was in the number
  `PL-4RBD` was re-banded on. `needs-decision`: the three routes trade
  resolution against the frame budget, and choosing is the project owner's.
- PL-ZX12 (S) — **added 2026-09-08.** Rename RunScore to RunDefinition: 'score' is a
  metaphor a domain reader has to be taught, in the package that should read like
  the domain. Captured after the freeze, and it re-enters this gate rather than
  waiting for Gate 2 because the problem predates it: the module landed in v0.4.8.
  Sequenced after `PL-8LXM`, whose citation sweep opens the same documents, and
  before `PL-49R8`, whose rule file would otherwise be born carrying the retired
  term.

**Cleared by v0.5.0 itself — 8 entries**

- PL-T691 (L) The run is its control-input timeline: hold keyframes at every event and answer any window in closed form
- PL-P1Z3 (M) State the canonical evaluation rule that carries determinism once the step is no longer fixed, and gate it
- PL-Y5WR (M) The 30-day scenario cap is enforced nowhere as an explicit halt, and dropping PL-011 removes the only item that required it
- PL-1PSX (M) The control-input timeline is unbounded and regrouped in full on every frame
- PL-B9PY (M) Decompose SimulationView so two runs can be rendered at once
- PL-RD3B (M) app/controller.py holds the run's trace vocabulary and drawn window as well as the UI-to-core boundary, and they are separable
- PL-TCD1 (M) SimulationSnapshot still names six flat compartment floats, so the readouts cannot express a second substance now that the recorded run can
- PL-YDKJ (S) Decide whether the chart should keep patching one control per plotted point

**`PL-YDKJ` is here as a consequence of `PL-2FM6`, not as a nineteenth Required-scope
entry** (moved 2026-09-08, `PL-YXXG`). It was in the product lane above, which asked for
the decision *before* v0.5.0 begins, while `PL-2FM6`'s brief says it "should be decided
after this lands rather than before - the point-movement rate is its main input, and this
item changes it", and `PL-2FM6` is in this group. `PL-YDKJ` is also a sizing question -
its own closing note reduces it to `2 * P^2 * T / window_seconds` in the drawn point count
and how often those points change, both of which `PL-2FM6` replaces - and its own trigger
condition ("answer it only when a scale, a trace count or a render cadence is actually
blocked by the ceiling") is unmet. It now carries `blocked-by: PL-2FM6`, so no check has
to re-derive the edge from prose. Required scope below stays at eighteen items; the gate
total stays at 132.

**Cleared before v0.5.0 begins, the product lane — 39 entries**

- PL-6Q8N (M) The reference adult's eleven physiologic parameters have no primary source at all
- PL-HB58 (M) Validate washout against the same published cohorts the wash-in gate already uses
- PL-4GN8 (S) The mass-balance release gate's absolute tolerance tracks whichever dial its test happens to run at
- PL-GYH2 (S) Bound or document the two gas volumes, which no supported range covers
- PL-L2F2 (S) The fixed-volume alveolus blocks nitrous oxide, not just omits it
- PL-BLHV (M) Record the intended-use statement and the IEC 62304 safety classification in docs/MODEL.md
- PL-FDBK (M) docs/MODEL.md has no hazard table, so every mitigation is argued forward and none is checked backward
- PL-KGNF (M) docs/MODEL.md still names sevoflurane specifically in section headings and Purpose, four releases after three agents shipped
- PL-WVSK (M) Nothing distinguishes a concentration fraction from a percent at the type level, and two boundaries convert implicitly
- PL-0NQ1 (S) The reference patient's cited sources disagree on vessel-rich perfusion
- PL-11YF (S) MODEL.md says the readouts sit in one row without saying above what width
- PL-3355 (S) The 'Simulated time' and compartment readouts wrap their value onto a second line at some window widths
- PL-4RBD (S) The drawn chart smooths through a control change that leaves the trace monotone, because M4 selects extremes and such a change is not one
- PL-8PZ1 (S) docs/MODEL.md's release gate is still headed 'Version v0.1.0 is complete only when', but entries are being added to it for v0.3.0
- PL-B32L (S) core/parameters.py raises OSError and JSONDecodeError outside the exception hierarchy its own docstring promises
- PL-C4PH (S) — **dropped 2026-09-08** (project owner). Record the history
  sampling cadence as a decision of its own, separate from the integration step.
  Superseded by `PL-2FM6`, which deletes the store that has a cadence; after it
  lands there is no recording cadence to state and `SIMULATION_STEP_S` plays one
  role again. Its durable half — the owner's 2026-09-05 chart-faithful-only
  decision, recorded nowhere else — is transplanted into `PL-2FM6`'s **Done when**
  and held there by a `verify:` grep. Counts as cleared, so the gate stands at 132
  entries, 44 cleared. `PL-4RBD` is deliberately **not** dropped with it.
- PL-DXQC (S) The v0.4.0 Goal section states two problems in the present tense that are now fixed
- PL-F5GN (S) The oracle's independence check walks only ImportFrom, so a plain import bypasses it
- PL-GVXP (S) Separate the six chart traces by more than colour, and meet contrast minima
- PL-GZP6 (S) Two of docs/MODEL.md's required tests are not implemented
- PL-LKCN (S) Pin PL-010's no-rebuild property with an allocation test on the render tick
- PL-Q4M4 (S) The simulated-time clock reads in seconds while the chart's own time axis reads in hours and minutes
- PL-Q4VH (S) The compartment chart labels its percent axis at a different interval from the gridlines it rules
- PL-X204 (S) require_valid_agent_accounting() reads nothing from self, so it will judge a result from another accounting period
- PL-YK2V (S) _apply_setting catches a narrower exception class than the timer paths, so an unexpected raise escapes into Flet's dispatch
- PL-16ZC (M) The two clinical references and the control marks have no show/hide control, though the chart's traces now do
- PL-F0L8 (M) Establish what accessibility Flet's rendering backend can actually deliver
- PL-WZVZ (M) 'Make an inter-machine difference attributable: which parameter differs, and what it does to the result'
- PL-0SHZ (S) README's bare-interpreter paragraph names two ruff.toml pins and there are now three, since .claude/hooks/ carries one too
- PL-4MHK (S) pyproject.toml's package metadata does not describe the project - a vague description and no classifiers
- PL-6194 (S) 46 redundant parentheses around bare keyword-argument values across src/, from the initial build
- PL-79YX (S) Six exact float-equality branch guards in core/ are correct and nowhere explained
- PL-BTSW (S) README.md was edited on 2026-09-05 despite the freeze, and the edit left an unwrapped line
- PL-KCWD (S) APP_VERSION falls back to 'unknown' in the one line tying a displayed value to the model that produced it
- PL-LL9Y (S) Check the warning and alert colours against the medical alarm-colour convention
- PL-QM5P (S) README.md's description of doc_check candidates still says it prints lines mentioning anything the diff touched, which PL-B2NS narrowed to code mentions
- PL-TCW5 (S) FLOW_FRACTION_TOLERANCE is defined twice, so the two perfusion-sum guards can drift apart silently
- PL-TG60 (S) Stop printing six decimals of an exhaust integral good to three
- PL-YTX9 (S) Decide whether a hidden compartment trace should keep its legend entry or vanish from the legend entirely

**Cleared before v0.5.0 begins, the workflow lane — 49 entries**

- PL-7QKY (M) The working-notes discovery instruction is circular - a session must read the whole file to learn whether its task touches one of its threads
- PL-8M8H (M) docket branch tells a session whose pull request already merged to merge the base in, not to restart, so the push that loses work looks correct
- PL-NBCS (M) docket next reads an exclusion written inside a Required scope bullet as membership, so PL-B9PY is ranked in scope for v0.4.0 when ROADMAP.md sends it to Gate 1
- PL-PGZK (M) docket concurrent's answer is dominated by docs/MODEL.md, which nearly every item touches, so it rules out almost everything and cannot discriminate between real and nominal contention
- PL-XLQ5 (M) The orphaned report counts a branch's superseded intermediate blob as work the squash left behind
- PL-20CQ (S) "docket check runs every open item's verify: command, so a verify: that invokes docket check recurses without bound"
- PL-39B7 (S) Make docket stranded distinguish a merged-and-deleted branch from an abandoned one, and say when its main is stale
- PL-4WQS (S) The docket summary and session digest label a count 'open' that excludes untriaged items, understating the queue by exactly the number beside it
- PL-CW14 (S) The top-band advisory tells a session to demote work docket check itself pins to P1
- PL-D188 (S) A brief written into an untriaged item is appended below docket new's template rather than replacing it, so the dead stub survives to triage
- PL-F4JS (S) bin/docket triage omits the **Decision needed.** requirement from the rules it prints, so triaging an item to needs-decision fails check after the edit
- PL-GBBZ (S) Clear the four undeclared prose prerequisites the new advisory names
- PL-GJDW (S) contrast_check's requirement descriptions cite simulation_view line numbers, and all eight are wrong
- PL-HKF4 (S) doc_check's tag advisory prints `<merge commit>`, which a shell reads as redirection, so pasting it fails with "no such file or directory: merge" instead of tagging
- PL-JBZK (S) docket.toml's workflow_paths names three tools tests by path, so the other seven and every new one fall on the product side of the lane boundary
- PL-JL2M (S) docket new seeds a template brief that a later-written brief appends to rather than replaces, leaving empty required headings that block triage
- PL-JSRH (S) A closed item's closed: and milestone: are records too, and nothing stops a branch rewriting either
- PL-K2C8 (S) The docket skill's stranded-branch recovery deletes only the local remote-tracking ref, which the next non-prune fetch restores while the branch still exists on the remote
- PL-KBD0 (S) A blocked-by edge with no status blocked is invisible to the ranking, which is the same silent wrong answer one step along
- PL-KD98 (S) bin/docket wave reports 'implement' for a milestone whose Required scope is complete, because the beat reads only the frozen gate list and never the scope's item ids
- PL-MGF9 (S) The process-work grooming advisory only examines the top band, so it cannot fire for the P2 and P3 bands where all the process work actually sits
- PL-N2X4 (S) Hold tools/contrast_check.py's line citations to the file, or drop them
- PL-NB4D (S) '`docket verify` reports "1 commit(s)" when the work it just checked is entirely uncommitted'
- PL-S5LB (S) _number_closing walks git log without rename detection, so an item whose file was renamed after it closed recovers the renaming commit's pull request instead of its own
- PL-WGXJ (S) apparatus-standard.md structurally exempts the apparatus from the expert-review standard, so the largest part of the tree has no review bar
- PL-YDL6 (S) An item whose work landed in one pull request but whose status done was written in a later one recovers the later number, which carries the closure but none of the work
- PL-YNCW (S) docket new --touches before the title swallows it, because nargs='*' is greedy and the error names the title instead
- PL-7790 (M) A session that starts an item by pushing only queue-file edits stakes no claim docket next can see
- PL-B73C (M) Decide whether docket flight and the digest should name unlanded refs carrying no item id at all
- PL-VV4D (M) Decide whether the left-behind check should compare against refs/pull/<n>/head, which is exact but makes the check GitHub-specific
- PL-01CK (S) The in-flight content test walks the default branch's history once per blob a candidate branch adds
- PL-3833 (S) An item file's name can drift from its title and nothing checks it, so the store carries a stale slug until some unrelated rewrite happens to fix it
- PL-BZCM (S) docket status shows no plan placement, so the feature survey a session leads with cannot say which work the current step includes
- PL-GNN1 (S) The contrast checker cannot express a requirement met by either of two channels
- PL-GVNS (S) docket.toml's workflow_paths lists docs/worker.md but not docs/maintainer.md, so an apparatus item whose record lands in the maintainer doc ranks in the product lane
- PL-H1JD (S) An outstanding needs_action is lost when its session is archived, so a request nobody acted on drops out of the closing-block read
- PL-J7C5 (S) Cite symbols rather than line numbers in the contrast table's reasons
- PL-JQVB (S) CLAUDE.md's four dispositions for a new rule list no carrier for a paste-able brief or an agent definition, and a skill's resident cost is invisible to measure_resident
- PL-KJ63 (S) doc_check reads any double-quoted phrase in a doc as a section citation, so quoting a measured figure hard-fails the check
- PL-MHQK (S) The contrast checker prints its known-shortfall detail on every run, where the verify advisory was narrowed to what a session is about to trip over
- PL-PMT7 (S) Memoize branches_in_flight so cmd_next and cmd_digest stop computing _flight twice per invocation
- PL-R6D8 (S) git log --source does not attribute a shared commit to the ref named first, and _unmerged_commits' docstring says it does
- PL-S2L4 (S) bin/docket delegable offers items that docs/worker.md forbids a worker to touch
- PL-V4LS (S) docket check recovers a merged pull request number and then asks a human to transcribe it, which is a decidable half left as prose
- PL-VFVW (S) docket feature draws a dropped item with the same empty checkbox as an open one, so counting the boxes disagrees with the 'N left' figure printed beside them
- PL-VP40 (S) docket verify reads per-commit patches, so a line a branch added and then removed still reads as added
- PL-W1LN (S) The in-flight walk guard cannot catch a false positive whose walk ends against a commit the base reaches by another path
- PL-WTQ1 (S) doc_check's math-rendering check reads a regex in an item's verify: command as LaTeX and hard-fails
- PL-Z0G0 (S) doc_check candidates attributes a hit to the alphabetically first matching term, so a line matched through render.py prints as (render)

**Cleared before v0.5.0 begins, reaching both halves — 9 entries**

Neither lane can take these to completion on its own, so each wants a session
that can hold the whole change.

- PL-1JDD (M) Make the source tier machine-readable so doc_check can decide it
- PL-028F (M) Work that lands between a release cut and its merge is inside the tag's span but absent from the release notes, and nothing reconciles the two
- PL-7J96 (M) Make the interface renderable in a check, so a presentation change can be looked at
- PL-8XPQ (M) Nothing checks that an interface string uses glyphs the Flutter client can actually draw
- PL-3MJH (S) CLAUDE.md's capture rule exempts a finding fixed in the same session but gives no session a way to enter that exemption, so every trivial fix becomes a queue item
- PL-4YY1 (S) Record provenance for the circuit volume and default fresh gas flow
- PL-K2YF (S) ROADMAP.md's release narrative skips v0.2.6, so the convention that each release adds a paragraph has already been missed once
- PL-GLBF (S) ROADMAP.md's subset counts - not-delegable, entries reaching into src/ - are still hand-maintained and unchecked
- PL-W8DQ (S) The four slider active tracks use ACCENT and miss the non-text minimum

**Added 2026-09-06 under the presence rule — 8 entries**

The 2026-09-06 triage pass classed the eleven captures that were untriaged when
this list was frozen the same day. Eight are debt, and every one of them
describes a problem that existed at the freeze and was merely undecidable then,
so they re-enter this gate under "The gate is a snapshot" rather than waiting
for Gate 2. None is inside this milestone's Required scope, so all eight clear
before implementation begins. Five sit in the product lane or reach both
halves, three in the workflow lane.

- PL-NBWP (M) app/playback.py claims a faster playback is 'never a modelling one', but the uninterruptible tick burst makes control resolution multiplier x 0.1 s - 30 s at 300x
- PL-NBCJ (S) Decide whether MAXIMUM_SIMULATION_STEP_S should move to 0.05 s so an abrupt manoeuvre's timing stays inside one parameter SD
- PL-74R0 (M) core/ still holds four compartment-level advance methods that the coupled step no longer calls
- PL-R460 (M) The exact step costs 27 us against the split's 18 us per step at held settings, and 1.2 ms on every settings change
- PL-5TRV (M) bin/docket stranded calls an open pull request's branch merged-and-abandoned when another PR independently wrote the same docket record pr: lines, and its recovery would discard the branch
- PL-B1WW (S) The reference gate's oracle step is not converged during a transient, so 86-99.8 percent of what it reports is the oracle's own RK4 truncation rather than the shipped step's error
- PL-RC0M (S) "A blocked item's verify: command is never replayed, so it can rot unnoticed and redden whichever pull request unblocks it"
- PL-1KTV (S) docket.toml counts .github as the workflow lane but apparatus-standard.md's paths do not, so 500 lines of workflow comments sit under the simulator's standard by default

**Added 2026-09-06 after `PL-NBWP` closed — 2 entries**

The two captures `PL-NBWP`'s own session left behind, triaged 2026-09-06 once
it had merged. Both are classed `safety`, so they re-enter under the second of
"The gate is a snapshot"'s two unconditional exceptions rather than under the
presence rule - which matters, because the presence answer differs between them
and the `safety` answer does not. `PL-X35V` describes a deficiency that predates
the freeze: the interface has never stated what a rate costs in control
resolution, and `PL-NBWP` only made it nameable. `PL-ZVS7`'s subject is new,
because the table it asks to pin is one `PL-NBWP` wrote. Neither is inside this
milestone's Required scope, so both clear before implementation begins.

- PL-X35V (M) The playback-rate control does not state the control resolution its rung costs, so the PL-NBWP disclosure reaches only a reader who has docs/MODEL.md open
- PL-ZVS7 (M) docs/MODEL.md's control-resolution tolerance table is a measured safety claim with no regression test; re-measuring it 2026-09-06 reproduced it, but nothing would have caught a drift

**Added 2026-09-07 under the unconditional safety/science exception — 11 entries**

Eleven items classed `safety` or `science` filed between the 2026-09-06 freeze
and 2026-09-07. They belong here whatever their presence answer, under the
second of "The gate is a snapshot"'s two unconditional exceptions and step 4 of
"The cadence", which state the same rule. None is inside this milestone's
Required scope, so all eleven clear before implementation begins. Nine sit in
the product lane and two reach both halves; nine are `science`, and eight of
those declare `docs/MODEL.md`, so they order against one another rather than
running eleven ways at once - a shared file is sequencing rather than
contention, per the tiering `PL-VRMK` added to `bin/docket concurrent`.

**Four further `safety`/`science` items from the same window are deliberately
not here.** `PL-1XPX`, `PL-CTD7`, `PL-W7H9` and `PL-Z3W6` are placed in this
milestone's own Required scope below, so they clear *with* the milestone rather
than before it - the distinction the "Cleared by v0.5.0 itself" group above
draws.

**That none of the eleven was recorded for two days is `PL-KTKP`.** The
procedure existed and had been run twice on the freeze day itself, in the two
groups above; what was missing is anything that reconciles the queue's classes
against this list. So `bin/docket wave` reported 84 open of 121 - arithmetically
correct against what was written, and omitting every open `P1` the project had,
because `docket check` pins `safety` and `science` to the top band and this list
therefore held none of them. `tools/doc_check.py` now raises an advisory naming
any open `safety`- or `science`-classed item this section does not place, which
is the decidable half; which of the three dispositions an unplaced one takes
stays a reader's judgment.

- PL-CXYT (S) docs/MODEL.md does not say whether fresh gas flow includes the vapor the vaporizer adds
- PL-WT07 (S) docs/MODEL.md says the ventilator start binds the per-rate displacement table 'throughout', but at 300x it leads the unperfused load by only 3% (10.36 vs 10.03 pp) and 'throughout' reads as a comfortable margin
- PL-5K5C (M) Record the model's sea-level assumption and the vaporizer-class dependence of the delivered-concentration dial
- PL-7HDS (M) Read Lowe and Ernst 1981, the upstream the Gas Man Workbook names for its volume and flow values
- PL-YKSM (M) Lowe and Ernst's cardiac output is allometric (0.2 x M^0.75 = 4.84 L/min at 70 kg), not the stored fixed 5.0, and weight_kg is still read by no equation
- PL-ZP7Z (M) The Workbook attributes the volatile partition coefficients to Yasuda's Anesthesiology abstract and to Abbott package-insert data, which is not what the agent files say
- PL-73G7 (M) Explain desflurane's opposite-sign washout disagreement once rebreathing is removed
- PL-W21J (M) Give the elimination comparison a test-only open-circuit driver, so washout can be validated rather than only measured
- PL-8PS6 (M) Fresh gas flow range is a machine property held in supported_ranges.py, not a global constant
- PL-XJ5P (M) Citing-sources says there is always a route, but a pre-abstract subscription paper has none and docs/references can no longer hold one
- PL-61WW (M) During a run, the agent name in the agent selector loses contrast against the agent colour

**Added 2026-09-08 under the presence rule — 17 entries**

The 2026-09-08 audit (`PL-36R4`) applied the presence test to every open item
this list and the Required scope below both omit: forty-two of them, all filed
on or after the freeze day, none previously placed and none previously
declined. That silence is the one disposition "The gate is a snapshot" forbids
by name, so each owed a decision either way.

**Thirteen are admitted, and the boundary is `docket.toml`'s own** (project
owner, 2026-09-08). The ten in the product lane and the three reaching both
halves come in; the twenty-nine wholly in the workflow lane are declined
below. That split is a fact in the files rather than a judgment re-made per
item — the same `workflow_paths` reading that separates two sessions — which
is what makes it reviewable. None is inside this milestone's Required scope,
so all thirteen clear before implementation begins.

**The fourteenth arrived after that audit, and is admitted for a reason of its
own** (2026-09-08). `PL-QXSB` asks whether the interface should stay on Flet,
and it qualifies for presence on the exception "The gate is a snapshot" states
for a late finding: the problem it describes long predates the freeze —
`PL-001`, `PL-010`, `PL-0VM7` and `PL-Q197` are all attempts on it — and only
the measurement that closes off the routes inside Flet is new. It sits in the
product lane, so the ground the twenty-nine below are declined on does not
reach it.

It is admitted rather than merely qualifying, though, because of what this
milestone is: v0.5.0 puts a **second chart** on the screen for a branched run.
The cost `PL-QXSB` names is charged per control present per frame, so the one
milestone whose defining feature doubles the interface is the one that should
not begin without an answer. The answer may well be "stay" — the item says so
— and that answer takes a reply rather than a migration.

**Its three consequences come with it** (2026-09-08). `PL-55DH` builds the
throwaway PySide6 spike, `PL-X9T3` runs it on hardware this container does not
have, and `PL-JRS3` establishes what a port would cost the two checks that read
`theme.py` — which would otherwise *pass* on a tree they no longer describe,
the failure mode `PL-20PT` had just been fixed for. They are on the list rather
than merely near it for the same reason `PL-QXSB` is: they are how it gets
decided, so a gate holding the decision and not its evidence would hold
nothing. `PL-JRS3` is the one that could stop a port cheaply, which is worth as
much as the two that would start it.

- PL-0Q1T (S) The new-case dialog leads its carry-over list with circuit volume, the one entry in it a user cannot set, and it is now the interface's only mention of the parameter
- PL-3PRZ (M) The agent-accounting guard catches an absurdly small alveolar volume at 1e-9 L but stops catching it by 1e-300 L, where the run returns a concentration of exactly zero with accounting passing
- PL-8GV5 (M) Decide whether the model should represent anaesthesia's own effect on cardiac output and regional perfusion, which it currently holds fixed
- PL-B9VL (S) Rename the wash-in validation module and its MODEL.md section now that both cover elimination too
- PL-CZFY (M) The elapsed-time readout states seconds, so a run at the newly declared 24-hour limit reads '86400.0 s' - seven characters of tenths on a quantity a reader thinks about in hours
- PL-F9TQ (S) PL-6580 strips only the concentration chart, but the wash-in panel's two paragraphs are the largest standing prose block on the screen and no item covers them
- PL-L7JB (S) docs/MODEL.md names the mass-balance tolerances MASS_BALANCE_ABSOLUTE_TOLERANCE and MASS_BALANCE_RELATIVE_TOLERANCE, but core/ calls them AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L and AGENT_ACCOUNTING_RELATIVE_TOLERANCE, so a reader grepping the documented name finds nothing
- PL-THXF (S) The trace legend swatch is a solid bar for a trace that is dashed, so the legend's own redundant channel is words only
- PL-WSDY (S) ROADMAP.md's current-baseline section hardcodes 'Gate 1 remains open at 92 of its 121 entries', which the gate section's own convention forbids and which is now wrong twice over
- PL-XF89 (S) README's opening says inhaled-anesthetic where the About field and pyproject say volatile - decide which scope word the project's one-line self-description uses
- PL-2CS8 (M) Nothing carries roadmap item 24's stated prerequisite: the display constants are scattered across theme.py, simulation_view.py and duplicated core/app defaults, with no item to consolidate them
- PL-36R4 (M) Forty-two presence-qualifying items carry neither a gate placement nor a recorded deferral, which is the one disposition ROADMAP's presence rule forbids
- PL-NGF7 (M) tools/contrast_check.py can see no disabled-state colour, because none of them is a constant in theme.py
- PL-QXSB (M) Decide whether the interface should stay on Flet: every route inside it has now been measured, and the remaining lever is fewer controls
- PL-55DH (M) Build the PySide6 + pyqtgraph spike: the concentration chart and the readout row behind the existing controller, disposable and touching no shipped app/ module
- PL-X9T3 (S) Run the Qt spike on the project owner's own machine and record frame cost, input latency and how it looks, which is the half no session here can measure
- PL-JRS3 (S) Establish what a Qt port would cost the checks that read theme.py: contrast_check and agent_identity_check would pass silently on a tree they no longer describe

**Added 2026-09-10 under the unconditional safety/science exception — 1 entry**

`PL-LT51` was filed on 2026-09-10 out of `PL-8SDL`, which identified the four
references Lowe and Ernst cite for the reference patient's organ volumes and
blood flows. It is `science`-classed and so re-enters this gate whatever its
presence answer, under the second of "The gate is a snapshot"'s two
unconditional exceptions. It is not inside this milestone's Required scope, so
it clears before implementation begins.

**It is admitted rather than deferred, and the reason is that it has twice been
shown to be closeable.** The obvious argument for deferring is that no session
can close it: it needs three 1960s and 1970s papers that PubMed holds no
abstract and no full text for, and the egress proxy refuses every publisher.
That argument does not survive the evidence — the project owner turned around
two interlibrary loans in three days for exactly this chain (`PL-7HDS` on
2026-09-08, `PL-8SDL` on 2026-09-10), and reference 26 was read on the day the
item was filed. Deferring it would shrink the gate on a claim the last week
disproves.

**What it has already established belongs beside the entry**, because it
changes what the remaining reading is for. ICRP Committee II's Table 8, page
151, is *Organs of standard man* — masses and effective radii, and **no blood
flows at all**. So the perfusion fractions, which set every time constant this
model computes, cannot descend from the one non-model reference of the four.
They descend from references 9, 19 or 20, which are uptake-and-distribution
models. The chain from `reference_adult.json` therefore terminates at tier 2 in
both halves and reaches tier 1 nowhere.

- PL-LT51 (M) Obtain and read Lowe and Ernst's four upstream references for the reference patient's volumes and flows, starting with ICRP Committee II page 151

**Added 2026-09-12 under the unconditional safety/science exception — 7 entries**

Found by the triage pass that took the queue from 46 untriaged captures to
none (`PL-3B47`), with a seventh added later the same day and explained at the
foot of this group. All seven are `safety`- or `science`-classed, so they
re-enter this gate whatever their presence answer, under the second of "The gate
is a snapshot"'s two unconditional exceptions. None is inside this milestone's
Required scope, so all seven clear before implementation begins.

**Four are the specification disagreeing with the tree it describes**, which is
the class this exception exists for: a reader consults `docs/MODEL.md` to decide
whether to trust a displayed value, and each of these tells them something the
shipped files no longer support. `PL-7KDC` and `PL-S3Q0` are both fallout from
`PL-8ZJQ` adopting Davis and Mapleson for the venous pool - the first leaves the
paragraph that counts what the parameter set rests on saying all eleven values
are Gas Man's, the second leaves two notes asserting that a tier-2 source may
never be the authority for a stored value, which this project has now done.
`PL-Q5NS` is an omission from Known limitations worth about 20% of every agent's
fast pool. `PL-MMWX` is the same failure one document over: `ROADMAP.md` item 30
scopes weight as an input without recording that the scaling is only safe as a
coupled package, and a session scoping it from the item alone would ship
paediatric kinetics wrong in the most-taught direction.

**`PL-RFLN` is admitted rather than deferred on the same evidence as `PL-LT51`
above.** It needs the methods sections of two 1991 papers neither PubMed Central
nor `docs/references/` holds, which reads like a reason to defer - and the last
week disproves it, the project owner having turned around three interlibrary
loans for exactly this kind of chain. What it asks of a session is bounded:
name the cause against the methods, or record that the question is unanswerable
from what this project can reach and say so in place of the two open candidates.
**Closed 2026-09-13 the second way**, and one candidate further than that: the
methods were read, the apparatus excluded, and end-tidal sampling struck on
Carpenter & Eger's measurement of the gradient it rests on. Only the published
value is left, which nothing this project runs can settle.

**`PL-YLKR` is here for what the tooltip may imply rather than for what it
says.** What it says is a bare number - no unit, no compartment, no agent, and
nothing marking the quantity as modelled rather than measured. `PL-KP7H` made it
a paused-only affordance, which is precisely when a reader stops to study a
number instead of glancing at a trace: so the tooltip is the surface a reader
meets with the most time to draw a conclusion from it and the least context to
draw one from, and a modelled alveolar fraction read as a measurement is the
confusion `CLAUDE.md` names in terms. The design is toolkit-independent and
survives the port; only its implementation moves.

**The seventh is the paragraph immediately above** (`PL-DZFJ`, found by the
`PL-0QQP` triage pass, 2026-09-12; corrected 2026-09-13). Until that date the
paragraph argued `PL-YLKR`'s admission from a mechanism the tree no longer has.
It said every drawn point was an M4 representative of its bucket - roughly 120
recorded samples at 300x - and that the hover "presents it as the value at that
instant". `PL-2FM6` deleted `RunHistory`, `HistoryWindow`,
`SimulationHistorySample` and the M4 decimation module in v0.4.12, and the chart
now evaluates the run's score *at* the instants it plots, with a control event
always given its own column. So the hover presenting a point as the value at
that instant is correct rather than misleading, and the gate's stated reason for
admitting a `P1` `safety` entry was false in exactly the direction that made the
entry look necessary.

What survives the correction is the admission rather than the argument, which is
why this is a rewrite and not a removal. A bare number with no unit, compartment
or agent beside it is a presentation-safety matter whatever produces it, and a
correct number carrying nothing that marks it as modelled is a failure
`CLAUDE.md` names in terms - so the paragraph above now argues that, and
`PL-YLKR` stays. It is admitted on the same ground as `PL-MMWX` above: a wrong
statement in this document about what a displayed value represents reaches the
session scoping the work rather than reaching a user. `PL-YLKR`'s own brief
carried the same sentence into work whose declared `touches` are
`docs/MODEL.md`, `README.md` and the chart-series module, and was corrected with it.

- PL-7KDC (S) docs/MODEL.md's 'Where this project stands' paragraph still says all eleven reference-patient parameters are the Gas Man default patient and 26 of 29 rows are tier 3, though PL-8ZJQ moved venous_pool_volume_l to a tier-2 source
- PL-DZFJ (S) ROADMAP.md's gate text and PL-YLKR's brief say every drawn chart point is an M4 representative of a bucket of recorded samples, which PL-2FM6 deleted in v0.4.12 - the chart evaluates the score at the plotted instants
- PL-MMWX (S) ROADMAP.md's planned-milestone item 30 does not say that cardiac-output scaling is one of its obligations, or that weight scaling is only safe as a coupled package
- PL-Q5NS (S) docs/MODEL.md's Known limitations does not list lung tissue and pulmonary blood as an omitted store, which is worth about 20 percent of every agent's fast pool
- PL-RFLN (M) Settle what causes desflurane's five-minute washout residual, which PL-73G7 narrowed to end-tidal sampling or the published datum
- PL-S3Q0 (S) Two paraphrases of the tier-2 absolute survived PL-FJGY's sweep, in docs/MODEL.md's Kharasch note and reference_adult.json's Frayn and Karpe note
- PL-YLKR (M) Design what a chart tooltip says: fl_chart's default is a bare number, and PL-KP7H makes the tooltip a paused-only readout that a reader will actually stop and study

**Added 2026-09-13 under the unconditional safety/science exception — 4 entries**

Found by the triage pass over the fourteen captures open that day (`PL-TQJ4`).
`PL-V6M0` is `safety`-classed, so it re-enters this gate whatever its presence
answer, under the second of "The gate is a snapshot"'s two unconditional
exceptions. It is not inside this milestone's Required scope, so it clears
before implementation begins.

**What it is.** `PL-YK2V` widened `_apply_setting`'s catch so that anything
outside the project hierarchy halts the run, and the narrow arm it kept catches
`AnesthesiaSimulationError` — the base class. That is right for
`SimulationConfigurationError`, where a value was refused and nothing was
miscalculated, and it inverts the meaning of `SimulationExecutionError`, whose
docstring in `core/exceptions.py` says the run must stop rather than continue:
such an error would be reported to the reader as a refused setting, over a run
that keeps producing readings. `SimulationDomainLimitError` is the same shape
again, mislabelled as a refusal rather than as the run reaching the edge of its
supported domain.

**Why `anticipated` does not defer it.** No route raises either type into
`_apply_setting` today, which is why the item carries that class — but
`checks.py` grants the class its exemption from the band only at `status:
blocked`, and nothing blocks this one: the trigger is a future route rather than
a named item or milestone. The exemption is therefore unavailable, and an
unavailable exemption is not a reason to seat safety-critical work lower. It is
also this milestone that makes the anticipation concrete: v0.5.0 turns a run
from a sequence of applied steps into a closed-form function of its
control-input timeline, so a setting applied to a run that has already been
evaluated — the "applied by re-stepping" route the item names as the way in
— is newly in play here rather than hypothetically.

**The second arrived in the triage pass over the twenty-seven captures open
later the same day** (`PL-DJYF`). It is `science`-classed on the same reading as
its twin `PL-4YY1` (record provenance for the circuit volume and default fresh
gas flow), which is already on this gate and shipped in v0.4.20, so it re-enters
whatever its presence answer. `AlveolarCompartment` carries `gas_volume_l` and
`alveolar_ventilation_l_min` as dataclass field defaults while
`data/patients/reference_adult.json` stores both with their provenance, and -
unlike the circuit, which `PL-4YY1` pinned with
`test_the_bare_circuit_defaults_match_the_shipped_machine_file` - nothing holds
the two copies equal. A constant free to drift from the parameter set
`docs/MODEL.md` cites is a run on a value the specification does not name,
presented with provenance that looks correct, which is the class this exception
exists for. It is not inside this milestone's Required scope, so it clears
before implementation begins.

- PL-V6M0 (S) _apply_setting reports a SimulationExecutionError as a refused setting and lets the run continue, which is the opposite of what that type means
**Two more arrived from the Targ, Yasuda and Eger 1989 circuit paper**, read
at full text from the private corpus on 2026-09-13 and merged the same evening.
Both are `science`-classed and neither changes a displayed value; what puts them
here is the `PL-Q5NS` shape - the specification understating what is known, which
a reader consults it precisely to judge.

`PL-QBKQ`: `data/machines/reference_circle_system.json`'s `provenance_gap` says
a measured circle-system volume "has not been sought yet", and one has now been
read - 9.86 L by water filling, which does *not* close the gap because it
includes a reservoir bag simulating the lungs, and saying so is the work. Three
figures now sit in one order and only one is measured: this project's 6.0 L, Gas
Man's published 8.0 L, and that 9.86 L upper bound.

`PL-XWCY`: the same paper strikes circuit-wall absorption as a candidate for
desflurane's residual, and in the same measurement says a real circle system
measurably retards sevoflurane and isoflurane relative to ideal - a mechanism
this model has no term for, pointing at cohorts in
`tests/reference/test_published_wash_in_and_elimination.py` that already sit at
+3.79 SD and +4.15 SD. The strike is bookkeeping; the second half is a named,
quantified departure bearing on an existing discrepancy, which is why it is not
deferred with the apparatus.

Neither is inside this milestone's Required scope, so both clear before
implementation begins.

- PL-DJYF (S) AlveolarCompartment restates the reference patient's gas volume and ventilation as core/ dataclass defaults, the same restatement PL-4YY1 found on BreathingCircuit
- PL-QBKQ (S) The only measured conventional circle-system volume this project holds is 9.86 L including a simulated lung, against a stored 6.0 L and Gas Man's published 8.0 L
- PL-XWCY (M) Circuit-component absorption is ruled out as a cause of desflurane's residual by the one paper that measured it, and is a live candidate for the other two agents

**Added 2026-09-14 under the unconditional safety/science exception — 3 entries**

`PL-YVHK` is `safety`-classed, so it re-enters this gate whatever its presence
answer, under the second of "The gate is a snapshot"'s two unconditional
exceptions. It is written down here because that rule requires it to be, **and
it is the one entry in this block that does not clear before implementation
begins** - its disposition is in § "Sequenced past v0.5.0" → "Sequenced behind
the port", and the two statements are not in conflict: the presence rule
decides that a safety finding is recorded against the current gate, and the
snapshot rule decides that a recorded deferral is how it may then be sequenced
out of it. Silence is the third thing, and the only one forbidden.

**What it is.** It is the build half of `PL-YLKR`, split from it on the project
owner's decision of 2026-09-14. The design and its derivation landed on v0.4.x
- `docs/MODEL.md` § "The chart's hover readout: what the tooltip may show" -
and what remains is writing the hover against pyqtgraph, which cannot be done
before the toolkit exists. It carries `safety` for the same reason its parent
did: a number a reader stopped the simulation to look at, with nothing around
it to say the value is modelled rather than measured, is the
modelled-versus-measured failure `CLAUDE.md` names.

**`PL-2K1R` is the second**, found 2026-09-13 and triaged 2026-09-14 (project
owner): `P1` `safety`, an interpretation disclaimer beside the use disclaimer,
so that the compartment readouts and chart traces are stated to be modelled
rather than measured - the line `CLAUDE.md`'s safety standard draws on the
surface a clinician reads. It rides the Qt port behind `PL-25KS` (port the
dashboard) on the carried-fix rule, text on a dashboard rewritten from scratch
being written once, and clears before v0.5.0 begins like the five carried
entries; § "Sequenced past v0.5.0" below carries it in that table, and the
port names it under "Decisions the port has to make anyway" so its parity
claim stays checkable.

- PL-2K1R (S) The interface carries a use disclaimer but no interpretation one, so nothing tells a reader the compartment readouts and chart traces are modelled rather than measured
- PL-YVHK (S) Implement the chart hover readout on pyqtgraph to the derivation docs/MODEL.md now carries, turn hoverable on so the affordance is not silently lost, and say in README.md that it exists

**`PL-27H0` is the third**, and it is the same
modelled-versus-measured line drawn in the specification rather than on the
screen. `docs/MODEL.md` still tells a reader that every point drawn on the
chart *is a recorded sample*, selected from a per-step store; `PL-2FM6` deleted
that store, and `app/chart_frame.py` now says the opposite deliberately -
"Every drawn point is a state of the run at the instant it is drawn at,
evaluated from the run definition rather than selected from recorded samples".
What makes it `safety` rather than `docs` is that the sentence is about the
provenance of a displayed value, which `CLAUDE.md` names as a safety failure in
its own right, and that the numbers are correct throughout - which is what makes
it hard to notice. Unlike the two above it needs no toolkit and clears before
implementation begins.

- PL-27H0 (M) docs/MODEL.md still specifies a per-step recorded sample store and a display operation that selects which recorded samples a trace draws, both of which PL-2FM6 deleted

**Added 2026-09-14 under the unconditional safety/science exception and the presence rule — 4 entries**

Found by `PL-JRS3`'s pre-port survey and triaged the same day into
`feature: qt-port`, where § "Completed: v0.4.26 - the interface moves to Qt" → "Required
scope" item 4 already places the first three by name and its opening paragraph
names the fourth. All four land before the port's first commit, on the branch
that records them here, so they clear ahead of this gate by construction; they
are listed because the presence rule requires the disposition to be written
down, not because the gate's clearance changes.

- PL-BXB2 (S) — **added 2026-09-14, `safety`.** contrast_check reads only
  theme.py and simulation_view.py, so a colour declared in any other app/
  module is measured by nothing and missed by nothing. Captured after the
  freeze; re-enters under the exception, the check it repairs being the
  accessibility floor.
- PL-V53R (M) — **added 2026-09-14, `safety`.** agent_identity_check reads only
  simulation_view.py and keys on `_apply_agent_color_scheme` by name, so a
  class moving out of that module is outside both of its rules. Same
  exception, the ISO 5360 agent-colour guard.
- PL-0PJG (S) — **added 2026-09-14, `safety`.** agent_identity_check prints
  "none of them rendered disabled" from an empty measurement set, so the
  sentence cannot be told from the same sentence earned. Same exception, the
  same guard.
- PL-9KDK (S) — **added 2026-09-14.** tools/import_boundary_check.py confines
  no UI toolkit and no numpy. `defect`, so it enters under the presence rule
  rather than the exception: the tool shipped on 2026-09-04 with no toolkit
  boundary, two days before this freeze, and `CLAUDE.md`'s rule that it now
  measures predates both.

**Added 2026-09-17 under the unconditional safety/science exception — 3 entries**

All three were captured on 2026-09-16 or 2026-09-17 and triaged on 2026-09-17
(`PL-Y4D6`). They are `science`- or `safety`-classed and so re-enter this gate
whatever their presence answer, under the second of "The gate is a snapshot"'s
two unconditional exceptions. None is inside this milestone's Required scope, so
all three clear before implementation begins. Each is `S`.

- PL-S6WW (S) — **added 2026-09-17, closed 2026-09-17.** `docs/MODEL.md`
  § "Agent amount" stated that every compartment stores agent as an equivalent
  gas volume "at one documented reference temperature and pressure", documented
  the pressure, and documented no temperature anywhere — not in that file, not
  in `core/`, not in `data/`. `science`, and its presence answer was yes as
  well: the sentence had been wrong since long before this freeze. Resolved at
  **20 °C and 760 mmHg, dry** (project owner, 2026-09-17, ratified — over
  37 °C), on the reference implementation's own five expansion constants, which
  the 20 °C derivation reproduces within 0.35 % and the 37 °C derivation misses
  by 5.6–6.2 %. § "Known limitations" now records what one condition costs for a
  circuit at ambient and tissues at 37 °C, and sizes it.
- PL-H4N8 (S) — **added 2026-09-17.** Planned-milestone item 28 specifies agent
  cost "from the exhausted-agent amount", and cost is what left the bottle, which
  is the delivered amount. `science`. By the accounting identity `initial +
  delivered = exhausted + currently stored`, exhausted understates delivered by
  exactly what is still stored, and the gap is largest during wash-in — the phase
  the low-flow lesson is about. Gas Man bills delivered too (`Cost = DELIVERED
  Flow x Cost/mL vapor`, Workbook p. 174).
- PL-QBX0 (S) — **added 2026-09-17.** Planned-milestone item 24's gating sentence
  keeps `data/**/*.json` out of the preferences panel and so covers neither the
  three ISO 5360 agent-identification colours nor the contrast-checked trace
  palette, both of which `app/theme.py` holds. `safety`: a panel that let a
  reader recolour agent identification would let one agent display in another's
  colour.

**They are admitted rather than deferred, and the reason is the rule rather than
a judgment.** "The gate is a snapshot" ends by making `safety` and `science` not
deferrable, and `tools/doc_check.py` says so where a session would otherwise
reach for the declined subsection: a `### Declined to Gate ...` entry answers the
disposition advisory and leaves the re-entry one standing. The one carve-out —
an `anticipated` finding whose hazard a later milestone creates — needs `status:
blocked` with it, and `PL-KZ99` is the entry from this triage that takes it, so
it is recorded in the declined subsection with `PL-0S0V` and `PL-VJZK` instead.

**Two of the three describe a hazard that is not live, and that is a reason to
do them now rather than to defer them.** Neither a cost readout nor a
preferences panel exists, so nothing displayed today is wrong. What each item
fixes is a sentence in the planned-milestone entry that a later session would
implement from, which is the cheapest moment such a correction will ever have —
and is why both are `ready` at `S` rather than blocked on the milestone they
protect. `PL-S6WW` is the live one of the three: its sentence is false as
written in the document this project calls authoritative for units and
assumptions, and the other two rest on ground it settles.

**Added 2026-09-19 under the unconditional safety/science exception — 2 entries**

Both were captured on 2026-09-17 and triaged on 2026-09-19, in the pass that
seated nineteen of the store's twenty untriaged items. They are `safety`- or
`science`-classed and so re-enter this gate whatever their presence answer,
under the second of "The gate is a snapshot"'s two unconditional exceptions.
Neither is `anticipated`, so the one carve-out to that exception does not reach
them: the hover is live on the shipped chart today, and `docs/MODEL.md` is the
authoritative specification today. Neither is inside this milestone's Required
scope, so both clear before implementation begins. The eleven other debt items
that pass seated are declined below, all wholly in the workflow lane.

- PL-JVHL (M) — **added 2026-09-19, `safety`.** `nearest_trace_point` and
  `nearest_wash_in_point` keep the single globally nearest drawn point within
  `HOVER_RADIUS_PIXELS`, so with two runs on one axis the hover answers for
  whichever is marginally nearer and a 2 px hand movement swaps which run is
  read, silently. Measured 2026-09-17: both runs' points sit inside the radius
  across 100 % of the shared axis for the fat compartment under every branch
  management tried, and 43.8–81.4 % of the hovers that could answer for either
  would print different text — `0.03 %  0.02 ×MAC` against `0.01 %
  <0.01 ×MAC` at one worked instant, a threefold difference in stored fat
  between a run still carrying agent and one 48 minutes into emergence.
  `safety` under the standard's presentation clause: the correct number read
  against the wrong run is the wrong patient context. Its presence answer is no
  — a second run on one axis is this milestone's own capability — which the
  exception makes irrelevant. `PL-MN4J` naming the run in the box makes the
  swap visible rather than silent and is a large mitigation, not a fix.
- PL-7DMJ (S) — **added 2026-09-19, `science`.** `docs/MODEL.md` names water
  vapour nowhere. Alveolar gas is saturated at 47 mmHg, so agent arriving dry
  from the circuit is diluted by 47/760 — 6.2 % — before any uptake has
  occurred, and the alveolar equation carries $`\dot V_A(F_I - F_A)`$ with no
  such factor. Changing the equation is explicitly out of scope: Gas Man makes
  the same simplification and the partition coefficients were assembled against
  it. What is wrong is narrower and certain — nine smaller simplifications are
  listed and this one is in neither "Assumptions" nor "Known limitations", so a
  reader sizing the model against a real circle system cannot see it. Presence
  is yes as well: the omission predates this freeze by the whole life of the
  document.

**Added 2026-09-20 under the unconditional safety/science exception — 1 entry**

Captured on 2026-09-19 by `PL-4DCG`'s machine survey and triaged on 2026-09-20.
It is `science`-classed and so re-enters this gate whatever its presence answer,
under the second of "The gate is a snapshot"'s two unconditional exceptions. Its
problem also predates the freeze independently: the sentence it corrects has
stood in the data file since before 2026-09-06. It is not inside this
milestone's Required scope, so it clears before implementation begins. It is `S`.

- PL-NM7X (S) — **added 2026-09-20.** `src/anesthesia_sim/data/machines/reference_circle_system.json` justifies its
  4 L/min `default_fresh_gas_flow_l_min` as "a routine mid-range clinical fresh
  gas flow", and its `provenance_gap` adds that no clinical convention for a
  default flow "HAS NOT BEEN SOUGHT". `PL-4DCG`'s survey has since sought one
  and found the claim superseded, and `docs/MODEL.md` § "Parameter provenance"
  and `docs/machine-survey.md` § "(a2)" both restate it. `science`: a reader
  consulting the document this project calls authoritative for provenance is
  told a clinical-practice claim the project's own survey contradicts. **The
  number is not what is open.** The project owner ruled on 2026-09-20 (ratified,
  over lowering the default to match contemporary low-flow practice) that 4.0
  stays, because an unlabelled default teaches a norm whatever it holds and the
  90 s circuit time constant is what makes the machine's lag legible inside a
  teaching run. What clears this entry is the wording.

### Deferred to v0.4.26, because the port dissolves the defect — 1 entry

**Recorded here because this list is frozen** and "The gate is a snapshot, not
a moving target" allows a deferral only if it says so and says why. `PL-NGF7`
stays written in its "Added 2026-09-08 under the presence rule" block above;
this is its disposition, not its deletion.

**`PL-NGF7`** - `tools/contrast_check.py` can see no disabled-state colour,
because Flet/Material supplies every colour a disabled control takes and none
of them is a constant in `theme.py`. That is a defect *of Flet*: Qt supplies no
such theme, so the port's `theme.py` declares those colours itself and the tool
can reach them. Clearing it before v0.5.0 means building a mechanism to measure
a half of the interface that is about to stop existing. It is `infra`/`test`
classed, so `check_gate_reentries`' unconditional `safety`/`science`/`P0`
re-entry does not hold it here, and its problem does not predate the freeze in
any sense that survives the toolkit changing underneath it.

**Expected disposition when the port lands: `dropped`, not `done`** - the port
resolves it rather than any work on it. That is recorded now so a later session
does not read a dropped item as one that was skipped.

**It closed `done` instead, in v0.4.26** (#621). The prediction was right about the
mechanism and wrong about the work: Qt supplies no disabled-state theme, so the
ported `app/theme.py` declares those colours as constants and there was something
for `tools/contrast_check.py` to be pointed *at*. The expectation is left as
written above rather than edited, because what it was wrong about is the useful
part of the record.

### Sequenced past v0.5.0, so not clearable before it begins — 13 entries

**`PL-Z34C` makes a thirteenth, on a different ground, 2026-09-20** (project
owner, ratified, over keeping it on the frozen list). It is not sequenced behind
the port. Its completion is a *standing condition* rather than a piece of work:
`verify_required_from` is retired when the grandfathered set reaches zero, and
that set drains as each of twelve unrelated open items is started, never by
anyone pushing on this entry. It also no longer qualifies as debt - it reached
this gate at `status: needs-decision`, has since moved to `blocked`, and its
classes (`infra`, `session-cost`) were never debt classes, so `bin/docket gate`
does not count it today. Written as the freeze put it, per § "The gate is a
snapshot, not a moving target": this is its disposition, not its deletion. It
was 12 of the 13 off-gate prerequisites `PL-FCM3` measured; with it here the
gate waits on `PL-FG9D` alone.

- PL-Z34C (S) Retire verify_required_from and its grooming advisory once the grandfathered set reaches zero

**Nine of these eleven became clearable on 2026-09-14, when the Qt port moved
ahead of v0.5.0** (project owner, on `PL-RKWB`; § "Completed: v0.4.26 - the interface moves
to Qt" carries the decision and the count behind it). The heading and every
entry below stay written as the freeze put them, per § "The gate is a snapshot,
not a moving target" - this is their disposition, not their deletion, and it is
the same treatment `PL-NGF7` already had.

**What changed is the port's position, not any entry's judgment.** Each of the
nine was sequenced behind a port that shipped *after* the milestone this list
gates, which is what made it unclearable before v0.5.0 began; the port now
lands before v0.5.0, so each clears in the ordinary way:

| Entry | Relation to the port | Now clears |
| --- | --- | --- |
| `PL-3355`, `PL-Q4VH`, `PL-THXF`, `PL-TG60`, `PL-W8DQ` | carried by it | before v0.5.0 |
| `PL-GS3R`, `PL-YVHK` | sequenced behind it, both `P1` `safety` | before v0.5.0 |
| `PL-NGF7` | dissolved by it | before v0.5.0, as `dropped` |
| `PL-16ZC` | deferred past it | before v0.5.0, behind `PL-G59B` |
| `PL-8PS6`, `PL-WZVZ` | behind a design round the roadmap places nowhere | unchanged |
| `PL-2K1R` | rides it, added after the freeze | before v0.5.0 |

**`PL-2K1R` is the twelfth, added after the freeze** (project owner, 2026-09-14):
`P1` `safety`, an interpretation disclaimer beside the use disclaimer, stating
that the readouts and traces are modelled rather than measured. Sequenced
behind `PL-25KS` on the rule the five carried entries already follow - text on
a dashboard rewritten from scratch is written once, in the port - and clearing
before v0.5.0 like them. It is named under the port's "Decisions the port has
to make anyway", which is what keeps the port's parity claim checkable with it
on the list. A `safety` entry re-enters the current gate whenever it is found,
per § "The cadence", which is why it is recorded here rather than left to
Gate 2.

**`bin/docket wave` still prints all thirteen as "waiting on work outside it", and
that is correct rather than stale.** It asks whether an entry's `blocked-by`
chain leaves the frozen list, and these chains still do - they name `PL-G59B`,
`PL-25KS` and `PL-L9RD`, which are port items rather than gate entries. What
changed is *when* that outside work happens, which is a fact about the timeline
above and not one any field carries. The two readings answer different
questions and both are true: the count says the gate cannot clear these by
itself, and this section says the work they wait on now precedes the milestone
they gate. Do not "fix" the count to agree with the prose.

**This is what `PL-D143` asked for and could not get.** That item recorded the
contradiction plainly: recorded debt is cleared *before* the milestone it gates,
and these could not be, because the decision was that they are fixed during a
release that comes *after* the release being gated - so the gate could not reach
zero until after the thing it was gating. The beat `bin/docket wave` printed,
"clear the gate", was asking for something the plan forbade. Moving the port is
what makes the beat satisfiable; it was not the reason the port moved, but it is
the structural debt the move happens to pay.

**The two that do not move are the two that never depended on the toolkit.**
`PL-8PS6` and `PL-WZVZ` wait on `PL-FG9D`, the base anesthesia-machine
abstraction, which no milestone section names. Nothing forbids clearing them
before v0.5.0; doing it means scoping that design round first, which is a
milestone decision rather than gate work.

**The re-point that carries this is in the items, not here.** All nine named a
version in `blocked-by` or in prose; each now names the port item that does the
work, so none of them depends on what number the port ships under. `PL-005` and
`PL-LPLD` carried the deferral in prose alone and were `status: ready` - the
exact defect `PL-D143` described and fixed for only five of the six - and are
now `blocked` with the field to match.

**Recorded because the rule requires it, and until 2026-09-13 it was not.**
§ "The gate is a snapshot, not a moving target" allows a deferral only where
this section "says so and says why". Nine open entries are sequenced past the
milestone this list gates, and only the `PL-NGF7` block above was written down;
the other eight said so in a `blocked-by:` field and nowhere else, which is
renegotiation by frontmatter (`PL-9S30`).

**Nothing moves, and no decision is taken here.** Every entry below stays
written where the freeze put it, exactly as `PL-NGF7` does - this is their
disposition, not their deletion. Five still sit under headings reading "Cleared
before v0.5.0 begins", and those headings record what the list said on
2026-09-06 rather than a claim about today. Each sequencing call was the
project owner's, taken on 2026-09-10 when the port was scoped, and each is
argued where it was taken; this is the index, not the argument.

**Carried by the Qt port — 5.** `PL-3355`, `PL-Q4VH`, `PL-THXF`, `PL-TG60`
and `PL-W8DQ`, on the rule in § "Completed: v0.4.26 — the interface moves to Qt" → "Fixes
this port carries, and why that is not scope creep": each defect lives in code
that milestone rewrites from scratch, so fixing it on Flet means writing the
same lines twice. Each now carries `blocked-by:` naming the port item
that does the work - which is what `PL-D143` intended and what its own
`verify:` command tested for, and which shipped as the port item alone.

**Sequenced behind the port — 2.** `PL-GS3R`, `P1` and `safety`-classed. It is
designed already; what it waits for is the port *landing*, because the
chord-width column rule costs frame time the port makes free. § "Completed: v0.4.26" →
"Required scope" item 1 is where that was decided.

`PL-YVHK` is the second, `P1` and `safety`-classed for the same reason, and it
arrived after the freeze rather than at it (project owner, 2026-09-14,
splitting `PL-YLKR`). The presence rule holds a `safety`-classed finding to the
*current* gate whenever it was found, which is why it is dispositioned here
rather than left to its `blocked-by` field. It is the build half of the hover
readout `docs/MODEL.md` § "The chart's hover readout: what the tooltip may
show" now specifies, and it is designed already in the same sense `PL-GS3R` is:
nothing about it is an open question, and § "Completed: v0.4.26" → "Required scope" item 1
names it. What it waits for is the toolkit. Writing it on Flet means roughly
1 870 per-point strings onto a pause-transition frame `PL-KP7H` measured at
71.9 ms and 90 KiB, deleted again at the port, where the same content is one
format callable. **It is parity rather than new capability**, which is what
separates it from `PL-16ZC` below: the Flet build has a hover and the Qt build
would not, because `ScatterPlotItem` ships `hoverable` set to `False`.

**Dissolved by the port — 1.** `PL-NGF7`, whose own block above carries the
reasoning and its expected disposition of `dropped` rather than `done`.

**Deferred past the port, because building it first is the work thrown away —
1.** `PL-16ZC`, a show/hide control for the two clinical references and the
control marks (project owner, 2026-09-14, on `PL-NR2K`). It is the mirror image
of the five carried by the port and it arrives at the same place by the
opposite route. Those are defects the port must not reproduce; this is new
capability, which § "Completed: v0.4.26" → "Fixes this port carries" excludes "whatever its
size" - and the owner ruled it out on 2026-09-10 for exactly that reason. But
the control extends the legend table `PL-CG7J` built inside
`app/simulation_view.py`, all 4 321 lines of which Required scope item 2
rewrites, so the same rule that keeps it out of the port makes writing it on
Flet first the one piece of open Gate 1 work that is purely written twice.
Its `blocked-by` names `PL-G59B`, the chart port that builds the legend and
both references this would toggle, rather than the port's version, which would assert
through `MilestoneStates.ships_with` that it ships with that milestone when it
deliberately does not.

**What is not deferred is the decision**, and saying so is the difference
between this and a parked item. `PL-16ZC` asks whether the references and the
control marks should be hideable *at all* - a question about what the chart is
for, which no toolkit answers and which its own Done-when allows to close the
item writing no code. That half is answerable any day; only the build waits.
It is the same split taken over `PL-YLKR` on 2026-09-14, whose design was
toolkit-independent and landed on v0.4.x while its build moved to `PL-YVHK`
above.

**How this was found is worth one line**, because the general form of it is
wrong. The project owner asked on 2026-09-14 whether all Flet-related gate
entries should be dropped or postponed now that the interface moves to Qt.
Counted rather than answered from the shape of the question: of the 23 entries
this gate can clear, 13 never touch the interface, 9 of the remaining 10
survive the port or are inputs to it - `PL-JRS3` is the port's own Required
scope item 4, `PL-LL9Y` is named under "Decisions the port has to make anyway",
`PL-YLKR`'s design is toolkit-independent, and `PL-B9PY` ships on Flet in
v0.5.0 by the decision recorded in § "Items this port moots or transforms".
One entry was left, and it is this one. The general proposal would have
suppressed nine real entries to catch it.

**Behind a design round no milestone section places — 2.** `PL-8PS6` and
`PL-WZVZ` both wait on `PL-FG9D`, the base anesthesia-machine abstraction,
which no milestone *section* names — though § "Planned milestones" item 1 is
its line of intent, and now names `PL-FG9D` and its prerequisite survey
`PL-4DCG` outright. This paragraph said item 1 did not exist ("has no
planned-milestone line of its own") until `PL-Z4WL` corrected it;
`PL-FG9D`'s own brief opens by quoting item 1, so the two documents had
disagreed about whether the intent was recorded at all. What is true is the
narrower claim: intent is not scope, no section places it, and so nothing
schedules it. These two are unlike the seven above: nothing forbids clearing
them before v0.5.0, but doing it means scoping that design round first, which
is a milestone decision rather than gate work.

**What reads this, and what reads past it.** `bin/docket wave` reaches the same
eleven from the items rather than from this prose - an open entry whose
`blocked-by` chain leaves the frozen list is counted apart from the ones this
gate can clear, so the beat asks for a number that is reachable (`PL-SL70`).
Two independent readings of one fact is the point rather than duplication: if
the prose and the count disagree, one of them is wrong and the disagreement is
visible on the next run.

### Declined to Gate 2 on the refilling-queue ground — 209 entries

**Recorded rather than silent, which is what the rule actually requires**
(project owner, 2026-09-08). "The gate is a snapshot" lets a session defer a
presence-qualifying finding, or decline one, but "either way it must say so and
say why". These twenty-nine were found by the same `PL-36R4` audit as the
thirteen admitted above, they pass the presence test as squarely as those do,
and they are deferred anyway on the second ground the rule states: pulling them
in "would recreate the refilling-queue problem the debt gate replaced Phase 0
to solve".

The arithmetic is the argument. Gate 1 stands at 132 entries against Gate 0's
21 — already by a wide margin the largest this project has held — with 89 still
open. Admitting all forty-two would take it to 173 and grow it 31% at a point
where it is not draining, which is the shape Phase 0 was retired for: a gate
that refills faster than it drains is abandoned rather than followed, and that
is worse than not having one.

Every one of the twenty-nine sits wholly in the workflow lane, which is why
this group and not another. They are apparatus, held to
`.claude/rules/apparatus-standard.md`'s deliberately lower bar, and none of
them can reach a reader of the simulator — so deferring them costs the gate
nothing it exists to protect, while the thirteen with a product-lane half are
admitted above precisely because they can. Where the two standards compete,
the simulator wins; this is that rule applied to the gate's own membership.

**The thirtieth arrived after the audit, on the same ground** (`PL-33WM`,
2026-09-08). `PL-HX5C` was captured hours after this subsection was written and
merged in `#477` against a base whose CI predated `PL-36R4`'s check, so `main`
went red on the one disposition this rule forbids — silence. It is recorded
here rather than admitted above because every argument in the four paragraphs
above applies to it unchanged: found after the 2026-09-06 freeze, `P2` and
neither `safety` nor `science`, and wholly in the workflow lane. Later
additions belong in this list for the same reason the first twenty-nine do;
what the audit found is a provenance note, not the test.

**Eleven more from the 2026-09-12 triage pass, and six of them are not in the
workflow lane** (`PL-3B47`, which closed with that pass). The refilling-queue arithmetic above is unchanged
and still the reason: the six that are apparatus sit exactly where the first
thirty do, and admitting them would grow a gate that is not draining. The other
six need their own ground, because "wholly in the workflow lane" is not true of
them, so it is stated rather than stretched.

**Four are waiting on the port rather than on anybody's attention.** `PL-7SVX`
*is* the port's Required scope item 7 and deleting the Qt spike tree before the
port landed would have removed the working reference every other item in that
milestone read from. `PL-C92D` asks for a caveat on a Flet measurement whose toolkit is
being removed, and was re-scoped in the same pass to stop asking for a
re-measurement. `PL-SQJ1` measures a playback shortfall that is a consequence of
frame cost the port removes, so measuring it now measures a tree about to
change. `PL-ZG5J` would land a harness built on `flet.messaging.session.Session`
for one milestone's use. Each is real and each gets a worse answer if it is
hurried in front of the port.

The port has since landed (`PL-25KS`, § "Completed: v0.4.26 — the interface
moves to Qt"), so the ground above is spent rather than wrong: it records why
these four were deferred on 2026-09-12, and whether each is startable now is
the queue's answer rather than this section's. `PL-ZG5J` closed on 2026-09-19
with a Qt harness under `tests/benchmarks/`, which is not the Flet one
described above — the serializing connection that made the Flet method subtle
is held in Qt by the paint, and the harness is written down rather than
thrown away so the next session re-measures instead of re-deriving.

**Two are decisions this gate should not force.** `PL-3JP0` and `PL-HKTB` both
ask whether a piece of the interface should change or be recorded as
deliberate, and `PL-L9RD` - the port's pass that makes the interface's visual
decisions once - is where both are cheapest to answer. Pulling them into Gate 1
would mean deciding them twice, which is the duplication that item exists to
prevent.

**`PL-CNCF` is the one to watch, and it is deferred with that said.** Its 6.2 ms
is the frame cost that *survives* the port - the score evaluation, no toolkit in
it - so unlike its neighbours it does not dissolve, and it is what sizes
`PL-GS3R`'s chord-width rule. It is deferred because nothing is blocked on it
today and because the number wants re-taking on the ported tree anyway, not
because it is small.

**One more from the session that answered `PL-69JZ` and `PL-L09X`** (2026-09-12).
`PL-NF6N` asks whether triage should have a write command instead of every pass
editing item front matter by hand. It is wholly in the workflow lane and sits on
the same refilling-queue ground as the first thirty; it is also a question about
whether a mechanism is worth building at all, which is the shape most likely to
be answered "no" and least likely to be worth holding a gate open for.

**Fourteen more from the 2026-09-12 triage pass over what the v0.4.14 range left
untriaged** (`PL-0QQP`). Twelve are wholly in the workflow lane and sit exactly
where the first thirty do: captured after the 2026-09-06 freeze, `P2` or `P3`,
neither `safety` nor `science`, and apparatus held to
`.claude/rules/apparatus-standard.md`'s deliberately lower bar. The
refilling-queue arithmetic in the four paragraphs above is unchanged and is still
the reason - this gate is not draining, and fourteen entries is a tenth of it
again.

**Two reach `ROADMAP.md` and so are not wholly apparatus**, which is stated
rather than stretched. `PL-0VFF` is this subsection's own bookkeeping: three of
its entries closed in v0.4.14 and nothing marks a closed entry apart from an open
one. `PL-880Z` is the wording of a frozen entry in the workflow-lane list above,
which repeats `PL-XLQ5`'s title and with it a mechanism `_landing_split` does not
have. Both are corrections to this document's account of its own queue, so
neither can reach a reader of the simulator, which is the test the first
twenty-nine were declined on. The one item from this pass that *could* reach such
a reader - `PL-DZFJ`, on what a drawn chart point represents - is admitted above
rather than declined, under the unconditional safety exception.

**Three more from the `vcs.py` batch closure** (`PL-CSHL`, 2026-09-13). `PL-QNYF`,
`PL-3LLZ` and `PL-7XNX` were filed by the session that closed nine of that
cluster's items, and each was produced by one of those closures rather than found
by an audit. All three are wholly in the workflow lane and sit on the same
refilling-queue ground as the first thirty: `PL-QNYF` is a `docket check` error
reachable only by a closure shape the same-commit rule makes uncommon and which no
item is in today, `PL-3LLZ` is test-fake upkeep, and `PL-7XNX` is a handful of git
subprocesses on a path `PL-PMT7` just cleared. Admitting them would grow a gate
that is not draining in order to hold the release open for apparatus that cannot
reach a reader of the simulator.

Worth stating because the batch was measured: these three *are* the spawn count
`PL-CSHL` recorded, so they are the visible cost of that pass and they are being
deferred rather than hidden. Filing them was the capture rule; deferring them is
this one.

**One is a decision the port makes cheaper, on the ground `PL-3JP0` and `PL-HKTB`
were declined on** (`PL-5B1N`, triaged 2026-09-13). It is not apparatus and cannot
be declined on the refilling-queue ground: it asks what visual channel separates a
committed run from an uncommitted preview, which is a question about a displayed
clinical value and reaches a reader of the simulator directly. It is declined
because the port rewrites the chart on pyqtgraph and redecides dash pattern, alpha
and stroke width along with it, so answering against the Flet chart would mean
answering twice - the same reason those two wait for `PL-L9RD`.

Nothing is misleading anybody meanwhile, which is what makes the deferral safe
rather than merely convenient: no preview is drawn today, so the safety obligation
the item records binds whoever builds it rather than describing a live defect. Had
a preview already shipped in a style a compartment uses, this would be admitted
above under the unconditional safety exception instead.

**One more from closing `PL-W1LN`** (`PL-CY8B`, 2026-09-13). Building that item's
reproduction turned up that `_shallow_pair`'s own commits carry `PL-M01`-style
subjects, which `ID_PATTERN` does not match, so the sibling guard test's
`assert "PL-M01" not in out` cannot fail. It is wholly in the workflow lane and sits
on the refilling-queue ground with the first thirty. Worth one sentence on why it is
not more urgent than that: the test's *other* assertions are sound and do fail if the
guard stops working, so the guard is covered - what the vacuous line never checked is
the narrower claim about the default branch's own ids, which `PL-W1LN`'s new test now
makes with valid ids. So the coverage exists; it is the older assertion that is
decorative.

They enter Gate 2 when it freezes at v0.5.0's ship, unless closed before it -
which is the trigger § "The cadence" records, not the scoping of the milestone
Gate 2 gates. (Written "when v0.6.0 is scoped" until 2026-09-16, when v0.6.0 was
scoped without freezing it.)

**Five more from the 2026-09-13 triage pass**, which folded in the captures the
stale-name batch of Gate 1 and the v0.4.15 cut left behind. Same ground as the
thirty before them and no new argument is owed: each was found after the
2026-09-06 freeze, each is `P2` or `P3`, none is `safety` or `science`, and all
five are apparatus - two `docket` command defects, a filename-drift sweep, a
pair of stale check workarounds, and the citation-form conversion `PL-V13T`
left open. None can reach a reader of the simulator, which is the test the
first twenty-nine were declined on.

**Twelve more from the 2026-09-13 triage pass over the fourteen captures open
that day** (`PL-TQJ4`). Nine are wholly in the workflow lane and sit exactly
where the first thirty do: found after the 2026-09-06 freeze, `P2` or `P3`,
neither `safety` nor `science`, and apparatus held to
`.claude/rules/apparatus-standard.md`'s deliberately lower bar. The
refilling-queue arithmetic above is unchanged and is still the reason. The
thirteenth item of that pass, `PL-V6M0`, is admitted above under the
unconditional safety exception rather than declined.

**Three are not wholly apparatus and so need their own ground**, which is
stated rather than stretched. `PL-BQ46` and `PL-KL2Q` are two halves of one
question about `core/`'s dimensionless vocabulary — whether a MAC-relative
ratio earns a type of its own, and which of the two percent/fraction
vocabularies a new parameter field takes. Both are `refactor`-classed hardening
of a boundary that produces no wrong value today: what they describe is a guard
`mypy` could give and does not, not a displayed number that is wrong. Neither is
under this milestone, which adds no field to `core/parameters.py` and no fourth
convention, and answering them apart would decide one question twice — so
they are better taken together, after the port has settled what `formatting`
looks like.

`PL-N32Y` is a correction to this document's account of a *past* release:
v0.1.0's Required scope says the release added tissue:blood partition data where
the agent files store tissue:gas. The scientific half is already fixed where a
reader of the model meets it — `PL-212V` corrected `docs/MODEL.md`'s
specification and `PL-H46J` gave the Symbols table the Code column that maps
each symbol onto `core/`, both in v0.4.17 — so what is left is the history,
and it cannot reach a reader of the simulator. It is also `needs-decision` on a
question only the project owner can answer, about whether a frozen `Required
scope` line is corrected or annotated when it turns out to be wrong; holding
v0.5.0 open would not produce that answer.

**One more from the 2026-09-13 article-review triage pass, on the same ground.** `PL-DG84`
(`docs/WORKING_NOTES.md` asks for resolved threads to be deleted and nothing
reads that policy) was captured that day and triaged to `needs-decision`, which
is what makes it debt this gate has to dispose of; it is `P2`, neither `safety`
nor `science`, and wholly apparatus. The accumulation it describes predates the
2026-09-06 freeze and so passes the presence test as squarely as the first
twenty-nine, and it is declined for the reason they were: it makes no remaining
entry cheaper, so it fails the arithmetic the presence rule asks for, and Gate 1
stands at 52 open entries it can clear.

Its five filed instances need no disposition of their own and are not listed
here - `PL-5748`, `PL-60CQ`, `PL-BHJW` and `PL-75R0` are `docs`-classed at
`ready`, which is not a debt class, and `PL-C92D` is already above on its `perf`
class. That asymmetry is worth naming rather than looking like an omission: the
systemic item reaches the gate only because its next step is a decision, while
the concrete defects it generalises do not reach it at all.

**Four more, and they are the heads of `PL-6ZQY`'s remaining clusters**
(`PL-VX5H`, 2026-09-18). `PL-6TP8`, `PL-HWW1`, `PL-4FBP` and `PL-4Q9B` were
captured on 2026-09-17 to record that four of the six clusters had no item that
could carry `root-cause-of:`; on 2026-09-18 each became that item, which is
what triaged them to `needs-decision` and so made them debt this gate has to
dispose of. Each is `P2`, neither `safety` nor `science`, and captured after
the 2026-09-06 freeze. Two are wholly apparatus - `PL-6TP8` and `PL-4Q9B`.
`PL-HWW1` reaches `ROADMAP.md` and `PL-4FBP` reaches `docs/MODEL.md`, so
neither is wholly in the workflow lane and both are stated here rather than
stretched: what either would change in those documents is how a fact is
*recorded*, not what the simulator computes or what it tells a reader, so
deferring them costs the gate nothing it exists to protect.

**Declining them costs less than it reads, because the ranking has already
answered it.** A sound `root-cause-of:` lifts an item above every band but
`P0` in `bin/docket next`, so all four are offered ahead of this gate's own
entries whether or not they sit on the list. `PL-BHVM` is the precedent -
declined here, and ranked first in the queue. What the gate decides is whether
v0.5.0 *waits* on them; what the ranking decides is when they are picked up,
and the answer to the second is already "before nearly everything else".

**A fifth, split out of one of those four on 2026-09-19** (`PL-2T03`).
Measuring `PL-HWW1`'s eight members against the code found four of them under
a different mechanism - the release train's *arrangement* is re-derived by
comparing version numbers, where § "The timeline" already records it as a
grammar-checked table - so those four moved to a head of their own and
`PL-HWW1` kept the three that are about membership. `PL-2T03` declines on this
subsection's own ground: captured after the freeze, `P2`, `defect` rather than
`safety` or `science`, wholly in the workflow lane, and completing no entry on
the frozen list. It carries `root-cause-of:` over `PL-Y1L0`, `PL-J45M`,
`PL-7CSP` and `PL-B5DW`, so the paragraph above applies to it unchanged: the
ranking already offers it ahead of this gate's own entries, and what is
declined is only whether v0.5.0 waits on it.

**Two more from the same session, on the project owner's 2026-09-19 request
that a reply refresh before reporting** (`PL-QSGX`, `PL-CM40`). The resident
half of that request took effect immediately, in
`.claude/rules/instruction-writing.md` rule 14; these are the deterministic
half it should later shrink into - `bin/docket flight` fetching like its
siblings, and one command printing the whole refreshed picture. Both were
captured after the freeze, both are workflow-lane apparatus, and neither is
`safety` or `science`. `PL-CM40` reaches `.claude/rules/instruction-writing.md`
rather than only `subprojects/docket/`, and is stated here rather than
stretched: what it changes there is a rule's *length*, by replacing three
command names with one.

**One more on a ground of its own: its problem did not exist at the freeze**
(`PL-09G9`, 2026-09-19). The other entries above are deferred despite passing
the presence test; this one fails it outright, and saying so is cheaper than
stretching the refilling-queue argument over it. The contract it makes
mechanical - that a `verify:` records the discriminator and not a second proof
of the tree - was decided on 2026-09-19 under `PL-6TP8`, thirteen days after
this gate froze, so there was nothing on 2026-09-06 for a gate to hold. It is
`P2`, `defect`-classed, wholly workflow-lane apparatus, and neither `safety`
nor `science`. It is stated rather than left silent because the disposition
rule asks for a sentence either way, and an open debt item the gate neither
places nor defers is reported as undisposed whatever the reason.

**A second on that same ground, and it is the rule catching itself**
(`PL-YFXG`, 2026-09-19). `_carried_work` was written on 2026-09-12 under
`PL-YDL6`, six days after this gate froze, so the mechanism this item describes
did not exist for a 2026-09-06 list to hold. It is `P2`, `defect`-classed,
wholly workflow-lane apparatus, and neither `safety` nor `science`. It was
found while closing `PL-Y5JX` as the reason `main` was red - a closure whose
work is queue files cannot have its `pr` recovered, and the resulting
`docket check` error fails `make check` on every branch - and recording it here
the same day is what the disposition rule exists to force, since the session
that found it is the one that would otherwise leave it silent.

- PL-09G9 (M) Nothing refuses a new verify: command that re-runs a test file make check already collects, so PL-6TP8's contract is enforced by prose alone and 82 of 180 open commands carry the clause
- PL-0M32 (S) Nothing can tell an item finished under a renamed test from one nobody has started
- PL-0VFF (S) ROADMAP.md's 'Declined to Gate 2' list names PL-483K, PL-69JZ and PL-L09X as deferred, but all three closed done in v0.4.14, and nothing distinguishes a still-open entry from a closed one
- PL-12P8 (S) PL-JBZK's lane check assumes every file under tests/ is a test file, so a shared non-test helper is told to declare itself apparatus
- PL-1BS2 (S) The session-start digest's Releasable line reads readiness without the interrupted-cut resume, so during an unfinished cut it reports the short remainder with nothing saying why
- PL-2GQW (S) PL-L9JS's not-delegable reason rests on the recursion claim PL-20CQ disproved, so the item may be delegable after all
- PL-2T03 (M) Four items re-derive the release train's arrangement by comparing version numbers, though ROADMAP.md's timeline table already records it
- PL-316G (M) Convert the 150 possessive-form document citations to the section-mark form, which is the only way doc_check can check them without reading prose as a citation
- PL-3DN1 (S) bin/docket release accepts a VERSION below the current one, so a typo silently downgrades pyproject.toml's version field
- PL-3JP0 (S) Decide whether the wash-in section's three paragraphs survive the same test PL-6580 applied to the chart panel above it
- PL-3V6C (S) PL-TFWR and PL-XQRK record incompatible causes for the same remote-deletion failure and both ruled out the git proxy on a field that does not record policy denials, so whichever lands first writes an unproven cause into the instructions
- PL-483K (S) The stop hook demands a push for work already pushed after a branch is restarted per the merged-PR recovery, because checkout -B from origin/main leaves the upstream pointing at main
- PL-4FBP (M) Fifteen items repair a document sentence whose link to the tree lives only in the reader's head: decide whether an assertion must name what it asserts
- PL-4Q9B (M) Ten items work around the clone being trusted as the remote and around an unrecorded set of permitted ref operations: record both
- PL-69JZ (S) docket verify's 'the checks themselves are unedited' audit REJECTs every item whose declared work is editing a .claude rules file, since gate_paths includes .claude and touches is not consulted
- PL-6BDX (S) Two shipped items are reported in flight in every session's digest, because their branch refs outlived their merges: PL-GVXP (v0.4.7) and PL-S5LB (v0.4.6)
- PL-6G8T (S) _section_text reads a required heading quoted at a line break as the section itself, so a wrapped quotation above an empty real heading masks the empty one
- PL-6TN8 (S) A verify: command whose discriminating half greps for a test name can exit 1 because the name was guessed, not because the work is outstanding, so watching it fail proves less than the rule assumes
- PL-6TP8 (M) Twelve items re-decide what a verify: exit status proves, because the field was specified as a command string and nothing else: one contract rather than twelve patches
- PL-6YWK (S) PL-4L6Z's verify: runs the whole reference suite, so it is killed at docket check's 120s limit and nothing is claimed about the item on any run
- PL-6YYR (M) A release tag can be pushed for a version that was never cut, and nothing detects it: v0.4.8 tags main at version 0.4.7 with no release notes and no ROADMAP row
- PL-77SV (S) PL-G8TR, PL-K2C8 and PL-TFWR all edit the same ten lines of the docket skill's recovery block, and PL-G8TR's Done-when is defined against that block's shape, so whoever lands first silently sets the other two's tests
- PL-7RTN (M) An open pull request can carry no check runs at all, so a branch merges with nothing having gated it
- PL-7SVX (S) Delete spikes/ and the last Flet import once the port is complete
- PL-7XTS (S) Nothing routes a close-out to bin/docket verify --self, so a session auditing its own branch runs the delegated mode PL-69JZ fixed and still gets a REJECT on correct work
- PL-879R (S) docket check advises on a verify: command's outcome but never its shape, so a grep for an id, or for a file another item is known to create, is only reported once it has already started passing
- PL-880Z (S) Five ref-lifecycle briefs carry citations that have moved, and PL-XLQ5's title names a mechanism _landing_split cannot have - which ROADMAP.md repeats verbatim as a frozen gate entry
- PL-8MJ3 (M) bin/docket triage's 'already edited on a branch' mark reads the merge base, so it keeps firing after that branch's edit has merged - it told one pass to skip four of its five items, every one a false positive
- PL-8P6D (S) Checks refuse a pull request whose branch carries no item id, so the owner's own web edits and any contributor's pull request fail CI
- PL-8T3Z (S) PL-K2C8's touches omits .claude/hooks/no-prune-guard.sh, which carries the same incomplete recovery recipe, and its Where sends a fix at PL-CPLD which is now dropped
- PL-9LXK (M) Nothing checks a prose claim about the tier or adoption of a stored value's source, though PL-1JDD made both machine-readable and three such claims went stale within a day
- PL-B8V1 (S) ROADMAP.md's declined-to-Gate-2 argument says 'Gate 1 stands at 132 entries ... with 89 still open' in the present tense, and it is now 159 with 94 open
- PL-BGMK (M) Two open items whose touches and verify: command overlap are never compared, so PL-1YDK and PL-8PT6 were filed and worked as one finding twice and only docket check --verify on main caught it
- PL-BHVM (M) Nineteen items re-decide what evidence proves a ref is done, seventeen of them in vcs.py: one design round rather than nineteen heuristic patches
- PL-BQ46 (S) MacAwakeReference.fraction_of_mac and formatting.mac_multiple are a third and fourth dimensionless convention beside Fraction, and neither is distinguished from a concentration fraction at the type level
- PL-C92D (S) PL-YSZN's Flet frame table predates PL-2FM6 and measures a tree that no longer exists in two of its three stages, so the Qt/Flet comparison rests on one row
- PL-CM40 (S) No single command prints the refreshed picture a closing block needs - main's tip, whether this branch is contained in it, flight and stranded - so the rule has to name three
- PL-CNCF (M) controller.drawn_window costs 6.2 ms a frame at the shipped 150-column budget - 99% of the frame's read and about eighty times the simulation at 1x
- PL-DG84 (M) docs/WORKING_NOTES.md asks for resolved threads to be deleted and nothing reads that policy
- PL-F48B (S) Nothing ever repairs a clone's tags after a history rewrite: fetch_remote runs git fetch without --tags --force, so release tags keep pointing at purged commits
- PL-F933 (S) doc_check resolves a path citation against the working tree, so a citation to a gitignored path passes locally and reddens CI
- PL-G8TR (S) no-prune-guard is evaded by the form it recommends - git branch -dr driven from a generated list is a prune
- PL-H9GV (S) PL-01GD shipped as one exported Makefile variable with no test: PYTHONDONTWRITEBYTECODE appears only at Makefile:21, its declared touches names tests/unit/test_tools_portability.py which never changed, and its verify: passes against an untouched suite
- PL-HKTB (S) The chart gridline and divider grey measures 1.31:1 on the panel and carries no contrast requirement; decide whether it should be darkened or recorded as exempt furniture
- PL-HWW1 (M) Three items patch a reading of ROADMAP.md's Required scope because membership is cited rather than declared: make the declaration the record
- PL-HX5C (S) Both in-flight guards passed and two sessions still implemented PL-W8XP independently: the second never renamed and its branch was named after a different item, so neither the ref read nor the session read could see it
- PL-JBRC (M) docket stranded still calls a branch merged when one of its commits is only docket record output, which converges byte-for-byte with the base
- PL-JW39 (S) docket next ranks a needs-decision item first, so every fresh session opens on work whose next step is the owner's answer
- PL-JXVD (S) PL-38PN's own line-number corrections are stale, so working it as written writes a second generation of wrong citations; PL-QV5Y has the same defect
- PL-K5PW (S) bin/docket check --items docs/items resolves config from docs/ rather than the repo root, so it reports a clean store as 112 errors
- PL-K82G (M) bin/docket verify's absolute 'no existing assertion removed' check has no passing route for an item whose own work makes a rendered string false, so a correct close-out REJECTs
- PL-KFWL (S) The v0.4.8 tag is pushed onto a commit where the release was never cut, so doc_check errors on main for every session
- PL-KL2Q (S) core/parameters.py now holds two overlapping percent/fraction vocabularies - Pydantic's PositivePercent which validates but does not type-check, and concentration.py's Percent which type-checks but does not validate - and nothing says which a new field takes
- PL-KNHX (S) contrast_check's KNOWN_SHORTFALLS entries are never checked against the requirements they excuse, so a stale one lingers and inflates the reported shortfall count
- PL-KRS6 (S) bin/docket release counts the previous release's own cut item as releasable work, so every session after a release is offered an empty one
- PL-L09X (M) An item blocked on a milestone that is decided but not yet named has no honest status: bare blocked errors, and blocked-by only accepts a version the roadmap already places
- PL-LBR6 (S) bin/docket record renames a drifted item file as a side effect of writing a pr number, which conflicts against whoever else is holding that file
- PL-LF2C (S) PL-VV4D's exact left-behind check rests on refs/pull/<n>/head being permanent, and GitHub is about to unreference 90 of them, so the check needs a third decline condition and one of its two test vectors dies
- PL-LKGL (S) A verify: command cannot detect a stale item: it tests for the presence of the fix, not the fault, so an item whose problem was solved another way stays red forever and reads as outstanding work
- PL-LN3T (S) wave does not report a milestone row the version has released whose section's Required scope is still open, so a patch cut at a milestone's own number leaves the plan stepped past it once the hand-off has scrolled by
- PL-LPWK (S) A release note cites the pull request that closed an item, not the one that carried its code, whenever the two differ
- PL-LT77 (S) git fetch --tags does not prune, so a tag deleted on origin keeps failing doc_check in every checkout that already fetched it, and nothing distinguishes stale local state from a real repository fault
- PL-MSFB (S) PL-6194's verify: command still uses [(] and [)] to work around the math check that PL-WTQ1 fixed, and WORKING_NOTES.md:504 still uses backticks to work around PL-KJ63
- PL-N32Y (S) ROADMAP.md's v0.1.0 Required scope says the release added tissue:blood partition data, where the agent data files store tissue:gas
- PL-NF6N (M) Triage has no write command: every pass edits item front matter by hand, which is the decidable half CLAUDE.md asks to be moved into code
- PL-P757 (S) bin/docket --items pointed at a nested store makes every annotating commit read as work, silently
- PL-PNW6 (S) A release cut at a version number some withdrawn tag once named leaves every warm checkout pointing v<version> at the old commit, and the handover's own 'git fetch origin main' is the command that leaves it stale silently
- PL-PQQ2 (S) PL-KBD0 is the workflow lane's top pick but all three live instances its brief names are now closed, and no open item at ready or needs-decision carries a blocked-by field
- PL-QSGX (S) bin/docket flight never fetches, unlike stranded and branch, so it reports refs as old as the clone - the one command whose whole job is reading other sessions' branches
- PL-QV5Y (S) Makefile's CI-timing comments quote a 1230-test suite at 78 s serial and 27 s parallel, measured 2026-09-03; the suite is now 2096 tests at about 43 s parallel, so a reader sizing a CI-cost decision from them is reading stale figures
- PL-SQJ1 (M) Playback delivers 73-91% of the rate the dropdown displays: 300x measured at 220x, 1x at 0.9x, so the clock on screen runs slower than its label
- PL-T7VS (M) A red doc_check voids the whole-store verify replay for the 29 open items gated behind it, and the replay reports green rather than declining to answer
- PL-T8PT (S) make check runs pr_title_check --discover against committed history, so a session that runs it before committing the closure sees a HEAD without it, passes locally, and goes red in CI anyway
- PL-TNB6 (S) docket next attributes the whole of Gate 1 to the v0.4.x step, where the plan makes Gate 1 its own row that no patch may ship
- PL-TP5M (S) PL-ZBRB's advisory names blocked-by to work around a checker that did not read it, and PL-KBD0's check now does
- PL-TTMF (S) PL-6BDX's title names two expired refs and the live instance this item was filed on has cleared too, so the item now reproduces nothing while the defect it describes is unfixed
- PL-VJFQ (S) Nothing enforces that KNOWN_SHORTFALLS only shrinks, so the contrast ledger could become the suppression list ui-color.md forbids in prose
- PL-VYK1 (S) The docket skill's release handover tags at origin/main rather than at the cut's own merge commit, so a re-run of the three commands tags whatever merged next
- PL-WZBX (M) bin/docket wave counts the four entries ROADMAP.md's gate places under 'Cleared by v0.5.0 itself' as clearable before the milestone begins, where the gate rule says the milestone clears them
- PL-XMNC (M) The pull-request verify replay scopes to items whose item file the branch edited, so a branch that invalidates some other item's verify: command by editing the file that command reads replays nothing, and the break is reported only by the whole-store sweep after the merge
- PL-Y1LD (M) docket concurrent orders a batch by file, but the lane mechanism separates only two sessions, so the third and fourth simultaneous session have no command that picks for them
- PL-Y31G (M) bin/docket stranded classes a branch left on pre-rewrite history as one whose pull request merged, because it compares file content and a rewrite leaves content unchanged
- PL-YFXG (S) bin/docket record can never supply the pr of an item whose work is the queue itself - _carried_work reads a queue-only diff as a closure that landed without its work, so PL-YTDN left main red with an error no command could clear
- PL-YKXQ (S) This container's initial clone had local main diverged 407 commits into pre-rewrite history, so a session that checks out main gets a stale tree and an old bin/docket
- PL-YTDN (S) Rename the nine item files whose slug no longer matches their title, now that docket check names them
- PL-Z5FG (S) The PL-B32L and PL-TCW5 edits to core/parameters.py shifted line numbers cited by PL-0NQ1 and PL-HXKC, which is PL-J7C5's hazard arriving again from an unrelated branch
- PL-ZG5J (M) Land the headless frame-cost harness that measured all of the above, so the simulation-versus-UI split can be re-measured rather than re-derived
- PL-FCM3 (S) `bin/docket wave` reports how many gate entries wait on work outside the gate and never names or counts those items, so the beat understates what clearing the gate costs - measured 2026-09-20 as 1 startable entry plus 13 off-gate prerequisites
- PL-TGFY (S) `PL-Z34C` reached this gate as `needs-decision`, has since moved to `blocked` and carries no debt class, so the frozen list holds an entry `bin/docket gate` no longer counts as debt and no session can clear by working it
- PL-ZM48 (S) `docs/worker.md` records a remote-branch deletion as exiting 0, and `PL-3V6C` as two incompatible causes, where one 2026-09-20 transcript carries the 403 and the `Everything up-to-date` line together at exit 1

**One entry on a second ground, recorded here rather than under a heading of
its own — `PL-VV6N` (decide a retention rule for items captured but never
worked).** Captured 2026-09-13, a week after this gate was frozen, so the
snapshot rule already places it in the next gate; it is written down because it
sits at `needs-decision`, which is what makes it debt, and a reader finding it
open would otherwise have to work out why it is absent.

Its ground is not the refilling queue above but that it cannot be worked yet.
It proposes *tightening* intake, and `.claude/rules/expert-review.md` requires
naming what the suppressed side would have to be worth and then counting it
before any such proposal is acted on. That count is `PL-YVV4`, filed the same
day and named in this item's `blocked-by`. `PL-LKGL` is the precedent: an
apparatus capture-bar proposal died when the count it had skipped came back 67%
still-real findings. Admitting it would put an entry on the frozen list that
cannot close until one that is not on the list closes first.

**Thirteen more from the 2026-09-13 triage pass over the twenty-seven
captures open that day.** Nine are wholly in the workflow lane and sit exactly
where the first thirty do: found after the 2026-09-06 freeze, `P2` or `P3`,
neither `safety` nor `science`, and apparatus held to
`.claude/rules/apparatus-standard.md`'s deliberately lower bar. They are
`PL-4V6B` (whether the decision archive is separated from the work queue),
`PL-4ZK8` and `PL-Q664` (two ways `docket`'s concurrency and in-flight answers
mislead a session), `PL-65HT` (a check for an unsourced `core/` numeric
default), `PL-D0K3` (the ten non-discriminating `verify:` commands), `PL-FX0K`
(the front-matter list field that parses silently empty), `PL-NJ9M` (the
delegable list cannot tell a determined brief from an open one), `PL-WHQS` (the
duplicated closed-item filter) and `PL-WTXB` (the unreferenced `milestone`
subcommand). The refilling-queue arithmetic in the four paragraphs above is
unchanged and is still the reason.

**Four are not apparatus and so need their own ground**, which is stated rather
than stretched. `PL-6KNM` and `PL-BDNB` are what `PL-9SH6`'s accessor rename
left behind - whether the validator, `core/concentration.py` and the `Fraction`
`NewType` name a representation or the quantity, and whether one local inside
the closed forms is renamed with them. Both are `refactor`-classed naming
decisions that produce no wrong value today, and taking them apart would decide
one question twice, which is the ground `PL-BQ46` and `PL-KL2Q` were declined
on. `PL-SPN6` is the third from that rename: three compartments now raise one
error string, so a refused step no longer says which refused. That is a
diagnostic a developer reads rather than a value a clinician could act on -
which is why it is `defect` rather than `safety` - and the loosened assertions
it also owes are not made cheaper by holding this gate open. `PL-V67Q` is a
y-axis range control the project owner raised as a passing want; it is
`needs-decision` because the design round has not happened, half its open
questions are the owner's, and that round owes a human-factors literature read
before any default is chosen. None of the four is inside this milestone's
Required scope.

The fifth non-apparatus item from that pass, `PL-DJYF`, is **admitted above**
rather than declined, under the unconditional science exception.

**One more, captured 2026-09-19 — `PL-ZMGR`** (a `needs-decision` item whose
answer is "retire this" can never carry `falsifies:`, so every session-decided
retirement rejects its own close-out). It sits exactly where the nine apparatus
entries above do: found well after the 2026-09-06 freeze, `P2`, neither
`safety` nor `science`, and apparatus held to
`.claude/rules/apparatus-standard.md`'s deliberately lower bar. The mechanism it
describes is itself post-freeze - `PL-7TYC` was still repairing the assertion
check's matcher on 2026-09-17 - so the snapshot rule places it in the next gate
on its own terms rather than by exception. The refilling-queue arithmetic above
is unchanged and is still the reason.

**Two more from the second 2026-09-13 triage pass**, which folded in the two
the first pass had to defer plus six that merged in from other sessions while it
ran. `PL-SCB4` (the store has no status for an item whose decision is made but
whose work waits on a measurable condition) is wholly in the workflow lane and
sits exactly where the first thirty do: captured after the 2026-09-06 freeze,
`P2`, neither `safety` nor `science`, apparatus held to
`.claude/rules/apparatus-standard.md`'s lower bar. It is worth one extra
sentence, because it is *about* this gate: `PL-Z34C` is the live case, an entry
whose question is answered and which holds Gate 1 open because no status says
so. Admitting the fix would not release `PL-Z34C` any sooner than deciding
`PL-Z34C` on its own terms does.

**`PL-DHJ7` is not wholly apparatus and so needs its own ground**, which is
stated rather than stretched: it reaches `ROADMAP.md`, which is product
direction. It asks whether the roughly fifteen live subset counts in this
document gain checks on the `PL-GLBF` pattern. It is declined because it is a
correction to how this document accounts for its own queue and cannot reach a
reader of the simulator, which is the test the first twenty-nine were declined
on - and because it is `needs-decision` on a question about three different
kinds of count, which holding v0.5.0 open would not answer. Worth recording that
this gate's own declines are among the fifteen lists it names, this paragraph
included.

**Thirty-four more from the 2026-09-14 triage pass** (`PL-6FJ5`), which took the
45 captures the v0.4.2x range left untriaged and verified each finding against
the tree before assigning fields. Two of the 36 debt-classed results are
`safety` - `PL-27H0` and `PL-2K1R`, both admitted to the frozen list above -
and these thirty-four are declined, on two
different grounds, and the split is stated rather than averaged.

**Nine were introduced by this milestone's own implementation work, so the
presence rule defers them by its own terms** rather than by the
refilling-queue exception. "The gate is a snapshot" says a finding "defers to
the next gate only when the problem itself is new: introduced by work done
while clearing this gate or implementing the milestone it protects", and
`PL-B9PY`, `PL-J2TD` and `PL-TFX5` all landed in the week before this pass.
Each of the nine is a property of the branching machinery those three built:
`PL-59WB`, `PL-7TBQ`, `PL-7TXJ`, `PL-CZTR`, `PL-JFYT`, `PL-LLBV`, `PL-NC62`, `PL-SM5V`, `PL-XJ37`.

**9 predate the freeze and are declined on the refilling-queue ground**, which is
the one the first twenty-nine were declined on. The arithmetic is the argument
here as it was there: this gate stands at 166 entries with 15 open, and
admitting these would take it past 180 while it is finally draining. None can
reach a reader of the simulator with a wrong number - they are documentation of
internal structure (`PL-9KP5`, `PL-C4RS`, `PL-D1RT`, `PL-DBGT`), a
type that is not yet wrong (`PL-W3Q5`), and three numerical-envelope findings
that no shipped path reaches (`PL-2MD9`, `PL-73ZN`, `PL-BMY5`).
`PL-0MLZ` is the one to watch, and it is deferred with that said: it makes
`uv run pytest` able to run stale bytecode after a source restore, which is a
verification step lying in the direction of a false pass. It is declined only
because it is reachable by hand today - export `PYTHONDONTWRITEBYTECODE`, or run
through `make` - and it is recommended as the first thing taken off this list.
The full 9: `PL-0MLZ`, `PL-2MD9`, `PL-73ZN`, `PL-9KP5`, `PL-BMY5`, `PL-C4RS`, `PL-D1RT`, `PL-DBGT`, `PL-W3Q5`.

**16 sit wholly in the workflow lane**, which is the group this section was
written for: apparatus, held to `.claude/rules/apparatus-standard.md`'s lower
bar, none of which can reach a reader of the simulator.
`PL-0HPV`, `PL-0PJG`, `PL-2M5T`, `PL-4PC5`, `PL-BXB2`, `PL-FT3M`, `PL-FWJF`, `PL-J45M`, `PL-JW9J`, `PL-MBTZ`, `PL-R0P3`, `PL-V53R`, `PL-VFD8`, `PL-WNQT`, `PL-YNYK`, `PL-Z85N`.

**Twelve more from the 2026-09-15 triage pass over the twenty untriaged
captures open that day.** All twelve were captured on 2026-09-14 or 2026-09-15,
eight days or more after the 2026-09-06 freeze, so "The gate is a snapshot"
already places them in the next gate; they are written down because each is
debt - eleven classed `defect`, and `PL-9TNJ` by its `needs-decision` status -
and a reader finding one open would otherwise have to work out why it is
absent.

**Nine sit wholly in the workflow lane**, where the thirty before them do, and
are deferred on the same refilling-queue ground:
`PL-188T`, `PL-3DXV`, `PL-9TNJ`, `PL-B5DW`, `PL-LKGW`, `PL-RWBV`, `PL-T86P`,
`PL-VZYS`, `PL-Y5ZB`.

`PL-RWBV` is the one to watch among them, and it is deferred with that said: it
reports eight open items whose `touches` names a path that does not exist, and
`touches` is read as a membership test by the lane split, the concurrency graph
and the delegation guard alike - so a stale path fails open in all three at
once. `PL-CNCF`'s is the expensive instance: it still names the pre-rename
spelling of `core/run_definition.py`, and only the live path is in
`protected_paths`, so the item reads as delegable when it is not. It is recommended as the first of these nine taken
off the list.

**Three are product-lane and are not waiting on this gate at all**, which is
why they are recorded here rather than left to look deferred:
`PL-J0F7` and `PL-TCR5` are live defects in what the Qt chart shows a reader -
a hover box nobody has looked at rendered, and a hover readout that answers the
pointer's previous position and never re-answers a resting pointer while paused
- so both are seated `P2` and belong to the v0.4.26 port beat, ahead of this
gate on the timeline rather than behind it. `PL-QRD1` is `blocked` on
`PL-8PSW`, which decides whether a two-run dashboard needs a selector lock at
all, and no shipped entry point reaches the defect today.

**One more from 2026-09-15, on the same ground and worth naming rather than
listing** — `PL-SMN4` (a push run on `main` can be cancelled by a later merge,
so a commit lands with no whole-store verify at all). Captured nine days after
this gate was frozen, so the snapshot rule already places it in the next gate.
It is written down here because it is `defect`-classed and therefore debt, and
because a reader finding it open would otherwise have to work out why a
`P2` CI defect is absent from a gate this large.

**Two more from 2026-09-16, on the same ground and named for the same reason** -
`PL-2M4X` (`PL-J45M`'s `verify` and `touches` name a shell-hook suite that
cannot exercise `release.py`) and `PL-SYG4` (the digest's `RESERVED` verdict
names its evidence and no way out). Both were captured ten days after this gate
was frozen, so the snapshot rule places them in the next gate; both are `P3` and
sit wholly in the workflow lane, reaching no reader of the simulator. They are
written down because triage made them debt - `PL-2M4X` by its `defect` class and
`PL-SYG4` by its `needs-decision` status - and a gate this large owes a reader a
reason for every open debt item it does not hold.

Deferred rather than admitted on the arithmetic this section rests on, not on
its merits: it is a false guarantee in a workflow comment plus a narrow
coverage hole that `main`'s next successful run closes, and admitting it would
grow a gate that is not draining. It is the workflow lane, held to
`.claude/rules/apparatus-standard.md`, and reaches no reader of the simulator.

**Seven more from the 2026-09-16 triage pass** (`PL-0C6W`), over the fourteen
captures open that morning. All seven were captured on 2026-09-15 or
2026-09-16, nine and ten days after the 2026-09-06 freeze, so "The gate is a
snapshot" already places them in the next gate; they are written down because
each is debt - five classed `defect`, and `PL-6QZP` and `PL-PFK1` by their
`needs-decision` status - and a reader finding one open would otherwise have to
work out why it is absent from a gate this size.
`PL-1RTM`, `PL-6QZP`, `PL-7CSP`, `PL-99YZ`, `PL-PFK1`, `PL-Q8RQ`, `PL-Z9K5`.

**The arithmetic has changed under this section, and the ground is stated on
what is true now rather than recited.** The paragraphs above decline on a gate
"not draining" and then "finally draining"; `bin/docket wave` reads it today at
**170 entries, 165 cleared, 5 open - and 0 that this gate can clear**, all five
blocked on work outside it. So the refilling-queue argument no longer describes
the fact pattern, and a weaker version of it should not be borrowed. What
applies instead is simpler: the gate has done its job. Admitting seven
post-freeze apparatus findings would re-open a cleared gate and hold v0.5.0 -
a simulator milestone - behind workflow-lane debt, which is the outcome the
snapshot rule exists to prevent. The timeline also puts v0.4.26 ahead of
v0.5.0, so this gate is not even the beat that is due.

**Three of the seven describe problems that are themselves new**, which defers
them by the snapshot rule's own terms rather than by any exception: `PL-6QZP`
and `PL-PFK1` are second-order consequences of `PL-69JZ` and `PL-7XTS` (closed
2026-09-12 and 2026-09-15), and `PL-Z9K5` is a residual gap inside the
exemption `PL-ZYQC` produced (closed 2026-09-12). The other four - `PL-1RTM`,
`PL-7CSP`, `PL-99YZ`, `PL-Q8RQ` - describe problems that predate the freeze and
pass the presence test squarely; they are declined on the ground stated above,
with that said rather than blurred.

**Six sit wholly in the workflow lane**, where the groups before them do:
apparatus held to `.claude/rules/apparatus-standard.md`'s lower bar, none of
which can reach a reader of the simulator. `PL-1RTM` is the exception and is
named rather than quietly counted with them - its `touches` reaches
`docs/ARCHITECTURE.md`, which `docket.toml` deliberately keeps out of
`workflow_paths` because it is written for a reader of the simulator. Its
product-lane half is one sentence describing what a tooling check covers, not
anything a clinician could read a number from, so it is declined with the rest.

`PL-Q8RQ` is the one to watch among them, and it is deferred with that said: a
bare `pytest -k SUBSTRING` exits 5 when it matches nothing, so it reads as a
command correctly failing before the work and goes on reading that way
afterwards. `PL-S5YM` turned `main` red exactly this way, and four open items
carry the shape today. It is recommended as the first of these seven taken off
the list.

**Two more from the 2026-09-16 evening triage pass over the six captures open
that day** (`PL-Q0J1`). Six arrived across the day from four sessions, after
`PL-0C6W` cleared that morning's fourteen. Two are not debt (`PL-85NT` was
dropped, and `PL-M3YJ` is `infra`, which "What counts" says explicitly is not
debt), and two - `PL-2M4X` and `PL-SYG4` - were triaged concurrently on
`claude/pl-syg4-pl-2m4x-triage` and are disposed of by that branch, higher in
this subsection, rather than twice here. That leaves two.

**`PL-L4KX` is apparatus and sits exactly where the groups above do**: captured
after the 2026-09-06 freeze, `P2`, neither `safety` nor `science`, wholly in the
workflow lane. `bin/docket verify` REJECTs every close-out of a dropped or
`not-delegable` item, so the skill's own close-out step cannot reach `ACCEPT`.
The refilling-queue arithmetic above is unchanged and is still the reason.

It is also the one to watch, on the same test `PL-Q8RQ` is named under: it is
`CLAUDE.md`'s second compounding-friction test, a refusal firing routinely on
correct work. Every close-out that drops an item ends on a `REJECT` the session
has to talk past, which trains a reader to skim the block where a real
protected-path failure is printed - the cost `PL-69JZ` named. It is recommended
as the first of these taken off the list.

**One more from the same evening, found while starting `PL-L9RD`** - `PL-Y4YX`
(where the Qt styling layer lives: 27 `setStyleSheet` sites compose CSS from
`app/theme.py`'s constants, against a file whose own comment forbids it a
toolkit import). Captured 2026-09-16, `P3`, `defect`, neither `safety` nor
`science`, so the snapshot rule places it in the next gate like the two above.

*Its ground was rewritten on 2026-09-16 when `PL-L9RD` closed.* It read that
this was `blocked-by: PL-L9RD` and would resolve inside that item. It did not:
`PL-L9RD` closed having fixed the *symptom* - the `verify:` command that
required PySide6 in `theme.py`, and the false reason the file's own comment
gave for forbidding it - and left the question itself open on purpose, because
the project owner approved un-absorbing the interface pass rather than a
refactor of where styling lives. So the ground now is the ordinary one this
subsection rests on: apparatus, wholly in the workflow lane, deferred on the
refilling-queue arithmetic. It is `needs-decision` rather than `ready`, which
is what makes it debt at all.

**And one from the split of `PL-L9RD`** - `PL-Z4K6` (whether seven readout
columns is wanted on a 1 366 px laptop, which misses the seven-column width by
nine pixels). Captured 2026-09-16, `P3`, `ux`, and debt only because it is
`needs-decision`. Deferred rather than admitted because the interface it asks
about is one planned-milestone item 33 is going to redecide: the levers are the
readout font size and the panel padding, both of which the interface pass
sets, and the third - `WINDOW_SCREEN_FRACTION` - is the one this can answer
alone. Four columns is correct meanwhile, so the row degrades rather than
breaking, and holding a gate open on a question whose own answer says "leave
two of the three levers to item 33" would be holding it open on item 33.

**One is not apparatus and needs its own ground**, which is stated rather than
stretched. `PL-PGZF` records that `PL-GS3R` made the chart's column budget
follow the window width, so `assemble_chart_frame` costs 8.4 ms at 150 columns
and 15.4 ms at 1 601, where `PL-CNCF` measured only the fixed budget. Its
ground is the snapshot rule alone - captured ten days after this gate was
frozen, `P3`, `perf`, neither `safety` nor `science`. What is worth saying
beside that is a fact about its **Done when.** rather than a claim about who
can work it: the half that settles whether the interface has margin is the
*full* frame, assembly and paint together, and every figure this container can
produce is `QT_QPA_PLATFORM=offscreen` on a software rasteriser with no GPU,
which `PL-QXSB` already found reports 18-28 ms for a frame where nothing
changed. So the assembly half is measurable anywhere and the conclusion is not;
that is the `PL-X9T3` shape. It also names `app/chart_frame.py`, which
`v0.4.26 - the interface moves to Qt` is rewriting.

**Two more filed under `PL-8PSW` while it was being built, both about the
interface's move to Blender-style areas** — `PL-VN6M` (`TraceLegend` owns the
compartment-visibility state inside a widget) and `PL-TH35` (define the common
View contract every `app/` view implements). Captured ten days after this
gate was frozen, so "The gate is a snapshot" already places them in the next
one; they are written down because both are `refactor`-classed and therefore
debt, and a reader finding them open would otherwise have to work out why.

Neither is deferred on the ground this subsection restates for `PL-0C6W`'s
seven - that the gate has done its job and admitting post-freeze findings would
re-open a cleared one. `PL-TH35` is
`blocked` on the Qt port item that reserves for the area system, and the
roadmap's own ordering argument — planned-milestone item 34, "a view's contract
is whatever the area system requires of its contents, so views built first are
built against today's fixed layout and rewritten" — is why it *cannot* be
cleared ahead of that work rather than merely why it is not. `PL-VN6M` is the
one concrete violation of `.claude/rules/ui-areas.md` the same pass found: it
misdraws nothing today, because there is exactly one legend and one chart in a
fixed layout, and it becomes real only when the area system makes a second of
either possible — which is the same item 34. Both are product-lane, and both
are recorded here rather than left to look deferred.

**One more from 2026-09-16 was written down here as a deferral, and that was the
wrong disposition for it** — `PL-MN4J` (the chart hover names the agent and the
instant but not which run). Captured ten days after this gate was frozen, so the
snapshot rule places it in the next one, and seated `P1` because `checks.py`
will not seat a `safety` class lower.

**It is `Required scope`, not a deferral** (`PL-R7XK`, project owner,
2026-09-16, ratified - chosen over leaving it deferred here). The ground written
for it was sound and is carried across to the bullet in § "Required scope"
below: the display it concerns does not exist outside the feature this milestone
builds, so it cannot be cleared before the compare mode it is about. But that is
what § "Debt inside the milestone's own scope" is for, and a deferral is
something else. "The gate is a snapshot" makes `safety` not deferrable, and the
two records say different things about who is holding the item: a deferral says
the gate has released it, where `Required scope` says this milestone's
definition of done holds it. Only the second is true, and only the second stops
it being closed out of v0.5.0 unnoticed. It is unaffected by `PL-83LS`'s
`anticipated` carve-out above, which is a different shape - v0.5.0 builds the
feature this hazard needs, where item 34's findings wait on a milestone two
steps out.

**Eighteen more from the 2026-09-16 triage pass, in three groups.** All
eighteen were captured on 2026-09-16, ten days after this gate was frozen, so
"The gate is a snapshot" already places them in the next one; most were filed
by `PL-BNYF`'s area-model queue audit. They are written down with their reasons
rather than listed because each group carries a ground of its own, and because
a reader finding them open would otherwise have to work out why.

**Eight are apparatus, on the ground this subsection already states** —
`PL-1T6T` (re-test the refusal of compaction), `PL-2XM2` (reorder the docket
skill so its four acted-on modes survive post-compaction truncation), `PL-6YL1`
(a check for the verify-target class), `PL-B11M` (detect a silent model
fallback), `PL-C6XD` (one renderer for the `RESERVED` release verdict),
`PL-JTHW` (a cancelled `main` run reported rather than passed over), `PL-R0Q0`
(the safety-class gate advisory that fires forever), and `PL-Y1L0`
(`outstanding_roadmap_edits` naming the milestone section a cut has passed).
Every one sits wholly in the workflow lane and none can reach a reader of the
simulator, so the refilling-queue arithmetic above applies to them unchanged.

**Nine are the area model, and the gate cannot precede the thing they are
about** — which is the ground `PL-TH35` and `PL-VN6M` are already deferred on
two paragraphs up. `PL-NMTF` (no open item builds `ROADMAP.md` item 34's area
system) is the head of it, and the rest are `blocked-by` it or waiting on the
same scoping round.

**That scoping round happened on 2026-09-16, and it converts the deferral into
a placement.** `PL-NMTF` closed by scoping item 34 as § "v0.6.0 - the layout is
the reader's" and a v0.7.0 row for break-out, so eight of the nine are now named
in v0.6.0's `Required scope` and are milestone-scope debt cleared *by* that
milestone rather than before it, per § "Debt inside the milestone's own scope".
The ninth, `PL-J4NW`, closed in the same session. The entries below are left as
the freeze wrote them, per § "The gate is a snapshot, not a moving target"; this
paragraph is their disposition.

**Eight more were filed by that scoping round itself, and are disposed of here
rather than added to the list.** Five are v0.6.0 `Required scope` and are
cleared by that milestone under § "Debt inside the milestone's own scope":
`PL-K285` (an Area that cannot be given the size its View needs says so
rather than collapsing it), `PL-904Y` (the whole-interface visibility predicate,
which stops meaning "can the reader see it" once an Area can be closed),
`PL-G5SX` (the headless tests that drive every layout operation against the
required set), `PL-50PZ` (the View chooser and the registry flag that make the
accounting tier reachable) and `PL-JSY5` (two `docs/MODEL.md` statements that
assume one window's width and one permanent surface). `PL-Y04W` (build
break-out) is v0.7.0's by the same rule one release further out. The last two
are neither: `PL-KKRP` (re-examine the debt gate's own freeze trigger) is a
decision about the cadence rather than debt against a milestone, and `PL-NDKC`
(PySide6 segfaults on `QDataStream` over a temporary `QByteArray`) is a
toolkit defect found while measuring, filed so the persistence work meets it
already written down. Every one of them is `anticipated`, and since 2026-09-16
that is a rule rather than a ground this subsection states for itself
(`PL-83LS`): § "The gate is a snapshot, not a moving target" makes an
`anticipated` finding **not debt until the hazard it describes exists**. The
splitter handles are inert today, so none of these hazards exists until the
milestone that creates them is built, and a gate that clears debt *before* a
milestone cannot clear a hazard that milestone introduces. So these are not
deferred here: they are not debt against this gate at all, and the placement
named for each above - v0.6.0's `Required scope`, v0.7.0's, or neither - is the
whole of their disposition.

Four of the nine are `safety`-classed, and it is worth saying what that used to
mean here and no longer does: `PL-7Z84` (a run has no identity a workspace can
pin to), `PL-9LNF` (three `app/` surfaces own state a layout could duplicate or
relocate), `PL-NWTM` (the unconditional displayed set has no structural home in
the code) and `PL-W54S` (what a broken-out top-level window owes that set). The
presence rule re-entered them here regardless of when they were found, and this
subsection then had to argue them back out one hazard at a time - which is the
argument `PL-83LS` turned into the rule above. Each is classed `anticipated`, so
none of the four is debt against this gate: the splitter handles are inert today
(`src/anesthesia_sim/app/qt_widgets.py:784`), and no reader can close, replace
or cover a required value until item 34 makes them live.

Each of the four is named in v0.6.0's `Required scope`, which is where the rule
puts a hazard rather than where a deferral would leave it: the milestone that
creates it is the one that carries the guard. `tools/doc_check.py`'s
`check_gate_reentries` now passes over all ten `anticipated` findings on the
class and the `blocked` status that dates it, rather than on this prose, so what
these paragraphs record is the reasoning and not the mechanism holding it. All
ten are blocked on item 34 today; each returns to the gate when it is promoted,
which is when the hazard it names has been built.

`PL-9PD6` (`docs/interface-provenance.md` contradicts itself about what
`README.md` records), `PL-D584` (`PL-TH35`'s `blocked-by` names an item that has
since closed, so the store advises every run that the View contract is ready
to promote) and `PL-J4NW` (`docs/ARCHITECTURE.md` routes every new display panel
by a fixed two-level layout) are startable today, and are deferred on the
ordinary snapshot ground instead: post-freeze `defect`s, neither `safety` nor
`science`, whose problems do not predate the freeze. `PL-L8RN` (nothing enforces
the one-adapter `QSplitter` confinement) is deferred because the boundary it
would declare has no tree to sit over until the adapter exists.

**One was the release train's own numbering, and it has since been answered** —
`PL-KQHN` (`ROADMAP.md` § "Completed: v0.4.26 - the interface moves to Qt" said both that a
patch cut takes this section's number and that the guard withholds it). It is
product-lane, so this subsection's workflow-lane ground never reached it, and it
was `needs-decision` on a question `CLAUDE.md` puts on the project owner's side
of the division of labour: what the release train does when a patch is cut
mid-port. Answered 2026-09-16 (ratified) — the guard withholds the number — and
closed with the prose correction that answer required, so unlike `PL-MN4J` above
it no longer waits on anything. The entry stays as the record of why it sat
here; it defers nothing now.

**Six more arrived with the 2026-09-16 triage pass (`PL-554Q`) and are disposed
of here rather than added to the list.** Four are post-freeze `defect`s in the
apparatus, neither `safety` nor `science`, whose problems do not predate the
freeze, and they are deferred on the ordinary snapshot ground: `PL-7K8Y`
(`docket record` normalises front-matter key order as it writes `pr:`, so
`docket verify` reads the backfill as a content edit), `PL-DMDF` (`docket digest`
asks one `git diff` per item file because `_superseded` is called with a
one-element tuple inside a loop), `PL-SH9Q` (`docket stranded` misses an item the
base already carries and a branch has modified) and `PL-WXX8` (merged items owe a
`pr` number and the advisory's remedy addresses the one population that is not
holding the debt). Every one sits wholly in the workflow lane and none can reach
a reader of the simulator.

The other two wait on answers rather than on attention, as `PL-KQHN` does.
`PL-7RYB` (nothing distinguishes a decision the owner ratified from one they
specified, on anything recorded before 2026-09-16) is `needs-decision` on what
their own past decisions meant, which is theirs rather than a session's.
`PL-NLP4` is this subsection's own closing paragraph, whose "66 dispositions" has
not been true for some time; it is `blocked-by` `PL-B8V1`, which holds the same
question one paragraph over, and its `Done when.` requires one answer to cover
both rather than two answers to cover one each. That is also why the figure is
left as it stands here: correcting it in place would pick the form `PL-B8V1` is
open to decide.

`PL-KND7` joins them, filed the same day and waiting on the same kind of answer:
`main` has been red since `52205f6` because `PL-D1RT`'s `Done when.` was
overtaken by two decisions of record - the interface pass's un-absorption
(`PL-L9RD`) and its move after item 34 (`PL-PHKP`) - so what becomes of that item
is the project owner's rather than a session's. It is workflow-lane and reaches
no reader of the simulator.

**Two more from the 2026-09-17 triage of the `preferences-store` captures, on a
ground none of the paragraphs above states.** `PL-0S0V` (display precision
becomes a function of quantity *and* unit once the unit is reader-selectable)
and `PL-VJZK` (a reader-set price needs its currency, the date it was set and
whether it is the shipped default, and must not read as an authority) are both
`safety`-classed and both `anticipated`. The `anticipated` rule is what disposes
of them, and it is stated in full in the v0.6.0 section rather than here: an
`anticipated` finding is not debt until the hazard it describes exists, and a
gate that clears debt *before* a milestone cannot clear a hazard that milestone
introduces. Nothing in this application is reader-selectable today, so neither
hazard exists to clear.

They differ from the four `anticipated` entries that section argues out in one
way only, and it is the reason they are recorded here rather than placed: those
four are each named in a `Required scope`, and these two have no milestone to be
placed by. The readouts they constrain are planned-milestone items 24 and 28,
which no release names. So this is the whole of their disposition, and it
expires the day either item is placed - at which point they belong in that
milestone's `Required scope` on exactly the terms the four already there hold.

**Ten from the 2026-09-17 triage of the twenty-six untriaged captures**
(`PL-Y4D6`). Two grounds, and they are not the same ground.

*One on the anticipated ground, which is the v0.6.0 section's rather than this
one's.* `PL-KZ99` (store each agent's molar mass and liquid density with the
density's measurement temperature) is `science`-classed and would be undeferrable
on that alone. It describes a hazard a later milestone creates — no
vapour-to-liquid conversion exists today — and it is `blocked` on `PL-S6WW`, so it
takes the carve-out that `anticipated` and `status: blocked` hold together.
It is the same case as `PL-0S0V` and `PL-VJZK` above, against the same
planned-milestone item 28, and takes the same disposition for the same reason:
item 28 is named by no release, so there is no `Required scope` to place it in.
It expires the day item 28 is placed.

The two findings against items 24 and 28 that arrived with it — `PL-H4N8` (cost
is the delivered amount, not the exhausted one) and `PL-QBX0` (item 24's gate
misses the ISO 5360 colours and the contrast-checked palette) — are **not** here.
Their hazards are anticipated in the same way, but their fix is a sentence in the
planned-milestone entry itself, so neither is blocked on anything and neither
takes the carve-out. They are on the frozen list above, added under the
unconditional exception, which is what `tools/doc_check.py` requires and says so
in terms: deferring is not a third option for these two classes.

*Nine on this subsection's own refilling-queue ground.* All were captured on
2026-09-16 or 2026-09-17, all are apparatus or documentation findings, and none
completes an entry already on the frozen list: `PL-4RHP` (this subsection's own
entry count is outside `check_gate_counts`' reach), `PL-B396` (whether item 28 is scoped at all, which is a milestone
decision rather than gate work), `PL-KF0T` and `PL-YD6X` (planned-milestone items
33 and 24 describe closed work as open), `PL-KSCW` (`stranded` sees a missing
item file and not a missing *section* of one), `PL-LBW5` (a `verify:` command naming a
path its own `touches` omits), `PL-M21Q` (a `needs-decision` item
carries the question and not the recommendation), `PL-SY1J` (`bin/docket show`
named the later of two branches carrying one item) and `PL-XD3C` (`digest`'s cost
grows with the item edits unmerged refs carry, and nothing prunes).

**The compounding-friction test was applied to two of the nine and neither
passes it.** `PL-SY1J` is the closest, handing a session a confident verdict that
names the wrong carrier, and `PL-XD3C` is the one that grows. The test is
arithmetic — name what each remaining entry pays and multiply — and neither is
paid per remaining entry: what remains of this gate is the milestone's own work,
while an in-flight verdict naming one carrier costs the sessions that collide and
`digest`'s growth costs every session equally whether this gate is open or shut.
No per-entry saving can be named, so both wait, which is what "work that is
merely valuable makes no remaining entry cheaper" says to do.

**Two more from the macOS Dark appearance defect** (`PL-DHBX`, 2026-09-17,
closed with the fix). The project owner found the Start, Pause and Reset labels
missing in Dark appearance; diagnosing it produced two findings that the fix
itself does not settle, filed under `feature: platform-palette`. Each needs its
own ground, because neither is wholly in the workflow lane.

`PL-4L49` — that `tools/contrast_check.py` measures only *declared* pairs, so a
control declaring no colour reads as covered — passes the presence test: the
check has had that limitation since long before this freeze, and it is why
`PL-DHBX` could ship. It is declined on the refilling-queue arithmetic above
rather than on its lane: it is `defect` and `infra` rather than `safety` or
`science`, the one instance it would have caught is closed, and the gate is
already the largest this project has held and is not draining. `PL-BXB2` is the
nearest admitted precedent and is unlike it in the way that matters — a colour
measured by nothing there could be an ISO 5360 agent colour, which is why that
one was `safety`; an *undeclared* control cannot be, since every
identity-carrying control is written by `_apply_agent_color_scheme` and guarded
by `tools/agent_identity_check.py`.

`PL-KRZW` — whether the application declares a Light colour scheme to Qt, leaves
the host appearance alone, or grows a second palette — is a decision this gate
should not force, on the same ground as `PL-3JP0` and `PL-HKTB` above. Its
Qt-specific form arrived *with* the port on 2026-09-14, after this freeze, so it
does not pass the presence test in the first place; and the `v0.5.x` interface
pass is where the interface's visual decisions are made once, which is where
answering it is cheapest. What the fix already guarantees is unaffected: every
colour that carries meaning is declared, so the decision changes the chrome
rather than the legibility of anything a reader acts on.


**One from `PL-BHVM`'s design round** (`PL-MM7F`, 2026-09-19). That round
measured `vcs.py`'s evidence layer and found that `GitRunner` stores a failed
git call in its memo exactly as it stores a real answer, so one non-zero exit
is served to every later caller in the session. It is declined on this
subsection's own refilling-queue ground: it was captured after this freeze, it
is `defect` rather than `safety` or `science`, and it completes no entry on the
frozen list.

The gate could not clear it in any case. It is `status: blocked` on `PL-Q9Z1`
(`_superseded` reads a failed git diff as the tips agreeing about every path),
which is untriaged and on no list here - until the evidence layer can say a
call failed, nothing can tell a failure from an empty answer worth caching. Its
sibling `PL-73P0` (`default_base` falls back to a guessed `"main"`) is
untriaged and so is not debt by the rule above; it reaches this gate only if a
triage pass classes it, which is the next gate's question.

**Eleven from the 2026-09-19 triage pass** (`PL-3BYK`, `PL-6T44`, `PL-8T83`,
`PL-C97K`, `PL-G6J5`, `PL-K1WS`, `PL-QJQL`, `PL-S0MB`, `PL-TKFD`, `PL-XZD0`,
`PL-Z6M3`). That pass seated nineteen untriaged items and so turned these eleven
into debt by § "What counts" — five classed `defect`, one `perf`, and five left
at `needs-decision` — where until then neither a class nor a triaged status made
any of them count. Each is declined on this subsection's own refilling-queue
ground, and the three facts that ground rests on hold for all eleven: every one
was captured on 2026-09-17 or later, eleven days past this freeze; none is
`safety` or `science`, so neither unconditional exception reaches them; and each
sits wholly in the workflow lane on `docket.toml`'s own `workflow_paths`
reading, so none can reach a reader of the simulator. The two from the same pass
that *are* `safety` or `science` — `PL-JVHL` and `PL-7DMJ` — are admitted above
rather than listed here, which is that boundary deciding the split rather than a
session doing it by hand.

The gate's own state is why the ground still holds. It stands at 173 entries
with five open; admitting eleven more would put two thirds of what remains on
apparatus findings a session made about its own tools, at the beat whose entire
content is "clear the gate". `PL-73P0` is the one case this section had already
disposed of in advance — the paragraph above it reads "it reaches this gate only
if a triage pass classes it, which is the next gate's question" — and the pass
classed it `defect`, so that sentence is now its recorded disposition rather
than a forecast, on exactly the same ground as the eleven.

**One from `PL-VYSP`'s design round** (`PL-2BZY`, 2026-09-19). That round found
that `branches_in_flight` kept one ref per id before `_taken_on_base` judged
the claim, so a bystander branch whose pull request had squash-merged deleted
the id from the report's do-not-start line and took two live design rounds'
claims with it: `PL-HWW1` and `PL-6TP8` read startable while `keen-cannon` and
`eager-brown` carried them. It is declined on this subsection's own
refilling-queue ground - captured after this freeze, `defect` rather than
`safety` or `science`, wholly in the workflow lane, and completing no entry on
the frozen list. `PL-LKFP`, which added the guard it defeats, was itself
captured after the freeze and is closed, so nothing here is left half-done by
declining this.

Its two siblings are the same collapse in front of the other two per-ref tests
in that function - `PL-RY2R` (`walk.edited` before `_superseded`) and `PL-61MD`
(`own_edits` before `_superseded` and the `needs-decision` promotion). The
session that started them classed both `defect` the same day, so the forecast
this paragraph carried - that they reach this gate only if a triage pass classes
them - is now their recorded disposition, on the same refilling-queue ground as
their sibling above and on the same three facts: captured after this freeze,
neither `safety` nor `science`, and wholly in the workflow lane. Both closed in
the branch that recorded them, so the gate never held either open; the
disposition is written because the presence rule asks for an answer in writing,
not because anything is outstanding.

That closes `feature: carrier-collapse`, which was named for what completes:
no reading in `branches_in_flight` now picks one carrier per id ahead of a guard
that judges carriers. `precedence`, the fourth reader of the same walk, never
collapsed - it keeps every candidate and sorts them - so the three are the whole
of it.

**One more from closing `PL-QJQL`** (`PL-XQGH`, 2026-09-19). Teaching the
assertion check to see `with pytest.raises(...)` anchored the new alternative on
the `with` keyword, which is the right anchor for every shape this tree writes
and gives up one it does not: the parenthesized multi-manager form, where
`with (` opens the statement and the expectation sits on a line of its own. It
is declined on the ground the first thirty sit on - found after the 2026-09-06
freeze, `P3`, neither `safety` nor `science`, and wholly in the workflow lane,
so it cannot reach a reader of the simulator. One thing this entry can say more
strongly than most: the hazard is not live. `ast` reports zero multi-manager
`with` statements of any kind across the tree's 97,687 lines, so there is
nothing for the blind spot to hide today, and what would make it live is a
condition on the tree rather than an argument - which the item records, so a
later session checks it instead of re-deriving it.

**Seventeen from the 2026-09-19 triage pass** (`PL-2P9L`). Twenty-one items
stood untriaged that morning, every one of them captured that same day, and
classing an item is what makes it debt - so they reach this gate together and
are declined together: `PL-245B`, `PL-28HG`, `PL-2DTK`, `PL-4FD2`, `PL-4HKS`,
`PL-BX1C`, `PL-CNJH`, `PL-CWD4`, `PL-D1NT`, `PL-DK8Y`, `PL-QMC0`, `PL-R77L`,
`PL-SZJ2`, `PL-WVJ0`, `PL-Y5JX`, `PL-YS9F` and `PL-ZPDM`. One of them,
`PL-QMC0`, closed in `#708` hours later and is left named here rather than
removed: what this subsection records is the disposition taken, and an entry
that was declined and then fixed anyway is still an entry that was declined.
`PL-0VFF` is the open item for the fact that nothing here distinguishes the
two. The three facts the
first thirty rest on hold for all seventeen: captured after the 2026-09-06
freeze, `P2` or `P3` and neither `safety` nor `science`, and wholly in the
workflow lane - every `touches` they declare is inside `docket.toml`'s
`workflow_paths`, so none can reach a reader of the simulator.

**The arithmetic above has reversed since it was written, and it now argues
the same way harder.** The paragraphs at the head of this subsection defer on
the ground that this gate "is not draining"; today it stands at 168 cleared of
175, with four entries left that it can clear. That premise is stale, and the
conclusion it supported is not: admitting these seventeen would take the
clearable remainder from four to twenty-one and move a milestone that is one
beat from starting back behind five times the work it currently waits on. A
gate one step from opening is the point at which "The gate is a snapshot, not a
moving target" is doing the most work, not the least - the temptation to fold
in the day's findings is strongest exactly when the list is nearly empty. Any
of the seventeen whose *problem* predates the freeze belongs on the list rather
than here, and `check_gate_reentries` is what decides that rather than this
paragraph.

**Eight more from the 2026-09-19 triage pass over the twelve untriaged
captures** (`PL-CSV0`). `PL-9KSY`, `PL-G424`, `PL-STC4`, `PL-VKGJ`, `PL-X3NY`
and `PL-YRYR` sit exactly where the first thirty do: captured on 2026-09-19,
well after the 2026-09-06 freeze, `P2` or `P3`, neither `safety` nor `science`,
and wholly in the workflow lane - every `touches` they declare is inside
`docket.toml`'s `workflow_paths`, so none can reach a reader of the simulator.
The arithmetic that the paragraph above says now argues harder is unchanged and
argues the same way here: this gate stands at 170 cleared of 175 with two
entries it can clear, and admitting eight would take that remainder from two to
ten at the beat where the milestone is one step from starting.

**`PL-G424` is a recorded generator, and that is a statement about its rank
rather than about this gate.** It carries `root-cause-of:` naming twenty-one
members, so `CLAUDE.md` ranks it above every band but `P0` and `bin/docket
next` will offer it ahead of the two entries this gate still holds. Declining
it here does not park it: a gate decides which findings a milestone waits on,
and the generator tier decides what a session picks up. Both answers are
recorded deliberately, and the second is the one that governs what happens
next.

**Two of the eight are not wholly apparatus, which is stated rather than
stretched.** `PL-HCTF` declares `ROADMAP.md`, and its subject is this
subsection's own stated entry count - which `#706` left at `174` while adding an
entry, and which nothing validates at `174`, `191` or `999`. It is a correction
to this document's account of its own queue, so it cannot reach a reader of the
simulator, which is the test `PL-0VFF` and `PL-880Z` were declined on above.
`PL-WPDB` sits in the product lane on `tests/benchmarks/`, and is declined on
the narrower ground that a frame-cost measurement is a number about this
repository's rendering budget rather than a clinical one: no reading of it
reaches a displayed value, so the safety exception that admitted `PL-DZFJ` does
not reach it either. It is `v0.5.0`'s own frame cost it leaves unmeasured,
which is an argument for doing it during that milestone rather than for holding
the gate open ahead of it.

**One more, raised by the project owner while the pass above was running, and
answered in the same session** (`PL-TQFB`). It asked whether a housekeeping
item should have to argue for its own category, on the measurement that 22
triage-pass items carry 1,127 lines of brief of which only 2 hold a finding.
The entry stays for the record rather than as a deferral: the owner ratified
route 1 the same day and the item closed, so this gate never waited on it. Had
it stayed open it would have sat on the refilling-queue ground as the first
thirty do - it declares the `docket` skill, `checks.py`, `render.py`,
`config.py` and `docket.toml`, all wholly inside `docket.toml`'s
`workflow_paths`, so none of it can reach a reader of the simulator.

**It is inside this section rather than beside it because the checker reads
only one.** `tools/doc_check.py`'s `_declined_ids` takes the first
`### Declined to Gate ...` subsection after the gate heading and stops at the
next heading of any level, so a second one silently orphans this section's 66
dispositions - the gate then reports them all as undisposed. `PL-82B0` carries
the defect.


**One more from the 2026-09-19 workflow-lane survey, on the same ground.**
`PL-LSR0` (`tools/generator_check.py` cannot see a store-drift generator:
`clusters()` partitions by a single `touches` path and `STORE_PATHS` excludes
`docs/items` and `docs/WORKING_NOTES.md`, where 15 of `PL-G424`'s 21 members
sit) was captured that day and triaged to `needs-decision`, which is what makes
it debt this gate has to dispose of. It is `P2`, neither `safety` nor `science`,
and wholly in the workflow lane.

**The predates-the-freeze argument was considered and refused, and it is the
closest call in this section.** `STORE_PATHS` is long-standing code, so the
*blind spot* plainly predates 2026-09-06 and `check_gate_reentries`' test is
the one this entry has to survive rather than assert its way past. What did not
exist at the freeze is the thing that makes it debt: the `impairs-generators:`
field was built on 2026-09-19 (`PL-G5ZH`), and before it there was no way to
say that a defect in the identification machinery ranks with a generator — so
the *finding* is new even though the code is old. Against that, this gate stands
at 173 of 175 cleared, and admitting an `M`-effort design decision to a gate two
entries from draining is precisely the refilling shape Phase 0 was retired for.
The blind spot has stood through eight recorded generators without preventing
one from being found by hand; it will stand through v0.5.0.

**Two more on the model-capability reference, 2026-09-19.** `PL-13PB`
(`docs/maintainer.md` names no model behind "the strongest available model", so
`bin/docket next`'s per-item strongest-model flag cannot be resolved by anyone
reading it) and `PL-V8QG` (the same file recommends `opusplan` as the default
strong/cheap split, which names the wrong family if the strongest model is not
an Opus). Both were captured that day, both are `P2`, neither is `safety` nor
`science`, and both sit wholly in the workflow lane.

They are deferred rather than admitted even though the flag they undermine
fires on `safety`- and `science`-classed items, because what they fix is the
*reference* a human reads when choosing a model, not any code path that
produces a clinical value: `CLAUDE.md`'s safety-critical standard reaches the
value and its presentation, and the maintainer still reviews every
safety-critical diff whatever model drafted it, which is the backstop that makes
this deferrable. The observation that prompted them — `PL-G424` started on a
weaker model than `PL-LSR0` while both carried the flag — cost nothing that a
gate entry would have prevented.
**One more from the v0.4.30 cut, 2026-09-19.** `PL-5MFL` (`bin/docket verify`'s
suppression check matches the line alone, so a `ROADMAP.md` prose line quoting
`xfail` is read as an added suppression and every release cut ends `REJECT`).
It is the one entry declined here whose *problem* squarely predates the freeze
rather than qualifying by argument: the scan has ignored the path since `docket
verify` landed on 2026-08-25 (`PL-D7JQ`), twelve days before this gate was
frozen on 2026-09-06.

It is deferred anyway, on the refilling-queue ground and on the shape of the
harm. The check is one of the four integrity checks `--self` deliberately does
not relax, so the failure is loud rather than silent, and what it costs is a
paragraph of explanation in a close-out rather than any wrong result reaching
anybody - `PL-SW0D`, the cut that met it, reported it and closed. Nothing it
touches is reachable by a reader of the simulator: `subprojects/docket/` sits
wholly inside `docket.toml`'s `workflow_paths`. Against that, and on the same refilling-queue arithmetic as the
groups above, this gate stands two entries from draining - 170 of 175 closed,
with three of the five still open blocked on work outside it - and admitting
one more at the beat where the milestone is one step from starting is the
refilling shape Phase 0 was retired for.

### Required scope

Eighteen items, in the order the dependencies allow. The first three are the
score architecture the 2026-09-05 design round filed and the project owner
placed here; the next five are boundary work this milestone's own code moves;
the last ten are the feature itself.

**Two more were required here and are already done** (`PL-C4RS`, 2026-09-19).
`PL-2FM6` deleted `RunHistory` so the chart is drawn from the sampler - where
`PL-011`'s dropped growth debt was actually paid - and `PL-8LXM` deleted the M4
decimation path with it, including its tests, the cited paper and every
reference to them: a sampler answering a window in closed form has nothing to
decimate. Both moved into the `v0.4.x` track on 2026-09-08 and shipped there,
which is the move whose own note said "Required scope below drops to sixteen
items", and they sit on the frozen gate under the heading that says so. They
are named here without a declaration slot deliberately - the milestone required
them and the patch track cleared them, and neither fact is this section
placing them.

- **The run becomes a closed-form function of its control-input timeline**
  (queue item PL-T691). Keyframes are held at every control event and any
  window is answered in closed form, so state at a time is computed rather
  than looked up. This is the head of the milestone: everything below it that
  touches a run depends on it, and it is what makes a branch's pre-branch
  history the same object as its parent's.
- **The canonical evaluation rule that carries determinism** (queue item
  PL-P1Z3). Once a time can be reached by more than one route — stepped to, or
  evaluated from a keyframe — "identical inputs give identical results" needs
  a rule saying which route is authoritative, stated in `docs/MODEL.md` and
  gated by test. Safety- and science-classed, and not deferrable within this
  milestone.
- **A path-scoped rule against re-introducing a sample store** (queue item
  PL-49R8), so a later session adding a convenience buffer is told why the
  store is absent rather than rediscovering it.
- **The controller's trace vocabulary and its UI-to-core boundary are
  separated** (queue item PL-RD3B). Two runs need the boundary, and each needs
  its own drawn window addressed through the same vocabulary. **Re-briefed
  2026-09-14** (`PL-5328`): this entry read "The controller's storage ...
  without a second copy of the storage" until `PL-2FM6` deleted the store, so
  what is left to separate is the vocabulary a trace is addressed by and the
  window a frame draws, not a store. The scope is unchanged; only the noun
  was stale.
- **The snapshot stops naming six flat compartment floats** (queue item
  PL-TCD1), so a readout can name which run and which substance it describes.
- **The control-input timeline is bounded and stops being regrouped in full on
  every frame** (queue item PL-1PSX). It is read on every branch operation
  here, not only drawn.
- **`SimulationView` is decomposed so two runs can be rendered at once** (queue
  item PL-B9PY). Held at this gate by v0.4.0 on the grounds that only this
  milestone needs it (project owner, 2026-09-02); this is that milestone.
- **The 30-day scenario cap becomes an explicit halt** (queue item PL-Y5WR).
  Safety-classed, and its only requiring item was dropped with `PL-011`, so it
  is carried here rather than lost.
- **A fork resumes into a live run** (queue item PL-J2TD): a run is opened at a
  canonical keyframe state of another run, on the case's own clock and with its
  run definition opening at the fork instant, and advances from there by the
  path a live run already takes. A branch has to become something a learner can *manage*, which
  is what separates it from a second curve, and it is what item 12's fork and
  the in-loop crossing detection two bullets down both presuppose. Internal: no
  user-facing replay control, which stays planned item 10 behind item 9's
  save/load.

  **Narrowed 2026-09-14** (project owner) from "a recorded control timeline can
  be applied to a run ... the mechanism by which a point *between* recorded
  samples is reached at all", which the first bullet of this list has since
  made wrong twice over. `PL-T691` delivered the applied timeline: a
  `RunDefinition`'s segment list *is* the recorded timeline and `state_at`
  answers any instant of it in closed form, so a point between recorded samples
  is already reached, and `tests/integration/test_controller.py` asserts the
  reproduction to 6.7e-16 as a fraction of one atmosphere. The bullet's other
  half — a resimulation driver sharing the live advance path — is now refused
  by § "The canonical evaluation rule", which takes every replayed, compared or
  branch-opening value canonically: a driver re-driving the fixed step path
  composes a third order of floating-point operations, measured there at
  1.8e-14 from the canonical answer, and the branch-reproduction entry below
  asserts element-wise equality rather than a tolerance. What was left once
  both halves went is the resumption, and that is what this entry now asks for.

  **Mechanism replaced 2026-09-14** (project owner, queue item PL-ZMRT), with
  the scope unchanged. This entry read "with its clock re-based by subtracting
  the fork instant" until the fork was built and drawn. That arrangement gave
  the branch a second time frame - the clock on the case's axis, the definition
  on its own - and made exactness conditional on every caller subtracting the
  fork instant rather than naming the branch's own elapsed time. What ships
  instead opens the branch's definition *at* the fork on the case's axis, so
  there is one frame, `SimulationController.origin_s` and both subtractions are
  gone, and the round-trip hazard the old rule guarded against is
  unrepresentable rather than forbidden. It also dissolves PL-2R2C - a branch's
  drawn columns anchored to its own zero, landing at case instants the trunk
  never draws - which needed no fix of its own once both runs shared an axis.
  `docs/MODEL.md` § "The canonical evaluation rule" carries the measurements.
- **Time bookmarks and MAC targets, as two separately listed collections**
  (queue item PL-LPLD). The Gas Man reference simulator's own shape, and its
  scope floor: an absolute simulated time, and a percent of MAC on any graphed
  compartment rather than the alveolar trace alone. Kept as two kinds rather
  than one kind with a field, so a list can show them the way the reference
  does.
- **Crossings are detected inside the advance loop** (queue item PL-CTD7), with
  an explicit not-reached outcome that reads differently from a reached one.
  Testing per rendered frame overshoots by the frame's worth of simulated time
  and worsens with the playback multiplier, so the same bookmark would halt at
  a different concentration depending on how fast the learner was running —
  a presentation-correctness failure by `CLAUDE.md`'s standard, and one that
  also breaks reproducibility of any branch taken there.
- **A run forks at any control-input event** (queue item PL-TFX5), flat rather
  than as a tree: one trunk with N branches, and no sub-forks. The branch
  carries its parent's agent and patient rather than re-choosing them.

  **Split 2026-09-14** (project owner). This entry read "at any control-input
  event **or bookmark**" until the fork was built, and the bookmark half turned
  out not to be unbuilt work but a *refused* operation: a bookmark's instant is
  not in general a keyframe, and the keyframe-only rule `PL-J2TD` landed
  deliberately admits no other opening. On the 120 s two-change run the fork
  tests use, 3 of the 1 201 instants a halt could land on are keyframes. The
  clause is the entry below, behind the two items that build a bookmark and its
  halt; what this entry keeps is what shipped.
- **A bookmark is a forkable instant** (queue item PL-B8MK), so a branch can be
  taken where a learner deliberately stopped rather than only where they moved
  a control. Two routes are measured in that item and the obvious one is the
  worse: recording a keyframe where the run halts makes the branch exact
  against the trunk it forked from, while moving that trunk's own later answers
  away from what the case would have said unmarked - so marking a run changes
  it. Opening the branch's definition at the keyframe *before* the bookmark
  costs the trunk nothing and is exact too. Behind `PL-LPLD` and `PL-CTD7`,
  which build the bookmark and the halt it would be recorded at, and ahead of
  the entry below, whose branch "taken between two recorded samples" is this
  one.
- **The branch reproduces its parent element-wise up to the branch point**
  (queue item PL-Z3W6), asserted by test at every sampled point rather than
  within a tolerance. Where exactness is unreachable the divergence is bounded,
  documented, and shown rather than implied to be absent.
- **Two branches are overlaid on one time axis** (queue item PL-8PSW), with the
  **compartment on line style and colour exactly as the single-run chart draws
  it, the run on line width, and at most two compartments drawn while two
  branches are shown**. The branch point is marked. Decided against two stacked
  panels sharing a time axis (project owner, 2026-09-06): the comparison is the
  whole point of the release, and stacking makes the eye travel to do it — a
  choice the evidence supports, since shared-space line graphs are the more
  efficient technique for comparisons over *small* visual spans, which is what
  comparing one compartment against itself under two settings is (Javed W,
  McDonnel B, Elmqvist N. *Graphical Perception of Multiple Time Series.* IEEE
  Trans Vis Comput Graph. 2010;16(6):927-34. doi:10.1109/TVCG.2010.162).

  **Which run carries the width offset was settled when it was built**
  (`PL-8PSW`, 2026-09-16, project owner). The first run is drawn wider and the
  second keeps the width the single-run chart draws it at. `PL-HLD5` had
  assumed the two curves are merely adjacent; they are not, because the entry
  above requires a branch to reproduce its parent element-wise up to the fork,
  so before the branch point they coincide exactly and whichever is thicker
  hides the other entirely over that stretch. Widening rather than narrowing
  also keeps every trace at or above 2 px, where a 1 px antialiased line
  renders lighter than its declared colour and walks into the 3:1 floor
  `.claude/rules/ui-color.md` treats as an error. `docs/MODEL.md` § "The six
  compartment traces" carries it.

  **The channel assignment is reversed from what this bullet said until
  2026-09-07, and the compartment cap is what makes it possible** (`PL-HLD5`).
  It read "the run encoded by line style and the compartment by colour", which
  `PL-GVXP` established the next day is not available: `docs/MODEL.md` § "The
  six compartment traces" measures the worst trace-against-trace pair at
  **1.01:1** against a 3:1 requirement, so colour cannot carry six categories
  here and re-picking the palette does not reach it. Line style is the only
  non-data channel with six-category capacity, so the compartment keeps it.

  That leaves nothing free for the run at six compartments — line style,
  colour and width are all already spent, width varying 2 px to 3 px across the
  six. **Capping the drawn compartments is what frees width**, which is why the
  cap is load-bearing rather than a convenience, and why "one shared compartment
  selection across both runs" is now a constraint the design rests on rather
  than an interface nicety. Two compartments times two runs is four curves,
  which is also the comparison a learner actually makes.

  **Colour keeps meaning "compartment" in both modes, deliberately.** Handing it
  to the run would make one channel mean two different things either side of a
  mode change, on the chart where a misread is a misread of a clinical value.
  If two compartments proves too tight in practice, the fallback is three with
  the run moved to direct labelling at each curve's end — position being the
  strongest channel available and the one that survives every colour-vision
  deficiency — but that is a change to test rather than to assume.
- **What the readouts show while two branches are displayed** (queue item
  PL-1XPX). A decision rather than an implementation: a numeric readout that
  does not say which run it describes is the safety-critical failure this
  project treats presentation as, and there is more than one defensible answer.
- **The chart's hover says which run it is reading** (queue item PL-MN4J).
  `safety`-classed, and milestone-scope debt under § "Debt inside the
  milestone's own scope" rather than debt this gate can clear: a hover naming
  the agent and the instant but not the run is ambiguous only while two runs are
  drawn, which is this milestone's own compare mode, so it cannot be cleared
  before the compare mode it is about. Before that ships there is one run on the
  chart and the hover names everything there is to name. Like `PL-1XPX` it is a
  decision rather than an implementation, and the project owner's: it amends
  `docs/MODEL.md` § "The chart's hover readout: what the tooltip may show",
  which derives the three-line form, so no session can close it either way.
  `PL-8PSW` shipped the legend and panel naming that make a curve attributable
  today; this is the remaining surface, and the definition of done's "no
  readout, label, legend entry or reference band ambiguous as to which run it
  describes" is what holds it.
- **What a comparison asserts and what it does not** (queue item PL-W7H9), in
  `docs/MODEL.md` and `docs/ARCHITECTURE.md`: what is shared between two
  branches and what is not, that a difference between them is attributable only
  to the settings that differ, and that neither branch is a prediction for a
  patient.

### Definition of done

v0.5.0 is complete only when:

- a branch taken at any recorded control event or bookmark reproduces its
  parent element-wise at every sampled point up to the branch point, asserted
  by test;
- a bookmark halts the run on the step that crosses it, at every playback
  multiplier, asserted by test — and a threshold that is never reached ends in
  a distinct, visible outcome rather than in silence;
- two branches read on one time axis with every curve attributable to its run
  and to the settings that produced it, and no readout, label, legend entry or
  reference band ambiguous as to which run it describes;
- the memory a run holds is bounded by its number of control events rather
  than by its length, and no sample store remains in `src/`;
- `docs/MODEL.md` states the canonical evaluation rule, what a comparison
  asserts and does not, and the bound on any divergence that could not be
  eliminated;
- every item of the frozen list above outside this milestone's Required scope
  is `done`, or `dropped` with its reason recorded;
- the v0.0.2 circuit, v0.1.0 sevoflurane and v0.2.0 multi-agent reference tests
  remain unchanged and passing, and no equation, parameter or governing
  constant has changed; and
- Ruff formatting and linting, strict mypy, pytest, `docket check`,
  `tools/doc_check.py` and GitHub Actions all pass.

### Explicitly out of scope for v0.5.0

- Scenario save/load (item 9) and a user-facing deterministic replay control
  (item 10). Only the resimulation driver replay needs is in scope.
- Sub-forks of forks, and any branch structure other than one trunk with N
  branches (project owner, 2026-08-25).
- More than two runs displayed at once. The comparison is specified for a
  trunk and one branch; N branches may exist and be selected between.
- Persisting bookmarks or branches across a restart, which is item 9's.
- A schematic compartment view (item 27) and agent cost (item 28).
- Nitrous oxide, coadministered gases and the concentration and second-gas
  effects (items 6-7), and the multi-substance patient state behind them.
- The anesthesia-machine abstraction, interlocks, agent switching with residual
  washout, direct injection and end-tidal control (items 1-5).
- Patient factors — age, sex, weight, body composition — and any change to the
  MAC basis (item 30).
- Horizontal panning of the chart window (queue item PL-Z7LY), which the
  fit-run scale still makes optional rather than necessary.
- Any change to the governing equations, the parameter set, or the exact
  solution the matrix exponential computes. This milestone changes what the
  model can be *asked*, never what it answers.

## v0.6.0 - the layout is the reader's

Planned-milestone item 34's first half. Scoped 2026-09-16 (project owner,
**ratified** on `PL-NMTF` - the placement, the split and the gate decision were
all recommendations put to them and agreed, so `CLAUDE.md`'s lower bar to
reopen applies to each; what the owner *specified* is item 34's own content,
which this milestone builds rather than re-decides), two releases ahead of its
turn, because the design was already
settled and fourteen prerequisites were waiting on a build item that did not
exist. Item 34 carries the design and the Blender provenance behind every
decision below; `docs/interface-provenance.md` carries what was read, what this
project adopts and what it deliberately does differently. This section is what
gets built.

**The vocabulary is Blender's for two of its three words** (`.claude/rules/ui-areas.md`):
an **Area** is a rectangle that reserves screen space and holds one thing; a
**View** is what occupies it; a **Workspace** is a set of Areas geared to a
task, switched as a tab. Where `PL-C842` wrote `Pane` and `view_kind` while
recommending the container, this section supersedes `Pane` and nothing else of
it: a model that says `Pane` while the roadmap says Area is the drift the
vocabulary rule exists to prevent.

**The third word is deliberately not Blender's** (project owner, 2026-09-17,
ratified - chosen over keeping `Editor`, and over `Component` and `Widget`).
Blender calls an Area's occupant an **Editor**, and most of Blender's editors
edit: the 3D viewport, the dope sheet, the text editor. This project's occupants
are the concentration graph, the compartment table, the MAC readout and the
control panel - one of the four takes input and the rest display modelled
values, so `Editor` asserts a mutability the reader does not have, which is the
class of wrong implication `CLAUDE.md`'s clinical-output standard treats as a
presentation defect. `Widget` was unavailable because `QWidget` is the base
class of every one of them; `Component` was rejected as vaguer rather than
wrong. `View` restores `PL-C842`'s own `view_kind`, is already the word
`app/run_view.py` and `app/simulation_view.py` use, and collides with no Qt
class used here. `PL-GPYV` carries the comparison and the Eclipse precedent -
Perspective/View/Editor, which matches this project on lifecycle and not on
multiplicity. Blender's own editors keep the name wherever
`docs/interface-provenance.md` describes Blender.

### Goal

The dashboard is one arrangement and the learner cannot change it. Every
surface is already an independent widget inside nested splitters whose handles
are disabled - `inert_splitter` at `src/anesthesia_sim/app/qt_widgets.py:784`,
the reservation v0.4.26 built and did not turn live - so the only way to see a
chart larger is to make the whole window larger. Stated as they stand on
2026-09-16, the day this milestone was scoped, three gaps:

- **Nothing can be resized, split, joined or swapped.** The handles are inert
  by deliberate reservation and there is no operation set behind them. Item
  34's four requested properties - resizable areas, modular views, presets for
  tasks, and presets the learner owns rather than a fixed shipped set - are
  none of them available.
- **There is no object above the widget tree.** No layout model, no View
  registry, no Workspace, and no user-writable state of any kind: nothing under
  `src/anesthesia_sim/` writes a file, so a layout cannot be named, saved, or
  returned to next launch. A saved Workspace would be this application's first
  user-written data, and its load path its first new failure surface since the
  shipped parameter files.
- **What the display is required to show sits inside the container that is
  about to become live.** `src/anesthesia_sim/app/simulation_view.py:296-309`
  puts the readout section - simulated time, the rate it is advancing at, the
  six compartment concentrations and the delivered concentration - inside
  `inert_splitter`, and the control-input record's panel sits in the sidebar
  inside the nested horizontal splitter. Only run state, halt reason and agent
  identity are outside it. So on the day the handles work, a learner can close
  the values `docs/MODEL.md` says no Workspace may remove. The violation is
  pre-loaded rather than absent, and `.claude/rules/ui-areas.md` rule 5 reads as
  already satisfied to a session looking at today's code, because nothing is
  closeable yet.

The end state: a learner divides a window into non-overlapping Areas, each
holding one View; switches between named task Workspaces as tabs; rearranges,
duplicates and saves their own and returns to them next launch - while the
values the display is required to show cannot be closed, cannot be collapsed to
make room, and cannot leave the screen with the surface that drew them.

### Debt gate: frozen when v0.5.0 ships, and nothing is recorded here yet

This milestone was scoped out of turn, so beat 1 of the cadence does not freeze
its list - see § "The debt gate" -> "The cadence", which records the exception
and the condition on it. Gate 2 holds v0.5.0's findings, and v0.5.0 has not been
implemented, so freezing here would produce a gate holding none of what it
exists for. **The list is frozen on the day v0.5.0 ships and is recorded under
this heading**, in the ordinary form, before implementation of this milestone
begins. Until then this heading is deliberately empty of entries, which is what
distinguishes "not yet frozen" from "frozen and empty".

Debt inside this milestone's own scope is cleared by it rather than before it,
per § "Debt inside the milestone's own scope": the test is whether Required
scope names the id, and nine of the ids below are `defect`-, `safety`- or
`refactor`-classed work that this milestone exists to do.

### Required scope

1. **The layout model** (queue items `PL-1FT6` and `PL-HJPY`). Pure Python,
   no Qt import: a tree of splits and Areas with `split`, `join`, `resize`,
   `swap` and `set_view`, a `borders()` query returning the handles collinear and
   adjacent to a given one, and versioned JSON serialization. The serialized
   root holds a *set of windows* from version 1, which `PL-HJPY` settles -
   what owns the set, how an Area is addressed across windows, and
   where the border-chain query terminates - because a root that gains a window
   set later is a schema migration against files a learner has already saved
   their own Workspaces into.

   *Where the tree cannot express a join it is refused rather than
   approximated.* `PL-3J2P` chose the nested-splitter tree knowing it is
   strictly less expressive than Blender's shared-vertex graph, on the ground
   that the limit "shows up as a join being unavailable rather than as a wrong
   value". That is a property the model has to have, not one it gets for free.

2. **The adapter** (queue item `PL-W9P6`). One module, the only importer of
   `QSplitter`, building and updating the widget tree from the model; this is
   where v0.4.26's inert handles go live. The Qt side owns no layout state: no
   view calls `saveState()`, reaches for a parent splitter, or stores its own
   geometry.

   *Measured rather than assumed*: `QSplitter.saveState()` returns 35 bytes for
   a three-pane splitter - magic `0xff`, format version 1, the sizes, then
   `childrenCollapsible`, `handleWidth`, `opaqueResize` and orientation. It
   records no widget identity at all: the same three children in reverse order
   save byte-identical state. `restoreState()` returns false only on a bad magic
   number or a newer format version, so a three-pane state restores into a
   two-pane splitter returning `True`, and a two-pane state into a three-pane
   splitter returning `True` with the third pane at zero. Re-measured on
   PySide6 6.11.2 / Qt 6.11.2 on 2026-09-16, which is the evidence behind
   `PL-C842` and is stronger than the form that item recorded.

3. **The View registry and the kind tag** (queue item `PL-R1WQ`). Where the
   registry lives, how a tag is allocated so an ordinary class rename does not
   trip the loud failure meant for a genuinely missing View, and how the
   pure-Python model validates a tag without importing a Qt view.

4. **Loud failure on an unknown View kind, per Area** (queue items `PL-R1WQ`
   and `PL-SSQW`). The flagship divergence from Blender, and it is a *pane*-level
   rule that the file-level version policy in entry 10 cannot reach: a saved
   Workspace naming a View this build does not have fails **visibly, in that
   Area**, substitutes nothing and drops nothing. Blender's own answer is to
   install a 3D viewport silently, which `docs/interface-provenance.md`
   § "Diverged" refuses on this project's preference for an obvious failure over
   a plausible-looking wrong one.

5. **The View contract** (queue item `PL-TH35`), written *with* the area
   system and validated against two Views that already exist, carrying the
   four clauses the 2026-09-16 audit added: what a View's saved state is and
   who writes it, what it owes when handed state it cannot read, what a split,
   a swap and a stack round trip each preserve, and what the container does when
   an Area cannot honour a size. Small by construction and re-checked against its
   implementers, per § "Prune the contract" in the provenance record.

6. **The import boundary with teeth** (queue item `PL-L8RN`). `QSplitter`
   confined to the adapter and concrete View modules confined out of the
   layout tree, which needs `tools/import_boundary_check.py` to decide a dotted
   import target rather than a root package. Both entries land in the commit
   that creates the adapter, because a boundary over a tree that does not exist
   is an `empty` error by construction.

7. **The unconditional region** (queue items `PL-NWTM` and `PL-W54S`). A named
   region outside the layout container, holding every unconditional value, that
   the model has no address for - so the adapter cannot place an Area there and
   no serialized Workspace can name it. `PL-NWTM` also supplies the pure-Python,
   UI-free declaration of what that set *is*, addressable by tier: the invariant
   tier, and the tier instantiated per modelled substance, which is what keeps a
   later intravenous run from being asked for a vaporizer dial it does not have.
   `PL-W54S` is the per-window shape that declaration is built in, settled on
   2026-09-16 and recorded in `docs/MODEL.md`: every top-level window carries the
   invariant tier and the name of the run it shows; the per-substance tier lives
   once, in a main window that cannot be closed while any other window is open.
   v0.6.0 opens one window, and building the region in that shape now is what
   stops v0.7.0 rebuilding it.

8. **An Area that cannot honour a size says so** (queue item `PL-K285`). The
   second of the three properties `docs/interface-provenance.md` records Blender
   not supplying: Blender's answer is `RGN_FLAG_TOO_SMALL` and collapse to zero
   extent, and "a required value is never hidden to make room" is the
   divergence. Whether a declared minimum is a request or a constraint, and what
   a split or a border drag does when it cannot be met, are this entry's.

9. **State a layout could duplicate or relocate** (queue items `PL-VN6M` and
   `PL-9LNF`). The compartment selection owned outside `TraceLegend`; `RunView`'s
   nine `build_*` accessors, which hand out the instance's own widgets so a
   second request silently reparents the first placement away; the chart time
   base, owned by a dropdown built into one plot's panel while governing both;
   and the chart's column budget, read as a maximum over two named siblings that
   stop being siblings once each is a View in its own Area.

10. **Run identity** (queue item `PL-7Z84`). A run carries an identity stable
    across serialization and independent of drawing order, with
    `run_label(run_index)` reduced to a rendering of it, and
    `docs/MODEL.md`'s rule for when a view names its run restated in terms of
    that identity rather than of how many runs are displayed.

11. **The Workspace object** (queue item `PL-WV9K`). What a Workspace carries
    **beyond its layout** - the pinned run by the identity above, each View's
    own saved state, and what a Workspace switch does to a run in progress - and
    how the set behaves: order, rename, duplicate, delete and save-as-mine, with
    Blender's refusal to delete the last Workspace enforced by the type rather
    than by a warning dialog. Shipped defaults are distinguished from the
    learner's own, and "reset" is defined.

    *A View's state survives leaving its Area and coming back.* The provenance
    record adopts Blender's per-Area stack of previously-open Editors for the
    property it buys - the outgoing View's state is kept rather than destroyed
    - and this milestone ships `swap` and `set_view`, which are the operations
    that would destroy it. The minimum form is in scope: one retained entry per
    View kind, which is how Blender bounds the stack by construction rather
    than by a cap.

    *A Workspace excludes preference state, and the tier a setting belongs to is
    decided by instance multiplicity rather than by Workspace membership.* Three
    tiers. **Run state** - the simulated values - is one set of numbers every
    View draws from and no reader setting reaches. **Per-View-instance
    state** is how *this* View draws them: which compartments it shows, its
    axis denomination and range, its time window. The View serializes it into
    the Workspace containing it, by the delegation `docs/interface-provenance.md`
    § "Persistence, and what happens when an editor is missing" already adopts
    from Blender's `SpaceType`, and two instances of one View kind **in one
    Workspace** hold it independently. The project owner's stated case, 2026-09-17:
    one graph showing the vessel-rich group against the MAC-awake band and the
    1 MAC line, a smaller one below it with every compartment on, and a third in
    a squarer Area zoomed to the first fifteen minutes to read the wash-in - all
    three in the same Workspace. **Reader preferences** are the settings for which
    a second simultaneous value is incoherent rather than merely unusual; the
    agent price and its currency is the one this project has today.

    The test, therefore, is *can a reader sensibly have two of these on screen at
    once?* Yes routes to the View; incoherent routes to preferences; and a
    setting that changes the numbers rather than their drawing is neither and
    stays in the versioned data files. So a Workspace excludes preference state
    because it is a container of View instances and a preference has one value
    - not because a unit or a price "is not layout", which is the weaker argument
    and the one that misroutes the axis range. This is also what keeps Blender's
    four Save & Load entries addable later without a migration: its preference
    reset reads `use_data = false, use_userdef = true`, resetting that third tier
    alone, while "reset this Workspace" restores the second from item 13's
    shipped JSON.

    **This holds while a run is ephemeral, which is a condition and not a
    permanent property.** Planned-milestone items 9, 10, 12, 26 and 30 add a
    saved scenario; a scenario is a fourth tier, and where it sits is placed when
    the first of them is scoped rather than assumed here.

12. **Persistence** (queue item `PL-SSQW`). Where the file lives per platform
    and the override a headless run or a test uses; an atomic write, so an
    interrupted save does not leave a truncated JSON the next launch has to
    classify; what a first run with no file does; and the schema-version policy
    answering **older**, **newer** and **invalid-at-the-supported-version** by
    name, each saying whether the file is migrated, refused, or set aside and
    replaced, and what the learner is told. `core/parameters.py`'s
    single-version rule is correct for files that ship with the code and wrong
    for a file the learner wrote, so the rule is decided rather than inherited.

13. **The shipped default Workspaces** (queue item `PL-KXTL`). The central-graph
    default with the other Views arranged around it, an induction Workspace
    with the concentration graph zoomed in, and a big-picture maintenance one -
    as validated versioned JSON beside the other shipped parameter files, with
    the provenance line `docs/interface-provenance.md` asks of anything derived
    from Blender's own named task Workspaces.

14. **The operations a reader performs** (queue item `PL-2KXB`). Border drag
    moving the collinear chain the `borders()` query returns; corner drag to
    split and to join; Area swap; and the Workspace tab strip with the lifecycle
    from entry 11. The chain is the query that recovers the one behaviour the
    tree gives up against Blender's graph, and `PL-3J2P` measured it as
    differing exactly once across thirty-two shipped Blender Workspaces.

15. **Every operation reachable without a drag** (queue item `PL-M352`), through
    a menu and the keyboard. This is not planned-milestone item 20's general
    accessibility pass arriving early; it is the narrower rule that this
    milestone does not *introduce* an interaction a keyboard-only reader cannot
    perform, which is cheap now and a retrofit later.

16. **The View chooser, and the accounting tier's reachability** (queue item
    `PL-50PZ`). `docs/MODEL.md` puts the agent accounting - cumulative delivered,
    cumulative exhausted, total stored, and the mass-balance residual with its
    absolute error - in a tier a Workspace may omit but that "must stay reachable
    in every layout, and must not be removable from the application". That is the
    one required class whose guarantee cannot be structural presence, so it
    becomes an invariant of the registry and the chooser instead.

17. **The visibility predicate** (queue item `PL-904Y`).
    `SimulationView.interface_strings` is this project's single definition of
    what is on screen and answers "is this string in this widget's subtree",
    which is the same question as "can the reader see it" only while the
    dashboard is one tree with nothing closeable. This milestone makes the two
    come apart at Area close and join. One predicate spans every Area and every
    top-level window the application owns, distinguishes present-in-the-tree from
    visible-to-the-reader, and is what entry 18 asserts through.

18. **Tests over the real interface** (queue item `PL-G5SX`), headless, driving
    split, join, swap, resize, Workspace switch, save and reload, and asserting
    after each that every unconditional value is on screen, that the accounting
    tier is reachable, and that a required value did not leave with the surface
    that drew it. Plus the assertion `PL-9LNF` says cannot be written today:
    resize one Area while paused and the redrawn series is sampled for that
    Area's new width.

19. **The documents this milestone falsifies** (queue items `PL-ZBBP`, `PL-JSY5`
    and `PL-RTG9`). `.claude/rules/ui-areas.md` is a standing prohibition on
    exactly what this milestone builds, and its `paths:` frontmatter does not
    reach a layout package living outside `app/`, so it is retired or re-scoped
    rather than left loading. `docs/ARCHITECTURE.md` describes the layout that
    exists. `docs/MODEL.md`'s readout-row rung and its always-on-screen
    disclaimer line both assume one window's width and one permanent surface.
    And `README.md` gains the Blender attribution line, which
    `docs/interface-provenance.md` § "Attribution" has been holding until the
    release in which the shipped interface actually is the area/workspace model.

### Definition of done

- A learner can split, join, resize, swap and close Areas; switch Workspaces by
  tab; rearrange, duplicate, rename and delete them; save their own; and find
  them on the next launch.
- Every one of those operations is performable from the keyboard as well as by
  drag.
- The layout model is exercised with no `QApplication` at all, including a
  fixture file one schema version ahead of the build and a file truncated
  mid-write.
- `tools/import_boundary_check.py` fails the build if any module but the adapter
  imports `QSplitter`, or if the layout tree imports a concrete View module.
- A Workspace naming an unknown View kind fails visibly in that Area and
  substitutes nothing; a Workspace file of an unsupported version is handled per
  the written policy rather than by whatever the load path found natural.
- Every unconditional value is outside the layout container, and a test asserts
  for each that no ancestor of its widget is that container, and that it is
  still on screen after a split, a join, a close, a Workspace switch and a
  reload.
- The accounting tier can be brought on screen through the interface alone from
  every shipped Workspace, and a Workspace naming none of those Views still
  leaves them reachable.
- Two Views that already exist implement the View contract, and a test
  builds two of one run's surfaces and asserts both draw.
- **No learner-visible regression against v0.5.0.** Compare mode ships before
  this milestone and is then rearranged by it; everything a learner could do
  with two runs on 2026-09-16 they can still do, checked against v0.5.0's own
  definition of done.
- `make check` is green, and the documents in Required scope entry 19 describe
  the interface that exists.

### Explicitly out of scope for v0.6.0

- **Break-out into a top-level window** - planned-milestone item 34's second
  half, and row 9 of the timeline, v0.7.0 (queue item `PL-Y04W`). Nothing in
  this release creates a second window. The split costs nothing structural
  because the two things break-out would otherwise force a rewrite of are both
  built here: the serialized root carries a window set from version 1 (entry 1),
  and the unconditional region is built in its per-window shape (entry 7). What
  v0.7.0 adds is the window, its lifetime and the test that drives it.
- **The View catalogue** - planned-milestone item 36, which stays after this
  milestone for the reason item 34 records: a View's contract is whatever the
  area system requires of its contents, so Views built first are built against
  today's fixed layout and rewritten. This milestone validates against two that
  exist and builds no new one. The queue audit that re-runs once item 36 is
  scoped is queue item `PL-L6QR`.
- **Floating Areas or panels - not yet, rather than never.** The option to take
  a tiled Area out into a floating one is wanted later; this milestone does not
  build it. Item 34 records that writing floating panels as permanently refused
  was a session's overreach and not a decision anybody took, so the exclusion is
  stated with its condition: floating arrives under `docs/MODEL.md`'s occlusion
  rule, which binds it without being re-argued for it.
- **The visual pass** - planned-milestone item 33, palette, type scale, spacing
  rhythm, density and the visual composition of each surface. Arrangement is
  this milestone's and appearance is that one's.
- **Blender's snap-merge operator and extend-drag**, which are the two
  behaviours the splitter-tree measurement found it unable to express, and the
  five-area pinwheel arrangement for the same reason.
  `docs/interface-provenance.md` § "Refused" records the count, the
  construction, and the condition under which the representation choice
  reverses.
- **Replace-by-dragging an Area into the middle of another.** The *operation* is
  in scope as `set_view` through the Area's own chooser (entries 1 and 16);
  only the corner-drag affordance for it is deferred, to whichever release takes
  up the rest of Blender's docking set.
- **Schema migration code.** The policy for an older file is in Required scope
  entry 12; there is no second schema version in existence to migrate from, and
  writing the migrator before the schema it migrates to exists is writing it
  twice.
- **Remembering which screen a window was on.** Restoring a position against a
  changed monitor set puts a window where the reader cannot see it, which is the
  occlusion failure arriving through persistence.
- **Anything under `core/`.** This milestone introduces the two things
  § "Development rules for scientific milestones" requires simulation code to
  stay independent of - filesystem state and display dimensions - so the
  boundary matters more here than usual, not less.
  `tools/import_boundary_check.py` enforces it, and Required scope entry 6 only
  adds to it.
- **Re-reading the Blender design rationale against the primary pages** (queue
  item `PL-PV5Q`), which rests on search summaries because `blender.org` is
  egress-blocked from this project's sessions. It is independent of this
  milestone and waits for a session that can reach those pages.

## Development rules for scientific milestones

- Define equations, units, assumptions, and reference cases before changing the
  scientific core.
- Keep simulation code independent of the UI toolkit, wall-clock time,
  filesystem state, and display dimensions.
- Store model parameters as validated data with schema version and provenance;
  do not place executable equations in data files.
- Preserve deterministic results for identical initial state, events, and time
  steps.
- Treat mass accounting and independent reference cases as release gates, not
  optional diagnostics.
- Keep each milestone narrow. New ideas belong below until promoted into a
  scoped release — or in `docs/items/` when they are a task rather
  than a release.
- **A Goal is frozen at scoping and dated there.** It records the problem the
  release was taken on to solve, in the tense and the state of that day, and
  closing items do not amend it. What a milestone achieved is recorded in its
  Required scope and its Definition of done, which is where a reader looking
  for current state should be sent. Rewriting a Goal into the past one clause
  at a time leaves the section describing neither the problem nor the product,
  and it puts an edit to this file on the critical path of every closure.
  `PL-DXQC` is why this is written down rather than left to imitation: two of
  v0.4.0's three Goal bullets were fixed while the section still asserted them
  in the present tense, and one had been stale for two releases before anybody
  noticed there was no convention to breach.
- **An exclusion is written under `Explicitly out of scope`, never inside a
  `Required scope` bullet.** Those two subsections are the only structures
  `bin/docket next` reads for membership, and it reads `Required scope` *in
  full* - a milestone names what it covers in whatever grammar the sentence
  wanted, so `"(queue item PL-DHV7)"` mid-bullet has to count. The cost of
  reading it in full is that an id named inside a scope bullet **in order to
  exclude it** is read as scope. `PL-NBCS` is why this is written down rather
  than left to imitation: v0.4.0's stage-3 exclusion put `PL-B9PY` into
  v0.4.0's `scope_ids`, and while v0.4.0 was the anchor `docket next` told
  every session that Gate-1 work was what v0.4.0 was waiting on - stated as a
  fact, with the milestone named. `tools/doc_check.py` fails an id named under
  both headings of one milestone, and advises where a scope bullet carries
  exclusion language.

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

**The same test decides a hazard, and it is the one carve-out the `safety` and
`science` exception takes.** A finding classed `anticipated` describes a hazard
a later milestone will create rather than one the tree carries now, so it is not
debt until that milestone builds it. § "The gate is a snapshot, not a moving
target" below states the rule, what it was chosen over, and what it costs.

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

**When a milestone is scoped, the debt list is frozen at that moment** - except
for a milestone scoped out of turn, whose gate freezes when the milestone before
it ships, per the exception recorded under § "The cadence". A
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

**One exception to that exception: an `anticipated` `safety` or `science`
finding is not debt until the hazard it describes exists** (project owner,
2026-09-16, ratified — chosen over placing each on the *next* milestone's frozen
list behind a marker nothing enforces, and over leaving the rule as it stands
and putting the 2026-09-16 area-model findings on v0.5.0's list). The paragraph
above is unconditional about *when* a finding was made; this says what it takes
to be a finding against the current gate at all. An item classed `anticipated`
describes a hazard a later milestone will create — the splitter handles are
inert today (`src/anesthesia_sim/app/qt_widgets.py:784`), so no reader can
close, replace or cover a required value until planned-milestone item 34 makes
them live — and a gate that exists to clear debt *before* a milestone begins
cannot clear a hazard that milestone introduces. It is § "What counts"'s own
live-mechanism test — "Process work is debt once the mechanism is live, not
before ... The distinction is state, not layer" — applied to a hazard rather
than to a mechanism.

It was also the only one of the three options that reaches a state a session can
get to. The other two leave `tools/doc_check.py`'s corrected safety-class
advisory lit against items nobody can dispose of, which is the defect
`CLAUDE.md` names: a check that "fires every run without changing a decision".
The disposition such a finding then takes is a **placement in the milestone that
creates the hazard** — v0.6.0's `Required scope` holds the ten this was written
for — never a deferral, which these two classes are still not offered.

**The carve-out expires with the wait it is granted for** (project owner,
2026-09-16, ratified — chosen over leaving it on the class alone, which never
stopped). `anticipated` claims the hazard is not live yet; `status: blocked` is
what the item stops saying once it is, and `blocked-by` is where it names what
has to happen first. So the exemption is held only by an item that has written
down what it is waiting for, and it lapses when that wait ends — where the class
on its own ran on past the milestone that created the hazard, which is the one
event the rule exists to notice (`PL-ZF2G`). It is the same pair
`subprojects/docket/src/docket/checks.py` already requires for the safety-band
exemption, read from there rather than decided again, so that `anticipated`
means one thing across both tools.

It lapses on the promotion rather than on the blocker closing, and nothing
rewrites `status` on its own: `bin/docket check`'s "every blocker has closed; it
is ready to promote" advisory is what asks for it. That leaves a window of one
grooming pass, in place of the indefinite one it replaces.

`check_gate_reentries` in `tools/doc_check.py` reads both fields for this
reason, so the rule runs on every `make check` rather than on whether a session
recalled it.

**What it costs, recorded rather than waved past.** `anticipated` now carries
weight it did not carry before, so a `safety` item wrongly classed becomes
invisible to the gate — `PL-MVC2`'s shape. Two things narrow that and neither
closes it: the class is claimed rather than inferred, and `PL-MVC2` itself made
a class outside the declared vocabulary a `bin/docket check` error, so a
misspelling fails closed and leaves the item named. Nothing catches a class
correctly spelled and wrongly applied. That is a reviewer's judgment, and this
decision is what makes it one worth making.

### The cadence

The gate is a recurring step on the plan, not a precondition assumed in the
background. Every milestone runs the same four beats, and "The plan" above
shows them on one timeline with the milestones they gate:

1. **Scope** the milestone here — goal, required scope, definition of done,
   explicit out-of-scope list. Scoping is the act that freezes the list.
2. **Freeze and record** the debt list in that milestone's own section, as
   item ids, on the day it was frozen.
3. **Clear** it — every item `done`, or `dropped` with its reason — before
   implementation of the milestone begins. **Sweep the frozen list for
   staleness first** (project owner, 2026-09-17, ratified — chosen over a second
   `verify:`-style field recording a fault test beside each fix test, and over
   leaving the sweep to whoever next noticed). A `verify:` command is specified
   as one that fails before the work and passes after, so it tests for the
   presence of the fix and never for the presence of the fault: an entry whose
   defect no longer reproduces fails forever and reads as outstanding work. One
   measured pass found 12 of 134 open items dead and 31 more overtaken — 32% —
   and nothing in the project noticed or can, a churn advisory having been
   built, measured against that pass's verdicts and rejected because `partly`
   churns *less* than `yes` (`PL-LKGL`). Staleness is a judgment, which is why
   this is a beat and not a check: read each frozen entry against the tree, drop
   what no longer reproduces with its reason, and correct the briefs that
   overstate what is left — before spending a session on any of them.
   `PL-6ZQY` is the standing item for the pass.
4. **Implement** the milestone. A finding made while clearing or implementing
   goes to the next gate unless the problem it describes predates the freeze
   (per "The gate is a snapshot" above) or is `P0`/`safety`/`science`, either
   of which re-enters this one.

A milestone whose gate has not been recorded has not been scoped, whatever
else has been written about it — **except where the milestone was scoped out
of turn, which is the one case beat 1 was not written for.**

**The exception, and why it is the rule's purpose rather than a departure from
it** (project owner, 2026-09-16, ratified while scoping v0.6.0). Beat 1 freezes the list
because scoping is normally the last thing that happens before beat 4: the
milestone before has shipped, its findings are in the queue, and the gate that
freezes is the gate that holds them. v0.6.0 was scoped with two releases still
ahead of it, so applying beat 1 on the day would have frozen Gate 2 before
v0.5.0 had been *implemented* — a list holding none of v0.5.0's findings, which
is the one thing "Gate 1 onward hold one milestone's findings" defines a gate to
hold, and v0.5.0's findings would have fallen to Gate 3. So a milestone scoped
out of turn freezes its gate **when the milestone before it ships**, which is
the moment beat 1 was reaching for, and beats 2, 3 and 4 then run unchanged.
Nothing is renegotiable in it: the freeze date is fixed by the timeline rather
than by whoever next opens the section, which is a stronger commitment than the
day of a scoping round, and the milestone's own section names the heading the
frozen list goes under when the moment comes.

**Twice in a row now, which is a fact about the trigger rather than about the
two milestones.** v0.4.26 took no gate by its own exception and v0.6.0 takes
this one, so "scoping freezes the gate" has not described the last two
milestones this project scoped. Whether the trigger should read "the gate
freezes when the preceding milestone ships" is a real question and is
`PL-KKRP`'s, filed 2026-09-16 rather than settled here: a rule that has been
excepted twice wants re-examining deliberately, not amended in passing by the
session that needed the second exception.

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
   later machine feature below builds on. **What "modular" is for: a real
   commercial machine is added as a data file, not as code.** That is the goal
   the three scoping items below serve, and it is a fidelity claim as much as
   an architectural one — name a machine in the interface and a learner
   attributes to it the behavior of the machine in their own operating room,
   so what the module may carry and what the interface may say are the same
   question. `PL-4DCG` surveyed the variation that reaches a number, `PL-FG9D`
   designed the abstraction against it, and `PL-WZVZ` is the surface that keeps
   a machine's effect on a curve attributable to a named parameter.

   **The default fresh gas flow is no longer this item's to place, and the
   sentence that said otherwise was stale.** It was a literal in
   `core/circuit.py` with no provenance until `PL-4YY1` moved it into
   `src/anesthesia_sim/data/machines/reference_circle_system.json`, where it
   has a cited file and a stated `provenance_gap`; `PL-8DJ7`'s deferral of its
   *home* to this abstraction is answered in `docs/machine-abstraction.md`,
   which places it among a run's opening conditions rather than among a
   machine's specifications, because no surveyed machine publishes a startup
   flow and a per-machine field would force every profile to invent one. Its
   *value* is `PL-NM7X`'s and is open.

   **Two queue items scoped this one, they were sequential, and both are
   done.** `PL-4DCG` surveyed the machines in current clinical use for the
   variables that change a simulated result; `PL-FG9D` then designed the base
   abstraction — what a module is, what the base type owns against what each
   machine supplies, and where the parameter/strategy line falls — and it
   depended on the survey, because the extension points are the axes of real
   variation that reach a number and designing them first is guessing. Three
   items wait behind them rather than behind this prose: `PL-8PS6` (fresh gas
   flow range is a machine property) and `PL-WZVZ` (make an inter-machine
   difference attributable) are carved out of Gate 1 for that reason, and
   `PL-439V` (make the Tec 6 the concrete second device class) is answered in
   the design's dial-mapping slot. All three now wait on this milestone being
   implemented rather than on a design that does not exist.

   **The survey is done and is `docs/machine-survey.md`.** It records which
   variables reach a number, which are per-machine data and which are genuinely
   different behavior, and what remains unknown. Two of its findings bear on
   how this milestone is scoped rather than on how it is built: apparatus
   volume alone does not account for the measured differences between machines,
   so a profile that is a volume and a set of bounds is already falsified; and
   the fresh gas inlet's position changes the inspired/delivered ratio at a
   fixed volume, which a single well-mixed circuit compartment cannot
   represent, so this milestone has to decide on the record whether to
   represent internal topology, to state that machines differing only in it are
   indistinguishable here, or to route it into the per-compartment gas-phase
   model at item 39.

   **The design is done and is `docs/machine-abstraction.md`.** Four of its
   results bear on scoping this milestone. **The seam already exists in the
   tree**: a machine's whole reach into the model is two rates and one volume
   in the breathing circuit's row of `core/governing_equations.py`'s system
   matrix, so adding machines cannot touch a patient row, and the reference
   machine's strategies reproduce today's matrix entry for entry — the
   abstraction lands with no change to any computed value. **The set of machine
   behaviors is closed by two properties of the existing solver** rather than
   by taste: a strategy must be constant across a step and must keep the matrix
   Metzler, which is why item 5 (automated end-tidal control) is a milestone
   and not a slot. **The inlet-position question above is answered**: decline to
   represent internal topology and say so where a machine is chosen, with
   folding it into an effective volume refused outright and item 39 named as
   the condition that reverses the decline. **What a machine may be called is
   decided** (project owner, 2026-09-20, ratified, over naming the machine by
   its trade name in the running interface): an archetype label wherever a
   machine is running or chosen, with the trade name confined to the panel
   holding that machine's parameter set, its sources and its `not_modelled`
   list. That is a scope constraint on this milestone and on `PL-WZVZ` rather
   than a preference — the trade name is admissible only where what the model
   does *not* claim about that machine is on screen beside it.

   Scoping this milestone therefore starts from a design rather than from a
   blank page, and the scope statement's own test is the design's stated cost
   target: a machine whose delivery and removal are already in the closed set
   is one data file under `src/anesthesia_sim/data/machines/`, with no change
   to `core/` and no new test of the physics.
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
    and write to, rather than adding a fourth scattered location.

    *What the panel must never make editable, and the test that decides it*
    (`PL-QBX0`, 2026-09-19). This gate named `data/**/*.json` and nothing
    else until then, which is one location rather than a criterion, and
    the agent-identification colours and the contrast-checked palette both
    sit outside it. **What decides is the guarantee a value carries, never the
    file it happens to live in:** a constant whose value is held to a safety,
    standards-conformance or accessibility guarantee by something outside the
    panel is out of the panel's reach wherever it is declared. An enumeration
    cannot carry that rule - this one has already been wrong once - so the
    table below is the instances known on that date and the criterion governs
    whatever is added after it.

    | What | Where it is declared | What holds its value |
    | --- | --- | --- |
    | Scientific parameters - partition coefficients, tissue volumes, MAC | `data/**/*.json` | validated, versioned and cited; `tools/doc_check.py` walks the provenance both ways |
    | The three ISO 5360:2016 agent-identification colours | `app/theme.py` | `tests/unit/test_theme.py` pins each fill to Table 2; `tools/agent_identity_check.py` keeps the pair as measured equal to the pair as rendered |
    | Every colour `tools/contrast_check.py` measures - the six compartment traces at 3:1 against the panel under normal vision and three simulated dichromacies, and every text pair at WCAG 2.2 AA | `app/theme.py`, and any module under `app/` that declares its own | `tools/contrast_check.py`, which reads every module under `app/` with `ast` |
    | The six compartment traces' dash patterns | `app/chart_frame.py` | nothing mechanical - a recorded judgment, which is exactly why it is listed |

    Each stays changeable only through the review that set it - deliberate
    scientific review per `CLAUDE.md`'s safety-critical standard for the first
    row, and the recorded reasoning in `app/theme.py` and `docs/MODEL.md` for
    the rest - never through an ad hoc settings screen.

    The colours are in scope for the same reason the parameters are. ISO 5360
    Table 2 footnote b makes displaying an agent colour an obligation to
    display the *right* one, so a panel that let a reader recolour them would
    let one agent be shown in another's identification colour, which is
    `CLAUDE.md`'s "the correct number with the wrong label" exactly. The last
    row is the one to read twice: colour cannot separate six traces at all -
    the 3:1 floor caps every trace's luminance, so six of them cannot be more
    than 1.48 apart, and `app/theme.py` records the search - so the dash
    patterns are the separating channel, and they are the single entry here
    that no check would defend if a panel flattened them.

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
28. Add agent cost, from the delivered-agent amount the model already tracks.
    The economic argument for low fresh gas flow is a standard teaching point
    and currently the one lesson in this class of simulator that the
    application has the numbers for and does not draw. Depends on nothing;
    kept out of the v0.4.0 scope because it is an addition rather than a
    prerequisite.

    *That sentence read "the exhausted-agent amount" until 2026-09-19, and
    that is the wrong quantity* (`PL-H4N8`).
    `core/agent_simulation_validation.py` holds the accounting identity
    `initial + delivered = exhausted + currently stored`, so with `initial` at
    zero, delivered *is* the total and the exhausted/stored pair says only
    where that agent is at this instant. Cost is what left the bottle, which
    is what the vaporizer added: `delivered_agent_l`. `exhausted_agent_l` is
    what has left the *circuit*, and understates delivered by exactly
    `currently_stored_agent_l`. The two converge only at full washout - this
    model has no metabolism and no chemical degradation, per `docs/MODEL.md`
    § "Assumptions" - which is what makes the wrong basis read plausibly. The
    Gas Man reference simulator bills delivered too (Workbook Appendix,
    printed p. 174: `Cost = DELIVERED Flow x Cost/mL vapor`), and so does
    this project's own `docs/MODEL.md`, whose "Known limitations" entry on
    the 20 °C reference already calls the delivered total "the figure that
    means cost". This sentence was the only document saying otherwise.

    *What the wrong basis would have cost.* Measured 2026-09-19 on
    `AgentUptakeSystem.default()` - reference adult, sevoflurane held at a
    fixed 1 MAC dial, 0.1 s step - as the percentage by which exhausted sits
    below delivered:

    | fresh gas flow | 15 min | 30 min | 60 min |
    | --- | --- | --- | --- |
    | 1.0 L/min | 63.7% low | 53.8% low | 45.7% low |
    | 4.0 L/min (the shipped default) | 28.6% low | 21.4% low | 16.9% low |
    | 8.0 L/min | 16.2% low | 11.8% low | 9.1% low |

    It is worst early, which is the phase the low-flow lesson is about, and
    worst at *low* flow - so it distorts the comparison the lesson *is*,
    rather than shifting both arms of it together. At a fixed dial delivered
    is proportional to flow, so 1 against 8 L/min is exactly 8:1 at all three
    times; on the exhausted basis the same pair reads 18.4:1, 15.3:1 and
    13.4:1, overstating the saving by as much as 2.3x. A teaching display
    that flatters its own lesson is worse than one that understates it.
    `PL-H4N8` carries the method, and the caveat that a fixed dial is not the
    equal-alveolar-concentration comparison a real low-flow protocol makes.

    *A prerequisite of its own, and it is narrower than it first looks.*
    `delivered_agent_l` is vapour litres and a bottle is liquid millilitres,
    so a figure in money or in bottles needs a vapour-to-liquid ratio - and
    that constant is already sourced and its reference condition already
    decided. `docs/MODEL.md` § "Agent amount" carries Biro's 184 mL of vapour
    per mL of liquid sevoflurane, reproduced to 182.8 mL from Laster, Fang
    and Eger's 20 °C density and the exact molar mass, and records the
    project owner's ratification of a 20 °C reference over 37 °C on
    2026-09-17 - naming this item as the consumer (`PL-S6WW`, shipped in
    v0.4.28). One litre of vapour is 5.47 mL of liquid sevoflurane here.

    What is left is that those numbers live in prose. None of
    `data/agents/sevoflurane.json`, `data/agents/isoflurane.json` or
    `data/agents/desflurane.json` carries a density, a molar mass or the
    ratio, so `CLAUDE.md`'s rule that model parameters live in validated,
    versioned data files is unmet for them and `tools/doc_check.py`'s
    provenance walk is structurally blind to a constant that never entered
    one - the same gap `PL-4YY1` closed for the circuit's volume and flow.
    That work is already filed as `PL-KZ99`, which stores each agent's molar
    mass and liquid density *with the density's measurement temperature* so
    the conversion is derived from Laster's primary measurement rather than
    from Biro's composite constant; it was blocked on `PL-S6WW` and is
    unblocked now that `PL-S6WW` has shipped. So this item's first step is
    `PL-KZ99` rather than anything new, and `PL-B396` chooses what the
    resulting figure looks like.

    *The exhausted/stored split keeps its own labels.* It is the uptake curve
    in mass form and is worth drawing; it is simply not the economics, and
    nothing here may relabel either line as waste. `PL-B396` chooses that
    display.

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
    It therefore sits immediately after v0.4.0 as the `v0.4.x` row of "The
    timeline", which keeps the benefit as early as the remaining constraint
    allows.

    **This paragraph read differently until 2026-09-06, and the difference
    matters (`PL-3P2P`).** It said "Nothing between v0.4.0 and v0.7.0 touches
    `core/` either — v0.5.0 and v0.6.0 are interface releases on an unchanged
    model — so the step is free anywhere in that span." That was true when it
    was written on 2026-09-02 and false three days later: the score
    architecture the 2026-09-05 design round placed in v0.5.0 is chained
    behind `PL-GS5X`, and `PL-T691` and `PL-P1Z3` both declare
    `src/anesthesia_sim/core` in their `touches`. So the step was not free
    across the span — it was pinned immediately ahead of v0.5.0, and was the
    head of the MVP's critical path rather than a readability pass that could
    slip. Read as originally written it understated its own priority in the one
    document that decides priority. `PL-GS5X` closed 2026-09-06 in pull request
    376, which is what made that chain startable.

    *Scoped 2026-09-03 (project owner), and the three open questions are
    answered. Re-scoped the same day, and it is no longer a patch.*

    **The bar, stated by the project owner 2026-09-03:** a reviewer who knows
    the standard variables and equations of the textbook should be able to
    follow `core/` and recognize them, without referring to `docs/MODEL.md` and
    without a lookup table. That is a sharper test than the one-line bar in
    `.claude/rules/core-domain.md`, and it is what the answers below are held
    to.

    **Naming alone could not reach it, which is what the re-scope found.** The
    alveolar balance's two terms were computed in two different steps of the
    operator split, separated by a third, and the pulmonary uptake term was
    never formed at all; three of the five composed sub-steps were objects of
    the splitting scheme rather than of the domain. The equations existed in
    the repository in exactly the right form — in the independent RK4 oracle,
    which may not be imported from `core/` without making the verification a
    tautology. So the split was replaced by the exact matrix exponential
    (`PL-GS5X`, landed 2026-09-06), under which assembling the system matrix
    *is* transcribing the governing equations, and the code that computes the
    answer is the code a reviewer recognizes. `PL-SPMQ` carries the measurement and the options that
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
    patch cut before this work lands takes it — unless the roadmap has given
    that number to a milestone section ahead of the current one, which the
    reserved-version guard withholds (project owner, 2026-09-16, ratified, on
    `PL-KQHN`). The number this ships under is whatever the cut assigns. This was briefly recorded as a minor earlier the same
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

    The numerical method changes and the displayed value moves in its last
    digit, but no capability boundary is crossed — same model, same parameters,
    same controls, same agents, and nothing a learner can do that they could
    not before — so it takes a patch version rather than a minor, per
    "Versioning decision". The paragraph above this one said "no behavior,
    equation, parameter, or numerical method changes"; that was written when
    item 29 was a naming pass and the 2026-09-03 re-scope superseded it.

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

    *Cardiac output is one of the quantities that scales, and the scaling is a
    coupled package (`PL-YKSM`, 2026-09-08).* The decision above settles what
    weight acts *through*; this settles what "weight scales the compartments
    directly" has to reach. A time constant here is
    $`V_i \lambda_{i:b} / Q_i`$, so a rule that scales the flows and leaves
    compartment volumes at the fixed litres this project stores makes
    $`\tau \propto M^{-3/4}`$ - a heavier patient equilibrating faster and a
    lighter one more slowly. Worked at 20 kg against the shipped sevoflurane
    coefficients, that gives a child **2.64 times** the adult's time constants,
    in a direction every textbook has running the other way, against **0.76
    times** when volumes scale with the flows and **1.00** when nothing scales
    at all. The half-measure is further from the truth than the status quo. So
    compartment volumes, alveolar gas volume, alveolar ventilation and the
    perfusion fractions move together with cardiac output and the tissue flows,
    or none of them moves. `PL-YKSM` carries the arithmetic and the alternative
    it refused.

    It is recorded here rather than only in `docs/MODEL.md` "Known limitations"
    and `reference_adult.json`'s Cattermole note - which is where a reader of
    the stored *value* meets it - because the session that scopes this
    milestone reads this item. The failure it guards against is that session
    scoping weight as "cardiac output becomes a function of weight", which is
    exactly the change `PL-YKSM` examined and refused, and shipping a
    paediatric patient whose kinetics are wrong in the most-taught direction.
    One paragraph now against a rebuild later.

    *A suggestion for scoping rather than a decision: prefer measured
    weight-banded normal ranges to an allometric formula for the default.* The
    learner sees the default, not the law that generated it, and Cattermole et
    al. 2017 - already cited in `data/patients/reference_adult.json`, 2218
    healthy subjects aged 0.5 to 89, reported by weight band - is a measurement
    of the quantity rather than a scaling exponent applied to one. It is not
    free of the provenance problem it would solve, and scoping has to weigh
    that: its subjects are awake, supine and at rest, measured by transcutaneous
    Doppler rather than thermodilution, and the authors state that normal ranges
    are method-specific - which is why the file cites it and does not adopt it.
    Adopting it as a default would be its own recorded decision under
    "Source hierarchy", on the terms every other value in `data/` is held to.

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
    closed against that decision, and `PL-N092` (rewrite README as a human-
    readable introduction) then ran on its own on 2026-09-06 rather than waiting
    for the pass — the reason it was deferred was that these documents cohere
    when written together, and the reason not to wait was that a stranger could
    already arrive at a repository with no `README.md` at all. So the root
    `README.md` exists again, written to the two audiences `PL-RM83` settled,
    and the check that held its absence retired itself in the same commit.

    **What is left here is the rest of what a first-time visitor meets**, this
    item's original scope less the README. Nothing surfaces it: nothing is
    blocked on it and no check reports it, so it waits for a session offering to
    scope this milestone or for the owner to ask.

33. Run the interface pass: one deliberate visual design pass over the whole
    interface — palette, type scale, spacing rhythm, density and the visual
    composition of each surface — rather than the per-defect corrections the
    queue has been making one at a time.

    Requested by the project owner on 2026-09-08, who framed it as "a decent
    size overhaul (theme, style, overall polish)" and as not urgent, wanted
    after the simulator works rather than before.

    *Arrangement is not on that list, and the word that used to be was
    "layout"* (corrected 2026-09-16, `PL-BNYF`). Which areas exist, where they
    sit, and what a reader may do to them is item 34's entire content; this item
    decides how what sits inside them looks. The two were separable in 2026-09-08
    when this was written against one fixed screen and are not separable any
    more, because under item 34 the arrangement is the *reader's*, and so is not
    a thing a design pass can decide once.

    *This resumes a shelved thread rather than opening a new one.*
    `docs/WORKING_NOTES.md` § "Shelved, then resumed: UI structure/form mockups" records a
    mockup round explored and shelved on the owner's call, closing "Do not
    resume this without the project owner asking again". That condition is now
    met. The note's own reasoning — that a mature UI could not be designed on
    the functionality then available — was written against v0.1.0 and is a
    statement about that baseline rather than about today; the principle beside
    it, that UI/UX ambition follows scientific-core maturity, is what places
    this after MVP. The three artefacts from that round are explicitly not a
    starting point, per the note.

    *Placement (project owner, 2026-09-08, and moved 2026-09-16).* After
    v0.7.0, as the `v0.7.x — the interface pass` row of "The timeline". A patch
    track rather than a numbered milestone, for the reason that row gives.

    *It runs after item 34 rather than before it* (project owner, 2026-09-16,
    ratified on `PL-PHKP` - chosen over leaving it between MVP and Gate 2,
    where 2026-09-08 had placed it). **The reason is that the pass has more to
    style after item 34 than before it, and would otherwise be partly redone.**
    Item 34 and break-out introduce an area header, a workspace tab strip, a
    live splitter handle and a drag affordance - none of which exists today, and
    the header is the *View's* own rather than the container's, which
    `docs/interface-provenance.md` § "What an editor must implement" establishes
    from the source. A pass run first would decide palette, type scale and
    spacing for a set of surfaces, and then meet four more.

    **What the other side bought, recorded because it was real.** Running first
    would have given a styled interface two releases sooner, and `PL-BNYF`
    already separated the two questions - arrangement is item 34's, appearance is
    this row's - so the visual composition of each *existing* surface would
    mostly have survived being rearranged. The cost accepted is that the
    interface keeps its current visual language until after v0.7.0. Nothing in
    either release was blocked on the answer either way, which is why the row was
    left in place while the question was open rather than moved on a guess.

    *Absorbed into the Qt port on 2026-09-10 and returned here on 2026-09-16*
    (project owner, on `PL-L9RD`). The port took this item on the argument that
    it would redecide palette, type scale, spacing and layout anyway; measured
    after it landed, it changed no palette entry, type size, padding or radius
    at all. The reversal leaves one piece behind deliberately: the port reserves
    the layout containers with their splitter handles inert (§ "Completed: v0.4.26 - the
    interface moves to Qt" → "Required scope" item 2), and **item 34** is what
    turns them live - corrected 2026-09-16 (`PL-BNYF`), this entry having said
    "this item" where item 34's own entry and the port's `Required scope` item 2
    both name item 34. What this item inherits from the reservation is its
    *other* half: every dashboard surface is now an independent widget with its
    own spacing and density, which is what makes one pass over them possible at
    all. It inherits none of the splitting, joining or workspace behaviour.
    So the placement above stands unchanged, and the thing to
    read before scoping this is that a port is not a design round - re-expressing
    widgets in a new toolkit does not decide anything about how they should look.

    *The structural half is not part of this item, and lands ahead of v0.5.0.*
    Most of what an overhaul looks like from outside is not polish and is
    already owed: `PL-2CS8` consolidates the display constants item 24 names as
    its own prerequisite and "Development pathway" Phase 2 orders first;
    `PL-NGF7` decides whether an explicit theme object replaces the Material
    defaults that supply colours no tool in this repository can measure; and
    `PL-B9PY` is the decomposition, which is also the component seam that makes
    the six repeated panel recipes one. All three are debt and reach the gate on
    their own class. What is left for this item is the part that is genuinely
    taste.

    *Two hard prerequisites, and they are the reason this cannot simply be
    started.* Nothing in this repository draws the interface. `PL-7J96` records
    two defects that shipped while every tree-level test passed — a required
    label wrapping mid-phrase, four of seven readouts dropping to a second
    baseline at some widths — both found only by screenshotting, and neither
    reachable from the control tree the suite reads. `PL-2QMK` records that no
    session in the web container can render Flet at all, the egress proxy
    refusing the CanvasKit fetch. A visual pass is the one class of change that
    suite structurally cannot see, so both land first.

    *Three constraints on any palette, recorded here so scoping does not
    rediscover them.* `tools/contrast_check.py` parses every module under
    `app/` with `ast` (`PL-BXB2`), holds every declared pair to WCAG 2.2
    AA under four vision models, and fails the build on a renamed or undeclared
    colour constant — so a restyle is also a `REQUIREMENTS` rewrite, in the same
    change, per `.claude/rules/ui-color.md` judgment 1. The three ISO 5360:2016
    Table 2 agent colours are fixed and not available to move (judgment 4); a
    palette lives with them and keeps them legible on whatever surface it puts
    behind them. And trace separation is carried by dash pattern rather than
    colour: `PL-GVXP` measured the pairwise ceiling at about 1.48 once each of
    six traces must also clear 3:1 against the panel, so re-picking the chart
    palette cannot buy what it appears to, and a session attempting it is
    solving a problem that has no solution in that channel.

    *Out of scope, and deliberately.* Dark mode is a separate decision — it
    doubles the declared contrast matrix and the ISO colours were chosen for a
    light context — and belongs to scoping this milestone rather than to this
    line. So does the publication-quality figure export
    `docs/WORKING_NOTES.md` § "Long-term vision" describes: it implies its own
    rendering path, separate from the Flet live chart, and is a capability
    rather than a restyle.

34. Take Blender's window management as the model for the interface: the
    application window divided into resizable, modular areas, each holding one
    view, with task-oriented layout presets the learner can switch between,
    customize and save.

    *Requested by the project owner, 2026-09-12*, naming four properties:
    resizable windows, modular views, presets for tasks, and presets that are
    the user's to customize and save rather than a fixed set shipped with the
    application.

    *Why Blender specifically, and what is worth copying.* Its window system is
    **tiling**, not floating: the window is subdivided into non-overlapping
    resizable areas, each area hosts one view, and areas are split and joined
    from their corners and borders. Areas are grouped into **Workspaces**,
    presented as tabs and each geared to a task, which the user can reorder,
    duplicate and delete; a layout persists by being saved into the startup
    file. The tiling half is the part that earns its place here rather than
    being taste: a tiled layout has no overlapping or hidden panels, and a
    covered value on this application's dashboard is a misread value, which
    `CLAUDE.md`'s standard treats as a safety failure rather than an
    inconvenience. See the Blender Manual, "Interface → Window System →
    Areas" and "→ Workspaces".

    *The vocabulary is Blender's, and it is the concept rather than a
    resemblance* (project owner, 2026-09-16: "the workspace/area concept ...
    is what I want to implement"). Read at the source, the manual's § "Areas"
    and § "Workspaces" pages having been supplied directly - `docs.blender.org`
    is blocked by the session egress proxy. Three terms, two of them adopted
    from Blender rather than invented:

    - an **Area** is a rectangle that reserves screen space. It holds one
      thing and nothing else, and areas never overlap;
    - a **View** is what occupies an area - the thing with the
      functionality. Item 36 is the catalogue of them;
    - a **Workspace** is a set of areas containing views, geared to a task,
      switched between as tabs. Blender puts the tabs in the Topbar, saves
      workspaces in the file, and lets a custom set become the defaults.

    **Docking** is the manual's word for the corner-drag operations, and the
    set is larger than "split and join": dragging from an area corner joins
    two areas, splits one, does both at once, or - dragged into the middle of
    a second area - *replaces* it. Areas also swap, adjacent ones through the
    border's Area Options and any two in a window through Ctrl-LMB from a
    corner. Resizing is a border drag, with modifiers to snap and to move
    aligned borders together.

    **Two precedents worth copying, both from the source.** Blender refuses to
    delete the last workspace - a floor it enforces structurally rather than
    by warning, which is the same shape `PL-WLWY` settled for the minimum
    display. And a workspace carries *settings*, not only a layout: Pin Scene
    makes activating a workspace switch back to the scene it remembers. The
    analogue here is a workspace pinning which **run** it shows, which is
    exactly what a broken-out window naming its run needs.

    *Tiled first, with break-out into a separate window* (project owner,
    2026-09-15). **Scoped across two releases on 2026-09-16**: § "v0.6.0 - the
    layout is the reader's" (ratified 2026-09-16) builds the tiled no-overlap invariant, the View
    contract, the registry, workspaces, persistence and the unconditional
    region, and the v0.7.0 row - "the second screen" - adds break-out. The
    split costs nothing structural because the two things break-out would
    otherwise force a rewrite of are both built in v0.6.0: the serialized
    layout root carries a set of windows from version 1, and the unconditional
    region is built in the per-window shape the next paragraph settles. What
    the two halves together build is the no-overlap invariant above,
    plus break-out: an area may be taken into **its own top-level window**,
    itself a full window with its own areas. The Blender Manual's § "Areas"
    documents that as *View > Duplicate Area into New Window*, or Shift-LMB on
    an area's splitter widget, and describes the result as a fully functional
    window belonging to the same running instance, useful across multiple
    monitors. Every window is then tiled, so nothing inside one covers anything
    else in it.

    *What is refused is silent occlusion, not floating* (project owner,
    2026-09-15, correcting this paragraph's first form). **Floating is
    deliberately not foreclosed**: the option to take a tiled area out into a
    floating one is wanted, later, and what this milestone does is simply not
    build it yet. The first version of this paragraph recorded floating panels
    as "not admitted" - a permanent refusal, which was the writing session's
    overreach rather than a decision anybody took. Tiled first is the
    sequencing; never floating is not the rule.

    The rule the safety argument actually supports is narrower, and it outlives
    whichever mechanism arrives: **nothing may cover a value the display is
    required to show while the application still believes it is showing it.** A
    floating panel over the dashboard is one way to do that, and a broken-out
    window dragged back over the main one is another - which is why the
    constraint belongs to the display rather than to a window type, stated once
    instead of re-argued per mechanism. **It is settled** (`PL-WLWY`, project
    owner, 2026-09-15), in `docs/MODEL.md` § "Minimum displayed outputs" ->
    "What this list requires once the layout is the reader's": that list now
    divides into an **unconditional** set no workspace may remove and nothing
    may cover - stated as a test rather than a list, with an invariant tier and
    a tier instantiated per modelled substance, so the inhaled agent's
    concentrations and MAC are today's instance and not a permanent
    requirement (project owner, 2026-09-16) - an **accounting** set that must
    stay reachable rather than simultaneously visible, and **conditional**
    obligations that bind a surface only when that surface is shown - so removing a chart removes no required
    value, because the numbers never left. The unconditional set sits outside
    the area system, which is the guarantee v0.6.0 has to build - and
    **what a second top-level window owes that set is settled too** (project
    owner, 2026-09-16, ratified, answering `PL-W54S` - chosen over that item's
    own two live readings): every top-level window carries the
    *invariant* tier and the name of the run it shows, while the
    *per-substance* tier lives once in a main window that cannot be closed
    while any other is open. The two tiers are unconditional for different
    reasons and those reasons travel differently, which is why they are
    allocated to windows differently; `docs/MODEL.md` carries the argument, the
    two readings it refused, and the limit on what occlusion any application can
    observe. It is recorded before break-out is built because it decides the
    shape v0.6.0 builds the region in. The
    occlusion rule is what any later floating mechanism arrives under, rather
    than being ruled out ahead of it. That division is recorded as **a stepping
    stone**, deliberately the rigid version while the layout apparatus is
    built, and is expected to be revisited as it matures; the occlusion rule is
    the part that must survive a revision.

    *The licence constraint, and it runs the opposite way for the two kinds of
    source.* `docs/interface-provenance.md` is the record - the study protocol,
    what was read, what this project adopts and what it deliberately does
    differently - and it is where a session building the layout should start.
    The short form: Blender's source files are GPL-2.0-or-later (the work as a
    whole GPL-3.0-or-later) and this project is Apache-2.0, so **reading the
    source is unrestricted** - GPLv2 s.0 puts activities other than copying,
    distribution and modification outside the licence's scope - while copying,
    translating or porting it into this tree is not, and would make the stated
    licence wrong. But the constraint that actually bites is the other one: the
    **Blender Manual and Developer Documentation, including the Human Interface
    Guidelines, are CC-BY-SA 4.0**, and pasting their prose *is* copying where
    reading source is not. **Paraphrase and cite; never paste** (`PL-P5QX`).
    The design rationale this project wants lives in the Developer Docs and the
    HIG rather than in the Manual, which documents behaviour for users. Qt
    supplies the primitives directly in any case: nested `QSplitter` for the
    tiling and a project file for a named preset.

    *The layout is a nested-splitter tree, and Blender's own shipped layouts are
    what settled it* (`PL-3J2P`, decided 2026-09-16 on the research the project
    owner asked for before the decision was fixed). The question was whether the
    layout is stored as Blender's shared-vertex graph - areas naming four corner
    points, neighbours sharing them - or as nested splitters. It was answered by
    measuring rather than arguing, against a threshold written down first.
    **Across all 32 workspaces Blender ships** - 11 defaults and 21 in its five
    application templates - **none uses an arrangement a splitter tree cannot
    express**, and exactly one contains a four-way junction, where the tree must
    split one of two crossing borders into two handles. The two behaviours a
    tree cannot express are both opt-in: extend-drag is the Shift key on the
    border drag, and snap-merge is its own operator on the border's right-click
    menu.

    One supporting argument did **not** survive the research, and the decision
    is recorded without it. A splitter tree is **strictly less expressive** than
    Blender's representation: five full-span splits and one ordinary join reach
    a five-area pinwheel, which no sequence of full-span cuts can produce. So
    the tree is chosen knowing it gives something up - on the grounds that
    Blender's own designers never used it in 32 shipped layouts, that this
    audience picks a workspace rather than authoring one, that the tree's limit
    shows up as a **join being unavailable** rather than as a wrong value, and
    that a planar subdivision is owned by one person forever.
    `docs/interface-provenance.md` carries the count, the method, the
    construction and the condition under which this reverses.

    *The container sits behind a layout model of this project's own*
    (`PL-C842`, recommended 2026-09-16 with the Blender read behind it; the
    owner delegated the architecture call). The negative half was settled by
    measurement and the research did not overturn it: `QSplitter.saveState()`
    returns 35 opaque bytes carrying sizes and a child count, **cannot record
    which view occupies which pane** - which is the whole of what a named
    workspace is - and restoring a three-child state into a two-child splitter
    **returns `True`** with sizes `[318, 318]` rather than failing. That last is
    disqualifying on this file's own standard, which prefers an obvious failure
    to a plausible-looking wrong result.

    What the Blender read added is that three properties this project needs are
    ones Blender does **not** provide, so they have to be built into a model of
    our own rather than inherited: a **loud failure** when a saved layout names a
    view this build lacks (Blender silently substitutes a 3D viewport); a
    guarantee that a **required value is never hidden to make room** (Blender
    collapses a region that will not fit); and **isolation with teeth** (Blender's
    views can reach the screen and ten of twenty-one do). A pure-Python
    `LayoutModel` is the source of truth - a tree of splits and panes, with
    `split`, `join`, `resize`, `swap` and `set_view`, serialized to versioned
    JSON - with one adapter module the only place importing `QSplitter`. A view
    is registered by kind, never sees a splitter, never calls `saveState()`, and
    never stores its own geometry. `PL-LH18`'s path-scoped rule already requires
    views to be interchangeable rather than merely movable; this extends the same
    reasoning to the container.

    *Given a version, and split, on 2026-09-16* (project owner, ratified on
    `PL-NMTF` - the alternatives put with it were inserting item 34 ahead of
    v0.5.0, which renumbers a scoped milestone, and shipping it undivided with
    break-out inside).
    Item 34 goes **after v0.5.0** rather than before it, on three grounds. A
    workspace pinning which run it shows has no content until more than one run
    exists, and v0.5.0 is what introduces the second run - `run_label` names a
    run `None` whenever it is shown alone today. Inserting it earlier would
    renumber a milestone already scoped with a frozen gate, where placing it
    after renumbers only rows § "Planned milestones" already calls provisional.
    And nothing is live-broken: `PL-NWTM` and `PL-9LNF` are both `safety`-classed
    and both *pre-loaded* rather than live, because the failures they name need
    a working handle and the port's are inert. It then splits across two
    releases on the project's own "keep each milestone narrow" rule - undivided
    it was roughly twice the largest milestone this project has run - with the
    cut taken at break-out because that is the one place the split costs nothing
    structural. The schematic (item 27) moves to v0.8.0 and multi-substance
    (items 6 and 7) to v0.9.0 as a consequence.

    *Reopened and re-affirmed, 2026-09-17* (project owner, ratified - chosen
    over moving item 34 ahead of v0.5.0, which is the alternative that was put).
    The placement above was reopened on an argument the `PL-NMTF` round had not
    weighed: that the build order is what decides whether a new display is a
    widget registered against a contract or an edit to whatever layout exists at
    the time, so every interface question settled before the area model is
    settled against a layout that is going away. The argument is sound and has
    an instance in the record - `PL-J4NW` found `docs/ARCHITECTURE.md` routing
    every new display panel to `run_view.py` or `simulation_view.py` "by asking
    whose it is", which is the fixed two-level layout this item refuses, and
    `.claude/rules/ui-areas.md` is a standing proxy for the system existing.
    What it does not reach is the tail actually in front of it, and the count is
    why. **v0.5.0's Required scope is 13 of 20 `done`, and the monolithic half
    is the part that landed**: `PL-8PSW`, the two-branch overlay this file calls
    the largest new visual surface in the project, and `PL-1XPX`, what the
    readouts show while two branches are displayed, are both closed, as are the
    fork (`PL-TFX5`) and the resumption (`PL-J2TD`). What remains is the
    bookmarks chain and three small items - **4 M and 3 S**, against this item's
    own 4 L / 16 M / 3 S. So the re-order would park an MVP a seventh the size
    behind this milestone to protect a surface that has already shipped, and it
    would strand `PL-7Z84`, because the bookmarks and fork work is what gives a
    workspace a run identity to pin to. The order stands. What the argument does
    change is the paragraph below, which until now was implied by § "The
    timeline"'s row order and is written as a rule because row order is not
    something a session reads as one.

    *No new display surface is built before this item* (project owner,
    2026-09-17, ratified - chosen over leaving the ordering implied by row
    position). A surface built before the area system is built against whatever
    layout exists at the time and against no view contract, so it is built
    twice: once into a fixed parent, and again as a View. Every remaining one
    is already behind this item - the schematic (item 27, v0.8.0),
    multi-substance and its readouts (items 6 and 7, v0.9.0), the interface pass
    (item 33, `v0.7.x`) - so the rule costs nothing today and exists so that the
    next row move cannot reopen the question by accident. **It binds a new
    surface, not a new value.** A reading `docs/MODEL.md` -> "Minimum displayed
    outputs" already owes, or a correction to one on screen, is not deferred by
    it: the safety-critical standard is a floor no ordering rule may lower, and
    a misleading displayed value is never held for a layout. **Its condition,
    and it is an instance rather than a permanent refusal**: the rule ends when
    this item's View contract (`PL-TH35`) and view registry (`PL-R1WQ`) ship,
    because at that point a new surface *is* one registry entry and the second
    build is what stops existing. A surface wanted before then is filed against
    item 36's catalogue rather than built.

    *Placed, and the timing question is decided* (project owner, 2026-09-12,
    `PL-8VL1`). The Qt port rewrites every layout in the dashboard onto Qt, and
    the argument that release made for absorbing item 33 — that applying a
    decision to Flet and then again to Qt is the same work twice — applies to
    layout *architecture* at least as strongly as to palette and spacing. **That
    absorption was reversed on 2026-09-16** for palette and spacing, on the
    measurement that the port did not in fact redecide them; **this reservation
    is unaffected and is the reason why.** A layout container really is built
    once by the port, so reserving costs nothing and rebuilding would cost
    twice — which is exactly the test the palette half failed. So the port reserves for this item and builds none of it: each
    dashboard surface becomes an independent widget inside nested `QSplitter`s
    with the handles inert, and this item is what turns them live — § "Completed: v0.4.26
    - the interface moves to Qt" → "Required scope" item 2 carries it.

    *The widget catalogue is separate work, and the layout comes first*
    (project owner, 2026-09-15): "the layout part with the adding, resizing,
    removing windows etc. and then telling the program what should be in that
    window ... is the functionality I want to end up with. Then separately want
    to work on widgets." Item 36 is that catalogue. The ordering is also the
    sound one rather than only the owner's preference - a view's contract is
    whatever the area system requires of its contents, so views built first are
    built against today's fixed layout and rewritten. One refinement: a
    container abstraction exercised by a single view is not exercised, so this
    item validates against **two** views that already exist rather than against
    any new one, which § "Completed: v0.4.26 - the interface moves to Qt" supplies for
    free in making each dashboard surface an independent widget.

    *What a preset differs in, by example* (project owner, 2026-09-15): an
    induction workspace with the concentration graph zoomed in, and a
    big-picture workspace to switch to during maintenance, alongside workspaces
    the learner creates for themselves. The default shape is a central graph of
    the compartments with the other views arranged around it, itself open to
    being rearranged.

35. Add an optional model of anaesthesia's own effect on cardiac output and
    regional perfusion, which the model holds fixed today. An option the user
    turns on, labelled as an illustrative overlay rather than as the model's
    own prediction, not a change to what a run does by default.

    *Framing (project owner, 2026-09-13).* Recorded as a possible future
    feature to consider rather than as a settled exclusion. `PL-8GV5` proposed
    closing the question outright and the owner agreed with the substance for
    now - the model holds perfusion fixed - while directing that the feature
    stay on this list as an option.

    *The evidence constraint, and it is what makes "optional" the right shape
    rather than a hedge.* Measured against the human volunteer literature
    while working `PL-8GV5`: desflurane alone did not change cardiac index at
    0.83-1.66 MAC (Weiskopf et al., Anesth Analg 1991;73:143-56, PMID
    1854029); the same volunteers with 60% nitrous oxide showed a
    dose-dependent fall (Cahalan et al., Anesth Analg 1991;73:157-64, PMID
    1854030); sevoflurane fell at 1.0 and 1.5 MAC and returned to baseline at
    2.0 MAC as systemic vascular resistance fell, with the depression
    diminishing over hours and under spontaneous ventilation (Malan et al.,
    Anesthesiology 1995;83:918-28, PMID 7486177). So the sign depends on the
    carrier gas, the dose-response is not monotonic, and the effect moves with
    time at a fixed dose. A single monotonic, time-invariant relation is
    therefore not supportable, and the hard part of scoping this is not the
    arithmetic but deciding what the option *asserts* and how its uncertainty
    reaches the reader. `docs/MODEL.md` § "Known limitations" carries the
    measurements, the citations and the consequence for the tissue time
    constants.

    *Also unsupported at rest, one layer down.* The regional half needs
    per-tissue flow under anaesthesia, and the reachable measurements are
    largely animal; `docs/MODEL.md` already records that the stored fat flow
    is about twice Heinonen et al.'s human resting PET measurement. A varying
    fraction on top of a resting one that far out is a second storey on the
    same foundation.


36. Build the catalogue of **views** an area can hold, as work separate from
    the layout mechanism and after it. Item 34 decides what an area is, how it
    is docked, split, joined, swapped and broken out, and how a workspace is
    saved; this decides what a learner can put in one. **The occupant of an area
    is a View** (project owner, 2026-09-17, ratified - chosen over `Editor`, and
    over `Component` and `Widget`). This reverses the 2026-09-16 decision that
    took Blender's own "Editor" and retired *views* and *widgets*: Blender's
    editors mostly edit, these mostly display modelled values, and `QWidget` is
    the base class of every one of them. § "v0.6.0 - the layout is the reader's"
    carries the full reasoning and `PL-GPYV` the comparison. The candidates named so far are the
    compartment schematic (item 27), the concentration chart and the F_A/F_I
    plot as views a workspace places rather than fixed sections of one
    screen, the control-input timeline, the numeric readouts, and item 37's
    interaction display. Requested by the project owner, 2026-09-15, as its own
    track (`PL-4D1M`). Each view added here owes what any displayed clinical
    value owes under `CLAUDE.md`'s clinical-output standard, and a catalogue is
    where that is settled once per view instead of being rediscovered per
    layout.

37. Add an opioid/hypnotic interaction display - iso-effect contours over a
    pair of effect-site concentrations, for a named endpoint such as tolerance
    of laryngoscopy - after items 13 and 15. It is not those two items plus a
    plot: a response-surface interaction model is its own model class whose
    measured quantity is the synergy itself, so it is not derivable from two
    single-drug models and owes its own versioned parameter file, provenance
    record and source-hierarchy decision exactly as each agent file does.
    `CLAUDE.md`'s safety-critical standard already names interaction surfaces
    among its own examples, which is what sets the bar for the display: the
    endpoint named on screen, because tolerance of laryngoscopy, of intubation
    and of skin incision are different surfaces; the plotted point marked as a
    predicted pair rather than as a measurement; and the contours' population
    uncertainty visible rather than implied away by clean curves. Requested by
    the project owner, 2026-09-15 (`PL-JFXG`).

38. Decide what this project is called and what it looks like - the name it
    ships under, an application icon, a splash screen if it has one, and the
    wordmark the README and the interface carry. Raised by the project owner,
    2026-09-16, explicitly as something to start thinking about down the road:
    this is intent, and scoping it is a later decision (`PL-KFJQ`).

    *Its own item because three others consume it.* Item 23 (packaging,
    signing and distribution) needs platform bundle icons, item 32 (make the
    repository presentable to a first-time visitor) needs whatever sits at the
    top of the README, and item 33 (the interface pass) sets the palette and
    type of the interface itself, which is adjacent to an identity and is not
    one. Left undecided, each invents its own answer at the moment it first
    needs one, which is how a project acquires three.

    *The name comes first, and it is the project owner's alone.*
    `open-anesthesia-sim` is a repository name; whether it is also the product
    name is open, and the icon, wordmark, window title and bundle identifier
    are all derived from that answer rather than independent of it.

    *A splash screen, if this application has one, is a safety surface rather
    than decoration.* It would be the one screen shown before any modelled
    number is, which makes it the least skippable place to carry the
    educational-simulation-not-for-clinical-use statement - and at the same
    time the place where polish does most to make a simulator read as a
    shipped clinical product, which `CLAUDE.md`'s clinical-output standard
    already governs. So scoping this decides what a splash screen says, not
    only what it looks like. Having none is a legitimate outcome: an
    application that launches quickly has no reason to hold a user at a logo,
    and that moves the same statement onto the first real screen rather than
    removing the obligation.

    *There is no placeholder to build on.* `PL-J7MM` removed the empty
    branding asset directory on 2026-09-15, the day before this was raised,
    because it had held one placeholder file since the bootstrap commit and
    nothing referenced it. This line is where the intent lives until someone
    scopes it.

39. Carry explicit gas-phase conditions per compartment, so that temperature
    and water content are represented rather than assumed away. Raised
    2026-09-19 from `PL-MPWP` (project owner, 2026-09-19, ratified, over
    filing it as a queue item to be worked): this is intent, and scoping it
    is a later decision.

    *Its own item because two recorded limitations already end here.*
    `docs/MODEL.md`'s "Known limitations" carries two notes that stop at the
    same unbuilt change. "One reference condition, where the model physically
    has two" sizes the temperature half: the alveolar, venous and tissue
    stores hold 5.8 % fewer moles than their 20 °C label implies. "The
    modeled alveoli are dry, and real ones are saturated at 47 mmHg" sizes
    the water half at 47/760. Each says lifting it is outside the current
    milestone, and neither had anywhere to point for what would lift it - so
    a reader asking whether it will be fixed got no answer, and the next
    session to meet either note re-derived the conclusion.

    *It is one change rather than two, and half of it is worse than neither.*
    Both notes describe a model carrying gas at one declared condition where
    it physically has several, so the lift is a per-compartment condition -
    temperature, pressure and water content together. Correcting the water
    half alone is what that note explicitly warns against: applying 713/760
    to the inspired term while the partition coefficients keep an unrecorded
    gas-phase basis moves all four validated wash-in ratios outside their
    published spread.

    *Nothing displayed today depends on it, which is why this is intent
    rather than debt.* Every concentration the interface shows is a
    dimensionless fraction and every partition coefficient a ratio, so the
    trajectories, the mass-balance identity and the MAC multiples are
    invariant to the condition the unit names. It reaches a reader only where
    an amount leaves the unit - the liquid-equivalent consumption figure item
    28 plans.

None of items 1-39 mix scientific-core and UI/tooling concerns within a
single milestone; where one depends on another (e.g. 2-5 on 1, 7 on 6, 10
on 9, 13 on 12), that dependency is noted inline rather than bundled into
one item.
