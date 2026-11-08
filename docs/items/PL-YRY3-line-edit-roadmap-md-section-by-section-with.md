---
id: PL-YRY3
title: Line edit ROADMAP.md section by section with the fixed copy editor once its restructure has landed
status: untriaged
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
---

**Problem.** Line edit ROADMAP.md section by section with the fixed copy editor once its restructure has landed

**Why it waits.** The project owner put structure ahead of every line edit (2026-11-07, over keeping restructures for later): no document is line edited before its structure read's findings are applied. `ROADMAP.md`'s restructure lands in nine slices, `PL-W0TS` to `PL-4BCF`. The repository's remaining copy edits wait until the copy editor no longer drops requirements, qualifiers and reasons (`PL-F0Q2`, project owner, 2026-11-07, ratified, over continuing with an audit of each document).

**How.** Run `python3 tools/copy_edit.py --sections ROADMAP.md`, as `docs/prose-review/README.md` § "Reviewing a whole document" step 3 says. Audit each edited section against the text before it for dropped statements, qualifiers, requirements and reasons, as `PL-95SW` did for `docs/MODEL.md`. Then close-out step 8 is satisfied for every slice's changed passages. The run planned on the owner's Mac on 2026-11-05 left out the frozen lists and § "Current baseline". Decide again whether to: a frozen list is a snapshot of what the gate held, and each release cut rewrites the baseline.

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
