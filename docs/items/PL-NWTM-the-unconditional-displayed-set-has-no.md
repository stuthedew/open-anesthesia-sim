---
id: PL-NWTM
title: The unconditional displayed set has no structural home in the code, so the guarantee docs/MODEL.md states as structural - a region outside the area system - exists only as prose
priority: P1
effort: L
status: done
classes: safety, anticipated
feature: interface-areas
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/unconditional_set.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/theme.py, docs/MODEL.md, docs/ARCHITECTURE.md, tools/contrast_check.py, tools/literal_home_check.py, tests/benchmarks/frame_cost.py, tests/integration/test_simulation_view.py, tests/unit/test_unconditional_set.py, tests/unit/test_dashboard_frame.py, docs/items/PL-41YP-assert-every-required-displayed-output-reaches.md, docs/items/PL-W9P6-build-the-one-adapter-module-that-drives-the-qt.md, docs/items/PL-JSY5-docs-model-md-s-readout-row-rung-and-its.md, docs/items/PL-W54S-decide-what-a-broken-out-top-level-window-owes.md
blocked-by: PL-1FT6
added: 2026-09-16
closed: 2026-10-18
pr: 1585
payoff: the values docs/MODEL.md says no Workspace may remove leave the splitter tree before its handles go live, so no drag, split, join or close can take them off screen, and a run with no volatile agent is never asked for a vaporizer dial
verify: grep -q 'def test_no_unconditional_value_sits_inside_the_layout_container' tests/integration/test_simulation_view.py && grep -q 'def test_a_run_with_no_volatile_agent_owes_no_vaporizer_circuit_or_mac_value' tests/unit/test_unconditional_set.py
---

**Problem.** The unconditional displayed set has no structural home in the code, so the guarantee docs/MODEL.md states as structural - a region outside the area system - exists only as prose

**Problem.** `docs/MODEL.md`:4859 makes the unconditional set safe *structurally* — a region outside the area system that no split, join, close or workspace switch can reach — and `ROADMAP.md` item 34 calls that region "the guarantee this milestone has to build". No queue item builds it. Worse, the shipped Qt dashboard already puts most of that set inside the reserved splitter tree: `src/anesthesia_sim/app/simulation_view.py:302-309` passes `run.build_readout_section()` into `inert_splitter(Qt.Orientation.Vertical, sections)`, and that section carries `READOUT_PANELS` (`src/anesthesia_sim/app/dashboard_frame.py:442`) — the "Simulated time" panel, whose second line is the playback rate, plus the six compartments — while `run_view.py:1003` puts the control-input record's panel in the sidebar inside the nested horizontal splitter. Only run state, halt reason and agent identity sit outside it, in the page column. The arrangement is asserted by a test: `tests/integration/test_simulation_view.py:245`, "the vertical splitter of readouts, settings and the chart row".

**Why it matters.** Two of the invariant-tier values — simulated time and the rate it advances at — and the whole per-substance tier are therefore inside the container item 34 makes live, so on the day the handles work a learner can close or replace them. `.claude/rules/ui-areas.md` rule 5 ("A required value never moves into something closeable") reads as already satisfied to a session looking at today's code, because nothing is closeable *yet*; the violation is pre-loaded rather than absent. `PL-TH35` (the View contract) touches the question only as "which views may not go in a closeable area at all", which is the weaker form: `docs/MODEL.md`'s settled answer is that such a value does not go in an area at all, making this container structure rather than view contract — and `PL-TH35` is blocked besides.

**Done when.** A named region outside the layout container holds every unconditional value; the layout model has no address for it, so the adapter cannot place a pane there and no serialized workspace can name it; the values above have moved out of the splitter tree; and a test asserts for each unconditional value that no ancestor of its widget is the layout container, and that it is still on screen after a split, a join, a close and a workspace switch.

*Basis (lens `required-values`).* docs/MODEL.md:4859, § "Minimum displayed outputs" → "What this list requires once the layout is the reader's": "**Guaranteed structurally, not by validating a saved layout.** The unconditional region sits outside the area system, so no split, join, close or workspace switch reaches it and no saved layout has to be checked against this list to be safe." ROADMAP.md item 34 restates it as work: "The unconditional set sits outside the area system, which is the guarantee this milestone has to build."

**Problem.** `docs/MODEL.md`:4798 states the unconditional set as a test with two tiers — invariant, and instantiated per modelled substance — and nothing in the tree represents it. `grep -rniE "minimum displayed|required output|unconditional" src/ tests/` returns only prose comments; `tools/doc_check.py` has no check over that section at all. The only machine-readable list is `READOUT_PANELS` (`src/anesthesia_sim/app/dashboard_frame.py:442`), a fixed seven-tuple whose qualifiers ("inspired", "end-tidal-equivalent") are the inhaled instance. The two filed checks predate the three-way split and read a flat list: `PL-036` (extend `doc_check.py`, `ready`) ties each bullet to a `SimulationSnapshot` field, and `PL-41YP` (assert every required displayed output reaches the rendered view, `ready`) carries the field → widget link. Neither distinguishes unconditional from reachable-only from conditional, and neither knows what the run models.

**Why it matters.** The structural guarantee is only as good as the set it is built from, and the set is the half that changes: a run administering no volatile agent owes no vaporizer dial, no circuit concentration and no MAC multiple. A region or a test built from today's seven would then require the display to show quantities the run does not have — the opposite of what the section exists for. This is not `PL-TCD1` re-opened: that item declined reshaping `SimulationSnapshot` per substance on the ground that a later field costs nothing, and this is a declaration of *which displayed values the floor requires*, not of how the snapshot is shaped.

**Done when.** One pure-Python, UI-free declaration returns the unconditional set for what a run models — the invariant tier plus the instance selected by the substance — and is the single source the region is built from and the tests assert over; `PL-036`'s and `PL-41YP`'s checks read it rather than a literal bullet list; and a test instantiates it against a substance with no volatile agent and shows that no vaporizer, circuit or MAC obligation is produced, with today's inhaled run still returning the seven.

*Basis (lens `required-values`).* docs/MODEL.md:4798 and :4809: "The set is stated as a *test*, not as a list … **Instantiated per modelled substance, and the current instance is not the rule** … **That instance holds only while an inhaled agent is what the run models.** … Writing today's instance as the permanent list is a specific error this document has already made once and is guarding against here."

**Problem.** `docs/MODEL.md`:4831 puts the agent accounting and the mass-balance residual in their own tier: removable from a workspace, but reachable in every layout and not removable from the application. Nothing defines what "reachable" means in the area system — a view the area's chooser always offers, a workspace that always exists, a menu entry — and nothing defines what would make the kind "removable from the application". `grep -rilE "stay reachable|reachable in every" docs/items/` returns only `PL-F48B`, which is about git tags; no item under `feature: interface-areas` covers it. Today the values are `accountingPanel` in `run_view.py:1003`, a sidebar panel inside the splitter tree, so there is no registry and no chooser for the guarantee to attach to yet.

**Why it matters.** This tier is how the display says whether the *model* is conserving mass. It is deliberately the one required class a workspace may omit, which makes it the one class whose guarantee cannot be structural presence and must instead be an invariant of the registry and the workspace machinery. Blender supplies the shape rather than the answer: it refuses to delete the last workspace — a floor enforced structurally rather than by warning, which `ROADMAP.md` item 34 already lists as one of the two precedents worth copying. Without an invariant of that kind, a learner who closes the accounting view and saves the workspace has no route back that the application guarantees, and no check would notice.

**Done when.** "Reachable" has a written definition in `docs/MODEL.md` § "Minimum displayed outputs"; the view registry records which kinds are required-reachable and refuses a build that lacks one; the area system's view chooser offers them from any workspace; and a test asserts that from each shipped workspace the accounting values can be brought on screen through the interface alone, and that a workspace naming none of them still leaves them reachable.

*Basis (lens `required-values`).* docs/MODEL.md:4831: "**Reachable rather than simultaneously visible.** The agent accounting — cumulative delivered, cumulative exhausted, total stored, and the mass-balance residual with its absolute error … a layout may leave them out. They must stay reachable in every layout, and must not be removable from the application."

## Area-model audit (PL-BNYF)

**Disposition: `missing-prereq`.** Filed 2026-09-16 by the area-model queue audit (`PL-BNYF`), which swept 49 open and untriaged items and seven gap lenses against `ROADMAP.md` item 34, `docs/interface-provenance.md` and `.claude/rules/ui-areas.md`. Each candidate was checked against the store before it was filed, so a gap an existing item already covers is not here.

**Confirmed 2026-09-19 by `PL-4FBP`'s ratified convention** (a live assertion names what it asserts, a dated one carries its date).
Unchanged, and still `blocked` as its own front matter records. Under clause 2
the unconditional displayed set becomes a code declaration the document is held
to, which is the strongest form the convention takes anywhere - a family whose
members resolve against the tree rather than against a citation.

**Groomed 2026-09-22 (`PL-Y4YG`), while grooming `PL-41YP`:** `PL-036` is
done, not `ready`, and it closed binding § "Minimum displayed outputs" to a
named test per bullet in `tools/doc_check.py`, which never imports the
application package - so the **Done when** clause that has `PL-036`'s check
read this item's declaration needs re-deciding when this is started: a
bare-checkout check cannot call a Python declaration under `src/`. `PL-41YP`'s
half is unaffected.

## Moved to `ready`, 2026-10-12

Set by `PL-1FT6`'s close-out. Read against the tree at that commit, the
readout section is still placed in the vertical `inert_splitter` by
`SimulationView._restack_sections`
(`src/anesthesia_sim/app/simulation_view.py`), and nothing open holds the
region or the declaration. The layout model now exists and addresses Areas
only, so the region needs no change to the model to be unaddressable. The
clause asking that each value stay on screen after a split, a join, a close
and a Workspace switch cannot be driven before the adapter and those
operations exist, and `PL-G5SX` (Required scope entry 18) already carries that
assertion over every operation; this item's test asserts the structural half,
that no unconditional value has the layout container among its widget's
ancestors. It goes first because `PL-W9P6` turns the handles live, and the
order the v0.6.0 Goal names - the required values out of the container before
it becomes live - is the one that keeps them on screen; `PL-W9P6` is blocked
on this item for that reason. The `PL-036` half of the second Done when still
wants the re-decision the 2026-09-22 note records, and the third Problem,
reachability, is `PL-50PZ`'s (Required scope entry 16).

## Build question 2026-10-18: the delivered concentration and the 1 MAC divisor

**Question put to the owner.** `docs/MODEL.md`'s per-substance tier requires
the delivered concentration in both units and the running agent's 1 MAC in
percent, so that the ×MAC readouts state their divisor. The band `PL-J8K2`
ratified, as its mock-up draws it, holds neither: the delivered value is only
on the dial in the Parameters View, and "1 MAC sevoflurane = 2.0%" is only in
the chart's caption. Both are Views a learner will be able to close. The laptop
budget (`PL-84QX`) leaves 25 px of slack, so no new row fits.

**Recommendation: the heading line.** Add both to the line above the seven
readout cards, which already exists and carries the substance heading, for
example "Delivered 2.50% (1.25 ×MAC) · 1 MAC sevoflurane = 2.0%". It costs no
height and leaves the dial and the chart caption as they are. *Alternatives:*
an eighth "Delivered" card, which narrows every card and may wrap the row to
two rows (+122 px) on the laptop; or leaving both in closeable Views and
amending `docs/MODEL.md` to drop them from the tier.

The build goes on with the parts both answers share. The heading line landed
in the same commit as the region, as two labels in `RunView`
(`_delivered_text`, `_one_mac_text`) and `dashboard_frame.delivered_line`, so
another answer replaces those three and their two tests.

## Built 2026-10-18

**What was built.** `app/unconditional_set.py` is the declaration the second
Done when asks for: a toolkit-free module whose `unconditional_set(substance)`
returns the invariant tier, the per-substance tier the substance selects, and
the control-input record. `INHALED_AGENT` is today's instance, with the seven
concentrations and the 1 MAC divisor. The accounting is absent by design,
because it is reachable-only and `PL-50PZ`'s. `SimulationView` now builds one
region above the splitter, laid out to `PL-J8K2`: each run's transport row with
its badge at the right end, its notice, its readout heading and cards on the
left, and its control-change record in a right column that scrolls within
itself. The title row is gone. `RunView.unconditional_widgets` maps every
declared value to the widget that draws it, and `_place_run` refuses a run
whose region lacks one, so a value moved back into the splitter fails at
construction.

**The record column's width.** It takes a quarter of the band, about 300 px at
a 1366 px window, rather than the sidebar's 228 px. At 228 px today's record
lines are cut off on the right (measured offscreen on `main` at `47d28760`), and
at 300 px they are not, while the seven readout cards still stand in one row
beside it. Holding it at exactly the sidebar's width was tried and gave the
record a horizontal scroll bar, because its longest line needs 257 px. The
exact width is `PL-W54S`'s, as `PL-J8K2` Q3 left it.

**Done-when clauses, one by one.**
- *A named region outside the layout container holds every unconditional
  value:* `SimulationView.unconditional_region`, object name
  `unconditionalRegion`. `test_no_unconditional_value_sits_inside_the_layout_container`
  asserts all 14 values for two runs.
- *The layout model has no address for it:* unchanged, since
  `src/anesthesia_sim/layout/` addresses Areas only and the region is not one.
- *Still on screen after a split, a join, a close and a Workspace switch:*
  `PL-G5SX`'s, as the 2026-10-12 note records; those operations do not exist
  yet.
- *One declaration, the single source the region and the tests read:* done.
  `test_a_run_with_no_volatile_agent_owes_no_vaporizer_circuit_or_mac_value`
  builds a substance with no volatile agent and finds no vaporizer, circuit or
  MAC value owed.
- *`PL-036`'s check reads it:* dropped. `PL-036` closed binding each bullet of
  the section to a named test in `tools/doc_check.py`, which runs from a bare
  checkout and cannot import `src/`. The tests it names now read this
  declaration, which is the reachable half.
- *`PL-41YP`'s check reads it:* `PL-41YP` is open and not this item's. Its
  brief now says to build from `unconditional_set`.
- *Reachability (third Problem):* `PL-50PZ`'s.

**Regression check against the code before the fix.** A variant of the new
container test that needs no new interface (it asks `view._sections` whether
it holds `run._readout_row` and `run._control_timeline_text`) was run on a
worktree of `origin/main` at `47d28760` with
`PYTHONPATH=<worktree>/src:<worktree> .venv/bin/python -m pytest -k pl_nwtm_variant`.
It failed with `AssertionError: inside the layout container`, since the
splitter `isAncestorOf` the `ReadoutRow`.

**Self-review, `bin/docket verify --self PL-NWTM`.** It returned REJECT on one
check: eight assertions in four tests changed. Each one is a test of the old
arrangement, and each change follows the layout `PL-J8K2` ratified:
- `test_the_header_shows_the_application_name_from_app_metadata` became
  `test_the_page_leaves_the_application_name_to_the_window_title`, because the
  title row is gone (Q2).
- `test_a_second_build_sidebar_panels_leaves_the_run_labels_on_screen` became
  `test_a_second_build_of_the_record_panels_leaves_the_run_labels_on_screen`,
  because `build_sidebar_panels` split into two builders.
- `test_the_run_added_after_construction_is_named_and_given_its_own_sections`
  now expects one new splitter section rather than two, since the readout
  section left the splitter, and asserts the new run's readouts are in the
  region.
- `test_the_sidebar_panels_name_the_run_they_record` now finds the named
  heading in either column, since the record moved to the band.
Its other note, whether a new test asserts the value the model should give,
is answered by the heading test's literals: 2.00% of a 2.0% MAC is 1.00 ×MAC,
and 3.00% is 1.50 ×MAC, worked by hand rather than read from the view.

**Unblocked here.** Closing this item left `PL-JSY5`, `PL-W54S` and
`PL-W9P6` blocked on nothing, so this pull request moves each to `ready` with a
`payoff:` and a `verify:`. `PL-JSY5` and `PL-W54S` carry the `safety` class, so
they move from `P2` to `P1`, as `docket check` requires of safety work.

**Fix-now:** none.

## Answered 2026-10-18: the heading line

**The heading line stays** (project owner, 2026-10-18, ratified, over an eighth
"Delivered" card and over dropping both values from the tier), given in the
project thread at 17:40 UTC as "Agree with recs". In the same message the owner
said that look-and-feel choices like this one are placeholders for now, while
the structure and function are developed. So the heading line's wording and
placement are not settled design. The requirement under it is: `docs/MODEL.md`
still requires the delivered concentration and the 1 MAC divisor to be on
screen in every layout.
