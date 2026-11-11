# Project roadmap

This file is the authoritative version and milestone map for the project. If a
build guide, issue, or conversation conflicts with this file, update the
conflicting artifact or amend this file deliberately in the same change.

This file covers releases only. Discrete tasks are tracked and prioritized in
`docs/items/`, not here. Those tasks are defects, fixes, cleanups,
optimizations and small features. A piece of work is a milestone rather than a
queue item when it needs its own goal, required scope, definition of done and
explicit out-of-scope list.

## Terms this file uses

- **Apparatus.** The tools and instructions that the project's development
  runs on: the queue of items in `docs/items/`, the command that reads and
  writes it, the checks, and the instructions that agent sessions follow. The
  simulator is the code in `src/` and `tests/`, with `docs/MODEL.md` and
  `README.md`.
- **Lane.** The side of the project that an item's files are on. Product-lane
  items change the simulator, and workflow-lane items change the apparatus.
  Items in different lanes share no files, so two sessions can work them at
  the same time.
- **Generator.** One cause that keeps producing defects, recorded once it has
  produced three or more items.
- **Generator head.** The item that records a generator's cause. The items
  the cause produced point back to it. A head is live while the cause still
  produces items, and spent once it no longer does.

## Current baseline: v0.6.17

In v0.6.17 the agent cost View shows the delivered agent in whole millilitres
of liquid, and `docs/MODEL.md` is restructured so that each fact has one home
and then line edited section by section. The contributor documents are
restructured and copy edited too: `docs/ARCHITECTURE.md`,
`docs/interface-provenance.md`, the two machine documents, `docs/maintainer.md`
and `docs/references/`. The release has 96 items. It is a patch on both halves
of the patch test in § "Versioning decision": it crosses no capability
boundary, and v0.7.0 is given to a milestone section, so no patch release may
take that number. v0.6.17 finishes five features: `landing-deletions`,
`maintainer-guide-structure`, `prose-quality`, `references-structure` and
`release-roadmap-seam`.

v0.7.0 is cut only after its Required scope has closed, Gate 3's frozen list
has cleared and the project owner has test-driven `main`. Two ids in the
Required scope are open. The project owner added both as entry 13 on
2026-11-10: `PL-HQPF`, which makes the accounting panel and the schematic name
the 20 °C and 1 atm at which an agent amount is stated, and `PL-RJN9`, which
makes the agent cost View read that temperature from the model instead of
writing it as text. When v0.6.17 was cut, 119 of the gate's 168 entries had
cleared, 36 were open for this gate to clear, and 11 were deferred to the next
gate.

**One displayed precision changed. No model code, equation, parameter or
stored value changed, and no run can differ:**

| Tree | v0.6.16 tag | This cut | What moved |
| --- | --- | --- | --- |
| `src/` | `a66313e` | `a110105` | the delivered-liquid precision in `app/formatting.py`; docstrings and comments elsewhere |
| `src/anesthesia_sim/core/` | `8186a8c` | `a72bd99` | docstrings and comments only |
| `src/anesthesia_sim/data/` | `c3fbdbc` | `c3fbdbc` | nothing |
| `tests/reference/` | `545a009` | `545a009` | nothing |
| `docs/MODEL.md` | `6bb0708` | `93505d9` | the restructure and the line edit |
| `README.md` | `6644ce2` | `a8f2abf` | a window image, and the elimination result |
| `.github/` | `fefd203` | `fefd203` | nothing |

`tools/ast_identity.py` finds only docstrings and comments changed in `core/`,
and the numbers and units in them are unchanged. The `core/` docstrings and
comments about arterial blood now say that the model has no shunt and one
alveolar compartment, and that the lung's exchange with blood is
perfusion-limited, so arterial blood leaves the lung at the alveolar partial
pressure. They had called that simplification flow-limited (`PL-Z6FR`,
`#2076`). Because `core/` and `data/` compute as they
did, the trajectories were not re-measured.

**The delivered agent in whole millilitres** (`PL-SP6H`, `#2024`). The agent
cost View shows the delivered agent in liquid to the whole millilitre, where it
showed a tenth. The figure's only uncertainty is the measured liquid density.
At the largest supported total, one step of 0.1 mL is about a thirtieth of one
SD of that uncertainty, so the tenth implied more precision than the density
supports. The same change corrected `docs/MODEL.md`'s litre-precision figures.

**The model specification** (`PL-BSMF`, `PL-BZ21`, `PL-FDW6`, `#2054`;
`PL-95SW`, `#2049`). `docs/MODEL.md` now gives each fact one home, and no
chapter relies on a later one. The line edit that followed was audited section
by section, and each statement it dropped was restored.

**The README** (`PL-MBP6`, `#2078`; `PL-L9FC`, `PL-GQWP`, `#2075`).
`README.md` shows the default case's window, and a test fails when the
readouts in that image go stale. Its validation paragraph now reports both
halves of the Yasuda comparison, the elimination check that fails as well as
the wash-in check that passes. Tests hold its playback rates, chart time bases
and agent list to the code.

§ "What a tag ships that its notes may not name" says how work ships that
merges on `main` after a release is cut and before its pull request lands.

## Versioning decision

The project uses milestone-based semantic versioning during early development.
The next release number is chosen for the capability boundary that the release
crosses, not by incrementing the patch number mechanically.

**One deliberate exception, v0.3.0 (project owner, 2026-08-26).** Under that
rule, clearing Gate 0 would be a patch, because it crosses no capability
boundary. Gate 0's frozen list is recorded under v0.4.0, and v0.3.0 released 21
of its entries: seven safety and science fixes, four refactors, eight workflow
and tooling fixes, a performance fix and the choice of a licence. After them,
the simulator does nothing it could not do before. v0.3.0 is still a minor
version, because clearing the inherited pre-MVP backlog is the boundary this
project most needs to be able to point at, and a patch number would bury it.

**The v0.3.0 exception is not a precedent.** It applies to Gate 0 alone,
because Gate 0 is the backlog that accumulated before the debt gate existed.
Gate 1 and every later gate contain the findings of a single milestone. None of
them takes a version of its own. The gated milestone's own number marks the
boundary that its scope crosses (§ "How gate work is released", under
§ "The debt gate"). Unless a further deliberate exception is recorded here,
the capability-boundary rule above applies.

**A patch cut may take only a free number.** A number that this file has given
to a milestone section ahead of the current one is not free (project owner,
2026-09-16, ratified, on `PL-KQHN`).

**The two halves of the patch test.** The first half is the capability-boundary
rule: the release crosses no capability boundary. The second half is the rule on
free numbers: the next minor number is already given to a milestone section. A
release record says whether a patch meets the test on both halves or on one. A
patch that meets only the second half crossed a boundary, and took a patch
number because the next minor number was not free.

### Version table

| Version | Status | What the release holds | Items | Details |
| --- | --- | --- | --- | --- |
| v0.0.1 | Completed | Initial runnable prototype: deterministic simulation clock, controller/view separation, basic charting and controls, and project quality tooling. | | |
| v0.0.2 | Completed | Analytically validated ideal breathing-circuit wash-in and washout with no patient uptake. | | |
| v0.1.0 | Completed | First patient sevoflurane uptake and distribution model - the "Sevo works" milestone. | | |
| v0.2.0 | Completed | Isoflurane and desflurane added as additional loadable volatile agents. | | |
| v0.2.1 | Completed | Validation hotfix: the vaporizer maximum is enforced in the core and rejects rather than clamps, the agent MAC cross-check fails closed, and the cited reference-adult defaults reach the running app. | | |
| v0.2.2 | Completed | Hardening and interface-provenance release on the same model: a failed step halts the run visibly instead of leaving it reading "Running", the parameter schemas reject unknown keys, agent selection carries its ISO 5360 identification color, and a dead non-conservative ventilation path is deleted. | | |
| v0.2.3 | Completed | Hardening and verification release on the same model: displayed concentrations are rounded to the resolution the solver actually supports, the chart payload is bounded and the render cadence decoupled from the simulation's, and the coupled dynamics are gated on an independent RK4 solution rather than on mass balance alone. | 9 items | `PL-1K0L` |
| v0.2.4 | Completed | Verification and delegation release on the same model: fourteen previously untested capacity and validation guards in the scientific core and the controller now have tests, `_halt_run`'s deliberate suppression is covered by a test rather than only a comment, and work whose success a command can prove can be handed to a cheaper model and verified in one step. | 12 items | |
| v0.2.5 | Completed | Licensing, documentation and planning release: the project is licensed Apache-2.0, v0.3.0 through the MVP is scoped onto one timeline with its debt gates, Phase 0 is retired in favour of the standing debt gate, and `docs/worker.md` states what a delegated worker decides for itself. | 7 items | `PL-1K0L` |
| v0.2.6 | Completed | Delegation and release-tooling release on the same model: work whose success a command can prove now has to name that command and have run it, `docket` computes the debt gate and the cadence beat instead of a session transcribing them, and the release path stopped leaving `uv.lock` stale, while drift between this table and the version file became something a check catches - caught, not prevented, since nothing writes the row. | 10 items | `PL-1K0L` |
| v0.2.7 | Completed | Session-discipline and applicability-domain release on the same model: the simulation step now refuses inputs outside the operator split's stated applicability domain and the splitting-error bound is measured across setting changes rather than one held operating point, while ten process items closed the three channels by which product work leaked into discussions that were not about it, gave multi-step instructions a written standard, and cleared three live tooling defects. | 14 items | `PL-1K0L` |
| v0.2.8 | Completed | The workflow works: thirty-eight frozen entries of development machinery the project already runs on - the merge path, the release script, the queue's ranking, the in-flight answer six commands read, the type-check and lint gates, and the instructions a session reads before it does anything. | 70 items | `PL-1K0L` |
| v0.2.9 | Completed | Validation, accessibility and tooling patch on the same model, changing no source file at all: `src/` is identical to v0.2.8. | 7 items | `PL-1K0L` |
| v0.2.10 | Completed | Interface-safety and accessibility patch on the same model: the supported input ranges became the model's own and are refused in `core/` rather than only bounded by the sliders, the alveolar readout stopped calling a modelled value "end-tidal", every readout now names its compartment above a smaller clinical gloss and shares one baseline with its neighbours, two colours that failed WCAG AA on clinical text were replaced, and the application acquired a name. | 11 items | `PL-1K0L` |
| v0.2.11 | Completed | Transactional-step and core-boundary patch on the same model: a simulation step that cannot be completed is now rolled back in full, so a halted run shows the last completed step rather than four of five sub-exchanges applied in order, and the entry point to the scientific core is named `AgentUptakeSystem` for what it owns rather than for anatomy that is one of its four compartments. | 5 items | `PL-1K0L` |
| v0.2.12 | Completed | Provenance and parallelism patch on the same model, changing no equation, parameter or numerical method and leaving `src/anesthesia_sim/data/` byte-identical to v0.2.11: `docs/MODEL.md`'s prose values are now held to the data files they restate rather than only its provenance table, so a data-file edit can no longer leave a stated figure quietly wrong, and a figure derived from several values is reported as needing recomputing when an input moves. | 6 items | `PL-1K0L` |
| v0.3.0 | Completed | The foundation: Gate 0's inherited backlog cleared, 21 of 21 frozen entries closed across the v0.2.5 to v0.3.0 patch series — the splitting-error bound widened across setting changes, the simulation step made transactional and bounded to the split's applicability domain, the `core/` boundary refactors, and the live tooling defects. | 7 items | `PL-1K0L` |
| v0.3.1 | Completed | Provenance-integrity and rollback patch on the same model, adding no capability and changing no equation, parameter or numerical method: `src/anesthesia_sim/data/` is byte-identical to v0.3.0, `docs/MODEL.md` is unchanged, and `src/` changes in one file. | 15 items | `PL-1K0L` |
| v0.3.2 | Completed | Provenance-honesty patch, and the release that decided how this project's numbers may be cited. | 8 items | `PL-1K0L` |
| v0.3.3 | Completed | Delegation and interface-boundary patch on the same model, adding no capability and changing no equation, parameter, numerical method, unit or displayed value: `src/anesthesia_sim/data/` is byte-identical to v0.3.2 and the one `src/` change is behavior-preserving. | 5 items | `PL-1K0L` |
| v0.3.4 | Completed | Documentation- and tooling-truth patch: every shipped Python file is byte-identical to v0.3.3 and `src/anesthesia_sim/data/` is unchanged, so no equation, parameter, numerical method, unit or displayed value moved. | 5 items | `PL-1K0L` |
| v0.3.5 | Completed | Gate-measurement patch changing no shipped code at all: `src/` and `src/anesthesia_sim/data/` are byte-identical to v0.3.4 and `docs/MODEL.md` is unchanged, so no equation, parameter, numerical method, unit or displayed value moved. | 8 items | `PL-1K0L` |
| v0.3.6 | Completed | The first two teachable-case items, and the first release since v0.2.3 to change what a learner sees: every compartment is displayed in MAC multiples alongside percent, on a chart that gained a percent axis left and a MAC axis right, and two horizontal clinical references - a band at the running agent's population MAC-awake, one standard deviation either side of the published mean, and a line at its nominal 1 MAC - so the gap between them shows the decrement required for arousal rather than only the endpoint. | 7 items | `PL-1K0L` |
| v0.3.7 | Completed | The run records its own inputs, and the interface stopped degrading under one: every setting change the model was stepped under is now recorded with the simulated time it took effect, marked on the chart as a third kind of series - vertical, labelled as a record of a user input rather than of anything measured - and listed beside it as the acts that produced it. | 8 items | `PL-1K0L` |
| v0.3.8 | Completed | The wash-in curve the literature teaches from, and the render path that can carry it. | 6 items | `PL-1K0L` |
| v0.3.9 | Completed | What a frame costs, what a learner is allowed to look at, and what a run *is*. | 6 items | `PL-1K0L` |
| v0.4.0 | Completed | The teachable case: the release that makes the model's lessons observable at all. | 36 items | `PL-647D` |
| v0.4.1 | Completed | The apparatus patch, changing no shipped code at all: `src/`, `tests/` and `docs/MODEL.md` are byte-identical to v0.4.0, so no equation, parameter, numerical method, unit or displayed value moved and the reference cases pass against exactly the code that validated them. | 11 items | `PL-J7Y7` |
| v0.4.2 | Completed | The apparatus patch that closes `docket-store`, changing no shipped code: `src/` and `docs/MODEL.md` are byte-identical to v0.4.1 and the only file under `tests/` that moved is the new check's own suite, so no equation, parameter, numerical method, unit or displayed value moved. | 9 items | `PL-7HDY` |
| v0.4.3 | Completed | The release where the gate learned what it costs, and the repository went public — and the second overtook the first. | 12 items | `PL-Y0W6` |
| v0.4.4 | Completed | **The code is the model.** | 13 items | `PL-XVCG` |
| v0.4.5 | Completed | **Going public, finished.** | 18 items | `PL-VR27` |
| v0.4.6 | Completed | **Provenance read at the source, and three checks that were asserting more than they knew.** | 13 items | `PL-5VR1` |
| v0.4.7 | Completed | **Three claims the model made without defending, and the first stored parameter to leave the Gas Man set.** | 10 items | `PL-H1GH` |
| v0.4.8 | Completed | **The gate that was measuring itself, and the run that became its own score.** | 17 items | `PL-BKDP` |
| v0.4.9 | Completed | **The release where the checks were found to be checking less than they claimed.** | 14 items | `PL-L3JB` |
| v0.4.10 | Completed | **The release where the apparatus stopped being implicit.** | 12 items | `PL-VLZT` |
| v0.4.11 | Completed | **The release where the interface's cost was measured rather than guessed.** | 21 items | `PL-R3Y3` |
| v0.4.12 | Completed | **The release where a run stopped being a record of itself.** | 6 items | `PL-R3Y3` |
| v0.4.13 | Completed | **The release where the reference patient's provenance chain was followed to its end, and found to contain no measurement.** | 11 items | `PL-10D6` |
| v0.4.14 | Completed | **The release where the project's own checks stopped refusing correct work.** | 17 items | `PL-3Z9X` |
| v0.4.15 | Completed | **The release where the project's own checks stopped reaching past what they could decide.** | 33 items | `PL-T6F9` |
| v0.4.16 | Completed | **The release where one quantity stopped being stated two ways.** | 13 items | `PL-9FMV` |
| v0.4.17 | Completed | **The release where `core/` said what it meant.** | 11 items | `PL-SXBQ` |
| v0.4.18 | Completed | **The release where the project checked what it tells the next session.** | 17 items | `PL-WHG6` |
| v0.4.19 | Completed | **The release where three questions were answered and `core/` did not change a line.** | 10 items | `PL-6BP6` |
| v0.4.20 | Completed | **The release where four stored values' sources were read back against the publications, and not one number moved.** | 5 items | `PL-D89D` |
| v0.4.21 | Completed | **The release where the stored coefficients were checked against the measurement they descend from, and the specification learned to argue backwards from harm.** | 21 items | `PL-4KKR` |
| v0.4.22 | Completed | **The release where what this project says about itself was checked against what is true.** | 15 items | `PL-MHYG` |
| v0.4.23 | Completed | **The release where standing decisions were re-taken by counting, and the counts moved them.** | 14 items | `PL-2YSL` |
| v0.4.24 | Completed | **The release where `core/` settled what its dimensionless numbers are called, and nothing it computes moved.** | 10 items | `PL-1V3X` |
| v0.4.25 | Completed | **The release where the run became forkable underneath the interface, and the last Flet build was tagged.** | 12 items | `PL-G7RD` |
| v0.4.26 | Completed | **The release where the interface was rewritten and the model was not.** | 94 items | `PL-06YW` |
| v0.4.27 | Completed | **The release where the audit every close-out runs stopped refusing the work it prescribes.** | 6 items | `PL-TM9J` |
| v0.4.28 | Completed | **The release where the queue stopped mistaking a live claim for a spent one, and a `verify:` command stopped being twelve separate promises.** | 58 items | `PL-T2LH` |
| v0.4.29 | Completed | **The release where the queue's own writers stopped moving the files that other items point at.** | 20 items | `PL-GL5P` |
| v0.4.30 | Completed | **The release where the machinery that finds root causes learned to look at the queue itself.** | 8 items | `PL-SW0D` |
| v0.4.31 | Completed | **The release where a recommendation started saying what it buys, and where the model split got a name at each end.** | 14 items | `PL-R5VS` |
| v0.4.32 | Completed | **The release where the chart's hover stopped answering for the wrong run.** | 6 items | `PL-V3GD` |
| v0.4.33 | Completed | **The release where a learner can write down the moment they care about, and the last thing the debt gate was waiting on was designed.** | 9 items | `PL-HP95` |
| v0.4.34 | Completed | **The release where the interface stopped answering in the host's colours, and the model's flow envelope stopped standing in for a machine's.** | 15 items | `PL-Y3XK` |
| v0.4.35 | Completed | **The release where a bookmark started stopping the run on the step that crosses it, and where what a comparison against Gas Man is worth got written down by phase.** | 16 items | `PL-F1SZ` |
| v0.5.0 | Completed | **MVP: the release where a learner can take a branch.** | 78 items | `PL-4B1G` |
| v0.5.1 | Completed | **The release in which the apparatus caught up with the milestone it had just shipped, and nothing a learner can reach moved.** | 13 items | `PL-V065` |
| v0.5.2 | Completed | **The release where "nothing computational moved" stopped being readable off a tree hash and had to be proved instead.** | 15 items | `PL-JYTJ` |
| v0.5.3 | Completed | **The release where the project's own gates stopped reporting a result they had not established.** | 11 items | `PL-CY4F` |
| v0.5.4 | Completed | **The release where the window stopped drawing the host's colours, and the two sentences a learner meets at a refusal started naming what refused and the control that ends it.** | 16 items | `PL-4KSZ` |
| v0.5.5 | Completed | **The release where one hover box stopped holding two moments, and four checks stopped passing on what they could not see.** | 15 items | `PL-3XWZ` |
| v0.5.6 | Completed | **The release where the in-flight guards stopped guessing who holds an item, and verify's assertion check started reading statements rather than lines.** | 12 items | `PL-38HD` |
| v0.5.7 | Completed | **The release where a git call that failed stopped reading as an empty answer, and a brief's prose started being read against its own status.** | 17 items | `PL-KNWP` |
| v0.5.8 | Completed | **The release where a `verify:` command outside the admitted shapes started being refused when it is written, and a closed generator head or a misspelt front-matter key stopped passing silently.** | 7 items | `PL-8543` |
| v0.5.9 | Completed | **The release where a gate's dispositions moved onto the item, `main` started refusing a branch that is not up to date, and an item filed more than 14 days ago started being re-confirmed before it is worked.** | 27 items | `PL-R498` |
| v0.5.10 | Completed | **The release where who holds an item started being recorded as a claim rather than inferred from commit subjects, and every generator head started naming the fact its members misread.** | 8 items | `PL-NLXK` |
| v0.5.11 | Completed | **The release where the in-flight guards started answering who holds an item from the recorded claim rather than from commit subjects, and the release train became something a claim holds.** | 16 items | `PL-DRRG` |
| v0.5.12 | Completed | **The release where the nine generator heads the Projects trial's "Fix generators" project set out to retire stopped generating, and the three Bash guards started reading a command the way bash runs it.** | 131 items | `PL-5ZLQ` |
| v0.5.13 | Completed | **The release where no generator head is left generating, and what the remote holds started being read from one listing of it rather than from the clone's own copies.** | 18 items | `PL-9MK6` |
| v0.5.14 | Completed | **The release where `docs/MODEL.md` started naming intertissue diffusion as a route this model leaves out, and saying which way leaving it out biases the fat and lean-tissue traces, and where break-out came off the timeline.** | 17 items | `PL-47SP` |
| v0.5.15 | Completed | **The release where `docs/MODEL.md` measured the first 24 hours of washout against the published human mean curves, and the window started opening maximized.** | 26 items | `PL-ZZTF` |
| v0.5.16 | Completed | **The release where a refused branch started naming each value it differs on, and a run's record started holding each flow as it was set.** | 5 items | `PL-2KC7` |
| v0.5.17 | Completed | **The release where each family of data files started reading its own schema version, a machine profile stopped having to invent a startup fresh gas flow, and the 24-hour washout tests stopped recomputing the same curves in every test worker.** | 20 items | `PL-HHCD` |
| v0.5.18 | Completed | **The release where each stored value's source started being named on the source entry itself, and `bin/docket release` started refusing a version the roadmap has given to an unfinished milestone.** | 10 items | `PL-G803` |
| v0.5.19 | Completed | **The release where a session stopped being able to merge a pull request itself, and a declared `touches` path started being checked against the tree.** | 13 items | `PL-84MH` |
| v0.5.20 | Completed | **The release where a release started being tagged by a workflow when its cut merges, so the release item and its one pull request became the whole release.** | 5 items | `PL-WSJJ` |
| v0.5.21 | Completed | **The release where the tools stopped respelling the facts `docket` already exports, and a run's record started holding the vaporizer setting as it was dialled.** | 51 items | `PL-R4ZC` |
| v0.5.22 | Completed | **The release where the matrix exponential under every step started keeping the equations' constant 1 exactly 1, and a run handed a point past the 24-hour supported length started being refused where it is built.** | 3 items | `PL-KXW1` |
| v0.5.23 | Completed | **The release where every flow, concentration, step and instant a run takes became a type only its own check can build, and the chart hover started answering the point under the pointer.** | 214 items | `PL-0F33` |
| v0.5.24 | Completed | **The release where a learner can branch wherever a paused run stands and at a mark the run has already passed, and where nothing in the repository may read a shared fact a second time beside the module that owns it.** | 79 items | `PL-9F3H` |
| v0.5.25 | Completed | **The release where a run that stops itself is drawn stopped at once, where every widget of a halted run states the run the controller holds, where a cardiac output that the blood flows do not match is refused when it is written, and where the saved Workspace set exists as code.** | 39 items | `PL-TT19` |
| v0.5.26 | Completed | **The release where the simulator's tests started catching wrong values they had let pass, and where `docs/MODEL.md` started saying which stored parameters the published-data comparison can detect an error in.** | 44 items | `PL-L7RV` |
| v0.5.27 | Completed | **The release where `docs/MODEL.md` started recording why no stored desflurane coefficient can fix its fast early wash-in, and where each agent file started citing the largest primary blood:gas measurement beside its stored value.** | 5 items | `PL-HFQ9` |
| v0.5.28 | Completed | **The release where no tissue group or venous pool stores a blood flow of its own any more, so each flow is formed from the cardiac output in one place, and where a machine profile that opens the run off its fresh gas slider's steps is refused.** | 70 items | `PL-SVZD` |
| v0.5.29 | Completed | **The release where the parts of v0.6.0 that have landed reach a learner: the required readouts sit in a band above the splitters, the splitter handles can be dragged, and two runs share one readout row.** | 61 items | `PL-YBQM` |
| v0.5.30 | Completed | **The release where two compared runs each take one line above one shared heading, so the concentration chart gets back 63 px on the laptop reference, and where a failed drift run reaches the next session.** | 3 items | `PL-1BL8` |
| v0.5.31 | Completed | **The release where every Area's header offers every View kind the build registers, so the accounting View can be brought on screen from any Workspace, and where a chart made wider by a resize or a dragged border is redrawn at its new width.** | 11 items | `PL-VL8G` |
| v0.5.32 | Completed | **The release where each Area builds its own View from the View registry under one View contract, so any registered View can be chosen for any Area and two Areas that name one kind each draw it, and where a pull request held for the owner's read carries its question in a commit trailer.** | 2 items | `PL-CKZL` |
| v0.5.33 | Completed | **The release where an Area that cannot be given the size its View needs says so instead of clipping the View, and where seven `docket` and `doc_check` answers that were wrong without saying so are refused, read correctly or named as unread.** | 11 items | `PL-WQJS` |
| v0.5.34 | Completed | **The release where `make check` looks for wrapped list items in every open item brief and stops reading indented code and HTML comments as prose, where the `verify --self` audit judges an appended `recurrences:` entry by the store's own grammar, and where the rule that forbade building the area system now describes it as built.** | 4 items | `PL-6JG7` |
| v0.5.35 | Completed | **The release where `doc_check`'s docstring checks name the source line a citation stands on, and where the close-out step that rewrites a branch's new simulator prose is kept on a measured rate.** | 2 items | `PL-GHDF` |
| v0.5.36 | Completed | **The release where docket's docstrings and the hooks say what three containers showed about a session's clone, and where three quotations of Claude Code's documentation read as the pages now do.** | 2 items | `PL-7NJ2` |
| v0.5.37 | Completed | **The release where `CLAUDE.md` says a path-scoped rule loads when a session reads, writes or edits a matching file, as Claude Code's memory page now says.** | 1 item | `PL-6KXN` |
| v0.5.38 | Completed | **The release where a weekly `drift.yml` job checks each sentence quoted from Claude Code's documentation against its page, so a quotation the page no longer carries is reported within a week.** | 1 item | `PL-TNTK` |
| v0.5.39 | Completed | **The release where `bin/docket arm` holds a simulator branch that adds long prose until a commit records its fresh review.** | 1 item | `PL-VRQ9` |
| v0.5.40 | Completed | **The release where every `bin/docket` command that reads the queue answers from the same copy of each item, the default branch's newer one, so `delegable` and `triage` no longer offer an item `main` has already closed or triaged.** | 1 item | `PL-06S3` |
| v0.5.41 | Completed | **The release where the dashboard opens on the shipped Workspaces with a tab strip to switch between them, and where each run keeps a number that is never given out twice, so a Workspace can pin the run it shows and says so when that run is gone, and where every layout operation can be done from a menu and the keyboard.** | 6 items | `PL-5VTL` |
| v0.5.42 | Completed | **The release where each chart keeps its own time window, so the shipped Induction Workspace opens its concentration chart on the first 15 minutes of the case while the other charts keep theirs.** | 1 item | `PL-9354` |
| v0.6.0 | Completed | **The release where the layout is the reader's: the dashboard is divided into Areas that a reader splits, joins, swaps, resizes and closes, each Area holds any View the build registers, the arrangements are kept as Workspaces that a reader saves and restores, and the values needed to read any number on screen stay in view outside the Areas, with the use disclaimer.** | 64 items | `PL-9CS6` |
| v0.6.1 | Completed | **The release where four of `CLAUDE.md`'s procedures moved into the skills that apply them and two rules a check already enforces were retired, so `CLAUDE.md`, which every session loads at launch, is about 10,300 characters shorter, and where pull requests run quality.yml's test parts on the arm64 runner.** | 9 items | `PL-XMCT` |
| v0.6.2 | Completed | **The release where the reply hook stops refusing a message that asks the owner for nothing and checks the coordinator's posts too, which finishes the review hold, and where a second copy of a shared fact is classed a defect at triage and two check baselines of such copies are drained.** | 16 items | `PL-Z4T7` |
| v0.6.3 | Completed | **The release where `tools/fact_home_check.py` refuses a predicate written inline and a fact copied under a new name, where a new check holds 21 configuration facts to their homes, and where `bin/docket arm` holds a simulator pull request until its blind generalist review passes are recorded.** | 20 items | `PL-TC7Y` |
| v0.6.4 | Completed | **The release where `core/` reads each input check from the one rule that owns it and requires four defaults that restated a data file, where each agent's MAC is built once as a checked type, and where each displayed unit and each run-state surface in the interface has one writer.** | 32 items | `PL-21GJ` |
| v0.6.5 | Completed | **The release where the headless worker runner refuses a host whose `bash` or `make` is older than `make check` needs, and where the docket skill tells builder subagents in one container to keep their own scratch files, run long commands in the foreground and leave the full suite to the parent.** | 4 items | `PL-Z7DZ` |
| v0.6.6 | Completed | **The release where a test that copies a supported-range limit is found by a monthly check that moves each limit and reruns the suite, where `docs/MODEL.md`'s figures for the supported run length are held to the constant they come from, where the choice of model and effort for each kind of work is read from one table in `docket.toml`, and where Gate 3's frozen list was swept for staleness.** | 7 items | `PL-2FHP` |
| v0.6.7 | Completed | **The release where a headless worker's branch that a review sent back no longer hides its item, where a worker's `make check` stays green on the item it has correctly finished, where each CI test part writes the test modules' assert-rewrite cache once instead of in every worker, where the session-start digest's `Top:` line under product focus names product work, where every docstring and comment under `src/` is rewritten in plain English, and where `tools/fact_home_check.py` refuses one repository path bound under two names.** | 11 items | `PL-LSN3` |
| v0.6.8 | Completed | **The release where `docs/MODEL.md`, `ROADMAP.md` and every docstring and comment in the simulator tests are rewritten in plain English with no equation, unit, number or test changed, where `tools/fact_home_check.py` refuses a plain string copied under a second name, where the untied-restatement check reads slash-joined lists, lower-case units and figures in math spans, and where `bin/docket verify` runs a core module's mutants against a changed core unit test.** | 15 items | `PL-43Z5` |
| v0.6.9 | Completed | **The release where every input to `core/` has a closed range that is refused when it is built, from each compartment volume and partition coefficient to the opening state, where every way of branching at a paused instant opens under the same settings and records the same provenance, where each agent stores its molar mass and its measured liquid density, and where the accounting check's delivered total now equals dial × flow × time to the last bit.** | 95 items | `PL-8D7L` |
| v0.6.10 | Completed | **The release where each value on the run screen is written from the same step as the label, divisor and verdict beside it, where a dial moved on a stopped run is refused, where the accounting panel of a run that an accounting failure halted shows the rejected step's own verdict and totals, where a run that a mark stopped says so in its status word, and where a test holds `docs/MODEL.md`'s MAC-awake washout figures to the model.** | 12 items | `PL-8BDX` |
| v0.6.11 | Completed | **The release where the coupled model refuses an input fraction above 0.99 of the ambient pressure and the chart refuses to draw a fraction above 1, where the mass-balance check keeps its fixed 1e-9 tolerance with the reason recorded, where holding a slider's thumb previews the trajectory that the held value would give, where every run holds while a Reset, new-case or Workspace question is open, and where `docs/MODEL.md` states the coupled system's modal time constants.** | 14 items | `PL-KDDS` |
| v0.6.12 | Completed | **The release where a press on an Area border in a window too small for the Areas no longer rewrites the saved arrangement, where a drag pushed into an Area held at its View's need turns the border WARNING as a keyboard step already did, where a too-small Area's notice is wrapped at the width the Area is drawn at, where the test behind `docs/MODEL.md`'s directional ventilation requirement checks that F_A/F_I is higher at the higher ventilation at every second of the first minute, and where the model review keeps counting a failed pull request title as a red CI run, because a measurement found that none of its 102 failures was by design.** | 6 items | `PL-2JYB` |
| v0.6.13 | Completed | **The release where the compartment schematic ships, drawing the circuit, the alveoli, venous blood and the three tissue groups as containers filled to their modelled tension, each labelled with its tension and its amount in millilitres of vapour, with one bar of each compartment's share of the agent the run holds, placed beside the concentration chart in the Maintenance Workspace; where the agent cost View shows the delivered agent in millilitres of liquid equivalent; where a reader's agent price and cost unit get a preferences file of their own; where a MAC target that a step lands on exactly reads the same on a branch as on the trunk; where an Area's floor is measured only at the width the Area is drawn at; and where the charts hand pyqtgraph numpy arrays.** | 22 items | `PL-PZGY` |
| v0.6.14 | Completed | **The release where the halted-dashboard guard reads a scroll bar's Qt container as part of the bar, so the drift run's upgraded dependencies, PySide6 6.12.0 among them, no longer fail it on a scroll bar that the layout shows on only one of the two dashboards it compares, and where four documents stop claiming more than their sources or the code support: the stored tissue:gas coefficients are Gas Man's figures for Yasuda, Targ and Eger's measurements rather than roundings of them, `docs/MODEL.md` names the held runs' own rounding bound, `control_timeline.py` says where the delivered dial's units change, and a textbook is tier 2 everywhere.** | 5 items | `PL-T343` |
| v0.6.15 | Completed | **The release where the agent cost View shows what the delivered agent cost in money, at a bottle price the reader sets for each agent, with the price's currency and date beside the cost; where most sections of `docs/MODEL.md` are rewritten in plain English for a clinician reader, with the history behind each value moved to the items; where every guard hook runs through one module that records a crash instead of passing silently, and judges the action a command performs rather than how it is spelled; where the owner-ask guard flags a pull request waiting on the owner by its state rather than by its wording; and where the step-size test's 0.5% limit, which never decided a result, is removed.** | 98 items | `PL-8B6Z` |
| v0.6.16 | Completed | **The release where the copy editor cuts a repeated fact, words a fact does not need and a fact meant for another reader, and is back in use; where the rest of `docs/MODEL.md`'s interface sections, and its section on how the document is held to the tree, are rewritten for a clinician reader; where `README.md` is copy edited with the fixed copy editor; and where the writing rule says a model limitation earns a sentence only where it could change what a clinician concludes from a displayed value.** | 11 items | `PL-80PZ` |
| v0.6.17 | Completed / current baseline | **The release where the agent cost View shows the delivered agent in whole millilitres of liquid, because a tenth implied more precision than the measured density supports, and where `docs/MODEL.md` gives each fact one home and is line edited with every dropped statement restored.** | 96 items | `PL-FNJ3` |

There is no active v0.0.3 milestone. Any guide that labels the first patient
sevoflurane build as v0.0.3 is superseded by this roadmap.

### Release tags and release notes

#### Every completed version has a tag on its own release's commit

**Tags.** Every version that the table above marks Completed carries an
annotated tag. As a result, `git describe --contains`
resolves for every commit up to and including the latest release. This was
verified on 2026-08-30 across the whole of `main`. The commits it does not
resolve are the unreleased ones after the newest tag, and the next release's
tag will cover them.

**The gap of untagged versions is closed, 2026-08-30.** v0.1.0 (`ddc868f6`) and v0.2.0 (`69a5888c`)
were the last two untagged versions.

A tag also has to sit on its own release's commit, and the tag's name cannot
show whether it does. So
`tools/doc_check.py` also reads the `pyproject.toml` at each release tag. The
check fails when that file declares a version other than the tag's. **One
version shipped with a stale version file**: v0.2.0. Its tag is on the release
commit `69a5888c`, whose `pyproject.toml` still read 0.1.0. The version bump
followed as `8687bdf2`, "Fix stale app version", which went out in v0.2.1.
Moving the tag onto the bump would make that commit appear to have shipped in
v0.2.0. So the tag stays where the release shipped, and the exception is named
here instead.

#### Where the tag is made

The tag goes on the release's cut. The cut is the commit that added the
release's notes file, which is the cut's own squash commit on `main`. The tag
does not go on whatever `main` holds when the tag is made (PL-QHCW).

#### What a tag ships that its notes may not name

The notes are rendered at the *cut*, and the tag goes on the *merge*. So anything that merges while the release
branch is open is inside the tag's span. No release notes name that work until
the next release claims it. This is not rare, and it is not visible afterwards.
A squash merge also gives the release commit one date, so `main`'s own history
cannot say how long the branch was open. A count on 2026-09-14 across 47 tagged
spans found 12 closing pull requests that merged inside a tag's span and that
the span's own notes never named. They fell in 11 distinct spans, which is
close to one release in four. A recount on 2026-09-22 across 65 spans found
**20 closing pull requests in 16 spans**. The two most recent completed spans
were among them, so the rate has held rather than decayed (`PL-P669`).

So the two records deliberately answer different questions (`PL-028F`, decided
2026-09-14). **The tag span is
what shipped**. `git describe --contains` is authoritative for what shipped,
and it is the provenance guarantee that § "Every completed version has a
tag on its own release's commit" describes. **The notes are what the
cut stamped**, which is the release's own account of the work it was for. Where
the two records differ, the work is described in another release's notes.
Usually that is the next release. It is not always the next release, though.
`#412` was attributed back to v0.4.6, the release its code shipped in, and
`#225` was recorded twelve releases later by v0.4.15. So the pointer described
below names the release rather than assuming one.

**Each notes file carries its own pointer, since 2026-09-22.** When a span
includes work that the cut did not stamp, its notes say so in an
`### also inside this tag's span` section. That section names the pull request
and the release that does describe the work. The section is additive, so the cut's
own account of what it was for is untouched. The section is written after the
tag. That is the one time a notes file is edited, and it is safe because a
tagged release is never re-cut. Two kinds of span are exempt. The first is a
release's own cut pull request. It is inside its own span by construction, and
the next release stamps it every time. The second is the newest tag's span,
until the next release's notes exist. Before then, its pointer would have to
name a release that nobody has cut. The cut that writes those notes is asked
for the pointer on its own branch (`PL-JLYG`).

#### Why nothing reconciles the tag span and the notes automatically

Nothing *reconciles* the two records automatically. That was the decision
rather than an omission (`PL-028F`, decided 2026-09-14). The pointer above is navigation, and it leaves the
reconciliation untouched. Re-stamping at merge would need a job triggered by
the merge, and such a job cannot write to `main` here. A push made with
`GITHUB_TOKEN` starts no workflow, so the required status checks can never
report on it (`PL-N5WZ`). Every variant that does land needs a person at the
merge anyway. Absorbing a newcomer, meaning work that the base took in after
the cut, would make the release narrative describe work that the session that
cut the release did not do. That is a judgment no tool should make.

## The plan

This plan has one timeline. Clearing debt and building feature milestones are
steps on the same plan, listed in the order they happen.

### Why the gates are on this list and not behind it

The gates are not a background assumption behind the features. They are half
the work. A gate that lives in a separate document, or in a session's memory,
gets renegotiated every time it is inconvenient. On the timeline, a gate is a
step with a size, and skipping it is visibly skipping a step. The cadence that
generates rows 2, 4, 6, 8 and 10 of § "The timeline" below is specified
under § "The debt gate" below.

### The planning model: a rolling wave

**This plan is a rolling wave, and naming it that turns its restrictions into
a method.** Rolling-wave planning describes the near-term work in detail and
keeps later work at a higher level. Progressive elaboration is the process of
adding that detail as the work gets closer and more is known (Project
Management Institute, *PMI Lexicon of Project Management Terms*, entries
*rolling wave planning* and *progressive elaboration*,
https://www.pmi.org/pmbok-guide-standards/lexicon). Some rows are not yet
scoped, some catalogue entries have no definition of done, and some version
numbers are still provisional. These are the model working as intended, not
gaps in it.

Each planning horizon is described to one level of detail, in one place:

| Horizon | Written in | Detailed to |
| --- | --- | --- |
| Near | the section of each milestone scoped and not yet shipped, below | its goal, frozen debt list, required scope, definition of done and explicit out-of-scope list; its tasks are the queue items that required scope names |
| Middle | § "The timeline", in its rows not yet scoped | each a name, the catalogue items it takes and its place in the order, with no scope and no size |
| Far | § "Development pathway", ordering § "Planned milestones" | intent: phases over a catalogue whose entries carry no goal, required scope or definition of done |

**Detail moves to a nearer horizon at two moments.** The first is when a
catalogue entry is placed on the timeline, which gives it a row and a position.
The second is when that row is scoped, which is beat 1 of § "The cadence" and
writes the row's section in this document. A decision that a nearer horizon
depends on may be taken sooner. It is then recorded where that horizon cites
it. Break-out's display tier split is the example. It was settled on 2026-09-16
because it fixes the shape that v0.6.0 builds. That is a decision taken early,
not detail planned ahead.

#### Where the order of releases is recorded

**The order is recorded once, by horizon.** § "The timeline" records the order
of every release it names. § "Development pathway" orders only the work that
the timeline has not named yet, which is the work under its last row, Beyond.
If the two disagree about a release that the timeline names, the timeline
wins, because the timeline is where reorders are recorded. Each reorder is
dated on the row it moved.

**No second plan of releases is kept beside this one** (`PL-LJVD`). The order
of the releases and each milestone's scope are written here and nowhere else.
Another document names the release it means and points at that release's
section. A dated record of a decision remains the history that it is. A view
generated from this file is not a second plan. `bin/docket wave` and the plan
line in the session digest are recomputed on every run, so they cannot drift.
Prose can drift, and nothing compares two prose plans. A second prose plan
therefore stays in step only while someone remembers that it exists, and a
session remembers nothing.

### What MVP means here

**The MVP is complete when a learner can run a case, branch it at a decision
point, and compare the two managements side by side. The learner does this in
the units clinicians reason in, on a time base that spans a case.**

That is the Graph and the Overlay of the Gas Man reference simulator, which
is the design this project is building on. Everything after the MVP extends a
working teaching tool, instead of working toward one. The boundary is drawn
there because comparison is what isolates the variable under study. Running
one case teaches a curve. Running the same case two ways teaches why the curve
moved. A simulator that cannot do the second is a demonstration, not a
teaching tool.

Two *feature* releases reach the MVP. Both are interface releases on the
existing, already-validated model. Two other releases come before them. The
v0.2.8 patch makes the development loop reliable, and the two feature releases
will be built through that loop. Release v0.3.0 adds no capability. It exists
to clear the ground that the feature releases are built on:

- **v0.3.0, the foundation**: it clears Gate 0's inherited backlog.
- **v0.4.0, the teachable case**: one case from start to finish, in clinical
  units. It runs at a speed and on a time base that make the case's lessons
  observable at all.
- **v0.5.0, the case you can branch**: bookmarks, forking a run from a
  bookmark, and side-by-side comparison of the branches.

### The timeline

| # | Step | What it is | Size |
| --- | --- | --- | --- |
| 1 | **v0.2.8 — the workflow works** | **Shipped 2026-09-01.** Scoped below. Its scope is its own frozen list of thirty-eight entries, which fix the development machinery the project already runs on before two long milestones are run through it. Nothing in the simulator changes. The list has two groups, and the second is new workflow capability, not debt. | 2 M, 36 S |
| 2 | **v0.3.0 — the foundation** | **Shipped 2026-09-02.** The entries of Gate 0's frozen debt list that lie outside v0.4.0's own scope, released as a minor version by deliberate exception (§ "Versioning decision"). The list is recorded under v0.4.0 below. | 4 M, 17 S |
| 3 | **v0.4.0 — the teachable case** | **Shipped 2026-09-05.** Scoped below. Of its 13 items, 6 are Gate 0 debt that the milestone cleared itself. Twelve landed, and the thirteenth, `PL-011`'s retention rule, was dropped as superseded. Its Required-scope entry records why. | 7 M, 6 S |
| — | **v0.4.x — the code is the model** | **Shipped.** It is planned-milestone item 29, released as patches in the `v0.4.x` track. Its nine items closed between v0.4.4 on 2026-09-06 and v0.4.19 on 2026-09-13. It was scoped and then re-scoped 2026-09-03. The owner's bar is that a reviewer can follow `core/` without a lookup table. Naming alone cannot meet that bar, so the exact matrix exponential replaces the operator split (`PL-GS5X`). The exact step shipped in v0.4.4 and moves the displayed value in its last digit, so "No behavior changes" held only until the re-scope. The track still ships as patches, because it crosses no capability boundary. Item 29 explains this, and why no exception is recorded. The nine items are two under `numerical-domain` (`PL-GS5X`, `PL-X9KD`), six under `core-domain-language` (`PL-H46J`, `PL-212V`, `PL-3TLK`, `PL-9SH6`, `PL-VZL0`, `PL-FZ6T`), and a prerequisite of one of those six (`PL-X2XX`, which `PL-VZL0` requires). The count leaves out one item that had already shipped in v0.3.2 (`PL-P0BB`). One naming item (`PL-3TLK`) leads, and the rest of the naming work follows the exact step. **This track promises no particular patch number**, which is what `v0.4.x` means. Patches are cut as work accumulates, and the exact step takes whichever number it lands on. **It freezes no gate and takes no section of its own (project owner, 2026-09-05).** **Moved from ahead of v0.4.0 to behind it** (project owner, 2026-09-02). The real constraint on its place is that it come before item 6's substance generalization. Because v0.4.0 changes no equation, holding the teachable case back for an unscoped pass over `core/` gained nothing. | 1 L, 6 M, 2 S |
| 4 | **Gate 1** | **Frozen 2026-09-06**, the day v0.5.0 was scoped, and recorded in that milestone's own section below. It holds v0.4.0's findings, the queue's own defects and the model-specification debt. It ships inside v0.5.0, not as its own release, except for the three items this table had already placed on the `v0.4.x` row, which that track carries. In the event, it cleared across the `v0.4.x` patches as well: at v0.4.32, on 2026-09-20, the project's tooling counted 172 of the 175 entries then in the gate as clear. Since 2026-09-27, § "The cadence" has stated the rule that a gate's work ships in patches as it clears (`PL-LPH9`). | — |
| — | **v0.4.26 — the interface moves to Qt** | **Shipped 2026-09-17**, all 28 Required-scope ids closed (`PL-06YW`). The dashboard, the chart and the theme move to PySide6 + pyqtgraph, and nothing a learner can do is lost. This port was prototyped under one item (`PL-55DH`) and measured under another (`PL-X9T3`). **Scoped 2026-09-10**, on a decision made the same day (`PL-QXSB`), and it has its own section below. **It absorbed planned-milestone item 33, the interface pass, and that absorption was reversed on 2026-09-16** (project owner, 2026-09-16, ratified, on `PL-L9RD`). **Moved ahead of v0.5.0** from its row after MVP (project owner, 2026-09-14, on `PL-RKWB`). | 2 L, 2 M, 3 S |
| 5 | **v0.5.0 — the case you can branch** | Planned-milestone items 8 (replay half), 26 (bookmarks), 12 (forking) and 11 (comparison). **Shipped 2026-09-21**, all 20 Required-scope ids closed (`PL-4B1G`), and its own section below records what each one delivered. **The score architecture belongs here (project owner, 2026-09-05):** `PL-T691` (hold keyframes at every control event and compute any window in closed form), `PL-2FM6` (delete `RunHistory` and draw the chart from the closed-form sampler), `PL-P1Z3`, `PL-8LXM` and `PL-49R8`, filed under `numerical-domain` by the 2026-09-05 design round and chained behind the exact step (`PL-GS5X`). **Four of the five shipped in the `v0.4.x` track instead.** Two of them landed in v0.4.8 (`PL-T691`, `PL-P1Z3`). Two more (`PL-2FM6`, `PL-8LXM`) were brought forward on 2026-09-08, when another item (`PL-4RBD`) was re-measured at 0.32 MAC and re-banded `P1` `safety`. The debt-gate section records that decision. **Scoped 2026-09-06** with 18 Required-scope items, and that scoping froze Gate 1. Gate 1 stood at 185 entries on 2026-09-21, and that section dates the entries added after the freeze. Seven more Required-scope items shipped early in the `v0.4.x` track, and v0.5.0's § "Required scope" names them. | 3 L, 13 M, 2 S |
| — | **MVP complete** | **Reached 2026-09-21, with v0.5.0.** A learner can run, branch, and compare a case. | — |
| 6 | **Gate 2** | **Frozen 2026-09-21, the day v0.5.0 shipped, not when the milestone below was scoped** (project owner, 2026-09-16, ratified - chosen over freezing it on the scoping day as beat 1 says, and over deferring the whole scoping round until v0.5.0 ships). Row 7 was scoped two releases early, so the cadence's own trigger would have frozen this list before v0.5.0 had been implemented — leaving it holding none of v0.5.0's findings, which is the one thing a gate is defined to hold. § "The cadence" now states that as the trigger, the later of a milestone's scoping and its predecessor's ship (`PL-KKRP`); v0.6.0's own section says where the frozen list goes when the moment comes. Its work ships in `v0.5.x` patches as it clears, and it takes no release of its own (§ "The cadence", `PL-LPH9`). | — |
| 7 | **v0.6.0 — the layout is the reader's** | **Shipped 2026-10-20**, all 40 Required-scope ids closed (`PL-9CS6`). Planned-milestone item 34's tiled half: the layout model, the View contract, the view registry, workspaces, persistence, the unconditional display region, and every layout operation. **Scoped 2026-09-16** (project owner, ratified on `PL-NMTF` - chosen over inserting item 34 ahead of v0.5.0, and over one undivided milestone with break-out inside it). The serialized layout format carries a multi-window root from v1; nothing in this release creates a second window. Break-out, item 34's second half, is on no row: it is wanted eventually and not soon (project owner, 2026-09-26), and came off the timeline that day, having been the next release, "the second screen", since 2026-09-16 (`PL-V1Y7`) — see that section's "Explicitly out of scope" for why the split costs nothing structural, and why v0.6.0 keeps what break-out needs. **The placement was reopened and re-affirmed on 2026-09-17** (project owner, ratified - chosen over moving item 34 ahead of v0.5.0, on the argument that every interface question settled before the area model is settled against a layout that is going away). Planned-milestone item 34's entry carries the count, and the rule that round produced, which ended when this release shipped item 34's View contract and view registry. | 4 L, 16 M, 3 S |
| — | **v0.6.x — one source of truth** | Planned-milestone item 43: every second copy of a shared fact replaced by a read of its one home, with a check per shape whose baseline can only shrink and is burned down to zero. **Placed 2026-10-19** (project owner, 2026-10-19, ratified on `PL-2LB5`, over folding the fixes into v0.6.0 and over leaving them unplaced): it is built after v0.6.0 ships, and its inventory (`PL-K88Z`) runs before then, because the inventory decides how large the row is. Patch-track work like item 40: it crosses no capability boundary, so it takes no version of its own and freezes no gate. **Inventoried 2026-10-19** by `PL-K88Z`, whose brief records the count. | — |
| — | **v0.6.x — the interface pass** | Planned-milestone item 33: one deliberate visual design pass over the whole interface - palette, type scale, spacing rhythm, density and the visual composition of each surface - rather than the per-defect corrections the queue has been making one at a time. **Arrangement is item 34's and not this row's** (`PL-BNYF`, 2026-09-16); the entry for item 33 carries why. A patch track rather than a numbered milestone, because it crosses no capability boundary. **Restored here 2026-09-16**, having been absorbed into v0.4.26 on 2026-09-10 and un-absorbed when that port turned out not to have redecided the visuals; the row that release's own entry reversed is this one. **Moved here from between MVP and Gate 2 on 2026-09-16** (project owner, 2026-09-16, ratified - chosen over leaving it ahead of item 34, on the argument that item 34 and break-out introduce an area header, a workspace tab strip, a live splitter handle and a drag affordance, none of which exists to be styled today; what the other side bought was a styled interface two releases sooner, and `PL-BNYF`'s separation of arrangement from appearance means the composition of each surface would mostly have survived the move). It renumbers from `v0.5.x` to `v0.7.x` as a consequence: a patch track takes the number of the release it follows, which is mechanical rather than a second decision. `PL-PHKP` carries it. **Renumbered `v0.6.x` on 2026-09-26** by the same rule, when break-out came off the timeline and this row came to follow v0.6.0 (`PL-V1Y7`); the entry for item 33 records why the argument that placed it still holds. It is a design round with the project owner before it is items: the owner framed it as "a decent size overhaul (theme, style, overall polish)" and as not urgent, wanted after the simulator works. | — |
| 8 | **Gate 3** | **Frozen 2026-10-25**, the day v0.7.0 was scoped, five days after v0.6.0 shipped, and recorded in that milestone's own section below. Its work ships in `v0.6.x` patches as it clears, before v0.7.0's implementation begins. The current baseline above says how many of its entries had cleared when v0.6.16 was cut, and where its current size is given. | — |
| 9 | **v0.7.0 — the schematic** | Planned-milestone items 27 and 28: a compartment schematic whose containers fill to tension, as Gas Man's Picture does, labelled with their amounts and with a bar showing where the agent *is*, and the agent cost View. **Scoped 2026-10-25** by `PL-LF0P` (project owner, 2026-10-25, ratified, over containers drawn to scale, over Gas Man's Picture as it is, and over leaving item 28 unscheduled), and it has its own section below. (Written `v0.6.0` until 2026-09-16, when item 34 took that number and this moved down two, and `v0.8.0` from then until 2026-09-26, when break-out came off the timeline and this moved up one.) **Its Required scope closed in v0.6.16, except entry 13, which the project owner added on 2026-11-10** (`PL-HQPF`, `PL-RJN9`). That entry requires every agent amount on screen to name the condition it is stated at. The cut waits on entry 13, on Gate 3 and on the project owner's test drive. | 1 L, 9 M, 3 S |
| 10 | **Gate 4** | Frozen when v0.7.0 ships. Its work ships in `v0.7.x` patches as it clears, before v0.8.0's implementation begins. | — |
| 11 | **v0.8.0 — the next milestone** | What it holds is the project owner's pick, made when it is scoped. It was the substance generalization and nitrous oxide until 2026-09-26, when those came off the timeline (Beyond row). | — |
| 12+ | **Beyond** | In § "Development pathway" order: patient factors (item 30); the substance generalization with nitrous oxide and its effects (items 6 and 7); the machine abstraction with interlocks (item 1) and agent switching (item 2); the preferences panel (item 24); end-tidal control, override mode and direct injection (items 5, 3 and 4); item 8's scenario events and accessibility (item 20); save/load and replay (items 9 and 10); then intravenous agents (items 13-15). Item 30 comes first because the project owner placed it ahead of the substance generalization on 2026-09-02, and item 30's entry gives the reason. **The substance generalization and items 6 and 7 came off the timeline on 2026-09-26** (project owner, 2026-09-26: "Add it back once we have a really fleshed out single agent set up with workspaces all working"). Whether that condition is met is the owner's judgment, so a session placing the next row after v0.7.0 asks the owner rather than placing the generalization by pathway order (`PL-5XG1`). **Item 40, the machine-profile framework, is no longer in this row.** The project owner split it out of item 1 on 2026-09-20. It is patch-track work that may ship whenever its items finish, and it takes no version of its own and freezes no gate. What stays here is the interlock baseline, and the machine behaviors that need the solver work that item 40 defers. | — |

**The Size column counts the items that a step was scoped with, by effort
(L, M and S).** For a milestone, the count is its Required scope when it was
scoped, and for rows 1 and 2 it is the frozen list. Items added later are not
counted, so a shipped row's count of closed Required-scope ids can be larger.
A row shows "—" when it has no scope of its own to count: the MVP marker, a
row before it is scoped, a patch track other than `v0.4.x`, and a gate, whose
list is counted in its milestone's section.

**Rows 1 and 2 are the only releases whose whole content is a frozen list, and
row 2's list is a gate while row 1's is not.** Row 2 is Gate 0's release. Row 1
is not a gate: v0.2.8's frozen list is that release's own scope. Gates 1 onward
each contain one milestone's findings. Their work takes no release of its own
(§ "How gate work is released"), which is why rows 4, 6, 8 and 10 carry no
version.

Rows 5, 7 and 9 are scoped and have their own sections below. So does the
`v0.4.26` row above them. A row becomes real only when it gets its own goal,
required scope, definition of done and out-of-scope list in this document, as
the development rules require.

**Row 7 is the first milestone scoped out of turn.** Every earlier milestone was
scoped when it was the next release, as § "The cadence" assumes. Row 7 was
scoped while two releases were still ahead of it, for two reasons. First, its
design was already settled: the representation (`PL-3J2P`), the container
(`PL-C842`) and the provenance (`PL-FTP5`) had been fixed. Second, a queue
audit (`PL-BNYF`) had filed fourteen prerequisites against a build item that
did not exist, and those fourteen were waiting for the milestone to be scoped.

## Development rules for scientific milestones

- Define equations, units, assumptions, and reference cases before changing the
  scientific core.
- Keep simulation code independent of the UI toolkit, wall-clock time,
  filesystem state, and display dimensions.
- Store model parameters as validated data, with a schema version and
  provenance. Do not place executable equations in data files.
- Preserve deterministic results for an identical initial state, identical
  events and identical time steps.
- Treat mass accounting and independent reference cases as release gates, not
  optional diagnostics.

### Writing a milestone entry

- Keep each milestone narrow. A new idea belongs in the sections below until
  it is promoted into a scoped release. An idea that is a task rather than a
  release belongs in `docs/items/` instead.
- **A Goal is frozen at scoping and dated there.** It records the problem that
  the release was taken on to solve, in the tense and the state of the day it
  was scoped. Closing items do not amend it. What a milestone achieved is
  recorded in its Required scope and its Definition of done. Those are where
  to send a reader who is looking for the current state. Rewriting a Goal into
  the past tense one clause at a time leaves the section describing neither
  the problem nor the product. It also puts an edit to this file on the
  critical path of every closure. `PL-DXQC` is why this rule is written down
  rather than left to imitation.
- **An exclusion is written under `Explicitly out of scope`, never inside a
  `Required scope` bullet.** To decide which items belong to a milestone, the
  queue tool reads only those two subsections (`bin/docket next`). It reads
  `Required scope` *in full*, because a milestone names what it covers in
  whatever grammar the sentence needed, so `"(queue item PL-DHV7)"` in the
  middle of a bullet has to count. The cost is that an id named inside a scope
  bullet **in order to exclude it** is treated as scope (`PL-NBCS`). The
  documentation check fails when one milestone names an id under both
  headings, and warns when a scope bullet contains exclusion language
  (`tools/doc_check.py`).
- **When a shipped release's Required scope line turns out wrong about what
  shipped, it is annotated, never rewritten.** The line records what the
  release was scoped to do. Add a dated note beside it that states what
  shipped, like the note on v0.1.0's partition-data line (`PL-N32Y`, on
  `PL-4FBP`'s ratified convention that a dated record is corrected by a dated
  note).

## The debt gate

**Recorded technical debt is cleared before a new milestone begins.** Phase 0
applies this rule once, to get out of a queue that had stopped shrinking. This
section makes the rule standing. It runs again before every milestone, not
only before the first. It freezes a list at a moment rather than chasing a
moving one, so the list is always finite and the gate can always open.

The reason is that debt is cheapest to clear while the code it describes is
still code that someone remembers. A defect carried across a milestone
boundary has to be diagnosed again, against a codebase that has moved since.
A decision left unanswered stops being a decision that anyone can make.
Deferred debt is not kept. It is either paid for twice or silently dropped.

### Phase 0, which the debt gate replaced

**Phase 0 (foundation) was replaced by the standing debt gate on 2026-08-25.**
Phase 0 no longer blocks implementing a planned milestone. Only that
milestone's own gate does. Phase 0's unmet conditions are not carried forward
as a backlog. The items behind them are in the current frozen gate, where they
can be worked and finished.

The session that scoped v0.3.0 under `PL-003` retired Phase 0 in commit
`53cbecaa`. No record says whether the project owner asked for the retirement. The reasons
this section gives come from that commit's message.

Phase 0's original text was: no new feature work until the existing queue is
closed out. The rule was not made because features are unwelcome. It was made
because the last stretch of work felt like whack-a-mole. When Phase 0 was
written, the queue held almost no defects. It held decisions that nobody had
made: nine of its twenty-four open items sat at `needs-decision`. Over a third
of the queue could not be picked up by anyone, so the queue never visibly
shrank, however much work got done.

"All bugs squashed" is not a closing condition, since the absence of defects
cannot be demonstrated. The closing conditions were these:

| Phase 0 closing condition | State on 2026-08-25 |
| --- | --- |
| no open item classed `safety`, `science` or `defect` | **Not met.** 6 safety/science and 8 defect-classed items open. |
| no open item classed only as process work (`session-cost`, `docs`, `infra`) | **Not met.** 11 such items open. |
| no item left at `needs-decision` | **Met**, and deliberately unmet again the same day: PL-Y2GG (the license choice) was moved *to* `needs-decision`. |
| every outstanding branch merged and a release cut | **Met.** The branch `claude/pl-64ls-promote` is gone from the remote, and v0.2.4 is cut. |

**Why Phase 0 was replaced rather than pursued.** The first two conditions
ask the queue to reach zero in categories that every working session refills.
The queue doubled while Phase 0 was meant to be draining it: it held 24 open
items when Phase 0 was written, and 48 when Phase 0 was retired on 2026-08-25.
That is the capture rule working as designed, not a failure of effort. A gate
that requires a refilling queue to empty never opens. Such a gate has only two
honest outcomes: it is quietly abandoned, or it blocks all work forever.

The debt gate that replaced Phase 0 is strictly better for the same purpose.
Phase 0 was trying to buy two things: debt cleared while the code it describes
is still fresh, and decisions answered rather than accumulated. The gate buys
both on a cadence instead of in one push.

### What counts

Debt is what the queue already records, minus new work. An open item is debt
when it is classed `defect`, `safety`, `science`, `refactor` or `perf`. It is
also debt when its status is `needs-decision`, because an unanswered decision
is debt whatever it is about.

An item classed `feature` or `planning` is **not** debt. It is the work that
the gate exists to protect. Counting it would make the rule say "do everything
before doing anything", and no gate could ever open under that rule.

**Process work is debt once the mechanism is live, not before.** Building a new
capability into the tooling is new work, and it does not keep a gate shut. A
mechanism that `main` already depends on, and that does not work reliably, is
debt. It is classed `defect` like any other defect. The class carries the
rule, so there is nothing extra to track. The distinction is about state, not
layer. An unbuilt tooling idea costs nothing to carry. A half-working
mechanism that the project already runs on charges interest every session,
which is what debt means. Half-finished process machinery must not be in
production use. Either it is made to work reliably, or it is abandoned and
removed.

The first pass through this rule got one thing wrong, so here is a caution.
Classing tooling breakage as `infra` rather than `defect` makes it impossible
to tell apart from a capability that nobody has built yet. When
`docket release` leaves `uv.lock` stale and breaks `make check` at every
release, that is a defect. Adding release tagging is not a defect. If the
class does not separate them, the gate cannot either.

**The same test decides a hazard, and it is the one carve-out the `safety` and
`science` exception takes.**

**One exception to that exception: an `anticipated` `safety` or `science`
finding is not debt until the hazard it describes exists** (project owner,
2026-09-16, ratified, chosen over placing each on the *next* milestone's frozen
list behind a marker nothing enforces, and over leaving the rule as it stands
and putting the 2026-09-16 area-model findings on v0.5.0's list, `PL-83LS`).
The re-entry exception in § "The gate is a snapshot, not a moving target" is
unconditional about *when* a finding was made. This paragraph says what it
takes for a finding to count against the current gate at all. An item classed
`anticipated` describes a hazard that a later milestone will create. For
example, today the only thing a splitter handle can do is resize an Area
(`src/anesthesia_sim/app/area_layout.py`'s `AreaLayout`, live since `PL-W9P6`
on 2026-10-18). So no reader can close, replace or cover a required value until
planned-milestone item 34's docking operations are built. A gate exists to
clear debt *before* a milestone begins, so it cannot clear a hazard that the
milestone introduces. This is the live-mechanism test above, applied to a
hazard rather than to a mechanism.

Such a finding is then disposed of by a **placement in the milestone that
creates the hazard**, never by a deferral. v0.6.0's `Required scope` lists the ten findings that this
rule was written for.

**The carve-out expires with the wait it is granted for** (project owner,
2026-09-16, ratified, chosen over leaving it on the class alone, which never
stopped). The class `anticipated` claims that the hazard is not live yet. An
item stops saying `status: blocked` once the hazard is live. Its `blocked-by`
field is where it names what has to happen first. So only an item that has
written down what it is waiting for keeps the exemption, and the exemption
lapses when that wait ends. By contrast, the class on its own kept the
exemption running past the milestone that created the hazard. That milestone
creating the hazard is the one event the rule exists to notice (`PL-ZF2G`).
`subprojects/docket/src/docket/checks.py` already requires the same pair of
fields for the safety-band exemption. This rule reads the pair from there
rather than deciding it again, so that `anticipated` means one thing in both
tools.

The exemption lapses when the item is promoted, not when its blocker closes.
Nothing rewrites `status` by itself. Since `PL-2349` (2026-10-12),
`bin/docket check` rejects a `blocked` item whose item blockers have all
closed. So for an item blocker, the promotion lands in the pull request that
closes the blocker, and no window is left. A milestone blocker still leaves
one grooming pass, through its "is scoped and every other blocker has closed"
advisory. That one pass replaces the indefinite window that came before it.

`check_gate_reentries` in `tools/doc_check.py` reads both fields for this
reason. The rule therefore runs on every `make check`, rather than depending
on whether a session remembered it.

**What it costs, recorded rather than waved past.** `anticipated` now carries
weight it did not carry before. So a `safety` item that is wrongly classed
becomes invisible to the gate, which is `PL-MVC2`'s shape. Two things narrow
that risk, and neither removes it. First, the class is claimed rather than
inferred. Second, `PL-MVC2` itself made a class outside the declared
vocabulary a `bin/docket check` error. So a misspelling fails closed and
leaves the item named. Nothing catches a class that is spelled correctly and
applied wrongly. Catching that is a reviewer's judgment, and this decision is
what makes that judgment worth making.

### Debt inside the milestone's own scope

**Debt that the milestone itself exists to clear is cleared *by* it, not
before it.** This carve-out is necessary rather than convenient. v0.4.0 was
scoped in part *because* six safety, science, defect and perf items were all
symptoms of the same thing. A rule that required them to be cleared before the
milestone that clears them would have no order that satisfies it.

The test is whether the item appears in the milestone's "Required scope". If
it does, it is milestone work. The frozen gate lists it under a heading that
says so, and the gate is open when everything *outside* the milestone's scope
is clear. If it does not appear there, it is cleared first, whatever it is
about.

This does not weaken the `safety`/`science` re-entry rule below. Such an item
inside the scope is cleared by the milestone rather than deferred from its
gate. It simply cannot be finished
earlier than the work it is part of, and the milestone's definition of done is
what enforces it.

### The cadence

The gate is a recurring step on the plan, not a precondition assumed in the
background. Every milestone runs the same four beats. § "The plan" above shows
them on one timeline with the milestones they gate:

1. **Scope** the milestone here. Give its goal, required scope, definition of
   done and explicit out-of-scope list. Add the heading that its frozen list
   goes under, with no entries in it until the freeze. A milestone without that
   heading has not been scoped, whatever else has been written about it.
2. **Freeze and record** the debt list in that milestone's own section, as item
   ids, on the day it was frozen. The list freezes on the later of two days:
   the day the milestone is scoped, and the day the milestone before it ships.
   A gate that nobody wrote down gets renegotiated. The point of freezing the
   list is that it cannot be renegotiated. A frozen list is computed from the
   store's *classes*, so it cannot see an untriaged backlog. A freeze taken
   while captures are waiting understates itself by however many of them turn
   out to be debt.
3. **Clear** it before implementation of the milestone begins. Clearing means
   `done` **or** `dropped`, with the reason recorded. Deciding that something
   is not worth doing is a legitimate way to clear it, and often the right one.
   Leaving it open and starting anyway is not legitimate. Each item ends
   `done`, or `dropped` with its reason, or **deferred to a later gate** on the
   terms of § "Deferring to the next gate". **Sweep the frozen list for
   staleness first** (project owner, 2026-09-17, ratified, chosen over a second
   `verify:`-style field recording a fault test beside each fix test, and over
   leaving the sweep to whoever next noticed). § "Sweep the frozen list for
   staleness" below says why and how.
4. **Implement** the milestone. A finding made while clearing or implementing
   goes to the next gate, unless § "The gate is a snapshot, not a moving
   target" returns it to this one.

**Why the later of the two days** (project owner, 2026-10-03, ratified, over
keeping scoping as the trigger with exceptions recorded against it, `PL-KKRP`).
A gate contains the findings of the milestone before it. So a list frozen
before that milestone ships contains none of those findings, and sends them to
the gate after. A list frozen before its own milestone is scoped has no section
to be recorded in. The timeline fixes the freeze date, not whoever next opens
the section.

Which beat is due is computed, not remembered. `bin/docket wave` reads the
version, the timeline above, the milestone sections and the frozen list that
each section records. It reports the current step and the beat that leaves
that step. It reports only what those files decide. It does not report
whether a gate should open early, or whether what is written beside a step is
still true.

#### Sweep the frozen list for staleness

A `verify:` command is specified as one that fails before the work and passes
after it. So it tests for the presence of the fix, and never for the presence
of the fault. An entry whose defect no longer reproduces therefore fails
forever and looks like outstanding work. One measured pass found 12 of 134 open
items dead and 31 more overtaken, 32% in all. Nothing in the project noticed
this, and nothing can (`PL-LKGL`). Staleness is a judgment, which is why this
is a beat and not a check. Read each frozen entry against the tree. Drop what
no longer reproduces, with its reason. Correct the briefs that overstate what
is left. Do all this before spending a session on any of them. **File the pass
as its own item under `feature: gate-staleness-sweep`. Do not name a standing
one here.** Any item named here is an item that can close. The next gate's
session then looks that item up and finds it `done` (`PL-D8KW`). An instruction
to file an item cannot go stale the way a pointer to one item does.

#### How gate work is released

**A gate does not get a version of its own. Its work ships as it clears.**
Cleared gate work ships in patch releases on the preceding milestone's track:
`v0.4.x` while Gate 1 drained, and `v0.5.x` while Gate 2 does. A session cuts
one whenever it judges the finished work worth releasing. **Since 2026-09-27
the occasion for a cut is a feature finishing**. A session cuts a release with
what is in it, and the project owner pushes the tag. That is the instance the
judgment currently turns on. It is dated so that a later reader can tell it
apart from the rule. The gated milestone's own number is reserved for the
capability boundary that its scope crosses, per § "Versioning decision". That
milestone's release notes then carry its own scope. That is what a milestone
should carry when its debt was paid down as it went.

**This records the practice rather than changing it** (project owner,
2026-09-27, `PL-LPH9`).

Gate 0 is the single exception. It was released as the *minor* v0.3.0, for
the reason recorded under § "Versioning decision". It is exempt because it
holds the backlog inherited from before this mechanism existed. Every later
gate holds one milestone's findings and is ordinary maintenance.

### The gate is a snapshot, not a moving target

#### Which findings re-enter the gate

**When a milestone's gate freezes, the debt list is frozen at that moment**.
Beat 2 of § "The cadence" says when that is. A finding re-enters this gate,
rather than waiting for the next one, when the problem it describes was already
*present* at that moment. That is true whatever id the finding is filed under,
and however long after the freeze someone happened to notice it (project owner,
2026-11-07, over deferring a late capture by the date it was filed, `PL-GW0P`).
A finding
stays off this gate's list only when the problem itself is new. A new problem is
one introduced by work done while clearing this gate, or while implementing the
milestone that the gate protects.

This part is what makes the rule survivable rather than a deadlock. Work
generates findings. Clearing thirteen items in one session generated fourteen
new ones. That is normal, and it is the capture rule doing its job. Suppose a
gate reopened for everything noticed after it froze. Its queue could then
never empty, and its milestone could never start. The rule would then be
abandoned rather than followed, which is worse than not having it. The gate
tests when a problem was present, not when it was discovered. That keeps the
gate from reopening for findings of *that* kind. It still closes one gap. A
stranded branch or a slow session can mean that the same problem gets
rediscovered under a new id, and that finding still re-enters this gate
(queue item `PL-64LS`).

**Friction that compounds is the clearest presence case** (project owner,
2026-08-30). Some findings cost something again on every remaining entry.
Examples are a tool that answers the wrong question, a check that cries wolf,
and a command that ends red when it succeeds. Such a finding was almost always
present at the freeze. It was merely invisible until the gate's own work
started paying its cost. Deferring one is a decision to pay that cost once per
remaining entry. So it re-enters, and it is worked early rather than merely
admitted.

The test is arithmetic, not enthusiasm. Name what each remaining entry pays,
and multiply it by the number of entries that remain. `PL-0RS6` qualified at
eighteen entries, each paying a twelve-command detour. That total is a large
fraction of the saving the release exists to deliver. Some work is merely
valuable, cleaner or more interesting, such as rewriting a working tool in
another language or adopting a nicer abstraction. That work makes no remaining
entry cheaper. So it fails the test and waits for the roadmap, however
appealing it is. If nobody can name the saving per entry, the finding does not
qualify.

**Presence is a presumption, not an absolute rule.** Favor it. A finding that
continues or completes an item already inside the frozen list belongs to this
gate. Record it with the item it continues (`PL-SWFM`). Sometimes a specific
reason argues otherwise. The finding may have no real connection to anything
frozen. Or pulling it in may recreate the refilling-queue problem that the debt
gate replaced Phase 0 to solve. Then a session may defer a presence-qualifying
finding to the next gate anyway. Being filed after the freeze is not such a
reason (`PL-GW0P`). It may also decline to pull in a finding that
only superficially resembles frozen scope. Either way, the session must say so
and say why. Silently reinterpreting which gate a finding belongs to is the
renegotiation that freezing the list exists to prevent.

Two further exceptions re-enter the current gate regardless of presence:
anything at `P0`, and anything classed `safety` or `science`. This project's
own standard does not allow a `P0` to be deferred. A `safety` or `science`
entry may be deferred only on the terms of § "Deferring to the next gate".
§ "What counts" states the one carve-out, for an `anticipated` finding.

#### What a frozen entry may take in

**What a freeze closes is new scope, not the completeness of a fix** (project
owner, 2026-08-30). A frozen list exists to fix a specific set of problems.
Sometimes one of its entries needs a further finding before it is actually
fixed. Refusing that finding keeps the list at its length but defeats its
purpose. The rule in § "Which findings re-enter the gate" applies this, and it
is deliberately not symmetric. It keeps new work out, and it lets in what an
entry needs.

**And it is worked with the entry it completes, not after it** (project owner,
2026-08-30). Suppose a finding is admitted to the list and then worked later as
a separate piece of work. That brings back exactly the problem that admitting
it prevented. The first entry ships half-fixed while the work that finishes it
waits in the queue. So pair them: one branch, one review, and both closed
together. The issue is then fully addressed before anything else starts.

**What a frozen entry waits on has three homes** (`PL-D388`, project owner,
2026-10-03, ratified, over admitting every open prerequisite of an entry
automatically). First, work that the milestone's own `Required scope` names
makes the entry the milestone's, per § "Debt inside the milestone's own scope".
Second, work that no release schedules before the milestone begins defers the
entry on the terms of § "Deferring to the next gate". The deferral is recorded
as the entry's `deferred-from:`. Third, anything else is let in beside the
entry, dated, and worked with it as described above.

### Deferring to the next gate

**The third disposition in beat 3 of § "The cadence", and the terms that make
it legitimate** (project owner, 2026-09-21, ratified, over leaving each
milestone's own bullet to be read at its own cut). An entry may be *deferred to
a later gate* instead of cleared. The release then ships without it. That is
allowed only when all three of these conditions hold:

- § "The gate is a snapshot, not a moving target" permits the deferral.
  That means the deferral **says so and says why**. The entry's item
  carries `deferred-from: vX.Y.Z - <why>`, naming this gate. That field is
  the one record that every reader of the gate reads (`PL-8QMD`, project
  owner, 2026-10-11, ratified, over the deferral group headings the
  gate sections used to carry). The gate section may also set out the decision
  behind the deferral at any length.
- The deferral **lands in a named later gate**, which is the next one. The
  next gate's freeze carries every open entry that this list deferred,
  debt or not, taken from what `bin/docket gate` prints. This matters
  because an entry deferred to nowhere is what holds a release open
  (`PL-S5Q9`).
- The entry **stays written on the frozen list**, because removing it is
  the renegotiation the freeze exists to prevent.

A `safety`- or `science`-classed entry may take this route only when its
deferral also records that its hazard is **not live**: no learner can see a
wrong value now (project owner, 2026-11-07, ratified, over making these two
classes never deferrable, `PL-8C8W`). That must be
checked against the tree rather than asserted. It is recorded in the
field's reason or in the gate section.

**Stated here rather than in each definition of done**, because it recurs.
Completed milestones' bullets are left as written. They record conditions those
releases met, and editing a satisfied condition is the wider change
(`PL-Y949`).

**Record a deferral on the item, not in this document.** A debt item that the
current gate neither places nor takes carries `deferred-from: vX.Y.Z - <why>`.
The version is the milestone whose frozen list excuses the item. It is never
the gate that the item goes to, because the next freeze takes every open debt
item anyway. The reason states the grounds for the deferral, which is what a
reader of the gate is owed. `bin/docket check` fails an open debt item that the current
gate neither places nor defers
(`PL-WD5Z`). A frozen entry deferred on the terms above carries the same field
(`PL-8QMD`). A section may state the
grounds that its deferrals share, as v0.6.0's section does, but no tool reads
that prose. Until `PL-WD5Z`, a deferral was an id named in a `###` subsection
headed `Declined`, `Deferred` or `Sequenced`. v0.5.0's section keeps those
subsections: the `Sequenced` one keeps its table, and the others keep a
sentence or one line per ground. Each disposition's text is in its item's
brief (project owner, 2026-11-07, ratified, over keeping them here,
`PL-LVN8`).

### Recording it

**Do not write how many entries of a frozen list are closed.** A count written
into a document goes stale the next time an item closes. v0.4.0's section once
said "5 done and 9 remaining as of 2026-08-26", while one of the nine it named
had already been closed. `bin/docket wave` reads a frozen list against
`docs/items/` and reports the split. So the answer is computed from the same
files that anyone would use to check it. A count dated to a release, as the
cut items and § "Current baseline" give, stays.

Since 2026-10-24, a gate section does not name the lane each entry is worked
in. `bin/docket gate` and `bin/docket picks` print the lane, because a lane
written into the section goes stale (`PL-Z64T`). `docket.toml` computes a lane
from each item's `touches`, which triage and every close-out rewrite. The lanes
still say how the list is worked. The product and workflow lanes share no
files, so they run concurrently in two sessions. The entries in neither lane
cross both lanes, and they need a session that can hold the whole change.

**Do not write a deferred item's state or release beside it.** `bin/docket
wave` prints each deferral of the current gate with its state and release,
read from the store (`PL-B60Q`). A mark written by hand would only copy a
field that the store already records.

## v0.7.0 - the schematic

This milestone is planned-milestone item 27, the compartment schematic, with
item 28, agent cost, beside it. `PL-LF0P` scoped it on 2026-10-25. The
schematic and the agent cost readout are each a View of their own, which any
Area can hold. The project owner confirmed this in the scoping round. Two
choices went to the project owner:

1. The schematic's containers fill to tension, as in Gas Man. They are
   labelled with their amounts, and a bar shows each compartment's share of
   the agent (project owner, 2026-10-25, ratified, over containers drawn to
   scale and over Gas Man's Picture as it is).

   **Gas Man's Picture shows where the tension is. It does not show where the
   agent is, and that is the lesson planned-milestone item 27 was written
   for.** The Gas Man Workbook's Figure 2-1 (printed p. 11) draws the circuit,
   the alveoli, arterial blood, the vessel-rich group, muscle, fat and venous
   blood as containers of one width. Each one fills "to a height representing
   partial pressure or tension in that compartment" (printed p. 11). The only
   amounts it shows are two totals in litres, Uptake and Delivered. A setting
   turns these into money. Appendix E (printed p. 188) gives the Picture's
   purpose as "viewing and manipulating the state of an experiment at a given
   point in its evolution", and says "the compartment schematic helps you
   visualize the relationships between compartment tensions".

   **Drawn to scale, four of this model's six containers would be between 1 and
   7 px wide in a 600 px View.** A container whose width is its capacity holds
   an amount equal to its filled area. Mapleson's electric analogue rests on
   the same relation, q = C·v. A condenser's charge equals its capacitance
   times its voltage (Mapleson WW, *J Appl Physiol* 1963;18(1):197-204,
   https://doi.org/10.1152/jappl.1963.18.1.197, read from the private reference
   corpus, equations 5 and 6). But this model's capacities span almost three
   orders of magnitude. For sevoflurane, fat holds 493 L of gas equivalent and
   venous blood 0.79 L, a ratio of about 620. In a View 600 px wide, drawn to
   scale, fat takes about 500 px. The circuit, the alveoli, venous blood and
   the vessel-rich group take between 1 and 7 px each. Isoflurane and
   desflurane give the same picture. These figures were computed from the
   shipped parameter files on 2026-10-25 (`PL-LF0P`).

2. Item 28 is built here rather than left unscheduled (project owner,
   2026-10-25, ratified, over leaving it out and deferring its four entries to
   Gate 4).

The rest of this section was decided in the scoping round without being put to
the project owner, because each remaining choice either had one clearly better
option or concerned look, wording or placement. Those are placeholders while
structure and function are being built.

### Goal

The end state is as follows. A learner places the compartment schematic in any
Area. For each displayed run, the schematic shows the circuit, the alveoli,
venous blood and the three tissue groups, in the order the agent reaches them.
Each fills to its tension on one shared scale, as in Gas Man. Each is labelled
with its amount of agent vapour. A bar shows each compartment's share of all
the agent the run holds, so fat's share grows on screen while its tension
stays near zero. A second View, the agent cost View, shows the delivered agent
in millilitres of liquid equivalent, and in money at a price the reader sets.
Every number on it is the number that the rest of the interface gives for the
same run at the same instant, and the View says that its values are modelled.

The interface draws tension and almost nothing else. The concentration chart
and the readouts give each compartment's partial pressure, in % atm and as a
MAC multiple. So the slow compartments look empty while they hold most of the
agent. The table below was measured on this model, with sevoflurane held at a
1 MAC dial, for the reference adult at the shipped defaults:

| At | Muscle: tension, share of stored agent | Fat: tension, share of stored agent |
| --- | --- | --- |
| 60 min | 0.50% atm, 49% | 0.03% atm, 20% |
| 180 min | 1.16% atm, 54% | 0.11% atm, 30% |

Fat's trace sits within a few pixels of zero on the chart for that whole time.
`PL-H5DV` measured the same pattern for all three agents, and the hours that
fat takes to overtake muscle.

As things stand on 2026-10-25, there are four gaps:

- **No surface says where the agent is.** The only amounts on screen are the
  agent accounting View's delivered, exhausted and stored totals, in litres of
  vapour. That View is a check that the model conserves mass. The project owner
  called it "not info the user really needs or cares to see" (2026-09-16,
  recorded in `PL-B396`).
- **The amounts exist and are not passed on.** Each compartment in `core/`
  stores its own `agent_amount_l`. `SimulationSnapshot` in
  `src/anesthesia_sim/app/controller.py` carries only their total,
  `stored_agent_l`. Nothing was left out by mistake. `ROADMAP.md` § "Designed
  for forking" declined per-compartment amounts until a consumer needed them,
  and this milestone is that consumer.
- **No View draws how the compartments connect.** The chart puts six traces on
  one axis. Nothing shows that agent passes from the circuit to the alveoli,
  then to the blood and on to each tissue, driven by the difference in
  tension. That relationship is what Gas Man's Picture exists to show.
- **Nothing says what the agent cost.** A clinician buys and fills agent as
  liquid, and the low-flow lesson of planned-milestone item 28 is about money.

### Debt gate: the frozen list

**Two groups, and only the second must clear before this milestone's
implementation begins.** The first group is debt that this milestone's own
Required scope names. The milestone clears that debt itself, as § "Debt inside
the milestone's own scope" says. The second group clears first, unless an entry
is deferred as § "Deferring to the next gate" says.

**Frozen 2026-10-25, the day this milestone was scoped.** Every open item that
counts as debt under § "The debt gate" above is on this list. The list shows
the store as it was at the cut: `origin/main` at `0947408`, with this
milestone's own items added.

**Swept for staleness on 2026-10-25** (`PL-F2NX`). Beat 3 of the cadence
requires this sweep before any entry on the list is worked. Each of the 24
entries open at the time was checked against the tree. None described a
problem that no longer reproduces, so none was dropped. Three briefs asked for
more work than is left. One entry waited on less than its record said, and two
waited on more. Each entry's brief carries its dated verdict, and `PL-F2NX`'s
brief has the tally.

**`PL-WZVZ` and `PL-B4P7` are deferred to Gate 4 on the terms of § "Deferring
to the next gate".** Both wait on machine selection, which no release
schedules. `PL-WZVZ` waits on `PL-TBMK`, a second machine profile, and on
`PL-4TWW`, the surface that selects between profiles. `PL-B4P7` waits on
`PL-2FZ9`, which loads a profile by id. Through `PL-2FZ9`, it also waits on a
second profile reaching a run. Checked against the tree at `0947408`, neither
hazard is live. `src/anesthesia_sim/data/machines/` holds one profile,
`reference_circle_system.json`, and nothing in `src/` selects between profiles.
So no displayed value can be attributed to the wrong machine, and no run can
open at another machine's flow. Gate 2 deferred `PL-WZVZ` for the same reason,
the same unmet condition (`PL-DB64`, project owner, 2026-09-27, ratified, over
keeping it on the list to hold the gate open). `PL-B4P7` was captured after
Gate 2's freeze and waits on the same condition. So the scoping round gave both
items the same disposition, without putting the question to the owner again.

**`PL-5B1N` clears in this gate.** It is the preview a control draws while it
is grabbed and not yet released. Only one open entry of v0.6.0's list is not
debt: `PL-5B1N`. It is on this list too, because a freeze carries over every
open entry of the previous list (`PL-JV5Q`). v0.6.0's gate deferred it to Gate
3 (`PL-YBFB`) with `blocked-by: v0.7.0`. `PL-5B1N` closed with its build, and
§ "Captures after the cut" records `PL-4LS8`, which held the one question that
build left open.

**This milestone itself clears the four entries that v0.6.0's gate deferred
for item 28.** `PL-B396`, `PL-KZ99`, `PL-0S0V` and `PL-VJZK` came onto this
list deferred from v0.6.0, because no release scheduled planned-milestone
item 28 (`PL-DB64`). This milestone schedules item 28, so the Required scope
below names all four, and they are in the first group. `PL-B396` is now also
classed `safety`, because it builds a unit conversion that is displayed.

**Cleared by v0.7.0 itself - 11 entries**

- PL-RNYV (L) Build the compartment schematic View: the circuit, the alveoli, venous blood and the three tissue groups as containers filled to tension, each labelled with its tension and its amount of agent vapour
- PL-0S0V (M) AGENT_VOLUME_DISPLAY_DECIMALS and the other display-precision constants are one Final per quantity, but once the unit is reader-selectable precision is a function of quantity AND unit, and docs/MODEL.md's derivation has to be per-unit too
- PL-1P15 (M) Show what the delivered agent cost in money, at a price per agent the reader sets, on the agent cost View
- PL-2881 (M) Specify the compartment schematic in docs/MODEL.md before it is drawn: what a fill height and an amount assert, how a vapour amount and a liquid-equivalent amount name their units, and the precision a compartment's amount is shown at
- PL-B396 (M) Agent amounts are displayed in litres of vapour, which is not the unit a reader buys, fills or wastes agent in - report a liquid-equivalent millilitre figure
- PL-KFTM (M) Carry each compartment's modelled agent amount on SimulationSnapshot as one record per compartment, and derive stored_agent_l from those records
- PL-KZ99 (M) Store each agent's molar mass and liquid density with the density's measurement temperature, so a vapour-to-liquid conversion is derived from a primary measurement rather than from a published composite constant
- PL-S79P (M) Draw each compartment's share of the agent the run holds as one bar on the compartment schematic, so fat's growing share shows while its tension stays near zero
- PL-VJZK (M) A reader-set agent price makes a displayed economic value's provenance partly the reader's, so the stored price needs its currency and the date it was set, and the display must not read as an authoritative figure
- PL-HQPF (M) The accounting panel's unit caption ('Litres of equivalent pure agent gas') and the schematic's unit ('mL vapour') do not name the condition an agent amount is stated at, 20 °C and 1 atm, so a learner cannot tell that an amount held in the body is stated at room temperature and reads 5.8% high
- PL-RJN9 (S) The agent cost View's two captions in src/anesthesia_sim/app/agent_cost.py write '20 degrees C' as text, a second copy of core/liquid_agent.py's REFERENCE_TEMPERATURE_CELSIUS, so a change to the reference temperature would leave the captions naming the old one

**Cleared before v0.7.0's implementation begins, unless deferred - 157 entries**

- PL-H57W (L) Since PL-CZXN no check measures whether a branch that changes no core function weakens a core unit test, because PL-7FPD's route compares only the display modules' mutants; the same comparison over core's mutants took 538 to 968 s for one changed test file
- PL-5B1N (M) Simulated traces should be solid and a dotted trace should mean an uncommitted predicted future, but dash pattern is already spent as the six traces' colour-blind-safe channel
- PL-4LS8 (S) Record the owner's answer on whether a dragged-dial preview curve may draw at 1 px or stops at 2 px
- PL-B4P7 (M) A run opening at the teaching-default fresh gas flow records nothing saying so, so once a second machine profile can reach a run nothing can label that flow as the project's teaching choice rather than the machine's
- PL-F9TC (M) src/anesthesia_sim/app/ re-checks quantities that core already owns: formatting.py checks mac_percent > 0 five times, playback.py checks tick_interval_s by hand instead of require_positive_finite, chart_time_base.py restates half the case-instant range twice, and simulation_view.py restates the 1-to-MAX_DISPLAYED_RUNS run count that RunCount holds
- PL-G84G (M) No check and no one-source-of-truth item covers a text fact restated under src/ (a unit label, a display name): tools/literal_home_check.py reads numbers only and PL-K88Z's inventory surveyed no strings; on 2026-10-24, 112 distinct short string literals sit in two or more modules under src/anesthesia_sim/, 12 of them unit-like
- PL-HSP8 (M) Returning to a mark opens the branch with a setting the trunk changed at that instant already in force, so the 'on your mark' branch repeats the trunk's own decision, though docs/MODEL.md calls it the branch the halt would have given
- PL-JS6P (M) Add a doc_check rule that ties each number docs/MODEL.md and README.md restate to its home in a data file or in code, and fails when they disagree
- PL-M85T (M) Three core class defaults restate data-file values (alveolar gas volume 2.5 L and ventilation 4.0 L/min in alveolar.py, circuit volume 6.0 L in circuit.py), and a fourth, the 100% maximum delivered concentration, matches no agent's vaporizer: decide whether they become required arguments
- PL-QQGZ (M) CI's quality run grew from a median of about 2 minutes in early September to about 8.7 minutes in the week of 2026-10-12, and its pytest step is 737 s against the 470 s baseline: find what slowed it
- PL-QX2G (M) Give the gas, blood and tissue volumes and the partition coefficients a declared numerical envelope, refused at build as checked types: today each is only positive and finite, so a tissue volume of 1e-300 L with a tissue:blood coefficient of 1e-30 makes washin_rate_s raise a bare ZeroDivisionError, and a 1e307 L tissue with a 1e-307 tissue:gas coefficient has a 1 L capacity but an infinite time constant
- PL-J5GC (M) The run screen's widgets each have one writer since PL-X7D5 and PL-WM5P, but nothing requires values shown together to come from one state, so a label, divisor or verdict can come from a different state than the value beside it: three members filed after PL-WM5P closed
- PL-SC0N (M) A pull request number is an int wherever docket and tools hold one, so a number parsed by hand reaches NewestPullRequest, SubjectPullRequest, Remote.frozen or pr_body_check.recovered unrefused; a PullRequestNumber type that only model.pr_number produces would make mypy refuse it (found building PL-N4FP)
- PL-WJJ8 (M) On a worker branch, make check's bin/docket check --verify fails the worked item as 'open but its verify: command already passes', because docs/worker.md forbids a worker to set status: done, so a worker that finishes its item correctly can never report the gate green
- PL-WM5P (M) Extend the run view's single-writer guard (PL-X7D5) to every surface that states run state, so no displayed run state has a second writer
- PL-WZVZ (M) Make an inter-machine difference attributable: which parameter differs, and what it does to the result
- PL-3B34 (M) A dial moved on a halted run, whether failed or stopped at the 24-hour supported run length, is applied to the core and recorded as a control change at the halt instant, so the settings readouts and the control-change record show a setting that no step ever ran under beside concentrations computed under the previous one, while the banner says the values shown are the last completed step
- PL-97WX (M) Dragging an Area border converts the pointer to a fraction linearly across the split while the splitters draw settle's held sizes, so a 1 px nudge of a held border rewrites the stored fraction (0.7 to about 0.626 in one case) and emits layout_changed though nothing moves, and the border then sticks for tens of pixels
- PL-K5BS (M) Resetting a branch after the learner changed a setting keeps the new setting, clears the branch's control timeline and writes the setting over the fork's opening stretch, so the branch runs under settings that neither its control record nor its `opened_from` provenance states, and the `_open_at` docstring's claim that the definition "always opens at the parent's stretch, under the parent's settings" is false at a control-event fork
- PL-MLPT (M) docs/MODEL.md and core/supported_ranges.py argue the 24-hour supported run length with two claims that do not hold: that it sits near the outer edge of the measured 0.35-to-9.5 MAC-hour range, when a run at 1 MAC reaches about 24 MAC-hours at the cap, and that the fat time constant bounds it from below, when 24 hours is about 0.6 of that time constant
- PL-N559 (M) At zero cardiac output and high fresh gas flow, the exact propagator settles with the alveolar fraction a few units in the last place above the inspired fraction and the dial, so read_wash_in classes the steady state as elimination and the wash-in plot tells the learner the patient is returning agent while nothing changed
- PL-QBQX (M) A run that halts on a mark still shows the status word "Paused", the same word as the learner's own Pause, and the only sign that a mark stopped it, the "Branch here: …, stopped on your mark" label, is withdrawn while two runs are compared, so a halt during a comparison, or a second halt on a MAC target whose row already reads "reached", looks like a pause nobody made
- PL-QZ7Z (M) layout/sizing.settle lets go every Area under the first unheld split at once, and that split is always the root, so a window a few pixels short of the Views' needs blanks every View, including ones that would still fit if one Area gave way
- PL-TNYP (M) A branch taken at a keyframe opens with the trunk's change at that instant already applied, but the offer is labelled only "1m", the branch's record says no setting changed, and a later edit to the trunk at the same instant erases the trunk's only record of the change the branch runs under
- PL-9B1M (M) A step from a state at the top of the fraction range, every compartment at a partial pressure fraction of 1, rounds a fraction up to 3.5e-11 past 1 (1986 of 10 368 steps in the envelope sweep), so AgentUptakeSystem.advance rolls the step back with SimulationNumericalError; the display path at the stiffest corners draws fractions up to 1.000033 without refusing
- PL-D88N (M) The mass-balance check's fixed relative tolerance of 1e-9 halts a stepped run at the numerical envelope's stiffest corners within seconds (4.3 s at a 0.01 L lung with blood:gas 1e4, measured 2026-10-25), because each step's propagator rounding there is about 1e-10 of the state; decide whether the tolerance should follow the propagator's stated error bound, 2**s times machine epsilon per step, or say why a fixed one is right
- PL-QVBR (M) A MAC target that a stepped reading lands on exactly halts the trunk and reads reached there, while a branch opened on that step asks the canonical reading, which can lie about 1e-14 short, so the branch opens on no crossing and reads the target as still running
- PL-0KPD (S) Paint cost at the window-following column budget is unmeasured: extrapolating the owner's 6.7 us per drawn point from one 3 204-point reading puts two compared runs on a 3 840 px plot at about 207 ms, past the 200 ms render interval, and only the owner's hardware can measure it (found closing PL-PGZF)
- PL-44R1 (S) The headless worker host still resolves make to /usr/bin/make (GNU Make 3.81), so make check fails the two GNU make comparison tests in tests/unit/test_makefile_reference.py on every worker run after PL-TSH9 closed, and no worker there can report the gate green
- PL-5PL5 (S) Parallel builder subagents in one session share one scratchpad folder, so one builder's pull request body was published on another's pull request (#1735) and a builder's verify.log was overwritten; the builder brief names no per-item file prefix
- PL-6YKY (S) Field guards in core/ match a field's name as a string (circuit.py's __setattr__ tests name == "circuit_volume_l", blood.py and tissue.py test name == "volume_l"), so renaming the field leaves its validation keyed to a name nothing sets any more and the check stops running without an error
- PL-84G1 (S) core/circuit.py set_circuit_volume checks the stored agent against the circuit volume by hand, with a vaguer message, instead of calling validation.require_room_for_the_agent_held as the alveolar, blood and tissue compartments do
- PL-88MK (S) dashed_pen leaves Qt's default square cap on 2-3 px pens, so each dash paints one pen width longer and each gap one shorter; three dashed compartment traces look near-solid, and dash is the only channel separating compartments for colour-vision-deficient readers
- PL-9DF9 (S) fit_to_run and following_window in app/chart_time_base.py each check by hand that newest_sample_s is finite and nonnegative on a bare float, where the one caller hands them the newest run snapshot's elapsed_s, a case instant: the chart time base is a holder of a case instant PL-CN5S left untyped, beside PL-RCYZ's control record (found sweeping PL-ZGYX)
- PL-9K28 (S) A builder subagent that runs make check in the background ends its turn and is not woken when the command finishes, so the PL-ZZ03 builder stopped twice with tested work unpushed until the parent resumed it; builder briefs do not say to run long checks in the foreground
- PL-BM6X (S) The branch panel's refusal notice outlives the case it was about: an agent change on the trunk starts a new case without emitting case_restarted, so 'Select an instant to branch at' stays on screen after the switch (reproduced offscreen by PL-K88Z's inventory)
- PL-CQ1M (S) BreathingCircuit.advance_fresh_gas, formed from the fraction it holds throughout (PL-YT8N), carries a washout residual only to an ulp of that fraction: at forty time constants it reports exactly 0 where the balance leaves 4e-18; the two-regime arrangement core/exponential_approach.py takes forms the result from the equilibrium beyond half a gap and keeps the residual, and the circuit could take the module (found reviewing PL-XWFP)
- PL-FPLQ (S) tests/integration/test_qt_chart.py::test_the_hover_answers_the_point_under_the_pointer failed in make check under a load average of about 30 on four cores, reading the previous point's hover, and passed alone in 2.9 s: _wait_for_hover gives delivery only _HOVER_DELIVERY_MS = 1000 ms of wall-clock time
- PL-GH8L (S) Four builder subagents each running the full suite at once drove the container's load average to about 30 on 4 cores, so bin/docket verify --self's make check step hit its fixed 1,800 s limit and gave no answer on three branches
- PL-GKX6 (S) bin/docket delegable offers an item whose work creates a new tracked file outside every workflow_paths and product_paths entry, while its touches omit docket.toml, so tools/workflow_paths_check.py fails make check and the worker must block (PL-928V, docs/workflow.md)
- PL-LL9F (S) plan.promotable skips any blocked item that also names a milestone in blocked-by, so closing an item blocker never refuses or names a dependent whose milestone blocker had already cleared: PL-K88Z's closure in #1712 left PL-JS6P, PL-WM5P, PL-VWXL and PL-SH0W (blocked-by v0.6.0, PL-K88Z) at blocked with only a grooming advisory
- PL-P55M (S) EMPTY_METRIC_QUALIFIER and EMPTY_METRIC_SECONDARY_VALUE hold a no-break space for a Flet layout fact Qt does not share: under PySide6 6.11.2 an empty label is as tall as one holding U+00A0 (found closing PL-TMSN)
- PL-P58M (S) A halted run keeps showing the old playback rate on the clock's second line after the playback-rate dropdown changes, because present_halt does not write the readout row and PL-X7D5's guard exempts _readout_row (reproduced offscreen by PL-K88Z's inventory: 5x in the dropdown, 1x real time in the readout)
- PL-Q3G9 (S) app/dashboard_frame.py's PARAMETER_CONTROLS types the unit L/min for fresh gas flow, alveolar ventilation and cardiac output, which app/control_record.py's CONTROL_INPUT_UNITS already holds, so a change to a control's unit in one leaves the panel label or the recorded unit wrong in the other
- PL-QG52 (S) BreathingCircuit.restore_state writes back a captured fraction rather than an amount, so a restore after the circuit volume changed creates or destroys agent and the next step fails accounting
- PL-RCYZ (S) ControlChange.elapsed_s, and ControlAdjustment's started_at_s and ended_at_s, are annotated float though every one is taken from a CaseInstant - SimulationState.elapsed_s - so the control record is the one holder of a case instant PL-CN5S left untyped (app/control_record.py and app/control_timeline.py were outside its touches)
- PL-VWXL (S) Add pylint's duplicate-code check (R0801) as a ratchet over src/, tools/ and subprojects/docket/, with a baseline that can only shrink
- PL-W5JR (S) A sent-back headless worker branch hides its item from bin/docket next, and the daily branch sweep keeps it, so only the owner's hand push can release the item: claude/pl-928v-worker after #1733 carried its two commits to main
- PL-YF16 (S) bin/docket show's session line names the configured model whenever it differs from the served one, and 292 of the ledger's 327 such rows differ only by a [1m] context-window suffix, so the note mostly flags sessions that never switched model and buries the 35 real fallbacks: compare with the suffix removed, or print the context window apart from the model
- PL-YH6Z (S) The wash-in hover prints the crossing column's F_A/F_I above 1 under the label 'Wash-in F_A/F_I', a value app/wash_in.py classes as elimination and refuses to show as wash-in
- PL-YHWH (S) core/parameters.py restates three rules that other core modules already own: the perfusion fractions summing to 1 (patient._require_fractions_sum_to_one), MAC within the vaporizer maximum, written twice (validation.require_within_vaporizer_maximum), and run_definition.py checks spacing_s positive and finite by hand instead of require_positive_finite
- PL-YT3T (S) A compartment's own step has a floor and no ceiling, so BreathingCircuit.advance_fresh_gas at a step near 1e308 s, or at a circuit volume near 1e-310 L, overflows the time constants elapsed to inf and returns an exhaust of inf or nan without checking it
- PL-02CD (S) The MAC-awake band's docstring in app/formatting.py and the Chortkoff 1995 source note in desflurane.json both say that importing Chortkoff's absolute 2.60% would teach a later wake-up, but a band drawn too high is crossed sooner during washout and teaches an earlier one, as docs/MODEL.md says
- PL-0WFJ (S) The guard every run opening shares, require_canonical_state, checks a state's length, finiteness and unit entry but no physical range, so a RunDefinition opened from a state with an alveolar fraction of -0.3 and a fat fraction of 1.7 accepts it and returns negative and above-one fractions from state_at and evaluate_anchored without any error, while the live system refuses the same state
- PL-39KH (S) docs/MODEL.md's MAC-awake section calls its benchmark a 3-hour 1 MAC sevoflurane case, but the default 2% dial at 4 L/min brings alveolar and vessel-rich only to 1.69% (0.84 MAC) in 3 hours, and it blames the vessel-rich trace's failure to reach the 1 MAC line on a short case, when ongoing uptake keeps every trace below the line however long the case
- PL-5RPD (S) docs/MODEL.md says two runs at different step sizes are two roundings of the same solution, but a step holds each setting for its whole length, so a control change lands at a different instant on each step grid and two runs with any setting change follow different trajectories by more than rounding
- PL-6RJ0 (S) The "1 MAC sevoflurane = 2.0%" line is written on a different path from the readout cards whose ×MAC values it divides: a halt after an agent change writes the new agent's 1 MAC above cards still holding the old agent's multiples, and a raise from setting_readouts would leave the old 1 MAC above freshly written cards
- PL-9SL5 (S) RunDefinition.evaluate spaces its columns as start_s plus a multiple of the spacing and never pins the last one, so about one window in forty returns a final instant one rounding unit past stop_s, and past the run's reach when stop_s is the reach, which the method says it refuses
- PL-C9XP (S) AreaLayout's minimum size hint is the sum of the Views' needs, while settle and each frame hold an Area at the larger of need and floor, so where a header floor is wider than a View's need the scrolling page grows too little and a neighbouring View shows "Too small" (568 px hint against a 585 px requirement in one case)
- PL-DQL9 (S) The uptake matrix takes the pulmonary blood:gas coefficient from the venous pool and each tissue's rate from that tissue's own blood:gas coefficient, and nothing requires the four to agree, so a mismatch makes the matrix create agent and halts the run as an AgentSimulationValidationError that blames the numerics for an inconsistent parameter set
- PL-GCGX (S) docs/MODEL.md says every way of misreading the MAC-awake band runs toward an earlier wake-up, but the band also inherits the Gas Man MAC divisor, which puts sevoflurane's band 11% above the primary literature and desflurane's 9% below it, and the sevoflurane and isoflurane mac_reference_basis record no base MAC
- PL-P319 (S) The sevoflurane and isoflurane mac_awake.mac_reference_basis cannot name the base MAC in percent or the age correction Katoh 1993 used, because the abstract gives neither and the full paper is not in the reference corpus; read the paper and name both, and state the form of Katoh's brain-uptake calculation in docs/MODEL.md
- PL-HF4B (S) After an agent-accounting failure halts a run, the rollback restores the previous step's passing validator, so the accounting panel reads "Valid" and "The simulation still accounts for all delivered agent" directly under a banner saying accounting validation failed, and the banner quotes the failed step's delivered and stored totals beside the panel's different restored ones
- PL-KDZW (S) When SimulationView._place_run refuses a run for a missing unconditional value, the run's transport row, banner, readouts and record are already in the shared layouts and stay there, so a refused branch from add_run leaves frozen widgets that no slot will ever refresh or remove
- PL-KHXB (S) The banner shown when a run reaches the 24-hour supported run length, and the core's refusal message, tell the learner that beyond it the model's omitted metabolism and its fat perfusion dominate the trace, for every agent, though docs/MODEL.md says nothing breaks at hour 25 and only sevoflurane is metabolized enough to matter
- PL-M8F6 (S) docs/INTERFACE.md § "Halting on a marked crossing" says the concentration displayed beside a halt is the height the learner marked, but the run halts on the first step at or past the height, so a circuit target of 0.10 ×MAC halts showing 0.11 ×MAC on 13 of 59 targets tried, and a learner reads a correct halt as a detection fault
- PL-NRR6 (S) A branch can be taken at the keyframe where the paused trunk stands, but the trunk can still replace or delete that keyframe with another setting change at the same instant, after which the branch's `opened_from` names a stretch the trunk never ran and `trunk.resumed_at` refuses the instant the branch opened at
- PL-PM67 (S) docs/MODEL.md says the fractions cannot leave their physical range and no parameter set can trigger the capacity guard, and core/exceptions.py says no step can raise SimulationNumericalError, but the Metzler argument proves only the lower bound, and rounding carries a fraction just above 1 from a saturated state
- PL-S11T (S) A frozen `UptakeEquationSettings` restored by unpickling is rebuilt through `__setstate__`, so its `__post_init__` never runs: a saved record whose state holds cardiac output as a bare 1000.0 and fresh gas flow as NaN loads with no error, and `RunDefinition` accepts it and advances, although `PL-5D1Z` closed the same hole for the flow values themselves
- PL-T5NJ (S) The chart hover labels each drawn column with its instant rounded to 0.1 s but prints the state at the column's exact instant, so early in a high-flow induction it pairs a value with an instant at which the model held a different displayed value, such as desflurane's circuit 2.70% shown at "6s" where the state at 6.0 s is 2.68%
- PL-TPBH (S) While the trunk-Reset question (or a Workspace question) is open, the run behind it keeps stepping at the selected rate, and the window-modal dialog blocks the Pause button, so at 300× a learner who reads the question for ten seconds watches fifty simulated minutes pass that they cannot stop
- PL-VHQX (S) A branch forked on, or reset onto, the 24 h supported run length shows the limit banner's "Reset to start a new run.", and `start()` says "reset it to start a new run", but Reset returns that branch to the same 24:00:00 fork, so the only way out the screen names leads straight back
- PL-WRVX (S) mac_awake_band_percent checks only that the band's lower edge is positive, so a negative standard deviation returns the band upper edge first, an infinite fraction returns (inf, inf), and a band reaching past 1 MAC is accepted, though its docstring promises lower first and a refusal of an undrawable band
- PL-X4X2 (S) The playback-rate line under the clock reads "300× real time" while the run is paused, reset or halted, but `docs/INTERFACE.md` § "Minimum displayed outputs" still defines that line as the rate at which simulated time is advancing, which contradicts § "Interface boundary"'s statement that the label states the setting
- PL-XV0D (S) A run's halt record, bookmark_halt, is filtered by instant when a mark is removed rather than re-derived from the current marks as the standings are since PL-1ZQ4, so a branch reset after a mark was removed and re-added names the removed mark and its old label, and a trunk halted on a mark loses "stopped on your mark" from its Branch here button once the same mark is removed and added back, although its row still reads passed
- PL-Y65Q (S) An Area too small for its View is held at a floor of header, rule, padding and one line, so its notice gets about 31 px: the body that states the size the View needs and the size the Area has gets 0 px of the 119-153 px it needs, and even the "Too small for ..." title gets 0 px
- PL-YDRT (S) docs/MODEL.md and the Katoh 1993 source notes for sevoflurane and isoflurane say Katoh measured the brain concentration at awakening directly, but the paper's own title says the cerebral concentration was predicted, so a modelled estimate is recorded as a tier 1 direct measurement
- PL-PTDZ (S) The washout figures in docs/INTERFACE.md § "MAC-awake as a chart reference" (2.86, 6.55 and 7.31 min crossings, 1.69% alveolar, 0.84 MAC after 3 hours) depend on the blood:gas and tissue coefficients, volumes, ventilation, cardiac output and the protocol, but no test pins them, so a parameter change leaves six figures in the specification stale with no check firing
- PL-000W (S) Which field holds a control's value is mapped twice: controller._control_value maps each ControlInput to an UptakeEquationSettings field, and dashboard_frame's flows dict maps three of them to the run's displayed settings, so a fifth control has to be added to both
- PL-D1LR (S) docs/MODEL.md lines 6057 and 6363 say the gas accumulators are displayed to six decimals of a litre (1e-6 L) and size the canonical-versus-display margin against that, but § on the agent-accounting panel (line 10154) says its amounts have shown 0.1 L since PL-TG60, so both margins are measured against a resolution the display no longer has (found by the PL-XK00 blind review, 2026-10-25)
- PL-SP6H (S) Check two docs/MODEL.md agent-amount precision claims against the figures they cite: 0.1 L is said to lie between a quarter of an SD and six SDs, but the quoted 0.016-0.23 L shifts give about 0.43 SD at the coarse end; and 0.1 mL of delivered liquid is said to lie inside the density's band, though at 8% and 10 L/min over 24 h one step is about a thirtieth of an SD
- PL-0P3F (M) The accounting panel's 0.1 L step for the agent totals is derived from partition-coefficient shifts measured only at 1 MAC with the reference flows; the model is linear in the dial, so at each agent's dial maximum and 10 L/min the 24 h shift is 3 to 4.6 times larger and one count of 0.1 L falls to about an eighth of an SD, at or past the seventh the section allows
- PL-GW0P (M) ROADMAP.md's v0.6.0 and v0.7.0 gate sections defer a debt item captured after the cut by its capture date, while the snapshot rule re-admits any finding whose problem was present at the freeze, however late it was filed
- PL-8C8W (S) ROADMAP.md says a safety or science finding cannot be deferred, while its deferral section lets a frozen safety or science entry be deferred when its hazard is not live, as PL-WZVZ was
- PL-1BVB (S) ROADMAP.md's planned-milestone catalogue still states six things other chapters contradict: item 8's unrecorded control changes, item 21's concentration history, item 1's open default flow and the three items waiting on it, and item 33's prerequisites and dark mode
- PL-392N (S) ROADMAP.md gives a 30-day case's control timeline as about 140 KiB against 3.16 GB in v0.4.0's section, and about 70 KiB at 50 changes a day in the v0.4.8 version row
- PL-4BCF (M) Restructure ROADMAP.md, slice 9: head v0.5.0's gate dispositions by the ground each was decided on
- PL-6LBQ (S) ROADMAP.md planned item 27 says fat holds a third of the agent at three hours, while v0.7.0's Goal table gives 30% at 180 min
- PL-9857 (S) ROADMAP.md's v0.6.0 section says Gate 2's frozen list has not yet been checked for stale entries, while the v0.5.1 version row says Gate 2's 168 clearable entries were swept
- PL-B6V1 (L) Restructure ROADMAP.md, slice 6: give each v0.6.0 decision one home in its Required scope, and gather v0.6.0's captures after the cut in one section
- PL-G6DP (M) Restructure ROADMAP.md, slice 4: move the toolchain policy to docs/maintainer.md, and the account of what the release tools read to the workflow documentation, keeping in the roadmap what each guarantees
- PL-H6T7 (S) ROADMAP.md uses apparatus, lane and generator (or generator head) throughout without saying what they mean, so a reader deciding a release cannot follow the rows that use them
- PL-HXJJ (S) ROADMAP.md's baseline and version rows test each patch against both halves, or one half, of § "Versioning decision"'s test, which names no halves
- PL-K6DG (S) ROADMAP.md's Beyond row orders items 1-5, 9-10 and 13-15 by § "Development pathway", which also orders items 24 and 20 and item 8's scenario events, and item 30 places itself in Phase 1 but is on no row
- PL-M3MV (L) Restructure ROADMAP.md, slice 7: keep each planned milestone to its intent and what remains, and move each shipped or scheduled record to its milestone section or item
- PL-S2LW (S) ROADMAP.md's baseline says v0.7.0 and v0.8.0 are given to milestone sections, but there is no v0.8.0 section, and § "The plan" lists only rows 5, 7, 9 and v0.4.26 as having sections
- PL-T5R7 (S) ROADMAP.md's v0.5.0 Required scope says PL-Y5WR makes the 30-day scenario cap an explicit halt, while the v0.4.7 version row says the cap became 24 h, enforced by the step count, before v0.5.0 shipped
- PL-TW3Q (S) ROADMAP.md's timeline gives v0.2.8 thirty-eight entries at Size 2 M, 35 S, which adds to 37, while its frozen list holds 2 M and 36 S
- PL-V8SJ (L) Restructure ROADMAP.md, slice 8: give each record of the milestones v0.1.0 to v0.5.0 one home in its own section, apart from v0.5.0's gate dispositions
- PL-W6VL (S) ROADMAP.md planned item 1 targets a new machine as one data file with no change to core/, while item 40 says that target cannot be reached, because a machine is one data file plus one provenance row per number
- PL-XRZW (S) ROADMAP.md's v0.4.26 section calls Gate 2's freeze an exception and a second instance, while § "The cadence" says the freeze trigger changed on 2026-10-03, so no exception remains, and that v0.4.26 was counted as a second exception in error
- PL-YNFS (M) Restructure ROADMAP.md, slice 5: restructure the v0.7.0 section, gather its captures after the cut in one section, and put the owner's test drive in its definition of done
- PL-501T (M) AreaLayout._fits, which stops a border drag and lights the WARNING line, still estimates each Area's drawn size as its window share minus one handle, not from the apportionment the splitters draw: the estimate ignores nested handles and overstates an Area whose split neighbour is held wider than its share, and two adapter tests pin the stop it gives, a handle's width short of the neighbour's need (found building PL-16BG)
- PL-J1ZM (M) Sessions write prose that over-explains, in every kind of text they write: each writing rule adds something a text must carry (a reason for each value, what changing it would do, the test that holds it, its provenance) and none says what the reader can do without, so docs, docstrings, the interface, item briefs, pull requests and replies each need rewrites, and each later change grows them again
- PL-3WFF (S) Review the 6 regular expressions in src/anesthesia_sim/ that tools/regex_baseline.py lets stand without a reason, and replace each one a parser or string method does better or write its reason beside it
- PL-8FT2 (L) Review the 340 regular expressions in tools/, .claude/hooks/, subprojects/docket/ and the tests that tools/regex_baseline.py lets stand without a reason, starting with the ones that read a format a module already parses
- PL-8W1Q (M) Every other frozen record in core/ that checks its fields in __post_init__ still restores from a pickle or a copy without running the check: a saved Keyframe with instant_s as a bare -50.0, a RunDefinition's slots and cache, BreathingCircuitState, SampledWindow, DeliverableFreshGasFlowRange, LiquidDensity and the parameter records all load unchecked, and nothing makes the next such record fail; the restore is also positional, so a record saved before a field reorder loads into the wrong fields (found at review of PL-S11T)
- PL-86VL (M) Two interface-wording tests in test_simulation_view.py pass any wording they do not list: the end-tidal check misses ET, Et, EtSevo and FET, and the emergence-time check finds a hedge only in the 12 characters before its phrase
- PL-8W1B (M) The Maintenance Workspace puts the schematic's 96 px containers beside the full-height concentration chart, so one tension stands at different screen heights in the two Views and a learner may read a fill level across against the chart's gridlines; align the containers to the plot's scale or caption them against that reading
- PL-LKX7 (S) docs/INTERFACE.md § "Displayed precision" says a maximized 1280 px screen opens the readout row on seven columns (measured 2026-09-27), but that predates the region's 0.82/0.18 split: at 1366 px the region's 1320 px leaves the readouts 1073 px, so a 1280 px screen's 1234 px likely leaves about 1000 px, below the 1005 px that seven across needs
- PL-TDX0 (M) docs/INTERFACE.md § "Displayed precision" gives the partition coefficients' measured SDs as 3.9% to 6.4% of the mean, which are Yasuda, Targ and Eger's brain:blood SDs, while the fat tissue:gas SDs the agent files record are 17% to 19%, so the section understates the fat fraction's uncertainty about 3.5 times and its one-SD displacement table may rest on the wrong SDs
- PL-19W8 (M) Hold docs/MODEL.md § "Known limitations" numeric paragraphs to named tests, write the tests § "Displayed precision" declares it owes, and count the claims found wrong (the first pass, which decides whether the rest run)
- PL-5C1H (M) Hold the numeric paragraphs in docs/MODEL.md's parameter and range sections (supported input ranges, delivery-limit and MAC parameters, source hierarchy, v0.2.0 agents) to named tests
- PL-5L84 (M) docs/MODEL.md states the 20 °C reference condition in 29 paragraphs with no marker tying them to core/liquid_agent.py REFERENCE_TEMPERATURE_CELSIUS, so the numeric-paragraph check cannot read °C as a unit until each is tied
- PL-H94Q (S) Hold the numeric paragraphs in docs/MODEL.md's model sections (selected method, alveolar gas, mass balance, agent amount, concentrations) to named tests
- PL-JP7P (M) Hold the numeric paragraphs in docs/MODEL.md's interface sections (hover readout, MAC-awake, MAC multiples, time base, control-input record and five smaller sections) to named tests
- PL-KG6S (S) docs/INTERFACE.md § "Displayed precision" bounds the last displayed digit at 'between about a seventh of one parameter SD and seven times it' and calls one SD 'one to seven counts', but its own table's fat tissue:gas row, 8.7e-4 to 6.7e-3 pp, is 0.09 to 0.67 counts, which puts the digit at 1.5 to 11.5 SDs; no row gives the 'seven times' end, so the bound should be restated from the table or limited to the rows it comes from (found by PL-J37P's blind review)
- PL-MCQ5 (M) Hold the numeric paragraphs in docs/MODEL.md's required-test sections (published wash-in and elimination, independent solution) to named tests
- PL-97S1 (S) Two citations name docs/MODEL.md's Known-limitations note 'One reference condition, where the model physically has two' without the section mark (core/liquid_agent.py:41 and ROADMAP.md:2759), so the doc check cannot see them, and the MODEL.md copy edit, which rewords that bold lead, would leave both pointing at nothing
- PL-G0R3 (M) docs/MODEL.md calls results of simulator runs 'measured' in at least twelve chapters, which a clinician can read as patient or instrument data; say 'simulated' or 'from a run' and keep 'measured' for real measurements (copy editor structure read, 2026-11-05)
- PL-GW26 (S) docs/INTERFACE.md § "MAC multiples as a display unit" has two wrong statements: the 1.39x rescale it gives for a desflurane against a sevoflurane wash-in is the isoflurane against desflurane figure (desflurane against sevoflurane is 4.00/3.00 = 1.33x), and "which a ceiling of 2 could not do" says a 2 x MAC ceiling would put the 1 MAC line on the frame, when it puts it at half height
- PL-HR4T (S) docs/MODEL.md § 'Intended use' lists extreme-preserving decimation as an interface safety feature, but § 'Interface boundary' says the chart evaluates the run at column instants and selects no recorded extremes; one is stale (copy editor structure read, 2026-11-05)
- PL-HVLD (S) docs/INTERFACE.md heading 'The run is that record, and every state is derived from it' says the run is the control-input record, while its rows describe the run definition and § 'The control-input timeline' treats the two as separate records (copy editor structure read, 2026-11-05)
- PL-G1J9 (S) docs/ARCHITECTURE.md § 'Layering' says app/ never performs a unit calculation, but § 'Data flow' and the package map say chart_frame.py, formatting.py and agent_cost.py convert units; one statement is wrong (copy editor structure read, 2026-11-05)
- PL-GSPR (S) docs/ARCHITECTURE.md's package map says blood.py, tissue.py and circuit.py advance their own amounts, but § 'Data flow' says one exact propagation advances the whole coupled system; the map may be stale (copy editor structure read, 2026-11-05)
- PL-HLTR (S) docs/ARCHITECTURE.md's startup diagram builds the system with AgentUptakeSystem.default(), but § 'Layering' and § 'Data flow' say for_agent() builds it from the data files; one is stale (copy editor structure read, 2026-11-05)
- PL-2WBR (S) docs/interface-provenance.md cites Blender's Copyright Rules handbook with no address or reading date, and the list of pages read leaves it out (copy editor structure read, 2026-11-05)
- PL-41CR (S) docs/interface-provenance.md says the blender.org hosts answered a probe on 2026-09-26, then says wm_window.cc was read through the GitHub mirror on 2026-09-27 because the Manual page was not reachable; which is right? (copy editor structure read, 2026-11-05)
- PL-68M1 (M) docs/interface-provenance.md § 'What the code cannot answer' draws four conclusions for this project (a named set of things that may float, the header staying visible, modes, no tablets) that the adopts-diverges-refuses list has no entry for: adopted, open, or only advice? (copy editor structure read, 2026-11-05)
- PL-GPTN (S) docs/interface-provenance.md's Prune entry still says this project's View contract 'should take the shape of Blender's' SpaceType (PL-TH35) and that the project 'should plan to prune such hooks and fields', but PL-TH35 is done: app/view_contract.py defines the View protocol and test_view_contract deletes any member with no call site, so the recommendation reads as open work that has shipped
- PL-QXYW (S) docs/interface-provenance.md says a reader can never be wrong about what context a displayed value belongs to, in two places, and neither names the document that sets the requirement (copy editor structure read, 2026-11-05)
- PL-Y9F0 (S) docs/interface-provenance.md says a View's chrome is the View's business and the Area only allocates the rectangle, but each Area has a header with the Area menu and the View chooser: does the View or the Area own the header? (copy editor structure read, 2026-11-05)
- PL-ZD8Y (S) docs/interface-provenance.md says Shift moves a border alone here, the reverse of Blender, only in the keyboard entry; the border-chain entry says nothing about Shift, and no divergence is recorded (copy editor structure read, 2026-11-05)
- PL-37N4 (L) docs/machine-abstraction.md: answer the close-out copy editor's queries (contradictions, unnamed items, missing citations)
- PL-8ZD7 (L) docs/machine-survey.md: answer the close-out copy editor's queries (contradictions and unstated reading depth)
- PL-5XRK (S) docs/references/yasuda-1991-figure-2-wash-in.md: neither Anesth Analg table has a 1.5-minute row, though the protocol sampled at 1.5 minutes and only the Anesthesiology figure is said to plot no point there; say why (copy editor structure read, 2026-11-07)
- PL-GZFR (M) docs/maintainer.md is addressed to the owner but instructs sessions in about a dozen places (owner-ask records, the Auto-merge trailer, worker-run review, the effort-trial reply); check each also stands where sessions read it, then leave here only what it guarantees the owner (copy editor structure read, 2026-11-07)
- PL-M8Z7 (S) docs/maintainer.md describes hooks acting in every session (effort trial, owner-ask guard, merge guard, stop hook patch), but its setup-script section says a Projects thread runs none of them until that script is added; say whether they act in a Projects thread today (copy editor structure read, 2026-11-07)
- PL-N8G4 (S) The chart's limit of 24 control marks (MAX_CHART_CONTROL_MARKS) and the change list's limit of 12 lines (MAX_LISTED_ADJUSTMENTS) carry no recorded reason: say why each is that number and what changing it would do
- PL-33FM (S) ROADMAP.md gives Gate 0's size as nine items, as twenty items deep and as 21 frozen entries
- PL-PNH2 (M) ROADMAP.md's timeline does not say what its Size column counts or as of when, whether rows 1 and 2, the v0.4.x track and Gate 3 have shipped or cleared, how v0.5.0's sixteen items square with its 20 ids and undated 185 entries, or what 'Row 11 is the intended order' covers
- PL-V82M (S) ROADMAP.md says the next release stamps a release's own cut pull request every time, but since PL-KRS6 a cut item ships in no release, and the version rows that stated that rule are now one sentence each
- PL-71H3 (M) Answer the questions the structure read of ROADMAP.md's v0.7.0 section left for its author: which choices the owner made, what the Goal table's figures date from, and the terms the section never defines
- PL-KYGF (M) Answer the questions the structure read of ROADMAP.md's v0.6.0 section left for its author: what 'the gate decision' was, which entry decides an Area refused a size, and the definition of done's baseline
- PL-0YR1 (S) docs/MODEL.md § MAC-awake as a chart reference says the three fractions 'sit in a narrow range, so each agent carries its own value', but a narrow range argues for one shared fraction; the stated reason does not support the choice
- PL-32QH (S) docs/MODEL.md § 'Status' calls the simulator not a medical device, while § 'Intended use' says the safety class settles no device status and the section claims no regulatory status; decide which claim stands (copy editor structure read, 2026-11-05)
- PL-3807 (S) docs/MODEL.md § 'What the published-data gate can and cannot resolve' counts the sign of the elimination disagreement as part of the published-data gate, but § 'Release gate' says the elimination comparison is not part of the release check; decide which elimination checks a release must pass (copy editor structure read, 2026-11-05)
- PL-4BGX (S) docs/MODEL.md's paragraph on the two classes of vaporizer is unclear and uses its own terms: it never says the maxima are dial maxima or how the classes differ, and states the altitude difference more firmly than a source the project can cite
- PL-52KB (S) docs/MODEL.md has five broken section pointers: Desflurane's residual sends the reader to a sensitivity run 'under Parameter provenance' (it is in 'What the published-data gate can and cannot resolve'); Known limitations says the Yasuda citation is in 'Parameter provenance'; two pointers name headings that do not exist ('The chart's vertical range is denominated in MAC, and fixed', 'Why the axis is fixed rather than fitted'); 'Mass-balance test' cites 'the release tolerances documented above' with no section (copy editor structure read, 2026-11-05)
- PL-8RFG (S) docs/MODEL.md uses 'gate' for four different checks (step-refinement, independent-solution, published-data and release), so a clinician cannot tell them apart; give each its own name (copy editor structure read, 2026-11-05)
- PL-DPY1 (S) docs/MODEL.md says the main window cannot be closed while another window is open, then that closing it closes the others; a reader cannot tell which is the requirement for break-out windows
- PL-DQD8 (S) docs/MODEL.md's paragraph saying 'always' does not mean the disclaimer is in view on every screen today is stale since PL-NNML fixed the scrolling page, and it points to a gap the paragraphs above no longer state
- PL-FRRQ (S) The Yasuda notes in the three agent data files judge the stored tissue:gas coefficients by whether a measured value rounds to them ("rounding to the stored precision explains only two", "2.04 does not round to"); the project owner said on 2026-11-09 'I wouldn't round coefficients', and MODEL.md now gives each difference as a percentage, so the notes should say the same
- PL-2BG1 (S) MODEL.md calls each stored MAC '1 MAC for a 40-year-old adult' (Delivery-limit and MAC parameters, and three provenance table rows), but its adopted source, De Wolf et al. 2012, gives a flat adult MAC with no age, and the same section's table shows the stored values 2.6% to 11.1% off Mapleson's age-40 figures
- PL-11Z9 (S) The agent cost View does not say on its face that its figures are modelled: 'Liquid used by the vaporizer' can read as a measured volume, and v0.7.0's definition of done asks the modelled label only of the schematic
- PL-FCYQ (M) No test replays a recorded control-input timeline into a fresh run and compares the two, though docs/MODEL.md § The control-input timeline requires that the replay reproduces the run
- PL-BLN0 (L) Sentences in docs/MODEL.md, docs/ARCHITECTURE.md and docs/interface-provenance.md that restate how the code or the interface behaves go stale when the code changes, because nothing ties a free-prose sentence to the code it describes

### Captures after the cut

An open debt item captured after the cut joins the frozen list when § "Which
findings re-enter the gate" says it re-enters: its problem was present at the
freeze, or it falls under one of that section's exceptions (`PL-GW0P`). The
open part of a frozen entry stays on the list rather than leaving it. A
capture that an entry waits on is either let onto the list beside that entry,
or the entry is deferred with it (`PL-D388`). Each deferred item records
`deferred-from: v0.7.0 - <why>`. The triage pass that classes the item writes
that field.

`PL-QX2G` and `PL-YT3T` (`safety`, 2026-10-25) re-entered after the cut. Both
were split from the generator head `PL-58D7` when its design round chose to
give each core input a declared numerical envelope. `PL-QX2G` bounds the
volumes and partition coefficients, and `PL-YT3T` bounds a compartment's own
step. The head and its two other members, `PL-06LS` and `PL-XST1`, are not
`safety` and are deferred.

`PL-J5GC` (`safety`, 2026-10-26) re-entered after the cut. It is the generator
head that `PL-R4Y2`'s defect review recorded on 2026-10-25, over `PL-6RJ0`,
`PL-3B34` and `PL-HF4B`. Its guard requires values shown together on the run
screen to come from one state, and each member is a `safety` entry already on
the frozen list.

**`PL-P319` joined the frozen list on 2026-10-26, after the freeze, beside
`PL-GCGX`.** `PL-GCGX` closed on #1863 with all of its work done except
naming the base MAC that Katoh 1993 measured its sevoflurane and isoflurane
fractions against. That part needs the full paper, which no session can
fetch, and it moved to `PL-P319`. Deferring it instead would need its hazard
to be not live, and it is live: nobody can yet check how far those two bands
sit from the source. So the remainder stays on the list, and this gate waits
on the project owner adding the paper to the reference corpus.

**`PL-4LS8` joined the frozen list on 2026-10-31, after the freeze.** It held
the one question that `PL-5B1N`'s build left open: whether a preview curve may
draw at 1 px. `PL-4LS8` closed the same day with the 2 px floor kept.

**Six captures joined the frozen list on 2026-10-31, after the freeze.** They
are `PL-9B1M`, `PL-D88N`, `PL-QVBR`, `PL-PTDZ`, `PL-000W` and `PL-D1LR`, each
classed `safety` or `science`. The rule at the head of this section admitted
such a capture rather than deferring it. `PL-R4Y2`'s triage placed them, and
deferred the other two captures it triaged, `PL-9Z74` and `PL-93LV`.

**`PL-SP6H` joined the frozen list on 2026-11-04, after the freeze.** It is
classed `safety`. The agent cost View showed the delivered total in millilitres
of liquid to 0.1 mL, and in long runs at a high delivered concentration that
step was finer than the figure's uncertainty supports. The hazard was live, so
the rule at the head of this section admitted the item rather than deferring
it. Its fix is whole millilitres, which the project owner chose on 2026-11-04.

**`PL-0P3F` joined the frozen list on 2026-11-04, after the freeze.** It is
classed `science`. A blind review of `PL-SP6H` found that the accounting
panel's 0.1 L step rests on shifts measured only at 1 MAC with the reference
flows. At each agent's dial maximum and 10 L/min, one count of 0.1 L falls to
about an eighth of an SD by 24 h, at the fine end of the band the section
allows. The panel shows that step at every setting, so the gap is live and the
item is admitted rather than deferred.

**36 captures joined the frozen list on 2026-11-07, after the freeze**
(`PL-GW0P`). 34 of them had been deferred because they were filed after the
freeze, and `PL-GW0P` and `PL-8C8W` had not yet been triaged. The project owner
ruled that a capture joins when the problem it describes was already present at
the freeze, as § "Which findings re-enter the gate" says. Each item's brief
records what the check against `817a4d88` found. `PL-GW0P` and `PL-8C8W` closed
the same day. Eight of the 36 stay deferred to the next gate on the terms of
§ "Deferring to the next gate", and each item's `deferred-from:` says why.
`PL-J1ZM` waits on four untriaged findings that no release schedules.
`PL-19W8`, `PL-5C1H`, `PL-5L84`, `PL-H94Q`, `PL-JP7P`, `PL-MCQ5` and `PL-86VL`
are classed `safety` or `science`, and the check found that no learner can see
a wrong value now (`PL-8C8W`). `PL-8W1B`, `PL-TDX0` and `PL-KG6S` are also
classed `safety` or `science` and are not deferred. A learner can misread a
tension from `PL-8W1B`'s containers today. The fat and muscle tissue:gas SDs
that the agent files store are far wider than the SDs `PL-TDX0` says the
section's table used, so a displayed digit may be finer than its uncertainty,
and `PL-KG6S`'s ratios are taken from that table. Seven other captures stay
deferred, because their problems began after the freeze: `PL-8G3F`, `PL-K4MQ`,
`PL-JTTD`, `PL-7R8S`, `PL-LPV0`, `PL-Z6FR` and `PL-HXF0`.

**40 captures joined the frozen list on 2026-11-09, after the freeze.** The
triage pass that day checked each one against `817a4d88`, and each brief
records what it found. For 38 of them the problem was already present at the
freeze, so they re-enter as § "Which findings re-enter the gate" says. They are
`PL-97S1`, `PL-G0R3`, `PL-GW26`, `PL-HR4T`, `PL-HVLD`, `PL-G1J9`, `PL-GSPR`,
`PL-HLTR`, `PL-2WBR`, `PL-41CR`, `PL-68M1`, `PL-GPTN`, `PL-QXYW`, `PL-Y9F0`,
`PL-ZD8Y`, `PL-37N4`, `PL-8ZD7`, `PL-5XRK`, `PL-GZFR`, `PL-M8Z7`, `PL-N8G4`,
`PL-33FM`, `PL-PNH2`, `PL-V82M`, `PL-71H3`, `PL-KYGF`, `PL-0YR1`, `PL-32QH`,
`PL-3807`, `PL-4BGX`, `PL-52KB`, `PL-8RFG`, `PL-DPY1`, `PL-DQD8`, `PL-FRRQ`,
`PL-2BG1`, `PL-FCYQ` and `PL-BLN0`. `PL-71H3` and `PL-KYGF` hold questions
for the project owner, and they count as debt while they wait at
`needs-decision`. The same pass filed `PL-BLN0`, the generator head for
document sentences that restate the code and go stale. It completes entries
already on the list, such as `PL-G1J9` and `PL-HR4T`.

The other two captures are `PL-11Z9` and `PL-RJN9`, new problems in the agent
cost View, which arrived on 2026-11-02, after the freeze. Both are classed
`safety`, so they re-enter whether or not their problem was present.
`PL-11Z9`'s hazard is live: the View does not say that its figures are
modelled, so a learner can take them for measurements today.

`PL-FCYQ` stays on the list but is deferred to the next gate, on the terms of
§ "Deferring to the next gate". The triage pass found that its hazard is not
live, so no learner can see a wrong value now. `PL-RJN9` was deferred on the
same terms until 2026-11-10.

**`PL-HQPF` joined the frozen list on 2026-11-10, after the freeze, and this
milestone clears it together with `PL-RJN9`.** A review of earlier fixes found
that the accounting panel and the schematic show agent amounts without the
condition they are stated at, 20 °C and 1 atm. The accounting panel's caption
was already in the tree at `817a4d88`, so the problem was present at the
freeze. The project owner chose to put both items in this milestone (project
owner, 2026-11-10, ratified, over deferring them to the next gate). Required
scope entry 13 names both, so they are in the first group, and `PL-RJN9` is
no longer deferred.

### Required scope

#### The compartment schematic

1. **The specification, before anything is drawn** (queue item `PL-2881`).
   `docs/INTERFACE.md` gains a subsection under § "Minimum displayed outputs".

   - The subsection says what the schematic asserts and what it does not. A
     fill height is the compartment's modelled tension, on the same scale for
     every container of one run. An amount is the compartment's modelled
     agent, in the unit § "Agent amount" defines. The amount is named as
     vapour, so that nobody reads it as liquid.
   - The subsection sets, once for the whole interface, how a vapour amount
     and a liquid-equivalent amount name their units. The schematic labels its
     amounts in millilitres of vapour. The agent cost View gives millilitres
     of liquid equivalent. About 183 mL of sevoflurane vapour come from 1 mL
     of liquid (§ "Agent amount"), so neither may show a bare "mL".
   - The subsection says what the share bar shows: each compartment's amount
     as a share of all the agent the run holds, circuit included.
   - The subsection derives the displayed precision of a per-compartment
     amount in § "Displayed precision". That precision does not come from the
     run totals' entry in `AGENT_AMOUNT_DISPLAY_PRECISION`, which was derived
     for the three totals. At that entry's resolution of 0.1 L, venous blood
     and the alveoli read 0.0 L for a whole hour at 1 MAC.
   - The subsection adds two rows to the hazard table in
     § "Reasonably foreseeable misuse, and the hazards the presentation carries".
     One row is for a height read as an amount. The other is for a vapour
     amount read as liquid.
   - The subsection also records why no container is drawn for arterial
     blood. This model gives arterial blood no amount of its own, because
     $`F_a \equiv F_A`$ (§ "Blood compartments"). A container drawn for
     arterial blood would show agent that the model does not hold.

2. **Each compartment's amount passed to the display** (queue item `PL-KFTM`).
   The snapshot that the display reads (`SimulationSnapshot`) carries the six
   compartments' amounts beside their tensions. Each amount is read from that
   compartment in the scientific core (`agent_amount_l` in `core/`). The
   amounts travel as one record per compartment rather than as six more flat
   floats, so that the substance generalization can key the same record by
   substance instead of adding fields. The build kept the core's one sum of the
   amounts (`stored_agent_l`), because summing the record again in the
   interface code (`app/`) would have computed the same fact twice (`PL-KFTM`,
   2026-11-01). A test checks that the record's amounts match that sum to the
   last bit. No equation changes: the core already computes every amount, and
   this item only passes them on. A test compares each amount at stated
   instants with an independent reference that does not use the core, as
   `.claude/rules/test-oracles.md` requires.

3. **The schematic View** (queue item `PL-RNYV`). The schematic is one
   registered View kind. It is built against the View contract
   (`src/anesthesia_sim/app/view_contract.py`) like every other View. So any
   Area can hold it, and compare mode draws one schematic per displayed run. The
   View draws the circuit, the alveoli, venous blood and the vessel-rich
   group, muscle and fat as containers. The containers appear in the order in
   which agent reaches them, joined as the circulation joins them. Each
   container fills to its tension and is labelled with its name, its tension
   and its amount. The View shows the run's current instant, as the readouts
   do. It redraws on every frame on which the readouts redraw, so it never
   shows a state the run has left. It declares the smallest size at which it
   can be read. Its colours are the chart's compartment trace colours
   (`app/theme.py`), so each compartment means the same thing on the chart and
   here.

4. **The share bar** (queue item `PL-S79P`). The schematic has one bar,
   divided by compartment. Each segment is as long as that compartment's share
   of all the agent the run holds, and each segment is named in text.
   Containers that fill to tension show fat nearly empty, although at one hour
   fat holds a fifth of the stored agent. Position on a common scale is read
   more accurately than area (Cleveland WS, McGill R, *J Am Stat Assoc*
   1984;79(387):531-554, https://doi.org/10.1080/01621459.1984.10478080). So
   the bar carries the amount. In this model, containers drawn to scale cannot
   carry it.

5. **A shipped Workspace that places the schematic** (queue item `PL-PR1W`).
   The schematic is already reachable from every Workspace through the View
   chooser. One shipped Workspace places it beside the concentration chart.
   A learner then meets tension over time and where the agent is now side by
   side, without having to build that layout first. Which Workspace places it
   is a placeholder decision.

#### Agent cost, in liquid and in money

6. **The constants a liquid figure is derived from** (queue item `PL-KZ99`).
   The agent's parameter file stores each agent's molar mass. It also stores
   the agent's liquid density, with the temperature at which the density was
   measured and the source of the density. The vapour-to-liquid factor is
   derived from these values in one place. It is checked against Biro's and
   Gas Man's published constants.

7. **A displayed precision for each quantity and unit** (queue item `PL-0S0V`).
   `docs/INTERFACE.md` § "Displayed precision" derives a precision for each
   quantity and each unit. The reason is that a unit the reader chooses makes
   precision depend on both.
8. **The agent cost View** (queue item `PL-B396`). The agent cost View is a
   View of its own, which any Area can hold. By default it shows the delivered
   agent in millilitres of liquid equivalent. If the reader chooses, it shows
   litres of vapour instead. Either way, the unit is named on the value. The
   basis is the delivered agent, not the exhausted agent, as item 28 records
   (`PL-H4N8`). The agent accounting View keeps litres of vapour, because it
   is a check that the model conserves mass.

9. **What a stored price records, and what a cost readout shows beside the cost**
   (queue item `PL-VJZK`). `docs/INTERFACE.md` § "A cost at the reader's price"
   states what a stored price carries, including its currency and the date on
   which it applied. It also states what a cost readout shows beside the cost:
   the modelled liquid volume that the cost multiplies, the price it used, and
   words saying that the price is the reader's rather than an authoritative
   figure.

10. **A preferences file** (queue item `PL-93B3`). The price and the cost
    View's unit belong to the reader, not to a layout. So they are kept in a
    versioned preferences file separate from the Workspaces, as `PL-MQHN`
    decided.

11. **The cost in money** (queue item `PL-1P15`). The agent cost View shows
    the delivered agent's cost at a price per agent that the reader sets. The
    project ships no price, because a shipped price goes stale and differs by
    institution. When no price is set, the View says so instead of showing a
    cost.

#### The copy editor

12. **Fix the copy editor, then make the five `docs/MODEL.md` rewrites that
    wait on it** (queue items `PL-HGZS`, `PL-HRPK`, `PL-PS5H`, `PL-XBJ3`,
    `PL-XT53` and `PL-YVL0`). The project owner added this to v0.7.0 (project
    owner, 2026-11-04). The copy editor is the review that every rewrite of
    `docs/MODEL.md` passes through. It keeps text that its reader does not
    need, and lengthens some of it. The copy editor is fixed and
    stress-tested first. Then the five `docs/MODEL.md` rewrites it blocks are
    made, so that the sections a learner reads beside the schematic, the agent
    cost View and the other displays are written for a clinician.

#### The condition an agent amount is stated at

13. **Every agent amount on screen names the condition it is stated at**
    (queue items `PL-HQPF` and `PL-RJN9`). The project owner added this to
    v0.7.0 (project owner, 2026-11-10, ratified, over deferring both items to
    the next gate). An agent amount is a volume of vapour, and the model
    states every amount at 20 °C and 1 atm. The accounting panel's unit
    caption, the schematic's amount unit and the agent cost View's two
    captions each name that temperature and pressure. Each label takes the
    two values from the constants that the conversion from vapour to liquid
    uses, so that a label cannot name a condition the figure was not computed
    at. The body's stores
    are not converted to 37 °C for display (project owner, 2026-11-10,
    ratified, over converting them). The accounting panel sums the delivered,
    exhausted and stored amounts, and they add up only when all three are
    stated at one condition. `docs/MODEL.md` § "Known limitations" already
    says that the 20 °C label overstates the alveolar, venous and tissue
    stores by 5.8%, because they are held at body temperature.

### Definition of done

**The compartment schematic**

- A learner can put the compartment schematic in any Area from its View
  chooser, in every Workspace, and one shipped Workspace places it.
- For each displayed run, the schematic shows the circuit, the alveoli,
  venous blood and the three tissue groups in the order agent reaches them.
  It draws no container for arterial blood.
- Each container fills to that compartment's modelled tension, on one scale
  for every container of the run. Each is labelled with its tension and its
  amount, and the amount is named as vapour.
- A bar shows each compartment's share of the agent the run holds. Each
  segment is named in text, and the shares add up to the whole.
- The schematic says on its face that its values are modelled. Its amounts are
  given at the precision that `docs/INTERFACE.md` § "Displayed precision" derives
  for them.
- `tools/contrast_check.py` covers every colour the schematic draws. Each
  container is named in text, so no compartment is told apart by colour alone.
- Every number the schematic shows is the number the rest of the interface
  gives for the same run at the same instant. A test asserts that each tension
  equals the readout's, and that the amounts add up to the agent accounting
  View's stored total.
- An end-to-end test runs patient inputs through the model to the drawn
  labels. It compares each amount at stated instants with an oracle
  independent of `core/`.
- The schematic never shows a state the run has left. A test drives a reset,
  an agent change, a branch, a return to a mark, and compare mode on and off.
  After each one, it checks that every label matches the snapshot.

**The agent cost View**

- A learner can place the agent cost View in any Area. They can read the
  delivered agent in millilitres of liquid equivalent or in litres of vapour,
  with the unit named on the value. Once they set a price, the View shows the
  cost with the price's currency and date.
- An end-to-end test checks the liquid figure against an independently
  computed conversion. It checks the cost against that figure times the price.
- The price and the unit survive a restart, in a preferences file separate
  from every Workspace.

**The condition an agent amount is stated at**

- Every agent amount on the accounting panel, the schematic and the agent
  cost View names 20 °C and 1 atm with its unit. A test asserts that each
  label states the values of the constants that the conversion from vapour to
  liquid uses.

**The copy editor**

- The copy editor cuts text that its reader does not need and keeps good
  text as it is, as `PL-HGZS`'s stress test judges. The five `docs/MODEL.md`
  rewrites that waited on it have merged.

**The whole release**

- Nothing a learner could do on v0.6.0 is lost, checked against v0.6.0's own
  definition of done.
- `make check` is green, and `docs/MODEL.md`, `docs/ARCHITECTURE.md` and
  `README.md` describe the interface that exists.
- v0.7.0 is cut only after the project owner has test-driven `main`.

### Explicitly out of scope for v0.7.0

- **Any change to the governing equations or parameters.** The model already
  computes every amount that the schematic draws. The only change under
  `src/anesthesia_sim/data/` is the two constants per agent that Required
  scope entry 6 stores. Only the agent cost View reads them.
- **The View catalogue** - planned-milestone item 36. This milestone adds the
  schematic View and the agent cost View. It does not decide which of today's
  surfaces become Views.

#### The schematic View

- **Controls on the schematic - not yet, rather than never.** Gas Man lets the
  reader set the vaporizer, fresh gas flow, ventilation and cardiac output
  from the Picture itself. Here the settings stay in the
  parameter controls View, so for now each setting has one control. A control
  on the schematic would be a second way to change the same setting, and that
  needs its own design round.
- **Liquid injection and the circuit flush.** Gas Man draws a button for each
  of them on its Picture. Each one is a new input to the model, not a display.
  Planned-milestone item 4 is direct injection.
- **The flows drawn as gauges.** Gas Man's lower half draws fresh gas flow,
  alveolar ventilation and cardiac output as bars. The parameter controls
  View already states all three. Drawing them a second time belongs with the
  controls above.
- **Containers drawn to scale.** The measurement in § "v0.7.0 - the schematic"
  shows that four of the six containers are between 1 and 7 px wide in a 600 px
  View. A filled area therefore cannot show the amount here. The share bar
  shows the amount instead.
- **More than one agent on one schematic.** Gas Man keeps one Picture for each
  agent. This model holds one substance at a time until the substance
  generalization, which is on no release yet (§ "The timeline", Beyond row).
  That work will key the per-compartment record by substance.
- **Showing a past instant.** The schematic shows the current instant of the
  run, as the readouts do. Drawing it at an instant picked on the chart first
  needs a way to scrub through a run, and no release schedules one.
- **The visual pass** - planned-milestone item 33, on the `v0.6.x` track.
  Until then, the schematic's look is a placeholder.

#### The agent cost View

- **A shipped price, or a price list.** A price goes stale, and it differs
  from one institution to another. So the reader sets it, as Required scope
  entry 11 says.
- **Carbon dioxide equivalent.** The unit decision behind entry 8 lists it as
  a candidate unit with the same shape as money. Like money, it needs a stored
  factor for each agent, from a source that can go stale. No source has been
  read for it, and it waits for a decision of its own.
- **Uptake as a headline figure.** Gas Man pairs Uptake with Delivered.
  `PL-DWHV` records that this model computes uptake but does not show it
  anywhere. Showing it is a display of its own, not part of the cost.
- **The rest of a preferences workflow.** Required scope entry 10 builds the
  file and what this milestone stores in it. Save, Revert and Load Factory
  Preferences (`PL-GL5X`) are not part of this milestone.

## Development pathway

The numbered items below are the catalogue. This section gives the intended
order for the part of the catalogue that § "The timeline" has not yet placed,
and the reasons for that order. Where the two disagree, the timeline's order
governs (§ "The planning model: a rolling wave"). Phases are groupings of
intent, not scoped milestones. Each item still has to be specified
individually before implementation, as the development rules above require.

The organizing goal is a mature inhalational simulator before any intravenous
work begins. The phases were written as the steps toward that goal: the
science first, then an interface that can actually drive it, then
reproducibility, then IV. Since 2026-08-25, the timeline has taken interface
and comparison work ahead of the science.

**Reordering (project owner, 2026-08-25): the teachable case is taken ahead
of Phase 1.** `PL-5XG1` quotes the record of that decision and its reasoning.

### The known risk

The known risk of the phases as written is that Phase 1 front-loads the hardest
work in the plan. Coupled-gas equations with reference cases are real
scientific work, and they are the most likely place for the project to stall.
That risk is accepted deliberately, because every milestone built before the
substance generalization is code written against the single-agent assumption,
and would have to be revisited afterwards.

The rework that the 2026-08-25 reordering accepts is bounded and known. The
view reads an immutable snapshot (`SimulationSnapshot`), so the time base,
playback, event marks and axis handling are substance-agnostic. The piece that
changes is the MAC readout, which becomes a MAC sum when a second substance
lands. The project owner accepted the risk for every release the timeline
names, and took the generalization off the timeline until a single agent works
well with its workspaces (project owner, 2026-09-26). § "The timeline"'s Beyond
row carries that condition.

### Phase 0 — foundation

Superseded by the standing debt gate, 2026-08-25. Its closing conditions, and
why the debt gate replaced it, are in § "Phase 0, which the debt gate
replaced".

### Phase 1 — scientific maturity

Item 30 (patient factors) comes first, ahead of the substance generalization
(project owner, 2026-09-02), for the reason that item 30's entry gives. Next
comes the substance generalization, which extends the patient's state from
one agent to N substances that are present at the same time. Then come items
6 and 7 (nitrous oxide, concentration and second-gas effects), then item 1
(machine abstraction with interlocks), then item 2 (agent switching with
residual washout). § "The timeline" places none of this phase, and its Beyond
row says when the generalization returns to the timeline. Item 40, the
machine-profile framework, is **not** part of this phase, because nothing in a
config file needs the substance generalization.

The generalization is the first half of item 6, and it comes before nitrous
oxide itself, item 7 and item 2, because those three need the same thing: holding more than one substance at once, with kinetics
for each substance. Agent switching needs the residual of the old agent while
the new one washes in. Nitrous oxide needs a second gas throughout. The
second-gas effect needs the coupling between the two gases. Doing the
generalization once, and deliberately, makes it one design decision instead
of three special cases. The second-gas effect is also the phenomenon that this
class of simulator is most used to teach. Without it, there is no credible
inhalational simulator to build an interface on.

The generalization settles the intravenous question without a speculative
abstraction. "A substance with compartmental kinetics and an effect site" is
also the shape that an intravenous agent needs, so intravenous support becomes
an extension rather than a rewrite. This works only if the generalization is
designed as substances, not as "volatile agent, plus nitrous oxide as a special
case". Designing it as substances is a requirement of this phase.

### Phase 2 — an interface that can drive the machine

First comes item 24 (the preferences panel), then items 5, 3 and 4
(end-tidal control, override mode, direct injection), then item 8's scenario
events and item 20 (accessibility).

The rest of this phase has shipped. The display
constants that item 24 first named as its prerequisite were gathered into
one module in v0.4.11 (`PL-2CS8`). Item 24's prerequisite is now a settings
store that can be written and saved, which its entry scopes. Item 25 (playback
speed) shipped in v0.4.0, and item 26 (run bookmarks) shipped in v0.5.0. Item
8's control-input timeline shipped in halves: recording in v0.4.0, and the
replay driver in v0.5.0.

### Phase 3 — reproducibility and comparison

Items 9 and 10 come in that order (save/load, then deterministic replay),
built on top of item 8's control-input timeline. Phase 3 cannot start without
that timeline, because save/load, replay and forking each restore from it.
Items 11 and 12 (side-by-side comparison, forking) shipped in v0.5.0 ahead of
both. v0.5.0 takes items 26, 12 and 11, with only the *replay driver* half of
item 8. It puts save/load (item 9) and a user-facing replay control (item 10)
out of scope. That is a deliberate departure from this phase's sequence of 9,
10, 11, 12. That sequence no longer applies to these four items.

This phase is also groundwork, which is why it comes before intravenous work
rather than after it. Save/load and forking both force the whole simulation
state to be explicit and copyable. Working features enforce that discipline,
not good intentions. That makes a more reliable foundation for adding
a drug subsystem than any abstraction designed before such a subsystem exists.

### Phase 4 — intravenous agents

Items 13, 14 and 15 (intravenous pharmacokinetics and effect site,
hypnosis/eBIS, nociceptive response).

### Alongside, as opportunity allows

Items 21 and 22 (performance, documentation) are continuous rather than
phased. Items 16 to 19 (renal/hepatic dysfunction, cardiopulmonary bypass,
ECMO, species profiles) and item 23 (packaging and distribution) are
deliberately later. Each is an extension of a mature model rather than a step
toward one.

## Planned milestones

This section is the catalogue of intent. § "The timeline" gives the order of
the releases that it names, and § "Development pathway" above gives the order
intended after them. Each item is left without a goal, required scope or
definition of done until it is promoted into a scoped milestone, though an
item may record its intent and the properties it must have.
§ "The planning model: a rolling wave" says what a scoped milestone carries.
A row's version number is provisional until its milestone is scoped, and the
number is assigned then.

Each item is kept to one improvement, so that scoping one item does not
implicitly drag others along with it. Items 37 and 43 each span the scientific
core and the interface or tooling, because the one improvement each delivers
needs both. The other items keep the two apart. Where one item depends on
another, the dependency is noted inline rather than bundled into one item, as
with items 2-5 on item 1, 7 on 6, 10 on 9 and 13 on 12.

An earlier item 1 (isoflurane and desflurane) was promoted into a fully scoped
milestone and delivered as v0.2.0 (§ "Completed: v0.2.0" below), so it no
longer appears here.

Volatile agents beyond isoflurane and desflurane remain an unscoped later idea:
halothane, enflurane, ether and xenon. Nitrous oxide is not among them, because
items 6-7 below cover it. Halothane is clinically obsolete, but it has
reasonable modern published data. Enflurane, ether and xenon are harder to
source, because their data are sparser. Each of these three should get its own
provenance check before it is added. None of the three should be assumed
available just because the Gas Man reference simulator shows it. The idea will
be added back here as its own item once someone is ready to scope it.

### Machines and agents (items 1-7)

#### 1. Modular anesthesia-machine abstraction with interlocks

Add a modular anesthesia-machine abstraction with normal
single-halogenated-agent interlock behavior. This is the safety baseline
that every later machine feature below builds on. What remains here is the
interlock baseline, and the machine behaviors that need the solver work
that item 40 explicitly defers.

**Split 2026-09-20 (project owner).**
*The framework half is item 40, and it is not gated behind Phase 1.*
This item was written with the goal that a real commercial machine is
added as a data file. That goal moved to item 40, which delivers it. The
interlocks are what put this item in Phase 1. Interlock behavior needs to
know which agents are mounted and what a machine forbids, so it needs the
machine profile. A single-halogenated-agent interlock is a statement about
holding more than one agent, so it comes after item 6.

**The default fresh gas flow is no longer this item's to place.**
`docs/machine-abstraction.md` places the default (4.0 L/min) among a run's
opening conditions rather than among a machine's specifications. The reason
is that no surveyed machine publishes a startup flow, so a per-machine field
would force every profile to invent one. The default's value is decided:
the project owner ruled on 2026-09-20 that 4.0 L/min stays (ratified, over
lowering it to match low-flow practice). The wording that justified it was
corrected in v0.4.33 (`PL-NM7X`).

**The survey is done and is `docs/machine-survey.md`.** It examined the
machines in current clinical use for the variables that change a
simulated result (`PL-4DCG`). It records which variables affect a number,
which of them are per-machine data and which are genuinely different
behavior, and what remains unknown. Two of its findings bear on how this
milestone is scoped rather than on how it is built:

1. Apparatus volume alone does not account for the measured differences
   between machines, so a profile that is a volume and a set of bounds is
   already falsified.
2. The position of the fresh gas inlet changes the inspired/delivered
   ratio at a fixed volume. A single well-mixed circuit compartment cannot
   represent that effect, so this milestone has to choose, on the record,
   among three options. It can represent internal topology, state that
   machines differing only in topology are indistinguishable here, or
   route the question into the per-compartment gas-phase model at item 39.

**The design is done and is `docs/machine-abstraction.md`.** It sets out
the base abstraction (`PL-FG9D`): what a module is, what the base type
owns and what each machine supplies, and where the line between parameter
and strategy falls. Four of its results bear on scoping this milestone:

1. **The seam already exists in the tree**, and item 40 states it. The
   reference machine's strategies reproduce today's matrix entry for
   entry, so the abstraction lands with no change to any computed value.
2. **The set of machine behaviors is closed by two properties of the
   existing solver**, rather than by taste. A strategy must be constant
   across a step, and it must keep the matrix Metzler. That is why item 5
   (automated end-tidal control) is a milestone and not a slot.
3. **The inlet-position question above is answered.** The design declines
   to represent internal topology, and requires that this be said where a
   machine is chosen. It refuses outright to fold topology into an
   effective volume. It names two conditions that reverse the decline:
   item 39 landing a gas-phase model for each compartment, or any
   multi-limb circuit entering the model.
4. **What a machine may be called is decided** (project owner, 2026-09-20,
   ratified, over naming the machine by its trade name in the running
   interface). An archetype label appears wherever a machine is running or
   chosen. The trade name is confined to the panel that holds that
   machine's parameter set, its sources and its list of what is not
   modelled (`not_modelled`). This naming rule is a scope constraint, not a
   preference.
   It applies to every surface that names a machine, whichever item builds
   it, including the comparison surface (`PL-WZVZ`). The trade name is
   admissible only where what the model does *not* claim about that
   machine is on screen beside it.

Scoping this milestone therefore starts from the design. The milestone's
scope statement is judged against the design's stated cost target. A
machine whose delivery and removal are already in the closed set is one
data file under `src/anesthesia_sim/data/machines/`, plus one provenance
row in `docs/MODEL.md` for each number in that file. It needs no change to
`core/` and no new test of the physics.

**The survey and then the design scoped this item.**
The design depended on the survey, because the extension points are the
axes of real variation that affect a number. Designing them first would
have been guessing. Three items waited behind those two. Two closed in
v0.4.34: making the fresh gas flow range a machine property (`PL-8PS6`),
and making the Tec 6 the concrete second device class, which the design's
dial-mapping slot answered (`PL-439V`). The third, `PL-WZVZ`, is the
surface that keeps a machine's effect on a curve attributable to a named
parameter. It is still open, and it waits on four other items: `PL-TH35`,
`PL-R1WQ`, `PL-TBMK` and `PL-4TWW`.

#### 2. Agent switching with residual washout

Add agent switching with residual washout accounting, after item 1. It
requires item 6's multi-substance patient state, because residual washout
means holding two agents at once.

#### 3. Experimental-override mode

Add an optional experimental-override mode that can bypass standard
interlocks, clearly labeled as non-standard, after item 1.

#### 4. Direct agent injection into the circuit

Add direct agent injection into the circuit, bypassing the vaporizer and
its interlocks, after item 1.

#### 5. Automated end-tidal control

Add automated end-tidal control (closed-loop titration to a target
end-tidal concentration), after item 1.

#### 6. Nitrous oxide, with the patient's state as a set of substances

Add nitrous oxide coadministration as a second inhaled gas, only after the
coupled-gas equations and reference cases are defined. Model the patient's
state as a set of substances, rather than as a volatile agent with nitrous
oxide bolted on. Items 2 and 7 need the same generalization, and it decides
whether item 13 is an extension or a rewrite.

#### 7. Concentration and second-gas effects

Add concentration and second-gas effects for coadministered gases, after
item 6.

### Scenarios, replay and forking (items 8-12)

#### 8. Scenario events on a recorded control-input timeline

Add scenario events (timed parameter or state changes during a run).
Build them on a recorded control-input timeline. On that timeline, every
change to fresh gas flow, the vaporizer dial, ventilation and cardiac
output is stamped with the simulated time at which it took effect.
*The timeline shipped in halves: recording in v0.4.0 (`PL-DR1Z`), and the
replay driver in v0.5.0. § "Completed: v0.4.0 - the teachable case" →
"Designed for forking" says why it comes first for forking, and
§ "Development pathway" → "Phase 3 — reproducibility and comparison" says
why save/load and replay need it.*

#### 9. Scenario save and load

Add scenario save/load.

#### 10. Deterministic replay

Add deterministic replay of a saved scenario, after item 9.

#### 11. Side-by-side comparison of runs

Add side-by-side comparison of multiple scenario runs on a shared time
axis. Each curve is labelled unambiguously with the run and the settings
that produced it. This item is delivered with item 12, which produces the
runs worth comparing. *Shipped in v0.5.0 - see § "Completed: v0.5.0 - the
case you can branch" below.*

#### 12. Simulation forking

Add simulation forking (branch a running simulation into an independent
copy). This is the educational payload of the group. Take two ways of
managing the same case: coast on low flow, or hold 0.5 MAC, and then
compare the time to a wake-up threshold. Comparing two managements of the
same case isolates the variable under study. Building the case twice
instead gives two runs that differ in everything that was not reproduced
identically. *Shipped in v0.5.0 - see § "Completed: v0.5.0 - the case you
can branch" below, which holds the flat trunk with N branches, forking at
any control-input event, and the element-wise reproducibility test.*

*Branch points (project owner, 2026-08-25; `PL-TFX5` quotes the decision).*
Bookmarks (item 26) remain useful as the *named,
threshold-triggered* subset of branch points that a learner can
fast-forward to and fork from repeatably. They are not the only subset that
qualifies. Even so, a snapshot policy should still be keyed on the bookmark
set. The bookmarks are the subset of points that a learner is expected to
revisit repeatedly. So they are worth keeping cheap to reach, even where an
arbitrary timeline point is not.

*Required property.* A branch taken at time t must reproduce its
parent's state exactly at every recorded sample up to t. This is asserted
element-wise, not within a tolerance. Suppose a branch is resimulated from
a stored point while its parent was simulated straight through. The two
can then diverge *before* the branch point. That divergence is subtle,
and it will not show up in a nominal test. It also destroys the one thing
forking is for, because a learner reading the comparison cannot see it.
This note named three causes, and two of them are closed as of PL-VM40
(v0.4.0's Required scope). § "Completed: v0.4.0 - the teachable case" →
"Designed for forking" lists all three. What is left is a different step size, which
`docs/MODEL.md` § "The reproducibility guarantee" states it does not cover.
Also left is whatever a branch restores from a stored point rather than
resimulating. If exactness is unreachable, the divergence must be bounded,
documented in `docs/MODEL.md`, and shown to the user rather than implied to
be absent.

*Snapshot and resimulation cost (timed 2026-08-25).* The full dynamic state
is six concentrations plus the elapsed time and the control settings. A
snapshot is therefore about the size of one history sample, so dense
snapshots are nearly free. Resimulation is also cheap.
`SimulationState.advance` measured at 8.9 us per 0.1 s step. So
reconstructing a 3-hour run from t=0 takes about 1 s, and reconstructing 24
hours takes about 8 s. What is *not* cheap is the per-step concentration
history, which item 21 covers.

### Patient and drug models (items 13-19)

#### 13. IV pharmacokinetic and effect-site models

Add IV pharmacokinetic and effect-site models, after item 12 (simulation
forking) is available.

#### 14. Hypnosis and eBIS effect model

Add a modular hypnosis/eBIS effect model, with explicit model version and
provenance.

#### 15. Nociceptive-response effect model

Add a modular nociceptive-response effect model, with explicit model
version and provenance.

#### 16. Renal and hepatic dysfunction modifiers

Add validated renal/hepatic dysfunction modifiers, where supported by the
selected model.

#### 17. Cardiopulmonary bypass modeling

Add validated cardiopulmonary bypass modeling, where supported by the
selected model.

#### 18. ECMO modeling

Add validated ECMO modeling, where supported by the selected model.

#### 19. Species-specific profiles

Add species-specific patient/model profiles without treating non-human
patients as scaled humans.

### The application (items 20-24)

#### 20. Accessibility

Improve accessibility (keyboard navigation, contrast, screen-reader
support, color-vision-safe encodings).

#### 21. Performance

Improve performance, working from the open entries in
`docs/items/`. The render payload and the coupling between the
simulation cadence and the render cadence are both resolved. v0.4.12
deleted the controller's concentration history, which had been unbounded:
the chart now computes each point it plots from the run. What remains in this
area is further headroom in how chart points are built.

#### 22. Documentation

Continue documentation work.

#### 23. Packaging, signing and distribution

Add packaging, signing, and distribution work for shipping the app.

#### 24. Preferences panel

Add a user-facing preferences/settings panel (theme, chart window, slider
ranges, and similar display settings).

*Prerequisite: a settings store that can be written and saved.* This item
first named a different prerequisite: gather the display constants into one
module. At the time they were spread over `app/theme.py`,
`app/simulation_view.py` and defaults duplicated between `core/` and
`app/controller.py`. They were gathered in `v0.4.11` (`PL-2CS8`), and
`app/theme.py` is now the one location. No core and controller duplication
remains: `app/controller.py` holds no default values, and every setting the
user has not chosen comes from `core/`, built from the data files (checked
2026-11-09, `PL-HQ03`).

What remains is something to build, not a consolidation. The one location,
`app/theme.py`, holds constants bound at import time. A panel that *writes* a
setting needs something that can be written and persisted, and this
repository has no such store yet. That store is the prerequisite to scope.

*What the panel must never make editable, and the test that decides it*
(`PL-QBX0`, 2026-09-19). **What decides is the guarantee a value carries,
never the file it happens to live in.** Suppose something outside the panel
enforces a safety, standards-conformance or accessibility guarantee on a
constant's value. Then that constant is out of the panel's reach, wherever
it is declared. An enumeration cannot carry that rule. So the table below
lists the instances known on that date, and the criterion governs whatever
is added after it.

| What | Where it is declared | What holds its value |
| --- | --- | --- |
| Scientific parameters - partition coefficients, tissue volumes, MAC | `data/**/*.json` | validated, versioned and cited; `tools/doc_check.py` walks the provenance both ways |
| The three ISO 5360:2016 agent-identification colours | `app/theme.py` | `tests/unit/test_theme.py` pins each fill to Table 2; `tools/agent_identity_check.py` keeps the pair as measured equal to the pair as rendered |
| Every colour `tools/contrast_check.py` measures - the six compartment traces at 3:1 against the panel under normal vision and three simulated dichromacies, and every text pair at WCAG 2.2 AA | `app/theme.py`, and any module under `app/` that declares its own | `tools/contrast_check.py`, which reads every module under `app/` with `ast` |
| The six compartment traces' dash patterns | `app/chart_frame.py` | nothing mechanical - a recorded judgment, which is exactly why it is listed |

Each of these values stays changeable only through the review that set
it, never through an ad hoc settings screen. For the first row, the review
is deliberate scientific review under `CLAUDE.md`'s safety-critical
standard. For the other rows, it is the recorded reasoning in
`app/theme.py` and `docs/MODEL.md`.

The colours are out of the panel's reach for the same reason the parameters
are. ISO 5360 Table 2 footnote b makes displaying an agent colour an
obligation to display the *right* one. A panel that let a reader recolour
the agent colours would let one agent be shown in another agent's
identification colour. That is exactly `CLAUDE.md`'s "the correct number
with the wrong units, label".

The dash patterns are what tells the six compartment traces apart, because
colour cannot separate them at all. The 3:1 contrast minimum caps every
trace's luminance, so no two of the six traces can differ by a contrast
ratio of more than 1.48:1. `app/theme.py` records the search. The dash
patterns are also the only entry in the table above that no check would
protect if a panel flattened them.

### Playback and teaching views (items 25-28)

#### 25. Playback speed multiplier

Add a playback speed multiplier, so a run can be advanced faster or slower
than real time without changing the simulation's own time step. It is kept
separate from deterministic replay (item 10). Replay reproduces a recorded
run, while this changes the rate at which any run is displayed.
*Shipped in v0.4.0 as `PL-SN2C` - see § "Completed: v0.4.0 - the teachable
case" below.*

#### 26. Run bookmarks

Add run bookmarks that halt a run at a target, after item 25. There is
currently no way to say "run fast until something happens, then stop". A
learner comparing gas-management strategies has to watch the clock and
pause by hand. That is not repeatable, and it is not possible at speed.
Bookmarks are what make fast-forward usable. They are also the branch
points that a learner deliberately returns to by name (item 12).
*Shipped in v0.5.0 - see § "Completed: v0.5.0 - the case you can branch"
below, which holds time bookmarks and MAC targets as two collections, and
crossings tested inside the advance loop with a distinct not-reached
outcome.*

Bookmarks are part of the saved scenario rather than local to one session,
so item 12 can branch from them.

#### 27. Schematic compartment view

Add a schematic compartment view alongside the graph, after the
interactive "Picture" of the Gas Man reference simulator. **Scheduled in
v0.7.0** (project owner, 2026-10-25, ratified, over containers drawn to
scale and over Gas Man's Picture as it is). § "v0.7.0 - the schematic" has
the scope.

#### 28. Agent cost

Add agent cost, from the delivered-agent amount that the model already
tracks. The economic argument for low fresh gas flow is a standard
teaching point. It is currently the one lesson in this class of simulator
that the application has the numbers for and does not draw.
**Scheduled in v0.7.0** (project owner, 2026-10-25, ratified, over
leaving it unscheduled and deferring its four entries to Gate 4).
§ "v0.7.0 - the schematic" has the scope.

*Cost is computed from delivered agent* (`PL-H4N8`).
`core/agent_simulation_validation.py` enforces the accounting identity
`initial + delivered = exhausted + currently stored`. Cost is what left the
bottle, which is what the vaporizer added: `delivered_agent_l`.
`exhausted_agent_l` is what has left the *circuit*. It understates delivered
by exactly `currently_stored_agent_l`. Measured on 2026-09-19 with
`AgentUptakeSystem.default()` (a reference adult, sevoflurane held at a
fixed 1 MAC dial, and a 0.1 s step), on the exhausted basis 1 against
8 L/min shows 18.4:1, 15.3:1 and 13.4:1 at 15, 30 and 60
minutes, where delivered is exactly 8:1. That overstates the saving by as
much as 2.3x. The Gas Man reference simulator bills delivered agent too
(Workbook Appendix, printed p. 174: `Cost = DELIVERED Flow x Cost/mL
vapor`). So does this project's own `docs/MODEL.md`.

*Prerequisite: a vapour-to-liquid ratio for each agent, now derived from
stored constants.*
`delivered_agent_l` is measured in litres of vapour, and a bottle holds
millilitres of liquid. So a figure in money or in bottles needs a
vapour-to-liquid ratio. `PL-KZ99` (2026-10-26) stored each agent's molar
mass and its liquid density, with the density's measurement temperature,
in `data/agents/sevoflurane.json`, `data/agents/isoflurane.json` and
`data/agents/desflurane.json`. `core/liquid_agent.py` derives the ratio from
them in one place (`docs/MODEL.md` § "Agent amount"). It is exact for the
delivered amount, which is the one a cost needs, and reads a compartment
store 5.8 % high (`docs/MODEL.md` § "Known limitations").

*The exhausted/stored split keeps its own labels.* The split is the uptake
curve in mass form, and it is worth drawing. It is simply not the
economics, and nothing here may relabel either line as waste. `PL-B396`
chooses that display and what the cost figure looks like.

### Code that reads like the domain (item 29)

#### 29. Make core/ read like the domain

Make `core/` read like the domain, as one deliberate pass over the whole
package rather than opportunistically. **The bar, stated by the project
owner 2026-09-03:** a reviewer who knows the standard variables and
equations of the textbook should be able to follow `core/` and recognize
them, without referring to `docs/MODEL.md` and without a lookup table. That
is a sharper test than the one-line bar in `.claude/rules/core-domain.md`.
The answers below are judged against it. The purpose is the project owner's
own fluency in the code. Reviewing the coupled-gas equations of items 6 and
7 is the hardest scientific work in this plan. Doing that review against
code that reads like the textbook is a different task from doing it against
code that does not.

*Placement (project owner, 2026-08-26; revised 2026-09-02).* The pass
comes after v0.4.0 and ahead of item 6's substance generalization. The
second half of that placement is the original constraint, and it has not
changed. Item 6's change restructures every compartment. Settling the
vocabulary first makes that change a transformation of well-named code,
instead of a renaming and a restructuring at once. The accepted cost is
that some of this pass is revisited when compartments become
per-substance. What survives is the convention, which is the part that is
expensive to invent twice. The pass sits immediately after v0.4.0, as the
`v0.4.x` row of "The timeline". The 2026-09-05 design round placed the
score architecture in v0.5.0, and that architecture is chained behind
`PL-GS5X`. The step was pinned immediately ahead of v0.5.0. `PL-GS5X`
closed on 2026-09-06 in pull request 376, which is what made that chain
startable.

*Version: a patch in the `v0.4.x` track, and no exception is recorded for
it (project owner, 2026-09-03; the specific number released 2026-09-05).*
The decision is the class of version, and it is unchanged. What was
dropped is the promise of `v0.4.1` in particular, which the release path
cannot keep. `docket release` gives the next free number to whatever is
finished, so a patch cut before this work lands takes that number.
§ "Versioning decision" says which numbers a patch cut may not take. This
step ships under whatever number the cut assigns.

§ "Versioning decision" above chooses by the **capability boundary
crossed**, and this step crosses none. The simulator models the same system
with the same parameters, the same four controls and the same three agents.
The learner can do nothing they could not do before. Two things do change,
and neither is a capability. First, the displayed value moves in its last
digit, which v0.2.11 already shipped as a patch. Second, the *guarantee*
strengthens from "within a measured bound of the stated equations" to "the
exact solution of them". The step bound may well survive with a different
justification rather than disappear. So even the set of accepted inputs may
be unchanged. `PL-X9KD` settles that question.

The temptation is to number it up so that the change can be pointed at.
That is exactly the argument that the v0.3.0 exception made, and that
exception says it is not a precedent. The release row and the baseline
section are where a change gets pointed at.

*Scoped, then re-scoped the same day (project owner, 2026-09-03); the three
open questions are answered.*

**Naming alone could not meet that bar, which is what the re-scope
found.** So the operator split was replaced by the exact matrix exponential
(`PL-GS5X`, landed 2026-09-06). Under that method, assembling the system
matrix *is* transcribing the governing equations. The code that computes
the result is the code that a reviewer recognizes. `PL-SPMQ` carries the
measurement and the options that were weighed.

This supersedes `PL-6GS0`, which decided in v0.2.8 to keep the split. That
decision weighed accuracy and step size, and it was right on both. The
readability requirement was not part of its frame. `PL-X9KD` re-derives
every published statement that was justified by the splitting error:
§ "Displayed precision", the supported step bound, and the pinned
reference states.

Nine items carry this step, and the `v0.4.x` row of § "The timeline" lists
them.

**What "reads like the domain" means concretely.** It is not a mapping
from symbol to identifier. Identifiers in this project carry their unit or
kind (`alveolar_ventilation_l_min`), which a bare symbol cannot do. The
compartment object already supplies the subscript, so $`F_A`$ in code is
`alveoli.<accessor>` rather than any single identifier. The mapping is
therefore from a symbol to an **expression**. It is kept as a fourth
column of `docs/MODEL.md` § "Symbols" (`PL-H46J`), which makes the pass
both finite and checkable. Beside it sits one name per modelled quantity.
`core/` currently gives the partial-pressure-equivalent fraction eight
names across four compartments, and `PL-9SH6` collapses them to one.

**Whether equations belong in the code or are cited from it.** The answer
is both, and the line between them is sharper than "per-case".
`docs/MODEL.md` writes the differential equations, while `core/`
implements their analytic solutions. The spec carries a solved form in
exactly one place. So a docstring that restates the solved form supplies
the missing half rather than a second source of truth. The rule is
therefore: always cite, restate only the solved form that the spec lacks,
and never restate what the spec states (`PL-VZL0`).

**How much of the bar is decidable.** There are three rules, and all of
them are mechanical. Every Code cell resolves to a real attribute. The
retired accessor names never reappear. A partition-coefficient identifier
names both phases in order (`PL-FZ6T`). What remains a matter of judgment
is the question that the bar is written as: would a reader who knows the
domain guess this?

**What the sources changed.** The project owner supplied two references
during scoping. They settled questions that the pass could not settle from
inside the tree. Hendrickx and De Wolf establish that the domain's
gas-phase cascade is $`F_D \rightarrow F_I \rightarrow F_A`$ and has no
$`F_C`$. So the middle state is named after its container rather than
after the clinical quantity. And the $`F_A/F_I`$ curve that this simulator
exists to draw has a denominator that cannot be found by name in the code
(`PL-3TLK`). Hendrickx and De Wolf also record that in the gas phase
"fraction", "concentration" and "partial pressure" are interchangeable.
That settles the accessor name, against a convention that distinguishes
the three terms. Baker and Farmery name one partition coefficient three
different ways within a single chapter. That is why the naming rule for
ratios is worth enforcing mechanically rather than leaving to a reader's
recall (`PL-212V`).

### Items added later (items 30-43)

#### 30. Patient factors

Add patient factors (age, sex and weight as inputs) so that a learner
can see how patient characteristics change the anesthetic. This is a
core teaching component, not a later extension. The reference adult in
`data/patients/reference_adult.json` is a placeholder for it. The
question "how would this differ in this patient" is the one a
compartment model exists to answer. Today the application's only
statement about patient variability is that there is none.

Built-in patient profiles stay read-only. They support a "duplicate and
customize" workflow that carries lineage and schema metadata, so that a
modified profile can always be traced to the cited profile it was
derived from.

*This item is placed in Phase 1, ahead of the substance generalization
(project owner, 2026-09-02).* That generalization is this plan's stated
known risk, and the most likely place for the work to stall. A core
teaching component does not belong behind it. Also, once compartments hold
N substances, changing how compartment volumes and flows are *derived*
touches N times as much surface. The same argument already places item
29 ahead of that work.

*The teaching payoff needs item 11, which has shipped.* A single trace
cannot show an effect, because the contrast is the lesson. Side-by-side
comparison (item 11) shipped in v0.5.0, on the two-run rendering that the
decomposition of the run view (`PL-B9PY`) made possible in v0.4.25. So
this item's payoff is available as soon as it ships.

*This item removes a safeguard that `docs/MODEL.md` names (`PL-DXJR`).*
The fixed reference adult is one of the two safeguards in `docs/MODEL.md`
§ "What keeps a real patient's data out of a run". Once age, sex and
weight are inputs, a run can be built from a real patient's data. So this
item rewrites that section and its hazard row.

*Scaling: not through body composition (project owner, 2026-09-02).*
Weight scales the compartments directly. Another route was proposed and
declined. In that route, weight, height and sex would first produce a
body-composition estimate, and that estimate would scale the
compartments. Sex is therefore a covariate in its own right, not
something that acts through fat mass.

The trade is worth recording rather than arguing, because scoping will
meet it. Fat is the pivotal compartment for volatile agents. Its
tissue:gas coefficients are 34 for sevoflurane, 70 for isoflurane and 13
for desflurane. So between two patients of the same mass and different
composition, the fat compartment is what separates them. A rule keyed on
total mass cannot express that difference. What the direct route buys is
one fewer layer of unsourced derivation. A body-composition estimate
needs its own formula, with its own provenance. An unsourced scalar in
front of the dominant compartment is the
"plausible but incorrect clinical value" that `CLAUDE.md` forbids. It is
that just as surely as having no scalar at all. Whichever rule is
chosen, it is sourced before it ships. `Weber et al. 2021` is already
cited in `data/patients/reference_adult.json`. It explores the obese case with
the same reference simulator that this project draws its parameters
from, and scoping should start reading there.

*Cardiac output is one of the quantities that scales, and the scaling is a
coupled package (`PL-YKSM`, 2026-09-08).* The decision above settles what
weight acts *through*. This one settles which quantities "weight scales
the compartments directly" has to include. A time constant here is
$`V_i \lambda_{i:b} / Q_i`$. Suppose a rule scales the flows but leaves
the compartment volumes at the fixed litres this project stores. Then
$`\tau \propto M^{-3/4}`$, so a heavier patient equilibrates faster and
a lighter one more slowly. Worked at 20 kg against the shipped
sevoflurane coefficients, that rule gives a child **2.64 times** the
adult's time constants. Every textbook has the effect running the other
way. When volumes scale with the flows, the figure is **0.76
times**, and when nothing scales at all it is **1.00**. The half-measure
is further from the truth than the status quo. So compartment volumes,
alveolar gas volume, alveolar ventilation and the perfusion fractions
move together with cardiac output and the tissue flows, or none of them
moves. `PL-YKSM` carries the arithmetic and the alternative it refused.

*Body composition defaults, and is editable per case (project owner,
2026-09-02).* A case opens with a body composition already set, rather
than asking the learner to supply one. The case settings let the learner
edit it when changing it is the point of the run. This settles the
derivation question in one direction. The default is *derived*
from the case's other patient inputs, so an edit overrides a value that
was already there rather than filling a blank. Two consequences follow,
and neither is in this item's scope as it currently stands. First, the
derived value has to be visible and attributed wherever it acts. The
attribution names the rule that produced it, and says whether it is still
the default or has been overridden. A silently substituted body composition
that moves fat uptake is exactly the plausible-but-unexplained clinical
value that the safety standard refuses. Second, an edited composition is
a covariate set that nobody sourced. So the supported-range refusal
below applies to the edit control exactly as it applies to the input.
Accepting a hand-entered composition outside the parameter set's domain
is the same failure as extrapolating to it. There is no case-settings
surface today. So this paragraph names an intended surface, not an
existing one.

*MAC moves to the Mapleson MAC40 basis (project owner, 2026-09-02).* The
move comes in the release that adds age. Today the simulator takes MAC
(`mac_percent`) from the flat Gas Man values that the agent files carry:
sevoflurane 2.0, isoflurane 1.2 and desflurane 6.0. The MAC40 values below
differ from these, so the displayed MAC changes at every age, *including*
40. The move is therefore a parameter-set change that needs a provenance
row and a release note, not a new input field. It lands after MAC
multiples become a display unit (`PL-DHV7`), because an age-adjusted MAC
with no MAC unit to show it in changes nothing a learner sees.

Nickalls and Mapleson (Br J Anaesth 2003;91(2):170-4) is already cited in
all three agent files (`data/agents/*.json`). Each file has a note
recording that the paper is *not* used, because this model has no age
parameter. This change puts the paper to use. Nickalls and Mapleson's
meta-analysis has log10 MAC falling linearly, and in parallel for every
inhaled agent, at about 6% per decade for age >= 1 year. MAC is expressed
relative to its value at 40 years. MAC40 is reported as 1.17% isoflurane,
1.80% sevoflurane and 6.60% desflurane. Confirm these figures against the
primary paper when this is scoped, rather than copying them from here.
That is the provenance standard that every other parameter in `data/`
must meet.

*Two questions are left for scoping: how body composition acts on the
model, and how the simulator responds to an edited body composition that
is out of range.* The first arises because the scaling decision has weight
act on the compartments directly, while the body-composition paragraph
has an edited composition move fat uptake. It also covers whether height
is an input, since height appears only in the declined route. The second
arises because the body-composition paragraph applies the supported-range
refusal to an out-of-range edit, while the covariate paragraph below
leaves the response (blocking, logging or both) open.

*This item suggests, without deciding, that scoping prefer measured
weight-banded normal ranges to an allometric formula for the default
cardiac output.* The learner sees the default, not the law that generated
it. Cattermole et al. 2017 is already cited in
`data/patients/reference_adult.json`. It reports 2218 healthy subjects aged
0.5 to 89, by weight band. It is a measurement of the quantity, not a
scaling exponent applied to one. It is not free of the provenance problem
it would solve, and scoping has to weigh that. Its subjects are awake,
supine and at rest. They were measured by transcutaneous Doppler rather
than thermodilution, and the authors state that normal ranges are
method-specific. That is why the file cites the paper and does not adopt
it. Adopting it as a default would be its own recorded decision under
§ "Source hierarchy", on the same terms as every other value in `data/`.

*An out-of-range covariate: agreed in principle, cutoffs unresearched
(project owner, 2026-09-02).* The right shape is accepted: bound each
covariate, and report when one is outside its bound by blocking, logging
or both. What is **not** settled is where any cutoff sits. No number is
written into `core/` until it is researched and sourced on the same
terms as every other value in `data/`. A bound invented just to have a
bound would refuse the paediatric or obese case that a learner most
wants, on a number nobody can cite. That is worse than no bound at all.

So this is a research question before it is an implementation question.
It is part of scoping this milestone, not a queue item that could be
picked up ahead of it. Two things frame it. First, `core/supported_ranges.py`
is the nearest pattern, and its argument still applies. A silently
extrapolated patient would simulate, display and chart a value that the
parameter set cannot support. Second, it is not the same case. The four
quantities that module covers are operating settings inside a run, where
refusing a value costs nothing. A covariate defines the case itself.
Refusing to construct a 3 kg or a 200 kg patient refuses the question
that a learner came with. That asymmetry is why the mechanism is open
rather than inherited.

#### 31. Primary-literature partition coefficients, selectable beside the Gas Man set

Ship a primary-literature partition-coefficient set alongside the Gas Man
set, and make the two selectable. Then one case can be run under both,
and the difference read off the same axes. Building the primary set is
the prerequisite and the larger half of the work. `vessel_rich` is a
lumped compartment, while Yasuda 1989 reports coefficients per organ. So
a scheme for weighting the organs in the group has to be constructed and
justified before any tissue value may be called primary. Shipping both
sets, rather than replacing one with the other, is the point. The
question "how much does the parameter set matter?" is one that no
commercial simulator lets a resident ask. Comparing the two sets teaches
the provenance lesson better than any note in a data file can.
`PL-D6LX` carries the analysis and the verified primary values. The
project owner chose this route on 2026-09-03.

#### 32. Repository presentable to a first-time visitor

Make the repository presentable to a first-time visitor, in one pass.

**What is left here is every human-facing piece that a first-time visitor
meets, other than the README.** The root `README.md` exists, written for the
two audiences that `PL-RM83` settled. No list of the other pieces was written,
and the list is made when this item is scoped. Nothing brings this work to
anyone's attention: nothing is blocked on it, and no check reports it. So it
waits for a session that offers to scope this milestone, or for the owner to
ask.

**The repository went public before this pass, not after** (project owner,
2026-09-05: "public today. Will do human facing pass in the nearish
future."). So this item is no longer a gate.

#### 33. The interface pass

Run the interface pass. This is one deliberate visual design pass over
the whole interface: palette, type scale, spacing rhythm, density and the
visual composition of each surface. It is one pass, instead of the
per-defect corrections that the queue has been making one at a time.

*Arrangement belongs to item 34* (corrected 2026-09-16, `PL-BNYF`). Item
34's entire content is which areas exist, where they sit, and what a
reader may do to them. This item decides how the contents of those areas
look. The two were separable on 2026-09-08, when this item was written
against one fixed screen. They are not separable any more. Under item 34
the arrangement belongs to the *reader*, so it is not something a design
pass can decide once.

*Dark mode and figure export are deliberately out of scope.* Dark mode is a
separate decision. It doubles the declared contrast matrix, and the ISO
colours were chosen for a light context. Part of it is settled: the
interface declares its own light palette, so a dark host no longer darkens
the window (project owner, 2026-09-20, ratified, over a second palette for
dark support, `PL-KRZW`). Whether to offer a dark mode belongs to scoping
this milestone rather than to this line. So does the publication-quality
figure export that `docs/WORKING_NOTES.md` § "Long-term vision" describes.
That export implies its own rendering path, separate from the live
chart, and it is a capability rather than a restyle.

*Placement (project owner, 2026-09-08; moved 2026-09-16; renumbered
2026-09-26).* The pass comes after v0.6.0, as the
`v0.6.x — the interface pass` row of "The timeline". It is a patch track
rather than a numbered milestone, for the reason that row gives. The
project owner requested it on 2026-09-08 as "a decent size overhaul
(theme, style, overall polish)". The owner called it not urgent, and
wanted it after the simulator works.

**The pass runs after item 34, because by then it has more to style, and a
pass run first would be partly redone** (project owner, 2026-09-16,
ratified on `PL-PHKP` - chosen over leaving it between MVP and Gate 2,
where 2026-09-08 had placed it). The live splitter handle, the drag
affordance and the Workspace tab strip are v0.6.0's Required scope
entry 14. The area header comes with the View contract and with each
Area's own chooser, entries 5 and 16. The header belongs to the *View*,
not to the container, as `docs/interface-provenance.md`
§ "What an editor must implement" establishes from the source. A pass
run first would decide palette, type scale and spacing for one set of
surfaces, and then meet four more. Whenever break-out is built, it adds
windows that carry that same chrome. Styling anything else it adds is
that build's own work. The cost accepted is that the interface keeps
its current visual language until after item 34.

*Two prerequisites, both now met.* A visual pass is the one class of
change that a suite without rendering cannot see, so both prerequisites
had to land first. When this item was written, nothing in this repository
drew the interface. One item recorded two defects that shipped while
every tree-level test passed (`PL-7J96`). A required label wrapped
mid-phrase, and four of seven readouts dropped to a second baseline at
some widths. Both were found only by screenshotting, and neither could be
detected from the control tree that the suite reads. Another item
recorded that no session in the web container could render the Flet
interface at all, because the egress proxy refused the CanvasKit fetch
(`PL-2QMK`). Both prerequisites are met: the interface moved to Qt in
v0.4.26, which closed the item on the web container with headless
rendering tests over the real interface (`PL-YCWZ`). The item on the two
defects was dropped as superseded by those tests.

*Three constraints on any palette.*

1. Every declared colour pair must meet WCAG 2.2 AA under four vision
   models. A check that reads every module under `app/` enforces this,
   and fails the build on a renamed or undeclared colour constant
   (`PL-BXB2`). So a restyle also rewrites the check's list of declared colour pairs
   (`REQUIREMENTS`) in the same change, per `.claude/rules/ui-color.md` judgment 1.
2. The three agent colours of ISO 5360:2016 Table 2 are fixed
   (judgment 4). A palette has to live with them, and keep them legible
   on whatever surface it puts behind them.
3. Trace separation is carried by dash pattern, not by colour. The
   ceiling that item 24 gives was measured (`PL-GVXP`). So re-picking the
   chart palette cannot improve trace separation, which has no solution
   in colour.

*Returned from the Qt port, which changed nothing visual* (project owner,
2026-09-16, ratified, on `PL-L9RD`). Measured after it landed, the port changed no palette entry,
type size, padding or radius at all. Every dashboard surface is now an
independent widget with its own spacing and density, and that is what
makes one pass over them possible at all. This item inherits none of the
splitting, joining or workspace behaviour. The point to read before
scoping this is that a port is not a design round. Re-expressing widgets
in a new toolkit does not decide anything about how they should look.

*The structural half is not part of this item, and it has landed.* Most of
what an overhaul looks like from outside is not polish, and all three
pieces of that structural work are now closed: the display constants
(item 24), `PL-B9PY`'s decomposition in `v0.4.25`, and `PL-NGF7`'s
theme-object question in `v0.4.26`. None of the three is debt that any
gate still has to clear. What is left for this item is the part that is
genuinely taste.

*The shelved mockups are not a starting point.* `docs/WORKING_NOTES.md`
§ "Shelved, then resumed: UI structure/form mockups" records a mockup
round. The round was explored and then shelved on the owner's call, and
the note closes with "Do not resume this without the project owner asking
again". That condition is now met. Per the note, the three artefacts from
that round are explicitly not a starting point.

#### 34. Blender's window management as the model for the interface

Take Blender's window management as the model for the interface. The
application window is divided into resizable, modular areas, and each area
holds one view. Task-oriented layout presets let the learner switch between
layouts, customize them and save them.

*Requested by the project owner, 2026-09-12*. The request named four
properties: resizable windows, modular views, presets for tasks, and
presets that the user can customize and save, rather than a fixed set
shipped with the application.

*This project uses three terms: Area, View and Workspace* (project owner,
2026-09-16: "the workspace/area concept ... is what I want to implement").
The terms were read at the source. The Blender Manual's "Areas" and
"Workspaces" pages were supplied directly, because the sessions' network
proxy refused `docs.blender.org` when this was written, though the host
answered a probe on 2026-09-26 (`PL-M701`). Area and Workspace are
Blender's terms, and View replaces Blender's Editor
(§ "The third word is deliberately not Blender's"):

- An **Area** is a rectangle that reserves screen space. It holds one
  thing and nothing else, and areas never overlap.
- A **View** is what occupies an area. The view is the part that has the
  functionality. Item 36 is the catalogue of views.
- A **Workspace** is a set of areas that contain views. Each workspace is
  geared to a task, and the user switches between workspaces as tabs.
  Blender puts the tabs in the Topbar and saves workspaces in the file. It
  also lets a custom set of workspaces become the defaults.

*Why Blender specifically, and what is worth copying.* Blender's window
system is **tiling**, not floating. The user splits and joins areas from
their corners and borders. The user can reorder, duplicate and delete
Workspaces. A layout persists when it is saved into the startup file. The
tiling half earns its place here on merit, not on taste. A tiled layout has
no overlapping or hidden panels. On this application's dashboard, a covered
value is a misread value, and `CLAUDE.md`'s standard treats a misread value
as a safety failure rather than an inconvenience. See the Blender Manual,
"Interface → Window System → Areas" and "→ Workspaces".

*The views are item 36, which comes after the layout* (project owner,
2026-09-15). The ordering is also the sound one, not only
the owner's preference. A view's contract is whatever the area system
requires of its contents. So views built first are built against today's
fixed layout and then rewritten. There is one refinement. A container
abstraction that only a single view exercises has not really been
exercised. So this item validates against **two** views that already
exist, rather than against any new one. § "Completed: v0.4.26 - the
interface moves to Qt" supplies those two views, as the next paragraph
says.

*The Qt port reserves the layout and builds none of it* (project owner,
2026-09-12, `PL-8VL1`). The port really does build a layout container
once. So reserving the layout costs nothing, and rebuilding it would cost
the work twice. So the port reserves the layout for this item and builds
none of it. Each dashboard surface becomes an independent widget inside
nested `QSplitter`s with the handles inert, and this item is what makes the
handles live. § "Completed: v0.4.26 - the interface moves to Qt" →
"Required scope" item 2 carries this.

*Item 34 follows v0.5.0, split at break-out* (project owner, 2026-09-16,
ratified on `PL-NMTF`,
over the two alternatives put with it: inserting item 34 ahead of v0.5.0,
which renumbers a scoped milestone, and shipping it undivided with
break-out inside). Item 34 goes **after v0.5.0** rather than before it, on
three grounds. First, a workspace that pins which run it shows has no
content until more than one run exists. And v0.5.0 is what introduces the
second run. Today `run_label` names a run `None` whenever it is shown
alone. Second, inserting item 34 earlier would renumber a milestone already
scoped with a frozen gate. Placing it after renumbers only rows that
§ "Planned milestones" already calls provisional. Third, no known failure
is live yet. `PL-NWTM` and `PL-9LNF` are both `safety`-classed, and both
are *pre-loaded* rather than live. The failures they name need a working
handle, and the port's handles are inert.

*Re-affirmed 2026-09-17* (project owner, ratified, chosen over moving item
34 ahead of v0.5.0, which is the alternative that was put). **v0.5.0's
Required scope is 13 of 20 `done`, and the monolithic half is the part
that landed**. `PL-8PSW` and `PL-1XPX` are both closed. `PL-8PSW` is the
two-branch overlay, which this file calls the largest new visual surface
in the project. `PL-1XPX` is what the readouts show while two branches are
displayed. The fork (`PL-TFX5`) and the resumption (`PL-J2TD`) are closed
too. What remains is the bookmarks chain and three small items, **4 M and
3 S**, against this item's own 4 L / 16 M / 3 S. So the re-order would
park an MVP a seventh the size behind this milestone, to protect a surface
that has already shipped. It would also strand `PL-7Z84`, because the
bookmarks and fork work is what gives a workspace a run identity to pin
to. The order is kept.

*No new display surface is built before this item* (project owner,
2026-09-17, ratified, chosen over leaving the ordering implied by row
position). A surface built before the area system is built against
whatever layout exists at the time, and against no view contract. So it is
built twice: once into a fixed parent, and again as a View. Every
remaining surface is already behind this item: the schematic (item 27),
multi-substance and its readouts (items 6 and 7), and the interface pass
(item 33). So the rule costs nothing today. It exists so that the next row
move cannot reopen the question by accident. **It binds a new surface, not
a new value.** The rule does not defer a reading that `docs/INTERFACE.md` ->
"Minimum displayed outputs" already requires, or a correction to a reading
already on screen. The safety-critical standard is a minimum that no
ordering rule may lower, and a misleading displayed value is never held
back for a layout. **Its condition, and it is an instance rather than a
permanent refusal**: the rule ends when this item's View contract
(`PL-TH35`) and view registry (`PL-R1WQ`) ship. At that point a new
surface *is* one registry entry, and the second build no longer exists. A
surface wanted before then is filed against item 36's catalogue rather
than built.

*Tiled first, with break-out into a separate window* (project owner,
2026-09-15). The tiled half shipped in v0.6.0 (§ "Completed: v0.6.0 - the
layout is the reader's"). Break-out lets an area be taken into **its own
top-level window**, which is itself a full window with its own areas. The
Blender Manual's "Areas" page documents this as *View > Duplicate Area into
New Window*, or Shift-LMB on an area's splitter widget. The manual
describes the result as a fully functional window that belongs to the same
running instance and is useful across multiple monitors. Every window is
then tiled, so nothing inside a window covers anything else in it.

*Break-out unscheduled, 2026-09-26* (project owner, 2026-09-26: "This is
something I don't want to rule out doing eventually. Not something that
needs done soon."). Break-out remains this item's second half and is still
wanted, but it has no row on § "The timeline". Its row, "the second screen",
came off that day. As a consequence, the schematic (item 27) moved to v0.7.0,
and multi-substance (items 6 and 7) moved to v0.8.0 (`PL-V1Y7`), then off the
timeline the same day (`PL-5XG1`). Break-out is placed when the owner
asks for it, as any catalogue entry is. **What keeps it possible stays in
v0.6.0, unchanged:** the saved layout root's set of windows (Required scope
entry 1) and the per-window shape of the unconditional region (entry 7).
Break-out's build item, `PL-Y04W`, was dropped the same day, because an
eventual feature is recorded here as intent, rather than as an item in the
queue. The item's brief keeps the measurement that the build will need
first. The rule the build must satisfy is `docs/INTERFACE.md` § "Minimum
displayed outputs" -> "What this list requires once the layout is the
reader's".

*Floating windows are deferred, not refused* (project owner, 2026-09-15,
correcting this paragraph's first form). Taking a tiled area out into a
floating one is wanted later, and this milestone does not build it yet.
Tiled first is only the order of work, not a rule that floating is never
allowed.

The safety argument actually supports a narrower rule, and that rule
outlives whichever mechanism arrives: **nothing may cover a value the
display is required to show while the application still believes it is
showing it.** A floating panel over the dashboard is one way to cover such
a value. A broken-out window dragged back over the main window is another.
That is why the constraint belongs to the display rather than to a window
type. It is stated once, instead of being argued again for each mechanism.
Any later floating mechanism must comply with the occlusion rule, rather
than being ruled out ahead of time. **It is settled** (`PL-WLWY`, project
owner, 2026-09-15), in `docs/INTERFACE.md` § "Minimum displayed outputs" ->
"What this list requires once the layout is the reader's".

That list now divides into three parts. The first is an **unconditional**
set that no workspace may remove and nothing may cover. This set is stated
as a test rather than a list. It has an invariant tier and a tier
instantiated for each modelled substance. So the inhaled agent's
concentrations and MAC are today's instance and not a permanent
requirement (project owner, 2026-09-16). The second part is an
**accounting** set that must stay reachable rather than simultaneously
visible. The third part is **conditional** obligations, which apply to a
surface only when that surface is shown. So removing a chart removes no
required value, because the numbers never left. The unconditional set sits
outside the area system, and keeping it there is the guarantee that v0.6.0
has to build.

**What a second top-level window owes that set is settled too** (project
owner, 2026-09-16, ratified, answering `PL-W54S`, chosen over that item's
own two live readings). Every top-level window carries the *invariant*
tier and the name of the run it shows. The *per-substance* tier appears
once, in a main window that cannot be closed while any other window is
open. The two tiers are unconditional for different reasons, and those
reasons carry over to a second window differently. That is why the tiers
are allocated to windows differently. `docs/MODEL.md` carries the
argument, the two readings it refused, and the limit on which occlusion
any application can observe. This decision is recorded before break-out
is built, because it decides the shape in which v0.6.0 builds the region.

The division of the list is recorded as **a stepping stone**. It is
deliberately the rigid version while the layout apparatus is built, and it
is expected to be revisited as the apparatus matures. The occlusion rule is
the part that must survive a revision.

*Two precedents from Blender's source: the last workspace cannot be
deleted, and a workspace can pin its run.*
Both precedents come from the source. Blender refuses to delete the last
workspace. It enforces this minimum structurally rather than by a warning,
which is the same shape `PL-WLWY` settled for the minimum display. A
workspace also carries *settings*, not only a layout. Pin Scene makes
activating a workspace switch back to the scene that the workspace
remembers. The equivalent here is a workspace that pins which **run** it
shows. That is exactly what a broken-out window needs in order to name its
run.

*Read Blender's source freely; paraphrase and cite its documentation,
never paste it* (`PL-P5QX`). `docs/interface-provenance.md` is the record.
It holds the study protocol, what was read, what this project adopts and
what it deliberately does differently. A session building the layout
should start there.

*The layout is a nested-splitter tree, and Blender's own shipped layouts
are what settled it* (`PL-3J2P`, decided 2026-09-16 on the research that
the project owner asked for before the decision was fixed). The record of
the Blender study (`docs/interface-provenance.md`) gives the count, the
method, the construction and the condition under which this decision
reverses.

*The layout container sits behind a layout model of this project's own*
(`PL-C842`, recommended 2026-09-16 with the review of Blender behind it,
and the owner delegated the architecture call). This project needs three
properties that Blender does **not** provide, so they have to be built
into its own model rather than inherited:

1. A **loud failure** when a saved layout names a view that this build
   lacks. Blender silently substitutes a 3D viewport.
2. A guarantee that a **required value is never hidden to make room**.
   Blender collapses a region that will not fit.
3. **Isolation with teeth**. Every Blender editor can reach the whole
   screen. In Blender 5.3's source, examined on 2026-09-15, ten of its
   twenty-one editors read the other areas. The record of the Blender
   study gives the count.

A layout is serialized to versioned JSON.
§ "Completed: v0.6.0 - the layout is the reader's" → "Required scope"
entries 1 and 2 hold the layout model and its adapter as built.

#### 35. Optional model of anaesthesia's effect on cardiac output and regional perfusion

Add an optional model of anaesthesia's own effect on cardiac output and
regional perfusion. The model keeps both fixed today. The new model would
be an option the user turns on, labelled as an illustrative overlay
rather than as the model's own prediction. It would not change what a run
does by default.

*Framing (project owner, 2026-09-13).* This is recorded as a possible
future feature to consider, not as a settled exclusion. The owner directed
that the feature stay on this list as an option.

*The volunteer studies support no single dose-response.* The sign of the
effect depends on the carrier gas. The dose-response is not monotonic. The
effect also changes with time at a fixed dose. A single monotonic,
time-invariant relation therefore cannot be supported. The hard part of
scoping this is not the arithmetic. It is deciding what the option
*asserts* and how its uncertainty is shown to the reader.
`docs/MODEL.md` § "Known limitations" records the measurements, the
citations and the consequence for the tissue time constants.

*Resting tissue blood flow is itself uncertain.* The regional half of the
option needs the blood flow to each tissue under anaesthesia. Most of the
measurements the project can reach are from animals. The project has two
human comparisons for the stored resting fat flow, and they point
different ways. `docs/MODEL.md` § "Known limitations" weighs them
(`PL-HBH2`). The resting flow is uncertain by up to about a factor of
two, and the direction of its error is unsettled. A varying fraction
would sit on top of a resting fraction whose sign of error the two human
sources cannot agree on. That would be a second storey on the same
foundation.

#### 36. The catalogue of views

Build the catalogue of **views** that an area can hold. This is work
separate from the layout mechanism, and it comes after that mechanism
(project owner, 2026-09-15): "the layout part with the adding, resizing,
removing windows etc. and then telling the program what should be in that
window ... is the functionality I want to end up with. Then separately want
to work on widgets." Item 34 decides what an area is, how it is docked,
split, joined, swapped and broken out, and how a workspace is saved. This
item decides what a learner can put in an area. **The occupant of an area
is a View** (project owner, 2026-09-17, ratified - chosen over `Editor`, and
over `Component` and `Widget`). § "Completed: v0.6.0 - the layout is the
reader's" has the full reasoning, and `PL-GPYV` has the comparison. The
candidates named so far are the compartment schematic (item 27), the
control-input timeline, the numeric readouts and item 37's interaction
display. They also include the concentration chart and the F_A/F_I plot,
as views that a workspace places rather than as fixed sections of one
screen. The project owner requested this on 2026-09-15 as its own track
(`PL-4D1M`). Each view added here owes what any displayed clinical value
owes under `CLAUDE.md`'s clinical-output standard. The catalogue is where
that is settled once for each view, instead of being rediscovered for each
layout.

#### 37. Opioid/hypnotic interaction display

Add an opioid/hypnotic interaction display, after items 13 and 15. The
display shows iso-effect contours over a pair of effect-site
concentrations, for a named endpoint such as tolerance of laryngoscopy.
It is not those two items plus a plot. A response-surface interaction
model is a model class of its own, and the quantity it measures is the
synergy itself. So it cannot be derived from two single-drug models. It
owes its own versioned parameter file, provenance record and
source-hierarchy decision, exactly as each agent file does. `CLAUDE.md`'s
safety-critical standard already names interaction surfaces among its
own examples, and that sets the bar for the display. The display must
name the endpoint on screen, because tolerance of laryngoscopy, of
intubation and of skin incision are different surfaces. It must mark the
plotted point as a predicted pair rather than as a measurement. It must
also show the contours' population uncertainty, rather than let clean
curves imply that there is none. The project owner requested this on
2026-09-15 (`PL-JFXG`).

#### 38. The project's name and look

Decide what this project is called and what it looks like. That means
the name it ships under, an application icon, a splash screen if it has
one, and the wordmark that the README and the interface carry. The
project owner raised this on 2026-09-16, explicitly as something to
start thinking about down the road. This is intent, and scoping it is a
later decision (`PL-KFJQ`).

*Its own item because three others consume it.* Item 23 (packaging,
signing and distribution) needs platform bundle icons. Item 32 (make the
repository presentable to a first-time visitor) needs whatever sits at
the top of the README. Item 33 (the interface pass) sets the palette and
type of the interface itself. That is adjacent to an identity, but it is
not one. If this is left undecided, each of the three invents its own
answer at the moment it first needs one. That is how a project acquires
three.

*The name comes first, and it is the project owner's alone.*
`open-anesthesia-sim` is a repository name. Whether it is also the
product name is still open. The icon, wordmark, window title and bundle
identifier all derive from that answer, rather than being independent of
it.

*A splash screen, if this application has one, is a safety surface rather
than decoration.* It would be the one screen shown before any modelled
number. That makes it the least skippable place to carry the statement
that this is an educational simulation and not for clinical use. It is
also the place where polish does the most to make a simulator look like a
shipped clinical product, and `CLAUDE.md`'s clinical-output standard
already governs that. So scoping this decides what a splash screen says,
not only what it looks like. Having no splash screen is a legitimate
outcome. An application that launches quickly has no reason to hold a
user at a logo. In that case the same statement moves onto the first real
screen, and the obligation remains.

*There is no placeholder to build on* (`PL-J7MM`). This line is where the
intent lives until someone scopes it.

#### 39. Gas-phase conditions for each compartment

Carry explicit gas-phase conditions for each compartment, so that
temperature, pressure and water content are represented rather than
assumed away. This was raised from `PL-MPWP` as intent (project owner,
2026-09-19, ratified, over filing it as a queue item to be worked).
Scoping it is a later decision.

*Nothing displayed today depends on gas-phase conditions, which is why
this is intent rather than debt.* Every concentration the interface shows
is a dimensionless fraction, and every partition coefficient is a ratio.
So the trajectories, the mass-balance identity and the MAC multiples do
not change with the condition that the unit names. The condition matters
to a reader only where an amount leaves the unit. That happens in the
liquid-equivalent consumption figure that item 28 plans.

*Its own item because two recorded limitations already end here.*
`docs/MODEL.md` § "Known limitations" has two notes that both stop at the
same unbuilt change. The note "One reference condition, where the model
physically has two" sizes the temperature half. The alveolar, venous and
tissue stores hold 5.5 % fewer moles than their 20 °C label implies. The
note "The modeled alveoli are dry, and real ones are saturated at 47
mmHg" sizes the water half at 47/760. Each note says that removing its
limitation is outside the current milestone.

*This item is one change rather than two, and half of it is worse than
neither.* Both notes describe a model that carries gas at one declared
condition, where the gas physically has several. So the fix is a condition
for each compartment, covering temperature, pressure and water content
together. Correcting the water half alone is what that note explicitly
warns against. If 713/760 is applied to the inspired term while the
partition coefficients keep an unrecorded gas-phase basis, all four
validated wash-in ratios move outside their published spread.

*This item is also where the circuit's internal topology would go.* The
design of the machine abstraction (`docs/machine-abstraction.md`) gives
this item the job of representing the fresh gas inlet's position, because
a multi-limb circuit changes the model boundary. The design names this
item, or any multi-limb circuit entering the model, as the condition that
reverses item 1's decline to represent topology.

#### 40. An anesthesia machine as a config file

Make an anesthesia machine a config file rather than hardcoded Python
constants. This is the framework half of item 1, split out of it on
2026-09-20 (project owner). **The deliverable is the extension point, not
the machines.** A second profile dropped into
`src/anesthesia_sim/data/machines/` should be loadable and selectable in
code, and it should be refused where it is not admissible. Which machines
exist, and how faithfully each is modelled, belongs to item 1 and has no
timeframe.

**What "modular" is for: a real commercial machine is added as a data
file, not as code.** It is a claim about fidelity as much as a claim about
architecture. When the interface names a machine, a learner attributes to
it the behavior of the machine in their own operating room. So what the
module may carry and what the interface may say are the same question.

*The data half already shipped and the selection half does not exist.* `PL-4YY1`
moved the circuit volume and the fresh gas flow out of the field
defaults in `core/circuit.py` and into a cited, strictly validated
`reference_circle_system.json`. `PL-8PS6` added the first per-machine
capability field beside them. But
`load_reference_circle_system_parameters()` names one filename, and
nothing looks a profile up by id. Nothing in `src/` reads the profile's
own `id` and `display_name`. A second profile put in that directory today
is ignored by the runtime and passes the unit suite unnoticed. This item
ends that state.

*It stays separate from item 1 while it changes no rate.*
`docs/machine-abstraction.md` establishes that a machine affects the
model only through two rates and one volume. All three are in the
breathing circuit's row of the system matrix, and none of them touches a
patient row. So this item is separable exactly as long as it changes no
rate. It declares where a rate would come from and leaves the rates where
they are. As soon as a profile needs to *compute* a rate differently, the
work belongs to item 1, and this split no longer applies.

*One profile and no machine chooser.* The item
ships one profile and no machine chooser. A comparison surface belongs to
`PL-WZVZ`, and it waits behind item 34's View contract anyway. A second
profile plus a selection surface is what would make `PL-WZVZ`'s
misattribution hazard live. Nothing displayed changes.

*Rate extraction and several other parts are explicitly deferred, with no
rework cost.* Extracting the delivery and removal rates from
`core/governing_equations.py` and `core/circuit.py` costs the same whether
it is done with one profile or ten, so it waits for a machine that needs
it. Several other parts wait in the same way: the second member of each
strategy slot, automated end-tidal control (item 5), fresh gas decoupling
and ventilator drive, and internal circuit topology. Internal circuit
topology was declined, and item 39 reverses that.

*Each machine also needs a provenance row for each number.* The
documentation check requires one in `docs/MODEL.md` for every leaf number
in every data file. Item 1's cost target counts those rows with the data
file.

The queue items for this work are grouped as `machine-profile-framework`.
The two that mattered for the *first* real profile, rather than the second,
are done. v0.5.17 made the startup fresh gas flow optional, so a profile no
longer has to invent a figure that no manufacturer publishes (`PL-QW19`).
v0.5.23 stated that the circuit volume field (`circuit_volume_l`) covers
the apparatus and the patient circuit together, so a profile author adds the
patient circuit to a manufacturer's apparatus-only figure (`PL-TBMX`).

#### 41. Opt-in chart time windows kept in step

Let a chart View opt in to keeping its time window in step with every
other opted-in chart in its Workspace. Blender's "Sync Visible Range"
does this for its time-based editors. This comes after item 34's
per-chart windows (`PL-L59K`). Wanted "later" (project owner,
2026-10-19). `PL-1RFZ` has the notes from reading the Blender source,
and a Done-when.

#### 42. Renaming a run

Let a learner rename a run, after item 12. The name would show wherever
`dashboard_frame.run_label` names the run. A Workspace's pin stays on the
run's `RunId`. Two open runs must never show the same name, because a
legend entry must still tell the reader which run's settings drew a
curve. Wanted "eventually" (project owner, 2026-10-19). `PL-YBZJ` has
the design note.

#### 43. One source of truth everywhere

Make the rule of one source of truth true everywhere, and enforce it
structurally. A value, grammar, predicate, state or reading that the
repository already holds is read from the one module, data file or
writer that owns it. This applies in the simulator, its documents and
the apparatus alike (project owner, 2026-10-19:
"one source of truth everywhere", "a core design principle",
"fix this structurally everywhere").
`CLAUDE.md` § "Architecture and development discipline" states the
principle.

A second copy takes one of four shapes, and the fix depends on the shape: a
value copied (`PL-JS6P`), state with two writers (`PL-WM5P`), a rule made in
several places (`PL-VWXL`), and configuration restated (`PL-SH0W`). The
design is in `PL-2LB5`. The items are filed under the feature
`one-source-of-truth`.

An inventory taken on 2026-10-19 (`PL-K88Z`) sized the work for the
`v0.6.x — one source of truth` row, which takes no scope of its own because
it is a patch track. That item's brief holds the counts. The result is 13
items filed under the feature, plus the baselines of the four check items.
The inventory did not count the numbers that `docs/MODEL.md` and
`README.md` restate, so the item for copied values (`PL-JS6P`) sizes that
part when it builds its baseline.

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
  provenance and validation. *Note added 2026-11-09 (`PL-N32Y`): what shipped
  stores tissue:gas, not tissue:blood, as `tissue_gas_partition_coefficients`
  in the agent data files. The simulator derives the tissue:blood form from it
  by dividing by blood:gas (`tissue_blood_partition_coefficient` in
  `core/numerical_envelope.py`).*
- Add cardiac output and perfusion-limited vessel-rich, muscle, and fat tissue
  groups.
- Compute mixed-venous return from tissue outflow and couple it back to the
  lung-blood exchange.
- Allow fresh gas flow, delivered sevo concentration, alveolar ventilation,
  and cardiac output to change during a run without resetting state.
- Expose at least the delivered, circuit/inspired, alveolar/end-tidal, and
  mixed-venous or representative tissue concentrations, in snapshots and in
  the interface.
- Track the agent delivered, the agent exhausted, and the agent stored in gas,
  blood, and tissue compartments, so that mass balance can be checked within a
  documented numerical tolerance.
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

All the criteria above were met when the release was tagged, with one gap.
The mass-balance tolerance was stated in `docs/MODEL.md`, but the
step-refinement tolerance (0.5 % relative) was stated only in its test. That
test compared the 0.1 s step with 0.05 s only.

The reference scenarios were the two directional tests: ventilation of 2
against 8 L/min, and cardiac output of 2.5 against 7.5 L/min.

`docs/MODEL.md` § "Release gate" has the matching checklist for the scientific
documentation.

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
compartments, with the governing equations in `docs/MODEL.md`) is generic
across agents rather than specific to sevoflurane. Do this by adding
isoflurane and desflurane as two more validated, data-driven volatile agents,
each with independent reference cases. This milestone adds only new
per-agent data and the loading capability to select among agents.

### Required scope

- Add `data/agents/isoflurane.json` and `data/agents/desflurane.json`,
  schema-validated like `data/agents/sevoflurane.json`, with cited
  blood:gas and tissue:gas partition coefficients and source provenance.
- Extend the agent loading in `core/parameters.py` so that an agent can be
  selected by id, instead of always loading sevoflurane. The core's default
  constructor (`RespiratorySystem.default()`) currently loads parameters
  through one path only, `load_sevoflurane_parameters()`, and that path is
  hardcoded. Consider migrating the JSON validation in `core/parameters.py` to
  Pydantic while working on it, because the boilerplate in its `_require_*`
  helpers grows with each new agent schema. The module is isolated behind plain
  dataclass returns, so the switch is low-risk here. The migration landed just
  after the tag (`8457af33`) and first shipped in v0.2.1.
- Add independent reference tests for isoflurane and desflurane wash-in,
  uptake, and washout. Follow the same pattern of directional solubility,
  equilibrium, and mass balance already used for sevoflurane in
  `tests/reference/test_sevo_patient.py`.
- Document the parameter provenance of both new agents in `docs/MODEL.md`.
  Also note any agent-specific numerical considerations worth recording, such
  as desflurane's low blood:gas solubility.

### Definition of done

v0.2.0 is complete only when all of the following are true:

- `isoflurane.json` and `desflurane.json` pass the same schema and range
  validation as `sevoflurane.json`.
- Each new agent has independent reference tests. The tests show correct
  directional solubility behavior, and they show that mass balance closes
  within the documented tolerance.
- The v0.0.2 circuit reference tests and the v0.1.0 sevoflurane reference
  tests are unchanged and still pass.
- `docs/MODEL.md` documents the parameter provenance of both new agents.
- Ruff formatting and linting, strict mypy, pytest, and GitHub Actions all
  pass.

All the criteria above were met when the milestone was tagged.
`isoflurane.json` and `desflurane.json` load through the same
`load_agent_parameters(agent_id)` path, which was added for this milestone.
`load_sevoflurane_parameters()` is now a thin wrapper over that path, so no
existing call site changed behavior. `tests/reference/test_multi_agent.py`
covers directional solubility and mass-balance closure for both new agents.
The parameter provenance table in `docs/MODEL.md` and the document's new
"v0.2.0: isoflurane and desflurane" subsection record where both agents'
parameters came from.

### Explicitly out of scope for v0.2.0

- A UI control for selecting which agent is running. Agent switching and
  interlock behavior belong to the anesthesia-machine milestone (item 1 in
  § "Planned milestones" above). (This was recorded as the milestone's scope
  when it was tagged. A basic picker was in fact added afterwards, in commit
  `00791b1`. The picker restarts the run rather than switching agents
  mid-run. So the interlock and residual-washout work that this milestone
  excluded is still outstanding.)
- Physics specific to the vaporizer as a delivery device, such as
  desflurane's need for a heated, pressurized vaporizer. This milestone
  models uptake and distribution only, not the delivery device.
- Halothane, enflurane, ether, or xenon. These are a stretch goal further in
  the future, beyond this milestone. § "Planned milestones" records them as an
  unscoped later idea, with what sourcing each needs.
- Nitrous oxide. It is not a halogenated volatile, so it is out of scope
  here. Items 6-7 in § "Planned milestones" above cover it separately.
- Any change to the v0.1.0 governing equations themselves.

## Completed: v0.2.8 - the workflow works

### Goal

Make the development loop reliable before two long milestones are run through
it. Everything in this release is machinery that the project already depends
on. That machinery is the merge path, the release script, the queue's ranking,
the session-start digest, the type-check and lint gates, and the instructions
that a session reads before it does anything else. None of this work touches
the simulator.

This release comes first because of a standing decision in `CLAUDE.md`, dated
2026-08-30. The decision is that workflow work outranks product work until the
workflow is settled. It exists because friction in the loop is paid again in
every future session, while a deferred feature is paid for once. v0.3.0 clears
twenty entries of inherited product debt. v0.4.0 then builds the first
teachable case on top of that work. Both are long runs through the same loop.
Three faults in the loop would make those runs cost more than fixing the
faults does. The merge path does not wait for CI. The release script stops
halfway. And `docket next` ranks work that the current milestone excludes.

This release is a patch by the ordinary rule under § "Versioning decision"
above. It crosses no capability boundary.
Gate 0's minor-version exception is not extended to this release, and the
release does not need it.

### Debt gate: the frozen list

**Frozen 2026-08-30, the day this release was scoped, at seventeen entries.**
More entries have been admitted since then. Some came in under the completion
rule and the scope test described after this list, and one came in at the
project owner's direction. So the list's whole content is the entries below,
not the original seventeen. Each entry's item file records how it closed. The
release shipped on 2026-09-01 (#176), with every entry done except `PL-J786`,
which was dropped.

**This list is a frozen scope, not a fourth gate in the cadence.** The first
group below is debt as § "What counts" defines it, and every entry in it is
classed `defect`. The second group is new workflow capability, which
§ "What counts" says explicitly is *not* debt and does not hold a gate closed.
The numbered gates are unaffected. Gate 0 is still recorded under v0.4.0
below, and it still binds v0.4.0. It becomes the nearest gate again as soon as
this release ships.

The list's *size* is not restated in prose here, for the reason
§ "Recording it" gives. The size is stated in the group headings below and in
the two table rows that name this release.

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
  test: the hook is outside the repository, but the deliverable is a line in
  the instructions a session reads (one of the six pieces of machinery the goal
  names), and the hook misfires after every merged pull request, several times
  a session. The "workable here" limit below excludes a finding *nothing in the
  tree can close*, but this one closes with a repository edit.
- PL-HDY6 (S) The scope reader counts any id a milestone's section names, so
  the queue's ranking (`docket next`) reports an id the section names
  *to exclude* as in scope for the current step. Admitted 2026-09-01 under the
  scope test, after `PL-3576`, `PL-1Q3S`, `PL-RWZV` and `PL-H8MQ` (admitted
  together in #129) and on the same reading: the queue's ranking was
  misdirecting a session on `main` that day, telling it that `PL-68XK` clears
  this gate on the strength of the paragraph below that says `PL-68XK` does
  not. The fix is not simply to prefer this subsection, because v0.4.0 names
  nine open ids as its own Required scope rather than as gate entries, and
  those are in scope. So the item records both candidate rules and what each
  costs.

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
  guards it. Admitted 2026-09-01 under the scope test: the lint gate is named
  in the goal, and this is the other half of `PL-921W`'s promise, left
  unguarded where that item guarded the first.
- PL-CMCB (S) All ten `type: ignore` directives sit under `tests/`, outside
  `[tool.mypy] files`, so mypy's check for unused ignores
  (`warn_unused_ignores`) has never evaluated one. Admitted 2026-08-31 under
  the scope test as the mypy half of what `PL-ZN0N` and `PL-69J3` did for
  `noqa`. It is the weakest of the seven admitted together on 2026-08-31
  (#119), because it is inert reporting rather than a loop that misfires. It
  is the first to drop if this list needs shortening.
- PL-RWZV (S) The brief check tests for a literal marker, so an elaborated
  heading fails and an empty section passes. Admitted 2026-09-01 under the
  scope test: the misfire is in the same machinery as `PL-5YK8` above
  (`docket check`), and the brief check is the gate deciding whether an item
  may reach `ready` at all. Two of the captures triaged on 2026-09-01 carried
  exactly the empty-section stub it accepts.
- PL-H8MQ (S) `ROADMAP.md` states this release's entry count in six places, and
  its group and debt splits in three more, with nothing holding any of them to
  the list. Admitted 2026-09-01 under the scope test: a count that day found
  three different totals in this file at once (eighteen, thirty-one and
  thirty-two), so a session reading it to learn how much of the release is
  left got a wrong number. Every admission needs those counts corrected by
  hand, the four of 2026-09-01 (`PL-3576`, `PL-1Q3S`, `PL-RWZV`, `PL-H8MQ`)
  included.

**Two items on the approved list are not entries.** `PL-J3ZK` (restore the tag
provenance) and `PL-20ZR` (the workflow-before-features ordering is
re-explained every session) were on the list the project owner approved. Both
closed before the list was written here. Recording a closed item as a frozen
entry would make this release report a size that includes work it never had
to clear.

**Seven entries are marked `not-delegable`,** which is high for a release this
size and worth knowing before the work is planned. PL-J786 and PL-S4M2 change
GitHub repository configuration, which no session in this project can access.
PL-8HJ2 can only be proved by cutting a release. PL-ZQ9C leaves open a
migration choice that rewrites the provenance of every closed item. PL-1Q3S
fixes a repository-side habit whose effect shows only when a session ends, in
a hook that no session can read. PL-H7XN's test is that no rule was lost,
which needs a review of the file rather than a command. PL-CMCB's deliverable
is a verdict on ten suppressions rather than an exit code.

**What the freeze closes, and what it does not** (project owner, 2026-08-30,
`PL-QDN7`). This rule applies to every frozen list. The list is closed to new
*scope*: new behavior, new capability, or another workflow idea raised while
this release runs. It is not closed to the work that an entry already on the
list needs before it is actually done. A finding made after the freeze belongs
here if it addresses something that a frozen entry is fixing. It is recorded
together with what it completes. The freeze exists to fix a specific set of
problems. Shipping an entry known to be half-fixed would preserve the list's
length but defeat its purpose.

This is not a new rule. § "The gate is a snapshot, not a moving target"
already says that a finding which continues or completes an item inside the
frozen list belongs to the same list.

**The list is a scope, not a set of items** (project owner, 2026-08-31,
recorded in `docs/WORKING_NOTES.md` § "Open thread: the v0.2.8 gate's
membership test"). This scope test applied to v0.2.8's list only. The scope
decides membership, and the completion rule above is one case of the scope,
not the test itself. This release's scope is its goal, stated at the top of
this section: a development loop reliable enough to run two long milestones
through. The loop has to be reliable across the machinery the goal names. A
finding that a *named* piece of that machinery misfires is inside this scope
however late it is found, and whether or not it completes an entry. It
belongs in the scope because leaving it out would ship a release titled "the
workflow works" while the workflow it names does not work.

So "new scope" means a different goal, such as a new workflow capability, a
better tool that nobody is blocked by, or an idea someone had because this
release made them think of it. It does not mean a newly discovered instance of
the goal that is already frozen. A defect in machinery that is already named
is a third case, and the list admits it. The rule used to offer only two
cases, "new scope" and "completes an entry". On 2026-08-31, nine findings were
triaged and sent to the queue because they were neither. Yet seven of them
were defects in the digest, the release script, the merge path and the lint
gate, which this release exists to make reliable.

Two limits stop that rule from reopening the list for everything. First, the
finding must be a **defect** in machinery that this section's goal names. An
improvement to that machinery does not count, and neither does machinery the
goal does not mention. Second, the finding must be **workable here**. A
finding whose cause is outside this repository is captured and left off the
list, however well it fits. The reason is that nothing in the tree could close
such an entry, so the entry would keep the gate open forever.

A finding classed `safety` or `science` goes to Gate 0 rather than here. A `P0` finding is a
hotfix on its own branch under the `docket` skill, and it joins no list.

PL-68XK (check that a recorded commit hash resolves) is not admitted by
the completion rule. It predates the freeze, and it was left out of
the approved list deliberately. `PL-68XK` records why it was dropped.

### Definition of done

- Every entry on the frozen list above is `done`, or `dropped` with its reason
  recorded. `bin/docket wave` reports the split against `docs/items/`.
- `make check` passes: `ruff format`, `ruff check`, `mypy`, `pytest`,
  `docket check`, and `tools/doc_check.py`.
- The two entries that change repository configuration rather than the tree
  are PL-J786 (a green `checks` run required before merge) and PL-S4M2
  (squash-merge). Both are confirmed in effect on a real pull request, not
  merely described as done. *Note added 2026-11-09 (`PL-C25K`): only PL-S4M2
  shipped. PL-J786 was dropped on 2026-08-31 (project owner), for the reason
  its item records: the repository was then private on GitHub Free, where a
  ruleset is created but not enforced, so no rule could require the check
  before a merge.*
- No equation, parameter, numerical method, unit or displayed value has
  changed, and the v0.0.2 circuit and v0.1.0 sevoflurane reference tests pass
  unaltered. Three entries are permitted to reach into `src/` and `tests/`, and each
  is limited to what its brief describes. PL-020 may add type annotations.
  PL-ZN0N and PL-69J3 may add, remove or annotate `noqa` directives. If any of
  them turns out to require a change to a modelled value, that change is a
  finding for Gate 0 and a scoped item of its own. It is not this release's
  work.

### Explicitly out of scope for v0.2.8

- Anything on Gate 0's frozen list. This
  release does not touch that gate, and clearing it is still what v0.3.0
  ships.
- Any simulator change at all: `src/anesthesia_sim/core/`,
  `src/anesthesia_sim/app/`, and the scientific content of `docs/MODEL.md`. A
  release whose whole claim is that the loop is now reliable cannot also be
  the one that moves the model.
- Workflow capability beyond the entries on that list, which § "Debt gate:
  the frozen list" calls new scope. The queue holds
  more process items than this release ships, and they wait for the next
  release. A release that absorbs
  every workflow idea raised while it runs never ships.

## Completed: v0.3.0 - the foundation

### Goal

Clear the inherited backlog, so that feature work starts from a codebase whose
known defects are closed rather than carried forward. After this release, the
simulator does what it did before, but correctly. Its verification gate is
widened to cover the inputs that the interface can actually reach. Its failure
path can no longer leave partial state behind.

This release's contents are exactly Gate 0's items that fall outside the
teachable case's own scope. Those are the items listed under § "Debt gate: the
frozen list" in the v0.4.0 section below. Only findings that § "The gate is a
snapshot, not a moving target" re-admits may join that list, and seven did
after the freeze.

This release is a minor version rather than a patch, by a deliberate exception
that is recorded under § "Versioning decision" above. That exception covers
Gate 0 alone.

### Definition of done

- Every item on Gate 0's frozen list that is outside the v0.4.0 milestone's
  Required scope is `done`, or `dropped` with its reason recorded.
- `make check` passes: `ruff format`, `ruff check`, `mypy`, `pytest`,
  `docket check`, and `tools/doc_check.py`.
- No equation, parameter, or numerical method has changed, and the v0.0.2
  circuit and v0.1.0 sevoflurane reference tests still pass unaltered. Neither
  of the two safety items the Goal describes is licensed to change a modelled
  value. If either
  turns out to require one, that is a finding for the next gate and a scoped
  item of its own, not this release's work.

### Explicitly out of scope for v0.3.0

- Anything in the v0.4.0 milestone's Required scope, including the six gate-0
  items that the milestone clears itself.
- Any item captured after Gate 0 was frozen, except the findings that
  § "The gate is a snapshot, not a moving target" re-admits.
- New capability of any kind. A release whose whole claim is "the ground is
  now solid" cannot also be the one that moves the ground.

## Completed: v0.4.0 - the teachable case

### Goal

Make the model teachable. The science is sound, but when this milestone was
scoped its lessons were unreachable, for three measurable reasons. They are
stated below as they stood on 2026-08-25 (§ "Writing a milestone entry"). The
Required scope below addresses all three, and that is where this milestone's
outcomes are recorded.

- The run advances at 1x real time (`app/simulation_view.py`, one 0.1 s step
  per 0.1 s sleep). Yet the compartments that make uptake and distribution
  worth teaching have time constants of 135 min (muscle) and 42 h (fat) for
  sevoflurane at reference settings. So the reservoirs that cause
  context-sensitive emergence cannot be observed at all.
- The chart shows a rolling five-minute window, on an axis labelled in seconds
  and scaled to the vaporizer's dial maximum. So a 1 MAC run occupies the
  bottom quarter of the plot, and everything slower than the vessel-rich group
  scrolls away flat.
- Every value is a percentage of an atmosphere. So three agents whose MACs
  differ threefold are displayed as though their numbers were comparable.

The end state is this. A learner runs one case from induction to emergence.
Time is compressed so that they can sit through it, values are in the unit
clinicians reason in, and the time base spans a whole case. The learner changes
something and sees on the record when they changed it. Then they turn the
vaporizer off and watch the level come down against a labelled reference.

This milestone changes no equation, parameter, or numerical method. It is a
minor release rather than a patch because it adds a displayed clinical unit, a
new time base, and a run-rate control. These are capability boundaries in what
the interface asserts, even though the model behind them is untouched.

It promotes planned-milestone item 25 (playback multiplier) in full, and the
recording half of item 8 (control-input timeline). It does not promote item
26 (bookmarks) or item 12 (forking). But it is designed so that neither is
blocked. See § "Designed for forking" below.

### Debt gate: the frozen list

**Frozen 2026-08-25, the day this milestone was scoped.** Twenty open items
count as debt under § "The debt gate" above. Six of them are inside this
milestone's own Required scope, so this milestone clears them, as "Debt inside
the milestone's own scope" says. The other fourteen are cleared before
implementation begins. The list itself stays frozen. Each entry's item file
records how it closed.

**Cleared before v0.4.0 begins — 21 entries, 22 item ids.** At the freeze the
list held 14 entries and 14 ids. `PL-SWFM` was filed later that day and joined
`PL-Z4GF`'s entry. Seven entries were added after the freeze, as the first
three notes beneath this list explain. These 21 entries are exactly what
v0.3.0, the foundation release, ships. All of them were closed by 2026-09-02,
when that release shipped, and none was dropped.

Count entries, not ids. The PL-Z4GF/PL-SWFM entry below holds two ids for one
problem. So 21 entries and 22 item ids are both true, but only the count of
entries is the gate's size.

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
under § "What counts":*

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
- PL-N2N1 (S) The release script (`docket release`) does not update this
  file's version table or baseline heading. Added after the freeze; see below.
- PL-K79K (S) The session-start digest told every session to run
  `bin/docket triage`, which did not exist. Added after the freeze; see below.

*Documentation, performance, and the one decision that is the project
owner's:*

- PL-Z4GF **and PL-SWFM** (S) One entry holds two ids. PL-Z4GF closed the
  README half of its original scope. The remainder surfaced later under the
  separate id PL-SWFM: this file's own duplicated v0.2.3 table row and stale
  "Current baseline" heading. Under the presence rule of § "The gate is a
  snapshot, not a moving target" above (project owner, 2026-08-25), that
  problem was already inside this frozen scope. So it cleared here rather than
  at the next gate, regardless of which id or session it surfaced under.
- PL-010 (S) Stop rebuilding render objects on every frame
- PL-Y2GG (S) Apache-2.0, chosen by the project owner.

**Two entries, `PL-N2N1` and `PL-K79K`, added 2026-08-30 under the presence
rule, both cleared in the same batch that added them.** The rule in "The gate
is a snapshot, not a moving target" says that a finding re-enters this gate
when the problem it describes was already present at the freeze. That is true
whatever id the finding is filed under, and however long after the freeze
someone noticed it.

The first, `PL-N2N1`, continues the scope of the PL-Z4GF/PL-SWFM entry.
It is the same document drifting for the same reason. This time the finding is
the mechanism behind the drift, rather than one more instance of it. The
PL-Z4GF/PL-SWFM entry is the case that the presence rule was written for.

In the second, `PL-K79K`, the digest advertised a command that does not exist.
It had done so since `6f1b5b1` on 2026-08-24, the day before this list was
frozen. So by date the problem was present at the freeze. It is also a
`defect` by § "What counts" above, because the digest is a live mechanism that
`main` depends on, and it does not work.

Neither entry adds to the work that the gate has left, because both are
closed.

**Four entries added 2026-08-30 from an outside consultant's read-only review
of the repository.** A session filed the review's fourteen findings as items
(`820aa7b7`). All four re-enter this gate rather than being deferred to Gate
1, and they are the only findings from that review that do. They qualify on
both of the grounds that "The gate is a snapshot, not a moving target" allows:

- *By the presence rule.* Each one describes a problem that was present in the
  tree before 2026-08-25. `core/` has never had an upper bound on the
  simulation step. The splitting-error gate has kept one operating point
  constant since it was written. Nothing in the repository has ever been
  compared with a published human measurement. The unhedged
  `"Alveolar / end-tidal"` label has been in the interface since `74bec83` on
  2026-08-23, two days before the freeze.
- *By the safety/science exception.* PL-VP7N is `safety`, PL-SLHS is
  `safety`/`science`, PL-9Y42 is `science` and PL-NV9W is `safety`. § "The
  gate is a snapshot, not a moving target" names these classes as ones that
  re-enter the gate, whenever they were captured.

PL-NV9W was added three entries later than the others. `PL-NV9W` records
why.

Unlike the two entries above, these four do add to the work that the gate has
left, by four items. That is the rule working as intended, not the gate being
widened. Each is a statement that `docs/MODEL.md` already makes and that the
implementation does not keep. v0.3.0's whole claim is that the ground is
solid. Suppose that release shipped with a `must fail` that does not fail, a
release bound that a shipped trajectory exceeds, and no validation against a
human measurement. Then the claim would be untrue on the day it was made.

The ten other findings from the same review are in the queue and are cleared
at Gate 1. Each is either post-freeze in substance or classed outside the
exception.

**One entry admitted 2026-09-02, having been missed rather than deferred.**
PL-0MLQ (refuse a setting outside the documented supported input range) is
`safety`-classed at `P1`. It qualifies on both of the same grounds as the four
above. The four compartment setters have never enforced `docs/INTERFACE.md`
§ "Supported input ranges", so the problem was in the tree at the freeze. The
`safety` class also re-enters the gate regardless of presence. The item was
captured on 2026-08-30, the same day that those four were admitted by exactly
this rule. Yet this file named it nowhere: not here, not in v0.3.0's
out-of-scope list, and not among the ten findings deferred to Gate 1.

The pairing rule under § "What a frozen entry may take in" says that an entry
is worked together with the entry it completes, not after it. That rule cannot
be met here, because PL-VP7N, the entry that PL-0MLQ continues, shipped in
v0.2.7. So PL-0MLQ is listed as its own entry.

The failure was invisible to the tool as well as to the reader. PL-Y4Q4
records the diagnosis.

Like the four above, this entry adds to the work that the gate has left, by
one `M` item. To match, the step-2 size in "The timeline" moves from
`3 M, 17 S` to `4 M, 17 S`.

**One presence-qualifying finding deliberately deferred to Gate 1, and later
split.** PL-WB0X (split `simulation_view.py`) describes a module that has been
oversized since long before the freeze, so the presumption admits it. It was
deferred anyway. "The gate is a snapshot" permits that, provided the reason is
stated. The reason has two parts. The item is an `M` restructure of the
interface layer, with no connection to anything on the frozen list. And
v0.3.0's claim is that the release adds no capability and clears only
inherited debt. Pulling in
unrelated pre-existing debt just because it is old is the refilling-queue
problem. The gate replaced Phase 0 to solve that problem.

**That deferral stands and is not reopened here: none of this item shipped in
v0.3.0.** What was settled on 2026-09-02 (project owner) is where the rest of
the item goes. `PL-WB0X` records the placements that were weighed. Stages 1
and 2 are the two pure-module extractions. They are named in v0.4.0's Required
scope below, where they gate
that milestone's MAC unit and its chart work. Stage 3, the `SimulationView`
decomposition proper, is now queue item PL-B9PY. It stays at Gate 1, inside
v0.5.0, where the only thing that requires it is v0.5.0's two-runs-at-once
comparison.

**Cleared by v0.4.0 itself (6 items).** Each appears in Required scope below:
PL-DHV7 (MAC as a displayed unit), PL-VM40 (simulated time from a step count),
PL-F52R (the MAC-awake reference band), PL-ZRSP (the F_A/F_I trace), PL-R3KB
(agent selection discarding a run) and PL-011 (bounding the concentration
history). PL-011 was cleared by being `dropped` on 2026-09-05, with its reason
recorded. Beat 3 of "The cadence" accepts that as clearing, and the Required scope below
sets it out in full. Six of six.

Findings made while clearing this gate go to Gate 1. The exceptions are `P0`
findings and `safety`/`science` findings, which re-enter this gate.

### Required scope

- **Simulated time becomes an exact function of step count** (queue item
  PL-VM40). Today `SimulationState.elapsed_s` accumulates
  `+= simulation_step_s` on each step. Derive it from an integer step counter
  instead, and fix the step at 0.1 s. The run loop advances a fixed number of
  steps per tick and never catches up to the wall clock.

  *Landed 2026-09-04.* `SimulationState` holds the step count and the size of
  the step it is taking, and reports `elapsed_s` as their product.
  "Fix the step at 0.1 s" ended up fixed *per run* rather than hard-coded.
  A step that differs from the one a run has already taken is refused rather
  than counted, and a reset frees the run to take a different step. The
  interface's own cadence is still 0.1 s. A step-refinement study can still
  take a whole run at a smaller step. `docs/MODEL.md` states the guarantee,
  and the four things it does not cover, under § "The reproducibility
  guarantee".
- **A playback multiplier** (queue item PL-SN2C). It offers five rates (1, 5,
  20, 60, 300x). It is implemented as more steps per tick and never as a
  larger step. The current rate is visible beside the clock at all times.
- **The interface layer's two pure-module extractions** (queue item PL-WB0X,
  stages 1 and 2 only). Stage 1 moves the displayed-precision formatters into
  a module of their own that is free of Flet. Stage 2 moves the chart-series
  shaping into a module beside the Flet chart-series module (deleted with
  `PL-25KS`). Neither stage changes behavior, and both must still pass the
  existing view tests. PL-WB0X's brief names the modules. Stage 1 lands before
  the MAC unit below, because that item rewrites every formatter and extends
  the derivation in `docs/INTERFACE.md` § "Displayed precision". Today that
  derivation ends in a private static method on a Flet view class. So the one
  function that the specification reasons about cannot be read, cited or
  tested without loading the whole interface. Stage 2 lands before the chart
  work, because four items of this milestone touch the chart in the same
  place.
- **MAC multiples as a display unit** across every readout and both chart
  axes, alongside percent (queue item PL-DHV7). The agent's `mac_percent`
  provenance must be traceable from the display.
- **A case-length time base**: minutes rather than seconds, with a selectable
  scale plus a fit-the-run scale (queue item PL-SSBP). It was scoped as
  "15, 30 and 60 minute scales" and settled wider (project owner,
  2026-09-04): 15 minutes to 12 hours, geometrically spaced. The range was
  widened because the three-scale list was written while any scale longer
  than an hour cost more per frame than the budget allowed, and `PL-D9WD`'s
  bucket cache removed that limit. The gridline interval is derived from the
  selected scale rather than fixed. The axis labels carry their own units,
  such as `3m`, `1h30m` and `12h`. They do so because a bare number would mean
  minutes on one scale and hours on another, and it would look the same on
  both. "Fit run" is the default, and it always contains the whole run. Past
  the widest listed scale, the ladder of scales doubles. It never shows part
  of a case under a name that claims the whole of it.
- **A vertical scale denominated in MAC** (queue item PL-CC23) rather than in
  the vaporizer's dial maximum. A MAC scale is what makes a comparison across
  agents honest. It was scoped as "fits the run" and decided otherwise
  (project owner, 2026-09-04). A fitted axis rescales a rising curve in the
  middle of a lesson. The item's own requirement that the rule be stable
  within a run rules that out. The axis is fixed at 0 to 3 x MAC for every
  agent. Three is exactly desflurane's dial maximum expressed in MAC. A trace
  above the ceiling is named, rather than left to draw as a plateau.
  `docs/INTERFACE.md` s "The chart's vertical range is set in MAC, and
  fixed" carries the reasoning.
- **A recorded control-input timeline** (queue item PL-DR1Z). Every change to
  the fresh gas flow, the vaporizer dial, alveolar ventilation or cardiac
  output is stamped with the simulated time at which it took effect. Each
  change is held with the state it describes and marked on the chart. The
  changes are recorded as `(simulated_time, control, value)` entries rather
  than as a fixed struct of named controls. `PL-DR1Z` records why.

  *Landed 2026-09-04 as a frozen `ControlChange` record rather than a literal
  tuple, preserving the property this paragraph asks for.* `PL-DR1Z` records
  why the record keeps that property. See
  `docs/INTERFACE.md` § "The control-input timeline".
- **`SimulationHistorySample` keyed by substance, not by six flat named
  compartment floats** (queue item PL-W3DD). There is exactly one substance
  today, so this changes the representation, not the behavior. § "Designed for
  forking" below says why it matters.

  *Landed 2026-09-05. The change applied to the store and the chart's binding
  as well as to the record.* `PL-W3DD` records how. Nothing displayed changed.
  See `docs/INTERFACE.md` § "Interface boundary".
- **Changing agent becomes an explicit new case** rather than a selector
  that silently discards the run and its history (queue item PL-R3KB).
- **A MAC-awake reference band** on the chart (queue item PL-F52R). It shows a
  cited population median for return of responsiveness. It is drawn as a band
  and labelled as a population reference, never as a time prediction for the
  individual patient.
- **An F_A/F_I trace** (queue item PL-ZRSP), the ratio that the uptake
  literature plots. It carries an interpretive caveat. The trace means what
  the textbook curve means only while the inspired concentration is held
  constant.
- **A bounded concentration history** (queue item PL-011). It stops being
  optional once a four-hour run at 10 Hz records 144,000 samples.

  *Not landed, and not deferred either: dropped 2026-09-05, the day of the
  cut.* This is the one Required-scope entry that the milestone shipped
  without. `PL-011` records how it was dropped.

  Another item, `PL-2FM6`, deletes the store that holds the run's history
  (`RunHistory`) outright. Deciding an eviction rule for a store that is about
  to be deleted would be wasted effort, so the question was retired rather
  than answered. `PL-011`'s measurements are kept in `PL-T691`'s brief.

  This release is what made the history's growth reachable at all. Before the
  playback multiplier, twelve simulated hours meant sitting in front of the
  application for twelve hours. At 300x, twelve simulated hours take 2.4
  minutes and about 55 MB. A simulated day takes 4.8 minutes and 110 MB. A
  simulated week takes 34 minutes and roughly 770 MB. The score architecture
  (`PL-T691`) was not yet scheduled, and until `PL-T691` (v0.4.8) and `PL-2FM6` (v0.4.12) landed,
  that growth was unbounded and nothing tracked it. That is the cost of
  dropping the entry rather than deferring it.

- **A documentation sweep** (queue item PL-RCTQ). It covers the sections of
  `docs/MODEL.md` on the interface boundary, the minimum displayed outputs and
  the displayed precision, and it covers `README.md`.

### Designed for forking

Forking a case at a point on it, to compare two managements of the same
patient, is planned-milestone item 12. It is not built here. Item 12 requires
one property: a branch reproduces its parent exactly at every recorded sample
up to the branch point, element-wise rather than within a tolerance. That
property is expensive to retrofit and cheap to preserve, so this milestone
preserves it:

- Deriving elapsed time from an integer step count removes the order of
  accumulation. That order would otherwise make a resimulated prefix differ
  from a straight-through run.
- Fixing the step at 0.1 s regardless of playback rate removes the divergence
  that a changing step size would cause.
- Never catching up to the wall clock means that the number of steps taken no
  longer depends on machine speed. This is the subtlest of the three. Without
  it, every run would be irreproducible on a different computer.
- The control-input timeline is what lets a point *between* recorded samples
  be reached by resimulation at all.
- The substance-keyed history record (above) keeps item 6 (nitrous oxide)
  from reshaping the record that item 12's reproducibility proof is written
  against, after that proof exists.

Some things are deliberately *not* designed for in advance: per-compartment
agent amounts in the snapshot, a schematic view, run comparison, and a
snapshot policy. Those are cheap to add when their milestone arrives. Adding
unused structure now would be speculative generality rather than groundwork.
The test is whether retrofitting a feature invalidates recorded runs or
merely adds a field.

### Definition of done

v0.4.0 is complete only when all of the following are true:

- Two runs given identical inputs produce element-wise identical recorded
  history at every playback multiplier, and a test asserts this. The two runs
  also produce identical history on a machine of any speed.
- The simulation step is 0.1 s at every playback multiplier, and a test
  asserts this.
- A learner can read every graphed compartment in MAC multiples and in
  percent. The learner can trace the agent's MAC value from the display to
  its cited source.
- A three-hour case can be run, watched and read end to end in a few minutes
  of wall-clock time. The muscle and fat curves visibly diverge from the
  alveolar one.
- Every control change during a run is recorded with the simulated time at
  which it took effect, and is visible on the chart.
- The recorded history is keyed by substance rather than by flat named
  compartment floats (queue item PL-W3DD).
- Changing agent cannot discard a run unless the user is told what will be
  lost and confirms.
- The MAC-awake band and the F_A/F_I trace each show, at the point of
  display, what they do and do not assert.
- `docs/MODEL.md` states the MAC transformation, what a MAC multiple on a
  non-alveolar compartment does not claim, the reproducibility guarantee
  above, and the interface's new obligations.
- The v0.0.2 circuit, v0.1.0 sevoflurane and v0.2.0 multi-agent reference
  tests remain unchanged and passing. No equation, parameter or numerical
  method has changed.
- Ruff formatting and linting, strict mypy, pytest, and GitHub Actions all
  pass.

### Explicitly out of scope for v0.4.0

- Nitrous oxide, coadministered gases, and the concentration and second-gas
  effects (items 6-7). This milestone is deliberately taken ahead of them.
  See the note in "Development pathway".
- The multi-substance patient state (Phase 1). Nothing here requires it. The
  view already consumes an immutable snapshot, so the MAC readout is the only
  piece that changes shape when a second substance lands.
- The anesthesia-machine abstraction, interlocks, agent switching with
  residual washout, direct injection, and end-tidal control (items 1-5).
- Run bookmarks (item 26), forking (item 12), save/load (item 9), replay
  (item 10) and run comparison (item 11). This includes the replay half of
  item 8's timeline. Only recording is in scope.
- A schematic compartment view (item 27) and agent cost (item 28).
- A second patient, weight-based scaling, age-adjusted MAC, dead space,
  airway sampling delay, or any depth, BIS or effect-site model.
- Horizontal panning of the chart window (queue item PL-Z7LY). The fit-run
  scale makes panning optional rather than necessary.
- Stage 3 of the interface layer's decomposition, which is the
  `SimulationView` decomposition proper (queue item PL-B9PY). Stages 1 and 2
  are in scope above. Stage 3 stays at Gate 1, because only v0.5.0's
  side-by-side comparison of two branches needs it (project owner,
  2026-09-02).

## Completed: v0.4.26 - the interface moves to Qt

### Goal

**Run the same simulator on PySide6 + pyqtgraph, and lose nothing a learner can
do today.** Since 2026-09-16 (`PL-L9RD`), the goal no longer includes the
interface pass (planned-milestone item 33).

The measured case for the port is in `docs/WORKING_NOTES.md` under "Measured on
real hardware". The slowness that opened the toolkit question (`PL-QXSB`) is
gone: the owner reports that the Flet build has not been noticeably slow since
`PL-2FM6` removed the run's sample store. The case therefore does not rest on
that slowness. Four grounds remain:

- **Input latency on Qt is 0.85-2.46 ms at the 90th percentile, against
  Flet's 20-30 ms.** The Qt figure was measured on the owner's Mac on
  2026-09-10, and the Flet figure in the container on 2026-09-08. Latency is
  what "laggy" referred to. The gap comes from the mechanism, not the
  hardware: a control-tree diff blocks Flet's event loop every frame, and Qt
  has no diff.
- **The toolkit choice settles a safety decision** (`PL-GS3R`). The cheapest
  way out of the chart's 0.26 MAC of chord error is more columns. On Qt, more
  columns cost 49.4 ms of a 200 ms budget (measured 2026-09-10). On Flet, the
  diff alone costs about 78 ms for the same columns, before its client renders
  anything (computed from `PL-YSZN`'s 24.5 µs per point).
- **On Qt, a session can visually confirm a chart change** (`PL-2QMK`). The Qt
  spike (`PL-55DH`) has shown this: it writes a PNG of the running interface in
  the same container where Flet's renderer cannot load. Most of
  `presentation-safety` waits on that ability.
- **Headroom** is needed for the schematic (planned-milestone item 27). The
  schematic is a second large visual surface, on a toolkit that charges for
  each control present in each frame. (This was written "v0.6.0's schematic"
  until 2026-09-16, when item 34 took that number and the schematic moved to
  v0.8.0. It is named by item number here, per the `PL-YVM1` rule this port
  already adopted, so it cannot go stale again.)

### Required scope

1. **The chart** (queue item `PL-G59B`). This covers the six compartment
   traces, the two clinical references, both axes, the control marks and the
   wash-in plot, all on pyqtgraph. `PL-GS3R`'s chord-width column rule lands
   here rather than separately. The port is what makes that rule affordable,
   and that is why `PL-GS3R` is sequenced behind this item.

   *`PL-YVHK`, the chart's hover readout, lands here too* (project owner,
   2026-09-14, splitting `PL-YLKR`). What the readout shows is already decided.
   `docs/INTERFACE.md` § "The chart's hover readout: what the tooltip may show"
   derives it, in v0.4.x. So this is a build against a written specification,
   not a design round inside a port. **It is parity rather than new
   capability.** In pyqtgraph, a scatter plot ships with hover turned off
   (`ScatterPlotItem` has `hoverable` set to `False`), and a plotted line has
   no hover at all. A port that said nothing about hover would therefore
   *lose* the Flet build's hover instead of reproducing it. Building the
   readout on Flet first was refused, because on Flet the same content takes
   roughly 1 870 per-point strings, and here it takes one format callable. The
   cost was measured on 2026-09-08 (`PL-KP7H`) and is recorded in `PL-YVHK`.
2. **The dashboard** (queue item `PL-25KS`). This covers the readout row, the
   parameter controls, the agent selector, the transport, the new-case dialog
   and the notice banner. They live in `app/simulation_view.py`, which was
   4 321 lines when measured on 2026-09-14.

   *The dashboard reserves space for planned-milestone item 34 and builds none
   of it (project owner, 2026-09-12).* Each of those surfaces becomes an
   independent widget inside nested `QSplitter`s rather than a fixed layout.
   **The splitter handles stay inert.** Item 34 is what makes them live, and
   it adds the split/join affordance, the workspace tabs and the savable
   presets.

   The reservation costs almost nothing, because another item already requires
   the components it needs. `PL-B9PY` decomposes `SimulationView` in v0.5.0 and
   records that "the Qt view is built decomposed from the start". So the only
   thing the reservation decides is the container those components go into:
   nested splitters rather than fixed layouts. The alternative is to lay out
   every panel twice. That is this milestone's argument for *reserving* space
   for item 34 here rather than building it. The reservation stayed when
   item 33 left this port, because this port does build a layout container,
   once.

   *The inert handles are deliberate.* A draggable splitter would let a learner
   do something they cannot do today, so live handles would be new capability.
   § "Fixes this port carries" excludes new capability "whatever its size".
   That exclusion keeps live handles out, as it kept out the show/hide control
   for the clinical references and control marks (`PL-16ZC`). Parity means
   identical to the Flet build except for the fixes that section lists, and it
   can be checked only while that list stays closed. Making the handles live is
   item 34's first step and costs one line.
3. **The theme** (queue item `PL-L9RD`). `app/theme.py` is re-expressed for
   Qt. The six compartment colours and their dash patterns stay intact, and
   both tools that read the file still describe it. **The interface pass is
   not here.** Item 33 left this port on 2026-09-16 and is its own row again.
   Later the same day it moved after item 34 (`PL-PHKP`). Where the Qt styling
   layer lives is left open on purpose, and
   § "Explicitly out of scope for v0.4.26" lists it.

   *This port absorbed planned-milestone item 33, and no longer does* (project owner,
   2026-09-16, on `PL-L9RD`). The argument was that restyling a dashboard that is
   about to be rewritten is the same work done twice. Porting rewrites
   `theme.py`, every layout and every density decision regardless. So palette,
   type scale, spacing rhythm and layout would be decided once, during the port,
   rather than applied to Flet and then again to Qt.

   *The premise was measured against the port that actually landed, and it did not
   hold.* `ae8fc7bc` (`#588`, `PL-25KS` and eleven others) changed `app/theme.py`
   by 10 insertions and 29 deletions. The only constant whose value it touched is
   one it removed: `ELAPSED_VALUE_WIDTH`, a Flet layout width with no Qt
   equivalent. Not one palette entry, type size, padding or radius changed.
   Nothing in `BACKGROUND`, `PANEL`, `PRIMARY`, `ACCENT`, `INK`, `MUTED`,
   `WARNING`, `APP_TITLE_SIZE`, `METRIC_VALUE_SIZE`, `PAGE_PADDING`,
   `PANEL_PADDING` or `PANEL_RADIUS` has moved since 2026-09-10. The port
   re-expressed the **widgets** and carried the **visual language** across intact.
4. **The two checks that read the theme** (queue items `PL-BXB2`, `PL-V53R`
   and `PL-0PJG`). Each check now reads every module under `app/` and names
   none by path, and an empty measurement set is an error. `PL-JRS3` records
   how the port would have broken them.
5. **Packaging and dependencies** (queue item `PL-3SQT`). PySide6-Essentials,
   pyqtgraph and numpy are added, and `flet` and `flet-charts` are removed.
   numpy arrives as a dependency of pyqtgraph. That reopens the scope of
   `docs/WORKING_NOTES.md` § "Decided: no numpy" but does not contradict its
   conclusion. numpy stays undeclared (`PL-3SQT`), because pyqtgraph installs
   it and nothing under `src/` imports it.
6. **Headless rendering tests** (queue item `PL-YCWZ`). These tests check the
   real interface as drawn, which `PL-2QMK` has been waiting for, and they make
   the rest of `presentation-safety` workable. With this port ahead of v0.5.0,
   they also mean that the two-branch overlay (`PL-8PSW`) is the first large
   display this project builds with a rendering check already in place.
7. **Deletion** (queue item `PL-7SVX`). The Qt spike tree is deleted, and so
   is every Flet import. `PL-C92D` retires the Flet frame-cost table that
   predates the port.
8. **The queued fixes named below** (queue items `PL-3355`, `PL-Q4VH`,
   `PL-THXF`, `PL-W8DQ`, `PL-TG60` and `PL-005`), under the rule stated there.
   `PL-HWW1` records why they are named here as well as in the declaration slot.

### Fixes this port carries, and why that is not scope creep

**Asked by the project owner, 2026-09-10**: "if we already had things we needed
to fix, wouldn't it make sense to fix those as part of the port, and not just
reintroduce old bugs still needing fixed?" Yes. The rule is narrow enough to
keep this release a patch.

**The rule: a queued fix rides the port when the port rewrites the code the
defect lives in, and it changes nothing a learner can do.** Everything else
waits. This is not a matter of taste. It follows from what a port is. Porting a
known defect means deliberately reproducing it in code that is being written
from scratch, and then rewriting the same lines again to fix it. The fix is
cheaper inside the port than before it or after it.

**What it does not license.** New capability stays out, whatever its size.
That is what keeps the patch argument in § "Versioning decision" true. A
defect in `core/` or in the Flet-free modules also stays out. The port does not
touch those modules, so fixing a defect there is unrelated work carrying this
milestone's name.

**The enumeration is the point.** "Parity with the Flet build" is this
milestone's checkable definition of done. A port that also changes behaviour
cannot be compared with the old build to prove that nothing was lost. So every
carried fix is named here in advance, and parity means *identical except for
this list*. That is stricter than parity without a list, not looser.

**Defects in the rewritten surface.** Reproduce none of these:

- `PL-3355` - the readouts wrap their value onto a second line at some widths.
- `PL-Q4VH` - the percent axis is labelled at a different interval from the
  gridlines it rules.
- `PL-THXF` - the legend swatch is a solid bar for a trace that is dashed, so
  the legend misdescribes the chart it explains.
- `PL-W8DQ` - the four slider active tracks miss the WCAG non-text minimum.
- `PL-TG60` - six decimals printed on an exhaust integral good to three.
- `PL-005` - the startup window is full-screen rather than sized and centred.

**Decisions the port has to make anyway**, so they are made deliberately rather
than by default. `PL-YTX9` decides whether a hidden trace keeps its legend
entry. `PL-CZFY` and `PL-Q4M4` concern the elapsed-time readout, which shows
seconds while the axis shows hours. `PL-LL9Y` concerns how the warning and
alert colours compare with the medical alarm-colour convention. `PL-2K1R`
concerns an interpretation disclaimer beside the use disclaimer. That disclaimer
states that the readouts and traces are modelled rather than measured. It is
text the dashboard states, not a control a learner operates, so it is a
decision rather than capability. The project owner added `PL-2K1R` to this
list on 2026-09-14.

**The show/hide control for the clinical references and the control marks
(`PL-16ZC`) is out** (project owner, 2026-09-10), and it shows where the line
is. It is small, and it sits squarely in the rewritten surface. But the control
does not exist today, so it is new capability, and the rule admits fixes, not
features. It stays a queue item on its own merits.

**The show/hide control is nonetheless sequenced behind this port** (project
owner, 2026-09-14, on `PL-NR2K`). That follows from the line between fixes and
features, and does not reverse it. A fix in the rewritten surface rides the
port, and a *feature* in the rewritten surface waits for it, because either
one written on Flet first would be written twice. Gate 1
§ "Sequenced past v0.5.0, so not clearable before it begins" lists the
disposition, and `PL-16ZC`'s brief records the reasoning. `PL-16ZC` is not in
this milestone's Required scope. It waited for the Qt chart (`PL-G59B`), was
then built against it as an ordinary queue item, and shipped in the v0.4.26
tag (#597).

### Items this port moots or transforms

Overlooking one of these items causes no defect, but it costs work that is done
and then thrown away.

- **The port keeps the design of the decomposed simulation view (`PL-B9PY`),
  not its code.** Gate 1 places `PL-B9PY` under § "Cleared by v0.5.0 itself".
  Decomposing `SimulationView` so that two runs render is what the
  branched-run milestone *is*. The decomposition therefore could not wait for
  the port, which was then due to ship after v0.5.0, without deferring the
  MVP. It landed on Flet on 2026-09-14, before this port moved ahead of
  v0.5.0, so the move did not reopen the question of which should come first.
  The Qt view is built decomposed from the start, so `PL-B9PY`'s design is a
  required input to the dashboard rewrite (`PL-25KS`) rather than a pass to
  redo. Writing the decomposition's code twice was the accepted price of
  shipping the MVP first. Because the shape the Qt view needs is already
  designed and reviewed, the move costs less than it would have before
  `PL-B9PY` was promoted on 2026-09-08.
- **A Flet defect in the colours of disabled controls (`PL-NGF7`) was deferred
  to this milestone** (project owner, 2026-09-10). When Material disables a
  control, the control takes every colour from the Material theme rather than
  from `theme.py`, so the contrast check (`tools/contrast_check.py`) cannot
  measure those colours. It closed `done` in v0.4.26 (#621). Its brief records
  the deferral and the outcome, and v0.5.0's
  § "Deferred to v0.4.26, because the port dissolves the defect" lists it.
- **The accessibility question becomes a different investigation**
  (`PL-F0L8`). It asks what accessibility Flet's rendering backend can
  deliver. After the port, it is a question about Qt's accessibility support
  (`QAccessible`) instead.
- **`PL-7J96` ("nothing in this repository draws the interface") is `dropped`
  as superseded.** It asks for what the headless rendering tests (`PL-YCWZ`)
  now do, and the decision went to `PL-YCWZ` (project owner, 2026-09-13).
  Before the decision, the Qt spike had already rendered the interface
  offscreen inside the web container, so `PL-YCWZ`'s capability was shown
  rather than assumed. `PL-7J96` would have built a Playwright renderer for
  the interface that this milestone replaces. The decision accepted that the
  shipped Flet build had no automated check that drew it, and so none that
  would catch a wrapped label, until the port deleted that build. The two
  defects that `PL-7J96` records are filed and dispositioned separately, so
  what is given up is the gate, not the fixes. `PL-MBP6` was blocked on
  `PL-7J96` and now depends on `PL-YCWZ`.
- **Two coverage items concern files that this milestone replaces.**
  `PL-NC2P` and `PL-YMY7` cover the paths in `app/main.py` and
  `app/simulation_view.py` that build the Flet interface.
- **`PL-027`** confirms the per-frame slider write-back on a live Flet client.

### Definition of done

- Every capability the Flet build has, the Qt build has. There is no
  regression a learner can see. This is checked against the readout labels,
  the hedges that `PL-NV9W` requires, the MAC axis, both clinical references
  and the control timeline.
- `make check` is green, including the two theme-reading checks, which are
  re-pointed rather than passing vacuously.
- A headless rendering test asserts on the real interface, and `PL-2QMK` closes
  on it.
- `PL-GS3R`'s worst drawn departure is re-measured at every rung of
  `TIME_BASE_LADDER` and recorded in `docs/MODEL.md`.
- `docs/ARCHITECTURE.md` describes the interface that exists.
- The Qt spike tree is deleted and no module imports Flet.

The cut (`PL-06YW`, 2026-09-17) checked each criterion against a closed item.
`docs/MODEL.md` records `PL-GS3R`'s departure for four of the ladder's ten
rungs (15 min, 1 h, 4 h and 12 h), not for every rung.

### Explicitly out of scope for v0.4.26

- **Any new learner-facing capability.** This release adds none, which is what
  makes it a patch. This is the line that the carried-fix rule above is drawn
  against, not an exception to it. **One item landed against this line and did
  not cross it**, at the project owner's direction. The two-run overlay is
  built. But `fork_at`, `fork_points_s` and `branches` have no caller outside
  `app/controller.py`, so nothing in the interface creates the second run that
  the overlay draws. The display shipped ahead of the capability it displays.
  The id and the reasoning are in the cut item that the v0.4.26 row of
  § "Versioning decision" names in its Details cell, and deliberately not here. `docket next` reads this heading, so an id named
  under it is treated as out of scope.
- **The branched run.** v0.5.0's bookmarks and forking belong to that
  milestone, and this one does not touch them. **Its comparison *display* is
  the exception above.** The exception is drawn here rather than in v0.5.0, so
  that the largest new visual surface in the project was built once, on Qt, in
  a container a session can look at. That is one of the three grounds this
  file already gave for moving the port ahead of v0.5.0.
- **`core/` and the `app/` modules that never imported Flet.** The port is
  tractable only because `core/`, `app/controller.py`, `app/formatting.py`,
  `app/chart_time_base.py`, `app/playback.py`, `app/wash_in.py` and
  `app/control_timeline.py` survive untouched. A check enforces that boundary
  (`tools/import_boundary_check.py`). The spike proved it by driving the real
  controller (`SimulationController`) with no adaptation at all.
- **Where the Qt styling layer lives, left open on purpose** (`PL-Y4YX`). When
  counted on 2026-09-16, 27 places in the code called `setStyleSheet` with CSS
  strings composed from `app/theme.py`'s constants, with partial helpers in
  the view modules. Yet `theme.py`'s own comment forbids it to import a
  toolkit. The port shipped with the styling composed in place, and `PL-Y4YX`
  moved it to `app/stylesheets.py` in v0.5.24.
- **The schematic** (planned-milestone item 27). This port makes it affordable
  and does not begin it.
- **The area system** (planned-milestone item 34, v0.6.0). Required scope item
  2 reserves space for it, as nested splitters with inert handles, and does
  not build it. Making those handles live is that milestone's first step.
- **Flet's web target**, which is given up rather than reimplemented. Nothing
  ships it today.

### Why it moved ahead of v0.5.0 and took a patch number

**Scoped 2026-09-10**, following `PL-QXSB`'s decision on the same day.

**Moved ahead of v0.5.0 on 2026-09-14** (project owner, 2026-09-14, on `PL-RKWB`). Before
that, it sat after MVP, which is where it was placed when it was scoped. The
question put was whether v0.5.0's work would have to be redone after the port.

**A count of v0.5.0's items answered whether its work would be redone after the
port.** Gate 1 used the same method on 2026-09-14, when the general form of
this question was asked about its entries, as `PL-16ZC`'s brief records.
v0.5.0 had eight open Required-scope ids. **One** is wholly inside the
surface this port rewrites: `PL-8PSW`, the two-branch overlay. Two have a slice
there: `PL-RD3B` and `PL-LPLD`, and the durable halves of both are in
`app/controller.py`. Five never touch it at all: `PL-CTD7`, `PL-B8MK`,
`PL-Z3W6`, `PL-W7H9` and `PL-49R8`. **So the premise of the question did not
hold, and the move was taken on three other grounds:**

1. **The two-branch overlay (`PL-8PSW`) would otherwise be built blind.** It
   carries more presentation-safety risk than any other item in v0.5.0. Six
   channels are already spent, the design rests on a two-compartment cap, and
   every curve must be attributed to its run. No session in the web container
   can visually confirm a chart change (`PL-2QMK`), because Flet's renderer
   fetches Flutter assets and the egress proxy denies them. The Qt spike
   rendered offscreen in that same container once `libegl1` was installed
   (`PL-VHLZ`). The port has since added headless rendering tests over the
   real interface (Required scope item 6). Their Flet counterpart (`PL-7J96`)
   is `dropped` as superseded, so the Flet build had no automated check that
   drew it until it was deleted.
2. **Two `P1` `safety`-classed items sat blocked behind this port.** They are
   `PL-GS3R` (0.26 MAC of drawn departure at the 12 h base, worst in the steep
   early wash-in) and `PL-YVHK` (the hover readout). Both are designed, and
   both waited only on the toolkit. Ordering v0.5.0 first would have kept them
   blocked for the whole of a milestone.
3. **The parity target is smaller now than it will ever be again.** This
   milestone's definition of done is parity against a **closed** enumeration.
   Landing v0.5.0 first would add compare mode, the largest new visual surface
   in the project, to the list that has to be checked.

**Apply what was decided, which is narrower than "move the milestone".**
Nothing new is built in `app/simulation_view.py` or the Flet chart-series
module before this port. v0.5.0's port-neutral spine is untouched and still
ships on its own schedule. Only its display half waited for the port. The
display half's two open items were the two-branch overlay (`PL-8PSW`) and
`PL-LPLD`'s bookmark list. The overlay shipped inside the port, and `PL-LPLD`
shipped in v0.4.33.

**This port takes a patch number, although it rewrites the whole
dashboard.** § "Versioning decision" chooses a release's number by the
capability boundary that the release crosses. After this port, a learner can do
nothing that they could not do before. The interface-pass row made the same
argument for the restyle it replaces. v0.2.8 is the precedent for machinery at
this scale taking a patch number. It had thirty-eight frozen entries and no
simulator change.

**This port takes a section, as no other patch in this project ever has.** It
rewrites the 5 133 lines in the three Flet modules (counted 2026-09-14), and it
has its own goal, required scope, definition of done and out-of-scope list. By
this file's own test, that makes it a milestone, whatever number it ships
under. The port's first reason for a section was mechanical and stopped
applying on 2026-09-14 (`PL-L09X`).

**Gate 2's freeze is deferred, deliberately, and moving this port did not
disturb it.** Gate 2 freezes when v0.5.0 ships. This port takes no gate of its
own, as was already true when it sat after MVP, so its own findings go to
Gate 2 alongside v0.5.0's.

**What the move does change is Gate 1, and in the direction `PL-D143`
asked for.** Nine of the twelve entries that gate could not clear were waiting
on this port. With the port ahead of v0.5.0, they clear before the milestone
they gate begins, instead of after the release that follows it. Gate 1's own
§ "Sequenced past v0.5.0" records the revised disposition.

## Completed: v0.5.0 - the case you can branch

**What this milestone is.** It keeps its number and its meaning. It is the
release that crosses the branching capability boundary, and the Qt port, which
moved ahead of it, crosses none.

**This milestone's display half is built on Qt.** The Qt port moved ahead of
this milestone, so `PL-8PSW` (the two-branch overlay) and `PL-LPLD`'s bookmark
list are built once, on pyqtgraph, rather than on Flet and then again.
§ "Completed: v0.4.26 - the interface moves to Qt" gives the decision, the
count behind it and the three grounds.

**Nothing else about this milestone moved with the port** (2026-09-14). The
milestone shipped on 2026-09-21. Its port-neutral spine was untouched by the
port:

- `PL-CTD7`: a bookmark crossing halts the run on the step that crosses it,
  with a distinct outcome for a mark never reached (v0.4.35).
- `PL-B8MK`: a branch can be taken at a bookmark instant (v0.5.0).
- `PL-Z3W6`: a test asserts that a branch reproduces its parent up to the
  branch point (v0.5.0).
- `PL-W7H9`: `docs/MODEL.md` and `docs/ARCHITECTURE.md` state what a
  comparison asserts and what it does not (v0.5.0).
- `PL-49R8`: a rule against bringing back a sample store (v0.5.0).
- The durable half of `PL-RD3B`: the controller's run vocabulary, moved into
  `app/run_series.py` (v0.4.26).
- The durable half of `PL-LPLD`: time bookmarks and MAC targets as two lists
  (v0.4.33).

The Required scope changed after 2026-09-14: `PL-MN4J` joined on 2026-09-16,
`PL-2FM6` and `PL-8LXM` left on 2026-09-19, and `PL-VKJW` joined the same
day.

### Goal

Make the comparison possible. v0.4.0 made one case observable, with
compressed time, clinical units and an axis as long as the case. A single
curve teaches a curve. It cannot teach *why* the curve moved, because that
needs a second curve that differs in exactly one thing. On 2026-09-06, the day
this milestone was scoped, three gaps stood in the way:

- There is no way to stop a run at a target. So the playback multiplier, which
  made a twelve-hour case reachable, cannot be used for anything precise. A
  learner who compares gas-management strategies has to watch the clock and
  pause by hand. At 300x, a hand pause overshoots by minutes of simulated time.
  It lands somewhere different on every attempt, and the learner cannot return
  to it.
- There is no way to take two different managements from one point in a case.
  The only route available is to build the case twice. The two runs then
  differ in everything that was not reproduced identically. That is the one
  thing a comparison must not do, because the learner who reads it cannot see which differences
  they caused.
- There is no way to display two runs at once. `SimulationView` binds one
  controller. The readouts, the chart traces, the clinical references and the
  control marks each assume that a single run sits behind them.

The end state is as follows. A learner runs a case, marks the decision point,
forks the case there, manages the two branches differently, and reads both on
one time axis. The branch point is marked. Every curve can be traced to the
run and the settings that produced it. The history before the branch point is
identical in the two branches.

**This milestone completes the MVP** as § "What MVP means here" defines it. It
is a minor release rather than a patch because it crosses a capability
boundary that the four releases before it did not cross. The application comes
to hold more than one run, and it asserts a relationship between them.

The milestone promotes planned-milestone item 26 (bookmarks), item 12
(forking), item 11 (side-by-side comparison), and the replay half of item 8,
which is the resimulation driver only. `PL-T691` delivered the applied
timeline that the driver would have replayed, and the driver itself was taken
out of this milestone's scope on 2026-09-14 (`PL-J2TD`). A replay control that
the user sees is item 10. It stays behind item 9's save/load, which is out of
scope here (project owner, 2026-09-06).

**It changes `core/`, and it changes what the numerical method can be asked,
not what it computes.** The exact matrix exponential landed ahead of this
milestone (`PL-GS5X`, pull request 376). The score architecture below turns a
run from a sequence of applied steps into a closed-form function of its
control-input timeline. The governing equations, the parameters and their
exact solution do not change. What changes is that the state at a given time
in a run can be computed without stepping the run to that time. This is what
makes a branch's history before the branch point *the same object* as its
parent's history, rather than a reproduction. Item 12 requires that property.

Beneath the three gaps above sits a fourth problem, which is a debt rather than
a gap: the run's sample store has no size limit. `PL-011` was dropped on
2026-09-05 on the promise that the score architecture would remove that store
rather than put a limit on it. Because a comparison holds two runs, this is the
milestone where the promise is kept, or else the debt doubles. `PL-2FM6`
removed the store in v0.4.12 (2026-09-08).

### Debt gate: the frozen list

**Gate 1, frozen 2026-09-06, the day this milestone was scoped.** This list holds every
open item that counts as debt under § "The debt gate" above. It is by a wide margin the
largest gate this project has held: Gate 0 held twenty-one items, and v0.2.8's frozen
scope held thirty-eight. The group headings below state its size, and so does the
timeline row that names this release. An automatic check compares those figures with
the list.

**The list has three groups, and only the third is a precondition for starting this
milestone.** The first group is the remaining work of the `v0.4.x` track, the second is
debt inside this milestone's own Required scope, and the third is everything else.
"The timeline" places the first group *ahead* of this gate, and it ships as a patch
rather than inside this milestone. That looks like an exception to
"A gate does not get a version", but it is not one. When this list was frozen, the
plan had already placed the `v0.4.x` work on an earlier step, and a gate cannot go back
and claim a step that the plan had already reached. The milestone clears the second
group itself, as "Debt inside the milestone's own scope" says. The third group is
cleared before implementation of this milestone begins.

**Fifteen items were untriaged at the freeze, so the list could not decide
them.** An untriaged item has no `classes` yet, so nothing can say whether it
is debt. Freezing against the store means freezing against what the store
knows. That leaves a hole in the gate, not an exemption, and
"The gate is a snapshot" closes it. Each of these items was captured
*before* this freeze, so the problem it describes was already present at the
freeze. Any of them that the triage pass classes as debt re-enters this gate
rather than waiting for Gate 2. The list below records what could be decided
on the day. A re-entering item is added to it with the date and the reason,
exactly as v0.4.0's three post-freeze notes record theirs.

**How the third group is meant to be worked.** The third group splits almost
evenly between the product and workflow lanes (§ "Terms this file uses"). The two halves share
no files, so they are worked at the same time in two sessions rather than
one after the other. That is what the lane split was built for. The product
half must also be ordered against the milestone's own work. Much of it names
`app/controller.py`, `core/` and `docs/MODEL.md`, which `PL-T691`
restructured in v0.4.8, on 2026-09-07, the day after the freeze. Clearing it *after* that restructure would mean diagnosing each
item again against code that had moved. That is exactly the cost that
"The debt gate" names when it opens. It is also the reason this list was
frozen whole rather than narrowed (project owner, 2026-09-06).

**Cleared by the `v0.4.x` track, ahead of this gate — 7 entries**

**Two moved here from "Cleared by v0.5.0 itself" on 2026-09-08, and two added** (project
owner). The reason is a measurement rather than a preference, and `PL-4RBD`
records it. `PL-4RBD` is now `P1`, `safety`. The sampler had to arrive before
the safety item could close properly, and `PL-2FM6` came forward with it. Both have
since left Required scope (`PL-C4RS`, 2026-09-19). The gate total rises by two, for `PL-ZX12`
and `PL-GS3R`. `PL-2FM6` and `PL-8LXM` moved between groups rather than
joining the gate.

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

**`PL-YDKJ` is here as a consequence of `PL-2FM6`, not as a nineteenth
Required-scope entry** (moved 2026-09-08, `PL-YXXG`). It now carries
`blocked-by: PL-2FM6`, so no check has to work out that dependency from the
prose again. `PL-YXXG` records the reasoning.

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
  `PL-2FM6` supersedes this item by deleting the store that has a cadence. After that
  lands, there is no recording cadence to state, and the simulation step
  (`SIMULATION_STEP_S`) plays one role again. The item's lasting half is the owner's
  chart-faithful-only decision of 2026-09-05, which was recorded nowhere else. It is
  now written into `PL-2FM6`'s **Done when**, and an automatic check keeps it there.
  The item counts as cleared. `PL-4RBD` is deliberately **not** dropped with it.
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
- PL-XLQ5 (M) The orphaned report asks whether the base ever held the branch's exact blob, so a path superseded on either side reads as work the squash left behind
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

Neither lane can complete these items on its own. So each one needs a session
that can work on the whole change across both lanes.

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

The 2026-09-06 triage pass classified the eleven captures that were still
untriaged when this list was frozen earlier that day. Eight of them are debt.
Each of the eight describes a problem that already existed at the freeze but
could not be decided then, so they re-enter this gate under
§ "The gate is a snapshot" rather than waiting for Gate 2. None of them is inside
this milestone's Required scope, so all eight clear before implementation begins.
Five are in the product lane or apply to both halves, and three are in the
workflow lane.

**Adding eight entries closed the hole that untriaged items left in the gate.**
`PL-NBWP` and `PL-NBCJ` are `P1` `safety` and `science` findings, on the playback
burst's control resolution and the step size. `PL-B1WW`, a `P2` `test` finding,
concerns the reference gate's oracle. That is the class of finding this rule exists
to catch rather than defer.

The session that scoped this milestone also captured four items of its own.
`PL-QYPX` and `PL-3P2P` closed with the change that scoped this milestone.
`PL-D9GM` is `planning`. `PL-M26Q` is `infra`, a tooling capability nobody has
built, and "What counts" says explicitly that such an item is not debt. So none of
the four adds to the list.

- PL-NBWP (M) app/playback.py claims a faster playback is 'never a modelling one', but the uninterruptible tick burst makes control resolution multiplier x 0.1 s - 30 s at 300x
- PL-NBCJ (S) Decide whether MAXIMUM_SIMULATION_STEP_S should move to 0.05 s so an abrupt manoeuvre's timing stays inside one parameter SD
- PL-74R0 (M) core/ still holds four compartment-level advance methods that the coupled step no longer calls
- PL-R460 (M) The exact step costs 27 us against the split's 18 us per step at held settings, and 1.2 ms on every settings change
- PL-5TRV (M) bin/docket stranded calls an open pull request's branch merged-and-abandoned when another PR independently wrote the same docket record pr: lines, and its recovery would discard the branch
- PL-B1WW (S) The reference gate's oracle step is not converged during a transient, so 86-99.8 percent of what it reports is the oracle's own RK4 truncation rather than the shipped step's error
- PL-RC0M (S) "A blocked item's verify: command is never replayed, so it can rot unnoticed and redden whichever pull request unblocks it"
- PL-1KTV (S) docket.toml counts .github as the workflow lane but apparatus-standard.md's paths do not, so 500 lines of workflow comments sit under the simulator's standard by default

**Added 2026-09-06 after `PL-NBWP` closed — 2 entries**

These are the two captures that `PL-NBWP`'s own session left behind. They were
triaged on 2026-09-06, once `PL-NBWP` had merged. Both are classed `safety`.
So they re-enter under the second of the two unconditional exceptions in "The
gate is a snapshot", not under the presence rule. That matters, because the
presence test gives a different result for each of them, and the `safety` test
does not. `PL-X35V` describes a deficiency that predates the freeze. The
interface has never stated what a playback rate costs in control resolution,
and `PL-NBWP` only made that cost possible to name. `PL-ZVS7`'s subject is
new, because the table it asks to pin is one that `PL-NBWP` wrote. Neither is
inside this milestone's Required scope, so both clear before implementation
begins.

- PL-X35V (M) The playback-rate control does not state the control resolution its rung costs, so the PL-NBWP disclosure reaches only a reader who has docs/MODEL.md open
- PL-ZVS7 (M) docs/MODEL.md's control-resolution tolerance table is a measured safety claim with no regression test; re-measuring it 2026-09-06 reproduced it, but nothing would have caught a drift

**Added 2026-09-07 under the unconditional safety/science exception — 11 entries**

Eleven items classed `safety` or `science` were filed between the 2026-09-06
freeze and 2026-09-07. They belong here whatever the presence test says about
them. The rule that says so is the second of the two unconditional exceptions
in "The gate is a snapshot". None is inside this milestone's Required scope, so
all eleven clear before implementation begins. Nine are in the product lane and
two apply to both halves. Nine are `science`, and eight of those declare
`docs/MODEL.md`. So they are ordered against one another rather than run eleven
ways at once. Under the tiering that `PL-VRMK` added to `bin/docket
concurrent`, a shared file means the items must be sequenced, not that they
contend.

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

**Four further `safety`/`science` items from the same window are deliberately
not here.** `PL-1XPX`, `PL-CTD7`, `PL-W7H9` and `PL-Z3W6` are placed in this
milestone's own Required scope below. So they clear *with* the milestone
rather than before it. That is the distinction that the
"Cleared by v0.5.0 itself" group above draws.

**That none of the eleven was recorded for two days is `PL-KTKP`.**
`tools/doc_check.py` now raises an advisory that names any open `safety`- or
`science`-classed item that this section does not place. That is the
decidable half of the problem. Which of the three dispositions an unplaced
item takes is still a reader's judgment.

**Added 2026-09-08 under the presence rule — 17 entries**

The 2026-09-08 audit (`PL-36R4`) applied the presence test to every open item
that both this list and the Required scope below leave out. There were
forty-two of them. All were filed on or after the freeze day, and none had
been placed or declined before. Leaving an item neither placed nor declined is
the one disposition that "The gate is a snapshot" forbids by name. So each of
the forty-two needed a decision either way.

**Thirteen are admitted, and the boundary is `docket.toml`'s own** (project
owner, 2026-09-08). The ten items in the product lane and the three that apply
to both halves come in. The twenty-nine that are wholly in the workflow lane
are declined below. None is inside this milestone's Required scope, so all thirteen
clear before implementation begins.

**The fourteenth arrived after that audit, and is admitted for a reason of its
own** (2026-09-08). `PL-QXSB` asks whether the interface should stay on Flet.
`PL-QXSB` records why it qualifies for presence.

It is admitted, and not merely qualified, because of what this milestone is.
This milestone, v0.5.0, puts a **second chart** on the screen for a branched
run. The cost that `PL-QXSB` names is paid for each control on screen in each
frame. So the one milestone whose defining feature doubles the interface is
the one that should not begin without an answer. The answer may well be
"stay", as the item itself says. That answer needs only a reply, not a
migration.

**Its three consequences come with it** (2026-09-08). `PL-55DH` builds the
throwaway PySide6 spike. `PL-X9T3` runs the spike on hardware that this
container does not have. `PL-JRS3` establishes what a port would cost the two
checks that read `theme.py`. `PL-QXSB` records why the three are on the list.

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

`PL-LT51` was filed on 2026-09-10 out of `PL-8SDL`. `PL-8SDL` identified the
four references that Lowe and Ernst cite for the reference patient's organ
volumes and blood flows. `PL-LT51` is classed `science` and `docs`. So it re-enters this
gate whatever the presence test says about it, under the second of the two
unconditional exceptions in "The gate is a snapshot". It is not inside this
milestone's Required scope, so it clears before implementation begins.

**It is admitted rather than deferred, and the reason is that it has twice been
shown to be closeable.** The obvious argument for deferring it is that no
session can close it. It needs three papers from the 1960s and 1970s. PubMed
holds no abstract and no full text for them, and the egress proxy refuses
every publisher. That argument does not survive the evidence. The project
owner turned around two interlibrary loans in three days for exactly this
chain of references: `PL-7HDS` on 2026-09-08 and `PL-8SDL` on 2026-09-10.
Reference 26 was read on the day the item was filed. Deferring the item would
shrink the gate on a claim that those three days disprove. `PL-LT51` closed on
2026-09-10 (#494, v0.4.13), when all four references had been read.

**What it has already established belongs beside the entry**, because it
changes what the remaining reading is for. Table 8 of ICRP Committee II, on
page 151, is *Organs of standard man*. It gives masses and effective radii,
and **no blood flows at all**. So the perfusion fractions cannot come from the
one reference of the four that is not itself a model, and these fractions set
every time constant this model computes. They come from references 9, 19 or 20, which are
uptake-and-distribution models. The chain of sources behind
`reference_adult.json` therefore ends at tier 2 in both halves and reaches
tier 1 nowhere.

- PL-LT51 (M) Obtain and read Lowe and Ernst's four upstream references for the reference patient's volumes and flows, starting with ICRP Committee II page 151

**Added 2026-09-12 under the unconditional safety/science exception — 7 entries**

Six of these were found by the triage pass that took the queue from 46
untriaged captures to none (`PL-3B47`). A seventh was added later the same day
and is explained at the foot of this group. All seven are `safety`- or
`science`-classed. So they re-enter this gate whatever the presence test says
about them, under the second of the two unconditional exceptions in "The gate
is a snapshot". None is inside this milestone's Required scope, so all seven
clear before implementation begins.

**Four are the specification disagreeing with the tree it describes**, which is
the class of problem this exception exists for. A reader consults
`docs/MODEL.md` to decide whether to trust a displayed value. Each of these
four tells that reader something the shipped files no longer support.
`PL-7KDC` and `PL-S3Q0` both follow from `PL-8ZJQ`, which adopted Davis and
Mapleson for the venous pool. `PL-7KDC` concerns the paragraph that counts
what the parameter set rests on, which still says all eleven values are Gas
Man's. `PL-S3Q0` concerns two notes that still assert a tier-2 source may
never be the authority for a stored value. This project has now done exactly
that. `PL-Q5NS` is an omission from Known limitations that is worth about 20%
of every agent's fast pool. `PL-MMWX` is the same failure in a different
document. `ROADMAP.md` item 30 scopes weight as an input but does not record
that the scaling is safe only as a coupled package. A session that scoped the
work from the item alone would ship paediatric kinetics wrong in the direction
that is taught most.

**`PL-RFLN` is admitted rather than deferred on the same evidence as `PL-LT51`
above.** **Closed 2026-09-13.** The methods were read, and the apparatus was excluded. End-tidal
sampling was struck on the strength of Carpenter & Eger's measurement of the
gradient that it depends on. Only the published value is left, and nothing
this project runs can settle it.

**`PL-YLKR` is here for what the tooltip may imply rather than for what it
says.** What it says is a bare number. It gives no unit, no compartment and no
agent, and nothing marks the quantity as modelled rather than measured.
`PL-KP7H` made the tooltip appear only while the run is paused. That is
precisely when a reader stops to study a number instead of glancing at a
trace. So the tooltip is where a reader has the most time to draw a
conclusion and the least context to draw it from. A modelled alveolar
fraction read as a measurement is the confusion that `CLAUDE.md` names
explicitly.

**The seventh is `PL-DZFJ`** (found by the `PL-0QQP` triage pass, 2026-09-12).
It corrected the `PL-YLKR` paragraph above, and `PL-YLKR`'s brief, on
2026-09-13. `PL-DZFJ` records the correction.

- PL-7KDC (S) docs/MODEL.md's 'Where this project stands' paragraph still says all eleven reference-patient parameters are the Gas Man default patient and 26 of 29 rows are tier 3, though PL-8ZJQ moved venous_pool_volume_l to a tier-2 source
- PL-DZFJ (S) ROADMAP.md's gate text and PL-YLKR's brief say every drawn chart point is an M4 representative of a bucket of recorded samples, which PL-2FM6 deleted in v0.4.12 - the chart evaluates the score at the plotted instants
- PL-MMWX (S) ROADMAP.md's planned-milestone item 30 does not say that cardiac-output scaling is one of its obligations, or that weight scaling is only safe as a coupled package
- PL-Q5NS (S) docs/MODEL.md's Known limitations does not list lung tissue and pulmonary blood as an omitted store, which is worth about 20 percent of every agent's fast pool
- PL-RFLN (M) Settle what causes desflurane's five-minute washout residual, which PL-73G7 narrowed to end-tidal sampling or the published datum
- PL-S3Q0 (S) Two paraphrases of the tier-2 absolute survived PL-FJGY's sweep, in docs/MODEL.md's Kharasch note and reference_adult.json's Frayn and Karpe note
- PL-YLKR (M) Design what a chart tooltip says: fl_chart's default is a bare number, and PL-KP7H makes the tooltip a paused-only readout that a reader will actually stop and study

**Added 2026-09-13 under the unconditional safety/science exception — 4 entries**

These entries were found by the triage pass over the fourteen captures open
that day (`PL-TQJ4`). `PL-V6M0` is `safety`-classed. So it re-enters this gate
whatever the presence test says about it, under the second of the two
unconditional exceptions in "The gate is a snapshot". It is not inside this
milestone's Required scope, so it clears before implementation begins.

**What it is.** `PL-YK2V` widened the catch in `_apply_setting` so that any
exception outside the project hierarchy halts the run. The narrow arm that it
kept catches `AnesthesiaSimulationError`, which is the base class. That is
right for `SimulationConfigurationError`, where a value was refused and nothing
was miscalculated. It inverts the meaning of `SimulationExecutionError`,
though. The docstring of that type in `core/exceptions.py` says the run must
stop rather than continue. Under the narrow arm, such an error would be
reported to the reader as a refused setting, while the run keeps producing
readings. `SimulationDomainLimitError` has the same problem. It would be
mislabelled as a refusal, when it means that the run has reached the edge of
its supported domain.

**Why `anticipated` does not defer it.** No route raises either type into
`_apply_setting` today, which is why the item carries that class. But
`checks.py` exempts the class from the band only at `status: blocked`, and
nothing blocks this item. Its trigger is a future route, not a named item or
milestone. So the exemption is unavailable, and an unavailable exemption is not
a reason to rank safety-critical work lower. This milestone is also what makes
the anticipated route concrete. v0.5.0 turns a run from a sequence of applied
steps into a closed-form function of its control-input timeline. A setting can
then be applied to a run that has already been evaluated. That is the
"applied by re-stepping" route that the item names as the way in, and it is
newly in play here rather than hypothetical.

**The second arrived in the triage pass over the twenty-seven captures open
later the same day** (`PL-DJYF`). It is `science`-classed for the same reason as
its twin `PL-4YY1` (record provenance for the circuit volume and default fresh
gas flow), which is already on this gate and shipped in v0.4.20. Being
`science`-classed, this item re-enters whatever its presence answer. `AlveolarCompartment` carries
`gas_volume_l` and `alveolar_ventilation_l_min` as dataclass field defaults.
`data/patients/reference_adult.json` stores both values with their provenance.
Nothing keeps the two copies equal. The circuit was different: `PL-4YY1` pinned
its copies with a test, which `PL-M85T` later retired along with the default.
A constant that is free to drift from the parameter set that `docs/MODEL.md`
cites gives a run on a value that the specification does not name. That run is
presented with provenance that looks correct. This is the class of finding that
this exception exists for. The item is not inside this milestone's Required
scope, so it clears before implementation begins.

- PL-V6M0 (S) _apply_setting reports a SimulationExecutionError as a refused setting and lets the run continue, which is the opposite of what that type means

**Two more arrived from the Targ, Yasuda and Eger 1989 circuit paper.** The
paper was read in full text from the private corpus on 2026-09-13, and the two
items were merged the same evening. Both are `science`-classed, and neither
changes a displayed value. They belong here because they have the `PL-Q5NS`
shape: the specification understates what is known, and judging what is known
is exactly why a reader consults it.

`PL-QBKQ` concerns the reference circle system's data file
(`data/machines/reference_circle_system.json`). Its note on missing provenance
(`provenance_gap`) says that a measured circle-system volume "has not been sought
yet". One has now been read: 9.86 L, measured by water filling. That value does
*not* close the gap, because the measurement includes a reservoir bag that
simulates the lungs. The item's work is to say so. Three figures now line up in
increasing order, and only one of them is measured: this project's 6.0 L, Gas
Man's published 8.0 L, and that 9.86 L upper bound.

`PL-XWCY` records that the same paper rules out circuit-wall absorption as a
candidate for desflurane's residual. In the same measurement, the paper reports
that a real circle system measurably slows sevoflurane and isoflurane relative to
an ideal one. This model has no term for that mechanism. The finding points at
published wash-in and elimination cohorts whose comparison with this model
already sits at +3.79 SD and +4.15 SD. Ruling out the desflurane candidate is
bookkeeping. The second half is a named, quantified departure that bears on an
existing discrepancy, which is why it was not declined to Gate 2 with the
workflow-apparatus items from the same triage.

Neither is inside this milestone's Required scope, so both clear before
implementation begins.

- PL-DJYF (S) AlveolarCompartment restates the reference patient's gas volume and ventilation as core/ dataclass defaults, the same restatement PL-4YY1 found on BreathingCircuit
- PL-QBKQ (S) The only measured conventional circle-system volume this project holds is 9.86 L including a simulated lung, against a stored 6.0 L and Gas Man's published 8.0 L
- PL-XWCY (M) Circuit-component absorption is ruled out as a cause of desflurane's residual by the one paper that measured it, and is a live candidate for the other two agents

**Added 2026-09-14 under the unconditional safety/science exception — 3 entries**

`PL-YVHK` is `safety`-classed, so it re-enters this gate whatever its presence
answer, under the second of the two unconditional exceptions in
"The gate is a snapshot". It closed on 2026-09-15, in v0.4.26. Its brief records
its disposition, and § "Sequenced past v0.5.0" lists it as sequenced behind the Qt
port. Its place on this gate and its place behind the port do not conflict. The
presence rule decides that a safety finding is recorded against the current gate.
The snapshot rule decides that a recorded deferral is how the finding may then be
sequenced out of that gate. Silence is the third option, and the only one that is
forbidden.

**`PL-YVHK` builds the chart hover readout that `PL-YLKR` designed.** The project
owner split it from `PL-YLKR` on 2026-09-14. The design and its derivation landed
on v0.4.x, in `docs/INTERFACE.md`
§ "The chart's hover readout: what the tooltip may show". The hover was then
written against pyqtgraph and shipped in v0.4.26 (#588). The item is classed
`safety` for its parent's reason. A reader may stop the simulation to look at a
number, and if nothing around that number says the value is modelled rather than
measured, that is the failure that `CLAUDE.md` names.

**The second, `PL-2K1R`, asks for a disclaimer that the compartment readouts and
chart traces are modelled rather than measured.** It was found on 2026-09-13 and
triaged on 2026-09-14 (project owner), and it is `P1` `safety`. This
interpretation disclaimer goes beside the use disclaimer. Its statement is the
line that `CLAUDE.md`'s safety standard draws on the surface a clinician reads.
The item rode the Qt port behind `PL-25KS` (port the dashboard) under the
carried-fix rule, because text on a dashboard being rewritten from scratch should
be written once. Like the five entries the port carried (`PL-3355`, `PL-Q4VH`,
`PL-THXF`, `PL-TG60`, `PL-W8DQ`), it closed before v0.5.0, in v0.4.26.
§ "Sequenced past v0.5.0" below carries it in that table. The port names it under
§ "Decisions the port has to make anyway", so that the port's parity claim stays
checkable.

- PL-2K1R (S) The interface carries a use disclaimer but no interpretation one, so nothing tells a reader the compartment readouts and chart traces are modelled rather than measured
- PL-YVHK (S) Implement the chart hover readout on pyqtgraph to the derivation docs/MODEL.md now carries, turn hoverable on so the affordance is not silently lost, and say in README.md that it exists

**`PL-27H0` is the third.** It draws the same modelled-versus-measured line in
the specification rather than on the screen. `docs/MODEL.md` still tells a
reader that every point drawn on the chart *is a recorded sample*, selected
from a per-step store. `PL-2FM6` deleted that store, and `app/chart_frame.py`
now deliberately says the opposite: "Every drawn point is a state of the run
at the instant it is drawn at, evaluated from the run definition rather than
selected from recorded samples". Two things make the item `safety` rather than
`docs`. The sentence is about the provenance of a displayed value, which
`CLAUDE.md` names as a safety failure in its own right. And the numbers are
correct throughout, which is what makes the error hard to notice. Unlike the
two items above, it needs no toolkit, and it clears before implementation
begins.

- PL-27H0 (M) docs/MODEL.md still specifies a per-step recorded sample store and a display operation that selects which recorded samples a trace draws, both of which PL-2FM6 deleted

**Added 2026-09-14 under the unconditional safety/science exception and the presence rule — 4 entries**

`PL-JRS3`'s pre-port survey found these four, and they were triaged the same
day into `feature: qt-port`. In
§ "Completed: v0.4.26 - the interface moves to Qt" → "Required scope", item 4
already places the first three by name, and its opening paragraph names the
fourth. All four land before the port's first
commit, on the branch that records them here, so they clear ahead of this gate
by construction.

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

**Added 2026-09-20 under the unconditional safety/science exception — 1 entry**

- PL-LHBY (M) — **added 2026-09-20, `safety`.** `SimulationView._refresh_bookmarks`
  draws the marks panel from the reference run alone, and a mark's *standing* is
  per-run where its *set* is not. With a branch displayed, a branch halted on a
  learner's MAC target shows no standing at all - the halt is indistinguishable
  from a Pause - and a mark the trunk reached is rendered `reached` beside a
  branch whose own standing says it never can be. `safety`: `CLAUDE.md` names the
  correct value under the wrong patient context as a failure of the value, and a
  standing is a claim about which run got there.

  **Admitted although the problem postdates the freeze by a fortnight**, because
  the rule above makes `safety` not deferrable and because this gate's own
  Required scope is what created it: `PL-VKJW` made two runs reachable from a
  shipped entry point for the first time. It is therefore debt this milestone
  clears itself rather than a precondition to beginning it, which is the only
  reading under which a defect created by a milestone can sit in that
  milestone's gate at all.

**Added 2026-09-17 under the unconditional safety/science exception — 3 entries**

All three were captured on 2026-09-16 or 2026-09-17 and triaged on 2026-09-17
(`PL-Y4D6`). They are `science`- or `safety`-classed, so they re-enter this
gate whatever their presence answer. They do so under the second of the two
unconditional exceptions in "The gate is a snapshot". None is inside this
milestone's Required scope, so all three clear before implementation begins.

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

**They are admitted rather than deferred, and the reason is the rule rather
than a judgment.** "The gate is a snapshot" makes `safety` and `science` not
deferrable. `tools/doc_check.py` says so at the point where a session would
otherwise turn to the declined subsection. A `### Declined to Gate ...` entry
clears the disposition error but leaves the re-entry advisory in place. There
is one carve-out, for an `anticipated` finding, and § "What counts" states it.
`PL-KZ99` is the entry from this triage that qualifies for it, so `PL-KZ99` is
recorded in the declined subsection with `PL-0S0V` and `PL-VJZK` instead.

**Two of the three describe a hazard that is not live, and that is a reason to
do them now rather than to defer them.** Neither a cost readout nor a
preferences panel exists, so nothing displayed today is wrong. Each item fixes
a sentence in the planned-milestone entry that a later session would implement
from. Now is the cheapest moment such a correction will ever have. That is why
both items are `ready` at `S` rather than blocked on the milestone they
protect. `PL-S6WW` is the live one of the three. Its sentence is false as
written, in the document that this project calls authoritative for units and
assumptions. The other two rest on ground that `PL-S6WW` settles.

**Added 2026-09-19 under the unconditional safety/science exception — 2 entries**

Both were captured on 2026-09-17 and triaged on 2026-09-19, in the pass that
placed nineteen of the store's twenty untriaged items. They are `safety`- or
`science`-classed, so they re-enter this gate whatever their presence answer.
They do so under the second of the two unconditional exceptions in "The gate
is a snapshot". Neither is `anticipated`, so the one carve-out to that
exception does not apply to them. The hover is live on the shipped chart today,
and `docs/MODEL.md` is the authoritative specification today. Neither is inside
this milestone's Required scope, so both clear before implementation begins.
The eleven other debt items that the pass placed are declined below, all of
them wholly in the workflow lane.

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

`PL-4DCG`'s machine survey captured this entry on 2026-09-19, and it was
triaged on 2026-09-20. It is classed `science`, so it re-enters this gate
whatever the result of its presence test, under the second of the two
unconditional exceptions in "The gate is a snapshot". Its problem also predates
the freeze: the sentence it corrects has been in the data file since before
2026-09-06. It is not inside this milestone's Required scope, so it must be
cleared before implementation begins.

- PL-NM7X (S) — **added 2026-09-20.** The reference circle system's data file
  (`src/anesthesia_sim/data/machines/reference_circle_system.json`) justifies its
  4 L/min default fresh gas flow (`default_fresh_gas_flow_l_min`) as "a routine
  mid-range clinical fresh gas flow". Its note on missing provenance (`provenance_gap`)
  adds that no clinical convention for a default flow "HAS NOT BEEN SOUGHT".
  `PL-4DCG`'s survey has since sought one and found the justification superseded.
  `docs/MODEL.md` § "Parameter provenance" and `docs/machine-survey.md` § "(a2)" both
  restate that justification. The item is classed `science` because the project's own
  survey contradicts a clinical-practice claim that a reader finds in the document this
  project calls authoritative for provenance. **The 4 L/min default is not what is
  open.** The project owner ruled on 2026-09-20 (ratified, over lowering the default
  to match contemporary low-flow practice) that 4.0 stays, because an unlabelled
  default teaches a norm whatever it holds, and the 90 s circuit time constant is what
  makes the machine's lag legible inside a teaching run. What clears this entry is the
  wording.

**Added 2026-09-20 under the unconditional safety/science exception — 3 entries**

All three were captured on 2026-09-19 or 2026-09-20 and triaged on 2026-09-20
(`PL-WQF1`). Each is classed `safety` or `science`, so each re-enters this gate
whatever the result of its presence test. The rule that allows this is the
second of the two unconditional exceptions in "The gate is a snapshot". None
is inside this milestone's Required scope, so all three must be cleared before
implementation begins.

The two `science` entries are the rest of `PL-4DCG`'s machine survey, as it
applies to `docs/MODEL.md`. That survey compared the anesthesia machines in
current clinical use with what this model claims. Most of what it found was
not a defect in the arithmetic. It was statements that the document owes its
readers about its own limits. The `safety` entry is the successor to
`PL-JVHL`, applied one axis over.

- PL-0RZ0 (S) — **added 2026-09-20, `safety`.** `PL-JVHL` took the *run* out of
  the pointer's hands, and deliberately left distance settling which
  **compartment** answers. The cause it named is untouched: the percent axis is
  scaled by the alveolar peak, so two slow compartments of one run contend
  inside one hover radius exactly as two runs' copies of one compartment did.
  `PL-0RZ0`'s brief records the measurement on one run (2026-09-20): two or
  more compartments sit inside the hover radius over 37.0% of the hoverable
  area. `safety` for `PL-JVHL`'s reason: the box prints a
  compartment name and a value, fat and muscle at one instant can differ
  severalfold, and a hand movement too small to aim with changes which of them
  is being read. **The scan comes before any rule** — `PL-JVHL`'s own lesson is
  that two of its three candidate rules changed nothing once counted — and the
  honest outcome may be to record the measurement and drop this in favour of
  `PL-QYBW`, which is the axis underneath it and is declined to Gate 2 below.
- PL-D126 (S) — **added 2026-09-20, `science`.** This project treats Gas Man as
  its reference implementation and compares against it throughout
  `docs/MODEL.md`. Candries, De Wolf and Hendrickx's prospective in-patient
  validation (*J Clin Monit Comput* 2022;36(6):1881–1890) reports Gas Man's
  agreement split by phase: over the first 15 minutes MDPE 18% and MDAPE 21% on
  the FLOW-i and 7% and 13% on the Zeus, against 0% and 6%, and −1% and 5%, over
  the last 45 minutes. The authors state the model performs better for
  maintenance than for wash-in. The wash-in is the phase this simulator most
  displays, so the phase in which its reference is least accurate is the one it
  shows most, and § "Known limitations" does not say so. A statement about the
  limits of a comparison rather than a defect in this implementation.
- PL-WJNS (S) — **added 2026-09-20, `science`.** § "Breathing circuit" states
  that "an equal fresh-gas volume leaves through the exhaust at the current
  mixed-circuit concentration", and § "Circuit exhaust" and the mass-balance
  identity are built on that being unconditional. It is how a semi-closed circle
  behaves and not how every machine behaves in every mode: Meyer et al. record
  that on the Zeus "the surplus gas valve can be closed to prevent any loss of
  gas volume", which is not a small exhaust but a different conservation
  statement. Confirmed at triage that `docs/MODEL.md` carries no semi-closed
  assumption anywhere — § "Model boundary" and § "Assumptions" are silent — so a
  reader who knows closed-circuit machines exist cannot tell whether the model
  excluded them or overlooked them. It matters ahead of any machine
  implementation for the reason the survey gives: this is the one machine
  variable that reaches an *equation* rather than a coefficient.

**Added 2026-09-20 under the unconditional safety/science exception — 2 entries**

These two entries are one problem and its consequence. The first was found
while building `PL-B8MK` (a bookmark is a forkable instant), which is in this
milestone's Required scope. The second was found later the same day, while
the first was being decided. Both are classed `safety`, so both re-enter this
gate whatever the result of their presence test. The rule that allows this is
the second of the two unconditional exceptions in "The gate is a snapshot".
Neither is itself inside Required scope, so both must be cleared before
implementation begins.

The problem is older than `PL-B8MK` in the code, but not in how easily a
learner could meet it. The comparison it turns on has always been strict.
Before a bookmark could be forked, a mark could sit exactly on a branch's fork
instant only if the learner had happened to mark a control-event instant.

- PL-3K9B (S) — **added 2026-09-20, `safety`; decided 2026-09-20.** A branch
  taken at a halt begins at the very crossing it was taken at, and the bookmark
  panel says that crossing has not happened on this run. Three cases measured
  2026-09-20 share one root. A time bookmark on the step grid reads
  `still_running`, "the run can still reach this mark". No step can make that
  true, because a step counts a mark as crossed only when the mark lies after the
  step's start (`crossed_between` is `before_s < instant_s <= after_s`), and the
  branch's first step starts at the fork. Every whole-second mark is on the step
  grid (3 600 of 3 600 over 1 s to 3 600 s). A time bookmark at an instant off the
  grid reads `before this branch opened` instead, so which row a learner gets turns
  on whether the number they typed is a multiple of 0.1 in binary. And a MAC target
  reads `still_running` on the branch while reading `reached` on its trunk. The
  target's crossing is the one the two runs share by construction, on a branch
  whose identity is the management taken at that height. Four further cases were
  then measured, two of them on a trunk with no branch anywhere: a mark added
  behind a running clock, a fork taken at a control event, a mark re-added at a
  fork instant, and a branch `reset()`. So the root is that `still_running` is
  inferred from the mark's absence from the halt set. Whether the instant is still
  ahead of the run is a question for a one-way clock. Decided (project owner,
  2026-09-20, ratified, over reusing `REACHED` for the at-or-behind case and over
  the item's original seed-and-reorder answer): add `PASSED` as a fifth bookmark
  standing (`MarkStanding`) and decide a time bookmark from the run's own clock,
  `REACHED` keeping its meaning and its word for MAC targets. `PL-4KZD` below is
  what that decision unmasks.

- PL-4KZD (S) — **added 2026-09-20, `safety`.** The bookmark panel is drawn once,
  from the reference run's snapshot (`snapshots[0]`). While two runs are shown, it
  therefore gives the reference run's standings for marks that every run carries,
  and nothing on the row names a run. The code (`_refresh_bookmarks`) justifies
  the single read by the marks being shared. That is true of the marks
  (`snapshot.bookmarks`) and false of their standings
  (`snapshot.bookmark_standings`), because each run computes a standing from its
  own clock, its own start (`began_at_s`) and its own halt set. Measured
  2026-09-20: a trunk halted at 0.4 ×MAC reads `reached`, while the branch forked
  there reads `still_running`. It was captured after the freeze and re-enters
  under the unconditional `safety` exception. The problem postdates the freeze,
  because the panel landed with `PL-LPLD` on 2026-09-20. The item was folded into
  `PL-LHBY` and closed with it (#811). The problem stays hidden while a standing
  behaves almost like a permanent latch, and `PL-3K9B`'s decision exposes it by
  making the standing depend on where each run *is*.

**Added 2026-09-20 under the unconditional safety/science exception — 1 entry**

- PL-N3N5 (S) — **added 2026-09-20, `safety`.** Every mark on a *failed* run
  reports `MarkStanding.STILL_RUNNING`, whose docstring says "the run can still
  reach this mark, and has not yet". Yet the controller refuses that run outright
  ("cannot resume a failed simulation … reset it first",
  `SimulationController.start`). The cause is that the code computing standings
  (`_bookmark_standings`) passes `stopped_at_cap` and nothing about whether the
  run can take another step. The adversarial review of `PL-LHBY` found the problem,
  and failing one of two displayed runs reproduced it: the run's own panel read
  `Stopped — simulation error` while its mark clause claimed the mark was still
  ahead of it. It was captured after the freeze and re-enters under the
  unconditional `safety` exception. The problem postdates the freeze and predates
  `PL-LHBY`. The standing has been wrong since `PL-CTD7` (2026-09-20), and it was
  invisible only because `STILL_RUNNING` showed no text. `PL-LHBY` changed that:
  the standing is now drawn in words on a row that names its run, where a learner
  can read it.

**Added 2026-09-21 under the unconditional safety/science exception — 1 entry**

This entry is the second `safety` finding from the adversarial review of `#784`,
and the triage pass of 2026-09-21 placed it in this gate. The first, `PL-LHBY`
above, was admitted on 2026-09-20 under the same exception. The review's five
other findings are not here. Two are deferred below (`PL-WG73`, `PL-624C`), and
three are classed `test` alone (`PL-FKN7`, `PL-R17Y`, `PL-RS3Z`).

- PL-25DD (S) — **added 2026-09-21, `safety`.** The wash-in state line and the
  off-scale notice are placed one per run into two shared columns beside the
  chart (`_place_run`'s `_off_scale_column` and `_wash_in_state_column` holders),
  and neither text names a run. The wash-in line reads `"Now: F_A/F_I = {ratio}"`
  (`WASH_IN_STATE_TEMPLATE`), and the off-scale notice (`off_scale_notice`) names
  compartments and a ceiling. With a branch drawn, two unlabelled lines stack, and
  only their order tells them apart. Nothing on screen says which run's line comes
  first, and the run names sit in a separate pane. It is `safety` because
  `CLAUDE.md` names the correct value under the wrong patient context as a failure
  of the value, and F_A/F_I read off the wrong run inverts the comparison a branch
  exists to teach.

  **Admitted although the problem postdates the freeze**, for the two reasons
  `PL-LHBY` was: the rule above makes `safety` not deferrable whatever the
  presence answer, and this gate's own Required scope is what created the
  hazard — `PL-VKJW` made two runs reachable from a shipped entry point for the
  first time. The widgets are older than the freeze; their ambiguity is not.

**Added 2026-09-21 under the unconditional safety/science exception — 2 entries**

The code that places a run on screen (`_place_run`) spreads the run's widgets across
six shared layouts. `PL-25DD` fixes two of them, and a review of the other four
found the same gap in two. Those two are admitted for the same two reasons as
`PL-25DD`. The remaining two need nothing: the transport row already includes the
run-name text (`build_transport_row`, `_run_name_text`), and the header badge names
the agent.

- PL-TSZM (S) — **added 2026-09-21, `safety`.** Each run puts one bare notice label
  (`NoticeLabel`) into a column that the runs share
  (`_holder(self._notice_column, (run.build_notice(),))`). All three notices it can
  show say something about a run and name none: "Simulation stopped"
  (`FAILURE_NOTICE_TEMPLATE`), "this run reached the supported run length"
  (`SUPPORTED_LIMIT_NOTICE_TEMPLATE`), and "The simulation is unchanged and still
  running its previous setting" (`REFUSED_SETTING_NOTICE_TEMPLATE`). It is `safety`
  for two reasons. The last notice is not merely unattributed but *false* of the run
  it is not about. And the hazard table in `docs/MODEL.md` has a row for "reading a
  run halted by a failure as one the user paused", but the distinction that row
  secures is lost the moment two runs are drawn.

- PL-C3GS (M) — **added 2026-09-21, `safety`.** Each run puts *two* panels into a
  shared sidebar column (`_holder(self._sidebar_column, run.build_sidebar_panels())`).
  With a branch, the sidebar therefore reads Agent accounting validation / Control
  changes / Agent accounting validation / Control changes, and no panel names its
  run. The control-changes caption (`CONTROL_TIMELINE_CAPTION`) reads "What was
  changed during this run, most recent first" over settings and the simulated times
  they took effect, and nothing says which run "this run" is. It is `safety` because
  comparing two managements of one patient is what a branch is for, so a setting
  change read off the wrong panel says the trunk received an intervention it never
  got.

### Declined to Gate 2, because this milestone's own work created them

Each entry's disposition, with its reasons, moved to its item's brief on
2026-11-08 (`PL-4BCF`), on the project owner's answer in `PL-LVN8`.

- Deferred 2026-09-21: `PL-WG73`, `PL-624C`.

### Deferred to v0.4.26, because the port dissolves the defect

Each entry's disposition, with its reasons, moved to its item's brief on
2026-11-08 (`PL-4BCF`), on the project owner's answer in `PL-LVN8`. `PL-NGF7`
was deferred to v0.4.26 and closed `done` there (#621).

### Sequenced past v0.5.0, so not clearable before it begins

The frozen list sequenced these entries past v0.5.0, most of them behind the Qt
port. The port moved ahead of v0.5.0 on 2026-09-14 (project owner, 2026-09-14,
on `PL-RKWB`), so most of them became clearable before v0.5.0 began. The table
is the one this section carried from that day. Each entry's disposition, with
its reasons, moved to its item's brief on 2026-11-08 (`PL-4BCF`), on the project
owner's answer in `PL-LVN8`.

| Entry | Relation to the port | Now clears |
| --- | --- | --- |
| `PL-3355`, `PL-Q4VH`, `PL-THXF`, `PL-TG60`, `PL-W8DQ` | carried by it | before v0.5.0 |
| `PL-GS3R`, `PL-YVHK` | sequenced behind it, both `P1` `safety` | before v0.5.0 |
| `PL-NGF7` | dissolved by it | before v0.5.0, as `dropped` |
| `PL-16ZC` | deferred past it | before v0.5.0, behind `PL-G59B` |
| `PL-8PS6`, `PL-WZVZ` | behind a design round the roadmap places nowhere | unchanged |
| `PL-2K1R` | rides it, added after the freeze | before v0.5.0 |

Since then, `PL-NGF7` closed `done` in v0.4.26 (#621) rather than `dropped`. The
design round happened (`PL-8G48`, 2026-09-20): `PL-8PS6` became ordinary gate
work and closed `done` in v0.4.34, and `PL-WZVZ` was deferred to Gate 2 (project
owner, 2026-09-20, on `PL-S5Q9`). `PL-Z34C` joined this section on 2026-09-20
(project owner, ratified, over keeping it on the frozen list), because its
completion is a standing condition, not a piece of work.

### Declined to Gate 2 on the refilling-queue ground

Each entry's disposition, with its reasons, moved to its item's brief on
2026-11-08 (`PL-4BCF`), on the project owner's answer in `PL-LVN8`. A paragraph
that disposed of several entries is quoted whole in one brief: one of theirs, or
that of the triage pass it names. Each other entry's brief names where. Each
line below names the ground that its entries' dispositions rested on. An entry
on the first line rests on the ground this heading names (project owner,
2026-09-08): pulling it in "would recreate the refilling-queue problem the debt
gate replaced Phase 0 to solve".

- **The refilling-queue ground**: `PL-087W`, `PL-0HPV`, `PL-0KQP`, `PL-0M32`,
  `PL-0MLZ`, `PL-0PJG`, `PL-12P8`, `PL-13PB`, `PL-162Y`, `PL-188T`, `PL-1BS2`,
  `PL-1T6T`, `PL-1X2C`, `PL-245B`, `PL-28HG`, `PL-2BZY`, `PL-2DTK`, `PL-2GQW`,
  `PL-2M4X`, `PL-2M5T`, `PL-2MD9`, `PL-2T03`, `PL-2XM2`, `PL-316G`, `PL-34BG`,
  `PL-3BYK`, `PL-3DN1`, `PL-3DXV`, `PL-3LLZ`, `PL-3V6C`, `PL-483K`, `PL-4FD2`,
  `PL-4HKS`, `PL-4L49`, `PL-4PC5`, `PL-4Q9B`, `PL-4RHP`, `PL-4V6B`, `PL-4W2L`,
  `PL-4ZK8`, `PL-5B39`, `PL-5B88`, `PL-5MFL`, `PL-61MD`, `PL-65HT`, `PL-69JZ`,
  `PL-6BDX`, `PL-6G8T`, `PL-6T44`, `PL-6TN8`, `PL-6TP8`, `PL-6YL1`, `PL-6YWK`,
  `PL-6YYR`, `PL-73G8`, `PL-73P0`, `PL-73ZN`, `PL-77SV`, `PL-7K2C`, `PL-7NKD`,
  `PL-7RTN`, `PL-7TVT`, `PL-7XNX`, `PL-7XTS`, `PL-879R`, `PL-8JQQ`, `PL-8MJ3`,
  `PL-8P6D`, `PL-8T3Z`, `PL-8T83`, `PL-9KP5`, `PL-9KSY`, `PL-9LXK`, `PL-9TNJ`,
  `PL-B11M`, `PL-B396`, `PL-B5DW`, `PL-B8V1`, `PL-BGMK`, `PL-BHBZ`, `PL-BHVM`,
  `PL-BMY5`, `PL-BX1C`, `PL-BXB2`, `PL-C4RS`, `PL-C6XD`, `PL-C97K`, `PL-CNJH`,
  `PL-CWD4`, `PL-CY8B`, `PL-D0K3`, `PL-D1NT`, `PL-D1RT`, `PL-DBGT`, `PL-DG84`,
  `PL-DK8Y`, `PL-DMNX`, `PL-F48B`, `PL-F933`, `PL-FCM3`, `PL-FT3M`, `PL-FWJF`,
  `PL-FX0K`, `PL-G21K`, `PL-G424`, `PL-G6J5`, `PL-G8TR`, `PL-GJPD`, `PL-H6VQ`,
  `PL-H9GV`, `PL-HJZW`, `PL-HX5C`, `PL-J3TV`, `PL-J3WK`, `PL-J45M`, `PL-J870`,
  `PL-JBRC`, `PL-JTHW`, `PL-JW39`, `PL-JW9J`, `PL-JXVD`, `PL-K1WS`, `PL-K5PW`,
  `PL-K82G`, `PL-KF0T`, `PL-KFWL`, `PL-KNHX`, `PL-KRS6`, `PL-KSCW`, `PL-L09X`,
  `PL-L4KX`, `PL-LBR6`, `PL-LBW5`, `PL-LF2C`, `PL-LKGL`, `PL-LKGW`, `PL-LN3T`,
  `PL-LPWK`, `PL-LSR0`, `PL-LT77`, `PL-M21Q`, `PL-MBTZ`, `PL-MFM4`, `PL-MM7F`,
  `PL-MSFB`, `PL-N2PP`, `PL-NF6N`, `PL-NGBM`, `PL-NJ9M`, `PL-NWSK`, `PL-P4XB`,
  `PL-P757`, `PL-PNW6`, `PL-PQQ2`, `PL-Q664`, `PL-QJQL`, `PL-QMC0`, `PL-QNYF`,
  `PL-QSGX`, `PL-QV5Y`, `PL-R0P3`, `PL-R0Q0`, `PL-R77L`, `PL-RBMK`, `PL-RR1N`,
  `PL-RWBV`, `PL-RY2R`, `PL-S0MB`, `PL-S8JT`, `PL-SCB4`, `PL-SMN4`, `PL-STC4`,
  `PL-SY1J`, `PL-SYG4`, `PL-SZJ2`, `PL-T441`, `PL-T7VS`, `PL-T86P`, `PL-T8PT`,
  `PL-TDBT`, `PL-TGFY`, `PL-TKFD`, `PL-TNB6`, `PL-TP5M`, `PL-TTMF`, `PL-V53R`,
  `PL-V8QG`, `PL-VFD8`, `PL-VJFQ`, `PL-VJPJ`, `PL-VKGJ`, `PL-VYK1`, `PL-VZYS`,
  `PL-W3Q5`, `PL-W7WL`, `PL-W80S`, `PL-WG7Q`, `PL-WHQS`, `PL-WNQT`, `PL-WTXB`,
  `PL-WVJ0`, `PL-WZBX`, `PL-X3NY`, `PL-XD3C`, `PL-XMNC`, `PL-XQGH`, `PL-XZD0`,
  `PL-Y1L0`, `PL-Y1LD`, `PL-Y31G`, `PL-Y4YX`, `PL-Y5JX`, `PL-Y5ZB`, `PL-YD6X`,
  `PL-YKXQ`, `PL-YNYK`, `PL-YRYR`, `PL-YS9F`, `PL-YTDN`, `PL-Z5FG`, `PL-Z6M3`,
  `PL-Z85N`, `PL-ZMGR`, `PL-ZPDM`.
- **Waiting on the Qt port, on 2026-09-12**: `PL-7SVX`, `PL-C92D`, `PL-SQJ1`,
  `PL-ZG5J`.
- **Nothing is blocked on it, and its number must be re-taken on the ported
  tree**: `PL-CNCF`.
- **A decision that the Qt port or its interface pass makes once**: `PL-3JP0`,
  `PL-HKTB`, `PL-5B1N`, `PL-KRZW`, `PL-Z4K6`.
- **Nothing misleads anybody in the meantime**: `PL-5B1N`, `PL-QYBW`, `PL-7CRY`.
- **Not wholly apparatus, but unable to change what a reader of the simulator
  sees**: `PL-0VFF`, `PL-880Z`, `PL-N32Y`, `PL-HWW1`, `PL-4FBP`, `PL-CM40`,
  `PL-DHJ7`, `PL-HCTF`, `PL-LPH9`, `PL-WPDB`, `PL-SPN6`.
- **A naming or placement decision that gives no wrong value either way**:
  `PL-BQ46`, `PL-KL2Q`, `PL-6KNM`, `PL-BDNB`, `PL-JQY1`.
- **Waiting on an answer that holding v0.5.0 open would not produce**:
  `PL-N32Y`, `PL-V67Q`, `PL-7RYB`, `PL-NLP4`, `PL-KND7`, `PL-WFFX`, `PL-KQHN`,
  `PL-DHJ7`.
- **It cannot be worked until a count outside the list is taken**: `PL-VV6N`.
- **Its problem did not exist at the 2026-09-06 freeze, so the snapshot rule
  defers it on its own terms**: `PL-HGB6`, `PL-QW19`, `PL-HNWX`, `PL-09G9`,
  `PL-YFXG`, `PL-ZMGR`, `PL-6QZP`, `PL-PFK1`, `PL-Z9K5`, `PL-9PD6`, `PL-D584`,
  `PL-J4NW`, `PL-7K8Y`, `PL-DMDF`, `PL-SH9Q`, `PL-WXX8`, `PL-PGZF`, `PL-ZM48`,
  `PL-WFFX`, `PL-1K9G`, `PL-KRZW`, `PL-VV6N`.
- **The gate had done its job on 2026-09-16, so admitting them would re-open a
  cleared gate**: `PL-1RTM`, `PL-7CSP`, `PL-99YZ`, `PL-Q8RQ`.
- **Introduced by work done while clearing this gate or implementing this
  milestone**: `PL-59WB`, `PL-7TBQ`, `PL-7TXJ`, `PL-CZTR`, `PL-JFYT`, `PL-LLBV`,
  `PL-NC62`, `PL-SM5V`, `PL-XJ37`, `PL-08CR`, `PL-FPY2`.
- **Waiting on planned-milestone item 34's area system, which v0.6.0 then
  scoped**: `PL-TH35`, `PL-VN6M`, `PL-NMTF`, `PL-7Z84`, `PL-9LNF`, `PL-NWTM`,
  `PL-W54S`, `PL-L8RN`.
- **Moved into v0.5.0's own Required scope (project owner, 2026-09-16, ratified,
  on `PL-R7XK`)**: `PL-MN4J`.
- **`anticipated`, with no milestone yet to place them in**: `PL-0S0V`,
  `PL-VJZK`, `PL-KZ99`.
- **Not debt against this gate, and recorded so that they do not look
  deferred**: `PL-J0F7`, `PL-TCR5`, `PL-QRD1`, `PL-KKRP`, `PL-NDKC`, `PL-TQFB`,
  `PL-TBMX`, `PL-K285`, `PL-904Y`, `PL-G5SX`, `PL-50PZ`, `PL-JSY5`, `PL-Y04W`.

### Required scope

This milestone requires nineteen items, listed in the order that their
dependencies allow. The first three are the score architecture that the
2026-09-05 design round filed and that the project owner placed here. The next
five are work on boundaries that this milestone's own code moves.
The last eleven are the feature itself.

**This milestone required two more items, and both are done** (`PL-C4RS`,
2026-09-19). One deleted `RunHistory`, so the chart is now drawn from the
sampler (`PL-2FM6`). The other deleted the M4 decimation path along with it,
including its tests, the cited paper and every reference to them (`PL-8LXM`).
Both items moved into the `v0.4.x` track on 2026-09-08 and shipped there.

**All twenty item ids below are `done`.** The nineteen entries hold twenty ids,
because `PL-B8MK` and `PL-TYWQ` share one. Fourteen ids shipped early in the
`v0.4.x` track, and six in v0.5.0 itself. The item that cut v0.5.0 (`PL-4B1G`)
lists each id's release.

#### The score architecture

- **The run becomes a closed-form function of its control-input timeline**
  (queue item PL-T691). Keyframes are kept at every control event, and any
  window is computed in closed form. So the state at a given time is computed
  rather than looked up. This item is the head of the milestone. Everything
  below it that touches a run depends on it. It is also what makes a branch's
  history before the branch point the same object as its parent's history.
- **The canonical evaluation rule that carries determinism** (queue item
  PL-P1Z3). Once a time can be reached by more than one route, either by
  stepping to it or by evaluating it from a keyframe, the promise that
  "identical inputs give identical results" needs a rule. The rule says which
  route is authoritative. It is stated in `docs/MODEL.md` and enforced by a
  test. The rule requires every replayed, compared or branch-opening value to
  be taken canonically. The item is classed as both safety and science, and it cannot be
  deferred within this milestone.
- **A path-scoped rule against re-introducing a sample store** (queue item
  PL-49R8). A later session that adds a convenience buffer is then told why
  the store is absent, rather than having to rediscover the reason.

#### Boundaries that this milestone's code moves

- **The controller's trace vocabulary and its UI-to-core boundary are
  separated** (queue item PL-RD3B). Two runs need the boundary, and each run
  needs its own drawn window, addressed through the same vocabulary.
- **The snapshot stops naming six flat compartment floats** (queue item
  PL-TCD1), so that a readout can name which run and which substance it
  describes.
- **The control-input timeline is bounded and stops being regrouped in full on
  every frame** (queue item PL-1PSX). In this milestone the timeline is read on
  every branch operation, not only drawn.
- **`SimulationView` is decomposed so two runs can be rendered at once** (queue
  item PL-B9PY). v0.4.0 left this item for this gate, because only this
  milestone needs it (project owner, 2026-09-02).
- **A run stops with a stated reason at the supported run length** (queue
  item PL-Y5WR). The item shipped early, in v0.4.7: the supported run length
  became 24 hours, a step past it is refused, and the interface says the run
  stopped at that limit. The item is classed as safety. It was carried here
  because the only item that required it was dropped with `PL-011`.

#### Taking and comparing a branch

- **A fork resumes into a live run** (queue item PL-J2TD). A run is opened at a
  canonical keyframe state of another run. It runs on the case's own clock,
  and its run definition opens at the fork instant. From there it advances by
  the same path that a live run already takes. A branch has to become
  something a learner can *manage*. That is what separates a branch from a
  second curve. Both item 12's fork and the in-loop crossing detection two
  bullets down assume that a branch resumes this way. The work is internal. It
  adds no user-facing replay control, which stays in planned item 10, behind
  item 9's save/load.
  `docs/INTERFACE.md` § "The canonical evaluation rule" carries the measurements
  behind this entry's narrowing and its change of mechanism.
- **Time bookmarks and MAC targets, as two separately listed collections**
  (queue item PL-LPLD). This follows the shape of the Gas Man reference
  simulator, and that shape sets the minimum scope. The minimum is an absolute
  simulated time, and a percent of MAC on any graphed compartment rather than
  on the alveolar trace alone. The two are kept as two kinds rather than one
  kind with a field, so that a list can show them the way the reference
  simulator does. **Shipped in v0.4.33, with two deviations from that minimum
  scope recorded here rather than silently taken.** First, the height is
  stored as a multiple of the running agent's 1 MAC rather than as a percent of
  it. Every compartment is already read in that unit. So a target is compared
  against the readouts with no conversion, and it survives a change of agent
  intact. Second, the rising/falling/either crossing direction is **withdrawn
  rather than met** (project owner, 2026-09-20), for the reason that the class
  `MacTarget` in `app/bookmarks.py` records. Halting at a mark is the entry below, PL-CTD7.
- **Crossings are detected inside the advance loop** (queue item PL-CTD7), with
  an explicit not-reached outcome that looks different from a reached one.
  Testing once per rendered frame overshoots by one frame's worth of simulated
  time, and the overshoot grows with the playback multiplier. The same
  bookmark would then halt at a different concentration depending on how fast
  the learner was running. That is a presentation-correctness failure by
  `CLAUDE.md`'s standard. It also breaks the reproducibility of any branch
  taken at that point.
- **A run forks at any control-input event** (queue item PL-TFX5), flat rather
  than as a tree: one trunk with N branches, and no sub-forks. The branch
  carries its parent's agent and patient rather than choosing them again.
- **A bookmark is a forkable instant** (queue items `PL-B8MK` and `PL-TYWQ`),
  so a branch can be taken where a learner deliberately stopped, not only where
  they moved a control. Opening the branch's definition at the keyframe
  *before* the bookmark costs the trunk nothing, and it is exact. **Shipped
  2026-09-20 on that route**, as `SimulationController.resumed_at_halt` and
  `BranchedCase.fork_at_halt`. No keyframe is recorded anywhere, and the trunk
  matches, element for element, the case it would have been unmarked. This
  item waited behind the two items that build the bookmark and the halt where
  the branch is taken (`PL-LPLD` and `PL-CTD7`). Both closed the same day. This
  item remains ahead of the entry below, because that entry's brief
  (`PL-Z3W6`) requires a branch "taken between two of them" (between recorded
  samples), and this item provides that branch.

  **The interface half of forking at a bookmark shipped 2026-09-21**
  (`PL-TYWQ`). The fork panel landed on a different branch on 2026-09-20
  (`PL-VKJW`) and offered only the trunk's keyframes as fork points
  (`BranchedCase.fork_points_s`). Forking at the halt is now a **second
  control** beside the panel's fork-point selector. It appears only while the
  trunk is stopped at the halt, and it is labelled with the instant at which
  the branch will open (project owner, 2026-09-21, ratified, over one list that
  grows a row while the run is halted). The reason is that a row that comes and
  goes would change the selector's list under someone who looked away. A
  control that is either there or not can be detected on sight. The two ways to
  fork stay as two methods and two fields rather than one list. That is what
  stops a fork being requested at a mark that the run has already left. This
  entry completes with that sequence, which is why it names both `PL-B8MK` and
  `PL-TYWQ`.
- **The branch reproduces its parent element-wise up to the branch point**
  (queue item PL-Z3W6). A test asserts this at every sampled point, rather
  than within a tolerance. Where exactness cannot be reached, the divergence
  is bounded, documented and shown, rather than implied to be absent.
- **Two branches are overlaid on one time axis** (queue item PL-8PSW). The
  **compartment is encoded by line style and colour, exactly as the single-run
  chart draws it. The run is encoded by line width. At most two compartments
  are drawn while two branches are shown.** The branch point is marked. Two
  stacked panels sharing a time axis were decided against (project owner,
  2026-09-06). The comparison is the whole point of the release, and stacking
  makes the eye travel to make it. The evidence supports that choice. Line
  graphs that share one space are the more efficient technique for
  comparisons over *small* visual spans. Comparing one compartment against
  itself under two settings is that kind of comparison (Javed W, McDonnel B,
  Elmqvist N. *Graphical Perception of Multiple Time Series.* IEEE Trans Vis
  Comput Graph. 2010;16(6):927-34. doi:10.1109/TVCG.2010.162).

  **Which run carries the width offset was settled when it was built**
  (`PL-8PSW`, 2026-09-16, project owner). The first run is drawn wider, and the
  second keeps the width that the single-run chart draws it at.
  `docs/INTERFACE.md` § "The six compartment traces" carries this decision.

  **The channel assignment is reversed from what this bullet said until
  2026-09-07, and the compartment cap is what makes it possible** (`PL-HLD5`).
  The bullet read "the run encoded by line style and the compartment by
  colour". The next day `PL-GVXP` established that this assignment is not
  available. `docs/INTERFACE.md` § "The six compartment traces" measures the worst
  trace-against-trace pair at **1.01:1**, against a 3:1 requirement. So colour
  cannot carry six categories here, and choosing a new palette does not fix
  that. Line style is the only non-data channel with capacity for six
  categories, so the compartment keeps it.

  That leaves no channel free for the run at six compartments. Line style,
  colour and width are all already used, with width varying from 2 px to 3 px
  across the six. **Capping the drawn compartments is what frees width.** That
  is why the cap is load-bearing rather than a convenience. It is also why "one
  shared compartment selection across both runs" is now a constraint that the
  design rests on, rather than an interface nicety. Two compartments times two
  runs is four curves, which is also the comparison a learner actually makes.

  **Colour keeps meaning "compartment" in both modes, deliberately.** Handing
  colour to the run would make one channel mean two different things on either
  side of a mode change. On this chart, a misread is a misread of a clinical
  value. If two compartments prove too tight in practice, the fallback is three
  compartments, with the run moved to a direct label at each curve's end.
  Position is the strongest channel available, and it is the one that
  survives every colour-vision deficiency. But that fallback is a change to
  test rather than to assume.
- **A learner takes the fork, and the dashboard comes to hold the branch**
  (queue item PL-VKJW). This is the entry the milestone was missing. Added
  2026-09-20 (project owner, 2026-09-20, `PL-XJ37`). What
  this entry delivers is this milestone's Goal sentence, word for word.

  **Two dispositions are settled in that item's brief rather than left to its
  pull request.** First, a **second fork is refused while a comparison is
  shown**. The selector is out of scope, so a learner who forks twice has no
  way to say which branch is displayed. Quietly swapping the displayed branch
  while the first one lives on in the `BranchedCase` would be the hidden state
  that this project refuses. There is one comparison at a time, and Reset is
  how the next one starts. Second, **a branch's `RunView` shows the
  running-agent chip in place of the agent dropdown**. The reason is that
  `SimulationController.set_agent` already refuses on a branch (`PL-TFX5`). A
  control that always refuses is a control presenting itself as working.

- **What the readouts show while two branches are displayed** (queue item
  PL-1XPX). This is a decision rather than an implementation. A numeric
  readout that does not say which run it describes is a safety-critical
  failure, because this project treats presentation as part of safety. There
  is more than one defensible answer.
- **The chart's hover says which run it is reading** (queue item PL-MN4J).
  The item is `safety`-classed. It is milestone-scope debt under § "Debt
  inside the milestone's own scope", not debt that this gate can clear. A
  hover that names the agent and the instant but not the run is ambiguous only
  while two runs are drawn. That happens only in this milestone's own compare
  mode, so the item cannot be cleared before the compare mode it is about.
  Until that mode ships, there is one run on the chart, and the hover names
  everything there is to name. Like `PL-1XPX`, it is a decision rather than an
  implementation, and the decision is the project owner's. It amends
  `docs/INTERFACE.md` § "The chart's hover readout: what the tooltip may show",
  which derives the three-line form, so no session can close it either way.
  `PL-8PSW` shipped the legend and panel naming that make a curve attributable
  today. This item covers the remaining surface. The definition of done
  requires "no readout, label, legend entry or reference band ambiguous as to
  which run it describes", and that requirement is what keeps this item in
  scope.
- **What a comparison asserts and what it does not** (queue item PL-W7H9), in
  `docs/MODEL.md` and `docs/ARCHITECTURE.md`. It states what two branches
  share and what they do not. It states that a difference between them can be
  attributed only to the settings that differ. It also states that neither
  branch is a prediction for a patient.

### Definition of done

v0.5.0 is complete only when:

- a branch taken at any recorded control event or bookmark reproduces its
  parent element-wise at every sampled point up to the branch point, and a test
  asserts this;
- a time bookmark or MAC target halts the run on the step that crosses it, at
  every playback multiplier, and a test asserts this;
- a MAC target that is never reached ends in a distinct, visible outcome rather
  than in silence;
- two branches can be read on one time axis, and every curve is attributable to
  its run and to the settings that produced it, with no readout, label, legend
  entry or reference band ambiguous as to which run it describes;
- the memory a run holds is bounded by its number of control events rather
  than by its length, and no sample store remains in `src/`;
- `docs/MODEL.md` states the canonical evaluation rule, what a comparison
  asserts and what it does not, and the bound on any divergence that could not
  be eliminated;
- every item of the frozen list above that is outside this milestone's
  Required scope is `done`, is `dropped` with its reason recorded, or is
  deferred to a later gate on the terms of beat 3 of § "The cadence";
- the v0.0.2 circuit, v0.1.0 sevoflurane and v0.2.0 multi-agent reference tests
  remain unchanged and pass, and no equation, parameter or governing constant
  has changed; and
- Ruff formatting and linting, strict mypy, pytest, `docket check`,
  `tools/doc_check.py` and GitHub Actions all pass.

### Explicitly out of scope for v0.5.0

- **Completing the fork and bookmark interaction beyond what Required scope
  and the definition of done already name** (project owner, 2026-09-21,
  ratified, over widening this milestone to close the interaction gap before
  cutting). The project owner described the shipped surface as "a bit of a
  mess with forks and bookmarks ... half implemented in terms of user
  interaction". The count supports this: on 2026-09-21, nine open items
  concerned that surface.

  **Four of the nine open items on forks and bookmarks stay in this
  milestone and are not deferred.** One is in Required scope above. Three fall
  under the definition of done's requirement of "no readout, label, legend
  entry or reference band ambiguous as to which run it describes". **The five
  left out** are `PL-W4XQ` (there is no way back to a mark set behind the
  clock), `PL-ZW0J` with `PL-8XMV` (whether returning to a mark forks or
  truncates, and the setting that chooses between the two), `PL-LLBV` (the
  check that a fork instant is a whole number of 0.1 s steps, measured on
  2026-09-14 to refuse 35.5% of the one-decimal times from 0 to 3600 s, then
  dropped on 2026-09-27 as unreachable), `PL-7TBQ` (`has_recorded_run` is true
  before the learner has touched the branch) and `PL-3QSX` (the unit of a
  listed MAC target).

  **The five fork and bookmark items that v0.5.0 leaves out belong to Gate 2
  by design, not by deferral.** Gate 2 (timeline row 6) froze on 2026-09-21,
  the day this milestone shipped, and is cleared before v0.6.0's implementation
  begins. So the interaction debt is paid before planned-milestone item 34's
  area system is built on top of it. § "The cadence" already arranges this for
  findings made inside a milestone.

  **One open question, not the schedule, kept the rest of the interaction out
  of this milestone.** The question is whether returning to a mark forks, or
  truncates after a confirmation (`PL-ZW0J`). The answer decides what taking a
  branch does. The project owner deferred that question on 2026-09-20 because
  they wanted to use the feature first. Widening v0.5.0 to complete the
  interaction would settle the question without the use it was deferred for.
  So the milestone is cut on the definition of done it already states.
- Sub-forks of forks, and any branch structure other than one trunk with N
  branches (project owner, 2026-08-25).
- More than two runs displayed at once, **and the selector that would choose
  which two** (project owner, 2026-09-20, `PL-XJ37`). `BranchedCase.branches`
  returns the branches in a stable order, chosen so that a later selector does
  not renumber the branch a learner is looking at. But **Selecting which two runs are
  displayed** is not built here. A comparison is always of a branch against
  the trunk. The milestone also does not return to a branch the learner has
  left.

  The selector was declined on the educational question, not the technical
  one. The display is capped at two runs under either answer. So a selector
  buys the *choice* of pair, not more curves, and branch-against-branch was
  judged not to be a teaching case for a first release. Adding the selector
  later is additive rather than a rework. The Required-scope entry for the
  control that calls `fork_at` settles what happens when a learner forks twice.
- Scenario save/load (item 9), including persisting bookmarks or branches
  across a restart, and a user-facing deterministic replay control (item 10).
  Only the resimulation driver that replay needs is in scope.
- The anesthesia-machine abstraction, interlocks, agent switching with residual
  washout, direct injection and end-tidal control (items 1-5).
- Nitrous oxide, coadministered gases and the concentration and second-gas
  effects (items 6-7), and the multi-substance patient state behind them.
- A schematic compartment view (item 27) and agent cost (item 28).
- Patient factors (age, sex, weight and body composition) and any change to
  the MAC basis (item 30).
- Horizontal panning of the chart window (queue item PL-Z7LY). Panning is
  still optional, because the default "Fit run" time scale always shows the
  whole run.
- Any change to the governing equations, the parameter set, or the exact
  solution the matrix exponential computes. This milestone changes the
  questions the model can be *asked*, never the answers it gives.

## Completed: v0.6.0 - the layout is the reader's

**The vocabulary is Blender's for two of its three words**
(`.claude/rules/ui-areas.md`). An **Area** is a rectangle that reserves screen
space and holds one thing. A **View** is what occupies an Area. A **Workspace**
is a set of Areas geared to a task, and Workspaces are switched as tabs.

**The third word is deliberately not Blender's** (project owner, 2026-09-17,
ratified - chosen over keeping `Editor`, and over `Component` and `Widget`).
Blender calls an Area's occupant an **Editor**, and most of Blender's editors
do edit: the 3D viewport, the dope sheet, the text editor. This project's
occupants are the concentration graph, the compartment table, the MAC readout
and the control panel. Only one of the four takes input, and the other three
display modelled values. So `Editor` would assert a mutability that the reader
does not have. `CLAUDE.md`'s clinical-output standard treats that class of
wrong implication as a presentation defect. `PL-GPYV` carries the comparison
and the Eclipse precedent.

This milestone is the first half of planned-milestone item 34. It was scoped
two releases ahead of its turn (project owner, 2026-09-16, **ratified** on
`PL-NMTF`), because the design was already settled and fourteen prerequisites
were waiting on a build item that did not exist. The placement, the split and
the gate decision were all recommendations put to the owner and agreed. So
`CLAUDE.md`'s lower bar to reopen applies to each of them. What the owner
*specified* is item 34's own content, which this milestone builds rather than
re-decides. Item 34 carries the design and the Blender provenance behind every
decision below. `docs/interface-provenance.md` carries what was read, what
this project adopts and what it deliberately does differently. This section
describes what gets built.

### Goal

The end state is as follows. A learner divides a window into non-overlapping
Areas, each holding one View. They switch between named task Workspaces as
tabs. They rearrange, duplicate and save their own Workspaces, and return to
them at the next launch. Throughout, the values the display is required to
show cannot be closed, cannot be collapsed to make room, and cannot leave the
screen with the surface that drew them.

The dashboard has one arrangement, and the learner cannot change it. Every
surface is already an independent widget inside nested splitters whose handles
are disabled. That is `inert_splitter` at
`src/anesthesia_sim/app/qt_widgets.py`, the reservation that v0.4.26 built and
did not make live. So the only way to see a chart larger is to make the whole
window larger. As things stood on 2026-09-16, the day this milestone was
scoped, there were three gaps:

- **Nothing can be resized, split, joined or swapped.** The handles are inert
  by deliberate reservation, and no set of operations sits behind them. Item 34
  requested four properties: resizable areas, modular views, presets for tasks,
  and presets that the learner owns rather than a fixed shipped set. None of
  the four is available.
- **There is no object above the widget tree.** There is no layout model, no
  View registry, no Workspace, and no user-writable state of any kind. Nothing
  under `src/anesthesia_sim/` writes a file, so a layout cannot be named,
  saved, or returned to at the next launch. A saved Workspace would be this
  application's first user-written data. Its load path would be the
  application's first new failure surface since the shipped parameter files.
- **What the display is required to show sits inside the container that is
  about to become live.** `src/anesthesia_sim/app/simulation_view.py:296-309`
  puts the readout section inside `inert_splitter`. That section holds
  simulated time, the rate at which time is advancing, the six compartment
  concentrations and the delivered concentration. The control-input record's
  panel sits in the sidebar, inside the nested horizontal splitter. Only run
  state, halt reason and agent identity are outside the container. So on the
  day the handles work, a learner could close the values that `docs/MODEL.md`
  says no Workspace may remove. The violation is pre-loaded (already built in)
  rather than absent.

### Debt gate: the frozen list

**Frozen 2026-09-21, the day v0.5.0 shipped.** This milestone was scoped out of
turn on 2026-09-16. Its list therefore froze on the later of the two days that
§ "The debt gate" -> "The cadence" names, which was the day v0.5.0 shipped.
Gate 2 contains v0.5.0's findings, and v0.5.0 is now implemented and released.
This list contains every open item that is debt by the definition in § "The
debt gate" above, as the store recorded it on the day of the cut.

**Thirteen entries were untriaged when this list was frozen and are on it all
the same.** They were open in the store on the day of the cut, and the
paragraph above says that is what this list contains. They had not been
*classed*, though. An untriaged capture carries no class, so the tool that
prints a gate's list (`bin/docket gate`) could not treat one as debt, however
old its problem was. Triage on the same day gave eleven of them `defect`, some
with `infra` or `test` beside it. It gave one `refactor` and one `perf`. Each
of these entries describes code that predates the freeze, so they re-enter by
the presumption in "The gate is a snapshot, not a moving target", not by the
exception that admits a `safety` finding regardless. The thirteen are
`PL-3QM9`, `PL-5DPF`, `PL-B78T`, `PL-CR36`, `PL-CZR6`, `PL-HVLJ`, `PL-JS0X`,
`PL-KZR1`, `PL-M6FY`, `PL-N0MH`, `PL-N67T`, `PL-NPWP` and `PL-YSMV`.

**The list was swept for staleness on the day it froze.** Beat 3 of the
cadence requires a staleness pass before any entry on this list is worked, and
§ "Sweep the frozen list for staleness" says why and how. The pass ran on all
168 clearable entries on 2026-09-21 and shipped in v0.5.1 (`PL-C4W8`).

**The list has two kinds of entry, and only the second is a precondition for
this milestone.** The first kind is debt inside this milestone's own Required
scope, which the milestone clears itself, as
§ "Debt inside the milestone's own scope" says. The second kind is the rest. It
clears before implementation of this milestone begins, unless this gate defers
it. It is recorded in one group, for the reason § "Recording it" gives for not
naming lanes. The test for the first kind is whether `Required scope` below
names the id, not whether the item carries the `interface-areas` feature. The
two tests differ in both directions. On 2026-09-23 `PL-NDKC` and `PL-Y04W`
carried the feature without being named. `PL-CNCF` and `PL-PGZF` were named
without carrying it, as they have been since `PL-YVP7`.

**One disagreement is `PL-NDKC`**, a `defect`/`infra` item about a PySide6
`QDataStream` segfault. The Qt code built around the layout model could meet
that segfault. It was first expected in the JSON persistence path, but that
path decodes no Qt blob, so it cannot meet the segfault. The item carries the
milestone's feature but is not in `Required scope`. So it clears before the
milestone rather than inside it, and it is on the list with the other entries
that do.

**What this gate defers is not a group: it is each entry's `deferred-from:
v0.6.0`** (`PL-8QMD`, project owner, 2026-10-11, ratified, over keeping the
deferral group headings, read through `blocked-by`, with a check per reader).
§ "Deferring to the next gate" gives the terms. `wave` counts a deferred entry
separately from what this gate can clear. Gate 3 freezes when v0.6.0 ships and
clears before the implementation of v0.7.0 begins. The paragraphs below record
the decision behind each deferral.

**`PL-Y04W`, the break-out build item, was deferred to Gate 3 when this list
froze, and dropped on 2026-09-26, when break-out came off the timeline**
(project owner, 2026-09-26: wanted eventually, not soon; `PL-V1Y7`). No release
builds break-out now, so the deferral has no release to clear before. An
eventual feature is recorded as intent in planned-milestone item 34, not as an
`L` item waiting in the queue. A dropped entry clears this gate in the same way
as a fixed one, as beat 3 of § "The cadence" says. Nothing that the entry
guarded is lost with it. The rule that a break-out build must satisfy is
`docs/INTERFACE.md` § "Minimum displayed outputs" -> "What this list requires once
the layout is the reader's". Item 34's entry cites the brief for the Qt
measurement that the build will need first.

**Five entries are deferred to Gate 3 on § "The cadence" beat 3's terms**
(project owner, 2026-09-27, ratified, over keeping them on this list, where
they would hold the gate open until planned-milestone item 28 and a machine
chooser are scheduled; `PL-DB64`): `PL-WZVZ`, `PL-B396`, `PL-0S0V`, `PL-VJZK`
and `PL-KZ99`. Beat 3 clears this list before implementation of v0.6.0 begins.
None of the five can close before then, in whatever order the rest is worked:

- `PL-WZVZ` waits on this milestone's own View contract `PL-TH35` and view
  registry `PL-R1WQ`, so it is unworkable until implementation has begun, and
  then on `PL-TBMK`, a second machine profile, and `PL-4TWW`, the surface that
  selects between profiles, which no release schedules.
- `PL-B396` is the liquid-volume readout planned-milestone item 28, agent
  cost, would build, and waits on `PL-YRLM`, which holds whether a release
  schedules item 28. None does before v0.6.0.
- `PL-0S0V`, `PL-VJZK` and `PL-KZ99` each wait on `PL-B396`, because each is
  work item 28 would create: a reader-selectable agent unit and its precision,
  a reader-set price, and the molar mass and liquid density a vapour-to-liquid
  conversion needs.

The deferral names **Gate 3**. v0.6.0 ships without the five. Waiting changes
nothing about them. Unless a release schedules item 28 or machine selection
before v0.6.0 ships, Gate 3 inherits all five, as this gate inherited
`PL-WZVZ`. Gate 3 then owes them the same disposition. That includes `PL-B396`,
whose `ux` and `docs` classes are not debt. It is included because `bin/docket
gate` prints every open entry of this list beside the store's open debt, with
each deferral marked, and the freeze carries all of them (`PL-JV5Q`).

**`PL-WZVZ` is inherited rather than found here.** It is Gate 1's one deferred
entry. `PL-S5Q9` deferred it on § "The cadence" beat 3's terms. It is still
written on v0.5.0's frozen list, where removing it would have been the
renegotiation that a freeze exists to prevent. The condition it waits on is
recorded in `PL-0H5D`'s field rather than in prose. It is `safety`-classed, so
it took that route only because the gate section that records it also records
that its hazard is not live, read against the tree.

**Four of the five are `safety`- or `science`-classed, and no hazard among them
is live, read against the tree at `19af95d` rather than asserted.**
`src/anesthesia_sim/data/machines/` contains one profile. It is loaded by name
through `core/parameters.py`'s `load_reference_circle_system_parameters`.
Nothing in `src/` selects between profiles, and no label in `app/` names a
machine. So no displayed difference can be misattributed between machines
(`PL-WZVZ`). Agent amounts are displayed in one fixed unit,
`app/dashboard_frame.py`'s `ACCOUNTING_UNIT_CAPTION`, with no selector. So
displayed precision still belongs to one quantity (`PL-0S0V`). Nothing in
`src/` stores or displays a price, a currency or a cost (`PL-VJZK`). Nothing
there stores or displays a liquid volume, a density or a molar mass either. So
no vapour-to-liquid conversion exists that could rest on a composite constant
(`PL-KZ99`). Each entry is owed its band the moment its condition lifts. The
conditions are a second profile or a surface naming a machine, a selectable
agent unit, a stored price, or a liquid figure. `PL-B396` is classed `ux` and
`docs`, so beat 3 asks for this record only of the other four.

**`PL-5B1N` is deferred to Gate 3 on the terms of § "The cadence" beat 3**
(project owner, 2026-09-27, ratified, over building the preview now as the
next item of the presentation-safety chain; `PL-YBFB`). `PL-5B1N` is the
preview that a control draws while it is grabbed and not yet released. The
preview shows the trajectory that the new setting would give. It sits inside a
tinted region to the right of the run's reach, with a label in the plot. The
presentation-safety design round settled that design on 2026-09-27, and the
item's brief records it. That cleared nothing on this list, because an entry
clears only at `done` or `dropped`. What is left is an M build of an entry
classed `feature`. It was on this list only because it was at `needs-decision`
on the day of the freeze. Building it before v0.6.0 begins would put a feature
in front of the layout milestone, and the owner made that scheduling choice
the other way. Nothing is done twice, whichever gate builds it, because the
preview draws on the pyqtgraph chart, and v0.6.0 wraps that chart in an Area
rather than rewriting it.

The deferral names **Gate 3**. v0.6.0 ships without `PL-5B1N`. Gate 3's freeze
takes it up even though a `feature` entry is not debt. `bin/docket gate` prints
every open entry of this list beside the store's open debt, and the freeze
carries all of them (`PL-JV5Q`).

**Its hazard is not live, read against the tree at `9ea31db2`**. This record
is kept even though beat 3 asks for it only for an entry classed `safety` or
`science`. Nothing under
`src/anesthesia_sim/app/` draws a predicted trajectory. The one widget named
for a preview is the bookmark dialog's `instant_preview`, and it shows a chosen
instant in the clock's form. A run also cannot be asked for a predicted
trajectory. `core/run_definition.py`'s `_require_within_run` refuses any
instant past the run's reach as "a prediction rather than the run". So nothing
on screen can be mistaken for a prediction. The item's brief names three
failure modes: a preview that outlives the interaction, a preview that carries
the run's visual weight, and a preview that reaches a screenshot without a
label. Whoever builds the preview is bound to prevent all three.

**Cleared by v0.6.0 itself - 18 entries**

- PL-9LNF (L) Three app/ surfaces own state a layout could duplicate or relocate beside PL-VN6M's TraceLegend: RunView's build_ accessors hand out the same widget object on every call, the chart time base is owned by a dropdown inside one plot's panel, and the chart's column budget is read from sibling plots
- PL-NWTM (L) The unconditional displayed set has no structural home in the code, so the guarantee docs/MODEL.md states as structural - a region outside the area system - exists only as prose
- PL-50PZ (M) Build the View chooser and the registry's required-reachable flag, which is what makes docs/MODEL.md's accounting tier reachable from every Workspace and not removable from the application
- PL-7Z84 (M) A run has no identity a workspace can pin to - the dashboard addresses runs by their position in its own drawing order, and ROADMAP item 34 commits a workspace to pinning which run it shows
- PL-904Y (M) Split the whole-interface visibility predicate out of PL-W54S: interface_strings answers is-this-string-in-this-widget-subtree, which stops meaning can-the-reader-see-it once a layout can close an area or move it to another window
- PL-CNCF (M) controller.drawn_window costs 6.2 ms a frame at the shipped 150-column budget - 99% of the frame's read and about eighty times the simulation at 1x
- PL-F2YS (M) The unconditional region opens a 1366 px laptop's readout row on four columns and stacks two runs' readouts in two rows where docs/MODEL.md pairs them in one, so compare mode leaves the chart below its 360 px minimum
- PL-G5SX (M) Headless tests that drive every layout operation and assert after each that the unconditional display set is still on screen, that the accounting tier is still reachable, and that a required value never left with the surface that drew it
- PL-K285 (M) An Area that cannot be given the size its View needs says so rather than collapsing it, which is the second of the three properties docs/interface-provenance.md records Blender not supplying
- PL-L8RN (M) Nothing enforces the one-adapter QSplitter confinement PL-C842 decided, because import_boundary_check.py confines root packages and PySide6 is one root package
- PL-NNML (M) The dashboard page still scrolls at laptop window heights, so the use disclaimer is below the fold and scrolling to it moves the unconditional region out of view
- PL-PGZF (M) PL-GS3R made the chart's column budget follow the window width, so assemble_chart_frame costs 8.4 ms at 150 columns and 15.4 ms at 1601 - PL-CNCF measured only the fixed 150-column budget, and 15.4 ms is essentially a whole 60 fps frame
- PL-QLZ5 (M) In compare mode, fold each run's transport row and readout heading line into one line, so the 1366 by 700 laptop reference gives the concentration chart back roughly 70 to 80 px (PL-JG82)
- PL-TH35 (M) Define the common View contract every app/ view implements so any view is interchangeable in any area
- PL-VN6M (M) TraceLegend owns the compartment-visibility state inside a widget, which an area system will have to move out
- PL-W54S (M) Decide what a broken-out top-level window owes docs/MODEL.md's unconditional display set, which PL-WLWY named as its own real work and then closed without choosing between its three readings
- PL-JG82 (S) Compare mode leaves the concentration chart about 200 px on the 1366 by 700 laptop reference, 159 px under PL-84QX's 360 px minimum, after PL-F2YS paired the readouts
- PL-JSY5 (S) docs/MODEL.md's readout-row rung and its educational-disclaimer line both assume one window's width and one always-on-screen surface, which the area system makes false

**Cleared before v0.6.0 begins unless deferred - 229 entries**

- PL-08CR (S) Decide whether format_time_bookmark and format_mac_target survive now that bookmark_panel builds every drawn row from the _stated_ helpers
- PL-0FJ8 (S) A MAC divisor's positivity is checked in five app/formatting.py functions and by nothing that holds it: AgentParameters admits Percent(0.0) built directly, only the loader's PositivePercent refuses one, and format_mac_reference checks nothing, directly or through another
- PL-0SG0 (S) Meybohm et al. 2021 Table 1 prints Gas Man 4.2's 1 MAC as 2.1% sevoflurane and 1.1% isoflurane where the three agent files store De Wolf et al. 2012's 2.0% and 1.2% as the same program's set, and no agent note records that the two tier-3 descriptions of Gas Man disagree on the MAC while agreeing on every partition coefficient
- PL-0S0V (M) AGENT_VOLUME_DISPLAY_DECIMALS and the other display-precision constants are one Final per quantity, but once the unit is reader-selectable precision is a function of quantity AND unit, and docs/MODEL.md's derivation has to be per-unit too
- PL-19Y0 (M) A direct write to a checked field of BreathingCircuit, VenousBloodCompartment, TissueGroup, AlveolarCompartment or AgentSimulationValidator skips every check its constructor and setters make: a sevoflurane dial of Percent(50.0) past its 8% vaporizer maximum, a bare-float dial, a zero circuit volume, an inspired fraction of 1.5 and a venous agent amount past capacity are each accepted; only the three flows are guarded (PL-LBQY), and PL-544D covers the alveolar and tissue agent amount alone (found sweeping PL-ZGYX)
- PL-0YYV (L) The three flows - fresh gas flow, alveolar ventilation and cardiac output - are bare floats range-checked by hand at each way in, so the way in nobody checked, UptakeEquationSettings, ran a cardiac output of 1000 L/min (PL-HSFV); slice 1 of PL-51B7 gives each a checked type built only through its require_supported_* guard, as SimulationStep is for the step
- PL-1DP1 (S) fraction_from_percent and percent_from_fraction take a bare float as given, so percent_from_fraction(0.5) from a caller mypy does not read is a Percent of 50.0 and format_percent(0.5) prints 50.00% whether the 0.5 was a fraction or a 0.5% dial, where every place a concentration is held refuses a bare float since PL-4R3W; whether the two crossings require the checked form too, or keep taking a number nobody built because it carries no form to refuse it by, is undecided (found building PL-SWD1, which refuses the other form and every other checked quantity there)
- PL-1K9G (M) Which grid column a trace answers a hover at is decided in two dimensions, so a purely vertical 2 px move can change the instant a value is labelled with
- PL-1ZQ4 (M) A mark added after the step that crossed it is answered three ways: the trunk reads a late MAC target as not reached where a branch opened on that step reads it reached, a mark added to a branch after it opened is never asked of its opening step, and fork_at at a keyframe the trunk halted on opens on no crossing where fork_here opens on the halt's
- PL-2MD9 (M) "The propagator's constant state row drifts and the squarings amplify it: 2.28e+222 at an alveolar volume of 1e-19 L, where governing_equations.UNIT_STATE promises no step can perturb it"
- PL-3800 (S) require_positive_finite and require_nonnegative_finite admit True (BreathingCircuit(circuit_volume_l=True) holds True, a 1 L circuit) and a Decimal (AlveolarCompartment(gas_volume_l=Decimal('2.5')) holds the Decimal), and refuse a str with math.isfinite's own TypeError, so every field they guard and SimulationStep, whose guard is built on the first, have the holes PL-LLMN closes for the flows and the concentrations; none is reachable from the interface; bring both guards to require_a_number in core/checked_number.py (found working PL-LLMN)
- PL-3JP0 (S) Decide whether the wash-in section's three paragraphs survive the same test PL-6580 applied to the chart panel above it
- PL-4R3W (M) Fraction and Percent are NewTypes, which the interpreter erases, so their ranges of 0 to 1 and 0 to 100 are checked by hand wherever a value enters - require_percent at four sites in circuit.py and governing_equations.py - the hand-checked pattern PL-51B7 replaces with checked types for the supported-range quantities; whether a concentration becomes a checked type too is undecided, because concentration.py chose NewTypes to catch a missing conversion, and whether a fraction computed at a bound can round past it is unmeasured
- PL-51B7 (M) The supported-range edge test finds the functions behind the six guards other than the step's by parameter name on five classes kept by hand, so a function taking a guarded quantity under another name, RunDefinition's opened_at_s, is never drawn; a checked type per quantity, as SimulationStep is for the step, would let it find every one by type
- PL-5291 (S) A branch built standing on the 24 h supported run length still offers Start, because SimulationController._open_at never sets _supported_limit_reason, the only limit signal the transport's stopped state reads, against Transport's own docstring
- PL-544D (M) AlveolarCompartment and TissueGroup admit a direct write of agent_amount_l past the compartment's capacity, so the quotient the display reads can leave 0 to 1 while every setter refuses it: PL-7DJK's case 1 is reproduced by that write, and test_a_halt_is_shown_when_the_snapshot_itself_is_refused depends on it staying open
- PL-59WB (S) chart_time_base.fit_to_run takes a parameter called run_length_s but is passed a case instant, which is the duration_s-was-not-a-duration defect one module over
- PL-624C (S) test_the_branch_is_drawn_beside_the_trunk_on_one_time_axis draws its own frame, so it cannot detect a fork that fails to redraw
- PL-73ZN (S) RunDefinition bounds opened_at_s below at induction but not above, so a definition may declare an opening past the 24 h envelope the model is claimed over
- PL-7CRY (S) The fresh gas flow slider reads the model envelope alone, so a machine profile declaring a narrower deliverable range would offer settings the circuit refuses
- PL-7DJK (M) A Fraction the display builds can now refuse, and the halt that follows is shown as a failed step, half-drawn, unnamed, or not at all, though no supported setting reaches it
- PL-7N8P (S) require_supported_case_instant admits True (as 1.0 s) and Decimal, and lets OverflowError escape for an int past the float range (CaseInstant(10**400)) rather than refusing in the simulator's words - the shape PL-LLMN records for the flows' _require_supported, so decide the two together; none is reachable from the interface (found reviewing #1354)
- PL-7TBQ (S) SimulationController.has_recorded_run reads elapsed_s > 0.0, so it is True the instant a branch is made and before the learner has touched it
- PL-85LJ (S) A slider dragged on a run whose snapshot refuses leaves its value label on the previous value while the dial and the circuit hold the new one, because only refresh rewrites it and no frame draws after the halt (found at PL-V2HC's review)
- PL-7TXJ (M) RunDefinition.record_change rebuilds the whole segment tuple per change, and each segment carries a keyframe, so it is the larger of the two unbounded records
- PL-8W1W (S) SimulationState.step_count and simulation_step_s can be assigned after construction without any check - state.step_count = 5 stores a bare int, and = -3 after a step makes elapsed_s raise - the shape PL-LBQY records for the compartments' flows, on the run's own state; nothing in src writes either outside advance and reset; decide it with PL-LBQY: a __setattr__ guard, read-only fields, or the window recorded as accepted (found reviewing #1354)
- PL-921Y (S) docs/MODEL.md's first-24-hours subsection compares the model's isolated muscle time constant with Yasuda's fitted one, which is an apparent constant read off the whole washout curve; read the same way, off the eigenvalues of the model's open-circuit system, the model's muscle term runs 1.9 to 2.0 times the fitted one at about half its amplitude (measured 2026-10-03), not 1.5 to 1.7
- PL-95NW (M) Test whether the model's slower muscle return explains the open-circuit washout tail's closest approach to Yasuda's fitted mean curves over hours 2 to 4, by varying the muscle tissue:gas coefficient in the late-washout module; docs/MODEL.md's first-24-hours subsection records that reading as inferred from the isolated time constants and not tested (PL-KK1Q)
- PL-979Z (M) CaseInstant and the three flow types are built from another checked quantity silently - CaseInstant(StepCount(600)) is an instant of 600 s, CaseInstant(FreshGasFlow(5.0)) one of 5 s and FreshGasFlow(CaseInstant(5.0)) a flow of 5 L/min - because require_a_number admits every int and float subclass and only the stored-value checks (require_case_instant, _require_built) name a swapped quantity; refuse another checked quantity at the constructor, as Fraction refuses a Percent (found reviewing PL-7N8P)
- PL-9YHR (L) The published-data gates cannot resolve most stored parameters - fat tissue:gas x2 and x0.5, fat volume x2, muscle tissue:gas x1.5 and vessel-rich tissue:gas x0.8 each pass every Yasuda-tied assertion, and only 6 of 25 simulation-affecting x1.10 perturbations fail one - while the gate's resolving power is recorded only for alveolar ventilation and cardiac output
- PL-B26Y (S) BreathingCircuit.advance_fresh_gas reports a nan exhaust at an admitted fresh-gas flow below about 2e-306 L/min, because the circuit's time constant overflows to inf there and its zero-flow branch tests == 0.0 only; core/__init__.py says the branch agrees with the general path bit for bit at the smallest denormal, which holds for the fraction and not for the exhaust
- PL-BBMG (M) RunDefinition accepts a delivered concentration above the agent's vaporizer maximum - 20% sevoflurane against an 8% maximum ran on 2026-10-04 - because UptakeEquationSettings carries no agent and no vaporizer maximum, so a run built from a settings record bounds the dial only at 100%, and the BreathingCircuit that refuses it is never built
- PL-BMY5 (S) SimulationState can be constructed already past the supported run length, and only the next advance refuses it
- PL-CBDX (M) Read every simulator diff merged unread since 2026-09-23 against the safety-critical standard, since the review hold was clicked through rather than read
- PL-CM1B (M) Desflurane's F_A/F_I rises 1.7 to 2.1 published SD faster than its Anesthesiology 1991 cohort from 1 to 10 minutes with F_I held at the airway, while the same volunteers' isoflurane and the sevoflurane cohort follow their curves, so something only desflurane has is too low
- PL-CN5S (M) A case instant and a run's step count are a bare float and a bare int checked by hand where each enters - require_supported_case_instant at RunDefinition's two ways in, _require_step_count in SimulationState - so a new way in for either repeats the check or skips it; slice 2 of PL-51B7 gives each a checked type, CaseInstant in s and StepCount, an int subclass checking what a count can be checked for alone
- PL-CZTR (S) ResumePoint.elapsed_s is the fork instant on the case's axis and should be named fork_instant_s, now that the definition's own instants are instant_s
- PL-DBGT (S) desflurane.json points at 'the five other candidates ruled out' in a MODEL.md table that now has nine rows, and names tests/reference/test_published_wash_in.py, which does not exist
- PL-FPY2 (M) A wrapped mark row's continuation can be a whole clause naming a run, so it reads as a row of its own and binds to the wrong mark
- PL-H1JH (M) Sevoflurane's and isoflurane's MAC-awake fraction_of_mac and all three agents' standard_deviation_fraction_of_mac have no behavioural oracle or literal pin from the adopted primary source, so a 10% transcription error passes every data-dependent simulator test, and desflurane's one published check passes only by float rounding
- PL-H8QP (S) The two for_agent reads-the-file tests cannot fail when for_agent() stops reading a data file, because the core defaults equal the files' values, so docs/MODEL.md's claim that they catch it holds only for the fresh gas flow
- PL-HBH2 (S) docs/MODEL.md's fat-perfusion note weighs the stored fat flow against Heinonen's PET adipose perfusion alone, though Yasuda 1991's two human washout fits put the fat group's time constant (1,340-2,130 min) and flow (2.1-2.4 mL/100 mL/min) where the stored parameters already sit (1,496-2,603 min, 2.07), so its 'would over-estimate fat loading' reading may be one-sided
- PL-HGB6 (S) docs/machine-abstraction.md says circuit_volume_l is apparatus-plus-circuit where the shipped profile says apparatus alone, so a profile author following the design document would store an assembled total the code does not expect
- PL-HNWX (M) SUPPORTED_SCHEMA_VERSION is one global constant across agents, patients and machines, so a machine-only schema bump drags three agent files and the patient file with it
- PL-HQF5 (M) After PL-KFNP a tissue group's or the venous pool's blood flow is still settable past its patient's cardiac output through TissueGroup.set_blood_flow and VenousBloodCompartment.set_blood_flow, which nothing in src/ but PatientCompartments._update_blood_flows calls, so the record PatientCompartments.__post_init__ refuses stays reachable by a caller mypy does not read and halts only at the next step or at Reset (PL-M4M0); decide whether a compartment's blood flow stays a field of its own that a caller can set (found in PL-KFNP's design round)
- PL-JPS2 (S) Both MAC-awake band tests take their expected band from the snapshot under test, so a band left at the previous agent's values after an agent switch passes the whole suite and the chart would draw sevoflurane's 0.34 x MAC band under desflurane's name
- PL-KFNP (M) PatientCompartments.__setattr__'s type-only guard (PL-LBQY) admits a checked CardiacOutput written past set_cardiac_output and leaves every tissue's blood flow at the old output, a record the core refuses wherever it is next built; root cause of PL-M4M0 and the two items filed beside it, so decide whether the write keeps the relation through set_cardiac_output or is refused outright, which PL-LBQY's three options did not weigh (found reviewing PL-M4M0)
- PL-HSFV (S) RunDefinition propagates an UptakeEquationSettings whose flows are outside the supported ranges - cardiac output 1000 L/min, a hundred times the supported maximum, ran on 2026-10-04 - because the settings record checks only that the tissue flows sum to cardiac output, and the range guards run only in the compartments' constructors and setters, which a run built from a settings record never calls
- PL-J0F7 (S) The Qt chart's hover box was never looked at rendered: its placement flips near the window's right edge and the axis top, and nothing has confirmed the flip lands the box inside the plot or that INK on PANEL in a pg.TextItem is what is painted
- PL-J39J (S) After a cardiac output written past set_cardiac_output halts the run, at the next step or at the Reset PL-M4M0 refuses, the cardiac output readout and dial show the written output beside compartment values and a chart computed at the old flows, under a banner saying the values shown are the last completed step; only the banner's own sentence names both figures (found reviewing PL-M4M0)
- PL-JQY1 (S) max_delivered_concentration_percent is a vaporizer device maximum stored as an agent property, so 18% reads as a fact about desflurane
- PL-JS0X (S) test_the_dashboard_fits_its_window_without_a_horizontal_scrollbar calls build_sidebar_panels a second time and then measures mapTo(page, ...) on panels that are not in the page, so its last two assertions are vacuous and the sidebar they claim to measure has been dismantled
- PL-KK1Q (M) Compare this model's washout over the first 24 h against Yasuda 1991's published five-compartment mean fits, to measure whether the modelled tail runs fast or slow where only the five-minute point is validated today
- PL-KRZW (M) Decide what the interface does under a dark system appearance, now that every colour it declares is a light-theme value
- PL-KZ99 (M) Store each agent's molar mass and liquid density with the density's measurement temperature, so a vapour-to-liquid conversion is derived from a primary measurement rather than from a published composite constant
- PL-KZR1 (S) RunView's build_* methods are split between returning a stored widget (build_notice, build_off_scale_notice) and constructing a new one on each call (build_sidebar_panels, build_readout_section), with nothing in the names saying which
- PL-LBQY (M) A bare float written straight onto a non-frozen compartment field (circuit.fresh_gas_flow_l_min = 1000.0) is caught only at the next equation_settings(), so for one tick the snapshot and the readouts carry an unchecked value and SimulationSnapshot's typed fields carry no runtime check of their own; decide whether a __setattr__ guard or frozen compartments moves the check to the write, or record the one-tick window as accepted (found reviewing #1350)
- PL-LLBV (S) The whole-step guard on a fork instant refuses 35.5% of the one-decimal times a user could type
- PL-LLMN (S) _require_supported admits -0.0 (shown as -0.0 L/min), True (as 1.0 L/min) and Decimal, and refuses a str with math.isfinite's own TypeError rather than the simulator's wording; none is reachable from the sliders (found reviewing #1350)
- PL-LPH9 (S) ROADMAP.md's cadence says no interim release is cut partway through clearing a gate, but 159 of Gate 1's 175 frozen entries already shipped in v0.4.x patches, so the sentence a later session would cite to refuse a cut describes nothing this project has done since v0.4.5
- PL-LTKL (S) The chart hover keeps answering after the pointer leaves the plot: nothing clears the stored pointer position on a Leave event, so the box stays up and every later frame re-answers for a pointer that has gone
- PL-M4M0 (M) RunView._handle_reset wraps SimulationController.reset() in nothing, so the SimulationConfigurationError that equation_settings() raises at Reset when the tissue flows are stale (a CardiacOutput written onto patient.cardiac_output_l_min past set_cardiac_output, the type-only write guard PL-LBQY chose) escapes the slot after pause() and _state.reset(), leaving a half-reset run paused with no failure recorded, the readout showing a cardiac output the model never ran at and case_restarted never emitted; at step time the same stale record is presented as a SimulationNumericalError in L/s where every readout shows L/min (found reviewing PL-LBQY)
- PL-N67T (S) RunView.build_sidebar_panels constructs fresh panels on every call and reparents the run's live labels into them, so a second call silently strips the accounting and control-change panels out of the sidebar
- PL-NC62 (S) resumed_at's settings-mismatch refusal blames the control timeline whatever the cause, so a patient or agent mismatch would be misdiagnosed
- PL-Q7V1 (S) ROADMAP.md's varying-perfusion note ('Also unsupported at rest, one layer down', under planned milestone item 35) reads the stored fat flow as 'that far out' against Heinonen alone, where PL-HBH2 records that Yasuda 1991's washout fits put it at or a little above the stored figure
- PL-QJXS (S) No test compares an agent-switched run with a fresh run of the new agent, so a set_agent that keeps the previous agent's patient compartments passes the whole suite while a run labelled Desflurane computes with sevoflurane's blood:gas 0.65 and shows alveolar 2.95% (0.49 xMAC) at 5 min against 3.59% (0.60 xMAC)
- PL-QPN8 (S) src/anesthesia_sim/data/patients/reference_adult.json's Meybohm et al. 2021 note says its Tables 1-3 could not be read, but pmc.ncbi.nlm.nih.gov answered through the egress proxy on 2026-10-06, so read PMC7943506's tables and settle whether they list a blood or venous volume
- PL-QW19 (S) default_fresh_gas_flow_l_min is a required field no manufacturer publishes, so the first real machine profile must invent an unsourced number or cannot be written
- PL-QYBW (M) The chart's percent axis is scaled by the alveolar peak, so the slow compartments are compressed into 1-2 px and two runs' fat curves cannot be told apart by pointing
- PL-R0NL (L) Wash-in is compared with published human data at one instant, 30 minutes, so the first 15 minutes of the F_A/F_I rise, the phase the simulator most displays, are compared against nothing published and a doubled FRC that moves F_A/F_I at 1 min by -0.118 passes every gate
- PL-RBMK (S) _apply_to_every_run documents a two-phase write it does not implement: it applies in a loop and catches, so the docstring promises atomicity the code cannot give
- PL-SM5V (M) A run's settings cannot be recovered from RunSegment.settings: the L/min to L/s conversion does not round-trip for 7 of 101 cardiac outputs
- PL-SPN6 (S) Three compartments now raise the same 'partial_pressure_fraction must be between 0 and 1', so a refused step no longer says which one refused
- PL-SQJ1 (M) Playback delivers 73-91% of the rate the dropdown displays: 300x measured at 220x, 1x at 0.9x, so the clock on screen runs slower than its label
- PL-SWD1 (S) fraction_from_percent and percent_from_fraction take the other type silently - percent_from_fraction(Percent(0.5)) is a Percent of 50.0 and fraction_from_percent(Fraction(0.5)) a Fraction of 0.005 - because the arithmetic runs first and the constructor's swapped-type check sees a plain float; refuse a Percent where a Fraction is handed in and the reverse, as the constructors do, before converting (found reviewing PL-LLMN)
- PL-SWY5 (S) Esper et al. 2015 (Anesth Analg 120:45-50), the primary blood:gas measurement Meybohm et al. 2021's Table 1 footnote says Gas Man's coefficients differ from, is cited in none of the three agent files beside the adopted De Wolf blood:gas values (found closing PL-0SG0; read 2026-10-12 from PMC7943506's XML record, footnote and reference 54)
- PL-T4FK (S) docs/MODEL.md line 2350 wraps '+ brain + liver' to the margin, so CommonMark renders it as a bullet reading 'brain + liver is 3,820 of 6,480 ml/min - 59.0%', which gives the kidney + heart + brain + liver sum to two organs (the wrapped-marker shape PL-DSMK fixed in ROADMAP.md)
- PL-T995 (S) A run that stops itself inside RunView.step_tick - a bookmark halt, or arrival at the supported run length - is never redrawn: step_tick requests no frame and render_tick draws only while a run runs or a frame is owed, so the screen keeps saying Running with a live Pause, a clock one step behind, and no Branch here button, until the learner presses something
- PL-TBMX (S) circuit_volume_l means apparatus plus patient circuit, so a real machine profile storing a published apparatus figure would understate the circuit time constant by about 40%
- PL-TCR5 (S) The chart hover answers the pointer's previous position and never re-answers a resting pointer while paused, because the direct sigMouseMoved slot reads the position the rate-limited proxy stored one event earlier
- PL-VCP4 (S) SimulationController._record_control_change builds the settings record after the setter has written, so on a run whose tissue flows no longer sum to the cardiac output every setting but the cardiac output is half applied: the compartment holds the new value and the dial reads it, the definition's open segment and the timeline keep the old one, and the banner says the simulation is unchanged and still running its previous setting (found reviewing PL-M4M0)
- PL-TDBT (M) docs/pr-bodies holds 187 historical documents that read as current: 21 cited paths no longer exist, 30 cite an unresolvable sha, and 22 angle-bracket placeholders in 15 files vanish in GitHub's own blob view, with doc_check blind to all of it by design
- PL-V2HC (M) A halted run whose snapshot refuses cannot change agent: RunView._handle_agent_change and SimulationController.set_agent both read snapshot() while the selector is unlocked on a halted run, so the slot's raise is printed by Qt and the new-case dialog never opens; Reset is the one exit and the halt banner names it (found at PL-7DJK)
- PL-V67Q (M) Add y-axis range control to the agent graph: optional auto-scale, and a settable MAC / volume-percent scale
- PL-VJZK (M) A reader-set agent price makes a displayed economic value's provenance partly the reader's, so the stored price needs its currency and the date it was set, and the display must not read as an authoritative figure
- PL-W3Q5 (S) app/formatting.py types mac_percent as Percent in two signatures and as a bare float in five others, so one parameter carries two types in one module
- PL-WG73 (S) COMPARING_FORK_LOCK_TEXT tells a learner to Reset the case, which labels no control - and the Reset they are likeliest to press discards the branch and leaves the lock standing
- PL-WMCJ (S) docs/MODEL.md's Known limitations never names intertissue diffusion, the route Eger and Saidman 2005 describe for agent reaching fat, though every tissue group here exchanges only with arterial blood
- PL-WPDB (S) The frame-cost harness measures a one-run dashboard, but v0.5.0 draws two runs on one chart, so the frame cost the branching milestone will actually pay is unmeasured
- PL-XWFP (S) TissueGroup.advance and VenousBloodCompartment.advance report uptake as a return - a negative change, as low as -3.2e-18 L, while the driving fraction is above the compartment's - at admitted flows from 1e-30 to 3e-13 L/min, because d + (i - d) * exp(-dt/tau) rounds at the scale of the driving fraction; the circuit's closed form was rewritten for the same reason (found fixing PL-YT8N)
- PL-WZVZ (M) Make an inter-machine difference attributable: which parameter differs, and what it does to the result
- PL-X7D5 (L) A run's screen has two writers - RunView.refresh from a drawn frame and RunView.present_halt from a hand-picked subset of controller state - and nothing owes a frame when the run changes outside present, so each widget missing from the subset, and each path that stops or changes a run without a frame, leaves the screen stating an old run: the cause of PL-1YDD, PL-DTJQ, PL-MMNX, PL-T995, PL-G3K7 and PL-0LG6 (found at the 2026-10-17 triage pass)
- PL-Y04W (L) Build break-out: an Area taken into its own top-level window, the window lifetime that keeps the main window unclosable while break-outs exist, and the test that every window the application can be left showing carries the invariant display tier
- PL-Y4YX (S) PL-L9RD's verify: demands PySide6 in app/theme.py, which that file's own documented invariant forbids, and the invariant's stated reason does not hold either - both tools ast.parse it and neither imports it
- PL-YD2V (S) Supported run length and the validation section's caveat 4 bound the slow tail on metabolism and fat flow alone, but the fourth compartment this model lacks is the largest term in Yasuda 1991's measured washouts from about hour 2-3 to hour 21-29, inside the 24 h envelope, and neither passage says so
- PL-YT8N (S) BreathingCircuit.advance_fresh_gas reports a negative exhaust, as low as -3.3e-16 L, at admitted flows from 1e-15 to 1e-6 L/min, because 1 - exp(-dt/tau) loses its digits to cancellation when dt/tau is small; the exhaust it integrates cannot be negative (found fixing PL-B26Y)
- PL-Z0HN (M) A tissue group's perfusion fraction can be changed on a built patient, and nothing checks that the fractions still sum to 1, so every later cardiac output change is refused, and its restore moves the tissue flows under a banner that says nothing changed (found reviewing PL-VCP4)
- PL-Z0T3 (S) dataclasses.replace() on PatientCompartments rewrites the tissue and venous flows of the original it shares those sub-objects with, because __post_init__ calls _update_blood_flows on them: a running system is left perfusing at the twin's cardiac output while its snapshot reports the old one, until the next step's tissue-sum check halts the run (found reviewing #1350)
- PL-Z4K6 (S) Decide whether seven readout columns on a 1366 px laptop is wanted, now that dashboard_frame.readout_columns is font-measured and that screen misses the seven-column width by nine pixels
- PL-ZH1F (S) RunDefinition.record_change's dial-moved-back branch is tested only on two-segment runs, the one size where segments[:-1] and segments[:1] agree, so a mutant that silently deletes every later stretch (state_at 600 s alveolar 0.01246 against 0.01867) survives all 5734 simulator tests
- PL-LN69 (L) Instruction-set growth is measured but never tested for effect, so a rule can be added on an argument and can never be retired on evidence
- PL-087W (M) bin/docket verify unions removed assertions per commit and never nets them against a later restore, so a line a session puts back on the check's own advice keeps refusing the branch
- PL-2DTK (M) docket verify --self cancels an added line against its removal only within the commits it selects per id, so an item is charged with removing an assertion a commit that does not name it had added on the same branch
- PL-3LLZ (M) Four fakes in test_vcs.py each answer the same commit-paths question, and each new git read has to be taught to all of them
- PL-4V6B (M) Decide whether the decision archive should be separated from the work queue
- PL-4W2L (M) design round: pick the altitude for verify's assertion check before the next of its three open items is worked, since six fixes have each uncovered the next and PL-G21K's ratified decision reached only the suppression check beside it
- PL-6YYR (M) A release tag can be pushed for a version that was never cut, and nothing detects it: v0.4.8 tags main at version 0.4.7 with no release notes and no ROADMAP row
- PL-73P0 (M) default_base falls back to the literal string main when no candidate ref resolves, so every comparison in vcs.py can be taken against a guessed base with nothing in the answer saying so
- PL-7RTN (M) An open pull request can carry no check runs at all, so a branch merges with nothing having gated it
- PL-7TVT (M) bin/docket flight separates a live session from an abandoned branch only by commit age, which cannot fire in the first hour: PR #757 sat green and unclaimed 25 minutes after its session was archived, with its three items still reading 'do not start these again'
- PL-99YZ (M) Three sessions opened three pull requests for the same red-main fix within four minutes, each having correctly filed its own item first, because every in-flight guard matches an existing PL- id and none of them can see an item that did not exist when the other sessions looked
- PL-9LXK (M) Nothing checks a prose claim about the tier or adoption of a stored value's source, though PL-1JDD made both machine-readable and three such claims went stale within a day
- PL-B78T (M) bin/docket stranded reads only docs/items, so unmerged work anywhere else is invisible to it: four recovered PR bodies on claude/festive-allen-nj1x98 and 206 lines of docket source on claude/recurrence-signal-feature-3hnynt sit on branches with no open pull request and nothing reports either
- PL-BGMK (M) Two open items whose touches and verify: command overlap are never compared, so PL-1YDK and PL-8PT6 were filed and worked as one finding twice and only docket check --verify on main caught it
- PL-BYMX (M) bin/docket stranded compares branches by item id, so a branch carrying a non-item file the default branch lacks is reported by nothing
- PL-CNJH (M) verify's replacement pairing folds an assertion whose inserted argument loosens it - approx(2.05) to approx(2.05, rel=0.5) - reporting the pair without refusing it; 4 of the 56 it folds across 905 commits change what the line asserts
- PL-CWD4 (M) A verify: command that can never pass on any tree is indistinguishable from one whose work is simply not done, so PL-4PC5 carried a dead command for five days after wave stopped printing the line it grepped
- PL-CZR6 (M) bin/docket stranded reported no branch carrying work its own pull request left behind while claude/sharp-lamport-t545rs carried two PL-X5PK commits pushed an hour after #823 squash-merged from it
- PL-DG84 (M) docs/WORKING_NOTES.md asks for resolved threads to be deleted and nothing reads that policy
- PL-GJPD (M) _carried_work reads a combined commit as having carried the work, so the triage pass that closed PL-3CBS is recorded as its pull request because it also edited ROADMAP.md - three of main's 698 answerable closures disagree with their stored pr
- PL-MFM4 (M) bin/docket release's collision guard reads unmerged refs for a cut in progress, so it cannot see a second session that has filed a release item and asked the owner for the version without cutting anything: PL-Z0C7 and PL-R5VS were two ids for one release and every guard matched both cleanly
- PL-N2PP (M) A rider item worked inside another item's session is invisible to every in-flight guard the project has
- PL-NJ9M (M) bin/docket delegable cannot tell a brief that determines the fix from one that leaves the choice open, so a hand-off meant to need no reading still does
- PL-NPWP (M) bin/docket stranded's ahead list keys on textual difference between the base's copy and a branch's, so a branch holding a stale copy is reported forever and no amount of recovery can empty the list - which is the completion test PL-DZM1 was written against
- PL-Q8RQ (M) Four open items' verify commands rest on a bare 'pytest -k SUBSTRING', which any unrelated test name can satisfy: PL-S5YM turned main red exactly this way, and whether a command can discriminate at all is decidable enough for docket check to refuse it
- PL-RR1N (M) A verify: grep for a prose phrase can never match once the document's own line-wrapping splits it, and exit 1 reads as work-not-done
- PL-S0MB (M) Catch-all feature names can never report completion: dev-tooling carries 174 items and queue-hygiene 29, so bin/docket feature <name> cannot answer 'yes, that is dealt with' for either, and 32 of 33 workflow features read as live
- PL-SY1J (M) bin/docket show named only one of two branches carrying PL-D1RT, and it was the later one, so the session holding the item read a verdict telling it to stand down
- PL-SYG4 (M) The digest's RESERVED verdict suppresses the release offer entirely rather than naming the next free patch number, so on the v0.4.x track with v0.5.0 reserved a session never offers a cut the plan actually wants
- PL-SZJ2 (M) wave reports nothing for a released milestone row whose own frozen list still has open entries, which is PL-LN3T's case in the other subsection: a gate-only milestone released with its list open drops out of the report entirely
- PL-TKFD (M) A session that discovers mid-work that its work falsifies an assertion cannot declare falsifies: on the base, so verify --self has no clean route for the case the field was built for
- PL-WNQT (M) bin/docket stranded reports a one-path commit as work left behind whenever a later merge edits that file, and its recovery recipe would revert the newer work
- PL-X3NY (M) bin/docket stranded reports in-flight pull-request work and abandoned-branch work identically because it reasons from refs alone, where the GitHub API can classify the two - so the reader re-derives every session what one API read would settle
- PL-Y1LD (M) docket concurrent orders a batch by file, but the lane mechanism separates only two sessions, so the third and fourth simultaneous session have no command that picks for them
- PL-Y5ZB (M) agent_identity_check's rule 2 reads only construction (self.X = <agent colour>), so a method other than _apply_agent_color_scheme writing self.X.color = AGENT_COLOR_SCHEMES[...] is a second writer of agent colour that neither rule sees
- PL-YVV4 (M) Run the suppression count expert-review.md requires before any triage-bar change
- PL-ZPDM (M) vcs.tags and vcs.changed_items answer with a bare frozenset, so a git that does not answer is indistinguishable from a repository with no tags and a branch that changed nothing
- PL-0HPV (S) make check omits the verify replay on a cost measured before --verify-base narrowed it, so a PR-only failure class is only ever found from CI
- PL-12P8 (S) PL-JBZK's lane check assumes every file under tests/ is a test file, so a shared non-test helper is told to declare itself apparatus
- PL-162Y (S) docket next names a blocked item whose item blockers have all closed, but not one whose blocked-by milestone is now scoped, which docket check reports as equally promotable
- PL-1BS2 (S) The session-start digest's Releasable line reads readiness without the interrupted-cut resume, so during an unfinished cut it reports the short remainder with nothing saying why
- PL-1T6T (S) Re-test the refusal of compaction now that root CLAUDE.md is known to reload after a compact
- PL-1X2C (S) bin/docket show names the reader's own branch as a carrier and stays silent about the other branch editing the same item
- PL-245B (S) docs/WORKING_NOTES.md cites test_vcs.py:467 as the test asserting _superseded's inverted direction, but that line has never held such a test - PL-Q9Z1's live thread rests on it
- PL-28HG (S) GitRunner._drop marks a root permanently unbatchable, so one transient cat-file fault costs every later blob in the command a separate git show process
- PL-3BYK (S) docket digest --profile's ref set block counts item-file edits per ref and sums across refs, while the walk holds one entry per identifier, so anyone predicting a diff count from it over-predicts by about 2x on a clone with overlapping long-lived branches
- PL-3DN1 (S) bin/docket release accepts a VERSION below the current one, so a typo silently downgrades pyproject.toml's version field
- PL-3QM9 (S) bin/docket flight reports a branch's age by calendar-date subtraction, so a branch committed 55 minutes ago reads 'last commit 1 day ago' across midnight and a running session looks abandoned
- PL-44DG (S) measure_resident undercounts the true per-session resident payload by 4,794 characters: the SessionStart digest and the docket skill description are resent every turn and counted by nothing
- PL-4HKS (S) docs/WORKING_NOTES.md's playback-speed open thread reasons from pre-Qt-port numbers - a 0.011 ms step and 15 ms of chart-point construction - and names PL-010 as unspent headroom, but PL-009 is dropped, PL-010 is done, and the step now costs 0.025 ms
- PL-4ZK8 (S) bin/docket concurrent offers a batch containing needs-decision and in-flight items, so a fan-out cannot hand it out as-is
- PL-5B88 (S) verify's suppression check misses @pytest.mark.skip and @pytest.mark.skipif, the two commonest ways a pytest test is disabled: @skip needs its @ against the name and pytest.skip needs its halves adjacent, so the check reports none while a disabled test sits in the diff
- PL-5DPF (S) A generator marked spent that accrues a new recurrence has had its verdict falsified, and nothing says so
- PL-6G8T (S) _section_text reads a required heading quoted at a line break as the section itself, so a wrapped quotation above an empty real heading masks the empty one
- PL-6QZP (S) CLAUDE.md's fix-now test 2 says a wider fix fails the touches audit, but under verify --self that check reports and the branch still ACCEPTs, so the deterrent the rule describes does not fire on a session's own branch
- PL-7NKD (S) bin/docket verify caps the removed-assertion evidence at five lines with nothing saying so, so a count of six prints five and the reader cannot tell which line is missing
- PL-9KSY (S) store.write_item's replace= parameter has no caller left now that every field write uses rewrite_item, and PL-YTDN's rename pass is specified as git mv, so the rename branch is dead code that the next field writer could still reach for
- PL-B11M (S) Detect a silent model fallback: last_served_model can differ from the configured model with nothing recording it
- PL-BX1C (S) bin/docket verify runs a dropped item's stale verify: command and REJECTs the close-out on it, though the skill says a dropped item has no command to run
- PL-CR36 (S) tools/ignore_check.py type-checks tests and subprojects/docket/tests in one mypy invocation, so a second file named conftest in those trees is a duplicate-module error that stops mypy before it evaluates anything and turns make check red
- PL-CY8B (S) test_flight_does_not_answer_from_a_walk_the_clone_truncated asserts PL-M01 is absent, but PL-M01 is not an id ID_PATTERN matches, so that assertion cannot fail
- PL-D1NT (S) doc_check's path-citation resolver crashes the whole run on a path it cannot stat: the glob branch is guarded against exactly this and the .exists() branch is not
- PL-DK8Y (S) The session-start digest prints 'The plan's numbering is behind the project' for every Wave.stale statement, which is false for the section-that-no-timeline-row-bears one
- PL-DMNX (S) PL-1DN9's premise that nothing repository-side runs when a pull request is created is now false, so the published-body read-back it bought 337 resident characters for may be scriptable
- PL-FT3M (S) cli._cuts's docstring says the unlanded-ref walk is gated on the release offer, where it is gated on Readiness.is_worth_cutting - and the two now diverge routinely
- PL-G8TR (S) no-prune-guard is evaded by the form it recommends - git branch -dr driven from a generated list is a prune
- PL-H6VQ (S) doc_check's _declined_ids counts every PL- id in a Declined-to-Gate subsection, including ids the deferral's prose only cites, so an item mentioned in another item's reasoning reads as disposed and check_gate_dispositions goes silent on it
- PL-H9GV (S) PL-01GD shipped as one exported Makefile variable with no test: PYTHONDONTWRITEBYTECODE appears only at Makefile:21, its declared touches names tests/unit/test_tools_portability.py which never changed, and its verify: passes against an untouched suite
- PL-HVLJ (S) doc_check reads local tags, so a checkout whose tags were fetched ahead of its working tree errors on a clean main - observed 2026-09-21 as 'git holds v0.4.35, but no row of the version table marks v0.4.35 completed' when the row and the tag are the same commit
- PL-HX5C (S) Both in-flight guards passed and two sessions still implemented PL-W8XP independently: the second never renamed and its branch was named after a different item, so neither the ref read nor the session read could see it
- PL-J3TV (S) .claude/hooks/no-prune-guard.sh still prints the pre-PL-K2C8 three-command restart recipe, so the incomplete version survives in the louder of the two places - the message a session reads at the moment it is refused a prune
- PL-J3WK (S) make check runs bin/docket check without --verify while CI runs it with, so a verify: command that proves nothing - a literal true, or one shared by three items - passes every local gate and fails CI; both halves of that are decidable statically, without running the 17 commands the flag runs
- PL-JTHW (S) tools/main_ci_status.py passes over a cancelled main run in silence, so after PL-SMN4 a commit with no whole-store verdict is indistinguishable from one nobody asked about
- PL-JW39 (S) docket next ranks a needs-decision item first, so every fresh session opens on work whose next step is the owner's answer
- PL-JW9J (S) core_vocabulary_check matches whole identifiers because two live names would have failed a substring rule, and since PL-6KNM neither exists: decide whether to tighten
- PL-KFWL (S) The v0.4.8 tag is pushed onto a commit where the release was never cut, so doc_check errors on main for every session
- PL-KNHX (S) contrast_check's KNOWN_SHORTFALLS entries are never checked against the requirements they excuse, so a stale one lingers and inflates the reported shortfall count
- PL-KRS6 (S) bin/docket release counts the previous release's own cut item as releasable work, so every session after a release is offered an empty one
- PL-LBW5 (S) Five open items' verify: commands grep a file their own touches does not declare, so bin/docket concurrent gives a wrong answer for work that will certainly edit it
- PL-LF2C (S) PL-VV4D's exact left-behind check rests on refs/pull/<n>/head being permanent, and GitHub is about to unreference 90 of them, so the check needs a third decline condition and one of its two test vectors dies
- PL-LKGW (S) bin/docket meets a python3 below docket's 3.11 floor with render.py's ImportError traceback rather than naming the floor and the interpreter it found, so a Mac whose python3 is Apple's 3.9 gets a cryptic failure by hand and silent hooks with nothing saying why
- PL-LPWK (S) A release note cites the pull request that closed an item, not the one that carried its code, whenever the two differ
- PL-LT77 (S) git fetch --tags does not prune, so a tag deleted on origin keeps failing doc_check in every checkout that already fetched it, and nothing distinguishes stale local state from a real repository fault
- PL-M6FY (S) cli.cmd_flight builds its own GitRunner instead of the invocation's, so flight loses the cat-file memo every other command shares
- PL-MSFB (S) PL-6194's verify: command still uses [(] and [)] to work around the math check that PL-WTQ1 fixed, and WORKING_NOTES.md:504 still uses backticks to work around PL-KJ63
- PL-N0MH (S) Only docket check names the settings it ran under, so next, digest, status and list under --items are read under the wrong policy in silence
- PL-NDKC (S) PySide6 6.11.2 segfaults on QDataStream over a temporary QByteArray, which the layout persistence work will meet the first time it decodes a saved blob
- PL-NGBM (S) --no-git does not stop the git reads behind a printed count, so docket digest --no-git shells out to git despite the flag saying branch detection is off
- PL-NWSK (S) required_checks_check.py treats a paths-filtered pull_request job as reporting, but GitHub leaves such a check pending forever on a pull request the filter excludes, so the reconciliation would read agreement while merges hang
- PL-P4XB (S) test_verify.py's _commission helper commits unconditionally, so calling it with fields identical to the base store's copy dies inside subprocess with CalledProcessError rather than saying nothing changed
- PL-PFK1 (S) bin/docket verify REJECTs a self-audited branch on commission checks alone without ever naming --self, so a session reaching the command from CLAUDE.md or --help still hits the wall PL-7XTS closed for the skill
- PL-PNW6 (S) A release cut at a version number some withdrawn tag once named leaves every warm checkout pointing v<version> at the old commit, and the handover's own 'git fetch origin main' is the command that leaves it stale silently
- PL-QNYF (S) docket check errors on an item whose closure landed in a queue-only commit, and the error names no remedy the session can reach
- PL-QSGX (S) bin/docket flight never fetches, unlike stranded and branch, so it reports refs as old as the clone - the one command whose whole job is reading other sessions' branches
- PL-QV5Y (S) Makefile's CI-timing comments quote a 1230-test suite at 78 s serial and 27 s parallel, measured 2026-09-03; the suite is now 2096 tests at about 43 s parallel, so a reader sizing a CI-cost decision from them is reading stale figures
- PL-RWBV (S) Seven open items declare touches paths that do not exist, three of them naming core/run_score.py which PL-ZX12 renamed to run_definition.py
- PL-T441 (S) The git reads behind a printed count resolve the store from config.items_dir rather than the tracked directory, so docket check --items pointed at a store elsewhere silently finds no closures
- PL-T8PT (S) make check runs pr_title_check --discover against committed history, so a session that runs it before committing the closure sees a HEAD without it, passes locally, and goes red in CI anyway
- PL-TP5M (S) PL-ZBRB's advisory names blocked-by to work around a checker that did not read it, and PL-KBD0's check now does
- PL-VJFQ (S) Nothing enforces that KNOWN_SHORTFALLS only shrinks, so the contrast ledger could become the suppression list ui-color.md forbids in prose
- PL-VJPJ (S) bin/docket next raises BrokenPipeError and prints a traceback when its output is piped into a command that closes early, so next | head looks like a crash to every session that pipes it
- PL-VV6N (S) Decide a retention rule for items captured but never worked
- PL-VYK1 (S) The docket skill's release handover tags at origin/main rather than at the cut's own merge commit, so a re-run of the three commands tags whatever merged next
- PL-WFFX (S) Name the merge client that sends an empty commit_message, which only the project owner can do: affected merges cluster by sitting at 98.3% and by owner-local hour at p=5e-5, but GitHub records no client identity
- PL-WG7Q (S) _merges_naming's subject scan applies only the closed-here test and never the carried-work one, so a closure split from its work is recorded whenever its own subject leads with the id
- PL-WHQS (S) Centralize the closed-item filter now duplicated across twelve call sites
- PL-WTXB (S) Remove the unreferenced docket milestone command
- PL-WVJ0 (S) The docket skill says bin/docket show prints no placement at all, but PL-J790 added the plan: line to show in v0.4.18, so a session is sent to look up what the command already prints
- PL-XQGH (S) verify's assertion check anchors on with, so the parenthesized multi-manager form leaves pytest.raises on a line of its own that matches nothing
- PL-YKXQ (S) This container's initial clone had local main diverged 407 commits into pre-rewrite history, so a session that checks out main gets a stale tree and an old bin/docket
- PL-YS9F (S) outstanding_roadmap_edits states both edits for a milestone number a cut has exactly reached because it cannot read the beat that decides which; the plan computed before the bump knows
- PL-YSMV (S) doc_check reads any quoted string near the word section as a section citation, so prose quoting a command's own output fails make check
- PL-Z6M3 (S) bin/docket stranded prints 'No item exists only on a branch' while an item sits on two branches and not on main, because the predicate is 'neither the store nor the default branch' and the rendered sentence drops the store half
- PL-Z85N (S) bin/docket release cuts whatever version it is handed, so the reserved-version answer exists only in the advisory digest and nothing objects on the cut path
- PL-Z9K5 (S) bin/docket record normalizes an item's whole front matter as well as inserting pr:, so PL-ZYQC's 'pr, not counted' exemption misses and the close-out audit reports files the skill told the session to touch
- PL-ZM48 (S) docs/worker.md records remote-branch deletion as exit status 0, and PL-3V6C as two incompatible causes, but one 2026-09-20 transcript carries the 403 and the Everything up-to-date line together at exit 1
- PL-1RTM (M) doc_check resolves path citations only in DOC_GLOBS, so the queue - most of this project's prose - has its citations unchecked
- PL-316G (M) Convert the 150 possessive-form document citations to the section-mark form, which is the only way doc_check can check them without reading prose as a citation
- PL-4L49 (M) tools/contrast_check.py measures only declared pairs, so a control that declares no colour reads as covered when nothing measures it
- PL-4RL2 (S) The Gas Man simulation study at PMC7943506 is cited as Meybohm P, et al., J Clin Monit Comput 2021;35:897-908 in the reference adult, the three agent files, the circuit file, docs/MODEL.md and tests/unit/test_parameters.py, but PubMed gives it as Weber J, Schmidt J, Wirth S, Schumann S, Philip JH, Eberhart LHJ, J Clin Monit Comput 2021;35(2):343-354 (PMID 32067148), so a reader following the citation cannot find the paper by its authors or pages (found working PL-SWY5)
- PL-5B1N (M) Simulated traces should be solid and a dotted trace should mean an uncommitted predicted future, but dash pattern is already spent as the six traces' colour-blind-safe channel
- PL-65HT (M) A core/ dataclass numeric field default other than 0 or 1 that appears in no provenance-table value is an unsourced scientific constant, and nothing checks for one
- PL-B396 (M) Agent amounts are displayed in litres of vapour, which is not the unit a reader buys, fills or wastes agent in - report a liquid-equivalent millilitre figure
- PL-KKRP (M) Re-examine the debt gate's freeze trigger: scoping a milestone has not frozen its gate for the last two milestones scoped, so the cadence's beat 1 no longer describes what the project does
- PL-0MLZ (S) uv run pytest writes bytecode that survives a source restore, so a mutation test can silently keep running the mutated build
- PL-73G8 (S) The recovery file header claims the body verbatim, but it is the body as GitHub serves it today rather than at merge time, and its commit: sha silently dangles after a history rewrite with nothing checking it
- PL-7K2C (S) quality.yml runs six to eleven tool checks after the whole-store verify replay, so a replay failure skips contrast, import-boundary, core-vocabulary and glyph checks on that main commit entirely - moving the replay to the end of the job would cost nothing and close the gap
- PL-HKTB (S) The chart gridline and divider grey measures 1.31:1 on the panel and carries no contrast requirement; decide whether it should be darkened or recorded as exempt furniture
- PL-VZYS (S) A hand-run 'uv run ruff check .' still reads the stale .ruff_cache that PL-QSJM's --no-cache removes from make check and make fix, so the guard sits at the entry point rather than where the tool reads it - the same shape as PL-0MLZ's finding about PYTHONDONTWRITEBYTECODE

### Captures after the cut

An open debt item that was captured after the cut (`e6cdfd93`, 07:04 on
2026-09-21) is deferred to the next gate, with two exceptions. The item is not
deferred if it is classed `safety` or `science`, or if an entry on the list
waits on it. An item captured after the cut was not in the store that the snapshot was
taken from. § "The gate is a snapshot, not a moving target" therefore applies the
presence test to it, and that test returns no. `PL-GW0P` replaced that reading
on 2026-11-07: the test asks whether the problem was present, and a capture
whose problem was present at the freeze joins the current gate's list. A capture that an entry waits
on is not deferred because of its date. Either it is let in beside the entry,
or the entry is deferred with it. These are two of the three places that
section gives for a prerequisite (`PL-D388`). Each deferred item records the
deferral as `deferred-from: v0.6.0 - <why>`. The triage pass that classes the
item writes that field. A frozen entry
that this gate defers carries the same field.

The `safety` or `science` items captured after the cut are placed on the list
above with the rest. Each entry below that opens with its id and class, rather
than with a bold lead, was placed on the list by the triage pass that classed
it, unless its paragraph says how else it joined. `bin/docket gate` prints each
one's lane. This section names each one with the date it re-entered.

`PL-WMCJ` (`science`, 2026-09-24) is the missing intertissue-diffusion
limitation in `docs/MODEL.md`. `PL-CBDX` (`safety`, 2026-09-25) is the review
of simulator diffs that were merged without being read since 2026-09-23. It was
split from `PL-SQTR` on the owner's answer, and like `PL-WMCJ` it is on the
list.

**`PL-TBMX` joined this list on 2026-09-27, after the freeze, under the
exception that admits a `safety` finding whenever it is made.** It was filed on
2026-09-20 and dropped the same day. The drop rested on a misreading of the
reference profile's phrase "the apparatus alone". There the phrase meant
without the lung, not without the patient circuit, and `PL-TBMX` reworded the
phrase to say so. `PL-TBMX`'s brief quotes the history from v0.5.0's
§ "Declined to Gate 2 on the refilling-queue ground". The project owner reopened it as a `P1` when `PL-HGB6` was re-scoped
(project owner, 2026-09-27, ratified, over building `PL-HGB6` as written). It
is `ready` rather than `blocked` behind `PL-2FZ9`, so the `anticipated`
carve-out does not apply to it. Its own brief places it before the point at
which a second profile can be loaded, because that gap is its whole exposure.

`PL-HBH2`, `PL-KK1Q` and `PL-YD2V` (`science`, 2026-09-27) are what `PL-WMCJ`
found about the late washout when it read the two Yasuda 1991 papers. The
fat-perfusion note was weighed against only one source. The 24-hour tail was
never compared with the published fits. The supported run length says nothing
about the missing fourth compartment.

`PL-921Y` (`science`, 2026-10-03) is what `PL-95NW`'s measurement found beside
its own result. The subsection compares an isolated muscle time constant with a
fitted apparent one.

**`PL-5291` joined this list on 2026-10-03, after the freeze, under the
exception that admits a `safety` finding whenever it is made.** The first
review of `#1292` filed it that day. It describes a run that has reached the
24-hour supported run length but looks like an ordinary paused run and offers
Start, until a refused step stops it. Three cases show it: a branch forked on
86 400.0 s, that branch after a reset, and a trunk halted on a mark at
24:00:00. Its triage classed it `defect` and `safety`. The triage rested on the
precedent of `PL-N3N5` and on `docs/INTERFACE.md` § "Supported run length", which
forbids presenting that stop as a pause. It would also re-enter by presence.
That conclusion comes from reading the code at the `v0.5.0` tag, not from a
measurement. That release was cut on the day this list froze. It already
shipped the 24-hour stop, branches and step-exact bookmark halts. Its
`_open_at` already opened a branch without setting the limit's reason.

`PL-YVV4` (`planning`, filed 2026-09-13) was let in on 2026-10-03. It is on the
list with `PL-VV6N`, which waits on it. `PL-YVV4` was in the store at the cut,
but the class filter left it off the list. Per § "The gate is a snapshot, not a
moving target", what an entry needs is let in and worked together with the
entry it completes. So the two items are one piece of work (`PL-D388`, project
owner, 2026-10-03, ratified, over admitting every open prerequisite of an entry
automatically and over deferring the pair to Gate 3).

`PL-LTKL` (`safety`, 2026-10-04) is a chart hover that keeps showing a value
for a pointer that has left the plot. The value is a modelled concentration
that keeps climbing with the run, as if it were a live reading. `PL-T4FK`
(`science`, 2026-10-04) is `docs/MODEL.md` showing the four-organ share of
cardiac output as a bullet about brain and liver.

**`PL-HSFV` joined this list on 2026-10-04, after the freeze, under the
exception that admits a `safety` finding whenever it is made.** `PL-V10T`'s
session filed it that day. It describes a run definition opened under an
`UptakeEquationSettings` whose flows are outside the supported ranges, or
changed to one. Examples are a cardiac output of 1000 L/min, a fresh gas flow
of 500 L/min and an alveolar ventilation of 200 L/min. Such a run simulated
instead of being refused. That happened because the range guards ran only in
the compartments, and a run built from a settings record calls none of them.
Its triage classed it `defect` and `safety`, following the precedent of
`PL-0MLQ`, which reached the same three flows through a setter. It would also
re-enter by presence, read from the code at the `v0.5.0` tag. That release's
settings record checked the three flows only for sign and finiteness. Its
`RunDefinition` already opened a settings record and recorded changes from one.

**The `parse-dont-validate` feature joined this list on 2026-10-04, after the
freeze, at the project owner's direction** (project owner, 2026-10-04: "Add
'parse don't validate' feature to current gate in v0.6.0 for it to be
implemented by 'Ship v0.6.0' project"). The feature gives each quantity that
has a check of its own a type that only the check can build. Then no way in
that nobody guarded can take an unchecked value. Such an unguarded way in is
how `PL-HSFV` came about. Five entries joined with the feature, beside
`PL-HSFV`, which was already here:

- `PL-51B7`'s three slices, which the owner decided the same day to build in
  order: `PL-0YYV`, the three flows as checked types, which closes `PL-HSFV`;
  `PL-CN5S`, the case instant and the step count; and `PL-51B7` itself, the
  supported-range edge test finding every guarded quantity by its type.
- Two decisions: `PL-4R3W`, whether a concentration's fraction and percent
  become checked types too, and `PL-BBMG`, a dial above the vaporizer maximum
  reaching a run through the record `PL-HSFV` went through.

`PL-BBMG` is classed `safety`, so it would have joined under the exception on
its own. `PL-4R3W`'s `NewType`s and its hand check on a fraction's range were
both in the code at the `v0.5.0` tag. But the feature joined whole on the
owner's word, so none of the five depends on either of those grounds. All five
are on the list. `bin/docket gate` prints each one's lane, and
`bin/docket feature parse-dont-validate` reports their progress.

`PL-LBQY`, `PL-LLMN` and `PL-Z0T3` (`safety`, 2026-10-04) are what the review
of `#1350` found in the flows' checked types and in the compartments that hold
them. A bare `float` can be written onto a flow field, and a Reset can leave
that value in place on a paused run with no notice. That finding was raised as
a decision, which was answered the same day in favour of a write guard. The
flows accept minus zero, a `bool` and a `Decimal`. `dataclasses.replace`
rewrites the original patient's tissue flows.

`PL-7N8P` and `PL-8W1W` (`safety`, 2026-10-04) are what the review of `#1354`
found: the same kinds of defect in the case instant and in the run's own state.
An instant accepts a `bool`, a `Decimal` and an `int` beyond the float range,
and that finding was worked together with `PL-LLMN`. A step count or step can
be written onto a built `SimulationState` with no check, and that finding was
given `PL-LBQY`'s write guard. `PL-B26Y` (`safety`, 2026-10-04) is the
circuit's closed form reporting a `nan` exhaust at an admitted fresh-gas flow
below about 2e-306 L/min.

`PL-3800`, `PL-979Z` and `PL-SWD1` (`safety`, 2026-10-05) are the same kinds of
defect in places beyond the checked types already on this list. The positive
and non-negative guards accept a `bool` and a `Decimal`, so `True` builds a 1 L
circuit. One checked quantity can be built silently from another, such as an
instant of 600 s from a `StepCount`. The fraction and percent conversions
accept the other form, so a `Percent` of 0.5 is read as 50.0. `PL-YT8N`
(`safety`, 2026-10-05) is the circuit's closed form reporting a negative
exhaust at admitted flows from 1e-15 to 1e-6 L/min. `PL-7DJK` and `PL-M4M0`
(`safety`, 2026-10-05) are halts that are shown wrongly. In one, a displayed
fraction is refused, and the screen still reads Running with no banner. In the
other, a Reset over a stale cardiac output escapes its slot. It leaves a
half-reset run and records no failure.

`PL-544D` (`safety`, 2026-10-11) is the alveolar and tissue amount accepting a
direct write beyond capacity. `PL-V2HC` (`safety`, 2026-10-11) is a halted run
whose agent selector raises an exception inside its slot when the snapshot
refuses. `PL-0FJ8` (`safety`, 2026-10-11) is `AgentParameters` accepting a zero
MAC. `format_mac_reference` then prints `1 MAC sevoflurane = 0.0%`. `PL-1DP1`
(`safety`, 2026-10-11) is the two concentration conversions accepting a bare
float as either form. `PL-QPN8` (`science`, 2026-10-11) is the reference
adult's note that cites Weber et al. 2021. That paper's tables can now be read
at the source.

**`PL-HQF5` joined this list on 2026-10-17, after the freeze, under the
exception that admits a `safety` finding whenever it is made.** It was filed on
2026-10-12 in `PL-KFNP`'s design round. It describes how a tissue group's or
the venous pool's blood flow can still be set apart from the patient's cardiac
output. A triage pass on 2026-10-17 deferred it as neither `safety` nor
`science`. `PL-KFNP`'s build then measured a case that the pass had not seen.
Flows moved between tissues with their sum unchanged pass the settings record.
The readouts then step at the moved flows. The chart is computed from the
recorded flows, so the two disagree on screen. The project owner classed it
`safety` the same day (project owner, 2026-10-17, ratified, "Agree", over
leaving it a `P2` defect deferred from this gate).

**`PL-Z0HN` joined this list on 2026-10-17, after the freeze, under the
exception that admits a `safety` finding whenever it is made.** The state
review of `#1488` filed it the same day. A tissue group's perfusion fraction
can be written on a built patient, and nothing checks that the fractions still
sum to 1. The next cardiac output change is then refused. Its restore moves
every tissue flow, under a banner saying that the simulation is unchanged. The
triage pass of 2026-10-17 classed it `safety`, because the screen states a run
that the model is not running.

`PL-QJXS`, `PL-JPS2`, `PL-ZH1F` and `PL-H1JH` (`safety`, 2026-10-17) are the
safety findings of the test-effectiveness audit. No test compares an
agent-switched run with a fresh run of the new agent. Both MAC-awake band tests
take their expected band from the snapshot under test. The dial-moved-back
branch of `RunDefinition.record_change` is tested only on two-segment runs. The
MAC-awake fractions and spreads have no pin from their primary source.
`PL-9YHR` and `PL-R0NL` (`science`, 2026-10-17) are the audit's validation
findings. The published-data gates cannot resolve most stored parameters.
Wash-in is compared with published human data at 30 minutes only.

`PL-CM1B` (`science`, 2026-10-18) is what `PL-R0NL`'s comparison of the early
wash-in curve found. Desflurane rises faster than in its 1991 cohort from 1 to
10 minutes. `PL-4RL2` (`science`, 2026-10-18) is what `PL-SWY5` found when it
read the Gas Man study at PMC7943506. The tree cited that study under the wrong
authors and pages.

**`PL-F2YS` joined this list after the freeze, on 2026-10-18, as a `safety`
entry**. `PL-F2YS` is the layout half of the work that Required scope entry 20
handed to `PL-W54S`. That half covers the region's width at 1366 px, and
compare mode against the chart's 360 px minimum. It was split out when
`PL-W54S` was re-confirmed as the per-window declaration of the unconditional
set. Entry 20 names it, so v0.6.0 itself clears it.

**`PL-JG82` joined this list the same day, also as a `safety` entry.** It is
the compare-mode half, which `PL-F2YS`'s build measured and could not settle.
Entry 20's budget names it, so v0.6.0 itself clears it. `PL-QLZ5` followed from
the owner's answer on the same day. Entry 20 names it too.

**`PL-NNML` joined this list on 2026-10-20, after the freeze, as a `safety`
entry.** Before the milestone was cut, a check of its Definition of done found
that the dashboard page still scrolled. So at laptop window heights the use
disclaimer was below the fold, and scrolling down to it moved the unconditional
region off the top. v0.6.0 itself clears it, because `docs/MODEL.md` had
recorded the gap as closing in this milestone.

The first 43 were recorded here in prose subsections, one for each triage pass.
Those passes ran from `PL-2JRC`'s pass to the pass on the generator heads that
`PL-T7Y1`'s audit and `PL-TH9K`'s session filed. On 2026-09-23 the records
moved onto their items, and the subsections were removed. This file's history
before that change holds their text.

### Required scope

#### The layout model and its Qt adapter

1. **The layout model** (queue items `PL-1FT6`, `PL-HJPY`, `PL-G60V` and
   `PL-5HSG`). The model is pure Python and imports no Qt. It is a tree of
   splits and Areas with the operations `split`, `join`, `resize`, `swap` and
   `set_view`. It has a `borders()` query that returns the handles collinear
   with a given handle and adjacent to it. It serializes to versioned JSON.
   From version 1, the serialized root holds a *set of windows*. `PL-HJPY`
   settles what owns the set, how an Area is addressed across windows, and
   where the border-chain query stops. It is settled now because adding a
   window set to the root later would be a schema migration. That migration
   would run against files into which a learner has already saved their own
   Workspaces.

   *Where the tree cannot express a join, the join is refused rather than
   approximated.* `PL-3J2P` chose the nested-splitter tree knowing that it is
   strictly less expressive than Blender's shared-vertex graph. It accepted
   the limit on the ground that the limit "shows up as a join being unavailable
   rather than as a wrong value". The model has to be built to have that
   property. It does not get it for free.

   *What a reader is offered depends on the rectangles they see, never on how
   the tree was built.* `PL-G60V` and `PL-5HSG` are two corrections that the
   model's own close-out review found (`#1448`). Each was decided (project
   owner, 2026-10-12, ratified, over keeping the `join` and the proportional
   drag that `#1448` shipped). First, where four Areas meet, whether a join is
   available no longer depends on which split came first. Second, a drag moves
   only the borders on its line, as Blender's drag does. As the decision says,
   `PL-5HSG` lands before the adapter (`PL-W9P6`) makes the handles live.
   `PL-G60V` lands before the join that a reader uses (`PL-2KXB`). So a reader
   never meets either behaviour in the form being replaced (`PL-F6H6`).

2. **The adapter** (queue item `PL-W9P6`). The adapter is one module, and it
   is the only module that imports `QSplitter`. It builds and updates the
   widget tree from the model. This is where v0.4.26's inert handles go live.
   The Qt side owns no layout state. No view calls `saveState()`, reaches up to
   a parent splitter, or stores its own geometry.

   *Measured rather than assumed*: `QSplitter.saveState()` returns 35 bytes for
   a three-pane splitter. The state records no widget identity at all.
   `restoreState()` returns false only on a bad magic number or a newer format
   version. So a three-pane state restores into a two-pane splitter and returns
   `True`. This was re-measured on PySide6 6.11.2 / Qt 6.11.2 on 2026-09-16.
   That measurement is the evidence behind `PL-C842`, and it is stronger than
   the form that item recorded.

#### Views

3. **The View registry and the kind tag** (queue item `PL-R1WQ`). This entry
   decides where the registry lives. It decides how a tag is allocated, so
   that an ordinary class rename does not trigger the loud failure meant for a
   View that is genuinely missing. It also decides how the pure-Python model
   validates a tag without importing a Qt view.

4. **Loud failure on an unknown View kind, per Area** (queue items `PL-R1WQ`
   and `PL-SSQW`). This is the flagship divergence from Blender. It is a
   *pane*-level rule, which the file-level version policy in entry 12 cannot
   cover. A saved Workspace that names a View this build does not have fails
   **visibly, in that Area**. It substitutes nothing and drops nothing. Blender
   instead installs a 3D viewport silently. `docs/interface-provenance.md`
   § "Diverged" refuses that behaviour, because this project prefers an obvious
   failure to a plausible-looking wrong one. Entry 20 (`PL-DB5G`) decides what
   that failure looks like.

5. **The View contract** (queue item `PL-TH35`). The contract is written
   *with* the area system and validated against two Views that already exist.
   It carries the four clauses that the 2026-09-16 audit added. They say what
   a View's saved state is and who writes it, and what a View owes when it is
   handed state it cannot read. They also say what a split, a swap and a stack
   round trip each preserve, and what the container does when an Area cannot
   honour a size. The contract is small by construction. It is re-checked
   against its implementers, as § "Prune the contract" in the provenance
   record requires.

6. **An enforced import boundary** (queue item `PL-L8RN`). `QSplitter` is
   confined to the adapter, and concrete View modules are kept out of the
   layout tree. That needs `tools/import_boundary_check.py` to decide a dotted
   import target rather than a root package. The tool has done so since
   `PL-YXFF`, which declared the first such boundary. Both entries land in the
   commit that creates the adapter, because a boundary over a tree that does
   not exist is an `empty` error by construction.

#### Required values stay on screen

7. **The unconditional region** (queue items `PL-NWTM`, `PL-W54S` and
   `PL-NNML`). This is a named region outside the layout container that holds
   every unconditional value. The model has no address for it. So the adapter
   cannot place an Area there, and no serialized Workspace can name it.
   `PL-NWTM` also supplies a pure-Python declaration, free of UI code, of what
   that set of values *is*. The declaration is addressable by tier. One tier is
   invariant. The other is instantiated once per modelled substance, and it is
   what keeps a later intravenous run from being asked for a vaporizer dial it
   does not have. `PL-W54S` is the per-window shape in which that declaration
   is built. It was settled on 2026-09-16 and recorded in `docs/MODEL.md`.
   Every top-level window carries the invariant tier and the name of the run it
   shows. The per-substance tier lives once, in a main window that cannot be
   closed while any other window is open. v0.6.0 opens one window. Building the
   region in that shape now means that break-out, the unscheduled second half
   of planned-milestone item 34, will not have to rebuild it. Entry 20
   (`PL-J8K2`) decides where the region sits and what it looks like, within the
   budget that `PL-84QX` sets. `PL-NNML` joined on 2026-10-20. That day the
   check of the Definition of done found that the page still scrolled the
   region and the use disclaimer out of view. The region now sits above the
   part of the page that scrolls, and the disclaimer sits below it.

8. **An Area that cannot honour a size says so** (queue item `PL-K285`).
   `docs/interface-provenance.md` records three properties that Blender does
   not supply, and this is the second. Blender's behaviour is
   `RGN_FLAG_TOO_SMALL` and a collapse to zero extent. The divergence is
   "a required value is never hidden to make room". This entry decides whether a
   declared minimum is a request or a constraint. It also decides what a split
   or a border drag does when the minimum cannot be met.
    Entry 20 (`PL-DB5G`) decides what the refusal looks like.

#### Workspaces and what they save

9. **State a layout could duplicate or relocate** (queue items `PL-VN6M`,
   `PL-9LNF`, `PL-CNCF` and `PL-PGZF`). There are four pieces of such state.
   The first is the compartment selection, which is owned outside
   `TraceLegend`. The second is `RunView`'s nine `build_*` accessors. They hand
   out the instance's own widgets, so a second request silently reparents a
   widget away from its first placement. The third is the chart time base. A
   dropdown built into one plot's panel owns it, yet it governs both plots. The
   fourth is the chart's column budget. It is read as a maximum over two named
   siblings, and they stop being siblings once each is a View in its own Area.

   **`PL-CNCF` and `PL-PGZF` are cleared by this milestone.** Both items
   measure a per-frame cost *against the column budget this entry relocates*.
   Measuring the cost first and moving the budget afterwards would measure the
   wrong number.

10. **Run identity** (queue item `PL-7Z84`). A run carries an identity that
    stays stable across serialization and does not depend on drawing order.
    `run_label(run_index)` is reduced to a rendering of that identity.
    `docs/MODEL.md`'s rule for when a view names its run is restated in terms
    of that identity, rather than in terms of how many runs are displayed.

11. **The Workspace object** (queue item `PL-WV9K`). This entry decides what a
    Workspace carries **beyond its layout**. That is three things: the pinned
    run, identified by the run identity above; each View's own saved state;
    and what a Workspace switch does to a run in progress. It also decides how the set of
    Workspaces behaves: order, rename, duplicate, delete and save-as-mine.
    Blender refuses to delete the last Workspace. Here the type enforces that
    refusal, rather than a warning dialog. Shipped defaults are distinguished
    from the learner's own, and "reset" is defined.

    *A View's state survives leaving its Area and coming back.* The provenance
    record adopts Blender's per-Area stack of previously-open Editors for the
    property it buys: the outgoing View's state is kept rather than destroyed.
    This milestone ships `swap` and `set_view`, which are the operations that
    would destroy that state. The minimum form is in scope. It keeps one
    retained entry per View kind. That is how Blender bounds the stack by
    construction rather than by a cap.

    *A Workspace excludes preference state, and the tier a setting belongs to
    is decided by instance multiplicity rather than by Workspace membership.*
    There are three tiers. **Run state** is the simulated values. It is one
    set of numbers that every View draws from, and no reader setting changes
    it. **Per-View-instance state** is how *this* View draws those numbers:
    which compartments it shows, its axis denomination and range, and its time
    window. The View serializes this state into the Workspace that contains
    it. It does so by the delegation that `docs/interface-provenance.md`
    § "Persistence, and what happens when an editor is missing" already adopts
    from Blender's `SpaceType`. Two instances of one View kind **in one
    Workspace** hold this state independently. The project owner stated the
    case on 2026-09-17. One graph shows the vessel-rich group against the
    MAC-awake band and the 1 MAC line. A smaller one below it has every
    compartment on. A third, in a squarer Area, is zoomed to the first fifteen
    minutes to read the wash-in. All three are in the same Workspace.
    **Reader preferences** are the settings for which a second simultaneous
    value is incoherent rather than merely unusual. The agent price and its
    currency is the one such setting this project has today.

    The test, therefore, is *can a reader sensibly have two of these on screen
    at once?* If yes, the setting goes to the View. If a second value would be
    incoherent, the setting goes to preferences. A setting that changes the
    numbers rather than how they are drawn is neither. It stays in the
    versioned data files. So a Workspace excludes preference state because it
    is a container of View instances and a preference has one value. The reason
    is not that a unit or a price "is not layout". That is the weaker argument,
    and it is the one that sends the axis range to the wrong tier. Excluding
    preference state for this reason is also what lets Blender's four Save &
    Load entries be added later without a migration. Blender's preference reset
    reads `use_data = false, use_userdef = true`, which resets the third tier
    alone. Meanwhile "reset this Workspace" restores the second tier from entry
    13's shipped JSON.

    **These tiers apply while a run is ephemeral. That is a condition, not a
    permanent property.** Planned-milestone items 9, 10, 12, 26 and 30 add a
    saved scenario. A scenario is a fourth tier. Where it sits is decided when
    the first of those items is scoped, and it is not assumed here.

12. **Persistence** (queue item `PL-SSQW`). This entry decides where the file
    lives on each platform, and the override that a headless run or a test
    uses. It requires an atomic write, so that an interrupted save does not
    leave a truncated JSON file that the next launch has to classify. It
    decides what a first run with no file does. It sets the schema-version
    policy, which handles **older**, **newer** and
    **invalid-at-the-supported-version** files by name. For each case the
    policy says whether the file is migrated, refused, or set aside and
    replaced, and what the learner is told. `core/parameters.py`'s
    single-version rule is correct for files that ship with the code. It is
    wrong for a file the learner wrote. So the rule is decided here rather than
    inherited.

13. **The shipped default Workspaces** (queue items `PL-KXTL` and `PL-L59K`).
    The first is the central-graph default, with the other Views arranged
    around the graph. The second is an induction Workspace with the
    concentration graph zoomed in. The third is a big-picture maintenance
    Workspace. They ship as validated, versioned JSON beside the other shipped
    parameter files. They carry the provenance line that
    `docs/interface-provenance.md` asks of anything derived from Blender's own
    named task Workspaces.
    The three are composed within the pixel budget that entry 20 sets
    (`PL-84QX`). The induction Workspace's zoom is the chart's own saved state.
    So `PL-L59K` adds the zoom once the View contract (entry 5, `PL-TH35`) says
    what that state holds.

#### What a reader can do

14. **The operations a reader performs** (queue item `PL-2KXB`). A border drag
    moves the collinear chain that the `borders()` query returns. A corner
    drag splits and joins. A reader can swap two Areas. The Workspace tab
    strip carries the lifecycle from entry 11. The chain query recovers the one
    behaviour that the tree gives up compared with Blender's graph. `PL-3J2P`
    measured that behaviour as differing exactly once across thirty-two shipped
    Blender Workspaces.
    Entry 20 decides the look of the strip, the handle and the corner
    affordance (`PL-QW1Z`, `PL-RQT1`, `PL-30L5`). `PL-MS34` decides the look
    of the Area header.

15. **Every operation reachable without a drag** (queue item `PL-M352`),
    through a menu and the keyboard. This is not planned-milestone item 20's
    general accessibility pass arriving early. It is a narrower rule: this
    milestone does not *introduce* an interaction that a keyboard-only reader
    cannot perform. Meeting that rule is cheap now. Meeting it later would
    take a retrofit.

16. **The View chooser, and the accounting tier's reachability** (queue item
    `PL-50PZ`). `docs/MODEL.md` puts the agent accounting in a tier that a
    Workspace may omit but that "must stay reachable in every layout, and must
    not be removable from the application". The accounting is cumulative
    delivered, cumulative exhausted, total stored, and the mass-balance
    residual with its absolute error. It is the one required class whose
    guarantee cannot rest on structural presence. So the guarantee becomes an
    invariant of the registry and the chooser instead.
    Entry 20 (`PL-RBXL`) decides how the chooser looks.

#### Tests

17. **The visibility predicate** (queue item `PL-904Y`).
    `SimulationView.interface_strings` is this project's single definition of
    what is on screen. It tests "is this string in this widget's subtree".
    That is the same question as "can the reader see it" only while the
    dashboard is one tree with nothing closeable. This milestone makes the two
    questions differ once an Area can be closed or joined. One predicate covers
    every Area and every top-level window that the application owns. It
    distinguishes present-in-the-tree from visible-to-the-reader. Entry 18
    makes its assertions through this predicate.

18. **Tests over the real interface** (queue item `PL-G5SX`). The tests run
    headless. They drive split, join, swap, resize, Workspace switch, save and
    reload. After each step they assert that every unconditional value is on
    screen, that the accounting tier is reachable, and that a required value
    did not leave with the surface that drew it. They also make the assertion
    that `PL-9LNF` says cannot be written today: resize one Area while paused,
    and the redrawn series is sampled for that Area's new width.

#### Documents to update

19. **The documents this milestone makes out of date** (queue items `PL-ZBBP`,
    `PL-JSY5` and `PL-RTG9`). `.claude/rules/ui-areas.md` is a standing
    prohibition on exactly what this milestone builds. Its `paths:` frontmatter
    does not cover a layout package that lives outside `app/`. So the rule is
    retired or re-scoped rather than left loading. `docs/ARCHITECTURE.md`
    describes the layout that exists. `docs/MODEL.md`'s readout-row rung and
    its always-on-screen disclaimer line both assume one window's width and one
    permanent surface. And `README.md` gains the Blender attribution line.
    `docs/interface-provenance.md` § "Attribution" has held that line back
    until the release in which the shipped interface actually is the
    area/workspace model.

#### Look and edge states

20. **The look and the edge states of every surface this milestone creates**
    (queue items `PL-QW1Z`, `PL-MS34`, `PL-RQT1`, `PL-30L5`, `PL-RBXL`,
    `PL-DB5G`, `PL-J8K2` and `PL-84QX`, and `PL-F2YS`, `PL-JG82` and `PL-QLZ5`,
    which joined on 2026-10-18). **All eight were decided on 2026-10-11**
    (project owner, ratified, over the alternatives each item names). The items
    record the decisions. The build items that they name are where the look is
    built. Every surface this milestone brings into existence has its
    appearance and its edge states decided here. They are not inherited from
    the toolkit, and they are not deferred to the visual pass. Entries 1-19 are
    mechanism. Entry 14 says what a border drag *does*, and entry 16 says what
    the chooser *guarantees*. No entry says what any of it looks like. Without
    this entry, that left the surfaces this milestone creates looking like
    whatever the toolkit's defaults produced, and left planned-milestone item
    33 to redo them one release later. The test for membership is whether the
    surface exists in the application today. The test separates new surfaces
    from inherited ones, not furniture from content. That is why the
    unconditional region and the two failure states qualify beside the
    furniture. There are seven surfaces, each with a queue item behind it:

    **The Workspace tab strip** (`PL-QW1Z`). This entry decides where the
    strip sits and how an active tab differs from an inactive one. It also
    decides how the rename, duplicate and delete actions appear, and how a
    shipped default Workspace is told apart from one the learner saved.

    **The Area header** (`PL-MS34`). The first question is whether there is a
    header at all. If there is, this entry decides its height, its contents,
    and whether the View name and the chooser sit in it. If there is not, it
    decides where the chooser goes instead. Planned-milestone item 33's own
    argument for the move names the header, but no entry specifies it.

    **The splitter handle** (`PL-RQT1`). This entry decides its width, its look
    at rest and on hover, its cursor and its drag feedback.

    **The corner split/join affordance** (`PL-30L5`). This entry decides
    whether the affordance is a visible widget, as in Blender, or a hot zone.
    It also decides whether a drag previews the split before the split
    commits. More than any other interaction in the milestone, this one is
    learned or missed depending on how it looks. An invisible affordance
    means most learners never discover that the layout is theirs.

    **The View chooser** (`PL-RBXL`), as something a learner sees. Entry 16
    specifies only what the chooser guarantees.

    **The two failure states** (`PL-DB5G`). These are a matter of
    presentation safety rather than taste. One is an Area that names a View
    this build lacks (entry 4). The other is an Area that was refused a size
    (entry 8). Both depart from Blender on purpose, and a learner sees both.
    A failure state that looks plausible is the hazard that `CLAUDE.md`'s
    clinical-output standard names.

    **Where the unconditional region sits** (`PL-J8K2`). Entry 7 guarantees
    that the region is outside the layout container. Nothing decides where
    it goes or what it looks like, yet it is on screen in every Workspace a
    learner ever builds.

    **The pixel budget** (`PL-84QX`). It is the one question that none of the
    seven covers alone. The tab strip, the headers and the live handles all
    take screen space from the chart, and the chart is the teaching payload.
    `PL-Z4K6` asked whether seven readout columns are wanted on a 1366 px
    laptop, on a window that carries none of this furniture yet. The project
    needs that number before it adds three new consumers of screen space. **The
    budget** (project owner, 2026-10-11, ratified, over lowering the chart's
    minimum and over keeping the in-page title row, `PL-84QX`) has three parts.
    First, on a 1366 by 768 display, which gives about 700 px of client area,
    the shipped default Workspace with one run shows the concentration chart at
    no less than its current 360 px minimum, with the parameter View visible.
    Second, the furniture above the first Area is capped at two text rows (the
    tab strip and one Area header) plus 8 px per handle. Third, the region
    gives back the in-page title row (`PL-J8K2`).

    Compare mode falls below that minimum on that screen. Compare mode accepts
    that shorter chart on this screen. The layout wins back what space it can
    by folding each run's transport row and heading into one line (project
    owner, 2026-10-18, ratified, over scrolling the page and over refusing the
    chart's Area, `PL-JG82`). The folding is `PL-QLZ5`. `PL-QLZ5` folded them
    on 2026-10-18 and measured the result with the offscreen font. With two
    runs, the region drops from 366 px to 303 px. That leaves the chart about
    264 px, which is 96 px short.

### Definition of done

- A learner can split, join, resize, swap and close Areas. They can switch
  Workspaces by tab, and rearrange, duplicate, rename and delete them. They can
  save their own Workspaces and find them on the next launch.
- A learner can perform every one of those operations from the keyboard as well
  as by drag.
- A Workspace that names an unknown View kind fails visibly in that Area, and
  nothing is substituted. A Workspace file of an unsupported version is handled
  by the written policy, not by whatever the load path found natural.
- Every unconditional value is outside the layout container. For each value, a
  test asserts that no ancestor of its widget is that container. The test also
  asserts that the value is still on screen after a split, a join, a close, a
  Workspace switch and a reload.
- From every shipped Workspace, a learner can bring the accounting tier on
  screen through the interface alone. A Workspace that names none of those
  Views still leaves them reachable.
- **No learner-visible regression against v0.5.0.** Compare mode ships before
  this milestone, and this milestone then rearranges it. Everything a learner
  could do with two runs on 2026-09-16, they can still do. This is checked
  against v0.5.0's own definition of done.
- Tests exercise the layout model with no `QApplication` at all. They include a
  fixture file one schema version ahead of the build and a file truncated
  mid-write.
- `tools/import_boundary_check.py` fails the build if any module other than the
  adapter imports `QSplitter`, or if the layout tree imports a concrete View
  module.
- Two Views that already exist implement the View contract. A test builds two
  surfaces for one run and asserts that both draw.
- `make check` is green, and the documents in Required scope entry 19 describe
  the interface that exists.

### Explicitly out of scope for v0.6.0

- **Break-out into a top-level window.** This is the second half of
  planned-milestone item 34. It is wanted eventually but not soon, so it is on
  no row of the timeline (project owner, 2026-09-26). Splitting break-out off
  costs nothing structural. Break-out would otherwise force a rewrite of two
  things, and both are built here. The serialized root carries a window set
  from version 1 (entry 1), and the unconditional region is built in its
  per-window shape (entry 7). When break-out is built, what it adds is the
  window, the window's lifetime and the test that drives it. **Both
  reservations stay although break-out is unscheduled** (entry 1).
- **Floating Areas or panels - not yet, rather than never.** The option to take
  a tiled Area out into a floating one is wanted later. This milestone does not
  build it. Floating arrives under `docs/MODEL.md`'s occlusion rule, which
  applies to it without being argued again for it.
- **Remembering which screen a window was on.** Restoring a position against a
  changed set of monitors puts a window where the reader cannot see it. That is
  the occlusion failure, arriving through persistence.
- **The View catalogue.** This is planned-milestone item 36. It stays after
  this milestone for the reason that item 34 records. A View's contract is
  whatever the area system requires of its contents. So Views built first would
  be built against today's fixed layout and then rewritten. This milestone
  validates the contract against two Views that exist and builds no new one.
- **The visual pass.** This is planned-milestone item 33: palette, type scale,
  spacing rhythm, density and the visual composition of each surface.
  Arrangement belongs to this milestone, and appearance belongs to item 33.
- **Replace-by-dragging an Area into the middle of another.** The *operation*
  is in scope as `set_view` through the Area's own chooser (entries 1 and 16).
  Only the corner-drag affordance for it is deferred, to whichever release
  takes up the rest of Blender's docking set.
- **Schema migration code.** The policy for an older file is in Required scope
  entry 12. No second schema version exists to migrate from. Writing the
  migrator before the schema it migrates to exists would mean writing it twice.
- **Blender's snap-merge operator and extend-drag**. The splitter-tree
  measurement found that the splitter tree cannot express these two behaviours.
  The five-area pinwheel arrangement is out of scope for the same reason.
  `docs/interface-provenance.md` § "Refused" records the count, the
  construction, and the condition under which the choice of representation
  reverses.
- **Changes to the simulation code (`core/`).** This milestone introduces two
  things that § "Development rules for scientific milestones" requires
  simulation code to stay independent of: filesystem state and display
  dimensions. So the boundary matters more here than usual, not less.
  `tools/import_boundary_check.py` enforces it, and Required scope entry 6 only
  adds to it.
- **Re-reading the Blender design rationale against the primary pages** (queue
  item `PL-PV5Q`). The pages were re-read on 2026-10-25, and the re-reading
  corrected three claims (`PL-PV5Q`).