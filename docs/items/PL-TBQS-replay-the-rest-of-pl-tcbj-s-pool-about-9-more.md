---
id: PL-TBQS
title: Replay the rest of PL-TCBJ's pool, about 9 more merged simulator pull requests, with one-generalist, three-generalist and specialist-panel arms on every pull request and scored per defect, to choose between a panel and generalist review passes
priority: P3
effort: L
status: done
classes: planning
feature: review-panel
milestone: v0.6.3
touches: docs/items/PL-TBQS-replay-the-rest-of-pl-tcbj-s-pool-about-9-more.md, docs/items/PL-TDV9-add-one-more-blind-generalist-review-pass-on.md
added: 2026-10-24
closed: 2026-10-24
pr: 1750
payoff: the choice between a specialist reviewer panel and generalist review passes rests on about 19 pull requests and an equal-cost comparison, not on ten
verify: grep -qE '^\*\*Result' docs/items/PL-TBQS-replay-the-rest-of-pl-tcbj-s-pool-about-9-more.md
---

**Problem.** Replay the rest of PL-TCBJ's pool, about 9 more merged simulator pull requests, with one-generalist, three-generalist and specialist-panel arms on every pull request and scored per defect, to choose between a panel and generalist review passes

**Why it matters.** `PL-TCBJ` (the first replay of a specialist reviewer panel) could not tell the panel from one generalist reviewer. The panel caught the later-filed defect in 4 of 10 merged pull requests and the generalist in 5. Only 3 pull requests were caught by one arm and not the other. The panel also ran three reviews to the generalist's one, so more draws could explain its catches as well as specialism could. The project owner asked for a larger test before choosing, and `PL-TDV9` (one more blind generalist review pass) is held until this one reports.

**Decision** (project owner, 2026-10-24, ratified, over choosing on `PL-TCBJ`'s ten pull requests, over running the rest of the pool with one generalist only, and over planting seeded defects to grow the sample past the pool).

**What this test can show, stated before it runs.** The pool holds about 18 or 19 pull requests, so the sample cannot grow past that without changing what is measured. At that size, an exact paired test detects an arm that wins 3 of every 4 discordant pull requests only about 9% of the time (`PL-TDV9` has the calculation). Scoring each key defect adds resolution, but defects in one pull request are not independent: `#578` and `#775` alone hold 10 of `PL-TCBJ`'s 20. So no p-value is computed on the defect counts. The bar below is a decision rule fixed in advance, not a significance test. That is acceptable here because the choice is cheap to reverse: a review pass can be added, removed or replaced on any later pull request.

**Protocol, fixed on 2026-10-24 before any review in this item runs.**

*The pool.* The pool is `PL-TCBJ`'s 73 candidate pull requests, less `#588`, in the order that `random.Random(20261024)` drew them. Candidates 1 to 39 are already examined and gave the 10 in `PL-TCBJ`'s answer key. Before using any later candidate, re-derive the candidate list with the SZZ procedure that `PL-TCBJ`'s protocol describes, and check that its first 24 match the order recorded there. If they do not match, stop and report rather than walk a different list.

*Verifying the new pairs.* Walk candidates 40 to 73 in that order and verify each pair as `PL-TCBJ` did: a pull request enters only when the defect its item describes lives in lines that pull request added. Every verified pull request enters, with no cap. Write one sentence per verified defect and commit those sentences to this item before any reviewer's output for that pull request is read.

*The arms.* Every pull request in the sample has four arms, all using "The reviewer brief, as run" in `PL-TCBJ`, unchanged, at the session's own model and effort:

1. **G1**, one generalist run. For `PL-TCBJ`'s ten, this is its clean control run, reused as recorded in its Result table. Each new pull request gets a fresh run.
2. **G2** and **G3**, two more generalist runs, each started fresh.
3. **Panel**, the three specialists (PK/PD, numerics and state, clinical display). For `PL-TCBJ`'s ten, this is its panel, reused as recorded. Each new pull request gets a fresh panel.

That is 2 new runs on each of the ten and 6 on each new pull request, about 74 in all. The three-generalist arm (G1, G2 and G3 together) costs the same as the panel. Each run gets its own directory holding only the tree at the merge commit, the diff and the brief, because `PL-TCBJ`'s first control was discarded after a reviewer read another arm's findings.

*Checking.* One blind checker per pull request marks each new finding correct, incorrect or not checkable against the code at merge, as in `PL-TCBJ`. This now includes the generalist findings, which `PL-TCBJ` did not check.

*Scoring.* `PL-TCBJ`'s own findings may still be readable in the transcript of the session that ran it (`session_01JQuNZNYNK5kqZyBxjguXe6`, read with `list_events`), because its reviewers returned their findings as their final replies. If they are, score them again with the new ones, so one scorer scores every arm. If they are not, reuse `PL-TCBJ`'s Result table for its ten. Score each finding against the key with its arm hidden: pool the findings for a pull request under random labels, score them, then unmask the labels. A pull request counts as caught by an arm when any of that arm's findings names its key defect, as `PL-TCBJ` defined it. A key defect counts as named by an arm when at least one run in that arm names it. Near misses are recorded and not counted.

**The bar, fixed before the count.** The decision is made on key defects named across the whole sample:

- Build the panel only if it names at least 3 more key defects than the three-generalist arm.
- Otherwise build generalist passes. Build one pass, as `PL-TDV9` describes. Build a second pass only if G2 and G3 together name at least 3 key defects that G1 missed.

Also report, without letting them change the decision: per-pull-request catches for each arm, the panel against G1 alone, what G2 and G3 each add to G1 on their own, and each arm's share of incorrect findings.

**Cost.** About 74 reviews at 150,000 to 300,000 subagent tokens each, so 11 to 22 million tokens, plus verifying up to 34 candidates and one checker per pull request. It runs as a multi-agent workflow, which needs the owner's explicit go-ahead because it is far larger than the default of fewer than 10 agents.

**Done when.** A `**Result.**` heading here lists every pull request in the sample with each arm's catches, the key defects each arm named, and the bar applied. `PL-TDV9`'s brief then records which build the bar chose, or an item is filed to build the panel and `PL-TDV9` is dropped with the reason.

**Limitations known in advance.** If `PL-TCBJ`'s findings cannot be recovered, its G1 and panel results on its ten were scored by a different session with the arm visible, so their scoring differs from the new runs'. Each run is one draw, and a second run of the same reviewer could find different things. The sample is still limited to defects that SZZ can trace to a diff.

**Generator check.** Work the owner asked for, on 2026-10-24. It touches only its own brief, and no head's fact explains it.

**Stage 1, 2026-10-24: the candidate order reproduces.** The brief's prose did not pin the SZZ procedure down closely enough to re-derive the order. Read literally, it gave 85 candidates, and with every id before the colon counted as a fix it gave 132. So `PL-TCBJ`'s own scripts were recovered verbatim from its session's transcript (`session_01JQuNZNYNK5kqZyBxjguXe6`) and run again here, against `origin/main` at `2f0101bb7` (`#1722`), the head that session read. The recovered procedure differs from the prose in five ways:

- A commit counts as a fix when the item's id appears anywhere before the subject's first colon.
- Only the top 4 blamed commits per item are kept.
- A commit that is not an item's most-blamed one needs at least 2 blamed lines.
- An item classed `test` or `infra` is dropped at the candidate step, and a blamed commit whose subject names the item is not a candidate.
- A pull request of more than 6,000 changed lines, counting every path, is dropped before the shuffle. That is the rule that removed `#588`.

The run gave 73 candidates, dropped `#588`, and shuffled 72. All 72 positions match the order the recovered transcript printed (1 to 44) and the recovered shuffle (45 to 72), and the first 24 match the order recorded in `PL-TCBJ`. The pool therefore ends at position 72, not 73. Positions 40 to 72 are `#308`, `#1428`, `#1448`, `#430`, `#1622`, `#283`, `#561`, `#1592`, `#288`, `#421`, `#488`, `#516`, `#376`, `#399`, `#1361`, `#784`, `#665`, `#568`, `#618`, `#1480`, `#1328`, `#316`, `#671`, `#556`, `#1191`, `#1188`, `#319`, `#306`, `#539`, `#263`, `#805`, `#311` and `#512`. Together they carry 104 pull-request and item pairs to verify.

**Answer key for the new pull requests, committed before any reviewer ran.** Five verifier subagents checked all 104 pairs at positions 40 to 72. Pull requests that share an item went to the same verifier. They accepted 19 defects in 10 pull requests. The other 23 pull requests had no verified pair: `#308`, `#1428`, `#283`, `#561`, `#1592`, `#488`, `#516`, `#399`, `#1361`, `#665`, `#618`, `#1480`, `#316`, `#671`, `#556`, `#1191`, `#1188`, `#319`, `#306`, `#539`, `#263`, `#311`, `#512`. Their pairs were SZZ false positives of the kinds `PL-TCBJ` met: docstrings, renames and moved code, a fault that predates the pull request or arrived with a later change, or an item that is a queue, planning or tooling task. The session checked two keys against the merge commits itself. For `#421`'s `PL-BMY5`, `SimulationState.__post_init__` never calls `require_supported_run_length`. For `#784`'s `PL-J12Z`, `ForkPanel.set_offer` calls `setCurrentIndex(max(restored, 0))`. Each entry gives the pull request's position in the drawn order. Where an item holds several faults and only some were added by that pull request, the entry names the part that counts. The verifiers' verdicts and reasons for all 104 pairs are in `replay/PL-TBQS/verify.json` on this branch.

- `#1448` (position 42), `PL-391Y`. In `layout/model.py` at b7a092afb, `LayoutModel.split` checks that a part has no size only on the same-axis branch. A nested cut such as `split(AreaId(1), Orientation.ROW, 5e-324)` on a single Area is taken, giving sizes `(5e-324, 1.0)` and an Area whose two edges `borders()` treats as one line. `Split` in `layout/tree.py`, and so `layout_from_dict`, accept sizes `(1.0, 5e-10)` because they sum to one within `LAYOUT_SIZE_SUM_TOLERANCE`, and `_boundaries` then places the second Area at left 1.0 and right 1.0, with no width.
- `#430` (position 43), `PL-3LZB`. In `core/run_score.py` (later renamed `run_definition.py`), the new `RunScore._require_within_run` refuses only `elapsed_s < 0.0`, the literal zero rather than the first segment's opening. The new `_segment_index_at` returns `bisect_right(self._segments, elapsed_s, key=_opening_of) - 1`, which is -1 for an instant before the first opening and so indexes the last segment. A score opening after zero would therefore answer `state_at`/`evaluate` at an instant before its opening with the last segment's keyframe, because `_propagator` returns None for the non-positive interval, instead of refusing.
  <!-- absent: core/run_score.py -->
- `#1622` (position 44), `PL-4L8B`. #1622's `AreaLayout._settle` in `app/area_layout.py` holds each Area frame at its View's need, which it reads only from build, resizeEvent, showEvent and drags, never after `refresh` draws the Views. The setting controls' Area is therefore fixed at the 220 px need read before their first frame and drawn 336 px wide. It jumps to the 590 px it needs once a later re-settle reads the filled-in View, so the first border move shifts the chart Area by about 250 px. Counted part: The launch-width half (the late re-settle after the first frame). The arrow-key half, where `border_stepped` steps from the model position, involves keyboard border stepping that was added after #1622.
- `#1622` (position 44), `PL-YJ21`. #1622's `AreaLayout._settle` in `app/area_layout.py` reads each View's `minimumSizeHint` only from build, resize, show and drags, and `AreaLayout.refresh` draws the Views without settling again. A View that builds or hides widgets on its first frame, such as ParameterControlsView's per-run copies or the concentration chart's per-run lines, leaves the Areas and the page sized from its pre-frame need.
- `#1622` (position 44), `PL-PHPZ`. #1622 overrides `AreaLayout.minimumSizeHint` in `app/area_layout.py` with `_least`, which `_settle` recomputes, calling `updateGeometry`, only on build, resize, show or drag. After the Views draw their first frame and their needs grow, nothing tells the parent layout, so the scrolling page lays the Areas out from the stale pre-draw hint.
- `#288` (position 48), `PL-90Y6`. In `app/simulation_view.py`, the new MAC-awake band is a single `chart_series.build_reference_line` series stroked only at its upper edge, filled through `below_line_bgcolor` down to the `below_line_cutoff_y` that `chart_series.redraw_reference_band` sets. The legend swatch is ruled only with `Border(top=...)`. With no stroke on the lower edge, the +/-0.05 MAC band, about 3.3% of plot height on the 3 MAC axis, draws as a line with a shadow rather than as an interval.
- `#421` (position 49), `PL-BMY5`. In `core/simulation.py`, #421 added the 24 h run-length guard `require_supported_run_length` only to `SimulationState.advance`, not to `__post_init__`. So `SimulationState(step_count=1_000_000, simulation_step_s=0.1)` builds without complaint and reports 100 000 s (27.8 h) elapsed, past `MAXIMUM_ELAPSED_SIMULATION_TIME_S`, and only the next `advance()` refuses it with `SimulationDomainLimitError`.
- `#421` (position 49), `PL-5291`. In `app/controller.py`, #421 records the 24 h limit only in the latch `_supported_limit_reason`. Only `halt_at_supported_limit` sets it, after the core refuses a step, and `snapshot()`, `start()` and the view's Start button and limit notice read only that latch. So a run standing exactly on 86 400 s with no step yet refused (for example, paused after the tick whose last step lands on 24:00:00) reads Paused, offers Start and shows no limit notice until Start is pressed and one tick is refused. Counted part: The latch design and the trunk route (a run standing on 24:00:00 before any step has been refused). The fork, branch-reset and time-mark routes in the item arrived with later pull requests that reused the latch.
- `#376` (position 52), `PL-2MD9`. In `core/matrix_exponential.py`, the new `matrix_exponential` shifts the matrix by `shift*I`, sums the series at the scaled interval, multiplies by `exp(-shift*scaled_interval_s)` and then squares `squarings` times. It never restores a zero row of A to its identity row and puts no cap on the squarings. The constant `UNIT_STATE` row's diagonal therefore comes back as 1+delta, and the squarings raise it to (1+delta)^(2^s). With `AlveolarCompartment.gas_volume_l` driven small at the 0.1 s step, `propagator[UNIT_STATE][UNIT_STATE]` reads 2.28e+222 at 1e-19 L, and the propagator is about 100% wrong at 1e-18 L while accounting passes. This contradicts `governing_equations.UNIT_STATE`'s docstring promise that no step can perturb it.
- `#376` (position 52), `PL-3PRZ`. In `core/matrix_exponential.py`, the new `matrix_exponential` checks only that the squared propagator is finite. When the squarings drive it to the all-zero matrix (sevoflurane at 0.1 s with `gas_volume_l` at 1e-300 L) it is returned anyway, `propagate` yields the zero state, and the run reports a concentration of exactly 0 with the mass-balance check passing. In addition, `_squarings_for` returns `ceil(log2(norm / MAXIMUM_SERIES_ARGUMENT_NORM))` without checking that the quotient is finite, so at 1e-309 L it overflows and a bare `OverflowError` escapes instead of a `SimulationConfigurationError`.
- `#784` (position 55), `PL-K5NY`. The new `SimulationView.add_run` in `app/simulation_view.py` checks only the displayed-run cap and that the agent matches. A controller that is not a branch of `self._case`, such as a fresh `SimulationController()` on the same agent, is therefore placed, drawn and named 'Run 2' of a case whose `runs` does not contain it.
- `#784` (position 55), `PL-J12Z`. The new `ForkPanel.set_offer` in `app/qt_widgets.py` restores the reader's selection with `setCurrentIndex(max(findData(selected_s), 0))`. When the selected instant is no longer a keyframe, for example after a dial is returned to its previous value at the same paused instant, `findData` returns -1 and the selector is moved to index 0 (induction). 'Branch here' then forks at induction.
- `#784` (position 55), `PL-WG73`. #784 added `COMPARING_FORK_LOCK_TEXT` in `app/dashboard_frame.py`, which reads 'One comparison at a time. Reset the case to end this one.' No control is labelled that way; the only label is `RESET_LABEL` = 'Reset'. In a two-run comparison the branch's Reset, the one a learner is likely to press, returns the branch to its fork and discards its progress while the lock stays in place.
- `#784` (position 55), `PL-T91K`. In `SimulationView`'s page builder in `app/simulation_view.py`, #784 added an always-visible `notices` widget to the 12 px-spaced page column, and `_place_run` wraps each run's banner in a `_holder` placed in it. With every banner hidden, the empty container still costs one 12 px column spacing with one run, and each further visible holder costs another 12 px with two runs.
- `#784` (position 55), `PL-LQ19`. In `app/simulation_view.py`, #784's `_place_run` connects the first run's `case_restarted` to `_handle_case_restarted`, and that handler's only guard is `len(self._runs) == 1`. On a dashboard built over loose controllers with no case, Reset on run 1 therefore removes every other run and its recorded history.
- `#784` (position 55), `PL-75P5`. #784's `SimulationView._handle_case_restarted` in `app/simulation_view.py` returns at `if len(self._runs) == 1` before it reaches `self._fork_refusal = None`. On a one-run case dashboard, the banner of a refused 'Branch here' press therefore stays after the trunk's Reset, naming an instant the restarted run no longer holds.
- `#568` (position 57), `PL-NC62`. In `app/controller.py`, the new `SimulationController.resumed_at` compares the replayed `equation_settings()` with `resume_point.segment.settings` by whole-object equality. On any difference it raises one fixed message ending 'the recorded timeline does not reproduce its own segments', so an agent or patient mismatch (for example, a data file edited between building the trunk and taking the branch) is blamed on the timeline, and no differing field or value is named. The agent's MAC, display name and vaporizer maximum, which the branch re-reads, are not compared at all.
- `#1328` (position 60), `PL-5D1Z`. The new `SimulationStep(float)` in `core/simulation_step.py` checks the step's range only in `__new__` and defines no `__reduce__`. A protocol-0 or protocol-1 pickle is therefore rebuilt through `copyreg._reconstructor`, which calls `float.__new__` and skips the check. A pickle of `SimulationStep(0.05)` edited to 5.0 loads as a `SimulationStep` holding 5.0, and `require_simulation_step` then accepts it, although protocol 2 refuses it. Counted part: The SimulationStep instance only. The other checked types the item names (the flows, CaseInstant, StepCount and the class-based Fraction and Percent) were added later, after this pull request.
- `#805` (position 70), `PL-1ZQ4`. #805 made `SimulationController._resume_point_at` in `app/controller.py` open a branch at a keyframe with `self._resume_point(segment, segment.opening, None)`, which carries no crossing, while the halt door seeds the halt's crossing. On a trunk halted on a mark at 118.1 s with a setting changed there, `resumed_at(118.1)` reads the 118.05 s time mark as before_this_branch and the MAC target as still_running, while the halt-door branch at the same instant reads them as passed and reached. Counted part: Case 3 only: fork_at (`resumed_at`) at a keyframe the trunk is halted on opens on no crossing, where the halt door opens on the halt's crossing.

With `PL-TCBJ`'s ten, the sample is 20 pull requests and 39 key defects.

**Stage 2, 2026-10-24: 80 reviews ran.** Each new pull request got G1, G2 and G3 and a fresh three-specialist panel. Each of `PL-TCBJ`'s ten got G2 and G3. Every run was a general-purpose subagent at this session's model and effort. Its one-line prompt pointed it at a brief file in its own directory, as `PL-TCBJ`'s runs did. The briefs match `PL-TCBJ`'s word for word, with the role strings recovered from its transcript. The directory held only the tree exported at the squash commit, `tree/REVIEW_DIFF.patch` (the commit message and diff) and the brief. Panel members had a directory each, not one shared directory as in `PL-TCBJ`. The 80 runs used 13.3 million subagent tokens, about 166,000 each. `PL-TCBJ`'s G1 and panel findings for its ten were all recovered from its session's transcript, so all six arms on all 20 pull requests go to the same scorers.

Findings per arm (a run with `NO FINDINGS` counts 0):

| Arm | `PL-TCBJ`'s ten | The ten new | Runs with no findings |
| --- | --- | --- | --- |
| G1 | 24 | 21 | 3 |
| G2 | 20 | 27 | 2 |
| G3 | 18 | 28 | 3 |
| Panel: PK/PD | 16 | 18 | 5 |
| Panel: numerics | 22 | 26 | 1 |
| Panel: display | 24 | 25 | 3 |

The panel's 62 findings on `PL-TCBJ`'s ten match the count its Result reports, which confirms the recovery. The raw findings are in `replay/PL-TBQS/findings_by_label.json` under blind labels, one label per run within each pull request. The table from label to arm is committed only after scoring.

The sample came to 10 new pull requests, not about 9, so the run needs 80 reviews and, with checkers and scorers, about 110 agents. That is above the about 90 first approved (project owner, 2026-10-24, ratified, over having 4 checkers each check 5 pull requests to stay near 90, which would have broken the brief's one checker per pull request).

**Result, 2026-10-24.** The bar chooses generalist review passes, and two of them. The panel named 19 of the 39 key defects and three generalist runs named 21, so the panel fell short of the 3 more it needed by 5. G2 and G3 together named 3 key defects that G1 missed, which meets the threshold of 3 for a second pass exactly. One of those 3 was a close call, as the second limitation below says.

*How it was scored.* Four scorer subagents scored every arm on all 20 pull requests. Each scored five pull requests, with every run's findings under a random label (`random.Random("PL-TBQS-<pr>")`), against the key. The labels were unmasked by a script only after all four had returned. `PL-TCBJ`'s own findings were recovered, so its ten were scored again with the new runs. The blind rescore matches the table `PL-TCBJ` recorded with the arms visible: on its ten, G1 named 8 key defects in 5 pull requests and the panel 7 in 4. A key defect counts as named by an arm when at least one run in that arm names it. Near misses are recorded and not counted.

| Pull request | Key defects | G1 | G2 | G3 | Panel |
| --- | --- | --- | --- | --- | --- |
| `#1451` | 1 | - | - | - | - |
| `#1292` | 1 | - | - | - | - |
| `#1585` | 1 | - | - | - | - |
| `#331` | 2 | `PL-NBWP` | - | - | - |
| `#1350` | 2 | - | - | - | - |
| `#1365` | 1 | `PL-979Z` | - | - | - |
| `#775` | 4 | `PL-3K9B`, `PL-4KZD`, `PL-LHBY` | the same three | the same three | the same three |
| `#204` | 1 | - | - | - | `PL-BNPY` |
| `#578` | 6 | `PL-TCR5`, `PL-LTKL` | the same two | the same two | the same two |
| `#1354` | 1 | `PL-979Z` | `PL-979Z` | - | `PL-979Z` |
| `#1448` | 1 | `PL-391Y` | - | - | - |
| `#430` | 1 | - | - | - | - |
| `#1622` | 3 | `PL-4L8B`, `PL-YJ21`, `PL-PHPZ` | the same three | the same three | the same three |
| `#288` | 1 | `PL-90Y6` | - | `PL-90Y6` | `PL-90Y6` |
| `#421` | 2 | - | - | - | `PL-BMY5` |
| `#376` | 2 | `PL-3PRZ` | `PL-2MD9`, `PL-3PRZ` | - | - |
| `#784` | 6 | `PL-WG73`, `PL-LQ19`, `PL-75P5` | `PL-WG73` | `PL-K5NY`, `PL-WG73`, `PL-LQ19` | `PL-K5NY`, `PL-J12Z`, `PL-WG73`, `PL-LQ19`, `PL-75P5` |
| `#568` | 1 | - | - | - | - |
| `#1328` | 1 | - | - | `PL-5D1Z` | `PL-5D1Z` |
| `#805` | 1 | `PL-1ZQ4` | `PL-1ZQ4` | `PL-1ZQ4` | `PL-1ZQ4` |

*The bar.* The rule fixed before the count builds the panel only if it names at least 3 more key defects than the three-generalist arm. It named 19 and that arm named 21, a difference of -2, so the build is generalist passes. A second pass is built only if G2 and G3 together name at least 3 key defects that G1 missed. They named exactly 3:

- `#376`'s `PL-2MD9`, named by G2.
- `#784`'s `PL-K5NY`, named by G3.
- `#1328`'s `PL-5D1Z`, named by G3.

So the bar chooses two generalist passes.

*Reported, not deciding.*

- **Key defects named across the 39:** G1 18, G2 13 and G3 14. The three generalist runs together named 21. The panel named 19: its PK/PD reviewer 6, its numerics reviewer 15 and its display reviewer 11.
- **Pull requests caught across the 20:** G1 11, G2 7, G3 7, the three generalist runs together 12, and the panel 10.
- **Panel against G1 alone:** 19 key defects to 18. The panel alone named 5: `PL-BNPY`, `PL-BMY5`, `PL-K5NY`, `PL-J12Z` and `PL-5D1Z`. G1 alone named 4: `PL-NBWP`, `PL-3PRZ`, `PL-979Z`'s concentration half and `PL-391Y`.
- **Panel against all three generalist runs:** the panel alone named 3 (`PL-BNPY`, `PL-BMY5`, `PL-J12Z`). The generalist runs alone named 5 (`PL-NBWP`, `PL-2MD9`, `PL-3PRZ`, `PL-979Z`'s concentration half, `PL-391Y`).
- **What each later run adds to G1:** G2 alone adds 1 (`PL-2MD9`) and G3 alone adds 2 (`PL-K5NY`, `PL-5D1Z`).
- **Defects no arm named:** 15 of the 39. For 8 of those, some run pointed at the right code with a different failure.

*Noise.* One blind checker per pull request marked every finding that `PL-TCBJ` had not already checked. That covered all generalist findings on all 20 pull requests and the new panels' findings on the new ten. Marked incorrect: G1 0 of 45, G2 1 of 47, G3 0 of 46, and the new panels 1 of 69. Marked not checkable: G1 1, G3 1 and the new panels 1. `PL-TCBJ`'s checker had marked its panel's 62 findings on its ten 59 correct, 3 not checkable and 0 incorrect. Its #1585 record was only partly recovered, so its own totals are used. The checker ran on the same model as the reviewers, as in `PL-TCBJ`, and could share their blind spots.

*Limitations.*

- **This sample is the whole pool.** The SZZ pool is exhausted at 20 pull requests and 39 key defects, so no larger replay of this kind can be run without changing what is measured. The defects cluster: `#578` and `#784` hold 12 of the 39.
- **The second pass rests on a close call.** It rests on exactly 3 defects. For `#376`'s `PL-2MD9`, the scorer counted a finding that describes the same squaring amplification through a decaying entry rather than a growing one. The scorer recorded this as the same cause through a different symptom. Without it, G2 and G3 add 2 and the bar would choose one pass. The call was made blind and stands as scored.
- **The earlier runs ran under different conditions.** `PL-TCBJ`'s G1 and panel on its ten ran in another session. Its panel shared one directory, and its G1 ran after a discarded first control. The new runs each had a directory of their own.
- **Every run is one draw**, and G1 on the new ten is itself one more draw of the same brief as G2 and G3. Scorers and checkers ran at this session's model and effort, and so did the reviewers.

*Cost.* The run used 110 subagents and about 17.5 million subagent tokens:

- 1 recovered `PL-TCBJ`'s records from its transcript.
- 5 verified the 104 candidate pairs.
- 80 reviewed.
- 20 checked.
- 4 scored.

*Findings beyond the key.* 214 of the 269 findings name no key defect. The checkers marked 261 of the 269 correct, so most of those 214 describe real faults at merge. Many may since have been fixed or filed, and this item does not sort them. One item is filed under the `replay-findings` feature to check them against `main`. The raw findings, the label table, the scores and the checks are in `replay/PL-TBQS/` in this item's pull request commits.
