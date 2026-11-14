---
id: PL-YRY3
title: Line edit ROADMAP.md section by section with the fixed copy editor once its restructure has landed
priority: P3
effort: L
status: dropped
classes: docs
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
closed: 2026-11-11
reason: the project owner dropped it on 2026-11-11 when the copy editor's per-branch use was removed
payoff: ROADMAP.md reads in plain sentences that state each fact once, so the owner can decide what a release holds in one read.
not-delegable: A line edit is proven by an audit of each edited section against the text before it, which no grep can show, and the copy editor run itself calls a model.
---

**Problem.** Line edit ROADMAP.md section by section with the fixed copy editor once its restructure has landed

**Why it waits.** The project owner put structure ahead of every line edit (2026-11-07, over keeping restructures for later): no document is line edited before its structure read's findings are applied. `ROADMAP.md`'s restructure lands in nine slices, `PL-W0TS` to `PL-4BCF`. The repository's remaining copy edits wait until the copy editor no longer drops requirements, qualifiers and reasons (`PL-F0Q2`, project owner, 2026-11-07, ratified, over continuing with an audit of each document).

**How.** Run `python3 tools/copy_edit.py --sections ROADMAP.md`, as `docs/prose-review/README.md` § "Reviewing a whole document" step 3 says. Audit each edited section against the text before it for dropped statements, qualifiers, requirements and reasons, as `PL-95SW` did for `docs/MODEL.md`. Then close-out step 8 is satisfied for every slice's changed passages. The run planned on the owner's Mac on 2026-11-05 left out the frozen lists and § "Current baseline". Decide again whether to: a frozen list is a snapshot of what the gate held, and each release cut rewrites the baseline.

**Why it matters.** `ROADMAP.md` is the document the owner reads to decide what a release holds. The restructure moved its text without rewording it, so it still carries the dense, repeated and undefined wording that each slice listed below.

**Done when.** Each section of `ROADMAP.md` has been line edited and audited, and each statement the edit dropped is restored or recorded with its reason.

**Left for this line edit by slice 2 (`PL-P0C5`), 2026-11-07.** Each needs a
sentence reworded or a term chosen, which a move-only slice does not do. The
row numbers are `ROADMAP.md` at `aff76df1`; find each passage by its words.

1. Choose one word for the cadence's four stages and define it where the list
   starts. The list's own text says "beats", and other passages say "steps",
   while "step" also names the simulation step and the timeline's `Step`
   column.
2. Call the snapshot rule by its heading's name everywhere. It is also called
   "the presence rule", "the presence test", "the snapshot rule" and "the
   presumption".
3. In § "What counts", fold the `infra` example (`uv.lock` left stale is a
   defect, release tagging is not) into the process-work paragraph.
4. In § "Which findings re-enter the gate", cut the second "The gate tests when
   a problem was present, not when it was discovered", which repeats the
   section's opening, and reword the sentence after it to stand alone.
5. Date or cut "while Gate 2 does" in § "How gate work is released".
6. Cut the two "is why this rule is written down rather than left to imitation"
   sentences in § "Writing a milestone entry", keeping each id as a pointer.
7. Define, or replace with plain words, the terms the chapter read found
   undefined: "the store", "release train", "places" and "takes", "promoted",
   "grooming pass", "capture rule", "fails closed", the `verify:` field, and
   what `bin/docket` is.
8. Date each undated figure: "12 of 134 open items dead and 31 more
   overtaken", "thirteen items in one session generated fourteen new ones",
   and "Gate 2's 190".
9. Give an example of the wording that draws the exclusion warning. The phrases
   are `SCOPE_EXCLUSION_MARKERS` in `tools/doc_check.py`.
10. Name the release and the saving in "the saving the release exists to
    deliver".
11. Say what each subsection of a milestone entry holds (Goal, Required scope,
    Definition of done, Explicitly out of scope), in § "Writing a milestone
    entry".
12. Cut the narration about the text itself that the moves left behind.

**From `PL-DWGC` part 1 (2026-11-07).** Eight version-table rows keep a first
sentence that does not say what the release changed: v0.2.9, v0.3.4, v0.3.5
and v0.4.1 say only what did not change, and v0.3.8, v0.3.9, v0.4.4 ("**The
code is the model.**") and v0.4.5 ("**Going public, finished.**") are too
general to tell. Each needs a sentence on what changed for a learner, taken
from the rest of its row in the item the Details cell names. v0.4.4 comes
first: its row no longer shows that a displayed value moved in that release,
because the operator split was replaced by an exact step. Four rows also still
run past 600 characters as one sentence (v0.6.12 to v0.6.15).

**From `PL-DWGC` part 2 (2026-11-07).** These findings of slice 3's structure
read need a sentence reworded, so they wait for this line edit. Each quotes the
text to find.

- § "Project roadmap": say how a version, a release and a milestone relate,
  then keep the file's scope once ("This file covers releases only" repeats
  the first sentence's "version and milestone map").
- § "Versioning decision": say what a capability boundary is (the roadmap's
  own example is "a learner can run, branch, and compare a case"); state that
  a milestone takes its number only once every id in its Required scope is
  closed, which only the old version rows stated; put the pointer to § "The
  debt gate" at the first "Gate 0".
- § "Current baseline": "where the `docs/MODEL.md` rewrites it held are
  finished" and "Entry 12's six items ... close here" say one thing; name
  `PL-SP6H` once; put the two app file names in the table's `src/` cell and
  say the trajectories were not re-run, without the tool's name; say in words
  what the two stale statements got wrong, and what "inside the v0.6.15 tag's
  span" means for `#2031`; say what the blind judge was (`docs/prose-review/README.md`
  § "Judging edits blind").
- § "Release tags and release notes": the two counts of work inside a tag's
  span ("This is not rare", the 2026-09-14 count and the 2026-09-22 recount)
  can be one sentence with the rate; open "What a tag ships" with "The tag
  span is what shipped" (its "So" needs rewording first); "That was the
  decision rather than an omission" keeps the decision and loses the contrast;
  define "cut", "span", "stamp" and the two dispositions where each first
  appears.
- § "The plan": state once, under the timeline, that a patch track crosses no
  capability boundary, takes no version and freezes no gate, and let each row
  say only that it is a patch track; trim the Gate 1, Gate 2, v0.6.0 and
  interface-pass cells to what the step holds, its dates and its decision
  tags (their arguments sit inside sentences that also carry a tag or a
  date); open § "What MVP means here" with the date the MVP was reached and
  put its plan in the past tense; shorten "Each planning horizon is described
  to one level of detail, in one place" now that the order paragraphs have
  their own subheading; cut "Release v0.3.0 adds no capability" once the next
  sentence no longer needs it; keep break-out's display tier split as a short
  example pointing at row 7; give row 3 `PL-011`'s drop date and the two items
  that replaced it; and say in Gate 2's cell that its frozen list has gone
  where v0.6.0's section says, since "when the moment comes" is past.

**Added by slice 3's second review (2026-11-07).** § "What a tag ships that its
notes may not name" uses "the tag's span" without defining it. The definition,
the commits that `git describe --contains` resolves to a release tag, left with
the sentence now quoted in `PL-J3ZK`.


**Left for this line edit by slice 5 (`PL-YNFS`), 2026-11-07.** Each finding of chapter reads 35 to 41 below needs a sentence reworded, which a move-only slice does not do. `PL-YNFS` quotes the reads whole; find each passage in § "v0.7.0 - the schematic" by its words.

1. "A setting turns these into money" is Gas Man's model of agent cost, inside the paragraph on tension. Its "these" names the two totals of the sentence before it, so moving it needs the totals named.
2. The section heading leaves out agent cost. A rename changes the citations of § "v0.7.0 - the schematic" in `src/`, `tests/` and `docs/MODEL.md` with it.
3. The Goal table "was measured on this model", and the out-of-scope entry on containers drawn to scale cites "The measurement". Both are model runs, not measurements.
4. Gap 1's bold lead, "No surface says where the agent is", may repeat the Goal's opening claim. Keep one.
5. The Goal's "**The amounts exist and are not passed on.**" paragraph and Required scope entry 2 are written for a developer. The reader needs four points: the model tracks each compartment's amount, the interface received only the total, § "Designed for forking" waited for a feature that needed the amounts, and this milestone is that feature. The code names go to `PL-KFTM`.
6. The frozen list cites the deferral term (§ "Deferring to the next gate") in three places and states it in words in none. State it once in the first paragraph.
7. The `PL-P319`, `PL-SP6H` and `PL-0P3F` paragraphs in § "Captures after the cut" repeat their list entries. Each could keep only why it joined and the decision it carries. The `PL-P319` paragraph's "this gate waits on the project owner adding the paper" is stale, because `PL-P319` closed.
8. The Gate 4 paragraph retells Gate 2's deferral in three sentences. One sentence can keep the owner's earlier decision with its tag whole, and say that the question was not put to him again.
9. In § "Captures after the cut", "Both were split from the generator head `PL-58D7` when its design round chose ..." and "It is the generator head that `PL-R4Y2`'s defect review recorded ..." are history for those items. Each paragraph needs only what its items bound or guard.
10. Required scope entry 1 restates what entries 3, 4 and 8 build: the fill height, the share bar ("circuit included"), the units, and why arterial blood has no container. Give each one home and point to it from the other. Entry 1's `AGENT_AMOUNT_DISPLAY_PRECISION` and entry 3's file paths go to `PL-2881` and `PL-RNYV`.
11. Required scope entry 12 states its point last. Entries 9 and 10 rely on entry 11's reader-set price, which comes after them.
12. The definition of done names checks by their internal names: "an oracle independent of `core/`", `tools/contrast_check.py`, "`PL-HGZS`'s stress test" and `make check`. Say what each guarantees.
13. The out-of-scope entries on controls and on gauges make one point: showing or changing a setting in a second place waits for one design round. Merge them. The entries that point at Required scope entries 6, 8, 10 and 11 could state the short fact in place.

**Left for this line edit by slice 6 (`PL-B6V1`), 2026-11-08.** Each finding of chapter reads 27 to 34 below needs a sentence reworded, which a move-only slice does not do. `PL-B6V1` quotes the reads whole; find each passage in § "Completed: v0.6.0 - the layout is the reader's" by its words.

1. The section never says what v0.6.0 builds, and "This section describes what gets built" describes the text. Planned-milestone item 34's sentence naming what v0.6.0 builds (the tiled no-overlap invariant, the View contract, the registry, workspaces, persistence and the unconditional region) is the source for an opening line.
2. The heading's "the layout is the reader's" uses "reader" for the learner. A rename changes every citation of the heading with it.
3. The Goal is written in the present tense of 2026-09-16 and names code (`inert_splitter`, `simulation_view.py:296-309`); say the plain facts: the panes sat in locked dividers, and the readout section sat inside them. "The handles are inert by deliberate reservation" repeats the opening paragraph's reservation. "No user-writable state", "Nothing ... writes a file" and "the first user-written data" are one fact, and the load path's risk wants a sentence of its own.
4. In the frozen list, "which was the day v0.5.0 shipped" repeats the bold lead; the `tools/doc_check.py` sentence is history; and the tool names (`bin/docket gate`, `wave`, `check`, `tools/doc_check.py`) want what the reader can see instead. The `PL-NDKC` paragraph's "The item carries the milestone's feature but is not in `Required scope`" repeats the group paragraph above it; dropping it needs its "So" reworded. The `PL-5B1N` paragraph's "and the owner made that scheduling choice the other way" repeats its tag.
5. The deferral paragraphs cite beat 3's terms seven times and state them nowhere: state them once in the paragraph that opens the deferrals, with `PL-B396`'s classes and the rule that beat 3 asks a hazard record only of a `safety` or `science` entry. Fold `PL-WZVZ`'s inheritance into its list item.
6. In § "Captures after the cut", each bold lead restates the rule that admits a `safety` finding; each entry could keep its date and class. The 33 short entries could be one table: item, class, date, and what it means for the release, with the findings said as their effect rather than in code terms (`SimulationState`, `StepCount`, `dataclasses.replace`, "closed form", "slot"). Leads such as "what the review of `#1350` found" and "what `PL-WMCJ` found" are provenance for the items. "Entry 20 names it, so v0.6.0 itself clears it" is said three times. The head's field form and presence-test derivation are workflow detail.
7. Required scope: entry 6 restates entry 2's confinement of `QSplitter` and names `tools/import_boundary_check.py`; it could say that a check enforces entry 2's rule from the commit that creates the adapter. Entry 14's border drag restates entry 1's. Entry 20's paragraph on where the region sits restates entry 7, and its "Nothing decides where it goes" was true only before `PL-J8K2`. Entry 20's failure-states paragraph repeats that both depart from Blender. Entry 11's "reset" is defined at the end of its third paragraph and used in its first; Blender's `use_data = false, use_userdef = true` belongs in `docs/interface-provenance.md`. "Tier" means three things (the region's two halves, the three kinds of setting, and `docs/MODEL.md`'s accounting tier). The chooser paragraph of entry 20 lists no decision. In the pixel budget's compare-mode paragraph, "Compare mode accepts that shorter chart" now follows the minimum directly, since the 200 px figure went to `PL-F2YS`.
8. The definition of done names `QApplication`, `tools/import_boundary_check.py` and `make check`; say what each guarantees. The fixture files belong with the load-failure bullet. The ancestor test is a developer's detail. The accounting-tier bullet says one thing twice, and "two surfaces" should be the two Views. "The documents in Required scope entry 19" could name them.
9. The out-of-scope list could open its two groups with a lead-in line each: planned for later, and ruled out by the design (`docs/interface-provenance.md` § "Refused"). The `core/` entry's tool name belongs in Required scope entry 6. In the snap-merge entry, "The five-area pinwheel arrangement is out of scope for the same reason" now repeats the lead.

**Left for this line edit by slice 7 (`PL-M3MV`), 2026-11-08.** Each finding of chapter reads 45 to 48 below needs a sentence reworded, so slice 7 moved the text and left the wording. `PL-M3MV` quotes the reads whole.

1. Item 1 explains the design's limits in developer terms: the system matrix, "Metzler", and strategies constant across a step. Say what they decide: a machine changes only the breathing circuit's terms, the reference machine reproduces today's values exactly, and a behaviour outside the design's set, such as item 5, needs a milestone of its own. The developer terms belong in `docs/machine-abstraction.md`.
2. Item 24's table names tools and tests in its "What holds its value" column. Give the guarantee each value carries instead (cited and versioned; ISO 5360:2016 Table 2; 3:1 trace contrast and WCAG 2.2 AA text contrast; only a recorded judgment), and move the tool names to `PL-QBX0`. The colours row's first cell has grown into an essay: name the thing in it, and put the contrast targets in the third column.
3. Item 24's luminance cap and the 1.48 spacing are the derivation `app/theme.py` records. Keep three facts: colour cannot separate the six traces, the dash patterns separate them, and no check protects the patterns.
4. Item 29's naming-rule paragraphs ("What reads like the domain means concretely" to "What the sources changed") are for a developer. Keep one sentence for each rule with its item (`PL-H46J`, `PL-VZL0`, `PL-FZ6T`, `PL-3TLK`, `PL-212V`).
5. Item 30 states the sourcing standard four times and the refusal of a plausible but unexplained value twice. State each once, at the head of item 30's decisions, and let each paragraph keep only its own source.
6. Item 33's palette constraints name `tools/contrast_check.py`, `ast`, `REQUIREMENTS`, judgments 1 and 4 of `.claude/rules/ui-color.md` and `PL-BXB2`. Keep the three constraints in words: every declared colour pair meets WCAG 2.2 AA under four vision models, and the declared list is rewritten in the same change; the three ISO 5360:2016 agent colours are fixed; traces are told apart by dash pattern.
7. Item 33's prerequisites label ("Two hard prerequisites, and they are the reason this cannot simply be started") should name the two prerequisites, once `PL-NTHF` question 14 is answered.
8. Item 34's occlusion paragraphs repeat `docs/MODEL.md` § "Minimum displayed outputs": the three-part division and the tier detail. Keep the rule that nothing may cover a required value, that v0.6.0 builds the unconditional set outside the area system in the per-window shape, the second-window decision with its tag, and that the division is a stepping stone.
9. Item 34 names `PL-NWTM` and `PL-9LNF` only by id and calls them "pre-loaded" without saying what that means. Say what each failure is.
10. "Catalogue" names both this list of entries and item 36's catalogue of views. Use one word for each.
11. Item 34's 2026-09-17 count uses the effort sizes L, M and S without explaining them.
12. Item 40's first paragraph names `load_reference_circle_system_parameters()` and the unit suite. Keep that the circuit volume and fresh gas flow already sit in one cited data file with a first per-machine field, but nothing selects a profile yet, so a second profile is ignored.
13. The catalogue uses terms it does not explain: "Phase 1", "the timeline's Beyond row", "Gate 1", "Gate 4", "the MVP", "slot" and "strategy slot", "the closed set", "the score architecture", "touches", "the capture rule", "apparatus", "the guard", "literal and fact baselines" and "four check items". § "The debt gate" defines the gates; define or point to each of the others.
14. Items 37 and 42 name items 12, 13 and 15 by number alone. Give each its name at that mention.
15. "Item" names both a numbered catalogue entry ("item 34") and a queue item ("build item `PL-Y04W`", "Six queue items"). Keep the two apart. The spelling varies too: "anaesthesia" in item 35 against "anesthesia" in items 1 and 40.
16. Every catalogue entry that is intent says so in its own words (items 34, 38 and 39). The rule that an unscheduled entry is recorded as intent, not as a queue item, could be stated once in the introduction, with each entry keeping the word "intent" and item 39 its tag.

**Left for this line edit by slice 8 (`PL-V8SJ`), 2026-11-08.** Each finding of chapter reads 6 to 16 and 24 to 26 below needs a sentence reworded, so slice 8 moved the text and left the wording. `PL-V8SJ` quotes the reads whole.

1. v0.1.0 states its scope and done criteria twice (circuit preservation, mass balance, determinism); keep each in one list. Its tool list and the word "Flet" are for a developer.
2. v0.2.0: trim the remaining restated clauses and the code detail in its scope and out-of-scope entries.
3. v0.2.8's frozen-list entries have grown into essays and name developers' tools; cut each to its title and outcome, and move the story told across entries (`PL-S1P1`'s retelling) to the items. Rewrite its planning tense ("will", "keep only not this release's work") as a record.
4. v0.3.0 states the release's scope three times (Goal, definition of done, out-of-scope list) and names it two ways ("the teachable case's own scope", "the v0.4.0 milestone's Required scope"); it spells Gate 0 as "gate-0", calls one change "widened" and "tighten", and uses "gate" for a test bound. Its definition of done lists the tools `make check` runs.
5. v0.4.0's Goal restates that items 26 and 12 are not promoted; keep that in the out-of-scope list, which needs "neither" reworded in the Goal. Trim "Count entries, not ids" to the count.
6. v0.4.0's Gate 0 notes restate the presence rule, the `safety`/`science` re-entry and `PL-K79K`'s command, and "Cleared by v0.4.0 itself" restates that `PL-011` was dropped. Say each once and point to it. Its prose names internal tools (`bin/docket wave`, `docket check`); say what each guarantees.
7. v0.4.0's Required scope keeps scoping-day wording that reads as current ("Today `SimulationState.elapsed_s` accumulates", "Today that derivation ends in a private static method"); date it or put it in the past tense. The `PL-CC23` entry writes "s" where § belongs.
8. v0.4.26 says the same thing in several places: rendering inside the container (five), `PL-7J96` dropped (two), 0.26 MAC under two names (use "drawn departure"), no new capability so a patch (four), "whatever its size" (two), parity means "identical except for this list" (three), compare mode (two), the untouched-code boundary (three), the schematic (two), the item 34 reservation (four), what item 34 holds (two), and "built decomposed from the start" (three). Each copy sits inside a bullet whose other sentences stay, so each needs a sentence reworded. Its closing section's "A rewrite of 5 133 lines ..." keeps only its point (`PL-DWGC`).
9. v0.4.26's § "Fixes this port carries, and why that is not scope creep" answers an objection in its heading; nine items and v0.5.0's gate cite it by that text, so renaming it means updating them. Its section citations use several forms (§ "Sequenced past v0.5.0" for the full heading, "The gate is a snapshot" without §).
10. v0.5.0's Goal: the paragraph opening "Beneath those three gaps sits a fourth problem" now follows the change to `core/` and needs a new opener.
11. Gate 1's opening "Fifteen items were untriaged" paragraph can be one sentence; "clears before implementation begins" is said five times, and the admission paragraph is repeated in every dated group. One rule has five names ("the second of the two unconditional exceptions", "the unconditional safety/science exception", "the safety test" and others); state it once and use one name.
12. Gate 1: "a value must be marked as modelled" is argued in five places and the paused-tooltip point in three; `PL-4KZD` is said three times; presence answers are given for entries the exception admits whatever the answer. Keep each once.
13. Gate 1's entries have grown into essays (`PL-GS3R`, `PL-ZX12`, `PL-C4PH`, `PL-LHBY`, `PL-S6WW`, `PL-JVHL`, `PL-0RZ0`, `PL-3K9B`, `PL-4KZD`, `PL-N3N5`) and name code; cut each to a line and move the measurements and code names to the items. Its prose names tool workings (`tools/doc_check.py` counts, `docket.toml`, `workflow_paths`, `PL-VRMK`'s tiering).
14. Gate 1: "The two statements do not conflict ... Silence is the third option" (at `PL-YVHK`) and the rule paragraph after the 2026-09-17 list are rules for the whole gate; they belong in § "The gate is a snapshot, not a moving target", reworded to stand without the entry. The "not live" paragraph belongs before its list. Dates are given in both the group headings and the entries.
15. v0.5.0's Required scope: the channel-reversal paragraph under `PL-8PSW` is history (`PL-HLD5`, `PL-GVXP`), but the cap paragraph after it opens "That leaves no channel free", so moving it needs the next paragraph reworded; the contrast reasoning belongs in `docs/MODEL.md` § "The six compartment traces". Branch-equals-parent is stated four times; the agent rule twice; `PL-1XPX` and `PL-MN4J` both say they are owner decisions, and `PL-MN4J` keeps two rules for sessions. Several entries use "First ... Second"; give each pair a short list. Positional pointers ("two bullets down", "the entry below") should name the entry. Bold openings that do not say what their paragraph holds: see chapter read 24's table. Method names (`resumed_at_halt`, `fork_at_halt`) are for a developer.
16. v0.5.0's definition of done points to beat 3 of § "The cadence" for a deferral's terms; state them and keep the pointer. Say in words what `docket check` and `tools/doc_check.py` cover.
17. v0.5.0's out-of-scope list describes `PL-ZW0J` twice (add "after a confirmation" to the first); its first bullet should run exclusion, the five deferred items, Gate 2, the reason, then the four kept; the deferral date belongs in `PL-ZW0J`; code names (`has_recorded_run`, `BranchedCase.branches`) should be described in words.

**Checked 2026-11-09:** `bin/docket feature roadmap-structure` shows all nine restructure slices (`PL-W0TS` to `PL-4BCF`) done, and `PL-F0Q2`, the copy editor's fix, is done. Nothing this item waits on is open. The feature's small contradiction items (`PL-1BVB`, `PL-9857`, `PL-T5R7` and the rest) each change a few sentences. They can land in any order with this edit, but landing them first spares the edit a sentence that is about to change.

**Left for this line edit by `PL-NTHF`, 2026-11-10.** The copy editor queried these passages in text that `PL-NTHF` did not write, and the documents do not answer them. Find each by its words.

1. Item 24's "`app/theme.py` records the search" names no search: say what was searched for.
2. Item 30's "The same argument already places item 29 ahead of that work" follows two arguments (the risk of stalling behind the generalization, and the surface built N times); say which.
3. Item 34's "gives the count, the method, the construction" does not say what was counted.
4. Item 34's "isolation with teeth" does not say what is kept apart (each view from the others, or each view from the rest of the screen) or what enforces it.
5. Item 39's "the condition that the unit names" and "where an amount leaves the unit" name no unit.
6. Item 39's "Correcting the water half alone is what that note explicitly warns against" follows "Both notes"; name the note.
7. Item 43's "the baselines of the four check items" does not say which four items or what a baseline is.

**Left for this line edit by `PL-VM1Q`, 2026-11-10.** `PL-VM1Q` corrected the completed-release records' false and stale statements, and left these wording calls. Its brief has the answer behind each, under the question number given.

1. Define, point to or replace the terms that the completed-release sections use without defining: "beat", "cadence", "parse floor", "grandfathered", "captures" and "groom" in v0.2.8 (question 6); "the presumption", "the refilling-queue problem", "the cut", "score architecture", "keyframe" and "bucket cache" in v0.4.0 (14); the v0.4.26 terms of question 23; Gate 1's terms of question 35; and the Required-scope terms of question 38.
2. Point v0.2.0's out-of-scope vaporizer bullet to planned-milestone item 1 and `PL-439V` (question 2).
3. Remove the four hand-written "Closed ... (pull request N)" notes in v0.2.8's list (question 3).
4. Give Gate 1's opening a pointer to § "Which findings re-enter the gate" (question 26).
5. Put Gate 1's `PL-S6WW` paragraph in the past tense: #669 corrected the sentence it calls false (question 34).
6. Decide whether `PL-Y5WR` belongs to v0.5.0's score-architecture group rather than its boundaries group, and recount the groups' sizes (question 37).
7. Name the queue's own check and the documentation check in words in v0.5.0's definition of done (question 39).
8. Move the owner's 2026-09-21 quotation and the "nine open items" count from v0.5.0's out-of-scope list to `PL-4B1G` (question 40).
9. Answer the copy editor's queries on text that `PL-VM1Q` did not write: what changed in v0.3.0's "Provenance and parallelism patch" row and in v0.3.1's row; which reading "held to the data files they restate rather than only its provenance table" means; the tense of the sentence in v0.4.0's note on `PL-K79K` that says it "advertised a command that does not exist"; what "three entries later" counts for `PL-NV9W`; what `RunHistory`, "the sampler", "the M4 decimation path" and `has_recorded_run` are, in words; which item of `PL-B8MK` and `PL-TYWQ` "This item" means, and whether "Both closed the same day" means the same day as each other; and what "this" refers to in "§ "The cadence" already arranges this".

**Generator check.** One-off: the line edit the owner asked to follow each restructure. No mechanism produces it.

**Dropped 2026-11-11** (project owner, 2026-11-11 05:17 UTC, ratified, over
keeping it as a copy editor run on request). The owner said on 2026-11-11 at
05:13 UTC that the copy editor function is being removed (`PL-J1ZM`, #2119).
That removal keeps the copy editor only for a section rewrite the owner asks
for. This line edit was a copy editor run, and the removal's own measurement
found that the copy editor left seven `ROADMAP.md` passages slightly longer on
#2101, at up to 32 minutes and $7.74 per run. The twelve wording points listed
above from slice 2, and the points from `PL-DWGC`, are not done. A later item
that rewords `ROADMAP.md` can take them from here.
