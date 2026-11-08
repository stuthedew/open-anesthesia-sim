---
id: PL-YNFS
title: Restructure ROADMAP.md, slice 5: restructure the v0.7.0 section, gather its captures after the cut in one section, and put the owner's test drive in its definition of done
priority: P2
effort: M
status: done
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md, docs/items/PL-11Z9-the-agent-cost-view-does-not-say-on-its-face.md, docs/items/PL-5B1N-simulated-traces-should-be-solid-and-a-dotted.md, docs/items/PL-71H3-answer-the-questions-the-structure-read-of.md, docs/items/PL-HDRN-bin-docket-arm-does-not-hold-a-simulator-pull.md, docs/items/PL-HGZS-the-copy-editor-passes-over-explained-text-and.md, docs/items/PL-J5GC-the-run-screen-s-widgets-each-have-one-writer.md, docs/items/PL-L6QR-re-run-the-area-model-queue-audit-when-roadmap.md, docs/items/PL-LF0P-scope-v0-7-0-the-schematic-in-roadmap-md-and.md, docs/items/PL-YRLM-decide-which-release-builds-planned-milestone.md, docs/items/PL-YRY3-line-edit-roadmap-md-section-by-section-with.md, docs/items/PL-B6V1-restructure-roadmap-md-slice-6-give-each-v0-6-0.md
blocked-by: PL-G6DP
added: 2026-11-07
closed: 2026-11-08
pr: 2065
payoff: a reader of v0.7.0's section finds what the release holds and every capture admitted after the cut in one place, and its definition of done says v0.7.0 is cut only after the owner has test-driven main
verify: grep -qF '### Captures after the cut' ROADMAP.md
---

**Problem.** Restructure ROADMAP.md, slice 5: restructure the v0.7.0 section, gather its captures after the cut in one section, and put the owner's test drive in its definition of done

**Source.** The copy editor's structure read of `ROADMAP.md`, run on the project owner's Mac on 2026-11-06: one read per chapter, then one read of all the chapters' outlines together. Row numbers are `ROADMAP.md` at `aff76df1`, the last commit to change it before slice 1 (`PL-W0TS`), so a later slice finds each passage by the words the finding quotes. The project owner chose to file the findings as items and apply them one slice per pull request (project owner, 2026-11-07, ratified, over one pull request for the whole restructure), because the release tools read the roadmap's gate sections and a small move is easier to check against them. The raw reads are in the project's shared folder, `/mnt/project-files/v0.7.0/repo-copy-edit/mac-structure-reads/ROADMAP-md/structure/`.

**Why it matters.** v0.7.0 is the release being built, and the project owner test-drives `main` before it is cut. Its section is what a reader opens to see what the release still needs. The condition that v0.7.0 is cut only after that test drive is stated in § "Current baseline" and the version rows, but not in v0.7.0's definition of done. Admissions after the cut are split between § "Deferred from this gate" and the frozen-list section.

**The findings, as the outline read gave them** (numbered by their order in the read: 7, 53).

- Heading and split record (6299-6413, 7173-7196): in v0.6.0 and in v0.7.0, the heading "Deferred from this gate" sits over a section that mostly records `safety` and `science` captures admitted to the list, because the deferrals themselves are now recorded on the items. Each milestone also records other admissions after the cut in its frozen-list section (5718-5805 and 6012-6034 in v0.6.0; 6991-7065 in v0.7.0). Record all of a milestone's admissions after the cut in one section, under a heading such as "Captures after the cut", and update citations such as 7046-7057.
- Missing from v0.7.0's Definition of done: 279-286 and version rows 159-160 say "v0.7.0 is cut only after the project owner has test-driven main", but v0.7.0's Definition of done (7321-7362) does not say so. The condition belongs there, and the baseline keeps the status.

**Care in this slice.** v0.7.0's frozen list and Required scope are what `bin/docket wave` and `bin/docket gate` read for the current release. No list entry leaves its list, and each entry keeps its id where the walker reads it. Finding 7 covers v0.6.0 and v0.7.0. This slice applies its v0.7.0 half, and slice 6 (`PL-B6V1`) applies the v0.6.0 half.

**The findings inside each chapter, as the chapter reads gave them.** Each chapter read also ended with an outline of one line per paragraph, which is left out here and kept in the shared folder. Each read is quoted whole, as a block, so that its quotations of the roadmap are not taken for this item's own claims.

**Chapter read 35: § "v0.7.0 - the schematic", rows 6879-6920.**

```text
- Rows 6881–6894: the first paragraph makes four points. It says what the release holds, gives decision history, states two decisions as "First, … Second, …" (pattern 5 in the writing rule) plus a third about Views and Areas, and says how the remaining choices were made. Split it in this order:
  1. What v0.7.0 holds: the compartment schematic (item 27) and the agent cost readout (item 28), each a View that any Area can hold.
  2. A numbered list of the decisions, each keeping its tag whole.
  3. The sentence saying that look, wording and placement are placeholders, and that the remaining choices were not put to the project owner.
- Rows 6882 and 6890–6893: "`PL-LF0P` scoped it on 2026-10-25", "The project owner confirmed this in the same round" and "because each remaining choice either had one clearly better option or concerned look, wording or placement" are decision history. That history belongs in `PL-LF0P`. The roadmap keeps a pointer to `PL-LF0P`, and it keeps which choices the owner made and which were made without the owner.
- Rows 6896–6907 and 6909–6920: these two paragraphs explain why the decision's two rejected options fail ("over containers drawn to scale and over Gas Man's Picture as it is", rows 6885–6886). Neither paragraph says so. Put them directly after that decision, and open each by naming the option it rules out.
- Row 6896: the bold phrase "What Gas Man's Picture shows, read at the source" describes the text rather than stating the point. The point comes last, at rows 6905–6907. Open with it, for example "**Gas Man's Picture shows where the tension is, not where the agent is.**", and follow it with the readings of the source.
- Row 6907: "Item 27 now says so" is history about an edit to the planned-milestone list. It belongs in `PL-LF0P`. The roadmap keeps nothing here.
- Row 6901: "A setting turns these into money" is Gas Man's model for agent cost (item 28), but it sits in a paragraph about tension. It belongs in a paragraph about the agent cost readout, and the section has no such paragraph (see the queries).
- Row 6909: in the bold phrase "Drawing each container to scale does not rescue it in this model", "it" points at no noun. State the point, for example "**Containers drawn to scale would leave four compartments 1 to 7 px wide.**"
- Rows 6911–6914: the Mapleson sentences repeat the relation that row 6910 already states ("holds an amount equal to its filled area"). A reader deciding what to build decides the same way without them. They could move to `PL-LF0P` together with their reading record ("read from the private reference corpus, equations 5 and 6"). If they stay, they stay whole.
- Rows 6919–6920: "The measurement used `AgentUptakeSystem.for_agent` on the shipped parameter files" names a tool this reader does not know. It also calls a model run a measurement. The method belongs in `PL-LF0P`. Keep the date beside the figures in rows 6916–6918, for example "(simulated from the shipped parameter files, 2026-10-25)".
- Row 6879: the heading "v0.7.0 - the schematic" leaves out agent cost, which this milestone also builds (rows 6881–6882 and 6887–6888). A heading that fits is "v0.7.0 - the schematic and agent cost". Renaming it means changing every citation of the old heading at the same time, so the owner should decide.
- Section length: three paragraphs need no subheadings once the first paragraph is split.
- Query: rows 6890–6893 say the rest of the section was decided in the scoping round, but the rest is the two reason paragraphs. They state no further choice, so the reader cannot tell which parts of v0.7.0 those choices cover.
- Query: the reader needs what the agent cost readout shows and what item 28's "four entries" are (row 6888). The section gives neither.
- Query: the reader needs to know whether v0.7.0's schematic lets the learner change the simulation's state. Appendix E says Gas Man's Picture is for "viewing and manipulating the state" (rows 6902–6903), and the section does not say.
- Query: the View decision has no tag in the form the other two use, only "confirmed this in the same round" (row 6890). The reader cannot tell whether it was ratified.
- Query: the Gas Man Workbook is cited only by printed page. It has no edition, year or record of how it was read (route, date), unlike the Mapleson citation (rows 6912–6914).
- Query: "View", "Area" and "Gate 4" are this repository's names, and this section does not explain them. The outline read should check whether another chapter of `ROADMAP.md` does.
```

**Chapter read 36: § "Goal", rows 6922-6969.**

```text
- **The goal comes last under a heading that promises it.** The section is headed "Goal", but the end state (6960-6969) comes only after 36 rows about the problem. A reader deciding what a release holds looks for the goal first. Move the end-state paragraph to sit right under the heading, and put the evidence and the gaps after it as the reason. Keep the heading text, because other files cite sections by their headings.
- **The end-state paragraph makes two points (6960-6969).** One is the compartment schematic (6960-6966). The other is the agent cost View (6966-6969). Split them into two paragraphs or two list items. Each could name the gap it closes: the schematic closes gaps 1 and 3, and the cost View closes gap 4.
- **The same fact appears in two gaps (6940-6942 and 6955-6956).** Gap 1 says "The only amounts on screen are the agent accounting View's delivered, exhausted and stored totals, in litres of vapour. That View is a check that the model conserves mass." Gap 4 says "The delivered total appears only in litres of vapour, inside the mass-conservation check." The fact belongs in gap 1. Gap 4 keeps only its own point: clinicians buy agent as liquid, and the low-flow lesson is about money. The two passages also give one View two names, "agent accounting View" and "the mass-conservation check". Use the first throughout.
- **The opening and gap 1 make the same point (6924 and 6940).** The opening says "The interface draws tension and almost nothing else", and gap 1's bold phrase says "No surface says where the agent is". Keep the general claim in the opening. Gap 1 keeps only the detail: the agent accounting View's totals are the only amounts on screen, and the owner judged that View not useful to learners.
- **Gap 2 is not like the other gaps (6945-6950).** The other three are things the learner cannot see. Gap 2 is a precondition for building the feature, and it is written for a developer. The reader does not know its code names (`core/`, `agent_amount_l`, `SimulationSnapshot`, `src/anesthesia_sim/app/controller.py`, `stored_agent_l`). The reader needs only this:
  - the model already tracks each compartment's amount;
  - the interface receives only the total;
  - § "Designed for forking" chose to wait until a feature needed the amounts;
  - this milestone is that feature.

  Put that after the list as its own short paragraph, and change "four gaps" to "three". The code names go to the item that builds the change, or to the milestone's design section if there is one. See the query below.
- **The paragraph at 6935-6938 makes three points.** "Fat's trace sits within a few pixels of zero" is what the learner sees, so it belongs with the table paragraph. The sentence about `PL-H5DV` names where the table's pattern was checked for all three agents, so it belongs beside the table. "As things stand on 2026-10-25, there are four gaps" stays as the lead-in to the list.
- Query: the reader needs to know when the table's values were produced, or for which version of the shipped defaults. The defaults change, and no date stands beside the figures. The only date, 2026-10-25, introduces the gaps.
- Query: the reader needs the hours that fat takes to overtake muscle. Row 6936 says `PL-H5DV` worked them out for all three agents, but the chapter gives no figure. That figure is the strongest argument for the milestone.
- Query: the table gives "share of stored agent" (6930), while the end state's bar gives "share of all the agent the run holds" (6964-6965). Do the two shares have the same denominator? In particular, does "stored" include the circuit, the alveoli and the blood, which the bar covers?
- Query: "View" and "Area" (6941, 6951, 6961, 6966) are this repository's own terms, and this chapter never explains them. The read across chapters should check whether an earlier chapter defines them.
- Query: the chapter does not name the item that will carry the code-level detail moved out of gap 2.
```

**Chapter read 37: § "Debt gate: the frozen list", rows 6971-7171.**

```text
- **The section opens with the wrong paragraph.** Rows 6997-7004 ("Two groups, and only the second must clear before this milestone's implementation begins") tell this reader what the list means for the release. They should open the section, ahead of the freeze details in rows 6973-6989. Their last two sentences are a rule for writers: "This section does not name the lane each entry is worked in. `bin/docket gate` and `bin/docket picks` print the lane, because a lane written here goes stale (`PL-Z64T`)." That rule belongs in `PL-Z64T`, so cut it here.
- **The owner's one action is buried.** "this gate waits on the project owner adding the paper to the reference corpus" (rows 7043-7044) is the one thing holding the gate that the owner can act on. Move it to the opening paragraph. The `PL-P319` paragraph keeps why the gate waits.
- **Rows 6973-6989 make five points and need splitting.**
  - Keep the freeze date, the cut (`origin/main` at `0947408`, plus this milestone's own items) and the debt classes. Move "That means every item classed `defect`, `safety` ..." (rows 6977-6979) to follow "Every open item that counts as debt" (rows 6975-6976). Today "That" points at the cut, not at the debt.
  - Cut "v0.6.0 shipped on 2026-10-20. § "The debt gate" -> "The cadence" names two days, and the later of them is the scoping day." It explains how the date was worked out, which the reader can do without.
  - Cut rows 6981-6986, "One item was untriaged at the cut ... So it is not on this list." This is the history of an item that is not on the list, and it belongs in `PL-HDRN`.
  - "This section does not record how many entries are closed, because ..." describes the text itself. Keep only that a tool reports how many entries are closed, said in words. The reason belongs with the writers' rule.
  - The `PL-5B1N` sentences in rows 6979-6981 go to the next finding.
- **`PL-5B1N` comes up in three places.** They are rows 6979-6981 (carried over though not debt, `PL-JV5Q`), rows 6991-6995 ("`PL-5B1N` closed with its build") and rows 7031-7035 (what it is, deferred to Gate 3, "ready again"). Make one paragraph that gives what the item is, why it is on the list, that it closed, and that its open question went to `PL-4LS8`. Today rows 6991-6995 use "a preview curve" and "`PL-5B1N`'s build" before rows 7031-7032 say what `PL-5B1N` is, so the reader has to read ahead.
- **The rule for deferring an entry is given in four places, and only one says what it is.** Rows 7000-7002 point at "§ "The cadence" beat 3" and say the `deferred-from:` field records the deferral. Row 7015 points at beat 3 again. Rows 7024-7025 say "Each item's `deferred-from: v0.7.0` says so". Only rows 7041-7042 state a term: "Deferring it instead would need its hazard to be not live". State the term once, in words, in the opening paragraph. Rows 7015-7024 and 7041-7043 then keep only whether each entry meets it. Cut the sentence in rows 7024-7025.
- **Items that joined after the freeze are scattered, and the rule that let them in is repeated.** They sit in rows 6991, 7037, 7046, 7052 and 7059, mixed in with the freeze, the groups and the deferrals. Gather them under one subheading such as "Joined after the freeze", in date order: `PL-P319` (2026-10-26); `PL-4LS8` and the six items from `PL-R4Y2`'s triage (2026-10-31); `PL-SP6H` and `PL-0P3F` (2026-11-04). Items got in by two routes, and each route's rule now appears more than once:
  - The unfinished part of an item that was on the list at the freeze stays on the list. This is in rows 6993-6994 and row 7043.
  - § "Deferred from this gate" admits a `safety` or `science` item rather than deferring it. This is in rows 7048-7049, 7055-7056 and 7064-7065.

  State each rule once at the head of the subsection. Each entry then gives only its date, class and the hazard that is still possible.
- **Paragraphs repeat the list entries.** Rows 7060-7064 repeat row 7171 (the 0.1 L step, 1 MAC with the reference flows, dial maximum and 10 L/min, about an eighth of an SD). Rows 7053-7055 repeat row 7170, rows 7038-7041 repeat row 7151, and rows 6992-6993 repeat row 7092. Leave the detail in the list entry. Each paragraph keeps why the entry joined and any decision, such as "whole millilitres, which the project owner chose on 2026-11-04".
- **The staleness sweep is in the wrong place.** Rows 7067-7074 check the list as frozen on 2026-10-25. Put them straight after the freeze paragraph, before the changes made since. Cut "The reason is that a `verify:` command tests for the fix and never for the fault". It is a maintainer's reason in a tool's internal name, and it belongs in § "The cadence" or `PL-F2NX`.
- **The item 28 paragraph (rows 7006-7013) carries history and could sit closer to its list.** Cut "`PL-YRLM` held the question of when to schedule item 28, and it closed with that answer". It is decision history and belongs in `PL-YRLM`. Put the paragraph next to the opening paragraph's first group, or straight above the first list.
- **The Gate 4 paragraph (rows 7015-7029) retells Gate 2.** Rows 7025-7029 retell how Gate 2 handled `PL-WZVZ`. Keep in one sentence that the deferral follows the owner's earlier decision, which the owner needs to know. Keep the tag "(`PL-DB64`, project owner, 2026-09-27, ratified, over keeping it on the list to hold the gate open)" whole beside that decision. Also say that the deferral was not put to the owner again. Separately, the list does not mark these two entries as deferred (rows 7093 and 7105), so a reader counting what must clear counts 82 rather than 80. Mark them in the list, or list them separately.
- **The section needs subheadings.** At 5,601 words, it is mostly an 82-entry list in an order the reader cannot use. Entries run by size, then in batches added later: `PL-4LS8` (S) sits among the M entries, `PL-0P3F` (M) comes last, and `PL-P319` follows `PL-GCGX`. Suggested subheadings:
  - For the prose: what must clear and what is deferred; how the list was frozen and checked; joined after the freeze.
  - In place of the bold lines in rows 7076 and 7088: one subheading for each list.
  - Inside the 82 entries: groups by what they change. Examples: the model and its specification (`PL-MLPT`, `PL-PM67`, `PL-GCGX`, `PL-P319`, `PL-YDRT`, `PL-PTDZ`, `PL-D1LR`, `PL-SP6H`, `PL-0P3F`); branches, marks and halts (`PL-HSP8`, `PL-K5BS`, `PL-TNYP`, `PL-NRR6`, `PL-QBQX`, `PL-XV0D`, `PL-VHQX`, `PL-3B34`); window layout (`PL-97WX`, `PL-QZ7Z`, `PL-C9XP`, `PL-Y65Q`); build and workflow tools (`PL-H57W`, `PL-QQGZ`, `PL-SC0N`, `PL-WJJ8`, `PL-44R1`, `PL-5PL5`, `PL-9K28`, `PL-GH8L`, `PL-GKX6`, `PL-LL9F`, `PL-W5JR`, `PL-YF16`, `PL-VWXL`, `PL-FPLQ`). Grouping by class is the other option, since the section defines debt by class.
- **One list heading disagrees with the opening paragraph.** "Cleared before v0.7.0 begins unless deferred - 82 entries" (row 7088) says "v0.7.0 begins", but rows 6997-6998 say "before this milestone's implementation begins". Use "Cleared before v0.7.0's implementation begins, unless deferred - 82 entries".
- **The section relies on sections that come after it.** It depends on § "The debt gate", its part "The cadence" (beat 3), § "Deferred from this gate", § "Debt inside the milestone's own scope" and "the Required scope below" (rows 6975-6976, 7009). By its own wording, § "The debt gate" and the Required scope come later. Put those sections before this list, so the reader meets "debt", "deferred" and "first group" after they are defined.
- **Queries:**
  - The text contradicts itself on `PL-5B1N`. Rows 7033-7035 say "That blocker cleared when this section was written. So the item is `ready` again, and it is worked with the rest of the second group." Row 6993 says "`PL-5B1N` closed with its build". Which is current?
  - The size of the sweep does not match the list. Row 7070 says "Each of the 24 entries open at the time was checked". The list held 81 entries open at the freeze on the same day (91 now, less the 10 that joined later). How do 24 and 81 relate?
  - The text contradicts itself on the lower edge of the band for the 0.1 L step. Row 7063 says "at the fine end of the band the section allows". Row 7171 says "at or past the seventh the section allows". Row 7170 says the band runs "between a quarter of an SD and six SDs". Is the fine end a quarter or a seventh of an SD? And which section is "the section"? None of the three names it.
  - The reader needs to know which gate is this milestone's. The text names gates by number (Gate 2, Gate 3 in row 7032, Gate 4 in row 7015) and by release ("v0.6.0's gate", "this gate"), and never says which number goes with which release.
  - The reader needs to know what planned-milestone item 28 is (rows 7006-7011), and the text does not say.
  - The reader needs to know what (L), (M) and (S) on each entry mean, and the text does not say.
  - The reader needs each entry's class (`defect`, `safety`, `science`, `refactor`, `perf`), because the section defines debt by class and admits later items by class. The list does not give it.
  - The text does not explain "capture" (rows 7046, 7049, 7027).
  - The reader deciding scope may need to know which three entries need less work than their briefs say, and which three wait on more or less than their records say (rows 7071-7073). The text sends them to each brief.
  - Do the list entries have to repeat their items' titles word for word? Rows 6988-6989 say a tool compares the list with `docs/items/`. If they do, the internal names this reader does not know (`make check`, `bin/docket check --verify`, `mypy`, `plan.promotable`) have to be fixed in the items. If not, the entries need the same edit as the prose.
  - Two list entries contradict each other. Row 7135 calls the control record "the one holder of a case instant PL-CN5S left untyped". Row 7123 calls the chart time base "a holder of a case instant PL-CN5S left untyped, beside PL-RCYZ's control record".
  - Where does the reader find what this gate deferred? Rows 7049-7050 name `PL-9Z74` and `PL-93LV` as deferred. I cannot see whether § "Deferred from this gate" lists them, or lists `PL-WZVZ` and `PL-B4P7`.
```

**Chapter read 38: § "Deferred from this gate", rows 7173-7196.**

```text
- One fact is given twice. Lines 7175-7176 say a capture is not deferred when "it is classed `safety` or `science`", and lines 7195-7196 say "It was first given `deferred-from:`, which a `safety` item cannot take". The rule belongs in the first paragraph. Lines 7195-7196 should keep nothing, because the wrong tag and its correction are history for item `PL-J5GC`.
- The first paragraph (7175-7182) serves two readers. Lines 7175-7178 give the owner the rule for what gets deferred. Lines 7178-7182 are for the people and sessions who keep the list: the field format `deferred-from: v0.7.0 - <why>`, "The triage pass that classes the item writes that field", "`bin/docket check` fails on any open debt item that this section neither places nor defers" and the `bin/docket wave` listing. Move those to items `PL-D388` and `PL-WD5Z`, or to the workflow file that describes the triage pass. Leave the owner two facts: every open debt item is either on this gate's list or deferred, and one command shows the deferrals with the state of each (`bin/docket wave`).
- Lines 7185-7186 are decision history: "Both were split from the generator head `PL-58D7` when its design round chose to give each core input a declared numerical envelope". This belongs in item `PL-58D7`. The paragraph keeps what each item bounds.
- Lines 7191-7193 are decision history: "It is the generator head that `PL-R4Y2`'s defect review recorded on 2026-10-25". This belongs in items `PL-J5GC` and `PL-R4Y2`. The paragraph keeps the guard and the three entries it covers (`PL-6RJ0`, `PL-3B34`, `PL-HF4B`).
- Lines 7184-7196 make one point in two paragraphs: an item captured after the cut joined the list because it is classed `safety`. These paragraphs record items that are on the gate's list, and the owner looks for those in the list itself. Move them to that list as one entry per item, saying what it adds to the release:
  - `PL-QX2G`: bounds on volumes and partition coefficients.
  - `PL-YT3T`: a bound on a compartment's own step.
  - `PL-J5GC`: values shown together on the run screen come from one state.

  Only the deferred items, `PL-58D7`, `PL-06LS` and `PL-XST1`, with the reason ("not `safety`"), stay in this section.
- The heading "Deferred from this gate" (7173) does not cover lines 7184-7196, which record items that came onto the list. Once those rows move, the heading fits. If they stay, the heading needs to name both outcomes, and every file that cites § "Deferred from this gate" must change with it.
- Query: lines 7177-7178 allow "the entry is deferred with it" with no exception for a `safety` entry. Lines 7195-7196 say a `safety` item "cannot take" `deferred-from:`. Can a `safety` entry be deferred along with a capture it depends on? Only the author knows which statement is right.
- Query: the reader needs to know which gate this is and which gate is next. The chapter gives "v0.7.0" only inside the field format (7179), and never names the next gate.
- Query: the reader needs to know when "the cut" (7175, 7184, 7191) took place, and this chapter does not say.
- Query: the reader needs to know what the dates in "(`safety`, 2026-10-25)" (7184) and "(`safety`, 2026-10-26)" (7191) record. They could mean classed, captured or let onto the list. The text does not say.
- Query: the chapter does not explain several of the repository's own terms that stay in the owner's text: "debt item", "capture" used as a noun, "classed", "generator head" and its "members", "guard", and "one state". It also does not say what "re-entered" means for an item that was captured after the cut and was never on the list.
```

**Chapter read 39: § "Required scope", rows 7198-7319.**

```text
- **The share bar is described twice.** Rows 7211-7213 say "each compartment's amount as a share of all the agent the run holds, circuit included". Rows 7256-7257 say "Each segment is as long as that compartment's share of all the agent the run holds". The description belongs in item 4, and "circuit included" should go there with it. Item 1 keeps only that the subsection says what the share bar shows (item 4). This also stops item 1 naming the share bar before item 4 introduces it.
- **The meaning of a fill height is given twice.** Rows 7203-7204 say "A fill height is the compartment's modelled tension, on the same scale for every container of one run". Row 7247 says "Each container fills to its tension". It belongs in item 3, which should also take "on the same scale for every container of one run". Item 1 keeps only that the subsection says what a fill height and an amount mean.
- **The agent cost View's unit is given twice.** Rows 7208-7209 say "The agent cost View gives millilitres of liquid equivalent." Rows 7285-7287 say "By default it shows the delivered agent in millilitres of liquid equivalent … Either way, the unit is named on the value." It belongs in item 8. Item 1 keeps the rule for the whole interface, with its reason. The schematic labels amounts in millilitres of vapour, and no amount shows a bare "mL", because about 183 mL of sevoflurane vapour come from 1 mL of liquid. This also stops item 1 naming the agent cost View before item 8 introduces it.
- **Two items add displayed precisions to the same section.** In rows 7213-7214, item 1 "derives the displayed precision of a per-compartment amount in § "Displayed precision"". In rows 7279-7281, item 7 says "§ "Displayed precision" derives a precision for each quantity and each unit". Query: the reader needs to know whether item 7 (`PL-0S0V`) covers the per-compartment amount that item 1 (`PL-2881`) derives, and the text does not say. If it does, give the derivation to one item and point to it from the other. If it does not, item 7 should say that the per-compartment amount is item 1's work.
- **The arterial blood reason is in the wrong item.** The reason no container is drawn for arterial blood (rows 7221-7224) belongs in item 3, beside the list of containers (rows 7243-7246). That is where a reader asks why arterial blood is missing. Item 1 keeps only that the subsection records the reason.
- **Item 2 is written for a developer.** Item 2 (rows 7227-7238) is full of code names: `SimulationSnapshot`, `agent_amount_l`, `core/`, `stored_agent_l`, `app/`, "an oracle" and `.claude/rules/test-oracles.md`. "Summing the record again in `app/` … so the build kept the one sum (`PL-KFTM`, 2026-11-01)" is decision history. Both belong in `PL-KFTM`. The item should keep what the release gains:
  - the model passes each of the six compartments' amounts to the display, beside its tension;
  - the amounts travel as one record per compartment, so that v0.8.0 can add substances without adding fields;
  - no equation changes;
  - a test checks each amount, at stated instants, against a calculation independent of the model.
- **Code names and decision history in other items belong in their queue items.**
  - Item 1's `AGENT_AMOUNT_DISPLAY_PRECISION` and "the three totals" (rows 7214-7216) go to `PL-2881`. Item 1 keeps that at the run totals' 0.1 L resolution, venous blood and the alveoli would read 0.0 L for a whole hour at 1 MAC. Query: the reader needs to know which three totals these are, and this chapter does not name them. If the code name moves, this question goes with it.
  - Item 3's `src/anesthesia_sim/app/view_contract.py` (row 7242) and `app/theme.py` (row 7252) go to `PL-RNYV`. Item 3 keeps that any Area can hold the schematic and that it uses the chart's compartment colours.
  - Item 10's "as `PL-MQHN` decided" and "`app/preferences.py` is that store (`PL-93B3`, 2026-11-01)" (rows 7301-7302) go to `PL-93B3`. Item 10 keeps the decision itself: a versioned preferences file, separate from the Workspaces.
- **Item 12 buries its point and uses an undefined term.** The point of item 12 (rows 7310-7319) comes only in its last sentence (rows 7316-7319): the copy editor is fixed so that the `docs/MODEL.md` sections a learner reads beside the schematic and the agent cost View are written for a clinician. Put it first.
  - The owner's verbatim message and its timestamp (rows 7312-7313) are decision history for `PL-HGZS`. The item keeps that the project owner added this work to v0.7.0 on 2026-11-04.
  - "so `PL-HGZS` records it as a live generator" (rows 7315-7316) uses a term this chapter does not explain. It belongs in `PL-HGZS`. The item keeps the fault in plain words: the copy editor keeps text the reader does not need, and lengthens some of it.
- **Items 9 and 10 depend on a fact only item 11 gives.** Items 9 and 10 (rows 7292-7302) rely on rows 7304-7307: the reader sets a price per agent, and the project ships none. Item 9 also speaks of "a stored price" (row 7293) before item 10 says where the price is stored. Use the order 8, 11, 10, 9. Query: the reader needs to know whether the item numbers give the build order, and the section does not say. If they do, keep the order and open item 9 with the reader-set price instead.
- **The section needs subheadings, and item 1 needs a sub-list.** The section holds three pieces of work in 1221 words. A reader deciding the release's scope has to find where each one starts.
  - Put a subheading before item 1 for the compartment schematic (items 1-5), one before item 6 for the agent cost in liquid and in money (items 6-11), and one before item 12 for the copy editor.
  - Keep the item numbers, because other text may cite them.
  - Item 1 makes six points in one list item (rows 7200-7224). Once the findings above are applied, give its remaining points as a sub-list: unit naming, the per-compartment precision, and the two hazard rows.
- **Some item headings do not say what the item holds.**
  - Row 7226, "Each compartment's amount on the snapshot": "snapshot" is a code name. Use "Each compartment's amount passed to the display".
  - Row 7265, "A shipped Workspace that places it": "it" points at nothing in the heading. Use "A shipped Workspace that places the schematic".
  - Row 7279, "The precision of each unit": the item derives a precision for each quantity and each unit. Use "A displayed precision for each quantity and unit".
  - Row 7292, "What a reader's price carries": the item also sets what a cost readout shows beside the cost. Use "What a stored price records, and what a cost readout shows beside it".
  - Rows 7310-7311, "The copy editor, fixed, and the rewrites it holds": "holds" is used in a private sense, and the body says "blocks". Use "Fix the copy editor, then make the five `docs/MODEL.md` rewrites that wait on it".
- Query, row 7288: "as item 28 records". This section has only twelve items. The reader needs to know which list item 28 belongs to, and the text does not say.
- Query, rows 7269-7270: "Which Workspace places it is a placeholder decision." The reader needs to know whether the choice of Workspace is still open, and who makes it before the release. The text does not say.
- Query, rows 7258-7259: "at one hour fat holds a fifth of the stored agent". The reader needs the setting (agent and MAC) at which this holds. Item 1 gives "at 1 MAC" for its own figure, and this sentence gives none.
- Query: this chapter never explains View, Area, Workspace, View chooser, compare mode or readouts. If no earlier chapter explains them, a contributor needs each one explained where it first appears.
```

**Chapter read 40: § "Definition of done", rows 7321-7362.**

```text
- Order: one bullet applies to the whole release, not to one feature: "Nothing a learner could do on v0.6.0 is lost, checked against v0.6.0's own definition of done" (rows 7348-7349). It sits between the schematic's bullets and the cost View's. Move it to the end, beside "`make check` is green, and `docs/MODEL.md`, `docs/ARCHITECTURE.md` and `README.md` describe the interface that exists" (rows 7361-7362). Each feature's bullets then stay together, and the release-wide conditions close the list.
- Order within the schematic's bullets: two bullets on what the learner sees come after three bullets on checks (rows 7333-7342). They are "The schematic says on its face that its values are modelled" with its precision (rows 7343-7345), and "Each container is named in text, so no compartment is told apart by colour alone" (rows 7346-7347). Move rows 7343-7347 to follow rows 7328-7332. The reader then gets what the schematic shows first, followed by the checks that its numbers are right.
- Subheadings: the list has 13 bullets on four subjects. Put a subheading, or a bold lead-in, before each group:
  - "Compartment schematic" before row 7323.
  - "Agent cost View" before row 7350.
  - "Copy editor" before row 7358.
  - "Whole release" over rows 7348-7349 and 7361-7362, once they are moved together.
- Split: the bullet at rows 7328-7332 makes two points. One is the containers' fill and labels (rows 7328-7330). The other is the bar of each compartment's share (rows 7331-7332). Give the bar its own bullet.
- Split: the bullet at rows 7350-7355 makes three points: placing the View and choosing a unit, the cost display, and the end-to-end test. Give the test (from "An end-to-end test checks the liquid figure", row 7353, to row 7355) its own bullet, as the schematic's test has at rows 7337-7339.
- Written for another reader: four bullets name tests, tools or folders by names this reader does not know:
  - "an oracle independent of `core/`" (rows 7338-7339)
  - "`tools/contrast_check.py` covers every colour" (row 7346)
  - "as `PL-HGZS`'s stress test judges" (row 7359)
  - "`make check` is green" (row 7361)

  The writing rule's owner decision (`PL-BGN1`) asks for what changes, not internal names. Keep here what each check guarantees, in words, and move the names to the milestone's items.
- Query: row 7342 says "every label matches the snapshot", and the chapter does not say what the snapshot is. The reader needs that to judge the condition.
- Query: the copy-editor bullet (rows 7358-7360) leaves three things open. The chapter does not say what `PL-HGZS`'s stress test measures or what result counts as passing. It does not say which five `docs/MODEL.md` rewrites "waited on it". Its "it" could mean the copy editor or the stress test. The reader needs all three to decide whether the release is done.
- Query: the schematic must say on its face that its values are modelled, and must give its amounts at a stated precision (rows 7343-7345). The cost View's figures are also modelled values from a run, but its bullets (rows 7350-7357) say neither. Should the cost View meet the same two conditions?
- Query: row 7326 names "the three tissue groups" without naming them. The reader deciding what the schematic shows needs the three names, and the chapter does not give them.
```

**Chapter read 41: § "Explicitly out of scope for v0.7.0", rows 7364-7411.**

```text
- Repeat (rows 7367-7368 and 7372-7373): "and inject liquid, from the Picture itself" and "Gas Man draws a button for each of them on its Picture" both describe liquid injection from Gas Man's Picture. It belongs in the injection entry (7372-7374). The controls entry (7366-7371) drops "and inject liquid" and keeps nothing.
- Repeat (rows 7368-7371 and 7376-7378): "Here the settings stay in the parameter controls View … A control on the schematic would be a second way to change the same setting, and that needs its own design round" and "The parameter controls View already states all three. Drawing them a second time belongs with the controls above" make one point. Showing or changing these settings in a second place waits for one design round. Merge the gauges entry (7375-7378) into the controls entry, so that it covers both controls and gauges on the schematic. The gauges entry then keeps nothing.
- Pointer back (row 7379): "The measurement above" sends the reader to a section this chapter does not name, and that section probably gives the same figures. The figures are short, so keep them in this entry and replace "above" with that section's heading in the form § "Heading". Query: the reader needs the heading of the section that reports the container widths, and the date they were measured, and the chapter gives neither.
- Wrong reader and wrong place (rows 7391-7392): "So `PL-L6QR`, which waits on item 36, now waits on v0.8.0 instead" records a change to another item's dependency, which is decision history. The change belongs in the `PL-L6QR` item. The current fact, that `PL-L6QR` waits on v0.8.0, belongs in the v0.8.0 chapter, where the reader looks for what that release holds. This entry keeps nothing.
- Order and subheadings (rows 7366-7411): the 13 entries mix the schematic, the agent cost View and the whole milestone, so a reader looking for one topic has to read the whole list. Use this order:
  - First, the entries that cover the whole milestone: equations and parameters (7395-7398), then the View catalogue (7389-7392).
  - Next, the schematic entries (7366-7388), with the visual pass (7393-7394) moved up after "Showing a past instant".
  - Next, the cost entries: price (7399-7401), carbon dioxide equivalent (7402-7405) and uptake (7409-7411).
  - Last, the preferences workflow (7406-7408).
  - Put a subheading over the schematic group and one over the cost group, such as "The schematic View" and "The agent cost View".
- Pointers to Required scope (rows 7397, 7401, 7402, 7406): entries 6, 8, 10 and 11 send the reader back to another section for short material. The second part should state each thing in place.
- Query (row 7397): the reader needs to know what "the two constants per agent" are, and the chapter does not say.
- Query (row 7402): "The unit decision behind entry 8" points to a decision the reader did not see. The reader needs to know which unit was chosen, which list "entry 8" belongs to, and which item records the decision. The chapter gives none of these.
- Query (rows 7404-7405): carbon dioxide equivalent "waits for a decision of its own", which is a decision for the owner, but no item tracks it. The reader needs that item's id.
- Query (rows 7372-7374): liquid injection has planned-milestone item 4, but the circuit flush has no item or release. The reader needs to know whether the flush is planned anywhere.
- Query (rows 7393-7394): the visual pass is "on the `v0.6.x` track", but "until then" the v0.7.0 schematic is a placeholder. The reader needs to know whether the visual pass comes before or after v0.7.0, and the chapter does not say.
- Query (rows 7392, 7405): the chapter does not say what `PL-L6QR` is. It also uses "Picture", "View", "the share bar", "the per-compartment record" and "the `v0.6.x` track" without explaining them. The outline read should confirm that an earlier chapter explains each one where it first appears.
- The heading "Explicitly out of scope for v0.7.0" says what the section holds.
```

**How to apply.** Move and deduplicate only. No sentence is reworded, except a pointer that replaces a restatement, a word such as "above" or "below" that a move made wrong, and a heading. The line edit of what this slice changes follows in `PL-YRY3`, once the copy editor no longer drops requirements (`PL-F0Q2`). Each finding is applied, or recorded here with the reason it was not. A query that the tree answers is answered in the pull request, and one that needs the author is filed as its own item under `roadmap-structure`. Whether a finding that moves decision history out of the roadmap and into an item is applied is decided by the project owner's answer in `PL-LVN8`. Before the pull request is marked ready, two reviewers compare the old and new text passage by passage for any change of meaning. The move-only restructures of the machine documents and of `docs/interface-provenance.md` each changed 10 or 11 meanings that only such a comparison found.

**Done when.** Each finding below is applied, or recorded here with the reason it was not. No statement is lost: every sentence that leaves its place is kept at its one home, or replaced by a pointer that names that home. `bin/docket wave`, `bin/docket gate` and `bin/docket check` give the same answers before and after the slice, and `make check` passes.

**Generator check.** The repeats came from accretion. Each change that touched a topic stated its own record in the section it was working in, instead of pointing to the section that already held it. The structure read found the same shape in every document it read (`PL-BSMF`, `PL-SVGH`, `PL-T8RL`, `PL-39ZK`, `PL-3MTS`), so these are one sweep's findings. No check can decide whether two sentences state one fact. The structure read, which the project owner put ahead of every line edit on 2026-11-07, is the procedure that catches the shape. Not recorded as a generator.

**Where the quoted row text is now (2026-11-07).** `PL-DWGC` keeps one sentence in each version-table row and moves the rest of the row, word for word, to the release's cut item, which the table's Details column names. The v0.6.15 and v0.6.16 rows' "test-driven" sentence is now in `PL-8B6Z`'s and `PL-80PZ`'s briefs, and the baseline still states it.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present in part when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. About two-thirds of the findings concern text that was in `817a4d88`, where the v0.7.0 section was written. The rest concern text added after it: each admission after the cut, the staleness-sweep paragraph and the test-drive condition.

**What this slice did (2026-11-07).** Each finding, by what happened to it. A sentence that left `ROADMAP.md` either duplicated one that stays, is held by the file named beside it, or is quoted word for word, under a line naming this slice, in the item named beside it.

*Applied.*

- Outline finding 7, v0.7.0's half. § "Deferred from this gate" is now § "Captures after the cut". It opens with the rule for a capture, which now also states once that the open part of a frozen entry stays on the list. Every admission after the freeze follows in date order: `PL-QX2G` and `PL-YT3T`, `PL-J5GC`, `PL-P319`, `PL-4LS8`, the six captures of 2026-10-31, `PL-SP6H`, `PL-0P3F` and the 36 captures of 2026-11-07. The two citations of § "Deferred from this gate" inside them now read "the rule at the head of this section".
- Outline finding 53. The definition of done ends with "v0.7.0 is cut only after the project owner has test-driven `main`", word for word from § "Current baseline", which keeps the status.
- Chapter read 35, the opener. It says what the milestone holds, then lists the two choices put to the owner as a numbered list with their tags whole. The two reason paragraphs sit under the first choice, each opening with its point as a bold lead. The paragraph after the list keeps which choices were made without the owner, and why. `PL-LF0P` now quotes "Item 27 now says so" and the sentence naming `AgentUptakeSystem.for_agent`. The figures keep their date in a sentence of their own, and a bold lead now says the six containers are this model's.
- Chapter read 36, the Goal. The end state comes first. The table's paragraph and the lead-in to the gaps are two paragraphs. Gap 4 no longer repeats gap 1's sentence that the only amounts are the accounting View's totals in litres of vapour.
- Chapter read 37, the frozen list. It opens with the two groups, then the freeze and the staleness sweep, then the two Gate 4 deferrals and `PL-5B1N`. The paragraph on the four item-28 entries sits straight above the first list, which holds them. The three `PL-5B1N` passages are one paragraph, and its stale "So the item is `ready` again" is quoted in `PL-5B1N`. The freeze-date derivation is quoted in `PL-LF0P`, the `PL-HDRN` history in `PL-HDRN`, and the `PL-YRLM` sentence in `PL-YRLM`. "Each item's `deferred-from: v0.7.0` says so" went, because § "Deferring to the next gate" records that each deferral is on its item. The sweep's reason sentence went, because `PL-F2NX`'s brief holds it. The second list's heading now reads "Cleared before v0.7.0's implementation begins, unless deferred", as the opening paragraph does.
- Chapter read 38. The `PL-J5GC` history of its first `deferred-from:` is quoted in `PL-J5GC`.
- Chapter read 39, Required scope. Three subheadings: the compartment schematic (entries 1 to 5), agent cost in liquid and in money (6 to 11), and the copy editor (12). Entry 1's six points are a sub-list. Four entry titles say what the entry holds: "passed to the display", "places the schematic", "A displayed precision for each quantity and unit", and "What a stored price records, and what a cost readout shows beside the cost". Entry 12's title is "Fix the copy editor, then make the five `docs/MODEL.md` rewrites that wait on it". The owner's quoted message and the stale "so `PL-HGZS` records it as a live generator" are quoted in `PL-HGZS`, because the generator is spent; the entry keeps "(project owner, 2026-11-04)". Entry 10's `app/preferences.py` sentence went, because `PL-93B3`'s brief holds it.
- Chapter read 40, the definition of done. Four bold group lines: the compartment schematic, the agent cost View, the copy editor and the whole release. What the schematic shows comes before the checks on its numbers. The fill bullet and the share-bar bullet are two, and the cost View's end-to-end test is its own bullet. The v0.6.0 regression bullet closes the list with `make check` and the test drive.
- Chapter read 41, out of scope. The two entries for the whole milestone come first, then a subheading for the schematic View's seven entries, with the visual pass after "Showing a past instant", then one for the agent cost View's four. The controls entry no longer repeats "and inject liquid". The `PL-L6QR` sentence is quoted in `PL-L6QR`, whose `blocked-by: v0.8.0` holds the current fact.

*Not applied, with the reason.*

- Rewording findings: `PL-YRY3`, the line edit, now lists 13 of them, among them the heading rename, "measured" for a model run, the code names in the Goal and in Required scope entries 1 to 3, and the internal check names in the definition of done.
- The Goal's gap on amounts not passed on stays in its dated list of four. Moved out of the list it read as true today, and `PL-KFTM` has since passed the amounts on.
- The opener keeps its "because each remaining choice ..." clause. Without it, the sentence after it read as making the whole section a placeholder.
- Required scope entry 2 keeps its second-sum sentence. `PL-KFTM`'s brief points at it, and it says why `stored_agent_l` stays `core/`'s sum although the list entry's title says it is derived from the records.
- "The measurement above" in the out-of-scope list stays, because the figures are still above it.
- The Goal's end-state paragraph stays one paragraph. Its last sentence's "it" and "the View" can mean the schematic or the agent cost View, and a split would settle the reading. `PL-71H3` and `PL-11Z9` hold the question.
- The paragraphs that repeat their list entries (`PL-P319`, `PL-SP6H`, `PL-0P3F`) keep the detail, because it is the evidence that each hazard was live, the ground for admitting it. Cutting it needs each paragraph reworded (`PL-YRY3`).
- The owner's one action on the gate, adding the Katoh 1993 paper (`PL-P319`), did not move to the opening paragraph. `PL-P319` is closed, so the gate no longer waits on it. `PL-YRY3` holds the stale clause.
- The list's two count-carrying group lines stay bold lines. `tools/doc_check.py` counts only a bold group line, and `bin/docket` reads "Cleared by v0.7.0 itself" from it. The 118 entries are not regrouped by subject: that is a new classification, and `bin/docket gate` prints them by feature.
- The frozen list keeps its place before Required scope. Every milestone section that records a gate has that order, and § "The debt gate" now comes before this section.
- The Gate 4 paragraph keeps its three sentences on Gate 2. They already give the owner's earlier decision with its tag whole and say the question was not put again; condensing them is the line edit's.
- In § "Captures after the cut", the generator-head history of `PL-58D7` and `PL-J5GC` stays. The sentences after them name the deferred members and the three entries the guard covers, so a move needs a rewording.
- Required scope entry 1 keeps what the specification asserts, although entries 3, 4 and 8 build the same things. Each entry is a different item's scope (`PL-2881` against `PL-RNYV`, `PL-S79P` and `PL-B396`). `PL-YRY3` holds the choice of one home. Entries 9 to 11 keep their order, because the out-of-scope list cites entries 10 and 11 by number. Entry 12's point stays last, because it is the second of two sentences in sequence.
- Entry 1's `AGENT_AMOUNT_DISPLAY_PRECISION`, entry 3's file paths and entry 10's "as `PL-MQHN` decided" stay. The first two need a rewording, and the third is the decision's pointer.
- The gauges entry stays beside the controls entry. Merging them needs a sentence saying the gauges wait on the same design round.
- The opener's "A setting turns these into money" stays, because its "these" names the two totals before it. The Mapleson citation stays whole, as the finding allowed.

*Queries the tree answers.*

- `PL-5B1N`: it closed with its build, which the merged paragraph now says.
- The 0.1 L step's band, a quarter or a seventh of an SD: `PL-SP6H` and `PL-KG6S`, both on the frozen list, hold that disagreement in `docs/MODEL.md` § "Displayed precision".
- Planned-milestone item 28 is agent cost, as the section's first sentence says. "As item 28 records" in Required scope entry 8 is that item.
- The list entries do not have to repeat their items' titles. The walker reads only each entry's leading ids.
- What the gate deferred: `bin/docket wave` prints each deferral with its state, as § "Recording it" says. `PL-9Z74` and `PL-93LV` are among them.
- A `safety` entry may be deferred with a capture it waits on since `PL-8C8W`, on the terms of § "Deferring to the next gate".
- The cut was the freeze on 2026-10-25, `origin/main` at `0947408`, as the frozen list says.
- The Workspace that places the schematic was chosen by `PL-PR1W`'s build, which is done.
- "At one hour fat holds a fifth of the stored agent" is sevoflurane at a 1 MAC dial, the Goal table's 60-minute row.
- The three tissue groups are the vessel-rich group, muscle and fat (Required scope entry 3). The five rewrites are `PL-HRPK`, `PL-PS5H`, `PL-XBJ3`, `PL-XT53` and `PL-YVL0` (entry 12). The two constants per agent are the molar mass and the liquid density (entry 6).

*Queries filed.* `PL-71H3` (feature `roadmap-structure`) holds the ten that need the author, among them whether the View choice was ratified, the Gas Man Workbook's edition, the Goal table's date and denominator, the sweep's count of 24, and the terms the section never defines. `PL-11Z9` is a finding the queries led to: the agent cost View does not say on its face that its figures are modelled, and the definition of done asks that only of the schematic. It changes interface wording on the safety-critical path, so it is filed for triage rather than fixed here.

*Review.* Two reviewers compared the old and new text, one for words that depend on position and one sentence by sentence. The second accounted for the 317 sentences outside the two entry lists, which are byte for byte the same: 193 unchanged, 16 with a changed word, 81 moved, 3 duplicates, 4 held elsewhere, 19 quoted in briefs, and 1 lost. Their findings, applied:

- The lost sentence, the six captures' citation of the rule that admitted them, is restored as "The rule at the head of this section admitted such a capture rather than deferring it". `PL-SP6H`'s "the rule above" pointed at the nearer `PL-P319` deferral test, so it names the head of the section too.
- The gap on amounts not passed on, the opener's "because" clause, and entry 2's second-sum sentence are restored, as listed above.
- The figures' date had attached to the isoflurane and desflurane sentence alone. It is now a sentence of its own after them, and "the six containers" is "this model's six containers", because the paragraph before it lists Gas Man's seven.
- The freeze paragraph now comes before the Gate 4 paragraph, which uses `0947408` before the freeze paragraph explained it.
- Entry 9's title ended "beside it", whose nearest noun was the price. It ends "beside the cost".
- Entry 12 keeps the owner's decision marker, "(project owner, 2026-11-04)".
- `PL-LF0P`'s lead-in glosses "Item 27" and "so", and `PL-5B1N`'s glosses "this section" as the whole v0.7.0 section.

Not applied: the definition of done's test-drive bullet is an addition rather than a move. It is the one addition this item's title asks for, and the pull request says so. "The section" in the `PL-0P3F` and `PL-TDX0` sentences was ambiguous before the move, and `PL-71H3` holds that question.

*Checked.* `bin/docket wave`, `bin/docket gate` and `bin/docket check` give the same answers as before, apart from this item's claim and the two items filed. `tools/doc_check.py check` reports 0 errors and the same two advisories.
