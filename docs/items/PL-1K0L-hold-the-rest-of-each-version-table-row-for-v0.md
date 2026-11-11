---
id: PL-1K0L
title: Hold the rest of each version-table row for v0.2.3 to v0.3.9, the releases cut before each release had an item of its own
status: done
feature: roadmap-structure
milestone: v0.6.17
touches: ROADMAP.md
added: 2026-11-07
closed: 2026-11-07
pr: 2061
verify: grep -qF '| `PL-1K0L` |' ROADMAP.md
---

**Problem.** `ROADMAP.md`'s version table gave each release a long row: what
the release changed, then how each claim was checked and what was decided on
the way. The project owner chose on 2026-11-07 to keep one sentence per row and
move the rest of each row to the release's cut item (`PL-LVN8`). The releases
v0.2.3 to v0.3.9 were cut before each release had an item of its own, so the
rest of their rows has no cut item to go to. This item holds it, and the
version table's Details column names this item for each of those releases.

**Done when.** Each of those rows keeps its first sentence in `ROADMAP.md`, and
the rest of the row is quoted below, word for word, under its version.

**Generator check.** A home for moved text, made once by `PL-DWGC` (slice 3 of
the roadmap restructure). No mechanism produced it, so nothing is recorded as a
generator.

**v0.2.3, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> Six further items rebuilt the development queue, swept the documentation, and recorded release provenance.

**v0.2.5, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> No source file changed.

**v0.2.6, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> The one scientific item widened the splitting-error bound to the whole settings envelope. No equation, parameter, or numerical method changed.

**v0.2.7, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> No equation or parameter changed, and the numerical method is unchanged - it is now guarded at the domain it was always specified for.

**v0.2.8, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> Seventy items in all. No simulator change: `src/` differs from v0.2.7 by three comments, and `docs/MODEL.md` only by the math syntax GitHub renders and by recording why the operator split is kept over an exact matrix exponential. No equation, parameter, numerical method, unit or displayed value changed.

**v0.2.9, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> Modelled wash-in is compared against published human measurements for the first time — verification became validation, with the two caveats that bound how strongly it may be stated recorded beside it — the interface gained a recorded WCAG 2.2 AA conformance target whose contrast ratios `make check` computes rather than a comment asserts, and three live defects in the queue's own ranking are closed. No equation, parameter, numerical method, unit or displayed value changed.

**v0.2.10, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> Five tooling items closed live defects in the queue's ranking, its verify timeout, and the cost `make check` pays to run it. No equation, parameter, or numerical method changed, and no displayed number changed.

**v0.2.11, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> `BreathingCircuit.set_circuit_volume()` conserves the agent in the circuit, closing a setter that destroyed 24 mL of it and made the *next* step fail for it. Two documentation items and one tooling item closed alongside. No equation, parameter, or numerical method changed; the only displayed values that differ are the ones a halted run shows, which is what the release is for.

**v0.2.12, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> The in-flight answer that keeps two sessions off one item reached only `docket show`; it now reaches `docket triage`, reads the harness's session list for a session that has pushed nothing, and answers in a shallow checkout instead of declining. `src/` changes in three files and only twice over: two uncalled descriptive time constants are deleted, and the boundary between a load-time payload and the public type it produces is documented at the classes themselves.

**v0.3.0, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> This cut carries the last two gate entries: the render loop stopped rebuilding what it could move (6.3x cheaper frame), and `BreathingCircuit` stopped defaulting to one agent's vaporizer maximum. No new capability, and no equation, parameter or numerical method changed; see the versioning exception above [`ROADMAP.md` § "Versioning decision"] for why it is a minor.

**v0.3.1, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> `AgentUptakeSystem.advance()`'s rollback moved off its `except` clauses onto the unwind path, closing a measured hole where a `BaseException` left a partly applied step in the live system, and `reset()` now anchors the mass-balance accounting period to what the compartments hold rather than to a zero it did not itself establish. The rest is the queue's own record of what closed an item: the retired `commit:` hash a squash discards is replaced by the pull request number, recovered from file history and refused at the pull-request title; duplicate front-matter keys, undeclared `classes:` and `feature:` values, and a merge that deletes a captured item became errors rather than silent corruption; a `verify:` command is owed as an error when a grandfathered item closes; and a scheduled job reports whether the tree still builds on a toolchain nobody pinned.

**v0.3.2, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> Every shipped Python file is byte-identical to v0.3.1 and every stored numeric value is unchanged; what moved is what the citations claim about them. `docs/MODEL.md` gained a three-tier source hierarchy — primary measurement, secondary synthesis, reference implementation — and only the first may be named as the authority for a stored value, which makes the shipped parameter set Gas Man's and says so, where the agent files had let a journal's name stand in for a measurement nobody made. The isoflurane blood:gas question is recorded rather than answered: 1.3 is stored, 1.46 is what Lerman et al. measured in adults, and the 11% gap is the widest in the project. Alongside it, the numerical method's future is settled — the operator split is to be replaced by an exact matrix exponential so the code that computes a value is the governing equations, with the state vector decided as fractions — and two live defects close: the conservation guard's three sensitivity constants are pinned, and the pull-request title check moved to a workflow that can observe the rename it asks for. No capability, equation, parameter or numerical method changed.

**v0.3.3, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> The queue's own provenance stopped needing a person: a closed item's pull request number is written by `bin/docket record`, riding whatever commit the session was already making, after the job meant to write it at merge time proved unlandable - a push made with `GITHUB_TOKEN` starts no workflow, so `main`'s required status checks can never report on the commit it pushes, and every configuration that would accept the push weakens that gate instead. That closes the `delegation` feature at 12 of 12. Alongside it, `app/simulation_view.py`'s displayed-precision formatters and chart-series assembly moved into two Flet-free modules, so `docs/MODEL.md`'s displayed-precision derivation now terminates in a function that can be read, cited and tested without loading the interface - stages 1 and 2 of v0.4.0's Required scope, landed ahead of the milestone. `core/` gained a 100% statement-and-branch coverage gate over the saturation it already had, before v0.4.1's exact-step solver arrives to be measured against it, and the pull-request title check now runs at the declared Python floor.

**v0.3.4, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> The whole release is the project correcting statements it was making about itself. `docs/MODEL.md` had named v0.2.3 as the current released baseline for thirteen releases, and still recorded the operator split as kept on a decision the 2026-09-03 re-scope reversed; both are corrected, and the specification now names no current version at all, because a second copy of one goes stale silently at every release. Two checks that reported a false state were repaired and retired: the top-band advisory no longer counts blocked items a session cannot start, and `doc_check`'s baseline-tag advisory is gone, because a local checkout cannot tell a release never tagged from one tagged since it last fetched.

**v0.3.5, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> The release is the project's own quality gate learning what it costs, saying so truthfully, and getting roughly twice as fast. `pytest-xdist` at `-n auto` took the suite from 78 s to 27 s with coverage byte-identical at 100%, `make check` from 115.0 s to 59.2 s and the CI step 28%, and `make test` — the whole-suite target a session reaches for while iterating — followed at 88.5 s to 31.8 s; no test was skipped, disabled or relaxed to pay for it. Two advisories that quoted figures measured once and left to go stale now print what the run actually cost. The two questions those measurements raised — the docket suite's share of the wall clock, and `bin/docket check` becoming the gate's largest item — were decided as accept-with-evidence rather than left open, each carrying the numbers that would have to change to reopen it. And two silent-divergence holes closed: the local and merge coverage gates are held to one command by a check rather than by two comments asking to be kept the same, and the guard that keeps two sessions off one item now reads what files it touches, not only who is on it.

**v0.3.6, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> Display and provenance work rather than model work: no equation, parameter, numerical method or solver step moved, `core/` computes neither reference, and what the agent files gained is three measured constants with primary citations checked against source, stored as fractions of MAC so they survive a change to `mac_percent`. `docs/MODEL.md` records what a MAC multiple on a non-alveolar compartment does and does not assert, that the band is read against the vessel-rich trace and not the alveolar one, and that the interface displays no time-to-wake-up figure of any kind. Alongside them, `core-boundaries` closes: one module may import Pydantic and a check enforces it. The queue itself learned to answer per lane, so two simultaneous sessions no longer rank onto the same item.

**v0.3.7, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> The record is faithful rather than tidy: a slider reports continuously while dragged, so one turn of a dial is several settings the run really was computed under, and the display groups them on a boundary the interface declares rather than on a time threshold the coming playback multiplier would invalidate. Changes superseded within one simulation step collapse into the one the step integrated, because the rest describe a run that did not happen, and the recorded value is read back off the compartment rather than taken from the caller. Alongside it the render stall closed: what saturated the Flutter client was 2 700 discrete control mutations a frame, not data volume, and anchoring the chart's decimation to the run rather than to the moving window leaves a steady frame moving the newest bucket and the final sample. Two features close - `delegation` at 13 of 13 with the stop hook's comparison point corrected, and `provenance` with three review-article PDFs filed as cited references - and three defects in how the queue answers. Display and interface work: no equation, parameter, numerical method or solver step moved, and `core/` neither records the timeline nor knows it exists.

**v0.3.8, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> F_A/F_I is plotted on its own bounded axis beneath the compartment chart, broken into segments wherever the ratio leaves its domain rather than joined by a line across the gap, labelled as a ratio against modelled inspired rather than against the vaporizer dial, and carrying the constant-F_I caveat in `docs/MODEL.md`: it is the textbook wash-in curve only while the dial is held, and a learner who misses that reads a dial change as uptake. Underneath it, what one frame reads stopped growing with the run. The snapshot carried a copy of every sample ever recorded - 4.08 ms at half a million samples, five times a second - and the chart discarded all but the visible few hundred; the controller now answers for a window cut at the axis the caller is about to draw, so a frame reads at most the visible window's own width divided by `SIMULATION_STEP_S` samples whether the run is a minute or a week old, and the decimation scan reads each sample once where it read about 2.8 times. Display and interface work: no equation, parameter, numerical method or solver step moved, and the ratio is a quotient of two modelled states `core/` already held. Alongside them, the literature route this environment actually has - direct HTTP to publishers is refused, the PubMed server answers - is recorded where a session about to write provenance will read it rather than only where a delegated worker would, and two sessions that discover they are on one item gained a rule for which of them yields.

**v0.3.9, moved from `ROADMAP.md`'s version table on 2026-11-07 (`PL-DWGC`).**

> Decimation had rescanned every sample in the visible window on every frame — 62.6 ms at a four-hour window and 207.7 ms at twelve, against a 200 ms frame budget — and now reads precomputed M4 aggregates held on a dyadic grid anchored to absolute sample index, merged tier to tier without revisiting a raw sample, so a frame costs what it draws rather than what the window holds. Beside it, a checkbox per compartment: the reference implementation's own affordance, the two-trace comparison a question like *why does fat lag muscle* actually needs, and the one lever on render cost that trades no fidelity, since a trace nobody is looking at is not a resolution loss. Underneath both, simulated time became the number of steps taken times the run's step rather than a sum accumulated a step at a time, and `docs/MODEL.md` states as a guarantee what had been an implementation detail: a run is a function of its inputs and its step count and of nothing else, so a machine that wakes the loop late runs slower and never differently — with the four things that guarantee does not cover named beside it. Interface and determinism work: no equation, parameter, numerical method or solver step moved, `src/anesthesia_sim/data/` is byte-identical to v0.3.8, and no displayed number changes — the recorded sample times differ in their last bits, about 35 ns after four hours, which no readout, axis or trace resolves. Three apparatus defects close alongside: a commit pushed after its own pull request merged is reported rather than silently dropped, the check that reports it stopped calling merged work lost, and `docket next` reserves what it recommends, so two sessions handed the same answer do not both start it.

**Outcome (2026-11-07).** Every row from v0.2.3 to v0.3.9 now keeps its first
sentence in `ROADMAP.md`, and the rest of each row is quoted above under its
version. Rows that had nothing after their first sentence have no entry here.
The version table's Details column names this item for each release in that
range.
