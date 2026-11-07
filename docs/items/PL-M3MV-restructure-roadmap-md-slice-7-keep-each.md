---
id: PL-M3MV
title: Restructure ROADMAP.md, slice 7: keep each planned milestone to its intent and what remains, and move each shipped or scheduled record to its milestone section or item
priority: P2
effort: L
status: blocked
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
blocked-by: PL-B6V1
deferred-from: v0.7.0 - filed after the gate froze; the roadmap's arrangement and wording, with no displayed value depending on it
added: 2026-11-07
---

**Problem.** Restructure ROADMAP.md, slice 7: keep each planned milestone to its intent and what remains, and move each shipped or scheduled record to its milestone section or item

**Source.** The copy editor's structure read of `ROADMAP.md`, run on the project owner's Mac on 2026-11-06: one read per chapter, then one read of all the chapters' outlines together. Row numbers are `ROADMAP.md` at `aff76df1`, the last commit to change it before slice 1 (`PL-W0TS`), so a later slice finds each passage by the words the finding quotes. The project owner chose to file the findings as items and apply them one slice per pull request (project owner, 2026-11-07, ratified, over one pull request for the whole restructure), because the release tools read the roadmap's gate sections and a small move is easier to check against them. The raw reads are in the project's shared folder, `/mnt/project-files/v0.7.0/repo-copy-edit/mac-structure-reads/ROADMAP-md/structure/`.

**Why it matters.** § "Planned milestones" says an item stays intent until it is promoted, and that a delivered item is removed. It still holds the scoping records of items 8, 11, 12, 25, 26, 27, 28, 29 and the tiled half of 34, and those records repeat the milestone sections. Some of them now contradict the sections (`PL-1BVB`). A reader choosing what to build next needs each entry to say what is still wanted.

**The findings, as the outline read gave them** (numbered by their order in the read: 21, 26, 37, 38, 39, 40, 41, 42, 47).

- Break-out came off the timeline: "The schematic (item 27) moved back to v0.7.0, and multi-substance (items 6 and 7) moved to v0.8.0 (PL-V1Y7)" (9296-9319); 450-456, 491, 1851-1856, 5863-5876, 6816-6831, 8985-8995 and version row 115 say it again. It belongs in item 34 (9296-9319). The timeline rows keep their dated renumberings, as 372-377 requires, and the others keep a pointer. 9275-9294 still gives the superseded consequence "schematic (item 27) to v0.8.0, multi-substance (items 6 and 7) to v0.9.0", which can go.
- Item 34's placement: row 7 gives "Scoped 2026-09-16 (project owner, ratified on PL-NMTF, over moving item 34 ahead of v0.5.0 and over one undivided milestone)" and "the work a reorder would protect was 4 M and 3 S" (450). Item 34 gives "Remaining: the bookmarks chain and three small items, 4 M and 3 S, against item 34's 4 L / 16 M / 3 S" (9321-9348). 479-488, 5607-5617 and 9275-9294 cover the same ground. It belongs in item 34, and timeline row 7 and the v0.6.0 section keep the dates. Row 7's "Standing rule: no new display surface before this release" (450) reads as if it still applies. 9350-9368 says the rule ends when the View contract and the view registry ship, and both shipped in v0.6.0, so row 7 should say that the rule has ended.
- The cost basis: "Gas Man bills delivered agent (Cost = DELIVERED Flow x Cost/mL vapor, Workbook p. 174)" (2931-2937) and "(Workbook Appendix, printed p. 174: Cost = DELIVERED Flow x Cost/mL vapor)" (8501-8505); 4584-4592 and 7284-7290 say it too. It belongs in item 28 (8488-8527), and the gate entry keeps one line.
- Shipped or scheduled items in the catalogue: § "Planned milestones" says an item stays intent until it is promoted (8080-8087) and that a delivered item is removed (8906-8912). It still keeps the scoping records of item 8 (8205-8220), items 11 and 12 (8223-8290), item 25 (8372-8379), item 26 (8380-8450), items 27 and 28 (8452-8555), item 29 (8557-8726) and item 34's tiled half (9076-9407). These records repeat the milestone sections:
  - a crossing is tested on every step (8416-8424; 5340-5347);
  - one trunk with N branches (8235-8238; 5348-5350, 5565-5566);
  - a branch reproduces its parent element-wise (8264-8281; 1537-1556, 2188-2198, 5394-5397);
  - fat's share of the agent at one hour (8465-8477; 6924-6938, 7255-7263);
  - Gas Man's Picture fills to tension, Workbook Figure 2-1, p. 11 (8452-8463; 6896-6907);
  - the 2026-10-25 decision on item 28 (8478-8486; 454, 6881-6894);
  - the vapour-to-liquid constants (8529-8550; 7200-7224, 7272-7277).
  Each record belongs in its milestone section, or in the items for decision history. Each catalogue entry keeps its intent, what remains of it, and "Shipped in vX" or "Scheduled in v0.7.0".
- "PL-2CS8 consolidated them in v0.4.11" (8316-8327), "PL-2CS8 landed it in v0.4.11" (8037-8045) and "PL-2CS8 consolidated the display constants in v0.4.11" (9027-9040): the fact belongs in item 24, and the other two places keep nothing.
- "six traces cannot be more than 1.48 apart" (8360-8370) and "PL-GVXP measured the pairwise ceiling at about 1.48" (9053-9066): the fact belongs in item 24's table of values the panel may not change, and item 33 keeps a pointer.
- "A machine's whole effect on the model is two rates and one volume in the breathing circuit's row" (8161-8182) and "a machine affects the model only through two rates and one volume" (9597-9604): the fact belongs in item 40, which builds the framework, and item 1 keeps a pointer. Query: item 1 gives the cost target as one data file "with no change to core/" (8184-8188). Item 40 says that target "cannot be reached ... a machine is one data file plus one provenance row per number. The target should say so" (9621-9626).
- Water vapour: "diluted by 47/760, or 6.2 %" (2993-3003), version row 96, and "applying 713/760 to the inspired term ... moves all four validated wash-in ratios outside their published spread" (9559-9566). The fact belongs in item 39. The gate entry and the version row keep one clause each.
- Why the teachable case came first: "The run advances at 1x real time and the chart spans 5 minutes" (8012-8030) reads as current. It restates v0.4.0's Goal, dated 2026-08-25 (1138-1148), and v0.4.0 has since fixed it (version row 65). It belongs in v0.4.0's Goal. § "Development pathway" keeps that the teachable case was taken ahead of Phase 1 on 2026-08-25.

**Queries filed separately.** `PL-W6VL` (item 1's cost target against item 40's), `PL-6LBQ` (fat's share at three hours), `PL-1BVB` (six catalogue statements other chapters contradict) and `PL-K6DG` (the Beyond row's order and item 30).

**The findings inside each chapter, as the chapter reads gave them.** Each chapter read also ended with an outline of one line per paragraph, which is left out here and kept in the shared folder. Each read is quoted whole, as a block, so that its quotations of the roadmap are not taken for this item's own claims.

**Chapter read 45: § "Development pathway", rows 7912-8076.**

```text
- **Repeats: the timeline overrides the phase order.** The point appears four times:
  - rows 7914-7916: "This section gives the intended order for the part of the catalogue that § "The timeline" has not yet placed"
  - rows 7916-7918: "A release that the timeline names takes the timeline's order. Where the two disagree, the timeline's order governs"
  - rows 7919-7920: "But a phase's order covers only what the timeline has not placed"
  - rows 7931-7932: "For the work that the timeline has not placed, that order still applies"

  Give it once, in the first paragraph, with its pointer to § "The planning model: a rolling wave". The other three places keep nothing.
- **Repeats: the change of order on 2026-08-25.** The point appears four times:
  - rows 7930-7931: "Since 2026-08-25, the timeline has taken interface and comparison work ahead of the science"
  - row 8008: "The reordering below set that placement aside"
  - rows 8026-8030: "That was the order on 2026-08-25 and is no longer: since then, the timeline has placed further releases ahead of the generalization"
  - rows 8073-8074: "Since 2026-08-25 the timeline builds milestones before it"

  It belongs in rows 7930-7931. The other three keep nothing.
- **Repeats: code written for a single gas must be reworked.** The point appears three times:
  - rows 8006-8008: "an interface built on a single-gas core would be reworked when it lands"
  - rows 8014-8015: "The reasoning was that an interface built on a single-gas core would be reworked"
  - rows 8071-8073: "Every milestone built before the substance generalization is code written against the single-agent assumption, and it would have to be revisited afterwards"

  It belongs in the known risk, which rows 8009-8010 already call its general form. The other two keep nothing.
- **Repeats: nitrous oxide was placed before the interface.** Rows 8003-8004 say "nitrous oxide sat before any interface work", and rows 8013-8014 say "Phase 1's substance generalization and nitrous oxide come before all interface work". Rows 7928-7930 already give the original order (the science, then the interface), so both can go.
- **Repeats: the size of the queue when Phase 0 was written.** Row 7944 says "nine of twenty-four open items", and rows 7958-7959 say "The queue held 24 open items when Phase 0 was written". Give the count once, wherever the Phase 0 history goes.
- **Repeats: Phase 0 can never close.** Row 7936 says "on its own terms it never can be", and rows 7962-7963 say "A gate that requires a refilling queue to empty never opens". Its status also has three names: "Superseded" (row 7934), "not closed" (row 7936) and "retired as a phase" (row 7973). Keep "Superseded", with its date, in the lead-in, and give the outcome once.
- **Repeats: Phase 3 depends on item 8.** Rows 8043-8045 say "Phase 3 cannot start without that entry, because save/load, replay and forking each restore from it", and rows 8048-8049 say "built on top of item 8's control-input timeline". The dependency and its reason belong in Phase 3. Phase 2 keeps only that the control-input timeline has shipped.
- **Order: Phase 0 (rows 7934-7976) gives its outcome last.** Rows 7973-7976 say what the reader acts on:
  - Phase 0 no longer blocks a planned milestone; only that milestone's own gate does.
  - The items behind its unmet conditions are in the current frozen gate.

  Put this right after the lead-in, with the pointer to § "The debt gate" from row 7965. Rows 7936-7971 are the record of the 2026-08-25 decision: the note on the reproduced conditions, the original rule and its motive, the table, why Phase 0 was superseded, and the gate compared with Phase 0. Move them to the item that records the decision, and keep "State on 2026-08-25" beside the table's counts. How the debt gate works (rows 7966-7968) belongs in § "The debt gate".
- **Table row 7954 has grown into an essay.** It packs in five points: the condition was met, it became unmet again the same day, the item `PL-Y2GG` was moved, why it was moved, and a judgement about honesty. Wherever the table goes, the reason for `PL-Y2GG`'s status belongs in `PL-Y2GG`. The cell keeps "Met" and the fact that one item was moved back to `needs-decision` the same day.
- **Rules for writers in the first paragraph (rows 7918-7922).** These sentences tell a writer how to maintain the section:
  - "Each phase keeps its name and its intent, because other documents cite a phase by name"
  - "Where the timeline has taken a phase's first half, the phase says so without naming the release. How that half came to be taken is dated as history rather than restated (`PL-5XG1`)"

  Move them to `PL-5XG1`. Leave the reader what the rules guarantee: a phase says when § "The timeline" has taken part of it, and that section gives the release.
- **Sentences about the text itself.** Three sentences describe the document instead of the plan:
  - rows 7936-7938: "Its closing conditions are reproduced below unchanged, followed by their state on the date above"
  - row 8037: "is recorded here as dated history"
  - rows 8050-8051: "That departed from the phase's first sequence of 9, 10, 11, 12, and § "The timeline" records why"

  Cut them. Phase 3 keeps "shipped in v0.5.0 ahead of both", and may keep the pointer to § "The timeline".
- **Item 40 (rows 7984-7986).** That item 40 was split out of item 1 on 2026-09-20 by the project owner is decision history, and belongs in item 40. Phase 1 keeps two facts: item 40 is not part of the phase, and nothing in a config file needs the substance generalization.
- **Rows 8003-8010, Phase 1 as first written.** This is the history of a placement the section no longer uses, and it sends the reader ahead twice ("The reordering below", "The known risk at the end of this section"). Its first reason still says why Phase 1 matters: the second-gas effect is the phenomenon this class of simulator is most used to teach. That reason can join the reasons in rows 7988-7993. The second reason is the known risk. Cut the rest.
- **Rows 8012-8030, the reordering.** This is a dated decision record. It sits inside Phase 1, although it moved work ahead of every phase, and its own last sentence says its order no longer holds. Its outcome is already in rows 7930-7931.
  - Move it to the item that records the decision, with its tag "(project owner, 2026-08-25)" whole.
  - One fact belongs with the known risk, because it bears on the owner's open question. On 2026-08-25 the rework of interface work built before the generalization was judged bounded and known: the MAC readout is the piece that changes, and it becomes a MAC sum when a second substance lands.
  - Three further faults: rows 8023-8024 are written for a developer (`SimulationSnapshot`, "substance-agnostic"). The lead-in's "the teachable case" does not say what was moved. Row 8013's "As written below" points down to a Phase 1 that stands above it.
- **Phase 2, rows 8032-8045.** "item 24 itself" (row 8032) refers back to a mention that comes only in rows 8038-8039, so the reader has to read ahead; drop "itself". Rows 8037-8045 are the history of shipped work:
  - Why the display constants came first belongs in `PL-2CS8`.
  - Which release shipped what belongs in § "The timeline".
  - The phase keeps one sentence naming its shipped work: the display constants, items 25 and 26, and item 8's control-input timeline.
- **The known risk (rows 8068-8076).** The one decision the owner must make in this section comes in its last sentence. The decision is whether the rework argument still applies to the milestones that the timeline places before the generalization (`PL-5XG1`). Move the whole paragraph to follow rows 7927-7932, where the reader learns that the timeline builds interface work before the science. State the question there in full, not as a pointer to its item. The departure from the planned order is then stated once.
- **Subheadings.** The section runs to 1716 words, and its phases are bold lead-ins inside running text. Make each a level-3 heading, with its name unchanged, so the reader can go straight to a phase and other documents can still cite it by name:
  - "Phase 0 — foundation"
  - "Phase 1 — scientific maturity"
  - "Phase 2 — an interface that can drive the machine"
  - "Phase 3 — reproducibility and comparison"
  - "Phase 4 — intravenous agents"
  - "Alongside, as opportunity allows"
  - "The known risk", wherever that paragraph ends up

  Phase 0's "Superseded by the standing debt gate, 2026-08-25" becomes its first sentence.
- **Section heading.** "Development pathway" says what the section holds, and keeps its text.
- **Query (decision records):** no item is named that records either 2026-08-25 decision: the replacement of Phase 0 by the debt gate (row 7934) or the reordering (row 8012). The history moved above therefore has no named destination. The Phase 0 lead-in also does not say who decided.
- **Query (row 7959):** "it holds 48 now" gives no date for the count.
- **Query (row 7961):** "the capture rule" is a repository term that this section neither explains nor points to.
- **Query (rows 7943 and 7952):** row 7943, "The queue holds almost no defects", contradicts row 7952, "8 defect-classed items open" on 2026-08-25. It holds only if row 7943 means the queue when Phase 0 was written.
- **Query (rows 8017-8019):** "The run advances at 1x real time and the chart spans five minutes" is in the present tense, but rows 8041-8042 say item 25 (playback speed) shipped in v0.4.0. Is row 8017 the state on 2026-08-25?
- **Query (rows 8038-8041):** these rows say the display-constants work "came first" in Phase 2. But it landed in v0.4.11, after v0.4.0 had already shipped item 25 and the recording half of item 8's control-input timeline.
- **Query (rows 7920-7921):** these rows say that where the timeline has taken a phase's first half, the phase does not name the release. Yet rows 8041-8043 and 8049-8050 name v0.4.0, v0.4.11 and v0.5.0. Does the rule cover only work not yet shipped?
- **Query (rows 8042-8043 and 8048):** item 8's replay driver shipped in v0.5.0, while item 10, deterministic replay, is still to come. The reader needs to know what item 10 adds.
- **Query (rows 8075-8076):** "`PL-5XG1` records that question, with its count" does not say what is counted. To decide, the owner needs the section to say which milestones the timeline places before the generalization.
```

**Chapter read 46: § "Planned milestones", rows 8078-8672.**

```text
- Repeat, rows 8097-8098 and 8133-8136: "`PL-4DCG` surveyed the variation that affects a computed number, and `PL-FG9D` designed the abstraction against that variation" and "`PL-4DCG` surveyed the machines in current clinical use … `PL-FG9D` then designed the base abstraction". Rows 8147 and 8161 then announce each as done a third time. The facts belong in the survey paragraph (8147-8159) and the design paragraph (8161-8182), which name the two documents. Rows 8097-8098 keep nothing. Rows 8132-8139 keep only that the design had to follow the survey.
- Repeat, rows 8099-8100 and 8141: "`PL-WZVZ` is the surface that keeps a machine's effect on a curve attributable to a named parameter" and "`PL-WZVZ` (make an inter-machine difference attributable)". It belongs at 8140-8145 with the other waiting items. Rows 8099-8100 keep nothing.
- Repeat, rows 8091-8092 and 8186-8188: "a real commercial machine is added as a data file, not as code" and "A machine whose delivery and removal are already in the closed set is one data file under `src/anesthesia_sim/data/machines/`". Rows 8115-8118 give this goal to item 40, so it belongs in item 40, which is in a later chapter. Item 1 keeps a pointer: "item 40 adds machines as data files". The outline read should check what item 40 already says.
- Repeat that makes the reader read ahead, rows 8156-8159 and 8171-8175: "this milestone has to choose, on the record, among three options" and "The inlet-position question above is answered … decline to represent internal topology". Give the decision once, at 8171-8175, with the survey finding (8153-8155) as its reason. The list of three options goes to `PL-FG9D` or to `docs/machine-abstraction.md`.
- Repeat, rows 8108-8110, 8190-8191 and 8199-8202: "holding more than one agent is the multi-substance generalization", "requires the multi-substance patient state … because residual washout means holding two agents at once" and "Model the patient's state as a set of substances … Items 2 and 7 need the same generalization". It belongs at item 6, which defines it. Items 1 and 2 keep "after item 6". Item 2 points at § "Development pathway" instead of item 6, so a reader going down the list does not learn that item 2 waits on an item numbered after it.
- Repeat, rows 8206-8208 and 8246-8248: "every change to fresh gas flow, the vaporizer dial, ventilation and cardiac output is stamped" and "Such an event is a fresh-gas-flow, vaporizer, ventilation, or cardiac-output change". The list belongs at item 8. Item 12 keeps "any change recorded on item 8's timeline".
- Repeat, rows 8260-8262 and 8385-8390: "Bookmarks (item 26) remain useful as the *named, threshold-triggered* subset … They are not the only subset that qualifies" and "Item 12's 'Branch points' note treats every event … as a valid branch point, not only bookmarks. Even so, a snapshot policy should still be keyed on the bookmark set". The snapshot policy is part of how forking stores its runs, so it belongs in item 12 beside the storage note (8283-8290). Item 26 keeps "bookmarks are also branch points (item 12)".
- Repeat, rows 8289-8290 and 8309-8310: "What is *not* cheap is the per-step concentration history itself" and "the controller's concentration history, which is still unbounded". It belongs in item 21. Item 12 keeps a pointer to item 21.
- Repeat, rows 8550 and 8554-8555: "`PL-B396` chooses what the resulting figure looks like" and "`PL-B396` chooses that display". Say it once, at the end of item 28.
- Repeat that makes the reader read ahead, rows 8533-8539 and 8545-8547: by its own account, the paragraph at 8533-8539 restates what `docs/MODEL.md` § "Agent amount" "carries": Biro's 184 mL, the 182.8 mL from Laster, Fang and Eger, and the 2026-09-17 ratification of 20 °C. Rows 8545-8547 then say the conversion rests on Laster "rather than on Biro's composite constant", so the reader meets a source and then its replacement. The figures belong in `docs/MODEL.md` § "Agent amount" alone. Item 28 keeps the following, with both § pointers: the ratio has been stored for each agent since `PL-KZ99` (2026-10-26), it is exact for the delivered amount, and it reads a compartment store 5.8 % high.
- Repeat, rows 8558-8562 and 8604-8608: "`CLAUDE.md` sets the bar: a clinician who knows uptake and distribution should recognize the physiology without a translation step" and the project owner's 2026-09-03 bar, "a sharper test than the one-line bar in `.claude/rules/core-domain.md`". Item 29 is judged against the 2026-09-03 bar, so that bar belongs in item 29's first paragraph in place of the `CLAUDE.md` bar. The account of when the `CLAUDE.md` bar was written goes.
- Repeat, rows 8624-8625 and 8659-8661: "This supersedes `PL-6GS0`, which decided in v0.2.8 to keep the split" and "v0.2.8's row already records why the split was kept over an exact matrix exponential". Keep 8624-8629. Rows 8659-8661 keep nothing.
- Repeat, rows 8583-8585 and 8594-8596: "The pass therefore sits immediately after v0.4.0, as the `v0.4.x` row" and "It was pinned immediately ahead of v0.5.0". Give the current placement once, in the placement paragraph (8568-8576): after v0.4.0, ahead of item 6, and ahead of v0.5.0, because v0.5.0's score architecture changes `core/` and waits on `PL-GS5X`.
- Repeat, rows 8663-8672: "The timeline row above carries the same list and the same correction." The list of nine items belongs once, in the row of § "The timeline", where the reader looks for what a release holds. Item 29 keeps a pointer to that row. The account of how the count was corrected (`PL-GGCN`, `PL-P0BB`) goes to `PL-YYL2`.
- Repeat, rows 8103 and 8115-8118: "*The framework half is item 40*" and "Item 40 is the half that can be built now … item 40 is the item that delivers it". Say it once, in the italic line at 8103.
- Decision history in item 1, rows 8104-8115: why the bundle sat in Phase 1 and what it cost the queue goes to the item that holds the 2026-09-20 split. No item is named (see the query below). Item 1 keeps 8103 and 8115-8117, which say what the item now holds.
- Decision history in item 1, rows 8120-8126: "the sentence that said otherwise was stale", the literal in `core/circuit.py`, and the history of `PL-4YY1` and `PL-8DJ7` go to those two items. Item 1 keeps 8126-8130: the default is one of a run's opening conditions and not part of a machine's specifications, because no surveyed machine publishes a startup flow, and its value is open under `PL-NM7X`. Give the current value there too. It appears only in item 28's table (8515): "4.0 L/min (the shipped default)".
- Decision history in item 12, rows 8242-8244: "This decision supersedes this note's original framing …" describes the text and its history. Cut it, or move it to the item that holds the 2026-08-25 forking decisions. No item is named (see the query below).
- Decision history in item 24, rows 8316-8327: the history of the consolidation (`PL-YD6X`, `PL-2CS8`, v0.4.11, the three former locations) goes to `PL-2CS8`. Item 24 keeps one sentence: the display constants are now in one place (`app/theme.py`). It also keeps rows 8329-8333, which name the prerequisite still to build: a settings store that can be written and saved.
- Decision history in item 24, rows 8336-8339 and 8343-8344: "Until that date, this gate named `data/**/*.json` and nothing else" and "this one has already been wrong once" go to `PL-QBX0`. Item 24 keeps the criterion (8339-8343) and the fact that the table lists the cases known on 2026-09-19.
- Decision history in item 27, rows 8457-8459: "Until 2026-10-25 this entry said that the containers were drawn to scale …" goes to the item behind the 2026-10-25 ratification. No item is named (see the query below).
- Decision history in item 28, rows 8482-8483: "It was kept out of the v0.4.0 scope …" no longer applies, because the item is now scheduled in v0.7.0 (8484). Cut it.
- Decision history in item 28, rows 8488-8527: the former wording, the accounting identity with its code names, the 2026-09-19 table and the ratios all argue a choice that is already settled. They go to `PL-H4N8`, which "carries the method". Item 28 keeps one paragraph saying four things. Cost is computed from delivered agent, which is what the vaporizer added. Exhausted agent understates it by the amount still stored. On the exhausted basis, low flow's saving is overstated by as much as 2.3x. Gas Man (Workbook Appendix, printed p. 174) and `docs/MODEL.md` also use the delivered amount.
- Decision history in item 29, rows 8578-8582 and 8587-8599: the old placements and the paragraph that "read differently until 2026-09-06" go to `PL-3P2P`. Keep "`PL-GS5X` closed on 2026-09-06 in pull request 376" only if the status line asked for below needs it.
- Decision history in item 29, rows 8643-8644: "Earlier on 2026-09-03, this step was briefly recorded as a minor version" goes to the item behind the 2026-09-03 version decision. No item is named (see the query below). Item 29 keeps the reason it is a patch (8644-8654).
- Written for another reader, item 1, rows 8162-8170: the system matrix, "Metzler" and strategies that stay constant across a step are for a developer. They belong in `docs/machine-abstraction.md`, which item 1 already names. The roadmap keeps what they decide. A machine changes only the breathing circuit's terms, never the patient's. The reference machine reproduces today's values exactly. A behaviour outside the design's set, such as item 5, needs a milestone of its own.
- Written for another reader, item 12, rows 8271-8277: the two closed causes (`elapsed_s` accumulation order, steps per frame) go to `PL-VM40`. Item 12 keeps that two causes were closed in v0.4.0, and what is left (8276-8281).
- Written for another reader, item 24's table, rows 8347-8352: the column "What holds its value" names tests and tools this reader does not know (`tools/doc_check.py`, `tests/unit/test_theme.py`, `tools/agent_identity_check.py`, `tools/contrast_check.py`). Instead give the guarantee each value carries: cited and versioned; ISO 5360:2016 Table 2; 3:1 trace contrast and WCAG 2.2 AA text contrast; only a recorded judgment. Move the tool names to `PL-QBX0`. The first cell of row 8351 has grown into an essay. Name the thing in it, such as "the chart and text colours", and put the contrast targets in the third column.
- Written for another reader, item 24, rows 8366-8369: the luminance cap and the 1.48 spacing are the derivation that `app/theme.py` records. Item 24 keeps three facts: colour cannot separate the six traces, the dash patterns separate them, and no check protects the patterns. "The last row is the one to read twice" talks about the text. Cut it.
- Written for another reader, item 26, rows 8431-8434: where the reasoning is recorded (`MacTarget` in `app/bookmarks.py`), and why, is for a developer, and the class already holds it. Cut it.
- Written for another reader, item 29, rows 8611-8622: the operator-split steps, the RK4 oracle and the tautology go to `PL-SPMQ`, which "carries the measurement and the options that were weighed". Item 29 keeps three facts. Renaming alone could not meet the bar. The operator split was therefore replaced by the exact matrix exponential (`PL-GS5X`, landed 2026-09-06). The code that computes the result now reads as the governing equations.
- Written for another reader, item 29, rows 8634-8641: how the release tool numbers a patch, and the guard that reserves a milestone's number (project owner, 2026-09-16, ratified, on `PL-KQHN`), apply to every release, not only item 29. They belong in § "Versioning decision". Item 29 keeps "a patch in the `v0.4.x` track, released under whatever number it is given".
- Item 25 (8372-8379) is away from where its reader looks. It shipped in v0.4.0 as `PL-SN2C`, yet it sits in a catalogue of items "left unspecified" until promoted. It belongs in § "Completed: v0.4.0 - the teachable case", which it already names. The catalogue keeps "Shipped in v0.4.0" or nothing. The outline read should check whether that section already gives the five rates.
- Items 27 and 28 (8452-8555) are scheduled in v0.7.0, and each says § "v0.7.0 - the schematic" "has the scope". Their remaining scope material (8465-8477, 8529-8555) belongs in that section. The catalogue keeps three things for each: the goal sentence, the scheduling decision with its tag whole, and the pointer. The outline read should check what that section already gives.
- Item 29 (8557-8672) has its own row in the timeline (`v0.4.x`) and its own scope. Once the moves above are made, its bar, placement, version and item list belong with that row or in a milestone section of their own. The catalogue keeps the goal and a pointer.
- Item 1 (8089-8188) mostly serves item 40. Its opening goal (8091-8100) and its survey, design and naming notes (8132-8188) serve the data-file framework that rows 8103 and 8115-8118 give to item 40. Item 1 should open with what it now holds: the interlock baseline, and the machine behaviours that need the solver work item 40 defers. The notes move to item 40.
- Order within item 29: the bar that says when the work is done (8604-8608) comes after the purpose, the placement and two history paragraphs. Use this order: goal and bar, placement, version, then the items with their status.
- Too long to find one's way in: run 1 alone holds items 1-29, and six of them (1, 12, 24, 26, 28, 29) run from 25 to 115 rows. After the moves, put subheadings between groups of items. Keep the item numbers, because other files cite "planned-milestone item N", and a Markdown ordered list may start at any number. Proposed subheadings:
  - before item 1, "Machines and agents (items 1-7)";
  - before item 8, "Scenarios, replay and forking (items 8-12)";
  - before item 13, "Patient models (items 13-19)";
  - before item 20, "The application (items 20-24)";
  - before item 25, "Playback and teaching views (items 25-28)";
  - before item 29, "Code that reads like the physiology (item 29)".
  This also gives item 12's "the group" (8228) a name. Check the groups against runs 2 and 3, where items 39 and 40 belong with the machine items.
- Labels that do not say what their paragraph holds:
  - 8283, "*Measured 2026-08-25, so the storage question is designed around the right cost.*": use "*Snapshot and resimulation cost (timed 2026-08-25).*".
  - 8316-8317, "*The consolidation that this item named as its prerequisite has landed, …*": use "*Prerequisite: a settings store that can be written and saved.*".
  - 8392, "*Scope floor*": use "*Minimum scope*". The writing rule names "floor" as a word to replace, and the change lets the definition at 8394 go.
  - 8529, "*A prerequisite of its own, and it is narrower than it first looks.*": use "*Prerequisite: a vapour-to-liquid ratio, now stored for each agent.*".
  - 8601-8602: once the history moves, use "*Scope (project owner, 2026-09-03).*".
  - 8587: the bold label goes with its paragraph.
- Query: rows 8082-8085 say each item stays unspecified, with "no goal, required scope, or definition of done", until it is promoted. Yet items that have not been promoted state a goal (8091-8092), a "Required property" (8264), and "Required properties" with a minimum scope (8392-8424). Either the rule or these entries is out of date, and only the author knows which.
- Query: rows 8086-8087 call version numbers "after v0.2.3" provisional. The chapter, though, cites shipped releases up to v0.4.28 (8538) and schedules items in v0.7.0 (8461, 8484). The reader needs to know the version after which numbers are provisional now.
- Query: item 28 says "This item depends on nothing" (8481-8482) and then gives "A prerequisite of its own" (8529). The text does not say whether "depends on nothing" means that `PL-KZ99` has already met the prerequisite.
- Query: item 12 says "This note named three causes, and two of them are closed" (8271). It then lists two things left: a different step size, and whatever a branch restores from a stored point (8276-8279). The reader cannot tell which of them is the third cause.
- Query: item 26 says `PL-CTD7` "shipped the outcomes as a set of four values" (8446-8447). It names "reached", "not reached, run-time cap hit" and the fourth, a time bookmark before the fork instant. The third outcome is not given.
- Query: item 26 names shipped work (`PL-CTD7`) and existing code (`MacTarget` in `app/bookmarks.py`), but does not say whether bookmarks have shipped, or in which release. A reader deciding what a release holds needs that status. The same is true of `PL-DHV7` (8414).
- Query: item 29 lists nine items and says that `PL-GS5X` landed on 2026-09-06. It gives no status for the other eight items, or for item 29 as a whole.
- Query: rows 8601-8602 say item 29 was re-scoped "and it is no longer a patch", while rows 8631-8633 say "Version: a patch in the `v0.4.x` track". Also, row 8601 says "the three open questions are answered" but does not name the three questions.
- Query: this chapter uses terms it does not explain: "Phase 1" (8103, 8106), "the timeline's Beyond row" (8111), "Gate 1" (8142), "Gate 4" (8485), "the MVP" (8596), "slot" and "the closed set" (8143, 8171, 8186), "the score architecture" (8592) and "touches" (8594). "This gate" at 8336 means item 24's list of values the panel may not edit, a different sense from Gate 1 and Gate 4. The outline read should check whether another chapter defines each term. Where none does, the reader needs a definition.
- Query: row 8368, "six traces cannot be more than 1.48 apart", gives no quantity or unit. It may be a contrast ratio or a luminance ratio.
- Query: the decision histories that this read moves out name no item to receive them: item 1's split (2026-09-20, 8102-8115), item 12's forking decisions (2026-08-25, 8242-8244), item 27's former wording (8457-8459), and item 29's version decision (2026-09-03, 8643-8644).
- Query: the naming decision binds "this milestone and … `PL-WZVZ`" (8180). After the split, the text does not say whether "this milestone" means item 1 (the interlocks) or item 40 (the data-file framework).
- Query: rows 8558 and 8607-8608 name a bar in `CLAUDE.md` and "the one-line bar in `.claude/rules/core-domain.md`". The text does not say whether these are one bar or two.
```

**Chapter read 47: § "Planned milestones", rows 8674-9257.**

```text
- **Rows 8674-8717 are written for another reader.** These rows set out item 29's naming rules: a symbol maps to an expression, equations are cited and only the missing solved form is restated, the three mechanical rules, and what the two sources settled. A developer changing code needs these rules. The owner, who is deciding what a release holds, does not. They belong in the items they name (`PL-H46J`, `PL-VZL0`, `PL-FZ6T`, `PL-3TLK`, `PL-212V`). ROADMAP.md keeps one sentence for each rule, with its item. Two parts are decision history and go to their items: "the shape guessed at here before the pass was measured" (8675-8676) goes to `PL-H46J`, and "A unit-suffix check was considered and rejected …" (8698-8700) goes to `PL-FZ6T`.
- **Rows 8719-8726 are in the wrong place.** The patch-not-minor version decision says what the release holds, so it belongs with item 29's opening scope, which is in the previous chapter. Its last two sentences ("The paragraph above this one said … superseded it") describe an earlier version of the text. Correct the superseded paragraph itself and cut these two sentences.
- **Rows 8739-8740 describe where a sentence used to sit.** "That requirement predates this item. It used to sit as an unattached sentence …" is about the text, not the plan. Cut it.
- **Rows 8747-8749 name a test.** `test_every_run_simulates_the_shipped_reference_adult` is a name this reader does not know. Move it to `PL-DXJR`. ROADMAP.md keeps "this item rewrites that section and its hazard row."
- **Rows 8840-8848 explain to the scoping session why the warning is recorded here.** Cut the paragraph. Keep one sentence of warning in 8823-8838: scoping weight as "cardiac output becomes a function of weight" is the change `PL-YKSM` examined and refused. The rest repeats other rows. "the change `PL-YKSM` examined and refused" repeats "`PL-YKSM` carries the arithmetic and the alternative it refused" (8838). "kinetics are wrong in the most-taught direction" repeats "Every textbook has the effect running the other way" (8832-8833).
- **Rows 8906-8912 interrupt the numbered list.** This note on maintaining the list sits between items 31 and 32: item 1 was promoted and delivered as v0.2.0, and further volatile agents remain an unscoped idea. Move it to the head of § "Planned milestones", or to a list of later ideas, and keep it whole.
- **Item 32 (8914-8937) leads with history and buries what is left.** The opening and rows 8921-8931 cover the 2026-09-05 deferral, `PL-XYRN` being closed, `PL-N092` running on 2026-09-06 and the check that retired itself. That history goes to `PL-XYRN` and `PL-N092`. ROADMAP.md keeps three facts: the repository is public, `README.md` exists, and the pass blocks nothing. Put 8933-8937 (what is left) straight after the item statement. Restate the statement (8914) too: the README part is done, so "in one pass" now promises more than is left.
- **Item 33 has four placement paragraphs.** Merge 8944-8946 (the request: not urgent, after the simulator works), 8969-8972, 8974-8983, 8985-8995 and 8997-9005 into one placement paragraph. It gives the decision tag whole ("project owner, 2026-09-16, ratified on `PL-PHKP` - chosen over leaving it between MVP and Gate 2, where 2026-09-08 had placed it"), the reason (item 34 adds four surfaces), and the cost (the current look stays until after item 34). The renumbering history goes to `PL-V1Y7`, and the account of the option not taken goes to `PL-PHKP`.
- **Item 33 lists the four new surfaces twice.** "an area header, a workspace tab strip, a live splitter handle and a drag affordance" (8978-8979) repeats "The live splitter handle, the drag affordance and the Workspace tab strip … The area header" (8989-8992). Keep one list in the merged placement paragraph.
- **The split between arrangement and appearance is given twice.** "Item 34's entire content is which areas exist … This item decides how the contents of those areas look" (8949-8951) is repeated by "`PL-BNYF` had already separated the two questions: arrangement is item 34's, and appearance is this row's" (8999-9000). Keep it in 8948-8955. The other place keeps nothing.
- **The cost of the placement is stated two ways.** "would have given a styled interface two releases sooner" (8998) contradicts "the cost recorded below, which is now one release rather than two" (8994-8995). The merged paragraph should state the cost once, as one release.
- **Rows 9007-9025 are mostly history.** Move the history of the Qt port taking the item and handing it back to `PL-L9RD`. Rows 9015-9017 ("This was corrected on 2026-09-16 … This entry had said 'this item'") describe an earlier version of the text, so cut them. Keep four points:
  - the port changed no palette entry, type size, padding or radius;
  - every dashboard surface is now an independent widget, which makes one pass possible;
  - this item inherits none of the splitting, joining or workspace behaviour;
  - a port is not a design round.
- **Rows 9027-9040 can be one sentence.** That sentence says no structural prerequisite remains: display constants landed in v0.4.11, panel decomposition in v0.4.25 and theme ownership in v0.4.26. The detail goes to `PL-2CS8`, `PL-B9PY` and `PL-NGF7`.
- **Rows 8957-8967 can be one sentence.** Keep: the owner asked again on 2026-09-08, and the three earlier mockups are not a starting point. The rest is already in `docs/WORKING_NOTES.md`.
- **Rows 9053-9066 name tools and rules this reader does not know.** `tools/contrast_check.py`, `ast`, `REQUIREMENTS`, judgments 1 and 4 of `.claude/rules/ui-color.md`, and `PL-BXB2` are for the contributor doing the restyle, and `.claude/rules/ui-color.md` is their home. ROADMAP.md keeps the three constraints in words:
  - every declared colour pair meets WCAG 2.2 AA under four vision models, and the declared list is rewritten in the same change;
  - the three ISO 5360:2016 agent colours are fixed;
  - traces are told apart by dash pattern.
- **Item 34's design detail is for the contributor building it.** Rows 9116-9122 (Blender's docking operations), 9200-9217 (licence analysis), 9219-9245 (splitter-tree research) and 9247-9257 (`QSplitter.saveState`) belong in `docs/interface-provenance.md`. Rows 9201-9203 and 9244-9245 say that file already holds the record, the count, the method, the construction and the condition for reversing the decision. ROADMAP.md keeps each decision in one sentence with its item:
  - the layout is stored as nested splitters behind the project's own layout model (`PL-3J2P`, `PL-C842`);
  - Blender's source may be read, and its documentation is paraphrased and cited, never pasted (`PL-P5QX`).

  The record of how the manual was obtained (9101-9104: the egress proxy refused the site, a probe on 2026-09-26 succeeded, `PL-M701`) moves with this material and is not cut.
- **Rows 9161-9198 repeat `docs/MODEL.md`.** The three-part division of the required outputs (unconditional, accounting, conditional) and the tier detail repeat `docs/MODEL.md` § "Minimum displayed outputs", which the paragraph names as their home. ROADMAP.md keeps:
  - the rule that nothing may cover a required value;
  - that v0.6.0 builds the unconditional set outside the area system, in the per-window shape;
  - the second-window decision, with its tag whole ("project owner, 2026-09-16, ratified, answering `PL-W54S`, chosen over that item's own two live readings");
  - that the division is a stepping stone.

  Split what stays: it is now one long essay.
- **"Floating is not ruled out" is said twice, once with history attached.** Rows 9156-9158 ("The first version of this paragraph recorded floating panels as 'not admitted' … overreach") describe an earlier version of the text, so cut them. "Floating is wanted later and not built in this milestone" (9153-9159) repeats "Any later floating mechanism must comply with the occlusion rule, rather than being ruled out ahead of time" (9193-9194). Keep it once, beside the occlusion rule.
- **What an area holds is said three times.** It appears at 9077-9078, 9088-9089 and 9107-9108, and "workspaces as tabs geared to a task" appears at 9089-9091 and 9111-9112. The definitions list (9107-9114) keeps them. Row 9086-9097 keeps only the safety reason: in a tiled layout no panel hides a value.
- **The break-out date is given in two items.** "Break-out came off the timeline, 2026-09-26" appears at 8985-8987 and 9137-9139. Keep it in item 34. Item 33 keeps only its placement.
- **The sourcing standard is stated four times in item 30.** "Every new value is sourced on the same terms as every other value in `data/`" appears at 8784-8785, 8817-8818, 8861-8862 and 8868-8869. "A plausible but unexplained or incorrect clinical value is refused" appears at 8762-8763 and 8815-8817. State both once, at the head of item 30's decisions. Each paragraph keeps only its own source.
- **"The only patient today is the reference adult" is said twice.** It appears at 8730-8731 and 8768-8769. Keep it at 8730-8731. Rows 8767-8770 keep nothing.
- **Item 30's order makes the reader read ahead.** Rows 8751-8770 point forward to "the derivation question below" and "the supported-range refusal below". Use this order:
  - statement and read-only profiles (8728-8740);
  - placement (8792-8798) and the dependency on item 11 (8885-8890);
  - the safeguard it removes (8742-8749);
  - the scaling decisions (8800-8838);
  - body composition (8751-8770);
  - the MAC basis (8772-8790);
  - then, under an open-questions label, the default cardiac output (8850-8862) and covariate bounds (8864-8883).
- **Item 33's order puts scope and exclusions apart.** Use this order:
  - statement (8939-8942);
  - arrangement belongs to item 34 (8948-8955);
  - out of scope (9068-9074), which tells the reader what the release leaves out;
  - the merged placement paragraph;
  - prerequisites (9042-9051);
  - palette constraints (9053-9066);
  - what the item inherits (the shortened 9007-9040 and 8957-8967).
- **Item 34's order uses terms before defining them.** Use this order:
  - statement and request (9076-9084);
  - definitions (9099-9114);
  - why tiling (9086-9097);
  - tiled first, floating later (9133-9159);
  - the occlusion rule (9161-9198);
  - then the two precedents (9124-9131), which cite `PL-WLWY` "for the minimum display" before 9168 explains it;
  - then pointers to the design material.
- **The chapter is too long to find one's way in.** Items 30, 33 and 34 each run to roughly 1,000 words or more inside a single numbered list entry, and item 34 continues past row 9257. Give each large milestone its own subheading that keeps its number, so citations such as "item 34" still work: "30. Patient factors", "33. The interface pass", "34. Areas, views and workspaces". Within each, group the run-in labels under "Decided", "Open for scoping", "Placement" and "Before starting".
- **Several run-in headings do not say what their paragraphs hold.** Replacements:

  | Rows | Current heading | Replacement |
  | --- | --- | --- |
  | 8850-8851 | "… for the default" | "… for the default cardiac output" |
  | 8948 | "Arrangement is not on that list, and the word that used to be was 'layout'" | "Arrangement belongs to item 34" |
  | 8957 | "This resumes a shelved thread rather than opening a new one" | "The shelved mockups are not a starting point" |
  | 8985 | "Renumbered `v0.6.x`, 2026-09-26" | merge into placement |
  | 8997 | "What the other side bought, recorded because it was real" | merge into placement as "The cost" |
  | 9007 | "Absorbed into the Qt port … returned here" | "The Qt port changed nothing visual" |
  | 9042 | "Two hard prerequisites, and they are the reason this cannot simply be started" | a heading that names the two prerequisites (see query) |
  | 9053 | "Three constraints on any palette, recorded here so scoping does not rediscover them" | "Three constraints on any palette" |
  | 9099 | "The vocabulary is Blender's, and it is the concept rather than a resemblance" | "Three terms: Area, View and Workspace" |
  | 9124 | "Two precedents worth copying, both from the source" | "The last workspace cannot be deleted, and a workspace can pin its run" |
  | 9133-9134 | "Tiled first, with break-out …" and "Scoped across two releases on 2026-09-16" | stale since break-out came off the timeline (see query) |
  | 9152 | "What is refused is silent occlusion, not floating" | "Floating windows are deferred, not refused" |
  | 9200 | "The licence constraint, and it runs the opposite way for the two kinds of source" | "Read Blender's source freely; paraphrase and cite its documentation, never paste it" |
  | 9234 | "One supporting argument did not survive the research" | merge into the splitter-tree paragraph before it moves |

**Queries:**
- Query, rows 8723-8726: the text says "The paragraph above this one said 'no behavior, equation, parameter, or numerical method changes'", but the paragraph directly above (8704-8717) says nothing like it. The reader cannot find the superseded text.
- Query, row 8755: "the derivation question below" names no paragraph that the reader can find below.
- Query, rows 8751-8770 against 8800-8805: body composition is derived by default and "moves fat uptake", yet weight scales the compartments directly and not through body composition. The reader needs to know how body composition acts on the model. "Height" appears only in the declined route, so the reader also needs to know whether height is an input.
- Query, rows 8764-8765 against 8865-8867 and 8882-8883: "the supported-range refusal below" says an out-of-range edit is refused. The covariate paragraphs say the response (blocking, logging or both) is open and that the mechanism is not inherited.
- Query, rows 8887-8888 against 9032-9033: item 30 says `PL-B9PY` covers two-run rendering, which is still to come. Item 33 says `PL-B9PY` is the panel decomposition that landed in v0.4.25.
- Query, rows 9048-9050 and 9073 against 9014: the prerequisites and the out-of-scope paragraph speak of Flet rendering, but the interface moved to Qt in v0.4.26. The reader needs to know whether the CanvasKit prerequisite still applies.
- Query, rows 9042-9051: the paragraph cites two records but does not say what each prerequisite requires to land, for example a check that draws and compares the interface, and an environment that can render it.
- Query, row 9063: "the pairwise ceiling at about 1.48" does not say what is measured, for example the contrast ratio between any two traces.
- Query, rows 9133-9139 against 8985-8987: break-out came off the timeline on 2026-09-26, so "Scoped across two releases" and "the two halves" are stale. The reader needs to know whether break-out is planned for any release. The "(see below)" at 9139 points to nothing below in this chapter.
- Query, rows 9142-9143: "the per-window shape that the next paragraph settles" is settled two paragraphs later (9182-9192), not in the next one.
- Query, row 9105: "two of them are adopted from Blender rather than invented" does not say which of Area, View and Workspace is the project's own term.
- Query, rows 8892-8904: item 31 gives no phase or release, and the reader needs one to decide what a release holds.
- Query, rows 8933-8937: "the rest of what a first-time visitor meets" is item 32's remaining scope, and no row in this chapter lists it.
- Query, rows 9116-9122: the reader needs to know which of the docking operations v0.6.0 builds. This chapter does not say. § "v0.6.0 - the layout is the reader's" may say, but it is not in this chapter.
- Unclear, row 9243: I cannot tell what "a planar subdivision is owned by one person forever" means.
```

**Chapter read 48: § "Planned milestones", rows 9259-9674.**

```text
**Facts given in more than one place**

- **Release numbers.** Rows 9292-9294 say "the schematic (item 27) moves to v0.8.0, and multi-substance (items 6 and 7) moves to v0.9.0". Rows 9300-9302 say "the schematic (item 27) moved back to v0.7.0, and multi-substance (items 6 and 7) moved to v0.8.0 (`PL-V1Y7`)". Only the second is current. It belongs with the paragraph that unschedules break-out (9296-9304). Rows 9292-9294 keep nothing. The move and the move back go to `PL-NMTF` and `PL-V1Y7`.
- **The split across two releases.** Rows 9288-9292 say "Item 34 then splits across two releases … The cut is taken at break-out". Rows 9298-9300 say "Break-out remains this item's second half … but it has no row on § "The timeline"". The second is what holds now. Rows 9288-9292 keep nothing, and the size history goes to `PL-NMTF`.
- **Item 34 after v0.5.0.** This placement is argued twice: in 9279-9288 (three grounds) and in 9321-9345 (reopened and re-affirmed).
  - Merge them into one paragraph with the reasons the owner can weigh now. A workspace pins a run, and v0.5.0 brings the second run (9280-9282). What is left of v0.5.0 is small, with a date for that count (9334-9341). No known failure is live yet (9285-9288).
  - Keep both decision tags whole beside it.
  - The argument and its rebuttal (9323-9333 and 9341-9345) go to the item that records the 2026-09-17 decision.
- **Why a surface built early is built twice.** This reason appears three times:
  - 9324-9328: "the build order decides whether a new display is a widget registered against a contract, or an edit to whatever layout exists at the time"
  - 9352-9354: "built against whatever layout exists at the time, and against no view contract. So it is built twice"
  - 9392-9394: "views built first are built against today's fixed layout and then rewritten"

  It belongs in the rule paragraph (9350-9368). The other two places keep nothing.
- **The rule written out.** Rows 9345-9348 say "Until now, that paragraph's rule was only implied by the row order … It is now written as a rule". The tag at 9351-9352 says "chosen over leaving the ordering implied by row position". The tag stays. Rows 9345-9348 go, because they describe the text rather than the subject.
- **The Qt port's handles that do nothing yet.** This appears three times: 9288 "the port's handles are inert"; 9381-9383 "Each dashboard surface becomes an independent widget inside nested `QSplitter`s with the handles inert"; 9398-9400 "supplies those two views for free, because it makes each dashboard surface an independent widget". It belongs in 9370-9385. Rows 9398-9400 keep a pointer that the two existing views come from the Qt port. Row 9288 keeps the fact only if its "no live failure" reason stays.
- **The view catalogue is separate work and comes after the layout.** This is in 9387-9391 (the owner's 2026-09-15 quote, "Item 36 is that catalogue"), in 9462-9466 "This is work separate from the layout mechanism, and it comes after that mechanism", and in 9477-9478 "requested this on 2026-09-15 as its own track (`PL-4D1M`)". The owner's decision belongs once, in item 36. Item 34 keeps a pointer to item 36 and its own scope point, which is testing against two existing views (9394-9397).
- **Calling the occupant of an area a View.** Rows 9466-9473 give the decision, the 2026-09-16 decision it reversed and two reasons. They also say that § "v0.6.0 - the layout is the reader's" has the full reasoning. Item 36 keeps the decision with its whole tag. The reversal history goes to `PL-GPYV`. The reasons stay only in § "v0.6.0 - the layout is the reader's", if that section gives them; the outline read can check.
- **Perfusion is fixed today.** Row 9410 says "The model keeps both fixed today", and 9417-9418 say "which is that the model keeps perfusion fixed". Keep 9410. The framing paragraph keeps only the owner's direction that the option stays on the list (2026-09-13). "`PL-8GV5` proposed closing the question outright" goes to `PL-8GV5`.
- **Item 35's studies.** Rows 9422-9433 and 9445-9455 give the volunteer and fat-flow studies with their citations. Rows 9436-9438 and 9443-9445 say that `docs/MODEL.md` § "Known limitations" already records and weighs them.
  - The citations belong in `docs/MODEL.md`, where a clinician checks a value.
  - `ROADMAP.md` keeps the conclusions and the pointer. The sign of the effect depends on the carrier gas. The dose-response is not monotonic. The effect changes with time at a fixed dose. So the option must decide what it asserts and how it shows its uncertainty. Resting fat flow is uncertain by up to about a factor of two, and the direction of the error is unsettled.
  - Cut a citation only once that section is confirmed to hold it.
- **Provenance rows for a machine profile.** Rows 9593-9594 say "fails `make check` on the provenance rows it owes", and 9623-9625 say "requires a provenance row in `docs/MODEL.md` for every leaf number in every data file". This belongs in 9621-9626. Rows 9593-9594 keep nothing.
- **The rule that an unscheduled entry is recorded as intent, not as a queue item.** It appears at 9309-9311, 9505-9506, 9538-9539 and 9543-9545. It belongs once, in the list's introduction, which is outside this chapter. Each entry keeps the word "intent", and item 39 keeps its tag whole. Rows 9538-9539 keep nothing.

**Paragraphs written for another reader**

- **Layout model design (9266-9273).** The `LayoutModel` tree, its method names, the one adapter module that imports `QSplitter`, `saveState()` and `PL-LH18` are a contributor's design. They belong in `docs/ARCHITECTURE.md` or in the item that builds the layout model. `ROADMAP.md` keeps the three guarantees (9261-9266) and the fact that a layout is saved as versioned data. Split rows 9259-9273, which make two points.
- **Qt window behaviour (9311-9319).** The transient-parent behaviour, read on PySide6 6.11.2 / Qt 6.11.2 on 2026-09-16, is already in the item brief, as the text says. Keep only the pointer to the `docs/MODEL.md` rule. The date moves with the behaviour it dates.
- **Evidence for the reopening (9328-9333).** `PL-J4NW`, the routing in `docs/ARCHITECTURE.md` and `.claude/rules/ui-areas.md` are evidence for an argument. They are history and go to the 2026-09-17 item.
- **Item 33 history (9371-9377).** Absorbing item 33 into the Qt port, and reversing that, is history of the port and of item 33. It goes to § "Completed: v0.4.26 - the interface moves to Qt" or `PL-8VL1`. Item 34 keeps the reservation and its tag.
- **Who checked the studies (9415-9417, 9422).** The account of the session that checked the literature is history and goes to `PL-8GV5`.
- **Branding placeholder (9535-9539).** The removal by `PL-J7MM` is history and goes to that item. Keep one sentence: there is no placeholder asset to build on.
- **Why item 39 was added (9554-9557).** "Neither note had anywhere to point … worked out the same conclusion again" is history. Cut it, because 9548-9549 already say both notes stop at this change.
- **Code detail in item 40 (9586-9595).** The function name, `make check` and the unit suite are code detail. They belong in the item brief or `docs/machine-abstraction.md`. Keep this: circuit volume and fresh gas flow already sit in one cited data file with a first per-machine field, but nothing selects a profile yet, so a second profile is ignored.
- **A fix to another document (9621-9626).** "The target should say so" asks for a change to `docs/machine-abstraction.md`. It belongs in that document or in a queue item. Keep the cost: one data file plus one provenance row per number.
- **Item 43's inventory (9660-9669).** The breakdown is given in the names of internal checks: "literal and fact baselines", "the guard", pylint, "hand re-checks" and "four check items". It goes to `PL-K88Z`. Keep the date, the 13 items filed, and the fact that numbers restated in `docs/MODEL.md` and `README.md` are not yet counted.

**Order**

- **Item 34's paragraphs.** In this chapter they run 2026-09-16, 09-26, 09-17, 09-17, 09-12, 09-15, 09-15. That is neither the order of the dates nor the order the reader needs, and "settled above" (9309) and "the paragraph below" (9345) make the reader search. Use this order:
  1. What the item builds: the three guarantees (9259-9266), the views are item 36 and the build is tested on two existing views (9387-9397), example workspaces (9402-9407).
  2. Where it sits: the Qt port reserves the layout (9370-9385), then the merged v0.5.0 placement.
  3. The rule that no new display surface comes before this item (9350-9368).
  4. Break-out: unscheduled, and what keeps it possible (9296-9319).

  Row 9304 puts this work in v0.6.0. If § "v0.6.0 - the layout is the reader's" is the milestone that builds item 34, the decisions belong there, and entry 34 becomes a short entry with a pointer. The outline read should decide.
- **Item 39.** Rows 9568-9574 ("Nothing displayed today depends on it") answer the owner's first question, whether a release needs this. Move them to just after the item's opening paragraph (9541-9545).
- **The closing paragraph (9671-9674).** It covers the whole list, but the reader meets it only after 43 entries. It belongs in the list's introduction, in another chapter.

**Too long**

- **Item 34.** In this chapter alone it runs 149 rows in seven paragraphs, each opening with an italic label. After the cuts above, give each group of the order above one italic label: what it builds, where it sits, the rule, break-out.
- **Item 43 (9647-9669).** It is one 23-row paragraph. Split it into three: what the item does, with the owner's words; the four kinds of second copy, with their items; the inventory, dated 2026-10-19.

**Labels that do not say what their paragraph holds**

- 9275, "*Given a version, and split, on 2026-09-16*", and 9321, "*Reopened and re-affirmed, 2026-09-17*": merge the two paragraphs under "*Item 34 follows v0.5.0*".
- 9370, "*Placed, and the timing question is decided*": use "*The Qt port reserves the layout and builds none of it*". The chapter never says what "the timing question" is.
- 9387, "*The widget catalogue is separate work, and the layout comes first*": use "*The views are item 36, and this item is tested on two existing views*". "Widget" is the name that item 36 retires (9467-9469).
- 9402, "*What a preset differs in, by example*": use "*Example workspaces and the default layout*". The word "preset" appears nowhere else here.
- 9421, "*The evidence constraint, which is why "optional" is the right shape rather than a hedge.*": use "*The volunteer studies support no single dose-response.*" The original rejects a "hedge" that nobody proposed.
- 9440, "*Also unsupported at rest, one layer down.*": use "*Resting tissue blood flow is itself uncertain.*"
- 9597, "*Why it is separable from item 1, stated as the test that would falsify it.*": use "*It stays separate from item 1 while it changes no rate.*"
- 9606, "*Scope constraints, both of which are what keeps it cheap.*": use "*One profile and no machine chooser.*"
- 9621, "*A stated cost that the design document's own target omits.*": use "*Each machine also needs a provenance row for each number.*"

**Queries**

- 9266: the reader needs the date or Blender version behind "ten of twenty-one", and the text does not give it.
- 9286-9288: `PL-NWTM` and `PL-9LNF` are named only by id, and "pre-loaded" is not explained. The reader needs to know what the two failures are.
- 9303, "as any catalogue entry is": does "catalogue" mean this list of entries, or item 36's view catalogue (9367, 9391)? The text uses the word for both.
- 9308-9309, "the per-window shape settled above (entry 7, `PL-W54S`)": nothing in this chapter settles it. The reader needs the shape, or the section that settles it.
- 9334-9341: "13 of 20 `done`", "4 M and 3 S" and "4 L / 16 M / 3 S" carry no date, so they read as true today. The chapter also does not explain the L/M/S sizes.
- 9321-9348: the 2026-09-17 decision names no item, so its history has nowhere to move.
- 9541-9542 against 9561-9562: the opening paragraph says "temperature and water content", but the fix covers "temperature, pressure and water content together". Which is the scope?
- 9617-9619, "Internal circuit topology was declined, and item 39 reverses that": item 39 (9541-9574) is about gas-phase conditions in each compartment and never mentions circuit topology. Either the text contradicts itself or the item number is wrong.
- 9616: "strategy slot" is not explained.
- 9484, 9640, 9673: items 12, 13 and 15 are named only by number. The reader of items 37 and 42 needs to know what they are. They may be named in an earlier chapter; the outline read can check.
- 9671-9672, "None of items 1-43 mix scientific-core and UI/tooling concerns": item 37 has its own parameter file (9490-9491) as well as a display, and item 43 covers the simulator, its documents and the apparatus (9650-9651). The text appears to contradict itself.
- 9659-9661: "`PL-K88Z`'s inventory sizes the work before the row is scoped", yet the inventory was taken on 2026-10-19. Is the row scoped now?
- 9651 and 9662-9666: "apparatus", "the guard", "literal and fact baselines" and "four check items" are not explained for this reader, wherever they stay.
- "Item" names both a numbered entry here ("item 34") and a queue item ("build item `PL-Y04W`", "Six queue items"). The section edits should keep the two apart. The spelling also varies: "anaesthesia" (9409, 9441) against "anesthesia" (9576).
```

**How to apply.** Move and deduplicate only. No sentence is reworded, except a pointer that replaces a restatement, a word such as "above" or "below" that a move made wrong, and a heading. The line edit of what this slice changes follows in `PL-YRY3`, once the copy editor no longer drops requirements (`PL-F0Q2`). Each finding is applied, or recorded here with the reason it was not. A query that the tree answers is answered in the pull request, and one that needs the author is filed as its own item under `roadmap-structure`. Whether a finding that moves decision history out of the roadmap and into an item is applied is decided by the project owner's answer in `PL-LVN8`. Before the pull request is marked ready, two reviewers compare the old and new text passage by passage for any change of meaning. The move-only restructures of the machine documents and of `docs/interface-provenance.md` each changed 10 or 11 meanings that only such a comparison found.

**Done when.** Each finding below is applied, or recorded here with the reason it was not. No statement is lost: every sentence that leaves its place is kept at its one home, or replaced by a pointer that names that home. `bin/docket wave`, `bin/docket gate` and `bin/docket check` give the same answers before and after the slice, and `make check` passes.

**Generator check.** The repeats came from accretion. Each change that touched a topic stated its own record in the section it was working in, instead of pointing to the section that already held it. The structure read found the same shape in every document it read (`PL-BSMF`, `PL-SVGH`, `PL-T8RL`, `PL-39ZK`, `PL-3MTS`), so these are one sweep's findings. No check can decide whether two sentences state one fact. The structure read, which the project owner put ahead of every line edit on 2026-11-07, is the procedure that catches the shape. Not recorded as a generator.
